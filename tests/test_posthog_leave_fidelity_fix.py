"""PostHog "Time off" (usecases/posthog_leave): three latent departures found by the fidelity sweep, fixed in the rules
(rows statute-latent-posthog-leave-U1, -U27, -U29; manage-agents reviews/spare/statute-corpus/fidelity-check/sweep/
posthog-leave.md FL01, FL04, FL05, FL06). Each row test is the check seat's own test, run with the text's own runner
(usecases/posthog_leave/run.py run_case: the staged prover over usecases/posthog_leave/translation.py and encode.py; the
question-set run replays every certificate in Lean).

* U1 FL01 ("at least 25 days off a year"): an absence was counted whole in every year it is marked in, never split at
  31 Dec / 1 Jan. A spanning absence now counts its stated days in the year (dy); spanning unstated -> no answer.
* U27 FL04 ("you will be paid" up to "the upper limit for paid sick leave"): an absence crossing the limit partway was
  wholly "not paid". Not paid now needs every day over the limit; partway -> no answer on pay.
* U27 FL05 ("will be specified in your contract"): the limit was counted per calendar year. That count is used only when
  the contract is stated to count per calendar year (limcal) or no earlier day off sick lies in another calendar year.
* U29 FL06 ("extended periods of illness (5+ work days)", unit 28 "book the day or two off ... then add more"): measured
  on each booking. Now on the period of illness (bookings stated sameill); a link not stated -> no answer on "not
  extended".

Each row test fails on the frozen rules (253abb2d55) and on the merge with after-release (a7e613cf88; after-release has no
usecases/posthog_leave, so the merge leaves it unchanged). On the frozen code the vocabulary the fix adds (span, within,
periods, limcal, dy) does not exist; run() drops what the vocabulary in use lacks, so a frozen run fails by behaviour, not
by a missing name. M19-M21 restore the frozen rules and are killed here. The guard tests pass on both.

Set POSTHOG_FIDFIX_UC to run these tests against another copy of usecases/posthog_leave (the frozen one).
"""
import os
from pathlib import Path

import pytest

from tests.usecase_scope import usecase_scope

UC = Path(os.environ.get("POSTHOG_FIDFIX_UC") or Path(__file__).resolve().parents[1] / "usecases" / "posthog_leave")


@pytest.fixture(scope="module")
def uc():
    with usecase_scope(UC):
        import encode as E
        import run as RUN
        import translation as T
        yield T, E, RUN


def case(cid, qs, **kw):
    c = {"id": cid, "members": ["m"], "absences": [], "years": [], "leaves": [], "blocks": [], "quarters": [],
         "facts": {}, "ints": {}, "in_year": [], "bridge": [], "judgement": []}
    c.update(kw)
    c["questions"] = [{"qid": f"{cid}-{i + 1}", "item": x, "form": f} for i, (x, f) in enumerate(qs)]
    return c


def run(uc, c, mutant=None):
    """The text's own runner on one case; facts and constants the vocabulary in use lacks are dropped (frozen code)."""
    T, E, RUN = uc
    c = dict(c)
    c["facts"] = {x: [p for p in v if p in T.FACTS] for x, v in c["facts"].items()}
    known = T.int_constants(E.ctx_of(c))
    c["ints"] = {n: v for n, v in c["ints"].items() if n in known}
    got = RUN.run_case(c, mutant)[0]
    return [got[q["qid"]]["answer"] for q in c["questions"]]


def has(uc, name):
    return name in uc[0].MUTANTS


# --- U1 FL01 ---------------------------------------------------------------------------------------------------------

def year_2026(**kw):
    """21 PTO work days inside 2026, plus a PTO absence 29 Dec 2026 - 4 Jan 2027 of 5 work days, 3 of them in 2026."""
    return case("FL01", [("y", "met")], absences=["a1", "a2"], years=["y"], facts={"a1": ["vac"], "a2": ["vac"]},
                ints={"days_a1": 21, "from_a1": "2026-03-02", "days_a2": 5, "from_a2": "2026-12-29", "dy_a2_y": 3},
                in_year=[("a1", "y"), ("a2", "y")], **kw)


def test_u1_fl01_pto_spanning_new_year_counts_its_days_in_the_year_not_met(uc):
    assert run(uc, year_2026(within=["a1"], span=["a2"])) == ["no"]  # 21 + 3 = 24 < 25


def test_u1_fl01_spanning_unstated_refused(uc):
    assert run(uc, year_2026()) == ["OPEN"]


def test_guard_u1_absences_within_the_year_counted_whole(uc):
    c = year_2026(within=["a1", "a2"])
    c["ints"] = {**c["ints"], "days_a2": 4, "from_a2": "2026-12-07"}
    del c["ints"]["dy_a2_y"]
    assert run(uc, c) == ["yes"]  # 21 + 4 = 25


def test_mutant_m19_restores_frozen_u1_killed(uc):
    if not has(uc, "M19"):
        pytest.fail("M19 (the frozen unit 1) is not planted")
    assert run(uc, year_2026(within=["a1"], span=["a2"]), "M19") == ["yes"]  # frozen: 21 + 5 = 26


# --- U27 FL04, FL05 --------------------------------------------------------------------------------------------------

def sick(cid, d1, f1, d2, f2, years, in_year, qs=(("a2", "paidsick"), ("a2", "overlimit")), member=()):
    return case(cid, list(qs), absences=["a1", "a2"], years=years,
                facts={"m": list(member), "a1": ["ill", "unexpected"], "a2": ["ill", "unexpected"]},
                ints={"limit_m": 10, "days_a1": d1, "from_a1": f1, "days_a2": d2, "from_a2": f2}, in_year=in_year)


def fl04():
    """Contract 10 paid sick days a year; 8 earlier sick days; a new 4-day sick absence the same year."""
    return sick("FL04", 8, "2027-02-01", 4, "2027-05-03", ["y"], [("a1", "y"), ("a2", "y")])


def fl05(member=()):
    """Contract 10 days a year; 8 sick days in November 2026, then 4 sick days in February 2027."""
    return sick("FL05", 8, "2026-11-09", 4, "2027-02-08", ["y1", "y2"], [("a1", "y1"), ("a2", "y2")], member=member)


def test_u27_fl04_absence_crossing_the_limit_partway_pay_refused(uc):
    assert run(uc, fl04()) == ["OPEN", "yes"]  # first 2 days paid, last 2 not: no single answer; over the limit


def test_u27_fl05_limit_period_unstated_across_new_year_refused(uc):
    assert run(uc, fl05()) == ["OPEN", "OPEN"]


def test_guard_u27_fl05_calendar_year_limit_stated_paid(uc):
    assert run(uc, fl05(member=["limcal"])) == ["yes", "no"]


def test_guard_u27_every_day_over_the_limit_not_paid(uc):
    c = sick("G27", 10, "2027-02-01", 2, "2027-05-03", ["y"], [("a1", "y"), ("a2", "y")])
    assert run(uc, c) == ["no", "yes"]


def test_mutant_m20_restores_frozen_u27_killed(uc):
    if not has(uc, "M20"):
        pytest.fail("M20 (the frozen unit 27) is not planted")
    assert run(uc, fl04(), "M20") == ["no", "yes"]
    assert run(uc, fl05(), "M20") == ["yes", "no"]


# --- U29 FL06 --------------------------------------------------------------------------------------------------------

def fl06(**kw):
    """Sick, books Mon-Tue (2 work days), then adds Wed-Fri (3 work days)."""
    return case("FL06", [("a1", "extended"), ("a2", "extended")], absences=["a1", "a2"],
                facts={"a1": ["ill", "unexpected"], "a2": ["ill", "unexpected"]},
                ints={"days_a1": 2, "from_a1": "2027-03-01", "days_a2": 3, "from_a2": "2027-03-03"}, **kw)


def test_u29_fl06_illness_booked_in_two_parts_is_extended(uc):
    assert run(uc, fl06(periods=[["a1", "a2"]])) == ["yes", "yes"]


def test_u29_fl06_link_between_sick_bookings_unstated_refused(uc):
    assert run(uc, fl06()) == ["OPEN", "OPEN"]


def test_guard_u29_separate_illnesses_not_extended(uc):
    assert run(uc, fl06(periods=[["a1"], ["a2"]])) == ["no", "no"]


def test_mutant_m21_restores_frozen_u29_killed(uc):
    if not has(uc, "M21"):
        pytest.fail("M21 (the frozen unit 29) is not planted")
    assert run(uc, fl06(periods=[["a1", "a2"]]), "M21") == ["no", "no"]
