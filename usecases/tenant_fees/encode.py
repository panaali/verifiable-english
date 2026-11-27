"""The encoder's facts for one case (cases.py). SAME-FAMILY.

Conventions (stated, the same for every case):
C1 closed world over the FACTS list: a unary fact the case record does not list as true is stated false for every item
   (the encoder lists every true fact it reads in the question's facts);
C2 the binary links (alternative_to, earlier_same, imposed_for) are exactly those the case lists (rules quantify over them);
C3 integer constants (amounts, days, the annual rent) are stated only where the question gives them; the late-rent cap
   intcap_<x> comes only from bridge/bridges.jsonl (never typed by the encoder);
C4 a stated judgment enters as the stated fact (translation.STATED), never decided by the encoder.
"""
from __future__ import annotations

import json
from pathlib import Path

import translation as T

HERE = Path(__file__).resolve().parent


def literal(name, value):
    unit = T.CASE_INTS[name][0] if name in T.CASE_INTS else T.INT_UNITS[name.split("_", 1)[0]][0]
    term = ["const", unit, name]
    return ["eq", term, ["decimal", T.GBP, value] if unit == T.GBP else ["date", value]]


def bridges():
    p = HERE / "bridge" / "bridges.jsonl"
    if not p.exists():
        return {}
    out = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[(r["case"], r["item"])] = r["intcap"]
    return out


def facts(case):
    out = []
    true = case.get("facts", {})
    for x in case["items"]:
        mine = set(true.get(x, ()))
        bad = mine - set(T.FACTS)
        if bad:
            raise ValueError(f"{case['id']} {x}: unknown facts {sorted(bad)}")
        for p in T.FACTS:
            f = T.U(p, x)
            out.append({"id": f"{x}.{p}", "formula": f if p in mine else ["not", f]})
    for (p, a, b) in case.get("links", ()):
        out.append({"id": f"{p}.{a}.{b}", "formula": T.B(p, a, b)})
    for name, value in sorted(case.get("ints", {}).items()):
        if name.startswith("intcap_"):
            raise ValueError("intcap comes from the bridge only")
        out.append({"id": name, "formula": literal(name, value)})
    br = bridges()
    for x in case["items"]:
        if (case["id"], x) in br:
            out.append({"id": f"intcap_{x}", "formula": literal(f"intcap_{x}", br[(case["id"], x)])})
    return out
