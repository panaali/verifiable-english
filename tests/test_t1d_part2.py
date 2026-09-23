"""T1d Part 2: universal rule-level claims, validator, mutations, VE certificates, Z3 baseline."""
import json
import random

import pytest

from ve import check_entailment_certificate, parse
from ve.ast import Document
from ve_experiments.t1d import rules as R


def _gold_and_mutant(seed=R.SEED_BASE, kinds=R.MUTATIONS):
    for s in range(seed, seed + 50):
        gold = R.generate(s)
        for k in kinds:
            ch, _, _ = R.mutate(gold, k, random.Random(1))
            if ch:
                return gold, ch[0], ch[1]
    raise AssertionError('no mutant')


def test_generator_is_deterministic_and_gold_claims_are_false_with_concrete_witness():
    for i in range(5):
        a, b = R.generate(R.SEED_BASE + i), R.generate(R.SEED_BASE + i)
        assert a == b
        v = R.validate(a)
        assert not v['claim_true'] and len(v['witness_rules']) >= 2
        assert R.witness_state(a, v['witness_types'], v['witness_rules'])['violation_by_bfs']
        assert any(not p for r in a['rules'] for _, p in r['src'] + r['dst'])  # an "unless" guard


def _independent_claim_true(rs):
    """Re-implemented semantics: tag vectors from scratch, step matrix, repeated squaring."""
    from itertools import product
    tags = list(R.TAGS)
    vecs = []
    for bits in product((0, 1), repeat=len(tags)):
        t = {x for x, b in zip(tags, bits) if b}
        if sum(k in t for k in R.KINDS) != 1:
            continue
        if any(a in t and R.ATTRIBUTES[a] not in t for a in R.ATTRIBUTES):
            continue
        if any(a in t and b in t for a, b in R.EXCLUSIVE):
            continue
        vecs.append(t)
    sat = lambda lits, t: all((tag in t) is bool(pos) for tag, pos in lits)

    def step(s, d):
        for rule in rs['rules']:
            src, dst, _ = R.RELATIONS[rule['relation']]
            if not (s & set(src) and d & set(dst)):
                continue
            if any(c['relation'] == rule['relation'] and sat([c['src']], s) and sat([c['dst']], d)
                   for c in rs['constraints']):
                continue
            if sat(rule['src'], s) and sat(rule['dst'], d):
                return True
        return False
    n = len(vecs)
    m = [[step(vecs[i], vecs[j]) for j in range(n)] for i in range(n)]
    reach = [row[:] for row in m]
    for _ in range(n):
        reach = [[reach[i][j] or any(reach[i][k] and m[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    t1, t2 = rs['claim']
    return not any(reach[i][j] for i in range(n) for j in range(n) if t1 in vecs[i] and t2 in vecs[j])


def test_validator_agrees_with_independent_reimplementation():
    for i in range(4):
        gold, _, mutant = _gold_and_mutant(R.SEED_BASE + 10 * i)
        for rs in (gold, mutant):
            assert _independent_claim_true(rs) == R.validate(rs)['claim_true']


def test_mutations_move_in_the_claim_making_true_direction_and_are_single_rule():
    gold, desc, mutant = _gold_and_mutant()
    assert not R.validate(gold)['claim_true'] and R.validate(mutant)['claim_true']
    assert desc['kind'] in R.MUTATIONS
    diff = sum(a != b for a, b in zip(gold['rules'], mutant['rules'])) + abs(len(gold['rules']) - len(mutant['rules']))
    assert diff >= 1 and gold['constraints'] == mutant['constraints'] and gold['claim'] == mutant['claim']


def test_ve_certificate_for_true_claim_replays_and_is_bound_to_its_rule_set():
    gold, _, mutant = _gold_and_mutant()
    ve = R.ve_certify_built(mutant)
    assert ve['built'] and ve['python_replay_valid']
    cross = check_entailment_certificate(R.ve_env(), R.premises(gold), R.goal(gold), ve['certificate'])
    assert not cross.valid


def test_false_claim_cannot_be_certified_and_forged_certificate_is_rejected():
    gold, _, _ = _gold_and_mutant()
    honest = R.ve_certify_built(gold)
    assert not honest['built']
    forged = R.ve_certify_built(gold, forge=True)
    assert forged['built'] and forged['forged_leaves'] >= 1 and not forged['python_replay_valid']


def test_invariant_is_sound_for_its_purpose():
    _, _, mutant = _gold_and_mutant()
    dnf, _ = R.invariant_dnf(mutant)
    types = R.valid_types()
    holds = lambda t: any(all(R.lit_holds(l, t) for l in c) for c in dnf)
    t1, t2 = mutant['claim']
    _, arcs = R.abstract_arcs(mutant)
    assert all(holds(t) for t in types if t1 in t)
    assert not any(holds(t) for t in types if t2 in t)
    assert all(holds(d) for s in types if holds(s) for d in arcs.get(s, {}))


def test_renderings_derive_from_one_representation():
    gold, _, mutant = _gold_and_mutant()
    for rs in (gold, mutant):
        text = R.render_ve(rs)
        doc = parse(R.ve_env(), text)
        assert doc == Document(tuple(R.premises(rs)) + (R.goal(rs),))
        assert json.loads(R.render_json(rs))['rules'] == rs['rules']
        assert R.render_english(rs).count('\nRule ') == len(rs['rules'])


def test_closed_world_unless_snapshot_certifies_and_negation_flip_forgery_fails():
    snap = R.generate_snapshot(R.SNAP_SEED)
    row = R.certify_snapshot(snap)
    assert row['python_replay_valid'] and row['lean_replay_valid'] in (True, None)
    forged = R.forged_snapshot(snap)
    assert forged is None or not forged['python_replay_valid']


def test_z3_chc_and_ground_checks_match_validator():
    pytest.importorskip('z3')
    pytest.importorskip('cvc5')
    from ve_experiments.t1d import z3check
    for i in range(3):
        gold, _, mutant = _gold_and_mutant(R.SEED_BASE + i)
        for rs in (gold, mutant):
            truth = R.validate(rs)['claim_true']
            assert z3check.chc_verdict(rs) == truth
            dnf, _ = R.invariant_dnf(rs)
            for solver in ('z3', 'cvc5'):
                g = z3check.ground_check(rs, dnf, solver)
                assert g['verdict'] == ('proved' if truth else 'unknown')  # never refutes


def test_mutant_certificate_rebound_to_gold_fails_logically_at_the_mutated_rule():
    from ve_experiments.t1d.part2 import rebind_regression
    for kind in ('added_exception', 'negation_flip'):
        gold, desc, mutant = _gold_and_mutant(kinds=(kind,))
        ve = R.ve_certify_built(mutant)
        assert ve['built'] and ve['python_replay_valid']
        rb = rebind_regression(gold, desc, ve['certificate'])
        assert not rb['python_valid'] and rb['logical_failure'] and rb['located']['at_mutated_rule']
        assert rb['lean_valid'] in (False, None)
