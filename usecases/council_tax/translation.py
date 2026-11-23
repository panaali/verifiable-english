"""Council tax England, LGFA 1992 (statute corpus batch 2, law 5): the VE translation, one pass with today's language.

Row statute-corpus-council-tax (dri-statute-corpus-council-tax-1123, Opus 5.5). SAME-FAMILY. Written from the pinned
source only (manage-agents reviews/spare/statute-corpus/batch2/council-tax/source.txt, sha256 44b9e045...a54c17) BEFORE
the encoder's question file was opened. Evidence branch: nothing here is a Lean kernel line, a profile, a refuses pair
or a lint change; nothing merges.

UNITS maps each in-scope unit n of batch2/council-tax/units.jsonl (tools/sample5.py --units council-tax) to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one case;
  ("PART", builder, cause, note) written except the part named in the note (bridged / stated / name / not written);
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2 + "other:table lookup").
Grounding is mechanical: a rule "for every person / day" is written once per person / day item the case names; "only
one resident", "each of them except one" and "no resident" are conjunctions / disjunctions over the case's person items
(closed world over the case's named persons: an encoding convention stated in encode.py). No number from a case's facts
is ever put into a rule as a coefficient (ISOLATION.md D3a): every coefficient below is a literal of the pinned text, or
one of the values a rule enumerates (D = 365, D = 366).
Vocabulary: one sort "item" (the dwelling w, value items, day items, person items, financial-year items); unary facts
and derived predicates on items; binary facts on (person, day) and (day, year); per-item integer constants (money in
gbp_penny, days in day, D in elapsed_day).
"""
from __future__ import annotations

import hashlib
import json

GBP, DAY, NDAYS = "gbp_penny", "day", "elapsed_day"
INT_UNITS = {  # per-item integer constants: base name -> (unit, words)
    "value": (GBP, "the value of the dwelling (a band question)"),
    "date": (DAY, "the day"),
    "amt": (GBP, "the amount set by the authority for the financial year for dwellings in the dwelling's listed band"),
    "amtd": (GBP, "the amount set by the authority for the financial year for dwellings in valuation band D"),
    "days": (NDAYS, "the number of days in the financial year"),
    "base": (GBP, "the amount calculated by the formula A / D for the day (s. 10(1))"),
    "pay": (GBP, "the amount of council tax payable for the day after any discount"),
    "certfrom": (DAY, "the first day of the period the medical certificate refers to"),
    "certto": (DAY, "the last day of the period the medical certificate refers to"),
}
BANDS = "ABCDEFGH"
PROPORTION = dict(zip(BANDS, (6, 7, 8, 9, 11, 13, 15, 18)))  # s. 5(1): "6: 7: 8: 9: 11: 13: 15: 18", 6 for band A ...
TABLE = [  # s. 5(2), England: each row as the text gives it (exceeding, not exceeding), pounds
    ("A", None, "40000.00"), ("B", "40000.00", "52000.00"), ("C", "52000.00", "68000.00"),
    ("D", "68000.00", "88000.00"), ("E", "88000.00", "120000.00"), ("F", "120000.00", "160000.00"),
    ("G", "160000.00", "320000.00"), ("H", "320000.00", None)]
APPROPRIATE = "25"  # s. 11(3): "the appropriate percentage" means 25 per cent (no order: fixed fact)

FACTS = {  # unary facts on an item (the encoder states each true or false)
    **{f"list_{b.lower()}": f"the billing authority's valuation list shows valuation band {b} as applicable to the dwelling"
       for b in BANDS},
    "has_cert": "a certificate of a registered medical practitioner states that the person has been or is likely to be "
                "severely mentally impaired as regards a period",
    "cert_open": "the period the certificate refers to has no last day",
}
BINARY = {  # binary facts: (person, day) unless marked (day, year)
    "resident": "the person is a resident of the dwelling on the day",
    "in_custody": "on the day the person is detained in a prison, a hospital or any other place",
    "basis_order": "the person's detention (or the detention he is temporarily discharged or released from) is by "
                   "virtue of an order or award",
    "basis_sentence": "the person's detention (or the detention he is temporarily discharged or released from) is by "
                      "virtue of a sentence, direction, warrant or other means of giving effect to the decision of a court",
    "uk_court": "that order, award, sentence, direction or warrant is of (gives effect to the decision of) a court in "
                "the United Kingdom",
    "service_offence": "that order or award was made in proceedings in respect of a service offence within the meaning "
                       "of the Armed Forces Act 2006",
    "under_ia1971": "the person is detained under paragraph 2 of Schedule 3 to the Immigration Act 1971",
    "under_mha1983": "the person is detained under Part II or section 46, 47, 48 or 136 of the Mental Health Act 1983",
    "under_scot": "the person is detained under Parts 5, 6 and 7 or sections 136 or 297 of the Mental Health (Care and "
                  "Treatment)(Scotland) Act 2003 or sections 52D or 52M of the Criminal Procedure (Scotland) Act 1995",
    "temp_released": "the person is temporarily discharged under s. 28 Prison Act 1952 or released under rules under "
                     "its s. 47(5), or released under rules under s. 300 Armed Forces Act 2006, or discharged under "
                     "s. 27 Prisons (Scotland) Act 1989 or released under rules under its s. 39(6)",
    "under_sch4_8": "the person is detained under regulations made under paragraph 8 of Schedule 4 to this Act",
    "fine_default": "the person is detained under s. 76 Magistrates' Courts Act 1980 or s. 108 Powers of Criminal Courts "
                    "(Sentencing) Act 2000 for default in payment of a fine",
    "only_cps1975": "the person is detained only under section 407 of the Criminal Procedure (Scotland) Act 1975",
    "severe_imp": "the person has a severe impairment of intelligence and social functioning (however caused) "
                  "(stated judgment)",
    "appears_perm": "the person's impairment appears to be permanent (stated judgment)",
    "cond2c": "as regards the day the person fulfils the conditions prescribed by order under para. 2(1)(c)",
    "age18": "the person has attained the age of 18 years on the day (from the bridge script only)",
    "cb_entitled": "another person is entitled to child benefit in respect of the person",
    "cb_but_for": "another person would be entitled to child benefit in respect of the person but for paragraph 1(c) "
                  "of Schedule 9 to the Social Security Contributions and Benefits Act 1992",
    "student": "the person is a student within the meaning assigned by order (para. 4(2))",
    "student_nurse": "the person is a student nurse within the meaning assigned by order (para. 4(2))",
    "apprentice": "the person is an apprentice within the meaning assigned by order (para. 4(2))",
    "ytt": "the person is a youth training trainee within the meaning assigned by order (para. 4(2))",
    "cond4b": "the conditions prescribed by order under para. 4(1)(b) are fulfilled",
    "patient": "the person is a patient",
    "smr_inst": "the person has his sole or main residence in the institution the facts name (stated judgment)",
    "inst_hs_hospital": "that institution is a health service hospital within the meaning of the National Health "
                        "Service Act 2006, the NHS (Wales) Act 2006 or s. 108(1) NHS (Scotland) Act 1978",
    "inst_mil_med": "that institution is a military, air-force or naval unit or establishment at or in which medical or "
                    "surgical treatment is provided for persons subject to service law (Armed Forces Act 2006)",
    "inst_cs2000_care_home": "that institution is a care home within the meaning of the Care Standards Act 2000",
    "inst_sswb_adult": "that institution is a building or part in which accommodation is provided for an adult under "
                       "Part 4 of the Social Services and Well-being (Wales) Act 2014",
    "inst_care_act": "that institution is a building or part in which accommodation is provided under Part 1 of the "
                     "Care Act 2014",
    "inst_s275_hospital": "that institution is a hospital as defined by s. 275 of the National Health Service Act 2006",
    "inst_csa2000_indep": "that institution is an independent hospital within the meaning of the Care Standards Act 2000",
    "inst_hostel": "that institution falls within a definition of hostel prescribed by order under para. 7(2)",
    "inst_england": "that institution is in England",
    "inst_wales": "that institution is in Wales",
    "receiving_care": "the person is receiving care or treatment (or both) in that institution",
    "in_year": "(day, year) the day falls in the financial year",
}
DAY_YEAR = ("in_year",)
STATED = ("severe_imp", "appears_perm", "smr_inst")
BRIDGED = ("age18",)
DERIVED_UNARY = {
    **{f"tband_{b.lower()}": f"under the Table in s. 5(2) the value is in valuation band {b}" for b in BANDS},
    **{f"listed_{b.lower()}": f"the dwelling is listed in valuation band {b} (s. 5(6))" for b in BANDS},
    "l11_1a": "s. 11(1)(a) holds on the day", "l11_1b": "s. 11(1)(b) holds on the day",
    "disc1": "the amount for the day is subject to a discount of the appropriate percentage (s. 11(1))",
    "l11_2a": "s. 11(2)(a) holds on the day", "l11_2b": "s. 11(2)(b) holds on the day",
    "disc2": "the amount for the day is subject to a discount of twice the appropriate percentage (s. 11(2))",
}
DERIVED_BINARY = {
    "detained": "for the purposes of Sch. 1 para. 1(1) the person is detained on the day (para. 1(3))",
    "order": "the detention is by virtue of an order (para. 1(5): an order includes a sentence, direction, warrant ...)",
    "applies12": "the order or award is one to which Sch. 1 para. 1(2) applies",
    "p1a": "Sch. 1 para. 1(1)(a) holds", "p1bcd": "Sch. 1 para. 1(1)(b), (c) or (d) holds",
    "exc14": "Sch. 1 para. 1(4) takes the person out of para. 1(1)",
    "dis1": "disregarded under Sch. 1 para. 1", "smi": "severely mentally impaired (Sch. 1 para. 2(2))",
    "cert_covers": "the certificate's period includes the day", "dis2": "disregarded under Sch. 1 para. 2",
    "dis3": "disregarded under Sch. 1 para. 3", "dis4": "disregarded under Sch. 1 para. 4",
    "hospital6": "the institution is a hospital (Sch. 1 para. 6(2))", "dis6": "disregarded under Sch. 1 para. 6",
    "care_home": "the institution is a care home (Sch. 1 para. 7(2))",
    "indep_hosp": "the institution is an independent hospital (Sch. 1 para. 7(2))",
    "hostel7": "the institution is a hostel (Sch. 1 para. 7(2))", "dis7": "disregarded under Sch. 1 para. 7",
    "disregarded": "the person falls to be disregarded for the purposes of discount on the day (s. 11(5), Sch. 1)",
}


# --- formula helpers (the ve-quantity@1 wire shapes; tenant_fees / pawhp conventions) ----------------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def B(p, x, y): return ["binary", p, c(x), c(y)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def gbp(v): return ["decimal", GBP, v]
def ndays(v): return ["decimal", NDAYS, v]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def scale(tag, k, t): return ["scale", tag, str(k), t]
def no_later(a, b): return ["date_no_later", a, b]
TRUE, FALSE = ["top"], ["bottom"]


def And(*fs):
    fs = [f for f in fs if f is not None]
    if not fs:
        return TRUE
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["and", f, r]
    return r


def Or(*fs):
    fs = [f for f in fs if f is not None]
    if not fs:
        return FALSE
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["or", f, r]
    return r


def k(base, x):
    """Per-item integer constant."""
    return ["const", INT_UNITS[base][0], f"{base}_{x}"]


def iff_u(p, x, body): return Iff(U(p, x), body)
def iff_b(p, x, y, body): return Iff(B(p, x, y), body)


# --- the case context ---------------------------------------------------------------------------------------------

class Ctx:
    """items by kind: dwelling (w), values, days, persons, years; links = the stated in_year (day, year) pairs."""

    def __init__(self, dwelling=None, values=(), days=(), persons=(), years=(), links=()):
        self.dwelling = dwelling
        self.values, self.days, self.persons, self.years = list(values), list(days), list(persons), list(years)
        self.links = {tuple(x) for x in links}

    @property
    def items(self):
        return ([self.dwelling] if self.dwelling else []) + self.values + self.days + self.persons + self.years

    def pd(self):
        return [(p, d) for d in self.days for p in self.persons]

    def years_of(self, d):
        return [y for (p, a, y) in sorted(self.links) if p == "in_year" and a == d]


def per_pd(fn):
    return lambda ctx: [f for (p, d) in ctx.pd() for f in fn(p, d, ctx)]


def per_day(fn):
    return lambda ctx: [f for d in ctx.days for f in fn(d, ctx)]


def per_value(fn):
    return lambda ctx: [f for v in ctx.values for f in fn(v, ctx)]


def per_dwelling(fn):
    return lambda ctx: fn(ctx.dwelling, ctx) if ctx.dwelling else []


def _row(b, lo, hi):
    def build(v, ctx):
        val = k("value", v)
        cond = And(Lt(gbp(lo), val) if lo else None, Le(val, gbp(hi)) if hi else None)
        return [iff_u(f"tband_{b.lower()}", v, cond)]
    return per_value(build)


def _proportion(ctx):
    """s. 5(1): the amounts for different bands are in the proportion 6: ... : 18, band D's being 9."""
    w = ctx.dwelling
    if not w:
        return []
    return [Implies(U(f"listed_{b.lower()}", w), Eq(scale(GBP, 9, k("amt", y)), scale(GBP, PROPORTION[b], k("amtd", y))))
            for y in ctx.years for b in BANDS]


def _day_amount(d, ctx):
    """s. 10(1): amount = A / D, written as D x amount = A by the case split D = 365 / D = 366 (D3a)."""
    out = []
    for y in ctx.years_of(d):
        for n in ("365", "366"):
            out.append(Implies(And(B("in_year", d, y), Eq(k("days", y), ndays(n))),
                               Eq(scale(GBP, n, k("base", d)), k("amt", y))))
    return out


def _discount_amounts(d, ctx):
    """s. 11(1)/(2) with (3): the amount for the day is subject to a discount of 25 per cent / twice 25 per cent;
    written as 100 x payable = (100 - percentage) x the day's amount (whole-number coefficients only in the language)."""
    pct, twice = int(APPROPRIATE), 2 * int(APPROPRIATE)
    left = lambda: scale(GBP, 100, k("pay", d))
    return [Implies(And(U("disc2", d)), Eq(left(), scale(GBP, 100 - twice, k("base", d)))),
            Implies(And(U("disc1", d), Not(U("disc2", d))), Eq(left(), scale(GBP, 100 - pct, k("base", d)))),
            Implies(And(Not(U("disc1", d)), Not(U("disc2", d))), Eq(k("pay", d), k("base", d)))]


def _s11_1(d, ctx):
    P = ctx.persons
    res = lambda p: B("resident", p, d)
    dis = lambda p: B("disregarded", p, d)
    a = Or(*[And(res(p), Not(dis(p)), *[Not(res(q)) for q in P if q != p]) for p in P])
    b = Or(*[And(res(p), Not(dis(p)), Or(*[res(q) for q in P if q != p]),
                 *[Implies(res(q), dis(q)) for q in P if q != p]) for p in P])
    return [iff_u("l11_1a", d, a), iff_u("l11_1b", d, b), iff_u("disc1", d, Or(U("l11_1a", d), U("l11_1b", d)))]


def _s11_2(d, ctx):
    P = ctx.persons
    res = lambda p: B("resident", p, d)
    a = And(*[Not(res(p)) for p in P])
    b = And(Or(*[res(p) for p in P]), *[Implies(res(p), B("disregarded", p, d)) for p in P])
    return [iff_u("l11_2a", d, a), iff_u("l11_2b", d, b), iff_u("disc2", d, Or(U("l11_2a", d), U("l11_2b", d)))]


def _disregarded(p, d, ctx):
    """s. 11(5) closes over Sch. 1; fixed fact: no paragraph but 1, 2, 3, 4, 6, 7 (and no order) applies."""
    return [iff_b("disregarded", p, d, Or(*[B(f"dis{n}", p, d) for n in (1, 2, 3, 4, 6, 7)]))]


UNITS = {
    # ---- s. 5 ----
    1: ("RULE", _proportion, "s. 5(1): 9 x A(band) = p(band) x A(band D), p = 6, 7, 8, 9, 11, 13, 15, 18 (the text's "
        "literals; linear). Used where a case gives A only for band D (ISOLATION.md D2)"),
    **{n: ("RULE", _row(b, lo, hi), f"s. 5(2) Table row {b}: an interval on the stated value, as the text gives it")
       for n, (b, lo, hi) in zip(range(2, 10), TABLE)},
    10: ("RULE", per_dwelling(lambda w, ctx: [iff_u(f"listed_{b.lower()}", w, U(f"list_{b.lower()}", w)) for b in BANDS]),
         "s. 5(6): listed in a band = the band shown as applicable in the valuation list (deeming 'construed as')"),
    # ---- s. 10 ----
    11: ("PART", per_day(_day_amount), "amount arithmetic",
         "s. 10(1) A / D for ONE day: written as D x amount = A by the case split D = 365 / 366 (no product of two "
         "quantities in the language; ISOLATION.md D3a). NOT written: the amount over a run of several days (a count "
         "of days times a day's amount, summed over the parts of the run). 'Subject to ss. 11 to 13A': 11A-13A given "
         "'none'"),
    # ---- s. 11 ----
    12: ("RULE", lambda ctx: [f for d in ctx.days for f in _s11_1(d, ctx) + _discount_amounts(d, ctx)[1:]],
         "s. 11(1)(a), (b) over the case's named persons; the discounted amount (1 - 25/100) x the day's amount"),
    13: ("RULE", lambda ctx: [f for d in ctx.days for f in _s11_2(d, ctx) + _discount_amounts(d, ctx)[:1]],
         "s. 11(2)(a), (b); twice the appropriate percentage. 'Subject to ss. 11A-11C': given 'none'"),
    14: ("RULE", lambda ctx: [], "s. 11(3): 25 per cent (the literal in units 12 and 13's amount rules; no order: given)"),
    # ---- Sch. 1 para. 1 ----
    15: ("PART", per_pd(lambda p, d, ctx: [
        iff_b("p1a", p, d, And(B("detained", p, d), B("order", p, d), B("applies12", p, d))),
        iff_b("p1bcd", p, d, And(B("detained", p, d), Or(B("under_ia1971", p, d), B("under_mha1983", p, d),
                                                        B("under_scot", p, d)))),
        iff_b("dis1", p, d, And(Or(B("p1a", p, d), B("p1bcd", p, d)), Not(B("exc14", p, d))))]),
        "cross-reference", "para. 1(1): (a) written; (b)-(d) 'detained under <named enactment>' are stated facts "
        "(the enactments are not pinned)"),
    16: ("PART", per_pd(lambda p, d, ctx: [iff_b("applies12", p, d, Or(B("uk_court", p, d), B("service_offence", p, d)))]),
         "definition by reference", "para. 1(2): 'service offence within the meaning of the Armed Forces Act 2006' a "
         "stated fact; 'a court in the United Kingdom' a stated fact"),
    17: ("PART", per_pd(lambda p, d, ctx: [iff_b("detained", p, d, Or(B("in_custody", p, d), B("temp_released", p, d)))]),
         "cross-reference", "para. 1(3) 'treated as detained' written (deeming as classification); which release "
         "rules apply (Prison Act 1952 s. 47(5) etc.) are stated facts"),
    18: ("PART", per_pd(lambda p, d, ctx: [iff_b("exc14", p, d, Or(B("under_sch4_8", p, d), B("fine_default", p, d),
                                                               B("only_cps1975", p, d)))]),
         "cross-reference", "para. 1(4): written; the named detentions are stated facts"),
    19: ("RULE", per_pd(lambda p, d, ctx: [iff_b("order", p, d, Or(B("basis_order", p, d), B("basis_sentence", p, d)))]),
         "para. 1(5): 'order' includes a sentence, direction, warrant or other means (an open 'includes' carried as "
         "the listed members only)"),
    # ---- para. 2 ----
    20: ("PART", per_pd(lambda p, d, ctx: [
        iff_b("cert_covers", p, d, And(U("has_cert", p), no_later(k("certfrom", p), k("date", d)),
                                       Or(U("cert_open", p), no_later(k("date", d), k("certto", p))))),
        iff_b("dis2", p, d, And(B("smi", p, d), B("cert_covers", p, d), B("cond2c", p, d)))]),
        "cross-reference", "para. 2(1): (a), (b) written (the period includes the day: date comparisons); (c) the "
        "conditions prescribed by order are a stated fact"),
    21: ("PART", per_pd(lambda p, d, ctx: [iff_b("smi", p, d, And(B("severe_imp", p, d), B("appears_perm", p, d)))]),
         "other:judgment standard", "para. 2(2): 'severe impairment of intelligence and social functioning' and "
         "'appears to be permanent' are stated judgments (stated)"),
    # ---- para. 3 ----
    22: ("PART", per_pd(lambda p, d, ctx: [iff_b("dis3", p, d, And(B("age18", p, d),
                                                                  Or(B("cb_entitled", p, d), B("cb_but_for", p, d))))]),
         "date/age arithmetic", "para. 3(1): (a) 'attained the age of 18' BRIDGED (bridge/age.py); (b) child benefit "
         "entitlement (SSCBA 1992) a stated fact (cross-reference, secondary)"),
    # ---- para. 4 ----
    23: ("PART", per_pd(lambda p, d, ctx: [iff_b("dis4", p, d, And(Or(B("student", p, d), B("student_nurse", p, d),
                                                                     B("apprentice", p, d), B("ytt", p, d)),
                                                                  B("cond4b", p, d)))]),
         "cross-reference", "para. 4(1): written; (b) the conditions prescribed by order are a stated fact"),
    24: ("NOT", None, "definition by reference", "para. 4(2): the four words have the meanings assigned by order "
         "(not pinned): carried as names, stated facts"),
    # ---- para. 6 ----
    25: ("PART", per_pd(lambda p, d, ctx: [iff_b("dis6", p, d, And(B("patient", p, d), B("smr_inst", p, d),
                                                                  B("hospital6", p, d)))]),
         "other:judgment standard", "para. 6(1): written; 'sole or main residence' a stated judgment (stated)"),
    26: ("PART", per_pd(lambda p, d, ctx: [iff_b("hospital6", p, d, Or(B("inst_hs_hospital", p, d),
                                                                       B("inst_mil_med", p, d)))]),
         "definition by reference", "para. 6(2): (a) 'health service hospital within the meaning of' three Acts and "
         "(b) 'subject to service law within the meaning of the Armed Forces Act 2006' are stated facts"),
    # ---- para. 7 ----
    27: ("PART", per_pd(lambda p, d, ctx: [iff_b("dis7", p, d, And(
        B("smr_inst", p, d), Or(B("care_home", p, d), B("indep_hosp", p, d), B("hostel7", p, d)),
        Or(B("inst_england", p, d), B("inst_wales", p, d)), B("receiving_care", p, d)))]),
         "other:judgment standard", "para. 7(1): written; 'sole or main residence' a stated judgment (stated)"),
    28: ("PART", per_pd(lambda p, d, ctx: [iff_b("care_home", p, d, Or(B("inst_cs2000_care_home", p, d),
                                                                       B("inst_sswb_adult", p, d),
                                                                       B("inst_care_act", p, d)))]),
         "definition by reference", "para. 7(2) 'care home': three limbs, each by reference to another Act (facts)"),
    29: ("NOT", per_pd(lambda p, d, ctx: [iff_b("hostel7", p, d, B("inst_hostel", p, d))]),
         "definition by reference", "para. 7(2) 'hostel': anything within a definition prescribed by order (not "
         "pinned): carried as a name"),
    30: ("PART", per_pd(lambda p, d, ctx: [iff_b("indep_hosp", p, d, Or(
        And(B("inst_england", p, d), B("inst_s275_hospital", p, d), Not(B("inst_hs_hospital", p, d))),
        And(B("inst_wales", p, d), B("inst_csa2000_indep", p, d))))]),
         "definition by reference", "para. 7(2) 'independent hospital': (a) England written over two stated facts "
         "(s. 275 NHS Act 2006 hospital, health service hospital); (b) Wales 'same meaning as in the Care Standards "
         "Act 2000' a stated fact"),
}
# The closure of s. 11(5) over Sch. 1 (the in-scope paragraphs; the fixed fact excludes paras 5, 8-11 and orders) is
# grounded with unit 12 (it feeds s. 11's "falls to be disregarded").
EXTRA = [("disregarded", per_pd(_disregarded))]


def units_table(mutant=None):
    t = dict(UNITS)
    if mutant is not None:
        t = MUTANTS[mutant][1](t)
    return t


def rules(ctx, mutant=None):
    """Ground rules for a case: [{"id", "unit", "formula", "defines"}]."""
    out = []
    table = units_table(mutant)
    entries = [(n, e[1]) for n, e in sorted(table.items()) if e[1] is not None]
    entries += [(f"x-{name}", b) for name, b in EXTRA]
    for n, builder in entries:
        for i, f in enumerate(builder(ctx)):
            for j, part in enumerate(conjuncts(f)):
                out.append({"id": f"u{n}.{i}.{j}", "unit": n, "formula": part, "defines": defines(part)})
    return out


# --- structure helpers (tenant_fees translation.py conventions) ---------------------------------------------------

def key(formula):
    return json.dumps(formula, sort_keys=True, separators=(",", ":"))


def q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def is_iff(f):
    return (type(f) is list and f and f[0] == "and" and type(f[1]) is list and type(f[2]) is list
            and f[1][:1] == ["implies"] and f[2][:1] == ["implies"] and f[1][1] == f[2][2] and f[1][2] == f[2][1])


def conjuncts(f):
    if is_iff(f) or type(f) is not list or f[0] != "and":
        return [f]
    return conjuncts(f[1]) + conjuncts(f[2])


def atoms_in(f, atoms, constants):
    if type(f) is not list or not f:
        return
    if f[0] in ("unary", "binary"):
        atoms.add(key(f))
        return
    if f[0] == "const" and len(f) == 3:
        constants.add(f[2])
        return
    for part in f[1:]:
        atoms_in(part, atoms, constants)


def defines(f):
    """The atoms / integer constants a ground rule fixes."""
    if is_iff(f):
        lhs = f[1][1]
        if lhs[0] in ("unary", "binary"):
            return [key(lhs)]
        raise ValueError(f"iff with a non-atom left side: {f}")
    if f[0] == "implies":
        return defines(f[2])
    if f[0] in ("unary", "binary"):
        return [key(f)]
    if f[0] == "not" and f[1][0] in ("unary", "binary"):
        return [key(f[1])]
    if f[0] == "eq" and f[1][0] == "const" and len(f[1]) == 3:
        return [f[1][2]]
    if f[0] == "eq" and f[1][0] == "scale" and f[1][3][0] == "const" and len(f[1][3]) == 3:
        return [f[1][3][2]]
    raise ValueError(f"no defined target: {f}")


# --- the environment for one case ---------------------------------------------------------------------------------

def environment(ctx):
    consts = {}
    for x in ctx.items:
        consts[x] = {"sort": "item", "description": f"The case's item {x}.", "verbalisation": f"item {x}"}
        for base, (u, w) in INT_UNITS.items():
            consts[f"{base}_{x}"] = {"sort": "$int", "unit": u, "description": f"{w[0].upper() + w[1:]} ({x}).",
                                     "verbalisation": f"{w} ({x})"}
    preds = {n: {"arguments": ["item"], "description": d[0].upper() + d[1:] + "."}
             for n, d in {**FACTS, **DERIVED_UNARY}.items()}
    preds.update({n: {"arguments": ["item", "item"], "description": d[0].upper() + d[1:] + "."}
                  for n, d in {**BINARY, **DERIVED_BINARY}.items()})
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "A dwelling, value, day, person or financial year the case names."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {"day": {"scale": "1", "display": {"kind": "iso_date"}},
                      NDAYS: {"scale": "1", "display": {"kind": "decimal", "label": "days"}},
                      GBP: {"scale": "100", "display": {"kind": "money", "currency": "GBP", "input_symbol": "£"}}}}


# --- planted errors (run.py --mutants): each must change the answer of at least one question ----------------------

def _swap(n, fn):
    def apply(t):
        t = dict(t)
        e = t[n]
        t[n] = (e[0], fn(e[1]), *e[2:])
        return t
    return apply


def _walk_replace(old, new):
    def walk(f):
        if f == old:
            return new
        if type(f) is list:
            return [walk(x) for x in f]
        return f
    return walk


def _wrap(walker):
    return lambda builder: (lambda ctx: [walker(f) for f in builder(ctx)])


def _json_sub(a, b):
    return lambda f: json.loads(json.dumps(f).replace(a, b))


MUTANTS = {
    "M1": ("TABLE: s. 5(2) band D row's upper limit 88,000 read as 80,000", _swap(5, _wrap(_json_sub('"88000.00"', '"80000.00"')))),
    "M2": ("DEEMING: Sch. 1 para. 1(3) 'treated as detained' dropped", _swap(17, _wrap(_json_sub('"temp_released"', '"in_custody"')))),
    "M3": ("DEEMING: Sch. 1 para. 1(5) 'order includes a sentence ...' dropped", _swap(19, _wrap(_json_sub('"basis_sentence"', '"basis_order"')))),
    "M4": ("ARITHMETIC: s. 11(2) 'twice the appropriate percentage' read as the appropriate percentage",
           _swap(13, _wrap(_json_sub('"50", ["const"', '"75", ["const"')))),
    "M5": ("ARITHMETIC: s. 5(1) band B's 7 read as 6", _swap(1, lambda b: (lambda ctx: [
        f if json.dumps(f).find('"listed_b"') < 0 else json.loads(json.dumps(f).replace('"7", ["const"', '"6", ["const"'))
        for f in b(ctx)]))),
    "M6": ("ARITHMETIC: s. 10(1) D = 365 read as 364 days", _swap(11, _wrap(_json_sub('"gbp_penny", "365"', '"gbp_penny", "364"')))),
    "M7": ("EXCEPTION: Sch. 1 para. 1(4) dropped (fine default etc. still disregarded)",
           _swap(18, _wrap(lambda f: Iff(f[1][1], FALSE)))),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
