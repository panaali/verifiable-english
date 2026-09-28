"""Reproducible, no-server copy measurement of the shipped web application."""
import json
import subprocess
import sys

from fastapi.testclient import TestClient

from ve_webapp.server import Settings, create_app
from webapp.vocabulary.audit import audit
from webapp.vocabulary.inventory import ROOT, JS


def test_catalogue_covers_served_page_and_source_literals(tmp_path):
    with TestClient(create_app(Settings('test-only-copy-audit-' + 'x' * 32, tmp_path,
                                        secure=False))) as client:
        page = client.get('/')
        assert page.status_code == 200
        assert client.get('/assets/app.js').text == (ROOT / JS).read_text()
        assert '/assets/app.js' in page.text
        result = audit(page.text)
    assert result['errors'] == []
    assert result['sentences'] > 0
    assert result['labels'] > 0
    # Every failed parse remains visible in the catalogue until the wording or
    # language changes; it cannot silently become a label.
    assert all(gap['reason'] for gap in result['gaps'])


def test_strict_copy_gate_tracks_recorded_violations():
    process = subprocess.run([sys.executable, '-m', 'webapp.vocabulary.audit', '--strict'],
                             cwd=ROOT, capture_output=True, text=True, check=False)
    result = json.loads(process.stdout)
    assert result['errors'] == []
    assert process.returncode == int(bool(result['gaps'] or result['dynamic_gaps']))
