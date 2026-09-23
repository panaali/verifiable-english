"""Claude proposer backend for ``ve assist`` via the audited claude CLI endpoint.

The proposer model is a parameter: ``haiku`` (default, claude-haiku-4-5-20251001),
``sonnet`` (claude-sonnet-5) or ``opus`` (claude-opus-5-5). Every call is ledgered by
``ClaudeCLI`` (intent before the call, full stream after) in its own JSONL file; the
assist session ledger records the reply text, token counts, and the requested and
served model ids. ``max_calls`` caps spend for a ledger file.

The Claude account is a label resolved to ``~/.claude-<label>``. There is no personal
default: pass ``account=``, or set ``VE_ASSIST_CLAUDE_ACCOUNT``; otherwise the
default ``~/.claude`` configuration (or ``VE_CLAUDE_ACCOUNT_CONFIG_DIR``) is used.
"""
from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path

from .claude_cli import MODELS, ClaudeCLI, Controls, account_dir_for_label

PROPOSER_MODELS = {name: MODELS[name] for name in ("haiku", "sonnet", "opus")}
DEFAULT_MODEL = "haiku"
ACCOUNT_ENV = "VE_ASSIST_CLAUDE_ACCOUNT"


def resolve_account(account=None):
    """Explicit label, else $VE_ASSIST_CLAUDE_ACCOUNT, else None (default config directory)."""
    return account or os.environ.get(ACCOUNT_ENV) or None


class ClaudeProposer:
    def __init__(self, ledger, *, model=DEFAULT_MODEL, account=None, max_calls=None, output_tokens=2048,
                 timeout_s=180, working_directory="/private/tmp/ve-assist-claude-empty"):
        if model not in PROPOSER_MODELS:
            raise ValueError("Proposer model must be one of: " + ", ".join(PROPOSER_MODELS))
        self.model, self.model_id = model, PROPOSER_MODELS[model]
        controls = Controls(model=self.model_id, thinking_tokens=None, output_tokens=output_tokens,
                            effort=None, timeout_s=timeout_s, working_directory=working_directory,
                            context_date=datetime.now(timezone.utc).date().isoformat())
        account = resolve_account(account)
        config = account_dir_for_label(account) if account else None
        self.client = ClaudeCLI(Path(ledger), controls, max_calls, account_config_dir=config)

    def secret_needles(self):
        """What the canonical sanitizer must redact for this backend (its live token; in memory only)."""
        return self.client.secret_needles()

    def __call__(self, system, prompt, item_id):
        row = self.client.sample(item_id, system, prompt, 0)
        return {"text": row["text"], "input_tokens": row["input_tokens"],
                "output_tokens": row["output_tokens"], "model": row["served_model"],
                "account_label": row["account_label"], "call_key": row["key"],
                "prior_attempts": row.get("prior_attempts", [])}


HaikuProposer = ClaudeProposer  # backward-compatible name; the default model is Haiku 4.5
