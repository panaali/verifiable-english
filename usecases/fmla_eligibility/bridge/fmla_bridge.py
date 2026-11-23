"""The one bridge script for FMLA 825.110 (SELECTION.md: "Bridged: 12 months, 7 years, the 12-month period"; [B5]).

It ONLY turns one date into the first day of the 12-month period before it, or one pair of dates into a duration in whole
calendar months and days. Every sum and every comparison with a limit (12 months, 52 weeks, seven years, 1,250 hours, 50)
is in translation.py. SAME-FAMILY. Conventions (stated, the same for every case):
W  the 12-month period immediately preceding a leave starting on day D runs from the same calendar date one year before D
   (if that date does not exist, 29 February, the next day: 1 March) to the day before D.
P  a period from its first day F to its last day L inclusive lasts m whole calendar months and d days, where m is the
   largest number with F + m months <= L + 1 day (F + m months: the same day number m months later, or the first day of
   the following month when that month is too short) and d = (L + 1 day) - (F + m months) in days.
K  weeks run Monday to Sunday (every case states it): a period from F to L touches ((Monday of L's week) - (Monday of
   F's week)) / 7 + 1 weeks (used only where a case gives a period's dates and not its number of weeks).
Input  bridge/inputs.jsonl: {"case", "item", "kind": "window", "start"} or {"case", "item", "kind": "duration", "from", "to"}.
Output bridge/bridges.jsonl: {"case", "item", "values": {...}} (window: wfrom; duration: months, monthsup, days, weeks).
"""
import datetime as dt
import json
import sys
from pathlib import Path


def add_months(d, m):
    y, mo = divmod(d.month - 1 + m, 12)
    y, mo = d.year + y, mo + 1
    try:
        return dt.date(y, mo, d.day)
    except ValueError:  # the month is too short: the first day of the next month
        y2, mo2 = (y + 1, 1) if mo == 12 else (y, mo + 1)
        return dt.date(y2, mo2, 1)


def window_start(start):
    return add_months(start, -12)


def duration(first, last):
    end = last + dt.timedelta(days=1)
    if end <= first:
        raise ValueError("a period must have at least one day")
    m = 0
    while add_months(first, m + 1) <= end:
        m += 1
    d = (end - add_months(first, m)).days
    return m, d


def weeks(first, last):
    monday = lambda d: d - dt.timedelta(days=d.weekday())  # noqa: E731
    return (monday(last) - monday(first)).days // 7 + 1


def row(r):
    if r["kind"] == "window":
        return {"wfrom": window_start(dt.date.fromisoformat(r["start"])).isoformat()}
    if r["kind"] == "duration":
        m, d = duration(dt.date.fromisoformat(r["from"]), dt.date.fromisoformat(r["to"]))
        f, t = dt.date.fromisoformat(r["from"]), dt.date.fromisoformat(r["to"])
        return {"months": m, "days": d, "monthsup": m + (1 if d else 0), "weeks": weeks(f, t)}
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
