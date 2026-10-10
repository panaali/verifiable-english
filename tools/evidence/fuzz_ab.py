"""Fuzz A/B: `tools/difffuzz.py` at the base and the head over the same seeds; the baseline must not grow.

    python -m tools.evidence fuzz_ab --base-root ../base --batch docs/<track>/<batch> \
        --out docs/<track>/<batch>/evidence/fuzz-ab.json [--head-root .] [--seed S ...] [--jobs N]

Each checkout runs its own `tools/difffuzz.py --ci` and `--deep 1 --seed S` per seed (its own `ve`, Lean and
Rust builds). Both must hold the same baseline file, so both replay the same entries (the baseline must not
grow, and an entry the head fixes stays listed until a later batch drops it). `compare` then names every
difference of a pair of reports, and each one is unexplained unless a rule of the batch's `evidence.toml`
(`[[fuzz_ab.explained]]`) explains it:

- `{kind = "count", field = "findings" | "answers", surface, key, base, head}`: one count, both values named;
- `{kind = "replay", id, base, head}`: one baseline entry's replay status on each side, both named;
- `{kind = "known_rejection", base_lean_prefix}`: a replayed entry whose base Lean answer was an error starting
  with the prefix, whose head Lean answer now equals the head Python answer, and whose Python and Rust answers
  did not change.

The sample (seed, scale, corpus, mutants), the baseline and its unreviewed entries must be equal; a head
signature the base did not find is always unexplained. Replay is compared entry by entry, status and answers
(a count or a digest over part of the run let two swapped verdicts pass, `docs/lean-first/b10a/trace_fuzzer.py`),
and a new Lean answer after a known rejection is explained only when it agrees with Python
(`docs/lean-first/b10b/fuzzer_gate.py:85` accepted any).
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile

from tools.evidence import ROOT, EvidenceError, dump, git, load

BASELINE = "conformance/difffuzz-baseline.json"
RULES = {"count": {"field", "surface", "key", "base", "head"}, "replay": {"id", "base", "head"},
         "known_rejection": {"base_lean_prefix"}}
SAMPLE = ("seed", "scale", "corpus", "mutants")


def rule_problems(rules) -> list[str]:
    if not isinstance(rules, list):
        return ["fuzz_ab.explained is not a list of rules"]
    errors = []
    for index, rule in enumerate(rules):
        fields = RULES.get(rule.get("kind")) if isinstance(rule, dict) else None
        if fields is None or set(rule) != fields | {"kind"}:
            errors.append(f"fuzz_ab rule {index} is not one of {sorted(RULES)} with exactly its fields: {rule!r}")
        elif rule["kind"] == "count" and rule["field"] not in ("findings", "answers"):
            errors.append(f"fuzz_ab rule {index}: a count rule names field findings or answers")
        elif rule["kind"] == "known_rejection" and not (isinstance(rule["base_lean_prefix"], str)
                                                        and rule["base_lean_prefix"].strip()):
            errors.append(f"fuzz_ab rule {index}: a known rejection names a non-empty prefix")
    return errors


def _signatures(report: dict, side: str) -> dict:
    out = {}
    for entry in report["new"]:
        if entry["signature"] in out:
            raise EvidenceError(f"the {side} report lists the new signature {entry['signature']} twice")
        out[entry["signature"]] = entry
    return out


def _replayed(report: dict, ids: set, side: str) -> dict:
    out = {}
    for row in report["baseline"]["not_reproduced"]:
        if row["id"] in out or row["id"] not in ids:
            raise EvidenceError(f"the {side} report replays {row['id']} twice or outside the baseline")
        out[row["id"]] = row
    return out


def _known_rejection(rule: dict, base_answers: dict, head_answers: dict) -> bool:
    old, new = base_answers.get("lean") or {}, head_answers.get("lean")
    return (old.get("outcome") == "error" and isinstance(old.get("text"), str)
            and old["text"].startswith(rule["base_lean_prefix"])
            and new is not None and new == head_answers.get("python")
            and base_answers.get("python") == head_answers.get("python")
            and base_answers.get("rust") == head_answers.get("rust"))


def compare(base: dict, head: dict, baseline: list[dict], rules: list[dict]) -> dict:
    """Every difference of two difffuzz reports over the same `baseline` entries, explained by a rule or not."""
    if rule_problems(rules):
        raise EvidenceError("; ".join(rule_problems(rules)))
    explained, unexplained = [], []

    def classify(row: dict, ok: bool) -> None:
        (explained if ok else unexplained).append(row)

    for field in SAMPLE:
        if base.get(field) != head.get(field):
            unexplained.append({"kind": "sample", "field": field})
    compared = sum(sum(counts.values()) for counts in head.get("mutants", {}).values())
    if compared == 0:
        unexplained.append({"kind": "sample", "field": "mutants", "problem": "the run compared no input"})
    for field in ("findings", "answers"):
        surfaces = set(base[field]) | set(head[field])
        for surface in sorted(surfaces):
            old, new = base[field].get(surface, {}), head[field].get(surface, {})
            for key in sorted(set(old) | set(new)):
                if old.get(key, 0) != new.get(key, 0):
                    row = {"kind": "count", "field": field, "surface": surface, "key": key,
                           "base": old.get(key, 0), "head": new.get(key, 0)}
                    classify(row, row in [{k: r[k] for k in row} for r in rules if r["kind"] == "count"])
    old_new, head_new = _signatures(base, "base"), _signatures(head, "head")
    for signature in sorted(head_new.keys() - old_new.keys()):
        entry = head_new[signature]
        unexplained.append({"kind": "new", "signature": signature, "surface": entry.get("surface"),
                            "classes": entry.get("classes"), "answers": entry.get("answers")})
    for signature in sorted(old_new.keys() - head_new.keys()):
        explained.append({"kind": "new", "signature": signature, "fixed_on_head": True})
    for field in ("entries", "unreviewed"):
        if base["baseline"].get(field) != head["baseline"].get(field):
            unexplained.append({"kind": "baseline", "field": field})
    if base["baseline"].get("entries") != len(baseline):
        unexplained.append({"kind": "baseline", "field": "entries", "problem": "the reports replayed another baseline"})
    ids = [entry["id"] for entry in baseline]
    if len(set(ids)) != len(ids):
        raise EvidenceError("the baseline names an entry twice")
    old_replay, new_replay = _replayed(base, set(ids), "base"), _replayed(head, set(ids), "head")
    for entry in baseline:
        old, new = old_replay.get(entry["id"]), new_replay.get(entry["id"])
        old_status, new_status = (old or {}).get("status", "reproduces"), (new or {}).get("status", "reproduces")
        if old_status == new_status and (old or {}).get("now") == (new or {}).get("now"):
            continue
        base_answers = (old or {}).get("now", {}).get("answers") or entry.get("answers") or {}
        head_answers = (new or {}).get("now", {}).get("answers") or entry.get("answers") or {}
        row = {"kind": "replay", "id": entry["id"], "base": old_status, "head": new_status,
               "base_lean": base_answers.get("lean"), "head_lean": head_answers.get("lean")}
        ok = any(rule["kind"] == "replay" and (rule["id"], rule["base"], rule["head"]) ==
                 (entry["id"], old_status, new_status) for rule in rules) or any(
            rule["kind"] == "known_rejection" and _known_rejection(rule, base_answers, head_answers)
            for rule in rules)
        classify(row, ok)
    return {"compared": compared, "explained": explained, "unexplained": unexplained}


def fuzz(root: Path, args: list[str], report: Path) -> dict:
    """One `tools/difffuzz.py` run of the checkout at `root`, with its own builds."""
    env = {**os.environ, "PATH": f"{Path.home()}/.elan/bin:{os.environ.get('PATH', '')}",
           "VE_RUST_BINARY": str(root / "rust/target/release/ve")}
    command = ["uv", "run", "--frozen", "python", "tools/difffuzz.py", *args, "--report", str(report)]
    run = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True)
    if not report.is_file():
        raise EvidenceError(f"{root} {' '.join(args)}: no report (exit {run.returncode}): "
                            f"{(run.stdout + run.stderr)[-2000:]}")
    return load(report)


def problems(evidence: dict, head: str) -> list[str]:
    """The errors of a saved fuzz A/B for the batch head `head`."""
    if not isinstance(evidence, dict):
        return ["fuzz A/B evidence is not a record"]
    errors = []
    if evidence.get("head_commit") != head:
        errors.append("fuzz A/B did not run on HEAD")
    runs = evidence.get("runs")
    if not isinstance(runs, list) or not runs:
        return errors + ["fuzz A/B ran nothing"]
    names = [run.get("run") for run in runs if isinstance(run, dict)]
    if len(names) != len(runs) or len(set(names)) != len(names):
        errors.append("fuzz A/B names a run twice or a run without a name")
    for run in runs:
        if not isinstance(run, dict) or type(run.get("compared")) is not int or run["compared"] <= 0:
            errors.append(f"fuzz A/B run {run.get('run') if isinstance(run, dict) else run!r} compared nothing")
        elif run.get("unexplained") != []:
            errors.append(f"fuzz A/B run {run['run']} has {len(run.get('unexplained') or [None])} "
                          "unexplained difference(s)")
    if evidence.get("pass") is not True:
        errors.append("fuzz A/B did not pass")
    return errors


def main(argv=None) -> int:
    from tools.evidence.config import read as read_toml

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--base-root", type=Path, required=True)
    parser.add_argument("--head-root", type=Path, default=ROOT)
    parser.add_argument("--batch", type=Path, help="the batch directory whose evidence.toml names seeds and rules")
    parser.add_argument("--seed", action="append", default=[], help="a --deep 1 seed (repeatable)")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args(argv)
    config = read_toml(args.batch).get("fuzz_ab", {}) if args.batch else {}
    rules, seeds = config.get("explained", []), [str(s) for s in config.get("seeds", [])] + args.seed
    errors = rule_problems(rules)
    if errors:
        print("\n".join(errors))
        return 1
    base_root, head_root = args.base_root.resolve(), args.head_root.resolve()
    baseline_path = base_root / BASELINE
    if baseline_path.read_bytes() != (head_root / BASELINE).read_bytes():
        print(f"the head's {BASELINE} differs from the base's: the fuzzer baseline must not change")
        return 1
    baseline = load(baseline_path)["entries"]
    runs = [["--ci"]] + [["--deep", "1", "--seed", seed, "--minimise-limit", "0"] for seed in seeds]
    with tempfile.TemporaryDirectory(prefix="ve-evidence-fuzz-ab-") as scratch:
        jobs = [(side, root, run) for run in runs for side, root in (("base", base_root), ("head", head_root))]
        with ThreadPoolExecutor(args.jobs) as pool:
            reports = list(pool.map(lambda job: fuzz(job[1], job[2], Path(scratch) / f"{job[0]}-{'-'.join(job[2])}.json"),
                                    jobs))
    rows = []
    for index, run in enumerate(runs):
        result = compare(reports[2 * index], reports[2 * index + 1], baseline, rules)
        rows.append({"run": " ".join(run), **result})
    evidence = {"base_commit": git("rev-parse", "HEAD", cwd=base_root).strip(),
                "head_commit": git("rev-parse", "HEAD", cwd=head_root).strip(),
                "baseline_sha256": hashlib.sha256(baseline_path.read_bytes()).hexdigest(), "rules": rules,
                "runs": rows}
    evidence["pass"] = not problems({**evidence, "pass": True}, evidence["head_commit"])
    dump(args.out, evidence)
    errors = problems(evidence, evidence["head_commit"])
    print("\n".join(errors) if errors else f"fuzz_ab PASS: {len(rows)} runs, "
          f"{sum(len(r['explained']) for r in rows)} explained differences; {args.out}")
    return 1 if errors else 0
