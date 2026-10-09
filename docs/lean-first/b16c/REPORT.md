# Batch 16c progress report

The branch contains a tested JSON-null and response-binding increment. It does not
complete the requested document-mode migration. See [DELTA.md](DELTA.md) for the
captured scope, corpus shares, per-case residue ledger and unmet targets.

The three planted faults and failing test excerpts are in `evidence/mutants.json`:

1. Treating `content: null` as present made `test_null_content_is_absent_on_the_lean_path` fail.
2. Accepting a forged alternate checked formula made `test_identities_and_content_are_leans` fail.
3. Accepting an untyped checked formula made `test_document_schema_types_checked_content` fail.

The source was restored after each run. The document-focused suite passed at the
code commit (`332 passed, 83 xfailed`). The full clean-worktree gate passed at
`f0c44d43` with 13,362 passed, 92 allowed skips, zero failures, and 36 Rust
tests passed; its result is saved in `evidence/gate.json`. The nine-corpus A/B
and the profile composition required for Python wrapper deletion remain open.
