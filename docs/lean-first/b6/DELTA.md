# Batch 6 delta and fix report (2026-10-06)

**Status: incomplete; do not merge.** This branch moves several soft-norm decisions to Lean, but it does not pass the section 5.1 gate or implement every item of row 6. All changes below are local commits on `lean-first/b6`; nothing was pushed.

## Ownership and deletion ledger

| Decision site | Owner after this branch | Remaining work |
| --- | --- | --- |
| Soft source acceptance, fault order, code, text and diagnostic record | `VE.SoftNorms.Phases.checkSource` and the Lean diagnose mode; `ve.backends.soft_relay.run` relays them | Python phase helpers remain for norm-defaults and readings wrappers, and for test-only contract hooks. Delete or replace those helpers after the wrappers have Lean route coverage. |
| `E′`, decisions, carve-outs, background, coherence pairs, layers and conflict targets | `VE.SoftNorms.Wire.regenerated`; `SoftNormDocument` hydrates Python containers from its row | Python still constructs W1 `NormDocument` containers and computes expansion sizes. Review every retained helper for semantic decisions. |
| Soft document hash, rank closure, residual counts, decider grouping and status | Lean `softDocumentHash`, `regenerated`, `residual`, `deciderCounts`, `residualStatus` | The W2 coverage wrapper still combines soft and rights status in Python. |
| Rust soft premises | `SoftNormDocument` takes Lean's `background` and `colliding_pairs` formulas; `rust_jsonl.soft_case` serializes these bound formulas | Rust's generic candidate evaluator remains under the plan's later batches. |
| Runtime regeneration comparison | Deleted from `ve.soft_route`; the old comparison lives in `conformance.soft_oracle` | Test-only oracle retained under the DRI's answer 7. |
| Soft wire contract and generic interpreter | Moved out of `ve/` to `conformance/softnorms_contract.py` and `conformance/wire_contract_engine.py`; runtime retains only a registry type used by other profiles | Test-only code remains until the DRI's batch-18 decision on the JSON contract. |

Against `9aaf918d`, the diff has **457 deleted and 163 added runtime Python lines** (net −294); the two moved contract modules no longer live in `ve/` but retain their test-only bodies. Lean `.lean` files have **69 added and 8 deleted lines** (net +61), including schemas and their encoder proof; 44 added lines are in the three `VE/SoftNorms` modules. These counts use `git diff --numstat` and include additions needed to bind the Lean response.

**Unimplemented row-6 output:** `soft-elaborate` does not yet emit witnessed `Overlap` or `override_cycles` lines, or the English-layer `DualGuardCycle` hint. It would be incorrect to emit an empty or merely structural witness list as if it were checked. The branch therefore does not satisfy the row-6 Lean work.

## Gate evidence

| Check | Result |
| --- | --- |
| Lean build | `lake build` passed, 743 jobs. The schema encoder proof was repaired in `30520e41`. |
| Lean audit / Rust build / Cargo tests | All passed in `/tmp/ve-b6-gate.json`; 50 Rust tests passed. |
| Full gate | **Failed** on clean HEAD `30520e41`: 10,884 passed, 191 failed, 7 skipped of 11,082 selected tests. A rerun on clean HEAD `084a0323` reached the 16-worker Python suite after the Lean build and audit and Rust build and tests passed, but hit a 25-minute command cap before pytest returned (exit 124). It has no valid final counts (`/tmp/ve-b6-gate-final.json` was only initialized). The full gate therefore remains unpassed at the latest HEAD. |
| Focused tests after fixes | Malformed environments: 2,672 passed; readings S1/S2 documents: 101 passed; selected route, schema, import and manifest tests passed. A later combined readings/wire-corpus run was interrupted after one wire-corpus failure; its traceback was not captured. |
| Differential fuzzer | Full CI sample with `--minimise-limit 0` passed: zero new, zero unreviewed, zero missing baseline signatures (`/tmp/ve-b6-difffuzz-ci.json`). The first full attempt was interrupted during minimization while its Lean/Rust binaries were absent. |
| A/B conformance | 39,612 records identical across Python and Lean authorities, zero unlisted differences (`/tmp/ve-b6-ab-compare.json`). |
| A/B Stage-0 probe | 18,870 records identical across Python and Lean authorities, zero unlisted differences (`/tmp/ve-b6-probe-compare.json`). |
| Soft-specific corpus, 14 date seeds, use-case answer keys, historical pilots | **Not run** as a base/head A/B comparison. The test suite's focused soft conformance fixtures passed earlier, but this is not the full section 5.1 comparison. |
| Latency | No comparable base/head Lean CPU or quiet-host wall sample was taken. This batch does not claim a speed improvement. The added Lean calls in Python containers need a latency measurement before acceptance. |
| Disk | 60 GiB free at the last `df -h .` check. |

### Three planted bugs, each removed

1. Replaced `residual.update(soft_row["soft_residual"])` with an empty update. `test_document_coverage_and_render_show_open_exception` failed (1 failed in 5.18 s).
2. Replaced `SoftNormDocument.document_hash` with 64 zeroes. `test_python_lean_spec_fixture[alpha-high]` failed (1 failed in 1.44 s).
3. Changed the Lean diagnostic attachment condition from `fault` to `clean`. `test_public_call_reports_the_first_fault_and_keeps_the_legacy_error` failed (1 failed in 2.44 s).

The files were restored after each mutant; the three focused tests then passed together.

## Outstanding acceptance and ownership

- **AGENT:** Implement witnessed `Overlap`, `override_cycles`, and `DualGuardCycle` Lean output and corresponding producer-derived schemas and tests. Remove the remaining Python soft phase/semantic decision sites once readings and norm-defaults wrappers use their own Lean owner.
- **AGENT:** Resolve the remaining full-gate failures and rerun `python3 tools/gate.py` on a clean, committed HEAD with sufficient time for pytest to return. The previous completed gate failures included stale route/contract test hooks (since fixed), wrapper rejection and malformed input crashes (focused tests now pass), and trust-map/statement metadata. The generated declaration dump is current, but `trust_map.py --check` still reports inherited K/S/V budget drift and 27 unclassified declarations; these are not silently signed or rebased here. `test_select_tests.py` also assumes Python AST `_field_types`, absent from the gate's Python 3.12.3.
- **AGENT:** Complete section 5.1 A/B coverage over the soft corpus, 14 date seeds, use-case answer keys and every historical pilot; list and classify every difference. Measure Lean CPU and quiet-host wall latency against the batch base.
- **HUMAN (DRI):** Review and sign any wording/order delta block and each verdict/availability delta, and decide whether the remaining cross-batch compatibility code may persist. No signature is claimed here.
- **EXTERNAL:** No external service or model call was used. Operational soak and any external pilot environment remain deferred to their assigned plan gates.

Checklist coverage: the changed response fields have Lean-generated schemas and mutation tests (items 1, 4, 13); the full fuzzer ran with 1- and 2-fault samples and zero baseline growth (2); malformed-environment tests passed (5); binaries were pinned and built through the offline gate (14); identities and new fields are covered by focused tests (15); the Lean statements dump was regenerated, with trust budget not approved (17); this report uses gate JSON counts and records omissions (20); the table above tags AGENT/HUMAN/EXTERNAL (21). Item 22 is **not satisfied** because the completed full gate failed, and the final-HEAD rerun timed out. Unchanged concerns in checklist items 3, 6–12, 16, 18 and 19 were not established by this batch's evidence.
