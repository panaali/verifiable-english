"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). CROSS-FAMILY questions, Opus encoder.

Encoder: dri-statute-corpus-posthog-leave-w-1124 (Opus 5.5), after the translation was committed (92b0de21b1); encode.py C1-C5.
Each question maps to one form of run.py on one item ("none" = no form carries it: refused, OPEN), or to "parts" (C5).
"judgement": anything the encoder decided beyond copying a stated fact (listed as "encoder judgement").
Bridge input = every leave's first day (deadline, prior-quarter window) and every quarter's year and number.
PROBES: out-of-scope cases (every answer UNSUPPORTED, D11). UNSUPPORTED: none.
REVISION 11-25 (dri-b4-policy-translation-revise-1125, after the translation revision 274273f0d5 was committed): 18 questions
the frozen run mapped to "none" are mapped to the new R13 forms (H001-3, H002-3, H003-3 minguide; H004-1 sigmore with Dara's
stated 40 PTO work days in 2026 as one absence; H004-2, H024-2, H031-3..H035-3 mgrappr; H004-3 results; H006-1 setupdone;
H007-1 viaapp; H010-2 bulkadd; H011-1 cancelroute; H012-1 musttell; H018-3 excsure). H014-2 keeps its form (R8 changed).
No other question's form changed; no encoder judgement added.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "4d7d2f1eb28013685d669ae5fc59b23d71fcd66830e406d3bace39c3514008e6"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

NORM = "none"  # a duty / request / permission or no-outcome question (translation R1, D9): refused


def case(cid, qs, members=("m",), absences=(), years=(), leaves=(), blocks=(), quarters=(), facts=None, ints=None,
         in_year=(), bridge=(), judgement=()):
    c = {"id": cid, "members": list(members), "absences": list(absences), "years": list(years), "leaves": list(leaves),
         "blocks": list(blocks), "quarters": list(quarters), "facts": {k: list(v) for k, v in (facts or {}).items()},
         "ints": dict(ints or {}), "in_year": [list(x) for x in in_year], "bridge": list(bridge),
         "judgement": list(judgement), "questions": []}
    for i, q in enumerate(qs):
        qid = f"{cid}-{i + 1}"
        if isinstance(q, list):
            c["questions"].append({"qid": qid, "parts": [list(p) for p in q]})
        else:
            x, f = q
            c["questions"].append({"qid": qid, "item": x, "form": f})
    return c


def year_case(cid, pto_days, pto_from, holidays):
    """H001-H003: one PTO absence and one absence per national holiday (1 work day each), all in 2026."""
    abs_ = ["a0"] + [f"h{i}" for i in range(len(holidays))]
    facts = {"a0": ["vac"]}
    ints = {"days_a0": pto_days, "from_a0": pto_from}
    for i, d in enumerate(holidays):
        facts[f"h{i}"] = ["vac", "holiday"]
        ints[f"days_h{i}"], ints[f"from_h{i}"] = 1, d
    return case(cid, [("y", "mindays"), ("y", "met"), ("m", "minguide")], absences=abs_,  # -3: rev 11-25 (R13)
                 years=["y"], facts=facts, ints=ints,
                in_year=[(a, "y") for a in abs_])


def leave(cid, qs, kind, tm, td, start, logday, lwk=0, extra=(), ints=None, blocks=None, absences=(), afacts=None,
          quarters=(), qbridge=(), judgement=()):
    """A parental leave l; 'Her country's law gives N weeks of paid parental leave' -> haslocal, lwk N; N = 0 -> the law
    gives no paid parental leave: haslocal false, no lwk (encoder judgement, listed)."""
    facts = {"l": [kind, *(("haslocal",) if lwk else ()), *extra]}
    i = {"tm_l": tm, "td_l": td, "start_l": start, "logday_l": logday}
    if lwk:
        i["lwk_l"] = lwk
    else:
        judgement = list(judgement) + ["'the law gives 0 weeks of paid parental leave' read as no local statutory paid "
                                       "parental leave (haslocal false)"]
    i.update(ints or {})
    bl = blocks or {}
    facts.update(bl)
    facts.update(afacts or {})
    br = [{"item": "l", "kind": "deadline", "start": start}] + list(qbridge)
    return case(cid, qs, leaves=["l"], blocks=list(bl), absences=absences, quarters=quarters, facts=facts, ints=i,
                bridge=br, judgement=judgement)


def sales_case(cid, att1, att2, weeks, q2form, sales=True):
    extra = ("sales",) if sales else ()
    ints = {"wtaken_l": weeks}
    quarters, qb = (), [{"item": "l", "kind": "window", "start": "2027-05-15"}]
    if sales:
        ints.update({"att_q1": att1, "att_q2": att2})
        quarters = ("q1", "q2")
        qb += [{"item": "q1", "kind": "quarter", "year": 2026, "n": 4}, {"item": "q2", "kind": "quarter", "year": 2027, "n": 1}]
    days = {11: 77, 12: 84}[weeks]
    return leave(cid, [("l", "weeks"), ("l", q2form), ("m", "mgrappr")], "maternity",  # -3: rev 11-25 (R13)
                 13, 0, "2027-05-15", "2027-01-15",
                 extra=extra, ints=ints, quarters=quarters, qbridge=qb,
                 judgement=[f"weeks taken {weeks} = the stated {days} calendar days / 7 (the leave's length in weeks)"])


SOLE = {"b1": ["sole"]}
CASES = [
    year_case("H001", 20, "2026-01-05", ["2026-02-02", "2026-03-02", "2026-04-06", "2026-05-04"]),
    year_case("H002", 20, "2026-01-05", ["2026-02-02", "2026-03-02", "2026-04-06", "2026-05-04", "2026-06-01"]),
    year_case("H003", 20, "2026-01-05", ["2026-02-02", "2026-03-02", "2026-04-06", "2026-05-04", "2026-06-01",
                                         "2026-07-06"]),
    case("H004", [("y", "sigmore"), ("m", "mgrappr"), ("m", "results")], absences=["a1"], years=["y"],  # rev 11-25 (R13)
         facts={"a1": ["vac"]}, ints={"days_a1": 40, "from_a1": "2026-01-05"}, in_year=[("a1", "y")]),
    case("H005", [("m", NORM), ("m", NORM), ("m", NORM)]),
    case("H006", [("a1", "setupdone"), [("a1", "autook"), ("a1", "incal")], ("m", NORM), ("m", NORM)], absences=["a1"],
         facts={"a1": ["vac", "app", "auth", "subs"]}, ints={"days_a1": 1, "from_a1": "2027-05-10"},
         judgement=["a one-day vacation is not 'longer term leave' (unit 13)"]),
    case("H007", [("a1", "viaapp"), ("a1", "incal")], absences=["a1"], facts={"a1": ["vac", "deelonly"]},
         ints={"days_a1": 1, "from_a1": "2027-05-12"}),
    case("H008", [("a1", "fitmedical"), ("a1", "fitpto")], absences=["a1"], facts={"a1": ["app"]},
         ints={"days_a1": 2, "from_a1": "2027-05-17"}),
    case("H009", [("a1", "fitmedical"), ("m", NORM)], absences=["a1"], facts={"a1": ["medself", "app"]},
         ints={"days_a1": 2, "from_a1": "2027-05-19"}),
    case("H010", [("m", NORM), ("m", "bulkadd")]),  # rev 11-25 (R13)
    case("H011", [("a1", "cancelroute"), ("m", "candelete")], absences=["a1"], facts={"a1": ["vac", "app", "msgcancel"]},
         ints={"days_a1": 2, "from_a1": "2027-06-07"}),
    case("H012", [("m", "musttell"), ("m", NORM), ("m", "countshours")]),  # rev 11-25 (R13)
    case("H013", [("a1", "fitsick"), ("m", NORM), ("m", NORM)], absences=["a1"], years=["y"],
         facts={"a1": ["ill", "unexpected", "app"]}, ints={"limit_m": 10, "days_a1": 4, "from_a1": "2027-06-07"},
         in_year=[("a1", "y")]),
    case("H014", [[("a1", "paidsick"), ("a2", "paidsick")], ("a3", "paidsick"), ("m", NORM)],
         absences=["a1", "a2", "a3"], years=["y"],
         facts={x: ["ill", "unexpected", "app"] for x in ("a1", "a2", "a3")},
         ints={"limit_m": 4, "days_a1": 2, "from_a1": "2027-06-14", "days_a2": 2, "from_a2": "2027-06-16", "days_a3": 1,
               "from_a3": "2027-06-18"}, in_year=[("a1", "y"), ("a2", "y"), ("a3", "y")]),
    case("H015", [("m", NORM), [("a1", "fitmedical"), ("a2", "fitmedical")]], absences=["a1", "a2"],
         facts={"a1": ["medself", "app"], "a2": ["medself", "app"]},
         ints={"days_a1": 1, "from_a1": "2027-06-21", "days_a2": 1, "from_a2": "2027-06-28"}),
    case("H016", [("a1", "covered"), ("a1", "bminwk"), ("m", NORM)], absences=["a1"], facts={"a1": ["pcloss"]},
         ints={"days_a1": 10, "from_a1": "2027-06-02"}),
    case("H017", [("a2", "treatedext"), ("a1", "asksrel")], absences=["a1", "a2"],
         facts={"a1": ["bereaved"], "a2": ["bereaved", "healthneed"]},
         ints={"days_a1": 10, "from_a1": "2027-06-02", "days_a2": 10, "from_a2": "2027-06-16"}),
    case("H018", [("m", NORM), ("m", NORM), ("m", "excsure")]),  # rev 11-25 (R13)
    leave("H019", [("l", "weeks"), ("l", "deadline"), ("l", "loggedok")], "maternity", 5, 29, "2027-03-31", "2026-11-30"),
    leave("H020", [("l", "weeks"), ("l", "deadline"), ("l", "loggedok")], "paternity", 5, 29, "2027-03-31", "2026-12-01"),
    leave("H021", [("l", "weeks"), ("l", "deadline"), ("m", "canparental")], "maternity", 6, 0, "2027-06-29",
          "2027-02-28"),
    leave("H022", [("l", "weeks"), ("l", "deadline"), ("l", "loggedok")], "paternity", 6, 0, "2027-06-30", "2027-02-28"),
    leave("H023", [("l", "weeks"), ("b1", "paidblock"), ("l", "topup")], "maternity", 11, 0, "2027-07-01", "2027-03-01",
          lwk=16, extra=("judgedless", "statrecv"), blocks=SOLE),
    leave("H024", [("l", "weeks"), ("m", "mgrappr"), ("l", "inaddition")], "paternity", 11, 0, "2027-07-01", "2027-03-01",
          lwk=1, extra=("localfull",)),
    leave("H025", [("l", "weeks"), ("l", "unpaidext"), ("m", NORM)], "maternity", 12, 0, "2027-07-01", "2027-03-01"),
    leave("H026", [("l", "weeks"), ("l", "unpaidext"), ("m", "canparental")], "paternity", 12, 0, "2027-07-01",
          "2027-03-01"),
    leave("H027", [("l", "weeks"), ("l", "allowed"), ("m", NORM)], "maternity", 12, 1, "2027-07-01", "2027-03-01",
          extra=("decrefuse",)),
    leave("H028", [("l", "weeks"), ("l", "payssplit"), ("a1", "fitparental")], "paternity", 12, 1, "2027-07-01",
          "2027-03-01", blocks={"b1": [], "b2": ["later"]}, absences=["a1"], afacts={"a1": ["parental", "app"]},
          ints={"days_a1": 30, "from_a1": "2027-07-01"}),
    leave("H029", [("l", "weeks"), ("l", "inaddition"), ("b1", "paidblock")], "maternity", 13, 0, "2027-07-01",
          "2027-03-01", lwk=28, extra=("localfull",), blocks=SOLE),
    leave("H030", [("l", "weeks"), ("l", NORM), ("l", "loggedok")], "paternity", 13, 0, "2027-07-01", "2027-03-02",
          lwk=2, extra=("localfull",)),
    sales_case("H031", 70, 90, 11, "oteapplies"),
    sales_case("H032", 70, 90, 12, "ote"),
    sales_case("H033", 90, 110, 12, "ote"),
    sales_case("H034", 110, 130, 12, "ote"),
    sales_case("H035", None, None, 12, "oteapplies", sales=False),
]
PROBES = {
    "H036": "birthday and anniversary gifts: out of scope (D1, D11)",
    "H037": "pay amounts during leave: out of scope (D11)",
    "H038": "expenses: not in the file (D11)",
    "H039": "notice periods for leaving: not in the file (D11)",
    "H040": "probation: not in the file (D11)",
}
PROBE_QIDS = {"H036": ["H036-1", "H036-2"], "H037": ["H037-1", "H037-2"], "H038": ["H038-1"], "H039": ["H039-1"],
              "H040": ["H040-1"]}
UNSUPPORTED = {}


def write_bridge_inputs():
    import json
    import encode as E
    lines = [json.dumps(b, sort_keys=True) for c in CASES for b in E.bridge_inputs(c)]
    (HERE / "bridge" / "inputs.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)

# FIDELITY FIX 11-26 (translation R14, encode.py C6): values of the new fields only, from two fresh Opus 5.5 encoder seats
# that saw only questions-enc.jsonl, this file and encode.py's conventions (never sealed/); manage-agents
# reviews/spare/statute-corpus/fidelity-check/sweep/posthog-leave/fix/encoder*/. Applied verbatim; every earlier field is
# unchanged. limcal false (H013, H014: "a year", no calendar anchor) and wholeyear false (H013, H014) are the C1 default.
FIDFIX_1126 = {
    "H001": {"within": ["a0", "h0", "h1", "h2", "h3"], "wholeyear": ["y"]},
    "H002": {"within": ["a0", "h0", "h1", "h2", "h3", "h4"], "wholeyear": ["y"]},
    "H003": {"within": ["a0", "h0", "h1", "h2", "h3", "h4", "h5"], "wholeyear": ["y"]},
    "H004": {"within": ["a1"], "wholeyear": ["y"]},
    "H013": {"within": ["a1"]},
    "H014": {"within": ["a1", "a2", "a3"], "periods": [["a1", "a2", "a3"]]},
}
for _c in CASES:
    _v = FIDFIX_1126.get(_c["id"], {})
    for _key in ("within", "span", "periods"):
        if _key in _v:
            _c[_key] = [list(x) if isinstance(x, (list, tuple)) else x for x in _v[_key]]
    for _y in _v.get("wholeyear", ()):
        _c["facts"].setdefault(_y, []).append("wholeyear")


if __name__ == "__main__":
    print(write_bridge_inputs(), "bridge inputs")
