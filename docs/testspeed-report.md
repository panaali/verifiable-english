# Test speed and load independence (FINDING-CLASSES class 13, throughput debt P0)

Branch `infra/testspeed`, based on `eccd329b`. How to run the suite, the fast path and the benchmarks is in `docs/TESTING.md`. The numbers below are generated from `tools/bench/results/*.json` by `tools/bench/suite_time.py`. `tests/test_bench_baselines.py::test_the_testspeed_report_shows_the_recorded_runs` fails if they drift.

## Acceptance items

| # | item | tag | status |
|---|---|---|---|
| 1 | Speed out of correctness tests | AGENT | done |
| 2 | Deadlines tested by injection; guard on removed or lowered settings | AGENT | done |
| 3 | `select_tests.py --impacted` as the documented fast path, with a reachability test | AGENT | done |
| 4 | Load-aware workers; prebuilt reuse by default in local runs | AGENT | done |
| 5 | Before and after measurement; the 10 slowest tests | AGENT | done (this machine, loaded; see below) |
| 6 | The wire-s5 recheck's instances | AGENT | done |
| - | Add `tools/bench/test_perf.py` to the nightly job | EXTERNAL (orchestrator) | deferred: the repository has no nightly runner |
| - | Decide whether the full asimov-extended sample rerun stays in the gate | HUMAN (DRI) | deferred: see "Not done" |

### 1. Speed is a benchmark, not a test criterion

- The suite's speed assertions are gone: the pre-commit hook's 10 CPU-second bound on a large staged change, the soft validators' 10 and 30 CPU-second bounds, and the W6a per-batch `cpu < CPU` asserts. They are now CPU-time benchmarks in `tools/bench/test_perf.py`, with stored baselines and a tolerance (`tools/bench/baselines.json`: allowed = baseline × 2 + 0.5 s). The W6a kernel CPU limit stays as a runaway guard: a batch that overruns it is killed, and the test fails on its exit status.
- `tests/test_hang_guards.py::test_no_short_wait_outside_the_reviewed_allowlist` fails on any of the following outside `INJECTED`, a reviewed allowlist keyed by `path::function`:
  - a wait shorter than `HANG_TIMEOUT`, given as a `timeout` keyword or default, or as a positional `wait`, `join` or `result`;
  - a sleep;
  - a short deadline setting (`setenv`, `setattr`, an environment entry or an assignment);
  - an assertion on a clock, a duration or a CPU cost.

  The blanket ≤ 10 s exemption is gone. `test_every_allowlist_entry_still_covers_a_short_wait` rejects stale entries.

### 2. Deadlines by injection

`tests/subprocesses.py::expired_waits` and `tests/test_lean_service.py::expire_service_waits` start the real fake child and inject its deadline as already expired. Each test asserts that the configured wait was the one asked for:

- Lean service request and handshake: `test_operational_faults_fail_closed[hang]`, `test_one_retry_recovers_a_hung_batch`, `test_bad_or_missing_handshake_is_unavailable[silent]`, `test_the_setting_replaces_the_request_and_startup_defaults`
- stage-2 hang faults: `tests/test_stage2_faults.py::test_lean_faults_fail_closed_in_every_adapter`
- Rust: `tests/test_stage2_dispatch.py::test_rust_checker_slower_than_the_setting_is_stopped_at_it`
- one-shot Lean runner: `tests/test_assurance_manifest.py::test_backend_faults_are_checker_unavailable[hang]`, `test_bundle_separates_rejection_from_unavailability`, `test_argument_separates_lean_rejection_from_unavailability`
- pre-commit wire check (30 s): `tests/test_hang_guards.py::test_a_wire_check_that_outlasts_its_wait_blocks_the_commit`
- native build: `tests/test_native_build_lock.py::test_timeout_stops_compiler_descendants`

At run time, `tests/conftest.py` already refused a child started without a checker setting. It now also refuses a real Lean or Rust checker started with a setting below `HANG_TIMEOUT` (`test_a_real_checker_started_with_a_lowered_setting_is_refused`).

### 3. The fast path

`tools/select_tests.py --impacted [--run]` selects the tests a change can affect: their Python import closure (with that of every `conftest.py` pytest loads for them), the Lean executables and the Rust checker their code starts, and the data paths their strings name. `tests/test_select_tests.py` checks five things: every test file is reachable from a source path; Lean and Rust changes select their conformance tests; a change to `tests/conftest.py` or anything it imports selects every test; narrow changes select fewer than 40 files; and unknown, deleted or facade changes select everything. Measured selections, out of 214 files:

| change | files selected |
|---|---|
| `usecases/asimov-laws/rules.ve` | 8 |
| `tools/hooks/precommit.py` | 7 |
| `tools/bench/baseline.py` | 9 |
| `conformance/evaluation.json` | 12 |
| `tests/conftest.py` | 214 |
| `ve/softnorms.py` | 214 |
| `lean/VE/Norms/Wire.lean` | 199 |
| `rust/ve/src/main.rs` | 192 |

The product modules import one another widely (for example, `ve/environment.py`'s closure holds 72 modules), so the static selection stays coarse for product and native changes. `tests/conftest.py` imports `ve.surface`, whose closure holds 72 product modules, so a change to any of them selects every test. The same commit fixes the two documented-layer rows `tools/test_layer_policy.py` reported as failing.

### 4. Parallelism and build reuse

- `-n auto` = max(`VE_TEST_MIN_WORKERS`, min(usable CPUs − 1-minute load, `VE_TEST_WORKERS`)). The floor defaults to 1, so by default the count is the capacity the load leaves, never fewer than one worker (32 CPUs at load 31: one). A larger floor is opt-in; this VM, whose load rarely falls below its 32 CPUs, sets one to avoid running the suite on one worker.
- Without `VE_NATIVE_PREBUILT`, a run reuses the binaries while the stamp of the last build in this checkout still matches. The stamp hashes the source contents and records each executable's identity. `=1` and `=0` keep their meanings, and the gate still builds explicitly.

### 6. The wire-s5 recheck's instances

- `tests/test_lean_service.py` lines 582 and 994 (the 0.5 s healthy retry): the first attempt's deadline is now injected, and the recovery waits `HANG_TIMEOUT`, which the tests assert. The flaky fake now decides to hang per process, so giving up early cannot race it.
- `tests/test_w6a_limit_generator.py::test_lean_authority_reports_resource_limit_on_every_generated_case` already waited `HANG_TIMEOUT` on `eccd329b` (it asserts both waits). Its remaining speed assert (`cpu < CPU` in `run`) moved to the benchmark.

## 5. Measurements

The machine has 32 vCPUs, shared with other agents' jobs, so the load changed during every run. The "after, -n 32" run used the same worker count and prebuilt binaries as the "before" run.

<!-- runs -->
| run | commit | workers | load (1 min) start → end | wall s | CPU s (user + sys) | passed | skipped | slowest test s |
|---|---|---|---|---|---|---|---|---|
| before | `eccd329b` | 32 | 48.5 → 21.6 | 1878 | 20947 | 6144 | 6 | 1592 |
| after, -n 32 | `a4fe3f55` | 32 | 44.5 → 25.7 | 1754 | 20860 | 6233 | 6 | 899 |
| after, -n auto (load-aware), default build reuse | `8e83637a` | 12 | 20.2 → 101.0 | 2500 | 18587 | 6233 | 6 | 946 |
<!-- /runs -->

On this machine the suite is CPU-bound, not bound by its slowest test. In the before run, 20,947 CPU s over 1,878 s is about 11 busy CPUs out of 32, because the other load took the rest. The longest single test fell from 1,592 s to 899 s. That shortens a run on an idle machine; on this one, wall time follows total CPU, which barely changed (20,947 → 20,860 CPU s). The load-aware run used 12 workers while the other load rose from 20 to 101, so it took longer (2,500 s) but caused less contention (18,587 CPU s).

### The 10 slowest tests before, and what was done

<!-- slowest -->
1. `tests/test_english_evidence.py::test_english_mixed_merge_smoke`: 1592 s
2. `tests/test_wire_gate_corpus.py::test_gate_corpus_holds_every_contract_and_soft_test_input`: 1354 s
3. `tests/test_asimov_extended.py::test_rerun_equals_the_committed_results`: 1116 s
4. `tests/test_wire_gate_corpus.py::test_unit_gate_corpus_holds_every_recorded_test_input[norm-defaults@0]`: 763 s
5. `tests/test_wire_gate_corpus.py::test_unit_gate_corpus_holds_every_recorded_test_input[norms@0]`: 574 s
6. `tests/test_readings_s1_differential.py::test_generated_sets_agree_with_lean`: 555 s
7. `tests/test_bluedot_grant.py::test_document_coverage_and_premise_limit`: 507 s
8. `tests/test_english.py::test_identity_fixtures_are_unchanged_after_english_roundtrip`: 403 s
9. `tests/test_rights_three_way.py::test_rights_differential_on_one_thousand_generated_documents`: 401 s
10. `tests/test_assist.py::test_astra_fix3_property_success_is_invariant_under_node_order_and_monotone_in_budget`: 396 s
<!-- /slowest -->

1. **Split** into one test per configuration, and the three slowest configurations into parts: 32 tests. The construct-coverage check no longer renders, because rendering also parses (`test_english_mixed_merge_generates_every_registered_construct`).
2, 4, 5. **Merged and parallelised.** Before, three serial runs re-ran the contract files three times and the norm files twice. Now one recording run under xdist records every unit, each from its own files (`test_gate_corpus_holds_every_test_input_of_every_unit`; `test_one_run_records_each_unit_as_its_own_run_does` checks the per-unit attribution). The soft comparisons it runs are in parts (4 near-limit, 8 rejected), and the generated-trees test no longer repeats them.
3. **Split** into document, records, sample and one test per mutant. Per-test CPU then showed the sample section alone spends 5,990 CPU s and the records section 1,002, about 38% of the suite's CPU. The cause is that Lean's `risk-decision` costs about 5.5 CPU s per case and grows linearly with the batch, so the work is per case, not process start-up. Not reduced: see "Not done".
6–10. **Not changed.** Each is one CPU-bound differential or property run of 184–296 CPU s (`suite-after-auto.json`). On this CPU-bound machine, splitting them would not shorten a run.

The 10 slowest tests after the change (the "after, -n 32" run):

<!-- slowest-after -->
1. `tests/test_wire_gate_corpus.py::test_gate_corpus_holds_every_test_input_of_every_unit`: 899 s
2. `tests/test_bluedot_grant.py::test_document_coverage_and_premise_limit`: 804 s
3. `tests/test_readings_s1_differential.py::test_generated_sets_agree_with_lean`: 792 s
4. `tests/test_english.py::test_identity_fixtures_are_unchanged_after_english_roundtrip`: 750 s
5. `tests/test_assist.py::test_astra_fix3_property_success_is_invariant_under_node_order_and_monotone_in_budget`: 696 s
6. `tests/test_rights_three_way.py::test_rights_differential_on_one_thousand_generated_documents`: 677 s
7. `tests/test_asimov_extended.py::test_rerun_sample_equals_the_committed_results`: 479 s
8. `tests/test_agent_policy_rerun.py::test_every_action_and_policy_query_equals_the_committed_results`: 451 s
9. `tests/test_p1_amendment13.py::test_refresh_dev_is_read_only_and_missing_cache_fails_closed`: 441 s
10. `tests/test_norm_defaults_three_way.py::test_spec8_differentials`: 375 s
<!-- /slowest-after -->

The tests that spend the most CPU (the load-aware run):

<!-- most-cpu -->
1. `tests/test_asimov_extended.py::test_rerun_sample_equals_the_committed_results`: 5990 CPU s
2. `tests/test_wire_gate_corpus.py::test_gate_corpus_holds_every_test_input_of_every_unit`: 1184 CPU s
3. `tests/test_asimov_extended.py::test_rerun_records_equal_the_committed_results`: 1002 CPU s
4. `tests/test_agent_policy_rerun.py::test_every_action_and_policy_query_equals_the_committed_results`: 448 CPU s
5. `tests/test_bluedot_grant.py::test_document_coverage_and_premise_limit`: 296 CPU s
6. `tests/test_readings_s1_differential.py::test_generated_sets_agree_with_lean`: 293 CPU s
7. `tests/test_english.py::test_identity_fixtures_are_unchanged_after_english_roundtrip`: 244 CPU s
8. `tests/test_rights_three_way.py::test_rights_differential_on_one_thousand_generated_documents`: 215 CPU s
9. `tests/test_lean_conformance.py::test_lean_transitive_axiom_allowlist`: 205 CPU s
10. `tests/test_assist.py::test_astra_fix3_property_success_is_invariant_under_node_order_and_monotone_in_budget`: 184 CPU s
<!-- /most-cpu -->

## Not done, and why

- **Asimov-extended sample rerun: about 6,000 CPU s per suite run.** There are two options, and both are a DRI decision. One is a Lean change: let `risk-decision` reuse a policy elaborated once per batch, keyed by `environment_id` and `document_hash`. The other is to run the full 300-record sample rerun nightly and check a strided subset per record in the suite, which reduces what the gate covers.
- **English rendering and parsing.** `render` runs the full unique-derivation parse. `EnglishVocabulary` and the Lark grammar are rebuilt for every parse: in one profiled configuration, 1,896 constructions took 47 of 113 s. The product deliberately keeps no global parse cache, so this needs a design decision, not a test change.

## The gate (checklist 22)

`tools/gate.py` now collects serially and then runs the suite on `--workers` xdist workers (`tools/gate_pytest.py` records the results in the xdist controller, and every worker must collect the collection run's selection). Every nested pytest run is built by `tools/pytest_run.py`: plugin autoload is off and the plugins are named. Before this, two of the branch's changes stopped the gate, because it disables plugin autoload. The xdist-only conftest hook caused an internal error, and the nested `-n auto` recording run failed with "unrecognized arguments: -n". The collection baseline now comes from the gate's own collection (`python3 tools/gate.py --write-collection`). It includes the deselected `tests/test_llm.py::test_live_smoke`, which the old baseline left out. `tests/test_gate.py::test_the_collection_baseline_is_what_the_gate_collects` fails while the baseline differs from that collection.

The gate passed on `6cfb38ba`, the commit before this report's update, in a clean worktree (`git status` empty at start and end; the Lean build directory was copied in, and `lake build` checked it): `python3 tools/gate.py --workers 24`. All six stages passed. The result: 6,263 collected, 1 deselected (the live smoke test), 6,255 passed, 7 skipped (all listed in `tools/gate-optional.json`), 0 failed, and 49 native Rust tests. The suite stage took 2,162 s at a 1-minute load of about 40 on 32 CPUs. An earlier gate run on `8813c3e4` failed one test, the nested `-n auto` run, which `6cfb38ba` fixes.
