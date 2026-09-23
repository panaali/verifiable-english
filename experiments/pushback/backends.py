"""Chat endpoints for the pushback study, built on existing audited backends.

Gemini: ve_experiments.paid (Vertex ADC, durable dollar ledger, served-revision
check, infrastructure retries). Claude: ve_experiments.claude_cli (isolated
subscription CLI, explicit account, ledger, served-model check, retries).

Channel semantics (recorded per provider, as the review asked):
  Gemini  system = Vertex system_instruction; turns are native user/model
          contents; model turns keep thought signatures.
  Claude  system = CLI --system-prompt (replaces Claude Code's prompt, no tools);
          the CLI is single-turn, so earlier turns are rendered as a transcript
          inside one user message. This is an approximation of multi-turn chat.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from ve_experiments import paid
from ve_experiments.paid import Ledger, PaidClient, PaidRequest, VertexBackend

# Runtime registration keeps the frozen P1 module untouched. Gemini 3 Flash is
# only the Jagged-Judges replication observer (their observer was GPT-5).
paid.MODELS.setdefault("flash", "gemini-3-flash-preview")
paid.RATES.setdefault("flash", ("0.5", "3", "1"))


class StudyVertexBackend(VertexBackend):
    """P1's Vertex wire plus per-request thinking/temperature overrides.

    metadata["thinking"]: "LOW" (P1 default), "DEFAULT" (omit thinking_config,
    i.e. provider default reasoning, as in Jagged Judges) or "MINIMAL".
    metadata["temperature"]: float, default 0.
    """

    def wire(self, request):
        from google.genai import types
        contents, cfg = super().wire(request)
        thinking = request.metadata.get("thinking", "LOW")
        update = {"temperature": request.metadata.get("temperature", 0)}
        if thinking == "DEFAULT":
            update["thinking_config"] = None
        elif thinking != "LOW":
            update["thinking_config"] = types.ThinkingConfig(thinking_level=thinking)
        if request.metadata.get("no_seed"):
            update["seed"] = None
        return contents, cfg.model_copy(update=update)


@dataclass
class Reply:
    text: str
    assistant: dict
    meta: dict


class GeminiChat:
    def __init__(self, client: PaidClient, model="pro", *, thinking="LOW", temperature=0.0,
                 max_output=2048, max_input=16000):
        self.client, self.model = client, model
        self.thinking, self.temperature = thinking, temperature
        self.max_output, self.max_input = max_output, max_input
        self.label = f"vertex:{paid.MODELS[model]}"

    def chat(self, identity, system, messages, metadata=None):
        wire = ([{"role": "system", "content": system}] if system else []) + list(messages)
        req = PaidRequest(identity, self.model, wire, self.max_input, self.max_output,
                          metadata={"thinking": self.thinking, "temperature": self.temperature,
                                    **(metadata or {})})
        reply = self.client.call(req)
        return Reply(reply.text, reply.assistant,
                     {"input_tokens": reply.input_tokens, "output_tokens": reply.output_tokens,
                      "thinking_tokens": reply.thinking_tokens, "revision": reply.revision,
                      "finish_reason": reply.finish_reason})


def transcript_prompt(messages):
    """Single-turn rendering of a conversation for the Claude CLI."""
    if len(messages) == 1:
        return messages[0]["content"]
    lines = ["The conversation so far is reproduced below. Your earlier replies are marked ASSISTANT (YOU).", ""]
    for m in messages[:-1]:
        who = "USER" if m["role"] == "user" else "ASSISTANT (YOU)"
        lines += [f"=== {who} ===", m["content"], ""]
    lines += ["=== USER (latest message; reply to this) ===", messages[-1]["content"]]
    return "\n".join(lines)


class ClaudeChat:
    def __init__(self, ledger: Path, model="opus", *, account_config_dir=None, thinking_tokens=1024,
                 output_tokens=6000, effort="low", context_date=None,
                 working_directory="/private/tmp/ve-claude-pushback-empty"):
        from datetime import datetime, timezone
        from ve_experiments.claude_cli import ClaudeCLI, Controls, MODELS
        controls = Controls(model=MODELS[model], thinking_tokens=thinking_tokens,
                            output_tokens=output_tokens, effort=effort,
                            working_directory=working_directory,
                            context_date=context_date or datetime.now(timezone.utc).date().isoformat())
        self.cli = ClaudeCLI(ledger, controls, account_config_dir=account_config_dir,
                             infrastructure_retries=True)
        self.label = f"claude-cli:{MODELS[model]}"

    def chat(self, identity, system, messages, metadata=None):
        prompt = transcript_prompt([{"role": m["role"], "content": m.get("content", "")} for m in messages])
        row = self.cli.sample(identity, system or "You are a helpful assistant.", prompt, 0)
        return Reply(row["text"], {"role": "assistant", "content": row["text"]},
                     {"input_tokens": row.get("input_tokens"), "output_tokens": row.get("output_tokens"),
                      "served_model": row.get("served_model")})


def gemini_client(ledger_path, cap_usd, backend=None):
    return PaidClient(backend or StudyVertexBackend(), Ledger(ledger_path, cap_usd), reuse_completed=True)


def spent(ledger_path):
    path = Path(ledger_path)
    if not path.exists():
        return 0.0
    ledger = Ledger(path, 10**6)
    with ledger.locked() as (_, rows):
        pending, committed, *_ = ledger.state(rows)
    return float(committed + sum(pending.values()))


def assistant_text(message):
    if "content" in message:
        return message["content"]
    parts = message.get("vertex_content", {}).get("parts", [])
    return "".join(p.get("text", "") for p in parts if not p.get("thought"))


def plain(messages):
    """Provider-neutral copy of a conversation (for persuaders/observers/logs)."""
    return [{"role": m["role"], "content": m["content"] if "content" in m else assistant_text(m)}
            for m in messages]


__all__ = ["GeminiChat", "ClaudeChat", "StudyVertexBackend", "gemini_client", "spent", "plain",
           "transcript_prompt", "assistant_text", "Reply", "replace"]
