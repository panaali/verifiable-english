"""Answer-alone calibration; Sonnet dev selection, untouched Opus heldout."""
from __future__ import annotations
import argparse
from collections import Counter
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

from ve_experiments.claude_cli import ClaudeCLI, Controls, EndpointError, MODELS
from ve_experiments.llm import parse_final_json
from generate import HERE, LEVERS, write

SYSTEM='Solve the supplied classical logic problem. Return only one JSON object with an answer key.'
INSTRUCTIONS='''Use only the stated premises, even when they contradict everyday beliefs. True means the query follows in every model of the premises; False means its negation follows; Uncertain means neither follows. The people form a nonempty domain; Ada and Ben are people and may coincide. "Or" is inclusive unless "exactly one" is stated. No unstated implications or closed-world assumptions apply.
Return exactly {"answer":"True"}, {"answer":"False"}, or {"answer":"Uncertain"}. Do not return a translation, proof, or explanation.
'''


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def prompt(item):
    return INSTRUCTIONS+'\nPremises:\n'+'\n'.join(f'{i+1}. {p["english"]}' for i,p in enumerate(item['premises']))+'\nQuery: '+item['query']['english']


def load_items(split):
    path=HERE/f'{split}.jsonl'; manifest=json.loads((HERE/'manifest.json').read_text())
    if digest(path)!=manifest['splits'][split]['sha256']: raise ValueError('Corpus drift')
    return [json.loads(line) for line in path.read_text().splitlines()]


def summarize(items, rows):
    types={}
    for kind in LEVERS:
        subset=[i for i in items if i['type']==kind]
        if not subset: continue
        scored=[]; repeats=majority_correct=all_correct=0
        for item in subset:
            rs=[rows.get((item['id'],k),{}) for k in range(3)]
            scored.extend(rs)
            votes=Counter(r.get('answer') for r in rs if r.get('answer') in ('True','False','Uncertain'))
            repeats+=any(v>=2 and a!=item['label'] for a,v in votes.items())
            majority_correct+=votes[item['label']]>=2
            all_correct+=votes[item['label']]==3
        types[kind]={'items':len(subset),'scheduled_samples':3*len(subset),
                     'correct_samples':sum(bool(r.get('correct')) for r in scored),
                     'invalid_or_missing':sum(r.get('answer') not in ('True','False','Uncertain') for r in scored),
                     'recurring_same_wrong_answer_items':repeats,'majority_correct_items':majority_correct,
                     'all_three_correct_items':all_correct}
    return {'scheduled_items':len(items),'scheduled_samples':3*len(items),'completed':len(rows),'by_type':types}


def run(split,judge,selection=None):
    if split=='smoke' and judge!='haiku': raise ValueError('Smoke is Haiku only')
    if split=='dev' and judge=='opus': raise ValueError('Never expose dev selection items to Opus')
    items=load_items(split)
    selection_hash=None
    if split=='heldout':
        if selection is None: raise ValueError('Heldout requires frozen Sonnet-dev selection')
        selected=json.loads(selection.read_text())
        if selected['judge']!='sonnet' or selected['split']!='dev': raise ValueError('Selection must use Sonnet dev')
        if selected['dev_corpus_sha256']!=digest(HERE/'dev.jsonl'): raise ValueError('Selection corpus mismatch')
        selection_hash=digest(selection)
        items=[i for i in items if i['type'] in selected['selected_types']]
        if not items: raise ValueError('No types selected; report calibration ceiling instead')
    out=HERE/'results'/f'{split}-{judge}';out.mkdir(parents=True,exist_ok=True)
    controls=Controls(model=MODELS[judge],output_tokens=3000,timeout_s=180)
    run_manifest={'split':split,'judge':judge,'model':MODELS[judge],'k':3,'controls':asdict(controls),
                  'corpus_sha256':digest(HERE/f'{split}.jsonl'),'selection_sha256':selection_hash,
                  'prompt_sha256':hashlib.sha256((SYSTEM+INSTRUCTIONS).encode()).hexdigest(),
                  'item_ids':[i['id'] for i in items]}
    rp=out/'run-manifest.json'
    if rp.exists() and json.loads(rp.read_text())!=run_manifest: raise ValueError('Run manifest drift')
    write(rp,run_manifest)
    client=ClaudeCLI(out/'ledger.jsonl',controls,max_calls=len(items)*3)
    rows={}
    for path in out.glob('*-score.json'):
        row=json.loads(path.read_text());rows[row['id'],row['sample_index']]=row
    limits=sum(bool(r.get('rate_limit')) for r in rows.values())
    if limits>=2: raise EndpointError('Already stopped on repeated rate limits')
    for item in items:
        for k in range(3):
            if (item['id'],k) in rows: continue
            scored={'id':item['id'],'sample_index':k,'correct':False}
            fatal=False
            try:
                row=client.sample(item['id'],SYSTEM,prompt(item),k)
                answer=parse_final_json(row['text']).get('answer')
                if answer not in ('True','False','Uncertain'): raise ValueError('Invalid answer label')
                scored.update(answer=answer,correct=answer==item['label'])
            except Exception as exc:
                last=json.loads(client.ledger.read_text().splitlines()[-1]) if client.ledger.exists() else {}
                message=str(exc)
                # Successful streams also contain rate_limit_event with status
                # allowed. Classify only the actual error/result text.
                records=[json.loads(s) for s in last.get('raw_stream','').splitlines() if s.strip()]
                raw=json.dumps([r for r in records if r.get('type')=='result' or r.get('error')]).lower()
                rate=any(s in raw for s in ('rate_limit','rate limit','usage limit','hit your limit','quota','overloaded'))
                limits+=int(rate)
                scored.update(error=message,rate_limit=rate)
                drift=any(s in message for s in ('drift','model mismatch','date expired','previously started'))
                fatal=isinstance(exc,EndpointError) and (drift or not rate or limits>=2)
            rows[item['id'],k]=scored
            write(out/f"{item['id']}-{k}-score.json",scored)
            write(out/'summary.json',summarize(items,rows))
            print(json.dumps({'completed':len(rows),**scored}),flush=True)
            if fatal: raise EndpointError('Stopped on endpoint drift/error or repeated rate limit')


def select():
    """Predeclared threshold, no model comparison or Opus-based item selection."""
    out=HERE/'results/dev-sonnet'; items=load_items('dev')
    rows={}
    for p in out.glob('*-score.json'):
        r=json.loads(p.read_text()); rows[r['id'],r['sample_index']]=r
    if len(rows)!=3*len(items): raise ValueError('Complete Sonnet dev first')
    summary=summarize(items,rows)
    if any(r.get('error') for r in rows.values()): raise ValueError('Operational errors require explicit protocol review')
    selected=[t for t,s in summary['by_type'].items() if s['recurring_same_wrong_answer_items']/s['items']>=.2]
    result={'judge':'sonnet','split':'dev','model':MODELS['sonnet'],'threshold':.2,
            'rule':'same wrong valid answer in at least 2/3 samples on at least 20% of type items',
            'dev_corpus_sha256':digest(HERE/'dev.jsonl'),'dev_ledger_sha256':digest(out/'ledger.jsonl'),
            'selected_types':selected,'summary':summary}
    path=HERE/'selection.json'
    if path.exists() and json.loads(path.read_text())!=result: raise ValueError('Selection already frozen')
    write(path,result)
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['run','select'])
    p.add_argument('--split',choices=['smoke','dev','heldout'],default='smoke')
    p.add_argument('--judge',choices=['haiku','sonnet','opus'],default='haiku')
    p.add_argument('--selection',type=Path)
    a=p.parse_args()
    select() if a.command=='select' else run(a.split,a.judge,a.selection)
