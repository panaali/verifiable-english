"""Independent exhaustive finite-semantics differential audit, serial only.

Integers encode ALL relation interpretations, not sampled interpretations.
Bit i is the truth value in interpretation i; connectives use bit operations
and quantifiers range explicitly over every entity. Sizes 0..3 are inclusive.
"""
from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
from itertools import product
import hashlib
import json
import platform
from pathlib import Path
import random
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ve.ast import (And, Binary, Bottom, Const, Eq, Exists, Forall, Implies,
                    Not, Or, Top, Unary, Var, formula_to_data)
from ve.entailment import check_entailment_certificate
from ve.environment import Environment, LANGUAGE, PROFILE, SPEC_REVISION
from ve.equivalence import Budgets, compare
from ve.search import check_countermodel


def environment(mode):
    sorts = ['item', 'other'] if mode == 'two_sorts' else ['item']
    right = sorts[-1]
    return Environment.from_dict({'language': LANGUAGE, 'profile': PROFILE,
        'spec_revision': SPEC_REVISION, 'vocabulary': {
            'sorts': {s: {'description': s} for s in sorts},
            'predicates': {'p': {'arguments': ['item'], 'description': 'P.'},
                           'q': {'arguments': [right], 'description': 'Q.'},
                           'r': {'arguments': ['item', right], 'description': 'R.'}},
            'constants': {c: {'sort': 'item', 'description': c} for c in ('a', 'b')}
                         if mode == 'constants' else {}}})


class Exhaustive:
    def __init__(self, env, sizes, constants):
        self.domains = {sort: tuple(range(size)) for sort, size in zip(env.sorts, sizes)}
        self.constants = constants
        atoms = [(name, row) for name, decl in env.predicates.items()
                 for row in product(*(self.domains[s] for s in decl.arguments))]
        self.worlds = 1 << len(atoms)
        self.full = (1 << self.worlds) - 1
        self.atoms = {}
        for index, atom in enumerate(atoms):
            step = 1 << index
            self.atoms[atom] = self.full // ((1 << (2 * step)) - 1) * (((1 << step) - 1) << step)
        # Bound memory over thousands of independently generated formulas.
        self.truth = lru_cache(maxsize=2048)(self._truth)

    def _truth(self, f, bindings=()):
        def term(t):
            return self.constants[t.name] if type(t) is Const else bindings[t.index]
        def visit(child):
            return self.truth(child, bindings)
        kind = type(f)
        if kind is Top: return self.full
        if kind is Bottom: return 0
        if kind is Unary: return self.atoms[f.predicate, (term(f.term),)]
        if kind is Binary: return self.atoms[f.predicate, (term(f.left), term(f.right))]
        if kind is Eq: return self.full if term(f.left) == term(f.right) else 0
        if kind is Not: return self.full ^ visit(f.body)
        if kind is And: return visit(f.left) & visit(f.right)
        if kind is Or: return visit(f.left) | visit(f.right)
        if kind is Implies: return (self.full ^ visit(f.left)) | visit(f.right)
        result = self.full if kind is Forall else 0
        for value in self.domains[f.sort]:
            child = self.truth(f.body, (value,) + bindings)
            result = result & child if kind is Forall else result | child
        return result


def interpretations(env):
    for sizes in product(range(4), repeat=len(env.sorts)):
        domain = dict(zip(env.sorts, sizes))
        names = list(env.constants)
        for values in product(*(range(domain[env.constants[name].sort]) for name in names)):
            yield Exhaustive(env, sizes, dict(zip(names, values)))


def generate(rng, env, depth, binders=()):
    terms = {sort: [Const(name) for name, decl in env.constants.items() if decl.sort == sort] +
             [Var(i) for i, s in enumerate(binders) if s == sort] for sort in env.sorts}
    atoms = [Top(), Bottom()]
    for name, decl in env.predicates.items():
        arguments = [terms[sort] for sort in decl.arguments]
        if all(arguments):
            selected = [rng.choice(options) for options in arguments]
            atoms.append(Unary(name, *selected) if len(selected) == 1 else Binary(name, *selected))
    for options in terms.values():
        if options:
            atoms.append(Eq(rng.choice(options), rng.choice(options)))
    if depth == 0 or rng.random() < .20:
        return rng.choice(atoms)
    ctor = rng.choice([Not, And, Or, Implies, Forall, Exists, Forall, Exists])
    if ctor in (Forall, Exists):
        sort = rng.choice(list(env.sorts))
        return ctor(sort, generate(rng, env, depth - 1, (sort,) + binders))
    a = generate(rng, env, depth - 1, binders)
    return Not(a) if ctor is Not else ctor(a, generate(rng, env, depth - 1, binders))


def scalar(f, model, bindings=()):
    def term(t):
        return model.constants[t.name] if type(t) is Const else bindings[t.index]
    kind = type(f)
    if kind is Top: return True
    if kind is Bottom: return False
    if kind is Unary: return (term(f.term),) in model.relations[f.predicate]
    if kind is Binary: return (term(f.left), term(f.right)) in model.relations[f.predicate]
    if kind is Eq: return term(f.left) == term(f.right)
    if kind is Not: return not scalar(f.body, model, bindings)
    if kind is And: return scalar(f.left, model, bindings) and scalar(f.right, model, bindings)
    if kind is Or: return scalar(f.left, model, bindings) or scalar(f.right, model, bindings)
    if kind is Implies: return not scalar(f.left, model, bindings) or scalar(f.right, model, bindings)
    values = (scalar(f.body, model, (x,) + bindings) for x in model.domains[f.sort])
    return all(values) if kind is Forall else any(values)


def check_bitset_engine():
    # Cross-check bit addressing independently on ALL 0..2 interpretations.
    from ve.model import FiniteModel
    env = environment('single_sort')
    formulas = [Exists('item', Unary('p', Var(0))),
                Forall('item', Exists('item', Binary('r', Var(1), Var(0)))),
                Exists('item', Forall('item', Eq(Var(1), Var(0))))]
    for size in range(3):
        engine = Exhaustive(env, (size,), {})
        atoms = list(engine.atoms)
        for world in range(engine.worlds):
            relations = {name: [] for name in env.predicates}
            for index, (name, row) in enumerate(atoms):
                if world & (1 << index):
                    relations[name].append([f"e{x}" for x in row])
            model = FiniteModel.from_dict(env, {'complete': True, 'domains': {'item': [f"e{x}" for x in range(size)]},
                                                'constants': {}, 'relations': relations})
            for f in formulas:
                assert bool(engine.truth(f) & (1 << world)) == scalar(f, model)


def run(count, seed, output):
    check_bitset_engine()
    rng = random.Random(seed)
    modes = ['single_sort', 'two_sorts', 'constants']
    envs = {mode: environment(mode) for mode in modes}
    engines = {mode: list(interpretations(env)) for mode, env in envs.items()}
    stats = Counter()
    digest = hashlib.sha256()
    unique_pairs = set()
    started = time.perf_counter()
    budgets = Budgets(max_proof_steps=1500, max_domain_size=2, max_models=1000, max_evaluations=20000)
    failures = []
    for index in range(count):
        mode = modes[index % len(modes)]
        env = envs[mode]
        a = generate(rng, env, rng.randint(1, 5))
        mutation = index % 7
        b = (Not(Not(a)) if mutation == 0 else And(a, Top()) if mutation == 1 else
             Or(a, Bottom()) if mutation == 2 else Not(a) if mutation == 3 else
             generate(rng, env, rng.randint(1, 5)))
        encoded = json.dumps([mode, formula_to_data(env, a), formula_to_data(env, b)], separators=(',', ':'))
        digest.update(encoded.encode())
        unique_pairs.add(encoded)
        result = compare(env, a, b, budgets)
        stats[result.status] += 1
        stats[mode] += 1
        stats['empty_only'] += result.relation_detail == 'differs_only_on_empty_sorts'
        pairs = [(engine, engine.truth(a), engine.truth(b)) for engine in engines[mode]]
        stats['model_interpretations_checked'] += sum(engine.worlds for engine, _, _ in pairs)
        for label, left, right, direction in [('a_implies_b', a, b, result.a_implies_b),
                                             ('b_implies_a', b, a, result.b_implies_a)]:
            if direction.certificate is not None:
                assert check_entailment_certificate(env, (left,), right, direction.certificate,
                                                   max_steps=1500).valid
                stats['certificates_replayed'] += 1
                for engine, av, bv in pairs:
                    x, y = (av, bv) if label == 'a_implies_b' else (bv, av)
                    if x & (engine.full ^ y):
                        failures.append({'index': index, 'pair': json.loads(encoded), 'direction': label})
                        break
            if direction.model is not None:
                assert check_countermodel(env, (left,), right, direction.model).valid
                assert scalar(left, direction.model) and not scalar(right, direction.model)
                stats['models_rechecked'] += 1
            certificate = result.nonempty_certificates.get(label)
            if certificate:
                conditions = tuple(Exists(sort, Top()) for sort in result.nonempty_sorts)
                assert check_entailment_certificate(env, (left, *conditions), right, certificate,
                                                   max_steps=1500).valid
                stats['conditional_certificates_replayed'] += 1
                for engine, av, bv in pairs:
                    if not all(engine.domains.values()): continue
                    x, y = (av, bv) if label == 'a_implies_b' else (bv, av)
                    if x & (engine.full ^ y):
                        failures.append({'index': index, 'pair': json.loads(encoded), 'conditional': label})
                        break
        if (index + 1) % 250 == 0:
            print(f'{index + 1}/{count}: {dict(stats)}', flush=True)
    import ve.entailment, ve.equivalence, ve.attacks
    summary = {'pairs': count, 'unique_pairs': len(unique_pairs), 'seed': seed, 'max_domain_size_per_sort': 3,
               'python': sys.version, 'platform': platform.platform(),
               'implementation_sha256': {module.__name__: hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
                                         for module in (ve.entailment, ve.equivalence, ve.attacks)},
               'input_sha256': digest.hexdigest(), 'seconds': time.perf_counter() - started,
               'counts': dict(stats), 'certified_counterexamples': failures}
    Path(output).write_text(json.dumps(summary, indent=2) + '\n')
    assert not failures, failures[:3]
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pairs', type=int, default=5000)
    parser.add_argument('--seed', type=int, default=20260922)
    parser.add_argument('--output', default='docs/prover-fair/fuzz.json')
    args = parser.parse_args()
    run(args.pairs, args.seed, args.output)
