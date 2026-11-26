"""GitHub Sponsors 'Terms For Sponsored Developer' (usecases/github_sponsors): the Stripe Connect cross-border minimum is
compared with "the balance accrued since the last payout" (unit 38), not with the month's own Sponsored Developer
Payment (row statute-corpus-github-sponsors-wrong-s028; DRI decide wake 20261125T2100Z,
reviews/dri-decisions-20261125-sponsors-s028.md item 1).

The frozen translation (5336e71bbc, evidence branch statute-github-sponsors-developer-1125 @ 60d692157a) made paid(m)
from mn(m) <= sdp(m), so a month below the minimum was lost instead of carried: cross-family S028-2 / S028-3 (Iris,
$49.00 March, nothing in April, $2.00 May, minimum $50.00) answered "no" / $0.00 where unit 38 pays $51.00 on 22 June.
These tests pin the rule (R6, translation._u38):
* two months below a cross-border minimum whose sum reaches it -> paid at the next payout date, for the carried sum;
* a payout resets the carry; a month whose carried balance the facts leave unknown gets no answer (OPEN, conservative);
* the carried Stripe balance counts matching money (unit 38 excludes nothing; unit 39's exclusion is ACH / wire only),
  and the 'payout' answer of a Stripe payee is that balance;
* a month paid with the first payments (unit 37: one payout may hold several months) carries and resets nothing, and
  its cross-border minimum is not read (OPEN); the same guard on the ACH / wire balance (review HIGH 2026-11-25);
* a Stripe developer who leaves below the minimum: OPEN, not 'not paid';
* the domestic ACH / wire $100 path (unit 39, S029) is unchanged;
* planted error M19 (the frozen 5336e71bbc reading) flips S028-2 / S028-3 back to "no" / $0.00.
Each answer is derived by the use case's own staged prover (usecases/github_sponsors/run.py run_sub); the question-set
run replays every certificate in Lean. Fails on 5336e71bbc / 60d692157a (no sbal, no M19, the month compared alone).
"""
from pathlib import Path

import pytest

from tests.usecase_scope import usecase_scope

GS = Path(__file__).resolve().parents[1] / "usecases" / "github_sponsors"


@pytest.fixture(scope="module")
def gs():
    with usecase_scope(GS):
        import cases as K
        import encode as E
        import run as R
        import translation as T
        yield K, E, R, T


def ask(gs, spec, *qs, mutant=None):
    R = gs[2]
    return R.run_sub({"spec": spec, "questions": [{"qid": q, "form": f} for q, f in qs]}, mutant)[0]


def val(a):
    return a.get("value", a["answer"])


def payee(gs, fd="2026-10-23"):
    """A US individual paid through Stripe Connect, first sponsorship long before the months asked."""
    E = gs[1]
    return E.Sub().dev("acc", "ind", "sc", "us").val("ad", "p", "2026-01-01").val("fd", "p", fd)


def test_two_months_below_a_cross_border_minimum_whose_sum_reaches_it_paid_at_the_next_payout_date(gs):
    """$30 (March) and $25 (April), each below a $50 minimum: March is not paid; April's payout, on its 22nd of May,
    pays the $55 accrued since the last payout."""
    spec = (payee(gs).month("m1", "2027-03-01", "chs", mn="50.00").pay("y1", "m1", "2027-03-31", "30.00", "ksp")
            .month("m2", "2027-04-01", mn="50.00").pay("y2", "m2", "2027-04-30", "25.00", "ksp"))
    got = ask(gs, spec, ("m1", ("yn", "paid", "m1")), ("m2", ("yn", "paid", "m2")), ("d2", ("date", "pdy", "m2")),
              ("s2", ("amt", "sbal", "m2")), ("o2", ("payout", "m2", "2027-05-22")))
    assert {q: val(a) for q, a in got.items()} == {"m1": "no", "m2": "yes", "d2": "2027-05-22", "s2": "55.00",
                                                   "o2": "55.00"}


def test_s028_iris_june_payout_is_made_for_51(gs):
    """The cross-family case itself (cases.py S028, the frozen encoding): $49 + $0 + $2 reaches $50 on 22 June."""
    K = gs[0]
    case = [c for c in K.CASES if c["id"] == "S028"][0]
    got = gs[2].run_case(case)
    assert {q: val(a) for q, a in got.items()} == {"S028-1": "no", "S028-2": "yes", "S028-3": "51.00"}


def test_mutant_m19_restores_the_frozen_reading(gs):
    """M19 (the month's own payment against the minimum) gives back the frozen wrong answers."""
    K, T = gs[0], gs[3]
    assert "M19" in T.MUTANTS
    case = [c for c in K.CASES if c["id"] == "S028"][0]
    got = gs[2].run_case(case, "M19")
    assert {q: val(a) for q, a in got.items()} == {"S028-1": "no", "S028-2": "no", "S028-3": "0.00"}


def test_a_payout_resets_the_carried_balance(gs):
    """$40 + $20 reaches $50 (paid in the second month); the third month's $5 starts again from nothing."""
    spec = (payee(gs).month("m1", "2027-03-01", "chs", mn="50.00").pay("y1", "m1", "2027-03-31", "40.00", "ksp")
            .month("m2", "2027-04-01", mn="50.00").pay("y2", "m2", "2027-04-30", "20.00", "ksp")
            .month("m3", "2027-05-01", mn="50.00").pay("y3", "m3", "2027-05-31", "5.00", "ksp"))
    got = ask(gs, spec, ("p2", ("yn", "paid", "m2")), ("s2", ("amt", "sbal", "m2")), ("p3", ("yn", "paid", "m3")),
              ("s3", ("amt", "sbal", "m3")))
    assert {q: val(a) for q, a in got.items()} == {"p2": "yes", "s2": "60.00", "p3": "no", "s3": "5.00"}


def test_unknown_carried_balance_is_not_answered(gs):
    """A month below the minimum that does not start the chain, with no earlier month in the case: what is carried
    into it is unknown, so neither 'paid' nor 'not paid' is proved (OPEN), even though the month alone is below."""
    spec = payee(gs).month("m1", "2027-03-01", mn="50.00").pay("y1", "m1", "2027-03-31", "30.00", "ksp")
    got = ask(gs, spec, ("p1", ("yn", "paid", "m1")), ("o1", ("payout", "m1", "2027-04-22")))
    assert val(got["p1"]) == "OPEN" and val(got["o1"]) == "OPEN"


def test_matching_money_counts_in_the_stripe_balance(gs):
    """Unit 38's balance is the Sponsored Developer Payments accrued (unit 5: 'plus any applicable Matching Funds');
    only unit 39's ACH / wire threshold leaves matching money out."""
    spec = (payee(gs).month("m1", "2027-03-01", "chs", mn="50.00").pay("y1", "m1", "2027-03-31", "40.00", "ksp")
            .pay("y2", "m1", "2027-03-31", "20.00", "kmf"))
    got = ask(gs, spec, ("p1", ("yn", "paid", "m1")), ("s1", ("amt", "sbal", "m1")))
    assert {q: val(a) for q, a in got.items()} == {"p1": "yes", "s1": "60.00"}


def test_months_paid_with_the_first_payments_neither_carry_nor_reset(gs):
    """Review HIGH (2026-11-25): first sponsorship 23 Nov 2026 -> the first payments 60 days later, 22 Jan 2027, hold
    November and December in ONE payout (unit 37). Treating November as its own payout reset the carry and proved
    'January paid, $55' (December's $10 + January's $45) although the $10 went out on 22 January. Now: no cross-border
    answer for a first-payment month and no balance carried out of one: January is OPEN (the frozen reading, M19,
    answers 'no': $45 alone)."""
    spec = (payee(gs, fd="2026-11-23").month("m1", "2026-11-01", "chs", mn="50.00")
            .pay("y1", "m1", "2026-11-23", "60.00", "ksp")
            .month("m2", "2026-12-01", mn="50.00").pay("y2", "m2", "2026-12-31", "10.00", "ksp")
            .month("m3", "2027-01-01", mn="50.00").pay("y3", "m3", "2027-01-31", "45.00", "ksp"))
    qs = (("f1", ("yn", "fst", "m1")), ("f2", ("yn", "fst", "m2")), ("f3", ("yn", "fst", "m3")),
          ("p1", ("yn", "paid", "m1")), ("p2", ("yn", "paid", "m2")), ("p3", ("yn", "paid", "m3")),
          ("s3", ("amt", "sbal", "m3")), ("o3", ("payout", "m3", "2027-02-22")))
    got = {q: val(a) for q, a in ask(gs, spec, *qs).items()}
    assert got == {"f1": "yes", "f2": "yes", "f3": "no", "p1": "OPEN", "p2": "OPEN", "p3": "OPEN", "s3": "OPEN",
                   "o3": "OPEN"}
    old = {q: val(a) for q, a in ask(gs, spec, *qs, mutant="M19").items()}
    assert old["p3"] == "no"


def test_ach_balance_is_not_carried_out_of_a_first_payment_month(gs):
    """The same guard on the ACH / wire balance (unit 39): November and December 2026 are paid with the first payments
    (22 Jan 2027); January's balance is not computed from them (OPEN)."""
    E = gs[1]
    spec = (E.Sub().dev("acc", "ind", "ach", "us").val("ad", "p", "2026-01-01").val("fd", "p", "2026-11-23")
            .month("m1", "2026-11-01", "chs").pay("y1", "m1", "2026-11-23", "120.00", "ksp")
            .month("m2", "2026-12-01").pay("y2", "m2", "2026-12-31", "10.00", "ksp")
            .month("m3", "2027-01-01").pay("y3", "m3", "2027-01-31", "95.00", "ksp"))
    got = ask(gs, spec, ("f2", ("yn", "fst", "m2")), ("b3", ("amt", "bal", "m3")), ("p3", ("yn", "paid", "m3")))
    assert {q: val(a) for q, a in got.items()} == {"f2": "yes", "b3": "OPEN", "p3": "OPEN"}


def test_matching_money_in_an_unpaid_month_carries_and_is_paid_out(gs):
    """Review LOW/MEDIUM: March $30 + $15 matching (below $50) carries into April's $10: $55 accrued, April paid, and
    the 22 May payout is that Stripe balance ($55.00), not the matching-free ACH balance ($40.00)."""
    spec = (payee(gs).month("m1", "2027-03-01", "chs", mn="50.00").pay("y1", "m1", "2027-03-31", "30.00", "ksp")
            .pay("y2", "m1", "2027-03-31", "15.00", "kmf")
            .month("m2", "2027-04-01", mn="50.00").pay("y3", "m2", "2027-04-30", "10.00", "ksp"))
    got = ask(gs, spec, ("p1", ("yn", "paid", "m1")), ("p2", ("yn", "paid", "m2")), ("s2", ("amt", "sbal", "m2")),
              ("o2", ("payout", "m2", "2027-05-22")))
    assert {q: val(a) for q, a in got.items()} == {"p1": "no", "p2": "yes", "s2": "55.00", "o2": "55.00"}


def test_a_stripe_leaver_below_the_minimum_is_not_answered_not_paid(gs):
    """Review LOW: no text says a Stripe developer's remaining balance below a cross-border minimum is withheld when
    they leave (39's leaving sentence is ACH / wire): OPEN, not 'no'."""
    spec = payee(gs).month("m1", "2027-03-01", "chs", "left", mn="50.00").pay("y1", "m1", "2027-03-31", "10.00", "ksp")
    got = ask(gs, spec, ("p1", ("yn", "paid", "m1")))
    assert val(got["p1"]) == "OPEN"


def test_without_a_cross_border_minimum_stripe_pays_regardless_of_the_amount(gs):
    spec = (payee(gs).month("m1", "2027-03-01", "chs").pay("y1", "m1", "2027-03-31", "1.00", "ksp")
            .month("m2", "2027-04-01").pay("y2", "m2", "2027-04-30", "1.00", "ksp"))
    got = ask(gs, spec, ("p1", ("yn", "paid", "m1")), ("p2", ("yn", "paid", "m2")), ("s2", ("amt", "sbal", "m2")))
    assert {q: val(a) for q, a in got.items()} == {"p1": "yes", "p2": "yes", "s2": "1.00"}


def test_domestic_ach_threshold_path_unchanged(gs):
    """Unit 39 (S029, ACH, $99.99 then $0.01): its balance already accrued (bal); not changed by this row. March is not
    paid; exactly $100.00 after an accrual stays OPEN (D6(b), the frozen reading)."""
    K = gs[0]
    case = [c for c in K.CASES if c["id"] == "S029"][0]
    got = gs[2].run_case(case)
    assert {q: val(a) for q, a in got.items()} == {"S029-1": "no", "S029-2": "OPEN", "S029-3": "OPEN"}
