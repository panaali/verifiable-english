"""Reproducible, no-server copy measurement of the shipped web application."""
import json
import subprocess
import sys

from fastapi.testclient import TestClient

from ve_webapp.server import Settings, create_app
from webapp.vocabulary.audit import audit
from webapp.vocabulary.inventory import ASIMOV, ROOT, JS


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


def test_asimov_text_under_any_facts_is_catalogued():
    """Every sentence the Asimov section can show, after any fact edit, is a catalogue entry;
    a sentence VE cannot parse is a recorded gap with a reason, never an unlisted one."""
    from ve_webapp import asimov
    from webapp.vocabulary.build_catalogue import asimov_module_copy, segments
    catalogue = json.loads((ROOT / 'webapp/vocabulary/catalogue.json').read_text())
    shown = {}
    for entry in catalogue['entries']:
        if entry['source'] in (ASIMOV, 've_webapp/asimov.py') and entry['visibility'] == 'UI':
            for part in entry['segments']:
                shown.setdefault(part['text'], set()).add(part.get('gap', 'parsed'))
    wanted = {part for text in asimov_module_copy() for part in segments(text)}
    assert asimov.reader_copy() <= asimov_module_copy()
    assert 'The robot can stop the thief by tackling them, which injures the thief, or by ' \
           'locking the lab door, which injures no one.' in wanted
    assert wanted - set(shown) == set()
    assert all(reasons and '' not in reasons for reasons in shown.values())
    result = audit()
    assert result['errors'] == []
    assert {gap['text'] for gap in result['gaps'] if gap['source'] in (ASIMOV, 've_webapp/asimov.py')} \
        == {text for text, reasons in shown.items() if reasons != {'parsed'}}


def test_strict_copy_gate_tracks_recorded_violations():
    process = subprocess.run([sys.executable, '-m', 'webapp.vocabulary.audit', '--strict'],
                             cwd=ROOT, capture_output=True, text=True, check=False)
    result = json.loads(process.stdout)
    assert result['errors'] == []
    assert process.returncode == int(bool(result['gaps'] or result['dynamic_gaps']))
