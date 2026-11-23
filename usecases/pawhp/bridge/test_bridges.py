#!/usr/bin/env python3
"""Tests for bridges.py (stream 6, PAWHP, SAME-FAMILY): known values from the Act's own words, boundaries either side of the
2026 week, the 'born' extraction, and planted errors (a corrupted table, a wrong pin, wrong date arithmetic) that the
self-check or these tests must catch.  Run: python3 -I test_bridges.py   (exit 0 only when all pass)"""
import datetime as dt
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bridges as b  # noqa: E402

D = dt.date
T = b.load_tables()
passed = failed = 0


def ok(got, want, name):
    global passed, failed
    if got == want:
        passed += 1
        print("PASS  " + name)
    else:
        failed += 1
        print("FAIL  %s (got %r, want %r)" % (name, got, want))


# 1. qualifying week = the week beginning on the third Monday of September
for y, s in ((2024, D(2024, 9, 16)), (2025, D(2025, 9, 15)), (2026, D(2026, 9, 21)), (2027, D(2027, 9, 20)),
             (2030, D(2030, 9, 16))):
    ok(b.qualifying_week(y), (s, s + dt.timedelta(days=6)), "qualifying week %d starts %s" % (y, s))
w = b.week_bridges()
ok(w["twelve_weeks_before_from"], "2026-06-29", "12 weeks before the 2026 week start on 29 Jun 2026 (84 days)")
ok(w["fifty_two_weeks_before_from"], "2025-09-22", "52 weeks before the 2026 week start on 22 Sep 2025 (364 days)")
ok((w["march_31_following"], w["april_1_following"]), ("2027-03-31", "2027-04-01"), "31 March / 1 April following")

# 2. self-check of the pinned tables
ok(b.selfcheck(T), [], "tables 1-4 contiguous, spanning the rules' periods, rule (7A) reproduced")
ok([len(T[t]) for t in (1, 2, 3, 4)], [44, 10, 11, 12], "row counts 44, 10, 11, 12")

# 3. pensionable age, each rule, from the Act's words
cases = [
    ("1960-06-27", None, ["2026-09-27"], "table 3, 66y3m: release B's own bridge row (PLAN.md:284)"),
    ("1960-06-28", None, ["2026-09-28"], "table 3, 66y3m: one day after the week"),
    ("1960-07-31", None, ["2026-11-30"], "rule (7A)(a)"),
    ("1960-12-31", None, ["2027-09-30"], "rule (7A)(b)"),
    ("1961-01-31", None, ["2027-11-30"], "rule (7A)(c)"),
    ("1960-04-05", None, ["2026-04-05"], "rule (6): 66"),
    ("1960-04-06", None, ["2026-05-06"], "table 3 first row: 66y1m"),
    ("1961-03-05", None, ["2028-02-05"], "table 3 last row: 66y11m"),
    ("1961-03-06", None, ["2028-03-06"], "rule (8): 67"),
    ("1954-10-06", None, ["2020-10-06"], "rule (6) first day: 66"),
    ("1954-10-05", None, ["2020-09-06"], "table 2 last row"),
    ("1953-12-06", None, ["2019-03-06"], "table 2 first row"),
    ("1953-12-05", "m", ["2018-12-05"], "rule (1): a man at 65"),
    ("1950-04-05", "f", ["2010-04-05"], "rule (2): a woman at 60"),
    ("1950-04-06", "f", ["2010-05-06"], "table 1 first row"),
    ("1950-04-06", None, ["2010-05-06", "2015-04-06"], "sex not stated before 6 Dec 1953: both dates"),
    ("1977-04-06", None, ["2044-05-06"], "table 4 first row"),
    ("1978-04-06", None, ["2046-04-06"], "rule (10): 68"),
]
for born, sex, want, name in cases:
    ok([p.isoformat() for p in b.pa_dates(b.parse_date(born), T, sex)], want, "PA born %s: %s" % (born, name))
ok(b.bridges_for(D(1960, 6, 27), T)["reached_pa_by_week_end"], True, "born 27 Jun 1960 reaches PA on the week's last day")
ok(b.bridges_for(D(1960, 6, 28), T)["reached_pa_by_week_end"], False, "born 28 Jun 1960 reaches PA the day after")
ok(b.bridges_for(D(1950, 4, 6), T)["reached_pa_by_week_end"], True, "both sexes before the week: one answer")

# 4. 80th birthday
ok(b.bridges_for(D(1946, 9, 27), T)["reached_80_by_week_end"], True, "80 on 27 Sep 2026: reached in the week")
ok(b.bridges_for(D(1946, 9, 28), T)["reached_80_by_week_end"], False, "80 on 28 Sep 2026: not reached")
ok(b.bridges_for(D(1946, 9, 21), T)["reached_80_by_week_end"], True, "80 on the week's first day")
ok(b.anniversary(D(1944, 2, 29), 80).isoformat(), "2024-02-29", "29 Feb 1944 -> 80 on 29 Feb 2024 (leap year)")
ok(b.anniversary(D(1948, 2, 29), 78).isoformat(), "2026-03-01", "29 Feb 1948 -> 1 Mar 2026 (common year)")

# 5. date parsing and the 'born' extraction
for text, want in (("14 March 1955", "1955-03-14"), ("3rd May 1944", "1944-05-03"), ("March 14, 1955", "1955-03-14"),
                   ("1960-06-27", "1960-06-27"), ("6th December 1953", "1953-12-06")):
    ok(b.parse_date(text).isoformat(), want, "parse %r" % text)
facts = ("Mary was born 14 March 1955 and has lived in Perth since 3 May 1998. Her husband John, born on 2nd July 1944, "
         "moved in on 1 June 2026. Their lodger (date of birth: 1960-06-27) shares the house.")
ok([x[0] for x in b.births_in(facts)], ["14 March 1955", "2nd July 1944", "1960-06-27"], "three births, no other dates")

# 6. planted errors: each must be caught
src = open(b.SCH4, "rb").read().decode("utf-8")
with tempfile.TemporaryDirectory() as tmp:
    def planted(text):
        p = os.path.join(tmp, "sch4.txt")
        open(p, "w", encoding="utf-8").write(text)
        return b.selfcheck(b.load_tables(p, check_sha=False))
    ok(bool(planted(src.replace("| 6th June 1960 to 5th July 1960", "| 6th June 1960 to 4th July 1960", 1))), True,
       "planted: a table-3 period cut short (gap) is caught")
    ok(bool(planted(src.replace("| 66 years and 3 months", "| 66 years and 4 months", 1))), True,
       "planted: a table-3 age off by a month is caught (values not increasing)")
    ok(bool(planted(src.replace("| 6th March 2019", "| 6th May 2019", 1))), True,
       "planted: a table-2 day repeated is caught")
    ok(bool(planted(src.replace("| 6th April 1977 to 5th May 1977", "| 6th April 1976 to 5th May 1977", 1))), True,
       "planted: a table-4 span that starts too early is caught")
    p = os.path.join(tmp, "sch4.txt")
    open(p, "w", encoding="utf-8").write(src + " ")
    try:
        b.load_tables(p)
        ok("loaded", "refused", "planted: an unpinned Schedule 4 text is refused")
    except SystemExit:
        ok("refused", "refused", "planted: an unpinned Schedule 4 text is refused")
real = b.anniversary
b.anniversary = lambda born, years, months=0: born + dt.timedelta(days=round(365.25 * years + 30.44 * months))
ok(bool(b.selfcheck(T)), True, "planted: day-count date arithmetic (not calendar months) is caught by rule (7A)")
b.anniversary = lambda born, years, months=0: real(born, years, months) + dt.timedelta(days=1)
ok(bool(b.selfcheck(T)), True, "planted: an off-by-one birthday is caught by rule (7A)")
b.anniversary = real
real_qw = b.qualifying_week
b.qualifying_week = lambda y: (lambda s: (s, s + dt.timedelta(days=6)))(D(y, 9, 15) + dt.timedelta(days=(7 - D(y, 9, 15).weekday()) % 7 + 7))
ok(sum(b.qualifying_week(y)[0] != s for y, s in ((2024, D(2024, 9, 16)), (2025, D(2025, 9, 15)), (2026, D(2026, 9, 21)))) > 0,
   True, "planted: 'first Monday after 15 September + 7' is caught by the section 1 weeks")
b.qualifying_week = real_qw

print("result: %d passed, %d failed" % (passed, failed))
sys.exit(0 if failed == 0 else 1)
