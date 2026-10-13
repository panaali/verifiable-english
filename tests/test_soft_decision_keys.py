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
