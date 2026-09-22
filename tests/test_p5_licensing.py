"""Mechanical dispute evidence must not launder a second flaw or stale review."""
from copy import deepcopy
import json
import shutil

import pytest
from experiments import p5, p5_licensing as licensing, p5_rendered
from experiments.p5_materials import read, write_json
from ve_experiments.paid import PreflightError


def disputed():
    return next(i for i in p5.materials() if i['id']=='ib9279ca87379a78c8da58ec68a9d4b42')


def test_actual_disputes_and_clear_free_readings():
    for item in p5.materials():
        if item['id'] not in licensing.AUTHORIZED_IDS:
            continue
        result=licensing.analyse(item['payload'])
        if item['id'] != disputed()['id']:
            assert result['kind']=='benign' and result['minimum_relaxations']==0
            continue
        assert result['zero_relaxation_assignments']==0
        assert result['unavoidable_unlicensed_steps']==['n03']
        for path in result['assignments']:
            steps={s['step_id']:s for s in path}
            assert steps['n20']['record']=='r10' and steps['n20']['relaxations']==0
            assert {a['required'][2] for a in steps['n20']['inputs']}=={'space available','fee waived'}
            assert steps['n05']['conclusion']==['unit4','clear','contamination absent']
            assert steps['n03']['inputs'][0]['required']==['unit4','clear','optically transparent']
            assert steps['n03']['inputs'][0]['producer']=='n05'


def test_second_shift_cannot_pass_global_one_relaxation_budget():
    packet=deepcopy(disputed()['payload'])
    rule=next(r for r in packet['records'] if r['id']=='r04')
    rule['text']=rule['text'].replace('unit7 is free (fee waived)','unit7 is free (space available)')
    assert licensing.search(packet,0)==[]
    assert licensing.search(packet,1)==[]
    assert licensing.search(packet,2)
    with pytest.raises(PreflightError,match='no reading'):
        licensing.analyse(packet)


def test_gate_recomputes_adjudication_and_retains_raw_diagnoses(tmp_path,monkeypatch):
    import experiments.p5_leakage
    monkeypatch.setattr(experiments.p5_leakage,'audit',lambda base:{'passed':True})
    for name in ('labels.jsonl.gz','materials/dossiers.jsonl.gz','materials/dev.jsonl.gz',
                 'materials/scored.jsonl.gz','materials/round5-reviewed-packets.jsonl.gz',
                 'materials/prose-policy.json','checks/round5-review-verification.txt',
                 'checks/gemini-rendered-submission.json','runs/revision-v8/gemini-review-costs.jsonl'):
        target=tmp_path/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p5.HERE/name,target)
    before=(tmp_path/'checks/gemini-rendered-submission.json').read_bytes()
    assert len(p5_rendered.review_gate(tmp_path)['unresolved'])==6
    licensing.adjudicate(tmp_path)
    result=p5_rendered.review_gate(tmp_path)
    assert result['passed'] and result['reviewed_slots']==84
    assert result['gemini_current']['matching_current_diagnoses']==78
    assert len(result['gemini_current']['adjudicated_packet_ids'])==6
    assert (tmp_path/'checks/gemini-rendered-submission.json').read_bytes()==before
    report=json.loads((tmp_path/licensing.REPORT).read_text())
    report['adjudications'][0]['evidence']['minimum_relaxations']=1
    write_json(tmp_path/licensing.REPORT,report)
    with pytest.raises(PreflightError,match='stale or invalid'):
        p5_rendered.review_gate(tmp_path)
    licensing.adjudicate(tmp_path)
    reviews=json.loads(before)
    next(r for r in reviews if r['item_id']==disputed()['id'])['review']['evidence']='changed'
    write_json(tmp_path/'checks/gemini-rendered-submission.json',reviews)
    with pytest.raises(PreflightError,match='stale or invalid'):
        p5_rendered.review_gate(tmp_path)
    # Even newly computed evidence cannot authenticate an edited provider reply.
    licensing.adjudicate(tmp_path)
    assert not p5_rendered.review_gate(tmp_path)['passed']
