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
changes. The conformance, profile, and pilot corpora preserve all accepted
outputs and identities. The probe verdict class contains only the four
`MAX_ENTITIES` and `MAX_TUPLES` error-shape records (both authorities): Lean's
error omits the old `path` field. The seven distinct wording pairs and all
fault-order records are listed in the same delta file.

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
| conformance | 39,612 | 39,560 | 8 | 44 | 0 | 0 |
| probe | 18,870 | 17,600 | 710 | 556 | 4 | 0 |
| profiles | 35,713 | 35,713 | 0 | 0 | 0 | 0 |
| pilots | 294 | 294 | 0 | 0 | 0 | 0 |
| **All** | **94,489** | **93,167** | **718** | **600** | **4** | **0** |

Code lines (base to head): production Python +204/−789 (net -585); Lean +128/−23 (net +105).
Differential fuzz: 15 runs (CI and 14 date seeds); baseline 331 → 252; 0 head-only new signatures; 0 head entries not reproduced.
Date-seed review added 24 distinct signatures before the confirming run.
UDHR: base 54.679 s → head 54.651 s; 0.999× wall; 1.000× child CPU; output identical; budget pass.
Eligibility: base 342.496 s → head 355.024 s; 1.037× wall; 1.263× child CPU; output identical; budget pass.
Full gate: pending committed HEAD run.
<!-- END GENERATED -->

The reviewed differential baseline's environment entries are replayed by
`test_reviewed_environment_findings_have_one_python_lean_diagnostic`: every
current Python and Lean `(outcome, code, text)` agrees. The baseline keeps
Rust and later-batch route discrepancies with their existing follow-up IDs.
The latency harness measures process-tree child CPU; it does not isolate Lean
CPU from Rust CPU. Eligibility's aggregate child CPU rose 26.3%; the section-4
Lean-only CPU item needs either an isolated measurement within its 20% budget
or a DRI-signed exception. The wall latency item is within 1.25×.

## Seeded failures

Each bug was planted in an isolated worktree at this batch's code, made its
named test fail, then was removed. The three tests pass together after
restoration; the logs are in `evidence/mutant-*.log` and
`evidence/mutants-restored.log`.

| Seeded bug | Test that failed |
|---|---|
| Bypass Lean in `validated_environment` | `test_a_lean_only_rejection_carries_leans_diagnostic` |
| Replace the bound Lean model ID with zeroes | `test_model_identity_is_bound_from_leans_answer` |
| Include the route observer in public probe records | `test_probe_record_excludes_nested_instrumentation` |

## Acceptance ownership

| Item | Owner | State |
|---|---|---|
| Build, frozen-source check, corpus comparison, fuzzer replay, latency, full suite, and deletion inventory | AGENT | Evidence above and in the committed gate JSON |
| One signature for the seven wording pairs and fault-order block | HUMAN — DRI | Pending review of `evidence/delta.json` |
| Four model-budget error-shape verdict records | HUMAN — DRI | Pending individual signatures on the two cases for each authority |
| Eligibility Lean CPU budget if isolated measurement exceeds 1.20× | HUMAN — DRI | Aggregate child CPU is 1.263×; isolation pending |
| Operational soak after batch 13b | EXTERNAL — lead/DRI | Deferred by the plan; not a batch-12 acceptance item |

The human signatures are required by plan §5.1. Listing these changes does
not supply the signatures.

### DRI signature record

- [ ] Wording and order block: the 7 text pairs, 718 wording records, and
  600 order records in `evidence/delta.json`. DRI, date, and decision: ___
- [ ] `probe/lean`, `MAX_ENTITIES`: rejected with the same `ResourceLimit`
  code, but the old `/domains/item` path is absent. DRI, date, and decision: ___
- [ ] `probe/python`, `MAX_ENTITIES`: same path change. DRI, date, and decision: ___
- [ ] `probe/lean`, `MAX_TUPLES`: rejected with the same `ResourceLimit`
  code, but the old `/relations` path is absent. DRI, date, and decision: ___
- [ ] `probe/python`, `MAX_TUPLES`: same path change. DRI, date, and decision: ___
