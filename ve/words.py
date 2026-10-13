"""Lean's situation lines, point clauses, filled-gap sentences and pair sentences (plan Q2.4): the relay of the
`words` service mode (`lean/VE/Words/Run.lean`).

Lean words every one of these lines (`VE.Words`): the readings routes' shown situations and filled gaps, and the
norm-defaults clauses, filling sentences and pair sentences. This module builds the request (the environment the
English is read in, its lexicon as Python selects it, one item per line), relays Lean's lines and checks only what a
relay checks (DRI ruling R8): the answer's schema (the service checks `words.json`) and its binding to the request,
the environment's and lexicon's identities and one non-empty line per item. It words nothing itself
(`tools/relay_lint.py`). Which elements, facts and points a line shows, and the suppositions after a situation, are
the caller's (plan 4.5: the soft and rights suppositions stay Python's).
"""
from __future__ import annotations

from collections import OrderedDict
import threading

from .errors import CheckerUnavailable

MODE = "words"
_LEXICONS: OrderedDict = OrderedDict()
_LEXICONS_LIMIT = 64
_lock = threading.Lock()


def lexicon(env) -> dict:
    """The lexicon Python selects for `env` (`english_grammar.export`), once per environment."""
    from .english import EnglishVocabulary
    from .english_grammar import export
    key = env.environment_id
    with _lock:
        found = _LEXICONS.get(key)
    if found is None:
        found = export(EnglishVocabulary(env))
        with _lock:
            _LEXICONS[key] = found
            while len(_LEXICONS) > _LEXICONS_LIMIT:
                _LEXICONS.popitem(last=False)
    return found


def request(env, items: list[dict]) -> dict:
    return {"id": MODE, "environment": env.to_dict(), "lexicon": lexicon(env), "items": items}


def answer_problem(result, case: dict, env) -> str | None:
    """Why Lean's `words` result is not an answer to `case` (R8: its binding to the request), or None."""
    from .english_grammar import lexicon_id
    if type(result) is not dict or set(result) != {"environment_id", "lexicon_id", "lines"}:
        return "the result's fields are not environment_id, lexicon_id and lines"
    if result["environment_id"] != env.environment_id:
        return "the result names another environment"
    if result["lexicon_id"] != lexicon_id(case["lexicon"]):
        return "the result names another lexicon"
    lines = result["lines"]
    if type(lines) is not list or len(lines) != len(case["items"]):
        return "the result does not have one line per item"
    if any(type(line) is not str or not line for line in lines):
        return "a line is not a non-empty string"
    return None


def lines(env, items: list[dict]) -> list[str]:
    """Lean's line for each item, in order."""
    if not items:
        return []
    from .backends.relay import decide_once
    case = request(env, items)
    row = decide_once(MODE, case)
    problem = answer_problem(row.get("result"), case, env)
    if problem is not None:
        raise CheckerUnavailable(f"CheckerUnavailable: Lean's words answer is not bound to its request: {problem}")
    return list(row["result"]["lines"])


def _model(data) -> dict:
    """The fields of a model a situation line reads: its domains, relations and constants, each as ids."""
    def plain(rows):
        return [list(row) for row in rows]
    return {"domains": {sort: list(ids) for sort, ids in (data.get("domains") or {}).items()},
            "relations": {p: plain(rows) for p, rows in (data.get("relations") or {}).items()},
            "constants": dict(data.get("constants") or {})}


def situation_item(data, facts, suppose=(), omit_sorts=()) -> dict:
    """A situation of the model `data` (its JSON): its elements by sort, named by their ids (without `omit_sorts`),
    the true rows of each predicate of `facts`, then the `suppose …` lines."""
    model = _model(data)
    model["domains"] = {sort: ids for sort, ids in model["domains"].items() if sort not in omit_sorts}
    return {"kind": "situation", "model": model, "facts": sorted(set(facts)), "suppose": list(suppose)}


def point_item(constants, predicate, values, value=True, *, kind="point") -> dict:
    """The clause (`kind="point"`) or filled-gap sentence (`kind="filling"`) of `predicate` at the element ids
    `values`, each named by the first constant of `constants` (name → element id) that denotes it."""
    return {"kind": kind, "constants": dict(constants or {}), "predicate": predicate,
            "tuple": [str(v) for v in values], "value": value}


def pair_item(required) -> dict:
    return {"kind": "pair", "required": required}


def situation(env, data, facts, suppose=(), omit_sorts=()) -> str:
    return lines(env, [situation_item(data, facts, suppose, omit_sorts)])[0]


def clause(env, constants, predicate, values, value=True) -> str:
    return lines(env, [point_item(constants, predicate, values, value)])[0]


def clauses(env, constants, points) -> list[str]:
    """The clauses of `(predicate, values, value)` points, in order, in one request."""
    return lines(env, [point_item(constants, p, vs, v) for p, vs, v in points])


def fillings(env, constants, points) -> list[tuple[str, str]]:
    """(clause, filled-gap sentence) of each `(predicate, values, value)` point, in order, in one request."""
    points = list(points)
    items = [point_item(constants, p, vs, True) for p, vs, _ in points]
    items += [point_item(constants, p, vs, v, kind="filling") for p, vs, v in points]
    found = lines(env, items)
    return list(zip(found[:len(points)], found[len(points):]))


def pair(env, required) -> str:
    return lines(env, [pair_item(required)])[0]


def constants_of(situation) -> dict:
    """A situation's constants (name → element id): a `FiniteModel`'s, a model JSON's, or an object with them."""
    found = situation.get("constants") if isinstance(situation, dict) else getattr(situation, "constants", None)
    return {str(name): str(element) for name, element in (found or {}).items()}
