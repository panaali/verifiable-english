"""Batch 15a review fixes: Lean's metered route (`ve_metered`) against Python.

Two differentials, each comparing the whole public answer (value, status,
counts, trace; suitable, evaluations, exhausted; error versus error):

* the saved conformance corpora (evaluation, countermodels, closure), each
  case with its own frozen `ve.core@0` / `ve.core@0.1` envelope, as plan
  section 4 requires of 15a;
* a seeded random differential over every checker family and the statement
  layers that change evaluation (definitions, data flags, regulated
  predicates, the layered core), with one- to three-entity domains and every
  formula and term constructor of `ve.ast.WIRE_TAGS`.
"""
from __future__ import annotations

import json
from pathlib import Path
import random
import subprocess

import pytest

from tests.subprocesses import HANG_TIMEOUT
from tests.probe_matrix import raw_environment
from ve import Environment, FiniteModel
from ve.errors import VEError
from ve.ast import (WIRE_TAGS, Add, And, Atom, Binary, Body, Bottom, Const, Eq, Exists,
                    Forall, Implies, Le, Lt, Named, Not, Num, Or, Reach, Scale, Top,
                    Unary, Var, formula_from_data, formula_to_data)
from ve.evaluate import _evaluate_validated
from tests import nonvacuity_oracle


ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / "lean/.lake/build/bin/ve_metered"
CHUNK = 2000
FULL = 1_000_000
needs_exe = pytest.mark.skipif(not EXE.exists(), reason="ve_metered has not been built")


def run(cases):
    rows = []
    for start in range(0, len(cases), CHUNK):
        answer = subprocess.run([str(EXE)], input=json.dumps(cases[start:start + CHUNK]),
                                text=True, capture_output=True, check=True, timeout=HANG_TIMEOUT)
        rows += json.loads(answer.stdout)
    assert len(rows) == len(cases)
    return rows


def public(row, kind):
    """The public part of a Lean row; an error is compared as an error."""
    if row.get("status") != "ok":
        return "error"
    if kind == "evaluate-budgeted":
        return row["evaluation"]
    return [row["suitable"], row["evaluations"], row["exhausted"]]


class Collector:
    """Cases for one `ve_metered` run, each with Python's answer."""

    def __init__(self):
        self.cases, self.expected = [], []

    def add(self, case, answer):
        case["id"] = str(len(self.cases))
        self.cases.append(case)
        self.expected.append(answer)

    def document(self, raw, wire, data, budgets_of, traces_of):
        """Evaluation and non-vacuity cases for one document, against Python.

        `data` is the document's wire AST; Python decodes it (an error is
        expected of Lean too) and its full charge picks the budgets."""
        try:
            env = Environment(raw)
            model = FiniteModel.from_dict(env, wire)
            formulas = tuple(formula_from_data(env, a) for a in data)
        except VEError:  # a Python rejection is an expected Lean error; anything else fails
            self.add({"kind": "evaluate-budgeted", "environment": raw, "model": wire,
                      "ast": data, "max_evaluations": FULL}, "error")
            return
        full = _evaluate_validated(formulas, model, max_evaluations=FULL).evaluations
        for budget in budgets_of(full):
            for trace, nodes in traces_of(budget):
                nodes = min(budget, nodes)
                self.add({"kind": "evaluate-budgeted", "environment": raw, "model": wire,
                          "ast": data, "max_evaluations": budget, "max_trace_nodes": nodes,
                          "trace": trace},
                         _evaluate_validated(formulas, model, max_evaluations=budget,
                                             max_trace_nodes=nodes, trace=trace).to_dict())
        for formula, item in zip(formulas, data):
            def oracle(budget, semantic):
                return nonvacuity_oracle.answer(raw, wire, item, budget, semantic,
                                                env=env, formula=formula, model=model)
            full = oracle(FULL, True)[1]
            for semantic in (False, True):
                for budget in budgets_of(full):
                    self.add({"kind": "non-vacuity", "environment": raw, "model": wire,
                              "formula": item, "max_evaluations": budget,
                              "semantic_nonvacuity": semantic},
                             oracle(budget, semantic))

    def mismatches(self):
        rows = run(self.cases)
        return [(case, public(row, case["kind"]), answer)
                for case, row, answer in zip(self.cases, rows, self.expected, strict=True)
                if public(row, case["kind"]) != answer]


def boundaries(full):
    return sorted({0, 1, full // 2, max(full - 1, 0), full, full + 1})


# --- the saved conformance corpora -----------------------------------------------------

def corpus(name):
    for case in json.loads((ROOT / "conformance" / f"{name}.json").read_text()):
        if name == "countermodels":
            yield case["environment"], case["model"], [*case["premises"], case["conclusion"]]
        else:
            yield case["environment"], case["model"], case["ast"]


@needs_exe
@pytest.mark.parametrize("name", ("evaluation", "countermodels", "closure"))
def test_conformance_corpora_with_their_frozen_envelopes_match_python(name):
    collector = Collector()
    for raw, wire, data in corpus(name):
        assert raw["language"] in ("ve.core@0", "ve.core@0.1")
        collector.document(raw, wire, data, boundaries,
                           lambda b: ((False, 10_000), (True, 10_000), (True, max(b - 1, 0))))
    assert "error" not in collector.expected
    bad = collector.mismatches()
    assert not bad, (len(bad), bad[:3])


# --- the seeded random differential ----------------------------------------------------

FAMILIES = ((), ("closure@0",), ("closure@0", "nary@0"), ("order@0",), ("definitions@0",),
            ("data@0",), ("norms@0",), ("closure@0", "definitions@0"),
            ("closure@0", "nary@0", "definitions@0"), ("closure@0", "nary@0", "data@0"))
ENTITIES = ("i", "j", "k")
SEEDS = (15, 1501, 150102)


def random_model(rng, env):
    domain = list(ENTITIES[:rng.randint(1, 3)])
    relations = {}
    for name, decl in env.predicates.items():
        if decl.defined is not None:
            continue
        rows = {tuple(rng.choice(domain) for _ in decl.arguments) for _ in range(rng.randint(0, 5))}
        if getattr(decl, "functional", False) and rng.random() < 0.7:
            rows = {row for row in rows if row[0] == domain[0]}
            rows = set(sorted(rows)[:1])
        relations[name] = [list(row) for row in sorted(rows)]
    constants = {name: rng.choice(domain) for name in env.constants}
    return {"complete": True, "domains": {"item": domain}, "constants": constants,
            "relations": relations}


class Formulas:
    """Random well-typed formulas over the probe-matrix vocabulary of one family."""

    def __init__(self, rng, env):
        self.rng, self.env, self.seen = rng, env, set()
        leaves = ["top", "bottom", "unary", "eq"]
        predicates = env.predicates
        if "step" in predicates:
            leaves += ["binary", "reach-named", "reach-body"]
        if "edge" in predicates:
            leaves.append("edge")
        if "triple" in predicates:
            leaves.append("atom")
        if "derived" in predicates:
            leaves.append("derived")
        if "permitted" in predicates:
            leaves.append("permitted")
        if env.order:
            leaves += ["lt", "le"]
        self.leaves = leaves

    def note(self, node):
        self.seen.add(type(node))
        return node

    def term(self, depth):
        if depth and self.rng.random() < 0.6:
            return self.note(Var(self.rng.randrange(depth)))
        return self.note(Const(self.rng.choice(sorted(self.env.constants))))

    def number(self):
        k = self.rng.randrange(4)
        if k == 0:
            return self.note(Add(self.number(), self.number()))
        if k == 1:
            return self.note(Scale(self.rng.choice((-1, 2)), self.number()))
        return self.note(Num(self.rng.randint(-1, 2)))

    def leaf(self, depth):
        kind, term = self.rng.choice(self.leaves), self.term
        node = {"top": lambda: Top(), "bottom": lambda: Bottom(),
                "unary": lambda: Unary("base", term(depth)),
                "derived": lambda: Unary("derived", term(depth)),
                "permitted": lambda: Unary("permitted", term(depth)),
                "eq": lambda: Eq(term(depth), term(depth)),
                "binary": lambda: Binary("step", term(depth), term(depth)),
                "edge": lambda: Binary("edge", term(depth), term(depth)),
                "reach-named": lambda: Reach(self.rng.choice(("plus", "star")),
                                             self.note(Named("step")), term(depth), term(depth)),
                "reach-body": lambda: Reach(self.rng.choice(("plus", "star")),
                                            self.note(Body("item", Binary("step", Var(1), Var(0)))),
                                            term(depth), term(depth)),
                "atom": lambda: Atom("triple", (term(depth), term(depth), term(depth))),
                "lt": lambda: Lt(self.number(), self.number()),
                "le": lambda: Le(self.number(), self.number())}[kind]()
        return self.note(node)

    def formula(self, depth, size):
        if size <= 0 or self.rng.random() < 0.2:
            return self.leaf(depth)
        kind = self.rng.choice(("not", "and", "or", "or", "implies", "implies", "all", "all", "ex"))
        if kind == "not":
            return self.note(Not(self.formula(depth, size - 1)))
        if kind in ("all", "ex"):
            return self.note((Forall if kind == "all" else Exists)("item",
                                                                   self.formula(depth + 1, size - 1)))
        left, right = self.formula(depth, size // 2), self.formula(depth, size // 2)
        return self.note({"and": And, "or": Or, "implies": Implies}[kind](left, right))


def random_documents(profiles, seed, documents=24):
    """The seeded documents of one family: (raw environment, [(model, formulas)], constructors seen)."""
    rng = random.Random(f"{seed}/{','.join(profiles)}")
    raw = raw_environment(profiles)
    env = Environment(raw)
    generator = Formulas(rng, env)
    rows = [(random_model(rng, env),
             [formula_to_data(env, generator.formula(0, rng.randint(1, 9)))
              for _ in range(rng.randint(1, 3))])
            for _ in range(documents)]
    return raw, rows, generator.seen


@needs_exe
@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("profiles", FAMILIES, ids=lambda p: "+".join(p) or "fol")
def test_seeded_random_differential_matches_python(profiles, seed):
    raw, rows, _ = random_documents(profiles, seed)
    rng = random.Random(seed)
    collector = Collector()
    for wire, data in rows:
        collector.document(raw, wire, data,
                           lambda full: sorted({0, rng.randint(0, full + 1), max(full - 1, 0), full,
                                                FULL}),
                           lambda b: ((rng.random() < 0.7, rng.choice((b, max(b - 1, 0), 10_000))),))
    bad = collector.mismatches()
    assert not bad, (len(bad), bad[:3])


def test_random_generator_covers_every_wire_constructor():
    """Checklist item 8: the differential's constructors are checked against the
    AST schema (`WIRE_TAGS`), every term kind and both reachability edges."""
    seen = set()
    for profiles in FAMILIES:
        for seed in SEEDS:
            seen |= random_documents(profiles, seed)[2]
    assert set(WIRE_TAGS) <= seen
    assert {Var, Const, Num, Add, Scale, Named, Body} <= seen


# --- regressions for the review's seeded mutants -----------------------------------------

def _single(profiles, wire, formulas, semantic_budgets=(0, 1, 3, 7, FULL)):
    raw = raw_environment(profiles)
    env = Environment(raw)
    collector = Collector()
    collector.document(raw, wire, [formula_to_data(env, f) for f in formulas],
                       lambda full: sorted({*semantic_budgets, max(full - 1, 0), full}),
                       lambda b: ((False, 10_000), (True, 10_000)))
    return collector


@needs_exe
def test_existential_under_no_universal_has_no_clause_guard():
    """Mutant `NonVacuity.lean:137`: an existential must not count as universal."""
    wire = {"complete": True, "domains": {"item": ["i", "j"]}, "constants": {"x": "i"},
            "relations": {"base": []}}
    collector = _single((), wire, [Exists("item", Or(Not(Unary("base", Var(0))), Bottom())),
                                   Exists("item", Or(Unary("base", Var(0)), Not(Top())))])
    bad = collector.mismatches()
    assert not bad, bad[:3]


@needs_exe
def test_nested_disjunction_is_one_clause():
    """Mutant `NonVacuity.lean:108`: a disjunction inside a clause adds no guard."""
    wire = {"complete": True, "domains": {"item": ["i", "j", "k"]}, "constants": {"x": "i"},
            "relations": {"base": [["i"]]}}
    clause = Or(Or(Not(Unary("base", Var(0))), Not(Eq(Var(0), Const("x")))), Bottom())
    collector = _single((), wire, [Forall("item", clause),
                                   Forall("item", Or(Not(Top()), Or(Not(Unary("base", Var(0))),
                                                                    Top())))])
    bad = collector.mismatches()
    assert not bad, bad[:3]


@needs_exe
@pytest.mark.parametrize("profiles", (("definitions@0",), ("closure@0", "nary@0", "definitions@0")))
def test_defined_tables_are_computed_on_every_family(profiles):
    """Mutant `MeteredRun.lean:38`: the layered core model keeps its defined tables."""
    nary = "nary@0" in profiles
    wire = {"complete": True, "domains": {"item": ["i", "j"]},
            "constants": {"x": "i", **({"y": "j"} if nary else {})},
            "relations": {"base": [["i"]], **({"step": [["i", "j"]], "triple": [["i", "j", "i"]]}
                                             if nary else {})}}
    collector = _single(profiles, wire, [Unary("derived", Const("x")),
                                         Forall("item", Implies(Unary("derived", Var(0)),
                                                                Unary("base", Var(0)))),
                                         Exists("item", Unary("derived", Var(0)))])
    assert "error" not in collector.expected
    bad = collector.mismatches()
    assert not bad, bad[:3]


# --- error parity: the metered route validates as the service does ---------------------

def _rejections():
    """(name, raw environment, model) pairs that Python rejects."""
    fol = raw_environment(())
    model = {"complete": True, "domains": {"item": ["i"]}, "constants": {"x": "i"},
             "relations": {"base": []}}
    defined = raw_environment(("definitions@0",))
    defined["profiles"] = ["relational-fol@0"]
    reserved = raw_environment(())
    reserved["vocabulary"]["sorts"]["no"] = {"description": "reserved"}
    data = raw_environment(("data@0",))
    legacy = json.loads((ROOT / "conformance/evaluation.json").read_text())[0]
    literal = json.loads(json.dumps(legacy["environment"]))
    literal["vocabulary"]["constants"]["quoted"] = {"sort": "$string"}
    revision = {**legacy["environment"], "spec_revision": "ve-v0.2-expand2-2026-09-25"}
    return (("defined-without-profile", defined, model),
            ("reserved-name", reserved, model),
            ("functional-violated", data, {**model, "relations": {"base": [], "edge": [["i", "i"], ["i", "j"]]},
                                           "domains": {"item": ["i", "j"]}}),
            ("unknown-entity", fol, {**model, "relations": {"base": [["z"]]}}),
            ("legacy-literal", literal, legacy["model"]),
            ("legacy-revision", revision, legacy["model"]))


@needs_exe
def test_rejected_environments_and_models_are_errors_as_in_python():
    collector = Collector()
    for _, raw, wire in _rejections():
        collector.document(raw, wire, [["top"]], boundaries, lambda b: ((True, 10_000),))
    assert collector.expected == ["error"] * len(_rejections())
    bad = collector.mismatches()
    assert not bad, bad[:3]
