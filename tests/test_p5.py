"""P5 regression tests: no network, no paid dispatch, no review fabrication."""
from collections import Counter
from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from experiments import p5 as p
from experiments import p5_review as review
from experiments.p5_materials import read, structural_signature, argument_signature, archive, build, topology
from experiments.p5_analysis import endpoint, parse, known_answer, analyze, menu
from ve_experiments.paid import PreflightError, PaidReply, OfflineBackend, Ledger, PaidClient, digest, packed

@pytest.fixture(scope='module')
def items():return p.materials()

@pytest.fixture(scope='module')
def labels():return p.labels(False)


def test_inventory_graphs_and_witnesses(items,labels):
    from ve import ArgumentGraph,FiniteModel,check_countermodel,check_argument,evaluate
    assert len(items)==len(labels)==84
    assert Counter(i['split'] for i in items)=={'dev':12,'scored':72}
    assert Counter(l['predicates'] for l in labels if l['split']=='scored')=={20:24,40:24,60:24}
    graphs=read(p.HERE/'materials/graphs.jsonl.gz')
    signatures={};reference={};formal_signatures={}
    for row in graphs:
        family=row['slot']['cluster'];sig=structural_signature(row['topology'])
        assert signatures.setdefault(family,sig)==sig
        intended=ArgumentGraph.from_dict(row['intended'])
        assert formal_signatures.setdefault(family,argument_signature(intended))==argument_signature(intended)
        assert len(intended.deductions)==16 and len(intended.claims)==22
        assert len(intended.env.predicates)==row['slot']['predicates']
        assert len(row['predicate_identities'])==len(intended.env.predicates)
        model=FiniteModel.from_dict(intended.env,row['model'])
        leaves=intended.claims[:6];root=next(c for c in intended.claims if c.name==intended.root)
        assert all(evaluate(intended.env,c.ast,model) for c in leaves)
        assert check_countermodel(intended.env,[c.ast for c in leaves],root.ast,model).valid==row['negative']
        # One full compositional replay per variant, not thousands of duplicate tests.
        if row['slot']['variant'] not in reference:
            g=ArgumentGraph.from_dict(row['augmented']);r=check_argument(g,search=False).to_dict()
            assert not r['errors'] and all(v==['follows'] for v in r['findings'].values())
            reference[row['slot']['variant']]=True
    assert len(signatures)==len(set(signatures.values()))==28
    assert len(set(formal_signatures.values()))==28


def test_shared_packet_allowlist_and_isolation(items):
    item=deepcopy(items[0]);baseline=p.packet(item)
    item['label']='CANARY';item['payload']['_audit']={'answer':'CANARY'}
    assert p.packet(item)==baseline and 'CANARY' not in p.packet(item)
    assert 'CANARY' not in packed(p.request(item,'shared','paraphrase').messages)
    for arm in p.ARMS:
        r=p.request(item,arm,'lone' if arm=='L' else 'judge')
        assert baseline in r.messages[1]['content']
        assert r.response_schema==p.VERDICT_SCHEMA and r.max_output_tokens==1024
    with pytest.raises(PreflightError):p.request(item,'X','answer',history=[{'text':'sibling'}])
    r=p.request(item,'X','followup_answer',commitment='COMMIT',question='QUESTION')
    assert 'COMMIT' in r.messages[-1]['content'] and 'QUESTION' in r.messages[-1]['content']
    assert 'Protocol record:' not in r.messages[-1]['content']
    assert '/shift' not in r.identity


def test_caps_and_scenarios():
    assert max(o for _,o in p.STAGES.values())==1024
    for scenario in p.SCENARIOS:
        c=p.ceilings(scenario)
        assert Decimal(c['all_in_usd'])<40
        assert all(Decimal(v)<Decimal('.16') for v in c['attributed_item_arm_usd'].values())
    assert Decimal(p.ceilings('dual_judge')['all_in_usd'])==Decimal('34.7512920096')
    for cap in (0,-1,41):
        with pytest.raises(PreflightError):p.ledger(cap)


def test_offline_prose_is_honest_and_no_gold():
    rows=read(p.HERE/'materials/paraphrases.jsonl.gz')
    assert len(rows)==84
    assert all(r['provenance']['independent_qwen_pass'] is False for r in rows)
    from experiments.p5_paraphrase import offline_pass
    with pytest.raises(ValueError):offline_pass([{'label':'shift'}])


def test_review_blind_missing_and_hash_guard(tmp_path,items,labels):
    for split in ('dev','scored'):archive(tmp_path/f'materials/{split}.jsonl.gz',[i for i in items if i['split']==split])
    archive(tmp_path/'labels.jsonl.gz',labels)
    out=tmp_path/'review.json';review.review_export(out,tmp_path)
    rows=json.loads(out.read_text())
    assert len(rows)==84 and all('kind' not in r['packet'] for r in rows)
    assert not review.gate(tmp_path)['passed']
    with pytest.raises(PreflightError):review.submit(out,tmp_path)
    rows[0]['packet_sha256']='tampered';out.write_text(json.dumps(rows))
    with pytest.raises(PreflightError,match='hash'):review.submit(out,tmp_path)


def test_parser_localization_and_failures(items,labels):
    label=next(l for l in labels if l['kind']=='shift')
    item=next(i for i in items if i['id']==label['id'])
    ids=[n['id'] for n in item['payload']['nodes']+item['payload']['premises']]
    answer={'verdict':'reject','issue_type':'shift','locations':label['acceptable_locations'][0],'explanation':'records conflict'}
    assert parse(packed(answer),ids)==answer
    row={'ok':True,'answer':answer}
    assert endpoint(label,row,True)['detection']==1
    assert endpoint(label,row,False)['detection']==0
    assert endpoint(label,None,True)['unsafe_approval']==1
    for locations in ([ids[0]]*2,ids[:3],['invented']):
        with pytest.raises(ValueError):parse(packed({**answer,'locations':locations}),ids)
    assert len(menu(ids))==507


def test_known_answers_actual_scorer(items,labels):
    r=known_answer(items,labels)
    json.dumps(r)  # Gate receipts must remain serializable native JSON.
    assert r['passed'] and r['oracle_detection_and_completion']==1
    expected=sum(len(l['acceptable_locations']) for l in labels)/len(labels)/507
    assert r['random_exact']==pytest.approx(expected)
    assert abs(r['random_simulated']-expected)<.02
    for split in ('dev','scored'):
        primary=r['oracle_reports'][split]['judges']['pro']['primary']
        assert primary['boundary_safeguard'] and primary['interval'][0]<0<primary['interval'][1]


def test_assignment_integrity(items,labels):
    item=items[0]; row={'item_id':item['id'],'condition':'X','judge':'pro','group':item['group'],'split':item['split'],
        'sample':0,'packet_sha256':digest(item['payload']),'ok':False,'answer':{}}
    dev=[i for i in items if i['split']=='dev']
    with pytest.raises(PreflightError,match='missing'):analyze([row],dev,labels)
    with pytest.raises(PreflightError,match='duplicate'):analyze([row,row],dev,labels,allow_missing=True)
    with pytest.raises(PreflightError,match='hash'):analyze([{**row,'packet_sha256':'bad'}],dev,labels,allow_missing=True)


class RecordingClient:
    def __init__(self,callback):
        self.callback=callback;self.requests=[];self.backend=SimpleNamespace(count=lambda req:len(req.messages[-1]['content'].split()))
    def call(self,req):
        self.requests.append(req)
        return SimpleNamespace(text=packed(self.callback(req)))


def test_x_full_protocol_fresh_copies(items):
    def response(req):
        role=req.metadata['role']
        if role=='author':return {'commitment':'frozen meanings','argument':'SECRET_FULL_DEFENSE'}
        if role=='critic':return {'questions':['q1','q2','q3']}
        if role=='followup':return {'question':'adaptive'}
        if role in ('answer','followup_answer'):return {'response':'PRIVATE_'+str(req.metadata['turn'])}
        return {'verdict':'unknown','issue_type':'unknown','locations':[],'explanation':'uncertain'}
    client=RecordingClient(response);rows=p.execute(items[0],'X',client,{'pro':client})
    assert len(rows)==1
    assert Counter(r.metadata['role'] for r in client.requests)=={'author':1,'critic':1,'answer':3,'followup':1,'followup_answer':1,'judge':1}
    for req in client.requests:
        if req.metadata['role'] in ('answer','followup_answer'):
            text=packed(req.messages)
            assert 'PRIVATE_' not in text and 'SECRET_FULL_DEFENSE' not in text
    assert 'PRIVATE_' in packed(client.requests[-1].messages)


def test_ve_one_repair_no_gold(items,monkeypatch):
    import experiments.p5_oracle as oracle
    monkeypatch.setattr(oracle,'bounded',lambda *a,**k:{'ok':False,'error':'bad artifact','elapsed_s':.01,'status':'UNKNOWN'})
    def response(req):
        if req.metadata['role']=='judge':return {'verdict':'unknown','issue_type':'unknown','locations':[],'explanation':'unresolved'}
        return {'queries':[],'splits':[]}
    client=RecordingClient(response);rows=p.execute(items[0],'VE',client,{'pro':client})
    assert sum(r.metadata['role']=='repair' for r in client.requests)==1
    assert rows[0]['author_failure'] and rows[0]['unresolved'] and rows[0]['oracle_unknown']
    assert 'predicate_identities' not in packed([r.messages for r in client.requests])
    final=client.requests[-1].messages[-1]['content']
    assert '"stage":"author"' in final and '"stage":"repair"' in final


def test_ledger_reuses_without_paid_replacement(tmp_path,items):
    req=p.request(items[0],'L','lone');count=[0]
    def reply(request):count[0]+=1;return '{"verdict":"unknown"}'
    book=Ledger(tmp_path/'costs.jsonl',1)
    client=PaidClient(OfflineBackend(reply),book,reuse_completed=True)
    try:
        first=client.call(req);second=client.call(req)
    finally:client.close()
    assert count==[1] and first.text==second.text


def test_oracle_requires_commitment_and_exact_record(items):
    from experiments.p5_oracle import query
    graph=read(p.HERE/'materials/graphs.jsonl.gz')[0]['intended']
    committed={'environment':graph['environment'],'claims':[{'id':c['name'],'source':c['source']} for c in graph['claims']]}
    with pytest.raises(ValueError):query({'committed':committed,'packet':items[0]['payload'],
        'query':{'claim_id':committed['claims'][0]['id'],'environment_id':'wrong','committed_source':'wrong'}})


def test_sibling_glossaries_and_workload_identical(items):
    for family in {i['group'] for i in items}:
        siblings=[i['payload'] for i in items if i['group']==family]
        assert len({packed(sorted((g['term'], g['sense'].split(' (R')[0]) for g in s['glossary'])) for s in siblings}) == 1
        assert len({digest([(n['id'],n['parents']) for n in s['nodes']]) for s in siblings})==1
        assert len({digest(s['records']) for s in siblings})==1
        assert len({packed(s['nodes']) for s in siblings})==3
        assert all('argument' not in s for s in siblings)
        assert all('rule_record' not in n for s in siblings for n in s['nodes'])
        assert all(len(s['nodes'])==16 and len(s['records'])==16 and len(s['premises'])==6 for s in siblings)


def test_replication_halt_does_not_erase_primary(items):
    from ve_experiments.paid import InfrastructureError
    primary=RecordingClient(lambda r:{'verdict':'unknown','issue_type':'unknown','locations':[],'explanation':'uncertain'})
    class Halt:
        def call(self,req):raise InfrastructureError('panel halted')
    result=p.execute(items[0],'L',primary,{'pro':primary,'replication':Halt()})
    assert len(result)==1 and result[0]['judge']=='pro'


def test_local_resume_reuses_durable_diagnostics(items,monkeypatch):
    import experiments.p5_oracle as oracle
    calls=[];durable=[]
    def bounded(*args,**kwargs):
        calls.append(args);return {'ok':False,'status':'UNKNOWN','error':'fixture','elapsed_s':.1}
    monkeypatch.setattr(oracle,'bounded',bounded)
    def response(req):
        return {'verdict':'unknown','issue_type':'unknown','locations':[],'explanation':'uncertain'} if req.metadata['role']=='judge' else {'queries':[],'splits':[]}
    first=RecordingClient(response);p.execute(items[0],'VE',first,{'pro':first},event_sink=durable.append)
    n=len(calls)
    second=RecordingClient(response);p.execute(items[0],'VE',second,{'pro':second},local_cache=durable)
    assert len(calls)==n
    assert [r.messages for r in first.requests]==[r.messages for r in second.requests]


def test_author_failure_is_assigned_failure(labels):
    l=next(l for l in labels if l['kind']=='shift')
    r={'ok':True,'author_failure':True,'answer':{'verdict':'reject','issue_type':'shift','locations':l['acceptable_locations'][0]}}
    assert endpoint(l,r,True)['score']==0


def test_item_arm_ceiling_includes_infrastructure_holds(tmp_path,items):
    book=p.P5Ledger(tmp_path/'costs.jsonl',40);req=p.request(items[0],'L','lone')
    with book.locked() as (f,_):
        book.append(f,{'event':'reserve','identity':'prior','metadata':req.metadata,'ceiling_usd':'.15','model':'pro'})
        book.append(f,{'event':'infrastructure_failure','identity':'prior','infrastructure_hold_usd':'.15'})
    from ve_experiments.paid import BudgetExceeded
    with pytest.raises(BudgetExceeded,match='item-arm'):book.reserve(req)


def test_rendered_prose_and_active_decoys(items):
    graphs={r['id']:r for r in read(p.HERE/'materials/graphs.jsonl.gz')}
    for item in items:
        q=item['payload']; g=graphs[item['id']]
        assert g['construction']['version']==3
        assert len(g['construction']['redundant_edges'])>=1
        for n in q['nodes']:
            assert p.packet(item).count(n['text']) == 1
            assert n['text'].startswith(('Given ', 'From ', 'Using ')) and ', ' in n['text']
        from ve import ArgumentGraph
        graph=ArgumentGraph.from_dict(g['intended'])
        claims={c.name:c for c in graph.claims}
        decoys=[claims[n].source for n in g['construction']['decoy_nodes']]
        assert len(set(decoys))==4
        # Both critical predicates are independently concluded on a comparison
        # lot in every variant, so predicate-orphan counts cannot identify it.
        comparisons=[claims[n].source for n in g['construction']['comparison_nodes']]
        assert len(set(comparisons))==2
        import re
        assert set(re.findall(r'p\d+',g['bridge']['source'])) <= set(re.findall(r'p\d+',' '.join(comparisons)))
        assert 'argument' not in q
        assert 'Possible senses' not in p.packet(item)
        assert 'rule_record' not in p.packet(item)
        assert 'rule_record' not in packed(p.request(item,'shared','paraphrase').messages)


def test_export_is_reproducible_and_not_variant_order(tmp_path,items,labels):
    for split in ('dev','scored'):
        archive(tmp_path/f'materials/{split}.jsonl.gz',[i for i in items if i['split']==split])
    out=tmp_path/'review.json';review.review_export(out,tmp_path)
    rows=json.loads(out.read_text()); first=out.read_bytes()
    kinds={l['id']:l['kind'] for l in labels}
    assert all(len({kinds[r['item_id']] for r in rows[k::3]})==3 for k in range(3))
    # Reversing the input archives cannot alter the seeded export.
    for split in ('dev','scored'):
        archive(tmp_path/f'materials/{split}.jsonl.gz',list(reversed([i for i in items if i['split']==split])))
    review.review_export(out,tmp_path)
    assert out.read_bytes()==first


def test_review_cannot_bypass_failed_leakage(tmp_path,items,labels,monkeypatch):
    import experiments.p5_leakage as leakage
    for split in ('dev','scored'):
        archive(tmp_path/f'materials/{split}.jsonl.gz',[i for i in items if i['split']==split])
    archive(tmp_path/'labels.jsonl.gz',labels)
    monkeypatch.setattr(leakage,'audit',lambda base:{'passed':False,'accuracy':1.0})
    result=review.gate(tmp_path)
    assert result['leakage_passed'] is False and result['passed'] is False
    assert json.loads((tmp_path/'checks/leakage.json').read_text())['accuracy']==1.0


def test_sibling_token_and_structure_workload(items):
    import re
    from experiments.p5_leakage import feature_row
    for family in {i['group'] for i in items}:
        siblings=[i for i in items if i['group']==family]
        # Opaque item identity is the only unigram difference. Content-role
        # assignment in the prose carries the label, not token frequency.
        bags=[Counter(re.findall(r'(?u)\b\w+\b', packed({k:v for k,v in i['payload'].items() if k!='id'}).lower())) for i in siblings]
        assert bags[0]==bags[1]==bags[2]
        assert feature_row(siblings[0],0)==feature_row(siblings[1],1)==feature_row(siblings[2],2)


def test_adjudication_excludes_superseded_packets(tmp_path,items,monkeypatch):
    item=items[0]; annotation={'kind':'benign'}
    archive(tmp_path/f"materials/{item['split']}.jsonl.gz",[item])
    current=[{'event':'review','item_id':item['id'],'packet_sha256':digest(item['payload']),
              'reviewer_id':r,'annotation':annotation} for r in ('test-a','test-b')]
    old={**current[0],'packet_sha256':'superseded','reviewer_id':'historical'}
    archive(tmp_path/'materials/review-ledger.jsonl.gz',[old,*current])
    resolution={'item_id':item['id'],'packet_sha256':digest(item['payload']),
                'adjudicator':'test-only','reason':'fixture','source_evidence':['fixture'],
                'review_digests':[digest(r) for r in current],'annotation':annotation}
    path=tmp_path/'resolution.json';path.write_text(json.dumps(resolution))
    monkeypatch.setattr(review,'gate',lambda base:{'test_only':True})
    assert review.adjudicate(path,tmp_path)=={'test_only':True}
    resolution['packet_sha256']='superseded';path.write_text(json.dumps(resolution))
    with pytest.raises(PreflightError,match='current packet'):
        review.adjudicate(path,tmp_path)


def test_replacement_ids_do_not_reuse_disclosed_labels(items):
    rejected=read(p.HERE/'materials/rejected-v1.jsonl.gz')
    assert len(rejected)==84
    assert not {i['id'] for i in items} & {i['id'] for i in rejected}


def test_node_relations_cover_balanced_units_and_independent_sense_orders(items, labels):
    from experiments.p5_leakage import node_features
    kinds = {l['id']: l['kind'] for l in labels}
    counts = Counter()
    for item in items:
        f = node_features(item['payload'])
        assert f['branch_n_alts'] == 3
        assert f['branch_con_sense_id'] > 0
        assert f['branch_con_sense_rank'] in (0, 2)
        counts[kinds[item['id']], f['branch_con_unit_is_sample']] += 1
    assert counts == Counter({(k, u): 14 for k in ('benign', 'shift', 'smuggle') for u in (0, 1)})
    for family in {i['group'] for i in items}:
        glossaries = [i['payload']['glossary'] for i in items if i['group'] == family]
        assert len({packed(sorted(g['sense'] for g in gs)) for gs in glossaries}) == 3
        assert len({packed([g['sense'].split(' (R')[0] for g in gs]) for gs in glossaries}) == 3
    corrupt = deepcopy(items[0]['payload'])
    corrupt['nodes'][0]['text'] = 'Unparsed prose must block the gate, never silently lose a node.'
    with pytest.raises(ValueError, match='unparsed inference'):
        node_features(corrupt)
