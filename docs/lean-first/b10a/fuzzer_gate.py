"""Run the fourteen dated differential samples on the base and this batch.

Both checkouts must have their Lean and Rust binaries built. The script waits for
every fuzzer process, compares every sampled input and engine answer through
stable digests as well as the summaries, and writes compact evidence without
changing the fuzzer baseline.
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
COMPARE = ("corpus", "mutants", "answers", "findings")
TRACE = Path(__file__).with_name("trace_fuzzer.py")


def revision(root: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()


def baseline_hash(root: Path) -> str:
    return hashlib.sha256((root / "conformance/difffuzz-baseline.json").read_bytes()).hexdigest()


def run(root: Path, seed: int, scratch: Path) -> dict:
    report = scratch / f"{root.name}-{seed}.json"
    trace = scratch / f"{root.name}-{seed}.trace.json"
    command = [sys.executable, str(TRACE), str(root), str(trace), "--deep", "1", "--seed", str(seed),
               "--minimise-limit", "0", "--report", str(report)]
    result = subprocess.run(command, cwd=root, text=True, capture_output=True)
    if not report.exists() or not trace.exists():
        raise RuntimeError(f"{root.name} seed {seed}: missing report or trace (exit {result.returncode}): "
                           f"{result.stderr[-2000:]}")
    data = json.loads(report.read_text())
    data["trace"] = json.loads(trace.read_text())
    if data["trace"].get("baseline_replay", {}).get("count") != data["baseline"]["entries"]:
        raise RuntimeError(f"{root.name} seed {seed}: incomplete baseline replay trace")
    for name, mutants in data["mutants"].items():
        if data["trace"].get(name, {}).get("count") != sum(mutants.values()):
            raise RuntimeError(f"{root.name} seed {seed}: incomplete {name} trace")
    data["exit"] = result.returncode
    return data


def compare(base: dict, head: dict) -> list[str]:
    differences = [key for key in COMPARE if base[key] != head[key]]
    if base["trace"] != head["trace"]:
        differences.append("trace")
    for key in ("entries", "seen_in_sample", "unreviewed", "not_reproduced"):
        if base["baseline"][key] != head["baseline"][key]:
            differences.append("baseline." + key)
    if {entry["signature"] for entry in base["new"]} != {entry["signature"] for entry in head["new"]}:
        differences.append("new.signatures")
    if base["exit"] != head["exit"]:
        differences.append("exit")
    return differences


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-root", type=Path, required=True)
    parser.add_argument("--head-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("evidence") / "fuzzer-seeds.json")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    base, head = args.base_root.resolve(), args.head_root.resolve()
    if baseline_hash(base) != baseline_hash(head):
        raise SystemExit("the base and head differential baselines differ")
    runs: dict[tuple[str, int], dict] = {}
    with tempfile.TemporaryDirectory(prefix="ve-b10a-fuzzer-") as tmp:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            jobs = {pool.submit(run, root, seed, Path(tmp)): (side, seed)
                    for side, root in (("base", base), ("head", head)) for seed in SEEDS}
            for job in as_completed(jobs):
                side, seed = jobs[job]
                runs[(side, seed)] = job.result()
                print(f"{side} {seed} finished (exit {runs[(side, seed)]['exit']})", flush=True)
    rows = []
    for seed in SEEDS:
        a, b = runs[("base", seed)], runs[("head", seed)]
        rows.append({"seed": seed, "base_exit": a["exit"], "head_exit": b["exit"],
                     "base_new": len(a["new"]), "head_new": len(b["new"]),
                     "base_not_reproduced": len(a["baseline"]["not_reproduced"]),
                     "head_not_reproduced": len(b["baseline"]["not_reproduced"]),
                     "mutants": a["mutants"], "base_trace": a["trace"],
                     "head_trace": b["trace"], "differences": compare(a, b)})
    evidence = {"base_commit": revision(base), "head_commit": revision(head),
                "baseline_sha256": baseline_hash(base), "seeds": rows}
    args.output.write_text(json.dumps(evidence, indent=2) + "\n")
    bad = [row for row in rows if row["differences"]]
    print(f"Compared {len(rows)} date seeds; {len(bad)} seeds differ. Evidence: {args.output}", flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
