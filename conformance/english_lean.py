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

For a vocabulary that passes the Lean lexical check `admissible` (so the
Lean theorems apply), a Lean parse that differs from the Python AST, a Lean
rendering that does not parse back in Lean, or a Lean rendering that Python
rejects is a failure; for other vocabularies these are reported by kind. A
Lean rendering that Python reads as a different AST is always a failure. A Python text that the Lean core parser does not read
(contractions, validated negatives, closure, order) is counted as outside the
core skeleton, as are ASTs outside the v0 constructors and vocabularies whose
wording does not tokenize into core templates. Tokenization, capitalisation
and spacing are harness-side (Lean coverage pending for that layer). No model
calls.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
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


def core_tokens(formula, lex):
    """Independent Python model of the core renderer's token grammar.

    This is computed before looking at any Lean result. Equality here is a
    sufficient (not necessary) test that Python produced core wording.
    """
    def depth(node, sort):
        if isinstance(node, (ast.Forall, ast.Exists)):
            return (node.sort == sort) + depth(node.body, sort)
        if isinstance(node, ast.Not): return depth(node.body, sort)
        if isinstance(node, (ast.And, ast.Or, ast.Implies)):
            return max(depth(node.left, sort), depth(node.right, sort))
        return 0

    limits = {sort: depth(formula, sort) for sort in lex['sorts']}

    def ref(sort, scope):
        noun = lex['sorts'][sort]['noun']
        count = sum(s == sort for s, _ in scope)
        if limits[sort] <= 1: return ('plain', sort), noun
        if limits[sort] == 2:
            return (('first' if count == 0 else 'second'), sort), []
        return ('named', sort, count + 1), noun + ['named', [lex['sorts'][sort]['letter'], count + 1]]

    def declaration(sort, scope):
        binding, named = ref(sort, scope)
        if binding[0] in ('first', 'second'):
            named = [binding[0]] + lex['sorts'][sort]['noun']
        return binding, named

    def term(value, scope):
        if isinstance(value, ast.Const): return lex['constants'][value.name]
        binding = scope[value.index][1]
        kind, sort = binding[:2]
        noun = lex['sorts'][sort]['noun']
        if kind == 'plain': return ['that'] + noun
        if kind in ('first', 'second'): return ['the', kind] + noun
        return [[lex['sorts'][sort]['letter'], binding[2]]]

    def clause(node, scope):
        if isinstance(node, ast.Top): return ['this', 'holds', 'in', 'all', 'cases']
        if isinstance(node, ast.Bottom): return ['this', 'is', 'impossible']
        if isinstance(node, ast.Eq): return term(node.left, scope) + ['is', 'the', 'same', 'as'] + term(node.right, scope)
        args = [node.term] if isinstance(node, ast.Unary) else [node.left, node.right]
        return [part
                for word in lex['predicates'][node.predicate]
                for part in ([word] if isinstance(word, str) else term(args[word], scope))]

    def simple(node): return isinstance(node, (ast.Top, ast.Bottom, ast.Unary, ast.Binary, ast.Eq))

    def sentence(node, scope=(), level=0):
        if simple(node): return clause(node, scope)
        if isinstance(node, ast.Not): return ['it', 'is', 'not', 'the', 'case', 'that'] + sentence(node.body, scope, level)
        if isinstance(node, (ast.Forall, ast.Exists)):
            binding, decl = declaration(node.sort, scope)
            body = sentence(node.body, ((node.sort, binding),) + scope, level)
            if isinstance(node, ast.Forall): return ['for', 'every'] + decl + [','] + body
            article = 'an' if decl[0][0] in 'aeiou' else 'a'
            return ['there', 'is', article] + decl + ['such', 'that'] + body
        left, right = node.left, node.right
        if isinstance(node, ast.Implies):
            return ['if'] + sentence(left, scope, level) + [',', 'then'] + sentence(right, scope, level)
        if simple(left) and simple(right):
            if isinstance(node, ast.And): return ['both'] + clause(left, scope) + ['and'] + clause(right, scope)
            return ['either'] + clause(left, scope) + ['or'] + clause(right, scope) + [',', 'or', 'both']
        if isinstance(node, ast.Or): header = ['at', 'least', 'one', 'of', 'the', 'following', 'holds', ':']
        elif isinstance(left, (ast.And, ast.Or, ast.Implies)) or isinstance(right, (ast.And, ast.Or, ast.Implies)):
            header = ['all', 'of', 'the', 'following', 'hold', ':']
        else: header = ['both', 'of', 'the', 'following', 'hold', ':']
        markers = ['(a)', '(b)'] if level % 2 == 0 else ['(i)', '(ii)']
        return header + [markers[0]] + sentence(left, scope, level + 1) + [';', markers[1]] + sentence(right, scope, level + 1)

    return sentence(formula) + ['.']


def core_reading(formula, tokens, lex):
    """Constructively recognize a core derivation of this AST, including synonyms.

    This matcher uses only the Python AST, vocabulary and input tokens. It does
    not consult the Lean renderer or parser. The binder scope determines each
    variable's reference form; all four grammatical declaration forms are tried.
    """
    def take(at, words):
        return at + len(words) if tokens[at:at + len(words)] == words else None

    def term(value, scope):
        if isinstance(value, ast.Const): return lex['constants'][value.name]
        kind, sort, number = scope[value.index]
        noun = lex['sorts'][sort]['noun']
        if kind == 'plain': return ['that'] + noun
        if kind in ('first', 'second'): return ['the', kind] + noun
        return [[lex['sorts'][sort]['letter'], number]]

    def literal(node, scope):
        if isinstance(node, ast.Top): return ['this', 'holds', 'in', 'all', 'cases']
        if isinstance(node, ast.Bottom): return ['this', 'is', 'impossible']
        if isinstance(node, ast.Eq):
            return term(node.left, scope) + ['is', 'the', 'same', 'as'] + term(node.right, scope)
        args = [node.term] if isinstance(node, ast.Unary) else [node.left, node.right]
        return [part for slot in lex['predicates'][node.predicate]
                for part in ([slot] if isinstance(slot, str) else term(args[slot], scope))]

    def simple(node): return isinstance(node, (ast.Top, ast.Bottom, ast.Unary, ast.Binary, ast.Eq))

    def declarations(sort, at):
        noun = lex['sorts'][sort]['noun']
        for kind, words in (('plain', noun), ('first', ['first'] + noun),
                            ('second', ['second'] + noun)):
            end = take(at, words)
            if end is not None:
                yield (kind, sort, 0), end
        end = take(at, noun + ['named'])
        if end is not None and end < len(tokens):
            label = tokens[end]
            if (isinstance(label, list) and len(label) == 2 and
                    label[0] == lex['sorts'][sort]['letter'] and
                    isinstance(label[1], int) and label[1] > 0):
                yield ('named', sort, label[1]), end + 1

    def scan(node, at, scope=(), level=0):
        if simple(node):
            end = take(at, literal(node, scope))
            return set() if end is None else {end}
        if isinstance(node, ast.Not):
            end = take(at, ['it', 'is', 'not', 'the', 'case', 'that'])
            return set() if end is None else scan(node.body, end, scope, level)
        if isinstance(node, (ast.Forall, ast.Exists)):
            if isinstance(node, ast.Forall):
                starts = [['for', 'every']]
            else:
                starts = [['there', 'is', 'a'], ['there', 'is', 'an']]
            ends = set()
            for start in starts:
                pos = take(at, start)
                if pos is None: continue
                for binding, after_decl in declarations(node.sort, pos):
                    if binding in scope: continue
                    after_header = take(after_decl, [','] if isinstance(node, ast.Forall)
                                        else ['such', 'that'])
                    if after_header is not None:
                        ends.update(scan(node.body, after_header, (binding,) + scope, level))
            return ends
        if isinstance(node, ast.Implies):
            pos = take(at, ['if'])
            if pos is None: return set()
            ends = set()
            for middle in scan(node.left, pos, scope, level):
                after_then = take(middle, [',', 'then'])
                if after_then is not None:
                    ends.update(scan(node.right, after_then, scope, level))
            return ends
        ends = set()
        if simple(node.left) and simple(node.right):
            head = ['both'] if isinstance(node, ast.And) else ['either']
            middle_word = ['and'] if isinstance(node, ast.And) else ['or']
            pos = take(at, head + literal(node.left, scope) + middle_word + literal(node.right, scope))
            if pos is not None:
                tail = [] if isinstance(node, ast.And) else [',', 'or', 'both']
                end = take(pos, tail)
                if end is not None: ends.add(end)
        headers = ([['all', 'of', 'the', 'following', 'hold', ':'],
                    ['both', 'of', 'the', 'following', 'hold', ':']]
                   if isinstance(node, ast.And) else
                   [['at', 'least', 'one', 'of', 'the', 'following', 'holds', ':']])
        first, second = (['(a)', '(b)'] if level % 2 == 0 else ['(i)', '(ii)'])
        for header in headers:
            pos = take(at, header + [first])
            if pos is None: continue
            for middle in scan(node.left, pos, scope, level + 1):
                after_marker = take(middle, [';', second])
                if after_marker is not None:
                    ends.update(scan(node.right, after_marker, scope, level + 1))
        return ends

    return len(tokens) - 1 in scan(formula, 0) and tokens[-1:] == ['.']


def run_lean(payload):
    """Returns (admissible, covers, per-case results) from the Lean runner."""
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
    output = json.loads(result.stdout)
    return output['admissible'], output['covers'], output['results']


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


def fixtures(lex):
    """Expected readings are fixed here, independently of the Lean response."""
    top, bottom = ['top'], ['bottom']
    rows = [
        ('noncanonical list', ['both', 'of', 'the', 'following', 'hold', ':', '(a)',
                               'this', 'holds', 'in', 'all', 'cases', ';', '(b)',
                               'this', 'is', 'impossible', '.'], [['and', top, bottom]]),
        ('noncanonical article', None, None),
        ('missing period', ['this', 'holds', 'in', 'all', 'cases'], None),
    ]
    sorts = [s for s in lex['sorts'] if s != '$int']
    if sorts:
        sort = sorts[0]
        noun = lex['sorts'][sort]['noun']
        article = 'a' if noun[0][0] in 'aeiou' else 'an'
        rows[1] = ('noncanonical article', ['there', 'is', article] + noun +
                   ['such', 'that', 'this', 'holds', 'in', 'all', 'cases', '.'],
                   [['exists', sort, top]])
        rows.append(('shadowed binder', ['for', 'every'] + noun + [',', 'there', 'is', 'a'] +
                     noun + ['such', 'that', 'this', 'holds', 'in', 'all', 'cases', '.'], None))
    return [(name, tokens, expected) for name, tokens, expected in rows if tokens is not None]


def differential(per_vocabulary=200, *, full=False):
    # Suggested overlays are accepted explicitly by their configurations.
    warnings.simplefilter('ignore', UnreviewedVocabularyWarning)
    rows, failures = [], []
    corpus_digest = hashlib.sha256()
    total_pairs = 0
    for offset, (name, env, options) in enumerate(configurations()):
        words = EnglishVocabulary(env, **options)
        counts = Counter()
        try:
            lex = lexicon(env, words)
        except Untokenizable as exc:
            rows.append({'vocabulary': name, 'status': 'outside core lexicon', 'reason': str(exc)})
            total_pairs += per_vocabulary
            print(json.dumps(rows[-1]), flush=True)
            continue
        letters = tuple(words.letters.values())
        cases, formulas, is_core = [], [], []
        for formula in corpus(env, words, name, per_vocabulary, offset):
            total_pairs += 1
            corpus_digest.update(json.dumps([name, repr(formula)], separators=(',', ':')).encode() + b'\n')
            if not v0_only(formula):
                counts['outside core AST'] += 1
                continue
            text = render(ast.Document((formula,)), env, 've_english', **options)
            tokens = tokenize(lower_sentence_starts(text), letters)
            cases.append({'tokens': tokens, 'formulas': [wire(formula)]})
            formulas.append(formula)
            is_core.append(tokens == core_tokens(formula, lex) or core_reading(formula, tokens, lex))
        fixed = fixtures(lex)
        fixture_cases = [{'tokens': tokens, 'formulas': [wire(ast.Top())]}
                         for _, tokens, _ in fixed]
        admissible, covers, all_results = run_lean({'environment': environment(env), 'lexicon': lex,
                                                    'cases': cases + fixture_cases})
        if not covers:
            failures.append({'vocabulary': name, 'kind': 'lexicon does not cover environment'})
        results, fixture_results = all_results[:len(cases)], all_results[len(cases):]
        if len(all_results) != len(cases) + len(fixed):
            raise RuntimeError('Lean runner returned the wrong number of results')
        # For an admitted lexicon the Lean theorems (checked_parse_render,
        # checked_unique_derivation) apply; every divergence is a failure. For
        # other lexicons Lean results are reported, and only Python's reading
        # of the Lean text is required to be faithful when Python accepts it.
        def problem(kind, **detail):
            if admissible:
                failures.append({'vocabulary': name, 'kind': kind, **detail})
            else:
                counts['outside admitted lexicon: ' + kind] += 1
        for (fixture_name, tokens, expected), result in zip(fixed, fixture_results, strict=True):
            if (expected is None or admissible) and result['parsed'] != expected:
                failures.append({'vocabulary': name, 'kind': 'fixture reading', 'fixture': fixture_name,
                                 'tokens': tokens, 'expected': expected, 'lean': result['parsed']})
            counts['fixture ' + ('accepted' if expected is not None else 'rejected')] += 1
        for formula, case, core, result in zip(formulas, cases, is_core, results, strict=True):
            expected = [wire(formula)]
            if result['parsed'] is None:
                if core or result['rendered'] == case['tokens']:
                    failures.append({'vocabulary': name, 'kind': 'missing core parse',
                                     'tokens': case['tokens'], 'expected': expected})
                else:
                    counts['python text outside core wording'] += 1
            elif result['parsed'] == expected:
                counts['lean parse agrees'] += 1
            else:
                problem('lean parse differs', tokens=case['tokens'], expected=expected, lean=result['parsed'])
            if not result['checked']:
                failures.append({'vocabulary': name, 'kind': 'lean rejects checked AST', 'formula': expected})
                continue
            if result['roundtrip']:
                counts['lean core round trip'] += 1
            else:
                problem('lean round trip', formula=expected, rendered=result['rendered'])
            if result['rendered'] == case['tokens']:
                counts['identical canonical text'] += 1
            if core:
                counts['independently identified core text'] += 1
            lean_text = detokenize(result['rendered'])
            try:
                reread = parse_english(env, lean_text, **options)
            except Exception as exc:  # any rejection by the Python parser is a divergence
                problem('python rejects lean core text', text=lean_text,
                        error=f'{type(exc).__name__}: {exc}'[:500])
                continue
            if reread == ast.Document((formula,)):
                counts['python reads lean core text'] += 1
            else:
                failures.append({'vocabulary': name, 'kind': 'python reads lean core text differently',
                                 'text': lean_text, 'expected': expected})
        rows.append({'vocabulary': name, 'status': 'compared', 'lean_admissible': admissible,
                     'lean_covers': covers,
                     'asts': len(formulas) + counts['outside core AST'],
                     **dict(sorted(counts.items()))})
        print(json.dumps(rows[-1]), flush=True)
    if full and (per_vocabulary != 5000 or total_pairs != 85000 or len(rows) != 17):
        failures.append({'kind': 'full corpus gate', 'pairs': total_pairs,
                         'vocabularies': len(rows), 'per_vocabulary': per_vocabulary})
    return {'method': 'independent Python core classification; Python render -> Lean core parse; Lean core render -> Lean parse and Python parse',
            'seed': SEED, 'corpus_sha256': corpus_digest.hexdigest(), 'pairs': total_pairs,
            'full_gate': full, 'per_vocabulary': per_vocabulary, 'vocabularies': rows, 'failures': failures[:200],
            'failure_count': len(failures)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--per-vocabulary', type=int, default=200,
                        help='ASTs per vocabulary; 5000 replays the full 85,000-pair corpus')
    parser.add_argument('--full', action='store_true', help='require exactly 17 x 5000 = 85,000 pairs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = differential(args.per_vocabulary, full=args.full)
    if args.output:
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    agree = sum(r.get('lean parse agrees', 0) for r in report['vocabularies'])
    admitted = [r['vocabulary'] for r in report['vocabularies'] if r.get('lean_admissible')]
    if report['failure_count']:
        print(json.dumps(report['failures'][:5], indent=2))
        raise SystemExit(f"FAIL: {report['failure_count']} Python/Lean core divergences")
    print(f'PASS: {agree} Python texts read identically by the Lean core parser; '
          f'{len(admitted)} vocabularies pass the Lean lexical check, and for them every Lean core '
          'rendering parses back in Lean and in Python; no divergences')
