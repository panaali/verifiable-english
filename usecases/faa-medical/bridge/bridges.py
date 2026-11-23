#!/usr/bin/env python3
"""14 CFR 61.23 (statute corpus law 4, SAME-FAMILY) bridges: the date facts the language does not compute, from the dates a
question states (ISOLATION.md D5: never computed by the encoder). Pure Python, no VE import. Tests: test_bridges.py.

Conventions (the writer's prompt states each as a fixed fact of the test; ISOLATION.md D4):
  age on a day                 completed years on that day; an age is reached on the anniversary of birth (no 29 February
                               birth or examination dates in the set: refused here)
  under age 40 on the exam     age on the date of examination < 40  ((d) table, "on the date of examination ... you were")
  60th birthday                the anniversary of birth in the 60th year ((a)(1)(iii), (d)(1)(ii))
  end of the Nth month after   "at the end of the last day of the Nth month after the month of the date of examination":
                               the last calendar day of the month (exam month + N), N in 6, 12, 24, 60 ((d))
  24 / 48 calendar months      "during the 24/48 calendar months before" a flight counts from the first day of the calendar
  before                       month 24/48 months before the flight's month: the last flight day a course (exam) supports
                               is the last day of the month (course month + 24) / (exam month + 48)
  after July 14, 2006          the date of examination is after 2006-07-14 ((c)(3)(i)(B))
  later                        one stated date strictly after another (which certificate / application is most recent)

Input: one JSON object per line (the encoder's transcription of the stated dates of one case, cases.py `dates()`):
  {"id": "F001", "facts": "<the question's facts text>", "birth": "1971-03-14" or null, "flight_day": "2025-05-03",
   "certs": {"cert1": "2024-10-09", ...}, "apps": {"app1": "2024-10-01", ...},
   "course_day": "2026-05-04" or null, "basic_exam_day": "2025-06-02" or null}
Every date given must appear in the facts text (as "14 March 1971", "March 14, 1971" or "1971-03-14"): a transcription
the facts do not state is refused (exit 3), so the encoder cannot add a date.

usage: python3 -I bridges.py --cases dates.jsonl > bridges.jsonl
       python3 -I bridges.py --born 1971-03-14 --exam 2024-10-09 --day 2025-05-03
"""
import calendar
import datetime as dt
import json
import re
import sys

D = dt.date
NS = (6, 12, 24, 60)


def iso(s):
    d = D.fromisoformat(s)
    if (d.month, d.day) == (2, 29):
        raise ValueError(f"29 February date refused: {s}")
    return d


def age_on(birth, day):
    return day.year - birth.year - ((day.month, day.day) < (birth.month, birth.day))


def anniversary(birth, years):
    return birth.replace(year=birth.year + years)


def end_of_nth_month_after(d, n):
    m = d.month - 1 + n
    y, m = d.year + m // 12, m % 12 + 1
    return D(y, m, calendar.monthrange(y, m)[1])


def spelled(d):
    """The ways a stated date may be written in the facts."""
    month = calendar.month_name[d.month]
    return (f"{d.day} {month} {d.year}", f"{month} {d.day}, {d.year}", d.isoformat(), f"{month} {d.day} {d.year}")


def stated(facts, d):
    return any(re.search(r"(?<![0-9])" + re.escape(s) + r"(?![0-9])", facts) for s in spelled(d))


def bridge_case(case):
    facts = case.get("facts", "")
    fd = iso(case["flight_day"])
    given = [("flight_day", fd)]
    out = {"id": case["id"], "flight_day": fd.isoformat(), "certs": {}, "apps": {}}
    birth = iso(case["birth"]) if case.get("birth") else None
    if birth:
        given.append(("birth", birth))
        out["birth"] = birth.isoformat()
        out["sixtieth"] = anniversary(birth, 60).isoformat()
        out["age_on_flight_day"] = age_on(birth, fd)
    for k, s in sorted(case.get("certs", {}).items()):
        e = iso(s)
        given.append((k, e))
        rec = {"exam": e.isoformat(), "after_2006": e > D(2006, 7, 14), "held_by_d": e <= fd}
        for n in NS:
            rec[f"end{n}"] = end_of_nth_month_after(e, n).isoformat()
        if birth:
            rec["age_at_exam"] = age_on(birth, e)
            rec["under40_exam"] = rec["age_at_exam"] < 40
        out["certs"][k] = rec
    for k, s in sorted(case.get("apps", {}).items()):
        a = iso(s)
        given.append((k, a))
        out["apps"][k] = {"day": a.isoformat()}
    for name, coll in (("later", out["certs"]), ("app_later", out["apps"])):
        key = "exam" if name == "later" else "day"
        out[name] = sorted([a, b] for a in coll for b in coll if a != b and coll[a][key] > coll[b][key])
    if case.get("course_day"):
        cd = iso(case["course_day"])
        given.append(("course_day", cd))
        out["course_day"] = cd.isoformat()
        out["course_end24"] = end_of_nth_month_after(cd, 24).isoformat()
    if case.get("basic_exam_day"):
        bd = iso(case["basic_exam_day"])
        given.append(("basic_exam_day", bd))
        out["basic_exam_day"] = bd.isoformat()
        out["basic_exam_end48"] = end_of_nth_month_after(bd, 48).isoformat()
    missing = [f"{n}={d.isoformat()}" for n, d in given if not stated(facts, d)]
    if missing:
        raise LookupError(f"{case['id']}: dates not stated in the facts: {', '.join(missing)}")
    return out


def main(argv):
    if argv[:1] == ["--cases"] and len(argv) == 2:
        try:
            for line in open(argv[1], encoding="utf-8"):
                if line.strip():
                    print(json.dumps(bridge_case(json.loads(line)), sort_keys=True))
        except (LookupError, ValueError) as e:
            print(f"bridges: REFUSED: {e}", file=sys.stderr)
            return 3
        return 0
    if argv[:1] == ["--born"]:
        a = dict(zip(argv[0::2], argv[1::2]))
        b, e, d = iso(a["--born"]), iso(a["--exam"]), iso(a["--day"])
        print(json.dumps({"age_at_exam": age_on(b, e), "sixtieth": anniversary(b, 60).isoformat(),
                          **{f"end{n}": end_of_nth_month_after(e, n).isoformat() for n in NS},
                          "valid_on_day": {n: d <= end_of_nth_month_after(e, n) for n in NS}}))
        return 0
    print(__doc__.strip().splitlines()[-2], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
