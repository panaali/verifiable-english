"""Scope, inverse grammar, all-view consistency, and lexical adversaries."""
import json
from pathlib import Path
import random
import re

import pytest

from ve import (And, Binary, Bottom, Const, Document, Environment, Eq, Exists,
                Forall, Implies, Not, Or, Top, Unary, Var, parse, render, render_fol)
from ve.errors import VEError
from ve.printer import VIEWS
from explicit_inverse import parse_explicit
from fluent_inverse import Inverse, parse_fluent
from test_views import ENV, _random_formula, vocabulary


def negative_vocabulary():
    data = vocabulary()
    predicates = data["vocabulary"]["predicates"]
    predicates["reviewed"]["negative_verbalisation"] = "{0} is not reviewed"
    predicates["owns"]["negative_verbalisation"] = "{0} does not own {1}"
    predicates["links"]["negative_verbalisation"] = "{0} does not depend on {1}"
    return data


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
    "for every service S that is deployed, S is reviewed",
    "for every service S that is deployed, there is a person P such that P owns S",
    "there is a person P such that for every service S that is deployed, P owns S",
    "it is false that (there is a service S such that both S is deployed and (it is false that S is reviewed))",
    "for every service S that is deployed, it is false that S is reviewed",
    "it is false that (for every service S that is deployed, S is reviewed)",
    "for every service S that is deployed and that is not the same service as @legacy, S is reviewed",
    "for every person P and every service S, if P owns S then P audits S",
    "for every person P and every service S, if P owns S then S audits P",
    "for every service S and every person P and every person P2, if (both P owns S and P2 owns S) then P is the same person as P2",
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
        document_text = render(document, env, "ve_fluent")
        assert document_text.startswith(expected + ".\n")
        assert render_fol(env, document, view="ve_fluent") == document_text
        assert [parse_fluent(env, line[:-1]) for line in document_text.splitlines()] == [formula] * 2
        with pytest.raises(VEError):
            parse(env, expected + ".\n")  # Fluent is not accepted source syntax.
        for view in VIEWS:
            text = render(formula, env, view)
            restored = parse_fluent(env, text) if view == "ve_fluent" else parse_explicit(env, text, view)
            assert restored == formula


@pytest.mark.parametrize("env", [ENV, Environment(negative_vocabulary())])
def test_random_inverse_injectivity_and_pairwise_consistency_all_five_views(env):
    rng = random.Random(20260921)
    sample = {_random_formula(rng, rng.randrange(1, 7)) for _ in range(24000)}
    assert len(sample) >= 6000
    print(f"{len(sample)} distinct random ASTs; {len(sample) * len(VIEWS)} inverse checks across five views")
    seen = {view: {} for view in VIEWS}
    for formula in sample:
        decoded = []
        for view in VIEWS:
            text = render(formula, env, view)
            assert seen[view].setdefault(text, formula) == formula, (view, text)
            if view == "ve_fluent":
                inverse = Inverse(env, text)
                restored = inverse.parse()
                assert [(kind, sort) for kind, sort, _ in inverse.binders] == binder_order(formula)
            else:
                restored = parse_explicit(env, text, view)
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
    assert render(Exists("agent", Top()), ENV, "ve_fluent") == "there is a person such that true"
    assert render(Forall("item", Top()), ENV, "ve_fluent") == "for every service, true"
    f = Forall("item", And(Exists("item", Binary("links", Var(1), Var(0))),
                           Exists("item", Eq(Var(0), Var(1)))))
    text = render(f, ENV, "ve_fluent")
    assert "service S2" in text and "service S3" in text
    assert parse_fluent(ENV, text) == f
    data = vocabulary()
    data["vocabulary"]["sorts"]["agent"]["verbalisation"]["singular"] = "specialist"
    env = Environment(data)
    f = Forall("item", Exists("agent", Binary("owns", Var(0), Var(1))))
    assert render(f, env, "ve_fluent") == "for every service R, there is a specialist S such that S owns R"
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
            declaration["negative_verbalisation"] = rng.choice(templates + [
                "{0} is not unreviewed", "{0} is not reviewed", "{0} does not own {1}"])
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
    assert text == "for every service S, there is a person P such that P owns S"
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
    assert render(formulas[3], ENV, "ve_fluent") == "it is false that @alice owns @api"
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


@pytest.mark.parametrize("predicate,negative", [
    ("reviewed", "{0} is not unreviewed"),
    ("reviewed", "{0} is reviewed"),
    ("reviewed", "{0} is not deployed"),
    ("reviewed", "{0} is never reviewed"),
    ("reviewed", "{0} is not reviewed already"),
    ("reviewed", "{0} is not reviewed and true"),
    ("reviewed", "{0} is not S2"),
    ("owns", "{0} owns {1}"),
    ("owns", "{0} does not audit {1}"),
    ("owns", "{1} does not own {0}"),
    ("owns", "{0} does not own {0}"),
    ("owns", "{0.__class__} does not own {1}"),
    ("owns", "{0} does not own {1}."),
    ("owns", "{0} does  not own {1}"),
])
def test_attacker_negative_templates_rejected_with_explicit_fallback(predicate, negative):
    from ve import lint_vocabulary, render_vocabulary
    data = negative_vocabulary()
    data["vocabulary"]["predicates"][predicate]["negative_verbalisation"] = negative
    env = Environment(data)
    atom = (Unary(predicate, Const("api")) if predicate == "reviewed"
            else Binary(predicate, Const("alice"), Const("api")))
    text = render(Not(atom), env, "ve_fluent")
    assert text == "it is false that " + render(atom, env, "ve_fluent")
    assert parse_fluent(env, text) == Not(atom)
    path = f"/vocabulary/predicates/{predicate}/negative_verbalisation"
    assert (path, "NEGATIVE_NOT_NEGATION") in {(i.path, i.code) for i in lint_vocabulary(env)}
    legend = json.loads(render_vocabulary(env))
    entry = next(p for p in legend["predicates"] if p["identifier"] == predicate)
    assert entry["negative_verbalisation"] == negative
    assert entry["rendered_negative_template"] is None


def test_exact_negatives_guards_and_double_negation_preserve_scope():
    from ve import lint_vocabulary, render_vocabulary
    env = Environment(negative_vocabulary())
    assert not lint_vocabulary(env)
    formulas = [
        (Not(Unary("reviewed", Const("api"))), "@api is not reviewed"),
        (Not(Binary("owns", Const("alice"), Const("api"))), "@alice does not own @api"),
        (Forall("item", Implies(Not(Unary("reviewed", Var(0))), Top())),
         "for every service S that is not reviewed, true"),
        (Forall("agent", Implies(Not(Binary("owns", Var(0), Const("api"))), Top())),
         "for every person P that does not own @api, true"),
        (Not(Not(Unary("reviewed", Const("api")))), "it is false that @api is not reviewed"),
        (Forall("item", Implies(And(Not(Unary("reviewed", Var(0))),
                                   Not(Binary("links", Var(0), Const("api")))), Bottom())),
         "for every service S that is not reviewed and that does not depend on @api, false"),
    ]
    for formula, expected in formulas:
        assert render(formula, env, "ve_fluent") == expected
        assert parse_fluent(env, expected) == formula
    assert len({render_vocabulary(env, view) for view in VIEWS}) == 1


@pytest.mark.parametrize("finite,base", [
    ("audits", "audit"), ("depends", "depend"), ("has", "have"), ("likes", "like"),
    ("links", "link"), ("owns", "own"), ("reviews", "review"), ("trusts", "trust"),
])
def test_every_whitelisted_negative_inflection(finite, base):
    from ve import lint_vocabulary
    data = vocabulary()
    data["vocabulary"]["predicates"] = {"relation": {
        "arguments": ["agent", "item"], "description": "Relation",
        "verbalisation": f"{{0}} {finite} {{1}}",
        "negative_verbalisation": f"{{0}} does not {base} {{1}}",
    }}
    env = Environment(data)
    assert not lint_vocabulary(env)
    formula = Not(Binary("relation", Const("alice"), Const("api")))
    text = render(formula, env, "ve_fluent")
    assert text == f"@alice does not {base} @api"
    assert parse_fluent(env, text) == formula


@pytest.mark.parametrize("positive,code", [
    (None, "NEGATIVE_WITHOUT_POSITIVE"),
    ("{0} is not reviewed", "NEGATIVE_WITHOUT_POSITIVE"),
    ("{0} is reviewed already", "NEGATIVE_WITHOUT_POSITIVE"),
    ("{0} foos {1}", "NEGATIVE_NOT_NEGATION"),
])
def test_negative_requires_accepted_positive_and_whitelisted_inflection(positive, code):
    from ve import lint_vocabulary
    data = negative_vocabulary()
    predicate = "owns" if positive == "{0} foos {1}" else "reviewed"
    entry = data["vocabulary"]["predicates"][predicate]
    if positive is None:
        entry.pop("verbalisation")
    else:
        entry["verbalisation"] = positive
    if predicate == "owns":
        entry["negative_verbalisation"] = "{0} does not admire {1}"
    env = Environment(data)
    assert any(i.code == code for i in lint_vocabulary(env))
    atom = (Unary(predicate, Const("api")) if predicate == "reviewed"
            else Binary(predicate, Const("alice"), Const("api")))
    assert render(Not(atom), env, "ve_fluent").startswith("it is false that ")


def test_negative_metadata_is_immutable_identity_bound_and_optional():
    data = negative_vocabulary()
    env = Environment(data)
    assert env.to_dict() == data
    assert Environment.from_json(json.dumps(data)).environment_id == env.environment_id
    assert ENV.environment_id != env.environment_id
    data["vocabulary"]["predicates"]["reviewed"]["negative_verbalisation"] = "{0} is reviewed"
    assert env.predicates["reviewed"].negative_verbalisation == "{0} is not reviewed"
    assert Environment(data).environment_id != env.environment_id
    assert "negative_verbalisation" not in ENV.to_dict()["vocabulary"]["predicates"]["reviewed"]


@pytest.mark.parametrize("bad", [None, {}, [], 1, "", "x" * 257])
def test_negative_metadata_type_and_length_checked(bad):
    data = negative_vocabulary()
    data["vocabulary"]["predicates"]["owns"]["negative_verbalisation"] = bad
    with pytest.raises(VEError):
        Environment(data)


@pytest.mark.parametrize("naming", ["per_statement", "per_document"])
def test_variable_letters_disjoint_across_sorts_scopes_statements_and_legend(naming):
    from ve import render_vocabulary
    data = vocabulary()
    data["vocabulary"]["sorts"]["agent"]["verbalisation"]["singular"] = "specialist"
    data["vocabulary"]["sorts"]["system"] = {"description": "Third S sort"}
    data["vocabulary"]["constants"]["s"] = {"sort": "item", "description": "Lowercase S"}
    data["vocabulary"]["constants"]["s2"] = {"sort": "item", "description": "Lowercase S2"}
    data["vocabulary"]["predicates"]["active"]["verbalisation"] = "{0} is S2"
    env = Environment(data)
    f = Forall("item", Exists("agent", Binary("owns", Var(0), Var(1))))
    g = Forall("system", Eq(Var(0), Var(0)))
    h = Forall("item", And(Eq(Var(0), Const("s")), Unary("active", Const("s2"))))
    document = Document((f, f, g, h))
    text = render(document, env, "ve_fluent", naming)
    first = "for every service R, there is a specialist P such that P owns R."
    second = (first if naming == "per_statement" else
              "for every service R2, there is a specialist P2 such that P2 owns R2.")
    assert text.splitlines()[:3] == [first, second,
        "for every system Y, Y is the same system as Y."]
    assert "@s" in text and "@s2" in text and "@s2 is active" in text
    from collections import Counter
    counts = Counter()
    letters = json.loads(render_vocabulary(env, naming=naming))["fluent_variables"]["letters_by_sort"]
    assert letters == {"agent": "P", "item": "R", "system": "Y"}
    for formula, line in zip(document.formulas, text.splitlines(), strict=True):
        if naming == "per_statement":
            counts.clear()
        inverse = Inverse(env, line[:-1])
        assert inverse.parse() == formula
        for _, sort, name in inverse.binders:
            counts[sort] += 1
            assert name == letters[sort] + (str(counts[sort]) if counts[sort] > 1 else "")
    for category in data["vocabulary"]:
        data["vocabulary"][category] = dict(reversed(list(data["vocabulary"][category].items())))
    reordered = Environment(data)
    assert render(document, reordered, "ve_fluent", naming) == text
    assert render_vocabulary(reordered, naming=naming) == render_vocabulary(env, naming=naming)
    assert render(f, env, "ve_fluent", naming) == first[:-1]


@pytest.mark.parametrize("naming", ["per_statement", "per_document"])
def test_all_sort_initial_collisions_have_disjoint_names(naming):
    from ve import render_vocabulary
    data = vocabulary()
    data["vocabulary"] = {"sorts": {f"sort{i}": {"description": "Sort"} for i in range(32)},
                          "predicates": {}, "constants": {}}
    env = Environment(data)
    statements = tuple(Forall(sort, Eq(Var(0), Var(0))) for sort in sorted(env.sorts)) * 2
    text = render(Document(statements), env, "ve_fluent", naming)
    names = re.findall(r"for every sort\d+ ([A-Z]+[0-9]*)", text)
    letters = json.loads(render_vocabulary(env, naming=naming))["fluent_variables"]["letters_by_sort"]
    assert len(set(letters.values())) == 32
    assert names[:32] == list(letters.values())
    assert names[32:] == [name + ("2" if naming == "per_document" else "") for name in names[:32]]
    assert all(not set(name).intersection("AIO") for name in names)
    assert [parse_fluent(env, line[:-1]) for line in text.splitlines()] == list(statements)


def test_committed_six_example_document_roundtrips_in_all_five_views():
    from ve import measure_view_lengths, render_vocabulary
    directory = Path(__file__).resolve().parents[1] / "examples/fluent"
    env = Environment.from_json((directory / "environment.json").read_bytes())
    document = parse(env, (directory / "examples.ve").read_bytes())
    assert len(document.formulas) == 6
    assert len({render_vocabulary(env, view) for view in VIEWS}) == 1
    rows = measure_view_lengths([document], env, include_vocabulary=True)
    assert len(rows) == 5
    for row in rows:
        view = row["view"]
        text = render(document, env, view)
        assert row["characters"] == len(render_vocabulary(env, view) + text)
        assert [parse_fluent(env, line[:-1]) if view == "ve_fluent"
                else parse_explicit(env, line[:-1], view)
                for line in text.splitlines()] == list(document.formulas)


def print_examples():
    """Reproduce the report's ten rows / fifty outputs."""
    for i, (env, formula) in enumerate(table_examples(), 1):
        print(f"{i}.")
        for view in VIEWS:
            print(f"{view}: {render(formula, env, view)}.")


if __name__ == "__main__":
    print_examples()
