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
            out.append({"id": f"{x}.{p}", "formula": f if p in mine else ["not", f]})
    pd = case.get("pd", {})
    br = bridges()
    for (p, d) in ctx.pd():
        mine = set(pd.get(f"{p}@{d}", ()))
        bad = mine - (set(T.BINARY) - set(T.DAY_YEAR))
        if bad:
            raise ValueError(f"{case['id']} {p}@{d}: unknown or bridged facts {sorted(bad)}")
        for b in T.BINARY:
            if b in T.DAY_YEAR:
                continue
            if b in T.BRIDGED:
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
