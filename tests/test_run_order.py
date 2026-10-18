"""Test speed B5: an agent's selected run starts the tests that failed last time and the changed ones,
and stops after `--maxfail` failures; the gate never stops early (tests/test_gate_quarantine.py).

The order is a permutation of the selection: B5 never changes which tests run, only when.
"""
from __future__ import annotations

import datetime
import json
import os
from pathlib import Path
import random
import select
import signal
import subprocess
import sys
import textwrap
import threading

import pytest

from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import nested_pytest  # noqa: E402
import quarantine  # noqa: E402
import run_order  # noqa: E402
import select_tests  # noqa: E402
import test_schedule  # noqa: E402
import test_map  # noqa: E402


# --- the order ---

def test_the_tools_modules_are_not_shadowed_by_test_modules():
    """tools/ and tests/ are both on the suite's import path: a tools module named like a test module
    (this one was first `test_order`, which is tests/test_order.py) resolves to the test in the full suite."""
    import test_order  # noqa: F401  (tests/test_order.py, imported first as in the full suite)
    for module in (run_order, quarantine):
        assert Path(module.__file__) == ROOT / "tools" / f"{module.__name__}.py"
        assert getattr(select_tests, module.__name__) is module
        assert not (ROOT / "tests" / f"{module.__name__}.py").exists()



def test_the_last_failed_then_the_changed_then_the_rest():
    units = ["tests/test_d.py", "tests/test_a.py", "tests/test_c.py", "tests/test_b.py", "tools/test_x.py"]
    assert run_order.order(units, changed=["tests/test_c.py", "docs/x.md", "tests/test_b.py"],
                            failed=["tests/test_d.py", "tests/test_b.py", "tests/test_gone.py"]) == [
        "tests/test_b.py", "tests/test_d.py",       # failed last time (one also changed)
        "tests/test_c.py",                          # changed
        "tests/test_a.py", "tools/test_x.py"]       # the rest, in name order


def test_within_each_group_the_slowest_recorded_unit_starts_first():
    """Eight jobs run the units: a long unit that started last would leave seven idle until it ended."""
    units = ["tests/test_a.py", "tests/test_b.py", "tests/test_c.py", "tests/test_d.py", "tests/test_e.py"]
    seconds = {"tests/test_e.py": 300.0, "tests/test_c.py": 20.0, "tests/test_b.py": 20.0, "tests/test_d.py": 90.0}
    assert run_order.order(units, seconds=seconds) == [
        "tests/test_e.py", "tests/test_d.py", "tests/test_b.py", "tests/test_c.py", "tests/test_a.py"]
    assert run_order.order(units, changed=["tests/test_a.py", "tests/test_c.py"], failed=["tests/test_b.py"],
                           seconds=seconds) == [
        "tests/test_b.py",                                    # failed last time
        "tests/test_c.py", "tests/test_a.py",                 # changed, slowest first
        "tests/test_e.py", "tests/test_d.py"]                 # the rest, slowest first
    # By default the seconds are the durations file's, summed per test file.
    recorded = test_schedule.unit_seconds()
    slowest = max(recorded, key=recorded.get)
    assert run_order.order(["tests/test_a_unrecorded.py", slowest])[0] == slowest
    assert test_schedule.unit_seconds({"tests/test_x.py::a": 2.0, "tests/test_x.py::b[1]": 3.5,
                                       "tests/test_y.py::c": 1.0}) == {"tests/test_x.py": 5.5, "tests/test_y.py": 1.0}


def test_the_order_is_a_permutation_of_the_selection():
    """Ordering never adds or drops a test: the selection is today's, only its order changes."""
    generator = random.Random(5)
    names = [f"tests/test_{index}.py" for index in range(30)]
    for _ in range(200):
        units = generator.sample(names, generator.randrange(0, 30))
        changed = generator.sample(names, generator.randrange(0, 10))
        failed = generator.sample(names, generator.randrange(0, 10))
        ordered = run_order.order(units, changed=changed, failed=failed)
        assert sorted(ordered) == sorted(set(units)) and len(ordered) == len(set(units))
        ranks = [0 if unit in failed else 1 if unit in changed else 2 for unit in ordered]
        assert ranks == sorted(ranks)


# --- what the last run left ---

def test_a_unit_leaves_the_last_failures_when_it_runs_to_the_end():
    previous = {"tests/test_a.py": ["tests/test_a.py::t"], "tests/test_b.py": ["tests/test_b.py::t"],
                "tests/test_c.py": ["tests/test_c.py::t"]}
    state = run_order.updated(previous, completed=["tests/test_a.py", "tests/test_b.py"],
                               failed={"tests/test_b.py": ["tests/test_b.py::u"], "tests/test_a.py": []})
    # a passed; b failed again (its new failures replace the old); c did not finish and keeps its own.
    assert state == {"tests/test_b.py": ["tests/test_b.py::u"], "tests/test_c.py": ["tests/test_c.py::t"]}


def test_the_last_failures_are_the_runs_and_a_newer_gates(tmp_path):
    state, record = tmp_path / "state.json", tmp_path / run_order.GATE_RECORD
    run_order.write_state(state, {"tests/test_a.py": ["tests/test_a.py::t"]})
    assert run_order.last_failed(tmp_path, state) == {"tests/test_a.py": ["tests/test_a.py::t"]}
    record.write_text(json.dumps({"failures": [
        {"stage": "pytest", "nodeid": "tests/test_g.py::t[1]", "reason": "x"},
        {"stage": "coverage", "reason": "baseline"}, "not a failure",
        {"stage": "pytest", "nodeid": "../outside.py::t", "reason": "x"}]}))
    os.utime(record, ns=(state.stat().st_mtime_ns + 10**9,) * 2)
    assert run_order.last_failed(tmp_path, state) == {"tests/test_a.py": ["tests/test_a.py::t"],
                                                       "tests/test_g.py": ["tests/test_g.py::t[1]"]}
    # A selected run after the gate has seen which of its failures still fail.
    os.utime(state, ns=(record.stat().st_mtime_ns + 10**9,) * 2)
    assert run_order.last_failed(tmp_path, state) == {"tests/test_a.py": ["tests/test_a.py::t"]}


@pytest.mark.parametrize("text", ["", "{", "[]", '{"format": "other", "failed": {}}',
                                  '{"format": "ve-last-failed@1", "failed": {"tests/test_a.py": [7]}}'])
def test_a_malformed_state_is_no_last_failures(tmp_path, text):
    """The state only orders the run: a bad one orders nothing first and never fails the run."""
    (tmp_path / "state.json").write_text(text)
    assert run_order.last_failed(tmp_path, tmp_path / "state.json") == {}


def test_the_state_is_in_this_worktrees_own_git_directory():
    assert run_order.state_path().parent == Path(subprocess.run(
        ["git", "rev-parse", "--absolute-git-dir"], cwd=ROOT, text=True, capture_output=True,
        check=True).stdout.strip())


# --- JUnit reports name the same tests as pytest ---

PROJECT = {
    "tests/test_mixed.py": """
        import pytest

        def test_passes():
            pass

        def test_fails():
            assert False

        @pytest.mark.parametrize("value", ["a.b", "c::d"])
        def test_param(value):
            assert value == "a.b"

        class TestGroup:
            class TestInner:
                def test_nested(self):
                    assert False

        @pytest.fixture
        def broken():
            raise RuntimeError("setup")

        def test_setup_error(broken):
            pass

        @pytest.mark.xfail(strict=True)
        def test_xfail():
            assert False
    """,
    "tests/test_broken_import.py": "import a_module_that_is_not_there\n",
}


def project(tmp_path, files=PROJECT) -> Path:
    for name, text in files.items():
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text(textwrap.dedent(text))
    return tmp_path


def pytest_run(root: Path, *arguments: str, **settings: str) -> subprocess.CompletedProcess:
    command = nested_pytest.command(["-q", "-p", "no:cacheprovider", *arguments], python=[sys.executable])
    environment = nested_pytest.environment(os.environ, PYTHONPATH=str(ROOT), **settings)
    return subprocess.run(command, cwd=root, env=environment, text=True, capture_output=True,
                          timeout=HANG_TIMEOUT)


def test_junit_failures_are_pytests_own_node_ids(tmp_path):
    """The node IDs read from the JUnit report are those pytest's own reports give (tools/gate_pytest.py)."""
    root = project(tmp_path)
    report, events = tmp_path / "junit.xml", tmp_path / "events.json"
    pytest_run(root, "-p", "tools.gate_pytest", "--continue-on-collection-errors",
               *run_order.junit_options(report), "tests", VE_GATE_PYTEST_RESULT=str(events))
    files, failed = run_order.read_junit(report)
    outcomes = json.loads(events.read_text())["tests"]
    expected = sorted(nodeid for nodeid, row in outcomes.items() if row["outcome"] == "failed")
    assert failed == sorted([*expected, "tests/test_broken_import.py"])
    assert "tests/test_mixed.py::TestGroup::TestInner::test_nested" in failed
    assert "tests/test_mixed.py::test_param[c::d]" in failed and "tests/test_mixed.py::test_setup_error" in failed
    assert files == {"tests/test_mixed.py", "tests/test_broken_import.py"}


def test_a_unit_without_a_junit_report_is_one_failure_named_by_the_unit(tmp_path):
    assert run_order.read_junit(tmp_path / "missing.xml") is None
    (tmp_path / "bad.xml").write_text("<testsuite><testcase")
    assert run_order.read_junit(tmp_path / "bad.xml") is None
    failed = {"exit": 1}
    assert select_tests.unit_failures("tests/test_a.py", failed, tmp_path / "missing.xml") == ["tests/test_a.py"]
    assert select_tests.unit_failures("tools/test_layer_policy.py", failed, tmp_path / "x.xml") == [
        "tools/test_layer_policy.py"]
    assert select_tests.unit_failures("tests/test_a.py", {"exit": 5}, tmp_path / "missing.xml") == []


# --- a selected run in one process: order, --maxfail, quarantine ---

PLAIN = {
    "tests/test_a.py": "import os\n\ndef test_a():\n    open(os.environ['ORDER_LOG'], 'a').write('a\\n')\n",
    "tests/test_b.py": "import os\n\ndef test_b():\n    open(os.environ['ORDER_LOG'], 'a').write('b\\n')\n"
                       "    assert False\n",
    "tests/test_c.py": "import os\n\ndef test_c():\n    open(os.environ['ORDER_LOG'], 'a').write('c\\n')\n"
                       "    assert False\n",
    "tests/test_q.py": "import os\n\ndef test_flaky():\n    open(os.environ['ORDER_LOG'], 'a').write('q\\n')\n"
                       "    assert False\n",
}


class Plain:
    """`select_tests.run_plain` in a scratch project: pytest runs from `root`, the state is in `tmp_path`."""

    def __init__(self, tmp_path, monkeypatch):
        self.root = project(tmp_path / "root", PLAIN)
        self.state, self.log = tmp_path / "state.json", tmp_path / "order.log"
        self.held: list[str] = []
        pytest_prefix = nested_pytest.command([], python=[sys.executable])
        monkeypatch.setattr(select_tests, "ROOT", self.root)
        monkeypatch.setattr(select_tests, "PYTEST", pytest_prefix)
        monkeypatch.setattr(run_order, "state_path", lambda root=None: self.state)
        monkeypatch.setattr(run_order, "ROOT", self.root)
        monkeypatch.setattr(quarantine, "load", lambda: [
            {"test": test, "added": "2026-10-10", "expires": "2026-10-17"} for test in self.held])
        monkeypatch.setattr(quarantine, "today", lambda: datetime.date(2026, 10, 12))
        self.prefix = pytest_prefix
        self.env = nested_pytest.environment(os.environ, ORDER_LOG=str(self.log))

    def run(self, files, *, changed=(), maxfail=0):
        self.log.unlink(missing_ok=True)
        code = select_tests.run_plain([*self.prefix, "-q", *files], {"changed": list(changed)}, maxfail, self.env)
        return code, self.log.read_text().split() if self.log.exists() else []


@pytest.fixture
def plain(tmp_path, monkeypatch):
    return Plain(tmp_path, monkeypatch)


ALL = ["tests/test_a.py", "tests/test_b.py", "tests/test_c.py"]


def test_a_plain_run_takes_the_last_failed_then_the_changed_first(plain):
    code, ran = plain.run(ALL, changed=["tests/test_c.py"])
    assert code == 1 and ran == ["c", "a", "b"]
    assert run_order.read_state(plain.state) == {"tests/test_b.py": ["tests/test_b.py::test_b"],
                                                  "tests/test_c.py": ["tests/test_c.py::test_c"]}
    # Both failed last time; a changed nothing and passed.
    code, ran = plain.run(ALL)
    assert code == 1 and ran == ["b", "c", "a"]


def test_a_plain_run_stops_after_maxfail_and_keeps_what_it_did_not_run(plain):
    run_order.write_state(plain.state, {"tests/test_c.py": ["tests/test_c.py::test_c"]})
    code, ran = plain.run(ALL, maxfail=1)
    assert code == 1 and ran == ["c"]  # the first failure stops the run: a and b never ran
    assert run_order.read_state(plain.state) == {"tests/test_c.py": ["tests/test_c.py::test_c"]}
    code, ran = plain.run(ALL, maxfail=0)
    assert code == 1 and ran == ["c", "a", "b"]


def test_a_plain_run_whose_only_failures_are_quarantined_passes(plain):
    files = ["tests/test_a.py", "tests/test_q.py"]
    assert plain.run(files)[0] == 1
    plain.held = ["tests/test_q.py::test_flaky"]
    code, ran = plain.run(files)
    assert code == 0 and sorted(ran) == ["a", "q"]  # the quarantined test still ran
    # A real failure next to it still fails the run.
    assert plain.run([*files, "tests/test_b.py"])[0] == 1


def test_a_quarantined_failure_never_stops_a_plain_run(plain):
    """ts-B5 review F1: pytest's own --maxfail counted the quarantined failure and stopped, while the exit
    status ignored it, so test_a never ran and the run passed. The stop counts what the exit counts."""
    plain.held = ["tests/test_q.py::test_flaky"]
    code, ran = plain.run(["tests/test_a.py", "tests/test_q.py"], changed=["tests/test_q.py"], maxfail=1)
    assert code == 0 and ran == ["q", "a"]
    # A real failure still stops the run after it, the quarantined one never counting towards the limit.
    code, ran = plain.run(ALL + ["tests/test_q.py"], changed=["tests/test_q.py"], maxfail=1)
    assert code == 1 and ran == ["q", "a", "b"]


def test_a_full_run_counts_quarantined_failures_and_never_stops(plain, monkeypatch):
    """ts-B5 review F5: `--full --run` is the whole suite before a green tag: no --maxfail, no quarantine."""
    plain.held = ["tests/test_q.py::test_flaky"]
    monkeypatch.setenv("ORDER_LOG", str(plain.log))
    plan = {"changed": [], "lean_build": False, "selected": [],
            "commands": [[*plain.prefix, "-q", "tests/test_q.py", "tests/test_a.py"]]}
    assert select_tests.run(plan, record=False, full=True) == 1
    assert sorted(plain.log.read_text().split()) == ["a", "q"]
    assert select_tests.run(plan, record=False) == 0  # an agent's run: the quarantine applies
    with pytest.raises(ValueError, match="never stops early"):
        select_tests.run(plan, record=False, full=True, maxfail=1)


@pytest.mark.parametrize("arguments, message", [
    (["--full", "--maxfail", "2"], "--full runs every test"), (["--maxfail", "-1"], "0 or a positive count")])
def test_the_maxfail_options(capsys, monkeypatch, arguments, message):
    monkeypatch.setattr(sys, "argv", ["select_tests.py", "--paths", "x", *arguments])
    with pytest.raises(SystemExit):
        select_tests.main()
    assert message in capsys.readouterr().err


# --- the one stop rule: failed tests outside the quarantine (tools/maxfail_pytest.py) ---

STOPS = {
    "tests/test_q.py": "import os\n\n"
                       "def test_flaky():\n    open(os.environ['ORDER_LOG'], 'a').write('q\\n')\n    assert False\n\n"
                       "def test_after():\n    open(os.environ['ORDER_LOG'], 'a').write('q2\\n')\n",
    "tests/test_r.py": "import os\n\n"
                       "def test_real():\n    open(os.environ['ORDER_LOG'], 'a').write('r\\n')\n    assert False\n\n"
                       "def test_after():\n    open(os.environ['ORDER_LOG'], 'a').write('r2\\n')\n",
    "tests/test_z.py": "import os\n\ndef test_z():\n    open(os.environ['ORDER_LOG'], 'a').write('z\\n')\n",
}
HELD = {"tests/test_q.py::test_flaky"}


def test_no_run_path_passes_pytests_own_stop_options():
    """pytest's --maxfail and -x count every failure; each path takes its options from `stop_options`."""
    for maxfail in (0, 1, 5):
        options = select_tests.stop_options(maxfail, HELD)
        assert not [option for option in options if option.startswith(("--maxfail", "-x", "--exitfirst"))]
    assert select_tests.stop_options(0, HELD) == []
    assert "--ve-quarantined=tests/test_q.py::test_flaky" in select_tests.stop_options(1, HELD)


def test_the_stop_plugin_refuses_pytests_own_maxfail(tmp_path):
    root = project(tmp_path, {"tests/test_z.py": "def test_z():\n    pass\n"})
    for early in ("--maxfail=1", "-x"):
        result = pytest_run(root, *select_tests.stop_options(1, set()), early, "tests")
        assert result.returncode == 4 and "replaces --maxfail/-x" in result.stderr


@pytest.mark.parametrize("maxfail", [1, 2])
def test_a_recorded_unit_runs_past_its_quarantined_failure(tmp_path, monkeypatch, maxfail):
    """ts-B5 review F1, the recorded run: each unit got pytest's --maxfail, so a quarantined failure first in
    a file (test_ci_run in test_difffuzz.py) skipped the rest of the file and the unit still passed."""
    root = project(tmp_path / "root", STOPS)
    log = tmp_path / "order.log"
    monkeypatch.setenv("ORDER_LOG", str(log))
    monkeypatch.setenv("PYTHONPATH", str(ROOT))
    monkeypatch.setattr(test_map, "ROOT", root)
    monkeypatch.setattr(test_map, "site_packages", lambda: tmp_path)
    monkeypatch.setattr(test_map, "install_hook", lambda site: None)
    monkeypatch.setattr(test_map, "remove_hook", lambda site: None)
    monkeypatch.setattr(test_map, "tracked_paths", lambda: set())
    monkeypatch.setattr(test_map, "unit_command", lambda unit, options=(): nested_pytest.command(
        ["-q", "-p", "no:cacheprovider", *options, unit], python=[sys.executable]))
    units = ["tests/test_q.py", "tests/test_r.py", "tests/test_z.py"]
    results, failures = select_tests.record_ordered(units, tmp_path / "work", 1, maxfail, HELD)
    ran = log.read_text().split()
    assert failures["tests/test_q.py"] == ["tests/test_q.py::test_flaky"]
    if maxfail == 1:  # the real failure stops its file and the run; the quarantined one stopped neither
        assert ran == ["q", "q2", "r"] and list(results) == units[:2]
    else:
        assert ran == ["q", "q2", "r", "r2", "z"] and list(results) == units


# --- a recorded run: the units start in order and the run stops after maxfail failures ---

class Units:
    """`test_map.record_units` with each unit a small Python program: `fail` exits 1, `pass` exits 0,
    `block` waits on a pipe nobody writes (for HANG_TIMEOUT) unless the run kills it."""

    def __init__(self, tmp_path, monkeypatch, kinds: dict[str, str]):
        self.started = tmp_path / "started.log"
        programs = {
            "pass": "pass",
            "fail": "raise SystemExit(1)",
            "block": f"import os, select\nread, write = os.pipe()\nselect.select([read], [], [], {HANG_TIMEOUT})",
        }
        monkeypatch.setattr(test_map, "site_packages", lambda: tmp_path)
        monkeypatch.setattr(test_map, "install_hook", lambda site: None)
        monkeypatch.setattr(test_map, "remove_hook", lambda site: None)
        monkeypatch.setattr(test_map, "tracked_paths", lambda: set())
        monkeypatch.setattr(test_map, "unit_command", lambda unit, options=(): [sys.executable, "-c", (
            f"open({str(self.started)!r}, 'a').write({unit!r} + '\\n')\n" + programs[kinds[unit]])])
        self.work = tmp_path / "work"

    def run(self, order, *, jobs=1, stop_after=0):
        return test_map.record_units(order, self.work, jobs, HANG_TIMEOUT, stop_after=stop_after)

    def started_units(self):
        return self.started.read_text().split() if self.started.exists() else []


def test_recorded_units_start_in_the_given_order(tmp_path, monkeypatch):
    units = Units(tmp_path, monkeypatch, {"u1": "pass", "u2": "fail", "u3": "pass"})
    results = units.run(["u3", "u1", "u2"])
    assert units.started_units() == ["u3", "u1", "u2"]
    assert {unit: result["exit"] for unit, result in results.items()} == {"u3": 0, "u1": 0, "u2": 1}


def test_a_recorded_run_stops_after_maxfail_failures(tmp_path, monkeypatch):
    units = Units(tmp_path, monkeypatch, {"u1": "fail", "u2": "pass", "u3": "fail", "u4": "pass"})
    results = units.run(["u1", "u2", "u3", "u4"], stop_after=1)
    assert units.started_units() == ["u1"] and list(results) == ["u1"]
    units = Units(tmp_path / "again", monkeypatch, {"u1": "fail", "u2": "pass", "u3": "fail", "u4": "pass"})
    (tmp_path / "again").mkdir()
    results = units.run(["u1", "u2", "u3", "u4"], stop_after=2)
    assert units.started_units() == ["u1", "u2", "u3"] and list(results) == ["u1", "u2", "u3"]


def test_stopping_kills_the_running_units(tmp_path, monkeypatch):
    """A unit still running when the run stops is killed and has no result (its partial coverage is not
    kept); without the stop it would wait HANG_TIMEOUT and pass."""
    units = Units(tmp_path, monkeypatch, {"slow": "block", "first": "fail", "later": "pass"})
    results = units.run(["slow", "first", "later"], jobs=2, stop_after=1)
    assert list(results) == ["first"] and "later" not in units.started_units()
    assert not (units.work / "slow.result.json").exists()


def test_without_maxfail_every_unit_runs(tmp_path, monkeypatch):
    units = Units(tmp_path, monkeypatch, {"u1": "fail", "u2": "fail", "u3": "pass"})
    assert list(units.run(["u1", "u2", "u3"])) == ["u1", "u2", "u3"]



# --- killing a recorded run kills its units, though each runs in its own session ---

RECORDER = """
import pathlib, signal, sys
for number in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
    signal.signal(number, signal.SIG_DFL)
sys.path.insert(0, {tools!r})
import test_map
test_map.site_packages = lambda: pathlib.Path({work!r})
test_map.install_hook = test_map.remove_hook = lambda site: None
test_map.tracked_paths = set
unit = ("import os, select\\n"
        "os.write(os.open({fifo!r}, os.O_WRONLY), str(os.getpid()).encode())\\n"
        "read, write = os.pipe()\\n"
        "select.select([read], [], [], {timeout})")
test_map.unit_command = lambda name, options=(): [sys.executable, "-c", unit]
test_map.record_units(["u"], pathlib.Path({work!r}) / "w", 1, {timeout})
"""


def alive(pid: int) -> bool:
    try:
        return Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0] != "Z"
    except (FileNotFoundError, IndexError):
        return False


@pytest.mark.parametrize("number", [signal.SIGTERM, signal.SIGINT, signal.SIGHUP],
                         ids=lambda number: number.name)
def test_killing_a_recorded_run_kills_its_units(tmp_path, number):
    """ts-B5 review F2: each unit runs in its own session, so a signal to the run's process group (a harness
    timeout, Ctrl-C, a closed terminal) left the running units going for up to UNIT_TIMEOUT."""
    fifo = tmp_path / "pid"
    os.mkfifo(fifo)
    reader = os.open(fifo, os.O_RDONLY | os.O_NONBLOCK)
    script = RECORDER.format(tools=str(ROOT / "tools"), work=str(tmp_path), fifo=str(fifo), timeout=HANG_TIMEOUT)
    recorder = subprocess.Popen([sys.executable, "-c", script], cwd=ROOT, start_new_session=True,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    unit = survived = None
    try:
        assert select.select([reader], [], [], HANG_TIMEOUT)[0], "the unit never started"
        unit = int(os.read(reader, 64))
        os.killpg(recorder.pid, number)
        recorder.wait(timeout=HANG_TIMEOUT)
        survived = alive(unit)
    finally:
        os.close(reader)
        for group in (recorder.pid, unit):
            if group is not None and alive(group):
                os.killpg(group, signal.SIGKILL)  # the unit leads its own session
    assert not survived, "the unit survived its run being killed"
    assert recorder.returncode != 0


def test_a_failing_recorded_run_kills_its_other_units(tmp_path, monkeypatch):
    """Any abnormal end of the run stops it: one unit's crash kills the unit still running beside it."""
    units = Units(tmp_path, monkeypatch, {"slow": "block", "bad": "pass"})
    command, start = test_map.unit_command, test_map.Stop.start
    started, running = [], threading.Event()

    def crash(unit, options=()):
        if unit == "bad":
            assert running.wait(HANG_TIMEOUT), "the slow unit never started"
            raise OSError("cannot start")
        return command(unit, options)

    def record_start(self, *arguments, **options):
        started.append(start(self, *arguments, **options))
        running.set()
        return started[-1]

    monkeypatch.setattr(test_map, "unit_command", crash)
    monkeypatch.setattr(test_map.Stop, "start", record_start)
    with pytest.raises(OSError, match="cannot start"):
        units.run(["slow", "bad"], jobs=2)
    assert len(started) == 1 and started[0].wait(timeout=HANG_TIMEOUT) == -signal.SIGKILL
