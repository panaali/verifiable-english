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
