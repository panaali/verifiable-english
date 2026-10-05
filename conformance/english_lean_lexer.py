"""Executable reference of the English lexer of the English-in-Lean instance (spec 2.2, tier B draft).

Test code: no admission path calls it. It is the oracle for the Lean `lex` of S2 and the instrument of
S0's character-versus-token probes (plan 7.2, spec O1 to O3). Tokens are the tuples of
`conformance.english_lean_engine`: ('word', text, initial), ('quoted', name), ('label', letter, index),
('numeral', value), ('punct', text, glued_before, glued_after).

Draft choices that the spec leaves to S0, recorded in `docs/spec/english-lean-measured.md`:

- **Whitespace (O3)** is the literal list `WHITESPACE`: exactly the characters for which Python's
  `str.isspace` is true, which is what `_normalise_english_source` collapses today. Lean's
  `Char.isWhitespace` covers only four of them; the Lean lexer must use this list.
- **Offsets** in rejections are UTF-8 byte offsets into the source, as Lean's `String.Pos` is.
- **Quoted identifiers** keep the characters between the quotes exactly, escapes included.
- **List markers** `(a)` `(b)` `(i)` `(ii)` are one token only when written without inner spaces.
- **Initial words**: the first word of a sentence, and the first word after a conclusion marker at the
  start of a sentence (`therefore`, `so`, `hence`, `it follows that`, the first word of the marker
  possibly capitalised, as the `kw` terminal accepts it).
- **Spacing** (DRI ruling 1, finding F1 of `docs/spec/english-lean-s2-integrate.md`): `SPACING` is Lean's
  `spacing` table. No whitespace before the first item or before a terminator, whitespace after a
  terminator unless the text ends, whitespace between two tokens of the word kinds; around punctuation
  the `glued` flags carry the spacing to the rules. A breach is `badSpacing` at the item that starts.
"""
from __future__ import annotations

MAX_SOURCE_BYTES = 64 * 1024
MAX_TEXT_CHARS = 10_000

# Every code point with `str.isspace()` (Python 3.12, Unicode 15); a literal list, as spec O3 asks.
# `test_english_lean_lexer` checks it against `str.isspace` over all of Unicode.
WHITESPACE = frozenset(map(chr, (
    0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x1C, 0x1D, 0x1E, 0x1F, 0x20, 0x85, 0xA0, 0x1680,
    0x2000, 0x2001, 0x2002, 0x2003, 0x2004, 0x2005, 0x2006, 0x2007, 0x2008, 0x2009, 0x200A,
    0x2028, 0x2029, 0x202F, 0x205F, 0x3000)))
PUNCTUATION = frozenset(',;:()[]+-*')
MARKERS = ('(ii)', '(a)', '(b)', '(i)')
CONCLUSION_MARKERS = (('therefore',), ('so',), ('hence',), ('it', 'follows', 'that'))

# Lean's `Item` and `spacing` (`lean/VE/EnglishGrammar/Lexer.lean`): for the item read last and the item that
# starts, whether whitespace must (True), must not (False) or may (None) come between them; the first row
# that matches decides ('*' matches any item).
ITEMS = ('start', 'word', 'punct', 'stop')
SPACING = (('start', '*', False), ('*', 'stop', False), ('stop', '*', True), ('word', 'word', True))


def spacing(last: str, nxt: str) -> bool | None:
    for a, b, required in SPACING:
        if a in ('*', last) and b in ('*', nxt):
            return required
    return None


class LexError(Exception):
    """A lexical rejection: `code` is the `Reject` constructor of spec 5.8, `at` its argument."""

    def __init__(self, code: str, at: int | None = None):
        super().__init__(code if at is None else f'{code} {at}')
        self.code = code
        self.at = at


def collapsed_length(source: str) -> int:
    """The length of the source after every whitespace run outside quotes became one space."""
    n = 0
    quoted = escaped = False
    previous_space = False
    for c in source:
        if not quoted and c in WHITESPACE:
            if not previous_space:
                n += 1
            previous_space = True
            continue
        previous_space = False
        n += 1
        if quoted:
            if escaped:
                escaped = False
            elif c == '\\':
                escaped = True
            elif c == '"':
                quoted = False
        elif c == '"':
            quoted = True
    return n


def _chunk_char(c: str) -> bool:
    return (c.isascii() and (c.isalnum() or c == '_')) or (not c.isascii() and c not in WHITESPACE)


# Python's `int(str)` and `str(int)` refuse numbers of more than `sys.get_int_max_str_digits()` digits
# (4,300 by default, 640 at the least). The lexer bounds a numeral only by the text limit (spec 2.2;
# `NumeralBound` is a later check), so decimal text and values convert in blocks below that limit,
# with the one conversion `ve/ast.py` owns.
from ve.ast import decimal_text, decimal_value  # noqa: E402,F401  (re-exported for the engine)


def _chunk_token(chunk: str, at: int) -> tuple:
    if chunk.isascii() and chunk.isdigit():
        if len(chunk) > 1 and chunk[0] == '0':
            raise LexError('badNumeral', at)
        return ('numeral', decimal_value(chunk))
    if chunk.isascii():
        k = 0
        while k < len(chunk) and 'A' <= chunk[k] <= 'Z':
            k += 1
        digits = chunk[k:]
        if 0 < k < len(chunk) and digits.isdigit() and digits[0] != '0':
            return ('label', chunk[:k], decimal_value(digits))
    return ('word', chunk, False)


def lex_spans(source: str) -> list[list[tuple[tuple, int, int]]]:
    """The sentences of `source` as lists of (token, start byte, end byte), or `LexError`."""
    data = source.encode('utf-8')
    if len(data) > MAX_SOURCE_BYTES:
        raise LexError('sourceTooLong')
    if collapsed_length(source) > MAX_TEXT_CHARS:
        raise LexError('textTooLong')
    # byte offset of each character index
    offsets = [0]
    for c in source:
        offsets.append(offsets[-1] + len(c.encode('utf-8')))
    sentences: list[list] = []
    current: list = []
    i = 0
    n = len(source)
    def punct(text: str, start: int, end: int) -> tuple:
        before = start > 0 and source[start - 1] not in WHITESPACE
        after = end < n and source[end] not in WHITESPACE
        return ('punct', text, before, after)

    last = 'start'

    def begin(item: str, at: int) -> None:
        nonlocal last
        required = spacing(last, item)
        if required is not None and required != (at > 0 and source[at - 1] in WHITESPACE):
            raise LexError('badSpacing', offsets[at])
        last = item

    while i < n:
        c = source[i]
        if c in WHITESPACE:
            i += 1
            continue
        if c == '"':
            begin('word', i)
            j = i + 1
            escaped = False
            while j < n:
                if escaped:
                    escaped = False
                elif source[j] == '\\':
                    escaped = True
                elif source[j] == '"':
                    break
                j += 1
            if j >= n:
                raise LexError('openQuote', offsets[i])
            current.append((('quoted', source[i + 1:j]), offsets[i], offsets[j + 1]))
            i = j + 1
            continue
        if _chunk_char(c):
            begin('word', i)
            j = i
            while j < n and _chunk_char(source[j]):
                j += 1
            current.append((_chunk_token(source[i:j], offsets[i]), offsets[i], offsets[j]))
            i = j
            continue
        if c == '.':
            if not current:
                raise LexError('emptySentence', len(sentences))
            begin('stop', i)
            sentences.append(current)
            current = []
            i += 1
            continue
        marker = next((m for m in MARKERS if source.startswith(m, i)), None)
        if marker:
            begin('punct', i)
            current.append((punct(marker, i, i + len(marker)), offsets[i], offsets[i + len(marker)]))
            i += len(marker)
            continue
        if c in PUNCTUATION:
            begin('punct', i)
            current.append((punct(c, i, i + 1), offsets[i], offsets[i + 1]))
            i += 1
            continue
        if c.isascii():
            raise LexError('badCharacter', offsets[i])
        raise AssertionError('unreachable: a character outside ASCII is a chunk or whitespace')
    if current:
        raise LexError('unterminated')
    if not sentences:
        raise LexError('emptyDocument')
    return [_mark_initials(s) for s in sentences]


def _is_marker(words: list[tuple]) -> bool:
    texts = [t[1] for t in words]
    for marker in CONCLUSION_MARKERS:
        if len(texts) == len(marker) and all(t[0] == 'word' for t in words):
            first_ok = texts[0] == marker[0] or texts[0] == marker[0][0].upper() + marker[0][1:]
            if first_ok and texts[1:] == list(marker[1:]):
                return True
    return False


def _mark_initials(sentence: list) -> list:
    out = []
    for k, (tok, start, end) in enumerate(sentence):
        if tok[0] == 'word' and (k == 0 or _is_marker([t for t, _, _ in sentence[:k]])):
            tok = ('word', tok[1], True)
        out.append((tok, start, end))
    return out


def lex(source: str) -> list[list[tuple]]:
    """`lex` of spec 2.2: the spans erased."""
    return [[tok for tok, _, _ in s] for s in lex_spans(source)]
