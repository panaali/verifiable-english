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
    # Opposite direction: with a competitor whose posture is not yet attainable, F25 does require the delay.
    c7 = rsp_run.conflict("C7")
    assert [r["holds"] for r in c7["choices"]] == [False, True]


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
    assert all(row["holds"] == (row["choice"]["RS4"] == "rel") for row in saved["choices"])


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
