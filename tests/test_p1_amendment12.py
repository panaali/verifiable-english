"""Ceiling-driven judge substitution: budgets, routing, reuse and disclosure."""
from decimal import Decimal
from dataclasses import replace
import json
import shutil

import pytest

from experiments import p1, p1_preflight
from ve_experiments import paid


def test_strict_scenarios_retained_costs_and_priority():
    expected = ['32.27620399850', '60.71913199850', '45.61666391850']
    for name, total in zip(p1.P1_AMENDMENT12_SCENARIOS, expected, strict=True):
        plan = p1.inventory()['budget_scenarios'][name]
        # Independent inventory call count, including every replay and retry.
        calls = sum((paid.cost(r['model'], r['max_input_per_call'],
                              r['max_billed_output_per_call'], arm=r['arm']) * r['calls']
                     for r in plan['budget_rows']), Decimal(0))
        assert calls + Decimal('2.41723326890') == Decimal(total)
        assert p1.cumulative_ceiling(name) == p1.cumulative_ceiling(name, worst_case=True) == Decimal(total)
    assert p1.amendment12_selection() == 'replication_3turn'
    assert p1.split_ceiling('replication_3turn', 'dev') == Decimal('4.3130218464')


def test_selection_fails_closed_and_keeps_priority(monkeypatch):
    names = list(p1.P1_AMENDMENT12_SCENARIOS)
    ceilings = dict(zip(names, (41, 40, 39)))
    monkeypatch.setattr(p1, 'cumulative_ceiling', lambda n, **kw: ceilings[n])
    assert p1.amendment12_selection() == names[1]
    ceilings[names[0]] = 40
    assert p1.amendment12_selection() == names[0]
    ceilings.update(dict.fromkeys(names, 41))
    assert p1.amendment12_selection() == 'stop'


def test_qwen_pushback_uses_gemini_attacker_and_separate_analysis(tmp_path):
    item = next(i for i in p1.materials('dev') if i['assignment']['pushback'])
    requests = []
    verdict = 'approve' if item['label'] == 'good' else 'reject'
    def respond(req):
        requests.append(req)
        return 'Please reconsider.' if req.metadata['role'] == 'attacker' else json.dumps({'verdict': verdict})
    ledger = paid.Ledger(tmp_path / 'costs', 40)
    client = paid.PaidClient(paid.OfflineBackend(respond), ledger, reuse_completed=True)
    def run(judge):
        initial, messages = p1.initial(client, item, 'A', judge, 1024)
        return [initial, *p1.pushback(client, item, 'A', messages, judge=judge, attacker_client=client)]
    try:
        rows = run('replication') + run('pro')
        before = len(requests)
        run('replication')
        assert len(requests) == before
    finally:
        client.close()
    for req in requests:
        role = req.metadata['role']
        if role == 'attacker':
            assert req.model == 'pro' and req.max_output_tokens == 1024
        elif '/replication/' in req.identity:
            assert req.model == 'replication' and req.max_output_tokens == 1024
    assert len({r.identity for r in requests}) == len(requests)
    result = p1.analyze_pushback(rows, [item])
    for judge in ('replication', 'pro'):
        assert result[f"{judge}/{item['assignment']['source']}/A"]['turn_error_counts'] == [0, 0, 0, 0]


def test_qwen_native_replay_is_preserved_for_gemini_attacker():
    req = next(r for r, _ in p1_preflight.token_requests('pro')
               if r.metadata.get('target_judge') == 'replication' and r.metadata['arm'] == 'R')
    backend = object.__new__(paid.VertexBackend)  # wire conversion needs no credentials/network
    contents, _ = backend.wire(req)
    calls = [part.function_call for c in contents for part in c.parts if part.function_call]
    responses = [part.function_response for c in contents for part in c.parts if part.function_response]
    assert len(calls) == len(responses) == 1
    assert calls[0].id == responses[0].id == 'preflight-replay'


@pytest.mark.parametrize('schedule', ['replication_3turn', 'replication_gemini_e5_2turn'])
def test_selected_dev_rebuys_changed_qwen_requests_and_blocks_scoring(tmp_path, monkeypatch, schedule):
    original = p1.HERE
    source_items = p1.materials('dev')
    items = [i for i in source_items if i['assignment']['pushback']]
    plan = p1.inventory()
    receipt = json.loads((original / 'checks/amendment12.json').read_text())
    shutil.copytree(original / 'prompts', tmp_path / 'prompts')
    shutil.copytree(original / 'runs/study', tmp_path / 'runs/study')
    ledger_path = tmp_path / 'runs/study/costs.jsonl'
    # This regression exercises the historical pre-Amendment-12 dev state.
    ledger_path.write_bytes(b''.join(ledger_path.read_bytes().splitlines(keepends=True)[:receipt['ledger_prefix_lines']]))
    assert p1.sha(ledger_path) == receipt['ledger_prefix_sha256']
    prefix = ledger_path.read_bytes()
    monkeypatch.setattr(p1, 'HERE', tmp_path)
    monkeypatch.setattr(p1, 'inventory', lambda: plan)
    monkeypatch.setattr(p1, 'materials', lambda _: items)
    monkeypatch.setattr(p1_preflight, 'runtime_counter', lambda: None)
    p1.write_json(tmp_path / 'checks/amendment12.json', receipt)
    p1.write_json(tmp_path / 'results/probe.json', {'status': 'complete', 'schedule': schedule})
    p1.write_json(tmp_path / 'freeze.json', {'hashes': {}, 'manifest_sha256': 'test', 'external_timestamp': {'verified': True}})
    for gate in (*p1_preflight.GATES, 'provider-preflight'):
        p1.write_json(tmp_path / f'checks/{gate}.json', {'passed': True, 'freeze_sha256': 'test'})
    calls = []
    labels = {i['id']: i['label'] for i in items}
    revisions = {r['model']: r['revision'] for r in p1.read_jsonl(tmp_path / 'runs/study/costs.jsonl') if r['event'] == 'complete'}
    def respond(req):
        calls.append(req)
        text = ('Please reconsider.' if req.metadata['role'] == 'attacker' else
                json.dumps({'verdict': 'approve' if labels[req.metadata['item_id']] == 'good' else 'reject'}))
        return paid.PaidReply(text, 1, 10, 0, 0, revisions[req.model], {},
                              {'role': 'assistant', 'content': text})
    monkeypatch.setattr(p1, 'OpenRouterBackend', lambda *a: paid.OfflineBackend(respond))
    monkeypatch.setattr(p1, 'VertexBackend', lambda: paid.OfflineBackend(respond))
    # Durable old Gemini fallback must not switch back to buying Gemini/E4.
    assert p1.run_split('dev', 6.85298379880) == 0
    assert all(r.model == 'replication' or schedule == 'replication_gemini_e5_2turn' and r.metadata['panel'] == 'E5'
               for r in calls if r.metadata['role'] != 'attacker')
    if schedule == 'replication_gemini_e5_2turn':
        assert any(r.model == 'pro' and r.metadata['role'] == 'initial' for r in calls)
    assert any('/amendment8/' in r.identity for r in calls if r.metadata['role'] == 'initial')
    assert (tmp_path / 'runs/study/costs.jsonl').read_bytes().startswith(prefix)
    before = len(calls)
    assert p1.run_split('dev', 6.85298379880) == 0
    assert len(calls) == before
    report = json.loads((tmp_path / 'runs/dev/analysis.json').read_text())
    assert set(report['families']) == {'replication/E4', 'replication/E5'} | (
        {'pro/E5'} if schedule == 'replication_gemini_e5_2turn' else set())
    assert report['gemini_e4_dev_ceiling']['judgments'] == 112
    assert all('exploratory-primary' in f['contrast_status'] for k, f in report['families'].items() if k.startswith('replication/'))
    with pytest.raises(paid.PreflightError, match='dev capability gate failed'):
        p1.run_split('scored', 24.28476399850)
    assert len(calls) == before


def test_e5_only_gemini_gate_has_no_phantom_e4_family():
    plan = p1.inventory()['budget_scenarios']['replication_gemini_e5_2turn']
    gates = p1.dev_gates([], p1.materials('dev'), plan['judges'], plan=plan)
    assert set(gates['gates']) == {'replication/E4', 'replication/E5', 'pro/E5'}
    assert not gates['passed']
