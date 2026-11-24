"""The encoder's facts for one case (cases.py). SAME-FAMILY.

Conventions (stated, the same for every case; written before the encoder's question file was read):
C1 closed world over the FACTS list: a fact the case record does not list as true is stated false, for every item, except
   the facts the case record lists as "unknown" for an item (the question leaves them open: neither polarity is stated);
C2 items: one conviction item per occasion of conviction asked about; one offence item per offence of which the person is
   convicted on that occasion; one previous-disqualification item per stated earlier disqualification of that person; one
   circumstance item per stated circumstance put to the court (or asked about in Q4);
C3 integer constants only where the question states them (the conviction's date, the points to be taken into account, the
   latest offence's date, a disqualification's date and its period as ordered, an extension period, an earlier occasion's
   date); the whole months and days between two dates come ONLY from bridge/bridges.jsonl (never typed by the encoder);
C4 a stated judgment enters as the stated fact (translation.STATED), never decided by the encoder;
C5 every case is a conviction in a court in England and Wales (the fixed fact of the test; (6) out).
"""
from __future__ import annotations

import json
from pathlib import Path

import translation as T

HERE = Path(__file__).resolve().parent


def literal(name, value):
    base = name.split("_", 1)[0]
    unit = (T.INT_UNITS.get(base) or T.PAIR_UNITS[base])[0]
    term = ["const", unit, name]
    if unit == T.DAY:
        return ["eq", term, ["date", value]]
    return ["eq", term, ["decimal", unit, str(value)]]


def bridge_inputs(case):
    """The date pairs the bridge turns into months and days (copied from the case's stated dates)."""
    ints, out = case.get("ints", {}), []
    for p, v in case.get("prevs", {}).items():
        a, e = ints.get(f"imp_{p}"), ints.get(f"lo_{v}")
        if a and e:
            out.append({"case": case["id"], "item": p, "conv": v, "kind": "pair", "from": a, "to": e})
    for x, v in case.get("circs", {}).items():
        a, e = ints.get(f"occ_{x}"), ints.get(f"conv_{v}")
        if a and e:
            out.append({"case": case["id"], "item": x, "conv": v, "kind": "pair", "from": a, "to": e})
    return out


def bridges():
    p = HERE / "bridge" / "bridges.jsonl"
    if not p.exists():
        return {}
    out = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[(r["case"], r["item"], r["conv"])] = r["values"]
    return out


def bridged_ints(case, ctx, br=None):
    br = bridges() if br is None else br
    out = {}
    for p, v in ctx.prevs.items():
        vals = br.get((case["id"], p, v)) or {}
        if vals:
            out[f"wm_{p}_{v}"], out[f"wd_{p}_{v}"] = vals["months"], vals["days"]
    for x, v in ctx.circs.items():
        vals = br.get((case["id"], x, v)) or {}
        if vals:
            out[f"cm_{x}_{v}"], out[f"cd_{x}_{v}"] = vals["months"], vals["days"]
    return out


def ctx_of(case):
    return T.Ctx(case.get("convictions", ()), case.get("offences", {}), case.get("prevs", {}), case.get("circs", {}),
                 case.get("tot_stated", ()))


def facts(case, br=None):
    ctx = ctx_of(case)
    out = []
    true = {x: set(v) for x, v in case.get("facts", {}).items()}
    unknown = {x: set(v) for x, v in case.get("unknown", {}).items()}
    for x in set(true) | set(unknown):
        if x not in ctx.items:
            raise ValueError(f"{case['id']}: facts for an unknown item {x}")
    for x in ctx.items:
        mine, open_ = true.get(x, set()), unknown.get(x, set())
        bad = (mine | open_) - set(T.FACTS)
        if bad:
            raise ValueError(f"{case['id']} {x}: unknown fact names {sorted(bad)}")
        for p in T.FACTS:
            if p in open_:
                continue
            f = T.U(p, x)
            out.append({"id": f"{x}.{p}", "formula": f if p in mine else ["not", f]})
    ints = dict(case.get("ints", {}))
    typed = {n for n in ints if n.split("_", 1)[0] in T.BRIDGED_PAIRS}
    if typed:
        raise ValueError(f"{case['id']}: bridged constants typed by the encoder: {sorted(typed)}")
    known = set(T.int_constants(ctx))
    stray = set(ints) - known
    if stray:
        raise ValueError(f"{case['id']}: constants not in the case's environment: {sorted(stray)}")
    ints.update(bridged_ints(case, ctx, br))
    for name, value in sorted(ints.items()):
        out.append({"id": name, "formula": literal(name, value)})
    return out
