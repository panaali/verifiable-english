"""Vehicle excise duty, light passenger vehicles first registered on or after 1 April 2017, VERA 1994 Sch 1 Part 1AA
(statute corpus batch 3, law ved-first-year): the VE translation, one pass with today's language. SAME-FAMILY (Opus writer,
Opus translator).

Row statute-corpus-ved-first-year (dri-statute-corpus-ved-first-year-1123, Opus 5.5). Written from the pinned source only
(manage-agents reviews/spare/statute-corpus/stock/ved-first-year/source.txt, sha256 7fad88d0...1e0) BEFORE the encoder's
file questions-enc.jsonl was opened. Evidence branch: nothing here is a Lean kernel line, a profile, a refuses pair or a
lint change; nothing merges.

UNITS maps each in-scope unit n of stock/ved-first-year/units.jsonl (41; 25 table rows) to
  ("RULE", builder, note)        the unit is written: builder(ctx) gives its ground formulas for one case;
  ("PART", builder, cause, note) written except the part named in the note (bridged / stated / not written);
  ("NOT", None, cause, note)     not written (the ledger row's cause, CAUSES.tsv v2 + "other:table lookup").
Items: each vehicle v (a case may name several), each non-standard accessory a of a vehicle, each vehicle licence l asked
about (other than the first). No number from a case's facts is ever put into a rule as a coefficient: every limit and
rate below is a literal of the pinned text (the table bands and rates, 1 April 2017, 1 April 2025, GBP 200, 640, 40,000,
50,000, six years, 0 g/km).

Translator readings, fixed here before any question was read:
R1 (1GC(5)) "meets the Euro 6d emissions standard ONLY IF first registered on the basis of an EU certificate of conformity
   which indicates ... Euro 6d (and does not meet it if ... Euro 6d-TEMP)": the text gives the necessary condition and
   the 6d-TEMP exclusion; the sufficient half (a vehicle so registered whose certificate indicates Euro 6d, and not
   6d-TEMP, meets the standard) is READ: the certificate's indication is the vehicle's exhaust emission level (the test's
   fixed facts state the standard only as what the certificate indicates). flips.py reports every answer that leans on the
   sufficient half (EURO6D_READ below switches it off: those answers are then refused).
R2 (1GA(1B)(c)) "this Part would apply if (1)(b)(ii) were met" = the other conditions of 1GA(1) hold ((a) and (b)(i), on an
   EU certificate of conformity or UK approval certificate); 1GA(1A) (motor caravans) is out of scope (no in-scope question
   turns on it) and is not written.
R3 (1GA(1C)) the deeming is written: the certificate is regarded as specifying a figure (so 1GA(1)(b)(ii) is met) and the
   applicable CO2 emissions figure is zero.
R4 (1GC(1), 1GD(1), 1GE(1)) the rates are worked out for a vehicle to which this Part applies; for any other vehicle VE
   derives "this Part does not apply" and no rate (Q3: 1GE(2) does not apply).
R5 (1GE(1)(b)) "first registered ... less than six years before the date on which the licence has effect": the duration
   from the first registration to that date as (whole years, days beyond them) is BRIDGED (bridge/years.py: one pair of
   dates -> a duration, [B5]); "less than six years" = whole years < 6 is compared in Lean.
R6 (1GF) prices: the list price, its absence, the notional price and each accessory's prices, "non-standard" and
   "attached when first registered under this Act" are stated facts (ITEPA 2003 ss. 123-130 by 1GF(3), out of scope);
   the SUM of (1)(a) and the choice of (2) are written.
"""
from __future__ import annotations

import hashlib
import json

GBP, DAY, YEARS, NDAYS, GKM = "gbp_penny", "day", "year_count", "elapsed_day", "g_per_km"
EURO6D_READ = True  # R1's sufficient half (flips.py switches it off)

V_UNITS = {  # per-vehicle constants: base -> (unit, words)
    "dreg": (DAY, "the day the vehicle was first registered (under this Act or under the law of a country or territory "
                  "outside the United Kingdom)"),
    "co2": (GKM, "the vehicle's applicable CO2 emissions figure in grams per kilometre driven"),
    "lp": (GBP, "the vehicle's list price"),
    "np": (GBP, "the vehicle's notional price"),
    "price": (GBP, "the price of the vehicle (1GF(1))"),
    "rate1": (GBP, "the annual rate of vehicle excise duty on the first vehicle licence for the vehicle"),
}
A_UNITS = {
    "alp": (GBP, "the accessory's list price"),
    "anp": (GBP, "the accessory's notional price"),
    "acc": (GBP, "the price of the accessory counted in the price of the vehicle (1GF(1)(a)(ii), (2))"),
}
L_UNITS = {
    "dlic": (DAY, "the date on which the licence has effect"),
    "ly": (YEARS, "whole years from the vehicle's first registration to the date on which the licence has effect "
                  "(bridge only)"),
    "ld": (NDAYS, "days beyond those whole years (bridge only)"),
    "rate2": (GBP, "the annual rate of vehicle excise duty on this (other) vehicle licence for the vehicle"),
}
BRIDGED = ("ly", "ld")
ASKED_BASES = ("price", "rate1", "acc", "rate2")  # derived constants: each one staged step over candidate values

V_FACTS = {  # unary facts on a vehicle (the encoder states each true or false)
    "basis_coc": "the vehicle was first registered on the basis of an EU certificate of conformity",
    "basis_ukac": "the vehicle was first registered on the basis of a UK approval certificate",
    "cert_lpv": "the certificate on the basis of which the vehicle was first registered identifies the vehicle as having "
                "been approved as a light passenger vehicle",
    "cert_co2": "that certificate specifies a CO2 emissions figure in terms of grams per kilometre driven",
    "zero_rate": "the vehicle's rate of CO2 emissions in grams per kilometre driven is zero",
    "diesel": "the vehicle is constructed so as to be propelled by diesel",
    "ind6d": "that certificate is an EU certificate of conformity which indicates that the exhaust emission level is Euro 6d",
    "ind6dtemp": "that certificate is an EU certificate of conformity which indicates that the exhaust emission level is "
                 "Euro 6d-TEMP",
    "has_lp": "the vehicle has a list price",
    "taxi": "when it was first registered the vehicle was a taxi capable of zero emissions (1GG regulations: stated)",
}
A_FACTS = {
    "a_nonstd": "the accessory is a non-standard accessory",
    "a_attached": "the accessory was attached to the vehicle when the vehicle was first registered under this Act",
    "a_has_lp": "the accessory has a list price",
}
DERIVED = {
    "reg17": "the vehicle was first registered on or after 1 April 2017",
    "basis": "the vehicle was so registered on the basis of an EU certificate of conformity or UK approval certificate",
    "would_apply": "this Part would apply to the vehicle if the condition in 1GA(1)(b)(ii) were met",
    "deem1c": "1GA(1C) has effect: the certificate is regarded as specifying a CO2 figure of zero",
    "spec_co2": "the certificate specifies (or is regarded as specifying) a CO2 emissions figure in g/km",
    "applies": "Part 1AA of Schedule 1 applies to the vehicle",
    "euro6d": "the vehicle meets the Euro 6d emissions standard",
    "hrd": "the vehicle is a higher rate diesel vehicle",
    "gc_on": "paragraph 1GC applies for the purpose of determining the rate on the first vehicle licence for the vehicle",
    "use_t1": "the annual rate on the first vehicle licence is determined in accordance with Table 1",
    "use_t2": "the annual rate on the first vehicle licence is determined in accordance with Table 2",
    **{f"t1_{r}": f"the vehicle's applicable CO2 emissions figure falls in row {r} of Table 1" for r in range(1, 14)},
    **{f"t2_{r}": f"the vehicle's applicable CO2 emissions figure falls in row {r} of Table 2" for r in range(1, 13)},
    "co2zero": "the vehicle's applicable CO2 emissions figure is zero",
    "over_amt": "the price of the vehicle exceeds the applicable amount (1GE(1A))",
    "reg25": "the vehicle was first registered on or after 1 April 2025",
    "co2pos": "the vehicle's applicable CO2 emissions figure exceeds 0g/km",
    "lt6": "the vehicle was first registered less than six years before the date on which the licence has effect",
    "ge2": "paragraph 1GE(2) applies for the purpose of determining the rate on the licence",
    "gd1_on": "paragraph 1GD(1) applies to the licence (1GD(2): it does not where 1GE(2) applies)",
    "taxi_excl": "1GE(5): sub-paragraph (2) does not apply to the vehicle (a taxi capable of zero emissions when first registered)",
}
L_DERIVED = ["lt6", "ge2", "gd1_on"]
V_DERIVED = [d for d in DERIVED if d not in L_DERIVED]

# Table 1 (vehicles other than higher rate diesel vehicles): (row, exceeding or (row 1) equal to, not exceeding, rate GBP)
T1 = [(1, 0, 0, 10), (2, 0, 50, 115), (3, 50, 75, 135), (4, 75, 90, 280), (5, 90, 100, 365), (6, 100, 110, 405),
      (7, 110, 130, 455), (8, 130, 150, 560), (9, 150, 170, 1410), (10, 170, 190, 2270), (11, 190, 225, 3420),
      (12, 225, 255, 4850), (13, 255, None, 5690)]
# Table 2 (higher rate diesel vehicles): (row, exceeding or (row 1) equal to or exceeding, not exceeding, rate GBP)
T2 = [(1, 0, 50, 135), (2, 50, 75, 280), (3, 75, 90, 365), (4, 90, 100, 405), (5, 100, 110, 455), (6, 110, 130, 560),
      (7, 130, 150, 1410), (8, 150, 170, 2270), (9, 170, 190, 3420), (10, 190, 225, 4850), (11, 225, 255, 5690),
      (12, 255, None, 5690)]


# --- formula helpers (the ve-quantity@1 wire shapes; fwa_australia / council_tax conventions) ---------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def gbp(v): return ["decimal", GBP, str(v)]
def gkm(v): return ["decimal", GKM, str(v)]
def yrs(v): return ["decimal", YEARS, str(v)]
def date(s): return ["date", s]
def Eq(a, b): return ["eq", a, b]
def Lt(a, b): return ["lt", a, b]
def Le(a, b): return ["le", a, b]
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


ALL_UNITS = {**V_UNITS, **A_UNITS, **L_UNITS}


def k(base, x):
    """Per-item constant."""
    return ["const", ALL_UNITS[base][0], f"{base}_{x}"]


def iff_u(p, x, body): return Iff(U(p, x), body)


# --- the case context ----------------------------------------------------------------------------------------------

class Ctx:
    """vehicles: [{"id": "v1", "accessories": ["v1a1", ...], "licences": ["v1l1", ...]}]"""
    def __init__(self, vehicles):
        self.vehicles = vehicles

    @property
    def items(self):
        out = []
        for v in self.vehicles:
            out += [v["id"]] + list(v["accessories"]) + list(v["licences"])
        return out


def per_v(fn):
    return lambda ctx: [f for v in ctx.vehicles for f in fn(v["id"], v, ctx)]


def per_l(fn):
    return lambda ctx: [f for v in ctx.vehicles for l in v["licences"] for f in fn(v["id"], l, ctx)]


# --- 1GA ------------------------------------------------------------------------------------------------------------

def _1ga_1(x, v, ctx):
    return [iff_u("reg17", x, Le(date("2017-04-01"), k("dreg", x))),
            iff_u("basis", x, Or(U("basis_coc", x), U("basis_ukac", x))),
            iff_u("applies", x, And(U("reg17", x), U("basis", x), U("cert_lpv", x), U("spec_co2", x)))]


def _1ga_1b(x, v, ctx):
    return [iff_u("would_apply", x, And(U("reg17", x), U("basis", x), U("cert_lpv", x))),
            iff_u("deem1c", x, And(U("zero_rate", x), Not(U("cert_co2", x)), U("would_apply", x)))]


def _1ga_1c(x, v, ctx):
    return [iff_u("spec_co2", x, Or(U("cert_co2", x), U("deem1c", x))),
            Implies(U("deem1c", x), Eq(k("co2", x), gkm(0)))]


# --- 1GC: first vehicle licence -------------------------------------------------------------------------------------

def _1gc_1(x, v, ctx):
    return [iff_u("gc_on", x, U("applies", x))]


def _1gc_2(x, v, ctx):
    return [iff_u("use_t1", x, And(U("gc_on", x), Not(U("hrd", x))))]


def _1gc_3(x, v, ctx):
    return [iff_u("use_t2", x, And(U("gc_on", x), U("hrd", x)))]


def _t1_row(r, lo, hi, rate):
    def build(x, v, ctx):
        y = k("co2", x)
        if r == 1:  # "Exceeding or, in the first row, equal to" 0; not exceeding 0
            cond = And(Eq(y, gkm(lo)), Le(y, gkm(hi)))
        else:
            cond = And(Lt(gkm(lo), y), Le(y, gkm(hi)) if hi is not None else None)
        return [iff_u(f"t1_{r}", x, cond),
                Implies(And(U("use_t1", x), U(f"t1_{r}", x)), Eq(k("rate1", x), gbp(rate)))]
    return per_v(build)


def _t2_row(r, lo, hi, rate):
    def build(x, v, ctx):
        y = k("co2", x)
        if r == 1:  # "Exceeding or, in the first row, equal to or exceeding" 0; not exceeding 50
            cond = And(Le(gkm(lo), y), Le(y, gkm(hi)))
        else:
            cond = And(Lt(gkm(lo), y), Le(y, gkm(hi)) if hi is not None else None)
        return [iff_u(f"t2_{r}", x, cond),
                Implies(And(U("use_t2", x), U(f"t2_{r}", x)), Eq(k("rate1", x), gbp(rate)))]
    return per_v(build)


def _1gc_4(x, v, ctx):
    return [iff_u("hrd", x, And(U("diesel", x), Not(U("euro6d", x))))]


def _1gc_5(x, v, ctx):
    """1GC(5): ONLY IF (necessary condition) + the 6d-TEMP exclusion, as the text gives them; the sufficient half is
    reading R1 (EURO6D_READ)."""
    out = [Implies(U("euro6d", x), And(U("basis_coc", x), U("ind6d", x))),
           Implies(And(U("basis_coc", x), U("ind6dtemp", x)), Not(U("euro6d", x)))]
    if EURO6D_READ:
        out = [iff_u("euro6d", x, And(U("basis_coc", x), U("ind6d", x), Not(U("ind6dtemp", x))))]
    return out


# --- 1GD, 1GE: any other vehicle licence ----------------------------------------------------------------------------

def _1gd_1(x, l, ctx):
    return [Implies(And(U("applies", x), U("gd1_on", l)), Eq(k("rate2", l), gbp(200)))]


def _1gd_2(x, l, ctx):
    return [iff_u("gd1_on", l, Not(U("ge2", l)))]


def _1ge_5(x, v, ctx):
    return [iff_u("taxi_excl", x, U("taxi", x))]


def _1ge_1(x, l, ctx):
    return [iff_u("lt6", l, Lt(k("ly", l), yrs(6))),
            iff_u("ge2", l, And(U("applies", x), U("over_amt", x), U("lt6", l),
                                Or(U("reg25", x), U("co2pos", x)), Not(U("taxi_excl", x))))]


def _1ge_1v(x, v, ctx):
    return [iff_u("reg25", x, Le(date("2025-04-01"), k("dreg", x))),
            iff_u("co2pos", x, Lt(gkm(0), k("co2", x)))]


def _1ge_1a(x, v, ctx):
    return [iff_u("co2zero", x, Eq(k("co2", x), gkm(0))),
            iff_u("over_amt", x, Or(And(U("co2zero", x), Lt(gbp("50000"), k("price", x))),
                                    And(Not(U("co2zero", x)), Lt(gbp("40000"), k("price", x)))))]


def _1ge_2(x, l, ctx):
    return [Implies(And(U("applies", x), U("ge2", l)), Eq(k("rate2", l), gbp(640)))]


# --- 1GF: the price -------------------------------------------------------------------------------------------------

def _1gf_1(x, v, ctx):
    total = k("lp", x)
    for a in v["accessories"]:
        total = add(GBP, total, k("acc", a))
    return [Implies(U("has_lp", x), Eq(k("price", x), total)),
            Implies(Not(U("has_lp", x)), Eq(k("price", x), k("np", x)))]


def _1gf_2(x, v, ctx):
    out = []
    for a in v["accessories"]:
        counted = And(U("a_nonstd", a), U("a_attached", a))
        out += [Implies(And(counted, U("a_has_lp", a)), Eq(k("acc", a), k("alp", a))),
                Implies(And(counted, Not(U("a_has_lp", a))), Eq(k("acc", a), k("anp", a))),
                Implies(Not(counted), Eq(k("acc", a), gbp(0)))]
    return out


UNITS = {
    1: ("PART", per_v(_1ga_1), "definition by reference", "1GA(1): written ((a) the first registration date compared "
        "with 1 April 2017 in Lean; (b) and (b)(i)-(ii)); the defined terms 'EU certificate of conformity' (1GA(4), out "
        "of scope: by reference to Directive 2007/46/EC / Reg (EU) 2018/858), 'UK approval certificate' (1G(2), not in "
        "the source) and 'light passenger vehicle' (1GA(2), out: Category M1) are stated facts: the certificate's kind "
        "and what it identifies the vehicle as"),
    2: ("RULE", per_v(_1ga_1b), "1GA(1B): (a) the zero rate of CO2 emissions a stated fact (Part 1A out), (b), (c) read "
        "as R2"),
    3: ("RULE", per_v(_1ga_1c), "1GA(1C): the deeming written (R3): regarded as specifying a figure; the applicable "
        "figure taken to be zero"),
    4: ("RULE", per_v(_1gc_1), "1GC(1): the paragraph applies for the first-licence rate of a vehicle to which this "
        "Part applies (R4); the guard of units 5 and 6"),
    5: ("RULE", per_v(_1gc_2), "1GC(2): not a higher rate diesel vehicle -> Table 1 by the applicable CO2 emissions "
        "figure ((a); (b) repealed)"),
    6: ("RULE", per_v(_1gc_3), "1GC(3): a higher rate diesel vehicle -> Table 2"),
    **{n: ("RULE", _t1_row(r, lo, hi, rate), f"Table 1 row {r}: {'equal to' if r == 1 else 'exceeding'} {lo} g/km"
           + (f", not exceeding {hi} g/km" if hi is not None else "") + f"; GBP {rate} (as the text gives it)")
       for n, (r, lo, hi, rate) in zip(range(7, 20), T1)},
    **{n: ("RULE", _t2_row(r, lo, hi, rate), f"Table 2 row {r}: {'equal to or exceeding' if r == 1 else 'exceeding'} {lo} "
           f"g/km" + (f", not exceeding {hi} g/km" if hi is not None else "") + f"; GBP {rate} (as the text gives it)")
       for n, (r, lo, hi, rate) in zip(range(20, 32), T2)},
    32: ("PART", per_v(_1gc_4), "definition by reference", "1GC(4): written; 'diesel' (1GC(6), out of scope: by "
         "reference to Directive 98/70/EC) and 'constructed so as to be propelled by diesel' a stated fact"),
    33: ("PART", per_v(_1gc_5), "definition by reference", "1GC(5): the necessary condition ('only if') and the "
         "6d-TEMP exclusion written; the sufficient half is reading R1; 'EU certificate of conformity' (1GA(4)) and what "
         "it indicates are stated facts"),
    34: ("RULE", per_l(_1gd_1), "1GD(1): GBP 200 on any other licence, for a vehicle to which this Part applies, "
         "unless 1GE(2) applies (unit 35)"),
    35: ("RULE", per_l(_1gd_2), "1GD(2): 1GD(1) does not apply where 1GE(2) applies"),
    36: ("PART", lambda ctx: per_l(_1ge_1)(ctx) + per_v(_1ge_1v)(ctx), "date/age arithmetic", "1GE(1): (a), (c)(i)-(ii) "
         "written (dates compared with 1 April 2025 in Lean; 'exceeds 0g/km' in Lean); (b) 'less than six years before "
         "the date on which the licence has effect': the whole years from the first registration to that date are "
         "BRIDGED (bridge/years.py), the comparison with six years is in Lean (R5)"),
    37: ("RULE", per_v(_1ge_1a), "1GE(1A): GBP 50,000 when the applicable figure is zero, else GBP 40,000; 'exceeds' "
         "compared in Lean"),
    38: ("RULE", per_l(_1ge_2), "1GE(2): GBP 640"),
    39: ("PART", per_v(_1ge_5), "definition by reference", "1GE(5): written (unit 36 reads it); 'a taxi "
         "capable of zero emissions (see paragraph 1GG)': its meaning is left to regulations under 1GG (out of scope): "
         "a stated fact"),
    40: ("PART", per_v(_1gf_1), "definition by reference", "1GF(1): the SUM of (a) and the choice of (b) written; "
         "'list price', 'non-standard accessory', 'notional price' (ITEPA 2003 ss. 123-130 by 1GF(3), out of scope) "
         "and 'attached when first registered under this Act' are stated facts (R6)"),
    41: ("PART", per_v(_1gf_2), "definition by reference", "1GF(2): the choice written (its list price if it has one, "
         "else its notional price); the prices themselves stated (ITEPA, R6)"),
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


# --- structure helpers (fwa_australia / council_tax translation.py conventions) -----------------------------------

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
    """The atoms / constants a ground rule fixes."""
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
    YEARS: {"scale": "1", "display": {"kind": "decimal", "label": "years"}},
    NDAYS: {"scale": "1", "display": {"kind": "decimal", "label": "days"}},
    GKM: {"scale": "100", "display": {"kind": "decimal", "label": "g/km"}},
    GBP: {"scale": "100", "display": {"kind": "money", "currency": "GBP", "input_symbol": "£"}},
}


def environment(ctx):
    consts = {}
    for v in ctx.vehicles:
        groups = [([v["id"]], V_UNITS, "vehicle"), (v["accessories"], A_UNITS, "accessory"),
                  (v["licences"], L_UNITS, "vehicle licence")]
        for xs, table, what in groups:
            for x in xs:
                consts[x] = {"sort": "item", "description": f"The case's {what} {x}.", "verbalisation": f"{what} {x}"}
                for base, (u, w) in table.items():
                    consts[f"{base}_{x}"] = {"sort": "$int", "unit": u, "description": f"{w[0].upper() + w[1:]} ({x}).",
                                             "verbalisation": f"{w} ({x})"}
    preds = {n: {"arguments": ["item"], "description": d[0].upper() + d[1:] + "."}
             for n, d in {**V_FACTS, **A_FACTS, **DERIVED}.items()}
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "A vehicle, accessory or vehicle licence the case names."}},
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


def _drop_accessories(f):
    """price = list price only (1GF(1)(a)(ii) dropped)."""
    if type(f) is list:
        if f[:1] == ["add"] and f[1] == GBP:
            return _drop_accessories(f[2])
        return [_drop_accessories(g) for g in f]
    return f


def _atom_to(pred, value):
    """Mutant helper: every atom of `pred` replaced by a constant truth value."""
    def walk(f):
        if type(f) is list:
            if f[:2] == ["unary", pred]:
                return value
            return [walk(g) for g in f]
        return f
    return walk


def _temp_as_6d(f):
    """M12 helper: a certificate indicating Euro 6d-TEMP read as indicating Euro 6d (the parenthesis of 1GC(5) dropped)."""
    if type(f) is list:
        if f[:2] == ["unary", "ind6dtemp"]:
            return FALSE
        if f[:2] == ["unary", "ind6d"]:
            return ["or", f, ["unary", "ind6dtemp", f[2]]]
        return [_temp_as_6d(g) for g in f]
    return f


def _drop_c(f):
    """M10 helper: (c) '(i) on or after 1 April 2025, or (ii) before that and the figure exceeds 0' -> true."""
    if type(f) is list:
        if f[:1] == ["or"] and type(f[1]) is list and f[1][:2] == ["unary", "reg25"]:
            return TRUE
        return [_drop_c(g) for g in f]
    return f


MUTANTS = {
    "M1": ("TABLE: Table 1 row 7 (110-130 g/km) GBP 455 read as GBP 445",
           _swap(13, _wrap(_json_sub('["decimal", "gbp_penny", "455"]', '["decimal", "gbp_penny", "445"]')))),
    "M2": ("TABLE: Table 2 row 12 (over 255 g/km) GBP 5690 read as GBP 6690 (the table re-derived as increasing)",
           _swap(31, _wrap(_json_sub('["decimal", "gbp_penny", "5690"]', '["decimal", "gbp_penny", "6690"]')))),
    "M3": ("BOUNDARY: Table 1 row 4 'not exceeding 90' read as 'less than 90' (and row 5 'exceeding 90' as 'at least')",
           lambda t: _swap(11, _wrap(_json_sub('["lt", ["decimal", "g_per_km", "90"]', '["le", ["decimal", "g_per_km", "90"]')))(
               _swap(10, _wrap(_json_sub('["le", ["const", "g_per_km"', '["lt", ["const", "g_per_km"')))(t))),
    "M4": ("BOUNDARY: Table 1 row 1 'equal to 0' dropped (0 g/km read into row 2's band 'exceeding 0')",
           lambda t: _swap(8, _wrap(_json_sub('["lt", ["decimal", "g_per_km", "0"]', '["le", ["decimal", "g_per_km", "0"]')))(
               _swap(7, _wrap(_json_sub('["eq", ["const", "g_per_km"', '["lt", ["const", "g_per_km"')))(t))),
    "M5": ("DEEMING: 1GA(1C) dropped (a zero-emission vehicle whose certificate specifies no figure is outside the Part)",
           _swap(3, _wrap(_atom_to("deem1c", FALSE)))),
    "M6": ("AMOUNT (SUM): 1GF(1)(a)(ii) dropped (the price is the list price alone)",
           _swap(40, _wrap(_drop_accessories))),
    "M7": ("AMOUNT: 1GF(2) inverted (an accessory with a list price counted at its notional price, and the other way)",
           _swap(41, _wrap(lambda f: json.loads(json.dumps(f).replace('"alp_', '"TMP_').replace('"anp_', '"alp_')
                                                .replace('"TMP_', '"anp_'))))),
    "M8": ("THRESHOLD: 1GE(1)(a) 'exceeds the applicable amount' read as 'is at least'",
           _swap(37, _wrap(_json_sub('["lt", ["decimal", "gbp_penny"', '["le", ["decimal", "gbp_penny"')))),
    "M9": ("THRESHOLD: 1GE(1A)(a) dropped (GBP 40,000 for a zero-emission vehicle too)",
           _swap(37, _wrap(_json_sub('"50000"', '"40000"')))),
    "M10": ("CONDITION: 1GE(1)(c) dropped (zero-emission vehicles registered before 1 April 2025 caught)",
            _swap(36, _wrap(lambda f: _drop_c(f)))),
    "M11": ("EXCEPTION: 1GE(5) dropped (a taxi capable of zero emissions pays the higher rate)",
            _swap(39, _wrap(_atom_to("taxi", FALSE)))),
    "M12": ("STANDARD: 1GC(5) 6d-TEMP exclusion dropped (a Euro 6d-TEMP certificate read as meeting Euro 6d)",
            _swap(33, _wrap(_temp_as_6d))),
    "M13": ("DATE: 1GE(1)(b) 'less than six years' read as 'not more than six whole years'",
            _swap(36, _wrap(_json_sub('["lt", ["const", "year_count"', '["le", ["const", "year_count"')))),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
