"""The one bridge script for RTOA 1988 s.35 (SELECTION.md: dates bridged for "within the three years immediately preceding";
[B5]). SAME-FAMILY.

It ONLY turns one pair of dates (A, E) into a duration in whole calendar months and days: the period from A to the day before
E. Every comparison with a limit (three years = 36 months, 56 days) and every sum is in translation.py. Convention (stated,
the same for every case):
P  a period from its first day F to its last day L inclusive lasts m whole calendar months and d days, where m is the
   largest number with F + m months <= L + 1 day (F + m months: the same day number m months later, or the first day of the
   following month when that month is too short) and d = (L + 1 day) - (F + m months) in days. For a pair (A, E) the period
   is F = A, L = E - 1 day; when A is not before E no duration is given (the order of the two dates is compared in Lean).
Input  bridge/inputs.jsonl: {"case", "item", "conv", "kind": "pair", "from", "to"}.
Output bridge/bridges.jsonl: {"case", "item", "conv", "values": {"months", "days"} or {}}.
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


def duration(first, last):
    end = last + dt.timedelta(days=1)
    if end <= first:
        raise ValueError("a period must have at least one day")
    m = 0
    while add_months(first, m + 1) <= end:
        m += 1
    return m, (end - add_months(first, m)).days


def pair(a, e):
    """Whole months and days from date a to the day before date e; {} when a is not before e."""
    if not a < e:
        return {}
    m, d = duration(a, e - dt.timedelta(days=1))
    return {"months": m, "days": d}


def row(r):
    if r["kind"] == "pair":
        return pair(dt.date.fromisoformat(r["from"]), dt.date.fromisoformat(r["to"]))
    raise ValueError(r["kind"])


def main(argv):
    here = Path(__file__).resolve().parent
    src = Path(argv[0]) if argv else here / "inputs.jsonl"
    out = Path(argv[1]) if len(argv) > 1 else here / "bridges.jsonl"
    lines = []
    for line in src.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            lines.append(json.dumps({"case": r["case"], "item": r["item"], "conv": r["conv"], "values": row(r)},
                                    sort_keys=True))
    out.write_text("".join(x + "\n" for x in lines), encoding="utf-8")
    print(f"{len(lines)} bridge rows -> {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
