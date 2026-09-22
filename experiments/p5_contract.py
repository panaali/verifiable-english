"""Offline, response-by-response audit of the superseded P5 v8 dev attempt."""
from collections import Counter
from dataclasses import fields
from decimal import Decimal
import hashlib
import json

from experiments import p5 as p
from experiments.p5_materials import read, write_json
from ve_experiments.paid import PaidRequest, VertexBackend, OpenRouterBackend, digest, PreflightError


def audit(base=None):
    base=base or p.HERE
    ledger=base/'runs/study/costs.jsonl'
    rows=read(ledger)
    reservations={r['identity']:r for r in rows if r['event']=='reserve'}
    items={i['id']:i for i in read(base/'materials/dev.jsonl.gz')}
    trials=read(base/'runs/dev/trials.jsonl')
    outcomes=[]
    for row in rows:
        if row['event']!='complete' or not row['identity'].startswith('dev/'):
            continue
        req=reservations[row['identity']];meta=req['metadata']
        judge=meta['role'] in ('lone','judge')
        ids={n['id'] for n in items[meta['item_id']]['payload']['nodes']+
             items[meta['item_id']]['payload']['premises']}
        codes=[];answer=None;json_error=None
        try:answer=json.loads(row['text'])
        except ValueError as exc:json_error=str(exc)
        truncated=row['finish_reason'].upper() in ('MAX_TOKENS','LENGTH')
        if truncated:codes.append('truncation')
        if judge:
            if json_error:codes.append('invalid_json')
            elif not isinstance(answer,dict):codes.append('non_object')
            else:
                expected={'verdict','issue_type','locations','explanation'}
                if set(answer)-expected:codes.append('extra_fields')
                if expected-set(answer):codes.append('missing_fields')
                if answer.get('verdict') not in ('approve','reject','unknown'):codes.append('verdict_vocabulary')
                if answer.get('issue_type') not in ('shift','smuggle','none','unknown'):codes.append('issue_type_vocabulary')
                loc=answer.get('locations')
                if not isinstance(loc,list) or any(not isinstance(s,str) for s in loc):codes.append('location_type')
                else:
                    if len(loc)>2:codes.append('location_count')
                    if len(set(loc))!=len(loc):codes.append('duplicate_locations')
                    if set(loc)-ids:codes.append('non_node_locations')
                exp=answer.get('explanation')
                if not isinstance(exp,str) or not exp.strip():codes.append('empty_or_nonstring_explanation')
        retained=PaidRequest(**{f.name:req[f.name] for f in fields(PaidRequest) if f.name in req})
        if retained.model=='pro':
            _,config=VertexBackend.__new__(VertexBackend).wire(retained)
            attached=config.response_schema is not None and config.response_mime_type=='application/json'
            wire_evidence='reconstructed frozen Vertex config; provider parsed field='+str('parsed' in row['response'])
        else:
            wire=OpenRouterBackend().wire(retained)
            attached=bool(wire.get('response_format',{}).get('json_schema',{}).get('schema'))
            wire_evidence='retained response format: '+str(row['response'].get('_p1_response_format'))
        if judge and not attached:codes.append('judge_schema_not_attached')
        trial=next((r for r in trials if r['item_id']==meta['item_id'] and
                    r['condition']==meta['arm'] and r['judge']==row['model']),None) if judge else None
        outcomes.append({'identity':row['identity'],'role':meta['role'],'arm':meta['arm'],'model':row['model'],
            'response_sha256':digest(row['text']),'finish_reason':row['finish_reason'],
            'visible_tokens':row['output_tokens'],'thinking_tokens':row['thinking_tokens'],
            'billed_output_tokens':row['billed_output_tokens'],'output_cap':req['max_output_tokens'],
            'output_cap_exceeded':row['billed_output_tokens']>req['max_output_tokens'],
            'schema_attached':attached,'schema_evidence':wire_evidence,
            'json_error':json_error,'judge_contract_applicable':judge,
            'legacy_contract_ok':trial['ok'] if trial else None,
            'legacy_contract_error':trial.get('error') if trial else None,
            'causes':codes,
            'verdict':answer.get('verdict') if isinstance(answer,dict) else None,
            'locations':answer.get('locations') if isinstance(answer,dict) else None,
            'explanation_chars':len(answer['explanation']) if isinstance(answer,dict) and isinstance(answer.get('explanation'),str) else None,
            'notes':('Free-text table/audit role; JSON verdict contract does not apply.' if meta['arm']=='S' and not judge
                else 'Fenced and incomplete formal JSON; environment starts as a string, not the required object. No complete artifact can be validated.'
                if meta['arm']=='VE' and not judge else '')})
    counts=Counter(c for o in outcomes for c in o['causes'])
    for code in ('verdict_vocabulary','issue_type_vocabulary','extra_fields','missing_fields',
                 'location_type','location_count','duplicate_locations','empty_or_nonstring_explanation','judge_schema_not_attached'):
        counts.setdefault(code,0)
    counts.update({'ve_truncation':sum(o['arm']=='VE' and 'truncation' in o['causes'] for o in outcomes),
        's_author_truncation':sum(o['arm']=='S' and 'truncation' in o['causes'] for o in outcomes),
        'judge_truncation':sum(o['judge_contract_applicable'] and 'truncation' in o['causes'] for o in outcomes),
        'output_cap_exceeded':sum(o['output_cap_exceeded'] for o in outcomes),
        'allowed_unknown_verdicts':sum(o['verdict']=='unknown' for o in outcomes),
        'judge_schema_domain_mismatch_exposures':sum(o['judge_contract_applicable'] for o in outcomes),
        'judge_schema_domain_mismatch_observed_failures':counts['non_node_locations'],
        've_roles_without_formal_schema':sum(o['arm']=='VE' and not o['schema_attached'] for o in outcomes)})
    counts['explanation_length_violations']=0  # No maximum exists in the frozen contract.
    # Bind the immutable pre-amendment prefix; later accounting events cannot
    # invalidate the audit or change it on an idempotent offline replay.
    prefix=ledger.read_bytes().splitlines(keepends=True)
    cutoff=next((i for i,r in enumerate(rows) if r['event']=='p5_dev_cap_recovery'),len(rows))
    evidence=b''.join(prefix[:cutoff])
    return {'status':'SUPERSEDED_INFRASTRUCTURE_ATTEMPT','date':'2026-09-22','generation_calls':0,
        'ledger_prefix_sha256':hashlib.sha256(evidence).hexdigest(),'ledger_prefix_bytes':len(evidence),
        'dev_completions':len(outcomes),'judge_completions':sum(o['judge_contract_applicable'] for o in outcomes),
        'dev_cost_usd':str(sum(Decimal(r['cost_usd']) for r in rows if r['event']=='complete' and r['identity'].startswith('dev/'))),
        'assigned_judgments':96,'missing_judgments':96-len(trials),
        'legacy_counts':{j:{'assigned':48,'observed':sum(r['judge']==j for r in trials),
            'valid':sum(r['judge']==j and r['ok'] for r in trials)} for j in ('pro','replication')},
        'counts':dict(counts),'responses':outcomes,
        'interpretation':[
            'Legacy compliance divides valid outputs by all 48 assignments per judge; 44 per judge were never observed.',
            'The final VE defender billed 1095 > 1024 and halted pro before either VE judgment; all costs were recorded.',
            'Unknown is valid. Explanations have no maximum length; nonempty text is the only syntactic requirement.',
            'Schema permits arbitrary location strings but legacy parser requires existing node IDs. One rule ID triggers that disagreement.',
            'Wrong/empty localization remains a scored failure; no gold IDs are added to provider schema.',
            'Four VE nonjudge roles request JSON but have no formal response schema; judge schema is not applicable to those roles.',
            'No provider HTTP request dump exists for Vertex; attachment evidence is the retained request plus unchanged wire builder and parsed responses.']}


def supersede(base=None):
    """Preserve historical trial/gate bytes; do not recover billing or pay for retries."""
    base=base or p.HERE
    report=audit(base)
    write_json(base/'checks/dev-contract-audit.json',report)
    source=base/'checks/dev.json';archive=base/'checks/dev-superseded-v8.json'
    if not archive.exists():
        archive.write_bytes(source.read_bytes())
    p.P5Ledger(base/'runs/study/costs.jsonl',p.CAP).supersede_dev()
    write_json(source,{'passed':False,'contract_passed':False,'status':'SUPERSEDED_REQUIRES_V9_DEV',
        'superseded_report':'checks/dev-superseded-v8.json','audit':'checks/dev-contract-audit.json',
        'new_run_directory':'runs/dev-v9','generation_calls':0,
        'reason':'Dated harness amendment; all old responses, costs and halts retained. No v9 trial exists.'})
    return report


if __name__=='__main__':
    report=supersede()
    print(json.dumps({k:v for k,v in report.items() if k!='responses'},indent=2))
