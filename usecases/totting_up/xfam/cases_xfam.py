"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). TEMPLATE for the cross-family encoder: the build's helpers and conventions, records removed.

Each case: one conviction item v1 (conviction date, latest offence date, points, facts satisfied / declines);
"offences" [(item, facts, unknown facts)]; "prevs" [(item, date imposed, {period ints}, facts)] (every previous
disqualification the case names; "prior" added for each); "circs" [(item, earlier occasion date or None, facts)];
"questions" [(qid, form, args)]; "judgement" (anything the encoder decided beyond copying a stated fact: listed as "encoder
judgement"). Bridge input (bridge/inputs.jsonl) = each previous disqualification's date with the latest offence's date, and
each earlier occasion's date with the conviction's date, copied from the facts (encode.bridge_inputs; write_bridge_inputs()).
PROBES: out-of-scope cases (every answer UNSUPPORTED). UNSUPPORTED: none.
Period facts: a period "of N days" -> in_days, based N, extd (the extension's days, 0 when the case says "with no extension
period"); "of N months" -> in_months, basem N (extd N when an extension in days is added); "of N year(s)" -> in_years, basey N;
an extension under a named section -> ext + ext_<section>.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENC = HERE / "questions-enc.jsonl" if (HERE / "questions-enc.jsonl").exists() else HERE.parent / "questions-enc.jsonl"
ENC_SHA256 = "2fc92d25ba27a63508b144c79acdb5d55f9d136fe59f144aeeb65b56d54f27fa"
if hashlib.sha256(ENC.read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

DE = ("disc", "oend")  # "an offence involving discretionary disqualification and obligatory endorsement"


def case(cid, conv, lo, pts, offences, qs, prevs=(), circs=(), vfacts=(), judgement=()):
    facts, unknown, ints = {"v1": list(vfacts)}, {}, {"conv_v1": conv, "lo_v1": lo, "pts_v1": pts}
    for o, fl, unk in offences:
        facts[o] = list(fl)
        if unk:
            unknown[o] = list(unk)
    for p, imp, base, fl in prevs:
        facts[p] = ["prior"] + list(fl)
        ints[f"imp_{p}"] = imp
        ints.update({f"{k}_{p}": v for k, v in base.items()})
    for c, occ, fl in circs:
        facts[c] = list(fl)
        if occ:
            ints[f"occ_{c}"] = occ
    return {"id": cid, "convictions": ["v1"], "offences": {o[0]: "v1" for o in offences},
            "prevs": {p[0]: "v1" for p in prevs}, "circs": {c[0]: "v1" for c in circs}, "facts": facts,
            "unknown": unknown, "ints": ints, "tot_stated": [],
            "questions": [{"qid": q, "form": f, "args": a} for (q, f, a) in qs], "judgement": list(judgement)}


def one(o="o1", fl=DE, unk=()):
    return [(o, fl, unk)]


def q12(cid):
    return [(f"{cid}-1", "must", ["v1"]), (f"{cid}-2", "minimum", ["v1"])]


def q3(qid, p):
    return (qid, "counts", [p, "v1"])


def q4(qid, c):
    return (qid, "may", [c, "v1"])


def M(n):
    return ({"basem": n}, ["fixed", "in_months"])


def Y(n):
    return ({"basey": n}, ["fixed", "in_years"])


def Dd(n, ext=0, *sec):
    fl = ["fixed", "in_days"] + (["ext"] + [f"ext_{s}" for s in sec] if ext else [])
    return ({"based": n, "extd": ext}, fl)


def P(p, imp, period, *extra):
    base, fl = period
    return (p, imp, base, fl + list(extra))


def Dt(total, ext, *sec):
    """A period "of N days" that the facts say INCLUDED an extension of E days: the total N is the stated figure
    (record's tot_stated; the period without the extension is derived by the build, not typed)."""
    return ({"totd": total, "extd": ext}, ["fixed", "in_days", "ext"] + [f"ext_{s}" for s in sec])


NOFIX = ({}, [])  # a previous disqualification with no fixed period ordered


def tot(rec, *ps):
    rec["tot_stated"] = list(ps)
    return rec


def unk(rec, item, *fs):
    rec["unknown"][item] = list(fs)
    return rec


CV, LO = "2026-09-01", "2026-06-01"
HCE = ["hardship", "exceptional"]

CASES = [
    case("Z001", CV, LO, 11, one(), q12("Z001")),
    case("Z002", CV, LO, 12, one(), q12("Z002") + [q4("Z002-3", "c1")], circs=[("c1", None, HCE)]),
    case("Z003", CV, LO, 13, one(), q12("Z003") + [q4("Z003-3", "c1")], circs=[("c1", None, ["nserious"])]),
    case("Z004", CV, LO, 12, one(), q12("Z004") + [q3("Z004-3", "p1")], prevs=[P("p1", "2024-07-01", Dd(55))]),
    case("Z005", CV, LO, 12, one(), q12("Z005") + [q3("Z005-3", "p1")], prevs=[P("p1", "2024-07-01", Dd(56))]),
    case("Z006", CV, LO, 12, one(), q12("Z006") + [q3("Z006-3", "p1")], prevs=[P("p1", "2023-06-02", Dd(90))]),
    case("Z007", CV, LO, 12, one(), q12("Z007") + [q3("Z007-3", "p1")], prevs=[P("p1", "2023-05-31", Dd(90))]),
    case("Z008", CV, LO, 12, one(), q12("Z008") + [q3("Z008-3", "p1")], prevs=[P("p1", "2026-07-01", Dd(90))]),
    case("Z009", CV, LO, 12, one(), q12("Z009") + [q3("Z009-3", "p1"), q3("Z009-4", "p2")],
         prevs=[P("p1", "2023-07-01", M(2)), P("p2", "2024-08-01", Y(1))]),
    case("Z010", CV, LO, 13, one(), q12("Z010") + [q3("Z010-3", "p1"), q3("Z010-4", "p2"), q3("Z010-5", "p3")],
         prevs=[P("p1", "2023-07-01", Dd(56)), P("p2", "2024-07-01", Dd(90)), P("p3", "2025-07-01", Dd(120))]),
    tot(case("Z011", CV, LO, 12, one(), q12("Z011") + [q3("Z011-3", "p1")],
             prevs=[P("p1", "2024-07-01", Dt(60, 5, "35a"))],
             judgement=["Z011 p1: 'fixed period of 60 days' that 'included' a 5-day extension read as total 60 (tot_stated)"]),
        "p1"),
    tot(case("Z012", CV, LO, 12, one(), q12("Z012") + [q3("Z012-3", "p1")],
             prevs=[P("p1", "2024-07-01", Dt(60, 5, "35c"))],
             judgement=["Z012 p1: 'fixed period of 60 days' that 'included' a 5-day extension read as total 60 (tot_stated)"]),
        "p1"),
    tot(case("Z013", CV, LO, 12, one(), q12("Z013") + [q3("Z013-3", "p1")],
             prevs=[P("p1", "2024-07-01", Dt(60, 5, "248d"))],
             judgement=["Z013 p1: 'fixed period of 60 days' that 'included' a 5-day extension read as total 60 (tot_stated)"]),
        "p1"),
    tot(case("Z014", CV, LO, 12, one(), q12("Z014") + [q3("Z014-3", "p1")],
             prevs=[P("p1", "2024-07-01", Dt(60, 5, "147a"))],
             judgement=["Z014 p1: 'fixed period of 60 days' that 'included' a 5-day extension read as total 60 (tot_stated)"]),
        "p1"),
    tot(case("Z015", CV, LO, 12, one(), q12("Z015") + [q3("Z015-3", "p1")],
             prevs=[P("p1", "2024-07-01", Dt(60, 5, "166"))],
             judgement=["Z015 p1: 'fixed period of 60 days' that 'included' a 5-day extension read as total 60 (tot_stated)"]),
        "p1"),
    tot(case("Z016", CV, LO, 12, one(), q12("Z016") + [q3("Z016-3", "p1")],
             prevs=[P("p1", "2024-07-01", Dt(60, 4, "35a"))],
             judgement=["Z016 p1: 'fixed period of 60 days' that 'included' a 4-day extension read as total 60 (tot_stated)"]),
        "p1"),
    case("Z017", CV, LO, 12, one(), q12("Z017") + [q3("Z017-3", "p1")],
         prevs=[P("p1", "2024-07-01", Dd(90), "u_s26")]),
    case("Z018", CV, LO, 12, one(), q12("Z018") + [q3("Z018-3", "p1")],
         prevs=[P("p1", "2024-07-01", Dd(90), "u_s147")]),
    case("Z019", CV, LO, 12, one(), q12("Z019") + [q3("Z019-3", "p1")],
         prevs=[P("p1", "2024-07-01", Dd(90), "u_s164")]),
    case("Z020", CV, LO, 12, one(), q12("Z020") + [q3("Z020-3", "p1")],
         prevs=[P("p1", "2024-07-01", Dd(90), "u_223a")]),
    case("Z021", CV, LO, 12, one(), q12("Z021") + [q3("Z021-3", "p1")],
         prevs=[P("p1", "2024-07-01", Dd(90), "u_436a")]),
    case("Z022", CV, LO, 12, one(), q12("Z022") + [q3("Z022-3", "p1")],
         prevs=[P("p1", "2024-07-01", Dd(90), "o_steal")]),
    case("Z023", CV, LO, 12, one(), q12("Z023") + [q3("Z023-3", "p1")],
         prevs=[P("p1", "2024-07-01", Dd(90), "o_ta12")]),
    case("Z024", CV, LO, 12, one(), q12("Z024") + [q3("Z024-3", "p1")],
         prevs=[P("p1", "2024-07-01", Dd(90), "o_ta25")]),
    case("Z025", CV, LO, 12, one(), q12("Z025") + [q3("Z025-3", "p1")],
         prevs=[P("p1", "2024-07-01", Dd(90), "o_rta178")]),
    case("Z026", CV, LO, 12, one(),
         q12("Z026") + [q3("Z026-3", "p1"), q3("Z026-4", "p2"), q3("Z026-5", "p3"), q3("Z026-6", "p4")],
         prevs=[P("p1", "2023-07-01", Dd(90), "attempt", "o_steal"), P("p2", "2024-01-01", Dd(90), "attempt", "o_ta12"),
                P("p3", "2024-07-01", Dd(90), "attempt", "o_ta25"), P("p4", "2025-01-01", Dd(90), "attempt", "o_rta178")]),
    case("Z027", CV, LO, 12, one("o1") + one("o2"), q12("Z027") + [q4("Z027-3", "c1")], circs=[("c1", None, [])],
         judgement=["Z027 c1: 'also committed the other offence of the occasion' asked in Q4 made a circumstance item with "
                    "no (4) fact (not hardship, not alleged to make the offence not serious, not taken earlier)"]),
    case("Z028", CV, LO, 12, one(fl=("oblig", "oend", "aid", "aid_oblig", "s34")), q12("Z028")),
    case("Z029", CV, LO, 12, one(fl=("oblig",)), q12("Z029"),
         judgement=["Z029 o1: 'an offence involving obligatory disqualification' read as not one involving discretionary "
                    "disqualification; obligatory endorsement not stated, false under C1"]),
    case("Z030", CV, LO, 12, one(fl=("oblig", "s34")), q12("Z030"),
         judgement=["Z030 o1: 'an offence involving obligatory disqualification' read as not one involving discretionary "
                    "disqualification; obligatory endorsement not stated, false under C1"]),
    unk(case("Z031", CV, LO, 12, one(), q12("Z031") + [q4("Z031-3", "c1")], circs=[("c1", None, HCE)],
             vfacts=["satisfied"],
             judgement=["Z031: 'thinks fit not to order' read as not declining (declines false); whether the satisfaction "
                        "rests on c1 is not stated (rests unknown)"]),
        "c1", "rests"),
    case("Z032", CV, LO, 12, one(), q12("Z032") + [q4("Z032-3", "c1")], circs=[("c1", None, ["hardship"])]),
    case("Z033", CV, LO, 12, one(), q12("Z033") + [q4("Z033-3", "c1")],
         circs=[("c1", "2023-09-02", HCE + ["taken"])]),
    unk(case("Z034", CV, LO, 12, one(), q12("Z034") + [q4("Z034-3", "c1")],
             circs=[("c1", "2023-08-31", HCE + ["taken"])], vfacts=["satisfied"],
             judgement=["Z034: 'thinks fit to order ... 3 months' read as not declining (declines false); whether the "
                        "satisfaction rests on c1 is not stated (rests unknown)"]),
        "c1", "rests"),
    case("Z035", CV, LO, 12, one(), q12("Z035") + [q3("Z035-3", "p1")], prevs=[P("p1", "2024-07-01", NOFIX)]),
]

PROBES = {
    "Z036": "probe: out of scope; whether the offence involves obligatory endorsement is not stated ((1A)(a) open)",
    "Z037": "probe: out of scope; the penalty points to be taken into account are not stated (s.29 not pinned)",
    "Z038": "probe: out of scope; which offences supply points under s.29 and their number are not stated (s.29 not pinned)",
    "Z039": "probe: out of scope; a court in Scotland (C5: England and Wales only; (6) out)",
    "Z040": "probe: out of scope; a court in Northern Ireland (the section does not extend there)",
    "Z041": "probe: out of scope; a licence revocation under the New Drivers Act 1995 is not a disqualification item",
    "Z042": "probe: out of scope; (3)(c) treatment for the purposes of an appeal is not written",
}
PROBE_QIDS = {}
UNSUPPORTED = {}
for _line in ENC.read_text(encoding="utf-8").splitlines():
    _r = json.loads(_line)
    if _r["scope"] == "out":
        PROBE_QIDS[_r["id"]] = [x["qid"] for x in _r["questions"]]


def write_bridge_inputs():
    import encode as E
    rows = [r for c in CASES for r in E.bridge_inputs(c)]
    (HERE / "bridge" / "inputs.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows),
                                                  encoding="utf-8")
    return len(rows)


if __name__ == "__main__":
    print(write_bridge_inputs(), "bridge input rows")
