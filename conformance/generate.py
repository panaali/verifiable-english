"""Regenerate portable evaluator fixtures. Run from the repository root.

Cases mirror the examples and Python semantic tests, plus seeded mixed-sort
formulas. Python supplies golden values; Lean agreement is a differential test,
not independent evidence that the Python decoder implements every wire rule.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve import Environment, FiniteModel, evaluate, parse, print_document
from ve.ast import (
    And, Binary, Bottom, Const, Document, Eq, Exists, Forall, Implies, Not,
    Or, Top, Unary, Var, document_to_data,
)


def build_cases():
    cases = []

    def add(name, env, model, formulas):
        doc = formulas if isinstance(formulas, Document) else Document(tuple(formulas))
        cases.append({
            "id": name, "environment": env.to_dict(), "model": model.to_dict(),
            "ast": document_to_data(env, doc), "source": print_document(env, doc),
            "expected": [evaluate(env, a, model).value for a in doc.formulas],
        })

    env = Environment.from_json((ROOT / "examples/environment.json").read_bytes())
    model = FiniteModel.from_json(env, (ROOT / "examples/model.json").read_bytes())
    for name in ("requirements", "premise", "conclusion"):
        add(f"example_{name}", env, model, parse(env, (ROOT / f"examples/{name}.ve").read_bytes()))
    for kind in ("empty", "unreviewed", "unowned"):
        data = model.to_dict()
        if kind == "empty":
            data["domains"] = {s: [] for s in env.sorts}
            data["relations"] = {p: [] for p in env.predicates}
        else:
            data["relations"]["reviewed" if kind == "unreviewed" else "owns"] = []
        add(f"example_requirements_{kind}", env, FiniteModel.from_dict(env, data),
            parse(env, (ROOT / "examples/requirements.ve").read_bytes()))

    base = {
        "language": "ve.core@0", "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20",
        "vocabulary": {
            "sorts": {"item": {"description": "An item."}},
            "predicates": {
                "marked": {"arguments": ["item"], "description": "Marked."},
                "edge": {"arguments": ["item", "item"], "description": "An edge."},
            }, "constants": {},
        },
    }
    env = Environment.from_dict(base)
    for size in range(3):
        domain = ["a", "b"][:size]
        for mask in range(1 << size):
            model = FiniteModel.from_dict(env, {
                "complete": True, "domains": {"item": domain}, "constants": {},
                "relations": {"marked": [[x] for i, x in enumerate(domain) if mask >> i & 1],
                              "edge": [[a, b] for a in domain for b in domain if a != b]},
            })
            add(f"quantifiers_size{size}_mask{mask}", env, model, [
                Top(), Bottom(), Forall("item", Unary("marked", Var(0))),
                Exists("item", Unary("marked", Var(0))),
                Forall("item", Bottom()), Exists("item", Top()),
                Exists("item", Forall("item", Bottom())),
                Implies(Exists("item", Top()), Bottom()),
                Exists("item", Exists("item", Binary("edge", Var(1), Var(0)))),
                Forall("item", Eq(Var(0), Var(0))),
                Exists("item", Exists("item", Not(Eq(Var(0), Var(1))))),
                And(Top(), Bottom()), Or(Bottom(), Top()), Not(Top()),
            ])

    base["vocabulary"]["constants"] = {
        "origin": {"sort": "item", "description": "Origin."},
        "other": {"sort": "item", "description": "Another named item."},
    }
    env = Environment.from_dict(base)
    for alias in (True, False):
        for reverse in (True, False):
            model = FiniteModel.from_dict(env, {
                "complete": True, "domains": {"item": ["a", "b"]},
                "constants": {"origin": "a", "other": "a" if alias else "b"},
                "relations": {"marked": [["a"]], "edge": [["b", "a"]] if reverse else [["a", "b"]]},
            })
            add(f"constants_alias{alias}_reverse{reverse}", env, model, [
                Eq(Const("origin"), Const("other")),
                Unary("marked", Const("origin")), Unary("marked", Const("other")),
                Binary("edge", Const("origin"), Const("other")),
                Exists("item", Binary("edge", Const("origin"), Var(0))),
                Forall("item", Implies(Unary("marked", Var(0)), Eq(Var(0), Const("origin")))),
            ])

    # Mixed sorts share local IDs but the entities remain sort-qualified.
    mixed = copy.deepcopy(base)
    mixed["vocabulary"]["sorts"]["person"] = {"description": "A person."}
    mixed["vocabulary"]["predicates"]["owns"] = {"arguments": ["person", "item"], "description": "Owns."}
    mixed["vocabulary"]["predicates"]["active"] = {"arguments": ["person"], "description": "Active."}
    mixed["vocabulary"]["constants"]["alice"] = {"sort": "person", "description": "Named person."}
    env = Environment.from_dict(mixed)
    rng = random.Random(20260921)

    def formula(depth, context):
        def term(sort):
            terms = [Const(c) for c, d in env.constants.items() if d.sort == sort]
            terms += [Var(i) for i, s in enumerate(context) if s == sort]
            return rng.choice(terms)

        def atom():
            kind = rng.randrange(5)
            if kind < 2:
                return Top() if kind == 0 else Bottom()
            if kind == 2:
                sort = rng.choice(list(env.sorts))
                return Eq(term(sort), term(sort))
            name = rng.choice(list(env.predicates))
            args = env.predicates[name].arguments
            return Unary(name, term(args[0])) if len(args) == 1 else Binary(name, term(args[0]), term(args[1]))

        kind = rng.randrange(8) if depth else 0
        if kind < 2:
            return atom()
        if kind == 2:
            return Not(formula(depth - 1, context))
        if kind < 6:
            return (And, Or, Implies)[kind - 3](formula(depth - 1, context), formula(depth - 1, context))
        sort = rng.choice(list(env.sorts))
        return (Forall if kind == 6 else Exists)(sort, formula(depth - 1, (sort,) + context))

    for i in range(160):
        domains = {s: ["same", "second"][:rng.randint(1, 2)] for s in env.sorts}
        constants = {c: rng.choice(domains[d.sort]) for c, d in env.constants.items()}
        relations = {}
        for p, d in env.predicates.items():
            rows = [[x] for x in domains[d.arguments[0]]] if len(d.arguments) == 1 else [
                [x, y] for x in domains[d.arguments[0]] for y in domains[d.arguments[1]]]
            relations[p] = [r for r in rows if rng.choice((True, False))]
        model = FiniteModel.from_dict(env, {"complete": True, "domains": domains,
                                         "constants": constants, "relations": relations})
        add(f"seeded_mixed_{i:03}", env, model, [formula(4, ()) for _ in range(4)])
    return cases


if __name__ == "__main__":
    result = build_cases()
    (ROOT / "conformance/evaluation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"Wrote {len(result)} cases / {sum(len(c['ast']) for c in result)} formulas")

    from conformance.extend import parser_cases, identity_cases, wire_cases, validation_cases, search_cases
    for name, cases in (("parser", parser_cases(result)), ("identity", identity_cases(result)), ("wire", wire_cases()), ("validation", validation_cases(result)), ("search", search_cases())):
        (ROOT / f"conformance/{name}.json").write_text(json.dumps(cases, indent=2, ensure_ascii=False) + "\n")
        print(f"Wrote {len(cases)} {name} cases")
