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


def located(token: str) -> str:
    """A fixture constant as the dump writes it: `name@Module`, `VE.Demo` unless given."""
    return token if "@" in token else f"{token}@VE.Demo"


def predicate_file(predicates: tuple[str, ...] = (), modules: tuple[str, ...] = ("VE.Demo",)) -> str:
    return "-- header\n" + "".join(f"module {m}\n" for m in modules) + "".join(f"{located(p)}\n" for p in predicates)


# What Lean's environment records for each fixture source (lean/declarations.txt without the
# module): every constant with a source range, as `<line>:<column>-<line>:<column> <kind> <name>`.
# The structure's field is inside its range; the anonymous instance has Lean's generated name.
COMPILED = {
    "FIXTURE": ["8:0-10:10 def VE.Demo.decodeThing", "12:0-13:53 theorem VE.Demo.decodeThing_empty",
                "15:0-16:13 instance VE.Demo.instInhabitedNat", "18:0-19:9 structure VE.Demo.Meaning",
                "19:2-19:3 def VE.Demo.Meaning.x", "22:0-22:20 def VE.Demo.helper"],
    "OTHER": ["3:0-4:9 structure VE.Demo.Meaning", "4:2-4:3 def VE.Demo.Meaning.y", "6:0-6:24 def VE.Demo.decodeThing",
              "8:0-8:19 def VE.Demo.helper"],
    "MARKER": ["5:0-5:32 theorem VE.Demo.marker", "7:0-7:82 theorem VE.Demo.decodeThing_tie"],
}
INSTANCE = "VE.Demo.instInhabitedNat"


def write_declarations(root: Path, generated: dict[str, list[str]] | None = None) -> None:
    """lean/declarations.txt for every file of a fixture tree, as tools/lean_statements.py writes it
    from the compiled environment: a fixture source takes its `COMPILED` entries, a committed file
    its block of the committed list. `generated` adds, per module, constants without a source
    range whose name extends no constant (`<kind> <name>`, as a `run_elab` adds them)."""
    sources = {globals()[name]: entries for name, entries in COMPILED.items()}
    committed, hashes = lean_statements.declaration_list()
    blocks = []
    for path in lean_statements.sources(root):
        module = lean_statements.module_name(path.relative_to(root / "lean").as_posix())
        digest = lean_statements.source_hash(path)
        if path.read_text() in sources:
            entries = [f"{e}@{module}" for e in sources[path.read_text()]]
        else:
            assert hashes[module] == digest, path
            entries = [f"{d.start[0]}:{d.start[1]}-{d.end[0]}:{d.end[1]} {d.kind} {d.name}@{module}"
                       if d.start else f"generated {d.kind} {d.name}@{module}" for d in committed[module]]
        entries += [f"generated {e}@{module}" for e in (generated or {}).get(module, [])]
        blocks.append(f"module {module} {digest}\n" + "".join(f"{e}\n" for e in entries))
    (root / "lean/declarations.txt").write_text("-- header\n" + "".join(blocks))


def write_tree(root: Path, table: dict, statements: str = "", predicates: tuple[str, ...] = (),
               modules: tuple[str, ...] = ("VE.Demo",)) -> None:
    (root / "lean/VE").mkdir(parents=True, exist_ok=True)
    (root / "lean/VE/Demo.lean").write_text(FIXTURE)
    (root / "tools").mkdir(exist_ok=True)
    (root / "tools/trust-classes.json").write_text(json.dumps({"modules": {"VE/Demo.lean": table}}))
    (root / "lean/statements.txt").write_text(statements)
    (root / "lean/predicates.txt").write_text(predicate_file(predicates, modules))
    write_declarations(root)


def scan_fixture(folder: Path, source: str, entries: list[str]) -> tuple[list, int, list[str]]:
    with_module = [lean_statements.DECLARED.match(f"{e}@VE.Demo") for e in entries]
    declared = [lean_statements.Declared(m[6].removesuffix("@VE.Demo"), m[5], (int(m[1]), int(m[2])),
                                         (int(m[3]), int(m[4]))) for m in with_module]
    path = folder / "Demo.lean"
    path.write_text(source)
    return trust_map.scan(path, declared)


def test_scan_spans_names_and_kinds(tmp_path):
    decls, total, problems = scan_fixture(tmp_path, FIXTURE, COMPILED["FIXTURE"])
    assert total == len(FIXTURE.splitlines()) and problems == []
    rows = [(d.kind, d.name, d.start, d.end) for d in decls]
    assert rows == [
        ("def", "VE.Demo.decodeThing", 8, 11),          # docstring through the blank line
        ("theorem", "VE.Demo.decodeThing_empty", 12, 14),  # the attribute line starts it
        ("instance", INSTANCE, 15, 17),
        ("structure", "VE.Demo.Meaning", 18, 20),        # its field is part of it
        ("def", "VE.Demo.helper", 22, 22),               # `section` and `end` are boundaries
        ("command", None, 25, 26),                       # `example` declares nothing
        ("command", None, 27, 28),
    ]


@pytest.mark.parametrize("source,entries,problem,line", [
    # A declaration the compiled module does not record (a stale or hand-written list): its lines
    # stay counted, trusted and unclassifiable (no name).
    (FIXTURE, [e for e in COMPILED["FIXTURE"] if "helper" not in e],
     "line 22 reads as a declaration, but the compiled module records none there", (None, "unrecorded", 22)),
    # Two declarations on one line: the scanner saw only the first.
    ("namespace VE.Demo\ndef a : Nat := 1 def b : Nat := 2\nend VE.Demo\n", ["2:0-2:16 def VE.Demo.a", "2:17-2:33 def VE.Demo.b"],
     "line 2: VE.Demo.a, VE.Demo.b start on one line; write each declaration on its own lines", (None, "unrecorded", 2)),
    # Two unrelated constants on one range cannot be told apart.
    ("def a : Nat := 1\n", ["1:0-1:16 def VE.Demo.a", "1:0-1:16 def VE.Demo.b"], "VE.Demo.b and VE.Demo.a share one source range",
     ("VE.Demo.a", "def", 1)),
])
def test_scan_fails_where_the_compiled_module_disagrees(tmp_path, source, entries, problem, line):
    decls, _, problems = scan_fixture(tmp_path, source, entries)
    assert problems == [problem]
    assert line in [(d.name, d.kind, d.start) for d in decls]


def test_nothing_inside_a_compiled_range_ends_the_declaration(tmp_path):
    """A column-0 comment block or a term-level `open … in` inside a declaration's body cut its
    lines short under the source scanner, and the rest counted `o` (untrusted)."""
    source = ("namespace VE.Demo\ndef meaning (n : Nat) : Nat :=\n/- a comment at column 0 -/\n  n +\n"
              "open Nat in succ 0\n\nexample : meaning 0 = 1 := rfl\nend VE.Demo\n")
    decls, _, problems = scan_fixture(tmp_path, source, ["2:0-5:18 def VE.Demo.meaning"])
    assert problems == []
    assert [(d.name, d.start, d.end) for d in decls] == [("VE.Demo.meaning", 2, 6), (None, 7, 7)]


def test_generated_parts_belong_to_their_declaration():
    """A structure's fields, a derived instance, a `where` helper and a macro's generated rules lie
    inside the declaration's range; of constants with one range the name the others extend wins."""
    tops, parts, problems = trust_map.top_level([
        lean_statements.Declared(n, k, s, e) for n, k, s, e in [
            ("VE.Pt", "structure", (1, 0), (4, 15)), ("VE.Pt.x", "def", (2, 2), (2, 3)),
            ("VE.instReprPt.repr", "def", (4, 11), (4, 15)), ("VE.instReprPt", "instance", (4, 11), (4, 15)),
            ("VE.helper", "def", (6, 0), (7, 34)), ("VE.helper.aux", "def", (7, 6), (7, 34)),
            ("_aux_X___macroRules_tacticWalk_1", "def", (9, 0), (9, 42)), ("tacticWalk", "def", (9, 0), (9, 42)),
            ("_hidden", "def", (11, 0), (11, 20))]])
    assert problems == [] and [t.name for t in tops] == ["VE.Pt", "VE.helper", "tacticWalk", "_hidden"]
    # The constants inside each range stay recorded as its parts, for `classify` to check.
    assert parts == {"VE.Pt": ["VE.Pt.x", "VE.instReprPt", "VE.instReprPt.repr"], "VE.helper": ["VE.helper.aux"],
                     "tacticWalk": ["_aux_X___macroRules_tacticWalk_1"], "_hidden": []}


def test_classes_counts_and_unclassified_fail_closed(tmp_path):
    write_tree(tmp_path, {"D[V]": ["VE.Demo.decodeThing"], "S": ["VE.Demo.Meaning"], "C": [INSTANCE]})
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
    return (f"theorem VE.Demo.decodeThing_empty\n  {statement}\n"
            f"  -- uses {' '.join(located(u) for u in uses.split())}\n  -- expr 1\n")


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


@pytest.mark.parametrize("spelling", ["instance:Inhabited Nat", "VE.Demo.«helper»", "VE.Demo.helper(n"])
def test_source_spellings_are_not_declarations(tmp_path, spelling):
    """Fix 4 B: the table names declarations as Lean compiles them. A name the old source scanner
    made up (an anonymous instance's signature, a quoted name, a binder without a space) classes
    nothing: it is a stale entry, and the declaration it meant stays unclassified and trusted."""
    files, problems = tie_problems(tmp_path, {"C": [spelling], "S": ["VE.Demo.Meaning"]}, "")
    assert problems == [f"trust-classes.json: VE/Demo.lean: {spelling} is not a declaration of that file"]
    # Lean's generated instance name can be tied like any other declaration.
    table = {"D[V]": [{"name": INSTANCE, "tied": ["VE.Demo.decodeThing_empty"]}], "S": ["VE.Demo.Meaning"]}
    files, problems = tie_problems(tmp_path, table, entry("…", f"VE.Demo.Meaning {INSTANCE}"))
    assert problems == [] and files["VE/Demo.lean"]["tied"] == 3


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
    predicates = {(m, "VE.Closure.Formula.WellFormed") for m in ("VE.Closure.Syntax", "VE.Norms.X", "VE.Tableau", "VE.New")}
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
    # A declaration holding a predicate (a `where` helper) is seeded as the predicate is; a tie of
    # it does not cover the predicate, so it does not stay (consolidate-b1d looprecheck 1).
    holder = [trust_map.Decl("VE.Demo.decoder", "def", 2, 4, ("VE.Demo.decoder.WellFormed",))]
    inside = {("VE.Norms.X", "VE.Demo.decoder.WellFormed")}
    for old in ("C", "D[R]", {"class": "C", "tied": ["VE.Demo.acceptance"]}, None):
        kept = {} if old is None else {"VE.Demo.decoder": old}
        assert trust_map.seed_module("VE/Norms/X.lean", holder, {"S": 5, "C": 5}, inside, kept) == {"VE.Demo.decoder": "S"}
    assert trust_map.seed_module("VE/Norms/X.lean", holder, {"S": 5, "C": 5}, set(), {"VE.Demo.decoder": "C"}) == {
        "VE.Demo.decoder": "C"}


def test_rebaseline_needs_a_reason_for_growth(tmp_path):
    write_tree(tmp_path, {"D[R]": ["VE.Demo.decodeThing"], "S": ["VE.Demo.Meaning", "VE.Demo.helper"],
                          "C": [INSTANCE]})
    tables = (tmp_path / "tools/trust-classes.json", tmp_path / "lean/statements.txt")
    baseline_path = tmp_path / "baseline.json"
    trust_map.write_baseline(trust_map.measure(tmp_path, *tables)[0], baseline_path, {})
    write_tree(tmp_path, {"K": ["VE.Demo.decodeThing"], "S": ["VE.Demo.Meaning", "VE.Demo.helper"],
                          "C": [INSTANCE]})
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
    assert ("VE.Closure.Syntax", "VE.Closure.Formula.WellFormed") in predicates


def test_ledger_credits_each_declaration_once(tmp_path):
    write_tree(tmp_path, {"S": ["VE.Demo.Meaning"], "G[V]": ["VE.Demo.helper"], "D[R]": ["VE.Demo.decodeThing"],
                          "C": [INSTANCE]})
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


# A second module that defines namesakes of VE/Demo.lean's declarations (nothing imports the two
# together, so Lean accepts both).
OTHER = '''namespace VE.Demo

structure Meaning where
  y : Nat

def decodeThing : Nat := 0

def helper : Nat := 2

end VE.Demo
'''
OTHER_TABLE = {"S": ["VE.Demo.Meaning"], "C": ["VE.Demo.decodeThing", "VE.Demo.helper"]}

# Review B (consolidate-b1d looprecheck 1), the reviewer's reproducer: a predicate written as a
# `where` helper lies inside the decoder's range, so it was part of the decoder and never checked
# as a predicate; with the decoder C, every entry point passed with zero trusted lines.
WHERE = '''namespace VE.Demo
def decoder (n : Nat) : Bool := n == 0
where
  WellFormed (n : Nat) : Prop := n = 0
theorem acceptance (n : Nat) : decoder n = true ↔ decoder.WellFormed n := by
  simp [decoder, decoder.WellFormed]
end VE.Demo
'''
COMPILED["WHERE"] = ["2:0-4:38 def VE.Demo.decoder", "4:2-4:38 def VE.Demo.decoder.WellFormed",
                     "5:0-6:36 theorem VE.Demo.acceptance"]
WHERE_FILES = {"files": {"VE/Where.lean": "WHERE"}}
NESTED = "VE.Demo.decoder.WellFormed@VE.Where"

# Review B (consolidate-b1 fix 5): a module whose source declares nothing Lean records a range
# for, as one whose only command is a `run_elab` that adds `VE.Empty.WellFormed` with `addDecl`.
# The predicate list names the predicate, but no declaration of the module did, so no file placed
# it and every entry point passed with zero trusted lines.
EMPTY = "namespace VE.Empty\nend VE.Empty\n"
COMPILED["EMPTY"] = []
EMPTY_FILES = {"files": {"VE/Empty.lean": "EMPTY"}}


def where_tree(decoder: dict, dump: str = "", predicates: tuple[str, ...] = (NESTED,)) -> tuple:
    """A problem tree: VE/Demo.lean with Meaning S, and VE/Where.lean with the decoder classed `decoder`."""
    return ({"S": ["VE.Demo.Meaning"]}, dump, predicates, False, {**WHERE_FILES, "table": {"VE/Where.lean": decoder}})


ACCEPTANCE = ("theorem VE.Demo.acceptance\n  …\n  -- uses VE.Demo.Meaning@VE.Demo VE.Demo.decoder@VE.Where "
              f"{NESTED}\n  -- expr 1\n")

# Every kind of validation problem `walk` reports, as (table, statement dump, predicates, drop the
# predicate list, options of `problem_tree`). Review B (looprecheck 1): `--ledger` discarded these
# and exited 0.
PROBLEM_TREES = {
    "predicate classed C": ({"C": ["VE.Demo.helper"], "S": ["VE.Demo.Meaning"]}, "", ("VE.Demo.helper",), False),
    "predicate classed D[R]": ({"D[R]": ["VE.Demo.helper"], "S": ["VE.Demo.Meaning"]}, "", ("VE.Demo.helper",), False),
    "tie not mentioned": (TIED, entry("True", "VE.Demo.Meaning"), (), False),
    "tie to nothing trusted": (TIED, entry("…", "VE.Demo.decodeThing"), (), False),
    "tying theorem missing": (TIED, "", (), False),
    # Fix 4 B: names the old source scanner spelled; Lean names these `VE.Demo.instInhabitedNat`
    # and `VE.Demo.helper`.
    "source-spelled instance": ({"C": ["instance:Inhabited Nat"], "S": ["VE.Demo.Meaning"]}, "", (), False),
    "quoted spelling": ({"C": ["VE.Demo.«helper»"], "S": ["VE.Demo.Meaning"]}, "", ("VE.Demo.helper",), False),
    "stale table entry": ({"D[V]": ["VE.Demo.gone"], "S": ["VE.Demo.Meaning"]}, "", (), False),
    "predicate list missing": ({"S": ["VE.Demo.Meaning"]}, "", (), True),
    # Review B (looprecheck 2): a theorem listed as S anchored the tie, while the budget counted it P.
    "theorem listed as S anchors a tie": ({"S": ["VE.Demo.decodeThing_empty"], **{"D[V]": TIED["D[V]"]}},
                                          entry("…", "VE.Demo.decodeThing VE.Demo.decodeThing_empty"), (), False),
    "theorem listed as P": ({"P": ["VE.Demo.decodeThing_empty"], "S": ["VE.Demo.Meaning"]}, "", (), False),
    "theorem listed tied": ({"C": [{"name": "VE.Demo.decodeThing_empty", "tied": ["VE.Demo.decodeThing_empty"]}],
                             "S": ["VE.Demo.Meaning"]}, entry("…", "VE.Demo.Meaning VE.Demo.decodeThing_empty"), (), False),
    "anchor listed for another file": ({"D[V]": TIED["D[V]"]}, entry("…", "VE.Demo.Meaning VE.Demo.decodeThing"),
                                       (), False, {"table": {"VE/Other.lean": {"S": ["VE.Demo.Meaning"]}}}),
    "anchor only unclassified": ({"D[V]": TIED["D[V]"]}, entry("…", "VE.Demo.helper VE.Demo.decodeThing"), (), False),
    # Review B (looprecheck 3): the anchors were full names without their module. The statement
    # mentions `VE.Demo.Meaning` of VE/Demo.lean, classed C; a namesake in VE/Other.lean, a module
    # nothing imports with it, is S and anchored the tie.
    "anchor's namesake in another module": (
        {**TIED, "S": [], "C": ["VE.Demo.Meaning"]}, entry("…", "VE.Demo.Meaning VE.Demo.decodeThing"), (), False,
        {"files": {"VE/Other.lean": "OTHER"}, "table": {"VE/Other.lean": OTHER_TABLE}}),
    # The same for the tied declaration: the statement is about another module's `decodeThing`.
    "tied declaration's namesake in another module": (
        TIED, entry("…", "VE.Demo.Meaning VE.Demo.decodeThing@VE.Other"), (), False,
        {"files": {"VE/Other.lean": "OTHER"}, "table": {"VE/Other.lean": OTHER_TABLE}}),
    # And for predicates: the list names VE/Demo.lean's `helper`, not the namesake.
    "predicate classed C beside a namesake": (
        {"C": ["VE.Demo.helper"], "S": ["VE.Demo.Meaning"]}, "", ("VE.Demo.helper",), False,
        {"files": {"VE/Other.lean": "OTHER"}, "table": {"VE/Other.lean": OTHER_TABLE}}),
    "a file the predicate scan did not read": (
        {"S": ["VE.Demo.Meaning"]}, "", (), False,
        {"files": {"VE/Other.lean": "OTHER"}, "table": {"VE/Other.lean": OTHER_TABLE}, "modules": ("VE.Demo",)}),
    "predicate list without modules": ({"S": ["VE.Demo.Meaning"]}, "", (), False,
                                       {"predicates": "-- header\nmodule VE.Demo\nVE.Demo.helper\n"}),
    "uses line without modules": (TIED, "theorem VE.Demo.decodeThing_empty\n  …\n"
                                        "  -- uses VE.Demo.Meaning VE.Demo.decodeThing\n  -- expr 1\n", (), False),
    # Fix 4 B: the declarations are the compiled module's; a source edited since, or no list at all,
    # leaves nothing to classify by.
    "source edited after the declaration list": ({"S": ["VE.Demo.Meaning"]}, "", (), False, {"edit": "VE/Demo.lean"}),
    "declaration list missing": ({"S": ["VE.Demo.Meaning"]}, "", (), False, {"declarations": None}),
    "declaration list of another module": ({"S": ["VE.Demo.Meaning"]}, "", (), False, {"declarations": (
        "-- header\nmodule VE.Demo 0000000000000000000000000000000000000000000000000000000000000000\n"
        "8:0-10:10 def VE.Demo.decodeThing@VE.Other\n")}),
    # Review B (consolidate-b1d looprecheck 1): a predicate inside a declaration's range is checked
    # under the declaration's class, which its lines take; a tie of the declaration does not cover it.
    "predicate inside a C declaration": where_tree({"C": ["VE.Demo.decoder"]}),
    "predicate inside a D[R] declaration": where_tree({"D[R]": ["VE.Demo.decoder"]}),
    "predicate inside a tied declaration": where_tree(
        {"C": [{"name": "VE.Demo.decoder", "tied": ["VE.Demo.acceptance"]}]}, ACCEPTANCE),
    # A generated predicate without a range (an inductive's `below`) is part of the declaration
    # its name extends; one that extends none is part of nothing and fails.
    "rangeless predicate of a C declaration": ({"C": ["VE.Demo.Meaning"]}, "", ("VE.Demo.Meaning.below",), False),
    "predicate of no declaration": ({"S": ["VE.Demo.Meaning"]}, "", ("VE.Demo.orphan",), False),
    # Review B (consolidate-b1 fix 5): every constant of the compiled dumps is placed or fails,
    # whatever file or module it names. A predicate of a file without declarations, of a module
    # that is no file, a module the predicate scan read that is no file, and a constant Lean
    # records without a range whose name extends no constant.
    "predicate of a file without declarations": ({"S": ["VE.Demo.Meaning"]}, "", ("VE.Empty.WellFormed@VE.Empty",),
                                                 False, EMPTY_FILES),
    "predicate of a module that is no file": ({"S": ["VE.Demo.Meaning"]}, "", ("VE.Gone.WellFormed@VE.Gone",), False),
    "scanned module that is no file": ({"S": ["VE.Demo.Meaning"]}, "", (), False, {"modules": ("VE.Demo", "VE.Gone")}),
    "generated constant": ({"S": ["VE.Demo.Meaning"]}, "", (), False, {"generated": {"VE.Demo": ["def VE.Demo.made"]}}),
    "generated constant of a file without declarations": (
        {"S": ["VE.Demo.Meaning"]}, "", (), False, {**EMPTY_FILES, "generated": {"VE.Empty": ["def VE.Empty.made"]}}),
}
VALID_TREES = {
    "tied": (TIED, entry("…", "VE.Demo.Meaning VE.Demo.decodeThing"), (), False),
    "unclassified": ({"S": ["VE.Demo.Meaning"]}, "", (), False),
    "predicate tied": ({"C": [{"name": "VE.Demo.helper", "tied": ["VE.Demo.decodeThing_empty"]}], "S": ["VE.Demo.Meaning"]},
                       entry("…", "VE.Demo.Meaning VE.Demo.helper"), ("VE.Demo.helper",), False),
    # A statement about the meaning another module defines ties to that meaning.
    "tied to another module's meaning": (
        {**TIED, "S": [], "C": ["VE.Demo.Meaning"]}, entry("…", "VE.Demo.Meaning@VE.Other VE.Demo.decodeThing"), (),
        False, {"files": {"VE/Other.lean": "OTHER"}, "table": {"VE/Other.lean": OTHER_TABLE}}),
    # A predicate of another module says nothing about its namesake here.
    "namesake of a predicate": (
        {"C": ["VE.Demo.helper"], "S": ["VE.Demo.Meaning"]}, "", ("VE.Demo.helper@VE.Other",), False,
        {"files": {"VE/Other.lean": "OTHER"}, "table": {"VE/Other.lean": {**OTHER_TABLE, "C": ["VE.Demo.decodeThing"],
                                                                          "S": ["VE.Demo.Meaning", "VE.Demo.helper"]}}}),
    "predicate inside an S declaration": where_tree({"S": ["VE.Demo.decoder"]}),
    "predicate inside a [V] declaration": where_tree({"D[V]": ["VE.Demo.decoder"]}),
    "predicate inside an unclassified declaration": where_tree({}),
    "rangeless predicate of an S declaration": ({"S": ["VE.Demo.Meaning"]}, "", ("VE.Demo.Meaning.below",), False),
}
WHOLE_TREE = {"steps": [{"step": "all", "title": "", "days": 1, "risk": 1, "removed": [{"module": "VE/*"}]}]}


def problem_tree(root: Path, tree: tuple) -> None:
    """Write a fixture tree: (table of VE/Demo.lean, statement dump, predicates, drop the predicate
    list, options). The options add files (`files`, path under lean/ to source or "OTHER"), table
    entries of other files (`table`), the modules the predicate scan read (`modules`, default every
    file), a predicate list verbatim (`predicates`), generated constants of the declaration list
    (`generated`, as `write_declarations` takes them), a declaration list verbatim (`declarations`,
    None for none) and a file edited after the declaration list was written (`edit`)."""
    table, dump, predicates, drop, *rest = tree
    options = rest[0] if rest else {}
    files = options.get("files", {})
    modules = options.get("modules", ("VE.Demo", *(f.removesuffix(".lean").replace("/", ".") for f in files)))
    write_tree(root, table, dump, predicates, modules)
    for name, text in files.items():
        (root / "lean" / name).write_text({"OTHER": OTHER, "WHERE": WHERE, "EMPTY": EMPTY}.get(text, text))
    if "table" in options:
        path = root / "tools/trust-classes.json"
        path.write_text(json.dumps({"modules": {**json.loads(path.read_text())["modules"], **options["table"]}}))
    if "predicates" in options:
        (root / "lean/predicates.txt").write_text(options["predicates"])
    if drop:
        (root / "lean/predicates.txt").unlink()
    write_declarations(root, options.get("generated"))
    if "declarations" in options:
        if options["declarations"] is None:
            (root / "lean/declarations.txt").unlink()
        else:
            (root / "lean/declarations.txt").write_text(options["declarations"])
    if "edit" in options:
        path = root / "lean" / options["edit"]
        path.write_text(path.read_text() + "-- edited\n")
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
    assert row["removed"] == sum(counts["trusted"] for counts in files.values())


@pytest.mark.parametrize("name,problem", [
    ("anchor's namesake in another module", "VE/Demo.lean: VE.Demo.decodeThing: the statement of "
     "VE.Demo.decodeThing_empty mentions no K, S or untied [V] declaration of the tree, validly classified, to tie it to"),
    ("tied declaration's namesake in another module", "VE/Demo.lean: VE.Demo.decodeThing: the statement of "
     "VE.Demo.decodeThing_empty does not mention VE.Demo.decodeThing of VE.Demo"),
    ("predicate classed C beside a namesake", "VE/Demo.lean: VE.Demo.helper: a predicate cannot be C unless a "
     "theorem ties it; classify it K or S (or P for a proof helper)"),
    ("a file the predicate scan did not read", "VE/Other.lean: predicates.txt did not read module VE.Other; "
     "rerun tools/lean_statements.py"),
    ("predicate list without modules", "predicates.txt: 'VE.Demo.helper' names no defining module; "
     "rerun tools/lean_statements.py"),
    ("uses line without modules", "VE/Demo.lean: VE.Demo.decodeThing: statements.txt has no uses line with "
     "defining modules for VE.Demo.decodeThing_empty; rerun tools/lean_statements.py"),
    ("source-spelled instance", "trust-classes.json: VE/Demo.lean: instance:Inhabited Nat is not a declaration of that file"),
    ("quoted spelling", "trust-classes.json: VE/Demo.lean: VE.Demo.«helper» is not a declaration of that file"),
    ("source edited after the declaration list", "VE/Demo.lean: declarations.txt was not compiled from this source; "
     "rerun tools/lean_statements.py"),
    ("declaration list missing", "declarations.txt is missing; run tools/lean_statements.py"),
    ("declaration list of another module", "declarations.txt: '8:0-10:10 def VE.Demo.decodeThing@VE.Other' is not a "
     "declaration of the module above it; rerun tools/lean_statements.py"),
    *((name, f"VE/Where.lean: VE.Demo.decoder: a declaration holding a predicate (VE.Demo.decoder.WellFormed) cannot be "
       f"{cls}; classify it K or S (or P for a proof helper), or declare the predicate on its own (a tie of the "
       "declaration does not tie what is inside it)")
      for name, cls in (("predicate inside a C declaration", "C"), ("predicate inside a D[R] declaration", "D[R]"),
                        ("predicate inside a tied declaration", "tied C"))),
    ("rangeless predicate of a C declaration", "VE/Demo.lean: VE.Demo.Meaning: a declaration holding a predicate "
     "(VE.Demo.Meaning.below) cannot be C; classify it K or S (or P for a proof helper), or declare the predicate on "
     "its own (a tie of the declaration does not tie what is inside it)"),
    ("predicate of no declaration", "VE/Demo.lean: the predicate VE.Demo.orphan is part of no declaration of the "
     "file (no source range, and its name extends none); rerun tools/lean_statements.py"),
    ("predicate of a file without declarations", "VE/Empty.lean: the predicate VE.Empty.WellFormed is part of no "
     "declaration of the file (no source range, and its name extends none); rerun tools/lean_statements.py"),
    ("predicate of a module that is no file", "predicates.txt: the predicate VE.Gone.WellFormed is of module VE.Gone, "
     "which is not a file of the tree; rerun tools/lean_statements.py"),
    ("scanned module that is no file", "predicates.txt read module VE.Gone, which is not a file of the tree; rerun "
     "tools/lean_statements.py"),
    *((name, f"{file}: VE.{module}.made (def) has no source range and its name extends no constant (a metaprogram such "
       "as `run_elab` or `addDecl` made it): no line of the file can be classified for it")
      for name, file, module in (("generated constant", "VE/Demo.lean", "Demo"),
                                 ("generated constant of a file without declarations", "VE/Empty.lean", "Empty"))),
])
def test_declarations_are_told_apart_by_module(tmp_path, name, problem):
    """Review B (looprecheck 3): a declaration is its name and its module. Each tree fails for
    exactly its own reason."""
    problem_tree(tmp_path, PROBLEM_TREES[name])
    _, problems = trust_map.measure(tmp_path, tmp_path / "tools/trust-classes.json", tmp_path / "lean/statements.txt")
    assert problems == [problem]


def test_namesake_cannot_lend_its_class(tmp_path):
    """The reviewer's numbers: with the anchor's namesake as the meaning, the D[V] decoder counted
    zero trusted lines, so `--check` passed decoder growth against a zero [V] budget."""
    problem_tree(tmp_path, VALID_TREES["tied to another module's meaning"])
    files, problems = trust_map.measure(tmp_path, tmp_path / "tools/trust-classes.json", tmp_path / "lean/statements.txt")
    assert problems == [] and files["VE/Demo.lean"]["tied"] == 4
    tied = trust_map.budget(files["VE/Demo.lean"])["V"]  # the unclassified helper and instance
    problem_tree(tmp_path, PROBLEM_TREES["anchor's namesake in another module"])
    files, problems = trust_map.measure(tmp_path, tmp_path / "tools/trust-classes.json", tmp_path / "lean/statements.txt")
    # The decoder's four lines fail closed into [V].
    assert problems and files["VE/Demo.lean"]["tied"] == 0 and trust_map.budget(files["VE/Demo.lean"])["V"] == tied + 4


COLLISION = {
    "lakefile.toml": 'name = "collision"\nversion = "0.1.0"\ndefaultTargets = ["VE"]\n[[lean_lib]]\nname = "VE"\n',
    "VE.lean": "import VE.Decoder\n",
    "VE/Audit.lean": "import VE.Decoder\n#print axioms VE.Demo.decodeThing_tie\n",
    "VE/Decoder.lean": ("namespace VE.Demo\ndef anchor : Nat := 1\ndef decodeThing (_ : String) : Nat :=\n  let x := 0\n"
                        "  x\ntheorem decodeThing_tie : decodeThing \"\" = 0 ∧ anchor = 1 := ⟨rfl, rfl⟩\nend VE.Demo\n"),
    "VE/Meaning.lean": "namespace VE.Demo\ndef anchor : Nat := 0\nend VE.Demo\n",
}


@pytest.mark.skipif(shutil.which("lake") is None, reason="lake is not on PATH")
def test_dump_tells_namesakes_of_two_modules_apart(tmp_path, capsys):
    """Review B (looprecheck 3), the reviewer's reproducer: VE/Decoder.lean's `anchor` is C and
    VE/Meaning.lean (nothing imports it) defines an S namesake. The tie of the decoder mentions the
    C one; it validated against the S one, and every entry point passed. A fresh dump names each
    constant's module, and reads VE/Meaning.lean although nothing imports it."""
    lean = tmp_path / "lean"
    (lean / "VE").mkdir(parents=True)
    shutil.copy(ROOT / "lean/lean-toolchain", lean / "lean-toolchain")
    for name, text in COLLISION.items():
        (lean / name).write_text(text)
    statements, predicates, declarations = lean_statements.dump_all(tmp_path)
    assert "  -- uses VE.Demo.anchor@VE.Decoder VE.Demo.decodeThing@VE.Decoder\n" in statements
    (lean / "statements.txt").write_text(statements)
    (lean / "predicates.txt").write_text(predicates)
    (lean / "declarations.txt").write_text(declarations)
    assert trust_map.predicate_list(lean / "predicates.txt")[1] == {"VE", "VE.Audit", "VE.Decoder", "VE.Meaning"}
    (tmp_path / "tools").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "tools/consolidation-ledger.json").write_text(json.dumps(
        {"steps": [{"step": "all", "title": "", "days": 1, "risk": 1, "removed": [{"module": "*"}]}]}))
    table_path = tmp_path / "tools/trust-classes.json"

    def classes(decoder: dict) -> None:
        table_path.write_text(json.dumps({"modules": {"VE/Meaning.lean": {"S": ["VE.Demo.anchor"]},
                                                      "VE/Decoder.lean": decoder}}))

    # The baseline: the decoder untrusted ([R]), so [V] is zero.
    classes({"C": ["VE.Demo.anchor"], "D[R]": ["VE.Demo.decodeThing"]})
    assert trust_map.main(["--write", "--root", str(tmp_path)]) == 0
    baseline = (tmp_path / "docs/trust-baseline.json").read_text()
    assert json.loads(baseline)["budget"]["V"] == 0
    # The decoder made D[V], tied through the C anchor: rejected by every entry point.
    classes({"C": ["VE.Demo.anchor"], "D[V]": [{"name": "VE.Demo.decodeThing", "tied": ["VE.Demo.decodeThing_tie"]}]})
    capsys.readouterr()
    for flags in ([], ["--check"], ["--write"], ["--ledger"]):
        assert trust_map.main([*flags, "--root", str(tmp_path)]) == 1, flags
        assert "VE.Demo.decodeThing: the statement of VE.Demo.decodeThing_tie mentions no K, S or untied [V]" \
            in capsys.readouterr().err
    assert (tmp_path / "docs/trust-baseline.json").read_text() == baseline
    # With the anchor it mentions classed S, the tie holds.
    classes({"S": ["VE.Demo.anchor"], "D[V]": [{"name": "VE.Demo.decodeThing", "tied": ["VE.Demo.decodeThing_tie"]}]})
    _, problems = trust_map.measure(tmp_path, table_path, lean / "statements.txt")
    assert problems == []


# Fix 4 B: one predicate, `WellFormed`, written in every spelling the old source scanner misread,
# each in its own module (the reviewer's reproducer was `def «WellFormed» : Prop`, which the
# scanner recorded as `VE.Demo.«WellFormed»`, and `def WellFormed(n : Nat)`, recorded as
# `WellFormed(n`). Each body is two lines, as `Plain`'s.
SPELLINGS = {
    "Plain": "namespace VE.Plain\ndef WellFormed (n : Nat) : Prop :=\n  n = n\nend VE.Plain\n",
    "Quoted": "namespace VE.Quoted\ndef «WellFormed» (n : Nat) : Prop :=\n  n = n\nend VE.Quoted\n",
    "Tight": "namespace VE.Tight\ndef WellFormed(n : Nat) : Prop :=\n  n = n\nend VE.Tight\n",
    "Nested": "namespace VE\nnamespace Nested\nsection\nvariable (k : Nat)\ndef WellFormed (n : Nat) : Prop :=\n"
              "  n = k\nend\nend Nested\nend VE\n",
    "Rooted": "def VE.Rooted.WellFormed (n : Nat) : Prop :=\n  n = n\n",
    "Mixed": "namespace VE.Mixed\n@[reducible] protected def «WellFormed»(n:Nat):Prop :=\n  n = n\nend VE.Mixed\n",
}


@pytest.mark.skipif(shutil.which("lake") is None, reason="lake is not on PATH")
def test_compiled_names_do_not_depend_on_spelling(tmp_path, capsys):
    """Every spelling of the predicate is the declaration `VE.<Module>.WellFormed` of the compiled
    module, with the same class, lines and verdict as the plain one in all four entry points."""
    lean = tmp_path / "lean"
    (lean / "VE").mkdir(parents=True)
    shutil.copy(ROOT / "lean/lean-toolchain", lean / "lean-toolchain")
    (lean / "lakefile.toml").write_text(COLLISION["lakefile.toml"])
    (lean / "VE.lean").write_text("".join(f"import VE.{m}\n" for m in SPELLINGS))
    (lean / "VE/Audit.lean").write_text("import VE\n")
    for module, text in SPELLINGS.items():
        (lean / f"VE/{module}.lean").write_text(text)
    statements, predicates, declarations = lean_statements.dump_all(tmp_path)
    for name, text in (("statements", statements), ("predicates", predicates), ("declarations", declarations)):
        (lean / f"{name}.txt").write_text(text)
    assert lean_statements.predicates(lean / "predicates.txt") == {(f"VE.{m}", f"VE.{m}.WellFormed") for m in SPELLINGS}
    (tmp_path / "tools").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "tools/consolidation-ledger.json").write_text(json.dumps(WHOLE_TREE))
    table_path = tmp_path / "tools/trust-classes.json"

    def classes(cls: str, spelled=lambda m: f"VE.{m}.WellFormed") -> None:
        table_path.write_text(json.dumps({"modules": {f"VE/{m}.lean": {cls: [spelled(m)]} for m in SPELLINGS}}))

    def report() -> tuple[list[tuple[str, str, str, int, bool]], list[str]]:
        walked, _, problems = trust_map.walk(tmp_path, table_path, lean / "statements.txt")
        rows = [(d.module, d.decl.name, d.cls, d.decl.lines, d.trusted) for d in walked if d.decl.name]
        return rows, problems

    # Classed S: every spelling is one trusted two-line predicate, and every entry point passes.
    classes("S")
    rows, problems = report()
    assert problems == [] and sorted(rows) == sorted((f"VE/{m}.lean", f"VE.{m}.WellFormed", "S", 2, True) for m in SPELLINGS)
    for flags in ([], ["--write"], ["--check"], ["--ledger"]):
        assert trust_map.main([*flags, "--root", str(tmp_path)]) == 0, flags
    baseline = (tmp_path / "docs/trust-baseline.json").read_text()
    assert json.loads(baseline)["budget"]["S"] == 2 * len(SPELLINGS)
    # Classed C: every spelling fails with the plain one's problem, in every entry point.
    classes("C")
    assert sorted(report()[1]) == sorted(f"VE/{m}.lean: VE.{m}.WellFormed: a predicate cannot be C unless a theorem "
                                         "ties it; classify it K or S (or P for a proof helper)" for m in SPELLINGS)
    # The scanner's spellings name nothing: each entry is stale and the predicate stays trusted.
    for spelled in (lambda m: f"VE.{m}.«WellFormed»", lambda m: f"VE.{m}.WellFormed(n"):
        classes("C", spelled)
        rows, problems = report()
        assert sorted(problems) == sorted(f"trust-classes.json: VE/{m}.lean: {spelled(m)} is not a declaration of that "
                                          "file" for m in SPELLINGS)
        assert all(cls == "?" and trusted for _, _, cls, _, trusted in rows)
    for spelled in (None, lambda m: f"VE.{m}.«WellFormed»"):
        classes("C", *([spelled] if spelled else []))
        capsys.readouterr()
        for flags in ([], ["--check"], ["--write"], ["--ledger"]):
            assert trust_map.main([*flags, "--root", str(tmp_path)]) == 1, flags
            assert "PASS" not in capsys.readouterr().out
    assert (tmp_path / "docs/trust-baseline.json").read_text() == baseline
    # A source edited after the dump fails until the dump is rewritten.
    classes("S")
    (lean / "VE/Quoted.lean").write_text(SPELLINGS["Quoted"].replace("  n = n\n", "  n = n ∧\n  n = n ∧\n  n = n\n"))
    assert report()[1] == ["VE/Quoted.lean: declarations.txt was not compiled from this source; rerun "
                           "tools/lean_statements.py"]
    assert trust_map.main(["--check", "--root", str(tmp_path)]) == 1
    (lean / "declarations.txt").write_text(lean_statements.dump_all(tmp_path)[2])
    assert report()[1] == []
    # The two added lines are S growth.
    assert trust_map.main(["--check", "--root", str(tmp_path)]) == 1
    assert "S grew from 12 to 14" in capsys.readouterr().err


@pytest.mark.skipif(shutil.which("lake") is None, reason="lake is not on PATH")
def test_where_predicate_is_checked_in_a_fresh_dump(tmp_path, capsys):
    """Review B (consolidate-b1d looprecheck 1), the reviewer's reproducer compiled: the decoder
    classed C holds `where WellFormed (n : Nat) : Prop`. Every entry point exited 0 with zero
    trusted lines, and two more predicate lines passed `--check` against the old baseline."""
    lean = tmp_path / "lean"
    (lean / "VE").mkdir(parents=True)
    shutil.copy(ROOT / "lean/lean-toolchain", lean / "lean-toolchain")
    (lean / "lakefile.toml").write_text(COLLISION["lakefile.toml"])
    (lean / "VE.lean").write_text("import VE.Demo\n")
    (lean / "VE/Audit.lean").write_text("import VE\n#print axioms VE.Demo.acceptance\n")
    (tmp_path / "tools").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "tools/consolidation-ledger.json").write_text(json.dumps(WHOLE_TREE))
    table_path = tmp_path / "tools/trust-classes.json"
    baseline_path = tmp_path / "docs/trust-baseline.json"

    def dump(source: str) -> None:
        (lean / "VE/Demo.lean").write_text(source)
        for name, text in zip(("statements", "predicates", "declarations"), lean_statements.dump_all(tmp_path)):
            (lean / f"{name}.txt").write_text(text)

    def classes(decoder: object) -> None:
        table_path.write_text(json.dumps({"modules": {"VE/Demo.lean": decoder}}))

    def entry_points(expected: int, needle: str = "") -> None:
        for flags in ([], ["--write"], ["--check"], ["--ledger"]):
            assert trust_map.main([*flags, "--root", str(tmp_path)]) == expected, flags
            out, err = capsys.readouterr()
            assert needle in err and (expected == 0 or "PASS" not in out and "| Step |" not in out)

    dump(WHERE)
    assert lean_statements.predicates(lean / "predicates.txt") == {("VE.Demo", "VE.Demo.decoder.WellFormed")}
    holding = "VE.Demo.decoder: a declaration holding a predicate (VE.Demo.decoder.WellFormed) cannot be"
    for decoder, how in (({"C": ["VE.Demo.decoder"]}, "C"), ({"D[I]": ["VE.Demo.decoder"]}, "D[I]"),
                         ({"C": [{"name": "VE.Demo.decoder", "tied": ["VE.Demo.acceptance"]}]}, "tied C")):
        classes(decoder)
        capsys.readouterr()
        entry_points(1, f"{holding} {how};")
        assert not baseline_path.exists()
    # Classed S, the decoder's three lines (its predicate's included) are trusted meaning.
    classes({"S": ["VE.Demo.decoder"]})
    entry_points(0)
    assert json.loads(baseline_path.read_text())["budget"]["S"] == 3
    # The predicate grown by two lines is S growth over the baseline; classed C, it fails again.
    dump(WHERE.replace("Prop := n = 0", "Prop :=\n    n = 0 ∧\n    True"))
    assert trust_map.main(["--check", "--root", str(tmp_path)]) == 1
    assert "S grew from 3 to 5" in capsys.readouterr().err
    classes({"C": ["VE.Demo.decoder"]})
    capsys.readouterr()
    for flags in ([], ["--check"], ["--ledger"]):
        assert trust_map.main([*flags, "--root", str(tmp_path)]) == 1, flags
        assert f"{holding} C;" in capsys.readouterr().err


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


SECTION11 = "## 11. Per-module line counts\n"
# The problem trees whose compiled dumps fail; the table plays no part, since `--seed` rewrites it.
DUMP_PROBLEMS = ["predicate list missing", "a file the predicate scan did not read", "predicate list without modules",
                 "source edited after the declaration list", "declaration list missing",
                 "declaration list of another module", "predicate of no declaration",
                 "predicate of a file without declarations", "predicate of a module that is no file",
                 "scanned module that is no file", "generated constant",
                 "generated constant of a file without declarations"]


@pytest.mark.parametrize("name", DUMP_PROBLEMS)
def test_seed_reads_the_dumps_as_every_entry_point_does(tmp_path, name):
    """`--seed` reads the tree through the same pass (`read_tree`, `place_tree`): it refuses every
    dump `walk` refuses, and leaves the table as it was."""
    problem_tree(tmp_path, PROBLEM_TREES[name])
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/TRUST-MAP.md").write_text(SECTION11)
    table = (tmp_path / "tools/trust-classes.json").read_text()
    with pytest.raises(SystemExit, match="cannot seed from compiled dumps that fail"):
        trust_map.main(["--seed", str(tmp_path / "docs/TRUST-MAP.md"), "--root", str(tmp_path)])
    assert (tmp_path / "tools/trust-classes.json").read_text() == table


def add_decl(name: str, type_: str, value: str) -> str:
    """A `run_elab` command adding the definition `name` with `addDecl`: Lean records no source
    range for it."""
    return (f"run_elab do\n  addDecl <| Declaration.defnDecl {{\n    name := `{name}\n    levelParams := []\n"
            f"    type := {type_}\n    value := {value}\n    hints := .abbrev\n    safety := .safe\n  }}\n")


ELAB_HEADER = "import Lean\nopen Lean Elab Command\n"
CONTROL = "namespace VE.Control\ndef checked : Nat := 0\nend VE.Control\n"
# Review B (consolidate-b1 fix 5), the reviewer's reproducer: VE/Demo.lean's only command adds the
# predicate `VE.Demo.WellFormed`, so the module has no ranged declaration; VE/Control.lean adds a
# definition beside a written one. Neither constant has a line of its own.
ADDED = {"VE/Demo.lean": ELAB_HEADER + add_decl("VE.Demo.WellFormed", "mkSort .zero", "mkConst ``True"),
         "VE/Control.lean": ELAB_HEADER + CONTROL + add_decl("VE.Control.decide", "mkConst ``Nat", "mkNatLit 1")}
ADDED_PROBLEMS = sorted([
    "VE/Demo.lean: the predicate VE.Demo.WellFormed is part of no declaration of the file (no source range, and its "
    "name extends none); rerun tools/lean_statements.py",
    *(f"{file}: {name} (def) has no source range and its name extends no constant (a metaprogram such as `run_elab` "
      "or `addDecl` made it): no line of the file can be classified for it"
      for file, name in (("VE/Demo.lean", "VE.Demo.WellFormed"), ("VE/Control.lean", "VE.Control.decide")))])


@pytest.fixture(scope="module")
def added_tree(tmp_path_factory):
    """A compiled tree with the baseline written before the `run_elab` commands were added, and the
    dumps written after."""
    root = tmp_path_factory.mktemp("added")
    lean = root / "lean"
    (lean / "VE").mkdir(parents=True)
    shutil.copy(ROOT / "lean/lean-toolchain", lean / "lean-toolchain")
    (lean / "lakefile.toml").write_text(COLLISION["lakefile.toml"])
    (lean / "VE.lean").write_text("import VE.Demo\nimport VE.Control\n")
    (lean / "VE/Audit.lean").write_text("import VE\n")
    for folder in ("tools", "docs"):
        (root / folder).mkdir()
    (root / "tools/consolidation-ledger.json").write_text(json.dumps(
        {"steps": [{"step": "all", "title": "", "days": 1, "risk": 1, "removed": [{"module": "*"}]}]}))
    (root / "tools/trust-classes.json").write_text(json.dumps({"modules": {"VE/Control.lean": {"C": ["VE.Control.checked"]}}}))
    (root / "docs/TRUST-MAP.md").write_text(SECTION11)

    def dump(sources: dict[str, str]) -> None:
        for path, text in sources.items():
            (lean / path).write_text(text)
        for name, text in zip(("statements", "predicates", "declarations"), lean_statements.dump_all(root)):
            (lean / f"{name}.txt").write_text(text)

    dump({"VE/Demo.lean": ELAB_HEADER, "VE/Control.lean": CONTROL})
    assert trust_map.main(["--write", "--root", str(root)]) == 0
    assert json.loads((root / "docs/trust-baseline.json").read_text())["totals"]["trusted"] == 0
    dump(ADDED)
    declarations = (lean / "declarations.txt").read_text()
    assert "\ngenerated def VE.Demo.WellFormed@VE.Demo\n" in declarations
    assert "\ngenerated def VE.Control.decide@VE.Control\n" in declarations
    assert lean_statements.declaration_list(lean / "declarations.txt")[0]["VE.Demo"] == [
        lean_statements.Declared("VE.Demo.WellFormed", "def", None, None)]
    assert lean_statements.predicates(lean / "predicates.txt") == {("VE.Demo", "VE.Demo.WellFormed")}
    return root


@pytest.mark.skipif(shutil.which("lake") is None, reason="lake is not on PATH")
@pytest.mark.parametrize("flags", [[], ["--write"], ["--check"], ["--ledger"], ["--seed"]])
def test_constants_added_by_a_metaprogram_fail_every_entry_point(added_tree, tmp_path, capsys, flags):
    """Review B (consolidate-b1 fix 5), compiled: the dumps list `VE.Demo.WellFormed` but no ranged
    declaration of VE.Demo, so no file placed the predicate; the default report, `--write`,
    `--check` and `--ledger` exited 0 with zero trusted lines against the unchanged baseline. Each
    entry point now fails on every constant no line of the tree is placed for, and writes nothing."""
    root = tmp_path / "tree"
    shutil.copytree(added_tree, root)
    _, problems = trust_map.measure(root, root / "tools/trust-classes.json", root / "lean/statements.txt")
    assert sorted(problems) == ADDED_PROBLEMS
    baseline, table = (root / "docs/trust-baseline.json").read_text(), (root / "tools/trust-classes.json").read_text()
    capsys.readouterr()
    if flags == ["--seed"]:
        with pytest.raises(SystemExit, match="cannot seed from compiled dumps that fail") as failed:
            trust_map.main(["--seed", str(root / "docs/TRUST-MAP.md"), "--root", str(root)])
        err = str(failed.value)
    else:
        assert trust_map.main([*flags, "--root", str(root)]) == 1
        out, err = capsys.readouterr()
        assert "PASS" not in out and "| Step |" not in out and "wrote" not in out
    assert all(problem in err for problem in ADDED_PROBLEMS)
    assert (root / "docs/trust-baseline.json").read_text() == baseline
    assert (root / "tools/trust-classes.json").read_text() == table


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
    (tmp_path / "lean/predicates.txt").write_text(predicate_file(("VE.Closure.Formula.WellFormed@VE.Closure.Syntax",),
                                                                 ("VE.Closure.Syntax",)))
    (tmp_path / "tools/consolidation-ledger.json").write_text(json.dumps({"steps": [
        {"step": "1", "title": "", "days": 1, "risk": 1,
         "removed": [{"module": module, "names": r"\.Formula\.WellFormed$"}]}]}))
    write_declarations(tmp_path)
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
                          "C": ["VE.Demo.Meaning", "VE.Demo.helper", INSTANCE]},
               "theorem VE.Demo.decodeThing_tie\n  VE.Demo.decodeThing \"\" = 0 ∧ VE.Demo.marker = True.intro\n"
               "  -- uses VE.Demo.decodeThing@VE.Demo VE.Demo.marker@VE.Marker\n  -- expr 1\n",
               modules=("VE.Demo", "VE.Marker"))
    (tmp_path / "lean/VE/Marker.lean").write_text(MARKER)
    write_declarations(tmp_path)
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

KIND_FIXED = {"theorem": "P", "command": "T"}


def unsound(walked: list, table: dict, proved: dict, predicates: set[tuple[str, str]]) -> list[str]:
    """What a report claims that the declarations contradict. This oracle reads only the reported
    classes, each declaration's kind and the statement dump, not the tool's anchor set: a theorem,
    example or command is P or T by its kind and cannot be listed; every other declaration is
    reported in its listed class (or `?`); `trusted` is K, S, `?` or untied [V]; each tying theorem
    mentions the declaration and another one the same report counts as trusted by its class, each
    as the module that defines it (`name@Module`); a predicate is not left untrusted untied."""
    def ident(d) -> tuple[str, str]:
        return d.module.removesuffix(".lean").replace("/", "."), d.decl.name

    reported = {ident(d): d for d in walked if d.decl.name is not None}
    errors = []
    for d in walked:
        name = d.decl.name
        me = ident(d) if name is not None else None
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
                if me not in used or not any(
                        n != me and n in reported and reported[n].trusted and not reported[n].tied
                        and reported[n].cls != "?" for n in used):
                    errors.append(f"{name}: {theorem} ties it to nothing the report counts as trusted")
        if me in predicates and not (counted or d.tied or d.cls in {"P", "T"}):
            errors.append(f"{name}: a predicate reported {d.cls} untied")
        held = [p for p in d.decl.parts if (me[0], p) in predicates] if me else []
        if held and not ((counted and not d.tied) or d.cls in {"P", "T"}):
            errors.append(f"{name}: holds the predicates {held} and is reported {d.cls}{' tied' * d.tied}")
    # Every predicate of the list is reported, as a declaration or a part of one, whether or not
    # its module reports any declaration (consolidate-b1 fix 5).
    placed = {(ident(d)[0], n) for d in walked if d.decl.name is not None for n in (d.decl.name, *d.decl.parts)}
    errors += [f"{p}: a predicate reported nowhere" for p in predicates if p not in placed]
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


def assert_sound_or_rejected(decls, files, table, proved, predicates, label) -> None:
    walked, problems = trust_map.classify_tree(decls, table, proved, predicates, files)
    errors = unsound(walked, table, proved, predicates)
    assert problems or not errors, f"{label}: passed while {errors}"


@pytest.mark.parametrize("name", VALID_TREES)
def test_mutated_fixture_classes_are_reported_or_rejected(tmp_path, name):
    """Every named declaration of a valid fixture tree, alone and in pairs, takes every class
    (untied and tied) or none."""
    problem_tree(tmp_path, VALID_TREES[name])
    decls, files, _, _ = trust_map.scan_tree(tmp_path)
    table = trust_map.load_table(tmp_path / "tools/trust-classes.json")
    proved = trust_map.statements(tmp_path / "lean/statements.txt")
    predicates = trust_map.lean_predicates(tmp_path / "lean/predicates.txt")
    assert not unsound(*trust_map.classify_tree(decls, table, proved, predicates, files)[:1], table, proved, predicates)
    targets = sorted({(m, d.name) for m, d in decls if d.name is not None})
    variants = {t: entry_variants(table.get(t[0], {}).get(t[1]), sorted(proved)) for t in targets}
    for i, (module, decl) in enumerate(targets):
        for variant in variants[module, decl]:
            once = mutate(table, module, decl, variant)
            assert_sound_or_rejected(decls, files, once, proved, predicates, f"{decl}={variant}")
            for module2, decl2 in targets[i + 1:]:
                for variant2 in variants[module2, decl2]:
                    assert_sound_or_rejected(decls, files, mutate(once, module2, decl2, variant2), proved, predicates,
                                             f"{decl}={variant}, {decl2}={variant2}")


@pytest.mark.parametrize("name", ["predicate of no declaration", "predicate of a file without declarations",
                                  "predicate of a module that is no file"])
def test_oracle_sees_every_unplaced_predicate(tmp_path, name):
    """The oracle checks every predicate of the list, not only those of modules that report a
    declaration (consolidate-b1 fix 5: it shared the tool's blind spot), and the tool rejects each
    one it reports nowhere."""
    problem_tree(tmp_path, PROBLEM_TREES[name])
    decls, files, _, _ = trust_map.scan_tree(tmp_path)
    predicates = trust_map.lean_predicates(tmp_path / "lean/predicates.txt")
    table, proved = trust_map.load_table(tmp_path / "tools/trust-classes.json"), {}
    walked, problems = trust_map.classify_tree(decls, table, proved, predicates, files)
    assert [e for e in unsound(walked, table, proved, predicates) if "a predicate reported nowhere" in e] and problems


@pytest.fixture(scope="module")
def committed_tree():
    decls, files, _, _ = trust_map.scan_tree()
    return decls, files, trust_map.load_table(), trust_map.statements(), trust_map.lean_predicates()


def test_mutated_committed_ties_are_reported_or_rejected(committed_tree):
    """Every committed tie and every declaration its theorems mention (its possible anchors) takes
    every class, untied and tied, or none, against the committed dump and the files they live in
    (with those files' table entries and predicates, so the sub-tree is itself a valid tree)."""
    decls, files, table, proved, predicates = committed_tree
    walked, problems = trust_map.classify_tree(decls, table, proved, predicates, files)
    assert problems == [] and not unsound(walked, table, proved, predicates)
    owner = {trust_map.ident(m, d.name): m for m, d in decls if d.name is not None}
    tying = sorted({t for entries in table.values() for e in entries.values() if isinstance(e, dict) for t in e["tied"]})
    targets = sorted({(m, n) for m, entries in table.items() for n, e in entries.items() if isinstance(e, dict)}
                     | {(owner[u], u[1]) for t in tying for u in proved[t] if u in owner})
    assert len(targets) > len(tying)
    files = sorted({m for m, _ in targets})
    decls = [(m, d) for m, d in decls if m in files]
    table = {m: entries for m, entries in table.items() if m in files}
    predicates = {p for p in predicates if p[0] in {lean_statements.module_name(m) for m in files}}
    walked, problems = trust_map.classify_tree(decls, table, proved, predicates, files)
    assert problems == [] and not unsound(walked, table, proved, predicates)
    for module, name in targets:
        for variant in entry_variants(table.get(module, {}).get(name), tying[:1]):
            assert_sound_or_rejected(decls, files, mutate(table, module, name, variant), proved, predicates,
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
                          "C": [INSTANCE]})
    tables = (tmp_path / "tools/trust-classes.json", tmp_path / "lean/statements.txt")
    files, _ = trust_map.measure(tmp_path, *tables)
    baseline_path = tmp_path / "baseline.json"
    trust_map.write_baseline(files, baseline_path, {})
    baseline = json.loads(baseline_path.read_text())
    assert trust_map.check(files, baseline) == []
    write_tree(tmp_path, {"D[V]": ["VE.Demo.decodeThing"], "S": ["VE.Demo.Meaning", "VE.Demo.helper"],
                          "C": [INSTANCE]})
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


def git(root: Path, *args: str) -> None:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env=env)


def test_since_gates_a_change_on_its_own_growth(tmp_path):
    """consolidate-b2 review B: with a stale baseline `--check` fails on growth merged earlier, and a
    change's own growth hid behind it. `--since` measures the parent tree and allows only the
    signed entries the change adds."""
    tables = (tmp_path / "tools/trust-classes.json", tmp_path / "lean/statements.txt")
    write_tree(tmp_path, {"D[R]": ["VE.Demo.decodeThing"], "S": ["VE.Demo.Meaning"], "C": [INSTANCE, "VE.Demo.helper"]})
    stale, _ = trust_map.measure(tmp_path, *tables)
    (tmp_path / "docs").mkdir()
    baseline_path = tmp_path / "docs/trust-baseline.json"
    trust_map.write_baseline(stale, baseline_path, {})
    inherited = {"change": "older", "signed": "DRI", "allow": {"V": 4}}
    baseline_path.write_text(json.dumps({**json.loads(baseline_path.read_text()), "signed": [inherited]}))
    # Earlier work grew S (helper) without a signed entry: the parent already fails `--check`.
    write_tree(tmp_path, {"D[R]": ["VE.Demo.decodeThing"], "S": ["VE.Demo.Meaning", "VE.Demo.helper"],
                          "C": [INSTANCE]})
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-qm", "parent")
    parent, problems, parent_baseline = trust_map.measure_rev("HEAD", tmp_path)
    assert problems == [] and parent_baseline == json.loads(baseline_path.read_text())
    assert parent == trust_map.measure(tmp_path, *tables)[0]
    assert trust_map.check(parent, parent_baseline)
    assert trust_map.since(parent, parent, parent_baseline, parent_baseline) == []
    # This change grows V; the inherited entry is the parent's, not this change's.
    write_tree(tmp_path, {"D[V]": ["VE.Demo.decodeThing"], "S": ["VE.Demo.Meaning", "VE.Demo.helper"],
                          "C": [INSTANCE]})
    grown, _ = trust_map.measure(tmp_path, *tables)
    baseline = json.loads(baseline_path.read_text())
    failures = trust_map.since(grown, parent, baseline, parent_baseline)
    assert len(failures) == 1 and failures[0].startswith("V grew") and "(signed allowance 0)" in failures[0]
    own = {"change": "this change", "signed": "DRI", "allow": {"V": 4}}
    baseline["signed"].append(own)
    assert trust_map.since(grown, parent, baseline, parent_baseline) == []
    assert trust_map.since(grown, parent, {**baseline, "signed": [own, {**own, "allow": {"V": 3}}][1:]},
                           parent_baseline)
    baseline_path.write_text(json.dumps(baseline))
    assert trust_map.main(["--root", str(tmp_path), "--since", "HEAD"]) == 0
    baseline_path.write_text(json.dumps({**baseline, "signed": [inherited]}))
    assert trust_map.main(["--root", str(tmp_path), "--since", "HEAD"]) == 1
    _, problems, _ = trust_map.measure_rev("no-such-commit", tmp_path)
    assert problems and problems[0].startswith("git archive no-such-commit")
    assert trust_map.main(["--root", str(tmp_path), "--since", "no-such-commit"]) == 1


def done_substeps(ledger: dict) -> list[str]:
    """The substeps a ledger title marks done: `2a done`, `1a, 1b done; 1c`."""
    done = []
    for step in ledger["steps"]:
        for clause in re.findall(r"\(([^)]*)\)", step["title"]):
            for part in clause.split(";"):
                if part.strip().endswith(" done"):
                    done += re.findall(r"\d+[a-z]", part)
    return done


def plan_declarations(plan: str, substep: str) -> list[str]:
    """The declarations a plan substep defines: a backticked signature `name args : type` and the
    `def`, `structure`, `theorem` (...) headers of its code blocks."""
    section = re.search(rf"^\*\*{substep}\..*?(?=^\*\*\d+[a-z]\.|^### |\Z)", plan, re.S | re.M)
    assert section, f"no plan section for {substep}"
    text = section.group(0)
    signatures = re.findall(r"`([A-Za-z_][\w.']*)(?: [^`:]*)? : [^`]+`", text)
    headers = re.findall(r"^\s*(?:def|structure|theorem|abbrev|inductive)\s+([A-Za-z_][\w.']*)", text, re.M)
    return signatures + headers


def unresolved(names: list[str], declared: set[str]) -> list[str]:
    return [n for n in names if not any(d == n or d.endswith("." + n) for d in declared)]


def test_plan_declarations_of_a_done_step_exist():
    """consolidate-b2 review B: step 2a was marked done while the plan's `fullLayer` was missing.
    Every declaration a done substep's plan text defines must be a compiled declaration."""
    plan = (ROOT / "docs/CONSOLIDATION-PLAN.md").read_text()
    ledger = json.loads((ROOT / "tools/consolidation-ledger.json").read_text())
    done = done_substeps(ledger)
    assert "2a" in done
    declared = {m[1] for m in re.finditer(r" (\S+)@\S+$", lean_statements.DECLARATIONS.read_text(), re.M)}
    missing = {s: unresolved(plan_declarations(plan, s), declared) for s in done}
    assert plan_declarations(plan, "2a")[:1] == ["fullLayer"]
    assert {s: m for s, m in missing.items() if m} == {}


def test_plan_declaration_check_can_fail():
    plan = "### Step 9\n\n**9a. Demo.**\n1. `missingLayer rv : Layer fol Unit`.\n```lean\ndef Shown : Prop\n```\n"
    assert plan_declarations(plan, "9a") == ["missingLayer", "Shown"]
    assert unresolved(plan_declarations(plan, "9a"), {"VE.Demo.Shown"}) == ["missingLayer"]
    ledger = {"steps": [{"title": "Kit (9a done; 9b)"}, {"title": "Other (9c, 9d done)"}, {"title": "Open"}]}
    assert done_substeps(ledger) == ["9a", "9c", "9d"]


def test_route_runners_go_through_the_composed_layer():
    """consolidate-b2 review B: the runner theorems read the definitions layer composed over the
    flags and literals (`fullLayer`, with its BackgroundSound), not an identity layer of `Intended`."""
    entries = lean_statements.parse(lean_statements.OUTPUT.read_text())
    sound = entries["VE.Route.WireSound.fullLayer_background_sound"]
    assert "VE.Route.BackgroundSound (VE.Route.WireSound.fullLayer rv hd)" in sound
    assert "(List.map Prod.fst (VE.Route.Wire.fullBackground rv))" in sound
    for family in ("runFol", "runClosure"):
        assert f"VE.Route.WireSound.BaseClaim VE.Route.WireSound.{family.removeprefix('run').lower()}Family" \
            in entries[f"VE.Route.WireSound.{family}_certificate_acceptance"]
    for family in ("fol", "closure"):
        assert "VE.Route.WireSound.BaseClaim" in entries[f"VE.Route.RunSound.route_{family}_certificate"]
    assert "VE.Route.WireSound.Runner.background_routeSound" not in entries


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
    statements, predicates, declarations = lean_statements.dump_all()
    assert declarations == lean_statements.DECLARATIONS.read_text(), \
        "lean/declarations.txt is stale: run python3 tools/lean_statements.py"
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
