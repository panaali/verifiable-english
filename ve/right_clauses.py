"""Python relay for the `right-clauses@0` profile (docs/spec/right-clauses.md 8.1, 10).

Lean's `clauses-elaborate` mode is the head of the profile (4.1): it decodes a rights document whose lines carry
clauses, a relation and `elided` spans, checks them in 4.1's order with section 7's texts, plains every structured line
(1.2) and returns the plained document's canonical bytes with the premise slot `Lim_{plain D} ++ Rel_D` (1.3). Python
decodes, checks and plains nothing (R8): it sends the document, and binds the answer to it. The service checks the
schema; `bind` checks that every unit, line and label the answer names is the request's, with no row missing or extra.
A rejection is Lean's text, raised as its class; an answer that does not bind is `CheckerUnavailable`, never a Python
verdict. The English of RC1 to RC5 is not shown here (cmp-s3-cfr-1d).
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import re

from .backends.lean_service import CheckerUnavailable

PROFILE = "right-clauses@0"
MODE = "clauses-elaborate"
_BODIES = ("right", "right_lines")
_ROLE = re.compile(r"(.+):(necessary|sufficient)", re.DOTALL)


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
    return bind(row["result"], document)


def _unbound(what: str) -> CheckerUnavailable:
    return CheckerUnavailable(f"CheckerUnavailable: Lean's {MODE} answer {what}")


def _bodies(units: list) -> list:
    """Each unit's (body key, its lines' rule names), `None` for a unit without a rights body."""
    out = []
    for unit in units:
        key = next((k for k in _BODIES if type(unit) is dict and type(unit.get(k)) is dict), None)
        lines = unit[key].get("lines") if key else None
        out.append(None if key is None or type(lines) is not list else
                   (key, [_rule(line) for line in lines]))
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
        for key in _BODIES:
            body = unit.get(key) if type(unit) is dict else None
            for line in (body.get("lines", []) if type(body) is dict and type(body.get("lines")) is list else []):
                relation = line.get("relation") if type(line) is dict else None
                if type(relation) is dict and relation.get("total") is not None:
                    out.append(_rule(line))
    return out


def _limitations(document: list) -> dict:
    """The request's limitation names, each with its conditions' names."""
    out = {}
    for unit in document:
        body = unit.get("limitation") if type(unit) is dict else None
        if type(body) is dict and type(body.get("name")) is str and type(body.get("conditions")) is list:
            out[body["name"]] = {c.get("name") for c in body["conditions"] if type(c) is dict}
    return out


def _limitation_bound(label: str, limitations: dict) -> bool:
    """`rights:limitation:<L>:<act>:<necessary|sufficient>:<c>` with `L` a request limitation and `c` its condition."""
    for name, conditions in limitations.items():
        head = f"rights:limitation:{name}:"
        for condition in conditions:
            tail = f":{condition}"
            if (type(condition) is str and label.startswith(head) and label.endswith(tail)
                    and len(label) > len(head) + len(tail) and _ROLE.fullmatch(label[len(head):-len(tail)])):
                return True
    return False


def bind(result: dict, document: list) -> Elaboration:
    """R8's binding of a schema-checked `clauses-elaborate` result to the request's document."""
    try:
        units = json.loads(result["plained"])
    except ValueError:
        raise _unbound("plained no JSON document") from None
    if type(units) is not list or type(document) is not list or len(units) != len(document):
        raise _unbound("plained other units than the request's")
    if _bodies(units) != _bodies(document):
        raise _unbound("plained other lines than the request's")
    rows = [(row["label"], row["ast"]) for row in result["clause_slot"]]
    relations = [label for label, _ in rows if label.startswith("rights:relation:")]
    if relations != [f"rights:relation:{rule}:total" for rule in _totals(document)]:
        raise _unbound("names other totality premises than the request's total relations")
    limitations = _limitations(document)
    for label, _ in rows:
        if not label.startswith("rights:relation:") and not _limitation_bound(label, limitations):
            raise _unbound(f"names a premise {label!r} of no limitation condition in the request")
    return Elaboration(result["plained"], tuple(rows))
