#!/usr/bin/env python3
"""Task B probe: how far does VE get with Euclid's infinitude of primes?

Writes `boundary/results.json` plus the `.ve` files it managed to produce.
Everything here is a *negative* result and is meant to be read with
`../boundary.md`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from ve import (And, Binary, Document, Environment, Exists, Forall, Implies,  # noqa: E402
                Not, Or, Unary, Var, VEError, find_countermodel, print_document,
                prove_entailment, render)

ENV = Environment.from_dict(json.loads((HERE / "environment.json").read_text()))
N = "number"

out = {"attempts": []}


def record(name, note, formula=None, error=None):
    entry = {"name": name, "note": note}
    if formula is not None:
        entry["ve"] = print_document(ENV, Document((formula,))).strip()
        entry["fluent"] = render(formula, ENV, "ve_fluent")
    if error is not None:
        entry["error"] = error
    out["attempts"].append(entry)
    return entry


# 1. The statement shape "there is no largest prime" IS expressible, because
#    `prime` and `lt` are taken as primitive uninterpreted symbols.
euclid = Forall(N, Implies(Unary("prime", Var(0)),
                           Exists(N, And(Unary("prime", Var(0)),
                                         Binary("lt", Var(1), Var(0))))))
record("euclid-statement",
       "Parses and type-checks. Says nothing about arithmetic: `prime` is an "
       "uninterpreted unary symbol.", euclid)
(HERE / "euclid-statement.ve").write_text(print_document(ENV, Document((euclid,))))

# 2. With no axioms it is of course not valid; the one-point model refutes it.
proof = prove_entailment(ENV, [], euclid, max_steps=50_000)
cm = find_countermodel(ENV, [], euclid, min_domain_size=1, max_domain_size=1)
out["unaxiomatised"] = {"prove_status": proof.status,
                        "countermodel_status": cm.status,
                        "countermodel": None if cm.model is None else cm.model.to_dict()}
if cm.model is not None:
    (HERE / "euclid-countermodel.json").write_text(
        json.dumps(cm.model.to_dict(), indent=2) + "\n")

# 3. The definition of "prime" needs a ternary product relation.
try:
    bad = Forall(N, Forall(N, Forall(N, Unary("times", Var(0)))))
    record("primality-definition", "unreachable", bad)
except VEError as exc:
    record("primality-definition",
           "Cannot be written: `p is prime iff p > 1 and for all a, b, a*b = p "
           "implies a = 1 or b = 1` needs the ternary relation times(a, b, c).",
           error=f"{type(exc).__name__}: {exc}")

# 4. What IS expressible about divisibility, without any arithmetic.
div_refl = Forall(N, Binary("divides", Var(0), Var(0)))
div_trans = Forall(N, Forall(N, Forall(N, Implies(
    And(Binary("divides", Var(2), Var(1)), Binary("divides", Var(1), Var(0))),
    Binary("divides", Var(2), Var(0))))))
prime_has_no_proper_divisor = Forall(N, Implies(
    Unary("prime", Var(0)),
    Forall(N, Implies(Binary("divides", Var(0), Var(1)),
                      Or(Unary("unit", Var(0)), Binary("associate", Var(0), Var(1)))))))
for name, f, note in [
    ("divides-reflexive", div_refl, "Statable: divisibility is a binary relation."),
    ("divides-transitive", div_trans, "Statable."),
    ("prime-has-no-proper-divisor", prime_has_no_proper_divisor,
     "Statable as an AXIOM about uninterpreted symbols. It is a consequence of "
     "primality in arithmetic; here it has to be assumed."),
]:
    record(name, note, f)

# 5. The three statements Euclid's proof needs and VE cannot make.
out["missing_for_the_proof"] = [
    "N = p1 * p2 * ... * pk + 1 : a product over a FINITE SET of unknown size, "
    "i.e. an iterated binary operation. Needs function symbols (G1), arity > 2 "
    "(G2), a set or list sort (G3) and recursion over it.",
    "every n > 1 has a prime divisor : provable by strong induction; VE has no "
    "induction (G5).",
    "p | N and p | N-1 implies p | 1 : needs subtraction and the unit (G1, G6).",
    "the set of primes is finite / enumerate p1..pk : needs finiteness, hence "
    "sets or numbers (G3, G6).",
]

(HERE / "results.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2)[:3000])
