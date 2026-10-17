"""Replay a measured whole-suite run through the scheduler, to separate what each rule and the fresh durations do.

    uv run --frozen python docs/test-architecture/slowtail/replay.py \
        docs/test-architecture/slowtail/evidence/before-main-85b20fcb.log.gz > docs/test-architecture/slowtail/evidence/replay.txt

The log is a stamped `-v -n 9 --durations=0 --durations-min=0` run (tools/bench/suite_tail.py stamp): its
`--durations` table gives each test's real seconds, and the order its tests were first reported in each file stands
in for the collection order (files in name order, as pytest collects them; within a file, an approximation). Each
scheduler then runs that collection with those real seconds on simulated workers that run what they are sent, as
xdist's worker loop does (tests/test_test_schedule.py `simulate`). A simulation, not a measurement: it shows the
order's effect with the machine's load held fixed.
"""
from __future__ import annotations

import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
from tools import test_schedule  # noqa: E402
from tools.bench import suite_tail  # noqa: E402
import test_test_schedule as harness  # noqa: E402
from xdist.scheduler import LoadScheduling  # noqa: E402

MAIN = "85b20fcba"  # the merge base the batch measured against
WORKERS = 9
# The test files that landed after the stale durations file was measured (2026-10-13/16).
LATE = ("tests/test_b16e", "tests/test_b16f")


def at_main(path: str) -> str:
    return subprocess.run(["git", "show", f"{MAIN}:{path}"], cwd=ROOT, capture_output=True, text=True,
                          check=True).stdout


def main() -> int:
    log = Path(sys.argv[1])
    text = (gzip.open(log, "rt") if log.suffix == ".gz" else log.open()).read()
    truth = suite_tail.logged_seconds(text)
    reported = []
    for line in text.splitlines():
        found = suite_tail.RESULT_LINE.match(suite_tail.unstamped(line)[1])
        if found:
            reported.append(found.group(3).rstrip())
    first = {nodeid: index for index, nodeid in reversed(list(enumerate(reported)))}
    collection = sorted(set(reported), key=lambda nodeid: (test_schedule.unit_of(nodeid), first[nodeid]))
    stale = json.loads(at_main("tools/test-durations.json"))
    stale_seconds = {nodeid: float(value) for nodeid, value in stale["seconds"].items()}
    fresh_seconds, fresh_unrecorded = test_schedule.read_estimates()
    measured = frozenset(nodeid for nodeid in collection if not nodeid.startswith(LATE))
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as copy:
        copy.write(at_main("tools/test_schedule.py"))
    spec = importlib.util.spec_from_file_location("main_test_schedule", copy.name)
    main_schedule = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_schedule)
    Path(copy.name).unlink()
    config = harness.Config(WORKERS)
    rows = {
        "xdist's load": LoadScheduling(config),
        "main's LongestFirst, main's (stale) durations": main_schedule.make_scheduler(
            config, None, stale_seconds, stale["unrecorded_seconds"]),
        "this branch, stale durations": test_schedule.make_scheduler(
            config, None, stale_seconds, stale["unrecorded_seconds"]),
        "this branch, stale durations, b16e/b16f unmeasured": test_schedule.make_scheduler(
            config, None, stale_seconds, stale["unrecorded_seconds"], measured),
        "this branch, refreshed durations": test_schedule.make_scheduler(config, None, fresh_seconds, fresh_unrecorded),
    }
    total = sum(truth.values())
    print(f"{len(collection)} tests, {total:.0f} test-seconds; even share on {WORKERS} workers {total / WORKERS:.0f} s")
    for name, scheduler in rows.items():
        started, end = harness.simulate(scheduler, collection, truth, WORKERS)
        finish: dict[str, float] = {}
        for index, (at, worker) in started.items():
            finish[worker] = max(finish.get(worker, 0.0), at + truth[collection[index]])
        last = sorted(finish.values(), reverse=True)
        print(f"{name:55} end {end:6.0f} s   tail (fewer than 4 busy) {last[0] - last[3]:5.0f} s   "
              f"one worker alone {last[0] - last[1]:5.0f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
