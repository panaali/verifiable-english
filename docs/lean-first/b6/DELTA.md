# Batch 6 delta and fix report (2026-10-06)

**Status: gate in progress; do not merge yet.** Local branch `lean-first/b6` is based on `9aaf918d`. Nothing was pushed. The producer schema regression corpus is `tests/data/route-cases.jsonl`, 292 cases after adding standalone and batched soft-rule answers.

## Ownership and deletion ledger

| Decision or output | Lean owner and Python relay |
| --- | --- |
| Soft source acceptance, fault order, code, text, limits and rule references | `VE.SoftNorms.Phases.checkSource` and `decodeSoftNorm`; `soft_relay.run` calls the service and preserves the Lean diagnostic. Python phase checks are removed from the runtime. |
| Soft expansion, decisions, ranks, exceptions, coherence pairs, preference predicates, rule acts and incompatibility | `VE.SoftNorms.Wire.regenerated` and `VE.SoftNorms.Run.runSoftKind`; `SoftNormDocument` hydrates display and search containers from the response. Python semantic reconstruction methods are removed. |
| Residual counts, decider grouping, status and document hash | Lean `residual`, `deciderCounts`, `residualStatus` and `softDocumentHash`; the readings wrapper sends the original identity environment, which Lean checks against its lowered source before hashing and regenerating the displayed environment. |
| Witnessed Overlap and override cycle lines, DualGuardCycle hint | Lean `warningRows`, `overlapLine`, `overrideCycleLine` and `dualGuardCycle` replay the supplied typed situation before reporting the line or hint. Python no longer decides these outcomes. |
| Rust soft premises | `SoftNormDocument` passes Lean's bound background and pair formulas to Rust's search adapter. Rust remains an untrusted witness generator under the plan. |
| Soft wire contract and generic interpreter | The former `ve/softnorms_contract.py` and `ve/wire_contract/engine.py` are under `conformance/` as test-only oracles, per DRI answer 7. The Python regeneration comparison is deleted. |

Against `9aaf918d`, `ve/**/*.py` has **1,131 deleted and 244 added lines** (net −887 runtime Python lines). The 837 lines removed from the two contract modules remain in test-only `conformance/`; excluding those moves, 294 old runtime lines were deleted and 244 relay/container lines added. Lean `.lean` files have **247 added and 18 deleted lines** (net +229), including the response schema and encoder proof. These numbers come from `git diff --numstat 9aaf918d..HEAD` and will be refreshed at the final head.

The relay caches only successful pure `soft-elaborate`, `soft-rule` and `soft-rules` answers through the existing bounded `decide_once` pool. Each caller receives a deep copy. The batch route validates several rules under one decoded source. An isolated large UDHR document still took 426.19 s wall / 425.72 s CPU against 58.90 s wall / 58.60 s CPU at the base; parsed JSON output was identical. This violates the latency allowance. The 822.53-second instrumented run logged 763 soft-elaborate, 253 soft-rules and 961 soft-rule calls, including cache hits; wall time spent inside those wrappers was 325.13, 225.39 and 176.82 seconds respectively under heavier load. The remaining distinct generated sources require repeated Lean checks.

## Gate evidence

| Check | Result |
| --- | --- |
| Lean build and response schemas | Full `lake build` passed (743 jobs); final `ve_service` rebuild passed (542 jobs). `tools/response_schemas.py --check`, frozen-source audit and relay lint passed. |
| Focused tests | 459 of 460 selected tests passed; the sole manifest review-list omission was fixed and its test and the new batch-rule test then passed. Earlier 112 norm-default tests passed after moving the shared placeholder producer. |
| A/B probe and conformance | 58,482 recorded results identical across base and head, zero differences (`/tmp/ve-b6-core-compare.json`). |
| A/B readings and discourse | 7,487 recorded results identical, zero differences (`/tmp/ve-b6-rd-compare.json`). |
| Soft-specific corpus | 1,000 accepted trees and 4,843 rejected inputs on both base and head; all 1,000 environment, layer, background and decision comparisons matched. The near-limit cohorts were 90 accepted and 137 rejected on each side. A final-head rerun is pending. |
| Differential fuzzer CI sample | Zero new, zero unreviewed, zero missing baseline signatures (`/tmp/ve-b6-difffuzz-ci-final.json`). Fourteen date seeds at the final head are pending. |
| Historical pilots | The base recorded 278 documents. Final-head recording is in progress. The first 52 head records had one 600-second wall timeout on a constitution S1 document under host load above 32 cores; the earlier head run of that document returned an identical result. All other first 52 records matched. |
| Full offline gate on clean head | Pending. The previous completed run, before the fixes in `c60cb4ca`, had 11,011 passed and 65 failed; its failures drove the focused repairs above. |
| Latency | The isolated UDHR translation completed with identical output in 38.99 s wall / 37.63 s CPU at the base and 150.37 s wall / 150.12 s CPU at the earlier head. The larger UDHR document completed with identical parsed JSON in 58.90 s wall / 58.60 s CPU at the base and 426.19 s wall / 425.72 s CPU at the current code head. Both exceed the plan's 120 s pilot wall budget and 20% CPU-growth allowance. |
| Disk | 68 GiB free at the last check. |

The producer schema has closed witness-model fields (`complete`, `domains`, `constants`, `relations`); the route-row mutation test rejects dropped, emptied and retyped required fields. `lean/declarations.txt` was regenerated. The trust class table now covers every declaration, and the consolidation-plan ledger figures were updated mechanically. `trust_map.py --since 9aaf918d` still reports **145 additional trusted Lean lines** against zero signed allowance. The inherited whole-tree S/V budget drift exists on the base as well. Neither budget was silently signed or rebased.

## Seeded bug checks

Each mutant was planted temporarily in changed code, made the named test fail, and was removed before continuing:

1. Changed the Lean Overlap witness conjunction to a disjunction; `test_witnessed_overlap_and_override_cycle_lines` accepted a false overlap and failed.
2. Negated the Lean preference-edge condition for `override_cycles`; the same test lost a valid cycle and failed.
3. Negated the Lean dependency condition for `DualGuardCycle`; `test_theta_dual_guard_cycle_on_t_prime` failed because the hint disappeared.
4. Ignored `identity_environment` in the Lean soft document hash; `test_readings_identity_environment_is_bound` failed, then passed with the restored service binary and lock.

The earlier incomplete report also recorded three removed mutants for residual count, document hash and diagnostic attachment. The new cache-isolation test passes; its mutant check is pending.

## Acceptance ownership

- **AGENT:** Complete the final-head pilot A/B, 14 date-seed comparison, final soft-corpus run and full offline gate on a clean committed head. Record every output or availability difference and final gate counts from its JSON.
- **HUMAN (DRI):** Review the 145-line trusted-code growth and any remaining latency or availability deltas. The plan requires a signature for the pilot CPU growth and each availability difference. No signature is claimed here.
- **EXTERNAL:** No model call or external service was used. The plan's later operational soak remains outside batch 6.

Checklist coverage: the generated response shape and mutation corpus cover items 1 and 4; the differential fuzzer covers item 2; the focused malformed-source and near-limit corpus covers item 5; Lean owns the three-valued soft status (6); the seeded mutants cover item 13; pinned binary and source hashes cover item 14; the bound readings identity test covers item 15; the route-case corpus and gate collection pin cover item 16; the statement dump and trust-map check cover item 17; the gate JSON and this report cover item 20; and the acceptance owners above cover item 21. Items 3, 7–12, 18 and 19 are unchanged concerns of other batches. Item 22 is pending the final clean-head gate and report commit.
