"""Audited abstentions, gate scope, zero-generation reuse and strict bounds."""
from copy import deepcopy
from decimal import Decimal
import json
import shutil

import pytest

from experiments import p1, p1_preflight
from ve_experiments import paid


def current_rows():
    return [r for r in p1.read_jsonl(p1.HERE / 'runs/dev/trials.jsonl') if r.get('amendment') == 8]


def test_gate_scope_and_narrow_contract_exception():
    plan = p1.inventory()['budget_scenarios']['replication_2turn']
    rows, items = current_rows(), p1.materials('dev')
    gate = p1.dev_gates(rows, items, ['replication'], plan=plan)
    assert gate['passed']
    e4 = gate['gates']['replication/E4']
    assert e4['good_approval'] and not e4['contract'] and e4['contract_accepted']
    assert e4['numbers']['R']['failures'] == 4
    assert e4['numbers']['F']['good_approval_rate'] == e4['numbers']['U']['good_approval_rate'] == 0
    assert e4['good_approval_excluded_by_design'] == ['F', 'U']
    # A baseline collapse, an extra R failure, or different failure type must block.
    for arm, error in [('A', 'unknown'), ('R', 'unknown'), ('R', 'parse_failure')]:
        changed = deepcopy(rows)
        for r in changed:
            if r['judge'] == 'replication' and r['condition'] == arm and r['item_id'].startswith('e4-') and not r.get('event') and not r.get('turn'):
                if error == 'parse_failure' or r.get('ok'):
                    r.update(ok=False, error=error, approved=None, verdict='unknown', response='{"verdict":"unknown"}')
                    if arm == 'R':
                        break
        assert not p1.dev_gates(changed, items, ['replication'], plan=plan)['passed']
    assert not p1.dev_gates(rows, items, ['replication'], halted={'replication': 'provider failure'}, plan=plan)['passed']


def test_audited_raw_replies_and_ceiling_disclosures():
    receipt = json.loads((p1.HERE / 'checks/amendment13.json').read_text())
    ledger = p1.read_jsonl(p1.HERE / 'runs/study/costs.jsonl')
    for case in receipt['r_contract_diagnosis']['cases']:
        raw = next(r for r in ledger if r['event'] == 'complete' and r['identity'] == case['identity'])
        assert raw['response']['choices'][0]['message']['content'] == case['text'] == '{"verdict":"unknown"}'
        assert case['finish_reason'] == case['native_finish_reason'] == 'stop'
        assert raw['tool_calls'] == case['tool_calls'] == []
        assert p1.parse(raw['text']) == ('unknown', 'unknown')
    for panel, n in [('E4', 112), ('E5', 96)]:
        ceiling = receipt['gemini_dev_ceilings'][panel]
        assert ceiling['judgments'] == n and ceiling['errors'] == 0
        assert ceiling['wilson_95_interval'] == pytest.approx(p1.rate_interval([0]*n, single_binary=True)['interval'])
        assert ceiling['harm_contrasts'] == 'no harm observable at ceiling'


def test_schedule_and_strict_ceiling():
    name = 'replication_2turn'
    plan = p1.inventory()['budget_scenarios'][name]
    assert plan['judges'] == ['replication'] and plan['sources'] == ['E4', 'E5']
    assert plan['pushback_turns'] == 2
    assert p1.split_ceiling(name, 'scored') == p1.split_ceiling(name, 'scored', worst_case=True) == Decimal('17.9592162432')
    assert p1.remaining_dev_ceiling(name) == 0
    assert p1.cumulative_ceiling(name, worst_case=True) == Decimal('20.15026000260')
    pending, committed, *_ = paid.Ledger.state(p1.read_jsonl(p1.HERE / 'runs/study/costs.jsonl'))
    # Scored receipts now exist; compare retained pre-scored overhead only.
    assert p1.budget_overhead(name) + p1.split_ceiling(name, 'scored') == Decimal('19.90026000260')
    assert sum(r['calls'] for r in plan['budget_rows'] if r['role'] == 'initial_judge') == 1336
    for item in p1.materials('scored'):
        assert not p1.scheduled(plan, 'pro', item)
        assert not p1.pushback_scheduled(plan, 'replication', item, 'U')


def test_refresh_dev_is_read_only_and_missing_cache_fails_closed(tmp_path, monkeypatch, capsys):
    source, plan, items = p1.HERE, p1.inventory(), p1.materials('dev')
    for name in ('checks', 'results', 'runs', 'prompts'):
        shutil.copytree(source / name, tmp_path / name)
    p1.write_json(tmp_path / 'freeze.json', {'hashes': {}, 'manifest_sha256': 'test'})
    monkeypatch.setattr(p1, 'HERE', tmp_path)
    monkeypatch.setattr(p1, 'inventory', lambda: plan)
    monkeypatch.setattr(p1, 'materials', lambda _: items)
    monkeypatch.setattr(p1_preflight, 'refresh_status', lambda: [])
    def forbidden(*args, **kwargs):
        pytest.fail('refresh-dev must never construct a provider or reserve a request')
    monkeypatch.setattr(p1, 'VertexBackend', forbidden)
    monkeypatch.setattr(p1, 'OpenRouterBackend', forbidden)
    monkeypatch.setattr(paid.Ledger, 'reserve', forbidden)
    paths = [tmp_path / 'runs/study/costs.jsonl', tmp_path / 'runs/dev/trials.jsonl']
    before = [x.read_bytes() for x in paths]
    assert p1.refresh_dev() == 0
    gate = json.loads((tmp_path / 'checks/dev.json').read_text())
    assert gate['passed'] and gate['generation_calls'] == 0
    assert len(gate['validated_requests']) == 208
    assert [x.read_bytes() for x in paths] == before
    report = json.loads((tmp_path / 'runs/dev/analysis.json').read_text())
    assert set(report['families']) == {'replication/E4', 'replication/E5'}
    assert set(report['gemini_dev_ceilings']) == {'E4', 'E5'}
    monkeypatch.setattr(paid.Ledger, 'cached_reply', lambda *args: None)
    with pytest.raises(paid.PreflightError, match='missing identical completed'):
        p1.refresh_dev()
    assert [x.read_bytes() for x in paths] == before


def test_scored_gate_and_cap_reach_only_qwen_attacker_backends(tmp_path, monkeypatch):
    source, plan = p1.HERE, p1.inventory()
    for name in ('checks', 'results', 'runs'):
        shutil.copytree(source / name, tmp_path / name)
    # This test exercises the historical Amendment 13/14 block. Amendment 15
    # has a separate fixed restart population and envelope, covered separately.
    (tmp_path / 'checks/amendment15.json').unlink(missing_ok=True)
    monkeypatch.setattr(p1, 'HERE', tmp_path)
    monkeypatch.setattr(p1, 'inventory', lambda: plan)
    p1.write_json(tmp_path / 'freeze.json', {'hashes': {}, 'manifest_sha256': 'test',
                                          'external_timestamp': {'verified': True}})
    for gate in (*p1_preflight.GATES, 'provider-preflight'):
        p1.write_json(tmp_path / f'checks/{gate}.json', {'passed': True, 'freeze_sha256': 'test'})
    dev = {'passed': True, 'schedule': 'replication_2turn', 'freeze_sha256': 'stale',
           'judges': {'replication': {'passed': True}}}
    p1.write_json(tmp_path / 'checks/dev.json', dev)
    with pytest.raises(paid.PreflightError, match='earlier execution freeze'):
        p1.run_split('scored', Decimal('19.90026000260'))
    dev['freeze_sha256'] = 'test'
    p1.write_json(tmp_path / 'checks/dev.json', dev)
    class DispatchBoundary(Exception):
        pass
    def boundary(*args):
        raise DispatchBoundary
    monkeypatch.setattr(p1, 'VertexBackend', boundary)
    monkeypatch.setattr(p1, 'OpenRouterBackend', boundary)
    monkeypatch.setattr(p1_preflight, 'runtime_counter', lambda: None)
    # Exact quoted cap must admit the full block before constructing providers.
    with pytest.raises(DispatchBoundary):
        p1.run_split('scored', Decimal('19.90026000260'))
    entries = p1.read_jsonl(tmp_path / 'runs/study/costs.jsonl')
    block = next(r for r in reversed(entries) if r['event'] in ('block_reserve', 'amendment14_block'))
    assert block['block_id'] == 'scored-amendment13-replication_2turn'
    assert Decimal(block['ceiling_usd']) == Decimal('17.9592162432')
