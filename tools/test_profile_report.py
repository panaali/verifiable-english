#!/usr/bin/env python3
"""Summarise the JSON-lines files `tools/pytest_profile.py` writes.

    python3 tools/test_profile_report.py DIR [--top 20] [--json OUT]

Prints the slowest tests and files (wall seconds of setup + call + teardown,
summed over a file's tests), child processes by executable, and each test's
wall time split by category: Lean routes and runners, the Rust checker,
builds (lake, cargo), child Python processes, other tools, and the remainder,
which is Python work in the test process (or waiting on the Lean service,
whose requests are not timed one by one). A test whose children ran in
parallel has its child time scaled down to its own wall time.

The suite's CPU is that of the xdist workers (or the single pytest process),
read from the controller's records: it includes every descendant.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import statistics


def load(directory: Path):
    tests, procs = {}, []
    for path in sorted(directory.glob("*.jsonl")):
        controller = path.name.startswith("main-")
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except ValueError:
                continue  # a worker killed mid-line
            if record["kind"] == "test":
                tests[record["nodeid"]] = record
            else:
                procs.append({**record, "controller": controller})
    return tests, procs


def wall(record) -> float:
    return sum(record.get(phase, 0.0) for phase in ("setup", "call", "teardown"))


def category(exe: str) -> str:
    if exe == "ve_service":
        return "lean service (CPU)"
    if exe.startswith("ve_") or exe in ("lean", "leanc"):
        return "lean route / runner"
    if exe == "ve":
        return "rust checker"
    if exe in ("lake", "cargo", "rustc"):
        return "build (lake/cargo)"
    if exe.startswith("python") or exe == "uv":
        return "child python"
    if exe == "git":
        return "git"
    return "other"


REMAINDER = "python in the test process (remainder)"


def summarise(tests, procs, top=20):
    by_file = defaultdict(lambda: [0.0, 0])
    for nodeid, record in tests.items():
        entry = by_file[nodeid.split("::")[0]]
        entry[0] += wall(record)
        entry[1] += 1
    in_tests = [p for p in procs if p["test"] is not None]
    by_exe = defaultdict(list)
    for proc in in_tests:
        by_exe[proc["exe"]].append(proc)
    exes = []
    for exe, rows in by_exe.items():
        walls = sorted(r["wall"] for r in rows)
        cpus = [r["cpu"] for r in rows if r["cpu"] is not None]
        exes.append({"exe": exe, "category": category(exe), "count": len(rows),
                     "wall": sum(walls), "cpu": sum(cpus),
                     "median_wall": statistics.median(walls), "min_wall": walls[0]})
    exes.sort(key=lambda e: -e["wall"])
    # Each test's wall time split among the processes it started; the service by its CPU.
    per_test = defaultdict(lambda: defaultdict(float))
    for proc in in_tests:
        seconds = (proc["cpu"] or 0.0) if proc["exe"] == "ve_service" else proc["wall"]
        per_test[proc["test"]][category(proc["exe"])] += seconds
    categories = defaultdict(float)
    for nodeid, record in tests.items():
        seconds, children = wall(record), per_test.get(nodeid, {})
        spent = sum(children.values())
        scale = min(1.0, seconds / spent) if spent else 0.0
        for name, value in children.items():
            categories[name] += value * scale
        categories[REMAINDER] += max(0.0, seconds - spent)
    suite = [p for p in procs if p["controller"] and p["test"] is None and category(p["exe"]) == "child python"]
    return {
        "tests": len(tests), "total_test_seconds": sum(wall(r) for r in tests.values()),
        "suite_cpu": sum(p["cpu"] or 0.0 for p in suite) or None,
        "self_cpu": sum(r.get("self_cpu", 0.0) for r in tests.values()),
        "child_cpu": sum(r.get("child_cpu", 0.0) for r in tests.values()),
        "slowest_tests": sorted(((wall(r), n) for n, r in tests.items()), reverse=True)[:top],
        "slowest_files": sorted(((s, c, f) for f, (s, c) in by_file.items()), reverse=True)[:top],
        "files": {f: s for f, (s, c) in by_file.items()},
        "executables": exes,
        "categories": dict(sorted(categories.items(), key=lambda kv: -kv[1])),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    summary = summarise(*load(args.directory), top=args.top)
    cpu = summary["suite_cpu"]
    print(f"{summary['tests']} tests, {summary['total_test_seconds']:.0f} s of test wall time; "
          f"suite CPU {'unknown' if cpu is None else f'{cpu:.0f} s'} (in tests: worker "
          f"{summary['self_cpu']:.0f} s, children {summary['child_cpu']:.0f} s)")
    print("\nslowest tests (s):")
    for seconds, nodeid in summary["slowest_tests"]:
        print(f"  {seconds:8.1f}  {nodeid}")
    print("\nslowest files (s, tests):")
    for seconds, count, name in summary["slowest_files"]:
        print(f"  {seconds:8.1f}  {count:5d}  {name}")
    print("\nchild processes started by tests (count, wall s, cpu s, median wall s, min wall s):")
    for e in summary["executables"][:args.top]:
        print(f"  {e['exe']:28s} {e['count']:7d} {e['wall']:9.1f} {e['cpu']:9.1f} "
              f"{e['median_wall']:7.3f} {e['min_wall']:7.3f}  [{e['category']}]")
    print("\ntest wall time by category (s):")
    for name, seconds in summary["categories"].items():
        print(f"  {seconds:9.1f}  {name}")
    if args.json:
        args.json.write_text(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
