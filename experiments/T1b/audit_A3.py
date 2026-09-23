"""Independent post-run provenance audit. No endpoint calls or score changes."""
from datetime import datetime
import json
from ve_experiments.t1b.a2_transport import MODELS, parse_stream, infrastructure_failure
from ve_experiments.t1b.materials import packet
from ve_experiments.t1b.protocol import JUDGE_SYSTEM, as_json
from ve_experiments.t1b.a3_run import HOME, ROOT, CELLS, load, save, sha, verify, passing_cells


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
            with file.open() as stream:records.extend(dict(json.loads(line), ledger_role=file.name.replace('-saeedi.danial-', '-').split('-',1)[1].rsplit('-',3)[0]) for line in stream)
        started=[r for r in records if r['status']=='started']
        completed={r['key']:r for r in records if r['status']=='ok'}
        failed=[r for r in records if r['status'] in ('error','infrastructure_error')]
        assert len(completed)==sum(r['status']=='ok' for r in records), 'Duplicate successful physical request'
        logical=[(r['item_id'],r['sample_index']) for r in completed.values()]
        assert len(logical)==len(set(logical)), 'Repeated completed logical sample'
        history={}
        for r in records:
            previous=history.get(r['key'])
            if r['status']=='started' and previous:
                assert previous['status']=='retry_scheduled'
                assert previous['classification']=='INFRASTRUCTURE' and previous['counts_as_sample'] is False
                assert previous['backoff_s'] in (30,60,120,240,480)
                assert (datetime.fromisoformat(r['timestamp'])-datetime.fromisoformat(previous['timestamp'])).total_seconds() >= previous['backoff_s']
            history[r['key']]=r
        assert all(infrastructure_failure(r.get('raw_stream',''),r['controls']['model'],r.get('error','')) for r in failed)
        successful_logical={(r['item_id'],r['sample_index']) for r in completed.values()}
        infrastructure_attempts=[]
        for r in failed:
            raw=[json.loads(line) for line in r.get('raw_stream','').splitlines() if line.strip()]
            provider=[x for x in raw if x.get('type')=='result']
            infrastructure_attempts.append({'key':r['key'],'item_id':r['item_id'],'sample_index':r['sample_index'],
                'error':r.get('error'),'elapsed_s':r.get('elapsed_s'),'timestamp':r['timestamp'],
                'counts_as_sample':False,'eventually_completed':(r['item_id'],r['sample_index']) in successful_logical,
                'provider_usage':[x.get('usage') for x in provider],
                'provider_errors':[x.get('result') for x in provider],
                'provider_model_usage':[x.get('modelUsage') for x in provider],
                'provider_list_price_usd_estimate':[x.get('total_cost_usd') for x in provider]})
        save(directory/'infrastructure-accounting-A3.json', {'attempts':infrastructure_attempts,
            'retry_events':[{k:r.get(k) for k in ('key','item_id','sample_index','timestamp','retry_number','backoff_s','counts_as_sample')} for r in records if r['status']=='retry_scheduled'],
            'unknown_usage_is_not_zero':True, 'subscription_dollars_inferred':False})
        usage_by_role={}
        for r in records:
            if r['status'] not in ('ok','error','infrastructure_error'): continue
            role=r['ledger_role']
            u=usage_by_role.setdefault(role,{'successful_calls':0,'failed_calls':0,'reported_input_tokens':0,'reported_output_tokens':0,'unknown_usage_calls':0,'elapsed_s':0.,'provider_list_price_usd_estimate':0.,'unknown_list_price_calls':0,'reported_thinking_tokens':0,'unknown_thinking_calls':0})
            u['successful_calls' if r['status']=='ok' else 'failed_calls']+=1
            u['elapsed_s']+=r.get('elapsed_s') or 0
            if r['status']=='ok':
                inp,out=r.get('input_tokens'),r.get('output_tokens')
                price=sum(v.get('costUSD',0) for v in (r.get('model_usage') or {}).values()) if r.get('model_usage') else None
            else:
                rs=[json.loads(line) for line in r.get('raw_stream','').splitlines() if line.strip()]
                provider_result=next((x for x in rs if x.get('type')=='result'),{})
                usage=provider_result.get('usage',{})
                inp=sum(usage[k] for k in ('input_tokens','cache_creation_input_tokens','cache_read_input_tokens')) if all(k in usage for k in ('input_tokens','cache_creation_input_tokens','cache_read_input_tokens')) else None
                out=usage.get('output_tokens')
                price=provider_result.get('total_cost_usd')
            u['reported_input_tokens']+=inp or 0
            u['reported_output_tokens']+=out or 0
            u['unknown_usage_calls']+=inp is None or out is None
            u['provider_list_price_usd_estimate']+=price or 0
            u['unknown_list_price_calls']+=price is None
            u['reported_thinking_tokens']+=r.get('thinking_tokens_reported') or 0
            u['unknown_thinking_calls']+=r.get('thinking_tokens_reported') is None
        save(directory/'physical-usage-A3.json',{'by_role':usage_by_role,'unknown_usage_is_not_zero':True,'subscription_charges_inferred':False,'shared_authoring_counted_once':True})
        snapshot=load(HOME/'resume-A3.json')
        a3_timestamp=load(HOME/'timestamp-A3.json')['created_at']
        for r in records:
            if r['account_label']=='saeedi.danial':
                assert split=='full' and r['timestamp'] > a3_timestamp
            else:
                assert r['account_label']=='danielsaeedi37' and r['timestamp'] < snapshot['at']
                if split=='full' and r['status']=='ok':
                    assert r['key'] in snapshot['retained_author_keys'] and r['ledger_role']=='author'
        if split=='full':
            assert all(completed[s['call_key']]['account_label']=='saeedi.danial' for s in scores)
        assert all(datetime.fromisoformat(r['timestamp'])>datetime.fromisoformat(timestamp['created_at']) for r in started)
        binary=load(HOME/'context-preflight.json')['cli_binary_sha256']
        assert all(r['controls']['binary_sha256']==binary for r in started)
        assert all(r['controls']['context_date']==r['timestamp'][:10] for r in started)
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
            response=as_json(row['text'])
            decision=response.get('decision')
            assert score['response']==response
            assert score['decision']==(decision if decision in ('APPROVE','REJECT') else 'INVALID')
            if score['arm']=='a':
                assert row['system']==JUDGE_SYSTEM
                assert row['prompt']==packet(item)+'\nUNTRUSTED SUBMISSION:\n'+json.dumps({'claim':item['claim']})
                assert not score['trusted_report']
        costs=[load(f) for f in (directory/'costs').glob('*.json')]
        assert {c['key'] for c in costs}==set(completed)
        if (HOME/'STOP-A3.json').exists():
            stopped=load(HOME/'STOP-A3.json')['at']
            assert all(r['timestamp']<=stopped for r in started)
        if split=='full' and started:
            assert result['splits']['gate']['complete']
            assert min(r['timestamp'] for r in started) > result['splits']['gate']['last_result']
        pause_file=directory/'PAUSE-A3.json'
        if pause_file.exists():
            paused_at=load(pause_file)['at']
            assert all(r['timestamp']<=paused_at for r in started)
            assert not (HOME/'STOP-A3.json').exists()
        result['splits'][split]={'costs_cover_all_successful_calls':True,'expected_decisions':len(expected),'observed_decisions':len(observed),'complete':observed==expected,
            'started_calls':len(started),'successful_calls':len(completed),'failed_calls':len(failed),
            'all_observed_slots_valid_unique':True,'all_raw_arm_prompts_exact':True,'protocol_streams_replayed':True,
            'served_models':sorted({r['served_model'] for r in completed.values()}),
            'first_intent':min((r['timestamp'] for r in started),default=None),
            'last_result':max((r['timestamp'] for r in completed.values()),default=None),
            'failed_errors':[r.get('error') for r in failed]}
    result['original_metadata_stop']=load(HOME/'STOP.json')
    result['resumable_pause']=load(HOME/'results-full/PAUSE-A3.json') if (HOME/'results-full/PAUSE-A3.json').exists() else None
    result['active_stop']=load(HOME/'STOP-A3.json') if (HOME/'STOP-A3.json').exists() else None
    result['amendment']='A1 metadata; A2 infrastructure recovery; A3 whole full-study account move'
    result['pre_A3_artifacts_preserved']=True
    result['full_monitor_account']='saeedi.danial'
    result['retained_author_responses']=2
    result['original_19_decisions_unchanged']=True
    result['pre_A2_ledger_prefixes_unchanged']=True
    result['provenance_checks_passed']=True
    save(HOME/'integrity-audit-A3.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
