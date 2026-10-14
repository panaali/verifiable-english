"""The full gate must reject missing coverage while honoring exact optional cases."""
import json
import os
import sys

import pytest

from subprocesses import HANG_TIMEOUT
from tools import gate, nested_pytest
from tools.gate import REQUIRED_FAMILIES, ROOT, interpret_pytest, permitted


def test_exact_parameterized_skip_and_live_deselection_are_accounted_for():
    policy = json.loads((ROOT / "tools/gate-optional.json").read_text())
    admission = "tests/test_p0_three_way.py::test_rust_matches_expected[admission]"
    live = "tests/test_llm.py::test_live_smoke"
    assert permitted(admission, "Skipped: admission is outside Rust scope",
                     policy["optional_tests"])
    for family in ("dependency-order", "labels"):
        node = f"tests/test_p0_three_way.py::test_rust_matches_expected[{family}]"
        assert permitted(node, f"Skipped: {family} is outside Rust scope", policy["optional_tests"])
        assert not permitted(node, "Skipped: admission is outside Rust scope", policy["optional_tests"])
    assert not permitted(admission.replace("admission", "labels"),
                         "Skipped: admission is outside Rust scope", policy["optional_tests"])
    selected = [f"tests/{name}::test_covered" for name in REQUIRED_FAMILIES] + [admission]
    events = {"collected": selected + [live], "selected": selected,
              "deselected": [live], "collection_reports": [],
              "tests": {node: {"outcome": "passed"} for node in selected[:-1]} |
                       {admission: {"outcome": "skipped", "reason": "Skipped: admission is outside Rust scope"}}}
    result = {"counts": {}, "skips": [], "failures": []}
    interpret_pytest(result, events, policy, events["collected"])
    assert not result["failures"]
    assert result["counts"]["selected"] == len(selected)
    assert result["counts"]["deselected"] == 1
    assert {row["nodeid"] for row in result["skips"]} == {admission, live}


def test_the_gate_collects_the_whole_suite_cleanly(tmp_path):
    """Review: the collection lacked the deselected tests/test_llm.py::test_live_smoke, which
    the gate's recorder collects, and the gate's pytest (plugin autoload off) stopped with
    an internal error on an xdist-only conftest hook. The gate's own collection command,
    in this environment, must succeed with no collection report or duplicate ID, and
    record the deselected live test: the merge base's collection is compared with it."""
    events = gate.collect({**os.environ, "VE_NATIVE_PREBUILT": "1"}, tmp_path / "collection.json")
    assert events["collection_reports"] == []
    assert len(events["collected"]) == len(set(events["collected"]))
    assert set(REQUIRED_FAMILIES) <= {nodeid.split("::")[0].removeprefix("tests/") for nodeid in events["selected"]}
    assert "tests/test_llm.py::test_live_smoke" in events["deselected"]


# Gate run review: under the gate (plugin autoload off, inherited by children) a nested
# recording run on `-n auto` failed with "unrecognized arguments: -n", though it passed on a
# developer's machine. tests/test_nested_pytest.py fails on a pytest command built anywhere
# but tools/nested_pytest.py, which turns autoload off and names the plugins.


def test_a_nested_run_on_workers_works_with_autoload_off(tmp_path):
    (tmp_path / "test_one.py").write_text("def test_one():\n    pass\n")
    env = nested_pytest.environment({**os.environ, "PYTHONPATH": str(ROOT), "PYTEST_ADDOPTS": "-p no:xdist"})
    assert env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] == "1" and "PYTEST_ADDOPTS" not in env
    run = gate.subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", str(tmp_path)], workers=2),
                              cwd=tmp_path, env=env, capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert run.returncode == 0, run.stdout + run.stderr


def test_the_gate_suite_runs_on_xdist_on_any_worker_count():
    """merge_pytest_events reads each xdist worker's collection, so the suite is on xdist
    even on one worker; `auto` is tests/conftest.py's load-aware count."""
    for workers, count in (("1", "1"), ("4", "4"), ("auto", "auto")):
        command = gate.suite_command([sys.executable], workers)
        assert command[command.index("-n") - 2:command.index("-n") + 2] == ["-p", "xdist", "-n", count]
    assert "-n" not in gate.collection_command([sys.executable])


SAMPLE = """import pytest

def test_passes():
    pass

@pytest.mark.live
def test_live_call():
    pass

def test_fails():
    assert False
"""


def test_the_gate_records_a_parallel_suite_run(tmp_path, monkeypatch):
    """The gate's two pytest runs on a sample project: the serial collection records the
    deselected live test, the xdist run records every result and each worker's selection."""
    monkeypatch.setattr(gate, "REQUIRED_FAMILIES", ())
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_sample.py").write_text(SAMPLE)
    (tmp_path / "pytest.ini").write_text("[pytest]\nmarkers =\n    live: a model call\n")
    env = nested_pytest.environment({**os.environ, "PYTHONPATH": str(ROOT)})
    collection = tmp_path / "collection.json"
    gate.subprocess.run(gate.collection_command([sys.executable]), cwd=tmp_path, check=True,
                        env={**env, "VE_GATE_PYTEST_RESULT": str(collection)}, capture_output=True,
                        timeout=HANG_TIMEOUT)
    suite = tmp_path / "suite.json"
    run = gate.subprocess.run(gate.suite_command([sys.executable], "2"), cwd=tmp_path, text=True,
                              env={**env, "VE_GATE_PYTEST_RESULT": str(suite)}, capture_output=True,
                              timeout=HANG_TIMEOUT)
    assert run.returncode == 1, run.stdout + run.stderr
    events = gate.merge_pytest_events(json.loads(collection.read_text()), json.loads(suite.read_text()))
    ids = ["tests/test_sample.py::test_passes", "tests/test_sample.py::test_fails"]
    assert events["selected"] == ids and events["deselected"] == ["tests/test_sample.py::test_live_call"]
    assert set(events["workers"]) == {"gw0", "gw1"} and all(row == ids for row in events["workers"].values())
    assert {node: row["outcome"] for node, row in events["tests"].items()} == {ids[0]: "passed", ids[1]: "failed"}
    result = {"counts": {}, "skips": [], "failures": []}
    interpret_pytest(result, events, {"optional_tests": [], "deselected_tests": [
        {"nodeid": "tests/test_sample.py::test_live_*",
         "reason": "Calls real model CLIs; excluded by the non-live gate."}]}, events["collected"])
    assert [failure.get("nodeid") for failure in result["failures"]] == [ids[1]]


@pytest.mark.parametrize("workers", [None, {}, {"gw0": ["tests/a.py::test_a"]},
                                     {"gw0": ["tests/a.py::test_a", "tests/b.py::test_b"],
                                      "gw1": ["tests/b.py::test_b", "tests/a.py::test_a", "tests/c.py::test_c"]}],
                         ids=["absent", "none", "fewer", "one worker more"])
def test_a_suite_run_whose_workers_did_not_collect_the_selection_fails(workers):
    selected = ["tests/a.py::test_a", "tests/b.py::test_b"]
    collection = {"collected": selected, "selected": selected, "deselected": [], "collection_reports": [],
                  "tests": {}, "workers": {}}
    suite = {"tests": {node: {"outcome": "passed"} for node in selected}}
    if workers is not None:
        suite["workers"] = workers
    with pytest.raises(RuntimeError, match="worker"):
        gate.merge_pytest_events(collection, suite)
