"""Check every catalogue entry against the shipped page and VE parser.

The strict command exits nonzero while language gaps remain. It is intended as
the web copy build gate; the ordinary test keeps the measurement reproducible.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

from ve.environment import Environment
from ve.english import lint_english_vocabulary, parse_english
from webapp.vocabulary.inventory import ROOT, HTML, inventory, html_text

HERE = Path(__file__).resolve().parent


def load():
    catalogue = json.loads((HERE / 'catalogue.json').read_text())
    ui = json.loads((HERE / 'ui-terms.json').read_text())
    env = Environment(json.loads((HERE / 'environment.json').read_text()))
    english_vocabulary = json.loads((HERE / 'english-vocabulary.json').read_text())
    return catalogue, ui, env, english_vocabulary


def audit(page: str | None = None):
    catalogue, ui, env, english_vocabulary = load()
    errors = []
    gaps = []
    if catalogue['format'] != 've-web-copy@1' or ui['format'] != 've-web-ui-terms@1':
        errors.append('Unknown catalogue or UI vocabulary format')
    lint = lint_english_vocabulary(env, vocabulary=english_vocabulary)
    errors.extend(f'App vocabulary: {issue}' for issue in lint)
    actual = inventory(html_source=page)
    for source, expected_digest in catalogue['sources'].items():
        digest = hashlib.sha256((ROOT / source).read_bytes()).hexdigest()
        if digest != expected_digest:
            errors.append(f'{source}: source changed without catalogue review')
    grouped = {}
    for entry in catalogue['entries']:
        grouped.setdefault(entry['source'], set()).add(entry['raw'])
    for source, values in actual.items():
        if values != grouped.get(source, set()):
            errors.append(f'{source}: literal inventory differs from catalogue')
    if page is not None and html_text(page) != grouped.get(HTML, set()):
        errors.append('Served page differs from catalogued visible HTML')
    words = set(ui['open_terms'])
    count = Counter()
    for entry in catalogue['entries']:
        if entry['visibility'] == 'INTERNAL':
            continue
        if entry['visibility'] != 'UI' or not entry.get('segments'):
            errors.append(f"{entry['source']}: invalid visibility classification")
            continue
        for item in entry['segments']:
            kind, text = item['kind'], item['text']
            count[kind] += 1
            if kind == 'LABEL':
                tokens = re.findall(r'[A-Za-z][A-Za-z0-9]*', text)
                missing = [token for token in tokens if token.casefold() not in words]
                if missing or len(tokens) > 8 or text.endswith(('.', '?', '!')):
                    errors.append(f"Invalid label {text!r}: unknown words {missing}")
            elif kind == 'SENTENCE':
                try:
                    parsed = parse_english(env, text, vocabulary=english_vocabulary)
                    if len(parsed.formulas) != 1:
                        raise ValueError('Expected exactly one formula')
                    if item.get('gap'):
                        errors.append(f"Stale language gap: {text!r}")
                except Exception as exc:
                    if item.get('gap') != type(exc).__name__:
                        errors.append(f"New or changed parse failure {text!r}: {type(exc).__name__}: {exc}")
                    else:
                        gaps.append({'source': entry['source'], 'text': text,
                                     'reason': type(exc).__name__})
            else:
                errors.append(f"Invalid catalogue kind: {kind!r}")
    return {'sentences': count['SENTENCE'], 'labels': count['LABEL'],
            'gaps': gaps, 'dynamic_gaps': catalogue['dynamic_gaps'], 'errors': errors}


def main() -> int:
    result = audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    strict = '--strict' in sys.argv
    return int(bool(result['errors'] or (strict and (result['gaps'] or result['dynamic_gaps']))))


if __name__ == '__main__':
    raise SystemExit(main())
