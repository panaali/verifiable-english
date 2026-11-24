"""FMLA 29 CFR 825.110: TEMPLATE for the cross-family encoder: the build's record format, helpers and conventions;
records removed.

Each case (built with case()): "leaves" [(item, start day, employee count on the notice day)], "periods" [(item, first day,
last day, stated weeks or None = bridged weeks, facts)], "breaks" [(item, first day, last day, facts)], "blocks" [(item,
first day, last day, hours, fact)], "lfacts" (facts true for every leave item), "precedes" [(period, break)],
"period_for" (default: every period for every leave), "questions" [(qid, leave, form)], "judgement" (anything the encoder
decided beyond copying a stated fact: listed as "encoder judgement").
Bridge input (bridge/inputs.jsonl) = every leave's start (window) and every period's and break's first and last day
(duration), copied from the facts; written by write_bridge_inputs(). The bridge (bridge/fmla_bridge.py) computes the
12-month window start, whole months and days, and weeks; never typed here.
PROBES: out-of-scope cases, id -> reason; PROBE_QIDS: id -> its qids (every answer UNSUPPORTED). UNSUPPORTED: in-scope
cases the vocabulary cannot state, id -> (reason, [qids]).
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

PAY = ("payroll",)
USERRA_ABS = ("userra_abs",)
REC = ("acct", "acc_record")  # "The employer keeps an accurate record of the hours worked" + hours stated (FLSA)


def case(cid, leaves, periods, qs, breaks=(), blocks=(), lfacts=REC, precedes=(), period_for=None, judgement=()):
    facts, ints, bridge, bweeks = {}, {}, {}, []
    for (l, start, count) in leaves:
        facts[l] = list(lfacts)
        ints[f"start_{l}"], ints[f"count_{l}"] = start, count
        bridge[l] = {"kind": "window", "start": start}
    for (s, a, b, weeks, fl) in periods:
        facts[s] = list(fl)
        if weeks is None:
            bweeks.append(s)
        else:
            ints[f"weeks_{s}"] = weeks
        bridge[s] = {"kind": "duration", "from": a, "to": b}
    for (b_, a, b, fl) in breaks:
        facts[b_] = list(fl)
        bridge[b_] = {"kind": "duration", "from": a, "to": b}
    for (h, a, b, hours, fl) in blocks:
        facts[h] = [fl]
        ints[f"hours_{h}"], ints[f"hfrom_{h}"], ints[f"hto_{h}"] = hours, a, b
    c = {"id": cid, "leaves": [x[0] for x in leaves], "periods": [x[0] for x in periods],
         "breaks": [x[0] for x in breaks], "blocks": [x[0] for x in blocks], "facts": facts, "ints": ints,
         "precedes": [list(x) for x in precedes], "bridge": bridge, "bridge_weeks": bweeks,
         "questions": [{"qid": q, "item": l, "form": f} for (q, l, f) in qs], "judgement": list(judgement)}
    if period_for is not None:
        c["period_for"] = [list(x) for x in period_for]
    return c


def std(cid, l="l1"):
    """Q1 eligible, Q2 twelve, Q3 hours."""
    return [(f"{cid}-1", l, "eligible"), (f"{cid}-2", l, "twelve"), (f"{cid}-3", l, "hours")]


def site3(cid, l="l1"):
    """Q1 eligible, Q2 twelve, Q3 the 50-within-75-miles condition."""
    return [(f"{cid}-1", l, "eligible"), (f"{cid}-2", l, "twelve"), (f"{cid}-3", l, "site")]


def H(h, a, b, hours, fl="h_worked"):
    return (h, a, b, hours, fl)


CAS = ("casual",)
NOREC_J = "acct false: no accurate record kept; the stipulated actual hours are stated not to be the employer's evidence"


def q2(cid, l="l1"):
    """Q1 eligible, Q2 twelve (cases with two questions)."""
    return std(cid, l)[:2]


CASES = [
    # --- one continuous period, accurate record ---------------------------------------------------------------------
    case("F001", [("l1", "2026-01-01", 50)], [("p1", "2024-01-01", "2025-12-31", None, PAY)], std("F001"),
         blocks=[H("h1", "2025-01-01", "2025-06-30", 600), H("h2", "2025-07-01", "2025-12-31", 650)]),
    case("F002", [("l1", "2026-01-01", 50)], [("p1", "2024-01-01", "2025-12-31", None, PAY)], std("F002"),
         blocks=[H("h1", "2025-01-01", "2025-06-30", 600), H("h2", "2025-07-01", "2025-12-31", 649)]),
    case("F003", [("l1", "2026-11-01", 50)], [("p1", "2026-02-01", "2026-10-31", None, PAY)], std("F003"),
         blocks=[H("h1", "2025-11-01", "2026-01-31", 0), H("h2", "2026-02-01", "2026-06-30", 650),
                 H("h3", "2026-07-01", "2026-10-31", 650)]),
    case("F004", [("l1", "2026-01-01", 49)], [("p1", "2024-01-01", "2025-12-31", None, PAY)], site3("F004"),
         blocks=[H("h1", "2025-01-01", "2025-06-30", 600), H("h2", "2025-07-01", "2025-12-31", 650)]),
    # --- casual employment, two periods and a break -----------------------------------------------------------------
    case("F005", [("l1", "2025-07-06", 50)],
         [("p1", "2024-01-01", "2024-06-30", None, PAY), ("p2", "2025-01-06", "2025-07-05", None, PAY)], std("F005"),
         breaks=[("b1", "2024-07-01", "2025-01-05", ())], precedes=[("p1", "b1")], lfacts=REC + CAS,
         blocks=[H("h1", "2024-07-06", "2025-01-05", 0), H("h2", "2025-01-06", "2025-03-31", 650),
                 H("h3", "2025-04-01", "2025-07-05", 650)]),
    case("F006", [("l1", "2025-07-06", 50)],
         [("p1", "2024-01-01", "2024-06-30", None, PAY), ("p2", "2025-01-13", "2025-07-05", None, PAY)], std("F006"),
         breaks=[("b1", "2024-07-01", "2025-01-12", ())], precedes=[("p1", "b1")], lfacts=REC + CAS,
         blocks=[H("h1", "2024-07-06", "2025-01-12", 0), H("h2", "2025-01-13", "2025-03-31", 650),
                 H("h3", "2025-04-01", "2025-07-05", 650)]),
    case("F007", [("l1", "2025-07-06", 50)],
         [("p1", "2023-01-02", "2023-07-30", None, PAY), ("p2", "2025-01-13", "2025-07-05", None, PAY)], std("F007"),
         breaks=[("b1", "2023-07-31", "2025-01-12", ())], precedes=[("p1", "b1")], lfacts=REC + CAS,
         blocks=[H("h1", "2024-07-06", "2025-01-12", 0), H("h2", "2025-01-13", "2025-03-31", 650),
                 H("h3", "2025-04-01", "2025-07-05", 650)]),
    case("F008", [("l1", "2025-07-06", 50)],
         [("p1", "2023-01-02", "2023-05-21", None, PAY), ("p2", "2025-01-13", "2025-07-05", None, PAY)], std("F008"),
         breaks=[("b1", "2023-05-22", "2025-01-12", ())], precedes=[("p1", "b1")], lfacts=REC + CAS,
         blocks=[H("h1", "2024-07-06", "2025-01-12", 0), H("h2", "2025-01-13", "2025-03-31", 650),
                 H("h3", "2025-04-01", "2025-07-05", 650)]),
    case("F009", [("l1", "2025-07-06", 50)],
         [("p1", "2016-01-04", "2016-07-03", None, PAY), ("p2", "2025-01-06", "2025-07-05", None, PAY)], std("F009"),
         breaks=[("b1", "2016-07-04", "2025-01-05", ())], precedes=[("p1", "b1")], lfacts=REC + CAS,
         blocks=[H("h1", "2024-07-06", "2025-01-05", 0), H("h2", "2025-01-06", "2025-03-31", 650),
                 H("h3", "2025-04-01", "2025-07-05", 650)]),
    case("F010", [("l1", "2025-07-06", 50)],
         [("p1", "2016-01-04", "2016-07-03", None, PAY), ("p2", "2025-01-06", "2025-07-05", None, PAY)], std("F010"),
         breaks=[("b1", "2016-07-04", "2025-01-05", ())], precedes=[("p1", "b1")],
         lfacts=REC + CAS + ("practice",),
         blocks=[H("h1", "2024-07-06", "2025-01-05", 0), H("h2", "2025-01-06", "2025-03-31", 650),
                 H("h3", "2025-04-01", "2025-07-05", 650)],
         judgement=["practice true: the stated practice (count employment before personal-travel breaks of any "
                    "length) covers this personal-travel break"]),
    case("F011", [("l1", "2025-07-06", 50)],
         [("p1", "2016-01-04", "2016-07-03", None, PAY), ("p2", "2025-01-06", "2025-07-05", None, PAY)], std("F011"),
         breaks=[("b1", "2016-07-04", "2025-01-05", ("b_rehire",))], precedes=[("p1", "b1")], lfacts=REC + CAS,
         blocks=[H("h1", "2024-07-06", "2025-01-05", 0), H("h2", "2025-01-06", "2025-03-31", 650),
                 H("h3", "2025-04-01", "2025-07-05", 650)]),
    # --- USERRA breaks: the break, its absence period (R2) and the but-for hours (c)(2) ------------------------------
    case("F012", [("l1", "2025-07-01", 50)],
         [("p1", "2016-01-01", "2016-01-31", None, PAY), ("u1", "2016-02-01", "2025-03-31", None, USERRA_ABS),
          ("p2", "2025-04-01", "2025-06-30", None, PAY)], std("F012"),
         breaks=[("b1", "2016-02-01", "2025-03-31", ("b_userra",))], precedes=[("p1", "b1")],
         blocks=[H("h1", "2024-07-01", "2025-03-31", 0), H("h2", "2025-04-01", "2025-05-31", 100),
                 H("h3", "2025-06-01", "2025-06-30", 50), H("h4", "2024-07-01", "2025-03-31", 1100, "h_userra")]),
    case("F013", [("l1", "2025-07-01", 50)],
         [("p1", "2024-07-01", "2024-08-31", None, PAY), ("u1", "2024-09-01", "2025-05-31", None, USERRA_ABS),
          ("p2", "2025-06-01", "2025-06-30", None, PAY)], std("F013"),
         breaks=[("b1", "2024-09-01", "2025-05-31", ("b_userra",))], precedes=[("p1", "b1")],
         blocks=[H("h1", "2024-07-01", "2024-08-31", 300), H("h2", "2024-09-01", "2025-05-31", 0),
                 H("h3", "2025-06-01", "2025-06-30", 150), H("h4", "2024-09-01", "2025-05-31", 800, "h_userra")]),
    case("F014", [("l1", "2025-07-01", 50)],
         [("p1", "2023-01-01", "2025-03-31", None, PAY), ("u1", "2025-04-01", "2025-05-31", None, USERRA_ABS),
          ("p2", "2025-06-01", "2025-06-30", None, PAY)], std("F014"),
         breaks=[("b1", "2025-04-01", "2025-05-31", ("b_userra",))], precedes=[("p1", "b1")],
         blocks=[H("h1", "2024-07-01", "2024-12-31", 600), H("h2", "2025-01-01", "2025-03-31", 400),
                 H("h3", "2025-04-01", "2025-05-31", 0), H("h4", "2025-06-01", "2025-06-30", 50),
                 H("h5", "2025-04-01", "2025-05-31", 200, "h_userra")]),
    case("F015", [("l1", "2025-07-01", 50)],
         [("p1", "2023-01-01", "2025-03-31", None, PAY), ("u1", "2025-04-01", "2025-05-31", None, USERRA_ABS),
          ("p2", "2025-06-01", "2025-06-30", None, PAY)], std("F015"),
         breaks=[("b1", "2025-04-01", "2025-05-31", ("b_userra",))], precedes=[("p1", "b1")],
         blocks=[H("h1", "2024-07-01", "2024-12-31", 600), H("h2", "2025-01-01", "2025-03-31", 400),
                 H("h3", "2025-04-01", "2025-05-31", 0), H("h4", "2025-06-01", "2025-06-30", 49),
                 H("h5", "2025-04-01", "2025-05-31", 200, "h_userra")]),
    # --- payroll weeks during leave (b)(3) ---------------------------------------------------------------------------
    case("F016", [("l1", "2025-07-01", 50)], [("p1", "2023-01-01", "2025-06-30", None, PAY)], std("F016"),
         blocks=[H("h1", "2024-07-01", "2024-12-31", 600), H("h2", "2025-01-01", "2025-03-31", 400),
                 H("h3", "2025-04-01", "2025-05-31", 0), H("h4", "2025-06-01", "2025-06-30", 50)]),
    # --- no accurate record (c)(3): the stated judgment --------------------------------------------------------------
    case("F017", [("l1", "2026-01-01", 50)], [("p1", "2024-01-01", "2025-12-31", None, PAY)], std("F017"), lfacts=(),
         blocks=[H("h1", "2025-01-01", "2025-06-30", 600), H("h2", "2025-07-01", "2025-12-31", 649)],
         judgement=[NOREC_J]),
    case("F018", [("l1", "2026-01-01", 50)], [("p1", "2024-01-01", "2025-12-31", None, PAY)], std("F018"),
         lfacts=("shows_below",),
         blocks=[H("h1", "2025-01-01", "2025-06-30", 600), H("h2", "2025-07-01", "2025-12-31", 649)],
         judgement=[NOREC_J]),
    case("F019", [("l1", "2026-01-01", 50)], [("p1", "2024-01-01", "2025-12-31", None, PAY)], std("F019"), lfacts=(),
         blocks=[H("h1", "2025-01-01", "2025-06-30", 600), H("h2", "2025-07-01", "2025-12-31", 600)],
         judgement=[NOREC_J]),
    case("F020", [("l1", "2026-01-01", 50)], [("p1", "2024-01-01", "2025-12-31", None, PAY)], std("F020"),
         lfacts=("shows_below",),
         blocks=[H("h1", "2025-01-01", "2025-06-30", 600), H("h2", "2025-07-01", "2025-12-31", 600)],
         judgement=[NOREC_J]),
    case("F021", [("l1", "2026-11-01", 50)], [("p1", "2026-02-01", "2026-10-31", None, PAY)], std("F021"), lfacts=(),
         blocks=[H("h1", "2025-11-01", "2026-01-31", 0), H("h2", "2026-02-01", "2026-06-30", 600),
                 H("h3", "2026-07-01", "2026-10-31", 649)],
         judgement=[NOREC_J]),
    case("F022", [("l1", "2026-01-01", 50)], [("p1", "2024-01-01", "2025-12-31", None, PAY)], std("F022"),
         blocks=[H("h1", "2025-01-01", "2025-06-30", 650), H("h2", "2025-07-01", "2025-12-31", 650)],
         judgement=["compensation-agreement hours not entered (c)(1): only the recorded actual hours are blocks"]),
    case("F023", [("l1", "2026-01-01", 50)], [("p1", "2024-01-01", "2025-12-31", None, PAY)], std("F023"),
         blocks=[H("h1", "2025-01-01", "2025-06-30", 600), H("h2", "2025-07-01", "2025-11-30", 600),
                 H("h3", "2025-12-01", "2025-12-31", 0)]),
    # --- the employee count on the notice day (e) --------------------------------------------------------------------
    case("F024", [("l1", "2026-01-01", 50)], [("p1", "2024-01-01", "2025-12-31", None, PAY)], site3("F024"),
         blocks=[H("h1", "2025-01-01", "2025-06-30", 600), H("h2", "2025-07-01", "2025-12-31", 650)]),
    case("F025", [("l1", "2026-01-01", 49)], [("p1", "2024-01-01", "2025-12-31", None, PAY)], site3("F025"),
         blocks=[H("h1", "2025-01-01", "2025-06-30", 600), H("h2", "2025-07-01", "2025-12-31", 650)]),
    case("F026", [("l1", "2026-01-01", 50)], [("p1", "2024-01-01", "2025-12-31", None, PAY)], site3("F026"),
         blocks=[H("h1", "2025-01-01", "2025-06-30", 600), H("h2", "2025-07-01", "2025-12-31", 650)],
         judgement=["intermittent episodes under one notice: one leave item at the first episode (2026-01-01)"]),
    case("F027", [("l1", "2026-01-01", 49)], [("p1", "2024-01-01", "2025-12-31", None, PAY)], site3("F027"),
         blocks=[H("h1", "2025-01-01", "2025-06-30", 600), H("h2", "2025-07-01", "2025-12-31", 650)],
         judgement=["intermittent episodes under one notice: one leave item at the first episode (2026-01-01)"]),
    case("F028", [("l1", "2026-01-01", 50)], [("p1", "2025-01-01", "2025-12-31", None, PAY)], std("F028"),
         blocks=[H("h1", "2025-01-01", "2025-06-30", 600), H("h2", "2025-07-01", "2025-12-31", 650)]),
    # --- the leave's start (d) ---------------------------------------------------------------------------------------
    case("F029", [("l1", "2025-12-15", 50)], [("p1", "2025-01-01", "2025-12-14", None, PAY)], std("F029"),
         blocks=[H("h1", "2024-12-15", "2024-12-31", 0), H("h2", "2025-01-01", "2025-06-30", 600),
                 H("h3", "2025-07-01", "2025-12-14", 650)]),
    case("F030", [("l1", "2026-01-01", 50)], [("p1", "2025-01-01", "2025-12-31", None, PAY)], std("F030"),
         blocks=[H("h1", "2025-01-01", "2025-06-30", 600), H("h2", "2025-07-01", "2025-12-14", 650),
                 H("h3", "2025-12-15", "2025-12-31", 0)],
         judgement=["leave item starts at the requested FMLA portion (2026-01-01), as the question asks; the absence "
                    "from 2025-12-15 is payroll time in p1"]),
    case("F031", [("l1", "2026-01-01", 50)], [("p1", "2024-01-01", "2025-12-31", None, PAY)], q2("F031"),
         blocks=[H("h1", "2025-01-01", "2025-06-30", 600), H("h2", "2025-07-01", "2025-11-30", 600),
                 H("h3", "2025-12-01", "2025-12-31", 50), H("h4", "2024-12-01", "2024-12-31", 0)]),
    case("F032", [("l1", "2026-01-01", 50)], [("p1", "2024-01-01", "2025-12-31", None, PAY)], q2("F032"),
         blocks=[H("h1", "2025-01-01", "2025-06-30", 600), H("h2", "2025-07-01", "2025-10-31", 600),
                 H("h3", "2025-11-01", "2025-12-31", 49), H("h4", "2024-11-01", "2024-12-31", 200)]),
    case("F033", [("l1", "2026-01-01", 49)], [("p1", "2024-01-01", "2025-12-31", None, PAY)], q2("F033"),
         blocks=[H("h1", "2025-01-01", "2025-06-30", 600), H("h2", "2025-07-01", "2025-12-31", 650)],
         judgement=["the earlier September notice and October leave are not an item; count is the December "
                    "notice day's (separate need)"]),
    case("F034", [("l1", "2025-07-06", 50)],
         [("p1", "2016-01-04", "2016-04-03", None, PAY), ("p2", "2016-04-11", "2016-07-10", None, PAY),
          ("p3", "2025-01-06", "2025-07-05", None, PAY)], q2("F034"),
         breaks=[("b1", "2016-04-04", "2016-04-10", ()), ("b2", "2016-07-11", "2025-01-05", ())],
         precedes=[("p1", "b1"), ("p1", "b2"), ("p2", "b2")], lfacts=REC + CAS + ("practice",),
         blocks=[H("h1", "2024-07-06", "2025-01-05", 0), H("h2", "2025-01-06", "2025-03-31", 650),
                 H("h3", "2025-04-01", "2025-07-05", 650)],
         judgement=["practice true: the stated practice (count employment before education breaks of any length) "
                    "covers the long break b2, an education break"]),
    case("F035", [("l1", "2026-02-01", 50)], [("p1", "2024-01-01", "2026-01-31", None, PAY)], q2("F035"),
         blocks=[H("h1", "2025-02-01", "2025-07-31", 600), H("h2", "2025-08-01", "2025-12-31", 600),
                 H("h3", "2026-01-01", "2026-01-31", 50), H("h4", "2025-01-01", "2025-01-31", 100)],
         judgement=["leave item starts 2026-02-01 as the question asks; count is the 2025-12-01 notice day's (the "
                    "February episode is under that notice)"]),
]

PROBES = {
    "F036": "airline flight crew: 825.801's special hours rule, outside the pinned section",
    "F037": "worksite outside the U.S. (825.105(b), not pinned)",
    "F038": "covered-employer question (825.104, not pinned; a fixed fact of the test)",
    "F039": "amount of leave (825.200, not pinned)",
    "F040": "paid or unpaid leave (825.207, not pinned)",
    "F041": "airline flight crew special hours threshold (825.801, not pinned)",
    "F042": "worksite outside the U.S. (825.105(b), not pinned)",
    "F043": "covered-employer question (825.104, not pinned; a fixed fact of the test)",
}
PROBE_QIDS = {
    "F036": ["F036-1", "F036-2"], "F037": ["F037-1"], "F038": ["F038-1"], "F039": ["F039-1"], "F040": ["F040-1"],
    "F041": ["F041-1"], "F042": ["F042-1"], "F043": ["F043-1"],
}
UNSUPPORTED = {}


def write_bridge_inputs(path=HERE / "bridge" / "inputs.jsonl"):
    rows = [json.dumps({"case": c["id"], "item": item, **r}, sort_keys=True)
            for c in CASES for item, r in c["bridge"].items()]
    Path(path).write_text("".join(x + "\n" for x in rows), encoding="utf-8")
    return len(rows)


if __name__ == "__main__":
    print(write_bridge_inputs(), "bridge input rows")
