"""The encoder's facts for one case (cases.py). CROSS-FAMILY questions, Opus encoder.

Conventions (stated, the same for every case; written with the translation, before the encoder's question file was read):
C1 closed world over translation.FACTS: a fact the case record does not list as true for an item is stated false (every unary
   fact for every item);
C2 items: one employment e per case (the current employer's; in a transfer or retendering case, the second employer's); one
   year item per year of employment a question asks about or a termination question owes for (its first and last day as
   the question or the case states them; "owe" marks a prior completed year of a termination question); one vacation item
   per vacation or period a question asks about; one holiday item per stated general holiday of such a vacation; one
   transfer item for a lease, transfer, sale, merger or retendering between two employers;
C3 day, count and money constants only where the case states them: the termination day td_e; a vacation's first and last
   days vs_v / ve_v; a holiday's day hd_h and wages hw_h; weeks or days taken tkw_v / tkd_v; wages wy_y and wt_e; vacation
   pay paid during a year vppy_y / during the part year vppt_e (0.00 when the case states none); vacation pay paid in respect
   of an owed year pd_y (0.00 when the case states none was paid); the transfer's l1_t, xd_t (the transfer day, or for a
   retendering the first day the second employer carries out the work), s2_t; no derived constant is ever typed;
C4 the dates the bridge reads (case "emp"): the current employment's start, the employer's kind of year ("anniv": twelve
   months from the start or an anniversary; "set": a calendar or other year determined by the employer, with one of its
   first days as "anchor"), and in a transfer case the first employer's start and last day; the bridge (bridge/bridge.py)
   gives ca/cb, nka/nkb, nea/neb and lst; they enter as facts marked "bridge";
C5 amounts are entered exactly as stated, in dollars and cents; a case that states the half-up rounding convention sets "hu".
"""
from __future__ import annotations

import sys
from pathlib import Path

import translation as T

sys.path.insert(0, str(Path(__file__).resolve().parent / "bridge"))
import bridge as B  # noqa: E402


def ctx_of(case):
    return T.Ctx(emps=case.get("emps", ["e"]), **{kd: case.get(kd, {}) for kd in T.Ctx.KINDS})


def literal(name, value):
    base = name.split("_", 1)[0]
    unit = T.INT_UNITS[base][0]
    if unit == T.DAY:
        lit = ["date", value]
    elif unit == T.CAD:
        lit = ["decimal", T.CAD, f"{float(value):.2f}" if not isinstance(value, str) else value]
    else:
        lit = ["decimal", unit, str(int(value))]
    return ["eq", ["const", unit, name], lit]


def bridged(case, ctx):
    """name -> value of every bridged constant (C4)."""
    emp = case.get("emp")
    if not emp:
        return {}
    out = {}
    e = ctx.emps[0]
    t = ctx.xfer_of(e)
    days = case.get("days", {})
    td = days.get(f"td_{e}")
    effs = {"a": B.eff_start(emp["start"])}
    if t is not None:
        effs["b"] = B.eff_start(emp["start"], emp["start1"], emp["end1"])
    for y, (first, last) in case.get("ydays", {}).items():
        for ab, eff in effs.items():
            out[f"c{ab}_{y}"] = B.year_count(first, last, eff, td)
        out[f"lst_{y}"] = B.ten_months(last)
    if td is not None:
        for ab, eff in effs.items():
            anchor = eff if emp["kind"] == "anniv" else emp["anchor"]
            out[f"nk{ab}_{e}"] = B.kind_years_by(anchor, eff, td)
            out[f"ne{ab}_{e}"] = B.elapsed_years(eff, td)
    return out


def facts(case):
    ctx = ctx_of(case)
    out = []
    true = {x: set(v) for x, v in case.get("facts", {}).items()}
    consts = {**case.get("days", {}), **case.get("cads", {}), **case.get("cnts", {})}
    for e in ctx.emps:
        consts.setdefault(f"vppt_{e}", "0.00")
    for y in ctx.years:
        consts.setdefault(f"vppy_{y}", "0.00")
    for name in consts:
        base, x = name.split("_", 1)
        if base not in T.INT_UNITS:
            raise ValueError(f"{case['id']}: unknown constant {name}")
        if x not in ctx.items:
            raise ValueError(f"{case['id']}: constant {name} of an unknown item")
        if base in T.DERIVED_CONSTS or base in T.BRIDGED:
            raise ValueError(f"{case['id']}: derived or bridged constant typed by the encoder: {name}")
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
    for name, value in sorted(bridged(case, ctx).items()):
        if name.split("_", 1)[1] not in ctx.items:
            continue
        out.append({"id": f"bridge:{name}", "formula": literal(name, value), "bridge": True})
    return out


def bridged_ints(case, ctx):
    return bridged(case, ctx)
