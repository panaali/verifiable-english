"""The suite starts its slowest tests first (tools/test_schedule.py), and that changes nothing but the order.

The scheduler is checked three ways: `head_first` on its own (a permutation; the recorded long tests lead,
longest first, a module's together; the rest keep collection order); the scheduler against xdist's `load` in a simulation of
workers that run what they are sent (a long test placed last in the collection starts first, and the run
ends sooner); and a real xdist run of a small project under the gate's event plugin, whose workers collect
exactly the collection run's selection (`tools.gate.merge_pytest_events`) and run every test once.
"""
from __future__ import annotations

import heapq
import json
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest
from xdist.scheduler import LoadScheduling

from tests.subprocesses import HANG_TIMEOUT
from tools import gate, nested_pytest, test_schedule

ROOT = Path(__file__).resolve().parents[1]


def test_head_first_is_a_permutation_led_by_the_recorded_long_tests_longest_first():
    collection = [f"tests/test_{i}.py::t" for i in range(10)]
    durations = {collection[2]: 7.0, collection[5]: 30.0, collection[7]: 7.0, collection[8]: test_schedule.HEAD_SECONDS,
                 collection[9]: 4.9, collection[1]: 0.5}
    order, sizes = test_schedule.head_first(collection, durations)
    assert sorted(order) == list(range(10))
    # 5 longest; 2 and 7 tie and keep collection order; 8 is at the threshold; 9 and 1 are not.
    assert order[:sum(sizes)] == [5, 2, 7, 8] and sizes == [1, 1, 1, 1]
    assert order[sum(sizes):] == [0, 1, 3, 4, 6, 9]
    assert test_schedule.head_first(collection, {}) == (list(range(10)), [])
    assert test_schedule.head_first([], durations) == ([], [])


def test_a_module_with_a_long_test_goes_out_whole_in_runs_up_to_the_longest_test():
    """What a module's tests share in one process (a module fixture, a module-level cache) is paid by the first
    of them a worker runs: a module with a long test goes to workers whole, in runs of consecutive tests no
    longer than the longest test, so neither its long tests nor its quick ones pay it again alone."""
    collection = ["tests/test_m.py::a", "tests/test_m.py::quick", "tests/test_m.py::b", "tests/test_other.py::long",
                  "tests/test_m.py::c", "tests/test_m.py::d", "tests/test_m.py::e", "tests/test_n.py::f",
                  "tests/test_q.py::quick", "tests/test_n.py::unrecorded"]
    durations = {"tests/test_m.py::a": 10.0, "tests/test_m.py::b": 10.0, "tests/test_m.py::c": 10.0,
                 "tests/test_m.py::d": 10.0, "tests/test_m.py::e": 10.0, "tests/test_other.py::long": 40.0,
                 "tests/test_n.py::f": 6.0, "tests/test_m.py::quick": 0.1, "tests/test_q.py::quick": 3.0}
    # m: a + quick + b + c = 30.1, then d + e (adding d would pass the 40 s of the longest test); test_q.py
    # holds no long test and stays with the rest; test_n.py's unrecorded test goes with f.
    assert test_schedule.head_batches(collection, durations) == [[3], [0, 1, 2, 4], [5, 6], [7, 9]]
    order, sizes = test_schedule.head_first(collection, durations)
    assert order == [3, 0, 1, 2, 4, 5, 6, 7, 9, 8] and sizes == [1, 4, 2, 2]
    # In a run, each batch's tests run back to back on one worker.
    started, _ = simulate(test_schedule.make_scheduler(Config(2), None, durations), collection,
                          {**durations, "tests/test_n.py::unrecorded": 0.1}, 2)
    by_worker = {}
    for index, (at, worker) in sorted(started.items(), key=lambda row: row[1][0]):
        by_worker.setdefault(worker, []).append(index)
    runs = [run[i:i + 4] for run in by_worker.values() for i in range(len(run))]
    assert [0, 1, 2, 4] in runs, by_worker


def test_durations_file_round_trips_and_a_bad_file_leaves_the_load_order(tmp_path):
    path = tmp_path / "durations.json"
    path.write_text(test_schedule.durations_text({"b": 12.34, "a": 1.0, "c": 0.99, "d": 0.01}, source="here"))
    assert test_schedule.read_estimates(path) == ({"a": 1.0, "b": 12.3}, 0.5)  # the mean of c and d
    assert list(json.loads(path.read_text())["seconds"]) == ["a", "b"]
    for text in ("", "[]", "{}", json.dumps({"format": "other@1", "seconds": {"a": 9}}),
                 json.dumps({"format": test_schedule.FORMAT, "seconds": []})):
        path.write_text(text)
        assert test_schedule.read_estimates(path) == ({}, test_schedule.UNRECORDED_SECONDS)
    for unrecorded in (True, -1, "0.2", None, 1e999):
        path.write_text(json.dumps({"format": test_schedule.FORMAT, "unrecorded_seconds": unrecorded, "seconds": {}}))
        assert test_schedule.read_estimates(path)[1] == test_schedule.UNRECORDED_SECONDS
    # Entries that are not seconds are dropped, never coerced.
    path.write_text(json.dumps({"format": test_schedule.FORMAT,
                                "seconds": {"a": True, "b": -1, "c": "9", "d": None, "e": 6}}))
    assert test_schedule.read_durations(path) == {"e": 6.0}
    assert test_schedule.read_durations(tmp_path / "absent.json") == {}


def test_committed_durations_file_is_read_whole():
    data = json.loads(test_schedule.DURATIONS.read_text())
    assert data["format"] == test_schedule.FORMAT and data["source"]
    assert list(data["seconds"]) == sorted(data["seconds"])
    assert test_schedule.read_estimates() == ({nodeid: float(value) for nodeid, value in data["seconds"].items()},
                                              data["unrecorded_seconds"])
    assert 0 < data["unrecorded_seconds"] < test_schedule.RECORDED_SECONDS
    assert min(data["seconds"].values()) >= test_schedule.RECORDED_SECONDS
    assert max(data["seconds"].values()) >= test_schedule.HEAD_SECONDS


class Config:
    """What xdist's schedulers read from the configuration."""

    def __init__(self, workers, dist="load"):
        self.values = {"tx": [f"{workers}*popen"], "dist": dist, "maxschedchunk": None}

    def getvalue(self, name):
        return self.values[name]

    getoption = getvalue


class Node:
    def __init__(self, name):
        self.gateway = SimpleNamespace(id=name)
        self.queue, self.shutting_down = [], False

    def send_runtest_some(self, indices):
        assert not self.shutting_down
        self.queue.extend(indices)

    def shutdown(self):
        self.shutting_down = True

    def __repr__(self):
        return self.gateway.id


def simulate(scheduler, collection, seconds, workers):
    """Run the collection on `workers` simulated xdist workers. A worker runs the first test it holds once it
    holds a second one or is shutting down, as xdist's worker loop does. Returns each test's (start, worker)
    and the time the last test ended."""
    nodes = [Node(f"gw{i}") for i in range(workers)]
    for node in nodes:
        scheduler.add_node(node)
        scheduler.add_node_collection(node, collection)
    scheduler.schedule()
    clock, running, started, events = 0.0, {}, {}, []

    def start_ready():
        for node in nodes:
            if node not in running and node.queue and (len(node.queue) >= 2 or node.shutting_down):
                index = node.queue.pop(0)
                assert index not in started, "a test ran twice"
                started[index] = (clock, node.gateway.id)
                running[node] = index
                heapq.heappush(events, (clock + seconds[collection[index]], node.gateway.id, index))

    start_ready()
    while events:
        clock, name, index = heapq.heappop(events)
        node = next(node for node in nodes if node.gateway.id == name)
        del running[node]
        scheduler.mark_test_complete(node, index, seconds[collection[index]])
        start_ready()
    assert sorted(started) == list(range(len(collection))), "every test runs once"
    assert all(not node.queue for node in nodes)
    return started, clock


def workload():
    """200 quick tests in collection order, then four long ones, as in a suite whose slowest tests come late."""
    collection = [f"tests/test_a.py::test_{i}" for i in range(200)] + [f"tests/test_z{i}.py::test_slow" for i in range(4)]
    seconds = {nodeid: 1.0 for nodeid in collection}
    seconds.update({collection[200]: 60.0, collection[201]: 120.0, collection[202]: 30.0, collection[203]: 90.0})
    return collection, seconds


def test_longest_first_starts_the_long_tests_first_and_ends_sooner_than_load():
    collection, seconds = workload()
    recorded = {nodeid: value for nodeid, value in seconds.items() if value >= test_schedule.RECORDED_SECONDS}
    load_started, load_end = simulate(LoadScheduling(Config(4)), collection, seconds, 4)
    started, end = simulate(test_schedule.make_scheduler(Config(4), None, recorded), collection, seconds, 4)
    # Under `load` the long tests, last in the collection, start after most quick tests have run.
    assert min(load_started[i][0] for i in range(200, 204)) > 0
    # Here each worker's first test is one of the four long ones, and all four start at once.
    workers = {worker for _, worker in started.values()}
    firsts = [min((at, index) for index, (at, who) in started.items() if who == worker)[1] for worker in workers]
    assert sorted(firsts) == [200, 201, 202, 203]
    assert [started[i][0] for i in (201, 203, 200, 202)] == [0.0] * 4
    # 500 s of tests on 4 workers: the run ends within a quick test of the even share, well before `load`'s.
    assert end <= 500 / 4 + 1.0 < load_end - 30


def test_quick_tests_keep_loads_chunks_in_collection_order():
    """After the long tests, each worker gets runs of consecutive tests, as under `load`, so a module's tests
    stay together on a worker and its module fixtures are set up once there."""
    collection, seconds = workload()
    recorded = {nodeid: value for nodeid, value in seconds.items() if value >= test_schedule.HEAD_SECONDS}

    def runs(scheduler):
        """Per worker, the runs of consecutive quick tests it ran; each in ascending order."""
        started, _ = simulate(scheduler, collection, seconds, 4)
        by_worker = {}
        for index, (at, worker) in sorted(started.items(), key=lambda row: (row[1][0], row[0])):
            if index < 200:
                by_worker.setdefault(worker, []).append(index)
        assert all(quick == sorted(quick) for quick in by_worker.values())
        return sum(1 + sum(1 for a, b in zip(quick, quick[1:]) if b != a + 1) for quick in by_worker.values())

    # About as few runs as `load` makes of the same tests: never a scattering of single tests.
    assert runs(test_schedule.make_scheduler(Config(4), None, recorded)) <= runs(LoadScheduling(Config(4))) + 8 < 60


def test_without_recorded_long_tests_or_under_another_mode_xdist_decides():
    collection, seconds = workload()
    plain = simulate(LoadScheduling(Config(3)), collection, seconds, 3)
    assert simulate(test_schedule.make_scheduler(Config(3), None, {}), collection, seconds, 3) == plain
    for dist in ("loadfile", "loadscope", "loadgroup", "worksteal", "each", "no"):
        assert test_schedule.make_scheduler(Config(3, dist), None, {collection[0]: 99.0}) is None


def test_the_worker_with_the_longest_test_gets_the_shortest_of_the_first_two_rounds():
    """Each worker holds two batches from the start; pairing the longest with the shortest evens them out."""
    collection = [f"tests/test_{i}.py::t" for i in range(8)]
    seconds = {nodeid: 10.0 * (8 - i) for i, nodeid in enumerate(collection)}  # 80, 70, ..., 10
    _, end = simulate(test_schedule.make_scheduler(Config(4), None, seconds), collection, seconds, 4)
    assert end == 90.0  # 80 + 10, 70 + 20, 60 + 30, 50 + 40


def test_quick_tests_go_out_by_estimated_seconds_not_by_count():
    """After the long tests, `load` sent the next free worker some 900 consecutive tests worth 30 minutes,
    which it then ran alone. Runs sized by estimated seconds end together."""
    collection = ([f"tests/test_long{i}.py::t" for i in range(4)] + [f"tests/test_a.py::t{i}" for i in range(600)]
                  + [f"tests/test_b.py::t{i}" for i in range(200)])
    seconds = dict(zip(collection, [10.0, 200.0, 200.0, 200.0]))  # one worker is free after 10 s
    seconds.update({nodeid: 0.1 for nodeid in collection[4:604]})
    seconds.update({nodeid: 3.0 for nodeid in collection[604:]})
    recorded = {nodeid: value for nodeid, value in seconds.items() if value >= test_schedule.RECORDED_SECONDS}
    _, load_end = simulate(LoadScheduling(Config(4)), collection, seconds, 4)
    _, end = simulate(test_schedule.make_scheduler(Config(4), None, recorded, 0.1), collection, seconds, 4)
    ideal = sum(seconds.values()) / 4  # 317.5 s
    assert end <= ideal + 3.0 < load_end - 30
    # Medium tests first: a run of a fixed share of the tests left (400 / 8 = 50 of them, 100 s) would wait
    # behind a long test; a share of the seconds left, less what the worker holds, does not.
    collection = ([f"tests/test_long{i}.py::t" for i in range(4)] + [f"tests/test_a.py::t{i}" for i in range(200)]
                  + [f"tests/test_b.py::t{i}" for i in range(200)])
    seconds = dict(zip(collection, [5.0, 100.0, 100.0, 100.0]))
    seconds.update({nodeid: 2.0 for nodeid in collection[4:204]})
    seconds.update({nodeid: 0.05 for nodeid in collection[204:]})
    recorded = {nodeid: value for nodeid, value in seconds.items() if value >= test_schedule.RECORDED_SECONDS}
    _, end = simulate(test_schedule.make_scheduler(Config(4), None, recorded, 0.05), collection, seconds, 4)
    assert end <= sum(seconds.values()) / 4 + 2.0  # 178.75 s


def test_bulk_count_takes_at_least_the_least_then_up_to_the_target():
    assert test_schedule.bulk_count([1.0, 1.0, 1.0, 5.0], target=2.5, least=1) == 2
    assert test_schedule.bulk_count([9.0, 1.0], target=2.5, least=1) == 1
    assert test_schedule.bulk_count([9.0, 1.0], target=-4.0, least=2) == 2
    assert test_schedule.bulk_count([1.0], target=10.0, least=2) == 1
    assert test_schedule.bulk_count([], target=10.0, least=2) == 0
    assert test_schedule.bulk_count(iter([0.5] * 100), target=10.0, least=1) == 20
    # At most `most`, never fewer than `least`.
    assert test_schedule.bulk_count([0.1] * 100, target=10.0, least=1, most=7) == 7
    assert test_schedule.bulk_count([0.1] * 100, target=10.0, least=3, most=1) == 3
    assert test_schedule.bulk_count([0.1] * 100, target=0.25, least=1, most=7) == 2


def test_fewer_tests_than_two_per_worker_all_run():
    collection = [f"tests/test_a.py::test_{i}" for i in range(5)]
    seconds = dict.fromkeys(collection, 10.0)
    started, end = simulate(test_schedule.make_scheduler(Config(4), None, seconds), collection, seconds, 4)
    assert len(started) == 5 and end == 20.0


def test_a_crashed_worker_s_tests_run_elsewhere():
    """xdist hands a crashed worker's queued tests (not the one it was running) back to the scheduler."""
    collection, seconds = workload()
    scheduler = test_schedule.make_scheduler(Config(2), None, {k: v for k, v in seconds.items() if v >= 5})
    nodes = [Node("gw0"), Node("gw1")]
    for node in nodes:
        scheduler.add_node(node)
        scheduler.add_node_collection(node, collection)
    scheduler.schedule()
    crashed = scheduler.node2pending[nodes[0]][0]
    held = list(scheduler.node2pending[nodes[0]][1:])
    assert scheduler.remove_node(nodes[0]) == collection[crashed]
    assert set(held) <= set(scheduler.pending) | set(scheduler.node2pending[nodes[1]])


def test_the_suite_conftest_installs_the_scheduler(tmp_path, monkeypatch):
    """tests/conftest.py hands every `load` run of the suite to LongestFirst with the run's durations: the file
    SOURCE_VARIABLE names (the gate's overlay), else the committed one."""
    import conftest
    monkeypatch.delenv(test_schedule.SOURCE_VARIABLE, raising=False)
    scheduler = conftest.pytest_xdist_make_scheduler(Config(2), None)
    assert type(scheduler).__name__ == "LongestFirst"
    assert (scheduler.durations, scheduler.unrecorded, scheduler.measured) == (*test_schedule.read_estimates(), None)
    assert conftest.pytest_xdist_make_scheduler(Config(2, "loadfile"), None) is None
    named = tmp_path / "durations.json"
    named.write_text(json.dumps({"format": test_schedule.FORMAT, "unrecorded_seconds": 0.25,
                                 "seconds": {"tests/test_a.py::t": 9.0}, "measured": ["tests/test_a.py::t"]}))
    monkeypatch.setenv(test_schedule.SOURCE_VARIABLE, str(named))
    assert test_schedule.source() == named
    scheduler = conftest.pytest_xdist_make_scheduler(Config(2), None)
    assert (scheduler.durations, scheduler.unrecorded, scheduler.measured) == (
        {"tests/test_a.py::t": 9.0}, 0.25, frozenset({"tests/test_a.py::t"}))
    # A named file that is missing or malformed leaves `load`, as a bad committed file does.
    for text in (None, "{", json.dumps({"format": "other@1", "seconds": {"tests/test_a.py::t": 9.0}})):
        if text is None:
            named.unlink()
        else:
            named.write_text(text)
        scheduler = conftest.pytest_xdist_make_scheduler(Config(2), None)
        assert (scheduler.durations, scheduler.unrecorded, scheduler.measured) == (
            {}, test_schedule.UNRECORDED_SECONDS, None)


def test_a_nested_run_and_the_run_cache_never_see_the_gates_durations_file():
    """The gate names its scratch durations file to its own suite only: a nested run's environment drops it, as it
    drops the gate's other suite settings, so a nested run orders by the committed file and the run cache's key
    (its `VE_` settings) does not change with each gate's scratch path."""
    from tools import run_cache
    outer = {test_schedule.SOURCE_VARIABLE: "/tmp/ve-gate-x/test-durations.json", "VE_NATIVE_PREBUILT": "1"}
    nested = nested_pytest.environment(outer)
    assert test_schedule.SOURCE_VARIABLE not in nested and nested["VE_NATIVE_PREBUILT"] == "1"
    assert test_schedule.SOURCE_VARIABLE not in run_cache.run_settings(ROOT, nested)
    assert test_schedule.SOURCE_VARIABLE in gate.STAGE_ENVIRONMENT["pytest"]


def test_a_measured_list_that_is_not_a_list_of_ids_is_ignored(tmp_path):
    path = tmp_path / "durations.json"
    for measured in ("tests/test_a.py::t", [7], {"tests/test_a.py::t": 1}, None, [None]):
        path.write_text(json.dumps({"format": test_schedule.FORMAT, "seconds": {"t": 2.0}, "measured": measured}))
        assert test_schedule.read_source(path) == ({"t": 2.0}, test_schedule.UNRECORDED_SECONDS, None)


def sends(scheduler, collection, workers, seconds):
    """Simulate the run (`simulate`), recording every hand-out: (worker, the indices sent together)."""
    sent = []
    original = Node.send_runtest_some

    def record(node, indices):
        sent.append((node.gateway.id, list(indices)))
        original(node, indices)
    Node.send_runtest_some = record
    try:
        simulate(scheduler, collection, seconds, workers)
    finally:
        Node.send_runtest_some = original
    return sent


def expensive_module_at_the_end(dear_after: bool):
    """1,000 quick tests the estimates know (as the mean), then a module of 64 tests no source measured that
    really take 10 s each (estimated at the mean, 0.1 s); with `dear_after`, a last module of 40 tests
    recorded at 4 s each."""
    collection = ([f"tests/test_a.py::t{i}" for i in range(1000)] + [f"tests/test_new.py::t{i}" for i in range(64)]
                  + ([f"tests/test_z.py::t{i}" for i in range(40)] if dear_after else []))
    recorded = {nodeid: 4.0 for nodeid in collection if nodeid.startswith("tests/test_z.py")}
    seconds = {nodeid: 0.1 for nodeid in collection} | {nodeid: 10.0 for nodeid in collection[1000:1064]} | recorded
    return collection, recorded, seconds


@pytest.mark.parametrize("dear_after", [False, True], ids=["last", "before dear tests"])
def test_an_unrecorded_expensive_module_at_the_end_is_not_one_workers_run(dear_after):
    """A run is never longer in tests than `load`'s share (1/(BULK_SHARE * workers) of those left), so a module
    the estimates take for cheap is split among the workers, even when estimated-dear tests follow it (where
    the seconds left alone would send all of it in one run). The hand-outs are checked, not times."""
    collection, recorded, seconds = expensive_module_at_the_end(dear_after)
    workers = 4
    new = set(range(1000, 1064))
    sent = sends(test_schedule.make_scheduler(Config(workers), None, recorded or {"tests/other.py::t": 9.0}, 0.1),
                 collection, workers, seconds)
    assert sorted(index for _, indices in sent for index in indices) == list(range(len(collection)))
    per_send = [len(new.intersection(indices)) for _, indices in sent]
    assert max(per_send) <= len(collection[1000:]) // (test_schedule.BULK_SHARE * workers), per_send
    assert len({worker for worker, indices in sent if new.intersection(indices)}) == workers


def test_unmeasured_tests_start_right_after_the_long_ones_in_shares_by_count():
    """Tests the durations did not measure (new since) cost what nobody knows: they go out right after the head
    batches, in collection order, a share of those left by count at a time, so a few that take minutes are
    neither sent together nor left among the last. Tests the source measured keep their place."""
    collection = (["tests/test_long.py::t"] + [f"tests/test_a.py::t{i}" for i in range(300)]
                  + [f"tests/test_new.py::t{i}" for i in range(3)] + [f"tests/test_b.py::t{i}" for i in range(600)])
    new = (301, 302, 303)
    recorded = {collection[0]: 60.0}
    measured = frozenset(collection) - {collection[i] for i in new}
    order, sizes = test_schedule.head_first(collection, recorded)
    moved, count = test_schedule.unmeasured_first(collection, order, sum(sizes), measured)
    assert count == 3 and sorted(moved) == list(range(len(collection)))
    assert moved[:4] == [0, *new] and moved[4:] == [i for i in order[1:] if i not in new]
    assert test_schedule.unmeasured_first(collection, order, sum(sizes), None) == (order, 0)
    # The three unmeasured tests take 150 s each: each goes to its own worker, first; without the list of
    # measured tests (the committed file alone) they ride in one run of the estimated-cheap rest.
    seconds = {nodeid: 0.1 for nodeid in collection} | recorded | {collection[i]: 150.0 for i in new}
    workers = 4
    for given, apart in ((measured, True), (None, False)):
        sent = sends(test_schedule.make_scheduler(Config(workers), None, recorded, 0.1, given),
                     collection, workers, seconds)
        assert sorted(index for _, indices in sent for index in indices) == list(range(len(collection)))
        together = max(len(set(new).intersection(indices)) for _, indices in sent)
        assert (together == 1) is apart, sent[:8]
    sent = sends(test_schedule.make_scheduler(Config(workers), None, recorded, 0.1, measured),
                 collection, workers, seconds)
    # The long test, then one unmeasured test to each other worker.
    assert sent[:4] == [("gw0", [0]), ("gw1", [301]), ("gw2", [302]), ("gw3", [303])]


def test_a_worker_added_mid_run_gets_two_tests_to_start():
    """xdist restarts a crashed worker as a new node and schedules again; a worker holding one test idles,
    so a batch of one test is topped up."""
    collection = [f"tests/test_{i}.py::t" for i in range(20)]
    seconds = {nodeid: 100.0 - i for i, nodeid in enumerate(collection)}
    scheduler = test_schedule.make_scheduler(Config(2), None, seconds)
    nodes = [Node("gw0"), Node("gw1")]
    for node in nodes:
        scheduler.add_node(node)
        scheduler.add_node_collection(node, collection)
    scheduler.schedule()
    assert [len(scheduler.node2pending[node]) for node in nodes] == [2, 2]
    late = Node("gw2")
    scheduler.add_node(late)
    scheduler.add_node_collection(late, collection)
    scheduler.schedule()
    assert len(scheduler.node2pending[late]) == 2 and late.queue == scheduler.node2pending[late]


PROJECT_CONFTEST = '''
import pytest

from tools import test_schedule

DURATIONS = {DURATIONS!r}


@pytest.hookimpl(optionalhook=True)
def pytest_xdist_make_scheduler(config, log):
    return test_schedule.make_scheduler(config, log, DURATIONS)
'''

PROJECT_TESTS = '''
import os
from pathlib import Path

import pytest


@pytest.mark.parametrize("case", range({CASES}))
def test_case(case, request):
    with open(Path(__file__).parent / "ran.jsonl", "a") as log:
        log.write('{{"worker": "%s", "nodeid": "%s"}}\\n' % (os.environ["PYTEST_XDIST_WORKER"], request.node.nodeid))
'''


def test_an_xdist_run_keeps_the_gates_collection_accounting(tmp_path):
    """Under the gate's event plugin, each worker collects the collection run's selection, in collection
    order (merge_pytest_events accepts the run), every test has one result, and each worker runs the
    long tests it is sent before any quick one."""
    cases = 40
    long_ids = [f"test_slow.py::test_case[{case}]" for case in (3, 1, 2, 0)]
    durations = {nodeid: 10.0 + rank for rank, nodeid in enumerate(reversed(long_ids))}
    (tmp_path / "conftest.py").write_text(PROJECT_CONFTEST.format(DURATIONS=durations))
    (tmp_path / "test_project.py").write_text(PROJECT_TESTS.format(CASES=cases))
    (tmp_path / "test_slow.py").write_text(PROJECT_TESTS.format(CASES=4))
    env = nested_pytest.environment(os.environ, PYTHONPATH=str(ROOT))
    arguments = ["-q", "-p", "no:cacheprovider", "-p", "tools.gate_pytest", "-o", "addopts=", "test_project.py",
                 "test_slow.py"]

    def run(command, events):
        result = subprocess.run(command, cwd=tmp_path, env={**env, "VE_GATE_PYTEST_RESULT": str(events)},
                                capture_output=True, text=True, timeout=HANG_TIMEOUT)
        assert result.returncode == 0, result.stdout[-4000:] + result.stderr[-4000:]
        return json.loads(events.read_text())

    collection = run(nested_pytest.command(["--collect-only", *arguments]), tmp_path / "collection.json")
    suite = run(nested_pytest.command(arguments, workers=3), tmp_path / "suite.json")
    merged = gate.merge_pytest_events(collection, suite)
    assert merged["selected"] == [*(f"test_project.py::test_case[{case}]" for case in range(cases)),
                                  *(f"test_slow.py::test_case[{case}]" for case in range(4))]
    assert len(merged["workers"]) == 3
    assert sorted(merged["tests"]) == sorted(merged["selected"])
    assert {row["outcome"] for row in merged["tests"].values()} == {"passed"}
    ran = [json.loads(line) for line in (tmp_path / "ran.jsonl").read_text().splitlines()]
    assert sorted(row["nodeid"] for row in ran) == sorted(merged["selected"])
    for worker in {row["worker"] for row in ran}:
        order = [row["nodeid"] in long_ids for row in ran if row["worker"] == worker]
        assert order == sorted(order, reverse=True), (worker, order)
    # The longest test is the first one some worker ran.
    assert long_ids[0] in {next(row["nodeid"] for row in ran if row["worker"] == worker)
                           for worker in {row["worker"] for row in ran}}


SOURCE_CONFTEST = '''
import pytest

from tools import test_schedule


@pytest.hookimpl(optionalhook=True)
def pytest_xdist_make_scheduler(config, log):
    return test_schedule.make_scheduler(config, log)
'''


def test_the_durations_source_never_changes_which_tests_run(tmp_path):
    """The suite's hook reads the durations SOURCE_VARIABLE names, else the committed file. With the committed
    file, the gate's overlay (long tests recorded, some tests unmeasured), a missing file and a malformed one, an
    xdist run under the gate's event plugin collects the same selection on every worker (merge_pytest_events),
    runs each selected test exactly once, and times each; only the order may differ."""
    (tmp_path / "conftest.py").write_text(SOURCE_CONFTEST)
    (tmp_path / "test_project.py").write_text(PROJECT_TESTS.format(CASES=30))
    (tmp_path / "test_slow.py").write_text(PROJECT_TESTS.format(CASES=4))
    (tmp_path / "test_new.py").write_text(PROJECT_TESTS.format(CASES=3))
    overlay = tmp_path / "overlay.json"
    measured = frozenset([*(f"test_project.py::test_case[{case}]" for case in range(30)),
                          *(f"test_slow.py::test_case[{case}]" for case in range(4))])
    overlay.write_text(test_schedule.overlay_text(
        test_schedule.read_source(test_schedule.DURATIONS),
        test_schedule.Estimates({f"test_slow.py::test_case[{case}]": 10.0 + case for case in range(4)}, 0.05, measured),
        source="a test"))
    assert test_schedule.read_source(overlay).measured == measured | set(test_schedule.read_durations())
    malformed = tmp_path / "malformed.json"
    malformed.write_text('{"format": "ve-test-durations@1", "seconds": [')
    sources = {"committed": None, "overlay": overlay, "missing": tmp_path / "absent.json", "malformed": malformed}
    arguments = ["-q", "-p", "no:cacheprovider", "-p", "tools.gate_pytest", "-o", "addopts=", "test_project.py",
                 "test_slow.py", "test_new.py"]
    runs = {}
    for name, path in sources.items():
        env = nested_pytest.environment({key: value for key, value in os.environ.items()
                                         if key != test_schedule.SOURCE_VARIABLE}, PYTHONPATH=str(ROOT))
        if path is not None:
            env[test_schedule.SOURCE_VARIABLE] = str(path)
        (tmp_path / "ran.jsonl").unlink(missing_ok=True)

        def run(command, events):
            result = subprocess.run(command, cwd=tmp_path, env={**env, "VE_GATE_PYTEST_RESULT": str(events)},
                                    capture_output=True, text=True, timeout=HANG_TIMEOUT)
            assert result.returncode == 0, (name, result.stdout[-4000:] + result.stderr[-4000:])
            return json.loads(events.read_text())

        collection = run(nested_pytest.command(["--collect-only", *arguments]), tmp_path / "collection.json")
        merged = gate.merge_pytest_events(collection, run(nested_pytest.command(arguments, workers=3),
                                                          tmp_path / "suite.json"))
        ran = [json.loads(line)["nodeid"] for line in (tmp_path / "ran.jsonl").read_text().splitlines()]
        assert sorted(ran) == sorted(set(ran)) == sorted(merged["selected"]), name
        assert sorted(merged["tests"]) == sorted(merged["seconds"]) == sorted(merged["selected"]), name
        assert all(type(value) is float and value >= 0 for value in merged["seconds"].values()), name
        runs[name] = (merged["collected"], merged["selected"], sorted(ran))
    assert len(runs["committed"][1]) == 37
    assert all(run == runs["committed"] for run in runs.values()), runs
