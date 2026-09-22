"""Advisory lexical evidence for proposals only; never used by the parser."""
from functools import lru_cache
from importlib.resources import files
import json
import re

VERSION = 'oewn-2025'
TOKEN = re.compile(r'[A-Za-z][A-Za-z0-9_]*')


@lru_cache(maxsize=1)
def _index():
    data = json.loads(files(__package__).joinpath(VERSION + '.json').read_text(encoding='utf-8'))
    index = {}
    known = set()
    for lemma, cls, suffixes, forms in data['entries']:
        keys = tuple(lemma + '%' + suffix for suffix in suffixes)
        known.add(lemma)
        if cls in {'noun', 'adjective'}:
            index.setdefault(lemma, set()).add((cls, lemma, keys))
        if cls == 'verb':
            for form in forms['third_person'] + forms['past_participle'] + forms['exceptions']:
                known.add(form)
            for form in forms['past_participle']:
                index.setdefault(form, set()).add(('participle', lemma, keys))
    return {word: tuple(sorted(rows)) for word, rows in index.items()}, frozenset(known)


def classify(phrase, declared=()):
    """Preserve token order and every compatible analysis, without selecting senses.

    A bare verb/third-person form has no unary class, so is labelled unknown
    here, but is still known to the lexicon and cannot trigger the all-unknown
    warning. Morphology and dictionary membership never gate a proposal.
    """
    index, known = _index()
    declared = {word.casefold() for word in declared}
    rows = []
    for token in TOKEN.findall(phrase):
        word = token.casefold()
        analyses = [{'class': cls, 'lemma': lemma, 'sense_keys': list(keys)}
                    for cls, lemma, keys in index.get(word, ())]
        rows.append({'token': token, 'classes': sorted({a['class'] for a in analyses}) or ['unknown'],
                     'analyses': analyses, 'known_to_lexicon': word in known,
                     'declared': word in declared})
    return {'version': VERSION, 'tokens': rows,
            'unknown_tokens': [r['token'] for r in rows if r['classes'] == ['unknown']],
            'all_unknown_undeclared': bool(rows) and all(not r['known_to_lexicon'] and not r['declared'] for r in rows)}


def describe(evidence):
    tokens = []
    for row in evidence['tokens']:
        labels = [f"{a['class']}({key})" for a in row['analyses'] for key in a['sense_keys']]
        tokens.append(row['token'].casefold() + '/' + '|'.join(labels or ['unknown(no sense key)']))
    return f"machine-proposed; lexicon {evidence['version']}; tokens: " + ', '.join(tokens)
