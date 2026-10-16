# Test architecture: the Lean answer store, in R1 only (tarch-store)

Rank 5 of `reviews/test-architecture-2026-10-14.md` (draft 2, section 3.6 and its inventory), with Astra's re-check
(ADOPT WITH CHANGES; point 8, "store key": the key uses the binary's actual digest). Branch `infra/tarch-store`
from `dae12d5ff`.

**For the DRI, first:**
1. **The effect is small.** Step 0's hit rate was high (98–99.6% of request lines), so the store was built. Measured
   on the Mac, it removes 93% of the Lean service's CPU, which is about a tenth of a run's CPU. Neither total CPU nor
   wall time moved by more than the shared runner's run-to-run noise (section 3). The store is **off unless a run
   asks for it**. Whether R1 turns it on is a DRI decision; this batch does not turn it on anywhere.
2. **A design point beyond the plan's text.** In store mode the client registers every environment a request's
   cases name in the request line itself, as well as deriving the nonce. Without this, 91–98% of the lines name
   environment handles that an earlier request registered, so their answer depends on the process's handle table.
   32 answers differed between two runs of the same line. Every one whose error text was recorded (24) was a
   handle-table error; the other 8 come from a run made before error texts were logged (section 1). This change is
   test-only (store mode exists only in R1) and is not user-visible. A DRI confirmation is welcome; no standing
   ruling covers it, because it is not a user-visible delta.
3. **External items (orchestrator, not this branch):**
   - R1's runner sets `VE_ANSWER_STORE` if the DRI turns the store on.
   - The nightlies run `tools/answer_replay.py store-replay` after `tools/gate.py --no-quarantine`.
   - tarch-cutoff also creates `tools/answer_replay.py`. This branch's part is one function (`store_replay`) and one
     `COMMANDS` entry, so the merge only joins the two dispatch tables.

## 0. Hard conditions, and where each is enforced

| Condition (DRI) | Delivered | Test |
|---|---|---|
| R1 only; never R2, the merge train or R3, enforced in code | The store is on only with `--answer-store=DIR` or `VE_ANSWER_STORE` (`tests/answer_store.py`), and the variable is removed from the environment once read. Asking for it with `VE_GATE_PYTEST_RESULT` set (tools/gate.py's pytest stage: R2, and R3 = `gate.py --no-quarantine`) raises `pytest.UsageError`. The seam also refuses every request while that variable is set. `gate_environment` never carries the variable | `test_a_store_hit_in_an_r2_flagged_run_is_impossible`: no hit under the flag with a populated store; a nested pytest under the flag exits 4 and creates nothing; the gate's environment drops the variable |
| Step 0: hit rate of exact lines over two R1-sized runs at the same pool size; stop if low | Measured: 98.3–99.5% of exact lines (section 1); built | evidence: section 1 and `measure_plugin.py` |
| Wire seam only: the stored line replaces the process's inside `_roundtrip`, after `_ensure` | `exchange` asks the store after `_ensure`; `_roundtrip` puts the stored line into the client's read buffer and reads it with `_read_line`, so framing, strict decoding, nonce, `check_response` and binding all run | `test_a_stored_answer_is_served_after_the_process_starts` (an unstarted service is started, pinned and handshaken; an unlisted build is refused though the store holds its answer) |
| Unit: the exact batch; nothing stripped, normalised or rewritten | Entries hold the request line and the response line byte for byte | `test_an_entry_is_one_request_line_and_one_response_line`; the byte replay tests |
| Key: SHA-256 of the binary's actual digest, the start-up limits and the request bytes | `key()`: `LeanService.build` (the executable's SHA-256, not a pin), `(address_space, max_rss, max_requests)`, the line | `test_an_entry_is_one_request_line_and_one_response_line` (each part changes the key) |
| Nonce derived from the rest of the line, in store mode only | `LeanService._line`: SHA-256 of the line with a fixed placeholder id; live mode keeps the random nonce | `test_a_store_mode_line_stands_alone` |
| Serving off for changes to ve/backends/, lean/VE/Service/, lean/checkers.lock, tests/subprocesses.py, tests/conftest.py | `GUARDED` (also `tests/answer_store.py`), against the merge base with main, committed or not; off when git cannot say | `test_serving_is_off_for_a_branch_that_changes_a_guarded_path` (6 cases), `test_serving_is_off_when_git_cannot_say_what_changed` |
| Off for explicit timeouts, non-default executables, expected hashes, unlisted builds | `Seam.reason`. Also off for a client subclass (the relay mutation gate's `_Replay` feeds mutated lines) and for a client whose internals a test replaced | `test_serving_is_off_for_every_request_the_plan_excludes`, `test_a_service_with_its_own_timeout_is_never_served` |
| Off for every test in the inventory's live column (`live_service`) | The mark is registered by the plugin and set on every inventory test; `pytest_runtest_protocol` reads it for each test | `test_a_live_service_test_is_never_served_and_is_counted`, `test_every_inventory_test_exists_and_runs_live`; the plugin itself, in a nested pytest on one and two workers: `test_the_plugin_serves_only_unmarked_tests_and_an_alarm_fails_the_run` (review F2) |
| A hit skips nothing a test observes (review F1) | An answer is stored only when its request wrote nothing to the process's standard error and was answered on its first attempt; the retry after any failed attempt is live and unstored. The store is off for a request when any client binding, table (a lowered `DEADLINES` entry, as `lean_routes.completed_within` sets) or `VE_LEAN_SERVICE*` setting differs from those it was installed with, read from the client itself (`SEAM`, `SEAM_GLOBALS`, `SEAM_ENV`) | `test_an_answer_whose_request_wrote_to_standard_error_is_never_served`, `test_an_answer_that_needed_a_retry_is_never_stored`, `test_a_changed_client_setting_turns_the_store_off` |
| Inventory rows 1–13 with a live test each; add RLIMIT_AS (6) and RSS recycle (9); row 14 (standard error) from the review | Section 2; `test_the_service_runs_under_its_address_space_limit`, `test_a_process_above_its_rss_threshold_is_recycled_before_the_next_request` | both new tests, live |
| Nightly byte replay of the whole store against its build; any difference fails | `answer_store.replay`, `tools/answer_replay.py store-replay` (exit 1) | `test_a_planted_wrong_entry_fails_the_byte_replay`, `test_a_planted_nondeterministic_answer_fails_the_byte_replay`, `test_an_empty_or_unreadable_store_is_reported` |
| R1 re-asks a random 1% of hits live, as a drift alarm only | `SAMPLE = 0.01`. A difference (or standard error written) is an alarm, the entry goes, the caller gets the process's answer, and the run fails | `test_a_sampled_hit_that_drifted_is_an_alarm_and_the_caller_gets_the_process_answer`; the run fails on an alarm: `test_the_plugin_serves_only_unmarked_tests_and_an_alarm_fails_the_run` |
| Seeded: a planted wrong entry and a planted nondeterministic answer fail the replay; a planted positional mismatch is refused, not served; an R2 hit is impossible | the four tests named above | section 4 (M1, M7, M8, M12) |

R2 and R3 are unchanged: `tools/gate.py`, the merge train and the nightlies are not touched, and every check that
existed still runs. No test asserts a duration.

## 1. Step 0: the hit rate of exact request lines

**Method.**
- `measure_plugin.py` was registered by a temporary, uncommitted line in tests/conftest.py. It logged every request
  at `_roundtrip`, after `_ensure`, with two keys:
  - the exact line, nonce masked;
  - the same request written self-contained (every environment registered in the line).
- It also logged the SHA-256 of each response.
- Two runs of the same selection on the Mac (ve-mac-1, `-n 6`, pool size 2), HEAD `dae12d5ff` plus the plugin.
- The default collection was split into its light and heavy tiers, so that each run fits one runner slot.

| Tier | Runs | Eligible lines | Exact line hits | of the service seconds | Self-contained line hits | of the service seconds |
|---|---|---:|---:|---:|---:|---:|
| light (15,458 tests) | 2 vs 1 | 626,870 | 99.49% | 98.24% | 99.56% | 98.49% |
| light | 3 vs 2 | 624,645 | 99.39% | 98.28% | 99.47% | 98.78% |
| heavy (170 tests) | 2 vs 1 | 689,841 | 98.31% | 94.22% | 98.38% | 97.16% |

**Why answers to the same line differed** (`store_diff*.py`, and full-byte dumps of 4 files):
- **Handle state, in every cross-run case whose error text was recorded:** 8 in the heavy tier, and 16 of the 24
  between light runs 2 and 3. Lean answered "environment handle … is not registered" in one run. In the other 8
  light cases run 3 answered without error, and run 2 was made before the plugin logged error texts, so its side is
  not known. Two causes:
  - The line named a handle that an earlier request had registered (only 8.8% of light lines and 2.2% of heavy lines
    were self-contained in live mode).
  - The client's mirror had been cleared after a request error while Lean kept its table. Lean then emptied its
    table partway through a line.
  - Hence the store-mode rules: every environment is registered in the line, and a `CheckerUnavailable` request
    error is never stored.
- **Mutated answers, within one run:** `tests/test_relay_mutation_gate.py` subclasses the client and feeds mutated
  lines. Hence the exact-class and replaced-internals rules.
- **No Lean nondeterminism was seen.** In the store-mode runs below, 53,500 sampled hits were asked of the process
  again, and every one was byte-identical except one inconclusive case (a handle error, which is never compared).

**What the hit rate depends on.**
- Batches depend on which tests share a process, because Python's per-process caches decide which cases are sent.
- test_views alone, in one process, hit only 46% of its lines (17,858 of 38,425) against a store that the `-n 6` runs
  had filled.
- So an R1 run whose selection or worker count differs from the runs that filled the store hits less. The first R1
  run after a Lean build hits nothing (a new namespace).

## 2. The bypassed-behaviour inventory (plan 3.6, rows 1–13; row 14 from the review)

The wire seam answers after `_ensure` and reads the stored line through `_read_line`. Every test named below carries
`live_service`, so no store answers it. The data is in `INVENTORY` in tests/answer_store.py, and
`test_every_inventory_test_exists_and_runs_live` checks each name and its mark with `ast`.

**Proof each one ran live:**
- Source: the summary of a store-mode light run, `evidence/store-run-light-s2.json`. In that run, 590,839 of 597,872
  lookups were answered from the store.
- Its `live_tests` table counts each `live_service` test that ran and the requests it made. A live test is never
  looked up, so it has no hits.
- The heavy tier has no `live_service` test.
- "Requests" counts `exchange` calls. A test that fails at start-up makes none, and that start-up is what it tests.

| # | Behaviour | Wire seam skips | Live test(s) | Ran live in the store run (test IDs, requests) |
|---|---|---|---|---|
| 1 | relay: wire check, memo, error classes | nothing (above the seam) | tests/test_relay.py | above the seam: no mark needed |
| 2 | pool split, parallel workers, earliest failure first | nothing (pool size is in the lines) | TLS::test_pool_serves_concurrent_callers, ::test_pool_answers_a_batch_in_parallel_with_the_same_results, ::test_pool_raises_the_earliest_failing_request | 1/12, 1/12, 1/7 |
| 3 | environment handles: encoding, registration, mirror, resend | handle reuse between requests (store mode registers every environment in its line) | tests/test_lean_handles.py (whole file) | 35/196 |
| 4 | chunking; a case over 16 MiB is ResourceLimit | nothing | TLS::test_chunks_fit_their_byte_budget | 1/18 |
| 5 | budget member, envelope, 16 MiB line cap | the random nonce | TLS::test_bound_request_error_is_deterministic, ::test_oversized_exchange_is_resource_limit_without_start, ::test_operational_faults_fail_closed | 2/2, 1/1, 12/12 |
| 6 | spawn, pin check, RLIMIT_AS, handshake | nothing (after `_ensure`) | TLS::test_unlisted_build_is_refused_by_default, ::test_bad_or_missing_handshake_is_unavailable, **::test_the_service_runs_under_its_address_space_limit (new)** | 1/0, 6/0 (fail at start, as tested), 1/2 |
| 7 | deadline computation (`_deadline`) | nothing: it runs, nothing is enforced | TLS::test_the_injected_clock_records_a_miscomputed_deadline; tests/test_w6a_limit_generator.py::test_lean_authority_reports_resource_limit_on_every_generated_case | 4/4; 3/171 |
| 8 | enforcement: CPU-deadline kill, wall cap, timeout | all of it (a changed `DEADLINES` entry or `VE_LEAN_SERVICE_TIMEOUT` turns the store off) | TLS::test_a_request_past_its_cpu_deadline_names_its_mode_and_is_not_retried, ::test_each_phase_of_a_request_is_bounded_by_its_cpu_deadline, ::test_a_request_that_gets_no_cpu_meets_the_wall_cap; test_soft_request_economy::test_soft_requests_on_the_widest_environment_stay_within_a_cpu_deadline; test_question_reading::test_the_whole_question_is_bounded_by_the_modes_deadline; review: the five `completed_within` tests (test_readings_lazy_pairs, test_lean_layers_once, test_readings_lean_sharing ×3) | 1/1, 6/6, 1/1; 1/2; 1/1; review additions not in that run |
| 9 | retry once, restart, RSS recycle | the process's failures and its RSS (an answer that needed a retry is never stored) | TLS::test_operational_faults_fail_closed, ::test_one_retry_recovers_a_hung_batch, ::test_recycling_after_max_requests, **::test_a_process_above_its_rss_threshold_is_recycled_before_the_next_request (new)**; review: the three `retries == 0` tests of tests/test_lean_service_schema.py | 12/12, 1/1, 1/5, 1/9; review additions not in that run |
| 10 | framing and decoding: line reader, 1 GiB cap, strict JSON, nonce match | nothing (the stored line goes through `_read_line`) | TLS::test_complete_lean_response_obeys_size_cap, ::test_operational_faults_fail_closed | 1/1, 12/12 |
| 11 | schema check (`check_response`) | nothing | TLS::test_random_malformed_responses_never_escape_schema; tests/test_lean_first_b13b.py (whole file) | 1/48; 45/81 |
| 12 | binding: id, mode, one row per case, digest, index, case_index | nothing | TLS::test_results_not_bound_to_their_cases_fail_closed, ::test_request_errors_without_their_binding_fail_closed | 11/22, 14/14 |
| 13 | stats counters | the process's own counts for a hit | TLS::test_pool_serves_concurrent_callers; tests/test_lean_handles.py | 1/12; 35/196 |
| 14 | the process's standard error (Lean's `PANIC` messages) | the process's writes (an answer whose request wrote there is never stored) | test_environment_field_types::test_every_lean_route_rejects_every_wrong_type_without_panicking, ::test_every_lean_route_reads_every_nested_value_without_panicking; test_lean_first_triage::test_df12_risk_route_rejects_an_nbsp_act_phrase | review additions not in that run |

TLS = tests/test_lean_service.py; the whole file is `live_service`. In that run 312 `live_service` tests ran, 242 of
them with requests. Requests that were not eligible:

| Reason | Requests |
|---|---:|
| client subclass (the relay mutation gate) | 12,511 |
| `live_service` test | 833 |
| unlisted build | 161 |
| explicit timeout | 141 |
| non-default executable | 52 |
| client replaced by the test | 22 |

## 3. The effect, measured on the Mac (before and after)

**Conditions.**
- ve-mac-1, `-n 6`, the light and heavy tiers of the default collection.
- The runner was shared with six other batches' runs: 1-minute load 4–41 on 18 cores.
- The "before" runs are live. The "after" runs are store mode, with an earlier store-mode run having filled the
  store.
- On this branch the store is off (it changes guarded paths), so for these runs `GUARDED` was emptied by an
  uncommitted edit. That edit is also why the 4 guard tests failed in those runs, and no other test did.
- CPU is `RUSAGE_CHILDREN` of the controller: every worker and every child, including Lean, Rust and git.
- "Lean CPU" is the user and system CPU of every `ve_service` process the workers ran, read from /proc before each
  stopped.
- Both were collected by a temporary, uncommitted conftest hook.

**Heavy tier (170 tests).** S = store run; hits = requests answered from the store.

| Pair | Mode | Wall (s) | Sum of test durations (s) | CPU (s) | Lean CPU (s) | Hits | Load |
|---|---|---:|---:|---:|---:|---|---|
| P1 | live | 966 | 5,686 | 4,812 | – | – | 30–42 |
| P1 | S | 750 | 4,392 | 3,499 | – | 666,917 of 674,085 | 18–34 |
| P2 | S | 890 | 5,224 | 3,736 | – | 659,271 of 666,219 | 31–35 |
| P2 | live | 566 | 3,325 | 3,756 | – | – | 21–34 |
| P3 | live | 561 | 3,308 | 3,928 | **495.7** (83 processes) | – | 5–22 |
| P3 | S | 669 | 3,872 | 3,803 | **20.4** (79 processes) | 663,595 of 670,642 | 10–16 |

**Light tier (15,485 tests).**

| Mode | Wall (s) | Sum of test durations (s) | Lean CPU (s) | Hits |
|---|---:|---:|---:|---|
| live | 846 | 4,536 | – | – |
| live | 820 | 4,440 | **259.2** (1,475 processes) | – |
| S, first run (records) | 977 | 5,295 | – | 477,269 of 600,734 (repeats within the run) |
| S | 959 | 5,268 | **34.7** (1,472 processes) | 590,839 of 597,872 |

**What the measurement shows.**
- **Lean CPU falls by 93%:** from 755 to 55 CPU-seconds per run of the default collection (both tiers).
- **That is about a tenth of a run's CPU.** In the heavy tier, Lean was 495.7 of 3,928 CPU-seconds (12.6%).
- **Total CPU and wall time did not change measurably.** Identical live heavy runs differed by 28% in CPU (3,756
  vs 4,812 s) and by 72% in wall time (561 vs 966 s). The store's differences within each pair go both ways:
  - CPU: −27%, −0.5% and −3%;
  - wall: −22%, +57% and +19%.
- **What a hit costs.** A profile of one process (test_views and test_assist_invariants, 223,571 requests) puts the
  store's own work at about 63 µs per request (`applies` 5.9 s, `answer` 8.1 s). Lean costs about 0.74 ms of CPU per
  heavy-tier request and 0.17 ms per small one.
- Two optimisations came from that profile and are in commit `0da9e30e`:
  - the executable path is resolved once per path, not 10 `lstat` calls per request;
  - recently used answers are kept in memory, at most 64 MiB per process.
- **Why this is smaller than run B's −38.6%.** Run B served at `run_bound`, which skipped the whole client: encoding,
  framing, schema and binding. The plan forbids that seam (Astra 2). At the wire seam, all of that Python work still
  runs on a hit, and only the Lean process's work is saved.

**Size.** After these runs, the store for one build held 349,070 entries in 1.5 GB. Lines were 1.5 KB at the median
and 5.6 KB on average; environments were 38% of the line bytes.

## 4. Seeded bugs (`mutants.json`, driver `seeded_bugs.py`)

- 14 bugs were planted on the Mac in one job. Each was planted in a changed file, the named tests ran in a nested
  pytest and failed (exit 1), and the file was restored byte for byte. Unmutated, the same 19 tests passed.
- The only product code that changed is Python (`ve/backends/lean_service.py`). No Lean or Rust changed, so the
  Python bugs are the per-language requirement.

| ID | File | Bug | Test that failed |
|---|---|---|---|
| M1 | ve/backends/lean_service.py | a stored line skips the client's checks | test_a_planted_positional_mismatch_is_refused_not_served |
| M2 | ve/backends/lean_service.py | the store-mode nonce is random | test_a_store_mode_line_stands_alone, test_a_stored_answer_is_served_after_the_process_starts |
| M3 | ve/backends/lean_service.py | store mode registers only the environments the process lacks | test_a_store_mode_line_stands_alone |
| M4 | ve/backends/lean_service.py | no `_ensure` in store mode | test_a_stored_answer_is_served_after_the_process_starts |
| M5 | ve/backends/lean_service.py | RLIMIT_AS not applied | test_the_service_runs_under_its_address_space_limit |
| M6 | ve/backends/lean_service.py | RSS recycle off | test_a_process_above_its_rss_threshold_is_recycled_before_the_next_request |
| M7 | tests/answer_store.py | the seam ignores the gate flag | test_a_store_hit_in_an_r2_flagged_run_is_impossible |
| M8 | tests/answer_store.py | the plugin accepts the store under the gate | test_a_store_hit_in_an_r2_flagged_run_is_impossible |
| M9 | tests/answer_store.py | `live_service` tests served | test_a_live_service_test_is_never_served_and_is_counted, test_serving_is_off_for_every_request_the_plan_excludes |
| M10 | tests/answer_store.py | a client whose internals a test replaced is still served | test_serving_is_off_for_every_request_the_plan_excludes |
| M11 | tests/answer_store.py | `ve/backends/` not guarded | test_serving_is_off_for_a_branch_that_changes_a_guarded_path |
| M12 | tests/answer_store.py | the replay compares decoded values, not bytes | test_a_planted_wrong_entry_fails_the_byte_replay, test_a_planted_nondeterministic_answer_fails_the_byte_replay |
| M13 | tests/answer_store.py | a `CheckerUnavailable` request error is recorded | test_a_checker_unavailable_request_error_is_never_recorded |
| M14 | tests/answer_store.py | a sampled hit is served without the live comparison | test_a_sampled_hit_that_drifted_is_an_alarm_and_the_caller_gets_the_process_answer |
| M15 | tests/answer_store.py | an answer whose request wrote to standard error (a PANIC) is stored | test_an_answer_whose_request_wrote_to_standard_error_is_never_served |
| M16 | tests/answer_store.py | the byte replay ignores standard error | test_an_answer_whose_request_wrote_to_standard_error_is_never_served |
| M17 | ve/backends/lean_service.py | the retry after a failed live attempt still uses the store, and records | test_an_answer_that_needed_a_retry_is_never_stored |
| M18 | tests/answer_store.py | a client table changed in place (a lowered `DEADLINES` entry) is still served | test_a_changed_client_setting_turns_the_store_off |
| M19 | tests/answer_store.py | a changed `VE_LEAN_SERVICE*` setting is still served | test_a_changed_client_setting_turns_the_store_off |
| M20 | tests/answer_store.py | the plugin never reads the `live_service` mark (PROBE F2) | test_the_plugin_serves_only_unmarked_tests_and_an_alarm_fails_the_run |
| M21 | tests/answer_store.py | an alarm never fails the run | test_the_plugin_serves_only_unmarked_tests_and_an_alarm_fails_the_run |
| M22 | tests/answer_store.py | the workers' reports are dropped (`pytest_testnodedown`) | test_the_plugin_serves_only_unmarked_tests_and_an_alarm_fails_the_run |

M15 to M22 come from the review fix round (section 6). The same driver ran all 22 mutants again on the VM, and each
named test failed (`mutants.json`, `review_fix`); unmutated, the 23 named tests passed.

M4 first survived: both phases of its test started the service with `with`. The test now asks an unstarted service
and also checks that the pins refuse an unlisted build before the store is asked (commit `6fc0a918e`); M4 then
failed it.

## 5. Notes

- **DELTA:** none user-visible (`DELTA.md`). When the store is not installed (every run but an R1 that asks for it,
  and every product use), `exchange` builds the same line as before. `_roundtrip` gained an optional final argument.
- **Two forms of the option.** Write `--answer-store=DIR`. As two words, pytest's first pass reads an existing DIR as
  a test path before the conftest registers the option, and roots the run there (seen once on the Mac). The
  variable has no such problem.
- **Synced with main** at `8bc65a907` (commit `8f9171ad`). The one conflict was docs/TESTING.md, where both
  sections were kept. Main's client change (the `search-budget` mode's deadline) does not touch the seam.
  `tools/regen_generated.py --check` passes all 27 entries after the Lean rebuild. On `8f9171ad` the whole default
  collection passed on the Mac: 16,383 light and 166 heavy tests, 0 failures. The selector picks every unit
  for this branch (checklist item 9), so this is the selected set.
- **Not run here:**
  - the full release gate, which the chain runs on the final HEAD;
  - the store in a real R1 run, since no runner sets the variable yet;
  - `tools/gate_collection.py --check`, because no test was removed or renamed (20 added).
- **Relay mutation gate: passes after a second sync with main.** At `e67dae7dd`, `tools/relay_mutation_gate.py`
  (42 routes, 116,583 mutants) reported 13 failures, and the same 13 on the merge base `dae12d5ff`. Twelve were
  allow-list entries of the `parse` and `readings-route` routes that matched nothing. The thirteenth was an accepted
  `norm-defaults` mutant (`results/*/result/unsaid/*/description` emptied). The pre-review gate counted them, so the
  branch was merged with main again at `171faae80` (commit `1487d7add`). Main now has fix/relay-mutation-gate
  (`f59dde41e`). There were no conflicts, and `tools/regen_generated.py --check` passes all 27 entries. On
  `1487d7add` the gate reports 43 routes, 119,091 mutants and 0 failures. This branch's own diff changes no relay,
  schema or allow list. The tests the merge touched pass on the Mac at `1487d7add`: the answer store, norm-defaults,
  platform contract, relay mutation gate and route row schemas, 629 passed.
- Acceptance items: all AGENT except the external items listed at the top (orchestrator).

## 6. Review fix round (tarch-store-review.final.md)

- **F1 (B): a hit skipped behaviours the inventory did not list.** Fixed as a class, in the seam, so that it holds for
  every test and not only the ones the sweep found:
  - *Standard error (Lean's PANIC).* A hit writes nothing there, so an answer is stored only when its request wrote
    nothing to the process's standard error. A sampled hit whose live request writes there is an alarm, and the
    byte replay fails on it. Inventory row 14.
  - *Deadlines set through `completed_within`, and every other client setting.* The seam no longer lists the client
    names it compares: `SEAM` is every method and property of `LeanService`, and `SEAM_GLOBALS` is every binding of
    `ve/backends/lean_service.py` except the seam itself and the digest cache. Tables (`DEADLINES`) are also
    compared by value, since `completed_within` changes an entry in place, and so are the `VE_LEAN_SERVICE*`
    settings. The plugin's `pytest_configure` is `trylast`, so it sees the suite's settings.
  - *`retries == 0` (row 9).* After any failed attempt, the client's retry asks the process without the store, and its
    answer is not stored. A hit therefore stands for an answer the process gave on its first attempt.
  - The swept tests carry `live_service` as well, and are listed in rows 8, 9 and 14: the two panicking tests and
    test_df12_risk_route_rejects_an_nbsp_act_phrase (row 14; the third PANIC check in the sweep is the helper
    `lean_route_rows`, which that test uses); the five `completed_within` tests (row 8); and the three tests behind
    the `retries == 0` checks of tests/test_lean_service_schema.py (row 9; the check at line 108 is in the
    `genuine_errors` fixture, so its two tests are marked).
  - PROBE F1 collected nothing (exit 5) before the fix. After it, 22 tests are collected (exit 0).
- **F2 (B): no test ran the plugin with a store on.** `test_the_plugin_serves_only_unmarked_tests_and_an_alarm_fails_the_run`
  runs a nested pytest with `--answer-store=` over one marked and one unmarked test, on two workers and on one:
  - Only the unmarked test is answered from the store. The marked test is counted as live.
  - The workers' reports are merged (`pytest_testnodedown`, `merged`).
  - A planted entry the client refuses fails a run whose two tests pass.
  The nested run is told that the branch changes no guarded path, by a stand-in for `changed_guarded_paths` (this
  branch changes guarded paths). PROBE F2 exited 1 before the fix and exits 0 after it. Mutants M20 to M22 also
  fail that test.
- **F3, F4, F5 (C):** not changed in this round. F5 is still open for the DRI.
- **DELTA:** none user-visible. Only the test-only store changes what it stores and when it answers.

## Self-review against BUILDER-CHECKLIST

1. **Lean answers typed and contained: PASS.** No new route or answer field. A stored answer goes through the same
   `check_response` and binding. M1 and test_a_planted_positional_mismatch_is_refused_not_served show a stored answer
   that fails binding is refused.
2. **Required deliverables: PASS.** Section 0 maps each plan row and DRI condition to its delivery and test. No
   permanent report test was added (D4): the evidence is saved files.
3. **Tests can fail: PASS.** 22 seeded bugs (section 4, mutants.json; M15 to M22 from the review). The replay comparator was run
   head-against-head (passes) and against an empty store (0 entries). It fails on a value-equal byte change (M12).
4. **Python, Lean and Rust agree: N.A.** No Lean or Rust change. Live answers are unchanged (DELTA none), and
   53,500 sampled hits were byte-identical to the process.
5. **R8 binding: PASS.** The client's binding runs on every hit (row 12 tests are live; M1).
6. **Gate evidence matches the final HEAD: PASS for this report's evidence.** The measurements name their
   snapshots. The full gate is the chain's, on the final HEAD.
7. **No unsigned item: PASS.** No user-visible delta. The store-mode registration is raised for the DRI at the top,
   as a design point, not a delta.
8. **Every user-visible change in DELTA: PASS.** DELTA.md is "none", and section 5 says why.
9. **Test selection: PASS.** `select_tests.py --base $(git merge-base HEAD main)` selects every unit because the
   branch changes tests/conftest.py and ve/backends/. Both are genuine whole-suite triggers: conftest loads the
   plugin into every session, and the client is behind every Lean test.
10. **Lean statements: N.A.** No Lean change.
11. **Budgets, limits and deadlines fail closed: PASS.**
    - The RLIMIT_AS and RSS tests are new (M5, M6).
    - A request with an explicit timeout is never served (test_a_service_with_its_own_timeout_is_never_served).
    - No test uses a literal timeout or sleep (test_hang_guards passes).
12. **No CPU or memory regression: PASS.** Live mode is unchanged. Store mode is measured in section 3, and each
    process keeps at most 64 MiB of answers in memory (test_a_repeated_batch_is_answered_from_memory_within_its_bound).
13. **Test-removed trailers: N.A.** No test removed or renamed (`git diff main...HEAD -- tests/` removes no
    `def test_`).
