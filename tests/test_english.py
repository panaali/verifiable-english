"""Writable English boundaries, scoped references and independent ambiguity checks."""
from copy import deepcopy
import json
from pathlib import Path
import random

import pytest
from lark import Lark

from ve import (And, Binary, Bottom, Const, Document, Environment, Eq, Exists,
                Forall, Implies, Not, Or, Top, Unary, Var, parse, render)
from ve.ast import Body, Named, Reach
from ve.english import (EnglishVocabulary, english_lark_grammar, parse_english,
                        parse_english_with_metadata)
from ve.errors import ResourceLimit, VEError
from test_views import ENV, _random_formula, vocabulary, review_vocabulary


def roundtrip(formula, env=ENV):
    text = render(Document((formula,)), env, 've_english')
    assert parse_english(env, text) == Document((formula,))
    return text


def test_common_careful_english_and_reference_scope():
    guard = Unary('active', Var(0))
    assert roundtrip(Forall('item', Implies(guard, Unary('reviewed', Var(0))))) == 'Every service that is deployed is reviewed.\n'
    assert roundtrip(Forall('item', Implies(guard, Exists('agent', Binary('owns', Var(0), Var(1)))))) == (
        'For every service that is deployed, there is a person who owns that service.\n')
    assert roundtrip(Forall('agent', Exists('agent', Eq(Var(1), Var(0))))) == (
        'For every first person, there is a second person such that the first person is the same as the second person.\n')
    three = Forall('item', Exists('item', Exists('item', Binary('links', Var(2), Var(0)))))
    assert 'named S1' in roundtrip(three) and 'S1 depends on S3' in roundtrip(three)
    assert 'that is deployed' in roundtrip(Exists('item', guard))


def test_no_formula_parentheses_and_no_flattening():
    p, q = Unary('active', Const('api')), Unary('reviewed', Const('api'))
    f = Implies(And(p, Or(q, Not(p))), Exists('item', And(p, q)))
    text = roundtrip(f)
    assert 'all of the following hold:' in text and '(i)' in text
    import re
    assert not re.search('[()]', re.sub(r'\((?:a|b|i|ii)\)', '', text))
    assert roundtrip(And(And(p, q), p)) != roundtrip(And(p, And(q, p)))


def test_minimal_pairs():
    p, q = Unary('active', Const('api')), Unary('reviewed', Const('api'))
    px, qx = Unary('active', Var(0)), Unary('reviewed', Var(0))
    pairs = [
        (Forall('item', Exists('agent', Binary('owns', Var(0), Var(1)))), Exists('agent', Forall('item', Binary('owns', Var(1), Var(0))))),
        (Binary('links', Const('api'), Const('api')), Exists('item', Binary('links', Var(0), Const('api')))),
        (Forall('item', Exists('item', Binary('links', Var(1), Var(0)))), Forall('item', Exists('item', Binary('links', Var(0), Var(1))))),
        (Forall('item', Implies(px, qx)), Implies(Forall('item', px), Forall('item', qx))),
        (And(p, q), Or(p, q)), (Implies(p, q), Implies(q, p)), (And(p, q), p),
        (Not(And(p, q)), And(Not(p), q)),
        (Forall('item', Implies(px, qx)), Forall('item', And(px, qx))),
        (Forall('item', Implies(And(px, Not(Unary('exempt', Var(0)))), qx)),
         Forall('item', Implies(px, And(Not(Unary('exempt', Var(0))), qx)))),
    ]
    for a, b in pairs: assert roundtrip(a) != roundtrip(b)


def test_located_diagnostics_and_paraphrase_back():
    result = parse_english_with_metadata(ENV, 'every  service is deployed.')
    assert result.paraphrase()['changed']
    assert result.english_text == 'Every service is deployed.\n'
    assert parse(ENV, result.canonical_text) == result.document
    with pytest.raises(VEError) as exc:
        parse_english(ENV, 'Every service is deployed.\nThat person owns it.\n')
    assert exc.value.span.line == 2
    assert exc.value.span.column >= 1
    with pytest.raises(VEError): parse_english(ENV, 'There is a person who owns that service.\n')
    with pytest.raises(ResourceLimit): parse_english(ENV, 'x' * 65537)
    with pytest.raises(ResourceLimit): parse_english(ENV, 'It is not the case that ' + 'it is not the case that ' * 65 + 'this is impossible.\n')


def test_closure_named_and_body_endpoints_in_order():
    data = vocabulary()
    data.pop('profile')
    data.update(language='ve.core@0.1', profiles=['closure@0', 'relational-fol@0'], spec_revision='ve-v0.1-closure-2026-09-21')
    env = Environment(data)
    formulas = [Reach('plus', Named('links'), Const('api'), Const('api')),
                Forall('item', Reach('star', Body('item', And(Binary('links', Var(1), Var(0)), Eq(Var(2), Var(1)))), Var(0), Const('api')))]
    parser = Lark(english_lark_grammar(env), parser='earley', lexer='dynamic_complete', ambiguity='explicit')
    for formula in formulas:
        text = roundtrip(formula, env)
        assert 'Starting from ' in text or 'starting from ' in text
        tree = parser.parse(text[0].lower() + text[1:])
        assert not list(tree.find_data('_ambig'))


@pytest.mark.parametrize('predicate,template', [
    ('owns', '{0} is owned by {1}'), ('owns', '{0} belongs to {1}'),
    ('owns', '{0} lacks {1}'), ('owns', '{0} audits carefully {1}'),
    ('deployed', '{0} is undeployed'), ('deployed', '{0} is reviewed already'),
    ('owns', '{1} owns {0}'), ('owns', '{0} owns'), ('owns', '{0} owns {0} {1}'),
    ('owns', '{0} (owns) {1}'), ('owns', '{0} owns\n{1}'), ('owns', '{0} Owns {1}'),
    ('owns', '{0} owns  things {1}'), ('owns', '{0:10} owns {1}'),
    ('deployed', '{0.__class__}'), ('owns', '{0} owns and audits {1}'),
    ('owns', '{0} is {1}'), ('deployed', '{0} is reviewed'), ('deployed', '{0} is  '),
])
def test_earlier_review_attacks_rejected_by_english_policy(predicate, template):
    data = review_vocabulary()
    data['vocabulary']['predicates'][predicate]['verbalisation'] = template
    words = EnglishVocabulary(Environment(data))
    assert words.predicates[predicate] != template
    assert any(i.path == f'/vocabulary/predicates/{predicate}/verbalisation' for i in words.issues)


def test_precision_pass_accepts_ordinary_complements_and_active_phrases():
    data = vocabulary()
    data['vocabulary']['predicates']['active']['verbalisation'] = '{0} is fully deployed'
    data['vocabulary']['predicates']['owns']['verbalisation'] = '{0} contributes to {1}'
    env = Environment(data)
    assert not EnglishVocabulary(env).issues
    assert 'fully deployed' in roundtrip(Forall('item', Unary('active', Var(0))), env)
    assert 'contributes to' in roundtrip(Binary('owns', Const('alice'), Const('api')), env)


def test_random_small_all_derivations():
    rng = random.Random(928)
    parser = Lark(english_lark_grammar(ENV), parser='earley', lexer='dynamic_complete', ambiguity='explicit')
    for _ in range(150):
        f = _random_formula(rng, rng.randrange(1, 7))
        text = roundtrip(f)
        tree = parser.parse(text[0].lower() + text[1:])
        assert not list(tree.find_data('_ambig'))


def test_identity_fixtures_are_unchanged_after_english_roundtrip():
    from ve.identity import meaning_id, source_id
    fixture = json.loads(Path('conformance/identity.json').read_text())
    # The original conformance test checks stored IDs; this adds English transport.
    for case in fixture:
        if 'source' not in case: continue
        env = Environment(case['environment'])
        document = parse(env, case['source'])
        copied = parse_english(env, render(document, env, 've_english'))
        assert document == copied
        assert meaning_id(env, copied) == case['expected_identity']['meaning_id']
        assert env.environment_id == case['expected_identity']['environment_id']
        assert render(copied, env, 've_strict') == render(document, env, 've_strict')


def test_cli_english_all_five_commands_and_strict_compatibility(tmp_path):
    from test_cli import cli
    from ve.model import FiniteModel
    from ve.identity import meaning_id, source_id
    env_path, source_path = tmp_path / 'env.json', tmp_path / 'english.txt'
    env_path.write_text(json.dumps(vocabulary()))
    f = Forall('item', Implies(Unary('active', Var(0)), Unary('reviewed', Var(0))))
    document = Document((f,))
    source_path.write_text(render(document, ENV, 've_english').lower())
    # Preserve proper-name case in general; this fixture contains none.
    for command in ('check', 'parse'):
        result = cli(command, '--env', env_path, '--surface', 'english', source_path)
        assert result.returncode == 0, result.stdout
        record = json.loads(result.stdout)
        assert record['meaning_id'] == meaning_id(ENV, document)
        assert record['source_id'] == source_id(source_path.read_bytes(), ENV)
        assert record['paraphrase']['changed']
        assert record['paraphrase']['input_text'] == source_path.read_text()
        assert record['display_text'] == render(document, ENV, 've_english')
    result = cli('render', '--env', env_path, '--surface', 'english', source_path)
    assert result.returncode == 0 and result.stdout == render(document, ENV, 've_english')
    assert json.loads(result.stderr)['paraphrase']['changed']
    model_path = tmp_path / 'model.json'
    model_path.write_text(json.dumps({'complete': True, 'domains': {'item': ['s'], 'agent': ['p']},
                                     'constants': {'api': 's', 'alice': 'p'},
                                     'relations': {'active': [], 'reviewed': [], 'exempt': [], 'owns': [], 'links': [], 'ready': []}}))
    result = cli('evaluate', '--env', env_path, '--surface', 'english', '--model', model_path, source_path)
    assert result.returncode == 0, result.stdout
    assert json.loads(result.stdout)['evaluation']['status'] == 'Satisfied'
    result = cli('countermodel', '--env', env_path, '--surface', 'english', '--conclusion', source_path)
    assert result.returncode == 0, result.stdout
    assert str(source_path) in json.loads(result.stdout)['paraphrases']
    strict_path = tmp_path / 'strict.ve'
    strict_path.write_text(render(document, ENV, 've_strict'))
    assert cli('render', '--env', env_path, strict_path).stdout == render(document, ENV, 've_english')
    assert cli('render', '--env', env_path, '--surface', 'strict', strict_path).stdout == strict_path.read_text()
    assert cli('render', '--env', env_path, '--view', 've_strict', strict_path).stdout == strict_path.read_text()


@pytest.mark.parametrize('word', 'not no never lacks without every all some any each and or if then unless only nothing everybody solely many few always may must can person service x x0 reviewed unreviewed'.split())
def test_precision_adjective_slot_cannot_smuggle_logic_or_symbols(word):
    data = vocabulary()
    data['vocabulary']['predicates']['active']['verbalisation'] = template = '{0} is fully ' + word
    words = EnglishVocabulary(Environment(data))
    assert words.predicates['active'] != template


def test_empty_vocabulary_and_lexical_precision_negative_lint():
    from ve import lint_vocabulary
    data = vocabulary()
    data['vocabulary'] = {'sorts': {}, 'predicates': {}, 'constants': {}}
    env = Environment(data)
    text = roundtrip(And(Top(), Bottom()), env)
    parser = Lark(english_lark_grammar(env), parser='earley', lexer='dynamic_complete', ambiguity='explicit')
    assert not list(parser.parse(text[0].lower() + text[1:]).find_data('_ambig'))
    data = vocabulary()
    data['vocabulary']['predicates']['active'].update(verbalisation='{0} is fully deployed', negative_verbalisation='{0} is not fully deployed')
    env = Environment(data)
    assert not lint_vocabulary(env, surface='english')
    assert lint_vocabulary(env)
    assert roundtrip(Not(Unary('active', Const('api'))), env) == 'Api is not fully deployed.\n'


def test_committed_english_artifacts_are_reproducible_and_every_usecase_roundtrips():
    from conformance.english_artifacts import generated_documentation
    from ve.english import english_legend
    marker = '<!-- BEGIN GENERATED ENGLISH EVIDENCE -->'
    assert Path('docs/english-surface.md').read_text().split(marker)[1] == '\n' + generated_documentation()
    for path in Path('usecases').glob('*/environment.json'):
        env = Environment.from_json(path.read_bytes())
        document = parse(env, path.with_name('claims.ve').read_bytes())
        text = render(document, env, 've_english')
        artifact = path.with_name('rendered-english.md').read_text()
        assert '```text\n' + text + '```' in artifact
        assert english_legend(env, 'compact') in artifact
        assert parse_english(env, text) == document


def test_rejected_template_equal_to_old_strict_fallback_stays_rejected():
    data = vocabulary()
    data['vocabulary']['predicates']['either'] = {'description': 'Opaque predicate', 'arguments': ['item'],
                                                'verbalisation': '{0} is either'}
    env = Environment(data)
    assert EnglishVocabulary(env).predicates['either'] == '{0} is classified as "either"'
    assert any('/either/' in i.path for i in EnglishVocabulary(env).issues)
    roundtrip(Unary('either', Const('api')), env)


def test_all_existing_negative_attack_templates_also_reject_in_english():
    from test_fluent import negative_vocabulary, test_attacker_negative_templates_rejected_with_explicit_fallback
    mark, = test_attacker_negative_templates_rejected_with_explicit_fallback.pytestmark
    attacks = mark.args[1]
    assert len(attacks) >= 14
    for predicate, negative in attacks:
        data = negative_vocabulary()
        data['vocabulary']['predicates'][predicate]['negative_verbalisation'] = negative
        env = Environment(data)
        assert predicate not in EnglishVocabulary(env).negatives
        atom = Unary(predicate, Const('api')) if predicate == 'reviewed' else Binary(predicate, Const('alice'), Const('api'))
        assert roundtrip(Not(atom), env).startswith('It is not the case that ')


def test_numbered_labels_must_use_declared_sort_letters():
    with pytest.raises(VEError):
        parse_english(ENV, 'For every service named Z1, Z1 is deployed.\n')
