"""The ONE bridge script of the PostHog 'Time off' translation (statute corpus batch 4, posthog-leave). SAME-FAMILY evidence.

It computes dates only (never an amount, a sum, a count or a comparison with a limit of the text):
- deadline(start): the day "4 months before" a parental leave's first day, by the test's stated convention (WRITER-BRIEF.md,
  "MONTHS BEFORE A DAY"): the day with the same day-number 4 calendar months earlier, or the last day of that earlier month
  when it has no such day-number (unit 43).
- window(start): the first and last day of "the prior two full quarters" before a leave's first day (unit 45), PostHog's
  quarters being the calendar quarters (the test's fixed fact): the two calendar quarters before the quarter that contains
  the first day.
- quarter(year, n): the first and last day of calendar quarter n (1-4) of a year.
Usage: python3 -I posthog_bridge.py inputs.jsonl > bridges.jsonl (one {"case", "item", "kind", ...} per line in, one
{"case", "item", "values"} per line out). Tests: python3 -I test_bridge.py.
"""
import calendar
import datetime as dt
import json
import sys


def months_before(day, n):
    y, m = day.year, day.month - n
    while m < 1:
        y, m = y - 1, m + 12
    last = calendar.monthrange(y, m)[1]
    return dt.date(y, m, min(day.day, last))


def deadline(start):
    return months_before(start, 4)


def quarter(year, n):
    first = dt.date(year, 3 * (n - 1) + 1, 1)
    lm = 3 * n
    return first, dt.date(year, lm, calendar.monthrange(year, lm)[1])


def window(start):
    y, n = start.year, (start.month - 1) // 3 + 1      # the quarter containing the first day
    n1y, n1 = (y, n - 1) if n > 1 else (y - 1, 4)       # the quarter before it
    n2y, n2 = (n1y, n1 - 1) if n1 > 1 else (n1y - 1, 4)  # and the one before that
    return quarter(n2y, n2)[0], quarter(n1y, n1)[1]


def one(r):
    d = dt.date.fromisoformat
    if r["kind"] == "deadline":
        v = {"dl": deadline(d(r["start"])).isoformat()}
    elif r["kind"] == "window":
        a, b = window(d(r["start"]))
        v = {"qwf": a.isoformat(), "qwt": b.isoformat()}
    elif r["kind"] == "quarter":
        a, b = quarter(int(r["year"]), int(r["n"]))
        v = {"qfrom": a.isoformat(), "qto": b.isoformat()}
    else:
        raise ValueError(r["kind"])
    return {"case": r["case"], "item": r["item"], "kind": r["kind"], "values": v}


if __name__ == "__main__":
    for line in open(sys.argv[1], encoding="utf-8"):
        if line.strip():
            print(json.dumps(one(json.loads(line)), sort_keys=True))
