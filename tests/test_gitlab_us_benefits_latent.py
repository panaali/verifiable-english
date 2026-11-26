"""GitLab US benefits (usecases/gitlab_us_benefits): two latent departures fixed (rows statute-latent-gitlab-us-benefits-U88
and -U90; reviews/spare/statute-corpus/fidelity-check/LATENT-DEPARTURES.md sections 10 and 11; orchestrator ruling
2026-11-25T23:02Z item 3).

The frozen translation (f8309cf469, encodings 8afa5584a1) answered correctly on its question set, but two rules said more
than the source:
* U88 ("Rollover Details for Medical and Limited Purpose FSA" / "Contribution and Rollover Limits: - 2026: $3,400 max
  contribution, $680 max rollover"): the $3,400 test of an election (elok) fired for every FSA account, a Dependent Care
  FSA included (a $5,000 Dependent Care election: a definite "over the maximum"). Fixed: elok only for an account stated
  to be a Medical or Limited Purpose FSA; Dependent Care, or a type not stated, stays OPEN.
* U90 ("Minimum $5 required for rollover"; the $680 cap is stated for 2026 only): the rule "ro = the amount left" (over
  $5, at most $680) had no 2026 condition, so a 2027 plan year with $600 left rolled over $600. Fixed: that rule needs a
  2026 plan year (another year, or a year not stated: OPEN).
The planted errors M27 (the frozen _u88) and M28 (the frozen _u90) restore the old rules; the tests below see each one.
Each answer is derived by the use case's own staged prover (run.run_sub, no Lean here); run.py and smoke_test.py replay
the certificates in Lean. The rollover tests state a Medical FSA: rollover for a Dependent Care FSA is a known departure
not fixed here (row statute-latent-gitlab-us-benefits-dcroll), and these tests must not pin it.
"""
from pathlib import Path

import pytest

from tests.usecase_scope import usecase_scope

UC = Path(__file__).resolve().parents[1] / "usecases" / "gitlab_us_benefits"


@pytest.fixture(scope="module")
def uc():
    with usecase_scope(UC):
        import encode as E
        import run as R
        import translation as T
        yield E, R, T


def fsa(uc, kind=None, year26=True, el=None, left=None):
    """One FSA account f: kind 'dc' (Dependent Care), 'mf' (Medical), 'lpf' (Limited Purpose) or None (not stated)."""
    E, _, _ = uc
    s = E.Sub().item("f", "fsa")
    if year26 is not None:
        s.fact("y26", "f", year26)
    if kind is not None:
        s.fact(kind, "f")
    if el is not None:
        s.val("el", "f", el)
    if left is not None:
        s.val("left", "f", left)
    return s


def ask(uc, spec, form, mutant=None):
    _, R, _ = uc
    a = R.run_sub({"spec": spec, "questions": [{"qid": "q", "form": form}]}, mutant)[0]["q"]
    return a.get("value", a["answer"])


ELOK = ("yn", "elok", "f")
RO = ("amt", "ro", "f")


# --- U88: the $3,400 cap is a Medical / Limited Purpose FSA limit --------------------------------------------------------

def test_u88_dependent_care_election_5000_in_2026_does_not_derive_elok_false(uc):
    assert ask(uc, fsa(uc, "dc", el="5000.00"), ELOK) == "OPEN"


def test_u88_dependent_care_election_3000_in_2026_does_not_derive_elok_true(uc):
    assert ask(uc, fsa(uc, "dc", el="3000.00"), ELOK) == "OPEN"


def test_u88_account_type_not_stated_stays_open(uc):
    assert ask(uc, fsa(uc, None, el="5000.00"), ELOK) == "OPEN"


@pytest.mark.parametrize("kind", ["mf", "lpf"])
def test_u88_health_fsa_election_tested_against_3400(uc, kind):
    assert ask(uc, fsa(uc, kind, el="3400.00"), ELOK) == "yes"
    assert ask(uc, fsa(uc, kind, el="3400.01"), ELOK) == "no"


def test_u88_health_fsa_election_other_year_stays_open(uc):
    assert ask(uc, fsa(uc, "mf", year26=False, el="5000.00"), ELOK) == "OPEN"


def test_u88_planted_error_m27_restores_the_frozen_rule(uc):
    assert ask(uc, fsa(uc, "dc", el="5000.00"), ELOK, mutant="M27") == "no"


# --- U90: the whole amount left rolls over (up to $680) only in a 2026 plan year -----------------------------------------

def test_u90_plan_year_2027_with_600_left_answers_open(uc):
    assert ask(uc, fsa(uc, "mf", year26=False, left="600.00"), RO) == "OPEN"


def test_u90_plan_year_not_stated_with_600_left_answers_open(uc):
    assert ask(uc, fsa(uc, "mf", year26=None, left="600.00"), RO) == "OPEN"


def test_u90_plan_year_2026_with_600_left_rolls_over_600(uc):
    assert ask(uc, fsa(uc, "mf", left="600.00"), RO) == "600.00"


def test_u90_under_5_forfeited_in_any_year_unchanged(uc):
    """The $5 minimum ('Important Notes') is not stated for 2026 only: left under $5 -> $0 rolled over, every year."""
    assert ask(uc, fsa(uc, "mf", year26=False, left="4.00"), RO) == "0.00"


def test_u90_planted_error_m28_restores_the_frozen_rule(uc):
    assert ask(uc, fsa(uc, "mf", year26=False, left="600.00"), RO, mutant="M28") == "600.00"


def test_mutants_m27_m28_are_listed(uc):
    _, _, T = uc
    assert {"M27", "M28"} <= set(T.MUTANTS)
