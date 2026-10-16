# tarch-select: selection map freshness and precision

DRI signature needed: none. No VE output changes (DELTA.md: 8 tooling rows, each directed by the batch prompt, none pending).

Rank 4 of `test-architecture-2026-10-14.md` (draft 2, section 3.5 "Map freshness and precision first", items 2-6), with Astra's re-check points 6 and 9.3. Work started at main `dae12d5ff` and was synced with main at `c99a3156b`. This batch owns `tools/select_tests.py`, `tools/source_graph.py` and `tools/test_map.py`. It also touches `tools/test_map_recorder.py` (the `["c", ...]` child record, 14 lines) and adds one registry line to `tools/regen_generated.py`. tarch-cutoff's opt-in hook point in `select_tests.py` is untouched: there is no answer-level cutoff here.

**R2 and R3 are unchanged.** `tools/gate.py` (the merge train's full live gate) and `tools/gate.py --no-quarantine` (the nightly) run the whole collection. They read no map, no build record and no selection. Nothing in this batch is on their path. A stale map or a missing build record still means "select everything" in R0/R1.

## Delivery

| Plan line | Delivery | Commit | Test |
|---|---|---|---|
| 2. `find_map` drops `tree-*` maps before its 30-newest window | `commit_maps` filters them before the window is counted | `9d1028f77`, `8a7b699ad` | `test_tree_maps_do_not_crowd_commit_maps_out_of_the_window` |
| 2. Freshness checks use `find_map`, not file mtimes | `tools/test_map.py fresh --base REV [--max-age-hours 24] [--max-behind N]`: prints the map selection would use and exits 0, or gives the reason on stderr and exits 1. The orchestrator commands are below; `verify.sh` and `fixloop.sh` are not edited | `9d1028f77` | `test_freshness_is_the_map_selection_would_use` |
| 3. Record the 9 unrecorded units | Per-unit timeout raised from 3,600 s to 14,400 s, and units start longest first. A killed child of a hooked process no longer makes its unit opaque, and a nested recording hands its records to the outer one. Measured below: 7 of 9 now recorded | `9d1028f77`, `8c95ae589` | `test_recording_starts_the_longest_units_first`, `test_a_child_that_records_here_and_left_no_file_ran_nothing`, `test_a_child_records_here_only_if_the_hook_started_this_process`, `test_a_recording_inside_a_recorded_test_hands_over_its_records` |
| 4. Narrow the directory-name literal match (`source_graph.py:203-206`); skip product literals as `:197` does for "." | In a `ve/` or `ve_experiments/` module, a bare name stands only for the product's own directories of that name. `Path(__file__).parent / "packs"` still works; `"evidence"` no longer names 51 directories | `9d1028f77` | `test_a_product_word_names_only_product_directories`, `test_an_evidence_file_selects_its_readers_not_every_unmapped_unit` |
| 5. `.gitattributes` as data | `.gitattributes` (in any directory) is data. Its readers include every unit that runs git, since git is what reads it. An edit to a line that can change checked-out bytes still selects everything, failing closed on unknown syntax. That covers a checkout attribute, a macro either version defines, an `[attr]` line or a quoted pattern | `9d1028f77` | `test_a_merge_driver_edit_of_gitattributes_selects_its_readers_and_git_users`, `test_only_checkout_attribute_edits_of_gitattributes_change_everything` (14 cases) |
| 5. Narrow the manifest's shared fields to their recorded field readers (`select_tests.py:509-511`) | A shared-field edit selects the units that read the whole manifest: the file read, or `ve.manifest.all`, through which `ve` hands out shared fields. `version`, which every importer checks, still selects everything. Found and fixed on the way: an operation's `authority`, read at import by the authority guard, now also selects the registrations of its entries | `9d1028f77` | `test_a_shared_manifest_field_selects_its_whole_manifest_readers`, `test_an_authority_change_selects_the_registrations_of_its_entries` |
| 6. Binary-level cutoff for Lean executables | `tools/test_map.py build-record` records, per `lean/` tree and platform, the SHA-256 of every `lean_exe`. It records only a current build: Lake's `--no-build` passes and no trace is stale. Every `record`, `update` and `--run` build records one. A test is then selected through an executable only if its digest differs between the base and head records. Lean source readers, `lake`/`lean` users and pin readers still select by file. A missing record, equal trees or a Lean change of unknown contents disable the cutoff. `--run` builds the head first when only its record is missing | `9d1028f77`, `86e0b3336` | `test_an_identical_rebuild_selects_no_runner`, `test_a_changed_binary_selects_all_its_runners`, `test_without_both_build_records_every_runner_is_selected`, `test_no_cutoff_when_the_trees_cannot_show_the_change`, `test_a_build_record_needs_a_current_build_of_one_tree`, `test_a_current_build_is_up_to_date_and_traced`, `test_a_run_builds_the_head_for_the_cutoff_when_the_base_build_is_recorded` |
| Astra 6: a format change ships with a recorded map or a converter; a test fails otherwise | `FORMAT_CHANGES` names how each `VERSION` became usable, and `CONVERTERS[7]` converts version-6 maps (no modes recorded, so every service user stays selected). The cached v6 maps (`f98183bf`, `da0c04bd`, `49de179e`) are usable again | `9d1028f77` | `test_each_map_format_version_ships_with_a_converter_or_a_recorded_map`, `test_a_version_6_map_converts_and_keeps_every_service_user` |
| Item 1: `tools/test_map.py update` works on a published commit, and the command is documented | Dry run on main `dae12d5ff` with this branch's tools: "map 2a4fbf7080 is 21 changed files behind; 131 of 394 units need recording". The command is in `docs/TESTING.md` and below | — | `test_map.py update --dry-run` (run in a scratch worktree of main) |
| Check: the 17-merge replay as a regression check of the plans | `replay.py` with evidence (`replay.json`, the recorded map, the nine recordings, the build records, the Mac durations). `--check` recomputes every saved plan in a worktree of the saved commit: **"replayed 3 columns x 17 merges: every plan as saved"**. With one saved unit dropped, the check fails ("1 plans differ") | `74a04c3ba` | `python3 docs/test-architecture/select/replay.py --check` |
| Check (seeded): an `evidence/` file in a mapped unit selects only its readers; an identical rebuild selects no runner; a changed binary selects all its runners | As tests | — | the three tests named in rows 4 and 6 |
| Check: 10 contemporaneous selected-vs-R2 runs | Not in this build. It needs 10 real merges after this lands, each with its R2. That is the chain's and the merge train's record, not a builder run | — | deferred: EXTERNAL (merge train, after merge) |

`docs/TESTING.md` documents each rule. Under D4 the replay is batch evidence checked by `--check`; there is no permanent test of this batch's numbers. The permanent tests above are hermetic: synthetic maps, private caches and private build records under `tmp_path`.

## Measured effect

### Selection on the 17 merges of Oct 11-14 (`evidence/replay.json`)

Each cell is units / share of recorded seconds, weighted by the complete map: the recorded seconds of the selected units over those of all 394 units. "Fresh" means `evidence/map-recorded.json.gz`, main's own map at `91858c03`, taken as recorded at each merge's parent (`--assume-fresh`), as the plan's own estimate did. "Main" is `tools/select_tests.py` at `dae12d5ff`; "branch" is this branch at `c7b44a495`. Both ran through their CLI in private caches.

| Merge | Item | Main, maps as they were | Main, fresh map | This branch, maps as they are | Branch, fresh map | + nine units recorded | + binary cutoff |
|---|---|---:|---:|---:|---:|---:|---:|
| `cd546c0d9` | arch-AR-7 | 394 / 100.0% (full) | 24 / 10.9% | 394 / 100.0% (full) | 24 / 10.9% | 24 / 10.9% | 24 / 10.9% |
| `8cec935af` | lf-16d | 394 / 100.0% (full) | 394 / 100.0% (full) | 394 / 100.0% (full) | 328 / 98.6% | 328 / 98.6% | 328 / 98.6% |
| `f1b719c7a` | lf-13b | 394 / 100.0% (full) | 394 / 100.0% (full) | 394 / 100.0% (full) | 394 / 100.0% | 394 / 100.0% | 394 / 100.0% |
| `c9b8cba63` | devtime-1 | 394 / 100.0% (full) | 20 / 29.5% | 394 / 100.0% (full) | 18 / 8.3% | 18 / 8.3% | 18 / 8.3% |
| `615e89d7f` | ts-B5 | 394 / 100.0% (full) | 61 / 35.2% | 394 / 100.0% (full) | 59 / 14.0% | 59 / 14.0% | 59 / 14.0% |
| `49de179e7` | ts-B1 | 394 / 100.0% (full) | 394 / 100.0% | 394 / 100.0% (full) | 394 / 100.0% | 394 / 100.0% | 394 / 100.0% |
| `11676c2c0` | arch-20261010-1 | 394 / 100.0% (full) | 394 / 100.0% (full) | 339 / 99.6% | 329 / 99.5% | 329 / 99.5% | 116 / 40.8% |
| `da0c04bd9` | arch-20261010-2 | 394 / 100.0% (full) | 65 / 36.1% | 148 / 42.5% | 63 / 14.8% | 63 / 14.8% | 63 / 14.8% |
| `09a807d7e` | arch-AR-9 | 394 / 100.0% (full) | 394 / 100.0% (full) | 394 / 100.0% (full) | 394 / 100.0% (full) | 394 / 100.0% (full) | 394 / 100.0% (full) |
| `406736a47` | eff-20261011-1 | 394 / 100.0% (full) | 27 / 39.2% | 166 / 45.4% | 25 / 18.0% | 25 / 18.0% | 25 / 18.0% |
| `d006b1f48` | rd-5 | 394 / 100.0% (full) | 125 / 73.1% | 303 / 89.8% | 125 / 73.1% | 125 / 73.1% | 125 / 73.1% |
| `2d964d5dc` | fix-main-relay | 394 / 100.0% (full) | 13 / 8.0% | 108 / 33.4% | 13 / 8.0% | 13 / 8.0% | 13 / 8.0% |
| `f98183bf5` | arch-AR-3 | 394 / 100.0% (full) | 394 / 100.0% (full) | 394 / 100.0% | 101 / 48.6% | 99 / 27.3% | 99 / 27.3% |
| `dccd9cf5a` | runner-portability | 394 / 100.0% (full) | 300 / 95.0% | 314 / 95.8% | 300 / 95.0% | 300 / 95.0% | 300 / 95.0% |
| `4667e8de6` | lf-14d | 394 / 100.0% (full) | 394 / 100.0% (full) | 394 / 100.0% | 394 / 100.0% | 394 / 100.0% | 394 / 100.0% |
| `8594f1d05` | repo-map-untracked | 394 / 100.0% (full) | 12 / 7.9% | 101 / 33.2% | 12 / 7.9% | 12 / 7.9% | 12 / 7.9% |
| `9f40783b8` | english-run-root | 394 / 100.0% (full) | 316 / 98.6% | 375 / 99.8% | 316 / 98.6% | 316 / 98.6% | 63 / 32.5% |
| **average** | | **394.0 / 100.0%** | **218.9 / 66.7%** | **317.6 / 84.7%** | **193.5 / 58.5%** | **193.4 / 57.3%** | **165.9 / 50.0%** |

- **Average selection: 100% before, 50.0% after** (recorded seconds), across the plan's 17 merges.
  - Measured in Mac test seconds instead (run A's per-file durations, `evidence/mac-durations.json`): 100% before, 49.3% after.
  - The plan estimated "92% → 55-67%". Its 92% counted three partly mapped plans that are full under today's cache; today every plan is full on main, because the v6 maps are skipped.
- **Where it comes from:**
  - map freshness alone gives 100 → 66.7% (main's own selector with a fresh map);
  - this batch's precision fixes give → 58.5%: `.gitattributes`, the manifest's shared fields, the product-literal narrowing (evidence files), and the v6 converter;
  - recording the nine units gives → 57.3% (`f98183bf5`: 48.6 → 27.3%);
  - the binary cutoff gives → 50.0% (`11676c2c0`: 99.5 → 40.8%; `9f40783b8`: 98.6 → 32.5%).
- **Full plans: 17 before, 6 with a fresh map on main, 1 after.** The remaining one is `09a807d7e`, which really changed `tests/conftest.py` (it added an autouse fixture). It stays a trigger.
- **What still selects nearly everything is real:**
  - `49de179e7` and `dccd9cf5a` (wide Python changes; `LeanService` itself);
  - `8cec935af`, `f1b719c7a` and `4667e8de6`, whose rebuilt `ve_service` really differs. That is the answer-level cutoff's domain (rank 8, tarch-cutoff).
- **"Maps as they are"** is the cache as it is today (non-reproducible, measured once). On this branch the v6 converter lets the older maps count again: 100 → 84.7%.
- **Selection time per plan:** 2.64 s on main (fresh), 2.12 s on this branch (with the cutoff), mean of 17.

### Binary cutoff: the batch's first measurement

The plan left one thing open: whether the one-shot executables were identical across Lean merges. I built each distinct `lean/` tree of the window once, oldest first, in one scratch worktree on the VM. Each build was `lake build`, then every `lean_exe`, 290-2,706 s each; one clang frontend crash on `VE.English.Run:c.o` (exit 135, known) passed on retry. Then I hashed every executable (`evidence/lean-builds/`).

| Merge | Executables built the same | Rebuilt differently |
|---|---|---|
| `8cec935af` lf-16d | `ve_conformance`, `ve_english_run` | 7, including `ve_service` and `ve_metered` |
| `f1b719c7a` lf-13b | `ve_english_run` | 8 |
| `11676c2c0` arch-20261010-1 | **all 9** | none |
| `4667e8de6` lf-14d | 6, including `ve_metered` | `ve_service`, `ve_response_decode`, `ve_speech_acts_route` |
| `9f40783b8` english-run-root | 8, including `ve_service` and `ve_metered` | `ve_english_run` |

- `ve_service` was byte-identical in 2 of 5 Lean merges, as the plan found from its replay.
- The one-shot `ve_metered` was identical in 3 of 5. It is started by 76 units, which is why the module rule undid most of the plan's gain.

### The nine unrecorded units (`evidence/nine-units.json.gz`)

These are the nine units unrecorded in map `f98183bf`. I recorded them on the loaded VM (load 70-104 on 32 cores, 5 parallel files) with this branch's recorder and the 4 h timeout. **Seven are now recorded:**

| Unit | Before | Now |
|---|---|---|
| `test_assist` | timeout at 3,600 s | exit 0, 4,795 s |
| `test_assist_invariants` | timeout | exit 0, 5,262 s |
| `test_english_evidence` | timeout | exit 0, 3,771 s |
| `test_readings_rd6b_differential` | timeout | exit 0, 3,061 s |
| `test_wire_gate_corpus` | timeout | exit 0, 2,580 s |
| `test_hang_guards` | opaque | exit 0, recorded (the killed child no longer counts) |
| `test_readings_defaults_rd8_report` | failed (known red, fixed on main by tarch-b8) | exit 0 |
| `test_run_order` | opaque | exit 0, **still opaque** |
| `test_select_tests` | opaque | exit 0, **still opaque** |

The last two stay opaque, and that is the sound answer. Their remaining unrecorded children are recordings rooted in a temporary fake repository (`VE_TESTMAP_ROOT` is a tmp dir). That recorder drops everything outside its root, so the code those children run from this repository (`tools.maxfail_pytest`, for one) is genuinely unseen. A few others are children killed mid-start inside a nested run. Recording them would need a multi-root recorder (follow-up F3).

Five of the nine ran past the old 3,600 s limit. Recorded maps on main time out on `test_assist` and `test_assist_invariants` at every update today (`91858c03`, `a650eeb6`).

### On the Mac (ve-mac-1, `mac-pytest.sh`, 6 workers)

| Run | Tests | pytest wall |
|---|---|---:|
| Before: the full default collection (what every one of the 17 merges ran with main's maps as they were) | 15,684 passed, 0 failed | **1,063.96 s** |
| After, `f98183bf5` (arch-AR-3, `.gitattributes`): 98 files | 3,547 passed | **530.62 s** |
| After, `da0c04bd9` (arch-20261010-2): 62 files | 3,004 passed | **166.51 s** |
| After, `9f40783b8` (english-run-root, binary cutoff): 62 files | 3,051 passed, 2 failed (pre-existing, below) | **510.36 s** |
| This branch's own selected run (`--select --base … --run`) at the synced HEAD | 37/401 units | 887 s end to end, including the clone and setup |

These are single runs on a shared runner, at Mac load 17-21. The walls exclude slot waits.

- The selected runs are bounded below by their heavy files: `test_wire_gate_corpus` (527 s of run A) is in all three, and `test_readings_rd6b_differential` (481 s) is in the first.
- This is the heavy tail rank 7 addresses. Selection takes the run from about 18 min to 3-9 min here.
- An earlier attempt of the `f98183bf5` run fell back to the VM (no Mac slot within 600 s) and was stopped. The rerun used `MAC_PYTEST_NOFALLBACK=1` and ran on the Mac.

## Commands for the orchestrator (not edited here)

- **verify.sh:11**, in place of the `find -mmin -1440` line:

  ```
  base=$(git merge-base HEAD $(git -C ~/code/ve-integration rev-parse HEAD)); fresh=$(uv run --frozen python tools/test_map.py fresh --base $base 2>/dev/null)
  ```

  An older branch without `fresh` prints nothing, so it gets the full suite (fail-safe).
- **fixloop.sh:15:**

  ```
  fresh=$(cd $wt && uv run --frozen python tools/test_map.py fresh --base $(git -C $wt merge-base HEAD main) 2>/dev/null)
  ```

- **merge-train.sh, after each publication**, in a clean checkout of the published commit:

  ```
  uv run --frozen python tools/test_map.py update --jobs 8
  ```

  This is what `testmap-refresh.sh` does; it also records that commit's Lean build digests.
- **Any runner job that builds main** (the Mac nightly, Mac integration builds), after its `lake build`:

  ```
  uv run --frozen python tools/test_map.py build-record
  ```

  The binary cutoff needs a base record on the same machine. Records live in `~/.cache/ve-lean-builds` (`$VE_LEAN_BUILDS`), outside the per-worktree map copy that `mac-pytest.sh` syncs. Without a base record the cutoff simply does not apply (full module rule).

## Seeded bugs

`mutants.json` lists 22 faults in Python, the only language whose product code changed (`tools/`; no Lean or Rust). Each was planted by exact text replacement in a changed file, in a scratch worktree of the HEAD. Each made its named test fail, and the file was restored (`git status` clean).

| Bug | File | Fault | Test that failed |
|---|---|---|---|
| S1 | `tools/test_map.py` | tree maps count in the window | `test_tree_maps_do_not_crowd_commit_maps_out_of_the_window` |
| S2 | `tools/test_map.py` | `VERSION = 8` with no `FORMAT_CHANGES` entry | `test_each_map_format_version_ships_with_a_converter_or_a_recorded_map` |
| S3 | `tools/test_map.py` | the 6-to-7 converter invents modes | `test_a_version_6_map_converts_and_keeps_every_service_user` |
| S4 | `tools/test_map.py` | every silent child counts as having run nothing | `test_a_child_that_records_here_and_left_no_file_ran_nothing` |
| S5 | `tools/test_map.py` | no handover from a nested recording | `test_a_recording_inside_a_recorded_test_hands_over_its_records` |
| S6 | `tools/test_map.py` | units record shortest first | `test_recording_starts_the_longest_units_first` |
| S7 | `tools/test_map.py` | `fresh` ignores the map's age | `test_freshness_is_the_map_selection_would_use` |
| S8 | `tools/test_map.py` | another platform's build record is used | `test_a_build_record_needs_a_current_build_of_one_tree` |
| S9 | `tools/test_map.py` | a build hashed while its tree changed is recorded | `test_a_build_record_needs_a_current_build_of_one_tree` |
| S10 | `tools/test_map_recorder.py` | "records here" without the hook | `test_a_child_records_here_only_if_the_hook_started_this_process` |
| S11 | `tools/source_graph.py` | product words name every directory again | `test_a_product_word_names_only_product_directories` |
| S12 | `tools/select_tests.py` | `.gitattributes` changes everything again | `test_a_merge_driver_edit_of_gitattributes_selects_its_readers_and_git_users` |
| S13 | `tools/select_tests.py` | macro uses are not checkout attributes | `test_only_checkout_attribute_edits_of_gitattributes_change_everything` |
| S14 | `tools/select_tests.py` | git users are not `.gitattributes` readers | `test_a_merge_driver_edit_of_gitattributes_selects_its_readers_and_git_users` |
| S15 | `tools/select_tests.py` | shared fields select no whole-manifest reader | `test_a_shared_manifest_field_selects_its_whole_manifest_readers` |
| S16 | `tools/select_tests.py` | the manifest `version` is an ordinary field | `test_a_shared_manifest_field_selects_its_whole_manifest_readers` |
| S17 | `tools/select_tests.py` | an authority edit selects only entry readers | `test_an_authority_change_selects_the_registrations_of_its_entries` |
| S18 | `tools/select_tests.py` | a changed binary counts as the same | `test_a_changed_binary_selects_all_its_runners` |
| S19 | `tools/select_tests.py` | a missing build record counts as identical | `test_without_both_build_records_every_runner_is_selected` |
| S20 | `tools/select_tests.py` | `--run` never builds the head for the cutoff | `test_a_run_builds_the_head_for_the_cutoff_when_the_base_build_is_recorded` |
| S21 | `tools/select_tests.py` | drift reads missing `.gitattributes` texts as unchanged | `test_a_merge_driver_edit_of_gitattributes_selects_its_readers_and_git_users` |
| S22 | `tools/select_tests.py` | equal `lean/` trees count as an identical build | `test_no_cutoff_when_the_trees_cannot_show_the_change` |

Fourteen of these behaviours also have a permanent in-process mutant in `test_selector_mutants_fail_the_checks` (`SAFETY_CASES`, 32 cases, all caught).

## Found while building

- **Cutoff on equal trees** (fixed, `86e0b3336`). The first cutoff compared one tree's record with itself whenever a Lean change was not in the trees: a `--paths` name without an edit, or the existing test's synthetic change. That dropped every runner. Recording `test_select_tests` under the real hook exposed it: `test_native_changes_schedule_builds_and_their_runners` failed because my real build record was in the shared cache. The cutoff now needs distinct trees and known contents, and tests use private build records.
- **History in a test** (fixed, `2882db850`). `test_freshness_is_the_map_selection_would_use` assumed `HEAD~1` is one commit behind. After the sync it was 125 behind, and the Mac selected run caught it.
- **ve-integration's Lean build was out of date** for its own HEAD: Lake `--no-build` gave exit 3 for `ve_service`. The rebuild took 26 min. Anything that copies it as current (`testmap-refresh.sh` seeds from it) rebuilds; `drop_stale` does not catch this, because the trace's input hash differs. Noted only.

## Pre-existing, not touched

- **main-known-red.txt.** In the Mac run of `9f40783b8`'s selection, `test_lean_service.py::test_the_sub_tick_deadline_tests_hold_on_a_fast_machine_and_need_the_response_check[checked]` and `[response unchecked]` failed with `module 'question_fixtures' has no attribute 'FIXTURES'`. They passed in the full Mac run.
  - The cause is module-name shadowing: `tests/question_fixtures.py` and `tools/question_fixtures.py` share a name. Test files that put `tools/` first on `sys.path` shadow one for the other, depending on which files share an xdist worker.
  - `tests/test_select_tests.py` has done that since before this branch.
  - These tests belong to their own item (follow-up F1).
- **Leaked children** (follow-up F2). `test_hang_guards.py::test_a_wire_check_that_outlasts_its_wait_blocks_the_commit` raises `TimeoutExpired` without killing its never-answering child (`tools/wire_contract.py --check`).
  - The child outlives the run and holds the checkout's native-build lock.
  - A later pytest session in that checkout that wants to build then waits on it. I saw this twice and killed my own leaked children.

## Not run here

- The full release gate: the chain runs it on the committed final HEAD.
- The 10 contemporaneous selected-vs-R2 runs: EXTERNAL, merge train after merge.
- Answer-level cutoff: rank 8, tarch-cutoff.
- A Mac-side cutoff measurement: no Mac base build records exist until a runner job runs `build-record`.

## Follow-ups

- **F1**: rename `tools/question_fixtures.py` or `tests/question_fixtures.py`, so test files that put `tools/` first on `sys.path` cannot shadow one with the other.
- **F2**: `test_hang_guards`' expired-wait test must kill its child.
- **F3**: a recorder that also records a fake-root child's reads under the real root, so `test_run_order` and `test_select_tests` can be recorded.
- **F4**: the orchestrator lines above.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: N.A. No relay, route or Lean answer is read by changed code.
2. Deliverables: PASS. Every plan line has a row in the Delivery table with its commit and test. The 10 R2 runs are deferred as EXTERNAL. Rule scan of the diff: no new Python copy of a Lean decision, no permanent report test (the replay is evidence with `--check`, D4), no authority switch.
3. Tests and gates can fail: PASS. `mutants.json` (S1-S22); `test_selector_mutants_fail_the_checks` (32 cases); the replay `--check` fails on tampered evidence ("1 plans differ").
4. Python, Lean and Rust agree: N.A. No checker behaviour changed. The full default collection passed on the Mac (15,684 passed).
5. R8 binding: N.A. No relayed answer.
6. Gate evidence matches the final HEAD: PASS for the build part. Synced with main (`c99a3156b`); the gate is the chain's, on the final HEAD; `tools/gate_collection.py --check --prebuilt` exit 0 (54 added, 0 removed, 0 refused, 0 stale, 0 malformed).
7. No unsigned item: PASS. DELTA.md has 8 rows, each directed by the batch prompt; "Zero rows wait for a signature".
8. Every user-visible change in DELTA: PASS. DELTA.md rows 1-8 cover each selector and map behaviour change; no VE output changed.
9. Test selection still finds the tests: PASS. `select_tests.py --paths` on each changed tool selects 53 units including `tests/test_select_tests.py`, where each seeded bug fails. The selected run on the Mac recorded 37/401 units.
10. Lean statements: N.A. No Lean changed.
11. Budgets, limits and deadlines fail closed: PASS. The recorder timeout is a hang guard (4 h), not a test; no test asserts a duration or sleeps (`tests/test_hang_guards.py` passes; it lints this). A missing record, equal trees or unknown contents disable the cutoff (`test_without_both_build_records_every_runner_is_selected`, `test_no_cutoff_when_the_trees_cannot_show_the_change`).
12. No CPU or memory regression: PASS. Selection time per plan is 2.64 s on main and 2.12 s on this branch (`replay.json` `plan_seconds`, mean of 17). The cutoff adds one working-tree id computation, and only for a Lean change in working-tree mode.
13. Test-removed trailers: PASS. No test removed or renamed; `gate_collection.py --check --prebuilt` reports 0 removed and 0 malformed.
