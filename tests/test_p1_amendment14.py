"""Attacker accounting recovery, exact scored reuse, and partial initial analysis."""
from contextlib import contextmanager
from copy import deepcopy
from decimal import Decimal
import json

import pytest

from experiments import p1
from ve_experiments import paid


@pytest.mark.parametrize('billed,passes', [(304, True), (1024, True), (1025, False)])
def test_visible_wire_and_billed_reserve_are_separate(tmp_path, billed, passes):
    req = p1.request(p1.materials('scored')[0], 'A', 'pro', 256, phase='attacker')
    assert req.max_output_tokens == 1024 and req.billed_output_cap == 1024
    _, wire = paid.VertexBackend.__new__(paid.VertexBackend).wire(req)
    assert wire.max_output_tokens == 1024
    reply = paid.PaidReply('hello', 1, 4, billed-4, 0, 'offline', {},
                           {'role': 'assistant', 'content': 'hello'}, finish_reason='STOP')
    ledger = paid.Ledger(tmp_path/'costs.jsonl', 40)
    client = paid.PaidClient(paid.OfflineBackend(lambda _: reply), ledger, reuse_completed=True)
    try:
        if passes:
            assert client.call(req).billed_output_tokens == billed
            assert client.call(req).billed_output_tokens == billed
        else:
            with pytest.raises(paid.InfrastructureError, match='token cap'):
                client.call(req)
    finally:
        client.close()
    rows = p1.read_jsonl(ledger.path)
    reserve = next(r for r in rows if r['event'] == 'reserve')
    assert Decimal(reserve['ceiling_usd']) == paid.cost('pro', req.max_input_tokens, 1024)
    assert sum(r['event'] == 'complete' for r in rows) == 1


def test_recover_and_reconstruct_every_retained_scored_call_without_dispatch(tmp_path, monkeypatch):
    # Replay the retained Amendment 14 population, before Amendment 15 added
    # restart calls, costs, and replacement trajectory rows to the final files.
    receipt = p1.amendment15_receipt()
    p1.validate_amendment15_sources(receipt)
    def retained_bytes(relative):
        return (p1.HERE / relative).read_bytes()[:receipt['sources'][relative]['bytes']]
    ledger = paid.Ledger(tmp_path/'costs.jsonl', Decimal('19.90026000260'))
    ledger.path.write_bytes(retained_bytes('runs/study/costs.jsonl'))
    before = ledger.path.read_bytes()
    block = p1.split_block_id('replication_2turn', 'scored')
    ceiling = p1.split_ceiling('replication_2turn', 'scored')
    ledger.amend_attacker_billing(block, ceiling)
    after = ledger.path.read_bytes()
    assert after.startswith(before)
    assert ledger.amend_attacker_billing(block, ceiling) == []
    entries = p1.read_jsonl(ledger.path)
    pending, spent, *_ = ledger.state(entries)
    assert not pending and spent == Decimal(receipt['retained_costs_and_holds_usd'])
    ledger.reserve_block(block, ceiling, resume=True)
    class MissingCache(Exception):
        pass
    def forbidden(*args):
        raise MissingCache
    # Exercise the real cache matcher over retained receipts, without disk
    # parsing for every call or any ability to reserve/dispatch a new request.
    @contextmanager
    def locked():
        yield None, entries
    monkeypatch.setattr(ledger, 'locked', locked)
    backend = paid.OfflineBackend(forbidden)
    monkeypatch.setattr(backend, 'count', lambda req: 0 if req.metadata.get('role') == 'attacker' and req.metadata.get('turn') == 0 else forbidden())
    reused = set()
    cached_reply = ledger.cached_reply
    def tracked_cache(req):
        reply = cached_reply(req)
        if reply is not None:
            reused.add(req.identity)
        return reply
    monkeypatch.setattr(ledger, 'cached_reply', tracked_cache)
    client = paid.PaidClient(backend, ledger, block, reuse_completed=True)
    source = [json.loads(line) for line in retained_bytes('runs/scored/trials.jsonl').splitlines()]
    def key(r):
        return r['item_id'], r['condition'], r['judge'], r.get('turn', 0), r.get('event')
    retained = {key(r): r for r in source}
    reconstructed = {}
    try:
        for item in p1.materials('scored'):
            for arm in p1.arms(item):
                try:
                    row, messages = p1.initial(client, item, arm, 'replication', 1024)
                    reconstructed[key(row)] = row
                    if item['assignment']['pushback'] and arm in p1.MAIN:
                        for row in p1.pushback(client, item, arm, messages, max_turns=2,
                                               judge='replication', attacker_client=client, amendment=14):
                            reconstructed[key(row)] = row
                except MissingCache:
                    pass
    finally:
        client.close()
    assert len([r for r in source if not r.get('turn') and not r.get('event')]) == 1128
    assert all(reconstructed[k] == row for k, row in retained.items())
    assert reused == {r['identity'] for r in entries if r['event'] == 'complete' and r['identity'].startswith('scored/')}
    # The over-cap attacker is now reusable, with original wire and receipt.
    halt = next(r for r in entries if r['event'] == 'amendment14_halt_recovery')
    original = next(r for r in entries if r['event'] == 'reserve' and r['identity'] == halt['identity'])
    request = paid.PaidRequest(**{k: original[k] for k in paid.PaidRequest.__dataclass_fields__})
    assert ledger.cached_reply(request).billed_output_tokens == 304
    assert ledger.path.read_bytes() == after


def test_partial_initial_estimates_and_complete_panel_survive_pushback_halt():
    items = p1.materials('dev')
    rows = [r for r in p1.read_jsonl(p1.HERE/'runs/dev/trials.jsonl')
            if r.get('amendment') == 8 and r['judge'] == 'replication' and not r.get('turn') and not r.get('event')]
    plan = p1.inventory()['budget_scenarios']['replication_2turn']
    report = p1.split_report(rows, items, ['replication'], {}, {'replication': 'later pushback halt'}, plan=plan)
    assert report['initial_stage_status'] == 'complete'
    assert report['pushback_status'] == 'pushback incomplete'
    assert set(report['families']) == {'replication/E4', 'replication/E5'}
    full = report['families']['replication/E4']
    e4 = [i for i in items if i['assignment']['source'] == 'E4']
    e4_rows = [r for r in rows if r['item_id'].startswith('e4-')]
    partial = p1.partial_initial_family(e4_rows, e4, 'replication')
    for name, contrast in full['contrasts'].items():
        assert partial['contrasts'][name]['nominal'] == contrast['nominal']
    absent = next(r for r in rows if r['condition'] == 'A' and r['item_id'].startswith('e4-'))
    report = p1.split_report([r for r in rows if r != absent], items, ['replication'], {}, {}, plan=plan)
    assert report['initial_stage_status'] == 'incomplete'
    family = report['families']['replication/E4']
    assert family['rates']['A']['missing'] == 1
    assert family['rates']['A']['failures'] == full['rates']['A']['failures']
    assert family['contrasts']['A-F_correct:accuracy']['paired_items'] == len(e4)-1
    assert family['wilson_rates']['A']['accuracy']['n'] == len(e4)-1
    with pytest.raises(ValueError, match='duplicate'):
        p1.partial_initial_family([*e4_rows, e4_rows[0]], e4, 'replication')


def test_recovery_never_forgives_input_or_billed_overrun(tmp_path):
    original = p1.read_jsonl(p1.HERE/'runs/study/costs.jsonl')
    # Reconstruct the historical halt prefix; later calls depend on the recovery.
    original = original[:next(n for n, r in enumerate(original) if r['event'].startswith('amendment14'))]
    halt = next(r for r in reversed(original) if r['event'] == 'panel_validation_halt')
    for field, value in [('billed_output_tokens', 1025), ('input_tokens', 99999)]:
        rows = deepcopy(original)
        completion = next(r for r in rows if r['event'] == 'complete' and r['identity'] == halt['identity'])
        completion[field] = value
        ledger = paid.Ledger(tmp_path/f'{field}.jsonl', 40)
        ledger.path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
        events = ledger.amend_attacker_billing(p1.split_block_id('replication_2turn', 'scored'),
                                              p1.split_ceiling('replication_2turn', 'scored'))
        assert not any(r['event'] == 'amendment14_halt_recovery' for r in events)
        assert 'pro' in p1.infrastructure_state(ledger)[1]
