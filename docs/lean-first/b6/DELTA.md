# Batch 6 delta and fix report (2026-10-07)

**Status: incomplete; do not merge.** Local branch `lean-first/b6` is based on `9aaf918d`. Nothing was pushed. The implementation is committed, but the full gate has one failing CI-fuzzer test, the large UDHR pilot exceeds the latency allowance, one eight-worker pilot timed out, and trusted Lean growth needs a DRI signature. The producer schema regression corpus has 292 cases, including standalone and batched soft-rule answers.

## Ownership and deletion ledger

| Decision or output | Lean owner and Python relay |
| --- | --- |
| Soft source acceptance, fault order, code, text, limits and rule references | `VE.SoftNorms.Phases.checkSource` and `decodeSoftNorm`; `soft_relay.run` calls the service and preserves the Lean diagnostic. Python phase checks are removed from the runtime. |
| Soft expansion, decisions, ranks, exceptions, coherence pairs, preference predicates, rule acts and incompatibility | `VE.SoftNorms.Wire.regenerated` and `VE.SoftNorms.Run.runSoftKind`; `SoftNormDocument` hydrates display and search containers from the response. Python semantic reconstruction methods are removed. |
| Residual counts, decider grouping, status and document hash | Lean `residual`, `deciderCounts`, `residualStatus` and `softDocumentHash`; the readings wrapper sends the original identity environment, which Lean checks against its lowered source before hashing and regenerating the displayed environment. |
| Witnessed Overlap and override cycle lines, DualGuardCycle hint | Lean `warningRows`, `overlapLine`, `overrideCycleLine` and `dualGuardCycle` replay the supplied typed situation before reporting the line or hint. Python no longer decides these outcomes. |
| Rust soft premises | `SoftNormDocument` passes Lean's bound background and pair formulas to Rust's search adapter. Rust remains an untrusted witness generator under the plan. |
| Soft wire contract and generic interpreter | The former `ve/softnorms_contract.py` and `ve/wire_contract/engine.py` are under `conformance/` as test-only oracles, per DRI answer 7. The Python regeneration comparison is deleted. |

Against `9aaf918d`, `ve/**/*.py` has **1,970 deleted and 351 added lines** (net −1,619 runtime Python lines, counted with `git diff --numstat --no-renames`). The 837 lines removed from the two contract modules remain in test-only `conformance/`; excluding those moves, 1,133 old runtime lines were deleted and 351 relay/container lines added. Lean `.lean` files have **271 added and 21 deleted lines** (net +250), including the response schemas and encoder proofs.

The relay caches only successful pure `soft-elaborate`, `soft-rule` and `soft-rules` answers through the existing bounded `decide_once` pool. Each caller receives a deep copy. The batch route validates several rules under one decoded source. An isolated large UDHR document still took 426.19 s wall / 425.72 s CPU against 58.90 s wall / 58.60 s CPU at the base; parsed JSON output was identical. This violates the latency allowance. The 822.53-second instrumented run logged 763 soft-elaborate, 253 soft-rules and 961 soft-rule calls, including cache hits; wall time spent inside those wrappers was 325.13, 225.39 and 176.82 seconds respectively under heavier load. The remaining distinct generated sources require repeated Lean checks.

## Gate evidence

| Check | Result |
| --- | --- |
| Lean build and response schemas | Full `lake build` passed (743 jobs); the theorem audit covered 4,311 declarations in 408 source files. `tools/response_schemas.py --check`, frozen-source audit and relay lint passed. |
| Focused tests | The first selected run had 459 passed and one manifest omission; the omission was fixed. All five failures from the first full gate then passed in a focused rerun. |
| A/B probe, conformance, readings, discourse | **65,969 identical**, zero differences: 58,482 probe/conformance and 7,487 readings/discourse. See [core-readings-compare.json](evidence/core-readings-compare.json). |
| Soft corpus | 1,000 accepted trees and 4,843 rejected inputs, with all 1,000 environment, layer, background and decision comparisons matching; 90 near-limit accepted and 137 rejected. See [soft-corpus.json](evidence/soft-corpus.json). |
| Differential fuzzer | All 14 date seeds used the same base/head corpus and mutant counts, with **zero added or removed signature IDs**. The fixed CI seed has 11 unreviewed signatures on both base and head after the test-input corpus expanded; its tracked 384-entry baseline was unchanged. `test_ci_run` requires zero and fails. See [difffuzz-14-seeds.json](evidence/difffuzz-14-seeds.json) and [difffuzz-ci.json](evidence/difffuzz-ci.json). |
| Historical pilots | 294 documents on each side; 293 identical, one **availability** difference: `pilot/udhr-20261003T0600Z:usecases/udhr-pilot/run-20261003T0600Z/translation.ve.md` returned at the base and hit the 600-second wall limit at the head under eight workers. The same source completed alone with identical parsed JSON in 426.19 s. See [pilots-compare.json](evidence/pilots-compare.json). |
| Full offline gate on clean head | Commit `a6d896b5`, clean worktree: 11,078 passed, 7 skipped, **1 failed** (`tests/test_difffuzz.py::test_ci_run`), 1 deselected; Rust 50 passed. See [full-gate.json](evidence/full-gate.json). |
| Latency | The isolated UDHR translation took 38.99 s wall / 37.63 s CPU at the base and 150.37 s wall / 150.12 s CPU at the earlier head. The larger UDHR document took 58.90 s wall / 58.60 s CPU at the base and 426.19 s wall / 425.72 s CPU at the final code head; parsed JSON matched. Both exceed the plan's 120 s pilot wall budget and 20% CPU-growth allowance. See [timings.json](evidence/timings.json). |
| Disk | 60 GiB free at the final check. |

The producer schema has closed witness-model fields (`complete`, `domains`, `constants`, `relations`); the route-row mutation test rejects dropped, emptied and retyped required fields. `lean/declarations.txt` was regenerated. The trust class table now covers every declaration, and the consolidation-plan ledger figures were updated mechanically. `trust_map.py --since 9aaf918d` reports **164 additional verdict-bearing Lean lines** against zero signed allowance (`SoftNorms.Run` +64, the soft response schema +63, `SoftNorms.Wire` +30, `SoftNorms.Phases` +7). The inherited whole-tree S/V budget drift exists on the base as well. Neither budget was silently signed or rebased.

## Seeded bug checks

Each mutant was planted temporarily in changed code, made the named test fail, and was removed before continuing:

1. Changed the Lean Overlap witness conjunction to a disjunction; `test_witnessed_overlap_and_override_cycle_lines` accepted a false overlap and failed.
2. Negated the Lean preference-edge condition for `override_cycles`; the same test lost a valid cycle and failed.
3. Negated the Lean dependency condition for `DualGuardCycle`; `test_theta_dual_guard_cycle_on_t_prime` failed because the hint disappeared.
4. Ignored `identity_environment` in the Lean soft document hash; `test_readings_identity_environment_is_bound` failed, then passed with the restored service binary and lock.

The earlier incomplete report also recorded three removed mutants for residual count, document hash and diagnostic attachment. The new cache-isolation and batched-rule tests pass; the four mutants above satisfy the batch's three-behaviour requirement.

## Acceptance ownership

- **AGENT:** The implementation, deletion, A/B recording, 14-seed comparison, soft corpus and foreground full gate are complete. Resolve the fixed CI sample's 11 inherited disagreements without enlarging its baseline, then rerun the full gate.
- **HUMAN (DRI):** Review the 164-line trusted-code growth, the latency breach and the one pilot availability difference. The plan requires a signature for the pilot CPU growth and each availability difference. No signature is claimed here.
- **EXTERNAL:** No model call or external service was used. The plan's later operational soak remains outside batch 6.

Checklist coverage: the generated response shape and mutation corpus cover items 1 and 4; the differential fuzzer exercises item 2 but its CI gate fails as recorded; the focused malformed-source and near-limit corpus covers item 5; Lean owns the three-valued soft status (6); the seeded mutants cover item 13; pinned binary and source hashes cover item 14; the bound readings identity test covers item 15; the route-case corpus and gate collection pin cover item 16; the statement dump and trust-map check cover item 17; the gate JSON and this report cover item 20; and the acceptance owners above cover item 21. Items 3, 7–12, 18 and 19 are unchanged concerns of other batches. Item 22 has a committed implementation and a full gate on a clean code head, but the gate failed as stated.
