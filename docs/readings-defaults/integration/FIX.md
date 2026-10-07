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

## Review fixes (2026-10-07: Astra `readings-defaults-review-astra.final.md`, Fable `reviews/readings-defaults-review-fable.md`)

| Finding | Fix (the class removed) | Commit |
|---|---|---|
| Astra A / Fable A1, merge scope | The DRI ruled the A4 slot change a signed English delta inside RD-1 (kept, not reverted); its correctness items are B below and Fable A1's new errors | — |
| Astra B: verb-only names hide precedence and exception notes | One rule (`sentence_slots`) decides over each candidate's full sentence, notes included: the italic verb only when the full sentences are one frame, else each full sentence. `rule_sentence` also shows a default rule's exception decider when it is not the document's default (no note showed it). Class test: every field of the rule schema (checked against the `Norm`/`SoftRule` dataclasses) mutated alone and with the verb, on a strict and a default base, 1,000+ pairs: different meanings (`rule_key`) always get different showable names. S1's K14 now shows full sentences (exception conditions); expectation updated | `9bf13780` |
| Fable A1, new errors under A4 | A reading the slot cannot show (no content, no read-back, one sentence for two meanings) is `Unnamed` and refused only where an answer names it; equal meanings share a name; the renderer's `ValueError` becomes the slot's refusal instead of escaping | `9bf13780` |
| Fable B1: `unsaid__` refused without `norm-defaults@0` | `Slots.reserved` from the document's profiles (fail-closed without an environment); the prefixes are one table in `ve/environment.py`, read by the environment check, `norm_defaults` and `tools/relay_lint.py`. Fable's document (`readings@1`, predicate `unsaid__x`) now answers | `9bf13780` |
| Fable B2: statement checker gaps | Spec 6.2 states the DRI-approved `attached_fillDoc`; PENDING empty; every 6.2 declaration (1 structure, 20 definitions with bodies, 10 theorems) is read from the spec block and compared; each of the 31 changed in Lean fails by name | `0d383ee4` |
| Astra C (DRI: fix): one-rule CONFLICT-FREE claim | The sentence is about a rule checked by itself, says it does not cover a reading checked with other rules (M8), and is null without a Lean answer; spec 10 matches | `4da1beb1` |
| Fable C2: READINGS.md hypotheses, stale pending note | Each theorem's own hypotheses; DRI approval recorded | `0d383ee4` |
| Fable C3: names re-rendered per pair | Computed once per set | `9bf13780` |
| Fable C1: Sonnet reader test of the long names | Not done: no model calls in this run (HUMAN/EXTERNAL, deferred to RD-3's signing) | — |

Seeded bugs, each planted, its test failed, then removed: verb-only without the frame check (8 tests failed, the
class test included); decider note dropped (2); reserved prefixes hidden regardless of profile (1); `ValueError`
not converted (1); definitions skipped by the checker (20); one-rule sentence without a Lean answer (1).

Gate on the fix commits (this worktree, HEAD `a18e08a8` plus this report): `lake build` 784 jobs, success;
`python lean/audit.py` PASS (430 files, 4668 theorems, standard axioms only); statement checker PASS (31 exact, 0
pending); `tools/relay_lint.py`, `tools/check_python_layers.py`, `tools/test_layer_policy.py` PASS; gate collection
regenerated (one ID renamed). Full suite in five chunks (`-n 16`, `VE_LEAN_PREBUILT=1`, four slow tests deselected):
1929 passed, 1 skipped; 4001 passed, 2 skipped; 1822 passed, 3 skipped; 2420 passed; 1517 passed. The four slow
tests alone (`-n 4`): 28 passed.

## Recheck fixes (2026-10-07: `readings-defaults-looprecheck1.final.md`)

| Finding | Fix (the class removed) | Commit |
|---|---|---|
| New B: reading names that quote author text are refused (`standard-x` holds `rd-`) | The S2 gate tested the whole line for the generated and reserved prefixes as substrings, in every slot that shows author text: rule names in notes, predicates in conclusions and situations, clauses. Names are generated and reserved by prefix (Lean's `startsWith`), so one function, `hidden_in`, matches a prefix only where no name character (letter, digit, `_`, `-`) precedes it. `may not` stays a substring test (G9 has no exception, composition.md 13.20). The gate and the tests' G6/G9 oracles all read `hidden_in`. Class tests: every prefix (`ve__`, `rd-`, `soft__`, `rights__`, `unsaid__`, `unsaid--`) in each of the four author-text slots, shown inside a name after five kinds of name character and refused at a name's start after eight kinds of boundary; the recheck's document with `standard-x`, `record-keeping`, `hazard-rd-x`, `ward-rd-2` (answers SOME); author predicates `save__x`, `microsoft__x`, `copyrights__x` in a conclusion | `63f44a46` |
| Follow-up: `"unsaid__"` hard-coded in `norms.py`, `norm_defaults.py` | These, and `norm_defaults_english.py`, read `environment.UNSAID_PREFIX` | `21f64a33` |

Not taken here (follow-up, no trigger found by the recheck): `named_pair` before E14/E24; multi-line assertion
names inside one-line sentences and "an user"; `rule_key`'s docstring. Seeded bug: the old substring test put back
in `hidden_in`, 12 of the new tests failed, then removed.

Gate on `21f64a33`: `lake build` 784 jobs, success; `python lean/audit.py` PASS (430 files, 4668 theorems, standard
axioms only); `tools/check_python_layers.py`, `tools/test_layer_policy.py` PASS; gate collection regenerated (13
IDs added, none removed). Full suite in five chunks (`-n 16`, `VE_LEAN_PREBUILT=1`, four slow tests deselected):
1929 passed, 1 skipped; 4001 passed, 2 skipped; 1835 passed, 3 skipped; 2420 passed; 1517 passed. The four slow
tests alone (`-n 4`): 28 passed.

## Open work and acceptance

- **Done (DRI 2026-10-07):** the corrected `attached_fillDoc` statement is approved and now in spec 6.2.
- **Done (DRI 2026-10-07):** the A4 `<reading>` wording change is signed; the review fixes above make it correct.
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
| 17. Approved statement diff | Done for RD-1 | Every 6.2 declaration (31) matches the approved text; nothing pending. |
| 18. Spec-stage theorem fixtures | Done for RD-1 | Lean fixture guards built, including the counterexample and iff boundaries; later batches have not started. |
| 19. Use-case formalisation | Not done | RD-5's pilot and answer-key mutants have not been built. |
| 20. Reports from gate JSON | Not done | The machine-readable gate result is included, but report-number regeneration by a test has not been added. |
| 21. Acceptance owners | Done | This report and the worker reports tag the DRI item HUMAN and the statement review EXTERNAL with owners. |
| 22. Commit, clean gate, disk, report | Done for code merge | Both merges were committed, `gate-code.json` is a clean-tree passing run on the code commit, disk had 63 GB free, and this report is non-empty. A final gate on the report commit is recorded separately. |
