# SC-3ac build report

Status: theorem and fixtures complete; selected failures resolved or reproduced on main; the chain's final-HEAD gate remains pending.
HEAD: `feature/sc-3ac` (the final local commit contains this report).
Changed: `title_identity` under `JsonWF`, stable merge-sort filtering, and empty-patch identity.
Open: only the chain's final-HEAD gate; the safety-framework saved-probes mismatch is pre-existing on main.
Signature: the 2026-10-27 item 2 decision covers the DELTA row.

## Plan and scope

| SC-3a row | Delivery | Check |
|---|---|---|
| Anchor/label reach and F8/F9′/F10 | Delivered by sc-3ab on main; no change here | Existing `Examples.lean` guards |
| `title_identity` (spec 5.5) | Proved with DRI-approved `JsonWF D.doc` premise | F-raw-title and well-formed title-only guards; `lake build VE.Scope.Theorems` |
| Stable order with a title among governors | `filter_mergeSort` from `List.mergeSort_cons`; `ordered_filter` | Equal-key carve-outs guard and `insertBy` guards |
| SC-3b condition effects | Not this item; after its approved addendum and SC-2 | Plan dependency |

Pilot bytes expected: 0; no pilot audit or whole-document run claimed. No Python, Rust, route, or response schema changed. There are no answer/refusal deltas. The hand-written change is about 620 lines including fixtures and evidence, near the plan's 600-line target; no work was cut.

## Proof and mutation evidence

The multi-governor proof preserves admission, filtering order, composition, and graph steps. For title alone, success excludes orphan parts, and `patch D [] = D.doc` uses `JsonWF` plus the admitted units array. F-raw-title demonstrates why raw non-WF trees need the premise.

Seeded bugs, each restored: equal-key insertion inverted (the `insertBy` guard failed); empty insertion returned `[]` (empty guard failed); `titleCarveA` changed `top` to `other` (equal-key guard failed); dropped `JsonWF` (`JsonWF D.doc` proof goal remained, with F-raw-title as the counterfixture); wrong empty-patch output (structural proof failed); admission changed to an error (admission proof failed). See `mutants.json`.

Trust on final source: K +0, S +0, V +0, unclassified 0, `tools/trust_map.py --check` PASS. `insertBy` is a proof helper (P); the title-order values are fixtures (T). Generated statements and audit files came from `regen_generated.py`. `lake build`, `lean/audit.py`, and `gate_collection.py --check --prebuilt` passed. The selected pass failed two tests: the trust-table coverage test passed after the class entries were added; the safety-framework saved-probes test failed again on main `795e003bd` with the same `probes.json is out of date` message. No use-case files were edited. The full release gate was not run here, as instructed; the chain runs it on final HEAD.

## Self-review against BUILDER-CHECKLIST

1. N.A. No new relayed answer or decoder.
2. PASS — SC-3a plan table above, `lake build VE.Scope.Theorems`.
3. PASS — `mutants.json`, Lean guards.
4. N.A. No cross-language behavior changed.
5. N.A. No response binding changed.
6. N.A. Final-HEAD gate is run by the chain after this build.
7. PASS — `DELTA.md`, `tools/trust_map.py --check`.
8. PASS — existing F8/F-raw-title output guards; no computed delta.
9. PASS — selected-test run; failed-ID rerun and main reproduction recorded above.
10. PASS — `title_identity` proof, dropped-premise mutant, F-raw-title guard.
11. N.A. No budget or deadline changed.
12. N.A. No runtime algorithm changed; sort helper is proof-only.
13. PASS — no test removed; `tools/gate_collection.py --check --prebuilt`.
