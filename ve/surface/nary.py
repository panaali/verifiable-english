"""The nary@0 wire constructor and surface extension point.

The first two relation arities keep their historical constructors and bytes.
N-ary English is strict only until the W8 fidelity gate approves an authoring
hook; an explicit identity-bound template may be parsed and rendered now.
"""
import re

from .registry import SurfaceRecord, register
from ..ast import Atom, Var


def template_parts(value: str, arity: int) -> tuple[str, ...] | None:
    """Check ordered single-use slots and return literal text between them."""
    slots = re.findall(r"\{[^{}]*\}", value)
    if slots != ["{" + str(i) + "}" for i in range(arity)]:
        return None
    parts = tuple(re.split(r"\{[0-5]\}", value))
    if len(parts) != arity + 1 or any(not part.startswith(" ") for part in parts[1:-1]):
        return None
    if parts[0] and not re.fullmatch(r"(?:[a-z]+ )+", parts[0]):
        return None
    if not all(re.fullmatch(r"(?: [a-z]+)+ ?", part) for part in parts[1:-1]):
        return None
    if parts[-1] and not re.fullmatch(r"(?: [a-z]+)+", parts[-1]):
        return None
    # A sequence of colours or adjectives between slots names no relation or
    # argument role. Require an overt relational head in the first connector.
    first = parts[1].split()
    if not (set(first) & {"reports", "records", "has", "is", "at", "maps", "relates", "links"}
            or parts[0].startswith("the value of ")):
        return None
    return parts


def print_atom(printer, node, scope):
    return f"{node.predicate}(" + ", ".join(printer.term(t, scope) for t in node.terms) + ")"


def render_english(renderer, node, scope, _depth):
    return renderer.words.atom(node.predicate, [renderer.term(t, scope) for t in node.terms])


def render_fluent(renderer, node, scope):
    return renderer.words.atom(node.predicate, tuple(renderer.term(t, scope) for t in node.terms))


def map_free(node, replacement, depth):
    def term(value):
        if not isinstance(value, Var) or value.index < depth:
            return value
        result = replacement(value.index - depth)
        return Var(result.index + depth) if isinstance(result, Var) else result
    return Atom(node.predicate, tuple(term(value) for value in node.terms))


def predicates(node):
    return {node.predicate}, ()


def import_fol(raw, scope, path, _depth, _formula, term):
    from ..fol import _fail
    if set(raw) != {"op", "predicate", "terms"} or not isinstance(raw["terms"], list):
        _fail("invalid n-ary atom fields", path)
    if not 3 <= len(raw["terms"]) <= 6:
        _fail("n-ary atom requires three to six terms", path + "/terms")
    return Atom(raw["predicate"], tuple(term(item, scope, f"{path}/terms/{i}")
                                        for i, item in enumerate(raw["terms"])))


def export_fol(node, scope, _counter, _export_formula):
    return {"op": "atom", "predicate": node.predicate,
            "terms": [{"var": scope[value.index]} if isinstance(value, Var)
                      else {"const": value.name} for value in node.terms]}


register(SurfaceRecord("atom", "p(t1, ..., tk)", (), "atom", "atom",
                       node_type=Atom, wire_arity=3, printer_hook=print_atom,
                       english_renderer=render_english, fluent_hook=render_fluent,
                       traversal_hooks={"map_free": map_free, "predicates": predicates},
                       fol_import_hook=import_fol, fol_export_hook=export_fol,
                       profiles=("nary@0",)))
