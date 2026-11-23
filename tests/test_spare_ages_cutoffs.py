"""spare-ages-cutoffs: bridges B2 and B3 read from the guide's birth-date cut-offs (W1-W7).

Before this change the pensionable-age date and the 80th birthday came from two tables worked out by hand
for 10 birth dates, and any other birth date stopped the run (KeyError). Now `translation.guide_cutoffs`
reads the two cut-offs from the guide's own sentences (S2:5 to S2:72, 19 source-coverage units) and
`age_facts` compares a birth date with them. These tests check that:
- the reader reads every one of the 19 sentences and refuses a sentence it does not read whole;
- the cut-offs agree with Pensions Act 1995 Sch. 4 (reference.py) for every birth date it can work out;
- planted errors (a cut-off moved by a day in one line, or in every line, another wording, a changed lead-in)
  are refused or caught;
- the boundary births of cases C01, C02, C04 and C05 fall on the right side, and a birth date that was in
  no table gets its answers (through Lean when the service is built).
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1] / "usecases" / "eligibility"
sys.path.insert(0, str(HERE))

import reference  # noqa: E402
import translation as T  # noqa: E402

GUIDE = (HERE / "source" / "wfp-print.txt").read_text(encoding="utf-8").split("\n")
SCH4_FIRST, SCH4_LAST = date(1935, 1, 1), date(1977, 4, 5)  # reference.py works out births up to 5 Apr 1977


def lines_with(number, old, new):
    lines = list(GUIDE)
    assert old in lines[number - 1], (number, old)
    lines[number - 1] = lines[number - 1].replace(old, new)
    return lines


def disagreements(pa_cutoff, age80_cutoff):
    """Birth dates (from 1935 to 5 Apr 1977) where the cut-offs and Sch. 4 (reference.py) differ, and the count
    checked. Table 2 births (6 Dec 1953 to 5 Oct 1954) are skipped by reference.py; they reach pensionable age by
    6 Sep 2020 (Sch4:143-144), so `test_table_2_births` checks them by the table's last day."""
    bad, checked, born = [], 0, SCH4_FIRST
    while born <= SCH4_LAST:
        person = {"birth": born}
        try:
            reached_pa = reference.reached_pensionable_age(person)
        except NotImplementedError:
            reached_pa = None
        if reached_pa is not None:
            checked += 1
            if reached_pa != (born <= pa_cutoff):
                bad.append(("pa", born))
        if reference.reached_80(person) != (born < age80_cutoff):
            bad.append(("80", born))
        born += timedelta(days=1)
    return bad, checked


def test_cutoffs_are_read_from_the_guide():
    assert T.guide_cutoffs() == (date(1960, 6, 27), date(1946, 9, 28))
    assert len(T.GUIDE_CUTOFF_LINES) == 19 and len(set(T.GUIDE_CUTOFF_LINES.values())) == 19


def test_cutoffs_agree_with_schedule_4():
    bad, checked = disagreements(*T.guide_cutoffs())
    assert bad == []
    assert checked > 15000  # every day from 1935 to 5 Apr 1977 but table 2


def test_table_2_births():
    """reference.py stops on table 2; every table 2 day is at the latest 6 Sep 2020, before the week."""
    pa_cutoff, _ = T.guide_cutoffs()
    assert date(1954, 10, 5) <= pa_cutoff and date(2020, 9, 6) <= date.fromisoformat(T.QW1)


@pytest.mark.parametrize("number,old,new", [
    (23, "27 June 1960", "28 June 1960"),  # one pensionable-age cut-off moved by a day
    (5, "27 June 1960", "26 June 1960"),
    (48, "before 28 September 1946", "before 27 September 1946"),  # one age-80 cut-off moved by a day
    (62, "28 September 1946 and 27 June 1960", "28 September 1946 and 28 June 1960"),
    (47, "born between 28 September 1946 and", "born after 28 September 1946 and"),  # a wording not read
    (59, "were both born before", "were both born on or after"),
    (46, "You’ll get either:", "You’ll get one of:"),  # a changed lead-in
    (71, "£100 if you were born", "You get £100 if you were born"),  # not an amount row
])
def test_planted_guide_errors_are_refused(number, old, new):
    with pytest.raises(ValueError):
        T.guide_cutoffs(lines_with(number, old, new))


@pytest.mark.parametrize("old,new", [("27 June 1960", "28 June 1960"), ("27 June 1960", "26 June 1960"),
                                     ("28 September 1946", "29 September 1946"),
                                     ("28 September 1946", "27 September 1946")])
def test_a_cutoff_moved_in_every_line_is_caught_by_schedule_4(old, new):
    lines = [line.replace(old, new) for line in GUIDE]
    moved = T.guide_cutoffs(lines)  # the reader reads it: the lines agree with each other
    assert moved != T.guide_cutoffs()
    bad, _ = disagreements(*moved)
    assert len(bad) == 1  # exactly the boundary birth is on the wrong side


def bound(facts, fid):
    """"date_no_later" when the facts put the day no later than the week's last day, else "date_after"."""
    end = date.fromisoformat(T.QW1)
    sides = set()
    for f in facts:
        op, const, (_, iso) = f["formula"]
        if const != T.num("applicant", fid.split(".")[1]):
            continue
        d = date.fromisoformat(iso)
        if op in ("date_on", "date_no_later") and d <= end:
            sides.add("date_no_later")
        if op in ("date_on", "date_after") and d >= end and not (op == "date_on" and d == end):
            sides.add("date_after")
    assert len(sides) == 1, (fid, facts)
    return sides.pop()


@pytest.mark.parametrize("case,birth,pa,age80", [
    ("C01", "1960-06-27", "date_no_later", "date_after"), ("C02", "1960-06-28", "date_after", "date_after"),
    ("C04", "1946-09-27", "date_no_later", "date_no_later"), ("C05", "1946-09-28", "date_no_later", "date_after"),
    (None, "1960-02-29", "date_no_later", "date_after"), (None, "1953-12-06", "date_no_later", "date_after"),
])
def test_boundary_births(case, birth, pa, age80):
    if case:
        (profile,) = [c for c in T.load_cases()["cases"] if c["id"] == case]
        assert profile["applicant"]["birth"] == birth
    facts = T.age_facts("applicant", birth)
    assert bound(facts, "applicant.pa_date") == pa and bound(facts, "applicant.eightieth") == age80


def _ask(birth):
    import explain as X
    from lean_routes import SERVICE
    data = X.explanation({"applicant": {"birth": birth, "ew_from": "1990-01-01"}}, lean=SERVICE.exists())
    return {e["question"]: e["answer"] for e in data["answers"]}


@pytest.mark.parametrize("birth,entitled,amount", [
    ("1958-04-17", "YES", "200.00"), ("1960-07-01", "NO", None), ("1945-03-03", "YES", "300.00"),
])
def test_a_birth_date_in_no_old_table_is_answered(birth, entitled, amount):
    """On main these births stopped the run with KeyError (the hand tables had 10 birth dates)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    answers = _ask(birth)
    assert answers["Q1"] == entitled
    if amount:
        assert answers["Q2"] == amount
