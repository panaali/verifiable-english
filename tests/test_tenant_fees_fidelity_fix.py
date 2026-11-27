"""Tenant Fees Act 2019 (usecases/tenant_fees): four latent departures found by the fidelity sweep, fixed in the rules
(rows statute-latent-tenant-fees-I7, -I10, -I15, -I39; manage-agents
reviews/spare/statute-corpus/fidelity-check/sweep/tenant-fees.md FL01-FL05). Each row test is the check seat's own test,
run with the text's own runner (usecases/tenant_fees/run.py run_case: the staged prover over
usecases/tenant_fees/translation.py and encode.py; the question-set run replays every certificate in Lean).

* I7 FL01 (unit 8): s. 1(8)(a) disapplies s. 1(7) when the other requirement is prohibited by s. 1 "or section 2". s. 2
  (a letting agent's requirements) is not carried, so when the other requirement is the agent's (new fact
  agent_imposed) and could be a prohibited one, s18 is left open: the option's s. 1 answer is refused, not YES.
* I10 FL02 (unit 11): s. 3(1) closed over the in-scope Sch. 1 paragraphs only, so rent (para. 1), a termination payment
  (para. 7) or a communication-service payment (para. 11) came out "prohibited in full". New facts rent_payment,
  termination_payment, communication_payment: when one holds, "permitted" is left open and nothing fixes the amount.
* I15 FL03 + FL04 (one unit, units 20/54 "excused" for Sch. 1 para. 3(5)(c)): FL04: an earlier deposit that para. 5
  still requires to be repaid (no notice) was counted as excused; now excused needs no repayment duty at all
  (must_repay, para. 3 or 5), and when para. 5's is the only duty excused is left open (whether its period had ended
  when the later deposit was paid is not compared; the audit's HIGH). FL03: when para. 6 applied part of the earlier
  deposit and the rest must be repaid, whether the unrepaid part is exactly the applied part is not in the vocabulary:
  excused is left open (refused).
* I39 FL05 (unit 54 p13): para. 13(a) "breaches section 1 or 2": an instructed agent's requirement (agent_imposed)
  imposed before the deadline that could be a prohibited one leaves p13 open, so Q3 is refused, not NO.
  I7 and I39 share one cause (s. 2 not carried, D4) and one new fact (agent_imposed).

Each row test fails on the frozen rules (9e77b4cef1) and on the merge with after-release (a2ce723706; after-release has
no usecases/tenant_fees, so the merge leaves it unchanged). On the frozen code the vocabulary the fix adds does not
exist; the helper drops what the vocabulary in use lacks, so a frozen run fails by behaviour, not by a missing name.
M6-M9 restore the frozen rules and are killed here: each gives the frozen answer again. The guard tests pass on both.

Set TF_FIDFIX_UC to run these tests against another copy of usecases/tenant_fees (the frozen one).
"""
import os
from pathlib import Path

import pytest

from tests.usecase_scope import usecase_scope

UC = Path(os.environ.get("TF_FIDFIX_UC") or Path(__file__).resolve().parents[1] / "usecases" / "tenant_fees")
PAY_T = ["is_payment", "payer_tenant"]
HD = PAY_T + ["by_or_for_tenant", "before_grant", "intended_schedule2", "for_tenancy_event"]


@pytest.fixture(scope="module")
def uc():
    with usecase_scope(UC):
        import encode as E
        import run as RUN
        import translation as T
        yield T, E, RUN


def Q(*rows):
    return [{"qid": qid, "item": item, "form": form} for (qid, item, form) in rows]


def known(T, c):
    """The case with only the facts the vocabulary in use has (the frozen rules lack the fix's names)."""
    return dict(c, facts={x: [f for f in fs if f in T.FACTS] for x, fs in c["facts"].items()})


def answers(uc, c, mutant=None):
    T, E, RUN = uc
    got = RUN.run_case(known(T, c), mutant)[0]
    return {q: (a["answer"], a.get("gbp"), a.get("date")) for q, a in got.items()}


# --- I7 FL01: the other requirement is a letting agent's (s. 1(8)(a) "or section 2") ------------------------------

def i7_case(other):
    return {"id": "P-I7", "items": ["clean", "ref"],
            "facts": {"clean": ["is_contract", "payer_tenant", "for_tenancy_event", "contract_third_party",
                                "contract_service", "offered_as_option"],
                      "ref": other},
            "links": [("alternative_to", "clean", "ref")],
            "ints": {"annual_rent": "15600.00", "amt_ref": "300.00"},
            "questions": Q(("P-I7-1", "clean", "s1"))}


def test_i7_fl01_agent_referencing_fee_alternative_refused(uc):
    """Check seat FL01: the frozen rules say s. 1 allows the cleaning contract (YES); the agent's £300 referencing fee
    may be prohibited by s. 2, so s. 1(7) may be disapplied: refused."""
    got = answers(uc, i7_case(PAY_T + ["to_agent", "agent_imposed"]))
    assert got["P-I7-1"][0] == "OPEN", got


def test_guard_i7_landlord_prohibited_alternative_contract_barred(uc):
    """The other requirement is the landlord's own prohibited fee: s. 1(8)(a) applies, the contract is barred (NO)."""
    got = answers(uc, i7_case(PAY_T + ["to_landlord", "for_tenancy_event"]))
    assert got["P-I7-1"][0] == "NO", got


def test_guard_i7_agent_permitted_payment_alternative_not_required(uc):
    """The agent's other requirement is a payment with nothing prohibited (a holding deposit of one week's rent): no
    s. 2 breach is possible, so s. 1(7) still applies and the contract is not required (YES), as frozen."""
    c = i7_case(HD + ["to_agent", "agent_imposed"])
    c["ints"]["received_ref"] = "2025-03-01"
    got = answers(uc, c)
    assert got["P-I7-1"][0] == "YES", got


# --- I10 FL02: rent, termination and communication-service payments ------------------------------------------------

def i10_case(kind, extra=()):
    return {"id": "P-I10", "items": ["p"], "facts": {"p": PAY_T + ["to_landlord", "ta_requires", kind, *extra]},
            "ints": {"annual_rent": "15600.00", "amt_p": "1300.00"},
            "questions": Q(("P-I10-1", "p", "permitted"), ("P-I10-2", "p", "amount"))}


def test_i10_fl02_rent_payment_refused(uc):
    """Check seat FL02: £1,300 of monthly rent; frozen Q1 NO and Q2 1300.00; Sch. 1 para. 1 permits rent: refused."""
    got = answers(uc, i10_case("rent_payment"))
    assert got["P-I10-1"][0] == "OPEN" and got["P-I10-2"][0] == "OPEN", got


def test_i10_fl02_termination_payment_refused(uc):
    got = answers(uc, i10_case("termination_payment"))
    assert got["P-I10-1"][0] == "OPEN" and got["P-I10-2"][0] == "OPEN", got


def test_i10_fl02_communication_payment_refused(uc):
    got = answers(uc, i10_case("communication_payment"))
    assert got["P-I10-1"][0] == "OPEN" and got["P-I10-2"][0] == "OPEN", got


def test_guard_i10_unlisted_fee_prohibited_in_full(uc):
    """A payment of no permitted kind (an administration fee) stays prohibited in full."""
    got = answers(uc, i10_case("for_tenancy_event"))
    assert got["P-I10-1"] == ("NO", None, None) and got["P-I10-2"] == ("AMOUNT", "1300.00", None), got


def test_guard_i10_council_tax_still_permitted(uc):
    c = i10_case("council_tax")
    c["facts"]["p"] = PAY_T + ["to_billing_authority", "council_tax", "rent_payment"]
    got = answers(uc, c)
    assert got["P-I10-1"][0] == "YES" and got["P-I10-2"] == ("AMOUNT", "0.00", None), got


# --- I15 FL03 + FL04: an earlier holding deposit and Sch. 1 para. 3(5)(c) ---------------------------------------------

def i15_case(h1_facts, h1_ints):
    ints = {"annual_rent": "15600.00", "amt_h2": "300.00", "received_h2": "2025-03-20", "amt_h1": "300.00",
            "received_h1": "2025-03-01"}
    ints.update(h1_ints)
    return {"id": "P-I15", "items": ["h2", "h1"],
            "facts": {"h2": HD + ["to_landlord"], "h1": HD + ["to_landlord", *h1_facts]},
            "links": [("earlier_same", "h2", "h1")], "ints": ints,
            "questions": Q(("P-I15-1", "h2", "permitted"), ("P-I15-2", "h2", "amount"))}


def test_i15_fl03_part_applied_rest_repaid_refused(uc):
    """Check seat FL03: £200 of H1 applied with consent, £100 repaid; frozen H2 NO, £300 prohibited. Whether the
    unrepaid part is exactly the applied part is not stated in the vocabulary: refused (the check seat's second fix)."""
    got = answers(uc, i15_case(["entered_agreement", "applied_with_consent"],
                               {"taday_h1": "2025-03-05", "applied6_h1": "200.00"}))
    assert got["P-I15-1"][0] == "OPEN" and got["P-I15-2"][0] == "OPEN", got


def test_i15_fl04_para9_without_notice_earlier_refused(uc):
    """Check seat FL04: D1 kept under para. 9 with no notice, so para. 5 requires repayment; frozen D2 YES, 0.00 (para. 5
    ignored). Whether para. 5's duty had arisen when D2 was paid (its period ended) is not compared: refused, not the
    check seat's NO (the audit's HIGH: D2 paid inside the period). D2 is paid after both periods here."""
    c = i15_case(["landlord_decided_not", "false_info", "reasonably_entitled", "believes_exception"],
                 {"decideday_h1": "2025-03-05"})
    c["ints"]["received_h2"] = "2025-03-25"
    got = answers(uc, c)
    assert got["P-I15-1"][0] == "OPEN" and got["P-I15-2"][0] == "OPEN", got


def test_audit_high_later_deposit_inside_para5_period_refused(uc):
    """The audit's example: H2 paid on 12 March, inside both para. 5(2) periods of H1 (decided 10 March; deadline 15
    March), no notice ever given. At that time para. 5 had not yet required repayment: never a definite NO."""
    c = i15_case(["landlord_decided_not", "false_info", "reasonably_entitled", "believes_exception"],
                 {"decideday_h1": "2025-03-10"})
    c["ints"]["received_h2"] = "2025-03-12"
    got = answers(uc, c)
    assert got["P-I15-1"][0] != "NO" and got["P-I15-2"][1] != "300.00", got


def test_guard_i15_whole_earlier_deposit_applied_permitted(uc):
    got = answers(uc, i15_case(["entered_agreement", "applied_with_consent"],
                               {"taday_h1": "2025-03-05", "applied6_h1": "300.00"}))
    assert got["P-I15-1"][0] == "YES" and got["P-I15-2"] == ("AMOUNT", "0.00", None), got


def test_guard_i15_para10_with_notice_in_period_permitted(uc):
    """D1 kept under para. 10 (the tenant withdrew before the deadline) with a notice in writing inside the para. 5(2)(b)
    period: no duty to repay remains, so para. 3(5)(c) fails and D2 is permitted, as frozen."""
    got = answers(uc, i15_case(["tenant_notified", "believes_exception", "notice_given"],
                               {"tnotifyday_h1": "2025-03-05", "noticeday_h1": "2025-03-17"}))
    assert got["P-I15-1"][0] == "YES" and got["P-I15-2"] == ("AMOUNT", "0.00", None), got


def test_i15_para9_notice_in_one_of_two_periods_refused(uc):
    """D1 kept under para. 9 after the landlord decided not to let, notice inside the para. 5(2)(a) period only. The
    rules already read both periods as running here (the notice is in one only: two outcomes), so para. 5 is open and
    so is excused: D2 refused. The frozen rules ignored para. 5 and said permitted."""
    got = answers(uc, i15_case(["landlord_decided_not", "false_info", "reasonably_entitled", "believes_exception",
                                "notice_given"], {"decideday_h1": "2025-03-05", "noticeday_h1": "2025-03-08"}))
    assert got["P-I15-1"][0] == "OPEN" and got["P-I15-2"][0] == "OPEN", got


def test_guard_i15_earlier_unrepaid_no_exception_not_permitted(uc):
    got = answers(uc, i15_case(["landlord_decided_not"], {"decideday_h1": "2025-03-05"}))
    assert got["P-I15-1"] == ("NO", None, None) and got["P-I15-2"] == ("AMOUNT", "300.00", None), got


# --- I39 FL05: para. 13(a) and an instructed agent's requirement -------------------------------------------------------

def i39_case(fee, reqday="2025-03-05"):
    return {"id": "P-I39", "items": ["h", "fee"],
            "facts": {"h": HD + ["to_landlord", "agent_instructed", "tenant_notified"], "fee": fee},
            "links": [("imposed_for", "fee", "h")],
            "ints": {"annual_rent": "15600.00", "amt_h": "300.00", "received_h": "2025-03-01",
                     "tnotifyday_h": "2025-03-10", "amt_fee": "150.00", "reqday_fee": reqday},
            "questions": Q(("P-I39-1", "h", "repay"))}


def test_i39_fl05_agent_referencing_fee_before_deadline_refused(uc):
    """Check seat FL05: the instructed agent requires a £150 referencing fee before the deadline; frozen Q3 NO (para. 10,
    p13 false). Para. 13(a) covers a breach of s. 2, which is not carried: refused."""
    got = answers(uc, i39_case(PAY_T + ["to_agent", "agent_imposed"]))
    assert got["P-I39-1"][0] == "OPEN", got


def test_guard_i39_landlord_breach_before_deadline_repay(uc):
    got = answers(uc, i39_case(PAY_T + ["to_landlord", "for_tenancy_event"]))
    assert got["P-I39-1"] == ("YES", "300.00", "2025-03-21"), got


def test_audit_low_agent_not_instructed_no(uc):
    """Para. 13(a) counts only a letting agent instructed by the landlord: an uninstructed agent's fee before the deadline
    leaves para. 10 in force (Q3 NO), as frozen."""
    c = i39_case(PAY_T + ["to_agent", "agent_imposed"])
    c["facts"]["h"] = [f for f in c["facts"]["h"] if f != "agent_instructed"]
    got = answers(uc, c)
    assert got["P-I39-1"] == ("NO", None, None), got


def test_guard_i39_agent_requirement_after_deadline_no(uc):
    got = answers(uc, i39_case(PAY_T + ["to_agent", "agent_imposed"], reqday="2025-03-20"))
    assert got["P-I39-1"] == ("NO", None, None), got


# --- flags of the fidelity step on the fix (fix/FIDELITY.md FL01-FL03 of the fix's read) ----------------------------

def test_step_fl01_agent_requirement_with_s1_limbs_not_s18_refused(uc):
    """The agent's other requirement carries s. 1(6) limb facts, so its s. 1 classification is a breach; s. 2 decides it
    (s. 2(8) can take it out), so it gives no s18 by the s. 1 test: refused, where the frozen rules said NO."""
    got = answers(uc, i7_case(PAY_T + ["to_agent", "agent_imposed", "for_tenancy_event"]))
    assert got["P-I7-1"][0] == "OPEN", got


def test_step_fl02_landlord_breach_on_deadline_day_refused(uc):
    """The landlord's prohibited fee is imposed ON the deadline day (15 March): 'before the deadline' is read two ways,
    as units 43 and 51 do, so p13 is open and Q3 refused, where the frozen rules said NO."""
    got = answers(uc, i39_case(PAY_T + ["to_landlord", "for_tenancy_event"], reqday="2025-03-15"))
    assert got["P-I39-1"][0] == "OPEN", got


def test_step_fl03_agent_requirement_with_s1_limbs_p13_refused(uc):
    """An agent's requirement whose s. 1 classification is a breach gives no p13 by the s. 1 test (whether s. 2 is
    breached, and whether the agent was instructed, are not carried): refused, where the frozen rules said YES."""
    got = answers(uc, i39_case(PAY_T + ["to_agent", "agent_imposed", "for_tenancy_event"]))
    assert got["P-I39-1"][0] == "OPEN", got


# --- mutants restoring the frozen rules (translation.MUTANTS, run.py --mutants) --------------------------------------

MUTANT_CASES = {
    "M6": (lambda: i7_case(PAY_T + ["to_agent", "agent_imposed"]), "P-I7-1", ("YES", None, None)),
    "M7": (lambda: i10_case("rent_payment"), "P-I10-1", ("NO", None, None)),
    "M8": (lambda: i15_case(["landlord_decided_not", "false_info", "reasonably_entitled", "believes_exception"],
                            {"decideday_h1": "2025-03-05"}), "P-I15-1", ("YES", None, None)),  # fixed: OPEN
    "M9": (lambda: i39_case(PAY_T + ["to_agent", "agent_imposed"]), "P-I39-1", ("NO", None, None)),
}


@pytest.mark.parametrize("mutant", sorted(MUTANT_CASES))
def test_mutant_restoring_frozen_rule_killed(uc, mutant):
    make, qid, frozen = MUTANT_CASES[mutant]
    c = make()
    fixed = answers(uc, c)[qid]
    got = answers(uc, c, mutant)[qid]
    assert got == frozen and got != fixed, (mutant, got, fixed)


def test_mutant_m8_also_restores_fl03(uc):
    c = i15_case(["entered_agreement", "applied_with_consent"], {"taday_h1": "2025-03-05", "applied6_h1": "200.00"})
    assert answers(uc, c, "M8")["P-I15-1"] == ("NO", None, None)
