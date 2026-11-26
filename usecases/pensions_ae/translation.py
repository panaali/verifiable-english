"""Pensions Act 2008 ss. 1, 3, 5, 13 (statute corpus batch 4, text 9, UK pensions/benefits): the VE translation, one pass
with today's language.

Row statute-corpus-pensions-auto-enrolment (dri-statute-corpus-pensions-auto-enrolment-w-1124, Opus 5.5, translator and
encoder). CROSS-FAMILY questions (Codex writer gpt-6-astra, sealed in manage-agents
reviews/spare/statute-corpus/batch4/pensions-auto-enrolment/ISOLATION.md). Written from the pinned source only
(batch4/pensions-auto-enrolment/source.txt, sha256 7f55be2b...de212; units.jsonl 23 units, 0 table rows) BEFORE the encoder's
question file was read; ISOLATION.md D1-D14 bind. Evidence branch: nothing here is a Lean kernel line, a profile, a refuses
pair or a lint change; nothing merges.

UNITS maps each in-scope unit n of units.jsonl to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one case;
  ("PART", builder, cause, note) written except the part named in the note;
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2).
Items (one sort "item"): per EMPLOYMENT (a person with one employer; s. 1(2)-(3): every rule below is grounded per
employment, over that employment's own items only, so nothing of one employer's periods, sums or schemes reaches another):
the employment j, days x (a day a question is about, a day of a stated window, the stated automatic enrolment or
re-enrolment date), pay reference periods r, sums s (a sum payable, with its description and gross amount) and
memberships m (a stated period of active membership of a scheme). Every literal below (16, 22, 75, 10,000, 6,240, 50,270,
12 months) is a literal of the pinned text; 12 and 52 as the length of 12 months in months and weeks are the test's
stated convention (ISOLATION.md D3(c)); no number from a case is a coefficient except a period's stated length n, which
enters ONLY as the guard Eq(length, n) of a proportion rule (s. 3(6B), 5(7B), 13(2)): the grounding emits the split for
the stated n alone (selection only: a rule for another n would be dead under its guard; Lean checks the guard).
Dates computed from dates (the age on a day; the first day of the 12 months ending with the day before a date; the days of
a window) come ONLY from bridge/pae_bridge.py (ledgered "bridged"); every comparison with a limit and every sum,
proportion and band is written here (AMOUNTS ARE NEVER BRIDGED).

Readings fixed here, on the text alone (refuse when in doubt; ISOLATION.md D1-D14 bind):
R1 JOBHOLDER (s. 1(1)) on a day x: working or ordinarily working in Great Britain under the worker's contract on x (a stated
   fact), aged at least 16 and under 75 on x (age bridged), and qualifying earnings payable in the relevant pay reference
   period: the stated period of the employment containing x (D3(b)); qualifying earnings are payable iff the period's
   earnings are more than the proportionate lower amount (s. 13(1)(a): "the part (if any) ... more than"). No stated
   period contains x: no answer (neither yes nor no). "Worker" and the employer are stated facts (D2).
R2 THE TRIGGER (s. 3(1)(c), 5(1)(c), 3(6B), 5(7B)): earnings of the relevant period (s. 13(3) meaning, units 8, 18)
   compared EXACTLY with 10,000 x n/12 (n months) or 10,000 x n/52 (n weeks), written as 12 x E > n x 10,000 (resp. 52 x E);
   never a rounded threshold (D5). "More than": equal is not more.
R3 QUALIFYING EARNINGS (s. 13(1)-(2)): with L = 6,240 x n/12 and H = 50,270 x n/12 (or /52): E <= L -> 0; L < E <= H ->
   E - L; E > H -> H - L; written as 12 x QE = ... (resp. 52 x QE). An exact answer must be a whole number of pence (the
   integer domain); when the case states "the answer to the nearest penny, half up" (the template's rounding convention,
   D5), the answer is the whole-penny Q with 12 x Q <= X + 6p < 12 x Q + 12p, X = 12 x (the exact amount); without that
   statement a non-whole-penny amount has no answer (refused).
R4 EARNINGS (s. 13(3), a closed list: D14): a sum counts iff it is payable to the person in connection with the
   employment and of a description in (a)-(f); the description is the encoder's reading of the stated words (one fact per
   paragraph); (f) only when the case states the sum is prescribed for s. 13. A sum the encoder cannot place in or out of
   the list is left unplaced: every answer that needs it is refused.
R5 AGES (s. 1(1)(b), 3(1)(a), 5(1)(a), 5(1A)(a)): the bridged age on the day (D3(a)); "aged at least 22" = age >= 22,
   "at least 16 and under 75" = 16 <= age < 75. PENSIONABLE AGE: reached on day x iff the stated day the person reaches
   it is on or before x; a case stating it comes after every day of the case: not reached.
R6 SECTION 3 APPLIES on day x iff the person is a jobholder on x (R1), aged at least 22 on x, has not reached pensionable
   age on x, and earnings more than the trigger in the relevant period (R2).
R7 THE AUTOMATIC ENROLMENT DATE (s. 3(7)): form (a) (ISOLATION.md; the brief) the stated date (s. 4 deferral: the stated
   later date); form (b) the first day of the stated window on which s. 3 applies (every day of the window listed by the
   bridge; "first" = s. 3 applies on it and on no earlier listed day); "none in the window" iff s. 3 applies on no listed
   day. s. 4 itself is not in the file: its effect enters only as the stated date.
R7a WINDOW STRETCHES (2026-11-25, a STRUCTURAL change made after the encoder's question file was opened and before any
   answer was read: windows of up to 1,095 days made one item per day impossible within the language's limits; no reading
   changed; ISOLATION.md records it). A form (b) window is listed by the bridge as POINTS: its first day, every stated date
   inside it and every birthday inside it, each point with the last day of its stretch (the day before the next point;
   the window's last day for the last point) and the age on that last day. s3none(x): s. 3 applies on no day of x's
   stretch, written from conditions that hold on every day of it: not working in Great Britain on any day of it (stated),
   aged 75 or more on its first day, under 22 on its last day, pensionable age reached on its first day, or the stretch
   inside one stated period whose earnings are not more than the trigger. prior(x) (s. 3 applies on a day before x in the
   window): true when it applies on the previous point or prior holds there; false when prior is false there and s3none
   holds for its stretch; each link checked in Lean (x is 1 day after the previous stretch's last day), the first point
   checked equal to the window's stated first day and the last stretch's last day equal to its stated last day. The first
   day on which s. 3 applies = the first point on which it applies with no prior (s. 3 applies on a point day itself);
   "none in the window" = no prior at the last point and s3none for its stretch. A stretch on which neither is decided
   leaves the answer open.
R8 THE s. 3(2) DUTY (whether s. 3(2) requires the employer to make the arrangements; the arrangements' content is not
   written): there is an automatic enrolment date x, s. 3 applies on x, the jobholder was not an active member of a
   qualifying scheme on x (s. 3(3)), and did not cease to be one, because of an action or omission of the jobholder, on a
   day within the prescribed period before x (s. 3(4)): the 12 months ending with the day before x (D3(d); its first day
   bridged), i.e. first day <= cessation day < x. Only a membership of a scheme stated qualifying (R9) is "an active
   member of a qualifying scheme"; a cessation from a scheme stated not qualifying is not one. The cause is read as in
   R10: stated as the jobholder's own action or omission -> own; stated as something else -> not own; a cessation caused
   by the person ceasing to meet s. 1(1)(a) or (c), with no further stated cause, is NOT SETTLED as the jobholder's action
   or omission by the text: inside the period it leaves s. 3(4), and so the duty, with no answer. Form (b) with no day in
   the window: no.
R9 ACTIVE MEMBER on day x: a stated membership of a qualifying scheme (in relation to this employment: s. 1(3)(b)) whose
   first day is on or before x and that is open or whose last day is on or after x. Scheme status (ss. 16, 17) is stated.
R10 SECTION 5 APPLIES on the re-enrolment date x iff (1): as s. 3 (R6); or (1A): a jobholder on x, aged at least 22, not
   at pensionable age, not an active member on x, and a stated cessation of a membership of a scheme stated qualifying
   (R9) caused by a period in which s. 1(1)(a) or (c) was not met, that period beginning after the stated automatic
   enrolment date (the period's stated first day; strictly after), the cessation on or before x; or (1B): a jobholder on x
   with a stated cessation of a membership of a scheme stated qualifying, on or before x, caused by something other than
   an action or omission by the jobholder. A cessation from a scheme stated not qualifying is neither (1A)'s nor (1B)'s. A cessation stated as caused by the jobholder's own
   action or omission (notice, opting out, asking to leave) is not (1B); one stated as caused by the employer or the
   scheme (closure, an error) is (1B); one caused by the person ceasing to meet s. 1(1)(a) or (c) is NOT SETTLED for (1B)
   by the text (it is (1A)'s cause; whether it is also "something other than an action or omission by the jobholder" is
   open): (1B) gets no answer from it unless the case states the conclusion (a stated judgment). Not applying needs (1),
   (1A) and (1B) all decided false.
R11 THE s. 5(2) DUTY on the stated re-enrolment date x (s. 5(8): stated): s. 5 applies on x, not an active member on x
   (s. 5(3)), and not (3A): the automatic enrolment date deferred under s. 4 from a date before x to a date after x
   (both strict; the deferral stated).
R12 WHICH TEST FAILS (Q3) on day x for s. 3(1) or 5(1): in the fixed order of the brief, each condition decided on its
   own: not working in Great Britain; age outside 16 to under 75; no qualifying earnings (R1's earnings test); under 22;
   pensionable age reached; earnings not more than the threshold (R2); "none" when every one is decided met. One condition
   undecided: no answer.
"""
from __future__ import annotations

import hashlib
import json

DAY, GBP, YRS, MON, WK = ("day", "gbp", "year_count", "month_count", "week_count")
INT_UNITS = {  # per-item integer constants: base -> (unit, words)
    # employments
    "pday": (DAY, "the day the person reaches pensionable age (stated)"),
    "aed": (DAY, "the person's automatic enrolment date with the employer (stated, form (a))"),
    "dfrom": (DAY, "the date before the s. 4 deferral of the automatic enrolment date (stated)"),
    "dto": (DAY, "the date after the s. 4 deferral of the automatic enrolment date (stated)"),
    "aeday": (DAY, "the person's automatic enrolment date with the employer"),
    "wf": (DAY, "the first day of the case's stated window (stated)"),
    "wl": (DAY, "the last day of the case's stated window (stated)"),
    # days
    "day": (DAY, "the day (stated or listed by the bridge)"),
    "age": (YRS, "the person's age in whole years on the day (bridge)"),
    "pst": (DAY, "the first day of the 12 months ending with the day before the day (bridge)"),
    "tt": (DAY, "the last day of the window stretch that begins on the point (bridge, R7a)"),
    "aget": (YRS, "the person's age in whole years on the stretch's last day (bridge, R7a)"),
    # pay reference periods
    "pf": (DAY, "the period's first day (stated)"),
    "pt": (DAY, "the period's last day (stated)"),
    "pm": (MON, "the period's length in whole calendar months (stated)"),
    "pw": (WK, "the period's length in whole weeks (stated)"),
    "earn": (GBP, "the period's earnings in the s. 13(3) meaning (sum)"),
    "x12": (GBP, "12 (or 52) times the period's exact qualifying earnings"),
    "qe": (GBP, "the period's qualifying earnings"),
    # sums
    "amt": (GBP, "the sum's gross amount (stated)"),
    # memberships
    "mf": (DAY, "the membership's first day (stated)"),
    "mt": (DAY, "the membership's last day (stated)"),
    "cday": (DAY, "the day the person ceased to be an active member (stated)"),
    "gap": (DAY, "the first day of the period in which s. 1(1)(a) or (c) was not met that caused the cessation (stated)"),
}
PAIR_UNITS = {
    "ps": (GBP, "(sum, period) the sum's amount counted as the period's earnings"),
}
FACTS = {  # unary facts (the encoder states each true or false)
    # employments
    "pnever": "the person reaches pensionable age after every day of the case (stated)",
    "formb": "the case does not state the automatic enrolment date (form (b): it follows from the facts)",
    "hasaed": "the case states the person's automatic enrolment date with the employer",
    "deferred": "the employer deferred the automatic enrolment date under section 4 (stated, with both dates)",
    # days
    "gb": "the person is working or ordinarily works in Great Britain under the worker's contract on the day",
    "win": "the day is a point of the case's stated window (form (b), R7a)",
    "nogbs": "the person is not working or ordinarily working in Great Britain on any day of the point's stretch (R7a)",
    "aestated": "the day is the stated automatic enrolment date (form (a))",
    "reday": "the day is the employer's stated automatic re-enrolment date",
    # pay reference periods
    "inweeks": "the period's length is stated in whole weeks (else in whole calendar months)",
    "halfup": "the case states: no rounding until the answer; the answer to the nearest penny, half up",
    # sums
    "conn": "the sum is payable to the person in connection with the person's employment with the employer",
    "da": "the sum is salary, wages, commission, bonuses or overtime (s. 13(3)(a))",
    "db": "the sum is statutory sick pay under Part 11 of the SSCBA 1992 (s. 13(3)(b))",
    "dc": "the sum is statutory maternity pay under Part 12 of that Act (s. 13(3)(c))",
    "dd": "the sum is statutory paternity pay under Part 12ZA of that Act (s. 13(3)(d))",
    "de": "the sum is statutory adoption pay under Part 12ZB of that Act (s. 13(3)(e))",
    "dea": "the sum is statutory shared parental pay under Part 12ZC of that Act (s. 13(3)(ea))",
    "deb": "the sum is statutory parental bereavement pay under Part 12ZD of that Act (s. 13(3)(eb))",
    "dec": "the sum is statutory neonatal care pay under Part 12ZE of that Act (s. 13(3)(ec))",
    "df": "the sum is of a description prescribed for the purposes of s. 13 (stated, s. 13(3)(f))",
    # memberships
    "qual": "the scheme is a qualifying scheme in relation to the person and this employment (stated)",
    "mopen": "the membership has no stated last day (it continues past every day of the case)",
    "ceased": "the person ceased to be an active member of the scheme (stated, with the day and the cause)",
    "own": "the cessation was caused by an action or omission by the jobholder (stated cause)",
    "notown": "the cessation was caused by something other than an action or omission by the jobholder (stated cause)",
    "gbqe": "the cessation was caused by a period in which the person was not working in Great Britain or had no "
            "qualifying earnings (s. 1(1)(a) or (c) not met; stated cause)",
}
BINARY = {
    "payin": "(sum, period) the sum is payable in the pay reference period",
}
DERIVED_UNARY = {
    "earns": "(sum) the sum is earnings in the s. 13(3) meaning (units 8, 18, 23)",
    "hasqe": "(period) qualifying earnings are payable in the period (s. 13(1)-(2))",
    "over": "(period) the period's earnings are more than the proportionate 10,000 (s. 3(1)(c), (6B))",
    "qd": "(day) qualifying earnings are payable in the relevant pay reference period for the day",
    "od": "(day) earnings of more than the proportionate 10,000 are payable in the relevant period for the day",
    "gbd": "(day) the person is working or ordinarily works in Great Britain under the worker's contract on the day "
           "(s. 1(1)(a))",
    "agejh": "(day) the person is aged at least 16 and under 75 on the day",
    "jh": "(day) the person is a jobholder of the employer on the day (s. 1(1))",
    "a22": "(day) the person is aged at least 22 on the day",
    "reached": "(day) the person has reached pensionable age on the day",
    "s3": "(day) section 3 applies to the person on the day (s. 3(1))",
    "ae": "(day) the day is the person's automatic enrolment date (s. 3(7))",
    "nonewin": "(employment) section 3 applies to the person on no day of the stated window",
    "prior": "(day) section 3 applies to the person on a day of the window before the point (R7a)",
    "s3none": "(day) section 3 applies to the person on no day of the point's stretch (R7a)",
    "active": "(day) the person is an active member of a qualifying scheme on the day",
    "ownin": "(day) the person ceased, because of an own action or omission, within the prescribed period before the day",
    "duty3": "(employment) section 3(2) requires the employer to make the arrangements (s. 3(2)-(4))",
    "s51": "(day) section 5(1) applies to the person on the day",
    "s51a": "(day) section 5(1A) applies to the person on the day",
    "s51b": "(day) section 5(1B) applies to the person on the day",
    "s5": "(day) section 5 applies to the person on the day",
    "def3a": "(day) the automatic enrolment date was deferred under s. 4 from before the day to after it (s. 5(3A))",
    "duty5": "(day) section 5(2) requires the employer to make the arrangements with effect from the day (s. 5(2)-(3A))",
}
DERIVED_BINARY = {
    "rel": "(day, period) the period is the relevant pay reference period for the day (the stated period containing it)",
}
STATED = ()
BRIDGED_CONSTS = ("age", "pst", "tt", "aget")


# --- formula helpers (the ve-quantity@1 wire shapes; fmla_eligibility / posthog_leave conventions) ------------------

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
def scale(tag, kk, t): return ["scale", tag, str(kk), t]
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
    return ["const", INT_UNITS[base][0], f"{base}_{x}"]


def kp(base, x, y):
    return ["const", PAIR_UNITS[base][0], f"{base}_{x}_{y}"]


def total(tag, terms):
    if not terms:
        return lit(tag, "0")
    r = terms[-1]
    for t in reversed(terms[:-1]):
        r = add(tag, t, r)
    return r


def iff_u(p, x, body): return Iff(U(p, x), body)


# --- the case context ---------------------------------------------------------------------------------------------

class Emp:
    """One employment (s. 1(2)-(3)): its items. lengths: {period: ("m" | "w", n)} = the STATED length, used only to select
    which guarded proportion rule to ground (the guard itself is a Lean premise). window: the stated window's points as the
    bridge lists them, first to last (R7a: each link carries the Lean check that the point is 1 day after the previous
    stretch's last day)."""
    def __init__(self, j, days=(), periods=(), sums=(), members=(), lengths=None, window=()):
        self.j, self.days, self.periods = j, list(days), list(periods)
        self.sums, self.members, self.lengths = list(sums), list(members), dict(lengths or {})
        self.window = list(window)  # the window's points in the bridge's order (each also in days; R7a)

    @property
    def items(self):
        return [self.j] + self.days + self.periods + self.sums + self.members


class Ctx:
    def __init__(self, emps=()):
        self.emps = list(emps)

    @property
    def items(self):
        return [x for e in self.emps for x in e.items]


def per_emp(fn):
    return lambda ctx: [f for e in ctx.emps for f in fn(e)]


def per(kind, fn):
    return lambda ctx: [f for e in ctx.emps for x in getattr(e, kind) for f in fn(x, e)]


def _cat(*builders):
    return lambda ctx: [f for b in builders for f in b(ctx)]


def _none(ctx):
    return []


def _split(e, r):
    """(coefficient of 12 months, n, guard) for the period's stated length (R2, D3(c))."""
    kind, n = e.lengths[r]
    if kind == "w":
        return 52, n, And(U("inweeks", r), Eq(k("pw", r), lit(WK, str(n))))
    return 12, n, And(Not(U("inweeks", r)), Eq(k("pm", r), lit(MON, str(n))))


# --- the units ----------------------------------------------------------------------------------------------------

def _u23(s, e):
    """s. 13(3) (R4): earnings = sums of the listed descriptions payable in connection with the employment."""
    desc = Or(*[U(p, s) for p in ("da", "db", "dc", "dd", "de", "dea", "deb", "dec", "df")])
    return [iff_u("earns", s, And(U("conn", s), desc))]


def _earn(r, e):
    """Units 8, 18 (s. 3(6A), 5(7A)) with 23: the period's earnings = the sum of its sums that are earnings."""
    out = [Eq(k("earn", r), total(GBP, [kp("ps", s, r) for s in e.sums]))]
    for s in e.sums:
        inr = B("payin", s, r)
        out += [Implies(And(inr, U("earns", s)), Eq(kp("ps", s, r), k("amt", s))),
                Implies(Or(Not(inr), Not(U("earns", s))), Eq(kp("ps", s, r), lit(GBP, "0")))]
    return out


def _band(r, e):
    """s. 13(1)-(2) (R3): qualifying earnings, the 6,240-50,270 band made proportionate (written x 12 or x 52)."""
    if r not in e.lengths:
        return []
    d, n, g = _split(e, r)
    E12 = scale(GBP, d, k("earn", r))
    lo, hi = scale(GBP, n, lit(GBP, "6240")), scale(GBP, n, lit(GBP, "50270"))
    out = [Implies(And(g, Lt(lo, E12)), U("hasqe", r)),
           Implies(And(g, Le(E12, lo)), Not(U("hasqe", r))),
           Implies(And(g, Le(E12, lo)), Eq(k("x12", r), lit(GBP, "0"))),
           Implies(And(g, Lt(lo, E12), Le(E12, hi)), Eq(k("x12", r), add(GBP, E12, scale(GBP, -n, lit(GBP, "6240"))))),
           Implies(And(g, Lt(hi, E12)), Eq(k("x12", r), add(GBP, hi, scale(GBP, -n, lit(GBP, "6240"))))),
           Implies(Not(U("halfup", r)), Eq(scale(GBP, d, k("qe", r)), k("x12", r)))]
    half = lit(GBP, "0.06") if d == 12 else lit(GBP, "0.26")
    out += [Implies(U("halfup", r), Le(scale(GBP, d, k("qe", r)), add(GBP, k("x12", r), half))),
            Implies(U("halfup", r), Lt(add(GBP, k("x12", r), half), add(GBP, scale(GBP, d, k("qe", r)),
                                                                         lit(GBP, "0.12" if d == 12 else "0.52"))))]
    return out


def _trigger(r, e):
    """s. 3(1)(c) with (6B), s. 5(1)(c) with (7B) (R2): earnings more than 10,000 x n/12 (n/52), compared exactly."""
    if r not in e.lengths:
        return []
    d, n, g = _split(e, r)
    E12, t = scale(GBP, d, k("earn", r)), scale(GBP, n, lit(GBP, "10000"))
    return [Implies(And(g, Lt(t, E12)), U("over", r)), Implies(And(g, Le(E12, t)), Not(U("over", r)))]


def _rel(x, e):
    """Relevant period (s. 15 by the test's convention D3(b)): the stated period containing the day."""
    out = []
    for r in e.periods:
        inside = And(no_later(k("pf", r), k("day", x)), no_later(k("day", x), k("pt", r)))
        out += [Implies(inside, B("rel", x, r)),
                Implies(Or(before(k("day", x), k("pf", r)), before(k("pt", r), k("day", x))), Not(B("rel", x, r)))]
    some = Or(*[B("rel", x, r) for r in e.periods])
    out += [Implies(Or(*[And(B("rel", x, r), U("hasqe", r)) for r in e.periods]), U("qd", x)),
            Implies(And(some, *[Or(Not(B("rel", x, r)), Not(U("hasqe", r))) for r in e.periods]), Not(U("qd", x))),
            Implies(Or(*[And(B("rel", x, r), U("over", r)) for r in e.periods]), U("od", x)),
            Implies(And(some, *[Or(Not(B("rel", x, r)), Not(U("over", r))) for r in e.periods]), Not(U("od", x)))]
    return out


def _u1(x, e):
    """s. 1(1) (R1): a jobholder on the day."""
    a = k("age", x)
    return [iff_u("gbd", x, U("gb", x)),
            iff_u("agejh", x, And(Le(lit(YRS, "16"), a), Lt(a, lit(YRS, "75")))),
            iff_u("jh", x, And(U("gbd", x), U("agejh", x), U("qd", x)))]


def _ages(x, e):
    """s. 3(1)(a)-(b), 5(1)(a)-(b), 5(1A)(a)-(b) (R5): at least 22; pensionable age reached."""
    j = e.j
    return [iff_u("a22", x, Le(lit(YRS, "22"), k("age", x))),
            Implies(And(Not(U("pnever", j)), no_later(k("pday", j), k("day", x))), U("reached", x)),
            Implies(And(Not(U("pnever", j)), before(k("day", x), k("pday", j))), Not(U("reached", x))),
            Implies(U("pnever", j), Not(U("reached", x)))]


def _u4(x, e):
    """s. 3(1) (R6)."""
    return [iff_u("s3", x, And(U("jh", x), U("a22", x), Not(U("reached", x)), U("od", x)))]


def _u10(e):
    """s. 3(7) (R7, R7a): the automatic enrolment date; form (a) stated, form (b) the first window day s. 3 applies, by
    the chain of stretches."""
    j, out, w = e.j, [], e.window
    for x in e.days:
        out.append(Implies(Not(U("formb", j)), Iff(U("ae", x), U("aestated", x))))
        if x not in w:
            out.append(Implies(And(U("formb", j), Not(U("win", x))), Not(U("ae", x))))
        out.append(Implies(U("ae", x), Eq(k("aeday", j), k("day", x))))
    if not w:
        return out
    first, last = w[0], w[-1]
    starts = And(no_later(k("day", first), k("wf", j)), no_later(k("wf", j), k("day", first)))
    ends = And(no_later(k("tt", last), k("wl", j)), no_later(k("wl", j), k("tt", last)))
    out.append(Implies(starts, Not(U("prior", first))))
    for i, x in enumerate(w):
        if i:
            p = w[i - 1]
            link = ["shift_days", k("day", x), k("tt", p), "1"]
            out += [Implies(And(link, Or(U("s3", p), U("prior", p))), U("prior", x)),
                    Implies(And(link, Not(U("prior", p)), U("s3none", p)), Not(U("prior", x)))]
        out.append(Implies(U("formb", j), Iff(U("ae", x), And(U("win", x), U("s3", x), Not(U("prior", x))))))
    out += [Implies(And(U("formb", j), ends, Not(U("prior", last)), U("s3none", last)), U("nonewin", j)),
            Implies(And(U("formb", j), Or(U("prior", last), U("s3", last))), Not(U("nonewin", j)))]
    return out


def _stretch(e):
    """R7a: s. 3 applies on no day of a point's stretch (conditions true on every day of it)."""
    j, out = e.j, []
    for x in e.window:
        inside = [And(no_later(k("pf", r), k("day", x)), no_later(k("tt", x), k("pt", r)), Not(U("over", r)))
                  for r in e.periods]
        out.append(Implies(Or(U("nogbs", x), Le(lit(YRS, "75"), k("age", x)), Lt(k("aget", x), lit(YRS, "22")),
                              And(Not(U("pnever", j)), no_later(k("pday", j), k("day", x))), *inside),
                           U("s3none", x)))
    return out


def _active(x, e):
    """R9: an active member of a qualifying scheme on the day (s. 1(3)(b): this employment's memberships)."""
    def on(m):
        return And(U("qual", m), no_later(k("mf", m), k("day", x)),
                   Or(U("mopen", m), no_later(k("day", x), k("mt", m))))

    def off(m):
        return Or(Not(U("qual", m)), before(k("day", x), k("mf", m)),
                  And(Not(U("mopen", m)), before(k("mt", m), k("day", x))))
    return [Implies(Or(*[on(m) for m in e.members]), U("active", x)),
            Implies(And(*[off(m) for m in e.members]), Not(U("active", x)))]


def _u7(x, e):
    """s. 3(4) (R8): ceased because of an own action or omission within the prescribed period before the day."""
    def inside(m):
        return And(U("ceased", m), U("qual", m), U("own", m), no_later(k("pst", x), k("cday", m)),
                   before(k("cday", m), k("day", x)))

    def outside(m):
        return Or(Not(U("ceased", m)), Not(U("qual", m)), U("notown", m), before(k("cday", m), k("pst", x)),
                  no_later(k("day", x), k("cday", m)))
    return [Implies(Or(*[inside(m) for m in e.members]), U("ownin", x)),
            Implies(And(*[outside(m) for m in e.members]), Not(U("ownin", x)))]


def _u5(e):
    """s. 3(2)-(4) (R8): whether s. 3(2) requires the employer to make the arrangements (per day: the automatic enrolment
    date decides; form (b) with no day in the window: no)."""
    j, out = e.j, []
    for x in e.days:
        ok = And(U("s3", x), Not(U("active", x)), Not(U("ownin", x)))
        bad = Or(Not(U("s3", x)), U("active", x), U("ownin", x))
        out += [Implies(And(U("ae", x), ok), U("duty3", j)), Implies(And(U("ae", x), bad), Not(U("duty3", j)))]
    out.append(Implies(And(U("formb", j), U("nonewin", j)), Not(U("duty3", j))))
    return out


def _u12(x, e):
    """s. 5(1) (R10): as s. 3(1)."""
    return [iff_u("s51", x, And(U("jh", x), U("a22", x), Not(U("reached", x)), U("od", x)))]


def _u13(x, e):
    """s. 5(1A) (R10): not an active member because of a period, beginning after the automatic enrolment date, in which
    s. 1(1)(a) or (c) was not met."""
    j = e.j
    cause = Or(*[And(U("ceased", m), U("qual", m), U("gbqe", m), no_later(k("cday", m), k("day", x)), U("hasaed", j),
                     before(k("aed", j), k("gap", m))) for m in e.members])
    nocause = And(*[Or(Not(U("ceased", m)), Not(U("qual", m)), Not(U("gbqe", m)), before(k("day", x), k("cday", m)),
                       And(U("hasaed", j), no_later(k("gap", m), k("aed", j)))) for m in e.members])
    base = And(U("jh", x), U("a22", x), Not(U("reached", x)), Not(U("active", x)))
    return [Implies(And(base, cause), U("s51a", x)),
            Implies(Or(Not(U("jh", x)), Not(U("a22", x)), U("reached", x), U("active", x), nocause), Not(U("s51a", x)))]


def _u14(x, e):
    """s. 5(1B) (R10): ceased because of something other than an action or omission by the jobholder."""
    cause = Or(*[And(U("ceased", m), U("qual", m), U("notown", m), no_later(k("cday", m), k("day", x)))
                 for m in e.members])
    nocause = And(*[Or(Not(U("ceased", m)), Not(U("qual", m)), U("own", m), before(k("day", x), k("cday", m)))
                    for m in e.members])
    return [Implies(And(U("jh", x), cause), U("s51b", x)),
            Implies(Or(Not(U("jh", x)), nocause), Not(U("s51b", x)))]


def _s5(x, e):
    return [iff_u("s5", x, Or(U("s51", x), U("s51a", x), U("s51b", x)))]


def _u17(x, e):
    """s. 5(3A) (R11): deferred under s. 4 from a date before the re-enrolment date to a date after it."""
    j = e.j
    return [iff_u("def3a", x, And(U("deferred", j), before(k("dfrom", j), k("day", x)), before(k("day", x), k("dto", j))))]


def _u15(x, e):
    """s. 5(2)-(3A) (R11) on the stated re-enrolment date."""
    return [Implies(Not(U("reday", x)), Not(U("duty5", x))),
            Implies(U("reday", x), Iff(U("duty5", x), And(U("s5", x), Not(U("active", x)), Not(U("def3a", x)))))]


NORM, XREF, DEFREF, DATE = "other:norm", "cross-reference", "definition by reference", "date/age arithmetic"

UNITS = {
    1: ("PART", _cat(per("days", _rel), per("days", _u1)), XREF,
        "R1: jobholder on a day WRITTEN (age BRIDGED); the relevant pay reference period (s. 15, not in the file) is the "
        "test's convention (the stated period containing the day); 'worker' and the employer stated"),
    2: ("RULE", _none, "s. 1(2): each employment separately: every rule is grounded per employment (Emp) over its own "
                       "items (D13)"),
    3: ("RULE", _none, "s. 1(3): the employer concerned and membership in relation to the employment: per-employment "
                       "grounding (Emp; R9 memberships of this employment only)"),
    4: ("PART", _cat(per("days", _ages), per("days", _u4)), XREF,
        "R5, R6: s. 3(1) WRITTEN (age BRIDGED); the relevant period of s. 15 by the test's convention; pensionable age "
        "(not in the file) a stated date"),
    5: ("PART", per_emp(_u5), NORM,
        "R8: whether s. 3(2) requires the employer to make the arrangements WRITTEN as a classification; the duty's "
        "content ('prescribed arrangements', the automatic enrolment scheme) and the norm itself NOT written"),
    6: ("RULE", per("days", _active), "s. 3(3) (R8, R9): active membership of a qualifying scheme on a day by stated "
                                      "dates; the exception itself in unit 5's builder"),
    7: ("PART", per("days", _u7), XREF,
        "R8: s. 3(4) WRITTEN; the prescribed period (regulations, not in the file) is the test's convention: the 12 months "
        "ending with the day before (its first day BRIDGED); the cessation's cause stated"),
    8: ("RULE", per("sums", _u23), "s. 3(6A): earnings in the s. 13(3) meaning (s. 13(3) in scope, unit 23's builder)"),
    9: ("RULE", per("periods", _trigger), "s. 3(6B) (R2): the 10,000 proportionately less or more, compared exactly "
                                          "(12 x E > n x 10,000; weeks: 52 x E) for the stated length n (D3(c))"),
    10: ("PART", _cat(per_emp(_u10), per_emp(_stretch)), XREF,
         "R7, R7a: the first day on which s. 3 applies WRITTEN (window points and stretch ends BRIDGED); 'subject to "
         "section 4' (not in the file): "
         "a deferral enters only as the stated date"),
    11: ("NOT", None, XREF, "s. 3(8): 'automatic enrolment scheme ... (see section 17)': the scheme's status is a stated "
                            "fact; no question's outcome is decided by this unit"),
    12: ("PART", per("days", _u12), XREF, "R10: s. 5(1) WRITTEN (age BRIDGED); the relevant period of s. 15 by the "
                                          "test's convention"),
    13: ("PART", per("days", _u13), DATE, "R10: s. 5(1A) WRITTEN (age BRIDGED); the cessation's cause and the period's "
                                          "first day stated"),
    14: ("RULE", per("days", _u14), "R10: s. 5(1B) on the stated cause; a cessation caused by ceasing to meet s. 1(1)(a) "
                                    "or (c) not settled (no answer)"),
    15: ("PART", per("days", lambda x, e: _s5(x, e) + _u15(x, e)), NORM,
         "R10, R11: whether s. 5(2) requires the employer to make the arrangements with effect from the stated "
         "re-enrolment date WRITTEN as a classification; the duty's content and the norm itself NOT written"),
    16: ("RULE", _none, "s. 5(3) in unit 15's builder (R11) with R9"),
    17: ("PART", per("days", _u17), XREF, "R11: s. 5(3A) WRITTEN; the s. 4 deferral (not in the file) stated with its two "
                                          "dates"),
    18: ("RULE", _none, "s. 5(7A): earnings in the s. 13(3) meaning (unit 8's builder)"),
    19: ("RULE", _none, "s. 5(7B) (R2): unit 9's builder (the same trigger, the same split)"),
    20: ("NOT", None, XREF, "s. 5(8): re-enrolment dates by regulations (not in the file): the employer's date stated"),
    21: ("RULE", per("periods", _band), "R3: s. 13(1) the band, exact (whole pence) or half up when the case states it"),
    22: ("RULE", _none, "s. 13(2): the band proportionately less or more (unit 21's builder, the same split)"),
    23: ("PART", per("periods", _earn), XREF,
         "R4: s. 13(3) WRITTEN as a closed list over the stated descriptions; (f) 'sums prescribed' (regulations, not in "
         "the file) stated; (b)-(ec) 'under Part ... of the SSCBA 1992' (definition by reference): the description stated"),
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


# --- structure helpers (fmla_eligibility / posthog_leave conventions) ----------------------------------------------

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


def _qe_in(f):
    cs = set()
    atoms_in(f, set(), cs)
    return sorted(n for n in cs if n.startswith("qe_"))


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
    if f[0] == "eq" and f[1][0] == "const" and len(f[1]) == 3:
        return [f[1][2]]
    if f[0] == "eq" and f[1][0] == "scale" and f[1][3][0] == "const" and len(f[1][3]) == 3:
        return [f[1][3][2]]
    if f[0] in ("le", "lt") and _qe_in(f):  # R3 half up: the two bounds define the rounded amount
        return _qe_in(f)
    raise ValueError(f"no defined target: {f}")


# --- the environment for one case ---------------------------------------------------------------------------------

KIND_BASES = {"j": ("pday", "aed", "dfrom", "dto", "aeday", "wf", "wl"), "days": ("day", "age", "pst", "tt", "aget"),
              "periods": ("pf", "pt", "pm", "pw", "earn", "x12", "qe"), "sums": ("amt",),
              "members": ("mf", "mt", "cday", "gap")}


def int_constants(ctx):
    out = {}
    for e in ctx.emps:
        for kind, bases in KIND_BASES.items():
            for x in ([e.j] if kind == "j" else getattr(e, kind)):
                for base in bases:
                    out[f"{base}_{x}"] = INT_UNITS[base]
    sums = [s for e in ctx.emps for s in e.sums]  # every pair of the case (planted error M17 joins employments)
    for e in ctx.emps:
        for s in sums:
            for r in e.periods:
                out[f"ps_{s}_{r}"] = PAIR_UNITS["ps"]
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
            "vocabulary": {"sorts": {"item": {"description": "An employment, day, pay reference period, sum or scheme "
                                                             "membership the case names."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {DAY: {"scale": "1", "display": {"kind": "iso_date"}},
                      GBP: {"scale": "100", "display": {"kind": "decimal", "label": "GBP"}},
                      YRS: {"scale": "1", "display": {"kind": "decimal", "label": "years"}},
                      MON: {"scale": "1", "display": {"kind": "decimal", "label": "months"}},
                      WK: {"scale": "1", "display": {"kind": "decimal", "label": "weeks"}}}}


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


def _atom_to(pred, repl):
    def walk(f):
        if type(f) is not list or not f:
            return f
        if f[0] == "unary" and f[1] == pred:
            return repl(f) if callable(repl) else repl
        return [walk(x) for x in f]
    return walk


def _drop(pred):
    return lambda builder: (lambda ctx: [f for f in builder(ctx) if not pred(json.dumps(f))])


def _trigger_ge(r, e):
    """M1: 'more than' read as 'at least'."""
    if r not in e.lengths:
        return []
    d, n, g = _split(e, r)
    E12, t = scale(GBP, d, k("earn", r)), scale(GBP, n, lit(GBP, "10000"))
    return [Implies(And(g, Le(t, E12)), U("over", r)), Implies(And(g, Lt(E12, t)), Not(U("over", r)))]


def _no_pst(f):
    """M12: the comparisons with the prescribed period's first day replaced by 'inside'."""
    if type(f) is not list or not f:
        return f
    if f[0] == "date_no_later" and f[1][:1] == ["const"] and f[1][2].startswith("pst_"):
        return TRUE
    if f[0] == "date_before" and f[2][:1] == ["const"] and f[2][2].startswith("pst_"):
        return FALSE
    return [_no_pst(x) for x in f]


def _first_dropped(f):
    """M13: in form (b), ae(x) iff win(x) and s3(x) (the 'no earlier listed day' conjunct dropped)."""
    def walk(g):
        if type(g) is not list or not g:
            return g
        if g[0] == "not" and g[1][:2] == ["unary", "prior"]:
            return TRUE
        return [walk(x) for x in g]
    return walk(f) if '"ae"' in json.dumps(f) else f


def _joined(t):
    """M17: s. 1(2) dropped: every sum of the case counted in every employment's periods."""
    t = dict(t)

    def b(ctx):
        sums = [s for em in ctx.emps for s in em.sums]
        return [f for em in ctx.emps for r in em.periods
                for f in _earn(r, Emp(em.j, em.days, em.periods, sums, em.members, em.lengths))]
    t[23] = (t[23][0], b, *t[23][2:])
    return t


def _u7_m18(x, e):
    """M18: s. 3(4) read for any stated scheme, and a cessation caused by ceasing to meet s. 1(1)(a) or (c) read as not
    own."""
    def inside(m):
        return And(U("ceased", m), U("own", m), no_later(k("pst", x), k("cday", m)), before(k("cday", m), k("day", x)))

    def outside(m):
        return Or(Not(U("ceased", m)), U("notown", m), U("gbqe", m), before(k("cday", m), k("pst", x)),
                  no_later(k("day", x), k("cday", m)))
    return [Implies(Or(*[inside(m) for m in e.members]), U("ownin", x)),
            Implies(And(*[outside(m) for m in e.members]), Not(U("ownin", x)))]


def _u13_m19(x, e):
    """M19: s. 5(1A)(c) read for any stated scheme's cessation."""
    j = e.j
    cause = Or(*[And(U("ceased", m), U("gbqe", m), no_later(k("cday", m), k("day", x)), U("hasaed", j),
                     before(k("aed", j), k("gap", m))) for m in e.members])
    nocause = And(*[Or(Not(U("ceased", m)), Not(U("gbqe", m)), before(k("day", x), k("cday", m)),
                       And(U("hasaed", j), no_later(k("gap", m), k("aed", j)))) for m in e.members])
    base = And(U("jh", x), U("a22", x), Not(U("reached", x)), Not(U("active", x)))
    return [Implies(And(base, cause), U("s51a", x)),
            Implies(Or(Not(U("jh", x)), Not(U("a22", x)), U("reached", x), U("active", x), nocause), Not(U("s51a", x)))]


def _u14_m20(x, e):
    """M20: s. 5(1B) read for any stated scheme's cessation."""
    cause = Or(*[And(U("ceased", m), U("notown", m), no_later(k("cday", m), k("day", x))) for m in e.members])
    nocause = And(*[Or(Not(U("ceased", m)), U("own", m), before(k("day", x), k("cday", m))) for m in e.members])
    return [Implies(And(U("jh", x), cause), U("s51b", x)),
            Implies(Or(Not(U("jh", x)), nocause), Not(U("s51b", x)))]


def _sub_units(ns, a, b):
    def apply(t):
        t = dict(t)
        for n in ns:
            t[n] = (t[n][0], _wrap(_json_sub(a, b))(t[n][1]), *t[n][2:])
        return t
    return apply


MUTANTS = {
    "M1": ("TRIGGER: s. 3(1)(c) 'more than' 10,000 read as 'at least'", _swap(9, lambda bld: per("periods", _trigger_ge))),
    "M2": ("TRIGGER: 10,000 read as 9,000", _swap(9, _wrap(_json_sub('"gbp", "10000"', '"gbp", "9000"')))),
    "M3": ("BAND: the lower amount 6,240 read as 6,420", _swap(21, _wrap(_json_sub('"gbp", "6240"', '"gbp", "6420"')))),
    "M4": ("BAND: the upper amount 50,270 read as 50,720", _swap(21, _wrap(_json_sub('"gbp", "50270"', '"gbp", "50720"')))),
    "M5": ("AGE: at least 22 read as at least 21", _swap(4, _wrap(_json_sub('"year_count", "22"', '"year_count", "21"')))),
    "M6": ("AGE: under 75 read as 75 or under", _swap(1, _wrap(_json_sub(
        '["lt", ["const", "year_count", "age_', '["le", ["const", "year_count", "age_')))),
    "M7": ("PENSIONABLE AGE: reached on the stated day read as reached only the day after", _swap(4, _wrap(lambda f: json.loads(
        json.dumps(f).replace('["date_no_later", ["const", "day", "pday_', '["date_before", ["const", "day", "pday_')
        .replace('["date_before", ["const", "day", "day_', '["date_no_later", ["const", "day", "day_'))))),
    "M8": ("PROPORTION: a week read as 1/53 of 12 months", _sub_units((9, 21), '["scale", "gbp", "52"', '["scale", "gbp", "53"')),
    "M9": ("EARNINGS: statutory sick pay left out of s. 13(3)", _swap(8, _wrap(_atom_to("db", FALSE)))),
    "M10": ("EARNINGS: s. 13(3) read as open (any sum in connection with the employment)",
            _swap(8, _wrap(lambda f: Iff(f[1][1], U("conn", f[1][1][2][1]))))),
    "M11": ("s. 3(3): the active-member exception dropped", _swap(5, _wrap(_atom_to("active", FALSE)))),
    "M12": ("s. 3(4): the prescribed period unbounded (any earlier own cessation)", _swap(7, _wrap(_no_pst))),
    "M13": ("s. 3(7): 'the first day' dropped (any window day on which s. 3 applies)", _swap(10, _wrap(_first_dropped))),
    "M14": ("s. 5(3A): 'from a date before' read as 'on or before'", _swap(17, _wrap(_json_sub(
        '["date_before", ["const", "day", "dfrom_', '["date_no_later", ["const", "day", "dfrom_')))),
    "M15": ("s. 5(1B) dropped", _swap(14, lambda bld: (lambda ctx: [Not(U("s51b", x)) for e in ctx.emps for x in e.days]))),
    "M16": ("s. 5(1A): the age 22 test dropped", _swap(13, _wrap(_atom_to("a22", TRUE)))),
    "M17": ("s. 1(2): two employments' sums added together", _joined),
    "M18": ("s. 3(4): a cessation from any scheme counts, and one caused by ceasing to meet s. 1(1)(a) or (c) is not own",
            _swap(7, lambda bld: per("days", _u7_m18))),
    "M19": ("s. 5(1A)(c): a cessation from any scheme counts", _swap(13, lambda bld: per("days", _u13_m19))),
    "M20": ("s. 5(1B): a cessation from any scheme counts", _swap(14, lambda bld: per("days", _u14_m20))),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
