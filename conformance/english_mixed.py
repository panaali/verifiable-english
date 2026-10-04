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
type registered in `ve.surface.registry` must have an exercising configuration
and occur in that configuration's corpus. A newly registered profile therefore
fails until the harness supplies a configuration and a generator for it.

The per-input check at admission, not this corpus, is what admits English.
No model calls.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from itertools import chain
import json
from pathlib import Path
import random
import warnings

from ve import ast, Environment, render
from ve.english import UnreviewedVocabularyWarning, parse_english
from ve.errors import AmbiguousDerivation, ResourceLimit, SyntaxError
from ve.profiles import LANGUAGE, SPEC_REVISION
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


def nary_configuration():
    """Exercise the registered n-ary atom in a mixed profile."""
    return 'nary', Environment({
        'language': LANGUAGE,
        'profiles': ['closure@0', 'nary@0', 'relational-fol@0'],
        'spec_revision': SPEC_REVISION,
        'vocabulary': {
            'sorts': {'item': {'description': 'An item.'}},
            'predicates': {'reports': {'arguments': ['item'] * 3,
                                       'description': 'A report from one item to another.',
                                       'verbalisation': '{0} reports {1} to {2}'}},
            'constants': {name: {'sort': 'item', 'description': name}
                          for name in ('alice', 'bob', 'carol')},
        },
    }), {}


def mixed(per_vocabulary=40, offsets=None, parse=True, part=(0, 1)):
    """The report over every configuration, or over the configurations at `offsets` only
    (each keeps its seed, so the slices together are the whole run; the coverage of the
    registered constructs is then not judged). `part=(i, n)` renders and parses only the
    texts whose index in their configuration is `i` modulo `n`. With `parse` false, texts
    are generated but neither rendered nor parsed: the coverage, which depends on the
    generated formulas only, is the same."""
    warnings.simplefilter('ignore', UnreviewedVocabularyWarning)
    rows, failures, covered = [], [], set()
    registered = {r.node_type for r in registry.records() if r.node_type is not None}
    enabled_anywhere = set()
    for offset, (name, env, options) in enumerate(chain(configurations(), (nary_configuration(),))):
        if offsets is not None and offset not in offsets:
            continue
        rng = random.Random(MIXED_SEED + offset)
        enabled = {r.node_type for r in registry.records()
                   if r.node_type is not None and registry.enabled(r, env)}
        enabled_anywhere |= enabled
        formulas = [f for f in compositions(rng, env) if closed(f, env)]
        if name == 'nary':
            atom = ast.Atom('reports', (ast.Const('alice'), ast.Const('bob'), ast.Const('carol')))
            premise = ast.Atom('reports', (ast.Var(0), ast.Const('bob'), ast.Const('carol')))
            formulas.extend((atom, ast.Forall('item', ast.Implies(premise, atom))))
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
        for index, document in enumerate(documents):
            for formula in document.formulas:
                node_types(formula, seen)
            if not parse or index % part[1] != part[0]:
                continue
            text = render(document, env, 've_english', **options)
            digest.update(text.encode())
            try:
                copied = parse_english(env, text, **options)
            except AmbiguousDerivation as exc:
                counts['multiple_derivations'] += 1
                failures.append({'vocabulary': name, 'kind': 'multiple derivations',
                                 'text': text, 'error': str(exc)[:1000]})
                continue
            except SyntaxError as exc:
                failures.append({'vocabulary': name, 'kind': 'rejected', 'text': text, 'error': str(exc)[:1000]})
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
                     **dict(sorted(counts.items())), 'multiple_derivations': counts['multiple_derivations'],
                     'node_types': sorted(t.__name__ for t in seen & enabled),
                     'corpus_sha256': digest.hexdigest()})
        print(json.dumps(rows[-1]), flush=True)
    unexercised_profiles = sorted(t.__name__ for t in registered - enabled_anywhere) if offsets is None else []
    if unexercised_profiles:
        failures.append({'kind': 'registered construct has no exercising configuration',
                         'node_types': unexercised_profiles})
    missing = sorted(t.__name__ for t in registered - covered) if offsets is None else []
    if missing:
        failures.append({'kind': 'registered construct not generated', 'node_types': missing})
    return {'method': 'rendered mixed-construct sentences and paragraphs; parse_english all-derivations check',
            'vocabularies': rows, 'missing_constructs': missing,
            'unexercised_profiles': unexercised_profiles, 'seed': MIXED_SEED,
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
