"""S2a's verdicts across readings (docs/spec/composition-s2.md 4.5, 4.6, 5, 6, 8.6).

Python's prover and model search are untrusted generators. On the superposed route every certificate and model they
find on `sup D` is checked by Lean's readings route (`readings-conflict`, `readings-certificate`, `readings-model`,
`readings-dead`) before a verdict is reported; on the enumerated route each compatible choice's own document is checked
as an ordinary document of the lower route through `readings-choice`, on the document Lean regenerates for the
choice: its conflict status, every certificate (the chain's certificate kind) and every model (`choice-model`). A Lean
refusal of evidence that Python's own check accepted is `CheckerUnavailable`, never a verdict; an exhausted search
budget is UNKNOWN, which asserts nothing, and an absence that cannot be certified is reported as not computed.
Nothing here is computed for W2's, the pending or the abstaining route (1.1).

The package (architecture plan AR-16b, which split `ve/readings_verdicts.py` along its call graph; each module imports
only the ones before it):

- `route`: the search budget, what every route shares (`_Route`), the pending route and a query's request key;
- `binding`: the binding of a `readings-verdicts` answer to its request (`_Frame`, `_check_answer`,
  `_check_sup_answer` and their helpers);
- `choice`: a compatible choice's own document (`_ChoiceDocument`, `_FilledView`, `_FilledChoiceDocument`);
- `superposed`: the superposed route, and the dead readings' certificates both routes send;
- `enumerated`: the enumerated route.

This `__init__` picks a document's route (`context`). The other names below are those callers import from
`ve.readings_verdicts`. A test that patches a name patches it in the module that looks it up (for example
`ve.readings_verdicts.superposed._ChoiceDocument`), not here.
"""
from __future__ import annotations

from .binding import (INVALID_ANSWER, PAIR_LABEL, ROW_PIECES, SHOWN_IN, _check_answer, _check_english,
                      _check_sup_answer, _Frame, _need, _shown_of, dead_finding, relayed)
from .choice import _ChoiceDocument, _FilledChoiceDocument, _FilledView
from .enumerated import Enumerated
from .route import BUDGET, PENDING, Pending
from .superposed import Superposed, _dead_certificates, _public_sup_conflict


def context(doc):
    """The verdict context of a loaded document with a content-bearing set, by its route; None on W2's route. A
    document whose readings carry their own vocabulary is the product of its cases (readings-defaults RD-4b)."""
    if doc.get("readings_components") is not None:
        from ..readings_components import context as components_context
        return components_context(doc)
    if "_readings_s2_context" not in doc:
        row = doc.get("readings_s2")
        route = row["route"] if row is not None else None
        doc["_readings_s2_context"] = (Superposed(doc) if route == "superposed" else
                                       Enumerated(doc) if route == "enumerated" else
                                       Pending(doc) if route in ("pending", "abstention") else None)
    return doc["_readings_s2_context"]


__all__ = ["BUDGET", "Enumerated", "PENDING", "Pending", "Superposed", "context"]
