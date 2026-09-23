"""Schedule selection, retained cost and assignment regressions; no inference."""
from collections import Counter
from decimal import Decimal

import pytest

from experiments import p5 as p, p5_budget as budget


def test_scenario_priority_and_maximal_balanced_family_count():
    report = budget.plan()
    for row in report['scenarios']:
        c = p.ceilings(row['scenario'], row['scored_families'])
        assert c['all_in_usd'] == row['all_in_usd']
        assert c['within_cap'] == row['within_study_cap']
    assert p.ceilings('dual_judge', 9)['within_cap']
    assert not p.ceilings('dual_judge', 12)['within_cap']
    assert not p.ceilings('primary', 24)['within_cap']
    assert p.ceilings('primary', 9)['within_cap']
    assert not p.ceilings('primary', 12)['within_cap']
    for invalid in (0, 8, 10, 27):
        with pytest.raises(ValueError): budget.family_names(invalid)


def test_execution_keeps_whole_balanced_siblings_and_all_arms():
    items = p.scheduled_materials('scored')
    selected = {i['id'] for i in items}
    labels = [r for r in p.labels(False) if r['id'] in selected]
    assert len(items) == 27 and len(p.scheduled_materials('dev')) == 12
    assert Counter(r['family'] for r in labels) == {f: 3 for f in budget.family_names(9)}
    assert Counter(r['predicates'] for r in labels) == {20: 9, 40: 9, 60: 9}
    assert Counter(r['kind'] for r in labels) == {'shift': 9, 'smuggle': 9, 'benign': 9}
    assert set(p.ARMS) == {'X', 'S', 'VE', 'L'}
    assert p.stage_list('X').count('answer') == 3
    assert len(p.materials()) == 84  # Reviewed archive remains intact.


def test_retained_envelopes_cpu_and_dev_are_charged_once():
    data = budget.plan()
    c = p.ceilings('dual_judge')
    assert Decimal(c['all_in_usd']) == (Decimal(data['retained_commitment_usd'])
        + Decimal(data['calibration_task_cap_usd']) + Decimal(c['api_usd']))
    assert c['future_online_calls'] == 774
    assert c['combined_attributed_item_arm_usd']['VE'] == '0.4275424776'
    assert Decimal(c['combined_attributed_item_arm_usd']['VE']) > Decimal('.38')


def test_reduced_assignment_analysis_uses_nine_independent_families():
    r = p.analyze([], p.scheduled_materials('scored'), p.labels(),
                  p.SCENARIOS['dual_judge'], allow_missing=True, draws_count=10)
    assert r['families'] == 9 and r['assigned'] == r['missing'] == 216


@pytest.mark.parametrize('arm', p.ARMS)
@pytest.mark.parametrize('model', ['pro', 'replication'])
@pytest.mark.parametrize('failure', ['500', 'reset', 'interrupted'])
def test_retried_arm_keeps_equal_reasoning_budget_and_study_charges(tmp_path, monkeypatch, arm, model, failure):
    from dataclasses import replace
    from experiments.p5_materials import read
    from ve_experiments import paid
    item = p.materials('dev')[0]
    req = p.request(item, arm, 'lone' if arm == 'L' else 'judge' if model == 'replication' else 'author', judge=model)
    ceiling = paid.cost(req.model, req.max_input_tokens, req.billed_output_cap)
    monkeypatch.setattr(p, 'HERE', tmp_path)
    monkeypatch.setattr(p, 'MATCHED_CAP', 2 * ceiling)
    monkeypatch.setattr(paid.time, 'sleep', lambda _: None)
    book = p.P5Ledger(tmp_path/'costs.jsonl', 40)
    calls = []
    if failure == 'interrupted':
        book.reserve(req)
        book.reconcile_interrupted()
    def respond(request):
        calls.append(request)
        if len(calls) == 1 and failure != 'interrupted':
            if failure == 'reset':
                raise ConnectionResetError('offline connection reset')
            raise paid.InfrastructureError('offline HTTP 500', 500)
        # Deliberately not a valid scored answer: acceptance is provider validation,
        # never semantic success or a favorable verdict.
        return paid.PaidReply('bad answer', req.max_input_tokens, req.billed_output_cap,
                              0, 0, 'offline', {}, {})
    client = paid.PaidClient(paid.OfflineBackend(respond), book, reuse_completed=True)
    try:
        if failure == 'reset':
            with pytest.raises(paid.PreflightError, match='connection reset'):
                client.call(req)
            book.reconcile_interrupted()
        client.call(req)
        assert budget.matched_charges(read(book.path))[1][item['id'], arm] == ceiling
        assert book.state(read(book.path))[1] == 2 * ceiling
        evidence = book.path.read_bytes()
        client.call(req)  # Resume/cache adds neither a call nor a charge.
        assert book.path.read_bytes() == evidence
        next_req = replace(req, identity=req.identity+'/next')
        # Infrastructure still exhausts the aggregate cap, even with matched room.
        book.cap = 3 * ceiling - Decimal('.00000001')
        with pytest.raises(paid.BudgetExceeded, match='--cap-usd'):
            client.call(next_req)
        book.cap = Decimal(40)
        client.call(next_req)  # Full second accepted call still fits exactly.
        assert book.state(read(book.path))[1] == 3 * ceiling
        assert budget.matched_charges(read(book.path))[1][item['id'], arm] == 2 * ceiling
        with pytest.raises(paid.BudgetExceeded, match='accepted responses only'):
            client.call(replace(req, identity=req.identity+'/over'))
    finally:
        client.close()


def test_matched_views_exclude_shared_failures_and_rejected_completions(tmp_path, monkeypatch):
    import json
    from hashlib import sha256
    from experiments.p5_materials import write_json
    from experiments.p5_preflight import cost_report
    item = p.materials('dev')[0]
    def events(identity, role, arm):
        meta = {'item_id': item['id'], 'role': role, 'arm': arm}
        return [
            {'event': 'reserve', 'identity': identity, 'metadata': meta},
            {'event': 'infrastructure_failure', 'identity': identity, 'infrastructure_hold_usd': '.30'},
            {'event': 'reserve', 'identity': identity, 'metadata': meta},
            {'event': 'interrupted', 'identity': identity, 'cost_usd': '.30'},
            {'event': 'reserve', 'identity': identity, 'metadata': meta},
            {'event': 'complete', 'identity': identity, 'cost_usd': '.01'},
        ]
    rows = events('study-v9/dev/shared', 'paraphrase', 'shared')
    rows += events('study-v9/dev/X', 'author', 'X')
    rows += events('study-v9/dev/VE', 'author', 'VE')
    rows += [{'event': 'panel_validation_halt', 'identity': 'study-v9/dev/VE'}]
    rows += events('study-v9/dev/S', 'author', 'S')
    rows += [{'event': 'halt', 'identity': 'study-v9/dev/S'}]
    monkeypatch.setattr(p, 'HERE', tmp_path)
    monkeypatch.setattr(p, 'scheduled_materials', lambda _: [item])
    ledger = tmp_path/'runs/study/costs.jsonl'
    ledger.parent.mkdir(parents=True)
    ledger.write_text(''.join(json.dumps(r)+'\n' for r in rows))
    revision = tmp_path/'runs/revision-fixture/paraphrase-costs.jsonl'
    revision.parent.mkdir()
    revision.write_text(''.join(json.dumps(r)+'\n' for r in events('rewrite', 'paraphrase', 'shared')))
    write_json(tmp_path/'checks/budget-scenarios.json', {
        'ledger_prefix_bytes': len(ledger.read_bytes()),
        'ledger_prefix_sha256': sha256(ledger.read_bytes()).hexdigest()})
    shared, charged = budget.item_charges()
    assert shared[item['id']] == Decimal('.02')
    assert charged[item['id'], 'X'] == Decimal('.01')
    assert charged[item['id'], 'VE'] == charged[item['id'], 'S'] == 0
    report = cost_report('dev')
    assert report['physical_shared_paraphrase_usd'] == '1.22'
    assert report['charged_infrastructure_holds_usd'] == '3.00'
    assert report['item_arm_attributed_usd'][item['id']+'/X'] == '0.03'
    assert report['item_arm_attributed_usd'][item['id']+'/VE'] == '0.02'
    assert report['matched_ceiling_passed']


def test_empty_cost_report_has_no_phantom_reasoning_charge(tmp_path, monkeypatch):
    from experiments.p5_preflight import cost_report
    item = p.materials('dev')[0]
    monkeypatch.setattr(p, 'HERE', tmp_path)
    monkeypatch.setattr(p, 'scheduled_materials', lambda _: [item])
    report = cost_report('dev')
    assert set(report['item_arm_attributed_usd'].values()) == {'0'}
    assert report['paired_cost_ratios_VE_over_X'][item['id']] is None
    assert report['family_paired_ratio'] == {'estimate': None, 'bootstrap_interval': None}
