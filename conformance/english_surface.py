"""Reproduce English round-trip/all-derivations and real-vocabulary measurements.

Run serially: uv run python -m conformance.english_surface
No model calls, no test-set tuning, no hidden atom token in the Earley grammar.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import random

from lark import Lark

from ve import ast, Environment, parse, render, suggest_vocabulary
from ve.english import EnglishVocabulary, english_lark_grammar, parse_english
from ve.printer import _NaturalVocabulary

ROOT = Path(__file__).resolve().parents[1]
SEED = 2026092107


def vocabularies():
    base = json.loads((ROOT / 'examples/fluent/environment.json').read_text())
    base['vocabulary']['predicates']['links'] = {'arguments': ['service', 'service'], 'description': 'Directed link.',
                                               'verbalisation': '{0} depends on {1}'}
    yield 'ordinary', Environment(base)
    closure = deepcopy(base)
    closure.pop('profile')
    closure.update(language='ve.core@0.1', profiles=['closure@0', 'relational-fol@0'], spec_revision='ve-v0.1-closure-2026-09-21')
    yield 'closure', Environment(closure)
    aliases = deepcopy(base)
    for decl in aliases['vocabulary']['sorts'].values():
        decl['verbalisation'] = {'singular': 'person', 'plural': 'people'}
    for decl in aliases['vocabulary']['predicates'].values():
        decl['verbalisation'] = '{0} is reviewed' if len(decl['arguments']) == 1 else '{0} owns {1}'
    yield 'colliding_aliases', Environment(aliases)
    structural = deepcopy(base)
    for sort, decl in structural['vocabulary']['sorts'].items():
        decl['verbalisation'] = {'singular': 'either' if sort == 'person' else 'following', 'plural': 'both'}
    for name, decl in structural['vocabulary']['predicates'].items():
        decl['verbalisation'] = '{0} is impossible' if len(decl['arguments']) == 1 else '{0} owns either {1}'
    structural['vocabulary']['constants'].update({name: {'sort': 'service', 'description': name}
                                                for name in ['both', 'either', 'this', 'starting', 'following', 'a', 'first']})
    yield 'function_words', Environment(structural)
    # Function words can be identifiers as well as supplied aliases.
    identifier = deepcopy(base)
    identifier['vocabulary'] = {
        'sorts': {name: {'description': name} for name in ['both', 'first', 'this']},
        'predicates': {'holds': {'description': 'Holds', 'arguments': ['both']},
                       'impossible': {'description': 'Impossible', 'arguments': ['this']},
                       'starting': {'description': 'Starting', 'arguments': ['both', 'first']}},
        'constants': {'case': {'description': 'Case', 'sort': 'both'},
                      'second': {'description': 'Second', 'sort': 'first'},
                      'holds': {'description': 'Holds', 'sort': 'this'}}}
    # VE forbids reuse across symbol categories.
    identifier['vocabulary']['constants']['ending'] = identifier['vocabulary']['constants'].pop('holds')
    yield 'function_identifiers', Environment(identifier)
    precision = deepcopy(base)
    precision['vocabulary']['predicates']['deployed']['verbalisation'] = '{0} is fully deployed'
    precision['vocabulary']['predicates']['owns'].update(verbalisation='{0} contributes to {1}',
                                                       negative_verbalisation='{0} does not contribute to {1}')
    yield 'precision_templates', Environment(precision)
    for path in sorted((ROOT / 'usecases').glob('*/environment.json')):
        yield path.parent.name, Environment.from_json(path.read_bytes())


def configurations():
    for name, env in vocabularies():
        yield name, env, {}
    for path in sorted((ROOT / 'usecases').glob('*/environment.json')):
        yield path.parent.name + '-reviewed', Environment.from_json(path.read_bytes()), {
            'vocabulary': json.loads(path.with_name('environment.english.json').read_text())}
    data = json.loads((ROOT / 'examples/fluent/environment.json').read_text())
    for decl in data['vocabulary']['predicates'].values():
        decl.pop('verbalisation', None); decl.pop('negative_verbalisation', None)
    env = Environment(data)
    yield 'accepted-suggestions', env, {'vocabulary': suggest_vocabulary(env), 'accept_suggested_vocabulary': True}


def directed_formulas(env, words):
    """Force every new guard shape/lexical template into the Earley sample."""
    object_coordination_checked = False
    for name, decl in env.predicates.items():
        atom = (ast.Unary(name, ast.Var(0)) if len(decl.arguments) == 1
                else ast.Binary(name, ast.Var(0), ast.Var(1)))
        def bind(body):
            result = ast.Forall(decl.arguments[0], body)
            return result if len(decl.arguments) == 1 else ast.Forall(decl.arguments[1], result)
        atoms = [atom] + ([ast.Not(atom)] if name in words.negatives else [])
        for p in atoms:
            q = atom
            guards = [p, ast.And(p, q), ast.And(ast.And(p, q), p), ast.And(p, ast.And(q, p)),
                      ast.And(ast.And(p, q), ast.And(q, p)), ast.And(p, ast.Or(q, p))]
            for guard in guards:
                yield bind(ast.Implies(guard, q))
                yield bind(ast.Implies(guard, ast.Not(ast.Eq(ast.Var(0), ast.Var(0)))))
        yield bind(ast.Implies(ast.Not(ast.Eq(ast.Var(0), ast.Var(0))), atom))
        if len(decl.arguments) == 2:
            incoming = ast.Binary(name, ast.Var(1), ast.Var(0))
            guards = [incoming] + ([ast.Not(incoming)] if name in words.negatives else [])
            if not object_coordination_checked:
                guards += [ast.And(incoming, incoming), ast.And(ast.And(incoming, incoming), incoming),
                           ast.And(incoming, ast.And(incoming, incoming))]
                object_coordination_checked = True
            for guard in guards:
                yield ast.Forall(decl.arguments[0], ast.Forall(decl.arguments[1], ast.Implies(guard, ast.Top())))
    # Nested if/then scopes are deliberately exercised in both argument positions.
    p, q = ast.Top(), ast.Bottom()
    yield ast.Implies(ast.Implies(p, q), p)
    yield ast.Implies(p, ast.Implies(q, p))


def random_formula(rng, env, depth, scope=()):
    def available(sort):
        return [ast.Var(i) for i, s in enumerate(scope) if s == sort] + [ast.Const(n) for n, d in env.constants.items() if d.sort == sort]
    def term(sort): return rng.choice(available(sort))
    eligible = [(name, d) for name, d in env.predicates.items() if all(available(s) for s in d.arguments)]
    sorts = [s for s in env.sorts if available(s)]
    choices = ['top', 'bottom'] + (['atom'] * 4 if eligible else []) + (['eq'] if sorts else [])
    if depth:
        choices += ['not', 'and', 'or', 'implies', 'forall', 'exists'] * 2
        if env.closure and sorts: choices += ['reach'] * 3
    choice = rng.choice(choices)
    child = lambda ctx=scope: random_formula(rng, env, depth - 1, ctx)
    if choice == 'top': return ast.Top()
    if choice == 'bottom': return ast.Bottom()
    if choice == 'atom':
        name, decl = rng.choice(eligible)
        return (ast.Unary if len(decl.arguments) == 1 else ast.Binary)(name, *(term(s) for s in decl.arguments))
    if choice == 'eq':
        sort = rng.choice(sorts)
        return ast.Eq(term(sort), term(sort))
    if choice == 'not': return ast.Not(child())
    if choice in ('and', 'or', 'implies'):
        return {'and': ast.And, 'or': ast.Or, 'implies': ast.Implies}[choice](child(), child())
    if choice in ('forall', 'exists'):
        sort = rng.choice(tuple(env.sorts))
        return (ast.Forall if choice == 'forall' else ast.Exists)(sort, child((sort, *scope)))
    sort = rng.choice(sorts)
    named = [name for name, d in env.predicates.items() if d.arguments == (sort, sort)]
    edge = ast.Named(rng.choice(named)) if named and rng.choice([False, True]) else ast.Body(sort, child((sort, sort, *scope)))
    return ast.Reach(rng.choice(['plus', 'star']), edge, term(sort), term(sort))


def lint_report():
    result = []
    for path in sorted((ROOT / 'usecases').glob('*/environment.json')):
        env = Environment.from_json(path.read_bytes())
        old, new = _NaturalVocabulary(env), EnglishVocabulary(env)
        overlay = json.loads(path.with_name('environment.english.json').read_text())
        reviewed = EnglishVocabulary(env, vocabulary=overlay)
        declared = {n: d.verbalisation for n, d in env.predicates.items() if d.verbalisation is not None}
        result.append({'usecase': path.parent.name, 'environment_id': env.environment_id,
                       'predicates': len(env.predicates), 'declared_templates': len(declared),
                       'missing_templates': sorted(set(env.predicates) - set(declared)),
                       'accepted_before': sum(t == old.predicates[n] for n, t in declared.items()),
                       'accepted_after': sum(t == new.predicates[n] for n, t in declared.items()),
                       'reviewed_templates': len(overlay['predicates']), 'overlay_digest': reviewed.overlay_digest,
                       'reviewed_lint': [i.to_dict() for i in reviewed.issues],
                       'still_rejected': [{'predicate': n, 'template': t,
                                           'codes': [i.code for i in new.issues if i.path == f'/vocabulary/predicates/{n}/verbalisation']}
                                          for n, t in declared.items() if t != new.predicates[n]]})
    return result


def audit(per_vocabulary=5000, earley_per_vocabulary=500):
    rows = []
    for offset, (name, env, options) in enumerate(configurations()):
        rng = random.Random(SEED + offset)
        words = EnglishVocabulary(env, **options)
        grammar = english_lark_grammar(env, **options)
        earley = Lark(grammar, parser='earley', lexer='dynamic_complete', ambiguity='explicit')
        seen, texts = set(), {}
        digest = hashlib.sha256()
        constructors = Counter()
        draws = checked = earley_count = 0
        directed = list(dict.fromkeys(directed_formulas(env, words)))
        if name.removesuffix('-reviewed') in {p.name for p in (ROOT / 'usecases').iterdir()}:
            directed += list(parse(env, (ROOT / 'usecases' / name.removesuffix('-reviewed') / 'claims.ve').read_bytes()).formulas)
        directed = list(dict.fromkeys(directed))
        assert len(directed) <= earley_per_vocabulary or earley_per_vocabulary == 0
        targeted_count = len(directed)
        while checked < per_vocabulary:
            formula = directed.pop(0) if directed else random_formula(rng, env, rng.randrange(2, 9))
            draws += 1
            if formula in seen: continue
            seen.add(formula)
            ast.check_formula(env, formula)
            text = render(ast.Document((formula,)), env, 've_english', **options)
            assert len(text.encode()) <= 65536
            copied = parse_english(env, text, **options)
            ast.check_document(env, copied)
            assert copied == ast.Document((formula,)), (name, text, formula, copied)
            assert texts.setdefault(text, formula) == formula
            # Independently enumerate ALL CFG derivations with dynamic_complete;
            # include long and short, core and closure, ordinary and adversarial texts.
            if earley_count < earley_per_vocabulary:
                tree = earley.parse(text[0].lower() + text[1:])
                assert not list(tree.find_data('_ambig')), (name, text, tree.pretty())
                earley_count += 1
            constructors[type(formula).__name__] += 1
            digest.update(text.encode())
            checked += 1
        row = {'vocabulary': name, 'environment_id': env.environment_id, 'seed': SEED + offset,
               'overlay_digest': words.overlay_digest, 'directed_asts': targeted_count,
               'draws_including_duplicates': draws, 'unique_asts_roundtripped': checked,
               'unique_texts': len(texts), 'earley_texts': earley_count, 'ambiguous_texts': 0,
               'top_level_constructors': dict(sorted(constructors.items())),
               'corpus_sha256': digest.hexdigest(), 'grammar_sha256': hashlib.sha256(grammar.encode()).hexdigest()}
        rows.append(row)
        print(json.dumps(row), flush=True)
    return {'method': 'unique directed and seeded random well-typed ASTs; separate Earley dynamic_complete all-derivations syntax envelope',
            'roundtrips': sum(r['unique_asts_roundtripped'] for r in rows),
            'earley_texts': sum(r['earley_texts'] for r in rows), 'ambiguous_texts': 0,
            'identity_fixtures': len(json.loads((ROOT / 'conformance/identity.json').read_text())),
            'vocabularies': rows, 'linter': lint_report()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--per-vocabulary', type=int, default=5000)
    parser.add_argument('--earley-per-vocabulary', type=int, default=500)
    parser.add_argument('--output', type=Path, default=ROOT / 'conformance/english-surface-report.json')
    args = parser.parse_args()
    if not 0 <= args.earley_per_vocabulary <= args.per_vocabulary:
        parser.error('Earley count must be between zero and the round-trip count')
    result = audit(args.per_vocabulary, args.earley_per_vocabulary)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(f"PASS: {result['roundtrips']} unique AST round trips; {result['earley_texts']} unique texts, no multiple derivations")
