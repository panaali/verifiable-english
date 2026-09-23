"""Missing-premise suggestions for an unproved step. OFF by default.

Suggestions are the most dangerous feature (they can assume the gap away), so
they are a separate, explicitly enabled session option, every suggestion is
labelled with its risk, and a node built from one is logged as
``suggestion-verbatim`` / ``suggestion-edited``.

Two deterministic kinds, no model calls:

* ``use_existing_node``: an existing node that, added as a parent, makes the
  step follow (checked by the prover). No new content is assumed.
* ``bridge``: the implication from the parents to the conclusion. It always
  closes the gap and is exactly "assuming the step"; unless a given sentence
  states it, it is an unanchored, load-bearing assumption and fails the item.
"""
from __future__ import annotations

from .. import ast

MAX_SUGGESTIONS = 5


def _conjunction(formulas):
    result = formulas[-1]
    for formula in reversed(formulas[:-1]):
        result = ast.And(formula, result)
    return result


def suggest_premises(session, node):
    parents = [session.nodes[p].formula for p in node.parents]
    below = session._descendants(node.name) | {node.name}
    rows = []
    for other in session.nodes.values():
        if other.name in below or other.name in node.parents:
            continue
        if session._entails([*parents, other.formula], node.formula):
            rows.append({"kind": "use_existing_node", "node": other.name, "formula": other.formula,
                         "anchor_state": session._anchor_state(other) if other.kind == "assumption" else "derived",
                         "action": f"rewrite {node.name} with parents {[*node.parents, other.name]}",
                         "risk": "none beyond the existing node's own anchoring"})
        if len(rows) >= MAX_SUGGESTIONS - 1:
            break
    bridge = ast.Implies(_conjunction(parents), node.formula) if parents else node.formula
    rows.append({"kind": "bridge", "formula": bridge,
                 "risk": "assumes the step itself; unanchored and load-bearing unless a given sentence states it"})
    return rows
