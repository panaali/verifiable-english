"""Amendment 8 contract, pricing, recovery, fallback and budget regressions; $0."""
import asyncio
from dataclasses import asdict, replace
from decimal import Decimal
import json

import httpx
import pytest

from experiments import p1, p1_preflight
from ve_experiments import paid


def rows(ledger):
    return [json.loads(x) for x in ledger.path.read_text().splitlines()] if ledger.path.exists() else []


def request(judge='weak', arm='R'):
    return paid.PaidRequest('dev/item/' + arm + '/' + judge + '/initial/0', judge,
        [{'role': 'user', 'content': 'Return a JSON verdict.'}], 100, 1024,
        metadata={'split': 'dev', 'arm': arm, 'role': 'initial'}, response_schema=paid.VERDICT_SCHEMA)


def test_identical_judge_contract_all_arms_and_phases():
    item = p1.materials('dev')[0]
    vertex = paid.VertexBackend.__new__(paid.VertexBackend)
    for judge in paid.MODELS:
        for arm in p1.arms(item):
            for phase in ('initial', 'replay', 'pushback', 'probe'):
                req = p1.request(item, arm, judge, 256, phase=phase)
                assert req.max_output_tokens == 1024 and req.response_schema == paid.VERDICT_SCHEMA
                if judge == 'pro':
                    _, config = vertex.wire(req)
                    assert config.response_mime_type == 'application/json'
                    assert config.response_schema['properties']['verdict']['enum'] == ['approve', 'reject', 'unknown']
                else:
                    wire = paid.OpenRouterBackend().wire(req)
                    assert wire['response_format']['json_schema']['schema'] == paid.VERDICT_SCHEMA
    attacker = p1.request(item, 'A', 'pro', 256, phase='attacker')
    assert attacker.response_schema is None and attacker.max_output_tokens == 256
    assert p1.parse('```json\n{"verdict":"approve"}\n```') == ('approve', None)


@pytest.mark.parametrize('status,error,fallback', [
    (400, 'json_schema is not supported by this endpoint', True),
    (422, 'unsupported response_format json_schema', True),
    (400, 'invalid tools', False), (500, 'unsupported json_schema', False)])
def test_format_fallback_is_narrow_durable_and_preserves_tools(tmp_path, monkeypatch, status, error, fallback):
    monkeypatch.setenv('OPENROUTER_API_KEY', 'offline-test-key')
    ledger = paid.Ledger(tmp_path / 'ledger', 1)
    req = replace(request(), tools=[{'name': 'replay', 'parameters': {'type': 'object'}}])
    calls = []
    def transport(r):
        calls.append(json.loads(r.content))
        if len(calls) == 1:
            return httpx.Response(status, json={'error': {'message': error}})
        # The fallback event must already be durable before the second dispatch.
        assert rows(ledger)[-1]['event'] == 'structured_output_fallback'
        return httpx.Response(200, json={'model': paid.MODELS['weak'], 'provider': 'Groq',
            'usage': {'prompt_tokens': 10, 'completion_tokens': 10, 'total_tokens': 20,
                'completion_tokens_details': {'reasoning_tokens': 0}, 'prompt_tokens_details': {'cached_tokens': 0}, 'cost': .0000013},
            'choices': [{'message': {'role': 'assistant', 'content': '{"verdict":"approve"}'}, 'finish_reason': 'stop'}]})
    original = httpx.AsyncClient
    monkeypatch.setattr(httpx, 'AsyncClient', lambda **kw: original(transport=httpx.MockTransport(transport), timeout=kw['timeout']))
    backend = paid.OpenRouterBackend()
    backend.record_fallback = ledger.format_fallback
    if fallback:
        reply = asyncio.run(backend.generate(req))
        assert reply.response['_p1_response_format'] == 'json_object'
        assert calls[1] == {**calls[0], 'response_format': {'type': 'json_object'}}
    else:
        with pytest.raises(paid.InfrastructureError):
            asyncio.run(backend.generate(req))
        assert len(calls) == 1 and not rows(ledger)


def test_cached_list_prices_and_served_billing_guard(tmp_path):
    listing = json.loads((p1.HERE / 'checks/provider-preflight.json').read_text())
    for endpoint in listing['judges']['weak']['endpoints']['data']['endpoints']:
        ri, ro, _ = paid.WEAK_PROVIDER_RATES[endpoint['provider_name']]
        assert Decimal(ri) / 1000000 == Decimal(endpoint['pricing']['prompt'])
        assert Decimal(ro) / 1000000 == Decimal(endpoint['pricing']['completion'])
    for provider in ('Groq', 'CoreWeave'):
        ledger = paid.Ledger(tmp_path / provider, 1)
        billed = paid.cost('weak', 10, 10, provider=provider) / Decimal('1.055')
        backend = paid.OfflineBackend(lambda _: paid.PaidReply('{"verdict":"approve"}', 10, 10, 0, 0,
            'rev', {'provider': provider}, {}, provider_cost_usd=str(billed)))
        client = paid.PaidClient(backend, ledger)
        client.call(request())
        client.close()
        assert ledger.state(rows(ledger))[1] == billed * Decimal('1.055')
    with pytest.raises(paid.PreflightError, match='absent'):
        paid.cost('weak', 10, 10, provider='Unlisted')


def test_amended_dev_rebuys_changed_request_only_and_keeps_charges(tmp_path):
    ledger = paid.Ledger(tmp_path / 'ledger', 1)
    old = replace(request('pro'), max_output_tokens=256, response_schema=None)
    reply = paid.PaidReply('truncated', 10, 10, 432, 0, 'rev', {}, {})
    ledger.reserve(old)
    ledger.complete(old, reply, 'provider exceeded per-call token cap', panel_only=True)
    original = ledger.path.read_bytes()
    ledger.amend_dev('.1')
    ledger.amend_dev('.1')
    assert ledger.path.read_bytes().startswith(original)
    assert not p1.infrastructure_state(ledger)[1]
    dispatched = []
    client = paid.PaidClient(paid.OfflineBackend(lambda r: dispatched.append(r) or paid.PaidReply('{"verdict":"approve"}', 0, 0, 0, 0, 'rev', {}, {})), ledger, reuse_completed=True)
    client.call(request('pro')); client.call(request('pro'))
    assert len(dispatched) == 1 and '/amendment8/' in dispatched[0].identity
    client.close()
    assert ledger.state(rows(ledger))[1] == paid.cost('pro', 10, 442)
    assert sum(r['event'] == 'complete' for r in rows(ledger)) == 2
    unchanged = replace(request('weak', 'V'), response_schema=None)
    ledger.reserve(unchanged)
    ledger.complete(unchanged, paid.PaidReply('saved', 0, 0, 0, 0, 'offline', {}, {}))
    client = paid.PaidClient(paid.OfflineBackend(lambda _: pytest.fail('unchanged request must be reused')), ledger, reuse_completed=True)
    assert client.call(unchanged).text == 'saved'
    client.close()
    scored = replace(request(), identity='scored/x', metadata={'split': 'scored'})
    assert ledger.amended_dev_request(scored) == scored


def test_last_50_gemini_calls_and_sticky_primary_fallback(tmp_path):
    ledger = paid.Ledger(tmp_path / 'ledger', 1)
    # Older expensive calls and OpenRouter calls must not influence this window.
    with ledger.locked() as (f, _):
        for n in range(51):
            ledger.append(f, {'event': 'complete', 'model': 'pro', 'billed_output_tokens': 1024 if n == 0 else 512})
        ledger.append(f, {'event': 'complete', 'model': 'weak', 'billed_output_tokens': 1024})
    assert ledger.gemini_schedule() == 'full_256'
    with ledger.locked() as (f, _):
        ledger.append(f, {'event': 'complete', 'model': 'pro', 'billed_output_tokens': 513})
    assert ledger.gemini_schedule() == 'primary_1024'
    assert ledger.gemini_schedule() == 'primary_1024'
    assert sum(r['event'] == 'schedule_fallback' for r in rows(ledger)) == 1


def test_1024_billed_cap_including_thinking(tmp_path):
    for billed, ok in ((442, True), (1024, True), (1025, False)):
        ledger = paid.Ledger(tmp_path / str(billed), 1)
        client = paid.PaidClient(paid.OfflineBackend(lambda _: paid.PaidReply('', 0, 10, billed-10, 0, 'rev', {}, {})), ledger)
        if ok:
            assert client.call(request('pro')).billed_output_tokens == billed
        else:
            with pytest.raises(paid.PreflightError, match='token cap'):
                client.call(request('pro'))
        client.close()


def test_running_mean_planning_is_not_a_worst_case_ceiling():
    total = sum((p1.split_ceiling('full_256', split) for split in ('dev', 'scored')), Decimal(0)) + Decimal('1.8069')
    assert total == Decimal('49.8991773888')  # Amendment 9 inputs and one attacker retry.
    assert p1.STUDY_CAP_USD == 40


def test_real_dev_evidence_is_retained_and_recovery_spends_nothing(tmp_path):
    source = p1.HERE / 'runs/study/costs.jsonl'
    audit_path = p1.HERE / 'checks/amendment8.json'
    if not source.exists() or not audit_path.exists():
        pytest.skip('local dev evidence absent')
    import hashlib
    audit = json.loads(audit_path.read_text())
    lines = source.read_bytes().splitlines(keepends=True)
    assert hashlib.sha256(b''.join(lines[:audit['ledger_prefix_lines']])).hexdigest() == audit['ledger_prefix_sha256']
    ledger = paid.Ledger(tmp_path / 'ledger', 36)
    ledger.path.write_bytes(b''.join(lines[:audit['ledger_prefix_lines']]))
    original = ledger.state(rows(ledger))[1]
    ledger.amend_dev(p1.split_ceiling('full_256', 'dev'))
    assert ledger.state(rows(ledger))[1] == original
    assert not p1.infrastructure_state(ledger)[1]
    entries = rows(ledger)
    prior = {r['identity']: r for r in entries if r['event'] == 'reserve'}
    changed = 0
    for completion in (r for r in entries if r['event'] == 'complete'):
        saved = prior[completion['identity']]
        req = paid.PaidRequest(**{k: saved[k] for k in paid.PaidRequest.__dataclass_fields__ if k in saved})
        if req.metadata['role'] != 'attacker':
            req = replace(req, max_output_tokens=1024, response_schema=paid.VERDICT_SCHEMA)
            assert ledger.amended_dev_request(req).identity != req.identity
            changed += 1
        else:
            assert ledger.amended_dev_request(req) == req
            assert ledger.cached_reply(req).response == completion['response']
    assert changed == audit['changed_judge_requests']
