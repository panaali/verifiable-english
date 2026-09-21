"""Scope, inverse grammar, all-view consistency, and lexical adversaries."""
import random

import pytest

from ve import (And, Binary, Bottom, Const, Document, Environment, Eq, Exists,
                Forall, Implies, Not, Or, Top, Unary, Var, parse, render, render_fol)
from ve.errors import VEError
from ve.printer import VIEWS
from explicit_inverse import parse_explicit
from fluent_inverse import Inverse, parse_fluent
from test_views import ENV, _random_formula, vocabulary


def table_examples():
    data = vocabulary()
    predicates = data["vocabulary"]["predicates"]
    predicates["audits"] = {"arguments": ["agent", "item"], "description": "Audits",
                             "verbalisation": "{0} audits {1}"}
    data["vocabulary"]["constants"]["legacy"] = {"sort": "item", "description": "Legacy service"}
    env = Environment(data)
    p, q = Unary("active", Var(0)), Unary("reviewed", Var(0))
    rows = [
        Forall("item", Implies(p, q)),
        Forall("item", Implies(p, Exists("agent", Binary("owns", Var(0), Var(1))))),
        Exists("agent", Forall("item", Implies(p, Binary("owns", Var(1), Var(0))))),
        Not(Exists("item", And(p, Not(q)))),
        Forall("item", Implies(p, Not(q))),
        Not(Forall("item", Implies(p, q))),
        Forall("item", Implies(And(p, Not(Eq(Var(0), Const("legacy")))), q)),
        Forall("agent", Forall("item", Implies(Binary("owns", Var(1), Var(0)), Binary("audits", Var(1), Var(0))))),
        Forall("agent", Forall("item", Implies(Binary("owns", Var(1), Var(0)), Binary("audits", Var(0), Var(1))))),
        Forall("item", Forall("agent", Forall("agent", Implies(
            And(Binary("owns", Var(1), Var(2)), Binary("owns", Var(0), Var(2))), Eq(Var(1), Var(0)))))),
    ]
    # Rows 8/9 cannot share one many-sorted audits signature. Keep the reversal
    # visible, with a separately typed environment for the ninth table row.
    predicates["audits"]["arguments"] = ["item", "agent"]
    reverse_env = Environment(data)
    return [(reverse_env if i == 8 else env, row) for i, row in enumerate(rows)]


EXPECTED = [
    "For every service S that is deployed, S is reviewed",
    "For every service S that is deployed, there is a person P such that P owns S",
    "There is a person P such that for every service S that is deployed, P owns S",
    "It is false that (there is a service S such that both S is deployed and (it is false that S is reviewed))",
    "For every service S that is deployed, it is false that S is reviewed",
    "It is false that (for every service S that is deployed, S is reviewed)",
    "For every service S that is deployed and that is not the same service as @legacy, S is reviewed",
    "For every person P and every service S, if P owns S then P audits S",
    "For every person P and every service S, if P owns S then S audits P",
    "For every service S and every person P and every person P2, if (both P owns S and P2 owns S) then P is the same person as P2",
]


def binder_order(value):
    if type(value) in (Forall, Exists):
        return [(type(value), value.sort)] + binder_order(value.body)
    if type(value) is Not:
        return binder_order(value.body)
    if type(value) in (And, Or, Implies):
        return binder_order(value.left) + binder_order(value.right)
    return []


def test_table_exact_all_five_views_and_read_only_entry_point():
    for (env, formula), expected in zip(table_examples(), EXPECTED, strict=True):
        assert render(formula, env, "ve_fluent") == expected
        document = Document((formula, formula))
        assert render(document, env, "ve_fluent") == (expected + ".\n") * 2
        assert render_fol(env, document, view="ve_fluent") == (expected + ".\n") * 2
        with pytest.raises(VEError):
            parse(env, expected + ".\n")  # Fluent is not accepted source syntax.
        for view in VIEWS:
            text = render(formula, env, view)
            restored = parse_fluent(env, text) if view == "ve_fluent" else parse_explicit(env, text, view)
            assert restored == formula


def test_random_inverse_injectivity_and_pairwise_consistency_all_five_views():
    rng = random.Random(20260921)
    sample = {_random_formula(rng, rng.randrange(1, 7)) for _ in range(24000)}
    assert len(sample) >= 6000
    print(f"{len(sample)} distinct random ASTs; {len(sample) * len(VIEWS)} inverse checks across five views")
    seen = {view: {} for view in VIEWS}
    for formula in sample:
        decoded = []
        for view in VIEWS:
            text = render(formula, ENV, view)
            assert seen[view].setdefault(text, formula) == formula, (view, text)
            if view == "ve_fluent":
                inverse = Inverse(ENV, text)
                restored = inverse.parse()
                assert [(kind, sort) for kind, sort, _ in inverse.binders] == binder_order(formula)
            else:
                restored = parse_explicit(ENV, text, view)
            assert restored == formula, (view, text)
            decoded.append(restored)
        assert all(a == b for a in decoded for b in decoded)


def minimal_pairs():
    p, q, r = (Unary(name, Const("api")) for name in ("active", "reviewed", "exempt"))
    px, qx = Unary("active", Var(0)), Unary("reviewed", Var(0))
    return [
        (Forall("item", Exists("item", Binary("links", Var(1), Var(0)))),
         Exists("item", Forall("item", Binary("links", Var(1), Var(0))))),
        (Exists("item", Binary("links", Const("api"), Var(0))), Exists("item", Binary("links", Var(0), Const("api")))),
        (Not(Exists("item", px)), Exists("item", Not(px))),
        (Forall("item", Implies(px, qx)), Implies(Forall("item", px), Forall("item", qx))),
        (And(p, q), Or(p, q)), (Implies(p, q), Implies(q, p)), (And(p, q), p),
        (And(Not(p), q), Not(And(p, q))),
        (Implies(And(p, Not(r)), q), Implies(p, q)),
        (And(Exists("item", px), Forall("item", Implies(px, qx))), Forall("item", Implies(px, qx))),
        (And(p, Or(q, r)), Or(And(p, q), r)),
        (And(And(p, q), r), And(p, And(q, r))),
        (Or(Or(p, q), r), Or(p, Or(q, r))),
        (Implies(Implies(p, q), r), Implies(p, Implies(q, r))),
        (Forall("item", Implies(And(px, qx), px)), Forall("item", Implies(px, px))),
        (Forall("item", Implies(px, qx)), Forall("item", And(px, qx))),
        (Forall("item", Implies(px, qx)), Forall("item", Implies(Not(px), qx))),
        (Exists("item", Top()), Top()), (Forall("item", Top()), Top()),
        (Exists("item", Eq(Var(0), Const("api"))), Exists("item", Eq(Const("api"), Var(0)))),
        (Forall("item", Forall("item", Binary("links", Var(1), Var(0)))),
         Forall("item", Forall("item", Binary("links", Var(0), Var(1))))),
    ]


@pytest.mark.parametrize("left,right", minimal_pairs())
def test_all_minimal_pairs_preserve_ast_in_every_view(left, right):
    for view in VIEWS:
        texts = [render(f, ENV, view) for f in (left, right)]
        assert texts[0] != texts[1]
        for f, text in zip((left, right), texts):
            assert (parse_fluent(ENV, text) if view == "ve_fluent" else parse_explicit(ENV, text, view)) == f


def test_names_vacuity_collisions_sibling_scopes_and_shadowing():
    assert render(Exists("agent", Top()), ENV, "ve_fluent") == "There is a person such that true"
    assert render(Forall("item", Top()), ENV, "ve_fluent") == "For every service, true"
    f = Forall("item", And(Exists("item", Binary("links", Var(1), Var(0))),
                           Exists("item", Eq(Var(0), Var(1)))))
    text = render(f, ENV, "ve_fluent")
    assert "service S2" in text and "service S3" in text
    assert parse_fluent(ENV, text) == f
    data = vocabulary()
    data["vocabulary"]["sorts"]["agent"]["verbalisation"]["singular"] = "specialist"
    env = Environment(data)
    f = Forall("item", Exists("agent", Binary("owns", Var(0), Var(1))))
    assert render(f, env, "ve_fluent") == "For every service S, there is a specialist S2 such that S2 owns S"
    assert parse_fluent(env, render(f, env, "ve_fluent")) == f


def test_lexical_adversaries_fallback_and_inverse():
    rng = random.Random(109)
    templates = ["{0} is active", "{0} is reviewed", "{0} is blue", "{0} is ready",
                 "{0} is", "{0} owns {1}", "{0} links {1}", "{0} trusts {1}",
                 "{0} is owned by {1}", "{0} is equal to {1}", "{1} owns {0}",
                 "{0} is not reviewed", "{0} does not own {1}", "{0} is false that", "{0.__class__}"]
    for _ in range(80):
        data = vocabulary()
        for declaration in data["vocabulary"]["predicates"].values():
            declaration["verbalisation"] = rng.choice(templates)
        for declaration in data["vocabulary"]["sorts"].values():
            declaration["verbalisation"]["singular"] = rng.choice(["item", "agent", "thing", "person", "some item"])
        env = Environment(data)
        sample = {_random_formula(rng, 4) for _ in range(80)}
        seen = {}
        for formula in sample:
            text = render(formula, env, "ve_fluent")
            assert seen.setdefault(text, formula) == formula
            assert "is owned by" not in text
            assert parse_fluent(env, text) == formula


@pytest.mark.parametrize("template", ["{0} is owned by {1}", "{0} was owned by {1}",
                                     "{0} gets owned through {1}", "{0} is owned via {1}"])
def test_passive_relational_templates_use_active_formal_fallback(template):
    data = vocabulary()
    data["vocabulary"]["predicates"]["owns"]["verbalisation"] = template
    env = Environment(data)
    formula = Forall("item", Exists("agent", Binary("owns", Var(0), Var(1))))
    text = render(formula, env, "ve_fluent")
    assert text == "For every service S, there is a person P such that P owns S"
    assert parse_fluent(env, text) == formula


def test_general_guards_negation_and_total_structural_fallback():
    formulas = [
        Forall("item", Implies(Binary("owns", Const("alice"), Var(0)), Top())),
        Forall("item", Implies(And(Unary("active", Var(0)), And(Unary("reviewed", Var(0)), Eq(Var(0), Const("api")))), Bottom())),
        Forall("item", Implies(Not(Unary("active", Var(0))), Top())),
        Not(Binary("owns", Const("alice"), Const("api"))),
        Not(Eq(Const("alice"), Const("alice"))),
    ]
    for formula in formulas:
        assert parse_fluent(ENV, render(formula, ENV, "ve_fluent")) == formula
    assert "such that @alice owns S" in render(formulas[0], ENV, "ve_fluent")
    assert render(formulas[3], ENV, "ve_fluent") == "It is false that @alice owns @api"
    assert render(formulas[4], ENV, "ve_fluent") == "@alice is not the same person as @alice"
    # All constructors at the accepted maximum depth, including unused binders.
    constructors = [lambda f: Forall("item", f), lambda f: Exists("agent", f), Not,
                    lambda f: And(Top(), f), lambda f: Or(f, Bottom()), lambda f: Implies(f, Top())]
    for start in (Top(), Unary("active", Const("api")), Eq(Const("api"), Const("api"))):
        for constructor in constructors:
            formula = start
            for _ in range(63):
                formula = constructor(formula)
            assert parse_fluent(ENV, render(formula, ENV, "ve_fluent")) == formula


def print_examples():
    """Reproduce the report's ten rows / fifty outputs."""
    for i, (env, formula) in enumerate(table_examples(), 1):
        print(f"{i}.")
        for view in VIEWS:
            print(f"{view}: {render(formula, env, view)}.")


if __name__ == "__main__":
    print_examples()
