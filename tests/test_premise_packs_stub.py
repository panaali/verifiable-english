"""Premise-packs spec 2.6 and its stub state what `PacksLabels.lean` proves (pk-1d, one owner of the statement).

The DRI's decision of 2026-10-27 (item 3) replaced the false `legacy_labels_nodup` with
`legacy_labels_nodup_of_actKeys`. The stub's statement must equal the built one after whitespace normalisation, read
by `check_readings_defaults_statements`; the superseded name stays only in spec 2.6's note. The stub cannot be
type-checked on today's tree (pk-1 declares its names), so this text comparison is what follows the built theorem.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
STUB = ROOT / "docs/spec/premise-packs/SpecStubs_pk1.lean"
SPEC = ROOT / "docs/spec/premise-packs.md"
BUILT = ROOT / "lean/VE/NormDefaults/PacksLabels.lean"
MUTANTS = ROOT / "docs/spec/premise-packs/mutants.py"
NAME = "legacy_labels_nodup_of_actKeys"
HK = "(hk : ∀ k ∈ VE.Rights.condKeys R, ':' ∉ k.2.1.toList)"
# The old name, not a longer name that begins with it.
OLD_NAME = re.compile(r"\blegacy_labels_nodup(?![\w']|\.\w)")


def _load(name: str, path: Path):
    sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECK = _load("check_rd", ROOT / "tools/check_readings_defaults_statements.py")


def statements(text: str) -> list[str]:
    return CHECK.declarations(text, statements_only=True).get(("theorem", NAME), [])


def same_statement(stub: str, built: str) -> bool:
    """Exactly one declaration on each side, with one text up to the proof's `:=`."""
    left, right = statements(stub), statements(built)
    return len(left) == 1 and left == right


def edited(text: str, old: str, new: str) -> str:
    """`text` with the first `old` from the theorem on replaced, so the edit lands in the statement."""
    start = text.index(f"theorem {NAME}")
    assert old in text[start:]
    return text[:start] + text[start:].replace(old, new, 1)


def old_name_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if OLD_NAME.search(line)]


def test_the_stub_states_the_built_theorem():
    assert same_statement(STUB.read_text(), BUILT.read_text())
    assert HK in statements(STUB.read_text())[0]


@pytest.mark.parametrize("old, new", [
    # the layouts of the two files
    ("(hw : WellFormedU U = true) (hk", "(hw : WellFormedU U = true)\n    (hk"),
    ("(R : VE.Rights.RightsDoc) (hs", "(R : VE.Rights.RightsDoc)\n    (hs"),
    ("(hs : VE.Rights.WellFormedRights R = true)", "(hs  :\tVE.Rights.WellFormedRights   R = true)"),
    # the proof is not part of the statement
    (".Nodup := sorry\n\n/-- 2.6 (5): assembly", ".Nodup := by\n  simp\n\n/-- 2.6 (5): assembly"),
])
def test_a_layout_or_proof_change_is_accepted(old, new):
    assert same_statement(edited(STUB.read_text(), old, new), BUILT.read_text())


@pytest.mark.parametrize("old, new", [
    # the seeded bug of the item: the stub keeps the old text
    (f" {HK} :", " :"),
    (f"theorem {NAME}", "theorem legacy_labels_nodup"),
    # one token off, each way
    ("':' ∉ k.2.1", "':' ∈ k.2.1"),
    ("k.2.1.toList", "k.2.2.toList"),
    ("k.2.1.toList", "k.1.toList"),
    ("VE.Rights.condKeys R, ':'", "VE.Rights.limKeys R, ':'"),
    ("':' ∉", "';' ∉"),
    ("(hk :", "(hk' :"),
    ("WellFormedRights R = true", "WellFormedRights R = false"),
    ("WellFormedU U = true", "WellFormedU R = true"),
    ("(hs : VE.Rights.WellFormedRights R = true)\n", "(hs : VE.SoftNorms.WellFormedSoft (VE.Rights.correlate R) = true)\n"),
    (".Nodup := sorry\n\n/-- 2.6 (5): assembly", ".length > 0 := sorry\n\n/-- 2.6 (5): assembly"),
    # a hypothesis more, or the order changed
    (f" {HK} :", f" {HK} (hz : U = U) :"),
    ("(hw : WellFormedU U = true) (hk", "(hk"),
    # a gap that is not whitespace normalisation's to close
    ("R = true)\n", "R =true)\n"),
])
def test_a_changed_statement_is_refused(old, new):
    assert not same_statement(edited(STUB.read_text(), old, new), BUILT.read_text())


def test_a_missing_or_doubled_declaration_is_refused():
    text = STUB.read_text()
    built = BUILT.read_text()
    assert not same_statement(text.replace(f"theorem {NAME}", f"theorem {NAME}_x"), built)
    assert not same_statement(text, built.replace(f"theorem {NAME}", f"theorem {NAME}_x"))
    doubled = text + "\n" + "\n".join(line for line in text.splitlines()[162:166]) + "\n"
    assert not same_statement(doubled, built)
    assert not same_statement("", "")


def test_the_superseded_name_stays_only_in_the_spec_note():
    assert old_name_lines(STUB.read_text()) == []
    lines = old_name_lines(SPEC.read_text())
    assert len(lines) == 1 and "It replaces the false `legacy_labels_nodup`" in lines[0]


@pytest.mark.parametrize("line, found", [
    ("`legacy_labels_nodup`", True),
    ("theorem legacy_labels_nodup (U : UDoc)", True),
    ("``legacy_labels_nodup, ``assemble_legacy_soft", True),
    ("the name legacy_labels_nodup.", True),
    (f"`{NAME}`", False),
    ("`legacy_labels_nodup_of_identifiers`", False),
    ("legacy_labels_nodup'", False),
    ("legacy_labels_nodup.foo", False),
    ("my_legacy_labels_nodup", False),
])
def test_the_old_name_is_told_from_its_neighbours(line, found):
    assert bool(old_name_lines(line)) is found


def test_spec_2_6_states_the_hypothesis_and_cites_the_decision():
    text = SPEC.read_text()
    section = text[text.index("### 2.6 The legacy packs"):text.index("### 2.7")]
    flat = CHECK.normal(section)
    assert f"`{NAME}` (stub:157, 163)" in flat
    assert HK in flat
    assert "`cx`" in flat
    assert "DRI decision 2026-10-27, item 3" in flat
    assert "dri-decisions-20261027-featureplan-gates.md" in flat


def test_the_spec_line_references_still_name_the_theorem():
    assert STUB.read_text().splitlines()[162].startswith(f"theorem {NAME} ")


def test_every_stub_mutant_still_applies_and_is_recorded():
    """A mutant whose text left the stub would stop mutants.py, so it must follow the statement."""
    mutants = _load("premise_packs_mutants", MUTANTS)
    text = STUB.read_text()
    for mutant in mutants.MUTANTS:
        for old, _ in mutant["edits"]:
            assert text.count(old) == 1, (mutant["id"], old)
    saved = json.loads((MUTANTS.parent / "mutants.json").read_text())
    assert [(r["id"], r["mutation"]) for r in saved] == [(m["id"], m["mutation"]) for m in mutants.MUTANTS]
    assert all(r["failed"] for r in saved)


def test_the_mutants_of_the_new_statement_reach_it():
    mutants = {m["id"]: m for m in _load("premise_packs_mutants", MUTANTS).MUTANTS}
    assert NAME in mutants["M11"]["mutation"]
    text = STUB.read_text()
    for mutant in ("M18", "M19"):
        changed = text
        for old, new in mutants[mutant]["edits"]:
            changed = changed.replace(old, new)
        assert not same_statement(changed, BUILT.read_text())
