"""Formal content of the mini-paper: every VE statement is built here, once.

Nothing in this file is trusted.  It only *constructs* abstract syntax; all
judgements come from `ve.prove_entailment` / `ve.check_entailment_certificate`
(Python), the Lean `ve_conformance check-certificate` executable, and
`ve.find_countermodel`.
"""
from __future__ import annotations

import json
from pathlib import Path

from ve import (And, Binary, Eq, Exists, Forall, Implies, Not, Or, Unary, Var,
                Environment, Named, Reach)

HERE = Path(__file__).resolve().parent

ENV = Environment.from_dict(json.loads((HERE / "environment.json").read_text()))
ENV_TC = Environment.from_dict(json.loads((HERE / "environment-closure.json").read_text()))

S = "point"


# ---------------------------------------------------------------- combinators
def iff(a, b):
    """VE has no biconditional connective; a definition axiom spells it out."""
    return And(Implies(a, b), Implies(b, a))


def all1(body):
    return Forall(S, body)


def all2(body):
    return Forall(S, Forall(S, body))


def all3(body):
    return Forall(S, Forall(S, Forall(S, body)))


def all4(body):
    return Forall(S, Forall(S, Forall(S, Forall(S, body))))


def rel(p, i, j):
    return Binary(p, Var(i), Var(j))


# ------------------------------------------------------- relational vocabulary
def irreflexive(p):
    return all1(Not(rel(p, 0, 0)))


def reflexive(p):
    return all1(rel(p, 0, 0))


def symmetric(p):
    return all2(Implies(rel(p, 1, 0), rel(p, 0, 1)))


def asymmetric(p):
    return all2(Implies(rel(p, 1, 0), Not(rel(p, 0, 1))))


def antisymmetric(p):
    return all2(Implies(And(rel(p, 1, 0), rel(p, 0, 1)), Eq(Var(1), Var(0))))


def transitive(p):
    return all3(Implies(And(rel(p, 2, 1), rel(p, 1, 0)), rel(p, 2, 0)))


def serial(p):
    return all1(Exists(S, rel(p, 1, 0)))


def total(p):
    # x = y, or x < y, or y < x.
    return all2(Or(Eq(Var(1), Var(0)), Or(rel(p, 1, 0), rel(p, 0, 1))))


def diagonal(p):
    """No x lists exactly the p-non-self-listing points."""
    return Not(Exists(S, Forall(S, iff(rel(p, 1, 0), Not(rel(p, 0, 0))))))


# -------------------------------------------------------- definition axioms
# A definition in VE is an ordinary biconditional premise.  It carries no
# special status and MUST be repeated among the hypotheses of every theorem
# that mentions the defined symbol.
DEF_GREATEST = all1(iff(Unary("greatest", Var(0)), Forall(S, rel("le", 0, 1))))
DEF_SIM = all2(iff(rel("sim", 1, 0), And(rel("le", 1, 0), rel("le", 0, 1))))
DEF_MINIMAL = all1(iff(Unary("minimal", Var(0)), Forall(S, Not(rel("lt", 0, 1)))))
DEF_LEAST = all1(iff(Unary("least", Var(0)),
                     Forall(S, Implies(Not(Eq(Var(0), Var(1))), rel("lt", 1, 0)))))


# The T7 family.  `T7_GOAL` is the statement a mathematician would write; the
# prover cannot reach it from the definition axiom directly (see the paper), so
# the two congruence halves are proved separately and then used as explicit
# hypotheses -- VE has no lemma-citation mechanism.
T7_GOAL = all4(Implies(And(rel("sim", 3, 2), And(rel("sim", 1, 0), rel("le", 3, 1))),
                       rel("le", 2, 0)))
T7A = all3(Implies(And(rel("sim", 2, 1), rel("le", 2, 0)), rel("le", 1, 0)))
T7B = all3(Implies(And(rel("le", 2, 1), rel("sim", 1, 0)), rel("le", 2, 0)))


# Hand-supplied countermodel candidates for hypothesis-necessity checks that the
# exhaustive search cannot finish inside the v0 evaluation budget.  They are not
# trusted: `verify.py` re-checks each with `ve.check_countermodel`.
NECESSITY_HINTS = {
    ("T6", "transitivity of le"): {
        "complete": True,
        "domains": {"point": ["a", "b", "c"]},
        "constants": {},
        "relations": {
            "le": [["a", "a"], ["a", "b"], ["b", "a"], ["b", "b"], ["b", "c"],
                   ["c", "b"], ["c", "c"]],
            "sim": [["a", "a"], ["a", "b"], ["b", "a"], ["b", "b"], ["b", "c"],
                    ["c", "b"], ["c", "c"]],
            "greatest": [], "minimal": [], "least": [],
            "lists": [], "mentions": [], "lt": [], "akin": [],
        },
    },
}


# ------------------------------------------------------------------ theorems
# Each entry: id, title, environment, ordered (label, formula) premises, goal.
THEOREMS = [
    dict(id="T1", title="Diagonal lemma (Russell / barber / relational Cantor)",
         env=ENV, premises=[], goal=diagonal("lists")),

    dict(id="T2", title="Corollary: the diagonal lemma at two distinct relations",
         env=ENV, premises=[], goal=And(diagonal("lists"), diagonal("mentions"))),

    dict(id="T3", title="Irreflexive and transitive implies asymmetric",
         env=ENV,
         premises=[("irreflexivity", irreflexive("lt")), ("transitivity", transitive("lt"))],
         goal=asymmetric("lt")),

    dict(id="T4", title="Asymmetric implies irreflexive",
         env=ENV,
         premises=[("asymmetry", asymmetric("lt"))],
         goal=irreflexive("lt")),

    dict(id="T5", title="Uniqueness of a greatest element in a partial order",
         env=ENV,
         premises=[("definition of greatest", DEF_GREATEST),
                   ("antisymmetry", antisymmetric("le"))],
         goal=all2(Implies(And(Unary("greatest", Var(1)), Unary("greatest", Var(0))),
                           Eq(Var(1), Var(0))))),

    dict(id="T6", title="In a preorder, the symmetrisation is an equivalence relation",
         env=ENV,
         premises=[("definition of sim", DEF_SIM),
                   ("reflexivity of le", reflexive("le")),
                   ("transitivity of le", transitive("le"))],
         goal=And(reflexive("sim"), And(symmetric("sim"), transitive("sim")))),

    dict(id="T7mono", title="The preorder respects its symmetrisation (monolithic attempt)",
         env=ENV,
         premises=[("definition of sim", DEF_SIM),
                   ("transitivity of le", transitive("le"))],
         goal=T7_GOAL, expect="fail", max_steps=1_000_000, skip_necessity=True),

    dict(id="T7a", title="Left congruence of the preorder under its symmetrisation",
         env=ENV,
         premises=[("definition of sim", DEF_SIM),
                   ("transitivity of le", transitive("le"))],
         goal=T7A),

    dict(id="T7b", title="Right congruence of the preorder under its symmetrisation",
         env=ENV,
         premises=[("definition of sim", DEF_SIM),
                   ("transitivity of le", transitive("le"))],
         goal=T7B),

    dict(id="T7", title="The preorder respects its symmetrisation (from the two congruence lemmas)",
         env=ENV,
         premises=[("left congruence (T7a)", T7A), ("right congruence (T7b)", T7B)],
         goal=T7_GOAL),

    dict(id="T8", title="In a total strict order, a minimal element is least",
         env=ENV,
         premises=[("totality", total("lt")),
                   ("definition of minimal", DEF_MINIMAL),
                   ("definition of least", DEF_LEAST)],
         goal=all1(Implies(Unary("minimal", Var(0)), Unary("least", Var(0))))),

    # --- closure profile ----------------------------------------------------
    dict(id="T9", title="Closure induction: r included in transitive s implies tc[r] included in s",
         env=ENV_TC,
         premises=[("edge inclusion r <= s", all2(Implies(rel("r", 1, 0), rel("s", 1, 0)))),
                   ("transitivity of s", transitive("s"))],
         goal=all2(Implies(Reach("plus", Named("r"), Var(1), Var(0)), rel("s", 1, 0))),
         expect="fail"),

    dict(id="T9a", title="Every r-edge is a tc[r]-path",
         env=ENV_TC, premises=[],
         goal=all2(Implies(rel("r", 1, 0), Reach("plus", Named("r"), Var(1), Var(0))))),

    dict(id="T9b", title="tc[r] is included in rtc[r]",
         env=ENV_TC, premises=[],
         goal=all2(Implies(Reach("plus", Named("r"), Var(1), Var(0)),
                           Reach("star", Named("r"), Var(1), Var(0))))),

    dict(id="T9c", title="rtc[r] is reflexive",
         env=ENV_TC, premises=[],
         goal=all1(Reach("star", Named("r"), Var(0), Var(0)))),

    dict(id="T9d", title="tc[r] is transitive",
         env=ENV_TC, premises=[],
         goal=all3(Implies(And(Reach("plus", Named("r"), Var(2), Var(1)),
                               Reach("plus", Named("r"), Var(1), Var(0))),
                           Reach("plus", Named("r"), Var(2), Var(0))))),

    dict(id="T9e", title="Monotonicity: r included in s implies tc[r] included in tc[s]",
         env=ENV_TC,
         premises=[("edge inclusion r <= s", all2(Implies(rel("r", 1, 0), rel("s", 1, 0))))],
         goal=all2(Implies(Reach("plus", Named("r"), Var(1), Var(0)),
                           Reach("plus", Named("s"), Var(1), Var(0)))),
         expect="fail"),

    # --- conjecture ---------------------------------------------------------
    dict(id="C1", title="CONJECTURE (false): every transitive symmetric relation is reflexive",
         env=ENV,
         premises=[("transitivity", transitive("akin")), ("symmetry", symmetric("akin"))],
         goal=reflexive("akin"),
         expect="refuted"),

    dict(id="C2", title="Corrected: transitive, symmetric and serial implies reflexive",
         env=ENV,
         premises=[("transitivity", transitive("akin")), ("symmetry", symmetric("akin")),
                   ("seriality", serial("akin"))],
         goal=reflexive("akin")),
]
