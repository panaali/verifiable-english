"""The order an xdist run starts its tests in: the slowest first, so no long test starts last.

xdist's default `load` scheduler hands each worker a run of consecutive tests in collection order and
the rest in shrinking chunks as workers finish. A test that takes minutes and happens to come late in
the collection then starts when the other workers are nearly done, and they idle until it ends (the
"tail"). `LongestFirst` is `load` with two changes, both driven by `tools/test-durations.json`:

- The modules that hold a test it records as taking at least HEAD_SECONDS go first, longest batch first,
  each batch to the next worker that is free. A batch is a run of one module's tests in collection order,
  together no longer than the longest single test (`head_batches`). A module goes whole because what its
  tests share in one process (a module fixture, a module-level cache: a minute or more for some, ten for
  the p1 experiment's) is paid by whichever of them runs first on a worker: a long test sent alone would
  pay it again, and a cheap test left for later could pay it last, alone. The cap keeps a batch from
  taking longer than the longest test, which bounds the run anyway.
- The rest follow in collection order, as runs of consecutive tests (which keep a module's tests
  together on a worker, as `load`'s do) sized by their estimated seconds rather than their number
  (`bulk_count`): `load`'s first run after the long tests held some 900 tests and 30 minutes of work,
  which one worker then ran alone at the end.

It changes only which worker runs a test and when. Every worker still collects the whole selection in
collection order (the gate's `merge_pytest_events` checks this) and every collected test runs once.
Without a durations file the run is `load`'s; a run that names another `--dist` mode keeps that mode.

The durations file is measured data, not a generated file: the `durations` command of the benchmark
script that measures the suite's tail writes it from profiled runs. A stale file only makes the order
less good; it never changes which tests run. (Every test's import closure holds this module, through the
suite's conftest, and the test selector takes each path or file name its strings hold as data that every
test reads: so its strings name no file but the durations file.)
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DURATIONS = ROOT / "tools/test-durations.json"
FORMAT = "ve-test-durations@1"
# Tests at least this long (setup + call + teardown, seconds) are recorded in the durations file.
RECORDED_SECONDS = 1.0
# Tests at least this long are started first, longest batch first.
HEAD_SECONDS = 5.0
# The estimate of a test the file does not record, when the file does not say (its `unrecorded_seconds`:
# the mean of the measured tests shorter than RECORDED_SECONDS).
UNRECORDED_SECONDS = 0.1
# After the long tests, a free worker gets consecutive tests worth 1/(BULK_SHARE * workers) of the estimated
# seconds left: large runs while much is left, single tests at the end, as `load` does by count.
BULK_SHARE = 2


def durations_text(timed: Mapping[str, float], *, source: str, unrecorded: float | None = None) -> str:
    """The durations file for the measured `timed` seconds per test ID: the tests of at least
    RECORDED_SECONDS, rounded to a tenth of a second, sorted by ID, and the mean of the others (or
    `unrecorded`, an earlier file's, when `timed` holds only some files' short tests)."""
    kept = {nodeid: round(value, 1) for nodeid, value in sorted(timed.items()) if value >= RECORDED_SECONDS}
    short = [value for value in timed.values() if value < RECORDED_SECONDS]
    if unrecorded is None:
        unrecorded = round(sum(short) / len(short), 3) if short else UNRECORDED_SECONDS
    return json.dumps({"format": FORMAT, "source": source, "unrecorded_seconds": unrecorded, "seconds": kept},
                      indent=1) + "\n"


def seconds_value(value) -> bool:
    return type(value) in (int, float) and 0 <= value < float("inf")


def read_estimates(path: Path = DURATIONS) -> tuple[dict[str, float], float]:
    """The recorded seconds per test ID, and the estimate of an unrecorded test; ({}, UNRECORDED_SECONDS)
    when the file is missing or not a durations file, which leaves the run to `load`."""
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return {}, UNRECORDED_SECONDS
    if not isinstance(data, dict) or data.get("format") != FORMAT or not isinstance(data.get("seconds"), dict):
        return {}, UNRECORDED_SECONDS
    unrecorded = data.get("unrecorded_seconds", UNRECORDED_SECONDS)
    return ({nodeid: float(value) for nodeid, value in data["seconds"].items()
             if isinstance(nodeid, str) and seconds_value(value)},
            float(unrecorded) if seconds_value(unrecorded) else UNRECORDED_SECONDS)


def read_durations(path: Path = DURATIONS) -> dict[str, float]:
    """The recorded seconds per test ID (`read_estimates`)."""
    return read_estimates(path)[0]


def unit_of(nodeid: str) -> str:
    """The test file of a test ID: a module, and a unit of the test selector's runs."""
    return nodeid.split("::", 1)[0]


def unit_seconds(durations: Mapping[str, float] | None = None) -> dict[str, float]:
    """The recorded seconds of each test file: the sum over its recorded tests (`durations`, default the
    durations file)."""
    totals: dict[str, float] = {}
    for nodeid, value in (read_durations() if durations is None else durations).items():
        totals[unit_of(nodeid)] = totals.get(unit_of(nodeid), 0.0) + value
    return totals


def head_batches(collection: Sequence[str], durations: Mapping[str, float],
                 head_seconds: float = HEAD_SECONDS, unrecorded: float = UNRECORDED_SECONDS) -> list[list[int]]:
    """The modules of `collection` that hold a test recorded as taking at least `head_seconds`, whole, as
    batches of indices: each batch is a run of one module's tests in collection order, together estimated
    (`durations`, else `unrecorded`) no longer than the longest test (a test alone may reach it); the
    batches longest first, ties in collection order. A module goes whole because what its tests share in
    one process (a module fixture, a module-level cache) is paid by whichever of them runs first there:
    a quick test sent on its own to another worker would pay it again, at the end."""
    estimate = [durations.get(nodeid, unrecorded) for nodeid in collection]
    long = {unit_of(nodeid) for nodeid in collection if durations.get(nodeid, 0.0) >= head_seconds}
    if not long:
        return []
    cap = max(value for nodeid, value in zip(collection, estimate) if unit_of(nodeid) in long)
    batches: list[list[int]] = []
    open_batch: dict[str, tuple[list[int], float]] = {}
    for index, nodeid in enumerate(collection):
        unit = unit_of(nodeid)
        if unit not in long:
            continue
        batch, total = open_batch.get(unit, (None, 0.0))
        if batch is None or total + estimate[index] > cap:
            batch, total = [], 0.0
            batches.append(batch)
        batch.append(index)
        open_batch[unit] = (batch, total + estimate[index])
    return sorted(batches, key=lambda batch: (-sum(estimate[i] for i in batch), batch[0]))


def head_first(collection: Sequence[str], durations: Mapping[str, float],
               head_seconds: float = HEAD_SECONDS, unrecorded: float = UNRECORDED_SECONDS) -> tuple[list[int], list[int]]:
    """The indices of `collection` in the order they are handed out, and the sizes of the batches that
    lead it (`head_batches`); then every other test in collection order. Always a permutation of
    range(len(collection))."""
    batches = head_batches(collection, durations, head_seconds, unrecorded)
    head = [index for batch in batches for index in batch]
    chosen = set(head)
    return head + [index for index in range(len(collection)) if index not in chosen], [len(b) for b in batches]


def bulk_count(estimates: Iterable[float], target: float, least: int) -> int:
    """How many of the next tests (their `estimates`, in order) to send together: at least `least` (when
    there are that many), then more while their sum stays within `target`."""
    count, total = 0, 0.0
    for estimate in estimates:
        if count >= least and total + estimate > target:
            break
        count, total = count + 1, total + estimate
    return count


def make_scheduler(config, log, durations: Mapping[str, float] | None = None,
                   unrecorded: float = UNRECORDED_SECONDS):
    """A LongestFirst scheduler for a `--dist load` run, else None (xdist picks the scheduler). `durations`
    and `unrecorded` default to the durations file's."""
    if config.getvalue("dist") != "load":
        return None
    from xdist.scheduler import LoadScheduling

    class LongestFirst(LoadScheduling):
        """`load`, with the recorded long tests handed out first, a batch at a time, longest first, and the
        rest in runs of consecutive tests sized by their estimated seconds."""

        def __init__(self, config, log=None):
            super().__init__(config, log)
            if durations is None:
                self.durations, self.unrecorded = read_estimates()
            else:
                self.durations, self.unrecorded = durations, unrecorded
            self.batches: list[int] = []  # the sizes of the head batches not yet handed out, which lead `pending`
            self.estimate: list[float] = []  # the estimated seconds of each test of the collection
            self.remaining, self.counted = 0.0, 0  # the estimated seconds of `pending`, summed at this length

        def schedule(self):
            if self.collection is not None or not self.durations or not self._check_nodes_have_same_collection():
                return super().schedule()
            collection = next(iter(self.node2collection.values()))
            order, self.batches = head_first(collection, self.durations, unrecorded=self.unrecorded)
            self.estimate = [self.durations.get(nodeid, self.unrecorded) for nodeid in collection]
            self.collection = collection
            self.pending[:] = order
            self.remaining, self.counted = sum(self.estimate), len(self.pending)
            # A worker runs a test only once it holds the next one (or is shutting down), so each worker
            # gets two batches. The second round goes in reverse order, so the worker holding the longest
            # batch holds the shortest of the first 2n.
            for node in [*self.nodes, *reversed(self.nodes)]:
                if self.pending:
                    self._send_next(node)
            if not self.pending:
                for node in self.nodes:
                    node.shutdown()

        def check_schedule(self, node, duration: float = 0) -> None:
            if not self.estimate:  # no durations: `load` itself
                return super().check_schedule(node, duration)
            if node.shutting_down:
                return
            if not self.pending:
                node.shutdown()
            # A worker holding fewer than two tests idles (a worker added mid-run holds none).
            while self.pending and len(self.node2pending[node]) < 2:
                self._send_next(node)

        def _send_next(self, node):
            """The next head batch, else the next tests in collection order up to a share of the estimated
            seconds left, less what the worker holds (`bulk_count`), and at least enough for it to hold two."""
            if self.batches:
                count = self.batches.pop(0)
            else:
                if len(self.pending) != self.counted:  # a crashed worker's tests came back
                    self.remaining = sum(self.estimate[index] for index in self.pending)
                # What the worker holds counts against its share: one still running a long test gets
                # only the test it needs to go on to.
                held = sum(self.estimate[index] for index in self.node2pending[node])
                count = bulk_count((self.estimate[index] for index in self.pending),
                                   self.remaining / (BULK_SHARE * len(self.nodes)) - held,
                                   max(1, 2 - len(self.node2pending[node])))
            self.remaining -= sum(self.estimate[index] for index in self.pending[:count])
            self._send_tests(node, count)
            self.counted = len(self.pending)

    return LongestFirst(config, log)
