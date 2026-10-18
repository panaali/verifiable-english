"""The RD-9 use of E14's existing sentence with Lean-selected gaps."""

import copy

import pytest

from tests import lean_routes
from tests.test_readings_nd_lean import PROBE1, base1, doc1, env1
from tests.test_readings_s1_lean import entry
from ve.errors import CheckerUnavailable
from ve import readings_route

from ve.readings_english import force_twin_sentence
from ve.readings_s2_english import s1_gated


def _line(gaps=""):
    return force_twin_sentence("must", "a must act", "a should act", "the decider", ("a", "u"),
                               "obligation", True, False, gaps=gaps)


def test_e14_without_gaps_keeps_the_existing_wording():
    assert _line() == ("This sentence says *must*. (1) *a must act* (2) *a should act* "
                       "They differ here: suppose the decider decides the exception applies to a and u. "
                       "Under (1) a still must. Under (2) a is not required to.")


def test_e14_places_leans_gap_after_decision_and_before_outcomes():
    text = _line(" Here the text does not say whether a must act; this situation answers 'no'.")
    assert "exception applies to a and u. Here the text does not say whether" in text
    assert "answers 'no'. Under (1) a still must. Under (2) a is not required to." in text


def test_e14_keeps_both_readings_and_the_source_word_with_a_gap():
    text = _line(" Here the text does not say whether a must act; this situation answers 'no'.")
    assert "says *must*. (1) *a must act* (2) *a should act*" in text
    assert text.count("Under (1)") == text.count("Under (2)") == 1
    assert s1_gated("E14", text) == text


def test_pair_gaps_are_typed_and_bound_to_the_request(monkeypatch):
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")
    raw = env1()
    document, _ = doc1(raw, entry(base1([["a", "u"]]), "asks", PROBE1, False))
    args = (raw, document["units"], document["reading_sets"])
    genuine = readings_route.validate(*args)
    pair = genuine["sets"][0]["pairs"][0]["pair"]
    assert pair["gaps"] == [["help_required", ["a", "u"], False]]

    for change in (
        lambda f: f.pop("gaps"),
        lambda f: f["gaps"][0].__setitem__(0, "asks"),
        lambda f: f["gaps"][0][1].__setitem__(0, "missing"),
        lambda f: f["gaps"][0].__setitem__(1, []),
        lambda f: f["gaps"][0].__setitem__(2, "yes"),
        lambda f: f["gaps"].append(copy.deepcopy(f["gaps"][0])),
    ):
        forged = copy.deepcopy(genuine)
        change(forged["sets"][0]["pairs"][0]["pair"])
        monkeypatch.setattr(readings_route, "run_lean", lambda *a, **k: [forged])
        with pytest.raises(CheckerUnavailable):
            readings_route.validate(*args)


@pytest.mark.parametrize('fixture,predicate,values', [
    ('F-ND1', 'help_required', ['b', 'u']),
    ('F-ND2', 'x_permitted', ['a']),
])
def test_unlisted_fnd_gap_flip_keeps_leans_witness_value(fixture, predicate, values):
    """B6: the pair value is stable when an admissible, unlisted gap flips."""
    from tests.test_readings_nd_lean import doc2, env2, one
    from tests.test_readings_s1_lean import situation_id
    raw = env1() if fixture == 'F-ND1' else env2()
    document, sid = (doc1(raw) if fixture == 'F-ND1' else doc2(raw))
    observed = []
    for present in (False, True):
        source = copy.deepcopy(document)
        reading_set = source['reading_sets'][0]
        situation = reading_set['situations'][sid]
        if fixture == 'F-ND1':
            situation['base']['domains']['agent'].append('b')
            situation['base']['relations']['unsaid__help_permitted'].append(['b', 'u'])
        situation['base']['relations']['unsaid__' + predicate] = [values] if present else []
        new_id = situation_id(raw, situation)
        reading_set['situations'] = {new_id: situation}
        for reading in reading_set['readings']:
            reading['admission']['distinguishing_models'] = {
                other: new_id for other in reading['admission']['distinguishing_models']}
        row = one('ve_readings_route', 'readings-validate', raw, source)
        assert row['status'] == 'ok', row
        pair = row['sets'][0]['pairs'][0]['pair']
        assert all((gap[0], gap[1]) != (predicate, values) for gap in pair['gaps'])
        observed.append((pair['witness_value'], pair['other_value'], pair['gaps']))
    assert observed[0] == observed[1]


@pytest.mark.parametrize('fixture', ['C2', 'C4'])
def test_unlisted_ce4_gap_flips_keep_leans_witness_value(fixture):
    """B6: every other CE4 completion table can flip without changing the shown pair value."""
    from tests import ce4
    from tests.test_readings_s1_lean import run, situation_id
    from tests.test_readings_sd_ce4 import PAIRS
    raw = ce4.environment()
    set_id, _, _, listed, _ = PAIRS[fixture]
    observed = []
    for predicate in ce4.REGULATED:
        if predicate == listed[0]:
            continue
        values = [{'claude_instance': 'c', 'situation': 's', 'user': 'u'}[sort]
                  for sort in raw['vocabulary']['predicates'][predicate]['arguments']]
        answers = []
        for present in (False, True):
            situation = ce4.sigma(set_id)
            situation['base']['relations']['unsaid__' + predicate] = [values] if present else []
            sets = ce4.with_situations(raw, ce4.reading_sets(), situation_id, {set_id: situation})
            for reading_set in sets:
                for reading in reading_set['readings']:
                    reading['meaning_id'] = 'm'
            [row] = run('ve_readings_route', [{
                'id': 'v', 'kind': 'readings-validate', 'environment': raw,
                'document': ce4.wire_document(sets)}])
            assert row['status'] == 'ok', row
            entry = next(item for item in row['sets'] if item['set'] == set_id)
            pair = entry['pairs'][0]['pair']
            assert all(gap[0] != predicate for gap in pair['gaps'])
            answers.append((pair['witness_value'], pair['other_value'], pair['gaps']))
        observed.append(answers)
    assert observed and all(left == right for left, right in observed)
