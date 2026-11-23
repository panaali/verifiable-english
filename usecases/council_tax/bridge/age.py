"""The ONE bridge script of council tax England (statute corpus batch 2 law 5): Sch. 1 para. 3(1)(a) "has attained the
age of 18 years" on a day, from a stated date of birth. SAME-FAMILY evidence branch, not for merge.

Convention (stated in every question that needs it; not in the pinned text): a person attains an age at the beginning
of the anniversary of the date of birth. Nobody is born on 29 February (writer prompt): such an input is refused.
Input  bridge/inputs.jsonl : {"case", "person", "day", "dob", "date"}   (copied from the question's stated facts)
Output bridge/bridges.jsonl: {"case", "person", "day", "attained18"}     (enters the case as a stated fact, never typed)
Usage: python3 -I usecases/council_tax/bridge/age.py   (rewrites bridges.jsonl from inputs.jsonl)
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def attained(dob: str, on: str, years: int = 18) -> bool:
    b, d = dt.date.fromisoformat(dob), dt.date.fromisoformat(on)
    if (b.month, b.day) == (2, 29):
        raise ValueError("born on 29 February: no convention fixed (refused)")
    return d >= b.replace(year=b.year + years)


def main() -> int:
    rows = [json.loads(l) for l in (HERE / "inputs.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    out = [{"case": r["case"], "person": r["person"], "day": r["day"], "attained18": attained(r["dob"], r["date"])}
           for r in rows]
    (HERE / "bridges.jsonl").write_text("".join(json.dumps(o, sort_keys=True) + "\n" for o in out), encoding="utf-8")
    print(f"bridges.jsonl: {len(out)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
