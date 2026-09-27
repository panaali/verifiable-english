"""Versioned, deterministic *possible* readings of source English.

A match is a prompt to inspect, never evidence that English has only these
readings. Only independently checked separating models produce reading cards.
"""
from __future__ import annotations

from dataclasses import dataclass
from contextlib import contextmanager
import re
import sys
import time
from typing import Callable, Mapping

from .. import ast
from ..ast import check_formula
from ..background import background
from ..background import validate_background
from ..errors import VEError
from ..evaluate import evaluate
from ..identity import meaning_id
from ..english import parse_english_with_metadata, render_english
from ..search import find_distinguishing_model

CATALOGUE_VERSION = "ve.ambiguity-patterns@1"
MAX_CANDIDATES = 32
MAX_COMPARISONS = 496
MAX_CARDS = 3
SEARCH_LIMITS = {"max_domain_size": 2, "min_domain_size": 0,
                 "max_models": 10_000, "max_evaluations": 1_000_000}
OPERATION_SECONDS = 8


class _Deadline(BaseException):
    """Raised inside a guarded region; BaseException so broad handlers cannot swallow it."""

    def __init__(self, budget=None):
        self.budget = budget


class Budget:
    """One operation deadline shared by every nested step of that operation.

    Checkpoints are numbered in execution order. A live budget reads the
    monotonic clock and records the first expired checkpoint; a replayed budget
    fires at exactly that recorded checkpoint, so ledger replay reproduces
    deadline outcomes without reading the clock. Expiry is sticky.
    """
    def __init__(self, seconds=None, *, stop=None, replay=False, fire_at=None):
        self.stop = stop if stop is not None else (
            float("inf") if seconds is None else time.monotonic() + seconds)
        self.replay, self.fire_at = replay, fire_at
        self.checks = 0
        self.fired = None
        self._regions = []

    def _hit(self, ordinal):
        if self.fired is None and ((ordinal == self.fire_at) if self.replay
                                   else time.monotonic() >= self.stop):
            self.fired = ordinal
        return self.fired is not None

    def expired(self) -> bool:
        self.checks += 1
        return self._hit(self.checks)

    @contextmanager
    def guard(self):
        """Run a region that raises _Deadline once this budget expires.

        Nested regions keep the outermost trace, so an inner step can neither
        extend the deadline nor displace the enclosing enforcement.
        """
        if self.expired():
            raise _Deadline(self)
        self._regions.append(self.checks)
        if self.replay or len(self._regions) > 1 or self.stop == float("inf"):
            try:
                yield
            finally:
                self._regions.pop()
            return
        previous = sys.gettrace()
        def trace(_frame, _event, _arg):
            if time.monotonic() >= self.stop:
                if self.fired is None:
                    self.fired = self._regions[-1]
                raise _Deadline(self)
            return trace
        sys.settrace(trace)
        try:
            yield
        finally:
            sys.settrace(previous)
            self._regions.pop()


def _budget(deadline) -> Budget:
    return deadline if isinstance(deadline, Budget) else Budget(
        OPERATION_SECONDS if deadline is None else None,
        stop=None if deadline is None else deadline)


@dataclass(frozen=True)
class Pattern:
    id: str
    tokens: str
    required: tuple[str, ...]
    constructor: Callable[[Mapping], tuple[tuple[str, ast.Formula], ...]]
    paraphrases: tuple[str, ...]

    def matches(self, source: str) -> bool:
        return re.search(self.tokens, source, flags=re.I) is not None


def _scope(s):
    e, v, r = s["every_sort"], s["some_sort"], s["relation"]
    return (("individual", ast.Forall(e, ast.Exists(v, ast.Binary(r, ast.Var(1), ast.Var(0))))),
            ("shared", ast.Exists(v, ast.Forall(e, ast.Binary(r, ast.Var(0), ast.Var(1))))))


def _negation(s):
    p, sort = s["predicate"], s["sort"]
    return (("none", ast.Not(ast.Exists(sort, ast.Unary(p, ast.Var(0))))),
            ("not_all", ast.Not(ast.Forall(sort, ast.Unary(p, ast.Var(0))))))


def _coordination(s):
    p, a, b = s["predicate"], s["left"], s["right"]
    return (("both", ast.And(ast.Unary(p, ast.Const(a)), ast.Unary(p, ast.Const(b)))),
            ("either", ast.Or(ast.Unary(p, ast.Const(a)), ast.Unary(p, ast.Const(b)))))


def _collective(s):
    p, group, members = s["predicate"], s["group"], tuple(s["members"])
    if len(members) < 2:
        raise ValueError("collective pattern needs at least two members")
    each = ast.Unary(p, ast.Const(members[0]))
    for member in members[1:]:
        each = ast.And(each, ast.Unary(p, ast.Const(member)))
    return (("group", ast.Unary(p, ast.Const(group))), ("each", each))


def _attachment(s):
    p, left, right = s["modifier"], s["left"], s["right"]
    return (("left", ast.Unary(p, ast.Const(left))),
            ("right", ast.Unary(p, ast.Const(right))))


def _reference(s):
    p = s["predicate"]
    return tuple((name, ast.Unary(p, ast.Const(name))) for name in s["antecedents"])


def _ellipsis(s):
    if s.get("transitive"):
        raise ValueError("transitive predicate copy requires a confirmed scoped completion")
    subject, predicates = s["subject"], tuple(s["predicates"])
    return tuple((p, ast.Unary(p, ast.Const(subject))) for p in predicates)


PATTERNS = (
    Pattern("scope.every_some@1", r"\b(every|each)\b.*\b(a|some)\b",
            ("every_sort", "some_sort", "relation"), _scope,
            ("Each {every_sort} stands in {relation} to at least one {some_sort}; choices may differ.",
             "One {some_sort} stands in {relation} to every {every_sort}.")),
    Pattern("scope.negation@1", r"\b(not|no|never)\b.*\b(all|every|some|any)\b|\b(not all|no)\b",
            ("sort", "predicate"), _negation,
            ("No {sort} is {predicate}.", "At least one {sort} is not {predicate}.")),
    Pattern("coordination.list@1", r"\b(and|or|either)\b",
            ("predicate", "left", "right"), _coordination,
            ("Both {left} and {right} are {predicate}.", "At least one of {left} and {right} is {predicate}.")),
    Pattern("coordination.collective@1", r"\b(together|collectively|team|group)\b",
            ("predicate", "group", "members"), _collective,
            ("The group is {predicate}.", "Each member is {predicate}.")),
    Pattern("attachment.modifier@1", r"\b(which|that|with|who)\b",
            ("modifier", "left", "right"), _attachment,
            ("{left} has the modifier {modifier}.", "{right} has the modifier {modifier}.")),
    Pattern("discourse.reference@1", r"\b(it|they|them|her|his|their)\b",
            ("predicate", "antecedents"), _reference,
            ("The named antecedent has property {predicate}.",)),
    Pattern("ellipsis.predicate_copy@1", r"\b(does too|do too|did too|also does)\b",
            ("subject", "predicates"), _ellipsis,
            ("{subject} also has the confirmed predicate.",)),
)


def pattern_by_id(pattern_id: str) -> Pattern:
    return next(p for p in PATTERNS if p.id == pattern_id)


def candidates(env, source: str, bindings: Mapping, *, pattern_id: str):
    """Construct only checked meanings. Missing/non-constant referents stay residual."""
    pattern = pattern_by_id(pattern_id)
    if not pattern.matches(source):
        return (), "pattern does not match source"
    if pattern_id == "discourse.reference@1" and re.search(r"\b(some|an?|another)\s+\w+", source, re.I):
        return (), "existential antecedent requires a confirmed scoped rewrite"
    missing = set(pattern.required) - set(bindings)
    if missing:
        return (), "missing bindings: " + ", ".join(sorted(missing))
    # A connective in the source does not license the opposite connective.
    # Likewise, the old attachment constructor only moved a predicate between
    # constants; it did not represent attachment of a modifier in the source.
    if pattern_id == "attachment.modifier@1":
        return (), "modifier attachment has no supported source reading constructor"
    try:
        rows = pattern.constructor(bindings)
        if pattern_id == "coordination.list@1":
            rows = tuple(row for row in rows if row[0] ==
                         ("both" if re.search(r"\band\b", source, re.I) else "either"))
        if pattern_id == "scope.negation@1":
            rows = tuple(row for row in rows if row[0] ==
                         ("none" if re.search(r"\bno\b", source, re.I) else "not_all"))
        for _, formula in rows:
            check_formula(env, formula)
    except (VEError, ValueError, KeyError, TypeError) as exc:
        return (), "unsupported meaning: " + str(exc)
    return rows, None


def checked_wording(env, wording: str, formula) -> str:
    """The exact displayed sentence must have one full writable derivation."""
    if not isinstance(wording, str) or not wording.strip():
        raise ValueError("empty displayed meaning")
    if not (wording.endswith(".") or wording.endswith(".\n")):
        raise ValueError("displayed meaning must be a writable sentence ending in a period")
    source = wording if wording.endswith(".\n") else wording + "\n"
    try:
        parsed = parse_english_with_metadata(env, source)
    except (VEError, ValueError, TypeError) as exc:
        raise ValueError("displayed meaning fails full English derivation") from exc
    if len(parsed.document.formulas) != 1 or parsed.document.formulas[0] != formula:
        raise ValueError("displayed meaning fails AST correspondence")
    return wording


def review(env, source: str, bindings: Mapping, *, pattern_id: str,
           cursor: int = 0, deadline: "float | Budget | None" = None) -> dict:
    """Return distinct cards only after search and independent model validation.

    Every unexamined or unresolved pair remains pending. Cursor is a pair index
    for display pagination only; approval requires zero pending pairs globally.
    Every step, including wording parses and model replay, runs inside the
    operation budget; an expired budget leaves the remaining work pending.
    """
    budget = _budget(deadline)
    expired = {"reason": "operation deadline (8 seconds)"}
    result = {"catalogue_version": CATALOGUE_VERSION, "pattern_id": pattern_id,
              "limits": {**SEARCH_LIMITS, "operation_seconds": OPERATION_SECONDS,
                         "max_candidates": MAX_CANDIDATES, "max_comparisons": MAX_COMPARISONS,
                         "max_cards": MAX_CARDS}, "cards": [], "pending": [],
              "candidate_count": 0, "comparison_count": 0, "candidates": [],
              "cursor": cursor, "next_cursor": None, "residual": None}
    try:
        with budget.guard():
            rows, residual = candidates(env, source, bindings, pattern_id=pattern_id)
    except _Deadline as exc:
        if exc.budget is not budget:
            raise
        result["pending"].append(dict(expired))
        return result
    result["candidate_count"], result["residual"] = len(rows), residual
    if residual:
        return result
    worded = []
    for name, formula in rows:
        try:
            with budget.guard():
                wording = checked_wording(env, render_english(formula, env) + ".", formula)
                mid = meaning_id(env, formula)
        except _Deadline as exc:
            if exc.budget is not budget:
                raise
            result["pending"].append(dict(expired))
            return result
        except (VEError, ValueError) as exc:
            result["residual"] = f"candidate {name} has no checked writable wording: {exc}"
            return result
        if "has the recorded relation" in wording or re.search(r'"[a-z][a-z0-9_]*"', wording):
            result["residual"] = f"candidate {name} needs admitted plain English vocabulary"
            return result
        worded.append({"name": name, "meaning_id": mid, "wording": wording})
    result["candidates"] = worded
    if len(rows) > MAX_CANDIDATES:
        result["residual"] = "candidate limit (32)"
        result["pending"].append({"reason": result["residual"]})
        return result
    pairs = [(i, j) for i in range(len(rows)) for j in range(i + 1, len(rows))]
    if type(cursor) is not int or not 0 <= cursor <= len(pairs):
        raise ValueError("invalid comparison cursor")
    end = min(len(pairs), MAX_COMPARISONS)
    for index in range(cursor, end):
        i, j = pairs[index]
        left, right = rows[i], rows[j]
        pair = [left[0], right[0]]
        try:
            with budget.guard():
                card, reason = _compare(env, left, right, pattern_id)
        except _Deadline as exc:
            if exc.budget is not budget:
                raise
            # The interrupted pair is retried on the next page and not counted.
            result["pending"].append({"pair": pair, **expired})
            result["next_cursor"] = index
            break
        except VEError as exc:
            card, reason = None, str(exc)
        if card is None:
            result["comparison_count"] += 1
            result["pending"].append({"pair": pair, "reason": reason})
            continue
        if len(result["cards"]) >= MAX_CARDS:
            # This pair is retried on the next page.
            result["pending"].append({"pair": pair, "reason": "page card limit (3)"})
            result["next_cursor"] = index
            break
        result["comparison_count"] += 1
        card["paraphrases"] = [worded[i]["wording"], worded[j]["wording"]]
        result["cards"].append(card)
    if result["next_cursor"] is None and end < len(pairs):
        result["next_cursor"] = end
        result["pending"].append({"reason": "pair comparison limit (496)"})
    if budget.expired() and not result["pending"]:
        result["pending"].append(dict(expired))
    return result


def _compare(env, left, right, pattern_id):
    """Search and independently replay one separating model: (card, None) or (None, reason)."""
    found = find_distinguishing_model(env, left[1], right[1], **SEARCH_LIMITS)
    if found.status != "Found" or found.model is None:
        return None, found.detail or found.status
    # Regenerate Background, validate the model, and evaluate every premise.
    validate_background(env, found.model)
    if any(evaluate(env, premise.formula, found.model,
                    max_evaluations=SEARCH_LIMITS["max_evaluations"], trace=False).value is not True
           for premise in background(env)):
        return None, "model violates regenerated Background"
    a = evaluate(env, left[1], found.model, max_evaluations=SEARCH_LIMITS["max_evaluations"], trace=False)
    b = evaluate(env, right[1], found.model, max_evaluations=SEARCH_LIMITS["max_evaluations"], trace=False)
    if a.value is None or b.value is None or a.value == b.value:
        return None, "model replay failed"
    return {"pair": [left[0], right[0]], "meaning_ids": [meaning_id(env, left[1]),
            meaning_id(env, right[1])], "model": found.model.to_dict(),
            "values": [a.value, b.value], "pattern_id": pattern_id}, None
