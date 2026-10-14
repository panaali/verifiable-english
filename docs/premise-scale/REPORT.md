# premise-scale: per-sort domain budget, ground-fact route, measured Rust limit

**DRI signature needed: DELTA rows 1, 2, 4, 5, 6 and 8.** The pre-review relay failure on
`service:graph` is fixed below. The all-route mutation run still has 11 pre-existing findings on
`service:route` and `service:parse` (follow-up 5); none is in the graph route or this batch's
`search-budget` route. (UNKNOWN or unavailable becoming a Lean-checked
model, as DRI decisions QT2, ME1 and ME2 direct; a changed Rust limit; a new service mode and search
options; CPU on documents that now get an answer). Rows 3 and 7 are signed by R3 and R6.

Branch `infra/premise-scale`, built on `infra/oom-rootcause` (merged first, `46213c31f`) and synced with
main three times: `f98183bf` (`b07a7cfa1`), `4667e8de` (lf-14d and runner-portability, `e91311b1a`) and
`8594f1d05` (repo-map-untracked, `3d56a0873`). DRI decisions 2026-10-13 QT2, ME1, ME2 and ET1
(`debates/plan-synthesis/DRI-DECISIONS-PHASE2.md`). Times are UTC.

## Summary

The premise-consistency check searched models only up to two entities per sort. It now:

1. **Raises a sort only where the premises force more entities.** Lean counts the entities a premise set
   forces in each sort (`VE.SearchBudget.demand`: constants stated pairwise distinct, or the variables of a
   head `∃ x₁ … xₖ` chain stated pairwise distinct) and proves the count is a lower bound for every model
   (`demand_sound`). A sort whose count exceeds the shared bound 2, up to a cap of 8, is searched at exactly
   that size (`sortBounds`, `sortBounds_spec`, `sortBounds_sound`); every other sort keeps bound 2, so the
   vector count stays (3^k for k unraised sorts) and lazy, as `infra/oom-rootcause` left it. The budget is
   Lean's: service mode `search-budget`, read by `ve.search.premise_budget` (schema and binding only).
2. **Takes ground stated facts as their own model.** After the search finds nothing, the Rust search builds
   one candidate from the premises' ground facts (numerals equated to integer constants, stated bounds,
   equated object constants, unary, binary and n-ary atoms) and checks it against the premises; Lean
   checks it again before it is reported. H's 217 stated quantities: one candidate, 0.03 s.
3. **Reads a Rust timeout in the premise search as "no witness"** (ME1): the check goes on to Lean's
   contradiction replay, and answers with Lean's result or UNKNOWN.
4. **Scales the Rust model search's wall-clock limit by the case's measured cost** (ME1): 4 × (2.47 s +
   7.42e-5 s per byte + 2.11e-4 s per constant²), at least 5 s; other Rust calls keep 5 s.

On the pilots: QT-0p's repaired whole constitution goes from UNKNOWN to a Lean-checked model with three
principal types (`anthropic`, `operators`, `users`); math-evidence H, V, V's appendix and DL go from
UNKNOWN or CheckerUnavailable to a model; UDHR part01 with three (and six) added sorts keeps its model at
the same CPU. Every answer that was `model` or `INCONSISTENT` is unchanged (A/B over 22 documents).

## Directive lines and what delivers them

| Directive (DRI-DECISIONS-PHASE2.md and the task) | Commit | Test or evidence |
|---|---|---|
| QT2 (b): lazy domain sizes | `b0ac5ba1d` (infra/oom-rootcause, merged in `46213c31f`) | `lazy_sizes_are_the_eager_order`; UDHR part01 +3/+6 sorts answered (below) |
| QT2: a per-sort domain budget that finds models needing 3+ objects of one sort; raise only the sorts that need it | `ae074090f`, `42db8229e` | `test_lean_raises_only_the_sort_the_premises_force`, `test_an_existential_chain_raises_its_sort`, `test_no_sort_is_raised_within_the_shared_bound_or_past_the_cap`, `test_exactly_three_principal_types_has_a_lean_checked_model_at_size_three`, `a_raised_sort_is_searched_at_its_size`; Lean `#guard`s in `VE/SearchBudget/Examples.lean` |
| QT2 / ME2: a route for ground stated facts (no search) | `ae074090f` | `test_stated_quantities_give_their_own_model`, `test_contradictory_stated_quantities_stay_inconsistent`, `ground_route_on_stated_quantities`, `a_ground_candidate_the_premises_reject_is_no_witness` |
| Budgets and limits are Lean's (no duplicated logic) | `ae074090f`, `24fbd0973`, `a55f3f9b2` | `test_the_readings_budget_is_leans`, `test_search_budget_answer.py` (one- and two-fault mutants), relay gate `service:search-budget` 957/957 refused |
| The three places named: `premise_status`, the readings route's `BUDGET`, the document mode's premise check | `ae074090f`, `a55f3f9b2` | `test_vacuity.py`, `test_readings_budget_zero.py`, `test_document_mode_premise_check_of_qt0p_content` |
| ME1: Rust limit set by measurement, scaled by document size; Lean's answer stands on a Rust timeout | `24fbd0973`, `037c00531`, `f46cf80c5` | `test_the_default_limit_grows_with_the_case`, `test_a_rust_timeout_is_no_witness`; `evidence/rust-timeout.json` |
| ME1: pilots use a raised `VE_RUST_TIMEOUT` and say so | evidence | the constitution rows ran at `VE_RUST_TIMEOUT=900` on both sides (the norm-defaults coverage search, not the premise check, timed out at the base's 5 s under load); also measured at HEAD's default limit |
| ET1: premise-scale before any pilot batch that adds sorts | evidence | UDHR part01 +3 and +6 sorts: `model`, CPU unchanged |
| Measure: constitution with QT-0p's content (a model at size 3, Lean-checked), H/V/DL, UDHR part01 + 3 sorts; time and memory before and after | `524110047` | `evidence/pilots-*.json`, `evidence/ab-documents.json` |
| No weakening of any check; nothing refuted or proved changes verdict | | A/B: 15 of 22 documents identical, the 7 others only UNKNOWN → model (DELTA 1, 2); `test_a_model_the_shared_bound_finds_is_unchanged`, `test_contradictory_stated_quantities_stay_inconsistent`, `test_raised_bounds_stay_in_the_unknown_budget`, `test_a_zero_model_budget_stays_unknown`, `test_readings_budget_zero.py` |

No directive line is deferred.

## Design notes

- **Soundness does not rest on the count.** `demand` only steers an untrusted search. A model is reported
  only after Lean checks it; a wrong count can lose a model (UNKNOWN), never invent one. `demand_sound`
  shows why raising a sort loses nothing: no model has fewer entities of that sort, and a sort is raised
  only when its count exceeds the shared bound, so no model the shared bound admits is excluded.
- **Order of the searches.** The shared-bound search runs first, as before; the raised search and the
  ground route run only when it found nothing. So every model the base found is the model reported
  (`test_a_model_the_shared_bound_finds_is_unchanged`; A/B).
- **The readings route's budget.** `BUDGET` was a Python copy of the same four numbers. It now reads Lean's
  (`ve.search.lean_budget`, one call per process); a test's override stands in for it, so the budget-zero
  sweep still zeroes every search. The raised search runs within the route's budget, with Lean's sort
  bounds only at Lean's own domain bound (a review-time catch: the first version ran at Lean's numbers and
  found a model under a zero budget; `test_readings_budget_zero.py` failed, and is one of the seeded faults).
- **The Rust limit is the client's transport guard,** like the 5 s it replaces, not a semantic budget: it
  only decides how long the client waits for an untrusted answer. Its numbers are a measurement
  (`evidence/rust-timeout.json`), not a copy of a Lean value.
- **Limits of the count.** Only constants stated pairwise distinct and head existential chains are
  counted. "Exactly three" written another way (a counting quantifier, a numeric cardinality, distinctness
  under a disjunction) raises nothing and stays UNKNOWN, as before. A sort needing more than 8 entities
  stays at the shared bound (UNKNOWN).

## Measurements

Before is `46213c31f` in a separate worktree with its own Lean and Rust builds; after is HEAD. Both run
side by side under `iso.sh` (24 GB cap) and `prlimit --as=6 GiB`, one fresh process per pilot. The machine
was loaded (load average 64 to 113 on 32 cores; other agents' builds), so wall times are noisy; CPU is the
check's process and every process it waited for, the Lean service included. Median of 3 runs (the two
constitution documents: 2, at `VE_RUST_TIMEOUT=900` on both sides). Memory: the largest child's peak RSS
(the Lean service) and the Python process's.

| Pilot | Bytes | Premises before | Premises after | Wall s (before / after) | CPU s | Peak child MB | Python MB |
|---|---:|---|---|---|---|---|---|
| QT-0p companion | 7,590 | UNKNOWN | model | 2.5 / 2.2 | 0.9 / 0.7 | 81 / 86 | 26 / 25 |
| math-evidence M (control) | 12,631 | model | model | 3.1 / 3.3 | 0.8 / 0.8 | 83 / 92 | 25 / 25 |
| math-evidence V | 57,763 | CheckerUnavailable (Rust timeout) 2/3, UNKNOWN 1/3 | model | 7.9 / 18.1 | 2.2 / 5.3 | 83 / 94 | 25 / 26 |
| math-evidence V appendix | 34,181 | UNKNOWN 2/3, CheckerUnavailable 1/3 | model | 8.4 / 14.2 | 3.0 / 4.0 | 84 / 95 | 27 / 27 |
| math-evidence DL | 268,666 | UNKNOWN 1/3, CheckerUnavailable 2/3 | model | 38.6 / 82.8 | 8.3 / 16.3 | 90 / 96 | 45 / 44 |
| math-evidence H (217 constants) | 1,219,270 | CheckerUnavailable (Rust timeout) | model | 49.1 / 107.3 | 12.3 / 21.6 | 139 / 145 | 44 / 44 |
| UDHR part01 + 3 sorts (ET-0 `u042`, 16 sorts) | 47,500 | model | model | 33.6 / 24.1 | 6.4 / 6.5 | 85 / 91 | 34 / 33 |
| UDHR part01 + 6 sorts (`u042u043`, 19 sorts) | 50,400 | model | model | 39.2 / 43.1 | 8.0 / 8.3 | 84 / 91 | 34 / 33 |
| Constitution + QT-0p (run 0600Z, repaired) | 418,074 | UNKNOWN | **model, principal_type = 3** | 250.3 / 259.5 | 63.0 / 67.0 | 92 / 97 | 42 / 41 |
| Constitution baseline (control) | 415,456 | model | model (identical) | 206.9 / 197.4 | 40.9 / 32.7 | 91 / 97 | 41 / 40 |

- The repaired constitution's model: `principal_type` = {e0, e1, e2} with `anthropic`, `operators`,
  `users` distinct and each one of Claude's types, checked by Lean's readings route (`readings-model`).
- At HEAD's default Rust limit (no `VE_RUST_TIMEOUT`) both constitution documents complete with `model`
  (140 s and 68 s wall at load about 60, `evidence/pilots-after-constitution-default-limit.json`); at the
  base's 5 s, and at the earlier constants-only limit (6 s), both were CheckerUnavailable at load 100 to 130.
- Before main merged `infra/oom-rootcause`, UDHR part01 with added sorts was CheckerUnavailable (ET-0's
  `part01.u042*.check.json`: the eager 3^16 vector list); that change is the OOM batch's, measured there.
- Pilot sources: QT-0p (`ve-p1-quantities`, `experiments/quantities-phase1/out/qt0p/…/nd-all.ve.md` and
  `docs/research/evidence/quantities/qt0p/constitution-u0042-u0043.ve.md`), math-evidence ME-0
  (`ve-p1-math-evidence`, `docs/research/evidence/math-evidence/*/source*.ve.md`), ET-0
  (`ve-p1-events-time-causation`, `…/et0/part01.u042*.ve.md`). Each row records the file's SHA-256.

### The Rust limit (ME1)

`measure_rust_timeout.py` ran each of the 98 search cases the pilots sent (recorded through a pass-through
wrapper) alone, with no timeout, plus a synthetic series of ground-fact cases (25 to 800 integer constants,
and 25 constants with the premises repeated 2 to 16 times). Over the 25 runs that spent the 10,000-model
budget (the longest a premise search runs), least squares gives 2.4734 s + 7.4237e-5 s/byte +
2.1123e-4 s/constant², worst case 1.74 × its fit. The fit by constants alone (the first version, 2.80 × worst)
missed the constitution's searches: 5 constants, 60 kB of premises, 11.5 s each, for a limit of 6 s. H's
search (217 constants, 50 kB) took 9.0 s at load 110 (ME-0's 47 s was the whole check at that time); its
limit is now 65 s. The limit is 4 × the fit (2.3 × the worst case's margin). Measured at load 102 to 122,
so the times are high, and the limit errs long; it only bounds a wait for an untrusted answer.

## Tests run

- Lean: `lake build` (893 jobs), `python3 lean/audit.py` PASS (487 files, 5,797 theorems), `lake build
  ve_english_lean_bench`; Rust: `rust_build.py test --locked --all-features` all pass; `rust_build.py
  --check` pinned; `regen_generated.py --check` 23 entries fresh; layer checks pass; `trust_map.py --check`
  PASS.
- Selected tests: `select_tests.py --base $(git merge-base HEAD main)` selects all 377 units (a shared field
  of `ve/assurance-manifest.json` changed: this batch's `other_json` entry for `VE/SearchBudget/Run.lean`,
  which the selector never narrows). Earlier, a run of this batch's own and related test files failed
  `test_readings_budget_zero.py` (8 cases), fixed in `a55f3f9b2` (above). The selection, run in 4 chunks at
  `-n 8`: 15,048 passed, 6 failed:
  - `test_stage2_dispatch.py::test_rust_wait_is_the_default_unless_configured`: the scaled limit applied
    to every Rust call; fixed in `f46cf80c5` (model searches only).
  - `test_lean_document_wrapper.py::test_every_seed_document_agrees_with_python_or_fails_closed`: the new
    fixture is a seed; listed as fail-closed (Lean's document mode refuses readings@1), `f46cf80c5`.
  - `test_readings_defaults_rd6b_report.py::test_trust_growth_is_rd6b_entry_and_listed_for_signature`:
    the baseline must be the current tree; `trust_map.py --write`, `f46cf80c5`.
  - `test_regen_generated.py::test_every_script_with_a_writing_mode_is_registered_or_excluded_with_a_reason`:
    the batch's scripts registered as recorded-once, `fbe264acd`.
  - `test_difffuzz.py::test_ci_run`: timed out at 1,800 s. Not load: the new seed shifted the bounded sample
    onto a pre-existing disagreement on the UDHR seed (follow-up 1), and minimising it on the 374 kB
    document ran past the limit. The base passes the same test in 23 min. Fixed in `f1b322ac2`; rerun
    with `test_lean_document_wrapper.py`: 182 passed.
  - `test_readings_defaults_rd8_report.py::test_review_fix_commit_chain_and_final_gate_target`:
    **pre-existing, not fixed**. It compares saved 8-character hashes with `git log %h`, which now prints
    9 characters as the shared object store grew. It fails the same way on the base worktree.
  Each fixed test passed on rerun; the files changed after the chunks ran were rerun
  (`test_premise_scale.py`, `test_stage2_dispatch.py`, `test_lean_document_wrapper.py`,
  `test_readings_defaults_rd6b_report.py`, `test_lean_first_b12_report.py`, `test_regen_generated.py`,
  `test_difffuzz.py`).
- Relay mutation gate. Before the second sync: 40 routes, 110,152 mutants, 0 failures, after pruning 42
  stale allow-list paths (`a8d92f06b`; stale on the base too, `--route service:norms` fails the same way
  there: the OOM merge's readings relay refuses those mutants). After syncing with main `4667e8de`: 41
  routes, 112,414 mutants, **26 failures** (`evidence/relay-mutation-gate.json`), every one on
  `service:graph`, `service:route` or `service:parse`, and every one also a failure of main `8594f1d05`
  itself (main has 30 on those routes; the other 4 are stale paths this branch already pruned;
  `evidence/relay-gate-vs-main.txt`). They came with main's re-recorded relay fixtures (lf-14d): 22
  accepted mutants (emptied, duplicated or rebound `background`, `premises`, `generators`; parse's
  `error` and `span`), 2 untyped (`service:graph` `background/*/ast/*`), and 4 stale allow-list paths.
  `service:search-budget`: 957 mutants, all refused.
- After the syncs: a curated run of the 12 test files main changed, this batch's tests, and the relay,
  schema, pin, manifest, trust, document and readings tests (36 files): 2,420 passed; `test_difffuzz.py`:
  94 passed; `test_repo_map.py`: 29 passed; `regen_generated.py --check`: 23 entries fresh; `lean/audit.py`
  PASS (489 files, 5,801 theorems). The measurements and seeded faults ran at `524110047`, before the last
  two syncs; neither sync changed this batch's code.
- The full release gate was not run by me (the chain runs it on the final HEAD).

## Seeded bugs

`docs/premise-scale/seed_faults.py` plants each fault, shows its test fails for the fault (a failure at a
hash or lock check is refused), restores the source, and checks the restored binaries are the pinned ones.
All 12 caught (`evidence/mutants.json`):

| # | Language | File | Fault | Failing test |
|---|---|---|---|---|
| 1 | Rust | `rust/ve-profile/src/search.rs` | a raised sort is searched at the shared bound | `premise_scale::a_raised_sort_is_searched_at_its_size` |
| 2 | Rust | `rust/ve-profile/src/search.rs` | the same, through the release binary | `test_exactly_three_principal_types_has_a_lean_checked_model_at_size_three` |
| 3 | Rust | `rust/ve-profile/src/ground.rs` | the ground candidate leaves out unary facts | `premise_scale::the_ground_route_tries_the_stated_facts_alone` |
| 4 | Rust | `rust/ve-profile/src/search.rs` | the ground candidate is reported unchecked | `premise_scale::a_ground_candidate_the_premises_reject_is_no_witness` |
| 5 | Python | `ve/search.py` | the budget row is not bound one entry per sort | `test_search_budget_answer.py::test_one_fault_mutants_are_refused_or_change_nothing` |
| 6 | Python | `ve/vacuity.py` | the premise check skips the ground route | `test_stated_quantities_give_their_own_model` |
| 7 | Python | `ve/vacuity.py` | a Rust timeout is a failure, not "no witness" | `test_a_rust_timeout_is_no_witness` |
| 8 | Python | `ve/readings_verdicts.py` | the scaled readings search takes Lean's budget over the route's | `test_readings_budget_zero.py::test_budget_zero_every_verdict_op_is_unknown` |
| 9 | Python | `ve/backends/rust_jsonl.py` | the Rust limit ignores the case's size | `test_the_default_limit_grows_with_the_case` |
| 10 | Lean | `lean/VE/SearchBudget/Run.lean` | the row states a domain bound one above the budget | `test_lean_raises_only_the_sort_the_premises_force` |
| 11 | Lean | `lean/VE/SearchBudget/Budget.lean` | a sort is raised past the cap | `test_no_sort_is_raised_within_the_shared_bound_or_past_the_cap` |
| 12 | Lean | `lean/VE/SearchBudget/Budget.lean` | a raised sort's most is one above its demand | the build fails inside `sortBounds_spec` (item 10) |

## Follow-ups

1. **Pre-existing Python/Lean disagreement on the document surface** (found by difffuzz, identical on the
   base): the UDHR pilot seed with `reading_sets[30].rejected_history` retyped to an object is
   `InvalidInput: invalid rejected reading history` from Python (owner readings) and `ok` from Lean's
   document mode. Owner: the readings route (Lean's document mode should refuse it). Not fixed here.
2. `test_readings_defaults_rd8_report.py` compares abbreviated hashes of a fixed length (pre-existing).
3. The norm-defaults coverage search (`ve/norm_defaults.py`) times out at 5 s on the constitution under
   load on the base; HEAD's scaled limit covers it, since it is a model search.
4. "Exactly N" in forms the count does not read (counting quantifiers, cardinalities) stays UNKNOWN.
5. **Main's relay mutation gate fails on `service:route` and `service:parse` after this fix** (30
   findings at `8594f1d05`, 26 on this branch before the graph repair, 11 now). The graph AST and label
   are typed; its two remaining accepted whole-list mutations are listed at exact B0 paths. The route and
   parse findings concern their existing response shapes and fixtures. Owner: those routes' relay contracts.

## Pre-review relay repair (2026-10-14, `8808fb359`)

- `ResponseShape/Schemas/Graph.lean` now types every regenerated background AST with the shared
  `generated_formula` grammar, and restricts its label to `background:` plus a Lean-owned generator.
  `response_schemas.py` regenerated `graph.json`; the graph encoder theorem and the full Lean build pass.
- The B0 allowance lists only the exact `service:graph` whole-background list paths. Three graph
  allowance paths for `supporting_edges` were stale and removed. The graph mutation run went from the
  pre-review's 12 findings to zero: 4 fixtures, 786 mutants, 764 refused, 22 permitted semantic-content
  mutations. The complete relay run found 11 findings, all on `service:route` and `service:parse`.
- `lean_statements.py` refreshed `declarations.txt` after the Lean source changed; no theorem statement
  changed. `lean/audit.py` passed (489 sources, 5,801 theorems), and `trust_map.py --check` reported zero
  trusted-line growth. `regen_generated.py --check` passed all 23 entries.
  `test_route_row_schemas.py`, `test_stage2_graph.py` and
  `test_regen_generated.py`: 91 passed. The branch selector chose all 377 units due the earlier shared
  assurance-manifest change; its foreground rerun was stopped after 74 passing files. The chain runs the
  full release gate on the committed final HEAD.
- This repair changes no VE verdict, diagnostic, limit, or displayed value. The graph response schema
  rejects malformed or undeclared generator labels and malformed background formulas earlier as
  `CheckerUnavailable`; the application's graph projection comparison already refused those values.

## Self-review against BUILDER-CHECKLIST

1. PASS for this batch's route and the graph repair (the all-route relay gate's other 11 findings are
   follow-up 5). Every field of the `search-budget` row is typed in `search-budget.json` (rendered from
   `ResponseShape/Schemas/SearchBudget.lean`, encoder theorem `runCaseReported_fits`) and retyped,
   dropped, duplicated and reordered one and two faults at a time: `test_search_budget_answer.py`
   (`test_every_field_is_typed`, `test_one_fault_mutants_…`, `test_two_fault_mutants_…`); relay gate 957/957.
2. PASS. Directive table above, each line with its commit and test; diff grep: no new permanent report
   test, no Python copy of a Lean decision (the readings `BUDGET` copy is removed: `test_the_readings_budget_is_leans`).
3. PASS. 12 seeded faults in Rust, Python and Lean (`evidence/mutants.json`), none caught at a hash step.
4. PASS. Base against head over 22 documents, whole answers compared (`evidence/ab-documents.json`); Lean
   checks every model the Rust search proposes (`check_countermodel`, `readings-model`).
5. PASS. The row binds each entry to the requested sort at its position and refuses a renamed, extra,
   missing or empty entry: `test_an_answer_to_another_request_is_refused`, `test_one_fault_mutants_…`;
   inputs: undeclared sort or bad bounds refused, `test_search_options_are_checked`,
   `test_rust_refuses_malformed_search_options[*]`, `sort_bounds_name_declared_sorts_in_order`.
6. N.A. for me: the chain runs the full gate on the final HEAD. Synced with main `8594f1d05`; the evidence
   commit list is `evidence/commits.txt` (`main..HEAD --no-merges`).
7. PASS. Every DELTA row is signed by a named ruling or listed as "DRI signature needed" in this report's
   first line; the trust growth (+5 V) is recorded under R6.
8. PASS. DELTA rows 1 to 8, from the A/B (only the 7 changed documents differ, only in the listed fields).
9. PASS. The selection is all 377 units because the manifest's shared `other_json` changed (by design of
   the selector); a seeded change to `ve/vacuity.py` alone selects `tests/test_premise_scale.py`
   (`select_tests.py --paths ve/vacuity.py`).
10. PASS. Seeded fault 12 breaks the build inside `sortBounds_spec`; the theorems are about the values the
    runner returns (`sortBound`, used by `runCase`). No approved statement changed; the `check_*_statements`
    tools cover other profiles.
11. PASS. Zero budgets stay UNKNOWN: `test_a_zero_model_budget_stays_unknown`,
    `test_raised_bounds_stay_in_the_unknown_budget`, `test_readings_budget_zero.py`; the Rust limit is
    tested with an injected stand-in (`test_the_default_limit_grows_with_the_case`), no sleeps.
12. PASS. Base and HEAD timed side by side on the constitution and UDHR pilots (CPU unchanged where the
    answer was already a model, `evidence/pilots-*.json`); the raised search enumerates only the raised
    sort's size (`DomainSizes::bounded`, lazy), and the ground route checks one candidate
    (`models_checked` ≤ 1, checked in `find_countermodel`).
