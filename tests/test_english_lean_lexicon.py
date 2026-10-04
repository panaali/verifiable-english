"""Lexicon validity fixtures of English in Lean (spec 8.5) against the Python reference of `Lexicon.valid`."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from ve import Environment
from ve.english import EnglishVocabulary
from ve.english_phrases import wording_key
from ve.english_vocabulary import negative_template

from conformance import english_lean_lexicon as X

ROOT = Path(__file__).resolve().parents[1]
CORPUS = json.loads((ROOT / 'conformance/english-lean/lexicon.json').read_text())


def _environment(name):
    spec = CORPUS['environments'][name]
    data = json.loads((ROOT / spec['path']).read_text())
    data['vocabulary']['predicates'].update(spec.get('add_predicates', {}))
    return Environment(data)


def _lexicon(case, env):
    lex = {'format': X.FORMAT, 'environment_id': env.environment_id, **deepcopy(CORPUS['LF'])}
    for edit in case['edits']:
        (op, args), = edit.items()
        entries = dict(map(tuple, lex[args[0]]))
        if op == 'remove':
            entries.pop(args[1])
        else:
            entries[args[1]] = args[2]
        lex[args[0]] = sorted([k, v] for k, v in entries.items())
    return lex


@pytest.mark.parametrize('case', CORPUS['cases'], ids=lambda c: c['id'])
def test_lexicon_validity_fixture(case):
    env = _environment(case['env'])
    failures = X.check(EnglishVocabulary(env), _lexicon(case, env))
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
