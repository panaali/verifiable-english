"""Pensions Act 2008 ss. 1, 3, 5, 13 (usecases/pensions_ae): three latent departures found by the fidelity sweep, fixed in
the rule (rows statute-latent-pensions-auto-enrolment-U7, -U13, -U14; manage-agents fidelity-check
sweep/pensions-auto-enrolment.md FL01-FL04).

* U7 FL01 (s. 3(4) "ceased to be an active member of a qualifying scheme because of any action or omission by the
  jobholder"): the frozen _u7 let an own cessation from ANY stated scheme, qualifying or not, inside the prescribed period
  remove the s. 3(2) duty. Now only a qualifying scheme's membership counts (qual in inside, Not(qual) in outside).
* U7 FL02 (s. 3(4) "because of any action or omission by the jobholder"): the frozen _u7 decided a cessation caused by
  ceasing to work in Great Britain or to have qualifying earnings (gbqe, cause otherwise unstated) as NOT own, though R10
  holds the text leaves that open. gbqe is no longer a sufficient "not own": such a cessation inside the period leaves
  ownin undecided and the s. 3(2) answer is refused, unless the case states own or notown.
* U13 FL03 (s. 5(1A)(c) "is not an active member of a qualifying scheme because there has been a period ..."): the frozen
  _u13 cause accepted a gap-caused cessation from a scheme stated NOT qualifying. Now the cause needs qual; Not(qual) is
  a nocause disjunct.
* U14 FL04 (s. 5(1B) "has ceased to be an active member of a qualifying scheme because of something other than an action
  or omission by the jobholder"): the frozen _u14 cause accepted a non-own cessation from a scheme stated NOT qualifying.
  Now the cause needs qual; Not(qual) is a nocause disjunct.

Each row test FAILS on the frozen translation (546c266be5) by behaviour; the guards (a qualifying scheme, the frozen
answers kept) pass on both. M18 (frozen unit 7), M19 (frozen unit 13) and M20 (frozen unit 14) in
usecases/pensions_ae/translation.py restore the frozen rules and are killed here. The answers come from the use case's
staged prover (usecases/pensions_ae/run.py run_case; the question-set run replays every certificate in Lean). Bridges
(age, prescribed-period start) come from usecases/pensions_ae/bridge/pae_bridge.py, as in smoke_test.py.
"""
import sys
from pathlib import Path

import pytest

from tests.usecase_scope import usecase_scope

UC = Path(__file__).resolve().parents[1] / "usecases" / "pensions_ae"
SAL = ["conn", "da"]
DOB = "1997-01-01"  # aged 30 on every day below


@pytest.fixture(scope="module")
def uc():
    with usecase_scope(UC):
        sys.path.insert(0, str(UC / "bridge"))
        import encode as E
        import pae_bridge as PB
        import run as R
        import translation as T
        yield E, PB, R, T
    sys.modules.pop("pae_bridge", None)


def case(cid, qs, day, facts, ints, open_cause=(), dob=DOB):
    """One employment j, one day x (the stated automatic enrolment or re-enrolment date), one monthly period r with one
    salary sum s, one membership m. qs: [(item, form)]."""
    ints = {"day_x": day, **ints}
    c = {"id": cid, "emps": [{"j": "j", "days": ["x"], "periods": ["r"], "sums": ["s"], "members": ["m"],
                              "lengths": {"r": ["m", 1]}}],
         "facts": {k: list(v) for k, v in facts.items()}, "ints": ints, "payin": [["s", "r"]],
         "bridge": [{"item": "x", "kind": "age", "dob": dob, "day": day}, {"item": "x", "kind": "pst", "day": day}],
         "gb_window": {}, "unplaced": [], "open_cause": list(open_cause), "judgement": [], "questions": []}
    for i, (x, f) in enumerate(qs):
        c["questions"].append({"qid": f"{cid}-{i + 1}", "item": x, "form": f})
    return c


def answers(uc, c, mutant=None, atoms=()):
    """The asked questions' answers, then the truth of each (predicate, item) in atoms ("yes" / "no" / "OPEN")."""
    E, PB, R, T = uc
    br = {}
    for b in E.bridge_inputs(c):
        r = PB.one(b)
        br[(r["case"], r["item"], r["kind"])] = r["values"]
    real = E.bridges
    E.bridges = lambda: br
    try:
        got, _, st, *_ = R.run_case(c, mutant)
    finally:
        E.bridges = real
    out = [got[q["qid"]]["answer"] for q in c["questions"]]
    for p, x in atoms:
        v = st.truth(T.U(p, x))
        out.append("OPEN" if v is None else ("yes" if v else "no"))
    return out


def month(first, last, amount):
    return {"pf_r": first, "pt_r": last, "pm_r": 1, "amt_s": amount}


# --- U7 (s. 3(4)): form (a), automatic enrolment date 1 June 2027, s. 3 applies on it (900.00 > 833.33...) ------------

def ae_case(cid, member_facts, mints, open_cause=()):
    return case(cid, [("x", "s3"), ("j", "duty3")], "2027-06-01",
                {"j": ["pnever"], "x": ["gb", "aestated"], "s": SAL, "m": member_facts},
                {**month("2027-06-01", "2027-06-30", "900.00"), **mints}, open_cause)


def fl01(cid="FL01"):
    """Gave notice and left a stated NON-qualifying scheme on 1 March 2027 (inside the 12 months before 1 June 2027)."""
    return ae_case(cid, ["ceased", "own"], {"mf_m": "2025-01-01", "mt_m": "2027-02-28", "cday_m": "2027-03-01"})


def fl02(cid="FL02"):
    """Her only membership, of a qualifying scheme, ceased on 1 December 2026 because she stopped working in Great
    Britain (gbqe; the cause is otherwise unstated: open_cause, neither own nor notown)."""
    return ae_case(cid, ["qual", "ceased", "gbqe"],
                   {"mf_m": "2024-01-01", "mt_m": "2026-11-30", "cday_m": "2026-12-01", "gap_m": "2026-12-01"},
                   open_cause=["m"])


def test_u7_fl01_own_cessation_from_non_qualifying_scheme_keeps_duty3(uc):
    assert answers(uc, fl01()) == ["yes", "yes"]


def test_u7_fl02_gb_caused_cessation_inside_period_refused(uc):
    assert answers(uc, fl02()) == ["yes", "OPEN"]


def test_guard_u7_own_cessation_from_qualifying_scheme_no_duty3(uc):
    c = ae_case("G1", ["qual", "ceased", "own"], {"mf_m": "2025-01-01", "mt_m": "2027-02-28", "cday_m": "2027-03-01"})
    assert answers(uc, c) == ["yes", "no"]


def test_guard_u7_gb_caused_cessation_before_period_duty3(uc):
    c = ae_case("G2", ["qual", "ceased", "gbqe"],
                {"mf_m": "2024-01-01", "mt_m": "2026-02-28", "cday_m": "2026-03-01", "gap_m": "2026-03-01"},
                open_cause=["m"])
    assert answers(uc, c) == ["yes", "yes"]


def test_guard_u7_gb_caused_cessation_stated_not_own_duty3(uc):
    c = ae_case("G3", ["qual", "ceased", "gbqe", "notown"],
                {"mf_m": "2024-01-01", "mt_m": "2026-11-30", "cday_m": "2026-12-01", "gap_m": "2026-12-01"})
    assert answers(uc, c) == ["yes", "yes"]


# --- U13 / U14 (s. 5(1A), (1B)): the re-enrolment date 1 June 2027, aged 30, not over the trigger ------------------------

RE = (("s51a", "x"), ("s51b", "x"))  # answers: s5, duty5, then s. 5(1A), s. 5(1B) on the re-enrolment date


def re_case(cid, amount, member_facts, mints, j_facts=("pnever",), open_cause=()):
    return case(cid, [("x", "s5"), ("x", "duty5")], "2027-06-01",
                {"j": list(j_facts), "x": ["gb", "reday"], "s": SAL, "m": member_facts},
                {**month("2027-06-01", "2027-06-30", amount), **mints}, open_cause)


def fl03(cid="FL03"):
    """AED 1 Jan 2025 stated; 700.00 in June 2027 (qualifying earnings, not over the trigger); a scheme stated NOT
    qualifying, ceased 1 Mar 2026 because she stopped working in Great Britain from 1 Feb 2026."""
    return re_case(cid, "700.00", ["ceased", "gbqe"],
                   {"aed_j": "2025-01-01", "mf_m": "2025-01-01", "mt_m": "2026-02-28", "cday_m": "2026-03-01",
                    "gap_m": "2026-02-01"}, j_facts=("pnever", "hasaed"), open_cause=["m"])


def fl04(cid="FL04"):
    """800.00 in June 2027; a scheme stated NOT qualifying ended 1 March 2027 because the employer closed it."""
    return re_case(cid, "800.00", ["ceased", "notown"],
                   {"mf_m": "2025-01-01", "mt_m": "2027-02-28", "cday_m": "2027-03-01"})


def test_u13_fl03_gap_cessation_from_non_qualifying_scheme_no_duty5(uc):
    assert answers(uc, fl03(), atoms=RE) == ["no", "no", "no", "no"]


def test_u14_fl04_employer_closed_non_qualifying_scheme_no_duty5(uc):
    assert answers(uc, fl04(), atoms=RE) == ["no", "no", "no", "no"]


def test_guard_u13_gap_cessation_from_qualifying_scheme_duty5(uc):
    c = re_case("G4", "700.00", ["qual", "ceased", "gbqe"],
                {"aed_j": "2025-01-01", "mf_m": "2025-01-01", "mt_m": "2026-02-28", "cday_m": "2026-03-01",
                 "gap_m": "2026-02-01"}, j_facts=("pnever", "hasaed"), open_cause=["m"])
    assert answers(uc, c, atoms=RE) == ["yes", "yes", "yes", "OPEN"]


def test_guard_u14_employer_closed_qualifying_scheme_duty5(uc):
    c = re_case("G5", "800.00", ["qual", "ceased", "notown"],
                {"mf_m": "2025-01-01", "mt_m": "2027-02-28", "cday_m": "2027-03-01"})
    assert answers(uc, c, atoms=RE) == ["yes", "yes", "no", "yes"]


# --- the mutants restoring the frozen rules (translation.MUTANTS, run.py --mutants) -------------------------------------

@pytest.mark.parametrize("mutant, make, atoms, frozen", [
    ("M18", fl01, (), ["yes", "no"]),
    ("M18", fl02, (), ["yes", "yes"]),
    ("M19", fl03, RE, ["yes", "yes", "yes", "no"]),
    ("M20", fl04, RE, ["yes", "yes", "no", "yes"]),
])
def test_mutant_restoring_frozen_rule_gives_frozen_answer(uc, mutant, make, atoms, frozen):
    assert mutant in uc[3].MUTANTS
    got = answers(uc, make(), mutant, atoms)
    assert got == frozen
    assert got != answers(uc, make(), atoms=atoms)
