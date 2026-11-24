"""Tests for the free in-patient treatment rules (row statute-xfam-wrong-pawhp-1): translation.fipt_rules and
encode.fipt_facts. SI 2005/3360 reg. 2(5) (read in by SSI 2024/351 reg. 2): the period begins on the DAY AFTER the day of
entry and ends on the day of leaving; reg. 9(a) needs it to cover the qualifying week (2026: 21-27 Sep) and the 52 weeks
immediately before it (22 Sep 2025 - 20 Sep 2026).

Each fact is derived by the checker's own prover from the rules and the stated dates, and every certificate is replayed
in Lean (ve.backends.relay), so a pass means the Lean kernel accepted the derivation.

Run (repository root, after `cd lean && lake build`):  uv run --frozen python -B usecases/pawhp/test_fipt.py
Also collected by pytest. Fails on 873c9ea940 (no fipt_rules, no M6, stated fipt_52w_before accepted).
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "bridge"))

import bridges as BR  # noqa: E402
import encode as E  # noqa: E402
import run as RUN  # noqa: E402
import translation as T  # noqa: E402
from ve.environment import Environment  # noqa: E402

R = T.R
RAW_ENV = T.environment()
PROVER = RUN.Prover(Environment(RAW_ENV))
QW0 = dt.date.fromisoformat(R.QW0)


def derive(stay, mutant=None):
    """(fipt_throughout_qw, fipt_52w_before, excluded_9) for a one-person case whose only fact of interest is the stay.
    Each value is True / False / None (OPEN); every certificate found is replayed in Lean."""
    people = [{"c": "applicant", "b": None, "sex": "F", "fipt": stay}]
    case = {"id": "TFIPT", "people": people}
    rules = T.rules(["applicant"], (), mutant)
    facts, _ = E.facts(case)
    st = RUN.Staged(PROVER, rules, facts)
    got = []
    for pred in ("fipt_throughout_qw", "fipt_52w_before", "excluded_9"):
        f = R.U(pred, "applicant")
        k = T.key(f)
        for t in st.order():  # earlier steps first (excluded_9 needs the custody / care / rb steps)
            if t == k:
                break
            if t.startswith("[") and t not in st.steps:
                g = json.loads(t)
                st.attempt(t, RUN.label(g), [g, ["not", g]])
        st.attempt(k, pred, [f, ["not", f]])
        got.append(st.known(f))
    cases = [{"id": f"c{i}", "kind": "certificate", "environment": RAW_ENV,
              "premises": [RUN.q(st.formula(n)) for n in s["premises"]], "conclusion": RUN.q(s["formula"]),
              "certificate": s["certificate"]} for i, s in enumerate(st.steps.values())]
    for r in RUN.lean(cases):
        assert r.get("status") == "ok" and r.get("valid") is True, r
    return tuple(got)


def day(d, n=0):
    return (dt.date.fromisoformat(d) + dt.timedelta(days=n)).isoformat()


W52 = (QW0 - dt.timedelta(days=364)).isoformat()   # 2025-09-22: first day of the 52 weeks


# --- bridge constants: the two dates the rules compare with come from the tested bridge script ------------------------
def test_constants_match_bridge():
    start, end = BR.qualifying_week(2026)
    assert (R.QW0, R.QW1) == (start.isoformat(), end.isoformat())
    assert T.QW_MINUS_52W == (start - dt.timedelta(days=364)).isoformat() == W52 == "2025-09-22"
    assert T.QW_MINUS_1D == (start - dt.timedelta(days=1)).isoformat() == "2026-09-20"


# --- (b) the boundary of the 52 weeks ------------------------------------------------------------------------------
def test_entry_52_weeks_plus_one_day_before_qualifies():
    # entry 21 Sep 2025 = 52 weeks + 1 day before the week's first day: the period begins 22 Sep 2025 -> covers all 52 weeks
    assert day(W52, -1) == "2025-09-21"
    assert derive([day(W52, -1), None]) == (True, True, True)


def test_entry_exactly_52_weeks_before_is_one_day_short():
    # entry 22 Sep 2025 (P020's day): the period begins 23 Sep 2025 -> 22 Sep 2025 is not covered -> not excluded
    assert derive([W52, None]) == (True, False, False)


def test_mutant_m6_counts_from_entry_day():
    # the planted error: counting from the day of entry makes the one-day-short stay qualify (the frozen build's P020)
    assert derive([W52, None], mutant=T.FIPT_ENTRY_DAY_MUTANT) == (True, True, True)
    assert derive([day(W52, -1), None], mutant=T.FIPT_ENTRY_DAY_MUTANT) == (True, True, True)


def test_left_on_last_day_of_week_is_throughout():
    # reg. 2(5): the period ends ON the day of leaving: leaving 27 Sep 2026 covers the whole week, 26 Sep does not
    assert derive([day(W52, -30), R.QW1]) == (True, True, True)
    assert derive([day(W52, -30), day(R.QW1, -1)]) == (False, True, False)


def test_entry_day_before_week_is_throughout_entry_on_first_day_is_not():
    assert derive([day(R.QW0, -1), None])[0] is True     # entry 20 Sep 2026: period from 21 Sep
    assert derive([R.QW0, None])[0] is False             # entry 21 Sep 2026: period from 22 Sep
    assert derive([R.QW0, None], mutant=T.FIPT_ENTRY_DAY_MUTANT)[0] is True


def test_left_before_week():
    # left 20 Sep 2026: the 52 weeks are covered, the week is not -> reg. 9(a) does not apply
    assert derive([day(W52, -1), T.QW_MINUS_1D]) == (False, True, False)
    assert derive([day(W52, -1), day(T.QW_MINUS_1D, -1)]) == (False, False, False)


def test_no_stay():
    assert derive(None) == (False, False, False)


# --- more than one stay: no linking rule is imported (out of scope, refused) ---------------------------------------
def test_two_stays_refused():
    # SSI 2024/351 reg. 2 imports only reg. 2(4) and (5) of SI 2005/3360: no rule links separate stays. A record with two
    # stays is refused (not answered), whatever the gap: a discharge and later readmission inside the 52 weeks, and a
    # same-day transfer (which reg. 2(5) itself makes continuous) alike. A list holding one stay is refused too.
    for stays in ([["2025-01-10", "2026-03-01"], ["2026-03-05", None]],      # readmitted 4 days later
                  [["2025-01-10", "2026-03-01"], ["2026-03-01", None]],      # same-day transfer
                  [["2025-01-10", "2026-03-01"]]):                           # one stay, wrongly wrapped
        try:
            derive(stays)
        except SystemExit as e:
            assert "one stay" in str(e)
        else:
            raise AssertionError(f"accepted {stays!r}")


def test_stay_entered_inside_the_52_weeks():
    # a single stay entered after the 52 weeks began (not a readmission convention: two stays are refused above)
    assert derive(["2026-03-05", None]) == (True, False, False)


def test_bad_stays_refused():
    for stay in (["2026-03-05", "2026-03-04"], ["2026-02-30", None], ["2026-13-01", None], ["2026-03-05"]):
        try:
            derive(stay)
        except SystemExit:
            pass
        else:
            raise AssertionError(f"accepted {stay!r}")


def test_stay_before_1970_is_clamped():
    assert derive(["1960-01-01", "1965-01-01"]) == (False, False, False)
    assert derive(["1960-01-01", None]) == (True, True, True)


def test_unknown_fipt_stays_open():
    case = {"id": "TFIPT", "people": [{"c": "applicant", "b": None, "unknown": ["fipt"]}]}
    facts, unknown = E.facts(case)
    assert "applicant.ever_fipt" in unknown and not any(f["id"].startswith("applicant.ever_fipt") for f in facts)
    st = RUN.Staged(PROVER, T.rules(["applicant"]), facts)
    f = R.U("fipt_52w_before", "applicant")
    st.attempt(T.key(f), "fipt_52w_before", [f, ["not", f]])
    assert st.known(f) is None


def test_other_people_get_the_rules():
    got = {r["id"] for r in T.rules(["applicant", "other1"])}
    assert {"rF.applicant.0", "rF.applicant.1", "rF.other1.0", "rF.other1.1"} <= got


# --- the stated fact of 873c9ea940 is no longer accepted ------------------------------------------------------------
def test_stated_52_week_fact_refused():
    for legacy in ("fipt_52w_before", "fipt_throughout_qw"):
        for person in ({"c": "applicant", "b": None, legacy: True}, {"c": "applicant", "b": None, "unknown": [legacy]}):
            case = {"id": "TFIPT", "people": [person]}
            try:
                E.facts(case)
            except SystemExit as e:
                assert "derived from the stay dates" in str(e)
            else:
                raise AssertionError(f"stated {legacy} was accepted: {person}")


def main():
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = 0
    for n, f in tests:
        try:
            f()
            print("PASS ", n)
        except Exception as e:  # noqa: BLE001
            failed += 1
            print("FAIL ", n, type(e).__name__, str(e)[:300])
    print(f"{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
