"""Post-run integrity audit; does not dispatch model calls or change scored data."""
from datetime import datetime
import json
from pathlib import Path

from ve_experiments.claude_cli import parse_stream, MODELS
from ve_experiments.t1.materials import packet
from ve_experiments.t1.protocol import JUDGE_SYSTEM
from ve_experiments.t1.run import HOME, load, save, verify


def main():
    timestamp=verify()
    directory=HOME/'results-gate'
    items={i['id']:i for i in load(HOME/'items-gate.json')}
    scores=[load(f) for f in (directory/'scores').glob('*.json')]
    expected={(identity,k) for identity in items for k in range(3)}
    assert {(s['item_id'],s['sample']) for s in scores}==expected and len(scores)==60
    assert not (directory/'STOP.json').exists()
    ledger=[]
    for file in (directory/'ledgers').glob('*.jsonl'):
        ledger.extend(json.loads(line) for line in file.read_text().splitlines())
    started=[r for r in ledger if r['status']=='started']
    completed={r['key']:r for r in ledger if r['status']=='ok'}
    assert len(started)==len(completed)==80 and len(ledger)==160
    assert all(r['account_label']=='danielsaeedi37' for r in ledger)
    assert min(datetime.fromisoformat(r['timestamp']) for r in started)>datetime.fromisoformat(timestamp['created_at'])
    assert len({r['controls']['binary_sha256'] for r in completed.values()})==1
    for row in completed.values():
        parsed=parse_stream(row['raw_stream'],MODELS['opus'])
        assert parsed['text']==row['text']
        assert row['served_model']==MODELS['opus']
        assert row['controls']['thinking_tokens']==1024 and row['controls']['effort']=='low'
    for score in scores:
        item=items[score['item_id']]
        row=completed[score['call_key']]
        assert score['arm']=='a' and score['judge']=='opus' and score['grants']==1500
        assert score['sabotaged']==item['sabotaged']
        assert row['system']==JUDGE_SYSTEM
        assert row['prompt']==packet(item)+'\nUNTRUSTED SUBMISSION:\n'+json.dumps({'claim':item['claim']})
        assert row['controls']['output_tokens']==6000
        assert not score['trusted_report']
    assert len({r['item_id'].split('/')[0] for r in started})==20
    result={'passed':True,'planned_and_observed_items':20,'planned_and_observed_judge_samples':60,
            'author_calls':20,'judge_calls':60,'retries':0,'failed_calls':0,'account':'danielsaeedi37',
            'served_model':MODELS['opus'],'freeze_verified':True,'ots_precedes_first_call':True,
            'all_judge_prompts_exact_raw_and_claim_only':True,'model_protocol_replayed':True,
            'all_sample_slots_unique_and_complete':True,'binary_hashes':sorted({r['controls']['binary_sha256'] for r in completed.values()}),
            'first_intent':min(r['timestamp'] for r in started),'last_result':max(r['timestamp'] for r in completed.values()),
            'notes':'Post-run audit script, not part of the preregistered analysis code. No model calls.'}
    save(directory/'integrity-audit.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
