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
    summary=summarize(items,results)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    ledger=[json.loads(x) for x in (out/'ledger.jsonl').read_text().splitlines()]
    attempts=[r for r in ledger if r['status']=='started']
    terminal=[r for r in ledger if r['status']!='started']
    ok=[r for r in terminal if r['status']=='ok']
    usage=Counter()
    for r in terminal:
        for key,value in r.get('usage',{}).items():
            if type(value) is int:usage[key]+=value
    models=Counter(r.get('served_model','unparsed') for r in terminal)
    groups=defaultdict(list)
    for r in ok:groups[r['item_id']].append(r['input_tokens'])
    drifts={k:v for k,v in groups.items() if len(set(v))>1}
    thinking=[r['thinking_tokens_reported'] for r in ok if r.get('thinking_tokens_reported') is not None]
    lines=['# B: full-size formalisation fidelity results','',
           'Preregistration commit: `6d8525e`; SHA-256 manifest `HASHES`, OpenTimestamps receipt `HASHES.ots`. No B main-study call preceded that commit. Human / independent-model fidelity audits and API replication remain pending. Python VE replay, not Lean verification.','',
           f"Scheduled: 60 fresh items × 3 = 180 calls. Started {len(attempts)}, terminal {len(terminal)}, successful endpoint responses {len(ok)}, scored {len(results)}.",'',
           '| Item type | Scheduled samples | Exact AST fidelity | Certified answer | Answer accuracy | Faithful + grounded certificate |',
           '|---|---:|---:|---:|---:|---:|']
    def pct(n,d):return f'{n}/{d} ({100*n/d:.1f}%)'
    for group in ['all','label:True','label:False','label:Uncertain']:
        s=summary['by_type'][group];n=s['n']
        lines.append('| '+group+' | '+str(n)+' | '+' | '.join(pct(s[m],n) for m in ['faithful_exact','certified_answer','answer_correct','grounded_certificate'])+' |')
    lines+=['',f"All three translations exact: {summary['all_three_exact_items']}/60 item clusters. Replicates are not independent items. More permissive mechanically checked equivalence: {summary['by_type']['all']['faithful_mechanical']}/180. Full scheduled denominators retain failures/missing outputs. These are descriptive results, not a frontier-benefit estimate.",'',
            'Primary taxonomy (multi-label sample incidences): `'+json.dumps(summary['taxonomy_samples_multilabel'])+'`. Parse/omission/endpoint failures enter other. Structural categories are diagnostics, not inferred model intent.','',
            'Errors: `'+json.dumps(summary['errors'])+'`. Complete per-depth/query-kind tables and row taxonomy are in `summary.json`. The independent per-row audit in `row-audit.json` preserves inspectable failures even if the original scorer aborted at a malformed row.','',
            'Served models: `'+json.dumps(dict(models))+'`. Input-count drifts for identical item content: `'+json.dumps(drifts)+'`. Usage: `'+json.dumps(dict(usage))+'`. Reported thinking tokens: '+str(sum(thinking))+f' across {len(thinking)} responses.','',
            'Endpoint overhead baselines: five canaries at **337 tokens each**, five trivial probes at **259 each**, zero drift. They include supplied text; absolute wrapper-only overhead is **unmeasured**. Fixed empty cwd, /bin/sh, locale, UTC, host release and date guard. The SDK identity prefix **“You are a Claude agent, built on Anthropic\'s Claude Agent SDK.” is an uncontrolled constant**; environment/model/cutoff/token-budget/date injection remains. No API-equivalence or invisible-context attestation.','',
            'Gold is generated with a declared restricted compositional English distribution; independent human English/gold and English/submission audit is outstanding. Certificates alone do not establish fidelity; the grounded metric additionally binds every graph leaf to the translated premise table. Uncertain certification requires both query-polarity witness models.','']
    (out/'RESULTS.md').write_text('\n'.join(lines))
    print('\n'.join(lines[:15]))

if __name__=='__main__':main()
