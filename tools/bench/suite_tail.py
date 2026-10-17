"""Measure the idle tail of a full-suite run: when each xdist worker finishes, and how busy the machine is.

    PATH="$HOME/.elan/bin:$PATH" uv run --frozen python tools/bench/suite_tail.py run \
        --label before --workers 8 --output docs/test-tail/suite-before.json --profile /tmp/ve-tail-before

runs the gate's pytest command (`tools.gate.pytest_args`, the same plugins, prebuilt checkers) on
`--workers` xdist workers with the profile plugin (`tools/pytest_profile.py`), samples the machine's CPU
(/proc/stat) every second, and writes one JSON: wall seconds, the outcome counts, the machine's busy
CPU and 1-minute load per minute, the workers' occupancy per minute (the share of worker-seconds spent
inside a test), when each worker finished its last test, and the slowest tests (setup + call +
teardown). `durations PROFILE [PROFILE ...] --output tools/test-durations.json` writes the durations file
that `tools/test_schedule.py` orders the suite by (each test's longest time among the runs; `--previous FILE`
counts an earlier file as one more run; `--log` reads the times a `--durations=0 --durations-min=0` run
printed instead of a profile).

A run elsewhere (the Mac test runner, whose output streams back) is measured from its `-v` output:
`... pytest -v -n 9 --durations=0 --durations-min=0 | suite_tail.py stamp --output LOG` writes each line with
the time it arrived, and `tail LOG` reads when each xdist worker finished its last test: the suite's wall, and
its tail, the seconds from the moment fewer than `--busy` workers (default 4) still had tests to the end. The
output arrives in blocks, so the times a line arrived are coarse; each worker's finish is also read as the sum of
the seconds of the tests it ran (`--durations`), as a worker runs its tests back to back.
A measurement, never a test criterion: the numbers depend on the machine and its load, which the file records.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools import gate, gate_collection, nested_pytest, test_schedule  # noqa: E402

SLOWEST = 40


def cpu_times() -> tuple[int, int]:
    """(busy, total) jiffies of the whole machine since boot."""
    fields = [int(value) for value in Path("/proc/stat").read_text().splitlines()[0].split()[1:]]
    idle = fields[3] + fields[4]  # idle + iowait
    return sum(fields) - idle, sum(fields)


class Sampler(threading.Thread):
    """The machine's busy CPU share each second and its 1-minute load, until stopped."""

    def __init__(self):
        super().__init__(daemon=True)
        self.samples: list[tuple[float, float, float]] = []
        self.stopped = threading.Event()

    def run(self):
        last = cpu_times()
        while not self.stopped.wait(1.0):
            now = cpu_times()
            busy, total = now[0] - last[0], now[1] - last[1]
            self.samples.append((time.time(), busy / total if total else 0.0, os.getloadavg()[0]))
            last = now


def records(profile: Path) -> list[dict]:
    """The profile plugin's test records, each with its worker (the file's name before the pid)."""
    rows = []
    for path in sorted(profile.glob("*.jsonl")):
        worker = path.stem.rsplit("-", 1)[0]
        for line in path.read_text().splitlines():
            row = json.loads(line)
            if row.get("kind") == "test":
                rows.append({**row, "worker": worker})
    return rows


def seconds(row: dict) -> float:
    return row.get("setup", 0.0) + row.get("call", 0.0) + row.get("teardown", 0.0)


def per_minute(values: list[tuple[float, float]], start: float) -> list[float]:
    buckets = defaultdict(list)
    for at, value in values:
        buckets[int((at - start) // 60)].append(value)
    return [round(100 * sum(buckets[m]) / len(buckets[m]), 1) if buckets[m] else 0.0
            for m in range(max(buckets) + 1)] if buckets else []


def occupancy(rows: list[dict], workers: int, start: float, end: float) -> list[float]:
    """Per minute of the run, the percentage of worker-seconds spent inside a test."""
    minutes = max(1, math.ceil((end - start) / 60))
    busy = [0.0] * minutes
    for row in rows:
        a, b = row["start"] - start, row["end"] - start
        while a < b:
            minute = int(a // 60)
            if minute >= minutes:
                break
            step = min(b, (minute + 1) * 60) - a
            busy[minute] += step
            a += step
    span = [min(60.0, (end - start) - 60 * m) for m in range(minutes)]
    return [round(100 * busy[m] / (workers * span[m]), 1) if span[m] > 0 else 0.0 for m in range(minutes)]


def summarise(label: str, rows: list[dict], events: dict, *, workers: int, start: float, end: float,
              samples: list, returncode: int) -> dict:
    finished = defaultdict(float)
    for row in rows:
        finished[row["worker"]] = max(finished[row["worker"]], row["end"] - start)
    outcomes = Counter(row["outcome"] for row in events.get("tests", {}).values())
    collections = list(events.get("workers", {}).values())
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                            check=True).stdout.strip()
    slowest = sorted(rows, key=lambda row: (-seconds(row), row["nodeid"]))[:SLOWEST]
    return {"label": label, "commit": commit, "cpus": len(os.sched_getaffinity(0)), "workers": workers,
            "returncode": returncode, "wall_seconds": round(end - start, 1),
            "tests": len(rows), "outcomes": dict(sorted(outcomes.items())),
            "workers_collected_alike": len(collections) == workers and all(c == collections[0] for c in collections),
            "test_seconds_sum": round(sum(seconds(row) for row in rows), 1),
            "setup_seconds_sum": round(sum(row.get("setup", 0.0) for row in rows), 1),
            "worker_finished_seconds": {worker: round(at, 1) for worker, at in sorted(finished.items())},
            "machine_busy_percent_per_minute": per_minute([(at, busy) for at, busy, _ in samples], start),
            "load_per_minute": [round(value / 100, 1) for value in per_minute([(at, load) for at, _, load in samples], start)],
            "worker_occupancy_percent_per_minute": occupancy(rows, workers, start, end),
            "slowest": [{"nodeid": row["nodeid"], "seconds": round(seconds(row), 1),
                         "setup": round(row.get("setup", 0.0), 1), "call": round(row.get("call", 0.0), 1),
                         "worker": row["worker"], "started_at": round(row["start"] - start, 1)}
                        for row in slowest]}


def run(args) -> int:
    profile, events_file = args.profile, args.profile / "gate-events.json"
    profile.mkdir(parents=True, exist_ok=False)
    rust = ROOT / "rust/target/release/ve"
    env = nested_pytest.environment(os.environ, VE_GATE_PYTEST_RESULT=str(events_file), VE_TEST_PROFILE_DIR=str(profile),
                                    VE_NATIVE_PREBUILT="1", VE_LEAN_PREBUILT="1", VE_RUST_PREBUILT="1",
                                    VE_RUST_BINARY=str(rust))
    command = nested_pytest.command(["-p", "tools.pytest_profile", *gate.pytest_args(args.files or None)],
                                    workers=args.workers, xdist=True)
    sampler = Sampler()
    sampler.start()
    start = time.time()
    with open(profile / "pytest.log", "w") as log:
        done = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    end = time.time()
    sampler.stopped.set()
    sampler.join()
    events = json.loads(events_file.read_text()) if events_file.exists() else {}
    result = summarise(args.label, records(profile), events, workers=args.workers, start=start, end=end,
                       samples=sampler.samples, returncode=done.returncode)
    args.output.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({key: result[key] for key in ("wall_seconds", "tests", "outcomes", "returncode",
                                                   "worker_finished_seconds")}))
    return 0


def durations(args) -> int:
    """The durations file from one or more profiled runs: each test's longest time among them. A test that
    pays a cost its process shares with other tests (a module fixture, a module-level cache) pays it only
    where it runs first; started early it cannot leave a tail, started late on the strength of a cheap run
    it can. A test the gate's collection baseline no longer has (renamed, split or removed) is left out.

    With `--previous`, an earlier durations file counts as one more run (of the tests it records) and keeps
    its estimate of an unrecorded test: profiling a few changed files adds the times of their new and split
    tests without forgetting the rest of the suite, or a cold time that this run measured warm."""
    current = set(json.loads(args.collection.read_text()) if args.collection is not None
                  else gate_collection.collect(ROOT))
    timed: dict[str, float] = {}
    runs = [[(row["nodeid"], seconds(row)) for row in records(profile)] for profile in args.profile]
    runs += [list(logged_seconds(log.read_text()).items()) for log in args.log]
    if not runs:
        raise SystemExit("no profile directory and no --log")
    for run_seconds in runs:
        for nodeid, value in run_seconds:
            if nodeid in current:
                timed[nodeid] = max(timed.get(nodeid, 0.0), value)
    unrecorded = None
    if args.previous is not None:
        previous, unrecorded = test_schedule.read_estimates(args.previous)
        if not previous:
            raise SystemExit(f"{args.previous}: not a durations file")
        for nodeid, value in previous.items():
            if nodeid in current:
                timed[nodeid] = max(timed.get(nodeid, 0.0), value)
    args.output.write_text(test_schedule.durations_text(timed, source=args.source, unrecorded=unrecorded))
    kept = sum(value >= test_schedule.RECORDED_SECONDS for value in timed.values())
    print(f"wrote {kept} of {len(timed)} tests to {args.output}")
    return 0


# A line of pytest's `--durations` table, and of `-v` output under xdist, after `stamp`'s time.
DURATION_LINE = re.compile(r"(\d+\.\d+)s (setup|call|teardown) +(\S.*)")
RESULT_LINE = re.compile(r"\[(gw\d+)\] \[ *\d+%\] (PASSED|FAILED|SKIPPED|ERROR|XFAIL|XPASS) (\S.*)")


def logged_seconds(text: str) -> dict[str, float]:
    """Setup + call + teardown seconds per test ID from the `--durations=0 --durations-min=0` table of a run's
    output (with or without `stamp`'s times)."""
    timed: dict[str, float] = defaultdict(float)
    for line in text.splitlines():
        found = DURATION_LINE.fullmatch(unstamped(line)[1])
        if found:
            timed[found.group(3)] += float(found.group(1))
    return dict(timed)


def unstamped(line: str) -> tuple[float | None, str]:
    """(the time `stamp` wrote before the line, or None; the line as pytest printed it)."""
    head, _, rest = line.partition(" ")
    try:
        return float(head), rest
    except ValueError:
        return None, line


def stamp(args) -> int:
    """Copy standard input to standard output and to `--output`, each line after the time it arrived."""
    with open(args.output, "w") as log:
        for line in sys.stdin:
            log.write(f"{time.time():.3f} {line}")
            log.flush()
            sys.stdout.write(line)
            sys.stdout.flush()
    return 0


def tail_summary(text: str, busy: int = 4) -> dict:
    """From a stamped `-v` xdist log: the wall seconds (first line to the last test's report), and, from the time
    each worker's last report arrived and from the summed seconds of its tests (`logged_seconds`), each worker's
    finish, the tail (the seconds after fewer than `busy` workers still had tests) and the seconds the last worker
    ran alone; with the sum of all tests' seconds over the workers (the even share)."""
    start, finished, end, ran = None, {}, None, defaultdict(list)
    for line in text.splitlines():
        at, body = unstamped(line)
        if at is None:
            continue
        start = at if start is None else start
        found = RESULT_LINE.match(body)
        if found:
            finished[found.group(1)] = end = at
            ran[found.group(1)].append(found.group(3).rstrip())
    if start is None or not finished:
        raise ValueError("no stamped xdist results")
    timed = logged_seconds(text)
    summed = {worker: sum(timed.get(nodeid, 0.0) for nodeid in ids) for worker, ids in ran.items()}

    def shape(finish: dict[str, float]) -> dict:
        last = sorted(finish.values(), reverse=True)
        return {"worker_finished_seconds": {worker: round(at, 1) for worker, at in sorted(finish.items())},
                "tail_seconds": round(last[0] - last[busy - 1], 1) if len(last) >= busy else None,
                "alone_seconds": round(last[0] - last[1], 1) if len(last) > 1 else None}
    return {"wall_seconds": round(end - start, 1), "workers": len(finished), "busy_below": busy,
            "reported": shape({worker: at - start for worker, at in finished.items()}),
            "summed": {**shape(summed), "even_share_seconds": round(sum(timed.values()) / len(finished), 1),
                       "untimed_tests": sum(nodeid not in timed for ids in ran.values() for nodeid in ids)}}


def tail(args) -> int:
    print(json.dumps(tail_summary(args.log.read_text(), args.busy), indent=1))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    measure = commands.add_parser("run", help="run the suite and measure it")
    measure.add_argument("--label", required=True)
    measure.add_argument("--workers", type=int, default=8)
    measure.add_argument("--output", type=Path, required=True)
    measure.add_argument("--profile", type=Path, required=True, help="a new directory for the raw records")
    measure.add_argument("files", nargs="*", help="test files instead of the whole suite")
    record = commands.add_parser("durations", help="write the durations file from a profiled run")
    record.add_argument("profile", type=Path, nargs="*", help="profile directories")
    record.add_argument("--log", type=Path, action="append", default=[],
                        help="the output of a --durations=0 --durations-min=0 run, as one more run")
    record.add_argument("--output", type=Path, default=test_schedule.DURATIONS)
    record.add_argument("--source", required=True, help="the commit and machine the run measured")
    record.add_argument("--collection", type=Path, help="test IDs to keep (default: collect the current gate suite)")
    record.add_argument("--previous", type=Path,
                        help="an earlier durations file, counted as one more run")
    stamped = commands.add_parser("stamp", help="copy standard input, each line after the time it arrived")
    stamped.add_argument("--output", type=Path, required=True)
    tailed = commands.add_parser("tail", help="the wall and tail of a stamped -v xdist log")
    tailed.add_argument("log", type=Path)
    tailed.add_argument("--busy", type=int, default=4, help="the tail starts when fewer workers than this are busy")
    args = parser.parse_args()
    return {"run": run, "durations": durations, "stamp": stamp, "tail": tail}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
