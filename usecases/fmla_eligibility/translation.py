"""FMLA eligible employee, 29 CFR 825.110 (statute corpus batch 3, law 1 of 9): the VE translation, one pass with today's language.

Row statute-corpus-fmla-eligibility (dri-statute-corpus-fmla-eligibility-1123, Opus 5.5). SAME-FAMILY. Written from the pinned
source only (manage-agents reviews/spare/statute-corpus/stock/fmla-eligibility/source.txt, sha256 701b7c47...cdaad) BEFORE the
encoder's question file was read (ISOLATION.md "Translation"). Evidence branch: nothing here is a Lean kernel line, a profile,
a refuses pair or a lint change; nothing merges.

UNITS maps each in-scope unit n of stock/fmla-eligibility/units.jsonl (tools/sample5.py --units fmla-eligibility) to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one case;
  ("PART", builder, cause, note) written except the part named in the note (bridged / stated / name / not written);
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2).
Grounding is mechanical: a rule "for every leave / period / break / block of hours" is written once per item the case names;
a sum over the employment periods (or blocks of hours) is a sum over the case's items, each item's share being its stated
number when the item counts and 0 when it does not (both written as guarded equations; an item whose share no rule fixes
leaves the sum unproved: refused). No number from a case's facts is ever put into a rule as a coefficient: every literal
below (12, 52, 84 = 7 x 12 months, 1,250, 50) is a literal of the pinned text.
Items (one sort "item"): leave items l (one per leave start asked), employment-period items s (a period of employment or of
USERRA-covered absence, with its stated count of weeks), break items b (a break in service), hour-block items h (a stated
count of hours over a stated run of days). Unary facts on items; binary facts period_for(s, l), precedes(s, b); per-item
integer constants. Durations in calendar months and the first day of the 12-month period come ONLY from the bridge script
(bridge/fmla_bridge.py; SELECTION.md: "Bridged: 12 months, 7 years, the 12-month period"); every comparison with a limit and
every sum is written here (SELECTION.md [B5]).

Readings fixed here, on the text alone (refuse when in doubt):
R1 (b)(3) second sentence deems 52 weeks equal to 12 months only "for purposes of determining whether intermittent/occasional/
   casual employment qualifies": for such employment, 12 months iff the weeks of employment total at least 52. For other
   employment the text gives two measures (weeks of employment, (b)(3) first sentence; calendar months, (a)(1)/(b)): the answer
   is given only when both agree (both at least 12 months, or both short), else refused (D1: two outcomes at once).
   Calendar months over non-consecutive periods: at least 12 when the whole months of the counted periods sum to 12 or more;
   short when the months rounded up (a part month counted whole) sum to less than 12; otherwise undetermined (refused).
R2 (b)(2)(i) second sentence ("the period of absence ... due to USERRA-covered service must be also counted"): a period of
   USERRA-covered absence counts as employment for the 12 months, whatever the length of the break (the sentence is not
   limited to breaks of more than seven years).
R3 (b)(1)/(b)(4): periods before a break of seven years or more are left out unless (b)(2) requires them or the employer's
   stated practice is to count them (the fixed fact of the test; uniformity, (b)(4) second sentence, is a duty not written).
R4 (c)(1)/(c)(3): the hours counted are the actual hours worked (FLSA principles, stated) when an accurate accounting of them
   is stated; where the employer keeps no accurate record and no accurate accounting is stated, the requirement is met unless
   the employer can clearly demonstrate the employee did not work 1,250 hours (a stated judgment).
R5 (d)/(e): the 12 months and the hours are measured as of the day the leave is to start; the employee count is the one on
   the day the employee gave notice of the need for leave (later counts do not matter).
"""
from __future__ import annotations

import hashlib
import json

DAY, NDAYS = "day", "elapsed_day"
HOURS, WEEKS, MONTHS, HEADS = "hour_count", "week_count", "month_count", "headcount"
INT_UNITS = {  # per-item integer constants: base name -> (unit, words)
    # leave items
    "start": (DAY, "the day the leave is to start"),
    "wfrom": (DAY, "the first day of the 12-month period immediately preceding the commencement of the leave (bridge)"),
    "count": (HEADS, "the number of employees employed by the employer within 75 miles of the employee's worksite on the "
                     "day the employee gave notice of the need for the leave (a stated count)"),
    "wk": (WEEKS, "the weeks of employment counted for the leave (sum over the periods)"),
    "mo": (MONTHS, "the whole calendar months of the periods counted for the leave (sum)"),
    "mu": (MONTHS, "the calendar months of the periods counted for the leave, a part month counted whole (sum)"),
    "hs": (HOURS, "the hours of service counted in the 12-month period before the leave (sum over the blocks)"),
    # period items
    "weeks": (WEEKS, "the stated number of weeks of the period"),
    "months": (MONTHS, "the whole calendar months of the period, up to the day before the leave (bridge)"),
    "monthsup": (MONTHS, "the calendar months of the period, a part month counted whole (bridge)"),
    # break items
    "bmonths": (MONTHS, "the whole calendar months of the break in service (bridge)"),
    "bdays": (NDAYS, "the days of the break in service beyond its whole calendar months (bridge)"),
    # hour blocks
    "hours": (HOURS, "the stated hours of the block"),
    "hfrom": (DAY, "the first day of the block of hours"),
    "hto": (DAY, "the last day of the block of hours"),
}
# per (item, leave) share constants: base -> (unit, words)
PAIR_UNITS = {
    "wc": (WEEKS, "the weeks the period contributes to the leave's count"),
    "mc": (MONTHS, "the whole months the period contributes"),
    "uc": (MONTHS, "the months (part month counted whole) the period contributes"),
    "hc": (HOURS, "the hours the block contributes to the leave's 12-month period"),
}
FACTS = {  # unary facts on an item (the encoder states each true or false)
    # leave items
    "employee": "the person is an employee of the employer (fixed fact: the employer is a covered employer)",
    "covered": "the employer is a covered employer (825.104, not pinned: the fixed fact of the test)",
    "casual": "the employee's employment is intermittent, occasional or casual employment",
    "practice": "the employer's practice is to count employment before a break in service of seven years or more",
    "acct": "an accurate accounting of the actual hours the employee worked under FLSA principles is stated",
    "acc_record": "the employer maintains an accurate record of the hours worked by the employee",
    "shows_below": "the employer can clearly demonstrate that the employee did not work 1,250 hours during the previous 12 "
                   "months (stated judgment)",
    # period items
    "payroll": "the employee was maintained on the payroll in each of the period's stated weeks (for any part of the week, "
               "working or on paid or unpaid leave during which other benefits or compensation were provided)",
    "userra_abs": "the period is a period of absence from work due to or necessitated by USERRA-covered service",
    # break items
    "b_userra": "the break in service is occasioned by the fulfilment of the employee's USERRA-covered service obligation",
    "b_rehire": "a written agreement, including a collective bargaining agreement, exists concerning the employer's "
                "intention to rehire the employee after the break in service",
    # hour blocks
    "h_worked": "the block's hours are hours of service the employee worked (FLSA principles)",
    "h_userra": "the block's hours are hours the employee would have worked but for USERRA-covered service (c)(2)",
}
BINARY = {
    "period_for": "(period, leave) the period is part of the employee's employment history before that leave",
    "precedes": "(period, break) the period is before that break in service",
}
STATED = ("shows_below",)
BRIDGED_CONSTS = ("wfrom", "months", "monthsup", "bmonths", "bdays")
DERIVED_UNARY = {
    "eligible": "the employee is an eligible employee for the leave (825.110(a))",
    "twelve": "the employee has been employed by the employer for at least 12 months, as of the leave's start (a)(1), (d)",
    "hrs": "the employee has been employed for at least 1,250 hours of service during the 12-month period immediately "
           "preceding the commencement of the leave (a)(2), (c), (d)",
    "site": "the employee is employed at a worksite where 50 or more employees are employed by the employer within 75 "
            "miles of that worksite, determined when the employee gave notice (a)(3), (e)",
    "seven_or_more": "the break in service is of seven years or more (b)(1)",
    "more_than_seven": "the break in service is of more than seven years (b)(2), (b)(4)",
    "must_count": "(b)(2) requires the periods before the break to be counted",
    "drops": "periods before the break are not counted (b)(1), unless (b)(2) or the employer's practice (b)(4)",
    "wkok": "the period's weeks count as weeks of employment (b)(3), or as USERRA absence (b)(2)(i)",
    "left_out": "the period is before a break whose earlier periods are not counted",
    "counted": "the period counts toward the 12 months",
}
DERIVED_BINARY = {
    "inside": "(block, leave) the block lies within the 12-month period immediately preceding the leave",
    "outside": "(block, leave) the block lies wholly outside that 12-month period",
}
SEVEN_YEARS_MONTHS = "84"  # (b)(1), (b)(2), (b)(4): seven years = 84 calendar months (the bridge gives whole months + days)


# --- formula helpers (the ve-quantity@1 wire shapes; council_tax / uc_award conventions) -------------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def B(p, x, y): return ["binary", p, c(x), c(y)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def lit(tag, v): return ["decimal", tag, v]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
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


def k(base, x):
    """Per-item integer constant."""
    return ["const", INT_UNITS[base][0], f"{base}_{x}"]


def kp(base, x, l):
    """Per (item, leave) share constant."""
    return ["const", PAIR_UNITS[base][0], f"{base}_{x}_{l}"]


def total(tag, terms):
    if not terms:
        return lit(tag, "0")
    r = terms[-1]
    for t in reversed(terms[:-1]):
        r = add(tag, t, r)
    return r


def iff_u(p, x, body): return Iff(U(p, x), body)
def iff_b(p, x, y, body): return Iff(B(p, x, y), body)


# --- the case context ---------------------------------------------------------------------------------------------

class Ctx:
    """items by kind: leaves, periods, breaks, blocks (of hours)."""

    def __init__(self, leaves=(), periods=(), breaks=(), blocks=()):
        self.leaves, self.periods, self.breaks, self.blocks = list(leaves), list(periods), list(breaks), list(blocks)

    @property
    def items(self):
        return self.leaves + self.periods + self.breaks + self.blocks


def per(kind, fn):
    return lambda ctx: [f for x in getattr(ctx, kind) for f in fn(x, ctx)]


# --- the units ----------------------------------------------------------------------------------------------------

def _u1(l, ctx):
    """(a): eligible iff an employee of a covered employer who meets (1), (2) and (3)."""
    return [iff_u("eligible", l, And(U("employee", l), U("covered", l), U("twelve", l), U("hrs", l), U("site", l)))]


def _u2(l, ctx):
    """(a)(1) with (b)(3) and reading R1: at least 12 months, as of the leave's start (the counted periods' sums)."""
    wk, mo, mu = k("wk", l), k("mo", l), k("mu", l)
    w52, m12 = lit(WEEKS, "52"), lit(MONTHS, "12")
    cas = U("casual", l)
    return [Implies(And(cas, Le(w52, wk)), U("twelve", l)),
            Implies(And(cas, Lt(wk, w52)), Not(U("twelve", l))),
            Implies(And(Not(cas), Le(w52, wk), Le(m12, mo)), U("twelve", l)),
            Implies(And(Not(cas), Lt(wk, w52), Lt(mu, m12)), Not(U("twelve", l)))]


def _u3(l, ctx):
    """(a)(2) with (c)(1)-(3) and reading R4: the hours of the blocks inside the 12-month period before the leave."""
    hs, lim = k("hs", l), lit(HOURS, "1250")
    acct, shows = U("acct", l), U("shows_below", l)
    return [Implies(And(acct, Le(lim, hs)), U("hrs", l)),
            Implies(And(acct, Lt(hs, lim)), Not(U("hrs", l))),
            Implies(And(Not(acct), Not(U("acc_record", l)), Not(shows)), U("hrs", l)),
            Implies(And(Not(acct), Not(U("acc_record", l)), shows), Not(U("hrs", l)))]


def _hours_sum(l, ctx):
    """(a)(2) "during the 12-month period immediately preceding the commencement of the leave" with (c)(1), (c)(2): the sum
    of the blocks' shares; a block inside the period gives its hours (worked, or credited for USERRA absence), a block wholly
    outside gives 0; a block across the period's edge has no share (no apportioning in the text): the sum stays unproved."""
    out = [Eq(k("hs", l), total(HOURS, [kp("hc", h, l) for h in ctx.blocks]))]
    for h in ctx.blocks:
        out += [iff_b("inside", h, l, And(no_later(k("wfrom", l), k("hfrom", h)), before(k("hto", h), k("start", l)))),
                iff_b("outside", h, l, Or(before(k("hto", h), k("wfrom", l)), no_later(k("start", l), k("hfrom", h)))),
                Implies(And(B("inside", h, l), Or(U("h_worked", h), U("h_userra", h))), Eq(kp("hc", h, l), k("hours", h))),
                Implies(Or(B("outside", h, l), And(Not(U("h_worked", h)), Not(U("h_userra", h)))),
                        Eq(kp("hc", h, l), lit(HOURS, "0")))]
    return out


def _u4(l, ctx):
    """(a)(3) with (e): 50 or more employees within 75 miles, counted on the day of the notice (a stated count)."""
    return [iff_u("site", l, Le(lit(HEADS, "50"), k("count", l)))]


def _sums(l, ctx):
    """(b) lead-in: the 12 months need not be consecutive: the counted periods' weeks / months are summed."""
    out = [Eq(k("wk", l), total(WEEKS, [kp("wc", s, l) for s in ctx.periods])),
           Eq(k("mo", l), total(MONTHS, [kp("mc", s, l) for s in ctx.periods])),
           Eq(k("mu", l), total(MONTHS, [kp("uc", s, l) for s in ctx.periods]))]
    for s in ctx.periods:
        yes = And(B("period_for", s, l), U("counted", s))
        no = Or(Not(B("period_for", s, l)), Not(U("counted", s)))
        out += [Implies(yes, Eq(kp("wc", s, l), k("weeks", s))), Implies(no, Eq(kp("wc", s, l), lit(WEEKS, "0"))),
                Implies(yes, Eq(kp("mc", s, l), k("months", s))), Implies(no, Eq(kp("mc", s, l), lit(MONTHS, "0"))),
                Implies(yes, Eq(kp("uc", s, l), k("monthsup", s))), Implies(no, Eq(kp("uc", s, l), lit(MONTHS, "0")))]
    return out


def _counted(s, ctx):
    """(b)(1)-(3): a period counts when its weeks are weeks of employment (or USERRA absence) and it is not left out."""
    bs = ctx.breaks
    return [iff_u("left_out", s, Or(*[And(B("precedes", s, b), U("drops", b)) for b in bs])),
            iff_u("counted", s, And(U("wkok", s), Not(U("left_out", s))))]


def _u6(b, ctx):
    """(b)(1): periods prior to a break of seven years or more need not be counted, subject to (b)(2); the employer's
    choice is its stated practice (R3)."""
    m84 = lit(MONTHS, SEVEN_YEARS_MONTHS)
    return [iff_u("seven_or_more", b, Le(m84, k("bmonths", b))),
            iff_u("drops", b, And(U("seven_or_more", b), Not(U("must_count", b)), *[Not(U("practice", l))
                                                                                  for l in ctx.leaves]))]


def _u7(b, ctx):
    """(b)(2): periods preceding a break of more than seven years must be counted where (i) USERRA or (ii) a written
    rehire agreement."""
    m84 = lit(MONTHS, SEVEN_YEARS_MONTHS)
    gt = Or(Lt(m84, k("bmonths", b)), And(Eq(k("bmonths", b), m84), Lt(lit(NDAYS, "0"), k("bdays", b))))
    return [iff_u("more_than_seven", b, gt),
            iff_u("must_count", b, And(U("more_than_seven", b), Or(U("b_userra", b), U("b_rehire", b))))]


def _u8(s, ctx):
    """(b)(3) first sentence (a week on the payroll for any part of it, including paid or unpaid leave with benefits, is a
    week of employment) with (b)(2)(i) second sentence (USERRA absence counted, R2)."""
    return [iff_u("wkok", s, Or(U("payroll", s), U("userra_abs", s)))]


def _cat(*builders):
    return lambda ctx: [f for b in builders for f in b(ctx)]


UNITS = {
    1: ("PART", per("leaves", _u1), "cross-reference",
        "(a) lead-in: written as the conjunction of (1)-(3); 'employee of a covered employer' (825.104, not pinned) a stated "
        "fact (the fixed fact of the test)"),
    2: ("RULE", per("leaves", _u2),
        "(a)(1): at least 12 months, with (b)(3)'s 52 weeks for casual employment and reading R1 for other employment "
        "(two measures, answered only when they agree); the months from the bridge, every sum and comparison here"),
    3: ("PART", _cat(per("leaves", _u3), per("leaves", _hours_sum)), "cross-reference",
        "(a)(2): 1,250 hours in the 12-month period immediately preceding the leave: written (blocks inside the period "
        "summed; the period's first day BRIDGED); the airline crew rule of 825.801 out (fixed fact: never applies)"),
    4: ("PART", per("leaves", _u4), "cross-reference",
        "(a)(3): 50 or more within 75 miles written over the stated count; how employees within 75 miles are counted "
        "(outside the pin) a stated fact; 'See 825.105(b)' a signpost"),
    5: ("RULE", per("leaves", _sums), "(b) lead-in: need not be consecutive: the counted periods' weeks and months summed"),
    6: ("PART", _cat(per("breaks", _u6), per("periods", _counted)), "other:norm",
        "(b)(1): 'need not be counted' is a permission to the employer: carried by the employer's stated practice (R3); "
        "seven years or more = at least 84 whole months (break length BRIDGED)"),
    7: ("PART", per("breaks", _u7), "cross-reference",
        "(b)(2): written; (i) 'USERRA-covered service obligation' (38 U.S.C. 4301) a stated fact, its second sentence "
        "written (R2, unit 8's rule), its third ('no greater entitlement than under USERRA') NOT written (USERRA not "
        "pinned); (ii) the written agreement a stated fact"),
    8: ("RULE", per("periods", _u8),
        "(b)(3): a week on the payroll for any part of it counts (the period's stated weeks); 52 weeks deemed 12 months "
        "for intermittent/occasional/casual employment (unit 2)"),
    9: ("PART", lambda ctx: [], "other:norm",
        "(b)(4): the employer's permission carried by its stated practice (unit 6's rule); 'must do so uniformly' (a duty "
        "on the employer) NOT written"),
    10: ("PART", lambda ctx: [], "cross-reference",
         "(c)(1): hours determined by FLSA principles (29 CFR part 785, not pinned): the stated hours worked are used, "
         "not records or compensation agreements (R4, unit 3's rule); 825.801 out"),
    11: ("PART", lambda ctx: [], "cross-reference",
         "(c)(2): the hours that would have been worked but for USERRA-covered service are added (blocks marked "
         "h_userra in unit 3's sum); 'USERRA-covered service' a stated fact; 'the pre-service work schedule can generally "
         "be used for calculations' NOT written (a schedule times a number of weeks is a product of two quantities)"),
    12: ("PART", lambda ctx: [], "cross-reference",
         "(c)(3): written in unit 3's rule (no accurate record: met unless the employer can clearly demonstrate it was "
         "not); 'clearly demonstrate' a stated judgment; FLSA exemptions (29 CFR part 541) and the teacher definition "
         "(825.102) not pinned (stated)"),
    13: ("PART", lambda ctx: [], "other:leave portion",
         "(d) first sentence written (every measure is as of the leave's start: unit 3's period and the periods up to "
         "the day before the leave); second sentence (the part of a non-FMLA leave after the day the employee meets "
         "the requirement is FMLA leave) NOT written: no day-by-day eligibility over a leave; 'See 825.300(b)' a "
         "signpost"),
    14: ("PART", lambda ctx: [], "other:norm",
         "(e): the count on the day of the notice decides (unit 4's rule; later changes ignored: the count is the "
         "notice-day one); 'an employer may not terminate employee leave that has already started' (a prohibition) NOT "
         "written; the August/December example is an illustration"),
}


def units_table(mutant=None):
    t = dict(UNITS)
    if mutant is not None:
        t = MUTANTS[mutant][1](t)
    return t


def rules(ctx, mutant=None):
    """Ground rules for a case: [{"id", "unit", "formula", "defines"}]."""
    out = []
    table = units_table(mutant)
    for n, e in sorted(table.items()):
        if e[1] is None:
            continue
        for i, f in enumerate(e[1](ctx)):
            for j, part in enumerate(conjuncts(f)):
                out.append({"id": f"u{n}.{i}.{j}", "unit": n, "formula": part, "defines": defines(part)})
    return out


# --- structure helpers (council_tax translation.py conventions) ---------------------------------------------------

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

def int_constants(ctx):
    """name -> (unit, words) for every integer constant of the case."""
    out = {}
    kinds = {"leaves": ("start", "wfrom", "count", "wk", "mo", "mu", "hs"), "periods": ("weeks", "months", "monthsup"),
             "breaks": ("bmonths", "bdays"), "blocks": ("hours", "hfrom", "hto")}
    for kind, bases in kinds.items():
        for x in getattr(ctx, kind):
            for base in bases:
                out[f"{base}_{x}"] = INT_UNITS[base]
    for l in ctx.leaves:
        for s in ctx.periods:
            for base in ("wc", "mc", "uc"):
                out[f"{base}_{s}_{l}"] = PAIR_UNITS[base]
        for h in ctx.blocks:
            out[f"hc_{h}_{l}"] = PAIR_UNITS["hc"]
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
            "vocabulary": {"sorts": {"item": {"description": "A leave, employment period, break in service or block of "
                                                             "hours the case names."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {DAY: {"scale": "1", "display": {"kind": "iso_date"}},
                      NDAYS: {"scale": "1", "display": {"kind": "decimal", "label": "days"}},
                      HOURS: {"scale": "100", "display": {"kind": "decimal", "label": "hours"}},
                      WEEKS: {"scale": "1", "display": {"kind": "decimal", "label": "weeks"}},
                      MONTHS: {"scale": "1", "display": {"kind": "decimal", "label": "months"}},
                      HEADS: {"scale": "1", "display": {"kind": "decimal", "label": "employees"}}}}


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


MUTANTS = {
    "M1": ("THRESHOLD: (a)(2) 1,250 hours read as 1,200", _swap(3, _wrap(_json_sub('"hour_count", "1250"',
                                                                                   '"hour_count", "1200"')))),
    "M2": ("THRESHOLD: (a)(3) 50 employees read as 51 (more than 50)", _swap(4, _wrap(_json_sub('"headcount", "50"',
                                                                                              '"headcount", "51"')))),
    "M3": ("DEEMING: (b)(3) 52 weeks = 12 months read as 53 weeks", _swap(2, _wrap(_json_sub('"week_count", "52"',
                                                                                            '"week_count", "53"')))),
    "M4": ("EXCEPTION: (b)(2) dropped (USERRA / rehire agreement no longer keeps earlier periods)",
           _swap(7, _wrap(lambda f: Iff(f[1][1], FALSE) if json.dumps(f).find('"must_count"') >= 0 else f))),
    "M5": ("EXCLUSION: (b)(1) seven years read as six (72 months)", _swap(6, _wrap(_json_sub('"month_count", "84"',
                                                                                            '"month_count", "72"')))),
    "M6": ("SUM: (b) the last period's weeks dropped from the sum", _swap(5, lambda b: _m6)),
    "M7": ("WINDOW: (a)(2) the 12-month period's first day dropped (every block before the leave counts)",
           _swap(3, lambda b: _cat(per("leaves", _u3), per("leaves", _hours_sum_m7)))),
    "M8": ("DEEMING: (b)(2)(i) the USERRA absence period not counted (R2 dropped)",
           _swap(8, _wrap(lambda f: Iff(f[1][1], U("payroll", f[1][1][2][1]))))),
    "M9": ("BURDEN: (c)(3) reversed (no accurate record: the stated judgment's polarity swapped)",
           _swap(3, lambda b: _cat(per("leaves", _u3_m9), per("leaves", _hours_sum)))),
}


def _m6(ctx):
    out = []
    for f in per("leaves", _sums)(ctx):
        if ctx.periods and f[0] == "eq" and f[1][2].startswith("wk_"):
            l = f[1][2][3:]
            f = Eq(k("wk", l), total(WEEKS, [kp("wc", s, l) for s in ctx.periods[:-1]]))
        out.append(f)
    return out


def _hours_sum_m7(l, ctx):
    out = [Eq(k("hs", l), total(HOURS, [kp("hc", h, l) for h in ctx.blocks]))]
    for h in ctx.blocks:
        out += [iff_b("inside", h, l, before(k("hto", h), k("start", l))),
                iff_b("outside", h, l, no_later(k("start", l), k("hfrom", h))),
                Implies(And(B("inside", h, l), Or(U("h_worked", h), U("h_userra", h))), Eq(kp("hc", h, l), k("hours", h))),
                Implies(Or(B("outside", h, l), And(Not(U("h_worked", h)), Not(U("h_userra", h)))),
                        Eq(kp("hc", h, l), lit(HOURS, "0")))]
    return out


def _u3_m9(l, ctx):
    hs, lim = k("hs", l), lit(HOURS, "1250")
    acct, shows = U("acct", l), U("shows_below", l)
    return [Implies(And(acct, Le(lim, hs)), U("hrs", l)),
            Implies(And(acct, Lt(hs, lim)), Not(U("hrs", l))),
            Implies(And(Not(acct), Not(U("acc_record", l)), shows), U("hrs", l)),
            Implies(And(Not(acct), Not(U("acc_record", l)), Not(shows)), Not(U("hrs", l)))]


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
