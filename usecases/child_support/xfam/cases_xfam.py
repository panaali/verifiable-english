"""The encoder's file for the frozen child support translation (CSA 1991 Sch. 1 Part I). Copy to out/cases_xfam.py and fill.

This template is the build's cases.py with its own records and probes removed (they encoded another question set).
The frozen run.py reads CASES, PROBES, PROBE_QIDS and UNSUPPORTED from this module; encode.py turns each record into facts
(its conventions C1-C6: read encode.py's docstring).

Each case: "parent" (the non-resident parent's item), "children", "persons" (everyone else the facts name: persons with care,
spouses, civil partners, people lived with), "benefits" (each benefit, pension or allowance named for the week), "facts"
(item -> unary facts of translation.FACTS true of it), "pairs" ("<a>@<b>" -> binary facts of translation.BINARY true of
the pair; every other one false, encode C1), "ints" (stated amounts and nights: names "<base>_<item>" with base in
translation.STATED_INTS; the parent's gross weekly income is the case() argument inc), "questions" (qid -> item and form:
rate = Q1 (item: the parent), amount = Q2 (item: the person with care named in the question), share = Q3 (item: the child
named in the question)), "judgement" (anything the encoder decided beyond copying a stated fact: listed as "encoder
judgement"). Items are any short lower-case names; use the same item for the same person throughout a case.
Standing readings the build used for the writer's fixed facts (every case): "no maintenance order / agreement" -> morder,
agree false; "no regulations under 10A", "no prescribed description under 10C(2)(b)", "not a variation" -> those facts
false; "receives <benefit> for the week" -> paid in respect of the week (encode C5); child benefit named as received is
also a benefit item (CHB below), prescribed for neither 4(1)(b) nor 4(1)(c) where the case says so.
PROBES: {case id: why} for out-of-scope cases (every answer UNSUPPORTED), with PROBE_QIDS {case id: [its qids]}.
UNSUPPORTED: {case id: (why, [its qids])} for an in-scope case the vocabulary cannot state.
"""
from __future__ import annotations

QC = ["qcalc", "childof"]          # a qualifying child of the calculation (stated), the parent's child
OTHER = []                          # a child who is not a qualifying child, no arrangement


def case(cid, parent, inc, qc, qs, others=(), persons=(), benefits=(), facts=None, pairs=None, ints=None,
         nights=None, judgement=()):
    """qc: {child: person with care}; qs: [(item, form)] numbered cid-1, cid-2, ...; nights: {child: n}."""
    children = list(qc) + list(others)
    people = []
    for w in list(qc.values()) + list(persons):
        if w not in people:
            people.append(w)
    f = {ch: list(QC) for ch in qc}
    for item, more in (facts or {}).items():
        f.setdefault(item, [])
        f[item] = sorted(set(f[item]) | set(more))
    pr = {f"{ch}@{w}": ["pwc"] for ch, w in qc.items()}
    for kk, more in (pairs or {}).items():
        pr[kk] = sorted(set(pr.get(kk, [])) | set(more))
    i = {f"inc_{parent}": inc}
    i.update({f"nights_{ch}": str(n) for ch, n in (nights or {}).items()})
    i.update(ints or {})
    return {"id": cid, "parent": parent, "children": children, "persons": people, "benefits": list(benefits),
            "facts": f, "pairs": pr, "ints": i,
            "questions": [{"qid": f"{cid}-{n}", "item": it, "form": fm} for n, (it, fm) in enumerate(qs, 1)],
            "judgement": list(judgement)}


def rate(x): return (x, "rate")
def amt(w): return (w, "amount")
def share(ch): return (ch, "share")


CHB = {"chb": []}  # child benefit as a benefit item: prescribed for neither 4(1)(b) nor 4(1)(c)

RAS = [rate("sam"), amt("bea"), share("ava")]
RA = [rate("sam"), amt("bea")]
ONE = {"ava": "bea"}
UK_RES = "child stated to habitually reside in England / Wales / Scotland entered as habuk (habitually resident in the UK)"

CASES = [
    # one qualifying child, Bea the person with care, no partner, no benefits: income and nights vary
    case("M001", "sam", "6.99", ONE, RAS, nights={"ava": 51}),
    case("M002", "sam", "7.00", ONE, RAS, nights={"ava": 52}),
    case("M003", "sam", "99.99", ONE, RAS, nights={"ava": 103}),
    case("M004", "sam", "100.00", ONE, RAS, nights={"ava": 104}),
    case("M005", "sam", "100.01", ONE, RAS, ints={"redrate_sam": "21.00"}, nights={"ava": 51}),
    case("M006", "sam", "199.99", ONE, RAS, ints={"redrate_sam": "21.00"}, nights={"ava": 52}),
    case("M007", "sam", "200.00", ONE, RA, nights={"ava": 0}),
    case("M008", "sam", "200.01", ONE, RAS, nights={"ava": 0}),
    case("M009", "sam", "799.99", ONE, RAS, nights={"ava": 0}),
    case("M010", "sam", "800.00", ONE, RA, nights={"ava": 0}),
    case("M011", "sam", "800.01", ONE, RAS, nights={"ava": 0}),
    case("M012", "sam", "2999.99", ONE, RAS, nights={"ava": 0}),
    case("M013", "sam", "3000.00", ONE, RAS, nights={"ava": 103}),
    case("M014", "sam", "3000.01", ONE, RAS, nights={"ava": 104}),
    case("M015", "sam", "700.00", {"ava": "bea", "ben": "bea"}, RAS, nights={"ava": 155, "ben": 0}),
    case("M016", "sam", "700.00", ONE, RAS, nights={"ava": 156}),
    case("M017", "sam", "700.00", ONE, RAS, nights={"ava": 174}),
    case("M018", "sam", "700.00", ONE, RAS, nights={"ava": 175}),
    case("M019", "sam", "700.00", {"ava": "bea", "ben": "bea"}, RAS, nights={"ava": 175, "ben": 175}),
    case("M020", "sam", "1000.00", {"ava": "bea", "ben": "bea", "cora": "bea"}, RAS,
         nights={"ava": 52, "ben": 104, "cora": 156}),
    case("M021", "sam", "1000.00", {"ava": "bea", "ben": "bea", "cora": "dana", "ella": "dana"},
         [rate("sam"), amt("bea"), amt("dana"), share("ava")], nights={"ava": 0, "ben": 0, "cora": 0, "ella": 0}),
    # child benefit and relevant other children
    case("M022", "sam", "1000.00", ONE, RA, others=["finn"], benefits=["chb"], facts=CHB,
         pairs={"sam@finn": ["cbpaid"], "sam@ava": ["cbpaid"], "sam@chb": ["paid"]}, nights={"ava": 0},
         judgement=["child benefit Sam receives entered as one benefit item chb paid to Sam (standing reading)"]),
    case("M023", "sam", "200.00", ONE, RA, others=["finn", "hana", "juno"], benefits=["chb"], facts=CHB,
         pairs={"sam@finn": ["cbpaid"], "sam@hana": ["cbpaid"], "sam@chb": ["paid"]}, nights={"ava": 0},
         judgement=["child benefit Sam receives entered as one benefit item chb paid to Sam (standing reading)"]),
    case("M024", "sam", "1000.00", ONE, RA, others=["finn", "hana", "ivan"], persons=["lee"], benefits=["chb"],
         facts=CHB, pairs={"sam@lee": ["married", "samehh"], "lee@finn": ["cbpaid"], "lee@hana": ["cbpaid"],
                           "lee@ivan": ["cbpaid"], "lee@chb": ["paid"]}, nights={"ava": 0},
         judgement=["child benefit Lee receives entered as one benefit item chb paid to Lee (standing reading)",
                    "'married, live together' entered as married + samehh, not livetog (no stated 10C(5)(b) judgment)"]),
    # benefits, partners, 4(1)(b), 4(1)(c), 4(2), 5(a)
    case("M025", "sam", "640.00", ONE, RA, benefits=["pension"], facts={"sam": ["presc5a"], "pension": ["b41b"]},
         pairs={"sam@pension": ["paid"]}, nights={"ava": 175}),
    case("M026", "sam", "640.00", ONE, RAS, benefits=["allowance"], facts={"allowance": ["b41b"]},
         pairs={"sam@allowance": ["due"]}, nights={"ava": 51},
         judgement=["allowance due but not yet paid for the week entered as due (not paid)"]),
    case("M027", "sam", "640.00", ONE, RAS, persons=["lee"], benefits=["benefit"],
         facts={"lee": ["alsonrp", "calcinforce"], "benefit": ["b41c"]},
         pairs={"sam@lee": ["married", "samehh"], "lee@benefit": ["paid"]},
         ints={"flatamt_sam": "10.00"}, nights={"ava": 52},
         judgement=["'married, live together' entered as married + samehh, not livetog (no stated 10C(5)(b) judgment)"]),
    case("M028", "sam", "640.00", ONE, RAS, persons=["lee"], benefits=["benefit"], facts={"benefit": ["b41c"]},
         pairs={"sam@lee": ["civil", "samehh"], "lee@benefit": ["paid"]}, nights={"ava": 52},
         judgement=["'civil partners, live together' entered as civil + samehh, not livetog (no stated "
                    "10C(5)(b) judgment)"]),
    case("M029", "sam", "640.00", ONE, RAS, persons=["lee"], benefits=["benefit"],
         facts={"lee": ["alsonrp"], "benefit": ["b41c"]},
         pairs={"sam@lee": ["livetog", "samehh"], "lee@benefit": ["paid"]}, nights={"ava": 52}),
    case("M030", "sam", "640.00", ONE, RAS, persons=["lee", "nora"], benefits=["benefit"],
         facts={"lee": ["alsonrp", "calcinforce"], "benefit": ["b41c"]},
         pairs={"sam@lee": ["polyg", "oppsex", "samehh"], "sam@nora": ["polyg", "oppsex", "samehh"],
                "lee@benefit": ["due"]},
         ints={"flatamt_sam": "3.50"}, nights={"ava": 51},
         judgement=["polygamous husband/wife entered as polyg (+ oppsex: man / women, samehh), not also as married",
                    "benefit due but not yet paid for the week entered as due (not paid)"]),
    # para. 5A: other maintenance arrangements
    case("M031", "sam", "600.00", {"ava": "bea", "ben": "bea"}, RAS, others=["cora"],
         facts={"cora": ["childof", "morder", "habuk"]}, nights={"ava": 0, "ben": 0, "cora": 0},
         judgement=[UK_RES + " (Cora, England)",
                    "Bea 'has care of' Cora (not a qualifying child) not entered as pwc"]),
    case("M032", "sam", "150.00", ONE, RAS, others=["ben"], facts={"ben": ["childof", "agree", "agree_presc", "habuk"]},
         ints={"redrate_sam": "7.00", "redrateh_sam": "7.00"}, nights={"ava": 0, "ben": 0},
         judgement=[UK_RES + " (Ben, Wales)",
                    "the one stated reduced rate (7.00, 'including the calculation with the arrangement children') "
                    "entered as both redrate and redrateh",
                    "Bea 'has care of' Ben (not a qualifying child) not entered as pwc"]),
    case("M033", "sam", "600.00", ONE, RA, others=["ben", "cora"], persons=["dana"],
         facts={"ben": ["childof", "agree", "habuk"], "cora": ["childof", "morder"]}, nights={"ava": 0},
         judgement=[UK_RES + " (Ben, Scotland); Cora (France) not habuk",
                    "Ben living with Bea and Cora with Dana not entered as pwc (neither a qualifying child)"]),
    case("M034", "sam", "150.00", {"ava": "bea", "ben": "dana"}, [rate("sam"), amt("bea"), amt("dana"), share("ava")],
         ints={"redrate_sam": "14.00"}, nights={"ava": 175, "ben": 175}),
    case("M035", "sam", "4000.00", ONE, RAS, others=["finn"], benefits=["chb"], facts=CHB,
         pairs={"sam@finn": ["cbpaid"], "sam@chb": ["paid"]}, nights={"ava": 0},
         judgement=["child benefit Sam receives entered as one benefit item chb paid to Sam (standing reading)"]),
]

UNSUPPORTED = {}
PROBES = {
    "M036": "Northern Ireland child support law, not the Great Britain Act's Schedule 1",
    "M037": "pre-2003 scheme assessment, not the current scheme",
    "M038": "2003-2012 scheme assessment, not the current scheme",
    "M039": "undecided special-expenses variation: variations are outside the text",
    "M040": "gross weekly income not determined; working it out from a pay slip needs the regulations",
    "M041": "gross weekly income not determined; working it out from a tax return needs the regulations",
    "M042": "whether the allowance is prescribed for 4(1)(b) or (c) is not supplied",
    "M043": "para. 10A regulations substitute a percentage that is not supplied",
}
PROBE_QIDS = {"M036": ["M036-1"], "M037": ["M037-1"], "M038": ["M038-1"], "M039": ["M039-1"], "M040": ["M040-1"],
              "M041": ["M041-1"], "M042": ["M042-1"], "M043": ["M043-1"]}
