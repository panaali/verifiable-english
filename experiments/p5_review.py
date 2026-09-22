"""Blind material and explanation annotation. No automatic reviewer approvals."""
from collections import defaultdict
from datetime import datetime, timezone
import json
import random
from pathlib import Path
from experiments.p5_materials import HERE, SEED, archive, read, write_json
from experiments.p5_isolation import blind_packet, export_isolated, validate_exposure
from ve_experiments.paid import digest, PreflightError

CHECKS = ('source_fidelity', 'root_preserved', 'no_added_assumption', 'no_repaired_flaw',
          'complete_sense_mapping', 'localization_anchored', 'no_answer_leakage')


def submit_schema():
    """Submission shape; source/hash/exposure checks still run in submit()."""
    text={'type':'string','minLength':1}
    strings={'type':'array','items':text}
    annotation={'type':'object','required':['kind','sense_use_mapping','required_assumptions',
        'root_meaning','acceptable_locations','source_evidence'], 'properties':{
        'kind':{'enum':['shift','smuggle','benign']},
        'sense_use_mapping':{'type':'object','minProperties':1,'additionalProperties':text},
        'required_assumptions':strings, 'root_meaning':text,
        'acceptable_locations':{'type':'array','minItems':2,'maxItems':2,
            'items':{'type':'array','minItems':1,'maxItems':2,'uniqueItems':True,'items':text}},
        'source_evidence':{'type':'array','minItems':1,'items':text}}}
    return {'$schema':'https://json-schema.org/draft/2020-12/schema',
        'title':'P5 sanitised paraphrase review submission','type':'array','minItems':1,
        'items':{'type':'object','required':['item_id','packet_sha256','reviewer_id',
            'reviewer_kind','model_family','minutes','checks','annotation','corrections','notes'],
            'properties':{'item_id':text,'packet_sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'},
                'reviewer_id':text,'reviewer_kind':{'enum':['human','project_lead','model']},
                'model_family':{'type':'string'},'minutes':{'type':'number','exclusiveMinimum':0},
                'checks':{'type':'object','required':list(CHECKS),'additionalProperties':False,
                    'properties':{k:{'type':'boolean'} for k in CHECKS}},
                'annotation':annotation,'corrections':strings,'notes':{'type':'string'}},
            'allOf':[{'if':{'properties':{'reviewer_kind':{'const':'model'}}},
                'then':{'properties':{'model_family':text}}}]}}


def review_export(destination, base=HERE):
    items = read(base/'materials/dev.jsonl.gz') + read(base/'materials/scored.jsonl.gz')
    sources={d['id']:d for d in read(base/'materials/dossiers.jsonl.gz')}
    # Sorting opaque IDs first prevents inventory/archive order from becoming
    # a label channel. The shuffle never inspects a label or family.
    items.sort(key=lambda item: item['id'])
    random.Random(f'{SEED}/packet-order-v3').shuffle(items)
    # No split/family/variant/formal artifact in review packets.
    rows = [{'item_id': i['id'], 'packet_sha256':digest(i['payload']), 'packet':blind_packet(i['payload']),
             'version':'sanitised-paraphrase', 'source_argument':sources[i['id']]['argument'],
             'reviewer_id':'', 'reviewer_kind':'human|project_lead|model', 'model_family':'',
             'minutes':0, 'checks':{k:None for k in CHECKS},
             'annotation':{'kind':None, 'sense_use_mapping':{}, 'required_assumptions':[],
                 'root_meaning':'', 'acceptable_locations':[], 'source_evidence':[]},
             'corrections':[], 'notes':''} for i in items]
    result=export_isolated(destination, rows, {i['id']:i['group'] for i in items})
    schema_path=Path(destination).with_suffix('.submit-schema.json')
    write_json(schema_path,submit_schema())
    return {**result,'version':'sanitised-paraphrase','submit_schema':str(schema_path)}


def submit(path, base=HERE, *, run_gate=True):
    submitted = json.loads(Path(path).read_text())
    items = {i['id']:i for split in ('dev','scored') for i in read(base/f'materials/{split}.jsonl.gz')}
    ledger_path = base/'materials/review-ledger.jsonl.gz'
    ledger = read(ledger_path)
    validate_exposure(submitted, ledger, items)
    prior = {(r['item_id'],r['reviewer_id'],r['packet_sha256']) for r in ledger if r['event']=='review'}
    new = []
    for row in submitted:
        if row.get('item_id') not in items or row.get('packet_sha256') != digest(items[row['item_id']]['payload']):
            raise PreflightError('review packet hash mismatch')
        if not row.get('reviewer_id') or row.get('reviewer_kind') not in ('human','project_lead','model'):
            raise PreflightError('identified reviewer and kind required')
        if row['reviewer_kind']=='model' and not row.get('model_family'):
            raise PreflightError('model-family disclosure required')
        if not isinstance(row.get('minutes'), (int,float)) or row['minutes'] <= 0:
            raise PreflightError('record positive manual/review time')
        if set(row.get('checks',{})) != set(CHECKS) or any(type(v)!=bool for v in row['checks'].values()):
            raise PreflightError('complete every checklist field explicitly')
        a=row.get('annotation',{})
        ids={n['id'] for n in items[row['item_id']]['payload']['nodes']} | {n['id'] for n in items[row['item_id']]['payload']['premises']}
        if a.get('kind') not in ('shift','smuggle','benign') or not a.get('sense_use_mapping') or not a.get('root_meaning') or not a.get('source_evidence'):
            raise PreflightError('recover meanings, evidence and label independently')
        if not {n['id'] for n in items[row['item_id']]['payload']['nodes']}<=set(a['sense_use_mapping']):
            raise PreflightError('sense mapping must cover all proposed nodes')
        locs=a.get('acceptable_locations',[])
        if (not isinstance(locs,list) or any(not isinstance(s,list) or any(not isinstance(n,str) for n in s) or len(set(s))!=len(s) or not set(s)<=ids for s in locs)
                or sorted(map(len,locs)) != [1,2]
                or not set(min(locs,key=len)) < set(max(locs,key=len))):
            raise PreflightError('invalid localization sets')
        key=(row['item_id'],row['reviewer_id'],row['packet_sha256'])
        if key in prior:
            raise PreflightError('duplicate review; preserve original and use adjudication')
        prior.add(key)
        new.append({**{k:v for k,v in row.items() if k!='packet'}, 'event':'review',
                    'time':datetime.now(timezone.utc).isoformat()})
    # Logical append only, deterministic archive; preserve every earlier event.
    archive(ledger_path, ledger+new)
    return gate(base) if run_gate else {'imported':len(new), 'gate_recomputed':False}


def adjudicate(path, base=HERE):
    row=json.loads(Path(path).read_text())
    ledger=read(base/'materials/review-ledger.jsonl.gz')
    items={i['id']:i for split in ('dev','scored') for i in read(base/f'materials/{split}.jsonl.gz')}
    item=items.get(row.get('item_id'))
    validate_exposure([{**row, 'reviewer_id':row.get('adjudicator')}], ledger, items)
    if item is None or row.get('packet_sha256') != digest(item['payload']):
        raise PreflightError('adjudication must bind the current packet')
    matching=[r for r in ledger if r['event']=='review' and r['item_id']==row.get('item_id')
              and r['packet_sha256']==row['packet_sha256']]
    if len(matching)<2 or not row.get('adjudicator') or not row.get('reason') or not row.get('source_evidence'):
        raise PreflightError('adjudication requires two reviews, identity, reason and source evidence')
    if row.get('review_digests') != [digest(r) for r in matching]:
        raise PreflightError('adjudication must bind all reviews in ledger order')
    if row.get('packet_sha256') != matching[-1]['packet_sha256']:
        raise PreflightError('adjudication packet mismatch')
    if row.get('annotation') not in [r['annotation'] for r in matching]:
        raise PreflightError('submit corrected independent reviews before a new annotation')
    archive(base/'materials/review-ledger.jsonl.gz', ledger+[{**row,'event':'adjudication'}])
    return gate(base)


def gate(base=HERE):
    items = read(base/'materials/dev.jsonl.gz')+read(base/'materials/scored.jsonl.gz')
    labels={r['id']:r for r in read(base/'labels.jsonl.gz')}
    ledger=read(base/'materials/review-ledger.jsonl.gz')
    unresolved=[]; anchored=[]
    for item in items:
        reviews=[r for r in ledger if r['event']=='review' and r['item_id']==item['id']
                 and r['packet_sha256']==digest(item['payload'])]
        eligible=(len({r['reviewer_id'] for r in reviews})>=2 and
                  (any(r['reviewer_kind'] in ('human','project_lead') for r in reviews) or
                   len({model_family(r.get('model_family','')) for r in reviews
                        if r['reviewer_kind']=='model'} - {None}) >= 2) and
                  all(all(r['checks'].values()) for r in reviews))
        annotation=reviews[0]['annotation'] if eligible else None
        if eligible and any(r['annotation']!=annotation for r in reviews):
            resolutions=[r for r in ledger if r['event']=='adjudication' and r['item_id']==item['id']
                and r['review_digests']==[digest(x) for x in reviews]]
            annotation=resolutions[-1]['annotation'] if resolutions else None
        if annotation and annotation['kind']!=labels[item['id']]['kind']:
            annotation=None  # A source-label mismatch halts; never silently relabel.
        if not annotation:
            unresolved.append(item['id'])
        else:
            anchored.append({'id':item['id'], 'packet_sha256':digest(item['payload']), **annotation})
    # Review cannot open on a stale or failing shortcut audit. Recompute from
    # exact packet bytes, including after the independent paraphrase pass.
    from experiments.p5_leakage import audit
    leakage = audit(base)
    write_json(base/'checks/leakage.json', leakage)
    result={'passed':len(items)==84 and not unresolved and leakage['passed'],
            'lead_hand_check':'deferred under orchestrator amendment 2026-09-22',
            'model_review_policy':'two different model families accepted; current packet hashes required',
            'leakage_passed':leakage['passed'], 'reviewed_slots':len(anchored),
            'unresolved':unresolved, 'ledger_sha256':digest(ledger)}
    archive(base/'materials/anchored-labels.jsonl.gz', anchored)
    write_json(base/'checks/review.json',result)
    return result


def model_family(name):
    """Canonical families: aliases of one provider are not independent reviews."""
    name = name.casefold()
    for family, aliases in (('anthropic', ('claude', 'anthropic')),
                            ('google', ('gemini', 'google')),
                            ('openai', ('gpt', 'openai')),
                            ('qwen', ('qwen', 'alibaba'))):
        if any(alias in name for alias in aliases):
            return family
    return None
