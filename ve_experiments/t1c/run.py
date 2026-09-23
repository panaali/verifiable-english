"""T1c runner: separating certificates for "cannot access" claims.

Commands (repository root, UV_CACHE_DIR=/private/tmp/ve-uv-cache-t4):
  prepare   generate items, certificates and trusted verdicts offline; write HASHES
  stamp     OpenTimestamps receipts for PREREG-T1c.md and HASHES
  gate      20 items x {haiku-raw, opus-raw} x k=3 at 20,000 grants   (model calls)
  full      only after gate CONTINUE: 80 items x 4 arms x k=3         (model calls)
  report    summaries from saved decisions (no calls)
`--backend oracle|random|approve|reject` exercises the whole pipeline offline with
synthetic monitors (no calls) into results-<split>-<backend>/.
"""
import argparse
from datetime import datetime, timedelta, timezone
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import time

from . import certificates as C
from . import protocol as p
from .materials import dataset, packet
from .metrics import gate as gate_decision, rate, summarize

ROOT = Path(__file__).resolve().parents[2]
HOME = ROOT / 'experiments/T1c'
K = {'gate': 3, 'full': 1, 'dev': 1}  # samples per item and arm
DEFAULT_ACCOUNT = 'danielsaeedi37'
NOT_BEFORE = '2026-09-23T06:00:00+00:00'  # 23:00 PDT on 2026-09-22
FAKE_BACKENDS = ('oracle', 'random', 'approve', 'reject')
CLI_SHA256 = '387a5c5dcdbb815085edf0baf79591f9d8894efe922bceaf3d75b1b08055229d'  # claude 2.1.280, as in T1b


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    tmp.replace(path)


def load(path):
    return json.loads(Path(path).read_text())


def save_gz(path, value):
    path.write_bytes(gzip.compress(json.dumps(value, sort_keys=True).encode(), mtime=0))


def load_gz(path):
    return json.loads(gzip.decompress(Path(path).read_bytes()))


def items(split):
    return load_gz(HOME / f'items-{split}.json.gz')


def evidence(split):
    return load_gz(HOME / f'evidence-{split}.json.gz')


# ---------------------------------------------------------------- offline preparation

def build_evidence(split_items, *, lean=True):
    result = {}
    for item in split_items:
        sub = C.build(item)
        cert = sub.pop('certificate')
        forged = sub.pop('forged_leaves')
        full = {**sub, 'certificate': cert}
        ve = C.ve_verdict(item, full, lean=lean)
        script = C.script_verdict(item, full)
        result[item['id']] = {'submission': full, 'forged_leaves': forged, 've_report': ve, 'script_report': script}
    return result


def offline_checks(split, split_items, ev):
    rows = []
    for item in split_items:
        e = ev[item['id']]
        ve, script = e['ve_report'], e['script_report']
        rows.append({'id': item['id'], 'grants': item['grants'], 'sabotaged': item['sabotaged'],
                     'kind': item['sabotage_kind'], 'set_size': ve['set_size'],
                     've_python_valid': ve['python_replay'] == 'Valid', 've_lean_valid': ve['lean_replay_valid'],
                     've_verdict': ve['verdict'], 'script_verdict': script['verdict'],
                     'replay_steps': ve['python_replay_steps'],
                     'statement_matches_claim': ve['statement'] == item['claim'],
                     'rule_decision_ve': p.rule_decision(item, ve), 'rule_decision_script': p.rule_decision(item, script)})
    summary = {}
    for size in sorted({r['grants'] for r in rows}):
        cell = [r for r in rows if r['grants'] == size]
        honest = [r for r in cell if not r['sabotaged']]
        bad = [r for r in cell if r['sabotaged']]
        summary[str(size)] = {
            'true_claims': len(honest),
            'true_claims_certified_python_and_lean': sum(r['ve_python_valid'] and r['ve_lean_valid'] for r in honest),
            'certification_rate': sum(r['ve_python_valid'] and r['ve_lean_valid'] for r in honest) / max(1, len(honest)),
            've_script_verdict_agreement': sum(r['ve_verdict'] == r['script_verdict'] for r in cell) / len(cell),
            'sabotaged': len(bad),
            'sabotaged_certificates_valid_for_claim': sum(r['ve_verdict'] == 'VALID' and r['statement_matches_claim'] for r in bad),
            'sabotaged_by_kind': {k: {'n': sum(r['kind'] == k for r in bad),
                                      've_valid_for_other_statement': sum(r['kind'] == k and r['ve_verdict'] == 'VALID' for r in bad)}
                                  for k in sorted({r['kind'] for r in bad})},
            'rule_checker_only': {'false_approval': sum(r['rule_decision_ve'] == 'APPROVE' for r in bad),
                                  'honest_completion': sum(r['rule_decision_ve'] == 'APPROVE' for r in honest)},
            'rule_script_only': {'false_approval': sum(r['rule_decision_script'] == 'APPROVE' for r in bad),
                                 'honest_completion': sum(r['rule_decision_script'] == 'APPROVE' for r in honest)},
            'max_replay_steps': max(r['replay_steps'] for r in cell),
            'set_size_range': [min(r['set_size'] for r in cell), max(r['set_size'] for r in cell)]}
    return {'split': split, 'summary': summary, 'rows': rows}


def context_rows(split, split_items, ev):
    rows = []
    for item in split_items:
        e = ev[item['id']]
        key = b'0' * 32
        raw_system, raw_user = p.prompts(item, 'haiku-raw')
        report = e['ve_report']
        ve_system, ve_user = p.prompts(item, 'haiku-ve', submission=e['submission'], report=report,
                                       key=key, signature=p.sign(key, report))
        for arm, system, user in (('raw', raw_system, raw_user), ('certificate', ve_system, ve_user)):
            size = len((system + user).encode())
            policy_lines = sum(body.count('\n') - 1 for body in item['raw'].values())
            policy_bytes = sum(len(body.encode()) for body in item['raw'].values())
            ids = sum(len(line.split(' ')) for body in item['raw'].values() for line in body.splitlines()[1:])
            # Calibration: T1b Haiku ledgers, 12.0 tokens per two-identifier CSV line, i.e. about
            # 6 tokens per identifier; other text at about 2 UTF-8 bytes per token.
            estimate = 6 * ids + 2 * policy_lines + (size - policy_bytes) // 2
            rows.append({'split': split, 'item_id': item['id'], 'grants': item['grants'], 'prompt': arm,
                         'utf8_bytes': size, 'identifiers': ids, 'estimated_tokens': estimate,
                         'estimated_fits_haiku_with_reserves': estimate + 6000 + 4096 <= 200000,
                         'byte_bound_fits_haiku': size + 6000 + 4096 <= 200000,
                         'byte_bound_fits_opus': size + 6000 + 4096 <= 1000000})
    return rows


def prepare(*, lean=True, force=False):
    if (HOME / 'HASHES').exists() and not force:
        raise RuntimeError('Already frozen; never regenerate after any model call')
    checks, ctx = {}, []
    for split in ('dev', 'gate', 'full'):
        split_items = dataset(split)
        save_gz(HOME / f'items-{split}.json.gz', split_items)
        ev = build_evidence(split_items, lean=lean)
        save_gz(HOME / f'evidence-{split}.json.gz', ev)
        checks[split] = offline_checks(split, split_items, ev)
        ctx.extend(context_rows(split, split_items, ev))
        print(json.dumps({split: checks[split]['summary']}, indent=1), flush=True)
    save(HOME / 'offline-checks.json', {'created_at': now(), 'model_calls': 0, 'lean_executable_sha256': sha(C.LEAN), **checks})
    save(HOME / 'context-preflight.json', {'created_at': now(), 'model_calls': 0, 'rows': ctx,
         'limits': {'haiku': 200000, 'opus': 1000000}, 'reserves': {'output': 6000, 'wrapper': 4096},
         'method': 'UTF-8 byte upper bound (tokens <= bytes); offline estimate calibrated on T1b Haiku ledgers '
                   '(about 6 tokens per identifier). The runner performs a native count_tokens check for every '
                   'prompt of a split before its first generation call and aborts if any prompt does not fit.'})
    freeze()


def frozen_files():
    return sorted([ROOT / 'design/crypto-inspired-oversight.md', ROOT / 'design/frontier-failure-modes-and-ve.md',
                   HOME / 'PREREG-T1c.md', HOME / 'README.md', HOME / 'known-answer.json', HOME / 'offline-checks.json', HOME / 'context-preflight.json',
                   *HOME.glob('items-*.json.gz'), *HOME.glob('evidence-*.json.gz'),
                   *sorted((ROOT / 've_experiments/t1c').glob('*.py')), ROOT / 'tests/test_t1c.py',
                   ROOT / 'pyproject.toml', ROOT / 'uv.lock', *sorted((ROOT / 've').glob('*.py')), C.LEAN])


def freeze():
    (HOME / 'HASHES').write_text(''.join(f'{sha(f)}  {f.relative_to(ROOT)}\n' for f in frozen_files()))


def ots(*args):
    env = dict(os.environ, UV_CACHE_DIR='/private/tmp/ve-uv-cache-t4', UV_TOOL_DIR='/private/tmp/ve-t1c-uv-tools')
    command = ['uvx', '--from', 'opentimestamps-client', 'ots', *map(str, args)]
    proc = subprocess.run(command, capture_output=True, text=True, env=env, timeout=180)
    return {'command': command, 'returncode': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr, 'at': now()}


def _receipt_ok(name):
    info = ots('info', str(HOME / name) + '.ots')
    good = (not info['returncode'] and ('File sha256 hash: ' + sha(HOME / name)) in info['stdout']
            and any(x in info['stdout'] for x in ('PendingAttestation(', 'BitcoinBlockHeaderAttestation(')))
    return good, info


def stamp():
    receipts = []
    for name in ('PREREG-T1c.md', 'HASHES'):
        if not (HOME / (name + '.ots')).exists():
            receipt = ots('stamp', HOME / name)
            receipts.append(receipt)
            if receipt['returncode']:
                save(HOME / 'timestamp-submission.json', receipts)
                raise RuntimeError('OTS submission failed')
        good, info = _receipt_ok(name)
        receipts.append(info)
        if not good:
            save(HOME / 'timestamp-submission.json', receipts)
            raise RuntimeError('Unbound or missing timestamp receipt for ' + name)
    save(HOME / 'timestamp-submission.json', receipts)
    save(HOME / 'timestamp.json', {'created_at': now(), 'status': 'bound_calendar_submission_pending_bitcoin',
                                   'bitcoin_verified': False,
                                   **{name: sha(HOME / name) for name in ('PREREG-T1c.md', 'HASHES', 'PREREG-T1c.md.ots', 'HASHES.ots')}})


def verify():
    for line in (HOME / 'HASHES').read_text().splitlines():
        expected, name = line.split('  ', 1)
        if sha(ROOT / name) != expected:
            raise RuntimeError('Preregistered file changed: ' + name)
    receipt = load(HOME / 'timestamp.json')
    for name in ('PREREG-T1c.md', 'HASHES', 'PREREG-T1c.md.ots', 'HASHES.ots'):
        if sha(HOME / name) != receipt[name]:
            raise RuntimeError('Timestamp binding changed: ' + name)
    for name in ('PREREG-T1c.md', 'HASHES'):
        if not _receipt_ok(name)[0]:
            raise RuntimeError('Timestamp proof failed to bind: ' + name)
    return receipt


# ---------------------------------------------------------------- monitor calls

class Runner:
    def __init__(self, split, backend='claude', account=DEFAULT_ACCOUNT):
        self.split, self.backend, self.account = split, backend, account
        suffix = '' if backend == 'claude' else '-' + backend
        self.directory = HOME / f'results-{split}{suffix}'
        self.directory.mkdir(parents=True, exist_ok=True)
        if (self.directory / 'STOP.json').exists():
            raise RuntimeError('Immutable integrity stop; see STOP.json')
        key_file = self.directory / 'verdict-key.bin'
        if not key_file.exists():
            key_file.write_bytes(os.urandom(32))
            key_file.chmod(0o600)
        self.key = key_file.read_bytes()
        meta = self.directory / 'run.json'
        if not meta.exists():
            save(meta, {'started': now(), 'split': split, 'backend': backend, 'account': account, 'k': K[split],
                        'freeze_sha256': sha(HOME / 'HASHES') if (HOME / 'HASHES').exists() else None, 'serial': True})
        self.clients, self.last = {}, {}

    def account_dir(self):
        return Path.home() / f'.claude-{self.account}'

    def controls(self, model, day):
        from .transport import Controls, MODELS
        return Controls(model=MODELS[model], thinking_tokens=1024, effort='low', output_tokens=6000,
                        timeout_s=600, working_directory='/private/tmp/ve-t1c-claude-empty', context_date=day)

    def fake(self, item, key):
        digest = hashlib.sha256(key.encode()).digest()
        decision = {'oracle': 'REJECT' if item['sabotaged'] else 'APPROVE',
                    'random': 'APPROVE' if digest[0] % 2 else 'REJECT',
                    'approve': 'APPROVE', 'reject': 'REJECT'}[self.backend]
        self.last = {'input_tokens': 0, 'output_tokens': 0, 'key': 'fake:' + key}
        return {'decision': decision, 'reason': 'synthetic ' + self.backend + ' monitor'}

    def ask(self, model, key, system, prompt, sample, item):
        if self.backend in FAKE_BACKENDS:
            return self.fake(item, f'{key}/{sample}')
        from .transport import ClaudeCLI, InfrastructurePaused, MODELS
        from .context import check as context_check
        if datetime.now(timezone.utc) < datetime.fromisoformat(NOT_BEFORE):
            raise RuntimeError(f'Monitor calls are not permitted before {NOT_BEFORE}')
        while (datetime.now(timezone.utc) + timedelta(seconds=1300)).date() != datetime.now(timezone.utc).date():
            print(json.dumps({'event': 'waiting_for_utc_date_boundary'}), flush=True)
            time.sleep(30)
        day = datetime.now(timezone.utc).date().isoformat()
        tag = f'{model}-judge-{self.account}-{day}'
        prior = []
        for ledger in sorted((self.directory / 'ledgers').glob(f'{model}-judge-*.jsonl')):
            for line in ledger.open():
                old = json.loads(line)
                if old['item_id'] == key and old['sample_index'] == sample:
                    prior.append(old)
                    if old['system'] != system or old['prompt'] != prompt:
                        raise RuntimeError('Logical request content changed')
                    if old['status'] == 'ok':
                        if old['account_label'] != self.account or old['served_model'] != MODELS[model]:
                            raise RuntimeError('Cross-account or cross-model response reuse')
                        self.last = old
                        return p.as_json(old['text'])
        if prior and prior[-1]['status'] == 'refusal':
            from .transport import Refusal
            raise Refusal('Previously recorded refusal')
        if prior and prior[-1]['status'] not in ('infrastructure_error', 'retry_scheduled'):
            raise RuntimeError('Logical request previously started or failed without a classified infrastructure failure')
        if sha(shutil.which('claude')) != CLI_SHA256:
            raise RuntimeError('CLI binary changed from preregistration')
        if tag not in self.clients:
            self.clients[tag] = ClaudeCLI(self.directory / f'ledgers/{tag}.jsonl', self.controls(model, day),
                                          account_config_dir=self.account_dir(), infrastructure_retries=True)
        client = self.clients[tag]
        client.resume_pending = bool(prior)
        context = context_check(model, system, prompt, client.controls.output_tokens, self.account_dir())
        save(self.directory / 'context' / (hashlib.sha256(f'{key}/{sample}'.encode()).hexdigest() + '.json'), context)
        if not context['fits']:
            raise RuntimeError(f'CONTEXT_DOES_NOT_FIT: {model} {key} {context}')
        row = client.sample(key, system, prompt, sample)
        usage = row.get('model_usage', {}).get(MODELS[model], {})
        if row['input_tokens'] + client.controls.output_tokens > usage.get('contextWindow', 0):
            raise RuntimeError('Observed input/output reserve exceeds served context')
        self.last = row
        print(json.dumps({'event': 'call_ok', 'key': key, 'sample': sample, 'model': model,
                          'input_tokens': row['input_tokens'], 'output_tokens': row['output_tokens']}), flush=True)
        return p.as_json(row['text'])

    def judge(self, item, arm, sample, ev):
        path = self.directory / 'scores' / f'{item["id"]}-{arm}-{sample}.json'
        if path.exists():
            return load(path)
        model = p.JUDGE[arm]
        submission = report = signature = None
        if arm in ('haiku-ve', 'haiku-script'):
            submission = ev['submission']
            report = ev['ve_report'] if arm == 'haiku-ve' else ev['script_report']
            signature = p.sign(self.key, report)  # Trusted harness signs; prompts() verifies before display.
        system, user = p.prompts(item, arm, submission=submission, report=report, key=self.key, signature=signature)
        from .transport import Refusal
        try:
            response = self.ask(model, f'{item["id"]}/{arm}/decision', system, user, sample, item)
        except Refusal as exc:
            row = {'item_id': item['id'], 'grants': item['grants'], 'arm': arm, 'judge': model, 'sample': sample,
                   'sabotaged': item['sabotaged'], 'sabotage_kind': item['sabotage_kind'], 'decision': 'REFUSAL',
                   'counts_as_sample': False, 'error': str(exc)}
            save(path, row)
            return row
        row = {'item_id': item['id'], 'grants': item['grants'], 'arm': arm, 'judge': model, 'sample': sample,
               'sabotaged': item['sabotaged'], 'sabotage_kind': item['sabotage_kind'],
               'decision': p.decision_of(response), 'response': response, 'trusted_report': report,
               'input_tokens': self.last.get('input_tokens', 0), 'output_tokens': self.last.get('output_tokens', 0),
               'call_key': self.last.get('key')}
        save(path, row)
        return row


def preflight_context(runner, split_items, ev, arms):
    """Native token counts for every distinct prompt of the split before any generation call."""
    if runner.backend in FAKE_BACKENDS:
        return
    from .context import check as context_check
    for item in split_items:
        for arm in arms:
            e = ev[item['id']]
            report = None if arm.endswith('raw') else (e['ve_report'] if arm == 'haiku-ve' else e['script_report'])
            system, user = p.prompts(item, arm, submission=e['submission'], report=report, key=runner.key,
                                     signature=None if report is None else p.sign(runner.key, report))
            path = runner.directory / 'context-preflight' / f'{item["id"]}-{arm}.json'
            if not path.exists():
                save(path, context_check(p.JUDGE[arm], system, user, 6000, runner.account_dir()))
            if not load(path)['fits']:
                raise RuntimeError(f'CONTEXT_DOES_NOT_FIT before generation: {item["id"]} {arm}')


def run(split, backend='claude', account=DEFAULT_ACCOUNT):
    if backend == 'claude':
        verify()
    if split == 'full':
        gate_result = report('gate', backend)['gate']
        if gate_result['decision'] != 'CONTINUE':
            print(json.dumps({'full_study': 'not run', 'gate': gate_result['decision']}), flush=True)
            return
    runner = Runner(split, backend, account)
    split_items, ev = items(split), evidence(split)
    arms = p.GATE_ARMS if split == 'gate' else p.ARMS
    sizes = sorted({i['grants'] for i in split_items})
    by_size = {s: [i for i in split_items if i['grants'] == s] for s in sizes}
    # Interleave sizes round-robin by item index (unequal counts continue with the larger size).
    ordered = [by_size[s][j] for j in range(max(map(len, by_size.values()))) for s in sizes if j < len(by_size[s])]
    preflight_context(runner, ordered, ev, arms)
    try:
        for index, item in enumerate(ordered):
            for sample in range(K[split]):
                shift = (index + sample) % len(arms)
                for arm in arms[shift:] + arms[:shift]:
                    runner.judge(item, arm, sample, ev[item['id']])
    except Exception as exc:
        from .transport import InfrastructurePaused
        if isinstance(exc, InfrastructurePaused):
            save(runner.directory / 'PAUSE.json', {'at': now(), 'error': str(exc), 'resumable': True})
        else:
            save(runner.directory / 'STOP.json', {'at': now(), 'error': type(exc).__name__ + ': ' + str(exc), 'resample': False})
        report(split, backend)
        raise
    if (runner.directory / 'PAUSE.json').exists():
        (runner.directory / 'PAUSE.json').unlink()
    print(json.dumps(report(split, backend), indent=1), flush=True)


def report(split, backend='claude'):
    suffix = '' if backend == 'claude' else '-' + backend
    directory = HOME / f'results-{split}{suffix}'
    everything = [load(f) for f in sorted((directory / 'scores').glob('*.json'))] if directory.exists() else []
    refusals = [r for r in everything if r['decision'] == 'REFUSAL']
    rows = [r for r in everything if r['decision'] != 'REFUSAL']
    result = summarize(rows)
    if split == 'gate':
        result['gate'] = gate_decision(everything, items('gate'), K['gate'])
    expected = len(items(split)) * K[split] * len(p.GATE_ARMS if split == 'gate' else p.ARMS)
    result.update(expected_decisions=expected, observed_decisions=len(rows), missing_decisions=expected - len(everything),
                  refusals=[{k: r[k] for k in ('item_id', 'arm', 'sample', 'error')} for r in refusals],
                  invalid_decisions=sum(r['decision'] == 'INVALID' for r in rows), backend=backend,
                  offline=load(HOME / 'offline-checks.json')[split]['summary'] if (HOME / 'offline-checks.json').exists() else None)
    if directory.exists():
        save(directory / 'summary.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=('prepare', 'freeze', 'stamp', 'gate', 'full', 'report'))
    parser.add_argument('--split', choices=('gate', 'full'), default='gate')
    parser.add_argument('--backend', choices=('claude',) + FAKE_BACKENDS, default='claude')
    parser.add_argument('--account', default=DEFAULT_ACCOUNT, help='account label; config ~/.claude-<label>')
    parser.add_argument('--no-lean', action='store_true', help='prepare only: skip Lean replay (development)')
    args = parser.parse_args()
    if args.command == 'prepare':
        return prepare(lean=not args.no_lean)
    if args.command == 'freeze':
        if any(HOME.glob('results-gate')) or any(HOME.glob('results-full')) or (HOME / 'HASHES.ots').exists():
            raise RuntimeError('Refreeze is only allowed before timestamping and before any model call')
        return freeze()
    if args.command == 'stamp':
        return stamp()
    if args.command == 'report':
        return print(json.dumps(report(args.split, args.backend), indent=1))
    lock_path = f'/private/tmp/ve-t1c-{args.account}.lock'
    with open(lock_path, 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run(args.command, args.backend, args.account)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        from .transport import InfrastructurePaused
        if isinstance(exc, InfrastructurePaused):
            sys.exit(75)
        raise
