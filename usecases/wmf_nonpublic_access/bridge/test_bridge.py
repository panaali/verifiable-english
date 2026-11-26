"""Tests of the WMF bridge (python3 -I test_bridge.py). Each value worked by hand from conventions A and B."""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wmf_bridge import attains, b10, count_after, row  # noqa: E402

D = dt.date.fromisoformat
NONE = set()
CASES = [
    (attains(D("2008-03-15"), 18), D("2026-03-15")),
    (attains(D("2010-12-31"), 16), D("2026-12-31")),
    (attains(D("1950-06-01"), 18), D("1970-01-01")),            # A: before 1970 entered as 1 January 1970
    (attains(D("1952-01-02"), 18), D("1970-01-02")),
    (row({"kind": "age", "dob": "2009-07-04"}), {"a16": "2025-07-04", "a18": "2027-07-04"}),
    # 2026-06-15 is a Monday: back from Mon 15 Jun: 15, 12, 11, 10, 9, 8 (Mon), 5, 4, 3, 2 Jun (Tue) = 10th
    (b10(D("2026-06-15"), NONE), D("2026-06-02")),
    # a Saturday disclosure day is not counted: Sat 20 Jun 2026 -> 19, 18, 17, 16, 15, 12, 11, 10, 9, 8 Jun
    (b10(D("2026-06-20"), NONE), D("2026-06-08")),
    # a named holiday is skipped: Wed 10 Jun named -> 15, 12, 11, 9, 8, 5, 4, 3, 2, 1 Jun
    (b10(D("2026-06-15"), {D("2026-06-10")}), D("2026-06-01")),
    (row({"kind": "b10", "day": "2026-06-15", "holidays": []}), {"b10": "2026-06-02"}),
    # the definition: sending on the day before b10 gives exactly ten business days; sending on b10 gives nine
    (count_after(D("2026-06-01"), D("2026-06-15"), NONE), 10),
    (count_after(D("2026-06-02"), D("2026-06-15"), NONE), 9),
    (count_after(D("2026-05-29"), D("2026-06-15"), NONE), 11),   # Fri 29 May: 1-5 Jun (5), 8-12 (5), 15 (1)
]


def check_equivalence():
    """For every s in a window and several t and holiday sets: count_after(s, t) >= 10 iff s < b10(t)."""
    bad = 0
    for t0 in ("2026-06-15", "2026-06-20", "2026-12-28", "2027-01-04"):
        t = D(t0)
        for hol in (NONE, {D("2026-06-10")}, {D("2026-12-25"), D("2027-01-01")}):
            b = b10(t, hol)
            for i in range(1, 40):
                s = t - dt.timedelta(days=i)
                bad += (count_after(s, t, hol) >= 10) != (s < b)
    return bad


def main():
    fails = sum(got != want for got, want in CASES)
    for got, want in CASES:
        if got != want:
            print("FAIL", got, "!=", want)
    eq = check_equivalence()
    print(f"{len(CASES) - fails}/{len(CASES)} bridge values; equivalence failures {eq}")
    return 1 if fails or eq else 0


if __name__ == "__main__":
    sys.exit(main())
