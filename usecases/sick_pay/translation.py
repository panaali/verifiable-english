"""Statutory sick pay, SSCBA 1992 ss. 151-155, 157 (statute corpus batch 3, law 8): the VE translation, one pass with today's
language. SAME-FAMILY (Opus writer, Opus translator/encoder).

Row statute-corpus-sick-pay (dri-statute-corpus-sick-pay-1123, Opus 5.5). Written from the pinned source only (manage-agents
reviews/spare/statute-corpus/stock/sick-pay/source.txt, sha256 f972a047...bb9a10dd) BEFORE the encoder's question file was
read (ISOLATION.md "Translation"). Evidence branch: nothing here is a Lean kernel line, a profile, a refuses pair or a lint
change; nothing merges.

UNITS maps each in-scope unit n of stock/sick-pay/units.jsonl to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one sub-case;
  ("PART", builder, cause, note) written except the part named in the note;
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2).
A builder returns (formula, target) pairs: target is the atom key or integer constant the formula defines (None = a check:
a formula with no target that the facts and steps must not contradict).

ONE SUB-CASE = one employee and one employer (one contract of service). 153(4) and 154(4) ("may also be ... as between him
and another employer") are carried by structure: every rule is grounded per contract, and nothing of one employer's
sub-case reads another's.

THE DAYS AS A CHAIN OF PIECES. A sub-case's days are cut (encode.py) into PIECES p0, p1, ... in time order: runs of consecutive
days with the same stated facts; a piece that may carry an amount lies within one week (beginning with Sunday); each asked day
is a piece of its own. Each piece has its first and last day as stated constants st_x, en_x. Nothing about the cut is trusted:
consecutiveness (st_x is 1 day after en_p) and membership of a week (0 <= days from the week's Sunday to st_x <= to en_x <= 6)
are date arithmetic in the rules, checked by Lean; a wrong cut leaves the answer undetermined (OPEN), never different.
For each piece x (p = the piece before it) the rules define:
  inc(x)     every day of x is a day of incapacity for work (151(4));
  com(x)     a period of incapacity for work commences with the first day of x (152(2): one day, or consecutive days, 152(5));
  lst_x      the last day of incapacity up to the end of x (or, before any is known in the chain, an upper bound: the day
             before the chain's first day), with known(x) = it is a day of incapacity the chain shows;
  lnk(x)     the period commencing with x is treated with the earlier one as a single period (152(3));
  accp_x     the amount to which the employee has become entitled during the period of entitlement before x (155(3));
  inpoe(x)   the days of x fall within a period of entitlement (153(1), (2), (7), (8));
  k_x        the number of qualifying days among the days of x (the week's indicators iq at x's offsets); nq_w the number of
             qualifying days in week w (154, 157(3));
  gr_x       the amount of statutory sick pay payable for the days of x (157(3): for each day, the weekly rate divided by
             nq_w; x's k_x qualifying days in the period of entitlement give nq_w x gr_x = k_x x rate);
  acc_x      accp_x + gr_x; ovr(x) the aggregate passes the entitlement limit within x.

READINGS (fixed here, before the questions were read; refuse when in doubt):
R1 152(3) "separated by a period of not more than 8 weeks": the days strictly between the last day of the earlier period and
   the first day of the later one number at most 56 (8 x 7; 152(5): no day disregarded), i.e. the elapsed days from that last
   day to that first day are at most 57. Linked only when the chain shows the earlier day of incapacity (known); not linked
   when even the upper bound is more than 57 days back; else undetermined.
R2 154(2) qualifying days: the days agreed between employee and employer where the facts state such an agreement for the
   week; failing agreement, the days of the week on which the contract requires the employee to be available for work (the
   parenthesis "that is to say, those days of the week on which he is required by his contract ... to be available for work");
   the regulations (not pinned) are read as fixing no other day. A week with no agreement and no required day: undetermined.
R3 153(2)(c), (7), (8): a day before the contract first takes effect, or after the day it expires or is brought to an end,
   is not within a period of entitlement as between them. So the period of entitlement begins with the commencement of the
   period of incapacity, or with the contract's first day when that falls within the period (7), or with the first day of
   the second of two linked periods when the contract first takes effect between them (8).
R4 153(2)(d): the period of entitlement ends with the day before the disqualifying period begins: a later day of the SAME
   (linked) period of incapacity is not within it; a period of incapacity that commences on or after that day: undetermined.
R5 155(3) / 153(2)(b): the maximum entitlement is reached on the first day on which the amount the employee has become entitled
   to during the period of entitlement reaches or passes 28 x the weekly rate; the period ends with that day (it is within).
   155(2) / 157(3): where a day's amount would take the aggregate past the limit, 157(3) gives the weekly rate / qualifying
   days and 155(2) a smaller amount: two outcomes at once, the amount is REFUSED (ISOLATION.md D1); whether SSP is payable
   that day is still answered (both readings: yes).
R6 157(1): one weekly rate per period of entitlement (fixed fact); normal weekly earnings are stated (s. 163 not pinned).
R7 The first piece of a sub-case: whether a period of incapacity commences with it is known only if it is not a day of
   incapacity (the day before it is not described): an incapacity piece first in the chain leaves com undetermined.
R8 Q3: the amount payable for a day is gr of its piece (0.00 where no SSP is payable); for a run of days it is the sum of the
   amounts payable for each of its days (the aggregate of 155(2)), written as a sum over the run's pieces, the tiling of the
   run by its pieces checked by date arithmetic.
R9 "the week (beginning with Sunday)": the anchor week's Sunday is a day the facts name with its day of the week, shifted
   back by its weekday number; every other week's Sunday is 7 x m days after (before) it; a piece's days lie at offsets
   0..6 from its week's Sunday; all in Lean (date arithmetic).
R10 154(3): where qualifying days are determined by agreement there is at least one qualifying day in each week: a check; a
   case whose agreed days break it contradicts the text and is refused.
No number from a case's facts is ever a coefficient: every coefficient is a literal of the pinned text (80, 100 for 80%; 28;
the 123.25 literal) or one of the values a rule enumerates (the number of qualifying days in a week, 1 to 7, and a piece's
qualifying days, 0 to 7).
"""
from __future__ import annotations

import hashlib
import json

GBP, DAY, NDAYS, CNT = "gbp_penny", "day", "elapsed_day", "count_day"
RATE_CAP = "123.25"      # 157(1)(a)
PCT = 80                 # 157(1)(b): 80%
LIMIT_WEEKS = 28         # 155(4)
LINK_GAP = 57            # R1: 152(3) "not more than 8 weeks" = at most 56 days between = elapsed at most 57
WEEKDAYS = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")

KINDS = {  # item kind -> {constant base: (unit, words)}
    "contract": {
        "nwe": (GBP, "the employee's normal weekly earnings under the contract"),
        "rate": (GBP, "the weekly rate of statutory sick pay (s. 157(1))"),
        "lim": (GBP, "the entitlement limit (s. 155(4))"),
        "cst": (DAY, "the day on which the contract of service first takes effect"),
        "cen": (DAY, "the day on which the contract of service expires or is brought to an end"),
        "dqs": (DAY, "the day on which the disqualifying period begins"),
    },
    "week": {
        "sun": (DAY, "the Sunday with which the week begins"),
        "anc": (DAY, "the day of this week the facts name with its day of the week"),
        "nq": (CNT, "the number of days in the week which are qualifying days"),
        **{f"iq{j}": (CNT, f"one if the week's {WEEKDAYS[j]} is a qualifying day, else zero") for j in range(7)},
    },
    "piece": {
        "st": (DAY, "the first day of the piece"),
        "en": (DAY, "the last day of the piece"),
        "os": (NDAYS, "the days from the week's Sunday to the piece's first day"),
        "oe": (NDAYS, "the days from the week's Sunday to the piece's last day"),
        "k": (CNT, "the number of the piece's days which are qualifying days"),
        "lst": (DAY, "the last day of incapacity for work up to the end of the piece (or an upper bound)"),
        "g": (NDAYS, "the days from that last day of incapacity before the piece to the piece's first day"),
        "accp": (GBP, "the amount the employee has become entitled to during the period of entitlement before the piece"),
        "acc": (GBP, "the amount the employee has become entitled to during the period of entitlement up to the end of the piece"),
        "gr": (GBP, "the amount of statutory sick pay payable for the days of the piece"),
        "pst": (DAY, "the day with which the (single) period of incapacity for work the piece belongs to commences"),
    },
    "run": {
        "rs": (DAY, "the first day of the days asked about"),
        "re": (DAY, "the last day of the days asked about"),
        "rn": (GBP, "the amount of statutory sick pay payable for the days asked about"),
    },
}
STEP_BASES = ("rate", "lim", "sun", "nq", "k", "lst", "accp", "acc", "gr", "pst", "rn")

FACTS = {  # unary facts (the encoder states each true or false)
    "dis": "on every day of the piece the employee has some specific disease or bodily or mental disablement",
    "cannot": "on every day of the piece the employee, by reason of it, cannot do work which he can reasonably be expected "
              "to do under the contract (stated judgment)",
    "deemed": "on every day of the piece regulations deem the employee incapable of work",
    "has_end": "the contract's end date is stated",
    "has_dq": "a disqualifying period begins on a stated day (153(2)(d), (12): fixed fact)",
    "agr": "qualifying days for the week are determined by agreement between the employee and the employer",
    **{f"agd{j}": f"the agreed qualifying days of the week include its {WEEKDAYS[j]}" for j in range(7)},
    **{f"req{j}": f"the contract requires the employee to be available for work on the week's {WEEKDAYS[j]}" for j in range(7)},
    **{f"anc{j}": f"the named day of the week (anc) is a {WEEKDAYS[j]}" for j in range(7)},
}
STATED = ("cannot",)
DERIVED = {
    "inc": "every day of the piece is a day of incapacity for work in relation to the contract (s. 151(4))",
    "com": "a period of incapacity for work commences with the first day of the piece (s. 152(2), (5))",
    "known": "the last day of incapacity up to the end of the piece is one the chain shows",
    "lnk": "the period of incapacity commencing with the piece and the one before are treated as one (s. 152(3))",
    "inpoe": "the days of the piece fall within a period of entitlement (s. 153(1), (2), (7), (8))",
    "pay": "statutory sick pay is payable for the day (s. 151(1), 153(1), 154(1))",
    "ovr": "the aggregate during the period of entitlement passes the entitlement limit within the piece (s. 155(2))",
}


# --- formula helpers (ve-quantity@1 wire shapes) --------------------------------------------------------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def gbp(v): return ["decimal", GBP, v]
def nd(v): return ["decimal", NDAYS, str(v)]
def cnt(v): return ["decimal", CNT, str(v)]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def scale(tag, kk, t): return ["scale", tag, str(kk), t]
def no_later(a, b): return ["date_no_later", a, b]
def before(a, b): return ["date_before", a, b]
def shift(a, b, n): return ["shift_days", a, b, str(n)]       # a is n days after b
def elapsed(a, b, n): return ["elapsed_days", a, b, n]       # the elapsed days from a to b equal n
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
    r = terms[-1]
    for t in reversed(terms[:-1]):
        r = ["add", unit, t, r]
    return r


UNIT_OF = {b: u for kind in KINDS.values() for b, (u, _) in kind.items()}


def k(base, x):
    """Per-item integer constant."""
    return ["const", UNIT_OF[base], f"{base}_{x}"]


def key(formula):
    return json.dumps(formula, sort_keys=True, separators=(",", ":"))


def A(p, x):
    """The target key of a unary atom."""
    return key(U(p, x))


# --- the sub-case context -----------------------------------------------------------------------------------------

class Ctx:
    """contract: the contract item id; weeks: [(id, m)], m = weeks after the anchor week (0 = the anchor week, whose
    named day anchors the Sundays); pieces: [(id, week id or None, (first offset, last offset) or None)] in time order;
    runs: [(id, [piece ids])]; asked: piece ids asked as days. The grounding's week and offsets are search aids: Lean
    checks them."""

    def __init__(self, contract="c", weeks=(), pieces=(), runs=(), asked=(), has_dq=False):
        self.contract = contract
        self.weeks = [tuple(w) for w in weeks]
        self.spans = [tuple(p) for p in pieces]
        self.pieces = [(p[0], p[1]) for p in self.spans]
        self.runs = [(r, list(ps)) for r, ps in runs]
        self.asked = list(asked)
        self.has_dq = has_dq

    def piece_spans(self):
        return self.spans

    @property
    def items(self):
        return ([(self.contract, "contract")] + [(w, "week") for w, _ in self.weeks]
                + [(p, "piece") for p, _ in self.pieces] + [(r, "run") for r, _ in self.runs])


# --- the rules, unit by unit ----------------------------------------------------------------------------------------

def _rate(ctx):
    """157(1): the lower of 123.25 and 80% of normal weekly earnings (written 100 x rate = 80 x earnings)."""
    cc = ctx.contract
    cap100 = scale(GBP, 100, gbp(RATE_CAP))
    e80 = scale(GBP, PCT, k("nwe", cc))
    return [(Implies(Le(cap100, e80), Eq(k("rate", cc), gbp(RATE_CAP))), f"rate_{cc}"),
            (Implies(Lt(e80, cap100), Eq(scale(GBP, 100, k("rate", cc)), e80)), f"rate_{cc}")]


def _limit(ctx):
    """155(4): 28 times the weekly rate."""
    cc = ctx.contract
    return [(Eq(k("lim", cc), scale(GBP, LIMIT_WEEKS, k("rate", cc))), f"lim_{cc}")]


def _inc(ctx):
    """151(4): incapable by reason of some specific disease or disablement of the work he can reasonably be expected to
    do under the contract, or deemed so by regulations. 152(6): no condition on the contract's dates or on the days he is
    required to be available (carried by structure: none here)."""
    return [(Iff(U("inc", x), Or(And(U("dis", x), U("cannot", x)), U("deemed", x))), A("inc", x)) for x, _ in ctx.pieces]


def _consecutive(x, p):
    return shift(k("st", x), k("en", p), 1)   # 152(5): no day of the week disregarded: the next calendar day


def _com(ctx):
    """152(2): a period of incapacity for work is one day or two or more consecutive days of incapacity; one commences
    with x when x is incapacity and the day before (the end of p, when x follows it) is not (R7 for the first piece)."""
    out = []
    for i, (x, _) in enumerate(ctx.pieces):
        if i == 0:
            out.append((Implies(Not(U("inc", x)), Not(U("com", x))), A("com", x)))
            continue
        p = ctx.pieces[i - 1][0]
        out.append((Iff(U("com", x), And(U("inc", x), Not(And(_consecutive(x, p), U("inc", p))))), A("com", x)))
    return out


def _last(ctx):
    """The chain's last day of incapacity (R1): the piece's last day if it is incapacity; else the one before; for a
    first piece that is not, the day before its first day as an upper bound (not known)."""
    out = []
    for i, (x, _) in enumerate(ctx.pieces):
        out.append((Implies(U("inc", x), Eq(k("lst", x), k("en", x))), f"lst_{x}"))
        out.append((Implies(U("inc", x), U("known", x)), A("known", x)))
        if i == 0:
            out.append((Implies(Not(U("inc", x)), shift(k("st", x), k("lst", x), 1)), f"lst_{x}"))
            out.append((Implies(Not(U("inc", x)), Not(U("known", x))), A("known", x)))
        else:
            p = ctx.pieces[i - 1][0]
            out.append((Implies(Not(U("inc", x)), Eq(k("lst", x), k("lst", p))), f"lst_{x}"))
            out.append((Implies(Not(U("inc", x)), Iff(U("known", x), U("known", p))), A("known", x)))
    return out


def _link(ctx):
    """152(3): two periods of incapacity separated by a period of not more than 8 weeks are treated as one (R1)."""
    out = []
    for i, (x, _) in enumerate(ctx.pieces):
        if i == 0:
            out.append((Implies(Not(U("com", x)), Not(U("lnk", x))), A("lnk", x)))
            continue
        p = ctx.pieces[i - 1][0]
        out.append((elapsed(k("lst", p), k("st", x), k("g", x)), f"g_{x}"))
        out.append((Implies(And(U("com", x), U("known", p), Le(k("g", x), nd(LINK_GAP))), U("lnk", x)), A("lnk", x)))
        out.append((Implies(And(U("com", x), Lt(nd(LINK_GAP), k("g", x))), Not(U("lnk", x))), A("lnk", x)))
        out.append((Implies(Not(U("com", x)), Not(U("lnk", x))), A("lnk", x)))
    return out


def _accp(ctx):
    """155(3) 'the amount to which the employee has become entitled ... during the period of entitlement': before x, the
    running total of the same (single) period of incapacity's period of entitlement, from 0 where a new one commences."""
    out = []
    for i, (x, _) in enumerate(ctx.pieces):
        fresh = And(U("com", x), Not(U("lnk", x)))
        if i == 0:
            out.append((Implies(Not(U("inc", x)), Eq(k("accp", x), gbp("0.00"))), f"accp_{x}"))
            out.append((Implies(fresh, Eq(k("accp", x), gbp("0.00"))), f"accp_{x}"))
            continue
        p = ctx.pieces[i - 1][0]
        out.append((Implies(fresh, Eq(k("accp", x), gbp("0.00"))), f"accp_{x}"))
        out.append((Implies(Or(Not(U("com", x)), U("lnk", x)), Eq(k("accp", x), k("acc", p))), f"accp_{x}"))
    return out


def _acc(ctx):
    return [(Eq(k("acc", x), ["add", GBP, k("accp", x), k("gr", x)]), f"acc_{x}") for x, _ in ctx.pieces]


def _pst(ctx):
    """The commencement day of the (single) period of incapacity x belongs to: needed only for R4 (153(2)(d))."""
    if not ctx.has_dq:
        return []
    out = []
    for i, (x, _) in enumerate(ctx.pieces):
        fresh = And(U("com", x), Not(U("lnk", x)))
        out.append((Implies(fresh, Eq(k("pst", x), k("st", x))), f"pst_{x}"))
        if i > 0:
            p = ctx.pieces[i - 1][0]
            out.append((Implies(Or(Not(U("com", x)), U("lnk", x)), Eq(k("pst", x), k("pst", p))), f"pst_{x}"))
    return out


def _poe_parts(x, ctx):
    cc = ctx.contract
    cwin = And(no_later(k("cst", cc), k("st", x)),
               Or(Not(U("has_end", cc)), no_later(k("en", x), k("cen", cc))))
    maxed = Le(k("lim", cc), k("accp", x))
    dq = And(U("has_dq", cc), no_later(k("dqs", cc), k("en", x)))
    return cwin, maxed, dq


def _inpoe(ctx):
    """153(1)-(2) with (7), (8) (R3), (b) max entitlement (R5), (c) contract end (R3), (d) disqualifying period (R4)."""
    out = []
    cc = ctx.contract
    for x, _ in ctx.pieces:
        cwin, maxed, dq = _poe_parts(x, ctx)
        t = A("inpoe", x)
        out.append((Implies(And(U("inc", x), cwin, Not(maxed), Not(dq)), U("inpoe", x)), t))
        out.append((Implies(Not(U("inc", x)), Not(U("inpoe", x))), t))
        out.append((Implies(Not(cwin), Not(U("inpoe", x))), t))
        out.append((Implies(maxed, Not(U("inpoe", x))), t))
        if ctx.has_dq:
            out.append((Implies(And(dq, before(k("pst", x), k("dqs", cc))), Not(U("inpoe", x))), t))
    return out


def _weeks(ctx):
    """R9: the anchor week's Sunday from its named day; every other week's Sunday 7 x m days after (before) it (m = the
    week's distance from the anchor week in the grounding; whatever m, the day is a Sunday, and Lean checks each piece
    lies within its week's seven days)."""
    out = []
    anchors = [w for w, m in ctx.weeks if m == 0]
    if not anchors:
        return out
    a = anchors[0]
    for w, m in ctx.weeks:
        if m == 0:
            for j in range(7):
                out.append((Implies(U(f"anc{j}", w), shift(k("anc", w), k("sun", w), j)), f"sun_{w}"))
        elif m > 0:
            out.append((shift(k("sun", w), k("sun", a), 7 * m), f"sun_{w}"))
        else:
            out.append((shift(k("sun", a), k("sun", w), -7 * m), f"sun_{w}"))
    return out


def _qual(ctx):
    """154(2) (R2) with 157(3)'s count: the week's j-th day is a qualifying day (iq = 1) or not (iq = 0): the agreed days
    where an agreement is stated; failing agreement, the days the contract requires availability (a week with neither:
    undetermined)."""
    out = []
    for w, _ in ctx.weeks:
        anyreq = Or(*[U(f"req{j}", w) for j in range(7)])
        for j in range(7):
            t, iq = f"iq{j}_{w}", k(f"iq{j}", w)
            out.append((Implies(And(U("agr", w), U(f"agd{j}", w)), Eq(iq, cnt(1))), t))
            out.append((Implies(And(U("agr", w), Not(U(f"agd{j}", w))), Eq(iq, cnt(0))), t))
            out.append((Implies(And(Not(U("agr", w)), anyreq, U(f"req{j}", w)), Eq(iq, cnt(1))), t))
            out.append((Implies(And(Not(U("agr", w)), anyreq, Not(U(f"req{j}", w))), Eq(iq, cnt(0))), t))
    return out


def _nq(ctx):
    """157(3): the number of days which are, in the week, qualifying days."""
    return [(Eq(k("nq", w), Add(CNT, [k(f"iq{j}", w) for j in range(7)])), f"nq_{w}") for w, _ in ctx.weeks]


def _agreed_check(ctx):
    """154(3) (R10): where qualifying days are determined by agreement, at least one in each week (a check)."""
    return [(Implies(U("agr", w), Le(cnt(1), k("nq", w))), None) for w, _ in ctx.weeks]


def _kq(ctx):
    """The piece's qualifying days (for 157(3)): the piece lies in its week from offset a to offset b (days after the
    week's Sunday, checked by date arithmetic), and its qualifying days are the week's qualifying days at offsets a..b."""
    out = []
    for x, w, span in ctx.piece_spans():
        if w is None:
            continue
        a, b = span
        out.append((elapsed(k("sun", w), k("st", x), k("os", x)), f"os_{x}"))
        out.append((elapsed(k("sun", w), k("en", x), k("oe", x)), f"oe_{x}"))
        out.append((Implies(And(Eq(k("os", x), nd(a)), Eq(k("oe", x), nd(b))),
                            Eq(k("k", x), Add(CNT, [k(f"iq{j}", w) for j in range(a, b + 1)]))), f"k_{x}"))
    return out


def _gross(ctx):
    """157(3): the amount for a day is the weekly rate divided by the week's qualifying days (case split on that number,
    1 to 7); for the piece, k qualifying days in the period of entitlement: nq x gr = k x rate (k = 0: nothing)."""
    out = []
    cc = ctx.contract
    for x, w in ctx.pieces:
        t = f"gr_{x}"
        out.append((Implies(Not(U("inpoe", x)), Eq(k("gr", x), gbp("0.00"))), t))
        if w is None:
            continue
        out.append((Implies(And(U("inpoe", x), Eq(k("k", x), cnt(0))), Eq(k("gr", x), gbp("0.00"))), t))
        for q in range(1, 8):
            for kk in range(1, q + 1):
                out.append((Implies(And(U("inpoe", x), Eq(k("nq", w), cnt(q)), Eq(k("k", x), cnt(kk))),
                                    Eq(scale(GBP, q, k("gr", x)), scale(GBP, kk, k("rate", cc)))), t))
    return out


def _pay(ctx):
    """151(1) with 153(1) and 154(1), for an asked day: a day of incapacity within a period of entitlement that is a
    qualifying day (its piece has one qualifying day)."""
    return [(Iff(U("pay", x), And(U("inc", x), U("inpoe", x), Le(cnt(1), k("k", x)))), A("pay", x)) for x in ctx.asked]


def _over(ctx):
    """155(2) (R5): the aggregate passes the entitlement limit within the piece."""
    cc = ctx.contract
    return [(Iff(U("ovr", x), Lt(k("lim", cc), k("acc", x))), A("ovr", x)) for x, _ in ctx.pieces]


def _runs(ctx):
    """R8: the amount for a run of days, the sum of its days' amounts, over pieces that tile it (checked)."""
    out = []
    for r, ps in ctx.runs:
        tiled = And(Eq(k("st", ps[0]), k("rs", r)), Eq(k("en", ps[-1]), k("re", r)),
                    *[_consecutive(ps[i], ps[i - 1]) for i in range(1, len(ps))])
        out.append((Implies(tiled, Eq(k("rn", r), Add(GBP, [k("gr", x) for x in ps]))), f"rn_{r}"))
    return out


def _merge(*builders):
    return lambda ctx: [f for b in builders for f in b(ctx)]


UNITS = {
    1: ("RULE", _pay, "151(1): liable for a day of incapacity if the conditions of ss. 153 and 154 are satisfied (the "
        "payable test of an asked day: incapacity, within a period of entitlement, a qualifying day)"),
    2: ("PART", _inc, "other:judgment standard", "151(4): written (incapacity by reason of a specific disease or "
        "disablement, or deemed by regulations); 'can reasonably be expected to do under that contract' is a stated "
        "judgment (stated); the deeming regulations are not pinned (deemed: a stated fact)"),
    3: ("RULE", _merge(_com, _last), "152(2): one day or consecutive days of incapacity; commencement over the chain"),
    4: ("RULE", _link, "152(3): two periods separated by not more than 8 weeks treated as one (R1, date arithmetic in "
        "Lean)"),
    5: ("RULE", lambda ctx: [], "152(5): no day disregarded: consecutiveness is the next calendar day (the shift_days 1 "
        "of units 3 and 19's runs)"),
    6: ("PART", lambda ctx: [], "other:norm", "152(6) 'may be a day of incapacity ... notwithstanding': a permission "
        "carried only by structure (units 2-4 put no condition on the contract's dates or the required days; mutant M9)"),
    7: ("RULE", _inpoe, "153(1): the day falls within a period of entitlement (with units 8-10)"),
    8: ("RULE", _merge(_accp, _acc, _pst), "153(2): beginning with the commencement of the (single) period; ending with "
        "(a) its termination, (b) maximum entitlement (R5), (c) the contract's end (R3), (d) the day before the "
        "disqualifying period (R4; its start a stated date)"),
    9: ("RULE", lambda ctx: [], "153(7): carried by R3 in unit 7 (no day before the contract's first day is within)"),
    10: ("RULE", lambda ctx: [], "153(8): carried by R3 in unit 7 with unit 4's linking"),
    11: ("RULE", lambda ctx: [], "154(1): the qualifying-day condition of unit 1's payable test"),
    12: ("PART", _merge(_qual, _nq), "cross-reference", "154(2): agreed days, failing agreement the contract's required "
         "days (R2); 'subject to regulations' and 'determined in accordance with regulations' (not pinned) are read as "
         "fixing no other day; a week with neither: undetermined"),
    13: ("PART", _agreed_check, "other:norm", "154(3) 'there shall ... be at least one qualifying day': a requirement on "
         "agreements, carried only as a check (R10: an agreement breaking it refuses the case)"),
    14: ("PART", lambda ctx: [], "other:norm", "154(4) 'may also be a qualifying day ... another employer': a permission "
         "carried only by structure (one sub-case per employer)"),
    15: ("RULE", _over, "155(2): the aggregate in a period of entitlement may not exceed the maximum entitlement; a day "
         "whose amount would pass it: two outcomes (R5, refused)"),
    16: ("RULE", lambda ctx: [], "155(3): reached on the first day the running total reaches or passes the limit (unit "
         "8's accp/acc and unit 7's 'maxed' test)"),
    17: ("RULE", _limit, "155(4): 28 times the weekly rate"),
    18: ("PART", _rate, "definition by reference", "157(1): the lower of 123.25 and 80% (100 x rate = 80 x earnings); "
         "'normal weekly earnings' is defined in s. 163 (not pinned): a stated amount"),
    19: ("PART", _merge(_weeks, _kq, _gross, _runs), "amount arithmetic", "157(3): the weekly rate divided by the week's "
         "qualifying days, written as nq x amount = k x rate by the case split nq = 1..7 (no division in the language); "
         "a day's amount that is not a whole number of pence has no model (refused); the week's Sunday by date "
         "arithmetic from a named day (R9)"),
}


def units_table(mutant=None):
    t = dict(UNITS)
    if mutant is not None:
        t = MUTANTS[mutant][1](t)
    return t


def rules(ctx, mutant=None):
    """Ground rules for a sub-case: [{"id", "unit", "formula", "defines"}]; defines = [] for a check."""
    out = []
    for n, e in sorted(units_table(mutant).items()):
        if e[1] is None:
            continue
        for i, (f, target) in enumerate(e[1](ctx)):
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


# --- the environment for one sub-case -----------------------------------------------------------------------------

def environment(ctx, used=None):
    """used: the constant names the rules and facts mention (only those are declared)."""
    consts = {}
    for x, kind in ctx.items:
        consts[x] = {"sort": "item", "description": f"The sub-case's {kind} {x}.", "verbalisation": f"{kind} {x}"}
        for base, (u, w) in KINDS[kind].items():
            name = f"{base}_{x}"
            if used is not None and name not in used:
                continue
            consts[name] = {"sort": "$int", "unit": u, "description": f"{w[0].upper() + w[1:]} ({x}).",
                            "verbalisation": f"{w} ({x})"}
    preds = {n: {"arguments": ["item"], "description": d[0].upper() + d[1:] + "."} for n, d in {**FACTS, **DERIVED}.items()}
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "A contract, week, piece of days or run of days."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {DAY: {"scale": "1", "display": {"kind": "iso_date"}},
                      NDAYS: {"scale": "1", "display": {"kind": "decimal", "label": "days"}},
                      CNT: {"scale": "1", "display": {"kind": "decimal", "label": "qdays"}},
                      GBP: {"scale": "100", "display": {"kind": "money", "currency": "GBP", "input_symbol": "£"}}}}


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


def _drop_deemed(builder):
    return lambda ctx: [(Iff(U("inc", x), And(U("dis", x), U("cannot", x))), A("inc", x)) for x, _ in ctx.pieces]


def _no_link(builder):
    return lambda ctx: [(Not(U("lnk", x)), A("lnk", x)) for x, _ in ctx.pieces]


def _divide_by_seven(builder):
    """157(3) misread: the weekly rate divided by 7 whatever the week's qualifying days."""
    def b(ctx):
        out = []
        for f, tg in builder(ctx):
            if tg and tg.startswith("gr_") and f[0] == "implies" and f[2][0] == "eq" and f[2][1][0] == "scale":
                f = [f[0], f[1], Eq(scale(GBP, 7, f[2][1][3]), f[2][2])]
            out.append((f, tg))
        return out
    return b


def _inc_needs_contract(builder):
    """152(6) dropped: a day of incapacity only within the contract's dates (needs the contract facts in the piece)."""
    def b(ctx):
        cc = ctx.contract
        return [(Iff(U("inc", x), And(Or(And(U("dis", x), U("cannot", x)), U("deemed", x)),
                                      no_later(k("cst", cc), k("st", x)))), A("inc", x)) for x, _ in ctx.pieces]
    return b


def _poe_drop(part):
    """Drop one ending of 153(2) / R3 from unit 7's inpoe rules."""
    def wrap(builder):
        def b(ctx):
            out = []
            for x, _ in ctx.pieces:
                cwin, maxed, dq = _poe_parts(x, ctx)
                cc = ctx.contract
                if part == "start":
                    cwin = Or(Not(U("has_end", cc)), no_later(k("en", x), k("cen", cc)))
                if part == "end":
                    cwin = no_later(k("cst", cc), k("st", x))
                if part == "max":
                    maxed = FALSE
                if part == "dq":
                    dq = FALSE
                t = A("inpoe", x)
                out.append((Implies(And(U("inc", x), cwin, Not(maxed), Not(dq)), U("inpoe", x)), t))
                out.append((Implies(Not(U("inc", x)), Not(U("inpoe", x))), t))
                out.append((Implies(Not(cwin), Not(U("inpoe", x))), t))
                out.append((Implies(maxed, Not(U("inpoe", x))), t))
                if ctx.has_dq and part != "dq":
                    out.append((Implies(And(dq, before(k("pst", x), k("dqs", cc))), Not(U("inpoe", x))), t))
            return out
        return b
    return wrap


def _req_over_agreed(builder):
    def b(ctx):
        out = []
        for w, _ in ctx.weeks:
            for j in range(7):
                t, iq = f"iq{j}_{w}", k(f"iq{j}", w)
                out.append((Implies(U(f"req{j}", w), Eq(iq, cnt(1))), t))
                out.append((Implies(Not(U(f"req{j}", w)), Eq(iq, cnt(0))), t))
        return out
    return lambda ctx: b(ctx) + [x for x in builder(ctx) if x[1] and x[1].startswith("nq")]


# A 152(6) mutant (_inc_needs_contract: a day before the contract's first day is not a day of incapacity) changes no
# answer of the smoke cases: under R3 no day before the contract is within a period of entitlement either way, and the
# period's start moves only where nothing is yet counted. It is not listed (unit 6 is a ledger row, other:norm).
MUTANTS = {
    "M1": ("AMOUNT: 157(1)(a) 123.25 read as 123.00", _swap(18, _json_sub('"123.25"', '"123.00"'))),
    "M2": ("AMOUNT: 157(1)(b) 80% read as 75%", _swap(18, _json_sub('"gbp_penny", "80"', '"gbp_penny", "75"'))),
    "M3": ("AMOUNT: 155(4) 28 times read as 27 times", _swap(17, _json_sub('"28"', '"27"'))),
    "M4": ("AMOUNT: 157(3) divided by the week's qualifying days read as divided by 7", _swap(19, _divide_by_seven)),
    "M5": ("DEEMING: 151(4) 'or is deemed in accordance with regulations' dropped", _swap(2, _drop_deemed)),
    "M6": ("DEEMING: 152(3) 'treated as a single period' dropped", _swap(4, _no_link)),
    "M7": ("THRESHOLD: 152(3) 8 weeks read as 56 days elapsed (55 between)", _swap(4, _json_sub('"elapsed_day", "57"', '"elapsed_day", "56"'))),
    "M8": ("CONDITION: 153(7)/(8) R3 dropped (days before the contract's first day within the period)", _swap(7, _poe_drop("start"))),
    "M10": ("ENDING: 153(2)(c) the contract's end dropped", _swap(7, _poe_drop("end"))),
    "M11": ("ENDING: 153(2)(b) maximum entitlement dropped", _swap(7, _poe_drop("max"))),
    "M12": ("ENDING: 153(2)(d) the disqualifying period dropped", _swap(7, _poe_drop("dq"))),
    "M13": ("QUALIFYING: 154(2) agreed days ignored (the required days always)", _swap(12, _req_over_agreed)),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
