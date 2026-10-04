"""The rejection sites of Python's English hand parser, classified for English in Lean (S0, spec 4.2, 7).

    uv run python -m conformance.english_lean_rejections

`SITES` lists every rejection site of `EnglishParser` and `_parse_english_document_uncached`
(`ve/english.py`), anchored by the start of its message, with its class:

- `G`: the text has no derivation in the generated grammar; Lean answers `none` and Python's message is a
  diagnostic only;
- `S`: the text has one derivation and its meaning is a declared rejection (`Reject` code of spec 5.8);
- `A`: subsumed by the ambiguity verdict (`many`);
- `B`: a blocked wording whose advice fires only when no atom matched, so Lean answers `none`; Python's
  advice remains the diagnostic shown (spec 4, D12);
- `L`: a lexer rejection; `R`: a resource limit; `X`: outside the reader (transport or API).

`PROBES` are sentences that witness a site's class by measurement: Python's verdict, the verdict of
Python's own Earley grammar (`require_unique_derivation`) and the verdict of that grammar over word
tokens (`conformance.english_lean_tokens`). For `S`, the Earley and token verdicts must be `one` while
Python rejects; for `G` and `B`, the token verdict must be `zero`. Measurement code; no admission path.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re

from ve import Environment
from ve.english import english_lark_grammar, parse_english
from ve.errors import VEError
from ve.surface.unambiguity import require_unique_derivation

from conformance import english_lean_engine as E
from conformance import english_lean_lexer as LX
from conformance import english_lean_tokens as K
from conformance.english_surface import order_environment, vocabularies

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'conformance' / 'english-lean' / 'rejections-report.json'

# (message prefix, number of call sites, class, Lean outcome or code, note)
SITES = [
    ("Expected {text!r} here", 22, 'G', 'none', '`need`: a fixed word or punctuation is missing'),
    ('Expected a space between these words.', 11, 'G', 'none',
     '`space`: over tokens spacing is invisible, so this is the O1 class (measured, section 4 of the report)'),
    ('This name is already in scope.', 1, 'S', 'shadowedName', 'probe p1, p2'),
    ('Expected a declared sort noun', 1, 'G', 'none', ''),
    ('The {name} of a term requires functional and total declarations.', 2, 'G', 'none',
     'attribute rules exist only for functional total relations (english.py `english_lark_grammar`)'),
    ('String-valued attribute properties require data stage 2.', 1, 'G', 'none',
     'property rules exclude the `$string` value sort'),
    ('The vocabulary gives this clause more than one meaning.', 1, 'A', 'many',
     'two templates match one span: two derivations'),
    ('A condition wording', 1, 'B', 'none', '`_RISK_CONDITION_IN_RULE`; to confirm on risk@0 texts in S3'),
    ('Phrase {…} extends existing wording', 1, 'G', 'none',
     'probe p11; plan 7.3 keeps it a shadow-comparison item: no derivable text was found'),
    ('Arithmetic term exceeds', 1, 'R', 'nestingLimit', ''),
    ('Expected an integer term such as [n + 1].', 1, 'G', 'none', ''),
    ('A scaling coefficient must be an integer numeral.', 1, 'S', 'new code needed',
     'probe p7: `[budget * limit]` has one derivation; the draft `Reject` list has no code for it'),
    ('Expected an integer term.', 1, 'G', 'none', ''),
    ('Unexpected text in an integer term.', 1, 'G', 'none', ''),
    ('_RISK_REJECTED (6 messages)', 1, 'B', 'none', 'in `unknown_atom`: fires only when no atom matched'),
    *((message, 1, 'B', 'none', 'alternatives@0 advice in `unknown_atom`: fires only when no atom matched')
      for message in ('The proximate cause wording needs a declared proximate role',
                      "Use the declared Boolean wording 'leads to' for this outcome.",
                      'This outcome wording is not Boolean.',
                      'Through inaction allows has two readings.',
                      'Write the long form: there is a harm such that',
                      "Permission for a person uses the W1 'may' wording")),
    ('Unknown English phrase', 1, 'G or S', 'none; unboundReference; pronounUnresolved',
     'G for unknown words; S when the phrase is a reference form the grammar derives but scope does not bind '
     '(probes p3, p4) or an `it` outside the first slot (probe p5)'),
    ('Expected a constant name or a definite reference', 1, 'G or S', 'none; unboundReference', 'as above'),
    ('Another action needs a rule on an action as its reference.', 1, 'S', 'unboundReference', 'probe p13'),
    ('The chooser has no antecedent', 1, 'S', 'unboundReference', 'probe p14'),
    ('The excluded action must be an action in scope.', 1, 'S', 'sortMismatch', 'not probed'),
    ('Choose whether no available action might lead to the harm', 1, 'S', 'blockedWording risk-every-cannot',
     '`_RISK_EVERY_CANNOT`; not probed'),
    ('This statement exceeds the 64-level nesting limit.', 1, 'R', 'nestingLimit', ''),
    ('This document exceeds the 10000-node limit.', 1, 'L', 'textTooLong',
     'every formula node consumes at least one character, so the node count never exceeds the collapsed length'),
    ('The referent of it is incomplete.', 1, 'S', 'pronounUnresolved', 'probe p6'),
    ('Plural or possessive reference needs', 1, 'B', 'none', 'probe p12'),
    ('Expected a or an before', 3, 'G', 'none', ''),
    ('The source and destination of a step must have the same sort.', 1, 'S', 'sortMismatch', 'probe p9'),
    ('Use an explicit for every clause for negation.', 1, 'S', 'blockedWording natural-negation', 'probe p10'),
    ('Expected a uniquely declared ownership clause.', 1, 'G', 'none', ''),
    ('Write at least one statement ending with a period.', 1, 'L', 'emptyDocument', ''),
    ('English input must be UTF-8.', 1, 'X', '—', 'the service receives a JSON string'),
    ('source must be str or bytes', 1, 'X', '—', 'API type check'),
    ('English source exceeds 65536 bytes', 1, 'L', 'sourceTooLong', ''),
]


def _fluent():
    return Environment.from_json((ROOT / 'examples/fluent/environment.json').read_bytes())


def _alternatives():
    import sys
    sys.path.insert(0, str(ROOT / 'tests'))
    from test_alternatives_profile import source
    raw = source()
    raw['vocabulary']['constants'] = {'r': {'sort': 'robot', 'description': 'r'},
                                      'h': {'sort': 'harm', 'description': 'h'}}
    return Environment(raw)


PROBES = [
    ('p1', 'fluent', 'For every service named S1, for every service named S1, S1 is reviewed.', 'S'),
    ('p2', 'fluent', 'For every service, for every service, that service is reviewed.', 'S'),
    ('p3', 'fluent', 'For every person, that service is reviewed.', 'S'),
    ('p4', 'fluent', 'That service is reviewed.', 'S'),
    ('p5', 'fluent', 'Legacy is deployed. Alice owns it.', 'S'),
    ('p6', 'fluent', 'Alice owns legacy. It is deployed.', 'S'),
    ('p7', 'order', 'Api costs [budget * limit].', 'S'),
    ('p8', 'order', 'Api costs [2 * limit].', 'accepted'),
    ('p9', 'closure', 'Starting from alice, legacy is reachable by one or more steps, where a step from a person '
                      'to a service satisfies this condition: that person owns that service.', 'S'),
    ('p10', 'fluent', 'Every deployed service is not reviewed.', 'S'),
    ('p11', 'fluent', 'Legacy is deployed quickly.', 'G'),
    ('p12', 'fluent', 'They are deployed.', 'G'),
    ('p13', 'alternatives', 'Another action available to r prevents h.', 'S'),
    ('p14', 'alternatives', 'Every action available to that robot prevents h.', 'S'),
]


def _environments():
    envs = dict(vocabularies())
    return {'fluent': _fluent(), 'order': order_environment(), 'closure': envs['closure'],
            'alternatives': _alternatives()}


def probe(env, text: str) -> dict:
    try:
        parse_english(env, text)
        python = 'accepted'
    except VEError as e:
        python = f'{type(e).__name__}: {str(e)[:100]}'
    try:
        require_unique_derivation(env, text[0].lower() + text[1:])
        earley = 'one'
    except VEError as e:
        earley = 'many' if 'two derivations' in str(e) else 'zero'
    G, _, _ = K.convert(english_lark_grammar(env))
    try:
        tokens = [('zero', 'one', 'many')[len(E.parse(G, E.terminal_accepts, 2, None, w))] for w in LX.lex(text)]
    except LX.LexError as e:
        tokens = ['lexical ' + e.code]
    return {'python': python, 'earley': earley, 'tokens': tokens}


def run() -> dict:
    envs = _environments()
    rows = []
    for pid, env_name, text, expected in PROBES:
        result = probe(envs[env_name], text)
        rejected_sentence = next((i for i, v in enumerate(result['tokens']) if v != 'one'), None)
        if expected == 'S':
            ok = result['python'] != 'accepted' and all(v == 'one' for v in result['tokens'])
        elif expected == 'G':
            ok = result['python'] != 'accepted' and 'zero' in result['tokens']
        else:
            ok = result['python'] == 'accepted' and all(v == 'one' for v in result['tokens'])
        rows.append({'id': pid, 'environment': env_name, 'text': text, 'class': expected, **result,
                     'consistent': ok, 'first_non_one_sentence': rejected_sentence})
    return {'format': 've.english-lean-rejections@1',
            'sites': [dict(zip(('message', 'call_sites', 'class', 'lean', 'note'), s)) for s in SITES],
            'call_sites': sum(s[1] for s in SITES), 'probes': rows,
            'consistent': all(r['consistent'] for r in rows)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    report = run()
    args.output.write_text(json.dumps(report, indent=1, sort_keys=True, ensure_ascii=False) + '\n')
    print(json.dumps({'consistent': report['consistent'], 'call_sites': report['call_sites'],
                      'inconsistent': [r['id'] for r in report['probes'] if not r['consistent']]}))
    return 0 if report['consistent'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
