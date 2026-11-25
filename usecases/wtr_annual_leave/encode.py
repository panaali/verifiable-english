"""The encoder's facts for one case (cases.py). CROSS-FAMILY questions, Opus encoder.

Conventions (stated, the same for every case):
C1 closed world over translation.FACTS and BINARY: a fact the case record does not list as true is stated false; the
   encoder lists every true fact it reads in the case's facts. "worker" is the fixed fact of the test for the worker item.
C2 items: one worker w; one leave-year item per leave year a question names or the rules need (consecutive, in order: a
   carried-forward question names the years between); one notice item per notice; one proposal item per proposed day.
C3 constants only where the case states them (days worked in a week, the employment's first day, the termination date, a
   leave year's first day as the question names it, the leave taken and the paid leave taken, a notice's day, earliest day
   and number of days or part-days, the agreement's sum, carry-forward days and timing offset, a proposed day); the next
   leave year, the days of a leave year, the days remaining / expired, the elapsed days of the 2007 / 2009 years, the end of
   the 18 months and the anniversaries come ONLY from bridge/bridges.jsonl (never typed by the encoder).
C4 a stated judgment enters as the stated fact (translation.STATED), never decided by the encoder. Anything the encoder
   decides beyond copying a stated fact is listed in the case's "judgement" ("encoder judgement").
C5 a question is mapped to one answer form (run.py) on one item, or to "parts" (all parts yes -> yes, one no -> no); a
   question no form carries is mapped to "none" (refused, OPEN); out-of-scope cases are answered UNSUPPORTED.
"""
from __future__ import annotations

import json
from pathlib import Path

import translation as T

HERE = Path(__file__).resolve().parent
KINDS = ("workers", "years", "notices", "proposals")


def base_of(name):
    return name.split("_", 1)[0]


def unit_of(name):
    b = base_of(name)
    return (T.INT_UNITS.get(b) or T.PAIR_UNITS[b])[0]


def literal(name, value):
    unit = unit_of(name)
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
    for w in ctx.workers:
        true.setdefault(w, set()).add("worker")  # C1
    for x in ctx.items:
        mine = true.get(x, set())
        bad = mine - set(T.FACTS)
        if bad:
            raise ValueError(f"{case['id']} {x}: unknown facts {sorted(bad)}")
        for p in T.FACTS:
            f = T.U(p, x)
            out.append({"id": f"{x}.{p}", "formula": f if p in mine else ["not", f]})
    of = {tuple(x) for x in case.get("of", ())}
    for p in ctx.proposals:
        for y in ctx.years:
            f = T.B("of", p, y)
            out.append({"id": f"of.{p}.{y}", "formula": f if (p, y) in of else ["not", f]})
    ints = dict(case.get("ints", {}))
    typed = {n for n in ints if base_of(n) in T.BRIDGED_CONSTS}
    if typed:
        raise ValueError(f"{case['id']}: bridged constants typed by the encoder: {sorted(typed)}")
    known = T.int_constants(ctx)
    bad = set(ints) - set(known)
    if bad:
        raise ValueError(f"{case['id']}: unknown constants {sorted(bad)}")
    asked = {n for n in ints if base_of(n) in T.ASKED_BASES}
    if asked:
        raise ValueError(f"{case['id']}: derived constants typed by the encoder: {sorted(asked)}")
    ints.update(bridged_ints(case, ctx, br))
    for name, value in sorted(ints.items()):
        out.append({"id": name, "formula": literal(name, value)})
    return out
