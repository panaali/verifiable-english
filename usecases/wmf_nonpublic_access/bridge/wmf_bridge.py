"""The one bridge script for the WMF Access to Nonpublic Personal Data Policy (statute corpus batch 4; ISOLATION.md D4).

It ONLY turns a stated date of birth into the days the member attains 16 and 18 years of age, and a stated disclosure day
(with the case's named public holidays) into the tenth business day counting back from it. Every comparison with these
days, every period of days (one week, 90 calendar days) and every deadline is in translation.py (Lean checks them).
Conventions (stated by the cases, the same for every case):
A  a person attains an age at the beginning of the anniversary of the date of birth (no date of birth is 29 February);
   a day before January 1, 1970 is entered as January 1, 1970 (R12: every case day it is compared with is later).
B  a business day is a Monday to Friday that is not a public holiday the case names; b10 = the tenth business day counting
   back from the disclosure day, the disclosure day counted when it is a business day. (The business days after a day s up
   to and including the disclosure day number ten or more exactly when s is before b10.)
Input  bridge/inputs.jsonl: {"case", "item", "kind": "age", "dob"} or {"case", "item", "kind": "b10", "day", "holidays": [..]}.
Output bridge/bridges.jsonl: {"case", "item", "values": {...}} (age: a16, a18; b10: b10).
"""
import datetime as dt
import json
import sys
from pathlib import Path

EPOCH = dt.date(1970, 1, 1)


def attains(dob, years):
    if dob.month == 2 and dob.day == 29:
        raise ValueError("no date of birth is 29 February (convention A)")
    return max(dob.replace(year=dob.year + years), EPOCH)


def business(day, holidays):
    return day.weekday() < 5 and day not in holidays


def b10(day, holidays):
    n, d = 0, day
    while True:
        if business(d, holidays):
            n += 1
            if n == 10:
                return d
        d -= dt.timedelta(days=1)


def count_after(s, t, holidays):
    """The business days after s up to and including t (used by the tests only)."""
    n, d = 0, s + dt.timedelta(days=1)
    while d <= t:
        n += business(d, holidays)
        d += dt.timedelta(days=1)
    return n


def row(r):
    if r["kind"] == "age":
        dob = dt.date.fromisoformat(r["dob"])
        return {"a16": attains(dob, 16).isoformat(), "a18": attains(dob, 18).isoformat()}
    if r["kind"] == "b10":
        hol = {dt.date.fromisoformat(h) for h in r.get("holidays", ())}
        return {"b10": b10(dt.date.fromisoformat(r["day"]), hol).isoformat()}
    raise ValueError(r["kind"])


def main(argv):
    here = Path(__file__).resolve().parent
    src = Path(argv[0]) if argv else here / "inputs.jsonl"
    out = Path(argv[1]) if len(argv) > 1 else here / "bridges.jsonl"
    lines = []
    for line in src.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            lines.append(json.dumps({"case": r["case"], "item": r["item"], "values": row(r)}, sort_keys=True))
    out.write_text("".join(x + "\n" for x in lines), encoding="utf-8")
    print(f"{len(lines)} bridge rows -> {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
