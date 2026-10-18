# Test architecture rank 3: history-dependent tests and evidence binding (tarch-histdep)

First line: **no DRI signature needed.** DELTA rows 1 and 2 are covered by R3 and R13. No Lean, `ve/` or Rust file
changes.

This is the rank-3 follow-on of `test-architecture-2026-10-14.md` draft 2, section 3.4 and rank row 3, with Astra's
re-check applied where it differs. tarch-b8 (on main) had already converted the report tests to saved evidence. This
batch lists every remaining test that reads git history, lints the list in the gate, and binds every history-dependent
result to its commit, runner and toolchains. The work started from `b5248038` and was synced with main `2d4b9320`.

## Delivery

| Plan row or directive | Commit | Delivery | Test |
|---|---|---|---|
| List every remaining git-reading test as `tests/history-dependent.json`, derived from the coverage map's units that start git, not by hand; each entry names the test and why | `52784c48c`, `77c9a14f0` | `tools/history_tests.py --save-map` saves `tests/history-map.json` from the map the selector uses (`find_map` at the merge base; here `de309d61`, version 7, 428 units). It records each unit that started git and each function the unit ran that starts git or reads `.git` in the source. `--write` derives the list from that extract plus a scan of each test file's own source. An entry has `test`, `why` (the git subcommands and the files that run them), `recorded` (`coverage map`, `source`) and `via` (each function, with what it does). Both files are registered in `tools/regen_generated.py` (`history-map` json, `history-tests` regenerate) and in docs/merge-tooling.md. | `test_every_unit_the_saved_map_saw_start_git_is_listed`, `test_the_extract_counts_a_start_only_where_the_map_saw_git_and_a_read_wherever_it_ran` |
| `tools/history_tests.py` with a lint that runs where the other repository lints run, so it can fail in the gate | `52784c48c`, `2f66f10fa` | `--check` fails on a unit that starts git or reads `.git` and is not listed (`missing`), on an entry that differs from what `--write` gives (`changed`), and on a malformed list or extract. `tests/test_history_tests.py::test_the_tree_passes` runs it on the tree inside the gate's suite, like `test_identity_lint`. `regen_generated.py --check` runs it too. | `test_the_tree_passes`, `test_the_command_line_lint_passes_on_the_tree`, `test_a_malformed_list_or_extract_fails`, `test_an_edited_entry_or_map_header_fails` |
| A test that starts git (or reads `.git`) and is not listed fails | `2f66f10fa` | — | `test_a_new_test_that_runs_git_log_and_is_not_listed_fails`; seeded bug H1 |
| A listed test that no longer reads git is reported as stale | `2f66f10fa` | It is printed as `stale:` with exit 0, and `--write` drops it. It is stale when its unit is gone or none of the functions that made it read history still does. | `test_an_entry_whose_unit_no_longer_reads_history_is_reported_stale_without_failing`, `test_a_unit_found_only_through_the_map_is_stale_once_its_function_stops_starting_git` |
| Evidence of a history-dependent result binds commit, tree, runner and toolchains and is never carried to another commit: check it holds and say where | `69fb3318f`, `66983f6cc` | See "Where a history-dependent result is bound" below. Two places did not hold and are fixed: `gate.py --rerun-failed` and the run cache. | `test_the_same_tree_on_another_commit_or_runner_runs_the_full_gate`, `test_a_run_that_reads_history_is_used_only_on_its_commit_runner_and_git`, `test_a_full_gate_records_its_tree_and_mode`, `test_poisoned_toolchain_variables_do_not_reach_real_tools` |
| R2 and R3 stay complete, live and without reuse; the list must not let any merge or nightly skip a test; nothing weakens what is checked | `c6de68038` | Only the lint, its test and the registry (which runs the lint as writer and checker) name the list. No gate, merge, selection or cache code reads it. The merge train has no tree reuse (merge-train.sh, "No reuse ... no identical-tree reuse of any PASS"), so the plan's 3.2 step 4 shortcut is not built. The two binding changes only refuse or rerun more. | `test_only_the_lint_reads_the_list`; seeded bug H17 |
| No timing-threshold correctness test | — | None added. The tests use `HANG_TIMEOUT` for their subprocesses. | — |
| Seeded bugs: a new `git log` test that is not listed; one entry deleted; one per behaviour | `66983f6cc`, `c6de68038` | `docs/test-architecture/histdep/mutants.json`, H1–H17, run by `tools/mutants.py`: 17/17 killed (`mutants-evidence.json`) | below |

## The list

On the merged tree, **94** test units read history. That is 93 from the map plus `tests/test_b16f_senses_document.py`,
which main added after the map was recorded; the per-file scan finds it from its own `git` calls.
- `recorded`: 61 entries through the coverage map only, 32 through both the map and their own source, 1 through
  source only.
- **How the scan and the map agree:** of the map's 428 units, exactly the 93 it recorded starting git ran a function
  that the source scan finds starting git. No unit started git without such a function, and none ran one without
  starting git. All 32 test files that start git themselves are among the 93. The map's 3 opaque units are all among
  them too.
- **Why the units read history:**
  - 51 load a frozen oracle by `git show <pinned commit>:<path>` (`conformance/frozen_norm_defaults.py`, also
    `conformance/frozen_words.py`). For 47 of them this is the only git they start.
  - The rest run the repository tools that ask git (`tools/gate.py`, `trust_map.py`, `gate_collection.py`,
    `test_map.py`, `select_tests.py`, `batch_evidence.py`, `source_graph.py`, `regen_generated.py`, ...), or build
    their own fixture repositories.
- **`.git` reads:** the map's recorder skips `.git` (tools/test_map_recorder.py:83), so these are found through the
  functions a unit ran. Two units read `.git`:
  - `test_gate_integrity` reads `.git/index` of a fixture repository;
  - `test_run_cache` opens a fixture repository's `.git/HEAD`.

What a site is (`tools/history_tests.py` `sites`):
- **Starts git:**
  - an argument vector whose first element is the string `"git"`;
  - a process call whose command string starts with `git`;
  - a use of a module- or class-level vector such as `GIT = ("git", ...)`, attributed to the code that uses it, not
    to the import.
- **Reads `.git`:** `.git` used as a path: joined, passed to a call, or assigned. A compared name, a name in a list
  of skipped names, or a name passed to a string-matching method does not count.

Each site is attributed to the `co_qualname` of the code object that runs it, which is the name the map records.
`test_genexpr_class_body_and_default_sites_carry_the_code_objects_qualname` checks this against compiled code objects.

**Limits:**
- **Starts the map can miss.** It records git started by a Python process of the project environment. Every such
  start in the extract is explained by a source site. A start by another program would give an entry with no `via`,
  and none exists today.
- **New git calls in already-mapped helpers.** If code that a mapped unit already ran gains a git call, the scan of
  the test's own file does not see it. That unit is listed only after `--save-map` from a newer map. A test file's
  own new git call is caught at once (H1).
- **Per-file granularity.** The map's unit is the test file, so the entry is per file. `via` names the test
  functions in the file that start git themselves.
- **Churn.** Editing a git call in a listed unit's own file, or in a function its `via` names, changes the generated
  entry. The lint then asks for `--write`, as for any generated file. The same happened here after the sync with
  main.

## Where a history-dependent result is bound

| Where a result is recorded or reused | Binding before | Now | Test |
|---|---|---|---|
| The gate record (`gate-result.json` and its git note, tools/gate_collection.py) | commit, tree, `dirty`, toolchains (Lean, Lake, Rust, Cargo, uv, Python, lock digest, paths); runner not named | adds `runner` (system, machine, node) and git's version and path (DELTA row 1) | `test_a_full_gate_records_its_tree_and_mode`, `test_poisoned_toolchain_variables_do_not_reach_real_tools` |
| `gate.py --rerun-failed`: the only place in the repository that keeps another gate's test results | tree and toolchains only, so a same-tree gate of another commit (an amend, an empty commit, a merge whose tree is unchanged) carried its other tests' results, history tests included | the same commit and runner are required as well, as R13 says (DELTA row 2) | `test_the_same_tree_on_another_commit_or_runner_runs_the_full_gate` (another commit, another runner, no runner) |
| The run cache (tools/run_cache.py): `test_wire_gate_corpus` reuses a nested run of 32 test files keyed by content. Several of those files read history (the norm-defaults oracle's `git show`; checked: a recorded run of `test_norm_defaults_differential.py` reports `history: ["git"]`) | content only: an entry was used on any commit with the same inputs, in every worktree of the checkout | a run that started git or opened a `.git` path (seen by tests/read_recorder.py) also binds the commit, the runner and `git --version`, and is used only while all three are unchanged. An entry is not stored when the commit cannot be named. Format 2, so format-1 entries are never used | `test_a_run_that_reads_history_is_used_only_on_its_commit_runner_and_git` (git, git through a shell, a `.git` path × another commit, runner, git), `test_a_run_that_reads_no_history_is_used_on_another_commit_with_the_same_files`, `test_a_run_that_reads_history_where_no_commit_can_be_named_is_not_stored`, `test_an_entry_of_the_format_before_history_binding_is_not_used`, `test_the_read_recorder_sees_git_started_or_a_git_path_opened` |
| R2, the merge train's candidate gate (manage-agents merge-train.sh) | the full live gate on the exact candidate commit; no branch verify and no tree reuse; the published commit is the gated one | unchanged; the list is not used for any reuse (`test_only_the_lint_reads_the_list`) | — |
| R3, the nightly (`gate.py --no-quarantine`, `VE_RUN_CACHE=off` set by manage-agents mac-gate-wrap.py / nightly-vm-verify.sh) | live, no cache | unchanged | — |
| Saved batch evidence read by report tests (tarch-b8's B11b, RD8 and others) | saved numbers and full commit ids; each test runs live in every gate | unchanged | — |
| Selection (R1: `select_tests.py --base`, `since_pass.py`) | carries "passed on the base" for unselected tests, history tests included | unchanged: selection is not evidence, and R2 runs every test live | — |

Outside this repository, for the orchestrator:
- `review-ready.py` accepts, for its pre-review check only, a passing gate of an ancestor of HEAD when only `docs/` or
  `*.md` changed after it. R2 still gates the candidate live.

**Cost of the run-cache binding.** The corpus's nested run reads history, so it now hits only on the commit it ran on.
An R2 candidate gate is on a new commit, so it now runs that nested run live. It may have hit before, when main's new
commits changed none of its keyed inputs. That is at most the nested run's own time (about 1,180 s of test time, by
the run_cache docstring) on such a candidate. Builder reruns on the same commit still hit. The nightly already ran it
live.

## Seeded bugs

All are Python (no Lean or Rust file changed). They are in `mutants.json` with `file` and `tests` keys. `tools/mutants.py` checks
that the named tests pass unmutated, applies each bug, requires a named test to fail and restores the file's
bytes. The result is **17/17 killed** (`mutants-evidence.json`, rerun on the merged tree).

| Bug | File | Fault | Test that failed |
|---|---|---|---|
| H1 | `tests/test_heavy_tests.py` | a new test that runs `git log` in an unlisted file | `test_history_tests.py::test_the_tree_passes` |
| H2 | `tests/history-dependent.json` | the `tests/test_ar8_evidence.py` entry deleted | `test_the_tree_passes`, `test_deleting_any_entry_of_the_committed_list_fails` |
| H3 | `tools/history_tests.py` | stale entries fail instead of being reported | `test_an_entry_whose_unit_no_longer_reads_history_is_reported_stale_without_failing` |
| H4 | `tools/history_tests.py` | stale entries are not reported | the stale test above, `test_a_unit_found_only_through_the_map_is_stale_once_its_function_stops_starting_git` |
| H5 | `tools/history_tests.py` | a named vector's use is not a site | `test_argument_vectors_shell_strings_and_named_vectors_are_sites_of_the_code_that_runs_them`, `test_the_tree_passes` |
| H6 | `tools/history_tests.py` | a compared `.git` name counts as a read | `test_a_git_path_is_a_read_but_a_compared_or_listed_name_is_not` |
| H7 | `tools/history_tests.py` | the extract counts a git function for a unit the map never saw start git | `test_the_extract_counts_a_start_only_where_the_map_saw_git_and_a_read_wherever_it_ran` |
| H8 | `tools/gate.py` | no commit check in `rerun_refusal` | `test_gate_rerun.py::test_the_same_tree_on_another_commit_or_runner_runs_the_full_gate` |
| H9 | `tools/gate.py` | no runner check in `rerun_refusal` | the same test |
| H10 | `tools/gate.py` | git's version not recorded under `toolchains.git` | `test_gate_integrity.py::test_poisoned_toolchain_variables_do_not_reach_real_tools` |
| H11 | `tools/gate.py` | the record's runner left empty | `test_gate_rerun.py::test_a_full_gate_records_its_tree_and_mode` |
| H12 | `tools/run_cache.py` | no history inputs added for a run that read history | `test_run_cache.py::test_a_run_that_reads_history_is_used_only_on_its_commit_runner_and_git` |
| H13 | `tools/run_cache.py` | `current` ignores the history inputs | the same test |
| H14 | `tools/run_cache.py` | the format left at 1 | `test_an_entry_of_the_format_before_history_binding_is_not_used` |
| H15 | `tests/read_recorder.py` | git started through `sh -c` not seen | `test_a_run_that_reads_history_is_used_only_on_its_commit_runner_and_git` |
| H16 | `tests/read_recorder.py` | a `.git` path opened not seen | the same test |
| H17 | `tools/gate.py` | the gate reads the list | `test_only_the_lint_reads_the_list` |

The first run of the harness counted six of these bugs as surviving, although each made its test fail. The harness
reads failed IDs as `\S+`, so it cannot match a parametrized ID with a space in it. The new tests' IDs now have no
spaces (`66983f6cc`).

## Runs

- **Selected tests, Mac runner, before the sync** (`89d4899a`): 363 units, all passed (2,558 s, `mac-pytest.sh
  --select`). The run before that (`69fb3318`) failed `test_history_tests` correctly, because the run-cache tests had
  gained git calls after the list was generated. The fix was to regenerate.
- **After the sync and the last test changes:**
  - Local runs pass: `test_history_tests` (14), `test_gate_rerun`, `test_gate_integrity`, `test_run_cache` and
    `test_merge_tooling_evidence`.
  - The selected run on the final code (`e10ba73c`, base main `2d4b9320`): **377 units, all passed**, on ve-mac-1
    (1,672 s, `mac-pytest.sh --select`; `tests/test_hang_guards.py` among them).
- `tools/gate_collection.py --check --prebuilt`: 17,280 collected, 31 added, 0 removed, 0 refused, 0 stale, 0
  malformed (after `lake build`, 959 jobs).
- `tools/regen_generated.py --check --only history-tests` and `--only gitattributes` pass.
- The full gate was not run by the builder; the chain runs it on the final HEAD.
- Main's known red tests (main-known-red.txt) are not touched.

**Selection (BUILDER-CHECKLIST 9).** `select_tests.py --base 2d4b9320` selects 377 of 432 units, for two causes:
- `.gitattributes` changed, which registering the two generated files requires. That alone selects every unit that
  runs git: 277 units.
- The nearest map (`b5248038`) is 70 changed files behind, which leaves 369 units uncertain (rank 4's map freshness).

A seeded change to `tools/history_tests.py` (H3) on the working tree selects 102 units, `tests/test_history_tests.py`
among them.

## Follow-ups (not in this batch)

1. **The candidate regen list.** Add `history-tests` to manage-agents `cand-regen-entries.txt` once a candidate has
   failed on it. Its writer reads only the tree and the saved extract (about 6 s). Until then, a candidate whose two
   sides each add history readers fails `test_the_tree_passes` with "run `python tools/history_tests.py --write`".
2. **Refreshing the extract.** Re-save it (`--save-map`) when a newer map is recorded, so that new git calls in
   helpers already mapped are listed. Today these are caught only when a unit's own file changes.
3. **R1 selection.** It could always add the listed units when the base differs from HEAD. That adds tests and never
   skips one, but costs 94 units. It needs a DRI decision on cost, and it is outside rank 3.

## Self-review against BUILDER-CHECKLIST

1. N.A. No Lean answer is read or relayed differently; no `ve/` change.
2. PASS. The delivery table above maps each plan row and directive to a commit and test. The list is generated
   (`test_the_tree_passes`, the regen entry). No report test of this batch's HEAD is added (D4); the batch's numbers
   are in this report and `mutants-evidence.json`.
3. PASS. 17 seeded bugs, 17 killed (`tools/mutants.py docs/test-architecture/histdep/mutants.json`). A missing entry
   (H2), an extra stale entry (H3, H4) and an edited entry (`test_an_edited_entry_or_map_header_fails`) are each caught.
4. N.A. No Python, Lean or Rust checker behaviour changes.
5. N.A. No relayed field.
6. PASS. Synced with main `2d4b9320` before the final runs. The chain runs the full gate on the final HEAD.
7. PASS. DELTA rows 1 and 2 cite R3 and R13 with their tests. The new refusal's status is checked on each refused
   path (`test_the_same_tree_on_another_commit_or_runner_runs_the_full_gate`: the status is `passed` from the full gate,
   never `rerun-passed`).
8. PASS. DELTA.md lists the record's new fields and the rerun rule. VE outputs are unchanged (no `ve/`, Lean or Rust
   change). `test_a_run_that_reads_no_history_is_used_on_another_commit_with_the_same_files` shows that the cache keeps
   what it kept for a run that reads no history.
9. PASS. Selection explained above; the seeded H3 change selects `tests/test_history_tests.py`.
10. N.A. No Lean statements.
11. PASS. No budget or deadline logic; the new tests use `HANG_TIMEOUT` (`tests/test_hang_guards.py` in the selected
    run).
12. PASS. No product algorithm changed. The lint takes about 6 s on the tree; `test_only_the_lint_reads_the_list`
    parses only the files that name the list (a text prefilter). There is no timing test.
13. PASS. No test removed or renamed relative to main (`gate_collection.py --check --prebuilt`: 0 removed, 0 refused,
    0 stale, 0 malformed).
