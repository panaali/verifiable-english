"""The nary@0 wire constructor and surface extension point.

The first two relation arities keep their historical constructors and bytes.
"""
from .registry import SurfaceRecord, register
from ..ast import Atom


register(SurfaceRecord("atom", "p(t1, ..., tk)", (), "atom", "atom",
                       node_type=Atom, wire_arity=3, profiles=("nary@0",)))
