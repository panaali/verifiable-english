"""Pensionable age, the 80th birthday and the qualifying week, worked out from the source text (spare-ages-dates).

`read_schedule4` reads Pensions Act 1995 Sch. 4 para. 1 (source/ukpga-1995-26-sch4.txt) itself: rules (1) to (10),
tables 1 to 4 and rule (7A). It knows one wording per kind of line and refuses (ValueError) the whole schedule at the
first line it does not read, so no rule is taken from a sentence it read only in part. `pensionable_age` then gives,
for a birth date, the day pensionable age is attained, as bounds (`earliest`, `latest`): the two are equal where the
source fixes one day. They differ where it does not:
- an age reached on a day the target month lacks (29 February 1960 plus 66 years) outside rule (7A): the source does
  not say which day; both candidates are kept (the last day of the month, and the first day of the next);
- a birth before 6 December 1953 with no sex given: rules (1) to (3) differ for men and women; both are kept.
`qualifying_week` reads the definition of the qualifying week (S1, uksi-2025-969-made.txt) and works out its first day.

Python, not Lean: W6a dates start on 1970-01-01 and every birth date here is earlier (probe P1), and W6a has no month
or year offsets. tests/test_spare_ages_dates.py checks this module against an independent working (reference.py) and
with planted errors. It imports nothing from reference.py.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCH4 = HERE / "source" / "ukpga-1995-26-sch4.txt"
S1 = HERE / "source" / "uksi-2025-969-made.txt"
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December")
_DAY = rf"([1-9]|[12][0-9]|3[01])(?:st|nd|rd|th) ({'|'.join(MONTHS)}) ([0-9]{{4}})"
_NUMBER = r"([1-9][0-9]?)"
_FIRST_LINE, _LAST_LINE = "RulesE+W+S", "Textual Amendments"
_HEADERS = {"| (1)", "| (2)", "| (1) Period within which woman’s birthday falls", "| (2) Day pensionable age attained",
            "| Period within which birthday falls", "| Day pensionable age attained", "| Age pensionable age attained"}
_TABLE_RULE = (r"A (woman|person) born on any day in a period mentioned in column 1 of table ([1-4]) attains pensionable age "
               r"(at the commencement of the day shown against that period in column 2|when the person attains the age "
               r"shown against that period in column 2)\.")
_AGE_RULES = (  # (pattern, groups: sex, after, before, years)
    (rf"A man born before {_DAY} attains pensionable age when he attains the age of {_NUMBER} years\.", "man"),
    (rf"A woman born before {_DAY} attains pensionable age when she attains the age of {_NUMBER}\.", "woman"),
    (rf"A person born after {_DAY} but before {_DAY} attains pensionable age when the person attains the age of "
     rf"{_NUMBER}\.", "person"),
    (rf"A person born after {_DAY} attains pensionable age when the person attains the age of {_NUMBER}\.", "person"),
)
_RULE_7A = (rf"a person born on {_DAY} is to be taken to attain the age of {_NUMBER} years and {_NUMBER} months at the "
            rf"commencement of {_DAY}[;.]")


@dataclass(frozen=True)
class Rule:
    """One way pensionable age is attained: births from `first` to `last` (None: open), for `sex` ("man", "woman"
    or "person"), attain it on `day`, or at `years` and `months` of age. `lines` are the source lines read for it."""
    rule: str
    sex: str
    first: date | None
    last: date | None
    day: date | None
    years: int | None
    months: int
    lines: tuple


@dataclass(frozen=True)
class Schedule4:
    rules: tuple
    taken_to_attain: dict  # rule (7A): (birth, years, months) -> day
    lines_read: frozenset


def _day(match, first):
    return date(int(match[first + 2]), MONTHS.index(match[first + 1]) + 1, int(match[first]))


def _footnotes(lines):
    ids = set()
    for line in lines:
        m = re.match(r"F([0-9]+)(?:Words|Sch\.)", line)
        if m:
            ids.add(m[1])
    return ids


def _clean(text, footnotes):
    """Drop the amendment markers "[F<n>" (n one of the schedule's own footnotes, the longest that fits) and "]"."""
    out, i = [], 0
    while i < len(text):
        if text.startswith("[F", i):
            digits = re.match(r"[0-9]+", text[i + 2:])
            if digits:
                fits = [n for n in range(len(digits[0]), 0, -1) if digits[0][:n] in footnotes]
                if not fits:
                    raise ValueError(f"an amendment marker that is no footnote of the schedule: {text!r}")
                i += 2 + fits[0]
                continue
        if text[i] != "]":
            out.append(text[i])
        i += 1
    return "".join(out)


def _age(text):
    m = re.fullmatch(r"\| ([0-9]+) years and ([0-9]+) months?", text)
    if not m or (m[2] == "1") != text.endswith("month"):
        raise ValueError(f"not an age: {text!r}")
    return int(m[1]), int(m[2])


def read_schedule4(lines=None):
    """Read Sch. 4 para. 1 rules (1) to (10). Raises ValueError at the first line it does not read."""
    if lines is None:
        lines = SCH4.read_text(encoding="utf-8").split("\n")
    notes = _footnotes(lines)
    start = lines.index(_FIRST_LINE) + 1
    end = lines.index(_LAST_LINE, start)
    rules, taken, read = [], {}, set()
    table, table_rule, table_sex, by_age, pending = None, None, None, False, None
    number, expect, tables_seen = 0, None, set()
    for i in range(start, end):
        n, text = i + 1, _clean(lines[i], notes)
        label = re.fullmatch(r"\(([0-9]+A?|[a-c])\)", text)
        where = f"Sch4:{n}"
        if label:
            if pending:
                raise ValueError(f"{where}: a table row without its second column")
            if label[1] in "abc":
                if expect != "7A":
                    raise ValueError(f"{where}: an item outside rule (7A)")
            else:
                number += 1 if label[1] != "7A" else 0
                if label[1] != ("7A" if label[1] == "7A" else str(number)):
                    raise ValueError(f"{where}: rule {label[1]} out of order")
                expect, table = label[1], None
            read.add(n)
            continue
        omitted = re.fullmatch(r"F([0-9]+)(?:\. ?)+", text)
        if omitted:  # a rule omitted by amendment: its footnote must say so
            if not any(line.startswith(f"F{omitted[1]}Sch. 4 para. 1 rule ({expect}) omitted") for line in lines):
                raise ValueError(f"{where}: rule ({expect}) left out, but footnote F{omitted[1]} does not omit it")
            read.add(n)
            continue
        if expect == "7A":
            if text == "For the purposes of table 3—":
                read.add(n)
                continue
            m = re.fullmatch(_RULE_7A, text)
            if not m:
                raise ValueError(f"{where}: not read: {text!r}")
            taken[(_day(m, 1), int(m[4]), int(m[5]))] = _day(m, 6)
            read.add(n)
            continue
        heading = re.fullmatch(r"TABLE ([1-4])", text)
        if heading:
            if table_rule is None or table_rule[1] != heading[1] or table_rule[1] in tables_seen:
                raise ValueError(f"{where}: table {heading[1]} not announced by the rule before it")
            tables_seen.add(heading[1])
            table = heading[1]
            read.add(n)
            continue
        if text in _HEADERS and table:
            read.add(n)
            continue
        if text.startswith("| ") and table:
            if pending is None:
                m = re.fullmatch(rf"\| {_DAY} to {_DAY}", text)
                if not m:
                    raise ValueError(f"{where}: not a period: {text!r}")
                pending = (_day(m, 1), _day(m, 4), n)
            else:
                first, last, row = pending
                if by_age:
                    years, months = _age(text)
                    day = None
                else:
                    m = re.fullmatch(rf"\| {_DAY}", text)
                    if not m:
                        raise ValueError(f"{where}: not a day: {text!r}")
                    day, years, months = _day(m, 1), None, 0
                rules.append(Rule(f"({table_rule[0]}) table {table}", table_sex, first, last, day, years, months, (row, n)))
                read.update((row, n))
                pending = None
            continue
        m = re.fullmatch(_TABLE_RULE, text)
        if m:
            table_rule, table_sex, by_age = (expect, m[2]), m[1], m[3].startswith("when")
            read.add(n)
            continue
        for pattern, sex in _AGE_RULES:
            m = re.fullmatch(pattern, text)
            if not m:
                continue
            if m.re.groups == 7:  # after D1 but before D2
                first, last, years = _day(m, 1) + timedelta(days=1), _day(m, 4) - timedelta(days=1), int(m[7])
            elif pattern.startswith("A person born after"):
                first, last, years = _day(m, 1) + timedelta(days=1), None, int(m[4])
            else:
                first, last, years = None, _day(m, 1) - timedelta(days=1), int(m[4])
            rules.append(Rule(f"({expect})", sex, first, last, None, years, 0, (n,)))
            read.add(n)
            break
        else:
            raise ValueError(f"{where}: not read: {text!r}")
    if pending:
        raise ValueError("a table row without its second column at the end of the schedule")
    if number != 10:
        raise ValueError(f"rules (1) to (10) expected, read {number}")
    return Schedule4(tuple(rules), taken, frozenset(read))


def anniversary(birth, years, months=0):
    """The day `years` and `months` after `birth`, or None when the target month has no such day."""
    total = birth.month - 1 + months
    try:
        return date(birth.year + years + total // 12, total % 12 + 1, birth.day)
    except ValueError:
        return None


def attained(birth, years, months=0, taken=None):
    """(earliest, latest) day an age is attained (at the commencement of the day, SCOPE.md: Family Law Reform Act
    1969 s. 9). A day the target month lacks: rule (7A) where it applies (`taken`), else both candidates."""
    day = anniversary(birth, years, months)
    if day is not None:
        return day, day
    if taken and (birth, years, months) in taken:
        return taken[(birth, years, months)], taken[(birth, years, months)]
    first_of_next = anniversary(birth.replace(day=1), years, months + 1)
    return first_of_next - timedelta(days=1), first_of_next


def _sexes(sex):
    return ("man", "woman") if sex is None else (sex,)


def pensionable_age(birth, sex=None, schedule=None):
    """(earliest, latest) day `birth` attains pensionable age; `sex` "man", "woman" or None (not given). Exactly one
    rule must apply for each possible sex, else ValueError."""
    schedule = schedule or read_schedule4()
    bounds = []
    for s in _sexes(sex):
        hits = [r for r in schedule.rules if r.sex in (s, "person") and (r.first is None or r.first <= birth)
                and (r.last is None or birth <= r.last)]
        if len(hits) != 1:
            raise ValueError(f"born {birth} ({s}): {len(hits)} rules of Sch. 4 apply")
        (rule,) = hits
        if rule.day is not None:
            bounds.append((rule.day, rule.day))
        else:
            bounds.append(attained(birth, rule.years, rule.months,
                                   schedule.taken_to_attain if "table 3" in rule.rule else None))
    return min(b[0] for b in bounds), max(b[1] for b in bounds)


def eightieth_birthday(birth):
    return attained(birth, 80)


_ORDINALS = ("first", "second", "third", "fourth")
_WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
QW_DEFINITION = (rf"“qualifying week” means in respect of any year the week beginning on the ({'|'.join(_ORDINALS)}) "
                 rf"({'|'.join(_WEEKDAYS)}) in the ({'|'.join(MONTHS)}) of that year;")


def qualifying_week(year, lines=None):
    """(first day, last day) of the qualifying week of `year`, from its definition in S1 reg. 1(3)."""
    if lines is None:
        lines = S1.read_text(encoding="utf-8").split("\n")
    found = [m for m in (re.fullmatch(QW_DEFINITION, line) for line in lines) if m]
    if len(found) != 1:
        raise ValueError(f"{len(found)} definitions of the qualifying week read")
    (m,) = found
    first = date(year, MONTHS.index(m[3]) + 1, 1)
    first += timedelta(days=(_WEEKDAYS.index(m[2]) - first.weekday()) % 7)
    first += timedelta(weeks=_ORDINALS.index(m[1]))
    return first, first + timedelta(days=6)
