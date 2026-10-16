# Build report: infra/rights-licence-relay

**DRI signature needed: the trust growth V +102 (K +0, S +0)**, itemised per file in [DELTA.md](DELTA.md) row 4.
The task asks for the DRI's signature. Standing ruling R6 covers the growth: the lines replace the deleted Python
`_narrowings` and `_in_scope`. R6 has the builder record the allowance. The chain's first full gate (572b5bfb) failed
only on `tests/test_trust_ratchet.py::test_committed_budget_passes_its_check` because no allowance was recorded. The
allowance is therefore now recorded with `tools/trust_map.py --allow`, signed "SIGNED by standing ruling R6
(DRI-RULINGS.md)". The budget is not written (`--write` belongs to the merge train). The DRI should still confirm
the R6 reading or replace that signature. Every other delta is signed by a standing ruling (R1, R3, R8; DELTA rows 1
to 3).

## Delivery

The item ends rd-9's D1 exception (`manage-agents/reviews/rd-9-dri-signatures-20261015.md` item 2). The DRI decided:
Lean returns the licences and Python relays them.

| Task line | Delivery | Commit | Check |
| --- | --- | --- | --- |
| Lean returns every (mechanism, licence) pair with the binding Python re-derived | Scope.lean `Ground`, `citedBy` (the citation `cited` finds), `citedGround` and `ground` (the first relation that holds, with the request items it rests on), `ruleBarReach`; Run.lean `licence` := the text of `ground`. The elaboration writes, per line, `limitations` (Lean's `scopeLimits`), `bar` (`ruleBarReach`) and `in_scope`, and per mechanism `licence` and `grounds`. `rule_narrowings` gives, per rule, the mechanisms naming it and what each of its citations licenses | e1e567062, ba896d0f0 | `lake build`; `ResponseShape.Encoders.Rights.elaborate_fits`, `groundJson_fits` |
| … established in Lean (by construction or a proved statement): the target is its rule's, the in-scope flag, the bar reach | By construction: `target` is `scopeTargetName` (`<rule>:<mechText>`), and `licence` and `grounds` come from the one value `ground`. Proved: `licence_spec` (the licence is the first relation of Scope.lean the request holds); `ground_isSome` (grounds exactly when `licensed` without certificates); `citedBy_isSome`, `citedBy_sound` (the citation is in the request); `ground_collision`, `ground_effect`, `ground_cited`; `limPack_mem_narrowings` (the limitation mechanism iff a limitation is in scope); `bar_mem_narrowings` (the bar mechanism iff `ruleBarReach` is some) | e1e567062, ba896d0f0 | `python3 lean/audit.py` (standard axioms; in the selected run); `tools/lean_statements.py --check` |
| Python only relays and checks shape; delete `_narrowings` and its call | `_narrowings` and `_in_scope` are deleted, and so are the relay's imports of `_incompatible` and `_rank_above`. `_bind_line_narrowings` binds each mechanism, licence and grounds to the request and to Lean's own rows (R8(b)). The limitation acts of the generated predicates come from Lean's per-line `limitations`, not from a Python `inScope` | e1e567062 | `tests/test_rights_licence_relay.py::test_probe_the_relay_holds_no_copy_of_the_licence_derivation` |
| No Python, Rust or test helper keeps a copy of the derivation (F24's included) | Searched `ve/`, `tools/`, `conformance/`, `tests/` and `rust/` for the mechanism grammar, the citation keys of `cited` (`unless:`, `over:`, `narrows:`, `alterable:`), `inScope` and the licence texts. The only remaining uses are test inputs (authored `cites`), assertions on Lean's answers, the relay's parse of the mechanism text and its binding of the effect licence's text to the rule it names. Rust relays no licence | e1e567062 | the probe test above |
| Delete or reword every comment, DELTA row and FIX-REPORT line that describes the exception; the D1 row says it ended | `docs/readings-defaults/rd9-lean/DELTA.md` D1 row: **ENDED** with this item. `docs/rd-9/integration/FIX-REPORT.md`: rows F20, F24 and "Audit class", the F24 DRI note, the F27 row, the D1 decision row and the F27-M2 seed row are reworded. `_narrowings`' docstring is gone with it. `tests/test_rd9_dri_signatures.py::test_the_d1_exception_cites_narrowings_lines` is removed (with its `Test-removed` trailer); the probe test replaces it | ba896d0f0 | `tools/gate_collection.py --check --prebuilt`: 1 removed by a trailer, 0 refused, stale or malformed |
| Keep every refusal; show that a corrupted mechanism, licence, target or scope flag is still refused | All rd-9 regressions pass: F18, F20, F21, F24, the identity, prime and bar tests of `test_soft_decision_keys.py`, the inventory fuzz `test_every_bound_field_mutant_is_unavailable[*]` and the cross-request replay `test_another_requests_genuine_answer_is_unavailable[*]`. New: 23 named corruptions (mechanism renamed or dropped, licence flipped, target, scope flag, bar reach, limitations, grounds, rule rows), each refused in the elaboration alone, with the scope answer forged too, and by the elaboration binder alone | ba896d0f0 | `tests/test_rights_licence_relay.py` (71 tests) |
| Answers users see must not change; run the rd-9 rights and readings tests and the selected tests before and after | `report_rights` and `RightsDocument.instances` are byte-identical on the 25 genuine sources: at d7ea7228b, and after the sync against 8bc65a907 | 086524d89 | `evidence/user-visible-answers.json`; the test runs below |
| Trust: `tools/trust_map.py --check`, growth itemised per file, listed for the DRI | V +102 against 171faae80: `ResponseShape/Schemas/Rights.lean` +62, `VE/Rights/Run.lean` +28, `VE/Rights/Scope.lean` +12. New declarations are classified in `tools/trust-classes.json`; `licence`, `citedBy`, `citedGround`, `ground` and `ruleBarReach` are tied to their theorems | ba896d0f0 | DELTA row 4 |

Other changes the delivery needed. The relay mutation gate's allow-list adds `rule_narrowings` to the rights B0 and F4
entries and a B3 entry for the nullable `bar`; `tools/relay_mutation_gate.py --route service:rights` reports 6,549
mutants and 0 failures. `docs/CONSOLIDATION-PLAN.md` step 5 now reads tied 457, because `licence` is tied. The rights
spec (`docs/spec/rights.md`, the `rights-elaborate` row) and `lean/RIGHTS.md` name the new fields and theorems. F20's
forgery helper `_extra_mechanism` adds `grounds: null`, so that its mutant still fits the new schema.

Acceptance items are all AGENT. No HUMAN or EXTERNAL item is in scope.

## Tests

| Run | Where | Tree | Result |
| --- | --- | --- | --- |
| rd-9 rights and readings tests, before (`tests/test_rd9_*.py`, `test_rights*.py`, `test_readings_sd_*.py`, `test_readings_route_*.py`, `test_soft_decision_keys.py`, `test_relay_binding_inventory.py`) | Mac (ve-mac-1) | d7ea7228b (clean) | 604 passed |
| The same set plus `test_rights_licence_relay.py`, after | Mac | c9d3ba236 | 674 passed (604 − 1 removed + 71 new) |
| The same, after | VM | c9d3ba236 | 674 passed |
| The same plus main's `test_b16e_rights_document.py`, after the first sync | VM | merge with 8bc65a907 | 742 passed |
| Selected (`select_tests.py --base $(git merge-base HEAD main) --run`), before the sync | Mac | ba896d0f0 | 342 units; 2 failed: `test_trust_ratchet.py::test_committed_budget_passes_its_check` (this item's unsigned growth) and `test_consolidation_tools.py::test_committed_ledger_names_real_declarations` (step 5's figures; fixed in c9d3ba236) |
| Selected, before the sync | Mac | c9d3ba236 | 343 units; 1 failed: `test_trust_ratchet.py::test_committed_budget_passes_its_check` |
| Selected, final | Mac | 2334e0a8b (+ this report) | 344 units; 1 failed: `test_trust_ratchet.py::test_committed_budget_passes_its_check` |
| Chain full gate | Mac runner | 572b5bfbb | 16,645 passed, 92 skipped; 1 failed: `test_trust_ratchet.py::test_committed_budget_passes_its_check` (no allowance recorded) |
| The failed test plus `test_rights_licence_relay.py`, after recording the R6 allowance | Mac and VM | 9ffc8a6c4 | 175 passed on each |
| Selected, after recording the R6 allowance | Mac | 9ffc8a6c4 | 344 units, 0 failed |

`tools/gate.py --rerun-failed` refused to reuse the 572b5bfbb record, because the allowance commit changes the tree.
It then started a full gate, which was stopped: the chain gates the final HEAD.

The "before" selection would have selected nothing (no change against main). The before baseline is therefore the
rd-9 rights and readings set, run on main itself. No test in `main-known-red.txt` failed in these runs. The full
release gate was not run here (task instruction): the chain runs it on the committed final HEAD.

Before the allowance, `tools/regen_generated.py --check` passed every entry except `trust-tables` (the same growth).
With the allowance recorded, it passes every entry.
`tools/relay_mutation_gate.py --route service:rights` passes, and so does `tools/gate_collection.py --check --prebuilt`.

## Seeded bugs (each restored)

Recorded in [`seeded-bugs.json`](seeded-bugs.json).

| Seed | Language | File | Temporary change | Failing test |
| --- | --- | --- | --- | --- |
| L1 | Lean | `lean/VE/Rights/Run.lean` | `groundJson` writes a collision's grounds under the strict-rule tag. The build and every theorem still pass; `ve_service` was rebuilt and pinned for the run, then restored, rebuilt and its pin restored | `test_rights_licence_relay.py::test_the_genuine_grounds_name_request_items`, `::test_a_corrupted_lean_answer_is_still_refused[collision licence dropped-elaboration]` |
| P1 | Python | `ve/rights_route.py` | any collision licence accepted | `test_rights_licence_relay.py::test_a_corrupted_lean_answer_is_still_refused[effect relicensed as a collision-elaboration and scope]` |
| P2 | Python | `ve/rights_route.py` | rule-named mechanisms not compared with `rule_narrowings` | `test_rights_licence_relay.py::test_the_elaboration_binder_alone_refuses_it[a rule-named mechanism dropped]` |
| P3 | Python | `ve/rights_route.py` | every check of the scope flag dropped | `test_rights_licence_relay.py::test_the_elaboration_binder_alone_refuses_it[scope flag flipped]` |
| P4 | Python | `ve/rights_route.py` | target not tied to `<rule>:<mechanism>` | `test_soft_decision_keys.py::test_rights_elaboration_premise_identities_are_bound[undeclared narrowing target]` |
| P5 | Python | `ve/rights_route.py` | Lean's slot order reduced to uniqueness | `test_soft_decision_keys.py::test_f20_mechanisms_are_exactly_the_request_implied_slots[mechanisms out of Lean order]` |

Two first attempts survived and were replaced, because another check also refuses the same corruption. Dropping
only the cited licence's citation check survived: the `rule_narrowings` citation rows refuse it too. Dropping only
the `in_scope`/limitations comparison survived: the limitation mechanism and the node's pack refuse it. No Rust
product code changed, so there is no Rust seed.

Checklist item 10 probe: renaming the elaboration's `grounds` key in `elaboratedNarrowingsJson` breaks
`ResponseShape.Encoders.Rights.elaborate_fits` (`lake build` fails at `Encoders/Rights.lean:82`). It was restored.

## Self-review against BUILDER-CHECKLIST

1. PASS: Lean answers fully typed and contained. `grounds` is a union of closed objects and null; `bar` is null or a string; `rule_narrowings` is closed. Evidence: `tools/relay_mutation_gate.py --route service:rights` (6,549 mutants, 0 failures); `test_relay_binding_inventory.py::test_every_bound_field_mutant_is_unavailable[rights-elaborate]`; `test_route_row_schemas.py` (selected run).
2. PASS: deliverables. The table above maps each task line to its commit and test. A grep of the diff finds no new Python copy of a Lean decision (`test_probe_the_relay_holds_no_copy_of_the_licence_derivation`) and no new permanent report test: the one removed report test has its trailer, and the new tests check code, not reports.
3. PASS: tests can fail. `seeded-bugs.json` lists L1 and P1 to P5, each with its failing test.
4. PASS: valid inputs still pass, and the outputs agree. All 25 genuine sources are accepted, and their user-visible answers are identical at base and head (`evidence/user-visible-answers.json`). Rust relays no licence.
5. PASS: R8 binding. Every new field is BOUND in the inventory and fuzzed (rename, other genuine value, flip, drop, duplicate, extend, reverse) and replayed across sources: `test_relay_binding_inventory.py`; `test_rights_licence_relay.py`.
6. PASS: synced with main twice, through 171faae80. Evidence lists use `main..HEAD --no-merges` and the merge base. The gate on the final HEAD is the chain's.
7. PASS: the trust growth, whose signature the task reserved to the DRI, is named in this report's first line and in DELTA row 4. Its allowance cites R6. Rows 1 to 3 cite R3, R8 and R1.
8. PASS: every user-visible change is in DELTA. The report and the documents are unchanged (`evidence/user-visible-answers.json`); the added Lean fields, the binder texts, the trust figures and the plan figures are DELTA rows 1 to 5.
9. PASS: test selection. `select_tests.py` selected 344 units, including every changed test file. Seed P5's failing test, `test_soft_decision_keys.py`, is in the selection.
10. PASS: the Lean statements are about the returned values. `licence_spec` and `ground_isSome` are about `licence` and `ground`, which the encoder writes. The renamed-field probe breaks `elaborate_fits`. No approved statement changed: `tools/lean_statements.py --check` reports only added theorems.
11. N.A.: no budget, limit or deadline is touched.
12. PASS: no CPU regression. `evidence/lean-cpu.json`: 125 report calls with the answer cache cleared used 0.61 to 0.66 s of `ve_service` CPU at base and 0.60 to 0.66 s at head. The Python binder no longer runs the derivation.
13. PASS: `Test-removed: tests/test_rd9_dri_signatures.py::test_the_d1_exception_cites_narrowings_lines` (commit ba896d0f0). `tools/gate_collection.py --check --prebuilt`: 1 removed by a trailer, 0 refused, 0 stale, 0 malformed.
