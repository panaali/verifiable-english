"""Copied from ve-codex-v4 tests/test_v4_account.py (backend reused unchanged)."""
import hashlib
import json
from unittest.mock import patch

import pytest

from ve_experiments.claude_cli import ClaudeCLI, Controls, EndpointError, oauth_token, command


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


def test_command_disables_tools_and_replaces_system_prompt(tmp_path):
    cmd = command('claude', Controls(), 'SYSTEM', tmp_path / 'mcp.json')
    assert cmd[cmd.index('--tools') + 1] == '' and cmd[cmd.index('--system-prompt') + 1] == 'SYSTEM'
    assert '--strict-mcp-config' in cmd and '--no-session-persistence' in cmd
