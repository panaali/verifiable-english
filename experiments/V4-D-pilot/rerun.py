"""Amended, serial judge-only run; original stopped evidence is immutable."""
import argparse
from dataclasses import replace
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import subprocess

import run as original
from ve_experiments.claude_cli import ClaudeCLI, EndpointError, account_config, account_label

HERE = original.HERE
OLD = HERE / 'results'
OUT = HERE / 'results-judge-rerun'
ACCOUNT = 'danielsaeedi37'


def verify():
    manifest = json.loads((HERE / 'rerun-manifest.json').read_text())
    for name, expected in manifest['sha256'].items():
        if original.sha(original.ROOT / name) != expected:
            raise EndpointError('Amended freeze drift: ' + name)
    if (OUT / 'STOP.json').exists():
        raise EndpointError('Amended run permanently stopped')
    return manifest


class Runner(original.Runner):
    def __init__(self, config):
        self.manifest = verify()
        self.config = account_config(config)
        self.account = account_label(self.config)
        if self.account != ACCOUNT:
            raise EndpointError('This judge run requires account ' + ACCOUNT)
        self.date = self.manifest['context_date']
        self.spent = self.manifest['previous_calls'] + sum(
            json.loads(line)['status'] == 'started'
            for p in OUT.rglob('*ledger.jsonl') for line in p.read_text().splitlines())
        # One ledger per entire arm/judge cell makes account mixing impossible,
        # including across different items and resume processes.
        for path in (OUT / 'ledgers').glob('*ledger.jsonl'):
            if any(json.loads(line).get('account_label') != self.account for line in path.read_text().splitlines()):
                raise EndpointError('Account mixing in arm/judge cell')

    def sample(self, item_id, tag, model, system, prompt, k=0):
        verify()
        if self.spent >= 790:
            raise EndpointError('Global call ceiling reached')
        ledger = OUT / 'ledgers' / f'{tag}-{model}-ledger.jsonl'
        controls = replace(original.controls(model, self.date), thinking_tokens=None)
        client = ClaudeCLI(ledger, controls, account_config_dir=self.config)
        before = sum(json.loads(x)['status'] == 'started' for x in ledger.read_text().splitlines()) if ledger.exists() else 0
        try:
            row = client.sample(item_id + ':' + tag, system, prompt, k)
        except Exception as exc:
            rows = [json.loads(x) for x in ledger.read_text().splitlines()] if ledger.exists() else []
            last = rows[-1] if rows else {}
            stop = {'error': str(exc), 'item_id': item_id, 'arm': tag, 'judge': model,
                    'expected_model': original.MODELS[model],
                    'observed_model_ids': original.identities(last.get('raw_stream', '')),
                    'account_label': self.account, 'timestamp': datetime.now(timezone.utc).isoformat()}
            original.dump(OUT / 'STOP.json', stop)
            print(json.dumps(stop), flush=True)
            raise EndpointError('Amended run permanently stopped: ' + str(exc)) from exc
        after = sum(json.loads(x)['status'] == 'started' for x in ledger.read_text().splitlines())
        self.spent += after - before
        print(json.dumps({'calls_started_total': self.spent, 'item': item_id, 'arm': tag,
                          'judge': model, 'k': k, 'account_label': self.account,
                          'thinking_tokens': row['thinking_tokens_reported']}), flush=True)
        return row


def smoke(config):
    runner = Runner(config)
    for k in range(2):
        runner.sample('account-verification', 'smoke', 'haiku',
                      'You are an experimental text endpoint. Answer concisely.', 'Reply with exactly OK.', k)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('command', choices=['smoke', 'run'])
    p.add_argument('--account-config-dir')
    args = p.parse_args()
    OUT.mkdir(exist_ok=True)
    with (OUT / 'run.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.command == 'smoke':
            smoke(args.account_config_dir)
            return
        runner = Runner(args.account_config_dir)
        smoke_rows = [json.loads(x) for x in (OUT / 'ledgers/smoke-haiku-ledger.jsonl').read_text().splitlines()]
        if sum(r['status'] == 'ok' for r in smoke_rows) != 2:
            raise EndpointError('Two account verification calls required')
        original.OUT = OUT
        for item in original.read_items():
            artifacts = json.loads((OLD / 'artifacts' / (item['id'] + '.json')).read_text())
            for arm in original.ARMS:
                for model in original.JUDGES:
                    for k in range(2):
                        runner.judge(item, arm, model, k, artifacts[arm])


if __name__ == '__main__':
    main()
