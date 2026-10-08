"""Seeded Python/Rust differential fuzzing with JSONL replay and greedy reduction.

Run: python conformance/fuzz.py --rust rust/target/release/ve --count 5000
The generated inputs and a failure, if any, stay under rust/target/. Rust reads no source
text: each one-statement case goes to its `evaluate-budgeted` kind, as `ve/evaluate.py` sends it.
"""
from __future__ import annotations
import argparse
import copy
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
from ve import Environment, FiniteModel, evaluate
from ve.ast import (And, Binary, Bottom, Const, Document, Eq, Exists, Forall,
                    Implies, Not, Or, Top, Unary, Var, document_from_data, document_to_data)
from ve.errors import VEError


def generate(count=5000, seed=20260922):
    rng = random.Random(seed)
    for i in range(count):
        sorts = ['item', 'person', 'service'][:rng.randint(1, 3)]
        vocabulary = {'sorts': {s: {'description': f'A {s}.'} for s in sorts},
                      'predicates': {}, 'constants': {}}
        for j, sort in enumerate(sorts):
            vocabulary['predicates'][f'marked{j}'] = {'arguments': [sort], 'description': 'Marked.'}
            vocabulary['predicates'][f'edge{j}'] = {'arguments': [sort, rng.choice(sorts)], 'description': 'An ordered edge.'}
            for k in range(rng.randrange(3)):
                vocabulary['constants'][f'named{j}_{k}'] = {'sort': sort, 'description': 'A named element.'}
        env = Environment.from_dict({'language': 've.core@0', 'profile': 'relational-fol@0',
                                     'spec_revision': 've-v0-draft-2026-09-20', 'vocabulary': vocabulary})
        domains = {s: ['same', 'next', 'last'][:rng.randint(int(any(d.sort == s for d in env.constants.values())), 3)] for s in sorts}
        model = FiniteModel.from_dict(env, {'complete': True, 'domains': domains,
            'constants': {c: rng.choice(domains[d.sort]) for c, d in env.constants.items()},
            'relations': {p: [list(row) for row in itertools.product(*(domains[s] for s in d.arguments))
                               if rng.randrange(2)] for p, d in env.predicates.items()}})
        def formula(depth, context):
            def terms(s):
                return [Const(c) for c, d in env.constants.items() if d.sort == s] + [Var(j) for j, t in enumerate(context) if t == s]
            def atom():
                available = [s for s in sorts if terms(s)]
                predicates = [p for p, d in env.predicates.items() if all(terms(s) for s in d.arguments)]
                kind = rng.randrange(4)
                if kind == 0 or not available: return rng.choice([Top(), Bottom()])
                if kind == 1 or not predicates:
                    s = rng.choice(available)
                    return Eq(rng.choice(terms(s)), rng.choice(terms(s)))
                p = rng.choice(predicates)
                ts = [rng.choice(terms(s)) for s in env.predicates[p].arguments]
                return Unary(p, ts[0]) if len(ts) == 1 else Binary(p, *ts)
            kind = rng.randrange(8) if depth else 0
            if kind < 2: return atom()
            if kind == 2: return Not(formula(depth-1, context))
            if kind < 6: return [And, Or, Implies][kind-3](formula(depth-1, context), formula(depth-1, context))
            s = rng.choice(sorts)
            return [Forall, Exists][kind-6](s, formula(depth-1, (s,) + context))
        f = formula(rng.randint(1, 5), ())
        # Half the cases force a bound variable into the generated context.
        if i % 2 == 0:
            s = rng.choice(sorts)
            f = rng.choice([Forall, Exists])(s, formula(rng.randint(1, 4), (s,)))
        doc = Document((f,))
        value = evaluate(env, f, model, max_trace_nodes=1_000_000).value
        assert value is not None
        yield {'id': f'fuzz_{seed}_{i}', 'kind': 'evaluate-budgeted', 'environment': env.to_dict(),
               'model': model.to_dict(), 'ast': document_to_data(env, doc), 'expected': [value]}


def refresh(case):
    env = Environment.from_dict(case['environment'])
    model = FiniteModel.from_dict(env, case['model'])
    doc = document_from_data(env, case['ast'])
    case['expected'] = [evaluate(env, f, model, max_trace_nodes=1_000_000).value for f in doc.formulas]
    return case


def mismatch(case, out):
    """Rust's document value on the model differs from Python's (one statement per case)."""
    return (out.get('status') not in ('Satisfied', 'Violated') or out.get('id') != case['id']
            or out.get('value') != all(case['expected']))


def reduce_failure(case, executable):
    """Greedy local minimization under type checking; not globally minimal."""
    def shrinks(node):
        yield ['top']; yield ['bottom']
        for j, child in enumerate(node[1:], 1):
            if isinstance(child, list) and child and child[0] not in ('var', 'const'):
                yield child
                for replacement in shrinks(child):
                    candidate = copy.deepcopy(node); candidate[j] = replacement; yield candidate
    def candidates(current):
        for f in shrinks(current['ast'][0]):
            c = copy.deepcopy(current); c['ast'] = [f]; yield c
        for p, rows in current['model']['relations'].items():
            for j in range(len(rows)):
                c = copy.deepcopy(current); del c['model']['relations'][p][j]; yield c
        env = Environment.from_dict(current['environment'])
        for s, domain in current['model']['domains'].items():
            for entity in domain:
                if any(d.sort == s and current['model']['constants'][n] == entity for n,d in env.constants.items()): continue
                c = copy.deepcopy(current); c['model']['domains'][s].remove(entity)
                for p, d in env.predicates.items():
                    c['model']['relations'][p] = [row for row in c['model']['relations'][p]
                        if not any(t == s and x == entity for x,t in zip(row,d.arguments))]
                yield c
    case = copy.deepcopy(case)
    while True:
        for candidate in candidates(case):
            try: candidate = refresh(candidate)
            except VEError: continue
            if len(json.dumps(candidate)) >= len(json.dumps(case)): continue
            run = subprocess.run([str(executable), 'conformance'], input=json.dumps(candidate), text=True,
                                 capture_output=True,
                                 timeout=int(os.environ.get("VE_CONFORMANCE_HANG_TIMEOUT", "10")))
            if run.stdout and mismatch(candidate, json.loads(run.stdout)[0]):
                case = candidate; break
        else: return case


def run(executable, count, seed, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    cases = list(generate(count, seed))
    raw = ''.join(json.dumps(c, separators=(',', ':')) + '\n' for c in cases)
    output.write_text(raw)
    process = subprocess.run([str(executable), 'jsonl', str(output)], text=True,
                             capture_output=True,
                             timeout=int(os.environ.get("VE_CONFORMANCE_HANG_TIMEOUT", "180")))
    results = [json.loads(line) for line in process.stdout.splitlines()]
    if len(results) != len(cases): raise AssertionError(f'Rust produced {len(results)}/{len(cases)} records: {process.stderr}')
    for case, result in zip(cases, results, strict=True):
        if mismatch(case, result):
            minimal = reduce_failure(case, executable)
            failure = output.with_name('fuzz-minimal.json'); failure.write_text(json.dumps(minimal, indent=2)+'\n')
            raise AssertionError(f'Disagreement: {case["id"]}; locally minimized replay: {failure}')
    assert process.returncode == 0, process.stderr
    summary = {'seed': seed, 'cases': count, 'formulas': count, 'agreements': count,
               'true': sum(c['expected'][0] for c in cases), 'false': sum(not c['expected'][0] for c in cases),
               'empty_domain_cases': sum(any(not d for d in c['model']['domains'].values()) for c in cases),
               'jsonl_sha256': hashlib.sha256(raw.encode()).hexdigest()}
    output.with_suffix('.summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary))
    return summary


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rust', type=Path, default=ROOT/'rust/target/release/ve')
    p.add_argument('--count', type=int, default=5000)
    p.add_argument('--seed', type=int, default=20260922)
    p.add_argument('--output', type=Path, default=ROOT/'rust/target/fuzz.jsonl')
    args = p.parse_args(); run(args.rust.resolve(), args.count, args.seed, args.output)
