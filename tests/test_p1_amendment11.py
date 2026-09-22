"""Budget choice and two-turn execution/analysis, without provider calls."""
from decimal import Decimal
import json

from experiments import p1
from ve_experiments import paid


def test_candidate_costs_include_every_call_retry_and_existing_allowance():
    expected = {
        'pro_replication_3turn': ('57.16220430250', '75.68651175850'),
        'pro_3turn': ('54.35460926890', '72.38110526890'),
        'full_2turn': ('46.70967065770', '64.06106086570'),
        'pro_replication_2turn': ('45.94988430250', '63.18395175850'),
        'primary_1024': ('25.18433726890', '25.18433726890'),
    }
    overhead = Decimal('2.08827326890')
    for name, (planning, worst) in expected.items():
        plan = p1.inventory()['budget_scenarios'][name]
        # Independently sum the inventory's cap-token rows, omitting the probe
        # row because its full $1 envelope is already in overhead.
        cap_total = sum((paid.cost(r['model'], r['max_input_per_call'],
                                  r['max_billed_output_per_call'], arm=r['arm']) * r['calls']
                         for r in plan['budget_rows'] if r['arm'] != 'probe'), Decimal(0))
        assert cap_total + overhead == Decimal(worst)
        assert p1.cumulative_ceiling(name) == Decimal(planning)
        assert p1.cumulative_ceiling(name, worst_case=True) == Decimal(worst)
    assert p1.STUDY_CAP_USD == 40
    assert p1.amendment11_selection() == 'primary_1024'
    probe = json.loads((p1.HERE / 'results/probe.json').read_text())
    assert probe['schedule_before_amendment12'] == 'primary_1024'
    assert probe['selected_output_cap'] == p1.JUDGE_OUTPUT_CAP == 1024
    assert probe['schedule_before_amendment11'] == 'full_256'
    assert probe['schedule_selection_before_amendment12']['amendment'] == 11


def test_selection_uses_priority_and_inclusive_strict_ceiling(monkeypatch):
    names = list(p1.P1_PANEL_SCENARIOS)
    ceilings = dict(zip(names, (41, 40, 39, 38)))
    def ceiling(name, *, worst_case=False):
        assert worst_case
        return ceilings[name]
    monkeypatch.setattr(p1, 'cumulative_ceiling', ceiling)
    assert p1.amendment11_selection() == names[1]
    ceilings[names[0]] = 40
    assert p1.amendment11_selection() == names[0]


def test_two_turn_dispatch_and_analysis_do_not_invent_third_turn(tmp_path):
    item = next(i for i in p1.materials('dev') if i['assignment']['pushback'])
    verdict = 'approve' if item['label'] == 'good' else 'reject'
    requests = []
    def respond(req):
        requests.append(req)
        return 'Please reconsider.' if req.metadata['role'] == 'attacker' else json.dumps({'verdict': verdict})
    ledger = paid.Ledger(tmp_path / 'ledger.jsonl', 40)
    client = paid.PaidClient(paid.OfflineBackend(respond), ledger)
    messages = p1.render(item, 'A')[0] + [{'role': 'assistant', 'content': json.dumps({'verdict': verdict})}]
    try:
        rows = list(p1.pushback(client, item, 'A', messages, max_turns=2))
    finally:
        client.close()
    assert [(r.metadata['role'], r.metadata['turn']) for r in requests] == [
        ('attacker', 1), ('pushback', 1), ('attacker', 2), ('pushback', 2)]
    assert rows[-1]['reason'] == 'complete' and rows[-1]['turn'] == 2
    initial = {'item_id': item['id'], 'judge': 'pro', 'condition': 'A', 'turn': 0,
               'ok': True, 'verdict': verdict}
    result = p1.analyze_pushback([initial, *rows], [item], max_turns=2)[f"pro/{item['assignment']['source']}/A"]
    assert result['turn_error_counts'] == [0, 0, 0]
    assert result['terminal_errors'] == result['missing_later_judgments'] == 0


def test_fallback_analysis_reports_dropped_panels_and_weak_not_run():
    plan = p1.inventory()['budget_scenarios']['primary_1024']
    items = [i for i in p1.materials('dev') if i['assignment']['source'] in plan['sources']]
    report = p1.split_report([], items, plan['judges'], {}, {'weak': 'historical halt'},
                             plan=plan, schedule_name='primary_1024')
    assert report['unscheduled'] == {'panels': ['E5'], 'judges': ['replication', 'weak']}
    assert report['weak_control_status'] == 'not run'
    assert report['pushback_turns'] == 0
    assert report['families'] == {}
    assert report['halted_judges'] == {}
