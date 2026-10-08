# Lean first batch 16a: document wrapper evidence

**Status: incomplete.** The new Lean `document` service mode handles front matter, byte partitioned units, MIXED provenance, base unit status inference, and base coverage and residual counts. It fails closed on nonempty reading sets and profile specific coverage. Batch 16a's full Lean wrapper is therefore not ready for the 16b Python switch. The 16a plan lists no Python deletion; the one changed Python line registers the service mode, and no Python semantic duplicate was removed.

## Saved source scope

Range: `main..HEAD --no-merges`, captured at code HEAD `2c2a1b31a7aec4bbb508473086c88668de2e24e1` while `main` was `acee4ede1c932537e9f0057a906c6f1ac1dc041f`. The branch's original A/B base is `29773091b436c14653fb21099152ecff4403476c`. Main advanced afterward; all numbers below read this saved scope rather than a moving ref.

Source commits (saved): 2c2a1b31a7aec4bbb508473086c88668de2e24e1, 9da901f5450ba05b101ec99f9ab7302ce50c7c63, 2b5407b72d0409dd8c22f71ac23f96db9b1b83c0, 8d549d54082060c23eecf0be368ec9b33a2207ad, 8b18d28621f19c5bfc09df4bc6af966625c7fd65

- Total lines deleted: 255
- Lean lines added: 280
- Python lines deleted: 1 (service mode registration replacement; zero semantic duplicate lines)

These are cumulative per commit numstat counts, including generated schema, assurance, declaration and trust files. They are not a net diff and do not imply 255 lines of duplicate logic were removed.

## Gate evidence

- Full gate: passed; 11845 passed, 7 skipped; commit `2c2a1b31a7aec4bbb508473086c88668de2e24e1`, clean worktree, 0 failed. Rust: 37 passed.
- A/B identical: 94498 public outcomes across probe, conformance, readings, discourse, rights, quantity and pilots; zero differences and zero unlisted cases. Pilots identical: 303 documents. No DELTA or DRI signature is needed for these unchanged public outcomes.
- CI baseline: 352 entries, 0 new signatures; all baseline entries replayed, no unreviewed findings.
- Date seeds: 14 paired; 550 inherited signatures; 0 head-only. The 13 non-CI dates fail the absolute committed baseline, but each signature set is identical at the pinned base and head. This batch grows the baseline by zero; the inherited gaps remain a separate baseline triage item for the DRI.
- `tools/lean_statements.py`: 0 statements added, removed or changed. `lake build` and Lean audit passed inside the full gate.

## Failure sensitivity

Seeded mutants: 3 failed as expected. Each changed the Lean file, built `ve_service`, failed its targeted test, was removed, and the original source hash and build were restored:

- `span_partition`: removing the terminal byte partition check failed `test_gap_and_wrong_status_are_rejected`.
- `mixed_provenance`: dropping the MIXED parent id failed `test_mixed_parent_counts_parts_once`.
- `status_inference`: forcing CHECKED failed `test_utf8_partition_status_and_counts`.

## Ownership and remaining work

The mode calls the existing Lean `VE.Discourse.Loader` for front matter, MIXED partitioning, meaning status and identities, and the existing Lean standalone environment and formula checkers for accepted cases. Its numeric response maps are closed to natural values in the generated client schema. The structural behavior is exercised by `tests/test_lean_document_wrapper.py`; the five `tests/test_b16a_evidence.py` checks read only the saved evidence files and report.

**AGENT completed:** structural mode, response schema and decoder inventory, clean gate, public A/B, CI and date seed differential checks, and three restored seeded failures. **AGENT unfinished:** Lean reading set composition, profile specific coverage and residual lines, status folds over nested statement layers, comprehensive malformed response and budget/deadline injection checks. **HUMAN deferred (DRI):** triage the 550 inherited date seed signatures and approve any future public deltas; no public delta was observed here. **EXTERNAL:** none.

The work is kept within the 16a Lean side: Python document check and display remain unchanged, as scheduled for 16b. Because the missing Lean branches are required by 16a, this report does not claim batch completion or authorize the 16b switch.
