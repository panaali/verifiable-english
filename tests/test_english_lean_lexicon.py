"""Lexicon validity fixtures of English in Lean (spec 8.5) against the Python reference of `Lexicon.valid`."""
import json
from pathlib import Path
import warnings

import pytest

from ve import Environment
from ve.english import EnglishVocabulary, UnreviewedVocabularyWarning
from ve.english_phrases import wording_key
from ve.english_vocabulary import negative_template
from ve.errors import VEError

from conformance import english_lean_lexicon as X

ROOT = Path(__file__).resolve().parents[1]
CORPUS = json.loads((ROOT / 'conformance/english-lean/lexicon.json').read_text())


def _environment(name):
    return X.fixture_environment(CORPUS, name)


def _lexicon(case, env):
    return X.fixture_lexicon(CORPUS, case, env)


@pytest.mark.parametrize('case', CORPUS['cases'], ids=lambda c: c['id'])
def test_lexicon_validity_fixture(case):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UnreviewedVocabularyWarning)
        words = X.fixture_vocabulary(CORPUS, case['env'])
    failures = X.check(words, _lexicon(case, words.env))
    assert sorted({f[0] for f in failures}) == case['conditions'], failures


@pytest.mark.parametrize('case', CORPUS['negative_templates'], ids=lambda c: c['wording'])
def test_negative_template_fixture(case):
    assert negative_template(case['wording'], case['arity']) == case['expected']


def test_python_selects_LF_for_the_fluent_environment():
    env = _environment('F')
    lex = X.export(EnglishVocabulary(env))
    assert {k: v for k, v in lex.items() if k not in ('format', 'environment_id')} == CORPUS['LF']
    assert X.check(EnglishVocabulary(env), lex) == []


def test_lexicon_id_is_domain_separated_and_changes_with_a_selection():
    env = _environment('F')
    lex = X.export(EnglishVocabulary(env))
    other = _lexicon(CORPUS['cases'][1], env)
    assert X.lexicon_id(lex) != X.lexicon_id(other)
    assert len(X.lexicon_id(lex)) == 64
    from ve.wire import digest
    assert X.lexicon_id(lex) != digest('ve-english-vocabulary-v1\n', lex)


def test_wording_key_port_agrees_on_ascii_and_folds_narrowly():
    for text in ['{0} is  Reviewed', '{0} is non-citizen of {1}', '{0} has "A  B" -- x']:
        assert X.wording_key_lean(text) == wording_key(text)
    # Python's casefold is wider than the Lean fold (spec 2.3): the sharp s is the first difference.
    assert wording_key('{0} is Groß') != X.wording_key_lean('{0} is Groß')


def test_wording_key_reads_quotes_as_lean_does():
    """looprecheck1 finding 2: an unmatched `"` is an ordinary character (the rest is folded), and an
    escaped line break stays inside its quoted part. The generated fixtures check the same texts
    against Lean's `wordingKey`; on ASCII, production's key is the reference's."""
    assert wording_key('"ALICE') == wording_key('"alice') == '"alice'
    assert wording_key('x "A" "B') == 'x "A" "b'
    assert wording_key('"a\\\nB"') != wording_key('"a\\\nb"')
    texts = X.wording_key_texts()
    assert len(texts) > 1400
    for text in texts:
        if text.isascii():
            assert wording_key(text) == X.wording_key_lean(text), repr(text)


def test_lean_fixtures_are_generated_from_the_python_reference():
    # `lake build` checks each #guard: Lean's `Lexicon.failures` equals the reference's failures.
    assert X.LEAN_FIXTURES.read_text() == X.lean_fixtures(), \
        'regenerate: uv run python -m conformance.english_lean_lexicon --lean-fixtures'


def test_every_corpus_environment_has_a_valid_selected_lexicon():
    report = X.corpus_report()
    assert len(report['environments']) == 39
    assert report['valid'] == len(report['environments'])
    assert report['invalid'] == 0
    assert report['failures_by_condition'] == {}
    assert report['wording_key_differences'] == []
    assert all('error' not in row and row['failures'] == [] for row in report['environments'])
    committed = json.loads((ROOT / 'conformance/english-lean/lexicon-report.json').read_text())
    assert committed == report


def test_mutants_reach_every_condition_and_never_crash():
    env = _environment('F')
    view = X.lexical_view(EnglishVocabulary(env))
    lf = {field: CORPUS['LF'][field] for field in X.LEXICON_FIELDS}
    found = {label: X.failures(view, lex) for label, lex in X.mutants(view, lf)}
    assert {f[0] for fs in found.values() for f in fs} == {'V1', 'V2', 'V3', 'V4', 'V5'}
    assert sum(1 for fs in found.values() if not fs) < len(found) // 4
    # a repeated entry of any field is V1 (review regression: dictionaries dropped the repetition)
    for field in ('nouns', 'letters', 'wordings', 'negatives', 'spellings'):
        for label, fs in found.items():
            if label.startswith(field + '[') and label.endswith(' dup'):
                assert any(f[0] == 'V1' for f in fs), label


@pytest.mark.parametrize('value', [7, None, True, {}, [['owns']], [['owns', 7]], [[1, 'x']], 'owns'])
def test_a_malformed_lexicon_is_refused(value):
    env = _environment('F')
    lex = _lexicon(CORPUS['cases'][0], env)
    lex['wordings'] = value
    with pytest.raises(VEError):
        X.check(EnglishVocabulary(env), lex)
    lex = _lexicon(CORPUS['cases'][0], env)
    lex['aliases'] = [['owns', '{0} has {1}', 0]]
    with pytest.raises(VEError):
        X.check(EnglishVocabulary(env), lex)


@pytest.mark.parametrize('wording,arity', [(None, 2), ('', 2), ('{0}', 2), ('{0}', 1), ('{0} gives {1} to {2}', 3),
                                           ('{0} is given {1} by {2}', 3)])
def test_negative_template_is_total(wording, arity):
    expected = '{0} is not given {1} by {2}' if wording == '{0} is given {1} by {2}' else None
    assert X.negative_template_of(wording, arity) == expected


@pytest.mark.parametrize('wording,arity,ok', [
    ('{0} owns {1}', 2, True), ('{0}, then {1}', 2, True), ('{0}s are {1}', 2, False),
    ('{0}"x" {1}', 2, False), (' {0} is deployed', 1, False), ('{0} is deployed .', 1, False)])
def test_v3_reads_the_substitution_of_the_lexical_rules(wording, arity, ok):
    """Review C2, the same wordings as `Examples.lean`: V3 holds exactly when `wording_tokens` (Lean's
    `wordingTokens`, which the lexical rules read) gives the wording's tokens, so no wording passes V3 and
    gives no rule."""
    assert X._shape_ok(wording, arity) is ok
    assert (X.wording_tokens(wording) is not None) is ok
