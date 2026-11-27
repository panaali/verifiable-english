"""Tests of bridges.py: hand-worked values and planted errors (each planted variant must give a different answer on at
least one fixture, so the fixtures would catch it). Run: python3 -I bridge/test_bridges.py"""
import datetime as dt
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bridges as B  # noqa: E402

FIX = [  # (instalment, due, payments, base_rates, expected pence, expected days) worked by hand
    # 13 days (2..14 Apr) x 1300 x 7.5% / 365 = 3.4726 -> 3.47
    ("1300.00", "2025-04-01", [["2025-04-15", "1300.00"]], [["2025-03-01", "2025-04-30", "4.50"]], 347, 13),
    # 1 day: paid the day after the due date: 1 x 1000 x 7% / 365 = 0.19178 -> 0.19
    ("1000.00", "2025-01-01", [["2025-01-03", "1000.00"]], [["2025-01-01", "2025-01-31", "4.00"]], 19, 1),
    # 1 x 1000 x 7.25% / 365 = 0.198630 -> rounded DOWN 0.19 (nearest would give 0.20)
    ("1000.00", "2025-01-01", [["2025-01-03", "1000.00"]], [["2025-01-01", "2025-01-31", "4.25"]], 19, 1),
    # paid on the due date: no day counted
    ("1000.00", "2025-01-01", [["2025-01-01", "1000.00"]], [["2025-01-01", "2025-01-31", "4.00"]], 0, 0),
    # part payment and a rate change: 8 d x 1690 @7.25 + 8 d x 690 @7.25 + 4 d x 690 @7.00 = 2.68548+1.09644+0.52932
    ("1690.00", "2025-09-01", [["2025-09-10", "1000.00"], ["2025-09-22", "690.00"]],
     [["2025-09-01", "2025-09-17", "4.25"], ["2025-09-18", "2025-09-30", "4.00"]], 431, 20),
    # across February 2026 (28 days): 2 Feb .. 2 Mar = 29 days x 2600 x 6.75% / 365 = 13.9438 -> 13.94
    ("2600.00", "2026-02-01", [["2026-03-03", "2600.00"]], [["2026-02-01", "2026-03-31", "3.75"]], 1394, 29),
    # leap year 2028: still /365: 2 days x 3650 x 10% / 365 = 2.00 exactly
    ("3650.00", "2028-02-28", [["2028-03-02", "3650.00"]], [["2028-02-01", "2028-03-31", "7.00"]], 200, 2),
]

passed = failed = 0


def check(name, got, want):
    global passed, failed
    if got == want:
        passed += 1
    else:
        failed += 1
        print("FAIL", name, got, want)


for i, (inst, due, pays, rates, pence, days) in enumerate(FIX):
    check(f"fixture {i}", B.late_rent_cap(inst, due, pays, rates), (pence, days))
check("gbp format", B.gbp(431), "4.31")
check("gbp format 2", B.gbp(5), "0.05")
try:
    B.late_rent_cap("100.00", "2025-01-01", [], [["2025-01-01", "2035-12-31", "4.00"]])
    check("never paid refused", "no error", "error")
except ValueError:
    check("never paid refused", "error", "error")
try:
    B.late_rent_cap("100.00", "2025-01-01", [["2025-01-05", "100.00"]], [["2025-01-01", "2025-01-02", "4.00"]])
    check("missing rate refused", "no error", "error")
except ValueError:
    check("missing rate refused", "error", "error")

# planted errors: each variant of late_rent_cap must disagree with some fixture
orig = B.late_rent_cap


def variant(**kw):
    def f(instalment, due, payments, base_rates, max_days=3660):
        start = dt.date.fromisoformat(due) + dt.timedelta(days=kw.get("start", 1))
        day, total, n = start, Fraction(0), 0
        while True:
            check_day = day - dt.timedelta(days=1) if kw.get("start_of_day") else day
            unpaid = B.unpaid_at_end(check_day, instalment, payments)
            if unpaid == 0:
                break
            yd = 366 if kw.get("leap") and day.year % 4 == 0 else kw.get("year", 365)
            margin = kw.get("margin", Fraction(3))
            total += (margin + B.rate_on(day, base_rates)) / 100 / yd * unpaid
            n += 1
            day += dt.timedelta(days=1)
        pence = total * 100
        p = round(pence) if kw.get("nearest") else pence.numerator // pence.denominator
        return int(p), n
    return f


PLANTED = {
    "counts the due date itself": variant(start=0),
    "reads the rent unpaid at the start of the day (counts the payment day)": variant(start_of_day=True),
    "divides by 360": variant(year=360),
    "366 in a leap year": variant(leap=True),
    "rounds to the nearest penny": variant(nearest=True),
    "margin 2% not 3%": variant(margin=Fraction(2)),
    "starts two days after the due date": variant(start=2),
}
for name, fn in PLANTED.items():
    differs = any(fn(i, d, p, r) != (pc, dy) for (i, d, p, r, pc, dy) in FIX)
    check(f"planted error caught: {name}", differs, True)
check("unplanted variant agrees (control)", all(variant()(i, d, p, r) == (pc, dy) for (i, d, p, r, pc, dy) in FIX), True)
print(f"test_bridges: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
