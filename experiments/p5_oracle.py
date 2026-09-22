"""Bounded online P5 mechanical work; input contains only model commitments."""
from dataclasses import replace
import json
import subprocess
import sys
import time
from ve import (Environment, Claim, Deduction, ArgumentGraph, check_argument,
                prove_entailment, parse, compare, Budgets)
from ve.argument import deduction_identity
from ve.attacks import validate_attack
from ve_experiments.paid import digest, packed

BUDGETS = dict(max_proof_steps=10000,max_domain_size=2,max_models=10000,max_evaluations=100000)


def author_graph(artifact, packet):
    env=Environment.from_dict(artifact['environment'])
    claims=tuple(Claim.create(env, c['id'], c['source']) for c in artifact['claims'])
    public={n['id'] for n in packet['nodes']} | {n['id'] for n in packet['premises']}
    if {c.name for c in claims}!=public or len(claims)!=len(public):
        raise ValueError('missing or duplicate claim coverage')
    if artifact['root']!=packet['root']:
        raise ValueError('original root missing')
    if set(artifact['alignment'])!=public or any(not artifact['alignment'][c] for c in public):
        raise ValueError('complete source/premise alignment required')
    records={r['id'] for r in packet['records']}
    if any(not set(v)<=records for v in artifact['alignment'].values()):
        raise ValueError('alignment must cite exact shared record IDs')
    edges=tuple(Deduction(e['id'], tuple(e['premises']), e['conclusion']) for e in artifact['edges'])
    declared={p['id'] for p in packet['premises']}
    if len(edges)!=24 or {c.name for c in claims}-{e.conclusion for e in edges}!=declared:
        raise ValueError('declared premise coverage changed; bridges are not free leaves')
    graph=ArgumentGraph(env,claims,edges,artifact['root'])
    by_id={c.name:c for c in claims}
    certified=[]
    for edge in edges:
        proof=prove_entailment(env,[by_id[p].ast for p in edge.premises],by_id[edge.conclusion].ast,
                              max_steps=10000)
        certified.append(replace(edge,certificates=({'edge_id':deduction_identity(graph,edge),
            'direction':'follows','proof':proof.certificate},) if proof.status=='Found' else ()))
    graph=replace(graph,deductions=tuple(certified))
    result=check_argument(graph,search=False).to_dict()
    good=not result['errors'] and all(v==['follows'] for v in result['findings'].values())
    return {'ok':good,'graph':graph.to_dict(),'findings':result,
            'obligations':[] if good else ['unproved edge or incomplete original-root coverage'],
            'warning':'Conditional proof only; source fidelity and premise support remain unassessed.'}


def query(data):
    committed=data['committed']; q=data['query']; packet=data['packet']
    env=Environment.from_dict(committed['environment'])
    claims={c['id']:c for c in committed['claims']}
    claim=claims[q['claim_id']]
    if q['environment_id']!=env.environment_id or q['committed_source']!=claim['source']:
        raise ValueError('query is not bound to committed source/environment')
    records={r['id']:r['text'] for r in packet['records']}
    if records.get(q['record_id'])!=q['rival_source_text']:
        raise ValueError('rival must cite exact source record text')
    left=parse(env,claim['source']).formulas[0]
    right=parse(env,q['rival_ve']).formulas[0]
    fn=compare if q['tool']=='compare' else validate_attack if q['tool']=='validate_attack' else None
    if fn is None:
        raise ValueError('unknown oracle tool')
    return {'result':fn(env,left,right,Budgets(**BUDGETS)).to_dict(),
            'warning':'Logical comparison does not select the source-faithful interpretation.'}


def bounded(operation, data, seconds=5):
    start=time.monotonic()
    try:
        p=subprocess.run([sys.executable,'-m','experiments.p5_oracle'],input=packed({'operation':operation,**data}),
                         text=True,capture_output=True,timeout=min(seconds,60))
        result=json.loads(p.stdout) if p.returncode==0 else {'ok':False,'error':p.stderr,'status':'UNKNOWN'}
    except (subprocess.TimeoutExpired,ValueError):
        result={'ok':False,'status':'UNKNOWN','error':'local timeout or invalid worker output'}
    return {**result,'query_sha256':digest(data),'elapsed_s':time.monotonic()-start}


def main():
    data=json.load(sys.stdin); start=time.process_time()
    try:
        result=author_graph(data['artifact'],data['packet']) if data['operation']=='author' else query(data)
    except Exception as exc:
        result={'ok':False,'status':'UNKNOWN','error':f'{type(exc).__name__}: {exc}'}
    print(packed({**result,'cpu_s':time.process_time()-start}))

if __name__=='__main__':
    main()
