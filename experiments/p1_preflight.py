"""P1 gate execution. Default preflight never dispatches model generations."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

from experiments import p1 as p
from ve_experiments.paid import PaidRequest, PaidClient, Ledger, OpenRouterBackend, PreflightError

GATES = ('known-answer', 'lean-replay', 'semantic-pairs', 'test-suite', 'tokenizer', 'external-timestamp')


def receipt(name, stamp, fn):
    try:
        result = fn()
    except Exception as exc:
        result = {'passed': False, 'error': f'{type(exc).__name__}: {exc}'}
    result.update(freeze_sha256=stamp, completed_at=datetime.now(timezone.utc).isoformat())
    p.write_json(p.HERE / f'checks/{name}.json', result)
    print(f'{name}: {result["passed"]}' + (f' ({result["error"]})' if 'error' in result else ''), flush=True)
    return result


def semantic_pairs():
    pairs = []
    for item in p.materials('dev') + p.materials('scored'):
        f, _ = p.render(item, 'F')
        u, _ = p.render(item, 'U')
        a, _ = p.render(item, 'A')
        claim = p.assertion(item)
        same_packet = all(m[-1]['content'].startswith(p.packet(item)) for m in (f, u, a))
        same_claim = claim in f[-1]['content'] and u[-1]['content'] == p.packet(item) + '\nProposer message:\n' + claim
        correct = True
        if item['assignment']['source'] == 'E4':
            fc, _ = p.render(item, 'F_correct')
            correct = fc[-1]['content'] == p.packet(item) + '\nProposer message:\n' + a[1]['content']
        pairs.append({'item_id': item['id'], 'passed': same_packet and same_claim and correct,
                      'F_sha256': p.digest(f), 'U_sha256': p.digest(u), 'assertion': claim})
    return {'passed': bool(pairs) and all(x['passed'] for x in pairs), 'pairs': pairs,
            'method': 'exact assertion bytes, unchanged source packet, A/F_correct exact finding bytes'}


def timestamp():
    hashes = p.ROOT / 'experiments/PREREG-HASHES.txt'
    proof = hashes.with_suffix('.txt.ots')
    expected = p.sha(p.HERE / 'PREREG.md')
    matches = any(line.split() == [expected, 'experiments/P1-deference/PREREG.md']
                  for line in hashes.read_text().splitlines())
    env = dict(os.environ, UV_CACHE_DIR='/private/tmp/ve-uv-cache-codex', UV_TOOL_DIR='/private/tmp/ve-uv-tools')
    cmd = ['uvx', '--from', 'opentimestamps-client', 'ots', 'info', str(proof)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)
    pending = 'PendingAttestation(' in proc.stdout
    bitcoin = 'BitcoinBlockHeaderAttestation(' in proc.stdout
    bound = f'File sha256 hash: {p.sha(hashes)}' in proc.stdout
    passed = matches and bound and proc.returncode == 0 and (pending or bitcoin)
    return {'passed': passed, 'verified': passed, 'prereg_sha256_matches': matches,
            'proof_binds_hash_file': bound, 'hash_file_sha256': p.sha(hashes), 'proof_sha256': p.sha(proof),
            'status': 'bitcoin_attestation_present_unverified' if bitcoin else 'pending_calendar' if pending else 'invalid',
            'bitcoin_confirmed': False, 'pending_calendar_sufficient_for_pilot': True,
            'policy': 'Current PREREG hash and parseable bound OTS calendar submission suffice for this pilot; ots info does not verify Bitcoin confirmation.',
            'command': cmd, 'exit_code': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr}


def lean():
    exe = p.ROOT / 'lean/.lake/build/bin/ve_conformance'
    if not exe.exists():
        proc = subprocess.run(['lake', 'build'], cwd=p.ROOT / 'lean', capture_output=True, text=True)
        (p.HERE / 'checks/lean-build.log').write_text(proc.stdout + proc.stderr)
        if proc.returncode:
            raise PreflightError('lake build failed; see checks/lean-build.log')
    return p.lean_replay()


def test_suite():
    cmd = [sys.executable, '-m', 'pytest', '-q']
    proc = subprocess.run(cmd, cwd=p.ROOT, capture_output=True, text=True)
    (p.HERE / 'checks/test-suite.log').write_text(proc.stdout + proc.stderr)
    return {'passed': proc.returncode == 0, 'command': cmd, 'exit_code': proc.returncode,
            'stdout': proc.stdout, 'stderr': proc.stderr}


def token_requests(judge='pro'):
    """Joint native wire fixtures plus explicit worst-case generated-token reserves.

    No invented text purports to predict a future model response. Actual native
    signatures/history are counted again by PaidClient before every dispatch.
    """
    for split in ('dev', 'scored'):
        for item in p.materials(split):
            for arm in p.arms(item):
                req = p.request(item, arm, judge, 256)
                yield req, 0
                history = req.messages + [{'role': 'assistant', 'content': ''}]
                generated = p.JUDGE_OUTPUT_CAP
                if arm == 'R':
                    call = {'id': 'preflight-replay', 'name': 'replay', 'arguments': {'item_id': item['id']}}
                    assistant = {'role': 'assistant', 'content': '', 'tool_calls': [{
                        'id': call['id'], 'type': 'function', 'function': {'name': 'replay', 'arguments': p.packed(call['arguments'])}}]}
                    if judge == 'pro':
                        assistant = {'role': 'assistant', 'vertex_content': {'role': 'model', 'parts': [{
                            'function_call': {'name': 'replay', 'id': call['id'], 'args': call['arguments']}}]}}
                    history = req.messages + [assistant] + p.replay_response(item, [call])[0]
                    yield p.request(item, arm, judge, 256, phase='replay', messages=history, tools=[]), 1024
                    history += [{'role': 'assistant', 'content': ''}]
                    generated = 2048  # tool request and continuation each have a 1024-token ceiling
                if judge == 'pro' and item['assignment']['pushback'] and arm in p.MAIN:
                    wrappers = history + [{'role': role, 'content': ''} for role in ('user', 'assistant') * 3]
                    attacker = [{'role': 'system', 'content': (p.HERE / 'prompts/attacker.txt').read_text()},
                                *wrappers[1:], {'role': 'user', 'content': 'Provide the next proposer message.'}]
                    for phase, messages in (('attacker', attacker), ('pushback', wrappers)):
                        yield p.request(item, arm, judge, 256, phase=phase, turn=3, messages=messages, tools=[]), generated + p.PUSHBACK_HISTORY_RESERVE


def tokenize(backend, judge='pro'):
    fixtures = list(token_requests(judge))
    def count(pair):
        req, reserve = pair
        row = {'identity': req.identity, 'request_sha256': p.digest([req.messages, req.tools]),
               'generated_token_reserve': reserve, 'limit': req.max_input_tokens}
        try:
            n = backend.count(req)
            row.update(tokens=n, bounded_tokens=n + reserve, passed=n + reserve <= req.max_input_tokens)
        except Exception as exc:
            row.update(passed=False, error=f'{type(exc).__name__}: {exc}')
        return row
    # Only free Vertex countTokens calls are concurrent. Paid dispatch stays serial.
    if judge == 'pro':
        with ThreadPoolExecutor(max_workers=8) as pool:
            rows = list(pool.map(count, fixtures))
    else:
        rows = [count(pair) for pair in fixtures]
    return {'passed': bool(rows) and all(r['passed'] for r in rows), 'schedule': 'full_256',
            'scope': 'all dev+scored items, all arms, replay continuations, joint maximal pushback attacker/judge histories',
            'judge': judge, 'model': p.MODELS[judge], 'requests': len(rows), 'counts': rows,
            'future_history_policy': 'Full joint native fixtures plus generated-token ceilings; actual provider signatures and transcript are recounted at runtime. '
                + ('This is not a Qwen/Llama tokenizer receipt.' if judge == 'pro' else
                   'Local model-native template counts; served provider agreement requires the separate OpenRouter smoke check.'),
            'generation_calls': 0}


def refresh_status():
    path = p.HERE / 'freeze.json'
    freeze = json.loads(path.read_text())
    stamp = freeze['manifest_sha256']
    unresolved = []
    if not freeze['cost_ceilings'].get(freeze['selected_schedule'], {}).get('within_study_cap', False):
        unresolved.append(f'selected schedule exceeds ${p.STUDY_CAP_USD} study cap')
    for name in (*GATES, 'provider-preflight'):
        gatepath = p.HERE / f'checks/{name}.json'
        report = json.loads(gatepath.read_text()) if gatepath.exists() else {}
        if report.get('passed') is not True or report.get('freeze_sha256') != stamp:
            unresolved.append(name)
        if name == 'external-timestamp':
            freeze['external_timestamp'] = report
    freeze['dev_blockers'] = unresolved
    freeze['unresolved'] = unresolved + ['dev capability gate (not run)']
    freeze['status'] = 'BLOCKED_NOT_DEV_READY' if unresolved else 'READY_FOR_DEV_NOT_SCORED'
    p.write_json(path, freeze)
    return unresolved


def cached_vertex_tokens():
    """Reevaluate retained real counts only when the counted wire is identical."""
    path = p.HERE / 'checks/tokenizer.json'
    old = json.loads(path.read_text())
    prior_hash = p.sha(path)
    by_identity = {r['identity']: r for r in old['counts']}
    class RetainedCounter:
        def count(self, request):
            row = by_identity[request.identity]
            if row['request_sha256'] != p.digest([request.messages, request.tools]):
                raise PreflightError('counted Vertex wire changed; fresh countTokens required')
            return row['tokens']
    result = tokenize(RetainedCounter())
    result.update(reused_count_receipt_sha256=prior_hash, count_source='retained real Vertex countTokens; identical messages/tools',
                  count_api_calls=0)
    return result


def preflight(offline=False):
    p.export()
    stamp = p.freeze_execution()
    freeze = json.loads((p.HERE / 'freeze.json').read_text())
    selected = freeze['selected_schedule']
    budget = freeze['cost_ceilings'].get(selected, {})
    print(f"Selected {selected} all-in ceiling: ${budget.get('all_in_ceiling_usd', 'unavailable')}; study cap: ${p.STUDY_CAP_USD}", flush=True)
    if not budget.get('within_study_cap', False):
        fallback = freeze['cost_ceilings']['primary_1024']['all_in_ceiling_usd']
        print(f'Budget stop; primary-only primary_1024 fallback all-in ceiling: ${fallback}; no schedule switch or dispatch', flush=True)
    results = {}
    for name, fn in (('known-answer', p.known_answer), ('lean-replay', lean),
                     ('semantic-pairs', semantic_pairs), ('test-suite', test_suite),
                     ('external-timestamp', timestamp), ('tokenizer', cached_vertex_tokens if offline else lambda: tokenize(p.VertexBackend()))):
        results[name] = receipt(name, stamp, fn)
    refresh_status()
    if not all(r['passed'] for r in results.values()):
        return 2
    return 0 if budget.get('within_study_cap', False) else 3


class CommandCounter:
    """Operator-supplied provider-native counter: JSON wire stdin, integer stdout."""
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.sha256 = p.sha(self.path)
        self.native = None
        self.assets = {}
        if self.path == (p.HERE / 'native_counter.py').resolve():
            import importlib.util
            spec = importlib.util.spec_from_file_location('p1_native_counter', self.path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.native = module.NativeCounter()
            self.assets = {path: p.sha(path) for path in (p.HERE / 'tokenizers').glob('*.json')}

    def __call__(self, wire):
        if p.sha(self.path) != self.sha256:
            raise PreflightError('native counter changed after provider validation')
        if any(p.sha(path) != stamp for path, stamp in self.assets.items()):
            raise PreflightError('native tokenizer configuration changed after validation')
        if self.native is not None:
            return self.native(wire)
        proc = subprocess.run([str(self.path)], input=p.packed(wire), capture_output=True, text=True, timeout=120)
        if proc.returncode:
            raise PreflightError('native joint counter failed')
        n = json.loads(proc.stdout)
        if type(n) is not int or n < 0:
            raise PreflightError('native joint counter must return a nonnegative integer')
        return n


def runtime_counter():
    report = json.loads((p.HERE / 'checks/provider-preflight.json').read_text())
    spec = report.get('counter')
    if not spec:
        raise PreflightError('OpenRouter native joint counter missing')
    counter = CommandCounter(spec['path'])
    if counter.sha256 != spec['sha256']:
        raise PreflightError('OpenRouter counter hash changed')
    return counter


def preflight_openrouter(cap, counter_path=None, *, cached_only=False):
    """Resume infrastructure checks, reusing successful smoke calls durably."""
    import httpx
    freeze = json.loads((p.HERE / 'freeze.json').read_text())
    for path, expected in freeze['hashes'].items():
        if p.sha(p.ROOT / path) != expected:
            raise PreflightError(f'freeze hash changed: {path}; rerun preflight')
    def run():
        path = p.HERE / 'checks/provider-preflight.json'
        report = json.loads(path.read_text()) if path.exists() else {}
        report.update(passed=False)
        report.setdefault('judges', {})
        report.pop('error', None)
        counter = CommandCounter(counter_path or p.HERE / 'native_counter.py')
        counter_spec = {'path': str(counter.path), 'sha256': counter.sha256}
        current = report.get('freeze_sha256') == freeze['manifest_sha256'] and report.get('counter') == counter_spec
        todo = [j for j in ('replication', 'weak') if not (current and report['judges'].get(j, {}).get('passed'))]
        report['counter'] = counter_spec
        ledger = Ledger(p.HERE / 'runs/provider-preflight/costs.jsonl', min(cap, .50))
        with httpx.Client(transport=httpx.HTTPTransport(retries=0), timeout=120) as http:
            models = {}
            if todo and not cached_only:
                response = http.get('https://openrouter.ai/api/v1/models')
                response.raise_for_status()
                models = {x['id']: x for x in response.json()['data']}
            for judge in todo:
                old = report['judges'].get(judge, {})
                row = report['judges'][judge] = {**old, 'passed': False, 'requested_model': p.MODELS[judge]}
                row.pop('error', None)
                row.pop('endpoint_passed', None)
                row.pop('reused_smoke', None)
                try:
                    if cached_only:
                        if row.get('catalog', {}).get('id') != p.MODELS[judge] or not row.get('endpoints'):
                            raise PreflightError('cached endpoint evidence absent')
                        row['endpoint_metadata_source'] = 'retained listing; no API calls'
                    else:
                        if p.MODELS[judge] not in models:
                            raise PreflightError('planned model is not served; substitution forbidden')
                        row['catalog'] = models[p.MODELS[judge]]
                        endpoints = http.get(f'https://openrouter.ai/api/v1/models/{p.MODELS[judge]}/endpoints')
                        endpoints.raise_for_status()
                        row['endpoints'] = endpoints.json()
                    backend = OpenRouterBackend(counter=counter)
                    row['tokenizer'] = tokenize(backend, judge)
                    if not row['tokenizer']['passed']:
                        raise PreflightError('native tokenizer panel blocked; no smoke generation dispatched')
                    # Fixed tiny smoke prompt; conservative reservation, never a study verdict.
                    req = PaidRequest(f'provider-preflight/{judge}', judge,
                        [{'role': 'system', 'content': 'Reply with one word.'}, {'role': 'user', 'content': 'Hello'}], 3072, 1)
                    row['native_smoke_tokens'] = backend.count(req)
                    client = PaidClient(backend, ledger)
                    try:
                        # Recheck cached evidence with today's counter and full panel.
                        # A failed counter-agreement smoke may be rerun, but never
                        # replace a smoke whose usage already agrees.
                        reply = ledger.cached_reply(req)
                        if reply is None or backend.count(req) != reply.input_tokens:
                            if cached_only:
                                raise PreflightError('cached smoke missing or mismatched; generation forbidden')
                            reply = client.call(req)
                        else:
                            row['reused_smoke'] = True
                    finally:
                        client.close()
                    row.update(served_revision=reply.revision, served_provider=reply.response.get('provider'),
                               usage=reply.response.get('usage'), endpoint_passed=True)
                    if backend.count(req) != reply.input_tokens:
                        raise PreflightError('native counter disagrees with smoke prompt usage')
                    row['passed'] = row['tokenizer']['passed']
                except Exception as exc:
                    # Backend already redacts credentials; never dump environment.
                    row['error'] = f'{type(exc).__name__}: {exc}'
                p.write_json(p.HERE / 'checks/provider-preflight.json', {**report, 'freeze_sha256': freeze['manifest_sha256']})
                if row.get('endpoint_passed') is not True:
                    break  # unknown billing or endpoint failure must stop dispatch
        probe = json.loads((p.HERE / 'results/probe.json').read_text())
        report['vertex'] = {'status': probe['status'], 'served_revisions': sorted({c['served_revision'] for c in probe['calls']})}
        report['passed'] = probe['status'] == 'complete' and len(report['judges']) == 2 and all(r['passed'] for r in report['judges'].values())
        return report
    def preserve_failure():
        try:
            return run()
        except Exception as exc:
            path = p.HERE / 'checks/provider-preflight.json'
            report = json.loads(path.read_text()) if path.exists() else {}
            return {**report, 'passed': False, 'error': f'{type(exc).__name__}: {exc}'}
    result = receipt('provider-preflight', freeze['manifest_sha256'], preserve_failure)
    refresh_status()
    return 0 if result['passed'] else 2
