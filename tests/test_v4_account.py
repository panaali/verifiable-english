import hashlib
import json
from pathlib import Path
from unittest.mock import patch
import pytest
from ve_experiments.claude_cli import ClaudeCLI, EndpointError, account_config, oauth_token


def test_explicit_account_ignores_ambient_token_and_selects_keychain(tmp_path, monkeypatch):
    monkeypatch.setenv('CLAUDE_CODE_OAUTH_TOKEN', 'wrong-account')
    config = tmp_path / '.claude-danielsaeedi37'
    result = type('Result', (), {'returncode': 0, 'stdout': json.dumps({'claudeAiOauth': {'accessToken': 'right-account'}})})()
    with patch('ve_experiments.claude_cli.subprocess.run', return_value=result) as call:
        assert oauth_token(config) == 'right-account'
    assert call.call_args.args[0] == ['security', 'find-generic-password', '-s',
        'Claude Code-credentials-' + hashlib.sha256(str(config).encode()).hexdigest()[:8], '-w']


def test_env_account_and_mixing_rejected_before_spending(tmp_path, monkeypatch):
    monkeypatch.setenv('VE_CLAUDE_ACCOUNT_CONFIG_DIR', str(tmp_path / '.claude-danielsaeedi37'))
    ledger = tmp_path / 'ledger.jsonl'
    ledger.write_text(json.dumps({'account_label': 'lead-main', 'status': 'started'}) + '\n')
    client = ClaudeCLI(ledger)
    assert client.account_label == 'danielsaeedi37'
    with patch('ve_experiments.claude_cli.oauth_token', side_effect=AssertionError('must not read auth')):
        with pytest.raises(EndpointError, match='Account mismatch'):
            client.sample('other-item', 's', 'p')


def test_auth_file_copies_only_access_token(tmp_path):
    (tmp_path / '.credentials.json').write_text(json.dumps({'claudeAiOauth': {'accessToken': 'access', 'refreshToken': 'secret'}, 'settings': {'bad': True}}))
    assert oauth_token(tmp_path) == 'access'


def test_amended_runner_accepts_over_old_cap_and_halts_on_integrity(tmp_path):
    import importlib.util
    import sys
    here = Path(__file__).resolve().parents[1] / 'experiments/V4-D-pilot'
    sys.path.insert(0, str(here))
    try:
        spec = importlib.util.spec_from_file_location('d_rerun', here / 'rerun.py')
        rerun = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rerun)
    finally:
        sys.path.remove(str(here))
    runner = object.__new__(rerun.Runner)
    runner.spent, runner.date = 210, '2026-09-22'
    runner.config, runner.account = tmp_path / '.claude-danielsaeedi37', 'danielsaeedi37'
    row = {'status':'ok','thinking_tokens_reported':1188}
    def response(client, *args):
        assert client.controls.thinking_tokens is None
        client.ledger.parent.mkdir(parents=True, exist_ok=True)
        client.ledger.write_text(json.dumps({'status':'started'})+'\n'+json.dumps(row)+'\n')
        return row
    with patch.object(rerun,'OUT',tmp_path), patch.object(rerun,'verify'), patch.object(ClaudeCLI,'sample',autospec=True,side_effect=response):
        assert runner.sample('item','alone','haiku','s','p') == row
        assert not (tmp_path/'STOP.json').exists()
    with patch.object(rerun,'OUT',tmp_path), patch.object(rerun,'verify'), patch.object(ClaudeCLI,'sample',side_effect=EndpointError('Served model mismatch')):
        with pytest.raises(EndpointError,match='permanently stopped'):
            runner.sample('item2','alone','haiku','s','p')
        assert (tmp_path/'STOP.json').exists()
