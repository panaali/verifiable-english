"""Apprenticeship levy, FA 2016 ss. 99-101 (statute corpus batch 3, law 7 of 9): the VE translation, one pass with today's
language.

Row statute-corpus-app-levy (dri-statute-corpus-app-levy-1123, Opus 5.5). SAME-FAMILY. Written from the pinned source only
(manage-agents reviews/spare/statute-corpus/stock/app-levy/source.txt, sha256 079bde29...b392d59f) BEFORE the encoder's
question file was opened. Evidence branch: nothing here is a Lean kernel line, a profile, a refuses pair or a lint change;
nothing merges.

UNITS maps each in-scope unit n of stock/app-levy/units.jsonl (tools/sample5.py --units app-levy, 28 units, 0 table rows) to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one case;
  ("PART", builder, cause, note) written except the part named in the note (stated / not written);
  ("NOT", builder|None, cause, note) not written (the ledger row's cause, CAUSES.tsv v2).
Grounding is mechanical over the case's named items (closed world over them: an encoding convention, encode.py C1):
persons (employers), earnings items (one stated payment of earnings, or the stated earnings of one earner, with its payer),
and groups (companies the facts state are connected with one another at the beginning of the tax year). One context is
one tax year. "The number of the members" (s. 101(12)) is grounded as a case split over which of the group's companies
are members (the coefficient n is a count of named items, never a number from the facts); every other coefficient is a
literal of the pinned text (0.5 % = 5 / 1000, GBP 15,000, zero). No product of two quantities exists in the language:
s. 101(7)'s "multiplying ... by 15,000 / T" (T a sum of stated amounts) is NOT written (ledger: amount arithmetic).

Translator readings, fixed before any question was read (each decides answers; a refusal is an OPEN answer):
R1  A person on whom levy is not charged has an amount charged of 0.00 (the brief's answer form for Q2).
R2  When s. 101(8) applies (and (13) does not), each relevant member's allowance is the s. 101(7) amount (NOT written:
    refused) and each other member's is zero (s. 101(10)); when (13) applies (and (8) does not), each member's is the
    s. 101(12) amount. "HMRC must determine ... accordingly subsection (2) is treated as never having applied": the
    (7) / (10) / (12) amounts replace the members' determination by force of the text ("is to be entitled", "is entitled").
R3  Both (8) and (13) apply to one unit: two outcomes at once, refused (no allowance rule fires).
R4  A member's allowance with neither (8) nor (13) applying is the amount the members' determination gives it, if the
    determination complies with (3) and (4); with no determination, or one that does not comply and is not corrected under
    R5, no rule gives an amount: refused.
R5  s. 101(5): an alteration has effect only where the determination failed to comply with (4) (the total is not
    GBP 15,000) and the altered determination complies with (3) and (4); any other alteration is ignored.
R6  s. 101(14) with (13)(a): where the case states the amounts due and payable, they are used; where it does not, the
    total due and payable for the tax year is the members' relevant percentages of their pay bills together minus the
    single GBP 15,000 of s. 101(4) (the members' allowances taken as one pool).
R7  A company unit: the companies of a stated group (connected with one another at the beginning of the tax year) that
    are companies, not charities, and entitled to a levy allowance, when at least two of the group are; a group whose
    entitled companies are fewer than two forms no unit and each company keeps s. 99(5)'s GBP 15,000.
R8  s. 101(12) rounding: a stated rounding (up or down, or HMRC's figure) is used only where it is the exact share
    rounded up or down to the penny; an exact share needs no rounding.
R9  A person with no pay bill is entitled to no levy allowance: its allowance is answered 0.00 (s. 99(4): "if any").
R10 A case that states the half-up convention for an amount charged ("no rounding until the answer; the answer to the
    nearest penny, half up") is answered to the penny half up; else the amount charged must be exact in pence (no
    exact amount: refused).
"""
from __future__ import annotations

import hashlib
import itertools
import json

GBP = "gbp_penny"
ALLOWANCE = "15000.00"  # s. 99(5), s. 101(4)
PCT_NUM, PCT_DEN = 5, 1000  # s. 99(6): 0.5 %

INT_UNITS = {  # per-item integer constants: base name -> (unit, words)
    # stated (encoder)
    "earn": (GBP, "the earnings of the earnings item in the tax year (as for Class 1 contributions)"),
    "det": (GBP, "the levy allowance the members' determination under s. 101(2) gives the company"),
    "alt": (GBP, "the levy allowance the members' later altered determination gives the company"),
    "ret": (GBP, "the amount of levy allowance set out in the company's apprenticeship levy return"),
    "paid": (GBP, "the amount the company paid in respect of apprenticeship levy for the period the facts state"),
    "due": (GBP, "the amount due and payable by the company for the period the facts state"),
    "rnd": (GBP, "HMRC's rounded amount of the company's share under s. 101(12)"),
    # derived (run.py steps)
    "part": (GBP, "the earnings of the item counted in its payer's pay bill"),
    "pb": (GBP, "the amount of the person's pay bill for the tax year (s. 100(2))"),
    "alw": (GBP, "the amount of the person's levy allowance for the tax year"),
    "chg": (GBP, "the amount of apprenticeship levy charged on the person for the tax year"),
    "dp": (GBP, "the determination's amount for the company if it is a member, else zero"),
    "ap": (GBP, "the altered determination's amount for the company if it is a member, else zero"),
    "rp": (GBP, "the amount set out in the company's return if it is a relevant member, else zero"),
    "pp": (GBP, "the amount the company paid if it is a member, else zero"),
    "qp": (GBP, "the amount due and payable by the company if it is a member, else zero"),
    "mpb": (GBP, "the company's pay bill if it is a member, else zero"),
}
STEP_BASES = ("part", "pb", "alw", "chg", "dp", "ap", "rp", "pp", "qp", "mpb")

FACTS_PERSON = {  # unary facts on a person (employer)
    "company": "the person is a company within the meaning of s. 1121(1) CTA 2010 (stated)",
    "llp": "the person is a limited liability partnership",
    "charity": "the person is a charity (s. 102; fixed fact: no)",
    "ret9": "the company has made an apprenticeship levy return (a return under regulations under s. 105(4)) on the "
            "basis that it is entitled to a levy allowance (whether or not of zero) for the tax year",
    "aware": "HMRC is aware that the company made that return and of the allowance it sets out",
    "notified8": "HMRC has notified the company in writing that HMRC is considering taking action under s. 101(6)",
    "notified13": "HMRC has notified the company in writing that HMRC is considering taking action under s. 101(11)",
    "rnd_up": "HMRC rounds the company's s. 101(12) share up to the penny (stated judgment)",
    "rnd_down": "HMRC rounds the company's s. 101(12) share down to the penny (stated judgment)",
    "rnd_fig": "the facts state HMRC's rounded figure for the company's s. 101(12) share (stated judgment)",
    "halfup": "the case states for the person's amount charged: no rounding until the answer; the answer to the nearest "
              "penny, half up",
}
FACTS_EARN = {  # unary facts on an earnings item
    "sec": "the payer is the secondary contributor in relation to the payments of earnings of the item to, or for the "
           "benefit of, an employed earner in the tax year",
    "liab": "in consequence the payer incurs a liability to pay secondary Class 1 contributions under Part 1 SSCBA 1992 "
            "on the item's earnings (including a liability of GBP 0)",
    "butfor": "the payer would incur such a liability on the item's earnings but for the condition in s. 6(1)(b) SSCBA",
}
FACTS_GROUP = {  # unary facts on a group
    "detmade": "the members made a determination under s. 101(2) of the allowance each is to have",
    "altmade": "the members later altered that determination",
    "not_taken8": "the remedial action specified in HMRC's s. 101(8)(b) notice was not taken within the period it specifies",
    "not_taken13": "the remedial action specified in HMRC's s. 101(13)(c) notice was not taken within the period it "
                   "specifies",
    "noreturns": "the members have made no apprenticeship levy returns for any period in the tax year",
    "insufficient": "the returns made do not contain sufficient information to enable HMRC to determine how the whole of "
                    "the GBP 15,000 is to be used by the members (stated judgment)",
    "dues_stated": "the facts state the amounts due and payable by the members for the period",
}
BINARY = {"conn": "(person, group) the company is connected with each other company of the group at the beginning of "
                  "the tax year (NICA 2014 Sch. 1 Part 1, stated)"}
STATED = ("rnd_up", "rnd_down", "rnd_fig", "insufficient")
DERIVED_PERSON = {
    "isco": "the person is a company for this Part (s. 101(18): includes a limited liability partnership)",
    "haspb": "the person has a pay bill for the tax year (s. 100(1))",
    "entitled": "the person is entitled to a levy allowance for the tax year (s. 99(4))",
    "member": "the company is a member of a company unit for the tax year (s. 101(1))",
    "relevant": "the company is a relevant member (s. 101(8)(a)(i))",
    "charged": "apprenticeship levy is charged on the person for the tax year (s. 99(1))",
    "liable": "the person is liable to pay the amount charged (s. 99(3))",
}
DERIVED_EARN = {"counted": "the payer incurs (or is treated as incurring) a liability on the item's earnings "
                           "(s. 100(1)(b), (3))"}
DERIVED_GROUP = {
    "detok3": "no member's amount in the determination is negative (s. 101(3))",
    "detok4": "the members' amounts in the determination total GBP 15,000 (s. 101(4))",
    "altok3": "no member's amount in the altered determination is negative",
    "altok4": "the members' amounts in the altered determination total GBP 15,000",
    "tworel": "two or more members are relevant members (s. 101(8)(a)(i))",
    "gt8": "the relevant returns together imply a total greater than GBP 15,000 (s. 101(8)(a)(ii))",
    "ntf8": "HMRC has notified every relevant member (s. 101(8)(b))",
    "app8": "s. 101(8) applies",
    "a13": "the members' total paid is less than the total due and payable (s. 101(13)(a), (14))",
    "ntf13": "HMRC has notified all the members (s. 101(13)(c))",
    "app13": "s. 101(13) applies",
}


# --- formula helpers (the ve-quantity@1 wire shapes; council_tax conventions) -------------------------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def B(p, x, y): return ["binary", p, c(x), c(y)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def gbp(v): return ["decimal", GBP, v]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
def scale(k, t): return ["scale", GBP, str(k), t]
def add(a, b): return ["add", GBP, a, b]
TRUE, FALSE = ["top"], ["bottom"]
ZERO = gbp("0.00")


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


def Sum(*ts):
    ts = list(ts)
    if not ts:
        return ZERO
    r = ts[-1]
    for t in reversed(ts[:-1]):
        r = add(t, r)
    return r


def k(base, x):
    """Per-item integer constant."""
    return ["const", INT_UNITS[base][0], f"{base}_{x}"]


def iff_u(p, x, body): return Iff(U(p, x), body)


# --- the case context ---------------------------------------------------------------------------------------------

class Ctx:
    """One tax year of a case. persons: employers; earnings: {item: payer}; groups: {group: [companies]} (the stated
    connected groups; a company in at most one group)."""

    def __init__(self, persons=(), earnings=None, groups=None):
        self.persons = list(persons)
        self.earnings = dict(earnings or {})
        self.groups = {g: list(m) for g, m in (groups or {}).items()}
        seen = [x for m in self.groups.values() for x in m]
        if len(seen) != len(set(seen)):
            raise ValueError("a company in two groups")
        if set(self.earnings.values()) - set(self.persons) or set(seen) - set(self.persons):
            raise ValueError("an earnings payer or group company is not a named person")

    @property
    def items(self):
        return self.persons + list(self.earnings) + list(self.groups)

    def jobs(self, x):
        return [j for j, p in self.earnings.items() if p == x]

    def group_of(self, x):
        for g, m in self.groups.items():
            if x in m:
                return g
        return None


def per_person(fn):
    return lambda ctx: [f for x in ctx.persons for f in fn(x, ctx)]


def per_earn(fn):
    return lambda ctx: [f for j in ctx.earnings for f in fn(j, ctx)]


def per_group(fn):
    return lambda ctx: [f for g in ctx.groups for f in fn(g, ctx.groups[g], ctx)]


def per_member(fn):
    """fn(x, g, members, ctx) for every company named in a group."""
    return lambda ctx: [f for g, m in ctx.groups.items() for x in m for f in fn(x, g, m, ctx)]


# --- s. 99 ---------------------------------------------------------------------------------------------------------

def _charged(x, ctx, den=PCT_DEN, strict=True):
    """s. 99(1): pay bill, and the relevant percentage (5 / 1000) of it exceeds the allowance:
    5 x pb > 1000 x alw (whole-number coefficients)."""
    cmp = Lt if strict else Le
    return [iff_u("charged", x, And(U("haspb", x), cmp(scale(den, k("alw", x)), scale(PCT_NUM, k("pb", x)))))]


def _amount(x, ctx, den=PCT_DEN, deduct=True):
    """s. 99(2): amount = N - A, N = 0.5 % of the pay bill: 1000 x chg = 5 x pb - 1000 x alw (R10: exact, or the
    stated half-up convention as two bounds); R1: not charged -> 0.00."""
    diff = add(scale(PCT_NUM, k("pb", x)), scale(-den, k("alw", x))) if deduct else scale(PCT_NUM, k("pb", x))
    lhs = scale(den, k("chg", x))
    half = gbp(f"{den // 200}.{(den // 2) % 100:02d}")  # half a penny x den
    return [Implies(And(U("charged", x), Not(U("halfup", x))), Eq(lhs, diff)),
            Implies(And(U("charged", x), U("halfup", x)),
                    And(Le(add(lhs, scale(-1, half)), diff), Lt(diff, add(lhs, half)))),
            Implies(Not(U("charged", x)), Eq(k("chg", x), ZERO))]


def _liable(x, ctx):
    return [iff_u("liable", x, U("charged", x))]


def _entitled(x, ctx):
    """s. 99(4): a person who has a pay bill is entitled to a levy allowance (s. 103: none, fixed fact)."""
    return [iff_u("entitled", x, U("haspb", x))]


def _basic_allowance(x, ctx):
    """s. 99(5): GBP 15,000 except where s. 101 (or 102: no charity, fixed fact) provides otherwise: an entitled person
    who is not a member of a company unit. R9: no allowance -> 0.00."""
    return [Implies(And(U("entitled", x), Not(U("member", x))), Eq(k("alw", x), gbp(ALLOWANCE))),
            Implies(Not(U("entitled", x)), Eq(k("alw", x), ZERO))]


# --- s. 100 --------------------------------------------------------------------------------------------------------

def _counted(j, ctx):
    """s. 100(1)(a), (b) with (3) (treated as incurring a liability it would incur but for s. 6(1)(b)) and (6) (a GBP 0
    liability is a liability: carried in the stated fact's words)."""
    return [iff_u("counted", j, And(U("sec", j), Or(U("liab", j), U("butfor", j))))]


def _counted_no_deeming(j, ctx):
    return [iff_u("counted", j, And(U("sec", j), U("liab", j)))]


def _haspb(x, ctx):
    return [iff_u("haspb", x, Or(*[U("counted", j) for j in ctx.jobs(x)]))]


def _part(j, ctx):
    return [Implies(U("counted", j), Eq(k("part", j), k("earn", j))),
            Implies(Not(U("counted", j)), Eq(k("part", j), ZERO))]


def _paybill(x, ctx):
    """s. 100(2): the total of the earnings in respect of which the liabilities are incurred."""
    return [Eq(k("pb", x), Sum(*[k("part", j) for j in ctx.jobs(x)]))]


# --- s. 101 --------------------------------------------------------------------------------------------------------

def _isco(x, ctx):
    """s. 101(18): 'company' (CTA 2010 s. 1121(1), stated) includes a limited liability partnership."""
    return [iff_u("isco", x, Or(U("company", x), U("llp", x)))]


def _cand(y, g):
    return And(U("isco", y), Not(U("charity", y)), B("conn", y, g), U("entitled", y))


def _member(x, ctx):
    """s. 101(1) (R7): two or more companies, not charities, connected with one another at the beginning of the year,
    each entitled to a levy allowance."""
    g = ctx.group_of(x)
    if g is None:
        return [iff_u("member", x, FALSE)]
    others = [y for y in ctx.groups[g] if y != x]
    return [iff_u("member", x, And(_cand(x, g), Or(*[_cand(y, g) for y in others])))]


def _member_parts(x, g, m, ctx):
    out = []
    for part, base in (("dp", "det"), ("ap", "alt"), ("pp", "paid"), ("qp", "due"), ("mpb", "pb")):
        out += [Implies(U("member", x), Eq(k(part, x), k(base, x))),
                Implies(Not(U("member", x)), Eq(k(part, x), ZERO))]
    out += [Implies(U("relevant", x), Eq(k("rp", x), k("ret", x))),
            Implies(Not(U("relevant", x)), Eq(k("rp", x), ZERO))]
    return out


def _det_checks(g, m, ctx):
    """s. 101(3), (4): the determination's amounts (and an altered determination's) over the members."""
    return [iff_u("detok3", g, And(*[Implies(U("member", y), Le(ZERO, k("det", y))) for y in m])),
            iff_u("detok4", g, Eq(Sum(*[k("dp", y) for y in m]), gbp(ALLOWANCE))),
            iff_u("altok3", g, And(*[Implies(U("member", y), Le(ZERO, k("alt", y))) for y in m])),
            iff_u("altok4", g, Eq(Sum(*[k("ap", y) for y in m]), gbp(ALLOWANCE)))]


def _relevant(x, g, m, ctx):
    """s. 101(8)(a)(i), (9): a member that has made a return on the basis that it is entitled to an allowance, of which
    HMRC is aware."""
    return [iff_u("relevant", x, And(U("member", x), U("ret9", x), U("aware", x)))]


def _s8(g, m, ctx):
    pairs = [And(U("relevant", y), U("relevant", z)) for y, z in itertools.combinations(m, 2)]
    return [iff_u("tworel", g, Or(*pairs)),
            iff_u("gt8", g, Lt(gbp(ALLOWANCE), Sum(*[k("rp", y) for y in m]))),
            iff_u("ntf8", g, And(*[Implies(U("relevant", y), U("notified8", y)) for y in m])),
            iff_u("app8", g, And(U("tworel", g), U("gt8", g), U("ntf8", g), U("not_taken8", g)))]


def _s13(g, m, ctx):
    """s. 101(13) with (14) (R6)."""
    paid = Sum(*[k("pp", y) for y in m])
    due = Sum(*[k("qp", y) for y in m])
    pool = add(Sum(*[scale(PCT_NUM, k("mpb", y)) for y in m]), scale(-PCT_DEN, gbp(ALLOWANCE)))
    a = Or(And(U("dues_stated", g), Lt(paid, due)),
           And(Not(U("dues_stated", g)), Lt(scale(PCT_DEN, paid), pool)))
    return [iff_u("a13", g, a),
            iff_u("ntf13", g, And(*[Implies(U("member", y), U("notified13", y)) for y in m])),
            iff_u("app13", g, And(U("a13", g), Or(U("noreturns", g), U("insufficient", g)), U("ntf13", g),
                                  U("not_taken13", g)))]


def _alw_determination(x, g, m, ctx):
    """s. 101(2)-(5) (R4, R5): neither (8) nor (13) applies."""
    base = And(U("member", x), Not(U("app8", g)), Not(U("app13", g)), U("detmade", g))
    return [Implies(And(base, U("detok3", g), U("detok4", g)), Eq(k("alw", x), k("det", x))),
            Implies(And(base, Not(U("detok4", g)), U("altmade", g), U("altok3", g), U("altok4", g)),
                    Eq(k("alw", x), k("alt", x)))]


def _alw_10(x, g, m, ctx):
    """s. 101(6), (10) (R2): (8) applies and (13) does not; a member that is not a relevant member: zero."""
    return [Implies(And(U("member", x), U("app8", g), Not(U("app13", g)), Not(U("relevant", x))),
                    Eq(k("alw", x), ZERO))]


def _alw_7(x, g, m, ctx):
    """s. 101(7): NOT written (15,000 / T x the return's amount: a product of two quantities)."""
    return []


def _alw_12(x, g, m, ctx, extra=0):
    """s. 101(11), (12) (R2, R8): (13) applies and (8) does not; 15,000 / N, N the number of the members, as a case split
    over which of the group's companies are members (n x alw = 15,000), or the stated rounding."""
    out = []
    others = [y for y in m if y != x]
    for r in range(1, len(others) + 1):
        for chosen in itertools.combinations(others, r):
            n = len(chosen) + 1 + extra
            who = And(U("member", x), *[U("member", y) for y in chosen],
                      *[Not(U("member", y)) for y in others if y not in chosen])
            guard = And(who, U("app13", g), Not(U("app8", g)))
            nx = scale(n, k("alw", x))
            cent = gbp(f"{n // 100}.{n % 100:02d}")  # n pence
            hi, lo = add(gbp(ALLOWANCE), cent), add(gbp(ALLOWANCE), scale(-1, cent))
            out += [Implies(And(guard, Not(U("rnd_up", x)), Not(U("rnd_down", x)), Not(U("rnd_fig", x))),
                            Eq(nx, gbp(ALLOWANCE))),
                    Implies(And(guard, U("rnd_up", x)), And(Le(gbp(ALLOWANCE), nx), Lt(nx, hi))),
                    Implies(And(guard, U("rnd_down", x)), And(Lt(lo, nx), Le(nx, gbp(ALLOWANCE)))),
                    Implies(And(guard, U("rnd_fig", x), Lt(lo, scale(n, k("rnd", x))), Lt(scale(n, k("rnd", x)), hi)),
                            Eq(k("alw", x), k("rnd", x)))]
    return out


def _member_rules(x, g, m, ctx):
    return (_relevant(x, g, m, ctx) + _member_parts(x, g, m, ctx) + _alw_determination(x, g, m, ctx)
            + _alw_10(x, g, m, ctx) + _alw_12(x, g, m, ctx))


UNITS = {
    # ---- s. 99 ----
    1: ("RULE", per_person(_charged), "s. 99(1): pay bill and 5 x pay bill > 1000 x allowance (0.5 %, linear)"),
    2: ("RULE", per_person(_amount), "s. 99(2): 1000 x amount = 5 x pay bill - 1000 x allowance (N - A); R1 0.00 when "
        "not charged; R10 exact, or the stated half-up convention as two bounds"),
    3: ("RULE", per_person(_liable), "s. 99(3): liable iff charged"),
    4: ("RULE", per_person(_entitled), "s. 99(4): entitled iff a pay bill ('except so far as s. 103': given none)"),
    5: ("RULE", per_person(_basic_allowance), "s. 99(5): GBP 15,000 unless a member of a company unit (s. 101; s. 102 "
        "charities given none); R9 0.00 with no allowance"),
    6: ("RULE", lambda ctx: [], "s. 99(6): 0.5 % = the literals 5 / 1000 in units 1 and 2"),
    # ---- s. 100 ----
    7: ("PART", lambda ctx: per_earn(_counted)(ctx) + per_person(_haspb)(ctx), "cross-reference",
        "s. 100(1): written over the earnings items; 'secondary contributor', 'employed earner', 'payments of earnings' "
        "and the liability to secondary Class 1 contributions are SSCBA 1992 matters, stated facts"),
    8: ("RULE", lambda ctx: per_earn(_part)(ctx) + per_person(_paybill)(ctx),
        "s. 100(2): pay bill = the total of the counted items' earnings (SUM over the payer's items)"),
    9: ("PART", lambda ctx: [], "cross-reference", "s. 100(3) 'treated as incurring' written (the 'butfor' limb of "
        "unit 7's counted); whether a liability would arise but for s. 6(1)(b) SSCBA is a stated fact"),
    10: ("NOT", None, "definition by reference", "s. 100(5)(a), (b): 'payments of earnings' and the amount of earnings "
         "as for Class 1 contributions under SSCBA 1992 (not pinned): stated facts"),
    11: ("PART", lambda ctx: [], "cross-reference", "s. 100(6): liability under Part 1 SSCBA 1992 (stated); 'including "
         "a liability of GBP 0' carried in the stated fact's words"),
    # ---- s. 101 ----
    12: ("RULE", lambda ctx: per_person(_isco)(ctx) + per_person(_member)(ctx),
         "s. 101(1): two or more companies, not charities, connected (unit 27, stated) and each entitled (R7)"),
    13: ("PART", per_member(_member_rules), "other:norm", "s. 101(2): 'must determine' (a duty) carried only as its "
         "effect: the determination's amount is the member's allowance when it complies (R4); 'But see (6) and "
         "(11)' as guards. Also grounds (8)(a)(i) relevant members, the members' parts and the (10), (12) amounts"),
    14: ("RULE", per_group(lambda g, m, ctx: _det_checks(g, m, ctx)[0:1] + _det_checks(g, m, ctx)[2:3]),
         "s. 101(3): no member's amount negative (a compliance condition)"),
    15: ("RULE", per_group(lambda g, m, ctx: _det_checks(g, m, ctx)[1:2] + _det_checks(g, m, ctx)[3:4]),
         "s. 101(4): the members' amounts total GBP 15,000 (SUM)"),
    16: ("PART", lambda ctx: [], "other:norm", "s. 101(5): 'cannot afterwards be altered' (a prohibition) carried only "
         "as its effect (R5: an alteration counts only to correct a (4) failure; in unit 13's rules)"),
    17: ("RULE", lambda ctx: [], "s. 101(6): (8) applies -> the (7) / (10) amounts replace the determination ('treated "
         "as never having applied', R2); the guards in unit 13's rules"),
    18: ("NOT", None, "amount arithmetic", "s. 101(7): the return's amount x 15,000 / T, T the total of the returns' "
         "amounts: a product of two quantities (no such term in the language); the stated rounding is a secondary "
         "judgment"),
    19: ("RULE", per_group(_s8), "s. 101(8): two relevant members; the relevant returns' amounts total > GBP 15,000; "
         "every relevant member notified; the action not taken in the period (stated official acts)"),
    20: ("RULE", lambda ctx: [], "s. 101(9): the basis (entitled, whether or not of zero): in the stated fact's words"),
    21: ("RULE", lambda ctx: [], "s. 101(10): a member that is not a relevant member: zero (unit 13's rules)"),
    22: ("RULE", lambda ctx: [], "s. 101(11): (13) applies -> the (12) amount replaces the determination (R2, R3)"),
    23: ("PART", lambda ctx: [], "other:judgment standard", "s. 101(12): N x allowance = 15,000, N the members counted "
         "over the case's named companies (unit 13's rules); 'may be rounded up or down where appropriate' a stated "
         "judgment (R8)"),
    24: ("PART", per_group(_s13), "other:judgment standard", "s. 101(13): (a) paid < due (SUM), (c), (d) written; (b) "
         "'do not contain sufficient information' a stated judgment"),
    25: ("RULE", lambda ctx: [], "s. 101(14): (4) taken into account: R6 pool reading in unit 24's (a)"),
    26: ("NOT", None, "definition by reference", "s. 101(16): a return under regulations under s. 105(4) (not pinned): "
         "a stated fact"),
    27: ("NOT", None, "definition by reference", "s. 101(17): 'connected' by NICA 2014 Sch. 1 Part 1 (not pinned): a "
         "stated fact"),
    28: ("PART", lambda ctx: [], "definition by reference", "s. 101(18): 'company' by CTA 2010 s. 1121(1) a stated "
         "fact; 'includes a limited liability partnership' written (unit 12's isco)"),
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


# --- structure helpers (council_tax conventions) -------------------------------------------------------------------

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


def _target_const(t):
    if t[0] == "const" and len(t) == 3:
        return t[2]
    if t[0] == "scale" and t[3][0] == "const" and len(t[3]) == 3:
        return t[3][2]
    if t[0] == "add":
        return _target_const(t[2])
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
    if f[0] == "and":  # two bounds on one target: the target is in the first bound (built so)
        return defines(f[1])
    if f[0] in ("unary", "binary"):
        return [key(f)]
    if f[0] == "not" and f[1][0] in ("unary", "binary"):
        return [key(f[1])]
    if f[0] == "eq":
        t = _target_const(f[1])
        if t is not None:
            return [t]
    if f[0] in ("le", "lt"):
        for side in (f[1], f[2]):
            t = _target_const(side)
            if t is not None and t.split("_", 1)[0] in STEP_BASES:
                return [t]
    raise ValueError(f"no defined target: {f}")


# --- the environment for one case ---------------------------------------------------------------------------------

def environment(ctx):
    consts = {}
    for x in ctx.items:
        consts[x] = {"sort": "item", "description": f"The case's item {x}.", "verbalisation": f"item {x}"}
        for base, (u, w) in INT_UNITS.items():
            consts[f"{base}_{x}"] = {"sort": "$int", "unit": u, "description": f"{w[0].upper() + w[1:]} ({x}).",
                                     "verbalisation": f"{w} ({x})"}
    unary = {**FACTS_PERSON, **FACTS_EARN, **FACTS_GROUP, **DERIVED_PERSON, **DERIVED_EARN, **DERIVED_GROUP}
    preds = {n: {"arguments": ["item"], "description": d[0].upper() + d[1:] + "."} for n, d in unary.items()}
    preds.update({n: {"arguments": ["item", "item"], "description": d[0].upper() + d[1:] + "."}
                  for n, d in BINARY.items()})
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "A person, earnings item or connected group the case names."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {"day": {"scale": "1", "display": {"kind": "iso_date"}},
                      GBP: {"scale": "100", "display": {"kind": "money", "currency": "GBP", "input_symbol": "£"}}}}


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


def _with_member_rules(**kw):
    def rules_fn(x, g, m, ctx):
        return (_relevant(x, g, m, ctx) + _member_parts(x, g, m, ctx)
                + kw.get("det", _alw_determination)(x, g, m, ctx) + kw.get("a10", _alw_10)(x, g, m, ctx)
                + kw.get("a12", _alw_12)(x, g, m, ctx))
    return lambda b: per_member(rules_fn)


def _det_ignoring_hmrc(x, g, m, ctx):
    """M6/M7: the members' determination prevails whatever (8) / (13) say."""
    base = And(U("member", x), U("detmade", g))
    return [Implies(And(base, U("detok3", g), U("detok4", g)), Eq(k("alw", x), k("det", x)))]


def _det_alter_always(x, g, m, ctx):
    base = And(U("member", x), Not(U("app8", g)), Not(U("app13", g)), U("detmade", g))
    return [Implies(And(base, Not(U("altmade", g)), U("detok3", g), U("detok4", g)), Eq(k("alw", x), k("det", x))),
            Implies(And(base, U("altmade", g), U("altok3", g), U("altok4", g)), Eq(k("alw", x), k("alt", x)))]


def _no_unit_entitlement(x, ctx):
    g = ctx.group_of(x)
    if g is None:
        return [iff_u("member", x, FALSE)]
    cand = lambda y: And(U("isco", y), Not(U("charity", y)), B("conn", y, g))
    others = [y for y in ctx.groups[g] if y != x]
    return [iff_u("member", x, And(cand(x), Or(*[cand(y) for y in others])))]


def _set(n, builder):
    def apply(t):
        t = dict(t)
        t[n] = (t[n][0], builder, *t[n][2:])
        return t
    return apply


def _chain(*fs):
    def apply(t):
        for f in fs:
            t = f(t)
        return t
    return apply


MUTANTS = {
    "M1": ("AMOUNT: s. 99(6) 0.5 % read as 0.05 % (5 / 10000)",
           _chain(_set(1, per_person(lambda x, ctx: _charged(x, ctx, den=10000))),
                  _set(2, per_person(lambda x, ctx: _amount(x, ctx, den=10000))))),
    "M2": ("AMOUNT: s. 99(2) N - A read as N (the allowance not deducted)",
           _set(2, per_person(lambda x, ctx: _amount(x, ctx, deduct=False)))),
    "M3": ("AMOUNT: s. 99(5) GBP 15,000 read as GBP 1,500", _swap(5, _wrap(_json_sub('"15000.00"', '"1500.00"')))),
    "M4": ("AMOUNT: s. 101(12) N miscounted (one more than the members)",
           _set(13, per_member(lambda x, g, m, ctx: _relevant(x, g, m, ctx) + _member_parts(x, g, m, ctx)
                               + _alw_determination(x, g, m, ctx) + _alw_10(x, g, m, ctx)
                               + _alw_12(x, g, m, ctx, extra=1)))),
    "M5": ("DEEMING: s. 100(3) 'treated as incurring' dropped",
           _set(7, lambda ctx: per_earn(_counted_no_deeming)(ctx) + per_person(_haspb)(ctx))),
    "M6": ("DEEMING: s. 101(6)(b)/(11)(b) 'treated as never having applied' dropped (the determination prevails)",
           _swap(13, _with_member_rules(det=_det_ignoring_hmrc))),
    "M7": ("THRESHOLD: s. 99(1)(b) 'exceeds' read as 'is at least'",
           _set(1, per_person(lambda x, ctx: _charged(x, ctx, strict=False)))),
    "M8": ("THRESHOLD: s. 101(8)(a)(ii) 'greater than' read as 'at least'",
           _swap(19, _wrap(_json_sub('["lt", ["decimal", "gbp_penny", "15000.00"]',
                                     '["le", ["decimal", "gbp_penny", "15000.00"]')))),
    "M9": ("PROHIBITION: s. 101(5) any alteration has effect", _swap(13, _with_member_rules(det=_det_alter_always))),
    "M10": ("CONDITION: s. 101(1)(b) 'each of them entitled to a levy allowance' dropped",
            _set(12, lambda ctx: per_person(_isco)(ctx) + per_person(_no_unit_entitlement)(ctx))),
    "M11": ("AMOUNT: s. 101(10) a non-relevant member keeps GBP 15,000 instead of zero",
            _swap(13, _with_member_rules(a10=lambda x, g, m, ctx: [
                Implies(And(U("member", x), U("app8", g), Not(U("app13", g)), Not(U("relevant", x))),
                        Eq(k("alw", x), gbp(ALLOWANCE)))]))),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
