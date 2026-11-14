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

import tests.omission_rule as omission_rule
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
    assert "sufficient additional safety plus security controls" in act("safeguards_during_development")
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
    blocks = T.rule_blocks() + T.fact_blocks()
    assert not [b.id for b in blocks if any(s == "RS11" for s, _ in b.when)]
    assert not {"f16-final", "f16-process"} & {b.id for b in blocks}
    assert "decision_reversal" in {json.loads(T.parsed_rule(b.id))["predicate"] for b in blocks
                                   if b.id.startswith("f16-board")}
    plan = (PF / "PLAN.md").read_text(encoding="utf-8")
    assert "**Excluded reading: RS11 = final.**" in plan
    assert "Where necessary, the Board may reverse a decision and/or mandate a revised course of action." in plan


def test_k_entries_are_the_saved_answers():
    """C6 and C-doc are NONE (PLAN 12 item 19); G9 is NONE (item 20 as amended by item 25: C.2's duty, unguarded
    under both RS9 choices, binds G9's model too); section 6 keeps its cells."""
    saved = json.loads((PF / "results.json").read_text())
    rows = {r["id"]: r for r in saved["comparison"]}
    assert rows["C6"]["ve"] == rows["C-doc"]["ve"] == rows["G9"]["ve"] == "NONE"
    g9 = saved["items"]["G9"]["choices"]
    assert g9 and not any(row["holds"] for row in g9)
    assert "item 25 amends item 20" in rows["G9"]["cause"]["reason"]
    for id_ in ("C6", "C-doc", "G9"):
        assert rows[id_]["cause"]["kind"] == "key finding"
    plan = (PF / "PLAN.md").read_text(encoding="utf-8")
    assert "19. **Key finding (K): C6 and C-doc are NONE" in plan and "20. **Key finding (K): G9 is SOME(P ∨ scoped)" in plan
    assert "**Amends item 20 (not rewritten; DRI ruling of 2026-11-13):** G9's VE answer is NONE" in " ".join(plan.split())


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
    header = next(b.source for b in T.fact_blocks() if b.id == "cl-levels")
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


# --- openai-preparedness-fidelity-fix-2: the 12 units the whole-document pass failed (PLAN 12 item 23) -----------
# Each test pins one claimed fix; the selection tests ask VE (soft-norms@0) on a case model built by run.atoms.

needs_lean = pytest.mark.skipif(not LEAN_SERVICE.exists(), reason="the Lean service is not built")


def legend(predicate):
    return V.environment()["vocabulary"]["predicates"][predicate]["description"]


def rule(block_id):
    return json.loads(T.parsed_rule(block_id))


def selections(reading, case, predicate, sign=True):
    """The rules VE selects for `predicate` on the case model, under both completion defaults."""
    choice = {**R.BASE, **reading}
    names, found = tuple(sorted(choice.items())), R.atoms(case, choice)
    picked = [set(R.selected(R.document(names, d), found, predicate, sign)) for d in ("deny", "allow")]
    assert picked[0] == picked[1]
    return picked[0]


def key_item(id_):
    return next(k for k in json.loads((PF / "answer-key.json").read_text())["items"] if k["id"] == id_)


def test_f3_internal_use_is_its_own_act_and_both_legends_say_additional(pf):
    """f3-develop-inuse(-forecast) (classes 1, 4): under RS18 = inuse the heading's internal use has its own act,
    "before internal use"; the development blocks name development only; both legends keep 4.4's wording."""
    for name in ("f3-inuse", "f3-inuse-forecast"):
        assert rule(name)["predicate"] == "safeguards_before_internal_use"
        assert "internal_deployment" in json.dumps(rule(name)["guard"])
        assert next(b for b in T.rule_blocks() if b.id == name).when == (("RS18", "inuse"),)
    for name in ("f3-develop-inuse", "f3-develop-inuse-forecast"):
        assert rule(name)["predicate"] == "safeguards_during_development"
        assert "internal_deployment" not in json.dumps(rule(name)["guard"])
    assert act("safeguards_before_internal_use").endswith("before internal use")
    assert "during development" not in act("safeguards_before_internal_use")
    for predicate in ("safeguards_before_internal_use", "safeguards_during_development"):
        assert "additional safeguards (safety and security controls)" in legend(predicate)
    assert B.READINGS["rs18-develop"][1]["inuse"] == ["f3-develop-inuse", "f3-develop-inuse-forecast", "f3-inuse",
                                                      "f3-inuse-forecast"]
    assert "safeguards_before_internal_use" in R.ATOMS["SUF"] and "f3-inuse" in R.N1_RULES


@needs_lean
def test_f3_internal_deployment_selects_the_internal_use_act_only(pf):
    for case, block in (({"id": "t", "levels": ["BIO-C"], "activity": "INT", "findings": {}}, "f3-inuse"),
                        ({"id": "t", "levels": [], "activity": "INT", "findings": {"OT10": True}}, "f3-inuse-forecast")):
        reading = {"RS18": "inuse", "RS2": "sep", "RS3": "ext"}
        assert selections(reading, case, "safeguards_before_internal_use") == {block}
        assert selections(reading, case, "safeguards_during_development") == set()
        assert selections({**reading, "RS18": "devonly"}, case, "safeguards_before_internal_use") == set()


TWO_AREAS = {"id": "t", "levels": ["BIO-H", "CYB-H"], "activity": "EXT", "findings": {"OT12": True},
             "extra": ["adjustment_conditions"], "relations": [["adjustment_area", "s", "biological_and_chemical"]]}
ONE_AREA = {**TWO_AREAS, "levels": ["BIO-H"]}
EXCEPTION = {"RS5": "exception", "RS3": "ext"}


def test_f11_exception_guards_name_the_capability_area(pf):
    """f11-exception(-deploy) (classes 2, 7): each releases only where a reached level is in the confirmed area,
    unless a reached level is in no confirmed area."""
    for name in ("f11-exception", "f11-exception-deploy"):
        data = rule(name)
        assert "adjustment_area" in json.dumps(data["guard"]) and "adjustment_area" in json.dumps(data["unless"])
        assert "in_category" in json.dumps(data["unless"])
        assert "that capability area" in legend("adjustment_area")
    assert R.WITNESS_RELATIONS["C1"] == (("adjustment_area", "s", "biological_and_chemical"),)


@needs_lean
def test_one_areas_adjustment_does_not_release_another_areas_duty(pf):
    """C1's sentence: "the level of safeguards that we require in that capability area"."""
    assert selections(EXCEPTION, ONE_AREA, "safeguards_before_deployment", sign=False) == {"f11-exception"}
    assert "f11-exception" not in selections(EXCEPTION, TWO_AREAS, "safeguards_before_deployment", sign=False)
    assert "f2-deploy" in selections(EXCEPTION, TWO_AREAS, "safeguards_before_deployment")


@needs_lean
def test_the_deploy_exception_permits_only_inside_the_confirmed_area(pf):
    assert selections(EXCEPTION, ONE_AREA, "deployment_permitted") == {"f11-exception-deploy"}
    assert selections(EXCEPTION, TWO_AREAS, "deployment_permitted") == set()
    assert "f2-no-deploy" in selections(EXCEPTION, TWO_AREAS, "deployment_permitted", sign=False)


def test_f6_guard_names_footnote_6s_three_methods(pf):
    """f6-rel (class 3): the guard is a model OpenAI distills, fine-tunes, or quantizes from one below High."""
    guard = json.dumps(rule("f6-rel")["guard"])
    name = "distilled_finetuned_or_quantized_from_below_high"
    assert name in guard and "significant_increase" in json.dumps(rule("f6-rel")["unless"])
    assert ("distills, fine-tunes, or quantizes from a model that was previously determined not to cross a High "
            "capability threshold") in legend(name)
    assert "derives" not in legend(name)
    assert "generally" in next(b.text for b in T.rule_blocks() if b.id == "f6-rel")


def test_f14_summary_covers_the_sag_recommendation_with_no_request_guard(pf):
    """f14-summary (classes 1, 7): the testing results and the SAG recommendation; requesting is permitted, not
    presupposed; the sensitive-information limits stay the carve-out."""
    data = rule("f14-summary")
    assert data["predicate"] == "summary_access" and data["guard"] == ["top"]
    assert "beyond_sensitive_limits" in json.dumps(data["unless"])
    assert "SAG summary" in act("summary_access") and len(act("summary_access")) <= 80
    assert ("a summary of the testing results and SAG recommendation on capability levels and safeguards (subject "
            "to certain limits for highly sensitive information)") in legend("summary_access")


def test_f12_undermining_keeps_and_or(pf):
    """f12-undermining(-unscoped) (classes 1, 5): no conjunction between capability and propensity."""
    assert "as well as" not in act("robust_case") and "what was discovered" in act("robust_case")
    assert "robust to the discovered capability and/or propensity" in legend("robust_case")
    assert {rule(n)["predicate"] for n in ("f12-undermining", "f12-undermining-unscoped")} == {"robust_case"}


def test_f12_sandbagging_is_one_disjunctive_duty(pf):
    """f12-sandbagging(-unscoped) (classes 1, 5, 7, 8): one act carries both alternatives; no carve-out and no
    harness assumption that the bound is unused."""
    for name in ("f12-sandbagging", "f12-sandbagging-unscoped"):
        assert rule(name)["predicate"] == "sandbagging_response" and rule(name)["unless"] == []
    assert rule("f12-sandbagging")["guard"] == ["unary", "sandbagging_found", ["var", 0]]
    assert rule("f12-sandbagging-unscoped")["guard"] == ["top"]
    assert ("Adopt elicitation approach that overcomes sandbagging, or use a conservative upper bound of the "
            "model’s non-sandbagged evaluation results") in legend("sandbagging_response")
    assert not hasattr(R, "ALTERNATIVES")
    assert "conservative_upper_bound_used" not in V.environment()["vocabulary"]["predicates"]


@needs_lean
def test_k10_stays_some_n_and_k12_all_on_a_live_query(pf):
    R.MUTANT = R.WITHOUT_NARROWING = None
    k10 = R.answer(key_item("K10"))
    assert "undecided" not in k10 and k10["choices"]
    assert all(row["holds"] == (row["choice"]["RS4"] == "N") for row in k10["choices"])
    k12 = R.answer(key_item("K12"))
    assert "undecided" not in k12 and k12["choices"] and all(row["holds"] for row in k12["choices"])


def test_f16_year_reviews_the_framework_once_as_to_continued_sufficiency(pf):
    """f16-year (classes 1, 2): the duty's subject is the Framework (a one-member sort), not each situation."""
    environment = V.environment()["vocabulary"]
    assert environment["predicates"]["annual_review"]["arguments"] == ["framework"]
    assert "Preparedness Framework" in environment["sorts"]["framework"]["description"]
    assert "continued sufficiency" in act("annual_review") and "at least once a year" in act("annual_review")
    assert ("We will review and potentially update the Preparedness Framework for continued sufficiency at least "
            "once a year.") in legend("annual_review")
    assert rule("f16-year")["predicate"] == "annual_review"
    assert next(b.text for b in T.rule_blocks() if b.id == "f16-year").startswith("Rule 1. Every framework must")


def test_facts_hold_exactly_their_stated_inventory(pf):
    """FACTS (class 7): facts.d1.ve is PLAN 4.1's levels, RS2 = nest and 4.4's dated fact; the change log's and
    footnote 5's sentences are headed blocks of rules.d1.ve, each read as its own unit; N4 names cl-levels."""
    assert [b.id for b in T.read_blocks("facts.d1.ve")] == [
        "bio-high", "bio-critical", "cyb-high", "cyb-critical", "ais-high", "ais-critical", "rs2-nest",
        "no-critical-models"]
    in_rules = {b.id: b for b in T.read_blocks("rules.d1.ve") if not T.is_rule(b)}
    assert set(in_rules) == {"cl-levels", "fn5-indicator"} and all(b.when == () for b in in_rules.values())
    assert re.search(r"^## cl-levels \| always \| Change log item 2: “Also, we are removing terms",
                     (PF / "rules.d1.ve").read_text(encoding="utf-8"), re.M)
    assert {"cl-levels", "fn5-indicator"} <= {b.id for b, _ in T.facts()}
    assert not {"cl-levels", "fn5-indicator"} & {b.id for b in T.rule_blocks()}
    saved = json.loads((PF / "results.json").read_text())
    assert saved["items"]["N4"]["choices"][0]["rules"] == ["cl-levels"]
    # Review F1: G7 rests on footnote 5's indicator premise, so every G7 row names fn5-indicator.
    assert [row["rules"] for row in saved["items"]["G7"]["choices"]] == [["fn5-indicator"]] * 2


def test_every_premise_unit_outside_facts_is_named_by_an_item():
    """Review F1 as a class: uc-audit ties an item to the units its results.json record names, plus FACTS. A fact
    block of rules.d1.ve is no part of FACTS, so some item's rows must name it, or an UNFAITHFUL re-read of it
    would fail no item."""
    saved = json.loads((PF / "results.json").read_text())
    named = {unit for item in saved["items"].values() for row in item.get("choices", ())
             for unit in row.get("rules", ())}
    units = {b.id for b in T.rule_fact_blocks()}
    assert units == {b.id for b in T.read_blocks("rules.d1.ve") if not T.is_rule(b)}
    assert units <= named, f"premise units no item names: {sorted(units - named)}"


def test_premise_units_follow_the_goal(pf):
    """Review F1: a route's premise units are derived from its goal's predicates (run.premise_units), not listed by
    hand: G7's goal (indicator_for) rests on fn5-indicator, N4's (low, medium) on cl-levels, and a goal naming
    neither rests on no unit outside FACTS."""
    from ve import ast as A
    env = T.base_environment()
    level = lambda p: ["exists", "level", ["unary", p, ["var", 0]]]  # noqa: E731
    indicator = ["exists", "evaluation", ["exists", "level", ["binary", "indicator_for", ["var", 1], ["var", 0]]]]
    assert R.premise_units(A.formula_from_data(env, indicator)) == ["fn5-indicator"]
    assert R.premise_units(A.formula_from_data(env, ["or", level("low"), level("medium")])) == ["cl-levels"]
    assert R.premise_units(A.formula_from_data(env, ["and", indicator, level("low")])) == [
        "cl-levels", "fn5-indicator"]
    assert R.premise_units(A.formula_from_data(env, level("high"))) == []
    assert R.low_medium_never()["choices"][0]["rules"] == ["cl-levels"]


def test_regulated_predicates_stay_within_64():
    stage0 = json.loads((REPO / "docs/usecases/safetyfw/openai-preparedness/stage0.json").read_text())
    count = sum("regulated" in p for p in V.environment()["vocabulary"]["predicates"].values())
    # fix-5 adds fast_track_request, the fast-track permission (PLAN 12 item 26)
    assert stage0["P7"]["regulated_predicates"] == count == 61 <= 64


# --- openai-preparedness-fidelity-fix-3: the six round-B units both adjudicators judged REAL ---------------------
# (reviews/audit-newrule-fsfpf/pf-adjud/result.md Q02 Q05 Q06 Q08 Q09 Q10; PLAN 12 item 24)

def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, (list, dict)):
        for item in (value.values() if isinstance(value, dict) else value):
            yield from _strings(item)


def predicates_read(block_id):
    """Every predicate a rule block names: its regulated act and each guard or exception predicate."""
    names = V.environment()["vocabulary"]["predicates"]
    return {s for s in _strings(rule(block_id)) if s in names}


def block(block_id):
    return next(b for b in T.rule_blocks() if b.id == block_id)


def legend_quotes(predicate):
    """The “…” quotations of a legend, each of which must be source text its block's header quotes."""
    return re.findall("“([^”]+)”", legend(predicate))


def test_f4_security_reads_no_coverage_condition(pf):
    """f4-security (Q08; DRI fix-2 q3 item 2): "for High capability models" states no coverage, so neither the rule
    nor the situation sort every rule reads carries one; `covered` stays only where the source says covered."""
    sorts = V.environment()["vocabulary"]["sorts"]
    assert sorts["situation"]["description"] == "a development, use, deployment, review or decision of a model"
    assert predicates_read("f4-security") == {"security_practices", "reached", "high"}
    for name in predicates_read("f4-security"):
        assert "covered" not in legend(name), name
    assert "no coverage condition" in block("f4-security").source
    # the fix-2 builder's survey the ruling names: F2, F7, F8, F9 and f16-sag-recommend, whose source states coverage
    assert {b.id for b in T.rule_blocks() if "covered" in predicates_read(b.id)} == {
        "f2-deploy", "f2-deploy-any", "f2-reminder", "f2-reminder-any", "f2-security-developed", "f7-evaluations",
        "f7-report", "f7-compile", "f8-start", "f9-report", "f16-sag-recommend"}


def test_f9_report_act_states_the_compilation_and_its_legend_quotes_4_2(pf):
    """f9-report (Q10): the act states 4.2's compilation, as f7-compile does for the Capabilities Report; the legend
    quotes the 4.2 sentence in full; section 4's scope guard (covered, a reached threshold) stays."""
    assert R.ATOMS["SAFEREP"] == ("safeguards_report",)
    assert [b.id for b in blocks_for("safeguards_report")] == ["f9-report"]
    assert act("safeguards_report") == "{0} have planned safeguard information compiled into a Safeguards Report"
    sentence = ("We compile the information on the planned safeguards needed to minimize the risk of severe harm "
                "into a Safeguards Report.")
    assert sentence in legend_quotes("safeguards_report")
    assert all(q in block("f9-report").source for q in legend_quotes("safeguards_report"))
    assert rule("f9-report")["guard"][1] == ["unary", "covered", ["var", 0]]
    assert predicates_read("f9-report") == {"safeguards_report", "covered", "reached"}


def test_cyberdefense_tools_keep_their_purpose(pf):
    """f1-contrib-cyb-strict and -default (Q05, Q06): one shared act keeps the tools "for cyberdefense"; the legend
    quotes the CYB-H bullet in full (PLAN 12 item 17's condition)."""
    assert [b.id for b in blocks_for("cyberdefense_contribution")] == ["f1-contrib-cyb-strict", "f1-contrib-cyb-default"]
    assert act("cyberdefense_contribution").endswith("cyberdefense policies as well as cyberdefense tools")
    assert legend_quotes("cyberdefense_contribution") == [
        "Contribute towards improved cyberdefense policies and tools for cyberdefense"]
    for name in ("f1-contrib-cyb-strict", "f1-contrib-cyb-default"):
        assert legend_quotes("cyberdefense_contribution")[0] in block(name).source


def test_reasonable_evidence_quotes_4_2s_condition_with_its_decider(pf):
    """f10-review (Q02), and f10-validate through the shared guard: "we find" and "as expected" are in the legend, and
    OT11's decider is OpenAI ('we') as PLAN 3.2 states."""
    condition = "If we find reasonable evidence that our safeguards are not working as expected"
    assert legend_quotes("reasonable_evidence") == [condition]
    assert "OpenAI ('we') finds reasonable evidence that its safeguards are not working as expected" in \
        legend("reasonable_evidence")
    assert "OpenAI ('we') decides this (OT11)" in legend("reasonable_evidence")
    assert R.OT["OT11"] == "reasonable_evidence"
    for name in ("f10-review", "f10-validate"):
        assert rule(name)["guard"] == ["unary", "reasonable_evidence", ["var", 0]]
        assert condition in block(name).source


def test_f13_review_names_the_latest_research_and_findings_per_category(pf):
    """f13-review (Q09): the act names what is reviewed and keeps "each Research Category"; the legend quotes 2.3's
    sentence in full; the periodicity stays ET-blocked."""
    assert [b.id for b in blocks_for("research_review")] == ["f13-review"]
    assert act("research_review") == ("{0} review the latest research as well as findings in each Research "
                                      "Category")
    sentence = "We will periodically review the latest research and findings for each Research Category."
    assert legend_quotes("research_review") == [sentence]
    assert sentence in block("f13-review").source
    assert B.PLACEMENTS["We will periodically review the latest research"] == ("blocked_rule", "f13-review", ("ET",))


def test_the_six_changed_acts_fit_the_act_limit(pf):
    for name in ("safeguards_report", "cyberdefense_contribution", "research_review"):
        text = act(name)
        assert len(text) <= 80 and re.fullmatch(r"\{0\}( [A-Za-z][A-Za-z'-]*)+", text), name
        assert not {"and", "or", "for", "if", "not", "no", "every", "must"} & set(text.lower().split()), name


# --- openai-preparedness-fidelity-fix-4: round B part 2, the other six units both adjudicators judged REAL ---------
# (reviews/audit-newrule-fsfpf/pf-adjud/result.md section 2: R01 R02 R03 R13 R14 R15; PLAN 12 item 25)

F3_DEVELOPMENT = ("f3-develop", "f3-develop-forecast", "f3-develop-inuse", "f3-develop-inuse-forecast", "f3-reminder")
SENTENCE_4_4 = ("Such models require additional safeguards (safety and security controls) during development, "
                "regardless of whether or when they are externally deployed.")
SENTENCE_APPENDIX_C = "Systems that reach Critical capability also require sufficient safeguards during development."


def test_f3_development_act_keeps_additional_with_the_sufficiency(pf):
    """f3-develop, f3-develop-forecast, f3-reminder (R13-R15, C1): one shared act, not forked, carries 4.4's
    "additional" safety and security controls and the sufficiency of 4.2 and Appendix C; its legend quotes the
    three sentences in full."""
    assert [b.id for b in blocks_for("safeguards_during_development")] == list(F3_DEVELOPMENT)
    assert act("safeguards_during_development") == (
        "{0} have sufficient additional safety plus security controls during development")
    assert legend_quotes("safeguards_during_development") == [
        SENTENCE_4_4, "Systems that reach Critical capability also require safeguards that sufficiently minimize "
        "associated risks during development.", SENTENCE_APPENDIX_C]
    for name in F3_DEVELOPMENT[:4]:
        assert SENTENCE_4_4 in block(name).source, name
    assert SENTENCE_APPENDIX_C in block("f3-reminder").source


def test_f3_development_units_read_no_coverage_condition(pf):
    """f3-develop, f3-develop-forecast, f3-reminder (R13-R15, C7): neither the sentences nor the rules state
    coverage; the situation sort (fix-3) carries none, and no predicate the rules read does."""
    assert "covered" not in V.environment()["vocabulary"]["sorts"]["situation"]["description"]
    for name in ("f3-develop", "f3-develop-forecast", "f3-reminder"):
        assert "covered" not in predicates_read(name), name
        for predicate in predicates_read(name):
            assert "covered" not in legend(predicate).replace("no coverage condition", ""), (name, predicate)
        assert "no coverage condition" in block(name).source, name


@needs_lean
def test_an_uncovered_critical_model_still_needs_development_safeguards(pf):
    """The live consequence of R13-R15's C7: OT7 false (not covered) does not release the development duty."""
    for case, rules in ((({"id": "t", "levels": ["BIO-C"], "activity": "DEV", "findings": {"OT7": False}}),
                         {"f3-develop", "f3-reminder"}),
                        (({"id": "t", "levels": [], "activity": "DEV", "findings": {"OT7": False, "OT10": True}}),
                         {"f3-develop-forecast"})):
        assert selections({"RS18": "devonly", "RS2": "sep"}, case, "safeguards_during_development") == rules
    # the opposite direction: below Critical and with no forecast, coverage or not, no development duty is selected
    for covered in (True, False):
        case = {"id": "t", "levels": ["BIO-H"], "activity": "DEV", "findings": {"OT7": covered}}
        assert selections({"RS18": "devonly", "RS2": "sep"}, case, "safeguards_during_development") == set()


def test_c3_access_reads_no_coverage_condition_and_states_why_may_require_is_untranslated(pf):
    """c3-access-strict and -default (R02, R03): "For all models" states no coverage, so the rules read none; the
    untranslated "may require" clause has its reason (a possibility, not a duty; no permission granted) in both
    headers and in the reading set's spans.json record, with its byte span inside the unit."""
    assert "covered" not in V.environment()["vocabulary"]["sorts"]["situation"]["description"]
    for name in ("c3-access-strict", "c3-access-default"):
        assert predicates_read(name) == {"access_limited"} and rule(name)["guard"] == ["top"], name
        assert "covered" not in legend("access_limited")
        header = block(name).source
        assert "no coverage condition" in header and "the “may require” clause is not translated, because" in header
        assert "a possibility" in header and "not a duty" in header and "grants no one a permission" in header
    record = next(u for u in json.loads((PF / "spans.json").read_text())["units"]
                  if u.get("reading_set") == "rs9-access")
    (fragment, reason, detail), = B.UNTRANSLATED["rs9-access"]
    (clause,) = record["untranslated"]
    assert clause == {"span": clause["span"], "reason": "possibility_not_duty", "detail": detail}
    assert fragment == "and may require additional approvals for access" and reason == clause["reason"]
    start, end = clause["span"]
    assert record["span"][0] <= start and end == start + len(fragment.encode()) <= record["span"][1]
    assert "not a duty" in detail and "PLAN 3.3" in detail


@needs_lean
def test_an_uncovered_model_still_has_access_strictly_limited(pf):
    """The live consequence of R02/R03: G9's uncovered model at no threshold is bound by C.3's access duty."""
    case = {"id": "t", "levels": [], "activity": None, "findings": {"OT7": False}}
    assert selections({"RS9": "strict"}, case, "access_limited") == {"c3-access-strict"}
    assert selections({"RS9": "default"}, case, "access_limited") == {"c3-access-default"}


SENTENCE_C2 = ("Safeguards should sufficiently minimize the risk associated with a misaligned model circumventing human "
               "control and oversight and executing severe harms.")


def test_c2_misalignment_has_no_risk_guard_under_either_reading(pf):
    """c2-misalignment-strict (R01) and, by the DRI ruling of 2026-11-13 item 2, -default: C.2's sentence states no
    applicability condition, so neither rule waits for a finding that the risk exists; RS9 changes only the modal;
    the legend quotes the sentence in full."""
    assert "misaligned_model_risk" not in V.environment()["vocabulary"]["predicates"]
    for name, modal in (("c2-misalignment-strict", "must"), ("c2-misalignment-default", "should")):
        assert rule(name)["guard"] == ["top"] and predicates_read(name) == {"misalignment_risk_minimized"}, name
        assert block(name).text.startswith(f"Rule 1. Every situation {modal} have safeguards"), name
        assert SENTENCE_C2 in block(name).source and "no applicability condition" in block(name).source, name
    assert legend_quotes("misalignment_risk_minimized") == [SENTENCE_C2]
    assert B.READINGS["rs9-c2-misalignment"][1] == {"strict": ["c2-misalignment-strict"],
                                                    "default": ["c2-misalignment-default"]}


@needs_lean
def test_c2_binds_a_model_with_no_risk_finding(pf):
    """The live consequence: a model at no threshold, uncovered and with no risk finding (G9's model), is bound."""
    case = {"id": "t", "levels": [], "activity": None, "findings": {"OT7": False}}
    assert selections({"RS9": "strict"}, case, "misalignment_risk_minimized") == {"c2-misalignment-strict"}
    assert selections({"RS9": "default"}, case, "misalignment_risk_minimized") == {"c2-misalignment-default"}


# --- openai-preparedness-fidelity-fix-5: K13's fast-track words (lp1701 item 1; PLAN 12 item 26) -----------------
# The ruling: a documented omission earns no credit. K13's case contains the words f16-chair-* once recorded as
# "loss 1" ("a fast track is requested"), so the fast-track sentence is now a rule: OpenAI may request the fast track.

SENTENCE_FAST_TRACK = ("In the rare case that a risk of severe harm rapidly develops (e.g., there is a change in our "
                       "understanding of model safety that requires urgent response), we can request a fast track for "
                       "the SAG to process the report urgently.")
SENTENCE_CHAIR = ("The SAG Chair should also coordinate with OpenAI Leadership for immediate reaction as needed to "
                  "address the risk.")
FAST_TRACK_WORDS = "we can request a fast track for the SAG to process the report urgently"
CHAIR_UNITS = ("f16-chair-strict", "f16-chair-default")
ACCOUNTING_ENTRY = re.compile(r'"([^"]*)"\s*([^;"]*)')


def accounting_entries():
    """accounting.d1.txt as {block id: [(omitted words, reason tag)]}."""
    lines = (PF / "accounting.d1.txt").read_text(encoding="utf-8").splitlines()
    return {line.split(" | omits:")[0]: [(w, t.strip()) for w, t in ACCOUNTING_ENTRY.findall(line.split(" | omits:")[1])]
            for line in lines}


def test_fast_track_sentence_is_carried_by_a_permission_rule_under_both_chair_readings(pf):
    """f16-chair-strict and -default quote the whole Fast-track passage; the fast-track sentence is carried by the
    rule their accounting names, f16-fast-track: under every RS9 choice OpenAI MAY request the fast track in the
    rapid-risk case (a permission, not a duty), and the act's legend quotes the full sentence, not a pointer."""
    entries = accounting_entries()
    fast = block("f16-fast-track")
    assert fast.when == () and SENTENCE_FAST_TRACK in fast.source
    for name in CHAIR_UNITS:
        assert SENTENCE_FAST_TRACK + " " + SENTENCE_CHAIR in block(name).source, name
        assert (FAST_TRACK_WORDS, "rule f16-fast-track") in entries[name], name
    assert fast.text.startswith("Rule 1. Every situation may have a fast track requested so the SAG processes")
    norm = rule("f16-fast-track")
    assert norm["predicate"] == "fast_track_request" and norm["sign"] is True and norm["unless"] == []
    assert norm["guard"] == ["unary", "rapid_risk", ["var", 0]]
    regulated = V.environment()["vocabulary"]["predicates"]["fast_track_request"]["regulated"]
    assert regulated["role"] == "permission" and regulated["default"] == "allow"
    text = act("fast_track_request")
    assert text == "{0} have a fast track requested so the SAG processes the report urgently"
    assert len(text) <= 80 and re.fullmatch(r"\{0\}( [A-Za-z]+)+", text)
    assert not {"and", "or", "for", "if", "not", "no", "every", "must", "is", "then"} & set(text.lower().split())
    assert legend_quotes("fast_track_request") == [SENTENCE_FAST_TRACK]
    # The Chair's coordination stays RS9 strict/default on its own sentence, and its legend quotes it in full.
    assert legend_quotes("chair_coordination") == [SENTENCE_CHAIR]
    for name, modal in (("f16-chair-strict", "must"), ("f16-chair-default", "should")):
        assert block(name).text.startswith(f"Rule 1. Every situation {modal} have the SAG Chair coordinate"), name
        assert predicates_read(name) == {"chair_coordination", "rapid_risk", "immediate_reaction_needed"}, name
    assert B.READINGS["rs9-chair"][1] == {"strict": ["f16-chair-strict"], "default": ["f16-chair-default"]}
    assert ("f16-fast-track",) in R.COMMITMENTS["F16"]


@needs_lean
def test_a_rapid_risk_case_may_request_the_fast_track_under_both_readings(pf):
    """The live consequence: in the rapid-risk case VE selects the permission under RS9 strict and default, never a
    duty or a prohibition on the request; without the rapid-risk finding nothing is selected."""
    rapid = {"id": "t", "levels": [], "activity": None, "findings": {"OT18": True}}
    calm = {"id": "t", "levels": [], "activity": None, "findings": {"OT18": False}}
    for choice in ("strict", "default"):
        assert selections({"RS9": choice}, rapid, "fast_track_request") == {"f16-fast-track"}, choice
        assert selections({"RS9": choice}, rapid, "fast_track_request", sign=False) == set(), choice
        assert selections({"RS9": choice}, calm, "fast_track_request") == set(), choice
    assert [b.id for b in blocks_for("fast_track_request")] == ["f16-fast-track"]


def test_accounting_has_no_loss_for_the_fast_track_words():
    """No block records "we can request a fast track for the SAG to process the report urgently" as a loss; the
    passage's "In the rare case that" and its "(e.g., ...)" example stay exposition with their reasons."""
    entries = accounting_entries()
    for name, rows in entries.items():
        for words, tag in rows:
            assert not ("fast track" in words and tag.startswith("loss")), (name, words, tag)
    for name in CHAIR_UNITS:
        assert ("In the rare case that", "exposition") in entries[name], name
        assert ("(e.g., there is a change in our understanding of model safety that requires urgent response)",
                "exposition") in entries[name], name
        assert not any(tag.startswith("loss") for _, tag in entries[name]), name
    assert entries["f16-fast-track"] == []


# The record paths of the uc-audit omission rule: tests/omission_rule.py ports the installed rule (omission-2) whole, with
# every fail-closed path (any tag but restates / rule / reading = loss). This file keeps no copy of its own.
def omission_records(units):
    """{unit: [path]} for every record path of the installed omission rule that names one of `units`."""
    return omission_rule.record_paths("openai-preparedness", units)


def omission_exposures(units):
    """{unit: [(path, detail)]}: the rule's exposures of `units`, with the words or sentence each one records."""
    return {u: [(e[2], e[3]) for e in es] for u, es in omission_rule.exposures("openai-preparedness", units).items()}


def plan12_item(number):
    """PLAN section 12's item `number` as one line of normalised text."""
    plan = (PF / "PLAN.md").read_text(encoding="utf-8")
    item = re.search(rf"^{number}\. .*?(?=^\d+\. |^\*\*|^## |\Z)", plan, re.M | re.S).group(0)
    return " ".join(item.split())


def test_k13_units_carry_only_their_exposition_and_plan12_records():
    """K13 (the Chair coordinating in the rapid-risk case with a fast track requested) reads f16-chair-strict and
    -default. Under the installed omission rule each still carries exactly two exposures from its accounting line, the
    exposition entries "In the rare case that" and the "(e.g., ...)" example (an exposition tag counts as a loss), and
    PLAN 12 item 26's record sentence; f16-fast-track carries item 26's sentences only. No record holds the fast-track
    words, so K13 counts as audited once an omission-audit seat's reads clear these exposures, and not before."""
    k13 = json.loads((PF / "results.json").read_text())["items"]["K13"]
    assert set(k13["selected_rules"]) == set(CHAIR_UNITS)
    assert [c["holds"] for c in k13["choices"]] == [True, True]
    exposures = omission_exposures(CHAIR_UNITS + ("f16-fast-track",))
    assert omission_records(CHAIR_UNITS + ("f16-fast-track",)) == {
        "f16-chair-strict": ["loss", "loss", "plan12"],
        "f16-chair-default": ["loss", "loss", "plan12"],
        "f16-fast-track": ["plan12", "plan12"]}
    for name in CHAIR_UNITS:
        assert [d for p, d in exposures[name] if p == "loss"] == [
            "In the rare case that (exposition)",
            "(e.g., there is a change in our understanding of model safety that requires urgent response) (exposition)"]
    item26 = plan12_item(26)
    assert item26.startswith("26. **Appendix B's fast-track sentence is a permission rule")
    for name, rows in exposures.items():
        for path, detail in rows:
            assert path == "loss" or detail in item26, (name, path, detail)
            assert path == "plan12" or "fast track" not in detail.lower(), (name, path, detail)
    spans = json.loads((PF / "spans.json").read_text())["units"]
    fast = next(u for u in spans if u.get("rule") == "f16-fast-track")
    chair = next(u for u in spans if u.get("reading_set") == "rs9-chair")
    assert fast["status"] == "OPEN" and fast["span"][1] == chair["span"][0] and "untranslated" not in chair
    # the check is not vacuous: a loss the case really records (c3-access-default's accounting line) is found
    assert "loss" in omission_records(("f16-year", "c3-access-default"))["c3-access-default"]
