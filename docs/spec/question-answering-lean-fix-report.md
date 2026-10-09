# Question answering Lean build report

Status: Q1.1 in progress. This report records the local state after the first reader implementation and proof pass. The approved statements remain in `docs/spec/question-answering.md` section 5.1.

## Changes checked

- The question shape, gap generation, candidate construction, classification, rephrasing, closest diagnosis, and corrected span mapper are implemented under `lean/VE/Question/`.
- Two of the fifteen approved Q1 theorems are proved: `got_none` and `question_reading_unique`. Their signatures match section 5.1. A list-order helper is also proved.
- Executable Lean guards cover F1 precedence, F2 gap order and bytes, the group fixture's exact G1 reading, G5 rephrasings, G9 closest candidate, the work budget at zero, the crossing interval G25, and Unicode interval G26.
- The frozen Norms, SoftNorms, and Route source files were not edited.

## Mutation checks

Each mutation was applied to the new Lean source, `lake build VE.Question.Examples` failed on an executable guard, and the source was restored and rebuilt successfully:

1. Forced F1 precedence off in `shape`: three F1 guards failed.
2. Kept punctuation as a gap in `gaps`: the `Ann, bo` gap guard failed.
3. Changed span enclosure's upper bound from `max` to `min`: the crossing interval guard failed.

## Checks and limits

`lake build` passed after the restored code. `python3 lean/audit.py --write` audited 463 source files and 4,812 theorems, with only the standard axiom allowlist. The required no-write audit and full gate are run separately from this report.

The remaining thirteen section 5.1 theorem proofs, the complete fixture set, the question lock list, the targeted joint span review, and the Q1.2 service integration are not complete. No model calls were made. No Q2 code was changed.

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
| 9. English render/read-back | Not done | The exact `rephrasings_read` and `asked_reads_back` theorems remain. |
| 10. One admit entry point | Not applicable | Q1.1 adds a pure Lean reader, no admission entry point. |
| 11. Compiler or library parsing | Done | Candidate gaps use `lexSpans`; candidates use E2's `read`, with no language regex. |
| 12. Stateful ledger | Not applicable | Q1.1 has no ledger or state machine. |
| 13. Seeded checker mutations | Done | The three mutations above each failed a guard and were removed. |
| 14. Hermetic execution | Done for Q1.1 | The new guards are pure Lean computations; no sleeps, caches, or external writes. |
| 15. Schema identity | Not applicable | Q1.1 has no wire schema or certificates. |
| 16. Complete lists and locks | Not done | The requested `ve/question/LOCK.json` is outstanding. |
| 17. Approved-statement diff | Not done | Two statements are proved; the statement-diff script and thirteen proofs are outstanding. |
| 18. Stub and boundary fixtures | Not done | The spec records stub evaluation, and the new guards cover selected boundaries only. |
| 19. Use-case formalisation | Not applicable | Q1.1 has no formalised document or rule answer key. |
| 20. Regenerated numeric report | Not applicable | This pass makes no coverage or performance claims. |
| 21. Acceptance owners | Not done | AGENT/HUMAN/EXTERNAL tags and deferred owner record are outstanding. |
| 22. Clean HEAD gate and fix report | Not done | This non-empty report exists; the full gate on clean HEAD remains. |
