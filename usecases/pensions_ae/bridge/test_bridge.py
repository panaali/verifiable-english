"""Tests of pae_bridge.py (python3 -I test_bridge.py): hand-worked dates and ages."""
import datetime as dt
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pae_bridge as B  # noqa: E402

D = dt.date
CASES = [
    (B.age(D(2005, 5, 2), D(2027, 5, 1)), 21),     # the day before the 22nd birthday
    (B.age(D(2005, 5, 2), D(2027, 5, 2)), 22),     # the birthday itself
    (B.age(D(2005, 5, 2), D(2027, 5, 3)), 22),
    (B.age(D(2004, 2, 29), D(2026, 2, 28)), 21),   # 29 February: not yet in a non-leap year
    (B.age(D(2004, 2, 29), D(2026, 3, 1)), 22),    # 1 March in a non-leap year
    (B.age(D(2004, 2, 29), D(2028, 2, 29)), 24),   # leap year: on 29 February
    (B.age(D(2004, 2, 29), D(2028, 2, 28)), 23),
    (B.age(D(2011, 1, 31), D(2027, 1, 31)), 16),
    (B.age(D(1952, 7, 1), D(2027, 6, 30)), 74),
    (B.age(D(1952, 7, 1), D(2027, 7, 1)), 75),
    (B.pst(D(2027, 5, 1)), D(2026, 5, 1)),         # 12 months ending 30 April 2027
    (B.pst(D(2027, 3, 1)), D(2026, 3, 1)),         # ending 28 February 2027 -> from 1 March 2026
    (B.pst(D(2028, 3, 1)), D(2027, 3, 1)),         # ending 29 February 2028 -> 28 February 2027 + 1
    (B.pst(D(2027, 1, 1)), D(2026, 1, 1)),         # ending 31 December 2026
    (B.pst(D(2027, 3, 31)), D(2026, 3, 31)),
    (B.pst(D(2027, 7, 15)), D(2026, 7, 15)),
    (len(B.days(D(2027, 2, 1), D(2027, 3, 1))), 29),
    (B.days(D(2028, 2, 28), D(2028, 3, 1)), [D(2028, 2, 28), D(2028, 2, 29), D(2028, 3, 1)]),
    (B.days(D(2027, 4, 1), D(2027, 4, 1)), [D(2027, 4, 1)]),
]
bad = [(i, got, want) for i, (got, want) in enumerate(CASES) if got != want]
for b in bad:
    print("FAIL", *b)
print(f"{len(CASES) - len(bad)} passed, {len(bad)} failed")
sys.exit(1 if bad else 0)
