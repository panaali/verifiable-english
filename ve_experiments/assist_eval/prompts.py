"""Author and auditor prompts. Hashed into PREREG-ASSIST (tuning may change them on DEV only).

The same task text and item materials go to every arm and author; arms differ
only in the action interface (tools vs whole-document resubmission) and the
tool list (proposer or not). The Claude text protocol is an interface detail
of the claude CLI backend, whose controlled endpoint disables native tools.
"""
from __future__ import annotations

import json

from ve.assist.proposer import GRAMMAR

PROMPT_VERSION = "ve-assist-eval-prompts@3"

TASK = """You are formalising an English argument into Verifiable English (VE), a small
first-order logic with a checker. You receive the argument split into
numbered SENTENCES, each with a role:
- given: the text states it as a premise (declared rules, records, facts);
- claimed: the argument asserts it as a conclusion; it must be derived;
- context: needs nothing.
TARGET sentences are the argument's final conclusion(s).

What a finished formalisation contains:
1. The frozen TARGET: the formal statement of each target sentence, written
   first and never changed afterwards.
2. NODES. Each node is ONE VE statement anchored to the sentence id(s) it
   formalises. A node without parents is an assumption; an assumption must be
   anchored to a GIVEN sentence that states it. A node with parents is a step:
   it must follow logically from its parents, and the checker certifies this
   (or returns a countermodel: a situation where every parent is true and the
   step is false).
3. COVERAGE: every claimed sentence is DERIVED: a certified step anchored to
   it states its conclusion. A claimed sentence may never be waived. Every
   given sentence is covered by a node anchored to it, or WAIVED with a reason
   when no statement can or need state it: a sentence that only lists which
   rules are declared, a sentence saying which checks remain unassumed, or a
   fact or rule the argument never uses. The checker's status lists any waiver
   as a failure ("asserting sentence(s) waived"); in this task that failure
   ALONE is acceptable when every waived sentence is given, and each waiver is
   audited.
4. A certified chain from anchored assumptions to a step that states each
   frozen target exactly.

Fidelity is your responsibility and is audited independently, sentence by
sentence: each node must say what its sentence says, no more and no less.
Give every claimed sentence its OWN step node stating exactly what that
sentence concludes (with that sentence's reasons as parents); do not skip
intermediate conclusions or anchor one node to several sentences it does not
fully state. Where a word has several
senses (several predicates), the given sentences name the sense; a claimed
sentence may leave it open. Then choose the sense that the sentence's own
stated reasons (and the given records they rely on) actually establish. Do
not switch to another sense just because a later step needs it; a step that
needs a different sense of the same word is a gap. Never add a premise that
no given sentence states: an unanchored assumption that a certified step
depends on fails the item. The argument itself MAY be flawed. If a claimed
step does not follow when faithfully formalised, do not force it: leave it
unproved and finish with verdict "gap", naming the step node(s).
"""

GUIDE = GRAMMAR.replace("Use ONLY the sorts, predicates and constants listed below. Where a word has\n"
                        "several senses, pick the predicate whose gloss matches this use.",
                        "Use ONLY the sorts, predicates and constants listed in the materials.") + """
Constants are written with @ (e.g. @unit5). A statement ends with a period.
A step's parents are node names; a rule node (an 'if ... then' assumption)
must be listed as a parent of any step that uses it.
"""

TOOLS_ARM = """You act through the tools listed below. Suggested order: freeze_target
for every target, then add assumption nodes for the given sentences you need,
then add step nodes for the claimed sentences with their parents and
check_step each one; waive given sentences that need no formalisation; call
status to see what is still missing. When status reports success, or its only
failure is the waiver line for given sentences, call finish with "complete"
(the harness refuses "complete" otherwise);
when you have a faithful formalisation with a step you believe does not
follow, call finish with "gap". You may issue several tool calls per turn; they run in order.
"""

DOCUMENT_ARM = """You have no interactive tools. Each turn, write the COMPLETE formalisation as
one JSON document (format below). The harness freezes your targets from your
first document (they cannot change later), adds every node, runs the checker
on every step and returns diagnostics: parse errors, per-step results
(follows / countermodel with the model / unknown), unanchored assumptions and
uncovered sentences. Then write a corrected COMPLETE document. The session
ends when a document passes every check (apart from waivers of given
sentences), when you include "finish", or when the budget runs out.

Document format (JSON, no comments):
{"targets": {"<target id>": "<VE statement>"},
 "nodes": [{"name": "<[a-z][a-z0-9_]*>", "text": "<VE statement>",
            "anchors": ["<sentence id>", ...], "parents": ["<node name>", ...]}],
 "waivers": {"<sentence id>": "<reason>"},
 "finish": {"verdict": "complete" | "gap", "gap_steps": ["<node>"], "note": "..."}}
"finish" is optional; include it only when you are done.
"""

FINISH_TOOL = {"name": "finish", "description": (
    "End the session. verdict 'complete' when status reports success or its only failure is the waiver "
    "line for given sentences; 'gap' when your faithful "
    "formalisation has step(s) that do not follow (name them in gap_steps)."),
    "input_schema": {"type": "object", "properties": {
        "verdict": {"type": "string", "enum": ["complete", "gap"]},
        "gap_steps": {"type": "array", "items": {"type": "string"}},
        "note": {"type": "string"}}, "required": ["verdict"], "additionalProperties": False}}

TEXT_PROTOCOL = """Tool-call protocol (text): this endpoint has no native tools. To act, end
your reply with ONE fenced JSON block, exactly:
```json
{{"calls": [{{"tool": "<tool name>", "arguments": {{...}}}}, ...]}}
```
with 1 to {per_turn} calls, run in order. Keep any prose before the block short.
The harness returns each call's JSON result in the next message. Tools
(name, description, JSON schema of arguments):
{tools}
"""

DOCUMENT_TEXT_PROTOCOL = """Reply format: end your reply with ONE fenced ```json block containing the
document. Keep any prose before the block short.
"""


def author_system(arm, *, text_protocol, tools=None, per_turn=10):
    parts = [TASK, GUIDE]
    if arm == "A2":
        parts.append(DOCUMENT_ARM)
        if text_protocol:
            parts.append(DOCUMENT_TEXT_PROTOCOL)
    else:
        parts.append(TOOLS_ARM)
        if text_protocol:
            listing = "\n".join(json.dumps({"name": t["name"], "description": t["description"],
                                            "arguments": t["input_schema"]}, ensure_ascii=False)
                                for t in tools)
            parts.append(TEXT_PROTOCOL.format(per_turn=per_turn, tools=listing))
    return "\n\n".join(p.strip() for p in parts) + "\n"


def item_materials(session):
    """The same materials for every arm: sentences, targets, vocabulary."""
    view = session.apply("sentences")
    lines = ["SENTENCES (id [role] text):"]
    for s in view["sentences"]:
        role = s["role"] + ("" if s["asserting"] else ", non-asserting")
        lines.append(f"  {s['id']} [{role}] {s['text']}")
    lines.append("TARGETS:")
    for t in view["targets"]:
        lines.append(f"  {t['id']} -> sentence {t['sentence']['id']}: {t['sentence']['text']}")
    vocab = view["vocabulary"]
    lines.append("VOCABULARY:")
    lines.append("  sorts: " + ", ".join(f"{k} ({v})" for k, v in vocab["sorts"].items()))
    lines.append("  predicates (name(argument sorts): gloss):")
    for k, v in vocab["predicates"].items():
        lines.append(f"    {k}({', '.join(v['arguments'])}): {v['gloss']}")
    lines.append("  constants: " + ", ".join(f"@{k} ({v})" for k, v in vocab["constants"].items()))
    return "\n".join(lines)


def budget_line(state):
    return (f"[budget] spent ${state['spent']:.4f} of ${state['budget']:.2f} "
            f"(author + proposer); tool calls {state['tool_calls']} of {state['max_tool_calls']}; "
            f"turns {state['turns']} of {state['max_turns']}.")


# ------------------------------------------------------------------ audit

AUDIT_SYSTEM = """You audit formalisations for FIDELITY. You never see whether any proof
succeeded, and you must not guess. Reply with a single JSON object only."""

AUDIT_INSTRUCTIONS = """Below is an English argument split into sentences (with roles), a glossary of
predicate senses, and for each sentence the formal statement(s) someone wrote
for it, shown as deterministic English paraphrases (sense names appear in the
predicate names, e.g. ready_packing_completed). Some sentences were instead
WAIVED with a reason, and some were left without any formalisation.

For each unit judge fidelity only:
- A formalised sentence is "faithful" if the paraphrase(s) together say what the
  sentence says: same entities, same conditions and conclusions, same
  direction of every 'if ... then', nothing added and nothing dropped. When a
  given sentence names a sense, the predicate must be that sense. When a claimed
  sentence leaves a word's sense open, the chosen sense must be one that the
  sentence's own stated reasons (via the given sentences) could establish; if
  several could, any of them is acceptable. For a sentence that states
  a conclusion with reasons ("because X, Y"), formalising the conclusion Y is
  faithful; the reasons may appear elsewhere.
- A formalisation may split one sentence into several statements; judge them
  together. A statement marked "also anchored to" other sentences may state
  several sentences jointly: it is faithful for THIS sentence only if it states
  this sentence's content correctly; a statement that states only some other
  sentence's conclusion does not formalise this one (unfaithful).
- A waiver is "acceptable" if the sentence asserts nothing the argument's
  reasoning relies on (e.g. a list of declared rule names, a statement of which
  checks remain unassumed, a fact never used).
Use "unfaithful"/"unacceptable" when something is wrong, "unclear" only when
the sentence itself is too ambiguous to judge.

Return {"units": [{"unit": "<unit id>", "verdict": "faithful|unfaithful|unclear|acceptable|unacceptable",
"reason": "<one sentence>"}]} with exactly one entry per unit id listed.
"""
