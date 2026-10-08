"""Seeded closure differential extension of conformance/fuzz.py.

Every pair contains Reach. Cases mix random typed bodies with directed graph
motifs and forced captures/nesting. JSONL replay and greedy failure reduction
stay under rust/target; no expected values are consumed by the Rust evaluator.
Rust reads no source text and prints no identities: each case goes to its
`evaluate-budgeted` kind, as `ve/evaluate.py` sends it.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from conformance.fuzz import mismatch, reduce_failure
from ve import Environment, FiniteModel, evaluate
from ve.ast import (And, Binary, Body, Bottom, Const, Document, Eq, Exists,
                    Forall, Implies, Named, Not, Or, Reach, Top, Unary, Var,
                    document_to_data)


def generate(count=3000, seed=20260924):
    rng = random.Random(seed)
    for i in range(count):
        n, m = rng.randrange(5), rng.randrange(4)
        domains = {'node': [f'e{j}' for j in range(n)], 'other': [f'e{j}' for j in range(m)]}
        constants = {'start': {'sort': 'node', 'description': 'Source.'},
                     'end': {'sort': 'node', 'description': 'Destination.'}} if n and i % 3 else {}
        env = Environment({'language': 've.core@0.1', 'profiles': ['closure@0', 'relational-fol@0'],
            'spec_revision': 've-v0.1-closure-2026-09-21', 'vocabulary': {
                'sorts': {s: {'description': s} for s in domains}, 'constants': constants,
                'predicates': {'edge': {'arguments': ['node', 'node'], 'description': 'Edge.'},
                               'marked': {'arguments': ['node'], 'description': 'Marked.'},
                               'flag': {'arguments': ['other'], 'description': 'Flag.'},
                               'link': {'arguments': ['node', 'other'], 'description': 'Link.'}}}})
        nodes = domains['node']
        motif = i % 5
        if motif == 0:
            edges = []
        elif motif == 1:
            edges = [[x, x] for x in nodes]
        elif motif == 2:
            edges = [[x, nodes[(j + 1) % n]] for j, x in enumerate(nodes)]
        elif motif == 3:
            edges = [[nodes[j], nodes[j + 1]] for j in range(n - 1)]
        else:
            edges = [[x, y] for x in nodes for y in nodes if rng.randrange(2)]
        relations = {p: [list(row) for row in itertools.product(*(domains[s] for s in d.arguments))
                         if rng.randrange(2)] for p, d in env.predicates.items()}
        relations['edge'] = edges
        model = FiniteModel.from_dict(env, {'complete': True, 'domains': domains,
            'constants': {c: rng.choice(nodes) for c in constants}, 'relations': relations})

        def terms(sort, context):
            return ([Const(c) for c, d in env.constants.items() if d.sort == sort]
                    + [Var(j) for j, s in enumerate(context) if s == sort])

        def formula(depth, context):
            available = [s for s in domains if terms(s, context)]
            tag = rng.randrange(10) if depth else rng.randrange(4)
            if tag == 0 or not available:
                return rng.choice([Top(), Bottom()])
            sort = rng.choice(available)
            ts = terms(sort, context)
            if tag == 1:
                return Eq(rng.choice(ts), rng.choice(ts))
            if tag == 2:
                return Unary('marked' if sort == 'node' else 'flag', rng.choice(ts))
            if tag == 3:
                return Binary('edge', rng.choice(ts), rng.choice(ts)) if sort == 'node' else Eq(*[rng.choice(ts) for _ in range(2)])
            if tag == 4:
                return Not(formula(depth - 1, context))
            if tag in (5, 6):
                s = rng.choice(list(domains))
                return (Forall if tag == 5 else Exists)(s, formula(depth - 1, (s, *context)))
            if tag in (7, 8):
                return rng.choice([And, Or, Implies])(formula(depth - 1, context), formula(depth - 1, context))
            edge = (Named('edge') if sort == 'node' and rng.randrange(2) else
                    Body(sort, formula(depth - 1, (sort, sort, *context))))
            return Reach(rng.choice(['plus', 'star']), edge, rng.choice(ts), rng.choice(ts))

        mode = i % 6
        scope = ('node', 'node')
        edge = Named('edge')
        if mode == 1:
            edge = Body('node', Binary('edge', Var(1), Var(0)))
        elif mode == 2:
            edge = Body('node', And(Binary('edge', Var(1), Var(0)), Not(Eq(Var(0), Var(2)))))
        elif mode == 3:
            edge = Body('node', Reach(rng.choice(['plus', 'star']),
                Body('node', And(Binary('edge', Var(1), Var(0)), Not(Eq(Var(0), Var(4))))), Var(1), Var(0)))
        elif mode == 4:
            edge = Body('node', formula(3, ('node', 'node', *scope)))
        elif mode == 5:
            scope = (*scope, 'other')
            edge = Body('node', And(Binary('edge', Var(1), Var(0)), Unary('flag', Var(4))))
        ts = terms('node', scope)
        f = Reach(rng.choice(['plus', 'star']), edge, rng.choice(ts), rng.choice(ts))
        f = rng.choice([Forall, Exists])('node', rng.choice([Forall, Exists])('node', f))
        if mode == 5:
            f = rng.choice([Forall, Exists])('other', f)
        if i % 7 == 0:
            f = Not(f)
        doc = Document((f,))
        value = evaluate(env, f, model, trace=False).value
        assert type(value) is bool, (i, 'Python exhausted')
        yield {'id': f'closure_fuzz_{seed}_{i}', 'kind': 'evaluate-budgeted', 'environment': env.to_dict(),
               'model': model.to_dict(), 'ast': document_to_data(env, doc), 'expected': [value]}


def features(case):
    counts = {'reach': 0, 'body': 0, 'nested': False}
    def walk(data, inside=False):
        if not isinstance(data, list) or not data:
            return
        reach = data[0] == 'reach'
        if reach:
            counts['reach'] += 1
            counts['body'] += data[2][0] == 'body'
            counts['nested'] |= inside
        for child in data:
            if isinstance(child, list):
                walk(child, inside or reach)
    walk(case['ast'])
    return counts


def run(executable, count, seed, output, summary_path=None):
    cases = list(generate(count, seed))
    output.parent.mkdir(parents=True, exist_ok=True)
    raw = ''.join(json.dumps(c, separators=(',', ':')) + '\n' for c in cases)
    output.write_text(raw)
    process = subprocess.run([str(executable), 'jsonl', str(output)], text=True,
                             capture_output=True,
                             timeout=int(os.environ.get("VE_CONFORMANCE_HANG_TIMEOUT", "180")))
    results = [json.loads(line) for line in process.stdout.splitlines()]
    assert len(results) == count, (len(results), count, process.stderr)
    for case, result in zip(cases, results, strict=True):
        if mismatch(case, result):
            failure = output.with_name('closure-fuzz-minimal.json')
            failure.write_text(json.dumps(reduce_failure(case, executable), indent=2) + '\n')
            raise AssertionError(f'Disagreement: {case["id"]}; reduced replay: {failure}')
    assert process.returncode == 0, process.stderr
    fs = [features(c) for c in cases]
    assert all(f['reach'] for f in fs)
    summary = {'seed': seed, 'cases': count, 'agreements': count,
        'true': sum(c['expected'][0] for c in cases), 'false': sum(not c['expected'][0] for c in cases),
        'empty_domain_cases': sum(any(not d for d in c['model']['domains'].values()) for c in cases),
        'body_cases': sum(bool(f['body']) for f in fs), 'nested_cases': sum(f['nested'] for f in fs),
        'forced_outer_parameter_cases': sum(i % 6 in (2, 3, 5) for i in range(count)),
        'self_loop_models': sum(any(x == y for x, y in c['model']['relations']['edge']) for c in cases),
        'forced_cycle_models': sum(i % 5 == 2 and len(c['model']['domains']['node']) > 1 for i, c in enumerate(cases)),
        'jsonl_sha256': hashlib.sha256(raw.encode()).hexdigest()}
    (summary_path or output.with_suffix('.summary.json')).write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary))
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rust', type=Path, default=ROOT/'rust/target/release/ve')
    parser.add_argument('--count', type=int, default=3000)
    parser.add_argument('--seed', type=int, default=20260924)
    parser.add_argument('--output', type=Path, default=ROOT/'rust/target/closure-fuzz.jsonl')
    parser.add_argument('--summary', type=Path)
    args = parser.parse_args()
    run(args.rust.resolve(), args.count, args.seed, args.output, args.summary)
