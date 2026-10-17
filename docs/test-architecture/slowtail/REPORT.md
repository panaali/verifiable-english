# tarch-slowtail: the suite's slow tail (speed program round 2, action #15; PIPELINE-LIMITS L41, L63)

Branch `infra/tarch-slowtail`, measured against main 85b20fcb, synced with main 3c664615. Python tooling only: no Lean,
`ve/` or Rust change, no trust growth. User-visible deltas: [DELTA.md](DELTA.md).

## Result

The same whole suite on the Mac test runner ve-mac-1 (18 cores, aarch64), at 9 xdist workers, before (main 85b20fcb)
and after (this branch, d159baf4), run by `mac-pytest.sh -- -v -p no:cacheprovider -o addopts=-ra -m "not live" -n 9
--durations=0 --durations-min=0 tests`, each line stamped as it arrived (`tools/bench/suite_tail.py stamp`):

| | before (main 85b20fcb) | after (branch d159baf4) |
|---|---:|---:|
| tests | 16,917 passed, 9 skipped, 83 xfailed | 16,951 passed, 9 skipped, 83 xfailed |
| suite wall (pytest's own) | 2,498 s | 2,156 s (−342 s, −13.7%) |
| suite wall (first line to last report) | 2,526 s | 2,188 s |
| **tail**: fewer than 4 of 9 workers busy, to the end (summed) | **517 s** | **2.8 s** |
| tail, from the time each worker's last line arrived | 506 s | 11 s |
| one worker alone at the end (summed) | 278 s | 1.9 s |
| last worker's finish against the even share (summed) | 2,473 s against 2,039 s | 2,123 s against 2,118 s |
| runner load (1, 5, 15 min, at the end) | 30.4, 22.0, 16.7 | 18.5, 23.3, 32.3 |

"Summed": each worker's finish is the sum of the `--durations` seconds of the tests it ran, as a worker runs its
tests back to back. The arrival times are coarse, because the output arrives in blocks over ssh; the two readings
agree within about 10 s. Both runs shared the runner with other jobs (the runner's 2 gate slots), so the walls carry
that noise. The tail does not depend on it: before, the last worker ran alone for 278 s; after, all 9 finish within
12 s of one another. Numbers: [evidence/before-main-85b20fcb.tail.json](evidence/before-main-85b20fcb.tail.json),
[evidence/after-branch-d159baf4.tail.json](evidence/after-branch-d159baf4.tail.json). They are regenerated from the
saved logs by `uv run --frozen python tools/bench/suite_tail.py tail evidence/<run>.log.gz`, after `gunzip`.

**Cause, confirmed.** The before-run's lone worker (gw4) ended with
`test_b16e_rights_document.py::test_rights_mutants_get_the_prior_outcome_wherever_lean_decides[0-False]` (208 s),
`[2-False]` (205 s) and `[16-True]` (92 s). None of them is in the committed durations file of Oct 13/16, so each was
estimated at 0.107 s and all three went out inside one run of consecutive "cheap" tests.

**What does it.** The measured before-run is replayed through each scheduler, with the real per-test seconds and
9 simulated workers ([replay.py](replay.py), output [evidence/replay.txt](evidence/replay.txt)). The simulation
reproduces main's measured run: an end of 2,468 s against 2,473 s, and a tail of 495 s against 517 s.

| scheduler, estimates | end | tail (fewer than 4 busy) | one worker alone |
|---|---:|---:|---:|
| xdist's `load` | 2,336 s | 173 s | 80 s |
| main's LongestFirst, main's stale file | 2,468 s | 495 s | 279 s |
| this branch, stale file | 2,480 s | 516 s | 291 s |
| this branch, stale file, b16e/b16f named unmeasured | 2,189 s | 163 s | 74 s |
| this branch, refreshed file | 2,040 s | 2 s | 1 s |

Fresh durations remove the tail. Next best is the unmeasured-first rule: with only the stale file, it cuts the tail by
two thirds once the source names what it measured, as the gate's overlay does. The count cap does nothing for this run
(+12 s, within the simulation's noise). It is for the case below.

**When the gate has fresh durations.** The refreshed committed file covers the suite now. The overlay of the merge
base's recorded durations takes over once main's tip carries a gate record with `durations`. The merge train's
candidate gate of this branch writes the first such record, on its candidate. Until a base has that record, every
gate orders by the committed file, as before.

## What changed (task items 1–4)

1. **Per-test seconds in the gate record (L41).** `tools/gate_pytest.py`'s controller adds each test's setup + call +
   teardown seconds from the reports xdist forwards (`seconds` in its events; `merge_pytest_events` passes them on).
   `tools/gate.py` `record_durations` keeps them as `result["durations"]` (`test_schedule.record_field`: the format
   name, `recorded_seconds` 1.0, `tests` timed, `unrecorded_seconds` the mean of the others, and `seconds_zlib`, the
   tests of at least 1 s rounded to 0.1 s, as compressed JSON). It also prints the 20 slowest in gate.log. On main's
   measured run the field is 32 KB, against a 505 KB note for main bc1936dd (+6%). Readers checked:
   `gate_collection.read_record`, `read_gate_result` and `base_durations` (tests/test_gate_durations.py);
   `batch_evidence` note-versus-evidence (tests/test_batch_evidence.py); manage-agents `gaterec.py final` and `sigs`,
   and `mac-gate-post.py`, run on records with the new fields ([evidence/readers.txt](evidence/readers.txt));
   `review-ready.py` and `main-red-check.py` read only `status`, `commit_sha`, `mode`, `stages`, `dirty` and
   `failures` (by inspection), which are unchanged. No manage-agents script was edited.
2. **Fresh durations for the scheduler.** After `base_collection`, `gate.suite_durations` writes
   `<scratch>/test-durations.json` and names it in `VE_GATE_PYTEST_DURATIONS`, an allowed variable of the pytest stage
   (`STAGE_ENVIRONMENT`, `test_schedule.SOURCE_VARIABLE`). The file is the committed file overlaid with the durations
   in the merge base's gate record (`base_durations`: the base's record, or its same-tree parent's, read through
   `gate_collection.recorded` and `read_gate_result`). Each test that gate measured (its collection) takes its time
   there: recorded, or the mean of the short ones. Every other test keeps the committed time. The file then names
   the measured tests, but only when that gate timed every test it selected. `test_schedule.source()` reads the named
   file when the variable is set, else the committed one. A missing, base-only, malformed or unreadable record, or a
   missing or malformed file, falls back as `read_estimates` does. `result["durations_source"]` records which source
   was used. The `VE_GATE_PYTEST_` prefix means `nested_pytest.environment` drops the variable from nested runs, as it
   drops the gate's other suite settings. So no nested run, and no run-cache key (`tools/run_cache.py` keys on a run's
   `VE_` settings; the wire-corpus recording stored there is ~1,180 test-seconds), changes with a gate's scratch path.
3. **Robust to unrecorded tests** (`tools/test_schedule.py`):
   - **Unmeasured first.** When the source names what it measured, the tests it did not measure (new since) are handed
     out right after the head batches, in collection order. Each run holds at most 1/(2 × workers) of those left, so a
     few that take minutes neither go together nor wait among the last (`unmeasured_first`).
   - **Count cap.** A bulk run is capped by count as well as by estimated seconds (`bulk_count`'s `most`: `load`'s
     len(pending)/(2 × workers), less what the worker holds; whichever cap is smaller), and ends with single tests. An
     estimated-cheap module followed by estimated-dear tests is then split. Without the cap, the seconds left would
     send it whole.
   - The collection order is unchanged: every worker still collects the selection, and `merge_pytest_events` checks it.
4. **Tests** (all new ones pass; no timing assertions, only simulated clocks and hand-out records):
   - Collected and run sets equal with the committed file, the overlay, a missing file and a malformed file, each test
     once, in a real xdist run under the gate's event plugin:
     tests/test_test_schedule.py::test_the_durations_source_never_changes_which_tests_run.
   - An unrecorded expensive module at the end of the collection is not one worker's run:
     ::test_an_unrecorded_expensive_module_at_the_end_is_not_one_workers_run[last], [before dear tests].
   - Unmeasured first: ::test_unmeasured_tests_start_right_after_the_long_ones_in_shares_by_count.
   - The hook reads the named file, else the committed one, and falls back on a bad one:
     ::test_the_suite_conftest_installs_the_scheduler, ::test_a_measured_list_that_is_not_a_list_of_ids_is_ignored.
   - Nested runs and the run cache never see the gate's file:
     ::test_a_nested_run_and_the_run_cache_never_see_the_gates_durations_file.
   - `bulk_count`'s `most`: ::test_bulk_count_takes_at_least_the_least_then_up_to_the_target.
   - The record field, its readers and the gate's wiring, in tests/test_gate_durations.py: round trip and size, 17
     retyped or malformed fields ignored, the overlay's semantics, `base_durations` against real git notes (no record,
     a record before durations, complete, incomplete, malformed, base-only, unknown commit), and `gate.main` naming the
     overlay to its suite, recording the suite's seconds in the record and the note, and logging the slowest.
   - `batch_evidence` with a durations note:
     tests/test_batch_evidence.py::test_batch_evidence_takes_a_gate_note_with_durations.
   - The measurement tooling: tests/test_suite_tail.py (`tail`, `--log`, `stamp`).

## What is not changed (R2, R3, "nothing weakens what is checked")

The durations decide which worker runs a test and when, never whether it runs or passes. The merge train's live full
gate (R2) and the nightly `--no-quarantine` (R3) still run the whole collection. Their selection does not depend on
the durations, the base's record or any cache: `test_the_durations_source_never_changes_which_tests_run` checks the
selection is identical under every source, and `merge_pytest_events` still refuses a worker that collected anything
else. Every check that ran before still runs. No test, check or limit was removed. No test asserts a duration. No
manage-agents script, `tools/select_tests.py`, the collection check or the quarantine was touched.

## Seeded bugs (Python: the only changed language)

[mutants.py](mutants.py) plants each one, runs the tests named, and restores the file. Results:
[seeded-mutants.json](seeded-mutants.json). All 19 were caught. M14–M19 answer review F1 (a computed value never
checked by value): each is a value the event plugin or the scheduler computes, now asserted exactly.

| # | file | seeded bug | failing test |
|---|---|---|---|
| M1 | tools/test_schedule.py | the scheduler drops an unmeasured test | test_the_durations_source_never_changes_which_tests_run, test_unmeasured_tests_start_right_after_the_long_ones_in_shares_by_count |
| M2 | tools/test_schedule.py | the scheduler hands one test out twice | the same two |
| M3 | tools/test_schedule.py | the overlay changes the selection (unmeasured tests left out) | test_the_durations_source_never_changes_which_tests_run |
| M4 | tools/test_schedule.py | the count cap is ignored | test_an_unrecorded_expensive_module_at_the_end_is_not_one_workers_run[before dear tests] |
| M5 | tools/test_schedule.py | unmeasured tests are not moved first | test_unmeasured_tests_start_right_after_the_long_ones_in_shares_by_count |
| M6 | tools/test_schedule.py | the scheduler ignores the file the gate names | test_the_suite_conftest_installs_the_scheduler |
| M7 | tools/gate.py | a record without durations | test_the_gate_names_the_overlay_to_its_suite_and_records_the_suites_seconds, test_the_log_names_the_twenty_slowest_and_ignores_what_is_not_seconds |
| M8 | tools/gate.py | the suite gets the committed durations only, never the base's | test_the_gate_names_the_overlay_to_its_suite_and_records_the_suites_seconds |
| M9 | tools/gate_pytest.py | the event plugin times no test | test_the_durations_source_never_changes_which_tests_run |
| M10 | tools/test_schedule.py | the record field drops the short tests' mean | test_the_record_field_keeps_the_recorded_tests_and_the_mean_of_the_others |
| M11 | tools/gate.py | an incompletely timed base still names its measured tests | test_the_base_durations_come_from_the_base_gate_record |
| M12 | tools/bench/suite_tail.py | the tail starts at the last worker's finish | test_tail_reads_when_each_worker_finished_its_last_test |
| M13 | tools/test_schedule.py | the gate's file is named in a variable nested runs inherit | test_a_nested_run_and_the_run_cache_never_see_the_gates_durations_file |
| M14 | tools/gate_pytest.py | a test's seconds are its last phase's, not the sum of its three | test_the_event_plugin_times_each_test_as_its_setup_call_and_teardown_seconds |
| M15 | tools/test_schedule.py | half of the unmeasured tests go out in one hand-out | test_unmeasured_tests_go_out_a_share_of_those_left_at_a_time |
| M16 | tools/test_schedule.py | the count cap ignores what the worker holds | test_the_count_cap_counts_what_the_worker_already_holds |
| M17 | tools/test_schedule.py | a worker holding nothing may get a single test | test_the_count_cap_counts_what_the_worker_already_holds |
| M18 | tools/test_schedule.py | the seconds left are not recounted when a crashed worker's tests come back | test_a_crashed_worker_s_tests_run_elsewhere |
| M19 | tools/test_schedule.py | an unrecorded test is estimated at the default, not the source's mean | test_an_unrecorded_test_is_estimated_at_the_sources_mean |

## Runs

- Whole suite on the Mac at 9 workers, this branch d159baf4: 0 failed (the "after" run above). Main 85b20fcb: 0 failed.
- The selected tests (`mac-pytest.sh --select`, 33 units): 0 failed at 8215a8a7. The later sync with main 3c664615 brought only fu-ar2-decoders (trust tools and docs), which this branch does not touch.
- Review F1 fix: the selected tests (33 units) 0 failed at 9bd63836 on the Mac; `lake build` and `lean/audit.py`
  pass (no Lean change); the 19 seeded bugs all caught (seeded-mutants.json).
- Pre-existing failures on main (main-known-red.txt): none of them is in this branch's tests. The three listed
  (test_lean_service sub-tick deadline ×2, test_readings_defaults_rd8_report) passed in both Mac runs and were not
  touched.
- Not run here: the full gate (tools/gate.py), which the chain runs on the final HEAD.
