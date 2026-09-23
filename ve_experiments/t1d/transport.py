"""T1d transport: T1c's audited Claude Code subscription endpoint (imported unchanged), with the T1d
changes the preregistration requires.

* A response stopped by the output-token cap is a COMPLETED SAMPLE, not an endpoint error: it is
  recorded with `truncated: true`, its stop reason and its (possibly partial) text, and scored by the
  same parser (almost always INVALID). T1c stopped the run on truncation instead.
* A request whose output cap the API or CLI rejects outright (before any generation) is classified
  `CapRejected`; the harness then moves down the preregistered cap ladder (run.py).
* Every other check of T1c's `parse_stream` and `ClaudeCLI` is kept: pinned CLI binary and version,
  isolated environment, empty tool/MCP inventory, served-model identity, single turn, ledger intent
  before every call, session-limit pause, bounded infrastructure retries.
"""
from __future__ import annotations

from dataclasses import asdict
import fcntl
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import tempfile
import time
import hashlib

from ve_experiments.t1c import transport as T
from ve_experiments.t1c.transport import (Controls, EndpointError, InfrastructureError, InfrastructurePaused,  # noqa: F401
                                          MODELS, Refusal, RETRY_BACKOFF, SessionLimit, check_context_date,
                                          check_session_limit, command, digest, empty_working_directory,
                                          infrastructure_failure, isolated_env, now, oauth_token)

_TRUNCATION = re.compile(r"exceeded the \d+ output token maximum|max_output_tokens|stop_reason\W+max_tokens", re.I)
_CAP_REJECTED = re.compile(r"(max_tokens|max_output_tokens|CLAUDE_CODE_MAX_OUTPUT_TOKENS)[^\n]{0,200}"
                           r"(greater than|exceeds|must be|invalid|too large|maximum allowed)", re.I)


class CapRejected(EndpointError):
    """The requested output cap was refused before generation; no sample exists."""


def _records(raw):
    out = []
    for line in raw.splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def truncation_signal(raw):
    """True if the stream shows the response was cut by the output-token cap."""
    records = _records(raw)
    stops = {r.get('stop_reason') for r in records if r.get('type') == 'result'}
    stops |= {r.get('message', {}).get('stop_reason') for r in records if r.get('type') == 'assistant'}
    if 'max_tokens' in stops:
        return True
    texts = [str(r.get('result', '')) for r in records if r.get('type') == 'result']
    texts += [str(b.get('text', '')) for r in records if r.get('type') == 'assistant'
              for b in r.get('message', {}).get('content', []) if isinstance(b, dict)]
    return any(_TRUNCATION.search(t) for t in texts)


def cap_rejected(raw, stderr=''):
    records = _records(raw)
    texts = [stderr] + [str(r.get('result', '')) for r in records if r.get('type') == 'result' and r.get('is_error')]
    texts += [str(b.get('text', '')) for r in records if r.get('type') == 'assistant'
              and r.get('message', {}).get('model') == '<synthetic>' for b in r.get('message', {}).get('content', [])]
    return any(_CAP_REJECTED.search(t) for t in texts) and not truncation_signal(raw)


def parse_stream(raw, expected_model):
    """T1c's parse_stream, except that a max-tokens stop is returned as a truncated sample."""
    check_session_limit(raw, expected_model)
    if not truncation_signal(raw):
        return {**T.parse_stream(raw, expected_model), 'truncated': False}
    records = [r for r in _records(raw)]
    results = [r for r in records if r.get('type') == 'result']
    assistants = [r['message'] for r in records if r.get('type') == 'assistant']
    served = {m.get('model') for m in assistants} | {k for r in results for k in r.get('modelUsage', {})}
    if served - {expected_model, '<synthetic>', None}:
        raise EndpointError(f"Served model mismatch: {sorted(map(str, served))}")
    if expected_model not in served:
        raise InfrastructureError('truncation reported without a served model')
    if any(b.get('type') not in ('text', 'thinking', 'redacted_thinking')
           for m in assistants for b in m.get('content', [])):
        raise EndpointError('Non-text assistant action')
    result = results[-1] if results else {}
    usage = result.get('usage', {})
    keys = ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens')
    text = ''.join(b.get('text', '') for m in assistants if m.get('model') == expected_model
                   for b in m.get('content', []) if b.get('type') == 'text')
    return {'init': next((r for r in records if r.get('subtype') == 'init'), {}), 'usage': usage,
            'model_usage': result.get('modelUsage'), 'served_model': expected_model,
            'input_tokens': sum(usage.get(k, 0) or 0 for k in keys), 'output_tokens': usage.get('output_tokens'),
            'thinking_tokens_reported': usage.get('output_tokens_details', {}).get('thinking_tokens'),
            'stop_reason': result.get('stop_reason') or 'max_tokens', 'text': text, 'truncated': True}


class ClaudeCLI(T.ClaudeCLI):
    """T1c's ClaudeCLI with the T1d stream parser (truncation is a sample; cap rejection is classified)."""

    def _sample_once(self, item_id, system, prompt, sample_index=0, *, content_tokens=None, retry_number=0):
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger.open('a+', encoding='utf-8') as log:
            fcntl.flock(log, fcntl.LOCK_EX)
            log.seek(0)
            try:
                history = [json.loads(line) for line in log if line.strip()]
            except json.JSONDecodeError as exc:
                raise EndpointError('Damaged ledger; preserve it and repair explicitly') from exc
            if any(r.get('account_label') != self.account_label for r in history):
                raise EndpointError('Account mismatch or unattributed legacy ledger; use a separately named ledger')
            executable = shutil.which('claude')
            if not executable:
                raise EndpointError('claude not found')
            binary_hash = hashlib.sha256(Path(executable).read_bytes()).hexdigest()
            control = {**asdict(self.controls), 'binary_sha256': binary_hash, 'backend_revision': 't1d-1',
                       'host_system': platform.system(), 'host_release': platform.release(),
                       'shell': '/bin/sh', 'locale': 'en_US.UTF-8', 'timezone': 'UTC'}
            group = digest([self.account_label, control, system, prompt, content_tokens])
            key = digest([group, item_id, sample_index])
            matching = [r for r in history if r.get('key') == key and r['status'] != 'retry_scheduled']
            if matching:
                if matching[-1]['status'] == 'ok':
                    return matching[-1]
                last = matching[-1]
                retryable = last['status'] == 'infrastructure_error' or (
                    last['status'] == 'error' and infrastructure_failure(
                        last.get('raw_stream', ''), self.controls.model, last.get('error', '')))
                if not (self.infrastructure_retries and retryable):
                    raise EndpointError('Sample previously started or failed; explicit new sample id required')
            if self.max_calls is not None and sum(r['status'] == 'started' for r in history) >= self.max_calls:
                raise EndpointError('Call budget exhausted')
            version = subprocess.check_output([executable, '--version'], text=True).strip()
            if version != self.controls.cli_version:
                raise EndpointError(f'CLI version drift: {version}')
            prior = [r for r in history if r['status'] == 'started']
            if prior and prior[0]['controls'] != control:
                raise EndpointError('Controls/binary drift; start a separately named ledger')
            check_context_date(self.controls)
            token = oauth_token(self.account_config)
            base = {'key': key, 'item_id': item_id, 'sample_index': sample_index, 'prompt_group': group,
                    'system': system, 'prompt': prompt, 'controls': control, 'content_tokens': content_tokens,
                    'account_label': self.account_label}

            def append(row):
                log.write(json.dumps(row, ensure_ascii=False) + '\n')
                log.flush()
                os.fsync(log.fileno())
            if matching or retry_number:
                delay = RETRY_BACKOFF[retry_number - 1] if retry_number else RETRY_BACKOFF[0]
                append({**base, 'status': 'retry_scheduled', 'timestamp': now(), 'retry_number': retry_number,
                        'backoff_s': delay, 'resumed': retry_number == 0,
                        'previous_status': matching[-1]['status'] if matching else 'prior_infrastructure_error',
                        'classification': 'INFRASTRUCTURE', 'counts_as_sample': False})
                time.sleep(delay)
                check_context_date(self.controls)
            append({**base, 'status': 'started', 'timestamp': now(), 'retry_number': retry_number})
            start = time.monotonic()
            raw, parsed = '', {}
            try:
                with empty_working_directory(self.controls.working_directory) as cwd, \
                        tempfile.TemporaryDirectory(prefix='ve-claude-t1d-') as tmp:
                    root = Path(tmp)
                    config, home = (root / n for n in ('config', 'home'))
                    for p in (config, home):
                        p.mkdir(mode=0o700)
                    mcp = root / 'empty-mcp.json'
                    mcp.write_text('{"mcpServers":{}}')
                    env = isolated_env(os.environ, config, home, token, self.controls)
                    proc = subprocess.run(command(executable, self.controls, system, mcp), input=prompt, text=True,
                                          capture_output=True, cwd=cwd, env=env, timeout=self.controls.timeout_s)
                    raw = proc.stdout
                    check_session_limit(raw, self.controls.model)
                    if cap_rejected(raw, proc.stderr):
                        raise CapRejected('Output cap rejected before generation: ' + str(self.controls.output_tokens))
                    if not truncation_signal(raw):
                        reason = infrastructure_failure(raw, self.controls.model, proc.stderr if proc.returncode else '')
                        if reason:
                            raise InfrastructureError(reason)
                        if proc.returncode:
                            raise EndpointError(f'CLI exit {proc.returncode}')
                    parsed = parse_stream(raw, self.controls.model)
                    check_context_date(self.controls)
                row = {**base, **parsed, 'status': 'ok', 'timestamp': now(), 'elapsed_s': time.monotonic() - start,
                       'raw_stream': raw}
            except Exception as exc:
                raw = raw.replace(token, '[REDACTED]')
                if isinstance(exc, (ConnectionError, subprocess.TimeoutExpired)):
                    if isinstance(exc, subprocess.TimeoutExpired) and exc.stdout:
                        raw = exc.stdout.decode(errors='replace') if isinstance(exc.stdout, bytes) else exc.stdout
                        raw = raw.replace(token, '[REDACTED]')
                    if infrastructure_failure(raw, self.controls.model, str(exc)) or isinstance(exc, ConnectionError):
                        exc = InfrastructureError('connection error or empty timed-out stream')
                status = ('infrastructure_error' if isinstance(exc, InfrastructureError) else 'refusal'
                          if isinstance(exc, Refusal) else 'cap_rejected' if isinstance(exc, CapRejected) else 'error')
                append({**base, **parsed, 'status': status,
                        'classification': 'INFRASTRUCTURE' if isinstance(exc, InfrastructureError) else 'ENDPOINT',
                        'counts_as_sample': False, 'retry_number': retry_number, 'timestamp': now(),
                        'error': str(exc).replace(token, '[REDACTED]'), 'raw_stream': raw,
                        'elapsed_s': time.monotonic() - start})
                raise exc
            row = json.loads(json.dumps(row).replace(token, '[REDACTED]'))
            append(row)
            return row
