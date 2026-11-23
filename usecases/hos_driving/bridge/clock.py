"""The ONE bridge script of hos-driving (ISOLATION.md D3, SELECTION.md [B5]): time arithmetic only. SAME-FAMILY.

It may only (a) turn one pair of clock times (date + HH:MM, one time zone, no clock change: a fixed fact of every case)
into a duration in minutes, (b) turn a stated duration "D days H hours M minutes" into minutes (24 hours a day, 60
minutes an hour), and (c) list the start times of the n days of a window: the latest time at or before a moment that is
the carrier's designated start of a 24-hour period, and the same clock time on each of the n - 1 days before it.
It never compares a duration with a limit and never adds durations (every comparison and every sum is the translation's).
"""
from __future__ import annotations

import datetime as dt


def parse(stamp: str) -> dt.datetime:
    """'2026-06-01T06:00' -> naive datetime (one time zone, no clock change)."""
    return dt.datetime.strptime(stamp, "%Y-%m-%dT%H:%M")


def fmt(t: dt.datetime) -> str:
    return t.strftime("%Y-%m-%dT%H:%M")


def minutes_between(a: str, b: str) -> int:
    """(a) the duration from clock time a to clock time b, in minutes (negative if b is before a)."""
    delta = parse(b) - parse(a)
    secs = delta.days * 86400 + delta.seconds
    if secs % 60:
        raise ValueError("clock times are whole minutes")
    return secs // 60


def stated_minutes(days: int, hours: int, minutes: int) -> int:
    """(b) a stated duration in minutes."""
    if days < 0 or hours < 0 or minutes < 0:
        raise ValueError("negative duration")
    return days * 1440 + hours * 60 + minutes


def day_starts(moment: str, designated: str, n: int) -> list[str]:
    """(c) the n day-starts of the window ending with the day that contains the moment, latest first."""
    t = parse(moment)
    hh, mm = (int(x) for x in designated.split(":"))
    start = t.replace(hour=hh, minute=mm)
    if start > t:
        start -= dt.timedelta(days=1)
    return [fmt(start - dt.timedelta(days=i)) for i in range(n)]
