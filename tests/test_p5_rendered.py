"""Amended material provenance, authentic review binding, and bounded recovery."""
from copy import deepcopy
from decimal import Decimal
import json
import shutil

import pytest
from experiments import p5, p5_rendered as r
from experiments.p5_materials import archive, read, write_json
from ve_experiments.paid import Ledger, PaidReply, digest, PreflightError


@pytest.fixture
def materials(tmp_path):
    for name in ('labels.jsonl.gz','materials/dossiers.jsonl.gz',
                 'materials/dev.jsonl.gz','materials/scored.jsonl.gz',
                 'materials/round5-reviewed-packets.jsonl.gz','materials/prose-policy.json',
                 'checks/round5-review-verification.txt'):
        target=tmp_path/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p5.HERE/name,target)
    return tmp_path


def test_provenance_rejects_laundered_payload_and_tail_change(materials):
    assert r.provenance(materials)['passed']
    path=materials/'materials/dev.jsonl.gz'
    items=read(path)
    items[0]['payload']['argument'] += ' Added assumption.'
    archive(path,items)
    policy=json.loads((materials/'materials/prose-policy.json').read_text())
    policy['packet_hashes'][items[0]['id']]=digest(items[0]['payload'])
    write_json(materials/'materials/prose-policy.json',policy)
    assert not r.provenance(materials)['passed']
    assert r.provenance(materials)['independent_paraphrase_required'] is False


def test_review_contract_uses_one_complete_judge_packet():
    item=p5.materials()[0]
    req=r.review_request(item)
    assert req.messages[-1]['content']==p5.packet(item,'L')
    assert req.max_output_tokens==4096
    assert req.billed_output_cap==4096
    assert req.metadata['packet_sha256']==digest(item['payload'])
    with pytest.raises(ValueError):
        r.validate_review({'ready':True},item)
    with pytest.raises(ValueError):
        r.validate_review({'ready':True,'kind':'shift','locations':['missing'],
                           'evidence':'example','issues':[]},item)


def test_report_policy_requires_every_authentic_current_diagnosis(materials,monkeypatch):
    import experiments.p5_leakage
    monkeypatch.setattr(experiments.p5_leakage,'audit',lambda base:{'passed':True})
    items=read(materials/'materials/dev.jsonl.gz')+read(materials/'materials/scored.jsonl.gz')
    labels={a['id']:a for a in read(materials/'labels.jsonl.gz')}
    reviews=[]; ledger=[]
    # Synthetic test evidence only; never submitted to the production review ledger.
    for item in items:
        label=labels[item['id']]; req=r.review_request(item)
        review={'ready':True,'kind':label['kind'],'locations':[] if label['kind']=='benign' else label['acceptable_locations'][1],
                'evidence':'synthetic test evidence','issues':[]}
        text=json.dumps(review)
        reviews.append({'item_id':item['id'],'packet_sha256':digest(item['payload']),
                        'request_version':3,'request_sha256':digest(req.messages),
                        'response_sha256':digest(text),'review':review})
        ledger.extend([{'event':'reserve','identity':req.identity,'messages':req.messages,'metadata':req.metadata},
                       {'event':'complete','identity':req.identity,'text':text,'input_tokens':100,
                        'billed_output_tokens':100,'finish_reason':'STOP','revision':'gemini-3.1-pro-preview'}])
    submission=materials/'checks/gemini-rendered-submission.json'
    write_json(submission,reviews)
    path=materials/'runs/revision-v8/gemini-review-costs.jsonl'
    path.parent.mkdir(parents=True)
    path.write_text('\n'.join(json.dumps(a) for a in ledger)+'\n')
    assert r.review_gate(materials)['passed']
    reviews[0]['packet_sha256']='stale'
    write_json(submission,reviews)
    result=r.review_gate(materials)
    assert not result['passed'] and len(result['unresolved'])==1
    assert read(materials/'materials/anchored-labels.jsonl.gz')==[]
    reviews[0]['packet_sha256']=digest(items[0]['payload'])
    reviews[0]['review']['issues']=['Unresolved ambiguity']
    write_json(submission,reviews)
    assert not r.review_gate(materials)['passed']  # cannot edit a billed answer


def test_narrow_cap_recovery_preserves_spend_and_new_limit(tmp_path):
    item=p5.materials()[0]
    book=Ledger(tmp_path/'review.jsonl',1)
    req=r.review_request(item,1)
    book.reserve(req)
    book.complete(req,PaidReply('incomplete',2000,24,800,0,'gemini-3.1-pro-preview',{},{}),
                  'provider exceeded per-call token cap',panel_only=True)
    original=book.path.read_bytes()
    r.recover_review_cap(book)
    assert book.path.read_bytes().startswith(original)
    assert sum(x['event']=='material_review_cap_recovery' for x in read(book.path))==1
    r.recover_review_cap(book)
    assert sum(x['event']=='material_review_cap_recovery' for x in read(book.path))==1
    book.reserve(r.review_request(item,2))
    with book.locked() as (_,rows):
        assert Ledger.state(rows)[1]==Decimal('.013888')


def test_review_cap_checked_before_dispatch(monkeypatch):
    monkeypatch.setattr(r,'provenance',lambda:{'passed':False})
    for cap in (0,-1,'1.644181','NaN'):
        with pytest.raises(PreflightError,match='cap'):
            r.gemini_review(cap)
    with pytest.raises(PreflightError,match='all 84'):
        r.gemini_review(1)


def test_revision_costs_include_failed_calls_without_envelopes(tmp_path):
    path=tmp_path/'runs/revision-v7/paraphrase-costs.jsonl'
    path.parent.mkdir(parents=True)
    rows=[{'event':'reserve','identity':'a','metadata':{'role':'paraphrase','item_id':'i'}},
          {'event':'complete','identity':'a','cost_usd':'.01'},
          {'event':'reserve','identity':'b','metadata':{'role':'paraphrase','item_id':'i'}},
          {'event':'interrupted','identity':'b','cost_usd':'.002'},
          {'event':'allowance','identity':'envelope','cost_usd':'.40'}]
    path.write_text('\n'.join(json.dumps(x) for x in rows)+'\n')
    shared,holds=p5.revision_paraphrase_costs(tmp_path)
    assert shared=={'i':Decimal('.012')} and holds==Decimal('.002')


def test_packet_safety_accepts_only_correct_leading_step_markers(monkeypatch):
    from experiments.p5_preflight import packet_safety
    items=deepcopy(p5.materials())
    monkeypatch.setattr(p5,'materials',lambda:items)
    assert packet_safety()['passed']
    original=items[0]['payload']['argument']
    items[0]['payload']['argument']=original.replace('] ','] From n99, ',1)
    assert not packet_safety()['passed']
    items[0]['payload']['argument']=original.replace(original.split(']')[0]+']','[n99]',1)
    assert not packet_safety()['passed']


@pytest.mark.parametrize('version,billed',[(1,824),(2,1068)])
def test_old_cap_recovery_is_idempotent_and_retains_cost(tmp_path,version,billed):
    book=Ledger(tmp_path/'costs.jsonl',r.REVIEW_CUMULATIVE_CAP)
    req=r.review_request(p5.materials()[0],version)
    book.reserve(req)
    book.complete(req,PaidReply('{}',2000,100,billed-100,0,'gemini-3.1-pro-preview',{},{}),
                  'provider exceeded per-call token cap',panel_only=True)
    original=book.path.read_bytes()
    r.recover_review_cap(book); r.recover_review_cap(book)
    assert book.path.read_bytes().startswith(original)
    assert sum(x['event']=='material_review_cap_recovery' for x in read(book.path))==1
    book.reserve(r.review_request(p5.materials()[1]))


def test_ledger_resume_retains_negative_and_rejects_parseable_truncation(tmp_path):
    items=p5.materials()[:3]
    book=Ledger(tmp_path/'costs.jsonl',1)
    review={'ready':False,'kind':'uncertain','locations':[],
            'evidence':'ambiguous record','issues':['Ambiguous record']}
    for item,finish in zip(items,('STOP','MAX_TOKENS','STOP')):
        req=r.review_request(item,2)
        book.reserve(req)
        book.complete(req,PaidReply(json.dumps(review),2000,100,200,0,
                                    'gemini-3.1-pro-preview',{},{},finish_reason=finish))
    results,attempts=r.ledger_reviews(items,read(book.path))
    assert 'review' in results[items[0]['id']]
    assert 'review' not in results[items[1]['id']]
    summary=r.review_summary(items,results)
    assert (summary['accepted'],summary['flagged_defect'],summary['incomplete'])==(0,2,1)
    assert summary['defect_groups']==[{'defect':'Ambiguous record',
                                      'packet_ids':sorted([items[0]['id'],items[2]['id']])}]
    req=r.review_request(items[1]); book.reserve(req)
    book.complete(req,PaidReply(json.dumps({**review,'ready':True,'kind':'benign','issues':[]}),
                               2000,100,200,0,'gemini-3.1-pro-preview',{},{},finish_reason='STOP'))
    results,attempts=r.ledger_reviews(items,read(book.path))
    assert attempts=={items[1]['id']:0}
    assert r.review_summary(items,results)['accepted']==1
    assert results[items[0]['id']]['review']==review
    rows=read(book.path)
    rows[0]['messages']=[{'role':'user','content':'changed packet'}]
    assert 'review' not in r.ledger_reviews(items,rows)[0][items[0]['id']]


def test_4096_overrun_does_not_get_recovered(tmp_path):
    book=Ledger(tmp_path/'costs.jsonl',1)
    req=r.review_request(p5.materials()[0]); book.reserve(req)
    book.complete(req,PaidReply('{}',2000,100,4000,0,'gemini-3.1-pro-preview',{},{}),
                  'provider exceeded per-call token cap',panel_only=True)
    r.recover_review_cap(book)
    assert not any(x['event']=='material_review_cap_recovery' for x in read(book.path))
    with pytest.raises(PreflightError,match='token cap'):
        book.reserve(r.review_request(p5.materials()[1]))


def test_resume_dispatches_only_incomplete_and_uses_distinct_retry(tmp_path,monkeypatch):
    items=p5.materials()[:2]
    monkeypatch.setattr(r,'HERE',tmp_path)
    monkeypatch.setattr(r,'provenance',lambda:{'passed':True})
    monkeypatch.setattr(p5,'verify_freeze',lambda:None)
    monkeypatch.setattr(p5,'materials',lambda:items)
    book=Ledger(tmp_path/'runs/revision-v8/gemini-review-costs.jsonl',1)
    negative={'ready':False,'kind':'uncertain','locations':[],
              'evidence':'ambiguous record','issues':['Ambiguous record']}
    for item,finish in zip(items,('STOP','MAX_TOKENS')):
        req=r.review_request(item,2); book.reserve(req)
        book.complete(req,PaidReply(json.dumps(negative),100,50,50,0,
                                    'gemini-3.1-pro-preview',{},{},finish_reason=finish))
    dispatched=[]
    class Backend:
        def count(self,request): return 0
        async def generate(self,request):
            dispatched.append(request)
            # A parseable but truncated first attempt must be reissued on resume.
            return PaidReply(json.dumps(negative),100,50,50,0,
                             'gemini-3.1-pro-preview',{},{},
                             finish_reason='MAX_TOKENS' if len(dispatched)==1 else 'STOP')
    monkeypatch.setattr(r,'ReviewBackend',Backend)
    first=r.gemini_review(1)
    assert first['reused_complete_reviews']==1 and first['incomplete']==1
    (tmp_path/'checks/gemini-rendered-submission.json').unlink()
    second=r.gemini_review(1)
    assert second['flagged_defect']==2 and second['incomplete']==0
    assert [q.identity for q in dispatched]==[
        r.review_request(items[1]).identity,r.review_request(items[1],attempt=1).identity]
    third=r.gemini_review(1)
    assert third['reused_complete_reviews']==2 and len(dispatched)==2
