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
