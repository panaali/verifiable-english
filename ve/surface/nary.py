"""The nary@0 wire constructor and surface extension point.

The first two relation arities keep their historical constructors and bytes.
N-ary English is strict only until the W8 fidelity gate approves an authoring
hook; an explicit identity-bound template may be parsed and rendered now.
"""
import re

from .registry import SurfaceRecord, register
from ..ast import Atom


def template_parts(value: str, arity: int) -> tuple[str, ...] | None:
    """Check ordered single-use slots and return literal text between them."""
    slots = re.findall(r"\{[^{}]*\}", value)
    if slots != ["{" + str(i) + "}" for i in range(arity)]:
        return None
    parts = tuple(re.split(r"\{[0-5]\}", value))
    if len(parts) != arity + 1 or parts[0] or any(not part.startswith(" ") for part in parts[1:-1]):
        return None
    if not all(re.fullmatch(r"(?: [a-z]+)+ ?", part) for part in parts[1:-1]):
        return None
    if parts[-1] and not re.fullmatch(r"(?: [a-z]+)+", parts[-1]):
        return None
    return parts


def print_atom(printer, node, scope):
    return f"{node.predicate}(" + ", ".join(printer.term(t, scope) for t in node.terms) + ")"


def render_english(renderer, node, scope, _depth):
    return renderer.words.atom(node.predicate, [renderer.term(t, scope) for t in node.terms])


def render_fluent(renderer, node, scope):
    return renderer.words.atom(node.predicate, tuple(renderer.term(t, scope) for t in node.terms))


register(SurfaceRecord("atom", "p(t1, ..., tk)", (), "atom", "atom",
                       node_type=Atom, wire_arity=3, printer_hook=print_atom,
                       english_renderer=render_english, fluent_hook=render_fluent,
                       profiles=("nary@0",)))
