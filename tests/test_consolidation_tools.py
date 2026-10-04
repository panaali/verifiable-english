"""Step 0 of docs/CONSOLIDATION-PLAN.md: the trust budget (TB), the statement dump (ST) and the Lean
output differential (OUT), with the input recorder OUT replays."""

import base64
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lean_output_diff  # noqa: E402
import lean_statements  # noqa: E402
import trust_map  # noqa: E402

FIXTURE = '''import VE.Syntax

/-! Module comment. -/

namespace VE.Demo
open VE

/-- A decoder. -/
def decodeThing (s : String) : Nat :=
  s.length

@[simp]
theorem decodeThing_empty : decodeThing "" = 0 := rfl

instance : Inhabited Nat where
  default := 0

structure Meaning where
  x : Nat

section
def helper : Nat := 1
end

example : helper = 1 := rfl

#guard helper == 1

end VE.Demo
'''


def write_tree(root: Path, table: dict, statements: str = "", predicates: tuple[str, ...] = ()) -> None:
    (root / "lean/VE").mkdir(parents=True, exist_ok=True)
    (root / "lean/VE/Demo.lean").write_text(FIXTURE)
    (root / "tools").mkdir(exist_ok=True)
    (root / "tools/trust-classes.json").write_text(json.dumps({"modules": {"VE/Demo.lean": table}}))
    (root / "lean/statements.txt").write_text(statements)
    (root / "lean/predicates.txt").write_text("-- header\n" + "".join(f"{p}\n" for p in predicates))


def test_scan_spans_names_and_kinds(tmp_path):
    path = tmp_path / "Demo.lean"
    try:
        path.write_text(FIXTURE)
        decls, total = trust_map.scan(path)
    finally:
        path.unlink()
    assert total == len(FIXTURE.splitlines())
    rows = [(d.kind, d.name, d.start, d.end) for d in decls]
    assert rows == [
        ("def", "VE.Demo.decodeThing", 8, 11),          # docstring through the blank line
        ("theorem", "VE.Demo.decodeThing_empty", 12, 14),  # the attribute line starts it
        ("instance", "instance:Inhabited Nat", 15, 17),
        ("structure", "VE.Demo.Meaning", 18, 20),
        ("def", "VE.Demo.helper", 22, 22),               # `section` and `end` are boundaries
        ("example", None, 25, 26),
        ("command", None, 27, 28),
    ]


def test_classes_counts_and_unclassified_fail_closed(tmp_path):
    write_tree(tmp_path, {"D[V]": ["VE.Demo.decodeThing"], "S": ["VE.Demo.Meaning"], "C": ["instance:Inhabited Nat"]})
    files, problems = trust_map.measure(tmp_path, tmp_path / "tools/trust-classes.json",
                                        tmp_path / "lean/statements.txt")
    assert problems == []
    counts = files["VE/Demo.lean"]
    assert (counts["D"], counts["D[V]"], counts["S"], counts["C"], counts["P"], counts["T"]) == (4, 4, 3, 3, 3, 4)
    # `helper` is in no table entry: counted as unclassified and trusted.
    assert counts["unclassified"] == 1
    assert counts["trusted"] == 4 + 3 + 1
    assert sum(counts[c] for c in trust_map.COLUMNS) + counts["unclassified"] == counts["lines"]


def tie_problems(root: Path, table: dict, dump: str, predicates: tuple[str, ...] = ()) -> tuple[dict, list[str]]:
    write_tree(root, table, dump, predicates)
    return trust_map.measure(root, root / "tools/trust-classes.json", root / "lean/statements.txt")


def entry(statement: str, uses: str) -> str:
    return f"theorem VE.Demo.decodeThing_empty\n  {statement}\n  -- uses {uses}\n  -- expr 1\n"


TIED = {"D[V]": [{"name": "VE.Demo.decodeThing", "tied": ["VE.Demo.decodeThing_empty"]}], "S": ["VE.Demo.Meaning"]}


def test_ties_are_checked_against_the_statement_dump(tmp_path):
    files, problems = tie_problems(tmp_path, TIED, entry('VE.Demo.decodeThing "" = (VE.Demo.Meaning.x ⟨0⟩)',
                                                         "VE.Demo.Meaning VE.Demo.Meaning.x VE.Demo.decodeThing"))
    assert problems == [] and files["VE/Demo.lean"]["tied"] == 4
    assert files["VE/Demo.lean"]["trusted"] == 7  # the unclassified helper and instance, and Meaning only
    _, problems = tie_problems(tmp_path, TIED, entry("True", "VE.Demo.Meaning"))
    assert problems and "does not mention VE.Demo.decodeThing" in problems[0]
    _, problems = tie_problems(tmp_path, {"D[V]": ["VE.Demo.gone"]}, "")
    assert any("VE.Demo.gone is not a declaration" in p for p in problems)


def test_tie_needs_the_qualified_declaration(tmp_path):
    """Review B: a statement about another namespace's `decodeThing` passed the short-name match."""
    _, problems = tie_problems(tmp_path, TIED, entry('VE.Other.decodeThing "" = 0 ∧ VE.Demo.Meaning = VE.Demo.Meaning',
                                                     "VE.Demo.Meaning VE.Other.decodeThing"))
    assert len(problems) == 1 and "does not mention VE.Demo.decodeThing" in problems[0]
    # Dot notation hides the namespace in the text; the uses line still names the declaration.
    files, problems = tie_problems(tmp_path, TIED, entry("∀ (m : VE.Demo.Meaning), m.decodeThing = 0",
                                                         "VE.Demo.Meaning VE.Demo.decodeThing"))
    assert problems == [] and files["VE/Demo.lean"]["tied"] == 4
    # A dump written before the uses line existed ties nothing.
    _, problems = tie_problems(tmp_path, TIED, "theorem VE.Demo.decodeThing_empty\n  VE.Demo.decodeThing \"\" = 0\n"
                                               "  -- expr 1\n")
    assert len(problems) == 1 and "has no uses line" in problems[0]


def test_tie_needs_a_trusted_meaning(tmp_path):
    """A theorem that mentions only the declaration (or only untrusted code) ties it to nothing."""
    _, problems = tie_problems(tmp_path, TIED, entry('VE.Demo.decodeThing "" = 0', "VE.Demo.decodeThing"))
    assert len(problems) == 1 and "mentions no K, S or untied [V]" in problems[0]
    checked = {**TIED, "S": [], "C": ["VE.Demo.Meaning"]}
    _, problems = tie_problems(tmp_path, checked, entry("…", "VE.Demo.Meaning VE.Demo.decodeThing"))
    assert len(problems) == 1 and "mentions no K, S or untied [V]" in problems[0]
    # Two declarations tied to each other leave nothing trusted.
    mutual = {"D[V]": [{"name": "VE.Demo.decodeThing", "tied": ["VE.Demo.decodeThing_empty"]},
                       {"name": "VE.Demo.helper", "tied": ["VE.Demo.decodeThing_empty"]}]}
    _, problems = tie_problems(tmp_path, mutual, entry("…", "VE.Demo.decodeThing VE.Demo.helper"))
    assert len(problems) == 2 and all("mentions no K, S or untied [V]" in p for p in problems)


@pytest.mark.parametrize("tie", [
    {"name": "VE.Demo.decodeThing", "tied": []},                    # review B: an empty list tied it
    {"name": "VE.Demo.decodeThing", "tied": "VE.Demo.decodeThing_empty"},
    {"name": "VE.Demo.decodeThing", "tied": [""]},
    {"name": "VE.Demo.decodeThing"},
    {"name": "VE.Demo.decodeThing", "tied": ["VE.Demo.decodeThing_empty"], "note": "x"},
    {"name": 3, "tied": ["VE.Demo.decodeThing_empty"]},
])
def test_malformed_ties_are_rejected(tmp_path, tie):
    with pytest.raises(ValueError, match="a tie must be"):
        tie_problems(tmp_path, {"D[V]": [tie], "S": ["VE.Demo.Meaning"]}, entry("…", "VE.Demo.Meaning VE.Demo.decodeThing"))


def test_unnamed_declaration_cannot_be_tied(tmp_path):
    table = {"D[V]": [{"name": "instance:Inhabited Nat", "tied": ["VE.Demo.decodeThing_empty"]}],
             "S": ["VE.Demo.Meaning"]}
    _, problems = tie_problems(tmp_path, table, entry("…", "VE.Demo.Meaning instance:Inhabited Nat"))
    assert any("an unnamed declaration cannot be tied" in p for p in problems)


@pytest.mark.parametrize("cls,ok", [("K", True), ("S", True), ("P", True), ("T", True), ("D[V]", True),
                                    ("G[V]", True), ("C", False), ("D[R]", False), ("G[I]", False)])
def test_predicate_is_never_untrusted_unread(tmp_path, cls, ok):
    """Review B: `Closure.Formula.WellFormed`, the kernel typing predicate, was C and left the budget."""
    write_tree(tmp_path, {cls: ["VE.Demo.helper"], "S": ["VE.Demo.Meaning"]}, predicates=("VE.Demo.helper",))
    files, problems = trust_map.measure(tmp_path, tmp_path / "tools/trust-classes.json",
                                        tmp_path / "lean/statements.txt")
    assert (problems == []) is ok
    if not ok:
        assert "VE.Demo.helper: a predicate cannot be" in problems[0]


def test_predicate_leaves_the_budget_only_through_a_tie(tmp_path):
    table = {"C": [{"name": "VE.Demo.helper", "tied": ["VE.Demo.decodeThing_empty"]}], "S": ["VE.Demo.Meaning"]}
    helper = ("VE.Demo.helper",)
    files, problems = tie_problems(tmp_path, table, entry("…", "VE.Demo.Meaning VE.Demo.helper"), helper)
    assert problems == [] and files["VE/Demo.lean"]["tied"] == 1 and files["VE/Demo.lean"]["C"] == 1
    _, problems = tie_problems(tmp_path, table, entry("…", "VE.Demo.helper"), helper)
    assert len(problems) == 1 and "mentions no K, S or untied [V]" in problems[0]


def test_missing_predicate_list_fails_closed(tmp_path):
    write_tree(tmp_path, {"S": ["VE.Demo.Meaning"]})
    (tmp_path / "lean/predicates.txt").unlink()
    _, problems = trust_map.measure(tmp_path, tmp_path / "tools/trust-classes.json", tmp_path / "lean/statements.txt")
    assert problems == ["predicates.txt is missing; run tools/lean_statements.py"]


def test_seed_puts_predicates_and_kernel_types_in_the_meaning():
    decls = [trust_map.Decl("VE.Closure.Edge", "inductive", 2, 3), trust_map.Decl("VE.Closure.Formula.WellFormed", "def", 4, 5),
             trust_map.Decl("VE.Closure.Formula.check", "def", 6, 7)]
    row = {"K": 4, "C": 3, "P": 0, "T": 0}
    predicates = {"VE.Closure.Formula.WellFormed"}
    # Before the fix the row's room decided, and WellFormed and Edge were C (review B).
    kept = {"VE.Closure.Edge": "C", "VE.Closure.Formula.WellFormed": "C", "VE.Closure.Formula.check": "C"}
    assert trust_map.seed_module("VE/Closure/Syntax.lean", decls, row, predicates, kept) == {
        "VE.Closure.Edge": "K", "VE.Closure.Formula.WellFormed": "K", "VE.Closure.Formula.check": "C"}
    assert trust_map.seed_module("VE/Closure/Syntax.lean", decls, row, predicates)["VE.Closure.Formula.WellFormed"] == "K"
    # Outside the kernel a predicate is S where the row has S, a proof helper where it has only C and P.
    assert trust_map.seed_module("VE/Norms/X.lean", decls[1:2], {"S": 5, "C": 5}, predicates)[decls[1].name] == "S"
    assert trust_map.seed_module("VE/Tableau.lean", decls[1:2], {"C": 5, "P": 9}, predicates)[decls[1].name] == "P"
    assert trust_map.seed_module("VE/New.lean", decls[1:2], None, predicates)[decls[1].name] == "S"
    # Reviewed classes and ties stay.
    tie = {"class": "C", "tied": ["VE.Closure.wf_iff"]}
    kept = {"VE.Closure.Formula.WellFormed": tie, "VE.Closure.Formula.check": "G[V]"}
    seeded = trust_map.seed_module("VE/Closure/Syntax.lean", decls, row, predicates, kept)
    assert seeded["VE.Closure.Formula.WellFormed"] == tie and seeded["VE.Closure.Formula.check"] == "G[V]"


def test_rebaseline_needs_a_reason_for_growth(tmp_path):
    write_tree(tmp_path, {"D[R]": ["VE.Demo.decodeThing"], "S": ["VE.Demo.Meaning", "VE.Demo.helper"],
                          "C": ["instance:Inhabited Nat"]})
    tables = (tmp_path / "tools/trust-classes.json", tmp_path / "lean/statements.txt")
    baseline_path = tmp_path / "baseline.json"
    trust_map.write_baseline(trust_map.measure(tmp_path, *tables)[0], baseline_path, {})
    write_tree(tmp_path, {"K": ["VE.Demo.decodeThing"], "S": ["VE.Demo.Meaning", "VE.Demo.helper"],
                          "C": ["instance:Inhabited Nat"]})
    grown, _ = trust_map.measure(tmp_path, *tables)
    with pytest.raises(ValueError, match="K grew from 0 to 4"):
        trust_map.write_baseline(grown, baseline_path)
    trust_map.write_baseline(grown, baseline_path, reason="reclassified decodeThing")
    history = json.loads(baseline_path.read_text())["history"]
    assert history[-1]["change"] == "reclassified decodeThing" and history[-1]["to"]["K"] == 4


def test_committed_kernel_meaning_is_trusted():
    """The kernel's typing predicates and syntax are K in every copy of the logic."""
    table = trust_map.load_table()
    for logic, module in (("VE", "VE/Syntax.lean"), ("VE.Closure", "VE/Closure/Syntax.lean"),
                          ("VE.Core", "VE/Core/Syntax.lean"), ("VE.Order", "VE/Order/Syntax.lean")):
        assert table[module][f"{logic}.Formula.WellFormed"] == "K"
        assert table[module][f"{logic}.Formula"] == "K"
    predicates = trust_map.lean_predicates()
    assert "VE.Closure.Formula.WellFormed" in predicates


def test_ledger_credits_each_declaration_once(tmp_path):
    write_tree(tmp_path, {"S": ["VE.Demo.Meaning"], "G[V]": ["VE.Demo.helper"], "D[R]": ["VE.Demo.decodeThing"],
                          "C": ["instance:Inhabited Nat"]})
    path = tmp_path / "ledger.json"
    path.write_text(json.dumps({"steps": [
        {"step": "a", "title": "", "days": 1, "risk": 2, "adds_est": 1,
         "tied": [{"module": "VE/{Demo,Gone}.lean", "names": r"\.(Meaning|decodeThing)$"}]},
        {"step": "b", "title": "", "days": 1, "risk": 1,
         "removed": [{"module": "VE/*.lean"}], "reclassified": [{"module": "VE/Demo.lean", "names": "nothing"}]}]}))
    rows, problems = trust_map.ledger(tmp_path, path, tmp_path / "tools/trust-classes.json",
                                      tmp_path / "lean/statements.txt")
    a, b = rows
    assert (a["tied"], a["tied_untrusted"], a["net"], a["score"]) == (3, 4, 2, 1.0)  # Meaning trusted, decodeThing [R]
    # Step b names the whole file again: Meaning and decodeThing are not credited twice.
    assert (b["removed"], b["removed_untrusted"]) == (1, 3)  # helper; the instance is C
    assert problems == ["ledger.json: step b reclassified: {'module': 'VE/Demo.lean', 'names': 'nothing'} "
                        "names no declaration"]


# Every kind of validation problem `walk` reports, as (table, statement dump, predicates, drop the
# predicate list). Review B (looprecheck 1): `--ledger` discarded these and exited 0.
PROBLEM_TREES = {
    "predicate classed C": ({"C": ["VE.Demo.helper"], "S": ["VE.Demo.Meaning"]}, "", ("VE.Demo.helper",), False),
    "predicate classed D[R]": ({"D[R]": ["VE.Demo.helper"], "S": ["VE.Demo.Meaning"]}, "", ("VE.Demo.helper",), False),
    "tie not mentioned": (TIED, entry("True", "VE.Demo.Meaning"), (), False),
    "tie to nothing trusted": (TIED, entry("…", "VE.Demo.decodeThing"), (), False),
    "tying theorem missing": (TIED, "", (), False),
    "unnamed tie": ({"D[V]": [{"name": "instance:Inhabited Nat", "tied": ["VE.Demo.decodeThing_empty"]}],
                     "S": ["VE.Demo.Meaning"]}, entry("…", "VE.Demo.Meaning instance:Inhabited Nat"), (), False),
    "stale table entry": ({"D[V]": ["VE.Demo.gone"], "S": ["VE.Demo.Meaning"]}, "", (), False),
    "predicate list missing": ({"S": ["VE.Demo.Meaning"]}, "", (), True),
    # Review B (looprecheck 2): a theorem listed as S anchored the tie, while the budget counted it P.
    "theorem listed as S anchors a tie": ({"S": ["VE.Demo.decodeThing_empty"], **{"D[V]": TIED["D[V]"]}},
                                          entry("…", "VE.Demo.decodeThing VE.Demo.decodeThing_empty"), (), False),
    "theorem listed as P": ({"P": ["VE.Demo.decodeThing_empty"], "S": ["VE.Demo.Meaning"]}, "", (), False),
    "theorem listed tied": ({"C": [{"name": "VE.Demo.decodeThing_empty", "tied": ["VE.Demo.decodeThing_empty"]}],
                             "S": ["VE.Demo.Meaning"]}, entry("…", "VE.Demo.Meaning VE.Demo.decodeThing_empty"), (), False),
    "anchor listed for another file": ({"D[V]": TIED["D[V]"]}, entry("…", "VE.Demo.Meaning VE.Demo.decodeThing"),
                                       (), False, {"VE/Other.lean": {"S": ["VE.Demo.Meaning"]}}),
    "anchor only unclassified": ({"D[V]": TIED["D[V]"]}, entry("…", "VE.Demo.helper VE.Demo.decodeThing"), (), False),
}
VALID_TREES = {
    "tied": (TIED, entry("…", "VE.Demo.Meaning VE.Demo.decodeThing"), (), False),
    "unclassified": ({"S": ["VE.Demo.Meaning"]}, "", (), False),
    "predicate tied": ({"C": [{"name": "VE.Demo.helper", "tied": ["VE.Demo.decodeThing_empty"]}], "S": ["VE.Demo.Meaning"]},
                       entry("…", "VE.Demo.Meaning VE.Demo.helper"), ("VE.Demo.helper",), False),
}
WHOLE_TREE = {"steps": [{"step": "all", "title": "", "days": 1, "risk": 1, "removed": [{"module": "VE/*"}]}]}


def problem_tree(root: Path, tree: tuple) -> None:
    table, dump, predicates, drop, *other = tree
    write_tree(root, table, dump, predicates)
    if other:
        path = root / "tools/trust-classes.json"
        path.write_text(json.dumps({"modules": {**json.loads(path.read_text())["modules"], **other[0]}}))
    if drop:
        (root / "lean/predicates.txt").unlink()
    (root / "tools/consolidation-ledger.json").write_text(json.dumps(WHOLE_TREE))


@pytest.mark.parametrize("name", [*PROBLEM_TREES, *VALID_TREES])
def test_ledger_and_measure_share_validation_and_trust(tmp_path, name):
    """One pass (`walk`) and one trust rule: the ledger reports every problem `measure` reports, and
    a step naming the whole tree credits exactly the trusted lines `measure` counts (a declaration
    whose class fails validation is trusted, failing closed)."""
    problem_tree(tmp_path, {**PROBLEM_TREES, **VALID_TREES}[name])
    tables = (tmp_path / "tools/trust-classes.json", tmp_path / "lean/statements.txt")
    files, measured = trust_map.measure(tmp_path, *tables)
    (row,), problems = trust_map.ledger(tmp_path, tmp_path / "tools/consolidation-ledger.json", *tables)
    assert problems == measured and (problems != []) is (name in PROBLEM_TREES)
    assert row["removed"] == files["VE/Demo.lean"]["trusted"]


@pytest.mark.parametrize("name", PROBLEM_TREES)
@pytest.mark.parametrize("flags", [[], ["--check"], ["--write"], ["--ledger"]])
def test_no_entry_point_succeeds_on_a_validation_problem(tmp_path, capsys, name, flags):
    problem_tree(tmp_path, PROBLEM_TREES[name])
    baseline = tmp_path / "docs/trust-baseline.json"
    assert trust_map.main([*flags, "--root", str(tmp_path)]) == 1
    assert not baseline.exists()
    out, err = capsys.readouterr()
    assert err.strip()
    if flags == ["--ledger"]:
        assert "| Step |" not in out and "the ledger is not reported" in err


def test_ledger_rejects_a_misclassified_kernel_predicate(tmp_path, capsys):
    """Review B (looprecheck 1): with the committed `Closure/Syntax.lean`, `Formula.WellFormed`
    classed C passed `--ledger` with zero trusted lines and exit 0."""
    (tmp_path / "lean/VE/Closure").mkdir(parents=True)
    shutil.copy(ROOT / "lean/VE/Closure/Syntax.lean", tmp_path / "lean/VE/Closure/Syntax.lean")
    module = "VE/Closure/Syntax.lean"
    table = {name: "K" for name in trust_map.load_table()[module]}
    table["VE.Closure.Formula.WellFormed"] = "C"
    by_class: dict[str, list] = {}
    for name, cls in table.items():
        by_class.setdefault(cls, []).append(name)
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools/trust-classes.json").write_text(json.dumps({"modules": {module: by_class}}))
    (tmp_path / "lean/statements.txt").write_text("")
    (tmp_path / "lean/predicates.txt").write_text("-- header\nVE.Closure.Formula.WellFormed\n")
    (tmp_path / "tools/consolidation-ledger.json").write_text(json.dumps({"steps": [
        {"step": "1", "title": "", "days": 1, "risk": 1,
         "removed": [{"module": module, "names": r"\.Formula\.WellFormed$"}]}]}))
    (row,), problems = trust_map.ledger(tmp_path, tmp_path / "tools/consolidation-ledger.json",
                                        tmp_path / "tools/trust-classes.json", tmp_path / "lean/statements.txt")
    assert len(problems) == 1 and "VE.Closure.Formula.WellFormed: a predicate cannot be C" in problems[0]
    assert row["removed"] > 0 and row["removed_untrusted"] == 0
    assert trust_map.main(["--ledger", "--root", str(tmp_path)]) == 1
    assert "a predicate cannot be C" in capsys.readouterr().err


MARKER = '''import VE.Demo

namespace VE.Demo

theorem marker : True := trivial

theorem decodeThing_tie : decodeThing "" = 0 ∧ marker = True.intro := ⟨rfl, rfl⟩

end VE.Demo
'''


@pytest.mark.parametrize("flags", [[], ["--check"], ["--write"], ["--ledger"]])
def test_theorem_listed_as_meaning_anchors_nothing(tmp_path, capsys, flags):
    """Review B (looprecheck 2): `theorem marker : True` listed as S anchored the tie of a D[V]
    decoder through `decodeThing "" = 0 ∧ marker = True.intro`, while the budget counted the
    theorem P. Every entry point succeeded with zero trusted lines, and `--check` passed decoder
    growth against a zero budget."""
    write_tree(tmp_path, {"D[V]": [{"name": "VE.Demo.decodeThing", "tied": ["VE.Demo.decodeThing_tie"]}],
                          "C": ["VE.Demo.Meaning", "VE.Demo.helper", "instance:Inhabited Nat"]},
               "theorem VE.Demo.decodeThing_tie\n  VE.Demo.decodeThing \"\" = 0 ∧ VE.Demo.marker = True.intro\n"
               "  -- uses And Eq Nat String True True.intro VE.Demo.decodeThing VE.Demo.marker\n  -- expr 1\n")
    (tmp_path / "lean/VE/Marker.lean").write_text(MARKER)
    table_path = tmp_path / "tools/trust-classes.json"
    modules = json.loads(table_path.read_text())["modules"]
    table_path.write_text(json.dumps({"modules": {**modules, "VE/Marker.lean": {"S": ["VE.Demo.marker"]}}}))
    (tmp_path / "tools/consolidation-ledger.json").write_text(json.dumps(WHOLE_TREE))
    (tmp_path / "docs").mkdir()
    zero = {"totals": trust_map.empty_counts(), "files": {}, "signed": []}
    (tmp_path / "docs/trust-baseline.json").write_text(json.dumps(zero))
    files, problems = trust_map.measure(tmp_path, table_path, tmp_path / "lean/statements.txt")
    assert sorted(problems) == [
        "VE/Demo.lean: VE.Demo.decodeThing: the statement of VE.Demo.decodeThing_tie mentions no K, S or untied [V] "
        "declaration of the tree, validly classified, to tie it to",
        "VE/Marker.lean: VE.Demo.marker: a theorem is P by its kind; the table cannot list it (it lists S)"]
    assert files["VE/Demo.lean"]["trusted"] == 4 and files["VE/Marker.lean"]["trusted"] == 2  # failing closed
    assert trust_map.check(files, zero)  # the decoder's lines are budget growth
    assert trust_map.main([*flags, "--root", str(tmp_path)]) == 1
    out, err = capsys.readouterr()
    assert "a theorem is P by its kind" in err and "PASS" not in out and "| Step |" not in out
    assert json.loads((tmp_path / "docs/trust-baseline.json").read_text()) == zero


# Generated mutation tests: each table entry's class (and each unlisted declaration's) is replaced,
# and the tool must either report a problem or report exactly what the declarations support.

KIND_FIXED = {"theorem": "P", "lemma": "P", "example": "T", "command": "T"}


def unsound(walked: list, table: dict, proved: dict, predicates: set[str]) -> list[str]:
    """What a report claims that the declarations contradict. This oracle reads only the reported
    classes, each declaration's kind and the statement dump, not the tool's anchor set: a theorem,
    example or command is P or T by its kind and cannot be listed; every other declaration is
    reported in its listed class (or `?`); `trusted` is K, S, `?` or untied [V]; each tying theorem
    mentions the declaration and another one the same report counts as trusted by its class; a
    predicate is not left untrusted untied."""
    reported = {d.decl.name: d for d in walked if d.decl.name is not None}
    errors = []
    for d in walked:
        name = d.decl.name
        listed = table.get(d.module, {}).get(name) if name is not None else None
        cls = listed if listed is None or isinstance(listed, str) else listed["class"]
        fixed = KIND_FIXED.get(d.decl.kind)
        if fixed and (d.cls != fixed or listed is not None):
            errors.append(f"{name}: a {d.decl.kind} reported {d.cls} and listed {cls}")
        elif not fixed and d.cls != (cls or "?"):
            errors.append(f"{name}: listed {cls}, reported {d.cls}")
        counted = d.cls in {"K", "S", "?"} or d.cls[0] in "DG" and d.cls.endswith("[V]") and not d.tied
        if d.trusted != counted:
            errors.append(f"{name}: {d.cls} reported trusted={d.trusted}")
        if d.tied:
            for theorem in listed["tied"]:
                used = proved.get(theorem) or set()
                if name not in used or not any(
                        n != name and n in reported and reported[n].trusted and not reported[n].tied
                        and reported[n].cls != "?" for n in used):
                    errors.append(f"{name}: {theorem} ties it to nothing the report counts as trusted")
        if name in predicates and not (counted or d.tied or d.cls in {"P", "T"}):
            errors.append(f"{name}: a predicate reported {d.cls} untied")
    return errors


def entry_variants(cls_now: object, theorems: list[str]) -> list[object]:
    """Every class, untied and tied to each theorem of the dump (or to the entry's own theorems),
    and no entry at all."""
    own = [cls_now["tied"]] if isinstance(cls_now, dict) else []
    ties = own + [[t] for t in theorems if [t] not in own]
    return [None, *trust_map.CLASSES, *({"class": c, "tied": t} for c in trust_map.CLASSES for t in ties)]


def mutate(table: dict, module: str, name: str, variant: object) -> dict:
    out = {m: dict(entries) for m, entries in table.items()}
    out.setdefault(module, {}).pop(name, None)
    if variant is not None:
        out[module][name] = variant
    return out


def assert_sound_or_rejected(decls, table, proved, predicates, label) -> None:
    walked, problems = trust_map.classify_tree(decls, table, proved, predicates)
    errors = unsound(walked, table, proved, predicates)
    assert problems or not errors, f"{label}: passed while {errors}"


@pytest.mark.parametrize("name", VALID_TREES)
def test_mutated_fixture_classes_are_reported_or_rejected(tmp_path, name):
    """Every named declaration of a valid fixture tree, alone and in pairs, takes every class
    (untied and tied) or none."""
    problem_tree(tmp_path, VALID_TREES[name])
    decls, _ = trust_map.scan_tree(tmp_path)
    table = trust_map.load_table(tmp_path / "tools/trust-classes.json")
    proved = trust_map.statements(tmp_path / "lean/statements.txt")
    predicates = trust_map.lean_predicates(tmp_path / "lean/predicates.txt")
    assert not unsound(*trust_map.classify_tree(decls, table, proved, predicates)[:1], table, proved, predicates)
    targets = sorted({(m, d.name) for m, d in decls if d.name is not None})
    variants = {t: entry_variants(table.get(t[0], {}).get(t[1]), sorted(proved)) for t in targets}
    for i, (module, decl) in enumerate(targets):
        for variant in variants[module, decl]:
            once = mutate(table, module, decl, variant)
            assert_sound_or_rejected(decls, once, proved, predicates, f"{decl}={variant}")
            for module2, decl2 in targets[i + 1:]:
                for variant2 in variants[module2, decl2]:
                    assert_sound_or_rejected(decls, mutate(once, module2, decl2, variant2), proved, predicates,
                                             f"{decl}={variant}, {decl2}={variant2}")


@pytest.fixture(scope="module")
def committed_tree():
    decls, _ = trust_map.scan_tree()
    return decls, trust_map.load_table(), trust_map.statements(), trust_map.lean_predicates()


def test_mutated_committed_ties_are_reported_or_rejected(committed_tree):
    """Every committed tie and every declaration its theorems mention (its possible anchors) takes
    every class, untied and tied, or none, against the committed dump and the files they live in
    (with those files' table entries, so the sub-tree is itself a valid tree)."""
    decls, table, proved, predicates = committed_tree
    walked, problems = trust_map.classify_tree(decls, table, proved, predicates)
    assert problems == [] and not unsound(walked, table, proved, predicates)
    modules = {d.name: m for m, d in decls if d.name is not None}
    tying = sorted({t for entries in table.values() for e in entries.values() if isinstance(e, dict) for t in e["tied"]})
    targets = sorted({(m, n) for m, entries in table.items() for n, e in entries.items() if isinstance(e, dict)}
                     | {(modules[n], n) for t in tying for n in proved[t] if n in modules})
    assert len(targets) > len(tying)
    files = {m for m, _ in targets}
    decls = [(m, d) for m, d in decls if m in files]
    table = {m: entries for m, entries in table.items() if m in files}
    walked, problems = trust_map.classify_tree(decls, table, proved, predicates)
    assert problems == [] and not unsound(walked, table, proved, predicates)
    for module, name in targets:
        for variant in entry_variants(table.get(module, {}).get(name), tying[:1]):
            assert_sound_or_rejected(decls, mutate(table, module, name, variant), proved, predicates,
                                     f"{name}={variant}")


def test_committed_ledger_names_real_declarations():
    rows, problems = trust_map.ledger()
    assert problems == []
    assert [r["step"] for r in rows] == ["1", "2a", "2b", "3", "4", "5", "6", "7", "8a", "8b", "9", "10"]
    # The plan's section 4 quotes these measured figures (E9); regenerate them after a table change.
    plan = (ROOT / "docs/CONSOLIDATION-PLAN.md").read_text()
    for r in rows:
        assert f"| {r['step']} | {r['removed']} | {r['tied']} |" in plan, r["step"]


def test_committed_ties_are_valid():
    """Every tie in the committed table passes the checks above against the committed dump."""
    table = trust_map.load_table()
    proved = trust_map.statements()
    assert all(uses is not None for uses in proved.values())
    _, problems = trust_map.measure()
    assert not [p for p in problems if "tie" in p or "mention" in p]
    assert all(isinstance(e, str) or e["tied"] for entries in table.values() for e in entries.values())


def test_budget_check_needs_a_signed_allowance(tmp_path):
    write_tree(tmp_path, {"D[R]": ["VE.Demo.decodeThing"], "S": ["VE.Demo.Meaning", "VE.Demo.helper"],
                          "C": ["instance:Inhabited Nat"]})
    tables = (tmp_path / "tools/trust-classes.json", tmp_path / "lean/statements.txt")
    files, _ = trust_map.measure(tmp_path, *tables)
    baseline_path = tmp_path / "baseline.json"
    trust_map.write_baseline(files, baseline_path, {})
    baseline = json.loads(baseline_path.read_text())
    assert trust_map.check(files, baseline) == []
    write_tree(tmp_path, {"D[V]": ["VE.Demo.decodeThing"], "S": ["VE.Demo.Meaning", "VE.Demo.helper"],
                          "C": ["instance:Inhabited Nat"]})
    grown, _ = trust_map.measure(tmp_path, *tables)
    failures = trust_map.check(grown, baseline)
    assert len(failures) == 1 and failures[0].startswith("V grew from 0 to 4")
    baseline["signed"] = [{"change": "demo", "signed": "DRI 2026-10-03", "allow": {"V": 4}}]
    assert trust_map.check(grown, baseline) == []
    baseline["signed"] = [{"change": "demo", "signed": "", "allow": {"V": 4}}]
    assert trust_map.check(grown, baseline)
    baseline_path.write_text(json.dumps({**baseline, "signed": [{"change": "demo", "signed": "DRI", "allow": {"V": 4}}]}))
    trust_map.write_baseline(grown, baseline_path)
    rewritten = json.loads(baseline_path.read_text())
    assert rewritten["signed"] == [] and rewritten["history"][0]["change"] == "demo"


def test_committed_trust_table_covers_every_declaration():
    files, problems = trust_map.measure()
    assert problems == []
    totals = trust_map.totals(files)
    assert totals["unclassified"] == 0
    baseline = json.loads(trust_map.BASELINE.read_text())
    assert set(baseline["files"]) <= set(files) | set(baseline["section11"])


def test_statement_dump_difference():
    old = "-- header\ntheorem A\n  P\n  -- expr 1\ntheorem B\n  Q\n  -- expr 2\n"
    new = "-- header\ntheorem B\n  Q'\n  -- expr 3\ntheorem C\n  R\n  -- expr 4\n"
    assert lean_statements.difference(old, new) == (["C"], ["A"], ["B"])
    assert lean_statements.difference(old, old) == ([], [], [])


def test_statement_dump_lists_every_audited_theorem():
    entries = lean_statements.parse(lean_statements.OUTPUT.read_text())
    assert sorted(entries) == lean_statements.audited_names()
    assert all(body.rstrip().splitlines()[-1].startswith("  -- expr ") for body in entries.values())


@pytest.mark.skipif(shutil.which("lake") is None, reason="lake is not on PATH")
def test_statement_dump_is_current():
    statements, predicates = lean_statements.dump_all()
    assert statements == lean_statements.OUTPUT.read_text(), \
        "lean/statements.txt is stale: run python3 tools/lean_statements.py"
    assert predicates == lean_statements.PREDICATES.read_text(), \
        "lean/predicates.txt is stale: run python3 tools/lean_statements.py"


def fake_build(folder: Path, names: list[str], body: str) -> None:
    folder.mkdir(parents=True)
    for name in names:
        path = folder / name
        path.write_text(f"#!/bin/sh\n{body}\n")
        path.chmod(0o755)


def test_output_diff_static_invocations_cover_every_mode_and_corpus():
    work = lean_output_diff.static_invocations()
    corpora = lean_output_diff.case_corpora()
    units = lean_output_diff.diagnose_units()
    assert "soft-norms@0" in units and ROOT / "lean/VE/Route/examples/route-cases.json" in corpora
    assert len(work) == len(corpora) * (len(lean_output_diff.CASE_MODES) + len(units))
    assert {exe for exe, _ in lean_output_diff.CASE_MODES} <= set(lean_output_diff.executables())


def test_output_diff_every_executable_has_inputs():
    """A `lean_exe` with no static inputs could change unseen (review B, consolidate-b1)."""
    static = {i.exe for i in lean_output_diff.static_invocations()}
    assert static | lean_output_diff.HARNESS_EXECUTABLES == set(lean_output_diff.executables())


@pytest.mark.skipif(not (lean_output_diff.BIN / "ve_service").is_file(), reason="ve_service is not built")
def test_output_diff_harness_inputs_cover_the_other_executables():
    work = lean_output_diff.harness_invocations(lean_output_diff.BIN)
    assert {i.exe for i in work} == lean_output_diff.HARNESS_EXECUTABLES
    session = next(i for i in work if i.exe == "ve_service")
    # Some request lines are malformed on purpose (the request errors); read the mode by prefix.
    modes = {re.match(r'\{"id":"out-\d+","mode":"([\w-]+)"', line)[1] for line in session.stdin.decode().splitlines()}
    assert {"evaluate", "route", "norms", "english", "identity"} <= modes
    decoded = [lean_output_diff.run(lean_output_diff.BIN / i.exe, i) for i in work if i.exe == "ve_response_decode"]
    # The genuine responses are accepted, so the decoder runs past its input checks.
    assert all(code == 0 and b'"accept"' in out for code, out, _ in decoded)


def test_output_diff_fails_when_a_rebuilt_executable_has_no_inputs(tmp_path, monkeypatch, capsys):
    """The reviewer's case: a rebuilt `ve_service` with zero invocations passed with exit 0."""
    names = lean_output_diff.executables()
    monkeypatch.setattr(lean_output_diff, "static_invocations", lambda root=ROOT: [
        lean_output_diff.Invocation("ve_norms_route", "a", ())])
    monkeypatch.setattr(lean_output_diff, "harness_invocations", lambda baseline: [])
    base, new = tmp_path / "base", tmp_path / "new"
    fake_build(base, names, "echo same")
    fake_build(new, names, "echo same")
    (new / "ve_service").write_text("#!/bin/sh\necho same\n# rebuilt\n")
    manifest = {"commit": "c", "executables": {n: lean_output_diff.digest(base / n) for n in names}}
    (base / "manifest.json").write_text(json.dumps(manifest))
    assert lean_output_diff.compare(base, new, [], tmp_path) == 1
    assert "no invocation of the rebuilt executables ve_service" in capsys.readouterr().err
    (new / "ve_service").write_text((base / "ve_service").read_text())
    assert lean_output_diff.compare(base, new, [], tmp_path) == 0
    # Under --all every executable is compared, so every one needs inputs.
    assert lean_output_diff.compare(base, new, [], tmp_path, everything=True) == 1
    monkeypatch.setattr(lean_output_diff, "static_invocations", lambda root=ROOT: [
        lean_output_diff.Invocation(name, "a", ()) for name in names])
    assert lean_output_diff.compare(base, new, [], tmp_path, everything=True) == 0
    # A recorded invocation of an executable the baseline lacks is an error, not a skip.
    unknown = [lean_output_diff.Invocation("ve_gone", "a", ())]
    assert lean_output_diff.compare(base, new, unknown, tmp_path) == 2


def test_output_diff_reports_a_changed_output(tmp_path, monkeypatch):
    names = lean_output_diff.executables()
    monkeypatch.setattr(lean_output_diff, "static_invocations", lambda root=ROOT: [
        lean_output_diff.Invocation(name, "demo", ("x",), b"in") for name in names])
    monkeypatch.setattr(lean_output_diff, "harness_invocations", lambda baseline: [])
    base, same, other = tmp_path / "base", tmp_path / "same", tmp_path / "other"
    fake_build(base, names, 'echo "$@"; cat')
    fake_build(same, names, 'echo "$@"; cat')
    fake_build(other, names, 'echo "$@"; echo changed')
    manifest = {"commit": "c", "executables": {n: lean_output_diff.digest(base / n) for n in names}}
    (base / "manifest.json").write_text(json.dumps(manifest))
    assert lean_output_diff.compare(base, same, [], tmp_path) == 0  # identical binaries: not run
    assert lean_output_diff.compare(base, same, [], tmp_path, everything=True) == 0
    assert lean_output_diff.compare(base, other, [], tmp_path) == 1
    monkeypatch.setattr(lean_output_diff, "static_invocations", lambda root=ROOT: [])
    assert lean_output_diff.compare(base, same, [], tmp_path) == 1  # nothing compared is not evidence
    assert lean_output_diff.compare(base, other, [], tmp_path) == 1


def test_output_diff_runs_only_rebuilt_executables(tmp_path, monkeypatch, capsys):
    names = lean_output_diff.executables()
    monkeypatch.setattr(lean_output_diff, "static_invocations", lambda root=ROOT: [
        lean_output_diff.Invocation("ve_norms_route", "a", ()), lean_output_diff.Invocation("ve_risk_route", "b", ())])
    base, new = tmp_path / "base", tmp_path / "new"
    fake_build(base, names, "echo same")
    fake_build(new, names, "echo same")
    (new / "ve_risk_route").write_text("#!/bin/sh\necho same\n# rebuilt\n")
    manifest = {"commit": "c", "executables": {n: lean_output_diff.digest(base / n) for n in names}}
    (base / "manifest.json").write_text(json.dumps(manifest))
    assert lean_output_diff.compare(base, new, [], tmp_path) == 0
    out = capsys.readouterr().out
    assert "different digest: ve_risk_route" in out and "2 invocations, 1 run on both builds, 1 skipped" in out


def test_recorder_records_lean_invocations_for_replay(tmp_path):
    bin_folder = tmp_path / "lean/.lake/build/bin"
    fake_build(bin_folder, ["ve_norms_route"], 'cat "$1"; cat')
    other = tmp_path / "elsewhere"
    fake_build(other, ["ve_norms_route"], "cat")
    cases = tmp_path / "cases.json"
    cases.write_text("[1]")
    script = tmp_path / "drive.py"
    script.write_text(
        "import subprocess, sys\n"
        f"sys.path.insert(0, {str(ROOT)!r})\n"
        "import tests.lean_input_recorder as recorder\n"
        f"subprocess.run([{str(bin_folder / 've_norms_route')!r}, {str(cases)!r}], input=b'[2]', capture_output=True)\n"
        f"subprocess.run([{str(other / 've_norms_route')!r}], input=b'ignored', capture_output=True)\n"
        "recorder.pytest_sessionfinish(None, 0)\n")
    subprocess.run([sys.executable, str(script)], check=True, env={**os.environ, "VE_LEAN_INPUTS": str(tmp_path / "rec")})
    lines = [json.loads(line) for path in (tmp_path / "rec").glob("*.jsonl") for line in path.read_text().splitlines()]
    assert len(lines) == 1
    record = lines[0]
    assert record["exe"] == "ve_norms_route" and record["args"] == ["@file:0"]
    assert base64.b64decode(record["files"][0]["data"]) == b"[1]" and base64.b64decode(record["stdin"]) == b"[2]"
    work = lean_output_diff.recorded_invocations(tmp_path / "rec", tmp_path / "scratch")
    assert len(work) == 1 and work[0].stdin == b"[2]" and Path(work[0].args[0]).read_text() == "[1]"


def test_contract_inputs_become_soft_elaborate_cases(tmp_path):
    path = tmp_path / "inputs.json"
    path.write_text(json.dumps([["t1", {"env": 1}, [{"norm": 1}]]]))
    work = lean_output_diff.contract_invocations(path)
    assert [w.exe for w in work] == ["ve_soft_norms_route", "ve_diagnose"]
    cases = json.loads(work[0].stdin)
    assert cases == [{"id": "recorded-0", "kind": "soft-elaborate", "environment": {"env": 1}, "norms": [{"norm": 1}]}]
