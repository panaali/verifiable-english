"""The ONE bridge script of statute corpus law 5 (Tenant Fees Act 2019): the Sch. 1 para. 4(5) late-rent cap. SAME-FAMILY.

Para. 4(5): "the aggregate of the amounts found by applying, in relation to each day after the due date for which the
rent remains unpaid, an annual percentage rate of 3% above the Bank of England base rate to the amount of rent that
remains unpaid at the end of that day." The text fixes no day count or rounding; the stated convention (SELECTION.md
counting rule, every question that needs it): simple interest; per day (3 + base rate that day) / 100 / 365 x the rent
unpaid at the end of that day; 365 in every year; the daily amounts added unrounded; the total rounded DOWN to the penny.
Days counted: due + 1, due + 2, ... while the rent unpaid at the end of the day is above zero.
Everything else in the law (one week's rent, the caps, every 7/14/15-day period) is written in VE (translation.py).

Input (inputs.jsonl, the encoder's transcription of stated facts, one line per item):
  {"case", "item", "instalment": "1300.00", "due": "2025-03-01", "payments": [["2025-03-14", "1300.00"]],
   "base_rates": [["2025-03-01", "2025-04-30", "4.50"]]}
Output (bridges.jsonl): {"case", "item", "intcap": "<GBP>", "days": <n>}
usage: python3 -I bridges.py inputs.jsonl > bridges.jsonl
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from fractions import Fraction

YEAR_DAYS = 365
MARGIN = Fraction(3)


def rate_on(day, base_rates):
    hits = [Fraction(r) for (a, b, r) in base_rates if dt.date.fromisoformat(a) <= day <= dt.date.fromisoformat(b)]
    if len(hits) != 1:
        raise ValueError(f"base rate on {day}: {len(hits)} stated values")
    return hits[0]


def unpaid_at_end(day, instalment, payments):
    paid = sum((Fraction(a) for (d, a) in payments if dt.date.fromisoformat(d) <= day), Fraction(0))
    return max(Fraction(instalment) - paid, Fraction(0))


def late_rent_cap(instalment, due, payments, base_rates, max_days=3660):
    """-> (cap in pence (int, rounded down), number of days counted)."""
    day = dt.date.fromisoformat(due) + dt.timedelta(days=1)
    total, n = Fraction(0), 0
    while True:
        unpaid = unpaid_at_end(day, instalment, payments)
        if unpaid == 0:
            break
        total += (MARGIN + rate_on(day, base_rates)) / 100 / YEAR_DAYS * unpaid
        n += 1
        day += dt.timedelta(days=1)
        if n > max_days:
            raise ValueError("rent never paid in full: no end day stated")
    pence = total * 100
    return pence.numerator // pence.denominator, n


def gbp(pence):
    return f"{pence // 100}.{pence % 100:02d}"


def main(argv):
    out = []
    for line in open(argv[0], encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        cap, n = late_rent_cap(r["instalment"], r["due"], r["payments"], r["base_rates"])
        out.append({"case": r["case"], "item": r["item"], "intcap": gbp(cap), "days": n})
    for o in out:
        print(json.dumps(o, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
