# eff-20261104-1: `--rescore` carries across inputs that only decide the plan

Status: built; selected tests green after two fixes; no DRI signature needed; the full gate is left to the chain (not run by me).
HEAD: the commit holding this report (branch infra/eff-20261104-1); tools/trust_mutants.py and its tests, no Lean, no Rust, no DELTA rows, trust +0.
Changed: `tool_files`, `PLAN_ONLY_TOOL` (tools/layer_policy.py only), `base`, trust_map's table, and lean/checkers.lock and lean/*.md that nothing Lake or Lean reads names now go on to mode "checks"; the mutant list still decides.
Replay: 9 recorded pairs, 6 of them carry; 1,056 carried verdicts, 0 differ from the recorded full runs.
Open: `base` has no measured carry (all 3 replayed base moves also changed a selected file, so they stay full); see "What this does not show".

## The cause

The eff pass of 2026-11-04 read the `rescore` fields of 7 days of Actions parts (302 runner-h). 28 sweeps, about 60 runner-h (20%), went to a full run for a reason that is no Lean source change: "its inputs differ (tool)" 4 sweeps / 15.4 h; "(tool, base)" 4 / 15.7; "(base)" 2 / 6.9; "tools/trust-classes.json is no module of lean/ ..." 13 / 18.8; "lean/checkers.lock is no module of lean/ ..." 5 / 2.8. Those numbers are the task's; I did not recount them. `inputs()` hashes every module of tools/ and lean/ in `sys.modules`, tools/layer_policy.py among them, so a layer row for a new file forced a full sweep (df-5: 426 mutants, 6.9 runner-h, the same 389 KILLED).

## What changed

`git diff --numstat` for tools/trust_mutants.py: +96/-36. tests/test_trust_mutants.py: 660 tests collected, 564 before. Regenerated: docs/codemap/*, tests/history-dependent.json.

- `inputs`: `tool_files` beside `files`; `tool` is the same digest (`test_the_overall_tool_digest_is_what_it_was_with_each_modules_beside_it`). It is not in `files`, whose digests manage-agents/cloud-tm-verify.py recomputes.
- `previous`: a `tool` that differs only by `PLAN_ONLY_TOOL` modules, both records holding `tool_files`, and/or a `base` that differs, goes on to the existing checks. The list check ("its mutants are not this tree's") and the `Reads.carry` rule are untouched. `options` stays fixed. A full run for the tool now names the modules ("its inputs differ (tool): tools/x.py"), so the follow-up can see which module to look at next.
- `check_only`: accepts `tools/trust-classes.json` and any file `no_build_reads` accepts.
- `no_build_reads` / `lake_reads`, at run time from the tree: lean/checkers.lock or a .md under lean/, only when nothing Lake reads names it. The lock's path is `lean_share.LOCK_PINS`, its one owner.
- `rescore.plan_only` (only in mode "checks", only when non-empty) names what crossed: the modules, `base`, the table, the lean/ files. `--merge` agrees on it and binds it; `--resume` compares it through its existing facts.
- `--merge` had to change: it refused a "checks" part with `changed: []`, which a base-only or tool-only carry writes. It now needs `changed` or `plan_only`, and it refuses `plan_only` on another mode, an empty one, and a name that is neither a `PLAN_ONLY_TOOL` module, `base` nor a changed file. Every earlier refusal stands (`checks-without-changed-files` still passes).

Stricter than the task asked (each has a test in `test_a_file_lake_or_lean_may_read_is_a_full_run`): an outside --test file that names the file, a symlink under lean/ whose target names it, a name in another case (a Mac's file system ignores case), and a `readDir`, `walkDir` or `input_dir` anywhere Lake reads (a listing reads a file without naming it). This tree has no directory listing (`LISTS_FILES.search(lake_reads(...))` printed None).

On this tree (probe in the replay section's command): lean/checkers.lock is accepted; 13 of the 26 .md files under lean/ are accepted and 13 refused, because some Lean file or comment names them.

## PLAN_ONLY_TOOL

One module: **tools/layer_policy.py**. It decides nothing on the path, not even the plan. The tool loads it only because tools/check_lean_imports.py does (`from layer_policy import ROOT, lean_layer`). The tool reads one name of that module, `imports`, which parses a Lean header's text and reads neither name, so the import closure (`Reads.imported`, `plan`'s importers) is computed from the current tree alone. `lean_layer` is read only by that module's own layer check, which the tool never calls; `ROOT` by its LEDGER, its `sys.path` line and that check. `test_the_plan_only_argument_still_holds` checks each of these from the sources: only check_lean_imports imports it, only trust_mutants imports check_lean_imports and only the name `imports`, `imports` reaches no name derived from `ROOT` or `lean_layer`, and layer_policy's module level imports only `ast`, `functools`, `pathlib`, `tomllib` and has no side effect, with its `ROOT` this repository. Left out for lack of an argument: trust_map (its `statements` feed `targets`), lean_statements, regen_generated (the inventory paths), and the modules that build or judge.

## The uses of `base`

From `grep -n "\bbase\b" tools/trust_mutants.py`: `main` resolves it (exit 2 if it is no commit); `plan` passes it to `changed_lines`, which decides the selected lines and the stale-declarations stop (exit 2, no verdict); `inputs` records it and `previous` compares it (the change here); `record` and `--plan` print it; `--merge` requires the parts to agree on it (`AGREED`, unchanged); `resumable` compares the whole `inputs` (unchanged, so another base is no resume). `run`, `settle`, `judge`, `probe`, `targets` and `Reads` never read it. So no other use can change a verdict, and base is not kept fixed. A base move that also changes a file in reach stays full (`base-and-a-file-of-the-import-closure`).

The table: `classify_tree` takes its declarations from the tree (`place_tree`), and the table only sets `cls`, `tied` and `trusted`, read by `chosen` and each row's class (`grep -n "trust_class\|\.trusted"`), not by `roles`, `targets` or a verdict. A carried row takes its class from the current plan. Scratch copies lean/ only, so no build reads the table.

The lock: `Scratch` restores a shared build by `lean_share.key`, whose `lean_tree` leaves the lock out. No file Lake reads names it on this tree.

## Replay

`uv run python docs/infra/eff-20261104-1/evidence/replay.py replay` (scratch worktrees under tmp, removed after; `git worktree list | grep -c ve-replay` printed 0); result in evidence/replay-result.json, inputs in evidence/<job>/ (prev.json is the PREV committed at the later head; full-run.json the recorded parts' rows, with each part's sha256). No PREV holds `tool_files`, so both were recomputed: on all 9 pairs each tree's own modules give the recorded `tool` digest, and the recomputed lean, tests, base and options digests equal the recorded ones, except that the earlier records of qt-a3db, qt-a4 and ap-3db hold an uncommitted lean/checkers.lock (`previous` reads the recorded digests). On all 9 the plan equals the recorded full run's list.

| pair (later head) | recorded full-run reason | new decision | mutants | carried (KILLED / INVALID) | rerun (of which KILLED in PREV) | carried verdicts differing from the full run | plan_only | reason, if full |
|---|---|---|---|---|---|---|---|---|
| df-5 66190bd0 | tool | checks | 426 | 397 (389 / 8) | 29 (0) | 0 | tools/layer_policy.py | - |
| ci-2 ad415a76 | tool | checks | 306 | 269 (229 / 40) | 37 (0) | 0 | tools/layer_policy.py | - |
| cmp-s3 1506199f | table | checks | 50 | 40 (28 / 12) | 10 (0) | 0 | tools/trust-classes.json | - |
| ci-1 ec141e96 | table | checks | 248 | 142 (118 / 24) | 106 (55) | 0 | tools/trust-classes.json | - |
| qt-a3db 84930ae4 | lock | checks | 75 | 45 (41 / 4) | 30 (0) | 0 | lean/checkers.lock | - |
| cmp-s4c 7a87e0ac | lock | checks | 179 | 163 (134 / 29) | 16 (0) | 0 | lean/checkers.lock | - |
| ci-2 921abb0f | base | full | 306 | 0 | 306 | n/a | - | (lean, base): lean/ResponseShape/Schemas/Command.lean is a selected declaration's file |
| qt-a4 7163aafe | tool, base | full | 145 | 0 | 145 | n/a | - | (tool, lean, base): lean/VE/Compose/Dispatch.lean is a selected declaration's file |
| ap-3db 3cda58df | tool, base | full | 160 | 0 | 160 | n/a | - | (tool, lean, base): lean/VE/Compose/Dispatch.lean is a selected declaration's file |

The stop rule did not fire: 1,056 carried, 0 differ. Six carried KILLED rows of qt-a3db name another line than the full run (M023 and M056 carry 605 where the full run says 599): the same status, a check added in the changed file refuting first. That is the existing "checks" rule ("a carried KILLED stands on its unchanged check's refutation"). ci-1's 55 reruns are KILLED verdicts whose killing check changed.

The task describes ci-2 921abb0f -> ad415a76 as "tools/layer_policy.py and lean/ inventories only". `git diff --stat` shows a new module too: lean/VE/Commands/RunSplit.lean, with lean/VE.lean and lean/VE/Audit.lean. All three are outside every selected declaration's closure, so the decision is unchanged.

## What this does not show

- **`base` has no measured carry.** The 3 replayed sweeps whose reason named base all changed a selected file as well, so they stay full, rightly. ap-3d a838ea64 and ap-4a cb9c9dd1 (also "(tool, base)") could not be replayed: their trees lack `trust_map.inventory`, which this tool's `plan` calls; jt-2c's PREV is not committed. Base's carry rests on its tests, the real-tree one comparing with a full run. In these records, base alone saved nothing.
- **Expect the reason strings to move, not all the hours.** "(tool, base)" and "(base)" should near 0, but at least 3 of those sweeps return as "(lean, base): ... selected declaration's file", which is a real Lean change.
- **`no_build_reads` looks for names.** A module that builds a file's name from pieces and reads it, without listing a directory, is not found; the docstring says so. Dependencies under .lake/packages are not searched (lean/lake-manifest.json lists no package today). Reviewers run without --rescore.
- No real sweep was run for the replay; the replay decides and builds nothing. Each carried verdict was compared with a recorded full run, not rerun.
- `.gitignore` and any other file stay a reason for a full run, as the task said.

## Seeded bugs

docs/infra/eff-20261104-1/mutants.json (13, each with file and test; all in tools/trust_mutants.py, each planted, the named test failing on an assertion, then restored; `git status --short` clean after). Task's three first; iii, x and xi were run again on the final `no_build_reads`.

| bug | failing test (tests/test_trust_mutants.py::) |
|---|---|
| i tools/trust_mutants.py in PLAN_ONLY_TOOL | test_any_other_change_beside_a_plan_only_input_is_a_full_run[tool-tools/trust_mutants.py] |
| ii list check skipped for the new cases | test_a_plan_only_input_that_moves_the_mutant_list_is_a_full_run[base] |
| iii an include_str'd file accepted | test_a_file_lake_or_lean_may_read_is_a_full_run[include-str] |
| iv base skips the file checks | test_any_other_change_...[base-and-a-file-of-the-import-closure] |
| v an old record taken as plan-only | test_any_other_change_...[old-record-without-tool-files] |
| vi the record drops plan_only | test_a_plan_only_rescore_in_one_run_and_in_parts_gives_one_record[base] |
| vii --merge needs a changed file | test_a_plan_only_rescore_in_one_run_and_in_parts_gives_one_record[base] |
| viii parts may disagree on plan_only | test_merge_binds_rescore_to_owned_rows[plan-only-disagrees] |
| ix outside --test files not searched | test_a_file_lake_or_lean_may_read_is_a_full_run[outside-test] |
| x the search minds case | test_a_file_lake_or_lean_may_read_is_a_full_run[bare-name] |
| xi a directory listing is no read | test_a_file_lake_or_lean_may_read_is_a_full_run[read-dir] |
| xii the table not named | test_plan_only_inputs_go_on_to_the_checks_and_are_recorded[table] |
| xiii tool_files not recorded | test_plan_only_inputs_go_on_to_the_checks_and_are_recorded[plan-only-module] |

## Tests

`uv run pytest --collect-only -q tests/test_trust_mutants.py`: 660, 564 at the merge base (+96); none removed, renamed or skipped. Three existing tests changed expectations because the behaviour changed as asked: `test_any_changed_input_but_checks_gives_a_full_run` (base and the table now carry; `previous` returns a fifth value), `test_a_check_only_change_lies_outside_every_selected_file_and_its_closure` (the table moved to the accepted list; lean/SCOPE.md stays refused with no tree read), `test_the_inputs_digest_the_tools_own_source` (`tool_files` moves too). The `sharded` fixture's stub `Reads` gained `carry`.

Selected tests, `zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` (this replaces the task's ve-integration base, per the run's test-budget rule), on Actions, run eff-20261104-1-371ccb72-t862242: SHARD 2/2 17 units, 17 passed; SHARD 1/2 18 units, 17 passed; tests/test_trust_mutants.py 496 + 164 passed. Two failures, both mine: `test_gi2b_names_every_pin_reader`, in the run before that one (a literal lock path in the tool; now `lean_share.LOCK_PINS`), and `test_no_train_only_path_is_read_outside_the_accessor`, in that run (`ast.dump` in my new test read as the file's own `dump`; removed). Both passed after the fix (the second in `mac-pytest.sh -- <id>`, "2 passed"; the first in `uv run pytest`). After that run only that assert message and a docstring in `no_build_reads` changed; the whole selection was not rerun. `tools/regen_generated.py --check`: "checked 35 entries". `tests/test_hang_guards.py`: 69 passed. Full gate: not run by me; the chain runs it on the final HEAD.

## Deliverables

| task line | delivered by |
|---|---|
| 1 `tool_files`, `PLAN_ONLY_TOOL` with its argument | `inputs`, the comment above the constant, `test_the_plan_only_argument_still_holds` |
| 2 `previous`, `plan_only`, base listed | `previous`; section "The uses of `base`"; `test_plan_only_inputs_go_on_to_the_checks_and_are_recorded` |
| 3 `check_only`, run-time decision | `check_only`, `no_build_reads`, `lake_reads`; `test_a_file_lake_or_lean_may_read_is_a_full_run`, `test_what_names_a_file_elsewhere_leaves_it_unread` |
| 4 the docstring's --rescore paragraph | module docstring |
| carry tests for each case | `test_rescore_on_a_real_tree_carries_across_each_plan_only_input[plan-only-module, base, table, lock, md]`, `..._every_plan_only_input_and_agrees_with_a_full_run` (KILLED, real Lean; the package has no INVALID row); INVALID: `test_a_plan_only_rescore_in_one_run_and_in_parts_gives_one_record` (stub `carry`, M004) |
| negative: trust_mutants.py | `test_rescore_on_a_real_tree_across_the_tool_itself_is_a_full_run` |
| negative: table moves the list | `test_rescore_on_a_real_tree_across_a_table_that_moves_the_mutants_is_a_full_run` |
| negative: include_str'd file | `test_a_file_lake_or_lean_may_read_is_a_full_run[include-str]` (no Lean: the real `previous`, `check_only`, `lake_reads` on a plain tree) |
| negative: base + closure file | `test_any_other_change_...[base-and-a-file-of-the-import-closure]` (the same) |
| negative: old record | `test_any_other_change_...[old-record-without-tool-files]`, `test_a_plan_only_rescore_...[old-record]` |
| replay, stop rule | section "Replay" |
| seeded bugs | section "Seeded bugs" |
| report, follow-up | this file |

Spec re-read (the task text): "KILLED/INVALID only; SURVIVOR, UNKNOWN and ALLOWED rerun" against `Reads.carry`, unchanged; "`options` stays fixed" against `previous`'s `fixed`; "lakefile.*, lean-toolchain, lake-manifest.json" against `LAKE_FILES`; "(needs `tool_files` in both records ...)" against `tools`/`moved`; "`rescore.mode` \"checks\"" against the return of `previous`.

## FOLLOW-UPS

For the eff pass: count `rescore.full_run` reasons in cloud-jobs part JSONs for 48 h after the merge. Expected: the five reasons above near 0; new "(tool): <module>" strings show which tool module to look at next, and "(lean, base): ..." strings are real Lean changes, not waste.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer. The part's new field is typed: `test_merge_binds_rescore_to_owned_rows[plan-only-not-a-list]`.
2. PASS: section "Deliverables"; no new Python copy of a Lean decision, no permanent report test (the replay reads its evidence outside the suite).
3. PASS: mutants.json, 13 seeded; both directions below.
4. N.A.: no Python/Lean/Rust output changes.
5. N.A.: no R8 binding; `plan_only` names bound in `--merge`: `test_merge_binds_rescore_to_owned_rows[plan-only-names-an-unchanged-file]`.
6. PASS on the chain's gate at final HEAD; regen check run; gate not run by me.
7. N.A.: no DELTA row, trust +0.
8. N.A.: no user-visible VE output changes; the tool's record gains `tool_files` and `rescore.plan_only`. Readers checked: cloud-tm-verify.py and actions-health.py (grep of their `inputs` and `rescore` uses).
9. PASS: `tools/select_tests.py --base ...` selects 32/544 units with the changed tests; seed: `tests/test_gen_inv_design.py` and `tests/test_inventory_path.py` caught my two slips through that selection.
10. N.A.: no Lean.
11. N.A.: no budget or deadline code.
12. PASS: `lake_reads` reads each Lake-read file once per rescore that has a changed file; 12.7 MB on this tree (probe printed 12697106 characters); `plan` already reads these sources. Not timed.
13. PASS: no test removed or renamed; none owes a trailer.
14. PASS: both directions: `test_plan_only_inputs_go_on...` / `test_any_other_change...`, `test_a_file_lake_or_lean_may_read...` / `test_what_names_a_file_elsewhere_leaves_it_unread`; claims cite commands above; spec re-read listed.
15. No overclaim: PASS, the limits are in "What this does not show" and the docstring. No silent cut: PASS, "Deliverables". Every new check can fail: PASS, mutants.json. Limits charged before work: N.A., no limit added.
