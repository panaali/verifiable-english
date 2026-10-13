# RD-9 integration progress (2026-10-12)

Status: **incomplete**. This is a committed integration increment, not RD-9 acceptance. No model calls or push were made. The public soft-completion route remains disabled.

## Changes and evidence

- Merged `rd-9/py` and `rd-9/lean`, resolving only generated assurance conflicts by regeneration.
- Lean selects the gap atoms used by a separating pair's witness. The completion pair row exposes `gaps`; the Python relay checks its type and binds predicate names and tuples to the request. `test_pair_gaps_are_typed_and_bound_to_the_request` mutates a genuine Lean row and checks rejection. The renderer uses that row for E14, E19 and E21. `test_fnd1_render_shows_the_situation_with_selected_gaps` checks the result.
- Lean adds `decided_units` to enumerated verdict answers under the completion, using the case's row folds and the submitted unit order. The relay checks presence, type, uniqueness and request membership. `test_completion_decided_units_come_from_leans_folds` checks genuine answers; three `test_a_mutated_verdicts_answer_is_unavailable` cases check missing, foreign and duplicate units. The response schema and encoder theorem cover the new field.
- Added dormant soft-completion admission checks and a computed Lean fixture in `SoftWire.lean` and `SoftExamples.lean`. This code is not dispatched publicly and does not establish SC-2 through SC-6.
- `lake build`: PASS, 892 jobs, including the final build before commit. `lean/audit.py --write` and plain `lean/audit.py`: PASS earlier on the same Lean sources, 485 source files and 5,288 named theorems, standard axioms only. A redundant final plain-audit rerun was interrupted while a generated-file check repeated the audit.
- The focused pair, render and verdict mutation tests passed; F-ND2's stale full-table-gap expectation failed in the selected run, was corrected to the SC-A witness selection, and its 65-test file passed. Decoder range and whole-file pin tests passed after reviewed pin updates.
- The selected map expands to all 366 test units without a usable recorded coverage map. One whole-file xdist attempt found the F-ND2 golden failure at 61%. A rerun passed it and reached 89% without another failure, then was interrupted after prolonged graph-search cases. The selected suite has **not** passed in full. The final focused RD-9 run passed 175 tests.
- The response-schema, assurance-manifest and route-map checks passed. The full generated-file check was interrupted during its repeated Lean audit. `tools/trust_map.py --check` classified all lines but failed the unsigned +150 trusted-line budget; the signed baseline remains unchanged.

## Seeded bugs removed

| Seed | Temporary change | Failing check |
| --- | --- | --- |
| M1 | Replaced the new pair-gap binding check in `ve/readings_route.py` with unconditional acceptance | `test_pair_gaps_are_typed_and_bound_to_the_request`: forged row did not raise `CheckerUnavailable` |
| M2 | Removed duplicate detection for `decided_units` in `ve/readings_verdicts.py` | `test_a_mutated_verdicts_answer_is_unavailable[decided unit duplicated]`: forged row did not raise `CheckerUnavailable` |
| M3 | Made Lean `decisionCount` always return zero in `UnspecifiedWire.lean` | `lake build VE.Readings.SoftExamples`: line 17's computed `#guard` failed |

All three mutations were restored. The restored Lean build and focused tests passed.

## DRI rulings and open signatures

| Delta | Ruling and evidence |
| --- | --- |
| Added completion pair `gaps` field | SIGNED by standing ruling R3 (DRI-RULINGS.md): `test_pair_gaps_are_typed_and_bound_to_the_request` checks the field against a genuine Lean row and binds each predicate and tuple to the request. |
| Added completion verdict `decided_units` field | **Needs item-specific DRI signature.** It carries Lean's derived unit decision, beyond R3's location/explanation class. `test_completion_decided_units_come_from_leans_folds` and the three `decided unit` mutations check the genuine value and binding. |
| E19 now omits full-table gap sentences unrelated to its witness | **Needs item-specific DRI signature.** F-ND1 loses two previously quoted gap answers and F-ND2 loses three; R1 does not cover information removal. The updated F-ND1 and F-ND2 goldens record the exact deltas. |
| Trusted Lean lines | **Needs item-specific DRI signature.** `tools/trust_map.py --check` classifies every declaration and measures trusted +150 against the signed baseline. R6 does not apply because no Python or Rust decision path was deleted. `docs/trust-baseline.json` is unchanged. |

## Remaining RD-9 work

- SC-1's `softX_wellFormed` theorem and the rest of its acceptance fixtures; SC-A's cone statements.
- SC-2 separation, SC-3 force twins, SC-4 route replay/dispatch, SC-5 soft verdicts, and SC-6 layered admission/certificate and graph leaves.
- SC-8 document relay and generators, SC-9 source audit and use-case report, and three-way Python/Lean/Rust conformance on the spec fixtures.
- Item-specific DRI decisions for the gap wording, trust growth and any later visible availability or statement change. A full release-gate attempt on the committed integration HEAD remains due after this report commit; it cannot establish RD-9 acceptance while these items and SC-1 through SC-9 remain open.

## Build checklist (`manage-agents/prompts/build-checklist.txt`)

Statuses describe this increment. **Open** entries are requirements for full RD-9 acceptance, not claimed as done.

| Line | Status | Evidence or reason |
| --- | --- | --- |
| 1 | Done for this increment | The new fields come from Lean and its generated response schema; no diagnostic table was copied. |
| 2 | Open | Three-way one- and two-fault conformance on the spec fixtures is not built. |
| 3 | Not applicable | No text normalizer or parser grammar changed. |
| 4 | Done for the new fields | Genuine Lean pair and verdict rows are retyped and rebound by the added mutations. |
| 5 | Open | Malformed input matrix for the completed soft route is not built. |
| 6 | Done for this increment | Existing three-valued folds remain; no soft verdict operation was enabled. |
| 7 | Not applicable | No deadline or budget wrapper changed. |
| 8 | Not applicable | No kind/owner inductive or fold changed. |
| 9 | Done for this increment | E14's parser gate and F-ND1/F-ND2's exact E19 render goldens pass; the soft route's English remains open. |
| 10 | Open | Soft route entry points and their metamorphic equality test are not built. |
| 11 | Done | No regex parser was added; Lean compilation and the existing English parser are the oracles. |
| 12 | Not applicable | No ledger or state machine changed. |
| 13 | Done | M1–M3 each failed a test or Lean guard and were removed. |
| 14 | Done for this increment | Added tests use genuine local Lean rows and `tmp_path`; no model, network, sleep or short timeout. |
| 15 | Done for the new fields | Gap predicates/tuples and unit ids are bound to the request; no certificate binding changed. |
| 16 | Done for this increment | Audit, statement, schema, checker pin, frozen-source and gate collection inventories regenerated. |
| 17 | Open | The exact-statement script passes 48 SC-1 declarations but reports `softX_wellFormed` unbuilt. |
| 18 | Open | `SoftExamples.lean` has computed guards, but SC-1/SC-2's full boundary fixture table is incomplete. |
| 19 | Open | SC-9 use-case formalisation and weakening/strengthening mutants are not built. |
| 20 | Open | The final acceptance report and saved gate evidence do not exist. |
| 21 | Done for this report | AGENT items and HUMAN/DRI signatures are separated here; SC-9's EXTERNAL source audit is deferred. |
| 22 | Open | Plain audit passed. The selected suite found a stale F-ND2 gap golden, corrected here; its rerun reached 89% with no further failure before interruption, so the selected suite remains incomplete. A full gate attempt on the committed integration HEAD is pending after this report commit. |
| 23 | Open | R3 covers the explanatory pair `gaps` field. Gap information loss, `decided_units` and trust growth need item-specific DRI signatures. |

## Acceptance owners

- **AGENT:** the merged partial code, schemas, proof, focused tests and mutations above; remaining SC batches and final gate open.
- **HUMAN / DRI:** the three unsigned deltas above and any later item-specific statement or availability ruling.
- **EXTERNAL:** SC-9's independent source check and three-way use-case evidence, not run.

## Post-review correction (2026-10-12)

The report above records the earlier integration commit. This correction fixes two live Lean answer defects without
claiming RD-9 acceptance:

- `ndPairFacts` now includes dependencies of both displayed pair values and reads each candidate from admission's
  table. F-ND1's default witness and F-ND2 each render the missing gap. The regression IDs are
  `test_fnd1_render_shows_the_situation_with_its_filled_gaps`, `test_fnd2_render`,
  `test_fnd1_validate_separates_on_the_filled_document` and
  `test_the_route_builds_a_candidates_document_only_in_the_request_table`.
- `ndVerdictsAnswer` tests whether `assumed` was supplied, including `assumed: []`. Component subanswers use that
  same answer constructor, and the product fold uses the same presence rule. The regression IDs are
  `test_explicit_empty_assumed_has_no_decided_units` and
  `test_component_completion_answers_include_decided_units_and_respect_empty_assumed`.
- The changed Lean files, checker, assurance pins, frozen-source list and test collection were refreshed through
  their owners. RD-6b's trust report test now measures its saved historical commit instead of a moving checkout.
- `lake build` and `python3 lean/audit.py` passed. The selected command ran all 366 mapped units. Its failures were
  rerun by node ID after the fixes and generator updates; the final two pin/report failures passed on their own
  rerun. The release gate was not run, as required by this fix task.

RD-9 remains incomplete: `softX_wellFormed`, SC-2 through SC-6, SC-8, SC-9 and three-way fixture agreement are
still open. The public soft completion is still disabled. No model calls or push were made. The `decided_units`
field, the English gap selection and the current trust growth still need item-specific DRI signatures; R1 and R6 do
not sign them. `tools/trust_map.py --check` reports K +0, S +56 and V +105 against the signed baseline (trusted +161),
with no unclassified declarations. The explanatory `gaps` field remains SIGNED by standing ruling R3
(DRI-RULINGS.md), with `test_pair_gaps_are_typed_and_bound_to_the_request` checking request binding.

## Committed-HEAD selected test run (2026-10-12)

On commit `2c5e77741f`, `uv run python tools/select_tests.py --base $(git merge-base HEAD main) --run`
selected and completed all 366 mapped units in the foreground. Its build and Lean audit stages passed. Three
existing test nodes failed in that run and passed when only those nodes were rerun:

| Node | Initial result | Focused rerun |
| --- | --- | --- |
| `tests/test_gate_integrity.py::test_fsmonitor_hook_cannot_hide_edited_source` | Failed to detect a same-size, immediate rewrite in a temporary Git repo | Passed |
| `tests/test_lean_document_wrapper.py::test_null_and_number_forms_agree_with_python_or_fail_closed[usecases/question-answering/udhr-part07.ve.md]` | One mutated document differed | Passed |
| `tests/test_question_reading.py::test_the_whole_question_is_bounded_by_the_modes_deadline` | One microsecond deadline did not fire | Passed |

The selection recorded 363 passing units and three failed units; the focused `pytest` invocation recorded
`3 passed`. This is evidence for the changed behavior and the requested rerun policy, not a passing release gate.
The full gate was not run under this task's explicit test instruction. No `PROBE Fk:` executable probes occur in
either review.

## rd-9-looprecheck1 fix round (2026-10-13)

The one open A/B finding of `rd-9-looprecheck1.final.md` is **Astra A / Fable B2**: `softX_wellFormed` unbuilt,
SC-2 to SC-6, SC-8 and three-way fixtures open, the soft route refusing. This round builds the soft route through
Lean and the document path. RD-9 is still not accepted: the items under "Still open" and the DRI signatures remain.
No model calls or push were made.

| Part of the finding | Fix | Regression tests | Commit |
| --- | --- | --- | --- |
| `softX_wellFormed` unbuilt (PROBE A) | `softX_wellFormed` proved through `Wire.softLabelledU_wellFormed`; the statement checker covers every built block of spec 6 | `tests/test_rd9_statements.py::test_rd9_statements_match_the_approved_text_with_nothing_unbuilt` (PROBE A failed before the fix: "unbuilt in this batch: softX_wellFormed"; passes after) | d420445e |
| SC-2 separation | `SoftSeparate.lean`: `separatesS`, `separatesS_sound`, `separatesS_separated` on filled sides; computed fixtures F-SD1 to F-SD5, K2, NSDp, NSDq, C1′, C2′, C9′ | `SoftSeparateExamples.lean` guards; `test_rd9_statements.py` (6.6) | d420445e |
| SC-6 layered kinds | admission and certificate kinds on the soft branch (`LayeredAdmission.lean`), `softCase` dispatch, schema and encoder | `tests/test_norm_defaults_soft_kinds.py` (8 tests) | 1c1cce1e |
| SC-4 wire | the readings route under the soft completion: admission, separation, elaborate and choice on `choiceLayeredG`, `soft_premises` relayed and bound | `tests/test_readings_sd_lean.py`, `tests/test_readings_sd_relay.py` | 321e610a |
| SC-5 verdicts | `XEvidence`, the `x*` rows and `x_rowsHold`; `NDEvidence = XEvidence (choiceU N c) []` with one per-choice decoder (`xEvidenceOf`) for both chains; `SoftVerdicts.lean` (`replayVerdictsSD`, seven `readings_wire_sd_verdicts_*` theorems); `readings-verdicts` answered under the soft completion with `decided_units` | `test_readings_sd_lean.py::test_fsd1_verdicts_*`, `::test_fsd2_verdicts_take_the_enumerated_route`, `::test_fsd4_a_conflict_free_answer_rests_on_the_coherence_premise`, `::test_fsd8_evidence_for_another_choice_is_never_a_verdict`, `::test_fsd9_verdicts_beyond_64_choices`, `::test_fsd11_a_verdict_certificate_binds_the_assertions_it_takes`; RD-3's verdict, component and decided-share tests unchanged (320 passed) | cecc1754 |
| SC-8 documents, relay, generators | the refusal narrowed to the rights route (3.11 row 7); no W1 container or Python soft premise under the soft completion; `_FilledChoiceDocument` reads the chain, `Soft_T` and the decision tables from Lean's row; the search filters by Lean's `soft_premises`; one soft-label binder | `tests/test_readings_sd_document.py` (F-SD1 load, check, render, `readings --conclusion`, generator, rights refusal); `test_readings_sd_relay.py::test_a_soft_label_the_request_does_not_declare_is_unavailable` | 4ff93b21, eba352a6 |
| Three-way fixtures (checklist 2) | the soft completion's differential: generated twins, Python's search against Lean, 1- and 2-fault mutations compared by text, the relay equal to Lean's row. Rust has no readings role (its replay was deleted in lean-first batch 3), so the third leg is Lean's own answer on the unmutated input | `tests/test_readings_sd_differential.py` (4 tests) | ec064fa9 |

### Seeded bugs (each restored)

| Seed | Language | Temporary change | Failing check |
| --- | --- | --- | --- |
| S2-M1 | Lean | `separatesS`'s `fillHoldsS` conjunct made vacuous | `lake build VE.Readings.SoftSeparateExamples`: `separatesS_sound` no longer elaborates |
| S6-M1 | Lean | `replayLayeredEntailment` bound without `X` | `test_norm_defaults_soft_kinds.py::test_the_soft_premises_are_part_of_the_binding` |
| S4-M1 | Python | `_bind_soft_premises` returns at once | 12 of `test_readings_sd_relay.py::test_a_mutated_soft_row_is_unavailable[*]` |
| S4-M2 | Lean | `pairFactsS` without the witness's `Fill_T` | `test_readings_sd_lean.py::test_fill_holds_alone_decides_the_pair` |
| S5-M1 | Lean | `xEvidenceOf` binds certificates without the choice's assertions | `test_readings_sd_lean.py::test_fsd11_a_verdict_certificate_binds_the_assertions_it_takes` |
| S8-M1 | Python | `_FilledChoiceDocument` without the choice's decision tables | `test_readings_sd_document.py::test_fsd1_check_folds_leans_verdicts`, `::test_fsd1_readings_conclusion_some_all_none` |
| S8-M2 | Python | `soft_label` accepts every label | 11 tests of `test_readings_sd_relay.py` |

No Rust product code changed.

### Evidence

- `lake build`: PASS (900 jobs). `python3 lean/audit.py`: PASS, 489 source files, 5,371 named theorems, standard
  axioms only. `tools/check_rd9_sc1_statements.py`: every block of SC-1, SC-2, SC-4, SC-5 and SC-6 matches, with two
  declarations pending the bounded statement re-check (spec 12.24 `choiceLayeredG`, 12.25 `ndTextWith`).
- `tools/regen_generated.py --check`: every generated file fresh except `trust-tables` (the budget below).
- Selected tests (`tools/select_tests.py --base $(git merge-base HEAD main) --run --jobs 8`, 372 units, in effect
  the whole suite) on ec064fa9: the run reached its one-hour foreground limit after 291 files, 289 passing. The 80
  files it had not reached ran by `pytest -n 8` on the same commit: 2,886 passed. Two failures were this branch's:
  `test_numeral_conversion.py::test_every_int_conversion_in_ve_is_bounded_or_reviewed` (`int()` in the moved soft
  label check) and `test_consolidation_tools.py::test_committed_ledger_names_real_declarations` (the plan's
  measured ledger rows); both are fixed in eba352a6 and pass on rerun with the tests the fix affects (343 passed).
- The release gate was not run, as this task requires.

### DRI rulings and open signatures

| Delta | Ruling and evidence |
| --- | --- |
| `soft_premises` per reading (validate, elaborate) | SIGNED by standing ruling R3 (DRI-RULINGS.md): information added, nothing removed; bound to the request by `_bind_soft_premises` and checked against Lean's rows by `test_readings_sd_relay.py` |
| Soft-completion documents answered (K18 and every soft-chain document under `norm-defaults@0`; the refusal narrowed to the rights route) | **Needs DRI signature**: it widens what is accepted (never covered by a standing ruling) |
| The layered certificate kind's refusal of a rights source ("property not found: premises") | **Needs DRI signature** (availability change) |
| `normDefaults_wire_admission` gains the hypothesis that the source is not on the soft layered route | **Needs DRI signature**: an approved statement changed |
| `choiceLayeredG` gains `(hN : N.D = b.D)`; `ndTextWith` keeps `let freeDoc` | **Pending the bounded statement re-check** (spec 12.24, 12.25) |
| Trusted Lean lines: K +0, S +171, trusted +529 against the signed baseline | **Needs DRI signature**: R6 does not apply (no Python or Rust decision path deleted) |
| `decided_units`, E19's gap selection (earlier rounds) | **Still need item-specific DRI signatures** |
| The E3 line of a soft label | **Needs a DRI wording decision**: D12 assumed soft-norms 2.1's and 2.3's sentences exist as renderers; no renderer words a coherence premise, so Lean's plan gives the label an `unworded` line and the answer is unavailable (`test_readings_sd_document.py::test_a_verdict_on_a_soft_label_is_unavailable_until_its_sentence_exists`) |

### Still open

- SC-3 (`decision_only_soundS`, off the path: E25 stays "not certified").
- SC-8's `soft__` relay lint: S1's and S2's Python still name decision predicates (`readings_s1.Side.gen_keys`,
  `readings_s2_wording._decision_names`, `readings_sup.name_map`). Removing them needs Lean to emit each decision's key
  in the soft row (a soft-norms wire change); not done in this round.
- The generator does not model `F_p` on the soft chain (no filled readings document exists there, 4.1): a separation
  whose guard reads a gap is not found (recorded in
  `test_readings_sd_document.py::test_generator_records_not_found_where_a_guard_reads_a_gap`).
- SC-9 (the constitution `CE4`, C1 to C10) and its EXTERNAL source check; SC-10 and SC-11 (superposition).
- The full release gate on the final HEAD.

### Build checklist (this round)

| Line | Status |
| --- | --- |
| 2 | Done for the soft completion's Python/Lean legs (`test_readings_sd_differential.py`); no Rust readings leg exists |
| 4 | Done: `soft_premises` and soft verdict labels mutated and retyped (`test_readings_sd_relay.py`) |
| 9 | Open for soft labels (the wording decision above); F-SD1's lines pass the existing renderers |
| 13 | Done: S2-M1 to S8-M2 above |
| 17 | Done except the two pending declarations above |
| 22 | Selected tests run as above; the full gate not run (task instruction) |
| 23 | As the table above |
