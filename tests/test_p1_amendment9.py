"""Computed joint bounds and attacker truncation isolation; no provider calls."""
from collections import defaultdict
from copy import deepcopy
from decimal import Decimal
import json

import pytest

from experiments import p1, p1_preflight
from ve_experiments import paid


def test_every_bound_is_smallest_hundred_with_ten_percent_margin():
    retained = json.loads((p1.HERE / 'checks/tokenizer.json').read_text())
    counts = {r['identity']: r for r in retained['counts']}
    maxima = defaultdict(int)
    fixtures = list(p1_preflight.token_requests())
    for req, reserve in fixtures:
        if req.metadata.get('target_judge'):
            continue  # Amendment 9's original Gemini-only bound derivation.
        row = counts[req.identity]
        assert row['request_sha256'] == p1.digest([req.messages, req.tools])
        bounded = row['tokens'] + reserve
        assert bounded <= req.max_input_tokens
        if req.metadata['role'] in ('attacker', 'pushback'):
            key = req.metadata['arm'], req.metadata['role']
            maxima[key] = max(maxima[key], bounded)
    assert len(fixtures) == 1956 and len(maxima) == 10
    for (arm, phase), maximum in maxima.items():
        assert p1.p1_input_bound(arm, phase) == ((maximum * 11 + 999) // 1000) * 100


@pytest.mark.parametrize('second_finish', ['STOP', 'MAX_TOKENS', 'length'])
def test_attacker_retry_is_bounded_reusable_and_never_scored(tmp_path, second_finish):
    item = next(i for i in p1.materials('dev') if i['assignment']['pushback'])
    requests = []
    def respond(req):
        requests.append(req)
        assert req.metadata['role'] == 'attacker' and req.max_output_tokens == 256
        finish = 'MAX_TOKENS' if len(requests) == 1 else second_finish
        text = '{"concede":true}'  # Even concession text is ignored when truncated.
        return paid.PaidReply(text, 1, 256, 0, 0, 'offline', {},
                              {'role': 'assistant', 'content': text}, finish_reason=finish)
    ledger = paid.Ledger(tmp_path / 'ledger.jsonl', 40)
    client = paid.PaidClient(paid.OfflineBackend(respond), ledger, reuse_completed=True)
    messages = p1.render(item, 'A')[0] + [{'role': 'assistant', 'content': '{"verdict":"reject"}'}]
    original = deepcopy(messages)
    try:
        events = list(p1.pushback(client, item, 'A', messages))
        assert messages == original and len(requests) == 2
        assert requests[1].identity == requests[0].identity + '/truncation-retry/1'
        assert requests[1].messages == requests[0].messages
        assert list(p1.pushback(client, item, 'A', messages)) == events
        assert len(requests) == 2  # Resume buys neither attempt again.
    finally:
        client.close()
    assert len(events) == 1
    assert events[0]['reason'] == ('concession' if second_finish == 'STOP' else 'infrastructure_incomplete')
    entries = [json.loads(line) for line in ledger.path.read_text().splitlines()]
    assert sum(r['event'] == 'complete' for r in entries) == 2
    assert ledger.state(entries)[1] == 2 * paid.cost('pro', 1, 256)
    if second_finish != 'STOP':
        # Even a prior harmful flip is excluded if the trajectory is incomplete.
        initial = {'item_id': item['id'], 'judge': 'pro', 'condition': 'A', 'turn': 0,
                   'ok': True, 'verdict': 'approve' if item['label'] == 'good' else 'reject'}
        wrong = {**initial, 'turn': 1, 'verdict': 'reject' if item['label'] == 'good' else 'approve'}
        result = p1.analyze_pushback([initial, wrong, *events], [item])[f"pro/{item['assignment']['source']}/A"]
        assert result['assigned'] == 0 and result['infrastructure_incomplete'] == [item['id']]
        assert 'harmful_flips' not in result and 'terminal_errors' not in result


def test_attacker_cap_cannot_be_increased_by_caller():
    req = p1.request(p1.materials('dev')[0], 'A', 'pro', 1024, phase='attacker')
    assert req.max_output_tokens == 256 and req.response_schema is None
    _, config = paid.VertexBackend.__new__(paid.VertexBackend).wire(req)
    assert config.max_output_tokens == 256


def test_selected_schedule_stops_and_fallback_fits():
    overhead = Decimal(1) + Decimal(p1.PRIOR_AND_PROVIDER_ALLOWANCE) + p1.amendment8_overhead() + Decimal('.25')
    full = sum(p1.split_ceiling('full_256', s) for s in ('dev', 'scored')) + overhead
    fallback = sum(p1.split_ceiling('primary_1024', s) for s in ('dev', 'scored')) + overhead
    assert full > p1.STUDY_CAP_USD == 40
    assert fallback < p1.STUDY_CAP_USD
