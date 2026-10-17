# RD-7 build report

The comparison base is `f98183bf5ff518c14e0cbdcf2950cdaf7736deeb`, the branch's merge base with main. The code head
is `074f96d3fca99843b6c0208bcb9c0aedb8410b25`: the corpus A/B, the route latency and the selected tests ran on it
(tree `441d892a`). The commits after it change only `docs/readings-defaults/rd7/` (evidence, DELTA and this report),
and the pilot latency was measured at one of them, `70b3a2bb`. No model calls were made and nothing was pushed.

## Plan and statement crosswalk

| RD-7 direction or gate | Delivery | Check | Owner |
|---|---|---|---|
| Add the superposed `readings-verdicts` route; keep enumerated requests and the 1024 checked-choice limit | `lean/VE/Readings/{Run,SupRun,SupVerdictsWire}.lean` | `test_sup_service_all_some_none_and_english`, `test_budget_free_nd_verdict_request_keeps_the_enumerated_contract`, `test_superposed_verdicts_keep_the_1024_choice_budget` | AGENT |
| Derive ALL from the empty-assumption certificate, SOME from one complete choice and a countermodel, NONE from per-choice countermodels, with the conflict gate | `SupVerdictsWire.lean`, `SupVerdictsSound.lean` | `SupVerdictsExamples.lean` computed guards; `test_sup_service_all_some_none_and_english`, `test_a_canonical_base_with_a_local_collision_is_not_a_premise_model` | AGENT |
| Per-reading premise status, dead readings, dependencies and the English for composition-s2 2.3 items 1–6 | `SupVerdictsWire.lean`, `SupDependencies.lean`, `VE/Norms/WitnessKind.lean` | `test_m5_narrowing_premise_and_no_dead_reading`, `test_m6_dead_reading_certified_by_lean`, `test_review_a_named_readings_keep_their_restriction_in_english` | AGENT |
| Chain `readings_wire_all_sound`, `readings_wire_model_sound` and `dead_sound` with the folds; prove the encoder's value fits a fully typed shape | `SupVerdictsSound.lean` (`readings_wire_sup_verdicts_all`, `_some`, `_none`, `_premises_model`, `_dead`, `_nd_all`, `_nd_counter`); `ResponseShape/{Schemas,Encoders}/ReadingsRoute.lean` | `lake build`, `lean/audit.py`, `test_sup_response_retypes_every_field_and_rebinds_references` | AGENT |
| Delete Python's superposed fold, SOME/NONE assembly, `_dependencies`, `_replays`, `_mentions` and the wording selection; keep evidence generation, binding and display | `ve/readings_verdicts.py`, `ve/readings_s2_wording.py`, `ve/readings_route.py`, [deletion-ledger.json](evidence/deletion-ledger.json) | `test_python_sup_has_no_fold_or_dependency_replay`, `test_superposed_scopes_need_only_the_two_answer_roundtrips`, relay mutation gate | AGENT |
| Model proposals and dead readings from the checked 1024-choice set, with bounded evidence generation | `SupVerdictsWire.lean` (`firstSupProposals`), `ve/readings_verdicts.py` | `test_scoped_proposals_reach_checked_choices_after_the_64_choice_prefix`, `test_superposed_scope_count_stays_bounded_above_64_choices`, `test_premise_model_short_circuits_proof_search`, `test_premise_scopes_reuse_lean_proposals_without_extra_verdicts` | AGENT |
| M1–M20 keep their verdicts and English; every difference in DELTA | `tests/test_readings_s2_document.py`, `tests/test_readings_sup_verdicts.py`, [DELTA.md](DELTA.md) | corpus A/B below | AGENT |
| Plan's full gate | The chain runs `tools/gate.py` on the final committed HEAD and writes `gate-result.json` | The builder did not run the full gate: the task assigns it to the chain | EXTERNAL: chain |

Lean computes the verdicts, premise and dead-reading statuses, conditions, diagnostics, limits and English plans.
Python checks the generated schema and binds the answer to the request before formatting it (R8). Rust product code
is unchanged. No new Lean statement uses `sorry`. The statement spec has no approved RD-7 block: the plan puts RD-7's
statement review before its own build. `tools/check_readings_defaults_statements.py` reports zero changed and zero
pending statements for the batches it holds. The trust increase is signed under R6 in [DELTA.md](DELTA.md).

## Checks and evidence

- **Lean.** `lake build` passed with 892 jobs. `python3 lean/audit.py` passed: 486 source files and 5,797 named
  theorem declarations, standard axioms only. No added line in `lean/` contains `sorry` or `admit`.
- **Inventories.** `tools/regen_generated.py --check` checked all 23 entries as fresh. `tools/repo_map.py --check`
  passed for 32 modes. `tools/trust_map.py --check` passed (K +0, S +0 against the signed allowances).
  `tools/rust_build.py --check` passed: the Rust binary is pinned. The rebuilt `ve_service` hash is in
  `lean/checkers.lock`.
- **Relay.** The full relay mutation gate ([relay-gate.json](evidence/relay-gate.json)) found zero findings over 39
  routes and 109,195 mutants. The focused `readings-route` run ([relay-route.json](evidence/relay-route.json)) found
  zero over 46 fixtures and 15,768 mutants. Both were recorded after the last product commit (`d51d23f5`), and their
  input hashes match the current files.
- **Corpus A/B** ([ab-compare.json](evidence/ab-compare.json), [DELTA.md](DELTA.md)). It covered 100,401 records:
  100,383 identical, 7 wording rows that differ only in the recorder's scratch path, and 11 unavailable on both
  sides (R7), with 0 unlisted. No verdict, order or availability changed. The four whole-UDHR documents in the
  pilots are unavailable on both sides. The three older ones were rerun one at a time
  ([udhr-serial.json](evidence/udhr-serial.json)): each run took 11–18 min and 18–30 GB, and gave the same
  CheckerUnavailable on base and head. `python -m tools.evidence ab` still reports the unavailable-on-both rows: it
  refuses them as evidence of preservation, and they are not counted as preserved.
- **Selected tests.** `select_tests.py --base $(git merge-base HEAD main) --run` ran 374 units on tree `441d892a`
  (the code head). The one failure is
  `tests/test_readings_defaults_rd8_report.py::test_review_fix_commit_chain_and_final_gate_target`. It is listed in
  main-known-red.txt and pre-existing on main. The branch leaves that file as it is at the merge base.
- **Latency** (20% allowance, all pass).
  - [Route latency](evidence/latency.json) (`tools/readings_batch_latency.py`, 5 pairs × 100 warm calls per case,
    load average 21): Lean CPU per call changed by +11.9%, −2.7% and −3.1%.
  - [Pilot render](evidence/pilot-render-latency.json): +2.2% (UDHR) and +3.1% (constitution).
  - [Pilot check](evidence/pilot-check-latency.json): −2.7% and −5.7%.
  - Both pilot measurements used one shared pinned Rust binary and `VE_RUST_TIMEOUT=60`, and gave identical outputs
    on each side. `test_superposed_scopes_need_only_the_two_answer_roundtrips` and
    `test_premise_scopes_reuse_lean_proposals_without_extra_verdicts` guard against an extra Lean request per scope.
- **Wording.** RD-1's signed change from "reading N" to the reading's own sentence is intact
  (`test_readings_defaults_english.py`, identical readings and pilot corpora).

### Seeded bugs

[mutants.json](evidence/mutants.json) holds 17 mutants. [seeded-bugs.json](evidence/seeded-bugs.json) records every
one replayed with `python -m tools.evidence mutants` on the current sources (each `source_sha256` is the committed
file's hash). In each case the baseline passed, the mutant failed and the file was restored. After the Lean mutants,
`lake build` restored the pinned `ve_service`. P8, L6 and L7 were re-aimed at the current code: the scope loop now
prepares conflict evidence, the budget counts `checked`, and the proposals use `firstSupProposals`. Their claims are
unchanged.

| Mutant | File | Failing check |
|---|---|---|
| P1 | `ve/readings_verdicts.py` | `test_missing_proof_scope_cannot_hide_behind_a_reindexed_model` |
| P2 | `ve/readings_s2_wording.py` | `test_sup_service_all_some_none_and_english` |
| P3, P4 | `ve/readings_route.py` | `test_superposed_answer_retypes_each_field_and_rebinds_each_reference` (each separately) |
| P5 | `ve/readings_verdicts.py` | `test_public_conflict_keeps_service_envelope_private` |
| P6 | `ve/readings_verdicts.py` | `test_superposed_verdicts_keep_the_1024_choice_budget` |
| P7 | `ve/readings_verdicts.py` | `test_superposed_scopes_need_only_the_two_answer_roundtrips` |
| P8 | `ve/readings_verdicts.py` | `test_premise_model_short_circuits_proof_search` |
| P9 | `ve/readings_verdicts.py` | `test_premise_scopes_reuse_lean_proposals_without_extra_verdicts` |
| L1 | `lean/VE/Readings/SupDependencies.lean` | `lake env lean VE/Readings/SupDependencies.lean`: `supDependencies_replay` fails |
| L2, L4 | `lean/VE/Readings/SupVerdictsWire.lean` | `lake build VE.Readings.SupVerdictsExamples`: the SOME guard (line 32) and the dependency guard (line 35) fail separately |
| L3 | `lean/VE/Readings/Run.lean` | `test_budget_free_nd_verdict_request_keeps_the_enumerated_contract` |
| L5, L8 | `lean/VE/Readings/SupVerdictsWire.lean` | `test_superposed_scope_count_stays_bounded_above_64_choices` (each separately) |
| L6 | `lean/VE/Readings/SupVerdictsWire.lean` | `test_superposed_verdicts_keep_the_1024_choice_budget` |
| L7 | `lean/VE/Readings/SupVerdictsWire.lean` | `test_scoped_proposals_reach_checked_choices_after_the_64_choice_prefix` |

The [comparator probes](evidence/comparator-probes.json) show the A/B comparator rejecting changed values,
bool-for-int, missing records, the same file given twice and empty input.

## Build-checklist audit

| Item | RD-7 disposition |
|---|---|
| 1. One contract | Lean owns the fold, wording, limits and fault order; `VE.Norms.witnessKind` owns the shared conflict-kind wording. The typed schema is generated from `ResponseShape`. |
| 2. Differential faults | `test_sup_response_retypes_every_field_and_rebinds_references` adds one- and two-fault response mutations. The corpus A/B compares Lean and Python authorities on the probe, conformance and quantity corpora. Rust product code is unchanged. |
| 3. Text normalization | N.A. No parser or normalization path changed. |
| 4. Untrusted output | `evidence/relay-route.json` and the binding tests cover schema types, bool-for-int, empty and extra rows, and every new reference. |
| 5. Malformed input | `test_superposed_answer_retypes_each_field_and_rebinds_each_reference` and the route mutation gate exercise malformed JSON nodes and references. Public failures stay VE errors. |
| 6. Three-valued verdict | `test_sup_zero_budget_is_unknown`, `test_superposed_verdicts_keep_the_1024_choice_budget` and the computed Lean boundary guards refuse false certainty. |
| 7. Whole-operation deadlines | No deadline code changed. `test_readings_budget_zero.py`, the selected hang-guard tests and the subprocess helpers cover the new route. |
| 8. Exhaustive folds | The ALL/SOME/NONE cases are Lean constructors, checked by `SupVerdictsExamples.lean`. |
| 9. English gate | `test_sup_service_all_some_none_and_english`, `test_readings_defaults_english.py` and the M1–M20 S2 fixtures run the Lean plan through the renderer. |
| 10. Entry points | `test_readings_s2_document.py`, `test_readings_nd_document.py` and `test_readings_sup_verdicts.py` cover document check, render, readings and the direct route. |
| 11. Compiler oracle | The new meaning is compiled Lean with audited proofs and computed guards. No syntax recognizer or regex is added. |
| 12. State and ledger | N.A. No product state machine or ledger changed. |
| 13. Failing tests | 17 seeded mutants, all killed on the current sources; comparator probes (above). |
| 14. Hermeticity | New fixtures write under `tmp_path`, with no sleeps or elapsed-time asserts. The Lean and Rust binaries are pinned. |
| 15. Identity | `test_sup_response_retypes_every_field_and_rebinds_references` and the relay mutation gate bind every new id, choice, span, label and model reference. |
| 16. Inventories | `tools/regen_generated.py --check` (23 entries), `tools/repo_map.py --check` and `tools/rust_build.py --check` pass. |
| 17. Approved statements | `tools/check_readings_defaults_statements.py`: no changed or pending approved statement. The spec has no RD-7 block (see the crosswalk). |
| 18. Theorem fixtures | `SupVerdictsExamples.lean` computes the ALL/SOME/NONE, dependency, conflict and limit boundaries; L1, L2 and L4 break them. |
| 19. Use-case formalisation | N.A. No source document was translated and no rule was added. |
| 20. Report numbers | Every number here comes from the saved evidence files named beside it. Under D4, no new permanent report test reads a moving `git diff`. |
| 21. Owners | Every plan direction is AGENT. The final full gate is EXTERNAL (the chain). |
| 22. Tests and gate | The selected tests ran on the code head (above). The builder does not run `tools/gate.py`: the chain runs it on the final committed HEAD. |
| 23. Signed deltas | `DELTA.md`: R6 (trust), R7 (unavailable on both sides), and RD-1's item ruling (retained wording). No row needs a new DRI signature. |

## Self-review against BUILDER-CHECKLIST

1. **PASS** — `test_sup_response_retypes_every_field_and_rebinds_references`, `test_superposed_answer_retypes_each_field_and_rebinds_each_reference`, `evidence/relay-route.json`.
2. **PASS** — the crosswalk above, `evidence/deletion-ledger.json`, `tools/regen_generated.py --check`, `lean/audit.py`.
3. **PASS** — `evidence/seeded-bugs.json` (17 of 17 killed on current sources), `evidence/comparator-probes.json`.
4. **PASS** — `evidence/ab-compare.json` (Lean and Python authorities identical), M1–M20 in `test_readings_s2_document.py`, `test_superposed_answer_is_stable_when_document_keys_are_reordered`.
5. **PASS** — `test_sup_response_retypes_every_field_and_rebinds_references`, `test_superposed_answer_retypes_each_field_and_rebinds_each_reference`, `evidence/relay-route.json`.
6. **PASS** — the A/B and route latency ran on the code head `074f96d3`, and later commits are docs only. The chain gates the final HEAD.
7. **PASS** — `DELTA.md` has no unsigned row (`review-ready.py --delta-dri-needed`: none).
8. **PASS** — `DELTA.md` lists every A/B difference by class, with `evidence/ab-delta.json`.
9. **PASS** — `select_tests.py --base $(git merge-base HEAD main) --run` selected 374 units, including every named mutant test.
10. **PASS** — `lake build`, `lean/audit.py`, `SupVerdictsExamples.lean`, seeded L1, L2 and L4.
11. **PASS** — `test_sup_zero_budget_is_unknown`, `test_superposed_verdicts_keep_the_1024_choice_budget` (L6), the selected hang-guard tests.
12. **PASS** — `evidence/latency.json`, `evidence/pilot-render-latency.json`, `evidence/pilot-check-latency.json`, `test_superposed_scopes_need_only_the_two_answer_roundtrips`. Whole-UDHR peak memory shows no consistent change (base 21.9, 20.3 and 29.6 GB; head 22.1, 23.1 and 17.8 GB; `evidence/udhr-serial.json`).
13. **PASS** — the three removed tests each carry a `Test-removed` trailer in the branch's commits.
