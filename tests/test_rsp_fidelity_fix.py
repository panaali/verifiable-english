"""anthropic-rsp-fidelity-fix: the T fixes of the RSP use-case audit (PLAN section 12, item 19).

The frozen key is compared cell by cell with PLAN section 6; the Appendix A, F9, F13/F16 and G1/N3/C-doc repairs are
checked on the translation and on the saved results, each in the direction it was written for and the opposite one.
"""
import json
import re

import pytest

import test_safetyfw_usecases as base

RSP, LEAN_SERVICE = base.RSP, base.LEAN_SERVICE
rsp_run, rsp_translation, rsp_vocabulary, rsp_stage0 = (base.rsp_run, base.rsp_translation, base.rsp_vocabulary,
                                                        base.rsp_stage0)
needs_lean = pytest.mark.skipif(not LEAN_SERVICE.exists(), reason="the Lean service is not built")
rsp_modules = base.rsp_modules


# --- the answer key against section 6, cell by cell ------------------------------------------------------------------

VERDICT = re.compile(r"SOME\([^)]*\)|\bALL\b|\bNONE\b")


def _tokens(cell):
    found = VERDICT.findall(cell.replace("∨", "|").replace("∧", "&"))
    return found or [cell.split()[0]]


def section6_cells(text):
    """Item id -> the verdict tokens of its section-6 cell (PLAN 6's tables: A by own/other row, B by atom, the
    rest by their Key column; "X … Y" rows expanded)."""
    cells, header = {}, None
    for line in text.split("\n"):
        if not line.startswith("| ") or line.startswith("|---"):
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if cols[0] == "Case":
            header = cols
            continue
        if header[1].startswith("PROTk"):
            for k in range(5):
                if cols[0] not in ("A-T0", "A-Tk, k = 1 … 4") or (k == 0) != (cols[0] == "A-T0"):
                    continue
                for j in range(1, 5):
                    for atom, own, other in (("PROT", 1, 2), ("ARG", 3, 4)):
                        cells[f"A-T{k}/{atom}{j}"] = _tokens(cols[own if j == k else other])
        elif "INSCOPE (F8)" in header:
            cells[f"{cols[0]}/INSCOPE"], cells[f"{cols[0]}/ASSESS"] = _tokens(cols[2]), _tokens(cols[3])
        else:
            ids = [cols[0]]
            if " … " in cols[0]:
                first, last = cols[0].split(" … ")
                ids = [first[:-1] + str(n) for n in range(int(first[-1]), int(last[-1]) + 1)]
            for id_ in ids:
                cells[id_] = _tokens(cols[header.index("Key")])
    return cells


def cell_mismatches(text, key_items):
    cells = section6_cells(text)
    out = sorted(set(cells) ^ {k["id"] for k in key_items})
    for k in key_items:
        want = list(k["key"].values()) if isinstance(k["key"], dict) else None
        got = cells.get(k["id"], [])
        if (got != want) if want is not None else (set(got) != {k["key"]}):
            out.append(k["id"])
    return out


def test_every_answer_key_cell_equals_its_section_6_cell():
    """No transcription finding is recorded for RSP, so there is no exception."""
    key = base.items("anthropic-rsp")
    assert len(key) == 126 and cell_mismatches(base.section("anthropic-rsp", 6), key) == []


def test_cell_check_catches_a_changed_or_missing_cell():
    text, key = base.section("anthropic-rsp", 6), base.items("anthropic-rsp")
    changed = [dict(k, key="NONE") if k["id"] == "N3" else k for k in key]
    assert cell_mismatches(text, changed) == ["N3"]
    assert cell_mismatches(text, [k for k in key if k["id"] != "D7"]) == ["D7"]
    assert cell_mismatches(text.replace("| G2 |", "| G2x |"), key) == ["G2", "G2x", "G2"]


# --- Appendix A -------------------------------------------------------------------------------------------------------

def _rule(block_id):
    return json.loads(rsp_translation.parsed_rule(block_id))


def _unaries(formula):
    text = json.dumps(formula)
    return set(re.findall(r'\["unary", "([a-z_]+)"', text)) | set(re.findall(r'\["binary", "([a-z_]+)"', text))


SCENARIOS = {"lead": ("f24-argument", "f24-delay"), "competitors": ("f25-meet", "f25-delay"),
             "upleveling": ("f26-effort", "f26-need-not-delay")}


def _open_term(name, term):
    return f"Open term {term}," in rsp_vocabulary.BASE.get(name, {}).get("description", "")


@needs_lean
def test_each_appendix_a_scenario_has_its_own_evidence_and_as_needed(rsp_modules):
    used = {scenario: {term: {p for b in blocks for p in _unaries(_rule(b)["guard"]) if _open_term(p, term)}
                       for term in ("OT7", "OT8")} for scenario, blocks in SCENARIOS.items()}
    evidence = [used[s]["OT8"] for s in SCENARIOS]
    assert all(len(e) == 1 for e in evidence) and len(set().union(*evidence)) == 3
    assert used["lead"]["OT7"] and used["competitors"]["OT7"] and not used["upleveling"]["OT7"]
    assert used["lead"]["OT7"].isdisjoint(used["competitors"]["OT7"])


@needs_lean
def test_f24_has_no_added_guard_and_both_delays_carry_their_release(rsp_modules):
    for block in SCENARIOS["lead"]:
        assert "highly_capable" not in _unaries(_rule(block)["guard"])
    assert _rule("f24-delay")["unless"] == [["unary", "lead_no_longer_believed", ["var", 0]]]
    assert _open_term("lead_no_longer_believed", "OT9")
    release = _rule("f25-delay")["unless"]
    assert release[0][:2] == ["forall", "competitor"]
    assert _unaries(release) == {"develops_highly_capable", "posture_attainable"}
    # "For our highly capable frontier models" is the source's own guard on F25.
    assert {"highly_capable"} <= _unaries(_rule("f25-meet")["guard"]) & _unaries(_rule("f25-delay")["guard"])


@needs_lean
def test_f25_quantifies_over_each_competitor_and_n3_enumerates_rs5(rsp_modules):
    assert rsp_vocabulary.REGULATED["posture_matched"]["arguments"] == ["situation", "competitor"]
    k20 = rsp_run.answer({"id": "K20", "case": "K20", "item": "REQUIRED:MEET_OR_EXCEED_COMPETITOR_POSTURE"})
    assert rsp_run.verdict(k20) == "ALL" and k20["choices"][0]["rules"] == ["f25-meet"]
    n3 = rsp_run.answer({"id": "N3", "case": None, "item": "NEVER:F25_IN_LEAD_SCENARIO_WITHOUT_COMPETITOR"})
    assert n3["cone"] == ["RS5"] and [r["choice"]["RS5"] for r in n3["choices"]] == ["import", "noimport"]
    assert rsp_run.verdict(n3) == "ALL" and all(r["rules"] == ["f24-delay"] for r in n3["choices"])
    # Opposite direction: with a competitor whose posture is not yet attainable, F25 does require the delay (and,
    # since fix-2, prevails over F26's release, so C7 is NONE: PLAN 12, item 21).
    delay = rsp_run.query(rsp_run.witness("C7"), "delay")
    assert rsp_run.verdict(delay) == "ALL" and "f25-delay" in {n for r in delay["choices"] for n in r["rules"]}


# --- F8, F9 and D3 ------------------------------------------------------------------------------------------------------

COVERAGE_DATE = {"publicly_deployed", "internally_deployed"}


@needs_lean
def test_f9_and_its_cases_state_no_coverage_date(rsp_modules):
    for block in ("f9-public", "f9-internal"):
        assert _unaries(_rule(block)["guard"]).isdisjoint(COVERAGE_DATE)
    for case_id, own in (("K2", "off_cycle_public_deployment"), ("K3", "off_cycle_public_deployment"),
                         ("K4", "off_cycle_internal_deployment")):
        names = {atom[0] for atom in rsp_run.atoms(rsp_run.CASES[case_id])}
        assert own in names and names.isdisjoint(COVERAGE_DATE), case_id
    assert {"internally_deployed", "determined_by_publication"} <= _unaries(_rule("f8-internal")["guard"])
    b_int = {atom[0] for atom in rsp_run.atoms(rsp_run.CASES["B-INT"])}
    assert "determined_by_publication" not in b_int
    assert rsp_run.verdict(rsp_run.query(rsp_run.CASES["K2"], "off_cycle_published")) == "ALL"


def test_d3_holds_f16s_thirty_days_of_receipt():
    saved = json.loads((base.RSP_EVIDENCE / "stage0.json").read_text())
    item, days, due, rule = rsp_stage0.RECEIPT_COUNT
    assert saved["P4"]["certificates"][item] is True and days == "30" and rule == "f16-ask-commentary"
    assert "of receipt" in rsp_vocabulary.REGULATED["commentary_asked"]["regulated"]["act"]


# --- F13 / F16, C4 and C-doc ------------------------------------------------------------------------------------------

@needs_lean
def test_f13_and_f16_regulate_different_versions(rsp_modules):
    acts = {block: rsp_vocabulary.REGULATED[_rule(block)["predicate"]]["regulated"]["act"]
            for block in ("f13-redact-p", "f13-disclose", "f13-justify-default", "f16-only-legal")}
    assert all("public" in acts[b] for b in ("f13-redact-p", "f13-disclose", "f13-justify-default"))
    assert "external reviewers" in acts["f16-only-legal"]
    only_legal = _rule("f16-only-legal")
    assert only_legal["sign"] is False and only_legal["unless"][0][0] == "or"
    assert _unaries(only_legal["unless"]) == {"legal_prohibition_redaction", "legal_rights_redaction"}
    saved = json.loads((RSP / "results.json").read_text())["items"]
    assert saved["C4"]["basis"]["different_acts"] == {b: acts[b] for b in ("f13-redact-p", "f16-only-legal")}
    assert saved["C1"].get("basis") is None  # one act: no different-versions basis


def test_c_doc_checks_the_f13_f16_pair_over_plan_m2s_cone():
    assert rsp_run.C_DOC_SETS == ("RS1", "RS4", "RS5", "RS7")
    assert ("f13-redact-p", "f16-only-legal") in rsp_run.c_doc_pairs()
    saved = json.loads((RSP / "results.json").read_text())["items"]["C-doc"]
    assert saved["cone"] == list(rsp_run.C_DOC_SETS) and len(saved["choices"]) == 24
    assert all(["f13-redact-p", "f16-only-legal"] in row["rules"] for row in saved["choices"])
    assert not any(row["holds"] for row in saved["choices"])  # F26 yields to F24/F25: NONE (PLAN 12, item 21)


# --- G1, the predicate budget ------------------------------------------------------------------------------------------

@needs_lean
def test_g1_asks_the_translated_delay_act(rsp_modules):
    translated = {_rule(b.id)["predicate"] for b in rsp_translation.rule_blocks()}
    assert rsp_run.G1_ACT in translated and rsp_run.G1_ACT in rsp_vocabulary.REGULATED
    assert rsp_run.verdict(rsp_run.gap_probe("G1")) == "ALL"
    try:
        rsp_run.MUTANT = "m2"
        assert rsp_run.verdict(rsp_run.gap_probe("G1")) == "NONE"
    finally:
        rsp_run.MUTANT = None


def test_regulated_predicates_stay_within_lean_limit():
    regulated = [n for n, e in rsp_vocabulary.environment()["vocabulary"]["predicates"].items() if "regulated" in e]
    assert len(regulated) == 64


# --- anthropic-rsp-fidelity-fix-2: the 11-11 re-audit's T fixes and the DRI's rulings (PLAN section 12, items 20-21) ---

KEY = {k["id"]: k for k in base.items("anthropic-rsp")}


def _act(predicate):
    return rsp_vocabulary.REGULATED[predicate]["regulated"]["act"]


def _legend(predicate):
    return {**rsp_vocabulary.BASE, **rsp_vocabulary.REGULATED}[predicate]["description"]


def _answer(id_):
    return rsp_run.answer(KEY[id_])


def _rules(result):
    return sorted({name for row in result["choices"] for name in row.get("rules", ())})


def evidence_twins(predicates):
    """Pairs (evidence term, predicate) where a predicate states the very fact an evidence term is about: a guard on
    both requires the fact as well as the evidence, which "We have strong evidence that ..." does not (class 7)."""
    out = []
    for name, entry in predicates.items():
        found = re.search(r"we have (?:strong|clear) evidence that (?:all |a |no )?(.{40})", entry["description"])
        if found:
            out += [(name, other) for other, e in predicates.items() if other != name and found[1] in e["description"]]
    return sorted(out)


def test_no_predicate_restates_the_fact_an_evidence_term_is_about():
    predicates = rsp_vocabulary.environment()["vocabulary"]["predicates"]
    assert evidence_twins(predicates) == []
    # Seeded: the cycle-1 fact predicates are found again.
    fact = {"description": "at {0} a competitor has implemented a risk mitigation that: (1) represents a significant "
                           "improvement on reduction of our prioritized risks relative to our analogous mitigations"}
    assert evidence_twins({**predicates, "competitor_better_mitigation": fact}) == [
        ("mitigation_evidence", "competitor_better_mitigation")]


@needs_lean
def test_appendix_a_guards_are_the_evidence_alone(rsp_modules):
    assert _unaries(_rule("f25-meet")["guard"]) == {"develops_highly_capable", "highly_capable", "competitors_evidence"}
    assert _unaries(_rule("f25-delay")["guard"]) == {"competitors_evidence", "highly_capable", "posture_delay_needed"}
    assert _unaries(_rule("f26-effort")["guard"]) == _unaries(_rule("f26-need-not-delay")["guard"]) == {
        "mitigation_evidence"}
    assert "(1) represents a significant improvement" in _legend("mitigation_evidence")
    assert "(2) we could implement at comparable (or lower) effort" in _legend("mitigation_evidence")


@needs_lean
def test_cases_set_only_declared_atoms_and_the_stipulated_evidence(rsp_modules):
    declared = set(rsp_vocabulary.environment()["vocabulary"]["predicates"])
    assert not set(rsp_run.SCENARIO_TERMS) & declared  # a scenario is a label, never an atom
    for case in rsp_run.CASES.values():
        assert {atom[0] for atom in rsp_run.atoms(case)} <= declared, case["id"]
    k20, k21 = ({atom[0] for atom in rsp_run.atoms(rsp_run.CASES[c])} for c in ("K20", "K21"))
    assert "competitors_evidence" in k20 and "mitigation_evidence" in k21
    assert {i: rsp_run.verdict(_answer(i)) for i in ("K20", "K21a", "K21b")} == {"K20": "ALL", "K21a": "ALL",
                                                                                  "K21b": "NONE"}


@needs_lean
def test_no_k_limit_hides_an_answer_the_selected_rules_give(rsp_modules):
    """A K item is undecided only where its selected rules give a wrong answer; K15a, K17, K12a and K12b are
    answered by the rules that encode them (f20-notify-board's "promptly", f23-publish's effective date, F15's
    unordered consultation and approval)."""
    for id_ in rsp_run.K_LIMITS:
        kind = KEY[id_]["item"]
        raw = rsp_run.query(rsp_run.CASES[KEY[id_]["case"]], rsp_run.PREDICATES[kind.split(":", 1)[-1]])
        assert not rsp_run.same_set(KEY[id_]["key"], raw), id_
    expected = {"K15a": "f20-notify-board", "K17": "f23-publish", "K12a": "f15-select-approval",
                "K12b": "f15-select-approval"}
    for id_, rule in expected.items():
        result = _answer(id_)
        assert "undecided" not in result and rsp_run.verdict(result) == "ALL" and _rules(result) == [rule], id_
    assert "promptly" in _act("board_notified") and "effective date" in _legend("update_published")


@needs_lean
def test_f10_in_line_guard_is_live_both_ways(rsp_modules):
    """K18 as PLAN 5 states it leaves the mitigation's status open: NONE (PLAN 12, item 21); with the mitigation in
    place or planned shortly, F10 requires the deviation report."""
    assert rsp_run.verdict(_answer("K18")) == "NONE"
    stated = {**rsp_run.CASES["K18"], "extra": ("mitigation_in_place_or_planned",)}
    result = rsp_run.query(stated, "deviation_reported")
    assert rsp_run.verdict(result) == "ALL" and _rules(result) == ["f10-in-line"]
    assert {"describes_mitigation_and_deviates", "mitigation_in_place_or_planned", "noteworthy"} == _unaries(
        _rule("f10-in-line")["guard"])


def test_acts_and_legends_carry_the_restored_qualifiers():
    assert _act("unredacted_shared").startswith("{0} have final unredacted Risk Reports")
    approval = _act("reviewers_approved")
    assert "after" not in approval.split() and "Board consulted" in approval and "approved by the LTBT" in approval
    assert "publish written findings" in _act("commentary_asked") and "of receipt" in _act("commentary_asked")
    assert "written report that is made public" in _legend("commentary_asked")
    assert "subject to the outlined procedures" in _act("ltbt_review") and "3.6.1 and 3.6.2" in _legend("ltbt_review")
    assert "subject to the procedures outlined below" in _legend("external_review_process")
    assert "continuing to work with them" in _legend("candidate_revenue_dependent")
    assert all(means in _legend("advance_recommendations") for means in (
        "example-setting", "addressing unsolved technical problems", "advocacy through industry groups",
        "policy advocacy"))
    assert "link" in _act("past_roadmaps_kept") and "responsible-scaling-policy/roadmap" in _legend("past_roadmaps_kept")
    assert "including model training, capability evals, mitigations, and risk analyses" in _legend("ltbt_briefed")


@needs_lean
def test_f26_release_yields_to_f24_and_f25(rsp_modules):
    """DRI ruling: under RS4 = rel F26 releases only its own scenario's delay; on the joint C1 and C7 witnesses no
    conflict is selected, and N2 stays ALL."""
    for id_ in ("C1", "C7"):
        result = rsp_run.conflict(id_)
        assert [row["choice"]["RS4"] for row in result["choices"]] == ["scope", "rel"], id_
        assert [row["holds"] for row in result["choices"]] == [False, False], id_
    assert {i: rsp_run.verdict(_answer(i)) for i in ("C1", "C7", "C-doc", "N2")} == {
        "C1": "NONE", "C7": "NONE", "C-doc": "NONE", "N2": "ALL"}
    assert {"f24-delay", "f25-delay"} == {r for r, over in rsp_translation.PRECEDENCE.items()
                                         if "f26-need-not-delay" in over}


def offers_rs3c_result(reading_sets, blocks, readings):
    """The places RS3c = result could be offered again: a reading set, a block's `when`, a READINGS entry."""
    found = [f"READING_SETS {name}" for name, values in reading_sets.items() if name == "RS3c" or "result" in values]
    found += [f"block {b.id}" for b in blocks if any(name == "RS3c" for name, _ in b.when)]
    found += [f"READINGS {unit}" for unit, (name, by_reading) in readings.items()
              if name == "RS3c" or "result" in by_reading]
    return found


def test_rs3c_result_is_never_offered():
    blocks = list(rsp_translation.rule_blocks()) + list(rsp_translation.read_blocks("facts.d1.ve"))
    readings = base.rsp_build.READINGS
    assert offers_rs3c_result(rsp_translation.READING_SETS, blocks, readings) == []
    assert {"s2-suff-result", "s2-only-if-result"}.isdisjoint(b.id for b in blocks)
    # Seeded: each way of offering it again is caught.
    tagged = rsp_translation.Block("s2-suff-result", (("RS3c", "result"),), "row T4", "")
    assert offers_rs3c_result({**rsp_translation.READING_SETS, "RS3c": ("third", "result")}, blocks + [tagged],
                              {**readings, "rs3c_t4": ("RS3c", {"result": []})}) == [
        "READING_SETS RS3c", "block s2-suff-result", "READINGS rs3c_t4"]


@needs_lean
def test_t7_answers_none(rsp_modules):
    assert rsp_run.verdict(_answer("T7")) == "NONE"
    assert rsp_run.verdict(_answer("T3")) == "ALL"


def test_key_deviations_are_plan_section_12s_and_the_saved_causes_cite_them():
    deviations = rsp_run.key_deviations()
    assert sorted(deviations) == ["C-doc", "C1", "C7", "K18", "T7"]
    assert all(row["key"] == KEY[id_]["key"] and row["answer"] == "NONE" for id_, row in deviations.items())
    saved = {r["id"]: r for r in json.loads((RSP / "results.json").read_text())["comparison"]}
    for id_ in deviations:
        assert saved[id_]["ve"] == "NONE" and saved[id_]["cause"]["kind"] == "key finding", id_
    assert {i for i, r in saved.items() if r["status"] == "disagree"} == set(deviations)
    # The reader sees only section 12's table: the same row elsewhere, or no table, gives nothing.
    plan = (RSP / "PLAN.md").read_text()
    assert rsp_run.key_deviations(plan.replace("| Key deviation |", "| Other |")) == {}
    moved = plan.replace("\n## 13.", "\n## 13x.").replace("\n## 12.", "\n## 12.\n## 13.", 1)
    assert rsp_run.key_deviations(moved) == {}


def test_regulated_predicates_stay_64_after_fix_2():
    regulated = [n for n, e in rsp_vocabulary.environment()["vocabulary"]["predicates"].items() if "regulated" in e]
    assert len(regulated) == 64 and "mitigation_in_place_or_planned" not in regulated


def test_probe_f1_fix_2_deliverables_are_present():
    """Review fix round 1, PROBE F1: the item's text deliverables exist on the branch."""
    rules = (RSP / "rules.d1.ve").read_text()
    harness = (RSP / "run.py").read_text()

    def body(block_id):
        return rules.split(f"\n## {block_id} ")[1].split("\n## ")[0].split("\n", 1)[1]

    report = base.REPO / "docs/usecases/anthropic-rsp/anthropic-rsp-fidelity-fix-2/REPORT.md"
    assert report.exists()
    assert "competitors_strong_measures" not in body("f25-meet") + body("f25-delay")
    assert "competitor_better_mitigation" not in body("f26-effort") + body("f26-need-not-delay")
    assert "effective-date order is not encoded" not in harness
    assert "final" in body("f19-unredacted") and "after consulting" not in body("f15-select-approval")


# --- anthropic-rsp-fidelity-fix-3: the union-rule audit's 10 units (PLAN section 12, item 22) -----------------------

def _block(name, block_id):
    return next(b for b in rsp_translation.read_blocks(name) if b.id == block_id)


def _header_quote(block_id, name="rules.d1.ve"):
    """The header's first double-quoted source text (the quote a reader checks the rule against)."""
    return re.search(r'"(.+?)"(?: \(|;|$)', _block(name, block_id).source)[1]


# Each changed block's header quotes the whole sentence it follows; the end shown is the part the audit found cut.
FULL_SENTENCE_ENDS = {
    "f6-maintain": "charting our progress as a company and raising the bar over time.",
    "f7-publish": "how we have made determinations about whether to continue AI development and deployment in light "
                  "of the risks.",
    "f10-candid-default": "about how we see the risks of our systems and our state of preparedness for them.",
    "f11-goal-missed": "Changes to our Frontier Safety Roadmap and any cases where we failed to meet our goals.",
    "f12-approval": "will be sent to the CEO and Responsible Scaling Officer (RSO) for final review and approval.",
    "f13-redact-p": "shared with all regular-clearance Anthropic employees. Reasons we may redact material include "
                    "but are not limited to:",
    "f16-share-one-week": "with one or more external reviewers within one week of submitting the same report to our "
                          "Board and LTBT.",
    "f18-rso": "a designated member of staff who is responsible for the implementation of this policy.",
    "f23-publish": "will record the differences from the prior draft in the Change Log.",
}


def test_fix_3_headers_quote_the_full_source_sentence():
    for block_id, end in FULL_SENTENCE_ENDS.items():
        quote = _header_quote(block_id)
        assert "..." not in quote and "…" not in quote, block_id
        assert quote.endswith(end), block_id
    t4 = _header_quote("t4-suff", "facts.d1.ve")
    assert "..." not in t4 and t4.startswith("We will consider this threshold to be met if we determine that either")
    legends = ("scenario_2", "roadmap_maintained", "risk_reports_published", "candid_reports",
               "roadmap_review_addressed", "executive_submitted", "redaction", "shared_with_reviewers",
               "rso_maintained", "update_published")
    assert [p for p in legends if "..." in _legend(p) or "\u2026" in _legend(p)] == []


def _determination(name):
    """Whether `name` is an open term the company decides under T4's "if we determine"."""
    description = rsp_vocabulary.BASE[name]["description"]
    return "Open term OT" in description and f"decided by {rsp_vocabulary.WE} (\"if we determine\")" in description


def test_t4_both_branches_are_the_companys_determination():
    """FACTS: "if we determine that either (1) ... or (2)" governs branch (2) as it governs branch (1)."""
    branches = {name: re.findall(r'classified as "([a-z0-9_]+)"', _block("facts.d1.ve", block).text)
                for name, block in (("suff", "t4-suff"), ("iff", "t4-only-if"))}
    assert set(branches["suff"]) == set(branches["iff"]) == {"full_substitution_at_competitive_cost", "scenario_2"}
    assert all(_determination(name) for name in branches["suff"])
    assert "we determine that there is" in _legend("scenario_2")
    # The plain stipulated situation it was, the audit's finding, is caught.
    plain = rsp_vocabulary._base(["situation"], "at {0} there is \"dramatic acceleration\" (T4 (2))")
    saved = rsp_vocabulary.BASE["scenario_2"]
    try:
        rsp_vocabulary.BASE["scenario_2"] = plain
        assert not _determination("scenario_2")
    finally:
        rsp_vocabulary.BASE["scenario_2"] = saved


@needs_lean
def test_t_answers_hold_with_the_branch_2_determination(rsp_modules):
    assert {i: rsp_run.verdict(_answer(i)) for i in ("T3", "T5", "T6", "T7")} == {
        "T3": "ALL", "T5": "ALL", "T6": "NONE", "T7": "NONE"}
    saved = {r["id"]: r for r in json.loads((RSP / "results.json").read_text())["comparison"]}
    assert all(saved[i]["status"] == "agree" for i in ("T1", "T2b", "T3", "T4b", "T5", "T6"))


@needs_lean
def test_f11_states_both_parts_of_review_item_3_with_no_guard(rsp_modules):
    rule = _rule("f11-goal-missed")
    assert rule["guard"] == ["top"] and rule["unless"] == []
    act = _act(rule["predicate"])
    assert "Roadmap changes" in act and "missed goals" in act
    assert "Changes to our Frontier Safety Roadmap and any cases where we failed to meet our goals" in _legend(
        rule["predicate"])


@needs_lean
def test_f12_approval_states_the_submission_not_an_approval(rsp_modules):
    act = _act(_rule("f12-approval")["predicate"])
    assert "sent to the CEO with the RSO" in act and "approved" not in act
    assert "for final review and approval" in _legend(_rule("f12-approval")["predicate"])
    # f12-share reads the approval as its own situation class, not the submission duty.
    assert _unaries(_rule("f12-share")["guard"]) == {"risk_report_approved"}


@needs_lean
def test_f13_redact_p_covers_both_versions_and_keeps_its_reasons_open(rsp_modules):
    rule = _rule("f13-redact-p")
    act, legend = _act(rule["predicate"]), _legend(rule["predicate"])
    assert "public" in act and "regular-clearance" in act
    assert "..." not in legend and "regular-clearance Anthropic employees" in legend
    assert "include but are not limited to" in legend
    assert _unaries(rule["guard"]) == {"redaction_reason_listed"}


@needs_lean
def test_f23_names_the_prior_draft_baseline(rsp_modules):
    predicate = _rule("f23-publish")["predicate"]
    assert "prior-draft differences" in _act(predicate) and "Change Log" in _act(predicate)
    assert "prior to or on its effective date" in _legend(predicate)
    assert "the differences from the prior draft in the Change Log" in _legend(predicate)


@needs_lean
def test_f7_act_and_legend_carry_the_continuation_determinations(rsp_modules):
    predicate = _rule("f7-publish")["predicate"]
    assert "continuation determinations" in _act(predicate)
    assert ("discussing the risks of our systems and how we have made determinations about whether to continue AI "
            "development and deployment in light of the risks") in _legend(predicate)


@needs_lean
def test_f16_legend_keeps_one_or_more_and_the_act_picks_no_quantifier(rsp_modules):
    predicate = _rule("f16-share-one-week")["predicate"]
    act = _act(predicate)
    assert "the external reviewers" in act
    reviewers = act.split(" shared with ")[1].split(" within ")[0]
    assert reviewers == "the external reviewers"  # no new quantifier: neither "at least one" nor "every"
    assert ("with one or more external reviewers within one week of submitting the same report to our Board and "
            "LTBT") in _legend(predicate)


@needs_lean
def test_f6_f10_f18_legends_carry_the_dropped_qualifiers(rsp_modules):
    legends = {b: _legend(_rule(b)["predicate"]) for b in ("f6-maintain", "f10-candid-default", "f18-rso")}
    assert "ambitious but achievable goals for improving our risk mitigations" in legends["f6-maintain"]
    assert "raising the bar over time" in legends["f6-maintain"]
    assert "how we see the risks of our systems and our state of preparedness for them" in legends[
        "f10-candid-default"]
    assert "a designated member of staff who is responsible for the implementation of this policy" in legends[
        "f18-rso"]
    spans = {u["id"]: u for u in json.loads((RSP / "spans.json").read_text())["units"]}
    assert spans["s4-rso-duties"]["status"] == "LABELLED"


def test_fix_3_items_keep_their_saved_answers():
    """The saved run: every item these units move keeps its answer (section 29's K1, K14, D5, K17, K22a, T5)."""
    saved = {r["id"]: r for r in json.loads((RSP / "results.json").read_text())["comparison"]}
    assert all(saved[i]["status"] == "agree" for i in ("K1", "K7", "K14", "D5", "K17", "K22a", "K22b", "T5", "C4"))
    assert {i: saved[i]["ve"] for i in ("T7", "C-doc")} == {"T7": "NONE", "C-doc": "NONE"}


def test_regulated_predicates_stay_64_after_fix_3():
    regulated = [n for n, e in rsp_vocabulary.environment()["vocabulary"]["predicates"].items() if "regulated" in e]
    assert len(regulated) == 64
    assert {"goal_miss_addressed", "executive_approved"}.isdisjoint(regulated)
