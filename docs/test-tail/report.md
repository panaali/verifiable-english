# Test tail: the slowest tests start first (infra item test-tail, DRI 2026-10-13, PIPELINE-LIMITS.md L18)

Branch `infra/test-tail`, from main 406736a4. The full suite's xdist run no longer ends with one or two
workers running alone: on the same 8-worker command, the last worker now finishes within seconds of the
first. No test was dropped, skipped, marked or weakened; one test was split into its 14 cases (every input
it checked is still checked), one runs its two independent halves at once.

## Result

Every run below is the gate's own pytest command (`tools.gate.pytest_args`: `-m "not live"`, the gate's
event plugin, prebuilt checkers) at `-n 8` on the shared 32-CPU VM, measured by `tools/bench/suite_tail.py
run` (wall time, each test's start and end on its worker, the machine's CPU every second). Other sessions
loaded the VM throughout; the load average is given per run. The saved measurements are
`docs/test-tail/suite-*.json`.

| run | commit | scheduler | load (1 min) min-mean-max | wall s | test s (sum) | ideal s (sum / 8) | wall / ideal | workers' end s (first, last) | last worker alone s |
|---|---|---|---|---|---|---|---|---|---|
| before | 406736a4 (main) | xdist `load` | 46 - 78 - 115 | **6,691** | 39,064 | 4,883 | 1.37 | 4,374, 6,678 | 2,024 |
| after, step 1 | 09d4e4f0 | longest first, durations of main's run | 35 - 64 - 101 | 4,555 | 31,778 | 3,972 | 1.15 | 3,917, 4,540 | 622 |
| after, step 2 | b5916ee9 | + each test's longest time across runs | 31 - 53 - 70 | 4,210 | 30,832 | 3,854 | 1.09 | 3,836, 4,202 | 365 |
| **after** | 65347b37 | + a file with a long test goes out whole | 23 - 61 - 94 | **4,246** | 33,603 | 4,200 | **1.011** | 4,223, 4,227 | **3** |

"Last worker alone" is the last worker's end less the median worker's end. Wall time fell 37% (6,691 s to
4,246 s), but the load was lower after (mean 61 against 78), so the load-independent figure is wall / ideal:
the run took 37% longer than its tests' even share of 8 workers before, and 1.1% longer after (the 1.1% is
collection, worker start-up and the last test's end). At the before run's own 39,064 test-seconds, 1.011 of
its ideal is 4,937 s, 26% less than 6,691 s.

**Worker occupancy per minute** (the share of the 8 workers' seconds spent inside a test; the machine's own
CPU was 98-100% busy in every minute of every run, from the other sessions, so it says nothing about the
tail; both series are in the JSON as `worker_occupancy_percent_per_minute` and
`machine_busy_percent_per_minute`, sampled each second from /proc/stat):

- before: 26% in minute 1 (collection), 99.5-100% in minutes 2-72, then 99, 88, 66, 59, 50, 45, 37, then 25%
  for 14 minutes (two workers) and 12.5% for 17 minutes (one worker): 39 of 112 minutes were the tail.
- after: 80% in minute 1, 98.5-100% in minutes 2-70, and the last, partial minute 52%.

The before run's tail: gw0 was given, as one of `load`'s chunks, `test_assist_invariants.py`'s 13 cases of
~130 s each after its own 1,430 s `test_assist` property test (which started at 2,714 s); gw1 got
`test_wire_gate_corpus`'s 1,257 s test at 4,346 s.

**Simulation** (`docs/test-tail/simulate.py`, saved in `evidence/simulation.json`): the before run's
measured tests replayed through xdist's real `LoadScheduling` and through `LongestFirst`, on simulated
workers that run what they are sent (no shared fixtures, exact estimates). It reproduces the before run
(6,629 s simulated, 6,691 s measured) and isolates the order's effect from the load:

| workers | ideal s | `load` s | longest first s |
|---|---|---|---|
| 8 | 4,883 | 6,629 | 4,885 |
| 16 | 2,442 | 5,731 | 2,445 |

At 16 workers (the M5's count), `load` leaves 57% of the run as tail on these durations.

Not run: the M5 Pro runner of the task's measurement (this worker has only the VM); a `vmstat 1` capture
(the /proc/stat sampler records the same busy share per second).

## What changed

1. **The order (task step 1).** `tools/test_schedule.py` defines `LongestFirst`, an xdist scheduler that
   `tests/conftest.py` installs for every `--dist load` run (the default under `-n`: the gate's suite, plain
   `pytest -n`, and the nested `-n` runs such as the wire corpus's recording). It is `load` with two changes,
   both driven by the committed `tools/test-durations.json` (measured data: each test of at least 1 s, its
   longest time across the profiled runs, and the mean of the rest):
   - the test files that hold a test of at least 5 s go first, each as runs of consecutive tests in
     collection order no longer than the longest test, longest run first, each to the next free worker;
   - the rest follow in collection order, in runs sized by estimated seconds (a share of what is left, less
     what the worker still holds), not by count.

   It changes only which worker runs a test and when: every worker still collects the whole selection in
   collection order, so `tools/gate.py`'s `merge_pytest_events` (each worker's collection equals the
   collection run's selection), `gate-collection.json` and the quarantine retry are unchanged; every
   collected test runs once (`workers_collected_alike` is true in every saved run, and the outcome counts
   match the collection). A run with another `--dist` mode, or without the file, is xdist's own.
   `tools/select_tests.py --run` runs one process per test file, eight at a time: `tools/run_order.py` now
   starts the slowest recorded files first within each of its groups (failed last time, changed, the rest).
2. **The split (task step 2)**, below.
3. **Measurement.** `tools/bench/suite_tail.py` (`run`: the measurement above; `durations`: the file);
   `tools/pytest_profile.py` records each test's start and end, and reads the clocks it imported: a test that
   patches `time.monotonic` had given itself a setup of -797,808 s.

Three findings shaped the scheduler, each measured:

- Sending the long tests one at a time (09d4e4f0's first version, run killed at 60 minutes): a module's
  long tests went to different workers, interleaved with other modules, so each re-ran its module fixture:
  setup time in that run's first 25% of tests was 3,928 s against 2,574 s in the whole before run
  (`test_lean_service_schema.py`'s ~70 s fixture once per case). Hence runs of one module's tests.
- `load`'s chunks by count after the long tests: in the simulation, one worker got 894 consecutive tests
  worth 1,886 s at 4,163 s and ran them alone (6,057 s against an ideal 4,883 s). Hence runs by seconds.
- Hidden per-process costs: `experiments/p1.py` caches each item's check per process (`lru_cache`), which
  costs the first `test_p1*` test on a worker 8-16 minutes on this VM. A p1 test that was cheap in the
  profiled run (its cache warm) then ran last on a cold worker: 824 s alone (09d4e4f0), then 545 s
  (b5916ee9). Hence each test's longest time across runs, and whole files. The cost is still paid once per
  worker that runs a p1 file (4,152 worker-seconds of `test_p1*` tests after, 3,009 before, on 5 workers
  rather than 2), but at the start, where it delays nothing.

## The split (task step 2)

| test | before | after | inputs before | inputs after |
|---|---|---|---|---|
| `test_assist.py::test_astra_fix3_property_success_is_invariant_under_node_order_and_monotone_in_budget` | 1 test, 1,430 s (before run) | 14 cases `[graph-search|no_search]`, 57-111 s each, 1,090 s together (09d4e4f0 run) | 7 graphs x 2 search settings x 8 budgets x 5 node orders = 560 sessions | 14 cases x 8 budgets x 5 orders = 560 sessions |
| `test_cli.py::test_check_display_overflow_never_changes_acceptance` | CLI check, then the in-process check | the in-process check runs while the CLI's process does | 1 document (753 sentences, 65,511 bytes), 6 assertions | the same document and the same 6 assertions |

In the split test each case checks, for its graph and search setting, exactly what the loop body checked:
one outcome across the 5 orders at every budget, monotone in the budget, and the expected outcome at the
largest; nothing is shared between cases. The CLI test took 421 s before and 186 s in the 09d4e4f0 run.

Not split, with the reason:

- `test_wire_gate_corpus.py::test_gate_corpus_holds_every_test_input_of_every_unit` (1,257 s before: 806 s
  setup, the module fixture's one nested recording run of 32 test files): its checks need the union of all
  units' recorded inputs, so parts would each repeat the recording or wait on one another. It now starts
  first, and the recording run's own `-n 4` uses the same scheduler: 730-949 s in the after runs.
- `test_p1.py::test_actual_offline_known_answer_gate` (832 s before, all of it the module fixture
  `p1.known_answer()`): the work is one function of `experiments/p1.py`, which is frozen with the P1
  preregistration (`experiments/P1-deference/freeze.json` hashes it); splitting it means editing that file.
  It now starts with the long tests: 575 s into the after run, against 2,069 s before.

## Seeded bugs

All in Python (no Lean or Rust product code changed). `docs/test-tail/mutants.json`, run with
`tools/mutants.py`; result `docs/test-tail/evidence/mutants-result.json`: 15 of 15 killed, each test passing
on the unmutated file first.

| id | file | behaviour | killed by |
|---|---|---|---|
| M1 | tools/test_schedule.py | longest batch first | test_test_schedule::test_head_first_is_a_permutation_led_by_the_recorded_long_tests_longest_first |
| M2 | tools/test_schedule.py | runs no longer than the longest test | test_test_schedule::test_a_module_with_a_long_test_goes_out_whole_in_runs_up_to_the_longest_test |
| M2b | tools/test_schedule.py | a file with a long test goes whole, quick tests too | same |
| M3 | tools/test_schedule.py | the long tests are handed out before the rest | test_test_schedule::test_longest_first_starts_the_long_tests_first_and_ends_sooner_than_load, ::test_an_xdist_run_keeps_the_gates_collection_accounting |
| M4 | tools/test_schedule.py | the longest batch is paired with the shortest of the first two rounds | test_test_schedule::test_the_worker_with_the_longest_test_gets_the_shortest_of_the_first_two_rounds |
| M5 | tools/test_schedule.py | runs after the long tests are sized by seconds, not count | test_test_schedule::test_quick_tests_go_out_by_estimated_seconds_not_by_count |
| M6 | tools/test_schedule.py | what a worker holds counts against its share | test_test_schedule::test_longest_first_starts_the_long_tests_first_and_ends_sooner_than_load |
| M7 | tools/test_schedule.py | another `--dist` mode is kept | test_test_schedule::test_without_recorded_long_tests_or_under_another_mode_xdist_decides |
| M8 | tools/test_schedule.py | a non-seconds entry is dropped, not coerced | test_test_schedule::test_durations_file_round_trips_and_a_bad_file_leaves_the_load_order |
| M9 | tools/run_order.py | selected runs start the slowest file first per group | test_run_order::test_within_each_group_the_slowest_recorded_unit_starts_first |
| M10 | tools/test_schedule.py | a file's seconds are its tests' sum | same |
| M11 | tools/pytest_profile.py | a test patching the clocks cannot skew its record | test_suite_tail::test_profile_records_keep_real_times_when_a_test_patches_the_clocks |
| M12 | tools/bench/suite_tail.py | the durations file keeps only collected tests | test_suite_tail::test_durations_command_writes_the_scheduler_s_file |
| M13 | tests/conftest.py | the suite's xdist runs use the scheduler | test_test_schedule::test_the_suite_conftest_installs_the_scheduler |
| M14 | tools/test_schedule.py | a worker added mid-run (a restarted one) is topped up to the two tests it needs to start | test_test_schedule::test_a_worker_added_mid_run_gets_two_tests_to_start |

Found in review of the diff, after the measured runs: a worker that xdist adds mid-run (to replace a
crashed one) and that was sent a head batch of one test would hold one test, which an xdist worker never
starts, and the run would not end. `check_schedule` now tops a worker up to two tests (M14). The measured
runs had no crashed worker, so the fix changes nothing they did.

## Rulings and deltas

No user-visible product delta: no verdict, diagnostic, wording, limit or checker CPU changes; no relayed
answer is touched, so the relay rules have nothing new to type or bind. The suite's test IDs change: one ID
is replaced by its 14 cases (the split the task asks for, with the input counts above; `gate-collection.json`
regenerated), and new tests are added. The standing rulings (R1-R15) cover none of this; the split is the
DRI's own instruction in this task (L18), recorded here rather than as a DELTA row.

## Follow-ups

- The p1 experiment's per-process cache costs each worker that runs a `test_p1*` file its first 8-16 minutes
  on this VM (+1,143 worker-seconds against `load`'s accidental grouping). Grouping files that share a
  process cache would need a declared group (xdist's `loadgroup` marks are not visible to a `load`
  scheduler); `experiments/p1.py` is frozen.
- Refresh `tools/test-durations.json` (`tools/bench/suite_tail.py durations`, from a `run`) when the slow
  tests change; a test it does not know is scheduled with the quick ones. The file holds each test's longest
  time, so an old slow time persists until the file is rewritten from newer runs.
- Measure on the M5 runner at 16 workers; the simulation predicts 2,445 s against `load`'s 5,731 s on the
  VM's durations.
