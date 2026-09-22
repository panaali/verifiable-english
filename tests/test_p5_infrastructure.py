"""Offline P5 authoring fallback and legacy-ledger recovery regressions."""
from dataclasses import replace
from decimal import Decimal
import json

import pytest

from experiments import p1, p5
from experiments.p5_materials import archive, read, write_json
from ve_experiments import paid


def test_only_paraphrase_enables_qwen_provider_fallback():
    item = p5.materials()[0]
    backend = paid.OpenRouterBackend()
    req = p5.request(item, 'shared', 'paraphrase')
    assert backend.wire(req)['provider'] == {
        'order': ['deepinfra', 'novita'], 'only': ['deepinfra', 'novita'],
        'allow_fallbacks': True, 'require_parameters': True,
    }
    for stage in ('judge', 'lone'):
        judge = p5.request(item, 'L', stage, judge='replication')
        assert backend.wire(judge)['provider'] == {
            'order': ['deepinfra'], 'only': ['deepinfra'], 'allow_fallbacks': False,
            'require_parameters': True, 'quantizations': ['fp8'],
        }


def test_paraphrase_resumes_legacy_failures_and_records_provider(tmp_path, monkeypatch):
    dossiers = read(p5.HERE / 'materials/dossiers.jsonl.gz')[:2]
    labels = p5.labels(False)
    monkeypatch.setattr(p5, 'HERE', tmp_path)
    monkeypatch.setattr(p5, 'verify_freeze', lambda **_: {'manifest_sha256': 'frozen'})
    monkeypatch.setattr(p5, 'labels', lambda _: labels)
    monkeypatch.setattr(p5, 'native_counter', lambda: None)
    archive(tmp_path / 'materials/dossiers.jsonl.gz', dossiers)
    write_json(tmp_path / 'checks/provider-preflight.json', {
        'freeze_sha256': 'frozen', 'models': {'replication': {'passed': True}},
    })
    book = p5.ledger('.17')
    book.reserve_block('shared-paraphrase', str(84 * paid.cost('replication', *p5.STAGES['paraphrase'])))
    req = p5.request({'id': dossiers[0]['id'], 'split': 'materials', 'payload': dossiers[0]},
                     'shared', 'paraphrase')
    req = replace(req, metadata={**req.metadata, 'block_id': 'shared-paraphrase'})
    for attempt in range(1, 5):
        book.reserve(req)
        book.infrastructure_failure(req, 'legacy 429', 429, 0, attempt=attempt)
    # No migration/rewrite needed, including for old records lacking lifetime_attempt.
    entries = read(book.path)
    for entry in entries:
        entry.pop('lifetime_attempt', None)
    book.path.write_text(''.join(paid.packed(r) + '\n' for r in entries))
    evidence = book.path.read_bytes()
    assert p1.infrastructure_state(book) == ({}, {})
    calls, sleeps = [], []
    monkeypatch.setattr(paid.time, 'sleep', sleeps.append)

    def respond(request):
        calls.append(request)
        if len(calls) == 1:
            raise paid.InfrastructureError('busy again', 429)
        dossier = next(d for d in dossiers if d['id'] == request.metadata['item_id'])
        provider = 'Novita' if dossier == dossiers[0] else 'DeepInfra'
        rate = Decimal('.38') if provider == 'Novita' else Decimal('.36')
        billing = (1000 * rate + 10 * Decimal('.40')) / 1000000
        return paid.PaidReply(json.dumps({'texts': {n['id']: n['text'] for n in dossier['nodes']}}),
            1000, 10, 0, 0, provider + '-revision', {'provider': provider}, {},
            provider_cost_usd=float(billing))

    monkeypatch.setattr(p5, 'OpenRouterBackend', lambda _: paid.OfflineBackend(respond))
    assert p5.paraphrase('.17')['slots'] == 2
    assert len(calls) == 3 and calls[0] == calls[1]
    assert sleeps == [5]
    assert book.path.read_bytes().startswith(evidence)
    completions = [r for r in read(book.path) if r['event'] == 'complete']
    assert [r['served_provider'] for r in completions] == ['Novita', 'DeepInfra']
    assert Decimal(completions[0]['cost_usd']) == Decimal('.000384') * Decimal('1.055')
    output = read(tmp_path / 'materials/paraphrases.jsonl.gz')
    assert [r['provenance']['served_provider'] for r in output] == ['Novita', 'DeepInfra']
    assert p5.paraphrase('.17')['slots'] == 2  # Cache, no replacement authoring samples.
    assert len(calls) == 3


@pytest.mark.parametrize('changed_role', ['judge', 'paraphrase'])
def test_paraphrase_revision_scope_does_not_unpin_judges(tmp_path, changed_role):
    item = p5.materials()[0]
    req = p5.request(item, 'shared', 'paraphrase')
    current = {'provider': 'DeepInfra', 'revision': 'deep-a'}

    def respond(_):
        return paid.PaidReply('{}', 1, 1, 0, 0, current['revision'],
                             {'provider': current['provider']}, {})

    book = paid.Ledger(tmp_path / 'ledger', 1)
    client = paid.PaidClient(paid.OfflineBackend(respond), book)
    judge = p5.request(item, 'L', 'lone', judge='replication')
    try:
        client.call(judge)
        current.update(provider='Novita', revision='novita-a')
        client.call(req)
        current.update(provider='DeepInfra', revision='deep-a')
        client.call(replace(req, identity='second-paraphrase'))
        client.call(replace(judge, identity='second-judge'))
        current.update(provider='Novita', revision='novita-a')
        changed = judge
        if changed_role == 'paraphrase':
            current['revision'] = 'novita-b'
            changed = req
        with pytest.raises(paid.PreflightError, match='revision changed'):
            client.call(replace(changed, identity='changed-revision'))
    finally:
        client.close()


def test_paraphrase_reserves_fallback_price_and_rejects_unlisted_provider(tmp_path):
    req = p5.request(p5.materials()[0], 'shared', 'paraphrase')
    book = paid.Ledger(tmp_path / 'ledger', 1)
    book.reserve(req)
    reservation = read(book.path)[0]
    assert Decimal(reservation['ceiling_usd']) == (
        4096 * Decimal('.38') + 1024 * Decimal('.40')) * Decimal('1.055') / 1000000
    with pytest.raises(paid.PreflightError, match='paraphrase price table'):
        paid.cost('replication', 1, 1, provider='Other', role='paraphrase')
