"""Tests of the six-year bridge (bridge/years.py). Run: python3 -I usecases/ved_first_year/bridge/test_years.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import years  # noqa: E402

CASES = [
    ("2020-06-15", "2026-06-15", (6, 0)),     # the sixth anniversary itself: not less than six years
    ("2020-06-15", "2026-06-14", (5, 364)),   # the day before: less than six years
    ("2020-06-15", "2026-06-16", (6, 1)),
    ("2019-03-01", "2025-02-28", (5, 364)),   # 2024-03-01 .. 2025-02-28 = 364 days
    ("2018-03-01", "2024-02-29", (5, 365)),   # leap day inside the last year: 2023-03-01 .. 2024-02-29 = 365 days
    ("2017-04-01", "2017-04-01", (0, 0)),
    ("2021-12-31", "2027-12-30", (5, 364)),
    ("2017-04-01", "2026-11-23", (9, 236)),
]


def main():
    fails = 0
    for reg, on, want in CASES:
        got = years.years(reg, on)
        ok = got == want
        fails += not ok
        print(("PASS" if ok else "FAIL"), reg, on, got)
    for bad in (("2020-02-29", "2026-03-01"), ("2026-01-02", "2026-01-01")):
        try:
            years.years(*bad)
            fails += 1
            print("FAIL refused input accepted", bad)
        except ValueError:
            print("PASS refused", bad)
    print(f"{len(CASES) + 2 - fails} passed, {fails} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
