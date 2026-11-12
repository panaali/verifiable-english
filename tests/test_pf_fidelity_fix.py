"""openai-preparedness-fidelity-fix: the T fixes of the use-case audit and the K findings of PLAN section 12.

Each test pins one behaviour the fix claims, read from the case's own modules and saved results: the safeguard acts
carry Table 1's standard and F2/F3's sufficiency, CAPREP asks 3.3's compilation sentence, F11's exception precedes
every F2 rule, RS11 = final stays excluded, every header quotes whole source sentences, and answer-key.json equals
PLAN section 6 cell by cell (the six B-*/MREP cells PLAN 12 item 15 records are repaired).
"""
import hashlib
import json
import re
from pathlib import Path

import pytest

import tests.test_usecase_key_transcription as transcription

REPO = Path(__file__).resolve().parents[1]
PF = REPO / "usecases" / "openai-preparedness"
LEAN_SERVICE = REPO / "lean/.lake/build/bin/ve_service"
NAMES = ("pf_vocabulary", "pf_translation", "build_document", "stage0", "run", "quote_evidence")


def _load():
    import importlib
    import sys
    saved = {name: sys.modules.pop(name) for name in NAMES if name in sys.modules}
    sys.path.insert(0, str(PF))
    sys.path.insert(0, str(PF / "source"))
    try:
        return {name: importlib.import_module(name) for name in NAMES}
    finally:
        sys.path.remove(str(PF / "source"))
        sys.path.remove(str(PF))
        for name in NAMES:
            sys.modules.pop(name, None)
        sys.modules.update(saved)


MODULES = _load()
V, T, B, R = (MODULES[n] for n in ("pf_vocabulary", "pf_translation", "build_document", "run"))
Q = MODULES["quote_evidence"]


@pytest.fixture
def pf(monkeypatch):
    import sys
    for name, module in MODULES.items():
        monkeypatch.setitem(sys.modules, name, module)


def act(predicate):
    return V.environment()["vocabulary"]["predicates"][predicate]["regulated"]["act"]


def blocks_for(predicate):
    """The rule blocks whose norm regulates `predicate`."""
    return [b for b in T.rule_blocks() if json.loads(T.parsed_rule(b.id))["predicate"] == predicate]


# --- PLAN section 6 against answer-key.json, cell by cell ------------------------------------------------------
# The section-6 transcriber is tests/test_usecase_key_transcription.py (one parser for every frozen-key use case).
# PLAN 12 item 15's six B-*/MREP cells, once truncated in the transcription, were repaired by
# reviews/dri-decisions-20261030-usecase-pf-run.md item 1 (usecase-pf-keyfix): no cell is an exception any more.

def test_answer_key_equals_section_6_cell_by_cell():
    """Every answer-key.json cell is its section 6 cell, the six repaired B-*/MREP cells included."""
    assert transcription.mismatches("openai-preparedness") == []


@pytest.mark.parametrize("id_, field, value", [("A-BIO-C-INT/SUF", "key", "SOME(nest)"), ("K13", "soft", None),
                                               ("G9", "key", "SOME(P | scoped)"), ("C6", "key", "NONE")])
def test_the_cell_comparison_catches_one_changed_cell(id_, field, value):
    """A scratch copy with one cell changed (even to a K entry's answer) is caught at that cell alone."""
    key = json.loads((PF / "answer-key.json").read_text(encoding="utf-8"))["items"]
    for item in key:
        if item["id"] == id_:
            item[field] = value
            if value is None:
                item.pop(field)
    assert {m[0] for m in transcription.mismatches("openai-preparedness", key)} == {id_}


# --- The corrected acts and the questions that ask them ---------------------------------------------------------

STANDARD = {"misuse_safeguards": "(Appendix C.1)", "alignment_safeguards": "(Appendix C.2)",
            "security_controls": "(Appendix C.3)"}


def test_table_1_acts_name_the_high_standard(pf):
    """f1 (class 1): the MIS, ALN and SEC acts are safeguards "meeting the High standard" of their appendix."""
    assert set(R.ATOMS["MIS"]) | set(R.ATOMS["ALN"]) <= set(STANDARD) and "security_controls" in R.ATOMS["SEC"]
    for predicate, appendix in STANDARD.items():
        assert "meeting the High standard" in act(predicate), predicate
        users = blocks_for(predicate)
        assert users and all(b.id.startswith("f1-") and "meeting High standard" in b.source and appendix in b.source
                             for b in users), predicate


def test_f2_f3_acts_carry_the_sufficiency(pf):
    """f2, f3 (class 1): SUF asks safeguards that sufficiently minimize the risk, and sufficient controls."""
    assert set(R.ATOMS["SUF"]) == {"safeguards_before_deployment", "safeguards_during_development",
                                   "safeguards_before_internal_use"}
    assert "sufficiently minimizing severe-harm risk" in act("safeguards_before_deployment")
    assert "sufficient safety as well as security controls" in act("safeguards_during_development")
    for name in ("f2-deploy", "f2-deploy-any", "f2-reminder", "f2-reminder-any"):
        block = next(b for b in T.rule_blocks() if b.id == name)
        assert "sufficiently minimize the associated risk of severe harm" in block.source, name
        assert json.loads(T.parsed_rule(name))["predicate"] == "safeguards_before_deployment"


def test_capabilities_report_items_ask_the_compilation_sentence(pf):
    """B-*/CAPREP and K4 ask 3.3's "compiled into a Capabilities Report that is submitted to the SAG", not the
    SAG's review of it."""
    asked = set(R.ATOMS["CAPREP"]) | set(R.K_ITEMS["CAPABILITIES_REPORT"])
    users = [b for p in asked for b in blocks_for(p)]
    assert [b.id for b in users] == ["f7-compile"]
    assert "are compiled into a Capabilities Report that is submitted to the SAG." in users[0].source
    assert "f7-compile" in T.RS0_STATEMENTS


def test_g9_asks_every_safeguard_rule_the_nuclear_one_included(pf):
    assert "nuclear_safeguards" in R.SAFEGUARD_PREDICATES
    assert {json.loads(T.parsed_rule(n))["predicate"] for n in ("f12-nuclear", "f12-nuclear-unscoped")} == {
        "nuclear_safeguards"}


# --- F11's exception and RS11 ----------------------------------------------------------------------------------

def test_f11_exception_precedes_every_f2_deployment_rule(pf):
    """C1 (class 3): under RS5 = exception an F11 rule precedes each rule of F2's two deployment parts."""
    f2 = [n for part in R.COMMITMENTS["F2"][:2] for n in part]
    overridden = {low: high for high, lows in T.PRECEDENCE.items() for low in lows}
    assert set(f2) <= set(overridden)
    for name in f2:
        exception = next(b for b in T.rule_blocks() if b.id == overridden[name])
        assert exception.id.startswith("f11-exception") and exception.when == (("RS5", "exception"),)
        assert json.loads(T.parsed_rule(exception.id))["predicate"] == json.loads(T.parsed_rule(name))["predicate"]
    assert set(R.CLUSTERS["C1"]) >= set(f2) | {"f11-exception", "f11-exception-deploy"}


@pytest.mark.skipif(not LEAN_SERVICE.exists(), reason="the Lean service is not built")
def test_c1_is_conflict_free_on_every_choice(pf):
    R.MUTANT = R.WITHOUT_NARROWING = None
    result = R.conflict("C1")
    assert "undecided" not in result and result["cone"] == ["RS3", "RS5"]
    assert [row["holds"] for row in result["choices"]] == [False] * 4


def test_rs11_final_is_excluded_and_no_rule_of_it_returns(pf):
    """f16-final, f16-process (classes 5, 9): RS11 = final is not offered, and no rule is selected by RS11."""
    assert T.READING_SETS["RS11"] == ("process",) and T.EXCLUDED_READINGS == {"RS11": ("final",)}
    assert B.READINGS["rs11-final"] == ("RS11", {"process": []})
    blocks = T.rule_blocks() + T.read_blocks("facts.d1.ve")
    assert not [b.id for b in blocks if any(s == "RS11" for s, _ in b.when)]
    assert not {"f16-final", "f16-process"} & {b.id for b in blocks}
    assert "decision_reversal" in {json.loads(T.parsed_rule(b.id))["predicate"] for b in blocks
                                   if b.id.startswith("f16-board")}
    plan = (PF / "PLAN.md").read_text(encoding="utf-8")
    assert "**Excluded reading: RS11 = final.**" in plan
    assert "Where necessary, the Board may reverse a decision and/or mandate a revised course of action." in plan


def test_k_entries_are_the_saved_answers():
    """C6 and C-doc are NONE and G9 is SOME(P ∨ scoped) (PLAN 12 items 19, 20); section 6 keeps its cells."""
    saved = json.loads((PF / "results.json").read_text())
    rows = {r["id"]: r for r in saved["comparison"]}
    assert rows["C6"]["ve"] == rows["C-doc"]["ve"] == "NONE"
    g9 = saved["items"]["G9"]["choices"]
    assert g9 and all(row["holds"] == (row["choice"]["RS4"] == "P" or row["choice"]["RS4s"] == "scoped")
                      for row in g9)
    for id_ in ("C6", "C-doc", "G9"):
        assert rows[id_]["cause"]["kind"] == "key finding"
    plan = (PF / "PLAN.md").read_text(encoding="utf-8")
    assert "19. **Key finding (K): C6 and C-doc are NONE" in plan and "20. **Key finding (K): G9 is SOME(P ∨ scoped)" in plan


# --- Class 11: whole source sentences ---------------------------------------------------------------------------

def test_every_header_quotes_whole_source_text(pf):
    blocks = Q.blocks()
    evidence = json.loads(Q.EVIDENCE.read_text())
    assert evidence == {"source_sha256": B.TEXT_SHA256, "quotes": Q.fingerprint(blocks)}
    assert len(evidence["quotes"]) == len(blocks)
    assert all(Q.quotes(block) and all("…" not in q for q in Q.quotes(block)) for block in blocks)
    if B.DEFAULT_SOURCE.exists():
        source = B.DEFAULT_SOURCE.read_bytes()
        B.check_source(source)
        assert Q.quote_faults(blocks, source.decode()) == []


def test_a_cut_altered_or_missing_quote_is_a_fault():
    source = "We will review and potentially update the Pre- paredness Framework for continued sufficiency.\n"
    good = T.Block("good", (), "A: “We will review and potentially update the Preparedness Framework for "
                                        "continued sufficiency.”", "")
    cut = T.Block("cut", (), "A: “We will review … continued sufficiency.”", "")
    altered = T.Block("altered", (), "A: “We will review the Preparedness Framework.”", "")
    none = T.Block("none", (), "A: a paraphrase", "")
    assert Q.quote_faults([good, cut, altered, none], source) == [
        ("cut", "We will review … continued sufficiency."), ("altered", "We will review the Preparedness Framework."),
        ("none", None)]


# Review F1: an anchored fact block made its whole source unit CHECKED without the word map a CHECKED rule needs.
# The class: no placement kind (rule or fact) reaches CHECKED unless CHECKED_CLAUSES maps every word of its unit.
CL_LEVELS_UNIT = "p15-u245"


def _spans():
    return {r["id"]: r for r in json.loads((PF / "spans.json").read_text())["units"]}


def test_every_checked_unit_is_a_rule_or_fact_with_a_complete_word_map(pf):
    checked = [r for r in _spans().values() if r["status"] == "CHECKED"]
    assert checked
    for r in checked:
        blocks = [r["rule"]] if "rule" in r else r.get("premises", [])
        assert blocks and all(b in B.CHECKED_CLAUSES for b in blocks), r
    assert set(B.FACT_ANCHORS) <= set(B.CHECKED_CLAUSES)


def test_change_log_removal_of_low_and_medium_is_a_blocked_unit(pf):
    unit = _spans()[CL_LEVELS_UNIT]
    assert unit["status"] == "UNFORMALISED" and unit["blocked_rule"] == "cl-levels", unit
    assert unit["residual"] == "unmapped_duty-p15-u245-b1881efef95f"  # main's residual id is kept
    assert "cl-levels" not in B.FACT_ANCHORS and "cl-levels" not in B.CHECKED_CLAUSES
    # The block's own header quotes the sentence; its "because" clause has no element in the facts.
    header = next(b.source for b in T.read_blocks("facts.d1.ve") if b.id == "cl-levels")
    sentence = re.search(r"(Also, we are removing terms.*?Preparedness work\.)", header)[1].encode()
    assert not B._complete_clause_map("cl-levels", sentence)


def test_a_partial_fact_word_map_is_not_complete(pf, monkeypatch):
    assert B._complete_clause_map("bio-high", b"[High]")
    assert not B._complete_clause_map("bio-high", b"[High] The model can provide")
    monkeypatch.setitem(B.CHECKED_CLAUSES, "bio-high", (("High", "fact", "is critical"),))
    assert not B._complete_clause_map("bio-high", b"[High]")


def test_a_fact_anchored_on_a_partly_translated_unit_is_blocked(pf, monkeypatch):
    if B.DEFAULT_SOURCE.exists():
        source = B.DEFAULT_SOURCE.read_bytes()
        B.check_source(source)
        _, records = B.build(source)
        by_id = {r["id"]: r for r in records}
        for block in B.FACT_ANCHORS:
            assert any(r.get("premises") == [block] for r in records), block
        assert by_id[CL_LEVELS_UNIT]["blocked_rule"] == "cl-levels"
        # The F1 bug, replanted: anchor cl-levels as a fact again.
        placements = {k: v for k, v in B.PLACEMENTS.items() if v[1] != "cl-levels"}
        monkeypatch.setattr(B, "PLACEMENTS", placements)
        monkeypatch.setitem(B.FACT_ANCHORS, "cl-levels", "Also, we are removing terms")
        _, replanted = B.build(source)
        unit = next(r for r in replanted if r["id"] == CL_LEVELS_UNIT)
        assert unit["kind"] == "unformalised" and "premises" not in unit, unit
        assert unit["blocked_rule"] == "cl-levels" and unit["residual"] == by_id[CL_LEVELS_UNIT]["residual"]
    # The same placement gate is exercised on every runner, including those without the licensed source.
    synthetic = b"Also, we are removing terms low and medium because this changes Preparedness work."
    monkeypatch.setattr(B, "check_source", lambda source: None)
    monkeypatch.setattr(B, "PLACEMENTS", {})
    monkeypatch.setattr(B, "FACT_ANCHORS", {"cl-levels": "Also, we are removing terms"})
    _, replanted = B.build(synthetic)
    assert len(replanted) == 1
    unit = replanted[0]
    assert unit["kind"] == "unformalised" and "premises" not in unit, unit
    assert unit["blocked_rule"] == "cl-levels"
    assert unit["residual"] == f"unmapped_duty-p1-u1-{hashlib.sha256(synthetic).hexdigest()[:12]}"


def test_every_blocked_reason_has_one_named_family(pf):
    # BLOCKER_DETAIL owns each reason's family; a reason missing from it cannot be placed (the replanted F1 hit one).
    assert set(B.BLOCKED_RULE_REASONS.values()) <= set(B.BLOCKER_DETAIL)
    assert not hasattr(B, "BLOCKER_FAMILY")
