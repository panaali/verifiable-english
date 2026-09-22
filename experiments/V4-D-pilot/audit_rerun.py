"""Read-only final cross-checks; writes only the audit report."""
import json
from collections import Counter
from rerun import HERE, OLD, OUT
import run as original


def main():
    manifest=json.loads((HERE/'rerun-manifest.json').read_text())
    hashes={name:original.sha(original.ROOT/name)==expected for name,expected in manifest['sha256'].items()}
    ledger=[json.loads(line) for p in (OUT/'ledgers').glob('*ledger.jsonl') for line in p.read_text().splitlines()]
    old=[json.loads(line) for p in OLD.rglob('*ledger.jsonl') for line in p.read_text().splitlines()]
    scores=[json.loads(p.read_text()) for p in (OUT/'scores').glob('*.json')]
    successful=[r for r in ledger if r['status']=='ok']
    ok={r['key']:r for r in successful}
    items=original.read_items()
    by_id={i['id']:i for i in items}
    expected={(i['id'],a,j,k) for i in items for a in original.ARMS for j in original.JUDGES for k in range(2)}
    actual={(r['item_id'],r['arm'],r['judge'],r['sample_index']) for r in scores}
    prompts=[]
    for score in scores:
        item=by_id[score['item_id']]
        artifact=json.loads((OLD/'artifacts'/f"{item['id']}.json").read_text())[score['arm']]
        system,prompt=original.judge_prompt(item,score['arm'],artifact)
        row=ok[score['key']]
        prompts.append(row['system']==system and row['prompt']==prompt)
    report={
        'frozen_files':len(hashes),'frozen_all_unchanged':all(hashes.values()),
        'frozen_mismatches':[p for p,v in hashes.items() if not v],
        'old_started':sum(r['status']=='started' for r in old),
        'new_started':sum(r['status']=='started' for r in ledger),
        'new_status_counts':dict(Counter(r['status'] for r in ledger)),
        'served_models':dict(Counter(r['served_model'] for r in successful)),
        'all_new_rows_expected_account':all(r.get('account_label')=='danielsaeedi37' for r in ledger),
        'all_served_models_match_request':all(r['served_model']==r['controls']['model'] for r in successful),
        'all_judges_default_thinking':all(r['controls']['thinking_tokens'] is None for r in ledger),
        'score_count':len(scores),'complete_grid':actual==expected and len(scores)==len(expected),
        'score_keys_unique':len({r['key'] for r in scores})==len(scores),
        'superseded_not_pooled':not ({r['key'] for r in scores}&{r['key'] for r in old}),
        'prompts_match_unchanged_arguments':all(prompts),
        'thinking_usage_missing':sum(r.get('thinking_tokens_reported') is None for r in successful),
        'thinking_above_old_1024':sum((r.get('thinking_tokens_reported') or 0)>1024 for r in successful),
        'stop_exists':(OUT/'STOP.json').exists(),
    }
    report['total_started']=report['old_started']+report['new_started']
    report['within_global_ceiling']=report['total_started']<=790
    attribution=[json.loads(line) for line in (HERE/'legacy-account-attribution.jsonl').read_text().splitlines()]
    report['historical_rows_attributed']=len(attribution)
    report['all_historical_rows_attributed_lead_main']=(len(attribution)==len(old) and
        all(r['account_label']=='lead-main' for r in attribution))
    if (OUT/'STOP.json').exists():
        stopped=json.loads((OUT/'STOP.json').read_text())['timestamp']
        report['post_stop_started_calls']=sum(r['status']=='started' and r['timestamp']>stopped for r in ledger)
    original.dump(OUT/'final-audit.json',report)
    print(json.dumps(report,indent=2))


if __name__=='__main__': main()
