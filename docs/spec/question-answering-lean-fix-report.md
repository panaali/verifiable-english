# Question answering Lean build report

Status: Q1.1 in progress. This report records the local state after the first reader implementation and proof pass. The approved statements remain in `docs/spec/question-answering.md` section 5.1.

## Changes checked

- The question shape, gap generation, candidate construction, classification, rephrasing, closest diagnosis, and corrected span mapper are implemented under `lean/VE/Question/`.
- Seven of the fifteen approved Q1 theorems are proved: `got_none`, `question_reading_unique`, `asked_reads_back`, `readQuestion_ambiguous`, `readQuestion_meanings`, `readQuestion_indefinite`, and `readQuestion_none`. Their signatures match section 5.1. Supporting lemmas establish list order, meaning-fold soundness and uniqueness, read-back, the two distinct derivations of an ambiguous candidate, the absence of readings in `.none`, and closest-candidate provenance.
- Executable Lean guards cover F1 precedence, F2 gap order and bytes, the group fixture's exact G1 reading, G5 rephrasings, G9 closest candidate, the work budget at zero, the crossing interval G25, and Unicode interval G26. Both span guards also check the emitted code point bounds.
- The frozen Norms, SoftNorms, and Route source files were not edited.

## Mutation checks

Each mutation was applied to the new Lean source, `lake build VE.Question.Examples` failed on an executable guard, and the source was restored and rebuilt successfully:

1. Forced F1 precedence off in `shape`: three F1 guards failed.
2. Kept punctuation as a gap in `gaps`: the `Ann, bo` gap guard failed.
3. Changed span enclosure's upper bound from `max` to `min`: the crossing interval guard failed.

## Checks and limits

`lake build` passed after the seventh theorem. `python3 lean/audit.py --write` and the no-write `python3 lean/audit.py` both passed on 463 source files and 4,838 theorems, with only the standard axiom allowlist. The full gate is run separately from this report.

The remaining eight section 5.1 theorem proofs, the complete fixture set, the targeted joint span review, and the Q1.2 service integration are not complete. No model calls were made. No Q2 code was changed.

`tools/trust_map.py --check` on this source reports 342 unclassified lines and 397 trusted-line growth against the baseline, including the new Question modules and existing drift in other modules. A DRI-signed allowance is not present.

## Build checklist (current Q1.1 scope)

| Line | Status | Basis |
|---|---|---|
| 1. One generated contract | Not done | Question codes and texts are Lean-only, but the generated table and JSON mode are not built. |
| 2. Differential fuzz Py/Lean/Rust | Not applicable | Q1.1 has only a Lean reader; no Python or Rust question implementation exists. |
| 3. Shared text normalization | Not applicable | The question reader delegates tokenization to the frozen English lexer and adds no normalization path. |
| 4. Validate untrusted output | Not applicable | Q1.1 has no external response or ledger decoder. |
| 5. Malformed JSON and IDs | Not applicable | Q1.1 has no JSON entry point or referenced IDs. |
| 6. Three-valued verdicts and budget zero | Done | `Outcome` distinguishes no reading, refusal, and budget; the zero-budget group guard checks budget. |
| 7. Whole-operation deadlines | Not done | The approved reader applies E2's work budget per candidate; no whole-question deadline test exists. |
| 8. Exhaustive kind and owner folds | Not applicable | Q1.1 introduces neither kind nor owner folds. |
| 9. English render/read-back | Not done | `asked_reads_back` is proved; `rephrasings_read` remains. |
| 10. One admit entry point | Not applicable | Q1.1 adds a pure Lean reader, no admission entry point. |
| 11. Compiler or library parsing | Done | Candidate gaps use `lexSpans`; candidates use E2's `read`, with no language regex. |
| 12. Stateful ledger | Not applicable | Q1.1 has no ledger or state machine. |
| 13. Seeded checker mutations | Done | The three mutations above each failed a guard and were removed. |
| 14. Hermetic execution | Done for Q1.1 | The new guards are pure Lean computations; no sleeps, caches, or external writes. |
| 15. Schema identity | Not applicable | Q1.1 has no wire schema or certificates. |
| 16. Complete lists and locks | Done for Q1.1 | `ve/question/LOCK.json` hashes every Question Lean file; `tools/question_lock.py` verifies the complete list and version. |
| 17. Approved-statement diff | Not done | `tools/question_statements.py` confirms the seven proved statements match section 5.1 and reports eight missing proofs. |
| 18. Stub and boundary fixtures | Not done | The spec records stub evaluation, and the new guards cover selected boundaries only. |
| 19. Use-case formalisation | Not applicable | Q1.1 has no formalised document or rule answer key. |
| 20. Regenerated numeric report | Not applicable | This pass makes no coverage or performance claims. |
| 21. Acceptance owners | Done | The table below records AGENT, HUMAN, and EXTERNAL acceptance work and the deferred gate. |
| 22. Clean HEAD gate and fix report | Not done | This non-empty report exists; the full gate on clean HEAD remains. |

## Acceptance owners

| Owner | Work | State |
|---|---|---|
| AGENT | Q1.1 Lean definitions, exact proofs, guards, lock, build and audit | In progress; eight proofs and full fixture coverage remain. |
| HUMAN | Targeted joint review of the corrected span map, byte and code point bounds, and G9/A9/U1 plus crossing and Unicode guards | Deferred until the AGENT span proofs and fixtures are complete. |
| EXTERNAL | RD-3 merge and review of the corrected Q2 statements and fixtures | Deferred; Q2 work has not started. |

## Full gate result on `17547abe`

The first clean-HEAD run stopped at Rust build because the offline cache lacked `serde`. `cargo fetch --locked` filled the ignored, pinned crate cache without changing tracked files. The rerun completed every gate stage: Lean build, Lean audit, Rust build, 36 Rust tests, Python collection and Python suite. The gate **failed** with 13,071 Python passes, 17 failures, 9 skips and one live-test deselection out of 13,098 collected tests.

The failures cluster around two repository inventories that this pass did not update: the compiled statement, predicate and declaration dumps, and `lean/VE/Route/frozen-sources.sha256`, which must list every new `VE` module and the changed audit manifest. The statement dumps have since been regenerated; a subsequent proof pass added `asked_reads_back` and refreshed them again. The Route inventory remains unchanged pending clarification of the explicit instruction to leave frozen Route untouched. `tools/trust_map.py --check` also reports 388 new unclassified trusted lines, including the new Question modules and existing baseline drift; no DRI budget signature was invented. Two skip-policy failures concern Rust-scope exclusions in the existing P0 suite.

## Full gate result on `5f2eb90e`

The clean-HEAD gate passed Lean build and audit, Rust build, and 36 Rust tests. Python collected 13,098 tests, selected 13,097, and recorded 13,075 passes, 13 failures, and 9 skips. The gate failed on the unclassified trust table (339 lines), the unchanged Route hash inventory, and precommit checks that depend on that inventory. Two existing Rust-scope skips are disallowed by gate policy. The source has since gained three more approved theorems; its audit and inventories are being refreshed before a new clean-HEAD run.
