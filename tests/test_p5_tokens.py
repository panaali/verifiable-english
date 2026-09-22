"""Billing calibration regressions: offline fixtures and fake countTokens only."""
from dataclasses import replace
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from decimal import Decimal

from experiments import p5 as p, p5_preflight as pf, p5_tokens as tokens
from ve_experiments.paid import Ledger, PaidClient, PreflightError, VertexBackend, packed
from ve_experiments.paid import PaidReply, MODELS


@pytest.fixture
def calibrated(tmp_path, monkeypatch):
    evidence=json.loads((Path(__file__).parent/'fixtures/p5_vertex_smoke.json').read_text())
    ledger=tmp_path/'runs/study/costs.jsonl';ledger.parent.mkdir(parents=True)
    ledger.write_text('\n'.join(packed(evidence[k]) for k in ('reservation','completion'))+'\n')
    monkeypatch.setattr(p,'HERE',tmp_path)
    monkeypatch.setattr(PaidClient,'call',lambda *a,**kw:pytest.fail('generation forbidden'))
    calls=[]
    def count(**kw):
        calls.append(kw)
        return SimpleNamespace(total_tokens=17 if kw['config'].generation_config else 9)
    client=SimpleNamespace(models=SimpleNamespace(count_tokens=count))
    monkeypatch.setattr(VertexBackend,'__init__',lambda self,client_arg=None:setattr(self,'client',client))
    calibration=tokens.calibrate()
    freeze={'manifest_sha256':'test-freeze','gemini_calibration':calibration}
    (tmp_path/'freeze.json').write_text(packed(freeze))
    monkeypatch.setattr(p,'verify_freeze',lambda **_:freeze)
    return ledger,calibration,client,calls


def test_full_config_calibration_and_p1_unchanged(calibrated):
    ledger,calibration,client,calls=calibrated
    req=pf.smoke_request('pro')
    assert VertexBackend(client).count(req)==9  # P1's exact prior counter path.
    assert calls[-1]['config'].generation_config is None
    backend=tokens.P5VertexBackend(client,calibration=calibration)
    assert backend.count(req)==64
    _,wire=backend.wire(req)
    cfg=calls[-1]['config']
    assert cfg.system_instruction==wire.system_instruction and cfg.tools==wire.tools
    assert cfg.generation_config.response_mime_type==wire.response_mime_type=='application/json'
    assert cfg.generation_config.response_schema.properties['verdict'].enum==['unknown']
    assert cfg.generation_config.max_output_tokens==wire.max_output_tokens
    assert cfg.generation_config.thinking_config==wire.thinking_config
    entry=calibration['configs'][tokens.config_key(req)]
    assert entry['overhead_tokens']==47
    assert entry['samples'][0]['native_tokens']==17
    reply=Ledger(ledger,p.CAP).cached_reply(req)
    assert tokens.cached_count(req,reply,calibration)==(64,17,47)


@pytest.mark.parametrize('change',[
    {'messages':[{'role':'system','content':'new system'},{'role':'user','content':'same content'}]},
    {'response_schema':p.VERDICT_SCHEMA},
    {'response_schema':None},
    {'tools':[{'name':'check','parameters':{'type':'object','properties':{}}}]},
    {'max_output_tokens':512},
])
def test_never_extrapolate_to_different_config(calibrated,change):
    _,calibration,client,calls=calibrated
    backend=tokens.P5VertexBackend(client,calibration=calibration)
    before=len(calls)
    with pytest.raises(PreflightError,match='no frozen billing calibration'):
        backend.count(replace(pf.smoke_request('pro'),**change))
    assert len(calls)==before


def test_same_config_applies_to_every_new_prompt(calibrated):
    _,calibration,client,_=calibrated
    req=replace(pf.smoke_request('pro'),messages=[{'role':'user','content':'A longer user prompt.'}])
    client.models.count_tokens=lambda **kw:SimpleNamespace(total_tokens=200)
    assert tokens.P5VertexBackend(client,calibration=calibration).count(req)==247


def test_offline_smoke_reuses_exact_billing_without_calls(calibrated,monkeypatch):
    ledger,_,_,calls=calibrated
    # Also retain the Qwen smoke so the combined provider gate can pass.
    evidence=json.loads((Path(__file__).parent/'fixtures/p5_deepinfra_smoke.json').read_text())
    with ledger.open('a') as f:
        for k in ('reservation','completion'):f.write(packed(evidence[k])+'\n')
    before=ledger.read_bytes();count_calls=len(calls)
    class Counter:
        sha256='fixture'
        def __call__(self,wire):return 17
    monkeypatch.setattr(p,'native_counter',lambda **kw:Counter())
    for _ in range(2):
        result=pf.provider_smoke(0,cached_only=True)
        row=result['models']['pro']
        assert result['passed'] and result['generation_calls']==0
        assert row['count']==row['billed_input']==64
        assert row['native_count']==17 and row['overhead_tokens']==47
        assert row['reused_smoke'] and row['response_format']=='application/json; response_schema'
    assert ledger.read_bytes()==before and len(calls)==count_calls


def test_cached_count_rejects_changed_response_and_wire(calibrated):
    ledger,calibration,_,_=calibrated
    req=pf.smoke_request('pro');reply=Ledger(ledger,p.CAP).cached_reply(req)
    with pytest.raises(PreflightError,match='exact smoke'):
        tokens.cached_count(replace(req,messages=[{'role':'user','content':'changed'}]),reply,calibration)
    reply.response={'changed':True}
    with pytest.raises(PreflightError,match='exact smoke'):
        tokens.cached_count(req,reply,calibration)


def test_study_coverage_does_not_accept_smoke_as_calibration(calibrated,monkeypatch):
    req=replace(pf.smoke_request('pro'),response_schema=p.VERDICT_SCHEMA)
    monkeypatch.setattr(pf,'fixtures',lambda:iter([(req,0)]))
    report=tokens.coverage()
    assert not report['passed']
    assert not report['configs'][tokens.config_key(req)]['calibrated']


def test_count_preserves_system_schema_and_tools(calibrated):
    _,_,client,calls=calibrated
    req=replace(pf.smoke_request('pro'),
        messages=[{'role':'system','content':'Audit this.'},{'role':'user','content':'A claim'}],
        tools=[{'name':'check','parameters':{'type':'object','properties':{}}}])
    calibration={'configs':{tokens.config_key(req):{'overhead_tokens':47}}}
    assert tokens.P5VertexBackend(client,calibration=calibration).count(req)==64
    cfg=calls[-1]['config']
    assert cfg.system_instruction.parts[0].text=='Audit this.'
    assert cfg.tools[0].function_declarations[0].name=='check'
    assert cfg.generation_config.response_schema.properties['verdict'].enum==['unknown']
    assert calls[-1]['contents'][0].parts[0].text=='A claim'


@pytest.mark.parametrize('limit,passed',[(63,False),(64,True)])
def test_retained_bounds_apply_overhead_once_including_common(calibrated,monkeypatch,limit,passed):
    req=replace(pf.smoke_request('pro'),max_input_tokens=limit)
    row={'identity':req.identity,'model':'pro','wire_sha256':p.digest([req.messages,req.response_schema]),
         'count_wire_sha256':tokens.wire_key(req),'native_tokens':17,
         'tokens':64,'bounded_tokens':64,'generated_reserve':0,'passed':True}
    (p.HERE/'checks/tokenizer.json').write_text(packed({
        'counts':[row],'common_packet_counts':[row],'passed':True}))
    monkeypatch.setattr(pf,'fixtures',lambda:iter([(req,0)]))
    monkeypatch.setattr(p,'materials',lambda:[{}])
    monkeypatch.setattr(p,'request',lambda *a,**kw:req)
    monkeypatch.setattr(p,'native_counter',lambda **kw:SimpleNamespace(sha256='fixture'))
    for _ in range(2):
        result=pf.retained_tokens()
        assert result['passed']==passed
        for r in result['counts']+result['common_packet_counts']:
            assert r['tokens']==64 and r['overhead_tokens']==47
        assert result['counts'][0]['limit']==limit
        assert result['common_packet_counts'][0]['limit']==2048


def test_calibrated_runtime_bound_stops_before_generation(calibrated,monkeypatch):
    ledger,calibration,client,_=calibrated
    backend=tokens.P5VertexBackend(client,calibration=calibration)
    req=replace(pf.smoke_request('pro'),identity='new-request',max_input_tokens=63)
    # Undo the broad no-call guard to exercise PaidClient's real input guard.
    monkeypatch.undo()
    paid=PaidClient(backend,Ledger(ledger,p.CAP))
    before=ledger.read_bytes()
    try:
        with pytest.raises(PreflightError,match='joint input 64 exceeds 63'):
            paid.call(req)
    finally:
        paid.close()
    assert ledger.read_bytes()==before


def test_smokes_one_per_config_durable_cap_and_no_rebuy(tmp_path,monkeypatch):
    req=pf.smoke_request('pro')
    other=replace(req,max_output_tokens=512)
    monkeypatch.setattr(pf,'fixtures',lambda:iter([(req,0),(req,0),(other,0)]))
    calls=[]
    class Backend:
        def native_count(self,r):return 17
        async def generate(self,r):
            calls.append(r)
            return PaidReply('{}',64,5,0,0,MODELS['pro'],{}, {})
    book=Ledger(tmp_path/'costs.jsonl',p.CAP)
    assert tokens.calibration_smokes(book,Backend(),Decimal('.50'))==2
    assert len(calls)==2
    assert {tokens.config_key(r) for r in calls}=={tokens.config_key(req),tokens.config_key(other)}
    assert tokens.calibration_smokes(book,Backend(),Decimal('.50'))==0
    assert len(calls)==2
    with pytest.raises(PreflightError,match='<='):
        tokens.calibration_smokes(book,Backend(),Decimal('.51'))


def test_smoke_failure_holds_billing_and_never_retries(tmp_path,monkeypatch):
    req=pf.smoke_request('pro')
    monkeypatch.setattr(pf,'fixtures',lambda:iter([(req,0)]))
    calls=[]
    class Backend:
        def native_count(self,r):return 17
        async def generate(self,r):
            calls.append(r)
            raise TimeoutError('unknown billing')
    book=Ledger(tmp_path/'costs.jsonl',p.CAP)
    with pytest.raises(PreflightError,match='no retry'):
        tokens.calibration_smokes(book,Backend(),Decimal('.50'))
    with pytest.raises(PreflightError):
        tokens.calibration_smokes(book,Backend(),Decimal('.50'))
    assert len(calls)==1
