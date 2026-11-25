"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). SAME-FAMILY.

Encoder: dri-statute-corpus-totting-up-1123 (Opus 5.5), after the translation was committed (bc8bc4f28d).
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
ENC_SHA256 = "535e08ad2fb8ffdd28be34bfaca86468dd27c97169414b23e120d9495b32075b"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
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


CASES = [
    case("Z001", "2026-03-14", "2026-01-02", 12, one(), q12("Z001") + [q4("Z001-3", "c1")],
         circs=[("c1", None, ["hardship"])]),
    case("Z002", "2026-06-09", "2026-02-20", 11, one(), q12("Z002"), prevs=[P("p1", "2024-06-05", M(6))]),
    case("Z003", "2026-05-02", "2026-01-20", 13, one(), q12("Z003") + [q3("Z003-3", "p1")],
         prevs=[P("p1", "2024-06-05", M(12))]),
    case("Z004", "2026-08-11", "2026-03-03", 14, one(), q12("Z004") + [q3("Z004-3", "p1"), q3("Z004-4", "p2")],
         prevs=[P("p1", "2023-09-01", M(6)), P("p2", "2025-02-10", M(6))]),
    case("Z005", "2026-10-07", "2026-05-14", 18, one(), q12("Z005") + [q4("Z005-3", "c1")],
         prevs=[P("p1", "2023-07-19", M(3)), P("p2", "2024-04-22", M(4)), P("p3", "2025-01-30", M(9))],
         circs=[("c1", None, ["nserious"])]),
    case("Z006", "2026-02-16", "2025-11-08", 12, one(), q12("Z006") + [q3("Z006-3", "p1")],
         prevs=[P("p1", "2025-04-01", Dd(55))]),
    case("Z007", "2026-02-16", "2025-11-08", 12, one(), q12("Z007") + [q3("Z007-3", "p1")],
         prevs=[P("p1", "2025-04-01", Dd(56))]),
    case("Z008", "2026-07-20", "2026-03-08", 12, one(), q12("Z008") + [q3("Z008-3", "p1")],
         prevs=[P("p1", "2023-03-09", M(6))]),
    case("Z009", "2026-07-20", "2026-03-08", 12, one(), q12("Z009") + [q3("Z009-3", "p1")],
         prevs=[P("p1", "2023-03-07", M(6))]),
    case("Z010", "2026-09-10", "2026-01-15", 13, one(), q12("Z010") + [q3("Z010-3", "p1")],
         prevs=[P("p1", "2023-01-02", M(12))]),
    case("Z011", "2026-10-01", "2025-04-04", 12, one(), q12("Z011") + [q3("Z011-3", "p1")],
         prevs=[P("p1", "2025-06-20", M(6))]),
    case("Z012", "2026-03-03", "2025-12-10", 12, one(), q12("Z012") + [q3("Z012-3", "p1"), q3("Z012-4", "p2")],
         prevs=[P("p1", "2025-05-12", Dd(42, 28, "35a")),
                ("p2", "2024-08-01", {"basem": 3, "extd": 14}, ["fixed", "in_months", "ext", "ext_35a"])]),
    case("Z013", "2026-05-25", "2026-02-02", 12, one(), q12("Z013") + [q3("Z013-3", "p1")],
         prevs=[P("p1", "2024-09-18", Dd(30, 60, "35c"))]),
    case("Z014", "2026-04-14", "2026-01-06", 15, one(), q12("Z014") + [q3("Z014-3", "p1"), q3("Z014-4", "p2")],
         prevs=[P("p1", "2025-03-03", Dd(49, 40, "248d")), P("p2", "2023-11-11", M(6))]),
    case("Z015", "2023-07-03", "2023-02-01", 12, one(), q12("Z015") + [q3("Z015-3", "p1"), q3("Z015-4", "p2")],
         prevs=[P("p1", "2020-06-15", Dd(50, 30, "147a")), P("p2", "2021-11-10", Dd(70))]),
    case("Z016", "2026-08-19", "2026-04-30", 12, one(), q12("Z016") + [q3("Z016-3", "p1")],
         prevs=[P("p1", "2024-11-04", Dd(28, 90, "166")), P("p2", "2024-03-20", Y(2))]),
    case("Z017", "2026-01-12", "2025-06-05", 12, one(), q12("Z017") + [q3("Z017-3", "p1")],
         prevs=[P("p1", "2025-07-01", M(3), "u_s26")]),
    case("Z018", "2023-12-01", "2023-08-05", 12, one(), q12("Z018") + [q3("Z018-3", "p1")],
         prevs=[P("p1", "2020-10-12", M(6), "u_s147")]),
    case("Z019", "2026-06-22", "2026-03-11", 13, one(), q12("Z019") + [q3("Z019-3", "p1"), q3("Z019-4", "p2")],
         prevs=[P("p1", "2024-09-09", Y(1), "u_s164"), P("p2", "2025-02-14", M(6))]),
    case("Z020", "2026-04-30", "2026-01-17", 12, one(), q12("Z020") + [q3("Z020-3", "p1")],
         prevs=[P("p1", "2024-05-06", M(12), "o_steal"), P("p2", "2023-10-02", M(6))]),
    case("Z021", "2026-07-08", "2026-03-21", 12, one(), q12("Z021") + [q3("Z021-3", "p1"), q3("Z021-4", "p2")],
         prevs=[P("p1", "2025-04-15", M(12), "o_ta12"), P("p2", "2024-12-03", M(6), "o_ta25")]),
    case("Z022", "2026-03-26", "2026-01-09", 12, one(), q12("Z022") + [q3("Z022-3", "p1")],
         prevs=[P("p1", "2024-08-28", M(6), "o_rta178")]),
    case("Z023", "2026-09-15", "2026-06-02", 14, one(), q12("Z023") + [q3("Z023-3", "p1"), q3("Z023-4", "p2")],
         prevs=[P("p1", "2024-11-19", M(9), "attempt", "o_ta12"), P("p2", "2025-07-07", M(4))]),
    case("Z024", "2026-06-02", "2026-02-19", 15, [("o1", DE, ()), ("o2", DE, ())],
         q12("Z024") + [q3("Z024-3", "p1"), q4("Z024-4", "c1")],
         prevs=[P("p1", "2024-08-12", Y(1))], circs=[("c1", None, ["nserious"])]),
    case("Z025", "2026-03-17", "2025-12-10", 12, [("o1", ["oblig", "s34"], ("oend",)), ("o2", DE, ())], q12("Z025"),
         judgement=["o1: whether the obligatory-disqualification offence involves obligatory endorsement is not stated: left "
                    "unknown (not stated false)"]),
    case("Z026", "2026-04-21", "2026-01-27", 12, [("o1", ["oblig"], ("oend",)), ("o2", DE, ())],
         q12("Z026") + [q3("Z026-3", "p1")], prevs=[P("p1", "2024-05-13", M(6))],
         judgement=["o1: obligatory endorsement not stated: left unknown"]),
    case("Z027", "2026-05-05", "2026-02-14", 12, one(fl=["oblig", "s34"], unk=("oend",)), q12("Z027"),
         judgement=["o1: obligatory endorsement not stated: left unknown"]),
    case("Z028", "2026-02-09", "2025-10-30", 13, one(fl=["oblig"], unk=("oend",)), q12("Z028") + [q4("Z028-3", "c1")],
         prevs=[P("p1", "2023-06-16", M(12)), P("p2", "2025-03-25", M(2))], circs=[("c1", None, ["hardship"])],
         judgement=["o1: obligatory endorsement not stated: left unknown"]),
    case("Z029", "2026-07-13", "2026-04-03", 12, one(fl=["aid", "aid_oblig", "oend"], unk=("oblig", "disc")),
         q12("Z029") + [q3("Z029-3", "p1")], prevs=[P("p1", "2024-10-21", M(6))],
         judgement=["o1: whether Hamid's own offence is stated as one involving obligatory or discretionary "
                    "disqualification: left unknown (the case states the aided offence's kind)"]),
    case("Z030", "2026-04-27", "2026-01-12", 12, one(fl=["aid", "aid_oblig", "oend"], unk=("oblig", "disc", "s34")),
         q12("Z030") + [q4("Z030-3", "c1")], circs=[("c1", None, ["hardship", "exceptional"])], vfacts=["satisfied"],
         judgement=["o1: own kind and any s.34 order not stated: left unknown",
                    "c1: 'no circumstance of this kind has been put to any court before' read as not taken into account "
                    "on an earlier occasion"]),
    case("Z031", "2026-10-06", "2026-06-19", 12, one(), q12("Z031") + [q4("Z031-3", "c1")],
         prevs=[P("p1", "2024-12-04", M(3))], circs=[("c1", None, ["hardship", "exceptional"])], vfacts=["satisfied"]),
    case("Z032", "2026-09-15", "2026-05-02", 12, one(), q12("Z032") + [q4("Z032-3", "c1")],
         circs=[("c1", "2024-05-10", ["hardship", "exceptional", "taken"])],
         judgement=["c1: the earlier court 'took into account under section 35(1) ... and on that occasion did not order "
                    "Fatima to be disqualified' read as taken into account in not ordering disqualification ((4)(c))"]),
    case("Z033", "2026-06-05", "2026-02-20", 12, one(), q12("Z033") + [q4("Z033-3", "c1")],
         circs=[("c1", "2023-06-01", ["hardship", "exceptional", "taken"])], vfacts=["satisfied"],
         judgement=["c1: as Z032 (taken into account in not ordering disqualification on 1 June 2023)"]),
    case("Z034", "2026-11-18", "2026-08-04", 12, one(), q12("Z034") + [q3("Z034-3", "p1"), q4("Z034-4", "c1")],
         prevs=[P("p1", "2023-11-20", Dd(30))],
         circs=[("c1", "2023-11-20", ["hardship", "exceptional", "taken"])],
         judgement=["c1: taken into account under s.35(1) on 20 November 2023 when the court ordered a s.35 disqualification "
                    "of 30 days: read as 'in ordering the offender to be disqualified for a shorter period' (30 days is "
                    "shorter than any minimum period of (2))"]),
    case("Z035", "2026-08-04", "2026-03-01", 13, one(),
         q12("Z035") + [q3("Z035-3", "p2"), q3("Z035-4", "p1"), q4("Z035-5", "c1"), q4("Z035-6", "c2")],
         prevs=[P("p1", "2025-02-10", M(6)), ("p2", "2024-04-03", {}, [])],
         circs=[("c1", None, ["hardship", "exceptional"]), ("c2", None, [])], vfacts=["satisfied"],
         judgement=["c1: considered on 10 February 2025 without the court being satisfied and without a shorter period: "
                    "not taken into account in ordering a shorter period or no disqualification ((4)(c) false)",
                    "c2: advanced driving lessons: not hardship (the case states it is not alleged to make the offence "
                    "not a serious one)"]),
]

PROBES = {
    "Z036": "probe: whether the offence involves obligatory endorsement is not stated",
    "Z037": "probe: the penalty points to be taken into account are not stated (s.29 out)",
    "Z038": "probe: which offences' points count under s.29 (out)",
    "Z039": "probe: a court in Scotland ((6) out; fixed fact England and Wales)",
    "Z040": "probe: a court in Northern Ireland (outside the Act's extent)",
    "Z041": "probe: revocation under the Road Traffic (New Drivers) Act 1995 (out)",
    "Z042": "probe: the effect of an appeal (out)",
    "Z043": "probe: the effect of an appeal, (3)(c) (out)",
    "Z044": "probe: the points to attribute and which count under s.29 (out)",
    "Z045": "probe: whether the offence involves obligatory endorsement is not stated",
}
PROBE_QIDS = {}
UNSUPPORTED = {}
for _line in (HERE / "questions-enc.jsonl").read_text(encoding="utf-8").splitlines():
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
