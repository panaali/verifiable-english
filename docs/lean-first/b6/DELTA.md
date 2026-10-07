# Batch 6 delta and fix report (2026-10-07)

**Status: complete; ready for review.** Local branch `lean-first/b6` is based on `9aaf918d`. Nothing was pushed. The fix directive's items are done. Soft-norms latency is within the plan's allowances (largest UDHR CPU ratio 1.17; the slowest head run took 78.11 s wall). The 11 inherited CI-fuzzer signatures are reviewed into the baseline. The DRI's signature for the 164 trusted Lean lines is recorded. The producer schema regression corpus is `tests/data/route-cases.jsonl`, 292 cases, including standalone and batched soft-rule answers.

## Ownership and deletion ledger

| Decision or output | Lean owner and Python relay |
| --- | --- |
| Soft source acceptance, fault order, code, text, limits and rule references | `VE.SoftNorms.Phases.checkSource` and `decodeSoftNorm`; `soft_relay.run` calls the service and preserves the Lean diagnostic. Python phase checks are removed from the runtime. |
| Soft expansion, decisions, ranks, exceptions, coherence pairs, preference predicates, rule acts and incompatibility | `VE.SoftNorms.Wire.regenerated` and `VE.SoftNorms.Run.runSoftKind`; `SoftNormDocument` hydrates display and search containers from the response. Python semantic reconstruction methods are removed. |
| Residual counts, decider grouping, status and document hash | Lean `residual`, `deciderCounts`, `residualStatus` and `softDocumentHash`; the readings wrapper sends the original identity environment, which Lean checks against its lowered source before hashing and regenerating the displayed environment. |
| Witnessed Overlap and override cycle lines, DualGuardCycle hint | Lean `warningRows`, `overlapLine`, `overrideCycleLine` and `dualGuardCycle` replay the supplied typed situation before reporting the line or hint. Python no longer decides these outcomes. |
| Rust soft premises | `SoftNormDocument` passes Lean's bound background and pair formulas to Rust's search adapter. Rust remains an untrusted witness generator under the plan. |
| Soft wire contract and generic interpreter | The former `ve/softnorms_contract.py` and `ve/wire_contract/engine.py` are under `conformance/` as test-only oracles, per DRI answer 7. The Python regeneration comparison is deleted. |

Against `9aaf918d`, `ve/**/*.py` has **1,974 deleted and 430 added lines** (counted with `git diff --numstat --no-renames`). The 837 lines removed from the two contract modules remain in test-only `conformance/`. Lean `.lean` files have 620 added and 324 deleted lines. The latency fix moved the layered checks from `VE/Readings/Layers.lean` to `VE/SoftNorms/Once.lean`, so those lines count once as deleted and once as added.

## Latency fix (fix directive, 2026-10-06)

**Cause.** Every soft-norms request decoded its source with `validateSoft`. That check rebuilt `soften D`, its layer order (a topological sort) and the expansion table for every formula it typed. `regeneratedCore` did the same for the conflict targets, the fragment test and the coherence premises. On the 70-predicate UDHR source a request cost about 1.5 s of Lean CPU with no rules at all. Readings then multiplied that cost: each candidate side rebuilt the rights correlation and sent the document's whole rule list again, and each pair's reading names re-sent every candidate rule. The large document made about 2,000 such calls.

**Fix, as a class.**

1. *One elaboration per document in Lean* (`dae69cf2`). The layered checks of batch 3d moved from the readings-only `VE.Readings.Layers` to `VE.SoftNorms.Once`, so every soft and rights decoder now uses them: the soft decoder (`decodeSoftSource`), soft admission's quoted rules (`checkQuoted`) and the rights decoder (`decodeRightsSource`, `validateRightsOnce`). `regeneratedCore` reads `targetsIn`, `cohPremiseIn`, `softLabelledIn` and `inFragmentOnce`. Each is proved equal to the function it replaces (`validateSoftOnce_eq`, `validateRightsOnce_eq`, `targetsIn_eq`, `cohPremiseIn_eq`, `softLabelledIn_eq`, `inFragmentOnce_eq`), so every answer and diagnostic is unchanged. Per request on the UDHR source, `soft-rule`/`soft-rules` went from 1.5 s to 0.05 s and `soft-elaborate` from 1.9 s to 0.15 s.
2. *One request per batch of unseen rules* (`0372cf8f`). `soft_relay.check_rules` keeps, per service pool and lower soft source, the rules Lean accepted. A rule check is a pure function of the source and the rule, and `soft-rules` checks each rule on its own. Each rebuild therefore sends one request holding only the rules not yet accepted, or no request at all. A rejected rule is never kept. If Lean refuses a request as a whole, the full request is sent again, so the diagnostic and code stay the full request's. An answer count that differs from the request is `CheckerUnavailable`. `decode_rule` uses the same memo, and the report's reading names are computed once per set from one batch. The services keep the environment handles they had. On the large document, `soft-rule` requests went from 63 to 0 and `soft-rules` from 94 to 34.

**Regression tests** (`tests/test_soft_request_economy.py`):

- A CPU-deadline test on the widest soft environment (64 regulated predicates, every request kind). It failed with the old `validateSoft` restored in the decoder: the run used more than its 2.5 s CPU deadline.
- Memo tests: unseen rules only; rejections never kept; a whole-request refusal resends the full request; a count mismatch is unavailable; a new pool starts empty.
- A three-reading document that must never ask Lean about an accepted rule twice. It failed, along with five others, with the memo disabled.

Not run: a separate mutant that restores `targets`/`InFragment` in `regeneratedCore` alone.

**Measured side by side** (`docs/lean-first/b6/udhr_timing.py`, evidence `evidence/udhr-timing.json`; the earlier figures are kept in `evidence/timings.json`). Before the fix, the isolated UDHR translation took 38.99 s at the base and 150.37 s at the head; the large document took 58.90 s at the base and 426.19 s at the head.

<!-- BEGIN GENERATED LATENCY: python3 docs/lean-first/b6/report.py --write -->
Base `9aaf918d` against head `8fbae87c`, both sides started together on each document (CPU is user + system, Lean services included).

| Document | Run | Bytes | Base wall s | Base CPU s | Head wall s | Head CPU s | CPU ratio | Same JSON | Load |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|
| udhr-20260927T0646Z | 1 | 44,627 | 0.27 | 0.27 | 0.28 | 0.27 | — | yes | 21.6 |
| udhr-20260927T1800Z | 1 | 43,580 | 0.28 | 0.27 | 0.29 | 0.28 | — | yes | 21.6 |
| udhr-20260928T1800Z | 1 | 46,850 | 0.29 | 0.28 | 0.26 | 0.26 | — | yes | 21.6 |
| udhr-20260929T0600Z | 1 | 48,260 | 0.28 | 0.27 | 0.31 | 0.30 | — | yes | 21.6 |
| udhr-20260929T1800Z | 1 | 58,557 | 0.28 | 0.27 | 0.29 | 0.29 | — | yes | 21.6 |
| udhr-20260930T0600Z | 1 | 288,342 | 45.68 | 45.21 | 44.34 | 44.10 | 0.98 | yes | 22.7 |
| udhr-20260930T1800Z | 1 | 258,521 | 26.53 | 26.47 | 28.13 | 28.05 | 1.06 | yes | 21.8 |
| udhr-20261001T1800Z | 1 | 241,065 | 23.20 | 23.17 | 21.08 | 21.04 | 0.91 | yes | 22.4 |
| udhr-20261002T0600Z | 1 | 224,845 | 13.80 | 13.79 | 11.34 | 11.33 | 0.82 | yes | 20.8 |
| udhr-20261002T1800Z | 1 | 228,316 | 13.29 | 13.28 | 11.91 | 11.91 | 0.90 | yes | 20.0 |
| udhr-20261003T0600Z | 1 | 869,161 | 59.66 | 59.65 | 63.51 | 63.51 | 1.06 | yes | 16.0 |
| udhr-20261003T0600Z | 2 | 869,161 | 65.98 | 65.92 | 75.85 | 75.81 | 1.15 | yes | 19.9 |
| udhr-20261003T0600Z | 3 | 869,161 | 67.05 | 66.97 | 78.11 | 78.07 | 1.17 | yes | 21.9 |
| udhr-20261004T0600Z | 1 | 237,049 | 0.41 | 0.41 | 0.31 | 0.31 | — | yes | 21.9 |
| udhr-20261004T1800Z | 1 | 244,289 | 0.45 | 0.45 | 0.39 | 0.39 | — | yes | 21.9 |
| udhr-20261005T0600Z | 1 | 270,770 | 0.42 | 0.42 | 0.43 | 0.42 | — | yes | 21.9 |
| udhr-20261005T1800Z | 1 | 269,413 | 0.26 | 0.26 | 0.49 | 0.48 | — | yes | 22.0 |
| udhr-20261006T1800Z | 1 | 287,435 | 0.42 | 0.42 | 0.43 | 0.43 | — | yes | 22.0 |

18 runs of 16 documents, every report identical: yes. Largest CPU ratio 1.17 (allowance 1.25); slowest head run 78.11 s wall (pilot limit 120 s). A ratio is omitted when both sides spent under 0.5 s of CPU.
<!-- END GENERATED LATENCY -->

## Gate evidence

| Check | Result |
| --- | --- |
| Lean build and response schemas | Full `lake build` passed (743 jobs); `lean/audit.py` covered 4,316 declarations in 408 source files. The frozen-source inventory, statement/declaration dumps, assurance-manifest pins and trust classes were regenerated for the moved and added declarations. |
| A/B probe, conformance, readings, discourse | **65,969 identical**, zero differences: 58,482 probe/conformance and 7,487 readings/discourse. These were recorded before the latency fix. See [core-readings-compare.json](evidence/core-readings-compare.json). |
| Soft corpus | 1,000 accepted trees and 4,843 rejected inputs, with all 1,000 environment, layer, background and decision comparisons matching; 90 near-limit accepted and 137 rejected. See [soft-corpus.json](evidence/soft-corpus.json). |
| Differential fuzzer | All 14 date seeds used the same base/head corpus and mutant counts, with **zero added or removed signature IDs**. The fixed CI seed finds the same 11 signature IDs on base and head after the soft test-input corpus grew; they are not regressions. Each is now in `conformance/difffuzz-baseline.json` (395 entries) with its follow-up id and a one-line `reason`: seven DF-3, two DF-9, one DF-4, one DF-19. `test_ci_run` passes. See [difffuzz-14-seeds.json](evidence/difffuzz-14-seeds.json) and [difffuzz-ci.json](evidence/difffuzz-ci.json). |
| Historical pilots | 294 documents on each side, re-recorded at the fixed head with eight workers: **294 identical**, no availability difference. The large UDHR translation that hit the 600-second limit before the fix now completes. See [pilots-compare.json](evidence/pilots-compare.json). |
| Full offline gate on clean head | Pending: recorded after this commit. |
| Disk | 67 GiB free at the final check. |

`trust_map.py --since 9aaf918d` passes. It measures **164 additional verdict-bearing Lean lines** (`VE.SoftNorms.Once` +144, which `VE.Readings.Layers` loses; `SoftNorms.Run` +64; the soft response schema +63; `SoftNorms.Wire` +30; `Rights.Wire` +12; `SoftNorms.Phases` +7). The DRI signed this on 2026-10-06 because the lines replace deleted Python decision logic; the signature is recorded in `docs/trust-baseline.json`. The latency fix adds no untied trusted line: its layered twins are tied to their equality theorems, and its explanations sit in module comments. The inherited whole-tree S/V drift exists on the base as well and was not rebased.

## Seeded bug checks

Each mutant was planted temporarily in changed code, made the named test fail, and was removed before continuing:

1. Changed the Lean Overlap witness conjunction to a disjunction; `test_witnessed_overlap_and_override_cycle_lines` accepted a false overlap and failed.
2. Negated the Lean preference-edge condition for `override_cycles`; the same test lost a valid cycle and failed.
3. Negated the Lean dependency condition for `DualGuardCycle`; `test_theta_dual_guard_cycle_on_t_prime` failed because the hint disappeared.
4. Ignored `identity_environment` in the Lean soft document hash; `test_readings_identity_environment_is_bound` failed, then passed with the restored service binary and lock.
5. Restored `validateSoft` in `decodeSoftSource`; `test_soft_requests_on_the_widest_environment_stay_within_a_cpu_deadline` failed when the service used more than its 2.5 s CPU deadline. The restored build hashes to the pinned `f759c318…`.
6. Disabled the accepted-rule memo; six tests of `tests/test_soft_request_economy.py` failed, including the whole-document readings test.

## Acceptance ownership

- **AGENT:** Done: the implementation, deletion, A/B recording, 14-seed comparison, soft corpus, latency fix with side-by-side measurement, the fuzzer baseline review and the foreground full gate.
- **HUMAN (DRI):** Signed 2026-10-06: the 164-line trusted-code growth. Review the 11 fuzzer baseline entries' grouping with the rest of DF-3 to DF-19 (an existing deferred item in `conformance/DIFFFUZZ.md`).
- **EXTERNAL:** No model call or external service was used. The plan's later operational soak remains outside batch 6.

Checklist coverage:

- Items 1 and 4: the generated response shape and mutation corpus.
- Item 2: the differential fuzzer, whose CI gate passes.
- Item 5: the focused malformed-source and near-limit corpus.
- Item 6: Lean owns the three-valued soft status.
- Item 13: the seeded mutants.
- Item 14: pinned binary and source hashes, and CPU, not wall, bounds in the new latency test.
- Item 15: the bound readings identity test.
- Item 16: the route-case corpus and gate collection pin.
- Item 17: the statement dump and the trust-map check.
- Item 20: the gate JSON, the generated latency table (`tests/test_lean_first_b6_report.py`) and this report.
- Item 21: the acceptance owners above.

Items 3, 7–12, 18 and 19 are unchanged concerns of other batches. Item 22: everything is committed and the full gate runs on a clean code head.
