#!/usr/bin/env python3
"""Stream 6 (PAWHP, SAME-FAMILY) bridges: the date facts the language does not compute, from the dates a question states
(PAGE.md [B7]: never computed by the encoder). Pure Python, no VE import. Tests: test_bridges.py beside this file.

Bridges:
  qualifying week of a year      reg. 2: the week beginning on the third Monday of September (Monday..Sunday)
  12 weeks / 52 weeks before     reg. 2 "residential care", reg. 9(a): the first day of the 84 / 364 days immediately
                                 preceding the week
  31 March / 1 April following   reg. 16B(2), 9B(3)(b)(i), 11(2): 31 March and 1 April of the next calendar year
  pensionable-age date           Pensions Act 1995 sch. 4 para. 1, rules (1)-(10) and tables 1-4, parsed from the pinned
                                 source file (sha256 checked); "attains the age of N" = the start of the Nth birthday,
                                 29 February -> 1 March in a common year (Age of Legal Capacity (Scotland) Act 1991 s.6,
                                 an outside rule stated here); "N years and M months" lands on the same day of the month,
                                 or the month's last day when that day does not exist (rule (7A) confirms the three cases
                                 it lists). A birth date before 6 December 1953 depends on sex (rules (1)-(3)): both dates
                                 are given when the question does not state it.
  80th birthday                  reg. 10(4)(a)(i), 10(3), 10(6): the start of the 80th birthday (29 Feb -> 1 Mar)

usage:
  python3 -I bridges.py --selfcheck                       parse the tables and check them (exit 0 only when sound)
  python3 -I bridges.py --born 1960-06-27 [--sex f|m]      one birth date
  python3 -I bridges.py --questions questions.jsonl        one JSON line per question: every birth date stated in "facts"
                                                          with its bridges and its comparisons with the 2026 week
"""
import calendar
import datetime as dt
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCH4 = os.environ.get("PAWHP_SCH4", os.path.join(HERE, "..", "..", "..", "..", "tools-local", "pawhp-indq", "source",
                                                 "ukpga-1995-26-sch4.txt"))
SCH4_SHA = "4d1fe57c20e9e0778cb28514bd2bea66d32d500614f9d925a8e1419a6d129815"
YEAR = 2026
MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
D = dt.date


def qualifying_week(year):
    sep1 = D(year, 9, 1)
    first_monday = sep1 + dt.timedelta(days=(7 - sep1.weekday()) % 7)
    start = first_monday + dt.timedelta(days=14)
    return start, start + dt.timedelta(days=6)


def anniversary(born, years, months=0):
    """The start of the day the person attains <years> years and <months> months."""
    y, m = born.year + years + (born.month - 1 + months) // 12, (born.month - 1 + months) % 12 + 1
    last = calendar.monthrange(y, m)[1]
    if born.month == 2 and born.day == 29 and months == 0 and last == 28:
        return D(y, 3, 1)  # 29 February in a common year -> 1 March (Scotland: 1991 Act s.6(2))
    return D(y, m, min(born.day, last))


def parse_date(text):
    t = re.sub(r"(\d)(st|nd|rd|th)\b", r"\1", text.strip().replace("[F10", "").replace("[", "").replace("]", ""))
    m = re.fullmatch(r"(\d{1,2}) ([A-Za-z]+),? (\d{4})", t)
    if m and m.group(2).lower() in MONTHS:
        return D(int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1)))
    m = re.fullmatch(r"([A-Za-z]+) (\d{1,2}),? (\d{4})", t)
    if m and m.group(1).lower() in MONTHS:
        return D(int(m.group(3)), MONTHS[m.group(1).lower()], int(m.group(2)))
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", t)
    if m:
        return D(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    raise ValueError("not a date: %r" % text)


def load_tables(path=SCH4, check_sha=True):
    raw = open(path, "rb").read()
    if check_sha and hashlib.sha256(raw).hexdigest() != SCH4_SHA:
        raise SystemExit("bridges: %s is not the pinned Schedule 4 text" % path)
    lines = [l.strip() for l in raw.decode("utf-8").split("\n")]
    tables, cur = {}, None
    for i, l in enumerate(lines):
        m = re.search(r"TABLE (\d)", l)
        if m and l.replace("[F9", "").replace("[F12", "").replace("]", "").strip().startswith("TABLE"):
            cur = int(m.group(1))
            tables[cur] = []
            continue
        if l.startswith("(") and re.fullmatch(r"\(\d+A?\)", l) and cur and tables[cur]:
            cur = None
        if cur is None or not l.startswith("|"):
            continue
        body = l.lstrip("| ").strip()
        m = re.fullmatch(r"(.+?) to (.+)", body)
        if m:
            try:
                tables[cur].append([parse_date(m.group(1)), parse_date(m.group(2)), None])
                continue
            except ValueError:
                pass
        if tables[cur] and tables[cur][-1][2] is None:
            m = re.fullmatch(r"66 years and (\d+) months?\]?", body)
            if m:
                tables[cur][-1][2] = ("age", 66, int(m.group(1)))
                continue
            try:
                tables[cur][-1][2] = ("day", parse_date(body))
            except ValueError:
                pass
    return tables


# the span each table must cover exactly, from the rules' own words (para. 1 rules (3), (5), (7), (9))
SPANS = {1: (D(1950, 4, 6), D(1953, 12, 5)), 2: (D(1953, 12, 6), D(1954, 10, 5)),
         3: (D(1960, 4, 6), D(1961, 3, 5)), 4: (D(1977, 4, 6), D(1978, 4, 5))}
RULE_7A = {D(1960, 7, 31): D(2026, 11, 30), D(1960, 12, 31): D(2027, 9, 30), D(1961, 1, 31): D(2027, 11, 30)}


def selfcheck(tables):
    errs = []
    for t, (lo, hi) in SPANS.items():
        rows = tables.get(t, [])
        if not rows:
            errs.append("table %d missing" % t)
            continue
        if rows[0][0] != lo or rows[-1][1] != hi:
            errs.append("table %d spans %s..%s, rule says %s..%s" % (t, rows[0][0], rows[-1][1], lo, hi))
        for a, b in zip(rows, rows[1:]):
            if b[0] != a[1] + dt.timedelta(days=1):
                errs.append("table %d gap or overlap between %s and %s" % (t, a[1], b[0]))
        for r in rows:
            if r[2] is None:
                errs.append("table %d row %s has no value" % (t, r[0]))
            elif (t == 3) != (r[2][0] == "age"):
                errs.append("table %d row %s has the wrong kind of value" % (t, r[0]))
        vals = [r[2][1] if r[2] and r[2][0] == "day" else (r[2][2] if r[2] else None) for r in rows]
        if None not in vals and any(x >= y for x, y in zip(vals, vals[1:])):
            errs.append("table %d values not strictly increasing" % t)
        if t == 3 and vals != list(range(1, 12)):
            errs.append("table 3 ages are not 66 years and 1 to 11 months in order")
    if not errs:
        for born, want in RULE_7A.items():
            got = pa_dates(born, tables)[0]
            if got != want:
                errs.append("rule (7A): born %s gives %s, the Act says %s" % (born, got, want))
    return errs


def pa_dates(born, tables, sex=None):
    """[pensionable-age date] (one, or two when it depends on an unstated sex: [female, male])."""
    def table(t):
        for lo, hi, v in tables[t]:
            if lo <= born <= hi:
                return v[1] if v[0] == "day" else anniversary(born, v[1], v[2])
        return None
    if born < D(1953, 12, 6):
        male = anniversary(born, 65)
        female = anniversary(born, 60) if born < D(1950, 4, 6) else table(1)
        return [female] if sex == "f" else [male] if sex == "m" else [female, male]
    if born <= D(1954, 10, 5):
        return [table(2)]
    if born < D(1960, 4, 6):
        return [anniversary(born, 66)]
    if born <= D(1961, 3, 5):
        return [table(3)]
    if born < D(1977, 4, 6):
        return [anniversary(born, 67)]
    if born <= D(1978, 4, 5):
        return [table(4)]
    return [anniversary(born, 68)]


def bridges_for(born, tables, sex=None, year=YEAR):
    q0, q1 = qualifying_week(year)
    pas = pa_dates(born, tables, sex)
    e80 = anniversary(born, 80)
    pa_by_week = sorted({p <= q1 for p in pas})
    return {"born": born.isoformat(), "pa_date": [p.isoformat() for p in pas],
            "pa_date_note": "depends on sex (female, male); not stated" if len(pas) == 2 else "",
            "reached_pa_by_week_end": pa_by_week[0] if len(pa_by_week) == 1 else "depends on sex",
            "eightieth": e80.isoformat(), "reached_80_by_week_end": e80 <= q1}


def week_bridges(year=YEAR):
    q0, q1 = qualifying_week(year)
    return {"qualifying_week": [q0.isoformat(), q1.isoformat()],
            "twelve_weeks_before_from": (q0 - dt.timedelta(days=84)).isoformat(),
            "fifty_two_weeks_before_from": (q0 - dt.timedelta(days=364)).isoformat(),
            "march_31_following": D(year + 1, 3, 31).isoformat(), "april_1_following": D(year + 1, 4, 1).isoformat()}


DATE_RX = re.compile(r"\b(\d{1,2}(?:st|nd|rd|th)? (?:%s),? \d{4}|(?:%s) \d{1,2},? \d{4}|\d{4}-\d{2}-\d{2})\b"
                     % ("|".join(m for m in calendar.month_name if m), "|".join(m for m in calendar.month_name if m)))
BORN_RX = re.compile(r"\b(?:born|date of birth(?: is|:)?|birthday is)\s+(?:on\s+)?$", re.I)


def births_in(facts):
    """Every date the text states right after 'born' / 'date of birth', in order (with 60 characters before it)."""
    out = []
    for m in DATE_RX.finditer(facts):
        before = facts[max(0, m.start() - 30):m.start()]
        if BORN_RX.search(before):
            out.append((m.group(1), facts[max(0, m.start() - 60):m.start()].strip()))
    return out


def main(argv):
    tables = load_tables()
    errs = selfcheck(tables)
    if errs:
        print("bridges: SELF-CHECK FAILED: " + "; ".join(errs), file=sys.stderr)
        return 1
    if argv[:1] == ["--selfcheck"]:
        print("bridges: tables 1-4 sound (%s rows), rule (7A) reproduced" % sum(len(v) for v in tables.values()))
        return 0
    if argv[:1] == ["--born"] and len(argv) >= 2:
        sex = argv[3] if len(argv) >= 4 and argv[2] == "--sex" else None
        print(json.dumps({**week_bridges(), **bridges_for(parse_date(argv[1]), tables, sex)}))
        return 0
    if argv[:1] == ["--questions"] and len(argv) == 2:
        print(json.dumps({"week": week_bridges(), "source_sha256": SCH4_SHA}))
        for line in open(argv[1], encoding="utf-8"):
            if not line.strip():
                continue
            q = json.loads(line)
            rows = []
            for text, ctx in births_in(q.get("facts", "")):
                rows.append({"stated": text, "context": ctx, **bridges_for(parse_date(text), tables)})
            print(json.dumps({"id": q["id"], "births": rows}, ensure_ascii=False))
        return 0
    print(__doc__.strip().split("usage:")[1], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
