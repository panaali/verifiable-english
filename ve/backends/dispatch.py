"""The single owner of every dispatched operation (docs/LEAN-FIRST-PLAN.md, rules 1 to 4).

Lean decides every operation; Rust's search proposes witnesses that Lean checks (lean-first batch
15b). Since batch 18 there is no authority to select: the `python` authority, its shadow and the
`VE_AUTHORITY` and `VE_AUTHORITY_OVERRIDES` settings are gone, and an operation runs its one owner.
Inputs outside an operation's Lean scope (the stage-2c fallbacks of docs/lean-first/b13b/DELTA.md)
stay with the retained Python of that operation's own module, which no setting selects.
"""
from __future__ import annotations

from typing import Callable, TypeVar

T = TypeVar("T")
# Callables told (op, owner) on every dispatched call; the Gate 2 parity tool uses them to tell
# adapter-routed cells from Python-only ones.
observers: list[Callable[[str, str], None]] = []


# The operations Lean decides (lean-first batches 13b and 18). Differential harnesses must not
# compare a "Python" answer of these operations with Lean's own (`conformance.three_way`,
# `tools/difffuzz.py`): they compare it with recorded answers or with another engine's check instead.
LEAN_OWNED = frozenset({
    "typing", "parse", "label", "dependency_order", "definitions_elaboration", "background", "bundle",
    "norms_elaborate", "norms_certificate", "norms_conflict", "norms_admission", "admission", "graph",
    "readings", "premise_status", "compare", "certificate_replay",
    "evaluate", "countermodel_check", "model_validation"})
SINGLE_OWNER = {"countermodel_search": "rust", "distinguishing_model": "rust",
                **dict.fromkeys(sorted(LEAN_OWNED), "lean")}


def owned(op: str, run: Callable[[], T]) -> T:
    """Run the operation `op` (SINGLE_OWNER) by its owner: `run`. Observers see the owner. A
    Rust-owned search's witnesses are checked by Lean, as its constituents are."""
    if op not in SINGLE_OWNER:
        raise ValueError(f"{op} is not a dispatched operation")
    for observe in observers:
        observe(op, SINGLE_OWNER[op])
    return run()
