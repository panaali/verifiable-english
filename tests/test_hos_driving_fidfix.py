"""Hours of service (usecases/hos_driving/translation.py): the fidelity sweep's two fix rows, one named test each (rows
statute-latent-hos-driving-I16 and -I19; manage-agents reviews/spare/statute-corpus/fidelity-check/sweep/hos-driving.md
flags FL01 and FL02).

Each row test is the check seat's test, answered by the text's own runner (run.py run_case: the encoder's pieces and
facts, the staged prover; the question-set run also replays every certificate in Lean). Each FAILS on the frozen commit
ebeefed90f and on after-release merged into it (the frozen answer is in the test's docstring) and passes on the fix.
Each fix has a planted error restoring the frozen rule (translation.MUTANTS M11, M12); the mutant tests show that the
row test's answer goes back to the frozen one under it. The guards pin answers the fix must keep. The fidelity step on
the fix (manage-agents .../sweep/hos-driving/fix/step/FIDELITY.md) flagged two more cases of unit 16, fixed with
M13 (Q3's guard, unit 8) and M14: a ride that ends the log, and a ride both after and before 7 hours in the sleeper
berth.

The test logs use activity words of their own; each is given its facts here, as the encoder gives an activity its facts
(cases.ACTIVITY, closed world encode.py C1), and removed again after the test.
"""
import datetime as dt
from pathlib import Path

import pytest

from tests.usecase_scope import usecase_scope

UC = Path(__file__).resolve().parents[1] / "usecases" / "hos_driving"

SLEEP = "resting in the sleeper berth while her co-driver Omar drives the truck"
RIDE = "riding in the passenger seat of the truck while Omar drives it on the highway"
LOAD = "loading the truck at a shipper's dock"
DRIVE = "driving the truck"
HOME = "at home"
PRE_EMPLOYMENT = "giving a urine sample for a pre-employment test directed by the carrier"
PRE_EMPLOYMENT_PAPERS = "giving a urine sample for a pre-employment test and filling in its forms for the carrier"


@pytest.fixture(scope="module")
def uc():
    with usecase_scope(UC):
        import cases as K
        import encode as E
        import run as R
        import translation as T
        added = {}
        # FL02: a sample for a pre-employment test. On the frozen translation FACTS['testing'] reads "testing required
        # by part 382 when directed by a motor carrier", which a pre-employment test is (the encoder states testing);
        # on the fix that fact names the four kinds, and the sample is the fact sample_other.
        other = ["sample_other"] if "sample_other" in T.FACTS else ["testing"]
        added[PRE_EMPLOYMENT] = other
        added[PRE_EMPLOYMENT_PAPERS] = other + ["carrier_work"]   # limb (8) separately stated
        for kk, v in added.items():
            assert kk not in E.ACTIVITY
            E.ACTIVITY[kk] = v
        try:
            yield K, E, R, T
        finally:
            for kk in added:
                E.ACTIVITY.pop(kk, None)


def case(entries, questions, every_day=False, start="2026-06-01T00:00"):
    """entries: [(hours, activity)] from `start` in order; questions: [(form, n)] asked at the log's last clock time."""
    t = dt.datetime.fromisoformat(start)
    log = []
    for hours, act in entries:
        u = t + dt.timedelta(hours=hours)
        log.append({"start": t.strftime("%Y-%m-%dT%H:%M"), "end": u.strftime("%Y-%m-%dT%H:%M"),
                    "stated": (hours // 24, hours % 24, 0), "activity": act})
        t = u
    end = t.strftime("%Y-%m-%dT%H:%M")
    return {"id": "TEST", "every_day": every_day, "designated": "00:00", "log": log,
            "questions": [{"qid": f"q{i}", "form": f, "n": n, "moment": end} for i, (f, n) in enumerate(questions)]}


def answers(uc, c, mutant=None):
    R = uc[2]
    got, _, staged, _, _, _, meta = R.run_case(c, mutant)
    return {q: a["answer"] for q, a in got.items()}, staged, meta


def excluded(uc, c, mutant=None):
    """The runner's truth of excl for the ride's first piece (True / False / None = unknown)."""
    T = uc[3]
    _, staged, meta = answers(uc, c, mutant)
    ctx = meta["ctx"]
    (a, _), = ctx.ride.values()
    return staged.truth(T.U("excl", a))


# --- I16 (FL01): 395.2 on-duty (4)(iii) "Up to 3 hours riding in the passenger seat ... immediately before or after a
# period of at least 7 consecutive hours in the sleeper berth"; the time before the log is unknown (encode.py C2) -----

def fl01_case():
    """The check seat's test: 00:00-05:00 sleeper berth (5 h), 05:00-08:00 passenger seat (3 h), then loading and
    driving 57 h in all; carrier not operating every day, designated start 00:00; Q3 (60 h / 7 days) at the end."""
    return case([(5, SLEEP), (3, RIDE), (30, LOAD), (27, DRIVE)], [("q3", 7)])


def test_i16_sleeper_run_at_log_start_under_7h_ride_not_decided(uc):
    """FL01. Frozen: 'yes' (the ride counts on duty: sbf = 5 h decides aft false, 60 h). Source: open (if the berth rest
    began 2 h or more before 00:00 the ride is excluded and the total is 57 h): no definite answer."""
    got, _, _ = answers(uc, fl01_case())
    assert got["q0"] in ("OPEN", "REFUSED"), got


def test_i16_ride_first_piece_not_decided(uc):
    """FL01, second part: a ride that is the log's first piece. Frozen: 'yes' (aft = FALSE when there is no previous
    piece). Source: the time before the log is unknown; it may be at least 7 h in the sleeper berth: no answer."""
    got, _, _ = answers(uc, case([(3, RIDE), (30, LOAD), (27, DRIVE)], [("q3", 7)]))
    assert got["q0"] in ("OPEN", "REFUSED"), got


def test_i16_guard_sleeper_run_at_log_start_7h_or_more_excludes_ride(uc):
    """A logged sleeper part of at least 7 h at the log's start: the ride after it is excluded (frozen and fix)."""
    c = case([(8, SLEEP), (3, RIDE), (30, LOAD), (27, DRIVE)], [("q3", 7)])
    assert excluded(uc, c) is True


def test_i16_guard_sleeper_run_after_home_under_7h_ride_counts(uc):
    """A sleeper run that begins inside the log (after time at home) and is under 7 h: the ride is not excluded and
    the 60 hours are reached (frozen and fix: 'yes')."""
    c = case([(12, HOME), (5, SLEEP), (3, RIDE), (30, LOAD), (27, DRIVE)], [("q3", 7)])
    assert excluded(uc, c) is False
    assert answers(uc, c)[0]["q0"] == "yes"


def test_m11_frozen_ride_rule_killed(uc):
    """M11 restores the frozen sleeper chain and aft rule: the row test's answer goes back to 'yes'."""
    assert answers(uc, fl01_case(), "M11")[0]["q0"] == "yes"


# --- units 16 and 8, the fidelity step on the fix (fix/step/FIDELITY.md FL01, FL02): the time after the log is unknown
# for Q3 (a ride that ends the log may be followed by 7 hours in the sleeper berth), and a ride both after and before 7
# hours in the sleeper berth is not decided (the unit's own note) ---------------------------------------------------------

def end_ride_case(questions=(("q3", 7),)):
    """12 h at home, 57 h loading and driving, then a 3 h passenger-seat ride that ends the log; asked at the end."""
    return case([(12, HOME), (30, LOAD), (27, DRIVE), (3, RIDE)], list(questions))


def both_sides_case():
    """12 h at home, 10 h driving, 8 h sleeper berth, 3 h ride, 8 h sleeper berth, 1 h driving; Q1 at the end."""
    return case([(12, HOME), (10, DRIVE), (8, SLEEP), (3, RIDE), (8, SLEEP), (1, DRIVE)], [("q1", None)])


def test_i16_ride_last_piece_not_decided(uc):
    """Frozen: Q3 'yes' (the ride ends the log and counts on duty: 60 h). Source: if at least 7 h in the sleeper berth
    follow, the ride is excluded (57 h): no answer."""
    got, _, _ = answers(uc, end_ride_case())
    assert got["q0"] in ("OPEN", "REFUSED"), got


def test_i16_ride_after_and_before_7h_not_decided(uc):
    """Frozen: 'no' (aft and bef both true make excl false for both pieces: the ride is on duty, so it ends the off-duty
    run and the 11 hours of driving (10 h + 1 h) are in one period). Source: up to 3 hours of the ride are excluded; the
    off-duty run 8 h + up to 3 h + 8 h then reaches 10 hours where sleeper-berth time counts as off duty (reading B) and
    not otherwise (reading A); the unit's note leaves this case not decided: no answer."""
    got, _, _ = answers(uc, both_sides_case())
    assert got["q0"] in ("OPEN", "REFUSED"), got


def test_i16_ride_after_sleeper_ends_log_q3_yes_refused(uc):
    """Audit MEDIUM (fix-review.md): 60 h on duty, 8 h in the sleeper berth, then a 2 h ride that ends the log. Frozen:
    Q3 'yes' (the ride's second piece, 0 h long, counts on duty, so the moment is not in an off-duty run). Source: the
    whole ride is excluded and the moment is in an off-duty run the time after the log may extend to 34 hours: no
    answer."""
    got, _, _ = answers(uc, case([(12, HOME), (30, LOAD), (30, DRIVE), (8, SLEEP), (2, RIDE)], [("q3", 7)]))
    assert got["q0"] in ("OPEN", "REFUSED"), got


def test_i16_guard_ride_last_piece_q2_answered(uc):
    """Q2 asks about driving from the moment on; a ride followed by driving is not immediately before a sleeper-berth
    period, so the ride's pieces keep their lengths and Q2 is answered: 12 h since 10 h off duty, so 2 h (120 min) left
    (frozen and fix; with 'before' left open the ride's lengths, and so Q2, would have no answer)."""
    R = uc[2]
    got = R.run_case(case([(12, HOME), (5, DRIVE), (4, LOAD), (3, RIDE)], [("q2", None)]))[0]
    assert (got["q0"]["answer"], got["q0"].get("minutes")) == ("DURATION", 120), got


def test_i19_every_sample_in_the_sets_is_stated_random_part382_directed(uc):
    """Audit HIGH (fix-review.md): the encoder gives a sample activity the fact testing only from its case's facts. Every
    case of both question sets that names a sample or a collection site states a random test required by part 382 that
    the carrier directed (same-family H010, H032; Codex-written H024)."""
    import json
    for f in (UC / "questions-enc.jsonl", UC / "xfam" / "questions-enc.jsonl"):
        for line in f.read_text().splitlines():
            d = json.loads(line)
            t = d["facts"]
            if any(w in t for w in ("urine", "breath", "collection site")):
                assert all(w in t for w in ("random", "part 382", "directed")), d["id"]


def test_m13_frozen_end_of_log_ride_killed(uc):
    assert answers(uc, end_ride_case(), "M13")[0]["q0"] == "yes"


def test_m14_frozen_both_sides_ride_killed(uc):
    assert answers(uc, both_sides_case(), "M14")[0]["q0"] == "no"


def test_m10_still_drops_the_exclusion(uc):
    """The exclusion's rules are implications now; M10 (exclusion dropped) still makes a ride after 8 h in the sleeper
    berth on duty."""
    c = case([(12, HOME), (8, SLEEP), (3, RIDE), (30, LOAD), (27, DRIVE)], [("q3", 7)])
    assert excluded(uc, c) is True
    assert excluded(uc, c, "M10") is False


# --- I19 (FL02): 395.2 on-duty (7) "to comply with the random, reasonable suspicion, post-crash, or follow-up testing
# required by part 382 of this subchapter when directed by a motor carrier" --------------------------------------------

def fl02_entries(sample=PRE_EMPLOYMENT):
    """Five days of 11 h loading after 12-13 h at home (55 h), 13 h at home, a 1 h sample, then 4 h driving: 59 h on
    duty plus the sample's hour in the 7-day window; carrier not operating every day."""
    out = [(12, HOME)]
    for _ in range(4):
        out += [(11, LOAD), (13, HOME)]
    out += [(11, LOAD), (13, HOME), (1, sample), (4, DRIVE)]
    return out


def test_i19_pre_employment_sample_not_limb7(uc):
    """FL02 (the check seat's test). Frozen: Q3 'yes', Q1 'no' (the sample is on duty by limb (7), 60 h). Source: limb
    (7) reaches only random, reasonable-suspicion, post-crash or follow-up tests; the head and limb (8) are not stated,
    so no definite answer on these facts."""
    got, _, _ = answers(uc, case(fl02_entries(), [("q3", 7), ("q1", None)]))
    assert got["q0"] in ("OPEN", "REFUSED"), got
    assert got["q1"] in ("OPEN", "REFUSED"), got


def test_i19_guard_pre_employment_sample_with_limb8_counts(uc):
    """The same log with limb (8) stated for the sample's hour (forms for the carrier): on duty, 60 h, 'yes' (frozen
    and fix)."""
    got, _, _ = answers(uc, case(fl02_entries(PRE_EMPLOYMENT_PAPERS), [("q3", 7)]))
    assert got["q0"] == "yes", got


def test_i19_guard_random_test_sample_counts(uc):
    """The set's 'giving a urine sample' (the encoder's reading testing, from H010's and H032's facts: a random test
    required by part 382 that the carrier directed): limb (7), on duty, 60 h, 'yes' (frozen and fix)."""
    got, _, _ = answers(uc, case(fl02_entries("giving a urine sample"), [("q3", 7)]))
    assert got["q0"] == "yes", got


def test_i19_testing_fact_names_the_four_kinds(uc):
    T = uc[3]
    w = T.FACTS["testing"]
    assert all(s in w for s in ("random", "reasonable suspicion", "post-crash", "follow-up")), w


def test_m12_frozen_limb7_killed(uc):
    """M12 restores the frozen limb (7) (any sample counts): the row test's answer goes back to 'yes'."""
    got, _, _ = answers(uc, case(fl02_entries(), [("q3", 7), ("q1", None)]), "M12")
    assert (got["q0"], got["q1"]) == ("yes", "no"), got


def test_mutants_listed(uc):
    T = uc[3]
    assert {"M11", "M12", "M13", "M14"} <= set(T.MUTANTS)
