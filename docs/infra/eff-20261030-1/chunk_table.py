"""Step 1 (and step 5) table of eff-20261030-1: how much of each heavy test file's wall time chunks could cut.

    uv run python docs/infra/eff-20261030-1/chunk_table.py <log dir> [--run "<run>"] [--json OUT] [--data OUT]

Reads the logs measure.sh wrote (pytest -n 0 -v --durations=0 per file) and prints one row per file: collected node
count, wall seconds (pytest's own "in N s"), the summed setup/call/teardown seconds, the setup a chunk repeats, the
largest single node, and for k = 2, 3, 4 the best chunk wall time: the per-process setup each chunk repeats plus the
larger of the heaviest chunk under a longest-first split of the per-node seconds and the largest single node. Then
the stop rule over the top 4 files (by the Actions runner seconds of the task) and, with --data, the decisions file
tools/select_tests.py reads (tools/test-chunks.json): a file is `never` chunked when its best k cuts less than
MIN_CUT of its wall time (the repeated setup eats the split).

The setup a chunk repeats: the process time outside the per-node durations (collection, session start) plus every
setup of SHARED_SECONDS or more that at most SHARED_COUNT nodes have (module or session fixtures: paid once per
process, so once per chunk); a large setup that many nodes have is per-test and splits with them. A module fixture
that does the selected tests' own work (tests/lean_pool.py `elaborate_selected`: it elaborates only what its process
runs) is divisible, not repeated: for such files the shared setup is spread over the nodes it serves.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import statistics

ROOT = Path(__file__).resolve().parents[3]
# Runner seconds per file on a 4-vCPU Actions runner (gha-tests/unit-seconds.json, the task's table, 2026-10-30).
ACTIONS_SECONDS = {
    "tests/test_consolidation_tools.py": 1918, "tests/test_acts_vocab_mutants.py": 1383,
    "tests/test_readings_rd6b_differential.py": 1219, "tests/test_english_evidence.py": 1002,
    "tests/test_trust_mutants.py": 980, "tests/test_defaults_checks.py": 979,
    "tests/test_speech_polar_lean.py": 934, "tests/test_lean_conformance.py": 701,
}
SHARED_SECONDS = 1.0
SHARED_COUNT = 10
KS = (2, 3, 4)
STOP_CUT = 0.35  # the task's stop rule: the top 4 together below a 35% cut
MIN_CUT = 0.20  # a file whose best k cuts less than this is setup-dominated: never chunked
DURATION = re.compile(r"^(?P<seconds>\d+(?:\.\d+)?)s (?P<when>setup|call|teardown)\s+(?P<nodeid>tests/\S.*)$")
SUMMARY = re.compile(r"^=+ (?P<counts>.*?) in (?P<seconds>\d+(?:\.\d+)?)s(?: \([0-9:]+\))? =+$")
OUTCOME = re.compile(r"^(?P<nodeid>tests/\S+?::\S.*?) (?P<outcome>PASSED|FAILED|SKIPPED|ERROR|XFAIL|XPASS)\b")


def parse(log: Path) -> dict:
    nodes: dict[str, dict[str, float]] = {}
    order, outcomes, wall, counts = [], {}, None, ""
    for line in log.read_text(errors="replace").splitlines():
        if found := DURATION.match(line):
            nodes.setdefault(found["nodeid"].strip(), {})[found["when"]] = float(found["seconds"])
        elif found := SUMMARY.match(line):
            wall, counts = float(found["seconds"]), found["counts"]
        elif found := OUTCOME.match(line):
            outcomes[found["nodeid"]] = found["outcome"]
            order.append(found["nodeid"])
    return {"nodes": nodes, "order": order, "outcomes": outcomes, "wall": wall, "counts": counts,
            "where": "ve-mac-1" if "pytest on ve-mac-1" in log.read_text(errors="replace") else "local"}


def longest_first(costs: list[float], k: int) -> float:
    bins = [0.0] * k
    for cost in sorted(costs, reverse=True):
        bins[bins.index(min(bins))] += cost
    return max(bins)


def row(file: str, parsed: dict) -> dict:
    nodes = parsed["nodes"]
    total = {nodeid: sum(times.values()) for nodeid, times in nodes.items()}
    setups = {nodeid: times.get("setup", 0.0) for nodeid, times in nodes.items()}
    big = [nodeid for nodeid, seconds in setups.items() if seconds >= SHARED_SECONDS]
    shared = sum(setups[nodeid] for nodeid in big) if len(big) <= SHARED_COUNT else 0.0
    divisible = "lean_pool.elaborate_selected" in (ROOT / file).read_text()
    outside = max(0.0, (parsed["wall"] or 0.0) - sum(total.values()))
    repeated = outside + (0.0 if divisible else shared)
    # Per-node cost without the shared setup (it is in `repeated`, or spread over the nodes when divisible).
    costs = {nodeid: total[nodeid] - (setups[nodeid] if nodeid in big and len(big) <= SHARED_COUNT else 0.0)
             for nodeid in total}
    if divisible and shared:
        costs = {nodeid: cost + shared / len(costs) for nodeid, cost in costs.items()}
    largest = max(costs.items(), key=lambda item: item[1]) if costs else ("", 0.0)
    wall = parsed["wall"] or 0.0
    best = {k: round(repeated + max(longest_first(list(costs.values()), k), largest[1]), 1) for k in KS}
    best_k = min(KS, key=lambda k: (best[k], k))
    return {"file": file, "where": parsed["where"], "nodes": len(nodes), "counts": parsed["counts"],
            "wall_seconds": round(wall, 1), "node_seconds": round(sum(total.values()), 1),
            "outside_seconds": round(outside, 1), "shared_setup_seconds": round(shared, 1),
            "setup_divisible": divisible, "setup_seconds": round(repeated, 1),
            "largest_node": largest[0], "largest_node_seconds": round(largest[1], 1),
            "median_node_seconds": round(statistics.median(costs.values()), 3) if costs else 0.0,
            "best_wall": best, "best_k": best_k,
            "best_cut": round(1 - best[best_k] / wall, 3) if wall else 0.0,
            "largest_over_half": largest[1] > wall / 2}


def reason(r: dict) -> str | None:
    """Why a file is never chunked: its best k saves less than MIN_CUT, because of one node or of the setup."""
    if r["best_cut"] >= MIN_CUT:
        return None
    if r["largest_node_seconds"] >= r["setup_seconds"]:
        return (f"one node is {r['largest_node_seconds']} of its {r['wall_seconds']} s ({r['largest_node']}): "
                f"no split ends before it")
    return f"each chunk would repeat {r['setup_seconds']} s of setup of its {r['wall_seconds']} s"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("logs", type=Path)
    parser.add_argument("--run", default="")
    parser.add_argument("--json", type=Path)
    parser.add_argument("--data", type=Path)
    args = parser.parse_args()
    rows = []
    for file in ACTIONS_SECONDS:
        log = args.logs / (Path(file).stem + ".log")
        if log.exists():
            rows.append(row(file, parse(log)))
    print("| file | where | nodes | wall s | node s | repeated setup s | largest node s | k=2 | k=3 | k=4 | best cut |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['file']} | {r['where']} | {r['nodes']} | {r['wall_seconds']} | {r['node_seconds']} | "
              f"{r['setup_seconds']}{' (divisible)' if r['setup_divisible'] else ''} | {r['largest_node_seconds']} | "
              + " | ".join(str(r["best_wall"][k]) for k in KS) + f" | {r['best_cut']:.0%} (k={r['best_k']}) |")
    top = [r for r in rows if r["file"] in sorted(ACTIONS_SECONDS, key=ACTIONS_SECONDS.get, reverse=True)[:4]]
    before, after = sum(r["wall_seconds"] for r in top), sum(r["best_wall"][r["best_k"]] for r in top)
    cut = 1 - after / before if before else 0.0
    halves = len(top) == 4 and all(r["largest_over_half"] for r in top)
    stop = len(top) < 4 or cut < STOP_CUT or halves
    print(f"\ntop 4: {before:.0f} s -> {after:.0f} s at each file's best k: cut {cut:.0%} "
          f"(stop rule: < {STOP_CUT:.0%}, or every top-4 file has a node above half its wall: {halves}) -> "
          f"{'STOP' if stop else 'BUILD'}")
    if args.json:
        args.json.write_text(json.dumps({"run": args.run, "rows": rows, "top4": {
            "before": round(before, 1), "after": round(after, 1), "cut": round(cut, 3), "stop": stop}}, indent=1) + "\n")
    if args.data:
        files = {r["file"]: {"run": args.run, "wall_seconds": r["wall_seconds"], "setup_seconds": r["setup_seconds"],
                             "largest_node_seconds": r["largest_node_seconds"], "best_k": r["best_k"],
                             "max_chunks": r["best_k"], "best_cut": r["best_cut"],
                             "never": r["best_cut"] < MIN_CUT, "reason": reason(r)} for r in rows}
        args.data.write_text(json.dumps({
            "format": "ve-test-chunks@1", "run": args.run,
            "source": "docs/infra/eff-20261030-1/chunk_table.py over docs/infra/eff-20261030-1/measure.sh logs; "
                      f"never = best cut below {MIN_CUT:.0%}; max_chunks = the best k of 2-4",
            "files": files}, indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
