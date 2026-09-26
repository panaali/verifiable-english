# W4 Fable review follow-up

Verified on `expand/w4-nary` after the Astra fixes (`66b3261`) on
2026-09-26. This record supersedes the earlier 16-commit worker summary.

| Finding | Disposition | Commit |
|---|---|---|
| B1: stale gate documentation, unrecorded P0 ownership change, and unverified final state | Corrected `lean/METATHEORY.md` and the gate comment in `ve/profiles.py`; recorded the P0-owned dispatch and fixture edits beside the ownership matrix in `PLAN-EXPAND2.md`; reran the checks below. | `19d3084` |
| B2: FOLIO acceptance item (5) | Still open. The pinned corpus contains 216 n-ary sentence pairs, of which 189 unchanged gold formulas parse directly. The other 27 have 10 syntax errors, 11 free variables, 5 predicate arity collisions, and 1 shadowed variable. `e8bb2dd` pins every failing ID and category. A reviewed correction policy or an explicit change to the counting rule is needed before claiming 216/216; repaired gold must be counted separately from direct unchanged-gold parses. | `e8bb2dd` (failure regression, before this review) |

Validation on this branch:

- `PATH=/home/seyran/.elan/bin:$PATH lake build`: passed, 171 jobs.
- `PATH=/home/seyran/.elan/bin:$PATH python3 lean/audit.py`: passed, 91 Lean source files and 495 named theorem declarations, with only the declared standard axiom allowlist.
- `python3 lean/VE/Route/frozen.py`: passed; frozen Lean sources and existing `Main.lean` subcommands unchanged.
- `CARGO_HOME=/tmp/ve-w4-fable-cargo cargo test --workspace` from `rust/`: passed.
- `UV_CACHE_DIR=/tmp/ve-uv-cache uv run --frozen python -m pytest -q`: 1,724 passed, 4 skipped, 1 live test deselected. No model calls were made.
- `conformance.nary_folio.report()`: 189/216 direct parses; frozen 30-item sample 28/30 direct fit.
