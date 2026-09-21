#!/usr/bin/env python3
"""Targeted finite-model checks for two semantic errors found before freezing.

These are witness checks, not differential tests against Cedar or OPA engines.
"""
import copy
import json
from pathlib import Path
import sys

sys.path.insert(0, '/private/tmp/ve-e0-integration')
import ve

ROOT = Path(__file__).resolve().parent


def row_for(dataset, suffix):
    combined = ROOT / 'second_rater.jsonl'
    path = combined if combined.exists() else ROOT / 'second_rater_work' / f'{dataset}.jsonl'
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    selected = [r for r in rows if r['dataset'] == dataset and r['id'].endswith(suffix)]
    assert len(selected) == 1
    return selected[0]


def empty_model(row):
    vocab = row['environment']['vocabulary']
    model = {'complete': True, 'domains': {s: [] for s in vocab['sorts']},
             'constants': {}, 'relations': {p: [] for p in vocab['predicates']}}
    for name, decl in vocab['constants'].items():
        model['domains'][decl['sort']].append(name)
        model['constants'][name] = name
    return model


def value(row, model):
    env = ve.Environment(row['environment'])
    checked = ve.check(env, row['formalization'], ve.FiniteModel.from_dict(env, model))
    result = checked['evaluation']
    assert result['status'] in ('Satisfied', 'Violated'), result['status']
    return result['value']


def cedar_missing_boolean():
    row = row_for('cedar', 'tests/multi/policies_4.cedar#3')
    model = empty_model(row)
    for sort, atom in [('request', 'q'), ('principal', 'p'), ('action', 'a'), ('resource', 'r')]:
        model['domains'][sort].append(atom)
    model['relations'].update(request_principal=[['q', 'p']], request_action=[['q', 'a']],
                              request_resource=[['q', 'r']])
    # Missing is an error/non-match, not the Boolean false.
    assert value(row, model) is True
    bad_missing = copy.deepcopy(model)
    bad_missing['relations']['contributes_forbid'] = [['q']]
    assert value(row, bad_missing) is False
    false_case = copy.deepcopy(model)
    false_case['relations']['authenticated_value'] = [['q', 'false_value']]
    assert value(row, false_case) is False  # must contribute forbid
    false_case['relations']['contributes_forbid'] = [['q']]
    assert value(row, false_case) is True
    true_case = copy.deepcopy(model)
    true_case['relations']['authenticated_value'] = [['q', 'true_value']]
    assert value(row, true_case) is True
    return 5


def gatekeeper_probe_binding():
    row = row_for('gatekeeper', 'general/requiredprobes/src.rego')
    model = empty_model(row)
    model['domains'].update(container=['c'], item=['liveness', 'readiness'],
                            probe=['live_probe', 'ready_probe'], value=['http_get'])
    model['relations'].update(
        has_container=[['review', 'c']],
        required_probe=[['liveness'], ['readiness']],
        required_probe_type=[['http_get']],
        container_probe=[['c', 'live_probe'], ['c', 'ready_probe']],
        probe_name=[['live_probe', 'liveness'], ['ready_probe', 'readiness']],
        probe_type_truthy=[['live_probe', 'http_get']],
    )
    # One valid probe cannot supply the required type for a different probe.
    assert value(row, model) is True
    model['relations']['probe_type_truthy'].append(['ready_probe', 'http_get'])
    assert value(row, model) is False
    model['relations']['container_probe'].pop()
    assert value(row, model) is True  # required probe is missing
    model['relations']['is_update'] = [['review']]
    assert value(row, model) is False  # update guard suppresses the violation
    return 4


if __name__ == '__main__':
    total = cedar_missing_boolean() + gatekeeper_probe_binding()
    print(f'{total} finite-model spot checks passed (Cedar missing Boolean; Gatekeeper probe binding/update).')
