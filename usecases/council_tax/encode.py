"""The encoder's facts for one case (cases.py). SAME-FAMILY.

Conventions (stated, the same for every case):
C1 closed world over the FACTS / BINARY lists: a fact the case record does not list as true is stated false (unary facts
   for every item; binary facts for every (person, day) pair and every (day, year) pair of the case); the encoder lists
   every true fact it reads in the question's facts;
C2 the persons of a case are the people its facts name for the days asked (the closed world of s. 11's "only one",
   "each of them except one", "no resident" is over them; the writer's fixed fact: the named residents and nobody else);
C3 integer constants (value, the day's date, A for the listed band, A for band D, D, certificate dates) only where the
   question gives them; "age18" comes only from bridge/bridges.jsonl (never typed by the encoder);
C4 a stated judgment enters as the stated fact (translation.STATED), never decided by the encoder.
C5 open facts (translation.OPEN) are never closed by C1: a record states one true by listing it in "pd" / "facts",
   or by a case-level key: "sch1_closed": True states it for every (person, day) pair of the case (the facts say no
   other Sch. 1 paragraph and no order applies to anyone), "adj_none": True for every day item (the facts say no
   premium or reduction applies and nothing changes any amount); or true / false in "open" ({"<person>@<day>" or
   "<item>": {fact: True | False}}); otherwise it is unknown and a rule that needs it refuses.
"""
from __future__ import annotations

import json
from pathlib import Path

import translation as T

HERE = Path(__file__).resolve().parent


def literal(name, value):
    unit = T.INT_UNITS[name.split("_", 1)[0]][0]
    term = ["const", unit, name]
    if unit == T.DAY:
        return ["eq", term, ["date", value]]
    return ["eq", term, ["decimal", unit, value]]


def bridges():
    p = HERE / "bridge" / "bridges.jsonl"
    if not p.exists():
        return {}
    out = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[(r["case"], r["person"], r["day"])] = r["attained18"]
    return out


def ctx_of(case):
    return T.Ctx(case.get("dwelling"), case.get("values", ()), case.get("days", ()), case.get("persons", ()),
                 case.get("years", ()), [("in_year", d, y) for (d, y) in case.get("in_year", ())])


def facts(case):
    ctx = ctx_of(case)
    out = []
    true = case.get("facts", {})
    for x in ctx.items:
        mine = set(true.get(x, ()))
        bad = mine - set(T.FACTS)
        if bad:
            raise ValueError(f"{case['id']} {x}: unknown facts {sorted(bad)}")
        for p in T.FACTS:
            f = T.U(p, x)
            if p in T.OPEN:
                v = True if (p in mine or (p == "adj_none" and case.get("adj_none") and x in ctx.days)) else \
                    case.get("open", {}).get(x, {}).get(p)
                if v is None:
                    continue  # C5: not stated, unknown
                out.append({"id": f"{x}.{p}", "formula": f if v else ["not", f]})
                continue
            out.append({"id": f"{x}.{p}", "formula": f if p in mine else ["not", f]})
    pd = case.get("pd", {})
    opened = case.get("open", {})
    for key_, vals in opened.items():
        bad = set(vals) - set(T.OPEN)
        if bad:
            raise ValueError(f"{case['id']} {key_}: not open facts {sorted(bad)}")
    br = bridges()
    for (p, d) in ctx.pd():
        mine = set(pd.get(f"{p}@{d}", ()))
        bad = mine - (set(T.BINARY) - set(T.DAY_YEAR))
        if bad:
            raise ValueError(f"{case['id']} {p}@{d}: unknown or bridged facts {sorted(bad)}")
        for b in T.BINARY:
            if b in T.DAY_YEAR:
                continue
            if b in T.OPEN:
                v = True if (b in mine or (b == "sch1_closed" and case.get("sch1_closed"))) else \
                    opened.get(f"{p}@{d}", {}).get(b)
                if v is None:
                    continue  # C5: not stated, unknown
                truth = v
            elif b in T.BRIDGED:
                v = br.get((case["id"], p, d))
                if v is None:
                    continue  # no bridge row: the fact is not stated (para. 3 cannot be decided for this pair)
                truth = v
            else:
                truth = b in mine
            f = T.B(b, p, d)
            out.append({"id": f"{b}.{p}.{d}", "formula": f if truth else ["not", f]})
    linked = {tuple(x) for x in case.get("in_year", ())}
    for d in ctx.days:
        for y in ctx.years:
            f = T.B("in_year", d, y)
            out.append({"id": f"in_year.{d}.{y}", "formula": f if (d, y) in linked else ["not", f]})
    for name, value in sorted(case.get("ints", {}).items()):
        out.append({"id": name, "formula": literal(name, value)})
    return out
