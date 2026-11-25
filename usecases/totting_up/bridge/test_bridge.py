"""Tests of the s.35 bridge (python3 -I test_bridge.py). Each value worked by hand from convention P."""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from totting_bridge import duration, pair, row  # noqa: E402

D = dt.date.fromisoformat
CASES = [
    (pair(D("2021-05-01"), D("2024-05-01")), {"months": 36, "days": 0}),   # the same date three years before: R4 refuses
    (pair(D("2021-05-02"), D("2024-05-01")), {"months": 35, "days": 29}),  # a day inside: 2 May 2021 + 35 months = 2 Apr 2024; to 30 Apr
    (pair(D("2021-04-30"), D("2024-05-01")), {"months": 36, "days": 1}),   # a day outside
    (pair(D("2023-01-10"), D("2024-03-05")), {"months": 13, "days": 24}),  # 10 Jan 2023 + 13 months = 10 Feb 2024; to 4 Mar
    (pair(D("2024-03-05"), D("2024-03-05")), {}),                          # same day: no duration
    (pair(D("2024-06-01"), D("2024-03-05")), {}),                          # after: no duration
    (pair(D("2024-03-04"), D("2024-03-05")), {"months": 0, "days": 1}),
    (pair(D("2021-02-28"), D("2024-02-29")), {"months": 36, "days": 1}),   # leap day: 28 Feb 2021 + 36 months = 28 Feb 2024
    (pair(D("2021-03-01"), D("2024-02-29")), {"months": 35, "days": 28}),  # 1 Mar 2021 + 35 = 1 Feb 2024; to 28 Feb
    (pair(D("2020-02-29"), D("2023-03-01")), {"months": 36, "days": 0}),   # 29 Feb + 36 months -> 1 Mar 2023 (P) = E
    (duration(D("2026-01-31"), D("2026-02-28")), (1, 0)),                  # 31 Jan + 1 month -> 1 Mar (P)
    (row({"kind": "pair", "from": "2022-11-15", "to": "2025-11-14"}), {"months": 35, "days": 30}),
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
