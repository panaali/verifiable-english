"""Tests of the age bridge (bridge/age.py). Run: python3 -I usecases/council_tax/bridge/test_age.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import age  # noqa: E402

CASES = [
    ("2007-05-12", "2025-05-12", True),   # the 18th birthday itself: attained at its beginning
    ("2007-05-12", "2025-05-11", False),  # the day before
    ("2007-05-12", "2025-05-13", True),
    ("2007-03-01", "2025-02-28", False),  # 1 March birthday, day before in a common year
    ("2008-02-28", "2026-02-28", True),
    ("2008-02-28", "2026-02-27", False),
    ("2006-12-31", "2024-12-31", True),
    ("2006-12-31", "2024-12-30", False),
    ("1990-01-01", "2025-06-01", True),
    ("2010-06-01", "2025-06-01", False),  # aged 15
]


def main():
    fails = 0
    for dob, on, want in CASES:
        got = age.attained(dob, on)
        ok = got is want
        fails += not ok
        print(("PASS" if ok else "FAIL"), dob, on, got)
    try:
        age.attained("2008-02-29", "2026-03-01")
        fails += 1
        print("FAIL 29 February accepted")
    except ValueError:
        print("PASS 29 February refused")
    print(f"{len(CASES) + 1 - fails} passed, {fails} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
