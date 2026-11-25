"""The encoder's facts for one case (cases.py). CROSS-FAMILY questions, Opus encoder.

Conventions (stated, the same for every case; written before the encoder's question file was read):
C1 closed world over translation.FACTS and BINARY: a fact the case record does not list as true is stated false; the encoder
   lists every true fact it reads in the case's facts. Exception (R4, R10): a sum the encoder cannot place in or out of the
   s. 13(3) list is listed in "unplaced" and gets NO description fact at all (neither true nor false), and a cessation whose
   cause is neither stated as the jobholder's own action or omission nor as something else gets neither "own" nor
   "notown" (it is "gbqe" when the stated cause is ceasing to work in Great Britain or to have qualifying earnings).
C2 items, per employment (s. 1(2)-(3)): the employment j; one day item per day a question names, per stated automatic
   enrolment or re-enrolment date, and per day of a stated window (form (b), listed by the bridge); one period per stated pay
   reference period; one sum per stated sum (its description and gross amount); one membership per stated period of active
   membership of a scheme.
C3 integer constants only where the case states them (days, period first/last days and lengths, amounts, the pensionable
   age day, membership and cessation days, the stated automatic enrolment date, the deferral's two dates); the age on a day,
   the first day of the 12 months ending with the day before a day, and the days of a window come ONLY from
   bridge/bridges.jsonl (never typed by the encoder).
C4 a stated judgment enters as the stated fact, never decided by the encoder; anything the encoder decides beyond copying a
   stated fact is listed in the case's "judgement" (encoder judgement).
C5 a question is mapped to one answer form (run.py: duty3, duty5, qe, fails, aedate) on one item; a question no form
   carries is answered UNSUPPORTED only when its case is out of scope, otherwise it is mapped to "none" and refused (OPEN).
C6 a working-in-Great-Britain fact is stated per day item from the case's stated dates (the case's words "works in Great
   Britain" throughout, or from / until a stated day); "nogbs" for a window point when no day of its stretch is inside the
   stated Great Britain days.
C7 (R7a, written with the translation's structural change, before any answer was read) a form (b) window is given to the
   bridge as its stated first and last day ("wf", "wl", typed), the date of birth, and every stated date inside it the
   case's facts change on (a pay reference period's first day and the day after its last day, the first and the last-plus-
   one day of working in Great Britain, the day pensionable age is reached, a membership's first day and the day after its
   last day); the bridge returns the points and stretch ends; each point's age, stretch-end age and prescribed-period start
   come from the bridge.
"""
from __future__ import annotations

import json
from pathlib import Path

import translation as T

HERE = Path(__file__).resolve().parent
DESC = ("da", "db", "dc", "dd", "de", "dea", "deb", "dec", "df")


def literal(name, value):
    base = name.split("_", 1)[0]
    unit = T.INT_UNITS[base][0]
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
    """The bridge input lines of a case (cases.py)."""
    return [{"case": case["id"], **b} for b in case.get("bridge", [])]


def windows(case, br=None):
    """{employment: [(point item, day, stretch end)]}: the points of each stated window, from the bridge only (R7a)."""
    br = bridges() if br is None else br
    out = {}
    for b in case.get("bridge", []):
        if b["kind"] == "points":
            v = br.get((case["id"], b["item"], "points"))
            if v is None:
                raise ValueError(f"{case['id']}: no bridge output for the window of {b['item']}")
            out[b["item"]] = [(f"{b['item']}w{i + 1}", d, t) for i, (d, t) in enumerate(zip(v["days"], v["tts"]))]
    return out


def ctx_of(case, br=None):
    win = windows(case, br)
    emps = []
    for e in case["emps"]:
        pts = [x for x, _, _ in win.get(e["j"], [])]
        emps.append(T.Emp(e["j"], list(e.get("days", ())) + pts, e.get("periods", ()), e.get("sums", ()),
                          e.get("members", ()), {r: tuple(v) for r, v in e.get("lengths", {}).items()}, pts))
    return T.Ctx(emps)


def bridged_ints(case, ctx=None, br=None):
    br = bridges() if br is None else br
    out = {}
    for b in case.get("bridge", []):
        if b["kind"] == "points":
            continue
        v = br.get((case["id"], b["item"], b["kind"]))
        if v is not None:
            for base, val in v.items():
                out[f"{base}_{b['item']}"] = val
    for pts in windows(case, br).values():
        for x, d, t in pts:
            out[f"day_{x}"], out[f"tt_{x}"] = d, t
            for kind in ("age", "pst", "aget"):
                v = br.get((case["id"], x, kind))
                if v is not None:
                    out[f"{kind}_{x}"] = v[kind]
    return out


def facts(case, br=None):
    br = bridges() if br is None else br
    ctx = ctx_of(case, br)
    win = windows(case, br)
    out = []
    true = {x: set(v) for x, v in case.get("facts", {}).items()}
    unplaced = set(case.get("unplaced", ()))
    open_cause = set(case.get("open_cause", ()))
    gbwin = case.get("gb_window", {})  # employment -> [first GB day or None, last GB day or None], or "never" (C6)
    for j, pts in win.items():
        g = gbwin.get(j, "never")
        for x, d, t in pts:
            true.setdefault(x, set()).add("win")
            if g != "never" and (g[0] is None or g[0] <= d) and (g[1] is None or d <= g[1]):
                true[x].add("gb")
            if g == "never" or (g[0] is not None and t < g[0]) or (g[1] is not None and g[1] < d):
                true[x].add("nogbs")
    for x in ctx.items:
        mine = true.get(x, set())
        bad = mine - set(T.FACTS)
        if bad:
            raise ValueError(f"{case['id']} {x}: unknown facts {sorted(bad)}")
        for p in T.FACTS:
            if x in unplaced and p in DESC:
                continue
            if x in open_cause and p in ("own", "notown"):
                continue
            f = T.U(p, x)
            out.append({"id": f"{x}.{p}", "formula": f if p in mine else ["not", f]})
    payin = {tuple(x) for x in case.get("payin", ())}
    for e in ctx.emps:
        for s in e.sums:
            for r in e.periods:
                f = T.B("payin", s, r)
                out.append({"id": f"payin.{s}.{r}", "formula": f if (s, r) in payin else ["not", f]})
    ints = dict(case.get("ints", {}))
    typed = {n for n in ints if n.split("_", 1)[0] in T.BRIDGED_CONSTS}
    if typed:
        raise ValueError(f"{case['id']}: bridged constants typed by the encoder: {sorted(typed)}")
    known = T.int_constants(ctx)
    bridged = bridged_ints(case, ctx, br)
    bad = (set(ints) | set(bridged)) - set(known)
    if bad:
        raise ValueError(f"{case['id']}: unknown constants {sorted(bad)}")
    clash = set(ints) & set(bridged)
    if clash:
        raise ValueError(f"{case['id']}: constants both typed and bridged: {sorted(clash)}")
    ints.update(bridged)
    for name, value in sorted(ints.items()):
        out.append({"id": name, "formula": literal(name, value)})
    return out


def expand_bridge(case, br):
    """Second bridge pass: for every window point, its age, its stretch-end age (from the window's stated date of birth)
    and its prescribed-period start. Returns the extra input lines (cases.py writes them to bridge/inputs.jsonl)."""
    out = []
    dobs = {b["item"]: b["dob"] for b in case.get("bridge", []) if b["kind"] == "points"}
    for j, pts in windows(case, br).items():
        for x, d, t in pts:
            out += [{"case": case["id"], "item": x, "kind": "age", "dob": dobs[j], "day": d},
                    {"case": case["id"], "item": x, "kind": "aget", "dob": dobs[j], "day": t},
                    {"case": case["id"], "item": x, "kind": "pst", "day": d}]
    return out
