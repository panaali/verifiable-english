# Test-speed batch B1

## Changes

- The v6 coverage map records assurance-manifest entry reads separately from import-time operation-presence checks. A changed entry selects its recorded readers and `test_assurance_manifest`; an added or removed operation also selects registration sites. A shared manifest change or missing map selects the full suite.
- Service response schemas compile a mode's row validator on first use.
- An added or removed Lean module invalidates the executables whose import closures contain it. An unreadable Lean import header still invalidates every executable.
- The nightly full suite and the release gate remain full-suite runs. Selection adds the smoke tests and all unmapped or opaque units.

## B1 gate evidence

The saved [shadow evidence](evidence/shadow.json) replays the selector over **10 fix rounds** (three consecutive non-merge commits per round, as in the research plan) against saved full-gate results. It records **3 full-suite test failures**, all in selected files, and zero outside selection. 9 rounds selected all 342 units; one selected 65. 5 rounds explicitly fell back to full selection. This gate checks safety, not a speed claim for those historical Lean-heavy rounds. The older coverage maps used for replay have no operation edges; a manifest change would fall back to the full suite.

The [v6 map](evidence/coverage-map.json.gz) recorded 342 units on B1 code. One unit, `test_difffuzz.py`, failed its CPU assertion under coverage recording and remains unmapped; the failed test passed in an isolated foreground rerun. The map records 29 distinct entry-read IDs and 25 presence-check IDs. Five seeded edits to existing manifest operations selected their saved entry readers and `test_assurance_manifest`:

| Edited operation | Selected units |
|---|---:|
| parse | 78/342 |
| typing | 229/342 |
| environment | 264/342 |
| model | 152/342 |
| evaluate | 90/342 |

The [manifest seed evidence](evidence/manifest-seeds.json) records 5 manifest edits, each selected file and every mapped reader. `tests/test_test_speed_b1_evidence.py` checks the saved map, the five edits, the ten saved full-gate outcomes, and the report numbers without consulting a moving Git diff. `tests/test_select_tests.py` covers shared manifest fallback, missing-map fallback, presence changes, direct reads, and Lean module presence. `tests/test_lean_service_schema.py::test_mode_rows_compile_only_when_used` checks a fresh process.

## Seeded bugs

The [mutant record](evidence/mutants.json) contains **6 seeded bugs** in changed Python product code. Each targeted test failed with the bug and passed after restoration:

| File | Seeded bug | Rejecting test |
|---|---|---|
| `tools/select_tests.py` | Drop changed-operation readers | `test_five_manifest_edits_select_their_readers[parse]` |
| `tools/select_tests.py` | Invalidate every executable for an added Lean module | `test_added_and_removed_lean_modules_select_only_importing_executables` |
| `ve/backends/service_schema.py` | Compile all mode rows on import | `test_mode_rows_compile_only_when_used` |
| `tools/select_tests.py` | Skip the missing-map full fallback | `test_automatic_selection_without_a_map_runs_full_suite` |
| `tools/test_map_recorder.py` | Record presence as an entry read | `test_recorder_tracks_manifest_operations_without_import_read` |
| `ve/assurance.py` | Register an operation as a full entry read | `test_semantic_registration_reads_only_presence` |

## Review and limits

No VE verdict, diagnostic, wire field, theorem statement, or accepted input changes. The CI selection behavior is the B1 change authorized by the DRI task instruction; no standing ruling for a product-visible delta is invoked. The remaining full-gate result is `gate-result.json` at the worktree root.

| Acceptance item | Owner | State |
|---|---|---|
| B1 implementation, saved five-edit gate, ten-round shadow replay, seeded bugs, full release gate | AGENT | Evidence and tests in this batch; release-gate result in `gate-result.json` |
| Independent review of the final diff and shadow limitations | HUMAN: DRI reviewer | Deferred to review |
| Nightly full-suite continuation | EXTERNAL: CI owner | Existing nightly job remains enabled; not run here |

Checklist applicability: the v6 map is validated before use (4); Lean imports use the repository import parser (11); the six mutants prove tests fail (13); recorder writes and cache paths are isolated (14); registered operation IDs are mapped and checked (16); this report is checked from saved evidence (20); owners are tagged above (21); the selected run and final-HEAD gate are required (22); the DRI ruling check above applies (23). Diagnostics, English, semantic verdicts, ledgers, and theorem statements are unchanged, so checklist items for those product surfaces do not apply to B1.
