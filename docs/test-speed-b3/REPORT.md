# Test speed batch B3: select against the branch's last passing tree

DRI signature needed: none. B3 changes developer test selection only, and the rule ships in shadow mode, so
`since_pass.py base` prints today's merge base until its activation evidence holds. No VE verdict, diagnostic,
wire field, theorem or accepted input changes. DELTA: none.

## The plan row and what delivers it

| Plan line (test-speed-research-2026-10.md, B3) | Delivered by | Test |
| --- | --- | --- |
| Fixers, rechecks and repeat gates select against their branch's last passing tree (from gate-records.jsonl), not main | `tools/since_pass.py` `choose`, `base` (727b3cfed) | `test_the_pass_closest_to_head_is_the_base`, `test_a_pass_outside_the_branchs_history_since_the_merge_base_is_not_a_base`, `test_a_pass_of_main_before_the_merge_base_is_not_a_base`, `test_a_row_whose_tree_is_not_its_commits_or_whose_commit_is_absent_is_not_a_base` |
| A pass is a passed full gate, or its failed tests rerun and passed (R13) | `PASSES`, `pass_row`, `read_passes` (727b3cfed, def6ecf78) | `test_a_rerun_that_passed_is_a_pass_and_a_failed_gate_is_not`, `test_a_gate_row_with_a_wrong_field_is_refused`, `test_a_merge_train_row_with_a_gate_key_is_another_writers_row` |
| A full run is forced after 5 steps or 24 h | `MAX_STEPS`, `MAX_AGE` in `choose` | `test_more_than_max_steps_since_the_pass_forces_todays_base`, `test_a_pass_older_than_a_day_or_in_the_future_forces_todays_base`, `test_a_sync_merge_is_one_step_and_moves_the_merge_base_past_the_pass` |
| Gate: shadow mode on 10 items | `after-gate` writes a shadow row beside every full gate whose suite completed; `check` recomputes each row; `base` uses the pass only when the committed evidence holds 10 items (branches) with no miss | `test_after_gate_writes_the_shadow_row_against_earlier_passes_then_records_its_pass`, `test_ten_items_without_a_miss_activate_the_rule_and_base_prints_the_pass`, `test_fewer_items_or_a_miss_keeps_todays_base`, `test_one_branch_under_ten_labels_is_one_item`, `test_check_refuses_every_retyped_rebound_or_dropped_field` |
| Batch rules: nightly full suite stays; unknown file, conftest, pyproject, uv.lock or a missing map still means the full suite | `select_tests.py` is unchanged and computes every plan; B3 only chooses its `--base` | `test_plan_between_is_the_select_tests_base_plan` |

## Gate status: shadow, 0 of 10 items

The gate cannot be met inside this branch: it needs shadow rows written beside live full gates of 10 items.
The committed [evidence](evidence/shadow.jsonl) is empty, `since_pass.py check` says `active: false`, and
`since_pass.py base` prints the merge base (probe on this HEAD: "rule merge-base ... shadow only (0/10 items in
the shadow evidence); base b96f04a5a1c8", equal to `git merge-base HEAD main`).

Deferred, EXTERNAL, owner: the orchestrator (the chain scripts are in manage-agents, not in this repository).
1. After every gate of a worktree, the chain runs
   `uv run python tools/since_pass.py after-gate --records $M/gate-records.jsonl --shadow $M/since-pass-shadow.jsonl --item <label> --result gate-result.json`.
   It records the gate's pass (a `gate` row) and, for a full gate whose suite completed, the shadow row.
2. Fixers and rechecks select with `--base $(uv run python tools/since_pass.py base --records $M/gate-records.jsonl)`.
   This is today's base until activation.
3. When the rows cover 10 branches with no miss, a commit copies them into `docs/test-speed-b3/evidence/shadow.jsonl`.
   `since_pass.py check` must exit 0 and report `active: true` on that commit. That commit activates the rule.

## Estimate (not the gate)

[estimate.json](evidence/estimate.json) (`estimate.py --check` exits 0) replays 14 fixed fix-round pairs
over B2's saved v7 map with `assume_fresh`. The rule selects a median of 36% of suite time, against 100% today
(means 44.9% and 93%). It is a selection-size estimate only: whether each P's gate passed is unknown, so it is
not the activation evidence.

## Sibling lessons (ts-B2 review)

- F1 (a missing dependency in the selection): N.A. B3 adds no dependency rule; every plan is `select_tests.select`'s
  for `P...HEAD`. A sync merge moves the merge base past the pass, and the rule then falls back to today's base
  (`test_a_sync_merge_is_one_step_and_moves_the_merge_base_past_the_pass`).
- F2 (retrospective evidence presented as the gate): the estimate is labelled as one. Activation reads only rows
  that `after-gate` writes beside a live full gate whose `pytest` stage ran, and today there are 0 of them.
- F3 (a saved verdict trusted): `check` recomputes `outside` and `counted` from each row's saved failures and
  plans and refuses a row whose saved lists differ (seeded bug `saved_outside_trusted`). Limit: the saved
  selection itself is not recomputed, because `check` cannot rerun the selector at a past tree with the map of
  that day. A failure counts as outside unless its test file is in the saved selection. That is conservative.

## Seeded bugs (Python; no Lean or Rust product code changed)

[mutants.json](evidence/mutants.json), written by [mutants.py](mutants.py): 19 of 19 caught (exit 1), each in
`tools/since_pass.py`. The source was restored byte for byte, and the clean source passes every test.

| Seeded bug | Failing test (tests/test_since_pass.py) |
| --- | --- |
| pass_off_the_branch | test_a_pass_outside_the_branchs_history_since_the_merge_base_is_not_a_base |
| pass_before_the_merge_base | test_a_pass_of_main_before_the_merge_base_is_not_a_base |
| tree_unbound | test_a_row_whose_tree_is_not_its_commits_or_whose_commit_is_absent_is_not_a_base |
| farthest_pass | test_the_pass_closest_to_head_is_the_base |
| step_bound_off_by_one | test_more_than_max_steps_since_the_pass_forces_todays_base |
| age_bound_doubled, future_pass | test_a_pass_older_than_a_day_or_in_the_future_forces_todays_base |
| failed_gate_is_a_pass | test_a_rerun_that_passed_is_a_pass_and_a_failed_gate_is_not |
| train_row_judged | test_a_merge_train_row_with_a_gate_key_is_another_writers_row |
| unbound_gate_record | test_after_gate_refuses_a_record_not_of_this_clean_head |
| every_failure_covered | test_a_failure_is_outside_a_selection_unless_its_file_is_selected |
| saved_outside_trusted | test_check_refuses_every_retyped_rebound_or_dropped_field |
| nine_items_activate, a_miss_activates, shadow_rule_used | test_fewer_items_or_a_miss_keeps_todays_base |
| full_rows_count | test_rows_whose_rule_selected_everything_do_not_count |
| labels_are_items | test_one_branch_under_ten_labels_is_one_item |
| detached_rows_count | test_a_detached_head_row_is_not_evidence |
| planner_not_the_base_plan | test_plan_between_is_the_select_tests_base_plan |

## What was run

- `tests/test_since_pass.py`: 97 passed.
- Selected run (`mac-pytest.sh --select`, HEAD def6ecf78): the full 376 units, because the VM has no
  coverage map. One failure: `test_regen_generated.py::test_every_script_with_a_writing_mode_is_registered_or_excluded_with_a_reason`
  (`estimate.py` was not registered). This branch caused it, and 79ed71d44 fixes it. The file then passed (38 tests).
- `tools/gate_collection.py --check --prebuilt`: 97 added, 0 removed, 0 refused, stale or malformed.
- The full release gate was not run here. The chain runs it on the final HEAD.
- Overlaps: `tools/regen_generated.py` is also edited by infra/arch-AR-1, infra/tarch-contract (other hunks) and
  infra/premise-scale (`NOT_REGENERATED`, ten lines below this branch's one-line entry). No other file overlaps.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer. The tool reads gate records and its own rows, and `check` refuses every retyped,
   rebound or dropped field (`test_check_refuses_every_retyped_rebound_or_dropped_field`, `test_a_gate_row_with_a_wrong_field_is_refused`).
2. PASS: the plan table above. No Python copy of a Lean decision, no permanent report test (`test_since_pass.py` reads
   no committed evidence), and no authority switch before the gate (`test_fewer_items_or_a_miss_keeps_todays_base`).
3. PASS: 19 of 19 seeded bugs caught (`evidence/mutants.json`). Empty evidence keeps the rule inactive
   (`test_fewer_items_or_a_miss_keeps_todays_base`).
4. N.A.: no Python, Lean or Rust checker path changed.
5. N.A.: no Lean answer is read. The gate record is bound to HEAD's commit, tree and a clean worktree (`test_after_gate_refuses_a_record_not_of_this_clean_head`).
6. PASS: synced with main (e9d5fa2cc). The gate runs on the final HEAD in the chain, and the report cites saved files only.
7. PASS: no DELTA row, no trust-budget growth. `check` exits 1 on a miss and 2 on a malformed row (`test_check_refuses_a_duplicated_row_and_a_line_that_is_not_json`).
8. PASS: DELTA none. No VE output changes, and `base` output equals today's merge base while in shadow (`test_fewer_items_or_a_miss_keeps_todays_base`).
9. PASS: the selection is the full suite, for "missing coverage map" (no map on the VM). The failing inventory test was in the selection.
10. N.A.: no Lean statement or proof.
11. PASS: the age bound uses an injected clock (`now`), with no sleep or wall deadline. A future pass is refused (`test_a_pass_older_than_a_day_or_in_the_future_forces_todays_base`).
12. N.A.: no checker code path. `after-gate` adds two selector plans per full gate.
13. PASS: `gate_collection.py --check --prebuilt` reports 0 removed, refused, stale or malformed. No test removed.
