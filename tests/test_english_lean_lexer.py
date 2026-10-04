"""The English-in-Lean lexer fixtures (spec 8.4) against the Python reference lexer."""
import json
from pathlib import Path
import sys

import pytest

from conformance import english_lean_engine as E
from conformance import english_lean_lexer as L

CASES = json.loads((Path(__file__).resolve().parents[1] / 'conformance/english-lean/lexer.json').read_text())['cases']


def _source(case):
    if 'source' in case:
        return case['source']
    r = case['source_repeat']
    return r['text'] * r['times'] + r['tail']


@pytest.mark.parametrize('case', CASES, ids=lambda c: c['id'])
def test_lexer_fixture(case):
    source = _source(case)
    if 'reject' in case:
        with pytest.raises(L.LexError) as caught:
            L.lex(source)
        assert caught.value.code == case['reject']
        assert caught.value.at == case.get('at')
    else:
        want = [[E.token_from_json(t) for t in s] for s in case['sentences']]
        assert L.lex(source) == want


def test_whitespace_list_is_pythons_isspace():
    assert L.WHITESPACE == frozenset(chr(c) for c in range(sys.maxunicode + 1) if chr(c).isspace())


def test_no_sentence_contains_the_terminator():
    sentences = L.lex('"x. y" is a. b. c (a) d.')
    assert all(E.TERMINATOR not in s for s in sentences)


def test_spans_are_byte_offsets_and_cover_the_token_text():
    source = 'Café owns "näme".'
    (sentence,) = L.lex_spans(source)
    data = source.encode('utf-8')
    assert [data[a:b].decode() for _, a, b in sentence] == ['Café', 'owns', '"näme"']


def test_collapsed_length_matches_python_normalisation():
    from ve.english import _normalise_english_source
    words = type('W', (), {'constants': {}, 'declared_constants': set()})()
    for source in ['a  b\t\tc.', ' x "a   b"  y. ', 'p  q.', '"open  \\"  q"   r.']:
        text, _ = _normalise_english_source(source, words)
        assert L.collapsed_length(source) == len(text)
