# en-sw build report

Status: F1 fixed in the Lean catalogue; selected tests have one unrelated safety-framework evidence failure; the chain owns the final release gate.
Built code: this branch's final committed HEAD. No product rows or verdict changes.
Open external action: the R16 ties-pass row for `/home/seyran/code/manage-agents/FOLLOW-UPS.md` could not be written because the sandbox rejects writes outside this worktree.
DRI signature needed: none. Pilot bytes expected from en-sw alone: 0.

## Statement and scope

The statement gate is the signed C1 decision in `reviews/dri-decisions-20261028-catalogue-owner.md` item 1. The owner is `english-lean`; `Catalogue.lean` remains the nonterminal table. SYNTHESIS O15/C22 and phase-2 X9/ET2 assign source-word rows to this module. Item 2 leaves consumer rows to ET-5, QT-A6, ME-11, AT-5, WG-4, SC-7, DF-4, and JT-3. Item 5 bars a new shared budget; this item adds none.

| en-sw requirement | Delivery | Check |
|---|---|---|
| Row type with `word`, `frame`, `profile`, `owner`, and `readings`/`refuse`/`fixed` kinds | `lean/VE/EnglishGrammar/SourceWords.lean` (`ab2a7fb57`) | `test_lean_boundary_fixtures` |
| Unique contextual keys; distinct normalized readings and nonempty situations; complete refusal fields and normalized substring-free rewrite | Lean `sourceWordsValid`, `SourceWordRow.validKind`, `sourceWordNormal` | `test_lean_boundary_fixtures`; `SourceWordsExamples.lean` guards |
| Empty product table; examples only in a fixture | `sourceWords := []`, `SourceWordsExamples.lean` (`ab2a7fb57`) | `test_generated_json_equals_lean_table` |
| Generated JSON and LOCK entry, one Python loader | `tools/english_grammar_gen.py`, `tools/regen_generated.py`, `ve/english_grammar/` (`ab2a7fb57`) | `test_generated_json_equals_lean_table`, `test_locked_view_refuses_drift`, `test_the_repository_is_in_sync` |
| No verdict changes and no new shared budget | no consumer or evaluator in en-sw | `DELTA.md`; code review |

All en-sw rows are AGENT checks and are delivered. Consumer rows are assigned to their named batches by the signed decision; ET-5 is next. The generated view is derived by running Lean's JSON export. Python loads it without repeating the Lean row checks. The existing grammar `actions_version` remains 34 because source-word rows do not alter grammar actions; the new Lean source and JSON are both hashed in the grammar LOCK. The R16 ties pass is EXTERNAL (DRI/chain); the final release gate is EXTERNAL (chain).

Overlap audit: the new `SourceWords` files and loader do not overlap in-flight branches. The shared `lean/VE.lean` import root also has separate edits on `feature/gi-1` (and older `foundation/me-1`); `tools/regen_generated.py` has older edits on `foundation/me-1` and `infra/arch-AR-1`. This item adds only the two imports and the new generator output path in those shared files; a later merge may require a mechanical rebase.

## Evidence

- F1 regression: `tests/test_source_words.py::test_lean_boundary_fixtures` passes with guards for case, repeated whitespace, tab, NBSP, Unicode folds, blank wording and blank keys. The supplied `PROBE F1` failed before the fix and passes after it.
- Lean: full `lake build`, `python3 lean/audit.py`, and `tools/english_grammar_gen.py --check` pass on the F1 code. The final release gate belongs to the chain.
- Runner portability: `tests/test_source_words.py` now builds through `tests.lean_build`; `tools/english_grammar_gen.py` resolves Lake through `tools.lake_outputs`, uses `HANG_TIMEOUT`, and reuses a prebuilt module. The two GitHub Actions failures caused by `/home/runner/.elan/bin/lake` were rerun with `VE_LEAN_PREBUILT=1` and passed. `test_source_word_export_uses_path_and_prebuilt_module` passes with a fake Lake on PATH and no home shim; restoring the hard-coded home path makes it fail.
- Trust: `tools/trust_map.py --check` measured K +0, S +55 and untied G[V] +20, all 75 lines in `VE/EnglishGrammar/SourceWords.lean`. The extra seven S lines for F1 have an R16 allowance in `docs/trust-baseline.json`; the full item remains below R16's 150-line limit. The ties-pass request for FOLLOW-UPS.md is: “Tie `SourceWords.lean` S +55 and G[V] +20 to existing English render, wire and encoder theorems.” That file is outside this worktree's writable roots; the request remains EXTERNAL (DRI/chain).
- Mutations: `mutants.json` and `trust-mutants-head.json` record the pre-F1 tree's results (102 KILLED, 24 INVALID, 34 ALLOWED). They are historical evidence, not a mutation run on F1. The F1 guards were planted against the original Lean checker and failed there before the fix.

## Seeded bugs

Each was planted in a changed product file, made the named check fail, and was removed before the committed build.

| Changed file | Seed | Failing check |
|---|---|---|
| `lean/VE/EnglishGrammar/SourceWords.lean` | replace the two-reading minimum with `true` | `lake build VE.EnglishGrammar.SourceWordsExamples` |
| `lean/VE/EnglishGrammar/SourceWords.lean` | disable the refusal substring test | same Lean fixture build |
| `lean/VE/EnglishGrammar/SourceWords.lean` | disable contextual key uniqueness | same Lean fixture build |
| `ve/english_grammar/__init__.py` | load `codes.json` in place of `source_words.json` | `tests/test_source_words.py::test_generated_json_equals_lean_table` |
| `lean/VE/EnglishGrammar/SourceWords.lean` | original exact-case rewrite, reading and ASCII-only lowercase checks | `lake build VE.EnglishGrammar.SourceWordsExamples` fails at the new F1 guards; the supplied `PROBE F1` fails |
| `tools/english_grammar_gen.py` | replace the resolved Lake executable with `missing_lake_seed` | `tests/test_source_words.py::test_generated_json_equals_lean_table` fails; restored before commit |
| `tools/english_grammar_gen.py` | restore the hard-coded home Lake path | `tests/test_source_words.py::test_source_word_export_uses_path_and_prebuilt_module` fails; restored before commit |

## Self-review against BUILDER-CHECKLIST

1. N.A. — no relayed Lean answer or request decoder was added.
2. PASS — C1 delivery table above and `test_lean_boundary_fixtures`.
3. PASS for F1 — the pre-fix Lean checker fails the new F1 guards and the supplied probe; `trust-mutants-head.json` applies only to the original catalogue tree.
4. N.A. — no evaluator or existing verdict path changed.
5. N.A. — no relayed answer or binder changed.
6. HANDOFF — the branch was originally synced at `046874048`; main advanced after this item branched. The merge train handles the current main merge and final gate, as this fix task instructs.
7. PASS — `DELTA.md` records the R16 trust row; `tools/trust_map.py --check` verifies the allowance.
8. PASS — no consumer reads the empty table; `test_generated_json_equals_lean_table` checks the new read-only view.
9. PASS — `tools/select_tests.py --base $(git merge-base HEAD main)` selection probe and selected test run are recorded below.
10. N.A. — no Lean theorem statement changed.
11. N.A. — no public budgeted operation added.
12. N.A. — no runtime admission or evaluator path changed.
13. PASS — no test removed or renamed; the original en-sw collection check reported 3 added and the F1 fix adds the path regression. The merge train checks final collection.

## Original en-sw test selection

`zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` selected 296 units. Its first pass ran 137 passing units and stopped on `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`: both new Lean JSON files lacked `other_json` entries. The manifest now records the encoder and fixture, and the isolated Mac rerun of that exact test passed. No known-main failure was edited. No full release gate was run locally, as the task assigns it to the chain.

## F1 test selection

The first F1 selected run covered 272 units on the branch: 271 units passed, and the source-word unit failed two tests because the GitHub Actions runner had no `/home/runner/.elan/bin/lake`. Both failed tests passed when rerun with the portability fix and `VE_LEAN_PREBUILT=1`.

The final selected run on the updated worktree covered 272 units: 271 passed, including `tests/test_source_words.py`; `tests/test_safety_framework.py::test_fsf_r2_probes_rerun_equals_saved_probes` failed because `probes.json` is out of date. An isolated rerun of only that test reproduced the failure. This branch changes none of the safety-framework source, test, probe code or evidence, and the failure is not one of the three entries in the supplied `main-known-red.txt`. It remains a separate fix item; no safety-framework file or known-main failure was edited. No full release gate was run locally, as this fix task assigns it to the merge train.

## Next item

ET-5 adds the first source-word rows. The C1 decision's stop-gap applies if ET-5 launched before en-sw merges; subsequent batches add rows here.
