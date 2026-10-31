# eff-20261030-1: a heavy test file of a selected run as several pytest processes ("chunks")

**Status: built; ready for the chain's gate.** HEAD: the last commit on branch infra/eff-20261030-1 (merge base c8c7e09741).
**What changed:** `tools/select_tests.py` runs each measured heavy test file (5 of the 8) as 2 to 4 pytest processes in the same `--jobs` pool. A file passes only if every chunk passes and every collected test ran in exactly one chunk. The map still gets one entry per file. With `--chunk-heavy` the plan lists the chunks for Actions.
**Measured:** step 1 projects a 59% cut for the top 4 files (BUILD). In step 5 every file gave identical per-node outcomes; the chunked wall fell 52-74% on the Mac and 31-60% on Actions runners.
**Open:** an orchestrator change to `gha/select-plan.py` (lines below; mine is not to make). Rows for files not yet measured. **No DRI signature needed; no DELTA rows; trust +0.**

## Sources

- PIPELINE-LIMITS L115 (test_acts_vocab_mutants as the long pole), L18 (the suite's long tail), L135 (Actions planner floor).
- The task text's measurements.
- `reviews/efficiency-daily-20261030.md` **does not exist** in /home/seyran/code/manage-agents/reviews (`ls reviews | grep 1030` lists no such file). I used the task's own numbers in its place.
- Docstrings read: `tools/select_tests.py` (run, run_recorded, record_ordered, light_tier), `tools/test_map.py` (record_units, build_map), `tools/run_order.py`, `tests/conftest.py`, `tests/lean_pool.py`, `gha/select-plan.py`, `gha/shard-select.py`.

## Step 1: measure before building

Command: `zsh docs/infra/eff-20261030-1/measure.sh /tmp/eff1-step1`. It does one `mac-pytest.sh -- -n 0 -v --durations=0 <file>` run per file: 8 runs, all on ve-mac-1 (aarch64), exit 0 (`step1/runs.tsv`). The raw logs are in `step1/logs.tar.gz`. The table comes from `uv run python docs/infra/eff-20261030-1/chunk_table.py /tmp/eff1-step1` (`step1/table.md`, `step1/table.json`).

How the table counts:
- **Repeated setup** is the process time outside the per-node durations, plus module or session setups of 1 s or more that at most 10 nodes have.
- **Divisible setup:** test_acts_vocab_mutants' pool fixture elaborates only the tests its process runs (`tests/lean_pool.py`), so the table spreads that setup over the file's nodes instead of repeating it.
- **k = 2, 3, 4:** repeated setup + max(heaviest chunk under a longest-first split, largest node).

| file | nodes | wall s | repeated setup s | largest node s | k=2 | k=3 | k=4 | best cut |
|---|---|---|---|---|---|---|---|---|
| tests/test_consolidation_tools.py | 288 | 357.7 | 7.9 | 290.0 | 298.0 | 298.0 | 298.0 | 17% |
| tests/test_acts_vocab_mutants.py | 643 | 129.8 | 0.5 (divisible) | 0.2 | 65.2 | 43.7 | 32.9 | 75% |
| tests/test_readings_rd6b_differential.py | 16 | 344.1 | 0.2 | 43.7 | 178.0 | 115.6 | 89.0 | 74% |
| tests/test_english_evidence.py | 77 | 510.3 | 0.5 | 26.7 | 255.4 | 170.5 | 128.0 | 75% |
| tests/test_trust_mutants.py | 505 | 515.9 | 178.4 | 23.9 | 347.2 | 290.9 | 262.8 | 49% |
| tests/test_defaults_checks.py | 3 | 99.2 | 0.1 | 98.1 | 98.3 | 98.3 | 98.3 | 1% |
| tests/test_speech_polar_lean.py | 9536 | 608.1 | 32.3 | 22.3 | 320.2 | 224.2 | 176.2 | 71% |
| tests/test_lean_conformance.py | 87 | 108.4 | 0.4 | 91.6 | 92.0 | 92.0 | 92.0 | 15% |

**Stop rule** (from the script's last line): the top 4 go from 1,342 s to 548 s at each file's best k, a **59% cut**, above the 35% bar. No top-4 file has one node above half its wall time except consolidation_tools. The verdict is **BUILD**.

`chunk_table.py --data` wrote `tools/test-chunks.json` (format `ve-test-chunks@1`, with its run line, as tests/heavy.json records its run). Its `never` rows are files whose best cut is under 20%:
- consolidation_tools: one test is 290 of 358 s.
- defaults_checks: one test is 98 of 99 s.
- lean_conformance: one test is 92 of 108 s.

None of the 8 files is setup-dominated in the narrow sense. The worst setup is trust_mutants: 178 s repeated per chunk, but it still cuts 49%. The `never` rule covers both causes (setup or one test) with the same data.

## What was built (one owner each)

| task item | where | evidence |
|---|---|---|
| 1. One place decides chunking | `tools/select_tests.py` section "Chunks" (details below) | `test_only_measured_units_over_the_threshold_are_chunked_and_capped`, `test_a_setup_dominated_file_is_never_chunked`, `test_a_malformed_decisions_file_chunks_nothing` |
| 2. A collection hook keeps chunk i of k | `tools/test_chunks.py` and `tests/conftest.py` (details below) | `test_the_parts_cover_every_node_exactly_once` (hypothesis, k 1..5), `test_the_parts_do_not_depend_on_collection_order`, `test_each_chunk_runs_its_part_and_together_they_run_every_test`, `test_unset_or_one_chunk_runs_every_test`, `test_the_chunk_applies_after_marker_deselection`, `test_the_suites_conftest_applies_the_chunk`, `test_a_chunk_under_xdist_is_a_usage_error`, `test_a_nested_run_never_inherits_the_chunk` |
| 3. Chunks run in the pool; the file is one unit | `record_ordered` and `run_recorded` (details below) | `test_a_chunked_file_passes_as_one_unit`, `test_a_failed_chunk_fails_the_unit`, `test_a_test_missing_from_every_chunk_fails_the_unit`, `test_a_test_run_by_two_chunks_fails_the_unit`, `test_the_map_entry_of_a_chunked_file_is_the_union_of_its_chunks`, `test_maxfail_stops_across_chunks_as_across_units`, `test_a_full_run_never_chunks` |
| 4. `--chunk-heavy` plan entries | `chunk_plan` and `main` (details below) | `test_the_plan_lists_chunks_only_with_the_option` (both cases), `test_the_chunk_option_is_for_a_recorded_selected_run` |

**1. The chunk decision** (`tools/select_tests.py`, section "Chunks"):
- The constants are `CHUNK_SECONDS` (500), `CHUNK_TARGET_SECONDS` (400) and `MAX_CHUNKS` (4), each with its reason in a comment.
- k = ceil(map seconds / 400), capped at 4 and at the row's `max_chunks`.
- The step 1 data are in `tools/test-chunks.json`, read by `chunk_decisions`.

**2. The hook** (`tools/test_chunks.py` and `tests/conftest.py`):
- `tools/test_chunks.py` holds the pure rule `partition`/`chunk`, the label syntax and `register`.
- `tests/conftest.py` `pytest_configure` calls `test_chunks.register`, next to the heavy-marker hook.
- `VE_TEST_CHUNK=<i>/<k>` is popped before any test runs. `tools/nested_pytest.py` also drops it, so no nested run inherits it.
- The hook is a `trylast` plugin, so it applies after `-m`/`-k`, and it deselects through `pytest_deselected`.
- Unset, nothing is registered.

**3. Running chunks as one unit** (`record_ordered` and `run_recorded`):
- Chunks are entries in the same `test_map.record_units` pool. `test_map.unit_command` and `chunk_setting` map a label to its file plus the variable.
- One `--collect-only` listing per chunked file, then `chunk_problems`: gap, overlap, duplicate, extra, wrong chunk, missing report and a lossy rule each fail the unit.
- `fold_chunks` gives the union of edges, the sum of seconds and the first failing exit.
- Each chunk's failures count towards `--maxfail` as it ends.
- Quarantine, failed-first state and STOPPED EARLY are keyed by the file.
- A file with only some chunks in this run (an Actions shard) is checked per chunk but left out of the map (static graph).

**Where full runs are excluded:**
- `run` passes `chunked=not full`, and `run_recorded` refuses chunk labels when not chunked.
- `main` refuses `--chunk-heavy` with `--full`, `--impacted`, `--no-record` or `--tier`.
- `tools/gate.py` never calls select_tests: it runs the suite through `tools/gate_pytest.py`, and VE_TEST_CHUNK is never set there.

**4. The plan with `--chunk-heavy`** (`chunk_plan` and `main`):
- `"selected"` lists `<file>::chunk(<i>/<k>)` in the file's place.
- `"chunk_seconds"` gives each label's expected seconds: S × (setup share + (1 − setup share) / k).
- Without the option the plan is not touched (byte-for-byte test).
- `select_tests.run()` given such a plan runs each label through the hook. This was exercised on Actions (below).

**Deviation (stricter than the task text, not weaker):** only files with a measured row are chunked. A file the table has not measured is never chunked, because what its chunks would repeat is unknown. L18 measured test_wire_gate_corpus.py at 166 s of setup to 70 s of tests. `measure.sh` and `chunk_table.py` add a row.

## Step 5: after building

### Mac (ve-mac-1)

Command: `zsh docs/infra/eff-20261030-1/measure5.sh /tmp/eff1-step5`. Each file runs whole (`--bench-chunk 1/1`), then each chunk alone. The `tools/bench/chunk_probe.py` plugin sets the chunk variable before the suite's own hook reads it and prints the process's peak RSS. The table comes from `uv run python docs/infra/eff-20261030-1/step5_table.py /tmp/eff1-step5` (exit 0 = identical outcomes for every file). Outputs: `step5/mac-table.md`, `step5/mac-table.json`, `step5/mac-logs.tar.gz`, `step5/mac-runs.tsv`.

The runs were serial and back to back. The Mac's 1-minute load was 15-40 during them (mac-pytest.jsonl), against 4-27 in step 1, so the whole-file walls here are slower than step 1's. The chunked wall is the longest chunk, as when the chunks run side by side.

| file | k | nodes | whole wall s | chunk walls s | chunked wall s (cut) | chunk sum s | peak RSS whole MiB | peak RSS per chunk MiB | outcomes identical |
|---|---|---|---|---|---|---|---|---|---|
| test_acts_vocab_mutants | 2 | 643 | 258.5 | 97.6 / 101.8 | 101.8 (61%) | 199.4 | 116.6 | 87.1 / 89.5 | yes, 643 passed |
| test_english_evidence | 4 | 77 | 707.7 | 183.5 / 154.0 / 163.8 / 167.5 | 183.5 (74%) | 668.8 | 158.7 | 148.2 / 146.1 / 149.2 / 145.9 | yes, 77 passed |
| test_readings_rd6b_differential | 4 | 16 | 518.1 | 155.5 / 111.9 / 104.9 / 147.0 | 155.5 (70%) | 519.3 | 95.6 | 81.6 / 83.5 / 81.8 / 82.8 | yes, 16 passed |
| test_speech_polar_lean | 4 | 9536 | 662.2 | 173.2 / 165.3 / 177.2 / 207.3 | 207.3 (69%) | 723.0 | 1192.6 | 1170.8 / 1084.7 / 1037.9 / 1040.3 | yes, 9536 passed |
| test_trust_mutants | 4 | 505 | 855.6 | 224.1 / 248.5 / 413.9 / 262.8 | 413.9 (52%) | 1149.2 | 77.5 | 62.9 / 77.9 / 63.3 / 63.0 | yes, 505 passed |

"Identical" means the union of the chunks' (node ID, outcome) pairs equals the whole run's, and no node is in two chunks.

**Memory:** each chunk's peak RSS is at most the whole run's. Run side by side, k chunks hold up to k times one process. The worst case is speech_polar: 4 × ~1.1 GiB against 1.2 GiB whole.

**CPU cost:** the summed chunk seconds against the whole run are −23% to +34%. trust_mutants is the +34%, from its 178 s of repeated setup.

### Actions: one selected run with chunks

Command: `zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run --chunk-heavy`. This was run eff-20261030-1-ddc954b9-t399713 on commit ddc954b9d (all product code final; later commits are docs and evidence only): 517 entries, 5 shards (capped by queue pressure), 2,142 s, exit 1. Evidence: `step5/actions-select-run.txt` (the `chunked`, `chunks:` and `SHARD` lines) and `step5/actions-select-run.log.gz`.

- The chunks spread over all 5 shards. Each shard checked its own chunks against its own listing ("each of its N tests ran in exactly one chunk"). Each left its partial files to the static graph ("3 with only some of their chunks here").
- **Per-node outcomes** (summed over shards) equal step 1's: acts_vocab 322 + 321 = 643, rd6b 4 + 8 + 4 = 16, english 20 + 20 + 19 + 18 = 77, trust 127 + 126 + 252 = 505, speech 4 × 2384 = 9536. All passed, 0 skipped, 0 failed.
- **The only failure** was `tests/test_nested_pytest.py::test_every_pytest_command_is_built_by_the_builder`, caused by my `seeded_bugs.py` building a pytest command by hand. Fixed in 8c9b39058 to use `nested_pytest`. Rerun alone with `mac-pytest.sh -- <id>`: 1 passed (exit 0).

| file | runner seconds whole (task table) | longest chunk on its runner s | cut |
|---|---|---|---|
| test_acts_vocab_mutants (k=2) | 1,383 | 788 | 43% |
| test_readings_rd6b_differential (k=4) | 1,219 | 491 | 60% |
| test_english_evidence (k=4) | 1,002 | 570 | 43% |
| test_trust_mutants (k=4) | 980 | 648 | 34% |
| test_speech_polar_lean (k=4) | 934 | 643 | 31% |

On 4-vCPU runners the chunks shared each runner with 3 other units. Their summed seconds are 1.1x (acts_vocab) to 2.2x (trust_mutants) the whole file's: chunking spends runner seconds, and Actions ran at 23% of its free capacity that day.

### Projected Actions selected-run wall median

Today's median is 2,631 s: lake build 483 s, plus a slowest shard of median 2,048 s, which runs about 1.05-1.5x the longest unit.

After this run, gha-tests/unit-seconds.json lists the longest whole units as:
- trust 1,373, english 1,370, acts_vocab 1,200, rd6b 1,038 (all now chunked);
- enum_domains 1,006, difffuzz 976 and wire_gate_corpus 844 (not measured, so not chunked);
- lean_conformance 820 (never: one test).

The longest chunk is 788. The floor therefore falls from ~1,373 s to ~1,006 s (enum_domains), and the planner's shard count n = total/(2 × longest) rises 1.36x.

**Projection:** a slowest shard of ~1.25 × 1,006 ≈ 1,260 s gives a selected-run wall median of about 2,631 − (2,048 − 1,260) ≈ **1,850 s (−30%)**, once select-plan.py places the chunks (lines below) and runners are free.

**Measured so far:** 2,142 s in this one run. It was a full selection, with the chunks weighted at the planner's default median because select-plan does not read `chunk_seconds` yet, and 5 shards.

**Going further:** rows for enum_domains, difffuzz and wire_gate_corpus (`measure.sh` + `chunk_table.py --data`) would lower the floor further.

## Orchestrator lines (for the DRI; I did not edit /home/seyran/code/manage-agents)

`gha/select-plan.py`:

1. Pass the option. After `out, maxsh, args = ...` add:
   `if "--run" in args and not {"--full", "--no-record", "--impacted"} & set(args) and not any(a.startswith("--tier") for a in args): args = [*args, "--chunk-heavy"]`
2. Weigh a chunk entry by its expected seconds. After the line `w = {u: (rs[u] if u in rs else (w.get(u) or 0) * ratio) for u in units}` add:
   `cs = plan.get("chunk_seconds") or {}; w.update({u: cs[u] * ratio for u in units if u in cs and u not in rs})`
   - `chunk_seconds` are map seconds, scaled like the other map seconds. A label already in `rs` keeps its runner seconds; gha-select.sh now records labels there, as this run did.
3. Nothing else: `keep` already carries `"selected"` (the labels), and shard-select.py hands them to `select_tests.run()`, which runs each through the hook.

**Query** for chunked units in a selected run's log (each shard prints a `chunks:` line, then one `chunked <file>: i of k chunks, exit, seconds, outcomes; check` line per file):
`grep -E '^(chunks:|chunked )' <log>`

## Seeded bugs (Python; the only language changed)

`uv run python docs/infra/eff-20261030-1/seeded_bugs.py --json docs/infra/eff-20261030-1/seeded-bugs.json` plants each bug, runs the one test, restores the file byte for byte, and exits 0 only if every bug is caught. Result: 16 of 16 caught (the last 4 added for review F1), as recorded in `seeded-bugs.json` (file and test keys).

| bug | file | failing test (tests/test_test_chunks.py::) |
|---|---|---|
| the chunk rule drops the last node | tools/test_chunks.py | test_the_parts_cover_every_node_exactly_once |
| the union check is skipped | tools/select_tests.py | test_a_test_missing_from_every_chunk_fails_the_unit |
| a failed chunk is ignored | tools/select_tests.py | test_a_failed_chunk_fails_the_unit |
| the map keeps only chunk 1's edges | tools/select_tests.py | test_the_map_entry_of_a_chunked_file_is_the_union_of_its_chunks |
| chunking is applied to a full run | tools/select_tests.py | test_a_full_run_never_chunks |
| a setup-dominated file is chunked | tools/select_tests.py | test_a_setup_dominated_file_is_never_chunked |
| the plan lists chunks without --chunk-heavy | tools/select_tests.py | test_the_plan_lists_chunks_only_with_the_option |
| a chunk's failures do not count towards --maxfail | tools/select_tests.py | test_maxfail_stops_across_chunks_as_across_units |
| the conftest does not register the hook | tests/conftest.py | test_the_suites_conftest_applies_the_chunk |
| a nested run inherits the chunk | tools/nested_pytest.py | test_a_nested_run_never_inherits_the_chunk |
| the hook keeps the chunk before -m deselects | tools/test_chunks.py | test_the_chunk_applies_after_marker_deselection |
| JUnit node IDs drop the class | tools/run_order.py | test_junit_cases_are_the_node_ids_of_the_file |
| the log path moves before the node ids (F1) | tools/select_tests.py | test_a_failed_unit_line_ends_in_its_log |
| the stopped note leaves the exit field (F1) | tools/select_tests.py | test_a_stopped_chunked_unit_line_keeps_the_format |
| only the first chunk's log tail is printed (F1) | tools/select_tests.py | test_a_chunked_unit_line_names_its_first_chunk_log_and_prints_every_tail |
| a quarantined unit is labelled FAILED (F1) | tools/select_tests.py | test_a_quarantined_unit_line_is_no_failure_to_the_parsers |

## Review fix F1: the failed-unit line

The review of 28e25046c found that the line printed for each failed unit no longer ended in `; log <path>` (the log went on the next line), and that a stopped chunked file got `FAILED <file> (stopped before its other chunks ended) (exit stopped): ...`. The orchestrator's parsers (`chain-gate.sh`, `review-ready.py`: `^FAILED \S+ \(exit [^)]*\): (.*); log \S+$`; `mac-pytest.sh`: `^FAILED [^ ]+ \(exit [^)]*\): `) then read no node IDs. The fix is one formatter, `select_tests.unit_line`, that prints every such line as `<label> <unit> (exit <exit>): <node id>, ...; log <first log>`. The stopped note is now the exit (`select_tests.STOPPED_EXIT`), so it never lands among the node IDs. The tail of every chunk's log follows the line. The tests in `tests/test_test_chunks.py` (section "the failed-unit line") run all three parsers on a plain failure, a chunked failure, a stopped chunked file and a quarantined unit, and a property test round-trips `unit_line` through the parsers. The review's probe fails (rc=1) on 28e25046c and passes (rc=0) after the fix.

## DELTA, trust, constraints

- **No user-visible delta.** Only test execution of selected runs changed: no verdict, diagnostic, CLI output of `ve`, or schema changed. There is no DELTA.md, and no row reserves a DRI signature.
- **No Lean, Rust or product code changed. Trust +0.** No lake build or audit was needed, and none was run.
- **No test removed, renamed or skipped.** One test file was added (`tests/test_test_chunks.py`, 58 tests: 53, plus 5 for review F1). The selected run collected the same IDs plus those.
- **Generated files** were regenerated with `tools/regen_generated.py --write` (code map, tests/history-dependent.json), never edited by hand.
- **Hermetic tests:** tmp_path plus synthetic trees, waits only through `HANG_TIMEOUT`, no sleeps. `tests/test_hang_guards.py` passed: 69 passed.
- **Selection** (checklist item 9): a seeded change to `tools/test_chunks.py` selects `tests/test_test_chunks.py`. It selects all 504 units because the module sits in the conftest's import closure and the map (432763b06d) predates it, the same case as `tools/test_schedule.py`. Once a map records it, a change to `partition` selects only the units that ran it.

**Not run by me:** the full gate (the chain runs it on the final HEAD) and `tools/gate_collection.py --check --prebuilt` (it needs a Lean build in this worktree, and nothing in lean/ changed).

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer is added or changed.
2. PASS: task items 1-4 and steps 1 and 5 are mapped to commits and tests in the tables above. The only deviation is the stricter "measured rows only", with its reason. No new report test (D4); the evidence is saved files.
3. PASS: 16 seeded bugs, each caught by a named test (`seeded-bugs.json`), and 3 or more per claimed behaviour.
4. N.A.: no Python/Lean/Rust checker path changed. Outcomes of the same tests are identical whole vs chunked: `step5/mac-table.json` `identical_outcomes` is true for all 5 files, and on Actions the counts are in `step5/actions-select-run.txt`.
5. N.A.: no Lean answer is read. The analogous binding (every collected node in exactly one chunk) is tested both ways: `test_chunks_that_run_their_parts_pass_the_check`, `test_a_test_no_chunk_ran_fails_the_check`, `test_a_test_two_chunks_ran_fails_the_check`, `test_a_missing_report_a_failed_listing_or_an_extra_test_fails_the_check`.
6. PASS for the evidence: the selected run is on the final code but for the docs-only fix 8c9b39058, whose failed test was rerun alone (passed). The gate runs on the final HEAD in the chain.
7. PASS: no unsigned item. There is no DELTA and trust is +0. Exit statuses on error paths: `test_a_failed_chunk_or_a_problem_fails_the_folded_unit` (timeout, failure, problem and all-empty).
8. PASS: no user-visible output of `ve` changed. The selector's output gains only the `chunks:` and `chunked` lines when files are chunked. The plan JSON is unchanged without `--chunk-heavy`: `test_the_plan_lists_chunks_only_with_the_option[option0]`.
9. PASS: the seeded change to `tools/test_chunks.py` selects `tests/test_test_chunks.py` (probe command in the section above).
10. N.A.: no Lean statement or proof.
11. PASS: no new deadline. Waits use `HANG_TIMEOUT` (tests) and `test_map.UNIT_TIMEOUT` (the listing), with no sleeps: `tests/test_hang_guards.py` passed.
12. PASS: CPU and memory are measured in step 5 (chunk sums −23% to +34% on the Mac, up to 2.2x runner seconds on Actions; peak RSS per chunk ≤ whole). With chunking off (`--full`, the gate, or no measured row) nothing changes: `test_a_full_run_never_chunks`.
13. N.A.: no test removed or renamed.
14. PASS:
    - Both directions for every check (pass and fail cases above; `test_unset_or_one_chunk_runs_every_test` and `test_a_bad_setting_is_a_usage_error`).
    - Every number in this report names its command and file.
    - Spec re-read against the task text: "Unset = today's behaviour, byte for byte" (`register` returns before anything when unset); "deselecting the rest with pytest's own deselect report" (`test_each_chunk_runs_its_part_and_together_they_run_every_test` asserts "N deselected"); "--jobs width is unchanged" (chunks are entries of the same `record_units` pool; the listing runs before the pool starts); "without the option the plan output is unchanged byte for byte" (`test_the_plan_lists_chunks_only_with_the_option[option0]`).
