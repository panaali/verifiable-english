"""The natural view only accepts exact, uniquely parsed English sentences."""

import pytest
from lark import Lark

from ve import (And, Binary, Const, Document, Environment, Exists, Forall,
                Implies, Not, Unary, Var, render)
from ve.english import english_lark_grammar, parse_english
from ve.ast import Le, Lt, Num, Scale
from ve.natural import _NOTATION, natural_coverage, render_natural_sentence
from ve.errors import ResourceLimit
from ve.printer import natural_document
from test_views import ENV, vocabulary


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
    data['vocabulary']['constants']['api']['verbalisation'] = 'the API'
    data['vocabulary']['constants']['alice']['verbalisation'] = 'Alice'
    data['vocabulary']['constants']['union'] = {
        'sort': 'item', 'description': 'European Union',
        'verbalisation': 'the European Union'}
    env = Environment(data)
    formulas = (Unary('reviewed', Const('api')),
                Unary('ready', Const('alice')),
                Unary('reviewed', Const('union')))
    document = Document(formulas)
    text = natural_document(env, document).text
    assert text == 'The API is reviewed. Alice is ready. The European Union is reviewed.'
    assert render(document, env, 've_natural') == text
    assert parse_english(env, text) == document
    assert len(natural_document(env, document).sentences) == 3


def test_web_app_first_example_is_one_checked_prose_argument():
    data = vocabulary()
    data['vocabulary']['sorts']['item']['verbalisation'] = {
        'singular': 'service', 'plural': 'services'}
    data['vocabulary']['predicates']['safe'] = {
        'arguments': ['item'], 'description': 'Safe', 'verbalisation': '{0} is safe'}
    data['vocabulary']['constants']['api']['verbalisation'] = 'the API'
    env = Environment(data)
    document = Document((
        Forall('item', Implies(Unary('reviewed', Var(0)), Unary('safe', Var(0)))),
        Unary('reviewed', Const('api')),
        Unary('safe', Const('api'))))
    expected = ('Every reviewed service is safe. The API is reviewed. '
                'Therefore the API is safe.')
    for marker in ('Therefore', 'So', 'Hence', 'It follows that'):
        text = expected.replace('Therefore', marker)
        assert parse_english(env, text) == document
        view = natural_document(env, document, conclusions=(2,), conclusion_marker=marker)
        assert view.text == text
        assert view.sentences[2]['role'] == 'conclusion'
        assert render(document, env, 've_natural', conclusions=(2,),
                      conclusion_marker=marker) == text
    with pytest.raises(Exception, match='no checked derivation'):
        parse_english(env, 'The API is reviewed. Therefore the API is safe.')
    with pytest.raises(Exception, match='earlier premise'):
        parse_english(env, 'Therefore the API is safe. The API is reviewed.')


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
