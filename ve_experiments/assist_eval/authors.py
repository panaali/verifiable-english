"""Author (and auditor) model backends with per-call cost and a pre-call ceiling.

``ClaudeTextAuthor``: the audited claude CLI endpoint (ve_experiments.claude_cli,
account saeedi.danial, CLAUDE_CODE_NO_MODEL_FALLBACK=1). The endpoint is
single-turn with native tools disabled, so each author turn is one fresh CLI
call whose user message is the whole transcript so far, and tool calls travel
as a JSON block in the reply text (``parse_text_calls``). Costed at API list
price with the CLI's cache breakdown.

``GeminiAuthor``: Vertex gemini-3.1-pro-preview through ve_experiments.paid
(durable dollar reservations, fail-closed ledger), native function calling
with automatic calling disabled.

Both expose ``turn(history) -> Turn`` and ``ceiling(history) -> Decimal``.
Completed calls are cached by their ledgers, so re-running an interrupted
session replays earlier turns without new spend.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
import re

from .pricing import ceiling as price_ceiling, claude_cost, gemini_cost

CLAUDE_MODELS = {"opus": "claude-opus-5-5", "haiku": "claude-haiku-4-5-20251001"}
DEFAULT_ACCOUNT = "saeedi.danial"
CHARS_PER_TOKEN = 3  # conservative estimate for ceilings (JSON-heavy text)


class AuthorError(RuntimeError):
    """The model produced no usable reply (charged); the loop reports it and continues."""


class AuthorAbort(RuntimeError):
    """Infrastructure or accounting failure: stop the session without a verdict."""


@dataclass
class Turn:
    text: str
    calls: list  # [{"id", "name", "arguments"}]
    cost: Decimal
    usage: dict
    protocol_error: str | None = None
    raw: dict = field(default_factory=dict)


# ------------------------------------------------------------------ text protocol

_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.S)


def last_json_block(text):
    """The last fenced JSON object in a reply (or a bare trailing object)."""
    blocks = _FENCE.findall(text)
    candidates = blocks[::-1] or []
    if not blocks:
        start = text.find("{")
        if start >= 0:
            candidates = [text[start:text.rfind("}") + 1]]
    for body in candidates:
        try:
            value = json.loads(body)
        except ValueError:
            continue
        if isinstance(value, dict):
            return value, None
    return None, "no parseable JSON object block in the reply"


def parse_text_calls(text):
    """Extract {"calls": [{"tool", "arguments"}]} from a reply; (calls, error)."""
    value, error = last_json_block(text)
    if error:
        return [], error
    rows = value.get("calls")
    if type(rows) is not list or not rows:
        return [], 'the JSON block has no nonempty "calls" list'
    calls = []
    for i, row in enumerate(rows):
        if type(row) is not dict or not isinstance(row.get("tool"), str):
            return [], f'call {i} is not {{"tool": <name>, "arguments": {{...}}}}'
        args = row.get("arguments", {})
        calls.append({"id": f"c{i}", "name": row["tool"], "arguments": args})
    return calls, None


def render_transcript(opening, history):
    """One user message for the single-turn CLI: materials, then every turn in order."""
    parts = [opening]
    for i, row in enumerate(history, 1):
        parts.append(f"=== Turn {i}: your reply ===\n{row['text']}")
        parts.append(f"=== Turn {i}: harness response ===\n{row['feedback']}")
    parts.append("=== Continue: your next reply ===")
    return "\n\n".join(parts)


# ------------------------------------------------------------------ Claude CLI

class ClaudeTextAuthor:
    family = "anthropic"

    def __init__(self, which, ledger, *, account=DEFAULT_ACCOUNT, effort="medium", output_tokens=16000,
                 timeout_s=600, max_calls=None, working_directory=None, client=None):
        from ve_experiments.claude_cli import Controls, ClaudeCLI, account_dir_for_label
        self.model = CLAUDE_MODELS[which]
        self.output_tokens = output_tokens
        if client is None:
            wd = working_directory or f"/private/tmp/ve-assist-eval-{which}-empty"
            controls = Controls(model=self.model, thinking_tokens=None, output_tokens=output_tokens,
                                effort=effort if which == "opus" else None, timeout_s=timeout_s,
                                working_directory=wd,
                                context_date=datetime.now(timezone.utc).date().isoformat())
            client = ClaudeCLI(Path(ledger), controls, max_calls,
                               account_config_dir=account_dir_for_label(account) if account else None,
                               infrastructure_retries=True)
        self.client = client
        self.system = None
        self.opening = None

    def start(self, system, opening, tools=None):
        self.system, self.opening = system, opening

    def prompt(self, history):
        return render_transcript(self.opening, history)

    def ceiling(self, history):
        tokens = (len(self.system) + len(self.prompt(history))) // CHARS_PER_TOKEN + 2000
        return price_ceiling(self.model, tokens, self.output_tokens)

    def turn(self, history, call_id, parse_calls=True):
        from ve_experiments.claude_cli import EndpointError, InfrastructureError
        try:
            row = self.client.sample(call_id, self.system, self.prompt(history), 0)
        except InfrastructureError as exc:
            raise AuthorAbort(f"infrastructure: {exc}") from exc
        except EndpointError as exc:
            # The call may have been served (e.g. truncated at the output cap): charge the ceiling.
            return Turn("", [], self.ceiling(history), {}, protocol_error=f"endpoint rejected the reply: {exc}")
        cost = claude_cost(self.model, row["usage"])
        usage = {"input_tokens": row["input_tokens"], "output_tokens": row["output_tokens"],
                 "cache_read_input_tokens": row["usage"].get("cache_read_input_tokens", 0),
                 "cache_creation_input_tokens": row["usage"].get("cache_creation_input_tokens", 0)}
        if not parse_calls:
            return Turn(row["text"], [], cost, usage, raw={"key": row["key"]})
        calls, error = parse_text_calls(row["text"])
        return Turn(row["text"], calls, cost, usage, protocol_error=error, raw={"key": row["key"]})

    def single(self, call_id, system, prompt):
        """One standalone call (auditor use)."""
        row = self.client.sample(call_id, system, prompt, 0)
        return row["text"], claude_cost(self.model, row["usage"]), row


# ------------------------------------------------------------------ Gemini (Vertex)

def vertex_tools(tools):
    return [{"name": t["name"], "description": t["description"],
             "parameters_json_schema": t["input_schema"]} for t in tools]


class GeminiAuthor:
    family = "google"
    model = "gemini-3.1-pro-preview"

    def __init__(self, ledger, *, cap_usd, output_tokens=16000, max_input_tokens=190_000, client=None,
                 backend=None):
        from ve_experiments.paid import Ledger, PaidClient, VertexBackend
        self.output_tokens = output_tokens
        self.max_input_tokens = max_input_tokens
        self.backend = backend or VertexBackend()
        self.client = client or PaidClient(self.backend, Ledger(ledger, cap_usd), reuse_completed=True)
        self.tools = []

    def start(self, system, opening, tools=None):
        self.system, self.opening, self.tools = system, opening, vertex_tools(tools or [])
        self._counted = (None, None)

    def messages(self, history):
        messages = [{"role": "system", "content": self.system}, {"role": "user", "content": self.opening}]
        for row in history:
            messages.append(row["assistant"])
            messages.append(row["reply_message"])
        return messages

    def request(self, history, call_id, max_input):
        from ve_experiments.paid import PaidRequest
        return PaidRequest(identity=call_id, model="pro", messages=self.messages(history),
                           max_input_tokens=max_input, max_output_tokens=self.output_tokens,
                           tools=self.tools, metadata={"role": "assist-author"}, timeout_s=120)

    def _count(self, history, call_id):
        key = len(history)
        if getattr(self, "_counted", (None, None))[0] == key:
            return self._counted[1]
        probe = self.request(history, call_id, self.max_input_tokens)
        count = self.backend.count(probe)
        self._counted = (key, count)
        return count

    def ceiling(self, history):
        count = self._count(history, "ceiling-probe")
        return gemini_cost(self._margin(count), self.output_tokens)

    @staticmethod
    def _margin(count):
        return count + count // 50 + 256

    def turn(self, history, call_id, parse_calls=True):
        from ve_experiments.paid import PreflightError
        count = self._count(history, call_id)
        if self._margin(count) > self.max_input_tokens:
            raise AuthorAbort(f"context {count} tokens exceeds the {self.max_input_tokens} cap")
        request = self.request(history, call_id, self._margin(count))
        try:
            reply = self.client.call(request)
        except PreflightError as exc:
            raise AuthorAbort(f"paid ledger: {exc}") from exc
        cost = gemini_cost(reply.input_tokens, reply.billed_output_tokens)
        usage = {"input_tokens": reply.input_tokens, "output_tokens": reply.output_tokens,
                 "thinking_tokens": reply.thinking_tokens, "cached_tokens": reply.cached_tokens,
                 "finish_reason": reply.finish_reason}
        assistant = reply.assistant
        if not parse_calls:
            return Turn(reply.text, [], cost, usage, raw={"assistant": assistant})
        calls = [{"id": c["id"], "name": c["name"], "arguments": c["arguments"]} for c in reply.tool_calls]
        error = None
        if not calls:
            error = f"no function call in the reply (finish_reason {reply.finish_reason})"
        return Turn(reply.text, calls, cost, usage, protocol_error=error, raw={"assistant": assistant})

    @staticmethod
    def function_responses(calls, results):
        """The user turn carrying one function_response per function call."""
        parts = [{"function_response": {"name": c["name"], "id": c["id"],
                                        "response": {"result": r}}} for c, r in zip(calls, results)]
        return {"role": "user", "vertex_content": {"role": "user", "parts": parts}}

    def single(self, call_id, system, prompt, response_schema=None):
        from ve_experiments.paid import PaidRequest
        messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
        probe = PaidRequest(call_id, "pro", messages, self.max_input_tokens, self.output_tokens,
                            metadata={"role": "assist-auditor"}, timeout_s=120)
        count = self.backend.count(probe)
        request = PaidRequest(call_id, "pro", messages, self._margin(count), self.output_tokens,
                              metadata={"role": "assist-auditor"}, timeout_s=120)
        reply = self.client.call(request)
        return reply.text, gemini_cost(reply.input_tokens, reply.billed_output_tokens), {
            "input_tokens": reply.input_tokens, "output_tokens": reply.billed_output_tokens}


def make_author(name, *, ledger_dir, gemini_ledger=None, gemini_cap_usd=None, account=DEFAULT_ACCOUNT):
    if name in CLAUDE_MODELS:
        return ClaudeTextAuthor(name, Path(ledger_dir) / "author-calls.jsonl", account=account)
    if name == "gemini":
        if gemini_ledger is None or gemini_cap_usd is None:
            raise ValueError("gemini needs --gemini-ledger and --gemini-cap-usd")
        return GeminiAuthor(gemini_ledger, cap_usd=gemini_cap_usd)
    raise ValueError(f"unknown author {name!r}: use opus, haiku or gemini")
