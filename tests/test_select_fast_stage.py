"""`select_tests --fast-stage`: the cheap units of a selection, run first on the host that sends the rest to
sharded runners, so a failing pin is heard in minutes rather than after the shards' wall.

Synthetic plans and maps; no test file runs (`run_plain` and the Lean freshness check are stubbed).
"""
from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import select_tests  # noqa: E402

CHEAP = select_tests.FAST_UNIT_SECONDS


def coverage(seconds: dict[str, float], *, programs: dict[str, list[str]] | None = None,
             failed=(), opaque=()) -> select_tests.Coverage:
    tests = sorted(seconds)
    return select_tests.Coverage({
        "commit": "0" * 40, "tests": tests, "functions": {}, "reads": {}, "dirs": {}, "operations": {},
        "presence": {}, "modes": {},
        "programs": {name: [tests.index(unit) for unit in units] for name, units in (programs or {}).items()},
        "status": {unit: {"exit": 1 if unit in failed else 0, "seconds": seconds[unit],
                          "opaque": ["subprocess"] if unit in opaque else []} for unit in tests}})


def plan_of(selected, *, lean_build=False, cargo=False) -> dict:
    commands = [["lake", "build"]] if lean_build else []
    if cargo:
        commands.append([*select_tests.CARGO, "build", "--locked", "--release"])
    return {"changed": [], "selected": list(selected), "lean_build": lean_build, "map": {"path": "map.json.gz"},
            "commands": [*commands, [*select_tests.PYTEST, "-q", *selected]]}


def test_the_cheap_recorded_units_go_cheapest_first():
    cov = coverage({"tests/test_pin.py": 39.0, "tests/test_tiny.py": 2.0, "tests/test_edge.py": CHEAP,
                    "tests/test_long.py": CHEAP + 1, "tests/test_failed.py": 1.0, "tests/test_opaque.py": 1.0,
                    "tests/test_unselected.py": 1.0},
                   failed=["tests/test_failed.py"], opaque=["tests/test_opaque.py"])
    plan = plan_of([unit for unit in cov.tests if unit != "tests/test_unselected.py"]
                   + ["tests/test_unmapped.py", "tests/test_tiny.py::chunk(1/2)", "conformance"])
    units = select_tests.fast_units(plan, cov, lean_fresh=True)
    assert units == ["tests/test_tiny.py", "tests/test_pin.py", "tests/test_edge.py"]


def test_the_budget_stops_the_stage():
    cov = coverage({f"tests/test_{i}.py": 50.0 for i in range(6)})
    plan = plan_of(cov.tests)
    assert select_tests.fast_units(plan, cov, lean_fresh=True, budget=150.0) == [
        "tests/test_0.py", "tests/test_1.py", "tests/test_2.py"]
    assert select_tests.fast_units(plan, cov, lean_fresh=True, budget=149.0) == ["tests/test_0.py", "tests/test_1.py"]


def test_no_map_no_fast_units():
    assert select_tests.fast_units(plan_of(["tests/test_a.py"]), None, lean_fresh=True) == []


def test_a_lean_runner_waits_for_a_pending_lean_build():
    cov = coverage({"tests/test_service.py": 5.0, "tests/test_lake.py": 6.0, "tests/test_pure.py": 7.0},
                   programs={"lean/.lake/build/bin/ve_service": ["tests/test_service.py"],
                             "lake": ["tests/test_lake.py"], "git": ["tests/test_pure.py"]})
    pending = plan_of(cov.tests, lean_build=True)
    assert select_tests.fast_units(pending, cov, lean_fresh=False) == ["tests/test_pure.py"]
    assert select_tests.fast_units(pending, cov, lean_fresh=True) == [
        "tests/test_service.py", "tests/test_lake.py", "tests/test_pure.py"]
    # no Lean build in the plan: the checkout's build is the one the run uses
    assert select_tests.fast_units(plan_of(cov.tests), cov, lean_fresh=False) == [
        "tests/test_service.py", "tests/test_lake.py", "tests/test_pure.py"]


def test_a_rust_runner_waits_for_the_plans_cargo_build():
    cov = coverage({"tests/test_rust.py": 5.0, "tests/test_cargo.py": 6.0, "tests/test_pure.py": 7.0},
                   programs={"rust/target/release/ve": ["tests/test_rust.py"], "cargo": ["tests/test_cargo.py"]})
    assert select_tests.fast_units(plan_of(cov.tests, cargo=True), cov, lean_fresh=True) == ["tests/test_pure.py"]
    assert select_tests.fast_units(plan_of(cov.tests), cov, lean_fresh=True) == [
        "tests/test_rust.py", "tests/test_cargo.py", "tests/test_pure.py"]


def test_the_lean_build_is_done_only_when_every_lake_command_needs_no_build(monkeypatch):
    calls, codes = [], {"ve_bench": 1}

    def fake_run(command, **kwargs):
        calls.append((command, kwargs["cwd"]))
        return type("Done", (), {"returncode": codes.get(command[2], 0) if len(command) > 3 else 0})()
    monkeypatch.setattr(select_tests.subprocess, "run", fake_run)
    plan = plan_of([], lean_build=True)
    assert select_tests.lean_built(plan, {}) is True
    assert calls == [(["lake", "build", "--no-build"], select_tests.ROOT / "lean")]
    plan["commands"].insert(1, ["lake", "build", "ve_bench"])
    assert select_tests.lean_built(plan, {}) is False
    assert select_tests.lean_built(plan_of([]), {}) is True  # no Lean build named: nothing runs


def stage(monkeypatch, cov, plan, *, fresh, code=1):
    ran = []
    monkeypatch.delenv("VE_LEAN_PREBUILT", raising=False)  # a selected run that built Lean exports it to its units
    monkeypatch.setattr(select_tests, "resolve_map", lambda base, path: cov)
    monkeypatch.setattr(select_tests, "lean_built", lambda plan, env: fresh)
    monkeypatch.setattr(select_tests, "run_plain",
                        lambda command, plan, maxfail, env, held=None: ran.append((command, maxfail, env)) or code)
    return select_tests.fast_stage(plan, 5), ran


def test_the_stage_runs_one_pytest_process_of_the_fast_units_and_no_build(monkeypatch, capsys):
    cov = coverage({"tests/test_pin.py": 39.0, "tests/test_slow.py": 900.0, "tests/test_service.py": 3.0},
                   programs={"lean/.lake/build/bin/ve_service": ["tests/test_service.py"]})
    code, ran = stage(monkeypatch, cov, plan_of(cov.tests, lean_build=True), fresh=False)
    assert code == 1
    [(command, maxfail, env)] = ran
    assert command == [*select_tests.PYTEST, "-q", "tests/test_pin.py"] and maxfail == 5
    assert "VE_LEAN_PREBUILT" not in env
    assert "fast stage: 1 of 3 units, 39.0 s in the map" in capsys.readouterr().out


def test_a_done_lean_build_lets_its_runners_in(monkeypatch):
    cov = coverage({"tests/test_pin.py": 39.0, "tests/test_service.py": 3.0},
                   programs={"lean/.lake/build/bin/ve_service": ["tests/test_service.py"]})
    code, [(command, _, env)] = stage(monkeypatch, cov, plan_of(cov.tests, lean_build=True), fresh=True, code=0)
    assert code == 0 and command[len(select_tests.PYTEST):] == ["-q", "tests/test_service.py", "tests/test_pin.py"]
    assert env["VE_LEAN_PREBUILT"] == "1"


def test_no_fast_unit_runs_nothing(monkeypatch):
    cov = coverage({"tests/test_slow.py": 900.0})
    code, ran = stage(monkeypatch, cov, plan_of(cov.tests), fresh=True)
    assert code == select_tests.NO_TESTS_COLLECTED and ran == []


@pytest.mark.parametrize("extra", [[], ["--full"], ["--impacted"], ["--no-record"], ["--tier", "light"],
                                   ["--chunk-heavy"]])
def test_the_stage_takes_a_mapped_recorded_run(monkeypatch, capsys, extra):
    monkeypatch.setattr(sys, "argv", ["select_tests.py", "--paths", "README.md", "--fast-stage",
                                      *(["--run"] if extra else []), *extra])
    with pytest.raises(SystemExit) as stop:
        select_tests.main()
    assert stop.value.code == 2 and "--fast-stage takes --run" in capsys.readouterr().err
