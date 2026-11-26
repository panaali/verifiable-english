"""Fidelity fix of the newcomer tour's text (stop 6, Winter Fuel Payment, usecases/eligibility).

Rows statute-latent-tour-wfp-b15-I23 and -I25, from the fidelity check of the tour's texts
(reviews/spare/statute-corpus/fidelity-check/sweep/tour-wfp-b15.md, FL01 and FL03; the fix record is
sweep/tour-wfp-b15/FIX.md there). Each condition is the check seat's test, run with the text's own
runner (run.py's staged route, and ask.py's printout).

- I23 (FIXED): S1 reg. 4(6)(b), "Paragraph (5) does not apply where ... regulation 5(2) applies", and
  reg. 5(2) (a relevant benefit for the week awarded by a later decision that s.115(1) of the
  Immigration and Asylum Act 1999 ceases to apply). The frozen R12 concluded 4(5), so "not entitled",
  for every person with neither a reg. 5(1) payment nor a timely claim. No profile field says whether
  reg. 5(2) applies, so R12 now concludes 4(5) only for a person paid no relevant benefit for the week
  (5(2) cannot apply) and leaves the rest open: VE gives no answer. The check seat's profile (born
  1950, resident in England, income support, no payment without a claim, no claim) was answered NO at
  tour 4454de2d3f and on after-release; it is now OPEN. Its residence start, 1950-01-01, is before the
  checker's first date (1970: ask.py refuses it, DateRange), so the profile states residence from
  1990-01-01, the cases.json default; the week's facts are the same.
- I25 (harmless): S2:166 "If you do not opt out and your total income is over £35,000 ...". The runner
  refuses a stated opt-out at input (ask.py: unknown field opted_out), so the check seat's profile
  gets no answer, and a profile silent on it is answered under the printed assumption "The applicant
  has not opted out of the payment", quoting S2:166. Those two tests pass at tour 4454de2d3f and on
  after-release, so the row closed harmless; they stay as guards.
"""
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "usecases" / "eligibility"
sys.path.insert(0, str(HERE))

import ask  # noqa: E402
import run  # noqa: E402
import translation as T  # noqa: E402
from ve.environment import Environment  # noqa: E402

# FL01's profile (sweep/tour-wfp-b15.md), residence stated from the cases.json default day (see above).
I23_PROFILE = {"id": "FL01", "applicant": {"birth": "1950-01-01", "ew_from": "1990-01-01",
                                           "benefits": ["income_support"], "claim": {"automatic": False}},
               "housemate": None}
# FL03's profile without the opt-out (the runner has no field for it): under 80, alone, no relevant benefit,
# income GBP 40,000.
I25_PROFILE = {"id": "FL03", "applicant": {"birth": "1960-01-01", "ew_from": "1990-01-01", "income": "40000.00"},
               "housemate": None}


@pytest.fixture(scope="module")
def runner():
    env = Environment(T.environment())
    return env, run.Prover(env), T.load_cases()["defaults"]


def answers(runner, case, mutant=None):
    env, prover, defaults = runner
    return run.run_profile(prover, env, ask.check_profile(case), defaults, mutant=mutant)[0]["staged"]


def with_applicant(case, **fields):
    return {**case, "applicant": {**case["applicant"], **fields}}


# --- I23: condition tests (fail at tour 4454de2d3f and on after-release) ---------------------------------

def test_i23_relevant_benefit_without_claim_or_payment_is_not_answered_no(runner):
    """The check seat's profile: reg. 5(2) may apply (a relevant benefit for the week, no claim, no reg. 5(1)
    payment), so 4(6)(b) may disapply 4(5). The frozen R12 answered NO; the source does not decide it on these
    facts, so VE gives no answer."""
    got = answers(runner, I23_PROFILE)
    assert got["Q1"] != "NO"
    assert got == {"Q1": "OPEN", "Q2": "OPEN", "Q3": "OPEN", "Q3gbp": "OPEN", "Q4": "OPEN"}


def test_i23_relevant_benefit_with_a_late_claim_is_not_answered_no(runner):
    """The same with a claim made after 31 March 2027: 4(5) applies unless 5(2) does, still not decided."""
    case = with_applicant(I23_PROFILE, claim={"automatic": False, "claimed_on": "2027-05-01"})
    assert answers(runner, case)["Q1"] == "OPEN"


def test_i23_ask_py_gives_no_answer_and_says_why():
    """ask.py's printout (the tour's stop 6 command) for the check seat's profile: no 'Entitled: NO', and the
    reg. 5(2) assumption is printed with the OPEN answer."""
    out = ask.ask(ask.check_profile({k: v for k, v in I23_PROFILE.items() if k != "id"}), lean=False)
    assert not out.startswith("Entitled: NO")
    assert "Regulation 5(2)" in out and "section 115(1) of the Immigration and Asylum Act 1999" in out


def test_m35_frozen_r12_is_killed(runner):
    """Planted error M35 restores the frozen R12 (4(5) whenever there is no claim and no reg. 5(1) payment):
    it answers the condition profile NO, which the fixed rule does not."""
    assert "M35" in T.FIX_MUTANTS and "M35" not in T.MUTANTS
    assert answers(runner, I23_PROFILE, mutant="M35")["Q1"] == "NO"
    assert answers(runner, I23_PROFILE)["Q1"] != answers(runner, I23_PROFILE, mutant="M35")["Q1"]


# --- I23: guards (pass before and after: the cases 5(2) cannot reach keep their answers) ---------------

def test_i23_no_relevant_benefit_without_claim_or_payment_is_still_no(runner):
    """Reg. 5(2) needs a relevant benefit for the week: with none, 4(5) applies as before."""
    case = with_applicant(I23_PROFILE, benefits=["state_pension"])
    assert answers(runner, case)["Q1"] == "NO"


@pytest.mark.parametrize("claim", [{"automatic": True}, {"automatic": False, "claimed_on": "2027-03-31"}])
def test_i23_paid_without_claim_or_claimed_in_time_is_still_yes(runner, claim):
    assert answers(runner, with_applicant(I23_PROFILE, claim=claim))["Q1"] == "YES"


# --- I25: the check seat's test closed harmless (passes at tour 4454de2d3f and on after-release) ---------

def test_i25_a_stated_opt_out_is_refused_at_input():
    """The check seat's profile states opted_out(applicant): the runner has no such field and refuses the
    profile, so it never answers 'HMRC takes it back' for a person who says they opted out."""
    with pytest.raises(ask.ProfileError, match="opted_out"):
        ask.check_profile(with_applicant(I25_PROFILE, opted_out=True))


def test_i25_unstated_opt_out_answer_prints_the_no_opt_out_assumption(runner):
    """Silent on opting out, the runner answers Q3 YES and prints the assumption it rests on, quoting S2:166."""
    assert answers(runner, I25_PROFILE)["Q3"] == "YES"
    out = ask.ask(ask.check_profile({k: v for k, v in I25_PROFILE.items() if k != "id"}), lean=False)
    assert "Taken back by HMRC: YES" in out
    assert "The applicant has not opted out of the payment" in out
    assert "If you do not opt out and your total income is over £35,000" in out
