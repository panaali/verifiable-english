# en-sw build report

Status: catalogue implemented and locally verified; the chain owns the final release gate.
Built code: `9a931e649`; synced with main at `046874048`. No product rows or verdict changes.
Open external action: the R16 ties-pass row for `/home/seyran/code/manage-agents/FOLLOW-UPS.md` could not be written because the sandbox rejects writes outside this worktree.
DRI signature needed: none. Pilot bytes expected from en-sw alone: 0.

## Statement and scope

The statement gate is the signed C1 decision in `reviews/dri-decisions-20261028-catalogue-owner.md` item 1. The owner is `english-lean`; `Catalogue.lean` remains the nonterminal table. SYNTHESIS O15/C22 and phase-2 X9/ET2 assign source-word rows to this module. Item 2 leaves consumer rows to ET-5, QT-A6, ME-11, AT-5, WG-4, SC-7, DF-4, and JT-3. Item 5 bars a new shared budget; this item adds none.

| en-sw requirement | Delivery | Check |
|---|---|---|
| Row type with `word`, `frame`, `profile`, `owner`, and `readings`/`refuse`/`fixed` kinds | `lean/VE/EnglishGrammar/SourceWords.lean` (`ab2a7fb57`) | `test_lean_boundary_fixtures` |
| Unique contextual keys; distinct readings and nonempty situations; complete refusal fields and substring-free rewrite | Lean `sourceWordsValid`, `SourceWordRow.validKind` (`ab2a7fb57`, `8cf7f22d4`) | `test_lean_boundary_fixtures`; `trust-mutants-final.json` |
| Empty product table; examples only in a fixture | `sourceWords := []`, `SourceWordsExamples.lean` (`ab2a7fb57`) | `test_generated_json_equals_lean_table` |
| Generated JSON and LOCK entry, one Python loader | `tools/english_grammar_gen.py`, `tools/regen_generated.py`, `ve/english_grammar/` (`ab2a7fb57`) | `test_generated_json_equals_lean_table`, `test_locked_view_refuses_drift`, `test_the_repository_is_in_sync` |
| No verdict changes and no new shared budget | no consumer or evaluator in en-sw | `DELTA.md`; code review |

All en-sw rows are AGENT checks and are delivered. Consumer rows are assigned to their named batches by the signed decision; ET-5 is next. The generated view is derived by running Lean's JSON export. Python loads it without repeating the Lean row checks. The existing grammar `actions_version` remains 34 because source-word rows do not alter grammar actions; the new Lean source and JSON are both hashed in the grammar LOCK. The R16 ties pass is EXTERNAL (DRI/chain); the final release gate is EXTERNAL (chain).

Overlap audit: the new `SourceWords` files and loader do not overlap in-flight branches. The shared `lean/VE.lean` import root also has separate edits on `feature/gi-1` (and older `foundation/me-1`); `tools/regen_generated.py` has older edits on `foundation/me-1` and `infra/arch-AR-1`. This item adds only the two imports and the new generator output path in those shared files; a later merge may require a mechanical rebase.

## Evidence

- Focused tests: `tests/test_source_words.py` (3 passed), and the repository sync/copy/write cases of `tests/test_english_grammar_gen.py` (3 passed).
- Lean: `lake build VE.EnglishGrammar.SourceWordsExamples`, full `lake build`, and `python3 lean/audit.py` passed before the main sync. Regeneration rebuilt and audited the Lean sources after the fixture and default-root edits. `python3 tools/check_lean_imports.py` passed on 670 modules. The final release gate will run on the committed HEAD in the chain, as the task instructs.
- Trust: `tools/trust_map.py --check` measured K +0, S +48 and untied G[V] +20, all 68 lines in `VE/EnglishGrammar/SourceWords.lean`. R16 allowance is in `docs/trust-baseline.json`, signed by standing ruling R16. The ties-pass request to add under `## en-sw` in FOLLOW-UPS.md is: “Tie `SourceWords.lean` S +48 and G[V] +20 to existing English render, wire and encoder theorems.” The sandbox denied the attempted edit to that external file.
- Mutations: `mutants.json` lists each of the eight trusted definitions and its fixture. Final `trust-mutants-head.json` records 102 KILLED, 24 INVALID, 34 ALLOWED, zero SURVIVOR and zero UNKNOWN on the import-fixed tree; `trust-mutants-allow.json` gives one-line reasons.

## Seeded bugs

Each was planted in a changed product file, made the named check fail, and was removed before the committed build.

| Changed file | Seed | Failing check |
|---|---|---|
| `lean/VE/EnglishGrammar/SourceWords.lean` | replace the two-reading minimum with `true` | `lake build VE.EnglishGrammar.SourceWordsExamples` |
| `lean/VE/EnglishGrammar/SourceWords.lean` | disable the refusal substring test | same Lean fixture build |
| `lean/VE/EnglishGrammar/SourceWords.lean` | disable contextual key uniqueness | same Lean fixture build |
| `ve/english_grammar/__init__.py` | load `codes.json` in place of `source_words.json` | `tests/test_source_words.py::test_generated_json_equals_lean_table` |

## Self-review against BUILDER-CHECKLIST

1. N.A. — no relayed Lean answer or request decoder was added.
2. PASS — C1 delivery table above and `test_lean_boundary_fixtures`.
3. PASS — four seeded bugs above and `trust-mutants-head.json`.
4. N.A. — no evaluator or existing verdict path changed.
5. N.A. — no relayed answer or binder changed.
6. PASS — main synced at `046874048`; `git merge-base --is-ancestor main HEAD`; final gate belongs to the chain by task instruction.
7. PASS — `DELTA.md` has no rows; `tools/trust_map.py --check` verifies the R16 allowance.
8. PASS — no consumer reads the empty table; `test_generated_json_equals_lean_table` checks the new read-only view.
9. PASS — `tools/select_tests.py --base $(git merge-base HEAD main)` selection probe and selected test run are recorded below.
10. N.A. — no Lean theorem statement changed.
11. N.A. — no public budgeted operation added.
12. N.A. — no runtime admission or evaluator path changed.
13. PASS — no test removed or renamed; `tools/gate_collection.py --check --prebuilt` reported 3 added, 0 removed/refused/stale/malformed.

## Final test selection

`zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` selected 296 units. Its first pass ran 137 passing units and stopped on `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`: both new Lean JSON files lacked `other_json` entries. The manifest now records the encoder and fixture, and the isolated Mac rerun of that exact test passed. No known-main failure was edited. No full release gate was run locally, as the task assigns it to the chain.

## Next item

ET-5 adds the first source-word rows. The C1 decision's stop-gap applies if ET-5 launched before en-sw merges; subsequent batches add rows here.
