"""The selected lexicon of English in Lean (spec 2.9, 5.8): Python's export and a reference validity check.

    uv run python -m conformance.english_lean_lexicon [--json]

`export(words)` turns Python's `EnglishVocabulary` (the producer, plan 2.4) into the `Lexicon` of spec 5.8,
and `lexicon_id` identifies it under the domain `ve-english-lexicon-v1` (spec 2.12). `check(words, lexicon)`
is a reference of `Lexicon.valid` (V1 to V5), written from spec 2.9: it returns the failing conditions,
each with its symbol. The run over every corpus environment reports where Python's own selection would be
refused by Lean (`invalidGrammar lexicon`). Test and measurement code; no admission path calls it. The
export and its identity are `ve.english_grammar`'s (english-lean-s2.md 6), which the adapter uses.

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
from ve.english_grammar import LEXICON_FORMAT as FORMAT, export, lexicon_id  # noqa: F401  (moved under ve/)
from ve.english_phrases import wording_key
from ve.english_vocabulary import IDIOMS, negative_template
from ve.errors import VEError
from ve.printer import _negative_template
from ve.wire import loads_json

from conformance.english_lean_engine import fold
from conformance.english_lean_lexer import decimal_value

ROOT = Path(__file__).resolve().parents[1]
HOLE = re.compile(r'\{([0-9]+)\}')


# ------------------------------------------------------------------ wordingKey (spec 2.9)

def wording_key_lean(text: str) -> str:
    """`wordingKey` as spec 2.9 states it: Python's `wording_key` (one reading of quoted parts) with
    the fold of 5.8 in place of `casefold`, which is wider outside ASCII (spec 2.3)."""
    return wording_key(text, fold=fold)


# ------------------------------------------------------------------ the honest wordings (spec 2.9)

def _symbols(mapping) -> set[str]:
    return set(mapping) | set(getattr(mapping, 'profile', {}))


def mechanical(name: str, arity: int) -> str | None:
    """`printer.py:190-195`, for a lower-case identifier (spec 2.9); none beyond six arguments, which
    have no ordinal, as in Lean's `mechanicalWording`."""
    if arity == 1:
        return '{0} is ' + name if re.fullmatch('[a-z]+', name) else None
    if arity == 2:
        return '{0} ' + name + ' {1}' if re.fullmatch('[a-z]+', name) else None
    if arity > 6:
        return None
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
    return sorted(decimal_value(h) for h in holes) == list(range(arity)) and bool(words)


def negative_template_of(wording: str | None, arity: int) -> str | None:
    """`negativeTemplate` of spec 2.9 on a selected wording, total as Lean's is. Where Python's
    `negative_template` is defined it is its value; where it fails, Lean's value is none: no selected
    wording (Lean reads it as the empty text), a wording of fewer than two words (Python indexes the
    second word), and an arity without an idiom table (Python indexes `IDIOMS[arity]`; Lean's is empty)."""
    if wording is None or len(wording.split()) < 2:
        return None
    if arity not in IDIOMS and not wording.startswith(('{0} is ', '{0} was ', '{0} has ')):
        return _negative_template(wording, 2) if wording in IDIOMS[1] else None
    return negative_template(wording, arity)


# ------------------------------------------------------------------ the lexical view and validity

def lexical_view(words: EnglishVocabulary) -> dict:
    """The `Env` of spec 5.8 that `Lexicon.valid` reads: every sort, predicate and constant, the symbols
    that profile blocks generate included, with their declared forms, and the forms profile blocks fix.
    The overlay is already applied (the display environment), so the Lean `Overlay` is empty. Lists are
    sorted by name; `lean_fixtures` writes the same view as Lean data."""
    env = words.env
    sorts, predicates, constants = _symbols(env.sorts), _symbols(env.predicates), _symbols(env.constants)
    if getattr(env, 'alternatives', None) is not None:
        predicates |= {'avoidable', 'unavoidable', 'allows', 'prevents'}
    if getattr(env, 'risk', None) is not None:
        constants |= set(loads_json(env.risk)['severity']['classes'])

    def declared(p):
        return env.predicates[p] if p in _symbols(env.predicates) else None

    def noun(s):
        decl = env.sorts[s] if s in _symbols(env.sorts) else None
        return decl.verbalisation.singular if decl is not None and decl.verbalisation else None

    return {
        'sorts': [{'name': s, 'noun': noun(s)} for s in sorted(sorts)],
        'predicates': [{'name': p, 'arity': len(declared(p).arguments) if declared(p) else 2,
                        'wording': declared(p).verbalisation if declared(p) else None,
                        'negative': declared(p).negative_verbalisation if declared(p) else None}
                       for p in sorted(predicates)],
        'constants': [{'name': c, 'display': words.declared_constants.get(c)} for c in sorted(constants)],
        'forms': profile_tables(env),
    }


LEXICON_FIELDS = {'nouns': 2, 'letters': 2, 'wordings': 2, 'negatives': 2, 'aliases': 3, 'spellings': 2}


def _entries(lexicon: dict, field: str) -> list[tuple]:
    """The entries of one field as tuples, in order and with repetitions: Lean's `Lexicon` holds lists,
    so a repeated symbol must reach the coverage check (V1). Anything that is not a Lean `Lexicon` is
    refused."""
    entries = lexicon.get(field) if isinstance(lexicon, dict) else None
    width = LEXICON_FIELDS[field]
    if type(entries) is not list:
        raise VEError(f'lexicon field {field} is not a list')
    out = []
    for e in entries:
        if (type(e) is not list or len(e) != width or not all(type(x) is str for x in e[:2])
                or (width == 3 and type(e[2]) is not bool)):
            raise VEError(f'lexicon field {field} has an entry that is not a {width}-element entry')
        out.append(tuple(e))
    return out


def _lookup(entries, key):
    """Lean's `List.lookup`: the value of the first entry for `key`."""
    return next((e[1] for e in entries if e[0] == key), None)


def failures(view: dict, lexicon: dict) -> list[tuple[str, str, str]]:
    """`Lexicon.failures` of `lean/VE/EnglishGrammar/Lexicon.lean` over a lexical view, condition by
    condition: (condition, symbol kind, symbol name), sorted and without repetition. Empty means valid."""
    L = {field: _entries(lexicon, field) for field in LEXICON_FIELDS}
    sorts = [s['name'] for s in view['sorts']]
    preds = [p['name'] for p in view['predicates']]
    consts = [c['name'] for c in view['constants']]
    pred = {p['name']: p for p in view['predicates']}
    noun = {s['name']: s['noun'] for s in view['sorts']}
    display = {c['name']: c['display'] for c in view['constants']}
    F = view['forms']

    def keys(field):
        return [e[0] for e in L[field]]

    def arity(p):
        return pred[p]['arity'] if p in pred else 0

    def coverage(kind, got, need):
        return ([('V1', kind, s) for s in need if got.count(s) != 1] +
                [('V1', kind, s) for s in got if s not in need])

    # V1 coverage: exactly one entry per symbol
    out = (coverage('sort', keys('nouns'), sorts) + coverage('letter', keys('letters'), sorts) +
           coverage('predicate', keys('wordings'), preds) + coverage('constant', keys('spellings'), consts))
    negs = keys('negatives')
    out += [('V1', 'negative', p) for p in negs if p not in preds or negs.count(p) != 1]
    out += [('V1', 'alias', p) for p in keys('aliases') if p not in preds]

    # V2 honesty, V3 shape, V5 polarity
    for p, w in L['wordings']:
        if p in preds:
            k = arity(p)
            if w not in {pred[p]['wording'], F['wordings'].get(p), mechanical(p, k), fallback(p, k)} - {None}:
                out.append(('V2', 'predicate', p))
            if not _shape_ok(w, k):
                out.append(('V3', 'predicate', p))
    for p, w in L['negatives']:
        if p in preds:
            k, fixed = arity(p), F['negatives'].get(p)
            if w not in {pred[p]['negative'], fixed} - {None}:
                out.append(('V2', 'negative', p))
            if not _shape_ok(w, k):
                out.append(('V3', 'negative', p))
            if fixed != w and negative_template_of(_lookup(L['wordings'], p), k) != w:
                out.append(('V5', 'negative', p))
    for p in sorted(set(keys('aliases')) | set(F['aliases'])):
        selected = [(w, neg) for q, w, neg in L['aliases'] if q == p]
        if sorted(selected) != sorted(map(tuple, F['aliases'].get(p, []))):
            out.append(('V2', 'alias', p))
        if not all(_shape_ok(w, arity(p)) for w, _ in selected):
            out.append(('V3', 'alias', p))
    for s, n in L['nouns']:
        if s in sorts:
            if n not in {noun[s], F['nouns'].get(s), s, 'entity of sort ' + quote(s)} - {None}:
                out.append(('V2', 'sort', s))
            if HOLE.search(n):
                out.append(('V3', 'sort', s))
    for c, sp in L['spellings']:
        if c in consts:
            if sp not in {display[c], c, quote(c)} - {None}:
                out.append(('V2', 'constant', c))
            if HOLE.search(sp):
                out.append(('V3', 'constant', c))

    # V4 distinctness: a selection against what every other symbol declares or selects, by Lean's key
    owners: dict[str, set[tuple[str, str]]] = {}

    def own(text, kind, name):
        if text:
            owners.setdefault(wording_key_lean(text), set()).add((kind, name))

    for p in preds:
        own(pred[p]['wording'], 'predicate', p)
        own(pred[p]['negative'], 'predicate', p)
        own(F['wordings'].get(p), 'predicate', p)
        for w, _ in F['aliases'].get(p, []):
            own(w, 'predicate', p)
    for s in sorts:
        own(noun[s], 'sort', s)
        own(_lookup(L['nouns'], s), 'sort', s)
    for c in consts:
        own(display[c], 'constant', c)
        own(_lookup(L['spellings'], c), 'constant', c)
    selections = ([(w, 'predicate', p) for p, w in L['wordings'] + L['negatives']] +
                  [(w, 'predicate', p) for p, w, _ in L['aliases']] +
                  [(n, 'sort', s) for s, n in L['nouns']] + [(sp, 'constant', c) for c, sp in L['spellings']])
    for text, kind, name in selections:
        if owners.get(wording_key_lean(text), set()) - {(kind, name)}:
            out.append(('V4', kind, name))
    return sorted(set(out))


def check(words: EnglishVocabulary, lexicon: dict) -> list[tuple[str, str, str]]:
    """The failures of `Lexicon.valid` for the lexicon of `words`' environment. Empty means valid."""
    return failures(lexical_view(words), lexicon)


# ------------------------------------------------------------------ the shared fixtures and their Lean copy

FIXTURES = ROOT / 'conformance/english-lean/lexicon.json'
LEAN_FIXTURES = ROOT / 'lean/VE/EnglishGrammar/LexiconFixtures.lean'


def fixture_environment(corpus: dict, name: str) -> Environment:
    spec = corpus['environments'][name]
    data = json.loads((ROOT / spec['path']).read_text())
    data['vocabulary']['predicates'].update(spec.get('add_predicates', {}))
    return Environment(data)


def fixture_vocabulary(corpus: dict, name: str) -> EnglishVocabulary:
    """The vocabulary of a corpus environment, with its English overlay (`overlay`: sorts, predicates
    and constants of a `ve.english-vocabulary@1` file) when it has one."""
    env = fixture_environment(corpus, name)
    overlay = corpus['environments'][name].get('overlay')
    if overlay is None:
        return EnglishVocabulary(env)
    return EnglishVocabulary(env, vocabulary={'format': 've.english-vocabulary@1',
                                              'environment_id': env.environment_id,
                                              'sorts': {}, 'predicates': {}, 'constants': {}, **overlay})


def apply_edits(lexicon: dict, edits: list) -> dict:
    """The edits of `lexicon.json` on the lists of a lexicon: `set` replaces every entry of a symbol by
    one, `add` appends an entry (a repeated symbol stays repeated), `remove` drops every entry of a
    symbol; the field is then sorted. `append` adds an entry at the end without sorting."""
    lex = json.loads(json.dumps(lexicon))
    for edit in edits:
        (op, args), = edit.items()
        field, symbol, rest = args[0], args[1], list(args[2:])
        entries = lex[field]
        if op in ('set', 'remove'):
            entries = [e for e in entries if e[0] != symbol]
        if op in ('set', 'add', 'append'):
            entries = entries + [[symbol, *rest]]
        if op not in ('set', 'add', 'append', 'remove'):
            raise ValueError(f'unknown edit {op}')
        lex[field] = entries if op == 'append' else sorted(entries)
    return lex


def fixture_lexicon(corpus: dict, case: dict, env: Environment) -> dict:
    return {'format': FORMAT, 'environment_id': env.environment_id,
            **apply_edits(corpus['LF'], case['edits'])}


def mutants(view: dict, lexicon: dict) -> list[tuple[str, dict]]:
    """One- and two-fault mutants of a valid lexicon: each entry repeated (with its own and with another
    honest value), dropped, emptied, cut to one word, given an extra hole, given the next entry's text,
    and respaced with a no-break space and upper case; an entry for an unknown symbol in each field; aliases with and without the
    right shape. Two-fault mutants pair single faults of different fields (a fixed sample)."""
    import random
    arity = {p['name']: p['arity'] for p in view['predicates']}

    def other(field, key):
        return {'nouns': 'entity of sort ' + quote(key), 'letters': 'Q',
                'wordings': fallback(key, arity.get(key, 2)) or key, 'negatives': '{0} is not ' + key,
                'spellings': quote(key)}[field]

    singles: list[tuple[str, str, list]] = []
    for field in ('nouns', 'letters', 'wordings', 'negatives', 'spellings'):
        for i, (key, value) in enumerate(lexicon[field]):
            for op, edit in (('dup', lambda es: es[:i + 1] + [es[i]] + es[i + 1:]),
                             ('dup-other', lambda es: es[:i + 1] + [[key, other(field, key)]] + es[i + 1:]),
                             ('drop', lambda es: es[:i] + es[i + 1:]),
                             ('empty', lambda es: es[:i] + [[key, '']] + es[i + 1:]),
                             ('one-word', lambda es: es[:i] + [[key, '{0}' if '{' in value else 'x']] + es[i + 1:]),
                             ('hole', lambda es: es[:i] + [[key, value + ' {9}']] + es[i + 1:]),
                             ('steal', lambda es: es[:i] + [[key, es[(i + 1) % len(es)][1]]] + es[i + 1:]),
                             ('respace', lambda es: es[:i] + [[key, value.replace(' ', '  ', 1).upper()]]
                                                    + es[i + 1:])):
                singles.append((f'{field}[{i}] {op}', field, edit(lexicon[field])))
        singles.append((f'{field} unknown', field, lexicon[field] + [['zzz', 'zzz']]))
    first = view['predicates'][0]['name']
    for label, entry in (('alias', [first, '{0} is liked', False]), ('alias-shape', [first, 'x', True]),
                         ('alias unknown', ['zzz', '{0} zzz {1}', False])):
        singles.append((label, 'aliases', lexicon['aliases'] + [entry]))

    def mutate(changes):
        lex = json.loads(json.dumps(lexicon))
        for _, field, entries in changes:
            lex[field] = entries
        return lex

    out = [(label, mutate([s])) for s in singles for label in [s[0]]]
    pairs = [(a, b) for a in singles for b in singles if a[1] < b[1]]
    for a, b in random.Random(0).sample(pairs, 40):
        out.append((a[0] + ' + ' + b[0], mutate([a, b])))
    return out


def lean_string(s: str) -> str:
    out = []
    for c in s:
        if c in '"\\':
            out.append('\\' + c)
        elif c == '\n':
            out.append('\\n')
        elif ' ' <= c <= '~':
            out.append(c)
        elif ord(c) <= 0xFFFF:
            out.append(f'\\u{ord(c):04X}')
        else:
            raise ValueError('a fixture text outside the basic plane')
    return '"' + ''.join(out) + '"'


def _option(s: str | None) -> str:
    return 'none' if s is None else 'some ' + lean_string(s)


def _pairs(entries) -> str:
    def entry(e):
        return '(' + ', '.join('true' if x is True else 'false' if x is False else lean_string(x) for x in e) + ')'
    return '[' + ', '.join(entry(e) for e in entries) + ']'


def lean_env(view: dict) -> str:
    F = view['forms']
    sorts = ', '.join(f'{{ name := {lean_string(s["name"])}, noun := {_option(s["noun"])} }}' for s in view['sorts'])
    preds = ',\n      '.join(f'{{ name := {lean_string(p["name"])}, arity := {p["arity"]}, '
                             f'wording := {_option(p["wording"])}, negative := {_option(p["negative"])} }}'
                             for p in view['predicates'])
    consts = ', '.join(f'{{ name := {lean_string(c["name"])}, display := {_option(c["display"])} }}'
                       for c in view['constants'])
    forms = (f'{{ wordings := {_pairs(sorted(F["wordings"].items()))}, '
             f'negatives := {_pairs(sorted(F["negatives"].items()))}, '
             f'aliases := {_pairs([p, w, n] for p, ws in sorted(F["aliases"].items()) for w, n in ws)}, '
             f'nouns := {_pairs(sorted(F["nouns"].items()))} }}')
    return (f'{{ sorts := [{sorts}],\n    predicates := [{preds}],\n    constants := [{consts}],\n'
            f'    forms := {forms} }}')


def lean_lexicon(lex: dict) -> str:
    return '{ ' + ',\n  '.join(f'{field} := {_pairs(lex[field])}' for field in LEXICON_FIELDS) + ' }'


def lean_fixtures() -> str:
    """`LexiconFixtures.lean`: every case of `lexicon.json` and the mutants of its valid lexicon, each with
    the failures the Python reference finds; `lake build` checks that Lean's `Lexicon.failures` finds
    the same (condition, kind, name) triples."""
    corpus = json.loads(FIXTURES.read_text())
    lines = ['import VE.EnglishGrammar.Lexicon', '',
             '/-! Generated by `python -m conformance.english_lean_lexicon --lean-fixtures` from',
             '`conformance/english-lean/lexicon.json`; do not edit. Each `#guard` states the failures that the',
             'Python reference of `Lexicon.valid` (`conformance/english_lean_lexicon.py`) finds for one lexicon:',
             'the cases of spec 8.5 and the review regressions, then one- and two-fault mutants of the valid',
             'lexicon `LF`. `tests/test_english_lean_lexicon.py` checks that this file is up to date. -/', '',
             'namespace VE.EnglishGrammar.LexiconFixtures', 'open VE.EnglishGrammar', '',
             '/-- The failures as `condition kind name` texts, sorted and without repetition. -/',
             'def failureSet (E : Env) (L : Lexicon) : List String :=',
             '  ((L.failures E {}).map (fun (c, k, n) => c ++ " " ++ k ++ " " ++ n)).eraseDups.mergeSort',
             '    (fun a b => !(b < a))', '']
    views = {}
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UnreviewedVocabularyWarning)
        for name in corpus['environments']:
            words = fixture_vocabulary(corpus, name)
            views[name] = (words.env, lexical_view(words))
            lines += [f'def env{name} : Env :=', '  ' + lean_env(views[name][1]), '']

    def guard(label, env_name, lex):
        found = [' '.join(f) for f in failures(views[env_name][1], lex)]
        lines.extend([f'-- {label}', f'#guard failureSet env{env_name}',
                      '  ' + lean_lexicon(lex).replace('\n', '\n  ') + ' ==',
                      '  [' + ', '.join(lean_string(f) for f in found) + ']'])

    for case in corpus['cases']:
        env, _ = views[case['env']]
        guard(case['id'], case['env'], fixture_lexicon(corpus, case, env))
    lf = {field: corpus['LF'][field] for field in LEXICON_FIELDS}
    for label, lex in mutants(views['F'][1], lf):
        guard('mutant ' + label, 'F', lex)
    texts = wording_key_texts()
    lines += ['', '-- wordingKey: every text of at most three characters over the alphabet of',
              '-- `wording_key_texts`, then the longer ones; the keys are `wording_key_lean`.']
    for k in range(0, len(texts), 100):
        chunk = texts[k:k + 100]
        lines += ['#guard [' + ', '.join(lean_string(t) for t in chunk) + '].map wordingKey ==',
                  '  [' + ', '.join(lean_string(wording_key_lean(t)) for t in chunk) + ']']
    lines += ['', 'end VE.EnglishGrammar.LexiconFixtures', '']
    return '\n'.join(lines)


# Quotes, escapes, line breaks, separators and case, with three characters the Lean fold or space set
# names (no-break space, dotted capital I, Kelvin sign) and one it leaves alone (sharp s).
KEY_ALPHABET = ('a', 'A', '"', '\\', ' ', '-', '\n', ' ', 'İ', 'K', 'ß')


def wording_key_texts() -> list[str]:
    """The texts of the `wordingKey` differential: all of at most three characters over
    `KEY_ALPHABET`, then longer texts with quoted parts, unmatched quotes and escaped line breaks."""
    from itertools import product
    texts = [''.join(p) for n in range(1, 4) for p in product(KEY_ALPHABET, repeat=n)]
    texts += ['"ALICE', '"alice', '{0} is "Odd', 'x "A" "B', '"a\\\nB"', '"a\\\nB', 'a "b\\" C',
              '"A\\\\" B', '  {0} --  is Reviewed  ', '"x" Y "z', '\\"A"B"', '""A""']
    return texts


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
    parser.add_argument('--lean-fixtures', action='store_true', help=f'write {LEAN_FIXTURES.relative_to(ROOT)}')
    args = parser.parse_args(argv)
    if args.lean_fixtures:
        LEAN_FIXTURES.write_text(lean_fixtures())
        print(LEAN_FIXTURES)
        return 0
    report = corpus_report()
    args.output.write_text(json.dumps(report, indent=1, sort_keys=True, ensure_ascii=False) + '\n')
    print(json.dumps({k: report[k] for k in ('valid', 'invalid', 'failures_by_condition')}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
