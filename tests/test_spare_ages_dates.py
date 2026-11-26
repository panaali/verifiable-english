"""spare-ages-dates: pensionable age, the 80th birthday and the qualifying week worked out from the source text.

usecases/eligibility/pensionable_age.py reads Pensions Act 1995 Sch. 4 para. 1 (rules (1)-(10), tables 1-4, rule (7A))
and the definition of the qualifying week (S1 reg. 1(3)); translation.age_facts and QW0/QW1 use it. These tests check:
- the schedule is read whole (every line from the rules heading to the amendment notes), and the 82 open
  source-coverage units' lines each decide the result (changed, the reader refuses or reads differently);
- the births partition: exactly one rule for each sex on every day from 1900 to the week;
- the working agrees with reference.py's independent Sch. 4 and with the tables' own two-month steps;
- planted errors: a wrong month offset, (7A) removed, 29 February, the boundary births (C01, C02, C04, C05),
  a period moved by a day, another wording, a wrong ordinal or weekday for the week;
- the guide's cut-offs must agree with Sch. 4 for the guide's week, else the profile is refused.
"""
from __future__ import annotations

import re
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1] / "usecases" / "eligibility"
sys.path.insert(0, str(HERE))

import pensionable_age as PA  # noqa: E402
import reference  # noqa: E402
import translation as T  # noqa: E402

LINES = PA.SCH4.read_text(encoding="utf-8").split("\n")
S1_LINES = PA.S1.read_text(encoding="utf-8").split("\n")
# The 82 open source-coverage units of Sch. 4 tagged temporal (reviews/relb/absent-1121.tsv, FAULTS.md section 4,
# groups P2-b to P2-j less the 9 tagged otherwise): unit -> first line; a unit is that line and the next.
OPEN_UNITS = {
    "S0116": 19, "S0117": 21, "S0118": 23, "S0119": 30, "S0120": 32, "S0121": 34, "S0122": 36, "S0123": 38,
    "S0124": 40, "S0126": 44, "S0127": 46, "S0128": 48, "S0129": 50, "S0130": 52, "S0131": 54, "S0132": 56,
    "S0133": 58, "S0134": 60, "S0136": 64, "S0137": 66, "S0138": 68, "S0139": 70, "S0140": 72, "S0141": 74,
    "S0142": 76, "S0143": 78, "S0144": 80, "S0146": 84, "S0147": 86, "S0148": 88, "S0149": 90, "S0150": 92,
    "S0151": 94, "S0152": 96, "S0153": 98, "S0154": 100, "S0156": 104, "S0157": 106, "S0158": 108, "S0159": 110,
    "S0160": 112, "S0161": 114, "S0162": 116, "S0163": 25, "S0166": 127, "S0167": 129, "S0168": 131, "S0169": 133,
    "S0170": 135, "S0171": 137, "S0172": 139, "S0173": 141, "S0174": 143, "S0176": 147, "S0178": 154, "S0179": 156,
    "S0180": 158, "S0181": 160, "S0182": 162, "S0183": 164, "S0184": 166, "S0186": 170, "S0187": 172, "S0188": 174,
    "S0189": 176, "S0190": 178, "S0191": 180, "S0192": 182, "S0193": 184, "S0194": 186, "S0196": 193, "S0197": 195,
    "S0198": 197, "S0199": 199, "S0200": 201, "S0201": 203, "S0202": 205, "S0203": 207, "S0204": 209, "S0206": 213,
    "S0207": 215, "S0208": 217,
}
D = date.fromisoformat


def changed(number, old, new, lines=LINES):
    out = list(lines)
    assert old in out[number - 1], (number, old, out[number - 1])
    out[number - 1] = out[number - 1].replace(old, new, 1)
    return out


def outcome(lines):
    try:
        s = PA.read_schedule4(lines)
        return ("read", s.rules, sorted(s.taken_to_attain.items()))
    except ValueError as exc:
        return ("refused", str(exc))


def test_the_schedule_is_read_whole():
    s = PA.read_schedule4()
    start, end = LINES.index("RulesE+W+S") + 1, LINES.index("Textual Amendments", LINES.index("RulesE+W+S"))
    assert s.lines_read == frozenset(n for n in range(start + 1, end + 1) if LINES[n - 1].strip())
    assert len(s.rules) == 82 and len(s.taken_to_attain) == 3
    assert [r.rule for r in s.rules].count("(3) table 1") == 44


@pytest.mark.parametrize("unit", sorted(OPEN_UNITS))
def test_each_open_unit_decides(unit):
    """Each line of the unit, changed (its first number that is not a footnote id moved by one, or its first word
    replaced), makes the reader refuse or read differently (reviews/spare/spare-ages-dates/measure.py, the same rule)."""
    base = outcome(LINES)
    for n in (OPEN_UNITS[unit], OPEN_UNITS[unit] + 1):
        text = LINES[n - 1]
        m = re.search(r"(?<![0-9F])[0-9]+", text)
        new = text[:m.start()] + str(int(m[0]) + 1) + text[m.end():] if m else re.sub(r"[A-Za-z]+", "Xx", text, count=1)
        assert outcome(changed(n, text, new)) != base, (unit, n)


def test_every_birth_has_one_rule_for_each_sex():
    s, born = PA.read_schedule4(), date(1900, 1, 1)
    while born <= D(T.QW1):
        for sex in ("man", "woman"):
            earliest, latest = PA.pensionable_age(born, sex, s)
            assert earliest <= latest
        born += timedelta(days=1)


def test_agrees_with_reference():
    """reference.py works Sch. 4 out separately (all births 6 Oct 1954 to 5 Apr 1977; before 6 Dec 1953 only the
    bound 5 Dec 2018) and the 80th birthday for every birth."""
    s, born, checked = PA.read_schedule4(), date(1935, 1, 1), 0
    while born <= date(1977, 4, 5):
        ours = PA.pensionable_age(born, schedule=s)
        try:
            theirs = reference.pensionable_age_dates(born)
        except NotImplementedError:  # table 2 births
            theirs = None
        if theirs is not None and born >= date(1953, 12, 6):
            assert ours == (min(theirs), max(theirs)), born
            checked += 1
        elif theirs is not None:
            assert ours[1] <= theirs[0] == date(2018, 12, 5), born
        their80 = reference.anniversaries(born, 80)
        assert PA.eightieth_birthday(born) == (min(their80), max(their80)), born
        born += timedelta(days=1)
    assert checked > 8000


@pytest.mark.parametrize("table,first_row_birth,first_day,rows,two_month_rows", [
    ("(3) table 1", date(1950, 4, 6), date(2010, 5, 6), 44, 36), ("(5) table 2", date(1953, 12, 6), date(2019, 3, 6), 10, 10),
    ("(9) table 4", date(1977, 4, 6), date(2044, 5, 6), 12, 12)])
def test_day_tables_step_by_months(table, first_row_birth, first_day, rows, two_month_rows):
    """Each row of tables 1, 2 and 4 is one month of births on; its day is two months on (four months on in table 1's
    last 8 rows, the Pensions Act 2011 entries), worked out here."""
    got = [r for r in PA.read_schedule4().rules if r.rule == table]
    assert len(got) == rows
    for k, r in enumerate(got):
        assert r.first == PA.anniversary(first_row_birth, 0, k)
        assert r.last == PA.anniversary(first_row_birth, 0, k + 1) - timedelta(days=1)
        steps = 2 * min(k, two_month_rows - 1) + 4 * max(0, k - two_month_rows + 1)
        assert r.day == PA.anniversary(first_day, 0, steps)


@pytest.mark.parametrize("birth,pa,age80", [
    ("1960-06-27", ("2026-09-27", "2026-09-27"), "2040-06-27"),  # C01
    ("1960-06-28", ("2026-09-28", "2026-09-28"), "2040-06-28"),  # C02
    ("1946-09-27", ("2006-09-27", "2011-09-27"), "2026-09-27"),  # C04: woman at 60 or man at 65
    ("1946-09-28", ("2006-09-28", "2011-09-28"), "2026-09-28"),  # C05
    ("1960-07-31", ("2026-11-30", "2026-11-30"), "2040-07-31"),  # (7A)(a)
    ("1960-12-31", ("2027-09-30", "2027-09-30"), "2040-12-31"),  # (7A)(b)
    ("1961-01-31", ("2027-11-30", "2027-11-30"), "2041-01-31"),  # (7A)(c)
    ("1960-02-29", ("2026-02-28", "2026-03-01"), "2040-02-29"),  # 29 February: the source does not fix the day
    ("1953-12-05", ("2018-11-06", "2018-12-05"), "2033-12-05"), ("1953-12-06", ("2019-03-06", "2019-03-06"), "2033-12-06"),
    ("1978-04-06", ("2046-04-06", "2046-04-06"), "2058-04-06"),
])
def test_boundaries(birth, pa, age80):
    assert PA.pensionable_age(D(birth)) == (D(pa[0]), D(pa[1]))
    assert PA.eightieth_birthday(D(birth)) == (D(age80), D(age80))


def test_planted_wrong_month_offset():
    """Table 3 row 3 says 66 years and 4 months: born 27 Jun 1960 then reads 27 Oct 2026, and the guide's cut-off
    (born on or before 27 June 1960) disagrees, so the profile is refused."""
    planted = PA.read_schedule4(changed(159, "66 years and 3 months", "66 years and 4 months"))
    assert PA.pensionable_age(D("1960-06-27"), schedule=planted) == (D("2026-10-27"), D("2026-10-27"))
    T._SCHEDULE4[:] = [planted]
    try:
        with pytest.raises(ValueError, match="guide's cut-off"):
            T.age_facts("applicant", "1960-06-27")
    finally:
        T._SCHEDULE4.clear()


def test_planted_7a_removed():
    """Without (7A)(a), 31 Jul 1960 has no single day (30 Nov or 1 Dec 2026): read differently, never rolled."""
    lines = list(LINES)
    del lines[177:179]  # "(a)" and its sentence
    assert PA.pensionable_age(D("1960-07-31"), schedule=PA.read_schedule4(lines)) == (D("2026-11-30"), D("2026-12-01"))


@pytest.mark.parametrize("number,old,new", [
    (156, "6th May 1960", "7th May 1960"),  # a period moved by a day: 6 May 1960 then has no rule
    (146, "born after", "born on or after"),  # a wording the reader does not read
    (155, "1 month", "1 months"),
    (179, "30th November 2026", "31st November 2026"),  # no such day
    (26, "F8", "F9"),  # rule (4) left out under a footnote that does not omit it
    (184, "(8)", "(9)"),
])
def test_planted_schedule_errors_are_refused(number, old, new):
    planted = changed(number, old, new)
    try:
        s = PA.read_schedule4(planted)
    except ValueError:
        return
    with pytest.raises(ValueError):
        PA.pensionable_age(D("1960-05-06"), schedule=s)


def test_qualifying_week():
    assert (T.QW0, T.QW1) == ("2026-09-21", "2026-09-27")  # the guide's S2:38 "21 to 27 September 2026"
    assert "between 21 to 27 September 2026" in (HERE / "source" / "wfp-print.txt").read_text(encoding="utf-8")
    assert PA.qualifying_week(2027) == (D("2027-09-20"), D("2027-09-26"))
    assert PA.qualifying_week(2025) == (D("2025-09-15"), D("2025-09-21"))
    for old, new, first in (("third Monday", "second Monday", "2026-09-14"), ("third Monday", "third Tuesday", "2026-09-15")):
        line = next(n for n, t in enumerate(S1_LINES, 1) if "“qualifying week”" in t)
        assert PA.qualifying_week(2026, changed(line, old, new, S1_LINES))[0] == D(first)
    with pytest.raises(ValueError):
        PA.qualifying_week(2026, changed(line, "third Monday", "last Monday", S1_LINES))


def test_birth_after_the_week_is_refused():
    with pytest.raises(ValueError):
        T.age_facts("applicant", "2026-09-28")


@pytest.mark.parametrize("birth,expected", [("1942-01-15", ("date_no_later", "2007-01-15")),
                                            ("1960-02-29", ("date_no_later", "2026-03-01"))])
def test_bounds_where_the_source_fixes_no_day(birth, expected):
    facts = {f["id"]: f["formula"] for f in T.age_facts("applicant", birth)}
    assert (facts["applicant.pa_date"][0], facts["applicant.pa_date"][2][1]) == expected
    assert facts["applicant.pa_date_from"][0] == "date_after"
