"""Measure a full-suite run: elapsed and CPU seconds, machine load, workers, slowest tests.

    PATH="$HOME/.elan/bin:$PATH" UV_CACHE_DIR=/tmp/ve-xdist-uv-cache uv run --frozen \
        python tools/bench/suite_time.py --label after --output tools/bench/results/suite-after.json -- -n auto

runs `python -m pytest -p no:cacheprovider -q <arguments>` in the foreground and writes the
measurement as JSON. `--junit FILE --time FILE --log FILE` instead imports a run already made
with `--junitxml` under `/usr/bin/time -f "%e wall %U user %S sys"`. A measurement, never a
test criterion: the numbers depend on the machine and its load, which the file records.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re
import resource
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]


def durations(junit: Path) -> list[tuple[str, float]]:
    rows = []
    for case in ET.parse(junit).iter("testcase"):
        path = case.get("classname", "").replace(".", "/") + ".py"
        rows.append((f"{path}::{case.get('name')}", float(case.get("time", 0))))
    return rows


def summary(log: str) -> dict:
    line = next((line for line in reversed(log.splitlines()) if re.search(r"\d+ (passed|failed)", line)), "")
    counts = {word: int(number) for number, word in re.findall(r"(\d+) (passed|failed|skipped|errors?|warnings?)", line)}
    workers = re.search(r"-n auto: (\d+) workers|created: (\d+)/\d+ workers", log)
    return {"summary": line.strip("= "), "counts": counts,
            "workers": int(next(filter(None, workers.groups()))) if workers else None}


def report(label, wall, user, system, rows, log, load_start, load_end, commit=None):
    files = Counter()
    for nodeid, seconds in rows:
        files[nodeid.split("::")[0]] += seconds
    commit = commit or subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                                      check=True, timeout=600).stdout.strip()
    return {"label": label, "commit": commit, "cpus": len(os.sched_getaffinity(0)),
            "load_start": load_start, "load_end": load_end,
            "wall_seconds": round(wall, 1), "cpu_seconds": {"user": round(user, 1), "system": round(system, 1),
                                                            "total": round(user + system, 1)},
            **summary(log), "test_seconds_sum": round(sum(s for _, s in rows), 1),
            "slowest_tests": [{"nodeid": n, "seconds": round(s, 1)}
                              for n, s in sorted(rows, key=lambda row: -row[1])[:10]],
            "slowest_files": [{"file": f, "seconds": round(s, 1)} for f, s in files.most_common(10)]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--label", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--junit", type=Path)
    parser.add_argument("--time", type=Path)
    parser.add_argument("--log", type=Path)
    parser.add_argument("--load", nargs=2, type=float, metavar=("START", "END"),
                        help="1-minute load averages at the start and end of an imported run")
    parser.add_argument("--commit", help="the commit an imported run tested")
    parser.add_argument("--workers", type=int, help="the xdist workers of an imported run")
    parser.add_argument("pytest", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.junit:
        wall, user, system = map(float, re.match(r"([\d.]+) wall ([\d.]+) user ([\d.]+) sys",
                                                 args.time.read_text()).groups())
        load = args.load or (None, None)
        result = report(args.label, wall, user, system, durations(args.junit), args.log.read_text(), *load,
                        commit=args.commit)
        result["workers"] = result["workers"] or args.workers
    else:
        with tempfile.TemporaryDirectory() as directory:
            junit = Path(directory) / "junit.xml"
            load_start = os.getloadavg()[0]
            before, started = resource.getrusage(resource.RUSAGE_CHILDREN), time.monotonic()
            done = subprocess.run([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q",
                                   f"--junitxml={junit}", *[a for a in args.pytest if a != "--"]],
                                  cwd=ROOT, capture_output=True, text=True, timeout=6 * 3600)
            wall, after = time.monotonic() - started, resource.getrusage(resource.RUSAGE_CHILDREN)
            result = report(args.label, wall, after.ru_utime - before.ru_utime, after.ru_stime - before.ru_stime,
                            durations(junit), done.stdout + done.stderr, load_start, os.getloadavg()[0])
            result["returncode"] = done.returncode
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("wall_seconds", "cpu_seconds", "summary", "workers")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
