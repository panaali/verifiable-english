"""Python's English grammar over word tokens: a first cut at the tree correspondence (plan section 4, S0).

    uv run python -m conformance.english_lean_tokens [--per-configuration N]

`convert(grammar)` turns the Lark grammar of `ve.english.english_lark_grammar`, after Lark's EBNF
expansion, into a grammar of the reference engine (`conformance.english_lean_engine`) over the tokens of
the reference lexer. The run reads the rendered corpus with it and compares the verdict with Python's
(every rendered text is accepted by Python, so the expected verdict is `one`), and it counts the engine's
steps, which is the Python side of the work budget of plan section 5. Measurement code; no admission path.

The conversion, rule by rule (the correspondence that S2's comparison must apply):

- the sentence is the start symbol; Lark's document rule `(sentence ".")+` is replaced by the lexer's
  sentence split, and `.` never occurs inside a sentence (W4);
- a terminal that is a literal phrase becomes its word tokens in place: a case-sensitive word becomes a `kw`
  terminal (Python lowers a sentence-initial capital before its Earley run; `kw` accepts it instead), a
  case-insensitive word a `content` terminal, a quoted identifier an `exact` quoted token, punctuation an
  `exact` punctuation token;
- an open class becomes a nonterminal: `LABEL` with one rule per letter (`cls label`), `NUMERAL` with
  `cls numeral` and `- cls numeral` (Python's numeral is signed; spec O2), `INT_OP` with `+`, `-`, `*`;
- a rule that uses the never-matching `IMPOSSIBLE` terminal is dropped;
- a constant alternative that is the capitalised spelling of another alternative of the same rule
  (`The api` beside `the api`) is dropped: `kw` accepts the sentence-initial capital, and keeping both would
  give two derivations of a sentence-initial `The api`. Mid-sentence `The api`, which Python's grammar
  derives, is then not derived (a difference to dispose of in S2).
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import random
import re
import time
import warnings

from lark import Lark

from ve.english import EnglishVocabulary, UnreviewedVocabularyWarning, english_lark_grammar, parse_english
from ve.errors import VEError

from conformance import english_lean_engine as E
from conformance import english_lean_lexer as LX
from conformance.english_lean_s0 import _phrase_of_regex, _texts
from conformance.english_surface import configurations

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'conformance' / 'english-lean' / 'tokens-report.json'
DOCUMENT_RULES = {'start', '__start_plus_0'}


class Unconvertible(Exception):
    pass


def _phrase_symbols(phrase: str, case_insensitive: bool) -> list:
    try:
        (tokens,) = LX.lex(phrase + '.')
    except (LX.LexError, ValueError) as e:
        raise Unconvertible(f'phrase {phrase!r} does not lex as one sentence: {e}') from e
    out = []
    for k, tok in enumerate(tokens):
        if tok[0] == 'word':
            out.append(E.T(('content', tok[1]) if case_insensitive else ('kw', tok[1])))
        else:
            if tok[0] == 'punct':
                # The period appended only to make a sentence must not make
                # the phrase's final punctuation look attached on its right.
                tok = ('punct', tok[1], tok[2], tok[3] if k < len(tokens) - 1 else False)
                if tok[1] in (',', ';', ':'):
                    tok = ('punct', tok[1], True, False)
                elif tok[1] == '[':
                    tok = ('punct', '[', False, True)
                elif tok[1] == ']':
                    tok = ('punct', ']', True, False)
            out.append(E.T(('exact', tok)))
    return out


def convert(grammar: str) -> tuple[E.Grammar, list[str], dict]:
    """The engine grammar, its nonterminal names and a record of what the conversion did."""
    lark = Lark(grammar, parser='earley', lexer='dynamic_complete')
    terminals = {t.name: t for t in lark.terminals}
    record = Counter()
    class_rules: dict[str, list[tuple]] = {}

    def symbols(name: str) -> list | None:
        t = terminals[name]
        if name == 'IMPOSSIBLE' or t.pattern.value == '[^\\s\\S]':
            return None
        if name == 'LABEL':
            letters = re.fullmatch(r'\(\?:(.*)\)\[1-9\]\[0-9\]\*', t.pattern.value)
            if not letters:
                raise Unconvertible(f'LABEL pattern {t.pattern.value!r}')
            class_rules['LABEL'] = [(E.T(('cls', ('label', l))),) for l in letters[1].split('|')]
            return [('n', 'LABEL')]
        if name == 'NUMERAL':
            # A sign is free before: the lexer counts its glue there only against a word character
            # (english-lean-e2.md 13), and Python reads no sign glued to a word.
            class_rules['NUMERAL'] = [(E.T(('cls', ('numeral',))),),
                                      (E.T(('exact', ('punct', '-', False, True))), E.T(('cls', ('numeral',))))]
            return [('n', 'NUMERAL')]
        if name == 'INT_OP':
            class_rules['INT_OP'] = [(E.T(('exact', ('punct', c, False, False))),) for c in '+-*']
            return [('n', 'INT_OP')]
        if t.pattern.type == 'str':
            phrase = t.pattern.value
        else:
            phrase = _phrase_of_regex(t.pattern.value)
            if phrase is None:
                raise Unconvertible(f'open regex terminal {name}: {t.pattern.value!r}')
        return _phrase_symbols(phrase, 'i' in t.pattern.flags)

    raw: list[tuple[str, list]] = []
    for r in lark.rules:
        if r.origin.name in DOCUMENT_RULES:
            continue
        rhs: list = []
        for s in r.expansion:
            if s.is_term:
                seq = symbols(s.name)
                if seq is None:
                    rhs = None
                    break
                rhs.extend(seq)
            else:
                rhs.append(('n', s.name))
        if rhs is None:
            record['dropped: uses IMPOSSIBLE'] += 1
            continue
        lhs = r.origin.name
        variants = [rhs]
        for pos, sym in enumerate(rhs):
            if not isinstance(sym, E.T) or sym.a[0] != 'exact' or sym.a[1][0] != 'punct':
                continue
            punct = sym.a[1]
            forms = [punct]
            # The integer marks: glued on the term's side, free on the other (english-lean-e2.md 13).
            if punct[1] == '[':
                forms = [('punct', '[', False, True)]
            elif punct[1] == ']':
                forms = [('punct', ']', True, False)]
            elif punct[1] == '-' and lhs in ('int_term', 'int_neg'):
                forms = [('punct', '-', False, True)]
            variants = [v[:pos] + [E.T(('exact', form))] + v[pos + 1:]
                        for v in variants for form in forms]
        raw.extend((lhs, variant) for variant in variants)
    for name, alternatives in class_rules.items():
        raw.extend((name, list(rhs)) for rhs in alternatives)
    # drop capitalised duplicates of a lower-case alternative of the same rule
    keys = {(lhs, tuple(map(_sym_key, rhs))) for lhs, rhs in raw}
    kept = []
    for lhs, rhs in raw:
        first = rhs[0] if rhs else None
        if isinstance(first, E.T) and first.a[0] == 'kw' and first.a[1][:1].isupper():
            lowered = [E.T(('kw', first.a[1][0].lower() + first.a[1][1:]))] + rhs[1:]
            if (lhs, tuple(map(_sym_key, lowered))) in keys:
                record['dropped: capitalised duplicate'] += 1
                continue
        kept.append((lhs, rhs))
    names = sorted({lhs for lhs, _ in kept} | {s[1] for _, rhs in kept for s in rhs if isinstance(s, tuple)})
    index = {n: i for i, n in enumerate(names)}
    rules = []
    for k, (lhs, rhs) in enumerate(kept):
        rules.append(E.Rule(index[lhs], tuple(E.N(index[s[1]]) if isinstance(s, tuple) else s for s in rhs),
                            0, f'{lhs}#{k}'))
    rank = _ranks(rules, len(names))
    record['rules'] = len(rules)
    record['nonterminals'] = len(names)
    record['rhs_total'] = sum(len(R.rhs) for R in rules)
    record['longest_rhs'] = max(len(R.rhs) for R in rules)
    return E.Grammar(tuple(rules), index['sentence'], tuple(rank)), names, dict(record)


def _sym_key(s):
    return s if isinstance(s, tuple) else (type(s).__name__, s.a if isinstance(s, E.T) else s.A)


def _ranks(rules: list, size: int) -> list[int]:
    """The depth of the left-corner graph; raises on a cycle (left recursion or a unit cycle)."""
    edges: dict[int, set[int]] = {}
    for R in rules:
        if R.rhs and isinstance(R.rhs[0], E.N):
            edges.setdefault(R.lhs, set()).add(R.rhs[0].A)
    depth: dict[int, int] = {}
    active: set[int] = set()

    def visit(A: int) -> int:
        if A in depth:
            return depth[A]
        if A in active:
            raise Unconvertible(f'left-corner cycle through nonterminal {A}')
        active.add(A)
        d = max((visit(B) + 1 for B in edges.get(A, ())), default=0)
        active.discard(A)
        depth[A] = d
        return d

    return [visit(A) for A in range(size)]


def parity(per_configuration: int) -> dict:
    rows = []
    differences = []
    steps_all = []
    earley_all: list[float] = []
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UnreviewedVocabularyWarning)
        for offset, (name, env, options) in enumerate(configurations()):
            G, names, record = convert(english_lark_grammar(env, **options))
            assert E.grammar_wf(G) and E.terminator_free(G)
            verdicts = Counter()
            steps = []
            seconds = 0.0
            earley_cpu = []
            from ve.surface.unambiguity import _parser
            earley = _parser(english_lark_grammar(env, **options))
            for formula, text in _texts(name, env, options, per_configuration, offset):
                (w,) = LX.lex(text)
                stats = E.ParseStats()
                started = time.process_time()
                ts = E.parse(G, E.terminal_accepts, 2, None, w, stats)
                seconds += time.process_time() - started
                verdict = ('zero', 'one', 'many')[len(ts)]
                started = time.process_time()
                earley.parse(text[0].lower() + text[1:])
                earley_cpu.append(time.process_time() - started)
                verdicts[verdict] += 1
                steps.append((stats.steps, len(w)))
                if verdict != 'one':
                    differences.append({'configuration': name, 'text': text, 'verdict': verdict,
                                        'trees': [E.show_tree(G, t) for t in ts][:2]})
            steps_all.extend(steps)
            rows.append({'configuration': name, **record, 'rank_depth': max(G.rank),
                         'verdicts': dict(verdicts), 'max_steps': max(s for s, _ in steps),
                         'max_tokens': max(n for _, n in steps),
                         'cpu_seconds': round(seconds, 3),
                         'earley_cpu_seconds': round(sum(earley_cpu), 3),
                         'earley_cpu_ms_max': round(1000 * max(earley_cpu), 1)})
            earley_all.extend(earley_cpu)
    steps_sorted = sorted(s for s, _ in steps_all)
    q = lambda p: steps_sorted[min(len(steps_sorted) - 1, int(p * len(steps_sorted)))]
    longest = max(steps_all, key=lambda x: x[1])
    ems = sorted(1000 * x for x in earley_all)
    eq = lambda p: round(ems[min(len(ems) - 1, int(p * len(ems)))], 2)
    return {'format': 've.english-lean-tokens@1', 'per_configuration': per_configuration,
            'earley_cpu_ms': {'p50': eq(0.5), 'p95': eq(0.95), 'p99': eq(0.99), 'max': round(ems[-1], 2),
                              'note': 'CPU time of the Lark Earley parse alone (process_time), one sentence each'},
            'configurations': rows, 'differences': differences,
            'steps': {'p50': q(0.5), 'p95': q(0.95), 'p99': q(0.99), 'max': steps_sorted[-1],
                      'at_longest_sentence': {'tokens': longest[1], 'steps': longest[0]}}}


def ambiguity_probe() -> list[dict]:
    """Python's constructed two-derivation sentences (`tests/test_natural.py`): the token grammar must
    find two derivations too."""
    import sys
    from ve import Environment
    sys.path.insert(0, str(ROOT / 'tests'))
    from test_views import vocabulary
    data = vocabulary()
    data['vocabulary']['sorts']['deployed_item'] = {
        'description': 'Deployed item',
        'verbalisation': {'singular': 'deployed service', 'plural': 'deployed services'}}
    env = Environment(data)
    G, _, _ = convert(english_lark_grammar(env))
    out = []
    for sentence in ('Every deployed service is reviewed.',
                     'It is not the case that every deployed service is reviewed.',
                     'Every DEPLOYED service is reviewed.'):
        try:
            parse_english(env, sentence)
            python = 'accepted'
        except VEError as e:
            python = type(e).__name__ + (': two derivations' if 'two derivations' in str(e) else '')
        (w,) = LX.lex(sentence)
        ts = E.parse(G, E.terminal_accepts, 2, None, w)
        out.append({'sentence': sentence, 'python': python, 'tokens': ('zero', 'one', 'many')[len(ts)],
                    'witnesses': [E.show_tree(G, t) for t in ts]})
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--per-configuration', type=int, default=60)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    report = parity(args.per_configuration)
    report['ambiguity_probe'] = ambiguity_probe()
    args.output.write_text(json.dumps(report, indent=1, sort_keys=True, ensure_ascii=False) + '\n')
    print(json.dumps({'differences': len(report['differences']), 'steps': report['steps'],
                      'earley_cpu_ms': report['earley_cpu_ms'],
                      'ambiguity_probe': [(x['python'], x['tokens']) for x in report['ambiguity_probe']]}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
