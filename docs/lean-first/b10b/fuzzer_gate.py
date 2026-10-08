"""Run the fourteen dated differential samples on the base and this batch.

Both checkouts run against the base's reviewed baseline, so every sampled input and
every replayed entry is the same on both sides (`trace_items.py`). Batch 10b's
committed baseline is the base's minus `RETIRED`: the norm-defaults decoder now
accepts a constant's `verbalisation`, as Python does (DF-19). An answer may differ
between base and head only in these ways:

- a sampled input mentioning norm-defaults whose base Lean answer is the DF-19
  rejection, whose Python and Rust answers are unchanged, and whose Lean answer
  changed (`df19`);
- a sampled input mentioning norm-defaults whose Python and Rust answers are
  unchanged and whose head Lean answer is now Python's own text for a repeated
  profile: setting `norm-defaults@0` aside used to drop every copy, so the base
  Lean accepted a repeated profile or reported a later fault (`repeated-profile`);
- a replayed `RETIRED` entry that reproduces on the base and is fixed on the head;
- a finding only the head makes, on an input DF-19 masked on the base, where the
  engines now differ in diagnostic text alone (`unmasked`: wording or fault order of
  a reviewed class, listed in the evidence).

Anything else is unexplained and fails the gate: in particular a head-only finding
of another class (an outcome or code difference), since the baseline must not grow.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

SEEDS = tuple(range(20260921, 20260931)) + tuple(range(20261001, 20261005))
SAME = ("corpus", "mutants")
RETIRED = frozenset({"environment-d253e2ea451c5fa3"})
DF19 = "fields do not match: expected [sort, description], got ["
REPEATED = "UnsupportedProfile: profiles must be sorted and unique"
TRACE = Path(__file__).with_name("trace_items.py")
BASELINE = "conformance/difffuzz-baseline.json"


def revision(root: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()


def check_baselines(base: Path, head: Path) -> None:
    """The head's committed baseline is the base's with exactly `RETIRED` removed."""
    old = json.loads((base / BASELINE).read_text())["entries"]
    new = json.loads((head / BASELINE).read_text())["entries"]
    if [e for e in old if e["id"] not in RETIRED] != new or {e["id"] for e in old} & RETIRED != RETIRED:
        raise SystemExit("the head baseline is not the base baseline less the retired entries")


def run(root: Path, baseline: Path, seed: int, scratch: Path) -> dict:
    stem = scratch / f"{root.name}-{seed}"
    report, trace, items = (stem.with_suffix(s) for s in (".json", ".trace.json", ".items.json"))
    command = [sys.executable, str(TRACE), str(root), str(trace), str(items), "--baseline", str(baseline),
               "--deep", "1", "--seed", str(seed), "--minimise-limit", "0", "--report", str(report)]
    result = subprocess.run(command, cwd=root, text=True, capture_output=True)
    if not all(path.exists() for path in (report, trace, items)):
        raise RuntimeError(f"{root.name} seed {seed}: missing output (exit {result.returncode}): "
                           f"{result.stderr[-2000:]}")
    data = json.loads(report.read_text())
    data["trace"] = json.loads(trace.read_text())
    data["items"] = json.loads(items.read_text())
    if len(data["items"]["replayed"]) != data["baseline"]["entries"]:
        raise RuntimeError(f"{root.name} seed {seed}: incomplete baseline replay records")
    for name, mutants in data["mutants"].items():
        if len(data["items"]["sampled"].get(name, ())) != sum(mutants.values()):
            raise RuntimeError(f"{root.name} seed {seed}: incomplete {name} records")
    data["exit"] = result.returncode
    return data


def explained_sample(a: dict, b: dict, *, diagnostic_finding: bool = False) -> str | None:
    """Why a sampled answer changed (`df19` or `repeated-profile`), or None if it is unexplained."""
    if "answers" not in a or "answers" not in b:
        return None
    old, new = a["answers"], b["answers"]
    lean = old.get("lean", {})
    if old.get("python") != new.get("python") or old.get("rust") != new.get("rust") or new.get("lean") == lean:
        return None
    if (lean.get("outcome") == "error" and lean.get("text", "").startswith(DF19)
            and "verbalisation" in lean["text"]
            and (new["lean"] == new["python"] or diagnostic_finding and
                 new["lean"].get("outcome") == new["python"].get("outcome") == "error" and
                 new["lean"].get("code") == new["python"].get("code"))):
        return "df19"
    if new["lean"].get("text") == new.get("python", {}).get("text") == REPEATED:
        return "repeated-profile"
    return None


def compare(base: dict, head: dict) -> dict:
    """Every difference between the two runs, split into explained and unexplained."""
    unexplained = [key for key in SAME if base[key] != head[key]]
    explained = []
    sampled_a, sampled_b = base["items"]["sampled"], head["items"]["sampled"]
    if sorted(sampled_a) != sorted(sampled_b):
        unexplained.append("sampled surfaces")
    old_signatures = {e["signature"] for e in base["new"]}
    diagnostic_inputs = {head["items"].get("new", {}).get(e["signature"])
                         for e in head["new"] if e["classes"] == ["diagnostic"]
                         and e["signature"] not in old_signatures}
    for name in sorted(set(sampled_a) & set(sampled_b)):
        rows_a, rows_b = sampled_a[name], sampled_b[name]
        if [r["input"] for r in rows_a] != [r["input"] for r in rows_b]:
            unexplained.append(f"{name}: sampled inputs")
            continue
        for index, (a, b) in enumerate(zip(rows_a, rows_b)):
            if a["answers_sha256"] == b["answers_sha256"]:
                continue
            kind = explained_sample(a, b, diagnostic_finding=a["input"] in diagnostic_inputs)
            row = {"surface": name, "index": index, "profile": a.get("profile"), "kind": kind,
                   "base_lean": a.get("answers", {}).get("lean"), "head_lean": b.get("answers", {}).get("lean"),
                   "head_lean_agrees_with_python": b.get("answers", {}).get("lean", {}).get("outcome")
                   == b.get("answers", {}).get("python", {}).get("outcome")}
            (explained if kind else unexplained).append(row)
    replay_a, replay_b = base["items"]["replayed"], head["items"]["replayed"]
    if [(r["id"], r["input"]) for r in replay_a] != [(r["id"], r["input"]) for r in replay_b]:
        unexplained.append("replayed entries")
    else:
        for a, b in zip(replay_a, replay_b):
            if a["answers_sha256"] == b["answers_sha256"]:
                continue
            row = {"replayed": a["id"], "base_status": a["status"], "head_status": b["status"]}
            ok = a["id"] in RETIRED and a["status"] == "reproduces" and b["status"] == "fixed"
            (explained if ok else unexplained).append(row)
    unexplained.extend(unmasked(base, head, explained))
    return {"explained": explained, "unexplained": unexplained}


def unmasked(base: dict, head: dict, explained: list) -> list:
    """Head findings the base did not find. One is listed (in `explained`) only if it was masked:
    its input's base Lean answer was the DF-19 rejection, and the engines now differ in text alone
    (class `diagnostic`: same outcome and code, a wording or fault-order difference). Any other is
    returned as unexplained."""
    old = {e["signature"] for e in base["new"]}
    rows = {row["input"]: row for rows in base["items"]["sampled"].values() for row in rows}
    bad = []
    for entry in head["new"]:
        if entry["signature"] in old:
            continue
        row = rows.get(head["items"].get("new", {}).get(entry["signature"]), {})
        lean = row.get("answers", {}).get("lean", {})
        masked = lean.get("outcome") == "error" and lean.get("text", "").startswith(DF19)
        listed = {"unmasked": entry["signature"], "surface": entry["surface"], "profile": entry["profile"],
                  "classes": entry["classes"], "answers": entry["answers"]}
        (explained if masked and entry["classes"] == ["diagnostic"] else bad).append(listed)
    return bad


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-root", type=Path, required=True)
    parser.add_argument("--head-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("evidence") / "fuzzer-seeds.json")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    base, head = args.base_root.resolve(), args.head_root.resolve()
    check_baselines(base, head)
    baseline = base / BASELINE
    runs: dict[tuple[str, int], dict] = {}
    with tempfile.TemporaryDirectory(prefix="ve-b10b-fuzzer-") as tmp:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            jobs = {pool.submit(run, root, baseline, seed, Path(tmp)): (side, seed)
                    for side, root in (("base", base), ("head", head)) for seed in SEEDS}
            for job in as_completed(jobs):
                side, seed = jobs[job]
                runs[(side, seed)] = job.result()
                print(f"{side} {seed} finished (exit {runs[(side, seed)]['exit']})", flush=True)
    rows = []
    for seed in SEEDS:
        a, b = runs[("base", seed)], runs[("head", seed)]
        result = compare(a, b)
        rows.append({"seed": seed, "base_exit": a["exit"], "head_exit": b["exit"],
                     "base_new": len(a["new"]), "head_new": len(b["new"]),
                     "base_only_new": len({e["signature"] for e in a["new"]} - {e["signature"] for e in b["new"]}),
                     "base_not_reproduced": sorted(e["id"] for e in a["baseline"]["not_reproduced"]),
                     "head_not_reproduced": sorted(e["id"] for e in b["baseline"]["not_reproduced"]),
                     "mutants": a["mutants"], "base_trace": a["trace"], "head_trace": b["trace"],
                     "explained": result["explained"], "unexplained": result["unexplained"]})
    evidence = {"base_commit": revision(base), "head_commit": revision(head),
                "baseline_sha256": hashlib.sha256(baseline.read_bytes()).hexdigest(),
                "head_baseline_sha256": hashlib.sha256((head / BASELINE).read_bytes()).hexdigest(),
                "retired": sorted(RETIRED), "seeds": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2) + "\n")
    bad = [row for row in rows if row["unexplained"]]
    print(f"Compared {len(rows)} date seeds; {len(bad)} have unexplained differences; "
          f"{sum(len(r['explained']) for r in rows)} explained differences. Evidence: {args.output}", flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
