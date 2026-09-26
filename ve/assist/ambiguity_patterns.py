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
from ..errors import VEError
from ..evaluate import evaluate
from ..identity import meaning_id
from ..search import find_distinguishing_model

CATALOGUE_VERSION = "ve.ambiguity-patterns@1"
MAX_CANDIDATES = 32
MAX_COMPARISONS = 496
MAX_CARDS = 3
SEARCH_LIMITS = {"max_domain_size": 2, "min_domain_size": 0,
                 "max_models": 10_000, "max_evaluations": 1_000_000}
OPERATION_SECONDS = 8


class _Deadline(Exception):
    pass


@contextmanager
def _operation_budget(stop):
    previous = sys.gettrace()
    def trace(_frame, _event, _arg):
        if time.monotonic() >= stop:
            raise _Deadline
        return trace
    sys.settrace(trace)
    try:
        yield
    finally:
        sys.settrace(previous)


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
    try:
        rows = pattern.constructor(bindings)
        for _, formula in rows:
            check_formula(env, formula)
    except (VEError, ValueError, KeyError, TypeError) as exc:
        return (), "unsupported meaning: " + str(exc)
    return rows, None


def review(env, source: str, bindings: Mapping, *, pattern_id: str,
           cursor: int = 0, deadline: float | None = None) -> dict:
    """Return distinct cards only after search and independent model validation.

    Every unexamined or unresolved pair remains pending. Cursor is a pair index
    for display pagination only; approval requires zero pending pairs globally.
    """
    rows, residual = candidates(env, source, bindings, pattern_id=pattern_id)
    result = {"catalogue_version": CATALOGUE_VERSION, "pattern_id": pattern_id,
              "limits": {**SEARCH_LIMITS, "operation_seconds": OPERATION_SECONDS,
                         "max_candidates": MAX_CANDIDATES, "max_comparisons": MAX_COMPARISONS,
                         "max_cards": MAX_CARDS}, "cards": [], "pending": [],
              "candidate_count": len(rows), "comparison_count": 0,
              "cursor": cursor, "next_cursor": None, "residual": residual}
    if residual:
        return result
    if len(rows) > MAX_CANDIDATES:
        result["residual"] = "candidate limit (32)"
        result["pending"].append({"reason": result["residual"]})
        return result
    pairs = [(i, j) for i in range(len(rows)) for j in range(i + 1, len(rows))]
    if type(cursor) is not int or not 0 <= cursor <= len(pairs):
        raise ValueError("invalid comparison cursor")
    end = min(len(pairs), MAX_COMPARISONS)
    stop = deadline if deadline is not None else time.monotonic() + OPERATION_SECONDS
    for index in range(cursor, end):
        if time.monotonic() >= stop:
            result["pending"].append({"reason": "operation deadline (8 seconds)", "pair": index})
            result["next_cursor"] = index
            break
        i, j = pairs[index]
        left, right = rows[i], rows[j]
        result["comparison_count"] += 1
        try:
            with _operation_budget(stop):
                found = find_distinguishing_model(env, left[1], right[1], **SEARCH_LIMITS)
            if found.status != "Found" or found.model is None:
                result["pending"].append({"pair": [left[0], right[0]],
                                          "reason": found.detail or found.status})
                continue
            # Regenerate Background, validate the model, and evaluate every premise.
            premises = background(env)
            if any(evaluate(env, premise.formula, found.model,
                            max_evaluations=SEARCH_LIMITS["max_evaluations"], trace=False).value is not True
                   for premise in premises):
                result["pending"].append({"pair": [left[0], right[0]],
                                          "reason": "model violates regenerated Background"})
                continue
            a = evaluate(env, left[1], found.model, max_evaluations=SEARCH_LIMITS["max_evaluations"], trace=False)
            b = evaluate(env, right[1], found.model, max_evaluations=SEARCH_LIMITS["max_evaluations"], trace=False)
            if a.value is None or b.value is None or a.value == b.value:
                result["pending"].append({"pair": [left[0], right[0]], "reason": "model replay failed"})
                continue
            card = {"pair": [left[0], right[0]], "meaning_ids": [meaning_id(env, left[1]),
                     meaning_id(env, right[1])], "model": found.model.to_dict(),
                     "values": [a.value, b.value], "pattern_id": pattern_id}
            templates = pattern_by_id(pattern_id).paraphrases
            if len(templates) == 2:
                card["paraphrases"] = [template.format(**bindings) for template in templates]
            else:
                card["paraphrases"] = [f"{name}: {templates[0].format(**bindings)}"
                                        for name in card["pair"]]
            if len(result["cards"]) < MAX_CARDS:
                result["cards"].append(card)
            else:
                result["pending"].append({"pair": card["pair"], "reason": "page card limit (3)"})
                result["next_cursor"] = index
                break
        except _Deadline:
            result["pending"].append({"pair": [left[0], right[0]],
                                      "reason": "operation deadline (8 seconds)"})
            result["next_cursor"] = index
            break
        except VEError as exc:
            result["pending"].append({"pair": [left[0], right[0]], "reason": str(exc)})
    if result["next_cursor"] is None and end < len(pairs):
        result["next_cursor"] = end
        result["pending"].append({"reason": "pair comparison limit (496)"})
    return result
