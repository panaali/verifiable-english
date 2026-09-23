"""Regression coverage for the observed v10 delivery and stale-summary defects."""
import json
from types import SimpleNamespace

import pytest

from experiments import p5 as p
from experiments.p5_preflight import explanations
from experiments.p5_rerun_diagnosis import cohen, paired_ratings, response_key
from ve_experiments.paid import packed


@pytest.mark.parametrize('value', [
    {'question':'Q', 'text':'other'}, {'question':'Q', 'answer':'leak'},
    {'text':'Q', 'nodes':'n00'}, {'question':'Q', 'node_id':['n00']},
    {'text':'Q', 'type':{}}, {'text':None},
])
def test_question_annotations_do_not_allow_ambiguous_text_or_arbitrary_payload(value):
    with pytest.raises(ValueError): p.question_text(value)


def test_observed_annotated_questions_reach_isolated_copies_without_annotations():
    items = {i['id']:i for i in p.materials('dev')}
    observed = [r for r in p.dev_revision.trials('dev') if r['condition']=='X' and r['judge']=='pro'
                and 'question must be text or a single question field' in (r['protocol_error'] or '')]
    assert len(observed)==9
    for retained in observed:
        item = items[retained['item_id']]
        critic = next(h['text'] for h in retained['history'] if h['stage']=='critic')
        questions = p.protocol_json(critic)['questions']
        expected = [q.get('question',q.get('text')) for q in questions]
        calls = []
        def call(req):
            calls.append(req)
            role=req.metadata['role']
            text = {'author':packed({'commitment':'FIXED', 'argument':'PRIVATE_DEFENSE'}),
                    'critic':critic, 'followup':packed({'question':''}),
                    'judge':packed({'verdict':'unknown','issue_type':'unknown','locations':[],
                                    'explanation':'synthetic regression'})}.get(role,'SYNTHETIC ANSWER')
            return SimpleNamespace(text=text)
        client=SimpleNamespace(call=call,backend=SimpleNamespace(count=lambda req:1))
        row=p.execute(item,'X',client,{'pro':client})[0]
        assert not row['protocol_error'] and not row['unresolved']
        answers=[r for r in calls if r.metadata['role']=='answer']
        assert len(answers)==len(expected)
        for req,question in zip(answers,expected):
            assert req.messages[-1]['content']==p.packet(item,'X')+'\nFrozen commitment:\nFIXED\nOne question:\n'+question
            assert 'PRIVATE_DEFENSE' not in req.messages[-1]['content']
        assert retained['unresolved']  # Stored history is not retroactively repaired.


def test_annotated_question_still_enforces_visible_token_limit():
    def call(req):
        value = {'author':{'commitment':'fixed'},
                 'critic':{'questions':[{'text':'TOO LONG','node_id':'n00'}]},
                 'judge':{'verdict':'unknown','issue_type':'unknown','locations':[],'explanation':'synthetic'}}
        assert req.metadata['role'] in value  # An over-limit question must never dispatch.
        return SimpleNamespace(text=packed(value[req.metadata['role']]))
    client=SimpleNamespace(call=call,backend=SimpleNamespace(count=lambda req:
        257 if req.messages[-1]['content']=='TOO LONG' else 1))
    row=p.execute(p.materials('dev')[0],'X',client,{'pro':client})[0]
    assert 'exceeds 256' in row['protocol_error']


def test_rating_import_refreshes_both_analysis_and_dev_summary(tmp_path, monkeypatch):
    rows=p.dev_revision.trials('dev'); items=p.materials('dev'); labels=p.labels()
    ratings=p.read(p.dev_revision.run_path('dev','ratings.jsonl'))
    monkeypatch.setattr(p,'HERE',tmp_path)
    monkeypatch.setattr(p.dev_revision,'trials',lambda split:rows)
    monkeypatch.setattr(p,'materials',lambda split:items)
    monkeypatch.setattr(p,'scheduled_materials',lambda split:items)
    monkeypatch.setattr(p,'labels',lambda:labels)
    monkeypatch.setattr(p,'verify_freeze',lambda:{'scenario':'dual_judge'})
    old=p.analyze(rows,items,labels,('pro','replication'))
    old.update(passed=False,contract_passed=True,stopped=None,halted_judges={},
               freeze_sha256='recorded-execution-freeze')
    p.write_json(tmp_path/'checks/dev.json',old)
    incoming=tmp_path/'incoming.json'; incoming.write_text(json.dumps(ratings))
    assert explanations('dev',submit=incoming)=={'ratings_imported':96}
    summary=json.loads((tmp_path/'checks/dev.json').read_text())
    analysis=json.loads(p.dev_revision.run_path('dev','analysis.json').read_text())
    assert summary['judges']==analysis['judges']
    assert summary['judges']['pro']['accuracy']['L']=={'shift':.75,'smuggle':.5,'benign':1.0}
    assert summary['judges']['replication']['accuracy']['S']['shift']==.25
    assert summary['freeze_sha256']=='recorded-execution-freeze'
    assert summary['missing']==0 and not summary['source_fidelity_passed'] and not summary['passed']
    assert len(p.read(p.dev_revision.run_path('dev','ratings.jsonl')))==96


def test_cohen_uses_marginals_and_handles_undefined_populations():
    a=cohen([(True,True)]*19+[(False,True)]*17+[(False,False)]*12)
    assert a['n']==48 and a['agreement']==31/48
    assert a['kappa']==pytest.approx(19/53)
    assert cohen([(True,True)]*6)['kappa'] is None
    assert cohen([])['kappa'] is None
    assert cohen([(True,False),(False,True)])['kappa']==-1


def test_actual_rating_coverage_and_eligible_flaws_do_not_conflate_disagreement():
    from experiments.p5_analysis import endpoint, explanation_ratings
    rows=p.dev_revision.trials('dev'); labels={l['id']:l for l in p.labels()}
    ratings=p.read(p.dev_revision.run_path('dev','ratings.jsonl')); paired=paired_ratings(ratings)
    assert len(paired)==48
    accepted=explanation_ratings(rows,ratings)
    eligible=[r for r in rows if labels[r['item_id']]['kind']!='benign' and endpoint(labels[r['item_id']],r,True)['score']]
    assert len(eligible)==13
    blocked=[r for r in eligible if not accepted[response_key(r)]]
    assert len(blocked)==7 and all(r['condition'] in ('X','VE') and response_key(r) not in paired for r in blocked)
    credited=[r for r in eligible if accepted[response_key(r)]]
    assert len(credited)==6 and all(all(t['source_grounded'] for t in paired[response_key(r)].values()) for r in credited)
