"""OPM "FEGLI Premiums" page, Premium Overview to before Rates History (statute corpus batch 4, NON-STATUTE (d) benefits
plan summary, STAND-IN: a premium schedule): the VE translation, one pass with today's language. CROSS-FAMILY questions
(Codex writer), Opus translator.

Row statute-corpus-opm-fegli-premiums (dri-statute-corpus-opm-fegli-premiums-w-1124, Opus 5.5). Written from the pinned
source (manage-agents reviews/spare/statute-corpus/batch4/opm-fegli-premiums/source.txt, sha256 322605c8...bd6b, US federal
work, 17 U.S.C. 105) and its 73 units (units.jsonl, sha256 25f080fa...0bf840; 64 table rows). The encoder's question file
(questions only, no answers) was read BEFORE this file was written (ISOLATION.md says so). Scope and the decisions D1-D13
are ISOLATION.md's, fixed before the writer ran; the readings below are fixed here, before cases.py exists. Evidence
branch: nothing here is a Lean kernel line, a profile, a refuses pair or a lint change; nothing merges.

UNITS maps each unit n of units.jsonl to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one sub-case;
  ("PART", builder, cause, note) written except the part named in the note;
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2).
Entry 0 is no unit: the question form "total premium for <coverages>" = the sum of the named coverages' premiums (R11).
A builder returns (formula, target) pairs: target is the atom key or constant the formula defines (None = a check).

ONE SUB-CASE = the items one question needs: the enrollee p; one premium period t (a biweekly pay period or one calendar
month); under t the coverages the question names (basic, opta, optb, optc); under an Option C coverage one item per
elected multiple. Every value a rule needs is a stated fact (the age in whole years throughout the period, the period's
first day, the 65th birthday, the Basic Insurance Amount, the Option B coverage amount, the effective day of a later
75% Reduction election) or a value computed in Lean from them. There is NO bridge: the rate dates and the 65th-birthday
months are date comparisons in the language; every premium is a product of a literal rate of the text and a stated
amount (an integer scaling, Lean) or a sum of literal rates over the elected multiples.

READINGS (fixed here; refuse when in doubt; D-numbers are ISOLATION.md's):
R1  Rate dates (units 5, 43; D7): "effective on the first pay period that started on or after October 1, 2021": the rates
    apply to a period whose first day is on or after 2021-10-01 and not to one that starts before it (the page gives no
    end: they are the page's current rates). An annuitant's calendar month starts on its first day (the encoder enters a
    named month as its first day). Every premium row needs its period's rates to apply; earlier rates are out of scope.
R2  Age groups (all age-group rows; D4): the stated whole-year age throughout the period; "Under 35" = age < 35; "35-39" =
    35 <= age <= 39; "65+" / "65 and over" / "60+" / "80 and over" / "Age 80+" = at least the number. No bridge.
R3  Employee tables (units 44-73, "Premiums for Employees") apply to a federal employee; the annuitant tables (units 6-42,
    "Premiums for Annuitants") to an eligible annuitant and only for a calendar month (monthly). Employee rows: a biweekly
    pay period takes the Biweekly column, a calendar month the Monthly column.
R4  Per $1,000 (units 6, 7, 17-29, 44, 52-62): premium = rate x (amount / $1,000), written as the integer equation
    1000 x 10^d x premium = (rate x 10^d) x amount in cents (d = the rate's decimal places); a premium that is not a whole
    number of cents has no model (refused, D6: never rounded). The Basic amount is the Basic Insurance Amount (for an
    annuitant: in effect at retirement, units 6/7's caption); the Option B amount is the stated Option B coverage.
R5  Per multiple (units 30-42, 63-73): each elected multiple costs the row's rate; the Option C premium is the sum over the
    elected multiples (one item each: a count times a rate is a sum of the rate, never a product of two quantities).
R6  Flat (units 9-16, 45-51): the Option A premium is the row's amount. "Free" = $0.00.
R7  65th birthday (units 6, 7; D5): "Until the Month after your 65th Birthday" holds for a month whose first day is on or
    before the 65th birthday (that month or an earlier one); "Starting the Month after" for a month whose first day is
    after it (every later month). Date comparisons in Lean.
R8  Reductions (units 6-8): the column is the Basic reduction elected at retirement (75%, 50%, No Reduction); a later
    "subsequent" 75% Reduction election (unit 8) takes the 75% column for a month whose first day is on or after its
    effective day, and the elected-at-retirement column before it.
R9  For life (unit 8): an annuitant on the 50% or No Reduction column "will continue to pay premiums for life" unless
    they cancel or subsequently elect 75% Reduction: yes when the column is 50%/No Reduction and neither happened; no when
    either happened.
R10 Options B and C at 65+ for annuitants (units 24, 25, 37, 38; D8): "Free* (But See Below)" holds for an annuitant aged
    65 or more who did not elect No Reduction for that option; one who elected No Reduction pays the No Reduction row by
    age (units 26-29, 39-42). Under 65 the age rows apply whatever the election.
R11 Totals (entry 0): the question's "total premium for <coverages>" = the sum of the premiums of the coverages it names.
R12 Descriptions (units 1-4; D9): the yes/no the text states for a Basic enrollee: the rate does not change as the
    enrollee ages (1); the enrollee pays an average cost over the term (2); the rate is the same regardless of age or
    health status (3); the cost of the post-65 benefit is included in the Basic level premium (4).
R13 Extra Benefit (unit 3; D10): the literal step rule: 100% at age 35 or younger, "beginning on the 36th birthday" 10%
    less each year, none from 45 ("until age 45, after which, there is no Extra Benefit"): a Basic enrollee aged at most
    44 is covered, aged 45 or more is not; it costs nothing extra ("at no extra cost"). The example (C5) is not used.
No number from a case's facts is ever a coefficient: every coefficient is a literal of the pinned text (the rates, 1,000
per $1,000, the ages, 2021-10-01).
"""
from __future__ import annotations

import hashlib
import json

USD, DAY, AGE = ("usd_cent", "day", "age_year")

# base -> (unit, wording); a constant is f"{base}_{item}"; bases carry no "_"
BASES = {
    "ag": (AGE, "the enrollee's age in whole years throughout the period (stated)"),
    "st": (DAY, "the first day of the pay period or calendar month (stated)"),
    "bd": (DAY, "the enrollee's 65th birthday (stated)"),
    "sd": (DAY, "the effective day of the later 75% Reduction election (stated)"),
    "amt": (USD, "the Basic Insurance Amount (at retirement for an annuitant) or the Option B coverage amount (stated)"),
    "pr": (USD, "the coverage's premium for the period"),
    "pm": (USD, "the premium of one Option C multiple for the period"),
    "tot": (USD, "the total premium of the named coverages for the period"),
}
STATED_BASES = ("ag", "st", "bd", "sd", "amt")
STEP_BASES = tuple(b for b in BASES if b not in STATED_BASES)

FACTS = {
    "emp": "the enrollee is a federal employee",
    "ann": "the enrollee is an eligible annuitant",
    "basic": "the enrollee has Basic insurance",
    "r75": "the enrollee elected 75% Reduction for Basic insurance at retirement",
    "r50": "the enrollee elected 50% Reduction for Basic insurance at retirement",
    "rno": "the enrollee elected No Reduction for Basic insurance at retirement",
    "s75": "the enrollee subsequently elected 75% Reduction for Basic insurance",
    "canc": "the enrollee cancelled Basic insurance",
    "nrb": "the enrollee elected No Reduction for Option B",
    "nrc": "the enrollee elected No Reduction for Option C",
    "bw": "the period is a biweekly pay period (false: one calendar month)",
}
STATED_JUDGMENT = ()   # the writer stated none (every question tagged "none"; no half-up convention in any case)
DERIVED = {
    "rap": "the page's rates apply to the period",
    "upto": "the month is the month of the 65th birthday or an earlier one",
    "aft": "the month is after the month of the 65th birthday",
    "s75in": "the later 75% Reduction election is in effect for the period",
    "c75": "the period's Basic column is 75% Reduction",
    "c50": "the period's Basic column is 50% Reduction",
    "cno": "the period's Basic column is No Reduction",
    "nrbpay": "the annuitant must continue to pay No Reduction Option B premiums for the period",
    "nrcpay": "the annuitant must continue to pay No Reduction Option C premiums for the period",
    "free": "the coverage costs nothing for the period",
    "life": "the enrollee will continue to pay Basic premiums for life",
    "agechg": "the enrollee's Basic rate changes as the enrollee ages",
    "avgc": "the enrollee pays an average cost over the term of the Basic coverage",
    "hlth": "the enrollee's health status gives a different individual Basic rate",
    "post65": "the Basic level premium includes the cost of the post-65 benefit",
    "xb": "the enrollee is covered by the Extra Benefit in the period",
    "xbcost": "the Extra Benefit costs the enrollee anything extra",
}


# --- formula helpers (ve-quantity@1 wire shapes) --------------------------------------------------------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def usd(v): return ["decimal", USD, v]
def age(v): return ["decimal", AGE, str(v)]
def date(v): return ["date", v]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def scale(tag, kk, t): return ["scale", tag, str(kk), t]
def add(tag, a, b): return ["add", tag, a, b]
def no_later(a, b): return ["date_no_later", a, b]
def before(a, b): return ["date_before", a, b]
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


def Add(unit, terms):
    terms = list(terms)
    if not terms:
        return ["decimal", unit, "0"]
    r = terms[-1]
    for t in reversed(terms[:-1]):
        r = ["add", unit, t, r]
    return r


UNIT_OF = {b: u for b, (u, _) in BASES.items()}


def k(base, x):
    return ["const", UNIT_OF[base], f"{base}_{x}"]


def key(formula):
    return json.dumps(formula, sort_keys=True, separators=(",", ":"))


def A(p, x):
    return key(U(p, x))


# --- the case context -------------------------------------------------------------------------------------------------

class Ctx:
    """items: [(id, kind)]; parent: {child id: parent id}. Kinds: person, period, basic, opta, optb, optc, mult."""

    def __init__(self, items, parent=None):
        self.items = list(items)
        self.parent = dict(parent or {})
        self.person = "p"

    def of(self, kind):
        return [x for x, kd in self.items if kd == kind]

    def children(self, x, kind=None):
        kinds = dict(self.items)
        return [y for y, p in self.parent.items() if p == x and (kind is None or kinds[y] == kind)]


P = "p"


def pf(name):
    return U(name, P)


def both(pos, neg, atom, x):
    """atom(x) <- pos; not atom(x) <- neg (either may be None)."""
    out = []
    if pos is not None:
        out.append((Implies(pos, U(atom, x)), A(atom, x)))
    if neg is not None:
        out.append((Implies(neg, Not(U(atom, x))), A(atom, x)))
    return out


# --- rates and age groups (the literals of the pinned text) ------------------------------------------------------------

def per_thousand(prem, amount, rate):
    """R4: premium = rate x amount / 1,000 as 1000 x 10^d x premium = (rate x 10^d) x amount (cents both sides)."""
    whole, _, frac = rate.partition(".")
    d = len(frac)
    return Eq(scale(USD, 1000 * 10 ** d, prem), scale(USD, int((whole or "0") + frac), amount))


def flat(prem, rate):
    return Eq(prem, usd("0.00" if rate == "Free" else rate))


def group(lo, hi):
    """R2: lo <= age <= hi on the period's stated age (None = open end); 'Under 35' (lo "<") = age < hi."""
    if lo is None and hi is None:
        return lambda t: None
    def f(t):
        if lo == "<":
            return Lt(k("ag", t), age(hi))
        return And(None if lo is None else Le(age(lo), k("ag", t)),
                   None if hi is None else Le(k("ag", t), age(hi)))
    return f


def _periods(ctx, kind):
    """(period, coverage) pairs for the coverages of kind under each period."""
    return [(ctx.parent[x], x) for x in ctx.of(kind)]


def _ann_month(t):
    return And(pf("ann"), Not(U("bw", t)), U("rap", t))


def _emp(t):
    return And(pf("emp"), U("rap", t))


# --- the rules, unit by unit ------------------------------------------------------------------------------------------

def _total(ctx):
    """Entry 0 (R11): the named coverages' total = the sum of their premiums."""
    return [(Eq(k("tot", t), Add(USD, [k("pr", x) for x in ctx.children(t)])), f"tot_{t}") for t in ctx.of("period")
            if ctx.children(t)]


def _u1(ctx):
    """Unit 1 (R12): the rate for an individual enrollee does not change as the enrollee ages."""
    return both(None, pf("basic"), "agechg", P)


def _u2(ctx):
    """Unit 2 (R12): the enrollee pays an average cost over the term of their coverage."""
    return both(pf("basic"), None, "avgc", P)


def _u3(ctx):
    """Unit 3 (R12, R13): same rate regardless of age or health status; the Extra Benefit (35 or younger; none from 45)."""
    out = both(None, pf("basic"), "hlth", P) + both(None, pf("basic"), "xbcost", P)
    for t in ctx.of("period"):
        out += both(And(pf("basic"), Le(k("ag", t), age(35))), None, "xb", t)
        out += both(And(pf("basic"), Le(age(36), k("ag", t)), Lt(k("ag", t), age(45))), None, "xb", t)
        out += both(None, And(pf("basic"), Le(age(45), k("ag", t))), "xb", t)
    return out


def _u4(ctx):
    """Unit 4 (R12): the cost of the post-65 benefit is included in the FEGLI Basic level premium."""
    return both(pf("basic"), None, "post65", P)


def _rates(who):
    def b(ctx):
        """Units 5 / 43 (R1): the rates apply to a period starting on or after 2021-10-01."""
        out = []
        for t in ctx.of("period"):
            out += both(And(pf(who), no_later(date("2021-10-01"), k("st", t))),
                        And(pf(who), before(k("st", t), date("2021-10-01"))), "rap", t)
        return out
    return b


def _columns(ctx):
    """R7, R8: the 65th-birthday months, the later 75% election and the period's Basic column."""
    out = []
    for t in ctx.of("period"):
        out += both(no_later(k("st", t), k("bd", P)), None, "upto", t)
        out += both(before(k("bd", P), k("st", t)), None, "aft", t)
        out += both(And(pf("s75"), no_later(k("sd", P), k("st", t))), Not(pf("s75")), "s75in", t)
        out.append((Implies(And(pf("s75"), before(k("st", t), k("sd", P))), Not(U("s75in", t))), A("s75in", t)))
        out += both(Or(pf("r75"), U("s75in", t)), None, "c75", t)
        out += both(And(pf("r50"), Not(U("s75in", t))), None, "c50", t)
        out += both(And(pf("rno"), Not(U("s75in", t))), None, "cno", t)
    return out


ANN_BASIC = {6: ("upto", {"c75": "0.3467", "c50": "1.0967", "cno": "2.5967"}),
             7: ("aft", {"c75": "Free", "c50": "0.75", "cno": "2.25"})}


def _ann_basic(n):
    when, cols = ANN_BASIC[n]

    def b(ctx):
        """Units 6 / 7 (R4, R7, R8): annuitant Basic per $1,000 of the amount at retirement, by month and column."""
        out = _columns(ctx) if ctx.of("basic") else []
        for t, x in _periods(ctx, "basic"):
            for col, rate in cols.items():
                cond = And(_ann_month(t), U(when, t), U(col, t))
                f = flat(k("pr", x), rate) if rate == "Free" else per_thousand(k("pr", x), k("amt", x), rate)
                out.append((Implies(cond, f), f"pr_{x}"))
        return out
    return b


def _u8(ctx):
    """Unit 8 (R9): premiums for life on the 50% / No Reduction column unless cancelled or a later 75% election."""
    out = []
    for col in ("r50", "rno"):
        out += both(And(pf("ann"), pf(col), Not(pf("canc")), Not(pf("s75"))), None, "life", P)
    out += both(None, And(pf("ann"), pf("canc")), "life", P)
    out += both(None, And(pf("ann"), pf("s75")), "life", P)
    return out


def _flat_row(kind, cond, lo, hi, rate, who_cond=None):
    def b(ctx):
        out = []
        for t, x in _periods(ctx, kind):
            out.append((Implies(And(cond(t), group(lo, hi)(t), None if who_cond is None else who_cond(t)),
                                flat(k("pr", x), rate)), f"pr_{x}"))
        return out
    return b


def _thousand_row(kind, cond, lo, hi, rate, extra=None):
    def b(ctx):
        out = []
        for t, x in _periods(ctx, kind):
            pre = And(cond(t), group(lo, hi)(t), None if extra is None else extra(t))
            f = flat(k("pr", x), rate) if rate == "Free" else per_thousand(k("pr", x), k("amt", x), rate)
            out.append((Implies(pre, f), f"pr_{x}"))
        return out
    return b


def _multiple_row(cond, lo, hi, rate, extra=None):
    def b(ctx):
        out = []
        for t, x in _periods(ctx, "optc"):
            ms = ctx.children(x, "mult")
            out.append((Eq(k("pr", x), Add(USD, [k("pm", m) for m in ms])), f"pr_{x}"))   # R5: per multiple
            for m in ms:
                pre = And(cond(t), group(lo, hi)(t), None if extra is None else extra(t))
                out.append((Implies(pre, flat(k("pm", m), rate)), f"pm_{m}"))
        return out
    return b


def _emp_flat_row(kind, lo, hi, bi, mo):
    def b(ctx):
        out = []
        for t, x in _periods(ctx, kind):
            g = group(lo, hi)(t)
            out.append((Implies(And(_emp(t), U("bw", t), g), flat(k("pr", x), bi)), f"pr_{x}"))
            out.append((Implies(And(_emp(t), Not(U("bw", t)), g), flat(k("pr", x), mo)), f"pr_{x}"))
        return out
    return b


def _emp_thousand_row(kind, lo, hi, bi, mo):
    def b(ctx):
        out = []
        for t, x in _periods(ctx, kind):
            g = group(lo, hi)(t)
            out.append((Implies(And(_emp(t), U("bw", t), g), per_thousand(k("pr", x), k("amt", x), bi)), f"pr_{x}"))
            out.append((Implies(And(_emp(t), Not(U("bw", t)), g), per_thousand(k("pr", x), k("amt", x), mo)), f"pr_{x}"))
        return out
    return b


def _emp_multiple_row(lo, hi, bi, mo):
    def b(ctx):
        out = []
        for t, x in _periods(ctx, "optc"):
            ms = ctx.children(x, "mult")
            out.append((Eq(k("pr", x), Add(USD, [k("pm", m) for m in ms])), f"pr_{x}"))   # R5: per multiple
            g = group(lo, hi)(t)
            for m in ms:
                out.append((Implies(And(_emp(t), U("bw", t), g), flat(k("pm", m), bi)), f"pm_{m}"))
                out.append((Implies(And(_emp(t), Not(U("bw", t)), g), flat(k("pm", m), mo)), f"pm_{m}"))
        return out
    return b


def _free(ctx):
    """'Free' (R6): a coverage costs nothing for the period exactly when its premium is $0.00."""
    out = []
    for x in ctx.of("basic") + ctx.of("opta") + ctx.of("optb") + ctx.of("optc"):
        out += both(Eq(k("pr", x), usd("0.00")), Lt(usd("0.00"), k("pr", x)), "free", x)
    return out


def _merge(*bs):
    return lambda ctx: [r for b in bs for r in b(ctx)]


def _nrpay(atom, fact, n):
    def b(ctx):
        """Units 25 / 38 (R10): an annuitant aged 65+ who elected No Reduction for the option must continue to pay."""
        out = []
        for t in ctx.of("period"):
            out += both(And(pf("ann"), pf(fact), Le(age(65), k("ag", t))), None, atom, t)
        return out
    return b


def _nothing(ctx):
    return []


# Group bounds: (lo, hi) inclusive; None = open
G = {"<35": ("<", 35), "35": (35, 39), "40": (40, 44), "45": (45, 49), "50": (50, 54), "55": (55, 59), "60": (60, 64),
     "60+": (60, None), "65+": (65, None), "65": (65, 69), "70": (70, 74), "75": (75, 79), "80+": (80, None)}
ANN_A = [(9, "<35", "0.43"), (10, "35", "0.43"), (11, "40", "0.65"), (12, "45", "1.30"), (13, "50", "2.17"),
         (14, "55", "3.90"), (15, "60", "13.00"), (16, "65+", "Free")]
ANN_B = [(17, "<35", "0.043"), (18, "35", "0.043"), (19, "40", "0.065"), (20, "45", "0.130"), (21, "50", "0.217"),
         (22, "55", "0.390"), (23, "60", "0.867")]
ANN_BNR = [(26, "65", "1.040"), (27, "70", "1.863"), (28, "75", "3.900"), (29, "80+", "6.240")]
ANN_C = [(30, "<35", "0.43"), (31, "35", "0.52"), (32, "40", "0.80"), (33, "45", "1.15"), (34, "50", "1.80"),
         (35, "55", "2.88"), (36, "60", "5.27")]
ANN_CNR = [(39, "65", "6.13"), (40, "70", "8.30"), (41, "75", "12.48"), (42, "80+", "16.90")]
EMP_A = [(45, "<35", "0.20", "0.43"), (46, "35", "0.20", "0.43"), (47, "40", "0.30", "0.65"), (48, "45", "0.60", "1.30"),
         (49, "50", "1.00", "2.17"), (50, "55", "1.80", "3.90"), (51, "60+", "6.00", "13.00")]
EMP_B = [(52, "<35", "0.02", "0.043"), (53, "35", "0.02", "0.043"), (54, "40", "0.03", "0.065"), (55, "45", "0.06", "0.130"),
         (56, "50", "0.10", "0.217"), (57, "55", "0.18", "0.390"), (58, "60", "0.40", "0.867"), (59, "65", "0.48", "1.040"),
         (60, "70", "0.86", "1.863"), (61, "75", "1.80", "3.900"), (62, "80+", "2.88", "6.240")]
EMP_C = [(63, "<35", "0.20", "0.43"), (64, "35", "0.24", "0.52"), (65, "40", "0.37", "0.80"), (66, "45", "0.53", "1.15"),
         (67, "50", "0.83", "1.80"), (68, "55", "1.33", "2.88"), (69, "60", "2.43", "5.27"), (70, "65", "2.83", "6.13"),
         (71, "70", "3.83", "8.30"), (72, "75", "5.76", "12.48"), (73, "80+", "7.80", "16.90")]

NO_OUTCOME = "other:no outcome"
UNITS = {
    0: ("RULE", _total, "no unit: the question's total premium of the named coverages (R11)"),
    1: ("PART", _u1, NO_OUTCOME, "unit 1: the rate does not change as the enrollee ages (R12) and 'per one "
        "thousand dollars' (R4) written; the parenthesis 'subject to periodic adjustments based on claims experience' and "
        "'a younger employee pays the same cost ... as a 64-year-old retiree. For example:' decide nothing for a case"),
    2: ("PART", _u2, NO_OUTCOME, "unit 2: 'pays an average cost over the term' written (R12); 'balances the premium over "
        "time, making the enrollee cost more predictable' decides nothing"),
    3: ("PART", _u3, NO_OUTCOME, "unit 3: same rate regardless of age or health status, the Extra Benefit's coverage by age "
        "and 'at no extra cost' written (R12, R13); 'younger employees may pay a comparatively higher premium than they "
        "would with coverage based ... on age' compares with a hypothetical policy and decides nothing; the amount the "
        "Extra Benefit pays (doubling, 10% a year) is no premium and no question asks it; the worked example (C5) is an "
        "illustration"),
    4: ("PART", _u4, NO_OUTCOME, "unit 4: 'the cost of this post-65 benefit is included in the FEGLI Basic level premium' "
        "written (R12); 'can be continued into retirement', 'some coverage can be continued by retirees at no cost', the "
        "net effect and the Government's share (no amount) decide no premium"),
    5: ("PART", _rates("ann"), "cross-reference", "unit 5: the annuitant rates apply from the first pay period starting "
        "on or after 2021-10-01 (R1); 'For earlier rates see our rates history pages' points outside the pinned text"),
    6: ("RULE", _ann_basic(6), "unit 6: annuitant Basic until the month after the 65th birthday (R4, R7, R8)"),
    7: ("RULE", _ann_basic(7), "unit 7: annuitant Basic from the month after the 65th birthday (R4, R7, R8)"),
    8: ("RULE", _u8, "unit 8: premiums for life unless cancelled or a later 75% Reduction election (R9)"),
}
for n, g, rate in ANN_A:
    UNITS[n] = ("RULE", _flat_row("opta", _ann_month, *G[g], rate), f"unit {n}: annuitant Option A {g} {rate} (R2, R6)")
UNITS[16] = ("RULE", _merge(UNITS[16][1], _free), UNITS[16][2] + "; 'Free' = $0.00 (R6)")
for n, g, rate in ANN_B:
    UNITS[n] = ("RULE", _thousand_row("optb", _ann_month, *G[g], rate), f"unit {n}: annuitant Option B {g} {rate} (R4)")
UNITS[24] = ("RULE", _thousand_row("optb", _ann_month, 65, None, "Free", lambda t: Not(pf("nrb"))),
             "unit 24: annuitant Option B 65+ Free unless No Reduction (R10)")
UNITS[25] = ("RULE", _nrpay("nrbpay", "nrb", 25), "unit 25: No Reduction Option B at 65+ is not free (R10)")
for n, g, rate in ANN_BNR:
    UNITS[n] = ("RULE", _thousand_row("optb", _ann_month, *G[g], rate, lambda t: U("nrbpay", t)),
                f"unit {n}: annuitant No Reduction Option B {g} {rate} (R4, R10)")
for n, g, rate in ANN_C:
    UNITS[n] = ("RULE", _multiple_row(_ann_month, *G[g], rate), f"unit {n}: annuitant Option C {g} {rate} (R5)")
UNITS[37] = ("RULE", _multiple_row(_ann_month, 65, None, "Free", lambda t: Not(pf("nrc"))),
             "unit 37: annuitant Option C 65+ Free unless No Reduction (R10)")
UNITS[38] = ("RULE", _nrpay("nrcpay", "nrc", 38), "unit 38: No Reduction Option C at 65+ is not free (R10)")
for n, g, rate in ANN_CNR:
    UNITS[n] = ("RULE", _multiple_row(_ann_month, *G[g], rate, lambda t: U("nrcpay", t)),
                f"unit {n}: annuitant No Reduction Option C {g} {rate} (R5, R10)")
UNITS[43] = ("PART", _rates("emp"), "cross-reference", "unit 43: the employee rates apply from the first pay period "
             "starting on or after 2021-10-01 (R1); 'For earlier rates see our rates history pages' points outside the "
             "pinned text")
UNITS[44] = ("RULE", _emp_thousand_row("basic", None, None, "0.1600", "0.3467"),
             "unit 44: employee Basic per $1,000 for all ages, biweekly $.1600, monthly $0.3467 (R4)")
for n, g, bi, mo in EMP_A:
    UNITS[n] = ("RULE", _emp_flat_row("opta", *G[g], bi, mo), f"unit {n}: employee Option A {g} {bi} / {mo} (R2, R6)")
for n, g, bi, mo in EMP_B:
    UNITS[n] = ("RULE", _emp_thousand_row("optb", *G[g], bi, mo), f"unit {n}: employee Option B {g} {bi} / {mo} (R4)")
for n, g, bi, mo in EMP_C:
    UNITS[n] = ("RULE", _emp_multiple_row(*G[g], bi, mo), f"unit {n}: employee Option C {g} {bi} / {mo} (R5)")
assert sorted(UNITS) == list(range(74)), sorted(set(range(74)) - set(UNITS))


def units_table(mutant=None):
    t = dict(UNITS)
    if mutant is not None:
        t = MUTANTS[mutant][1](t)
    return t


def rules(ctx, mutant=None):
    """Ground rules for a sub-case: [{"id", "unit", "formula", "defines"}]; a formula grounded by two units is kept once."""
    out, seen = [], set()
    for n, e in sorted(units_table(mutant).items()):
        if e[1] is None:
            continue
        for i, (f, target) in enumerate(e[1](ctx)):
            kk = key([f, target])
            if kk in seen:
                continue
            seen.add(kk)
            out.append({"id": f"u{n}.{i}", "unit": n, "formula": f, "defines": [] if target is None else [target]})
    return out


# --- structure helpers --------------------------------------------------------------------------------------------

def q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def is_iff(f):
    return (type(f) is list and f and f[0] == "and" and type(f[1]) is list and type(f[2]) is list
            and f[1][:1] == ["implies"] and f[2][:1] == ["implies"] and f[1][1] == f[2][2] and f[1][2] == f[2][1])


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


def environment(ctx, used=None):
    consts = {}
    for x, kind in ctx.items:
        consts[x] = {"sort": "item", "description": f"The case's {kind} {x}.", "verbalisation": f"{kind} {x}"}
    for name in sorted(used or ()):
        base, x = name.split("_", 1)
        u, w = BASES[base]
        consts[name] = {"sort": "$int", "unit": u, "description": f"{w[0].upper() + w[1:]} ({x}).",
                        "verbalisation": f"{w} ({x})"}
    preds = {n: {"arguments": ["item"], "description": d[0].upper() + d[1:] + "."} for n, d in {**FACTS, **DERIVED}.items()}
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "An enrollee, premium period, coverage or Option C multiple."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {DAY: {"scale": "1", "display": {"kind": "iso_date"}},
                      AGE: {"scale": "1", "display": {"kind": "decimal", "label": "years"}},
                      USD: {"scale": "100", "display": {"kind": "money", "currency": "USD", "input_symbol": "$"}}}}


# --- planted errors (run.py --mutants): each must change the answer of at least one question ----------------------

def _swap(n, fn):
    def apply(t):
        t = dict(t)
        e = t[n]
        t[n] = (e[0], fn(e[1]), *e[2:])
        return t
    return apply


def _json_sub(a, b):
    return lambda builder: (lambda ctx: [(json.loads(json.dumps(f).replace(a, b)), tg) for f, tg in builder(ctx)])


def _drop(builder):
    return _nothing


def _many(ns, fn):
    def apply(t):
        for n in ns:
            t = _swap(n, fn)(t)
        return t
    return apply


_UNDER35 = _json_sub('["lt", ["const", "age_year", "ag_t"], ["decimal", "age_year", "35"]]',
                     '["lt", ["const", "age_year", "ag_t"], ["decimal", "age_year", "36"]]')

MUTANTS = {
    "M1": ("TABLE: employee Option A 40-44 biweekly $0.30 read as $0.37 (the Option C cell of the same age)",
           _swap(47, _json_sub('"usd_cent", "0.30"', '"usd_cent", "0.37"'))),
    "M2": ("AGE GROUP: 'Under 35' read as 35 or under (employee Basic-free rows 45, 52, 63 and annuitant 9, 17, 30)",
           _many((9, 17, 30, 45, 52, 63), _UNDER35)),
    "M3": ("PER $1,000: employee Option B rates read per $100 (ten times)", _many(
        range(52, 63), lambda b: (lambda ctx: [(json.loads(json.dumps(f).replace('["scale", "usd_cent", "1000', '["scale", "usd_cent", "100', 1)), tg)
                                              for f, tg in b(ctx)]))),
    "M4": ("FREE: unit 25 dropped (No Reduction Option B at 65+ read as free)", lambda t: _swap(25, _drop)(
        _swap(24, lambda b: (lambda ctx: [(json.loads(json.dumps(f).replace('["not", ["unary", "nrb", ["const", "p"]]]',
                                                                         '["top"]')), tg) for f, tg in b(ctx)]))(t))),
    "M5": ("65TH BIRTHDAY: 'Until the Month after your 65th Birthday' read as before the birthday's month", lambda t: _swap(
        6, _json_sub('"upto"', '"aft"'))(_swap(7, _json_sub('"aft"', '"upto"'))(t))),
    "M6": ("DATE: 'on or after October 1, 2021' read as after it (employee and annuitant)", _many(
        (5, 43), _json_sub('["date_no_later", ["date", "2021-10-01"]', '["date_before", ["date", "2021-10-01"]'))),
    "M7": ("COLUMN: annuitant Basic from the month after 65, 50% Reduction $0.75 read as $2.25",
           _swap(7, _json_sub('["scale", "usd_cent", "75",', '["scale", "usd_cent", "225",'))),
    "M8": ("BASIC: employee biweekly $.1600 read as the monthly $0.3467",
           _swap(44, _json_sub('["scale", "usd_cent", "1600",', '["scale", "usd_cent", "3467",'))),
    "M9": ("LIFE: unit 8's 'unless you cancel' dropped", _swap(8, lambda b: (lambda ctx: [
        (json.loads(json.dumps(f).replace('["not", ["unary", "canc", ["const", "p"]]]', '["top"]')), tg)
        for f, tg in b(ctx) if json.dumps(f) != json.dumps(Implies(And(pf("ann"), pf("canc")), Not(pf("life"))))]))),
    "M10": ("SUBSEQUENT: a later 75% Reduction election ignored for the column", _many((6, 7), lambda b: _json_sub(
        '["or", ["unary", "r75", ["const", "p"]], ["unary", "s75in", ["const", "t"]]]', '["unary", "r75", ["const", "p"]]')(
        _json_sub('["and", ["unary", "rno", ["const", "p"]], ["not", ["unary", "s75in", ["const", "t"]]]]',
                  '["unary", "rno", ["const", "p"]]')(
            _json_sub('["and", ["unary", "r50", ["const", "p"]], ["not", ["unary", "s75in", ["const", "t"]]]]',
                      '["unary", "r50", ["const", "p"]]')(b))))),
    "M11": ("EXTRA BENEFIT: 'until age 45' read as until 40", _swap(3, _json_sub('["decimal", "age_year", "45"]',
                                                                             '["decimal", "age_year", "40"]'))),
    "M12": ("PER MULTIPLE: Option C read as one rate for all multiples (only the first multiple counted)", _many(
        list(range(30, 43)) + list(range(63, 74)), lambda b: (lambda ctx: [
            ((Eq(f[1], f[2][2]) if f[0] == "eq" and f[2][0] == "add" else f), tg) for f, tg in b(ctx)]))),
    "M13": ("WHO: employee Option A 60+ read as the annuitant table (65+ Free)", _swap(51, lambda b: (lambda ctx: b(ctx) + [
        (Implies(And(_emp(t), Le(age(65), k("ag", t))), flat(k("pr", x), "Free")), f"pr_{x}")
        for t, x in _periods(ctx, "opta")]))),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
