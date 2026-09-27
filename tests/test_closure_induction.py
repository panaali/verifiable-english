"""Induction replay, hostile certificates, compatibility and cyclic policies."""
import copy
import json
from subprocesses import HANG_TIMEOUT
import subprocess
from pathlib import Path

import pytest

from conformance.certificates import envelope, invoke, replay_python
from conformance.closure_certificates import environment, positive_cases as old_cases
from conformance.induction import positive_cases, forged_cases, policy_cases, schema_cases
from ve import (And, Binary, Const, Document, FiniteModel, Forall, Implies, Named,
                Reach, Unary, Var, check_entailment_certificate, evaluate,
                formula_from_data, prove_entailment)
from ve.closure import induction_step
from ve.environment import Environment

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / 'lean/.lake/build/bin/ve_conformance'


def test_induction_python_lean_differential():
    good, bad = positive_cases(), forged_cases()
    assert len(good) == 36 and len(bad) == 17
    rows = invoke(LEAN, good + bad)
    assert [row['valid'] for row in rows] == [True] * len(good) + [False] * len(bad)


def test_previous_closure_version_replays_all_original_rules():
    cases, _ = old_cases()
    for case in cases:
        case['certificate']['checker_version'] = 've-tableau-closure-checker@0'
        assert replay_python(case)
    assert all(row['valid'] for row in invoke(LEAN, cases))


def test_all_committed_mini_paper_certificates_still_replay_unchanged():
    from ve import parse
    directory = ROOT / 'usecases/math-mini-paper'
    cases = []
    for path in sorted((directory / 'theorems').glob('*/certificate.json')):
        if not path.read_bytes().strip():
            continue
        cert = json.loads(path.read_bytes())
        closure = cert['checker_version'].startswith('ve-tableau-closure-')
        env = Environment(json.loads((directory / ('environment-closure.json' if closure else 'environment.json')).read_text()))
        ps = parse(env, (path.parent / 'premises.ve').read_text()).formulas if (path.parent / 'premises.ve').read_text().strip() else ()
        goal = parse(env, (path.parent / 'conclusion.ve').read_text()).formulas[0]
        assert check_entailment_certificate(env, ps, goal, cert).valid, path
        cases.append(envelope(path.parent.name, env, ps, goal, cert))
    assert len(cases) == 15
    assert all(row['valid'] for row in invoke(LEAN, cases))


@pytest.mark.parametrize('kind', ['plus', 'star'])
def test_supplied_invariant_proves_universal_rule_without_constants(kind):
    raw = environment().to_dict()
    raw['vocabulary']['constants'] = {}
    env = Environment(raw)
    p, edge = Unary('p', Var(0)), Named('rel')
    goal = Forall('item', Implies(And(p, induction_step('item', edge, p)),
        Forall('item', Implies(Reach(kind, edge, Var(1), Var(0)), p))))
    result = prove_entailment(env, [], goal, invariants=[p], max_steps=1000)
    assert result.status == 'Found', result
    assert 'closure-induct@1' in json.dumps(result.certificate)
    assert invoke(LEAN, [envelope('universal_' + kind, env, [], goal, result.certificate)])[0]['valid']
    model = FiniteModel.from_dict(env, {'complete': True, 'domains': {s: [] for s in env.sorts},
                                       'constants': {}, 'relations': {p: [] for p in env.predicates}})
    assert evaluate(env, goal, model).value is True


def test_policy_has_a_model_with_a_real_cycle_and_detects_broken_preservation():
    for case in policy_cases():
        env = Environment(case['environment'])
        ps = [formula_from_data(env, f) for f in case['premises']]
        goal = formula_from_data(env, case['conclusion'])
        raw = {'complete': True, 'domains': {'entity': ['g1', 'g2', 'resource']},
               'constants': {x: x for x in ('g1', 'g2', 'resource')},
               'relations': {'group': [['g1'], ['g2']], 'link': [['g1', 'g2'], ['g2', 'g1']]}}
        model = FiniteModel.from_dict(env, raw)
        assert all(evaluate(env, f, model).value is True for f in [*ps, goal])
        assert evaluate(env, Reach('plus', Named('link'), Const('g1'), Const('g1')), model).value is True
        raw['relations']['link'].append(['g2', 'resource'])
        broken = FiniteModel.from_dict(env, raw)
        assert all(evaluate(env, f, broken).value is True for f in ps[:4] + ps[5:])
        assert evaluate(env, goal, broken).value is False
        # A real refutation after dropping the preservation hypothesis.
        from ve import check_countermodel
        assert check_countermodel(env, ps[:4] + ps[5:], goal, broken).valid


def test_captured_invariant_cannot_swap_local_and_ambient_parameters():
    case = copy.deepcopy(schema_cases()[-1])
    node = case['certificate']['trace']
    while node['rule'] != 'closure-induct@1':
        node = node['children'][0]
    # Under Exists, index 2 is the captured parameter, index 1 the induction node.
    node['invariant'][2][1][2] = ['var', 1]
    assert not replay_python(case)
    assert not invoke(LEAN, [case])[0]['valid']


def test_negative_index_rejected_at_both_wire_boundaries():
    case = schema_cases()[0]
    case['certificate']['trace']['at'] = -1
    assert not replay_python(case)
    proc = subprocess.run([str(LEAN), 'check-certificate'], input=json.dumps(case),
                          capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert proc.returncode != 0


def test_induction_budget_and_profile_gates():
    case = schema_cases()[0]
    env = Environment(case['environment'])
    ps = [formula_from_data(env, f) for f in case['premises']]
    goal = formula_from_data(env, case['conclusion'])
    for budget in (0, 1, 3):
        result = check_entailment_certificate(env, ps, goal, case['certificate'], max_steps=budget)
        assert not result.valid and result.status == 'ResourceLimit'
    from conformance.certificates import environment as v0
    with pytest.raises(ValueError, match='closure@0'):
        prove_entailment(v0(), [], Unary('p', Const('a')), invariants=[Unary('p', Var(0))])
    # Even an already contradictory branch cannot bypass the invariant's AST
    # budget. Use a shallow balanced tree to isolate node count from depth.
    from ve.ast import Bottom
    from ve.entailment import _binding
    ps = [ps[0], Bottom()]
    invariant = ['top']
    for _ in range(13):
        invariant = ['and', invariant, invariant]
    cert = {**_binding(env, tuple(ps), Bottom()), 'trace': {
        'rule': 'closure-induct@1', 'at': 0, 'sort': 'item', 'invariant': invariant,
        'children': [{'rule': 'close'}] * 3}}
    checked = check_entailment_certificate(env, ps, Bottom(), cert)
    assert not checked.valid and checked.status == 'ResourceLimit'
    row = invoke(LEAN, [envelope('oversized_invariant', env, ps, Bottom(), cert)])[0]
    assert not row['valid'] and 'node count' in row['error']


def test_induction_schema_in_all_two_node_graphs_and_unary_interpretations():
    env = environment()
    p, edge = Unary('p', Var(0)), Named('rel')
    step = induction_step('item', edge, p)
    for edges in range(16):
        for members in range(4):
            raw = {'complete': True, 'domains': {'item': ['x', 'y'], 'place': []},
                   'constants': {c: ('x' if d.sort == 'item' else 'z') for c, d in env.constants.items()},
                   'relations': {q: [] for q in env.predicates}}
            raw['domains']['place'] = ['z']
            raw['relations']['p'] = [[v] for i, v in enumerate(('x', 'y')) if members & (1 << i)]
            raw['relations']['rel'] = [[x, y] for i, (x, y) in enumerate(
                ((x, y) for x in ('x', 'y') for y in ('x', 'y'))) if edges & (1 << i)]
            model = FiniteModel.from_dict(env, raw)
            for kind in ('plus', 'star'):
                rule = Forall('item', Implies(And(p, step),
                    Forall('item', Implies(Reach(kind, edge, Var(1), Var(0)), p))))
                assert evaluate(env, rule, model).value is True
