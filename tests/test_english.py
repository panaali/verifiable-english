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
    assert cli('render', '--env', env_path, strict_path).stdout == strict_path.read_text()
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
    for path in (p.with_name('environment.json') for p in Path('usecases').glob('*/claims.ve')):
        env = Environment.from_json(path.read_bytes())
        document = parse(env, path.with_name('claims.ve').read_bytes())
        overlay = json.loads(path.with_name('environment.english.json').read_text())
        text = render(document, env, 've_english', vocabulary=overlay)
        artifact = path.with_name('rendered-english.md').read_text()
        assert '```text\n' + text + '```' in artifact
        assert english_legend(env, 'compact', vocabulary=overlay) in artifact
        assert parse_english(env, text, vocabulary=overlay) == document


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


def test_guards_coordinate_without_losing_binary_association():
    data = vocabulary()
    data['vocabulary']['predicates']['reviewed']['negative_verbalisation'] = '{0} is not reviewed'
    env = Environment(data)
    p, q = Unary('active', Var(0)), Unary('reviewed', Var(0))
    guards = [p, And(p, Not(q)), And(And(p, q), p), And(p, And(q, p))]
    parser = Lark(english_lark_grammar(env), parser='earley', lexer='dynamic_complete', ambiguity='explicit')
    texts = []
    for guard in guards:
        formula = Forall('item', Implies(guard, q))
        text = roundtrip(formula, env)
        assert '(a)' not in text and 'following' not in text
        assert not list(parser.parse(text[0].lower() + text[1:]).find_data('_ambig'))
        texts.append(text)
    assert texts[-1] != texts[-2]
    for guard in [And(And(p, q), And(q, p)), And(p, Or(q, p))]:
        assert 'following hold:' in roundtrip(Forall('item', Implies(guard, q)), env)
    assert parse_english(env, 'For every service that is deployed and that is reviewed, that service is reviewed.') == Document((Forall('item', Implies(And(p, q), q)),))


def test_no_single_item_lists_or_split_if_then_labels():
    p, q = Unary('active', Const('api')), Unary('reviewed', Const('api'))
    for f in [Implies(Not(Eq(Const('api'), Const('api'))), p),
              Implies(Forall('item', p), Exists('item', q)),
              Implies(Implies(p, q), p), Implies(p, Implies(q, p))]:
        text = roundtrip(f)
        assert text.startswith('If ') and ', then ' in text
        assert 'following' not in text and '(a)' not in text
    text = roundtrip(And(Forall('item', p), Exists('item', q)))
    assert text.startswith('Both of the following hold:')


def test_reviewed_overlays_preserve_all_historical_views_and_identities():
    from ve import meaning_id
    from ve.english import english_legend
    from ve.printer import VIEWS, render_vocabulary
    for path in (p.with_name('environment.json') for p in Path('usecases').glob('*/claims.ve')):
        raw = path.read_bytes()
        env = Environment.from_json(raw)
        original = env.to_dict()
        overlay = json.loads(path.with_name('environment.english.json').read_text())
        doc = parse(env, path.with_name('claims.ve').read_bytes())
        words = EnglishVocabulary(env, vocabulary=overlay)
        assert not words.issues
        assert len(overlay['predicates']) == len(env.predicates)
        text = render(doc, env, 've_english', vocabulary=overlay)
        copied = parse_english(env, text, vocabulary=overlay)
        assert copied == doc and meaning_id(env, copied) == meaning_id(env, doc)
        assert env.to_dict() == original and path.read_bytes() == raw
        for view in VIEWS:
            assert render(doc, env, view, vocabulary=overlay) == render(doc, env, view)
            assert render_vocabulary(env, view, vocabulary=overlay) == render_vocabulary(env, view)
        legend = json.loads(english_legend(env, vocabulary=overlay))
        assert legend['environment_id'] == env.environment_id
        assert legend['overlay_digest'] == words.overlay_digest
        assert all(e['review_status'] == 'reviewed' for e in legend['predicates'].values())


def test_suggestions_are_deterministic_linted_and_require_explicit_acceptance(tmp_path):
    from ve import suggest_vocabulary
    from ve.english import english_legend
    from test_cli import cli
    data = vocabulary()
    data['vocabulary']['predicates'] = {
        'is_active': {'description': 'Recorded as active.', 'arguments': ['item']},
        'fully_reviewed': {'description': 'Recorded review.', 'arguments': ['item']},
        'has_access_to': {'description': 'Access.', 'arguments': ['agent', 'item']},
        'owns': {'description': 'Ownership.', 'arguments': ['agent', 'item']},
        'opaque_flag': {'description': 'Recorded as honest.', 'arguments': ['agent']},
        'us_citizen': {'description': 'Citizenship.', 'arguments': ['agent']},
        'is_not_safe': {'description': 'Negation is not guessed.', 'arguments': ['item']},
    }
    env = Environment(data)
    overlay = suggest_vocabulary(env)
    assert overlay == suggest_vocabulary(env)
    assert set(overlay['predicates']) == {'is_active', 'fully_reviewed', 'has_access_to', 'owns', 'opaque_flag'}
    assert all(entry['suggested'] is True for entries in (overlay['sorts'], overlay['predicates']) for entry in entries.values())
    options = dict(vocabulary=overlay, accept_suggested_vocabulary=True)
    assert not EnglishVocabulary(env, **options).issues
    doc = Document((Forall('item', Unary('is_active', Var(0))),))
    original = render(doc, env, 've_english')
    with pytest.raises(VEError, match='accept-suggested-vocabulary'):
        render(doc, env, 've_english', vocabulary=overlay)
    text = render(doc, env, 've_english', **options)
    assert text != original and parse_english(env, text, **options) == doc
    assert render(doc, env, 've_english') == original
    legend = json.loads(english_legend(env, **options))
    assert all(legend['predicates'][name]['review_status'] == 'unreviewed' for name in overlay['predicates'])
    env_path, overlay_path, source = tmp_path / 'env.json', tmp_path / 'words.json', tmp_path / 'source.ve'
    env_path.write_text(json.dumps(data)); overlay_path.write_text(json.dumps(overlay))
    source.write_text(render(doc, env, 've_strict'))
    args = ('render', '--env', env_path, '--view', 've_english', '--english-vocabulary', overlay_path, source)
    assert cli(*args).returncode == 2
    assert cli(*args, '--accept-suggested-vocabulary').stdout == text
    assert cli('render', '--env', env_path, '--view', 've_english', source, '--accept-suggested-vocabulary').stdout == text
    assert json.loads(cli('suggest-vocabulary', '--env', env_path).stdout) == overlay


@pytest.mark.parametrize('mutation', ['identity', 'arguments', 'description', 'unknown', 'bad_template', 'bad_negative', 'suggested_type', 'null_entry'])
def test_overlay_rejects_semantic_fields_and_invalid_metadata(mutation):
    from ve import suggest_vocabulary
    overlay = suggest_vocabulary(ENV)
    overlay['predicates']['active'] = {'verbalisation': '{0} is deployed', 'suggested': False}
    entry = overlay['predicates']['active']
    if mutation == 'identity': overlay['environment_id'] = 'wrong'
    elif mutation == 'unknown': overlay['predicates']['missing'] = entry
    elif mutation == 'bad_template': entry['verbalisation'] = '{0} is either'
    elif mutation == 'bad_negative': entry['negative_verbalisation'] = '{0} is deployed'
    elif mutation == 'suggested_type': entry['suggested'] = 'false'
    elif mutation == 'null_entry': overlay['predicates']['active'] = None
    else: entry[mutation] = ['item'] if mutation == 'arguments' else 'Changed semantics'
    with pytest.raises(VEError): EnglishVocabulary(ENV, vocabulary=overlay, accept_suggested_vocabulary=True)


def test_object_relative_guards_preserve_argument_positions_and_mixed_coordination():
    data = vocabulary()
    data['vocabulary']['predicates']['owns']['negative_verbalisation'] = '{0} does not own {1}'
    env = Environment(data)
    incoming = Binary('owns', Const('alice'), Var(0))
    unary = Unary('active', Var(0))
    parser = Lark(english_lark_grammar(env), parser='earley', lexer='dynamic_complete', ambiguity='explicit')
    for guard in [incoming, Not(incoming), And(incoming, unary), And(unary, incoming),
                  And(And(incoming, unary), Not(incoming)), And(incoming, And(unary, incoming))]:
        text = roundtrip(Forall('item', Implies(guard, Unary('reviewed', Var(0)))), env)
        assert 'Every service that ' in text and 'following' not in text
        assert not list(parser.parse(text[0].lower() + text[1:]).find_data('_ambig'))
    assert roundtrip(Forall('item', Implies(incoming, unary)), env) == 'Every service that alice owns is deployed.\n'
    # An object relative is a noun restriction, never a stand-alone assertion.
    assert roundtrip(Forall('item', incoming), env) == 'For every service, alice owns that service.\n'
    outer_subject = Binary('owns', Var(1), Var(0))
    text = roundtrip(Forall('agent', Forall('item', Implies(And(outer_subject, outer_subject), unary))), env)
    assert 'that that person owns and that person owns' in text
    assert not list(parser.parse(text[0].lower() + text[1:]).find_data('_ambig'))
    with pytest.raises(VEError): parse_english(env, 'Every service alice owns.')


@pytest.mark.parametrize('name,template', [
    ('us_citizen', '{0} is inappropriately harmful'),
    ('deprives', '{0} was appointed by {1}'),
    ('denies_equal_protection', '{0} promised {1}'),
])
def test_idioms_cannot_mislabel_unrelated_predicates(name, template):
    from ve.english_vocabulary import display_environment
    path = Path('usecases/us-constitution-14th-s1/environment.json')
    env = Environment.from_json(path.read_bytes())
    overlay = {'format': 've.english-vocabulary@1', 'environment_id': env.environment_id,
               'sorts': {}, 'predicates': {name: {'verbalisation': template, 'suggested': False}}}
    display, _, _ = display_environment(env, overlay, False)
    issues = EnglishVocabulary(display).issues
    assert any(i.code == 'IDIOM_UNRELATED' and name in i.path for i in issues)
    with pytest.raises(VEError, match='template linter'):
        EnglishVocabulary(env, vocabulary=overlay)


@pytest.mark.parametrize('case', ['constant', 'predicate', 'head', 'converse'])
def test_idioms_still_check_collisions_and_argument_direction(case):
    data = vocabulary()
    predicates = data['vocabulary']['predicates']
    predicates['promised'] = {'arguments': ['agent', 'item'], 'description': 'Promised.',
                              'verbalisation': '{0} promised {1}'}
    if case == 'constant':
        data['vocabulary']['constants']['promised'] = {'sort': 'agent', 'description': 'Name.'}
        # Constants and predicates must have distinct identifiers.
        predicates['pledge'] = predicates.pop('promised')
        target = 'pledge'
    elif case in ('predicate', 'head'):
        predicates['pledge'] = {'arguments': ['agent', 'item'], 'description': 'Promised.'}
        predicates['pledge']['verbalisation'] = '{0} promised {1}'
        target = 'pledge'
        if case == 'head':
            predicates['promises'] = predicates.pop('promised')
            predicates['promises']['verbalisation'] = '{0} promised carefully {1}'
    else:
        predicates['appoints'] = {'arguments': ['agent', 'item'], 'description': 'Appointed by.',
                                  'verbalisation': '{0} was appointed by {1}'}
        target = 'appoints'
    words = EnglishVocabulary(Environment(data))
    assert words.predicates[target] != predicates[target]['verbalisation']
    assert any(i.path == f'/vocabulary/predicates/{target}/verbalisation' for i in words.issues)


def test_review_status_requires_exact_independently_pinned_digest(tmp_path):
    from ve.english import english_legend
    from ve.english_vocabulary import overlay_provenance
    from ve import check, meaning_id
    from test_cli import cli
    path = Path('usecases/us-constitution-14th-s1/environment.json')
    env = Environment.from_json(path.read_bytes())
    overlay = json.loads(path.with_name('environment.english.json').read_text())
    assert overlay_provenance(overlay)['review_status'] == 'reviewed'
    # A harmless metadata change invalidates the review of the entire digest.
    del overlay['predicates']['us_citizen']['negative_verbalisation']
    provenance = overlay_provenance(overlay)
    assert provenance['review_status'] == 'unreviewed'
    assert all(not e['suggested'] for e in overlay['predicates'].values())
    legend = json.loads(english_legend(env, vocabulary=overlay))
    assert legend['review_status'] == 'unreviewed'
    assert all(e['review_status'] == 'unreviewed' for e in legend['predicates'].values())
    assert 'unreviewed' in english_legend(env, 'compact', vocabulary=overlay)
    doc = Document((Forall('person', Unary('us_citizen', Var(0))),))
    from ve.english import UnreviewedVocabularyWarning
    with pytest.warns(UnreviewedVocabularyWarning, match='unreviewed'):
        text = render(doc, env, 've_english', vocabulary=overlay)
    result = check(env, text, surface='english', vocabulary=overlay)
    for key, value in provenance.items():
        assert result[key] == result['paraphrase'][key] == value
    assert result['meaning_id'] == meaning_id(env, doc)
    words_path = tmp_path / 'words.json'; words_path.write_text(json.dumps(overlay))
    source = tmp_path / 'source.ve'; source.write_text(render(doc, env, 've_strict'))
    checked = cli('check', '--env', path, '--english-vocabulary', words_path, source)
    assert checked.returncode == 0
    record = json.loads(checked.stdout)
    assert record['display_text'] == text
    for key, value in provenance.items(): assert record[key] == value
    rendered = cli('render', '--env', path, '--view', 've_english', '--english-vocabulary', words_path, source)
    assert rendered.stdout == text and json.loads(rendered.stderr.splitlines()[0]) == provenance


def test_document_grammar_and_roundtrip_reset_statement_scope():
    formulas = (Forall('item', Unary('active', Var(0))),
                Exists('agent', Exists('agent', Eq(Var(0), Var(1)))),
                Forall('item', Exists('item', Exists('item', Binary('links', Var(2), Var(0))))))
    doc = Document(formulas)
    text = render(doc, ENV, 've_english')
    assert parse_english(ENV, text) == doc
    syntax = ''.join((t := render(Document((f,)), ENV, 've_english'))[0].lower() + t[1:] for f in formulas)
    parser = Lark(english_lark_grammar(ENV), parser='earley', lexer='dynamic_complete', ambiguity='explicit')
    assert not list(parser.parse(syntax).find_data('_ambig'))
    with pytest.raises(VEError): parse_english(ENV, 'Every service is deployed.\nThat service is deployed.\n')


@pytest.mark.parametrize('record', [None, '{}', '[{"overlay_digest": "fake"}]', 'malformed'])
def test_absent_or_invalid_pinned_review_fails_closed(monkeypatch, tmp_path, record):
    from ve import english_vocabulary
    path = Path('usecases/us-constitution-14th-s1/environment.english.json')
    overlay = json.loads(path.read_text())
    monkeypatch.setattr(english_vocabulary, 'files', lambda package: tmp_path)
    if record is not None: (tmp_path / 'reviewed-overlays.json').write_text(record)
    assert english_vocabulary.overlay_provenance(overlay)['review_status'] == 'unreviewed'


def test_conformance_report_includes_deep_random_and_document_samples():
    report = json.loads(Path('conformance/english-surface-report.json').read_text())
    assert len(report['vocabularies']) == 15
    assert report['random_earley_texts'] >= 3750
    assert report['multi_statement_documents'] >= 750
    for row in report['vocabularies']:
        assert row['random_earley_texts'] >= 250
        assert set(row['random_earley_actual_depths']) == {'6', '7', '8', '9'}
        assert sum(row['random_earley_actual_depths'].values()) == row['random_earley_texts']
        assert row['random_earley_seed'] != row['seed']
        assert row['multi_statement_documents'] >= 50
        assert row['ambiguous_texts'] == 0


def test_lint_clean_semantic_lie_is_still_unreviewed():
    from ve import check
    from ve.english import UnreviewedVocabularyWarning
    path = Path('usecases/us-constitution-14th-s1/environment.json')
    env = Environment.from_json(path.read_bytes())
    overlay = {'format': 've.english-vocabulary@1', 'environment_id': env.environment_id,
               'sorts': {}, 'predicates': {'us_citizen': {'verbalisation': '{0} is fully harmful', 'suggested': False}}}
    words = EnglishVocabulary(env, vocabulary=overlay)
    assert not words.issues and words.review_status == 'unreviewed'
    with pytest.warns(UnreviewedVocabularyWarning):
        record = check(env, 'Every person is fully harmful.\n', surface='english', vocabulary=overlay)
    assert record['review_status'] == record['paraphrase']['review_status'] == 'unreviewed'
    assert record['overlay_digest'] == words.overlay_digest
    assert record['ast'] == [['forall', 'person', ['unary', 'us_citizen', ['var', 0]]]]
