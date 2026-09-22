"""Amendment 7: entirely offline dispatch, restart and partial-panel evidence."""
from dataclasses import replace
from decimal import Decimal
import json
import shutil

import pytest

from experiments import p1, p1_preflight
from ve_experiments import paid


def entries(ledger):
    return [json.loads(line) for line in ledger.path.read_text().splitlines()]


def req(judge='weak', arm='R', phase='initial'):
    return paid.PaidRequest(f'dev/item/{arm}/{judge}/{phase}/0', judge,
        [{'role': 'user', 'content': 'fixed'}], 100, 10,
        [{'name': 'replay', 'parameters': {'type': 'object'}}] if phase == 'initial' and arm == 'R' else [],
        {'arm': arm, 'split': 'dev'})


def test_only_weak_r_removes_provider_and_quantization_filters():
    backend = paid.OpenRouterBackend()
    for phase in ('initial', 'replay'):
        wire = backend.wire(req(phase=phase))
        assert wire['provider'] == {'require_parameters': True}
        assert (wire['temperature'], wire['seed'], wire['max_tokens']) == (0, 20260921, 10)
    assert backend.wire(req(arm='A'))['provider']['only'] == ['deepinfra', 'novita', 'groq']
    assert backend.wire(req('replication'))['provider']['only'] == ['deepinfra']
    evidence = json.loads((p1.HERE / 'checks/provider-preflight.json').read_text())
    qwen = evidence['judges']['replication']['endpoints']['data']['endpoints']
    assert any(e['provider_name'] == 'DeepInfra' and 'tools' in e['supported_parameters'] for e in qwen)


def test_legacy_rejection_recovered_once_and_completed_calls_not_rebought(tmp_path):
    ledger = paid.Ledger(tmp_path / 'ledger', 1)
    ledger.reserve_block('dev', '.1')
    seen = []
    client = paid.PaidClient(paid.OfflineBackend(lambda r: seen.append(r) or 'malformed output'), ledger, 'dev', reuse_completed=True)
    first = client.call(req(arm='V'))
    failed = replace(req(), metadata={**req().metadata, 'block_id': 'dev'})
    ledger.reserve(failed)
    ledger.halt(failed, 'InfrastructureError: OpenRouter HTTP 404: No endpoints found that support tool use')
    original = ledger.path.read_bytes()
    ledger.recover_tool_routing()
    ledger.recover_tool_routing()
    ledger.reserve_block('dev', '.1', resume=True)
    assert client.call(req(arm='V')) == first
    client.call(req())
    client.close()
    assert len(seen) == 2
    assert ledger.path.read_bytes().startswith(original)
    assert sum(r['event'] == 'routing_recovery' for r in entries(ledger)) == 1
    assert not ledger.state(entries(ledger))[-1]
    with pytest.raises(paid.PreflightError, match='changed'):
        ledger.cached_reply(replace(failed, messages=[]))


def test_tool_unavailability_releases_reservation_and_is_durable(tmp_path):
    ledger = paid.Ledger(tmp_path / 'ledger', 1)
    ledger.reserve_block('dev', '.1')
    calls = []
    def reply(r):
        calls.append(r)
        raise paid.InfrastructureError('No endpoints found that support tool use', 404)
    client = paid.PaidClient(paid.OfflineBackend(reply), ledger, 'dev', reuse_completed=True)
    with pytest.raises(paid.ToolEndpointUnavailable):
        client.call(req())
    with pytest.raises(paid.ToolEndpointUnavailable):
        client.call(replace(req(), identity='dev/other/R/weak/initial/0'))
    client.close()
    assert len(calls) == 1
    row = entries(ledger)[-1]
    assert row['event'] == 'arm_unavailable' and row['sample'] is False
    pending, spent, _, _, blocked = ledger.state(entries(ledger))
    assert pending == {'block:dev': Decimal('.1')} and spent == 0 and not blocked


@pytest.fixture
def split_env(tmp_path, monkeypatch):
    original = p1.HERE
    all_items = p1.materials('dev')
    first = next(i for i in all_items if i['assignment']['source'] == 'E4')
    items = [i for i in all_items if i['assignment']['template'] == first['assignment']['template']]
    shutil.copytree(original / 'prompts', tmp_path / 'prompts')
    monkeypatch.setattr(p1, 'HERE', tmp_path)
    monkeypatch.setattr(p1, 'materials', lambda _: items)
    monkeypatch.setattr(p1, 'inventory', lambda: {'budget_scenarios': {
        'full_256': {'sources': ['E4'], 'judges': ['weak', 'replication', 'pro'], 'pushback': False}}})
    monkeypatch.setattr(p1, 'split_ceiling', lambda *a: Decimal('.1'))
    monkeypatch.setattr(p1_preflight, 'runtime_counter', lambda: None)
    monkeypatch.setattr(paid.time, 'sleep', lambda _: None)
    p1.write_json(tmp_path / 'results/probe.json', {'status': 'complete', 'schedule': 'full_256', 'selected_output_cap': 256})
    p1.write_json(tmp_path / 'freeze.json', {'hashes': {}, 'manifest_sha256': 'test'})
    for gate in (*p1_preflight.GATES, 'provider-preflight'):
        p1.write_json(tmp_path / f'checks/{gate}.json', {'passed': True, 'freeze_sha256': 'test'})
    return tmp_path, items


@pytest.mark.parametrize('error', ['tools', '401', '429'])
def test_judges_continue_and_restart_reuses_all_calls(split_env, monkeypatch, error):
    path, items = split_env
    calls = []
    def respond(r):
        calls.append(r.identity)
        if r.model == 'weak' and r.metadata['arm'] == 'R':
            raise paid.InfrastructureError('No endpoints found that support tool use' if error == 'tools' else error,
                                           404 if error == 'tools' else int(error))
        return '{"verdict":"approve"}'
    monkeypatch.setattr(p1, 'OpenRouterBackend', lambda *a: paid.OfflineBackend(respond))
    monkeypatch.setattr(p1, 'VertexBackend', lambda: paid.OfflineBackend(respond))
    assert p1.run_split('dev', 2) == (0 if error == 'tools' else 2)
    ledger = paid.Ledger(path / 'runs/study/costs.jsonl', 2)
    before = ledger.path.read_bytes()
    trials = (path / 'runs/dev/trials.jsonl').read_bytes()
    count = len(calls)
    assert p1.run_split('dev', 2) == (0 if error == 'tools' else 2)
    assert len(calls) == count and ledger.path.read_bytes() == before
    assert (path / 'runs/dev/trials.jsonl').read_bytes() == trials
    report = json.loads((path / 'runs/dev/analysis.json').read_text())
    assert {'replication/E4', 'pro/E4'} <= report['families'].keys()
    gates = json.loads((path / 'checks/dev.json').read_text())['gates']
    assert gates['replication/E4']['complete'] and gates['pro/E4']['complete']
    assert gates['weak/E4']['numbers']['V']['failures'] == 0
    if error == 'tools':
        assert 'R' not in report['families']['weak/E4']['rates']
        assert report['unavailable_arms']['weak']['R']
        assert 'R' not in gates['weak/E4']['numbers']
    else:
        assert 'weak/E4' not in report['families']
        assert gates['weak/E4']['numbers']['R']['completed'] == 0
        assert gates['weak/E4']['numbers']['R']['failures'] == 0
        assert gates['weak/E4']['halted']


def test_all_19_retained_calls_reuse_exact_original_responses(tmp_path):
    source = p1.HERE / 'runs/study/costs.jsonl'
    if not source.exists():
        pytest.skip('local dev evidence absent in clean checkout')
    ledger = paid.Ledger(tmp_path / 'ledger', 36)
    shutil.copyfile(source, ledger.path)
    rows = entries(ledger)
    client = paid.PaidClient(paid.OfflineBackend(lambda _: pytest.fail('must not dispatch')), ledger, 'dev', reuse_completed=True)
    count = 0
    for row in rows:
        if row['event'] != 'complete':
            continue
        reservation = next(r for r in rows if r['event'] == 'reserve' and r['identity'] == row['identity'])
        request = paid.PaidRequest(**{k: reservation[k] for k in paid.PaidRequest.__dataclass_fields__})
        assert client.call(request).response == row['response']
        count += 1
    client.close()
    assert count >= 19
    assert ledger.path.read_bytes() == source.read_bytes()


def test_resume_between_initial_tool_call_and_replay(tmp_path):
    item = p1.materials('dev')[0]
    ledger = paid.Ledger(tmp_path / 'ledger', 1)
    ledger.reserve_block('dev', '.1')
    phases = []
    def respond(r):
        phases.append(r.metadata['role'])
        if r.metadata['role'] == 'initial':
            call = {'id': 'saved-tool-id', 'name': 'replay', 'arguments': {'item_id': item['id']}}
            return paid.PaidReply('', 0, 0, 0, 0, 'offline', {'provider': 'Groq'},
                {'role': 'assistant', 'content': '', 'tool_calls': [{'id': call['id'], 'type': 'function',
                 'function': {'name': 'replay', 'arguments': json.dumps(call['arguments'])}}]}, [call])
        assert r.messages[-1]['tool_call_id'] == 'saved-tool-id'
        return paid.PaidReply('{"verdict":"approve"}', 0, 0, 0, 0, 'offline', {'provider': 'Groq'},
                              {'role': 'assistant', 'content': '{"verdict":"approve"}'})
    client = paid.PaidClient(paid.OfflineBackend(respond), ledger, 'dev', reuse_completed=True)
    client.call(p1.request(item, 'R', 'weak', 256))
    client.close()  # Process stopped before its continuation and trial row.
    restarted = paid.PaidClient(paid.OfflineBackend(respond), ledger, 'dev', reuse_completed=True)
    row, _ = p1.initial(restarted, item, 'R', 'weak', 256)
    restarted.close()
    assert row['ok'] and row['served_provider'] == 'Groq'
    assert phases == ['initial', 'replay']


def test_scored_survives_dev_infrastructure_panel_and_is_resumable(split_env, monkeypatch):
    from copy import deepcopy
    path, items = split_env
    labels = {i['id']: i['label'] for i in items}
    def materials(split):
        result = deepcopy(items)
        for i in result:
            i['split'] = split
        return result
    monkeypatch.setattr(p1, 'materials', materials)
    calls = []
    def respond(r):
        calls.append(r)
        if r.model == 'weak':
            raise paid.InfrastructureError('unauthorized', 401)
        good = labels[r.metadata['item_id']] == 'good'
        # W has errors on bad items, with intact good approval and contract.
        verdict = 'approve' if good or r.metadata['arm'] == 'W' else 'reject'
        return json.dumps({'verdict': verdict})
    monkeypatch.setattr(p1, 'OpenRouterBackend', lambda *a: paid.OfflineBackend(respond))
    monkeypatch.setattr(p1, 'VertexBackend', lambda: paid.OfflineBackend(respond))
    assert p1.run_split('dev', 2) == 2
    p1.write_json(path / 'freeze.json', {'hashes': {}, 'manifest_sha256': 'test', 'external_timestamp': {'verified': True}})
    assert p1.run_split('scored', 2) == 0
    count = len(calls)
    assert p1.run_split('scored', 2) == 0 and len(calls) == count
    assert not any(r.model == 'weak' and r.metadata['split'] == 'scored' for r in calls)
    report = json.loads((path / 'runs/scored/analysis.json').read_text())
    assert report['dev_ineligible_judges'] == ['weak']
    assert {'pro/E4', 'replication/E4'} == report['families'].keys()
    dev = json.loads((path / 'checks/dev.json').read_text())
    dev['stopped'] = 'study-wide validation failure'
    p1.write_json(path / 'checks/dev.json', dev)
    with pytest.raises(paid.PreflightError, match='study-wide'):
        p1.run_split('scored', 2)
    assert len(calls) == count


def test_provider_billing_validation_halts_only_that_judge(tmp_path):
    ledger = paid.Ledger(tmp_path / 'ledger', 1)
    ledger.reserve_block('dev', '.1')
    def respond(r):
        return paid.PaidReply('Hi', 1, 1, 0, 0, 'rev', {'provider': 'Groq'}, {}, provider_cost_usd=.000001)
    client = paid.PaidClient(paid.OfflineBackend(respond), ledger, 'dev', reuse_completed=True)
    with pytest.raises(paid.InfrastructureError, match='billing exceeds'):
        client.call(req())
    with pytest.raises(paid.InfrastructureError, match='billing exceeds'):
        client.call(req(arm='V'))
    # Actual provider billing remains accounted even when it exceeds the table.
    assert ledger.state(entries(ledger))[1] == Decimal('.000001055')
    client.close()
    other = paid.PaidClient(paid.OfflineBackend(lambda _: '{"verdict":"approve"}'), ledger, 'dev', reuse_completed=True)
    other.call(req('pro'))
    other.close()
    assert p1.infrastructure_state(ledger)[1].keys() == {'weak'}
    assert not ledger.state(entries(ledger))[-1]


def test_actual_dev_prefix_reconstructs_without_duplicate_trials(tmp_path, monkeypatch):
    original = p1.HERE
    source = original / 'runs/study/costs.jsonl'
    if not source.exists():
        pytest.skip('local dev evidence absent in clean checkout')
    items = p1.materials('dev')
    plan = p1.inventory()
    shutil.copytree(original / 'prompts', tmp_path / 'prompts')
    for relative in ('runs/study/costs.jsonl', 'runs/dev/trials.jsonl', 'results/probe.json'):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original / relative, target)
    retained = (tmp_path / 'runs/dev/trials.jsonl').read_bytes()
    monkeypatch.setattr(p1, 'HERE', tmp_path)
    monkeypatch.setattr(p1, 'inventory', lambda: plan)
    monkeypatch.setattr(p1, 'materials', lambda _: items)
    # The real original split ceiling is retained in the ledger.
    ledger_rows = [json.loads(line) for line in source.read_text().splitlines()]
    ceiling = Decimal(next(r['ceiling_usd'] for r in ledger_rows if r['event'] == 'block_reserve'))
    monkeypatch.setattr(p1, 'split_ceiling', lambda *a: ceiling)
    monkeypatch.setattr(p1_preflight, 'runtime_counter', lambda: None)
    class CacheOnly(paid.OfflineBackend):
        def __init__(self):
            super().__init__(lambda _: pytest.fail('no dispatch'))
        def count(self, request):
            # pushback counts its joint history before replaying cached turns.
            if request.metadata['role'] == 'attacker':
                return 0
            raise paid.BudgetExceeded('offline stop at first uncompleted assignment')
    monkeypatch.setattr(p1, 'VertexBackend', CacheOnly)
    monkeypatch.setattr(p1, 'OpenRouterBackend', lambda *a: CacheOnly())
    p1.write_json(tmp_path / 'freeze.json', {'hashes': {}, 'manifest_sha256': 'test'})
    for gate in (*p1_preflight.GATES, 'provider-preflight'):
        p1.write_json(tmp_path / f'checks/{gate}.json', {'passed': True, 'freeze_sha256': 'test'})
    assert p1.run_split('dev', 36) == 3
    assert (tmp_path / 'runs/dev/trials.jsonl').read_bytes() == retained
    ledger = paid.Ledger(tmp_path / 'runs/study/costs.jsonl', 36)
    assert sum(r['event'] == 'complete' for r in entries(ledger)) == 19
    assert entries(ledger)[-1]['event'] == 'routing_recovery'
    report = json.loads((tmp_path / 'checks/dev.json').read_text())
    assert len(report['gates']) == 6 and not report['passed']
