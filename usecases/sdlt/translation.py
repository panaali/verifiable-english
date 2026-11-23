"""SDLT, Finance Act 2003 s.55 + Sch 6ZA (statute corpus batch 2 law 1): the VE translation, one pass with today's language.
SAME-FAMILY.

Row statute-corpus-sdlt (dri-statute-corpus-sdlt-1123, Opus 5.5). Written from the pinned source only (manage-agents
reviews/spare/statute-corpus/batch2/sdlt/source.txt, sha256 80938433...a88684) BEFORE the encoder's question file was
opened. Evidence branch: nothing here is a Lean kernel line, a profile, a refuses pair or a lint change.

UNITS maps each in-scope unit n of batch2/sdlt/units.jsonl (tools/sample5.py --units sdlt) to
  ("RULE", builder, note)          the unit is written: builder(ctx) gives its ground formulas for one case;
  ("PART", builder, cause, note)   written except the part named in the note;
  ("NOT", None, cause, note)       not written (the ledger row's cause, CAUSES.tsv v2).
Vocabulary: two sorts, txn (a land transaction the case names: the one asked about, transactions linked to it, a later
transaction, and each purchaser's earlier acquisitions anywhere) and person. Money in gbp_penny, years to run in years.
Grounding is mechanical: "each of the purchasers" is a conjunction over the persons the case names; "linked", "earlier"
and the 1(6) relations are binary facts the case lists, and a quantifier or total over them ("the total of the chargeable
consideration for all those transactions", "linked only to land transactions within sub-paragraph (6)", "has not
previously ...") is a finite conjunction, disjunction or sum over the items the case LINKS by that fact (closed world
over the case's items: an encoding convention, encode.py C1-C2).
Tables: every row is written as the text gives it: the part of the consideration the row names (by guarded linear rules)
and the row's rate as 100 x amount = rate x part on the penny grid (an amount not exact in pence has no solution: nothing
derived). Step 3 of s.55(1C) (multiply by C / R, a product of two quantities) is NOT written: the language's arithmetic is
linear (add, scale by a literal); linked-transaction amounts are therefore never derived (amount arithmetic).
"""
from __future__ import annotations

import hashlib
import json

GBP, YEARS = "gbp_penny", "years"

# per-txn integer constants: base -> (unit, words). Bases never contain "_" (run.py splits names on the first "_").
TABLE_A = [("sa1", "pa1", "0.00", "125000.00", 0), ("sa2", "pa2", "125000.00", "250000.00", 2),
           ("sa3", "pa3", "250000.00", "925000.00", 5), ("sa4", "pa4", "925000.00", "1500000.00", 10),
           ("sa5", "pa5", "1500000.00", None, 12)]
TABLE_B = [("sb1", "pb1", "0.00", "150000.00", 0), ("sb2", "pb2", "150000.00", "250000.00", 2),
           ("sb3", "pb3", "250000.00", None, 5)]
TABLE_F = [("sf1", "pf1", "0.00", "300000.00", 0), ("sf2", "pf2", "300000.00", "500000.00", 5)]  # para 4 substitute

INT_UNITS = {
    "cons": (GBP, "the chargeable consideration for the transaction"),
    "rc": (GBP, "the relevant consideration (s. 55(3)(b), (4)(b); Sch. 6ZA para. 7)"),
    "years": (YEARS, "the whole years the lease has to run at the beginning of the day after its effective date or "
                     "acquisition (a lease only)"),
    "taxa": (GBP, "the sum of the amounts at Step 1 under Table A (Step 2)"),
    "taxb": (GBP, "the sum of the amounts at Step 1 under Table B (Step 2)"),
    "taxf": (GBP, "the sum of the amounts at Step 1 under the Table A substituted by Sch. 6ZA para. 4 (Step 2)"),
    "taxnr": (GBP, "the amount of tax chargeable in respect of the transaction if relief is not claimed"),
    "taxr": (GBP, "the amount of tax chargeable in respect of the transaction if relief is claimed"),
}
for _tbl, _name in ((TABLE_A, "Table A"), (TABLE_B, "Table B"), (TABLE_F, "the substituted Table A")):
    for _i, (_s, _p, _lo, _hi, _r) in enumerate(_tbl, 1):
        INT_UNITS[_s] = (GBP, f"the part of the relevant consideration in row {_i} of {_name}")
        INT_UNITS[_p] = (GBP, f"the amount at Step 1 for row {_i} of {_name} ({_r}%)")
STATED_BASES = ("cons", "years")  # stated by the encoder; every other base is derived (a run step)

FACTS = {  # unary facts on a txn (the encoder states each true or false)
    "freehold": "the main subject-matter is the freehold (a major interest: s. 117, rule of the test)",
    "lease": "the main subject-matter is a lease, a term of years absolute (a major interest: s. 117, rule of the test)",
    "allres": "the land an interest in which is the main subject-matter consists entirely of residential property",
    "hrt": "the transaction is a higher rates transaction for the purposes of Sch. 4ZA para. 1 (given)",
    "sch4a3": "paragraph 3 of Schedule 4A applies to the transaction (given)",
    "s74step4": "step 4 of section 74(1A) applies to the transaction (given)",
    "usedsingle": "the building or part of a building is used as a single dwelling",
    "suitablesingle": "the building or part of a building is suitable for use as a single dwelling (stated judgment)",
    "constructing": "the building or part is in the process of being constructed or adapted for use as a single dwelling",
    "used116": "the building or part is used for a purpose specified in section 116(2) or (3) (given)",
    "multidwelling": "the main subject-matter includes more than one building or part of a building",
    "extraland": "the main subject-matter includes land besides the building or part of a building",
    "extragarden": "that other land is, or is to be, occupied or enjoyed with the dwelling as a garden or grounds",
    "extrabenefit": "that other land subsists, or is to subsist, for the benefit of the dwelling",
    "substperf": "the effective date is the day a contract (including any agreement) was substantially performed, by "
                 "virtue of a relevant deeming provision (given)",
    "tobebuilt": "the main subject-matter is an interest in a building or part to be constructed or adapted under the "
                 "contract for use as a single dwelling",
    "notbegun": "construction or adaptation had not begun by the time the contract was substantially performed",
    "affirst": "the transaction is the first transaction under an alternative finance arrangement (s. 71A(1) or 73(1)) "
               "entered into between a person and a financial institution (given)",
    "landtxn": "the acquisition was a land transaction within the Act (given for earlier acquisitions)",
    "wales": "the dwelling is situated in Wales",
    "abroad": "the dwelling is situated in a country or territory outside England, Wales and Northern Ireland",
    "equivalent": "the interest acquired outside England, Wales and Northern Ireland is equivalent to a major interest "
                  "(stated judgment)",
}
PFACTS = {"individual": "the person is an individual"}
PTFACTS = {  # binary facts (person, txn), closed world over every pair
    "acquires": "the person acquires the interest (is a party acquiring it)",
    "baretrustee": "the person acquires the interest as bare trustee",
    "btbeneficiary": "the person is a person for whom the acquirer is bare trustee",
    "afperson": "the person is 'the person' for the purposes of s. 71A or 73 under the arrangement whose first "
                "transaction this is (given)",
    "wouldbeaf": "the person would have been such a person for an acquisition of a dwelling outside the Act's reach had "
                 "ss. 71A/73 been in force there (Sch. 6ZA para. 6(1)(d); stated judgment)",
    "intends": "the person intends to occupy the dwelling as the person's only or main residence",
}
TTFACTS = {  # binary facts (txn, txn): only the pairs the case lists (C2); rules quantify over them
    "linked": "the two transactions are linked transactions (s. 108, given)",
    "earlier": "the first acquisition was made before the second transaction",
    "gardenof": "the main subject-matter of the first consists of an interest in land that is or forms part of the "
                "garden or grounds of the dwelling bought by the second",
    "benefitof": "the main subject-matter of the first consists of an interest in or right over land that subsists for "
                 "the benefit of the dwelling bought by the second, or of land that is or forms part of its garden or "
                 "grounds",
}
STATED = ("suitablesingle", "equivalent", "wouldbeaf", "intends")
DERIVED = {  # unary on txn
    "applies55": "section 55 applies to the transaction (s. 55(1A))",
    "linkedany": "the transaction is one of a number of linked transactions",
    "tablea": "the appropriate table is Table A",
    "major6": "the main subject-matter is a major interest for the purposes of Sch. 6ZA (para. 8)",
    "shortlease": "the main subject-matter is a lease with less than 21 years to run",
    "dwelling": "the building or part counts as a dwelling (Sch. 6ZA para. 9(2), (7), (8))",
    "offplan": "the main subject-matter is taken to consist of a major interest in a dwelling under para. 9(5)",
    "extraok": "any other land in the main subject-matter is taken to be part of the dwelling (para. 9(3), (4))",
    "midwelling": "the main subject-matter is a major interest in a dwelling (for this Schedule)",
    "c1": "the first condition (para. 1(2))", "c2": "the second condition (para. 1(3))",
    "c3": "the third condition (para. 1(4))", "c4": "the fourth condition (para. 1(5), (6))",
    "elig1": "relief may be claimed under paragraph 1", "elig2": "relief may be claimed under paragraph 2",
    "claimable": "first-time buyers' relief may be claimed for the transaction",
}
PDERIVED = {  # binary (person, txn)
    "purch16": "the person is the purchaser (Sch. 16 para. 3 as if (2) and (3) were omitted: paras. 3A, 6(3))",
    "purch6": "the person is treated as a purchaser for paras. 1(4) and 2(2) (para. 3(2), para. 3A)",
    "hita": "the acquisition makes the person not a first-time buyer under para. 6(1)(a)",
    "hitb": "the acquisition makes the person not a first-time buyer under para. 6(1)(b)",
    "hitc": "the acquisition makes the person not a first-time buyer under para. 6(1)(c)",
    "hitd": "the acquisition makes the person not a first-time buyer under para. 6(1)(d)",
    "ftb": "the person is a first-time buyer in relation to the transaction (para. 6(1))",
}
THRESH = "500000.00"


# --- formula helpers (the ve-quantity@1 wire shapes; tenant_fees/translation.py conventions) ---------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def B(p, x, y): return ["binary", p, c(x), c(y)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def gbp(v): return ["decimal", GBP, v]
def yrs(v): return ["decimal", YEARS, v]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def add(tag, a, b): return ["add", tag, a, b]
def scale(tag, k, t): return ["scale", tag, str(k), t]
def minus(a, b): return add(GBP, a, scale(GBP, -1, b))
TRUE = ["true"]
FALSE = ["not", ["true"]]


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


def Sum(terms):
    r = terms[0]
    for t in terms[1:]:
        r = add(GBP, r, t)
    return r


def k(base, x):
    """Per-txn integer constant."""
    return ["const", INT_UNITS[base][0], f"{base}_{x}"]


def iff_atom(p, x, body):
    return Iff(U(p, x), body)


def iff_b(p, x, y, body):
    return Iff(B(p, x, y), body)


# --- the case context ---------------------------------------------------------------------------------------

class Ctx:
    def __init__(self, txns, persons, links=()):
        self.txns = list(txns)
        self.persons = list(persons)
        self.items = self.txns  # run.py: per-item constants are per txn
        self.links = {(p, a, b) for (p, a, b) in links}

    def linked(self, pred, x):
        """Txns y with the stated binary fact pred(x, y)."""
        return [b for (p, a, b) in sorted(self.links) if p == pred and a == x]

    def linked_to(self, pred, x):
        """Txns y with the stated binary fact pred(y, x)."""
        return [a for (p, a, b) in sorted(self.links) if p == pred and b == x]


def each(fn):
    return lambda ctx: [f for x in ctx.txns for f in fn(x, ctx)]


def each_pt(fn):
    return lambda ctx: [f for p in ctx.persons for x in ctx.txns for f in fn(p, x, ctx)]


# --- the tables (s. 55(1B) Tables A and B; Sch. 6ZA para. 4) ------------------------------------------------------

def slice_rules(x, s, lo, hi):
    """The row's part of the relevant consideration R: 'so much as does not exceed hi' (lo = 0), 'so much as exceeds lo
    but does not exceed hi', 'the remainder (if any)' / 'any remainder (so far as not exceeding hi)' (hi given)."""
    R, S = k("rc", x), k(s, x)
    out = [Implies(Le(R, gbp(lo)), Eq(S, gbp("0.00")))]
    if hi is None:
        out.append(Implies(Lt(gbp(lo), R), Eq(S, minus(R, gbp(lo)))))
    else:
        out.append(Implies(And(Lt(gbp(lo), R), Le(R, gbp(hi))), Eq(S, minus(R, gbp(lo)))))
        out.append(Implies(Lt(gbp(hi), R), Eq(S, minus(gbp(hi), gbp(lo)))))
    return out


def rate_rule(x, s, p, rate):
    """Step 1: the row's rate applied to its part: 100 x amount = rate x part (0% -> the amount is 0)."""
    if rate == 0:
        return [Eq(k(p, x), gbp("0.00"))]
    return [Eq(scale(GBP, 100, k(p, x)), scale(GBP, rate, k(s, x)))]


def row(table, i):
    s, p, lo, hi, rate = table[i]
    return each(lambda x, ctx: slice_rules(x, s, lo, hi) + rate_rule(x, s, p, rate))


def step2(table, total):
    return each(lambda x, ctx: [Eq(k(total, x), Sum([k(r[1], x) for r in table]))])


def relief_rules(src):
    """Para. 4: with relief, (1B) applies with the substituted table in place of Table A (src = its Step 2 sum)."""
    return each(lambda x, ctx: [
        Implies(And(U("applies55", x), Not(U("linkedany", x)), U("tablea", x)), Eq(k("taxr", x), k(src, x))),
        Implies(And(U("applies55", x), Not(U("linkedany", x)), Not(U("tablea", x))), Eq(k("taxr", x), k("taxb", x)))])


# --- the units (n = batch2/sdlt/units.jsonl) ------------------------------------------------------------------

UNITS = {
    # ---- s. 55 ----
    1: ("RULE", lambda ctx: [], "s. 55(1): carried by the (1B) rules (units 3-12, 15) and the written part of (1C)"),
    2: ("PART", each(lambda x, ctx: [iff_atom("applies55", x, And(Not(U("sch4a3", x)), Not(U("s74step4", x))))]),
        "cross-reference",
        "s. 55(1A): whether Sch. 4A para. 3 or s. 74(1A) step 4 applies is a given fact (fixed: neither)"),
    3: ("RULE", each(lambda x, ctx: [
        Implies(And(U("applies55", x), Not(U("linkedany", x)), U("tablea", x)), Eq(k("taxnr", x), k("taxa", x))),
        Implies(And(U("applies55", x), Not(U("linkedany", x)), Not(U("tablea", x))), Eq(k("taxnr", x), k("taxb", x)))]),
        "s. 55(1B) Step 1 for a transaction that is not linked: the tax is the Step 2 sum under the appropriate table"),
    4: ("RULE", lambda ctx: step2(TABLE_A, "taxa")(ctx) + step2(TABLE_B, "taxb")(ctx) + each(lambda x, ctx2: [
        iff_atom("tablea", x, And(U("allres", x), *[U("allres", y) for y in ctx2.linked("linked", x)]))])(ctx),
        "s. 55(1B) the appropriate table ((a) Table A if the relevant land is entirely residential, (b) Table B if it "
        "includes other land; the relevant land per (3)(a) / (4)(a)) and Step 2 (add the Step 1 amounts)"),
    5: ("RULE", row(TABLE_A, 0), "Table A row 1 (0%)"),
    6: ("RULE", row(TABLE_A, 1), "Table A row 2 (2%)"),
    7: ("RULE", row(TABLE_A, 2), "Table A row 3 (5%)"),
    8: ("RULE", row(TABLE_A, 3), "Table A row 4 (10%)"),
    9: ("RULE", row(TABLE_A, 4), "Table A row 5, the remainder (12%)"),
    10: ("RULE", row(TABLE_B, 0), "Table B row 1 (0%)"),
    11: ("RULE", row(TABLE_B, 1), "Table B row 2 (2%)"),
    12: ("RULE", row(TABLE_B, 2), "Table B row 3, the remainder (5%)"),
    13: ("RULE", each(lambda x, ctx: [iff_atom("linkedany", x, Or(*[B("linked", x, y) for y in ctx.linked("linked", x)]))]),
         "s. 55(1C) Step 1: the same table rows applied to the relevant consideration (the total, unit 16); 'one of a "
         "number of linked transactions' = linked to some transaction the case lists"),
    14: ("PART", lambda ctx: [], "amount arithmetic",
         "s. 55(1C) appropriate table and Step 2 written (units 4, 16); Step 3 'multiply ... by C / R' NOT written: a "
         "product of the Step 2 amount and a ratio of two quantities is outside the linear arithmetic (add, scale by a "
         "literal); no tax amount is derived for a linked transaction (NEW-BAND x SUM x PROD)"),
    15: ("RULE", each(lambda x, ctx: [Implies(Not(U("linkedany", x)), Eq(k("rc", x), k("cons", x)))]),
         "s. 55(3): (a) the relevant land is the transaction's own land (unit 4's tablea); (b) R = C"),
    16: ("RULE", each(lambda x, ctx: [Implies(U("linkedany", x), Eq(k("rc", x), Sum(
        [k("cons", x)] + [k("cons", y) for y in ctx.linked("linked", x)])))]),
         "s. 55(4): (a) any land of any of the linked transactions (unit 4); (b) R = the total of the chargeable "
         "consideration for all those transactions: a finite sum over the transactions the case lists as linked "
         "(closed world, C2)"),
    # ---- Sch. 6ZA Part 1 ----
    17: ("RULE", each(lambda x, ctx: [iff_atom("elig1", x, And(U("c1", x), U("c2", x), U("c3", x), U("c4", x),
                                                                Not(U("hrt", x))))]),
         "para. 1(1): relief may be claimed if the four conditions are met, subject to (7)"),
    18: ("PART", each(lambda x, ctx: [
        iff_atom("c1", x, And(U("major6", x), Or(
            And(U("dwelling", x), Not(U("multidwelling", x)), U("extraok", x)), U("offplan", x))))]),
         "definition by reference",
         "para. 1(2): 'major interest' is s. 117's (freehold, or a lease: a rule of the test, given as facts); 'a single "
         "dwelling' = one building or part counting as a dwelling (9(2)) with no other land beyond 9(3)-(4)"),
    19: ("RULE", each(lambda x, ctx: [iff_atom("c2", x, Le(k("rc", x), gbp(THRESH)))]),
         "para. 1(3): relevant consideration (para. 7; no rent: fixed fact) not more than 500,000"),
    20: ("PART", each(lambda x, ctx: [iff_atom("c3", x, And(*[
        Implies(B("purch6", p, x), And(B("ftb", p, x), B("intends", p, x))) for p in ctx.persons]))]),
         "other:judgment standard",
         "para. 1(4): each purchaser (para. 3 / 3A, unit 27) a first-time buyer (para. 6) intending to occupy as only or "
         "main residence (an intention: a fact; 'main' residence among several: stated judgment)"),
    21: ("RULE", each(lambda x, ctx: [iff_atom("c4", x, And(*[
        Or(B("gardenof", y, x), B("benefitof", y, x)) for y in ctx.linked("linked", x)]))]),
         "para. 1(5): not linked (empty conjunction) or linked only to transactions within (6)"),
    22: ("RULE", lambda ctx: [],
         "para. 1(6): (a) garden or grounds, (b)(i)/(ii) interest or right for the benefit of the dwelling or its garden: "
         "the binary facts gardenof / benefitof read by unit 21's rule"),
    23: ("PART", lambda ctx: [], "cross-reference",
         "para. 1(7): written in unit 17's rule (not hrt); 'higher rates transaction' (Sch. 4ZA) a given fact"),
    24: ("RULE", each(lambda x, ctx: [iff_atom("elig2", x, Or(*[
        And(B("linked", x, m), U("elig1", m),
            *[Implies(B("purch6", p, x), B("purch6", p, m)) for p in ctx.persons])
        for m in ctx.linked("linked", x)]))]),
         "para. 2(1): linked to a main transaction eligible under para. 1 (or that would be if chargeable: elig1 is "
         "computed whatever its chargeability)"),
    25: ("RULE", lambda ctx: [], "para. 2(2): written in unit 24's rule (every purchaser of it a purchaser of the main)"),
    26: ("PART", lambda ctx: [], "cross-reference",
         "para. 3(1): whether a transaction is the first transaction under an alternative finance arrangement with a "
         "financial institution (ss. 71A, 73) is a given fact (affirst); read by unit 27's rule"),
    27: ("RULE", each_pt(lambda p, x, ctx: [
        iff_b("purch6", p, x, Or(And(B("purch16", p, x), Not(U("affirst", x))), And(U("affirst", x), B("afperson", p, x))))]),
         "para. 3(2): the person (rather than the institution) is treated as the purchaser for 1(4) and 2(2)"),
    28: ("NOT", None, "definition by reference",
         "para. 3(3): 'alternative finance arrangement' (ss. 71A(1), 73(1)) and 'financial institution' (s. 73BA): given"),
    29: ("NOT", None, "definition by reference", "para. 3(3): 'first transaction' (ss. 71A(1)(a), 73(1)(a)(i)): given"),
    30: ("PART", each_pt(lambda p, x, ctx: [
        iff_b("purch16", p, x, Or(And(B("acquires", p, x), Not(B("baretrustee", p, x))), B("btbeneficiary", p, x)))]),
         "cross-reference",
         "para. 3A: Sch. 16 para. 3 (not pinned; a rule of the test) as if (2) and (3) were omitted: the beneficiary, not "
         "the bare trustee, is the purchaser, a lease included"),
    # ---- Sch. 6ZA Part 2 ----
    31: ("RULE", lambda ctx: row(TABLE_F, 0)(ctx) + step2(TABLE_F, "taxf")(ctx) + relief_rules("taxf")(ctx),
         "para. 4 and its row 1 (0%): if relief is claimed, s. 55(1B) is applied as if the substituted table were Table A "
         "(Table B unchanged); a linked transaction's (1C) Step 3 is not written (unit 14)"),
    32: ("RULE", row(TABLE_F, 1), "para. 4 row 2: any remainder so far as not exceeding 500,000 (5%)"),
    33: ("PART", lambda ctx: [], "other:history",
         "para. 5(1): relief claimed for a first transaction, then a later linked transaction: the state after the "
         "later transaction is encoded as its own case state (the later transaction linked), so 'ceases to be a "
         "transaction for which relief may be claimed' is that state's claimable = false; the before/after "
         "comparison is two encoded states, not one formula"),
    34: ("PART", lambda ctx: [], "amount arithmetic",
         "para. 5(2): 'as if the claim had not been made' = taxnr in the later state (written as a deeming); the first "
         "transaction is then linked, so the amount needs s. 55(1C) Step 3 (unit 14): not derived"),
    # ---- Sch. 6ZA Part 3 ----
    35: ("PART", lambda ctx: (
        each_pt(lambda p, u, c2: [
            iff_b("hita", p, u, And(B("purch16", p, u), U("landtxn", u), U("midwelling", u))),
            iff_b("hitb", p, u, And(B("purch16", p, u), Not(U("shortlease", u)), U("dwelling", u), Or(
                And(U("abroad", u), U("equivalent", u)), And(U("wales", u), Or(U("freehold", u), U("lease", u))))))
            , iff_b("hitc", p, u, And(B("afperson", p, u), U("affirst", u), U("midwelling", u))),
            iff_b("hitd", p, u, And(B("wouldbeaf", p, u), Not(U("shortlease", u))))])(ctx)
        + each_pt(lambda p, x, c2: [iff_b("ftb", p, x, And(U("individual", p), *[
            Not(Or(B("hita", p, u), B("hitb", p, u), B("hitc", p, u), B("hitd", p, u)))
            for u in c2.linked_to("earlier", x)]))])(ctx)),
         "cross-reference",
         "para. 6(1): (a) written; (b)(i) 'equivalent interest' a stated judgment, (b)(ii) the s. 117(2) kind by the "
         "test's s. 117 rule; (c) 'the person' for ss. 71A/73 and 'first transaction' given; (d) the counterfactual a "
         "stated judgment. 'previously' = the acquisitions the case lists as earlier (closed world)"),
    36: ("RULE", each(lambda x, ctx: [iff_atom("shortlease", x, And(U("lease", x), Lt(k("years", x), yrs("21"))))]),
         "para. 6(2): ignore a lease (in Wales a term of years absolute) with less than 21 years to run (hitb, hitd)"),
    37: ("PART", lambda ctx: [], "cross-reference",
         "para. 6(3): Sch. 16 para. 3 as if (2) and (3) omitted: written in unit 30's purch16, read by 6(1)(a), (b)"),
    38: ("RULE", lambda ctx: [], "para. 7: the same relevant consideration as s. 55(3)(b)/(4)(b) (units 15, 16)"),
    39: ("RULE", each(lambda x, ctx: [iff_atom("major6", x, Or(U("freehold", x), And(U("lease", x), Not(U("shortlease", x)))))]),
         "para. 8: a term of years with less than 21 years to run is not a major interest for this Schedule"),
    40: ("PART", each(lambda x, ctx: [
        iff_atom("dwelling", x, Or(And(U("usedsingle", x), Not(U("used116", x))),
                                   And(U("suitablesingle", x), Not(U("used116", x))), U("constructing", x))),
        iff_atom("midwelling", x, And(U("major6", x), Or(U("dwelling", x), U("offplan", x))))]),
         "other:judgment standard", "para. 9(2): (a) 'used' a fact, 'suitable for use' a stated judgment; (b) a fact"),
    41: ("RULE", each(lambda x, ctx: [iff_atom("extraok", x, Or(Not(U("extraland", x)), U("extragarden", x),
                                                                 U("extrabenefit", x)))]),
         "para. 9(3): garden or grounds taken to be part of the dwelling (with 9(4) in one rule)"),
    42: ("RULE", lambda ctx: [], "para. 9(4): written in unit 41's rule (extrabenefit)"),
    43: ("PART", each(lambda x, ctx: [iff_atom("offplan", x, And(U("substperf", x), U("tobebuilt", x), U("notbegun", x)))]),
         "cross-reference",
         "para. 9(5): (a) effective date by substantial performance under a relevant deeming provision (ss. 44-45A, Sch. "
         "2A, Sch. 17A) a given fact; (b), (c) facts"),
    44: ("NOT", None, "other:definition carried as fact wording",
         "para. 9(6): 'contract includes any agreement': no formula; carried only by the wording of the fact substperf"),
    45: ("NOT", None, "definition by reference", "para. 9(6): 'substantially performed' has the s. 44 meaning: given"),
    46: ("PART", lambda ctx: [], "cross-reference",
         "para. 9(7): written in unit 40's rule (not used as a dwelling); the s. 116(2)/(3) purpose a given fact"),
    47: ("RULE", lambda ctx: [], "para. 9(8): written in unit 40's rule (suitability not counted when used116)"),
}
CLAIM_RULE = each(lambda x, ctx: [iff_atom("claimable", x, Or(U("elig1", x), U("elig2", x)))])
UNITS[17] = (UNITS[17][0], (lambda b: lambda ctx: b(ctx) + CLAIM_RULE(ctx))(UNITS[17][1]), UNITS[17][2]
             + "; 'relief may be claimed' = under paragraph 1 or 2")


def units_table(mutant=None):
    t = dict(UNITS)
    if mutant is not None:
        t = MUTANTS[mutant][1](t)
    return t


def rules(ctx, mutant=None):
    """Ground rules for a case: [{"id", "unit", "formula", "defines"}]."""
    out = []
    for n, entry in sorted(units_table(mutant).items()):
        if entry[0] not in ("RULE", "PART") or entry[1] is None:
            continue
        for i, f in enumerate(entry[1](ctx)):
            f = simplify(f)
            if f == TRUE:
                continue
            if f == FALSE:
                raise ValueError(f"unit {n}: a ground rule simplifies to false")
            for j, part in enumerate(conjuncts(f)):
                out.append({"id": f"u{n}.{i}.{j}", "unit": n, "formula": part, "defines": defines(part)})
    return out


def simplify(f):
    """Remove the empty-conjunction / empty-disjunction markers grounding leaves (TRUE / FALSE never reach a rule)."""
    if type(f) is not list or not f:
        return f
    if f[0] in ("and", "or"):
        a, b = simplify(f[1]), simplify(f[2])
        unit, zero = (TRUE, FALSE) if f[0] == "and" else (FALSE, TRUE)
        if a == unit:
            return b
        if b == unit:
            return a
        if a == zero or b == zero:
            return zero
        return [f[0], a, b]
    if f[0] == "not":
        a = simplify(f[1])
        return FALSE if a == TRUE else TRUE if a == FALSE else ["not", a]
    if f[0] == "implies":
        a, b = simplify(f[1]), simplify(f[2])
        if a == TRUE:
            return b
        if a == FALSE or b == TRUE:
            return TRUE
        if b == FALSE:
            return ["not", a] if a[0] != "not" else a[1]
        return ["implies", a, b]
    return f


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
        if lhs == ["true"] or (lhs[0] == "not" and lhs[1] == ["true"]):
            return []
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
    for x in ctx.txns:
        consts[x] = {"sort": "txn", "description": f"The case's transaction {x}.", "verbalisation": f"transaction {x}"}
        for base, (u, w) in INT_UNITS.items():
            consts[f"{base}_{x}"] = {"sort": "$int", "unit": u, "description": f"{w[0].upper() + w[1:]} ({x}).",
                                     "verbalisation": f"{w} ({x})"}
    for p in ctx.persons:
        consts[p] = {"sort": "person", "description": f"The case's person {p}.", "verbalisation": f"person {p}"}
    preds = {n: {"arguments": ["txn"], "description": d[0].upper() + d[1:] + "."} for n, d in {**FACTS, **DERIVED}.items()}
    preds.update({n: {"arguments": ["person"], "description": d[0].upper() + d[1:] + "."} for n, d in PFACTS.items()})
    preds.update({n: {"arguments": ["person", "txn"], "description": d[0].upper() + d[1:] + "."}
                  for n, d in {**PTFACTS, **PDERIVED}.items()})
    preds.update({n: {"arguments": ["txn", "txn"], "description": d[0].upper() + d[1:] + "."}
                  for n, d in TTFACTS.items()})
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"txn": {"description": "A land transaction or earlier acquisition the case names."},
                                     "person": {"description": "A person the case names."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {YEARS: {"scale": "1", "display": {"kind": "decimal", "label": "years"}},
                      GBP: {"scale": "100", "display": {"kind": "money", "currency": "GBP", "input_symbol": "£"}}}}


# --- planted errors (run.py --mutants): one per stress the law carries; each must change a named answer -------------

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


def _drop_garden(t):
    """Deeming dropped: para. 9(3) garden or grounds no longer taken to be part of the dwelling."""
    t = dict(t)
    t[41] = ("RULE", each(lambda x, ctx: [iff_atom("extraok", x, Or(Not(U("extraland", x)), U("extrabenefit", x)))]),
             "M2")
    return t


def _no_substitute(t):
    """Deeming dropped: para. 4's substituted table ignored (relief computed on the ordinary Table A)."""
    t = dict(t)
    e = t[31]
    t[31] = (e[0], lambda ctx: row(TABLE_F, 0)(ctx) + step2(TABLE_F, "taxf")(ctx) + relief_rules("taxa")(ctx), *e[2:])
    return t


def _step2_drop_row(t):
    """Arithmetic step changed: Step 2 of Table A adds rows 1-4 only (the 12% remainder dropped)."""
    t = dict(t)
    e = t[4]
    t[4] = (e[0], lambda ctx: [Eq(k("taxa", x), Sum([k(r[1], x) for r in TABLE_A[:4]])) for x in ctx.txns]
            + step2(TABLE_B, "taxb")(ctx) + [f for f in e[1](ctx) if f[0] != "eq"], *e[2:])
    return t


MUTANTS = {
    "M1": ("Table A row 3: rate 5% read as 4% (a table row value)", None),
    "M2": ("Sch. 6ZA para. 9(3) deeming dropped: a garden is not taken to be part of the dwelling", _drop_garden),
    "M3": ("s. 55(1B) Step 2 changed: Table A's remainder row (12%) left out of the sum", _step2_drop_row),
    "M4": ("Sch. 6ZA para. 4 deeming dropped: relief computed on the ordinary Table A", _no_substitute),
    "M5": ("Sch. 6ZA para. 8 / 6(2): 21 years read as 20", None),
    "M6": ("Table B row 2: threshold 250,000 read as 200,000 (a table row value)", None),
}


def _rate_mutant(t):
    t = dict(t)
    e = t[7]
    t[7] = (e[0], lambda ctx: [json.loads(json.dumps(f).replace('"scale", "gbp_penny", "5"', '"scale", "gbp_penny", "4"'))
                               for f in e[1](ctx)], *e[2:])
    return t


def _years_mutant(t):
    t = dict(t)
    e = t[36]
    t[36] = (e[0], _wrap(_walk_replace(yrs("21"), yrs("20")))(e[1]), *e[2:])
    return t


def _tableb_mutant(t):
    t = dict(t)
    e = t[11]
    t[11] = (e[0], _wrap(_walk_replace(gbp("250000.00"), gbp("200000.00")))(e[1]), *e[2:])
    e = t[12]
    t[12] = (e[0], _wrap(_walk_replace(gbp("250000.00"), gbp("200000.00")))(e[1]), *e[2:])
    return t


MUTANTS["M1"] = (MUTANTS["M1"][0], _rate_mutant)
MUTANTS["M5"] = (MUTANTS["M5"][0], _years_mutant)
MUTANTS["M6"] = (MUTANTS["M6"][0], _tableb_mutant)


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
