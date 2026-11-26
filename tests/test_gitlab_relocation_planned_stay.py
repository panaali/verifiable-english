"""GitLab relocation (usecases/gitlab_relocation): a planned stay's length is never stated, so a place with a planned stay
never gets a definite "not long-term" (row statute-latent-tour-gitlab-relocation-U15; fidelity check of the tour texts,
manage-agents reviews/spare/statute-corpus/fidelity-check/sweep/tour-gitlab-relocation.md FL02).

Unit 15: "If you plan on staying in a location for more than 6 months in a single calendar year ... that becomes your
residence and you must complete the long-term relocation process." The frozen R7 / R8 / R9 counted a place's days over its
stated stays only (_days: pd = the sum of the stay children), so a place whose only child is a planned stay had pd = 0 and
got ltr / mustltr NO, st YES and comp NO whatever the planned length. The vocabulary states only a planned stay's first day
(ps). The fix (translation R18): a place with a planned stay gets no R7 NO, no R8 short-term YES and no R9 NO (refused);
the YES side (stated stays' days, or a change of permanent location) is unchanged.

Each answer is derived by the use case's own runner (run.run_sub: the staged prover, every certificate replayed in Lean).
On the frozen commit (after-release a5dde317c4, the tour's pin) and on after-release 6ab1713fa8 the four behaviour tests
test_planned_only_place_*, and test_plan_beside_short_stays_not_no, fail by BEHAVIOUR (definite no / yes); the M18-M20
tests fail there because the planted errors do not exist yet (regression tests of the new rule).
"""
from pathlib import Path

import pytest

from tests.usecase_scope import usecase_scope

UC = Path(__file__).resolve().parents[1] / "usecases" / "gitlab_relocation"

FORMS = {"mustltr": ("yn", "mustltr", "es"), "ltr": ("yn", "ltr", "es"), "st": ("yn", "st", "es"),
         "comp": ("yn", "comp", "es")}


@pytest.fixture(scope="module")
def uc():
    with usecase_scope(UC):
        import encode as E
        import run as R
        import translation as T
        yield E, R, T


def spain(uc, plan=True, stays=(), chg=False, mail=False, year="2027"):
    """The team member, the year, Spain (not named by the text, not on any list) with the stated chg / mail facts, the
    stated stays there and (plan=True) a planned stay from 1 January of the year (its length not stated)."""
    E, _, _ = uc
    s = E.Sub().year(year)
    s.item("es", "place").fact("chg", "es", chg).fact("mail", "es", mail)
    if plan:
        s.item("x", "plan", "es").val("ps", "x", f"{year}-01-01")
    for i, (a, b) in enumerate(stays):
        s.stay(f"s{i + 1}", "es", a, b)
    return s


def ask(uc, spec, mutant=None):
    _, R, _ = uc
    sub = {"spec": spec, "questions": [{"qid": k, "form": f} for k, f in FORMS.items()]}
    return {k: v["answer"] for k, v in R.run_sub(sub, mutant)[0].items()}


def test_planned_only_place_long_term_process_not_no(uc):
    """The row's named test: Spain whose only child is a plan from 1 January 2027 (not changing permanent location, no
    mail there), 'Must the team member complete the long-term relocation process?': not NO (refused)."""
    got = ask(uc, spain(uc))
    assert got["mustltr"] == "OPEN"
    assert got["ltr"] == "OPEN"


def test_planned_only_place_short_term_refused(uc):
    assert ask(uc, spain(uc))["st"] == "OPEN"


def test_planned_only_place_compensation_refused(uc):
    assert ask(uc, spain(uc))["comp"] == "OPEN"


def test_plan_beside_short_stays_not_no(uc):
    """A planned stay can add days to 32 stated days: no definite NO / short-term either."""
    got = ask(uc, spain(uc, stays=[("2027-01-01", "2027-02-01")]))
    assert got == {"mustltr": "OPEN", "ltr": "OPEN", "st": "OPEN", "comp": "OPEN"}


def test_change_of_permanent_location_with_plan_still_yes(uc):
    """Guard: the YES side is unchanged (R7: a change of permanent location to the place)."""
    got = ask(uc, spain(uc, chg=True))
    assert got["mustltr"] == "yes" and got["ltr"] == "yes" and got["st"] == "no"
    assert got["comp"] == "OPEN"        # more than 183 days not shown; chg blocks the NO


def test_stated_stays_over_six_months_with_plan_still_yes(uc):
    """Guard: 200 stated days in Spain answer YES whatever the plan adds."""
    got = ask(uc, spain(uc, stays=[("2027-01-01", "2027-07-19")]))
    assert got == {"mustltr": "yes", "ltr": "yes", "st": "no", "comp": "yes"}


def test_place_without_plan_unchanged(uc):
    """Guard: a place with stated stays only keeps the frozen answers (32 days: no, short-term, no change)."""
    got = ask(uc, spain(uc, plan=False, stays=[("2027-01-01", "2027-02-01")]))
    assert got == {"mustltr": "no", "ltr": "no", "st": "yes", "comp": "no"}


def test_m18_frozen_long_term_rule_killed(uc):
    """M18 (the frozen R7) answers the named test NO again."""
    _, _, T = uc
    assert "M18" in T.MUTANTS
    got = ask(uc, spain(uc), "M18")
    assert got["mustltr"] == "no" and got["ltr"] == "no"


def test_m19_frozen_short_term_rule_killed(uc):
    _, _, T = uc
    assert "M19" in T.MUTANTS
    assert ask(uc, spain(uc), "M19")["st"] == "yes"


def test_m20_frozen_compensation_rule_killed(uc):
    _, _, T = uc
    assert "M20" in T.MUTANTS
    assert ask(uc, spain(uc), "M20")["comp"] == "no"
