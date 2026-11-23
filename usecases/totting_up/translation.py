"""Disqualification for repeated offences, RTOA 1988 s.35 (statute corpus batch 3, law 6 of 9): the VE translation, one pass.

Row statute-corpus-totting-up (dri-statute-corpus-totting-up-1123, Opus 5.5). SAME-FAMILY. Written from the pinned source only
(manage-agents reviews/spare/statute-corpus/stock/totting-up/source.txt, sha256 80a88f6e...7330c) BEFORE the encoder's question
file was read (ISOLATION.md "Translation"). Evidence branch: nothing here is a Lean kernel line, a profile, a refuses pair or a
lint change; nothing merges.

UNITS maps each in-scope unit n of stock/totting-up/units.jsonl to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one case;
  ("PART", builder, cause, note) written except the part named in the note (bridged / stated / not written);
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2).
Items (one sort "item"): conviction items v (one per occasion of conviction asked about), offence items o (each offence of
which the offender is convicted on that occasion), previous-disqualification items p, circumstance items c (a circumstance
put to the court). Each o, p and c belongs to one conviction (ctx.owner). Unary facts on items; per-item and per-(item,
conviction) integer constants. The counting of previous disqualifications is a sum over the conviction's p items of a share
fixed by a guarded equation (1 when the disqualification is to be taken into account, 0 when not; a share no rule fixes
leaves the count unproved: refused). Every literal below is a literal of the pinned text (12 points, 56 days, three years,
one / more than one) or a calendar restatement of one (fixed in reading R3).
Durations: the whole calendar months and extra days from one date to another come ONLY from the bridge script
(bridge/totting_bridge.py; SELECTION.md: "dates (bridged: 'within the three years immediately preceding')"); every comparison
with a limit and every sum is written here ([B5]).

Readings fixed here, on the text alone (refuse when in doubt):
R1 (1) "must order ... unless the court is satisfied ... and thinks fit to order ... a shorter period or not to order": the
   question "must the court order" is answered yes when (1)(a) and (b) hold and the court is not satisfied of mitigating
   grounds; no when (1)(a) or (b) fails; no when the court is satisfied (the order is then the court's choice), EXCEPT where
   the case states that the satisfied court does not think fit to shorten or omit the order (the literal reading keeps the
   duty, the other does not: refused) or the stated satisfaction rests on a circumstance (4) says no account is to be taken
   of (refused: the stated judgment and (4) pull apart).
R2 (1)(a) "convicted of an offence to which this subsection applies": any offence of the occasion (with (3)); (5A) reads an
   offence committed by aiding, abetting, counselling, procuring or inciting the commission of an offence involving
   obligatory disqualification as one involving discretionary disqualification (and so not as one involving obligatory
   disqualification) for every preceding provision.
R3 (2) "for a fixed period of 56 days or more" over the period as ordered: days compared with 56; a period ordered in weeks
   with 8 weeks (= 56 days); in whole calendar months: 2 months or more is 56 days or more (any two calendar months have at
   least 59 days) and 1 month is less (at most 31 days); in years: 1 year or more is 56 days or more. An extension period
   (in days) is added to a period ordered in days; (2A) compares the period without the extension with 56 days.
R4 "within the three years immediately preceding" day E: the bridge gives the whole calendar months m and extra days d from
   the date D to the day before E (convention P of the bridge). Within iff D is before E and m < 36; not within iff D is
   after E, or m > 36, or m = 36 and d > 0; m = 36 and d = 0 (D is the same calendar date three years before E) and D = E
   are left undecided (refused).
R5 (2) "is to be taken into account if" read as the full test (only if), subject to (2A) and to (5)'s exclusions; a
   disqualification that is not for a fixed period is not to be taken into account; "previous" = imposed on the offender
   before this conviction (a stated fact).
R6 Q2 "the minimum period": 6 months / 1 year / 2 years when (1)(a) and (b) hold, by the count of previous disqualifications
   to be taken into account (0 / 1 / more than 1); "none" when (1)(a) or (b) fails (no disqualification under (1)).
R7 (4)(c) "circumstances which, within the three years immediately preceding the conviction, have been taken into account
   under that subsection in ordering the offender to be disqualified for a shorter period or not ordering him to be
   disqualified": the earlier occasion's date is compared with the conviction's date (R4); being so taken into account is
   a stated fact. Q4 "may the court take into account under (1) the circumstance": yes iff none of (4)(a)-(c) applies.
"""
from __future__ import annotations

import hashlib
import json

DAY, NDAYS = "day", "elapsed_day"
MONTHS, WEEKS, YEARS = "month_count", "week_count", "year_count"
POINTS, DCOUNT, LDAYS = "penalty_point", "disq_count", "period_day"
INT_UNITS = {  # per-item integer constants: base name -> (unit, words)
    # conviction items
    "conv": (DAY, "the date of the conviction"),
    "lo": (DAY, "the date the latest offence in respect of which penalty points are taken into account (s.29) was committed"),
    "pts": (POINTS, "the penalty points to be taken into account on the occasion (a stated number; s.29 not pinned)"),
    "cnt": (DCOUNT, "the number of previous disqualifications to be taken into account (sum of the shares)"),
    # previous-disqualification items
    "imp": (DAY, "the date the previous disqualification was imposed"),
    "based": (LDAYS, "the fixed period as ordered, in days, without any extension period"),
    "basew": (WEEKS, "the fixed period as ordered, in weeks"),
    "basem": (MONTHS, "the fixed period as ordered, in whole calendar months"),
    "basey": (YEARS, "the fixed period as ordered, in years"),
    "extd": (LDAYS, "the extension period added, in days (0 when none)"),
    "totd": (LDAYS, "the fixed period in days with the extension period added"),
    # circumstance items
    "occ": (DAY, "the date of the earlier occasion on which the circumstance was taken into account under s.35(1)"),
}
# per (item, conviction) constants: base -> (unit, words)
PAIR_UNITS = {
    "wm": (MONTHS, "whole calendar months from the previous disqualification's imposition to the day before the latest "
                   "offence (bridge)"),
    "wd": (NDAYS, "the extra days beyond those whole months (bridge)"),
    "cm": (MONTHS, "whole calendar months from the earlier occasion to the day before the conviction (bridge)"),
    "cd": (NDAYS, "the extra days beyond those whole months (bridge)"),
    "sh": (DCOUNT, "the share the previous disqualification gives the count (1 or 0)"),
}
FACTS = {  # unary facts on an item (the encoder states each true or false; a fact the case leaves open stays unknown)
    # conviction items
    "satisfied": "the court is satisfied, having regard to all the circumstances, that there are grounds for mitigating the "
                 "normal consequences of the conviction (stated judgment)",
    "declines": "the court, though so satisfied, does not think fit to order a shorter period or not to order disqualification",
    # offence items
    "disc": "the offence is an offence involving discretionary disqualification",
    "oend": "the offence is an offence involving obligatory endorsement",
    "oblig": "the offence is an offence involving obligatory disqualification",
    "s34": "an order under section 34 of this Act is made in respect of the offence",
    "aid": "the offence was committed by aiding, abetting, counselling, procuring or inciting to the commission of another "
           "offence",
    "aid_oblig": "the offence so aided, abetted, counselled, procured or incited is an offence involving obligatory "
                 "disqualification",
    # previous-disqualification items
    "prior": "the disqualification was imposed on the offender before this conviction (a previous disqualification)",
    "fixed": "the disqualification was for a fixed period",
    "in_days": "the fixed period was ordered in days",
    "in_weeks": "the fixed period was ordered in weeks",
    "in_months": "the fixed period was ordered in calendar months",
    "in_years": "the fixed period was ordered in years",
    "ext": "an extension period was added to the fixed period",
    "ext_35a": "an extension period was added pursuant to section 35A of this Act",
    "ext_35c": "an extension period was added pursuant to section 35C of this Act",
    "ext_248d": "an extension period was added pursuant to section 248D of the Criminal Procedure (Scotland) Act 1995",
    "ext_147a": "an extension period was added pursuant to section 147A of the Powers of Criminal Courts (Sentencing) Act 2000",
    "ext_166": "an extension period was added pursuant to section 166 of the Sentencing Code",
    "u_s26": "the disqualification was imposed under section 26 of this Act",
    "u_s147": "the disqualification was imposed under section 147 of the Powers of Criminal Courts (Sentencing) Act 2000",
    "u_s164": "the disqualification was imposed under section 164 of the Sentencing Code",
    "u_223a": "the disqualification was imposed under section 223A of the Criminal Procedure (Scotland) Act 1975",
    "u_436a": "the disqualification was imposed under section 436A of the Criminal Procedure (Scotland) Act 1975",
    "attempt": "the offence in respect of which the disqualification was imposed was an attempt to commit an offence",
    "o_steal": "the offence (or the offence attempted) is an offence of stealing a motor vehicle",
    "o_ta12": "the offence (or the offence attempted) is an offence under section 12 of the Theft Act 1968",
    "o_ta25": "the offence (or the offence attempted) is an offence under section 25 of the Theft Act 1968",
    "o_rta178": "the offence (or the offence attempted) is an offence under section 178 of the Road Traffic Act 1988",
    # circumstance items
    "nserious": "the circumstance is alleged to make the offence or any of the offences not a serious one (stated judgment)",
    "hardship": "the circumstance is hardship",
    "exceptional": "the hardship is exceptional hardship (stated judgment)",
    "taken": "the circumstance has been taken into account under s.35(1) on an earlier occasion in ordering the offender to "
             "be disqualified for a shorter period or not ordering him to be disqualified",
    "rests": "the court's stated satisfaction of mitigating grounds rests on this circumstance",
}
STATED = ("satisfied", "declines", "nserious", "exceptional")
BRIDGED_PAIRS = ("wm", "wd", "cm", "cd")
DERIVED_UNARY = {
    # offences
    "disc_eff": "the offence is to be treated as an offence involving discretionary disqualification ((5A) applied)",
    "oblig_eff": "the offence is an offence involving obligatory disqualification after (5A)",
    "applies": "subsection (1) applies to the offence (1A)",
    # convictions
    "s1a": "the person is convicted of an offence to which subsection (1) applies (1)(a)",
    "twelve": "the penalty points to be taken into account on the occasion number twelve or more (1)(b)",
    "trig": "(1)(a) and (1)(b) hold",
    "tainted": "the court's stated satisfaction rests on a circumstance of which (4) says no account is to be taken",
    "must_order": "the court must order the offender to be disqualified for not less than the minimum period (1)",
    "m6": "the minimum period is six months (2)(a)",
    "m1y": "the minimum period is one year (2)(b)",
    "m2y": "the minimum period is two years (2)(b)",
    "mnone": "no minimum period under (2) applies: subsection (1) does not apply on this conviction",
    # previous disqualifications
    "bge56": "the fixed period without any extension period is 56 days or more",
    "ge56": "the fixed period (with any extension period) is 56 days or more",
    "ext_named": "an extension period was added pursuant to a provision (2A)(a)-(c) names",
    "excl2a": "(2A): the period would have been less than 56 days but for an extension period added pursuant to (2A)(a)-(c)",
    "excl5": "(5): the disqualification is not a disqualification for the purposes of this section",
    "listed": "the offence (or the offence attempted) is one (5) names",
}
DERIVED_BINARY = {
    "win": "(p, v) the disqualification was imposed within the three years immediately preceding the commission of the "
           "latest offence in respect of which penalty points are taken into account (2)",
    "counts": "(p, v) the previous disqualification is to be taken into account for the purposes of (2)",
    "within3c": "(c, v) the earlier occasion was within the three years immediately preceding the conviction (4)(c)",
    "excl4": "(c, v) no account is to be taken under (1) of the circumstance (4)",
    "may_take": "(c, v) the court may take the circumstance into account under (1)",
}
THREE_YEARS_MONTHS = "36"


# --- formula helpers (the ve-quantity@1 wire shapes; council_tax / fmla_eligibility conventions) ------------------

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
    return ["const", INT_UNITS[base][0], f"{base}_{x}"]


def kp(base, x, v):
    return ["const", PAIR_UNITS[base][0], f"{base}_{x}_{v}"]


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
    """convictions; offences, prevs, circs: item -> owning conviction; tot_stated: p items whose total (with the
    extension) is the stated figure (the period without the extension is then derived, not typed)."""

    def __init__(self, convictions=(), offences=None, prevs=None, circs=None, tot_stated=()):
        self.convictions = list(convictions)
        self.offences, self.prevs, self.circs = dict(offences or {}), dict(prevs or {}), dict(circs or {})
        self.tot_stated = set(tot_stated)

    @property
    def items(self):
        return self.convictions + list(self.offences) + list(self.prevs) + list(self.circs)

    def of(self, kind, v):
        return [x for x, w in getattr(self, kind).items() if w == v]


def per(kind, fn):
    if kind == "convictions":
        return lambda ctx: [f for v in ctx.convictions for f in fn(v, ctx)]
    return lambda ctx: [f for x, v in getattr(ctx, kind).items() for f in fn(x, v, ctx)]


def _cat(*builders):
    return lambda ctx: [f for b in builders for f in b(ctx)]


# --- the units ----------------------------------------------------------------------------------------------------

def _u1(v, ctx):
    """(1) with reading R1: (a) any offence of the occasion to which (1) applies, (b) twelve or more points; the duty."""
    offs = ctx.of("offences", v)
    circs = ctx.of("circs", v)
    return [iff_u("s1a", v, Or(*[U("applies", o) for o in offs])),
            iff_u("twelve", v, Le(lit(POINTS, "12"), k("pts", v))),
            iff_u("trig", v, And(U("s1a", v), U("twelve", v))),
            iff_u("tainted", v, Or(*[And(U("rests", x), B("excl4", x, v)) for x in circs])),
            Implies(And(U("trig", v), Not(U("satisfied", v))), U("must_order", v)),
            Implies(Not(U("trig", v)), Not(U("must_order", v))),
            Implies(And(U("satisfied", v), Not(U("declines", v)), Not(U("tainted", v))), Not(U("must_order", v)))]


def _u2(o, v, ctx):
    """(1A): (a) discretionary disqualification and obligatory endorsement; (b) obligatory disqualification with no s.34
    order; read with (5A)'s deeming (unit 8's rule gives disc_eff / oblig_eff)."""
    return [iff_u("applies", o, Or(And(U("disc_eff", o), U("oend", o)),
                                   And(U("oblig_eff", o), Not(U("s34", o)))))]


def _u8(o, v, ctx):
    """(5A): an offence committed by aiding, abetting, counselling, procuring or inciting an offence involving obligatory
    disqualification: the preceding provisions apply as if it were an offence involving discretionary disqualification."""
    deemed = And(U("aid", o), U("aid_oblig", o))
    return [iff_u("disc_eff", o, Or(U("disc", o), deemed)),
            iff_u("oblig_eff", o, And(U("oblig", o), Not(deemed)))]


def _window(prefix_m, prefix_d, x, v, d_from, d_to):
    """R4: d_from within the three years immediately preceding d_to (bridged whole months and days)."""
    m, d, m36 = kp(prefix_m, x, v), kp(prefix_d, x, v), lit(MONTHS, THREE_YEARS_MONTHS)
    return (And(before(d_from, d_to), Lt(m, m36)),
            Or(before(d_to, d_from), And(before(d_from, d_to), Or(Lt(m36, m), And(Eq(m, m36), Lt(lit(NDAYS, "0"), d))))))


def _u3(v, ctx):
    """(2): the minimum period by the count of previous disqualifications to be taken into account (R5, R6)."""
    ps = ctx.of("prevs", v)
    cnt = k("cnt", v)
    out = [Eq(cnt, total(DCOUNT, [kp("sh", p, v) for p in ps])),
           iff_u("mnone", v, Not(U("trig", v))),
           iff_u("m6", v, And(U("trig", v), Lt(cnt, lit(DCOUNT, "1")))),
           iff_u("m1y", v, And(U("trig", v), Eq(cnt, lit(DCOUNT, "1")))),
           iff_u("m2y", v, And(U("trig", v), Lt(lit(DCOUNT, "1"), cnt)))]
    for p in ps:
        out += [Implies(B("counts", p, v), Eq(kp("sh", p, v), lit(DCOUNT, "1"))),
                Implies(Not(B("counts", p, v)), Eq(kp("sh", p, v), lit(DCOUNT, "0")))]
    return out


def _u3p(p, v, ctx):
    """(2) last limb (with R3, R4, R5): to be taken into account iff a previous disqualification (not excluded by (5)), for a
    fixed period of 56 days or more, imposed within the three years immediately preceding the latest offence, and not
    excluded by (2A)."""
    yes, no = _window("wm", "wd", p, v, k("imp", p), k("lo", v))
    d56 = lit(LDAYS, "56")
    out = [Implies(yes, B("win", p, v)), Implies(no, Not(B("win", p, v))),
           iff_b("counts", p, v, And(U("prior", p), Not(U("excl5", p)), U("fixed", p), U("ge56", p), B("win", p, v),
                                     Not(U("excl2a", p)))),
           iff_u("bge56", p, Or(And(U("in_days", p), Le(d56, k("based", p))),
                                And(U("in_weeks", p), Le(lit(WEEKS, "8"), k("basew", p))),
                                And(U("in_months", p), Le(lit(MONTHS, "2"), k("basem", p))),
                                And(U("in_years", p), Le(lit(YEARS, "1"), k("basey", p))))),
           Implies(U("bge56", p), U("ge56", p)),
           Implies(And(U("in_days", p), Le(d56, k("totd", p))), U("ge56", p)),
           Implies(And(U("in_days", p), Lt(k("totd", p), d56)), Not(U("ge56", p))),
           Implies(And(Not(U("ext", p)), Not(U("bge56", p))), Not(U("ge56", p)))]
    if p in ctx.tot_stated:  # the period with the extension is the stated figure: the period without it is derived
        out.append({"defines": "based_" + p, "formula": Eq(k("totd", p), add(LDAYS, k("based", p), k("extd", p)))})
    else:
        out.append(Eq(k("totd", p), add(LDAYS, k("based", p), k("extd", p))))
    return out


def _u4(p, v, ctx):
    """(2A): not to be taken into account if the fixed period would have been less than 56 days but for an extension period
    added pursuant to (a) s.35A or 35C, (b) s.248D CP(S)A 1995, (c) s.147A PCC(S)A 2000 or s.166 Sentencing Code."""
    return [iff_u("ext_named", p, Or(U("ext_35a", p), U("ext_35c", p), U("ext_248d", p), U("ext_147a", p),
                                     U("ext_166", p))),
            iff_u("excl2a", p, And(U("fixed", p), U("ext_named", p), Not(U("bge56", p))))]


def _u6(x, v, ctx):
    """(4) with R7: no account under (1) of (a) circumstances alleged to make an offence not a serious one, (b) hardship
    other than exceptional hardship, (c) circumstances taken into account under (1) within the three years immediately
    preceding the conviction in ordering a shorter period or no disqualification."""
    yes, no = _window("cm", "cd", x, v, k("occ", x), k("conv", v))
    return [Implies(yes, B("within3c", x, v)), Implies(no, Not(B("within3c", x, v))),
            iff_b("excl4", x, v, Or(U("nserious", x), And(U("hardship", x), Not(U("exceptional", x))),
                                 And(U("taken", x), B("within3c", x, v)))),
            iff_b("may_take", x, v, Not(B("excl4", x, v)))]


def _u7(p, v, ctx):
    """(5): references to disqualification do not include one imposed under s.26, s.147 PCC(S)A 2000, s.164 Sentencing
    Code, s.223A or 436A CP(S)A 1975, or in respect of stealing a motor vehicle, s.12 or 25 Theft Act 1968, s.178 RTA
    1988, or an attempt to commit such an offence."""
    named = Or(U("o_steal", p), U("o_ta12", p), U("o_ta25", p), U("o_rta178", p))
    return [iff_u("listed", p, named),
            iff_u("excl5", p, Or(U("u_s26", p), U("u_s147", p), U("u_s164", p), U("u_223a", p), U("u_436a", p),
                              And(Not(U("attempt", p)), U("listed", p)), And(U("attempt", p), U("listed", p))))]


UNITS = {
    1: ("PART", per("convictions", _u1), "cross-reference",
        "(1): written with reading R1 ((a) over the occasion's offences, (b) 12 points); 'the penalty points to be taken "
        "into account on that occasion' (s.29, not pinned) a stated number; the court's satisfaction a stated judgment; "
        "'thinks fit to order ... a shorter period or not to order' NOT written (refused where the satisfied court is "
        "stated not to think fit)"),
    2: ("PART", per("offences", _u2), "cross-reference",
        "(1A): written; whether an offence involves discretionary / obligatory disqualification or obligatory endorsement "
        "(Sch 2, not pinned) and whether a s.34 order is made: stated facts"),
    3: ("PART", _cat(per("convictions", _u3), per("prevs", _u3p)), "cross-reference",
        "(2): written (count of previous disqualifications to be taken into account; 56 days by R3); 'the latest offence "
        "in respect of which penalty points are taken into account under section 29' (not pinned) a stated fact; the "
        "three-year window's calendar months BRIDGED (R4), the comparison with 36 months here"),
    4: ("RULE", per("prevs", _u4),
        "(2A): written (the period without the extension compared with 56 days; the named provisions are the stated "
        "identities of the order)"),
    5: ("PART", lambda ctx: [], "other:norm",
        "(3)(a) 'not more than one disqualification shall be imposed' (a prohibition) and (b) 'must take into account all "
        "the offences' (a duty on the court) NOT written as norms; carried only by structure: one conviction item per "
        "occasion, (1)(a) read over all its offences (unit 1)"),
    6: ("PART", per("circs", _u6), "deadline/time limit",
        "(4): written as Q4's classification (R7); (a) 'alleged to make ... not a serious one' and (b) 'exceptional' "
        "stated judgments; (c) the three-year window's calendar months BRIDGED (R4), being taken into account on the "
        "earlier occasion a stated fact"),
    7: ("RULE", per("prevs", _u7),
        "(5): written (the provisions and offences named are the stated identities of the order and offence)"),
    8: ("RULE", per("offences", _u8),
        "(5A): the deeming written (disc_eff / oblig_eff, reading R2)"),
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
            if type(f) is dict:
                out.append({"id": f"u{n}.{i}.0", "unit": n, "formula": f["formula"], "defines": [f["defines"]]})
                continue
            for j, part in enumerate(conjuncts(f)):
                out.append({"id": f"u{n}.{i}.{j}", "unit": n, "formula": part, "defines": defines(part)})
    return out


# --- structure helpers (council_tax / fmla_eligibility translation.py conventions) -------------------------------

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
    for v in ctx.convictions:
        for base in ("conv", "lo", "pts", "cnt"):
            out[f"{base}_{v}"] = INT_UNITS[base]
    for p, v in ctx.prevs.items():
        for base in ("imp", "based", "basew", "basem", "basey", "extd", "totd"):
            out[f"{base}_{p}"] = INT_UNITS[base]
        for base in ("wm", "wd", "sh"):
            out[f"{base}_{p}_{v}"] = PAIR_UNITS[base]
    for x, v in ctx.circs.items():
        out[f"occ_{x}"] = INT_UNITS["occ"]
        for base in ("cm", "cd"):
            out[f"{base}_{x}_{v}"] = PAIR_UNITS[base]
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
                  for n, d in DERIVED_BINARY.items()})
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "A conviction, offence, previous disqualification or "
                                                             "circumstance the case names."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {DAY: {"scale": "1", "display": {"kind": "iso_date"}},
                      NDAYS: {"scale": "1", "display": {"kind": "decimal", "label": "days"}},
                      LDAYS: {"scale": "1", "display": {"kind": "decimal", "label": "days of a period"}},
                      MONTHS: {"scale": "1", "display": {"kind": "decimal", "label": "months"}},
                      WEEKS: {"scale": "1", "display": {"kind": "decimal", "label": "weeks"}},
                      YEARS: {"scale": "1", "display": {"kind": "decimal", "label": "years"}},
                      POINTS: {"scale": "1", "display": {"kind": "decimal", "label": "penalty points"}},
                      DCOUNT: {"scale": "1", "display": {"kind": "decimal", "label": "disqualifications"}}}}


# --- planted errors (run.py --mutants): each must change the answer of at least one question ----------------------

def _swap(n, fn):
    def apply(t):
        t = dict(t)
        e = t[n]
        t[n] = (e[0], fn(e[1]), *e[2:])
        return t
    return apply


def _wrap(walker):
    def w(f):
        if type(f) is dict:
            return {**f, "formula": walker(f["formula"])}
        return walker(f)
    return lambda builder: (lambda ctx: [w(f) for f in builder(ctx)])


def _json_sub(a, b):
    return lambda f: json.loads(json.dumps(f).replace(a, b))


def _drop_iff(pred, body):
    """Replace the body of the iff defining pred."""
    def walk(f):
        if is_iff(f) and f[1][1][0] in ("unary", "binary") and f[1][1][1] == pred:
            return Iff(f[1][1], body(f[1][1]))
        return f
    return walk


MUTANTS = {
    "M1": ("THRESHOLD: (1)(b) twelve points read as thirteen", _swap(1, _wrap(_json_sub('"penalty_point", "12"',
                                                                                        '"penalty_point", "13"')))),
    "M2": ("THRESHOLD: (2) 56 days read as 57 (days; weeks unchanged)",
           _swap(3, _wrap(_json_sub('"period_day", "56"', '"period_day", "57"')))),
    "M3": ("WINDOW: (2) three years read as two (24 months)",
           _swap(3, _wrap(_json_sub('"month_count", "36"', '"month_count", "24"')))),
    "M4": ("DEEMING: (5A) dropped (aiding an obligatory offence no longer treated as discretionary)",
           _swap(8, _wrap(lambda f: _drop_iff("disc_eff", lambda a: U("disc", a[2][1]))(
               _drop_iff("oblig_eff", lambda a: U("oblig", a[2][1]))(f))))),
    "M5": ("EXCLUSION: (5) dropped (every listed disqualification counts)",
           _swap(7, _wrap(_drop_iff("excl5", lambda a: FALSE)))),
    "M6": ("EXCEPTION: (2A) dropped (extension periods always count)",
           _swap(4, _wrap(_drop_iff("excl2a", lambda a: FALSE)))),
    "M7": ("COUNT: (2)(b) 'more than one' read as 'more than two'",
           _swap(3, _wrap(_drop_iff("m2y", lambda a: And(U("trig", a[2][1]),
                                                         Lt(lit(DCOUNT, "2"), k("cnt", a[2][1]))))))),
    "M8": ("CONDITION: (1A)(b) the s.34 proviso dropped",
           _swap(2, _wrap(_drop_iff("applies", lambda a: Or(And(U("disc_eff", a[2][1]), U("oend", a[2][1])),
                                                            U("oblig_eff", a[2][1])))))),
    "M9": ("EXCLUSION: (4)(b) 'other than exceptional hardship' dropped (all hardship excluded)",
           _swap(6, _wrap(lambda f: _drop_iff("excl4", lambda a: Or(
               U("nserious", a[2][1]), U("hardship", a[2][1]),
               And(U("taken", a[2][1]), B("within3c", a[2][1], a[3][1]))))(f)))),
    "M10": ("WINDOW: (4)(c) the three-year limit dropped (any earlier occasion excludes)",
            _swap(6, _wrap(lambda f: _drop_iff("excl4", lambda a: Or(
                U("nserious", a[2][1]), And(U("hardship", a[2][1]), Not(U("exceptional", a[2][1]))),
                U("taken", a[2][1])))(f)))),
    "M11": ("POLARITY: (1) the mitigating-grounds exception dropped (satisfied court still must)",
            _swap(1, lambda b: (lambda ctx: [f for f in b(ctx)
                                             if not (f[0] == "implies" and key(f).find('"satisfied"') >= 0)]
                                + [Implies(U("trig", v), U("must_order", v)) for v in ctx.convictions]))),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
