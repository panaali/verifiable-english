# SC-3ac build report

Status: theorem and fixtures complete; the chain's final-HEAD gate is pending.
HEAD: `feature/sc-3ac` (the final local commit contains this report).
Changed: `title_identity` under `JsonWF`, stable merge-sort filtering, and empty-patch identity.
Open: only the chain gate; the safety-framework saved-probes failure reproduces on main.
Signature: 2026-10-27 DRI decision item 2 covers the DELTA row.
## Delivery

- SC-3a anchor/label reaches and F8/F9′/F10 were delivered by sc-3ab; their guards remain.
- Spec 5.5 `title_identity` is proved with the approved `JsonWF D.doc` premise. F-raw-title proves why it is needed; well-formed title-only guards accept.
- Stable order is proved through `List.mergeSort_cons`, `filter_mergeSort`, and `ordered_filter`; equal-key and empty-input guards exercise it.
- SC-3b follows after its approved addendum and SC-2. Pilot bytes expected: 0; no pilot audit or whole-document run claimed.

For several governors, admission, composition, rule order and graph steps agree after title removal. For title alone, successful governance excludes orphan parts; `JsonWF` and the admitted units array give `patch D [] = D.doc`. No Python, Rust, route, response schema, or runtime algorithm changed. The item uses about 600 hand-written lines including fixtures and evidence; no work was cut.
Seeded bugs, all restored: inverted equal-key insertion and empty insertion returned `[]` (the two `insertBy` guards failed); changed `titleCarveA` to `other` (order guard failed); dropped `JsonWF` (open goal `JsonWF D.doc`, F-raw-title counterexample); claimed null empty-patch output (structural proof failed); changed admission success to an error (admission proof failed). See `mutants.json`.
Trust: K +0, S +0, V +0, unclassified 0 (`tools/trust_map.py --check` PASS). `insertBy` is a P proof helper and the title-order values are T fixtures. Regeneration, `lake build`, `lean/audit.py`, and `gate_collection.py --check --prebuilt` passed.
The selected pass found two failures: trust-table coverage passed after classification; `test_fsf_r2_probes_rerun_equals_saved_probes` still reports `probes.json is out of date` on detached main `795e003bd`. No safety-framework files were edited. The full release gate was not run here, as instructed.
## Self-review against BUILDER-CHECKLIST

1. N.A. No relayed answer or decoder.
2. PASS — SC-3a delivery above; `lake build VE.Scope.Theorems`.
3. PASS — `mutants.json` and Lean guards.
4. N.A. No cross-language behavior changed.
5. N.A. No response binding changed.
6. N.A. Final-HEAD gate runs in the chain.
7. PASS — `DELTA.md` and `tools/trust_map.py --check`.
8. PASS — F8/F-raw-title guards; no computed delta.
9. PASS — selected pass, failed-ID rerun, and main reproduction.
10. PASS — `title_identity`, dropped-premise mutant, F-raw-title.
11. N.A. No budget or deadline changed.
12. N.A. No runtime algorithm changed.
13. PASS — no test removed; `gate_collection.py --check --prebuilt`.
