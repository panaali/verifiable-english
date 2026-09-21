"""Serial fixed-family benchmark; run directly (not collected by pytest).

Baseline: --baseline-root /private/tmp/ve-prover-fair-baseline (git archive
7a85024 ve). Both runs use this same generator, budgets and external deadline.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
import platform
from pathlib import Path
import random
import signal
import statistics
import sys
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--baseline-root')
parser.add_argument('--output', required=True)
parser.add_argument('--variants', type=int, default=10)
args = parser.parse_args() if __name__ == '__main__' else None
if args and args.baseline_root:
    sys.path.insert(0, args.baseline_root)
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ve.ast import (And, Binary, Bottom, Const, Eq, Exists, Forall, Implies,
                    Not, Or, Top, Unary, Var, formula_to_data)
from ve.entailment import check_entailment_certificate
from ve.environment import Environment, LANGUAGE, PROFILE, SPEC_REVISION
from ve.equivalence import Budgets, compare
from ve.search import check_countermodel


def environment(constants=False):
    return Environment.from_dict({'language': LANGUAGE, 'profile': PROFILE,
        'spec_revision': SPEC_REVISION, 'vocabulary': {
            'sorts': {'item': {'description': 'Item.'}},
            'predicates': {**{p: {'arguments': ['item'], 'description': p} for p in ('p', 'q', 's')},
                           'r': {'arguments': ['item', 'item'], 'description': 'R.'}},
            'constants': {'a': {'sort': 'item', 'description': 'A.'}} if constants else {}}})


def cases(variants=10):
    rng = random.Random(20260921)
    for depth in range(1, 6):
        for variant in range(variants):
            names = rng.sample(['p', 'q', 's'], 3)
            p, q, r = [Unary(name, Var(0)) for name in names]
            # Half the variants depend on every binder, including binary
            # relations. Quantifier depth must not just count vacuous prefixes.
            if variant % 2:
                for index in range(depth):
                    p = And(p, Binary('r', Var(index), Var((index + 1) % depth)))
                q = Or(Unary(names[1], Var(depth - 1)), Binary('r', Var(0), Var(depth - 1)))
            prefix = [rng.choice([Forall, Exists]) for _ in range(depth)]
            def wrap(body, constructors=prefix):
                for ctor in reversed(constructors):
                    body = ctor('item', body)
                return body
            env = environment()
            rows = [
                ('commutation', wrap(And(p, q)), wrap(And(q, p))),
                ('association', wrap(Or(p, Or(q, r))), wrap(Or(Or(p, q), r))),
                ('de_morgan', wrap(Not(And(p, q))), wrap(Or(Not(p), Not(q)))),
                ('contraposition', wrap(Implies(p, q)), wrap(Implies(Not(q), Not(p)))),
                ('quantifier_duals', wrap(p), Not(wrap(Not(p), [Exists if c is Forall else Forall for c in prefix]))),
                ('double_negation', wrap(p), wrap(Not(Not(p)))),
                ('vacuous_quantifiers', wrap(Top()), Top()),
                ('near_misses', wrap(And(p, q)), wrap(Or(p, q))),
            ]
            # Move a CLOSED side formula across the outer quantifier; universal
            # conjunction and existential disjunction have real empty-sort traps.
            side = Exists('item', Unary(names[1], Var(0)))
            inner = wrap(p, prefix[1:])
            # Shift only the free outer variable of inner under the same binder:
            # side is closed and can be used verbatim on either side.
            ctor = prefix[0]
            connective = And if ctor is Forall else Or
            rows += [('prenex_empty_trap', ctor('item', connective(inner, side)),
                      connective(ctor('item', inner), side)),
                     ('unprenexing', connective(ctor('item', inner), Not(side)),
                      ctor('item', connective(inner, Not(side))))]
            # Both prenex families deliberately retain empty-sort near misses.
            if depth >= 2:
                same = rng.choice([Forall, Exists])
                constructors = [same, same] + prefix[2:]
                left = Binary('r', Var(depth - 1), Var(depth - 2))
                right = Binary('r', Var(depth - 2), Var(depth - 1))
                rows.append(('same_quantifier_swap', wrap(left, constructors), wrap(right, constructors)))
            else:
                rows.append(('same_quantifier_distribution', Forall('item', And(p, q)),
                             And(Forall('item', p), Forall('item', q))))
            for family, a, b in rows:
                yield family, depth, variant, env, a, b
            # One-point rules use a declared constant, so this family correctly
            # excludes empty domains. Other families have no constants.
            point = And(Eq(Var(0), Const('a')), Unary(names[0], Var(0)))
            a = wrap(point, prefix[:-1] + [Exists])
            b = Unary(names[0], Const('a'))
            b = wrap(b, prefix[:-1])
            if depth >= 2 and variant % 2:
                a = wrap(Exists('item', And(Eq(Var(0), Var(1)), Binary('r', Var(1), Var(0)))), prefix[:-1])
                b = wrap(Binary('r', Var(0), Var(0)), prefix[:-1])
                yield 'one_point', depth, variant, env, a, b
            else:
                yield 'one_point', depth, variant, environment(True), a, b
    env = environment()
    p = Unary('p', Var(0))
    yield 'review_minimal_1', 2, 0, env, Forall('item', Exists('item', Unary('q', Var(1)))), Forall('item', Exists('item', Not(Not(Unary('q', Var(1))))))
    yield 'review_minimal_2', 2, 0, env, Exists('item', Forall('item', p)), Exists('item', Not(Exists('item', Not(p))))


class PairTimeout(Exception):
    pass


def alarm(*_):
    raise PairTimeout


def percentile(values, proportion):
    return sorted(values)[math.ceil(proportion * len(values)) - 1] if values else None


def quantifier_depth(formula):
    if type(formula) in (Forall, Exists): return 1 + quantifier_depth(formula.body)
    if type(formula) is Not: return quantifier_depth(formula.body)
    if type(formula) in (And, Or, Implies):
        return max(quantifier_depth(formula.left), quantifier_depth(formula.right))
    return 0


def summarize(rows):
    times = [row['seconds'] for row in rows]
    sizes = [size for row in rows for size in row['certificate_bytes']]
    unknown = sum(row['status'] == 'UNKNOWN' for row in rows)
    return {'pairs': len(rows), 'unknown': unknown, 'unknown_percent': 100 * unknown / len(rows),
            'median_ms': 1000 * statistics.median(times), 'p95_ms': 1000 * percentile(times, .95),
            'certificate_count': len(sizes), 'certificate_median_bytes': statistics.median(sizes) if sizes else None,
            'certificate_p95_bytes': percentile(sizes, .95), 'timeouts': sum(row['timeout'] for row in rows)}


def main():
    signal.signal(signal.SIGALRM, alarm)
    rows = []
    budgets = Budgets(max_proof_steps=10000, max_domain_size=2, max_models=10000, max_evaluations=100000)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.with_suffix('.jsonl').open('w') as stream:
        for family, depth, variant, env, a, b in cases(args.variants):
            inputs = {'environment': env.to_dict(), 'a': formula_to_data(env, a), 'b': formula_to_data(env, b)}
            depth = max(quantifier_depth(a), quantifier_depth(b))
            row = {'family': family, 'depth': depth, 'variant': variant, **inputs,
                   'input_sha256': hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest(),
                   'certificate_bytes': [], 'timeout': False}
            started = time.perf_counter()
            try:
                signal.setitimer(signal.ITIMER_REAL, 2.0)
                result = compare(env, a, b, budgets)
                elapsed = time.perf_counter() - started
                signal.setitimer(signal.ITIMER_REAL, 0)
                row.update(status=result.status, relation=result.relation,
                           relation_detail=getattr(result, 'relation_detail', None), seconds=elapsed,
                           directions=[result.a_implies_b.status, result.b_implies_a.status])
                for label, left, right in [('a_implies_b', a, b), ('b_implies_a', b, a)]:
                    certificate = result.certificates.get(label)
                    if certificate:
                        assert check_entailment_certificate(env, (left,), right, certificate).valid
                        row['certificate_bytes'].append(len(json.dumps(certificate, separators=(',', ':')).encode()))
                    certificate = getattr(result, 'nonempty_certificates', {}).get(label)
                    if certificate:
                        conditions = tuple(Exists(sort, Top()) for sort in result.nonempty_sorts)
                        assert check_entailment_certificate(env, (left, *conditions), right, certificate).valid
                        row['certificate_bytes'].append(len(json.dumps(certificate, separators=(',', ':')).encode()))
                for label, model in result.models.items():
                    left, right = (a, b) if label == 'a_not_implies_b' else (b, a)
                    assert check_countermodel(env, (left,), right, model).valid
            except PairTimeout:
                row.update(status='UNKNOWN', seconds=time.perf_counter() - started, timeout=True)
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
            rows.append(row)
            stream.write(json.dumps(row, sort_keys=True) + '\n'); stream.flush()
            if len(rows) % 100 == 0:
                print(f'{len(rows)} pairs complete', flush=True)
    import ve.entailment, ve.equivalence, ve.attacks
    summary = {'seed': 20260921, 'seconds_per_pair': 2, 'variants': args.variants,
               'python': sys.version, 'platform': platform.platform(),
               'implementation_sha256': {module.__name__: hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
                                         for module in (ve.entailment, ve.equivalence, ve.attacks)},
               'baseline_root': args.baseline_root, 'overall': summarize(rows),
               'by_depth': {str(depth): summarize([r for r in rows if r['depth'] == depth]) for depth in range(1, 6)},
               'depth_ge_3': summarize([r for r in rows if r['depth'] >= 3]),
               'by_family': {family: summarize([r for r in rows if r['family'] == family]) for family in sorted({r['family'] for r in rows})}}
    output.write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary['overall'], indent=2))


if __name__ == '__main__':
    main()
