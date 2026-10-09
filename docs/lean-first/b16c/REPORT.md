# Batch 16c progress report

The branch contains a tested JSON-null and response-binding increment. It does not
complete the requested document-mode migration. See [DELTA.md](DELTA.md) for the
captured scope, corpus shares, per-case residue ledger and unmet targets.

The 16c review's findings are fixed. B1: the response schema typed relayed narrowings as
tokens. B2: Lean's JSON reader decided `null` and number forms differently from Python.
B3: unit `kind`, `meaning`, `status` and `support` were untyped. See DELTA.md, "Boundary
and binding change". The ten planted faults and their failing test excerpts are in
`evidence/mutants.json`; `seed_faults.py` regenerates them.

The source was restored after each run. The saved clean-worktree gate in
`evidence/gate.json` is the run at `f0c44d43`: 13,362 passed, 92 allowed skips, zero
failures, and 36 Rust tests passed. No saved gate result exists for `86eed2e8`; that
commit changed only these documents. The 16c review records that its first gate run had
three failures, apparently SIGTERM flakes, which passed on rerun. The review fixes were checked with the full suite in the working tree,
not with a saved clean-worktree gate; the corpus shares in DELTA.md are still the
`f0c44d43` measurement. The nine-corpus A/B
and the profile composition required for Python wrapper deletion remain open.
