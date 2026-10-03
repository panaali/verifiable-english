"""Seal the shadow corpus of English in Lean (plan section 5, S0): hash every source of corpus texts.

    uv run python -m conformance.english_lean_seal            # write conformance/english-lean/corpus-seal.json
    uv run python -m conformance.english_lean_seal --check    # report every sealed file that changed

The seal lists, with SHA-256: every file of the test suite, conformance, use cases and bench that calls an
English entry point; the use-case English documents, environments and overlays; the example environments;
the committed corpus reports whose per-configuration digests pin the generated streams; the pilot pins of
`bench/PROFILE-GOLDEN.json` (the pilots live in sibling checkouts and are pinned there, not copied); and the
item-1 fixture files. The generated streams are sealed by their recorded digests (seed, corpus, document
and grammar SHA-256 per configuration), which S2's harness recomputes before it compares.

`--check` is for the shadow harness: a changed source means the seal must be renewed before a comparison
counts. The test suite does not enforce it, so ordinary edits to tests stay independent of this item.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from ve.wire import digest

ROOT = Path(__file__).resolve().parents[1]
SEAL = ROOT / 'conformance' / 'english-lean' / 'corpus-seal.json'
DOMAIN = 've-english-lean-corpus-seal-v1\n'
ENTRY = re.compile(r"parse_english\b|parse_english_with_metadata|render_english\b|'ve_english'|\"ve_english\"")
GLOBS = ('usecases/*/rendered-english.md', 'usecases/*/*.ve.md', 'usecases/*/claims.ve',
         'usecases/*/environment*.json', 'examples/environment.json', 'examples/fluent/environment.json',
         'conformance/english-surface-report.json', 'conformance/english-mixed-report.json',
         'conformance/natural-view-report.json', 'conformance/english-lean-report.json',
         'bench/PROFILE-GOLDEN.json', 'conformance/english-lean/engine.json',
         'conformance/english-lean/lexer.json', 'conformance/english-lean/lexicon.json')


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sources() -> list[dict]:
    found: dict[str, str] = {}
    for directory in ('tests', 'conformance', 'usecases', 'bench'):
        for path in sorted((ROOT / directory).rglob('*.py')):
            rel = str(path.relative_to(ROOT))
            if 'english_lean' in path.name:
                continue
            if ENTRY.search(path.read_text(errors='replace')):
                found[rel] = 'entry-point caller'
    for pattern in GLOBS:
        for path in sorted(ROOT.glob(pattern)):
            found.setdefault(str(path.relative_to(ROOT)), 'corpus source')
    return [{'path': p, 'kind': k, 'sha256': _sha(ROOT / p)} for p, k in sorted(found.items())]


def generated() -> list[dict]:
    rows = []
    surface = json.loads((ROOT / 'conformance/english-surface-report.json').read_text())
    for row in surface['vocabularies']:
        rows.append({'stream': 'english-surface', 'vocabulary': row['vocabulary'], 'seed': row['seed'],
                     **{k: row[k] for k in ('corpus_sha256', 'random_earley_corpus_sha256',
                                            'document_corpus_sha256', 'grammar_sha256', 'environment_id',
                                            'unique_asts_roundtripped') if k in row}})
    mixed = json.loads((ROOT / 'conformance/english-mixed-report.json').read_text())
    rows.append({'stream': 'english-mixed', 'seed': mixed['seed'], 'texts': mixed['texts']})
    natural = json.loads((ROOT / 'conformance/natural-view-report.json').read_text())
    rows.append({'stream': 'natural-view', 'statements': natural['statements']})
    return rows


def pilots() -> list[dict]:
    golden = json.loads((ROOT / 'bench/PROFILE-GOLDEN.json').read_text())
    documents = golden['documents']
    items = documents.items() if isinstance(documents, dict) else enumerate(documents)
    return [{'pilot': str(name), 'pin': entry} for name, entry in items]


def build() -> dict:
    body = {'format': 've.english-lean-corpus-seal@1', 'sources': sources(), 'generated': generated(),
            'pilots': pilots()}
    return {**body, 'seal_id': digest(DOMAIN, body)}


def check(seal: dict) -> list[str]:
    drift = []
    for entry in seal['sources']:
        path = ROOT / entry['path']
        if not path.exists():
            drift.append(f"missing: {entry['path']}")
        elif _sha(path) != entry['sha256']:
            drift.append(f"changed: {entry['path']}")
    current = {e['path'] for e in sources()}
    drift += [f'unsealed: {p}' for p in sorted(current - {e['path'] for e in seal['sources']})]
    return drift


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--check', action='store_true', help='report sealed files that changed')
    args = parser.parse_args(argv)
    if args.check:
        drift = check(json.loads(SEAL.read_text()))
        for line in drift:
            print(line)
        print(f'{len(drift)} difference(s)', file=sys.stderr)
        return 1 if drift else 0
    seal = build()
    SEAL.write_text(json.dumps(seal, indent=1, sort_keys=True, ensure_ascii=False) + '\n')
    print(SEAL, seal['seal_id'], len(seal['sources']), 'sources')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
