"""The selected lexicon of English in Lean (spec 2.9, 5.8): Python's export and a reference validity check.

    uv run python -m conformance.english_lean_lexicon [--json]

`export(words)` turns Python's `EnglishVocabulary` (the producer, plan 2.4) into the `Lexicon` of spec 5.8,
and `lexicon_id` identifies it under the domain `ve-english-lexicon-v1` (spec 2.12). `check(words, lexicon)`
is a reference of `Lexicon.valid` (V1 to V5), written from spec 2.9: it returns the failing conditions,
each with its symbol. The run over every corpus environment reports where Python's own selection would be
refused by Lean (`invalidGrammar lexicon`). Test and measurement code; no admission path calls it.

The reference reads the honest wordings from the display environment that `EnglishVocabulary` holds (the
environment with the overlay applied), and the profile-fixed forms from the tables below, which copy
`ve/english.py` (alternatives@0, risk@0, rights@0, norms@0). The Lean port reads the same tables as data
of the fixed rules (spec 2.9 notes, O7).
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import warnings

from ve import Environment
from ve.english import EnglishVocabulary, UnreviewedVocabularyWarning, quote
from ve.english_phrases import wording_key
from ve.english_vocabulary import negative_template
from ve.wire import digest, loads_json

from conformance.english_lean_engine import fold

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = 've-english-lexicon-v1\n'
FORMAT = 've.english-lexicon@1'
HOLE = re.compile(r'\{([0-9]+)\}')


# ------------------------------------------------------------------ export and identity

def export(words: EnglishVocabulary) -> dict:
    """The lexicon Python selects, in the field order of spec 5.8; every list sorted by symbol."""
    return {
        'format': FORMAT,
        'environment_id': words.env.environment_id,
        'nouns': sorted([s, n] for s, n in words.sorts.items()),
        'letters': sorted([s, l] for s, l in words.letters.items()),
        'wordings': sorted([p, w] for p, w in words.predicates.items()),
        'negatives': sorted([p, w] for p, w in words.negatives.items()),
        'aliases': sorted([p, w, bool(neg)] for p, w, neg in words.input_aliases),
        'spellings': sorted([c, s] for c, s in words.constants.items()),
    }


def lexicon_id(lexicon: dict) -> str:
    return digest(DOMAIN, lexicon)


# ------------------------------------------------------------------ wordingKey (spec 2.9)

def wording_key_lean(text: str) -> str:
    """`wordingKey` as spec 2.9 states it, with the fold of 5.8: outside quoted parts, fold and turn
    each run of whitespace and hyphens into one space; trim."""
    parts = re.split(r'("(?:[^"\\]|\\.)*")', text)
    return ''.join(p if p.startswith('"') else re.sub(r'[\s-]+', ' ', fold(p)) for p in parts).strip()


# ------------------------------------------------------------------ the honest wordings (spec 2.9)

def _symbols(mapping) -> set[str]:
    return set(mapping) | set(getattr(mapping, 'profile', {}))


def mechanical(name: str, arity: int) -> str | None:
    """`printer.py:190-195`, for a lower-case identifier (spec 2.9)."""
    if arity == 1:
        return '{0} is ' + name if re.fullmatch('[a-z]+', name) else None
    if arity == 2:
        return '{0} ' + name + ' {1}' if re.fullmatch('[a-z]+', name) else None
    return ('{0} has recorded relation ' + name + ' with ' +
            ' and '.join('argument ' + ('two', 'three', 'four', 'five', 'six')[i - 1] + ' {' + str(i) + '}'
                         for i in range(1, arity)))


def fallback(name: str, arity: int) -> str | None:
    if arity == 1:
        return '{0} is classified as ' + quote(name)
    if arity == 2:
        return '{0} has the recorded relation ' + quote(name) + ' to {1}'
    return None


def profile_tables(env) -> dict:
    """The forms a profile block fixes: wordings, negatives, aliases, nouns (copied from ve/english.py)."""
    wordings: dict[str, str] = {}
    negatives: dict[str, str] = {}
    aliases: dict[str, list] = {}
    nouns: dict[str, str] = {}
    if getattr(env, 'alternatives', None) is not None:
        block = loads_json(env.alternatives)
        for role in ('available', 'leads_to', 'inaction', 'taken', 'proximate'):
            if role in block:
                wordings[block[role]] = env.predicates[block[role]].verbalisation
        risk = getattr(env, 'risk', None)
        wordings.update({'avoidable': '{0} is avoidable by {1}', 'unavoidable': '{0} is unavoidable by {1}',
                         'allows': '{0} allows {1} to happen',
                         'prevents': '{0} might prevent {1}' if risk is not None else '{0} prevents {1}'})
        aliases['avoidable'] = [['{0} is preventable by {1}', False]]
        aliases['allows'] = [['{0} lets {1} happen', False]]
        if risk is None:
            aliases.setdefault(block['leads_to'], []).append(['{0} does not lead to {1}', True])
        else:
            rblock = loads_json(risk)
            nouns[rblock['severity']['sort']] = 'severity'
            wordings.update({'risk__might_lead_to': '{0} might lead to {1}', 'risk__class': '{0} is {1}',
                             'risk__or_worse': '{0} is {1} or worse',
                             'risk__less_worst': '{0} has a less severe worst case than {1}'})
            negatives[block['leads_to']] = '{0} might not lead to {1}'
            negatives['risk__might_lead_to'] = '{0} cannot lead to {1}'
    for name, template in (getattr(env, 'rights_wordings', None) or {}).items():
        wordings[name] = template
    if 'norms@0' in env.profiles:
        for name, decl in env.predicates.items():
            reg = decl.regulated
            if reg is not None and reg.role in ('permission', 'obligation'):
                modal = 'may' if reg.role == 'permission' else 'must'
                wordings[name] = reg.act.replace('{0} ', '{0} ' + modal + ' ', 1)
    return {'wordings': wordings, 'negatives': negatives, 'aliases': aliases, 'nouns': nouns}


def _shape_ok(wording: str, arity: int) -> bool:
    holes = HOLE.findall(wording)
    words = [w for w in HOLE.sub(' ', wording).split() if w]
    return sorted(int(h) for h in holes) == list(range(arity)) and bool(words)


def check(words: EnglishVocabulary, lexicon: dict) -> list[tuple[str, str, str]]:
    """The failures of `Lexicon.valid`: (condition, symbol kind, symbol name). Empty means valid."""
    env = words.env
    prof = profile_tables(env)
    failures: list[tuple[str, str, str]] = []
    nouns = dict(map(tuple, lexicon['nouns']))
    letters = dict(map(tuple, lexicon['letters']))
    wordings = dict(map(tuple, lexicon['wordings']))
    negatives = dict(map(tuple, lexicon['negatives']))
    spellings = dict(map(tuple, lexicon['spellings']))
    aliases: dict[str, list] = {}
    for p, w, neg in lexicon['aliases']:
        aliases.setdefault(p, []).append([w, neg])
    sorts, predicates, constants = _symbols(env.sorts), _symbols(env.predicates), _symbols(env.constants)
    if getattr(env, 'alternatives', None) is not None:
        predicates |= {'avoidable', 'unavoidable', 'allows', 'prevents'}
    if getattr(env, 'risk', None) is not None:
        constants |= set(loads_json(env.risk)['severity']['classes'])

    # V1 coverage
    for kind, have, want in (('sort', set(nouns), sorts), ('letter', set(letters), sorts),
                             ('predicate', set(wordings), predicates), ('constant', set(spellings), constants)):
        failures += [('V1', kind, n) for n in sorted(want - have)] + [('V1', kind, n) for n in sorted(have - want)]
    failures += [('V1', 'negative', p) for p in sorted(set(negatives) - predicates)]
    failures += [('V1', 'alias', p) for p in sorted(set(aliases) - predicates)]

    def arity(p):
        return len(env.predicates[p].arguments) if p in _symbols(env.predicates) else 2

    def declared_wording(p):
        return env.predicates[p].verbalisation if p in _symbols(env.predicates) else None

    def declared_negative(p):
        return env.predicates[p].negative_verbalisation if p in _symbols(env.predicates) else None

    def declared_noun(s):
        decl = env.sorts[s] if s in _symbols(env.sorts) else None
        return decl.verbalisation.singular if decl is not None and decl.verbalisation else None

    # V2 honesty and V3 shape
    for p, w in sorted(wordings.items()):
        if p not in predicates:
            continue
        k = arity(p)
        honest = {declared_wording(p), prof['wordings'].get(p), mechanical(p, k), fallback(p, k)} - {None}
        if w not in honest:
            failures.append(('V2', 'predicate', p))
        if not _shape_ok(w, k):
            failures.append(('V3', 'predicate', p))
    for p, w in sorted(negatives.items()):
        if p not in predicates:
            continue
        if w not in {declared_negative(p), prof['negatives'].get(p)} - {None}:
            failures.append(('V2', 'negative', p))
        if not _shape_ok(w, arity(p)):
            failures.append(('V3', 'negative', p))
        # V5 polarity
        if prof['negatives'].get(p) != w and w != negative_template(wordings.get(p, ''), arity(p)):
            failures.append(('V5', 'negative', p))
    for p in sorted(set(aliases) | set(prof['aliases'])):
        if sorted(map(tuple, aliases.get(p, []))) != sorted(map(tuple, prof['aliases'].get(p, []))):
            failures.append(('V2', 'alias', p))
        for w, _ in aliases.get(p, []):
            if not _shape_ok(w, arity(p)):
                failures.append(('V3', 'alias', p))
    for s, n in sorted(nouns.items()):
        if s not in sorts:
            continue
        if n not in {declared_noun(s), prof['nouns'].get(s), s, 'entity of sort ' + quote(s)} - {None}:
            failures.append(('V2', 'sort', s))
        if HOLE.search(n):
            failures.append(('V3', 'sort', s))
    for c, sp in sorted(spellings.items()):
        if c not in constants:
            continue
        if sp not in {words.declared_constants.get(c), c, quote(c)} - {None}:
            failures.append(('V2', 'constant', c))
        if HOLE.search(sp):
            failures.append(('V3', 'constant', c))

    # V4 distinctness: a selection against what every other symbol declares or selects
    owners: dict[str, set[tuple[str, str]]] = {}

    def own(key_text, kind, name):
        if key_text:
            owners.setdefault(wording_key(key_text), set()).add((kind, name))

    for p in predicates:
        own(declared_wording(p), 'predicate', p)
        own(declared_negative(p), 'predicate', p)
        own(prof['wordings'].get(p), 'predicate', p)
        for w, _ in prof['aliases'].get(p, []):
            own(w, 'predicate', p)
    for s in sorts:
        own(declared_noun(s), 'sort', s)
        own(nouns.get(s), 'sort', s)
    for c in constants:
        own(words.declared_constants.get(c), 'constant', c)
        own(spellings.get(c), 'constant', c)
    selections = ([(w, 'predicate', p) for p, w in wordings.items()] +
                  [(w, 'predicate', p) for p, w in negatives.items()] +
                  [(w, 'predicate', p) for p, ws in aliases.items() for w, _ in ws] +
                  [(n, 'sort', s) for s, n in nouns.items()] +
                  [(sp, 'constant', c) for c, sp in spellings.items()])
    for text, kind, name in sorted(selections):
        others = owners.get(wording_key(text), set()) - {(kind, name)}
        if others:
            failures.append(('V4', kind, name))
    return sorted(set(failures))


# ------------------------------------------------------------------ the corpus run

def environments():
    """The 17 round-trip configurations, then every use-case environment that loads, with its overlay."""
    from conformance.english_surface import configurations
    yield from configurations()
    for path in sorted(ROOT.glob('usecases/*/environment*.json')):
        if path.name.endswith('.english.json'):
            continue
        try:
            env = Environment.from_json(path.read_bytes())
        except Exception:   # not an environment file of this form
            continue
        yield str(path.relative_to(ROOT)), env, {}
        overlay = path.with_name(path.stem + '.english.json')
        if overlay.exists():
            yield str(path.relative_to(ROOT)) + '+overlay', env, {'vocabulary': json.loads(overlay.read_text())}


def corpus_report() -> dict:
    rows = []
    key_differences = []
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UnreviewedVocabularyWarning)
        for name, env, options in environments():
            try:
                words = EnglishVocabulary(env, **options)
            except Exception as e:      # an overlay this build refuses
                rows.append({'environment': name, 'error': f'{type(e).__name__}: {e}'})
                continue
            lex = export(words)
            failures = check(words, lex)
            for _, w in lex['wordings'] + lex['negatives'] + lex['nouns'] + lex['spellings']:
                if wording_key(w) != wording_key_lean(w):
                    key_differences.append({'environment': name, 'text': w})
            rows.append({'environment': name, 'lexicon_id': lexicon_id(lex),
                         'symbols': len(lex['nouns']) + len(lex['wordings']) + len(lex['spellings']),
                         'failures': [list(f) for f in failures]})
    by_condition = Counter(f[0] for r in rows for f in r.get('failures', []))
    return {'format': 've.english-lean-lexicon-report@1', 'environments': rows,
            'failures_by_condition': dict(sorted(by_condition.items())),
            'valid': sum(1 for r in rows if not r.get('failures') and 'error' not in r),
            'invalid': sum(1 for r in rows if r.get('failures')),
            'wording_key_differences': key_differences}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--output', type=Path, default=ROOT / 'conformance/english-lean/lexicon-report.json')
    args = parser.parse_args(argv)
    report = corpus_report()
    args.output.write_text(json.dumps(report, indent=1, sort_keys=True, ensure_ascii=False) + '\n')
    print(json.dumps({k: report[k] for k in ('valid', 'invalid', 'failures_by_condition')}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
