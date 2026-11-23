"""The encoder's facts for one award (cases.py). SAME-FAMILY.

Conventions (stated, the same for every award):
C1 closed world over the FACTS list: a unary fact the award record does not list as true is stated false for every
   person (the encoder lists every true fact it reads in the question's facts);
C2 closed world over the BINARY list: the links are exactly those the record lists (every other ordered pair is stated
   false); couple, married and poly_law are read in either order by the rules;
C3 integer constants are stated only from the question's facts: each adult's age (whole years on the first day of the
   assessment period), earned and unearned income (0.00 where the facts say none), and the housing costs element
   (0.00 where the award contains none). No amount is computed by the encoder (criterion 10);
C4 a stated judgment enters as the stated fact (translation.STATED), never decided by the encoder;
C5 the anchor is the first person the question names; a case with two awards gives two records.
"""
from __future__ import annotations

import translation as T


def literal(name, value):
    base = name.split("_", 1)[0]
    unit = T.PERSON_INTS[base][0] if base in T.PERSON_INTS else T.AWARD_INTS[base][0]
    return ["eq", ["const", unit, name], ["decimal", unit, value]]


ENCODER_INTS = ("age", "earn", "unearn", "housing")


def facts(case):
    out = []
    true = case.get("facts", {})
    persons = case["persons"]
    for x in persons:
        mine = set(true.get(x, ())) | ({"anchor"} if x == case["anchor"] else set())
        bad = mine - set(T.FACTS)
        if bad:
            raise ValueError(f"{case['id']} {x}: unknown facts {sorted(bad)}")
        for p in T.FACTS:
            f = T.U(p, x)
            out.append({"id": f"{x}.{p}", "formula": f if p in mine else ["not", f]})
    links = {tuple(l) for l in case.get("links", ())}
    for (p, a, b) in links:
        if p not in T.BINARY or a not in persons or b not in persons:
            raise ValueError(f"{case['id']}: bad link {(p, a, b)}")
    for p in T.BINARY:
        for a in persons:
            for b in persons:
                if a == b:
                    continue
                f = T.B(p, a, b)
                out.append({"id": f"{p}.{a}.{b}", "formula": f if (p, a, b) in links else ["not", f]})
    for name, value in sorted(case.get("ints", {}).items()):
        if name.split("_", 1)[0] not in ENCODER_INTS:
            raise ValueError(f"{case['id']}: the encoder states no {name} (derived amounts are never typed)")
        out.append({"id": name, "formula": literal(name, value)})
    return out
