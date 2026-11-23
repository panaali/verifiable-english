"""The ONE bridge script of fwa-australia (statute corpus batch 3): the employee's age on the day the notice is given, as a
DURATION (whole years, days beyond them) from the stated date of birth ([B5]: a bridge only turns one pair of dates into a
duration; the comparison with 45 years stays in the translation, s. 117(3)(b), unit 8). SAME-FAMILY evidence branch.

Convention (whole years, a stated convention per [B5]): a whole year of age is completed on each anniversary of the date of
birth (the birthday); the days are those after the last birthday on or before the day. With the test's convention (over 45
from the day after the 45th birthday) the translation's "45 < years, or years = 45 and 0 < days" gives exactly that.
Nobody is born on 29 February in this law's cases: such an input is refused (no convention fixed).
Input  bridge/inputs.jsonl : {"case", "dob", "date"}      (copied from the question's stated facts: birth, notice day)
Output bridge/bridges.jsonl: {"case", "years", "days"}    (enters the case as stated constants agey_e, aged_e)
Usage: python3 -I usecases/fwa_australia/bridge/age.py   (rewrites bridges.jsonl from inputs.jsonl)
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def age(dob: str, on: str) -> tuple[int, int]:
    b, d = dt.date.fromisoformat(dob), dt.date.fromisoformat(on)
    if (b.month, b.day) == (2, 29):
        raise ValueError("born on 29 February: no convention fixed (refused)")
    if d < b:
        raise ValueError("day before the date of birth")
    years = d.year - b.year - (1 if (d.month, d.day) < (b.month, b.day) else 0)
    last = b.replace(year=b.year + years)
    return years, (d - last).days


def main() -> int:
    rows = [json.loads(l) for l in (HERE / "inputs.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    out = []
    for r in rows:
        y, n = age(r["dob"], r["date"])
        out.append({"case": r["case"], "years": y, "days": n})
    (HERE / "bridges.jsonl").write_text("".join(json.dumps(o, sort_keys=True) + "\n" for o in out), encoding="utf-8")
    print(f"bridges.jsonl: {len(out)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
