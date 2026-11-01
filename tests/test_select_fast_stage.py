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


def test_each_lean_build_of_the_plan_is_checked_on_its_own(monkeypatch):
    calls, codes = [], {"ve_bench": 3}

    def fake_run(command, **kwargs):
        calls.append((command, kwargs["cwd"]))
        return type("Done", (), {"returncode": codes.get(command[2], 0) if len(command) > 3 else codes.get("", 0)})()
    monkeypatch.setattr(select_tests.subprocess, "run", fake_run)
    plan = plan_of([], lean_build=True)
    assert select_tests.lean_pending(plan, {}) == []
    assert calls == [(["lake", "build", "--no-build"], select_tests.ROOT / "lean")]
    calls.clear()
    plan["commands"].insert(1, ["lake", "build", "ve_bench", "ve_other"])
    plan["commands"].insert(2, ["lake", "build", "ve_bench"])
    assert select_tests.lean_pending(plan, {}) == ["ve_bench"]  # the bench alone, not every Lean build
    assert [command for command, _ in calls] == [["lake", "build", "--no-build"],
                                                 ["lake", "build", "ve_bench", "--no-build"],
                                                 ["lake", "build", "ve_other", "--no-build"]]
    codes[""] = 3
    assert select_tests.lean_pending(plan, {}) == [select_tests.DEFAULT_LEAN_BUILD, "ve_bench"]
    assert select_tests.lean_pending(plan_of([]), {}) == []  # no Lean build named: nothing runs


SERVICE, BENCH = "lean/.lake/build/bin/ve_service", "lean/.lake/build/bin/ve_bench"


@pytest.mark.parametrize("pending, fresh", [
    ([], {SERVICE, BENCH, "lake", "git"}),
    (["ve_bench"], {SERVICE, "git"}),  # F2: a pending bench holds back its own runners, and lake's
    ([select_tests.DEFAULT_LEAN_BUILD], {"git"}),
    ([select_tests.DEFAULT_LEAN_BUILD, "ve_bench"], {"git"})])
def test_a_lean_program_is_fresh_unless_its_own_build_is_pending(pending, fresh):
    is_fresh = select_tests.lean_fresh_program(pending)
    assert {name for name in (SERVICE, BENCH, "lake", "git") if is_fresh(name)} == fresh


@pytest.mark.parametrize("cargo, stale", [
    ([], set()),
    ([["build", "--locked", "--release"]], {"rust/target/release/ve", "cargo", "rust/other"}),
    ([["build", "--locked"]], {"rust/target/debug/ve", "cargo", "rust/other"}),
    ([["test", "--locked"]], {"rust/target/debug/ve", "cargo", "rust/other"}),
    ([["test"], ["build", "--release"]], {"rust/target/release/ve", "rust/target/debug/ve", "cargo", "rust/other"})])
def test_a_rust_program_is_stale_only_when_a_cargo_command_of_the_plan_remakes_it(cargo, stale):
    plan = plan_of([])
    plan["commands"][:0] = [[*select_tests.CARGO, *command] for command in cargo]
    is_stale = select_tests.rust_stale(plan)
    names = ("rust/target/release/ve", "rust/target/debug/ve", "cargo", "rust/other", "lake", "git")
    assert {name for name in names if is_stale(name)} == stale


@pytest.mark.parametrize("reasons, rank", [
    (["changed test"], 0), (["reads lean/VE/Calc/Units.lean"], 0), (["reads the whole manifest"], 0),
    (["smoke", "reads lean/A.lean"], 0), (["reads lean/A.lean (static)"], 2), (["lists the directory of lean/A.lean"], 2),
    (["smoke"], 2), (["runs Lean via lean/A.lean"], 1), (["tools/a.py:f"], 1), (["smoke", "runs Rust via rust/a.rs"], 1),
    ([], 1), (None, 1)])
def test_the_rank_puts_the_readers_of_the_change_first(reasons, rank):
    assert select_tests.fast_rank(reasons) == rank


def test_a_reader_of_the_change_is_never_crowded_out_by_cheaper_units():
    """F1 (review of 8f8ca0d98): cheapest first filled the budget with 2-15 s units, so the 58.2-s pin that reads
    the changed Lean file never ran early."""
    seconds = {f"tests/test_cheap_{i:02}.py": 5.0 for i in range(60)}
    seconds |= {"tests/test_pin.py": 58.2, "tests/test_ledger.py": 50.0, "tests/test_changed.py": 40.0,
                "tests/test_weak.py": 1.0, "tests/test_slow_reader.py": CHEAP + 1}
    cov = coverage(seconds)
    plan = plan_of(cov.tests)
    plan["reasons"] = {unit: ["runs Lean via lean/VE/Calc/Units.lean"] for unit in cov.tests}
    plan["reasons"] |= {"tests/test_pin.py": ["reads lean/VE/Calc/Units.lean"], "tests/test_weak.py": ["smoke"],
                        "tests/test_ledger.py": ["reads lean/VE/Calc/UnitsExamples.lean", "smoke"],
                        "tests/test_changed.py": ["changed test"], "tests/test_slow_reader.py": ["reads lean/A.lean"]}
    units = select_tests.fast_units(plan, cov, lean_fresh=True)
    assert units[:3] == ["tests/test_changed.py", "tests/test_ledger.py", "tests/test_pin.py"]
    # then the other strong reasons, cheapest first, to the budget; a weak one only after them; never a slow one
    assert units[3:] == [f"tests/test_cheap_{i:02}.py" for i in range(18)]
    # the readers alone over the budget: all of them still run, and nothing else
    assert select_tests.fast_units(plan, cov, lean_fresh=True, budget=100.0) == units[:3]


def test_a_weak_unit_comes_after_every_stronger_one():
    cov = coverage({"tests/test_weak.py": 1.0, "tests/test_runs.py": 9.0})
    plan = plan_of(cov.tests)
    plan["reasons"] = {"tests/test_weak.py": ["lists the directory of lean/A.lean"],
                       "tests/test_runs.py": ["runs Lean via lean/A.lean"]}
    assert select_tests.fast_units(plan, cov, lean_fresh=True) == ["tests/test_runs.py", "tests/test_weak.py"]
    assert select_tests.fast_units(plan, cov, lean_fresh=True, budget=9.5) == ["tests/test_runs.py"]


def stage(monkeypatch, cov, plan, *, pending=(), code=1, jobs=1):
    ran = []
    monkeypatch.delenv("VE_LEAN_PREBUILT", raising=False)  # a selected run that built Lean exports it to its units
    monkeypatch.setattr(select_tests, "resolve_map", lambda base, path: cov)
    monkeypatch.setattr(select_tests, "lean_pending", lambda plan, env: list(pending))
    monkeypatch.setattr(select_tests, "run_plain",
                        lambda command, plan, maxfail, env, held=None: ran.append((command, maxfail, env)) or code)
    return select_tests.fast_stage(plan, 5, jobs=jobs), ran


def test_a_pending_bench_keeps_the_service_runners_in_the_stage(monkeypatch, capsys):
    """F2 (review of 8f8ca0d98): one out-of-date bench target dropped every Lean runner, the pin test too."""
    cov = coverage({"tests/test_pin.py": 58.2, "tests/test_bench.py": 3.0, "tests/test_lake.py": 4.0},
                   programs={SERVICE: ["tests/test_pin.py"], BENCH: ["tests/test_bench.py"],
                             "lake": ["tests/test_lake.py"]})
    plan = plan_of(cov.tests, lean_build=True)
    plan["commands"].insert(1, ["lake", "build", "ve_bench"])
    code, [(command, _, env)] = stage(monkeypatch, cov, plan, pending=["ve_bench"], code=0)
    assert command[len(select_tests.PYTEST):] == ["-q", "tests/test_pin.py"]
    assert env["VE_LEAN_PREBUILT"] == "1"  # the default build is done: no unit builds Lean itself
    assert "Lean build pending: ve_bench" in capsys.readouterr().out


def test_the_stage_runs_on_up_to_jobs_workers(monkeypatch, capsys):
    cov = coverage({f"tests/test_{i}.py": 2.0 for i in range(3)})
    _, [(command, _, _)] = stage(monkeypatch, cov, plan_of(cov.tests), jobs=8)
    assert command[len(select_tests.PYTEST):] == ["-p", "xdist", "-n", "3", "-q", *cov.tests]
    out = capsys.readouterr().out
    assert "on 3 workers" in out and "Lean build none in the plan" in out  # C2: nothing checked, nothing claimed
    _, [(command, _, _)] = stage(monkeypatch, cov, plan_of(cov.tests[:1]), jobs=8)
    assert command == [*select_tests.PYTEST, "-q", cov.tests[0]]


def test_main_sends_the_fast_stage_its_jobs_and_builds_nothing(monkeypatch):
    """C1: `--fast-stage` goes to `fast_stage`, never to the full run, and skips the binary cutoff's Lean build."""
    import answer_cutoff
    plan = {**plan_of(["tests/test_a.py"], lean_build=True), "selected_count": 1, "full_count": 9, "full": False,
            "full_reasons": [], "seconds": 0.0, "reasons": {}, "map": {"commit": "0" * 40, "path": "map.json.gz"},
            "lean_cutoff": {"state": "no record of the head build", "same": None}}
    calls = []
    monkeypatch.setattr(answer_cutoff, "select", lambda *args, **kwargs: plan)
    monkeypatch.setattr(select_tests.test_map, "build_lean", lambda *args, **kwargs: calls.append("build"))
    monkeypatch.setattr(select_tests, "run", lambda *args, **kwargs: calls.append("run") or 0)
    monkeypatch.setattr(select_tests, "fast_stage",
                        lambda plan, maxfail, *, jobs: calls.append(("fast", maxfail, jobs)) or 0)
    monkeypatch.setattr(sys, "argv", ["select_tests.py", "--paths", "lean/A.lean", "--run", "--fast-stage",
                                      "--jobs", "6"])
    assert select_tests.main() == 0
    assert calls == [("fast", select_tests.MAXFAIL, 6)]


def test_the_stage_runs_one_pytest_process_of_the_fast_units_and_no_build(monkeypatch, capsys):
    cov = coverage({"tests/test_pin.py": 39.0, "tests/test_slow.py": 900.0, "tests/test_service.py": 3.0},
                   programs={"lean/.lake/build/bin/ve_service": ["tests/test_service.py"]})
    code, ran = stage(monkeypatch, cov, plan_of(cov.tests, lean_build=True),
                      pending=[select_tests.DEFAULT_LEAN_BUILD])
    assert code == 1
    [(command, maxfail, env)] = ran
    assert command == [*select_tests.PYTEST, "-q", "tests/test_pin.py"] and maxfail == 5
    assert "VE_LEAN_PREBUILT" not in env
    assert "fast stage: 1 of 3 units, 39.0 s in the map" in capsys.readouterr().out


def test_a_done_lean_build_lets_its_runners_in(monkeypatch):
    cov = coverage({"tests/test_pin.py": 39.0, "tests/test_service.py": 3.0},
                   programs={"lean/.lake/build/bin/ve_service": ["tests/test_service.py"]})
    code, [(command, _, env)] = stage(monkeypatch, cov, plan_of(cov.tests, lean_build=True), code=0)
    assert code == 0 and command[len(select_tests.PYTEST):] == ["-q", "tests/test_service.py", "tests/test_pin.py"]
    assert env["VE_LEAN_PREBUILT"] == "1"


def test_no_fast_unit_runs_nothing(monkeypatch):
    cov = coverage({"tests/test_slow.py": 900.0})
    code, ran = stage(monkeypatch, cov, plan_of(cov.tests))
    assert code == select_tests.NO_TESTS_COLLECTED and ran == []


@pytest.mark.parametrize("extra", [[], ["--full"], ["--impacted"], ["--no-record"], ["--tier", "light"],
                                   ["--chunk-heavy"]])
def test_the_stage_takes_a_mapped_recorded_run(monkeypatch, capsys, extra):
    monkeypatch.setattr(sys, "argv", ["select_tests.py", "--paths", "README.md", "--fast-stage",
                                      *(["--run"] if extra else []), *extra])
    with pytest.raises(SystemExit) as stop:
        select_tests.main()
    assert stop.value.code == 2 and "--fast-stage takes --run" in capsys.readouterr().err
