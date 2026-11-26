"""Tests of bridge.py (made-up dates worked by hand). usage: .venv/bin/python -B usecases/gitlab_us_benefits/test_bridge.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bridge as B  # noqa: E402

CASES = [
    (B.first_of_next_month("2027-01-01"), "2027-02-01"),
    (B.first_of_next_month("2027-01-31"), "2027-02-01"),
    (B.first_of_next_month("2027-12-15"), "2028-01-01"),
    (B.first_of_next_month("2028-02-29"), "2028-03-01"),
    (B.month_day_after("2026-12-31", 3, 15), "2027-03-15"),
    (B.month_day_after("2026-12-31", 3, 31), "2027-03-31"),
    (B.month_day_after("2027-03-15", 3, 15), "2028-03-15"),
    (B.month_day_after("2027-03-14", 3, 15), "2027-03-15"),
    (B.month_day_of_year(2027, 4, 22), "2027-04-22"),
    (B.month_day_of_year("2028", 3, 31), "2028-03-31"),
    # 2027-03-31 is a Wednesday: Thu 1, Fri 2, Mon 5, Tue 6, Wed 7 April
    (B.business_days_after("2027-03-31", 5, B.MON_FRI), "2027-04-07"),
    # 2027-04-02 is a Friday: Mon 5, Tue 6, Wed 7
    (B.business_days_after("2027-04-02", 3, B.MON_FRI), "2027-04-07"),
    # 2027-04-03 is a Saturday: Mon 5, Tue 6, Wed 7
    (B.business_days_after("2027-04-03", 3, B.MON_FRI), "2027-04-07"),
    (B.business_days_after("2027-04-05", 1, B.MON_FRI), "2027-04-06"),
]
bad = [(i, got, exp) for i, (got, exp) in enumerate(CASES) if got != exp]
for name, args in (("calendar", ("2027-04-05", 3, "mon-sat")), ("n", ("2027-04-05", 0, B.MON_FRI))):
    try:
        B.business_days_after(*args)
        bad.append((name, "no error", "ValueError"))
    except ValueError:
        pass
for b in bad:
    print("FAIL", *b)
print(f"bridge tests: {len(CASES) + 2 - len(bad)}/{len(CASES) + 2}")
sys.exit(1 if bad else 0)
