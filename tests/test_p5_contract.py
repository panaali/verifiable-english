"""V9 contract/coverage separation and actual provider wire regressions, $0."""
import asyncio
from dataclasses import replace
import json
from types import SimpleNamespace

import httpx
import pytest

from experiments import p5 as p, p5_contract as audit
from experiments.p5_analysis import contract_report, endpoint, parse
from experiments.p5_materials import read
from ve_experiments import paid


def test_ledger_diagnosis_all_fifteen_responses():
    report=audit.audit()
    assert report['dev_completions']==15 and report['judge_completions']==8
    assert report['dev_cost_usd']=='0.1476830522'
    assert report['missing_judgments']==88
    c=report['counts']
    assert c['truncation']==6 and c['ve_truncation']==4
    assert c['judge_truncation']==c['s_author_truncation']==c['non_node_locations']==1
    assert c['output_cap_exceeded']==1 and c['allowed_unknown_verdicts']==2
    assert all(c[k]==0 for k in ('extra_fields','missing_fields','verdict_vocabulary',
        'issue_type_vocabulary','judge_schema_not_attached','empty_or_nonstring_explanation'))
    assert sum(o['legacy_contract_ok'] is True for o in report['responses'])==6


@pytest.mark.parametrize('locations',[[],['r02'],['not_a_node'],['n00']])
def test_wrong_and_missing_localization_are_scored_failures(locations):
    answer={'verdict':'reject','issue_type':'shift','locations':locations,'explanation':'records conflict'}
    answer=parse(json.dumps(answer),['n00','n01'])
    label={'kind':'shift','acceptable_locations':[['n00','n01']]}
    outcome=endpoint(label,{'ok':True,'answer':answer},True)
    assert outcome['score']==0 and outcome['failed']==0


def test_unknown_is_valid_but_unsuccessful_and_long_explanation_is_valid():
    answer={'verdict':'unknown','issue_type':'unknown','locations':[],'explanation':'x'*10000}
    assert parse(json.dumps(answer),[])==answer
    for kind in ('benign','shift'):
        assert endpoint({'kind':kind,'acceptable_locations':[['n00']]},
                        {'ok':True,'answer':answer},True)['score']==0
    for bad in ({**answer,'extra':0},{**answer,'verdict':'yes'},{**answer,'explanation':' '},
                {**answer,'locations':['n00','n00']},{**answer,'locations':[1]},[]):
        with pytest.raises(ValueError):parse(json.dumps(bad),['n00'])


def test_compliance_separates_missing_from_malformed_and_keeps_gate_closed():
    rows=read(p.HERE/'runs/dev/trials.jsonl')
    r=contract_report(rows,48,('pro','replication'))
    assert r['contract_compliance']=={'pro':.5,'replication':1.0}
    assert r['assigned_valid_fraction']=={'pro':2/48,'replication':4/48}
    assert not r['coverage_passed'] and not r['contract_passed']
    assert contract_report([],48,('pro',))['contract_compliance']['pro'] is None


def test_finish_truncation_fails_even_when_json_is_complete():
    answer={'verdict':'unknown','issue_type':'unknown','locations':[],'explanation':'uncertain'}
    client=SimpleNamespace(call=lambda _:SimpleNamespace(text=json.dumps(answer),finish_reason='MAX_TOKENS'))
    row=p.execute(p.materials('dev')[0],'L',client,{'pro':client})[0]
    assert not row['ok'] and row['error']=='truncated judgment: MAX_TOKENS'


def test_audit_prefix_is_immutable():
    import hashlib
    report=audit.audit()
    prefix=(p.HERE/'runs/study/costs.jsonl').read_bytes()[:report['ledger_prefix_bytes']]
    assert hashlib.sha256(prefix).hexdigest()==report['ledger_prefix_sha256']
    assert report['ledger_prefix_sha256']=='d52a861a041e6e1cefe2d928a9f63a4ade68b59e650c0179eccf448dbe5fa091'


def test_schemas_reach_actual_generate_calls_on_both_providers(monkeypatch):
    item=p.materials('dev')[0]
    captured=[]
    class Models:
        async def generate_content(self,**kw):
            captured.append(kw)
            # Fail after capturing the real transport arguments, before parsing.
            raise RuntimeError('captured Vertex wire')
    req=p.request(item,'L','lone')
    backend=paid.VertexBackend(SimpleNamespace(aio=SimpleNamespace(models=Models())))
    with pytest.raises(RuntimeError,match='captured Vertex'):
        asyncio.run(backend.generate(req))
    cfg=captured[0]['config']
    assert cfg.response_mime_type=='application/json'
    assert cfg.response_schema==p.VERDICT_SCHEMA
    assert cfg.max_output_tokens==4096
    assert cfg.thinking_config.thinking_level=='LOW'
    monkeypatch.setenv('OPENROUTER_API_KEY','offline-test')
    wires=[]
    def capture(request):
        wires.append(json.loads(request.content))
        return httpx.Response(400,json={'error':'json_schema unsupported'})
    original=httpx.AsyncClient
    monkeypatch.setattr(httpx,'AsyncClient',lambda **kw:original(transport=httpx.MockTransport(capture)))
    with pytest.raises(paid.InfrastructureError):
        asyncio.run(paid.OpenRouterBackend().generate(p.request(item,'L','lone',judge='replication')))
    assert len(wires)==1  # P5 must not silently degrade to schema-less JSON mode.
    assert wires[0]['response_format']['json_schema']['schema']==p.VERDICT_SCHEMA
    assert wires[0]['response_format']['json_schema']['strict'] is True


def test_v9_caps_history_reserves_and_no_legacy_cache_reuse():
    from experiments.p5_preflight import fixtures
    item=p.materials('dev')[0]
    for stage in ('author','repair','critic','defender','judge'):
        r=p.request(item,'VE',stage)
        assert r.max_output_tokens==r.billed_output_cap==4096
        assert r.identity.startswith('study-v9/dev/')
    assert p.run_path('dev','trials.jsonl')!=p.HERE/'runs/dev/trials.jsonl'
    pairs=[(r,n) for r,n in fixtures() if r.metadata['item_id']==item['id'] and r.metadata['arm']=='VE']
    assert next(n for r,n in pairs if r.metadata['role']=='judge')==4*4096+1024
    assert next(n for r,n in pairs if r.metadata['role']=='defender')==3*4096+512


def test_supersession_is_narrow_append_only_and_preserves_spend(tmp_path):
    rows=read(p.HERE/'runs/study/costs.jsonl')
    # Recreate pre-amendment ledger, even after the real recovery has run.
    rows=[r for r in rows if r['event']!='p5_dev_cap_recovery' and not
          (r['event']=='block_release' and r['block_id']=='dual_judge/dev')]
    path=tmp_path/'costs.jsonl';path.write_text(''.join(paid.packed(r)+'\n' for r in rows))
    book=p.P5Ledger(path,p.CAP);before=path.read_bytes();spent=book.state(rows)[1]
    book.supersede_dev()
    after=path.read_bytes();assert after.startswith(before)
    assert book.state(read(path))[1]==spent
    assert not p.infrastructure_state(book)[1]
    assert 'block:dual_judge/dev' not in book.state(read(path))[0]
    book.supersede_dev();assert path.read_bytes()==after
    # A new 4096 overrun remains a blocking halt.
    halt=next(r for r in rows if r['event']=='panel_validation_halt')
    p.append(path,{**halt,'time':halt['time']+1,'identity':'study-v9/'+halt['identity']})
    book.supersede_dev()
    assert p.infrastructure_state(book)[1]
