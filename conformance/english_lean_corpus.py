"""Run the English-in-Lean engine corpus against the Python reference engine.

    uv run python -m conformance.english_lean_corpus [--json]

Every case of `conformance/english-lean/engine.json` (spec 8.1 to 8.3 and 8.7) is checked against
`conformance.english_lean_engine`. A case passes when the reference engine gives exactly the
hand-derived expectation. The run also reports what the Lean prototype of S1a is compared with:
the budget threshold of g16, the step count of g17 against the bound of spec 2.6, and the
counts of g18. No model calls; nothing here is on an admission path.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
import random

from conformance import english_lean_engine as E

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / 'conformance' / 'english-lean' / 'engine.json'
ACC = E.terminal_accepts


def load(path: Path = CORPUS) -> dict:
    return json.loads(path.read_text())


def _grammar(corpus: dict, name: str) -> tuple[E.Grammar, list[str]]:
    return E.grammar_from_json(corpus['grammars'][name])


def _tokens(xs: list) -> list:
    return [E.token_from_json(x) for x in xs]


def _shows(G: E.Grammar, ts: list) -> list[str]:
    return [E.show_tree(G, t) for t in ts]


# ------------------------------------------------------------------ test libraries (corpus "libraries")

def _library(name: str, names: list[str]) -> tuple[E.Sig, callable, list[E.Action]]:
    sig = E.Sig('tok')
    if name in ('GA', 'GA3'):
        ty = lambda A: 'num'
        value = E.Action(('tok',), 'num', lambda tok: tok[1])
        if name == 'GA':
            add = E.Action(('tok', 'num', 'tok', 'num', 'tok'), 'num', lambda _a, x, _b, y, _c: x + y)
        else:
            add = E.Action(('tok', 'num', 'tok'), 'num', lambda _a, x, _b: x)
        return sig, ty, [value, add]
    if name == 'G1':
        types = {'S': 'sent', 'A': 'a'}
        ty = lambda A: types.get(names[A], 'none') if A < len(names) else 'none'
        acts = [E.Action(('tok', 'a'), 'sent', lambda _t, x: x),
                E.Action(('tok',), 'a', lambda _t: 1),
                E.Action(('tok',), 'sent', lambda _t: 2),
                E.Action(('tok', 'tok'), 'sent', lambda _t, _u: 3),
                E.Action(('tok',), 'a', lambda _t: 9)]
        return sig, ty, acts
    raise KeyError(name)


def _meaning(name: str, G: E.Grammar):
    consulted = []

    def mu1(st, t):
        consulted.append(t)
        return st, False, st + 1

    def mu2(st, t):
        consulted.append(t)
        raise E.Rejected('no')

    def mu_r10(st, t):
        consulted.append(t)
        if G.rules[t.rule].tag == 'r0':
            return st, False, st + 1
        raise E.Rejected('no')

    return {'mu1': mu1, 'mu2': mu2, 'mu-r9': mu1, 'mu-r10': mu_r10}[name], consulted


def _outcome_json(G: E.Grammar, o: tuple) -> list:
    if o[0] == 'ambiguous':
        return ['ambiguous', E.show_tree(G, o[1]), E.show_tree(G, o[2])]
    if o[0] == 'stopped':
        return ['stopped', o[1], _outcome_json(G, o[2])]
    if o[0] == 'ok' and isinstance(o[1], list):
        return ['ok', [list(x) for x in o[1]]]
    return list(o)


# ------------------------------------------------------------------ the parse checks

def _check_parse(G: E.Grammar, w: list, cap: int, budget: int, expect: dict, where: str) -> list[str]:
    failures = []
    ts = E.parse(G, ACC, cap, budget, w)
    if ts is None:
        return [f'{where}: budget exhausted']
    shown = _shows(G, ts)
    if len(set(shown)) != len(shown):
        failures.append(f'{where}: duplicate trees {shown}')
    for t in ts:
        if not E.is_derivation(G, ACC, w, t):
            failures.append(f'{where}: returned tree is not a derivation: {E.show_tree(G, t)}')
    if 'trees' in expect and sorted(shown) != sorted(expect['trees']):
        failures.append(f'{where}: trees {shown}, expected {expect["trees"]}')
    if 'count' in expect:
        if len(ts) != expect['count'] or not set(shown) <= set(expect['among']):
            failures.append(f'{where}: {shown} is not {expect["count"]} members of {expect["among"]}')
    if 'complete' in expect and (len(ts) < cap) != expect['complete']:
        failures.append(f'{where}: complete is {len(ts) < cap}, expected {expect["complete"]}')
    if 'verdict' in expect:
        v = E.verdict(G, ACC, budget, w)
        if v is None or v[0] != expect['verdict']:
            failures.append(f'{where}: verdict {v and v[0]}, expected {expect["verdict"]}')
    return failures


def _random_grammar(rng: random.Random, spec: dict) -> E.Grammar:
    """Mostly well-formed: distinct ranks, and a leading nonterminal of lower rank, except with a
    small probability, so that the not-well-formed side is exercised too. Duplicate rules and
    shared terminals give ambiguity."""
    k = spec['nonterminals']
    rank = list(range(k))
    rng.shuffle(rank)
    rules: list[E.Rule] = []
    for r in range(rng.randint(2, spec['max_rules'])):
        if rules and rng.random() < 0.2:
            R = rng.choice(rules)
            rules.append(E.Rule(R.lhs, R.rhs, 0, f'r{r}'))
            continue
        lhs = 0 if r == 0 else rng.randrange(k)
        rhs = []
        for d in range(rng.randint(1, spec['max_rhs'])):
            lower = [A for A in range(k) if rank[A] < rank[lhs]]
            pool = lower if d == 0 and rng.random() > 0.1 else list(range(k))
            if pool and rng.random() < 0.5:
                rhs.append(E.N(rng.choice(pool)))
            else:
                rhs.append(E.T(('kw', rng.choice(spec['terminals']))))
        rules.append(E.Rule(lhs, tuple(rhs), 0, f'r{r}'))
    return E.Grammar(tuple(rules), 0, tuple(rank))


def run_case(corpus: dict, case: dict, report: dict | None = None) -> list[str]:
    """The failures of one case, as messages. Measurements go into `report`."""
    report = report if report is not None else {}
    kind = case['kind']
    cid = case['id']
    budget = case.get('budget', corpus['default_budget'])
    if not isinstance(budget, int):
        budget = corpus['default_budget']
    cap = case.get('cap', 2)
    failures: list[str] = []

    if kind == 'parse':
        G, _ = _grammar(corpus, case['grammar'])
        return _check_parse(G, _tokens(case['input']), cap, budget, case['expect'], cid)

    if kind == 'parse-each':
        G, _ = _grammar(corpus, case['grammar'])
        expect = case['expect']
        for n, xs in enumerate(case['inputs']):
            w = _tokens(xs)
            where = f'{cid}[{n}]'
            sub = {k: v for k, v in expect.items() if k in ('verdict', 'trees', 'complete')}
            failures += _check_parse(G, w, cap, budget, sub, where)
            ts = E.parse(G, ACC, cap, budget, w) or []
            want = expect.get('rule_of_child') or (expect.get('rules_of_child') or [None] * 9)[n]
            if want and (len(ts) != 1 or G.rules[ts[0].kids[1].rule].tag != want):
                failures.append(f'{where}: expected the child rule {want}, got {_shows(G, ts)}')
        return failures

    if kind == 'not-wf':
        for name in case['grammars']:
            G, _ = _grammar(corpus, name)
            if E.grammar_wf(G):
                failures.append(f'{cid}: {name} is well-formed')
            for xs in case['inputs']:
                w = _tokens(xs)
                ts = E.parse(G, ACC, 8, budget, w)
                if ts is None:
                    failures.append(f'{cid}: {name} exhausted the budget')
                    continue
                for t in ts:
                    if not E.is_derivation(G, ACC, w, t):
                        failures.append(f'{cid}: {name} returned a tree that is not a derivation')
        return failures

    if kind == 'budget-sweep':
        G, _ = _grammar(corpus, case['grammar'])
        w = _tokens(case['input'])
        same = next(c for c in corpus['cases'] if c['id'] == case['same_as'])
        want = sorted(same['expect']['trees'])
        threshold = None
        for b in range(0, 10_000):
            ts = E.parse(G, ACC, 2, b, w)
            if ts is None:
                if threshold is not None:
                    failures.append(f'{cid}: budget {b} gave no result after {threshold} did')
                    break
                continue
            if sorted(_shows(G, ts)) != want:
                failures.append(f'{cid}: budget {b} gave {_shows(G, ts)}')
                break
            if threshold is None:
                threshold = b
            if b > threshold + 50:
                break
        if threshold is None:
            failures.append(f'{cid}: no budget below 10,000 gave a result')
        report['g16_threshold'] = threshold
        return failures

    if kind == 'steps':
        G, _ = _grammar(corpus, case['grammar'])
        w = [('word', case['input_word'], False)] * case['input_length']
        stats = E.ParseStats()
        ts = E.parse(G, ACC, 2, None, w, stats)
        if ts != []:
            failures.append(f'{cid}: expected no derivation, got {len(ts or [])}')
        size = sum(len(R.rhs) for R in G.rules)
        n = len(w)
        bound = size * n ** 3 * 2 ** 2
        report['g17'] = {'steps': stats.steps, 'G': size, 'n': n, 'cap': 2, 'unit_bound': bound,
                         'ratio': round(stats.steps / bound, 6), 'entry_members': stats.entries,
                         'suffix_members': stats.suffix_members}
        if stats.steps > bound:
            failures.append(f'{cid}: {stats.steps} steps exceed |G| n^3 cap^2 = {bound}')
        return failures

    if kind == 'random':
        rng = random.Random(case['seed'])
        counts = {'wf': 0, 'not_wf': 0, 'inputs': 0, 'saturated': 0, 'max_derivations': 0}
        terminals = case['terminals']
        inputs = [list(p) for n in range(0, case['max_input_length'] + 1)
                  for p in itertools.product(terminals, repeat=n)]
        for g in range(case['grammars']):
            G = _random_grammar(rng, case)
            wf = E.grammar_wf(G)
            counts['wf' if wf else 'not_wf'] += 1
            for xs in inputs:
                w = [('word', x, False) for x in xs]
                counts['inputs'] += 1
                ts = E.parse(G, ACC, case['cap'], budget, w)
                if ts is None:
                    failures.append(f'{cid}: grammar {g} exhausted the budget on {xs}')
                    continue
                for t in ts:
                    if not E.is_derivation(G, ACC, w, t):
                        failures.append(f'{cid}: grammar {g}, {xs}: not a derivation')
                if not wf:
                    continue
                every = E.enumerate_all(G, ACC, w)
                counts['max_derivations'] = max(counts['max_derivations'], len(every))
                if len(set(ts)) != len(ts) or len(ts) != min(case['cap'], len(every)):
                    failures.append(f'{cid}: grammar {g}, {xs}: {len(ts)} trees, {len(every)} derivations')
                elif len(every) <= case['cap'] and set(ts) != set(every):
                    failures.append(f'{cid}: grammar {g}, {xs}: tree set differs from the enumeration')
                if len(every) > case['cap']:
                    counts['saturated'] += 1
                # Beyond the fixture: small caps exercise truncation (the cap invariant of 2.6).
                for c in case.get('also_caps', ()):
                    small = E.parse(G, ACC, c, budget, w)
                    if (small is None or len(set(small)) != len(small) or len(small) != min(c, len(every))
                            or not set(small) <= set(every)):
                        failures.append(f'{cid}: grammar {g}, {xs}, cap {c}: wrong truncation')
                    elif len(every) > c:
                        counts['saturated_small_cap'] = counts.get('saturated_small_cap', 0) + 1
            if len(failures) > 20:
                break
        report['g18'] = counts
        return failures

    if kind == 'all-returned-derive':
        return []   # checked inside every parse case above

    if kind == 'saturation':
        G, _ = _grammar(corpus, case['grammar'])
        w = _tokens(case['input'])
        expect = case['expect']
        every = E.enumerate_all(G, ACC, w)
        if len(every) != expect['derivations']:
            failures.append(f'{cid}: {len(every)} derivations, expected {expect["derivations"]}')
        for key, c in (('cap64', 64), ('cap129', 129)):
            ts = E.parse(G, ACC, c, budget, w)
            want = expect[key]
            if ts is None or len(ts) != want['count'] or len(set(ts)) != len(ts) or (len(ts) < c) != want['complete']:
                failures.append(f'{cid}: cap {c} gave {None if ts is None else len(ts)} trees')
            elif not set(ts) <= set(every):
                failures.append(f'{cid}: cap {c} returned a tree the enumeration lacks')
        return failures

    if kind in ('typed', 'value'):
        G, names = _grammar(corpus, case['grammar'])
        sig, ty, acts = _library(case['library'], names)
        typed = E.grammar_typed(G, sig, ty, acts)
        if kind == 'typed':
            return [] if typed == case['expect']['typed'] else [f'{cid}: typed is {typed}']
        w = _tokens(case['input'])
        v = E.verdict(G, ACC, budget, w)
        if v is None or v[0] != case['expect']['verdict']:
            return [f'{cid}: verdict {v}']
        val = E.tree_sem(G, sig, acts, v[1])
        want = case['expect']['value']
        if want is None:
            return [] if val is None else [f'{cid}: value {val}, expected none']
        return [] if val == (case['expect']['type'], want) else [f'{cid}: value {val}']

    if kind == 'read-sentence':
        G, _ = _grammar(corpus, case['grammar'])
        mu, consulted = _meaning(case['meaning'], G)
        w = _tokens(case['input'])
        if case.get('budget') == 'below the threshold of g16':
            g16 = next(c for c in corpus['cases'] if c['id'] == 'g16')
            sub: dict = {}
            run_case(corpus, g16, sub)
            budget = sub['g16_threshold'] - 1
        o, st = E.read_sentence(G, ACC, mu, case['state'], budget, w)
        expect = case['expect']
        got = _outcome_json(G, o)
        if got != expect['outcome'] or st != expect['state']:
            failures.append(f'{cid}: {got}, state {st}; expected {expect["outcome"]}, state {expect["state"]}')
        if expect.get('meaning_consulted') is False and consulted:
            failures.append(f'{cid}: the meaning was consulted')
        return failures

    if kind == 'read-document':
        G, _ = _grammar(corpus, case['grammar'])
        mu, _ = _meaning(case['meaning'], G)
        o, st = E.read_document(G, ACC, mu, case['state'], budget, [_tokens(xs) for xs in case['inputs']])
        got = _outcome_json(G, o)
        expect = case['expect']
        if got != expect['outcome'] or st != expect['state']:
            failures.append(f'{cid}: {got}, state {st}; expected {expect["outcome"]}, state {expect["state"]}')
        return failures

    if kind == 'reading-set':
        G, _ = _grammar(corpus, case['grammar'])
        mu, _ = _meaning(case['meaning'], G)
        w = _tokens(case['input'])
        ts = E.parse(G, ACC, cap, budget, w)
        expect = case['expect']
        readings = [list(x) for x in E.reading_set(mu, case['state'], ts)]
        if readings != expect['readings']:
            failures.append(f'{cid}: readings {readings}, expected {expect["readings"]}')
        if 'trees' in expect and sorted(_shows(G, ts)) != sorted(expect['trees']):
            failures.append(f'{cid}: trees {_shows(G, ts)}')
        if 'complete' in expect and (len(ts) < cap) != expect['complete']:
            failures.append(f'{cid}: complete is {len(ts) < cap}')
        if 'read_outcome' in expect:
            o, _ = E.read_sentence(G, ACC, mu, case['state'], budget, w)
            if o[0] != expect['read_outcome']:
                failures.append(f'{cid}: read outcome {o[0]}')
        return failures

    if kind == 'extension':
        G, names = _grammar(corpus, case['small'])
        G2, names2 = _grammar(corpus, case['large'])
        # One action table: an action index names the same action in both grammars.
        sig, ty, acts = _library(case['library'], names)
        acts2 = acts
        rm = case['rule_map']
        e = E.RuleMap(lambda r: rm['rule'][r] if r < len(rm['rule']) else r + 1000,
                      lambda A: rm['nt'][A] if A < len(rm['nt']) else A + 1000)
        ok, clause = E.rule_map_ok(e, G, G2, acts, acts2)
        expect = case['expect']
        if ok != expect['ok']:
            return [f'{cid}: RuleMap.Ok is {ok} ({clause})']
        if not ok:
            return [] if clause == expect['failing_clause'] else [f'{cid}: failing clause {clause}']
        w = _tokens(case['input'])
        v = E.verdict(G, ACC, budget, w)
        v2 = E.verdict(G2, ACC, budget, w)
        image = E.rule_map_tree(e, v[1])
        if E.show_tree(G2, image) != expect['image'] or not E.is_derivation(G2, ACC, w, image):
            failures.append(f'{cid}: image {E.show_tree(G2, image)}')
        if v2 is None or v2[0] != expect['large_verdict']:
            failures.append(f'{cid}: larger grammar verdict {v2 and v2[0]}')
        if expect.get('same_value') and E.tree_sem(G2, sig, acts2, image) != E.tree_sem(G, sig, acts, v[1]):
            failures.append(f'{cid}: the image has another value')
        return failures

    return [f'{cid}: unknown kind {kind}']


def run(corpus: dict | None = None) -> tuple[dict, list[str]]:
    corpus = corpus or load()
    report: dict = {'cases': len(corpus['cases'])}
    failures: list[str] = []
    for case in corpus['cases']:
        failures += run_case(corpus, case, report)
    report['failures'] = len(failures)
    return report, failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--json', action='store_true', help='print the report as JSON')
    args = parser.parse_args(argv)
    report, failures = run()
    if args.json:
        print(json.dumps({'report': report, 'failures': failures}, indent=2, sort_keys=True))
    else:
        for f in failures:
            print('FAIL', f)
        print(json.dumps(report, sort_keys=True))
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
