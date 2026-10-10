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
import subprocess
import sys
import textwrap

import pytest

from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import nested_pytest  # noqa: E402
import quarantine  # noqa: E402
import run_order  # noqa: E402
import select_tests  # noqa: E402
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


def test_maxfail_is_a_count(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["select_tests.py", "--paths", "x", "--maxfail", "-1"])
    with pytest.raises(SystemExit):
        select_tests.main()
    assert "--maxfail is 0 or a positive count" in capsys.readouterr().err
