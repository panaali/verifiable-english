"""Notice of termination and redundancy pay, Fair Work Act 2009 (Cth) ss. 117, 119, 121(1), 123 (statute corpus batch 3,
law fwa-australia): the VE translation, one pass with today's language. SAME-FAMILY (Opus writer, Opus translator).

Row statute-corpus-fwa-australia (dri-statute-corpus-fwa-australia-1123, Opus 5.5). Written from the pinned source only
(manage-agents reviews/spare/statute-corpus/stock/fwa-australia/source.txt, sha256 a5b17b40...8fccb). Evidence branch:
nothing here is a Lean kernel line, a profile, a refuses pair or a lint change; nothing merges.

UNITS maps each in-scope unit n of stock/fwa-australia/units.jsonl to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one case;
  ("PART", builder, cause, note) written except the part named in the note (bridged / stated / not written);
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2 + "other:table lookup").
Every case is about ONE employee (item e) and one employer (the fixed facts of the test). No number from a case's facts
is ever put into a rule as a coefficient: every coefficient and limit below is a literal of the pinned text (the table
periods, the years of the table rows, 45 years, 2 years, 12 months as 1 year, 1 week).
Durations: a stated period of service (and the bridged age) is a pair (whole years, days beyond the whole years), as the
facts state it (WRITER-BRIEF: "years and days"); "more than N years" = y > N or (y = N and d > 0); "at least N years" =
y >= N; "less than N years" = y < N. Amounts: weeks x the stated weekly rate, the weeks a literal of the table (scale by
a literal; the "+1 week" of s. 117(3)(b) is an add of the rate once more).
"""
from __future__ import annotations

import hashlib
import json

AUD, DAY, NDAYS, YEARS, WEEKS, MINUTE = "aud_cent", "day", "elapsed_day", "year_count", "week_count", "minute_of_day"
INT_UNITS = {  # per-item integer constants: base name -> (unit, words)
    "ncy_ntc": (YEARS, "whole years of the employee's period of continuous service with the employer, other than "
                       "periods of employment as a casual employee, at the time the notice is given"),
    "ncd_ntc": (NDAYS, "days beyond those whole years, at the time the notice is given"),
    "ncy_end": (YEARS, "whole years of that period of continuous service at the end of the day the notice is given"),
    "ncd_end": (NDAYS, "days beyond those whole years, at the end of the day the notice is given"),
    "ncy_trm": (YEARS, "whole years of that period of continuous service at (immediately before) the termination"),
    "ncd_trm": (NDAYS, "days beyond those whole years, at the termination"),
    "cay": (YEARS, "whole years of the employee's periods of employment as a casual employee of the employer"),
    "cad": (NDAYS, "days beyond those whole years (casual employment)"),
    "agey": (YEARS, "the employee's age in whole years at the end of the day the notice is given (bridge only)"),
    "aged": (NDAYS, "days of age beyond those whole years (bridge only)"),
    "dn": (DAY, "the day the written notice of termination is given"),
    "dt": (DAY, "the day of the termination"),
    "cn": (MINUTE, "the clock time (minutes after midnight) at which the notice is given"),
    "ct": (MINUTE, "the clock time (minutes after midnight) at which the employment terminates"),
    "base": (AUD, "the employee's base rate of pay for his or her ordinary hours of work, per week"),
    "full": (AUD, "the employee's full rate of pay, per week"),
    "minp": (WEEKS, "the minimum period of notice (s. 117(3))"),
    "red": (AUD, "the amount of the redundancy pay (s. 119(2))"),
    "piln": (AUD, "the least payment in lieu of notice under s. 117(2)(b)"),
}
T117 = [(1, None, 1), (2, 1, 3), (3, 3, 5), (4, 5, None)]  # s. 117(3)(a): row, more than (years), not more than; period
P117 = {1: 1, 2: 2, 3: 3, 4: 4}  # weeks
T119 = [(1, 1, 2, 4), (2, 2, 3, 6), (3, 3, 4, 7), (4, 4, 5, 8), (5, 5, 6, 10), (6, 6, 7, 11), (7, 7, 8, 13),
        (8, 8, 9, 14), (9, 9, 10, 16), (10, 10, None, 12)]  # s. 119(2): row, at least, less than (years), weeks

FACTS = {  # unary facts on the employee item (the encoder states each true or false)
    "written_notice": "the employer gave the employee written notice of the day of the termination",
    "same_hours": "the employee works the same ordinary hours every week and no other hours, and would have kept "
                  "working them every week had the employment continued (stated)",
    "emp_init": "the employment is terminated at the employer's initiative",
    "not_required": "the employment is terminated because the employer no longer requires the job done by the "
                    "employee to be done by anyone",
    "turnover": "that is due to the ordinary and customary turnover of labour (stated judgment)",
    "insolv": "the employment is terminated because of the insolvency or bankruptcy of the employer",
    "sbe_ntc": "the employer is a small business employer at the time the notice is given (s. 23: stated)",
    "sbe_trm": "the employer is a small business employer immediately before the time of the termination (stated)",
    "spec_period": "the employee is employed for a specified period of time",
    "spec_task": "the employee is employed for a specified task",
    "spec_season": "the employee is employed for the duration of a specified season",
    "avoid": "a substantial reason for employing the employee as described in s. 123(1)(a) was to avoid the "
             "application of the Division (stated judgment)",
    "misconduct": "the employee's employment is terminated because of serious misconduct",
    "casual": "the employee is a casual employee",
    "training": "a training arrangement applies to the employee",
    "apprentice": "the employee is an apprentice",
    "tr_limited": "the employee's employment is, for any reason, limited to the duration of the training arrangement",
    "presc_div": "the employee is prescribed by the regulations as an employee to whom the Division does not apply",
    "presc_suba": "the employee is prescribed by the regulations as an employee to whom Subdivision A does not apply",
    "presc_subb": "the employee is prescribed by the regulations as an employee to whom Subdivision B does not apply",
    "daily_hire": "the employee is a daily hire employee",
    "weekly_hire": "the employee is a weekly hire employee",
    "bci": "the employee works in the building and construction industry",
    "bci_conn": "the employee works in connection with the erection, repair, renovation, maintenance, ornamentation "
                "or demolition of buildings or structures",
    "meat_slaughter": "the employee works in the meat industry in connection with the slaughter of livestock",
    "meat_conn": "the employee works in connection with the meat industry",
    "seasonal": "the termination of the employee's employment is determined solely by seasonal factors",
    "isrs_award": "an industry-specific redundancy scheme in a modern award applies to the employee",
    "ea_scheme": "a redundancy scheme in an enterprise agreement applies to the employee",
    "ea_incorp": "that scheme is an industry-specific redundancy scheme incorporated by reference (and as in force "
                 "from time to time) into the enterprise agreement from a modern award that is in operation",
    "ea_covered": "the employee is covered by the industry-specific redundancy scheme in the modern award",
}
STATED = ("turnover", "avoid")
BRIDGED = ("agey", "aged")
DERIVED_UNARY = {
    **{f"r117_{r}": f"under row {r} of the table in s. 117(3)(a) the period is {P117[r]} week(s)" for r, *_ in T117},
    "over45": "the employee is over 45 years old at the end of the day the notice is given",
    "plus117": "s. 117(3)(b): the period is increased by 1 week",
    **{f"r119_{r}": f"row {r} of the table in s. 119(2) applies (redundancy pay period {w} weeks)" for r, a, b, w in T119},
    "l119_a": "s. 119(1)(a) holds", "l119_b": "s. 119(1)(b) holds", "l119": "s. 119(1) holds",
    "ntc_first": "the notice of the termination as described in s. 117(1) was given before the time of the termination",
    "x121_a": "s. 121(1)(a) holds", "x121_b": "s. 121(1)(b) holds",
    "app119": "section 119 applies to the termination (s. 121(1))",
    "x123_1": "the employee is one of the employees s. 123(1) lists (read with s. 123(2))",
    "app_div": "the Division applies to the employee (s. 123(1), (2))",
    "x123_3": "the employee is one of the employees s. 123(3) lists",
    "app_suba": "Subdivision A (notice of termination) applies to the employee",
    "x123_4": "the employee is one of the employees s. 123(4) lists",
    "app_subb": "Subdivision B (redundancy pay) applies to the employee",
    "entitled": "the employee is entitled to be paid redundancy pay by the employer (s. 119)",
}


# --- formula helpers (the ve-quantity@1 wire shapes; tenant_fees / pawhp / council_tax conventions) ----------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def aud(v): return ["decimal", AUD, v]
def yrs(v): return ["decimal", YEARS, str(v)]
def days(v): return ["decimal", NDAYS, str(v)]
def wks(v): return ["decimal", WEEKS, str(v)]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def scale(tag, n, t): return ["scale", tag, str(n), t]
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


def k(base, x):
    """Per-item integer constant."""
    return ["const", INT_UNITS[base][0], f"{base}_{x}"]


def iff_u(p, x, body): return Iff(U(p, x), body)


# --- durations as (whole years, days beyond them) ------------------------------------------------------------------

def more_than(n, y, d):
    """'more than n years' for a duration of y whole years and d days."""
    return Or(Lt(yrs(n), y), And(Eq(y, yrs(n)), Lt(days(0), d)))


def at_least(n, y, d):
    return Le(yrs(n), y)


def less_than(n, y, d):
    return Lt(y, yrs(n))


# The service each section counts. s. 117(4) and s. 119(3): "continuous service with the employer does not include
# periods of employment as a casual employee": the stated service other than casual periods (units 9, 21; the
# mutants M5/M6 add the casual period back in).
def svc117(x): return k("ncy_end", x), k("ncd_end", x)
def svc119(x): return k("ncy_trm", x), k("ncd_trm", x)


# --- the case context ----------------------------------------------------------------------------------------------

class Ctx:
    def __init__(self, employee="e"):
        self.employee = employee

    @property
    def items(self):
        return [self.employee]


def per_e(fn):
    return lambda ctx: fn(ctx.employee, ctx)


def _t117_row(r, lo, hi):
    def build(x, ctx):
        y, d = svc117(x)
        cond = And(more_than(lo, y, d) if lo else None, Not(more_than(hi, y, d)) if hi else None)
        return [iff_u(f"r117_{r}", x, cond)]
    return per_e(build)


def _s117_3(x, ctx):
    """s. 117(3): first the table's period, then + 1 week under (b); the minimum period of notice is worked out for an
    employee to whom Subdivision A applies (s. 123). The amount of s. 117(2)(b) (unit 2) is written with it."""
    out = []
    for r, lo, hi in T117:
        n = P117[r]
        g = And(U("app_suba", x), U(f"r117_{r}", x))
        out.append(Implies(And(g, Not(U("plus117", x))), Eq(k("minp", x), wks(n))))
        out.append(Implies(And(g, U("plus117", x)), Eq(k("minp", x), add(WEEKS, wks(n), wks(1)))))
    return out


def _s117_2b(x, ctx):
    """s. 117(2)(b): the least payment in lieu = the full rate of pay for the hours the employee would have worked had
    the employment continued until the end of the minimum period of notice; for an employee who works the same ordinary
    hours every week (a stated fact) that is the full weekly rate for each week of the period."""
    out = []
    for r, lo, hi in T117:
        n = P117[r]
        g = And(U("app_suba", x), U("same_hours", x), U(f"r117_{r}", x))
        out.append(Implies(And(g, Not(U("plus117", x))), Eq(k("piln", x), scale(AUD, n, k("full", x)))))
        out.append(Implies(And(g, U("plus117", x)),
                           Eq(k("piln", x), add(AUD, scale(AUD, n, k("full", x)), k("full", x)))))
    return out


def _s117_3b(x, ctx):
    y, d = svc117(x)
    over45 = Or(Lt(yrs(45), k("agey", x)), And(Eq(k("agey", x), yrs(45)), Lt(days(0), k("aged", x))))
    return [iff_u("over45", x, over45), iff_u("plus117", x, And(U("over45", x), at_least(2, y, d)))]


def _s119_1(x, ctx):
    return [iff_u("l119_a", x, And(U("emp_init", x), U("not_required", x), Not(U("turnover", x)))),
            iff_u("l119_b", x, U("insolv", x)),
            iff_u("l119", x, Or(U("l119_a", x), U("l119_b", x))),
            iff_u("entitled", x, And(U("l119", x), U("app119", x), U("app_subb", x)))]


def _t119_row(r, lo, hi, w):
    def build(x, ctx):
        y, d = svc119(x)
        cond = And(at_least(lo, y, d), less_than(hi, y, d) if hi else None)
        return [iff_u(f"r119_{r}", x, cond),
                Implies(And(U("entitled", x), U(f"r119_{r}", x)), Eq(k("red", x), scale(AUD, w, k("base", x))))]
    return per_e(build)


def _s121_1(x, ctx):
    """s. 121(1): at the time notice (as in s. 117(1)) was given or immediately before the termination, whichever
    happened first; (a) less than 12 months (= 1 whole year) of continuous service other than casual periods; (b) the
    employer a small business employer (s. 23 not pinned: stated)."""
    first = And(U("written_notice", x), Or(Lt(k("dn", x), k("dt", x)),
                                           And(Eq(k("dn", x), k("dt", x)), Lt(k("cn", x), k("ct", x)))))
    f = U("ntc_first", x)
    return [iff_u("ntc_first", x, first),
            iff_u("x121_a", x, Or(And(f, less_than(1, k("ncy_ntc", x), k("ncd_ntc", x))),
                                  And(Not(f), less_than(1, k("ncy_trm", x), k("ncd_trm", x))))),
            iff_u("x121_b", x, Or(And(f, U("sbe_ntc", x)), And(Not(f), U("sbe_trm", x)))),
            iff_u("app119", x, Not(Or(U("x121_a", x), U("x121_b", x))))]


def _s123_1(x, ctx):
    """s. 123(1) read with (2): (a) unless avoiding the Division was a substantial reason; (b)-(e)."""
    a = And(Or(U("spec_period", x), U("spec_task", x), U("spec_season", x)), Not(U("avoid", x)))
    d = And(U("training", x), Not(U("apprentice", x)), Or(U("spec_period", x), U("tr_limited", x)))
    return [iff_u("x123_1", x, Or(a, U("misconduct", x), U("casual", x), d, U("presc_div", x))),
            iff_u("app_div", x, Not(U("x123_1", x)))]


def _s123_3(x, ctx):
    b = And(U("daily_hire", x), Or(U("bci", x), U("bci_conn", x)))
    cc = And(U("daily_hire", x), U("meat_slaughter", x))
    d = And(U("weekly_hire", x), U("meat_conn", x), U("seasonal", x))
    return [iff_u("x123_3", x, Or(b, cc, d, U("presc_suba", x))),
            iff_u("app_suba", x, And(U("app_div", x), Not(U("x123_3", x))))]


def _s123_4(x, ctx):
    cc = And(U("ea_scheme", x), U("ea_incorp", x), U("ea_covered", x))
    return [iff_u("x123_4", x, Or(U("apprentice", x), U("isrs_award", x), cc, U("presc_subb", x))),
            iff_u("app_subb", x, And(U("app_div", x), Not(U("x123_4", x))))]


UNITS = {
    # ---- s. 117 ----
    1: ("NOT", None, "other:norm", "s. 117(1): 'must not terminate ... unless ... written notice of the day of the "
        "termination (which cannot be before the day the notice is given)': a prohibition, not a classification. Its "
        "'notice ... as described in subsection 117(1)' is used by s. 121(1) as the stated fact written_notice"),
    2: ("PART", per_e(_s117_2b), "other:norm", "s. 117(2): the prohibition ('must not terminate unless (a) ... or "
        "(b) ...') is NOT written; the amount of (b), the least payment in lieu of notice, IS written (the full rate "
        "for the hours of the minimum period of notice = the weeks of the period x the full weekly rate, for an "
        "employee who works the same ordinary hours every week: a stated fact)"),
    3: ("RULE", per_e(_s117_3), "s. 117(3)(a): the period from the table, then (b); worked out for an employee to "
        "whom Subdivision A applies (s. 123)"),
    **{n: ("RULE", _t117_row(r, lo, hi), f"s. 117(3) table row {r}: an interval on the stated service at the end of "
           f"the day the notice is given, as the text gives it; {P117[r]} week(s)")
       for n, (r, lo, hi) in zip(range(4, 8), T117)},
    8: ("PART", per_e(_s117_3b), "date/age arithmetic", "s. 117(3)(b): 'over 45 years old' compared in Lean with the "
        "age (whole years, days) BRIDGED from the stated date of birth and the day the notice is given "
        "(bridge/age.py; the test's convention: over 45 from the day after the 45th birthday); 'completed at least 2 "
        "years of continuous service' written; '+1 week' written as an add"),
    9: ("RULE", lambda ctx: [], "s. 117(4): the service s. 117 counts is the stated service other than casual periods "
        "(used by units 4-8; mutant M5)"),
    # ---- s. 119 ----
    10: ("PART", per_e(_s119_1), "other:judgment standard", "s. 119(1): (a) and (b) written; 'due to the ordinary and "
         "customary turnover of labour' is a stated judgment; the entitlement is read with s. 121(1) and s. 123"),
    **{n: ("RULE", _t119_row(r, lo, hi, w), f"s. 119(2) table row {r}: an interval on the stated service on "
           f"termination, as the text gives it; amount = {w} x the weekly base rate (scale by the table's literal)")
       for n, (r, lo, hi, w) in zip(range(11, 21), T119)},
    21: ("RULE", lambda ctx: [], "s. 119(3): the service s. 119 counts is the stated service other than casual "
         "periods (used by units 11-20; mutant M6)"),
    # ---- s. 121 ----
    22: ("PART", per_e(_s121_1), "cross-reference", "s. 121(1): written ('whichever happened first' by the stated "
         "days and clock times; (a) '12 months' read as 1 whole year of the stated years-and-days service; (b) "
         "'small business employer' (s. 23, not pinned) a stated fact"),
    # ---- s. 123 ----
    23: ("PART", per_e(_s123_1), "cross-reference", "s. 123(1): (a)-(d) written; (e) 'prescribed by the regulations' "
         "(not pinned) a stated fact; 'serious misconduct', 'casual employee', 'training arrangement' (s. 12 "
         "definitions, not pinned) stated facts"),
    24: ("PART", lambda ctx: [], "other:judgment standard", "s. 123(2): written inside unit 23's (a); 'a substantial "
         "reason ... was to avoid the application of this Division' a stated judgment"),
    25: ("PART", per_e(_s123_3), "cross-reference", "s. 123(3): (b)-(d) written (the 'including ... buildings or "
         "structures' limb as a second fact); (e) 'prescribed by the regulations' a stated fact; 'determined solely "
         "by seasonal factors' a stated fact"),
    26: ("PART", per_e(_s123_4), "cross-reference", "s. 123(4): (a)-(c) written; (d) 'prescribed by the regulations' a "
         "stated fact; 'industry-specific redundancy scheme', 'modern award', 'enterprise agreement' (s. 12, not "
         "pinned) stated facts"),
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
    entries = [(n, e[1]) for n, e in sorted(table.items()) if e[1] is not None]
    for n, builder in entries:
        for i, f in enumerate(builder(ctx)):
            for j, part in enumerate(conjuncts(f)):
                out.append({"id": f"u{n}.{i}.{j}", "unit": n, "formula": part, "defines": defines(part)})
    return out


# --- structure helpers (tenant_fees / council_tax translation.py conventions) ------------------------------------

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

UNIT_DECL = {
    DAY: {"scale": "1", "display": {"kind": "iso_date"}},
    NDAYS: {"scale": "1", "display": {"kind": "decimal", "label": "days"}},
    YEARS: {"scale": "1", "display": {"kind": "decimal", "label": "years"}},
    WEEKS: {"scale": "1", "display": {"kind": "decimal", "label": "weeks"}},
    MINUTE: {"scale": "1", "display": {"kind": "decimal", "label": "minutes after midnight"}},
    AUD: {"scale": "100", "display": {"kind": "money", "currency": "AUD", "input_symbol": "$"}},
}


def environment(ctx):
    consts = {}
    for x in ctx.items:
        consts[x] = {"sort": "item", "description": f"The case's employee {x}.", "verbalisation": f"employee {x}"}
        for base, (u, w) in INT_UNITS.items():
            consts[f"{base}_{x}"] = {"sort": "$int", "unit": u, "description": f"{w[0].upper() + w[1:]} ({x}).",
                                     "verbalisation": f"{w} ({x})"}
    preds = {n: {"arguments": ["item"], "description": d[0].upper() + d[1:] + "."}
             for n, d in {**FACTS, **DERIVED_UNARY}.items()}
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "The employee the case names."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1", "units": UNIT_DECL}


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


def _with_casual(names_y, names_d):
    """Mutant helper: the service read WITH the casual period (s. 117(4) / s. 119(3) dropped)."""
    def walk(f):
        if type(f) is list:
            if f[:1] == ["const"] and len(f) == 3 and f[2].rsplit("_", 1)[0] in names_y:
                return add(YEARS, f, ["const", YEARS, "cay_e"])
            if f[:1] == ["const"] and len(f) == 3 and f[2].rsplit("_", 1)[0] in names_d:
                return add(NDAYS, f, ["const", NDAYS, "cad_e"])
            return [walk(g) for g in f]
        return f
    return walk


def _drop_add(f):
    """Mutant helper: ["add", tag, a, b] -> a (the '+1 week' of s. 117(3)(b) dropped)."""
    if type(f) is list:
        if f[:1] == ["add"]:
            return _drop_add(f[2])
        return [_drop_add(g) for g in f]
    return f


MUTANTS = {
    "M1": ("TABLE: s. 117(3) row 2's upper limit 3 years read as 4 years",
           _swap(5, _wrap(_json_sub('["decimal", "year_count", "3"]', '["decimal", "year_count", "4"]')))),
    "M2": ("TABLE: s. 119(2) row 10's 12 weeks read as 16 weeks (the table re-derived as increasing)",
           _swap(20, _wrap(_json_sub('"scale", "aud_cent", "12"', '"scale", "aud_cent", "16"')))),
    "M3": ("ARITHMETIC: s. 117(3)(b) '+1 week' dropped (the period and the payment in lieu not increased)",
           lambda t: _swap(2, _wrap(_drop_add))(_swap(3, _wrap(_drop_add))(t))),
    "M4": ("BOUNDARY: s. 117(3)(b) 'over 45' read as '45 or over' (the 45th birthday counted)",
           _swap(8, _wrap(_json_sub('["lt", ["decimal", "elapsed_day", "0"], ["const", "elapsed_day", "aged_e"]]',
                                    '["le", ["decimal", "elapsed_day", "0"], ["const", "elapsed_day", "aged_e"]]')))),
    "M5": ("EXCLUSION: s. 117(4) dropped (casual periods counted for the notice period)",
           lambda t: {**t, **{n: (t[n][0], (lambda b: (lambda ctx: [_with_casual({"ncy_end"}, {"ncd_end"})(f)
                                                                    for f in b(ctx)]))(t[n][1]), *t[n][2:])
                              for n in (4, 5, 6, 7, 8)}}),
    "M6": ("EXCLUSION: s. 119(3) dropped (casual periods counted for the redundancy pay period)",
           lambda t: {**t, **{n: (t[n][0], (lambda b: (lambda ctx: [_with_casual({"ncy_trm"}, {"ncd_trm"})(f)
                                                                    for f in b(ctx)]))(t[n][1]), *t[n][2:])
                              for n in range(11, 21)}}),
    "M7": ("EXCEPTION: s. 123(2) dropped (a specified-period employee always outside the Division)",
           _swap(23, _wrap(_json_sub('["not", ["unary", "avoid", ["const", "e"]]]', '["top"]')))),
    "M8": ("EXCLUSION: s. 123(4)(c)(i) dropped (any enterprise agreement redundancy scheme excludes)",
           _swap(26, _wrap(_json_sub('["unary", "ea_incorp", ["const", "e"]]', '["top"]')))),
    "M9": ("EXCEPTION: s. 119(1)(a) 'except ... ordinary and customary turnover of labour' dropped",
           _swap(10, _wrap(_json_sub('["not", ["unary", "turnover", ["const", "e"]]]', '["top"]')))),
    "M10": ("TIME: s. 121(1) 'whichever happened first' read as the time of the termination always",
            _swap(22, _wrap(_json_sub('["unary", "written_notice", ["const", "e"]]', '["bottom"]')))),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
