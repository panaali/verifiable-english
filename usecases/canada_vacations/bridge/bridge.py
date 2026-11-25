"""The ONE bridge script of the Canada Labour Code vacations translation (statute corpus batch 4; evidence branch, not for
merge). ISOLATION.md D4, D5: it gives only dates and counts of years from STATED dates (never an amount, a sum of money, or a
comparison with a limit of the text; never whether employment is deemed continuous: that is s.189, decided in Lean):

- add_years(d, n) / add_months(d, n): the same day number n years / months later; if that month has no such day, its last
  day (D5's convention, used for both);
- year_count(first, last, eff, end): the number of years of employment of the employer's kind completed by the last day of
  the year [first, last], that year included = the number of j >= 0 with add_years(first, -j) >= eff; 0 when the year itself
  is not completed (first < eff, or the employment ended (end) before last); [first, last] must be one year of the kind
  (last = add_years(first, 1) - 1 day);
- kind_years_by(anchor, eff, day): the number of whole years of the employer's kind [anchor + j years, anchor + j + 1 years
  - 1 day] (any integer j) that begin on or after eff and end on or before day;
- elapsed_years(eff, day): the largest n with add_years(eff, n) - 1 day <= day (whole years of continuous employment from eff
  through day);
- eff_start(start2, start1=None, end1=None): the start of the continuous employment: start2 (count A, the current employer);
  with the first employer (count B), start1 moved later by the days strictly between end1 and start2 (s.189(1.4): that
  period is not included);
- ten_months(last): add_months(last, 10) (unit 7(a), D5).
The encoder calls these and enters the results as facts marked "bridge" (encode.py).
"""
from __future__ import annotations

import calendar
import datetime as dt

D = dt.date.fromisoformat
ONE = dt.timedelta(days=1)


def _shift_month(d: dt.date, months: int) -> dt.date:
    m0 = d.year * 12 + (d.month - 1) + months
    y, m = divmod(m0, 12)
    m += 1
    return dt.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def add_months(d: str, n: int) -> str:
    return _shift_month(D(d), n).isoformat()


def add_years(d: str, n: int) -> str:
    return _shift_month(D(d), 12 * n).isoformat()


def ten_months(last: str) -> str:
    return add_months(last, 10)


def eff_start(start2: str, start1: str | None = None, end1: str | None = None) -> str:
    if start1 is None:
        return start2
    gap = (D(start2) - D(end1)).days - 1
    if gap < 0:
        raise ValueError("second employment begins before the first ends")
    return (D(start1) + dt.timedelta(days=gap)).isoformat()


def year_count(first: str, last: str, eff: str, end: str | None = None) -> int:
    if D(add_years(first, 1)) - ONE != D(last):
        raise ValueError(f"[{first}, {last}] is not one year")
    if D(first) < D(eff) or (end is not None and D(end) < D(last)):
        return 0
    j = 0
    while D(add_years(first, -(j + 1))) >= D(eff):
        j += 1
    return j + 1


def kind_years_by(anchor: str, eff: str, day: str) -> int:
    a = D(anchor)
    j = (D(eff).year - a.year) - 2
    n = 0
    while True:
        s = D(add_years(anchor, j))
        e = D(add_years(anchor, j + 1)) - ONE
        if s > D(day):
            return n
        if s >= D(eff) and e <= D(day):
            n += 1
        j += 1


def elapsed_years(eff: str, day: str) -> int:
    n = 0
    while D(add_years(eff, n + 1)) - ONE <= D(day):
        n += 1
    return n
