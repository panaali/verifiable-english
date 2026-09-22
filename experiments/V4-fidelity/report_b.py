"""Render a descriptive full-denominator B report from immutable saved evidence."""
from collections import Counter,defaultdict
import json
from pathlib import Path
from fidelity import HERE
from run_b import summarize


def main():
    out=HERE/'results/b'
    items=[json.loads(x) for x in (HERE/'items-b.jsonl').read_text().splitlines()]
    results={}
    for p in out.glob('*-score.json'):
        r=json.loads(p.read_text());results[r['id'],r['sample_index']]=r
    stop=json.loads((out/'STOP.json').read_text()) if (out/'STOP.json').exists() else None
    excluded={tuple(k) for k in stop['post_stop_identities']} if stop else set()
    results={k:r for k,r in results.items() if k not in excluded}
    summary=summarize(items,results)
    summary.update(status=stop['status'] if stop else 'RUNNING_OR_COMPLETE', post_stop_exclusions=sorted(excluded))
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    ledger=[json.loads(x) for x in (out/'ledger.jsonl').read_text().splitlines()]
    attempts=[r for r in ledger if r['status']=='started']
    all_terminal=[r for r in ledger if r['status']!='started']
    terminal=[r for r in all_terminal if (r['item_id'],r['sample_index']) not in excluded]
    ok=[r for r in terminal if r['status']=='ok']
    usage=Counter()
    for r in terminal:
        for key,value in r.get('usage',{}).items():
            if type(value) is int:usage[key]+=value
    models=Counter(r.get('served_model','unparsed') for r in terminal)
    transport=Counter()
    for r in terminal:
        if r['status']!='error': continue
        for line in r.get('raw_stream','').splitlines():
            record=json.loads(line)
            if record.get('type')=='result': transport[record.get('result','unknown')]+=1
    response_scores=[results.get((r['item_id'],r['sample_index']),{}) for r in ok]
    conditional={'n':len(ok),**{m:sum(bool(r.get(m)) for r in response_scores)
                 for m in ('faithful_exact','certified_answer','answer_correct','grounded_certificate')}}
    groups=defaultdict(list)
    for r in ok:groups[r['item_id']].append(r['input_tokens'])
    drifts={k:v for k,v in groups.items() if len(set(v))>1}
    thinking=[r['thinking_tokens_reported'] for r in ok if r.get('thinking_tokens_reported') is not None]
    rejected_usage=[]
    for r in terminal:
        if r['status']!='error': continue
        for line in r.get('raw_stream','').splitlines():
            record=json.loads(line)
            if record.get('type')=='result' and any(record.get('usage',{}).get(k,0) for k in ('input_tokens','output_tokens')):
                rejected_usage.append({'id':r['item_id'],'sample_index':r['sample_index'],
                    'num_turns':record.get('num_turns'),'usage':record.get('usage'),'model_usage':record.get('modelUsage')})
    (out/'rejected-usage.json').write_text(json.dumps(rejected_usage,indent=2)+'\n')
    lines=['# B: stopped formalisation fidelity study' if stop else '# B: full-size formalisation fidelity results','',
           'Preregistration commit: `6d8525e`; SHA-256 manifest `HASHES`, OpenTimestamps receipt `HASHES.ots`. No B main-study call preceded that commit. Human / independent-model fidelity audits and API replication remain pending. Python VE replay, not Lean verification.','',
           f"Scheduled: 60 fresh items × 3 = 180 calls. Started {len(attempts)}, terminal records {len(all_terminal)}; pre-stop attempts {len(terminal)}, accepted pre-stop endpoint responses {len(ok)}, pre-stop scores {len(results)}.",'',
           '| Item type | Scheduled samples | Exact AST fidelity | Certified answer | Answer accuracy | Faithful + grounded certificate |',
           '|---|---:|---:|---:|---:|---:|']
    def pct(n,d):return f'{n}/{d} ({100*n/d:.1f}%)'
    for group in ['all','label:True','label:False','label:Uncertain']:
        s=summary['by_type'][group];n=s['n']
        lines.append('| '+group+' | '+str(n)+' | '+' | '.join(pct(s[m],n) for m in ['faithful_exact','certified_answer','answer_correct','grounded_certificate'])+' |')
    lines+=['',f"All three translations exact: {summary['all_three_exact_items']}/60 item clusters. Replicates are not independent items. More permissive mechanically checked equivalence: {summary['by_type']['all']['faithful_mechanical']}/180. Full scheduled denominators retain failures/missing outputs. These are descriptive results, not a frontier-benefit estimate.",'',
            ('**STOP:** Attempt 142 (`v4b-047`, replicate 0) requested/initialized Opus 5.5 but served `claude-opus-4-8`. The backend rejected it. Its result also reports three turns, 16,963 output tokens and 9,711 thinking tokens, violating the intended single-turn/budget controls. Further B and C model calls were withheld after the user\'s served-model stop condition. The complete rejected usage is in `rejected-usage.json`.' if stop else ''),'',
            ('**Protocol deviation:** The frozen runner confused the ordinary `rate_limit_event: allowed` event with a rate-limit error. It therefore permitted one follow-on Opus 5.5 response and another started identity before manual interruption. Both post-stop identities are excluded from confirmatory successes; their original ledger/score records remain intact. STOP.json records the cutoff. No failed identity was retried. The stop handler is now corrected and covered by regression tests; a permanent stop file prevents resumption. Original preregistered source remains in commit `6d8525e` and `run_b-preregistered.py`. The current runner intentionally no longer matches its original HASHES entry; no preregistration or timestamp was rewritten.' if stop else ''),'',
            'Primary taxonomy (multi-label sample incidences): `'+json.dumps(summary['taxonomy_samples_multilabel'])+'`. Parse/omission/endpoint failures enter other. Structural categories are diagnostics, not inferred model intent.','',
            'Errors: `'+json.dumps(summary['errors'])+'`. Transport details: `'+json.dumps(dict(transport))+'`. During sustained DNS failure the runner was briefly paused and resumed after connectivity recovered, without retrying any failed identity; see `operations.json`. A local watchdog subsequently pauses new calls after two consecutive network errors. Model prompts/controls and scheduled identities did not change.','',
            'Response-only descriptive counts (secondary, conditioned on endpoint success; not the scheduled-denominator estimand): `'+json.dumps(conditional)+'`. The outage prevents interpreting the full-denominator gap as solely a model reasoning/translation deficit.','',
            'Complete per-depth/query-kind tables and row taxonomy are in `summary.json`. The independent per-row audit in `row-audit.json` preserves inspectable failures even if the original scorer aborted at a malformed row.','',
            'Served models: `'+json.dumps(dict(models))+'`. Input-count drifts for identical item content among accepted pre-stop responses: `'+json.dumps(drifts)+'`. Reported usage from parsed responses: `'+json.dumps(dict(usage))+'`. Reported thinking tokens: '+str(sum(thinking))+f' across {len(thinking)} responses; maximum {max(thinking,default=0)}, with {sum(t>1024 for t in thinking)} above the requested 1024 setting. The setting is constant; this is not evidence of a strict internal reasoning-token ceiling. Transport failures may have incomplete usage reporting.','',
            'Endpoint overhead baselines: five canaries at **337 tokens each**, five trivial probes at **259 each**, zero drift. They include supplied text; absolute wrapper-only overhead is **unmeasured**. Fixed empty cwd, /bin/sh, locale, UTC, host release and date guard. The SDK identity prefix **“You are a Claude agent, built on Anthropic\'s Claude Agent SDK.” is an uncontrolled constant**; environment/model/cutoff/token-budget/date injection remains. No API-equivalence or invisible-context attestation.','',
            'Gold is generated with a declared restricted compositional English distribution; independent human English/gold and English/submission audit is outstanding. Certificates alone do not establish fidelity; the grounded metric additionally binds every graph leaf to the translated premise table and requires every table row to appear as a same-named, same-source graph claim. Omitting unused premise claims can therefore fail that stricter metric without invalidating the deduction. Uncertain certification requires both query-polarity witness models.','']
    (out/'RESULTS.md').write_text('\n'.join(lines))
    print('\n'.join(lines[:15]))

if __name__=='__main__':main()
