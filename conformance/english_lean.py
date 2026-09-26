"""Python/Lean differential for the core English skeleton (PLAN-EXPAND2 W7).

Run from the repository root after `cd lean && lake build`:

    uv run python -m conformance.english_lean [--per-vocabulary N]

For every configuration of `conformance.english_surface` and every AST of its
round-trip corpus (5,000 per vocabulary gives the full 85,000 pairs), this
harness:

1. renders the AST with the Python renderer, tokenizes the text and asks the
   Lean core parser (`lean/VE/English/Run.lean`) for its reading;
2. asks the Lean core renderer for its canonical core text and checks that the
   Lean parser reads it back;
3. gives that Lean text to the Python parser (which runs the all-derivations
   check) and requires the same AST.

A Lean parse that differs from the Python AST, a Lean rendering that does not
parse back in Lean, or a Lean rendering that Python rejects or reads
differently is a failure. A Python text that the Lean core parser does not read
(contractions, validated negatives, closure, order) is counted as outside the
core skeleton, as are ASTs outside the v0 constructors and vocabularies whose
wording does not tokenize into core templates. Tokenization, capitalisation
and spacing are harness-side (Lean coverage pending for that layer). No model
calls.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import random
import re
import subprocess
import tempfile
import warnings

from ve import ast, render
from ve.english import EnglishVocabulary, UnreviewedVocabularyWarning, parse_english

from conformance.english_surface import SEED, configurations, directed_formulas, random_formula

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / 'lean'
RUNNER = 'VE/English/Run.lean'
PUNCTUATION = ',;:.'
MARKERS = {'(a)', '(b)', '(i)', '(ii)'}
V0 = (ast.Top, ast.Bottom, ast.Unary, ast.Binary, ast.Eq, ast.Not, ast.And, ast.Or, ast.Implies,
      ast.Forall, ast.Exists)


class Untokenizable(ValueError):
    pass


def lower_sentence_starts(text):
    # Same folding as ve.surface.unambiguity: the parser folds the first letter
    # of every sentence before matching.
    return re.sub(r"(^|(?<=\.)\s+)([A-Z])", lambda match: match[1] + match[2].lower(), text)


def tokenize(text, letters=(), placeholders=False):
    """Words, detached trailing punctuation, labels as [letter, index]."""
    label = re.compile('(' + '|'.join(sorted(map(re.escape, letters), key=len, reverse=True))
                       + r')([1-9][0-9]*)') if letters else None
    tokens = []
    for raw in text.split():
        trail = []
        while raw and raw not in MARKERS and raw[-1] in PUNCTUATION:
            trail.insert(0, raw[-1])
            raw = raw[:-1]
        if raw:
            hole = re.fullmatch(r'\{([0-9]+)\}', raw) if placeholders else None
            match = label.fullmatch(raw) if label else None
            if hole:
                tokens.append(int(hole[1]))
            elif placeholders and '{' in raw:
                raise Untokenizable(f'placeholder inside a word: {raw!r}')
            elif match:
                tokens.append([match[1], int(match[2])])
            else:
                tokens.append(raw)
        tokens.extend(trail)
    return tokens


def detokenize(tokens):
    text = ''
    for token in tokens:
        word = token[0] + str(token[1]) if isinstance(token, list) else token
        if text and word not in PUNCTUATION:
            text += ' '
        text += word
    # Capitalise every sentence start, as the Python renderer does.
    return re.sub(r"(^|(?<=\.)\s+)([a-z])", lambda match: match[1] + match[2].upper(), text)


def lexicon(env, words):
    """The Lean lexicon for this vocabulary, or Untokenizable."""
    def plain(text):
        result = tokenize(text)
        if any(not isinstance(t, str) for t in result):
            raise Untokenizable(f'label-shaped word in {text!r}')
        return result
    return {
        'sorts': {s: {'noun': plain(words.sorts[s]), 'letter': words.letters[s]} for s in env.sorts},
        'predicates': {p: [t for t in tokenize(words.predicates[p], placeholders=True)]
                       for p in env.predicates},
        'constants': {c: plain(words.constants[c]) for c in env.constants}}


def environment(env):
    return {'sorts': list(env.sorts),
            'predicates': {p: list(d.arguments) for p, d in env.predicates.items()},
            'constants': {c: d.sort for c, d in env.constants.items()}}


def v0_only(formula):
    if not isinstance(formula, V0):
        return False
    if isinstance(formula, ast.Unary):
        return isinstance(formula.term, (ast.Var, ast.Const))
    if isinstance(formula, (ast.Binary, ast.Eq)):
        return all(isinstance(t, (ast.Var, ast.Const)) for t in (formula.left, formula.right))
    if isinstance(formula, (ast.Not, ast.Forall, ast.Exists)):
        return v0_only(formula.body)
    if isinstance(formula, (ast.And, ast.Or, ast.Implies)):
        return v0_only(formula.left) and v0_only(formula.right)
    return True


def wire_term(term):
    return ['var', term.index] if isinstance(term, ast.Var) else ['const', term.name]


def wire(formula):
    kind = type(formula)
    if kind is ast.Top: return ['top']
    if kind is ast.Bottom: return ['bottom']
    if kind is ast.Unary: return ['unary', formula.predicate, wire_term(formula.term)]
    if kind is ast.Binary: return ['binary', formula.predicate, wire_term(formula.left), wire_term(formula.right)]
    if kind is ast.Eq: return ['eq', wire_term(formula.left), wire_term(formula.right)]
    if kind is ast.Not: return ['not', wire(formula.body)]
    if kind in (ast.And, ast.Or, ast.Implies):
        return [{ast.And: 'and', ast.Or: 'or', ast.Implies: 'implies'}[kind], wire(formula.left), wire(formula.right)]
    return ['forall' if kind is ast.Forall else 'exists', formula.sort, wire(formula.body)]


def run_lean(payload):
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as handle:
        json.dump(payload, handle)
        path = handle.name
    try:
        result = subprocess.run(['lake', 'env', 'lean', '--run', RUNNER, path], cwd=LEAN,
                                text=True, capture_output=True)
    finally:
        Path(path).unlink()
    if result.returncode:
        raise RuntimeError('Lean runner failed: ' + result.stderr[-2000:])
    return json.loads(result.stdout)['results']


def corpus(env, words, name, per_vocabulary, offset):
    """The same directed-then-seeded stream as conformance.english_surface."""
    rng = random.Random(SEED + offset)
    directed = list(dict.fromkeys(directed_formulas(env, words)))
    if name.removesuffix('-reviewed') in {p.name for p in (ROOT / 'usecases').iterdir()}:
        from ve import parse
        directed += list(parse(env, (ROOT / 'usecases' / name.removesuffix('-reviewed') / 'claims.ve').read_bytes()).formulas)
    directed = list(dict.fromkeys(directed))
    seen, result = set(), []
    while len(result) < per_vocabulary:
        formula = directed.pop(0) if directed else random_formula(rng, env, rng.randrange(2, 9))
        if formula in seen:
            continue
        seen.add(formula)
        result.append(formula)
    return result


def differential(per_vocabulary=200):
    # Suggested overlays are accepted explicitly by their configurations.
    warnings.simplefilter('ignore', UnreviewedVocabularyWarning)
    rows, failures = [], []
    for offset, (name, env, options) in enumerate(configurations()):
        words = EnglishVocabulary(env, **options)
        counts = Counter()
        try:
            lex = lexicon(env, words)
        except Untokenizable as exc:
            rows.append({'vocabulary': name, 'status': 'outside core lexicon', 'reason': str(exc)})
            print(json.dumps(rows[-1]), flush=True)
            continue
        letters = tuple(words.letters.values())
        cases, formulas = [], []
        for formula in corpus(env, words, name, per_vocabulary, offset):
            if not v0_only(formula):
                counts['outside core AST'] += 1
                continue
            text = render(ast.Document((formula,)), env, 've_english', **options)
            cases.append({'tokens': tokenize(lower_sentence_starts(text), letters), 'formulas': [wire(formula)]})
            formulas.append(formula)
        results = run_lean({'environment': environment(env), 'lexicon': lex, 'cases': cases}) if cases else []
        for formula, case, result in zip(formulas, cases, results):
            expected = [wire(formula)]
            if result['parsed'] is None:
                counts['python text outside core wording'] += 1
            elif result['parsed'] == expected:
                counts['lean parse agrees'] += 1
            else:
                failures.append({'vocabulary': name, 'kind': 'lean parse differs', 'tokens': case['tokens'],
                                 'expected': expected, 'lean': result['parsed']})
            if not result['checked']:
                failures.append({'vocabulary': name, 'kind': 'lean rejects checked AST', 'formula': expected})
                continue
            if result['roundtrip']:
                counts['lean core round trip'] += 1
            else:
                counts['lean core round trip fails'] += 1
                failures.append({'vocabulary': name, 'kind': 'lean round trip', 'formula': expected,
                                 'rendered': result['rendered']})
            if result['rendered'] == case['tokens']:
                counts['identical canonical text'] += 1
            lean_text = detokenize(result['rendered'])
            try:
                reread = parse_english(env, lean_text, **options)
            except Exception as exc:  # any rejection by the Python parser is a divergence
                failures.append({'vocabulary': name, 'kind': 'python rejects lean core text',
                                 'text': lean_text, 'error': f'{type(exc).__name__}: {exc}'[:500]})
                continue
            if reread == ast.Document((formula,)):
                counts['python reads lean core text'] += 1
            else:
                failures.append({'vocabulary': name, 'kind': 'python reads lean core text differently',
                                 'text': lean_text, 'expected': expected})
        rows.append({'vocabulary': name, 'status': 'compared', 'asts': len(formulas) + counts['outside core AST'],
                     **dict(sorted(counts.items()))})
        print(json.dumps(rows[-1]), flush=True)
    return {'method': 'Python render -> Lean core parse; Lean core render -> Lean parse and Python parse',
            'per_vocabulary': per_vocabulary, 'vocabularies': rows, 'failures': failures[:200],
            'failure_count': len(failures)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--per-vocabulary', type=int, default=200,
                        help='ASTs per vocabulary; 5000 replays the full 85,000-pair corpus')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = differential(args.per_vocabulary)
    if args.output:
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    agree = sum(r.get('lean parse agrees', 0) for r in report['vocabularies'])
    if report['failure_count']:
        print(json.dumps(report['failures'][:5], indent=2))
        raise SystemExit(f"FAIL: {report['failure_count']} Python/Lean core divergences")
    print(f'PASS: {agree} Python texts read identically by the Lean core parser; '
          'every Lean core rendering parses back in Lean and in Python; no divergences')
