"""Independent Art. I §7 calendar table; certification awaits numbers2."""
from ve.units import day_number, iso_date


def deadline(start, count):
    day = start
    remaining = count
    while remaining:
        day += 1
        if day % 7 != 3:  # 1970-01-01 was Thursday; Sunday has residue 3.
            remaining -= 1
    return day


def test_seven_presentment_weekdays_and_zero():
    expected = [
        ("2026-09-14", 4, 11, "2026-09-25"),
        ("2026-09-15", 5, 11, "2026-09-26"),
        ("2026-09-16", 6, 12, "2026-09-28"),
        ("2026-09-17", 0, 12, "2026-09-29"),
        ("2026-09-18", 1, 12, "2026-09-30"),
        ("2026-09-19", 2, 12, "2026-10-01"),
        ("2026-09-20", 3, 11, "2026-10-01"),
    ]
    for spelling, residue, offset, result in expected:
        start = day_number(spelling)
        assert start % 7 == residue
        assert deadline(start, 0) == start
        end = deadline(start, 10)
        assert end - start == offset
        assert iso_date(end) == result
        assert start + 11 <= end
    sunday = day_number("2026-09-20")
    assert sunday + 12 > deadline(sunday, 10)
