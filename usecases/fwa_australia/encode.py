"""The encoder's facts for one case (cases.py). SAME-FAMILY.

Conventions (stated, the same for every case):
C1 closed world over translation.FACTS: a fact the case record does not list as true is stated false; the encoder lists
   every true fact it reads in the question's facts (one employee, item e);
C2 integer constants (the service years and days at the three times the facts name, the casual period, the days and clock
   times of notice and termination, the weekly base and full rates) only where the question gives them; the age
   (agey, aged) comes only from bridge/bridges.jsonl (never typed by the encoder);
C3 a stated judgment enters as the stated fact (translation.STATED), never decided by the encoder;
C4 "the time of termination" service the facts state is the service "immediately before the time of the termination"
   (s. 121(1)); a casual period the facts do not mention is 0 years 0 days ("has never been employed ... as a casual
   employee").
"""
from __future__ import annotations

import json
from pathlib import Path

import translation as T

HERE = Path(__file__).resolve().parent


def literal(name, value):
    unit = T.INT_UNITS[name.rsplit("_", 1)[0]][0]
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
            out[r["case"]] = (r["years"], r["days"])
    return out


def ctx_of(case):
    return T.Ctx("e")


def facts(case):
    out = []
    mine = set(case.get("facts", ()))
    bad = mine - set(T.FACTS)
    if bad:
        raise ValueError(f"{case['id']}: unknown facts {sorted(bad)}")
    for p in T.FACTS:
        f = T.U(p, "e")
        out.append({"id": f"e.{p}", "formula": f if p in mine else ["not", f]})
    ints = dict(case.get("ints", {}))
    if set(ints) & {f"{b}_e" for b in T.BRIDGED}:
        raise ValueError(f"{case['id']}: a bridged constant typed by the encoder")
    br = bridges().get(case["id"])
    if br is not None:
        ints["agey_e"], ints["aged_e"] = br
    for name, value in sorted(ints.items()):
        out.append({"id": name, "formula": literal(name, value)})
    return out
