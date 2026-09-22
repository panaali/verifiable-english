"""Offline P5 authoring fallback and legacy-ledger recovery regressions."""
from dataclasses import replace
from decimal import Decimal
import json

import pytest

from experiments import p1, p5
from experiments.p5_materials import archive, read, write_json
from ve_experiments import paid


def source_item():
    dossier = read(p5.HERE / 'materials/dossiers.jsonl.gz')[0]
    return {'id': dossier['id'], 'split': 'materials', 'payload': dossier}


def test_only_paraphrase_enables_qwen_provider_fallback():
    item = source_item()
    backend = paid.OpenRouterBackend()
    req = p5.request(item, 'shared', 'paraphrase')
    assert backend.wire(req)['provider'] == {
        'order': ['deepinfra'], 'only': ['deepinfra'],
        'allow_fallbacks': False, 'require_parameters': True,
    }
    for stage in ('judge', 'lone'):
        judge = p5.request(item, 'L', stage, judge='replication')
        assert backend.wire(judge)['provider'] == {
            'order': ['deepinfra'], 'only': ['deepinfra'], 'allow_fallbacks': False,
            'require_parameters': True, 'quantizations': ['fp8'],
        }


def test_paraphrase_resumes_legacy_failures_and_records_provider(tmp_path, monkeypatch):
    monkeypatch.setattr('experiments.p5_semantics.acceptance_check', lambda *_: {'passed': True})
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
    item = source_item()
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
    req = p5.request(source_item(), 'shared', 'paraphrase')
    book = paid.Ledger(tmp_path / 'ledger', 1)
    book.reserve(req)
    reservation = read(book.path)[0]
    assert Decimal(reservation['ceiling_usd']) == (
        4096 * Decimal('.38') + 1024 * Decimal('.40')) * Decimal('1.055') / 1000000
    with pytest.raises(paid.PreflightError, match='paraphrase price table'):
        paid.cost('replication', 1, 1, provider='Other', role='paraphrase')


@pytest.mark.parametrize('status', [200, 429, 400, 422, 500, 504])
@pytest.mark.parametrize('stage', ['paraphrase', 'judge'])
def test_chat_wire_falls_back_only_for_rate_limited_paraphrase(tmp_path, monkeypatch, status, stage):
    import httpx
    monkeypatch.setenv('OPENROUTER_API_KEY', 'offline-key')
    monkeypatch.setattr(paid, 'INFRASTRUCTURE_BACKOFF_S', ())
    requests = []
    req = p5.request(source_item(), 'shared', stage, judge='replication')

    def capture(request):
        requests.append(request)
        if len(requests) == 1 and status != 200:
            return httpx.Response(status, json={'error': {'message': 'provider rejected'}})
        return httpx.Response(200, json={
            'provider': 'Novita' if len(requests) == 2 else 'DeepInfra',
            'model': paid.MODELS['replication'],
            'usage': {'prompt_tokens': 1, 'completion_tokens': 1, 'total_tokens': 2,
                      'completion_tokens_details': {'reasoning_tokens': 0},
                      'prompt_tokens_details': {'cached_tokens': 0}, 'cost': 0},
            'choices': [{'message': {'role': 'assistant', 'content': '{}'}}]})

    original = httpx.AsyncClient
    monkeypatch.setattr(httpx, 'AsyncClient', lambda **kw: original(transport=httpx.MockTransport(capture)))
    book = paid.Ledger(tmp_path / 'ledger', 1)
    client = paid.PaidClient(paid.OpenRouterBackend(lambda _: 1), book, reuse_completed=True)
    fallback = status == 429 and stage == 'paraphrase'
    try:
        if status == 200 or fallback:
            client.call(req)
        else:
            with pytest.raises(paid.InfrastructureError):
                client.call(req)
    finally:
        client.close()
    assert len(requests) == 1 + fallback
    for index, request in enumerate(requests):
        assert str(request.url) == 'https://openrouter.ai/api/v1/chat/completions'
        wire = json.loads(request.content)
        assert wire['messages'] == req.messages
        assert [m['role'] for m in wire['messages']] == ['system', 'user']
        assert 'prompt' not in wire
        provider = 'novita' if index else 'deepinfra'
        assert wire['provider']['only'] == wire['provider']['order'] == [provider]
        assert wire['provider']['allow_fallbacks'] is False
    if fallback:
        first, second = [json.loads(r.content) for r in requests]
        first.pop('provider'); second.pop('provider')
        assert first == second
    assert len([r for r in read(book.path) if r['event'] == 'provider_fallback']) == fallback


def endpoint_rejection(provider='Novita', raw=None):
    return 'InfrastructureError: OpenRouter HTTP 400: ' + json.dumps({'error': {
        'code': 400, 'metadata': {'provider_name': provider,
        'raw': raw or json.dumps({'reason': 'INVALID_REQUEST_BODY',
            'message': f"model: {paid.MODELS['replication']} does not support endpoint: completions"}),
        'previous_errors': [{'code': 504, 'provider_name': 'DeepInfra'}]}}})


@pytest.mark.parametrize('change', ['none', 'provider', 'error', 'role', 'identity', 'model'])
def test_endpoint_recovery_is_narrow_idempotent_and_keeps_hold(tmp_path, change):
    req = p5.request(source_item(), 'shared', 'paraphrase')
    error = endpoint_rejection()
    if change == 'provider': error = endpoint_rejection('DeepInfra')
    if change == 'error': error = endpoint_rejection(raw='some other 400')
    if change == 'role': req = replace(req, metadata={**req.metadata, 'role': 'judge'})
    if change == 'identity': req = replace(req, identity='materials/legacy')
    if change == 'model': req = replace(req, model='weak')
    book = paid.Ledger(tmp_path / 'ledger', 1)
    book.reserve(req)
    book.stop_panel(req, error)
    evidence = book.path.read_bytes()
    before = book.state(read(book.path))
    book.recover_paraphrase_routing()
    recovered = book.path.read_bytes()
    book.recover_paraphrase_routing()
    assert book.path.read_bytes() == recovered
    assert recovered.startswith(evidence)
    assert book.state(read(book.path)) == before
    if change == 'none':
        with pytest.raises(paid.PreflightError, match='changed frozen request'):
            book.reserve(replace(req, max_output_tokens=100))
        book.reserve(req)
    else:
        assert recovered == evidence
        with pytest.raises(paid.InfrastructureError):
            book.reserve(req)


def substantive_reply(dossier):
    from experiments.p5_paraphrase import inference_parts
    texts = {}
    for index, node in enumerate(dossier['nodes']):
        ant, con, tail, _ = inference_parts(node['text'])
        text = (f'Our reasoning rests on the following premises: {ant}. Therefore, {con}.' if index % 2
                else f'We take as our starting points the following information: {ant}; hence {con}.')
        texts[node['id']] = text + (' ' + tail if tail else '')
    return paid.PaidReply(json.dumps({'texts': texts}), 100, 10, 0, 0, 'revision',
                          {'provider': 'DeepInfra'}, {})


@pytest.mark.parametrize('invalid_cached', [None, 'copy', 'meaning'])
def test_v6_resumes_fourteen_completions_and_revalidates_semantics(tmp_path, monkeypatch, invalid_cached):
    from experiments import p5_revision
    dossiers = read(p5.HERE / 'materials/dossiers.jsonl.gz')[:15]
    labels = p5.labels(False)
    monkeypatch.setattr(p5, 'HERE', tmp_path)
    monkeypatch.setattr(p5_revision, 'HERE', tmp_path)
    monkeypatch.setattr(p5, 'labels', lambda _: labels)
    monkeypatch.setattr(p5, 'verify_freeze', lambda **_: {'manifest_sha256': 'frozen'})
    monkeypatch.setattr(p5, 'native_counter', lambda: None)
    monkeypatch.setenv('OPENROUTER_API_KEY', 'offline-key')
    archive(tmp_path / 'materials/dossiers.jsonl.gz', dossiers)
    write_json(tmp_path / 'checks/provider-preflight.json', {
        'freeze_sha256': 'frozen', 'models': {'replication': {'passed': True}}})
    book = p5_revision.revision_ledger('paraphrase', '.40')
    book.reserve_block('shared-paraphrase', '.40')
    for index, dossier in enumerate(dossiers):
        req = p5.request({'id': dossier['id'], 'split': 'materials', 'payload': dossier}, 'shared', 'paraphrase')
        req = replace(req, metadata={**req.metadata, 'block_id': 'shared-paraphrase'})
        book.reserve(req)
        if index == 14:
            book.stop_panel(req, endpoint_rejection())
        else:
            reply = substantive_reply(dossier)
            if index == 0 and invalid_cached == 'copy':
                # Correct meaning but copied prose must fail edit-distance acceptance.
                reply.text = json.dumps({'texts': {n['id']: n['text'] for n in dossier['nodes']}})
            elif index == 0 and invalid_cached == 'meaning':
                reply.text = reply.text.replace('unit', 'unit999', 1)
            book.complete(req, reply)
    evidence = book.path.read_bytes()
    calls = []
    def respond(req):
        calls.append(req)
        return substantive_reply(next(d for d in dossiers if d['id'] == req.metadata['item_id']))
    monkeypatch.setattr(p5, 'OpenRouterBackend', lambda _: paid.OfflineBackend(respond))
    result = p5.paraphrase('.40', revision=True)
    assert result['accepted'] == 15 and result['paraphrase_failed'] == 0
    assert [(r.metadata['item_id'], r.metadata['turn']) for r in calls] == (
        [(dossiers[0]['id'], 1)] if invalid_cached else []) + [(dossiers[14]['id'], 0)]
    assert book.path.read_bytes().startswith(evidence)
    assert p5.paraphrase('.40', revision=True) == result
    assert len(calls) == 1 + bool(invalid_cached)
    output = read(tmp_path / 'materials/paraphrases.jsonl.gz')
    assert all(r['provenance']['semantic_acceptance']['passed'] for r in output)
    before = book.path.read_bytes()
    assert p5.paraphrase(0, cached_only=True, revision=True) == result
    assert book.path.read_bytes() == before
