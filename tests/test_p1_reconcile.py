"""Append-only budget reconciliation and request reuse across schedule changes."""
from dataclasses import replace
from decimal import Decimal
import json
import shutil

import pytest

from experiments import p1
from ve_experiments import paid


def historical_ledger(path):
    receipt = json.loads((p1.HERE / 'checks/amendment12.json').read_text())
    data = (p1.HERE / 'runs/study/costs.jsonl').read_bytes()
    path.write_bytes(b''.join(data.splitlines(keepends=True)[:receipt['ledger_prefix_lines']]))
    assert p1.sha(path) == receipt['ledger_prefix_sha256']


def rows(ledger):
    return p1.read_jsonl(ledger.path)


def test_releases_are_idempotent_and_keep_receipts_and_active_holds(tmp_path):
    ledger = paid.Ledger(tmp_path / 'ledger', 40)
    ledger.allowance('old', 1)
    ledger.reserve_block('old-dev', 10, schedule='full_256', split='dev')
    req = paid.PaidRequest('dev/x', 'pro', [], 100, 100, metadata={'block_id': 'old-dev'})
    ledger.reserve(req)
    ledger.complete(req, paid.PaidReply('saved', 10, 20, 0, 0, 'rev', {}, {}))
    original = ledger.path.read_bytes()
    releases = {'old-dev': 'schedule superseded'}
    allowances = {'old': {'cost_usd': '.1', 'reason': 'completed envelope; keep realised cost'}}
    events = ledger.reconcile(releases, allowances)
    assert ledger.path.read_bytes().startswith(original)
    assert len(events) == 2 and all(e['reason'] for e in events)
    assert paid.Ledger.state(rows(ledger))[1] == Decimal('.1') + paid.cost('pro', 10, 20)
    assert ledger.cached_reply(req).text == 'saved'
    assert ledger.reconcile(releases, allowances) == []
    ledger.reserve_block('active', 2, schedule='selected', split='dev')
    ledger.reconcile(releases, allowances)
    assert paid.Ledger.state(rows(ledger))[0] == {'block:active': Decimal(2)}
    with pytest.raises(paid.BudgetExceeded):
        paid.Ledger(ledger.path, 1).reserve_block('active', 2, resume=True)


def test_unknown_billing_cannot_be_released(tmp_path):
    ledger = paid.Ledger(tmp_path / 'ledger', 40)
    ledger.reserve_block('old', 1)
    ledger.reserve(paid.PaidRequest('dev/x', 'pro', [], 100, 100, metadata={'block_id': 'old'}))
    before = ledger.path.read_bytes()
    with pytest.raises(paid.PreflightError, match='billing unresolved'):
        ledger.reconcile({'old': 'superseded'}, {})
    assert ledger.path.read_bytes() == before


def test_completed_amended_calls_reused_across_block_ids(tmp_path):
    ledger = paid.Ledger(tmp_path / 'ledger', 40)
    req = paid.PaidRequest('dev/x/pro/initial/0', 'pro', [], 100, 256, metadata={'split': 'dev'})
    ledger.reserve(req)
    ledger.complete(req, paid.PaidReply('old', 0, 0, 0, 0, 'offline', {}, {}))
    ledger.amend_dev(1)
    req = replace(req, max_output_tokens=1024, response_schema=paid.VERDICT_SCHEMA)
    # Emulate an existing amended identity whose digest included the old block.
    old = replace(req, metadata={'split': 'dev', 'block_id': 'old'})
    old = replace(old, identity=req.identity + '/amendment8/' + paid.digest(paid.asdict(old)))
    ledger.reserve_block('old', 1)
    ledger.reserve(old)
    ledger.complete(old, paid.PaidReply('amended', 1, 1, 0, 0, 'offline', {}, {}))
    ledger.release_block('old')
    ledger.reserve_block('new', 1)
    before = ledger.path.read_bytes()
    client = paid.PaidClient(paid.OfflineBackend(lambda _: pytest.fail('unchanged completed request dispatched')),
                             ledger, 'new', reuse_completed=True)
    try:
        assert client.call(req).text == 'amended'
    finally:
        client.close()
    assert ledger.path.read_bytes() == before


def test_real_reconciliation_preserves_every_call_and_quotes_exact_caps(tmp_path, monkeypatch, capsys):
    source = p1.HERE
    shutil.copytree(source / 'runs', tmp_path / 'runs')
    shutil.copytree(source / 'results', tmp_path / 'results')
    historical_ledger(tmp_path / 'runs/study/costs.jsonl')
    p1.write_json(tmp_path / 'results/probe.json', {'status': 'complete', 'schedule': 'replication_3turn'})
    inventory = p1.inventory()
    ceilings = {s: p1.split_ceiling('replication_3turn', s, worst_case=True) for s in ('dev', 'scored')}
    monkeypatch.setattr(p1, 'HERE', tmp_path)
    monkeypatch.setattr(p1, 'inventory', lambda: inventory)
    monkeypatch.setattr(p1, 'split_ceiling', lambda name, split, **kwargs: ceilings[split])
    ledger = paid.Ledger(tmp_path / 'runs/study/costs.jsonl', 40)
    # Model an interrupted legacy reservation absent from the current checkout.
    ledger.reserve_block('obsolete', 20, schedule='full_256', split='dev')
    with ledger.locked() as (f, _):
        ledger.append(f, {'event': 'block_reserve', 'block_id': 'completed', 'ceiling_usd': '1',
                          'schedule': 'replication_3turn'})
        ledger.append(f, {'event': 'block_complete', 'block_id': 'completed'})
    original = ledger.path.read_bytes()
    completions = [r for r in rows(ledger) if r['event'] == 'complete']
    assert p1.reconcile() == 0
    capsys.readouterr()
    report = json.loads((tmp_path / 'checks/reconciliation.json').read_text())
    assert ledger.path.read_bytes().startswith(original)
    assert [r for r in rows(ledger) if r['event'] == 'complete'] == completions
    assert Decimal(report['study_realised_usd']) == Decimal('.60778371370')
    assert Decimal(report['realised_usd']) == Decimal('.64413983720')
    assert Decimal(report['live_holds_usd']) == Decimal('.30784555520')
    assert Decimal(report['remaining_usd']) == Decimal('39.04801460760')
    pending, spent, *_ = ledger.state(rows(ledger))
    assert not pending
    assert Decimal(report['cap_usd']['dev']) == spent + ceilings['dev']
    assert Decimal(report['cap_usd']['scored']) == spent + sum(ceilings.values())
    ledger.require_block(ceilings['dev'])
    before = ledger.path.read_bytes()
    assert p1.reconcile() == 0
    assert ledger.path.read_bytes() == before
    assert json.loads((tmp_path / 'checks/reconciliation.json').read_text()) == report


def test_all_real_gemini_e4_calls_reused_and_old_qwen_calls_stale(tmp_path):
    ledger = paid.Ledger(tmp_path / 'ledger', 40)
    historical_ledger(ledger.path)
    items = [i for i in p1.materials('dev') if i['assignment']['source'] == 'E4']
    def fail(_):
        pytest.fail('completed Gemini E4 call must not be dispatched')
    client = paid.PaidClient(paid.OfflineBackend(fail), ledger, 'selected-new-block', reuse_completed=True)
    before = ledger.path.read_bytes()
    try:
        for item in items:
            for arm in p1.arms(item):
                row, _ = p1.initial(client, item, arm, 'pro', 1024)
                assert row['ok']
                req = p1.request(item, arm, 'replication', 1024)
                assert ledger.cached_reply(ledger.amended_dev_request(req)) is None
    finally:
        client.close()
    assert ledger.path.read_bytes() == before
    assert len(items) * len(p1.ARMS) == 112
