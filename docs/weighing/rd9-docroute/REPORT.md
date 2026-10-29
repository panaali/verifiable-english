# rd9-docroute build report

STOP (L52): F6 is fixed, but the graph-free soft-chain availability DELTA needs a DRI signature; the claim-graph row alone is signed (reviews/dri-decisions-20261029-rd9-docroute.md item 1).
HEAD: `feature/rd9-docroute` (see `git log -1` for the final local commit).
Changed: soft document claim-graph admission and premise reporting use Lean's filled tree, generated vocabulary, and free norm selection; direct unfilled soft checks still refuse.
Open: DRI signature for graph-free availability, merge-train gate, and the next constitution pilot audit.
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
| DELTA signature | The DRI signed the expanded row in `reviews/dri-decisions-20261029-rd9-docroute.md` item 1; commit `b3f062755` records it in `DELTA.md`. | HUMAN: completed by the DRI. The seven tests named in the decision passed in the selected run. |

No theorem statement was added or changed. No Lean or Rust product code changed. No generated-file input changed, so regeneration, Lean build/audit and trust mutants are N.A. The local branch started clean at `main` `71b1d27ad`. An in-flight branch scan found no overlap in the handwritten files touched. `tools/trust_map.py --check` measured K +0, S +0, D +0, G +0, trusted +0 against that base. Handwritten additions are below the 600-line item limit (`git diff --numstat`); no work was cut.

## Reproduction and seeded bugs

The 06:00Z pilot probe loaded, then its check returned 1 with the exact through-fill refusal; the 18:00Z file records the same. On the small committed fixture, check returned 1 before the repair and 0 after. The after report has `admission.admitted: true`, a direct filled-route report equality, and `premises.status: model` (`probe.json`). No full pilot document was run.

Each temporary mutation was restored before the final code:

The review fix round ran probes F1, F2 and F3 before the fix; each failed with the reported wrong status, `UnknownSymbol`, and through-fill refusal, respectively. All three probes passed after the fix. The new regressions cover the generated norm layers, `Fill_T`, soft coherence, a strict contradiction, and a soft document without `readings@1`. A temporary mutation of `ve/document/report.py` omitted Lean's filled norm layers; `test_filled_soft_premises_make_a_contradiction_vacuous` failed (`model` instead of `INCONSISTENT`). It was restored and recorded in `seeded-bugs.json` for review-ready F-ready1. No Lean or Rust product code changed in this round.

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
7. PASS — the DRI signed the DELTA row in `reviews/dri-decisions-20261029-rd9-docroute.md` item 1; `b3f062755` records the signature.
8. PASS — the single new availability delta is in `DELTA.md`; `probe.json` records both small-fixture outcomes.
9. PASS — the Mac `--select` run selected `test_rd9_docroute.py` and `test_lean_document_wrapper.py`; its one failed ID passed on targeted rerun.
10. N.A. — no Lean statement or proof changed (`git diff --name-only main...HEAD`).
11. N.A. — no budget, deadline or evaluator changed; `test_direct_soft_check_of_unfilled_tree_still_refuses` retains failure behavior.
12. N.A. — L70 forbids a full constitution pilot check; the small fixture's CLI probe is in `probe.json`.
13. N.A. — no test was removed or renamed (`git diff --name-status main...HEAD`).

## Review fix round (2026-10-29)

| Finding | Fix | Regression | Commit |
| --- | --- | --- | --- |
| F1 | Report premises now include Lean's filled norm layers, `Fill_T`, soft premises and background | `tests/test_rd9_docroute.py::test_filled_soft_premises_make_a_contradiction_vacuous`; `test_soft_fill_uses_every_lean_generated_premise_class` | `b6b590294` |
| F2 | Graph assumptions are decoded in the report's filled vocabulary | `tests/test_rd9_docroute.py::test_filled_graph_leaves_decode_in_the_filled_vocabulary`; `test_soft_coherence_graph_leaf_uses_filled_vocabulary` | `b6b590294` |
| F3 | The lower soft document is built from the placeholder with or without `readings@1` | `tests/test_rd9_docroute.py::test_soft_chain_without_readings_uses_the_filled_route` | `b6b590294` |
| F-ready1 | Seeded a dropped filled-layer bug in the changed Python file, observed the regression fail, restored it and committed `seeded-bugs.json` | `tests/test_rd9_docroute.py::test_filled_soft_premises_make_a_contradiction_vacuous`; review-ready `[mutants]` PASS | `b6b590294` |
| F4 | A shared base predicate projection removes source `regulated` and `instruction_of` metadata before comparing with Lean's filled vocabulary; the report accepts valid declarations in both readings variants | `tests/test_rd9_docroute.py::test_filled_soft_source_instruction_declarations_match_lean_base[False]`; `[True]` | `6b9ba415d` |

The first selected run exposed two history lint failures and three frozen readings ID mismatches from applying the filled report context to the readings CLI. Regenerating `tests/history-dependent.json` fixed the lint; keeping the filled context inside `_report` preserved the frozen readings IDs. The five failed IDs passed targeted checks after that fix, and all 21 focused tests passed locally. `lake build` and `python3 lean/audit.py` passed. The final `mac-pytest.sh --select` run covered 489 selected units on the Mac, with zero failures and none left unrun (snapshot `fe540373`, code commit `b6b590294`). No full gate or full suite was run in this fix round, as directed.

## F4 recheck fix (2026-10-29)

The original F4 probe raised `CheckerUnavailable` before the fix and passed after it. Both new regression variants failed before the fix and passed after it. A temporary mutation of `ve/softnorms.py` retained `instruction_of`; both variants failed again, and the mutation was restored (`seeded-bugs.json`). The complete `test_rd9_docroute.py` file passed (18 tests). The selected Mac run covered 139 units on the code snapshot for `6b9ba415d`, with zero failures (tree `9c3a958271`). `lake build` and `python3 lean/audit.py` passed. The three known-red main tests listed in `main-known-red.txt` were not changed and did not fail in this selection. No Lean or Rust product code changed; no full suite or release gate was run, as directed.

## F5 recheck fix (2026-10-29)

F5 -> The filled report now sends Lean the free norm units selected by the loader's `_free_norms`, excluding units replaced by active reading sets and units attached to open sets -> `tests/test_rd9_docroute.py::test_filled_soft_premises_exclude_norm_replaced_by_assertion_reading[authored]` and `[open]` -> `e620911e8`.

The exact F5 probe failed before the fix (`INCONSISTENT` instead of `model`) and passed afterward. The regression checks both reading-set statuses and keeps a strict, unreplaced norm as a contradictory control. A temporary mutation that dropped the active-set exclusion failed the authored regression; it was restored and recorded in `seeded-bugs.json`. The focused file passed all 20 tests. `lake build` and `python3 lean/audit.py` passed. No Lean or Rust product code changed. The three tests in `main-known-red.txt` remain pre-existing and were not edited. No full suite or release gate was run, as directed.

The selected run on `dcf922a36` exercised 146 units on the VM after the Mac connection timed out. Two failed: `test_one_selection_serves_both_python_paths` counted two callers of `_free_norms` before the report became a third, and `test_fsf_r2_probes_rerun_equals_saved_probes` found the saved graph-free DF-c probe stale. The call-site test now covers all three uses. `measure_r2.py` regenerated the saved probe, changing only DF-c's document status from `UnsupportedProfile` to `CHECKED`, and `test_fsf_r2_probes_record_lean_s_answer_on_each_merged_item` now asserts it. The two failed IDs and the new assertion passed on targeted reruns. The graph-free availability change has its own DELTA row, awaiting a DRI signature under L52; the earlier claim-graph decision does not sign it.

## F6 recheck fix (2026-10-29)

F6 -> The filled report now passes the loader's compiled units to the shared `_free_norms` selector, as the other document paths do -> `tests/test_rd9_docroute.py::test_filled_soft_report_selects_compiled_units` (four variants) -> `0c5e47feb`.

The exact F6 probe failed before the fix with `KeyError: 'content'` and passed afterward. The regression combines present or omitted norm content with flat or `MIXED` units. A seeded mutation back to raw metadata made three variants fail (`KeyError: 'content'` or `'kind'`); it was restored and recorded in `seeded-bugs.json`. This is a Python document-route fix; no Lean or Rust product code changed. The three tests in `main-known-red.txt` remain pre-existing and were not edited. The graph-free availability row remains unsigned under L52.
