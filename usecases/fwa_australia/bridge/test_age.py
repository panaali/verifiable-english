"""Tests of the age bridge (bridge/age.py). Run: python3 -I usecases/fwa_australia/bridge/test_age.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import age  # noqa: E402

CASES = [
    ("1981-09-07", "2026-09-07", (45, 0)),    # the 45th birthday itself: 45 years 0 days (not over 45)
    ("1981-09-22", "2026-09-23", (45, 1)),    # the day after: over 45 under the test's convention
    ("1981-09-08", "2026-09-07", (44, 364)),  # the day before the 45th birthday (2025-09-08 .. 2026-09-07)
    ("1976-03-30", "2026-08-31", (50, 154)),
    ("1980-01-09", "2026-10-13", (46, 277)),
    ("1999-03-01", "2024-02-29", (24, 365)),  # leap year: 2023-03-01 .. 2024-02-29 = 365 days
    ("2000-12-31", "2026-12-30", (25, 364)),
    ("2000-01-01", "2000-01-01", (0, 0)),
]


def main():
    fails = 0
    for dob, on, want in CASES:
        got = age.age(dob, on)
        ok = got == want
        fails += not ok
        print(("PASS" if ok else "FAIL"), dob, on, got)
    for bad in (("1984-02-29", "2026-03-01"), ("2026-01-02", "2026-01-01")):
        try:
            age.age(*bad)
            fails += 1
            print("FAIL refused input accepted", bad)
        except ValueError:
            print("PASS refused", bad)
    print(f"{len(CASES) + 2 - fails} passed, {fails} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
