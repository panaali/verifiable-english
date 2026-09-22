"""P5 evidence gates. Free counters never perform generation."""
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys

from experiments import p5 as p
from experiments.p5_materials import read, write_json, archive
from ve_experiments.paid import PaidRequest, PaidClient, Ledger, VertexBackend, OpenRouterBackend, digest, packed, PreflightError


def fixtures():
    """Exact base wire plus explicit generated-output reserves, counted again live."""
    for item in p.materials():
        for arm in p.ARMS:
            author=p.STAGES['author'][1]; critic=p.STAGES['critic'][1]
            for stage in dict.fromkeys(p.stage_list(arm)):
                if stage in ('answer','followup_answer'):
                    req=p.request(item,arm,stage,commitment='',question='')
                    reserve=512+256
                else:
                    reserve={'author':0,'lone':0,'repair':author+512,'critic':author+512 if arm=='VE' else author,
                        'defender':author+critic+(p.STAGES['repair'][1]+512 if arm=='VE' else 0),
                        'followup':author+critic+3*512,
                        'judge':author+critic+(3*512+256+512 if arm=='X' else 1024)+
                            (p.STAGES['repair'][1]+1024 if arm=='VE' else 0)}[stage]
                    req=p.request(item,arm,stage,history=[{'item_id':item['id'],'stage':'reserved_history','text':''}] if reserve else None)
                yield req,reserve
                if stage in ('judge','lone'):
                    yield p.request(item,arm,stage,history=[{'item_id':item['id'],'stage':'reserved_history','text':''}] if reserve else None,judge='replication'),reserve
        dossier=next(d for d in read(p.HERE/'materials/dossiers.jsonl.gz') if d['id']==item['id'])
        yield p.request({'id':item['id'],'split':'materials','payload':dossier},'shared','paraphrase'),0


def tokenize():
    native=p.native_counter(); vertex=VertexBackend(); router=OpenRouterBackend(native)
    def count(pair):
        req,reserve=pair
        try:
            n=(vertex if req.model=='pro' else router).count(req)
            return {'identity':req.identity,'model':req.model,'wire_sha256':digest([req.messages,req.response_schema]),
                'tokens':n,'generated_reserve':reserve,'bounded_tokens':n+reserve,'limit':req.max_input_tokens,
                'passed':n+reserve<=req.max_input_tokens,'source':'Vertex count_tokens (free)' if req.model=='pro' else 'pinned native Qwen chat template'}
        except Exception as exc:
            return {'identity':req.identity,'model':req.model,'passed':False,'error':str(exc)}
    pairs=list(fixtures())
    # Native tokenizer loading is serial; only Vertex countTokens is concurrent.
    native_rows=[count(x) for x in pairs if x[0].model!='pro']
    with ThreadPoolExecutor(max_workers=8) as pool:
        vertex_rows=list(pool.map(count,[x for x in pairs if x[0].model=='pro']))
    # Common packet + judgment envelope must itself fit 2048, not just stage cap.
    common=[]
    with ThreadPoolExecutor(max_workers=8) as pool:
        common=list(pool.map(lambda i:count((p.request(i,'L','lone'),0)),p.materials()))
    for row in common:
        row['limit']=2048;row['passed']=row.get('tokens',10**9)<=2048
    return {'passed':all(r['passed'] for r in native_rows+vertex_rows+common),
        'counts':native_rows+vertex_rows,'common_packet_counts':common,'generation_calls':0,
        'counter_sha256':native.sha256,
        'scope':'all slots/arms/stages, system/schema included; max prior-output reserves; exact runtime recount; no truncation'}


def inventory(count_tokens=False):
    result={'slot_count':84,'slots':[{k:r[k] for k in ('id','family','split','predicates')} for r in p.labels(False)],'composition':{'dev':12,'scored':72,'scored_families':24,
        'scored_per_variant':24,'scored_families_per_predicate_count':{'20':8,'40':8,'60':8}},
        'scenario_ceilings':{s:p.ceilings(s) for s in p.SCENARIOS},
        'original_design_inventory':'inventory.json (UNBUILT aggregate design; slot labels removed in v5)',
        'stage_caps':p.STAGES,'token_counts':None,'material_status':'OFFLINE_DRAFT_REQUIRES_QWEN_AND_REVIEW'}
    if count_tokens:
        counts=tokenize();write_json(p.HERE/'checks/tokenizer.json',counts)
        result['token_counts']=counts
    elif (p.HERE/'checks/tokenizer.json').exists():
        result['token_counts']=json.loads((p.HERE/'checks/tokenizer.json').read_text())
    write_json(p.HERE/'execution-inventory.json',result)
    return {k:v for k,v in result.items() if k not in ('token_counts','slots')} | {'tokenizer_passed':(result['token_counts'] or {}).get('passed')}


def lean_replay():
    from ve import ArgumentGraph, FiniteModel, check_countermodel, check_argument, formula_to_data
    exe=p.ROOT/'lean/.lake/build/bin/ve_conformance'
    if not exe.exists():raise PreflightError('lake build required')
    entries=[]
    labels={r['id']:r for r in p.labels(False)}
    for row in read(p.HERE/'materials/graphs.jsonl.gz'):
        for role in ('merged','augmented','intended'):
            g=ArgumentGraph.from_dict(row[role]); by_id={c.name:c for c in g.claims};queries=[]
            if role=='intended' and labels[row['id']]['kind'] != 'benign':
                premises=[c.ast for c in g.claims[:6]];root=by_id[g.root].ast
                model=FiniteModel.from_dict(g.env,row['model'])
                if not check_countermodel(g.env,premises,root,model).valid:
                    raise PreflightError('Python root witness failed')
                query={'id':row['id']+'/whole-premise-witness','environment':g.env.to_dict(),
                    'premises':[formula_to_data(g.env,c) for c in premises],
                    'conclusion':formula_to_data(g.env,root),'kind':'countermodel','model':row['model']}
                commands=[('countermodel',[query])]
            else:
                checked=check_argument(g,search=False).to_dict()
                if checked['errors'] or any(v!=['follows'] for v in checked['findings'].values()):
                    raise PreflightError('Python certificate replay failed')
                for edge in g.deductions:
                    for certificate in edge.certificates:
                        queries.append({'id':row['id']+'/'+role+'/'+edge.name,'environment':g.env.to_dict(),
                            'premises':[formula_to_data(g.env,by_id[n].ast) for n in edge.premises],
                            'conclusion':formula_to_data(g.env,by_id[edge.conclusion].ast),'certificate':certificate['proof']})
                commands=[('certificate',queries)]
            for kind,queries in commands:
                proc=subprocess.run([str(exe),*(['check-certificate'] if kind=='certificate' else [])],
                    input=packed(queries),text=True,capture_output=True,timeout=60)
                responses=json.loads(proc.stdout)
                if len(responses)!=len(queries):raise PreflightError('Lean response join mismatch')
                for query,response in zip(queries,responses,strict=True):
                    passed=proc.returncode==0 and response.get('status')=='ok' and response.get('valid' if kind=='certificate' else 'refutes') is True
                    entries.append({'item_id':row['id'],'kind':kind,'query_sha256':digest(query),
                                    'artifact_sha256':digest(row[role]),'response':response,'passed':passed})
                    if not passed:raise PreflightError('Python/Lean disagreement')
    archive(p.HERE/'checks/lean-replay-ledger.jsonl.gz',entries)
    return {'passed':True,'queries':len(entries),'items':84,'executable_sha256':p.sha(exe),
            'ledger_sha256':p.sha(p.HERE/'checks/lean-replay-ledger.jsonl.gz'),'generation_calls':0}


def leakage():
    from experiments.p5_leakage import audit
    return audit(p.HERE)


def role_boundaries():
    item=p.materials()[0]
    r=p.request(item,'X','answer',commitment='fixed',question='single')
    content=r.messages[-1]['content']
    forbidden=False
    try:p.request(item,'X','answer',history=[{'secret':'sibling answer'}],commitment='fixed',question='single')
    except PreflightError:forbidden=True
    return {'passed':forbidden and 'sibling answer' not in content and 'fixed' in content and 'single' in content,
        'fresh_context_fields':['packet','commitment','one_question'],'adaptive_followups':1,
        'judges_structured':all(p.request(item,a,'lone' if a=='L' else 'judge').response_schema==p.VERDICT_SCHEMA for a in p.ARMS)}



def packet_safety():
    import re
    from experiments.p5_isolation import validate_exposure
    items=p.materials(); bad=[]
    for item in items:
        q=item['payload']; seen={n['id'] for n in q['premises']}
        paragraphs=q['argument'].split('\n\n'); references=0
        if len(paragraphs)!=16 or q['nodes'][-1]['id']!=q['root']:
            bad.append(item['id']); continue
        for index,(n,para) in enumerate(zip(q['nodes'],paragraphs,strict=True)):
            if not set(n['parents']) <= seen or not para.startswith(f"[{n['id']}] "):
                bad.append(item['id'])
            seen.add(n['id'])
            if re.search(r'\bn\d+\b',para.split('] ',1)[-1]):
                bad.append(item['id'])
            refs=re.findall(r'the immediately preceding ([a-z-]+) result',para)
            references+=len(refs)
            for term in refs:
                from experiments.p5_paraphrase import inference_parts
                previous=inference_parts(q['nodes'][index-1]['text'])[1] if index else ''
                if not re.fullmatch(r'unit\d+ is '+re.escape(term),previous):
                    bad.append(item['id'])
        if references!=4:
            bad.append(item['id'])
    sample=items[0]; sibling=next(i for i in items if i['group']==sample['group'] and i['id']!=sample['id'])
    rejected=[]
    for check in (
        lambda:p.request(sample,'X','author',examples=[sibling]),
        lambda:p.request(sample,'X','judge',history=[{'item_id':sibling['id']}]),
        lambda:validate_exposure([{'item_id':sibling['id'],'reviewer_id':'fixture'}],
            [{'item_id':sample['id'],'reviewer_id':'fixture'}],{i['id']:i for i in items})):
        try:check();rejected.append(False)
        except PreflightError:rejected.append(True)
    return {'passed':len(items)==84 and not bad and all(rejected), 'items':len(items),
            'prose_failures':sorted(set(bad)), 'references_per_packet':4,
            'sibling_guards':rejected, 'context_policy':'one packet; no examples; item-bound transcript; disjoint raters',
            'generation_calls':0}

def external_timestamp(stamp):
    # Exact aggregate hash publication is required; local dates/commits are insufficient.
    proof=p.HERE/'freeze-manifest.sha256.ots';source=p.HERE/'freeze-manifest.sha256'
    if not proof.exists() or not source.exists() or source.read_text().strip()!=stamp:
        return {'passed':False,'reason':'publish exact manifest hash and retain bound OpenTimestamps receipt'}
    proc=subprocess.run(['uvx','--from','opentimestamps-client','ots','info',str(proof)],capture_output=True,text=True,timeout=60)
    bound=f'File sha256 hash: {p.sha(source)}' in proc.stdout
    return {'passed':proc.returncode==0 and bound and ('PendingAttestation(' in proc.stdout or 'BitcoinBlockHeaderAttestation(' in proc.stdout),
        'source_sha256':p.sha(source),'proof_sha256':p.sha(proof),'stdout':proc.stdout,
        'policy':'bound calendar submission is pilot timestamp evidence; not a claim of verified Bitcoin confirmation'}


def preflight(offline=False):
    f=p.verify_freeze();stamp=f['manifest_sha256'];reports={}
    from experiments.p5_surface import audit as surface_audit
    from experiments.p5_blinding import audit as blinding_audit
    checks=[('tracked-blinding',blinding_audit),('surface-soundness',surface_audit),('review',lambda:p.review.gate()),
        ('independent-prose',lambda:{'passed':len(read(p.HERE/'materials/paraphrases.jsonl.gz'))==84 and all(r['provenance'].get('independent_qwen_pass') for r in read(p.HERE/'materials/paraphrases.jsonl.gz'))}),
        ('construction',lambda:json.loads((p.HERE/'checks/construction.json').read_text())),
        ('known-answer',lambda:p.known_answer(p.materials(),p.check_labels())),
        ('lean-replay',lean_replay),('packet-safety',packet_safety),
        ('leakage',lambda:json.loads((p.HERE/'checks/leakage.json').read_text())
            if 'leakage_passed' in reports['review'] else {'passed':False,'reason':'review leakage audit failed'}),('role-boundaries',role_boundaries),
        ('external-timestamp',lambda:external_timestamp(stamp))]
    if not offline:checks.append(('tokenizer',tokenize))
    else:
        checks.append(('tokenizer',lambda:retained_tokens()))
    for name,fn in checks:
        try:result=fn()
        except Exception as exc:result={'passed':False,'error':f'{type(exc).__name__}: {exc}'}
        reports[name]=p.gate_receipt(name,result,stamp)
    blockers=[name for name,r in reports.items() if not r.get('passed')]
    f['unresolved']=blockers+['provider-preflight','dev'];f['status']='BLOCKED_NOT_SCORED_READY'
    f['external_timestamp']=reports['external-timestamp']
    write_json(p.HERE/'freeze.json',f)
    return {'passed':not blockers,'gates':{name:r.get('passed') for name,r in reports.items()},'generation_calls':0,'blockers':blockers}


def prose_token_fit():
    """Exact local Qwen counts; never substitute them for Gemini counts."""
    backend=OpenRouterBackend(p.native_counter())
    rows=[]
    for item in p.materials():
        dossier=next(d for d in read(p.HERE/'materials/dossiers.jsonl.gz') if d['id']==item['id'])
        requests=[('paraphrase',p.request({'id':item['id'],'split':'materials','payload':dossier},'shared','paraphrase'),4096),
                  ('common',p.request(item,'L','lone',judge='replication'),2048)]
        for scope,req,limit in requests:
            n=backend.count(req)
            rows.append({'scope':scope,'identity':req.identity,'wire_sha256':digest([req.messages,req.response_schema]),
                         'tokens':n,'limit':limit,'passed':n<=limit})
    result={'passed':all(r['passed'] for r in rows),'counts':rows,'generation_calls':0,
            'scope':'All 84 Qwen common-packet and paraphrase input requests; exact pinned native tokenizer and chat template; no provider calls.',
            'ranges':{scope:{'minimum':min(r['tokens'] for r in rows if r['scope']==scope),
                             'maximum':max(r['tokens'] for r in rows if r['scope']==scope),
                             'failures':sum(not r['passed'] for r in rows if r['scope']==scope)}
                      for scope in ('paraphrase','common')}}
    write_json(p.HERE/'checks/prose-token-fit.json',result)
    return result


def retained_tokens():
    receipt=json.loads((p.HERE/'checks/tokenizer.json').read_text())
    rows={r['identity']:r for r in receipt.get('counts',[])}
    for req,reserve in fixtures():
        r=rows.get(req.identity,{})
        if r.get('wire_sha256')!=digest([req.messages,req.response_schema]) or r.get('generated_reserve')!=reserve:
            local=prose_token_fit()
            return {'passed':False,'reason':'Tokenizer fixtures changed; free Gemini recount required. Local Qwen counts do not replace Gemini counts.',
                    'local_qwen_passed':local['passed'],'local_qwen_ranges':local['ranges'],'generation_calls':0}
    return receipt


def provider_smoke(cap,only_openrouter=False):
    # Separate infrastructure smoke, never an efficacy probe or replacement sample.
    book=p.ledger(cap);f=p.verify_freeze();results={}
    for model in (('replication',) if only_openrouter else ('pro','replication')):
        backend=VertexBackend() if model=='pro' else OpenRouterBackend(p.native_counter())
        client=PaidClient(backend,book,reuse_completed=True)
        req=PaidRequest('provider-preflight/p5/'+model,model,
            [{'role':'user','content':'Return JSON {"verdict":"unknown"}.'}],128,1024,
            response_schema={'type':'object','properties':{'verdict':{'type':'string','enum':['unknown']}},'required':['verdict'],'additionalProperties':False},
            metadata={'role':'probe'})
        try:
            count=backend.count(req);reply=client.call(req)
            results[model]={'passed':json.loads(reply.text)=={'verdict':'unknown'} and count==reply.input_tokens,
                'revision':reply.revision,'count':count,'billed_input':reply.input_tokens,
                'billed_output':reply.billed_output_tokens,'request_sha256':digest(req.messages)}
        finally:client.close()
    path=p.HERE/'checks/provider-preflight.json'
    old=json.loads(path.read_text()) if path.exists() else {}
    if old.get('freeze_sha256')==f['manifest_sha256']:results={**old.get('models',{}),**results}
    result={'passed':set(results)=={'pro','replication'} and all(r['passed'] for r in results.values()),'models':results}
    return p.gate_receipt('provider-preflight',result,f['manifest_sha256'])


def explanations(split,export=None,submit=None):
    rows=read(p.HERE/f'runs/{split}/trials.jsonl');items={i['id']:i for i in p.materials(split)}
    from experiments.p5_isolation import blind_packet, export_isolated, validate_exposure
    if export:
        records=[]
        for row in rows:
            key=digest({k:row[k] for k in ('item_id','condition','judge','answer')})
            records.append({'response_sha256':key,'item_id':row['item_id'],'packet':blind_packet(items[row['item_id']]['payload']),
                'answer':row['answer'],'rater_id':'','source_grounded':None,'reason':'','protocol_recognized':None,
                'source_fidelity':None,'event':'rating'})
        # Opaque hashes; no arm/model/order clues.
        import random
        random.Random(p.SEED).shuffle(records)
        return export_isolated(export,records,{i['id']:i['group'] for i in items.values()})
    if submit:
        incoming=json.loads(submit.read_text());allowed={digest({k:r[k] for k in ('item_id','condition','judge','answer')}) for r in rows}
        response_items={digest({k:r[k] for k in ('item_id','condition','judge','answer')}):r['item_id'] for r in rows}
        incoming=[{**r, 'item_id':response_items.get(r.get('response_sha256'))} for r in incoming]
        prior=read(p.HERE/f'runs/{split}/ratings.jsonl')
        validate_exposure(incoming,prior,items,identity='rater_id')
        for r in incoming:
            if r.get('response_sha256') not in allowed or not r.get('rater_id') or type(r.get('source_grounded')) is not bool or not r.get('reason'):
                raise PreflightError('complete identified, source-grounded ratings required')
            if r.get('event')=='adjudication' and not r.get('rating_digests'):
                raise PreflightError('adjudication must bind ratings')
            p.append(p.HERE/f'runs/{split}/ratings.jsonl',{k:v for k,v in r.items() if k not in ('packet','answer')})
        if split=='dev':
            ratings=read(p.HERE/'runs/dev/ratings.jsonl');ok=p.analyze(rows,p.materials('dev'),p.labels(),p.SCENARIOS[p.verify_freeze()['scenario']],ratings)
            keys={digest({k:r[k] for k in ('item_id','condition','judge','answer')}) for r in rows}
            fidelity=all(len({r['rater_id'] for r in ratings if r['response_sha256']==key and r.get('source_fidelity') is True})>=2 for key in keys)
            report=json.loads((p.HERE/'checks/dev.json').read_text());report['source_fidelity_passed']=fidelity
            report['passed']=fidelity and report.get('contract_passed') and not report.get('stopped') and report.get('missing')==0
            write_json(p.HERE/'checks/dev.json',report)
        return {'ratings_imported':len(incoming)}
    raise PreflightError('explanations requires --export or --submit')


def cost_report(split):
    import numpy as np
    rows=read(p.HERE/'runs/study/costs.jsonl')
    reservations={r['identity']:r for r in rows if r['event']=='reserve'}
    shared=defaultdict(Decimal); actual=defaultdict(Decimal); holds=Decimal(0)
    for row in rows:
        if row['event'] not in ('complete','infrastructure_failure','panel_halt'):
            continue
        meta=reservations.get(row.get('identity'),{}).get('metadata',{})
        value=Decimal(row.get('cost_usd',row.get('infrastructure_hold_usd','0')))
        if row['event']!='complete':holds+=value
        if meta.get('role')=='paraphrase':shared[meta['item_id']]+=value
        elif row['identity'].startswith(split+'/'):
            actual[(meta['item_id'],meta['arm'])]+=value
    attributed={(i['id'],a):actual[(i['id'],a)]+shared[i['id']]+Decimal('.0004')
                for i in p.materials(split) for a in p.ARMS}
    families=sorted({i['group'] for i in p.materials(split)})
    family_costs={a:[float(sum(attributed[(i['id'],a)] for i in p.materials(split) if i['group']==f)/3)
                    for f in families] for a in p.ARMS}
    draws=np.random.default_rng(p.SEED).integers(0,len(families),(20000,len(families)))
    numerator=np.asarray(family_costs['VE']);denominator=np.asarray(family_costs['X'])
    ratios=numerator[draws].mean(1)/denominator[draws].mean(1)
    return {'physical_shared_paraphrase_usd':str(sum(shared.values())),
        'shared_full_attribution_per_item_usd':{k:str(v) for k,v in shared.items()},
        'charged_infrastructure_holds_usd':str(holds),
        'item_arm_attributed_usd':{item+'/'+arm:str(v) for (item,arm),v in attributed.items()},
        'paired_cost_ratios_VE_over_X':{i['id']:str(attributed[(i['id'],'VE')]/attributed[(i['id'],'X')]) for i in p.materials(split)},
        'family_paired_ratio':{'estimate':float(numerator.mean()/denominator.mean()),
                              'bootstrap_interval':np.quantile(ratios,[.025,.975]).tolist()},
        'mean_attributed_cost_by_arm':{a:float(np.mean(v)) for a,v in family_costs.items()},
        'matched_ceiling_passed':all(v<=Decimal('.16') for v in attributed.values()),
        'engineering_manual_time':'review ledger; not included as free model work',
        'framing':'matched .16 ceiling; no actual-dollar top-up or outcome-dependent allocation'}
