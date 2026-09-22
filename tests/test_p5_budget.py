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
        + Decimal('.30') + Decimal(c['api_usd']))
    assert c['future_online_calls'] == 858
    assert c['combined_attributed_item_arm_usd']['VE'] == '0.4465404776'
    assert Decimal(c['combined_attributed_item_arm_usd']['VE']) > Decimal('.38')


def test_reduced_assignment_analysis_uses_nine_independent_families():
    r = p.analyze([], p.scheduled_materials('scored'), p.labels(),
                  p.SCENARIOS['dual_judge'], allow_missing=True, draws_count=10)
    assert r['families'] == 9 and r['assigned'] == r['missing'] == 216
