"""Retained P5 smoke and exact paraphrase wire: no providers or downloads."""
import asyncio
from copy import deepcopy
import json
from pathlib import Path

import httpx
import pytest

from experiments import p5 as p
from experiments import p5_preflight as pf
from experiments.p5_materials import read
from ve_experiments.paid import OpenRouterBackend, PaidClient, digest, packed

EVIDENCE = Path(__file__).parent/'fixtures/p5_deepinfra_smoke.json'


@pytest.fixture
def retained(tmp_path, monkeypatch):
    evidence=json.loads(EVIDENCE.read_text())
    ledger=tmp_path/'runs/study/costs.jsonl'
    ledger.parent.mkdir(parents=True)
    ledger.write_text('\n'.join(packed(evidence[k]) for k in ('reservation','completion'))+'\n')
    monkeypatch.setattr(p,'HERE',tmp_path)
    monkeypatch.setattr(p,'verify_freeze',lambda:{'manifest_sha256':'test-freeze'})
    monkeypatch.setattr(PaidClient,'call',lambda *a,**kw:pytest.fail('generation forbidden'))
    monkeypatch.setattr(httpx,'get',lambda *a,**kw:pytest.fail('downloads forbidden'))
    return ledger,evidence


def cached_counter():
    counter=p.native_counter(cached_only=True)
    source=counter.native.sources[p.MODELS['replication']]['files']['tokenizer.json']
    if not (counter.native.cache/(source['git_blob_sha1']+'.json')).exists():
        pytest.skip('pinned Qwen tokenizer not cached; never download')
    return counter


def test_recorded_smoke_exact_count_and_idempotence(retained):
    ledger,evidence=retained
    counter=cached_counter()
    req=pf.smoke_request('replication')
    wire=OpenRouterBackend(counter).wire(req)
    assert counter(wire)==17
    # Render the untouched HF template through the same implementation.
    counter.native.sources['upstream-template']=counter.native.sources[p.MODELS['replication']]
    counter.native.loaded['upstream-template']=counter.native.loaded[p.MODELS['replication']]
    assert counter({**wire,'model':'upstream-template'})==38
    assert counter({k:v for k,v in wire.items() if k!='response_format'})==17
    assert digest(req.messages)==evidence['reservation']['prompt_sha256']==(
        '3f8c59a0e68023eb1c5bda8090fa898a1175f258ac1ec3da37a8a60ae61d0a0d')
    before=ledger.read_bytes()
    first=pf.provider_smoke(0,only_openrouter=True,cached_only=True)
    assert first==pf.provider_smoke(0,only_openrouter=True,cached_only=True)
    assert ledger.read_bytes()==before
    row=first['models']['replication']
    assert row['passed'] and row['reused_smoke']
    assert row['count']==row['billed_input']==17
    assert row['billed_output']==11 and row['response_format']=='json_schema'
    assert first['generation_calls']==0 and first['requested_models_passed']
    assert not first['passed']  # Full provider gate still needs Gemini evidence.


@pytest.mark.parametrize('cached_only',[True,False])
def test_smoke_rechecks_passed_receipt_and_keeps_mismatched_reply(retained,monkeypatch,cached_only):
    ledger,_=retained
    class Counter:
        sha256='test-counter'
        def __call__(self,wire):return 38
    monkeypatch.setattr(p,'native_counter',lambda **kw:Counter())
    receipt=p.HERE/'checks/provider-preflight.json'
    receipt.parent.mkdir()
    receipt.write_text(packed({'freeze_sha256':'test-freeze','models':{'replication':{'passed':True}}}))
    before=ledger.read_bytes()
    result=pf.provider_smoke(.01,only_openrouter=True,cached_only=cached_only)
    row=result['models']['replication']
    assert row['count']==38 and row['billed_input']==17 and not row['passed']
    assert row['reused_smoke'] and ledger.read_bytes()==before


@pytest.mark.parametrize('change',['missing','messages','max_output_tokens','response_schema','tools'])
def test_cached_smoke_missing_or_changed_fails_closed(retained,monkeypatch,change):
    ledger,evidence=retained
    class Counter:
        sha256='test-counter'
        def __call__(self,wire):return 17
    monkeypatch.setattr(p,'native_counter',lambda **kw:Counter())
    if change=='missing':ledger.write_text('')
    else:
        evidence['reservation'][change]=None
        ledger.write_text('\n'.join(packed(evidence[k]) for k in ('reservation','completion'))+'\n')
    before=ledger.read_bytes()
    result=pf.provider_smoke(0,only_openrouter=True,cached_only=True)
    assert not result['models']['replication']['passed']
    assert 'cached smoke' in result['models']['replication']['error']
    assert result['generation_calls']==0 and ledger.read_bytes()==before


def test_cli_forwards_offline_without_spending_cap(monkeypatch):
    calls=[]
    monkeypatch.setattr(pf,'provider_smoke',lambda *a,**kw:calls.append((a,kw)) or
                        {'passed':False,'requested_models_passed':True})
    assert p.main(['preflight-openrouter','--offline'])==0
    assert calls==[((0,),{'only_openrouter':True,'cached_only':True})]


def test_retained_fixture_recounts_native_and_rejects_uncalibrated_vertex(tmp_path,monkeypatch):
    from dataclasses import replace
    req=pf.smoke_request('replication')
    vertex=replace(req,identity='vertex-fixture',model='pro')
    rows=[{'identity':r.identity,'wire_sha256':digest([r.messages,r.response_schema]),
           'generated_reserve':0,'tokens':38,'bounded_tokens':38,'passed':True}
          for r in (req,vertex)]
    path=tmp_path/'checks/tokenizer.json';path.parent.mkdir()
    path.write_text(packed({'counts':rows,'common_packet_counts':[{'passed':True}],
                           'counter_sha256':'old','passed':True}))
    monkeypatch.setattr(p,'HERE',tmp_path)
    monkeypatch.setattr(p,'verify_freeze',lambda:{'gemini_calibration':{'configs':{}}})
    monkeypatch.setattr(p,'materials',lambda:[])
    monkeypatch.setattr(pf,'fixtures',lambda:iter([(req,0),(vertex,0)]))
    class Counter:
        sha256='new'
        def __call__(self,wire):
            assert wire['model']==p.MODELS['replication']
            return 17
    monkeypatch.setattr(p,'native_counter',lambda **kw:Counter())
    result=pf.retained_tokens()
    assert not result['passed'] and result['counter_sha256']=='new'
    assert result['native_recounts']==1 and result['generation_calls']==0
    assert result['counts'][0]['tokens']==17
    assert not result['counts'][1]['passed']
    assert 'no frozen billing calibration' in result['counts'][1]['error']
    rows[1]['wire_sha256']='stale';path.write_text(packed({'counts':rows}))
    monkeypatch.setattr(pf,'prose_token_fit',lambda:{'passed':True,'ranges':{}})
    assert not pf.retained_tokens()['passed']


def test_paraphrase_count_receives_exact_generation_wire(monkeypatch):
    counter=cached_counter()
    dossier=read(p.HERE/'materials/dossiers.jsonl.gz')[0]
    req=p.request({'id':dossier['id'],'split':'materials','payload':dossier},'shared','paraphrase')
    counted=[];sent=[]
    def count(wire):
        counted.append(deepcopy(wire))
        return counter(wire)
    backend=OpenRouterBackend(count)
    n=backend.count(req)
    assert n<=4096
    assert [m['role'] for m in counted[0]['messages']]==['system','user']
    assert counted[0]['messages']==req.messages
    assert counted[0]['max_tokens']==1024
    assert 'response_format' not in counted[0] and 'tools' not in counted[0]
    response=json.loads(EVIDENCE.read_text())['completion']['response']
    def capture(request):
        sent.append(json.loads(request.content))
        return httpx.Response(200,json=response)
    original=httpx.AsyncClient
    monkeypatch.setenv('OPENROUTER_API_KEY','offline-fixture')
    monkeypatch.setattr(httpx,'AsyncClient',lambda **kw:original(transport=httpx.MockTransport(capture)))
    asyncio.run(backend.generate(req))
    assert counted==sent
    # An explicit system prompt means the shared-template correction leaves
    # every paraphrase's input count unchanged from the upstream template.
    tokenizer,config=counter.native.loaded[p.MODELS['replication']]
    import importlib.util
    spec=importlib.util.spec_from_file_location('counter_for_test',counter.path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    for dossier in read(p.HERE/'materials/dossiers.jsonl.gz'):
        req=p.request({'id':dossier['id'],'split':'materials','payload':dossier},'shared','paraphrase')
        wire=backend.wire(req)
        upstream=module.chat_text({**wire,'model':'upstream-template'},config)
        assert counter(wire)==len(tokenizer.encode(upstream,add_special_tokens=False).ids)
