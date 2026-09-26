"""Mixed-construct English harness (PLAN-EXPAND2 W7): regression evidence only.

Run serially from the repository root:

    uv run python -m conformance.english_mixed [--per-vocabulary N]

For every configuration of `conformance.english_surface` (every merged profile
and the reviewed, suggested and adopted overlays), it renders

* every ordered pair of connective or quantifier constructors applied over a
  simple clause (depth three; operands and clauses drawn with a fixed seed),
* seeded random formulas of depth exactly three mixing every constructor the
  environment's profiles enable, and
* three-sentence paragraphs of those formulas,

and parses each text with `parse_english`, which runs the complete Earley
all-derivations check. Any text with more than one derivation fails, as does
a round trip to a different AST or an exhausted derivation budget. Every node
type registered in `ve.surface.registry` must occur in the corpus of some
vocabulary whose profiles enable it; a newly registered construct without a
generator fails here until the harness generates it.

The per-input check at admission, not this corpus, is what admits English.
No model calls.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import warnings

from ve import ast, render
from ve.english import UnreviewedVocabularyWarning, parse_english
from ve.errors import ResourceLimit, SyntaxError
from ve.surface import registry

from conformance.english_surface import SEED, configurations, formula_depth, random_formula

ROOT = Path(__file__).resolve().parents[1]
MIXED_SEED = SEED + 700_000


def node_types(node, seen):
    """Every AST class occurring in `node`."""
    seen.add(type(node))
    for field in getattr(node, '__dataclass_fields__', {}):
        value = getattr(node, field)
        if hasattr(value, '__dataclass_fields__'):
            node_types(value, seen)
    return seen


def simple_clauses(rng, env, scope):
    """Two or three depth-one clauses available in `scope`."""
    clauses = [random_formula(rng, env, 0, scope) for _ in range(6)]
    return list(dict.fromkeys(clauses))[:3]


def wrappers(env, scope):
    """One-constructor contexts: each takes a child builder over a scope."""
    result = [('not', lambda build: ast.Not(build(scope)))]
    for kind, node in (('and', ast.And), ('or', ast.Or), ('implies', ast.Implies)):
        result.append((kind + '-left', lambda build, node=node: node(build(scope), ast.Top())))
        result.append((kind + '-right', lambda build, node=node: node(ast.Bottom(), build(scope))))
    for sort in sorted(s for s in env.sorts if s != '$int'):
        result.append(('forall', lambda build, sort=sort: ast.Forall(sort, build((sort, *scope)))))
        result.append(('exists', lambda build, sort=sort: ast.Exists(sort, build((sort, *scope)))))
    return result


def compositions(rng, env):
    """Every ordered pair of wrappers around a simple clause: depth three."""
    formulas = []
    outer = wrappers(env, ())
    for _, first in outer:
        for index in range(len(outer)):
            def inner(scope, index=index):
                middle = wrappers(env, scope)[index % len(wrappers(env, scope))][1]
                return middle(lambda scope2: rng.choice(simple_clauses(rng, env, scope2)))
            formulas.append(first(inner))
    return formulas


def closed(formula, env):
    try:
        ast.check_formula(env, formula)
        return True
    except Exception:
        return False


def mixed(per_vocabulary=40):
    warnings.simplefilter('ignore', UnreviewedVocabularyWarning)
    rows, failures, covered = [], [], set()
    enabled_anywhere = set()
    for offset, (name, env, options) in enumerate(configurations()):
        rng = random.Random(MIXED_SEED + offset)
        enabled = {r.node_type for r in registry.records()
                   if r.node_type is not None and registry.enabled(r, env)}
        enabled_anywhere |= enabled
        formulas = [f for f in compositions(rng, env) if closed(f, env)]
        sampled = attempts = 0
        while sampled < per_vocabulary and attempts < 50 * per_vocabulary:
            attempts += 1
            formula = random_formula(rng, env, 3)
            if formula_depth(formula) >= 3:
                formulas.append(formula)
                sampled += 1
        formulas = list(dict.fromkeys(formulas))
        documents = [ast.Document((f,)) for f in formulas]
        documents += [ast.Document(tuple(formulas[i:i + 3])) for i in range(0, len(formulas) - 2, 3)]
        counts, seen, digest = Counter(), set(), hashlib.sha256()
        for document in documents:
            for formula in document.formulas:
                node_types(formula, seen)
            text = render(document, env, 've_english', **options)
            digest.update(text.encode())
            try:
                copied = parse_english(env, text, **options)
            except SyntaxError as exc:
                kind = 'multiple derivations' if 'two derivations' in str(exc) else 'rejected'
                failures.append({'vocabulary': name, 'kind': kind, 'text': text, 'error': str(exc)[:1000]})
                continue
            except ResourceLimit as exc:
                failures.append({'vocabulary': name, 'kind': 'budget exhausted', 'text': text, 'error': str(exc)})
                continue
            if copied != document:
                failures.append({'vocabulary': name, 'kind': 'round trip', 'text': text})
                continue
            counts['paragraphs' if len(document.formulas) > 1 else 'sentences'] += 1
        covered |= seen & enabled
        rows.append({'vocabulary': name, 'seed': MIXED_SEED + offset, 'texts': len(documents),
                     **dict(sorted(counts.items())), 'multiple_derivations': 0,
                     'node_types': sorted(t.__name__ for t in seen & enabled),
                     'corpus_sha256': digest.hexdigest()})
        print(json.dumps(rows[-1]), flush=True)
    missing = sorted(t.__name__ for t in enabled_anywhere - covered)
    if missing:
        failures.append({'kind': 'registered construct not generated', 'node_types': missing})
    return {'method': 'rendered mixed-construct sentences and paragraphs; parse_english all-derivations check',
            'vocabularies': rows, 'missing_constructs': missing,
            'texts': sum(r['texts'] for r in rows), 'failures': failures[:200], 'failure_count': len(failures)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--per-vocabulary', type=int, default=40, help='random depth-3 formulas per vocabulary')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = mixed(args.per_vocabulary)
    if args.output:
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    if report['failure_count']:
        print(json.dumps(report['failures'][:5], indent=2))
        raise SystemExit(f"FAIL: {report['failure_count']} mixed-construct failures")
    print(f"PASS: {report['texts']} mixed-construct texts, each with exactly one derivation; "
          'every registered construct generated')
