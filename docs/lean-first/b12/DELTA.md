# Lean-first batch 12: environments, models, and the profile gate

## Implementation and deletion ledger

Lean's `environment` and `model` service modes now validate every authored
profile envelope before Python constructs `Environment` or `FiniteModel`.
The service uses the composed profile dispatch and batch 2's persistent
content-addressed request handles. Python binds the accepted identities from
Lean's rows. Generated search environments remain internal to the search
generator and are checked again when a witness is reported.

| Removed Python decision | Lean owner or retained boundary |
|---|---|
| `profiles.checker_family`, `route_gate`, and `require_checker` profile and route refusals | `VE.Compose.todayGate` and `dispatch`, reached by `VE.Service.Standalone.validatedComposedEnvironment` |
| `Environment._decode` declaration, profile block, reference, limit, and metadata refusals | `VE.Service.Standalone.validatedComposedEnvironment` and the selected Risk, Alternatives, SpeechActs, Reports, Time, Readings, Rights, SoftNorms, NormDefaults, or core decoder |
| Environment identity answer | `VE.Service.Standalone.environmentCase`; Python compares its constructed identity and binds Lean's ID |
| `FiniteModel._decode` shape, domain, tuple, limit, and background refusals | `VE.Service.Standalone.modelCase`, its family model decoder, and `VE.Norms.Plain.profileOk` |
| Model identity answer and claimed-ID checks | `VE.Service.Standalone.modelCase`; Python binds Lean's `model_id` |
| `validation.decided` for environment and model validation | `validation.construct_after_lean`; `decided` remains for other surfaces scheduled in later batches |

The route vocabulary decoder now carries a `validNames` witness, including
well-formed, distinct, and dependency-safe names. The norm-defaults model
projection reads `unspecified` as its `deny` placeholder for model checking,
while identity remains bound to the submitted envelope. The signed DRI ruling
on the act word `no` is applied in Lean. A test-only copy of the old Python
profile gate remains as the frozen oracle under the DRI's retention decision.

- [x] DRI §8.1, per-batch corpus evidence: `test_delta_numbers_are_regenerated_from_evidence`.
- [x] DRI §8.3, Lean's text is canonical: `test_a_lean_only_rejection_carries_leans_diagnostic`.
- [x] DRI §8.4, the A/B recorder: `test_probe_record_excludes_nested_instrumentation`.
- [x] DRI §8.6, signed act-word `no`: `test_k1_lean_rejects_the_act_phrase_word_no`.
- [x] DRI §8.7, frozen Python oracle: `test_all_registered_subsets`.
- [x] DRI §8.8, generated soft-norms contract: `test_fixtures_records_and_legacy_agreement`.

`tools/semantic_inventory.py` was regenerated after deleting the Python gate;
the deleted symbols have no production consumers. `tools/relay_lint.py` passes.

## Gate evidence

The source recordings and complete classified changes are in
[`evidence/delta.json`](evidence/delta.json) and the four `*-compare.json`
files. Each comparison replays against that listing with zero unlisted
changes. All accepted outputs and identities are preserved. The repaired
model diagnostics retain every frozen `path`; the remaining 22 text pairs
describe wording only, across 1086 wording records. There are 0 order records,
0 verdict records, and 0 availability records.

Fault order is deterministic: the envelope and profile gate run before the
vocabulary decoder. Vocabulary shape, limits, and declaration names are
checked before sort references, in sort, predicate, then constant order.
Model fields, completeness, table shapes, limits, domains, constants, and
relations are checked in that order, with pointers carried at each failure.

Latency uses the historical readings-bearing UDHR translation at
`pilot/udhr-20261003T0600Z:usecases/udhr-pilot/run-20261003T0600Z/translation.ve.md`
(SHA-256 recorded in `evidence/latency.json`). Base and head ran alternately
three times. The eligibility harness ran once per side with `--no-write`.
Both pairs returned byte-identical output. An initial short translation from
the 2026-10-06 pilot lacked `readings@1`; it was excluded from the UDHR gate
measurement because it exercised a different, much smaller workload.

<!-- BEGIN GENERATED: python docs/lean-first/b12/report.py --write -->
| Corpus | Records per side | Same | Wording | Order | Verdict | Availability |
|---|---:|---:|---:|---:|---:|---:|
| conformance | 39,612 | 39,566 | 46 | 0 | 0 | 0 |
| probe | 18,870 | 17,830 | 1,040 | 0 | 0 | 0 |
| profiles | 35,713 | 35,713 | 0 | 0 | 0 | 0 |
| pilots | 294 | 294 | 0 | 0 | 0 | 0 |
| **All** | **94,489** | **93,403** | **1,086** | **0** | **0** | **0** |

Code lines (base to head): production Python +223/−790 (net -567); Lean +697/−88 (net +609).
Differential fuzz: 15 runs (CI and 14 date seeds); baseline 331 → 273; 0 head-only new signatures; 0 head entries not reproduced.
First-pass date-seed review found 24 distinct head-only signatures.
UDHR: base 54.679 s → head 54.651 s; 0.999× wall; 1.000× child CPU; output identical; budget pass.
Eligibility: base 342.496 s → head 355.024 s; 1.037× wall; 1.263× child CPU; output identical; budget pass.
Eligibility isolated Lean CPU: base 331.740 s → head 351.730 s; 1.060×; output identical; budget pass.
Full gate: passed; 11,655 passed, 7 skipped, 0 failures.
<!-- END GENERATED -->

The reviewed differential baseline's environment entries are replayed by
`test_reviewed_environment_findings_have_one_python_lean_diagnostic`: every
current Python and Lean `(outcome, code, text)` agrees. The baseline keeps
Rust and later-batch route discrepancies with their existing follow-up IDs.
The final baseline has 273 entries against 331 at the batch base. The CI sample
and all 14 date seeds have zero head-only signatures and reproduce every head
entry. The follow-up review groups request model and decoder codes under DF-7
and DF-9, dependency order under DF-8, Rust envelope differences under DF-4
and DF-19, and norm-defaults wire phase differences under DF-13 and DF-20.
The original latency harness measures process-tree child CPU, including Rust.
The separate [`lean-cpu.json`](evidence/lean-cpu.json) uses four full eligibility
runs in alternating base/head and head/base order. It records all 14 Lean
service processes per run before shutdown, with raw counters and identical
stdout in `evidence/lean-cpu-*.jsonl` and `eligibility-*.log`. Median Lean CPU
is 331.74 s base and 351.73 s head (1.060×); median wall is 306.09 s base and
329.92 s head (1.078×). Both budgets pass. The individual CPU values varied
substantially with host load (264–399 s base, 266–438 s head), so the paired
medians are the reported measure.

## Seeded failures

Each bug was planted in this batch's code, made its named test fail, then
removed. The first three used isolated worktrees; the last three were
temporarily planted and restored in this worktree. All six tests pass after
restoration; the logs are in `evidence/mutant-*.log` and
`evidence/mutants-restored*.log`.

| Seeded bug | Test that failed |
|---|---|
| Bypass Lean in `validated_environment` | `test_a_lean_only_rejection_carries_leans_diagnostic` |
| Replace the bound Lean model ID with zeroes | `test_model_identity_is_bound_from_leans_answer` |
| Include the route observer in public probe records | `test_probe_record_excludes_nested_instrumentation` |
| Preserve a null rights recognition on the restricted Lean wire | `test_phi_null_recognition_is_the_absent_field` |
| Send a rights-profile source through the composed environment gate on the soft route | `test_soft_route_alone_refuses_rights_profile` |
| Apply the binary-flag precheck to unspecified norm defaults | `test_u1_claude_settled_no_and_sol_undecided` |

## Acceptance ownership

| Item | Owner | State |
|---|---|---|
| Build, frozen-source check, corpus comparison, fuzzer replay, latency, full suite, and deletion inventory | AGENT | Evidence above and in the committed gate JSON |
| Signature for the 22 wording pairs and empty order block | HUMAN — DRI | Signed by orchestrator, 2026-10-07, against `evidence/delta.json` |
| Model diagnostic error shapes | AGENT | All frozen paths and diagnostic classes restored; zero verdict records |
| Eligibility Lean CPU budget | AGENT | Isolated full-harness median is 1.060×; raw service counters in `evidence/lean-cpu-*.jsonl` |
| Operational soak after batch 13b | EXTERNAL — lead/DRI | Deferred by the plan; not a batch-12 acceptance item |

Plan §5.1's DRI ruling in `lf-12-review.final.md` signs wording only where
quoted names, paths, and specificity survive. The re-recorded delta satisfies
those conditions. `test_dri_signed_every_batch_12_delta_record` binds the
approval in `evidence/signoff.json` to the exact delta digest.

### DRI signature record

- [x] Wording and order block: 22 text pairs, 1086 wording records, and
  0 order records. DRI: orchestrator; date: 2026-10-07; decision: approved
  under `lf-12-review.final.md` §5.1 item 2 after the path and name repairs.
- [x] Verdict-shape records: zero; the model and budget paths are retained.
