"""relb-privacy-code-2/-3: account locations come from settings with neutral defaults, never from private names.

code-2: ve_experiments/claude_cli.py finds the Claude CLI's credentials file by the CLI's standard name or by
VE_CLAUDE_CREDENTIALS_FILE. code-3: the experiment runners take the accounts directory from
VE_ACCOUNTS_DIR (default ~/accounts) for the picker check and the Codex home. code-1 (the pre-commit hook's
private-directory rule) is tested in tests/test_precommit_hook.py.
No fixture names a private value, so this file holds no hit for tests/test_public_tree_privacy.py.
"""
import importlib.util
import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# (file, function that checks the picker's answer, what it does once the answer is accepted)
CLAUDE_RUNNERS = [
    ("docs/act-phrases/ap-7/runner.py", lambda m: m.call("k", "body"), "reads"),
    ("docs/judgment-terms/jt-e1r/runner.py", lambda m: m.account(), "reads"),
    ("docs/presupposition/ps-e1/e1_runner.py", lambda m: m.pick_account(), "reads"),
    ("docs/judgment-terms/jt-e3/runner.py", lambda m: m.picked_claude(dict(os.environ)), "returns"),
]
CODEX_RUNNERS = ["experiments/authoring-gates/risk-wording-probe/run.py",
                 "experiments/authoring-gates/risk-wording-probe-2/run.py"]


def load(rel, tag, monkeypatch):
    monkeypatch.syspath_prepend(str((ROOT / rel).parent))  # runners import their sibling modules
    spec = importlib.util.spec_from_file_location(f"relb_privacy_code_{tag}", ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fake_picker(module, monkeypatch, answer):
    def run(args, **kwargs):
        return subprocess.CompletedProcess(args, 0, stdout=answer + "\n", stderr="")
    monkeypatch.setattr(module.subprocess, "run", run)


@pytest.mark.parametrize("rel, check, accepted", CLAUDE_RUNNERS, ids=[r[0].split("/")[-2] for r in CLAUDE_RUNNERS])
def test_runner_accepts_a_picked_account_under_ve_accounts_dir(tmp_path, monkeypatch, rel, check, accepted):
    accounts = tmp_path / "accts"
    cfg = accounts / ("claude" + "-tester")
    cfg.mkdir(parents=True)
    # an API-key account: a runner that gets past the directory check stops at its own OAuth check, before any call
    (cfg / ".claude.json").write_text(json.dumps({"primaryApiKey": "placeholder"}))
    monkeypatch.setenv("VE_ACCOUNTS_DIR", str(accounts))
    module = load(rel, "in", monkeypatch)
    fake_picker(module, monkeypatch, str(cfg))
    if accepted == "returns":
        assert check(module) == str(cfg)
    else:
        with pytest.raises(RuntimeError, match="not an OAuth subscription"):
            check(module)


@pytest.mark.parametrize("rel, check, accepted", CLAUDE_RUNNERS, ids=[r[0].split("/")[-2] for r in CLAUDE_RUNNERS])
def test_runner_refuses_a_picked_account_outside_ve_accounts_dir(tmp_path, monkeypatch, rel, check, accepted):
    monkeypatch.setenv("VE_ACCOUNTS_DIR", str(tmp_path / "accts"))
    module = load(rel, "out", monkeypatch)
    fake_picker(module, monkeypatch, str(tmp_path / "elsewhere" / ("claude" + "-tester")))
    with pytest.raises(RuntimeError, match="picker"):
        check(module)


@pytest.mark.parametrize("rel", CODEX_RUNNERS, ids=["probe-1", "probe-2"])
def test_probe_codex_home_is_under_ve_accounts_dir(tmp_path, monkeypatch, rel):
    monkeypatch.setenv("VE_ACCOUNTS_DIR", str(tmp_path))
    assert load(rel, "codex", monkeypatch).CODEX_HOME == str(tmp_path / "codex")


@pytest.mark.parametrize("rel", [r[0] for r in CLAUDE_RUNNERS] + CODEX_RUNNERS)
def test_a_home_relative_setting_is_expanded(monkeypatch, rel):
    monkeypatch.setenv("VE_ACCOUNTS_DIR", "~/accts")
    assert load(rel, "tilde", monkeypatch).ACCOUNTS_DIR == os.path.expanduser("~/accts")


@pytest.mark.parametrize("rel", [r[0] for r in CLAUDE_RUNNERS] + CODEX_RUNNERS)
def test_default_accounts_dir_is_neutral(monkeypatch, rel):
    monkeypatch.delenv("VE_ACCOUNTS_DIR", raising=False)
    assert load(rel, "default", monkeypatch).ACCOUNTS_DIR == os.path.expanduser("~/accounts")


def test_credentials_file_name_comes_from_the_setting(tmp_path, monkeypatch):
    from ve_experiments import claude_cli as cc
    monkeypatch.delenv("CLAUDE_CODE_OAUTH_TOKEN", raising=False)
    (tmp_path / "login.json").write_text(json.dumps({"claudeAiOauth": {"accessToken": "fake-access"}}))
    monkeypatch.setenv("VE_CLAUDE_CREDENTIALS_FILE", "login.json")
    assert cc.oauth_token(tmp_path) == "fake-access"


def test_credentials_file_default_is_the_cli_documented_name(tmp_path, monkeypatch):
    from ve_experiments import claude_cli as cc
    monkeypatch.delenv("CLAUDE_CODE_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("VE_CLAUDE_CREDENTIALS_FILE", raising=False)
    (tmp_path / ".credentials.json").write_text(
        json.dumps({"claudeAiOauth": {"accessToken": "fake-default"}}))
    assert cc.oauth_token(tmp_path) == "fake-default"
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "home")
    assert cc.credentials_file() == tmp_path / "home" / ".claude" / ".credentials.json"
