# eff-20261011-1: trust baseline merge

## Result

`regen_generated.py --resolve` now combines concurrent `docs/trust-baseline.json` file counts as `base + (ours - base) + (theirs - base)`, treating an absent base count as zero. It still refuses a deleted module or count changed by the other side. `totals` and `budget` are recomputed from the merged `files` by `trust_map.totals` and `trust_map.budget`; the other ledger fields retain the structural JSON merge. The trust-table check remains in the `--resolve` check list and still refuses measured growth beyond the merged baseline plus signed allowances. The tool neither calls `write_baseline` nor adds a rebaseline reason.

The decoder-total calculation is pure during a merge. Importing `assurance_manifest` at that point read an unresolved manifest from disk in two historical replays; the calculation now uses the same range formula without loading that file.

**Delta:** Automatic resolution of concurrent trust-count changes is **SIGNED by standing ruling R11 (DRI-RULINGS.md), decision D3**: the budget is the sum of both sides' changes to measured file rows and cannot absorb later measured growth. Evidence: `tests/test_regen_generated.py::test_trust_merge_adds_file_deltas_and_recomputes_both_derived_values`, `::test_trust_merge_refuses_delete_versus_change`, and `::test_resolve_fails_when_measured_tree_exceeds_merged_trust_budget`. No trusted Lean line or approved theorem changes in this batch; R6 needs no allowance.

## Historical replay

The three requested two-parent merges were replayed in scratch clones with the current trust merge. Each merged budget equals the agent's committed budget, and `trust_map.check` accepts the committed historical file ledger against it. `--resolve --only trust-tables` and its trust check passed for all three. For `17573bbb` and `fc106062`, other generated conflicts were first filled with the respective committed merge's generated output, so this run isolates the trust ledger and check. `6aafef85` passed directly. The full regeneration of every historical generated file was not run. The [initial targeted attempts](evidence/replay-initial-targeted.json) failed on stale generated declarations or on the conflicted assurance-manifest import; those conditions were removed in the successful isolated replays. [Budget evidence](evidence/replay-budgets.json), [scratch outcomes](evidence/replay-trust-check.json), [direct 6aafef85 outcome](evidence/replay-targeted-after-fix.json).

| Merge | Before | After | Remaining stop |
|---|---|---|---|
| `17573bbb` | Trust `$.totals.D` | Resolved | — |
| `6aafef85` | Trust `$.totals.D` | Resolved | — |
| `fc106062` | Trust `$.totals.S` | Resolved | — |
| `ef243d37` | Resolved | Resolved | — |
| `b8118aa7` | Resolved | Resolved | — |
| `372652cf` | Resolved | Resolved | — |
| `e41d104f` | Resolved | Resolved | — |
| `b4653fc8` | Resolved | Resolved | — |
| `68f5bd07` | Resolved | Resolved | — |
| `27655d64` | Resolved | Resolved | — |
| `1a221d54` | Source conflict | Source conflict | `docs/ARCHITECTURE-LAYERS.md`, `ve/document.py` |
| `099dae2e` | Source conflict | Source conflict | `tools/relay_lint.py` |
| `b12e7c90` | Source conflict | Source conflict | `lean/ResponseShape/Schemas/ReadingsRoute.lean`, `tests/test_difffuzz.py`, `tools/check_readings_defaults_statements.py` |
| Daily-count retry A | Reported generated-only | Not independently replayed | No distinct two-parent commit or parent IDs in the available record |
| Daily-count retry B | Reported source conflict | Not independently replayed | No distinct two-parent commit or conflicting path list in the available record |

The daily review counts 15 conflicted sync attempts (8 previously resolvable, 3 trust-only, 4 source). The available two-parent merge history reconstructs 13 distinct conflicted pairs (7, 3, 3). The two extra rows reconcile the daily aggregate but are **not** claimed as replays. The 13 reproducible classifications, parent IDs, paths, and error text are saved in [replay-classification.json](evidence/replay-classification.json).

For `17573bbb`, the merged budget is **K 997, S 9791, V 36969**. The other merged budgets are **K 997, S 9788, V 37087** (`6aafef85`) and **K 997, S 9974, V 37363** (`fc106062`). These are recomputed from the saved file ledgers, not copied into a permanent report test.

## Tests and seeded bugs

The fixture test uses file rows cut from the base, parents, and committed results of the three named merges. It checks the additive row, both derived objects, and the committed result. Other tests check equal concurrent additions with a missing base row, deleted module and count conflicts, unchanged structural treatment of `signed`/`history`/`section11`/`comment`, and rejection when the measured tree exceeds the merged budget. The merge-tooling test file passed **31 tests** with pytest's native setup omitted during iteration and also passed in the selected run.

The required selected-test command ran all 363 units. It reported four nonpassing files: `test_select_tests.py` found the new top-level evidence directory; that directory was moved under `docs/` in commit `888ea166`, and its focused test passed on that commit. `test_lean_conformance.py` timed out in its audit subprocess under the concurrent run; the failed audit test passed serially in 1668 seconds. `test_english_evidence.py` and `test_wire_gate_corpus.py` reached the selector's 3600-second per-file timeout. English evidence passed all 67 tests serially in 6022 seconds. A serial wire-gate corpus rerun reached an error in its first recorded-input fixture after roughly one hour; the nested recorder itself has a 3600-second timeout, and the remaining file run was stopped after that error. The selector also failed while writing its test map to the sandbox's read-only default home cache; subsequent focused runs used `VE_TESTMAP_CACHE` under `/tmp`. Host load was above 130 during these runs. The [selected-run evidence](evidence/selected-run.json) records commands and outcomes. The full release gate result is reported separately.

An initial full-gate attempt on `f3464040` passed toolchain checks, the 886-job Lean build, the Lean audit (481 source files and 5252 declarations), Rust build and tests, and Python collection (14491 active tests). It was stopped during pytest after the load-aware `-n auto` selected one worker under host load above 150 and made too little progress for a practical gate run. This produced no completed pytest result. The final gate invocation uses `--workers 8` on a new committed HEAD; this changes scheduling only, retaining the same test collection and checks.

Three temporary seeded bugs in the changed Python product file were each caught by `tests/test_regen_generated.py::test_trust_merge_adds_file_deltas_and_recomputes_both_derived_values` and then removed:

| Seeded bug in `tools/regen_generated.py` | Failing behavior |
|---|---|
| Keep our budget unchanged | All three historical fixture cases failed |
| Skip totals recomputation | All three historical fixture cases failed |
| Take their count instead of adding both deltas | `fc106062` failed |

The exact failures are saved in [mutants.json](evidence/mutants.json). Only Python product code changed, so no Lean or Rust seeded bug applies.

## Acceptance and scope

- **AGENT:** JSON merge rule, derived totals and budget, refusal of delete-versus-change and growth beyond allowance, scratch replay, seeded bugs, selected tests, and the final full gate.
- **HUMAN:** Independent review after the pre-review gate. Owner: DRI/reviewer.
- **EXTERNAL:** None.

The final full gate writes `gate-result.json` at the repository root on the committed code. The [selection plan](evidence/selection-plan.json) records the exact selected units; the selector chose all 363 test units for this change. No relay-answer schema, Lean theorem, Rust product code, document verdict, or checker limit changed, so checklist items for those surfaces do not apply. The generated-file registry and layer checks remain in the release gate.

Self-review used the pinned main commit `8cec935a` and `git diff main...HEAD`: the product diff is confined to JSON merge and derived-value handling, the trust checker command is unchanged, and `git diff --check` is clean. The 15-attempt history gap is disclosed above rather than counted as a verified replay.
