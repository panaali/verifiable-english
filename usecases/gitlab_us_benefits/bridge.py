"""The ONE bridge script of the GitLab US benefits translation (statute corpus batch 5): calendar dates the language has no
step for. Dates and business days only; AMOUNTS ARE NEVER BRIDGED. Every unit that reads one of these values is ledgered
"bridged". Tested by test_bridge.py (made-up dates worked by hand).

- first_of_next_month(d):          unit 75 "Changes take effect on the 1st of the following month".
- month_day_after(d, month, day):  unit 83 "the March 15 / March 31" that first follow the stated plan year end.
- month_day_of_year(year, m, day): unit 86 "March 31 / April 22 of the current tax year" (the case states the year).
- business_days_after(d, n):       units 47, 86: the n-th business day after d (d is day 0), ONLY for the calendar the
                                   case states as "business days are Monday to Friday" with no public holidays in the
                                   period; any other calendar raises (the question is refused, never guessed).
"""
from __future__ import annotations

import datetime as dt

MON_FRI = "mon-fri, no holidays"


def _d(s):
    return dt.date.fromisoformat(s)


def first_of_next_month(d):
    x = _d(d)
    return (dt.date(x.year + 1, 1, 1) if x.month == 12 else dt.date(x.year, x.month + 1, 1)).isoformat()


def month_day_after(d, month, day):
    x = _d(d)
    y = dt.date(x.year, month, day)
    return (y if y > x else dt.date(x.year + 1, month, day)).isoformat()


def month_day_of_year(year, month, day):
    return dt.date(int(year), month, day).isoformat()


def business_days_after(d, n, calendar):
    if calendar != MON_FRI:
        raise ValueError(f"bridge: unsupported business-day calendar {calendar!r} (refuse)")
    x, left = _d(d), int(n)
    if left < 1:
        raise ValueError("bridge: n must be at least 1")
    while left:
        x += dt.timedelta(days=1)
        if x.weekday() < 5:
            left -= 1
    return x.isoformat()


def sha256():
    import hashlib
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
