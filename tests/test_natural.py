"""The natural view only accepts exact, uniquely parsed English sentences."""

import json
import pytest
from lark import Lark
from pathlib import Path

from ve import (And, Binary, Const, Document, Environment, Exists, Forall,
                Implies, Not, Or, Unary, Var, check_argument,
                parse_english_argument, render)
from ve.english import english_lark_grammar, parse_english
from ve.ast import Body, Le, Lt, Num, Reach, Scale
from ve.natural import _NOTATION, natural_coverage, render_natural_sentence
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
    with pytest.raises(Exception, match='no checked derivation'):
        parse_english(env, 'The API is reviewed. Therefore the API is safe.', **options)
    with pytest.raises(Exception, match='earlier premise'):
        parse_english(env, 'Therefore the API is safe. The API is reviewed.', **options)


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
    with pytest.raises(Exception):
        parse_english(env, source, **options)
    document = Document((Unary('reviewed', Const('api')),
                         Exists('item', Unary('active', Var(0))),
                         Unary('reviewed', Const('api'))))
    view = natural_document(env, document, **options)
    assert view.text.endswith('The API is reviewed.')
    assert parse_english(env, view.text, **options) == document


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


def test_repository_corpus_accepts_no_wrong_reading():
    from conformance.natural_surface import audit
    report = audit(random_per_vocabulary=5)
    assert report['accepted_wrong_readings'] == 0
    assert not report['skipped']
    assert report['natural'] and report['fallback']
