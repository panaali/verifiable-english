"""The shadow-corpus seal of English in Lean is self-consistent (its drift check is the harness's job)."""
import json

from ve.wire import digest

from conformance import english_lean_seal as Z


def test_seal_identity_covers_its_content():
    seal = json.loads(Z.SEAL.read_text())
    body = {k: v for k, v in seal.items() if k != 'seal_id'}
    assert seal['seal_id'] == digest(Z.DOMAIN, body)
    assert {e['kind'] for e in seal['sources']} == {'entry-point caller', 'corpus source'}
    assert len({e['path'] for e in seal['sources']}) == len(seal['sources'])
    assert any(row['stream'] == 'english-surface' for row in seal['generated'])
