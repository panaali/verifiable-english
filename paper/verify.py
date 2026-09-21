#!/usr/bin/env python3
"""Check provenance and assembled artifacts; not a scientific claim verifier."""
from pathlib import Path
from hashlib import sha256
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

def main():
    manifest = json.loads((ROOT / 'sources/manifest.json').read_text())
    for record in manifest['files']:
        p = ROOT / 'sources' / record['file']
        assert sha256(p.read_bytes()).hexdigest() == record['sha256'], p
    audit = json.loads((ROOT / 'reference-audit.json').read_text())
    allowed = {r['url'] for r in audit}
    for record in audit:
        assert any(record['url'] in (ROOT.parent / p).read_text()
                   for p in record['repository_sources']), record['url']
    body = (ROOT / 'build/paper.md').read_text()
    assert '<!-- INCLUDE ' not in body
    assert body.isascii()
    urls = set(re.findall(r'\]\((https?://[^)]+)\)', body))
    assert urls <= allowed, urls - allowed
    assert len(re.findall(r'^# (?!Abstract|References)', body, re.M)) == 11
    status = json.loads((ROOT / 'build/draft-status.json').read_text())
    assert len(status['result_placeholders']) == 11, status['result_placeholders']
    if '--html' in sys.argv:
        html = (ROOT / 'build/paper.html').read_text()
        assert '<html' in html and '<math' in html and 'data:image/svg+xml' in html
        assert not re.search(r'<(?:img|link)[^>]+(?:src|href)="(?:figures/|style.css)', html)
        assert all(marker in html for marker in status['result_placeholders'])
    if '--pdf' in sys.argv:
        p = ROOT / 'build/paper.pdf'
        assert p.read_bytes().startswith(b'%PDF-')
        result = subprocess.run(['pdftotext', str(p), '-'], check=True, capture_output=True, text=True)
        assert all(marker in result.stdout for marker in status['result_placeholders'])
    plain = subprocess.run(['pandoc', str(ROOT / 'build/paper.md'), '-t', 'plain'],
                           check=True, capture_output=True, text=True).stdout
    status['rendered_word_count'] = len(plain.split())
    status['rendered_word_count_method'] = 'pandoc plain-text output split on whitespace; includes tables, captions and references, excludes metadata.'
    (ROOT / 'build/draft-status.json').write_text(json.dumps(status, indent=2) + '\n')
    print(f"Verified source hashes, citation allowlist, section inventory, and artifact; {status['rendered_word_count']:,} rendered words.")

if __name__ == '__main__':
    main()
