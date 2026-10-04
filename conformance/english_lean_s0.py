"""S0 measurements for English in Lean (plan section 5, spec section 7): grammar sizes, shape checks,
terminal classes, synthetic limit environments, sentence lengths in tokens and lexer probes.

    uv run python -m conformance.english_lean_s0 [--per-configuration N] [--output PATH]

Writes `conformance/english-lean/s0-report.json`; `docs/spec/english-lean-measured.md` summarises it.
No model calls. Nothing here is on an admission path.

What is measured, per configuration of `conformance.english_surface` (17 vocabularies) and per
synthetic limit environment:

- the size of Python's generated grammar after Lark's EBNF expansion: rules, nonterminals, the longest
  right-hand side and `|G|` (the total length of the right-hand sides);
- whether any expanded rule is empty, and whether the left-corner graph has a cycle (left recursion or a
  unit cycle); when it has none, the depth of the graph is the largest `rank` a certificate needs;
- every terminal by class: a literal string, a regex that is a fixed word sequence (a phrase that the Lean
  grammar writes as word tokens), or an open regex class; and every terminal phrase that the draft lexer
  (`conformance.english_lean_lexer`) rejects or splits into several tokens;
- for `data@0`, the attribute-property product and its factored size (spec 2.10, D13);
- on the rendered corpus: the lexer's outcome on every accepted text, the token length of every sentence,
  and token-preserving spacing mutants (spec O1) read by Python's full pipeline.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import random
import re
import time

from lark import Lark

from ve import ast, Environment, render
from ve.english import EnglishVocabulary, english_lark_grammar, parse_english
from ve.errors import VEError

from conformance import english_lean_lexer as LX
from conformance.english_surface import SEED, configurations, directed_formulas, random_formula

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'conformance' / 'english-lean' / 's0-report.json'


# ------------------------------------------------------------------ grammar shape

def _phrase_of_regex(pattern: str) -> str | None:
    """The word sequence a regex stands for, when it is one: `\\s+`-joined escaped literal parts, as
    `ve.english._literal_pattern` builds them. Otherwise `None` (an open class)."""
    parts = pattern.split(r'\s+')
    words = []
    for part in parts:
        plain = re.sub(r'\\(.)', r'\1', part)
        if not plain or re.escape(plain) != part:
            return None
        words.append(plain)
    return ' '.join(words)


def _lex_phrase(phrase: str) -> tuple[str, int]:
    """('ok', token count) or (reject code, 0) for a terminal phrase, read as one sentence."""
    try:
        sentences = LX.lex(phrase + '.')
    except LX.LexError as e:
        return e.code, 0
    return 'ok', sum(len(s) for s in sentences)


def grammar_inventory(grammar: str) -> dict:
    lark = Lark(grammar, parser='earley', lexer='dynamic_complete')
    rules = lark.rules
    nonterminals = {r.origin.name for r in rules}
    empty = [r.origin.name for r in rules if not r.expansion]
    edges: dict[str, set[str]] = {}
    for r in rules:
        if r.expansion and not r.expansion[0].is_term:
            edges.setdefault(r.origin.name, set()).add(r.expansion[0].name)
    # depth of the left-corner graph; a cycle means left recursion or a unit cycle
    depth: dict[str, int] = {}
    on_stack: set[str] = set()
    cycles: list[str] = []

    def visit(A: str) -> int:
        if A in depth:
            return depth[A]
        if A in on_stack:
            cycles.append(A)
            return 0
        on_stack.add(A)
        d = 0
        for B in edges.get(A, ()):
            d = max(d, visit(B) + 1)
        on_stack.discard(A)
        depth[A] = d
        return d

    for A in sorted(nonterminals):
        visit(A)
    classes = Counter()
    open_classes = []
    split_phrases = Counter()
    unlexable = []
    for t in lark.terminals:
        if t.name in {'WS', 'IMPOSSIBLE'}:
            classes['layout-or-impossible'] += 1
            continue
        if t.pattern.type == 'str':
            phrase = t.pattern.value
            classes['literal'] += 1
        else:
            phrase = _phrase_of_regex(t.pattern.value)
            if phrase is None:
                classes['open-regex'] += 1
                open_classes.append({'name': t.name, 'pattern': t.pattern.value})
                continue
            classes['phrase-regex'] += 1
        status, count = _lex_phrase(phrase)
        if status != 'ok':
            unlexable.append({'phrase': phrase, 'reject': status})
        elif count > 1:
            split_phrases[count] += 1
    return {
        'rules': len(rules), 'nonterminals': len(nonterminals),
        'longest_rhs': max((len(r.expansion) for r in rules), default=0),
        'rhs_total': sum(len(r.expansion) for r in rules),
        'empty_rules': sorted(set(empty)),
        # Lark expands the document-level `(sentence ".")+` left-recursively; the Lean design splits
        # sentences in the lexer instead, so that one cycle is not part of the sentence grammar.
        'left_corner_cycles': sorted(set(cycles) - {'__start_plus_0'}),
        'document_level_cycles': sorted(set(cycles) & {'__start_plus_0'}),
        'rank_depth': max(depth.values(), default=0),
        'terminals': dict(classes), 'open_regex_terminals': open_classes,
        'phrases_by_token_count': {str(k): v for k, v in sorted(split_phrases.items())},
        'unlexable_phrases': unlexable,
    }


def attribute_product(env) -> dict:
    """Python's `the R of t is P` alternatives (english.py, data@0) and the factored count of D13."""
    if 'data@0' not in env.profiles:
        return {'pairs': 0, 'relations': 0, 'properties': 0, 'factored_rules': 0}
    relations = [(n, d) for n, d in env.predicates.items()
                 if len(d.arguments) == 2 and d.functional and d.total and d.arguments[1] != '$string']
    value_sorts = {d.arguments[1] for _, d in relations}
    properties = [n for n, d in env.predicates.items() if len(d.arguments) == 1 and d.arguments[0] in value_sorts]
    pairs = sum(1 for _, d in relations for p in properties if env.predicates[p].arguments == (d.arguments[1],))
    return {'pairs': pairs, 'relations': len(relations), 'properties': len(properties),
            'factored_rules': len(relations) + len(properties)}


# ------------------------------------------------------------------ synthetic limit environments

def _word(k: int) -> str:
    letters = 'bcdfghjklmnpqrstvwxz'
    out = ''
    k += 20
    while k:
        k, r = divmod(k, len(letters))
        out = letters[r] + 'a' + out
    return 'qu' + out


DATA_HEADER = {'language': 've.core@0.2', 'profiles': ['data@0', 'relational-fol@0'],
               'spec_revision': 've-v0.2-expand2-2026-09-25'}
ORDER_HEADER = {'language': 've.core@0.1', 'profiles': ['order@0', 'relational-fol@0'],
                'spec_revision': 've-v0.1-order-2026-09-22'}


def synthetic_environments():
    """Limit-size environments across declaration shapes (plan section 5, S0 inventory)."""
    sorts = {'service': {'description': 'A service.'}, 'shade': {'description': 'A shade.'}}
    constants = {'legacy': {'sort': 'service', 'description': 'Legacy.'}}

    def env(header, predicates, sorts=sorts, constants=constants):
        return Environment({**header, 'vocabulary': {'sorts': sorts, 'predicates': predicates,
                                                     'constants': constants}})

    yield 'unary-256-mechanical', env(DATA_HEADER, {
        _word(k): {'arguments': ['service'], 'description': 'A property.'} for k in range(256)})
    yield 'unary-256-declared', env(DATA_HEADER, {
        _word(k): {'arguments': ['service'], 'description': 'A property.',
                   'verbalisation': '{0} is ' + _word(k)} for k in range(256)})
    yield 'binary-256-declared', env(DATA_HEADER, {
        _word(k): {'arguments': ['service', 'service'], 'description': 'A relation.',
                   'verbalisation': '{0} ' + _word(k) + 's {1}'} for k in range(256)})
    product = {_word(k): {'arguments': ['service', 'shade'], 'description': 'An attribute.',
                          'functional': True, 'total': True} for k in range(128)}
    product.update({_word(128 + k): {'arguments': ['shade'], 'description': 'A property.'} for k in range(128)})
    yield 'data-128x128', env(DATA_HEADER, product)
    yield 'order-256-int-slots', env(ORDER_HEADER, {
        _word(k): {'arguments': ['service', '$int'], 'description': 'A cost.',
                   'verbalisation': '{0} ' + _word(k) + 's {1}'} for k in range(256)},
        sorts={'service': {'description': 'A service.'}},
        constants={'legacy': {'sort': 'service', 'description': 'Legacy.'},
                   'budget': {'sort': '$int', 'description': 'Budget.'}})


# ------------------------------------------------------------------ corpus probes

def _texts(name, env, options, n, offset):
    rng = random.Random(SEED + 500_000 + offset)
    words = EnglishVocabulary(env, **options)
    formulas = list(dict.fromkeys(directed_formulas(env, words)))[: n // 2]
    seen = set(formulas)
    tries = 0
    while len(formulas) < n and tries < 20 * n:
        tries += 1
        f = random_formula(rng, env, rng.randrange(2, 8))
        if f not in seen:
            seen.add(f)
            formulas.append(f)
    for f in formulas:
        yield f, render(ast.Document((f,)), env, 've_english', **options)


def _mutants(text: str) -> list[tuple[str, str]]:
    """Token-preserving spacing mutants: the draft lexer gives each the tokens of `text`."""
    out = []
    for kind, pattern, repl in (('space-before-punct', r'(?<=\w)([,;:])', r' \1'),
                                ('no-space-after-punct', r'([,;:]) (?=\w)', r'\1'),
                                ('spaced-hyphen', r'(?<=\w)-(?=\w)', ' - '),
                                ('spaced-marker', r'\((a|b|i|ii)\)', r'( \1 )')):
        m = re.sub(pattern, repl, text, count=1)
        if m != text:
            out.append((kind, m))
    return out


def corpus_probe(per_configuration: int) -> dict:
    lengths = Counter()
    rejects = Counter()
    reject_examples = {}
    mutant_counts = Counter()
    mutant_examples = []
    texts_seen = 0
    sentences_seen = 0
    for offset, (name, env, options) in enumerate(configurations()):
        for formula, text in _texts(name, env, options, per_configuration, offset):
            texts_seen += 1
            try:
                sentences = LX.lex(text)
            except LX.LexError as e:
                rejects[e.code] += 1
                reject_examples.setdefault(e.code, {'configuration': name, 'text': text})
                continue
            for s in sentences:
                sentences_seen += 1
                lengths[len(s)] += 1
            for kind, mutant in _mutants(text):
                same_tokens = _same_tokens(text, mutant)
                try:
                    doc = parse_english(env, mutant, **options)
                    verdict = 'same' if doc == ast.Document((formula,)) else 'different'
                except VEError as e:
                    verdict = 'rejected:' + type(e).__name__
                mutant_counts[(kind, same_tokens, verdict)] += 1
                if verdict != 'same' and len(mutant_examples) < 12 and same_tokens:
                    mutant_examples.append({'configuration': name, 'kind': kind, 'text': text,
                                            'mutant': mutant, 'python': verdict})
    total = sum(lengths.values())
    cumulative, p = 0, {}
    for k in sorted(lengths):
        cumulative += lengths[k]
        for q in (50, 90, 95, 99, 100):
            if q not in p and cumulative * 100 >= q * total:
                p[q] = k
    return {
        'texts': texts_seen, 'sentences': sentences_seen,
        'lexer_rejections': dict(rejects), 'lexer_rejection_examples': reject_examples,
        'token_length_percentiles': {f'p{q}': v for q, v in sorted(p.items())},
        'token_length_histogram': {str(k): lengths[k] for k in sorted(lengths)},
        'spacing_mutants': [{'kind': k, 'same_tokens': s, 'python': v, 'count': c}
                            for (k, s, v), c in sorted(mutant_counts.items())],
        'spacing_mutant_examples': mutant_examples,
    }


def _same_tokens(a: str, b: str) -> bool:
    try:
        return LX.lex(a) == LX.lex(b)
    except LX.LexError:
        return False


# ------------------------------------------------------------------ the report

def measure(per_configuration: int = 60) -> dict:
    rows = []
    for name, env, options in configurations():
        started = time.perf_counter()
        inv = grammar_inventory(english_lark_grammar(env, **options))
        rows.append({'configuration': name, 'environment_id': env.environment_id,
                     **inv, 'attribute_product': attribute_product(env),
                     'seconds': round(time.perf_counter() - started, 3)})
    synthetic = []
    for name, env in synthetic_environments():
        started = time.perf_counter()
        words = EnglishVocabulary(env)
        inv = grammar_inventory(english_lark_grammar(env))
        product = attribute_product(env)
        synthetic.append({'environment': name, 'predicates': len(env.predicates),
                          'declared_wordings_kept': sum(1 for n, d in env.predicates.items()
                                                        if d.verbalisation and words.predicates[n] == d.verbalisation),
                          **{k: inv[k] for k in ('rules', 'nonterminals', 'longest_rhs', 'rhs_total',
                                                 'empty_rules', 'left_corner_cycles', 'rank_depth')},
                          'attribute_product': product,
                          'rules_after_factoring': inv['rules'] - product['pairs'] + product['factored_rules'],
                          'seconds': round(time.perf_counter() - started, 3)})
    return {'format': 've.english-lean-s0@1', 'per_configuration': per_configuration,
            'configurations': rows, 'synthetic': synthetic,
            'corpus': corpus_probe(per_configuration)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--per-configuration', type=int, default=60)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    report = measure(args.per_configuration)
    args.output.write_text(json.dumps(report, indent=1, sort_keys=True, ensure_ascii=False) + '\n')
    print(args.output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
