"""Lexical utilities for diagnostics and explicit unary vocabulary proposals.

These do not parse formulas or infer argument structure.
"""
import re

BOUNDARIES = frozenset('is does not and or if then that who which both either every some for'.split())
TOKEN = re.compile(r'[A-Za-z][A-Za-z0-9_]*|[^\s]')


def phrase_end(source, start):
    end = start
    for token in TOKEN.finditer(source, start):
        if token.group().lower() in BOUNDARIES or token.group() in {',', '.'}:
            break
        end = token.end()
    return end


def unary_phrase(template):
    match = re.fullmatch(r'\{0\} is (?:a |an )?([A-Za-z][A-Za-z0-9_]*(?: [A-Za-z][A-Za-z0-9_]*)*)', template)
    if not match or len(template) > 80:
        return None
    phrase = match[1]
    # Passive inference is explicitly outside version 1.
    if phrase.lower() in {'a', 'an'} or set(phrase.lower().split()) & (BOUNDARIES | {'by'}):
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
        rows.append({'symbol': name, 'kind': kind, 'wording': wording, 'edit_distance': edit,
                     'shared_stem': stem, 'near_duplicate': edit <= 2 or stem})
    return sorted(rows, key=lambda r: (r['edit_distance'], not r['shared_stem'], r['symbol']))
