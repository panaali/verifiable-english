"""Canada Labour Code ss.183-189 (annual vacations; Justice Laws XML, pit-date 2026-10-20; statute corpus batch 4, statute,
Canada leave): the VE translation, one pass with today's language. CROSS-FAMILY questions (Codex writer), Opus translator/encoder.

Row statute-corpus-canada-vacations (dri-statute-corpus-canada-vacations-w-1124, Opus 5.5). Written from the pinned source only
(manage-agents reviews/spare/statute-corpus/batch4/canada-vacations/source.txt, sha256 14cfd15c...8799f18), the decisions D1-D13
of ISOLATION.md and the fixed facts of WRITER-BRIEF.md, BEFORE the encoder's question file (questions-enc.jsonl) was opened.
Evidence branch: nothing here is a Lean kernel line, a profile, a refuses pair or a lint change; nothing merges.

UNITS maps each in-scope unit n of batch4/canada-vacations/units.jsonl (unit 16, s.189(1.5), is OUT: META.tsv) to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one case;
  ("PART", builder, cause, note) written except the part named in the note;
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2).
Duties and permissions are carried as CLASSIFICATIONS of the stated facts (a yes/no predicate whose definition is the text's
condition: "the vacation may be taken in more than one period"); a norm that cannot be carried so is other:norm.

ONE CASE = one employee. Items (one sort "item"):
  e   the employee's employment by the (current) employer: the termination day, the amounts owed on termination, the
      completed years at termination (bridged), the rounding flag;
  y   a year of employment (in question, or a prior completed year owed on termination): its completed-years count
      (bridged), wages, vacation pay paid during it, the vacation pay paid in respect of it, the weeks, the vacation pay,
      the latest day the vacation may begin (bridged);
  v   a vacation (or one period of a vacation) of a year y: its first and last days, weeks or days taken, the written request
      and approval, whether the vacation is taken in more than one period;
  h   a general holiday of a vacation v (stated day and stated wages for it, D2);
  t   a lease/transfer or retendering between a first and a second employer (s.189).
Days are integers of the unit "day"; counts (completed years, weeks, days taken) integers of the unit "count"; money in
Canadian cents (unit "cad", scale 100). Every literal below (1, 5, 10, 2, 3, 4 weeks, 4 %, 6 %, 8 %, 30 days, 92 days) is a
literal of the pinned text or of the brief's fixed conventions (D5); no number from a case is ever a coefficient (the weeks
and days taken enter through a fixed table of literals, 1..4 weeks, 1..28 days).

THE ONE BRIDGE (bridge/bridge.py, tested; D4, D5; never the encoder; every bridged value enters as a fact marked "bridge" and
its unit is ledgered "bridged"): from stated dates only,
  ca_y / cb_y  the number of years of employment of the employer's kind completed by the last day of the year y, the year y
               itself included, 0 when y itself is not completed (it begins before the continuous employment or ends after
               the employment ended); A counts the employment by the current employer only, B also the first employer's,
               with the period between the two employers left out (s.189(1.4), applied by the arithmetic, never by the
               encoder);
  nka / nkb    the number of whole years of employment of the employer's kind completed on the termination day (A / B);
  nea / neb    the number of whole years elapsed from the start of the continuous employment to the termination day (A / B);
  lst_y        the day ten months after the last day of y (D5: the same day number, else that month's last day).
Whether A or B counts is the TEXT's question (s.189(1), (1.1), (1.2), (2)): decided in Lean (rule dc), never by the bridge.

READINGS (fixed here, on the text and the brief's fixed facts; refuse when in doubt):
R1  Completed years (units 3, 4, 5): "completed at least N (consecutive) years of employment (with the same employer)" counts
    years of employment as unit 3 defines them (the employer's kind of year), the year in respect of which the vacation is
    owed included. 184(a) "at least one year" holds when y itself is completed (cy >= 1). With deemed continuity (R7) the two
    employers are the same employer.
R2  "At least" (unit 4): every paragraph whose condition holds applies; the minimum the sections give is the greatest of them
    (10+ years: 4 weeks; 5-9: 3; 1-4: 2). This is the text's own nesting of conditions, not a choice between outcomes (D9).
    A year not completed (cy = 0): no week count ("none").
R3  Vacation pay (units 2, 5, 8): the percentage of 184.01 by the same completed years (10+: 8 %, 5-9: 6 %, else 4 %) of the
    wages during y; s.186 (deemed wages for all purposes): the vacation pay PAID during y (stated separately, D7) is part of
    y's wages. vp_y exists only for a completed year (R2).
R4  Split vacation (unit 6): more than one period is allowed iff the employee requested it in writing AND the employer
    approved it in writing.
R5  Latest start (unit 7(a)): the vacation begins in time iff its first day is on or before lst_y (bridged, D5).
    Period pay (unit 7(b)(ii)): the vacation pay of y times (the vacation taken in the period / the annual vacation the
    employee is entitled to, wk_y weeks); taken in weeks, or in days with a stated week of 5 working days or 7 days.
    Computed from the wages directly (no intermediate rounding). 7(b) "at any time prescribed by the regulations": no day.
R6  General holidays (unit 9): a holiday whose stated day is on or after the vacation's first day and on or before its last
    day "occurs during" it: the vacation may be extended (one day per holiday) and the employer must pay the holiday's
    stated wages in addition; the total of those wages is the sum over the holidays that occur.
R7  Termination (unit 10): the latest day = the day the employee ceases to be employed + 30 (D5). The amount = the vacation
    pay owing for each prior completed year (its vacation pay less what was paid in respect of it, stated) + the applicable
    percentage of the wages (with vacation pay paid during it, R3) of the completed portion of the current year in respect
    of which vacation pay has not been paid. The applicable percentage of 188(b): by the years completed on the termination
    day; when the count of years of the employer's kind (nk) and the elapsed whole years (ne) give different percentages, the
    text gives two readings: refused (no rule fires, D9). Termination on the last day of a year: that year is a prior
    completed year and there is no part ("nopart").
R8  Continuity (units 11-15, 18): s.189(1) applies iff a lease or transfer of the work, undertaking or business (sale, merger
    or otherwise) AND the employee is employed in or in connection with its operation before and after AND the work is a
    federal one (stated, or by unit 18's inclusion of a deleted / severed portion of the federal public administration) or
    becomes one due to the transfer; (1.1) iff a retendering AND the second employer becomes responsible for a federal work
    (stated) AND the employee is employed in connection with it before and after; (1.2) neither applies iff the first day of
    employment by the second employer is on or after the 92nd day after the earlier of the last day with the first employer
    and the transfer day / the second employer's first day of carrying out the work (D5). Deemed continuous = (1) or (1.1).
    (1.4) the period between the employers never counts (in B by the bridge; Q4 "no"); without (1)/(1.1) there is no
    continuous employment across the two (unit 3: "continuous employment ... by one employer"): also "no". (1.3): a period in
    which the work was not federal counts iff the work became federal due to a change in its activities.
R9  Severance (unit 17): s.189 applies to the calculation of severance pay at the second employer iff it applies at all (dc)
    and the first employer did not pay severance pay (stated).
R10 Rounding: amounts are exact in cents (D6); a case that states the half-up convention ("hu") gets the rounded value of the
    exact amount for a year's vacation pay and a period's pay; a termination total or holiday total with "hu" is refused.
"""
from __future__ import annotations

import hashlib
import json

DAY = "day"
CNT = "count"
CAD = "cad"
WEEK_OPTS = (2, 3, 4)

INT_UNITS = {  # base -> (unit, words)
    # employment e
    "td": (DAY, "the day the employee ceases to be employed"),
    "dl": (DAY, "the latest day for paying the amounts owed on termination"),
    "nka": (CNT, "the years of employment completed on the termination day, current employer only (bridged)"),
    "nkb": (CNT, "the years of employment completed on the termination day, both employers (bridged)"),
    "nea": (CNT, "the whole years elapsed to the termination day, current employer only (bridged)"),
    "neb": (CNT, "the whole years elapsed to the termination day, both employers (bridged)"),
    "nk": (CNT, "the years of employment completed on the termination day"),
    "ne": (CNT, "the whole years of continuous employment elapsed to the termination day"),
    "wt": (CAD, "the wages of the completed portion of the current year in respect of which vacation pay has not been paid"),
    "vppt": (CAD, "the vacation pay paid to the employee during that portion"),
    "bst": (CAD, "the wages of that portion for the purposes of section 184.01"),
    "pt": (CAD, "the applicable percentage of the wages of that portion"),
    "tdue": (CAD, "the amount the employer must pay on termination"),
    # year y
    "ca": (CNT, "the years of employment completed by the end of the year, current employer only (bridged)"),
    "cb": (CNT, "the years of employment completed by the end of the year, both employers (bridged)"),
    "cy": (CNT, "the years of employment completed by the end of the year"),
    "wk": (CNT, "the weeks of vacation the employee is entitled to at least, in respect of the year"),
    "wy": (CAD, "the wages during the year of employment (stated, without vacation pay)"),
    "vppy": (CAD, "the vacation pay paid to the employee during the year"),
    "bs": (CAD, "the wages during the year for the purposes of section 184.01"),
    "vp": (CAD, "the vacation pay the employee is entitled to in respect of the year"),
    "pd": (CAD, "the vacation pay paid in respect of the year"),
    "ow": (CAD, "the vacation pay owing in respect of the year"),
    "lst": (DAY, "the last day of the ten months immediately following the completion of the year (bridged)"),
    # vacation v
    "vs": (DAY, "the first day of the vacation"),
    "ve": (DAY, "the last day of the vacation"),
    "tkw": (CNT, "the weeks of vacation taken in the period"),
    "tkd": (CNT, "the days of vacation taken in the period"),
    "pp": (CAD, "the vacation pay for the period"),
    "hws": (CAD, "the wages for the general holidays occurring during the vacation"),
    # holiday h
    "hd": (DAY, "the day of the general holiday"),
    "hw": (CAD, "the wages the employee is entitled to for the general holiday (stated)"),
    "hx": (CAD, "the holiday's wages if it occurs during the vacation, else nothing"),
    # transfer t
    "l1": (DAY, "the employee's last day of employment by the first employer"),
    "xd": (DAY, "the day the work is transferred or the first day the second employer carries it out"),
    "s2": (DAY, "the employee's first day of employment by the second employer"),
    "ear": (DAY, "the earlier of the last day with the first employer and the transfer day"),
    "g92": (DAY, "the 92nd day after that earlier day"),
}
BASES_OF = {"emps": ("td", "dl", "nka", "nkb", "nea", "neb", "nk", "ne", "wt", "vppt", "bst", "pt", "tdue"),
            "years": ("ca", "cb", "cy", "wk", "wy", "vppy", "bs", "vp", "pd", "ow", "lst"),
            "vacs": ("vs", "ve", "tkw", "tkd", "pp", "hws"),
            "hols": ("hd", "hw", "hx"),
            "xfers": ("l1", "xd", "s2", "ear", "g92")}
DERIVED_CONSTS = {"dl", "nk", "ne", "bst", "pt", "tdue", "cy", "wk", "bs", "vp", "ow", "pp", "hws", "hx", "ear", "g92"}
BRIDGED = {"nka", "nkb", "nea", "neb", "ca", "cb", "lst"}
FACTS = {
    # employment
    "ceased": "the employee ceased to be employed by the employer (on the day td)",
    "hu": "the case states the convention: no rounding until the answer, the answer to the nearest cent, half up",
    "nopart": "there is no completed portion of a year of employment after the last completed year",
    "chg": "the employer's work, undertaking or business became a federal one due to a change in its activities",
    # year
    "owe": "the year is a prior completed year whose vacation pay is asked on termination",
    # vacation
    "multi": "the vacation is taken in more than one period",
    "reqw": "the employee made a request in writing to take the vacation in more than one period",
    "aprw": "the employer approved that request in writing",
    "wd5": "a week of vacation is stated as five working days",
    "wd7": "a week of vacation is stated as seven days",
    # transfer
    "lease": "the work, undertaking or business (or part) was leased or transferred from the first to the second employer "
             "by sale, merger or otherwise",
    "retender": "due to a contract awarded through a retendering process, the second employer became responsible for carrying "
                "out a work, undertaking or business (or part) previously carried out by the first employer",
    "conn": "the employee is employed in or in connection with the operation of the work, undertaking or business before and "
            "after the lease, transfer or retendering",
    "fedb": "the work, undertaking or business is a federal work, undertaking or business (stated)",
    "becfed": "the work, undertaking or business becomes a federal one due to the lease or transfer (stated)",
    "sch145": "the portion of the federal public administration was specified in Schedule I, IV or V to the Financial "
              "Administration Act",
    "deleted": "the portion was deleted from that Schedule",
    "inclp": "the portion was included in a portion of the federal public administration so specified",
    "severed": "the portion was severed from the portion in which it was included",
    "estcorp": "the portion is established as or becomes a part of a corporation or federal work, undertaking or business to "
               "which Part III applies",
    "sevpaid": "the first employer paid the employee severance pay in respect of the employment by it",
}
DERIVED_UNARY = {
    "done": "the year of employment is completed",
    "vpw": "vacation pay is deemed to be wages for all purposes",
    "nfinc": "the period in which the work was not federal is included in the period of continuous employment",
    "splitok": "the vacation may be taken in more than one period",
    "startok": "the vacation begins within the ten months immediately following the completion of the year",
    "hin": "the general holiday occurs during the vacation",
    "ext": "the vacation may be extended by one day for each general holiday occurring during it",
    "hwp": "the employer must pay the wages for the general holidays occurring during the vacation in addition to the "
           "vacation pay",
    "fed": "the work, undertaking or business is a federal work, undertaking or business for the purposes of s.189(1)",
    "late": "the first day of employment by the second employer is more than 13 weeks after the earlier day of s.189(1.2)",
    "dc1": "section 189(1) deems the employment continuous with one employer",
    "dc11": "section 189(1.1) deems the employee continuously employed with one employer",
    "dc": "the employment by the two employers is deemed continuous",
    "gapcnt": "the period between the employment by the first and by the second employer counts in the period of continuous "
              "employment",
    "sevapp": "section 189 applies in respect of the calculation of severance pay at the second employer",
}


# --- formula helpers (ve-quantity@1 wire shapes; hipaa_breach_notice / sick_pay conventions) -------------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def no_later(a, b): return ["date_no_later", a, b]
def shift(a, b, n): return ["shift_days", a, b, str(n)]       # a is n days after b
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def Eq(a, b): return ["eq", a, b]
def cnt(v): return ["decimal", CNT, str(v)]
def cad(v): return ["decimal", CAD, v]
def scale(kk, t, unit=CAD): return ["scale", unit, str(kk), t]
def add(a, b, unit=CAD): return ["add", unit, a, b]
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


def iff_u(p, x, body): return Iff(U(p, x), body)
def yes(cond, p, x): return Implies(cond, U(p, x))
def no(cond, p, x): return Implies(cond, Not(U(p, x)))


def add_all(terms, unit=CAD):
    r = terms[-1]
    for t in reversed(terms[:-1]):
        r = ["add", unit, t, r]
    return r


def band(n, lo, hi=None):
    """lo <= n (< hi)."""
    return And(Le(cnt(lo), n), Lt(n, cnt(hi)) if hi is not None else None)


BANDS = ((1, 5, 2, 4), (5, 10, 3, 6), (10, None, 4, 8))   # (from, below, weeks, percent): R2, R3


def _amount(target, mul, div, base, cond, hu_atom):
    """R10: div x target = mul x base (exact, when not hu); with hu: div x target - div/2 cent <= mul x base < div x target +
    div/2 cent (half up). mul, div: literals of the text (percent, weeks or days taken, 100 x weeks entitled)."""
    lhs, rhs = scale(div, target), scale(mul, base)
    half = f"{div / 200:.2f}"      # div/2 cents, in dollars
    out = [Implies(And(cond, Not(hu_atom)), Eq(lhs, rhs))]
    if hu_atom is not None:
        out.append(Implies(And(cond, hu_atom), Le(add(lhs, cad("-" + half)), rhs)))
        out.append(Implies(And(cond, hu_atom), Lt(rhs, add(lhs, cad(half)))))
    return out


# --- the case context ---------------------------------------------------------------------------------------------

class Ctx:
    """emps: [e]; years: {y: e}; vacs: {v: y}; hols: {h: v}; xfers: {t: e} (at most one transfer per employment)."""
    KINDS = ("years", "vacs", "hols", "xfers")

    def __init__(self, emps=("e",), years=None, vacs=None, hols=None, xfers=None):
        self.emps = list(emps)
        self.years, self.vacs, self.hols, self.xfers = dict(years or {}), dict(vacs or {}), dict(hols or {}), dict(xfers or {})

    @property
    def items(self):
        return self.emps + [x for kd in self.KINDS for x in getattr(self, kd)]

    def of(self, kind, i):
        return [x for x, j in getattr(self, kind).items() if j == i]

    def xfer_of(self, e):
        ts = self.of("xfers", e)
        return ts[0] if ts else None

    def emp_of_year(self, y):
        return self.years[y]


def per_emp(fn):
    return lambda ctx: [f for e in ctx.emps for f in fn(e, ctx)]


def per(kind, fn):
    return lambda ctx: [f for x, i in getattr(ctx, kind).items() for f in fn(x, i, ctx)]


# --- the units ----------------------------------------------------------------------------------------------------

def _pick(target, a, b, t):
    """R8 / bridge: the count with both employers (B) when the employment is deemed continuous, else the current one (A)."""
    if t is None:
        return [Eq(target, a)]
    return [Implies(U("dc", t), Eq(target, b)), Implies(Not(U("dc", t)), Eq(target, a))]


def _cy(y, e, ctx):
    """Unit 3 (R1, bridge): the years of employment completed by the end of y; y completed."""
    t = ctx.xfer_of(e)
    return _pick(k("cy", y), k("ca", y), k("cb", y), t) + [iff_u("done", y, Le(cnt(1), k("cy", y)))]


def _weeks(y, e, ctx):
    """Unit 4 (R1, R2): at least two / three / four weeks."""
    return [Implies(And(U("done", y), band(k("cy", y), lo, hi)), Eq(k("wk", y), cnt(w))) for lo, hi, w, _ in BANDS]


def _vp(y, e, ctx):
    """Units 2, 5 (R3): 4 / 6 / 8 % of the year's wages (the s.186 base)."""
    out = []
    for lo, hi, _, pct in BANDS:
        out += _amount(k("vp", y), pct, 100, k("bs", y), And(U("done", y), band(k("cy", y), lo, hi)), U("hu", e))
    return out


def _deemed_y(y, e, ctx):
    """Unit 8 (R3, D7): vacation pay paid during the year is part of its wages."""
    return [Eq(k("bs", y), add(k("wy", y), k("vppy", y)))]


def _deemed_e(e, ctx):
    return [U("vpw", e), Eq(k("bst", e), add(k("wt", e), k("vppt", e)))]


def _split(v, y, ctx):
    """Unit 6 (R4): one period, or more than one on a written request approved in writing."""
    return [iff_u("splitok", v, And(U("reqw", v), U("aprw", v)))]


def _start(v, y, ctx):
    """Unit 7(a) (R5): begins not later than ten months after the completion of the year (bridged lst_y)."""
    return [iff_u("startok", v, no_later(k("vs", v), k("lst", y)))]


def _pp(v, y, ctx):
    """Unit 7(b)(ii) (R5): the proportion of the vacation pay that the vacation taken is of the annual vacation; from the
    wages directly (percent x taken / (100 x entitled)), a fixed table of literals."""
    e = ctx.emp_of_year(y)
    out = []
    for lo, hi, w, pct in BANDS:
        cond_y = And(U("done", y), band(k("cy", y), lo, hi), U("multi", v))
        for t in range(1, w + 1):
            out += _amount(k("pp", v), pct * t, 100 * w, k("bs", y), And(cond_y, Eq(k("tkw", v), cnt(t))), U("hu", e))
        for per_week, flag in ((5, "wd5"), (7, "wd7")):
            for d in range(1, per_week * w + 1):
                out += _amount(k("pp", v), pct * d, 100 * per_week * w, k("bs", y),
                               And(cond_y, U(flag, v), Eq(k("tkd", v), cnt(d))), U("hu", e))
    return out


def _hol(h, v, ctx):
    """Unit 9 (R6): the holiday occurs during the vacation; its wages counted if so."""
    inn = U("hin", h)
    return [iff_u("hin", h, And(no_later(k("vs", v), k("hd", h)), no_later(k("hd", h), k("ve", v)))),
            Implies(inn, Eq(k("hx", h), k("hw", h))), Implies(Not(inn), Eq(k("hx", h), cad("0.00")))]


def _hol_v(v, y, ctx):
    hs = ctx.of("hols", v)
    any_in = Or(*[U("hin", h) for h in hs])
    out = [iff_u("ext", v, any_in), iff_u("hwp", v, any_in)]
    if hs:
        e = ctx.emp_of_year(y)
        out.append(Implies(Not(U("hu", e)), Eq(k("hws", v), add_all([k("hx", h) for h in hs]))))
    return out


def _term(e, ctx):
    """Unit 10 (R7): within 30 days after ceasing to be employed; (a) owing for prior completed years; (b) the applicable
    percentage of the completed portion's wages."""
    t = ctx.xfer_of(e)
    out = [shift(k("dl", e), k("td", e), 30)]
    out += _pick(k("nk", e), k("nka", e), k("nkb", e), t)
    out += _pick(k("ne", e), k("nea", e), k("neb", e), t)
    hu = U("hu", e)
    for lo, hi, _, pct in ((0, 5, 0, 4), (5, 10, 0, 6), (10, None, 0, 8)):
        both = And(band(k("nk", e), lo, hi), band(k("ne", e), lo, hi))
        out.append(Implies(And(U("ceased", e), Not(U("nopart", e)), Not(hu), both),
                           Eq(scale(100, k("pt", e)), scale(pct, k("bst", e)))))
    out.append(Implies(And(U("ceased", e), U("nopart", e)), Eq(k("pt", e), cad("0.00"))))
    owed = [y for y in ctx.of("years", e)]
    terms = [k("ow", y) for y in owed] + [k("pt", e)]
    out.append(Implies(And(U("ceased", e), Not(hu)), Eq(k("tdue", e), add_all(terms))))
    return out


def _owing(y, e, ctx):
    """Unit 10(a) (R7): the vacation pay owing for a prior completed year: its vacation pay less what was paid for it; a year
    the case does not ask about on termination owes nothing to the total."""
    return [Implies(U("owe", y), Eq(k("ow", y), add(k("vp", y), scale(-1, k("pd", y))))),
            Implies(Not(U("owe", y)), Eq(k("ow", y), cad("0.00")))]


def _fed(t, e, ctx):
    """Unit 18 (R8): a federal work, undertaking or business includes a deleted portion of a Schedule I, IV or V portion, or a
    severed portion included in one, established as or becoming part of a corporation or federal work (for s.189(1))."""
    return [iff_u("fed", t, Or(U("fedb", t),
                               And(U("sch145", t), U("deleted", t), U("estcorp", t)),
                               And(U("inclp", t), U("severed", t), U("estcorp", t))))]


def _late(t, e, ctx):
    """Unit 13 (R8, D5): more than 13 weeks after the earlier of the two days = on or after the 92nd day after it."""
    l1, xd, ear = k("l1", t), k("xd", t), k("ear", t)
    return [Implies(no_later(l1, xd), Eq(ear, l1)), Implies(no_later(xd, l1), Eq(ear, xd)),
            shift(k("g92", t), ear, 92),
            iff_u("late", t, no_later(k("g92", t), k("s2", t)))]


def _dc1(t, e, ctx):
    """Unit 11 (R8): lease or transfer of a federal work (or one that becomes federal due to it)."""
    return [iff_u("dc1", t, And(U("lease", t), U("conn", t), Or(U("fed", t), U("becfed", t)), Not(U("late", t))))]


def _dc11(t, e, ctx):
    """Unit 12 (R8): retendering of a federal work."""
    return [iff_u("dc11", t, And(U("retender", t), U("fedb", t), U("conn", t), Not(U("late", t))))]


def _dc(t, e, ctx):
    return [iff_u("dc", t, Or(U("dc1", t), U("dc11", t)))]


def _nfinc(e, ctx):
    """Unit 14 (R8): a period in which the work was not federal is included iff it became federal by a change in its
    activities."""
    return [iff_u("nfinc", e, U("chg", e))]


def _gap(t, e, ctx):
    """Unit 15 (R8): the period between the two employers is not included (with (1)/(1.1)); without them there is no
    continuous employment across the two (unit 3)."""
    return [Implies(U("dc", t), Not(U("gapcnt", t))), Implies(Not(U("dc", t)), Not(U("gapcnt", t)))]


def _sev(t, e, ctx):
    """Unit 17 (R9): s.189 does not apply to severance pay at the second employer if the first employer paid it."""
    return [iff_u("sevapp", t, And(U("dc", t), Not(U("sevpaid", t))))]


def _cat(*builders):
    return lambda ctx: [f for b in builders for f in b(ctx)]


NONE = lambda ctx: []  # noqa: E731
UNITS = {
    1: ("RULE", NONE, "lead-in of the definitions (units 2, 3): 'In this Division'"),
    2: ("RULE", NONE, "R3: vacation pay is the amount of unit 5 (vp_y is that amount)"),
    3: ("PART", per("years", _cy), "definition by reference",
        "R1: years of employment counted by the bridge from stated dates (bridged); the employer's 'calendar year or other "
        "year determined ... in accordance with the regulations' (regulations not pinned) is a stated fact of the case"),
    4: ("RULE", per("years", _weeks), "R1, R2: 2 / 3 / 4 weeks by the completed years (the count is bridged: unit 3)"),
    5: ("RULE", per("years", _vp), "R3: 4 / 6 / 8 % of the year's wages, exact in cents (half up when stated)"),
    6: ("RULE", per("vacs", _split), "R4: more than one period on a written request approved in writing"),
    7: ("PART", _cat(per("vacs", _start), per("vacs", _pp)), "cross-reference",
        "R5: the ten months (bridged day) and the period proportion written; 'at any time that is prescribed by the "
        "regulations' (the payment time; regulations not pinned) not carried"),
    8: ("RULE", _cat(per("years", _deemed_y), per_emp(_deemed_e)),
        "R3, D7: vacation pay paid during a year is part of its wages; deemed wages for all purposes"),
    9: ("PART", _cat(per("hols", _hol), per("vacs", _hol_v)), "cross-reference",
        "R6: holiday during the vacation, extension and the holiday's wages written; which days are general holidays and "
        "their wages (s.196, not pinned) are stated facts"),
    10: ("RULE", _cat(per_emp(_term), per("years", _owing)),
         "R7: 30 days in Lean; (a) owing for prior completed years; (b) the applicable percentage of the completed portion "
         "(two readings of the years count: refused)"),
    11: ("PART", per("xfers", _dc1), "cross-reference",
         "R8: written; whether a work is a 'federal work, undertaking or business' (s.2, not pinned) is a stated fact"),
    12: ("PART", per("xfers", _dc11), "cross-reference",
         "R8: written; 'federal work, undertaking or business' (s.2) a stated fact"),
    13: ("RULE", per("xfers", _late), "R8, D5: the earlier day and 92 days in Lean"),
    14: ("RULE", per_emp(_nfinc), "R8: a change in activities includes the non-federal period"),
    15: ("RULE", _cat(per("xfers", _dc), per("xfers", _gap)),
         "R8: (1) or (1.1) applies; the period between the employers not included (and the count B leaves it out)"),
    17: ("PART", per("xfers", _sev), "cross-reference",
         "R9: written; whether the first employer paid severance pay under s.235 (not pinned) is a stated fact"),
    18: ("PART", per("xfers", _fed), "cross-reference",
         "R8: written; membership of the Financial Administration Act Schedules (not pinned) is a stated fact"),
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


# --- structure helpers (hipaa_breach_notice translation.py conventions) -------------------------------------------

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


def _derived_in(t):
    cs = set()
    atoms_in(t, set(), cs)
    return sorted(n for n in cs if n.split("_", 1)[0] in DERIVED_CONSTS)


def defines(f):
    """The atoms / day, count or money constants a ground rule fixes."""
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
    if f[0] == "eq" and f[1][0] == "scale":            # div x target = mul x base
        return _derived_in(f[1])
    if f[0] in ("le", "lt"):                           # the half-up bounds: the derived constant on the scaled side
        d = _derived_in(f[1]) if f[0] == "le" else _derived_in(f[2])
        if len(d) == 1:
            return d
    if f[0] == "shift_days" and f[1][0] == "const" and len(f[1]) == 3:
        return [f[1][2]]
    raise ValueError(f"no defined target: {f}")


# --- the environment for one case ---------------------------------------------------------------------------------

def int_constants(ctx):
    """name -> (unit, words) for every day / count / money constant of the case."""
    out = {}
    for kind, bases in BASES_OF.items():
        xs = ctx.emps if kind == "emps" else list(getattr(ctx, kind))
        for x in xs:
            for base in bases:
                out[f"{base}_{x}"] = INT_UNITS[base]
    return out


def environment(ctx):
    consts = {}
    for x in ctx.items:
        consts[x] = {"sort": "item", "description": f"The case's item {x}.", "verbalisation": f"item {x}"}
    for name, (unit, w) in int_constants(ctx).items():
        consts[name] = {"sort": "$int", "unit": unit, "description": f"{w[0].upper() + w[1:]} ({name}).",
                        "verbalisation": f"{w} ({name})"}
    preds = {n: {"arguments": ["item"], "description": d[0].upper() + d[1:] + "."}
             for n, d in {**FACTS, **DERIVED_UNARY}.items()}
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "The employment, a year of employment, a vacation or one period "
                                                             "of it, a general holiday, or a transfer or retendering the "
                                                             "case names."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {DAY: {"scale": "1", "display": {"kind": "iso_date"}},
                      CNT: {"scale": "1", "display": {"kind": "decimal", "label": "count"}},
                      CAD: {"scale": "100", "display": {"kind": "money", "currency": "CAD", "input_symbol": "$"}}}}


# --- planted errors (run.py --mutants): each must change the answer of at least one question ----------------------

def _swap(n, fn):
    def apply(t):
        t = dict(t)
        e = t[n]
        t[n] = (e[0], fn(e[1]), *e[2:])
        return t
    return apply


def _with_bands(bands, fn):
    def run(*a):
        global BANDS
        old = BANDS
        BANDS = bands
        try:
            return fn(*a)
        finally:
            BANDS = old
    return run


B_6Y = ((1, 6, 2, 4), (6, 10, 3, 6), (10, None, 4, 8))
B_11Y = ((1, 5, 2, 4), (5, 11, 3, 6), (11, None, 4, 8))
B_5PCT = ((1, 5, 2, 4), (5, 10, 3, 5), (10, None, 4, 8))


def _m_split(v, y, ctx):
    return [iff_u("splitok", v, U("reqw", v))]


def _m_start(v, y, ctx):
    return [iff_u("startok", v, ["date_before", k("vs", v), k("lst", y)])]


def _m_deemed_y(y, e, ctx):
    return [Eq(k("bs", y), k("wy", y))]


def _m_hol(h, v, ctx):
    out = _hol(h, v, ctx)
    out[0] = iff_u("hin", h, And(["date_before", k("vs", v), k("hd", h)], no_later(k("hd", h), k("ve", v))))
    return out


def _m_term30(e, ctx):
    out = _term(e, ctx)
    out[0] = shift(k("dl", e), k("td", e), 31)
    return out


def _m_term_a(e, ctx):
    out = _term(e, ctx)
    terms = [k("pt", e)]
    out[-1] = Implies(And(U("ceased", e), Not(U("hu", e))), Eq(k("tdue", e), add_all(terms)))
    return out


def _m_late91(t, e, ctx):
    out = _late(t, e, ctx)
    out[2] = shift(k("g92", t), k("ear", t), 91)
    return out


def _m_later(t, e, ctx):
    out = _late(t, e, ctx)
    l1, xd, ear = k("l1", t), k("xd", t), k("ear", t)
    out[0] = Implies(no_later(l1, xd), Eq(ear, xd))
    out[1] = Implies(no_later(xd, l1), Eq(ear, l1))
    return out


def _m_fed(t, e, ctx):
    return [iff_u("fed", t, U("fedb", t))]


def _m_dc1(t, e, ctx):
    return [iff_u("dc1", t, And(U("lease", t), U("conn", t), U("fed", t), Not(U("late", t))))]


def _m_sev(t, e, ctx):
    return [iff_u("sevapp", t, U("dc", t))]


def _m_cy(y, e, ctx):
    return [Eq(k("cy", y), k("ca", y)), iff_u("done", y, Le(cnt(1), k("cy", y)))]


def _m_nfinc(e, ctx):
    return [iff_u("nfinc", e, FALSE)]


MUTANTS = {
    "M1": ("THRESHOLD: three weeks from six completed years (not five)", _swap(4, lambda b: per("years", _with_bands(B_6Y, _weeks)))),
    "M2": ("THRESHOLD: four weeks and 8 % from eleven completed years (not ten)",
           lambda t: _swap(5, lambda b: per("years", _with_bands(B_11Y, _vp)))(
               _swap(4, lambda b: per("years", _with_bands(B_11Y, _weeks)))(t))),
    "M3": ("RATE: 5 % for five to nine years (not 6 %)", _swap(5, lambda b: per("years", _with_bands(B_5PCT, _vp)))),
    "M4": ("DEEMING (s.186): vacation pay paid during the year left out of its wages",
           _swap(8, lambda b: _cat(per("years", _m_deemed_y), per_emp(_deemed_e)))),
    "M5": ("SPLIT: a written request alone allows more than one period", _swap(6, lambda b: per("vacs", _m_split))),
    "M6": ("TEN MONTHS: a vacation beginning on the last day of the ten months is late",
           _swap(7, lambda b: _cat(per("vacs", _m_start), per("vacs", _pp)))),
    "M7": ("HOLIDAY: a general holiday on the vacation's first day does not occur during it",
           _swap(9, lambda b: _cat(per("hols", _m_hol), per("vacs", _hol_v)))),
    "M8": ("PERIOD: 30 days after ceasing to be employed read as 31",
           _swap(10, lambda b: _cat(per_emp(_m_term30), per("years", _owing)))),
    "M9": ("TERMINATION (a): vacation pay owing for prior completed years left out",
           _swap(10, lambda b: _cat(per_emp(_m_term_a), per("years", _owing)))),
    "M10": ("THIRTEEN WEEKS: the 91st day already more than 13 weeks after", _swap(13, lambda b: per("xfers", _m_late91))),
    "M11": ("EARLIER: the later of the two days of s.189(1.2)", _swap(13, lambda b: per("xfers", _m_later))),
    "M12": ("INCLUSION (s.189(2)): a deleted Schedule portion not a federal work", _swap(18, lambda b: per("xfers", _m_fed))),
    "M13": ("TRANSFER: a work that becomes federal due to the transfer not covered", _swap(11, lambda b: per("xfers", _m_dc1))),
    "M14": ("SEVERANCE (1.6): the first employer's severance payment ignored", _swap(17, lambda b: per("xfers", _m_sev))),
    "M15": ("CONTINUITY: the first employer's years never counted", _swap(3, lambda b: per("years", _m_cy))),
    "M16": ("CHANGE OF ACTIVITIES (1.3): the non-federal period never included", _swap(14, lambda b: per_emp(_m_nfinc))),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
