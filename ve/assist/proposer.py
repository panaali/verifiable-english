"""``propose(sentence)``: a cheap model drafts 1-3 VE candidates for ONE sentence.

The model backend is injected (``session.proposer``); this module never calls a
provider itself. Every candidate is parsed and type-checked by the ordinary VE
parser; invalid ones get one located repair round, then are dropped. Valid
candidates are shown with the deterministic paraphrase and, for each pair
that differs in meaning, a checked distinguishing model. Candidates never
enter the graph: the author must ``accept``/``add_node`` them explicitly, and
the ledger marks such nodes ``proposer-verbatim`` or ``proposer-edited``.
"""
from __future__ import annotations

import hashlib
import json
import re

from .. import ast
from ..errors import VEError
from ..search import check_countermodel, find_distinguishing_model
from .ground import ground_countermodel

PROMPT_VERSION = "ve-assist-propose@3"
SYSTEM = ("You formalise ONE English sentence into Verifiable English (VE) strict syntax. "
          "Reply with a single JSON object and nothing else.")

GRAMMAR = """VE strict syntax (exact spacing and parentheses; every compound operand is parenthesised):
  F ::= true | false
      | T is UNARY                      e.g. @pebble is marked
      | T BINARY T                      e.g. @lot1 supplied @pebble
      | T equals T
      | not (F)
      | (F) and (F)      | (F) or (F)   binary only: (A) and ((B) and (C))
      | if (F), then (F)
      | for every SORT v, (F)  | there exists SORT v, (F)
  T ::= variable | @constant
Examples (unrelated vocabulary, do not copy symbols):
  if ((@pebble is marked) and (@pebble is round)), then (@stone is marked).
  for every rock r, (if (r is marked), then (r is round)).
Never add extra parentheses: each operand gets exactly one pair, e.g.
  if ((@a is p) and (@b is q)), then (@c is r).   not   if (((@a is p) and (@b is q))), then ((@c is r)).
Use ONLY the sorts, predicates and constants listed below. Where a word has
several senses, pick the predicate whose gloss matches this use."""

INSTRUCTIONS = """Return {{"candidates":[{{"ve":"<one VE statement ending with a period>","reading":"<short English gloss of this reading>"}}]}}
with 1 to {k} candidates. Formalise only what THIS sentence asserts, as one statement
(use a conjunction for a list of facts). If it gives reasons for a conclusion
("because X, Y" / "since X, it follows that Y"), formalise the conclusion Y; the
reasons are parents. If it states a conditional ("would imply", "if ... then"),
formalise the conditional. When a word in the sentence matches SEVERAL predicates
(senses) and the sentence itself does not settle which, give one candidate per
plausible sense rather than guessing. Otherwise give more than one candidate only
when the sentence genuinely admits different readings (scope, conditional vs
asserted). Different candidates must differ in meaning."""


# Anything that looks like a credential is redacted from every logged or returned error and from
# backend-reported identity fields (a token echoed as a "model name" must not reach the ledger).
# The same patterns live in ve_experiments/claude_cli.py, which does not import ve.
_SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_\-]{6,}"),                                    # API / OAuth keys
    re.compile(r"eyJ[A-Za-z0-9_\-]{6,}\.[A-Za-z0-9_\-]{6,}(?:\.[A-Za-z0-9_\-]*)?"),  # JWTs
    re.compile(r"(?i)\bbearer\s+[^\s'\",;\]]+"),
    re.compile(r"(?i)\b([a-z_]*(?:token|secret|password|api_?key|credential)[a-z_]*)\s*[:=]\s*[^\s'\",;\]]{8,}"),
    re.compile(r"(?<![A-Za-z0-9_\-])(?=[A-Za-z0-9_\-]*[0-9])(?=[A-Za-z0-9_\-]*[A-Za-z])[A-Za-z0-9_\-]{32,}"),
)


def redact_secrets(value):
    """Return ``value`` (any str; other types pass through) with credential-like substrings replaced."""
    if not isinstance(value, str):
        return value
    for pattern in _SECRET_PATTERNS:
        value = pattern.sub("[REDACTED]", value)
    return value


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def build_prompt(session, sentence, k, note=None):
    s = session.sentences[sentence]
    block = [session.sentences[i]["text"] for i in session.sentence_order
             if session.sentences[i]["block"] == s["block"]]
    vocab = session.vocabulary()
    accepted = [f"{n.name}: {n.text}" for n in session.nodes.values()][:40]
    targets = [f"{t}: {row['text']}" for t, row in session.targets.items() if row["text"]]
    parts = [GRAMMAR, "Vocabulary:\n" + json.dumps(vocab, ensure_ascii=False, sort_keys=True)]
    if targets:
        parts.append("Frozen targets:\n" + "\n".join(targets))
    if accepted:
        parts.append("Already accepted statements:\n" + "\n".join(accepted))
    parts.append(f"Paragraph ({s['role']}):\n" + " ".join(block))
    parts.append("Sentence to formalise:\n" + s["text"])
    if note:
        parts.append("Author note:\n" + str(note)[:500])
    parts.append(INSTRUCTIONS.format(k=k))
    return "\n\n".join(parts)


def build_repair_prompt(prompt, raw, diagnostics):
    return (prompt + "\n\nYour previous reply:\n" + raw[:4000] +
            "\n\nNone of those candidates parsed. Diagnostics:\n" +
            json.dumps(diagnostics, ensure_ascii=False) +
            "\nReturn corrected JSON in the same format.")


def _matching(text):
    stack, pairs = [], {}
    for i, ch in enumerate(text):
        if ch == "(":
            stack.append(i)
        elif ch == ")":
            if not stack:
                return None
            pairs[stack.pop()] = i
    return None if stack else pairs


def strip_redundant_parentheses(text):
    """Remove parenthesis pairs that directly wrap another pair: '((X))' -> '(X)'.

    VE's grammar has no extra grouping production, so such a pair can only be
    redundant; removing it cannot change which formula a successful parse yields.
    Also drops one pair wrapping the whole statement. The result is re-parsed.
    """
    body = text.strip()
    period = body.endswith(".")
    body = body[:-1].rstrip() if period else body
    changed = True
    while changed:
        changed = False
        pairs = _matching(body)
        if pairs is None:
            return text
        if pairs.get(0) == len(body) - 1:
            body, changed = body[1:-1], True
            continue
        for start, end in sorted(pairs.items()):
            if body[start + 1:start + 2] == "(" and pairs.get(start + 1) == end - 1:
                body, changed = body[:start] + body[start + 1:end] + body[end + 1:], True
                break
    return body + ("." if period else "")


def extract_candidates(text):
    """Parse the model's JSON reply leniently (code fences, surrounding prose)."""
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        return [], "no JSON object in reply"
    try:
        data = json.loads(match[0])
    except ValueError as exc:
        return [], f"invalid JSON: {exc}"
    rows = data.get("candidates") if type(data) is dict else None
    if type(rows) is not list:
        return [], "reply has no candidates list"
    out = []
    for row in rows:
        if type(row) is dict and isinstance(row.get("ve"), str):
            out.append({"ve": row["ve"], "reading": str(row.get("reading", ""))[:300]})
        elif isinstance(row, str):
            out.append({"ve": row, "reading": ""})
    return out, None


class ProposerBackendError(VEError):
    code = "ProposerBackendError"


def _call(session, purpose, system, prompt, item):
    recorded = session.recorded_model_call()
    if recorded is not None:
        if recorded.get("prompt_digest") != _digest([system, prompt]):
            raise VEError("Recorded model call does not match the replayed prompt")
        call = recorded
    else:
        if session.proposer is None:
            raise VEError("No proposer backend is configured for this session")
        base = {"purpose": purpose, "prompt_version": PROMPT_VERSION, "prompt_digest": _digest([system, prompt]),
                "requested_model": getattr(session.proposer, "model_id", None), "item_id": item}
        try:
            reply = session.proposer(system, prompt, item)
        except Exception as exc:  # the backend boundary: log the failure and the usage actually spent
            spent = getattr(exc, "usage", None)
            spent = spent if type(spent) is dict else {}
            tokens = {k: spent.get(k) if type(spent.get(k)) is int and spent.get(k) >= 0 else None
                      for k in ("input_tokens", "output_tokens")}
            call = {**base, "failed": True, "text": None,
                    "error": redact_secrets(f"{type(exc).__name__}: {str(exc)}")[:300],
                    **tokens, "model": redact_secrets(spent.get("model")),
                    "account_label": redact_secrets(spent.get("account_label")),
                    "call_key": spent.get("call_key")}
        else:
            call = {**base, "text": reply["text"],
                    "input_tokens": reply.get("input_tokens"), "output_tokens": reply.get("output_tokens"),
                    "model": reply.get("model"), "account_label": reply.get("account_label"),
                    "call_key": reply.get("call_key")}
    session._model_calls.append(call)
    if call.get("failed"):
        raise ProposerBackendError("Proposer backend failed (usage recorded; propose again to retry): "
                                   + str(call.get("error")))
    if not isinstance(call.get("text"), str):
        raise VEError("Recorded model call has no reply text")
    return call


def run_propose(session, sentence, k=None, note=None):
    if sentence not in session.sentences:
        raise VEError(f"Unknown sentence id {sentence!r}")
    k = session.options["proposer_k"] if k is None else k
    if type(k) is not int or not 1 <= k <= 3:
        raise VEError("k must be 1, 2 or 3")
    pid = f"q{len(session.proposals) + 1}"
    prompt = build_prompt(session, sentence, k, note)
    # The event sequence number makes every propose attempt a fresh backend key, so a failed
    # call can be retried (the endpoint refuses to re-run a key that started or failed).
    item = f"{session.session_id}/{pid}/e{session._seq}"
    valid, dropped = [], []
    raw_prompt = prompt
    for round_number in range(1 + session.options["propose_repair_rounds"]):
        call = _call(session, "propose" if round_number == 0 else "repair", SYSTEM, prompt,
                     f"{item}/r{round_number}")
        rows, problem = extract_candidates(call["text"])
        if problem:
            dropped.append({"round": round_number, "raw": call["text"][:500], "error": problem})
        diagnostics = []
        for row in rows:
            repaired = None
            try:
                formula, surface = session._parse(row["ve"], "auto")
            except VEError as exc:
                normalised = strip_redundant_parentheses(row["ve"])
                try:
                    if normalised == row["ve"]:
                        raise exc
                    formula, surface = session._parse(normalised, "strict")
                    repaired = "redundant parentheses removed"
                except VEError:
                    diagnostics.append({"ve": row["ve"], "error": exc.to_dict()})
                    dropped.append({"round": round_number, "raw": row["ve"], "error": exc.to_dict()})
                    continue
            if any(v["formula"] == formula for v in valid):
                continue
            valid.append({"formula": formula, "reading": row["reading"], "surface": surface,
                          **({"repaired": repaired} if repaired else {})})
        if valid or round_number == session.options["propose_repair_rounds"]:
            break
        prompt = build_repair_prompt(raw_prompt, call["text"], diagnostics or [{"error": problem}])
    valid = valid[:k]
    candidates = []
    for i, row in enumerate(valid, 1):
        cid = f"{pid}.{i}"
        session.candidates[cid] = {"formula": row["formula"], "proposal": pid, "sentence": sentence}
        candidates.append({"id": cid, "text": session._canonical(row["formula"]),
                           "paraphrase": session.paraphrase_formula(row["formula"]),
                           "reading": row["reading"], "surface": row["surface"],
                           **({"repaired": row["repaired"]} if "repaired" in row else {})})
    comparisons = []
    for i in range(len(valid)):
        for j in range(i + 1, len(valid)):
            result = compare_formulas(session, valid[i]["formula"], valid[j]["formula"])
            comparisons.append({"a": candidates[i]["id"], "b": candidates[j]["id"], **result})
    session.proposals[pid] = {"sentence": sentence, "candidates": [c["id"] for c in candidates]}
    return {"proposal": pid, "sentence": session._sentence_view(sentence), "candidates": candidates,
            "dropped": dropped, "comparisons": comparisons,
            "note": "Candidates are drafts. Nothing is added until you accept or add_node."}


def _distinguish(session, a, b):
    """A checked model where a is true and b is false, or None."""
    status, model = ground_countermodel(session.env, (a,), b)
    if status == "Unsupported":
        budget = session._budget()
        result = find_distinguishing_model(session.env, a, b, max_domain_size=budget["max_domain_size"],
                                           max_models=budget["max_models"],
                                           max_evaluations=budget["max_evaluations"])
        model = result.model
    if model is None:
        return None
    checked = check_countermodel(session.env, (a,), b, model)
    return model if checked.valid else None


def compare_formulas(session, a, b):
    """equivalent / a_stronger / b_stronger / incomparable / unknown, with models."""
    forward = session._entails([a], b)
    backward = session._entails([b], a)
    result = {"a_text": session._canonical(a), "b_text": session._canonical(b)}
    if forward and backward:
        return {**result, "relation": "equivalent"}
    models = []
    for label, left, right, proved in (("a_true_b_false", a, b, forward), ("b_true_a_false", b, a, backward)):
        if proved:
            continue
        model = _distinguish(session, left, right)
        if model is not None:
            models.append({"kind": label, "model_id": model.model_id,
                           **session.describe_model(model, (a, b)),
                           "a_value": label == "a_true_b_false", "b_value": label == "b_true_a_false"})
    found = {m["kind"] for m in models}
    relation = ("a_stronger" if forward and "b_true_a_false" in found else
                "b_stronger" if backward and "a_true_b_false" in found else
                "incomparable" if found == {"a_true_b_false", "b_true_a_false"} else
                "different" if found else "unknown")
    return {**result, "relation": relation, "distinguishing_models": models}
