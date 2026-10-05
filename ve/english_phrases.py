"""Lexical utilities for diagnostics and explicit unary vocabulary proposals.

These do not parse formulas or infer argument structure.
"""
import re

BOUNDARIES = frozenset('is does not and or if then that who which both either every some for'.split())
BLOCKED = frozenset('than by no never longer neither nor without true false equals equal'.split())
PREPOSITIONS = frozenset('of in on at to from with under over for into upon about against through between among'.split())
CONTENT_STOP = PREPOSITIONS | frozenset('a an the is was are be been being not'.split())
TOKEN = re.compile(r'[A-Za-z][A-Za-z0-9_]*|[^\s]')


def phrase_end(source, start):
    end = start
    for token in TOKEN.finditer(source, start):
        if token.group().lower() in BOUNDARIES or token.group() in {',', '.'}:
            break
        end = token.end()
    return end


def unary_phrase(template):
    match = re.fullmatch(r'\{0\} is (?:a |an )?([A-Za-z][A-Za-z0-9_]*(?:[ -][A-Za-z][A-Za-z0-9_]*)*)', template, re.I)
    if not match or len(template) > 80:
        return None
    phrase = match[1]
    # Passive inference is explicitly outside version 1.
    if phrase.lower() in {'a', 'an'} or set(phrase.lower().split()) & (BOUNDARIES | BLOCKED):
        return None
    return phrase


def distance(left, right):
    row = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        new = [i]
        for j, b in enumerate(right, 1):
            new.append(min(new[-1] + 1, row[j] + 1, row[j - 1] + (a != b)))
        row = new
    return row[-1]


def lexical(text):
    return ' '.join(w for w in re.findall(r'[a-z0-9]+', text.lower())
                    if w not in {'0', '1', 'is', 'not', 'a', 'an'})


# A quoted part runs from `"` to the next `"` not escaped by `\` (the escaped character may be a line
# break); a `"` with no closing quote is an ordinary character. Lean's `wordingKey` reads the same.
_QUOTED = re.compile(r'("(?:[^"\\]|\\.)*")', re.S)


def wording_key(text, fold=str.casefold):
    """Display spelling has no lexical identity; quoted identifiers still do. Outside quoted parts,
    fold and turn each run of whitespace and hyphens into one space; then trim. `re.split` puts the
    quoted parts at odd positions, so text after an unmatched `"` is folded like any other."""
    return ''.join(part if i % 2 else re.sub(r'[\s-]+', ' ', fold(part))
                   for i, part in enumerate(_QUOTED.split(text))).strip()


def content_tokens(text):
    # Deliberately tiny plural normalization; never stem the abbreviation US.
    return {w[:-1] if len(w) > 3 and w.endswith('s') and not w.endswith('ss') else w
            for w in re.findall(r'[a-z0-9]+', text.lower())
            if w not in CONTENT_STOP and w not in {'0', '1'}}


def nearest(phrase, words):
    target = lexical(phrase)
    rows = []
    symbols = [(name, template.removeprefix('{0} '), 'predicate')
               for name, template in words.predicates.items()]
    symbols += [(name, noun, 'sort') for name, noun in words.sorts.items()]
    symbols += [(name, text, 'constant') for name, text in words.constants.items()]
    for name, wording, kind in symbols:
        candidates = (lexical(wording), lexical(name))
        edit = min(distance(target, other) for other in candidates)
        # "Stem" is a shared final content token, without morphology guessing.
        stem = any(target.split()[-1:] == other.split()[-1:] for other in candidates)
        overlap = sorted(set().union(*(content_tokens(phrase) & content_tokens(other)
                                      for other in (wording, name))))
        rows.append({'symbol': name, 'kind': kind, 'wording': wording, 'edit_distance': edit,
                     'shared_stem': stem, 'content_overlap': overlap,
                     'near_duplicate': edit <= 2 or stem or bool(overlap)})
    return sorted(rows, key=lambda r: (r['edit_distance'], not r['shared_stem'], r['symbol']))
