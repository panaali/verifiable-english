"""Empirical injectivity, controlled vocabulary, and adversarial scope cases."""
from copy import deepcopy
import random
import re

import pytest

from ve import (And, Binary, Bottom, Const, Document, Environment, Eq, Exists,
                FiniteModel, Forall, Implies, Not, Or, Top, Unary, Var, evaluate,
                parse, render, render_fol)
from ve.errors import ResourceLimit, VEError
from ve.printer import VIEWS, natural_document, natural_formula, print_document


def vocabulary():
    return {
        "language": "ve.core@0", "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20",
        "vocabulary": {
            "sorts": {
                "item": {"description": "Item", "verbalisation": {"singular": "service", "plural": "services"}},
                "agent": {"description": "Agent", "verbalisation": {"singular": "person", "plural": "people"}},
            },
            "predicates": {
                "active": {"arguments": ["item"], "description": "Deployed", "verbalisation": "{0} is deployed"},
                "reviewed": {"arguments": ["item"], "description": "Reviewed", "verbalisation": "{0} is reviewed"},
                "exempt": {"arguments": ["item"], "description": "Exempt", "verbalisation": "{0} is exempt"},
                "owns": {"arguments": ["agent", "item"], "description": "Owner", "verbalisation": "{0} owns {1}"},
                "links": {"arguments": ["item", "item"], "description": "Link", "verbalisation": "{0} depends on {1}"},
                "ready": {"arguments": ["agent"], "description": "Ready", "verbalisation": "{0} is ready"},
            },
            "constants": {"api": {"sort": "item", "description": "API"},
                          "alice": {"sort": "agent", "description": "Alice"}},
        },
    }


ENV = Environment(vocabulary())


def test_four_views_exact_example_and_legacy_entry_points():
    formula = Forall("item", Implies(Unary("active", Var(0)),
                                    Exists("agent", Binary("owns", Var(0), Var(1)))))
    texts = {
        "fol_symbols": "∀ x0:item, ((active(x0)) → (∃ x1:agent, (owns(x1, x0))))",
        "fol_keywords": "forall x0:item, ((active(x0)) implies (exists x1:agent, (owns(x1, x0))))",
        "ve_strict": "for every item x0, (if (x0 is active), then (there exists agent x1, (x1 owns x0)))",
        "ve_explicit": "for every service x0: (if (x0 is deployed), then (there is a person x1 such that (x1 owns x0)))",
    }
    for view, expected in texts.items():
        assert render(formula, ENV, view) == expected
        doc_text = expected
        assert render(Document((formula,)), ENV, view) == doc_text + ".\n"
        assert render_fol(ENV, Document((formula,)), view=view) == doc_text + ".\n"
    assert natural_formula(ENV, formula).text == "Every deployed service has an owner"
    document = Document((formula, formula))
    assert render(document, ENV, "ve_strict") == print_document(ENV, document)
    assert natural_document(ENV, document).text.count("Every deployed service has an owner") == 2
    assert "x2" not in natural_document(ENV, document).text
    with pytest.raises(ValueError):
        render(formula, ENV, "informal")


def _random_formula(rng, depth, scope=()):
    def term(sort):
        choices = [Const("api" if sort == "item" else "alice")]
        choices += [Var(i) for i, s in enumerate(scope) if s == sort]
        return rng.choice(choices)

    choice = rng.randrange(11 if depth else 5)
    if choice == 0: return Top()
    if choice == 1: return Bottom()
    if choice == 2:
        predicate = rng.choice(tuple(ENV.predicates))
        signature = ENV.predicates[predicate].arguments
        args = [term(s) for s in signature]
        return Unary(predicate, *args) if len(args) == 1 else Binary(predicate, *args)
    if choice == 3:
        sort = rng.choice(tuple(ENV.sorts))
        return Eq(term(sort), term(sort))
    if choice == 4: return Unary(rng.choice(("active", "reviewed", "exempt")), term("item"))
    if choice == 5: return Not(_random_formula(rng, depth - 1, scope))
    if choice in (6, 7, 8):
        return (And, Or, Implies)[choice - 6](_random_formula(rng, depth - 1, scope),
                                             _random_formula(rng, depth - 1, scope))
    sort = rng.choice(tuple(ENV.sorts))
    return (Forall if choice == 9 else Exists)(sort, _random_formula(rng, depth - 1, (sort, *scope)))


def _grouping(text, view):
    # FOL's atomic p(t,u) delimiters are argument lists, not formula scope.
    if view.startswith("fol_"):
        text = re.sub(r"\b[a-z][a-z0-9_]*\([^()]*\)", "ATOM", text)
    return "".join(c for c in text if c in "()")


def test_large_random_sample_all_views_injective_names_and_grouping_identical():
    rng = random.Random(20260921)
    # The fifth view deliberately has different names and grouping. Its inverse
    # and all-five consistency checks are in test_fluent.py.
    seen = {view: {} for view in VIEWS if view != "ve_fluent"}
    sample = set()
    for _ in range(24000):
        sample.add(_random_formula(rng, rng.randrange(1, 7)))
    assert len(sample) >= 6000
    for formula in sample:
        names, grouping = None, None
        for view in seen:
            text = render(formula, ENV, view)
            assert seen[view].setdefault(text, formula) == formula, (view, text)
            current_names = re.findall(r"\bx[0-9]+\b", text)
            current_grouping = _grouping(text, view)
            if names is None:
                names, grouping = current_names, current_grouping
            assert current_names == names  # declarations AND references, including sibling scopes
            assert current_grouping == grouping
        assert parse(ENV, render(Document((formula,)), ENV, "ve_strict")) == Document((formula,))


def test_adversarial_pairs_differ_in_text_and_in_a_checked_model():
    p, q, exception = (Unary(name, Const("api")) for name in ("active", "reviewed", "exempt"))
    px, qx = Unary("active", Var(0)), Unary("reviewed", Var(0))
    pairs = [
        # Quantifier dependency, argument reversal, and negation scope.
        (Forall("item", Exists("item", Binary("links", Var(1), Var(0)))),
         Exists("item", Forall("item", Binary("links", Var(1), Var(0))))),
        (Exists("item", Binary("links", Const("api"), Var(0))),
         Exists("item", Binary("links", Var(0), Const("api")))),
        (Not(Exists("item", px)), Exists("item", Not(px))),
        (Forall("item", Implies(px, qx)), Implies(Forall("item", px), Forall("item", qx))),
        (And(p, q), Or(p, q)),
        (Implies(p, q), Implies(q, p)),
        (And(p, q), p),
        (Implies(And(p, Not(exception)), q), Implies(p, q)),
        (And(Exists("item", px), Forall("item", Implies(px, qx))),
         Forall("item", Implies(px, qx))),
    ]
    # Exhaust this tiny, deliberately rich family of structures independently of
    # search, so these are semantically distinct pairs, not just different ASTs.
    witnesses = [False] * len(pairs)
    for active in ([], [["a"]], [["a"], ["b"]]):
        for reviewed in ([], [["b"]], [["a"], ["b"]]):
            for exempt in ([], [["a"]]):
                for links in ([], [["a", "a"], ["b", "b"]], [["a", "b"]]):
                    model = FiniteModel.from_dict(ENV, {
                        "complete": True, "domains": {"item": ["a", "b"], "agent": ["p"]},
                        "constants": {"api": "a", "alice": "p"},
                        "relations": {"active": active, "reviewed": reviewed, "exempt": exempt,
                                      "links": links, "owns": [], "ready": []}})
                    for i, (left, right) in enumerate(pairs):
                        witnesses[i] |= evaluate(ENV, left, model).value != evaluate(ENV, right, model).value
    assert all(witnesses)
    for left, right in pairs:
        assert render(left, ENV, "ve_explicit") != render(right, ENV, "ve_explicit")
    exception_text = render(pairs[7][0], ENV, "ve_explicit")
    assert "it is not the case that (@api is exempt)" in exception_text
    assert "then (@api is reviewed)" in exception_text


@pytest.mark.parametrize("template", [
    "{0} is deployed and reviewed", "{0} is not deployed", "{0} is deployed unless exempt",
    "{0} is deployed.", "{0.__class__}", "{1} is deployed", "{0} is deployed {0}",
    "is deployed", "{0} is x0", "{0} is deployed\n", "{0} is {1}",
    "{0} is", "{0} banana", "{0} runs quickly",
])
def test_unsafe_or_inexpressible_template_falls_back_to_strict_atom(template):
    data = vocabulary()
    data["vocabulary"]["predicates"]["active"]["verbalisation"] = template
    env = Environment(data)
    assert render(Unary("active", Const("api")), env, "ve_explicit") == "@api is active"


def test_collision_fallback_including_other_symbols_strict_forms():
    data = vocabulary()
    data["vocabulary"]["predicates"]["active"]["verbalisation"] = "{0} is reviewed"
    env = Environment(data)
    assert render(Unary("active", Const("api")), env, "ve_explicit") == "@api is active"
    assert render(Unary("reviewed", Const("api")), env, "ve_explicit") == "@api is reviewed"
    data["vocabulary"]["sorts"]["item"]["verbalisation"]["singular"] = "agent"
    env = Environment(data)
    assert render(Exists("item", Top()), env, "ve_explicit").startswith("there is an item x0")
    data["vocabulary"]["sorts"]["item"]["verbalisation"]["singular"] = "person"
    env = Environment(data)
    assert "item x0" in render(Forall("item", Top()), env, "ve_explicit")
    assert "agent x0" in render(Forall("agent", Top()), env, "ve_explicit")


def test_verbalisation_roundtrip_identity_and_defensive_copy():
    data = vocabulary()
    original = deepcopy(data)
    env = Environment(data)
    assert env.to_dict() == original
    assert Environment.from_dict(env.to_dict()).environment_id == env.environment_id
    data["vocabulary"]["sorts"]["item"]["verbalisation"]["singular"] = "changed"
    assert env.to_dict() == original
    changed = Environment(data)
    assert changed.environment_id != env.environment_id
    for sort in data["vocabulary"]["sorts"].values():
        sort.pop("verbalisation")
    for predicate in data["vocabulary"]["predicates"].values():
        predicate.pop("verbalisation")
    assert Environment(data).to_dict() == data  # old wire shape and IDs unchanged


@pytest.mark.parametrize("bad", [42, "", {"template": "{0} is ready"}])
def test_malformed_verbalisation_rejected(bad):
    data = vocabulary()
    data["vocabulary"]["predicates"]["active"]["verbalisation"] = bad
    with pytest.raises(VEError):
        Environment(data)


def test_verbalisation_size_is_bounded():
    data = vocabulary()
    data["vocabulary"]["predicates"]["active"]["verbalisation"] = "x" * 257
    with pytest.raises(ResourceLimit):
        Environment(data)


def test_injectivity_across_template_collisions_and_sort_aliases():
    rng = random.Random(109)
    for _ in range(80):
        data = vocabulary()
        for predicate in data["vocabulary"]["predicates"].values():
            predicate["verbalisation"] = rng.choice([
                "{0} is active", "{0} is reviewed", "{0} is blue", "{0} is ready",
                "{0} is", "{0} owns {1}", "{0} links {1}", "{0} trusts {1}",
                "{0} is equal to {1}", "{1} owns {0}"])
        for sort in data["vocabulary"]["sorts"].values():
            sort["verbalisation"]["singular"] = rng.choice(["item", "agent", "thing", "person", "some item"])
        env = Environment(data)
        atoms = [Top(), Bottom(), Eq(Const("api"), Const("api"))]
        for name, predicate in env.predicates.items():
            terms = [Const("api" if sort == "item" else "alice") for sort in predicate.arguments]
            atoms.append(Unary(name, *terms) if len(terms) == 1 else Binary(name, *terms))
        formulas = atoms + [cls(sort, body) for cls in (Forall, Exists)
                            for sort in env.sorts for body in atoms]
        assert len({render(f, env, "ve_explicit") for f in formulas}) == len(formulas)


def review_vocabulary():
    """The review's deployed/reviewed/owns/audits vocabulary and typed constants."""
    data = vocabulary()
    data['vocabulary'] = {
        'sorts': {'service': {'description': 'Service'}, 'person': {'description': 'Person'}},
        'predicates': {
            'deployed': {'arguments': ['service'], 'description': 'Deployed'},
            'reviewed': {'arguments': ['service'], 'description': 'Reviewed'},
            'owns': {'arguments': ['person', 'service'], 'description': 'Ownership'},
            'audits': {'arguments': ['person', 'service'], 'description': 'Auditing'},
        },
        'constants': {'api': {'sort': 'service', 'description': 'API'},
                      'alice': {'sort': 'person', 'description': 'Alice'}},
    }
    return data


@pytest.mark.parametrize('predicate,template,code', [
    # All newly accepted-template reproductions in review-views.md.
    ('owns', '{0} is owned by {1}', 'BINARY_AUXILIARY'),
    ('owns', '{0} belongs to {1}', 'BINARY_CONVERSE'),
    ('owns', '{0} lacks {1}', 'LOGICAL_WORD'),
    ('owns', '{0} audits carefully {1}', 'SYMBOL_COLLISION'),
    ('deployed', '{0} is undeployed', 'NEGATED_HEAD'),
    ('deployed', '{0} is reviewed already', 'UNARY_MODIFIER'),
    # Already rejected cases must stay rejected and now produce diagnostics.
    ('owns', '{1} owns {0}', 'TEMPLATE_SHAPE'),
    ('owns', '{0} owns', 'TEMPLATE_SHAPE'),
    ('owns', '{0} owns {0} {1}', 'PHRASE_SYNTAX'),
    ('owns', '{0} (owns) {1}', 'PHRASE_SYNTAX'),
    ('owns', '{0} owns\n{1}', 'TEMPLATE_SHAPE'),
    ('owns', '{0} Owns {1}', 'PHRASE_SYNTAX'),
    ('owns', '{0} owns  things {1}', 'PHRASE_SYNTAX'),
    ('owns', '{0:10} owns {1}', 'TEMPLATE_SHAPE'),
    ('deployed', '{0.__class__}', 'TEMPLATE_SHAPE'),
    ('owns', '{0} owns and audits {1}', 'LOGICAL_WORD'),
    ('owns', '{0} is {1}', 'BINARY_AUXILIARY'),
    ('deployed', '{0} is reviewed', 'SYMBOL_COLLISION'),
    ('deployed', '{0} is  ', 'PHRASE_SYNTAX'),
])
def test_review_template_reproductions_fall_back_and_lint(predicate, template, code):
    from ve import lint_vocabulary
    data = review_vocabulary()
    data['vocabulary']['predicates'][predicate]['verbalisation'] = template
    env = Environment(data)
    formula = (Unary(predicate, Const('api')) if predicate == 'deployed'
               else Binary(predicate, Const('alice'), Const('api')))
    assert render(formula, env, 've_explicit') == render(formula, env, 've_strict')
    assert render(formula, env, 've_fluent') == render(formula, env, 've_strict')
    path = f'/vocabulary/predicates/{predicate}/verbalisation'
    assert (path, code) in {(issue.path, issue.code) for issue in lint_vocabulary(env)}


@pytest.mark.parametrize('word', 'is are was were be been being gets got'.split())
def test_all_binary_auxiliaries_rejected(word):
    from ve import lint_vocabulary
    data = review_vocabulary()
    data['vocabulary']['predicates']['owns']['verbalisation'] = f'{{0}} {word} owning {{1}}'
    env = Environment(data)
    assert any(i.code == 'BINARY_AUXILIARY' for i in lint_vocabulary(env))
    assert render(Binary('owns', Const('alice'), Const('api')), env, 've_explicit') == '@alice owns @api'


@pytest.mark.parametrize('word', 'by to of from with for'.split())
def test_all_binary_converse_endings_rejected(word):
    from ve import lint_vocabulary
    data = review_vocabulary()
    data['vocabulary']['predicates']['owns']['verbalisation'] = f'{{0}} belongs {word} {{1}}'
    assert any(i.code == 'BINARY_CONVERSE' for i in lint_vocabulary(Environment(data)))


@pytest.mark.parametrize('word', [
    'not', 'no', 'never', 'lacks', 'without', 'every', 'all', 'some', 'any', 'each',
    'and', 'or', 'if', 'then', 'unless', 'only', 'x', 'x0', 'x12', 'X', 'A',
    'api', 'person', 'audits', 'unreviewed', 'nonreviewed', 'un-reviewed', 'non-reviewed',
])
def test_forbidden_words_checked_in_templates_and_both_sort_nouns(word):
    from ve import lint_vocabulary
    for field in ('predicate', 'singular', 'plural'):
        data = review_vocabulary()
        if field == 'predicate':
            data['vocabulary']['predicates']['owns']['verbalisation'] = f'{{0}} owns {word} {{1}}'
            path = '/vocabulary/predicates/owns/verbalisation'
        else:
            noun = {'singular': 'service', 'plural': 'services'}
            noun[field] = 'service ' + word
            data['vocabulary']['sorts']['service']['verbalisation'] = noun
            path = '/vocabulary/sorts/service/verbalisation/' + field
        env = Environment(data)
        assert any(i.path == path for i in lint_vocabulary(env)), (word, field)
        formula = (Binary('owns', Const('alice'), Const('api')) if field == 'predicate'
                   else Forall('service', Top()))
        expected = '@alice owns @api' if field == 'predicate' else 'for every service x0: (true)'
        assert render(formula, env, 've_explicit') == expected


@pytest.mark.parametrize('noun', ['x', 'service x', 'x1', 'X'])
def test_review_variable_sort_nouns_rejected(noun):
    from ve import lint_vocabulary
    data = review_vocabulary()
    data['vocabulary']['sorts']['service']['verbalisation'] = {'singular': noun, 'plural': 'services'}
    env = Environment(data)
    assert render(Forall('service', Top()), env, 've_explicit') == 'for every service x0: (true)'
    assert any(i.code == 'VARIABLE_TOKEN' for i in lint_vocabulary(env))


def test_template_head_and_identifier_collisions_across_all_categories():
    from ve import lint_vocabulary
    data = review_vocabulary()
    data['vocabulary']['predicates']['audits']['verbalisation'] = '{0} inspects {1}'
    data['vocabulary']['predicates']['owns']['verbalisation'] = '{0} inspects carefully {1}'
    data['vocabulary']['sorts']['service']['verbalisation'] = {'singular': 'inspects', 'plural': 'services'}
    env = Environment(data)
    assert render(Binary('owns', Const('alice'), Const('api')), env, 've_explicit') == '@alice owns @api'
    assert render(Forall('service', Top()), env, 've_explicit') == 'for every service x0: (true)'
    assert len([i for i in lint_vocabulary(env) if i.code == 'SYMBOL_COLLISION']) >= 2
    # Exact duplicate templates are explicitly diagnosed for both declarations.
    data['vocabulary']['predicates']['owns']['verbalisation'] = '{0} inspects {1}'
    assert len([i for i in lint_vocabulary(Environment(data)) if i.code == 'DUPLICATE_TEMPLATE']) == 2


@pytest.mark.parametrize('sort,noun', [('service', 'owner'), ('person', 'asset')])
def test_review_sort_aliases_remain_visible_and_declared_collisions_reject(sort, noun):
    import json
    from ve import lint_vocabulary, render_vocabulary
    data = review_vocabulary()
    data['vocabulary']['sorts'][sort]['verbalisation'] = {'singular': noun, 'plural': noun + 's'}
    env = Environment(data)
    # Arbitrary aliases are trusted data: no lexical heuristic can prove that
    # "asset" truthfully describes person. Every judge must see the same mapping.
    legends = {render_vocabulary(env, view) for view in VIEWS}
    assert len(legends) == 1
    entry = next(s for s in json.loads(legends.pop())['sorts'] if s['identifier'] == sort)
    assert entry['verbalisation']['singular'] == entry['rendered_noun'] == noun
    # If the name belongs to another declared sort, it is rejected outright.
    data['vocabulary']['sorts'][noun] = {'description': noun}
    env = Environment(data)
    assert render(Forall(sort, Top()), env, 've_explicit') == f'for every {sort} x0: (true)'
    assert any(i.code == 'SORT_COLLISION' for i in lint_vocabulary(env))
    # The same check covers another sort's noun even when its identifier differs.
    data['vocabulary']['sorts'].pop(noun)
    data['vocabulary']['sorts']['other'] = {
        'description': 'Other', 'verbalisation': {'singular': noun, 'plural': noun + 's'}}
    assert any(i.code == 'SORT_COLLISION' for i in lint_vocabulary(Environment(data)))


def test_legend_identical_deterministic_complete_and_lint_order_stable():
    import json
    from ve import lint_vocabulary, render_vocabulary
    data = review_vocabulary()
    data['vocabulary']['predicates']['owns']['verbalisation'] = '{0} is owned by {1}'
    env = Environment(data)
    text = render_vocabulary(env, 've_explicit')
    assert all(render_vocabulary(env, view) == text for view in VIEWS)
    legend = json.loads(text)
    owns = next(p for p in legend['predicates'] if p['identifier'] == 'owns')
    assert owns == {'identifier': 'owns', 'arguments': ['person', 'service'],
                    'description': 'Ownership', 'verbalisation': '{0} is owned by {1}',
                    'rendered_template': '{0} owns {1}', 'negative_verbalisation': None,
                    'rendered_negative_template': None}
    assert {c['identifier'] for c in legend['constants']} == {'alice', 'api'}
    for category in data['vocabulary']:
        data['vocabulary'][category] = dict(reversed(list(data['vocabulary'][category].items())))
    reversed_env = Environment(data)
    assert render_vocabulary(reversed_env) == text
    assert lint_vocabulary(env) == lint_vocabulary(reversed_env)
    assert legend['lint'] == [i.to_dict() for i in lint_vocabulary(env)]
    with pytest.raises(ValueError):
        render_vocabulary(env, 'unknown')


def test_same_real_output_limit_in_all_views():
    data = review_vocabulary()
    name, constant = 'p' * 64, 'c' * 64
    data['vocabulary']['predicates'] = {name: {'arguments': ['service'], 'description': 'P'}}
    data['vocabulary']['constants'] = {constant: {'sort': 'service', 'description': 'C'}}
    env = Environment(data)
    small = Document((Unary(name, Const(constant)),) * 400)
    large = Document((Unary(name, Const(constant)),) * 600)
    for view in VIEWS:
        assert len(render(small, env, view).encode()) < 65536
        with pytest.raises(ResourceLimit, match='65536-byte'):
            render(large, env, view)


def test_per_item_view_length_covariates_measure_actual_text_and_optional_legend():
    from ve import measure_view_lengths, render_vocabulary
    items = [Top(), Document((Top(), Bottom()))]
    rows = measure_view_lengths(iter(items), ENV)
    assert len(rows) == len(items) * len(VIEWS) == 10
    for row in rows:
        text = render(items[row['item_index']], ENV, row['view'])
        assert row['characters'] == len(text)
        assert row['tokenish'] == len(re.findall(r'\w+|[^\w\s]', text))
        assert row['includes_vocabulary'] is False
    assert rows[0]['characters'] == rows[0]['tokenish'] == 1  # Unicode symbol, not UTF-8 bytes
    assert rows[1]['characters'] == 4 and rows[1]['tokenish'] == 1
    with_legend = measure_view_lengths(items, ENV, include_vocabulary=True)
    for row, full in zip(rows, with_legend, strict=True):
        assert full['characters'] - row['characters'] == len(render_vocabulary(ENV))
        assert full['includes_vocabulary'] is True
    assert measure_view_lengths([], ENV) == []
