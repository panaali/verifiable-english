"""The encoder's facts for one case (cases.py): only what the question states, as ground facts over the case's items.

Conventions (stated in RESULT.md): every claimant is an insured person (writer prompt, fixed facts); no benefits under
s. 23 (fixed facts: s23 false); 'halfup' is true exactly where the question states the half-cent-up convention; weekly
earnings are the stated amounts for weeks 1..M of the qualifying period (week ids w01..); lay-off/separation amounts are
the listed items s1..; the benefit period's first day and the maximum yearly insurable earnings are copied as stated.
"""
from __future__ import annotations

import translation as T


def context(case):
    return T.Ctx([f"w{i:02d}" for i in range(1, len(case["weeks"]) + 1)], [f"s{i}" for i in range(1, len(case["seps"]) + 1)])


def facts(case):
    ctx = context(case)
    out = []

    def add(fid, f):
        out.append({"id": fid, "formula": f})
    U, k = T.U, T.k
    add("insured", U("insured", T.CL) if case.get("insured", True) else T.Not(U("insured", T.CL)))
    add("interruption", U("interruption", T.CL) if case["interruption"] else T.Not(U("interruption", T.CL)))
    add("s23", T.Not(U("s23", T.CL)))
    add("halfup", U("halfup", T.CL) if case.get("halfup") else T.Not(U("halfup", T.CL)))
    add("rate", T.Eq(k("rate"), T.lit(T.RATE, case["rate"])))
    add("hours", T.Eq(k("hours"), T.lit(T.HOUR, case["hours"])))
    add("bpstart", T.Eq(k("bpstart"), T.day(case["bpstart"])))
    if case.get("myie") is not None:
        add("myie", T.Eq(k("myie"), T.cad(case["myie"])))
    for w, amt in zip(ctx.weeks, case["weeks"]):
        add(f"earn_{w}", T.Eq(k(f"earn_{w}"), T.cad(amt)))
    for s, amt in zip(ctx.seps, case["seps"]):
        add(f"sepamt_{s}", T.Eq(k(f"sepamt_{s}"), T.cad(amt)))
    return out
