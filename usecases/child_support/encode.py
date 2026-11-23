"""The encoder's facts for one case (cases.py). SAME-FAMILY.

Conventions (stated, the same for every case; fixed before the encoder's questions were read):
C1 closed world over the FACTS / BINARY lists: a fact the case record does not list as true is stated false (unary facts
   for every item; binary facts for every pair of the kinds the fact relates); the encoder lists every true fact it
   reads in the question's facts;
C2 the items of a case are the non-resident parent x, the children, the other persons and the benefits its facts name
   (the counts of para. 2, 5A, 6 and 7(5) are over the named children: the writer's fixed fact names every qualifying
   child and every other child of the household);
C3 integer constants (gross weekly income, the stated reduced rate, the prescribed flat rate of 4(2), the nights of
   shared care) only where the question gives them; the nights of a qualifying child with no shared care are 0 (the
   writer's fixed fact: "0 when there is no shared care");
C4 a stated judgment enters as the stated fact (translation.STATED), never decided by the encoder;
C5 "receives <benefit> for the week" enters as "paid in respect of the week" (10C(3): paid or due to be paid; either
   gives the same answer);
C6 binary facts between persons are written with the non-resident parent first.
"""
from __future__ import annotations

import translation as T

PAIR_KINDS = {  # binary fact -> (first kind, second kind)
    "pwc": ("children", "persons"),
    "cbpaid": ("people", "children"), "cbdue": ("people", "children"),
    "paid": ("people", "benefits"), "due": ("people", "benefits"),
    **{b: ("parent", "persons") for b in ("married", "civil", "samehh", "livetog", "polyg", "oppsex")},
}


def literal(name, value):
    unit = T.INT_UNITS[name.split("_", 1)[0]][0]
    return ["eq", ["const", unit, name], ["decimal", unit, value]]


def ctx_of(case):
    return T.Ctx(case["parent"], case.get("children", ()), case.get("persons", ()), case.get("benefits", ()))


def kind(ctx, name):
    return {"parent": [ctx.x], "children": ctx.children, "persons": ctx.persons, "benefits": ctx.benefits,
            "people": ctx.people}[name]


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
    pairs = {}
    for k2, names in case.get("pairs", {}).items():
        a, b = k2.split("@")
        for n in names:
            if n not in T.BINARY:
                raise ValueError(f"{case['id']} {k2}: unknown fact {n}")
            pairs.setdefault(n, set()).add((a, b))
    for n, (ka, kb) in PAIR_KINDS.items():
        listed = pairs.get(n, set())
        for a in kind(ctx, ka):
            for b in kind(ctx, kb):
                f = T.B(n, a, b)
                out.append({"id": f"{n}.{a}.{b}", "formula": f if (a, b) in listed else ["not", f]})
        stray = {p for p in listed if p[0] not in kind(ctx, ka) or p[1] not in kind(ctx, kb)}
        if stray:
            raise ValueError(f"{case['id']}: {n} on items of the wrong kind {sorted(stray)}")
    ints = dict(case.get("ints", {}))
    for ch in ctx.children:
        if f"nights_{ch}" not in ints and ch in case.get("qc_children", ctx.children):
            ints[f"nights_{ch}"] = "0"
    for name, value in sorted(ints.items()):
        if name.split("_", 1)[0] not in T.STATED_INTS:
            raise ValueError(f"{case['id']}: {name} is not a stated integer")
        out.append({"id": name, "formula": literal(name, value)})
    return out
