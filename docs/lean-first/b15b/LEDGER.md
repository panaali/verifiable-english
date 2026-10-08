# Batch 15b owner and deletion ledger

Plan: `git show design/lean-first:docs/LEAN-FIRST-PLAN.md` (draft 3), sections 1 (rule 3, rule 4), 4 (the 15b
preservation obligation), 5.1 and 5.2 row 15b. The rule-3 condition was measured first
([`rule3.json`](evidence/rule3.json), [REPORT](REPORT.md)); it does not hold, so this batch deletes the rest of
its list and keeps the three rule-3 duplicates, listed unfinished.

## Deleted

| # | Deleted decision site (base) | What it decided | Owner now | Caller now |
|---|---|---|---|---|
| D1 | `ve/search.py` `_find_countermodel_python`, `_find_distinguishing_model_python`, the enumerator (`_models`, `_order_models`, `_relation_assignments`, `_subsets`, `_domain_sizes`, `_int_terms`, `_int_value`, `ORDER_SEARCH_MAGNITUDE`), the shared model pool (`model_search_scope`, `_query_models`, `_models_with_terminal_error`, `_read_shared_models`, `_SearchSpaceLimit`) | the default authority's countermodel and distinguishing-model search: candidate order, counts, charging, `NotFound`/`ResourceLimit` | Rust's search (`rust/ve-profile/src/search.rs`, `order.rs` `order_search`), untrusted generator (rule 3) | `ve.search.find_countermodel` and `find_distinguishing_model` under every authority (`execute(..., rust, lean=rust, rust=rust)`) |
| D2 | `ve/search.py` `_nonvacuous` (Python traversal over `_Evaluator`) | whether a search witness is non-vacuous | Lean `VE.Route.NonVacuity` (`ve_metered`, kind `non-vacuity`) | `ve.search._nonvacuous`, a relay declared in the manifest (`countermodel.search` binding) |
| D3 | `ve/evaluate.py` `evaluate` lean path: Rust's `evaluate-budgeted` answer (value, count, trace, `ResourceLimit`) with Lean checking the value only | the reported evaluation count, trace and exhaustion | Lean `VE.Route.Metered`, `MeteredTrace` (`ve_metered`, kind `evaluate-budgeted`) | `ve.evaluate._evaluate_lean` under the `lean` and `rust-experimental` authorities |
| D4 | `ve/document.py` `check_document`'s `model_search_scope` | sharing the Python enumerator's model stream across a document's searches | none needed (Rust enumerates per query) | — |
| D5 | Rust `surface.rs` (the `ve-surface` crate), `route.rs`, and the `ve` binary's parse/format/evaluate/countermodel commands, `label`/`dependency-order` kinds and source/canonical branch | a third parser and printer, label and dependency-order checks with no runtime caller in `ve/` | Lean (`parse`, `route` `label`/`dependency-order`), Python relays | see the [REPORT](REPORT.md) Rust section |

`tools/relay_lint.py` passes. No consumer of a deleted symbol remains in `ve/`, `tools/` or `conformance/`
(`tools/inventory_lint.py` lost its exception for `_find_distinguishing_model_python`; the 15a tests that used
`_nonvacuous` as their oracle read its frozen answers, `tests/nonvacuity_oracle.py`).

## Retained, listed unfinished

| Site | Why it stays | Removed by |
|---|---|---|
| Rust `eval.rs` and the order evaluator in `order.rs` (rule-3 duplicate 1) | the 15b condition fails: Lean evaluation of every candidate misses the bluedot search deadline (REPORT); generator-internal, never reported: evaluation counts and traces reported to Python are now Lean's (D3); Rust's search counters, which the measurement shows equal to Lean's on every row, are still Rust's | the lead's decision on question 10 |
| The provers' internal Python replay (`entailment.py` `_Replayer`, `_check_certificate_python` with `_background=False`, `order.py` `replay_trace`, `closure.py` derivations) (rule-3 duplicate 2) | the condition is one decision for all three duplicates; its own rows pass (REPORT) | the lead's decision on question 10 |
| `ve/evaluate.py` `_Evaluator` and `_evaluate_validated` (the plan's "rewire `norms`, `cedar`, `readings`, `model`") | the default authority is still `python` (batches 12b and 13b, which make Lean the default for environments, models and the core operations, have not merged): `FiniteModel.from_dict`'s defined tables, Background validity, readings, norms, norm defaults, Cedar and the default countermodel check evaluate in-process; rewiring them before 12b/13b changes every default-authority answer path | batch 15b follow-up after 12b and 13b |
| Lean checking every witness under the default authority | Lean's route refuses environments Python accepts (English `verbalisation` fields on sorts, predicates and constants); under the default authority the witness check stays `check_countermodel` under the run's authority, non-vacuity is Lean's under every authority | batch 12b (Lean's environment mode accepts every profile Python's does) |
| Rust's `check`, `evaluate-budgeted` and `readings-superposed-evaluate` kinds | `check` is the `rust-experimental` typing path (not on 15b's list); `evaluate-budgeted` has no caller in `ve/` after D3 but is the conformance tooling's Rust evaluation leg; the readings S2 shadow is batch 3's | batch 18 |
