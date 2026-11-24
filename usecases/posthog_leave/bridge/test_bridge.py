"""Tests of posthog_bridge.py (python3 -I test_bridge.py): hand-worked dates."""
import datetime as dt
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import posthog_bridge as B  # noqa: E402

D = dt.date
CASES = [
    (B.deadline(D(2027, 3, 15)), D(2026, 11, 15)),   # same day-number, across a year end
    (B.deadline(D(2027, 6, 30)), D(2027, 2, 28)),    # no 30 February 2027: the month's last day
    (B.deadline(D(2028, 6, 30)), D(2028, 2, 29)),    # leap year
    (B.deadline(D(2027, 6, 29)), D(2027, 2, 28)),
    (B.deadline(D(2027, 7, 31)), D(2027, 3, 31)),    # 31st -> 31st
    (B.deadline(D(2027, 8, 31)), D(2027, 4, 30)),    # no 31 April: the 30th
    (B.deadline(D(2027, 1, 1)), D(2026, 9, 1)),
    (B.deadline(D(2027, 4, 30)), D(2026, 12, 30)),
    (B.quarter(2027, 1), (D(2027, 1, 1), D(2027, 3, 31))),
    (B.quarter(2027, 2), (D(2027, 4, 1), D(2027, 6, 30))),
    (B.quarter(2027, 3), (D(2027, 7, 1), D(2027, 9, 30))),
    (B.quarter(2027, 4), (D(2027, 10, 1), D(2027, 12, 31))),
    (B.window(D(2027, 5, 10)), (D(2026, 10, 1), D(2027, 3, 31))),   # Q2 start: Q4 2026 and Q1 2027
    (B.window(D(2027, 4, 1)), (D(2026, 10, 1), D(2027, 3, 31))),    # first day of Q2: Q1 is full
    (B.window(D(2027, 1, 15)), (D(2026, 7, 1), D(2026, 12, 31))),   # Q1 start: Q3 and Q4 of the year before
    (B.window(D(2027, 2, 28)), (D(2026, 7, 1), D(2026, 12, 31))),
    (B.window(D(2027, 9, 30)), (D(2027, 1, 1), D(2027, 6, 30))),
    (B.window(D(2027, 12, 31)), (D(2027, 4, 1), D(2027, 9, 30))),
]
bad = [(i, got, want) for i, (got, want) in enumerate(CASES) if got != want]
for b in bad:
    print("FAIL", *b)
print(f"{len(CASES) - len(bad)} passed, {len(bad)} failed")
sys.exit(1 if bad else 0)
