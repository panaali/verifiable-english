"""The encoder's facts for one case (cases.py). SAME-FAMILY. Written with the translation, BEFORE questions-enc.jsonl was
opened; cases.py (the per-case records) after.

Conventions (stated, the same for every case):
C1 closed world over translation.V_FACTS / A_FACTS: a fact the case record does not list as true is stated false; the
   encoder lists every true fact it reads in the question's facts;
C2 constants only where the question gives them: the first registration date, the applicable CO2 emissions figure (Part 1A
   out: stated; never typed when the certificate specifies no figure: then 1GA(1C) decides it or nothing does), the list
   price or the notional price, each accessory's list or notional price, each licence's date; the whole years and days from
   the first registration to a licence's date come only from bridge/bridges.jsonl (never typed by the encoder);
C3 "propelled by diesel" and the standard the certificate indicates are copied as stated (fixed facts of the test); a
   certificate indicating Euro 6d-TEMP is not one indicating Euro 6d (ind6d false, ind6dtemp true), as the text's own
   parenthesis in 1GC(5) says;
C4 an accessory the facts name as non-standard and attached when the vehicle was first registered under the Act is listed
   with those facts; an accessory fitted later, or standard, is listed with them false (it then counts GBP 0);
C5 a licence the facts call the first vehicle licence is asked as Q1 (rate1); any other licence is an item of its own with
   its date (Q2 rate2, Q3 ge2).
"""
from __future__ import annotations

import json
from pathlib import Path

import translation as T

HERE = Path(__file__).resolve().parent


def literal(name, value):
    base = name.rsplit("_", 1)[0]
    unit = T.ALL_UNITS[base][0]
    term = ["const", unit, name]
    if unit == T.DAY:
        return ["eq", term, ["date", value]]
    return ["eq", term, ["decimal", unit, str(value)]]


def bridges():
    p = HERE / "bridge" / "bridges.jsonl"
    if not p.exists():
        return {}
    out = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[(r["case"], r["licence"])] = (r["years"], r["days"])
    return out


def ctx_of(case):
    return T.Ctx([{"id": v["id"], "accessories": [a["id"] for a in v.get("accessories", ())],
                   "licences": [l["id"] for l in v.get("licences", ())]} for v in case["vehicles"]])


def _unary(out, item, mine, table):
    bad = set(mine) - set(table)
    if bad:
        raise ValueError(f"{item}: unknown facts {sorted(bad)}")
    for p in table:
        f = T.U(p, item)
        out.append({"id": f"{item}.{p}", "formula": f if p in mine else ["not", f]})


def facts(case):
    out = []
    br = bridges()
    for v in case["vehicles"]:
        x = v["id"]
        _unary(out, x, v.get("facts", ()), T.V_FACTS)
        for base, value in sorted(v.get("ints", {}).items()):
            if base not in T.V_UNITS or base in T.ASKED_BASES:
                raise ValueError(f"{case['id']}: {base} is not a stated vehicle constant")
            out.append({"id": f"{base}_{x}", "formula": literal(f"{base}_{x}", value)})
        for a in v.get("accessories", ()):
            _unary(out, a["id"], a.get("facts", ()), T.A_FACTS)
            for base, value in sorted(a.get("ints", {}).items()):
                if base not in ("alp", "anp"):
                    raise ValueError(f"{case['id']}: {base} is not a stated accessory constant")
                out.append({"id": f"{base}_{a['id']}", "formula": literal(f"{base}_{a['id']}", value)})
        for l in v.get("licences", ()):
            out.append({"id": f"dlic_{l['id']}", "formula": literal(f"dlic_{l['id']}", l["date"])})
            b = br.get((case["id"], l["id"]))
            if b is not None:
                out.append({"id": f"ly_{l['id']}", "formula": literal(f"ly_{l['id']}", b[0])})
                out.append({"id": f"ld_{l['id']}", "formula": literal(f"ld_{l['id']}", b[1])})
    return out
