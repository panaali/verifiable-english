# Test-speed batch B5: test order and a tracked quarantine

Plan: `manage-agents/reviews/test-speed-research-2026-10.md`, section B5. Base: main cbbab2df.

## What changed

1. **Agents' runs take the likely failures first.** `tools/select_tests.py --run` starts these first: the test files that failed last time, then the test files the change edits, then the rest in name order. The order code is in `tools/run_order.py`, and each run prints its order. The order is a permutation of the selection, so no test is added or dropped. The last failures belong to the worktree. They are the failed tests of its last selected run, kept in its git directory, plus those of its `gate-result.json` if the gate ran after that run. Failed tests are read from each file's JUnit report with the XML library. A test checks these node IDs against pytest's own.
2. **`--maxfail` for agents.** `--run` stops after 5 failed tests by default (`--maxfail N`; `0` runs everything). A recorded run then starts no more files and kills the running ones (each file runs in its own process group). It prints `STOPPED EARLY` with the files that did not run and exits 1. In the map it saves, the static graph answers for those files. Each file's pytest also gets `--maxfail`.
3. **The gate never stops early.** `tools/gate_pytest.py` refuses `--maxfail`, `-x`, `--exitfirst`, `--sw` and `--stepwise-skip`, so a gate run given any of them exits with pytest's usage error (4). The gate already replaced the project's `addopts` and dropped `PYTEST_ADDOPTS`. A test now runs the gate's arguments against a project that asks for `--maxfail=1`, with a shell that sets `-x`, and both failing tests still get a result.
4. **A tracked quarantine.** `tools/test-quarantine.json` holds one entry per test: the test's node ID, its saved load evidence, an owner, the day it was added and an expiry at most 7 days later. `tools/quarantine.py` checks the file; a malformed file fails the gate. The first entry is `tests/test_difffuzz.py::test_ci_run` (owner orchestrator, 2026-10-10 to 2026-10-17). Its [evidence](evidence/quarantine-test_ci_run.json) records 4 observations: the 2026-10-10 nightly (it failed in the suite and passed alone in 183.88 s), the lf-16d verify fix, the profile's 7 of 9 failed builder gates, and the eff-tests before-run. A quarantined test still runs everywhere:
   - **gate:** if it fails, it runs once more, alone and serially. If it passes there, it no longer fails the gate, the counts show its final outcome, and `quarantine.retried` records both outcomes. If it fails again, or gives no result, it fails the gate.
   - **an agent's run:** its failure is printed as `QUARANTINED` and counts towards neither `--maxfail` nor the exit status.
   - **nightly:** `tools/gate.py --no-quarantine` retries nothing, so every failure blocks.

   An expired entry no longer applies: the test blocks again. The record lists expired entries under `quarantine.expired`.

`docs/TESTING.md` ("Order, early stop and the quarantine") documents all four.

## Evidence

**First failure sooner (replay).** [measure.py](measure.py) replays the per-file durations of the nightly coverage map `tree-c6f37e55` (main c24aeab2, created 2026-10-10 07:13 UTC). It covers 340 files and 18,372.1 s of tests, run on 8 workers as `record_units` runs them, and makes each file in turn the one that fails. Run in name order, the last file ends at 3,469.5 s. Putting the failing file first shows its failure sooner by these amounts:

| | minutes sooner |
|---|---:|
| median | 11.7 |
| mean | 12.4 |
| 90th percentile | 27.2 |
| max | 32.9 |

180 of the 340 files show their failure at least 10 minutes sooner. This matches the plan's estimate of about 10 to 20 minutes. It is a replay of saved durations, not a timed run: it does not count `--maxfail` stopping a file early, and a selection smaller than the full suite saves less. The inputs and every row are saved in [durations.json](evidence/durations.json) and [first-failure.json](evidence/first-failure.json). `measure.py --check` recomputes them.

**Real runs on this branch.**
- [demo-run.log](evidence/demo-run.log): a recorded run of 77 selected files with `tests/test_gate_quarantine.py` seeded as failed last time. The order line puts it first and the changed `tests/test_test_order.py` (since renamed `tests/test_run_order.py`, see "Gate runs") second. 76 pytest files passed. Afterwards, the passing file had left the last failures, and the failing `tools/test_layer_policy.py` had been added (see "Found, not fixed").
- [demo-stop.log](evidence/demo-stop.log): the same paths with `--maxfail 1` and 14 selected files. The last-failed `tools/test_layer_policy.py` started first and failed, and the run stopped. 11 files had finished, and 3 (`test_gate_collection.py`, `test_select_tests.py`, `test_wire_gate_corpus.py`) were killed or never started. The run printed `STOPPED EARLY` and exited 1, and none of its processes were left running.

**Shadow gate.** B5 states no shadow count, and it changes no selection: `test_the_order_is_a_permutation_of_the_selection` checks 200 random selections. The nightly full suite and the gate's full run are unchanged. The gate's only new step is the serial retry of a failed quarantined test.

## Seeded bugs

[mutants.py](mutants.py) applies each bug alone, runs its test, restores the file and checks it byte for byte. It writes [mutants.json](evidence/mutants.json). All 10 bugs were caught, and every test passes on the clean source. All of them are in Python: this batch changes no Lean or Rust.

| Bug | File | Behaviour | Failing test |
|---|---|---|---|
| changed_before_failed | `tools/run_order.py` | last-failed first | `test_the_last_failed_then_the_changed_then_the_rest` |
| passed_units_stay_failed | `tools/run_order.py` | a passing file leaves the list | `test_a_unit_leaves_the_last_failures_when_it_runs_to_the_end` |
| recorded_run_never_stops | `tools/test_map.py` | recorded run stops at `--maxfail` | `test_a_recorded_run_stops_after_maxfail_failures` |
| plain_run_ignores_maxfail | `tools/select_tests.py` | one-process run stops at `--maxfail` | `test_a_plain_run_stops_after_maxfail_and_keeps_what_it_did_not_run` |
| plain_run_counts_quarantined | `tools/select_tests.py` | quarantined failure does not fail an agent's run | `test_a_plain_run_whose_only_failures_are_quarantined_passes` |
| gate_plugin_allows_maxfail | `tools/gate_pytest.py` | the gate never stops early | `test_the_gates_plugin_refuses_to_stop_early` |
| retry_failure_ignored | `tools/gate.py` | failing alone still fails the gate | `test_a_quarantined_failure_that_fails_alone_fails_the_gate` |
| nightly_retries | `tools/gate.py` | `--no-quarantine` retries nothing | `test_the_nightly_retries_nothing` |
| expired_entry_applies | `tools/quarantine.py` | an expired entry stops applying | `test_an_entry_applies_from_its_added_day_to_its_expiry` |
| eight_day_entry | `tools/quarantine.py` | at most 7 days | `test_a_malformed_entry_is_refused` |

## Deltas and rulings

See [DELTA.md](DELTA.md). No VE verdict, diagnostic, wire field, theorem or accepted input changes; the deltas are in the developer tools.

## Found, not fixed

- `tools/test_layer_policy.py::test_documented_python_layers_match_policy` fails on main cbbab2df: `ve/ask.py` is in `tools/layer_policy.py` layer 4 but not in `docs/ARCHITECTURE-LAYERS.md`. It is outside this batch. The gate does not run it, because it is a unittest under `tools/`.

## Acceptance

| Item | Owner | State |
|---|---|---|
| Order, `--maxfail`, gate never stops early, quarantine file and gate retry, seeded bugs, replay, full gate on the final HEAD | AGENT | done; the gate record is `evidence/gate.json` |
| Point the nightly at the quarantine: run the nightly with `tools/gate.py --no-quarantine`, or keep `verify.sh` and stop its serial retry from passing a quarantined test | EXTERNAL: orchestrator (`manage-agents/verify.sh`, `nightly-verify.sh`) | deferred. Today's nightly runs plain pytest, which ignores the quarantine, but its serial retry turns a load failure into `PASS (RETRIED)` |
| Review of the gate retry (DELTA row D3) | HUMAN: DRI | deferred to review |
| Renew or drop the `test_ci_run` entry by 2026-10-17 | orchestrator (owner in the file) | open |

Checklist: tests can fail (13: ten seeded bugs). Runs are hermetic (14: scratch projects in `tmp_path`, the clock is injected through `quarantine.today`, and no sleep). The quarantine file is validated strictly and fails closed (4, 5: every field typed, bool-for-int version refused, evidence bound to the test). JUnit is read with the XML library (11). Report numbers come from saved evidence (20). Owners are tagged (21). Tests: the affected files while iterating, then one full gate on the final HEAD (22). DELTA rows (23). Lean, Rust, diagnostics, English and verdicts are unchanged, so items 1–3, 6–10, 12 and 15–19 do not apply.
