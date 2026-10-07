# Readings-defaults integration: fix report

## Landed locally

- `28689222` merged `readings-defaults/py`. The relay lint conflict keeps both the existing imported-helper closure and the new reserved-completion-name rule; the test list keeps both branches' tests.
- `90ca9564` merged `readings-defaults/lean`. The frozen inventory, declaration dump, and gate collection were regenerated from the merged source and compiled environment.
- No branch was pushed. No model was called.

The merged source builds (`lake build`, 784 jobs). `python3 lean/audit.py` passed: only `propext`, `Classical.choice`, and `Quot.sound` occur. The RD-1 statement checker reports nine exact statements and one pending review. The targeted merged tests passed. The full clean-tree gate on `90ca9564` passed; its machine-readable result is `gate-code.json`. The gate result is evidence of the current implemented surface, not evidence that RD-2 through RD-5 exist.

## Seeded bugs, planted and removed

Each temporary mutation was made in the merged `tools/relay_lint.py`, run against its targeted test, and restored before the clean-tree gate:

| Bug | Test evidence |
|---|---|
| Empty the reserved prefix list, allowing completion names in readings modules | `test_seeded_readings_modules`: 6 failed |
| Skip the imported-helper closure, letting a relayed check escape lint by moving modules | `test_a_check_moved_into_its_own_module_is_still_linted`: 1 failed |
| Ignore the `non-wording` marker and reject legitimate guard literals | `test_seeded_readings_modules`: 1 failed |

## Open work and acceptance

- **EXTERNAL, orchestrator and reviewers Astra/Fable:** the approved `attached_fillDoc` statement is false without `singlyAttached`. The Lean theorem uses that extra hypothesis; the statement checker preserves this as pending. The existing RD-1 report gives the checked counterexample. A changed approved statement needs re-review.
- **HUMAN, DRI:** sign the A4 `<reading>` wording change described in the Python report.
- **AGENT, not done:** RD-2a admission, separation, and per-choice completion wire; RD-2b relay and generators; RD-3 Lean verdict fold and English plan with deletion of the Python fold; RD-4a/b companion split and product; RD-5 pilot migration and measurement. The spec's F-ND service fixtures, end-to-end checks, and three-way conformance have not run because these paths do not exist yet. The current gate tests the merged RD-1 and preparatory Python work only.

## Build checklist on the integrated scope

`Done` records evidence present in this merge. `Not done` identifies an applicable check that cannot be claimed yet. `Not applicable` means no corresponding surface changed in the landed code.

| Line | Status | Evidence or reason |
|---|---|---|
| 1. Shared diagnostic contract | Not applicable | No new cross-language diagnostic table landed. RD-2 admission remains open. |
| 2. Three-way differential fuzz | Not done | The F-ND wire and service path is not implemented; there is no three-way run on its fixtures. |
| 3. Shared text normalization | Not applicable | No text parser or normalization path changed. |
| 4. Validate untrusted output | Not done | The decided-share helper validates its input, but the new Lean response producer and relay do not exist. |
| 5. Malformed input and ID resolution | Not done | The helper's malformed-input tests pass; F-ND route inputs and references have not been exercised. |
| 6. Three-valued verdicts | Not done | The completion verdict operation has not landed. |
| 7. Whole-operation budgets | Not done | The new public operations and their budget tests have not landed. |
| 8. Exhaustive kind/owner folds | Not done | RD-3's fold remains in Python. |
| 9. English derivation | Not done | New sentences pass the unique-derivation tests, but no F-ND answer displays them yet. |
| 10. One admission path | Not done | The completion entry points and metamorphic test have not landed. |
| 11. Parse real languages with a compiler | Not done | The reserved-name lint uses Python's AST, but the RD-1 statement checker still compares Lean text with regular expressions. |
| 12. State-machine ledger | Not applicable | No state machine or ledger changed. |
| 13. Seeded mutants and actual three-way tests | Not done | Three temporary bugs above failed tests; actual F-ND three-way tests remain absent. |
| 14. Hermetic tests | Done | The new tests use temporary paths; the full gate ran with its isolated environment and clean worktree. |
| 15. Identity mutations | Not applicable | No identity schema field changed in the landed batches. |
| 16. Generated and complete lists | Done | Frozen hashes, Lean declarations, and gate collection were regenerated; lint glob coverage is tested. |
| 17. Approved statement diff | Not done | The checker passed nine exact statements; `attached_fillDoc` awaits re-approval. |
| 18. Spec-stage theorem fixtures | Done for RD-1 | Lean fixture guards built, including the counterexample and iff boundaries; later batches have not started. |
| 19. Use-case formalisation | Not done | RD-5's pilot and answer-key mutants have not been built. |
| 20. Reports from gate JSON | Not done | The machine-readable gate result is included, but report-number regeneration by a test has not been added. |
| 21. Acceptance owners | Done | This report and the worker reports tag the DRI item HUMAN and the statement review EXTERNAL with owners. |
| 22. Commit, clean gate, disk, report | Done for code merge | Both merges were committed, `gate-code.json` is a clean-tree passing run on the code commit, disk had 63 GB free, and this report is non-empty. A final gate on the report commit is recorded separately. |
