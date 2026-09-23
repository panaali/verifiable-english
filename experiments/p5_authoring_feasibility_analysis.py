"""Read-only analysis of the frozen authoring probe; no provider calls."""
from collections import Counter
from datetime import datetime
import json
from experiments import p5 as p
from experiments import p5_authoring_feasibility as f
from ve import Environment, Claim, prove_entailment
from ve_experiments.paid import digest


def main():
    out=f.OUT
    rows=json.loads((out/'results.json').read_text())
    paid=p.read(out/'costs.jsonl')
    completed={r['identity']:r for r in paid if r['event']=='complete'}
    reserves={r['identity']:r for r in paid if r['event']=='reserve'}
    items={i['id']:i for i in p.materials('dev')}
    records=[]
    for row in rows:
        for stage in row['stages']:
            ident=stage['identity']; paidrow=completed[ident]
            assert digest(paidrow['text'])==stage['response_sha256']
            result=stage['replay']
            detail={k:stage[k] for k in ('stage','identity','response_sha256','finish_reason')}
            detail.update(item_id=row['item_id'],ok=result['ok'],delivery_ok=False,environment_ok=False,
                    all_claims_parse=False,graph_checked='findings' in result)
            try:
                artifact=p.protocol_json(paidrow['text']); detail['delivery_ok']=True
                env=Environment.from_dict(artifact['environment']);detail['environment_ok']=True
                errors=[]; claims={}
                for c in artifact['claims']:
                    try: claims[c['id']]=Claim.create(env,c['id'],c['source'])
                    except Exception as e: errors.append({'claim_id':c['id'],'error':type(e).__name__+': '+str(e)})
                detail['claim_count']=len(artifact['claims']);detail['claim_parse_failures']=errors
                detail['all_claims_parse']=not errors
                detail['category']='success' if result['ok'] else f.category(result)
                if 'findings' in result:
                    detail['checker_errors']=result['findings']['errors']
                    detail['edge_findings']=result['findings']['findings']
                    proofs=[]
                    for e in artifact['edges']:
                        proof=prove_entailment(env,[claims[n].ast for n in e['premises']],claims[e['conclusion']].ast,max_steps=10000)
                        proofs.append({'edge_id':e['id'],'conclusion':e['conclusion'],'premises':e['premises'],
                        'status':proof.status,'steps':proof.steps,'detail':proof.detail})
                    detail['offline_proof_search']=proofs
                    if not result['ok']:
                        if detail['checker_errors']:
                            detail['category']='graph/certificate rejection'
                        elif any(x['status']=='ResourceLimit' for x in proofs):
                            detail['category']='prover ResourceLimit'
                        else:
                            detail['category']='unproved edge (NotFound, not a refutation)'
            except Exception as e:
                detail['inspection_error']=type(e).__name__+': '+str(e)
                detail['category']='JSON delivery' if not detail['delivery_ok'] else f.category(result)
            req=reserves[ident]
            # Every request uses this packet, this guide and only the permitted history.
            assert req['messages'][0]['content']==p.request(items[row['item_id']],'VE',stage['stage']).messages[0]['content']
            assert f.GUIDE in req['messages'][-1]['content']
            records.append(detail)
    summary={'n':len(rows),'artifacts':len(records),'category_counts':dict(Counter(r['category'] for r in records)),
        'delivery_ok':sum(r['delivery_ok'] for r in records),'environment_ok':sum(r['environment_ok'] for r in records),
        'all_claims_parse':sum(r['all_claims_parse'] for r in records),'graph_checked':sum(r['graph_checked'] for r in records),
        'initial_all_claims_parse':sum(r['all_claims_parse'] for r in records if r['stage']=='author'),
        'repair_all_claims_parse':sum(r['all_claims_parse'] for r in records if r['stage']=='repair'),
        'initial_successes':sum(r['ok'] for r in records if r['stage']=='author'),
        'repair_successes':sum(r['ok'] for r in records if r['stage']=='repair'),
        'records':records,'ledger_sha256':p.sha(out/'costs.jsonl'),'results_sha256':p.sha(out/'results.json'),
        'paid_calls_in_this_analysis':0}
    manifest=json.loads((out/'freeze.json').read_text())
    assert datetime.fromisoformat(manifest['time_utc']).timestamp() < min(r['time'] for r in reserves.values())
    assert len(completed) <= 24 and set(completed) == set(reserves)
    assert all(r['model'] == 'pro' and r['metadata']['role'] in ('author', 'repair') for r in reserves.values())
    assert f.retained_inputs()==manifest['retained_hashes']
    assert all(p.sha(p.ROOT/name)==sha for name,sha in manifest['hashes'].items())
    summary['frozen_sources_and_retained_inputs_unchanged']=True
    summary['freeze_precedes_first_dispatch']=True
    p.write_json(out/'artifact-analysis.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='records'},indent=2))


if __name__ == "__main__":
    main()
