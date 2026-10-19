"""PS-6r (docs/spec/presupposition-PLAN.md): wording rows for the four pilot nouns.

The idiom rows "{0} is a N of {1}" for core value, guideline, mission and nature let a heading's presupposition
be written in VE English: "Some thing is a core value of Claude." parses to exactly `∃x core_value_of(x, claude)`,
and VE's enumerated uniqueness form parses to exactly `U(D)`. Declaring the four beside "{0} is human" leaves that
wording's lint unchanged (phase 1 saw it fall back before the head fix 7080d6d04).
"""
from __future__ import annotations

import pytest

from ve.ast import formula_from_data, formula_to_data
from ve.english import EnglishVocabulary, parse_english, render_english
from ve.environment import Environment

# (predicate, noun, owner): the four nouns of the constitution's heading units u0013, u0095, u0002 and u0235.
NOUNS = [('core_value_of', 'core value', 'claude'), ('guideline_of', 'guideline', 'anthropic'),
         ('mission_of', 'mission', 'anthropic'), ('nature_of', 'nature', 'claude')]
HUMAN = {'arguments': ['entity'], 'description': 'Recorded as human.',
         'verbalisation': '{0} is human', 'negative_verbalisation': '{0} is not human'}


def environment(*, nouns=True, human=True):
    predicates = {'human': HUMAN} if human else {}
    if nouns:
        predicates.update({name: {'arguments': ['entity', 'entity'], 'description': f'Recorded as {name}.',
                                  'verbalisation': '{0} is a ' + noun + ' of {1}'} for name, noun, _ in NOUNS})
    return Environment({
        'language': 've.core@0', 'profile': 'relational-fol@0', 'spec_revision': 've-v0-draft-2026-09-20',
        'vocabulary': {
            # The pilot's noun for the sort `entity` (a document field, presupposition-PLAN 2.1).
            'sorts': {'entity': {'description': 'An entity.', 'verbalisation': {'singular': 'thing', 'plural': 'things'}}},
            'predicates': predicates,
            'constants': {'claude': {'sort': 'entity', 'description': 'Claude.'},
                          'anthropic': {'sort': 'entity', 'description': 'Anthropic.'}}}})


def display(env):
    """The capitalised display forms of the two constants (an English overlay)."""
    return {'format': 've.english-vocabulary@1', 'environment_id': env.environment_id, 'sorts': {}, 'predicates': {},
            'constants': {'claude': {'verbalisation': 'Claude'}, 'anthropic': {'verbalisation': 'Anthropic'}}}


def formulas(env, text, **options):
    return [formula_to_data(env, f) for f in parse_english(env, text, **options).formulas]


def existence(name, owner):
    return ['exists', 'entity', ['binary', name, ['var', 0], ['const', owner]]]


def uniqueness(name, owner):
    # U(D): some x is D, and every y that is D is x (under the inner binder var 0 is y, var 1 is x).
    body = ['binary', name, ['var', 0], ['const', owner]]
    return ['exists', 'entity', ['and', body, ['forall', 'entity', ['implies', body, ['eq', ['var', 0], ['var', 1]]]]]]


@pytest.fixture(scope='module')
def env():
    return environment()


@pytest.mark.parametrize('name,noun,owner', NOUNS)
def test_each_pilot_wording_is_admitted(env, name, noun, owner):
    words = EnglishVocabulary(env)
    assert words.predicates[name] == '{0} is a ' + noun + ' of {1}'
    assert not [i for i in words.issues if i.path.startswith(f'/vocabulary/predicates/{name}/')]


@pytest.mark.parametrize('name,noun,owner', NOUNS)
def test_existence_sentence_parses_exactly_and_round_trips(env, name, noun, owner):
    sentence = f'Some thing is a {noun} of {owner}.'
    assert formulas(env, sentence) == [existence(name, owner)]
    rendered = render_english(formula_from_data(env, existence(name, owner)), env) + '.'
    assert rendered == f'There is a thing that is a {noun} of {owner}.'
    assert 'recorded relation' not in rendered
    assert formulas(env, rendered) == [existence(name, owner)]


def test_the_plan_sentence_with_capitalised_display_parses_exactly(env):
    assert formulas(env, 'Some thing is a core value of Claude.', vocabulary=display(env)) == [
        existence('core_value_of', 'claude')]


@pytest.mark.parametrize('name,noun,owner', [n for n in NOUNS if n[0] in ('mission_of', 'nature_of')])
def test_enumerated_uniqueness_parses_to_exactly_u_of_d(env, name, noun, owner):
    rendered = render_english(formula_from_data(env, uniqueness(name, owner)), env) + '.'
    assert rendered == ('There is a first thing such that both of the following hold:\n'
                        f'  (a) the first thing is a {noun} of {owner};\n'
                        f'  (b) for every second thing that is a {noun} of {owner}, '
                        'the second thing is the same as the first thing.')
    assert formulas(env, rendered) == [uniqueness(name, owner)]


def test_the_four_wordings_leave_human_unchanged(env):
    alone, beside = EnglishVocabulary(environment(nouns=False)), EnglishVocabulary(env)
    assert beside.predicates['human'] == alone.predicates['human'] == '{0} is human'
    assert beside.negatives['human'] == alone.negatives['human'] == '{0} is not human'
    human = lambda words: sorted((i.path, i.code) for i in words.issues if '/human/' in i.path)
    assert human(beside) == human(alone) == []
    assert formulas(env, 'Claude is not human.') == [['not', ['unary', 'human', ['const', 'claude']]]]
