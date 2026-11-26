"""GitHub Sponsors 'Terms For Sponsored Developer' (usecases/github_sponsors): three latent departures of the frozen
translation 5336e71bbc that sat behind correct answers (manage-agents reviews/spare/statute-corpus/fidelity-check/
LATENT-DEPARTURES.md sections 4, 5 and 7; rows statute-latent-github-sponsors-developer-U6, -U30, -U8; orchestrator ruling
2026-11-25T23:02Z item 3).

* U6 (translation._u6, R9): unit 6's "must" conditions (age, a valid GitHub account, agreement) are necessary, not
  sufficient: entry into the Program "is contingent upon your completion of the registration process and acceptance into
  the Program by GitHub" (unit 27). A "may take part" yes now needs regd and acc; without them no answer (OPEN).
* U30 (translation._u30, R11): "You are responsible for compliance with any third-party payment service provider's
  agreements, policies, and laws or regulations that may apply" is a required item (dtpcomp), not "not required" by the
  duty closure.
* U8 (translation._ban, R10): a ban of units 9-15 fires only on an act that "allow[s] payments or raise[s] funds" (rf,
  unit 8's lead-in); an act with a listed purpose and no rf is OPEN (no closure on rf).
* Planted errors M20 / M21 / M22 restore the frozen readings and are killed here.
Each answer is derived by the use case's own staged prover (usecases/github_sponsors/run.py run_sub); the question-set
run replays every certificate in Lean. Fails on 5336e71bbc / 6ddb5b7b14 (no rf, no dtpcomp, no M20-M22; part yes
without acceptance).
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


def adult(gs, *entry):
    """A US developer aged 20 with a valid GitHub account who agreed to the terms; entry facts as given."""
    E = gs[1]
    return E.Sub().dev("ghacct", "agreed", "us", *entry).val("ag", "p", "20")


# --- U6 ---------------------------------------------------------------------------------------------------------------

def test_us_developer_aged_20_with_account_and_agreement_but_not_accepted_does_not_take_part_yes(gs):
    """The row's test: US, 20, ghacct, agreed, registered, no acceptance: unit 6 alone gave 'may take part'; now OPEN."""
    a = ask(gs, adult(gs, "regd"), ("q", ("yn", "part", "p")))
    assert val(a["q"]) != "yes"
    assert val(a["q"]) == "OPEN"


def test_accepted_but_not_registered_developer_does_not_take_part_yes(gs):
    a = ask(gs, adult(gs, "acc"), ("q", ("yn", "part", "p")))
    assert val(a["q"]) == "OPEN"


def test_registered_and_accepted_developer_meeting_unit_6_takes_part(gs):
    a = ask(gs, adult(gs, "regd", "acc"), ("q", ("yn", "part", "p")), ("g", ("yn", "gr", "p")))
    assert (val(a["q"]), val(a["g"])) == ("yes", "yes")


def test_under_age_developer_still_does_not_take_part_without_acceptance(gs):
    """The 'no' rules of unit 6 are unchanged: under 13 in the US is 'no' with or without entry."""
    E = gs[1]
    a = ask(gs, E.Sub().dev("ghacct", "agreed", "us").val("ag", "p", "12"), ("q", ("yn", "part", "p")))
    assert val(a["q"]) == "no"


def test_mutant_m20_restores_the_frozen_participation_reading(gs):
    a = ask(gs, adult(gs, "regd"), ("q", ("yn", "part", "p")), mutant="M20")
    assert val(a["q"]) == "yes"


# --- U30 --------------------------------------------------------------------------------------------------------------

def test_complying_with_the_third_party_payment_provider_agreements_policies_and_laws_is_required(gs):
    """The row's test: the duty item derives req; the closure gave 'not required' on 5336e71bbc."""
    E = gs[1]
    a = ask(gs, E.Sub().dev("us").duty("u1", "dtpcomp").duty("u2", None),
            ("q", ("yn", "req", "u1")), ("o", ("yn", "req", "u2")))
    assert (val(a["q"]), val(a["o"])) == ("yes", "no")


def test_mutant_m22_restores_the_frozen_duty_closure(gs):
    E = gs[1]
    a = ask(gs, E.Sub().dev("us").duty("u1", "dtpcomp"), ("q", ("yn", "req", "u1")), mutant="M22")
    assert val(a["q"]) == "no"


# --- U8 ---------------------------------------------------------------------------------------------------------------

def test_crypto_act_without_allowing_payments_or_raising_funds_is_not_forbidden_yes(gs):
    """The row's test: an act with crypto and no rf must not derive forb; it did on 5336e71bbc."""
    E = gs[1]
    a = ask(gs, E.Sub().dev("acc", "ind").act("a1", "crypto"), ("q", ("yn", "forb", "a1")))
    assert val(a["q"]) == "OPEN"


def test_raising_funds_for_crypto_is_forbidden(gs):
    E = gs[1]
    a = ask(gs, E.Sub().dev("acc", "ind").act("a1", "rf", "crypto").act("a2", "rf"),
            ("q", ("yn", "forb", "a1")), ("n", ("yn", "forb", "a2")))
    assert (val(a["q"]), val(a["n"])) == ("yes", "no")


def test_every_listed_purpose_needs_the_lead_in(gs):
    """Units 9-15: each purpose alone (no rf) is OPEN; with rf it is forbidden."""
    E = gs[1]
    for facts, st in ((("fraud",), {}), (("reasons",), {"misrep": True}), (("secur",), {}), (("sellpi",), {}),
                      (("pilaw",), {}), (("gamble",), {}), (("sanct",), {})):
        a = ask(gs, E.Sub().act("a1", *facts, **st).act("a2", "rf", *facts, **st),
                ("q", ("yn", "forb", "a1")), ("r", ("yn", "forb", "a2")))
        assert (val(a["q"]), val(a["r"])) == ("OPEN", "yes"), facts


def test_unit_31_advertising_agreement_ban_does_not_need_the_lead_in(gs):
    E = gs[1]
    a = ask(gs, E.Sub().act("a1", "adagr", "adproh"), ("q", ("yn", "forb", "a1")))
    assert val(a["q"]) == "yes"


def test_mutant_m21_restores_the_frozen_ban_on_the_purpose_alone(gs):
    E = gs[1]
    a = ask(gs, E.Sub().dev("acc", "ind").act("a1", "crypto"), ("q", ("yn", "forb", "a1")), mutant="M21")
    assert val(a["q"]) == "yes"


def test_set_cases_s005_to_s008_keep_their_answers_with_the_fresh_rf(gs):
    """S005-S008 (every 'May <developer> raise funds for <purpose>' question): rf entered from the fresh encoder seat
    (latent-enc/enc.jsonl); the bans still answer 'no' (may not), S005-2 stays OPEN (no IP rule), S008-2 unit 31."""
    K, R = gs[0], gs[2]
    got = {}
    for c in K.CASES:
        if c["id"] in ("S005", "S006", "S007", "S008"):
            for s in c["subs"]:
                got.update({q: val(a) for q, a in R.run_sub(s, None)[0].items()})
    want = {"S005-1": "no", "S005-2": "OPEN", "S005-3": "no", "S006-1": "no", "S006-2": "no", "S006-3": "no",
            "S007-1": "no", "S007-2": "no", "S007-3": "no", "S007-4": "no", "S008-1": "no", "S008-2": "no"}
    assert got == want
