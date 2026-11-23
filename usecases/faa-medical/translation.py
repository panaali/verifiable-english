"""14 CFR 61.23: the VE translation used by run.py. SAME-FAMILY (Opus 5.5 author; never a headline).

Statute corpus law 4 (row statute-corpus-faa-medical, dri-statute-corpus-faa-medical-1123). The formulas are rows.py,
written from the source text before the encoder's file was opened. This file adds only MECHANICAL steps (law 1's
translation.py, adapted from people/marriages to certificates/applications):

1. Grounding. A rule "for every certificate ..." is written out once for each certificate the case names; "some
   certificate" is the disjunction over them; the same for applications. The case names every medical certificate and
   application the question states (domain closure, an encoding convention stated in cases.py). Distinct constants denote
   distinct records (unique names), so an equation between two of them is decided here and simplified away. The per-
   certificate (d) rules (rows.cert_rules) are written once per certificate the case names.
2. Splitting. A rule that is a conjunction becomes one rule per conjunct; "exactly when" (two implications) stays one rule.
3. "defines". Each rule names the atom (or the day constant) it fixes: the left side of "exactly when", else the atoms and
   constants in the "then" part. run.py proves one defined atom at a time from its rules.

Nothing here is a Lean kernel line, a profile or a refuses pair: the environment is rows.environment().
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

import rows as R  # noqa: E402

TRUE, FALSE = ["true"], ["false"]  # grounding sentinels only; never reach VE


def environment():
    return R.environment()


def key(formula):
    return json.dumps(formula, sort_keys=True, separators=(",", ":"))


def q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def is_entity(term):
    return type(term) is list and len(term) == 2 and term[0] == "const" and (
        term[1] in R.CERTS or term[1] in R.APPS or term[1] == "pilot")


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
    return formula  # date comparisons and terms: no variables inside


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
    """The atoms / day constants a ground rule fixes."""
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


def rules(certs, apps=(), mutant=None):
    """Ground rules for a case: [{"id", "cite", "formula", "defines"}]."""
    table = R.T(list(certs), list(apps))
    if mutant is not None:
        table = MUTANTS[mutant][1](table)
    domains = {"certificate": list(certs), "application": list(apps), "person": ["pilot"]}
    out = []
    for rid, cite, formula in table:
        g = ground(formula, domains)
        for i, part in enumerate(conjuncts(g)):
            if part == TRUE:
                continue
            if part == FALSE:
                raise ValueError(f"rule {rid} grounds to false")
            out.append({"id": f"{rid}.{i}", "cite": cite, "formula": part, "defines": defines(part)})
    return out


# --- planted errors (mutants): each must change the answer of a named case (run.py --mutants) ------

def _walk(old, new):
    def walk(f):
        if f == old:
            return new
        if type(f) is list:
            return [walk(x) for x in f]
        return f
    return walk


def _on(suffix, fn):
    def apply(table):
        return [(rid, cite, fn(f) if rid == suffix or rid.endswith("." + suffix) else f) for rid, cite, f in table]
    return apply


def _end(n_old, n_new):
    def fn(f):
        def walk(x):
            if type(x) is list and len(x) == 3 and x[0] == "const" and x[1] == "day" and x[2].endswith(f"_end{n_old}"):
                return ["const", "day", x[2][: -len(str(n_old))] + str(n_new)]
            if type(x) is list:
                return [walk(y) for y in x]
            return x
        return walk(f)
    return fn


MUTANTS = {
    "M1": ("(d)(1)(ii): first class, age 40+, ATP PIC lasts 12 months instead of 6", _on("d1ii", _end(6, 12))),
    "M2": ("(d)(3)(ii): third class, age 40+, lasts 60 months instead of 24", _on("d3ii", _end(24, 60))),
    "M3": ("(c)(1)(vi) 'Notwithstanding' dropped: (b)(2) wins over the night 61.113(i) rule",
           _on("b_eff", _walk(R.Not(R.u("c1vi")), R.Or(R.u("c1vi"), R.Not(R.u("c1vi")))))),
    "M4": ("(d) expiry read as exclusive: valid only BEFORE the end of the last day",
           _on("valid_med", _walk(R.no_later(R.ci("flight_day"), R.ci("expiry")), R.before(R.ci("flight_day"), R.ci("expiry"))))),
    "M5": ("(c)(3)(i)(C): the course window ignored (any course ever completed counts)",
           _on("c3ic", _walk(R.no_later(R.ci("flight_day"), R.ci("course_end24")),
                             R.no_later(R.ci("course_day"), R.ci("flight_day"))))),
    "M6": ("(a)(1)(iii): the 60th-birthday condition dropped (every part 121 required pilot needs first class)",
           _on("a13", _walk(R.u("reached_60"), R.u("part121")))),
}
