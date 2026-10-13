"""The order an xdist run starts its tests in: the slowest first, so no long test starts last.

xdist's default `load` scheduler hands each worker a run of consecutive tests in collection order and
the rest in shrinking chunks as workers finish. A test that takes minutes and happens to come late in
the collection then starts when the other workers are nearly done, and they idle until it ends (the
"tail"). `LongestFirst` is `load` with one change: the tests that `tools/test-durations.json` records as
taking at least HEAD_SECONDS go first, one at a time, longest first, each to the next worker that is
free; the rest follow in collection order under `load`'s own chunking, which keeps a module's tests
together on a worker.

It changes only the order in which tests are handed to workers. Every worker still collects the whole
selection in collection order (the gate's `merge_pytest_events` checks this), every collected
test runs once, and a test the durations file does not name is scheduled exactly as `load` would. A
run that names another `--dist` mode keeps that mode.

The durations file is measured data, not a generated file: the `durations` command of the benchmark
script `suite_tail.py` writes it from a profiled run. A stale file only makes the order less good; it
never changes which tests run. (Every test's import closure holds this module, through the suite's
conftest, and the test selector reads each path its strings name as data every test reads: so its
strings name no path but the durations file.)
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DURATIONS = ROOT / "tools/test-durations.json"
FORMAT = "ve-test-durations@1"
# Tests at least this long (setup + call + teardown, seconds) are recorded in the durations file.
RECORDED_SECONDS = 1.0
# Tests at least this long are started first, longest first, one per free worker.
HEAD_SECONDS = 5.0


def durations_text(timed: Mapping[str, float], *, source: str) -> str:
    """The durations file for the measured `timed` seconds per test ID: the tests of at least
    RECORDED_SECONDS, rounded to a tenth of a second, sorted by ID."""
    kept = {nodeid: round(value, 1) for nodeid, value in sorted(timed.items()) if value >= RECORDED_SECONDS}
    return json.dumps({"format": FORMAT, "source": source, "seconds": kept}, indent=1) + "\n"


def read_durations(path: Path = DURATIONS) -> dict[str, float]:
    """The recorded seconds per test ID; empty when the file is missing or not a durations file,
    which leaves the run in `load`'s order."""
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict) or data.get("format") != FORMAT or not isinstance(data.get("seconds"), dict):
        return {}
    return {nodeid: float(value) for nodeid, value in data["seconds"].items()
            if isinstance(nodeid, str) and type(value) in (int, float) and value >= 0}


def unit_seconds(durations: Mapping[str, float] | None = None) -> dict[str, float]:
    """The recorded seconds of each test file (a unit of the test selector's runs): the sum over its
    recorded tests (`durations`, default the durations file)."""
    totals: dict[str, float] = {}
    for nodeid, value in (read_durations() if durations is None else durations).items():
        unit = nodeid.split("::", 1)[0]
        totals[unit] = totals.get(unit, 0.0) + value
    return totals


def head_first(collection: Sequence[str], durations: Mapping[str, float],
               head_seconds: float = HEAD_SECONDS) -> tuple[list[int], int]:
    """The indices of `collection` in the order they are handed out, and how many lead it: the tests
    recorded as taking at least `head_seconds`, longest first (ties in collection order), then every
    other test in collection order. Always a permutation of range(len(collection))."""
    head = sorted((index for index, nodeid in enumerate(collection)
                   if durations.get(nodeid, 0.0) >= head_seconds),
                  key=lambda index: (-durations[collection[index]], index))
    chosen = set(head)
    return head + [index for index in range(len(collection)) if index not in chosen], len(head)


def make_scheduler(config, log, durations: Mapping[str, float] | None = None):
    """A LongestFirst scheduler for a `--dist load` run, else None (xdist picks the scheduler)."""
    if config.getvalue("dist") != "load":
        return None
    from xdist.scheduler import LoadScheduling

    class LongestFirst(LoadScheduling):
        """`load`, with the recorded long tests handed out first, one at a time, longest first."""

        def __init__(self, config, log=None):
            super().__init__(config, log)
            self.durations = read_durations() if durations is None else durations
            self.head = 0  # the long tests not yet handed out: the first `head` entries of `pending`

        def schedule(self):
            if self.collection is not None or not self._check_nodes_have_same_collection():
                return super().schedule()
            collection = next(iter(self.node2collection.values()))
            order, self.head = head_first(collection, self.durations)
            if not self.head:
                return super().schedule()
            self.collection = collection
            self.pending[:] = order
            if self.maxschedchunk is None:
                self.maxschedchunk = len(self.collection)
            # A worker runs a test only once it holds the next one (or is shutting down), so each
            # worker gets two. The second round goes in reverse order, so the worker holding the
            # longest test holds the shortest of the first 2n.
            for node in [*self.nodes, *reversed(self.nodes)]:
                if self.pending:
                    self._send_one(node)
            if not self.pending:
                for node in self.nodes:
                    node.shutdown()

        def _send_one(self, node):
            self.head = max(0, self.head - 1)
            self._send_tests(node, 1)

        def check_schedule(self, node, duration: float = 0) -> None:
            if self.head and not node.shutting_down:
                if len(self.node2pending[node]) < 2:
                    self._send_one(node)
                return
            super().check_schedule(node, duration)

    return LongestFirst(config, log)
