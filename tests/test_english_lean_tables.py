"""The tables that the Lean English instance copies from Python stay equal to Python's.

`lean/VE/EnglishGrammar/Lexicon.lean` ports `negative_template` with its idiom and irregular-verb tables
(docs/spec/english-lean.md 2.9), and `lean/VE/EnglishGrammar/Lexer.lean` uses the whitespace list of
Python's `str.isspace` (spec O3). A change on either side without the other fails here.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

from ve.english_vocabulary import IDIOMS
from ve.printer import _IRREGULAR_VERBS

ROOT = Path(__file__).resolve().parents[1]
LEXICON = ROOT / 'lean/VE/EnglishGrammar/Lexicon.lean'
LEXER = ROOT / 'lean/VE/EnglishGrammar/Lexer.lean'


def _definition(path: Path, name: str) -> str:
    """The source text of a Lean `def` up to the next blank line."""
    text = path.read_text()
    start = text.index(f'def {name} ')
    end = text.find('\n\n', start)
    return text[start:end if end >= 0 else len(text)]


def _strings(source: str) -> list[str]:
    return [json.loads(m) for m in re.findall(r'"(?:[^"\\]|\\.)*"', source)]


def test_idiom_tables_equal_python():
    assert set(_strings(_definition(LEXICON, 'idioms1'))) == IDIOMS[1]
    assert set(_strings(_definition(LEXICON, 'idioms2'))) == IDIOMS[2]
    assert set(IDIOMS) == {1, 2}


def test_irregular_verbs_equal_python():
    words = _strings(_definition(LEXICON, 'irregularVerbs'))
    assert dict(zip(words[0::2], words[1::2])) == _IRREGULAR_VERBS


def test_past_verbs_equal_python():
    source = Path(ROOT / 've/english_vocabulary.py').read_text()
    python = re.search(r"past = (\{[^}]*\})", source)[1]
    expected = json.loads(python.replace("'", '"'))
    words = _strings(_definition(LEXICON, 'pastVerbs'))
    assert dict(zip(words[0::2], words[1::2])) == expected


def test_whitespace_list_equals_python_isspace():
    codes = {int(h, 16) for h in re.findall(r'0x([0-9A-Fa-f]+)', _definition(LEXER, 'spaceCodes'))}
    assert codes == {c for c in range(0x110000) if chr(c).isspace()}
