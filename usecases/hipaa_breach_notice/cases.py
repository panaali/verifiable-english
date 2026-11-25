"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). CROSS-FAMILY questions, Opus encoder.

Encoder: dri-statute-corpus-hipaa-breach-notice-w-1124 (Opus 5.5), after the translation was committed (39a9391971).
Each case: items by kind (translation.Ctx; incident "i"), "facts" {item: [true facts]} (C1: all others false), "days" {day
constant: YYYY-MM-DD}, "cnts" {count constant: n}, "names" {State item: name}, "questions" [(qid, item, form)], "judgement"
(anything the encoder decided beyond copying a stated fact: listed as "encoder judgement").
Forms: translation.DERIVED_UNARY names read as yes/no (Q1 for the covered entity: bun; for the business associate: baduty);
"who_ce" / "who_ba" the Q2 recipients; "li", "lm", "ls", "lb", "dly" read a day (run.VALUE); NOFORM: the question asks
whether a whole draft, arrangement or act SATISFIES the requirements (a conjunction over several requirements and stated
details no rule of translation.py decides as one question), or what a statement "authorizes" over an interval: answered OPEN
(refused), never forced into a nearby predicate.
"The clinic has not performed a risk assessment": no low-probability demonstration (lowprob false by C1; R1's presumption).
PROBES: out-of-scope cases (every answer UNSUPPORTED, from the scope field). UNSUPPORTED (in scope): none.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "03ec97f1f9e1bc6d38836686b136ce9bd77fe049f139914cb19552dde70e158d"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

NOFORM = "noform"
OUT = ["phi", "notperm", "acq"]     # an outside person's deliberate, impermissible access to unencrypted PHI


def case(cid, qs, inc=OUT, states=(), facts=None, days=None, cnts=None, judgement=(), **items):
    st, names, c = {}, {}, dict(cnts or {})
    for n, (name, res) in enumerate(states, 1):
        st[f"s{n}"] = "i"
        names[f"s{n}"] = name
        c[f"res_s{n}"] = res
    f = {"i": list(inc)}
    for x, v in (facts or {}).items():
        f[x] = f.get(x, []) + list(v)
    return {"id": cid, "incs": ["i"], "states": st, "names": names, "facts": f, "days": days or {}, "cnts": c, **items,
            "questions": [{"qid": f"{cid}-{n}", "item": x, "form": fm} for (n, x, fm) in qs], "judgement": list(judgement)}


def ce3(form3=None, item3="i"):
    qs = [(1, "i", "bun"), (2, "i", "who_ce")]
    return qs + ([(3, item3, form3)] if form3 else [])


def ba3(form3="lb"):
    return [(1, "b", "baduty"), (2, "b", "who_ba"), (3, "b", form3)]


BA = {"bas": {"b": "i"}}

CASES = [
    case("N001", ce3("li"), states=[("Ohio", 500)], days={"disc_i": "2027-01-01"}),
    case("N002", ce3("lm") + [(4, "i", NOFORM)], states=[("Ohio", 501)], days={"disc_i": "2028-01-01"}),
    case("N003", ce3("ls") + [(4, "i", "logreq")], states=[("Ohio", 499)], days={"disc_i": "2027-12-31"}),
    case("N004", ce3("li"), states=[("Ohio", 300), ("Indiana", 300)], days={"disc_i": "2027-11-15"}),
    case("N005", ce3("ls"), states=[("Ohio", 250), ("Indiana", 250)],
         days={"disc_i": "2027-03-01", "isd_i": "2027-03-20"}),
    case("N006", ce3("ls"), states=[("Indiana", 499)], days={"disc_i": "2026-12-31"}),
    case("N007", ce3(), inc=OUT + ["guid"], states=[("Ohio", 501)], days={"disc_i": "2027-04-01"}),
    case("N008", ce3(), inc=["phi", "acq"], states=[("Indiana", 501)], days={"disc_i": "2027-04-02"}),
    case("N009", ce3(), inc=OUT + ["wf", "unint", "gfs"], states=[("Ohio", 12)], days={"disc_i": "2027-04-05"}),
    case("N010", ce3("li"), inc=OUT + ["wf", "unint", "gfs", "further"], states=[("Ohio", 12)],
         days={"disc_i": "2027-04-07"}),
    case("N011", ce3(), inc=["phi", "notperm", "dsc", "inadv", "authfrom", "authto"], states=[("Ohio", 14)],
         days={"disc_i": "2027-04-08"}),
    case("N012", ce3("li"), inc=["phi", "notperm", "dsc", "inadv", "authfrom", "authto", "further"],
         states=[("Ohio", 14)], days={"disc_i": "2027-04-10"}),
    case("N013", ce3(), inc=["phi", "notperm", "dsc", "gfret"], states=[("Ohio", 16)], days={"disc_i": "2027-04-11"}),
    case("N014", ce3("li"), inc=["phi", "notperm", "dsc"], states=[("Ohio", 16)], days={"disc_i": "2027-04-12"}),
    case("N015", ce3(), inc=OUT + ["lowprob"], states=[("Ohio", 501)], days={"disc_i": "2027-05-01"}),
    case("N016", ce3("lm"), states=[("Ohio", 501), ("Indiana", 501)], days={"disc_i": "2027-05-02"}),
    # second-form discovery: who learned when (knowers), and the stated reasonable-diligence day
    case("N017", ce3("li"), states=[("Ohio", 24)], facts={"k1": ["kce"]},
         days={"kd_k1": "2027-03-03", "dd_i": "2027-03-03"}, knows={"k1": ["ce", "i"]}),
    case("N018", ce3("li"), states=[("Ohio", 24)], facts={"k1": ["kce"], "k2": ["kce"]},
         days={"kd_k1": "2027-04-02", "kd_k2": "2027-04-10", "dd_i": "2027-04-02"},
         knows={"k1": ["ce", "i"], "k2": ["ce", "i"]}),
    case("N019", ce3("li"), inc=OUT + ["wf", "unint"], states=[("Ohio", 24)], facts={"k1": ["kce", "kcom"]},
         days={"kd_k1": "2027-05-10", "dd_i": "2027-05-01"}, knows={"k1": ["ce", "i"]},
         judgement=["N019-3: Anna, whose own access is the incident, taken as the person committing it (kcom); the stated "
                    "reasonable-diligence day (1 May) is earlier than her learning day either way"]),
    # the business associate
    case("N020", ba3() + [(4, "b", "bidreq"), (5, "b", "binforeq")], states=[("Ohio", 412), ("Indiana", 95)],
         facts={"b": ["bknow", "bidpos"]}, days={"bdisc_b": "2027-12-15"}, **BA),
    case("N021", ba3(), states=[("Ohio", 18)], facts={"b": ["bknow"], "k1": ["kba"], "k2": ["kba"]},
         days={"kd_k1": "2028-01-31", "kd_k2": "2028-02-05", "bdd_b": "2028-01-31"},
         knows={"k1": ["ba", "i"], "k2": ["ba", "i"]}, **BA),
    case("N022", ba3(), inc=OUT + ["wf"], states=[("Ohio", 18)],
         facts={"b": ["bknow"], "k1": ["kba", "kcom"], "k2": ["kba"]},
         days={"kd_k1": "2027-01-31", "kd_k2": "2027-02-10", "bdd_b": "2027-02-01"},
         knows={"k1": ["ba", "i"], "k2": ["ba", "i"]}, **BA),
    # methods of notice
    case("N023", ce3("li") + [(4, "i", "altok")], states=[("Ohio", 20)], days={"disc_i": "2027-06-01"},
         cnts={"nins_i": 9}),
    case("N024", [(1, "i", "bun"), (2, "i", "who_ce"), (3, "i", NOFORM), (4, "i", NOFORM)], states=[("Ohio", 20)],
         days={"disc_i": "2027-06-02"}, cnts={"nins_i": 10}),
    case("N025", ce3("substreq", "g1"), states=[("Ohio", 11)], facts={"g1": ["dec", "ins", "nokins"]},
         days={"disc_i": "2027-06-03"}, groups={"g1": "i"},
         judgement=["N025-3: 'no address for her next of kin or personal representative' taken as insufficient contact "
                    "information that precludes written notification to them (nokins)"]),
    case("N026", ce3(NOFORM) + [(4, "g2", "emailok")], states=[("Ohio", 3)],
         facts={"g1": ["agr"], "g2": ["agr", "wdr"], "g3": ["dec", "nokad"]}, days={"disc_i": "2027-06-04"},
         groups={"g1": "i", "g2": "i", "g3": "i"}),
    case("N027", ce3("li") + [(4, "i", "urgok")], inc=OUT + ["urg"], states=[("Ohio", 30)],
         days={"disc_i": "2027-06-05"}),
    case("N028", ce3(NOFORM), states=[("Ohio", 30)], days={"disc_i": "2027-06-06"}),
    # law enforcement statements
    case("N029", ce3("dly", "o"), states=[("Ohio", 501)], facts={"o": ["purp", "wr", "per", "ab_ind", "ab_med"]},
         days={"disc_i": "2027-02-01", "od_o": "2027-03-02", "pend_o": "2027-04-10"}, stmts={"o": "i"}),
    case("N030", ce3("li"), states=[("Ohio", 25)], facts={"o": ["purp", "wr", "ab_ind"]},
         days={"disc_i": "2027-02-01", "od_o": "2027-02-20"}, stmts={"o": "i"}),
    case("N031", ce3("dly", "o") + [(4, "o", NOFORM)], states=[("Ohio", 25)], facts={"o": ["purp", "oral", "ab_ind"]},
         days={"disc_i": "2027-02-01", "od_o": "2027-03-20"}, stmts={"o": "i"}),
    case("N032", ce3("dly", "o"), states=[("Ohio", 25)], facts={"o": ["purp", "oral", "fw", "fwper", "ab_ind"]},
         days={"disc_i": "2027-02-01", "od_o": "2027-03-20", "fwd_o": "2027-04-10", "fwend_o": "2027-05-10"},
         stmts={"o": "i"}),
    case("N033", [(1, "b", "baduty"), (2, "b", "who_ba"), (3, "o1", "dly"), (4, "o1", NOFORM), (5, "o2", "dly")],
         states=[("Ohio", 25)], facts={"b": ["bknow"], "o1": ["purp", "oral", "ab_ba"], "o2": ["purp", "wr", "per", "ab_ba"]},
         days={"bdisc_b": "2027-02-01", "od_o1": "2027-03-20", "od_o2": "2027-04-25", "pend_o2": "2027-05-10"},
         stmts={"o1": "i", "o2": "i"}, **BA,
         judgement=["N033-3: 'on the basis of the oral statement alone': the oral statement entered as its own statement "
                    "item with no written statement following (o1)",
                    "N033-5: 'under the written statement of 25 April 2027': the written statement entered as its own "
                    "statement item (o2)"]),
    case("N034", ce3("li"), states=[("Ohio", 25)], facts={"o": ["wr", "per", "ab_ind"]},
         days={"disc_i": "2027-02-01", "od_o": "2027-03-20", "pend_o": "2027-05-10"}, stmts={"o": "i"}),
    case("N035", ce3("li") + [(4, "i", "admin"), (5, "i", "burden")], inc=OUT + ["wf"], states=[("Ohio", 22)],
         days={"disc_i": "2027-07-01"}),
]

PROBES = {"N036": "a State's breach-notification law (not in the pinned file)",
          "N037": "the law of another country",
          "N038": "civil money penalties and criminal sanctions (not in the pinned file)",
          "N039": "the content of the Secretary's guidance and the security rule (not pinned)",
          "N040": "breach notification by vendors of personal health records (a different federal rule)"}
UNSUPPORTED = {}


def _probe_qids():
    out = {}
    for line in (HERE / "questions-enc.jsonl").read_text(encoding="utf-8").splitlines():
        c = json.loads(line)
        if c["scope"] == "out":
            out[c["id"]] = [q["qid"] for q in c["questions"]]
    return out


PROBE_QIDS = _probe_qids()


def check():
    """Every in-scope qid of the encoder file is encoded exactly once; every probe case is listed."""
    want, scope = [], {}
    for line in (HERE / "questions-enc.jsonl").read_text(encoding="utf-8").splitlines():
        c = json.loads(line)
        scope[c["id"]] = c["scope"]
        if c["scope"] == "in":
            want += [q["qid"] for q in c["questions"]]
    got = [q["qid"] for c in CASES for q in c["questions"]]
    assert sorted(got) == sorted(want), (sorted(set(want) - set(got)), sorted(set(got) - set(want)))
    assert set(PROBES) == {cid for cid, s in scope.items() if s == "out"}
    return len(got)


if __name__ == "__main__":
    print("in-scope questions encoded:", check())
