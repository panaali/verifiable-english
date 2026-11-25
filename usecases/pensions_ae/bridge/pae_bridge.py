"""The ONE bridge script of the Pensions Act 2008 ss. 1, 3, 5, 13 translation (statute corpus batch 4,
pensions-auto-enrolment). CROSS-FAMILY questions, Opus translator.

It computes dates and ages only (never an amount, a sum, a proportion or a comparison with a limit of the text):
- age(dob, day): the person's age in whole years on the day, by the test's stated convention (ISOLATION.md D3(a); the
  brief's "AGE"): an age is attained at the start of the anniversary of the date of birth; a person born on 29 February
  attains it on 1 March in a year that is not a leap year.
- pst(day): the first day of "the 12 months ending with the day before" the day (D3(d), the s. 3(4) prescribed period):
  the day after the day 12 calendar months before the day before; a day-number the earlier month lacks is its last day.
- days(first, last): every day of a stated window, first to last inclusive (D6: "a list of the days of a window").
- points(first, last, dob, dates): the window's points (translation R7a): its first day, every one of the given stated
  dates that falls inside it, and every birthday (age attained, D3(a)) inside it, sorted, each once; with the last day of
  each point's stretch (the day before the next point; the window's last day for the last point). A sub-list of the
  window's days and their neighbours: dates only.
Usage: python3 -I pae_bridge.py inputs.jsonl > bridges.jsonl (one {"case", "item", "kind", ...} per line in, one
{"case", "item", "kind", "values"} per line out). Tests: python3 -I test_bridge.py.
"""
import calendar
import datetime as dt
import json
import sys


def birthday(dob, year):
    if dob.month == 2 and dob.day == 29 and not calendar.isleap(year):
        return dt.date(year, 3, 1)
    return dt.date(year, dob.month, dob.day)


def age(dob, day):
    n = day.year - dob.year
    return n if birthday(dob, day.year) <= day else n - 1


def months_before(day, n):
    y, m = day.year, day.month - n
    while m < 1:
        y, m = y - 1, m + 12
    return dt.date(y, m, min(day.day, calendar.monthrange(y, m)[1]))


def pst(day):
    end = day - dt.timedelta(days=1)
    return months_before(end, 12) + dt.timedelta(days=1)


def days(first, last):
    out, d = [], first
    while d <= last:
        out.append(d)
        d += dt.timedelta(days=1)
    return out


def points(first, last, dob, dates):
    pts = {first} | {d for d in dates if first <= d <= last}
    for y in range(first.year, last.year + 1):
        b = birthday(dob, y)
        if first <= b <= last:
            pts.add(b)
    pts = sorted(pts)
    tts = [p - dt.timedelta(days=1) for p in pts[1:]] + [last]
    return pts, tts


def one(r):
    d = dt.date.fromisoformat
    if r["kind"] == "age":
        v = {"age": age(d(r["dob"]), d(r["day"]))}
    elif r["kind"] == "pst":
        v = {"pst": pst(d(r["day"])).isoformat()}
    elif r["kind"] == "aget":
        v = {"aget": age(d(r["dob"]), d(r["day"]))}
    elif r["kind"] == "points":
        pts, tts = points(d(r["first"]), d(r["last"]), d(r["dob"]), [d(x) for x in r.get("dates", [])])
        v = {"days": [x.isoformat() for x in pts], "tts": [x.isoformat() for x in tts]}
    elif r["kind"] == "days":
        v = {"days": [x.isoformat() for x in days(d(r["first"]), d(r["last"]))]}
    else:
        raise ValueError(r["kind"])
    return {"case": r["case"], "item": r["item"], "kind": r["kind"], "values": v}


if __name__ == "__main__":
    for line in open(sys.argv[1], encoding="utf-8"):
        if line.strip():
            print(json.dumps(one(json.loads(line)), sort_keys=True))
