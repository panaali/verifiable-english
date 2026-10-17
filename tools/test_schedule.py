"""The order an xdist run starts its tests in: the slowest first, so no long test starts last.

xdist's default `load` scheduler hands each worker a run of consecutive tests in collection order and
the rest in shrinking chunks as workers finish. A test that takes minutes and happens to come late in
the collection then starts when the other workers are nearly done, and they idle until it ends (the
"tail"). `LongestFirst` is `load` with these changes, driven by the durations the run is given (`source`):

- The modules that hold a test it records as taking at least HEAD_SECONDS go first, longest batch first,
  each batch to the next worker that is free. A batch is a run of one module's tests in collection order,
  together no longer than the longest single test (`head_batches`). A module goes whole because what its
  tests share in one process (a module fixture, a module-level cache: a minute or more for some, ten for
  the p1 experiment's) is paid by whichever of them runs first on a worker: a long test sent alone would
  pay it again, and a cheap test left for later could pay it last, alone. The cap keeps a batch from
  taking longer than the longest test, which bounds the run anyway.
- When the durations name the tests they measured (`measured`), the tests they did not measure (new
  since) follow, in collection order, in runs of at most 1/(BULK_SHARE * workers) of those left: their
  cost is unknown, so they start early and spread, and the measured rest is left to fill in around them.
  Estimated at the mean, a few unmeasured tests of minutes each went out inside one run of hundreds of
  "cheap" tests, which one worker then ran alone for five minutes at the end.
- The rest follow in collection order, as runs of consecutive tests (which keep a module's tests
  together on a worker, as `load`'s do) sized by their estimated seconds (`bulk_count`): `load`'s first
  run after the long tests held some 900 tests and 30 minutes of work, which one worker then ran alone at
  the end. A run is also never longer in tests than `load`'s (1/(BULK_SHARE * workers) of those left), so
  tests estimated too cheaply before tests estimated dearly are still split.

It changes only which worker runs a test and when. Every worker still collects the whole selection in
collection order (the gate's `merge_pytest_events` checks this) and every collected test runs once.
Without durations the run is `load`'s; a run that names another `--dist` mode keeps that mode.

The durations are measured data, not a generated file: the committed durations file, written by the
`durations` command of the benchmark script that measures the suite's tail from profiled runs, or the
scratch file the gate names in SOURCE_VARIABLE: the committed file overlaid with the durations the merge
base's gate recorded (`record_field`, `overlay_text`). A stale, missing or malformed source only makes the
order less good; it never changes which tests run. (Every test's import closure holds this module,
through the suite's conftest, and the test selector takes each path or file name its strings hold as
data that every test reads: so its strings name no file but the durations file.)
"""
from __future__ import annotations

import base64
from collections.abc import Iterable, Mapping, Sequence
import json
import os
from pathlib import Path
from typing import NamedTuple
import zlib

ROOT = Path(__file__).resolve().parents[1]
DURATIONS = ROOT / "tools/test-durations.json"
FORMAT = "ve-test-durations@1"
# The environment variable naming the durations file of a run, when it is not the committed one.
SOURCE_VARIABLE = "VE_TEST_DURATIONS"
# The most bytes a record's compressed durations may expand to.
MAX_RECORD_BYTES = 4 * 1024 * 1024
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


class Estimates(NamedTuple):
    """A durations source read: the recorded seconds per test ID, the estimate of a test it does not record,
    and the IDs it measured (recorded or not), or None when it does not say."""
    durations: dict[str, float]
    unrecorded: float
    measured: frozenset[str] | None = None


def source() -> Path:
    """The durations file of this run: the one SOURCE_VARIABLE names, else the committed one."""
    named = os.environ.get(SOURCE_VARIABLE)
    return Path(named) if named else DURATIONS


def read_source(path: Path) -> Estimates:
    """The durations file at `path`; Estimates({}, UNRECORDED_SECONDS) when it is missing or not a durations
    file, which leaves the run to `load`. Entries that are not seconds are dropped, never coerced; a
    `measured` that is not a list of IDs is ignored."""
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return Estimates({}, UNRECORDED_SECONDS)
    if not isinstance(data, dict) or data.get("format") != FORMAT or not isinstance(data.get("seconds"), dict):
        return Estimates({}, UNRECORDED_SECONDS)
    unrecorded = data.get("unrecorded_seconds", UNRECORDED_SECONDS)
    measured = data.get("measured")
    return Estimates({nodeid: float(value) for nodeid, value in data["seconds"].items()
                      if isinstance(nodeid, str) and seconds_value(value)},
                     float(unrecorded) if seconds_value(unrecorded) else UNRECORDED_SECONDS,
                     frozenset(measured) if isinstance(measured, list)
                     and all(isinstance(nodeid, str) for nodeid in measured) else None)


def read_estimates(path: Path = DURATIONS) -> tuple[dict[str, float], float]:
    """The recorded seconds per test ID, and the estimate of an unrecorded test (`read_source`)."""
    return read_source(path)[:2]


def read_durations(path: Path = DURATIONS) -> dict[str, float]:
    """The recorded seconds per test ID (`read_estimates`)."""
    return read_estimates(path)[0]


# --- the gate record's durations --------------------------------------------------------------------------

def record_field(timed: Mapping[str, float]) -> dict:
    """The durations of one gate's suite (`timed`: setup + call + teardown seconds per test ID) as its record
    keeps them, small enough for its git note: the tests of at least RECORDED_SECONDS, rounded to a tenth
    of a second and compressed, the mean of the others, and how many tests were timed."""
    data = json.loads(durations_text(timed, source="gate"))
    raw = json.dumps(data["seconds"], ensure_ascii=True, separators=(",", ":")).encode()
    return {"format": FORMAT, "recorded_seconds": RECORDED_SECONDS, "tests": len(timed),
            "unrecorded_seconds": data["unrecorded_seconds"],
            "seconds_zlib": base64.b64encode(zlib.compress(raw, 9)).decode("ascii")}


def read_record_field(field) -> Estimates | None:
    """The durations of a gate record's `record_field`, or None when it is absent or malformed."""
    if not isinstance(field, dict) or field.get("format") != FORMAT or type(field.get("seconds_zlib")) is not str \
            or not seconds_value(field.get("unrecorded_seconds")):
        return None
    try:
        decoder = zlib.decompressobj()
        raw = decoder.decompress(base64.b64decode(field["seconds_zlib"], validate=True), MAX_RECORD_BYTES + 1)
        if len(raw) > MAX_RECORD_BYTES or not decoder.eof or decoder.unused_data:
            return None
        seconds = json.loads(raw)
    except (ValueError, zlib.error, UnicodeDecodeError):
        return None
    if not isinstance(seconds, dict) or not all(isinstance(nodeid, str) and seconds_value(value)
                                                for nodeid, value in seconds.items()):
        return None
    return Estimates({nodeid: float(value) for nodeid, value in seconds.items()},
                     float(field["unrecorded_seconds"]))


def overlay_text(committed: Estimates, base: Estimates | None, *, source: str) -> str:
    """The durations file a gate gives its suite: `committed` (the committed file's), overlaid with `base`
    (the merge base's gate record's, `read_record_field`, with the IDs that gate measured): each test that
    gate measured takes its time there (recorded, or the mean of its short tests), every other test keeps
    the committed file's. The result names what it measured only when `base` does."""
    if base is None:
        seconds, unrecorded, measured = committed.durations, committed.unrecorded, None
    else:
        known = base.measured or frozenset()
        seconds = {**{nodeid: value for nodeid, value in committed.durations.items() if nodeid not in known},
                   **base.durations}
        unrecorded = base.unrecorded
        measured = None if base.measured is None else sorted(known | set(seconds))
    data = {"format": FORMAT, "source": source, "unrecorded_seconds": unrecorded,
            "seconds": dict(sorted(seconds.items()))}
    if measured is not None:
        data["measured"] = measured
    return json.dumps(data, indent=1) + "\n"


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


def unmeasured_first(collection: Sequence[str], order: Sequence[int], heads: int,
                     measured: frozenset[str] | None) -> tuple[list[int], int]:
    """`order` (`head_first`'s, led by `heads` head-batch tests) with the tests `measured` does not hold moved
    from the rest to just after the head batches, in collection order; and how many they are. Unchanged
    when the source does not say what it measured. Always a permutation of `order`."""
    if measured is None:
        return list(order), 0
    rest = order[heads:]
    unknown = [index for index in rest if collection[index] not in measured]
    chosen = set(unknown)
    return [*order[:heads], *unknown, *(index for index in rest if index not in chosen)], len(unknown)


def bulk_count(estimates: Iterable[float], target: float, least: int, most: int | None = None) -> int:
    """How many of the next tests (their `estimates`, in order) to send together: at least `least` (when
    there are that many), then more while their sum stays within `target` and their number within `most`."""
    count, total = 0, 0.0
    for estimate in estimates:
        if count >= least and (total + estimate > target or most is not None and count >= most):
            break
        count, total = count + 1, total + estimate
    return count


def make_scheduler(config, log, durations: Mapping[str, float] | None = None,
                   unrecorded: float = UNRECORDED_SECONDS, measured: frozenset[str] | None = None):
    """A LongestFirst scheduler for a `--dist load` run, else None (xdist picks the scheduler). `durations`,
    `unrecorded` and `measured` default to the run's durations file's (`source`)."""
    if config.getvalue("dist") != "load":
        return None
    from xdist.scheduler import LoadScheduling

    class LongestFirst(LoadScheduling):
        """`load`, with the recorded long tests handed out first, a batch at a time, longest first, then the
        unmeasured tests by count, and the rest in runs of consecutive tests sized by their estimated
        seconds and at most `load`'s count."""

        def __init__(self, config, log=None):
            super().__init__(config, log)
            if durations is None:
                self.durations, self.unrecorded, self.measured = read_source(source())
            else:
                self.durations, self.unrecorded, self.measured = durations, unrecorded, measured
            self.batches: list[int] = []  # the sizes of the head batches not yet handed out, which lead `pending`
            self.unmeasured = 0  # the unmeasured tests not yet handed out, which follow them
            self.estimate: list[float] = []  # the estimated seconds of each test of the collection
            self.remaining, self.counted = 0.0, 0  # the estimated seconds of `pending`, summed at this length

        def schedule(self):
            if self.collection is not None or not self.durations or not self._check_nodes_have_same_collection():
                return super().schedule()
            collection = next(iter(self.node2collection.values()))
            order, self.batches = head_first(collection, self.durations, unrecorded=self.unrecorded)
            order, self.unmeasured = unmeasured_first(collection, order, sum(self.batches), self.measured)
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
            """The next head batch; else the next unmeasured tests, a share of those left by count; else the
            next tests in collection order up to a share of the estimated seconds left and of the tests left,
            less what the worker holds (`bulk_count`), and at least enough for it to hold two."""
            share = BULK_SHARE * len(self.nodes)
            if self.batches:
                count = self.batches.pop(0)
            elif self.unmeasured:
                # A crashed worker's tests come back at the end of `pending`, after these.
                count = min(self.unmeasured, max(1, self.unmeasured // share))
                self.unmeasured -= count
            else:
                if len(self.pending) != self.counted:  # a crashed worker's tests came back
                    self.remaining = sum(self.estimate[index] for index in self.pending)
                # What the worker holds counts against its share: one still running a long test gets
                # only the test it needs to go on to.
                held = self.node2pending[node]
                least = max(1, 2 - len(held))
                count = bulk_count((self.estimate[index] for index in self.pending),
                                   self.remaining / share - sum(self.estimate[index] for index in held),
                                   least, max(least, len(self.pending) // share - len(held)))
            self.remaining -= sum(self.estimate[index] for index in self.pending[:count])
            self._send_tests(node, count)
            self.counted = len(self.pending)

    return LongestFirst(config, log)
