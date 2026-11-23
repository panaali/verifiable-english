"""Child support maintenance calculation, CSA 1991 Sch. 1 Part I (statute corpus stock, batch 3 law 5): the VE translation.

Row statute-corpus-child-support (dri-statute-corpus-child-support-1123, Opus 5.5). SAME-FAMILY. Written from the pinned
source only (manage-agents reviews/spare/statute-corpus/stock/child-support/source.txt, sha256 860a9df0...03c3) BEFORE
the encoder's question file was opened. Evidence branch: nothing here is a Lean kernel line, a profile, a refuses pair
or a lint change; nothing merges.

UNITS maps each in-scope unit n of stock/child-support/units.jsonl to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one case;
  ("PART", builder, cause, note) written except the part named in the note (stated / not written);
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2 + "other:table lookup").
Grounding is mechanical over the items the case names: the non-resident parent x, its children, the other persons and
the benefits. "One / two / three or more" children and "the number of" children are counts over the case's child items
(exactly-k disjunctions over the named children: closed world over the case's children, an encoder convention).
No number from a case's facts is ever a coefficient: every coefficient is a literal of the pinned text, or a count k that
a rule enumerates (k = 1, 2, ... up to the number of child items), the case split council tax used for D = 365 / 366.
Amounts are integer pence; an amount the text's arithmetic makes not whole in pence has no model (the run refuses it).
Vocabulary: one sort "item"; unary facts and derived predicates on items; binary facts on pairs; per-item integer
constants (money in gbp_penny, nights in night, shared-care fractions in fourteenths).

Readings fixed here (from the text alone, before any question was read):
R1 10(3) before 2(3): the amount over 3,000 pounds is ignored from the gross weekly income "calculated as above" (the
   regulations' figure), and 2(3) then treats that income as reduced (2(3) acts "for the purposes of (1) and (2)").
R2 Paras 3(1)(b), 4(1)(a) and 5(b) compare the gross weekly income after 10(3), never after 2(3) (2(3) is only for 2).
R3 Under 5A the rate is "determined under paragraph 5A" (7(1) names it beside the basic and a reduced rate): asked
   "basic, reduced, flat or nil", the translation gives no answer (refused) when 5A applies.
R4 5A(3)'s "amount which would be payable" is the weekly rate (paras 2-5 with the larger set of qualifying children),
   before apportionment and shared care (7(1) applies 7 to the rate "determined under 5A"). With a reduced rate the
   hypothetical amount is the one the regulations give for that larger set (a stated amount, redrateh); with a rate
   calculated following agreement to a variation it is not written (variations are outside the pinned text).
R5 1(2): where the nil rate applies the amount payable is nil (0.00).
R6 Para 8(2) makes the amount nil; the 7(4) Table does not apply under 8. Asked "what decrease applies" (a Table fraction
   or none), the translation gives no answer where 8(2) makes the amount nil (refused); where neither 7 nor 8(2)
   decreases anything the answer is "none".
R7 7(7): the floor compares the aggregate payable to all persons with care (one person: the amount) with 7 pounds; the
   7 pounds is then apportioned under para. 6 where para. 6 applies.
"""
from __future__ import annotations

import hashlib
import itertools
import json

GBP, NIGHT, F14 = "gbp_penny", "night", "fourteenth"
INT_UNITS = {  # per-item integer constants: base name -> (unit, words)
    "inc": (GBP, "the non-resident parent's gross weekly income as determined under the regulations (para. 10(1))"),
    "cinc": (GBP, "the gross weekly income after para. 10(3) (any amount over 3,000 pounds ignored)"),
    "redrate": (GBP, "the reduced rate the regulations under para. 3(2) give for the case"),
    "redrateh": (GBP, "the reduced rate the regulations under para. 3(2) give for the case if the qualifying children "
                      "also included every child of a qualifying maintenance arrangement (para. 5A(3))"),
    "flatamt": (GBP, "the flat rate prescribed for para. 4(2)"),
    "brate": (GBP, "the basic rate (para. 2)"),
    "hbrate": (GBP, "the basic rate if the qualifying children also included every child of a qualifying maintenance "
                    "arrangement (para. 5A(3))"),
    "hyp": (GBP, "the amount which would be payable under para. 5A(3)"),
    "a5": (GBP, "the amount found under para. 5A(3)-(5)"),
    "rate": (GBP, "the weekly rate of child support maintenance (para. 1(1), 5A(2))"),
    "pre": (GBP, "the amount payable weekly to the person before shared care (para. 1(2)(a), (b), para. 6)"),
    "aft": (GBP, "the amount after the shared-care decrease of para. 7(3)-(5)"),
    "aft2": (GBP, "the amount after para. 7(6)"),
    "tot": (GBP, "the aggregate of the amounts after para. 7(6) payable to all persons with care"),
    "pay": (GBP, "the weekly amount of child support maintenance payable to the person"),
    "nights": (NIGHT, "the number of nights of shared care the Secretary of State determined or expects in the "
                      "prescribed 12-month period (para. 7(3), 8(2))"),
}
PAIR_UNITS = {  # per (child, person) integer constants
    "f": (F14, "the Table fraction for the child in the person's care, in fourteenths (0 if none)"),
    "d7": (GBP, "the 7 pounds of para. 7(6) for the child in the person's care (0 if the fraction is not one-half)"),
}
PERSON_UNITS = {"s": (F14, "the sum of the Table fractions of the qualifying children in the person's care, in "
                           "fourteenths (para. 7(5))")}
STATED_INTS = ("inc", "redrate", "redrateh", "flatamt", "nights")
BASIC_PCT = {1: 12, 2: 16, 3: 19}    # para. 2(1)
REMAINDER_PCT = {1: 9, 2: 12, 3: 15}  # para. 2(2)
REDUCE_PCT = {0: 0, 1: 11, 2: 14, 3: 16}  # para. 2(3)
TABLE = [  # para. 7(4): (row, low nights, high nights or None, fraction in fourteenths, the Table's words)
    (1, 52, 103, 2, "One-seventh"), (2, 104, 155, 4, "Two-sevenths"), (3, 156, 174, 6, "Three-sevenths"),
    (4, 175, None, 7, "One-half")]

FACTS = {  # unary facts on an item (the encoder states each true or false)
    "presc5a": "the non-resident parent is of a description prescribed for para. 5(a)",
    "variation": "the weekly rate is calculated following agreement to a variation (para. 5A(1)(b))",
    "qcalc": "the child is a qualifying child with respect to whom the maintenance calculation falls to be made",
    "qother": "the child is a qualifying child with respect to whom another maintenance calculation in respect of "
              "the non-resident parent has effect",
    "childof": "the child is a child of the non-resident parent",
    "morder": "the non-resident parent is liable to pay maintenance or aliment for the child under a maintenance order",
    "agree": "the non-resident parent is a party to an agreement which provides for him to make payments for the "
             "benefit of the child",
    "agree_presc": "that agreement is of a prescribed description",
    "habuk": "the child is habitually resident in the United Kingdom",
    "presc_roc": "the child is of a description prescribed under para. 10C(2)(b)",
    "b41b": "the benefit, pension or allowance is prescribed for para. 4(1)(b)",
    "b41c": "the benefit is prescribed for para. 4(1)(c)",
    "alsonrp": "the person is also a non-resident parent",
    "calcinforce": "the person is a person with respect to whom a maintenance calculation is in force",
}
BINARY = {
    "pwc": "(child, person) the person is the person with care of the child",
    "cbpaid": "(person, child) child benefit under Part IX SSCBA 1992 for the child is paid to the person for the week",
    "cbdue": "(person, child) child benefit under Part IX SSCBA 1992 for the child is due to be paid to the person for "
             "the week",
    "paid": "(person, benefit) the benefit, pension or allowance is paid to the person in respect of the week",
    "due": "(person, benefit) the benefit, pension or allowance is due to be paid to the person in respect of the week",
    "married": "(person, person) the two are married to each other",
    "civil": "(person, person) the two are civil partners of each other",
    "samehh": "(person, person) the two are members of the same household",
    "livetog": "(person, person) the two are living together as a married couple or civil partners (stated judgment)",
    "polyg": "(person, person) the two are husband and wife by virtue of a marriage entered into under a law which "
             "permits polygamy",
    "oppsex": "(person, person) the two are of the opposite sex",
}
STATED = ("livetog",)
DERIVED_UNARY = {
    "qc": "the child is a qualifying child (para. 10C(1))",
    "roc": "the child is a relevant other child (para. 10C(2))",
    "qma": "the non-resident parent is a party to a qualifying maintenance arrangement with respect to the child (5A(6))",
    "qch": "the child is a qualifying child if they also included every child of a qualifying maintenance arrangement",
    "roch": "the child is a relevant other child if the qualifying children also included those children (5A(3))",
    "hasqma": "para. 5A(1)(a) holds", "nil": "the nil rate applies (para. 5)",
    "l41b": "para. 4(1)(b) holds", "l41c": "para. 4(1)(c) holds", "c42": "a case falling within para. 4(2)",
    "flat41": "the flat rate of para. 4(1) applies", "flat42": "the flat rate of para. 4(2) applies",
    "flat": "a flat rate applies", "reduced": "a reduced rate applies (para. 3(1))",
    "basic": "the basic rate applies (para. 1(1))", "p5a": "para. 5A applies (5A(1))",
    "p6": "para. 6 applies (6(1))", "p7": "para. 7 applies (7(1))", "p8": "para. 8 applies (8(1))",
    "floor7": "para. 7(7) applies", "ispwc": "the person is a person with care of a qualifying child",
    "sh52": "para. 8(2): the care of a qualifying child in the person's care is shared for at least 52 nights",
    **{f"band{j}": f"para. 7(4) Table row {j}" for j in (1, 2, 3, 4)},
    "band0": "the number of nights is below the Table's first row",
}
COUNTS = {  # derived count atoms on x: name -> (the literal's builder over a child, words)
    "cq": "the number of qualifying children is k", "ch": "the number of children taken into account under 5A(3) is k",
    "cr": "the number of relevant other children is k", "crh": "the number of relevant other children under 5A(3) is k",
}
DERIVED_BINARY = {
    "recv": "(person, benefit) the person receives the benefit for the week (para. 10C(3))",
    "cbrecv": "(person, child) the person receives child benefit for the child for the week (para. 10C(3))",
    "couple": "(person, person) the two are a couple (para. 10C(5))",
    "partner": "(person, person) the second is the first's partner (para. 10C(4))",
    "inq": "(child, person) the child is a qualifying child and the person is its person with care",
}


# --- formula helpers (the ve-quantity@1 wire shapes; tenant_fees / council_tax conventions) -----------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def B(p, x, y): return ["binary", p, c(x), c(y)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def gbp(v): return ["decimal", GBP, v]
def nts(v): return ["decimal", NIGHT, str(v)]
def f14(v): return ["decimal", F14, str(v)]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def scale(tag, k, t): return ["scale", tag, str(k), t]
def add(tag, a, b): return ["add", tag, a, b]
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


def Sum(tag, terms):
    terms = list(terms)
    if not terms:
        return ["decimal", tag, "0"] if tag != GBP else gbp("0.00")
    r = terms[-1]
    for t in reversed(terms[:-1]):
        r = add(tag, t, r)
    return r


def k(base, x):
    """Per-item integer constant."""
    return ["const", INT_UNITS[base][0], f"{base}_{x}"]


def kp(base, ch, w):
    return ["const", PAIR_UNITS[base][0], f"{base}_{ch}_{w}"]


def ks(w):
    return ["const", F14, f"s_{w}"]


def iff_u(p, x, body): return Iff(U(p, x), body)
def iff_b(p, x, y, body): return Iff(B(p, x, y), body)
def cnt(name, kk): return f"{name}{kk}"


def exactly(n, lits):
    """Exactly n of the literals hold (a disjunction over the subsets of size n of the case's items)."""
    lits = list(lits)
    if n > len(lits):
        return FALSE
    out = []
    for chosen in itertools.combinations(range(len(lits)), n):
        out.append(And(*[lits[i] if i in chosen else Not(lits[i]) for i in range(len(lits))]))
    return Or(*out) if out else TRUE


# --- the case context ---------------------------------------------------------------------------------------------

class Ctx:
    """x = the non-resident parent; children, persons (everyone else the case names), benefits."""

    def __init__(self, parent, children=(), persons=(), benefits=()):
        self.x = parent
        self.children, self.persons, self.benefits = list(children), list(persons), list(benefits)

    @property
    def items(self):
        return [self.x] + self.children + self.persons + self.benefits

    @property
    def people(self):
        return [self.x] + self.persons


MAX_CHILDREN = 8  # the exactly-k disjunctions are written for at most 8 child items (none written beyond: refused)


def _counts(ctx):
    """Count atoms on x for the four child sets (exactly k, k = 0 .. number of child items)."""
    x, C = ctx.x, ctx.children
    if len(C) > MAX_CHILDREN:
        return []
    out = []
    for name, pred in (("cq", "qc"), ("ch", "qch"), ("cr", "roc"), ("crh", "roch")):
        lits = [U(pred, ch) for ch in C]
        for n in range(len(C) + 1):
            out.append(iff_u(cnt(name, n), x, exactly(n, lits)))
    return out


def count_is(ctx, name, n):
    """The guard 'the count is n' ('3' means three or more where the text says so: use count_atleast)."""
    return U(cnt(name, n), ctx.x) if n <= len(ctx.children) else FALSE


def count_atleast(ctx, name, n):
    return Or(*[U(cnt(name, m), ctx.x) for m in range(n, len(ctx.children) + 1)])


def _pct_class(ctx, name, kk):
    """The text's classes: one / two / three or more (kk = 1, 2, 3); for relevant other children also none (kk = 0)."""
    return count_atleast(ctx, name, 3) if kk == 3 else count_is(ctx, name, kk)


# --- para. 10C -----------------------------------------------------------------------------------------------------

def _qc(ctx):
    return [iff_u("qc", ch, Or(U("qcalc", ch), U("qother", ch))) for ch in ctx.children]


def _cbx(ctx, ch):
    """The non-resident parent or his partner receives child benefit for the child."""
    x = ctx.x
    return Or(B("cbrecv", x, ch), *[And(B("partner", x, y), B("cbrecv", y, ch)) for y in ctx.persons])


def _roc(ctx):
    return [iff_u("roc", ch, Or(And(Not(U("qc", ch)), _cbx(ctx, ch)), U("presc_roc", ch))) for ch in ctx.children]


def _receives(ctx):
    out = [iff_b("recv", y, b, Or(B("paid", y, b), B("due", y, b))) for y in ctx.people for b in ctx.benefits]
    out += [iff_b("cbrecv", y, ch, Or(B("cbpaid", y, ch), B("cbdue", y, ch))) for y in ctx.people for ch in ctx.children]
    return out


def _partner(ctx):
    x = ctx.x
    return [iff_b("partner", x, y, Or(B("couple", x, y), And(B("polyg", x, y), B("oppsex", x, y), B("samehh", x, y))))
            for y in ctx.persons]


def _couple(ctx):
    x = ctx.x
    out = []
    for y in ctx.persons:
        wed = Or(B("married", x, y), B("civil", x, y))
        out.append(iff_b("couple", x, y, Or(And(wed, B("samehh", x, y)), And(Not(wed), B("livetog", x, y)))))
    return out


# --- paras 3, 4, 5 and 1(1): which rate ---------------------------------------------------------------------------

def _cinc(ctx):
    x = ctx.x
    return [Implies(Le(k("inc", x), gbp("3000.00")), Eq(k("cinc", x), k("inc", x))),
            Implies(Lt(gbp("3000.00"), k("inc", x)), Eq(k("cinc", x), gbp("3000.00")))]


def _nil(ctx):
    x = ctx.x
    return [iff_u("nil", x, Or(U("presc5a", x), Lt(k("cinc", x), gbp("7.00"))))]


def _flat41(ctx):
    x, P, Bn = ctx.x, ctx.persons, ctx.benefits
    l41b = Or(*[And(B("recv", x, b), U("b41b", b)) for b in Bn])
    l41c = Or(*[And(Or(B("recv", x, b), *[And(B("partner", x, y), B("recv", y, b)) for y in P]), U("b41c", b))
                for b in Bn])
    return [iff_u("l41b", x, l41b), iff_u("l41c", x, l41c),
            iff_u("flat41", x, And(Not(U("nil", x)), Not(U("c42", x)),
                                   Or(Le(k("cinc", x), gbp("100.00")), U("l41b", x), U("l41c", x))))]


def _flat42(ctx):
    x, Bn = ctx.x, ctx.benefits
    c42 = Or(*[And(B("partner", x, y), U("alsonrp", y), U("calcinforce", y),
                   Or(*[And(Or(B("recv", x, b), B("recv", y, b)), U("b41c", b)) for b in Bn]))
               for y in ctx.persons])
    return [iff_u("c42", x, c42), iff_u("flat42", x, And(Not(U("nil", x)), U("c42", x))),
            iff_u("flat", x, Or(U("flat41", x), U("flat42", x)))]


def _reduced(ctx):
    x = ctx.x
    return [iff_u("reduced", x, And(Not(U("flat", x)), Not(U("nil", x)),
                                    Lt(k("cinc", x), gbp("200.00")), Lt(gbp("100.00"), k("cinc", x))))]


def _basic_rule(ctx):
    x = ctx.x
    return [iff_u("basic", x, And(Not(U("reduced", x)), Not(U("flat", x)), Not(U("nil", x))))]


# --- para. 2: the basic rate (and its 5A(3) twin) ------------------------------------------------------------------

def _basic_amount(ctx, target, qname, rname, side=("low", "high"), pct=None, rem=None, reduce=None, band=800):
    """10000 x basic = the text's percentages of the income after 10(3), treated as reduced by 2(3) (one rule per
    class of qualifying children x class of relevant other children x side of 800 pounds)."""
    pct, rem, reduce = pct or BASIC_PCT, rem or REMAINDER_PCT, reduce or REDUCE_PCT
    x = ctx.x
    out = []
    for qk in (1, 2, 3):
        for rk in (0, 1, 2, 3):
            red = reduce[rk]
            gq, gr = _pct_class(ctx, qname, qk), _pct_class(ctx, rname, rk)
            if FALSE in (gq, gr):
                continue  # no such class among the case's child items
            guard = And(gq, gr)
            reduced100 = scale(GBP, 100 - red, k("cinc", x))  # 100 x the income treated as reduced
            low = Le(reduced100, gbp(f"{band * 100}.00"))      # the reduced income does not exceed 800 pounds
            if "low" in side:
                out.append(Implies(And(guard, low),
                                   Eq(scale(GBP, 10000, k(target, x)), scale(GBP, pct[qk], reduced100))))
            if "high" in side:
                out.append(Implies(And(guard, Not(low)),
                                   Eq(scale(GBP, 10000, k(target, x)),
                                      add(GBP, scale(GBP, 100 * pct[qk], gbp(f"{band}.00")),
                                          scale(GBP, rem[qk], add(GBP, reduced100, gbp(f"-{band * 100}.00")))))))
    return out


def _basic_2_1(ctx, **kw):
    return _basic_amount(ctx, "brate", "cq", "cr", side=("low",), **kw)


def _basic_2_2(ctx, **kw):
    return _basic_amount(ctx, "brate", "cq", "cr", side=("high",), **kw)


# --- para. 5A ------------------------------------------------------------------------------------------------------

def _qma(ctx):
    x = ctx.x
    out = []
    for ch in ctx.children:
        out.append(iff_u("qma", ch, And(Or(U("morder", ch), And(U("agree", ch), U("agree_presc", ch))), U("habuk", ch))))
    return out


def _p5a(ctx):
    x = ctx.x
    has = Or(*[And(U("qma", ch), U("childof", ch), Not(U("qc", ch))) for ch in ctx.children])
    return [iff_u("hasqma", x, has),
            iff_u("p5a", x, And(U("hasqma", x), Or(U("basic", x), U("reduced", x),
                                                   And(U("variation", x), Or(U("flat", x), U("nil", x))))))]


def _hyp_sets(ctx):
    out = [iff_u("qch", ch, Or(U("qc", ch), U("qma", ch))) for ch in ctx.children]
    out += [iff_u("roch", ch, Or(And(Not(U("qch", ch)), _cbx(ctx, ch)), U("presc_roc", ch))) for ch in ctx.children]
    return out


def _hyp(ctx):
    """5A(3): the amount payable with the larger set: the basic rate (para. 2 over the larger set) or the reduced rate
    the regulations give for it (stated); a rate following a variation: not written."""
    x = ctx.x
    return (_basic_amount(ctx, "hbrate", "ch", "crh")
            + [Implies(And(U("p5a", x), U("basic", x)), Eq(k("hyp", x), k("hbrate", x))),
               Implies(And(U("p5a", x), U("reduced", x)), Eq(k("hyp", x), k("redrateh", x)))])


def _divide_multiply(ctx):
    """5A(4)-(5): divide by the number of children taken into account, multiply by the number of qualifying children:
    n x a5 = q x hyp, one rule per enumerated (n, q)."""
    x, N = ctx.x, len(ctx.children)
    out = []
    for n in range(1, N + 1):
        for q in range(1, n + 1):
            out.append(Implies(And(U("p5a", x), U(cnt("ch", n), x), U(cnt("cq", q), x)),
                               Eq(scale(GBP, n, k("a5", x)), scale(GBP, q, k("hyp", x)))))
    return out


def _greater7(ctx):
    x = ctx.x
    return [Implies(And(U("p5a", x), Le(gbp("7.00"), k("a5", x))), Eq(k("rate", x), k("a5", x))),
            Implies(And(U("p5a", x), Lt(k("a5", x), gbp("7.00"))), Eq(k("rate", x), gbp("7.00")))]


def _rate(ctx):
    """1(1) with 3(2), 4(1), 4(2), 5: the weekly rate when 5A does not apply."""
    x = ctx.x
    n5 = Not(U("p5a", x))
    return [Implies(And(n5, U("basic", x)), Eq(k("rate", x), k("brate", x))),
            Implies(And(n5, U("reduced", x)), Eq(k("rate", x), k("redrate", x))),
            Implies(And(n5, U("flat41", x)), Eq(k("rate", x), gbp("7.00"))),
            Implies(And(n5, U("flat42", x)), Eq(k("rate", x), k("flatamt", x))),
            Implies(And(n5, U("nil", x)), Eq(k("rate", x), gbp("0.00")))]


# --- paras 1(2), 6: the amount payable to each person with care before shared care -------------------------------

def _inq(ctx):
    return [iff_b("inq", ch, w, And(U("qc", ch), B("pwc", ch, w))) for ch in ctx.children for w in ctx.persons]


def _ispwc(ctx):
    out = [iff_u("ispwc", w, Or(*[B("inq", ch, w) for ch in ctx.children])) for w in ctx.persons]
    if len(ctx.children) <= MAX_CHILDREN:
        for w in ctx.persons:
            lits = [B("inq", ch, w) for ch in ctx.children]
            out += [iff_u(f"m{n}", w, exactly(n, lits)) for n in range(len(ctx.children) + 1)]
    return out


def _p6(ctx):
    x, P = ctx.x, ctx.persons
    two_pwc = Or(*[And(U("ispwc", a), U("ispwc", b)) for a, b in itertools.combinations(P, 2)])
    return [iff_u("p6", x, And(count_atleast(ctx, "cq", 2), two_pwc))]


def _pre_a(ctx):
    """1(2)(a): the applicable rate where para. 6 does not apply."""
    x = ctx.x
    return [Implies(And(U("ispwc", w), Not(U("p6", x))), Eq(k("pre", w), k("rate", x))) for w in ctx.persons]


def _pre_b(ctx):
    """1(2)(b) with 6(2): n x share = m x rate (n qualifying children, m in the person's care), one rule per
    enumerated (n, m)."""
    x, N = ctx.x, len(ctx.children)
    out = []
    for w in ctx.persons:
        for n in range(2, N + 1):
            for m in range(1, n + 1):
                out.append(Implies(And(U("ispwc", w), U("p6", x), U(cnt("cq", n), x), U(f"m{m}", w)),
                                   Eq(scale(GBP, n, k("pre", w)), scale(GBP, m, k("rate", x)))))
    return out


# --- para. 7 ---------------------------------------------------------------------------------------------------------

def _p7(ctx):
    x = ctx.x
    return [iff_u("p7", x, Or(U("basic", x), U("reduced", x), U("p5a", x)))]


def _row(j, lo, hi):
    def build(ctx):
        return [iff_u(f"band{j}", ch, And(Le(nts(lo), k("nights", ch)), Le(k("nights", ch), nts(hi)) if hi else None))
                for ch in ctx.children]
    return build


def _band0(ctx):
    return [iff_u("band0", ch, Lt(k("nights", ch), nts(52))) for ch in ctx.children]


def _fractions(ctx, table=None):
    """7(3)-(4) per child in the person's care: the Table fraction in fourteenths (0 below the first row)."""
    out = []
    for ch in ctx.children:
        for w in ctx.persons:
            out.append(Implies(Not(B("inq", ch, w)), Eq(kp("f", ch, w), f14(0))))
            out.append(Implies(And(B("inq", ch, w), U("band0", ch)), Eq(kp("f", ch, w), f14(0))))
            for (j, lo, hi, v, _) in (table or TABLE):
                out.append(Implies(And(B("inq", ch, w), U(f"band{j}", ch)), Eq(kp("f", ch, w), f14(v))))
    return out


def _sum_fractions(ctx):
    """7(5): the sum of the appropriate fractions (s) and its value atoms."""
    out = []
    for w in ctx.persons:
        out.append(Eq(ks(w), Sum(F14, [kp("f", ch, w) for ch in ctx.children])))
        out += [iff_u(f"s{v}", w, Eq(ks(w), f14(v))) for v in range(0, 7 * len(ctx.children) + 1)]
    return out


def _decrease(ctx):
    """7(3)-(5): the amount decreased by the sum of the fractions divided by the number of qualifying children in the
    person's care: 14m x aft = (14m - s) x pre, one rule per enumerated (m, s)."""
    x, N = ctx.x, len(ctx.children)
    out = []
    for w in ctx.persons:
        for m in range(1, N + 1):
            for v in range(0, 7 * m + 1):
                out.append(Implies(And(U("p7", x), U("ispwc", w), U(f"m{m}", w), U(f"s{v}", w)),
                                   Eq(scale(GBP, 14 * m, k("aft", w)), scale(GBP, 14 * m - v, k("pre", w)))))
    return out


def _half7(ctx, each="7.00"):
    """7(6): a further 7 pounds for each qualifying child in the person's care whose fraction is one-half."""
    x = ctx.x
    out = []
    for ch in ctx.children:
        for w in ctx.persons:
            half = And(B("inq", ch, w), U("band4", ch))
            out.append(Implies(half, Eq(kp("d7", ch, w), gbp(each))))
            out.append(Implies(Not(half), Eq(kp("d7", ch, w), gbp("0.00"))))
    for w in ctx.persons:
        out.append(Implies(And(U("p7", x), U("ispwc", w)),
                           Eq(k("aft2", w), add(GBP, k("aft", w),
                                                scale(GBP, -1, Sum(GBP, [kp("d7", ch, w) for ch in ctx.children]))))))
        out.append(Implies(Not(U("ispwc", w)), Eq(k("aft2", w), gbp("0.00"))))
    return out


def _floor(ctx):
    """7(7): the aggregate below 7 pounds -> 7 pounds a week, apportioned under para. 6 where it applies."""
    x, N = ctx.x, len(ctx.children)
    out = [Implies(U("p7", x), Eq(k("tot", x), Sum(GBP, [k("aft2", w) for w in ctx.persons]))),
           iff_u("floor7", x, And(U("p7", x), Lt(k("tot", x), gbp("7.00"))))]
    for w in ctx.persons:
        out.append(Implies(And(U("p7", x), Not(U("floor7", x)), U("ispwc", w)), Eq(k("pay", w), k("aft2", w))))
        out.append(Implies(And(U("p7", x), U("floor7", x), U("ispwc", w), Not(U("p6", x))), Eq(k("pay", w), gbp("7.00"))))
        for n in range(2, N + 1):
            for m in range(1, n + 1):
                out.append(Implies(And(U("p7", x), U("floor7", x), U("ispwc", w), U("p6", x), U(cnt("cq", n), x),
                                       U(f"m{m}", w)),
                                   Eq(scale(GBP, n, k("pay", w)), scale(GBP, m, gbp("7.00")))))
    return out


# --- para. 8 and the remaining 1(2) routes ---------------------------------------------------------------------------

def _p8(ctx):
    x = ctx.x
    return [iff_u("p8", x, And(U("flat", x), Not(U("p5a", x)), Or(U("l41b", x), U("l41c", x), U("c42", x))))]


def _sh52(ctx):
    return [iff_u("sh52", w, Or(*[And(B("inq", ch, w), Le(nts(52), k("nights", ch))) for ch in ctx.children]))
            for w in ctx.persons]


def _pay8(ctx):
    x = ctx.x
    out = []
    for w in ctx.persons:
        out.append(Implies(And(U("p8", x), U("ispwc", w), U("sh52", w)), Eq(k("pay", w), gbp("0.00"))))
        out.append(Implies(And(U("p8", x), U("ispwc", w), Not(U("sh52", w))), Eq(k("pay", w), k("pre", w))))
    return out


def _pay_other(ctx):
    """1(2): nil -> nothing payable (R5); a flat rate outside para. 8 is not adjusted."""
    x = ctx.x
    out = []
    for w in ctx.persons:
        out.append(Implies(And(U("nil", x), Not(U("p5a", x)), U("ispwc", w)), Eq(k("pay", w), gbp("0.00"))))
        out.append(Implies(And(U("flat", x), Not(U("p8", x)), Not(U("p5a", x)), U("ispwc", w)),
                           Eq(k("pay", w), k("pre", w))))
    return out


def _empty(ctx):
    return []


UNITS = {
    1: ("RULE", lambda ctx: _basic_rule(ctx) + _rate(ctx),
        "1(1): basic unless a reduced, a flat or the nil rate applies; 'subject to 5A': the rate rules are guarded by "
        "not-5A and 5A(2) gives the rate where 5A applies"),
    2: ("RULE", lambda ctx: _pre_a(ctx) + _pay_other(ctx),
        "1(2)(a), (b): the applicable rate, or apportioned under 6, adjusted under 7 or 8; nil -> nothing (R5)"),
    3: ("RULE", _basic_2_1, "2(1): 12 / 16 / 19 per cent by class of qualifying children (LIN; literals of the text)"),
    4: ("RULE", _basic_2_2, "2(2): above 800 pounds, the 2(1) amount on the first 800 plus 9 / 12 / 15 per cent of the "
        "remainder (NEW-BAND, written linearly with the text's literals)"),
    5: ("RULE", _empty, "2(3): 'treated as reduced' by 11 / 14 / 16 per cent by class of relevant other children "
        "(deeming; written inside units 3-4's rules as (100 - p) x income)"),
    6: ("RULE", _reduced, "3(1): a reduced rate if neither flat nor nil and 100 < income < 200 (after 10(3), R2)"),
    7: ("PART", _empty, "cross-reference", "3(2): the reduced rate is prescribed by regulations (not pinned): the "
        "amount the regulations give is a stated fact (redrate); unit 1's rate rule uses it"),
    8: ("PART", _flat41, "cross-reference", "4(1): written; which benefits are prescribed for (1)(b), (c) is a stated "
        "fact (regulations not pinned)"),
    9: ("PART", _flat42, "cross-reference", "4(2): written; the prescribed amount and 'a maintenance calculation is in "
        "force' are stated facts"),
    10: ("PART", _nil, "cross-reference",
         "5: (b) written; (a) 'of a prescribed description' a stated fact"),
    11: ("PART", _p5a, "cross-reference",
         "5A(1): written; (b)'s 'calculated following agreement to a variation' is a stated fact and the rate under a "
         "variation is not written (variations are outside the pinned text; R4)"),
    12: ("RULE", _greater7, "5A(2): the greater of 7 pounds and the amount found"),
    13: ("PART", lambda ctx: _hyp_sets(ctx) + _hyp(ctx), "cross-reference",
         "5A(3): the counterfactual set (qualifying children plus every arrangement child) written; the basic rate "
         "over it written (para. 2); the reduced rate for it is the regulations' (stated, redrateh); a variation: "
         "not written (R4)"),
    14: ("RULE", _empty, "5A(4): divide by the number of children taken into account (in unit 15's n x a5 = q x hyp)"),
    15: ("RULE", _divide_multiply, "5A(5): multiply by the number of qualifying children: n x a5 = q x hyp, one rule "
         "per enumerated (n, q) (PROD by case split)"),
    16: ("PART", _qma, "cross-reference", "5A(6): written; 'maintenance order', 'agreement of a prescribed "
         "description' and 'habitually resident' are stated facts"),
    17: ("RULE", _p6, "6(1): more than one qualifying child and more than one person with care"),
    18: ("RULE", _pre_b,
         "6(2): n x share = m x rate (PROD by case split over the enumerated counts)"),
    19: ("RULE", _p7, "7(1): para. 7 applies to the basic rate, a reduced rate or a rate determined under 5A"),
    20: ("RULE", _empty, "7(2): shared care with the non-resident parent having the child overnight: the stated "
         "nights; the decrease is units 21-28"),
    21: ("RULE", _band0, "7(3): the decrease follows the number of nights the Secretary of State determined or "
         "expects (stated: the official determination)"),
    **{n: ("RULE", _row(j, lo, hi), f"7(4) Table row {j}: {lo} to {hi} nights -> {words} (an interval on the stated "
           f"nights, as the text gives it)" if hi else f"7(4) Table row {j}: {lo} or more nights -> {words}")
       for n, (j, lo, hi, v, words) in zip(range(22, 26), TABLE)},
    26: ("RULE", lambda ctx: _fractions(ctx) + _sum_fractions(ctx) + _decrease(ctx),
         "7(5): the sum of the fractions divided by the number of qualifying children in the person's care: 14m x aft "
         "= (14m - s) x pre (fractions in fourteenths; case split over m and s)"),
    27: ("RULE", _half7, "7(6): 7 pounds for each child whose fraction is one-half"),
    28: ("RULE", _floor, "7(7): the aggregate below 7 pounds -> 7 pounds a week, apportioned under 6 (R7)"),
    29: ("RULE", _p8, "8(1): a flat rate because of 4(1)(b), (c) or 4(2)"),
    30: ("RULE", lambda ctx: _sh52(ctx) + _pay8(ctx), "8(2): at least 52 nights -> nil to that child's person with "
         "care (the prescribed 12-month period: the stated nights)"),
    31: ("RULE", _cinc, "10(3): any amount over 3,000 pounds ignored (R1: before 2(3))"),
    32: ("RULE", _qc, "10C(1): the qualifying children of the calculation or of another calculation in force (stated "
         "official facts)"),
    33: ("PART", _roc, "cross-reference", "10C(2): (a) written over 'receives child benefit under Part IX SSCBA 1992' "
         "(stated); (b) 'such other description as may be prescribed' a stated fact"),
    34: ("RULE", _receives, "10C(3): receives = paid or due to be paid in respect of the week"),
    35: ("RULE", _partner, "10C(4): partner = the other member of a couple, or a polygamous spouse of the opposite sex in "
         "the same household"),
    36: ("PART", _couple, "other:judgment standard", "10C(5): (a) written; (b) 'living together as a married couple or "
         "civil partners' a stated judgment (stated)"),
}
# Grounding helpers outside any one unit: the count atoms (units 3-5, 14-15, 18, 26), the qualifying children in a
# person's care (units 17-18, 26-30) and the 5A twin of para. 2 (unit 13).
EXTRA = [("counts", _counts), ("inq", _inq), ("ispwc", _ispwc)]


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
    seen = set()
    for n, builder in entries:
        for i, f in enumerate(builder(ctx)):
            for j, part in enumerate(conjuncts(f)):
                kk = key(part)
                if kk in seen:
                    continue
                seen.add(kk)
                out.append({"id": f"u{n}.{i}.{j}", "unit": n, "formula": part, "defines": defines(part)})
    return out


# --- structure helpers (council_tax translation.py conventions) ----------------------------------------------------

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

def int_constants(ctx):
    """name -> (unit, words) for every integer constant of the case."""
    out = {}
    for x in ctx.items:
        for base, (u, w) in INT_UNITS.items():
            out[f"{base}_{x}"] = (u, f"{w} ({x})")
    for ch in ctx.children:
        for w in ctx.persons:
            for base, (u, words) in PAIR_UNITS.items():
                out[f"{base}_{ch}_{w}"] = (u, f"{words} ({ch}, {w})")
    for w in ctx.persons:
        out[f"s_{w}"] = (F14, PERSON_UNITS["s"][1] + f" ({w})")
    return out


def environment(ctx):
    consts = {}
    for x in ctx.items:
        consts[x] = {"sort": "item", "description": f"The case's item {x}.", "verbalisation": f"item {x}"}
    for name, (u, w) in int_constants(ctx).items():
        consts[name] = {"sort": "$int", "unit": u, "description": f"{w[0].upper() + w[1:]}.", "verbalisation": w}
    unary = {**FACTS, **DERIVED_UNARY}
    N = len(ctx.children)
    for name, words in COUNTS.items():
        unary.update({cnt(name, n): words.replace(" k", f" {n}") for n in range(N + 1)})
    unary.update({f"m{n}": f"the number of qualifying children in the person's care is {n}" for n in range(N + 1)})
    unary.update({f"s{v}": f"the sum of the Table fractions in the person's care is {v} fourteenths"
                  for v in range(7 * N + 1)})
    preds = {n: {"arguments": ["item"], "description": d[0].upper() + d[1:] + "."} for n, d in unary.items()}
    preds.update({n: {"arguments": ["item", "item"], "description": d[0].upper() + d[1:] + "."}
                  for n, d in {**BINARY, **DERIVED_BINARY}.items()})
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "A parent, child, other person or benefit the case names."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {NIGHT: {"scale": "1", "display": {"kind": "decimal", "label": "nights"}},
                      F14: {"scale": "1", "display": {"kind": "decimal", "label": "fourteenths"}},
                      GBP: {"scale": "100", "display": {"kind": "money", "currency": "GBP", "input_symbol": "£"}}}}


# --- planted errors (run.py --mutants): each must change the answer of at least one question ----------------------

def _put(n, builder):
    def apply(t):
        t = dict(t)
        t[n] = (t[n][0], builder, *t[n][2:])
        return t
    return apply


def _chain(*fs):
    def apply(t):
        for f in fs:
            t = f(t)
        return t
    return apply


NO_REDUCTION = {0: 0, 1: 0, 2: 0, 3: 0}
MUTANTS = {
    "M1": ("TABLE: para. 7(4) row 1's upper limit 103 read as 104 (row 2 from 105)",
           _chain(_put(22, _row(1, 52, 104)), _put(23, _row(2, 105, 155)))),
    "M2": ("TABLE: para. 7(4) row 4 'One-half' read as three-sevenths",
           _put(26, lambda ctx: _fractions(ctx, [r if r[0] != 4 else (4, 175, None, 6, "x") for r in TABLE])
                + _sum_fractions(ctx) + _decrease(ctx))),
    "M3": ("DEEMING: para. 2(3) 'treated as reduced' dropped",
           _chain(_put(3, lambda ctx: _basic_2_1(ctx, reduce=NO_REDUCTION)),
                  _put(4, lambda ctx: _basic_2_2(ctx, reduce=NO_REDUCTION)))),
    "M4": ("DEEMING: para. 10(3) 'any amount over 3,000 pounds ignored' dropped",
           _put(31, lambda ctx: [Eq(k("cinc", ctx.x), k("inc", ctx.x))])),
    "M5": ("ARITHMETIC: para. 2(1) 12 per cent for one qualifying child read as 11",
           _chain(_put(3, lambda ctx: _basic_2_1(ctx, pct={**BASIC_PCT, 1: 11})),
                  _put(4, lambda ctx: _basic_2_2(ctx, pct={**BASIC_PCT, 1: 11})))),
    "M6": ("ARITHMETIC: para. 2(2) threshold 800 pounds read as 900",
           _chain(_put(3, lambda ctx: _basic_2_1(ctx, band=900)), _put(4, lambda ctx: _basic_2_2(ctx, band=900)))),
    "M7": ("ARITHMETIC: para. 5A(4)-(5) divide and multiply dropped (the amount found = the 5A(3) amount)",
           _put(15, lambda ctx: [Implies(f[1], Eq(f[2][1][3], f[2][2][3])) for f in _divide_multiply(ctx)])),
    "M8": ("ARITHMETIC: para. 7(6) 7 pounds per child read as 6", _put(27, lambda ctx: _half7(ctx, "6.00"))),
    "M9": ("FLOOR: para. 7(7) dropped (no 7 pounds floor)",
           _put(28, lambda ctx: [Iff(f[1][1], FALSE) if is_iff(f) else f for f in _floor(ctx)])),
    "M10": ("ARITHMETIC: para. 6(2) apportionment dropped (each person with care gets the whole rate)",
            _put(18, lambda ctx: [Implies(f[1], Eq(f[2][1][3], f[2][2][3])) for f in _pre_b(ctx)])),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
