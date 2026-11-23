"""relb-fixes: release B's recorded faults in the Winter Fuel Payment checker (usecases/eligibility).

Faults (manage-agents reviews/relb/FAULTS.md "Take first", and the headline encoder's FAULTS.md F1-F8):
- O2 / F1 / F2: the birth-date bridges B2/B3, now worked out from Sch. 4 for any birth date and, where the sex is
  given, by the rule for that sex (14 March 1940: a woman on 14 March 2000, a man on 14 March 2005).
- O3 / F8: payment without a claim: a reg. 5(1) payment counts only on or before 31 March 2027 (R12); with none
  stated, the guide's list of who need not claim (S2:75-90) decides (encoding rule O3, `paid_without_claim`).
- F7: Q3 as the GBP amount taken back (`Q3gbp`), a named answer with its own Lean-admitted document.
- F3: remand, then a sentence, in one custody (`custody.sentenced_from`; R9 reads the sentence start).
- F6: `scot_ni_from` is the day the person most recently became resident in Scotland or Northern Ireland.
Each test fails on main before this change (no `age_bounds`, `guide_no_claim`, profiles C28-C33 or `Q3gbp`).
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "usecases" / "eligibility"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import reference  # noqa: E402
import run  # noqa: E402
import translation as T  # noqa: E402
from ve.environment import Environment  # noqa: E402

D = date.fromisoformat

# The 21 bridge keys of release B's headline round, with the values the grader checked against Sch. 4 para. 1
# (manage-agents reviews/relb/indq/graded/bridges-check.md, "Per key": 21 of 21 right). The checker must now
# give each of them by itself, with no hand entry: (birth, sex or None, pensionable-age day, 80th birthday).
HEADLINE_BRIDGE_KEYS = [
    ("1940-03-14", "woman", "2000-03-14", "2020-03-14"), ("1940-03-14", "man", "2005-03-14", "2020-03-14"),
    ("1945-03-14", "woman", "2005-03-14", "2025-03-14"), ("1946-09-26", "woman", "2006-09-26", "2026-09-26"),
    ("1946-09-27", "woman", "2006-09-27", "2026-09-27"), ("1946-09-28", "man", "2011-09-28", "2026-09-28"),
    ("1950-03-14", "man", "2015-03-14", "2030-03-14"), ("1950-04-06", "woman", "2010-05-06", "2030-04-06"),
    ("1952-03-14", "man", "2017-03-14", "2032-03-14"), ("1953-12-06", "man", "2019-03-06", "2033-12-06"),
    ("1955-03-14", None, "2021-03-14", "2035-03-14"), ("1956-03-14", None, "2022-03-14", "2036-03-14"),
    ("1960-04-05", None, "2026-04-05", "2040-04-05"), ("1960-06-27", None, "2026-09-27", "2040-06-27"),
    ("1960-06-28", None, "2026-09-28", "2040-06-28"), ("1960-07-31", None, "2026-11-30", "2040-07-31"),
    ("1960-12-31", None, "2027-09-30", "2040-12-31"), ("1961-01-31", None, "2027-11-30", "2041-01-31"),
    ("1961-03-06", None, "2028-03-06", "2041-03-06"), ("1977-04-06", None, "2044-05-06", "2057-04-06"),
    ("1978-04-06", None, "2046-04-06", "2058-04-06"),
]


def _key_mismatches(bounds):
    """Keys whose bounds (a function like T.age_bounds) are not exactly the checked days."""
    out = []
    for birth, sex, pa, eighty in HEADLINE_BRIDGE_KEYS:
        got_pa, got_80 = bounds(birth, sex)
        if got_pa != (D(pa), D(pa)) or got_80 != (D(eighty), D(eighty)):
            out.append((birth, sex, got_pa, got_80))
    return out


def recorded():
    return json.loads((HERE / "results.json").read_text(encoding="utf-8"))


# --- O2 / F1 / F2: birth-date bridges ---------------------------------------------------------------------

def test_no_hand_tables_left():
    assert not hasattr(T, "PENSIONABLE_AGE") and not hasattr(T, "EIGHTIETH")


def test_all_21_headline_bridge_keys_come_out_right_without_a_hand_entry():
    assert _key_mismatches(T.age_bounds) == []


def test_planted_sex_dropped_is_caught():
    """Plant: the bridge ignores the sex. The two 1940-03-14 keys (and the other sexed keys) no longer match."""
    planted = _key_mismatches(lambda birth, sex: T.age_bounds(birth, None))
    assert ("1940-03-14", "woman") in {(b, s) for b, s, *_ in planted}
    assert ("1940-03-14", "man") in {(b, s) for b, s, *_ in planted}


def test_sex_decides_where_sch4_does_f2():
    assert T.age_bounds("1940-03-14", "woman")[0] == (D("2000-03-14"), D("2000-03-14"))  # rule (2), at 60
    assert T.age_bounds("1940-03-14", "man")[0] == (D("2005-03-14"), D("2005-03-14"))  # rule (1), at 65
    assert T.age_bounds("1940-03-14")[0] == (D("2000-03-14"), D("2005-03-14"))  # not given: both kept
    facts = {f["id"]: f["formula"] for f in T.age_facts("applicant", "1940-03-14", "woman")}
    assert facts["applicant.pa_date"] == ["date_on", T.num("applicant", "pa_date"), T.day("2000-03-14")]
    with pytest.raises(ValueError):
        T.age_bounds("1940-03-14", "female")


def test_sex_agrees_with_the_reference_for_every_birth_before_6_april_1950():
    """Rules (1) and (2) against the reference's own anniversaries, one birth a fortnight 1930 to 1950."""
    born = date(1930, 1, 1)
    while born < date(1950, 4, 6):
        for sex, years in (("man", 65), ("woman", 60)):
            days = reference.anniversaries(born, years)
            assert T.age_bounds(born.isoformat(), sex)[0] == (min(days), max(days)), (born, sex)
        born = date.fromordinal(born.toordinal() + 14)


def test_a_profile_with_a_sex_is_read():
    case = {"id": "X", "applicant": {"birth": "1940-03-14", "sex": "man"}, "housemate": None}
    facts = {f["id"]: f["formula"] for f in T.profile_facts(case, T.load_cases()["defaults"])}
    assert facts["applicant.pa_date"][2] == T.day("2005-03-14")


@pytest.mark.parametrize("birth,pa", [("1960-06-27", "2026-09-27"), ("1960-06-28", "2026-09-28")])
def test_guide_pensionable_age_cutoff(birth, pa):
    """Born 27 Jun 1960: pensionable age 27 Sep 2026 (in the week); 28 Jun 1960: 28 Sep (after it)."""
    assert T.age_bounds(birth)[0] == (D(pa), D(pa))
    op = {f["id"]: f["formula"][0] for f in T.age_facts("applicant", birth)}["applicant.pa_date"]
    assert op == "date_on"
    assert reference.reached_pensionable_age({"birth": D(birth)}) is (D(pa) <= D("2026-09-27"))


@pytest.mark.parametrize("birth,eighty", [("1946-09-27", "2026-09-27"), ("1946-09-28", "2026-09-28")])
def test_guide_age_80_cutoff(birth, eighty):
    """Born 27 Sep 1946: 80 on 27 Sep 2026 (in the week); 28 Sep 1946: 80 on 28 Sep (after it)."""
    assert T.age_bounds(birth)[1] == (D(eighty), D(eighty))
    assert reference.reached_80({"birth": D(birth)}) is (D(eighty) <= D("2026-09-27"))


# --- O3 / F8: payment without a claim ---------------------------------------------------------------------

def _source_lines():
    return (HERE / "source" / "wfp-print.txt").read_text(encoding="utf-8").split("\n")


def test_guide_list_is_read_from_the_guide():
    constants, others = T.guide_no_claim()
    assert constants == ("state_pension", "pension_credit", "universal_credit", "attendance_allowance",
                         "income_related_esa")
    assert len(others) == 7 and "Personal Independence Payment (PIP)" in others
    assert "income_support" not in constants and "income_based_jsa" not in constants


@pytest.mark.parametrize("line,text", [
    (75, "You need to claim if you get any of the following:"),  # the lead-in turned round
    (77, "Pension Credit, if you also claim it"),  # an item that is not a bare benefit name
    (89, "you’ve got the Winter Fuel Payment before"),  # S2:88-90 changed
])
def test_planted_guide_list_changes_are_refused(line, text):
    lines = _source_lines()
    lines[line - 1] = text
    with pytest.raises(ValueError):
        T.guide_no_claim(lines)


def _answers(case_id, mutant=None):
    data = T.load_cases()
    case = next(c for c in data["cases"] if c["id"] == case_id)
    env = Environment(T.environment())
    return run.run_profile(run.Prover(env), env, case, data["defaults"], mutant=mutant)[0]["staged"]


def test_payment_on_31_march_and_after_it_differ_f8():
    assert _answers("C31")["Q1"] == "YES"  # paid without a claim on 2027-03-31
    assert _answers("C30")["Q1"] == "NO"  # on 2027-04-01: not a reg. 5(1) payment
    assert _answers("C30", "M33")["Q1"] == "YES"  # the mutant without the bound misses it


def test_planted_guide_list_without_state_pension_is_caught(monkeypatch):
    """Plant: the encoding rule without the guide's list (or without State Pension on it). C28 (State Pension, no
    claim) and C32 (PIP, no claim) are no longer paid without a claim and their answers change to NO."""
    assert _answers("C28")["Q1"] == "YES" and _answers("C32")["Q1"] == "YES"
    with monkeypatch.context() as m:  # the encoding rule removed: only a stated payment counts
        m.setattr(T, "paid_without_claim", lambda p: bool(p["claim"].get("automatic")))
        assert _answers("C28")["Q1"] == "NO" and _answers("C32")["Q1"] == "NO"
    monkeypatch.setattr(T, "GUIDE_NO_CLAIM_BENEFITS", ("pension_credit",))  # State Pension off the list
    with pytest.raises(ValueError):  # now on no list, and C28 does not say it must claim: refused
        _answers("C28")
    monkeypatch.setattr(T, "GUIDE_OTHER_NO_CLAIM", ())
    case = {"id": "X", "applicant": {"birth": "1955-03-14", "benefits": [],
                                     "claim": {"other_benefits": ["Personal Independence Payment (PIP)"]}},
            "housemate": None}
    with pytest.raises(ValueError):
        T.profile_facts(case, T.load_cases()["defaults"])


def test_encoding_rule_o3_is_labelled():
    data = T.load_cases()
    case = next(c for c in data["cases"] if c["id"] == "C28")
    kinds = {f["id"]: f["kind"] for f in T.profile_facts(case, data["defaults"])}
    assert kinds["applicant.paid_without_claim"] == "assumption O3"
    assert kinds["applicant.unclaimed_paid"] == "assumption O3"
    case = next(c for c in data["cases"] if c["id"] == "C31")
    facts = {f["id"]: f for f in T.profile_facts(case, data["defaults"])}
    assert facts["applicant.paid_without_claim"]["kind"] == "fact"
    assert facts["applicant.unclaimed_paid"]["formula"][0] == "date_on"


def test_claim_profiles_recorded():
    got = {p["id"]: p["answers"]["Q1"] for p in recorded()["profiles"]}
    assert {k: got[k] for k in ("C28", "C29", "C30", "C31", "C32")} == {
        "C28": "YES", "C29": "NO", "C30": "NO", "C31": "YES", "C32": "YES"}


@pytest.mark.parametrize("claim,benefits", [
    ({}, []),  # on no list and must_claim not said: the guide does not say (S2:88-90)
    ({"must_claim": True}, ["state_pension"]),  # on the list and must_claim
    ({"automatic": False, "paid_on": "2027-01-10"}, ["state_pension"]),  # a payment day without a payment
    ({"paid_on": "2027-01-10"}, ["state_pension"]),
    ({"automatic": True, "other_benefits": ["Carer’s Allowance"]}, []),
    ({"other_benefits": ["Housing Benefit"]}, []),  # not on the guide's list
])
def test_claim_records_the_guide_does_not_decide_are_refused(claim, benefits):
    case = {"id": "X", "applicant": {"birth": "1955-03-14", "benefits": benefits, "claim": claim}, "housemate": None}
    with pytest.raises(ValueError):
        T.profile_facts(case, T.load_cases()["defaults"])


# --- F7: Q3 as the amount taken back ----------------------------------------------------------------------

def test_q3_amount_is_a_named_lean_admitted_answer():
    results = recorded()
    by_id = {p["id"]: p for p in results["profiles"]}
    for p in results["profiles"]:
        a = p["answers"]
        if a["Q1"] == "YES":
            assert a["Q3gbp"] == (a["Q2"] if a["Q3"] == "YES" else "0.00"), p["id"]
            assert p["lean"]["documents"]["Q3gbp"] is True, p["id"]
        else:
            assert a["Q3gbp"] == "N/A" and "Q3gbp" not in p["lean"]["documents"], p["id"]
    assert by_id["D02"]["answers"]["Q3gbp"] == "200.00" and by_id["A01"]["answers"]["Q3gbp"] == "0.00"
    assert run.answer_targets({"Q1": "YES", "Q2": "200.00", "Q3": "YES", "Q3gbp": "200.00", "Q4": "0.00"})[
        "Q3gbp"] == "recovered_amount"


# --- F3: remand then sentence -----------------------------------------------------------------------------

def test_remand_then_sentence_in_the_week_f3():
    assert _answers("C33")["Q1"] == "YES"  # remand on QW0: not under a sentence throughout the week
    assert _answers("C33", "M34")["Q1"] == "NO"  # reading the custody start as the sentence start
    assert _answers("B07")["Q1"] == "NO"  # sentenced throughout: still excluded


def test_sentence_start_outside_a_sentence_is_refused():
    custody = {"from": "2026-09-01", "sentenced_from": "2026-09-22", "release": "2026-12-01", "sentenced": False}
    case = {"id": "X", "applicant": {"birth": "1955-03-14", "custody": custody}, "housemate": None}
    with pytest.raises(ValueError):
        T.profile_facts(case, T.load_cases()["defaults"])


# --- F6: scot_ni_from -------------------------------------------------------------------------------------

def test_scot_ni_from_means_the_day_of_becoming_resident_f6():
    words = T.ROLE_INTEGERS["scot_ni_from"][1]
    assert "most recently becoming" in words and "first day" not in words
    env = json.dumps(T.environment())
    assert "most recently becoming ordinarily resident in Scotland or Northern Ireland" in env
