#!/usr/bin/env python3
"""Summarise the JSON-lines files `tools/pytest_profile.py` writes.

    python3 tools/test_profile_report.py DIR [--top 20] [--json OUT]

Prints the slowest tests and files (wall seconds of setup + call + teardown,
summed over a file's tests), child-process time by executable, and time by
category: Lean routes and service, the Rust checker, builds (lake, cargo),
child Python processes, other tools, and the remainder of each test's wall
time, which is Python work in the test process or waiting.
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
                procs.append(record)
    return tests, procs


def wall(record) -> float:
    return sum(record.get(phase, 0.0) for phase in ("setup", "call", "teardown"))


def category(exe: str) -> str:
    if exe == "ve_service":
        return "lean service"
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


def summarise(tests, procs, top=20):
    by_file = defaultdict(lambda: [0.0, 0])
    for nodeid, record in tests.items():
        entry = by_file[nodeid.split("::")[0]]
        entry[0] += wall(record)
        entry[1] += 1
    by_exe = defaultdict(list)
    for proc in procs:
        by_exe[proc["exe"]].append(proc)
    exes = []
    for exe, rows in by_exe.items():
        walls = sorted(r["wall"] for r in rows)
        cpus = [r["cpu"] for r in rows if r["cpu"] is not None]
        exes.append({"exe": exe, "category": category(exe), "count": len(rows),
                     "wall": sum(walls), "cpu": sum(cpus),
                     "median_wall": statistics.median(walls), "min_wall": walls[0]})
    exes.sort(key=lambda e: -e["wall"])
    # Child processes run inside a test's wall time (the service also between tests).
    categories = defaultdict(float)
    for e in exes:
        categories[e["category"]] += e["wall"]
    total = sum(wall(r) for r in tests.values())
    child = sum(e["wall"] for e in exes if e["exe"] != "ve_service")
    categories["python in the test process (remainder)"] = max(0.0, total - child)
    return {
        "tests": len(tests), "total_test_seconds": total,
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
    print(f"{summary['tests']} tests, {summary['total_test_seconds']:.0f} s of test wall time "
          f"(worker CPU {summary['self_cpu']:.0f} s, child CPU {summary['child_cpu']:.0f} s)")
    print("\nslowest tests (s):")
    for seconds, nodeid in summary["slowest_tests"]:
        print(f"  {seconds:8.1f}  {nodeid}")
    print("\nslowest files (s, tests):")
    for seconds, count, name in summary["slowest_files"]:
        print(f"  {seconds:8.1f}  {count:5d}  {name}")
    print("\nchild processes (count, wall s, cpu s, median wall s, min wall s):")
    for e in summary["executables"][:args.top]:
        print(f"  {e['exe']:28s} {e['count']:7d} {e['wall']:9.1f} {e['cpu']:9.1f} "
              f"{e['median_wall']:7.3f} {e['min_wall']:7.3f}  [{e['category']}]")
    print("\ntime by category (s):")
    for name, seconds in summary["categories"].items():
        print(f"  {seconds:9.1f}  {name}")
    if args.json:
        args.json.write_text(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
