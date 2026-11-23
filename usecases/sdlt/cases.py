"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). SAME-FAMILY.

Encoder: dri-statute-corpus-sdlt-1123 (Opus 5.5), after the translation was committed (3dfd9401e8, 16:33:58Z).
Each case: "txns" (the transaction asked about = t, a linked transaction = g, earlier acquisitions = p, q), "persons",
"facts" (unary facts true of each txn or person; every other entry false, encode.py C1), "pt" (true (person, txn) facts;
others false), "links" (txn-txn facts, C2), "ints" (stated consideration and years to run), "questions" (qid -> txn and
form: taxnr = Q1, claim = Q2, taxr = Q3 if relief is claimed, taxw = Q3 after a later linked transaction), "judgement"
(anything the encoder decided beyond copying a stated fact: listed as "encoder judgement").
PROBES: out-of-scope cases (scope "out" in the encoder's file): every question UNSUPPORTED.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "6d6ccd62f2b0b5a4096238fffc2597a2c52ca2704b6ff5c62d2a5dd2234d81ab"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

HOUSE = ["freehold", "allres", "usedsingle", "landtxn"]          # a freehold house used as a single dwelling (E or NI)
FLAT = ["lease", "allres", "usedsingle", "landtxn"]              # a lease of a flat used as a single dwelling
WITHGARDEN = ["extraland", "extragarden"]                        # bought together with its garden


def Q(cid, *forms, item="t"):
    out = []
    for i, f in enumerate(forms, 1):
        it, form = (f if isinstance(f, tuple) else (item, f))
        out.append({"qid": f"{cid}-{i}", "item": it, "form": form})
    return out


def solo(cid, cons, facts=HOUSE, years=None, extra_facts=None, txns=("t",), persons=("a",), pt=None, links=(),
         ints=None, judgement=(), forms=("taxnr", "claim", "taxr")):
    """One buyer a, one transaction t, not linked, intending to occupy as only home, no earlier acquisition."""
    f = {"t": list(facts), "a": ["individual"]}
    f.update(extra_facts or {})
    i = {"cons_t": cons}
    if years is not None:
        i["years_t"] = years
    i.update(ints or {})
    return {"id": cid, "txns": list(txns), "persons": list(persons), "facts": f,
            "pt": pt if pt is not None else [("acquires", "a", "t"), ("intends", "a", "t")],
            "links": list(links), "ints": i, "questions": Q(cid, *forms), "judgement": list(judgement)}


def linked2(cid, cons_t, cons_g, gfacts, rel=(), tfacts=HOUSE, pt=None, persons=("a",), extra_facts=None,
            judgement=(), forms=None, ints=None):
    f = {"t": list(tfacts), "g": list(gfacts), "a": ["individual"]}
    f.update(extra_facts or {})
    links = [("linked", "t", "g"), ("linked", "g", "t")] + [(r, "g", "t") for r in rel]
    i = {"cons_t": cons_t, "cons_g": cons_g}
    i.update(ints or {})
    return {"id": cid, "txns": ["t", "g"], "persons": list(persons), "facts": f,
            "pt": pt if pt is not None else [("acquires", "a", "t"), ("intends", "a", "t"), ("acquires", "a", "g")],
            "links": links, "ints": i, "questions": forms, "judgement": list(judgement)}


CASES = [
    solo("S001", "300000.00"),
    solo("S002", "500000.00", facts=FLAT, years="118"),
    solo("S003", "500020.00"),
    solo("S004", "125000.00", txns=("t", "p"), extra_facts={"p": ["freehold", "usedsingle", "landtxn"]},
         pt=[("acquires", "a", "t"), ("intends", "a", "t"), ("acquires", "a", "p")], links=[("earlier", "p", "t")]),
    solo("S005", "1600000.00", facts=HOUSE + WITHGARDEN),
    solo("S006", "250000.00", persons=("a", "b"), extra_facts={"b": ["individual"]},
         pt=[("acquires", "a", "t"), ("intends", "a", "t"), ("acquires", "b", "t"), ("intends", "b", "t")]),
    solo("S007", "400000.00", facts=["freehold", "usedsingle", "landtxn", "extraland"],
         judgement=["the main subject-matter is the whole building: the flat (a part used as a single dwelling) and the "
                    "shop, read as land besides the dwelling that is neither garden or grounds nor land for its benefit"]),
    solo("S008", "250000.00", facts=["freehold", "usedsingle", "landtxn", "extraland"],
         judgement=["the 40 acres of let grazing fields read as other land that is not garden or grounds (the domestic "
                    "garden would be; the fields make the other land, taken as a whole, not garden)"]),
    solo("S009", "150000.00", facts=["freehold", "landtxn"]),
    solo("S010", "280000.00", facts=FLAT, years="140", txns=("t", "p"), persons=("a", "b"),
         extra_facts={"b": ["individual"], "p": ["lease", "usedsingle", "landtxn"]},
         pt=[("acquires", "a", "t"), ("intends", "a", "t"), ("acquires", "b", "t"), ("intends", "b", "t"),
             ("acquires", "b", "p")], links=[("earlier", "p", "t")], ints={"years_p": "98"}),
    solo("S011", "400000.00", txns=("t", "p"), extra_facts={"p": ["lease", "usedsingle", "wales"]},
         pt=[("acquires", "a", "t"), ("intends", "a", "t"), ("acquires", "a", "p")], links=[("earlier", "p", "t")],
         ints={"years_p": "20"},
         judgement=["the 2019 grant of a lease of a flat in Wales read as not a land transaction under this Act (land "
                    "transaction tax applies in Wales from 1 April 2018; outside the pin)"]),
    solo("S012", "299990.00", txns=("t", "p"), extra_facts={"p": ["lease", "usedsingle", "landtxn"]},
         pt=[("acquires", "a", "t"), ("intends", "a", "t"), ("acquires", "a", "p")], links=[("earlier", "p", "t")],
         ints={"years_p": "21"}),
    solo("S013", "300010.00", txns=("t", "p"), extra_facts={"p": ["usedsingle", "abroad", "equivalent"]},
         pt=[("acquires", "a", "t"), ("intends", "a", "t"), ("acquires", "a", "p")], links=[("earlier", "p", "t")]),
    solo("S014", "350000.00", txns=("t", "p", "q"),
         extra_facts={"p": ["lease", "usedsingle", "landtxn"], "q": ["lease", "usedsingle", "abroad", "equivalent"]},
         pt=[("acquires", "a", "t"), ("intends", "a", "t"), ("acquires", "a", "p"), ("acquires", "a", "q")],
         links=[("earlier", "p", "t"), ("earlier", "q", "t")], ints={"years_p": "20", "years_q": "20"}),
    linked2("S015", "360000.00", "40000.00", ["freehold", "allres", "landtxn"], rel=("gardenof",),
            forms=Q("S015", "taxnr", "claim", "taxr", ("g", "taxnr"), ("g", "claim"), ("g", "taxr"))),
    linked2("S016", "490000.00", "10000.00", ["allres", "landtxn"], rel=("benefitof",),
            forms=Q("S016", "taxnr", "claim", "taxr", ("g", "taxnr"), ("g", "claim"), ("g", "taxr")),
            judgement=["a permanent right of way read as neither a freehold nor a lease of land (no major interest)"]),
    linked2("S017", "240000.00", "60000.00", ["freehold", "landtxn"],
            forms=Q("S017", "taxnr", "claim", "taxr", ("g", "taxnr"), ("g", "claim"), ("g", "taxr"))),
    linked2("S018", "320000.00", "80000.00", ["freehold", "allres", "landtxn"], rel=("gardenof",),
            persons=("a", "b"),
            extra_facts={"b": ["individual"]},
            pt=[("acquires", "a", "t"), ("intends", "a", "t"), ("acquires", "a", "g"), ("acquires", "b", "g")],
            forms=Q("S018", "taxnr", "claim", "taxr", ("g", "taxnr"), ("g", "claim"), ("g", "taxr")),
            judgement=["Samuel's 2015 Leeds house is not encoded as an earlier acquisition item: it bears only on "
                       "Samuel, who is not a purchaser of the house; his status as purchaser of the plot decides 2(2)"]),
    linked2("S019", "300000.00", "100000.00", ["freehold", "landtxn"],
            forms=Q("S019", "taxnr", "claim", "taxw"),
            judgement=["the case states the two purchases ARE linked: every question (Q1 too) is read in that state, "
                       "after the later purchase"]),
    linked2("S020", "360000.00", "40000.00", ["allres", "landtxn"], rel=("benefitof",), tfacts=FLAT,
            ints={"years_t": "120"}, forms=Q("S020", "taxnr", "claim", "taxw"),
            judgement=["the case states the two purchases ARE linked: every question (Q1 too) is read in that state",
                       "a permanent parking right read as neither a freehold nor a lease of land (no major interest)"]),
    linked2("S021", "440000.00", "110000.00", ["freehold", "allres", "landtxn"], rel=("gardenof",),
            forms=Q("S021", "taxnr", "claim", "taxw", ("g", "taxnr"), ("g", "claim"), ("g", "taxr")),
            judgement=["the case states the two purchases ARE linked: every question (Q1 too) is read in that state"]),
    solo("S022", "400000.00", persons=("a", "f"), extra_facts={"t": HOUSE + ["affirst"]},
         pt=[("acquires", "f", "t"), ("afperson", "a", "t"), ("intends", "a", "t")],
         judgement=["the institution (Amanah) is a person that is not an individual"]),
    solo("S023", "260000.00", txns=("t", "p"), persons=("a", "f"),
         extra_facts={"p": ["freehold", "usedsingle", "landtxn", "affirst"]},
         pt=[("acquires", "a", "t"), ("intends", "a", "t"), ("acquires", "f", "p"), ("afperson", "a", "p")],
         links=[("earlier", "p", "t")]),
    solo("S024", "425000.00", txns=("t", "p"), extra_facts={"p": ["usedsingle", "abroad"]},
         pt=[("acquires", "a", "t"), ("intends", "a", "t"), ("wouldbeaf", "a", "p")], links=[("earlier", "p", "t")],
         judgement=["the Malaysian bank's purchase of the apartment encoded as an earlier acquisition item (not a "
                    "lease) on which the stated para. 6(1)(d) conclusion is read"]),
    solo("S025", "320000.00", facts=FLAT, years="125", persons=("a", "z"),
         extra_facts={"z": ["individual"]},
         pt=[("acquires", "a", "t"), ("baretrustee", "a", "t"), ("btbeneficiary", "z", "t"), ("intends", "z", "t")],
         judgement=["Alan's own 1998 house is not encoded: Alan is not the purchaser (para. 3A); it bears only on him"]),
    solo("S026", "275000.00", txns=("t", "p"), persons=("a", "m"),
         extra_facts={"p": ["lease", "usedsingle", "landtxn"], "m": ["individual"]},
         pt=[("acquires", "a", "t"), ("intends", "a", "t"), ("acquires", "m", "p"), ("baretrustee", "m", "p"),
             ("btbeneficiary", "a", "p")], links=[("earlier", "p", "t")], ints={"years_p": "99"}),
    {"id": "S027", "txns": ["t"], "persons": ["a"], "facts": {"t": HOUSE + ["hrt"], "a": ["individual"]},
     "pt": [("acquires", "a", "t"), ("intends", "a", "t")], "links": [], "ints": {"cons_t": "210000.00"},
     "questions": Q("S027", "claim"), "judgement": []},
    solo("S028", "245000.00", txns=("t", "p"), extra_facts={"p": ["lease", "usedsingle", "wales"]},
         pt=[("acquires", "a", "t"), ("intends", "a", "t"), ("acquires", "a", "p")], links=[("earlier", "p", "t")],
         ints={"years_p": "25"},
         judgement=["the 2020 grant of a lease of a flat in Wales read as not a land transaction under this Act (land "
                    "transaction tax applies in Wales from 1 April 2018; outside the pin)"]),
    solo("S029", "150000.00", facts=FLAT, years="20"),
    solo("S030", "360000.00", facts=["freehold", "allres", "landtxn", "substperf", "tobebuilt", "notbegun"],
         judgement=["the freehold of the plot read as 'a major interest in a building ... to be constructed under the "
                    "contract' (para. 9(5)(b))"]),
    solo("S031", "180000.00", facts=["freehold", "allres", "landtxn", "constructing"]),
    solo("S032", "430000.00", facts=["freehold", "allres", "landtxn", "suitablesingle"]),
    solo("S033", "480000.00", facts=["freehold", "landtxn", "used116", "suitablesingle"]),
    solo("S034", "925000.00"),
    solo("S035", "1500000.00", facts=HOUSE + WITHGARDEN),
]

PROBES = {f"S0{n}": "out-of-scope case (scope 'out' in the encoder's file): not supported" for n in range(36, 46)}
PROBE_QIDS = {"S036": ["S036-1", "S036-2"], "S037": ["S037-1", "S037-2"], "S038": ["S038-1", "S038-2", "S038-3"],
              "S039": ["S039-1", "S039-2", "S039-3"], "S040": ["S040-1", "S040-2"],
              "S041": ["S041-1", "S041-2", "S041-3"], "S042": ["S042-1"], "S043": ["S043-1", "S043-2"],
              "S044": ["S044-1"], "S045": ["S045-1", "S045-2"]}
UNSUPPORTED = {}
