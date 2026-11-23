"""The encoder's facts for one case (cases.py). SAME-FAMILY.

Conventions (stated, the same for every case; written before the encoder's question file was read):
C1 closed world over the FACTS / BINARY lists: a fact the case record does not list as true is stated false (unary facts for
   every item; period_for for every (period, leave) pair; precedes for every (period, break) pair); the encoder lists every
   true fact it reads in the question's facts;
C2 items: one leave item per leave start asked; one period item per stated period of employment (cut at the day before the
   leave's start; its stated number of weeks maintained on the payroll) or of USERRA-covered absence (its stated weeks); one
   break item per stated break in service; one block item per stated count of hours with its first and last day;
C3 integer constants only where the question states them (weeks, hours, the employee count on the day of the notice, the
   leave's start, a block's first and last day); the first day of the 12-month period, whole months of a period and of a
   break and a break's extra days come ONLY from bridge/bridges.jsonl (never typed by the encoder), and so do the weeks of a
   period whose number of weeks the question does not state (case field bridge_weeks; added after the questions were read:
   USERRA absences are given by their dates only);
C4 a stated judgment enters as the stated fact (translation.STATED), never decided by the encoder;
C5 "employee" and "covered" are the fixed facts of the test (every employer is a covered employer): true for every leave.
"""
from __future__ import annotations

import json
from pathlib import Path

import translation as T

HERE = Path(__file__).resolve().parent


def literal(name, value):
    base = name.split("_", 1)[0]
    unit = T.INT_UNITS[base][0]
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
            out[(r["case"], r["item"])] = r["values"]
    return out


def bridged_ints(case, ctx, br=None):
    """The bridged integer constants of a case: window -> wfrom_<leave>; period -> months, monthsup; break -> bmonths, bdays."""
    br = bridges() if br is None else br
    out = {}
    for x in ctx.items:
        v = br.get((case["id"], x))
        if v is None:
            continue
        if "wfrom" in v:
            out[f"wfrom_{x}"] = v["wfrom"]
        elif x in ctx.periods:
            out[f"months_{x}"], out[f"monthsup_{x}"] = v["months"], v["monthsup"]
            if x in case.get("bridge_weeks", ()):
                out[f"weeks_{x}"] = v["weeks"]
        elif x in ctx.breaks:
            out[f"bmonths_{x}"], out[f"bdays_{x}"] = v["months"], v["days"]
    return out


def ctx_of(case):
    return T.Ctx(case.get("leaves", ()), case.get("periods", ()), case.get("breaks", ()), case.get("blocks", ()))


def facts(case, br=None):
    ctx = ctx_of(case)
    out = []
    true = {x: set(v) for x, v in case.get("facts", {}).items()}
    for l in ctx.leaves:
        true.setdefault(l, set()).update(("employee", "covered"))  # C5
    for x in ctx.items:
        mine = true.get(x, set())
        bad = mine - set(T.FACTS)
        if bad:
            raise ValueError(f"{case['id']} {x}: unknown facts {sorted(bad)}")
        for p in T.FACTS:
            f = T.U(p, x)
            out.append({"id": f"{x}.{p}", "formula": f if p in mine else ["not", f]})
    pf = {tuple(x) for x in case.get("period_for", [(s, l) for s in ctx.periods for l in ctx.leaves])}
    pre = {tuple(x) for x in case.get("precedes", ())}
    for s in ctx.periods:
        for l in ctx.leaves:
            f = T.B("period_for", s, l)
            out.append({"id": f"period_for.{s}.{l}", "formula": f if (s, l) in pf else ["not", f]})
        for b in ctx.breaks:
            f = T.B("precedes", s, b)
            out.append({"id": f"precedes.{s}.{b}", "formula": f if (s, b) in pre else ["not", f]})
    ints = dict(case.get("ints", {}))
    typed = {n for n in ints if n.split("_", 1)[0] in T.BRIDGED_CONSTS}
    typed |= {f"weeks_{s}" for s in case.get("bridge_weeks", ()) if f"weeks_{s}" in ints}
    if typed:
        raise ValueError(f"{case['id']}: bridged constants typed by the encoder: {sorted(typed)}")
    ints.update(bridged_ints(case, ctx, br))
    for name, value in sorted(ints.items()):
        out.append({"id": name, "formula": literal(name, value)})
    return out
