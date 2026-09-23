"""JSON tool-calling API for ``ve assist`` (Anthropic-style tool schemas).

``tool_schemas(...)`` returns the tool list for one evaluation arm; the
proposer and premise-suggestion tools/parameters are only present when that
arm enables them. ``call_tool(session, name, arguments)`` executes one call,
logs it in the session ledger and returns a JSON-serialisable result; invalid
calls return ``{"ok": false, "error": ...}`` rather than raising.
"""
from __future__ import annotations

import json

from ..errors import VEError
from .session import AssistSession

_STR = {"type": "string"}
_STRS = {"type": "array", "items": {"type": "string"}}
_SURFACE = {"type": "string", "enum": ["auto", "strict", "english"],
            "description": "Input language: strict VE, the controlled English surface, or auto (strict first)."}


def _tool(name, description, properties, required=()):
    return {"name": name, "description": description,
            "input_schema": {"type": "object", "properties": properties, "required": list(required),
                             "additionalProperties": False}}


def tool_schemas(*, proposer=False, premise_suggestions=False):
    check_props = {"name": {**_STR, "description": "Step node to check."},
                   "invariants": {**_STRS, "description": "Optional closure-induction invariants (strict VE)."}}
    if premise_suggestions:
        check_props["suggest_premises"] = {"type": "boolean", "description":
            "If the step fails, also list premise suggestions. Suggestions can assume the gap away; "
            "a bridge suggestion is an unanchored assumption unless a given sentence states it."}
    tools = [
        _tool("sentences", "List the source sentences (id, role given/claimed/context), the targets, "
              "and the vocabulary (sorts, predicates with glosses, constants).", {}),
        _tool("freeze_target", "Commit the formal statement of a target sentence. Irreversible; must be "
              "done for every target before any node is added.",
              {"target": _STR, "text": {**_STR, "description": "One VE statement."}, "surface": _SURFACE,
               **({"candidate": {**_STR, "description": "Use a proposer candidate's text."}} if proposer else {})},
              ["target"]),
        _tool("add_node", "Add one node (one VE statement). No parents = an assumption; with parents = a step "
              "that check_step must certify. Anchor it to the sentence id(s) it formalises. An assumption "
              "is anchored only by a 'given' sentence.",
              {"name": {**_STR, "description": "New node name [a-z][a-z0-9_]*."},
               "text": {**_STR, "description": "One VE statement (omit to accept a candidate verbatim)."},
               "anchors": {**_STRS, "description": "Sentence ids this node formalises."},
               "parents": {**_STRS, "description": "Existing node names this step follows from."},
               "surface": _SURFACE,
               **({"candidate": {**_STR, "description": "Proposer candidate id to accept/edit."}} if proposer else {}),
               **({"suggestion": {**_STR, "description": "Premise-suggestion id to accept/edit."}}
                  if premise_suggestions else {})},
              ["name"]),
        _tool("rewrite", "Change a node's statement, anchors and/or parents. Invalidates its check and its "
              "children's checks.",
              {"name": _STR, "text": _STR, "anchors": _STRS, "parents": _STRS, "surface": _SURFACE}, ["name"]),
        _tool("remove_node", "Remove a node that is not a parent of another node.", {"name": _STR}, ["name"]),
        _tool("declare", "Declare a new predicate, constant or sort. A gloss (what it means) is required. "
              "Near-duplicates of existing vocabulary and names/glosses restating a target conclusion are "
              "blocked until acknowledged by flag.",
              {"name": _STR, "gloss": _STR,
               "kind": {"type": "string", "enum": ["predicate", "constant", "sort"]},
               "arguments": {**_STRS, "description": "Predicate argument sorts (1 or 2)."},
               "sort": {**_STR, "description": "Sort of a constant."},
               "verbalisation": {**_STR, "description": "Optional English template, e.g. '{0} is sealed'."},
               "acknowledge": {**_STRS, "description": "Flags from a blocked declaration you accept."}},
              ["name", "gloss"]),
        _tool("check_step", "Check whether a step follows from its parents. Returns 'follows' (a replayed "
              "certificate), 'countermodel' (a checked model where every parent is true and the conclusion "
              "false), or 'unknown'.", check_props, ["name"]),
        _tool("status", "Summarise progress: target certification (graph replay), unproved steps, unanchored "
              "assumptions and whether they are load-bearing, sentence coverage/waivers, renamed-conclusion "
              "flags, provenance counts and token usage. 'success' is true only when everything passes.", {}),
        _tool("waive", "Explicitly mark a sentence as not formalised, with a reason. The waiver is reported; "
              "waiving ANY asserting sentence blocks 'success', even one already covered or derived (every "
              "claimed sentence must be derived by a certified step, every given sentence covered).",
              {"sentence": _STR, "reason": _STR}, ["sentence", "reason"]),
        _tool("show", "Show all nodes (or one node, with history) with their deterministic English paraphrase.",
              {"name": _STR}),
        _tool("paraphrase", "Parse a VE statement without adding it; return canonical text and paraphrase.",
              {"text": _STR, "surface": _SURFACE}, ["text"]),
        _tool("compare", "Compare two statements (node names, target ids, candidate ids, or VE text): "
              "equivalent / a_stronger / b_stronger / incomparable, with checked distinguishing models.",
              {"a": _STR, "b": _STR}, ["a", "b"]),
    ]
    if proposer:
        tools.append(_tool("propose", "Ask a cheap model for 1-3 parsed, type-checked VE candidates for ONE "
                           "sentence, each with its paraphrase and distinguishing models between candidates. "
                           "Nothing is added until you accept.",
                           {"sentence": _STR, "k": {"type": "integer", "minimum": 1, "maximum": 3},
                            "note": {**_STR, "description": "Optional hint for the proposer."}}, ["sentence"]))
        tools.append(_tool("accept", "Add a proposer candidate verbatim as a node.",
                           {"candidate": _STR, "name": _STR, "anchors": _STRS, "parents": _STRS},
                           ["candidate", "name"]))
    return tools


def tools_for_session(session):
    return tool_schemas(proposer=session.proposer is not None,
                        premise_suggestions=session.options["premise_suggestions"])


def call_tool(session: AssistSession, name, arguments=None):
    allowed = {t["name"]: t for t in tools_for_session(session)}
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments) if arguments.strip() else {}
        except ValueError as exc:
            return session.log_rejection(str(name), {"raw": arguments},
                                         {"code": "InvalidArguments", "message": str(exc)})
    arguments = arguments or {}
    if type(arguments) is not dict:
        return session.log_rejection(str(name), {"raw": repr(arguments)[:200]},
                                     {"code": "InvalidArguments", "message": "arguments must be an object"})
    if name not in allowed:
        return session.log_rejection(str(name), arguments,
                                     {"code": "UnknownTool", "message": f"No tool {name!r} in this session"})
    extra = set(arguments) - set(allowed[name]["input_schema"]["properties"])
    if extra:
        return session.log_rejection(name, arguments, {"code": "InvalidArguments",
                                     "message": "Unknown argument(s): " + ", ".join(sorted(extra))})
    try:
        return session.apply(name, arguments)
    except VEError as exc:
        return {"ok": False, "error": exc.to_dict()}
    except RuntimeError as exc:  # never lose a backend failure: log it as a rejected call
        return session.log_rejection(name, arguments, {"code": "BackendError", "message": str(exc)[:500]})
