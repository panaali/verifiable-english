"""The wording change of Lean-first batch 0 (docs/lean-first/b0/DELTA.md, wording list W1).

`ve/backends/relay.py` shows Lean's diagnostic text verbatim. Until batch 0 the client
stripped Lean's `Class:` prefix where Python's own checker writes the text without it, so
the two read alike; that stripping is deleted. The tests that compare Python's retained
checkers with Lean (deleted with them, batches 12 and 13b) compare Python's diagnostic
with Lean's through `lean_wording`, the one statement of that change.
"""
from __future__ import annotations

# Codes whose texts Python's checkers write without the code; Lean writes `Code: text`.
UNPREFIXED = frozenset({"UnknownSymbol", "TypeMismatch", "UnboundVariable", "UnsupportedProfile"})
# `_Checker`'s budget messages (ve/ast.py), which Python writes without `ResourceLimit:`.
UNPREFIXED_LIMITS = frozenset({"AST exceeds 10,000 nodes", "Formula exceeds 64 nesting levels",
                               "Arithmetic term exceeds 64 nesting levels"})


def lean_wording(code: str, text: str) -> tuple[str, str]:
    """Lean's `(code, text)` for Python's diagnostic `(code, text)`."""
    if code in UNPREFIXED or (code == "ResourceLimit" and text in UNPREFIXED_LIMITS):
        return code, f"{code}: {text}"
    return code, text
