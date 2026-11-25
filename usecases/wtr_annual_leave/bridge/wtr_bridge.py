"""The ONE bridge script of the Working Time Regulations 1998 annual-leave translation (statute corpus batch 4,
wtr-annual-leave). CROSS-FAMILY evidence.

It computes dates and numbers of calendar days between two dates only (D6: never an amount, a proportion, a sum or a
comparison with a limit of the text):
- year(ys): the first day of the next leave year (the anniversary of ys: same day and month a year later) and the calendar
  days of the leave year (yn - ys).
- rem(ys, es): the calendar days of the leave year from es, es included, to the end of the leave year (yn - es).
- term(ys, td): the calendar days of the leave year before td (td - ys).
- phb(ys): the days of the year beginning 1 October 2007 elapsed at the end of the leave year (its last day included),
  clipped to that year, and that year's days.
- phd(ys): the same for the year beginning 1 April 2009.
- e18(ys): the last day of the period of 18 months from the end of the leave year (the day before the date 18 calendar
  months after the next leave year's first day).
- anniv(ys, es, agr): the day in the calendar year of ys with the month and day of es, of 1 October 1998, and of the
  agreement's date (month and day).
A 29 February anniversary is refused (no such input in the cases). Usage: python3 -I wtr_bridge.py inputs.jsonl >
bridges.jsonl (one {"case", "item", "kind", ...} per line in, one {"case", "item", "kind", "values"} per line out).
Tests: python3 -I test_bridge.py.
"""
import datetime as dt
import json
import sys

D = dt.date.fromisoformat


def anniversary(day, year):
    if (day.month, day.day) == (2, 29):
        raise ValueError("29 February anniversary")
    return dt.date(year, day.month, day.day)


def next_year(ys):
    return anniversary(ys, ys.year + 1)


def add_months(day, n):
    y, m = day.year, day.month - 1 + n
    y, m = y + m // 12, m % 12 + 1
    return dt.date(y, m, day.day)        # day 1 only in use (the first day of a leave year); others refused below


def clip_elapsed(start, ys):
    """Days of the year beginning `start` elapsed at the end of the leave year beginning ys (last day included)."""
    end_year = next_year(start)                   # the year beginning `start` ends the day before
    ly_last = next_year(ys) - dt.timedelta(days=1)
    upto = min(ly_last, end_year - dt.timedelta(days=1))
    n = (upto - start).days + 1
    return max(0, n), (end_year - start).days


def one(r):
    k = r["kind"]
    if k == "year":
        ys = D(r["ys"])
        yn = next_year(ys)
        v = {"yn": yn.isoformat(), "ylen": (yn - ys).days}
    elif k == "rem":
        ys, es = D(r["ys"]), D(r["es"])
        v = {"rem": (next_year(ys) - es).days}
    elif k == "term":
        ys, td = D(r["ys"]), D(r["td"])
        v = {"exp": (td - ys).days}
    elif k == "phb":
        n, ln = clip_elapsed(dt.date(2007, 10, 1), D(r["ys"]))
        v = {"elb": n, "lenb": ln}
    elif k == "phd":
        n, ln = clip_elapsed(dt.date(2009, 4, 1), D(r["ys"]))
        v = {"eld": n, "lend": ln}
    elif k == "e18":
        yn = next_year(D(r["ys"]))
        if yn.day != 1:
            raise ValueError("e18 only for leave years beginning on the 1st of a month")
        v = {"e18": (add_months(yn, 18) - dt.timedelta(days=1)).isoformat()}
    elif k == "anniv":
        ys = D(r["ys"])
        v = {"a98": anniversary(dt.date(1998, 10, 1), ys.year).isoformat()}
        if r.get("es"):
            v["aes"] = anniversary(D(r["es"]), ys.year).isoformat()
        if r.get("agr"):
            v["aagr"] = anniversary(D("2000-" + r["agr"]), ys.year).isoformat()
    else:
        raise ValueError(k)
    return {"case": r["case"], "item": r["item"], "kind": k, "values": v}


if __name__ == "__main__":
    for line in open(sys.argv[1], encoding="utf-8"):
        if line.strip():
            print(json.dumps(one(json.loads(line)), sort_keys=True))
