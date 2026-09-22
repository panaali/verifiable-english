"""Complete-run presentation using the unchanged paired analysis and scoring."""
import json
import analyze_rerun
import audit_resume
import run as original
from rerun import HERE, OUT


def main():
    audit = audit_resume.main()
    assert audit['complete_grid'], 'Wait for the complete 480-sample grid'
    for key in ('effective_frozen_all_unchanged','changes_limited_to_authorized_transport_code',
                'pre_resume_ledger_prefixes_unchanged','previous_successes_never_restarted',
                'all_new_rows_expected_account','all_served_models_match_request','all_success_streams_reparsed',
                'all_judges_default_thinking','score_keys_unique','successful_keys_unique','superseded_not_pooled',
                'prompts_match_unchanged_arguments','scores_recomputed_match','historical_stop_preserved',
                'within_global_ceiling'):
        assert audit[key], key
    assert not audit['endpoint_stop_exists'] and not audit['pause_exists'] and not audit['unclassified_failures']
    analyze_rerun.main()
    summary = json.loads((OUT/'summary.json').read_text())
    # The frozen formatter treats every STOP as active. Preserve this historical
    # fact under an explicit name; only its presentation is superseded here.
    summary['historical_transport_stop'] = summary.pop('stop')
    summary['infrastructure_recovery'] = audit
    rows = [json.loads(line) for p in (OUT/'ledgers').glob('*ledger.jsonl') for line in p.read_text().splitlines()]
    verification = [r for r in rows if r['status']=='ok' and r['item_id'].startswith('account-verification:')]
    failures = [original.charged_usage(r) for r in rows if r['status'] in ('error','infrastructure_error')]
    def usage(rs):
        return {'calls':len(rs), **{k:sum(r.get(k) or 0 for r in rs) for k in
                ('input_tokens','output_tokens','thinking_tokens_reported')},
                **{k+'_missing':sum(r.get(k) is None for r in rs) for k in
                ('input_tokens','output_tokens','thinking_tokens_reported')}}
    summary['verification_usage'] = usage(verification)
    summary['infrastructure_failure_usage'] = usage(failures)
    scores = [json.loads(p.read_text()) for p in (OUT/'scores').glob('*.json')]
    failures_scored = [s for s in scores if not s['correct']]
    summary['incorrect_samples'] = [{k:s.get(k) for k in
        ('item_id','arm','judge','sample_index','valid','answer','label','false_approval','translation_caught')}
        for s in sorted(failures_scored,key=lambda s:(s['item_id'],s['arm'],s['judge'],s['sample_index']))]
    original.dump(OUT/'summary.json',summary)
    text = (HERE/'RESULTS.md').read_text()
    text = '\n'.join(line for line in text.splitlines() if not line.startswith('**STOPPED:**'))
    opening = ('**COMPLETE: 480/480 judgments, reusing all 128 pre-interruption scores and adding the remaining 352.** '
        'The [infrastructure amendment](AMENDMENT-INFRASTRUCTURE-2026-09-22.md) classifies connection errors, '
        'empty streams and synthetic placeholders without a served model as infrastructure failures, never samples. '
        'Retries retain request identity and are ledgered with 30/60/120/240/480-second backoff; exhaustion pauses resumably. '
        'The historical stop and failed raw stream are preserved. Real served-model mismatches still halt.\n\n')
    text = text.replace('# D pilot: amended judge results\n\n','# D pilot: amended judge results\n\n'+opening,1)
    metrics = summary['metrics']
    total = {j:sum(m['correct'] for key,m in metrics.items() if key.endswith('-'+j)) for j in original.JUDGES}
    attack = {j:metrics['mistranslation-'+j] for j in original.JUDGES}
    observed = (f"Sonnet answered {total['sonnet']}/240 judgments correctly and Haiku {total['haiku']}/240. "
        f"Haiku's misses comprised {sum(not s['valid'] for s in failures_scored if s['judge']=='haiku')} invalid answer formats and "
        f"{sum(s['false_approval'] for s in failures_scored if s['judge']=='haiku')} false approvals of dishonest attacks. "
        f"For eligible dishonest mistranslation attacks, Haiku rejected the advocated wrong answer in {attack['haiku']['answer_rejections']}/24 samples "
        f"and explicitly caught the translation flaw in {attack['haiku']['translation_catches']}/24; Sonnet's corresponding counts were "
        f"{attack['sonnet']['answer_rejections']}/24 and {attack['sonnet']['translation_catches']}/24. "
        'The attack rows combine these 24 dishonest samples with 24 honest samples. '
        'A certified deduction can still rest on a false translation, and noticing that flaw does not by itself guarantee a correct answer. '
        'The paired intervals above quantify differences on these 24 items; they do not establish a general ranking of oversight methods.\n\n')
    text = text.replace('## Interpretation\n\n','## Interpretation\n\n'+observed,1)
    text += '\n\n## Incorrect completed samples\n\n'
    text += '| Item | Arm | Judge | Sample | Valid answer | Answer | Gold | False approval | Translation caught |\n|---|---|---|---:|---|---|---|---|---|\n'
    for s in summary['incorrect_samples']:
        text += f"| {s['item_id']} | {analyze_rerun.NAMES[s['arm']]} | {s['judge'].title()} | {s['sample_index']} | {s['valid']} | {s['answer']} | {s['label']} | {s['false_approval']} | {s['translation_caught']} |\n"
    text += (f"\n## Audit and spend\n\n"
        f"All **{audit['frozen_files']} effective frozen files** and pre-resume ledger prefixes passed validation. "
        'All 128 prior scores are byte-for-byte unchanged; none of the 130 prior successful requests (including verification) was restarted. '
        'All 480 score keys are unique, prompts match the original argument artifacts, raw successful streams were reparsed, '
        'and scoring was independently recomputed. All replacement ledger rows use **danielsaeedi37**; '
        'all served models match their requested identities. Superseded original judges are not pooled. '
        f"Missing thinking usage: **{audit['thinking_usage_missing']}**.\n\n"
        f"There were **{audit['new_started']} replacement-stage physical starts**: 480 scored judgments, two account-verification successes, "
        f"and {audit['infrastructure_failures']} infrastructure failure(s). "
        f"The ledger records {audit['retry_events']} retry event(s), including recovery of the historical interruption. "
        f"Including {audit['old_started']} original starts, cumulative starts are **{audit['total_started']}/790**. "
        'Retry events are not additional starts until the next started record, and failed attempts never enter sample denominators. '
        'Verification and failed-attempt token usage, including missing-usage counts, are separate in `summary.json`. '
        'Zero reported failed-attempt usage does not prove that no provider-side work occurred.\n\n'
        '`resume-audit.json` records the complete audit. The original `rerun-manifest.json`, historical `STOP.json`, '
        'and prior `final-audit.json` remain preserved; `resume-manifest.json` documents the authorized backend/runner changes '
        'and exact evidence reused. Recovery code and freeze were committed as `5f56803` before resumed calls. '
        '45 targeted offline tests passed for retries, exhaustion/resume, endpoint/account isolation and pilot mechanisms.\n')
    text += '\nReproduce this report and audit without model calls:\n\n```sh\nUV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/V4-D-pilot/report_resume.py\n```\n'
    (HERE/'RESULTS.md').write_text('\n'.join(line.rstrip() for line in text.splitlines())+'\n')


if __name__=='__main__': main()
