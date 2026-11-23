"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). SAME-FAMILY.

Encoder: dri-statute-corpus-fmla-eligibility-1123 (Opus 5.5), after the translation was committed (92e36c119b).
Each case: "leaves" [(item, start day, employee count on the notice day)], "periods" [(item, first day, last day, stated
weeks or None = bridged weeks, facts)], "breaks" [(item, first day, last day, facts)], "blocks" [(item, first day, last
day, hours, fact)], "lfacts" (facts true for every leave item: acct, acc_record, casual, practice, shows_below),
"precedes" [(period, break)], "period_for" (default: every period for every leave), "questions" [(qid, leave, form)],
"judgement" (anything the encoder decided beyond copying a stated fact: listed as "encoder judgement").
Bridge input (bridge/inputs.jsonl) = every leave's start (window) and every period's and break's first and last day
(duration), copied from the facts; written by write_bridge_inputs().
PROBES: out-of-scope cases (every answer UNSUPPORTED). UNSUPPORTED: none.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "0e1fd64d29a0b1b2bd3c89c15840b11a7d1c5cca140268f662bb5baafa499562"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

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


CASES = [
    case("F001", [("l1", "2026-03-02", 120)], [("s1", "2025-01-06", "2026-03-01", 60, PAY)], std("F001"),
         blocks=[H("h1", "2025-01-06", "2025-03-01", "330"), H("h2", "2025-03-02", "2025-08-31", "820"),
                 H("h3", "2025-09-01", "2026-03-01", "790")]),
    case("F002", [("l1", "2026-07-06", 75)],
         [("s1", "2025-03-31", "2025-09-28", 26, PAY), ("s2", "2026-01-05", "2026-07-05", 26, PAY)], std("F002"),
         breaks=[("b1", "2025-09-29", "2026-01-04", ())], precedes=[("s1", "b1")], lfacts=REC + ("casual",),
         blocks=[H("h1", "2025-03-31", "2025-07-05", "480"), H("h2", "2025-07-06", "2025-09-28", "450"),
                 H("h3", "2026-01-05", "2026-07-05", "850")]),
    case("F003", [("l1", "2026-07-06", 75)],
         [("s1", "2025-03-31", "2025-09-28", 26, PAY), ("s2", "2026-01-12", "2026-07-05", 25, PAY)], std("F003"),
         breaks=[("b1", "2025-09-29", "2026-01-11", ())], precedes=[("s1", "b1")], lfacts=REC + ("casual",),
         blocks=[H("h1", "2025-03-31", "2025-07-05", "500"), H("h2", "2025-07-06", "2025-09-28", "470"),
                 H("h3", "2026-01-12", "2026-07-05", "830")]),
    case("F004", [("l1", "2026-03-02", 90)],
         [("s1", "2020-03-02", "2020-11-01", 35, PAY), ("s2", "2025-09-01", "2026-03-01", 26, PAY)], std("F004"),
         breaks=[("b1", "2020-11-02", "2025-08-31", ())], precedes=[("s1", "b1")],
         blocks=[H("h1", "2020-03-02", "2020-11-01", "1300"), H("h2", "2025-09-01", "2026-03-01", "1310")]),
    case("F005", [("l1", "2026-03-02", 90)],
         [("s1", "2012-01-02", "2017-06-25", 286, PAY), ("s2", "2025-06-30", "2026-03-01", 35, PAY)], std("F005"),
         breaks=[("b1", "2017-06-26", "2025-06-29", ())], precedes=[("s1", "b1")],
         blocks=[H("h1", "2025-06-30", "2026-03-01", "1480")]),
    case("F006", [("l1", "2026-06-01", 65)],
         [("s1", "2014-02-03", "2017-10-01", 191, PAY), ("s2", "2017-10-02", "2026-02-01", None, USERRA_ABS),
          ("s3", "2026-02-02", "2026-05-31", 17, PAY)], std("F006"),
         breaks=[("b1", "2017-10-02", "2026-02-01", ("b_userra",))], precedes=[("s1", "b1")],
         blocks=[H("h1", "2026-02-02", "2026-05-31", "700"), H("h2", "2025-06-01", "2026-02-01", "550", "h_userra")],
         judgement=["F006: the USERRA absence (2 Oct 2017 - 1 Feb 2026) is both the break in service and a period counted "
                    "for the 12 months (R2); its weeks come from the bridge (K)"]),
    case("F007", [("l1", "2026-06-01", 80)],
         [("s1", "2017-08-28", "2018-06-03", 40, PAY), ("s2", "2026-02-16", "2026-05-31", 15, PAY)], std("F007"),
         breaks=[("b1", "2018-06-04", "2026-02-15", ("b_rehire",))], precedes=[("s1", "b1")],
         blocks=[H("h1", "2026-02-16", "2026-05-31", "640")]),
    case("F008", [("l1", "2026-06-01", 50)],
         [("s1", "2014-01-06", "2014-08-03", 30, PAY), ("s2", "2025-10-13", "2026-05-31", 33, PAY)],
         std("F008") + [("F008-4", "l1", "site")],
         breaks=[("b1", "2014-08-04", "2025-10-12", ("b_rehire",))], precedes=[("s1", "b1")],
         blocks=[H("h1", "2025-10-13", "2026-05-31", "1320")],
         judgement=["F008: the collective bargaining agreement stating the employer's intention to rehire employees who "
                    "leave for childrearing read as a written agreement concerning its intention to rehire Hugo (b)(2)(ii)"]),
    case("F009", [("l1", "2026-08-03", 300)],
         [("s1", "2015-01-05", "2015-11-15", 45, PAY), ("s2", "2026-01-05", "2026-08-02", 30, PAY)], std("F009"),
         breaks=[("b1", "2015-11-16", "2026-01-04", ())], precedes=[("s1", "b1")], lfacts=REC + ("practice",),
         blocks=[H("h1", "2026-01-05", "2026-08-02", "1280")]),
    case("F010", [("l1", "2026-06-01", 300)],
         [("s1", "2013-01-07", "2013-08-04", 30, PAY), ("s2", "2025-11-17", "2026-05-31", 28, PAY)], std("F010"),
         breaks=[("b1", "2013-08-05", "2025-11-16", ())], precedes=[("s1", "b1")], lfacts=REC + ("practice",),
         blocks=[H("h1", "2025-11-17", "2026-05-31", "1260")],
         judgement=["F010: 'the employer's practice is to count employment before a continuous break of more than seven "
                    "years' copied as the practice fact; the HR manager's contrary decision for Jonas is not encoded (the "
                    "uniformity duty of (b)(4), not written, is what makes it irrelevant)"]),
    case("F011", [("l1", "2026-05-04", 140)], [("s1", "2025-01-06", "2026-05-03", 69, PAY)], std("F011"),
         blocks=[H("h1", "2025-01-06", "2025-05-03", "600"), H("h2", "2025-05-04", "2025-12-31", "830"),
                 H("h3", "2026-01-01", "2026-05-03", "419")]),
    case("F012", [("l1", "2026-05-04", 140)], [("s1", "2025-02-03", "2026-05-03", 65, PAY)], std("F012"),
         blocks=[H("h1", "2025-02-03", "2025-05-03", "480"), H("h2", "2025-05-04", "2025-10-31", "700"),
                 H("h3", "2025-11-01", "2026-05-03", "550")]),
    case("F013", [("l1", "2026-09-07", 70)], [("s1", "2024-09-02", "2026-09-06", 105, PAY)], std("F013"),
         blocks=[H("h1", "2024-09-02", "2025-09-06", "1900"), H("h2", "2025-09-07", "2026-03-06", "600"),
                 H("h3", "2026-03-07", "2026-09-06", "600")]),
    case("F014", [("l1", "2026-08-03", 95)], [("s1", "2024-03-04", "2026-08-02", 126, PAY)], std("F014"),
         blocks=[H("h1", "2024-03-04", "2025-05-31", "1500"), H("h2", "2025-06-01", "2025-08-02", "120"),
                 H("h3", "2025-08-03", "2026-05-31", "1100"), H("h4", "2026-06-01", "2026-08-02", "400")]),
    case("F015", [("l1", "2026-02-02", 200), ("l2", "2026-03-09", 200)],
         [("s1", "2025-03-03", "2026-02-01", 48, PAY), ("s2", "2026-02-02", "2026-03-08", 5, PAY)],
         [("F015-1", "l1", "eligible"), ("F015-2", "l1", "twelve"), ("F015-3", "l2", "twelve"),
          ("F015-4", "l2", "eligible")],
         period_for=[("s1", "l1"), ("s1", "l2"), ("s2", "l2")],
         blocks=[H("h1", "2025-03-03", "2025-03-08", "40"), H("h2", "2025-03-09", "2026-02-01", "1660"),
                 H("h3", "2026-02-02", "2026-03-08", "0")],
         judgement=["F015: leave item l2 = the part of the one noticed leave from 9 March 2026 ((d) second sentence); "
                    "its employee count is the notice-day count (19 January 2026), as for l1"]),
    case("F016", [("l1", "2026-07-13", 58)],
         [("s1", "2025-04-07", "2025-08-24", 20, PAY), ("s2", "2025-12-01", "2026-04-19", 20, PAY),
          ("s3", "2026-04-20", "2026-07-12", 12, PAY)], std("F016"),
         breaks=[("b1", "2025-08-25", "2025-11-30", ())], precedes=[("s1", "b1")], lfacts=REC + ("casual",),
         blocks=[H("h1", "2025-04-07", "2025-07-12", "560"), H("h2", "2025-07-13", "2025-08-24", "300"),
                 H("h3", "2025-12-01", "2026-04-19", "980"), H("h4", "2026-04-20", "2026-07-12", "0")]),
    case("F017", [("l1", "2026-08-03", 52)],
         [("s1", "2025-06-02", "2025-12-28", 30, PAY), ("s2", "2026-03-02", "2026-08-02", 22, PAY)], std("F017"),
         breaks=[("b1", "2025-12-29", "2026-03-01", ())], precedes=[("s1", "b1")], lfacts=REC + ("casual",),
         blocks=[H("h1", "2025-06-02", "2025-08-02", "310"), H("h2", "2025-08-03", "2025-12-28", "560"),
                 H("h3", "2026-03-02", "2026-08-02", "720")],
         judgement=["F017: 'an on-call nursing aide' read as intermittent/occasional/casual employment ((b)(3) second "
                    "sentence)"]),
    case("F018", [("l1", "2026-03-02", 400)], [("s1", "2024-08-19", "2026-03-01", 80, PAY)], std("F018"), lfacts=(),
         judgement=["F018: the recorded classroom hours (1,080) are not an accurate accounting of hours worked: not "
                    "encoded as a block (the facts say the district does not maintain an accurate record)"]),
    case("F019", [("l1", "2026-09-07", 85)], [("s1", "2024-07-01", "2026-09-06", 114, PAY)], std("F019"),
         lfacts=("shows_below",)),
    case("F020", [("l1", "2026-05-04", 110)], [("s1", "2024-10-07", "2026-05-03", 82, PAY)], std("F020"),
         lfacts=("acct",), blocks=[H("h1", "2025-05-04", "2025-11-01", "680"), H("h2", "2025-11-02", "2026-05-03", "620")]),
    case("F021", [("l1", "2026-05-04", 49)], [("s1", "2023-01-02", "2026-05-03", 174, PAY)], site3("F021"),
         blocks=[H("h1", "2025-05-04", "2025-11-03", "880"), H("h2", "2025-11-04", "2026-05-03", "860")]),
    case("F022", [("l1", "2026-09-07", 50)], [("s1", "2023-01-02", "2026-09-06", 192, PAY)], site3("F022"),
         blocks=[H("h1", "2025-09-07", "2026-03-06", "900"), H("h2", "2026-03-07", "2026-09-06", "910")]),
    case("F023", [("l1", "2026-03-09", 55)], [("s1", "2024-01-01", "2026-03-08", 114, PAY)], site3("F023"),
         blocks=[H("h1", "2025-03-09", "2025-09-08", "950"), H("h2", "2025-09-09", "2026-03-08", "930")]),
    case("F024", [("l1", "2026-12-07", 60)], [("s1", "2025-06-02", "2026-12-06", 79, PAY)], site3("F024"),
         blocks=[H("h1", "2025-12-07", "2026-06-06", "1000"), H("h2", "2026-06-07", "2026-12-06", "1010")]),
    case("F025", [("l1", "2026-07-06", 49)], [("s1", "2022-01-03", "2026-07-05", 235, PAY)], site3("F025"),
         blocks=[H("h1", "2025-07-06", "2026-01-05", "940"), H("h2", "2026-01-06", "2026-07-05", "960")]),
    case("F026", [("l1", "2026-06-08", 75)],
         [("s1", "2024-07-01", "2025-01-26", 30, PAY), ("s2", "2025-01-27", "2026-03-29", None, USERRA_ABS),
          ("s3", "2026-03-30", "2026-06-07", 10, PAY)], std("F026"),
         breaks=[("b1", "2025-01-27", "2026-03-29", ("b_userra",))], precedes=[("s1", "b1")],
         blocks=[H("h1", "2026-03-30", "2026-06-07", "400"), H("h2", "2025-06-08", "2026-03-29", "1640", "h_userra")],
         judgement=["F026: the USERRA absence (27 Jan 2025 - 29 Mar 2026) is both the break and a period counted for the "
                    "12 months (R2); its weeks come from the bridge (K)"]),
    case("F027", [("l1", "2026-09-07", 90)],
         [("s1", "2016-01-04", "2018-09-30", 143, PAY), ("s2", "2018-10-01", "2026-02-15", None, USERRA_ABS),
          ("s3", "2026-02-16", "2026-09-06", 29, PAY)], std("F027"),
         breaks=[("b1", "2018-10-01", "2026-02-15", ("b_userra",))], precedes=[("s1", "b1")],
         blocks=[H("h1", "2026-02-16", "2026-09-06", "649"), H("h2", "2025-09-07", "2026-02-15", "600", "h_userra")],
         judgement=["F027: the USERRA absence is both the break and a period counted for the 12 months (R2); its weeks "
                    "come from the bridge (K)"]),
    case("F028", [("l1", "2026-10-05", 61)],
         [("s1", "2025-04-07", "2025-08-24", 20, PAY), ("s2", "2025-12-01", "2026-03-15", 15, PAY),
          ("s3", "2026-06-01", "2026-10-04", 18, PAY)], std("F028"),
         breaks=[("b1", "2025-08-25", "2025-11-30", ()), ("b2", "2026-03-16", "2026-05-31", ())],
         precedes=[("s1", "b1"), ("s1", "b2"), ("s2", "b2")], lfacts=REC + ("casual",),
         blocks=[H("h1", "2025-04-07", "2025-08-24", "700"), H("h2", "2025-12-01", "2026-03-15", "520"),
                 H("h3", "2026-06-01", "2026-10-04", "780")]),
    case("F029", [("l1", "2026-03-02", 66)],
         [("s1", "2010-01-04", "2011-06-26", 77, PAY), ("s2", "2025-01-06", "2026-03-01", 60, PAY)], std("F029"),
         breaks=[("b1", "2011-06-27", "2025-01-05", ())], precedes=[("s1", "b1")],
         blocks=[H("h1", "2025-01-06", "2025-03-01", "200"), H("h2", "2025-03-02", "2026-03-01", "1100")]),
    case("F030", [("l1", "2026-03-30", 150)],
         [("s1", "2014-01-06", "2014-10-12", 40, PAY), ("s2", "2023-01-16", "2023-06-04", 20, PAY),
          ("s3", "2025-09-01", "2026-03-29", 30, PAY)], std("F030"),
         breaks=[("b1", "2014-10-13", "2023-01-15", ()), ("b2", "2023-06-05", "2025-08-31", ())],
         precedes=[("s1", "b1"), ("s1", "b2"), ("s2", "b2")],
         blocks=[H("h1", "2025-09-01", "2026-03-29", "1350")]),
    case("F031", [("l1", "2026-03-30", 150)],
         [("s1", "2015-05-04", "2016-02-07", 40, PAY), ("s2", "2023-01-16", "2023-06-04", 20, PAY),
          ("s3", "2025-09-01", "2026-03-29", 30, PAY)], std("F031"),
         breaks=[("b1", "2016-02-08", "2023-01-15", ()), ("b2", "2023-06-05", "2025-08-31", ())],
         precedes=[("s1", "b1"), ("s1", "b2"), ("s2", "b2")],
         blocks=[H("h1", "2025-09-01", "2026-03-29", "1350")]),
    case("F032", [("l1", "2026-04-06", 52), ("l2", "2026-09-07", 45)],
         [("s1", "2023-01-02", "2026-04-05", None, PAY), ("s2", "2023-01-02", "2026-09-06", 192, PAY)],
         [("F032-1", "l1", "eligible"), ("F032-2", "l2", "twelve"), ("F032-3", "l2", "eligible"),
          ("F032-4", "l2", "site")],
         period_for=[("s1", "l1"), ("s2", "l2")],
         blocks=[H("h1", "2025-04-06", "2025-09-06", "900"), H("h2", "2025-09-07", "2026-04-05", "1000"),
                 H("h3", "2026-04-06", "2026-04-19", "0"), H("h4", "2026-04-20", "2026-09-06", "850")],
         judgement=["F032: for the first leave the employment up to 5 April 2026 is a period of its own whose weeks come "
                    "from the bridge (K); 'on the payroll in each of the 192 weeks' read as on the payroll in each of its "
                    "weeks"]),
    case("F033", [("l1", "2026-06-08", 70)], [("s1", "2025-06-02", "2026-06-07", 53, PAY)], std("F033"),
         blocks=[H("h1", "2025-06-02", "2025-06-07", "45"), H("h2", "2025-06-08", "2025-11-30", "1000"),
                 H("h3", "2025-12-01", "2026-06-07", "950")]),
    case("F034", [("l1", "2026-06-01", 88)], [("s1", "2023-01-02", "2026-05-31", 178, PAY)], std("F034"),
         blocks=[H("h1", "2025-03-02", "2025-05-31", "500"), H("h2", "2025-06-01", "2026-03-01", "900"),
                 H("h3", "2026-03-02", "2026-05-31", "200")]),
    case("F035", [("l1", "2026-06-08", 230)], [("s1", "2025-09-01", "2026-06-07", 40, PAY)], std("F035"), lfacts=()),
]

PROBES = {
    "F036": "airline flight crew employee (825.801: out of scope)",
    "F037": "airline flight crew employee (825.801: out of scope)",
    "F038": "employee working outside the United States (825.105(b): out of scope)",
    "F039": "employee working outside the United States (825.105(b): out of scope)",
    "F040": "whether the employer is a covered employer (825.104: out of scope)",
    "F041": "whether the employer is a covered employer (825.104: out of scope)",
    "F042": "the amount of leave (out of scope)",
    "F043": "pay during leave (out of scope)",
    "F044": "the amount of leave (out of scope)",
    "F045": "substitution of paid leave / its pay (out of scope)",
}
_ENC = [json.loads(x) for x in (HERE / "questions-enc.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
PROBE_QIDS = {c["id"]: [q["qid"] for q in c["questions"]] for c in _ENC if c["id"] in PROBES}
UNSUPPORTED = {}
assert {c["id"] for c in _ENC if c["scope"] == "out"} == set(PROBES)
assert sorted(q["qid"] for c in _ENC if c["scope"] == "in" for q in c["questions"]) == \
    sorted(q["qid"] for c in CASES for q in c["questions"])


def write_bridge_inputs(path=HERE / "bridge" / "inputs.jsonl"):
    rows = [json.dumps({"case": c["id"], "item": item, **r}, sort_keys=True)
            for c in CASES for item, r in c["bridge"].items()]
    Path(path).write_text("".join(x + "\n" for x in rows), encoding="utf-8")
    return len(rows)


if __name__ == "__main__":
    print(write_bridge_inputs(), "bridge input rows")
