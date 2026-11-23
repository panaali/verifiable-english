"""Tests of bridge/clock.py (run: python3 -I usecases/hos_driving/bridge/test_clock.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clock as C  # noqa: E402

cases = [
    (C.minutes_between("2026-06-01T06:00", "2026-06-01T11:00"), 300),
    (C.minutes_between("2026-05-30T06:00", "2026-06-01T06:00"), 2880),
    (C.minutes_between("2026-06-01T16:00", "2026-06-02T01:59"), 599),
    (C.minutes_between("2026-06-02T02:00", "2026-06-01T16:00"), -600),
    (C.minutes_between("2026-02-28T23:00", "2026-03-01T01:00"), 120),
    (C.stated_minutes(2, 0, 0), 2880), (C.stated_minutes(0, 9, 59), 599), (C.stated_minutes(3, 10, 0), 4920),
    (C.day_starts("2026-06-02T02:00", "00:00", 3), ["2026-06-02T00:00", "2026-06-01T00:00", "2026-05-31T00:00"]),
    (C.day_starts("2026-06-02T05:59", "06:00", 2), ["2026-06-01T06:00", "2026-05-31T06:00"]),
    (C.day_starts("2026-06-02T06:00", "06:00", 1), ["2026-06-02T06:00"]),
    (C.day_starts("2026-07-13T11:30", "12:00", 8)[-1], "2026-07-05T12:00"),
    (len(C.day_starts("2026-07-13T11:30", "00:00", 7)), 7),
]
bad = [i for i, (got, want) in enumerate(cases) if got != want]
for fn, args in ((C.stated_minutes, (-1, 0, 0)),):
    try:
        fn(*args)
        bad.append("no error")
    except ValueError:
        pass
print(f"bridge clock tests: {len(cases) + 1 - len(bad)} passed, {len(bad)} failed {bad}")
sys.exit(1 if bad else 0)
