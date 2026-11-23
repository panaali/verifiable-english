"""Tests of bridges.py: hand-worked values and planted errors (each planted variant must give a different answer on at
least one fixture). Run: python3 -I bridge/test_bridges.py"""
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bridges as B  # noqa: E402

AGE = [  # (dob, day, years) worked by hand
    ("2008-06-01", "2026-06-01", 18),   # birthday on the first day: attained at its beginning
    ("2008-06-02", "2026-06-01", 17),   # birthday the next day
    ("2005-05-31", "2026-06-01", 21),
    ("2005-06-15", "2026-06-01", 20),
    ("2007-12-31", "2026-01-01", 18),
    ("2008-01-01", "2026-12-31", 18),
    ("2007-03-01", "2026-02-28", 18),   # not yet 19
]
W12 = [  # (start, day, within) worked by hand
    ("2025-06-01", "2026-05-31", True),
    ("2025-06-01", "2026-06-01", False),  # the first anniversary is outside
    ("2025-06-01", "2025-06-01", True),   # the commencement day itself
    ("2026-04-15", "2026-05-01", True),
    ("2024-09-10", "2026-04-01", False),
    ("2026-07-01", "2026-06-01", False),  # before commencement: not within
]
passed = failed = 0


def check(name, got, want):
    global passed, failed
    if got == want:
        passed += 1
    else:
        failed += 1
        print("FAIL", name, got, want)


for dob, day, want in AGE:
    check(f"age {dob} {day}", B.age_on(dob, day), want)
for s, day, want in W12:
    check(f"w12 {s} {day}", B.within_first_12_months(s, day), want)


def planted_age_off_by_one(dob, day):  # birthday counted only from the next day
    dob_, day_ = dt.date.fromisoformat(dob), dt.date.fromisoformat(day)
    y = day_.year - dob_.year
    return y - 1 if (day_.month, day_.day) <= (dob_.month, dob_.day) else y


def planted_w12_inclusive(start, day):  # anniversary counted as within
    s, x = dt.date.fromisoformat(start), dt.date.fromisoformat(day)
    return s <= x <= s.replace(year=s.year + 1)


check("planted age caught", any(planted_age_off_by_one(a, b) != w for a, b, w in AGE), True)
check("planted w12 caught", any(planted_w12_inclusive(a, b) != w for a, b, w in W12), True)
for bad in (("2008-02-29", "2026-06-01"),):
    try:
        B.age_on(*bad)
        check("29 Feb refused", False, True)
    except ValueError:
        check("29 Feb refused", True, True)
print(f"{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
