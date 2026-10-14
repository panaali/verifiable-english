"""Each soft decision's key in Lean's soft-norms row (`SoftNorms.keyedDecisions`; rd-9 soft-chain plan SC-8).

The readings modules find a decision's name by what it decides, never by spelling it (`tools/relay_lint.py`), so the
row's `decisions` carry Lean's key. A genuine row keys every decision; the relay binds each key to the request (a
declared rule, default for an exception, the party among its switches for a switch, a colliding pair's `outweighs`
on its act and ranks), and every mutant of a key, retyped or rebound, is `CheckerUnavailable` (DRI ruling R8).
"""
from __future__ import annotations

import copy

import pytest

from tests.test_soft_norms_lean import elaborate, env, lean, ranks, should  # noqa: F401  (the `lean` fixture)
from ve import softnorms
from ve.errors import CheckerUnavailable


def _source():
    raw = env(ranks(["a", "b"], "holistic", parties=("user",)))
    norms = [should("h", "x_required", True, rank="a", alterable=["user"]),
             should("l", "x_required", False, rank="b")]
    return raw, norms


@pytest.fixture(scope="module")
def genuine(lean):
    raw, norms = _source()
    return elaborate(lean, raw, norms)


def test_every_decision_carries_leans_key(genuine):
    assert [(d["key"], d["name"]) for d in genuine["decisions"]] == [
        ({"excepted": "h"}, "soft__excepted__h"),
        ({"excepted": "l"}, "soft__excepted__l"),
        ({"off": "h", "party": "user"}, "soft__off__h__user"),
        ({"outweighs": "x_permitted", "lower": "b", "higher": "a"}, "soft__outweighs__b__a__x_permitted")]


def _document(monkeypatch, row):
    raw, norms = _source()
    monkeypatch.setattr(softnorms, "check_soft_source", lambda *args, **kwargs: row)
    return softnorms.SoftNormDocument(softnorms.SoftEnvironment(raw), norms)


def test_the_relay_finds_each_name_by_its_key(monkeypatch, genuine):
    document = _document(monkeypatch, copy.deepcopy(genuine))
    assert document.decision_name(("excepted", "l")) == "soft__excepted__l"
    assert document.decision_name(("off", "h", "user")) == "soft__off__h__user"
    assert document.decision_name(("outweighs", "x_permitted", "b", "a")) == "soft__outweighs__b__a__x_permitted"


def _key(row, i):
    return row["decisions"][i]["key"]


def _reverse_coherence_label(row):
    pair = row['colliding_pairs'][0]
    reversed_label = f"soft:coherence:{pair['pair'][1]},{pair['pair'][0]}"
    old_label = pair['label']
    pair['label'] = reversed_label
    for entry in row['background']:
        if entry.get('label') == old_label:
            entry['label'] = reversed_label
    row['conditional_on'] = [reversed_label if label == old_label else label
                             for label in row['conditional_on']]


MUTATIONS = {
    "key dropped": lambda row: row["decisions"][0].pop("key"),
    "key null": lambda row: row["decisions"][0].__setitem__("key", None),
    "key a list": lambda row: row["decisions"][0].__setitem__("key", ["excepted", "h"]),
    "key empty": lambda row: row["decisions"][0].__setitem__("key", {}),
    "key field retyped": lambda row: _key(row, 0).__setitem__("excepted", 7),
    "key with an extra field": lambda row: _key(row, 0).__setitem__("bearer", "u"),
    "key of another kind": lambda row: row["decisions"][0].__setitem__("key", {"lim": "h", "act": "x_required"}),
    "exception of an undeclared rule": lambda row: _key(row, 0).__setitem__("excepted", "nobody"),
    "exception key duplicated": lambda row: _key(row, 1).__setitem__("excepted", "h"),
    "switch for a party the rule does not name": lambda row: _key(row, 2).__setitem__("party", "operator"),
    "switch of a rule without switches": lambda row: _key(row, 2).__setitem__("off", "l"),
    "switch without its party": lambda row: _key(row, 2).pop("party"),
    "outweighs on another act": lambda row: _key(row, 3).__setitem__("outweighs", "x_required"),
    "outweighs between other ranks": lambda row: _key(row, 3).__setitem__("lower", "c"),
    "outweighs with no colliding pair": lambda row: row["colliding_pairs"][0].__setitem__("outweighs", None),
    "decision entry duplicated": lambda row: row["decisions"].append(copy.deepcopy(row["decisions"][0])),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_a_mutated_decision_key_is_unavailable(monkeypatch, genuine, name):
    row = copy.deepcopy(genuine)
    MUTATIONS[name](row)
    with pytest.raises(CheckerUnavailable):
        _document(monkeypatch, row)


def test_two_faults_together_are_unavailable(monkeypatch, genuine):
    row = copy.deepcopy(genuine)
    row["decisions"].reverse()
    _key(row, 0).__setitem__("lower", "a")
    with pytest.raises(CheckerUnavailable):
        _document(monkeypatch, row)


def test_f11_forged_act_in_key_and_collision_is_unavailable(monkeypatch, genuine):
    row = copy.deepcopy(genuine)
    row['decisions'][3]['key']['outweighs'] = 'absent'
    row['colliding_pairs'][0]['act'] = 'absent'
    with pytest.raises(CheckerUnavailable):
        _document(monkeypatch, row)


@pytest.mark.parametrize('mutation', [
    lambda row: row['colliding_pairs'][0].__setitem__('act', 'absent'),
    lambda row: row['colliding_pairs'][0]['pair'].__setitem__(0, 'absent'),
    lambda row: row['rule_acts'].__setitem__('h', 'absent'),
    lambda row: row.__setitem__('decisions', []),
    lambda row: row['decisions'].pop(0),
    lambda row: row['decisions'].pop(2),
    lambda row: row['decisions'].pop(3),
])
def test_f11_unbound_or_missing_decision_rows_are_unavailable(monkeypatch, genuine, mutation):
    row = copy.deepcopy(genuine)
    mutation(row)
    with pytest.raises(CheckerUnavailable):
        _document(monkeypatch, row)


def test_f11_public_soft_elaboration_binds_lean_row(monkeypatch, genuine):
    from ve.backends import soft_relay
    raw, norms = _source()
    row = copy.deepcopy(genuine)
    row['decisions'][0]['key']['excepted'] = 'absent'
    monkeypatch.setattr(soft_relay, 'run', lambda case: row)
    with pytest.raises(CheckerUnavailable):
        softnorms.check_soft_source(raw, norms)


def test_f11_public_soft_route_binds_lean_row(monkeypatch, genuine):
    from ve import soft_route
    document = _document(monkeypatch, copy.deepcopy(genuine))
    row = copy.deepcopy(genuine)
    row['decisions'][0]['key']['excepted'] = 'absent'
    monkeypatch.setattr(soft_route, '_run', lambda case: row)
    with pytest.raises(CheckerUnavailable):
        soft_route.elaborate_soft_document(document)


def test_f11_public_rights_route_binds_lean_row(monkeypatch):
    from tests.test_rights_lean import ARREST, GAMMA, env as rights_env
    from ve.rights import RightsEnvironment
    from ve import rights_route
    environment = RightsEnvironment(rights_env(ARREST))
    row = rights_route.run_rights_case(environment, GAMMA, 'rights-elaborate')
    forged = copy.deepcopy(row)
    forged['decisions'].append({'name': 'soft__excepted__absent', 'arguments': [],
                                'key': {'excepted': 'absent'}})
    monkeypatch.setattr(rights_route, 'decide_once', lambda mode, case: forged)
    with pytest.raises(CheckerUnavailable):
        rights_route.run_rights_case(environment, GAMMA, 'rights-elaborate')


@pytest.mark.parametrize('mutation', [
    pytest.param(lambda row: row.__setitem__('conditional_on', ['soft:coherence:absent:nobody']),
                 id='unbound conditional label'),
    pytest.param(lambda row: row.__setitem__('conditional_on', [row['colliding_pairs'][0]['label']] * 2),
                 id='duplicate conditional label'),
    pytest.param(lambda row: row['colliding_pairs'][0].__setitem__('label', 'soft:coherence:absent,nobody'),
                 id='unbound pair label'),
    pytest.param(lambda row: row.__setitem__('default_exceptions_by_decider', {'absent': 2}),
                 id='unbound decider'),
    pytest.param(lambda row: row.__setitem__('default_exceptions_by_decider', {'unstated': 1}),
                 id='unused fallback decider'),
    pytest.param(lambda row: row.__setitem__('default_exceptions_by_decider', {'assistant': 9}),
                 id='decider count exceeds defaults'),
    pytest.param(lambda row: row['soft_residual'].__setitem__('default_exceptions', 9),
                 id='default count exceeds rules'),
    pytest.param(lambda row: row['soft_residual'].__setitem__('instruction_switches', 9),
                 id='switch count exceeds rules'),
    pytest.param(lambda row: row['soft_residual'].__setitem__('holistic_overrides', 9),
                 id='override count exceeds decisions'),
    pytest.param(lambda row: row['soft_residual'].__setitem__('weighing_points', 9),
                 id='weighing count exceeds pairs'),
])
def test_f12_public_soft_route_rejects_unbound_output(monkeypatch, genuine, mutation):
    from ve import soft_route
    document = _document(monkeypatch, copy.deepcopy(genuine))
    row = copy.deepcopy(genuine)
    mutation(row)
    monkeypatch.setattr(soft_route, '_run', lambda case: row)
    with pytest.raises(CheckerUnavailable):
        soft_route.elaborate_soft_document(document)


def test_f12_decider_counts_are_bound_per_decider(monkeypatch, lean):
    """A valid decider cannot claim the default rule assigned to another decider."""
    from ve import soft_route
    raw, norms = _source()
    norms[1]['norm']['exception']['decided_by'] = 'user'
    row = elaborate(lean, raw, norms)
    assert row['default_exceptions_by_decider'] == {'assistant': 1, 'user': 1}
    monkeypatch.setattr(softnorms, 'check_soft_source', lambda *args, **kwargs: row)
    document = softnorms.SoftNormDocument(softnorms.SoftEnvironment(raw), norms)
    forged = copy.deepcopy(row)
    forged['default_exceptions_by_decider'] = {'assistant': 2}
    monkeypatch.setattr(soft_route, '_run', lambda case: forged)
    with pytest.raises(CheckerUnavailable):
        soft_route.elaborate_soft_document(document)


@pytest.mark.parametrize('mutation', [
    pytest.param(lambda row: row['background'].append(
        {'generator': 'soft', 'label': 'soft:exception:nobody:sufficient:7', 'ast': ['top']}),
        id='F14 undeclared background label'),
    pytest.param(lambda row: row['background'].append(copy.deepcopy(next(
        entry for entry in row['background'] if entry['generator'] == 'soft'))),
        id='duplicate background row'),
    pytest.param(lambda row: row['background'].__setitem__(slice(None), [
        entry for entry in row['background'] if entry['generator'] != 'soft']),
        id='missing background row'),
    pytest.param(lambda row: row['derived'].append(copy.deepcopy(row['derived'][0])),
                 id='extra derived row'),
    pytest.param(lambda row: row['derived'][0].__setitem__('rule', 'absent'),
                 id='undeclared derived rule'),
    pytest.param(lambda row: row['premises'][0].__setitem__('label', 'layer:norms:absent'),
                 id='undeclared layer label'),
    pytest.param(lambda row: row['ranks_above'].__setitem__('absent', []),
                 id='undeclared rank'),
    pytest.param(lambda row: row['ranks_above']['b'].append('absent'),
                 id='undeclared outranking rank'),
    pytest.param(lambda row: row['order'].append('absent'),
                 id='undeclared layer order'),
    pytest.param(lambda row: row['conflict_targets'].append(
        {'target': 'absent', 'sorts': [], 'ast': ['top']}),
        id='extra conflict target'),
    pytest.param(lambda row: row['incompatible_pairs'].append(['h', 'absent']),
                 id='unbound incompatible pair'),
    pytest.param(_reverse_coherence_label, id='reversed coherence label'),
])
def test_f14_each_soft_identity_field_is_bound(monkeypatch, genuine, mutation):
    from ve import soft_route
    document = _document(monkeypatch, copy.deepcopy(genuine))
    row = copy.deepcopy(genuine)
    mutation(row)
    monkeypatch.setattr(soft_route, '_run', lambda case: row)
    with pytest.raises(CheckerUnavailable):
        soft_route.elaborate_soft_document(document)


@pytest.mark.parametrize('field,value', [
    ('conditional_on', ['soft:coherence:absent,nobody']),
    ('conditional_on', ['rights:limitation:absent']),
    ('targets', ['absent']),
    ('targets', []),
    ('targets', ['arrest_permitted', 'arrest_permitted']),
])
def test_f15_rights_conflict_identities_are_bound(monkeypatch, field, value):
    from tests.test_rights_lean import ARREST, GAMMA, env as rights_env
    from ve.rights import RightsEnvironment
    from ve import rights_route
    environment = RightsEnvironment(rights_env(ARREST))
    real = rights_route.decide_once

    def forged(mode, case):
        row = copy.deepcopy(real(mode, case))
        if case['kind'] == 'rights-conflict':
            row[field] = value
        return row

    monkeypatch.setattr(rights_route, 'decide_once', forged)
    with pytest.raises(CheckerUnavailable):
        rights_route.report_rights(environment, GAMMA)


@pytest.mark.parametrize('mutation', [
    pytest.param(lambda row: row['limitations'][0].__setitem__(
        'label', 'rights:limitation:absent:arrest_permitted:necessary:determined_by_law'),
        id='undeclared limitation'),
    pytest.param(lambda row: row['limitations'].append(copy.deepcopy(row['limitations'][0])),
                 id='duplicate limitation'),
    pytest.param(lambda row: row['rights_background'].clear(),
                 id='missing rights background'),
    pytest.param(lambda row: row.__setitem__('conditional_on', ['soft:coherence:absent,nobody']),
                 id='undeclared coherence'),
    pytest.param(lambda row: row['generated'][0].__setitem__('limitation', 'absent'),
                 id='undeclared generated limitation'),
    pytest.param(lambda row: row['generated'].append(copy.deepcopy(row['generated'][0])),
                 id='duplicate generated key'),
    pytest.param(lambda row: row['wordings'].__setitem__('rights__absent', 'forged'),
                 id='extra generated wording'),
    pytest.param(lambda row: row['distinction'][0].__setitem__('predicate', 'absent'),
                 id='undeclared distinction predicate'),
    pytest.param(lambda row: row['lines'][0].__setitem__('right', 'absent'),
                 id='undeclared line right'),
    pytest.param(lambda row: row['lines'][0].__setitem__('predicate', 'absent'),
                 id='undeclared line predicate'),
    pytest.param(lambda row: row['narrowings'][0].__setitem__('right', 'absent'),
                 id='undeclared narrowing right'),
    pytest.param(lambda row: row['narrowings'][0]['mechanisms'][0].__setitem__(
        'target', 'absent:limitation'), id='undeclared narrowing target'),
    pytest.param(lambda row: row['distinction'][0]['hits'].append({
        'right': 'absent', 'rule': row['lines'][0]['rule'],
        'protected': row['distinction'][0]['predicate'], 'cited': False}),
                 id='undeclared distinction right'),
])
def test_rights_elaboration_premise_identities_are_bound(monkeypatch, mutation):
    from tests.test_rights_lean import ARREST, GAMMA, env as rights_env
    from ve.rights import RightsEnvironment
    from ve import rights_route
    environment = RightsEnvironment(rights_env(ARREST))
    row = copy.deepcopy(rights_route.run_rights_case(environment, GAMMA, 'rights-elaborate'))
    mutation(row)
    monkeypatch.setattr(rights_route, 'decide_once', lambda mode, case: row)
    with pytest.raises(CheckerUnavailable):
        rights_route.run_rights_case(environment, GAMMA, 'rights-elaborate')
