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


@pytest.mark.parametrize('digits', [1, 599, 600, 601, 4300, 4301, 9998])
def test_numerals_and_label_indices_have_no_bound_but_the_text_limit(digits):
    # Review regression: `int(str)` refused more than 4,300 digits; Lean's `Examples.lean` lexes the same.
    value = 10 ** digits - 1
    assert L.lex('9' * digits + '.') == [[('numeral', value)]]
    assert L.lex('S' + '9' * digits + '.') == [[('label', 'S', value)]]
    assert L.decimal_text(value) == '9' * digits
    assert E.show_tree(None, E.Leaf(('numeral', -value))) == '-' + '9' * digits


def test_numeral_text_limit_boundary():
    # 9,999 digits and the terminator are the longest text (L.MAX_TEXT_CHARS); one more digit is too long.
    assert L.lex('9' * 9999 + '.') == [[('numeral', 10 ** 9999 - 1)]]
    for source in ('9' * 10_000 + '.', 'S' + '9' * 9999 + '.'):
        with pytest.raises(L.LexError) as caught:
            L.lex(source)
        assert caught.value.code == 'textTooLong'


def test_decimal_conversion_round_trips_under_the_lowest_digit_limit():
    old = sys.get_int_max_str_digits()
    try:
        sys.set_int_max_str_digits(640)
        for text in ['0', '7', '1' + '0' * 1199, '12345678901234567890' * 300]:
            assert L.decimal_text(L.decimal_value(text)) == text
        assert L.decimal_value('1' + '0' * 1199) == 10 ** 1199
    finally:
        sys.set_int_max_str_digits(old)


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


def test_punctuation_adjacency_is_part_of_exact_matching():
    canonical = L.lex('Legacy is non-compliant.')[0][3]
    assert canonical == ('punct', '-', True, True)
    for source in ('Legacy is non - compliant.', 'Legacy is non -compliant.',
                   'Legacy is non- compliant.'):
        mutant = L.lex(source)[0][3]
        assert mutant != canonical
        assert not E.terminal_accepts(('exact', canonical), mutant)


def test_collapsed_length_matches_python_normalisation():
    from ve.english import _normalise_english_source
    words = type('W', (), {'constants': {}, 'declared_constants': set()})()
    for source in ['a  b\t\tc.', ' x "a   b"  y. ', 'p  q.', '"open  \\"  q"   r.']:
        text, _ = _normalise_english_source(source, words)
        assert L.collapsed_length(source) == len(text)
