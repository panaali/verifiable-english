"""The nary@0 wire constructor and surface extension point.

The first two relation arities keep their historical constructors and bytes.
"""
from .registry import SurfaceRecord, register
from ..ast import Atom


def print_atom(printer, node, scope):
    return f"{node.predicate}(" + ", ".join(printer.term(t, scope) for t in node.terms) + ")"


register(SurfaceRecord("atom", "p(t1, ..., tk)", (), "atom", "atom",
                       node_type=Atom, wire_arity=3, printer_hook=print_atom,
                       profiles=("nary@0",)))
