"""Cross-check reported metrics and bootstrap endpoints by exact convolution."""
import json
from collections import Counter
import numpy as np
from rerun import OUT
import run as original


def main():
    summary=json.loads((OUT/'summary.json').read_text())
    scores=[json.loads(p.read_text()) for p in (OUT/'scores').glob('*.json')]
    assert len(scores)==480
    items=sorted({s['item_id'] for s in scores})
    values={(s['item_id'],s['arm'],s['judge'],s['sample_index']):int(s['correct']) for s in scores}
    ledgers=[json.loads(line) for p in (OUT/'ledgers').glob('*ledger.jsonl') for line in p.read_text().splitlines()]
    ok={r['key']:r for r in ledgers if r['status']=='ok'}
    checks=[]
    for cell,m in summary['metrics'].items():
        arm,judge=cell.rsplit('-',1)
        rs=[s for s in scores if s['arm']==arm and s['judge']==judge]
        assert len(rs)==48 and m['missing']==0
        for metric in ('correct','valid','false_approval','honest_completion'):
            assert m[metric]==sum(bool(s[metric]) for s in rs)
        assert m['both_correct']==sum(sum(values[i,arm,judge,k] for k in (0,1))==2 for i in items)
        thinking=[ok[s['key']]['thinking_tokens_reported'] for s in rs]
        assert m['thinking_total']==sum(thinking) and m['thinking_mean']==np.mean(thinking)
        eligible=[s for s in rs if s['attack_eligible']]
        assert m['eligible_attack_samples']==len(eligible)
        assert m['answer_rejections']==sum(s['correct'] for s in eligible)
        assert m['translation_catches']==sum(s.get('translation_caught',False) for s in eligible)
        for baseline,p in m['paired'].items():
            # Each whole item's difference is an integer in [-2,2], divided by 2.
            # The exact bootstrap distribution is the 24-fold convolution of
            # the empirical item distribution; no Monte Carlo or sample-level
            # resampling is used in this independent interval check.
            d=[sum(values[i,arm,judge,k]-values[i,baseline,judge,k] for k in (0,1)) for i in items]
            assert p['n']==24 and abs(p['difference']-sum(d)/48)<1e-12
            freq=Counter(d)
            pmf=np.array([freq.get(i,0)/24 for i in range(-2,3)])
            distribution=np.array([1.])
            for _ in range(24): distribution=np.convolve(distribution,pmf)
            support=(np.arange(len(distribution))-48)/48
            cdf=np.cumsum(distribution)
            exact=[float(support[np.searchsorted(cdf,q)]) for q in (.025,.975)]
            error=max(abs(a-b) for a,b in zip(exact,p['ci95']))
            assert error<=1/48+1e-12, (cell,baseline,exact,p['ci95'])
            checks.append({'cell':cell,'baseline':baseline,'exact_ci95':exact,
                           'reported_ci95':p['ci95'],'max_endpoint_difference':error})
    result={'all_cell_metrics_checked':True,'comparisons':len(checks),
            'exact_bootstrap_checks':checks,'max_endpoint_difference':max(c['max_endpoint_difference'] for c in checks)}
    original.dump(OUT/'analysis-validation.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='exact_bootstrap_checks'}))


if __name__=='__main__': main()
