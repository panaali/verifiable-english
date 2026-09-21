"""Seeded synthetic template audit; no calls to model providers or rewards.

Run from the repository root with `uv run python -m experiments.oracle.measure_unknown`.
Every draw stays in the denominator, including fake attacks and UNKNOWN results.
This is an engineering sample, not an estimate on a deployed task distribution.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
import json
from pathlib import Path
import random
import time

from ve.ast import (And, Binary, Bottom, Eq, Exists, Forall, Implies, Not, Or, Top,
                    Unary, Var, formula_to_data)
from ve.attacks import validate_attack
from ve.environment import Environment, LANGUAGE, PROFILE, SPEC_REVISION
from ve.equivalence import Budgets, in_two_variable_fragment, validate_reference
from ve.printer import print_formula


ENV = Environment.from_dict({
    'language': LANGUAGE, 'profile': PROFILE, 'spec_revision': SPEC_REVISION,
    'vocabulary': {'sorts': {'item': {'description': 'An item in the task.'}},
        'predicates': {'p': {'arguments': ['item'], 'description': 'Item has property P.'},
                       'q': {'arguments': ['item'], 'description': 'Item has property Q.'},
                       'r': {'arguments': ['item', 'item'], 'description': 'First item is related to second.'}},
        'constants': {}},
})
TEMPLATES = ('requirement', 'existence', 'pair_requirement', 'related_witness',
             'all_pairs', 'self_relation', 'exclusive', 'unique_property',
             'coverage', 'category_coverage')
MUTATIONS = ('identity', 'double_negation', 'weaken', 'strengthen', 'replace', 'quantifier')


def draw_pair(rng):
    family, mutation = rng.choice(TEMPLATES), rng.choice(MUTATIONS)
    p_name, q_name = rng.sample(('p', 'q'), 2)
    p, q = Unary(p_name, Var(0)), Unary(q_name, Var(0))
    py = Unary(p_name, Var(1))
    edge = Binary('r', Var(1), Var(0))
    if rng.choice((False, True)):
        edge = Binary('r', Var(0), Var(1))
    templates = {
        'requirement': Forall('item', Implies(p, q)),
        'existence': Exists('item', And(p, q)),
        'pair_requirement': Forall('item', Forall('item', Implies(And(py, edge), q))),
        'related_witness': Forall('item', Implies(p, Exists('item', And(edge, q)))),
        'all_pairs': Forall('item', Forall('item', Implies(py, edge))),
        'self_relation': Forall('item', Implies(p, Binary('r', Var(0), Var(0)))),
        'exclusive': Forall('item', Not(And(p, q))),
        'unique_property': And(Exists('item', p), Forall('item', Forall('item',
            Implies(And(py, p), Eq(Var(1), Var(0)))))),
        'coverage': And(Exists('item', p), Exists('item', q)),
        # Three disjoint attribute categories need >=3 objects despite using
        # only one live variable. This tests a real limit of a size-two search.
        'category_coverage': And(Exists('item', And(p, q)),
            And(Exists('item', And(p, Not(q))), Exists('item', Not(p)))),
    }
    faithful = templates[family]
    if mutation == 'identity':
        attacked = faithful
    elif mutation == 'double_negation':
        attacked = Not(Not(faithful))
    elif mutation == 'weaken':
        attacked = Or(faithful, Exists('item', q))
    elif mutation == 'strengthen':
        attacked = And(faithful, Forall('item', q))
    elif mutation == 'replace':
        attacked = rng.choice((Exists('item', q), Forall('item', q), Top(), Bottom()))
    elif type(faithful) in (Forall, Exists):
        attacked = (Exists if type(faithful) is Forall else Forall)(faithful.sort, faithful.body)
    else:
        attacked = Forall('item', Implies(p, q))
    return family, mutation, faithful, attacked


def run(count, seed, budgets):
    rng = random.Random(seed)
    rows = []
    start = time.perf_counter()
    for index in range(count):
        family, mutation, faithful, attacked = draw_pair(rng)
        assert in_two_variable_fragment(faithful) and in_two_variable_fragment(attacked)
        validation = validate_attack(ENV, faithful, attacked, budgets)
        reference = validate_reference(ENV, faithful, budgets)
        result = validation.comparison
        rows.append({
            'id': index, 'template': family, 'mutation': mutation,
            'faithful': print_formula(ENV, faithful) + '.\n',
            'attacked': print_formula(ENV, attacked) + '.\n',
            'faithful_ast': formula_to_data(ENV, faithful), 'attacked_ast': formula_to_data(ENV, attacked),
            'label': result.status, 'relation': result.relation,
            'failed_directions': list(result.failed_directions),
            'directions': {k: {'status': d.status, 'reason': d.reason, 'attempts': list(d.attempts)}
                           for k, d in (('a_implies_b', result.a_implies_b), ('b_implies_a', result.b_implies_a))},
            'attack_status': validation.status, 'attack_reason': validation.reason,
            'classification': validation.classification, 'witnesses': list(validation.witnesses),
            'warnings': list(validation.warnings),
            'reference_status': reference.status, 'reference_reason': reference.reason,
        })
    seconds = time.perf_counter() - start
    labels = Counter(r['label'] for r in rows)
    attacks = Counter(r['attack_status'] for r in rows)
    references = Counter(r['reference_status'] for r in rows)
    different, unknown = labels['DIFFERENT'], labels['UNKNOWN']
    summary = {
        'schema': 've-oracle-template-audit@1', 'seed': seed, 'count': count,
        'budgets': asdict(budgets), 'environment': ENV.to_dict(),
        'distribution': 'Independent uniform draws over 10 template families and 6 mutation families; vocabulary order and relation orientation randomized',
        'denominator': 'All draws, including equivalent/fake attacks and invalid or UNKNOWN references',
        'labels': dict(labels), 'unknown_rate': unknown / count,
        'difference_rate_bounds': [different / count, (different + unknown) / count],
        'equivalence_rate_bounds': [labels['EQUIVALENT'] / count, (labels['EQUIVALENT'] + unknown) / count],
        'attack_validation': dict(attacks), 'attack_unknown_rate': attacks['UNKNOWN'] / count,
        'reference_validation': dict(references),
        'by_template': {name: {'count': sum(r['template'] == name for r in rows),
                              'unknown': sum(r['template'] == name and r['label'] == 'UNKNOWN' for r in rows)}
                        for name in TEMPLATES},
        'elapsed_seconds': round(seconds, 3), 'seconds_per_pair_including_validation': round(seconds / count, 6),
        'limitations': ['Synthetic template distribution; no claim of task representativeness',
                       'Finite search and tableau remain bounded, even within FO2',
                       'Non-vacuity means inhabited sorts and implication guard coverage',
                       'No sampled case is removed from the denominator'],
    }
    return rows, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--count', type=int, default=400)
    parser.add_argument('--seed', type=int, default=20260921)
    parser.add_argument('--output', type=Path, default=Path('experiments/oracle/results'))
    parser.add_argument('--max-domain-size', type=int, default=2)
    parser.add_argument('--max-proof-steps', type=int, default=1000)
    parser.add_argument('--max-models', type=int, default=1000)
    parser.add_argument('--max-evaluations', type=int, default=100_000)
    args = parser.parse_args()
    if args.count < 1:
        parser.error('--count must be positive')
    budgets = Budgets(args.max_proof_steps, args.max_domain_size, args.max_models, args.max_evaluations)
    rows, summary = run(args.count, args.seed, budgets)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'sample.jsonl').write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in rows))
    (args.output / 'summary.json').write_text(json.dumps(summary, sort_keys=True, indent=2) + '\n')
    print(json.dumps(summary, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
