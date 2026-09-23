"""Render preregistered result summaries; never dispatch endpoint calls."""
from ve_experiments.t1b.amendment_run import HOME, load, report


def pct(v):
    return 'NA' if v is None else f'{100*v:.1f}%'


def rate(v):
    lo,hi=v['cluster_t_95']
    return f"{v['approvals']}/{v['scheduled_samples']} ({pct(v['rate'])}; {pct(lo)}–{pct(hi)})"


def main():
    gate=report('gate')
    stop=load(HOME/'STOP-A1.json') if (HOME/'STOP-A1.json').exists() else None
    lines=['# T1b results','',
        'Original T1 is unchanged: 2/30 false approvals, STOP_CEILING. T1b is a new exploratory follow-up.', '',
        '## Gate','',
        '| Judge | Grants | Scored / planned decisions | False approvals (item-cluster t 95% CI) | Honest completion (95% CI) | Decision |',
        '|---|---:|---:|---|---|---|']
    for label,c in gate['gate'].items():
        size,judge=label.split('/')
        fa=rate(c['false_approval']) if c['complete'] else 'NA — incomplete'
        hc=rate(c['honest_completion']) if c['complete'] else 'NA — incomplete'
        lines.append(f"| {judge} | {size} | {c['observed_decisions']}/60 | {fa} | {hc} | {c['decision']} |")
    lines+=['','Partial observations only (completed samples; not gate estimates):','',
        '| Judge / grants | False approvals / observed sabotaged samples | Honest approvals / observed honest samples | Invalid responses |',
        '|---|---:|---:|---:|']
    for label,c in gate['gate'].items():
        fa,hc=c['false_approval'],c['honest_completion']
        lines.append(f"| {label} | {fa['approvals']}/{fa['scheduled_samples']} | {hc['approvals']}/{hc['scheduled_samples']} | {fa['invalid']+hc['invalid']} |")
    lines+=['','Intervals use policy items as clusters, not independent repeated samples. Sample Wilson and item-any-approval Wilson intervals are retained in summary.json. Degenerate intervals do not establish zero uncertainty.']
    if (HOME/'results-full').exists():
        full=report('full')
        lines+=['','## Full five-arm study','',f"Observed {full['observed_decisions']}/{full['expected_decisions']} scheduled final decisions.",'',
            '| Judge / grants | Arm | False approval (95% CI) | Honest completion (95% CI) | Judge tokens in / out, including audit/code |',
            '|---|---|---|---|---:|']
        for label,c in sorted(full['cells'].items()):
            size,arm,judge=label.split('/')
            usage=c['judge_total_including_audit_and_code']
            lines.append(f"| {judge} / {size} | {arm} | {rate(c['false_approval'])} | {rate(c['honest_completion'])} | {usage['input_tokens']:,} / {usage['output_tokens']:,} |")
        lines+=['','Full-study authoring: '+str(full['authoring_total']),
                '', 'Paired c-minus-control estimates, honest noninferiority intervals, monitor usage and attack-generation outcomes are in results-full/summary.json. Partial results cannot establish the preregistered benefit criterion.']
    else:
        lines+=['','The full study was not run.']
    if stop:
        lines+=['','## Stop','',stop['error']+' The retained provider error text identifies ECONNRESET: connection to the API was lost. The only assistant model field in that failed call is <synthetic>; no real alternate served model was returned.', '', 'No calls were made after this active global stop. Missing observations are not rejections and cannot pass the gate.']
    lines+=['','## Provenance and limitations','',
        'PREREG-T1b.md and HASHES were submitted to OpenTimestamps before any model call (commit 220ca61). Calendar receipts are retained; Bitcoin confirmation is not asserted.',
        '', 'A1 (commit 160fc5a) corrects an overly strict supplementary canonical-ID check before any decision was inspected or scored. The first Haiku response served exactly claude-haiku-4-5-20251001, with canonical shorthand claude-haiku-4-5. The original stop and response remain preserved. A1 was independently frozen/timestamped before continuation; the response was reused without resampling. Exact served-model guards remain enforced.',
        '', 'All original T1 frozen hashes remain unchanged. Thirteen offline T1b tests passed, including host sandbox confinement; the exact A1 equivalence test also passed.',
        '', 'All raw gate/full packets fit both context windows using a conservative byte bound. The largest 5,000-record raw prompt is 179,442 bytes, or 189,538 with output/wrapper reserves. Full evidence packets have separate exact-prompt context checks. No truncation is permitted.',
        '', 'This is a generated monotone RBAC fragment. Increasing records also increases background edge density. Gate-selected cells and unadjusted exploratory intervals do not support population-general claims.',
        '', '## Gate usage','',
        '| Role | Successful calls | Input tokens | Output tokens | Elapsed call seconds |',
        '|---|---:|---:|---:|---:|']
    for label,c in sorted(gate['cost_by_arm_role'].items()):
        lines.append(f"| {label} | {c['calls']} | {c['input_tokens']:,} | {c['output_tokens']:,} | {c['elapsed_s']:.1f} |")
    lines+=['',f"Total authoring list-price estimate: ${gate['authoring_total']['provider_list_price_usd_estimate']:.6f}. The failed request reported zero usage in its raw provider result; it returned no scored decision.", '', 'Provider list-price estimates, when reported, are not subscription charges. Authoring is counted once physically, including reused evidence.']
    (HOME/'RESULTS.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
