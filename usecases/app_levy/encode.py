"""The encoder's facts for one case (cases.py). SAME-FAMILY.

Conventions (stated, the same for every case; fixed with the translation, before the encoder's questions were read):
C1 closed world over the case's named items and translation's facts: a fact the case record does not list is stated
   false; the encoder lists every true fact it reads in the question's facts. Fixed facts of the test (WRITER-BRIEF):
   no person is a charity and s. 103 does not apply (charity is always false).
C2 one context = one tax year; a case that names two tax years is encoded as one record per year (ids <case>@<year>).
C3 persons are the employers the facts name; "company" is listed for a person the facts call a company (a limited
   company, plc) and "llp" for a limited liability partnership; an individual employer has neither.
C4 earnings items: one per earner per employer as the facts state them, with the stated amount (the encoder never adds,
   splits or computes an amount); the item's liability is as stated: a liability to pay secondary Class 1 contributions
   (including GBP 0) -> sec + liab; "would incur but for s. 6(1)(b)" (earnings below the lower earnings limit) -> sec +
   butfor; neither -> sec only.
C5 a group is the set of companies the facts state are connected with one another at the beginning of the tax year
   (conn for each); a company stated not connected with the others is in no group.
C6 determinations, alterations, returns (on the basis that the company is entitled to an allowance, whether or not of
   zero), HMRC's awareness and written notices, the remedial action and whether it was taken in the period, amounts paid
   and due: as stated; a member a stated determination gives no amount is given GBP 0.00 only where the facts say so.
C7 a stated rounding of a s. 101(12) share -> rnd_up / rnd_down, or rnd_fig with HMRC's figure; the half-up convention
   for an amount charged -> halfup on that person.
"""
from __future__ import annotations

import translation as T

KINDS = {"person": T.FACTS_PERSON, "earn": T.FACTS_EARN, "group": T.FACTS_GROUP}


def ctx_of(case):
    return T.Ctx(case["persons"], case.get("earnings", {}), case.get("groups", {}))


def literal(name, value):
    return ["eq", ["const", T.GBP, name], ["decimal", T.GBP, str(value)]]


def facts(case):
    ctx = ctx_of(case)
    listed = set(case.get("facts", ()))
    items = {"person": ctx.persons, "earn": list(ctx.earnings), "group": list(ctx.groups)}
    known = set()
    out = []
    for kind, preds in KINDS.items():
        for x in items[kind]:
            for p in preds:
                tag = f"{p}:{x}"
                known.add(tag)
                if p == "charity" and tag in listed:
                    raise ValueError(f"{case['id']}: a charity (out of scope: a probe)")
                f = T.U(p, x)
                out.append({"id": tag, "formula": f if tag in listed else ["not", f]})
    for g, members in ctx.groups.items():
        for x in ctx.persons:
            tag = f"conn:{x}:{g}"
            known.add(tag)
            f = T.B("conn", x, g)
            out.append({"id": tag, "formula": f if tag in listed else ["not", f]})
    bad = listed - known
    if bad:
        raise ValueError(f"{case['id']}: unknown facts {sorted(bad)}")
    ints = dict(case.get("ints", {}))
    for name, value in sorted(ints.items()):
        base, x = name.split("_", 1)
        if base not in T.INT_UNITS or x not in ctx.items:
            raise ValueError(f"{case['id']}: unknown constant {name}")
        if base in T.STEP_BASES:
            raise ValueError(f"{case['id']}: a derived amount typed by the encoder ({name})")
        out.append({"id": name, "formula": literal(name, value)})
    return out
