# RD-9 Lean progress report

Status: **in progress; not an RD-9 acceptance report**. This increment builds a part of SC-1. No soft-completion route is enabled by it. No model calls were made.

## Implemented

- `LayeredEntail.lean`: the exact SC-1 `premisesX`, `EntailsX`, conflict-certificate and finite-model statements, their soundness proofs, nil conservativity, and the shared `bindCertX` binder.
- `SoftDefaults.lean`: the soft document shape and per-document `X` definitions, the strict and norms-shaped nil theorems, `filledAuthorEnv`, and `WellFormedSD`.
- `Verdicts.lean`: `ChoiceSem`, `HoldsG`, `CoversG`, `RowsHoldG`, seven generic fold soundness proofs, `CounterX`, `ConsistentX`, `ndSem`, and `xSem`. RD-3's seven fold theorems retain their statements and now apply the generic proofs.
- The norms choice and verdict certificate callers use `bindCertX` with `X = []`. This does not alter their regenerated premise list or wire output.
- `UnspecifiedWire.lean` now states `fillRest`, `ndRest_eq_fillRest`, and `wellFormedSD_eq` with the spec's exact expressions.
- Generated axiom, statement, declaration, predicate, frozen-source and checker-pin inventories were refreshed. The assurance manifest's whole-file decoder pins and its generated document were updated for the two edited wire files. The source files under `VE/Norms`, `VE/SoftNorms`, and `VE/Route` were not edited.

## Outstanding work

- SC-1 still needs `softX_wellFormed`, the approved fixture module, and exact-statement checks for the later RD-9 batches. `check_rd9_sc1_statements.py` checks the 48 SC-1 declarations already built and reports the missing theorem explicitly.
- SC-A, SC-2, SC-3, SC-4, SC-5, and SC-6 are not implemented here; SC-8 and SC-9 are also not done. The plan's SC-0 bounded re-check and the item-specific DRI signature for the SC-6 theorem amendment are not recorded in this worktree.
- `tools/trust_map.py --check` classifies every new declaration and reports `S +56` and untied verdict-bearing `V +13`, for 69 added trusted lines. **Needs a DRI signature.** Standing ruling R6 does not cover this change because no Python or Rust decision path was deleted. No allowance was added to `docs/trust-baseline.json`.
- No user-visible wording, field, fault-order, verdict, or availability delta is enabled by this increment. Thus no standing ruling signs a user-visible delta yet. Future batches must record each delta and its ruling/test in this file.

## Verification to date

- `PATH=~/.elan/bin:$PATH lake build`: PASS, 890 jobs.
- `PATH=~/.elan/bin:$PATH python3 lean/audit.py --write` and the plain `python3 lean/audit.py`: PASS, 483 source files, 5,281 named theorems, standard axioms only.
- `tools/lean_statements.py` through `regen_generated.py`: 29 added theorem statements, 0 removed, 0 changed; 4,831 statements total. `tools/check_readings_defaults_statements.py`: existing RD-1, RD-2a, RD-3, RD-4a/b, RD-6a/b statements pass unchanged.
- `tools/check_rd9_sc1_statements.py`: 48 implemented SC-1 declarations match the approved text; `softX_wellFormed` remains unbuilt.
- `VE/Route/frozen.py`: PASS after regeneration; frozen source files unchanged.
- `tools/assurance_manifest.py --check` and the selected `tests/test_assurance_manifest.py`: PASS after reviewing and updating the two whole-file decoder pins.
- Selected tests (`select_tests.py --base $(git merge-base HEAD main) --run`): the first run selected 81 units and failed while generated inventories and `ve_service` pin were stale. It also could not write the test-map cache under the sandbox's read-only home cache. The pin and inventories have since been regenerated. A targeted rerun of selected norm-defaults and consolidation cases produced 23 pass and one classification failure; the classification failure passed after adding the new declarations to `tools/trust-classes.json`. A later pre-commit selection of 81 units found two stale assurance decoder pins; both were corrected. On commit `ed42c25d` the selector ran all 358 units: 357 passed, and `tests/test_readings_defaults_rd6b_report.py::test_trust_growth_is_rd6b_entry_and_listed_for_signature` failed because `docs/trust-baseline.json` still pins the approved base. This is intentionally left unsigned pending DRI review. The wire-gate corpus unit passed.
- Full release gate: **not run**. It is reserved for the committed final RD-9 HEAD, which this is not.

### Seeded bugs removed

Each temporary mutation was made in `LayeredEntail.lean`, `lake build VE.NormDefaults.LayeredEntail` exited 1, and the file was restored. The restored target builds successfully. The mutation logs were saved under `/tmp/rd9-mutant-*.log` during this run.

| Seed | Temporary bug | Failing Lean check |
|---|---|---|
| M1 | Omit `X` from `premisesX` | `acceptanceX` proof, line 38 |
| M2 | Omit `X` from the conflict certificate premises | `conflictFreeCheckX_sound` proof, line 83 |
| M3 | Replace `extraValid U X M F` with `true` | `modelCheckX_sound` proof, line 113 |

## Build checklist (current increment)

1. Not applicable yet: no diagnostic, limit, or decoder contract changed.
2. Not applicable yet: no three-language contract surface changed.
3. Not applicable: no text normalization changed.
4. Not applicable yet: the existing certificate decoder and binder are reused; no response schema changed.
5. Not applicable: no new JSON decoder or referenced-id lookup.
6. Not applicable yet: no public verdict route enabled.
7. Not applicable: no new public operation or deadline.
8. Not applicable: no kind or owner fold changed.
9. Not applicable: no English rendered or parsed.
10. Not applicable: no entry point changed.
11. Done: Lean compiler is the oracle for the new declarations; no language regex was added.
12. Not applicable: no ledger or state machine changed.
13. Done for this increment: three seeded mutations each failed a Lean proof check; all were removed.
14. Done for the new checker: it reads the spec and Lean source only. Selected tests use cache paths under `/tmp` in this sandbox. The first attempt without those paths failed before running tests.
15. Done for the binder change: existing full-envelope certificate binding is preserved with `X = []`; no identity field was added.
16. Done for the current declarations: audit, statement, declaration, predicate, frozen-source and checker-pin inventories regenerated, and both affected assurance decoder pins reviewed and updated.
17. Done for the implemented SC-1 declarations: the new checker compares all 48 against the approved text and lists the one unbuilt theorem. The later batches remain not done.
18. Not done: SC-1 acceptance fixtures have not been added, although SC-0's scratch stub contains computed fixture values.
19. Not applicable yet: no use-case formalisation changed.
20. Not done: this progress report's measurements are not backed by a saved-evidence report test.
21. Done for this report: implemented proofs/build are AGENT; SC-0 review and SC-6 amendment are HUMAN/DRI, deferred to the DRI; SC-9 source audit is EXTERNAL, deferred to SC-9.
22. Not done: final clean-HEAD gate awaits completion of RD-9; this increment has an open trust-budget failure. Disk space was checked (65 GB available).
23. Not done: no user-visible delta is enabled; the new trusted-line allowance needs a DRI signature before acceptance.
