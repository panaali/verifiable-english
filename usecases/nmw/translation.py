"""National Minimum Wage Regulations 2015 regs 4-16 (statute corpus batch 2, law 2): the VE translation, one pass with
today's language. SAME-FAMILY.

Row statute-corpus-nmw (dri-statute-corpus-nmw-1123, Opus 5.5). Written from the pinned source only (manage-agents
reviews/spare/statute-corpus/batch2/nmw/source.txt, sha256 dbe22e58...e1469a4) BEFORE the encoder's question file was
opened for question text. Evidence branch: nothing here is a Lean kernel line, a profile, a refuses pair or a lint change.

UNITS maps each in-scope unit n of batch2/nmw/units.jsonl (tools/sample5.py --units nmw) to
  ("RULE", builder, note)       the unit is written: builder(ctx) gives its ground formulas for one case;
  ("PART", builder, cause, note) written except the part named in the note (bridged / stated / not written);
  ("NOT", None, cause, note)    not written (the ledger row's cause, CAUSES.tsv v2).
Grounding is mechanical (tenant-fees translation conventions): a rule "for every item" is written once per item the case
names; a quantifier over other items is a conjunction / disjunction over the case's items or the items it LINKS by a
stated binary fact (closed world over the case's items). The grounding expands only constructs the language has; it never
emulates one the language lacks (no sum over a set, no product of two quantities, no product across units; ISOLATION.md
D2a, D2b), and never puts a number from a case's facts into a rule.
Vocabulary: sort item (the worker "w" in the pay reference period asked about, each money item the case names: a payment
by the employer, a deduction, a payment by the worker, a provision of living accommodation, and each stated run of days of
accommodation), unary facts and derived predicates on items, per-item integer constants (money in gbp_penny, days in
day, day counts in count, ages in year), case constants (rate, rem = R, the period's days).
"""
from __future__ import annotations

import hashlib
import json

GBP, DAY, CNT, YR = "gbp_penny", "day", "count", "year"
OFFSET_PER_DAY = "11.10"          # reg. 16(1)
MAX_DAYS = 31                     # reg. 6: a pay reference period is a month or a shorter period
RATES = {"nlw": "12.71", "b": "10.85", "c": "8.00", "d": "8.00"}   # regs. 4, 4A(1)(b), (c), (d)

INT_UNITS = {  # per-item integer constants: base name -> (unit, words)
    "amt": (GBP, "the amount of the item (a payment, deduction or worker payment; for living accommodation the amount "
                 "of the deduction the employer is entitled to make or the payment it is entitled to receive)"),
    "contrib": (GBP, "the item's contribution to the remuneration R (a payment counted: its amount; a reduction: minus "
                     "its amount; otherwise 0)"),
    "offset": (GBP, "the amount as respects the provision of living accommodation (reg. 16(1))"),
    "wdays": (CNT, "the number of days in the pay reference period for which the accommodation was provided (reg. 16)"),
    "ndays": (CNT, "the number of days in the stated run of days"),
    "paid": (DAY, "the day the payment was paid, the deduction made or the worker payment paid or due"),
    "recday": (DAY, "the day the worker gave the completed record of work to the employer"),
}
CASE_INTS = {
    "rate": (GBP, "the hourly rate of the national minimum wage that applies to the worker in the pay reference period"),
    "rem": (GBP, "the remuneration in the pay reference period (R)"),
    "age": (YR, "the worker's age in whole years on the first day of the pay reference period (bridge script)"),
    "first": (DAY, "the first day of the pay reference period"),
    "last": (DAY, "the last day of the pay reference period"),
    "nfirst": (DAY, "the first day of the following pay reference period"),
    "nlast": (DAY, "the last day of the following pay reference period"),
    "termday": (DAY, "the day on which the worker's contract terminated"),
    "monthend": (DAY, "the last day of the period of a month beginning with the day after termination (stated)"),
    "fourthwd": (DAY, "the fourth working day before the end of the following pay reference period (stated)"),
}

FACTS = {  # unary facts on an item (the encoder states each true or false)
    # the worker (item w)
    "worker": "is the worker in the pay reference period asked about",
    "nlw": "the worker qualifies for the national living wage rate (Act s. 1(3), stated)",
    "contract_appr": "the worker is employed under a contract of apprenticeship, an apprenticeship agreement (ASCLA "
                     "2009 s. 32) or an approved English apprenticeship agreement (ASCLA 2009 s. A1(3))",
    "eng_england": "the worker is engaged in England under arrangements",
    "eng_scotland": "the worker is engaged in Scotland under arrangements",
    "eng_ni": "the worker is engaged in Northern Ireland under arrangements",
    "eng_wales": "the worker is engaged in Wales under arrangements",
    "known_england": "the arrangements are known as Apprenticeships, Advanced Apprenticeships, Intermediate Level "
                     "Apprenticeships or Advanced Level Apprenticeships",
    "known_scotland": "the arrangements are known as Modern Apprenticeships",
    "known_ni": "the arrangements are known as Apprenticeships NI",
    "known_wales": "the arrangements are known as Foundation Apprenticeships, Apprenticeships or Higher Apprenticeships",
    "made_eng": "the arrangements are made by the Secretary of State under ETA 1973 s. 2 or JSA 1995 s. 17B",
    "made_wal": "the arrangements are made by the Secretary of State or the Welsh Ministers under ETA 1973 s. 2 or by the "
                "Secretary of State under JSA 1995 s. 17B",
    "made_sco": "the arrangements are made by the Secretary of State or the Scottish Ministers under ETA 1973 s. 2 or by "
                "Scottish Enterprise or Highlands and Islands Enterprise under ENTSA 1990 s. 2",
    "made_ni": "the arrangements are made by the Department for Employment and Learning under ETA (NI) 1950 s. 1",
    "tb_agreement": "an agreement between the employer and the worker provides for the worker to work for the employer "
                    "and for the employer or another person to provide training to assist the worker to achieve a "
                    "standard in the work done under the agreement",
    "tb_standard": "that standard is the one published by the Secretary of State in connection with the Government "
                   "arrangements known as Trailblazer Apprenticeships which applies to the work",
    "within12_cur": "the first day of the period is within the first 12 months after the worker commenced employment "
                    "with this employer (bridge script)",
    "within12_prior": "the first day of the period is within the first 12 months after the worker commenced the earlier "
                      "employment with another employer (bridge script)",
    "prior_continuity": "the worker was previously employed by another employer and continuity of employment is preserved "
                        "between the two employments by or under an enactment",
    "terminated": "the worker's contract terminated",
    # money items
    "emp_payment": "is a payment by the employer to the worker",
    "deduction": "is a deduction made by the employer from the worker's wages",
    "wpay_emp": "is a payment paid by or due from the worker to the employer",
    "wpay_other": "is a payment by the worker to a person other than the employer",
    "as_prp": "is as respects the pay reference period asked about",
    "as_prev": "is as respects the pay reference period immediately before the one asked about",
    "as_older": "is as respects a pay reference period earlier than the one immediately before",
    "rec_obligation": "the worker is under an obligation to complete a record of the amount of work done (for the work "
                      "the payment is as respects)",
    "rec_condition": "the worker is not entitled to payment until the completed record has been given to the employer",
    "rec_given": "the worker gave the completed record to the employer (on recday)",
    "rec_paid_window": "the payment is paid in the pay reference period in which the record is given or the period after",
    "x_loan_advance": "is by way of an advance under an agreement for a loan or an advance of wages",
    "x_retirement": "is a pension, allowance or gratuity in connection with retirement or compensation for loss of office",
    "x_court": "is an award of a court or tribunal or a payment to settle proceedings",
    "due_contract": "is the payment of an amount due under the worker's contract",
    "x_redundancy": "is referable to the worker's redundancy",
    "x_suggestion": "is an award for a suggestion under a scheme established by the employer to reward suggestions",
    "benefit_kind": "is a benefit in kind provided to the worker (other than living accommodation)",
    "x_voucher": "is a voucher, stamp or similar document capable of being exchanged for money, goods or services",
    "x_hours_not_work": "is as respects hours which are not, or not treated as, hours of time work (reg. 35), hours of "
                        "output work (reg. 40) or hours of unmeasured work (reg. 48) (stated)",
    "x_salaried_reduced": "in the context of salaried hours work, is attributable to hours to be reduced under reg. 23 "
                          "(directly or by reason of reg. 28(3)) (stated)",
    "premium_excess": "is the part of a payment as respects hours of time work or output work that exceeds the lowest "
                      "rate per hour which could be payable under the contract for that work (stated as its own amount)",
    "part_excluded": "is excluded by reg. 10 only in part (reg. 10(i) or (j)) and the part that counts is not stated as "
                     "its own amount (it would need a subtraction or hours x rates)",
    "arrangement_pay": "is attributable to a particular aspect of the working arrangements or to working or personal "
                       "circumstances",
    "consolidated": "is consolidated into the worker's standard pay",
    "performance": "is attributable to the performance of the worker in carrying out the work",
    "expenditure": "is as respects the worker's expenditure in connection with the employment",
    "x_tips": "represents amounts paid by customers by way of a service charge, tip, gratuity or cover charge",
    "x_travel338": "is as respects travelling expenses allowed as deductions from earnings under ITEPA 2003 s. 338",
    "x_salary_premium": "is a payment of a salary premium",
    "own_use": "is for the employer's own use and benefit",
    "conduct_liable": "is in respect of the worker's conduct or another event for which the worker is contractually "
                      "liable",
    "loan_repay": "is on account of an advance under an agreement for a loan or an advance of wages",
    "overpayment": "is as respects an accidental overpayment of wages made by the employer to the worker",
    "shares": "is as respects the purchase by the worker of shares, other securities, share options or a partnership share",
    "purchase_emp": "is as respects the purchase by the worker of goods or services from the employer",
    "purchase_required": "the purchase is made to comply with a requirement imposed by the employer in connection with "
                         "the worker's employment",
    "met_by_emp": "is met, or intended to be met, by a payment paid to the worker by the employer",
    "accommodation": "is the provision of living accommodation by the employer to the worker in the pay reference period",
    "acc_entitled": "the employer is entitled to make a deduction from the worker's wages or to receive a payment from the "
                    "worker as respects that provision",
    "payee_hei": "the deduction or payment is to or by a higher education institution (FHEA 1992 s. 91(5)), a further "
                 "education institution (s. 91(3)) or a 16 to 19 Academy",
    "enrolled_there": "the worker is enrolled on a full-time higher or further education course at that institution or a "
                      "full-time course provided by that Academy",
    "payee_lha": "the deduction or payment is to or by a local housing authority or a registered social landlord "
                 "(reg. 14(3))",
    "employed_by_payee": "the accommodation is provided in connection with the worker's employment with that authority "
                         "or landlord",
    "absent": "the worker is absent from work in the pay reference period",
    "c15a": "the worker would be required to do time work but for the absence",
    "c15b": "the worker is paid, for the absent hours, not less than the worker would have been entitled to under these "
            "Regulations but for the absence (stated)",
    "c15c": "the hours of work in the period are, by reason of the absence, less than in a period with the same number of "
            "working days worked without reduced hours and no additional hours",
    "c15d": "the accommodation deduction or payment does not increase by reason of the absence",
    "acc_run": "is a stated run of days of living accommodation",
    "whole": "the accommodation was provided for the whole of each day of the run",
}
STATED = ("nlw", "x_hours_not_work", "x_salaried_reduced", "c15b", "within12_cur", "within12_prior")
DERIVED = {
    "gov_eng": "the arrangements are Government arrangements in England (reg. 5(4)(a)(i))",
    "gov_wal": "the arrangements are Government arrangements in Wales (reg. 5(4)(a)(ii))",
    "gov_sco": "the arrangements are Government arrangements in Scotland (reg. 5(4)(a)(iii))",
    "gov_ni": "the arrangements are Government arrangements in Northern Ireland (reg. 5(4)(a)(iv))",
    "trailblazer": "the worker is engaged under a Trailblazer Apprenticeship (reg. 5(4)(b), (c))",
    "treated_appr": "the worker is treated as employed under a contract of apprenticeship (reg. 5(2))",
    "within12": "the first day of the period is within the first 12 months after the commencement of the employment "
                "(reg. 5(1)(b) with 5(3))",
    "appr": "the apprenticeship rate applies to the worker (reg. 5(1))",
    "band_b": "the worker is aged 18 or over but not yet 21 (reg. 4A(1)(b))",
    "band_c": "the worker is aged under 18 (reg. 4A(1)(c))",
    "under19": "the worker is under 19 years of age",
    "in_prp": "the item is paid (made, due) in the pay reference period",
    "in_next": "the item is paid in the following pay reference period",
    "later_next": "the item is paid later than the following pay reference period",
    "final_prp": "the pay reference period is the worker's final pay reference period",
    "in_month_after": "the item is paid in the period of a month beginning with the day after termination",
    "rec_late": "the worker failed to give the record before the fourth working day before the end of the following "
                "period (reg. 9(2)(c))",
    "req92": "the requirements of reg. 9(2) are met",
    "earlier_req": "the payment is required to be included in an earlier pay reference period (reg. 9(1)(b) or (c))",
    "p9": "the payment is treated as a payment by the employer to the worker as respects the period (reg. 9(1)(a)-(d))",
    "excl10": "the payment does not form part of the worker's remuneration (reg. 10)",
    "counted_pay": "the payment counts as a payment by the employer as respects the period",
    "exc12": "the deduction or payment is not treated as a reduction (reg. 12(2))",
    "r12": "treated as a reduction under reg. 12(1)",
    "r13": "treated as a reduction under reg. 13(1)",
    "exc14": "the payment or deduction falls within reg. 14(2)",
    "reg15": "the accommodation amount is to be adjusted under reg. 15 (all of reg. 15(1)(a)-(d) and an absence)",
    "r14": "treated as a reduction under reg. 14(1) (it exceeds the reg. 16 amount)",
    "free_acc": "reg. 9(1)(e) applies to the provision (accommodation provided, no deduction or payment entitled)",
    "reduction": "the item is treated as a reduction (reg. 11; subtracted once, reg. 11(2))",
    "contributes": "the item contributes to R (a counted payment, a reg. 9(1)(e) amount above 0, or a reduction)",
    "counts16": "the run's days count as days for which accommodation was provided (reg. 16(2))",
}
BINARY = {"run_of": "the first item is a stated run of days of the second item (a provision of living accommodation)"}


# --- formula helpers (the ve-quantity@1 wire shapes; tenant-fees translation conventions) -----------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def B(p, x, y): return ["binary", p, c(x), c(y)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def gbp(v): return ["decimal", GBP, v]
def cnt(v): return ["decimal", CNT, str(v)]
def yrs(v): return ["decimal", YR, str(v)]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def add(tag, a, b): return ["add", tag, a, b]
def scale(tag, k, t): return ["scale", tag, str(k), t]
def minus(a, b): return add(GBP, a, scale(GBP, -1, b))
def dle(a, b): return ["date_no_later", a, b]   # a is no later than b
def dlt(a, b): return ["date_before", a, b]     # a is before b
TRUE = ["not", ["not", ["true"]]]
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


def k(base, x):
    """Per-item integer constant."""
    return ["const", INT_UNITS[base][0], f"{base}_{x}"]


def kc(name):
    return ["const", CASE_INTS[name][0], name]


def iff_atom(p, x, body):
    return Iff(U(p, x), body)


# --- the case context ---------------------------------------------------------------------------------------

class Ctx:
    def __init__(self, items, links=()):
        self.items = list(items)
        self.links = {(p, a, b) for (p, a, b) in links}

    def linked_to(self, pred, x):
        """Items y with the stated binary fact pred(y, x)."""
        return [a for (p, a, b) in sorted(self.links) if p == pred and b == x]

    @property
    def money(self):
        return [x for x in self.items if x != "w" and not x.startswith("run")]

    @property
    def runs(self):
        return [x for x in self.items if x.startswith("run")]


def each(fn, which="money"):
    def build(ctx):
        xs = {"money": ctx.money, "all": ctx.items, "w": ["w"], "runs": ctx.runs}[which]
        return [f for x in xs for f in fn(x, ctx)]
    return build


def _rate_rules(ctx):
    w = "w"
    out = [
        Implies(U("appr", w), Eq(kc("rate"), gbp(RATES["d"]))),
        Implies(And(Not(U("appr", w)), U("nlw", w)), Eq(kc("rate"), gbp(RATES["nlw"]))),
        Implies(And(Not(U("appr", w)), U("band_b", w)), Eq(kc("rate"), gbp(RATES["b"]))),
        Implies(And(Not(U("appr", w)), U("band_c", w)), Eq(kc("rate"), gbp(RATES["c"]))),
    ]
    return out


def _offset_rules(x, ctx):
    """reg. 16(1): days x 11.10, as a case split the rule enumerates over n = 0 .. 31 (Lean multiplies)."""
    return [Implies(Eq(k("wdays", x), cnt(n)), Eq(k("offset", x), scale(GBP, n, gbp(OFFSET_PER_DAY))))
            for n in range(MAX_DAYS + 1)]


def _wdays_rules(x, ctx):
    """reg. 16(1)-(2): the day count is the stated count of the ONE run whose days count (no sum over runs: D2a)."""
    runs = ctx.linked_to("run_of", x)
    out = []
    for r in runs:
        others = [Not(U("counts16", s)) for s in runs if s != r]
        out.append(Implies(And(U("counts16", r), *others), Eq(k("wdays", x), k("ndays", r))))
    out.append(Implies(And(*[Not(U("counts16", r)) for r in runs]), Eq(k("wdays", x), cnt(0))))
    return out


def _rem_rules(ctx):
    """reg. 8 restricted to the configurations that need no addition (D2b): one contributing item, or none. A payment
    excluded only in part (part_excluded) blocks both: its counted part is not written (amount arithmetic)."""
    xs = ctx.money
    whole = [Not(U("part_excluded", y)) for y in xs]
    out = []
    for x in xs:
        out.append(Implies(And(U("contributes", x), *[Not(U("contributes", y)) for y in xs if y != x], *whole),
                           Eq(kc("rem"), k("contrib", x))))
    out.append(Implies(And(*[Not(U("contributes", y)) for y in xs], *whole), Eq(kc("rem"), gbp("0.00"))))
    return out


def _contrib_rules(x, ctx):
    pay = And(U("counted_pay", x), Not(U("accommodation", x)))
    red1213 = And(Or(U("r12", x), U("r13", x)), Not(U("accommodation", x)))
    return [
        iff_atom("contributes", x, Or(pay, And(U("free_acc", x), Lt(gbp("0.00"), k("offset", x))), red1213, U("r14", x))),
        Implies(pay, Eq(k("contrib", x), k("amt", x))),
        Implies(U("free_acc", x), Eq(k("contrib", x), k("offset", x))),
        Implies(red1213, Eq(k("contrib", x), scale(GBP, -1, k("amt", x)))),
        Implies(U("r14", x), Eq(k("contrib", x), minus(k("offset", x), k("amt", x)))),
    ]


UNITS = {
    # ---- Part 2: rates ----
    1: ("PART", lambda ctx: [_rate_rules(ctx)[1]], "cross-reference",
        "reg. 4: the national living wage rate £12.71 for a worker who qualifies 'for the purposes of section 1(3) of the "
        "Act' (not pinned: a stated fact, cross-reference)"),
    2: ("PART", lambda ctx: _rate_rules(ctx)[2:] + [
        iff_atom("band_b", "w", And(Le(yrs(18), kc("age")), Lt(kc("age"), yrs(21)))),
        iff_atom("band_c", "w", Lt(kc("age"), yrs(18)))],
        "date/age arithmetic",
        "reg. 4A(1)(b)-(d): the bands are written as comparisons of the age with 18 and 21; the age on the first day of "
        "the period is the bridge script's (bridged)"),
    3: ("RULE", lambda ctx: [_rate_rules(ctx)[0]],
        "reg. 4A(2): every other rate's rule is guarded by 'not appr' (and appr fixes £8.00)"),
    4: ("PART", lambda ctx: [], "date/age arithmetic",
        "reg. 4B: the rate on the first day of the period: the bridge computes the age and the 12-month test on that "
        "day (bridged); the rate rules read those facts"),
    5: ("PART", lambda ctx: [
        iff_atom("appr", "w", And(Or(U("contract_appr", "w"), U("treated_appr", "w")),
                                 Or(U("within12", "w"), U("under19", "w")))),
        iff_atom("under19", "w", Lt(kc("age"), yrs(19)))],
        "date/age arithmetic",
        "reg. 5(1): (a) 'within the meaning of' ASCLA 2009 s. 32 / s. A1(3) a stated fact (secondary definition by "
        "reference); (b) 'within the first 12 months' and the age are the bridge's (bridged)"),
    6: ("RULE", lambda ctx: [iff_atom("treated_appr", "w", Or(
        And(U("eng_england", "w"), Or(And(U("gov_eng", "w"), U("known_england", "w")), U("trailblazer", "w"))),
        And(U("eng_scotland", "w"), U("gov_sco", "w"), U("known_scotland", "w")),
        And(U("eng_ni", "w"), U("gov_ni", "w"), U("known_ni", "w")),
        And(U("eng_wales", "w"), U("gov_wal", "w"), U("known_wales", "w"))))],
        "reg. 5(2)(a)-(d): engaged in the nation under Government arrangements known by a listed name (or, in England, "
        "under a Trailblazer Apprenticeship)"),
    7: ("PART", lambda ctx: [iff_atom("within12", "w", Or(
        And(Not(U("prior_continuity", "w")), U("within12_cur", "w")),
        And(U("prior_continuity", "w"), U("within12_prior", "w"))))],
        "cross-reference",
        "reg. 5(3): no commencement with the new employer where continuity is preserved 'by or under any enactment' (a "
        "stated fact; cross-reference); the 12 months then run from the earlier commencement (bridged)"),
    8: ("PART", lambda ctx: [
        iff_atom("gov_eng", "w", U("made_eng", "w")), iff_atom("gov_wal", "w", U("made_wal", "w")),
        iff_atom("gov_sco", "w", U("made_sco", "w")), iff_atom("gov_ni", "w", U("made_ni", "w")),
        iff_atom("trailblazer", "w", And(U("tb_agreement", "w"), U("tb_standard", "w")))],
        "definition by reference",
        "reg. 5(4): (a) arrangements 'under section 2 of the Employment and Training Act 1973' etc. are stated facts "
        "(definition by reference); (b), (c) written as a conjunction of stated facts"),
    9: ("NOT", None, "date/age arithmetic",
        "reg. 6: a month, or the shorter period by reference to which wages are paid: the period's first and last day "
        "(and the following period's) are stated by the question or read from the calendar by the encoder; no rule "
        "derives them"),
    # ---- Part 3 ----
    10: ("NOT", None, "amount arithmetic",
         "reg. 7: R / H against the rate needs a money rate times an hours quantity: the language's scale takes an "
         "integer and keeps its unit (UnitMismatch measured, ISOLATION.md D2b); every Q3 unsupported"),
    11: ("RULE", lambda ctx: [], "reg. 7 'R': the constant rem, fixed by Part 4 (units 13-37)"),
    12: ("NOT", None, "cross-reference",
         "reg. 7 'H': the hours of work by Part 5 (out of scope): a given fact, used only by reg. 7 (unit 10)"),
    # ---- Part 4 ----
    13: ("PART", lambda ctx: _rem_rules(ctx), "amount arithmetic",
         "reg. 8: payments less reductions is a sum over the case's items (SUM): written only where one item "
         "contributes, or none (D2b); two or more contributors -> no R (unsupported, SUM)"),
    14: ("PART", lambda ctx: each(lambda x, ctx: [
        iff_atom("in_prp", x, And(dle(kc("first"), k("paid", x)), dle(k("paid", x), kc("last")))),
        iff_atom("in_next", x, And(dle(kc("nfirst"), k("paid", x)), dle(k("paid", x), kc("nlast")))),
        iff_atom("later_next", x, dlt(kc("nlast"), k("paid", x))),
        iff_atom("in_month_after", x, And(dlt(kc("termday"), k("paid", x)), dle(k("paid", x), kc("monthend")))),
        iff_atom("earlier_req", x, And(U("in_prp", x), Or(U("as_prev", x), And(U("as_older", x), U("req92", x))))),
        iff_atom("p9", x, And(U("emp_payment", x), Or(
            And(U("in_prp", x), Not(U("earlier_req", x))),
            And(U("in_next", x), U("as_prp", x)),
            And(U("later_next", x), U("as_prp", x), U("req92", x)),
            And(U("final_prp", "w"), U("in_month_after", x))))),
        iff_atom("free_acc", x, And(U("accommodation", x), Not(U("acc_entitled", x))))])(ctx) + [
        iff_atom("final_prp", "w", And(U("terminated", "w"), dle(kc("first"), kc("termday")),
                                       dle(kc("termday"), kc("last"))))],
         "deadline/time limit",
         "reg. 9(1)(a)-(e): (a)-(c) as date comparisons with the period's stated bounds; (b)/(c)'s exception in (a) for "
         "a payment as respects an earlier period; (d) 'the period of a month beginning with the day after' termination: "
         "its last day is a stated fact (deadline/time limit), the comparisons are written; (e) the reg. 16 amount "
         "where no deduction or payment is entitled (unit 35)"),
    15: ("PART", each(lambda x, ctx: [
        iff_atom("rec_late", x, Or(Not(U("rec_given", x)), dle(kc("fourthwd"), k("recday", x)))),
        iff_atom("req92", x, And(U("rec_obligation", x), U("rec_condition", x), U("rec_late", x),
                                 U("rec_paid_window", x)))]),
         "deadline/time limit",
         "reg. 9(2): (c) 'before the fourth working day before the end' of the following period: that day is a stated "
         "fact (working day, reg. 2, not pinned); 'failed to give before' = given on or after it, or not given; (d) the "
         "period in which the record is given (calendar membership) a stated fact"),
    16: ("PART", each(lambda x, ctx: [
        iff_atom("excl10", x, Or(
            U("x_loan_advance", x), U("x_retirement", x), And(U("x_court", x), Not(U("due_contract", x))),
            U("x_redundancy", x), U("x_suggestion", x), U("benefit_kind", x), U("x_voucher", x),
            U("x_hours_not_work", x), U("x_salaried_reduced", x), U("premium_excess", x),
            And(U("arrangement_pay", x), Not(U("consolidated", x)), Not(U("performance", x))),
            U("expenditure", x), U("x_tips", x), U("x_travel338", x), U("x_salary_premium", x))),
        iff_atom("counted_pay", x, And(U("p9", x), Not(U("excl10", x)), Not(U("part_excluded", x))))]),
         "cross-reference",
         "reg. 10(a)-(o): each limb a stated purpose; (h), (i) refer to regs. 23, 28(3), 35, 40, 48 (Part 5) and (n) to "
         "ITEPA s. 338: stated facts (cross-reference); (o) 'salary premium' a given name (reg. 2, definition by "
         "reference); (j) 'to the extent that' the excess over the lowest rate: written only where the excess is stated "
         "as its own amount; an excess of hours x rates is a product (amount arithmetic, secondary): no counted amount"),
    17: ("PART", lambda ctx: [], "amount arithmetic",
         "reg. 11(1): 'adding together all' reductions is a sum over a set (SUM): not written beyond one item (unit 13)"),
    18: ("RULE", each(lambda x, ctx: [iff_atom("reduction", x, Or(U("r12", x), U("r13", x), U("r14", x)))]),
         "reg. 11(2): one reduction per item however many provisions catch it (one contribution, unit 13's rules)"),
    19: ("RULE", each(lambda x, ctx: [iff_atom("r12", x, And(
        Or(U("deduction", x), U("wpay_emp", x)), U("in_prp", x), U("own_use", x), Not(U("exc12", x)),
        Not(U("accommodation", x))))]),
         "reg. 12(1): 'for the employer's own use and benefit' a stated fact; reg. 14 items are the accommodation items"),
    20: ("RULE", each(lambda x, ctx: [iff_atom("exc12", x, Or(
        U("conduct_liable", x), U("loan_repay", x), U("overpayment", x), U("shares", x),
        And(U("wpay_emp", x), U("purchase_emp", x),
            Not(And(U("purchase_required", x), Not(U("met_by_emp", x)))))))]),
         "reg. 12(2)(a)-(e); (e) names 'payments' only (a deduction for a purchase is not within (e))"),
    21: ("RULE", lambda ctx: [], "reg. 13 (the heading repeated in the text): carried by units 22-23"),
    22: ("RULE", each(lambda x, ctx: [iff_atom("r13", x, And(U("in_prp", x), U("expenditure", x), Or(
        U("deduction", x), And(Or(U("wpay_emp", x), U("wpay_other", x)), Not(U("met_by_emp", x))))))]),
         "reg. 13(1)(a), (b) with (2) (the exception for (b) payments met by the employer) in one rule"),
    23: ("RULE", lambda ctx: [], "reg. 13(2): written in unit 22's rule"),
    24: ("RULE", each(lambda x, ctx: [iff_atom("r14", x, And(
        U("accommodation", x), U("acc_entitled", x), Not(U("exc14", x)), Not(U("reg15", x)),
        Lt(k("offset", x), k("amt", x))))]),
         "reg. 14(1): the entitled amount is a reduction to the extent it exceeds the reg. 16 amount; where reg. 15 "
         "adjusts it, no rule fires (the adjustment is a product, unit 31)"),
    25: ("RULE", each(lambda x, ctx: [iff_atom("exc14", x, Or(
        And(U("payee_hei", x), U("enrolled_there", x)),
        And(U("payee_lha", x), Not(U("employed_by_payee", x)))))]),
         "reg. 14(2)(a), (b); the institution kinds are stated facts in reg. 14(3)'s words (units 26-29)"),
    26: ("NOT", None, "definition by reference",
         "reg. 14(3) 'further education institution' = FHEA 1992 s. 91(3): a stated fact (payee_hei)"),
    27: ("NOT", None, "definition by reference",
         "reg. 14(3) 'higher education institution' = FHEA 1992 s. 91(5): a stated fact (payee_hei)"),
    28: ("NOT", None, "definition by reference",
         "reg. 14(3) 'local housing authority' = Housing Act 1985 Part 1 etc.: a stated fact (payee_lha)"),
    29: ("NOT", None, "definition by reference",
         "reg. 14(3) 'registered social landlord' = HRA 2008 Part 2, HA 1996 Part 1 etc.: a stated fact (payee_lha)"),
    30: ("PART", each(lambda x, ctx: [iff_atom("reg15", x, And(
        U("accommodation", x), U("acc_entitled", x), U("absent", "w"), U("c15a", x), U("c15b", x), U("c15c", x),
        U("c15d", x)))]), "amount arithmetic",
         "reg. 15(1)(a)-(d): conditions as facts; (b) 'an amount not less than' the entitlement under the Regulations is "
         "an amount comparison (pay x hours) carried only as a stated fact (stated)"),
    31: ("NOT", None, "amount arithmetic",
         "reg. 15(2): (A x B) / C, a product and a quotient of stated quantities (PROD): not written; the item's "
         "contribution stays open (Q2 unsupported, PROD)"),
    32: ("RULE", lambda ctx: [], "reg. 15(2) 'A': the entitled amount amt of the accommodation item (reg. 14)"),
    33: ("NOT", None, "cross-reference", "reg. 15(2) 'B': hours of time work by Part 5 (out of scope)"),
    34: ("NOT", None, "amount arithmetic", "reg. 15(2) 'C': used only in the formula (unit 31)"),
    35: ("RULE", lambda ctx: [f for x in ctx.money if x.startswith("acc") for f in _offset_rules(x, ctx) + _wdays_rules(x, ctx)],
         "reg. 16(1): days x £11.10 by a case split over the day count 0-31 (Lean multiplies the text's literal by the "
         "branch's integer); the day count is the stated count of the one run that counts (a sum over runs is not "
         "written, D2a)"),
    36: ("RULE", each(lambda x, ctx: [iff_atom("counts16", x, And(U("acc_run", x), U("whole", x)))], "runs"),
         "reg. 16(2): a day counts only if provided for the whole of it (the run's fact 'whole')"),
    37: ("RULE", lambda ctx: [], "reg. 16(3): the regulations in force on the first day: every period asked about "
                                 "begins 1 April - 1 October 2026 with the file's text in force (fixed fact)"),
}
# contributions (units 13, 18, 24, 35 together): one item's contribution to R
UNITS[18] = ("RULE", lambda ctx: [f for x in ctx.money for f in (
    [iff_atom("reduction", x, Or(U("r12", x), U("r13", x), U("r14", x)))] + _contrib_rules(x, ctx))],
    UNITS[18][2])


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
            for j, part in enumerate(conjuncts(f)):
                out.append({"id": f"u{n}.{i}.{j}", "unit": n, "formula": part, "defines": defines(part)})
    return out


# --- structure helpers (tenant-fees translation.py conventions) --------------------------------------------------

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
    raise ValueError(f"no defined target: {f}")


# --- the environment for one case ---------------------------------------------------------------------------------

def environment(ctx):
    consts = {}
    for x in ctx.items:
        consts[x] = {"sort": "item", "description": f"The case's item {x}.", "verbalisation": f"item {x}"}
        for base, (u, w) in INT_UNITS.items():
            consts[f"{base}_{x}"] = {"sort": "$int", "unit": u, "description": f"{w[0].upper() + w[1:]} ({x}).",
                                     "verbalisation": f"{w} ({x})"}
    for name, (u, w) in CASE_INTS.items():
        consts[name] = {"sort": "$int", "unit": u, "description": w[0].upper() + w[1:] + ".", "verbalisation": w}
    preds = {n: {"arguments": ["item"], "description": d[0].upper() + d[1:] + "."}
             for n, d in {**FACTS, **DERIVED}.items()}
    preds.update({n: {"arguments": ["item", "item"], "description": d[0].upper() + d[1:] + "."}
                  for n, d in BINARY.items()})
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "The worker, or a money item or a run of days the case "
                                                             "names."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {"day": {"scale": "1", "display": {"kind": "iso_date"}},
                      GBP: {"scale": "100", "display": {"kind": "money", "currency": "GBP", "input_symbol": "£"}},
                      CNT: {"scale": "1", "display": {"kind": "decimal", "label": "days"}},
                      YR: {"scale": "1", "display": {"kind": "decimal", "label": "years"}}}}


# --- planted errors (run.py --mutants): each must change the answer of a named question ---------------------------

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


def _drop_r12(builder):
    """reg. 12(1)'s deeming line dropped: nothing is treated as a reduction under it."""
    return lambda ctx: [iff_atom("r12", x, FALSE) for x in ctx.money]


def _drop_pred(name):
    def walk(f):
        if type(f) is list and f[:2] == ["unary", name]:
            return FALSE
        if type(f) is list:
            return [walk(x) for x in f]
        return f
    return walk


MUTANTS = {
    "M1": ("reg. 4A(1)(b): £10.85 read as £10.58 (a rate value)",
           _swap(2, _wrap(_walk_replace(gbp("10.85"), gbp("10.58"))))),
    "M2": ("reg. 12(1): the deeming line 'treated as reductions' dropped", _swap(19, _drop_r12)),
    "M3": ("reg. 16(1): £11.10 per day read as £11.00 (an arithmetic step)",
           _swap(35, _wrap(_walk_replace(gbp("11.10"), gbp("11.00"))))),
    "M4": ("reg. 4A(1)(b): 'aged 18 or over' read as 'over 18' (age > 18)",
           _swap(2, _wrap(_walk_replace(Le(yrs(18), kc("age")), Lt(yrs(18), kc("age")))))),
    "M5": ("reg. 10: the exclusion of tips (m) dropped", _swap(16, _wrap(_drop_pred("x_tips")))),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
