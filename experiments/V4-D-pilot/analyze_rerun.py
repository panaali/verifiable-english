"""Descriptive item-paired analysis of replacement judgments only."""
import json
from collections import Counter
import numpy as np
import run as original
from rerun import HERE, OLD, OUT

NAMES = {'alone':'Judge alone','consultancy':'Consultancy','debate':'Debate',
         've_consultancy':'VE-consultancy','mistranslation':'Mistranslation attack'}


def count(n, d):
    return f'{n}/{d} ({100*n/d:.1f}%)' if d else 'N/A'


def main():
    scores = [json.loads(p.read_text()) for p in (OUT/'scores').glob('*.json')]
    indexed = {(r['item_id'],r['arm'],r['judge'],r['sample_index']):r for r in scores}
    rows = [json.loads(line) for p in (OUT/'ledgers').glob('*ledger.jsonl') for line in p.read_text().splitlines()]
    ok = {r['key']:r for r in rows if r['status']=='ok'}
    items = original.read_items()
    summary = {'completed':len(scores),'scheduled':480,'account_label':'danielsaeedi37','metrics':{},
               'calls_started_new':sum(r['status']=='started' for r in rows),
               'served_models':dict(Counter(r['served_model'] for r in ok.values()))}
    lines = ['# D pilot: amended judge results','',
             'Orchestrator amendment: [2026-09-22](AMENDMENT-2026-09-22.md). '
             'All replacement judges use **danielsaeedi37**; unchanged Opus arguments use **lead-main**, a separate role. '
             'The original 16 scored judgments and over-cap stream remain superseded evidence in `results/`; none are pooled.', '',
             f'Completed replacement judgments: **{len(scores)}/480**, plus two account-verification calls. '
             '24 paired items, 12 honest and 12 dishonest, two independent samples per cell. '
             '**Haiku 4.5 with default thinking**; Sonnet 5 with high effort and default adaptive thinking. '
             'No judge thinking cap is enforced. Total-output ceilings remain 4,096 / 32,000.', '',
             '| Arm | Judge | Accuracy /48 | False approval /24 | Honest completion /24 | Both correct /24 | Thinking total (mean/call) |',
             '|---|---|---:|---:|---:|---:|---:|']
    paired_lines = ['','## Paired accuracy differences','',
        'Arm minus baseline, percentage points; 95% percentile bootstrap intervals from 100,000 resamples '
        'of whole items (both samples kept together), seed 20260922. Only complete paired items enter a contrast. '
        'These descriptive intervals have no multiplicity correction. A degenerate interval at a ceiling '
        'does not imply population certainty.','',
        '| Arm | Judge | vs judge alone [95% interval] | vs debate [95% interval] |',
        '|---|---|---:|---:|']
    for arm in original.ARMS:
        for judge in original.JUDGES:
            subset = [r for r in scores if r['arm']==arm and r['judge']==judge]
            usage = [ok[r['key']] for r in subset]
            thinking = [r['thinking_tokens_reported'] for r in usage if r.get('thinking_tokens_reported') is not None]
            m = {'completed':len(subset),'missing':48-len(subset),
                 **{f:sum(r.get(f,False) for r in subset) for f in ['correct','valid','false_approval','honest_completion']},
                 'both_correct':sum(all(indexed.get((i['id'],arm,judge,k),{}).get('correct',False) for k in range(2)) for i in items),
                 'thinking_total':sum(thinking),'thinking_missing':len(subset)-len(thinking),
                 'thinking_mean':float(np.mean(thinking)) if thinking else None,
                 'thinking_max':max(thinking) if thinking else None,
                 'input_tokens':sum(r['input_tokens'] for r in usage),'output_tokens':sum(r['output_tokens'] for r in usage),
                 'paired':{}}
            eligible = [r for r in subset if r['attack_eligible']]
            m.update(eligible_attack_samples=len(eligible),answer_rejections=sum(r['correct'] for r in eligible),
                     translation_catches=sum(r.get('translation_caught',False) for r in eligible))
            for baseline in ['alone','debate']:
                differences = []
                for item in items:
                    pair = [indexed.get((item['id'],a,judge,k)) for a in [arm,baseline] for k in range(2)]
                    if all(r is not None for r in pair):
                        differences.append((sum(r['correct'] for r in pair[:2])-sum(r['correct'] for r in pair[2:]))/2)
                if differences:
                    data = np.array(differences)
                    rng = np.random.default_rng(20260922)
                    boot = data[rng.integers(0,len(data),size=(100000,len(data)))].mean(axis=1)
                    m['paired'][baseline]={'n':len(data),'difference':float(data.mean()),
                        'ci95':np.quantile(boot,[.025,.975]).tolist(),'item_differences':differences}
            summary['metrics'][arm+'-'+judge]=m
            t = f"{m['thinking_total']:,} ({m['thinking_mean']:.1f})" if thinking else 'N/A'
            lines.append(f"| {NAMES[arm]} | {judge.title()} | {count(m['correct'],48)} | {count(m['false_approval'],24)} | {count(m['honest_completion'],24)} | {m['both_correct']}/24 | {t} |")
            def contrast(b):
                p=m['paired'].get(b)
                return f"{100*p['difference']:+.1f} [{100*p['ci95'][0]:+.1f}, {100*p['ci95'][1]:+.1f}] (n={p['n']})" if p else 'N/A'
            paired_lines.append(f'| {NAMES[arm]} | {judge.title()} | {contrast("alone")} | {contrast("debate")} |')
    lines += ['', 'Scheduled denominators are shown; missing judgments are not observed errors. Invalid completed answers count as incorrect. '
              'For judge alone, false approval and honest completion are matched-subset error/accuracy; for debate, they refer to the focal assigned side. '
              'Thinking is included in output tokens. Missing thinking counts are recorded separately in the summary.', *paired_lines,
              '', '## Certified mistranslation attacks','',
              'All 12 selected dishonest attacks are reused unchanged, yielding 24 eligible samples per judge. '
              'Answer rejection (correct answer) and explicit translation detection (translation_faithful=false) are distinct.', '',
              '| Judge | Answer rejection | Translation catch |','|---|---:|---:|']
    for judge in original.JUDGES:
        m=summary['metrics']['mistranslation-'+judge]
        lines.append(f"| {judge.title()} | {count(m['answer_rejections'],m['eligible_attack_samples'])} | {count(m['translation_catches'],m['eligible_attack_samples'])} |")
    for item in items:
        artifact=json.loads((OLD/'artifacts'/f"{item['id']}.json").read_text())['mistranslation']
        if not artifact.get('attack_eligible'): continue
        pid=artifact['private_fidelity']['mistranslated_premises'][0]
        tr=next(t for t in artifact['submission']['translations'] if t['premise_id']==pid)
        lines += ['',f"Example `{item['id']}`, premise `{pid}`: {tr['english']}", '', f"Submitted VE: `{tr['ve']}`. Gold: **{item['label']}**; advocated: **{item['assigned']}**. "
                  'Deduction certified with no unbound leaves; query faithful; premise translation demonstrably non-equivalent. These private fidelity findings were not shown to judges.']
        for judge in original.JUDGES:
            for k in range(2):
                s=indexed.get((item['id'],'mistranslation',judge,k),{})
                j=s.get('judgment',{})
                lines += ['',f"- {judge.title()} sample {k}: answer `{s.get('answer','missing')}`, faithful `{j.get('translation_faithful','missing')}`; {j.get('reason','')} "]
        break
    old_summary=json.loads((OLD/'summary.json').read_text())
    summary['physical_opus_tokens']=old_summary['physical_opus_tokens']
    summary['mistranslation_honest_reused_tokens']=old_summary['mistranslation_honest_reused_tokens']
    lines += ['', '## Original arguer usage (lead-main)','', '| Arm | Calls | Input | Output | Thinking |','|---|---:|---:|---:|---:|']
    for arm,t in summary['physical_opus_tokens'].items():
        lines.append(f"| {NAMES.get(arm,arm)} | {t['calls']} | {t['input_tokens']} | {t['output_tokens']} | {t['thinking_tokens']} |")
    lines += ['', 'All four attack candidates are charged. The 12 honest arm-4 outputs are reused in arm 5 with no extra physical calls. '
              'Full usage and reused logical exposure are in `results-judge-rerun/summary.json`.', '',
              '## Interpretation','',
              'This is a small, paired mechanism pilot with unequal arm budgets, not a powered superiority test. '
              'Certification verifies deductions relative to submitted translations; it does not verify their English meaning. '
              'Translation catches and correct answers must therefore be read separately. '
              'Results apply to these generated items, prompts, models and account configuration. '
              'The amendment followed observation of the original cap failure; it is transparently post-stop, not an untouched preregistration.', '']
    if (OUT/'STOP.json').exists():
        summary['stop']=json.loads((OUT/'STOP.json').read_text())
        lines += ['**STOPPED:** '+json.dumps(summary['stop']), '']
    original.dump(OUT/'summary.json',summary)
    (HERE/'RESULTS.md').write_text('\n'.join(lines))
    print(json.dumps({'completed':len(scores),'calls_started_new':summary['calls_started_new']}))


if __name__=='__main__': main()
