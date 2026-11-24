"""SDLT: TEMPLATE for the cross-family encoder: the build's record format, helpers and conventions; records removed.

Each case: "txns" (the transaction asked about = t, a linked or later transaction = g, earlier acquisitions = p, q, ...;
any short names), "persons", "facts" (unary facts true of each txn or person; every other entry false, encode.py C1),
"pt" (true (person, txn) facts; others false), "links" (txn-txn facts, C2: "linked" listed both ways), "ints" (stated
consideration "cons_<txn>" and stated whole years to run "years_<txn>" only; never computed), "questions" (qid -> txn and
form: taxnr = Q1 (the tax if relief is not claimed), claim = Q2 (may relief be claimed), taxr = Q3 if relief is claimed,
taxw = Q3 asked after a later linked transaction), "judgement" (anything the encoder decided beyond copying a stated fact:
reported as "encoder judgement").
PROBES: out-of-scope cases (scope "out" in the encoder's file), id -> reason; PROBE_QIDS: id -> its qids; every question
UNSUPPORTED. UNSUPPORTED: in-scope cases the vocabulary cannot state, id -> (reason, [qids]).
Vocabulary: translation.py FACTS, PFACTS, PTFACTS, TTFACTS (STATED = stated judgments, entered as stated).
"""
from __future__ import annotations

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


def rec(cid, txns, persons, facts, pt, links=(), ints=None, questions=None, judgement=()):
    """A record in the build's format (any shape); persons listed with their facts in `facts`."""
    return {"id": cid, "txns": list(txns), "persons": list(persons), "facts": facts, "pt": list(pt),
            "links": list(links), "ints": dict(ints or {}), "questions": questions, "judgement": list(judgement)}


def both(a, b):
    return [("linked", a, b), ("linked", b, a)]


IND = ["individual"]
T3 = ("taxnr", "claim", "taxr")
T6 = ("taxnr", "claim", "taxr", ("u", "taxnr"), ("u", "claim"), ("u", "taxr"))
G6 = ("taxnr", "claim", "taxr", ("g", "taxnr"), ("g", "claim"), ("g", "taxr"))
OWN = ["freehold", "landtxn"]                      # a freehold acquired in a land transaction (no dwelling stated)

CASES = [
    # S001: p = Alice's 2010 lease of a Leeds flat (20 years to run)
    rec("S001", ["t", "p"], ["a"], {"t": HOUSE, "p": ["lease", "usedsingle", "landtxn"], "a": IND},
        [("acquires", "a", "t"), ("intends", "a", "t"), ("acquires", "a", "p")], [("earlier", "p", "t")],
        {"cons_t": "124999.00", "years_p": "20"}, Q("S001", *T3),
        ["p (2010 purchase of a lease of a Leeds flat) read as a land transaction within the Act (landtxn)"]),
    solo("S002", "125000.00", facts=HOUSE + WITHGARDEN,
         judgement=["the shed standing in the garden read as part of the garden land (extraland, extragarden), "
                    "not a further building (multidwelling false)"]),
    solo("S003", "125001.00", facts=HOUSE + ["extraland", "extrabenefit"]),
    solo("S004", "149999.00", facts=["freehold", "usedsingle", "landtxn", "multidwelling", "extraland"],
         judgement=["the separate shop building read as a second building (multidwelling) and land besides the house "
                    "(extraland)"]),
    solo("S005", "150000.00", facts=OWN, pt=[("acquires", "a", "t")]),
    solo("S006", "150001.00", facts=OWN + ["suitablesingle", "used116"]),
    # S007: t = Nina and Owen's Exeter house; u = Quentin's Durham field; p = Owen's 2015 Plymouth house
    rec("S007", ["t", "u", "p"], ["n", "o", "qn"],
        {"t": HOUSE, "u": OWN, "p": ["freehold", "usedsingle", "landtxn"], "n": IND, "o": IND, "qn": IND},
        [("acquires", "n", "t"), ("acquires", "o", "t"), ("intends", "n", "t"), ("intends", "o", "t"),
         ("acquires", "qn", "u"), ("acquires", "o", "p")],
        [("earlier", "p", "t"), ("earlier", "p", "u")],
        {"cons_t": "249999.00", "cons_u": "249999.00"}, Q("S007", *T6),
        ["p (2015 purchase of a Plymouth freehold) read as a land transaction within the Act (landtxn)"]),
    # S008: t = Thomas's Chester house; u = Wendy's Worcester yard; p = Thomas's 2012 Manchester flat lease
    rec("S008", ["t", "u", "p"], ["th", "w"],
        {"t": HOUSE, "u": OWN, "p": ["lease", "usedsingle", "landtxn"], "th": IND, "w": IND},
        [("acquires", "th", "t"), ("intends", "th", "t"), ("acquires", "w", "u"), ("acquires", "th", "p")],
        [("earlier", "p", "t"), ("earlier", "p", "u")],
        {"cons_t": "250000.00", "cons_u": "250000.00", "years_p": "21"}, Q("S008", *T6),
        ["p (2012 purchase of a lease of a Manchester flat) read as a land transaction within the Act (landtxn)"]),
    # S009: t = Yasmin's empty Lancaster house; u = Adrian's Coventry warehouse
    rec("S009", ["t", "u"], ["y", "ad"],
        {"t": ["freehold", "allres", "suitablesingle", "landtxn"], "u": OWN, "y": IND, "ad": IND},
        [("acquires", "y", "t"), ("intends", "y", "t"), ("acquires", "ad", "u")], (),
        {"cons_t": "250001.00", "cons_u": "250001.00"}, Q("S009", *T6)),
    # S010: d = Daniel (bare trustee), e = Emma; p = Daniel's 2014 Reading house
    rec("S010", ["t", "p"], ["d", "e"],
        {"t": FLAT, "p": ["freehold", "usedsingle", "landtxn"], "d": IND, "e": IND},
        [("acquires", "d", "t"), ("baretrustee", "d", "t"), ("btbeneficiary", "e", "t"), ("intends", "e", "t"),
         ("acquires", "d", "p")], [("earlier", "p", "t")],
        {"cons_t": "299999.00", "years_t": "125"}, Q("S010", *T3),
        ["p (2014 purchase of a Reading freehold) read as a land transaction within the Act (landtxn)"]),
    # S011: hf = Harbour Finance, h = Hannah
    rec("S011", ["t"], ["hf", "h"], {"t": HOUSE + ["affirst"], "h": IND},
        [("acquires", "hf", "t"), ("afperson", "h", "t"), ("intends", "h", "t")], (),
        {"cons_t": "300000.00"}, Q("S011", *T3),
        ["Harbour Finance (a financial institution) read as not an individual"]),
    # S012: p = Isabel's 2011 Cardiff house lease
    rec("S012", ["t", "p"], ["i"], {"t": HOUSE, "p": ["lease", "usedsingle", "landtxn", "wales"], "i": IND},
        [("acquires", "i", "t"), ("intends", "i", "t"), ("acquires", "i", "p")], [("earlier", "p", "t")],
        {"cons_t": "300001.00", "years_p": "20"}, Q("S012", *T3),
        ["p (2011 Cardiff lease, before Welsh LTT) read as a land transaction within the Act (landtxn), situated in "
         "Wales (wales)"]),
    # S013: l = Leo, ol = Olivia; p = 2013 Sheffield flat lease granted to Leo as bare trustee for Olivia
    rec("S013", ["t", "p"], ["l", "ol"],
        {"t": ["freehold", "allres", "constructing", "landtxn"], "p": ["lease", "usedsingle", "landtxn"],
         "l": IND, "ol": IND},
        [("acquires", "l", "t"), ("intends", "l", "t"), ("acquires", "l", "p"), ("baretrustee", "l", "p"),
         ("btbeneficiary", "ol", "p")], [("earlier", "p", "t")],
        {"cons_t": "499999.00", "years_p": "99"}, Q("S013", *T3),
        ["p (2013 Sheffield lease grant) read as a land transaction within the Act (landtxn)"]),
    # S014: hf = Hearth Finance, m = Miriam
    rec("S014", ["t"], ["hf", "m"],
        {"t": ["freehold", "allres", "landtxn", "substperf", "tobebuilt", "notbegun", "affirst"], "m": IND},
        [("acquires", "hf", "t"), ("afperson", "m", "t"), ("intends", "m", "t")], (),
        {"cons_t": "500000.00"}, Q("S014", *T3),
        ["Hearth Finance (a financial institution) read as not an individual"]),
    solo("S015", "500001.00"),
    rec("S016", ["t"], ["s", "ta"], {"t": HOUSE, "s": IND, "ta": IND},
        [("acquires", "s", "t"), ("acquires", "ta", "t"), ("intends", "s", "t"), ("intends", "ta", "t")], (),
        {"cons_t": "924999.00"}, Q("S016", *T3)),
    solo("S017", "925000.00", facts=FLAT, years="87"),
    solo("S018", "925001.00", facts=HOUSE + WITHGARDEN),
    solo("S019", "1499999.00"),
    rec("S020", ["t"], ["ce", "de"], {"t": FLAT, "ce": IND, "de": IND},
        [("acquires", "ce", "t"), ("acquires", "de", "t"), ("intends", "ce", "t"), ("intends", "de", "t")], (),
        {"cons_t": "1500000.00", "years_t": "99"}, Q("S020", *T3)),
    solo("S021", "1500001.00", facts=HOUSE + WITHGARDEN,
         judgement=["the garage standing in the garden read as part of the garden and grounds (extraland, "
                    "extragarden), not a further building (multidwelling false)"]),
    # S022: t = Alina and Basil's York house; g = Alina's garden strip (same instant, linked)
    rec("S022", ["t", "g"], ["al", "ba"], {"t": HOUSE, "g": ["freehold", "allres", "landtxn"], "al": IND, "ba": IND},
        [("acquires", "al", "t"), ("acquires", "ba", "t"), ("intends", "al", "t"), ("intends", "ba", "t"),
         ("acquires", "al", "g")], both("t", "g") + [("gardenof", "g", "t")],
        {"cons_t": "300000.00", "cons_g": "100000.00"}, Q("S022", *G6)),
    # S023: t = Nadia's house and garden; g = right of way (no freehold or lease)
    rec("S023", ["t", "g"], ["na"], {"t": HOUSE + WITHGARDEN, "g": ["allres", "landtxn"], "na": IND},
        [("acquires", "na", "t"), ("intends", "na", "t"), ("acquires", "na", "g")],
        both("t", "g") + [("benefitof", "g", "t")],
        {"cons_t": "240000.00", "cons_g": "60000.00"}, Q("S023", *G6),
        ["g, a permanent right of way, read as neither a freehold nor a lease (a right over land: benefitof)"]),
    # S024: t = Olive's Durham house; g = Olive and Patrick's right of way
    rec("S024", ["t", "g"], ["ol", "pa"], {"t": HOUSE, "g": ["allres", "landtxn"], "ol": IND, "pa": IND},
        [("acquires", "ol", "t"), ("intends", "ol", "t"), ("intends", "pa", "t"), ("acquires", "ol", "g"),
         ("acquires", "pa", "g")], both("t", "g") + [("benefitof", "g", "t")],
        {"cons_t": "300000.00", "cons_g": "100000.00"}, Q("S024", *G6),
        ["g, a permanent right of way, read as neither a freehold nor a lease (a right over land: benefitof)"]),
    # S025-S027: t = the house, g = the later linked purchase; encoded as the state after g
    rec("S025", ["t", "g"], ["r"], {"t": HOUSE, "g": ["freehold", "allres", "landtxn"], "r": IND},
        [("acquires", "r", "t"), ("intends", "r", "t"), ("acquires", "r", "g")],
        both("t", "g") + [("gardenof", "g", "t"), ("earlier", "t", "g")],
        {"cons_t": "450000.00", "cons_g": "150000.00"}, Q("S025", "taxnr", "claim", "taxw")),
    rec("S026", ["t", "g"], ["um"], {"t": HOUSE, "g": OWN, "um": IND},
        [("acquires", "um", "t"), ("intends", "um", "t"), ("acquires", "um", "g")],
        both("t", "g") + [("earlier", "t", "g")],
        {"cons_t": "320000.00", "cons_g": "80000.00"}, Q("S026", "taxnr", "claim", "taxw")),
    rec("S027", ["t", "g"], ["y"], {"t": HOUSE, "g": ["freehold", "allres", "landtxn"], "y": IND},
        [("acquires", "y", "t"), ("intends", "y", "t"), ("acquires", "y", "g")],
        both("t", "g") + [("gardenof", "g", "t"), ("earlier", "t", "g")],
        {"cons_t": "300000.00", "cons_g": "100000.00"}, Q("S027", "taxnr", "claim", "taxw")),
    # S028: t = Lydia's Bristol house; g = garden-strip lease granted to Marcus as bare trustee for Lydia (asked);
    # p = Marcus's 2014 Leeds house
    rec("S028", ["t", "g", "p"], ["ly", "m"],
        {"t": HOUSE, "g": ["lease", "allres", "landtxn"], "p": ["freehold", "usedsingle", "landtxn"],
         "ly": IND, "m": IND},
        [("acquires", "ly", "t"), ("intends", "ly", "t"), ("acquires", "m", "g"), ("baretrustee", "m", "g"),
         ("btbeneficiary", "ly", "g"), ("acquires", "m", "p")],
        both("t", "g") + [("gardenof", "g", "t"), ("earlier", "p", "t"), ("earlier", "p", "g")],
        {"cons_t": "300000.00", "cons_g": "100000.00", "years_g": "20"}, Q("S028", *T3, item="g"),
        ["p (2014 purchase of a Leeds freehold) read as a land transaction within the Act (landtxn)"]),
    # S029: lease of a Cambridge house (21 years); p = 2010 Toronto lease (20 years)
    rec("S029", ["t", "p"], ["am"],
        {"t": FLAT, "p": ["lease", "usedsingle", "abroad", "equivalent"], "am": IND},
        [("acquires", "am", "t"), ("intends", "am", "t"), ("acquires", "am", "p")], [("earlier", "p", "t")],
        {"cons_t": "350000.00", "years_t": "21", "years_p": "20"}, Q("S029", *T3),
        ["the Toronto lease read as a lease (term of years) for the para. 6(2) rule (lease)"]),
    # S030: p = 2012 Ottawa lease (21 years)
    rec("S030", ["t", "p"], ["da"],
        {"t": HOUSE, "p": ["lease", "usedsingle", "abroad", "equivalent"], "da": IND},
        [("acquires", "da", "t"), ("intends", "da", "t"), ("acquires", "da", "p")], [("earlier", "p", "t")],
        {"cons_t": "400000.00", "years_p": "21"}, Q("S030", *T3),
        ["the Ottawa lease read as a lease (term of years) for the para. 6(2) rule (lease)"]),
    # S031: gi = Gita, he = Henry (bare trustee); p = 2011 Cardiff lease grant
    rec("S031", ["t", "p"], ["gi", "he"],
        {"t": HOUSE, "p": ["lease", "usedsingle", "landtxn", "wales"], "gi": IND, "he": IND},
        [("acquires", "gi", "t"), ("intends", "gi", "t"), ("acquires", "he", "p"), ("baretrustee", "he", "p"),
         ("btbeneficiary", "gi", "p")], [("earlier", "p", "t")],
        {"cons_t": "425000.00", "years_p": "21"}, Q("S031", *T3),
        ["p (2011 Cardiff lease grant, before Welsh LTT) read as a land transaction within the Act (landtxn), "
         "situated in Wales (wales)"]),
    # S032: p = Cedar Finance's 2015 Leeds house (Jamal 'the person'); q = Willow Finance's 2016 Nottingham house (Inez)
    rec("S032", ["t", "p", "q"], ["in", "ja", "cf", "wf"],
        {"t": HOUSE, "p": ["freehold", "usedsingle", "landtxn", "affirst"],
         "q": ["freehold", "usedsingle", "landtxn", "affirst"], "in": IND, "ja": IND},
        [("acquires", "in", "t"), ("acquires", "ja", "t"), ("intends", "in", "t"), ("intends", "ja", "t"),
         ("acquires", "cf", "p"), ("afperson", "ja", "p"), ("acquires", "wf", "q"), ("afperson", "in", "q")],
        [("earlier", "p", "t"), ("earlier", "q", "t")],
        {"cons_t": "450000.00"}, Q("S032", *T3),
        ["p, q (2015 Leeds, 2016 Nottingham purchases) read as land transactions within the Act (landtxn)",
         "Cedar Finance and Willow Finance (financial institutions) read as not individuals"]),
    # S033: p = Larch Finance's 2000 Leeds house purchase under the arrangement with Kiran
    rec("S033", ["t", "p"], ["k", "lf"],
        {"t": HOUSE, "p": ["freehold", "usedsingle"], "k": IND},
        [("acquires", "k", "t"), ("intends", "k", "t"), ("acquires", "lf", "p"), ("wouldbeaf", "k", "p")],
        [("earlier", "p", "t")],
        {"cons_t": "275000.00"}, Q("S033", *T3),
        ["p (9 March 2000, before SDLT) read as not a land transaction within the Act and not a first transaction "
         "under ss. 71A/73 (landtxn, affirst false)",
         "Larch Finance (a financial institution) read as not an individual"]),
    solo("S034", "200000.00", facts=FLAT, years="20"),
    solo("S035", "350000.00", facts=HOUSE + ["hrt"], forms=("claim",)),
]

PROBES = {
    "S036": "non-resident transaction (Sch. 9A): outside s. 55 / Sch. 6ZA as given",
    "S037": "company purchaser; Sch. 4A para. 3 applies, so s. 55 does not apply",
    "S038": "s. 74(1A) step 4 applies, so s. 55 does not apply in the ordinary way",
    "S039": "land in Wales: land transaction tax, not SDLT",
    "S040": "land in Scotland: LBTT, not SDLT",
    "S041": "new lease with rent: rent (Sch. 5) outside the given law",
    "S042": "chargeable consideration for the land not stated",
    "S043": "whether the land is entirely residential is not stated",
    "S044": "whether the building is suitable for use as a single dwelling is not stated",
    "S045": "whether the Toronto lease was an equivalent interest is not stated",
}
PROBE_QIDS = {cid: [f"{cid}-{i}" for i in (1, 2, 3)] for cid in PROBES}
UNSUPPORTED = {}
