"""Simulate xdist's `load` scheduler and tools/test_schedule.py's LongestFirst on a measured run's tests.

    uv run python docs/test-tail/simulate.py PROFILE_DIR [--workers 8 16] [--output evidence/simulation.json]

PROFILE_DIR is a run of `tools/bench/suite_tail.py run` (its per-worker records and gate-events.json, not
committed: some 15,000 rows). Each test takes the time it took in that run; LongestFirst gets the durations
file that run would write (`test_schedule.durations_text`), so its estimates are exact. The simulation
leaves out what workers share (module fixtures, process caches) and the controller's own delay, so it
measures the order alone; tests/test_test_schedule.py's `simulate` is the worker model.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from xdist.scheduler import LoadScheduling  # noqa: E402

from tests.test_test_schedule import Config, simulate  # noqa: E402
from tools import test_schedule  # noqa: E402
from tools.bench import suite_tail  # noqa: E402

QUIET = SimpleNamespace(loadsched=lambda *args: None)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("profile", type=Path)
    parser.add_argument("--workers", type=int, nargs="+", default=[8, 16])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    events = json.loads((args.profile / "gate-events.json").read_text())
    collection = next(iter(events["workers"].values()))
    measured = {row["nodeid"]: max(0.0, suite_tail.seconds(row)) for row in suite_tail.records(args.profile)}
    seconds = {nodeid: measured.get(nodeid, 0.0) for nodeid in collection}
    recorded = {nodeid: round(value, 1) for nodeid, value in seconds.items() if value >= test_schedule.RECORDED_SECONDS}
    short = [value for value in seconds.values() if value < test_schedule.RECORDED_SECONDS]
    unrecorded = sum(short) / len(short)
    result = {"profile": str(args.profile), "tests": len(collection), "test_seconds": round(sum(seconds.values()), 1),
              "runs": []}
    for workers in args.workers:
        _, load_end = simulate(LoadScheduling(Config(workers), QUIET), collection, seconds, workers)
        _, longest_end = simulate(test_schedule.make_scheduler(Config(workers), QUIET, recorded, unrecorded),
                                  collection, seconds, workers)
        result["runs"].append({"workers": workers, "ideal_seconds": round(sum(seconds.values()) / workers, 1),
                               "load_seconds": round(load_end, 1), "longest_first_seconds": round(longest_end, 1)})
    text = json.dumps(result, indent=1) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
