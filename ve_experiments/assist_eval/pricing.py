"""List prices used for budget matching (USD per million tokens).

Claude calls go through the subscription CLI but are costed at Anthropic API
list price (orchestrator decision c), using the CLI's usage breakdown:
uncached input, 5-minute cache writes (1.25x input) and cache reads (0.1x
input for Haiku 4.5; $0.20 for Opus 5.5). Thinking is billed as output.
Gemini 3.1 Pro uses ve_experiments.paid's registered table ($2 in / $12 out,
thoughts billed as output, cached input charged at the full input rate) and
calls are capped below the 200k-token long-context tier.
"""
from __future__ import annotations

from decimal import Decimal

PRICES = {
    "claude-opus-5-5": {"input": "4", "output": "20", "cache_write": "5", "cache_read": "0.20"},
    "claude-haiku-4-5-20251001": {"input": "1", "output": "5", "cache_write": "1.25", "cache_read": "0.10"},
    "gemini-3.1-pro-preview": {"input": "2", "output": "12", "cache_write": "2", "cache_read": "2"},
}
M = Decimal(1_000_000)


def claude_cost(model, usage):
    """Cost of one claude CLI call from its usage block (input split by cache state)."""
    p = {k: Decimal(v) for k, v in PRICES[model].items()}
    return (Decimal(usage.get("input_tokens", 0)) * p["input"]
            + Decimal(usage.get("cache_creation_input_tokens", 0)) * p["cache_write"]
            + Decimal(usage.get("cache_read_input_tokens", 0)) * p["cache_read"]
            + Decimal(usage.get("output_tokens", 0)) * p["output"]) / M


def ceiling(model, input_tokens, output_tokens):
    """Worst-case cost of a call: all input uncached, full output allowance."""
    p = PRICES[model]
    return (Decimal(input_tokens) * Decimal(p["input"]) + Decimal(output_tokens) * Decimal(p["output"])) / M


def gemini_cost(input_tokens, billed_output_tokens):
    from ve_experiments.paid import cost
    return cost("pro", input_tokens, billed_output_tokens)
