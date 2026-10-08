"""The RD-1 declarations against the approved text of docs/spec/readings-defaults.md 6.2."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _checker():
    spec = importlib.util.spec_from_file_location("check_rd", ROOT / "tools/check_readings_defaults_statements.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _approved_names():
    return sorted(_checker().approved())


def test_rd1_statements_match_the_approved_text(capsys):
    checker = _checker()
    assert checker.main() == 0
    out = capsys.readouterr().out
    assert "checked 31 approved RD-1 declarations (10 theorems)" in out
    # Review B2: the DRI approved `attached_fillDoc`'s added hypothesis; 6.2 states it, so nothing is pending.
    assert checker.PENDING == {}
    assert "0 pending" in out


def test_the_definitions_are_compared_too():
    """Review B2: the 6.2 definitions, not only the theorems, are read from the spec block and compared."""
    names = {name for kind, name in _checker().approved() if kind == "def"}
    assert {"AchievesU", "fillDoc", "fillNamesFree", "normsShaped", "WellFormedND"} <= names


def _mutate(source, kind, name, checker):
    """`source` with the Lean declaration `kind name` changed at the end of its compared text."""
    import re
    start = re.search(rf"^{kind} {re.escape(name)}\b", source, re.M)
    line_end = source.find("\n", start.end())
    stop = checker.STOP.search(source, line_end + 1)
    text = source[start.start():stop.start()]
    if kind == "theorem":
        head, proof = text.split(":=", 1)
        changed = head.rstrip() + " ∧ True :=" + proof
    else:
        changed = text.rstrip() + " ∧ True\n"
    return source[:start.start()] + changed + source[stop.start():]


@pytest.mark.parametrize("kind, name", _approved_names(), ids=lambda v: str(v))
def test_rd1_checker_fails_on_every_changed_declaration(tmp_path, capsys, kind, name):
    """Each declaration of the spec block, changed in Lean, fails the check by name (checklist 13: the check can
    fail on every item it lists)."""
    checker = _checker()
    path = tmp_path / "Unspecified.lean"
    path.write_text(_mutate(checker.SOURCE.read_text(), kind, name, checker))
    checker.SOURCE = path
    assert checker.main() == 1
    assert f"{name}: {kind} differs" in capsys.readouterr().out


def test_rd1_checker_fails_on_a_dropped_hypothesis(tmp_path, capsys):
    checker = _checker()
    source = checker.SOURCE.read_text()
    mutated = source.replace("(hn : normsShaped N.D = true) (hf : fillNamesFree N = true) (s : String) (i : Nat) :",
                             "(hf : fillNamesFree N = true) (s : String) (i : Nat) :", 1)
    assert mutated != source
    path = tmp_path / "Unspecified.lean"
    path.write_text(mutated)
    checker.SOURCE = path
    assert checker.main() == 1
    assert "fillDoc_one: theorem differs" in capsys.readouterr().out


def test_rd1_checker_fails_on_the_first_approved_attached_statement(tmp_path, capsys):
    """Review B2: the statement without `singlyAttached` (false, F-ND11) is no longer accepted as pending."""
    checker = _checker()
    source = checker.SOURCE.read_text()
    restored = source.replace("(hs : singlyAttached N.D = true) (u : String)", "(u : String)", 1)
    assert restored != source
    path = tmp_path / "Unspecified.lean"
    path.write_text(restored)
    checker.SOURCE = path
    assert checker.main() == 1
    assert "attached_fillDoc: theorem differs" in capsys.readouterr().out


def test_rd1_checker_fails_when_a_pending_entry_is_stale(capsys):
    checker = _checker()
    checker.PENDING = {"attached_fillDoc": "seeded"}
    assert checker.main() == 1
    assert "attached_fillDoc: listed as pending but matches the approved text" in capsys.readouterr().out


def test_rd1_checker_fails_on_a_missing_declaration(tmp_path, capsys):
    checker = _checker()
    path = tmp_path / "Unspecified.lean"
    path.write_text(checker.SOURCE.read_text().replace("def fillHolds ", "private def fillHolds ", 1))
    checker.SOURCE = path
    assert checker.main() == 1
    assert "fillHolds: expected one Lean def, found 0" in capsys.readouterr().out


# RD-2a: spec 6.3, its declarations placed in three files by 6.1.

def test_rd2a_statements_match_the_approved_text(capsys):
    checker = _checker()
    assert checker.main_rd2a() == 0
    out = capsys.readouterr().out
    assert "checked 16 approved RD-2a declarations (5 theorems)" in out
    assert checker.PENDING_RD2A == {} and "0 pending" in out


def _rd2a_names():
    return sorted(_checker().approved_rd2a())


def _with_sources(checker, tmp_path, edit):
    """The checker reading copies of RD-2a's sources, `edit` applied to their text."""
    copies = []
    for source in checker.SOURCES_RD2A:
        path = tmp_path / source.name
        path.write_text(edit(source.read_text()))
        copies.append(path)
    checker.SOURCES_RD2A = copies


@pytest.mark.parametrize("kind, name", _rd2a_names(), ids=lambda v: str(v))
def test_rd2a_checker_fails_on_every_changed_declaration(tmp_path, capsys, kind, name):
    """Each declaration of the 6.3 block, changed in Lean (a body-less one in its signature), fails by name."""
    import re
    checker = _checker()

    def edit(text):
        if not re.search(rf"^{kind} {re.escape(name)}\b", text, re.M):
            return text
        if kind == "def" and ":=" not in checker.approved_rd2a()[(kind, name)][0]:
            # a signature: the result type gains a conjunct before the body
            start = re.search(rf"^{kind} {re.escape(name)}\b", text, re.M)
            body = text.index(" :=", start.end())
            return text[:body] + " × Unit" + text[body:]
        return _mutate(text, kind, name, checker)
    _with_sources(checker, tmp_path, edit)
    assert checker.main_rd2a() == 1
    assert f"{name}: {kind} differs" in capsys.readouterr().out


def test_rd2a_checker_fails_on_a_dropped_hypothesis_and_a_missing_declaration(tmp_path, capsys):
    checker = _checker()
    _with_sources(checker, tmp_path, lambda t: t.replace(
        "    (hcf : VE.NormDefaults.Wire.conflictFreeCheckU (choiceU x.r.N x.c) x.certs = true) :\n", " :\n", 1))
    assert checker.main_rd2a() == 1
    assert "readings_wire_nd_choice_entails: theorem differs" in capsys.readouterr().out
    checker = _checker()
    _with_sources(checker, tmp_path, lambda t: t.replace("def ndChoiceText ", "private def ndChoiceText ", 1))
    assert checker.main_rd2a() == 1
    assert "ndChoiceText: expected one Lean def, found 0" in capsys.readouterr().out


# ---------------------------------------------------------------------------------------------------------------
# RD-6a: lean/VE/Readings/SupExtra.lean against 6.7

RD6B = ["fill_transfers", "nd_superpose_all", "nd_superpose_conflict_free"]


def _approved_6a_names():
    return sorted(key for key in _checker().approved_6a() if key[1] not in RD6B)


def _run_6a(tmp_path, source, checker=None):
    checker = checker or _checker()
    path = tmp_path / "SupExtra.lean"
    path.write_text(source)
    checker.SOURCE_6A = path
    return checker, checker.main()


def test_rd6a_statements_match_the_approved_text(capsys):
    checker = _checker()
    assert checker.main() == 0
    out = capsys.readouterr().out
    assert "checked 7 approved RD-6a declarations (4 theorems)" in out
    assert f"not built yet (a later batch): {', '.join(RD6B)}" in out
    assert ("RD-6a PASS: 7 exact after whitespace normalization (1 amended by a DRI ruling, its original refuted in "
            "Lean); 0 pending the statement re-review") in out
    assert ("superpose_all_extra: amended by DRI ruling 2026-10-07, refuted original mechanised "
            "(superpose_all_extra_refuted)") in out
    # Finding B1 of rd-6a-looprecheck1: the DRI ruling replaced the re-review, so nothing is pending.
    assert checker.PENDING_6A == checker.EDITS_6A == {}
    assert set(checker.AMENDED_6A) == {"superpose_all_extra"}
    assert checker.LATER_6A == set(RD6B)


@pytest.mark.parametrize("kind, name", _approved_6a_names(), ids=lambda v: str(v))
def test_rd6a_checker_fails_on_every_changed_declaration(tmp_path, capsys, kind, name):
    """Each RD-6a declaration of 6.7, changed in Lean, fails by name, the pending one included (its pending edit
    is exact)."""
    checker = _checker()
    checker, code = _run_6a(tmp_path, _mutate(checker.SOURCE_6A.read_text(), kind, name, checker), checker)
    assert code == 1
    out = capsys.readouterr().out
    expected = "is not the approved text with the edit of DRI ruling 2026-10-07" if name in checker.AMENDED_6A \
        else f"{kind} differs"
    assert f"{name}: {expected}" in out


def test_rd6a_checker_fails_on_the_approved_all_statement(tmp_path, capsys):
    """The approved `superpose_all_extra` (without `hQw`, false: fixture X1) fails: the amendment requires `hQw`."""
    checker = _checker()
    source = checker.SOURCE_6A.read_text()
    restored = source.replace("(hQw : VE.Compose.SlotWellFormed (correlate (sup D).1) Q)\n    ", "", 1)
    assert restored != source
    checker, code = _run_6a(tmp_path, restored, checker)
    assert code == 1
    assert ("superpose_all_extra: is not the approved text with the edit of DRI ruling 2026-10-07"
            in capsys.readouterr().out)


# Finding B1 of rd-6a-looprecheck1: an amended declaration passes only with its original refuted in Lean.

def _run_refutations(tmp_path, source, checker=None, audit=None):
    checker = checker or _checker()
    path = tmp_path / "SupExtraExamples.lean"
    path.write_text(source)
    checker.REFUTATIONS_6A = path
    if audit is not None:
        audit_path = tmp_path / "Audit.lean"
        audit_path.write_text(audit)
        checker.AUDIT = audit_path
    return checker, checker.main()


PROPOSITION_MUTANTS = {
    "a binder dropped": ("(hcf : ConflictFreeP.{u} (correlate (sup D).1) (slotUnder D A ++ Q))\n    ", ""),
    "the built hypothesis added": ("(hq : Transfers.{u} D Q Q')\n",
                                   "(hq : Transfers.{u} D Q Q') (hQw : VE.Compose.SlotWellFormed (correlate (sup D).1) Q)\n"),
    "a binder weakened": ("(hc : Compatible D c)", "(hc : True)"),
    "the conclusion changed": ("  φ.denote (expand (choiceDoc D c).1 B) []\n\n/-- The approved proposition",
                               "  ¬ φ.denote (expand (choiceDoc D c).1 B) []\n\n/-- The approved proposition"),
    "renamed": ("def SuperposeAllExtraApproved : Prop", "def SuperposeAllExtraApproved' : Prop"),
}


@pytest.mark.parametrize("mutant", sorted(PROPOSITION_MUTANTS))
def test_rd6a_amendment_fails_when_the_refuted_proposition_is_not_the_approved_statement(tmp_path, capsys, mutant):
    checker = _checker()
    source = checker.REFUTATIONS_6A.read_text()
    old, new = PROPOSITION_MUTANTS[mutant]
    assert source.count(old) == 1
    checker, code = _run_refutations(tmp_path, source.replace(old, new), checker)
    assert code == 1
    assert ("superpose_all_extra: SuperposeAllExtraApproved is not the approved statement as one proposition"
            in capsys.readouterr().out)


@pytest.mark.parametrize("old, new", [
    ("theorem superpose_all_extra_refuted ", "theorem superpose_all_extra_refuted' "),
    ("¬ SuperposeAllExtraApproved.{0} := by", "¬ False := by"),
    ("¬ SuperposeAllExtraApproved.{0} := by", "SuperposeAllExtraApproved.{0} → True := by"),
], ids=["missing", "other conclusion", "not a negation"])
def test_rd6a_amendment_fails_without_the_refutation(tmp_path, capsys, old, new):
    checker = _checker()
    source = checker.REFUTATIONS_6A.read_text()
    assert source.count(old) == 1
    checker, code = _run_refutations(tmp_path, source.replace(old, new), checker)
    assert code == 1
    assert ("superpose_all_extra: no one theorem superpose_all_extra_refuted concluding ¬ SuperposeAllExtraApproved"
            in capsys.readouterr().out)


def test_rd6a_amendment_fails_when_the_refutation_is_not_audited(tmp_path, capsys):
    checker = _checker()
    entry = "#print axioms VE.Readings.SupExtraExamples.superpose_all_extra_refuted\n"
    audit = checker.AUDIT.read_text()
    assert audit.count(entry) == 1
    checker, code = _run_refutations(tmp_path, checker.REFUTATIONS_6A.read_text(), checker,
                                     audit.replace(entry, "-- " + entry))
    assert code == 1
    assert "superpose_all_extra: superpose_all_extra_refuted is not audited in Audit.lean" in capsys.readouterr().out


def test_rd6a_a_declaration_cannot_be_both_pending_and_amended(capsys):
    checker = _checker()
    checker.PENDING_6A = {"superpose_all_extra": "seeded"}
    assert checker.main() == 1
    assert "superpose_all_extra: listed as both pending and amended" in capsys.readouterr().out


def test_signature_reads_binders_by_bracket_depth():
    """A `:` or a nested bracket inside a binder does not end the binders."""
    checker = _checker()
    text = "theorem t (a : Nat) {b : List (Nat × Nat)} [inst : DecidableEq α] (h : ∀ x ∈ b, (x.1 : Nat) = 0) : a = a"
    assert checker.signature(text) == (
        "(a : Nat) {b : List (Nat × Nat)} [inst : DecidableEq α] (h : ∀ x ∈ b, (x.1 : Nat) = 0)", "a = a")
    with pytest.raises(ValueError):
        checker.signature("theorem t (a : Nat a = a")
    with pytest.raises(ValueError):
        checker.signature("theorem t (a : Nat) a = a")


def test_rd6a_checker_fails_on_a_missing_declaration(tmp_path, capsys):
    checker = _checker()
    source = checker.SOURCE_6A.read_text().replace("theorem transfers_nil ", "theorem transfers_nil' ", 1)
    checker, code = _run_6a(tmp_path, source, checker)
    assert code == 1
    assert "transfers_nil: expected one Lean theorem, found 0" in capsys.readouterr().out


def test_rd6a_checker_compares_an_rd6b_declaration_once_built(tmp_path, capsys):
    """A later (RD-6b) declaration in the file is compared: the approved text passes, a changed one fails."""
    checker = _checker()
    spec_text = checker.SPEC.read_text().split("### 6.7 RD-6a", 1)[1].split("```lean", 1)[1].split("```", 1)[0]
    start = spec_text.index("theorem fill_transfers")
    stop = spec_text.index("theorem nd_superpose_conflict_free")
    statement = spec_text[start:stop].rstrip() + " := by\n  sorry\n"
    source = checker.SOURCE_6A.read_text().replace("end Extra", statement + "\nend Extra", 1)
    checker, code = _run_6a(tmp_path, source, checker)
    assert code == 0
    out = capsys.readouterr().out
    assert "checked 8 approved RD-6a declarations (5 theorems)" in out
    assert "not built yet (a later batch): nd_superpose_all, nd_superpose_conflict_free" in out
    changed = source.replace("(hs : superposable (fillDoc N) = true) (hsu", "(hsu", 1)
    checker, code = _run_6a(tmp_path, changed)
    assert code == 1
    assert "fill_transfers: theorem differs" in capsys.readouterr().out


# ---------------------------------------------------------------------------------------------------------------
# RD-3: lean/VE/Readings/Verdicts.lean and VerdictsWire.lean against 6.4 and 6.5

def test_rd3_statements_match_the_approved_text(capsys):
    checker = _checker()
    assert checker.main_rd3() == 0
    out = capsys.readouterr().out
    assert "checked 30 approved RD-3 declarations (11 theorems)" in out
    assert checker.PENDING_RD3 == {} and "RD-3 PASS: 30 exact" in out


def _rd3_names():
    return sorted(_checker().approved_rd3())


def _with_rd3_sources(checker, tmp_path, edit):
    copies = []
    for source in checker.SOURCES_RD3:
        path = tmp_path / source.name
        path.write_text(edit(source.read_text()))
        copies.append(path)
    checker.SOURCES_RD3 = copies


@pytest.mark.parametrize("kind, name", _rd3_names(), ids=lambda v: str(v))
def test_rd3_checker_fails_on_every_changed_declaration(tmp_path, capsys, kind, name):
    """Each declaration of the 6.4 and 6.5 blocks, changed in Lean (a body-less one in its signature), fails by
    name."""
    import re
    checker = _checker()

    def edit(text):
        if not re.search(rf"^{kind} {re.escape(name)}\b", text, re.M):
            return text
        approved = checker.approved_rd3()[(kind, name)][0]
        if kind == "def" and ":=" not in approved and "| ." not in approved:  # `Holds` is defined by cases
            start = re.search(rf"^{kind} {re.escape(name)}\b", text, re.M)
            body = text.index(" :=", start.end())
            return text[:body] + " × Unit" + text[body:]
        return _mutate(text, kind, name, checker)
    _with_rd3_sources(checker, tmp_path, edit)
    assert checker.main_rd3() == 1
    assert f"{name}: {kind} differs" in capsys.readouterr().out


def test_rd3_checker_fails_on_a_dropped_hypothesis_and_a_missing_declaration(tmp_path, capsys):
    checker = _checker()
    _with_rd3_sources(checker, tmp_path, lambda t: t.replace(
        "(hA : ∃ c, Compatible D c ∧ ∀ x ∈ A, x ∈ c)\n    (l : String) :", "\n    (l : String) :", 1))
    assert checker.main_rd3() == 1
    assert "restrictionsFor_spec: theorem differs" in capsys.readouterr().out
    checker = _checker()
    _with_rd3_sources(checker, tmp_path, lambda t: t.replace("def foldPremises ", "private def foldPremises ", 1))
    assert checker.main_rd3() == 1
    assert "foldPremises: expected one Lean def, found 0" in capsys.readouterr().out
