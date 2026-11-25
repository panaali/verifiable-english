"""Tests of wtr_bridge.py (python3 -I test_bridge.py): hand-worked dates and day counts."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import wtr_bridge as B  # noqa: E402


def v(**r):
    return B.one({"case": "T", "item": "y", **r})["values"]


CASES = [
    (v(kind="year", ys="2026-01-01"), {"yn": "2027-01-01", "ylen": 365}),
    (v(kind="year", ys="2024-01-01"), {"yn": "2025-01-01", "ylen": 366}),          # 29 Feb 2024 inside
    (v(kind="year", ys="2024-03-31"), {"yn": "2025-03-31", "ylen": 365}),          # 29 Feb 2024 before the year
    (v(kind="year", ys="2023-03-01"), {"yn": "2024-03-01", "ylen": 366}),          # 29 Feb 2024 inside
    (v(kind="rem", ys="2026-01-01", es="2026-10-20"), {"rem": 73}),                 # 20 Oct..31 Dec: 12+30+31
    (v(kind="rem", ys="2024-01-01", es="2024-07-02"), {"rem": 183}),                # 2 Jul..31 Dec 2024
    (v(kind="rem", ys="2026-01-01", es="2026-12-31"), {"rem": 1}),
    (v(kind="term", ys="2026-01-01", td="2026-03-15"), {"exp": 73}),                # 1 Jan..14 Mar: 31+28+14
    (v(kind="term", ys="2026-01-01", td="2026-01-01"), {"exp": 0}),
    (v(kind="term", ys="2026-01-01", td="2026-12-31"), {"exp": 364}),
    (v(kind="phb", ys="2007-09-30"), {"elb": 365, "lenb": 366}),                    # 1 Oct 2007..29 Sep 2008
    (v(kind="phb", ys="2007-01-01"), {"elb": 92, "lenb": 366}),                     # 1 Oct..31 Dec 2007
    (v(kind="phb", ys="2006-06-01"), {"elb": 0, "lenb": 366}),                      # ends 31 May 2007
    (v(kind="phd", ys="2008-10-01"), {"eld": 183, "lend": 365}),                    # 1 Apr..30 Sep 2009
    (v(kind="phd", ys="2009-03-31"), {"eld": 364, "lend": 365}),                    # 1 Apr 2009..30 Mar 2010
    (v(kind="phd", ys="2008-04-02"), {"eld": 1, "lend": 365}),                      # ends 1 Apr 2009
    (v(kind="e18", ys="2024-01-01"), {"e18": "2026-06-30"}),                        # from 1 Jan 2025: 18 months
    (v(kind="e18", ys="2025-04-01"), {"e18": "2027-09-30"}),
    (v(kind="anniv", ys="2026-05-10", es="2020-05-10"), {"a98": "2026-10-01", "aes": "2026-05-10"}),
    (v(kind="anniv", ys="2025-10-01", es="1998-10-02"), {"a98": "2025-10-01", "aes": "2025-10-02"}),
    (v(kind="anniv", ys="2026-01-01", agr="01-01"), {"a98": "2026-10-01", "aagr": "2026-01-01"}),
]
bad = [(i, got, want) for i, (got, want) in enumerate(CASES) if got != want]
for b in bad:
    print("FAIL", *b)
try:
    v(kind="anniv", ys="2026-03-01", es="2024-02-29")
    bad.append(("29 Feb not refused",))
    print("FAIL 29 February anniversary not refused")
except ValueError:
    pass
print(f"{len(CASES) + 1 - len(bad)} passed, {len(bad)} failed")
sys.exit(1 if bad else 0)
