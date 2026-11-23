"""Canada Employment Insurance Act ss.7(1)-(2), 12(1)-(2) + Sch I, 14(1)-(4) (statute corpus batch 2, law 3): the VE
translation, one pass with today's language. SAME-FAMILY.

Row statute-corpus-ei-canada (dri-statute-corpus-ei-canada-1123, Opus 5.5). Written from the pinned source only
(manage-agents reviews/spare/statute-corpus/batch2/ei-canada/source.txt, sha256 76957f62...b0dbd2d468d0) BEFORE the
encoder's question file was opened. Evidence branch: nothing here is a Lean kernel line, a profile, a refuses pair or a
lint change.

UNITS maps each in-scope unit n of batch2/ei-canada/units.jsonl (tools/sample5.py --units ei-canada) to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one case;
  ("PART", builder, cause, note) written except the part named in the note;
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2 + "other:table lookup").
TABLE ROWS are written as the text gives them, one rule per (row, non-blank cell): a band of the regional rate (and, for
Schedule I, a band of hours) implies the row's number. No row is re-derived by a formula the text does not state.
Arithmetic is linear over integer constants on fixed grids (cents, tenths of a percent, hours, weeks); division by the
s.14(2) number N is written per row as N x wie = total (no solution off the cent grid: nothing derived). Sums over the
weeks of the qualifying period and over lay-off/separation amounts are running sums over the items the case names
(SUM); s.14(4)'s "the N weeks with the highest insurable earnings" (NEW-TOPN) is written per week as a rank count
(running count of the other weeks ranked above it) compared with N, with ties at the cut-off broken by week order: the
total does not depend on which of equal weeks is taken (encoding convention E1, stated in RESULT.md).
Vocabulary: sort item (the claimant c, the weeks w01.., the lay-off/separation amounts s1..), unary facts and derived
predicates, integer constants with units.
"""
from __future__ import annotations

import hashlib
import json

CAD, RATE, HOUR, WEEK, DAY = "cad_cent", "rate_tenth", "hour", "week_count", "day"

CASE_INTS = {  # name -> (unit, words)
    "rate": (RATE, "the regional rate of unemployment that applies to the claimant"),
    "hours": (HOUR, "the number of hours of insurable employment of the claimant in the qualifying period"),
    "reqh": (HOUR, "the number of hours of insurable employment required by the s. 7(2) table"),
    "bpstart": (DAY, "the day on which the claimant's benefit period begins"),
    "myie": (CAD, "the maximum yearly insurable earnings for the year the benefit period begins"),
    "mwie": (CAD, "the maximum weekly insurable earnings (s. 14(1.1))"),
    "maxweeks": (WEEK, "the maximum number of weeks for which benefits may be paid in the benefit period (s. 12(2))"),
    "nweeks": (WEEK, "the number of weeks determined by the s. 14(2) table"),
    "calcsum": (CAD, "the claimant's insurable earnings during the calculation period (s. 14(3)(a))"),
    "septotal": (CAD, "the insurable earnings paid or payable in the qualifying period by reason of lay-off or "
                      "separation (s. 14(3)(b))"),
    "total": (CAD, "the insurable earnings in the calculation period (s. 14(3))"),
    "wie": (CAD, "the claimant's weekly insurable earnings (s. 14(2))"),
    "wiecap": (CAD, "the weekly insurable earnings after the maximum (convention B5)"),
    "benefit": (CAD, "the rate of weekly benefits payable to the claimant (s. 14(1))"),
}
WEEK_INTS = {"earn": (CAD, "the claimant's insurable earnings in the week (lay-off/separation amounts apart)"),
             "part": (CAD, "the week's insurable earnings counted in the calculation period"),
             "acc": (CAD, "the running total of counted earnings up to and including the week"),
             "rank": (WEEK, "the number of other weeks of the qualifying period ranked above the week")}
SEP_INTS = {"sepamt": (CAD, "the lay-off or separation amount"),
            "sacc": (CAD, "the running total of lay-off or separation amounts up to and including this one")}

FACTS = {
    "insured": "is an insured person",
    "interruption": "has had an interruption of earnings from employment",
    "s23": "is paid benefits under section 23 where the maximum is set by s. 12(3)(b)(ii) (the 33% case)",
    "halfup": "the question states the half-cent-up rounding convention (no text rule; stated-judgment)",
}
DERIVED = {
    "qualifies": "qualifies under s. 7(2)",
    "payable": "unemployment benefits are payable to the person (s. 7(1))",
    "bp": "a benefit period is established for the claimant (test convention C1: if and only if s. 7(2) holds)",
    "calc": "the week is in the calculation period (s. 14(4))",
}

# s. 7(2) table (units 3-11), s. 14(2) table (units 17-25): (unit n, lower bound exclusive or None, upper inclusive or None, value)
T72 = [(3, None, "6", 700), (4, "6", "7", 665), (5, "7", "8", 630), (6, "8", "9", 595), (7, "9", "10", 560),
       (8, "10", "11", 525), (9, "11", "12", 490), (10, "12", "13", 455), (11, "13", None, 420)]
T142 = [(17, None, "6", 22), (18, "6", "7", 21), (19, "7", "8", 20), (20, "8", "9", 19), (21, "9", "10", 18),
        (22, "10", "11", 17), (23, "11", "12", 16), (24, "12", "13", 15), (25, "13", None, 14)]
# Schedule I columns: rate bands, in the order of the header line (eiact.txt:114)
SCH1_COLS = [(None, "6"), ("6", "7"), ("7", "8"), ("8", "9"), ("9", "10"), ("10", "11"), ("11", "12"), ("12", "13"),
             ("13", "14"), ("14", "15"), ("15", "16"), ("16", None)]
_B = None  # a blank cell
SCH1 = {  # unit n: (hours low, hours high or None, 12 cells) as printed (eiact.txt:115-155)
    28: (420, 454, [_B] * 8 + [26, 28, 30, 32]),
    29: (455, 489, [_B] * 7 + [24, 26, 28, 30, 32]),
    30: (490, 524, [_B] * 6 + [23, 25, 27, 29, 31, 33]),
    31: (525, 559, [_B] * 5 + [21, 23, 25, 27, 29, 31, 33]),
    32: (560, 594, [_B] * 4 + [20, 22, 24, 26, 28, 30, 32, 34]),
    33: (595, 629, [_B] * 3 + [18, 20, 22, 24, 26, 28, 30, 32, 34]),
    34: (630, 664, [_B] * 2 + [17, 19, 21, 23, 25, 27, 29, 31, 33, 35]),
    35: (665, 699, [_B] + [15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35]),
    36: (700, 734, [14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36]),
    37: (735, 769, [14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36]),
    38: (770, 804, [15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37]),
    39: (805, 839, [15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37]),
    40: (840, 874, [16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38]),
    41: (875, 909, [16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38]),
    42: (910, 944, [17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39]),
    43: (945, 979, [17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39]),
    44: (980, 1014, [18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40]),
    45: (1015, 1049, [18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40]),
    46: (1050, 1084, [19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41]),
    47: (1085, 1119, [19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41]),
    48: (1120, 1154, [20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42]),
    49: (1155, 1189, [20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42]),
    50: (1190, 1224, [21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43]),
    51: (1225, 1259, [21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43]),
    52: (1260, 1294, [22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44]),
    53: (1295, 1329, [22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44]),
    54: (1330, 1364, [23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45]),
    55: (1365, 1399, [23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45]),
    56: (1400, 1434, [24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 45]),
    57: (1435, 1469, [25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 45]),
    58: (1470, 1504, [26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 45, 45]),
    59: (1505, 1539, [27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 45, 45]),
    60: (1540, 1574, [28, 30, 32, 34, 36, 38, 40, 42, 44, 45, 45, 45]),
    61: (1575, 1609, [29, 31, 33, 35, 37, 39, 41, 43, 45, 45, 45, 45]),
    62: (1610, 1644, [30, 32, 34, 36, 38, 40, 42, 44, 45, 45, 45, 45]),
    63: (1645, 1679, [31, 33, 35, 37, 39, 41, 43, 45, 45, 45, 45, 45]),
    64: (1680, 1714, [32, 34, 36, 38, 40, 42, 44, 45, 45, 45, 45, 45]),
    65: (1715, 1749, [33, 35, 37, 39, 41, 43, 45, 45, 45, 45, 45, 45]),
    66: (1750, 1784, [34, 36, 38, 40, 42, 44, 45, 45, 45, 45, 45, 45]),
    67: (1785, 1819, [35, 37, 39, 41, 43, 45, 45, 45, 45, 45, 45, 45]),
    68: (1820, None, [36, 38, 40, 42, 44, 45, 45, 45, 45, 45, 45, 45]),
}
MAX_1997_2000 = "750.00"


# --- formula helpers (the ve-quantity@1 wire shapes; tenant_fees/translation.py conventions) ---------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def lit(unit, v): return ["decimal", unit, str(v)]
def cad(v): return lit(CAD, v)
def day(iso): return ["date", iso]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def add(tag, a, b): return ["add", tag, a, b]
def scale(tag, k, t): return ["scale", tag, str(k), t]
def k(name): return ["const", unit_of(name), name]


def And(*fs):
    fs = [f for f in fs if f is not None]
    if not fs:
        return ["true"]
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["and", f, r]
    return r


def unit_of(name):
    if name in CASE_INTS:
        return CASE_INTS[name][0]
    base = name.split("_", 1)[0]
    if base in ("ab", "gfirst", "glast", "gsize", "gabove", "weeknum"):
        return WEEK
    for table in (WEEK_INTS, SEP_INTS):
        if base in table:
            return table[base][0]
    raise KeyError(name)


def band(lo, hi, term, unit):
    """'more than lo% but not more than hi%' (lo None: 'lo% and under' / 'not more than'; hi None: 'more than lo%')."""
    return And(Lt(lit(unit, lo), term) if lo is not None else None, Le(term, lit(unit, hi)) if hi is not None else None)


def rate_band(lo, hi):
    return band(lo, hi, k("rate"), RATE)


# --- the case context -------------------------------------------------------------------------------------------

class Ctx:
    """weeks w01..; seps s1..; runs = the question's stated runs of weeks with one amount ("weeks a to b: $X each" or
    "week a: $X"), in the order stated: [(run id, [week ids])] (encoding E2)."""
    def __init__(self, weeks, seps, runs=None):
        self.weeks, self.seps = list(weeks), list(seps)
        self.runs = list(runs) if runs is not None else [(f"g{i:02d}", [w]) for i, w in enumerate(self.weeks, 1)]
        self.run_of = {w: g for g, ws in self.runs for w in ws}
        self.items = ["c"] + self.weeks + self.seps


CL = "c"


def _t72_row(n, lo, hi, v):
    return lambda ctx: [Implies(rate_band(lo, hi), Eq(k("reqh"), lit(HOUR, v)))]


def _t142_row(n, lo, hi, v):
    def build(ctx):
        b = rate_band(lo, hi)
        return [Implies(b, Eq(k("nweeks"), lit(WEEK, v))),
                Implies(And(b, Not(U("halfup", CL))), Eq(scale(CAD, v, k("wie")), k("total"))),
                # the stated half-up convention (D7; only where the question states it): benefit - 1/2 cent <=
                # 55% x total / N < benefit + 1/2 cent, times 20N (whole-number coefficients): 20N x benefit - 10N cents
                # <= 11 x total < 20N x benefit + 10N cents, below the maximum; s. 14(1) 55% with the division by N
                Implies(And(b, U("halfup", CL), Not(U("s23", CL)), Le(k("total"), scale(CAD, v, k("mwie")))),
                        And(Le(add(CAD, scale(CAD, 20 * v, k("benefit")), cad(f"-{v / 10:.2f}")),
                               scale(CAD, 11, k("total"))),
                            Lt(scale(CAD, 11, k("total")), add(CAD, scale(CAD, 20 * v, k("benefit")),
                                                                 cad(f"{v / 10:.2f}"))))),
                Implies(And(b, U("halfup", CL), Lt(scale(CAD, v, k("mwie")), k("total"))),
                        Eq(k("wiecap"), k("mwie")))]
    return build


def _sch1_row(n, lo, hi, cells):
    def build(ctx):
        hb = And(Le(lit(HOUR, lo), k("hours")), Le(k("hours"), lit(HOUR, hi)) if hi is not None else None)
        return [Implies(And(U("bp", CL), hb, rate_band(clo, chi)), Eq(k("maxweeks"), lit(WEEK, v)))
                for (clo, chi), v in zip(SCH1_COLS, cells) if v is not None]
    return build


def _rank_rules(ctx, strict=True):
    """s. 14(4): rank_w = the number of weeks ranked above week w: weeks with higher earnings, or equal earnings and an
    earlier place (tie-break E1: the total is the same for any choice among equal weeks); calc(w) iff rank_w < N.
    Grounded over the stated runs (E2: a run is "weeks a to b: $X each"; all its weeks have the run's amount, so a run is
    ranked by the earnings of its first week): gsize_g = glast_g - gfirst_g + 1; gabove_g = the total size of the runs
    ranked above run g (running count ab_g_0..); rank_w = gabove_g + (weeknum_w - gfirst_g)."""
    out = []
    R = ctx.runs
    head = {g: ws[0] for g, ws in R}
    for g, ws in R:
        out.append(Eq(k(f"gsize_{g}"), add(WEEK, add(WEEK, k(f"glast_{g}"), scale(WEEK, -1, k(f"gfirst_{g}"))), lit(WEEK, 1))))
    for i, (g, ws) in enumerate(R):
        others = [h for h, _ in R if h != g]
        out.append(Eq(k(f"ab_{g}_0"), lit(WEEK, 0)))
        for j, h in enumerate(others, 1):
            hi = [x for x, _ in R].index(h)
            above = (Le(k(f"earn_{head[g]}"), k(f"earn_{head[h]}")) if hi < i
                     else Lt(k(f"earn_{head[g]}"), k(f"earn_{head[h]}")))
            prev, cur = k(f"ab_{g}_{j - 1}"), k(f"ab_{g}_{j}")
            out.append(Implies(above, Eq(cur, add(WEEK, prev, k(f"gsize_{h}")))))
            out.append(Implies(Not(above), Eq(cur, prev)))
        out.append(Eq(k(f"gabove_{g}"), k(f"ab_{g}_{len(others)}")))
        for w in ws:
            out.append(Eq(k(f"rank_{w}"), add(WEEK, k(f"gabove_{g}"),
                                               add(WEEK, k(f"weeknum_{w}"), scale(WEEK, -1, k(f"gfirst_{g}"))))))
            out.append(Iff(U("calc", w), Lt(k(f"rank_{w}"), k("nweeks")) if strict else Le(k(f"rank_{w}"), k("nweeks"))))
    return out


def _sum_rules(ctx):
    """s. 14(3)(a): the total of the counted weeks' earnings (running sum over the weeks); (b) the lay-off/separation
    amounts (running sum over the listed amounts); s. 14(3): the total of (a) and (b)."""
    out = []
    W, S = ctx.weeks, ctx.seps
    for w in W:
        out.append(Implies(U("calc", w), Eq(k(f"part_{w}"), k(f"earn_{w}"))))
        out.append(Implies(Not(U("calc", w)), Eq(k(f"part_{w}"), cad("0.00"))))
    for i, w in enumerate(W):
        out.append(Eq(k(f"acc_{w}"), k(f"part_{w}") if i == 0 else add(CAD, k(f"acc_{W[i - 1]}"), k(f"part_{w}"))))
    out.append(Eq(k("calcsum"), k(f"acc_{W[-1]}") if W else cad("0.00")))
    return out


def _sep_rules(ctx):
    S, out = ctx.seps, []
    for i, s in enumerate(S):
        out.append(Eq(k(f"sacc_{s}"), k(f"sepamt_{s}") if i == 0 else add(CAD, k(f"sacc_{S[i - 1]}"), k(f"sepamt_{s}"))))
    out.append(Eq(k("septotal"), k(f"sacc_{S[-1]}") if S else cad("0.00")))
    return out


UNITS = {
    # ---- s. 7 ----
    1: ("RULE", lambda ctx: [Iff(U("payable", CL), And(U("insured", CL), U("qualifies", CL)))],
        "s. 7(1): payable to an insured person who qualifies (a classification; 'as provided in this Part' a signpost)"),
    2: ("RULE", lambda ctx: [Iff(U("qualifies", CL), And(U("insured", CL), U("interruption", CL),
                                                          Le(k("reqh"), k("hours"))))],
        "s. 7(2)(a)+(b): 'qualifies if' read as the whole condition (the question asks whether the person qualifies "
        "under s. 7(2)); 'at least the number of hours ... set out in the table' = reqh <= hours; the interruption "
        "of earnings and the hours are stated facts (regulations)"),
    **{n: ("RULE", _t72_row(n, lo, hi, v), f"s. 7(2) table row ({lo or ''}..{hi or ''}] -> {v} hours")
       for (n, lo, hi, v) in T72},
    # ---- s. 12 ----
    12: ("PART", lambda ctx: [], "other:norm",
         "s. 12(1): the condition 'if a benefit period has been established' is carried as the bp guard of the "
         "Schedule I rules (unit 13); 'benefits may be paid for each week of unemployment' (a permission over weeks of "
         "unemployment) is not carried and no question asks it"),
    13: ("RULE", lambda ctx: [], "s. 12(2): carried by the Schedule I row rules (units 28-68), each guarded by bp; "
                                 "'by reference to the regional rate ... and the number of hours' = the row's two bands"),
    # ---- s. 14 ----
    14: ("RULE", lambda ctx: [
        Implies(And(Not(U("s23", CL)), Not(U("halfup", CL))), Eq(scale(CAD, 100, k("benefit")), scale(CAD, 55, k("wiecap")))),
        Implies(And(U("s23", CL), Not(U("halfup", CL))), Eq(scale(CAD, 100, k("benefit")), scale(CAD, 33, k("wiecap")))),
        Implies(And(U("halfup", CL), Not(U("s23", CL)), Eq(k("wiecap"), k("mwie"))),
                And(Le(add(CAD, scale(CAD, 20, k("benefit")), cad("-0.10")), scale(CAD, 11, k("mwie"))),
                    Lt(scale(CAD, 11, k("mwie")), add(CAD, scale(CAD, 20, k("benefit")), cad("0.10")))))],
        "s. 14(1): 55% (or 33% in the s. 23 case) of weekly insurable earnings, exact on the cent grid (no rounding rule "
        "in the text); the half-up convention (D7) only where the question states it (fact halfup), written per "
        "s. 14(2) row with the division (units 17-25)"),
    15: ("PART", lambda ctx: [
        Implies(And(["date_no_later", day("1997-01-01"), k("bpstart")], ["date_no_later", k("bpstart"), day("2000-12-31")]),
                Eq(k("mwie"), cad(MAX_1997_2000))),
        Implies(["date_no_later", day("2001-01-01"), k("bpstart")], Eq(scale(CAD, 52, k("mwie")), k("myie"))),
        Implies(And(Not(U("halfup", CL)), Le(k("wie"), k("mwie"))), Eq(k("wiecap"), k("wie"))),
        Implies(And(Not(U("halfup", CL)), Lt(k("mwie"), k("wie"))), Eq(k("wiecap"), k("mwie")))],
        "other:no operative clause",
        "s. 14(1.1)(a), (b) written (the maximum: $750 for a benefit period beginning 1997-2000; MYIE / 52 written as "
        "52 x mwie = myie on the cent grid). HOW the maximum applies is not in the text: the cap on weekly insurable "
        "earnings (wiecap = the lesser) is the stated convention B5 (stated)"),
    16: ("RULE", lambda ctx: [], "s. 14(2): carried by the s. 14(2) table row rules (units 17-25): N x wie = total"),
    **{n: ("RULE", _t142_row(n, lo, hi, v), f"s. 14(2) table row ({lo or ''}..{hi or ''}] -> {v} weeks")
       for (n, lo, hi, v) in T142},
    26: ("RULE", lambda ctx: _sum_rules(ctx) + _sep_rules(ctx) + [Eq(k("total"), add(CAD, k("calcsum"), k("septotal")))],
         "s. 14(3)(a)+(b): running sums over the weeks counted (a) and over the listed lay-off/separation amounts (b); "
         "'established and calculated in accordance with the regulations' = the stated amounts; weekly earnings are "
         "stated without lay-off/separation amounts (fixed facts)"),
    27: ("RULE", _rank_rules,
         "s. 14(4): the N weeks (N from the s. 14(2) table), consecutive or not, with the highest insurable earnings: a "
         "week is in iff fewer than N weeks rank above it (ties broken by place, E1: the total is the same for any "
         "choice among equal weeks); grounded over the stated runs of weeks (E2)"),
    **{n: ("RULE", _sch1_row(n, lo, hi, cells), f"Schedule I row {lo}-{hi or ''}: {sum(v is not None for v in cells)} "
                                                    f"cells (blank cells: no rule)")
       for n, (lo, hi, cells) in SCH1.items()},
}
CONVENTIONS = {  # test conventions (the writer prompt's fixed facts), not units of the text
    "C1": (lambda ctx: [Iff(U("bp", CL), U("qualifies", CL))],
           "a benefit period is established if and only if the claimant qualifies under s. 7(2) (s. 10 not pinned)"),
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
    entries = [(n, e[1]) for n, e in sorted(table.items()) if e[0] in ("RULE", "PART") and e[1] is not None]
    entries += [(cn, fn) for cn, (fn, _) in CONVENTIONS.items()]
    for n, fn in entries:
        for i, f in enumerate(fn(ctx)):
            for j, part in enumerate(conjuncts(f)):
                out.append({"id": f"u{n}.{i}.{j}", "unit": n, "formula": part, "defines": defines(part)})
    return out


# --- structure helpers (tenant_fees translation.py conventions) ------------------------------------------------

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


def _target(t):
    if t[0] == "const" and len(t) == 3:
        return t[2]
    if t[0] == "scale" and t[3][0] == "const" and len(t[3]) == 3:
        return t[3][2]
    if t[0] == "add" and t[2][0] == "scale" and t[2][3][0] == "const":  # 2N x benefit +/- c
        return t[2][3][2]
    return None


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
    if f[0] == "eq":
        t = _target(f[1])
        if t is not None:
            return [t]
    if f[0] == "and" and f[1][0] == "le":  # the half-up pair: le(2N x benefit - c, 1.1 x total) and lt(...)
        t = _target(f[1][1])
        if t is not None:
            return [t]
    raise ValueError(f"no defined target: {f}")


# --- the environment for one case -------------------------------------------------------------------------------

def int_constants(ctx):
    """name -> (unit, words) for every integer constant of the case."""
    out = dict(CASE_INTS)
    n = len(ctx.weeks)
    for w in ctx.weeks:
        for base, (u, words) in WEEK_INTS.items():
            out[f"{base}_{w}"] = (u, f"{words} ({w})")
        out[f"weeknum_{w}"] = (WEEK, f"the number of week {w} in the qualifying period")
    for g, ws in ctx.runs:
        for base, words in (("gfirst", "the first week number of run"), ("glast", "the last week number of run"),
                            ("gsize", "the number of weeks of run"), ("gabove", "the number of weeks ranked above run")):
            out[f"{base}_{g}"] = (WEEK, f"{words} {g}")
        for j in range(len(ctx.runs)):
            out[f"ab_{g}_{j}"] = (WEEK, f"weeks of the first {j} other runs ranked above run {g}")
    for s in ctx.seps:
        for base, (u, words) in SEP_INTS.items():
            out[f"{base}_{s}"] = (u, f"{words} ({s})")
    return out


def environment(ctx):
    consts = {x: {"sort": "item", "description": f"The case's item {x}.", "verbalisation": f"item {x}"}
              for x in ctx.items}
    for name, (u, w) in int_constants(ctx).items():
        consts[name] = {"sort": "$int", "unit": u, "description": w[0].upper() + w[1:] + ".", "verbalisation": w}
    preds = {n: {"arguments": ["item"], "description": d[0].upper() + d[1:] + "."} for n, d in {**FACTS, **DERIVED}.items()}
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "The claimant, a week of the qualifying period, or a "
                                                             "lay-off or separation amount."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {"day": {"scale": "1", "display": {"kind": "iso_date"}},
                      CAD: {"scale": "100", "display": {"kind": "money", "currency": "CAD", "input_symbol": "C$"}},
                      RATE: {"scale": "10", "display": {"kind": "decimal", "label": "percent"}},
                      HOUR: {"scale": "1", "display": {"kind": "decimal", "label": "hours"}},
                      WEEK: {"scale": "1", "display": {"kind": "decimal", "label": "weeks"}}}}


# --- planted errors (run.py --mutants): each must change at least one answer ---------------------------------------

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


def _sch1_cell(n, col, new):
    lo, hi, cells = SCH1[n]
    cells = list(cells)
    cells[col] = new
    return lambda t: {**t, n: (t[n][0], _sch1_row(n, lo, hi, cells), *t[n][2:])}


MUTANTS = {
    "M1": ("TABLE: Schedule I row 700-734, column '6% and under': 14 read as 15", _sch1_cell(36, 0, 15)),
    "M2": ("TABLE: s. 7(2) table row 'more than 13%': 420 hours read as 455",
           lambda t: {**t, 11: (t[11][0], _t72_row(11, "13", None, 455), *t[11][2:])}),
    "M3": ("TABLE: s. 14(2) table row 'not more than 6%': 22 weeks read as 21",
           lambda t: {**t, 17: (t[17][0], _t142_row(17, None, "6", 21), *t[17][2:])}),
    "M4": ("ARITHMETIC: s. 14(1) 55% read as 50%",
           _swap(14, _wrap(_walk_replace(scale(CAD, 55, k("wiecap")), scale(CAD, 50, k("wiecap")))))),
    "M5": ("ARITHMETIC: s. 14(3)(b) lay-off/separation amounts dropped from the total",
           _swap(26, _wrap(_walk_replace(Eq(k("total"), add(CAD, k("calcsum"), k("septotal"))),
                                         Eq(k("total"), k("calcsum")))))),
    "M7": ("CAP: s. 14(1.1)(a) $750 read as $700",
           _swap(15, _wrap(_walk_replace(cad(MAX_1997_2000), cad("700.00"))))),
}


def _m6(t):
    return {**t, 27: (t[27][0], lambda ctx: _rank_rules(ctx, strict=False), *t[27][2:])}


MUTANTS["M6"] = ("TOP-N: s. 14(4) one week more than the table's number (rank <= N)", _m6)


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
