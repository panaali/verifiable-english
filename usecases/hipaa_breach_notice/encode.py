"""The encoder's facts for one case (cases.py). CROSS-FAMILY questions, Opus encoder.

Conventions (stated, the same for every case; written with the translation, before the encoder's question file was read):
C1 closed world over translation.FACTS: a fact the case record does not list as true for an item is stated false (every unary
   fact for every item);
C2 items: one incident i per case; one State item per State or jurisdiction named with affected residents (its name kept for
   the Q2 answer); one business-associate item b when a business associate is in the case; one knower item per person whose
   learning day the case states (side "ce" or "ba"); one statement item per law enforcement statement; one individual item
   per individual (or alike group) a method question asks about; one element item per content element a question asks about;
C3 day and count constants only where the case states them (the discovery day of a first-form case is disc_i / bdisc_b; a
   person's learning day kd_k; the reasonable-diligence day dd_i / bdd_b; residents res_s; individuals with insufficient
   contact information nins_i; a posting's or toll-free number's days; a statement's day, its stated last day, a following
   written statement's day and last day; the day individual notices were given isd_i); the presence flags hasdd, hasbdd,
   hasisd, hasnins, post, tfree are set exactly when the matching constant is stated; no total, no derived day is ever typed;
C4 a stated judgment enters as the stated fact (translation.STATED), never decided by the encoder;
C5 a constant the translation derives (disc/bdisc of a second-form case, li, lm, ls, ye, lb, l30, dly, tot) is never typed.
"""
from __future__ import annotations

import translation as T

DERIVED = {"disc", "bdisc", "li", "lm", "ls", "ye", "lb", "l30", "dly", "tot"}
FLAGS = {"dd": "hasdd", "bdd": "hasbdd", "isd": "hasisd", "nins": "hasnins", "pdays": "post", "tdays": "tfree"}


def ctx_of(case):
    return T.Ctx(incs=case.get("incs", ["i"]), **{kd: case.get(kd, {}) for kd in T.Ctx.KINDS})


def literal(name, value):
    base = name.split("_", 1)[0]
    unit = T.INT_UNITS[base][0]
    lit = ["date", value] if unit == T.DAY else ["decimal", unit, str(int(value))]
    return ["eq", ["const", unit, name], lit]


def facts(case):
    ctx = ctx_of(case)
    out = []
    true = {x: set(v) for x, v in case.get("facts", {}).items()}
    consts = {**case.get("days", {}), **case.get("cnts", {})}
    for name in consts:
        base, x = name.split("_", 1)
        if base not in T.INT_UNITS:
            raise ValueError(f"{case['id']}: unknown constant {name}")
        if x not in ctx.items:
            raise ValueError(f"{case['id']}: constant {name} of an unknown item")
        if base in FLAGS:
            true.setdefault(x, set()).add(FLAGS[base])
    stated_disc = {n for n in consts if n.split("_", 1)[0] in ("disc", "bdisc")}
    typed = {n for n in consts if n.split("_", 1)[0] in DERIVED} - stated_disc
    if typed:
        raise ValueError(f"{case['id']}: derived constants typed by the encoder: {sorted(typed)}")
    for x in ctx.items:
        mine = true.get(x, set())
        bad = mine - set(T.FACTS)
        if bad:
            raise ValueError(f"{case['id']} {x}: unknown facts {sorted(bad)}")
        for p in T.FACTS:
            f = T.U(p, x)
            out.append({"id": f"{x}.{p}", "formula": f if p in mine else ["not", f]})
    for name, value in sorted(consts.items()):
        out.append({"id": name, "formula": literal(name, value)})
    return out


def bridged_ints(case, ctx):
    return {}   # no bridge in this translation: every day and count step is in Lean
