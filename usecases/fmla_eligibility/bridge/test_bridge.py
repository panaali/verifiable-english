"""Tests of the FMLA bridge (python3 -I test_bridge.py). Each value worked by hand from the conventions W and P."""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fmla_bridge import duration, row, weeks, window_start  # noqa: E402

D = dt.date.fromisoformat
CASES = [
    (window_start(D("2026-03-02")), D("2025-03-02")),
    (window_start(D("2025-03-01")), D("2024-03-01")),
    (window_start(D("2028-02-29")), D("2027-03-01")),          # W: 29 February a year back does not exist
    (window_start(D("2026-01-05")), D("2025-01-05")),
    (duration(D("2025-09-29"), D("2026-01-04")), (3, 7)),        # 29 Sep - 4 Jan inclusive: 3 months 7 days
    (duration(D("2025-01-06"), D("2026-01-05")), (12, 0)),       # a full year
    (duration(D("2025-01-06"), D("2026-01-04")), (11, 30)),      # one day short of 12 months
    (duration(D("2025-01-06"), D("2025-12-28")), (11, 23)),      # 52 Monday-Sunday weeks, 11 months 23 days
    (duration(D("2018-03-01"), D("2025-02-28")), (84, 0)),       # exactly seven years (no case may use it)
    (duration(D("2018-03-01"), D("2025-03-01")), (84, 1)),       # seven years and a day
    (duration(D("2018-03-02"), D("2025-02-28")), (83, 27)),      # short of seven years: +83 months = 2 Feb 2025; 2 Feb..28 Feb = 27 days
    (duration(D("2026-01-31"), D("2026-02-28")), (1, 0)),        # 31 Jan + 1 month -> 1 Mar (P) = 28 Feb + 1 day: 1 month
    (duration(D("2026-01-31"), D("2026-02-27")), (0, 28)),
    (duration(D("2026-05-01"), D("2026-05-01")), (0, 1)),
    (row({"kind": "duration", "from": "2025-09-29", "to": "2026-01-04"}), {"months": 3, "days": 7, "monthsup": 4, "weeks": 14}),
    (row({"kind": "duration", "from": "2025-01-06", "to": "2026-01-05"}), {"months": 12, "days": 0, "monthsup": 12, "weeks": 53}),
    (weeks(D("2025-01-27"), D("2026-03-29")), 61),               # Monday to Sunday: 427 days = 61 weeks
    (weeks(D("2023-01-02"), D("2026-09-06")), 192),              # a stated count in the question file, checked
    (weeks(D("2025-01-06"), D("2026-03-01")), 60),               # a stated count in the question file, checked
    (weeks(D("2026-05-03"), D("2026-05-04")), 2),                # Sunday then Monday: two weeks touched
    (weeks(D("2026-05-05"), D("2026-05-07")), 1),
    (row({"kind": "window", "start": "2026-07-06"}), {"wfrom": "2025-07-06"}),
]
bad = [(i, got, want) for i, (got, want) in enumerate(CASES) if got != want]
for b in bad:
    print("FAIL", b)
try:
    duration(D("2026-05-02"), D("2026-05-01"))
    print("FAIL empty period accepted")
    bad.append("empty")
except ValueError:
    pass
print(f"{len(CASES) + 1 - len(bad)}/{len(CASES) + 1} passed")
sys.exit(1 if bad else 0)
