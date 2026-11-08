"""Lean's readings of one act phrase under a rule's modal words (act-phrases 7, AP-4): the relay of the
`act-readings` service mode (`lean/VE/Acts/Run.lean`, `runActReadings`).

Lean lexes the phrase, lists its readings (`phraseReadings`) and paraphrases them, and writes each token's UTF-8 byte
span and each act's token indices. This module builds the request, relays the row and checks only what a relay checks
(DRI ruling R8): the row's schema (the service checks `act-readings.json`, which bounds the readings at Lean's 64) and
its binding to the request: the readings are non-empty exactly when the verdict is `LISTED`; every span lies within
the phrase's UTF-8 bytes, in order and disjoint; every `from` index names a token, none twice in one act; no two
readings have the same acts or the same paraphrase. It lexes nothing and composes no text. Binding cannot see a
reading dropped with its row (spec 7, "What binding cannot show"): that is Lean's content (`phraseReadings_exact`).
"""
from __future__ import annotations

from .errors import CheckerUnavailable

MODE = "act-readings"


def request(phrase: str, *, fixed=(), frames=(), adverbs=(), role: str = "plain", sign: bool = True,
            form: str | None = None, case_id: str = MODE) -> dict:
    """The mode's request (spec 7): the phrase, the `acts` block's fixed phrases, frames and adverbs as data, and the
    rule's role, sign and (for a plain act) form, absent when `None`."""
    case = {"id": case_id, "phrase": phrase, "fixed": list(fixed), "frames": [dict(f) for f in frames],
            "adverbs": list(adverbs), "role": role, "sign": sign}
    return case if form is None else {**case, "form": form}


def answer_problem(row, case: dict) -> str | None:
    """Why Lean's `act-readings` row is not an answer to `case` (R8: its binding to the request), or None."""
    if type(row) is not dict or row.get("status") != "ok" or row.get("id") != case["id"]:
        return "the row is not an answer to this case"
    readings, tokens, verdict = row.get("readings"), row.get("tokens"), row.get("verdict")
    if type(readings) is not list or type(tokens) is not list:
        return "the readings or tokens are not lists"
    if (verdict == "LISTED") != bool(readings) or (verdict != "LISTED") and tokens:
        return "the readings are not non-empty exactly when the verdict is LISTED"
    end = 0
    for span in tokens:
        if (type(span) is not list or len(span) != 2 or any(type(x) is not int for x in span)
                or not end <= span[0] < span[1] <= len(case["phrase"].encode("utf-8"))):
            return "a token span is not within the phrase, in order and disjoint"
        end = span[1]
    for reading in readings:
        for act in reading["acts"]:
            if any(not 0 <= i < len(tokens) for i in act["from"]):
                return "a token index is out of range"
            if len(set(act["from"])) != len(act["from"]):
                return "a token index occurs twice in one act"
    if len({repr(r["acts"]) for r in readings}) != len(readings):
        return "two readings have the same acts"
    if len({r["paraphrase"] for r in readings}) != len(readings):
        return "two readings have the same paraphrase"
    return None


def read_answer(row, case: dict) -> dict:
    """Lean's answer `row` to `case` after the binding check (`answer_problem`)."""
    problem = answer_problem(row, case)
    if problem is not None:
        raise CheckerUnavailable(f"CheckerUnavailable: Lean's act-readings answer is not bound to its request: {problem}")
    return {key: row[key] for key in ("verdict", "tokens", "readings", "diagnostic") if key in row}


def readings(phrase: str, **request_fields) -> dict:
    """Lean's readings of `phrase` (`request` names the fields): verdict, token spans, readings and diagnostic."""
    from .backends.relay import decide_once
    case = request(phrase, **request_fields)
    return read_answer(decide_once(MODE, case), case)
