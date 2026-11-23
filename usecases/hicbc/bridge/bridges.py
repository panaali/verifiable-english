"""HICBC bridge script: the calendar of 681H(3) and the arithmetic of 681C(2)-(3). Never the encoder's; tested (test_bridges.py).

Input: one case record of cases.py (the encoder's transcription of the stated dates and amounts; every date it uses must
occur verbatim in the question's facts, checked by check_quotes). Output (case_bridge):
- weeks: the Mondays of the tax year (a week is in the tax year iff its Monday is; 681H(3)); tax year YYYY-YY = 6 April YYYY
  to 5 April YYYY+1 (a fixed fact of the test, ITA 2007 s.4, not in the pin).
- segments: the year's weeks grouped by the vector of every stated fact on that week (child benefit records active and their
  election flag, child-lives-with records active, the set of day-types of each week, the 681D(4) facts of each record); a
  segment's weeks are alike in every stated fact.
- items: one per (segment, child benefit record active in it): claimant, child, basis, weeks, total in pence (weeks x weekly
  amount), election flag, the 681D(4) facts, the persons with the child living with them.
- daytypes: each distinct combination of the stated relationship facts over all pairs that holds on some day of some week of
  the year, and the items whose weeks contain it.
- pct: per person with a stated ANI, the appropriate percentage min(100, floor((ANI - 60000) / 200)) (0 when ANI <= 60000).
- charge_table(subject): for every subset of the case's items, total = floor(sum of the subset's totals to whole pounds),
  charge = floor(total x pct / 100) in whole pounds (681C(1), (3)(a); the total is rounded down before the percentage is
  applied, and the charge after).
Conventions: a child benefit or child-lives-with period [from, to] covers the weeks whose Monday lies in it (both stated as
weeks or Mondays in this set); a relationship fact [from, to] holds on every day from `from` to `to` inclusive (to = None:
still holds).
"""
from __future__ import annotations

import datetime as dt
import itertools
import json
import re
import sys
from decimal import Decimal

D = dt.date
ONE_WEEK = dt.timedelta(days=7)
KINDS = ("married_or_cp", "sep_court", "sep_permanent", "as_if_married")
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
          "December"]


def iso(s):
    return None if s is None else D.fromisoformat(s)


def tax_year(ty):
    m = re.fullmatch(r"(\d{4})-(\d{2})", ty)
    y = int(m.group(1))
    if (y + 1) % 100 != int(m.group(2)):
        raise ValueError(f"bad tax year {ty}")
    return D(y, 4, 6), D(y + 1, 4, 5)


def mondays(start, end):
    d = start + dt.timedelta(days=(7 - start.weekday()) % 7)
    out = []
    while d <= end:
        out.append(d)
        d += ONE_WEEK
    return out


def covers_week(rec, monday):
    """A weekly record (child benefit, lives-with) covers the week whose Monday lies in [from, to]."""
    f, t = iso(rec["from"]), iso(rec.get("to"))
    return (f is None or f <= monday) and (t is None or monday <= t)


def holds_on(rec, day):
    f, t = iso(rec.get("from")), iso(rec.get("to"))
    return (f is None or f <= day) and (t is None or day <= t)


def pair_key(a, b):
    return tuple(sorted((a, b)))


def day_vector(case, day):
    """The relationship facts of every pair of named persons on one day: ((pair, (k1..k4)), ...)."""
    out = []
    for a, b in itertools.combinations(sorted(case["people"]), 2):
        flags = tuple(any(r["kind"] == k and pair_key(*r["pair"]) == (a, b) and holds_on(r, day) for r in case["rel"])
                      for k in KINDS)
        out.append(((a, b), flags))
    return tuple(out)


def b_run(case, rec, monday):
    """681D(4): the contiguous run of weeks, containing `monday`, for which the claimant is entitled for the child by virtue of
    s.143(1)(b); returns (length in weeks or None when unbounded, first Monday, last Monday)."""
    def b_on(m):
        return any(r["claimant"] == rec["claimant"] and r["child"] == rec["child"] and r["basis"] == "b" and covers_week(r, m)
                   for r in case["cb"])
    if not b_on(monday):
        return None
    first, n = monday, 1
    while b_on(first - ONE_WEEK):
        first -= ONE_WEEK
        n += 1
        if n > 600:
            return (None, None, None)
    last = monday
    while b_on(last + ONE_WEEK):
        last += ONE_WEEK
        n += 1
        if n > 600:
            return (None, first, None)
    return (n, first, last)


def a_on(case, rec, monday):
    return any(r["claimant"] == rec["claimant"] and r["child"] == rec["child"] and r["basis"] == "a" and covers_week(r, monday)
               for r in case["cb"])


def d4_facts(case, rec, monday):
    if rec["basis"] != "b":
        return (False, False, False)
    run = b_run(case, rec, monday)
    n, first, last = run
    short = n is not None and n <= 52
    before = first is not None and a_on(case, rec, first - ONE_WEEK)
    after = last is not None and a_on(case, rec, last + ONE_WEEK)
    return (short, before, after)


def election_on(rec, monday):
    e = rec.get("election")
    if e is None:
        return False
    if e == "all":
        return True
    return covers_week({"from": e[0], "to": e[1]}, monday)


def lives(case, rec, monday):
    """Persons who have the child living with them in the week (s.143(1)(a) purposes): stated lives-with records, and the
    claimant of an (a)-basis record (entitled 'because the child lives with' them)."""
    out = {r["person"] for r in case.get("lives", []) if r["child"] == rec["child"] and covers_week(r, monday)}
    out |= {r["claimant"] for r in case["cb"] if r["child"] == rec["child"] and r["basis"] == "a" and covers_week(r, monday)}
    return tuple(sorted(out))


def pence(s):
    v = Decimal(s) * 100
    if v != v.to_integral_value():
        raise ValueError(f"not whole pence: {s}")
    return int(v)


def pct(ani):
    """681C(2), (3)(b): min(100, floor((ANI - 60000) / 200)); 0 when ANI does not exceed 60000."""
    p = pence(ani) - 6_000_000
    if p <= 0:
        return 0
    return min(100, p // 20_000)


def case_bridge(case):
    start, end = tax_year(case["tax_year"])
    weeks = mondays(start, end)
    recs = case["cb"]
    week_info, dtypes = [], {}
    for m in weeks:
        dvs = []
        for k in range(7):
            vec = day_vector(case, m + dt.timedelta(days=k))
            if vec not in dtypes:
                dtypes[vec] = "d" + str(len(dtypes) + 1)
            dvs.append(dtypes[vec])
        active = tuple((j, election_on(r, m), d4_facts(case, r, m), lives(case, r, m))
                       for j, r in enumerate(recs) if covers_week(r, m))
        week_info.append((m, (active, tuple(sorted(set(dvs))))))
    segs = {}
    for m, k in week_info:
        segs.setdefault(k, []).append(m)
    segments = sorted(segs.items(), key=lambda kv: kv[1][0])
    items, seg_out = [], []
    for s_no, ((active, dts), ms) in enumerate(segments, 1):
        seg_out.append({"segment": s_no, "weeks": len(ms), "first": ms[0].isoformat(), "last": ms[-1].isoformat(),
                        "daytypes": list(dts)})
        for j, elect, d4, lw in active:
            r = recs[j]
            items.append({"item": f"i{len(items) + 1}", "segment": s_no, "record": j, "claimant": r["claimant"],
                          "child": r["child"], "basis": r["basis"], "weeks": len(ms), "weekly": r["weekly"],
                          "total_pence": len(ms) * pence(r["weekly"]), "election_13a": elect,
                          "d4_short": d4[0], "d4_a_before": d4[1], "d4_a_after": d4[2], "lives_with": list(lw),
                          "daytypes": list(dts)})
    dt_out = {name: {"pairs": {f"{a}|{b}": dict(zip(KINDS, flags)) for (a, b), flags in vec}}
              for vec, name in dtypes.items()}
    return {"id": case["id"], "tax_year": case["tax_year"], "year": [start.isoformat(), end.isoformat()],
            "weeks_in_year": len(weeks), "segments": seg_out, "items": items, "daytypes": dt_out,
            "pct": {p: pct(a) for p, a in sorted(case["ani"].items())}}


def charge_table(bridge, subject):
    items = [i["item"] for i in bridge["items"]]
    p = bridge["pct"][subject]
    tot = {i["item"]: i["total_pence"] for i in bridge["items"]}
    out = []
    for n in range(len(items) + 1):
        for sub in itertools.combinations(items, n):
            pounds = sum(tot[x] for x in sub) // 100
            out.append({"counted": list(sub), "total": pounds, "pct": p, "charge": f"{pounds * p // 100}.00"})
    return out


def long_date(s):
    d = D.fromisoformat(s)
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def check_quotes(case, facts):
    """Every date the transcription uses (except the tax year's own bounds) occurs verbatim in the question's facts."""
    missing = []
    dates = [x for r in case["cb"] for x in (r["from"], r.get("to"))]
    dates += [x for r in case["cb"] if isinstance(r.get("election"), list) for x in r["election"]]
    dates += [x for r in case.get("lives", []) for x in (r["from"], r.get("to"))]
    dates += [x for r in case["rel"] for x in (r.get("from"), r.get("to"))]
    for s in dates:
        if s is None or s in case.get("unstated_dates_ok", []):
            continue
        if long_date(s) not in facts:
            missing.append(s)
    return missing


def main(argv):
    """python3 -I bridge/bridges.py <questions-enc.jsonl>  -> bridges.jsonl on stdout (cases from ../cases.py)."""
    import importlib.util
    from pathlib import Path
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("cases", here.parent / "cases.py")
    K = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(K)
    facts = {json.loads(l)["id"]: json.loads(l)["facts"] for l in open(argv[0], encoding="utf-8") if l.strip()}
    bad = 0
    for case in K.CASES:
        miss = check_quotes(case, facts[case["id"]])
        if miss:
            bad += 1
            print(f"{case['id']}: dates not in the facts: {miss}", file=sys.stderr)
        b = case_bridge(case)
        b["charge_table"] = charge_table(b, case["subject"]) if case["subject"] in case["ani"] else []
        print(json.dumps(b, sort_keys=True))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
