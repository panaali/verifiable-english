Status: code complete; the selected run's three own-code failures pass on targeted rerun; release gate belongs to the chain.
HEAD: d27b2e77c (final code fix); this report's commit is the branch's final HEAD; baseline: 73b77383a.
Changed: component choice elaborations use one `rows()` batch; the service pool has a load-aware size cap.
Open: `iso.sh` could not connect to the user systemd bus, so timing used `nice -n 15`; no DRI signature needed.
DELTA: none; F-C17's batched and serial document JSON and injected refusal agree.

# Scale choice batch

## Delivery

| Acceptance item | Owner | Commit and evidence |
|---|---|---|
| Batch every component's filled-choice elaboration in component and choice order | AGENT | a57a58ad9, d27b2e77c; `test_component_choice_elaborations_are_one_relay_batch` |
| Keep answer bytes, order and refusal behavior | AGENT | a57a58ad9, d27b2e77c; `test_batched_and_serial_choice_elaboration_have_identical_document_answers`, `test_a_refused_choice_in_the_batch_fails_as_it_did_alone`, `test_budget_zero_every_verdict_op_is_unknown[F-ND1]` |
| Size the pool from available vCPUs and one-minute load, with a default of two and one documented setting | AGENT | a57a58ad9, d27b2e77c; `test_service_pool_size_setting_uses_spare_vcpus_and_clamps`, `test_every_int_conversion_in_ve_is_bounded_or_reviewed`, `docs/spec/lean-service.md` |
| No Lean change, no trust increase, no meaning change | AGENT | `git diff main...HEAD -- lean/` empty; `tools/trust_map.py --check` reports K/S/D/G/trusted +0; no DELTA rows |
| Before and after measurement on the same VM tree | AGENT | 73b77383a and a57a58ad9; `before.json`, `after.json` |
| Final release gate | EXTERNAL | Deferred to the chain on committed final HEAD, as requested |

The input was the saved `prefix-50.ve.md` from the 2026-10-28 scale report's growth table: 64 units, three main reading sets and four companion sets. The VM's one-minute load exceeded 32 at baseline, so this is a readings-only report timing on that prefix. A literal prefix through Article 3 has 27 units and zero reading sets, so it cannot measure choice batching; the 50% prefix is the first saved growth-table input with several choices. Both runs used the same document and measurement script, with the same built Lean and Rust checkers. The source tree changed only by the batching and pool code between runs; the explicit pool setting was unset, so both runs had the default two services. `iso.sh exp-scale-choice-batch 24G -- ...` failed before launching with `Failed to connect to bus: No data available`. Both runs therefore used `nice -n 15` in this workspace. No external AI model calls were made.

| Reading report | Wall s | Python CPU s | Lean CPU s | 1-min load start → end | Readings-route requests | All service requests |
|---|---:|---:|---:|---|---|---:|
| Serial | 82.241 | 7.954 | 55.460 | 54.75 → 58.27 | 18 × 1 case | 1,141 |
| Batched | 30.432 | 5.673 | 34.230 | 28.05 → 27.60 | 2 × 1 case, 2 × 8 cases | 1,127 |

Both reports returned `CONFLICT-FREE`. The 2.70× wall ratio is confounded by the large load change; it is not a controlled throughput estimate. CPU columns measure the Python process and the Lean service requests respectively; Rust subprocess CPU is not included. The requests show that the 16 choice elaborations became two eight-case service requests, while the two other readings-route calls remained single-case.

## Seeded bugs

Each temporary code fault was restored before commit. These are test failures, not build or hash failures.

| Changed product file and planted fault | Failing test |
|---|---|
| `ve/readings_components.py`: skip prefetch, restoring six serial elaborations on F-C17 | `test_component_choice_elaborations_are_one_relay_batch` |
| `ve/readings_components.py`: reverse the rows assigned to choices | `test_batched_and_serial_choice_elaboration_have_identical_document_answers` |
| `ve/backends/relay.py`: return a constant pool size of two | `test_service_pool_size_setting_uses_spare_vcpus_and_clamps` |
| `ve/readings_verdicts/choice.py`: accept an inner Lean refusal | `test_a_refused_choice_in_the_batch_fails_as_it_did_alone` |

## Checklist coverage

Build-checklist items 1–3, 5–12, 15–19 do not add new contracts to this transport-only change: Lean meanings, schema generation, input decoders, normalization, budgets, English, state machines, and proof statements are unchanged. Item 4 is covered by the existing `test_readings_components_lean`, `test_readings_components_load`, and `test_relay_mutation_gate`: `rows()` remains the typed and request-bound relay. Item 13 is the four seeded failures above. Item 14 uses `tmp_path` in the new tests; no sleeps or network calls were added. Item 16 uses no new inventory. Item 20's numbers come from the saved measurement JSON, not a moving Git diff. Item 21 is the delivery table. Item 22: the selected Mac run on a57a58ad9 ran 488 test units; three test IDs failed on new code, and the targeted rerun of those same IDs passed on d27b2e77c's uncommitted snapshot. The final gate is delegated to the chain. Item 23 has no user-visible DELTA row. No tests were removed or renamed.

## Self-review against BUILDER-CHECKLIST

1. PASS — `test_readings_components_lean` and `test_relay_mutation_gate` cover typed, bound responses before the pool returns them.
2. PASS — delivery table above ties each task item to a commit and test; `git diff --stat main...HEAD` reviewed.
3. PASS — four seeded bugs above each failed its named test and were restored.
4. PASS — `test_batched_and_serial_choice_elaboration_have_identical_document_answers` compares full JSON on F-C17.
5. PASS — `test_readings_components_lean` and `test_readings_components_load` fuzz request binding for these unchanged answer shapes.
6. N.A. — the chain runs the final-HEAD full gate; this builder was directed not to run it.
7. PASS — no DELTA rows and trust +0 from `tools/trust_map.py --check`.
8. PASS — F-C17's serial and batched document JSON and refusal test match; no user-visible delta observed.
9. PASS — the selected runner includes `tests/test_readings_components_document.py` and `tests/test_relay.py`.
10. N.A. — no Lean source or theorem changed.
11. N.A. — no semantic budget or deadline changed; pool sizing test covers its new resource bound.
12. PASS — `before.json`, `after.json`, and `test_component_choice_elaborations_are_one_relay_batch` measure cost and guard request count.
13. N.A. — no test was removed or renamed.
