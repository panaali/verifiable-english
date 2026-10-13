"""Save or check batch 14b gate evidence against a pinned base and raw archive.

Run after the clean-HEAD release gate::

    python docs/lean-first/b14b/evidence_manifest.py --raw /tmp/lf14b-evidence-worktree/raw \
      --write /tmp/lf14b-evidence-worktree/batch-manifest.json

At batch review or merge, use ``--check`` with that manifest. This is a batch
evidence check, not a permanent test of a report's prose (decision D4).
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "docs/lean-first/b14b/evidence"
BASE = "f1b719c7"
CORPORA = {
    "probe": 18870,
    "conformance": 39612,
    "readings": 1137,
    "discourse": 6350,
    "rights": 2500,
    "quantity": 25726,
    "norm-defaults": 2020,
    "document": 3632,
    "pilots": 486,
}
FUZZ_RUNS = ["ci"] + [f"deep-1---seed-202609{day}" for day in range(26, 31)] + [
    f"deep-1---seed-202610{day:02d}" for day in range(1, 10)]


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True,
                          check=True).stdout.strip()


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(raw: Path) -> dict:
    head = git("rev-parse", "HEAD")
    if subprocess.run(["git", "merge-base", "--is-ancestor", BASE, head],
                      cwd=ROOT).returncode != 0:
        raise ValueError("the pinned batch base is not an ancestor of HEAD")
    if git("status", "--porcelain"):
        raise ValueError("the task worktree is not clean")
    gate_path = ROOT / "gate-result.json"
    gate = read(gate_path)
    if gate.get("commit_sha") != head or gate.get("dirty") is not False or gate.get("status") != "passed":
        raise ValueError("full release gate did not pass on the clean final HEAD")
    if gate.get("stages") != ["toolchains", "lean_build", "lean_audit", "rust_build", "cargo_test", "pytest"]:
        raise ValueError("release gate stages are incomplete")
    comparisons = {}
    for corpus, expected in CORPORA.items():
        path = EVIDENCE / f"{corpus}-compare.json"
        row = read(path)
        if row.get("unlisted") != 0 or sum(row.get("records", {}).values()) != expected:
            raise ValueError(f"{corpus}: incomplete or unlisted A/B comparison")
        if corpus == "pilots":
            if row.get("totals") != {"same": 480, "unavailable": 6} or len(row.get("differences", [])) != 6:
                raise ValueError("historical pilot exceptions differ from R7 list")
        elif row.get("totals") != {"same": expected} or row.get("unavailable_both"):
            raise ValueError(f"{corpus}: changed or unavailable A/B outcome")
        comparisons[corpus] = {"records": expected, "sha256": digest(path), "totals": row["totals"]}
    fuzz_path = EVIDENCE / "difffuzz-ab.json"
    fuzz = read(fuzz_path)
    runs = fuzz.get("runs", [])
    if fuzz.get("ok") is not True or len(runs) != 15 or any(
        not row.get("ok") or row.get("head_only_new") or row.get("head_not_reproduced")
        for row in runs
    ):
        raise ValueError("CI plus 14 date-seed differential baseline grew")
    own = read(EVIDENCE / "corpus-ab.json")
    if (own.get("documents") != 150 or own.get("records") != 1350
            or len(own.get("differences", [])) != 16):
        raise ValueError("own corpus's listed changes changed")
    fallback = read(EVIDENCE / "fallback-compare.json")
    if (fallback.get("documents") != 150 or fallback.get("records") != 1350
            or fallback.get("identical") is not True or fallback.get("differences")):
        raise ValueError("retained Python route differs from the base recording")
    pilots = read(EVIDENCE / "pilots-delta.json")
    if len(pilots.get("unavailable", [])) != 6:
        raise ValueError("R7 pilot listing changed")
    for name, key in (("agent-policy", "42/42"), ("eligibility", "269/269")):
        row = read(EVIDENCE / f"{name}-ab.json")
        if row.get("semantic_equal") is not True or row.get("answer_key_base") != key or row.get("answer_key_head") != key:
            raise ValueError(f"{name}: answer-key A/B changed")
    latency = read(EVIDENCE / "latency.json")
    if latency.get("pass") is not True:
        raise ValueError("latency budget did not pass")
    mutants = read(EVIDENCE / "mutants.json").get("mutants", [])
    if len(mutants) < 3 or not {"ve/norms.py", "lean/VE/Norms/Family.lean"} <= {
        row.get("file") for row in mutants
    } or any(row.get("planted", {}).get("exit") in (None, 0) or row.get("restored", {}).get("exit") != 0
             for row in mutants):
        raise ValueError("seeded faults are missing, uncaught or not restored")
    archive = {}
    for corpus in CORPORA:
        for side in ("base", "head"):
            path = raw / f"{side}-{corpus}.jsonl.gz"
            with gzip.open(path, "rb") as stream:
                count = sum(1 for _ in stream)
            per_side = CORPORA[corpus]
            if count != per_side:
                raise ValueError(f"{path}: {count} rows, expected {per_side}")
            archive[path.name] = {"records": count, "bytes": path.stat().st_size, "sha256": digest(path)}
    fuzz_archive = {}
    for side in ("base", "head"):
        for run in FUZZ_RUNS:
            name = f"{side}---{run}.json"
            path = raw.parent / "difffuzz" / name
            report = read(path)
            if not isinstance(report.get("findings"), dict) or "baseline" not in report:
                raise ValueError(f"{path}: incomplete differential recording")
            fuzz_archive[name] = {"bytes": path.stat().st_size, "sha256": digest(path)}
    return {
        "base": git("rev-parse", BASE), "head": head,
        "commits_no_merges": git("log", "--no-merges", "--format=%H", f"{BASE}..HEAD").splitlines(),
        "gate": {"sha256": digest(gate_path), "status": gate["status"], "counts": gate.get("counts")},
        "comparisons": comparisons,
        "own_corpus": {"records": 1350, "same": 1334, "listed": 16,
                       "sha256": digest(EVIDENCE / "corpus-ab.json")},
        "fallback": {"records": 1350, "same": 1350, "sha256": digest(EVIDENCE / "fallback-compare.json")},
        "difffuzz": {"runs": len(runs), "sha256": digest(fuzz_path), "head_only": 0},
        "pilots_delta_sha256": digest(EVIDENCE / "pilots-delta.json"),
        "latency_sha256": digest(EVIDENCE / "latency.json"),
        "mutants_sha256": digest(EVIDENCE / "mutants.json"),
        "raw": archive,
        "difffuzz_raw": fuzz_archive,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raw", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    args = parser.parse_args()
    current = snapshot(args.raw)
    if args.write:
        args.write.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
    elif read(args.check) != current:
        raise ValueError("saved batch manifest differs from final HEAD evidence")
    print(f"batch evidence PASS: {len(current['commits_no_merges'])} commits, "
          f"{len(current['comparisons'])} A/B corpora, {current['difffuzz']['runs']} fuzz runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
