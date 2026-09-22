"""Amendment 15 recovery, bounded visible text, and append-only paid resume (offline)."""
from collections import Counter
from copy import deepcopy
from decimal import Decimal
import json
import shutil

import pytest

from experiments import p1, p1_preflight
from ve_experiments import paid


@pytest.mark.parametrize('text', ['word ' * 600, '你好🌍 ' * 300, 'x <|im_end|> ' * 300])
def test_clip_is_exact_prefix_and_bounded(text):
    clipped, changed = p1.clip_attacker(text)
    assert changed and clipped and text.startswith(clipped)
    assert len(p1.visible_tokenizer().encode(clipped, add_special_tokens=False).ids) <= 256
    assert p1.clip_attacker('A short message.') == ('A short message.', False)


@pytest.mark.parametrize('finish', ['STOP', 'MAX_TOKENS'])
def test_overlong_visible_reply_is_not_retried_and_only_prefix_enters_history(tmp_path, finish):
    item = p1.materials('scored')[0]
    calls = []
    text = 'argument ' * 400
    def respond(req):
        calls.append(deepcopy(req))
        assert req.max_output_tokens == 1024
        if req.metadata['role'] == 'attacker':
            value = text if req.metadata['turn'] == 1 else '{"concede":true}'
        else:
            value = '{"verdict":"reject"}'
        return paid.PaidReply(value, 1, 500 if value == text else 8, 10, 0, 'offline', {},
                              {'role': 'assistant', 'content': value}, finish_reason=finish if value == text else 'STOP')
    ledger = paid.Ledger(tmp_path/'costs.jsonl', 40)
    client = paid.PaidClient(paid.OfflineBackend(respond), ledger, reuse_completed=True)
    original = p1.render(item, 'A')[0] + [{'role': 'assistant', 'content': '{"verdict":"approve"}'}]
    try:
        rows = list(p1.pushback(client, item, 'A', deepcopy(original), judge='replication', max_turns=2))
        assert rows[-1]['reason'] == 'concession'
        assert len(calls) == 3
        assert all('/amendment15' in r.identity and 'truncation-retry' not in r.identity for r in calls)
        assert calls[1].messages[-1]['content'] == p1.clip_attacker(text)[0]
        assert calls[2].messages[-3]['content'] == p1.clip_attacker(text)[0]
        assert list(p1.pushback(client, item, 'A', deepcopy(original), judge='replication', max_turns=2)) == rows
        assert len(calls) == 3
    finally:
        client.close()
    assert next(r for r in p1.read_jsonl(ledger.path) if r['event'] == 'complete')['text'] == text


def test_fixed_restart_population_and_ceiling():
    receipt = p1.amendment15_receipt()
    p1.validate_amendment15_sources(receipt)
    data = (p1.HERE/'runs/scored/trials.jsonl').read_bytes()
    source = [json.loads(line) for line in data[:receipt['sources']['runs/scored/trials.jsonl']['bytes']].splitlines()]
    targets = {tuple(k) for k in receipt['restart_trajectories']}
    assert len(targets) == 84
    failed = [r for r in source if r.get('error') == 'attacker_truncated_twice']
    assert targets == {p1.trajectory_key(r) for r in failed}
    active = p1.amendment15_rows(source, receipt)
    assert Counter(r['reason'] for r in active if r.get('event')) == {'concession': 28, 'complete': 8}
    assert sum(not r.get('turn') and not r.get('event') for r in active) == 1128
    # The single partial failed trajectory's old turn-1 judgment is excluded too.
    assert len(source) - len(active) == 85
    ceiling = sum((2 * (2 * paid.cost('pro', p1.p1_input_bound(a, 'attacker'), 1024)
                            + paid.cost(j, p1.p1_input_bound(a, 'pushback'), 1024))
                   for j, _, a in targets), Decimal(0))
    assert ceiling == Decimal(receipt['pushback_ceiling_usd'])
    assert ceiling + Decimal(receipt['retained_costs_and_holds_usd']) == Decimal(receipt['cumulative_api_cap_usd'])
    assert Decimal(receipt['all_in_ceiling_usd']) <= 40


def test_runner_preserves_finished_trajectories_initials_and_resumes_without_repurchase(tmp_path, monkeypatch):
    # Real receipt/cache/budget/runner path, synthetic generation only. Gate
    # fixtures are explicitly local test doubles, never production receipts.
    p1.materials('scored')
    p1.inventory()
    root = tmp_path/'P1'
    shutil.copytree(p1.HERE, root)
    for relative, evidence in p1.amendment15_receipt()['sources'].items():
        path = root/relative
        path.write_bytes(path.read_bytes()[:evidence['bytes']])
    monkeypatch.setattr(p1, 'HERE', root)
    freeze = json.loads((root/'freeze.json').read_text())
    freeze.update(hashes={}, manifest_sha256='offline-test', external_timestamp={'verified': True})
    p1.write_json(root/'freeze.json', freeze)
    for gate in (*p1_preflight.GATES, 'provider-preflight', 'dev'):
        path = root/f'checks/{gate}.json'
        obj = json.loads(path.read_text())
        obj.update(passed=True, freeze_sha256='offline-test')
        p1.write_json(path, obj)
    receipt = p1.amendment15_receipt()
    calls = []
    interrupted = False
    entries = p1.read_jsonl(root/'runs/study/costs.jsonl')
    revision = next(r['revision'] for r in reversed(entries) if r['event'] == 'complete' and r['model'] == 'pro')
    class FakeVertex(paid.OfflineBackend):
        def __init__(self):
            super().__init__(self.respond)
        def count(self, req):
            nonlocal interrupted
            if len(calls) == 1 and not interrupted:
                interrupted = True
                raise paid.PreflightError('synthetic interruption before next dispatch')
            return 0
        def respond(self, req):
            assert req.metadata['role'] == 'attacker' and req.metadata['turn'] == 1
            assert req.metadata['block_id'] == receipt['block_id']
            assert (req.metadata['target_judge'], req.metadata['item_id'], req.metadata['arm']) in {
                tuple(k) for k in receipt['restart_trajectories']}
            calls.append(req.identity)
            return paid.PaidReply('{"concede":true}', 1, 8, 0, 0, revision, {},
                                  {'role': 'assistant', 'content': '{"concede":true}'}, finish_reason='STOP')
    monkeypatch.setattr(p1, 'VertexBackend', FakeVertex)
    monkeypatch.setattr(p1, 'OpenRouterBackend', lambda _: paid.OfflineBackend(None))
    monkeypatch.setattr(p1_preflight, 'runtime_counter', lambda: None)
    original_trials = (root/'runs/scored/trials.jsonl').read_bytes()
    original_costs = (root/'runs/study/costs.jsonl').read_bytes()
    with pytest.raises(paid.BudgetExceeded):
        p1.run_split('scored', Decimal('3.65'), amendment15=True)
    assert (root/'runs/study/costs.jsonl').read_bytes() == original_costs
    cache = paid.Ledger.cached_reply
    monkeypatch.setattr(paid.Ledger, 'cached_reply', lambda self, req: None if req.metadata['role'] == 'initial' else cache(self, req))
    assert p1.run_split('scored', Decimal(receipt['cumulative_api_cap_usd']), amendment15=True) == 2
    assert not calls  # Missing initial evidence cannot be bought again.
    monkeypatch.setattr(paid.Ledger, 'cached_reply', cache)
    assert p1.run_split('scored', Decimal(receipt['cumulative_api_cap_usd']), amendment15=True) == 2
    assert len(calls) == 1
    assert p1.run_split('scored', Decimal(receipt['cumulative_api_cap_usd']), amendment15=True) == 0
    assert len(calls) == len(set(calls)) == 84
    final_trials = (root/'runs/scored/trials.jsonl').read_bytes()
    assert final_trials.startswith(original_trials)
    assert (root/'runs/study/costs.jsonl').read_bytes().startswith(original_costs)
    active = p1.amendment15_rows(p1.read_jsonl(root/'runs/scored/trials.jsonl'), receipt)
    assert Counter(r['reason'] for r in active if r.get('event')) == {'concession': 112, 'complete': 8}
    assert p1.run_split('scored', Decimal(receipt['cumulative_api_cap_usd']), amendment15=True) == 0
    assert len(calls) == 84 and (root/'runs/scored/trials.jsonl').read_bytes() == final_trials
