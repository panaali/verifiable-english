import json,os,signal,subprocess,time
from pathlib import Path
ledger=Path('/Users/seyran/code/ve-codex-v4/experiments/V4-fidelity/results/b/ledger.jsonl')
pid=43841
while True:
    result=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True)
    if 'experiments/V4-fidelity/run_b.py' not in result.stdout: break
    try: rows=[json.loads(s) for s in ledger.read_text().splitlines()]
    except json.JSONDecodeError:
        time.sleep(1);continue
    terminal=[r for r in rows if r['status']!='started']
    if len(terminal)>=180: break
    last=terminal[-2:]
    if len(last)==2 and all(r['status']=='error' and any(e in r.get('raw_stream','') for e in ('ENOTFOUND','ECONNRESET','ETIMEDOUT')) for r in last):
        os.kill(pid,signal.SIGSTOP)
        ledger.with_name('NETWORK-PAUSED.json').write_text(json.dumps({'pid':pid,'reason':'two consecutive transport failures; pause unstarted identities, no retries','samples':[[r['item_id'],r['sample_index']] for r in last]},indent=2)+'\n')
        print('NETWORK PAUSED',flush=True)
        break
    time.sleep(1)
