"""The ONE bridge script of the GitHub Sponsors (Sponsored Developer) translation (statute corpus batch 5; evidence branch,
not for merge). ISOLATION.md D5: it gives only DAYS from STATED days, the calendar steps the language has no form for
(the last day of a month, a month's 22nd, a month's third Thursday, "the same calendar date 12 months later", whole years
of age). It never gives an amount, a sum of money, a count compared with a limit of the text, or a yes/no of the text:
every period counted in days (30, 60, 90) and every comparison is written in Lean (translation.py).

- month_last(d): the last calendar day of the month containing d (the brief's convention (b): "close"/"end" of a month).
- next_22nd(first): the 22nd of the calendar month after the month whose first day is first (unit 38).
- next_third_thursday(first): the third Thursday of the calendar month after that month (unit 39).
- on_or_after(day, method): the first 22nd ("sc") / third Thursday ("aw") of any month that is on or after day;
  next_after_60(fd, method): that day for the day 60 days after fd (unit 37 reading B; Lean computes fd + 60 itself).
- twelve_months(acc): (lo, hi), the last day of the "first 12 months in the Program" (convention (c): up to and including
  the day before the same calendar date 12 months later). For an acceptance on 29 February the same date does not exist
  12 months later: lo = the day before 28 February (that date read as the same date), hi = 28 February (1 March read as
  it); the days between are two readings (translation.py: OPEN). Otherwise lo = hi.
- age(dob, day): whole years from dob to day (convention (e)); None for a 29 February birthday counted on 28 February
  of a common year (two readings: the birthday falls on 28 February or on 1 March).
The encoder calls these and enters the results as facts marked "bridge" (encode.py); the run records which answers rest on
them (uses_bridge).
"""
from __future__ import annotations

import calendar
import datetime as dt

D = dt.date.fromisoformat
ONE = dt.timedelta(days=1)


def month_last(d: str) -> str:
    x = D(d)
    return dt.date(x.year, x.month, calendar.monthrange(x.year, x.month)[1]).isoformat()


def _next_month(d: str):
    x = D(d)
    return (x.year + 1, 1) if x.month == 12 else (x.year, x.month + 1)


def _third_thursday(y: int, m: int) -> dt.date:
    first = dt.date(y, m, 1)
    off = (3 - first.weekday()) % 7          # Thursday = 3
    return first + dt.timedelta(days=off + 14)


def next_22nd(first: str) -> str:
    y, m = _next_month(first)
    return dt.date(y, m, 22).isoformat()


def next_third_thursday(first: str) -> str:
    y, m = _next_month(first)
    return _third_thursday(y, m).isoformat()


def on_or_after(day: str, method: str) -> str:
    x = D(day)
    y, m = x.year, x.month
    for _ in range(3):
        cand = dt.date(y, m, 22) if method == "sc" else _third_thursday(y, m)
        if cand >= x:
            return cand.isoformat()
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    raise AssertionError(day)


def twelve_months(acc: str):
    a = D(acc)
    y = a.year + 1
    if a.month == 2 and a.day == 29:
        return (dt.date(y, 2, 28) - ONE).isoformat(), dt.date(y, 2, 28).isoformat()
    same = dt.date(y, a.month, a.day)
    return (same - ONE).isoformat(), (same - ONE).isoformat()


def age(dob: str, day: str):
    b, d = D(dob), D(day)
    if (b.month, b.day) == (2, 29) and (d.month, d.day) == (2, 28) and not calendar.isleap(d.year):
        return None        # is the birthday on 28 February or on 1 March in a common year: two readings
    return d.year - b.year - ((d.month, d.day) < (b.month, b.day))


def next_after_60(fd: str, method: str) -> str:
    """The first 22nd ("sc") / third Thursday ("aw") on or after the day 60 days after fd (unit 37, reading B; Lean
    computes fd + 60 itself and compares it with this day)."""
    return on_or_after((D(fd) + dt.timedelta(days=60)).isoformat(), method)
