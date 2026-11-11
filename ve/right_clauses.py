"""Python relay for the `right-clauses@0` profile (docs/spec/right-clauses.md 8.1, 10).

Lean's `clauses-elaborate` mode is the head of the profile (4.1): it decodes a rights document whose lines carry
clauses, a relation and `elided` spans, checks them in 4.1's order with section 7's texts, plains every structured line
(1.2) and returns the plained document's canonical bytes with the premise slot `Lim_{plain D} ++ Rel_D` (1.3). Python
decodes, checks and plains nothing (R8): it sends the document, and binds the answer to it. The service checks the
schema; `bind` checks that every unit, line and label the answer names is the request's (its docstring says what is
bound: the plained units and lines one for one, the totality rows exactly; how many `Lim` rows there are is Lean's).
A rejection is Lean's text, raised as its class; an answer that does not bind is `CheckerUnavailable`, never a Python
verdict. The English of RC1 to RC5 is not shown here (cmp-s3-cfr-1d).
"""
from __future__ import annotations

from dataclasses import dataclass
import json

from .backends.lean_service import CheckerUnavailable
from .backends.service_schema import same_json

PROFILE = "right-clauses@0"
MODE = "clauses-elaborate"
_BODIES = ("right", "right_lines")
_HEAD = ("elided", "clauses", "relation")
_RELATION = "rights:relation:"


@dataclass(frozen=True)
class Elaboration:
    """Lean's answer: the plained document's canonical bytes, as Lean wrote them, and the slot's (label, AST) rows."""
    plained: str
    clause_slot: tuple[tuple[str, object], ...]

    @property
    def units(self) -> list:
        return json.loads(self.plained)


def elaborate(environment: dict, document: list) -> Elaboration:
    """Lean's head on one document; a refusal raises Lean's diagnostic (`relay.decide`)."""
    from .backends.relay import decide
    [row] = decide(MODE, [{"id": "clauses", "environment": environment, "document": document}])
    return bind(row["result"], document, environment)


def _unbound(what: str) -> CheckerUnavailable:
    return CheckerUnavailable(f"CheckerUnavailable: Lean's {MODE} answer {what}")


def _lines(unit) -> tuple:
    """A unit's rights body key and its lines, as Wire.lean's `unitBody` picks them (`right` first); `None` lines when
    the unit has no such body or its lines are no array."""
    key = next((k for k in _BODIES if type(unit) is dict and k in unit), None)
    body = unit[key] if key else None
    lines = body.get("lines") if type(body) is dict else None
    return key, lines if type(lines) is list else None


def _with_lines(unit: dict, key: str, lines: list) -> dict:
    return {**unit, key: {**unit[key], "lines": lines}}


def _structured(line) -> bool:
    """A request line whose norm guard Lean rewrites: clauses or a relation (Wire.lean `plainLineJson`)."""
    clauses = line.get("clauses") if type(line) is dict else None
    return bool(type(clauses) is list and clauses) or (type(line) is dict and line.get("relation") is not None)


def _masked(line, structured: bool):
    """The line with its norm guard left out when it is Lean's (`elaborate_plain` ties it to the line's clauses)."""
    norm = line.get("norm") if type(line) is dict else None
    return {**line, "norm": {**norm, "guard": None}} if structured and type(norm) is dict and "guard" in norm else line


def _request_plained(document: list) -> list:
    """The request as Lean's plain writes it (Wire.lean `elaborateJson`), structured guards left out: each unit without
    `span`, each line of its rights body without the head's keys."""
    out = []
    for unit in document:
        unit = {k: v for k, v in unit.items() if k != "span"} if type(unit) is dict else unit
        key, lines = _lines(unit)
        if lines is not None:
            unit = _with_lines(unit, key, [_masked({k: v for k, v in line.items() if k not in _HEAD}, _structured(line))
                                           if type(line) is dict else line for line in lines])
        out.append(unit)
    return out


def _answer_plained(units: list, document: list) -> list:
    """Lean's plained units, the guards of the request's structured lines left out (nothing else is dropped)."""
    out = []
    for unit, asked in zip(units, document):
        key, lines = _lines(unit)
        asked_lines = _lines(asked)[1]
        if lines is not None and asked_lines is not None and len(lines) == len(asked_lines):
            unit = _with_lines(unit, key, [_masked(line, _structured(a)) for line, a in zip(lines, asked_lines)])
        out.append(unit)
    return out


def _rule(line) -> object:
    """A line object's rule name as written: its norm's, else its liberty's."""
    for key in ("norm", "liberty"):
        part = line.get(key) if type(line) is dict else None
        if type(part) is dict and "name" in part:
            return part["name"]
    return None


def _totals(document: list) -> list:
    """The request's rule names whose relation has `total` set, in document order."""
    out = []
    for unit in document:
        for line in _lines(unit)[1] or []:
            relation = line.get("relation") if type(line) is dict else None
            if type(relation) is dict and relation.get("total") is not None:
                out.append(_rule(line))
    return out


def _limitation_bound(label: str, document: list, environment) -> bool:
    """`rights:limitation:<L>:<act>:<role>:<c>`: `L` a request limitation, `act` a declared predicate, `c` one of `L`'s
    conditions with role `role` (as ve.rights_route binds the rights route's limitation premises)."""
    parts = label.split(":", 5)
    vocabulary = environment.get("vocabulary") if type(environment) is dict else None
    predicates = vocabulary.get("predicates") if type(vocabulary) is dict else None
    if len(parts) != 6 or parts[:2] != ["rights", "limitation"] or type(predicates) is not dict or \
            parts[3] not in predicates or parts[4] not in ("necessary", "sufficient"):
        return False
    for unit in document:
        body = unit.get("limitation") if type(unit) is dict else None
        if type(body) is dict and body.get("name") == parts[2] and type(body.get("conditions")) is list and any(
                type(c) is dict and c.get("name") == parts[5] and c.get("role") == parts[4] for c in body["conditions"]):
            return True
    return False


def bind(result: dict, document: list, environment: dict) -> Elaboration:
    """R8's binding of a schema-checked `clauses-elaborate` result to the request. The plained document is the
    request's, unit for unit and line for line, less what Lean's plain drops, but for the guards of structured lines.
    The slot is `Lim_{plain D} ++ Rel_D` (1.3): limitation premises first, each naming a request limitation, one of
    its conditions with its role and a declared act; then one totality premise per total relation of the request, in
    its order. Which lines a limitation scopes is Lean's (rights' scope), so how many `Lim` rows there are, and
    whether a label repeats (cmp-s3's `cxDoc`, reviews/dri-decisions-20261104-cmp-s3.md Q3), is not bound here."""
    try:
        units = json.loads(result["plained"])
    except (ValueError, RecursionError):
        raise _unbound("plained no JSON document") from None
    if type(units) is not list or type(document) is not list or len(units) != len(document) or \
            not same_json(_answer_plained(units, document), _request_plained(document)):
        raise _unbound("plained another document than the request's")
    rows = [(row["label"], row["ast"]) for row in result["clause_slot"]]
    first = next((i for i, (label, _) in enumerate(rows) if label.startswith(_RELATION)), len(rows))
    if [label for label, _ in rows[first:]] != [f"{_RELATION}{rule}:total" for rule in _totals(document)]:
        raise _unbound("names other totality premises than the request's total relations, or not last")
    for label, _ in rows[:first]:
        if not _limitation_bound(label, document, environment):
            raise _unbound(f"names a premise {label!r} of no limitation condition in the request")
    return Elaboration(result["plained"], tuple(rows))
