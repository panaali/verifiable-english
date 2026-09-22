"""Amendment 5: offline transport failures, no paid/network calls."""
from dataclasses import replace
from decimal import Decimal
import json
from types import SimpleNamespace

import httpx
import pytest

from experiments import p1, p1_preflight as gates
from ve_experiments import paid
from ve_experiments.paid import (PaidRequest, PaidReply, PaidClient, Ledger,
    OfflineBackend, InfrastructureError, PreflightError, OpenRouterBackend, cost)


@pytest.fixture(autouse=True)
def no_backoff_wait(monkeypatch):
    monkeypatch.setattr(paid.time, 'sleep', lambda _: None)


def request(identity='dev/item/V/pro/initial/0'):
    return PaidRequest(identity, 'pro', [{'role': 'user', 'content': 'fixed'}], 100, 100)


def rows(ledger):
    return [json.loads(x) for x in ledger.path.read_text().splitlines()]


@pytest.mark.parametrize('exc,status', [
    (InfrastructureError('HTTP 429', 429), 429),
    (InfrastructureError('HTTP 503', 503), 503),
    (TimeoutError(), 'timeout'), (httpx.ReadTimeout('read'), 'timeout'),
])
def test_retry_same_assignment_and_budget_holds(tmp_path, monkeypatch, exc, status):
    seen, sleeps = [], []
    monkeypatch.setattr(paid.time, 'sleep', sleeps.append)
    def respond(req):
        seen.append(req)
        if len(seen) <= 3:
            raise exc
        return '{"verdict":"approve"}'
    ledger = Ledger(tmp_path / 'ledger', 1)
    ledger.reserve_block('dev', '.1')
    client = PaidClient(OfflineBackend(respond), ledger, 'dev')
    client.call(request())
    client.close()
    assert len(seen) == 4 and all(r == seen[0] for r in seen)
    assert sleeps == [1, 2, 4]
    failures = [r for r in rows(ledger) if r['event'] == 'infrastructure_failure']
    assert [r['attempt'] for r in failures] == [1, 2, 3]
    assert all(r['status'] == status and r['sample'] is False for r in failures)
    assert sum(r['event'] == 'complete' for r in rows(ledger)) == 1
    ledger.release_block('dev')
    _, spent, _, _, blocked = ledger.state(rows(ledger))
    assert spent == (0 if status == 429 else 3 * cost('pro', 100, 100))
    assert not blocked
    with pytest.raises(PreflightError, match='already dispatched'):
        ledger.reserve(seen[0])


def test_retry_exhaustion_survives_restart_and_is_not_a_trial(tmp_path):
    calls = []
    def fail(req):
        calls.append(req)
        raise InfrastructureError('busy', 429)
    ledger = Ledger(tmp_path / 'ledger', 1)
    for _ in range(2):
        client = PaidClient(OfflineBackend(fail), Ledger(ledger.path, 1))
        with pytest.raises(PreflightError, match='retry limit'):
            client.call(request())
        client.close()
    assert len(calls) == 4
    assert not any(r['event'] == 'complete' for r in rows(ledger))
    assert ledger.state(rows(ledger))[1] == 0


def test_unknown_billing_retry_cannot_exceed_cap(tmp_path):
    calls = []
    def fail(req):
        calls.append(req)
        raise TimeoutError()
    ledger = Ledger(tmp_path / 'ledger', cost('pro', 100, 100))
    client = PaidClient(OfflineBackend(fail), ledger)
    with pytest.raises(paid.BudgetExceeded):
        client.call(request())
    client.close()
    assert len(calls) == 1
    assert ledger.state(rows(ledger))[1] == ledger.cap


def test_output_failure_scored_once_and_nonretryable_http_halts(tmp_path):
    item = p1.materials('dev')[0]
    client = PaidClient(OfflineBackend(lambda _: 'not JSON'), Ledger(tmp_path / 'output', 1))
    trial, _ = p1.initial(client, item, 'V', 'pro', 256)
    assert trial['ok'] is False and trial['error'] == 'parse_failure'
    with pytest.raises(PreflightError, match='already dispatched'):
        p1.initial(client, item, 'V', 'pro', 256)
    client.close()
    def fail(_):
        raise InfrastructureError('HTTP 401', 401)
    client = PaidClient(OfflineBackend(fail), Ledger(tmp_path / 'http', 1))
    with pytest.raises(PreflightError, match='401'):
        client.call(request())
    client.close()
    assert [r['event'] for r in rows(client.ledger)] == ['reserve', 'halt']


def test_smoke_exception_recovers_legacy_halt_preserving_evidence(tmp_path):
    req = replace(request('provider-preflight/weak'), model='weak')
    ledger = Ledger(tmp_path / 'ledger', 1)
    ledger.reserve(req)
    ledger.halt(req, 'PreflightError: OpenRouter HTTP 404: unavailable provider')
    original = ledger.path.read_bytes()
    client = PaidClient(OfflineBackend(lambda _: 'Hi'), ledger)
    client.call(req)
    client.close()
    assert ledger.path.read_bytes().startswith(original)
    assert any(r['event'] == 'smoke_recovery' for r in rows(ledger))
    assert ledger.cached_reply(req).text == 'Hi'
    assert not ledger.state(rows(ledger))[-1]


def test_weak_provider_changes_allowed_but_within_provider_revision_pinned(tmp_path):
    current = {'provider': 'DeepInfra', 'fingerprint': 'a'}
    def reply(_):
        return PaidReply('Hi', 1, 1, 0, 0, json.dumps(current), dict(current), {})
    client = PaidClient(OfflineBackend(reply), Ledger(tmp_path / 'ledger', 1))
    req = replace(request(), model='weak')
    client.call(req)
    current['provider'] = 'Groq'
    client.call(replace(req, identity='two'))
    current['fingerprint'] = 'b'
    with pytest.raises(PreflightError, match='revision changed'):
        client.call(replace(req, identity='three'))
    client.close()
    assert [r['served_provider'] for r in rows(client.ledger) if r['event'] == 'complete'] == ['DeepInfra', 'Groq', 'Groq']


@pytest.mark.parametrize('cached_weak', [False, True])
def test_provider_preflight_resumes_legacy_ledger_and_is_idempotent(tmp_path, monkeypatch, cached_weak):
    monkeypatch.setattr(p1, 'HERE', tmp_path)
    monkeypatch.setattr(gates, 'refresh_status', lambda: [])
    p1.write_json(tmp_path / 'freeze.json', {'hashes': {}, 'manifest_sha256': 'new'})
    p1.write_json(tmp_path / 'results/probe.json', {'status': 'complete', 'calls': []})
    counter = SimpleNamespace(path=tmp_path / 'counter', sha256='counter', __call__=lambda _: 19)
    monkeypatch.setattr(gates, 'CommandCounter', lambda _: counter)
    monkeypatch.setattr(gates, 'tokenize', lambda *a: {'passed': True})
    class Metadata:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def get(self, url):
            return SimpleNamespace(raise_for_status=lambda: None, json=lambda: {'data': [{'id': v} for v in p1.MODELS.values()]})
    monkeypatch.setattr(httpx, 'Client', lambda **kw: Metadata())
    called = []
    class Backend(OfflineBackend):
        def __init__(self, **kw): super().__init__(self.reply)
        def count(self, req): return 21 if req.model == 'weak' else 19
        def reply(self, req):
            called.append(req.model)
            return PaidReply('Hi', self.count(req), 1, 0, 0, 'rev', {'usage': {}, 'provider': 'DeepInfra'}, {})
    monkeypatch.setattr(gates, 'OpenRouterBackend', Backend)
    ledger = Ledger(tmp_path / 'runs/provider-preflight/costs.jsonl', .5)
    def req(model):
        return PaidRequest(f'provider-preflight/{model}', model,
            [{'role': 'system', 'content': 'Reply with one word.'}, {'role': 'user', 'content': 'Hello'}], 3072, 1)
    ledger.reserve(req('replication'))
    ledger.complete(req('replication'), Backend().reply(req('replication')))
    ledger.reserve(req('weak'))
    if cached_weak:
        # The old HF template failed agreement (41 vs 21), but the completed
        # provider response remains reusable after the template correction.
        ledger.complete(req('weak'), Backend().reply(req('weak')))
    else:
        ledger.halt(req('weak'), 'OpenRouter HTTP 404: old slug')
    called.clear()
    assert gates.preflight_openrouter(.5) == 0
    assert called == ([] if cached_weak else ['weak'])
    original = ledger.path.read_bytes()
    assert gates.preflight_openrouter(.5) == 0
    assert called == ([] if cached_weak else ['weak']) and ledger.path.read_bytes() == original
    report = json.loads((tmp_path / 'checks/provider-preflight.json').read_text())
    assert report['passed'] and report['freeze_sha256'] == 'new'
    assert report['judges']['replication']['reused_smoke']
    assert report['judges']['weak']['native_smoke_tokens'] == 21
    if cached_weak:
        assert report['judges']['weak']['reused_smoke']


def test_completed_probe_is_noop(monkeypatch):
    monkeypatch.setattr(p1, 'VertexBackend', lambda: pytest.fail('no dispatch'))
    assert p1.probe(1) == 0


def test_openrouter_http_retry_and_invalid_tool_json_are_distinct(tmp_path, monkeypatch):
    monkeypatch.setenv('OPENROUTER_API_KEY', 'offline-test-key')
    calls = []
    class Transport:
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass
        async def post(self, url, **kwargs):
            calls.append(kwargs['json'])
            if len(calls) == 1:
                return httpx.Response(429, text='offline-test-key overloaded')
            return httpx.Response(200, json={
                'provider': 'Novita', 'model': p1.MODELS['weak'],
                'usage': {'prompt_tokens': 1, 'completion_tokens': 1, 'total_tokens': 2,
                    'completion_tokens_details': {'reasoning_tokens': 0},
                    'prompt_tokens_details': {'cached_tokens': 0}, 'cost': 0},
                'choices': [{'finish_reason': 'tool_calls', 'message': {
                    'role': 'assistant', 'content': '', 'tool_calls': [
                        {'id': 'bad', 'function': {'name': 'replay', 'arguments': 'bad JSON'}}]}}]})
    monkeypatch.setattr(httpx, 'AsyncClient', lambda **kw: Transport())
    client = PaidClient(OpenRouterBackend(counter=lambda _: 1), Ledger(tmp_path / 'ledger', 1))
    reply = client.call(replace(request(), model='weak'))
    client.close()
    assert len(calls) == 2 and calls[0] == calls[1]
    assert reply.tool_calls[0]['arguments'] == 'bad JSON'
    assert 'offline-test-key' not in client.ledger.path.read_text()
    assert rows(client.ledger)[-1]['served_provider'] == 'Novita'


def test_vertex_status_code_classification():
    from google.genai.errors import ClientError, ServerError
    assert paid.infrastructure_status(ClientError(429, {'error': {'message': 'busy'}})) == 429
    assert paid.infrastructure_status(ServerError(503, {'error': {'message': 'busy'}})) == 503
    assert paid.infrastructure_status(ClientError(400, {'error': {'message': 'bad'}})) is None


def test_retry_cannot_change_request_after_restart(tmp_path):
    ledger = Ledger(tmp_path / 'ledger', 1)
    req = request()
    ledger.reserve(req)
    ledger.infrastructure_failure(req, 'busy', 429, 0)
    with pytest.raises(PreflightError, match='changed frozen request'):
        Ledger(ledger.path, 1).reserve(replace(req, max_output_tokens=99))


def test_cache_rejects_changed_smoke_and_halted_complete(tmp_path):
    ledger = Ledger(tmp_path / 'ledger', 1)
    req = replace(request(), metadata={'role': 'probe'})
    client = PaidClient(OfflineBackend(lambda _: 'Hi'), ledger)
    client.call(req)
    client.close()
    with pytest.raises(PreflightError, match='cached smoke request changed'):
        ledger.cached_reply(replace(req, messages=[]))
    ledger.halt(req, 'billing validation failed')
    assert ledger.cached_reply(req) is None


@pytest.mark.parametrize('failure', [InfrastructureError('exhausted'), paid.BudgetExceeded('retry ceiling')])
def test_stopped_split_does_not_score_infrastructure_as_output(tmp_path, monkeypatch, failure):
    item = p1.materials('dev')[0]
    monkeypatch.setattr(p1, 'HERE', tmp_path)
    monkeypatch.setattr(p1, 'materials', lambda _: [item])
    monkeypatch.setattr(p1, 'arms', lambda _: ['V'])
    monkeypatch.setattr(p1, 'inventory', lambda: {'budget_scenarios': {
        'full_256': {'sources': ['E4'], 'judges': ['pro'], 'pushback': False}}})
    monkeypatch.setattr(p1, 'split_ceiling', lambda *a, **kw: Decimal('.01'))
    monkeypatch.setattr(p1, 'VertexBackend', lambda: OfflineBackend(lambda _: pytest.fail('dispatch')))
    monkeypatch.setattr(p1, 'analyze', lambda *a, **kw: pytest.fail('incomplete run must not score missing samples'))
    def fail(*a): raise failure
    monkeypatch.setattr(p1, 'initial', fail)
    p1.write_json(tmp_path / 'results/probe.json', {'status': 'complete', 'schedule': 'full_256', 'selected_output_cap': 256})
    p1.write_json(tmp_path / 'freeze.json', {'hashes': {}, 'manifest_sha256': 'new'})
    for gate in (*gates.GATES, 'provider-preflight'):
        p1.write_json(tmp_path / f'checks/{gate}.json', {'passed': True, 'freeze_sha256': 'new'})
    assert p1.run_split('dev', 2) == (3 if isinstance(failure, paid.BudgetExceeded) else 2)
    report = json.loads((tmp_path / 'runs/dev/analysis.json').read_text())
    assert report['families'] == {} and report['completed_observations'] == 0
    assert not (tmp_path / 'runs/dev/trials.jsonl').exists()
    assert not json.loads((tmp_path / 'checks/dev.json').read_text())['passed']
