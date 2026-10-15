"""The measured split and the light-tier command plan."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest

from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import heavy_tests  # noqa: E402
import nested_pytest  # noqa: E402
import quarantine  # noqa: E402
import run_order  # noqa: E402
import select_tests  # noqa: E402
from conftest import HEAVY_IDS, pytest_collection_modifyitems  # noqa: E402


def test_heavy_inventory_is_generated_from_complete_measurement():
    run, times = heavy_tests.read_report(heavy_tests.REPORT)
    actual = json.loads(heavy_tests.INVENTORY.read_text())
    assert actual == heavy_tests.inventory(run, times)
    # Counts derive from the committed report, so `--write --report <nightly>` keeps this green.
    assert actual["collected_count"] == len(times)
    assert {row["nodeid"] for row in actual["heavy"]} == HEAVY_IDS
    assert HEAVY_IDS == {nodeid for nodeid, seconds in times.items() if seconds >= heavy_tests.THRESHOLD}


def test_pytest_duration_report_includes_setup_call_and_teardown(tmp_path):
    report = tmp_path / "durations.txt"
    report.write_text("10.00s call tests/test_a.py::test_one\n"
                      "11.00s setup tests/test_a.py::test_one\n"
                      "0.25s teardown tests/test_a.py::test_one\n"
                      "0.01s call tests/test_a.py::test_two\n"
                      "0.02s call tests/test_a.py::test_with_space[plain words]\n")
    run, times = heavy_tests.read_report(report)
    assert run == "durations.txt"
    assert times == {"tests/test_a.py::test_one": 21.25,
                     "tests/test_a.py::test_two": 0.01,
                     "tests/test_a.py::test_with_space[plain words]": 0.02}


def test_no_test_fails_because_a_test_became_slow(tmp_path, monkeypatch, capsys):
    """tarch-b1 review F1: a seeded 30 s unmarked test failed a budget check. Slowness is drift
    reported to the DRI, never a failure: `--check --report <nightly>` lists the rows and exits 0."""
    assert not hasattr(heavy_tests, "BUDGET") and not hasattr(heavy_tests, "check_budget")
    inventory = tmp_path / "heavy.json"
    inventory.write_text(json.dumps({"heavy": [
        {"nodeid": "tests/test_old.py::test_now_fast", "seconds": 12.0, "run": "a"},
        {"nodeid": "tests/test_old.py::test_renamed", "seconds": 40.0, "run": "a"},
        {"nodeid": "tests/test_old.py::test_still_slow", "seconds": 15.0, "run": "a"}]}))
    report = tmp_path / "nightly.json"
    report.write_text(json.dumps({"run": "nightly", "tests": {
        "tests/test_new.py::test_slow": 30.0, "tests/test_new.py::test_fast": 0.01,
        "tests/test_old.py::test_now_fast": 2.0, "tests/test_old.py::test_still_slow": 16.0}}))
    monkeypatch.setattr(heavy_tests, "INVENTORY", inventory)
    monkeypatch.setattr(sys, "argv", ["heavy_tests.py", "--check", "--report", str(report)])
    assert heavy_tests.main() == 0
    assert capsys.readouterr().out.splitlines() == [
        "enters heavy: tests/test_new.py::test_slow (30.00 s in nightly)",
        "leaves heavy: tests/test_old.py::test_now_fast (2.00 s in nightly, was 12.00 s)",
        "absent from nightly: tests/test_old.py::test_renamed (heavy at 40.00 s)"]


def test_check_refuses_an_inventory_stale_against_the_committed_report(tmp_path, monkeypatch):
    report, inventory = tmp_path / "durations.json", tmp_path / "heavy.json"
    report.write_text(json.dumps({"run": "committed", "tests": {"tests/test_a.py::test_slow": 30.0,
                                                                "tests/test_a.py::test_fast": 0.01}}))
    monkeypatch.setattr(heavy_tests, "REPORT", report)
    monkeypatch.setattr(heavy_tests, "INVENTORY", inventory)
    monkeypatch.setattr(sys, "argv", ["heavy_tests.py", "--check"])
    inventory.write_text(json.dumps({"heavy": []}))
    assert heavy_tests.main() == 1
    inventory.write_text(json.dumps(heavy_tests.inventory(*heavy_tests.read_report(report))))
    assert heavy_tests.main() == 0


def test_every_measured_node_is_exactly_light_or_heavy():
    _, times = heavy_tests.read_report(heavy_tests.REPORT)

    class Item:
        def __init__(self, nodeid):
            self.nodeid = nodeid
            self.marks = []

        def add_marker(self, mark):
            self.marks.append(mark)

        def get_closest_marker(self, name):
            return None

    items = [Item(nodeid) for nodeid in times]
    pytest_collection_modifyitems(items)
    marked = {item.nodeid for item in items if item.marks}
    assert marked == HEAVY_IDS
    assert len(items) - len(marked) == len(times) - len(HEAVY_IDS)
    assert all(len(item.marks) <= 1 for item in items)


def test_an_unlisted_manual_heavy_mark_is_refused():
    class Item:
        nodeid = "tests/test_new.py::test_manual"

        def get_closest_marker(self, name):
            return pytest.mark.heavy

    with pytest.raises(pytest.UsageError, match="absent from tests/heavy.json"):
        pytest_collection_modifyitems([Item()])


def test_light_tier_runs_every_light_node_and_selected_heavy_function(tmp_path):
    inventory = {"run": "fixture", "collected_count": 3,
                 "heavy": [{"nodeid": "tests/test_a.py::test_changed", "seconds": 30, "run": "fixture"},
                           {"nodeid": "tests/test_b.py::test_other", "seconds": 40, "run": "fixture"}]}
    path = tmp_path / "heavy.json"
    path.write_text(json.dumps(inventory))
    plan = {"selected": ["tests/test_a.py"], "commands": [[*select_tests.PYTEST, "-q", "tests/test_a.py"]]}
    tier = select_tests.light_tier(plan, path, jobs=6)
    assert tier["tier"]["light_count"] == 1
    assert tier["tier"]["selected_heavy"] == ["tests/test_a.py::test_changed"]
    light, heavy = tier["commands"]
    assert light[-1] == "tests" and "not heavy" in light[-2]
    assert heavy[-1] == "tests/test_a.py" and heavy[-2].endswith(" and heavy")
    assert "tests/test_b.py" not in heavy
    assert tier["may_select_none"] == [heavy]
    assert all("not live and not nightly" in command[-2] for command in (light, heavy))
    assert all(command[command.index("-n") + 1] == "6" for command in (light, heavy))


def test_no_light_tier_command_names_a_saved_node_id(tmp_path):
    """tarch-b1 review F2: the heavy stage put saved node IDs on the command line, so a renamed
    heavy test made pytest exit 4. Every command names files; the hook marks what is collected."""
    real = json.loads(heavy_tests.INVENTORY.read_text())["heavy"]
    path = tmp_path / "heavy.json"
    path.write_text(json.dumps({"run": "fixture", "collected_count": len(real) + 1, "heavy": [
        *real, {"nodeid": "tests/test_heavy_tests.py::test_renamed", "seconds": 30, "run": "fixture"}]}))
    selected = sorted({row["nodeid"].split("::", 1)[0] for row in real} | {"tests/test_heavy_tests.py"})
    plan = select_tests.light_tier({"selected": selected, "commands": []}, path, jobs=1)
    assert plan["tier"]["selected_heavy_count"] == len(real) + 1
    for command in plan["commands"]:
        assert not [argument for argument in command if "::" in argument]
    assert plan["tier"]["heavy_files"] == selected
    assert plan["commands"][-1][-len(selected):] == selected


def test_a_renamed_heavy_test_does_not_break_the_heavy_stage(tmp_path):
    """tarch-b1 review F2, the probe: collect the heavy stage the plan prints, with one heavy ID
    renamed away and one still real; the real one is collected, the stale one is no error."""
    real = json.loads(heavy_tests.INVENTORY.read_text())["heavy"][0]["nodeid"]
    unit = real.split("::", 1)[0]
    path = tmp_path / "heavy.json"
    path.write_text(json.dumps({"run": "fixture", "collected_count": 2, "heavy": [
        {"nodeid": real, "seconds": 30, "run": "fixture"},
        {"nodeid": f"{unit}::test_renamed_away", "seconds": 30, "run": "fixture"},
        {"nodeid": "tests/test_heavy_tests.py::test_renamed", "seconds": 30, "run": "fixture"}]}))
    for selected, expected in (([unit], 0), (["tests/test_heavy_tests.py"], select_tests.NO_TESTS_COLLECTED)):
        heavy = select_tests.light_tier({"selected": selected, "commands": []}, path, jobs=1)["commands"][-1]
        command = [sys.executable, *heavy[len(select_tests.UV_PYTHON):], "--co", "-p", "no:cacheprovider"]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=HANG_TIMEOUT,
                                env=nested_pytest.environment(os.environ, VE_NATIVE_PREBUILT="1"))
        assert result.returncode == expected, result.stdout + result.stderr
        assert (real in result.stdout) == (expected == 0)
        assert "test_renamed" not in result.stdout


def test_a_heavy_stage_that_selects_nothing_is_skipped(tmp_path, monkeypatch, capsys):
    """When every selected heavy test is gone, the stage selects nothing: `run` skips it instead of
    failing with pytest's exit 5, and any other command that selects nothing still fails."""
    root = tmp_path / "root"
    (root / "tests").mkdir(parents=True)
    (root / "tests/test_a.py").write_text(textwrap.dedent("""
        def test_light():
            pass
    """))
    prefix = nested_pytest.command([], python=[sys.executable])
    monkeypatch.setattr(select_tests, "ROOT", root)
    monkeypatch.setattr(select_tests, "PYTEST", prefix)
    monkeypatch.setattr(run_order, "ROOT", root)
    monkeypatch.setattr(run_order, "state_path", lambda root=None: tmp_path / "state.json")
    monkeypatch.setattr(quarantine, "load", lambda: [])
    heavy = [*prefix, "-q", "-p", "no:cacheprovider", "-m", "heavy", "tests/test_a.py"]
    plan = {"changed": [], "lean_build": False, "selected": [], "commands": [heavy], "may_select_none": [heavy]}
    assert select_tests.run(plan, record=False) == 0
    assert "heavy stage skipped" in capsys.readouterr().out
    assert select_tests.run({**plan, "may_select_none": []}, record=False) == select_tests.NO_TESTS_COLLECTED
