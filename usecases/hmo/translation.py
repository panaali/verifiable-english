"""HMO England: mechanical grounding of rows.py for one case. SAME-FAMILY (Opus 5.5 author). Same steps as
usecases/pawhp/translation.py (grounding over the case's names with unique names, splitting conjunctions, "defines"), plus the
expansion of the AtLeast abbreviation. Nothing here reads the law: every reading is in rows.py; every fact in cases.py.

AtLeast(k, sort, body) = "exists x1..xk pairwise different with body(x1) .. body(xk)". Under unique names, writing it out over
all k-tuples and deciding the equations gives a disjunction whose disjuncts are, up to order, one per k-SUBSET of the domain;
`ground` writes the subset form directly (atleast_fol writes the tuple form; test_translation.py checks both agree as
propositional formulas on every assignment of small domains).
"""
from __future__ import annotations

import itertools
import json

import rows as R

TRUE, FALSE = ["true"], ["false"]  # grounding sentinels only; never reach VE


def key(formula):
    return json.dumps(formula, sort_keys=True, separators=(",", ":"))


def q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def environment():
    return R.environment()


def is_entity(term):
    return type(term) is list and len(term) == 2 and term[0] == "const"


def subst0(formula, const, depth=0):
    """Replace var `depth` (the innermost binder at this point) by const, lowering outer vars by one."""
    if type(formula) is not list or not formula:
        return formula
    h = formula[0]
    if h == "var":
        i = formula[1]
        if i == depth:
            return ["const", const]
        return ["var", i - 1] if i > depth else formula
    if h in ("forall", "exists"):
        return [h, formula[1], subst0(formula[2], const, depth + 1)]
    if h == "atleast":
        return [h, formula[1], formula[2], subst0(formula[3], const, depth + 1)]
    return [h] + [subst0(x, const, depth) if type(x) is list else x for x in formula[1:]]


def ground(formula, domains):
    if type(formula) is not list or not formula:
        return formula
    head = formula[0]
    if head in ("forall", "exists"):
        parts = [ground(subst0(formula[2], d), domains) for d in domains[formula[1]]]
        return simplify(["and" if head == "forall" else "or_n", *parts]) if parts else (TRUE if head == "forall" else FALSE)
    if head == "atleast":
        k, sort, body = formula[1], formula[2], formula[3]
        inst = {d: ground(subst0(body, d), domains) for d in domains[sort]}
        combos = [simplify(["and", *(inst[d] for d in combo)]) for combo in itertools.combinations(domains[sort], k)]
        return simplify(["or_n", *combos]) if combos else FALSE
    if head in ("unary", "binary"):
        return formula
    if head == "eq":
        a, b = formula[1], formula[2]
        if is_entity(a) and is_entity(b):
            return TRUE if a == b else FALSE
        return formula
    if head in ("and", "or", "implies", "not"):
        return simplify([head, *(ground(f, domains) for f in formula[1:])])
    return formula


def atleast_fol(k, sort, body):
    """The literal FOL form of AtLeast (k nested exists, pairwise inequalities), for the equivalence test only."""
    def at(f, i):
        if type(f) is not list or not f:
            return f
        if f == ["var", 0]:
            return ["var", i]
        return [f[0]] + [at(x, i) if type(x) is list else x for x in f[1:]]
    conj = [at(body, i) for i in range(k)]
    conj += [["not", ["eq", ["var", i], ["var", j]]] for i in range(k) for j in range(i + 1, k)]
    f = R.And(*conj)
    for _ in range(k):
        f = ["exists", sort, f]
    return f


def simplify(f):
    head = f[0]
    if head == "not":
        return FALSE if f[1] == TRUE else TRUE if f[1] == FALSE else f
    if head in ("and", "or_n", "or"):
        unit, zero = (TRUE, FALSE) if head == "and" else (FALSE, TRUE)
        parts = []
        for p in f[1:]:
            if p == unit or p in parts:
                continue
            parts.append(p)
        if any(p == zero for p in parts):
            return zero
        if not parts:
            return unit
        return balanced("and" if head == "and" else "or", parts)
    if head == "implies":
        a, b = f[1], f[2]
        if a == FALSE or b == TRUE:
            return TRUE
        if a == TRUE:
            return b
        if b == FALSE:
            return simplify(["not", a])
        return f
    return f


def balanced(op, parts):
    """A balanced binary tree (depth log2 of the parts: VE's MAX_DEPTH is 64); same meaning as the right-nested chain."""
    if len(parts) == 1:
        return parts[0]
    mid = len(parts) // 2
    return [op, balanced(op, parts[:mid]), balanced(op, parts[mid:])]


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
    for part in f[1:]:
        atoms_in(part, atoms, constants)


def defines(f):
    if type(f) is list and f[:1] == ["implies"] and not is_iff(f):
        return defines(f[2])  # a guarded definition: guard -> (atom <-> body)
    if is_iff(f):
        lhs = f[1][1]
        if lhs[0] in ("unary", "binary"):
            return [key(lhs)]
        raise ValueError(f"iff with a non-atom left side: {f}")
    if f[0] in ("unary", "binary"):
        return [key(f)]
    if f[0] == "not" and f[1][0] in ("unary", "binary"):
        return [key(f[1])]
    raise ValueError(f"no defined target: {f}")


def rules(domains, mutant=None):
    table = dict(R.T)
    if mutant is not None:
        table = MUTANTS[mutant][1](table)
    out = []
    for n in sorted(table):
        cat, formula, _, _ = table[n]
        if cat != "RULE":
            continue
        g = ground(formula, domains)
        for i, part in enumerate(conjuncts(g)):
            if part == TRUE:
                continue
            if part == FALSE:
                raise ValueError(f"row {n} grounds to false")
            out.append({"id": f"r{n}.{i}", "row": n, "formula": part, "defines": defines(part)})
    return out


# --- planted errors (mutants): each must change at least one in-scope answer (run.py --mutants) --------------------------

def _swap(n, f):
    def apply(table):
        t = dict(table)
        cat, formula, note, units = t[n]
        t[n] = (cat, f(formula), note, units)
        return t
    return apply


def _replace(old, new):
    def walk(f):
        if f == old:
            return new
        if type(f) is list:
            return [walk(x) for x in f]
        return f
    return walk


def _rename(old, new):
    def walk(f):
        if type(f) is list and f[:1] in (["unary"], ["binary"]) and f[1] == old:
            return [f[0], new] + f[2:]
        if type(f) is list:
            return [walk(x) for x in f]
        return f
    return walk


def _atleast_k(old, new):
    def walk(f):
        if type(f) is list and f[:1] == ["atleast"] and f[1] == old:
            return ["atleast", new] + f[2:]
        if type(f) is list:
            return [walk(x) for x in f]
        return f
    return walk


MUTANTS = {
    "M1": ("art. 4(a) five -> four persons", _swap(1, _atleast_k(5, 4))),
    "M2": ("Sch. 14 para 6(1)(c) with reg. 6(2): two -> three other persons", _swap(45, _atleast_k(3, 4))),
    "M3": ("s.258(4)(c) dropped: a half-sibling is not a relative",
           _swap(27, _rename("half_sibling_of", "sibling_of"))),
    "M4": ("art. 4(c)(ii) exception dropped: a purpose-built flat in a block of three or more is prescribed",
           _swap(3, _replace(R.Not(R.And(R.U("purpose_built", R.P), R.U("block3", R.P))), R.U("is_part", R.P)))),
    "M5": ("s.254(2)(f) dropped: the standard test needs no shared or lacking amenity",
           _swap(13, _replace(R.Or(R.U("shared_between", R.P), R.U("lacks", R.P)), R.U("only_use", R.P)))),
}
