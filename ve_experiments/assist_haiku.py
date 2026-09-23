"""Haiku 4.5 proposer backend for ``ve assist`` via the audited claude CLI endpoint.

Every call is ledgered by ``ClaudeCLI`` (intent before the call, full stream
after) in its own JSONL file; the assist session ledger records the reply text
and token counts. ``max_calls`` caps spend for a ledger file.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .claude_cli import MODELS, ClaudeCLI, Controls, account_dir_for_label

DEFAULT_ACCOUNT = "saeedi.danial"


class HaikuProposer:
    def __init__(self, ledger, *, account=DEFAULT_ACCOUNT, max_calls=None, output_tokens=2048,
                 timeout_s=180, working_directory="/private/tmp/ve-assist-claude-empty"):
        controls = Controls(model=MODELS["haiku"], thinking_tokens=None, output_tokens=output_tokens,
                            effort=None, timeout_s=timeout_s, working_directory=working_directory,
                            context_date=datetime.now(timezone.utc).date().isoformat())
        config = account_dir_for_label(account) if account else None
        self.client = ClaudeCLI(Path(ledger), controls, max_calls, account_config_dir=config)

    def __call__(self, system, prompt, item_id):
        row = self.client.sample(item_id, system, prompt, 0)
        return {"text": row["text"], "input_tokens": row["input_tokens"],
                "output_tokens": row["output_tokens"], "model": row["served_model"],
                "account_label": row["account_label"], "call_key": row["key"]}
