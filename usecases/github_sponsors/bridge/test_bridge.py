"""Tests of bridge.py (run: python3 -I usecases/github_sponsors/bridge/test_bridge.py). Expected days checked by hand
against a calendar (weekdays: 2027-07-01 is a Thursday, 2027-10-01 a Friday, 2028-06-01 a Thursday)."""
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
    print(("PASS " if ok else "FAIL ") + name, "" if ok else f"got {got!r} want {want!r}")


# month ends: 28, 29, 30, 31 days; year end
check("Feb 2027 ends 28th", B.month_last("2027-02-01"), "2027-02-28")
check("Feb 2028 ends 29th (leap)", B.month_last("2028-02-15"), "2028-02-29")
check("Apr 2027 ends 30th", B.month_last("2027-04-30"), "2027-04-30")
check("Dec 2027 ends 31st", B.month_last("2027-12-01"), "2027-12-31")
# the 22nd of the next month
check("22nd after Mar 2027", B.next_22nd("2027-03-01"), "2027-04-22")
check("22nd after Dec 2027 (year changes)", B.next_22nd("2027-12-01"), "2028-01-22")
# third Thursday of the next month
check("third Thursday of Jul 2027 (starts on a Thursday)", B.next_third_thursday("2027-06-01"), "2027-07-15")
check("third Thursday of Oct 2027 (starts on a Friday)", B.next_third_thursday("2027-09-01"), "2027-10-21")
check("third Thursday of Jun 2028 (starts on a Thursday)", B.next_third_thursday("2028-05-01"), "2028-06-15")
check("third Thursday of Jan 2028", B.next_third_thursday("2027-12-01"), "2028-01-20")
# first schedule day on or after a day
check("22nd on or after 2027-03-22 is itself", B.on_or_after("2027-03-22", "sc"), "2027-03-22")
check("22nd on or after 2027-03-23", B.on_or_after("2027-03-23", "sc"), "2027-04-22")
check("22nd on or after 2027-12-23 (year end)", B.on_or_after("2027-12-23", "sc"), "2028-01-22")
check("third Thursday on or after 2027-07-15 is itself", B.on_or_after("2027-07-15", "aw"), "2027-07-15")
check("third Thursday on or after 2027-07-16", B.on_or_after("2027-07-16", "aw"), "2027-08-19")
check("first 22nd on or after 60 days after 2027-01-21 (2027-03-22)", B.next_after_60("2027-01-21", "sc"), "2027-03-22")
check("first 22nd on or after 60 days after 2027-01-22 (2027-03-23)", B.next_after_60("2027-01-22", "sc"), "2027-04-22")
check("first third Thursday on or after 60 days after 2027-05-16 (2027-07-15)", B.next_after_60("2027-05-16", "aw"), "2027-07-15")
# the first 12 months
check("12 months from 10 Mar 2027", B.twelve_months("2027-03-10"), ("2028-03-09", "2028-03-09"))
check("12 months from 31 Jan 2027", B.twelve_months("2027-01-31"), ("2028-01-30", "2028-01-30"))
check("12 months from 1 Mar 2027 (leap Feb before)", B.twelve_months("2027-03-01"), ("2028-02-29", "2028-02-29"))
check("12 months from 29 Feb 2028: two readings", B.twelve_months("2028-02-29"), ("2029-02-27", "2029-02-28"))
check("12 months from 31 Dec 2027", B.twelve_months("2027-12-31"), ("2028-12-30", "2028-12-30"))
# ages in whole years
check("age on the 13th birthday", B.age("2014-05-10", "2027-05-10"), 13)
check("age the day before the 13th birthday", B.age("2014-05-10", "2027-05-09"), 12)
check("age 17 the day before 18", B.age("2009-05-10", "2027-05-09"), 17)
check("29 Feb birthday on 28 Feb of a common year: two readings", B.age("2012-02-29", "2027-02-28"), None)
check("29 Feb birthday on 1 Mar of a common year", B.age("2012-02-29", "2027-03-01"), 15)
check("29 Feb birthday on 29 Feb", B.age("2012-02-29", "2028-02-29"), 16)
print(f"bridge tests: {n - fails}/{n}")
sys.exit(1 if fails else 0)
