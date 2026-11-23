#!/usr/bin/env python3
"""Tests for bridges.py (14 CFR 61.23 bridges). Hand-worked values, written before any question was read, plus planted
errors that each must be caught. usage: python3 -I test_bridges.py (exit 0 only when all pass)."""
import datetime as dt
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bridges as B  # noqa: E402

D = dt.date
passed = failed = 0


def ok(got, want, name):
    global passed, failed
    if got == want:
        passed += 1
    else:
        failed += 1
        print(f"FAIL {name}: got {got!r}, want {want!r}")


# end of the last day of the Nth month after the month of examination (hand-worked)
ok(B.end_of_nth_month_after(D(2024, 10, 9), 6), D(2025, 4, 30), "Oct 2024 + 6 -> 30 Apr 2025")
ok(B.end_of_nth_month_after(D(2024, 10, 9), 12), D(2025, 10, 31), "Oct 2024 + 12 -> 31 Oct 2025")
ok(B.end_of_nth_month_after(D(2024, 10, 9), 24), D(2026, 10, 31), "Oct 2024 + 24 -> 31 Oct 2026")
ok(B.end_of_nth_month_after(D(2024, 10, 9), 60), D(2029, 10, 31), "Oct 2024 + 60 -> 31 Oct 2029")
ok(B.end_of_nth_month_after(D(2023, 8, 31), 6), D(2024, 2, 29), "Aug 2023 + 6 -> 29 Feb 2024 (leap)")
ok(B.end_of_nth_month_after(D(2024, 8, 1), 6), D(2025, 2, 28), "Aug 2024 + 6 -> 28 Feb 2025")
ok(B.end_of_nth_month_after(D(2025, 7, 15), 6), D(2026, 1, 31), "Jul 2025 + 6 crosses the year -> 31 Jan 2026")
ok(B.end_of_nth_month_after(D(2025, 12, 1), 12), D(2026, 12, 31), "Dec 2025 + 12 -> 31 Dec 2026")
ok(B.end_of_nth_month_after(D(2025, 1, 31), 1), D(2025, 2, 28), "Jan 31 + 1 -> 28 Feb")
# ages
ok(B.age_on(D(1985, 6, 15), D(2025, 6, 14)), 39, "the day before the 40th birthday: 39")
ok(B.age_on(D(1985, 6, 15), D(2025, 6, 15)), 40, "on the 40th birthday: 40")
ok(B.age_on(D(1985, 6, 15), D(2025, 6, 16)), 40, "the day after: 40")
ok(B.anniversary(D(1966, 3, 1), 60), D(2026, 3, 1), "60th birthday")
# the 24 / 48 calendar-month windows (the prompt's example: a flight in March 2027, a course on or after 1 March 2025)
ok(B.end_of_nth_month_after(D(2025, 3, 1), 24), D(2027, 3, 31), "course 1 Mar 2025 supports flights to 31 Mar 2027")
ok(B.end_of_nth_month_after(D(2025, 2, 28), 24) < D(2027, 3, 1), True, "course 28 Feb 2025 does not support March 2027")
ok(B.end_of_nth_month_after(D(2022, 6, 2), 48), D(2026, 6, 30), "exam 2 Jun 2022 supports flights to 30 Jun 2026")
# 29 February refused
for s in ("2024-02-29",):
    try:
        B.iso(s)
        ok("accepted", "refused", "29 Feb refused")
    except ValueError:
        ok("refused", "refused", "29 Feb refused")
# a whole case
case = {"id": "X1", "facts": "Born 14 March 1971. First-class, examination on 9 October 2024; earlier third-class "
        "examination on October 2, 2022. Course completed 4 May 2026, comprehensive examination 2 June 2025. "
        "Applications 1 October 2024 (issued). Flight on 3 May 2025.",
        "birth": "1971-03-14", "flight_day": "2025-05-03", "certs": {"cert1": "2024-10-09", "cert2": "2022-10-02"},
        "apps": {"app1": "2024-10-01"}, "course_day": "2026-05-04", "basic_exam_day": "2025-06-02"}
b = B.bridge_case(case)
ok(b["certs"]["cert1"]["under40_exam"], False, "age 53 on 9 Oct 2024")
ok(b["certs"]["cert1"]["end6"], "2025-04-30", "cert1 end6")
ok(b["certs"]["cert1"]["held_by_d"], True, "cert1 held by D")
ok(b["later"], [["cert1", "cert2"]], "cert1 later than cert2 only")
ok(b["sixtieth"], "2031-03-14", "60th birthday")
ok(b["course_end24"], "2028-05-31", "course window end")
ok(b["basic_exam_end48"], "2029-06-30", "exam window end")
ok(b["certs"]["cert2"]["after_2006"], True, "after July 14, 2006")
young = B.bridge_case({**case, "birth": "1985-06-15", "facts": case["facts"] + " Born 15 June 1985."})
ok(young["certs"]["cert1"]["under40_exam"], True, "age 39 on 9 Oct 2024")
# planted errors: each must be caught
try:
    B.bridge_case({**case, "certs": {"cert1": "2024-10-08"}})
    ok("accepted", "refused", "planted: a date the facts do not state")
except LookupError:
    ok("refused", "refused", "planted: a date the facts do not state")
ok(B.end_of_nth_month_after(D(2024, 10, 9), 6) != D(2025, 4, 9), True, "planted: same-day reading (9 Apr) differs")
ok(B.end_of_nth_month_after(D(2024, 10, 9), 6) != D(2025, 3, 31), True, "planted: N-1 months differs")
ok(B.age_on(D(1985, 6, 15), D(2025, 6, 14)) != B.age_on(D(1985, 6, 15), D(2025, 6, 15)), True,
   "planted: a birthday-eve age equal to the birthday age")
ok(B.stated("born 14 March 1971", D(1971, 3, 4)), False, "planted: 4 March not matched inside 14 March")
# the CLI
p = subprocess.run([sys.executable, "-I", os.path.join(HERE, "bridges.py"), "--born", "1971-03-14", "--exam", "2024-10-09",
                    "--day", "2025-05-01"], capture_output=True, text=True)
ok(json.loads(p.stdout)["valid_on_day"]["6"], False, "CLI: 1 May 2025 is after the 6-month end")
print(f"test_bridges: {passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
