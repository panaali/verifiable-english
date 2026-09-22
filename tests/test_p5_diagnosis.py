"""P5 retained-dev diagnosis and narrowly scoped delivery/scorer regressions."""
from types import SimpleNamespace

import pytest

from experiments import p5 as p
from experiments.p5_analysis import endpoint, parse
from experiments.p5_diagnosis import audit
from ve_experiments.paid import packed


@pytest.mark.parametrize('wrapper', ['{}','```json\n{}\n```','```\n{}\n```'])
def test_nonjudge_wrapper_is_lossless(wrapper):
    artifact={'environment':'invalid, never repaired','source':'some prose'}
    assert p.protocol_json(wrapper.format(packed(artifact)))==artifact


@pytest.mark.parametrize('text', ['```json\n{"x":1}',
    'prefix\n```json\n{"x":1}\n```', '```json\n{"x":1}\n```\nsuffix',
    '```json\n{"x":1,}\n```', '```python\n{"x":1}\n```'])
def test_nonjudge_parser_never_salvages_partial_or_invalid_content(text):
    with pytest.raises(ValueError): p.protocol_json(text)


def test_final_judgment_contract_stays_strict():
    answer={'verdict':'approve','issue_type':'none','locations':[],'explanation':'supported'}
    with pytest.raises(ValueError): parse('```json\n'+packed(answer)+'\n```',[])


@pytest.mark.parametrize('question', [None,17,{}, {'question':'q','answer':'leak'}, {'question':[]}])
def test_question_wrapper_is_not_arbitrary_serialization(question):
    with pytest.raises(ValueError): p.question_text(question)


def test_fenced_x_protocol_delivers_questions_and_preserves_copy_isolation():
    item=p.materials('dev')[0]; requests=[]
    def call(req):
        requests.append(req); role=req.metadata['role']
        value={'author':{'commitment':'FIXED','argument':'PRIVATE_DEFENSE'},
            'critic':{'questions':[{'question':'Q1'},'Q2',{'question':'Q3'}]},
            'followup':{'question':'Q4'},
            'judge':{'verdict':'unknown','issue_type':'unknown','locations':[],'explanation':'uncertain'}}.get(role)
        text='ANSWER_'+str(req.metadata['turn']) if value is None else packed(value)
        if role in ('author','critic','followup'): text='```json\n'+text+'\n```'
        return SimpleNamespace(text=text)
    client=SimpleNamespace(call=call,backend=SimpleNamespace(count=lambda req:len(req.messages[-1]['content'].split())))
    row=p.execute(item,'X',client,{'pro':client})[0]
    answers=[r for r in requests if r.metadata['role'] in ('answer','followup_answer')]
    assert len(answers)==4 and not row['protocol_error'] and not row['unresolved']
    for req,q in zip(answers,('Q1','Q2','Q3','Q4')):
        content=req.messages[-1]['content']
        assert content==p.packet(item,'X')+'\nFrozen commitment:\nFIXED\nOne question:\n'+q
        assert 'PRIVATE_DEFENSE' not in content and 'ANSWER_' not in content
    judge=requests[-1].messages[-1]['content']
    assert judge.count('"stage":"isolated_answer"')==3
    assert '"stage":"isolated_followup_answer"' in judge
    assert 'ANSWER_2' in judge


def test_fenced_ve_reaches_checker_but_invalid_environment_is_still_failure(monkeypatch):
    from experiments import p5_oracle as oracle
    checks=[]
    def bounded(operation,data,seconds):
        checks.append(data)
        # Use the actual checker rejection, not a fabricated graph result.
        with pytest.raises(Exception,match='Expected a JSON object'):
            oracle.author_graph(data['artifact'],data['packet'])
        return {'ok':False,'status':'UNKNOWN','error':'VEError: Expected a JSON object','elapsed_s':.001}
    monkeypatch.setattr(oracle,'bounded',bounded)
    requests=[]
    def call(req):
        requests.append(req)
        answer={'verdict':'approve','issue_type':'none','locations':[],'explanation':'supported'}
        artifact={'environment':'VE core@0 environment','queries':[],'splits':[]}
        return SimpleNamespace(text=packed(answer) if req.metadata['role']=='judge' else '```json\n'+packed(artifact)+'\n```')
    client=SimpleNamespace(call=call)
    row=p.execute(p.materials('dev')[0],'VE',client,{'pro':client})[0]
    assert len(checks)==3  # author, the single repair, defender
    assert row['author_failure'] and row['unresolved']
    assert 'VEError: Expected a JSON object' in requests[-1].messages[-1]['content']
    assert endpoint({'kind':'benign','acceptable_locations':[]},row)['score']==0


def test_author_failure_does_not_override_valid_final_decision_or_safety():
    label={'kind':'shift','acceptable_locations':[['n01'],['n00','n01']]}
    answer={'verdict':'reject','issue_type':'shift','locations':['n01'],'explanation':'records conflict'}
    row={'ok':True,'answer':answer,'author_failure':True,'unresolved':['tool failed']}
    result=endpoint(label,row,True)
    assert result['score']==1 and result['author_failure']==1
    assert result['failed']==0 and result['unsafe_approval']==0
    assert endpoint(label,row,False)['score']==0
    for change in ({'verdict':'approve'},{'issue_type':'smuggle'},{'locations':['n01','r00']},{'locations':[]}):
        assert endpoint(label,{**row,'answer':{**answer,**change}},True)['score']==0
    for change in ({'ok':False},{'error':'invalid JSON'}):
        assert endpoint(label,{**row,**change},True)['score']==0
    assert endpoint(label,None,True)['score']==0


def test_retained_dev_ledger_delivery_and_corrected_scores():
    rows=p.read(p.run_path('dev','trials.jsonl'))
    report=audit(rows,p.materials('dev'),p.labels(),p.read(p.HERE/'runs/study/costs.jsonl'))
    assert report['assigned']==96 and report['observed']==94
    assert all(d.get('ledger_and_history_verified') for d in report['decisions'] if d['observed'])
    assert sum(d['score'] for d in report['decisions'] if d['kind']!='benign')==0
    assert report['cause_counts_overlap']['scorer_author_failure_veto']=={'pro':3,'replication':1}
    assert all(not r['isolated_answer_requests'] for r in report['protocols'] if r['arm']=='X')
    stages=[s for r in report['protocols'] if r['arm']=='VE' for s in r['stages'] if 'offline_checker' in s]
    assert len(stages)==36 and all(not s['offline_checker']['ok'] for s in stages)
    # Source logs are evidence only: no reconstructed answers or ratings.
    assert report['model_calls']==0 and report['rating_records']==0
