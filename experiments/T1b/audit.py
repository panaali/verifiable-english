"""Independent post-run provenance audit. No endpoint calls or score changes."""
from datetime import datetime
import json
from ve_experiments.claude_cli import MODELS, parse_stream
from ve_experiments.t1b.materials import packet
from ve_experiments.t1b.protocol import JUDGE_SYSTEM
from ve_experiments.t1b.run import HOME, ROOT, CELLS, load, save, sha, verify, passing_cells


def main():
    timestamp=verify()
    for line in (ROOT/'experiments/T1/HASHES').read_text().splitlines():
        digest,name=line.split('  ',1)
        assert sha(ROOT/name)==digest,name
    result={'freeze_verified':True,'original_t1_unchanged':True,'splits':{}}
    for split in ('gate','full'):
        directory=HOME/f'results-{split}'
        if not directory.exists():continue
        items={i['id']:i for i in load(HOME/f'items-{split}.json')}
        cells=CELLS if split=='gate' else passing_cells()
        arms=('a',) if split=='gate' else ('a','b-exec','b-prime','c','d')
        expected={(i['id'],arm,judge,k) for size,judge in cells for i in items.values() if i['grants']==size for arm in arms for k in range(3)}
        scores=[load(f) for f in (directory/'scores').glob('*.json')]
        observed={(r['item_id'],r['arm'],r['judge'],r['sample']) for r in scores}
        assert len(observed)==len(scores) and observed<=expected
        records=[]
        for file in (directory/'ledgers').glob('*.jsonl'):
            with file.open() as stream:records.extend(json.loads(line) for line in stream)
        started=[r for r in records if r['status']=='started']
        completed={r['key']:r for r in records if r['status']=='ok'}
        failed=[r for r in records if r['status'] in ('error','infrastructure_error')]
        assert len({r['key'] for r in started})==len(started)
        assert all(r['account_label']=='danielsaeedi37' for r in records)
        assert all(datetime.fromisoformat(r['timestamp'])>datetime.fromisoformat(timestamp['created_at']) for r in started)
        binary=load(HOME/'context-preflight.json')['cli_binary_sha256']
        assert all(r['controls']['binary_sha256']==binary for r in started)
        for row in completed.values():
            parsed=parse_stream(row['raw_stream'],row['controls']['model'])
            assert parsed['text']==row['text']
            assert row['served_model']==row['controls']['model']
            assert row['controls']['context_date']==row['timestamp'][:10]
        for score in scores:
            item=items[score['item_id']]
            row=completed[score['call_key']]
            assert score['sabotaged']==item['sabotaged'] and score['grants']==item['grants']
            assert row['controls']['model']==MODELS[score['judge']]
            assert row['controls']['output_tokens']==6000
            if score['arm']=='a':
                assert row['system']==JUDGE_SYSTEM
                assert row['prompt']==packet(item)+'\nUNTRUSTED SUBMISSION:\n'+json.dumps({'claim':item['claim']})
                assert not score['trusted_report']
        result['splits'][split]={'expected_decisions':len(expected),'observed_decisions':len(observed),'complete':observed==expected,
            'started_calls':len(started),'successful_calls':len(completed),'failed_calls':len(failed),
            'all_observed_slots_valid_unique':True,'all_raw_arm_prompts_exact':True,'protocol_streams_replayed':True,
            'served_models':sorted({r['served_model'] for r in completed.values()}),
            'first_intent':min((r['timestamp'] for r in started),default=None),
            'last_result':max((r['timestamp'] for r in completed.values()),default=None),
            'failed_errors':[r.get('error') for r in failed]}
    result['stop']=load(HOME/'STOP.json') if (HOME/'STOP.json').exists() else None
    result['provenance_checks_passed']=True
    save(HOME/'integrity-audit.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
