"""The ONE bridge script of ved-first-year (statute corpus batch 3): the time from a vehicle's first registration to the
date on which a vehicle licence has effect, as a DURATION (whole years, days beyond them) ([B5]: a bridge only turns one
pair of dates into a duration; the comparison with six years stays in the translation, 1GE(1)(b), unit 36). SAME-FAMILY.

Convention (whole years, the anniversary convention): a whole year is completed on each anniversary of the first
registration date; the days are those after the last anniversary on or before the licence's date. So "less than six
years before the date" = whole years < 6: a licence taking effect on the sixth anniversary is NOT less than six years
after (6 years 0 days); the day before it is (5 years, 364 or 365 days).
A first registration on 29 February has no anniversary in a common year: such an input is refused (no convention fixed).
A licence date before the first registration is refused.
Input  bridge/inputs.jsonl : {"case", "licence", "registered", "date"}   (copied from the question's stated facts)
Output bridge/bridges.jsonl: {"case", "licence", "years", "days"}        (enter the case as stated constants ly_, ld_)
Usage: python3 -I usecases/ved_first_year/bridge/years.py   (rewrites bridges.jsonl from inputs.jsonl)
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def years(registered: str, on: str) -> tuple[int, int]:
    r, d = dt.date.fromisoformat(registered), dt.date.fromisoformat(on)
    if (r.month, r.day) == (2, 29):
        raise ValueError("first registered on 29 February: no convention fixed (refused)")
    if d < r:
        raise ValueError("licence date before the first registration")
    y = d.year - r.year - (1 if (d.month, d.day) < (r.month, r.day) else 0)
    last = r.replace(year=r.year + y)
    return y, (d - last).days


def main() -> int:
    rows = [json.loads(l) for l in (HERE / "inputs.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    out = []
    for row in rows:
        y, n = years(row["registered"], row["date"])
        out.append({"case": row["case"], "licence": row["licence"], "years": y, "days": n})
    (HERE / "bridges.jsonl").write_text("".join(json.dumps(o, sort_keys=True) + "\n" for o in out), encoding="utf-8")
    print(f"bridges.jsonl: {len(out)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
