"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). CROSS-FAMILY questions, Opus encoder.

Encoder: dri-statute-corpus-wtr-annual-leave-w-1124 (Opus 5.5), after the translation was committed (90d34720ac); encode.py
C1-C5. Each question maps to one form of run.py on one item ("none" = no form carries it: refused, OPEN), or to "parts" (C5).
"judgement": anything the encoder decided beyond copying a stated fact (listed as "encoder judgement"): none in this file.
Every leave year's leave taken / paid leave taken is 0 unless the case states leave ("No annual leave has been taken ...
except as expressly stated below"). Bridge inputs are given only where a rule needs the bridged value (next leave year,
days of a leave year, remaining / expired days, the 2007 / 2009 years, the 18 months, anniversaries), so an answer that
needs none uses none.
PROBES: out-of-scope cases (every answer UNSUPPORTED, D2). UNSUPPORTED: none.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "7c9f085e9a5ab11f2c6e7483e847f75645ffc8b12d2da20845c7c4e61c7e77aa"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")


def case(cid, qs, dpw=5, es=None, years=(), agr=True, wfacts=(), wints=None, yfacts=None, yints=None, notices=(),
         nfacts=None, nints=None, proposals=(), of=(), bridge=(), judgement=()):
    """years: [(item, first day)]; the worker's facts: agrly when a relevant agreement fixes the leave years (agr)."""
    yitems = [y for y, _ in years]
    facts = {"w": [*(["agrly"] if agr else []), *wfacts]}
    for x, fs in (yfacts or {}).items():
        facts[x] = list(fs)
    for x, fs in (nfacts or {}).items():
        facts[x] = list(fs)
    ints = {}
    if dpw is not None:
        ints["dpw_w"] = dpw
    if es:
        ints["es_w"] = es
    ints.update(wints or {})
    for y, d in years:
        ints[f"ys_{y}"] = d
        ints[f"tk_{y}"], ints[f"tkp_{y}"] = 0, 0
    ints.update(yints or {})
    ints.update(nints or {})
    c = {"id": cid, "workers": ["w"], "years": yitems, "notices": list(notices), "proposals": list(proposals),
         "facts": facts, "ints": ints, "bridge": list(bridge), "of": [list(x) for x in of], "judgement": list(judgement),
         "questions": []}
    for i, q in enumerate(qs):
        qid = f"{cid}-{i + 1}"
        if isinstance(q, list):
            c["questions"].append({"qid": qid, "parts": [list(p) for p in q]})
        else:
            c["questions"].append({"qid": qid, "item": q[0], "form": q[1]})
    return c


def Y(item, ys):
    return {"item": item, "kind": "year", "ys": ys}


def TERM(item, ys, td):
    return {"item": item, "kind": "term", "ys": ys, "td": td}


def NOTICE(n, given, earliest, count, kind):
    return {f"nd_{n}": given, f"ne_{n}": earliest, f"nc_{n}": count}, kind


def notices(*rows):
    ints, facts, items = {}, {}, []
    for n, given, earliest, count, kind in rows:
        items.append(n)
        ints.update({f"nd_{n}": given, f"ne_{n}": earliest, f"nc_{n}": count})
        facts[n] = list(kind) if isinstance(kind, (list, tuple)) else [kind]
    return items, facts, ints


J26 = [("y1", "2026-01-01")]
CASES = []
A = CASES.append

# --- entitlements (13(1), 13A(2)(e), 13A(3)) ---
A(case("W001", [("y1", "e13"), ("y1", "e13a")], dpw=2, es="2026-01-01", years=J26))
A(case("W002", [("y1", "etot"), ("y1", "begins")], dpw=3, es="2020-05-10", years=[("y1", "2026-05-10")], agr=False,
       bridge=[{"item": "y1", "kind": "anniv", "ys": "2026-05-10", "es": "2020-05-10"}]))
A(case("W003", [("y1", "etot"), ("y1", "e13a")], dpw=5, es="2026-01-01", years=J26))
A(case("W004", [("y1", "e13"), ("y1", "e13a")], dpw=6, es="2020-01-01", years=J26))
A(case("W005", [("y1", "e13"), ("y1", "e13a")], dpw=7, es="2020-01-01", years=J26))
A(case("W006", [("y1", "etot"), ("y1", "begins")], es="1998-10-01", years=[("y1", "2025-10-01")], agr=False,
       bridge=[{"item": "y1", "kind": "anniv", "ys": "2025-10-01", "es": "1998-10-01"}]))
A(case("W007", [("y1", "etot"), ("y2", "begins")], es="1998-10-02", years=[("y1", "2025-10-02"), ("y2", "2025-10-01")],
       agr=False, bridge=[{"item": "y2", "kind": "anniv", "ys": "2025-10-01", "es": "1998-10-02"}]))
# --- first leave year (13(5), 13A(5)) ---
A(case("W008", [("y1", "e13"), ("y1", "e13a")], es="2026-10-20", years=J26,
       bridge=[Y("y1", "2026-01-01"), {"item": "y1", "kind": "rem", "ys": "2026-01-01", "es": "2026-10-20"}]))
A(case("W009", [("y1", "e13"), ("y1", "e13a")], es="2024-07-02", years=[("y1", "2024-01-01")],
       bridge=[Y("y1", "2024-01-01"), {"item": "y1", "kind": "rem", "ys": "2024-01-01", "es": "2024-07-02"}]))
A(case("W010", [("y1", "e13"), ("y1", "e13a")], dpw=3, es="2020-01-01", years=[("y1", "2024-03-31")]))
A(case("W011", [("y1", "e13"), ("y1", "e13a")], dpw=3, es="2020-01-01", years=[("y1", "2024-04-01")]))
# --- phases (13A(2)(a)-(d)) and payment in lieu (13A(6)) ---
A(case("W012", [("y1", "e13a"), ("y1", "pil13a")], es="2000-01-01", years=[("y1", "2007-09-30")], wfacts=["round2"],
       bridge=[{"item": "y1", "kind": "phb", "ys": "2007-09-30"}]))
A(case("W013", [("y1", "e13a"), ("y2", "e13a"), ("y2", "pil13ai"), ("y2", "pil13af")], es="2000-01-01",
       years=[("y1", "2007-10-01"), ("y2", "2008-10-01")], wfacts=["round2"],
       bridge=[{"item": "y2", "kind": "phd", "ys": "2008-10-01"}]))
A(case("W014", [("y1", "e13a"), ("y2", "e13a"), ("y1", "pil13a"), ("y2", "pil13a")], es="2000-01-01",
       years=[("y1", "2008-04-01"), ("y2", "2009-04-01")]))
A(case("W015", [("y1", "etot"), [("y1", "inst13"), ("y1", "inst13a")], [("y1", "pil13"), ("y1", "pil13a")]],
       es="2020-01-01", years=J26, yints={"tk_y1": 5, "tkp_y1": 5}))
# --- carry forward (13(14)-(18), 13A(7), (7A)) ---
Y25 = [("y1", "2025-01-01"), ("y2", "2026-01-01")]
A(case("W016", [("y1", "etot"), ("y2", "etot"), ("y1_y2", "takall")], es="2025-01-01", years=Y25,
       bridge=[Y("y1", "2025-01-01")]))
A(case("W017", [("y1", "etot"), ("y2", "etot"), ("y1_y2", "takall")], es="2025-01-01", years=Y25,
       yfacts={"y1": ["stat13", "stat13a"]}, bridge=[Y("y1", "2025-01-01")]))
A(case("W018", [("y1", "e13"), ("y2", "e13"), ("y3", "e13"), ("p1", "canuse"), ("p2", "canuse")], es="2024-01-01",
       years=[("y1", "2024-01-01"), ("y2", "2025-01-01"), ("y3", "2026-01-01")], yfacts={"y1": ["sick13"]},
       proposals=["p1", "p2"], of=[("p1", "y1"), ("p2", "y1")], wints={"pday_p1": "2026-06-30", "pday_p2": "2026-07-01"},
       bridge=[Y("y1", "2024-01-01"), {"item": "y1", "kind": "e18", "ys": "2024-01-01"}]))
A(case("W019", [("y1", "e13"), ("y2", "e13"), ("y3", "e13"), ("y4", "e13"), ("y1_y3", "tak13"), ("p1", "canuse"),
                ("p2", "canuse")], es="2024-01-01",
       years=[("y1", "2024-01-01"), ("y2", "2025-01-01"), ("y3", "2026-01-01"), ("y4", "2027-01-01")],
       yfacts={"y1": ["faila"], "y2": ["failopp", "failenc"]}, yints={"tk_y1": 5, "tkp_y1": 0},
       proposals=["p1", "p2"], of=[("p1", "y1"), ("p2", "y1")], wints={"pday_p1": "2026-12-31", "pday_p2": "2027-01-01"},
       bridge=[Y("y1", "2024-01-01"), Y("y2", "2025-01-01"), Y("y3", "2026-01-01"), Y("y4", "2027-01-01")]))
A(case("W020", [("y1", "etot"), ("y2", "etot"), ("y2", "pay14")], es="2025-01-01", years=Y25, wfacts=["terminated"],
       wints={"td_w": "2026-01-01"}, yfacts={"y1": ["failinf"]},
       bridge=[Y("y1", "2025-01-01"), Y("y2", "2026-01-01"), TERM("y2", "2026-01-01", "2026-01-01")]))
A(case("W021", [("y1", "etot"), ("y2", "etot"), ("y1_y2", "tak13a")], es="2025-01-01", years=Y25, wfacts=["agrcf"],
       wints={"agrcap_w": 3}, bridge=[Y("y1", "2025-01-01")]))
# --- termination (14) ---
T26 = [Y("y1", "2026-01-01"), TERM("y1", "2026-01-01", "2026-03-15")]
A(case("W022", [("y1", "etot"), ("y1", "pay14")], es="2026-01-01", years=J26, wfacts=["terminated"],
       wints={"td_w": "2026-03-15"}, bridge=T26))
A(case("W023", [("y1", "etot"), ("y1", "pay14"), ("y1", "comp")], es="2026-01-01", years=J26,
       wfacts=["terminated", "agrcomp"], wints={"td_w": "2026-03-15"}, yints={"tk_y1": "5.6", "tkp_y1": "5.6"}, bridge=T26))
A(case("W024", [("y1", "etot"), ("y1", "pay14"), ("y1", "comp")], es="2026-01-01", years=J26,
       wfacts=["terminated", "agrcomp"], wints={"td_w": "2026-03-15"}, yints={"tk_y1": 6, "tkp_y1": 6}, bridge=T26))
A(case("W025", [("y1", "etot"), ("y1", "pay14")], es="2026-01-01", years=J26, wfacts=["terminated"],
       wints={"td_w": "2026-01-01"}, bridge=[Y("y1", "2026-01-01"), TERM("y1", "2026-01-01", "2026-01-01")]))
A(case("W026", [("y1", "etot"), ("y1", "pay14")], es="2026-01-01", years=J26, wfacts=["terminated"],
       wints={"td_w": "2026-12-31"}, bridge=[Y("y1", "2026-01-01"), TERM("y1", "2026-01-01", "2026-12-31")]))
A(case("W027", [("y1", "etot"), ("y1", "pay14")], es="2026-01-01", years=J26, wfacts=["terminated", "agrpaysum"],
       wints={"td_w": "2026-03-15", "agrpay_w": "400.00"}, bridge=T26))
A(case("W028", [("y1", "etot"), ("y2", "etot"), ("y2", "pay14")], es="2025-01-01", years=Y25, wfacts=["terminated"],
       wints={"td_w": "2026-01-01"}, yfacts={"y1": ["stat13", "stat13a"]},
       bridge=[Y("y1", "2025-01-01"), Y("y2", "2026-01-01"), TERM("y2", "2026-01-01", "2026-01-01")]))
A(case("W029", [("y1", "etot"), ("y2", "etot"), ("y2", "pay14")], es="2025-01-01", years=Y25,
       wfacts=["terminated", "agrcf"], wints={"td_w": "2026-01-01", "agrcap_w": 3}, yfacts={"y1": ["sick13"]},
       bridge=[Y("y1", "2025-01-01"), Y("y2", "2026-01-01"), TERM("y2", "2026-01-01", "2026-01-01")]))
# --- notices (15) ---
_n, _f, _i = notices(("n1", "2026-05-11", "2026-05-18", 3, "nelect"), ("n2", "2026-05-12", "2026-05-18", 3, "nelect"))
A(case("W030", [("y1", "etot"), ("n1", "latest"), ("n1", "intime"), ("n2", "intime")], es="2020-01-01", years=J26,
       notices=_n, nfacts=_f, nints=_i))
_n, _f, _i = notices(("n1", "2026-06-04", "2026-06-08", 2, "nreq"), ("n2", "2026-06-03", "2026-06-08", 2, "nreq"))
A(case("W031", [("y1", "etot"), ("n1", "latest"), ("n1", "intime"), ("n2", "intime")], es="2020-01-01", years=J26,
       notices=_n, nfacts=_f, nints=_i))
_n, _f, _i = notices(("n1", "2026-07-03", "2026-07-06", 2, "nnot"), ("n2", "2026-07-04", "2026-07-06", 2, "nnot"))
A(case("W032", [("y1", "etot"), ("n1", "latest"), ("n1", "intime"), ("n2", "intime")], es="2020-01-01", years=J26,
       notices=_n, nfacts=_f, nints=_i))
_n, _f, _i = notices(("n1", "2026-08-05", "2026-08-10", 2, "nelect"), ("n2", "2026-08-06", "2026-08-10", 2, "nreq"),
                     ("n3", "2026-08-07", "2026-08-10", 2, "nnot"), ("n4", "2026-08-06", "2026-08-10", 2, "nelect"),
                     ("n5", "2026-08-05", "2026-08-10", 2, "nreq"), ("n6", "2026-08-08", "2026-08-10", 2, "nnot"))
A(case("W033", [("y1", "etot"), ("n1", "latest"), ("n2", "latest"), ("n3", "latest"), ("n1", "intime"), ("n2", "intime"),
                ("n3", "intime"), ("n4", "intime"), ("n5", "intime"), ("n6", "intime")], es="2020-01-01", years=J26,
       notices=_n, nfacts=_f, nints=_i))
_n, _f, _i = notices(("n1", "2026-05-17", "2026-05-18", 1, ["nelect", "varied"]), ("n2", "2026-05-16", "2026-05-18", 1, "nnot"))
_i["agroff_n1"] = 1
A(case("W034", [("y1", "etot"), ("n1", "latest"), ("n1", "intime"), ("n2", "imposes")], dpw=3, es="2020-01-01",
       years=J26, wfacts=["sch2", "partagri", "agr133", "agr15", "excl2b"], notices=_n, nfacts=_f, nints=_i))
A(case("W035", [("w", "app133"), ("w", "app15"), ("w", "app13aw")], es="2020-01-01", agr=False,
       wfacts=["sch2", "partagri", "awsa"]))

PROBES = {
    "W036": "regulation 15B applies (reg 15B out of scope, D2)",
    "W037": "the week's pay from earnings (reg 16 and ERA ss.221-224 out of scope, D2)",
    "W038": "a worker wholly in agriculture in Wales: Schedule 2 (out of scope, D2)",
    "W039": "Northern Ireland (the Great Britain regulations only, D2)",
    "W040": "contractual leave (out of scope, D2)",
    "W041": "remedies (out of scope, D2)",
}
PROBE_QIDS = {"W036": ["W036-1", "W036-2"], "W037": ["W037-1"], "W038": ["W038-1"], "W039": ["W039-1"],
              "W040": ["W040-1"], "W041": ["W041-1"]}
UNSUPPORTED = {}


def write_bridge_inputs():
    import json
    import encode as E
    lines = [json.dumps(b, sort_keys=True) for c in CASES for b in E.bridge_inputs(c)]
    (HERE / "bridge" / "inputs.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


if __name__ == "__main__":
    print(write_bridge_inputs(), "bridge inputs")
