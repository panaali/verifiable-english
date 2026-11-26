"""GitLab relocation (usecases/gitlab_relocation): unit 11's "no change to compensation" NO is for a temporary, short-term
location, so it never holds for a place the team member's mail is delivered to, or where that is not stated (row
statute-latent-tour-gitlab-relocation-U11-mail; fidelity step FL01 on the U15 fix, manage-agents
reviews/spare/statute-corpus/fidelity-check/sweep/tour-gitlab-relocation/fix-fidelity/FIDELITY.md).

Unit 11: "Any time spent in temporary locations for 183 days or less (short term relocation) will not result in any change
to compensation or employment agreements." Unit 19: "If you ... will have your mail delivered to an address in a different
address, please follow the steps below to request a long-term relocation." R7's long-term NO (and so R8's short-term YES)
already requires that the mail will not go to an address in the place; the frozen R9 gave comp NO on days and chg alone.
The fix (translation R19): comp's NO also requires Not(mail), as R7's NO does; where mail is not stated the NO is not
derivable (refused). The YES side (more than 183 days) is unchanged.

Each answer is derived by the use case's own runner (run.run_sub: the staged prover). On fidfix-tour-gitlab-relocation-1126
@ bd0a94054a (the U15 fix) and on after-release 123842735f the named test fails by BEHAVIOUR (comp: a definite no); the
M21 test fails there because the planted error does not exist yet.
"""
from pathlib import Path

import pytest

from tests.usecase_scope import usecase_scope

UC = Path(__file__).resolve().parents[1] / "usecases" / "gitlab_relocation"

FORMS = {"mustltr": ("yn", "mustltr", "es"), "ltr": ("yn", "ltr", "es"), "st": ("yn", "st", "es"),
         "comp": ("yn", "comp", "es")}
DAYS32 = [("2027-01-01", "2027-02-01")]
DAYS200 = [("2027-01-01", "2027-07-19")]


@pytest.fixture(scope="module")
def uc():
    with usecase_scope(UC):
        import encode as E
        import run as R
        import translation as T
        yield E, R, T


def spain(uc, stays=DAYS32, chg=False, mail=False, year="2027"):
    """The team member, the year, Spain (not named by the text, not on any list) with the stated chg fact, the mail fact
    (True / False stated; None: not stated) and the stated stays there; no planned stay."""
    E, _, _ = uc
    s = E.Sub().year(year)
    s.item("es", "place").fact("chg", "es", chg)
    if mail is not None:
        s.fact("mail", "es", mail)
    for i, (a, b) in enumerate(stays):
        s.stay(f"s{i + 1}", "es", a, b)
    return s


def ask(uc, spec, mutant=None):
    _, R, _ = uc
    sub = {"spec": spec, "questions": [{"qid": k, "form": f} for k, f in FORMS.items()]}
    return {k: v["answer"] for k, v in R.run_sub(sub, mutant)[0].items()}


def test_comp_of_place_with_mail_32_days_not_no(uc):
    """The row's named test: Spain with mail delivered there (mail = True), 32 stated days, no change of permanent
    location: 'Will the stay change the compensation?' is not NO (refused), as ltr / st already are."""
    got = ask(uc, spain(uc, mail=True))
    assert got["comp"] == "OPEN"
    assert got["ltr"] == "OPEN" and got["st"] == "OPEN"


def test_comp_mail_not_stated_refused(uc):
    """Where the case does not state whether the mail goes there, comp's NO is not derivable (refused), like ltr's NO."""
    got = ask(uc, spain(uc, mail=None))
    assert got["comp"] == "OPEN"
    assert got["ltr"] == "OPEN"


def test_comp_no_mail_32_days_still_no(uc):
    """Guard: mail stated not to go there, 32 days, no chg: the frozen answers stand (no change, short-term)."""
    got = ask(uc, spain(uc, mail=False))
    assert got == {"mustltr": "no", "ltr": "no", "st": "yes", "comp": "no"}


def test_comp_mail_over_183_days_still_yes(uc):
    """Guard: the YES side is unchanged: 200 stated days answer comp yes whatever the mail."""
    for mail in (True, False, None):
        got = ask(uc, spain(uc, stays=DAYS200, mail=mail))
        assert got["comp"] == "yes", mail
        assert got["ltr"] == "yes", mail


def test_m21_frozen_compensation_rule_killed(uc):
    """M21 (the frozen R9, mail not read) answers the named test NO again."""
    _, _, T = uc
    assert "M21" in T.MUTANTS
    assert ask(uc, spain(uc, mail=True), "M21")["comp"] == "no"
    assert ask(uc, spain(uc, mail=None), "M21")["comp"] == "no"
