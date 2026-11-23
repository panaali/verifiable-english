"""The encoder's facts for one period record (cases.py). SAME-FAMILY.

Conventions (stated, the same for every case):
C1 closed world over the FACTS list: a unary fact the record does not list as true is stated false for every item, except
   the facts the record lists under "unknown" (stated neither way: the question gives no fact that settles them without
   arithmetic);
C2 the binary links (run_of) are exactly those the record lists (rules quantify over them);
C3 integer constants (amounts, days, day counts) are stated only where the question gives them; the age and the 12-month
   facts come only from bridge/bridges.jsonl (never typed by the encoder);
C4 the worker is the item "w"; the pay reference period's first and last day are the question's; the following period's
   first and last day are read from the stated pay pattern and the calendar (C5);
C5 calendar membership (which calendar month or week a stated day falls in) is read by the encoder from the stated dates
   and pay pattern (reg. 9(2)(d) rec_paid_window; the following period's bounds): a calendar reading, listed per case.
"""
from __future__ import annotations

import json
from pathlib import Path

import translation as T

HERE = Path(__file__).resolve().parent
BRIDGED = ("within12_cur", "within12_prior")


def literal(name, value):
    unit = T.CASE_INTS[name][0] if name in T.CASE_INTS else T.INT_UNITS[name.split("_", 1)[0]][0]
    term = ["const", unit, name]
    if unit == T.GBP:
        return ["eq", term, ["decimal", T.GBP, value]]
    if unit == T.DAY:
        return ["eq", term, ["date", value]]
    return ["eq", term, ["decimal", unit, str(value)]]


def bridges():
    p = HERE / "bridge" / "bridges.jsonl"
    if not p.exists():
        return {}
    return {r["case"]: r for r in (json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip())}


def facts(case):
    out = []
    true = case.get("facts", {})
    unknown = case.get("unknown", {})
    br = bridges().get(case["id"])
    if br is None:
        raise ValueError(f"{case['id']}: no bridge row")
    true = {x: list(v) for x, v in true.items()}
    for b in BRIDGED:
        if any(b in v for v in true.values()):
            raise ValueError(f"{case['id']}: {b} comes from the bridge only")
        if br.get(b):
            true.setdefault("w", []).append(b)
    for x in case["items"]:
        mine = set(true.get(x, ()))
        bad = (mine | set(unknown.get(x, ()))) - set(T.FACTS)
        if bad:
            raise ValueError(f"{case['id']} {x}: unknown facts {sorted(bad)}")
        for p in T.FACTS:
            if p in unknown.get(x, ()):
                continue
            f = T.U(p, x)
            out.append({"id": f"{x}.{p}", "formula": f if p in mine else ["not", f]})
    for (p, a, b) in case.get("links", ()):
        out.append({"id": f"{p}.{a}.{b}", "formula": T.B(p, a, b)})
    for name, value in sorted(case.get("ints", {}).items()):
        if name == "age":
            raise ValueError("age comes from the bridge only")
        out.append({"id": name, "formula": literal(name, value)})
    out.append({"id": "age", "formula": literal("age", br["age"])})
    return out
