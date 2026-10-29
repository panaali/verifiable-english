# rd9-docroute build report

BLOCKED: the refusal-to-answer DELTA needs a DRI signature; `msg.sh` could not write its read-only inbox.
HEAD: `feature/rd9-docroute` (see `git log -1` for the final local commit).
Changed: soft document claim-graph admission now reaches Lean's `norm-defaults` fill route; direct unfilled soft checks still refuse.
Open: DRI decision, final-head chain gate, and the next constitution pilot audit.
Pilot bytes: 0 newly formalised bytes from routing alone; the previous probe reported 215 CHECKED source bytes, not a checked document answer.

## Plan and spec rows

| Row or directive | Delivery | Evidence and owner |
| --- | --- | --- |
| RD-9 spec 3.8 and norm-defaults spec 2.3: fill runs last on a soft document | `6deb6a2d4` routes document admission through the existing Lean `NormDefaults.Run.runCase`, whose `layeredRoute` chooses the filled soft tree | AGENT: `test_soft_chain_document_checks_the_filled_route` compares the document report with that route's direct answer; `test_filled_soft_layer_matches_ordinary_w1` checks a generated `unsaid__` layer against Lean's ordinary W1 admission. |
| RD-9 plan D8 / SC-8: soft document under `norm-defaults@0` is admitted | `6deb6a2d4` and the small committed fixture `2425b8a4e` | AGENT: `test_soft_chain_document_checks_the_filled_route`; `probe.json`. |
| Keep the direct unfilled soft refusal and the no-profile refusal | The existing Lean direct route and W1 guard stay in place | AGENT: `test_direct_soft_check_of_unfilled_tree_still_refuses`, `test_direct_w1_outcome_of_unfilled_soft_tree_still_refuses`, `test_unspecified_without_profile_keeps_its_own_refusal`. |
| R8: typed and request-bound relay | Admission fields are checked by the existing schema and report binder; `conditional_on` is checked against Lean's elaboration of the same source. The admitted variant is checked against that Lean row. | AGENT: `test_soft_admission_row_fields_are_typed`, `test_soft_admission_conditions_are_bound_to_the_source`. |
| Original pilot probe before and after | Before is copied from the 06:00Z `soft-chain-probe.json`; the small fixture has an exact before/after check in `probe.json`. The full pilot after is deferred under L70. | EXTERNAL: next pilot audit owns the whole-document result. |
| Document seed inventory | The new small fixture is classified as `FAIL_CLOSED` for Lean's document wrapper, whose composed-route deferral is expected; Python's document path answers it. | AGENT: `test_every_seed_document_agrees_with_python_or_fails_closed` passed after this inventory entry. |
| DELTA signature | Not delivered. The new availability is not signed by R1–R18; prior RD-9 B1 signed a different, earlier readings availability item. `msg.sh dri rd9-docroute` failed with `read-only file system` at the DRI inbox. | HUMAN: DRI decision required before review-ready. |

No theorem statement was added or changed. No Lean or Rust product code changed. No generated-file input changed, so regeneration, Lean build/audit and trust mutants are N.A. The local branch started clean at `main` `71b1d27ad`. An in-flight branch scan found no overlap in the handwritten files touched. `tools/trust_map.py --check` measured K +0, S +0, D +0, G +0, trusted +0 against that base. Handwritten additions are below the 600-line item limit (`git diff --numstat`); no work was cut.

## Reproduction and seeded bugs

The 06:00Z pilot probe loaded, then its check returned 1 with the exact through-fill refusal; the 18:00Z file records the same. On the small committed fixture, check returned 1 before the repair and 0 after. The after report has `admission.admitted: true`, a direct filled-route report equality, and `premises.status: model` (`probe.json`). No full pilot document was run.

Each temporary mutation was restored before the final code:

| Seeded bug | File | Failing test |
| --- | --- | --- |
| Skip fill by sending document admission to the direct soft route | `ve/document/report.py` | `test_soft_chain_document_checks_the_filled_route` failed with the original `UnsupportedProfile` |
| Elaborate the fill twice | `ve/norm_defaults_route.py` | `test_soft_admission_elaborates_fill_once` failed on the extra Lean call |
| Supply Lean's already filled base environment to admission, applying fill at the wrong stage | `ve/norm_defaults_route.py` | `test_soft_chain_document_checks_the_filled_route` failed with `UnsupportedProfile: norms@0 is required` |
| Remove the direct W1 unfilled guard | `ve/norms.py` | `test_direct_w1_outcome_of_unfilled_soft_tree_still_refuses` failed with the different soft-route refusal |
| Accept an unbound `conditional_on` label | `ve/norm_defaults_route.py` | `test_soft_admission_conditions_are_bound_to_the_source` failed (`DID NOT RAISE`) |

## Tests and limits

Named fixture, binding, refusal, plain-soft and W1 admission tests passed during iteration. The one selected run on the Mac covered 489 test files and found one failure: the document seed inventory had not classified the new fixture. The sole failed ID, `tests/test_lean_document_wrapper.py::test_every_seed_document_agrees_with_python_or_fails_closed`, passed on its targeted rerun after the two-line inventory fix; the selection was not rerun. Core admission and norms files account for the broad selection. `tools/trust_map.py --check` passed. No full gate, whole pilot, model call or push was run. The final full gate belongs to the chain on the committed HEAD. The next item is WG-0, followed by WG-5 after the part-document design `const-part-doc`.

## Self-review against BUILDER-CHECKLIST

1. PASS — `test_soft_admission_row_fields_are_typed` checks each genuine admission field's type and presence; `test_soft_admission_conditions_are_bound_to_the_source` covers the variant relation.
2. PASS — plan rows and the DELTA are mapped above; `test_soft_chain_document_checks_the_filled_route` covers D8/SC-8.
3. PASS — the five seeded bugs above failed named tests; `test_soft_admission_elaborates_fill_once` pins the one-fill call count.
4. PASS — `test_soft_chain_document_checks_the_filled_route`, `test_filled_soft_layer_matches_ordinary_w1`, `test_plain_soft_document_keeps_its_admission_route`, `test_document_graph_admits_the_layer_of_fill_u`, and `test_every_seed_document_agrees_with_python_or_fails_closed` cover the new and retained paths.
5. PASS — `test_soft_admission_conditions_are_bound_to_the_source` rejects absent and duplicated labels; `test_soft_admission_row_fields_are_typed` rejects absent and retyped fields.
6. N.A. — the chain runs the final-head gate after handoff, as this item explicitly directs.
7. N.A. — blocked on the DRI signature recorded in DELTA; the DRI inbox is read-only here.
8. PASS — the single new availability delta is in `DELTA.md`; `probe.json` records both small-fixture outcomes.
9. PASS — the Mac `--select` run selected `test_rd9_docroute.py` and `test_lean_document_wrapper.py`; its one failed ID passed on targeted rerun.
10. N.A. — no Lean statement or proof changed (`git diff --name-only main...HEAD`).
11. N.A. — no budget, deadline or evaluator changed; `test_direct_soft_check_of_unfilled_tree_still_refuses` retains failure behavior.
12. N.A. — L70 forbids a full constitution pilot check; the small fixture's CLI probe is in `probe.json`.
13. N.A. — no test was removed or renamed (`git diff --name-status main...HEAD`).
