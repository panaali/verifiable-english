"""Tests of bridge.py (run: python3 -I usecases/canada_vacations/bridge/test_bridge.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bridge as B  # noqa: E402

fails = n = 0


def check(name, got, want):
    global fails, n
    n += 1
    ok = got == want
    fails += not ok
    print(("PASS " if ok else "FAIL ") + name, f"got {got!r} want {want!r}" if not ok else "")


# months and years (D5: same day number, else the month's last day)
check("ten months after 30 Apr 2027", B.ten_months("2027-04-30"), "2028-02-29")
check("ten months after 30 Apr 2026 (Feb, not leap)", B.ten_months("2026-04-30"), "2027-02-28")
check("ten months after 31 Dec 2026", B.ten_months("2026-12-31"), "2027-10-31")
check("ten months after 31 Mar 2027", B.ten_months("2027-03-31"), "2028-01-31")
check("ten months after 29 Apr 2027", B.ten_months("2027-04-29"), "2028-02-29")
check("ten months after 28 Apr 2027", B.ten_months("2027-04-28"), "2028-02-28")
check("add_years leap day back", B.add_years("2028-02-29", -1), "2027-02-28")
check("add_years", B.add_years("2020-03-15", 5), "2025-03-15")
# year counts (anniversary kind: first = start + m years)
check("first year completed", B.year_count("2026-03-15", "2027-03-14", "2026-03-15"), 1)
check("fifth year", B.year_count("2030-03-15", "2031-03-14", "2026-03-15"), 5)
check("tenth year", B.year_count("2035-03-15", "2036-03-14", "2026-03-15"), 10)
check("ninth year", B.year_count("2034-03-15", "2035-03-14", "2026-03-15"), 9)
check("year ended by termination the day before its last day", B.year_count("2026-03-15", "2027-03-14", "2026-03-15",
                                                                           "2027-03-13"), 0)
check("terminated on the last day: completed", B.year_count("2026-03-15", "2027-03-14", "2026-03-15", "2027-03-14"), 1)
# calendar kind, employment began part way through the previous year
check("calendar year after a part year", B.year_count("2027-01-01", "2027-12-31", "2026-07-01"), 1)
check("part calendar year is not a year", B.year_count("2026-01-01", "2026-12-31", "2026-07-01"), 0)
check("calendar year 5", B.year_count("2031-01-01", "2031-12-31", "2026-07-01"), 5)
try:
    B.year_count("2027-01-01", "2027-12-30", "2026-07-01")
    check("misaligned year refused", "accepted", "refused")
except ValueError:
    check("misaligned year refused", "refused", "refused")
# termination counts
check("kind years by termination, calendar", B.kind_years_by("2027-01-01", "2022-07-01", "2027-09-30"), 4)
check("elapsed years by termination", B.elapsed_years("2022-07-01", "2027-09-30"), 5)
check("elapsed: day before first anniversary", B.elapsed_years("2026-03-15", "2027-03-13"), 0)
check("elapsed: last day of the first year", B.elapsed_years("2026-03-15", "2027-03-14"), 1)
check("kind years, anniversary anchor", B.kind_years_by("2026-03-15", "2026-03-15", "2031-03-14"), 5)
check("kind years, anniversary anchor, day before", B.kind_years_by("2026-03-15", "2026-03-15", "2031-03-13"), 4)
check("less than one year", B.kind_years_by("2026-03-15", "2026-03-15", "2026-12-01"), 0)
# s.189(1.4): the period between employers left out
check("eff start, no gap", B.eff_start("2025-01-01", "2020-01-01", "2024-12-31"), "2020-01-01")
check("eff start, 30-day gap", B.eff_start("2025-01-31", "2020-01-01", "2024-12-31"), "2020-01-31")
check("eff start, current only", B.eff_start("2025-01-31"), "2025-01-31")
check("count B across a transfer", B.year_count("2025-01-01", "2025-12-31", B.eff_start("2025-01-01", "2020-01-01",
                                                                                         "2024-12-31")), 6)
print(f"## result: {n - fails} passed, {fails} failed")
sys.exit(1 if fails else 0)
