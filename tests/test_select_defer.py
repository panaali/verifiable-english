"""`select_tests --defer-heavy`: a builder run leaves the heavy test files that only weak reasons select
to the chain gate, and never records them as passed.

With `--defer-broad` it also leaves out the heavy broad Lean consumers that only weak and Lean reasons select.
Synthetic plans and maps, and the recorded plans in tests/data/select_defer/: each item's tip ran `select_tests.py
--base <base> --json` with that tip's code, trimmed to the selected units and their map seconds, and for the heavy
ones their reasons, their `lean_share` (this branch's `lean_shares` of the base's map and the tip's graph, frozen:
only the synthetic test runs `lean_shares`) and `names_change` (those whose source named a changed Lean module
then), so these tests read no other test's source. Nothing runs a test file and every write goes under tmp_path.
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
        "seconds": 600.0, "reasons": ["imports ve/a.py (static)", "lists the directory of ve/b.py"], "class": "weak"}}
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


# --- --defer-broad -------------------------------------------------------------------------------------------

FIVE = ("tests/test_trust_mutants.py", "tests/test_acts_vocab_mutants.py", "tests/test_english_evidence.py",
        "tests/test_readings_rd6b_differential.py", "tests/test_speech_polar_lean.py")
RECORDED = ROOT / "tests/data/select_defer"
BROAD = select_tests.BROAD_LEAN_SHARE


def test_lean_reasons_are_the_lean_trees_files_never_python_or_static():
    lean = ["reads lean/VE/Scope/Plain.lean", "reads lean/declarations.txt", "reads lean/statements.txt",
            "reads lean/predicates.txt", "reads lean/axioms.txt", "reads lean/checkers.lock",
            "reads lean/lakefile.toml", "runs Lean via lean/Main.lean",
            "runs Lean via lean/VE/Scope/Plain.lean", "runs service mode via lean/VE/Senses/Run.lean"]
    other = ["reads lean/audit.py", "runs Lean via lean/VE/A.lean (static)", "reads ve/a.py", "changed test",
             "reads lean/VE/Route/examples/route-cases.json", "reads lean/VE/Route/frozen-sources.sha256",
             "reads lean/README.md", "reads ve/data/x.lean.json", "lists the directory of lean/VE/A.lean",
             "lean/audit.py:code_only reads a changed name", "runs git, which reads .gitattributes", "smoke"]
    assert [reason for reason in lean + other if select_tests.lean_reason(reason)] == lean


class Graph:
    """A source graph with two executables: `small` holds A, `big` holds A, B and C."""
    def __init__(self, root: Path, unreadable=()):
        self.root, self.lean_unreadable = root, list(unreadable)
        self.lean_modules = {f"VE.{name}": f"lean/VE/{name}.lean" for name in "ABCD"}
        self.imports = {"Small": {"VE.A"}, "Big": {"VE.A", "VE.B", "VE.C"}}

    def lean_closure(self, module: str) -> set[str]:
        return {module, *self.imports.get(module, ())}


def test_a_units_lean_reach_is_what_it_reads_and_the_closures_of_what_it_runs(tmp_path):
    (tmp_path / "lean").mkdir()
    (tmp_path / "lean/lakefile.toml").write_text(
        '[[lean_exe]]\nname = "small"\nroot = "Small"\n[[lean_exe]]\nname = "big"\nroot = "Big"\n')
    data = {"tests": ["tests/test_reads.py", "tests/test_small.py", "tests/test_big.py", "tests/test_lake.py",
                      "tests/test_none.py"],
            "reads": {f"lean/VE/{name}.lean": [0] if name == "A" else [] for name in "ABCD"}
            | {"lean/declarations.txt": [0], "ve/a.py": [4]},
            "programs": {"lean/.lake/build/bin/small": [1], "lean/.lake/build/bin/big": [2], "lake": [3],
                         "git": [4]}}
    assert select_tests.lean_shares(data, Graph(tmp_path)) == {
        "tests/test_reads.py": 0.25, "tests/test_small.py": 0.25, "tests/test_big.py": 0.75, "tests/test_lake.py": 1.0}
    assert select_tests.lean_shares(data, Graph(tmp_path, ["lean/VE/D.lean"]))["tests/test_small.py"] == 1.0
    assert select_tests.lean_shares({"tests": [], "reads": {}, "programs": {}}, Graph(tmp_path)) == {}


def test_a_unit_names_a_changed_module_or_its_directory_never_a_sibling():
    changed = ["lean/VE/Scope/Authoring.lean"]
    named = ['"lean/VE/Scope/Authoring.lean"', "import VE.Scope.Authoring", 'ROOT / "lean/VE/Scope/"',
             '"lean/VE/Scope"']
    not_named = ['"lean/VE/Scope/Govern.lean"', "VE.Scope.AuthoringExamples", "VE.Scope.Govern", "lean/VE/Scope.lean",
                 "NVE/Scope/Authoring"]
    assert [text for text in named + not_named if select_tests.names_changed_lean(text, changed)] == named
    assert select_tests.names_changed_lean("lean/VE/Audit.lean", ["lean/VE/Audit.lean"])
    assert not select_tests.names_changed_lean('"lean/VE/"', ["lean/VE/Audit.lean"])  # lean/VE is no family
    assert select_tests.names_changed_lean('"lean/VE.lean"', ["lean/VE.lean"])
    assert not select_tests.names_changed_lean("VE.Scope", ["lean/VE.lean"])
    assert select_tests.names_changed_lean(select_tests.unit_text("tests/test_scope_lean.py"),
                                           ["lean/VE/Scope/Plain.lean"])


def broad_plan(**extra) -> tuple[dict, dict, dict]:
    reasons = {"tests/test_broad.py": ["runs Lean via lean/VE/A/X.lean", "imports ve/a.py (static)"],
               "tests/test_python.py": ["runs Lean via lean/VE/A/X.lean", "reads ve/a.py"],
               "tests/test_narrow.py": ["runs Lean via lean/VE/A/X.lean"],
               "tests/test_own.py": ["reads lean/VE/A/X.lean"],
               "tests/test_a_family.py": ["runs Lean via lean/VE/A/X.lean"],
               "tests/test_unshared.py": ["runs Lean via lean/VE/A/X.lean"],
               "tests/test_weak.py": ["imports ve/a.py (static)"], **extra}
    shares = {unit: 0.0 if unit == "tests/test_narrow.py" else 1.0 for unit in reasons if unit != "tests/test_unshared.py"}
    return plan_of(reasons, changed=["lean/VE/A/X.lean"]), dict.fromkeys(reasons, HEAVY), shares


def text_of(unit: str) -> str:
    return 'LEAN = "lean/VE/A/X.lean"' if unit == "tests/test_own.py" else ""


def test_with_shares_a_broad_lean_consumer_is_deferred_and_the_rest_stays():
    plan, seconds, shares = broad_plan()
    found = select_tests.defer_heavy(plan, seconds, shares=shares, text=text_of)
    assert found["deferred"] == {
        "tests/test_broad.py": {"seconds": HEAVY, "reasons": plan["reasons"]["tests/test_broad.py"],
                                "class": "broad", "lean_share": 1.0},
        "tests/test_weak.py": {"seconds": HEAVY, "reasons": ["imports ve/a.py (static)"], "class": "weak"}}
    assert found["selected"] == ["tests/test_a_family.py", "tests/test_narrow.py", "tests/test_own.py",
                                 "tests/test_python.py", "tests/test_unshared.py"]
    assert found["deferred_seconds"] == 2 * HEAVY
    assert list(select_tests.defer_heavy(plan, seconds, text=text_of)["deferred"]) == ["tests/test_weak.py"]
    # an unreadable map gives no shares: nothing is broad
    assert list(select_tests.defer_heavy(plan, seconds, shares={}, text=text_of)["deferred"]) == ["tests/test_weak.py"]


def test_a_test_of_a_changed_modules_family_is_named_for_it():
    changed = ["lean/VE/Scope/Authoring.lean", "lean/VE/RightClauses.lean", "docs/a.md", "lean/VE.lean"]
    family = ["tests/test_scope_answer.py", "tests/test_scope.py", "tests/test_b16_scope_lean.py",
              "tests/test_right_clauses_plain.py"]
    other = ["tests/test_scoped.py", "tests/test_telescope.py", "tests/test_right.py", "tests/test_clauses.py",
             "tests/test_ve.py", "tests/test_authoring.py"]
    assert [unit for unit in family + other if select_tests.family_test(unit, changed)] == family


def test_the_share_threshold_is_inclusive():
    plan, seconds, shares = broad_plan()
    at = {**shares, "tests/test_broad.py": BROAD}
    below = {**shares, "tests/test_broad.py": BROAD - 0.001}
    assert "tests/test_broad.py" in select_tests.defer_heavy(plan, seconds, shares=at, text=text_of)["deferred"]
    assert "tests/test_broad.py" not in select_tests.defer_heavy(plan, seconds, shares=below, text=text_of)["deferred"]


def recorded(item: str) -> tuple[dict, dict, dict, object]:
    """A recorded plan, its map seconds, its heavy units' Lean shares and their source text as recorded: a unit in
    `names_change` names a changed Lean module."""
    row = json.loads((RECORDED / f"{item}.json").read_text())
    reasons = {unit: row["reasons"].get(unit, ["(not recorded: under the threshold)"])
               for unit in row["selected"]}
    plan = {**plan_of(reasons, changed=row["changed"], full=row["full"]), "selected": row["selected"]}
    named, lean = set(row["names_change"]), [path for path in row["changed"] if path.endswith(".lean")]
    return plan, row["seconds"], row["lean_share"], lambda unit: lean[0] if unit in named else ""


# One-family Lean changes: cmp-s3a-cfr-2 (RightClauses) and sc-7 (Scope) run none of the ve_service users
# rd6b_differential and speech_polar_lean, so the plans recorded at their tips do not select those two; sn-b6d
# (Senses) selects all five.
ONE_FAMILY = {"cmp-s3a-cfr-2": FIVE[:3], "sc-7": FIVE[:3], "sn-b6d": FIVE}


@pytest.mark.parametrize("item", sorted(ONE_FAMILY))
def test_the_heavy_lean_wide_files_are_deferred_for_a_one_family_lean_change(item):
    plan, seconds, shares, text = recorded(item)
    assert set(FIVE) & set(plan["selected"]) == set(ONE_FAMILY[item])
    found = select_tests.defer_heavy(plan, seconds, shares=shares, text=text)
    assert {unit: found["deferred"].get(unit, {}).get("class") for unit in ONE_FAMILY[item]} == dict.fromkeys(
        ONE_FAMILY[item], "broad")
    assert not set(ONE_FAMILY[item]) & set(select_tests.defer_heavy(plan, seconds)["deferred"])  # no --defer-broad
    before = sum(seconds.get(unit, 0.0) for unit in plan["selected"])
    assert found["deferred_seconds"] > 0.4 * before  # about half the selected map seconds (REPORT)


@pytest.mark.parametrize("item", sorted(ONE_FAMILY))
@pytest.mark.parametrize("why", ["its source changed", "it failed last time"])
def test_each_heavy_lean_wide_file_stays_when_it_changed_or_failed(item, why):
    plan, seconds, shares, text = recorded(item)
    for unit in ONE_FAMILY[item]:
        changed = {**plan, "changed": [*plan["changed"], unit]} if why == "its source changed" else plan
        found = select_tests.defer_heavy(changed, seconds, shares=shares, text=text,
                                         keep={unit} if why == "it failed last time" else set())
        assert unit not in found["deferred"] and unit in found["selected"], (unit, why)


def test_a_familys_own_lean_test_and_a_python_reader_stay_in_the_recorded_sc_7_plan():
    """A test whose source names a changed module, one whose name makes it a test of a changed family, and one
    with a non-Lean reason stay; all three would be broad otherwise."""
    plan, seconds, shares, text = recorded("sc-7")
    found = select_tests.defer_heavy(plan, seconds, shares=shares, text=text)
    own = "tests/test_question_reading.py"  # its source names lean/VE/Audit.lean, which sc-7 changed
    assert shares[own] >= BROAD and all(select_tests.weak_reason(reason) or select_tests.lean_reason(reason)
                                        for reason in plan["reasons"][own])
    assert own not in found["deferred"]
    assert "tests/test_consolidation_tools.py" not in found["deferred"]  # reads docs/trust-baseline.json
    scope = "tests/test_scope_answer.py"  # a Scope test by its name; its source names VE/Scope/Run.lean only
    assert shares[scope] >= BROAD and text(scope) == "" and scope not in found["deferred"]
    assert all(select_tests.weak_reason(reason) or select_tests.lean_reason(reason)
               for reason in plan["reasons"][scope])


def test_each_recorded_plan_keeps_these_map_seconds():
    """The map seconds each recorded plan keeps: selected, under --defer-heavy, and with --defer-broad too.
    ps-2a changed Python (tools/lean_statements.py, lean/audit.py) and .gitattributes, so most of its heavy units
    stay for a non-Lean reason."""
    after = {}
    for item in ("cmp-s3a-cfr-2", "sc-7", "ps-2a", "sn-b6d"):
        plan, seconds, shares, text = recorded(item)
        before = sum(seconds.get(unit, 0.0) for unit in plan["selected"])
        heavy = select_tests.defer_heavy(plan, seconds)["deferred_seconds"]
        broad = select_tests.defer_heavy(plan, seconds, shares=shares, text=text)["deferred_seconds"]
        after[item] = (round(before), round(before - heavy), round(before - broad))
    assert after == {"cmp-s3a-cfr-2": (19915, 19915, 5835), "sc-7": (24080, 24080, 13407),
                     "ps-2a": (50868, 50712, 47814), "sn-b6d": (50047, 50047, 22076)}


def test_the_option_passes_the_maps_shares_and_marks_broad_files(monkeypatch, capsys):
    plan, seconds, shares = broad_plan()
    monkeypatch.setattr(select_tests, "map_lean_shares", lambda found: shares if found is plan else {})
    monkeypatch.setattr(select_tests, "unit_text", text_of)
    found = main_plan(monkeypatch, capsys, plan, seconds, {}, "--defer-heavy", "--defer-broad")
    assert {unit: row["class"] for unit, row in found["deferred"].items()} == {
        "tests/test_broad.py": "broad", "tests/test_weak.py": "weak"}
    assert list(main_plan(monkeypatch, capsys, plan, seconds, {}, "--defer-heavy")["deferred"]) == [
        "tests/test_weak.py"]
    plan.update(full_count=9, seconds=0.1, full_reasons=[])
    monkeypatch.setattr(sys, "argv", ["select_tests.py", "--paths", "lean/VE/A/X.lean", "--static",
                                      "--defer-heavy", "--defer-broad"])
    assert select_tests.main() == 0
    printed = capsys.readouterr().out
    assert "deferred to the chain gate: 2 test files" in printed and "broad Lean consumers (1)" in printed
    assert "tests/test_broad.py (broad), tests/test_weak.py" in printed


@pytest.mark.parametrize("other", [[], ["--defer-heavy", "--full"], ["--defer-heavy", "--impacted"],
                                   ["--defer-heavy", "--tier", "light"]])
def test_defer_broad_takes_defer_heavy_and_its_exclusions(monkeypatch, other):
    monkeypatch.setattr(sys, "argv", ["select_tests.py", "--paths", "ve/a.py", "--defer-broad", *other])
    with pytest.raises(SystemExit) as stopped:
        select_tests.main()
    assert stopped.value.code == 2
