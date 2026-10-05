"""Inputs of the G1a measurement of the English-in-Lean grammar engine (plan section 5, S1a).

    uv run python -m bench.english_lean_g1a [--per-configuration N] [--output PATH]
    (cd lean && lake build ve_english_lean_bench)
    lean/.lake/build/bin/ve_english_lean_bench PATH 3 > RESULTS.jsonl
    uv run python -m bench.english_lean_g1a --output PATH --summarise RESULTS.jsonl

Writes the grammars and sentences that `ve_english_lean_bench` (lean/EnglishLeanBenchMain.lean) reads,
and the step count of the Python reference engine on each sentence, so that the two step counters can
be compared. It needs the S0 tools of branch `english-lean/py` (`conformance.english_lean_engine`,
`english_lean_lexer`, `english_lean_s0`, `english_lean_tokens`). Measurement only; no admission path.

The inputs, by the kinds that G1a names:

- ordinary: the rendered corpus of S0 (the 17 configurations, `--per-configuration` texts each), over
  Python's grammar converted to word tokens (`english_lean_tokens.convert`);
- limit sizes: the synthetic limit environments of S0, with the attribute-property product factored as
  spec 2.10 prescribes (one rule per relation over a property nonterminal);
- long: rendered sentences of 280 tokens and more, searched among random formulas (the design point of
  the DRI's ruling is 300 tokens);
- failing prefixes: each of the longest sentences with its last token removed, and with a word that no
  rule reads put before its last token;
- ambiguous: Python's constructed two-derivation sentences (`english_lean_tokens.ambiguity_probe`), and
  a saturating grammar `S -> A S | A`, `A -> a | a a` on runs of `a` of up to 300 tokens.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
import re
import warnings

from ve import ast, render
from ve.english import UnreviewedVocabularyWarning, english_lark_grammar

from conformance import english_lean_engine as E
from conformance import english_lean_lexer as LX
from conformance.english_lean_s0 import _texts, synthetic_environments
from conformance.english_lean_tokens import convert
from conformance.english_surface import configurations, random_formula

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.cache' / 'english-lean-g1a-input.json'  # 3 MB; regenerated, not committed
PRODUCT = re.compile(r'"the" "(\w+)" "of" term "is" "(\w+)"')


def tok_json(tok: tuple) -> list:
    return list(tok)


def terminal_json(a: tuple) -> list:
    kind = a[0]
    if kind in ('kw', 'content'):
        return [kind, a[1]]
    if kind == 'exact':
        return ['exact', tok_json(a[1])]
    return ['cls', list(a[1])]


def grammar_json(name: str, G: E.Grammar, sentences: list, kind: str) -> dict:
    rules = [{'lhs': R.lhs, 'tag': R.tag,
              'rhs': [{'n': s.A} if isinstance(s, E.N) else {'t': terminal_json(s.a)} for s in R.rhs]}
             for R in G.rules]
    steps = []
    for w in sentences:
        stats = E.ParseStats()
        E.parse(G, E.terminal_accepts, 2, None, w, stats)
        steps.append(stats.steps)
    return {'name': name, 'kind': kind, 'rules': rules, 'start': G.start, 'rank': list(G.rank),
            'sentences': [[tok_json(t) for t in w] for w in sentences], 'python_steps': steps}


def factored(grammar: str) -> str:
    """Spec 2.10: the alternatives `the R of t is P` become `the R of t is property` and `property: P`."""
    relations = list(dict.fromkeys(m[1] for m in PRODUCT.finditer(grammar)))
    properties = list(dict.fromkeys(m[2] for m in PRODUCT.finditer(grammar)))
    if not relations:
        return grammar
    lines = []
    for line in grammar.split('\n'):
        if line.startswith('atom:'):
            alternatives = [a for a in line[len('atom:'):].split(' | ') if not PRODUCT.fullmatch(a.strip())]
            alternatives += [f'"the" "{r}" "of" term "is" attr_property' for r in relations]
            line = 'atom: ' + ' | '.join(a.strip() for a in alternatives)
        lines.append(line)
    lines.insert(-1, 'attr_property: ' + ' | '.join(f'"{p}"' for p in properties))
    return '\n'.join(lines)


def lexed(text: str) -> list:
    (w,) = LX.lex(text)
    return w


def corpus(per_configuration: int) -> tuple[list[dict], list[tuple]]:
    out, longest = [], []
    for offset, (name, env, options) in enumerate(configurations()):
        G, _, _ = convert(english_lark_grammar(env, **options))
        ws = [lexed(text) for _, text in _texts(name, env, options, per_configuration, offset)]
        out.append(grammar_json(name, G, ws, 'ordinary'))
        longest += [(len(w), name, G, w) for w in ws]
    return out, longest


def long_sentences(minimum: int, wanted: int) -> list[dict]:
    """Rendered sentences of at least `minimum` tokens, searched among deep random formulas."""
    out = []
    for offset, (name, env, options) in enumerate(configurations()):
        rng = random.Random(20261004 + offset)
        found = []
        for _ in range(4000):
            f = random_formula(rng, env, rng.randrange(7, 12))
            text = render(ast.Document((f,)), env, 've_english', **options)
            w = lexed(text)
            if len(w) >= minimum:
                found.append(w)
            if len(found) >= wanted:
                break
        if found:
            G, _, _ = convert(english_lark_grammar(env, **options))
            out.append(grammar_json(name + '/long', G, found, 'long'))
    return out


def failing(longest: list[tuple]) -> list[dict]:
    """The longest sentences, made to fail at their end."""
    by_name: dict = {}
    for n, name, G, w in sorted(longest, key=lambda x: -x[0])[:20]:
        by_name.setdefault(name, (G, []))[1].extend([w[:-1], w[:-1] + [('word', 'zzzq', False)] + w[-1:]])
    return [grammar_json(name + '/failing', G, ws, 'failing') for name, (G, ws) in by_name.items()]


def synthetic(per_environment: int) -> list[dict]:
    out = []
    for offset, (name, env) in enumerate(synthetic_environments()):
        G, _, _ = convert(factored(english_lark_grammar(env)))
        rng = random.Random(20261004 + 100 + offset)
        ws = []
        for _ in range(50 * per_environment):
            try:
                text = render(ast.Document((random_formula(rng, env, rng.randrange(2, 8)),)), env, 've_english')
            except ValueError:
                continue  # no writable English form; the renderer refuses it, as Python does
            ws.append(lexed(text))
            if len(ws) >= per_environment:
                break
        out.append(grammar_json(name, G, ws, 'limit'))
        # The design point of the DRI's ruling: sentences of about 300 tokens, at limit size.
        longs = []
        for _ in range(3000):
            try:
                text = render(ast.Document((random_formula(rng, env, rng.randrange(8, 13)),)), env, 've_english')
            except ValueError:
                continue
            w = lexed(text)
            if len(w) >= 280:
                longs.append(w)
            if len(longs) >= 3:
                break
        if longs:
            out.append(grammar_json(name + '/long', G, longs, 'limit-long'))
    return out


def ambiguous() -> list[dict]:
    a = E.T(('kw', 'a'))
    G = E.Grammar((E.Rule(0, (E.N(1), E.N(0)), 0, 'S-AS'), E.Rule(0, (E.N(1),), 0, 'S-A'),
                   E.Rule(1, (a,), 0, 'A-a'), E.Rule(1, (a, a), 0, 'A-aa')), 0, (1, 0))
    runs = [[('word', 'a', k == 0) for k in range(n)] for n in (10, 50, 100, 150, 200, 266, 300)]
    return [grammar_json('saturating', G, runs, 'ambiguous')]


def summarise(input_path: Path, results_path: Path) -> dict:
    """Per kind: verdicts, steps (Lean against the Python reference), tokens and latency percentiles."""
    configs = {c['name']: c for c in json.loads(input_path.read_text())['configurations']}
    rows = [json.loads(line) for line in results_path.read_text().splitlines() if line.strip()]
    prepare = {r['configuration']: {'ms': r['prepare_micros'] / 1000, 'terminals': r['terminals'],
                                    'rules': len(configs[r['configuration']]['rules'])}
               for r in rows if 'prepare_micros' in r}
    rows = [r for r in rows if 'steps' in r]
    kinds: dict = {}
    mismatched = []
    per_token = []
    for r in rows:
        if configs[r['configuration']]['kind'] in ('ordinary', 'long', 'limit', 'limit-long', 'failing'):
            per_token.append((r['tokens'], r['nanos'], r['configuration']))
        c = configs[r['configuration']]
        if r['steps'] != c['python_steps'][r['sentence']]:
            mismatched.append((r['configuration'], r['sentence'], r['steps'], c['python_steps'][r['sentence']]))
        k = kinds.setdefault(c['kind'], {'verdicts': {}, 'steps': [], 'micros': [], 'tokens': []})
        k['verdicts'][r['verdict']] = k['verdicts'].get(r['verdict'], 0) + 1
        k['steps'].append(r['steps'])
        k['micros'].append(r['micros'])
        k['tokens'].append(r['tokens'])

    def pct(xs: list, p: float):
        xs = sorted(xs)
        return xs[min(len(xs) - 1, int(p * len(xs)))]

    out = {}
    for kind, k in kinds.items():
        longest = max(range(len(k['tokens'])), key=lambda i: k['tokens'][i])
        out[kind] = {'sentences': len(k['steps']), 'verdicts': k['verdicts'],
                     'tokens_max': max(k['tokens']),
                     'steps': {'p50': pct(k['steps'], .5), 'p95': pct(k['steps'], .95), 'max': max(k['steps'])},
                     'ms': {'p50': pct(k['micros'], .5) / 1000, 'p95': pct(k['micros'], .95) / 1000,
                            'max': max(k['micros']) / 1000},
                     'longest': {'tokens': k['tokens'][longest], 'steps': k['steps'][longest],
                                 'ms': k['micros'][longest] / 1000}}
    out['step_counter_mismatches'] = mismatched
    out['prepare_ms_max'] = max(prepare.items(), key=lambda kv: kv[1]['ms'])
    # The latency budget of plan section 5 names a 150-token sentence; the largest of 140 to 170 tokens.
    near = [x for x in per_token if 140 <= x[0] <= 170]
    out['near_150_tokens_ms_max'] = max(((n / 1e6, t, c) for t, n, c in near), default=None)
    out['budget_2_1M_exceeded'] = [(r['configuration'], r['sentence'], r['steps']) for r in rows
                                   if r['steps'] > 2_100_000]
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--per-configuration', type=int, default=60)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    parser.add_argument('--summarise', type=Path, metavar='RESULTS',
                        help='summarise the JSON lines that ve_english_lean_bench printed for --output')
    args = parser.parse_args(argv)
    if args.summarise:
        print(json.dumps(summarise(args.output, args.summarise), indent=1))
        return 0
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UnreviewedVocabularyWarning)
        configs, longest = corpus(args.per_configuration)
        configs += failing(longest)
        configs += long_sentences(280, 3)
        configs += synthetic(20)
        configs += ambiguous()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({'configurations': configs}) + '\n')
    print(json.dumps({c['name']: len(c['sentences']) for c in configs}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
