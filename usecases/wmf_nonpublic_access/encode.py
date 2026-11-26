"""The encoder's facts for one case (cases.py). CROSS-FAMILY questions, Opus encoder.

Conventions (stated, the same for every case; written with the translation, before the encoder's question file was read):
C1 closed world over translation.FACTS / BINARY: a fact the case record does not list as true is stated false (every unary
   fact for every item; chg for every (change, test) pair, from for every (data, tool) pair, unless listed);
C2 items: one member m; one test item per grant, candidacy or compliance check asked; one change item per change of address;
   one disclosure item per disclosure or request asked; tools, data, uses, complaints, information as asked;
C3 day constants only where the question states the day (the act's day, the day asked, the effective day, the grant day,
   the extension day, the disclosure day, the email and approval days, the revocation day); the days a member attains 16
   and 18 and the tenth business day back from a disclosure come ONLY from bridge/bridges.jsonl (never typed by the encoder);
   "hasapp" is set exactly when an application day is stated besides the day asked;
C4 a stated judgment enters as the stated fact (translation.STATED), never decided by the encoder;
C5 a test of the (e) deadline (case field "atdl") gets no stated day: its day is the member's deadline, a Lean step;
C6 (latent fix 11-26) a data item gets "npd" and "npdst" when the case says the data is nonpublic / private personal data,
   "npdst" alone when it says the data is not (no personal data, public), neither when it says nothing (the destroy
   question is then refused). Nothing in this file changed but this note: C1 already covers the two new facts.
"""
from __future__ import annotations

import json
from pathlib import Path

import translation as T

HERE = Path(__file__).resolve().parent


def literal(name, value):
    return ["eq", ["const", T.DAY, name], ["date", value]]


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
    """test -> a16_<t>, a18_<t>; disclosure -> b10_<d>."""
    br = bridges() if br is None else br
    out = {}
    for x in ctx.tests + ctx.discs:
        v = br.get((case["id"], x))
        if v is None:
            continue
        for base in ("a16", "a18", "b10"):
            if base in v:
                out[f"{base}_{x}"] = v[base]
    return out


def ctx_of(case):
    return T.Ctx(**{kd: case.get(kd, ()) for kd in T.Ctx.KINDS}, atdl=case.get("atdl", ()))


def facts(case, br=None):
    ctx = ctx_of(case)
    out = []
    true = {x: set(v) for x, v in case.get("facts", {}).items()}
    ints = dict(case.get("ints", {}))
    for a in ctx.tests:
        if f"app_{a}" in ints:
            true.setdefault(a, set()).add("hasapp")
    for x in ctx.items:
        mine = true.get(x, set())
        bad = mine - set(T.FACTS)
        if bad:
            raise ValueError(f"{case['id']} {x}: unknown facts {sorted(bad)}")
        for p in T.FACTS:
            f = T.U(p, x)
            out.append({"id": f"{x}.{p}", "formula": f if p in mine else ["not", f]})
    chg = {tuple(x) for x in case.get("chg", [(e, a) for e in ctx.changes for a in ctx.tests])}
    frm = {tuple(x) for x in case.get("from", ())}
    for e in ctx.changes:
        for a in ctx.tests:
            f = T.B("chg", e, a)
            out.append({"id": f"chg.{e}.{a}", "formula": f if (e, a) in chg else ["not", f]})
    for x in ctx.datas:
        for t in ctx.tools:
            f = T.B("from", x, t)
            out.append({"id": f"from.{x}.{t}", "formula": f if (x, t) in frm else ["not", f]})
    typed = {n for n in ints if n.split("_", 1)[0] in T.BRIDGED_CONSTS}
    if typed:
        raise ValueError(f"{case['id']}: bridged constants typed by the encoder: {sorted(typed)}")
    steps = {f"at_{a}" for a in ctx.atdl}
    if steps & set(ints):
        raise ValueError(f"{case['id']}: a deadline test's day typed by the encoder")
    ints.update(bridged_ints(case, ctx, br))
    for name, value in sorted(ints.items()):
        out.append({"id": name, "formula": literal(name, value)})
    return out
