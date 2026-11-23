"""PAWHP (SSI 2024/351): the VE translation used by run.py. SAME-FAMILY (Opus 5.5 author; never a headline).

Stream 5 / statute corpus law 1, build half (row spare-second-statute-build, dri-spare-second-statute-build-1123).

What is translated: the formulas are rows_v2.py, a byte-for-byte copy of pass65.py v2 (finished before the questions
existed; checked below by hash). This file adds only MECHANICAL steps, no reading of the law:

1. Grounding. A rule "for every person ..." is written out once for each person the case names; "some person" is the
   disjunction over them; the same for marriages and for the five benefit constants. The case names everyone in the
   household (domain closure, an encoding convention stated in cases.py). Distinct constants denote distinct people
   (unique names), so an equation between two of them is decided here and simplified away.
2. Splitting. A rule that is a conjunction becomes one rule per conjunct; "exactly when" (two implications) stays one rule.
3. "defines". Each rule names the atom (or the amount / application day) it fixes: the left side of "exactly when",
   else the atoms and amounts in the "then" part. run.py proves one defined atom at a time from its rules.

Nothing here is a Lean kernel line, a profile or a refuses pair: the environment is rows_v2.environment() with domain
constants added for the other people and marriages a case names.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

import rows_v2 as R  # noqa: E402

ROWS_SLICE_SHA256 = "d93e89de686f843eb0344891bec8416ad500d1be7339f1ab9093a11dd302ea94"  # pass65.py v2 lines 37-348


def check_rows():
    text = (HERE / "rows_v2.py").read_text(encoding="utf-8")
    body = text[text.index("QW0, QW1 = "):]
    got = hashlib.sha256(body.encode("utf-8")).hexdigest()
    if got != ROWS_SLICE_SHA256:
        raise SystemExit(f"rows_v2.py differs from pass65.py v2 lines 37-348: {got}")


check_rows()

PEOPLE = ("applicant", "other1", "other2")  # person constants a case may name (households of up to 3 in the set)
MARRIAGES = ("marriage1",)
BENEFITS = tuple(R.BENEFITS)
AMOUNTS = ("316.70", "211.15", "158.35", "105.55", "0.00")  # reg. 10(4)-(6) and 9A(4)
TRUE, FALSE = ["true"], ["false"]  # grounding sentinels only; never reach VE


def environment():
    env = R.environment()
    consts = env["vocabulary"]["constants"]
    for p in PEOPLE[1:]:
        consts[p] = {"sort": "person", "description": f"Another person the case names ({p}).",
                     "verbalisation": f"the case's {p}"}
    for m in MARRIAGES:
        consts[m] = {"sort": "marriage", "description": f"A marriage the case names ({m}).",
                     "verbalisation": f"the case's {m}"}
    return env


def key(formula):
    return json.dumps(formula, sort_keys=True, separators=(",", ":"))


def q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


# --- grounding -----------------------------------------------------------------------------------

ENTITY_SORTS = ("person", "marriage", "benefit")


def is_entity(term):
    return type(term) is list and len(term) == 2 and term[0] == "const" and (
        term[1] in PEOPLE or term[1] in MARRIAGES or term[1] in BENEFITS)


def ground(formula, domains, stack=()):
    """Write out quantifiers over the case's domains; decide equations between entity constants."""
    if type(formula) is not list or not formula:
        return formula
    head = formula[0]
    if head == "var":
        return ["const", stack[formula[1]]]
    if head in ("forall", "exists"):
        parts = [ground(formula[2], domains, (d,) + stack) for d in domains[formula[1]]]
        return simplify(["and" if head == "forall" else "or_n", *parts])
    if head in ("unary", "binary"):
        return [head, formula[1], *(ground(t, domains, stack) for t in formula[2:])]
    if head == "eq":
        a, b = ground(formula[1], domains, stack), ground(formula[2], domains, stack)
        if is_entity(a) and is_entity(b):
            return TRUE if a == b else FALSE
        return ["eq", a, b]
    if head in ("and", "or", "implies", "not"):
        return simplify([head, *(ground(f, domains, stack) for f in formula[1:])])
    return formula  # date/decimal comparisons and terms: no variables inside in rows_v2


def simplify(f):
    head = f[0]
    if head == "not":
        return FALSE if f[1] == TRUE else TRUE if f[1] == FALSE else f
    if head in ("and", "or_n", "or"):
        unit, zero = (TRUE, FALSE) if head == "and" else (FALSE, TRUE)
        parts = [p for p in f[1:] if p != unit]
        if any(p == zero for p in parts):
            return zero
        if not parts:
            return unit
        out = parts[-1]
        for p in reversed(parts[:-1]):
            out = ["and" if head == "and" else "or", p, out]
        return out
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
        if lhs[0] == "not" and lhs[1][0] in ("unary", "binary"):
            return [key(lhs[1])]
        raise ValueError(f"iff with a non-atom left side: {f}")
    if f[0] == "implies":
        return defines_conclusion(f[2])
    if f[0] in ("unary", "binary"):
        return [key(f)]
    if f[0] == "not" and f[1][0] in ("unary", "binary"):
        return [key(f[1])]
    if f[0] == "eq" and f[1][0] == "const" and len(f[1]) == 3:
        return [f[1][2]]
    raise ValueError(f"no defined target: {f}")


def defines_conclusion(c):
    if is_iff(c) or c[0] in ("unary", "binary", "not", "implies") or (c[0] == "eq"):
        return defines(c)
    if c[0] == "and":
        out = []
        for part in conjuncts(c):
            out += defines(part)
        return list(dict.fromkeys(out))
    raise ValueError(f"no defined target in conclusion: {c}")


def rules(people, marriages=(), mutant=None):
    """Ground rules for a case: [{"id", "row", "cite", "formula", "defines"}]."""
    table = dict(R.T)
    if mutant is not None:
        table = MUTANTS[mutant][1](table)
    domains = {"person": list(people), "marriage": list(marriages), "benefit": list(BENEFITS)}
    out = []
    for n in sorted(table):
        cat, formula, _ = table[n]
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


# --- planted errors (mutants): each must change the answer of a named person (run.py --mutants) ------

def _swap(n, f):
    def apply(table):
        t = dict(table)
        cat, formula, note = t[n]
        t[n] = (cat, f(formula), note)
        return t
    return apply


def _replace_amount(old, new):
    def walk(f):
        if f == ["decimal", "gbp_penny", old]:
            return ["decimal", "gbp_penny", new]
        if type(f) is list:
            return [walk(x) for x in f]
        return f
    return walk


def _replace(old, new):
    def walk(f):
        if f == old:
            return new
        if type(f) is list:
            return [walk(x) for x in f]
        return f
    return walk


MUTANTS = {
    "M1": ("10(5)(a) pays 316.70 instead of 211.15", _swap(43, _replace_amount("211.15", "316.70"))),
    "M2": ("reg. 6 compares the pensionable-age date with the week's FIRST day", _swap(25, _replace(R.day(R.QW1), R.day(R.QW0)))),
    "M3": ("16B(2) limit read as before 31 March (strict)",
           _swap(63, lambda f: _replace(["date_no_later", R.ci("applicant_application"), R.day(R.END_MARCH)],
                                        ["date_before", R.ci("applicant_application"), R.day(R.END_MARCH)])(f))),
    "M4": ("reg. 4(2) dropped: an award in error still excludes",
           _swap(23, lambda f: _replace(R.Not(R.U("wfp_award_in_error", R.V(0))), R.U("wfp_awarded", R.V(0)))(f))),
    "M5": ("80th birthday compared with the week's first day", _swap(42, _replace(R.day(R.QW1), R.day(R.QW0)))),
}
