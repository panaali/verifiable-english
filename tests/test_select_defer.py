"""`select_tests --defer-heavy`: a builder run leaves the heavy test files that only weak reasons select
to the chain gate, and never records them as passed.

Synthetic plans and maps; nothing runs a test file and every write goes under tmp_path.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import run_order  # noqa: E402
import select_tests  # noqa: E402
import test_map  # noqa: E402

HEAVY = select_tests.DEFER_SECONDS + 1


def plan_of(reasons: dict[str, list[str]], *, changed=(), full=False) -> dict:
    selected = sorted(reasons)
    files = [unit for unit in selected if unit.startswith("tests/")]
    return {"changed": list(changed), "selected": selected, "selected_count": len(selected), "full": full,
            "reasons": reasons, "map": None, "lean_cutoff": None,
            "commands": [["lake", "build"], [*select_tests.PYTEST, "-q", *files]]}


def test_the_weak_reasons_are_the_static_graph_a_listed_directory_and_smoke():
    weak = ["imports ve/english.py (static)", "names conformance/x.json (static)", "runs Lean via lean/VE/A.lean (static)",
            "lists the directory of docs/new.md", "smoke"]
    strong = ["reads conformance/x.json", "ve/english.py:parse_english", "ve/english.py: import-time change",
              "changed test", "runs Lean via lean/VE/A.lean", "runs service mode via lean/VE/A.lean",
              "history inventory", "manifest contract", "ve/english.py reads a changed name"]
    assert [reason for reason in weak + strong if select_tests.weak_reason(reason)] == weak


def test_a_heavy_file_selected_only_for_weak_reasons_is_deferred():
    plan = plan_of({"tests/test_weak.py": ["imports ve/a.py (static)", "lists the directory of ve/b.py"],
                    "tests/test_strong.py": ["imports ve/a.py (static)", "reads ve/a.py"],
                    "tests/test_light.py": ["imports ve/a.py (static)"]})
    seconds = {"tests/test_weak.py": 600.0, "tests/test_strong.py": 600.0, "tests/test_light.py": 30.0}
    deferred = select_tests.defer_heavy(plan, seconds)
    assert deferred["deferred"] == {"tests/test_weak.py": {
        "seconds": 600.0, "reasons": ["imports ve/a.py (static)", "lists the directory of ve/b.py"]}}
    assert deferred["deferred_seconds"] == 600.0
    assert deferred["selected"] == ["tests/test_light.py", "tests/test_strong.py"]
    assert deferred["selected_count"] == 2
    assert deferred["commands"] == [["lake", "build"],
                                    [*select_tests.PYTEST, "-q", "tests/test_light.py", "tests/test_strong.py"]]
    assert plan["selected_count"] == 3  # the input plan is unchanged


def test_only_a_file_over_the_threshold_is_heavy():
    plan = plan_of({"tests/test_edge.py": ["smoke (static)"], "tests/test_over.py": ["imports ve/a.py (static)"]})
    seconds = {"tests/test_edge.py": select_tests.DEFER_SECONDS, "tests/test_over.py": HEAVY}
    assert list(select_tests.defer_heavy(plan, seconds)["deferred"]) == ["tests/test_over.py"]
    assert list(select_tests.defer_heavy(plan, seconds, threshold=HEAVY)["deferred"]) == []


@pytest.mark.parametrize("unit, why", [
    ("tests/test_changed.py", "a changed test"),
    (select_tests.SMOKE[0], "SMOKE"),
    (select_tests.HISTORY_TEST, "HISTORY_TEST"),
    ("tests/test_failed.py", "failed last time"),
    ("tests/test_unrecorded.py", "no recorded seconds"),
    ("trust_mutants", "not a test file"),
])
def test_these_heavy_weak_units_always_stay(unit, why):
    plan = plan_of({unit: ["smoke"], "tests/test_weak.py": ["imports ve/a.py (static)"]},
                   changed=["tests/test_changed.py"])
    seconds = {"tests/test_weak.py": HEAVY, **({} if why == "no recorded seconds" else {unit: HEAVY})}
    deferred = select_tests.defer_heavy(plan, seconds, keep={"tests/test_failed.py"})
    assert list(deferred["deferred"]) == ["tests/test_weak.py"], why
    assert unit in deferred["selected"], why


def test_a_full_plan_defers_nothing():
    plan = plan_of({"tests/test_weak.py": ["imports ve/a.py (static)"]}, full=True)
    deferred = select_tests.defer_heavy(plan, {"tests/test_weak.py": HEAVY})
    assert deferred["deferred"] == {} and deferred["selected"] == plan["selected"]
    assert deferred["commands"] == plan["commands"]


def test_deferring_every_file_drops_the_pytest_command():
    """A pytest command left with no test file would run the whole suite."""
    plan = plan_of({"tests/test_weak.py": ["imports ve/a.py (static)"]})
    deferred = select_tests.defer_heavy(plan, {"tests/test_weak.py": HEAVY})
    assert deferred["selected"] == [] and deferred["commands"] == [["lake", "build"]]


def test_the_seconds_are_the_whole_process_seconds_of_the_plans_map(tmp_path, monkeypatch):
    path = tmp_path / "tree.json.gz"
    path.write_text("")
    monkeypatch.setattr(test_map, "load", lambda found: {"status": {
        "tests/test_a.py": {"exit": 0, "seconds": 321.5, "opaque": []},
        "tests/test_b.py": {"exit": "stale", "seconds": None, "opaque": []}}} if found == path else {})
    assert select_tests.map_seconds({"map": {"path": str(path)}}) == {"tests/test_a.py": 321.5, "tests/test_b.py": 0.0}
    assert select_tests.map_seconds({"map": None}) == {}
    assert select_tests.map_seconds({"map": {"path": ""}}) == {}
    monkeypatch.setattr(test_map, "load", lambda found: (_ for _ in ()).throw(EOFError("truncated")))
    assert select_tests.map_seconds({"map": {"path": str(path)}}) == {}


def recorded_map(tmp_path, monkeypatch, plan: dict, base_status: dict) -> dict:
    """The map `run_recorded` writes for `plan`, whose selected units all pass, over a base map whose
    entries are `base_status`; nothing runs."""
    written = {}
    every = sorted({*plan["selected"], *base_status})
    monkeypatch.setattr(test_map, "working_tree_id", lambda: "a" * 40)
    monkeypatch.setattr(test_map, "build_natives", lambda: None)
    monkeypatch.setattr(run_order, "state_path", lambda: tmp_path / "state.json")
    monkeypatch.setattr(run_order, "last_failed", lambda **_: {})
    monkeypatch.setattr(select_tests.tempfile, "mkdtemp", lambda prefix: str(tmp_path / "work"))
    monkeypatch.setattr(select_tests, "record_ordered", lambda ordered, *_: (
        {unit: {"exit": 0, "seconds": 1.0} for unit in ordered}, {unit: [] for unit in ordered}))
    monkeypatch.setattr(select_tests, "units", lambda: every)
    monkeypatch.setattr(select_tests, "resolve_map", lambda *_: type("Base", (), {
        "commit": "b" * 40, "status": base_status, **{key: {} for key in (
            "tests", "functions", "reads", "dirs", "programs", "operations", "presence", "modes")}})())
    monkeypatch.setattr(select_tests, "working_changes", lambda commit: ({}, {}))
    monkeypatch.setattr(select_tests, "uncertain_units", lambda *_: set())
    monkeypatch.setattr(select_tests.source_graph, "load", lambda root: None)
    monkeypatch.setattr(test_map, "unit_edges", lambda data: {unit: {} for unit in base_status})
    monkeypatch.setattr(test_map, "build_map", lambda results, commit: {"status": results})
    monkeypatch.setattr(test_map, "write_map", lambda data, path: written.update(data))
    assert select_tests.run_recorded({**plan, "map": {"path": "base"}}, 1, held=set()) == 0
    return written["status"]


def test_a_deferred_unit_is_never_recorded_as_passed(tmp_path, monkeypatch):
    plan = plan_of({"tests/test_weak.py": ["imports ve/a.py (static)"], "tests/test_ran.py": ["reads ve/a.py"]})
    plan = select_tests.defer_heavy(plan, {"tests/test_weak.py": HEAVY})
    passed = {"exit": 0, "seconds": HEAVY, "opaque": []}
    status = recorded_map(tmp_path, monkeypatch, plan, {"tests/test_weak.py": passed, "tests/test_other.py": passed})
    assert status["tests/test_weak.py"]["exit"] == "deferred"
    assert status["tests/test_other.py"]["exit"] == 0  # unselected: the base map's entry, as before
    assert status["tests/test_ran.py"]["exit"] == 0


def main_plan(monkeypatch, capsys, plan: dict, seconds: dict, failed: dict, *flags: str) -> dict:
    monkeypatch.setattr(select_tests, "select", lambda *_, **__: plan)
    monkeypatch.setattr(select_tests, "map_seconds", lambda found: seconds if found is plan else {})
    monkeypatch.setattr(run_order, "last_failed", lambda: failed)
    monkeypatch.setattr(sys, "argv", ["select_tests.py", "--paths", "ve/a.py", "--static", "--json", *flags])
    assert select_tests.main() == 0
    return json.loads(capsys.readouterr().out)


def test_the_option_defers_and_keeps_what_failed_last_time(monkeypatch, capsys):
    plan = plan_of({"tests/test_weak.py": ["imports ve/a.py (static)"],
                    "tests/test_failed.py": ["imports ve/a.py (static)"]})
    seconds = {"tests/test_weak.py": HEAVY, "tests/test_failed.py": HEAVY}
    found = main_plan(monkeypatch, capsys, plan, seconds, {"tests/test_failed.py": ["tests/test_failed.py::t"]},
                      "--defer-heavy")
    assert list(found["deferred"]) == ["tests/test_weak.py"] and found["selected"] == ["tests/test_failed.py"]
    assert "deferred" not in main_plan(monkeypatch, capsys, plan, seconds, {})  # opt-in


@pytest.mark.parametrize("other", [["--full"], ["--impacted"], ["--tier", "light"]])
def test_the_option_refuses_full_impacted_and_tier_runs(monkeypatch, other):
    monkeypatch.setattr(sys, "argv", ["select_tests.py", "--paths", "ve/a.py", "--defer-heavy", *other])
    with pytest.raises(SystemExit) as stopped:
        select_tests.main()
    assert stopped.value.code == 2
