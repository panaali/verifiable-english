# Lean-first batch 5: risk and alternatives

Base `9aaf918d`; head is this batch's final commit. Scope: risk and alternatives block validation, alternatives coverage, and risk-first admission. [Deletion ledger](LEDGER.md) maps the removed decision sites to Lean.

## Ownership

`Environment` calls `alt-elaborate` or `risk-elaborate` before materialising an envelope with either block. `VE.Alternatives.Wire` owns the reserved wording check and coverage fold. `VE.Risk.Wire` owns risk block acceptance and the W6 canonical round trip. `ve.alternatives.run_case` and `ve.risk.run_case` only relay raw cases. Risk admission calls the risk route first, including for W6 environments. The Rust risk evaluator and its conformance-only route kinds are deleted; the Lean risk-eval versus brute-force test remains.

## Gate evidence

The A/B recorder covered the Stage-0 probes, conformance corpus, discourse and readings corpora, and every historical pilot document: [corpus-ab.json](corpus-ab.json) records 66,247 paired results. 66,246 were identical. The one remaining record is the historical constitution-pilot readings document, unavailable on both base and head at the recorder's 600-second limit; [delta.json](delta.json) gives its reason. There are no wording, order, verdict, or one-sided availability differences. No verdict or availability difference is accepted without the DRI's signature.

The CI differential-fuzz sample produced no new signatures in the [head report](difffuzz-head-ci.json). Its reviewed baseline shrank from 384 entries in the [base report](difffuzz-base-ci.json) to 358 (26 findings fixed by removing the duplicate paths). The [14 date-seed A/B result](difffuzz-14-seeds.json) has zero head-only signatures; the base had 682 unbaselined signatures summed over seeds and the head had 606. Both checkouts ran their own locked builds; [difffuzz_ab.py](difffuzz_ab.py) reproduces the run. Summed Python and child CPU across the 14 runs was 4,858.3 s base and 4,837.2 s head; this is total fuzzer CPU, not isolated Lean CPU.

`tools/gate.py` runs the full hermetic Lean build and audit, reproducible Rust build and tests, and Python suite on the committed clean head. It writes the machine-readable result to the ignored root `gate-result.json`; the handoff cites that result directly.

Source delta against `9aaf918d` from `git diff --numstat`: 197 Lean source lines added, 9 deleted; 417 `ve/` Python source lines deleted, 47 added; 1,038 Rust source lines deleted, 2 added. This is 1,464 source lines deleted across the three languages, excluding tests, generated schemas, manifests, and report data. The removed Rust evaluator accounts for 1,002 of those lines.

Latency sample: [latency_bench.py](latency_bench.py) constructed the same accepted environment 100 times per profile in each checkout, with one warm-up, on a host with load average 47–53. In the adjacent base/head pair, alternatives took 0.286/0.880 s wall; risk took 0.581/0.813 s wall. The head's Lean service consumed 0.09/0.23 s CPU for the 100 calls (0.9/2.3 ms per call); base construction makes no Lean service call. The loaded-host wall readings vary and do not establish the section-4 quiet-host wall bound. The batch adds one Lean validation call to each construction; it is not a speed batch.

## Mutant checks

Each temporary bug was applied to changed source in a disposable worktree at `22b6db1c`, caused a targeted pytest failure, and was removed. `git diff --exit-code` confirmed that worktree's tracked source matched HEAD afterward:

| Seeded bug | Test that failed | Observed failure |
|---|---|---|
| Skip the Lean alternatives/risk validation call in `Environment._decode` | `test_block_rejections[AlternativesReserved: wording]` | Did not raise `VEError`; 12 rejections failed |
| Replace the Lean coverage section with `{}` in `ve.document.coverage` | `test_coverage_names_declared_alternatives_and_counterfactual_support` | Missing `alternatives_declared` |
| Send risk admission to the alternatives route in `ve.admission` | `test_risk_admission_calls_risk_owner` | Lean rejected risk fields on the wrong route |
| Accept Boolean values as residual counts in the generated coverage response schema | `test_coverage_response_shape_rejects_dropped_and_boolean_counts` | Did not raise `Invalid` |

## Checklist scope

The batch changes no English parser, state machine, ledger, theorem statement, use-case formalisation or scientific report. Those checklist items are outside this batch. The gate evidence covers diagnostics and fault order, malformed inputs, response schema, identity and counts, registry coverage, source statements, mutants, hermetic builds and the full suite.

| Acceptance item | Tag | Owner and disposition |
|---|---|---|
| Lean block validation, coverage, admission routing, and duplicate deletion | **AGENT** | Builder; checked by the source ledger, focused tests, mutants and full gate. |
| Corpus preservation and differential fuzz baseline | **AGENT** | Builder; identical paired results except the listed paired unavailability, baseline shrunk. |
| Verdict or one-sided availability changes | **HUMAN** | DRI; none occurred, so no signature is requested or inferred. |
| Historical constitution-pilot readings timeout | **EXTERNAL** | Pilot throughput owner (the plan's readings optimisation track); recorded in `delta.json` as unavailable on both sides, deferred from this batch. |
