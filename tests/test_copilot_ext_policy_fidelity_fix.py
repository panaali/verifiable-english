"""GitHub Copilot Extension Developer Policy (usecases/copilot_ext_policy): latent departures found by the fidelity sweep,
fixed in the rule (rows statute-latent-github-copilot-ext-U18, -U38; manage-agents fidelity-check sweep/github-copilot-ext.md
FL04, FL07, FL08).

* U18 FL04 (unit 18 "you must delete all associated Personal Data within thirty days"; unit 37 "This Agreement will
  terminate immediately ... if you breach any term"): the frozen rules never counted a missed thirty-day deadline as a
  breach, so the Agreement came out in force after it. Now a deletion item whose data was all deleted on a stated day
  after the last day ends the Agreement: not in force on any later day (R13), in force up to and on the last day; with
  no stated deletion (or no stated day) the breach is unknown and the Agreement after the last day is refused.
* U38 FL07 ("you will return (or, at our request, destroy) all of our Pre-release materials"): the frozen _required kept
  return required when GitHub asked for destruction. Now return is required only when GitHub did not ask.
* U38 FL08 ("Upon termination ... you will certify in writing that you've complied with these requirements"): the frozen
  _required asked for the certification only when the developer held Pre-release Materials. Now it is required on
  termination alone.

Each row test FAILS on the frozen translation (28765183ad) and on its after-release merge by behaviour; the guards pass on
both. M14 (frozen unit 37) and M15 (frozen unit 31's Pre-release duties) in usecases/copilot_ext_policy/translation.py
restore the frozen rules and are killed here. The answers come from the use case's own runner
(usecases/copilot_ext_policy/run.py run_case: the staged prover; the question-set run replays every certificate in Lean),
with cases built by usecases/copilot_ext_policy/encode.py.
"""
import sys
from pathlib import Path

import pytest

from tests.usecase_scope import usecase_scope

UC = Path(__file__).resolve().parents[1] / "usecases" / "copilot_ext_policy"


@pytest.fixture(scope="module")
def uc():
    with usecase_scope(UC):
        import run as R
        import translation as T
        yield R, T


def _case(cid, items, qs):
    return {"id": cid, "judgement": [], "subs": [{"spec": {"items": items, "links": []},
                                                  "questions": [{"qid": f"{cid}-{n}", "form": f, "item": x}
                                                                for n, (f, x) in enumerate(qs, 1)]}]}


def dele(x, facts, ev=None, dd=None):
    d = {"id": x, "kind": "del", "facts": list(facts)}
    if ev:
        d["ev"] = ev
    if dd:
        d["dd"] = dd
    return d


def qd(x, day):
    return {"id": x, "kind": "q", "qday": day}


def duty(x, facts):
    return {"id": x, "kind": "duty", "facts": list(facts), "stated": {}}


def ans(R, case, mutant=None):
    return {q: a["answer"] for q, a in R.run_case(case, mutant).items()}


# --- U18 FL04: a missed thirty-day deadline is a breach that ends the Agreement ------------------------------------

def fl04_case():
    """The check seat's test: a User deletes the Extension on 2027-01-10 (last day 2027-02-09); the developer deletes the
    associated Personal Data on 2027-03-01; no other ending act. Is the Agreement in force on 2027-03-15?"""
    return _case("F04", [dele("d", ("user_deleted_ext", "all_deleted"), ev="2027-01-10", dd="2027-03-01"),
                         qd("q", "2027-03-15")], [("inforce", "q")])


def test_u18_fl04_missed_deletion_deadline_ends_agreement(uc):
    R, _ = uc
    assert ans(R, fl04_case()) == {"F04-1": "no"}


def test_u18_fl04_day_after_last_day_not_in_force(uc):
    R, _ = uc
    c = _case("F04b", [dele("d", ("user_deleted_ext", "all_deleted"), ev="2027-01-10", dd="2027-03-01"),
                       qd("q", "2027-02-10")], [("inforce", "q")])
    assert ans(R, c) == {"F04b-1": "no"}


def test_u18_fl04_no_stated_deletion_refused_after_last_day(uc):
    """No stated deletion of all the data: all_deleted is closed (C1), so its absence does not say the data was kept; the
    breach is unknown and the Agreement on a day after the last day is refused (OPEN), not answered."""
    R, _ = uc
    c = _case("F04c", [dele("d", ("ext_removed",), ev="2027-01-10"), qd("q", "2027-03-15")], [("inforce", "q")])
    assert ans(R, c) == {"F04c-1": "OPEN"}


def test_u18_fl04_deletion_day_unstated_refused_after_last_day(uc):
    """All the data deleted, its day not stated: whether the period was missed is unknown, so the Agreement on a day after
    the last day is refused (OPEN), not answered."""
    R, _ = uc
    c = _case("F04d", [dele("d", ("discontinued_ext", "all_deleted"), ev="2027-01-10"), qd("q", "2027-03-15")],
              [("inforce", "q")])
    assert ans(R, c) == {"F04d-1": "OPEN"}


def test_guard_u18_missed_deadline_in_force_on_last_day(uc):
    R, _ = uc
    c = _case("G04a", [dele("d", ("user_deleted_ext", "all_deleted"), ev="2027-01-10", dd="2027-03-01"),
                       qd("q", "2027-02-09")], [("inforce", "q")])
    assert ans(R, c) == {"G04a-1": "yes"}


def test_guard_u18_deadline_met_stays_in_force(uc):
    R, _ = uc
    c = _case("G04b", [dele("d", ("user_deleted_ext", "all_deleted"), ev="2027-01-10", dd="2027-02-09"),
                       qd("q", "2027-03-15")], [("inforce", "q"), ("met", "d")])
    assert ans(R, c) == {"G04b-1": "yes", "G04b-2": "yes"}


def test_guard_u18_request_only_has_no_deadline_breach(uc):
    R, _ = uc
    c = _case("G04c", [dele("d", ("request_only",)), qd("q", "2027-03-15")], [("inforce", "q")])
    assert ans(R, c) == {"G04c-1": "yes"}


# --- U38 FL07 / FL08: return or (at GitHub's request) destroy; certify on termination -------------------------------

def fl07_case():
    """The check seat's test: GitHub terminates; the developer holds Pre-release Materials and GitHub asks for them to be
    destroyed. Must the developer return them?"""
    return _case("F07", [duty("ret", ("k_return_prerelease", "has_prerelease", "terminated_before", "gh_asked_destroy")),
                         duty("dest", ("k_destroy_prerelease", "has_prerelease", "terminated_before",
                                       "gh_asked_destroy"))],
                 [("must", "ret"), ("must", "dest")])


def fl08_case():
    """The check seat's test: the developer stopped using the Platform and never received Pre-release Materials. Must it
    certify in writing?"""
    return _case("F08", [duty("cert", ("k_certify", "terminated_before"))], [("must", "cert")])


def test_u38_fl07_return_not_required_when_github_asks_destruction(uc):
    R, _ = uc
    assert ans(R, fl07_case()) == {"F07-1": "no", "F07-2": "yes"}


def test_u38_fl08_certify_required_on_termination_without_prerelease(uc):
    R, _ = uc
    assert ans(R, fl08_case()) == {"F08-1": "yes"}


def test_guard_u38_return_required_when_github_did_not_ask(uc):
    R, _ = uc
    c = _case("G07", [duty("ret", ("k_return_prerelease", "has_prerelease", "terminated_before")),
                      duty("dest", ("k_destroy_prerelease", "has_prerelease", "terminated_before"))],
              [("must", "ret"), ("must", "dest")])
    assert ans(R, c) == {"G07-1": "yes", "G07-2": "no"}


def test_guard_u38_certify_with_prerelease_and_not_before_termination(uc):
    R, _ = uc
    c = _case("G08", [duty("c1", ("k_certify", "has_prerelease", "terminated_before")),
                      duty("c2", ("k_certify", "has_prerelease"))],
              [("must", "c1"), ("must", "c2")])
    assert ans(R, c) == {"G08-1": "yes", "G08-2": "no"}


# --- mutants restoring the frozen rules ---------------------------------------------------------------------------

def test_m14_frozen_unit37_killed(uc):
    R, T = uc
    assert "M14" in T.MUTANTS
    assert ans(R, fl04_case(), "M14") == {"F04-1": "yes"}


def test_m15_frozen_unit38_duties_killed(uc):
    R, T = uc
    assert "M15" in T.MUTANTS
    assert ans(R, fl07_case(), "M15") == {"F07-1": "yes", "F07-2": "yes"}
    assert ans(R, fl08_case(), "M15") == {"F08-1": "no"}
