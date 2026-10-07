# Batch 6 delta and fix report (2026-10-07)

**Status: complete; ready for review.** Local branch `lean-first/b6` is based on `9aaf918d`. Nothing was pushed. The fix directive's items are done. Soft-norms latency is within the plan's allowances for `ve document check` and `ve document render` (largest UDHR CPU ratio 1.11; the slowest head run took 69.91 s wall). The 11 inherited CI-fuzzer signatures are reviewed into the baseline. The DRI's signature for the 164 trusted Lean lines is recorded. The producer schema regression corpus is `tests/data/route-cases.jsonl`, 292 cases, including standalone and batched soft-rule answers.

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

## Recheck fix: render's per-candidate requests (lf-6c, 2026-10-07)

**Finding B.** `ve document render` of the large UDHR translation, which the UDHR pilot runs (`finish.py` calls `render_document`), still cost 1.32 to 1.49 times the base CPU; the fix above had measured `check` only. Render sent 273 `soft-elaborate` and 116 `soft-rules` requests (base: none). Every right candidate's display document (`render_document.candidate_rights`, 115) and every readings side the English wording built (`readings_s1.Side`, 156) was a whole soft document Lean was asked to elaborate, and each asked about its own line rules. All of them carry one environment, and a soft request costs Lean 0.06 to 0.1 s of environment-wide validation however few rules it holds.

**Fix, as a class** (`2ffbe0c1`). Building a candidate's document no longer costs a Lean request of its own:

1. *Deferred soft documents.* `SoftNormDocument(deferred=True)` holds its Python-hydrated `env`, `rules` and `core`. The first read of any field Lean supplies asks Lean for the whole document, exactly as eager construction does, and raises its diagnostic (on every read). A document Python cannot hydrate asks Lean at once, so its error is the eager one. Readings sides (which Lean's readings route checks as `sideWF`) and render's candidate display documents are deferred. `Side._checked_elaborate` and S2's `_ChoiceDocument`, which are checks, stay eager.
2. *One rule request per source.* `RightsDocument.warm_rules` asks Lean about the line rules of many documents in one `soft-rules` request per lower source, through the accepted-rule memo, before they are built one by one. It builds nothing. It absorbs only a content refusal, which each document then raises when built; `CheckerUnavailable` propagates. Render warms its right candidates, `Decoded` warms every side once, and `validate_reading_sets` warms the right candidates it checks alone (rights documents without `readings@1`, whose whole documents admission still checks one by one).

On the large document, render now sends 29 `soft-elaborate` and 3 `soft-rules` requests, and check 30 and 3 (it sent 95 and 34). Of the `soft-elaborate` requests, 27 are E22/E23 reading Lean's rule acts and incompatible pairs of a twin's side. Render's and check's outputs are identical to the base's and to the previous head's.

What a deferred document leaves unchecked: a readings@1 right candidate's display document alone over the source units is no longer elaborated by Lean as a whole. Its line rules are Lean-checked (`soft-rules`), and Lean's readings route checks the candidate's side, with Lean's own correlation. S2's Python regeneration of the route refusal (`route_refusal`) still asks Lean about each compatible choice's document, up to 64; it is a conformance comparison of Python's correlation with Lean's and is left as it is. No UDHR document reaches it.

**Regression tests** (`tests/test_soft_candidate_economy.py`): the soft requests of render and check do not grow from seven to nine sets of right candidates (one rule request in all), nor admission's rule requests from one to three sets; outputs equal those of eager construction; a deferred document asks Lean once for all of its Lean fields (the list is generated from eager construction), raises Lean's diagnostic on every read, and gives the eager error when Python cannot hydrate it; `extend` reaches `extended_env` either way; the warm-up raises no diagnostic, raises an outage, sends one request, and keeps each document's diagnostic.

**Measured side by side** (`docs/lean-first/b6/udhr_timing.py`, evidence `evidence/udhr-timing.json`; the earlier figures are kept in `evidence/timings.json`). Before the fix, the isolated UDHR translation took 38.99 s at the base and 150.37 s at the head; the large document took 58.90 s at the base and 426.19 s at the head.

<!-- BEGIN GENERATED LATENCY: python3 docs/lean-first/b6/report.py --write -->
Base `9aaf918d` against head `2ffbe0c1`, both sides started together on each document (CPU is user + system, Lean services included).

| Document | Command | Run | Bytes | Base wall s | Base CPU s | Head wall s | Head CPU s | CPU ratio | Same output | Load |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|
| udhr-20260927T0646Z | check | 1 | 44,627 | 0.48 | 0.43 | 0.33 | 0.32 | — | yes | 17.3 |
| udhr-20260927T0646Z | render | 1 | 44,627 | 0.31 | 0.31 | 0.26 | 0.25 | — | yes | 17.3 |
| udhr-20260927T1800Z | check | 1 | 43,580 | 0.27 | 0.26 | 0.40 | 0.40 | — | yes | 17.3 |
| udhr-20260927T1800Z | render | 1 | 43,580 | 0.25 | 0.24 | 0.31 | 0.30 | — | yes | 17.3 |
| udhr-20260928T1800Z | check | 1 | 46,850 | 0.27 | 0.26 | 0.25 | 0.25 | — | yes | 17.3 |
| udhr-20260928T1800Z | render | 1 | 46,850 | 0.30 | 0.29 | 0.32 | 0.32 | — | yes | 17.3 |
| udhr-20260929T0600Z | check | 1 | 48,260 | 0.25 | 0.24 | 0.32 | 0.32 | — | yes | 17.3 |
| udhr-20260929T0600Z | render | 1 | 48,260 | 0.49 | 0.49 | 0.38 | 0.37 | — | yes | 17.3 |
| udhr-20260929T1800Z | check | 1 | 58,557 | 0.33 | 0.32 | 0.31 | 0.31 | — | yes | 17.3 |
| udhr-20260929T1800Z | render | 1 | 58,557 | 0.55 | 0.53 | 0.46 | 0.46 | 0.87 | yes | 17.3 |
| udhr-20260930T0600Z | check | 1 | 288,342 | 47.49 | 47.21 | 45.60 | 45.29 | 0.96 | yes | 20.3 |
| udhr-20260930T0600Z | render | 1 | 288,342 | 47.71 | 47.70 | 40.17 | 40.17 | 0.84 | yes | 15.3 |
| udhr-20260930T1800Z | check | 1 | 258,521 | 26.13 | 26.12 | 21.79 | 21.79 | 0.83 | yes | 13.6 |
| udhr-20260930T1800Z | render | 1 | 258,521 | 26.98 | 26.98 | 26.17 | 26.16 | 0.97 | yes | 13.4 |
| udhr-20261001T1800Z | check | 1 | 241,065 | 20.48 | 20.47 | 17.22 | 17.22 | 0.84 | yes | 12.8 |
| udhr-20261001T1800Z | render | 1 | 241,065 | 23.38 | 23.37 | 18.66 | 18.65 | 0.80 | yes | 12.2 |
| udhr-20261002T0600Z | check | 1 | 224,845 | 26.12 | 22.44 | 21.84 | 17.69 | 0.79 | yes | 22.0 |
| udhr-20261002T0600Z | render | 1 | 224,845 | 19.62 | 19.56 | 15.83 | 15.78 | 0.81 | yes | 21.1 |
| udhr-20261002T1800Z | check | 1 | 228,316 | 14.75 | 14.70 | 12.64 | 12.59 | 0.86 | yes | 20.3 |
| udhr-20261002T1800Z | render | 1 | 228,316 | 16.02 | 16.02 | 12.64 | 12.63 | 0.79 | yes | 18.8 |
| udhr-20261003T0600Z | check | 1 | 869,161 | 72.76 | 71.85 | 68.08 | 67.31 | 0.94 | yes | 27.7 |
| udhr-20261003T0600Z | check | 2 | 869,161 | 62.54 | 59.74 | 56.64 | 55.07 | 0.92 | yes | 29.5 |
| udhr-20261003T0600Z | check | 3 | 869,161 | 73.65 | 70.21 | 69.91 | 65.70 | 0.94 | yes | 29.0 |
| udhr-20261003T0600Z | render | 1 | 869,161 | 60.96 | 59.64 | 56.66 | 56.00 | 0.94 | yes | 25.9 |
| udhr-20261003T0600Z | render | 2 | 869,161 | 80.63 | 77.88 | 67.75 | 65.41 | 0.84 | yes | 30.7 |
| udhr-20261003T0600Z | render | 3 | 869,161 | 63.42 | 62.78 | 57.87 | 56.65 | 0.90 | yes | 26.1 |
| udhr-20261004T0600Z | check | 1 | 237,049 | 0.27 | 0.26 | 0.26 | 0.26 | — | yes | 26.1 |
| udhr-20261004T0600Z | render | 1 | 237,049 | 0.46 | 0.45 | 0.51 | 0.50 | 1.11 | yes | 26.1 |
| udhr-20261004T1800Z | check | 1 | 244,289 | 0.31 | 0.30 | 0.29 | 0.28 | — | yes | 26.1 |
| udhr-20261004T1800Z | render | 1 | 244,289 | 0.52 | 0.51 | 0.42 | 0.41 | 0.80 | yes | 26.1 |
| udhr-20261005T0600Z | check | 1 | 270,770 | 0.27 | 0.26 | 0.24 | 0.23 | — | yes | 26.1 |
| udhr-20261005T0600Z | render | 1 | 270,770 | 0.49 | 0.48 | 0.46 | 0.45 | — | yes | 26.1 |
| udhr-20261005T1800Z | check | 1 | 269,413 | 0.32 | 0.32 | 0.33 | 0.33 | — | yes | 26.1 |
| udhr-20261005T1800Z | render | 1 | 269,413 | 0.55 | 0.54 | 0.52 | 0.51 | 0.94 | yes | 26.1 |
| udhr-20261006T1800Z | check | 1 | 287,435 | 0.32 | 0.31 | 0.32 | 0.32 | — | yes | 26.1 |
| udhr-20261006T1800Z | render | 1 | 287,435 | 0.51 | 0.51 | 0.45 | 0.44 | 0.86 | yes | 26.1 |

36 runs of 16 documents (check and render), every output identical: yes. Largest CPU ratio 1.11 (check 0.96, render 1.11; allowance 1.25); slowest head run 69.91 s wall (pilot limit 120 s). A ratio is omitted when both sides spent under 0.5 s of CPU.
<!-- END GENERATED LATENCY -->

## Gate evidence

| Check | Result |
| --- | --- |
| Lean build and response schemas | Full `lake build` passed (743 jobs); `lean/audit.py` covered 4,316 declarations in 408 source files. The frozen-source inventory, statement/declaration dumps, assurance-manifest pins and trust classes were regenerated for the moved and added declarations. |
| A/B probe, conformance, readings, discourse | **65,969 identical**, zero differences: 58,482 probe/conformance and 7,487 readings/discourse. These were recorded before the latency fix. See [core-readings-compare.json](evidence/core-readings-compare.json). |
| Soft corpus | 1,000 accepted trees and 4,843 rejected inputs, with all 1,000 environment, layer, background and decision comparisons matching; 90 near-limit accepted and 137 rejected. See [soft-corpus.json](evidence/soft-corpus.json). |
| Differential fuzzer | All 14 date seeds used the same base/head corpus and mutant counts, with **zero added or removed signature IDs**. The fixed CI seed finds the same 11 signature IDs on base and head after the soft test-input corpus grew; they are not regressions. Each is now in `conformance/difffuzz-baseline.json` (395 entries) with its follow-up id and a one-line `reason`: seven DF-3, two DF-9, one DF-4, one DF-19. `test_ci_run` passes. See [difffuzz-14-seeds.json](evidence/difffuzz-14-seeds.json) and [difffuzz-ci.json](evidence/difffuzz-ci.json). |
| Historical pilots | 294 documents on each side, re-recorded at the fixed head with eight workers: **294 identical**, no availability difference. The large UDHR translation that hit the 600-second limit before the fix now completes. See [pilots-compare.json](evidence/pilots-compare.json). |
| Full offline gate on clean head | Commit `51a89eca`, clean worktree, every stage in the foreground: `lake build` (743 jobs), `lean/audit.py` (4,316 theorems), Rust 50 passed, and the full suite with the gate's options in seven file-disjoint chunks covering all 265 test files: 11,092 passed, 6 skipped, 0 failed, 1 deselected (`live`). `tools/gate.py` itself ran out of the 60-minute call limit twice at load 43 to 50; its first attempt had found the two collection and lint failures fixed in `51a89eca`. See [full-gate.json](evidence/full-gate.json). |
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
7. Recheck fix (`tests/test_soft_candidate_economy.py`), ten mutants, each killed by at least one test: readings sides built eagerly; render's candidate documents built eagerly; render's warm-up off; the side warm-up off; admission's warm-up off; a deferred read that returns without asking Lean; `extend` dropped; a hydration failure kept deferred; a rejected rule kept by the warm-up; an outage absorbed by the warm-up.

## Acceptance ownership

- **AGENT:** Done: the implementation, deletion, A/B recording, 14-seed comparison, soft corpus, latency fix with side-by-side measurement, the fuzzer baseline review and the foreground full suite (in chunks; see the gate row).
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

Items 3, 7–12, 18 and 19 are unchanged concerns of other batches. Item 22: everything is committed, and the full suite passed on the clean code head `51a89eca`.
