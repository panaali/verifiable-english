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


@pytest.mark.parametrize('mutation', [
    pytest.param(lambda row: row['bars'].append({**copy.deepcopy(row['bars'][0]),
                                                  'name': 'rights-bar-2'}),
                 id='extra bar node'),
    pytest.param(lambda row: row['bars'][0]['over'].append('absent'),
                 id='undeclared bar over rule'),
])
def test_rights_bar_nodes_are_bound_to_generated_aimed_predicates(monkeypatch, mutation):
    from tests.test_rights_lean import IMPART, env as rights_env, line, norm, right
    from ve.rights import RightsEnvironment
    from ve import rights_route
    environment = RightsEnvironment(rights_env(
        IMPART, sorts=('person', 'idea'), rights={'holders': ['person'], 'bearers': ['person']}))
    source = [right('r19', [line('liberty', norm('may-impart', 'impart_permitted', True))]),
              {'bar': {'name': 'b30', 'reading': 'rule'}}]
    row = copy.deepcopy(rights_route.run_rights_case(environment, source, 'rights-elaborate'))
    mutation(row)
    monkeypatch.setattr(rights_route, 'decide_once', lambda mode, case: row)
    with pytest.raises(CheckerUnavailable):
        rights_route.run_rights_case(environment, source, 'rights-elaborate')


@pytest.mark.parametrize('mutation', [
    pytest.param(lambda row: row['narrowings'][0].__setitem__('right', 'absent'),
                 id='F16 forged scope right'),
    pytest.param(lambda row: row['narrowings'][0].__setitem__('rule', 'absent'),
                 id='forged scope rule'),
    pytest.param(lambda row: row['narrowings'].clear(), id='missing scope line'),
    pytest.param(lambda row: row['narrowings'].append(copy.deepcopy(row['narrowings'][0])),
                 id='extra scope line'),
    pytest.param(lambda row: row['narrowings'][0]['mechanisms'][0].__setitem__('target', 'absent:limitation'),
                 id='forged scope target'),
    pytest.param(lambda row: row['narrowings'][0]['mechanisms'].clear(),
                 id='missing scope mechanism'),
])
def test_f16_scope_rows_are_bound_to_elaboration(monkeypatch, mutation):
    from tests.test_rights_lean import ARREST, GAMMA, env as rights_env
    from ve.rights import RightsEnvironment
    from ve import rights_route
    environment = RightsEnvironment(rights_env(ARREST))
    real = rights_route.decide_once

    def forged(mode, case):
        row = copy.deepcopy(real(mode, case))
        if case['kind'] == 'rights-scope':
            mutation(row)
        return row

    monkeypatch.setattr(rights_route, 'decide_once', forged)
    with pytest.raises(CheckerUnavailable):
        rights_route.report_rights(environment, GAMMA)


@pytest.mark.parametrize('mutation', [
    pytest.param(lambda row: row['bars'][0].__setitem__('predicate', 'absent'),
                 id='forged bar predicate'),
    pytest.param(lambda row: row['bars'][0].__setitem__('aimed', 'rights__bar__9'),
                 id='forged bar aimed'),
    pytest.param(lambda row: row['bars'].clear(), id='missing bar row'),
    pytest.param(lambda row: row['bars'].append(copy.deepcopy(row['bars'][0])),
                 id='extra bar row'),
    pytest.param(lambda row: row['bars'][0]['barred'].append('absent'),
                 id='forged barred rule'),
    pytest.param(lambda row: row['bars'][0]['barred'].clear(),
                 id='missing barred rule'),
    pytest.param(lambda row: row['bars'][0]['blocked_defaults'].append('absent'),
                 id='forged blocked default'),
    pytest.param(lambda row: row['bars'][0]['blocked_defaults'].append('may-impart'),
                 id='strict rule as blocked default'),
    pytest.param(lambda row: row['bars'][0]['composition_candidates'].append('absent'),
                 id='forged composition candidate'),
    pytest.param(lambda row: row['bars'][0]['composition_candidates'].append('may-impart'),
                 id='same-predicate line as composition candidate'),
])
def test_f16_bar_rows_are_bound_to_elaboration(monkeypatch, mutation):
    from tests.test_rights_lean import IMPART, env as rights_env, line, norm, right
    from ve.rights import RightsEnvironment
    from ve import rights_route
    environment = RightsEnvironment(rights_env(
        IMPART, sorts=('person', 'idea'), rights={'holders': ['person'], 'bearers': ['person']}))
    source = [right('r19', [line('liberty', norm('may-impart', 'impart_permitted', True))]),
              {'bar': {'name': 'b30', 'reading': 'rule'}}]
    real = rights_route.decide_once

    def forged(mode, case):
        row = copy.deepcopy(real(mode, case))
        if case['kind'] == 'rights-bar':
            mutation(row)
        return row

    monkeypatch.setattr(rights_route, 'decide_once', forged)
    with pytest.raises(CheckerUnavailable):
        rights_route.report_rights(environment, source)


@pytest.mark.parametrize('mutation', [
    pytest.param(lambda row: row['distinction'][0]['hits'].__setitem__(slice(None), [{
        'right': 'r9', 'rule': 'no-arbitrary-arrest', 'protected': 'absent', 'cited': False}]),
                 id='F17 forged protected name'),
    pytest.param(lambda row: row['distinction'].clear(), id='missing distinction row'),
    pytest.param(lambda row: row['distinction'].append(copy.deepcopy(row['distinction'][0])),
                 id='extra distinction row'),
    pytest.param(lambda row: row['distinction'][0].__setitem__('predicate', 'absent'),
                 id='forged distinction predicate'),
])
def test_f17_distinction_rows_and_hits_are_bound(monkeypatch, mutation):
    from tests.test_rights_lean import ARREST, GAMMA, env as rights_env
    from ve.rights import RightsEnvironment
    from ve import rights_route
    environment = RightsEnvironment(rights_env(ARREST))
    real = rights_route.decide_once

    def forged(mode, case):
        row = copy.deepcopy(real(mode, case))
        if case['kind'] == 'rights-elaborate':
            mutation(row)
        return row

    monkeypatch.setattr(rights_route, 'decide_once', forged)
    with pytest.raises(CheckerUnavailable):
        rights_route.report_rights(environment, GAMMA)


def test_f17_authored_protected_hit_is_accepted_and_duplicate_is_unavailable(monkeypatch):
    from tests.test_rights_lean import ARREST, GAMMA, env as rights_env
    from ve.rights import RightsEnvironment
    from ve import rights_route
    raw = rights_env(ARREST, rights={
        'holders': ['person'], 'bearers': ['state', 'person'],
        'protected': ['arbitrary_arrest']})
    environment = RightsEnvironment(raw)
    row = rights_route.run_rights_case(environment, GAMMA, 'rights-elaborate')
    assert row['distinction'][0]['hits'][0]['protected'] == 'arbitrary_arrest'
    forged = copy.deepcopy(row)
    forged['distinction'][0]['hits'].append(copy.deepcopy(forged['distinction'][0]['hits'][0]))
    monkeypatch.setattr(rights_route, 'decide_once', lambda mode, case: forged)
    with pytest.raises(CheckerUnavailable):
        rights_route.run_rights_case(environment, GAMMA, 'rights-elaborate')


@pytest.mark.parametrize('mutation', [
    pytest.param(lambda row: row['environment_prime']['vocabulary']['predicates'].__setitem__(
        'ghost', {'arguments': ['assistant'], 'description': 'base'}), id='prime extra predicate'),
    pytest.param(lambda row: row['environment_prime']['profiles'].append('readings@1'),
                 id='prime extra profile'),
    pytest.param(lambda row: row['decisions'][0].__setitem__('arguments', ['user']),
                 id='decision arguments'),
    pytest.param(lambda row: row['decisions'][0].__setitem__('name', 'soft__ghost'),
                 id='decision name'),
    pytest.param(lambda row: row['decisions'][0].update(
        name=row['decisions'][1]['name']), id='decision duplicate name'),
    pytest.param(lambda row: row['rule_acts'].__setitem__('h', 'x_required'),
                 id='wrong declared act'),
    pytest.param(lambda row: row['order'].clear(), id='missing layer'),
    pytest.param(lambda row: row['conflict_targets'].clear(), id='missing target'),
    pytest.param(lambda row: row['soft_residual'].__setitem__('default_exceptions', 0),
                 id='missing default count'),
    pytest.param(lambda row: row.__setitem__('default_exceptions_by_decider', {}),
                 id='missing decider'),
])
def test_binding_audit_soft_fields_reject_forgery(monkeypatch, genuine, mutation):
    row = copy.deepcopy(genuine)
    mutation(row)
    with pytest.raises(CheckerUnavailable):
        _document(monkeypatch, row)


@pytest.mark.parametrize('mechanism', ['blockedBy absent', 'switch absent', 'carve-out 999'])
def test_f18_narrowing_mechanism_and_target_bind_to_authored_line(monkeypatch, mechanism):
    from tests.test_rights_lean import ARREST, GAMMA, env as rights_env
    from ve.rights import RightsEnvironment
    from ve import rights_route
    environment = RightsEnvironment(rights_env(ARREST))
    row = copy.deepcopy(rights_route.run_rights_case(environment, GAMMA, 'rights-elaborate'))
    row['narrowings'][0]['mechanisms'][0].update(
        mechanism=mechanism, target=f'no-arbitrary-arrest:{mechanism}')
    monkeypatch.setattr(rights_route, 'decide_once', lambda mode, case: row)
    with pytest.raises(CheckerUnavailable):
        rights_route.run_rights_case(environment, GAMMA, 'rights-elaborate')


@pytest.mark.parametrize('mechanism', ['blockedBy absent', 'switch absent', 'carve-out 999'])
def test_f18_extra_undeclared_mechanism_is_unavailable(monkeypatch, mechanism):
    from tests.test_rights_lean import ARREST, GAMMA, env as rights_env
    from ve.rights import RightsEnvironment
    from ve import rights_route
    environment = RightsEnvironment(rights_env(ARREST))
    row = copy.deepcopy(rights_route.run_rights_case(environment, GAMMA, 'rights-elaborate'))
    extra = copy.deepcopy(row['narrowings'][0]['mechanisms'][0])
    extra.update(mechanism=mechanism, target=f'no-arbitrary-arrest:{mechanism}')
    row['narrowings'][0]['mechanisms'].append(extra)
    monkeypatch.setattr(rights_route, 'decide_once', lambda mode, case: row)
    with pytest.raises(CheckerUnavailable):
        rights_route.run_rights_case(environment, GAMMA, 'rights-elaborate')


@pytest.mark.parametrize('mutation', [
    pytest.param(lambda row: row['environment_prime']['vocabulary']['predicates'].__setitem__(
        'rights__lim__9', {'arguments': ['state', 'person'], 'description': 'forged'}),
                 id='extra prime predicate'),
    pytest.param(lambda row: row['environment_prime']['profiles'].append('readings@1'),
                 id='extra prime profile'),
    pytest.param(lambda row: row['lines'][0].__setitem__('instance', 'immunity'),
                 id='wrong line instance'),
    pytest.param(lambda row: row['lines'][0]['node'].__setitem__('sign', True),
                 id='wrong line sign'),
    pytest.param(lambda row: row['lines'][0]['node'].__setitem__('hard', True),
                 id='wrong line hard'),
    pytest.param(lambda row: row['lines'][0]['node'].__setitem__('over', ['absent']),
                 id='wrong line over'),
    pytest.param(lambda row: row['generated'].clear(), id='missing generated predicates'),
    pytest.param(lambda row: row['limitations'].clear(), id='missing limitation premise'),
    pytest.param(lambda row: row['findings'].append('ProtectedInCone: ghost in rule nobody on right nobody'),
                 id='forged distinction finding'),
    pytest.param(lambda row: row['wordings'].__setitem__(
        next(iter(row['wordings'])), '{0.__class__}'), id='unsafe wording placeholder'),
])
def test_binding_audit_rights_fields_reject_forgery(monkeypatch, mutation):
    from tests.test_rights_lean import ARREST, GAMMA, env as rights_env
    from ve.rights import RightsEnvironment
    from ve import rights_route
    environment = RightsEnvironment(rights_env(ARREST))
    row = copy.deepcopy(rights_route.run_rights_case(environment, GAMMA, 'rights-elaborate'))
    mutation(row)
    monkeypatch.setattr(rights_route, 'decide_once', lambda mode, case: row)
    with pytest.raises(CheckerUnavailable):
        rights_route.run_rights_case(environment, GAMMA, 'rights-elaborate')


def test_binding_audit_pair_and_label_removed_together_is_unavailable(monkeypatch, genuine):
    row = copy.deepcopy(genuine)
    label = row['colliding_pairs'].pop()['label']
    row['background'][:] = [entry for entry in row['background'] if entry.get('label') != label]
    row['conditional_on'][:] = [entry for entry in row['conditional_on'] if entry != label]
    row['decisions'][:] = [entry for entry in row['decisions']
                           if 'outweighs' not in entry['key']]
    row['soft_residual']['holistic_overrides'] = 0
    with pytest.raises(CheckerUnavailable):
        _document(monkeypatch, row)


def test_binding_audit_reversed_pair_and_label_together_is_unavailable(monkeypatch, genuine):
    row = copy.deepcopy(genuine)
    pair = row['colliding_pairs'][0]
    old = pair['label']
    pair['pair'].reverse()
    pair['label'] = f"soft:coherence:{pair['pair'][0]},{pair['pair'][1]}"
    for entry in row['background']:
        if entry.get('label') == old:
            entry['label'] = pair['label']
    row['conditional_on'] = [pair['label'] if label == old else label for label in row['conditional_on']]
    with pytest.raises(CheckerUnavailable):
        _document(monkeypatch, row)


def test_binding_audit_rights_generated_name_swap_is_unavailable(monkeypatch):
    from tests.test_rights_lean import ARREST, GAMMA, env as rights_env
    from ve.rights import RightsEnvironment
    from ve import rights_route
    environment = RightsEnvironment(rights_env(ARREST))
    row = copy.deepcopy(rights_route.run_rights_case(environment, GAMMA, 'rights-elaborate'))
    first, second = row['generated'][:2]
    first['name'], second['name'] = second['name'], first['name']
    monkeypatch.setattr(rights_route, 'decide_once', lambda mode, case: row)
    with pytest.raises(CheckerUnavailable):
        rights_route.run_rights_case(environment, GAMMA, 'rights-elaborate')


def test_binding_audit_scope_findings_and_licences_are_bound(monkeypatch):
    from tests.test_rights_lean import ARREST, GAMMA, env as rights_env
    from ve.rights import RightsEnvironment
    from ve import rights_route
    environment = RightsEnvironment(rights_env(ARREST))
    real = rights_route.decide_once

    def forged(mode, case):
        row = copy.deepcopy(real(mode, case))
        if case['kind'] == 'rights-scope':
            row['findings'] = ['UnlicensedLimitation: ghost of rule nobody on right nobody']
        return row

    monkeypatch.setattr(rights_route, 'decide_once', forged)
    with pytest.raises(CheckerUnavailable):
        rights_route.report_rights(environment, GAMMA)


def _rights_relay(monkeypatch, mutation, kinds=('rights-elaborate', 'rights-scope')):
    """Mutate Lean's rows of `kinds` consistently, each still fitting its schema."""
    from ve import rights_route
    from ve.backends.service_schema import check_row
    real = rights_route.decide_once

    def forged(mode, case):
        row = copy.deepcopy(real(mode, case))
        if case['kind'] in kinds:
            mutation(row)
            check_row(mode, row, case, 0)
        return row

    monkeypatch.setattr(rights_route, 'decide_once', forged)


def _default_gamma():
    from tests.test_rights_lean import GAMMA
    from tests.test_soft_norms_lean import DECIDER
    units = copy.deepcopy(GAMMA)
    units[0]['right']['lines'][0]['norm'].update(mode='default', exception=copy.deepcopy(DECIDER))
    return units


def _decision_declaration(field, value):
    def mutation(row):
        name = row['decisions'][0]['name']
        row['environment_prime']['vocabulary']['predicates'][name][field] = value
    return mutation


PRIME_MUTATIONS = [
    pytest.param(_decision_declaration('arguments', ['person']), id='F19 decision declared with one argument'),
    pytest.param(_decision_declaration('arguments', ['person', 'state']), id='decision declared with swapped sorts'),
    pytest.param(_decision_declaration('description', 'forged'), id='decision declaration description'),
    pytest.param(lambda row: row['environment_prime']['vocabulary']['sorts'].__setitem__(
        'ghost', {'description': 'ghost'}), id='prime extra sort'),
    pytest.param(lambda row: row['environment_prime']['vocabulary']['constants'].__setitem__('ghost', 'person'),
                 id='prime extra constant'),
    pytest.param(lambda row: row['environment_prime'].__setitem__('language', 'ghost'), id='prime language'),
    pytest.param(lambda row: row['environment_prime'].__setitem__('spec_revision', 'ghost'),
                 id='prime spec revision'),
]


@pytest.mark.parametrize('mutation', PRIME_MUTATIONS + [
    pytest.param(lambda row: row['environment_prime']['vocabulary']['rights'].__setitem__('protected', ['ghost']),
                 id='prime rights block'),
])
def test_f19_rights_prime_environment_is_the_request_plus_bound_declarations(monkeypatch, mutation):
    from tests.test_rights_lean import ARREST, env as rights_env
    from ve.rights import RightsEnvironment
    from ve import rights_route
    environment = RightsEnvironment(rights_env(ARREST))
    units = _default_gamma()
    row = copy.deepcopy(rights_route.run_rights_case(environment, units, 'rights-elaborate'))
    mutation(row)
    monkeypatch.setattr(rights_route, 'decide_once', lambda mode, case: row)
    with pytest.raises(CheckerUnavailable):
        rights_route.run_rights_case(environment, units, 'rights-elaborate')


@pytest.mark.parametrize('mutation', PRIME_MUTATIONS)
def test_f19_soft_prime_environment_is_the_request_plus_bound_declarations(monkeypatch, genuine, mutation):
    row = copy.deepcopy(genuine)
    mutation(row)
    with pytest.raises(CheckerUnavailable):
        _document(monkeypatch, row)


def _extra_mechanism(mechanism, conclusion=('top',)):
    def mutation(row):
        entry = row['narrowings'][0]
        entry['mechanisms'].append({'mechanism': mechanism, 'target': f"{entry['rule']}:{mechanism}",
                                    'licence': 'bar' if mechanism == 'bar' else None,
                                    'conclusion': list(conclusion)})
        if 'licensed' in row and mechanism != 'bar':
            row['findings'].append(
                f"UnlicensedLimitation: {mechanism} of rule {entry['rule']} on right {entry['right']}")
            row['licensed'] = False
    return mutation


def _reverse_mechanisms(row):
    row['narrowings'][0]['mechanisms'].reverse()
    if 'licensed' in row:
        row['findings'].reverse()


@pytest.mark.parametrize('units,mutation', [
    pytest.param('strict', _extra_mechanism('bar'), id='F20 bar with no bar requested'),
    pytest.param('strict', _extra_mechanism('exception'), id='F20 exception of a strict line'),
    pytest.param('carve-out', _extra_mechanism('carve-out 01'), id='F20 duplicate carve-out 01'),
    pytest.param('carve-out', _extra_mechanism('carve-out +1'), id='signed carve-out index'),
    pytest.param('carve-out', _extra_mechanism('carve-out 1'), id='repeated carve-out 1'),
    pytest.param('strict', _extra_mechanism('exception no-arbitrary-arrest'), id='line excepted by itself'),
    pytest.param('strict', _extra_mechanism('limitation'), id='repeated limitation'),
    pytest.param('default', _extra_mechanism('blockedBy no-arbitrary-arrest'), id='line blocked by itself'),
    pytest.param('default', _reverse_mechanisms, id='mechanisms out of Lean order'),
])
def test_f20_mechanisms_are_exactly_the_request_implied_slots(monkeypatch, units, mutation):
    from tests.test_rights_lean import ARREST, GAMMA, env as rights_env
    from ve.rights import RightsEnvironment
    from ve import rights_route
    environment = RightsEnvironment(rights_env(ARREST))
    kind, units = units, {'strict': copy.deepcopy(GAMMA), 'default': _default_gamma(),
                          'carve-out': copy.deepcopy(GAMMA)}[units]
    if kind == 'carve-out':
        units[0]['right']['lines'][0]['norm']['unless'] = [['top']]
    rights_route.report_rights(environment, units)
    _rights_relay(monkeypatch, mutation)
    with pytest.raises(CheckerUnavailable):
        rights_route.report_rights(environment, units)


def _rename_rule(old, new):
    """Rename a rule id everywhere a row names it, so only its binding to the request can fail."""
    def mutation(row):
        for line in row.get('lines', []):
            if line['rule'] == old:
                line['rule'] = line['node']['name'] = new
        for entry in row.get('bars', []):
            if entry.get('name') == old:
                entry['name'] = new
        for entry in row.get('derived', []):
            if entry['rule'] == old:
                entry['rule'] = new
        for entry in row['narrowings']:
            if entry['rule'] == old:
                entry['rule'] = new
                for mechanism in entry['mechanisms']:
                    mechanism['target'] = f"{new}:{mechanism['mechanism']}"
    return mutation


def _fan_out_source():
    from tests.test_norms import permission
    from tests.test_rights_lean import env as rights_env, line, norm, right
    predicates = {name: permission('allow', act='{0} torture {1}', args=(bearer, 'person'))
                  for bearer, name in [('state', 'torture_permitted_state'),
                                        ('person', 'torture_permitted_person')]}
    units = [right('r5', [line('claim', norm('no-torture', None, False),
                               fan_out={'state': 'torture_permitted_state',
                                        'person': 'torture_permitted_person'})])]
    return rights_env(predicates), units


def _swap_fan_names(row):
    _rename_rule('rights-fan-1', 'swap')(row)
    _rename_rule('rights-fan-2', 'rights-fan-1')(row)
    _rename_rule('swap', 'rights-fan-2')(row)


@pytest.mark.parametrize('source,mutation', [
    pytest.param('fan-out', _rename_rule('rights-fan-1', 'ghost'), id='F21 invented fan-out rule id'),
    pytest.param('fan-out', _rename_rule('rights-fan-2', 'rights-fan-3'), id='fan-out id out of sequence'),
    pytest.param('fan-out', _swap_fan_names, id='fan-out ids swapped between bearers'),
    pytest.param('line', _rename_rule('no-arbitrary-arrest', 'ghost'), id='authored line renamed'),
    pytest.param('bar', _rename_rule('rights-bar-1', 'rights-bar-9'), id='bar rule id out of sequence'),
])
def test_f21_generated_rule_ids_follow_leans_naming(monkeypatch, source, mutation):
    from tests.test_rights_lean import ARREST, GAMMA, IMPART, env as rights_env, line, norm, right
    from ve.rights import RightsEnvironment
    from ve import rights_route
    raw, units = {
        'fan-out': _fan_out_source,
        'line': lambda: (rights_env(ARREST), copy.deepcopy(GAMMA)),
        'bar': lambda: (rights_env(IMPART, sorts=('person', 'idea'),
                                   rights={'holders': ['person'], 'bearers': ['person']}),
                        [right('r19', [line('liberty', norm('may-impart', 'impart_permitted', True))]),
                         {'bar': {'name': 'b30', 'reading': 'rule'}}]),
    }[source]()
    environment = RightsEnvironment(raw)
    rights_route.report_rights(environment, units)
    _rights_relay(monkeypatch, mutation)
    with pytest.raises(CheckerUnavailable):
        rights_route.report_rights(environment, units)


def _conflict_sorts_relay(route):
    """The public elaboration call of `route` and the patch point of its Lean answer."""
    from tests.test_rights_lean import ARREST, GAMMA, env as rights_env
    from tests.test_soft_norms_lean import env as soft_env
    from ve import rights_route, soft_route
    from ve.rights import RightsEnvironment
    if route == 'rights':
        environment = RightsEnvironment(rights_env(ARREST))
        return (lambda: rights_route.run_rights_case(environment, GAMMA, 'rights-elaborate'),
                rights_route, 'decide_once', 'rights')
    document = softnorms.SoftNormDocument(softnorms.SoftEnvironment(soft_env()),
                                          [should_rule('a', 'x_required', True)])
    return lambda: soft_route.elaborate_soft_document(document), soft_route, '_run', 'soft-norms'


def should_rule(name, predicate, sign):
    from tests.test_soft_norms_lean import should
    return should(name, predicate, sign)


@pytest.mark.parametrize('route,sorts', [
    (route, sorts) for route in ('rights', 'soft') for sorts in ('undeclared', 'empty', 'reversed', 'extended')
    if (route, sorts) != ('soft', 'reversed')])  # the soft fixture's targets have one sort
def test_f22_conflict_target_sorts_are_the_declared_argument_sorts(monkeypatch, route, sorts):
    """F22 (PROBE F22): each conflict target's sorts are its layer's argument sorts, or for a declared
    `req->perm` pair the obligation's (Norms/Replay.lean `targets`); both relays share the binder."""
    from ve.backends.service_schema import check_row
    call, module, attribute, mode = _conflict_sorts_relay(route)
    genuine = call()
    forged = copy.deepcopy(genuine)
    entry = max(forged['conflict_targets'], key=lambda entry: len(set(entry['sorts'])))
    entry['sorts'] = {'undeclared': ['ghost'], 'empty': [], 'reversed': entry['sorts'][::-1],
                      'extended': [*entry['sorts'], entry['sorts'][0]]}[sorts]
    assert forged != genuine

    def reply(*args):
        check_row(mode, forged, args[-1], 0)
        return copy.deepcopy(forged)

    monkeypatch.setattr(module, attribute, reply)
    with pytest.raises(CheckerUnavailable):
        call()


@pytest.mark.parametrize('slot', [99, 0, 2])
def test_f23_an_authored_holder_slot_stays_the_lines_slot(monkeypatch, slot):
    """F23 (PROBE F23): a line's holder slot is Tree.lean `holderSlot`: 0 for a liberty half, the
    authored `holder_slot` when there is one, else the first object slot of the holder sort."""
    from tests.test_rights_lean import ARREST, GAMMA, env as rights_env
    from ve.backends.service_schema import check_row
    from ve.rights import RightsDocument, RightsEnvironment
    from ve import rights_route
    units = copy.deepcopy(GAMMA)
    units[0]['right']['guard'] = ['top']
    units[0]['right']['lines'][0]['holder_slot'] = 1
    environment = RightsEnvironment(rights_env(ARREST))
    assert RightsDocument(environment, units).instances[0]['holder_slot'] == 1
    real = rights_route.decide_once

    def reply(mode, case):
        row = copy.deepcopy(real(mode, case))
        if case['kind'] == 'rights-elaborate':
            row['lines'][0]['holder_slot'] = slot
            check_row(mode, row, case, 0)
        return row

    monkeypatch.setattr(rights_route, 'decide_once', reply)
    with pytest.raises(CheckerUnavailable):
        RightsDocument(environment, units)


def _relicense(licence):
    """Set every carve-out's licence and make the scope findings and `licensed` agree with it."""
    def mutation(row):
        for entry in row['narrowings']:
            for mechanism in entry['mechanisms']:
                if mechanism['mechanism'].startswith('carve-out '):
                    mechanism['licence'] = licence
        if 'licensed' in row:
            row['findings'] = [] if licence else [
                f"UnlicensedLimitation: carve-out 1 of rule {entry['rule']} on right {entry['right']}"
                for entry in row['narrowings'][:1]]
            row['licensed'] = not row['findings']
    return mutation


@pytest.mark.parametrize('cited,licence,kinds', [
    pytest.param(False, licence, kinds, id=f"F24 uncited carve-out as {licence!r} in {'+'.join(kinds)}")
    for licence in ('cited', 'collision', 'certified', 'effect delivered by strict rule no-arbitrary-arrest')
    for kinds in (('rights-scope',), ('rights-elaborate',), ('rights-elaborate', 'rights-scope'))] + [
    pytest.param(True, None, kinds, id=f"F24 cited carve-out unlicensed in {'+'.join(kinds)}")
    for kinds in (('rights-scope',), ('rights-elaborate', 'rights-scope'))])
def test_f24_a_licence_names_a_relation_the_request_holds(monkeypatch, cited, licence, kinds):
    """F24 (PROBE F24): a scope licence is the first relation of Scope.lean the request holds (a citation,
    a colliding right line, a same-effect strict rule), as Run.lean `licence` gives it; a forged
    licence with its UnlicensedLimitation finding dropped (or added) to match is CheckerUnavailable."""
    from tests.test_rights_lean import ARREST, GAMMA, env as rights_env
    from ve.rights import RightsEnvironment
    from ve import rights_route
    units = copy.deepcopy(GAMMA)
    units[0]['right']['lines'][0]['norm']['unless'] = [['top']]
    if cited:
        units[0]['right']['lines'][0]['cites'] = {'unless:1': ['u0']}
        units.append({'source_units': ['u0']})
    environment = RightsEnvironment(rights_env(ARREST))
    genuine = rights_route.report_rights(environment, units)
    assert [m['licence'] for m in genuine['narrowings'][0]['mechanisms']] == [
        'cited' if cited else None, 'limitation']
    assert bool(genuine['unlicensed_limitations']) is not cited
    _rights_relay(monkeypatch, _relicense(licence), kinds)
    with pytest.raises(CheckerUnavailable):
        rights_route.report_rights(environment, units)


def test_a_hit_cited_with_its_finding_dropped_is_unavailable(monkeypatch):
    """Two faults together: a distinction hit marked cited and its ProtectedInCone finding removed. The
    `cited` flag is the line's `guard` citation (Distinction.lean `distinctionHits`), not Lean's to choose."""
    from tests.test_rights_lean import ARREST, GAMMA, env as rights_env
    from ve.rights import RightsEnvironment
    from ve import rights_route
    environment = RightsEnvironment(rights_env(ARREST, rights={
        'holders': ['person'], 'bearers': ['state', 'person'], 'protected': ['arbitrary_arrest']}))
    row = copy.deepcopy(rights_route.run_rights_case(environment, GAMMA, 'rights-elaborate'))
    assert row['findings'] and not row['distinction'][0]['hits'][0]['cited']
    row['distinction'][0]['hits'][0]['cited'] = True
    row['findings'] = []
    monkeypatch.setattr(rights_route, 'decide_once', lambda mode, case: row)
    with pytest.raises(CheckerUnavailable):
        rights_route.run_rights_case(environment, GAMMA, 'rights-elaborate')
