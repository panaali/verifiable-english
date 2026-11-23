"""The encoder's facts for one case (cases.py). SAME-FAMILY.

Conventions (stated, the same for every case):
C1 closed world: a unary fact on a transaction or person, and a (person, transaction) fact, that the case record does not
   list as true is stated false (the encoder lists every true fact it reads in the question's facts);
C2 the (transaction, transaction) links (linked, earlier, gardenof, benefitof) are exactly those the case lists: every
   other ordered pair of distinct transactions is stated false for each of them; "linked" is listed in both directions
   for every pair of transactions the facts say are linked (rules quantify over the listed ones);
C3 integer constants (chargeable consideration, years a lease has to run) are stated only where the question gives them;
   nothing is computed by the encoder (no bridge in this law: amounts are never bridged);
C4 a stated judgment enters as the stated fact (translation.STATED), never decided by the encoder.
"""
from __future__ import annotations

import translation as T


def literal(name, value):
    unit = T.INT_UNITS[name.split("_", 1)[0]][0]
    return ["eq", ["const", unit, name], ["decimal", unit, value]]


def facts(case):
    out = []
    true = case.get("facts", {})
    txns, persons = case["txns"], case.get("persons", [])
    for x in list(true):
        if x not in txns and x not in persons:
            raise ValueError(f"{case['id']}: facts for unknown item {x}")
    for x in txns:
        mine = set(true.get(x, ()))
        bad = mine - set(T.FACTS)
        if bad:
            raise ValueError(f"{case['id']} {x}: unknown facts {sorted(bad)}")
        for p in T.FACTS:
            f = T.U(p, x)
            out.append({"id": f"{x}.{p}", "formula": f if p in mine else ["not", f]})
    for x in persons:
        mine = set(true.get(x, ()))
        bad = mine - set(T.PFACTS)
        if bad:
            raise ValueError(f"{case['id']} {x}: unknown facts {sorted(bad)}")
        for p in T.PFACTS:
            f = T.U(p, x)
            out.append({"id": f"{x}.{p}", "formula": f if p in mine else ["not", f]})
    pt = {(p, a, b) for (p, a, b) in case.get("pt", ())}
    for (p, a, b) in pt:
        if p not in T.PTFACTS or a not in persons or b not in txns:
            raise ValueError(f"{case['id']}: bad person-txn fact {(p, a, b)}")
    for a in persons:
        for b in txns:
            for p in T.PTFACTS:
                f = T.B(p, a, b)
                out.append({"id": f"{p}.{a}.{b}", "formula": f if (p, a, b) in pt else ["not", f]})
    for (p, a, b) in case.get("links", ()):
        if p not in T.TTFACTS or a not in txns or b not in txns:
            raise ValueError(f"{case['id']}: bad link {(p, a, b)}")
        out.append({"id": f"{p}.{a}.{b}", "formula": T.B(p, a, b)})
    listed = {(p, a, b) for (p, a, b) in case.get("links", ())}
    for a in txns:
        for b in txns:
            if a != b:
                for p in T.TTFACTS:
                    if (p, a, b) not in listed:
                        out.append({"id": f"{p}.{a}.{b}", "formula": ["not", T.B(p, a, b)]})
    links = set(case.get("links", ()))
    for (p, a, b) in links:
        if p == "linked" and ("linked", b, a) not in links:
            raise ValueError(f"{case['id']}: linked must be listed both ways ({a}, {b})")
    for name, value in sorted(case.get("ints", {}).items()):
        if name.split("_", 1)[0] not in T.STATED_BASES:
            raise ValueError(f"{case['id']}: {name} is derived, never stated")
        out.append({"id": name, "formula": literal(name, value)})
    return out
