"""The data of English in Lean that Python produces or names (docs/spec/english-lean-s2.md 2.9, 2.10).

The directory holds each profile's fixed-rule source (`relational-fol@0.json`, `order@0.json`,
`alternatives@0.json`) and the lock file (`LOCK.json`), which `tools/english_grammar_gen.py` checks and
renders into Lean. This module gives the adapter (`ve/backends/english_lean.py`) what it compares Lean's
identities with: the lexicon Python selects (`export`, base 5.8) and its `lexicon_id`, the `grammar_id` of an
environment's profiles and the `actions_version` of the lock file (base 2.12). Python gets no copy of the
grammar (S2 plan, A1).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ..wire import digest

HERE = Path(__file__).resolve().parent
LEXICON_DOMAIN = 've-english-lexicon-v1\n'
LEXICON_FORMAT = 've.english-lexicon@1'
GRAMMAR_DOMAIN = 've-english-grammar-v1\n'
# The profiles that have a fixed-rule table, with its source (spec 2.5: `closure@0` has none; S3 2.14: the
# staged tables of `order@0` and `alternatives@0`). `tools/english_grammar_gen.py` generates Lean's list of
# the same tables; tests/test_english_grammar_gen.py checks that the two name the same sources.
TABLES = {'relational-fol@0': 'relational-fol@0.json', 'order@0': 'order@0.json',
          'alternatives@0': 'alternatives@0.json'}


def export(words) -> dict:
    """The lexicon Python selects (an `EnglishVocabulary`), in the field order of base 5.8; every list sorted
    by symbol."""
    return {
        'format': LEXICON_FORMAT,
        'environment_id': words.env.environment_id,
        'nouns': sorted([s, n] for s, n in words.sorts.items()),
        'letters': sorted([s, l] for s, l in words.letters.items()),
        'wordings': sorted([p, w] for p, w in words.predicates.items()),
        'negatives': sorted([p, w] for p, w in words.negatives.items()),
        'aliases': sorted([p, w, bool(neg)] for p, w, neg in words.input_aliases),
        'spellings': sorted([c, s] for c, s in words.constants.items()),
    }


def lexicon_id(lexicon: dict) -> str:
    return digest(LEXICON_DOMAIN, lexicon)


def grammar_id(profiles) -> str:
    """The digest, under `ve-english-grammar-v1`, of the environment's profiles that have a table, in the
    environment's order, each with the SHA-256 of its JSON source (base 2.12)."""
    return digest(GRAMMAR_DOMAIN, [[profile, hashlib.sha256((HERE / TABLES[profile]).read_bytes()).hexdigest()]
                                   for profile in profiles if profile in TABLES])


def actions_version() -> str:
    return json.loads((HERE / 'LOCK.json').read_text())['actions_version']


CODES_FORMAT = 've.english-codes@1'


def codes() -> tuple[dict[str, str], dict[str, tuple[str, ...]], frozenset[str]]:
    """Lean's class of every code, the codes each response status may carry and the rejection codes that name
    no sentence (`Run.codeClasses`, `Run.statusCodes`, `Run.unsentencedCodes`), as the `english.grammar` export
    gives them. `codes.json` is written from the service by `tools/english_codes.py --write`, and the suite
    checks it against the service: the relay keeps no table of its own (spec 2.6, D9)."""
    data = json.loads((HERE / 'codes.json').read_text())
    if data.get('format') != CODES_FORMAT:
        raise ValueError(f'{HERE / "codes.json"}: format is not {CODES_FORMAT}')
    return ({code: cls for code, cls in data['codes']},
            {status: tuple(found) for status, found in data['statuses']}, frozenset(data['unsentenced']))
