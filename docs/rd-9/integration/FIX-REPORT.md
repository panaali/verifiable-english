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
| The layered certificate kind now replays a soft source; a missing `premises` field gives the norms replay's existing `property not found: premises` text | DRI decision B2, conditional: `test_missing_certificate_premises_has_the_norms_branch_text` checks byte-identical text. Follow-up: Lean's decoder should give typed `InvalidInput` with a JSON path (AR-13 codes). Rights sources retain `UnsupportedProfile` (`test_rights_sources_keep_todays_answers`). |
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

## rd-9-looprecheck2 fix round (2026-10-13)

`rd-9-looprecheck2.final.md` has two open A/B findings: **Astra A / Fable B2** (narrowed to the `CE4` fixtures C1 to C8
and SC-8's relay lint) and **new B3** (soft labels not bound to the request's conditions). Each is fixed as a class.
RD-9 is still not accepted: the DRI signatures and the deferred items below remain. No model calls or push were made.

| Finding | Fix | Regression tests | Commit |
| --- | --- | --- | --- |
| B3: a soft label is bound to a declared rule only, not to its conditions (PROBE B3) | One binder for `soft_premises` and verdict labels: `readings_route.soft_rules` reads each declared rule's shape as Lean decodes it (`node_value`: default or strict, the numbers of sufficient and necessary conditions); `soft_label` accepts `soft:exception:<rule>:<role>:<i>` only for a default rule with `i` below that role's count, and `soft:coherence:<a>,<b>` only for two default rules in Lean's order (`collidingPairs`: `a < b`). This also closes the FOLLOW-UP "the coherence pair's order isn't bound" | `tests/test_readings_sd_relay.py::test_probe_b3_an_exception_index_past_the_rules_conditions_is_unavailable` (the probe: failed before, "DID NOT RAISE"; passes after); `::test_the_binder_accepts_exactly_the_exception_labels_lean_regenerates` (every rule × role × index ≤ 3: accepted = Lean's `excLabels`); 6 new `::test_a_mutated_soft_row_is_unavailable[…]` and 5 new `::test_a_soft_label_the_request_does_not_declare_is_unavailable[…]` | ca40261b |
| A2, part 1: SC-8's relay lint; 12 `soft__` literals in `ve/readings*.py` | Lean's soft-norms row keys each decision: `SoftNorms.keyedDecisions` (`keyedDecisions_names`: its names are `decisions`), `Wire.decisionKeyJson`, the `decision_key` shape and `decisionKeyJson_fits`. The relay binds each key to the request (`SoftNormDocument.decision_by_key`: a declared rule, default for an exception, the party among its switches, an `outweighs` on a colliding pair's act and ranks). `Side.gen_keys`, `superposed_elaboration`, `name_map` and the S2 wording's decision map read names from Lean's rows (the soft row, a candidate side's soft row, `generated_predicates`); the `"__"`-splitting of `outweighs` names is gone. `tools/relay_lint.py` forbids the soft decision prefix as well as the completion's, in literals and comments (read with `tokenize`) | `tests/test_relay_lint.py::test_probe_a2_no_readings_module_spells_a_soft_or_unsaid_name` (the probe's grep half); 5 new `::test_seeded_readings_modules[…]`; `tests/test_soft_decision_keys.py` (19 tests: Lean's keys, lookup, 16 one-fault and one two-fault mutants) | 812437cc |
| A2, part 2: the `CE4` fixtures C1 to C8 | `tests/ce4.py` builds `CE4` from the pinned translation (pilot commit `76922d6c`, kept byte for byte in `tests/data/ce4/` and checked against its git blob id; read back from the commit when the repository has it). C1 to C4 and C1.4 through Lean's readings route; C1 to C8 through `ve document load`, `check`, `render` and `readings --conclusion`; SC-8's generator run recorded (found for all eight ordered pairs) | `tests/test_readings_sd_ce4.py` (18 tests: `test_c1_to_c4_validate_separates_by_the_decision_alone[C1…C4]`, `test_c1_4_status_undecided_under_default_settled_no_under_strict`, `test_c1_to_c4_render_one_gap_sentence_on_each_separation_line[C1…C4]`, `test_c5_…`, `test_c6_…`, `test_c7_…`, `test_c8_…`, the generator and the pin) | 5019007c |
| Found while building C6 (class of B9/B12): the countermodel line read "e0 is classified as \"unsaid__denial_of_being_claude_permitted\"" | Filled tables were found only from `F_p` units, which the soft chain does not have. `readings_s1.Document` now reads them from Lean's filled environment (the predicates it adds, already bound by `_bind_completion`) on both chains | `tests/test_readings_sd_ce4.py::test_c6_the_denial_query_some_all_none` (asserts no reserved name in any line), `::test_the_filled_tables_are_those_leans_filled_environment_adds`; the norms chain's `tests/test_readings_nd_document.py` unchanged and passing | 5019007c |

PROBE A2 (`grep -rlq 76922d6c tests/ && ! grep -n 'soft__\|unsaid__' ve/readings*.py`): failed on 67edc98b (no
test names the pilot commit; 12 literals), exits 0 on 5019007c.

The recorded wire-gate input is committed after 5019007c, with this report. PROBE B3: as in the table.

The plan's C1 to C8 against what Lean answers (all *derived* expectations hold). R14: every row is a result about the
pilot's translation (`CE4`), not about the constitution's text. C5 reports no conflict; any conflict this route reports
about the constitution is a CANDIDATE (R14 source check pending: SC-9 external check, FOLLOW-UP) until an independent source check has run, and is never presented as a conflict in
the source (`tests/test_rd9_r14_candidates.py`).

| # | Plan | Observed |
| --- | --- | --- |
| C1, C3 | σ separates, witness `default` true, strict false; `SeparatedByDecisionOnly` with S1's wording rule; E14 with *should* / *shouldn't* | as planned; the finding carries ` (not certified)` (D5, E25 in force); one gap each, answered 'yes' |
| C2, C4 | σ separates, default false, strict true; C2's one gap sentence "whether c must seek clarification in s; … 'no'" | as planned, word for word |
| C1.4 | UNDECIDED under `default`, R7's sentence; SETTLED no under `strict` | as planned (`readings-choice`, `norm-defaults-status`) |
| C5 | 16 choices, each CONFLICT-FREE, `conditional_on: []` | as planned |
| C6 | SOME; ALL under `:0`; NONE under `:1` with the supposition and "… may directly deny being Claude; this situation answers 'yes'." | as planned, after the filled-table fix above |
| C7 | SOME; ALL under `force-u0036-s05:0` | as planned |
| C8 | the four units when C5's rows are decided and every premise status is `model` | Lean's premises answer: the four units; under an assumed reading, none. The conflict answer alone carries none on this path (its request sends no models, so the premise rows are not yet decided) |

### Seeded bugs (each restored)

| Seed | Language | Temporary change | Failing check |
| --- | --- | --- | --- |
| B3-M1 | Python | `soft_label` without the index bound | 9 tests of `test_readings_sd_relay.py`, the probe test among them |
| A2-M1 | Python | `SoftNormDocument` accepts every decision key | 8 of `test_soft_decision_keys.py::test_a_mutated_decision_key_is_unavailable[…]` and the two-fault test |
| A2-M2 | Lean | `keyedDecisions` writes a switch's key as `.off π N.name` (service rebuilt and pinned for the run, then restored) | `test_soft_decision_keys.py::test_every_decision_carries_leans_key`, `::test_the_relay_finds_each_name_by_its_key` (the relay refuses the row) |
| A2-M3 | Python | `superposed_elaboration` spells `"soft__excepted__" + …` again | `test_relay_lint.py::test_every_relayed_module_exists_and_passes`, `::test_every_readings_module_is_read_by_the_reserved_rule`, `::test_probe_a2_…` |
| CE4-M1 | Python | no filled table on the soft chain (the old behaviour) | `test_readings_sd_ce4.py::test_c6_the_denial_query_some_all_none` |

No Rust product code changed (Rust has no readings or soft-norms elaboration role).

### DRI rulings and open signatures

| Delta | Ruling and evidence |
| --- | --- |
| `key` on each `decisions` entry of the soft-norms elaboration row (and so of `rights-elaborate`) | SIGNED by standing ruling R3 (DRI-RULINGS.md): information added, nothing removed or renamed; the generated schema and its encoder theorem cover it; `test_every_decision_carries_leans_key` checks the field equals Lean's key; `test_a_mutated_decision_key_is_unavailable` binds it to the request |
| The relay refuses soft labels outside the request's conditions or Lean's pair order | No user-visible delta: only a tampered row changes (R8's binding) |
| Soft-chain English no longer names a filled table as an author fact | No delta against `main` (which refuses soft-completion documents); it restores spec 2.5 |
| Trusted Lean lines: K +0, S +171, trusted +531 against the signed baseline (+2 in this round: the `decisions` shape and `regeneratedCore`; `keyedDecisions` is tied by `keyedDecisions_names`, `DecisionKey`, `decisionKeyJson` and the `decision_key` shape are `[I]`) | **Needs DRI signature** with the earlier growth: R6 does not apply |
| Lean CPU: a soft-chain side's decision names now come from its soft row, and the S2 name map elaborates each default or switchable candidate's own side | Not measured in this round; S1 already elaborated every side it evaluates. For the gate's benchmarks (R4 needs the saved figures) |
| Earlier rounds' items (soft-chain documents answered, the rights-source certificate refusal, `normDefaults_wire_admission`'s hypothesis, `decided_units`, the gap selection, soft-label wording) | Unchanged: **still need DRI signatures** |

### Evidence

- `lake build`: PASS (900 jobs). `python3 lean/audit.py`: PASS (also inside the selected run).
- `tools/regen_generated.py --check`: every generated file fresh except `trust-tables` (the budget above).
- Selected tests (`select_tests.py --base $(git merge-base HEAD main) --run --jobs 8` on 5019007c) selected all 374
  units: the checker pin and `Audit.lean` changed. The run reached the one-hour foreground limit with 269 files
  finished, every one exit 0 (the builds, the audit and the layer checks passed first). The 104 files it had not
  finished ran by `pytest -n 8` on the same commit in two halves: 1,938 passed; 1,565 passed and one failed,
  `test_wire_gate_corpus.py::test_gate_corpus_holds_every_test_input_of_every_unit` (the new soft source of
  `test_soft_decision_keys.py` was not yet a recorded gate input). Its inputs were recorded (`python -m conformance.wire_contract_gate --record-test-inputs`, the test-inputs file
  only); that file and every `tests/test_wire_contract*.py` file then passed (355 passed).
- The release gate was not run, as this task requires.

### Still open

- DEFERRED as in the recheck: the DRI signatures above; the bounded statement re-check of `choiceLayeredG` and
  `ndTextWith`; the full gate on the final HEAD; SC-9's Sonnet comprehension check (C10) and external source check;
  C9 on the translation (SC-9).
- FOLLOW-UP: `soft_chain` (`readings_route.py`) still copies Lean's `chainOf`; Fable C1 to C7 and recheck C8 to
  C10. `python -m conformance.wire_contract_gate --record-test-inputs` on this commit rewrites the stored
  `soft-norms@0-gate.json` (last written 12481cac, 2026-10-03) with boundary problems such as
  `0:r0-guard-nodes: function record or message differs` (the relayed text carries `ResourceLimit: `, the record
  does not). No diagnostic changed in this round; the stored report is kept and only the test inputs are recorded.

## RD-9 final recheck and DRI conditions (2026-10-14)

F14 and F15 were reproduced before the fix (`DID NOT RAISE CheckerUnavailable`) and pass after it.
`docs/spec/rd-9-relay-binding.md` inventories every soft and rights elaboration field, its owner and binding test.
The soft binder checks the complete set of request-derived soft background labels, derived rule rows, layer labels,
rank identities and target identities. The rights binder checks limitation labels and the matching background; the
authored line identities, generated declaration keys, narrowing right/rule pairs and targets, and distinction hits.
Rule-reading bar rows are bound to their generated aimed predicates and their `over` rule names to elaborated lines.
The rights conflict path binds its displayed targets and conditional labels to the same bound elaboration. The mutation
matrix in `test_f14_each_soft_identity_field_is_bound`, `test_rights_elaboration_premise_identities_are_bound` and
`test_f15_rights_conflict_identities_are_bound` covers undeclared identities, duplicate and missing rows, and empty
targets. The follow-up reversed coherence label now fails binding; its former two-order allowance was seeded back,
failed the F14 mutation, and was restored. A seeded Python mutant that accepted extra soft labels failed the F14 regression and was restored. A second mutant that omitted the rights bar `over` binding failed
`test_rights_bar_nodes_are_bound_to_generated_aimed_predicates[undeclared bar over rule]` and was restored. A seeded
Lean mutant that negated the B3 soft-admission `#guard` failed `lake build VE.NormDefaults.Examples` at line 186 and
was restored.

The DRI's Task B conditions stand as follows:

| Item | Current evidence and disposition |
| --- | --- |
| B1 availability | Binding condition met by F11 to F15 regressions. The full gate and SC-9 external source check remain outside this requested test run. `soft_chain`/`chainOf` consolidation is scheduled for the next readings relay batch before merge; its acceptance test will compare all three chains' field presence and route against Lean. Do not mark B1 signed before those conditions. |
| B2 certificate kind | Soft source, not rights source; `test_missing_certificate_premises_has_the_norms_branch_text` pins the norms decoder's byte-identical refusal. Follow-up: AR-13 typed `InvalidInput` with path in Lean. |
| B3 admission theorem | `Run.lean` has a computed soft-source `#guard` whose `runCase` and `softCase` both succeed on a branch with `layeredRoute = soft-norms@0`. `normDefaults_wire_admissionX` remains a proved theorem. `python3 tools/lean_statements.py --diff` against merge base c9b8cba6 reports exactly one changed statement, `VE.NormDefaults.Run.normDefaults_wire_admission` (107 added and five removed declarations are separate). `mem_rows` retains its original statement via a generic helper. |
| B4 `choiceLayeredG hN` | Bounded independent statement recheck remains pending; this task forbids model calls. Do not sign before that review. |
| B5 `decided_units` | Signed by the item-specific DRI decision. `test_completion_decided_units_come_from_leans_folds` and the existing mutation tests bind the added field. |
| B6 gap selection | **Not claimed: the gap selection is not proved sound.** `coneEval_sound` and `coneEval_definite` are not in the audit. The new `test_unlisted_fnd_gap_flip_keeps_leans_witness_value` and `test_unlisted_ce4_gap_flips_keep_leans_witness_value` flip admissible unlisted completion atoms and compare Lean's displayed witness value for F-ND1, F-ND2, C2 and C4. F-ND1/F-ND2 goldens already retain each removed sentence. |
| B7 soft coherence wording | Keep unavailable. `test_a_verdict_on_a_soft_label_is_unavailable_until_its_sentence_exists` pins it. Wording follow-up: add one Lean-owned `VE.Words` sentence, W7 derivation gate and external comprehension check. |
| B8 trust | The regenerated inventory measures K +0, S +171, V +363, trusted +534 against the signed baseline, with unclassified 0. The per-file figures and ties pass below are saved here; a signed baseline allowance remains pending the bounded B4 review and final HEAD. No R6 claim. |
| B9 CPU | Final HEAD document and CE4 measurements remain due from the merge train's gate, which this task expressly forbids. No R4 claim without them. |

The B1, B4 and B8 rows above are superseded by the DRI's signatures recorded in "DRI signatures and conditions"
(2026-10-15) below.

The B8 trusted-line changes by file (including a negative move) are: `VE/Readings/Run.lean` +145,
`VE/Readings/VerdictsWire.lean` +69, `VE/NormDefaults/LayeredAdmission.lean` +54,
`VE/NormDefaults/Run.lean` +54, `VE/Readings/Verdicts.lean` +52, `VE/Readings/SoftWire.lean` +44,
`ResponseShape/Schemas/ReadingsRoute.lean` +30, `VE/Readings/ComponentsWire.lean` -29,
`VE/Readings/SoftVerdicts.lean` +24, `VE/Readings/SoftSeparate.lean` +20,
`VE/NormDefaults/Admission.lean` +17, `VE/NormDefaults/LayeredEntail.lean` +15,
`ResponseShape/Schemas/NormDefaults.lean` +14, `VE/Readings/UnspecifiedWire.lean` +12,
`VE/Readings/SoftDefaults.lean` +10, `ResponseShape/Schemas/SoftNorms.lean` +2, and
`VE/NormDefaults/Layered.lean` +1. The `tools/trust_map.py --seed` pass classified the new
soft admission witness as T. Placing that witness in `Run.lean` instead of `Examples.lean` adds three
G[V] boundary lines in the trust scanner, which are included in the +534 figure.

Ties pass: `keyedDecisions` remains tied to `keyedDecisions_names`. The table still has untied G[V]
declarations adjacent to proved wire or encoder theorems, including `NormDefaults.Admission.softCase`,
`Readings.Wire.admitSD`, `Readings.Run.runCase`, `Readings.Run.ndVerdictsAnswer`, and
`ResponseShape.Schemas.ReadingsRoute` shapes. A follow-up should tie each declaration only after
checking that the theorem states its full accepted behavior; no tie was added merely for proximity.

## F18 and response-binding audit (2026-10-14)

The current Python relay checks the schema and the request binding of every
identity/count it reads or displays. `docs/spec/rd-9-relay-binding.md` inventories
the fields. Lean still owns the ASTs, verdicts and diagnostic wording (R8).
The binding-audit review's rows 1–17 and 39–47 are covered by the common soft
binder and its soft-pairs, soft-conflict and admission callers; rows 18–38 and
the rights admission caller are covered by the rights binder. The probes mutate
genuine Lean rows, including coordinated removal of a pair and its labels.

| Finding | Fix | Regression | Commit |
| --- | --- | --- | --- |
| F18 | Each narrowing target equals `rule:mechanism`; referenced rules, parties and carve-out indices belong to the submitted source. Required request-implied mechanisms are present. | `test_f18_narrowing_mechanism_and_target_bind_to_authored_line`, `test_f18_extra_undeclared_mechanism_is_unavailable` | a7ba8c025, 7e6cdb201 |
| Binding audit 1–17, 39–47 | Bind prime predicates/profiles, decisions, pair membership and orientation, ranks, counts, targets, admission labels and the two auxiliary soft results. | `test_binding_audit_soft_fields_reject_forgery`, `test_binding_audit_pair_and_label_removed_together_is_unavailable`, `test_binding_audit_reversed_pair_and_label_together_is_unavailable` | a7ba8c025 |
| Binding audit 18–38 | Bind source line instances and node fields, generated keys/declarations, limitation labels, wordings, mechanism references, findings and exact bar membership. | `test_binding_audit_rights_fields_reject_forgery`, `test_binding_audit_rights_generated_name_swap_is_unavailable`, `test_f16_bar_rows_are_bound_to_elaboration` | a7ba8c025, 7e6cdb201 |

PROBE F18 failed before the fix with `DID NOT RAISE CheckerUnavailable`
and passed after it. Two seeded Python bugs were detected and restored:
`ve/softnorms.py` accepting an extra E′ predicate failed
`test_binding_audit_soft_fields_reject_forgery[prime extra predicate]`;
`ve/rights_route.py` accepting any mechanism reference failed
`test_f18_extra_undeclared_mechanism_is_unavailable[blockedBy absent]`.

The Task B dispositions above still apply. B1 requires the merge train's final
gate and SC-9 external source check; B4 requires the independent bounded
statement recheck; B8 requires signing the final-HEAD allowance; B9 requires
the saved CPU figures from the gate. This worker ran no model calls or release
gate, as directed. None of those four conditions is claimed signed here.

## F19–F21: exact prime, mechanism slots and generated rule ids (2026-10-14)

Each finding was a binding relation Python checked by membership where the
request fixes the exact value. All three are R8 (b) bindings; Lean output is
unchanged and no Lean or Rust product code changed (Rust has no rights relay).

| Finding | Class removed | Regression | Commit |
| --- | --- | --- | --- |
| F19 | The prime environment is the request plus exactly the bound declarations. One binder, `softnorms.bind_prime_environment`, now serves soft and rights: every field other than `vocabulary.predicates` equals the request, added names are disjoint, and each decision is declared with its key's argument sorts. | `test_f19_rights_prime_environment_is_the_request_plus_bound_declarations`, `test_f19_soft_prime_environment_is_the_request_plus_bound_declarations` | 19c42811b |
| F20 | A line's mechanism texts are matched against the slots of Correlate.lean `narrowings`, in order. Request-fixed slots (carve-outs as canonical `carve-out <i>`, `limitation`, `exception`, switches, `bar`) must be exact. Rule-named slots take only other direct rules, with the mode Lean filters on. Duplicates, `carve-out 01`, an unrequested `bar` or `exception`, self-references and reordering are all rejected. | `test_f20_mechanisms_are_exactly_the_request_implied_slots` | 19c42811b |
| F21 | Generated rule ids follow Tree.lean naming. A line's rule is its authored name or `rights-fan-<k>` (k-th fan-out instance in document order). A bar rule is `rights-bar-<i>` for its aimed predicate's index. | `test_f21_generated_rule_ids_follow_leans_naming` | 19c42811b |

PROBE F19, F20 and F21 (`/tmp/rd9_recheck.py`) each failed before the fix with
`DID NOT RAISE CheckerUnavailable` and pass after it. The probe's `audit` also
passes (F19–F21 PASS). Seeded bugs: restoring the pre-fix `ve/rights_route.py`
and `ve/softnorms.py` made 20 of the 29 new cases fail, for example
`[F19 decision declared with one argument]`, `[F20 duplicate carve-out 01]` and
`[F21 invented fan-out rule id]`. The other 9 were already rejected and stay as
class coverage. Selected tests (Mac runner, HEAD 19c42811b): 373 of 374 files
pass. The one failure is the known Mac-only
`test_question_reading.py::test_the_whole_question_is_bounded_by_the_modes_deadline`,
which passes on the VM rerun. `lake build` and `python3 lean/audit.py` pass.
The full gate was not run, as directed.

## F22, F23 and the binding-audit class: a schema-derived field inventory (2026-10-14)

F22 and F23 were fields that the audit had listed as "unused". The class is "a relayed field that no
binder names". The fix removes the class as well as the two examples.
`tests/test_relay_binding_inventory.py` walks the generated schemas of every relayed RD-9 answer:
soft elaborate, pairs, conflict, witness and admission, and rights elaborate, scope, bar, conflict,
witness and admission. Every field must be classified as bound or as Lean-derived with a reason
(`test_every_schema_field_is_classified`), so a field a Lean shape adds cannot go unclassified.
Every bound field is fuzzed with one-fault mutants on genuine answers of sixteen sources: renamed,
shifted, flipped, emptied, dropped, duplicated, extended and, when ordered, reversed. Each mutant
that still fits the schema must be `CheckerUnavailable` at the public relay
(`test_every_bound_field_mutant_is_unavailable[<route>]`). Each bound field must occur in some
genuine answer, or name the regression that covers it (`UNEXERCISED`, checked by
`test_unexercised_fields_name_existing_regressions`). `docs/spec/rd-9-relay-binding.md` now names
this inventory as the checked owner.

| Finding | Fix | Regression | Commit |
| --- | --- | --- | --- |
| F22 | Each conflict target's `sorts` must be its layer's declared argument sorts, or the obligation's for a declared `req->perm` pair (Norms/Replay.lean `targets`). The one soft binder serves both the soft and rights relays. | `test_f22_conflict_target_sorts_are_the_declared_argument_sorts[*]`, `test_every_bound_field_mutant_is_unavailable[soft-elaborate]`, `[rights-elaborate]` | f1795fed5 |
| F23 | A line's `holder_slot` is Tree.lean `holderSlot`: 0 for a liberty half, else the authored slot, else the first object slot of the right's holder sort. A null authored slot is the absent field. | `test_f23_an_authored_holder_slot_stays_the_lines_slot[*]`, inventory source "null optional fields" | f1795fed5, 11c67262a |
| Audit class: same gap in other fields | The sweep found more unbound fields and binds them. (1) Admission reports on all three admission relays use one binder, `admission.bind_report`: the exact ordered unfolding of the request graph (ClaimGraph.lean `Unfolds`). Before, this was graph membership only. (2) Bar nodes are strict, hard and negative with no carve-out (`barNode`). (3) A line node's carve-outs are the authored ones plus one pack exactly when in scope. (4) Elaboration `in_scope` follows `inScope`, and its licences use the scope's shared form check. (5) Mechanisms `exception M`, `blockedBy M` and `dominatedBy M` are the exact Correlate.lean `narrowings` lists. Before, any subset was accepted. (6) A distinction hit's `cited` is its line's guard citation. (7) The soft-conflict `budget` is the one sent, and its `conditional_on` holds open pairs only. (8) `overlaps`/`override_cycles` rows are refused, since no relay submits a witness. | `test_every_bound_field_mutant_is_unavailable[*]` (11 routes), `test_a_report_is_the_ordered_unfolding_of_the_request_graph`, `test_unrequested_witness_rows_are_unavailable`, `test_a_hit_cited_with_its_finding_dropped_is_unavailable` | ecc295e24, 11c67262a |

R8 applies to every row above as a (b) binding: no Lean answer changes and no user-visible delta
arises for a genuine answer. No standing ruling needed to be invoked. No Lean or Rust product code
changed: Rust relays none of these answers, and its only `conflict_targets` use is the evaluate
accelerator. The witness `target` was already bound by the schema's `x-equals`. A Python duplicate
of that check was added and then removed, keeping one owner.

PROBE F22 and PROBE F23 (`/tmp/rd9_362b17c_related.py`) each exited 1 before the fix, with
`unbound conflict-target sorts accepted: [('rights', ['ghost']), ('rights', []), ('rights',
['person', 'state']), ('soft', ['ghost']), ('soft', [])]` and `unbound holder slots accepted: [99,
0]`. Both exit 0 after it, and each is now a regression test (rows above).

Seeded bugs (Python only; no other language changed), each restored:
- Restoring the pre-fix `ve/softnorms.py`, `ve/rights_route.py`, `ve/soft_route.py` and `ve/admission.py` failed 17 of the new tests: all F22/F23 cases, five inventory routes, the witness-row test and the unfolding test.
- Single seeds:
  - Dropping the mechanism completeness check fails `[rights-elaborate]`.
  - Dropping the bar-node constants fails `[rights-elaborate]`.
  - Dropping elaboration `in_scope` fails `[rights-elaborate]`.
  - Dropping the `cited` binding fails `test_a_hit_cited_with_its_finding_dropped_is_unavailable`.
  - Dropping the budget binding fails `[soft-conflict]`.
  - Dropping the witness-row refusal fails `test_unrequested_witness_rows_are_unavailable`.
  - Dropping the unfolding comparison fails `test_a_report_is_the_ordered_unfolding_of_the_request_graph`.
  - Dropping the elaboration licence check fails `[rights-elaborate]`.
  - Treating a null `holder_slot` as present makes the genuine "null optional fields" source refused at recording.

Checks on HEAD 11c67262a:
- `lake build` (900 jobs) and `python3 lean/audit.py` (489 files, 5374 theorems) pass on ecc295e24. No Lean source changed after that commit.
- Selected tests: no Mac slot was free, so they ran on the VM; all 375 units were selected. 372 pass. The other 3 hit the runner's 3600 s per-file cap under the 6-job load: `test_assist.py`, `test_assist_invariants.py` and `test_english_evidence.py`. None of them touches the relays changed here, and on a rerun of just those three on the Mac runner (HEAD 11c67262a, 6 workers) they pass: 195 passed, 1 skipped (P5 materials not available), exit 0.
- An earlier selected run on ecc295e24 found the genuine-answer refusal fixed in 11c67262a (`test_compose_integration`, `test_norm_defaults_*`).
- The full gate was not run, as directed.

## F24 and its class: a licence that names no relation of the request (2026-10-15)

F24: a forged scope answer marked an uncited carve-out `cited`, dropped its UnlicensedLimitation finding
and set `licensed: true`, and Python accepted it. The licence check looked only at the licence's form.
The class is "a value that names a relation of the request (a citation, a colliding line, a strict rule)
and is checked only for its form". The fuzz missed it because a one-fault mutant only ever renamed a
value to "ghost", never to another valid value.

| Finding | Fix | Regression | Commit |
| --- | --- | --- | --- |
| F24 | The rights elaboration binder now checks each `(mechanism, licence)` pair against Run.lean `licence`: the first relation of Scope.lean that the request holds. In order: a citation (`cited`, over `citesOf` and `lineKeys`), a right line of the opposite effect (`rightCollision`, which for dominance also needs a cited rank), a same-effect strict rule (`sameEffectStrict`), else none. A scope licence must equal the elaboration's licence. The one exception is `certified`, accepted only where the elaboration left the mechanism unlicensed and certificates were sent. This also closes the follow-up "`certified` passes on any mechanism". The form-only `_licence_bound` is deleted. For the class: the inventory fuzz now also sets each bound scalar to every value the same field takes in another genuine answer. A new test replays each source's genuine answer as the answer to every other source of its family. That is a whole, self-consistent forgery, the shape F24 took. Twelve sources were added, one for each licence and its uncited twin, including a fan-out line cited through its source norm. | `test_f24_a_licence_names_a_relation_the_request_holds[*]` (14 cases), `test_another_requests_genuine_answer_is_unavailable[*]` (11 routes), `test_every_bound_field_mutant_is_unavailable[rights-elaborate]`, `[rights-scope]` | 0b8015d14 |

R8(b) covers this: a licence is a choice that names a relation of the request. No Lean answer changes,
and no genuine answer is refused. All 25 genuine rights sources still pass at recording: the 13 earlier ones and
the 12 new ones, which between them carry every licence (`cited`, `collision`,
`effect delivered by strict rule M`, `limitation`, `bar` and none).
No Lean or Rust product code changed, and Rust relays no licence. DRI note under the deferred D1 item: the
licence is now one more Lean derivation that Python follows, the same as the mechanism list (F20). It
reads only request relations, and its source is named in `_narrowings`.

PROBE F24 (`/tmp/rd9_a264_probe.py F24`): exit 1 before the fix (`scope: uncited carve-out licensed as
"cited", finding dropped -> ACCEPTED`), exit 0 after it (`-> REJECTED`). The probe is the
`F24 uncited carve-out as 'cited' in rights-scope` case of the regression test.

Seeded bugs (Python only), each restored:
- Restoring the pre-fix `ve/rights_route.py`:
  - fails 5 of the 14 F24 cases (every `cited` forgery and both "cited carve-out unlicensed" cases);
  - fails `test_every_bound_field_mutant_is_unavailable[rights-elaborate]` and `[rights-scope]` (licence set to `cited` or `collision`);
  - fails `test_another_requests_genuine_answer_is_unavailable[rights-elaborate]` and `[rights-scope]` (for example "cited carve-out answered for carve-out").
- Ignoring the carve-out citation, dropping the cited-rank condition of a dominance collision, dropping the same-effect test, or leaving out the source norm from `lineKeys`: each makes a genuine source refused at recording (`CheckerUnavailable: ... unbound narrowing target or mechanism`), so the inventory tests error.
- Not tying the scope licence to the elaboration fails `test_every_bound_field_mutant_is_unavailable[rights-scope]`.

Checks on HEAD 0b8015d14:
- `lake build` passes (900 jobs, no Lean source changed), and so does `python3 lean/audit.py` (489 files, 5374 theorems).
- Selected tests ran on the Mac runner (ve-mac-1). All 375 units were selected; 1 test failed: `test_question_reading.py::test_the_whole_question_is_bounded_by_the_modes_deadline`. That test also fails on this VM, and it fails the same way on the unchanged base a264e8893 with the same built binaries. It exercises `english.question`, not a rights relay, so it is unrelated to F24.
- `tools/regen_generated.py --check`: `gate-collection` is regenerated. `trust-tables` still fails. That failure was already there: trusted Lean growth in `VE/Readings/*` and `VE/NormDefaults/*` (S +171, V +363) with no signed allowance. This fix changed no Lean.
- The full gate was not run, as directed.

## DRI signatures and conditions (2026-10-15)

Review `manage-agents/reviews/rd-9-conditions-gap-20261015.md` (F25 to F28) against the DRI's decisions in
`manage-agents/reviews/rd-9-dri-signatures-20261015.md`. F25 and F26 meet B1's open conditions; F27 records the
signatures as decided (not re-decided). F28 is a C note. No model calls or push were made.

| Finding | Fix | Regression tests | Commit |
| --- | --- | --- | --- |
| F25 (B1(d)): `readings_route.soft_chain` recomputed Lean's `Compose.dispatch`/`chainOf` and decided `soft_premises` presence | Lean names the chain a completion took: `filled.chain` (`Readings.Chain.text`, written by `UnspecifiedWire.filledJson` and `Run.filledJsonS` from the admitted environment's chain; the `filled` shape requires it, `chainText_fits` proves it fits). The relay reads it: the completion fields present must be exactly that chain's (`COMPLETION_FIELDS`), and the request must declare `norm-defaults@0` and the chain's profile (`CHAIN_PROFILES`). `soft_chain` is deleted; no binder of the completion reads a chain profile to decide presence. Class: a relay that decides which fields a Lean row carries from its own copy of a Lean dispatch | `tests/test_rd9_chain_relay.py`: `test_probe_f25_python_holds_no_copy_of_the_chain_derivation`, `test_field_presence_and_route_are_leans_on_every_chain[norms, soft, rights]` (acceptance, against Lean), `test_the_rights_chain_beside_norm_defaults_is_leans_refusal`, `test_a_forged_chain_is_refused[*]` (14 forgeries on validate and elaborate rows), `test_a_chain_the_request_does_not_declare_is_refused` (two faults) | 35204a970 |
| F26 (B1(c), R14): a constitution conflict must not be presented as a conflict in the source before an independent source check | No rd-9 report, spec, docstring or golden stated a `CE4` conflict as real (C5 answers CONFLICT-FREE on all 16 choices). The reports (this one's C1 to C8 table, `DELTA.md`), spec 8.4 and the `CE4` tests' docstring now say that every `CE4` result is about the pilot's translation and that any conflict reported about the constitution is a CANDIDATE (R14 source check pending: SC-9 external check, FOLLOW-UP). A scan makes the class fail closed. Answers are unchanged | `tests/test_rd9_r14_candidates.py`: `test_the_reports_and_specs_label_every_constitution_conflict`, `test_the_ce4_goldens_and_docstrings_label_every_constitution_conflict`, `test_probe_f26_the_rd9_reports_record_r14`, `test_the_scan_flags_exactly_unlabelled_source_conflicts[*]`, `test_a_golden_that_asserts_a_ce4_conflict_needs_the_label` | 1b650d615 |
| F27: record the signatures | (a) the trust growth's signed entry in `docs/trust-baseline.json`, itemised per file and class and re-measured on this round's final tree (below); (b) the D1 exception, with `_narrowings`' lines cited and its expiry in its docstring; (c) B4's two declarations moved from `PENDING` to `SIGNED` in `tools/check_rd9_sc1_statements.py`, each as the approved text with exactly its one edit; (d) B1 and B8 | `tests/test_rd9_dri_signatures.py`; `tests/test_rd9_statements.py::test_probe_f27_the_signed_declarations_are_no_longer_pending`, `::test_a_signed_declaration_still_fails_on_any_other_difference[*]`, `::test_a_signed_edit_that_no_longer_applies_fails` | the F27 commit (this section's) |
| F28 (C) | Not changed: the branch lacks main's dccd9cf5; its Mac gate failure `test_question_reading.py::test_the_whole_question_is_bounded_by_the_modes_deadline` is in main-known-red territory and that test is not edited. The merge train's candidate gate on main plus this branch is the authority | — | — |

### Decision table (signed 2026-10-15)

| Item | Signature | Evidence |
| --- | --- | --- |
| Trust growth (B8 trust, B9) | **SIGNED WITH CONDITION** by the DRI (item 1): K 997, S 9,959, V 37,526 measured with `tools/trust_map.py` on the final tree of this round; against the signed baseline K +0, S +171, V +372 (V +363 at 67d0cb31, plus F25's V +9). Itemised per file and class in `DELTA.md` and in the signed entry of `docs/trust-baseline.json`. FOLLOW-UP: a ties pass binding these lines to the existing render, wire and encoder theorems | `trust_map.py --check` PASS; `tests/test_rd9_dri_signatures.py::test_the_trust_entry_is_signed_and_itemised` |
| D1 exception, `ve/rights_route.py:23-89` `_narrowings` (F24's licence derivation at lines 45, 56-63 and 67-88; the binder's call at 313-317) | **GRANTED, time-boxed to 2026-10-22** (item 2). It expires when the FOLLOW-UP infra item **rights-licence-relay** merges: Lean returns the licences and Python relays them | `tests/test_rd9_dri_signatures.py::test_the_d1_exception_cites_narrowings_lines` |
| B4 (`choiceLayeredG` gains `hN`; `ndTextWith` builds `free N.D` once) | **SIGNED** (item 3; bounded re-check PASS, `manage-agents/reviews/rd-9-b4-recheck.md`) | `tools/check_rd9_sc1_statements.py` prints no `PENDING re-review` |
| B1 (soft-completion availability) | **SIGNED once the full gate passes on the final HEAD** (item 3): (a) F11 met earlier; (c) F26; (d) F25. (b) the full gate is the merge train's branch verify; it was not run in this round (task instruction) | as F25 and F26 |
| B8 (gap selection) | **SIGNED** (item 3): "Not claimed" stated (B6 row above, spec 8) with the flip tests `tests/test_rd9_gap_relay.py::test_unlisted_fnd_gap_flip_keeps_leans_witness_value`, `::test_unlisted_ce4_gap_flips_keep_leans_witness_value` | — |
| SC-9 external and comprehension checks | FOLLOW-UP (DRI), not blocking | — |


### Probes

- PROBE F25 (`! grep -n 'def soft_chain' ve/readings_route.py`): failed on 67d0cb317 (`def soft_chain` at line 37),
  passes from 35204a970; test `test_rd9_chain_relay.py::test_probe_f25_python_holds_no_copy_of_the_chain_derivation`.
- PROBE F26 (`grep -rn -i 'R14' docs/rd-9 docs/readings-defaults/rd9-lean | grep -q -i candidate`): failed on
  67d0cb317 (no R14 line), passes from 1b650d615; test `test_rd9_r14_candidates.py::test_probe_f26_the_rd9_reports_record_r14`.
- PROBE F27 (`regen_generated.py --check && ! check_rd9_sc1_statements.py | grep -q 'PENDING re-review'`): failed on
  67d0cb317 (`trust-tables`: S +171, V +363 unsigned; two `PENDING re-review` lines), passes on 98f97159e with the
  virtual environment's `python3` first on `PATH` (the system `python3` has no pytest, which the
  `assurance-manifest` check runs); tests `test_rd9_statements.py::test_probe_f27_the_signed_declarations_are_no_longer_pending`
  and `test_rd9_dri_signatures.py`.

### Seeded bugs (each restored)

| Seed | Language | Temporary change | Failing check |
| --- | --- | --- | --- |
| F25-M1 | Python | the relay ignores the chain: soft fields required iff `soft_premises` is present | `test_rd9_chain_relay.py::test_a_forged_chain_is_refused[soft-named norms]`, `[soft-soft fields dropped]` |
| F25-M2 | Python | the soft chain derived again from the request's profiles (`soft_chain`'s body) | `test_rd9_chain_relay.py::test_probe_f25_python_holds_no_copy_of_the_chain_derivation` |
| F25-M3 | Lean | `Run.filledJsonS` names the norms chain (`Chain.norms.text`); `ve_service` rebuilt and pinned for the run, then restored | `test_rd9_chain_relay.py::test_field_presence_and_route_are_leans_on_every_chain[soft]`, `::test_a_forged_chain_is_refused[soft-soft fields dropped]`, `test_readings_sd_relay.py::test_genuine_soft_rows_pass_the_relay` and two mutation tests (the relay refuses Lean's genuine soft rows) |
| F26-M1 | report | the C5 row of this report states the conflict verdict on the constitution, without the label | `test_rd9_r14_candidates.py::test_the_reports_and_specs_label_every_constitution_conflict` |
| F27-M1 | Python | `signed_edits` skips an edit that no longer applies instead of failing | `test_rd9_statements.py::test_a_signed_edit_that_no_longer_applies_fails` |
| F27-M2 | Python | a line inserted above `_narrowings` (the cited range goes stale) | `test_rd9_dri_signatures.py::test_the_d1_exception_cites_narrowings_lines` |

No Rust product code changed, so no Rust seed.

### Evidence on 98f97159e

- `lake build`: PASS (900 jobs). `python3 lean/audit.py`: PASS, 489 source files, 5,375 named theorems, standard
  axioms only.
- `tools/regen_generated.py --check`: PASS, 25 entries (trust-tables: K +0, S +0, V +0 against the new baseline).
- Selected tests on the Mac runner (ve-mac-1, `mac-pytest.sh --select`, base `git merge-base HEAD main`): all 378
  units selected; 377 passed. One test failed: `tests/test_question_reading.py::test_the_whole_question_is_bounded_by_the_modes_deadline`,
  the F28 test, which fails the same way on the unchanged base a264e8893 (F24 section above) and which main fixes at
  dccd9cf5; not edited here (F28).
- The full gate was not run (task instruction). B1's signature waits on it.
