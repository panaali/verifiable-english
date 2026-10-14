"""The measured split and the light-tier command plan."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import heavy_tests  # noqa: E402
import select_tests  # noqa: E402
from conftest import HEAVY_IDS, pytest_collection_modifyitems  # noqa: E402


def test_heavy_inventory_is_generated_from_complete_measurement():
    run, times = heavy_tests.read_report(heavy_tests.REPORT)
    actual = json.loads(heavy_tests.INVENTORY.read_text())
    assert actual == heavy_tests.inventory(run, times)
    assert len(times) == 15179
    assert len(actual["heavy"]) == 171
    assert len(HEAVY_IDS) == 171


def test_pytest_duration_report_includes_setup_call_and_teardown(tmp_path):
    report = tmp_path / "durations.txt"
    report.write_text("10.00s call tests/test_a.py::test_one\n"
                      "11.00s setup tests/test_a.py::test_one\n"
                      "0.25s teardown tests/test_a.py::test_one\n"
                      "0.01s call tests/test_a.py::test_two\n")
    run, times = heavy_tests.read_report(report)
    assert run == "durations.txt"
    assert times == {"tests/test_a.py::test_one": 21.25,
                     "tests/test_a.py::test_two": 0.01}


def test_a_new_unmarked_slow_test_fails_the_budget_check(tmp_path, monkeypatch):
    times = {"tests/test_new.py::test_slow": 30.0,
             "tests/test_new.py::test_fast": 0.01}
    assert heavy_tests.check_budget(times, set()) == ["tests/test_new.py::test_slow"]
    assert heavy_tests.check_budget(times, {"tests/test_new.py::test_slow"}) == []
    report = tmp_path / "durations.json"
    report.write_text(json.dumps({"run": "seed", "tests": times}))
    inventory = tmp_path / "heavy.json"
    inventory.write_text(json.dumps({"heavy": []}))
    monkeypatch.setattr(heavy_tests, "INVENTORY", inventory)
    monkeypatch.setattr(sys, "argv", ["heavy_tests.py", "--check", "--report", str(report)])
    assert heavy_tests.main() == 1


def test_every_measured_node_is_exactly_light_or_heavy():
    _, times = heavy_tests.read_report(heavy_tests.REPORT)

    class Item:
        def __init__(self, nodeid):
            self.nodeid = nodeid
            self.marks = []

        def add_marker(self, mark):
            self.marks.append(mark)

    items = [Item(nodeid) for nodeid in times]
    pytest_collection_modifyitems(items)
    marked = {item.nodeid for item in items if item.marks}
    assert marked == HEAVY_IDS
    assert len(items) - len(marked) == 15008
    assert all(len(item.marks) <= 1 for item in items)


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
    assert heavy[-1] == "tests/test_a.py::test_changed"
    assert "tests/test_b.py::test_other" not in heavy
    assert all("not live and not nightly" in command[-2] for command in (light, heavy))
    assert all(command[command.index("-n") + 1] == "6" for command in (light, heavy))
