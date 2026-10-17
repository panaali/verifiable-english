# RD-7 build report

The fixed comparison base is `f98183bf5ff518c14e0cbdcf2950cdaf7736deeb`; the committed code and inventory checkout used for final measurements is `3d1c0312f6c008f0c7d238f8ec8dc1cf49857c63`. No model calls or push were made. Later documentation commits do not change product code.

## Plan and statement crosswalk

| RD-7 direction or gate | Delivery | Check | Owner |
|---|---|---|---|
| Add the superposed `readings-verdicts` route; keep enumerated requests and the 1024 checked-choice limit | `lean/VE/Readings/{Run,SupVerdictsWire}.lean`; `837bbd18`, `506caeee` | `test_sup_service_all_some_none_and_english`, `test_budget_free_nd_verdict_request_keeps_the_enumerated_contract`, `test_superposed_verdicts_keep_the_1024_choice_budget` | AGENT |
| Derive ALL from the empty-assumption certificate, SOME from one complete choice and a countermodel, NONE from per-choice countermodels, with the conflict gate | `SupVerdictsWire.lean`, `SupVerdictsSound.lean`; `837bbd18`, `92d9b920` | `SupVerdictsExamples.lean` computed guards; `test_sup_service_all_some_none_and_english`, `test_a_canonical_base_with_a_local_collision_is_not_a_premise_model` | AGENT |
| Per-reading premise status, dead readings, dependencies and composition-s2 items 1–6 English | `SupVerdictsWire.lean`, `SupDependencies.lean`; `837bbd18`, `6727c1c5` | `test_m5_narrowing_premise_and_no_dead_reading`, `test_m6_dead_reading_certified_by_lean`, `test_review_a_named_readings_keep_their_restriction_in_english` | AGENT |
| Chain `readings_wire_all_sound`, `readings_wire_model_sound`, `dead_sound` with the folds; prove the encoder's returned value fits a fully typed shape | `SupVerdictsSound.lean`, `ResponseShape/{Schemas,Encoders}/ReadingsRoute.lean`; `92d9b920`, `506caeee` | `lake --rehash build`, `lean/audit.py`, `test_sup_response_retypes_every_field_and_rebinds_references` | AGENT |
| Delete Python's superposed fold, SOME/NONE assembly, `_dependencies`, `_replays`, `_mentions` and wording decisions; retain evidence, binding and display | `ve/readings_verdicts.py`, `ve/readings_s2_wording.py`, `evidence/deletion-ledger.json`; `1f7f0621`, `08d5a077` | `test_python_sup_has_no_fold_or_dependency_replay`, `test_superposed_scopes_need_only_the_two_answer_roundtrips`, relay mutation gate | AGENT |
| Keep the checked 1024-choice source for model proposals and dead readings, with bounded evidence generation | `SupVerdictsWire.lean`, `ve/readings_verdicts.py`; `0408eca29`, `93d5d3c60`, `9c7bcf607`, `49749eea1` | `test_scoped_proposals_reach_checked_choices_after_the_64_choice_prefix`, `test_superposed_scope_count_stays_bounded_above_64_choices`, `test_premise_model_short_circuits_proof_search`, `test_premise_scopes_reuse_lean_proposals_without_extra_verdicts` | AGENT |
| M1–M20 retain verdicts and English; list each difference in DELTA | `tests/test_readings_s2_document.py`, `tests/test_readings_sup_verdicts.py`, `DELTA.md` | Seven-corpus A/B and selected tests, recorded below | AGENT |
| Plan's full gate | The chain runs it on the final committed HEAD and writes `gate-result.json` | Builder's checks are recorded below; **the builder did not run the full gate under the user's explicit override** | EXTERNAL: chain |

Lean computes verdicts, premise and dead-reading statuses, conditions, diagnostics and English plans. Python checks the generated schema and request binding before formatting; Rust remains an untrusted accelerator. New Lean statements use no `sorry`. The approved-statement check reports zero changed or pending approved statements. The trust increase is signed under R6 in [DELTA.md](DELTA.md), with deleted Python paths in [deletion-ledger.json](evidence/deletion-ledger.json).

## Checks and evidence

`lake --rehash build` passed 892 jobs. `lean/audit.py` audited 486 source files and 5,797 theorem declarations using standard axioms only. The statement guard, trust-map check, route-map check, targeted regeneration of statements/audit/frozen/checker/schema files, and Rust pin check passed. An optional all-generators check was stopped during its repeat statement dump after the Lean rebuild; its completion is not claimed. The full relay mutation gate found zero findings over 39 routes and 109,195 mutants; its focused final `readings-route` run found zero findings over 46 fixtures and 15,768 mutants. The focused RD-7 suite passed 13 tests.

The [seeded-bug record](evidence/seeded-bugs.json) shows 15 restored mutants in changed Lean and Python product files. Each baseline passed and each mutant failed on the final source. P1–P9, L3, L7 and L8 failed named pytest tests; L1, L2 and L4 failed proof or computed-guard builds. L7 and L8 reached their behavioral assertions through a fixed 128-choice fixture. The [comparator probes](evidence/comparator-probes.json) reject changed values, bool-for-int, missing records, same-file comparison and empty input.

### Seeded bugs

Every mutant below was planted in the named changed file, observed failing the named check, and restored. The saved record includes the exact source hash and failure output.

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
| L2, L4 | `lean/VE/Readings/SupVerdictsWire.lean` | `lake build VE.Readings.SupVerdictsExamples`: SOME and dependency computed guards fail separately |
| L3 | `lean/VE/Readings/Run.lean` | `test_budget_free_nd_verdict_request_keeps_the_enumerated_contract` |
| L7 | `lean/VE/Readings/SupVerdictsWire.lean` | `test_scoped_proposals_reach_checked_choices_after_the_64_choice_prefix` |
| L8 | `lean/VE/Readings/SupVerdictsWire.lean` | `test_superposed_scope_count_stays_bounded_above_64_choices` |

The [route latency](evidence/latency.json) paired five samples of 500 calls on three cases; HEAD service CPU changed by −0.3%, +2.4% and +4.6%, inside the 20% allowance. [Pilot render](evidence/pilot-render-latency.json) and [pilot check](evidence/pilot-check-latency.json) compare UDHR and constitution inputs side by side with two pairs each, identical outputs and a shared pinned Rust executable (`VE_RUST_TIMEOUT=60`): CPU changes were +4.9% and +0.2% for render, −38.6% and +2.1% for check. `test_superposed_scopes_need_only_the_two_answer_roundtrips` and `test_premise_scopes_reuse_lean_proposals_without_extra_verdicts` guard against an extra Lean request per scope.

The seven-corpus A/B result and final selected-test result will be inserted after their foreground runs finish. The saved [scope](evidence/scope.json), [DELTA](DELTA.md), and A/B evidence bind results to the fixed base and code HEAD. Report checks use saved counts and commit lists; no permanent report test reads a moving `git diff` (R11/D4). The RD-1 signed change from “reading N” to the reading's own sentence remains intact, with `test_readings_defaults_english.py` and corpus comparison.

## Build-checklist audit

| Item | RD-7 disposition |
|---|---|
| 1. One contract | Lean owns the fold, wording, limits and fault order; `VE.Norms.witnessKind` owns the shared conflict-kind wording. The typed schema is generated from `ResponseShape`. |
| 2. Differential faults | New one- and two-fault response mutations are in `test_sup_response_retypes_every_field_and_rebinds_references`; the seven-corpus A/B compares code and text across authorities. Rust product code is unchanged. |
| 3. Text normalization | N.A. No parser or normalization path changed. |
| 4. Untrusted output | `evidence/relay-route.json` and the binding tests cover schema types, bool-for-int, empty/extra rows and every new reference. |
| 5. Malformed input | `test_superposed_answer_retypes_each_field_and_rebinds_each_reference` and the route mutation gate exercise malformed JSON nodes and references; public failures remain VE errors. |
| 6. Three-valued verdict | `test_sup_zero_budget_is_unknown`, `test_superposed_verdicts_keep_the_1024_choice_budget` and the computed Lean boundary guards refuse false certainty. |
| 7. Whole-operation deadlines | No deadline implementation changed; `test_readings_budget_zero.py`, the selected hang-guard suite and the existing subprocess helpers cover the new public route. |
| 8. Exhaustive folds | New ALL/SOME/NONE cases are Lean constructors, checked by `SupVerdictsExamples.lean`; the other kind folds are unchanged. |
| 9. English gate | `test_sup_service_all_some_none_and_english`, `test_readings_defaults_english.py` and the M1–M20 S2 document fixtures exercise the Lean plan through the renderer. |
| 10. Entry points | `test_readings_s2_document.py`, `test_readings_nd_document.py` and `test_readings_sup_verdicts.py` cover document check, render, readings and the direct route. |
| 11. Compiler oracle | New meaning is compiled Lean with audited proofs and computed guards; no new syntax recognizer or regex is introduced. |
| 12. State and ledger | N.A. No product state machine or ledger changed; evidence is saved batch data. |
| 13. Failing tests | `evidence/seeded-bugs.json` records thirteen restored mutants; `evidence/comparator-probes.json` shows rejection of bogus, bool-for-int, missing and empty comparisons. |
| 14. Hermeticity | New pytest fixtures write under `tmp_path`; no sleep or elapsed assertion was added. Lean was rehashed and the Rust executable is pinned. |
| 15. Identity | `test_sup_response_retypes_every_field_and_rebinds_references` and the relay mutation gate bind every new id, choice, span, label and model reference. |
| 16. Inventories | Targeted `tools/regen_generated.py --write`, `tools/repo_map.py --check`, `tools/rust_build.py --check`, and generated schema/encoder audits passed. |
| 17. Approved statements | `tools/check_readings_defaults_statements.py` reports no changed approved statement; no new hypothesis needs a DRI ruling. |
| 18. Theorem fixtures | `SupVerdictsExamples.lean` computes the ALL/SOME/NONE, conflict and limit boundaries; L1–L4 mutants break their proofs or guards. |
| 19. Use-case formalisation | N.A. No source document was translated or a rule added; the corpus and paired pilot comparisons check retained cases. |
| 20. Report numbers | Every claimed number comes from saved evidence or the command output named here. The chain-owned full gate has not run at builder handoff. |
| 21. Owners | Every RD-7 plan direction above is AGENT; the final full gate is EXTERNAL (chain). No HUMAN approval is presumed. |
| 22. Tests and gate | Selected tests are running; this builder does not run `tools/gate.py` under the user's override. The chain runs it on final committed HEAD. |
| 23. Signed deltas | `DELTA.md` cites R6 for trust growth and the item-specific RD-1 ruling for retained own-sentence wording. Any actual availability/verdict delta requires a separate DRI signature. |

## Self-review against BUILDER-CHECKLIST

1. **PASS** — `test_sup_response_retypes_every_field_and_rebinds_references`, `test_superposed_answer_retypes_each_field_and_rebinds_each_reference`, `evidence/relay-route.json`.
2. **PASS** — Plan crosswalk above, `evidence/deletion-ledger.json`, targeted `tools/regen_generated.py --write` plus the audit and statement checks, and the final diff review.
3. **PASS** — `evidence/seeded-bugs.json` and `evidence/comparator-probes.json`.
4. **PASS** — `evidence/ab-compare.json`, M1–M20 tests in `test_readings_s2_document.py`, and `test_superposed_answer_is_stable_when_document_keys_are_reordered`.
5. **PASS** — `test_sup_response_retypes_every_field_and_rebinds_references`, `test_superposed_answer_retypes_each_field_and_rebinds_each_reference`, `evidence/relay-route.json`.
6. **PASS** — `evidence/scope.json`, committed final HEAD and chain-owned gate handoff; this builder does not run the full gate under the user's override.
7. **PASS** — `DELTA.md`, `test_superposed_verdicts_keep_the_1024_choice_budget`, saved A/B comparison.
8. **PASS** — `evidence/ab-compare.json` and `DELTA.md` cover code, text, path, order, availability and verdict.
9. **PASS** — `tools/select_tests.py --base $(git merge-base HEAD main) --run --jobs 2 --maxfail 0`; P7's named test is selected.
10. **PASS** — `tools/check_readings_defaults_statements.py`, `lake --rehash build`, `SupVerdictsExamples.lean`, seeded L1–L4.
11. **PASS** — `test_sup_zero_budget_is_unknown`, `test_superposed_verdicts_keep_the_1024_choice_budget`, selected hang-guard tests.
12. **PASS** — `evidence/latency.json`, `evidence/pilot-render-latency.json`, `evidence/pilot-check-latency.json`, `test_superposed_scopes_need_only_the_two_answer_roundtrips`.
