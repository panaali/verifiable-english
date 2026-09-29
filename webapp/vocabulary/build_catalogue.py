"""Regenerate the reviewed copy inventory after editing shipped app text.

Run this locally, then review every changed classification and gap. The test
compares this snapshot with the actual assets and Python message literals.
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re

from ve.environment import Environment
from ve.english import parse_english
from webapp.vocabulary.inventory import ROOT, HTML, JS, ASIMOV, SOURCES, inventory
from ve_webapp.examples import EXAMPLES


def raised_messages(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    result = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Name) or node.func.id not in {'HTTPException', 'ValueError', 'StaleDraft'}:
            continue
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                result.add(arg.value)
            elif isinstance(arg, ast.JoinedStr):
                result.add(''.join(part.value if isinstance(part, ast.Constant) else '{}'
                                   for part in arg.values))
    return result


def asimov_module_copy() -> set[str]:
    """Explanation sentences, notes and scenario text (under any facts) a live re-run can show."""
    from ve_webapp import asimov
    constants = {value for name, value in vars(asimov).items()
                 if name.isupper() and isinstance(value, str) and name not in ('CASE', 'OUTPUT')}
    return (constants | set(asimov.NO_CLEAR.values()) | set(asimov.OPEN_LIMITS)
            | set(asimov.GROUPS.values()) | asimov.reader_copy())


def visible_sources(raw: dict[str, set[str]]) -> dict[str, set[str]]:
    # All DOM text and accessible attributes in the served page are included.
    result = {HTML: raw[HTML]}
    # Browser literals with a capital initial are copy unless explicitly known
    # protocol/control tokens. Dynamic status fields are listed separately.
    internal_js = {'Content-Type', 'X-VE-CSRF', 'GET', 'POST', 'Enter', 'Invalid request',
                   'String', 'Data', 'JSON', 'CONFLICT-FREE'}
    result[JS] = {s for s in raw[JS] if s and (s[0].isupper() or s[0] in '✓↗?“')
                  and s not in internal_js}
    result[JS] |= {s for s in raw[JS] if s.startswith('{} ·') or s.startswith('“{}”')}
    result[JS] |= {'blank draft', 'saving', 'explicit form', 'unknown', 'true', 'false'} & raw[JS]
    server = 've_webapp/server.py'
    result[server] = raised_messages(ROOT / server)
    result[server] |= {'Request exceeds 32 KiB.', 'Request timed out.'} & raw[server]
    # Configuration/startup errors are not browser messages.
    result[server] -= {'Access token must contain at least 32 characters; generate a random token.',
                       'Call caps must be positive.', 'Could not detect claude --version; use --claude-cli-version.',
                       'Claude CLI version cannot be empty.'}
    drafts = 've_webapp/drafts.py'
    result[drafts] = raised_messages(ROOT / drafts) | {
        'Unsigned copy; access to this export does not prove authorship.'}
    worker = 've_webapp/worker.py'
    result[worker] = {s for s in raw[worker] if s and s[0].isupper() and
                      (s.endswith('.') or s.endswith(' ') or s.startswith('This world has'))
                      and not s.startswith(('Disposable,', 'A plain-language'))}
    rules = 've_webapp/rules.py'
    result[rules] = {s for s in raw[rules] if s.startswith(('For an urgent act,',
        'The checked rules', 'The check ran', 'Rule 1.'))}
    # The Asimov section shows the built data, catalogued as served. Its module
    # adds the explanation sentences, notes and scenario text under other facts that a
    # live re-run can show, unless the built data already shows each of its sentences.
    result[ASIMOV] = raw[ASIMOV]
    module = 've_webapp/asimov.py'
    built = {part for value in raw[ASIMOV] for part in segments(value)}
    result[module] = {value for value in raw[module] & asimov_module_copy()
                      if not set(segments(value)) <= built}
    examples = 've_webapp/examples.py'
    result[examples] = set()
    for example in EXAMPLES:
        result[examples].update(example[k] for k in ('title', 'category', 'english', 'note'))
        vocab = example['environment']['vocabulary']
        for group in ('sorts', 'predicates', 'constants'):
            result[examples].update(entry['description'] for entry in vocab[group].values())
    return result


def segments(raw: str) -> list[str]:
    return [part.strip() for part in re.split(r'(?<=[.!?])\s+(?=[A-Z])', raw) if part.strip()]


def is_sentence(text: str) -> bool:
    # A sentence with a missing full stop is still a sentence, not a label.
    return (text.endswith(('.', '?', '!', '…')) or
            ('.' in text and text != 've-document.json') or
            text.startswith(('There are no true cases of', 'This world has ',
                             '{} · one paid call per request')))


def main() -> None:
    raw = inventory()
    visible = visible_sources(raw)
    env = Environment(json.loads((ROOT / 'webapp/vocabulary/environment.json').read_text()))
    english_vocabulary = json.loads((ROOT / 'webapp/vocabulary/english-vocabulary.json').read_text())
    entries = []
    for source in SOURCES:
        for value in sorted(raw[source]):
            if value not in visible[source]:
                entries.append({'source': source, 'raw': value, 'visibility': 'INTERNAL'})
                continue
            parts = []
            for text in segments(value):
                kind = 'SENTENCE' if is_sentence(text) else 'LABEL'
                entry = {'kind': kind, 'text': text}
                if kind == 'SENTENCE':
                    try:
                        parse_english(env, text, vocabulary=english_vocabulary)
                    except Exception as exc:
                        entry['gap'] = type(exc).__name__
                parts.append(entry)
            entries.append({'source': source, 'raw': value, 'visibility': 'UI', 'segments': parts})
    labels = sorted({word.casefold() for entry in entries if entry['visibility'] == 'UI'
                     for part in entry['segments'] if part['kind'] == 'LABEL'
                     for word in re.findall(r"[A-Za-z][A-Za-z0-9]*", part['text'])})
    output = {'format': 've-web-copy@1',
              'sources': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCES},
              'entries': entries,
              'dynamic_gaps': [
                  {'source': JS, 'expression': 'data.error.message and data.detail',
                   'reason': 'Core and framework diagnostics are displayed without a VE parse.'},
                  {'source': JS, 'expression': 'user text, model glosses, draft reasons and situation summaries',
                   'reason': 'Unbounded external or user-authored text reaches visible nodes.'},
                  {'source': JS, 'expression': 'document state, revision number, model and evaluation values',
                   'reason': 'Status fragments and interpolated numbers are not VE sentences.'},
                  {'source': 've_webapp/worker.py', 'expression': '_reader_world and _comparison_summary',
                   'reason': 'Generated world prose uses undeclared names, counts and truth wording.'},
                  {'source': 've_webapp/rules.py', 'expression': 'RULES_TEXT',
                   'reason': 'Norm examples use the separate norm grammar, not the writable English parser.'},
                  {'source': 've_webapp/asimov.py', 'expression': 'explain, _laws and a reader edit through POST /api/asimov',
                   'reason': 'A live re-run joins fixed explanation sentences and law names; '
                             'a combination absent from asimov.json is not catalogued. Each '
                             'scenario sentence under any facts is catalogued on its own.'},
              ]}
    path = ROOT / 'webapp/vocabulary/catalogue.json'
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False) + '\n')
    terms = ROOT / 'webapp/vocabulary/ui-terms.json'
    terms.write_text(json.dumps({'format': 've-web-ui-terms@1',
        'open_terms': labels,
        'aliases': {'ve': 'app', 'desk': 'workspace', 'claim': 'conclusion',
                    'countermodel': 'world'},
        'symbols': ['✓', '◐', '→', '↓', '⌘', '&', '/', '·', ':', '(', ')', ',', '-', '1', '2']},
        indent=2, ensure_ascii=False) + '\n')
    gaps = [p for e in entries if e['visibility'] == 'UI' for p in e['segments'] if p.get('gap')]
    print(f'{sum(p["kind"] == "SENTENCE" for e in entries if e["visibility"] == "UI" for p in e["segments"])} sentences, '
          f'{sum(p["kind"] == "LABEL" for e in entries if e["visibility"] == "UI" for p in e["segments"])} labels, '
          f'{len(gaps)} parse gaps')


if __name__ == '__main__':
    main()
