"""HICBC (ITEPA 2003 ss. 681B-681H): the VE translation. Statute corpus law 2. SAME-FAMILY (Opus 5.5 author). NOT for merge.

Written from the pinned source (manage-agents reviews/spare/statute-corpus/hicbc/source.txt, sha256 18c35647...fcb042d4)
BEFORE the encoder's question file was opened (this file's first commit precedes cases.py). One translation pass with
today's language: ve.core@0.2 formulas (documents@1, order@0, relational-fol@0, time@0), unary/binary predicates, money
comparisons; nothing here is a Lean kernel line, a profile, a refuses pair or a lint change.

Entities of a case (all named by the case; domain closure, as law 1):
- person: every person the question names.
- item: one amount in respect of child benefit: one person's entitlement for one child over one SEGMENT of weeks of the tax
  year (bridge: the Monday-weeks of the year, grouped so that every stated fact is constant over a segment's weeks; the
  item's total is weeks x the weekly amount). "For a week" conditions are decided per item; every week of an item is alike.
- pair: an unordered pair of two different named persons. A pair constant denotes its two members (link(pair, person) is
  decided at grounding, as law 1 decides equality between named constants).
- daytype: one combination of the stated relationship facts that holds on some day (bridge). in_week(daytype, item) says it
  occurs on a day of the item's weeks; "throughout the week" = on every day-type that occurs (681B(3)(b), (4)(b), 681D(1)(b),
  681E(2)(b)).
Arithmetic of 681C(2)-(3) and the calendar of 681H(3) are bridges (bridge/bridges.py, tested): never written here.
"""
from __future__ import annotations

import itertools
import json

LIMIT = "60000.00"   # 681B(1)(a) and L in 681C(2)(b)

# ---- vocabulary --------------------------------------------------------------------------------------------------------
FACTS = {  # predicate: (arguments, description) -- given facts (questions) or bridge outputs
    "entitled": (["person", "item"], "the person is entitled to the amount of child benefit"),
    "basis_b": (["item"], "the entitlement is by virtue of s.143(1)(b) SSCBA 1992 or s.139(1)(b) SSCB(NI)A 1992 (contributing to the cost of providing for the child)"),
    "election_13a": (["item"], "an election under s.13A SSAA 1992 or s.11A SSA(NI)A 1992 has effect in respect of the amount"),
    "by_145a": (["item"], "the person is entitled to the amount by virtue of s.145A SSCBA 1992 or s.141A SSCB(NI)A 1992"),
    "is_child": (["item"], "the amount is for a child or qualifying young person within s.142 SSCBA 1992 or s.138 SSCB(NI)A 1992"),
    "child_lives_with": (["person", "item"], "for the purposes of s.143(1)(a) SSCBA 1992 the person has the item's child living with them in the item's weeks"),
    "d4_short": (["item"], "bridge: the s.143(1)(b) period of entitlement which includes the item's weeks does not exceed 52 weeks"),
    "d4_a_before": (["item"], "bridge: the claimant is entitled for the child by virtue of s.143(1)(a) for the week immediately before that period"),
    "d4_a_after": (["item"], "bridge: the claimant is entitled for the child by virtue of s.143(1)(a) for the week immediately after that period"),
    "in_week": (["daytype", "item"], "bridge: the day-type occurs on a day of the item's weeks"),
    "married_or_cp": (["pair", "daytype"], "on the days of the type the two persons are married to, or civil partners of, each other"),
    "sep_court": (["pair", "daytype"], "on the days of the type the two persons are separated under a court order"),
    "sep_permanent": (["pair", "daytype"], "on the days of the type the two persons are separated in circumstances in which the separation is likely to be permanent (stated judgement)"),
    "as_if_married": (["pair", "daytype"], "on the days of the type the two persons are living together as if they were a married couple or civil partners (stated judgement)"),
}
DERIVED = {
    "partner_on": (["pair", "daytype"], "the two persons are partners of each other on the days of the type (681G(1)-(3))"),
    "partner_thr": (["pair", "item"], "the two persons are partners of each other throughout the item's weeks"),
    "over_limit": (["person"], "the person's adjusted net income for the year exceeds the limit (681B(1)(a))"),
    "ani_gt": (["person", "person"], "the first person's adjusted net income for the year exceeds the second's"),
    "counts": (["item"], "the amount is not disregarded under 681E(1)"),
    "ent0": (["person", "item"], "the person is entitled to the amount, and it is not disregarded"),
    "a0": (["person", "item"], "condition A (681B(3)) is met for the person and the amount, before 681D"),
    "b0": (["person", "item"], "condition B (681B(4)) is met for the person and the amount, before 681D"),
    "liable0": (["person", "item"], "the person is liable in respect of the amount under 681B, before 681D (681D(1)(b))"),
    "d4_ignored": (["item"], "the amount is ignored for 681D(1)(a) under 681D(4)"),
    "d_applies": (["item"], "section 681D applies to the amount (681D(1))"),
    "deemed": (["person", "item"], "681B applies as if the person were entitled to the amount (681D(2), (3))"),
    "d3_unresolved": (["item"], "681D applies but no single person has the highest adjusted net income (681D(3)): refused"),
    "ent1": (["person", "item"], "the person is entitled, or treated as entitled under 681D(2), to the amount"),
    "a1": (["person", "item"], "condition A is met for the person and the amount"),
    "b1": (["person", "item"], "condition B is met for the person and the amount"),
    "pre": (["person", "item"], "the person would be liable in respect of the amount apart from 681E(3)"),
    "e3_out": (["person", "item"], "681E(3): another partner of the same entitled person with a higher adjusted net income is the one liable"),
    "e3_unresolved": (["item"], "681E(2) applies but no single partner has the highest adjusted net income: refused"),
    "liable_for": (["person", "item"], "the person is liable to the charge in relation to the amount (the amount counts in 681C(1))"),
    "liable": (["person"], "the person is liable to the high income child benefit charge for the tax year (681B(1))"),
}
SORTS = ("person", "item", "pair", "daytype")


def environment(case_consts):
    """case_consts: {"person": [...], "item": [...], "pair": [...], "daytype": [...], "ani": [person...], "charge": [person...]}"""
    consts = {}
    for sort in SORTS:
        for c in case_consts.get(sort, []):
            consts[c] = {"sort": sort, "description": f"The case's {sort} {c}.", "verbalisation": f"the case's {c}"}
    for p in case_consts.get("ani", []):
        consts["ani_" + p] = {"sort": "$int", "unit": "gbp_penny", "description": f"The adjusted net income of {p} for the tax year.",
                              "verbalisation": f"the adjusted net income of {p}"}
    for p in case_consts.get("charge", []):
        consts["charge_" + p] = {"sort": "$int", "unit": "gbp_penny", "description": f"The amount of the charge on {p}.",
                                 "verbalisation": f"the charge on {p}"}
    preds = {n: {"arguments": a, "description": d[0].upper() + d[1:] + "."} for n, (a, d) in {**FACTS, **DERIVED}.items()}
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {s: {"description": f"A {s}."} for s in SORTS}, "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {"gbp_penny": {"scale": "100", "display": {"kind": "money", "currency": "GBP", "input_symbol": "£"}}}}


# ---- formula DSL with NAMED variables (grounded away before VE sees a formula) -------------------------------------------
def v(x): return ["var", x]
def t(x): return x if isinstance(x, list) else ["const", x]
def U(p, x): return ["unary", p, t(x)]
def B(p, x, y): return ["binary", p, t(x), t(y)]
def Not(f): return ["not", f]
def Imp(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def All(sort, x, f): return ["forall", sort, x, f]
def Ex(sort, x, f): return ["exists", sort, x, f]
def Neq(a, b): return ["neq", t(a), t(b)]            # decided at grounding (unique names)
def Link(pr, p): return ["link", t(pr), t(p)]       # decided at grounding (a pair names its two members)
def gbp(s): return ["decimal", "gbp_penny", s]
def ani(p): return ["ani", t(p)]                    # -> ["const", "gbp_penny", "ani_<p>"] at grounding
def Lt(a, b): return ["lt", a, b]


def And(*fs):
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["and", f, r]
    return r


def Or(*fs):
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["or", f, r]
    return r


def partner_of(q, p, i):
    """q is a partner of p throughout the weeks of item i (q, p different)."""
    return And(Neq(q, p), Ex("pair", "pr#", And(Link(v("pr#"), q), Link(v("pr#"), p), B("partner_thr", v("pr#"), i))))


P, Q, R, S, S2, T, X, Y, I, D, PR = (v(n) for n in ("P", "Q", "R", "S", "S2", "T", "X", "Y", "I", "D", "PR"))


def cond_a(ent, a):
    return All("person", "P", All("item", "I", Iff(B(a, P, I), And(B(ent, P, I), Not(Ex("person", "Q", And(
        partner_of(Q, P, I), B("ani_gt", Q, P))))))))


def cond_b(ent, b):
    return All("person", "P", All("item", "I", Iff(B(b, P, I), Ex("person", "Q", And(
        B(ent, Q, I), partner_of(Q, P, I), B("ani_gt", P, Q))))))


# ROWS: (id, provision, kind, formula or None, note). kind RULE = written; NAME = a declared name only; BRIDGED = done by the
# bridge script; NOT = not written; FACT = a given fact (stated in every question that needs it).
ROWS = [
    (1, "681B(1)", "RULE", And(
        All("person", "P", Iff(U("liable", P), Ex("item", "I", B("liable_for", P, I))))),
        "liable for the year = liable in relation to some amount for a week of the year; (a) over_limit and (b) A or B sit "
        "in pre/liable_for (rows 1b, 14)"),
    ("1b", "681B(1)(a)", "RULE", All("person", "P", Iff(U("over_limit", P), Lt(gbp(LIMIT), ani(P)))),
     "'exceeds' = strictly greater; ANI is a given number (681H(2))"),
    (2, "681B(2)", "NAME", None, "the name of the charge: a label with no condition"),
    (3, "681B(3)", "RULE", And(cond_a("ent0", "a0"), cond_a("ent1", "a1")), "condition A, before and after 681D"),
    (4, "681B(4)", "RULE", And(cond_b("ent0", "b0"), cond_b("ent1", "b1")), "condition B, before and after 681D"),
    ("4b", "681B (ANI comparisons)", "RULE",
     All("person", "P", All("person", "Q", Imp(Neq(P, Q), Iff(B("ani_gt", P, Q), Lt(ani(Q), ani(P)))))),
     "'has an adjusted net income which exceeds that of'"),
    (5, "681C(1)", "RULE", All("person", "P", All("item", "I", Iff(B("liable_for", P, I), And(B("pre", P, I), Not(B("e3_out", P, I)))))),
     "WHICH amounts count for P (A or B met, and P the one liable after 681E(3)); the total and the percentage of it are "
     "bridged (row 7)"),
    (6, "681C(2)", "BRIDGED", None, "the appropriate percentage: min(100, floor((ANI - 60000) / 200)) from bridges.py"),
    (7, "681C(3)", "BRIDGED", None, "rounding down the total, the charge and the percentage: bridges.py"),
    (8, "681D(1)", "RULE", All("item", "I", Iff(U("d_applies", I), And(
        U("counts", I), U("basis_b", I), U("is_child", I), Not(U("d4_ignored", I)),
        All("person", "R", Imp(B("ent0", R, I), And(Not(B("liable0", R, I)), All("person", "Q", Imp(
            partner_of(Q, R, I), Not(B("liable0", Q, I))))))),
        Ex("person", "R", Ex("person", "S", And(B("ent0", R, I), Neq(S, R), B("child_lives_with", S, I))))))),
     "(a) R entitled by s.143(1)(b) (a fact); (b) neither R nor a partner of R throughout the week liable in respect of "
     "it; (c) another person S has the child living with them in that week (a fact)"),
    ("8b", "681D(1)(b)", "RULE", All("person", "P", All("item", "I", Iff(B("liable0", P, I), And(
        U("over_limit", P), Or(B("a0", P, I), B("b0", P, I)))))),
     "'liable ... in respect of that amount under section 681B'"),
    (9, "681D(2)", "RULE", All("person", "S", All("item", "I", Iff(B("deemed", S, I), And(
        U("d_applies", I), B("child_lives_with", S, I), Not(B("ent0", S, I)),
        All("person", "S2", Imp(And(Neq(S2, S), B("child_lives_with", S2, I), Not(B("ent0", S2, I))),
                                B("ani_gt", S, S2))))))),
     "with (3): the person the child lives with (not R), and of several, the one with the highest ANI"),
    (10, "681D(3)", "RULE", All("item", "I", Iff(U("d3_unresolved", I), And(
        U("d_applies", I), Not(Ex("person", "S", B("deemed", S, I)))))),
     "a tie for the highest ANI: the text names no one; refused (the case is answered OPEN)"),
    ("10b", "681B as applied by 681D(2)", "RULE", All("person", "P", All("item", "I", Iff(B("ent1", P, I), Or(
        B("ent0", P, I), B("deemed", P, I))))), "entitled, or treated as entitled"),
    (11, "681D(4)", "RULE", All("item", "I", Iff(U("d4_ignored", I), And(
        U("basis_b", I), U("d4_short", I), U("d4_a_before", I), U("d4_a_after", I)))),
     "the 52-week length and the neighbouring weeks are bridge facts; the condition is written"),
    (12, "681D(5)", "FACT", None, "'child' by reference to s.142 SSCBA 1992: a given fact (is_child)"),
    (13, "681E(1)", "RULE", All("item", "I", Iff(U("counts", I), And(Not(U("election_13a", I)), Not(U("by_145a", I))))),
     "(a) a s.13A election in effect and (b) s.145A entitlement: disregarded for the whole Chapter"),
    ("13b", "681E(1)", "RULE", All("person", "P", All("item", "I", Iff(B("ent0", P, I), And(B("entitled", P, I), U("counts", I))))),
     "entitlement to an amount not disregarded"),
    (14, "681E(2)", "RULE", All("person", "P", All("item", "I", Iff(B("pre", P, I), And(
        U("over_limit", P), Or(B("a1", P, I), B("b1", P, I)))))),
     "(c) 'would, apart from subsection (3), each be liable ... in relation to that amount'"),
    (15, "681E(3)", "RULE", And(
        All("person", "P", All("item", "I", Iff(B("e3_out", P, I), And(B("pre", P, I), Ex("person", "T", And(
            B("ent1", T, I), partner_of(P, T, I), Ex("person", "X", And(
                Neq(X, P), partner_of(X, T, I), B("pre", X, I), B("ani_gt", X, P))))))))),
        All("item", "I", Iff(U("e3_unresolved", I), Ex("person", "T", Ex("person", "X", Ex("person", "Y", And(
            Neq(X, Y), B("ent1", T, I), partner_of(X, T, I), partner_of(Y, T, I), B("pre", X, I), B("pre", Y, I),
            Not(B("e3_out", X, I)), Not(B("e3_out", Y, I))))))))),
     "only the partner with the highest ANI is liable; two left at the top = a tie: refused"),
    (16, "681G(1)", "RULE", All("pair", "PR", All("item", "I", Iff(B("partner_thr", PR, I), All("daytype", "D", Imp(
        B("in_week", D, I), B("partner_on", PR, D)))))),
     "'a partner ... at any time': partners on every day of the week = throughout the week"),
    (17, "681G(2)", "RULE", All("pair", "PR", All("daytype", "D", Iff(B("partner_on", PR, D), Or(
        And(B("married_or_cp", PR, D), Not(B("sep_court", PR, D)), Not(B("sep_permanent", PR, D))),
        And(Not(B("married_or_cp", PR, D)), B("as_if_married", PR, D)))))),
     "condition A (married or civil partners, neither (a) nor (b)) or condition B (681G(3)); 'likely to be permanent' and "
     "'as if they were a married couple' are stated facts (judgement)"),
    (18, "681G(3)", "RULE", None, "written in row 17 (condition B of 681G)"),
    (19, "681H(2)", "NAME", None, "ANI by reference to ITA 2007 s.58: a given number per person and year"),
    (20, "681H(3)", "BRIDGED", None, "'week' = 7 days from a Monday, in the tax year iff its Monday is: bridges.py"),
]


# ---- grounding -----------------------------------------------------------------------------------------------------------
TRUE, FALSE = ["true"], ["false"]


def pair_name(a, b):
    a, b = sorted((a, b))
    return f"pr__{a}__{b}"


def pair_members(name):
    _, a, b = name.split("__")
    return {a, b}


def ground(f, dom, env=None):
    env = env or {}
    if type(f) is not list or not f:
        return f
    h = f[0]
    if h == "var":
        return ["const", env[f[1]]]
    if h in ("forall", "exists"):
        _, sort, x, body = f
        parts = [ground(body, dom, {**env, x: c}) for c in dom[sort]]
        if not parts:
            return TRUE if h == "forall" else FALSE
        return simplify(["and" if h == "forall" else "or", *parts])
    if h == "neq":
        a, b = ground(f[1], dom, env), ground(f[2], dom, env)
        return FALSE if a == b else TRUE
    if h == "link":
        pr, p = ground(f[1], dom, env), ground(f[2], dom, env)
        return TRUE if p[1] in pair_members(pr[1]) else FALSE
    if h == "ani":
        p = ground(f[1], dom, env)
        return ["const", "gbp_penny", "ani_" + p[1]]
    if h in ("unary", "binary"):
        return [h, f[1], *(ground(x, dom, env) for x in f[2:])]
    if h in ("and", "or", "implies", "not"):
        return simplify([h, *(ground(x, dom, env) for x in f[1:])])
    if h in ("lt", "le", "eq"):
        return [h, *(ground(x, dom, env) for x in f[1:])]
    return f


def simplify(f):
    h = f[0]
    if h == "not":
        return FALSE if f[1] == TRUE else TRUE if f[1] == FALSE else f
    if h == "implies":
        a, b = f[1], f[2]
        if a == FALSE or b == TRUE:
            return TRUE
        if a == TRUE:
            return b
        if b == FALSE:
            return simplify(["not", a])
        return f
    if h in ("and", "or"):
        unit, zero = (TRUE, FALSE) if h == "and" else (FALSE, TRUE)
        parts = []
        for p in f[1:]:
            if p == unit:
                continue
            if p == zero:
                return zero
            parts.append(p)
        if not parts:
            return unit
        out = parts[-1]
        for p in reversed(parts[:-1]):
            out = [h, p, out]
        return out
    return f


def key(f):
    return json.dumps(f, sort_keys=True, separators=(",", ":"))


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
    if is_iff(f):
        lhs = f[1][1]
        if lhs[0] in ("unary", "binary"):
            return [key(lhs)]
        raise ValueError(f"iff with a non-atom left side: {f}")
    if f[0] == "implies":
        c = f[2]
        if c[0] == "eq" and c[1][0] == "const" and len(c[1]) == 3:
            return [c[1][2]]
        return defines(c)
    if f[0] in ("unary", "binary"):
        return [key(f)]
    if f[0] == "not" and f[1][0] in ("unary", "binary"):
        return [key(f[1])]
    raise ValueError(f"no defined target: {f}")


def table(mutant=None):
    rows = {r[0]: r for r in ROWS}
    if mutant is not None:
        rows = MUTANTS[mutant][1](rows)
    return rows


def rules(dom, ani_people, mutant=None):
    """Ground rules for a case. dom: {sort: [constants]}; ani_people: persons with a stated ANI (rows using ani() are
    grounded only over them)."""
    out = []
    for rid, row in table(mutant).items():
        _, prov, kind, formula, _ = row
        if kind != "RULE" or formula is None:
            continue
        uses_ani = "\"ani\"" in json.dumps(formula)
        d = dict(dom)
        if uses_ani:
            d["person"] = [p for p in dom["person"] if p in ani_people]
        g = ground(formula, d)
        for k, part in enumerate(conjuncts(g)):
            if part == TRUE:
                continue
            if part == FALSE:
                raise ValueError(f"row {rid} grounds to false")
            out.append({"id": f"r{rid}.{k}", "row": rid, "formula": part, "defines": defines(part)})
    return out


def charge_rules(subject, items, table_rows):
    """681C(1) with the bridged arithmetic: for each set of the subject's amounts that may count (liable_for), the bridged
    charge. table_rows: [{"counted": [item...], "charge": "123.00"}] over every subset of `items` (bridges.py)."""
    out = []
    for k, row in enumerate(table_rows):
        lits = [B("liable_for", subject, i) if i in row["counted"] else Not(B("liable_for", subject, i)) for i in items]
        f = Imp(And(*lits) if lits else TRUE, ["eq", ["const", "gbp_penny", "charge_" + subject], gbp(row["charge"])])
        out.append({"id": f"c.{k}", "row": "681C", "formula": simplify(f), "defines": ["charge_" + subject]})
    return out


# ---- planted errors: each must change a named household's answer (run.py --mutants) --------------------------------------
def _replace(old, new):
    def walk(f):
        if f == old:
            return new
        if type(f) is list:
            return [walk(x) for x in f]
        return f
    return walk


def _swap(rid, fn):
    def apply(rows):
        r = dict(rows)
        a, b, c, formula, note = r[rid]
        r[rid] = (a, b, c, fn(formula), note)
        return r
    return apply


MUTANTS = {
    "M1": ("681B(1)(a) read as 'at least £60,000' (le for lt)",
           _swap("1b", _replace(Lt(gbp(LIMIT), ani(P)), ["le", gbp(LIMIT), ani(P)]))),
    "M2": ("'throughout the week' read as 'on some day of the week'",
           _swap(16, _replace(All("daytype", "D", Imp(B("in_week", D, I), B("partner_on", PR, D))),
                              Ex("daytype", "D", And(B("in_week", D, I), B("partner_on", PR, D)))))),
    "M3": ("681E(1)(a) dropped: an amount under a s.13A election still counts",
           _swap(13, _replace(Not(U("election_13a", I)), ["true"]))),
    "M4": ("681G(2)(b) dropped: a permanent separation still leaves partners",
           _swap(17, _replace(Not(B("sep_permanent", PR, D)), ["true"]))),
    "M5": ("681D(1)(b) dropped: 681D applies even when R or R's partner is liable",
           _swap(8, _replace(All("person", "R", Imp(B("ent0", R, I), And(Not(B("liable0", R, I)), All("person", "Q", Imp(
               partner_of(Q, R, I), Not(B("liable0", Q, I))))))), ["true"]))),
}
