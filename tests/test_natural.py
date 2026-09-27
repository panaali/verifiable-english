"""The natural view only accepts exact, uniquely parsed English sentences."""

import json
import random
import re
import pytest
from lark import Lark
from pathlib import Path

from ve import (And, Binary, Const, Document, Environment, Exists, Forall,
                Implies, Not, Or, Unary, Var, check_argument,
                parse_english_argument, render)
from ve.english import english_lark_grammar, parse_english, _normalise_english_source, EnglishVocabulary
from ve.surface.unambiguity import require_unique_derivation
from ve.ast import Body, Le, Lt, Num, Reach, Scale
from ve.natural import (_NOTATION, natural_coverage, render_natural_sentence,
                        parse_presentation, render_presentation, migrate_presentation,
                        PresentationNeedsRepair)
from ve.errors import ResourceLimit
from ve.printer import natural_document
from test_views import ENV, vocabulary


def _names(env, **forms):
    return {'vocabulary': {'format': 've.english-vocabulary@1',
                           'environment_id': env.environment_id,
                           'sorts': {}, 'predicates': {},
                           'constants': {name: {'verbalisation': form}
                                         for name, form in forms.items()}}}


def test_natural_core_forms_are_writable_and_unique():
    deployed = Unary('active', Var(0))
    owner = Exists('agent', Binary('owns', Var(0), Var(1)))
    cases = [
        (Exists('item', deployed), 'Some service is deployed'),
        (Not(Exists('item', deployed)), 'No service is deployed'),
        (Forall('item', Implies(deployed, owner)), 'Every deployed service has an owner'),
        (Forall('item', Implies(deployed, Unary('reviewed', Var(0)))),
         'Every deployed service is reviewed'),
        (Forall('item', Implies(deployed, And(Unary('reviewed', Var(0)), owner))),
         'Every deployed service is reviewed and has an owner'),
    ]
    earley = Lark(english_lark_grammar(ENV), parser='earley', lexer='dynamic_complete', ambiguity='explicit')
    for formula, expected in cases:
        result = render_natural_sentence(formula, ENV)
        assert result.natural and result.text == expected and result.reason is None
        assert parse_english(ENV, expected + '.') == Document((formula,))
        assert not list(earley.parse(expected.lower() + '.').find_data('_ambig'))
        assert render(formula, ENV, 've_natural') == expected


def test_prose_paragraph_and_declared_constant_display_forms():
    data = vocabulary()
    data['vocabulary']['constants']['union'] = {
        'sort': 'item', 'description': 'European Union'}
    env = Environment(data)
    options = _names(env, api='the API', alice='Alice', union='the European Union')
    formulas = (Unary('reviewed', Const('api')),
                Unary('ready', Const('alice')),
                Unary('reviewed', Const('union')))
    document = Document(formulas)
    text = natural_document(env, document, **options).text
    assert text == 'The API is reviewed. Alice is ready. The European Union is reviewed.'
    assert render(document, env, 've_natural', **options) == text
    assert parse_english(env, text, **options) == document
    assert len(natural_document(env, document, **options).sentences) == 3


def test_web_app_first_example_is_one_checked_prose_argument():
    example = Path(__file__).resolve().parents[1] / 'examples/assist'
    env = Environment.from_json((example / 'environment.json').read_bytes())
    options = {'vocabulary': json.loads((example / 'environment.english.json').read_text())}
    document = Document((
        Forall('service', Implies(Unary('reviewed', Var(0)), Unary('safe', Var(0)))),
        Unary('reviewed', Const('api')),
        Unary('safe', Const('api'))))
    expected = ('Every reviewed service is safe. The API is reviewed. '
                'Therefore the API is safe.')
    for marker in ('Therefore', 'So', 'Hence', 'It follows that'):
        text = expected.replace('Therefore', marker)
        assert parse_english(env, text, **options) == document
        view = natural_document(env, document, conclusions=(2,), conclusion_marker=marker, **options)
        assert view.text == text
        assert view.sentences[2]['role'] == 'conclusion'
        assert render(document, env, 've_natural', conclusions=(2,),
                      conclusion_marker=marker, **options) == text
        graph = parse_english_argument(env, text, **options)
        assert graph.deductions[0].premises == ('s1', 's2')
        checked = check_argument(graph, search=False)
        assert checked.findings['d3'] == ('follows',)
        assert checked.remaining_assumptions == ('s1', 's2')
    separated = natural_document(env, document, conclusions=(2,), paragraph_breaks=(2,), **options)
    assert separated.text == expected.replace(' Therefore', '\n\nTherefore')
    assert separated.paragraphs == ({'start': 0, 'end': 2}, {'start': 2, 'end': 3})
    assert parse_english(env, separated.text, **options) == document
    repeated = Document((*document.formulas, document.formulas[-1]))
    repeated_view = natural_document(env, repeated, conclusions=(2, 3), **options)
    repeated_graph = parse_english_argument(env, repeated_view.text, **options)
    assert tuple(edge.premises for edge in repeated_graph.deductions) == (
        ('s1', 's2'), ('s1', 's2'))
    repeated_prose = parse_presentation(env, repeated_view.text, **options)
    assert repeated_prose.sentences[2]['dependencies'] == (0, 1)
    assert repeated_prose.sentences[3]['dependencies'] == (0, 1)
    with pytest.raises(Exception, match='no checked derivation'):
        parse_english(env, 'The API is reviewed. Therefore the API is safe.', **options)
    with pytest.raises(Exception, match='earlier premise'):
        parse_english(env, 'Therefore the API is safe. The API is reviewed.', **options)


def test_versioned_prose_roundtrip_preserves_words_roles_spans_and_dependencies():
    example = Path(__file__).resolve().parents[1] / 'examples/assist'
    env = Environment.from_json((example / 'environment.json').read_bytes())
    options = {'vocabulary': json.loads((example / 'environment.english.json').read_text())}
    source = ('Every reviewed service is safe. The API is reviewed.\n\n'
              'Hence the API is safe.')
    parsed = parse_presentation(env, source, **options)
    assert parsed.text == source
    assert parsed.version == 've.prose@1'
    assert parsed.paragraphs == ({'start': 0, 'end': 2}, {'start': 2, 'end': 3})
    assert [s['role'] for s in parsed.sentences] == ['premise', 'premise', 'conclusion']
    assert parsed.sentences[2]['dependencies'] == (0, 1)
    for sentence in parsed.sentences:
        assert source[sentence['start']:sentence['end']] == sentence['text']
    rendered = render_presentation(env, parsed.document, conclusions=(2,),
                                   paragraph_breaks=(2,), **options)
    assert rendered.document == parsed.document
    assert rendered.sentences[2]['dependencies'] == (0, 1)
    preview = migrate_presentation(env, source, **options)
    assert preview['meaning_unchanged'] and preview['presentation_approval_required']
    assert preview['previous'].text == source
    assert preview['proposed'].text.startswith('Every reviewed service is safe.')
    with pytest.raises(ValueError):
        parse_presentation(env, source, version='ve.prose@2', **options)


def test_it_requires_one_preceding_constant_referent():
    env = Environment(vocabulary())
    options = _names(env, api='the API', alice='Alice')
    one = Document((Unary('reviewed', Const('api')), Unary('active', Const('api'))))
    assert natural_document(env, one, **options).text == 'The API is reviewed. It is deployed.'
    assert parse_english(env, 'The API is reviewed. It is deployed.', **options) == one
    with pytest.raises(Exception):
        parse_english(env, 'It is deployed.', **options)
    many = Document((Unary('reviewed', Const('api')),
                     Unary('ready', Const('alice')),
                     Unary('active', Const('api'))))
    assert 'It is deployed' not in natural_document(env, many, **options).text
    with pytest.raises(Exception):
        parse_english(env, 'The API is reviewed. Alice is ready. It is deployed.', **options)


def test_existential_antecedent_blocks_unconfirmed_it_even_with_one_constant():
    env = Environment(vocabulary())
    options = _names(env, api='the API')
    source = 'The API is reviewed. Some service is deployed. It is reviewed.'
    with pytest.raises(Exception, match='referent of it is incomplete'):
        parse_english(env, source, **options)
    document = Document((Unary('reviewed', Const('api')),
                         Exists('item', Unary('active', Var(0))),
                         Unary('reviewed', Const('api'))))
    view = natural_document(env, document, **options)
    assert view.text.endswith('The API is reviewed.')
    assert parse_english(env, view.text, **options) == document


def test_it_cannot_skip_referents_inside_the_current_sentence():
    data = vocabulary()
    data['vocabulary']['constants']['beta'] = {'sort': 'item', 'description': 'Beta'}
    env = Environment(data)
    for source in (
        'Api is reviewed. If beta is reviewed, then it is deployed.',
        'Api is reviewed. If some service is deployed, then it is reviewed.',
    ):
        with pytest.raises(Exception):
            parse_english(env, source)
        with pytest.raises(Exception):
            parse_presentation(env, source)
    # An explicit name still makes the intended claim writable.
    assert parse_english(env, 'Api is reviewed. If beta is reviewed, then api is deployed.')


def test_it_is_only_available_at_its_own_sentence_initial_position():
    data = vocabulary()
    data['vocabulary']['constants']['beta'] = {'sort': 'item', 'description': 'Beta'}
    env = Environment(data)
    for source in ('Api is reviewed. Beta depends on it.',
                   'Api is reviewed. Api depends on it.',
                   'Api is reviewed. Beta is the same as it.'):
        with pytest.raises(Exception):
            parse_english(env, source)
        with pytest.raises(Exception):
            parse_presentation(env, source)
    initial = 'Api is reviewed. It depends on beta.'
    expected = Document((Unary('reviewed', Const('api')),
                         Binary('links', Const('api'), Const('beta'))))
    assert parse_english(env, initial) == expected
    assert parse_presentation(env, initial).document == expected


def test_lowercase_alias_and_conclusion_initials_roundtrip():
    env = Environment(vocabulary())
    options = _names(env, api='api')
    premise = Unary('reviewed', Const('api'))
    document = Document((premise, premise))
    assert parse_english(env, 'Api is reviewed.', **options) == Document((premise,))
    assert render(document, env, 've_english', **options) == 'Api is reviewed.\nApi is reviewed.\n'
    assert natural_document(env, document, **options).text == 'Api is reviewed. It is reviewed.'
    for selected in ({}, options):
        text = 'Api is reviewed. Therefore api is reviewed.'
        parsed = parse_presentation(env, text, **selected)
        view = natural_document(env, parsed.document, conclusions=(1,), **selected)
        assert view.text.endswith('Therefore Api is reviewed.')
        assert parse_presentation(env, view.text, **selected).sentences[1]['role'] == 'conclusion'
        assert render_presentation(env, parsed.document, conclusions=(1,), **selected).document == document
        english = render(document, env, 've_english', conclusions=(1,), **selected)
        assert english.endswith('Therefore api is reviewed.\n')


@pytest.mark.parametrize('alias', ('The API', 'The Api', 'The api'))
@pytest.mark.parametrize('marker', ('Therefore', 'So', 'Hence', 'It follows that'))
def test_capitalized_article_alias_keeps_exact_case_in_conclusions(alias, marker):
    env = Environment(vocabulary())
    options = _names(env, api=alias)
    premise = Unary('reviewed', Const('api'))
    document = Document((premise, premise))
    source = f'{alias} is reviewed. {marker} {alias} is reviewed.'
    parsed = parse_presentation(env, source, **options)
    assert parsed.document == document
    assert [sentence['role'] for sentence in parsed.sentences] == ['premise', 'conclusion']
    view = natural_document(env, document, conclusions=(1,),
                            conclusion_marker=marker, **options)
    assert view.text == source
    assert render(document, env, 've_natural', conclusions=(1,),
                  conclusion_marker=marker, **options) == source
    assert render_presentation(env, document, conclusions=(1,),
                               conclusion_marker=marker, **options).document == document
    migration = migrate_presentation(env, source, **options)
    assert migration['proposed'].document == document
    assert migration['meaning_unchanged']


def test_declared_names_keep_case_with_extra_whitespace():
    env = Environment(vocabulary())
    upper = _names(env, api='The API')
    formula = Unary('reviewed', Const('api'))
    source = 'The  API is reviewed. Therefore  The\tAPI is reviewed.'
    expected = Document((formula, formula))
    assert parse_english(env, source, **upper) == expected
    presented = parse_presentation(env, source, **upper)
    assert presented.document == expected
    assert [s['role'] for s in presented.sentences] == ['premise', 'conclusion']

    lower = _names(env, api='api')
    source = 'Api is reviewed. Therefore  Api is reviewed.'
    assert parse_english(env, source, **lower) == expected
    assert parse_presentation(env, source, **lower).document == expected

    from conformance.english_surface import order_environment
    order = order_environment()
    order_options = _names(order, budget='Annual Budget')
    comparison = Le(Num(3), Const('budget'))
    assert parse_presentation(order, 'Annual  Budget is at least 3.',
                              **order_options).document == Document((comparison,))


def test_list_alias_conclusion_marker_and_doubling_accept_editable_whitespace():
    env = Environment(vocabulary())
    options = _names(env, api='The API')
    list_formula = And(Unary('reviewed', Const('api')),
                       And(Unary('active', Const('api')), Unary('exempt', Const('api'))))
    list_source = 'The  API is reviewed, deployed and exempt.'
    assert parse_english(env, list_source, **options) == Document((list_formula,))
    assert parse_presentation(env, list_source, **options).document == Document((list_formula,))
    require_unique_derivation(env, list_source, **options)

    premise = Unary('reviewed', Const('api'))
    conclusion_source = 'The API is reviewed. It  follows\tthat The API is reviewed.'
    presented = parse_presentation(env, conclusion_source, **options)
    assert presented.document == Document((premise, premise))
    assert [row['role'] for row in presented.sentences] == ['premise', 'conclusion']
    assert parse_english(env, conclusion_source, **options) == presented.document
    require_unique_derivation(env, conclusion_source, **options)

    from conformance.english_surface import order_environment
    order = order_environment()
    doubled = Lt(Scale(2, Const('budget')), Const('limit'))
    doubled_source = 'Limit is more than twice  the\tbudget.'
    assert parse_english(order, doubled_source) == Document((doubled,))
    assert parse_presentation(order, doubled_source).document == Document((doubled,))
    require_unique_derivation(order, doubled_source)


def test_accepted_corpus_whitespace_perturbations_share_one_reading():
    data = vocabulary()
    for name in ('beta', 'gamma'):
        data['vocabulary']['constants'][name] = {'sort': 'item', 'description': name}
    env = Environment(data)
    options = _names(env, api='The API', beta='Beta', gamma='Gamma')
    from conformance.english_surface import order_environment
    order = order_environment()
    corpus = [
        (env, options, 'The API is reviewed.'),
        (env, options, 'The API is reviewed, deployed and exempt.'),
        (env, options, 'The API, Beta and Gamma are reviewed.'),
        (env, options, 'The API is reviewed. It follows that The API is reviewed.'),
        (env, options, 'Some service is deployed.'),
        (env, options, 'Every deployed service is reviewed.'),
        (env, options, 'For every service, that service is reviewed.'),
        (order, {}, 'Limit is more than twice the budget.'),
    ]
    rng = random.Random(20260927)
    for selected_env, selected_options, source in corpus:
        expected = parse_english(selected_env, source, **selected_options)
        for _ in range(3):
            changed = re.sub(r' +', lambda _match: rng.choice(('  ', '\t', '\n', ' \t ')), source)
            assert parse_english(selected_env, changed, **selected_options) == expected
            assert parse_presentation(selected_env, changed, **selected_options).document == expected
            require_unique_derivation(selected_env, changed, **selected_options)


def test_normalisation_preserves_quoted_identifier_and_source_offsets():
    env = Environment(vocabulary())
    words = EnglishVocabulary(env, **_names(env, api='The API'))
    source = 'The  API is reviewed.\n\n"a.  B" is reviewed.'
    normalised, boundaries = _normalise_english_source(source, words)
    assert normalised == 'The API is reviewed. "a.  B" is reviewed.'
    assert source[boundaries[normalised.index('"')]:].startswith('"a.  B"')


def test_plural_and_possessive_references_require_explicit_repair():
    env = Environment(vocabulary())
    options = _names(env, api='the API', alice='Alice')
    for sentence in ('They are reviewed.', 'Her manager is ready.',
                     'Their service is deployed.'):
        with pytest.raises(Exception, match='explicit-name or scoped-referent'):
            parse_english(env, 'Alice is ready. ' + sentence, **options)


def test_three_item_subject_and_predicate_lists_have_exact_ast():
    data = vocabulary()
    data['vocabulary']['constants']['beta'] = {
        'sort': 'item', 'description': 'Beta'}
    data['vocabulary']['constants']['gamma'] = {
        'sort': 'item', 'description': 'Gamma'}
    env = Environment(data)
    options = _names(env, api='the API', beta='Beta', gamma='Gamma')
    for cls, connective, verb in ((And, 'and', 'are'), (Or, 'or', 'is')):
        atoms = [Unary('reviewed', Const(n)) for n in ('api', 'beta', 'gamma')]
        subjects = cls(atoms[0], cls(atoms[1], atoms[2]))
        text = f'The API, Beta {connective} Gamma {verb} reviewed'
        assert render_natural_sentence(subjects, env, **options).text == text
        assert parse_english(env, text + '.', **options) == Document((subjects,))
        atoms = [Unary(p, Const('api')) for p in ('reviewed', 'active', 'exempt')]
        predicates = cls(atoms[0], cls(atoms[1], atoms[2]))
        text = f'The API is reviewed, deployed {connective} exempt'
        assert render_natural_sentence(predicates, env, **options).text == text
        assert parse_english(env, text + '.', **options) == Document((predicates,))


def test_relative_who_and_that_bind_the_local_quantifier():
    formula = Forall('agent', Implies(Unary('ready', Var(0)),
                                      Unary('ready', Var(0))))
    for pronoun in ('who', 'that'):
        assert parse_english(ENV, f'Every person {pronoun} is ready is ready.') == Document((formula,))


def test_colliding_declared_names_use_exact_identifiers():
    env = Environment(vocabulary())
    options = _names(env, api='Alice', alice='Alice')
    first = render_natural_sentence(Unary('reviewed', Const('api')), env, **options)
    second = render_natural_sentence(Unary('ready', Const('alice')), env, **options)
    assert first.form == second.form == 'explicit form'
    assert '"api"' in first.text and '"alice"' in second.text
    assert parse_english(env, first.text + '.', **options) == Document((Unary('reviewed', Const('api')),))


@pytest.mark.parametrize('alias', ['the api', 'The api', 'the API', 'api', 'API'])
def test_declared_constant_cannot_shadow_generated_article_or_case(alias):
    data = vocabulary()
    data['vocabulary']['constants']['beta'] = {'sort': 'item', 'description': 'Beta'}
    env = Environment(data)
    options = _names(env, beta=alias)
    from ve.english import EnglishVocabulary
    words = EnglishVocabulary(env, **options)
    assert words.constants['api'] == 'api'
    assert words.constants['beta'] == '"beta"'
    api = Document((Unary('reviewed', Const('api')),))
    beta = Document((Unary('reviewed', Const('beta')),))
    assert parse_english(env, 'The api is reviewed.', **options) == api
    assert parse_english(env, 'the api is reviewed.', **options) == api
    assert parse_english(env, '"beta" is reviewed.', **options) == beta
    assert '"beta"' in natural_document(env, beta, **options).text


def test_closure_body_referents_disable_ambiguous_it():
    data = vocabulary()
    data['vocabulary']['constants']['beta'] = {'sort': 'item', 'description': 'Beta'}
    data.pop('profile')
    data.update(language='ve.core@0.1', profiles=['closure@0', 'relational-fol@0'],
                spec_revision='ve-v0.1-closure-2026-09-21')
    env = Environment(data)
    closure = Reach('plus', Body('item', Binary('links', Var(1), Const('beta'))),
                    Const('api'), Const('api'))
    followup = Unary('reviewed', Const('api'))
    first = render(Document((closure,)), env, 've_natural')
    assert parse_english(env, first) == Document((closure,))
    view = natural_document(env, Document((closure, followup)))
    assert 'It is reviewed' not in view.text
    assert parse_english(env, view.text) == Document((closure, followup))
    with pytest.raises(Exception):
        parse_english(env, first + ' It is reviewed.')


def test_writable_shared_copula_and_unqualified_owner():
    compound = Exists('item', And(Unary('active', Var(0)), Unary('reviewed', Var(0))))
    owner = Forall('item', Exists('agent', Binary('owns', Var(0), Var(1))))
    assert parse_english(ENV, 'Some service is deployed and reviewed.') == Document((compound,))
    assert parse_english(ENV, 'Every service has an owner.') == Document((owner,))
    for formula in (compound, owner):
        sentence = render_natural_sentence(formula, ENV).text
        assert parse_english(ENV, sentence + '.') == Document((formula,))


def test_complete_natural_document_obeys_english_derivation_budget():
    from ve import Top
    document = Document((Top(),) * 420)
    for display in (lambda: render(document, ENV, 've_natural'),
                    lambda: natural_document(ENV, document).text):
        with pytest.raises(ResourceLimit, match='MAX_NODES'):
            display()


def test_no_contractor_with_definite_constant():
    data = vocabulary()
    data['vocabulary']['sorts']['agent']['verbalisation'] = {'singular': 'contractor', 'plural': 'contractors'}
    data['vocabulary']['predicates']['may_access'] = {
        'arguments': ['agent', 'item'], 'description': 'Contractor may access a service',
        'verbalisation': '{0} may access {1}'}
    data['vocabulary']['constants']['server'] = {'sort': 'item', 'description': 'The server'}
    env = Environment(data)
    formula = Not(Exists('agent', Binary('may_access', Var(0), Const('server'))))
    assert render_natural_sentence(formula, env).text == 'No contractor may access the server'
    assert parse_english(env, 'No contractor may access the server.') == Document((formula,))


def test_negative_arithmetic_is_audited_explicit_form():
    from conformance.english_surface import order_environment
    env = order_environment()
    formula = Le(Num(-3), Const('budget'))
    result = render_natural_sentence(formula, env)
    assert not result.natural and result.reason == 'symbols_or_variable_names'
    assert result.fluent_text == render(formula, env, 've_fluent')
    assert result.form == 'explicit form'
    assert parse_english(env, result.text + '.') == Document((formula,))
    assert natural_coverage([Le(Num(3), Const('budget')), formula], env) == {
        'statements': 2, 'natural': 1, 'fallback': 1, 'natural_fraction': 0.5,
        'fallback_reasons': {'symbols_or_variable_names': 1}}


def test_versioned_prose_keeps_notation_fallback_unresolved():
    from conformance.english_surface import order_environment
    env = order_environment()
    formula = Le(Num(-3), Const('budget'))
    document = Document((formula,))
    with pytest.raises(PresentationNeedsRepair) as raised:
        render_presentation(env, document)
    assert raised.value.details == ({'statement': 1,
                                     'reason': 'symbols_or_variable_names'},)
    legacy = render(document, env, 've_english')
    with pytest.raises(PresentationNeedsRepair):
        parse_presentation(env, legacy)
    preview = migrate_presentation(env, legacy)
    assert preview['proposed'] is None and preview['unresolved']
    assert preview['meaning_unchanged'] and preview['presentation_approval_required']


def test_nested_word_lists_and_some_compound_roundtrip():
    from ve.printer import natural_document
    nested = And(Unary('active', Const('api')),
                 And(Unary('reviewed', Const('api')),
                     Not(Unary('exempt', Const('api')))))
    compound = Exists('item', And(Unary('active', Var(0)), Unary('reviewed', Var(0))))
    document = Document((nested, compound))
    view = natural_document(ENV, document)
    assert 'first clause:' in view.text and 'end second clause' in view.text
    assert view.sentences[1]['text'] == 'Some service is deployed and is reviewed'
    assert parse_english(ENV, view.text) == document
    assert all(item['form'] == 'natural' for item in view.to_dict()['sentences'])


def test_three_bound_entities_use_writable_ordinals():
    from ve import Eq
    formula = Forall('item', Forall('item', Forall('item',
              Eq(Var(2), Var(0)))))
    result = render_natural_sentence(formula, ENV)
    assert result.natural
    assert 'third service' in result.text
    assert parse_english(ENV, result.text + '.') == Document((formula,))


def test_distinct_identifiers_survive_explicit_fallback():
    data = vocabulary()
    for name in ('flag_a', 'flag__a'):
        data['vocabulary']['predicates'][name] = {
            'arguments': ['item'], 'description': name}
    data['vocabulary']['constants']['a__b'] = {'sort': 'item', 'description': 'A double underscore'}
    env = Environment(data)
    formulas = (Unary('flag_a', Const('api')), Unary('flag__a', Const('api')),
                Unary('active', Const('a__b')))
    results = [render_natural_sentence(formula, env) for formula in formulas]
    assert len({r.text for r in results}) == 3
    assert all(r.form == 'explicit form' for r in results)
    for formula, result in zip(formulas, results):
        assert parse_english(env, result.text + '.') == Document((formula,))


def test_negative_universal_uses_explicit_scope():
    formula = Forall('item', Not(Unary('reviewed', Var(0))))
    result = render_natural_sentence(formula, ENV)
    assert 'it is not the case that' in result.text
    assert parse_english(ENV, result.text + '.') == Document((formula,))
    assert not result.text.startswith('Every service is not')


def test_case_varied_and_nested_adjective_ambiguity_rejects():
    data = vocabulary()
    data['vocabulary']['sorts']['deployed_item'] = {
        'description': 'Deployed item',
        'verbalisation': {'singular': 'deployed service', 'plural': 'deployed services'}}
    env = Environment(data)
    for sentence in ('Every deployed service is reviewed.',
                     'It is not the case that every deployed service is reviewed.',
                     'Every DEPLOYED service is reviewed.'):
        with pytest.raises(Exception, match='two derivations'):
            parse_english(env, sentence)


def test_forced_candidate_rejection_audits_final_fallback(monkeypatch):
    import ve.natural as natural
    from ve.errors import ResourceLimit
    real_parse = natural.parse_english
    calls = []
    def reject_once(env, text, **options):
        calls.append(text)
        if len(calls) == 1:
            raise ResourceLimit('forced Earley budget rejection')
        return real_parse(env, text, **options)
    monkeypatch.setattr(natural, 'parse_english', reject_once)
    formula = Exists('item', Unary('active', Var(0)))
    result = natural.render_natural_sentence(formula, ENV)
    assert result.form == 'explicit form' and len(calls) == 2
    assert result.reason == 'english_audit_ResourceLimit'
    assert real_parse(ENV, result.text + '.') == Document((formula,))


def test_no_sentence_is_displayed_when_every_audit_exhausts_budget(monkeypatch):
    import ve.natural as natural
    from ve.errors import ResourceLimit
    def exhausted(*_args, **_kwargs):
        raise ResourceLimit('forced budget exhaustion')
    monkeypatch.setattr(natural, 'parse_english', exhausted)
    with pytest.raises(ValueError, match='No writable English form'):
        natural.render_natural_sentence(Exists('item', Unary('active', Var(0))), ENV)


def test_order_comparison_uses_at_least_without_operator_symbols():
    from conformance.english_surface import order_environment
    env = order_environment()
    formula = Le(Num(3), Const('budget'))
    result = render_natural_sentence(formula, env)
    assert result.natural and result.text == 'Budget is at least 3'
    assert parse_english(env, result.text + '.') == Document((formula,))
    twice = Lt(Scale(2, Const('budget')), Const('limit'))
    result = render_natural_sentence(twice, env)
    assert result.natural and result.text == 'Limit is more than twice the budget'
    assert parse_english(env, result.text + '.') == Document((twice,))


def test_order_comparison_preserves_internal_capitals_in_declared_names():
    from conformance.english_surface import order_environment
    env = order_environment()
    options = _names(env, budget='Annual Budget', limit='Quarterly Limit')
    comparison = Le(Num(3), Const('budget'))
    doubled = Lt(Scale(2, Const('budget')), Const('limit'))
    document = Document((comparison, comparison))
    source = 'Annual Budget is at least 3. Therefore Annual Budget is at least 3.'
    assert parse_english(env, source, **options) == document
    assert render_natural_sentence(comparison, env, **options).text == 'Annual Budget is at least 3'
    presentation = render_presentation(env, document, conclusions=(1,), **options)
    assert presentation.text == source
    assert migrate_presentation(env, source, **options)['proposed'].document == document
    doubled_options = _names(env, limit='Quarterly Limit')
    assert render_natural_sentence(doubled, env, **doubled_options).text == 'Quarterly Limit is more than twice the budget'
    assert parse_english(env, 'Quarterly Limit is more than twice the budget.',
                         **doubled_options) == Document((doubled,))


def test_repository_corpus_accepts_no_wrong_reading():
    from conformance.natural_surface import audit
    report = audit(random_per_vocabulary=5)
    assert report['accepted_wrong_readings'] == 0
    assert not report['skipped']
    assert report['natural'] and report['fallback']
    assert sum(report['fallback_dispositions'].values()) == report['fallback']
    assert report['real_documents']['exact_prose_round_trips'] > 0
    assert not report['real_documents']['prose_failures']
