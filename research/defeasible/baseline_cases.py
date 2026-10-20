"""DF-0.3's cases, without git or `ve`: P-1's questions and documents, the plan's expectations, and what counts as
answered. `research/defeasible/baseline.py` runs them; `tests/test_defeasible_baseline_evidence.py` checks the saved
evidence against them.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tests import ce4  # noqa: E402

COMMAND = "uv run python research/defeasible/baseline.py"
BINARIES = {"ve_service": "lean/.lake/build/bin/ve_service", "rust_jsonl": "rust/target/release/ve"}

# P-1's three sets (the plan's 4.2 "the three remaining constitution sets") and each one's question, as the plan
# writes it: `∀ c ∀ s. genuine_ambiguity(s) → clarification_required(c, s)`; `∀ c ∀ u. ¬
# system_prompt_deception_permitted(c, u)`; `∀ c ∀ s. explicit_instruction_against_exploits(c, s) →
# exploit_instruction_compliance_required(c, s)`. Variables are de Bruijn indices, 0 the innermost binder.
QUESTIONS = {
    "force-u0036-s05": ["forall", "claude_instance", ["forall", "situation", [
        "implies", ["unary", "genuine_ambiguity", ["var", 0]],
        ["binary", "clarification_required", ["var", 1], ["var", 0]]]]],
    "force-u0156-s03": ["forall", "claude_instance", ["forall", "user", [
        "not", ["binary", "system_prompt_deception_permitted", ["var", 1], ["var", 0]]]]],
    "force-u0263-s04-p2": ["forall", "claude_instance", ["forall", "situation", [
        "implies", ["binary", "explicit_instruction_against_exploits", ["var", 1], ["var", 0]],
        ["binary", "exploit_instruction_compliance_required", ["var", 1], ["var", 0]]]]],
}
# What the plan expects today (4.2): P-1 "0" probes answered unless an exception applies; P-2 SOME each.
EXPECTED = {"p1_answered": 0, "p2_verdict": "SOME"}

# P-1's controls (review df-03 F1): the same frame and sentence with the unit's content changed, or without
# `soft-norms@0`. Name -> (candidate id, or None for no content; whether the profile stays).
CONTROLS = {"strict": ("strict", True), "no-content": (None, True), "strict-no-soft": ("strict", False)}


def document_bytes(front, text):
    return b"---\n" + json.dumps(front).encode() + b"\n---\n" + text


def p1_document(set_id, candidate="default", soft=True):
    """The set's `default` candidate alone, in `CE4`'s frame: the set's sentence and one unit with that content.
    A control names another candidate (None: no content) or drops `soft-norms@0` from the profiles."""
    text, units, _ = ce4.source_text()
    [R] = [R for R in ce4.reading_sets() if R["id"] == set_id]
    [unit] = [u for u in units if u["id"] == R["unit"]]
    start, stop = unit["span"]
    sentence = text[start:stop]
    content = None
    if candidate is not None:
        [chosen] = [a for a in R["readings"] if a["id"] == candidate]
        content = chosen["content"]
    environment = ce4.environment()
    if not soft:
        environment["profiles"].remove("soft-norms@0")
    front = {"format": "ve-document@1", "environment": environment,
             "units": [{**unit, "span": [0, len(sentence)], "content": content}]}
    return document_bytes(front, sentence)


def control_name(control, set_id):
    return f"control-{control}-{set_id}.ve.md"


def follows(answer):
    """A probe is answered when today's answer says the conclusion follows (ALL); none of today's verdicts says
    "unless an exception applies"."""
    return answer["exit"] == 0 and answer["verdict"] == "ALL"
