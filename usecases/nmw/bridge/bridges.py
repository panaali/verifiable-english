"""The ONE bridge script of the NMW translation (ISOLATION.md D4): dates only, never an amount. SAME-FAMILY.

For each period of a case (inputs.jsonl: {"case", "first", "dob", "start", "prior_start"}) it gives
- age: the worker's age in whole years on the first day of the pay reference period (a person attains an age at the
  beginning of the anniversary of the date of birth; the prompt's stated convention; never 29 February);
- within12_cur / within12_prior: whether that first day is within the first 12 months after the commencement of the
  employment that commenced on start / prior_start (before the first anniversary of the commencement day; the
  commencement day itself is within; the prompt's stated convention; start days never the 29th-31st).
Run: python3 -I bridge/bridges.py  (reads inputs.jsonl, writes bridges.jsonl next to it).
"""
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def d(iso):
    return dt.date.fromisoformat(iso)


def age_on(dob, day):
    dob, day = d(dob), d(day)
    if (dob.month, dob.day) == (2, 29):
        raise ValueError("29 February date of birth is outside the stated convention")
    years = day.year - dob.year
    if (day.month, day.day) < (dob.month, dob.day):
        years -= 1
    return years


def within_first_12_months(start, day):
    start, day = d(start), d(day)
    if start.day > 28:
        raise ValueError("commencement on the 29th-31st is outside the stated convention")
    anniversary = start.replace(year=start.year + 1)
    return start <= day < anniversary


def bridge(row):
    out = {"case": row["case"], "first": row["first"], "age": age_on(row["dob"], row["first"])}
    if row.get("start"):
        out["within12_cur"] = within_first_12_months(row["start"], row["first"])
    if row.get("prior_start"):
        out["within12_prior"] = within_first_12_months(row["prior_start"], row["first"])
    return out


def main():
    src = os.path.join(HERE, "inputs.jsonl")
    rows = [json.loads(line) for line in open(src, encoding="utf-8") if line.strip()]
    with open(os.path.join(HERE, "bridges.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(bridge(r), sort_keys=True) + "\n")
    print(f"{len(rows)} bridge rows")


if __name__ == "__main__":
    sys.exit(main())
