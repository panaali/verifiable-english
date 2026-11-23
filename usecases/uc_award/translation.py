"""Universal Credit award (statute corpus batch 2, law 4): the VE translation, one pass with today's language. SAME-FAMILY.

Row statute-corpus-uc-award (dri-statute-corpus-uc-award-1123, Opus 5.5). Written from the pinned source only
(manage-agents reviews/spare/statute-corpus/batch2/uc-award/source.txt, sha256 b28e1d46...f8eed2: WRA 2012 s.8, UC Regs
2013 regs 3, 4, 22, 24, 36 as in force for 2026-27) BEFORE the encoder's question file was opened. Evidence branch:
nothing here is a Lean kernel line, a profile, a refuses pair or a lint change.

UNITS maps each in-scope unit n of batch2/uc-award/units.jsonl (tools/sample5.py --units uc-award) to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one award;
  ("PART", builder, cause, note) written except the part named in the note (a stated fact from outside the pin, or a
                                 stated judgment);
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2).
One run case = ONE AWARD. Its persons are the case's items (sort person). The anchor is the person whose award is asked
(the first person the question names). Grounding is mechanical: "for each child or qualifying young person", "any other
person", "either of them" are written once per person the case names (closed world over the case's persons, an encoding
convention stated in encode.py); a SUM over the set (the maximum amount over the children, the combined income) is an
`add` chain over the case's persons whose summands are 0 for a person outside the set (linear arithmetic).
Money is gbp_penny; ages are whole years (unit "years"). The text's 55% is written over integers as
20 x deduction = 11 x amount (exact because earned income is a whole number of pounds, a fixed fact of the questions).
"""
from __future__ import annotations

import hashlib
import json

GBP, YEARS = "gbp_penny", "years"

# ---- vocabulary -------------------------------------------------------------------------------------------------
PERSON_INTS = {  # per-person integer constants: base -> (unit, words)
    "age": (YEARS, "the person's age in whole years on the first day of the assessment period (stated convention)"),
    "earn": (GBP, "the person's earned income in respect of the assessment period"),
    "unearn": (GBP, "the person's unearned income in respect of the assessment period"),
    "cel": (GBP, "the child element included for the person (reg. 24(1))"),
    "dis": (GBP, "the additional amount for the person as a disabled child or qualifying young person (reg. 24(2))"),
    "lcx": (GBP, "the LCWRA element included in respect of the person"),
    "crx": (GBP, "the carer element included in respect of the person"),
    "ea": (GBP, "the person's earned income counted in the award (s. 8(4), reg. 22(1), (3))"),
    "ue": (GBP, "the person's unearned income counted in the award (s. 8(4), reg. 22(1), (3))"),
}
AWARD_INTS = {  # per-award integer constants (named after the anchor)
    "housing": (GBP, "the amount of the housing costs element in the award (0 if none; stated)"),
    "sa": (GBP, "the standard allowance (reg. 36 table)"),
    "maxamt": (GBP, "the maximum amount (s. 8(2))"),
    "earned": (GBP, "the earned income of the claimant, or the combined earned income (s. 8(4), reg. 22)"),
    "unearned": (GBP, "the unearned income of the claimant, or the combined unearned income (s. 8(4), reg. 22)"),
    "wa": (GBP, "the work allowance (reg. 22(2) and table)"),
    "dede": (GBP, "the amount deducted in respect of earned income (reg. 22(1)(b))"),
    "ded": (GBP, "the amounts to be deducted (s. 8(3), reg. 22(1))"),
    "award": (GBP, "the amount of the award (s. 8(1))"),
}
# Every derived constant the runner establishes as a step (with candidate values; never typed by the encoder)
STEP_BASES = ("cel", "dis", "lcx", "crx", "ea", "ue", "sa", "maxamt", "earned", "unearned", "wa", "dede", "ded", "award")

FACTS = {  # unary facts on a person (the encoder states each true or false)
    "anchor": "is the person whose award the question asks about (the first person it names)",
    "child": "is a child (s. 40 of the Act; stated)",
    "qyp": "is a qualifying young person (s. 40 of the Act, reg. 5; stated)",
    "fails_a": "does not meet the basic condition in s. 4(1)(a) (at least 18 years old)",
    "min_age8": "is a person in respect of whom the minimum age specified in regulation 8 applies",
    "fails_b": "does not meet the basic condition in s. 4(1)(b) (under the qualifying age for state pension credit)",
    "fails_c": "does not meet the basic condition in s. 4(1)(c) (in Great Britain)",
    "fails_d": "does not meet the basic condition in s. 4(1)(d) (not receiving education)",
    "excepted_d": "is excepted from the basic condition in s. 4(1)(d)",
    "prisoner": "is a prisoner",
    "reg19": "is a person in respect of whom entitlement does not arise by virtue of regulation 19",
    "s115": "is a person to whom s. 115 of the Immigration and Asylum Act 1999 applies",
    "same_household": "is living in the same household as the anchor (stated judgment, reg. 3(4)(b))",
    "temp_absent": "is temporarily absent from the household (stated)",
    "abs_over6": "the absence is expected to exceed, or does exceed, 6 months (stated)",
    "abs_from_gb": "the absence is from Great Britain",
    "abs_over1m": "the absence is expected to exceed, or does exceed, one month (stated)",
    "reg11_circ": "the absence is in circumstances where an absence of a person for longer than one month would be "
                  "disregarded for the purposes of regulation 11(2) or (3) (stated)",
    "la_care": "is looked after by a local authority",
    "dis_lower": "is entitled to disability living allowance, Scottish adult disability living allowance, child "
                 "disability payment, adult disability payment or personal independence payment",
    "dis_higher": "is entitled to a component at the rate named in reg. 24(2)(b)(i), or is blind (reg. 24(2)(b)(ii))",
    "lcw": "has limited capability for work (stated)",
    "lcwra_el": "the award includes an LCWRA element in respect of the person (regs 27-28, not pinned; stated)",
    "pre2026": "is a pre-2026 claimant, a severe conditions criteria claimant or a claimant who is terminally ill",
    "carer_el": "the award includes a carer element in respect of the person (regs 29-30, not pinned; stated)",
    "sos_any": "the Secretary of State has determined which person has the main responsibility for the person",
    "nom_any": "a joint nomination of the person with the main responsibility for this person has been made",
}
STATED = ("same_household", "temp_absent", "abs_over6", "abs_over1m", "living_couple", "main_judged")
BINARY = {
    "couple": "the two persons are a couple (s. 39 of the Act, not pinned; stated)",
    "lives": "the first person (a child or qualifying young person) normally lives with the second (stated)",
    "living_couple": "the two persons are living as a couple (stated judgment, reg. 4(3))",
    "nominated": "the persons with whom the second person normally lives jointly nominated the first as having the main "
                 "responsibility for the second (reg. 4(5))",
    "sos_det": "the Secretary of State determined that the first person has the main responsibility for the second "
               "(reg. 4(5))",
    "main_judged": "the first person has the main responsibility for the second (stated judgment, reg. 4(4))",
    "married": "the two persons are parties to a marriage to each other",
    "poly_law": "the marriage of the two persons took place under the laws of a country which permits polygamy",
    "earlier": "the first person is a party to a marriage to the second that is earlier than the first person's other "
               "marriage and still subsists",
}
DERIVED = {  # unary on a person
    "young": "is a child or qualifying young person",
    "single_claim": "the award to the anchor is on a single claim",
    "joint": "the award is on a joint claim (the anchor and a partner are joint claimants)",
    "couple_single": "the anchor is a member of a couple but claims as a single person",
    "claimant": "is a claimant of the award",
    "inc_counted": "the person's income counts in the award (s. 8(4); reg. 22(1), (3))",
    "has_resp": "is responsible for one or more children or qualifying young persons",
    "counted": "is a child or qualifying young person for whom a claimant of the award is responsible",
    "no_resp": "is treated as not being the responsibility of any person (reg. 4(6))",
    "abs_ceases": "a temporary absence ends responsibility for the person (reg. 4(7))",
    "wa_exists": "a work allowance is specified in the reg. 22 table for the award",
    "lower_wa": "the award contains an amount for the housing costs element (reg. 22(2)(b))",
    "row_joint": "the work allowance row is the joint claimants' row (reg. 22(3) reads a couple claiming as single as "
                 "joint claimants)",
    "higher_rate": "the additional amount for the person is the higher rate",
    "lower_rate": "the additional amount for the person is the lower rate",
    "any_over25": "the claimant, or one of the joint claimants, is aged 25 or over",
}
DERIVED_BIN = {  # binary derived
    "tcp": "the two persons are treated as a couple (not ceased under reg. 3(6), not disregarded under reg. 3(4))",
    "msp": "the second person's partner situation lets the first make a claim as a single person (reg. 3(3))",
    "jointp": "the first person and the second are joint claimants",
    "polygamous": "the marriage of the two persons is a polygamous marriage (reg. 3(5))",
    "poly_dis": "the fact that the two persons are husband and wife is disregarded (reg. 3(4))",
    "resp": "the first person is responsible for the second (a child or qualifying young person), reg. 4",
    "multi": "the second person normally lives with the first and with another person who is not the first's partner",
    "main": "the first person has the main responsibility for the second (reg. 4(4), (5))",
}

# The reg. 22 and reg. 36 table values, as the text gives each row
WA_HIGHER_SINGLE, WA_HIGHER_JOINT, WA_LOWER_SINGLE, WA_LOWER_JOINT = "710.00", "710.00", "427.00", "427.00"
SA_S_U25, SA_S_25, SA_J_U25, SA_J_25 = "338.58", "424.90", "528.34", "666.97"
CHILD_EL, DIS_LOW, DIS_HIGH = "303.94", "164.79", "514.71"
LCWRA_STD, LCWRA_PRE, CARER = "217.26", "429.80", "209.34"
AGE_25 = "25"


# ---- formula helpers (the ve-quantity@1 wire shapes; usecases/tenant_fees/translation.py conventions) ----------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def B(p, x, y): return ["binary", p, c(x), c(y)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def gbp(v): return ["decimal", GBP, v]
def years(v): return ["decimal", YEARS, v]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def add(tag, a, b): return ["add", tag, a, b]
def scale(tag, k, t): return ["scale", tag, str(k), t]
def minus(a, b): return add(GBP, a, scale(GBP, -1, b))
FALSE = ["not", ["true"]]


def And(*fs):
    fs = [f for f in fs if f is not None]
    if not fs:
        return ["true"]
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


def total(terms):
    """A grounded sum (an add chain) of money terms; 0.00 for an empty set."""
    if not terms:
        return gbp("0.00")
    r = terms[-1]
    for t in reversed(terms[:-1]):
        r = add(GBP, t, r)
    return r


def k(base, x):
    """Per-person integer constant."""
    return ["const", PERSON_INTS[base][0], f"{base}_{x}"]


def ka(base, ctx):
    """Per-award integer constant (named after the award)."""
    return ["const", AWARD_INTS[base][0], f"{base}_{ctx.award}"]


def iff_atom(p, x, body):
    return Iff(U(p, x), body)


def iff_bin(p, x, y, body):
    return Iff(B(p, x, y), body)


# ---- the award context -------------------------------------------------------------------------------------------

class Ctx:
    def __init__(self, award, persons, anchor, links=()):
        self.award, self.persons, self.anchor = award, list(persons), anchor
        self.links = {(p, a, b) for (p, a, b) in links}

    def linked(self, pred, x):
        """Persons y with the stated binary fact pred(x, y) (either order for the symmetric couple/married facts)."""
        sym = pred in ("couple", "married", "poly_law")
        return sorted({b for (p, a, b) in self.links if p == pred and a == x}
                      | ({a for (p, a, b) in self.links if p == pred and b == x} if sym else set()))

    def partners(self):
        return self.linked("couple", self.anchor)

    def others(self, x):
        return [y for y in self.persons if y != x]


def each(fn):
    return lambda ctx: [f for x in ctx.persons for f in fn(x, ctx)]


def sym(p, x, y):
    """A symmetric stated binary fact, read in either order (the encoder states it once)."""
    return Or(B(p, x, y), B(p, y, x))


# ---- the units (n = batch2/uc-award/units.jsonl) ------------------------------------------------------------------

def _u1(ctx):
    return [Eq(ka("award", ctx), minus(ka("maxamt", ctx), ka("ded", ctx)))]


def _u2(ctx):
    terms = [ka("sa", ctx)]
    terms += [add(GBP, k("cel", y), k("dis", y)) for y in ctx.persons]
    terms += [ka("housing", ctx)]
    terms += [add(GBP, k("lcx", x), k("crx", x)) for x in ctx.persons]
    return [Eq(ka("maxamt", ctx), total(terms))]


def _u3(ctx):
    return [Eq(ka("ded", ctx), add(GBP, ka("dede", ctx), ka("unearned", ctx)))]


def _u4(ctx):
    out = []
    for x in ctx.persons:
        out += [Implies(U("inc_counted", x), Eq(k("ea", x), k("earn", x))),
                Implies(Not(U("inc_counted", x)), Eq(k("ea", x), gbp("0.00"))),
                Implies(U("inc_counted", x), Eq(k("ue", x), k("unearn", x))),
                Implies(Not(U("inc_counted", x)), Eq(k("ue", x), gbp("0.00")))]
    out += [Eq(ka("earned", ctx), total([k("ea", x) for x in ctx.persons])),
            Eq(ka("unearned", ctx), total([k("ue", x) for x in ctx.persons]))]
    a = ctx.anchor
    out += [iff_atom("inc_counted", x, Or(U("anchor", x), *[And(B("tcp", a, x)) for p in ctx.partners() if p == x]))
            for x in ctx.persons]
    return out


def _basic_ok(a, p):
    """reg. 3(2): a couple may be joint claimants although one member fails 4(1)(b) or 4(1)(d) (not excepted), if the
    other meets that condition (or is excepted from it). Members who both fail it are not covered (no conclusion)."""
    def d_ok(x): return Or(Not(U("fails_d", x)), U("excepted_d", x))
    return And(Or(Not(U("fails_b", a)), Not(U("fails_b", p))), Or(d_ok(a), d_ok(p)))


def _u5(ctx):
    a = ctx.anchor
    return [iff_bin("jointp", a, p, And(B("tcp", a, p), Not(B("msp", a, p)), _basic_ok(a, p))) for p in ctx.partners()]


def _u6(ctx):
    a = ctx.anchor
    out = []
    for p in ctx.partners():
        out.append(iff_bin("msp", a, p, Or(And(U("fails_a", p), Not(U("min_age8", p))), U("fails_c", p),
                                             U("prisoner", p), And(Not(U("prisoner", p)), U("reg19", p)),
                                             U("s115", p))))
    out.append(iff_atom("joint", a, Or(*[B("jointp", a, p) for p in ctx.partners()])))
    out.append(iff_atom("couple_single", a, Or(*[And(B("tcp", a, p), B("msp", a, p)) for p in ctx.partners()])))
    out.append(iff_atom("single_claim", a, Not(U("joint", a))))
    out += [iff_atom("claimant", x, Or(U("anchor", x), *[B("jointp", a, x) for p in ctx.partners() if p == x]))
            for x in ctx.persons]
    return out


def _u7(ctx):
    """reg. 3(4): husband and wife disregarded where one of them is a party to an earlier subsisting marriage whose
    other party is living in the same household; the pair is then not treated as a couple (unit 9's tcp)."""
    a = ctx.anchor
    out = []
    for p in ctx.partners():
        earlier = [And(B("earlier", x, z), U("same_household", z))
                   for x in (a, p) for z in ctx.linked("earlier", x) if z not in (a, p)]
        out.append(iff_bin("poly_dis", a, p, And(B("polygamous", a, p), Or(*earlier))))
    return out


def _u8(ctx):
    a = ctx.anchor
    out = []
    for p in ctx.partners():
        more = [sym("married", x, z) for x in (a, p) for z in ctx.persons if z not in (a, p)]
        out.append(iff_bin("polygamous", a, p, And(sym("married", a, p), sym("poly_law", a, p), Or(*more))))
    return out


def _u9(ctx):
    a = ctx.anchor
    return [iff_bin("tcp", a, p, And(sym("couple", a, p), Not(And(U("temp_absent", p), U("abs_over6", p))),
                                     Not(B("poly_dis", a, p))))
            for p in ctx.partners()]


def _young(ctx):
    return [iff_atom("young", x, Or(U("child", x), U("qyp", x))) for x in ctx.persons]


def _u11(ctx):
    """reg. 4(2)-(7) as one classification resp(x, y) for every pair of the case's persons."""
    out = []
    for x in ctx.persons:
        for y in ctx.others(x):
            out.append(iff_bin("resp", x, y, And(
                U("young", y), B("lives", y, x),
                Not(And(U("qyp", y), sym("living_couple", x, y))),           # 4(3)
                Or(Not(B("multi", x, y)), B("main", x, y)),                   # 4(4)
                Not(U("no_resp", y)),                                         # 4(6)
                Not(U("abs_ceases", y)))))                                    # 4(7)
    for x in ctx.persons:
        out.append(iff_atom("has_resp", x, Or(*[B("resp", x, y) for y in ctx.others(x)])))
    return out


def _u13(ctx):
    out = []
    for x in ctx.persons:
        for y in ctx.others(x):
            others = [And(B("lives", y, z), Not(sym("couple", x, z))) for z in ctx.persons if z not in (x, y)]
            out.append(iff_bin("multi", x, y, And(B("lives", y, x), Or(*others))))
    return out


def _u14(ctx):
    out = []
    for x in ctx.persons:
        for y in ctx.others(x):
            out.append(iff_bin("main", x, y, Or(
                B("sos_det", x, y),
                And(Not(U("sos_any", y)), B("nominated", x, y)),
                And(Not(U("sos_any", y)), Not(U("nom_any", y)), B("main_judged", x, y)))))
    return out


def _u15(ctx):
    return [iff_atom("no_resp", y, Or(U("la_care", y), U("prisoner", y))) for y in ctx.persons]


def _u16(ctx):
    return [iff_atom("abs_ceases", y, And(U("temp_absent", y), Or(
        U("abs_over6", y), And(U("abs_from_gb", y), U("abs_over1m", y), Not(U("reg11_circ", y))))))
            for y in ctx.persons]


def _u17(ctx):
    a = ctx.anchor
    earned, wa, dede = ka("earned", ctx), ka("wa", ctx), ka("dede", ctx)
    return [
        iff_atom("wa_exists", a, Or(*[And(U("inc_counted", x), Or(U("has_resp", x), U("lcw", x)))
                                      for x in ctx.persons])),
        # (b)(i): no work allowance: 55% of the earned income (20 x deduction = 11 x income)
        Implies(Not(U("wa_exists", a)), Eq(scale(GBP, 20, dede), scale(GBP, 11, earned))),
        # (b)(ii): 55% of the amount by which earned income exceeds the work allowance (none if it does not exceed)
        Implies(And(U("wa_exists", a), Lt(wa, earned)), Eq(scale(GBP, 20, dede), scale(GBP, 11, minus(earned, wa)))),
        Implies(And(U("wa_exists", a), Le(earned, wa)), Eq(dede, gbp("0.00"))),
    ]


def _u18(ctx):
    a = ctx.anchor
    return [iff_atom("lower_wa", a, Lt(gbp("0.00"), ka("housing", ctx)))]


def _u19(ctx):
    a = ctx.anchor
    return [iff_atom("row_joint", a, Or(U("joint", a), U("couple_single", a)))]


def _wa_row(higher, joint, value):
    def b(ctx):
        a = ctx.anchor
        g = And(U("wa_exists", a), U("lower_wa", a) if not higher else Not(U("lower_wa", a)),
                U("row_joint", a) if joint else Not(U("row_joint", a)))
        return [Implies(g, Eq(ka("wa", ctx), gbp(value)))]
    return b


def _no_wa(ctx):
    return [Implies(Not(U("wa_exists", ctx.anchor)), Eq(ka("wa", ctx), gbp("0.00")))]


def _u24(ctx):
    out = []
    for y in ctx.persons:
        out.append(iff_atom("counted", y, Or(*[And(U("claimant", x), B("resp", x, y)) for x in ctx.others(y)])))
        out.append(Implies(U("counted", y), Eq(k("cel", y), gbp(CHILD_EL))))
        out.append(Implies(Not(U("counted", y)), Eq(k("cel", y), gbp("0.00"))))
    return out


def _u25(ctx):
    out = []
    for y in ctx.persons:
        out += [iff_atom("higher_rate", y, And(U("counted", y), U("dis_higher", y))),
                iff_atom("lower_rate", y, And(U("counted", y), U("dis_lower", y), Not(U("dis_higher", y)))),
                Implies(U("higher_rate", y), Eq(k("dis", y), gbp(DIS_HIGH))),
                Implies(U("lower_rate", y), Eq(k("dis", y), gbp(DIS_LOW))),
                Implies(And(Not(U("higher_rate", y)), Not(U("lower_rate", y))), Eq(k("dis", y), gbp("0.00")))]
    return out


def _u27(ctx):
    """reg. 36(3): a member of a couple claiming as a single person takes the single claimant amounts. Written as the
    single rows' guard: the standard allowance rows read single_claim (true for that member, unit 6)."""
    return []


def _sa_row(joint, over25, value):
    def b(ctx):
        a = ctx.anchor
        guard = And(U("joint", a) if joint else Not(U("joint", a)),
                    U("any_over25", a) if over25 else Not(U("any_over25", a)))
        return [Implies(guard, Eq(ka("sa", ctx), gbp(value)))]
    return b


def _over25(ctx):
    a = ctx.anchor
    return [iff_atom("any_over25", a, Or(*[And(U("claimant", x), Le(years(AGE_25), k("age", x)))
                                           for x in ctx.persons]))]


def _lcwra(pre, value):
    def b(ctx):
        out = []
        for x in ctx.persons:
            out.append(Implies(And(U("lcwra_el", x), U("pre2026", x) if pre else Not(U("pre2026", x))),
                               Eq(k("lcx", x), gbp(value))))
            if not pre:
                out.append(Implies(Not(U("lcwra_el", x)), Eq(k("lcx", x), gbp("0.00"))))
        return out
    return b


def _carer(ctx):
    out = []
    for x in ctx.persons:
        out += [Implies(U("carer_el", x), Eq(k("crx", x), gbp(CARER))),
                Implies(Not(U("carer_el", x)), Eq(k("crx", x), gbp("0.00")))]
    return out


def _cat(*builders):
    return lambda ctx: [f for b in builders for f in b(ctx)]


UNITS = {
    # ---- WRA 2012 s. 8 ----
    1: ("RULE", _u1, "s. 8(1): award = maximum amount - amounts deducted (D4: every in-scope award is above 0)"),
    2: ("RULE", _u2, "s. 8(2): the total, a grounded SUM over the case's persons (per-child amounts, LCWRA and carer "
                     "elements) plus the standard allowance and the stated housing costs element"),
    3: ("RULE", _u3, "s. 8(3): earned-income deduction plus unearned income (the 'prescribed manner' = reg. 22)"),
    4: ("RULE", _u4, "s. 8(4): income of the claimant, or the combined income of joint claimants; reg. 22(3) adds the "
                     "partner of a member of a couple claiming as single (inc_counted for a treated-couple partner)"),
    # ---- reg. 3 ----
    5: ("PART", _u5, "cross-reference",
        "reg. 3(2): written over stated facts 'does not meet the basic condition in s. 4(1)(b)/(d)', 'excepted' (s. 4 "
        "of the Act not pinned); a couple who both fail is not covered (no conclusion)"),
    6: ("PART", _u6, "cross-reference",
        "reg. 3(3)(a)-(e): written over stated facts (s. 4(1)(a), (c), reg. 8, reg. 19, IAA 1999 s. 115, 'prisoner'); "
        "'may make a claim as a single person' carried by the fixed convention that such a member does (D7); the "
        "tail signposts regs 18, 36, 22"),
    7: ("PART", _u7, "other:judgment standard",
        "reg. 3(4): 'the fact that they are husband and wife is to be disregarded' written as: the pair is not treated "
        "as a couple (unit 9); 'living in the same household' a stated judgment (stated); 'still subsists' a fact"),
    8: ("PART", _u8, "cross-reference",
        "reg. 3(5): 'a party to it is married to more than one person' written over the case's marriage links; 'under "
        "the laws of a country which permits polygamy' a stated fact about another country's law"),
    9: ("PART", _u9, "other:judgment standard",
        "reg. 3(6): 'cease to be treated as a couple' written (tcp false); 'temporarily absent' and 'expected to "
        "exceed, or does exceed, 6 months' stated facts (stated)"),
    # ---- reg. 4 ----
    10: ("RULE", _young, "reg. 4(1): 'a child or qualifying young person' (young = child or qyp, stated statuses); "
                         "'is determined as follows' = units 11-16"),
    11: ("PART", _u11, "other:judgment standard",
         "reg. 4(2): 'normally lives with' a stated household fact (D6, stated); the responsibility rule written for "
         "every pair of the case's persons, with (3)-(7) as exceptions"),
    12: ("PART", lambda ctx: [], "other:judgment standard",
         "reg. 4(3): written inside unit 11's rule; 'living as a couple' a stated judgment (stated)"),
    13: ("PART", _u13, "other:judgment standard",
         "reg. 4(4): 'two or more persons who are not a couple' written over the case's persons; 'the main "
         "responsibility' a stated judgment where no nomination or determination exists (stated)"),
    14: ("PART", _u14, "other:judgment standard",
         "reg. 4(5): a determination by the Secretary of State prevails over a joint nomination; the conditions of "
         "(a), (b) ('in the opinion of the Secretary of State') are not tested: the determination is a stated fact"),
    15: ("PART", _u15, "cross-reference",
         "reg. 4(6): the deeming ('treated as not being the responsibility of any person') written; 'Subject to "
         "regulation 4A' (reg. 4A not pinned; fixed fact: never applies); 'looked after by a local authority' and "
         "'prisoner' stated facts (defined outside the pin)"),
    16: ("PART", _u16, "cross-reference",
         "reg. 4(7): written; 'unless ... regulation 11(2) or (3)' a stated cross-reference fact (D2(d)); the "
         "absence's expected length a stated fact (stated)"),
    # ---- reg. 22 ----
    17: ("PART", _u17, "definition by reference",
         "reg. 22(1): (a) all unearned income and (b)(i)/(ii) 55% written (20 x deduction = 11 x amount; floor 0 as "
         "two guarded equations); 'limited capability for work' a stated status (reg. 2 -> s. 37(1) of the Act, "
         "regs 39-44 not pinned); income amounts are stated (Part 6 not pinned)"),
    18: ("RULE", _u18, "reg. 22(2): the award contains a housing costs element iff its stated amount is above 0"),
    19: ("RULE", _u19, "reg. 22(3): the deduction as if joint claimants: combined income (unit 4) and the joint row"),
    20: ("RULE", _cat(_wa_row(True, False, WA_HIGHER_SINGLE), _no_wa), "table row: higher, single claimant"),
    21: ("RULE", _wa_row(True, True, WA_HIGHER_JOINT), "table row: higher, joint claimants"),
    22: ("RULE", _wa_row(False, False, WA_LOWER_SINGLE), "table row: lower, single claimant"),
    23: ("RULE", _wa_row(False, True, WA_LOWER_JOINT), "table row: lower, joint claimants"),
    # ---- reg. 24 ----
    24: ("RULE", _u24, "reg. 24(1): the child element for each child or qualifying young person for whom a claimant is "
                       "responsible (per person, summed in unit 2)"),
    25: ("PART", _u25, "cross-reference",
         "reg. 24(2): lower / higher rate written, '(unless sub-paragraph (b) applies)' written; entitlement to the "
         "named benefits, components and rates (other Acts and Scottish regulations) and 'blind' stated facts"),
    # ---- reg. 36 ----
    26: ("RULE", lambda ctx: [], "reg. 36(1): 'are given in the following table' = the table rows (units 28-39)"),
    27: ("RULE", _u27, "reg. 36(3): carried by the single rows' guard (not joint), which holds for a member of a couple "
                       "claiming as a single person"),
    28: ("RULE", _cat(_sa_row(False, False, SA_S_U25), _over25), "table row: single claimant aged under 25"),
    29: ("RULE", _sa_row(False, True, SA_S_25), "table row: single claimant aged 25 or over"),
    30: ("RULE", _sa_row(True, False, SA_J_U25), "table row: joint claimants both aged under 25"),
    31: ("RULE", _sa_row(True, True, SA_J_25), "table row: joint claimants where either is aged 25 or over"),
    32: ("RULE", lambda ctx: [], "table row: child element 303.94 (the value written in unit 24's rule)"),
    33: ("RULE", lambda ctx: [], "table row: lower rate 164.79 (the value written in unit 25's rule)"),
    34: ("RULE", lambda ctx: [], "table row: higher rate 514.71 (the value written in unit 25's rule)"),
    35: ("PART", _lcwra(False, LCWRA_STD), "cross-reference",
         "table row: LCWRA element 217.26 written; that the award includes the element (regs 27-28) and the statuses "
         "'pre-2026 claimant', 'severe conditions criteria', 'terminally ill' are stated facts"),
    36: ("PART", _lcwra(True, LCWRA_PRE), "cross-reference", "table row: LCWRA element 429.80 written; as unit 35"),
    37: ("PART", _carer, "cross-reference",
         "table row: carer element 209.34 written; that the award includes it (regs 29-30) a stated fact"),
    38: ("NOT", None, "cross-reference",
         "table row: childcare costs element maximum, one child: no pinned sentence includes or caps the element "
         "(reg. 34 not pinned; D3: probes only)"),
    39: ("NOT", None, "cross-reference", "table row: childcare costs element maximum, two or more children: as unit 38"),
}


def units_table(mutant=None):
    t = dict(UNITS)
    if mutant is not None:
        t = MUTANTS[mutant][1](t)
    return t


def rules(ctx, mutant=None):
    """Ground rules for one award: [{"id", "unit", "formula", "defines"}]."""
    out = []
    for n, entry in sorted(units_table(mutant).items()):
        if entry[0] not in ("RULE", "PART") or entry[1] is None:
            continue
        for i, f in enumerate(entry[1](ctx)):
            f = _fix_empty(f)
            if f is None:
                continue
            for j, part in enumerate(conjuncts(f)):
                out.append({"id": f"u{n}.{i}.{j}", "unit": n, "formula": part, "defines": defines(part)})
    return out


TRUE = ["true"]


def simplify(f):
    """Propagate the grounding constants TRUE (an empty conjunction) and FALSE (an empty disjunction) out of a formula;
    the wire format has no 'true', so a ground rule that is TRUE is dropped and none may be FALSE."""
    if type(f) is not list or not f:
        return f
    if f == TRUE or f == FALSE:
        return f
    if is_iff(f):
        lhs, rhs = f[1][1], simplify(f[1][2])
        if rhs == TRUE:
            return lhs
        if rhs == FALSE:
            return ["not", lhs]
        return Iff(lhs, rhs)
    tag = f[0]
    if tag == "not":
        a = simplify(f[1])
        return FALSE if a == TRUE else TRUE if a == FALSE else ["not", a]
    if tag in ("and", "or"):
        a, b = simplify(f[1]), simplify(f[2])
        unit, zero = (TRUE, FALSE) if tag == "and" else (FALSE, TRUE)
        if a == zero or b == zero:
            return zero
        if a == unit:
            return b
        if b == unit:
            return a
        return [tag, a, b]
    if tag == "implies":
        a, b = simplify(f[1]), simplify(f[2])
        if a == FALSE or b == TRUE:
            return TRUE
        if a == TRUE:
            return b
        if b == FALSE:
            return ["not", a]
        return ["implies", a, b]
    return f


def _fix_empty(f):
    """Simplify the grounding constants away; a rule that becomes TRUE is dropped (None)."""
    f = simplify(f)
    if f == TRUE:
        return None
    if f == FALSE:
        raise ValueError("a ground rule simplified to false")
    return f


# ---- structure helpers (tenant_fees translation.py conventions) ------------------------------------------------

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


# ---- the environment for one award ---------------------------------------------------------------------------------

def environment(ctx):
    consts = {}
    for x in ctx.persons:
        consts[x] = {"sort": "person", "description": f"The case's person {x}.", "verbalisation": f"person {x}"}
        for base, (u, w) in PERSON_INTS.items():
            consts[f"{base}_{x}"] = {"sort": "$int", "unit": u, "description": f"{w[0].upper() + w[1:]} ({x}).",
                                     "verbalisation": f"{w} ({x})"}
    for base, (u, w) in AWARD_INTS.items():
        consts[f"{base}_{ctx.award}"] = {"sort": "$int", "unit": u, "description": w[0].upper() + w[1:] + ".",
                                         "verbalisation": w}
    preds = {n: {"arguments": ["person"], "description": d[0].upper() + d[1:] + "."}
             for n, d in {**FACTS, **DERIVED}.items()}
    preds.update({n: {"arguments": ["person", "person"], "description": d[0].upper() + d[1:] + "."}
                  for n, d in {**BINARY, **DERIVED_BIN}.items()})
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"person": {"description": "A person the case names (adult, child or qualifying "
                                                               "young person)."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {YEARS: {"scale": "1", "display": {"kind": "decimal", "label": "years"}},
                      GBP: {"scale": "100", "display": {"kind": "money", "currency": "GBP", "input_symbol": "£"}}}}


# ---- planted errors (run.py --mutants): each must change at least one answer ----------------------------------------

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


def _drop(n):
    def apply(t):
        t = dict(t)
        e = t[n]
        t[n] = (e[0], lambda ctx: [], *e[2:])
        return t
    return apply


def _drop_no_resp(t):
    """reg. 4(6) deeming dropped: no child is treated as not being anyone's responsibility."""
    t = dict(t)
    e = t[15]
    t[15] = (e[0], lambda ctx: [["not", U("no_resp", y)] for y in ctx.persons], *e[2:])
    return t


def _drop_absent6(t):
    """reg. 3(6) deeming dropped: an absent partner never ceases to be treated as a couple."""
    t = dict(t)
    e = t[9]

    def b(ctx):
        a = ctx.anchor
        return [iff_bin("tcp", a, p, And(sym("couple", a, p), Not(B("poly_dis", a, p)))) for p in ctx.partners()]
    t[9] = (e[0], b, *e[2:])
    return t


def _m6(t):
    """s. 8(3)(b) dropped: the unearned income is not deducted."""
    t = dict(t)
    e = t[3]
    t[3] = (e[0], lambda ctx: [Eq(ka("ded", ctx), ka("dede", ctx))], *e[2:])
    return t


MUTANTS = {
    "M1": ("table row value: the child element read as 330.94 (reg. 36 table, unit 32 via unit 24's rule)",
           _swap(24, _wrap(_walk_replace(gbp(CHILD_EL), gbp("330.94"))))),
    "M2": ("table row value: the lower work allowance (single) read as 710.00 (reg. 22 table, unit 22)",
           _swap(22, _wrap(_walk_replace(gbp(WA_LOWER_SINGLE), gbp("710.00"))))),
    "M3": ("deeming line dropped: reg. 4(6) (looked after by a local authority / prisoner) never applies",
           _drop_no_resp),
    "M4": ("deeming line dropped: reg. 3(6) (partner absent over 6 months) never ends the couple", _drop_absent6),
    "M5": ("arithmetic step changed: 55% read as 50% in reg. 22(1)(b)(ii) (20 x d = 10 x excess)",
           _swap(17, _wrap(lambda f: json.loads(json.dumps(f).replace(
               '["scale","gbp_penny","11",["add"', '["scale","gbp_penny","10",["add"'
           ).replace('["scale", "gbp_penny", "11", ["add"', '["scale", "gbp_penny", "10", ["add"'))))),
    "M6": ("arithmetic step changed: unearned income dropped from the deduction (s. 8(3)(b))", _m6),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
