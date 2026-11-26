"""The encoder's facts for one case (cases.py). CROSS-FAMILY questions, Opus encoder.

Conventions (stated, the same for every case; written before the encoder's question file was read):
C1 closed world over translation.FACTS and BINARY: a fact the case record does not list as true is stated false; the encoder
   lists every true fact it reads in the case's facts. "member" is the fixed fact of the test for every member item; "of"
   defaults to every absence being the (single) member's; "in_year" is listed per (absence, year).
C2 items: one member per case; one absence per stated absence (its first day and its stated work days); one year item per
   calendar year a question asks about; one leave item per parental leave; one block per continuous block of a parental leave
   the case names; one quarter item per quarter whose attainment is stated.
C3 integer constants only where the case states them (work days, first days, the contract's limit, months and days at
   PostHog, the local statutory weeks, the leave's first day, the day it was logged, the weeks taken, a quarter's
   attainment); the day 4 months before a leave, a quarter's first and last day and the prior two full quarters come ONLY
   from bridge/bridges.jsonl (never typed by the encoder).
C4 a stated judgment enters as the stated fact (translation.STATED), never decided by the encoder; "longterm" is set only as
   an encoder judgement (listed in the case's "judgement").
C5 a question is mapped to one answer form (run.py YESNO / AMOUNT / "weeks" / "deadline") on one item; a question no form
   carries is answered UNSUPPORTED only when its case is out of scope, otherwise it is mapped to "none" and refused (OPEN).
C6 (fidelity fix 11-26, translation R14) open facts, NOT closed-world: "span" lists the absences whose days fall in more
   than one calendar year, "within" those stated to lie in one; an absence in neither list has no span fact (unknown).
   "periods" lists groups of absences, each group one continuous period of illness: two absences in the same group are
   sameill, two listed absences in different groups are not; a pair with an unlisted absence has no fact (unknown).
   "dy_<absence>_<year>" (the absence's work days in the year) is an integer constant stated like the others (C3).
"""
from __future__ import annotations

import json
from pathlib import Path

import translation as T

HERE = Path(__file__).resolve().parent
KINDS = ("members", "absences", "years", "leaves", "blocks", "quarters")


def literal(name, value):
    base = name.split("_", 1)[0]
    unit = (T.INT_UNITS.get(base) or T.PAIR_UNITS[base])[0]  # pair constants: dy (C6)
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
            out[(r["case"], r["item"], r["kind"])] = r["values"]
    return out


def bridge_inputs(case):
    """The bridge input lines of a case (copied from its facts by cases.py)."""
    return [{"case": case["id"], **b} for b in case.get("bridge", [])]


def bridged_ints(case, ctx, br=None):
    br = bridges() if br is None else br
    out = {}
    for b in case.get("bridge", []):
        v = br.get((case["id"], b["item"], b["kind"]))
        if v is None:
            continue
        for base, val in v.items():
            out[f"{base}_{b['item']}"] = val
    return out


def ctx_of(case):
    return T.Ctx(*[case.get(kd, ()) for kd in KINDS])


def facts(case, br=None):
    ctx = ctx_of(case)
    out = []
    true = {x: set(v) for x, v in case.get("facts", {}).items()}
    for m in ctx.members:
        true.setdefault(m, set()).add("member")  # C1
    for x in ctx.items:
        mine = true.get(x, set())
        bad = mine - set(T.FACTS)
        if bad:
            raise ValueError(f"{case['id']} {x}: unknown facts {sorted(bad)}")
        for p in T.FACTS:
            f = T.U(p, x)
            out.append({"id": f"{x}.{p}", "formula": f if p in mine else ["not", f]})
    iy = {tuple(x) for x in case.get("in_year", ())}
    of = {tuple(x) for x in case.get("of", [(a, m) for a in ctx.absences for m in ctx.members])}
    for a in ctx.absences:
        for y in ctx.years:
            f = T.B("in_year", a, y)
            out.append({"id": f"in_year.{a}.{y}", "formula": f if (a, y) in iy else ["not", f]})
        for m in ctx.members:
            f = T.B("of", a, m)
            out.append({"id": f"of.{a}.{m}", "formula": f if (a, m) in of else ["not", f]})
    out += open_facts(case, ctx)
    ints = dict(case.get("ints", {}))
    typed = {n for n in ints if n.split("_", 1)[0] in T.BRIDGED_CONSTS}
    if typed:
        raise ValueError(f"{case['id']}: bridged constants typed by the encoder: {sorted(typed)}")
    known = T.int_constants(ctx)
    bad = set(ints) - set(known)
    if bad:
        raise ValueError(f"{case['id']}: unknown constants {sorted(bad)}")
    ints.update(bridged_ints(case, ctx, br))
    for name, value in sorted(ints.items()):
        out.append({"id": name, "formula": literal(name, value)})
    return out


def open_facts(case, ctx):
    """C6: the open facts span (unary) and sameill (binary, symmetric); unstated = no fact."""
    out = []
    span, within = set(case.get("span", ())), set(case.get("within", ()))
    periods = [list(g) for g in case.get("periods", ())]
    listed = [a for g in periods for a in g]
    bad = (span | within | set(listed)) - set(ctx.absences)
    if bad or span & within or len(listed) != len(set(listed)):
        raise ValueError(f"{case['id']}: bad span/within/periods {sorted(bad | (span & within))}")
    for a in ctx.absences:
        if a in span or a in within:
            f = T.U("span", a)
            out.append({"id": f"{a}.span", "formula": f if a in span else ["not", f]})
    group = {a: i for i, g in enumerate(periods) for a in g}
    for a in ctx.absences:
        for b in ctx.absences:
            if a != b and a in group and b in group:
                f = T.B("sameill", b, a)
                out.append({"id": f"sameill.{b}.{a}", "formula": f if group[a] == group[b] else ["not", f]})
    return out
