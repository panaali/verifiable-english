"""Working Time Regulations 1998 regs 13, 13A, 14, 15 (statute corpus batch 4, text 6, UK leave): the VE translation, one
pass with today's language.

Row statute-corpus-wtr-annual-leave (dri-statute-corpus-wtr-annual-leave-w-1124, Opus 5.5, translator and encoder).
CROSS-FAMILY questions (Codex writer gpt-6-astra, sealed in manage-agents reviews/spare/statute-corpus/batch4/wtr-annual-leave/
ISOLATION.md before any translation). Written from the pinned source (batch4/wtr-annual-leave/source.txt, sha256
b722b8a9...7b5a; units.jsonl 32 units, 0 table rows). The encoder's question file (questions only, never the answers) was
read BEFORE this file was written (as stock/oas-canada did; ISOLATION.md "Translation" records it); every reading below is
fixed on the text's words and ISOLATION.md D1-D13, never on an answer. Evidence branch: nothing here is a Lean kernel line, a
profile, a refuses pair or a lint change; nothing merges.

UNITS maps each in-scope unit n of units.jsonl to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one case;
  ("PART", builder, cause, note) written except the part named in the note (the ledger row's cause, CAUSES.tsv v2);
  ("NOT", None, cause, note)     not written.
Items (one sort "item"): the worker w; leave years y1, y2, ... (consecutive, in order; each with its stated first day);
notices n1, ... (a notice under reg 15(1) or (2)); proposals p1, ... (a day on which carried-forward leave would be taken).

ARITHMETIC. The language has sums and products by a LITERAL only (no product of two quantities). Every day amount (days
worked in a week, entitlements, calendar-day counts, leave taken) is in one unit, leave_day, at 1/100 day. Products of two
case quantities are written as a case split the rule enumerates over literals of the translation: the days worked in a
week n = 1..7 (atoms dw1..dw7) and the days of a year l = 365 / 366 (atoms l365 / l366), the council-tax / child-support
precedent. Calendar-day counts between two dates (the days of a leave year, the days of it remaining on the day employment
begins, the days expired before the termination date, the days of the years beginning 1 October 2007 / 1 April 2009 elapsed
at the end of a leave year) and the dates "the next anniversary", "the anniversary in the year of a leave year's first day"
and "the last day of the 18 months from the end of a leave year" come ONLY from bridge/wtr_bridge.py (dates only, D6;
ledgered "bridged"). The reg 15 relevant date and latest notice day are computed in Lean (elapsed_days / shift_days).
AMOUNTS ARE NEVER BRIDGED: every proportion, product, cap, sum and comparison is here.

READINGS (fixed on the text's words; refuse when in doubt; D1-D13 bind):
R1  WEEKS: one week of leave = the worker's stated days worked in a week (D5(a)); "four weeks" = 4n days, "1.6 weeks" =
    1.6n, "0.8 weeks" = 0.8n; the 28 days of 13A(3) are days on the same basis.
R2  APPLICATION (13(A1), 13A(A1)): a leave year whose first day is before 1 April 2024, or one for which reg 15B does not
    apply (stated fact). 13A(8): not to a worker to whom the Agricultural Wages (Scotland) Act 1949 applies. "Subject to
    regulation 26A" (13A(1)): where 26A applies, no 13A entitlement is derived (none of the cases).
R3  LEAVE YEAR (13(3)): (a) the agreement's date: the leave year begins on the anniversary of the agreement's date in its
    calendar year; (b)(i) employment began on or before 1 October 1998: 1 October 1998 and each anniversary; (b)(ii) after:
    the employment's first day and each anniversary (on or after it). 13(4): 13(3) does not apply to a worker to whom
    Schedule 2 applies, except a worker partly employed in agriculture in Wales or Scotland where a relevant agreement so
    provides. 13A(4): the same leave year (one leave-year item serves both).
R4  FIRST LEAVE YEAR (13(5), 13A(5)): applies when a relevant agreement fixes the leave year, employment begins after the
    leave year's first day and before the next leave year. "The proportion of that leave year remaining on the date on which
    his employment begins" = the calendar days from that date (INCLUDED: the day has not elapsed on that date) to the end of
    the leave year / the days of the leave year (D5(b)).
R5  CAP (13A(3)): the aggregate of 13A(2)'s period and 13(1)'s four weeks is at most 28 days; 13A(1) is "subject to (3)",
    13(1) is not, so the cut falls on the additional leave: 13A = min(13A(2)'s period, 28 - 4n). In a first leave year
    (13A(5)) where the cap binds (n >= 6 after 2009), "cap, then proportion" and "proportion, then cap" give two outcomes:
    no answer (D1). A first leave year in phase (b) or (d) (a proportion of a proportion, a product of two quantities): no
    answer.
R6  PHASES (13A(2)): by the leave year's first day: before 1 Oct 2007 (b); 1 Oct 2007 to 31 Mar 2008 (a); exactly 1 Apr
    2008 (c); 2 Apr 2008 to 31 Mar 2009 (d); from 1 Apr 2009 (e). (b): 0.8n x (days of the year beginning 1 Oct 2007 elapsed
    at the end of the leave year, last day included) / that year's days; (d): 0.8n + 0.8n x (days of the year beginning 1
    Apr 2009 elapsed at the end of the leave year) / that year's days.
R7  ROUNDING (D7): exact amounts; where the case states "two decimal places, half up" the stated rounding is applied to the
    derived days (in Lean, as the two inequalities of half-up rounding); an amount not exact at 1/100 day without a stated
    rounding has no model: no answer.
R8  INSTALMENTS / PAYMENT IN LIEU (13(9), 13A(6)): leave may be taken in instalments; 13 leave may be replaced by a payment
    in lieu only where employment is terminated; 13A leave also where it arises under 13A(2)(a), (b) or (c); under (2)(d)
    the 0.8-week entitlement "in respect of that part of the leave year which would have elapsed before 1 April 2009" is the
    initial 0.8 weeks of (d) (the further proportion is in respect of the part after it), so the initial component may be
    replaced and the further one not (unless employment is terminated). 13(9)(a): leave may only be taken in its own leave
    year except as carried forward.
R9  CARRY FORWARD (13(14), (15), (17), 13A(7), (7A)): "as a result of" statutory / sick leave "unable to take" is a stated
    judgment (D4); only "unable to take any" is written (then the untaken leave = the year's entitlement, no leave taken).
    (14), (7A): into the following leave year only. (15): may be taken until the last day of the 18 months from the end of
    the leave year (the proviso would be idle if the leave had to be taken in the following leave year: a leave year is 12
    months). (16): (17) applies in a leave year where the employer fails any of (a), (b) (opportunity, or encouragement), (c)
    (stated judgments). (17): the untaken leave and the leave taken but not paid (when no paid leave was taken: the whole
    13 entitlement). (18): leave carried under (17) can be taken up to the end of the first full leave year after it in which
    (17) does not apply (the chain y0, y1, ...: taken in yk when (17) applies in y0 and every year between). 13A(7): the
    agreement's carry forward, up to the agreement's stated days (a fact).
R10 TERMINATION (14(1)-(3)): the leave year in which the termination date falls; "the proportion of the leave year which
    has expired" = B = calendar days of the leave year before the termination date (that date EXCLUDED, "expired before the
    termination date") / days of the leave year; A = the 13 + 13A entitlement of a full leave year (a first leave year with a
    termination in it: A x B is a product of two quantities, no answer); C = leave taken in the leave year. Taken less than
    expired: C x days < A x expired days. The payment (3)(a) is the agreement's sum; (3)(b) is the reg 16 sum for A x B - C
    = the week's pay x a period: a product of two quantities, NOT written (refused, gitlab-expenses R14 precedent); where
    the proportions are equal or more leave was taken, no payment under (2) (0). 14(4): compensation where the agreement
    provides it and more leave was taken than expired. 14(6): the reg 16 sum for carried-forward leave (a product: not
    written) except where there is no previous leave year of the employment, or none carried (0). The Q2 payment = (2) + (6).
R11 NOTICES (15): a notice under (1) (the worker's election) or (2)(a) (the employer's requirement to take leave): the
    relevant date is twice as many days before the earliest day specified as the days or part-days the notice relates to; a
    notice under (2)(b): as many days. "Given ... before the relevant date": the latest day is the day before it; a notice
    given on or before it is in time. 15(5): an agreement varying the timing (stated: on or before the day a stated number
    of days before the earliest day) replaces it; one excluding the (2)(b) right means no (2)(b) requirement is imposed.
    15(6): not to a worker to whom Schedule 2 applies, except partly employed in agriculture with a relevant agreement.
"""
from __future__ import annotations

import hashlib
import json

DAY, LD, ND, GBP = "day", "leave_day", "elapsed_day", "gbp"
NS = range(1, 8)            # days worked in a week, enumerated (R1)
LS = (365, 366)              # days of a year, enumerated

INT_UNITS = {  # per-item constants: base -> (unit, words)
    # worker
    "dpw": (LD, "the days the worker works in a week (stated)"),
    "es": (DAY, "the day the worker's employment began (stated)"),
    "td": (DAY, "the termination date (stated)"),
    "agrpay": (GBP, "the sum a relevant agreement provides for the purposes of regulation 14 (stated)"),
    "agrcap": (LD, "the days of untaken additional leave a relevant agreement allows to be carried forward (stated)"),
    # leave years
    "ys": (DAY, "the first day of the leave year (stated)"),
    "yn": (DAY, "the first day of the next leave year (bridge)"),
    "ylen": (LD, "the calendar days of the leave year (bridge)"),
    "rem": (LD, "the calendar days of the leave year from the day employment began, that day included (bridge)"),
    "exp": (LD, "the calendar days of the leave year before the termination date (bridge)"),
    "elb": (LD, "the days of the year beginning 1 October 2007 elapsed at the end of the leave year (bridge)"),
    "lenb": (LD, "the days of the year beginning 1 October 2007 (bridge)"),
    "eld": (LD, "the days of the year beginning 1 April 2009 elapsed at the end of the leave year (bridge)"),
    "lend": (LD, "the days of the year beginning 1 April 2009 (bridge)"),
    "e18": (DAY, "the last day of the period of 18 months from the end of the leave year (bridge)"),
    "aagr": (DAY, "the day in the calendar year of the leave year's first day with the agreement's day and month (bridge)"),
    "a98": (DAY, "the anniversary of 1 October 1998 in the calendar year of the leave year's first day (bridge)"),
    "aes": (DAY, "the anniversary of the employment's first day in the calendar year of the leave year's first day (bridge)"),
    "tk": (LD, "the days of leave the worker took in the leave year, up to the termination date (stated)"),
    "tkp": (LD, "the days of leave the worker took and was paid for in the leave year (stated)"),
    "e13": (LD, "the days of leave the worker is entitled to under regulation 13 in the leave year"),
    "a2": (LD, "the period of additional leave determined in accordance with regulation 13A(2) for the leave year"),
    "e13a": (LD, "the days of additional leave the worker is entitled to under regulation 13A in the leave year"),
    "etot": (LD, "the days of leave under regulations 13 and 13A together in the leave year"),
    "cf13": (LD, "the days of the leave year's regulation 13 leave carried forward into the following leave year"),
    "cf13a": (LD, "the days of the leave year's regulation 13A leave carried forward into the following leave year"),
    "dper": (LD, "the period of leave by the formula (A x B) - C of regulation 14(3)(b)"),
    "p142": (GBP, "the payment in lieu under regulation 14(2) on the termination"),
    "p146": (GBP, "the payment in lieu under regulation 14(6) on the termination"),
    "pay14": (GBP, "the payment in lieu under regulation 14 on the termination"),
    # notices
    "nd": (DAY, "the day the notice is given (stated)"),
    "ne": (DAY, "the earliest day specified in the notice (stated)"),
    "nc": (ND, "the number of days or part-days to which the notice relates (stated)"),
    "agroff": (ND, "the days before the earliest day on or before which a relevant agreement lets the notice be given (stated)"),
    "rel": (DAY, "the relevant date of the notice (regulation 15(4))"),
    "latest": (DAY, "the latest day on which the notice is given before the relevant date"),
    # proposals
    "pday": (DAY, "the day on which the worker would take the carried-forward leave (stated)"),
}
PAIR_UNITS = {
    "tak13": (LD, "(leave year y0, leave year y1) days of y0's regulation 13 leave carried forward that may be taken in y1"),
    "tak13a": (LD, "(y0, y1) days of y0's regulation 13A leave carried forward that may be taken in y1"),
    "takall": (LD, "(y0, y1) days of y0's regulation 13 and 13A leave carried forward that may be taken in y1"),
}
FACTS = {
    # worker
    "worker": "the item is the worker (the fixed fact of the test)",
    "agrly": "a relevant agreement provides the date on which the worker's leave years begin",
    "sch2": "Schedule 2 applies to the worker (agriculture in Wales or Scotland)",
    "partagri": "the worker is only partly employed in agriculture in Wales or Scotland",
    "agr133": "a relevant agreement provides that regulation 13(3) applies to the worker",
    "agr15": "a relevant agreement provides that regulation 15 applies to the worker",
    "awsa": "the Agricultural Wages (Scotland) Act 1949 (as it had effect on 1 July 1999) applies to the worker",
    "r26a": "regulation 26A applies to the worker",
    "terminated": "the worker's employment is terminated (the termination date stated)",
    "agrpaysum": "a relevant agreement provides a sum for the purposes of regulation 14",
    "agrcomp": "a relevant agreement provides that the worker compensates the employer where leave taken exceeds the year expired",
    "round2": "the case states that days are given to two decimal places, half up",
    "agrcf": "a relevant agreement provides for 13A leave to be carried forward into the following leave year, up to agrcap days",
    "excl2b": "a relevant agreement excludes the employer's right under regulation 15(2)(b)",
    # leave years
    "b15": "regulation 15B applies to the worker in respect of the leave year",
    "stat13": "as a result of statutory leave in the leave year, the worker was unable to take any of the year's regulation 13 leave (stated judgment)",
    "stat13a": "as a result of statutory leave in the leave year, the worker was unable to take any of the year's regulation 13A leave (stated judgment)",
    "sick13": "as a result of sick leave in the leave year, the worker was unable to take any of the year's regulation 13 leave (stated judgment)",
    "faila": "in the leave year the employer failed to recognise the right to annual leave or to payment for it (stated judgment)",
    "failopp": "in the leave year the employer failed to give a reasonable opportunity to take the leave (stated judgment)",
    "failenc": "in the leave year the employer failed to encourage the worker to take the leave (stated judgment)",
    "failinf": "in the leave year the employer failed to inform the worker that untaken leave would be lost (stated judgment)",
    # notices
    "nelect": "the notice is the worker's notice electing to take leave (regulation 15(1))",
    "nreq": "the notice is the employer's notice requiring the worker to take leave (regulation 15(2)(a))",
    "nnot": "the notice is the employer's notice requiring the worker not to take leave (regulation 15(2)(b))",
    "varied": "a relevant agreement replaces the notice's timing by: on or before the day agroff days before the earliest day",
}
BINARY = {"of": "(proposal, leave year) the proposed day is for leave of that leave year carried forward"}
STATED = ("stat13", "stat13a", "sick13", "faila", "failopp", "failenc", "failinf")
BRIDGED_CONSTS = ("yn", "ylen", "rem", "exp", "elb", "lenb", "eld", "lend", "e18", "aagr", "a98", "aes")
DERIVED_UNARY = {
    **{f"dw{n}": f"(worker) the worker works {n} days in a week" for n in NS},
    **{f"{p}{l}": f"(leave year) {w} has {l} days" for p, w in (("l", "the leave year"), ("lb", "the year beginning 1 October 2007"),
                                                                 ("ld", "the year beginning 1 April 2009")) for l in LS},
    "tk0": "(leave year) the worker took no leave in the leave year",
    "tkp0": "(leave year) the worker took no paid leave in the leave year",
    "app13": "(leave year) regulation 13 applies to the worker in respect of the leave year (13(A1))",
    "app13a": "(leave year) regulation 13A applies to the worker in respect of the leave year (13A(A1), (8))",
    "part": "(leave year) employment begins after the first day of the leave year fixed by a relevant agreement (13(5), 13A(5))",
    "pha": "(leave year) the leave year begins on or after 1 October 2007 but before 1 April 2008 (13A(2)(a))",
    "phb": "(leave year) the leave year begins before 1 October 2007 (13A(2)(b))",
    "phc": "(leave year) the leave year begins on 1 April 2008 (13A(2)(c))",
    "phd": "(leave year) the leave year begins after 1 April 2008 but before 1 April 2009 (13A(2)(d))",
    "phe": "(leave year) the leave year begins on or after 1 April 2009 (13A(2)(e))",
    "begins": "(leave year) the worker's leave year under regulation 13 begins on the leave year's first day (13(3))",
    "app17": "(leave year) regulation 13(17) applies in the leave year (13(16))",
    "termin": "(leave year) the worker's employment is terminated during the leave year (14(1)(a))",
    "lt14": "(leave year) the proportion of leave taken is less than the proportion of the leave year expired (14(2))",
    "gt14": "(leave year) the proportion of leave taken exceeds the proportion of the leave year expired (14(4))",
    "comp": "(leave year) the worker must compensate the employer under regulation 14(4) and the agreement",
    "inst13": "(leave year) regulation 13 leave may be taken in instalments (13(9))",
    "inst13a": "(leave year) regulation 13A leave may be taken in instalments (13A(6))",
    "pil13": "(leave year) the year's regulation 13 leave may be replaced by a payment in lieu (13(9)(b))",
    "pil13a": "(leave year) the year's regulation 13A leave may be replaced by a payment in lieu (13A(6))",
    "pil13ai": "(leave year) the initial 0.8-week component under 13A(2)(d) may be replaced by a payment in lieu (13A(6)(c))",
    "pil13af": "(leave year) the further component under 13A(2)(d) may be replaced by a payment in lieu (13A(6))",
    "app133": "(worker) regulation 13(3) applies to the worker (13(4))",
    "app15": "(worker) regulation 15 applies to the worker (15(6))",
    "app13aw": "(worker) regulation 13A applies to the worker (13A(8))",
    "intime": "(notice) the notice is given before the relevant date (15(3)(c), (4), (5))",
    "imposes": "(notice) the notice imposes a requirement under regulation 15(2)(b)",
    "canuse": "(proposal) the worker may take the carried-forward leave on the proposed day",
}
DERIVED_BINARY = {"nextly": "(leave year y0, leave year y1) y1 is the leave year immediately following y0"}

D2024, D1998 = "2024-04-01", "1998-10-01"
D2007, D2008, D2009 = "2007-10-01", "2008-04-01", "2009-04-01"


# --- formula helpers (ve-quantity@1 wire shapes; posthog_leave conventions) ----------------------------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def B(p, x, y): return ["binary", p, c(x), c(y)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def lit(tag, v): return ["decimal", tag, str(v)]
def date(v): return ["date", v]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def add(tag, a, b): return ["add", tag, a, b]
def scale(tag, kk, t): return ["scale", tag, str(kk), t]
def no_later(a, b): return ["date_no_later", a, b]
def before(a, b): return ["date_before", a, b]
def on(a, b): return ["date_on", a, b]
def elapsed(d, t, v): return ["elapsed_days", d, t, v]      # v = t - d (days)
def shift(t, d, n): return ["shift_days", t, d, str(n)]      # t = d + n
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
    return ["const", INT_UNITS[base][0], f"{base}_{x}"]


def kp(base, x, y):
    return ["const", PAIR_UNITS[base][0], f"{base}_{x}_{y}"]


def L(v): return lit(LD, v)
def iff_u(p, x, body): return Iff(U(p, x), body)


def dec(v):
    """An exact decimal string for a Fraction-free literal (ints and one-decimal products)."""
    s = f"{v:.2f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


# --- the case context ---------------------------------------------------------------------------------------------

class Ctx:
    def __init__(self, workers=("w",), years=(), notices=(), proposals=()):
        self.workers, self.years = list(workers), list(years)
        self.notices, self.proposals = list(notices), list(proposals)

    @property
    def items(self):
        return self.workers + self.years + self.notices + self.proposals

    @property
    def w(self):
        return self.workers[0]


def per(kind, fn):
    return lambda ctx: [f for x in getattr(ctx, kind) for f in fn(x, ctx)]


def _cat(*builders):
    return lambda ctx: [f for b in builders for f in b(ctx)]


def _none(ctx):
    return []


# --- splits (R1, arithmetic) --------------------------------------------------------------------------------------

def _splits_w(w, ctx):
    return [iff_u(f"dw{n}", w, Eq(k("dpw", w), L(n))) for n in NS]


def _splits_y(y, ctx):
    out = []
    for p, base in (("l", "ylen"), ("lb", "lenb"), ("ld", "lend")):
        out += [iff_u(f"{p}{l}", y, Eq(k(base, y), L(l))) for l in LS]
    out += [iff_u("tk0", y, Eq(k("tk", y), L(0))), iff_u("tkp0", y, Eq(k("tkp", y), L(0)))]
    return out


def _prop(target, y, w, coef_of_n, count, den_atom, l, n, rounded):
    """target x l = coef(n) x count (exact), or its half-up rounding at 1/100 day (R7): 200 l T - l <= 200 coef count <
    200 l T + l. coef_of_n is the literal coefficient for n (a float with at most one decimal); scaled by 10 to integers."""
    cf10 = round(coef_of_n * 10)
    T = k(target, y)
    if not rounded:
        return [Eq(scale(LD, 10 * l, T), scale(LD, cf10, count))]
    return [Le(scale(LD, 2000 * l, T), add(LD, scale(LD, 200 * cf10, count), L(10 * l))),
            Lt(scale(LD, 200 * cf10, count), add(LD, scale(LD, 2000 * l, T), L(10 * l)))]


# --- regulation 13 ------------------------------------------------------------------------------------------------

def _u1(y, ctx):
    """13(A1) (R2)."""
    return [iff_u("app13", y, Or(before(k("ys", y), date(D2024)), Not(U("b15", y))))]


def _u2(y, ctx):
    """13(1) (R1): four weeks = 4 x the days worked in a week, in a leave year that is not a first leave year under 13(5)."""
    w = ctx.w
    return [Implies(And(U("app13", y), Not(U("part", y))), Eq(k("e13", y), scale(LD, 4, k("dpw", w))))]


def _u3(y, ctx):
    """13(3) with 13(4) (R3): the leave year begins on the anniversary of the agreement's date / 1 October 1998 / the
    employment's first day."""
    w, ys = ctx.w, k("ys", y)
    a, es = U("agrly", w), k("es", w)
    body = Or(And(a, on(ys, k("aagr", y))),
              And(Not(a), no_later(es, date(D1998)), on(ys, k("a98", y))),
              And(Not(a), before(date(D1998), es), no_later(es, ys), on(ys, k("aes", y))))
    neg = Or(And(a, Not(on(ys, k("aagr", y)))),
             And(Not(a), no_later(es, date(D1998)), Not(on(ys, k("a98", y)))),
             And(Not(a), before(date(D1998), es), Or(before(ys, es), Not(on(ys, k("aes", y))))))
    return [Implies(And(U("app133", w), body), U("begins", y)), Implies(And(U("app133", w), neg), Not(U("begins", y)))]


def _u4(w, ctx):
    """13(4)."""
    return [iff_u("app133", w, Or(Not(U("sch2", w)), And(U("partagri", w), U("agr133", w))))]


def _part(y, ctx):
    """13(5) / 13A(5) (R4): the first leave year fixed by a relevant agreement, employment beginning after its first day."""
    w = ctx.w
    es = k("es", w)
    return [iff_u("part", y, And(U("agrly", w), before(k("ys", y), es), before(es, k("yn", y))))]


def _u5(y, ctx):
    """13(5) (R4, R7): 4n x remaining days / days of the leave year."""
    w, out = ctx.w, []
    for n in NS:
        for l in LS:
            for rd in (False, True):
                g = And(U("app13", y), U("part", y), U(f"dw{n}", w), U(f"l{l}", y), U("round2", w) if rd else Not(U("round2", w)))
                out += [Implies(g, f) for f in _prop("e13", y, w, 4 * n, k("rem", y), None, l, n, rd)]
    return out


def _u6(y, ctx):
    """13(9) (R8): instalments; a payment in lieu only where employment is terminated."""
    w = ctx.w
    return [Implies(U("app13", y), U("inst13", y)),
            Implies(And(U("app13", y), U("terminated", w)), U("pil13", y)),
            Implies(And(U("app13", y), Not(U("terminated", w))), Not(U("pil13", y)))]


def _cf13(y, ctx):
    """13(14), (15), (17) (R9): the year's 13 leave carried forward into the following leave year."""
    s, sk, a17 = U("stat13", y), U("sick13", y), U("app17", y)
    return [Implies(And(Or(s, sk), U("tk0", y)), Eq(k("cf13", y), k("e13", y))),
            Implies(And(a17, U("tkp0", y)), Eq(k("cf13", y), k("e13", y))),
            Implies(And(Not(s), Not(sk), Not(a17)), Eq(k("cf13", y), L(0)))]


def _u9(y, ctx):
    """13(16) (R9)."""
    return [iff_u("app17", y, Or(U("faila", y), U("failopp", y), U("failenc", y), U("failinf", y)))]


def _nextly(ctx):
    ys = ctx.years
    return [Iff(B("nextly", a, b), on(k("ys", b), k("yn", a))) for a, b in zip(ys, ys[1:])]


def _tak(ctx):
    """13(14), (15), (17), (18), 13A(7), (7A) (R9): leave of y0 carried forward that may be taken in y1 (the next leave
    year, or the one after it through the (17) chain)."""
    ys, out = ctx.years, []
    for i, y0 in enumerate(ys):
        if i + 1 < len(ys):
            y1 = ys[i + 1]
            nx = B("nextly", y0, y1)
            out += [Implies(nx, Eq(kp("tak13", y0, y1), k("cf13", y0))),
                    Implies(nx, Eq(kp("tak13a", y0, y1), k("cf13a", y0))),
                    Implies(nx, Eq(kp("takall", y0, y1), add(LD, k("cf13", y0), k("cf13a", y0))))]
        if i + 2 < len(ys):
            ym, y1 = ys[i + 1], ys[i + 2]
            ch = And(B("nextly", y0, ym), B("nextly", ym, y1))
            t13 = kp("tak13", y0, y1)
            out += [Implies(And(ch, U("app17", y0), U("tkp0", y0), U("app17", ym), U("tk0", ym)), Eq(t13, k("e13", y0))),
                    Implies(And(ch, Not(U("sick13", y0)), Or(Not(U("app17", y0)), Not(U("app17", ym)))), Eq(t13, L(0))),
                    Implies(ch, Eq(kp("tak13a", y0, y1), L(0))),
                    Implies(ch, Eq(kp("takall", y0, y1), add(LD, t13, kp("tak13a", y0, y1))))]
    return out


def _canuse(p, ctx):
    """13(9)(a), (14), (15), (17), (18) (R8, R9): may the carried-forward 13 leave of y0 be taken on the proposed day."""
    ys, out, d = ctx.years, [], k("pday", p)
    for i, y0 in enumerate(ys):
        of = B("of", p, y0)
        sk, st, a17 = U("sick13", y0), U("stat13", y0), U("app17", y0)
        out += [Implies(And(of, sk, U("tk0", y0), no_later(k("yn", y0), d), no_later(d, k("e18", y0))), U("canuse", p)),
                Implies(And(of, sk, Not(a17), before(k("e18", y0), d)), Not(U("canuse", p))),
                Implies(And(of, Not(sk), Not(st), Not(a17), no_later(k("yn", y0), d)), Not(U("canuse", p)))]
        if i + 1 < len(ys):
            y1 = ys[i + 1]
            inn = And(B("nextly", y0, y1), no_later(k("ys", y1), d), before(d, k("yn", y1)))
            out += [Implies(And(of, st, U("tk0", y0), inn), U("canuse", p))]
        for kk in range(i + 1, len(ys)):
            yk = ys[kk]
            chain = And(*[B("nextly", ys[j], ys[j + 1]) for j in range(i, kk)])
            inn = And(no_later(k("ys", yk), d), before(d, k("yn", yk)))
            mids = ys[i + 1:kk]
            out.append(Implies(And(of, a17, U("tkp0", y0), chain, inn, *[U("app17", m) for m in mids],
                                   *[U("tk0", m) for m in mids]), U("canuse", p)))
            if mids:
                out.append(Implies(And(of, a17, Not(sk), Not(st), chain, inn, Or(*[Not(U("app17", m)) for m in mids])),
                                   Not(U("canuse", p))))
    return out


# --- regulation 13A -----------------------------------------------------------------------------------------------

def _u12(y, ctx):
    """13A(A1), (8) (R2)."""
    w = ctx.w
    return [iff_u("app13a", y, And(Or(before(k("ys", y), date(D2024)), Not(U("b15", y))), Not(U("awsa", w))))]


def _u14(y, ctx):
    """13A(2) (R6, R7): the period of additional leave by the leave year's first day."""
    w, ys, out = ctx.w, k("ys", y), []
    out += [iff_u("pha", y, And(no_later(date(D2007), ys), before(ys, date(D2008)))),
            iff_u("phb", y, before(ys, date(D2007))),
            iff_u("phc", y, on(ys, date(D2008))),
            iff_u("phd", y, And(before(date(D2008), ys), before(ys, date(D2009)))),
            iff_u("phe", y, no_later(date(D2009), ys))]
    g = And(U("app13a", y), Not(U("r26a", w)))
    a2, dpw = k("a2", y), k("dpw", w)
    out += [Implies(And(g, Or(U("pha", y), U("phc", y))), Eq(scale(LD, 10, a2), scale(LD, 8, dpw))),
            Implies(And(g, U("phe", y)), Eq(scale(LD, 10, a2), scale(LD, 16, dpw)))]
    for n in NS:
        for l in LS:
            for rd in (False, True):
                r = U("round2", w) if rd else Not(U("round2", w))
                gb = And(g, U("phb", y), U(f"dw{n}", w), U(f"lb{l}", y), r)
                out += [Implies(gb, f) for f in _prop("a2", y, w, 0.8 * n, k("elb", y), None, l, n, rd)]
                # (d): 10 l a2 = 8 n l + 8 n eld  (0.8n + 0.8n x eld / l)
                gd = And(g, U("phd", y), U(f"dw{n}", w), U(f"ld{l}", y), r)
                if not rd:
                    out.append(Implies(gd, Eq(scale(LD, 10 * l, a2), add(LD, L(8 * n * l), scale(LD, 8 * n, k("eld", y))))))
                else:  # 2000 l a2 - 10 l <= 200 (8nl + 8n eld) < 2000 l a2 + 10 l
                    rhs = add(LD, L(1600 * n * l), scale(LD, 1600 * n, k("eld", y)))
                    out += [Implies(gd, Le(scale(LD, 2000 * l, a2), add(LD, rhs, L(10 * l)))),
                            Implies(gd, Lt(rhs, add(LD, scale(LD, 2000 * l, a2), L(10 * l))))]
    return out


def _u15(y, ctx):
    """13A(1), (3) (R5): a full leave year: min(13A(2)'s period, 28 - 4n)."""
    w = ctx.w
    g = And(U("app13a", y), Not(U("r26a", w)), Not(U("part", y)))
    agg = add(LD, k("a2", y), scale(LD, 4, k("dpw", w)))
    return [Implies(And(g, Le(agg, L(28))), Eq(k("e13a", y), k("a2", y))),
            Implies(And(g, Lt(L(28), agg)), Eq(add(LD, k("e13a", y), scale(LD, 4, k("dpw", w))), L(28)))]


def _u17(y, ctx):
    """13A(5) (R4, R5, R7): a first leave year, phases (a), (c), (e) only, and only where the cap does not bind."""
    w, out = ctx.w, []
    g = And(U("app13a", y), Not(U("r26a", w)), U("part", y))
    for n in NS:
        for l in LS:
            for rd in (False, True):
                r = U("round2", w) if rd else Not(U("round2", w))
                if 5.6 * n <= 28:
                    ge = And(g, U("phe", y), U(f"dw{n}", w), U(f"l{l}", y), r)
                    out += [Implies(ge, f) for f in _prop("e13a", y, w, 1.6 * n, k("rem", y), None, l, n, rd)]
                if 4.8 * n <= 28:
                    gac = And(g, Or(U("pha", y), U("phc", y)), U(f"dw{n}", w), U(f"l{l}", y), r)
                    out += [Implies(gac, f) for f in _prop("e13a", y, w, 0.8 * n, k("rem", y), None, l, n, rd)]
    return out


def _etot(y, ctx):
    return [Eq(k("etot", y), add(LD, k("e13", y), k("e13a", y)))]


def _u18(y, ctx):
    """13A(6) (R8)."""
    w = ctx.w
    a, t = U("app13a", y), U("terminated", w)
    early = Or(U("pha", y), U("phb", y), U("phc", y))
    return [Implies(a, U("inst13a", y)),
            Implies(And(a, Or(t, early)), U("pil13a", y)),
            Implies(And(a, Not(t), U("phe", y)), Not(U("pil13a", y))),
            Implies(And(a, U("phd", y)), U("pil13ai", y)),
            Implies(And(a, U("phd", y), t), U("pil13af", y)),
            Implies(And(a, U("phd", y), Not(t)), Not(U("pil13af", y)))]


def _cf13a(y, ctx):
    """13A(7), (7A) (R9)."""
    w = ctx.w
    s, ag, cf = U("stat13a", y), U("agrcf", w), k("cf13a", y)
    e = k("e13a", y)
    return [Implies(And(s, U("tk0", y)), Eq(cf, e)),
            Implies(And(Not(s), ag, U("tk0", y), Le(k("agrcap", w), e)), Eq(cf, k("agrcap", w))),
            Implies(And(Not(s), ag, U("tk0", y), Lt(e, k("agrcap", w))), Eq(cf, e)),
            Implies(And(Not(s), Not(ag)), Eq(cf, L(0)))]


def _u21(w, ctx):
    """13A(8)."""
    return [Implies(U("awsa", w), Not(U("app13aw", w)))]


# --- regulation 14 ------------------------------------------------------------------------------------------------

def _u22(y, ctx):
    """14(1)-(3) (R10): the termination's leave year; taken less than / more than expired, split over n and l."""
    w, out = ctx.w, []
    td = k("td", w)
    out.append(iff_u("termin", y, And(U("terminated", w), no_later(k("ys", y), td), before(td, k("yn", y)))))
    g = And(U("termin", y), Not(U("part", y)), U("phe", y), U("app13", y), U("app13a", y), Not(U("r26a", w)))
    tk, ex = k("tk", y), k("exp", y)
    for n in NS:
        a10 = min(56 * n, 280)        # 10 x A: min(5.6 n, 28) days
        for l in LS:
            gg = And(g, U(f"dw{n}", w), U(f"l{l}", y))
            lhs, rhs = scale(LD, 10 * l, tk), scale(LD, a10, ex)
            out += [Implies(And(gg, Lt(lhs, rhs)), U("lt14", y)), Implies(And(gg, Le(rhs, lhs)), Not(U("lt14", y))),
                    Implies(And(gg, Lt(rhs, lhs)), U("gt14", y)), Implies(And(gg, Le(lhs, rhs)), Not(U("gt14", y))),
                    Implies(gg, Eq(add(LD, scale(LD, 10 * l, k("dper", y)), lhs), rhs))]
    return out


def _u24(y, ctx):
    """14(2), (3) (R10): (3)(a) the agreement's sum; no payment where taken is not less than expired; (3)(b) NOT written."""
    w = ctx.w
    t = U("termin", y)
    return [Implies(And(t, Not(U("lt14", y))), Eq(k("p142", y), lit(GBP, "0"))),
            Implies(And(t, U("lt14", y), U("agrpaysum", w)), Eq(k("p142", y), k("agrpay", w)))]


def _u25(y, ctx):
    """14(4)."""
    w = ctx.w
    return [Implies(And(U("gt14", y), U("agrcomp", w)), U("comp", y)),
            Implies(And(U("termin", y), Or(Not(U("gt14", y)), Not(U("agrcomp", w)))), Not(U("comp", y)))]


def _u26(ctx):
    """14(6) (R10): 0 where there is no previous leave year of the employment or nothing was carried from the only one; the
    reg 16 sum otherwise NOT written (a product of two quantities). The Q2 payment = 14(2) + 14(6)."""
    w, out, ys = ctx.w, [], ctx.years
    for i, y in enumerate(ys):
        t = U("termin", y)
        out += [Implies(And(t, no_later(k("ys", y), k("es", w))), Eq(k("p146", y), lit(GBP, "0"))),
                Implies(t, Eq(k("pay14", y), add(GBP, k("p142", y), k("p146", y))))]
        if i >= 1:
            y0 = ys[i - 1]
            out.append(Implies(And(t, B("nextly", y0, y), no_later(k("ys", y0), k("es", w)),
                                   Eq(add(LD, k("cf13", y0), k("cf13a", y0)), L(0))), Eq(k("p146", y), lit(GBP, "0"))))
    return out


# --- regulation 15 ------------------------------------------------------------------------------------------------

def _u30(n, ctx):
    """15(4) (R11): the relevant date; 15(3)(c): the latest day is the day before it; 15(5): a varied timing."""
    v = U("varied", n)
    return [Implies(And(Or(U("nelect", n), U("nreq", n)), Not(v)), elapsed(k("rel", n), k("ne", n), scale(ND, 2, k("nc", n)))),
            Implies(And(U("nnot", n), Not(v)), elapsed(k("rel", n), k("ne", n), k("nc", n))),
            Implies(Not(v), shift(k("rel", n), k("latest", n), 1))]


def _u29(n, ctx):
    """15(3)(c) (R11): given on or before the latest day = before the relevant date."""
    w = ctx.w
    return [Implies(And(U("app15", w), no_later(k("nd", n), k("latest", n))), U("intime", n)),
            Implies(And(U("app15", w), before(k("latest", n), k("nd", n))), Not(U("intime", n)))]


def _u31(n, ctx):
    """15(5) (R11): the agreement's timing; the (2)(b) right excluded."""
    w = ctx.w
    nn = U("nnot", n)
    return [Implies(U("varied", n), elapsed(k("latest", n), k("ne", n), k("agroff", n))),
            Implies(And(nn, U("excl2b", w)), Not(U("imposes", n))),
            Implies(And(nn, Not(U("excl2b", w)), U("intime", n)), U("imposes", n)),
            Implies(And(nn, Not(U("excl2b", w)), Not(U("intime", n))), Not(U("imposes", n)))]


def _u32(w, ctx):
    """15(6)."""
    return [iff_u("app15", w, Or(Not(U("sch2", w)), And(U("partagri", w), U("agr15", w))))]


NORM, JUDG = "other:norm", "other:judgment standard"
UNITS = {
    1: ("RULE", _cat(per("workers", _splits_w), per("years", _splits_y), per("years", _u1)), "13(A1) (R2); the splits of R1"),
    2: ("RULE", per("years", _u2), "13(1): four weeks = 4n days (R1)"),
    3: ("RULE", per("years", _u3), "13(3) (R3); anniversaries BRIDGED"),
    4: ("RULE", per("workers", _u4), "13(4)"),
    5: ("RULE", _cat(per("years", _part), per("years", _u5)), "13(5) (R4, R7); remaining days BRIDGED"),
    6: ("PART", _cat(per("years", _u6), per("proposals", _canuse)), NORM,
        "13(9) (R8): instalments and payment in lieu WRITTEN as outcomes; 'may be taken' / 'may not be replaced' are "
        "permissions and prohibitions read as their outcomes for a stated proposal; 13(9)(a)'s 'only in the leave year' "
        "WRITTEN in canuse"),
    7: ("PART", per("years", _cf13), JUDG, "13(14) (R9): 'as a result of ... unable to take' a stated judgment; only "
                                            "'unable to take any' written"),
    8: ("PART", _none, JUDG, "13(15) (R9, unit 7's builder and canuse): the 18 months BRIDGED; 'as a result of' a stated "
                             "judgment; only 'unable to take any' written"),
    9: ("PART", per("years", _u9), JUDG, "13(16): 'reasonable opportunity' and the failures are stated judgments"),
    10: ("RULE", _none, "13(17) (R9, unit 7's builder): untaken and taken-unpaid leave carried; written where no paid "
                        "leave was taken"),
    11: ("RULE", _cat(_nextly, _tak), "13(18) (R9): the (17) chain; next leave years BRIDGED"),
    12: ("RULE", per("years", _u12), "13A(A1) (R2) with 13A(8)"),
    13: ("RULE", _none, "13A(1): subject to 26A (stated not to apply), (3), (5) (unit 15's builder)"),
    14: ("PART", per("years", _u14), "date/age arithmetic", "13A(2) (R6, R7): the phases WRITTEN; the elapsed days of the "
                                                             "years beginning 1 Oct 2007 / 1 Apr 2009 BRIDGED"),
    15: ("RULE", _cat(per("years", _u15), per("years", _etot)), "13A(3) (R5)"),
    16: ("RULE", _none, "13A(4): the same leave-year items serve 13 and 13A"),
    17: ("PART", per("years", _u17), "amount arithmetic", "13A(5) (R4, R5): written for phases (a), (c), (e) where the cap "
                                                           "does not bind; with the cap binding two outcomes (D1); phases "
                                                           "(b), (d) a product of two proportions"),
    18: ("RULE", per("years", _u18), "13A(6) (R8)"),
    19: ("RULE", per("years", _cf13a), "13A(7): the agreement's carry forward up to its stated days (R9)"),
    20: ("PART", _none, JUDG, "13A(7A) (unit 19's builder): 'as a result of' a stated judgment"),
    21: ("RULE", per("workers", _u21), "13A(8)"),
    22: ("RULE", per("years", _u22), "14(1) (R10); expired days BRIDGED"),
    23: ("RULE", _none, "14(2) (R10, unit 22's builder)"),
    24: ("PART", per("years", _u24), "amount arithmetic", "14(3) (R10): (a) WRITTEN; (b) the reg 16 sum for A x B - C is the "
                                                           "week's pay x a period, a product of two quantities NOT written "
                                                           "(the period itself is written: dper)"),
    25: ("RULE", per("years", _u25), "14(4)"),
    26: ("PART", _u26, "amount arithmetic", "14(6) (R10): the reg 16 sum for the carried leave is a product of two "
                                            "quantities, NOT written; 0 where nothing was carried"),
    27: ("PART", _none, NORM, "15(1): 'may take leave ... as he may elect' a permission NOT written; its notice is the "
                              "notice under (1) of units 29-30"),
    28: ("PART", _none, NORM, "15(2): 'may require' a permission NOT written; the notices under (2)(a), (b) of units "
                              "29-30, 'imposes' in unit 31"),
    29: ("PART", per("notices", _u29), NORM, "15(3)(c) WRITTEN (intime); (a) 'may relate' a permission and (b) 'shall "
                                             "specify' a duty NOT written"),
    30: ("RULE", per("notices", _u30), "15(4) (R11)"),
    31: ("RULE", per("notices", _u31), "15(5) (R11): the agreement's terms stated"),
    32: ("RULE", per("workers", _u32), "15(6)"),
}


def units_table(mutant=None):
    t = dict(UNITS)
    if mutant is not None:
        t = MUTANTS[mutant][1](t)
    return t


def rules(ctx, mutant=None):
    out = []
    for n, e in sorted(units_table(mutant).items()):
        if e[1] is None:
            continue
        for i, f in enumerate(e[1](ctx)):
            for j, part in enumerate(conjuncts(f)):
                out.append({"id": f"u{n}.{i}.{j}", "unit": n, "formula": part, "defines": defines(part)})
    return out


# --- structure helpers --------------------------------------------------------------------------------------------

ASKED_BASES = ("e13", "a2", "e13a", "etot", "cf13", "cf13a", "dper", "p142", "p146", "pay14", "rel", "latest",
               "tak13", "tak13a", "takall")


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


def asked_in(t):
    a, cs = set(), set()
    atoms_in(t, a, cs)
    return sorted(x for x in cs if x.split("_", 1)[0] in ASKED_BASES)


def defines(f):
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
    if f[0] == "eq":
        got = asked_in(f[1]) or asked_in(f[2])
        if len(got) == 1:
            return got
        if f[1][0] == "const" and len(f[1]) == 3:
            return [f[1][2]]
    if f[0] in ("le", "lt"):
        got = sorted(set(asked_in(f[1])) | set(asked_in(f[2])))
        if len(got) == 1:
            return got
    if f[0] == "shift_days":            # t = d + n defines d (the latest day from the relevant date)
        return asked_in(f[2])
    if f[0] == "elapsed_days":          # v = t - d defines d
        return asked_in(f[1])
    raise ValueError(f"no defined target: {f}")


# --- the environment for one case ---------------------------------------------------------------------------------

KIND_BASES = {"workers": ("dpw", "es", "td", "agrpay", "agrcap"),
              "years": ("ys", "yn", "ylen", "rem", "exp", "elb", "lenb", "eld", "lend", "e18", "aagr", "a98", "aes", "tk",
                        "tkp", "e13", "a2", "e13a", "etot", "cf13", "cf13a", "dper", "p142", "p146", "pay14"),
              "notices": ("nd", "ne", "nc", "agroff", "rel", "latest"),
              "proposals": ("pday",)}


def int_constants(ctx):
    out = {}
    for kind, bases in KIND_BASES.items():
        for x in getattr(ctx, kind):
            for base in bases:
                out[f"{base}_{x}"] = INT_UNITS[base]
    for i, a in enumerate(ctx.years):
        for b in ctx.years[i + 1:]:
            for base in PAIR_UNITS:
                out[f"{base}_{a}_{b}"] = PAIR_UNITS[base]
    return out


def environment(ctx):
    consts = {}
    for x in ctx.items:
        consts[x] = {"sort": "item", "description": f"The case's item {x}.", "verbalisation": f"item {x}"}
    for name, (u, w) in int_constants(ctx).items():
        consts[name] = {"sort": "$int", "unit": u, "description": f"{w[0].upper() + w[1:]} ({name}).",
                        "verbalisation": f"{w} ({name})"}
    preds = {n: {"arguments": ["item"], "description": d[0].upper() + d[1:] + "."}
             for n, d in {**FACTS, **DERIVED_UNARY}.items()}
    preds.update({n: {"arguments": ["item", "item"], "description": d[0].upper() + d[1:] + "."}
                  for n, d in {**BINARY, **DERIVED_BINARY}.items()})
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "The worker, a leave year, a notice or a proposed day the case "
                                                             "names."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {DAY: {"scale": "1", "display": {"kind": "iso_date"}},
                      ND: {"scale": "1", "display": {"kind": "decimal", "label": "days"}},
                      LD: {"scale": "100", "display": {"kind": "decimal", "label": "leave-days"}},
                      GBP: {"scale": "100", "display": {"kind": "decimal", "label": "GBP"}}}}


# --- planted errors (run.py --mutants): each must change the answer of at least one question ----------------------

def _swap(n, fn):
    def apply(t):
        t = dict(t)
        e = t[n]
        t[n] = (e[0], fn(e[1]), *e[2:])
        return t
    return apply


def _wrap(walker):
    return lambda builder: (lambda ctx: [walker(f) for f in builder(ctx)])


def _json_sub(a, b):
    return lambda f: json.loads(json.dumps(f).replace(a, b))


def _drop(pred):
    return lambda builder: (lambda ctx: [f for f in builder(ctx) if not pred(json.dumps(f))])


def _dropf(pred):
    return lambda builder: (lambda ctx: [f for f in builder(ctx) if not (f[0] == "implies" and pred(f))])


def _set_shift(f, n):
    if f[0] == "implies" and f[2][0] == "shift_days":
        return ["implies", f[1], f[2][:3] + [n]]
    return f


def _rem_minus_one(f):
    if type(f) is not list:
        return f
    if f[:2] == ["const", LD] and len(f) == 3 and f[2].startswith("rem_"):
        return ["add", LD, f, ["decimal", LD, "-1"]]
    return [_rem_minus_one(x) for x in f]


MUTANTS = {
    "M1": ("WEEKS: 13(1) four weeks read as five", _swap(2, _wrap(_json_sub('"scale", "leave_day", "4"',
                                                                           '"scale", "leave_day", "5"')))),
    "M2": ("WEEKS: 13A(2)(e) 1.6 weeks read as 1.5", _swap(14, _wrap(_json_sub('"leave_day", "16", ["const", "leave_day", "dpw_',
                                                                              '"leave_day", "15", ["const", "leave_day", "dpw_')))),
    "M3": ("CAP: 13A(3) the 28-day maximum dropped", _swap(15, _drop(lambda s: '"leave_day", "28"]]' in s and '"lt"' in s))),
    "M4": ("CAP: 13A(3) 28 days read as 30", _swap(15, _wrap(_json_sub('["decimal", "leave_day", "28"]',
                                                                       '["decimal", "leave_day", "30"]')))),
    "M5": ("DATE: 13(3)(b) 1 October 1998 read as 2 October 1998 (on or before)",
           _swap(3, _wrap(_json_sub('"1998-10-01"', '"1998-10-02"')))),
    "M6": ("PHASE: 13A(2)(e) from 1 April 2009 read as from 2 April 2009",
           _swap(14, _wrap(_json_sub('"2009-04-01"', '"2009-04-02"')))),
    "M7": ("PIL: 13A(6)(b) phases (a)-(c) payment in lieu dropped",
           _swap(18, _drop(lambda s: '"pil13a"' in s and '"pha"' in s))),
    "M8": ("NOTICE: 15(4)(a) twice as many days read as as many", _swap(30, _wrap(_json_sub('"scale", "elapsed_day", "2"',
                                                                                         '"scale", "elapsed_day", "1"')))),
    "M9": ("NOTICE: 15(3)(c) 'before the relevant date' read as 'on or before' (latest = the relevant date)",
           _swap(30, _wrap(lambda f: _set_shift(f, "0")))),
    "M10": ("PROPORTION: 13(5) remaining days read as excluding the first day (one day fewer)",
            _swap(5, _wrap(_rem_minus_one))),
    "M11": ("CARRY: 13(15) the 18-month limit dropped (sick leave carried without end)",
            _swap(6, _dropf(lambda f: f[2][0] == "not" and '"e18_' in json.dumps(f)))),
    "M12": ("CHAIN: 13(18) the (17) chain dropped (carried leave usable only in the next leave year)",
            _swap(6, _dropf(lambda f: f[2][:2] == ["unary", "canuse"] and '"app17"' in json.dumps(f[1])
                            and '"stat13"' not in json.dumps(f[1]) and '"sick13"' not in json.dumps(f[1])))),
    "M13": ("TERMINATION: 14(2) 'less than' read as 'not more than' (equal proportions pay)",
            _swap(22, _wrap(lambda f: json.loads(json.dumps(f).replace('["lt", ["scale", "leave_day"', '["le", ["scale", "leave_day"'))
                            if '"lt14"' in json.dumps(f) else f))),
    "M14": ("13A(8): the Agricultural Wages (Scotland) Act exclusion dropped", _swap(21, lambda b: _none)),
    "M15": ("15(6)/13(4): Schedule 2 exclusion dropped", _swap(32, _wrap(_json_sub('"sch2"', '"partagri"')))),
    "M16": ("CARRY: 13A(7) the agreement's cap dropped (all untaken 13A leave carried)",
            _swap(19, _drop(lambda s: '"agrcap_' in s and '["le"' in s))),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
