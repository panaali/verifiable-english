# Test architecture batch 1: tiers and R1

DRI signature needed: none. This is the repository half of the requested batch 1 plan;
the DRI owns the orchestrator prompt changes after merge. The [delta](DELTA.md)
records no VE user-visible change.

## Scope and acceptance

| Plan §5 item | Owner | Delivered | Evidence |
|---|---|---|---|
| 1. Generated `tests/heavy.json` from a duration report, `--check`, seed from run A | AGENT | `0211be322`, `4887896a7`, `204cb0314`: `tools/heavy_tests.py`, complete 15,179-ID run A report, 171 heavy IDs, generated inventory registered in `tools/regen_generated.py` and its documented table; spaced node IDs preserved | `tests/test_heavy_tests.py::test_heavy_inventory_is_generated_from_complete_measurement`, `test_pytest_duration_report_includes_setup_call_and_teardown`, `tests/test_merge_tooling_evidence.py::test_the_generated_file_table_names_every_entry`; `python3 tools/heavy_tests.py --check`; `python3 tools/regen_generated.py --check --only gitattributes --only heavy-tests` |
| 2. Collection mark and pytest marker; leave `addopts` alone | AGENT | `0211be322`, `81a85f530`: `tests/conftest.py`, `pyproject.toml`; unlisted manual marks fail closed | `tests/test_heavy_tests.py::test_every_measured_node_is_exactly_light_or_heavy`, `test_an_unlisted_manual_heavy_mark_is_refused`; plain pytest addopts diff |
| 3. `--tier light`: all light tests plus selected heavy tests, print counts, run via Mac | AGENT | `0211be322`, `6246007c0`, review fix F2: `tools/select_tests.py`; two pytest processes use the runner's worker count; the heavy stage names selected files with `-m heavy`, never saved node IDs, and is skipped when it selects nothing | `tests/test_heavy_tests.py::test_light_tier_runs_every_light_node_and_selected_heavy_function`, `test_no_light_tier_command_names_a_saved_node_id`, `test_a_renamed_heavy_test_does_not_break_the_heavy_stage`, `test_a_heavy_stage_that_selects_nothing_is_skipped`; Mac selected run below |
| 4. Exact split, selected changed heavy function, seeded bugs; no timing-threshold test (DRI note, plan §3.5) | AGENT | `0211be322`, `6246007c0`, `b4ed439da`, `81a85f530`, `4887896a7`, review fix F1: `tests/test_heavy_tests.py`, `tests/test_select_tests.py`; the 20 s budget and its seeded 30 s test are removed; `--check --report <nightly>` lists drift and exits 0; seeded bugs below | `tests/test_heavy_tests.py::test_no_test_fails_because_a_test_became_slow`, `test_check_refuses_an_inventory_stale_against_the_committed_report`; seeded bugs below |
| 5. Fixloop/build checklist use R1 after merge; branch verify stays full | HUMAN (DRI) | Deferred to DRI after merge, as the task assigns | Orchestrator side is outside this worktree |
| Row 1 shadow on 10 fix rounds | HUMAN (DRI) | Deferred to the DRI's orchestrator rollout after merge | Compare R1 failures with the full branch verify; heavy tests still run in the full verify |
| Final full release gate on committed HEAD | EXTERNAL (chain) | Scheduled by the chain after this builder finishes, per the task override | `gate-result.json` on this branch |

The nightly full live no-reuse run, branch verify, default pytest options, and every
existing test remain in place. `--tier light` is opt-in. No test fails because a test
became slow: `python3 tools/heavy_tests.py --check --report /path/to/pytest-durations.txt`
lists the rows a nightly measurement would add or drop and exits 0, and the DRI can
update both committed duration input and generated inventory with
`python3 tools/heavy_tests.py --write --report /path/to/pytest-durations.txt`.

## Measurement

Baseline from the plan's Mac run A on main `9f40783b8`: 1,648.1 s wall with six
workers for the full default suite, 15,179 collected, 171 heavy. The 15,008 light
tests account for 2,410 s of aggregate test time without the future answer store.
The first post-change Mac light stage took **995.62 s** with six workers, 39.6%
less test wall time than the run A full suite. That is a light-only comparison;
this batch's infrastructure files select all 171 heavy tests, so its complete
R1 run will take longer. The first selected run reported 375/375 units selected,
15,008 measured light tests and 171/171 heavy selected. First-checkout setup
(Lean build and pins) took 506 s, separately from pytest. The Mac wrapper took
1,996 s including queue, setup and selected checks. Its light process reported
14,922 passed, 9 skipped, 83 xfailed and one failure in 995.62 s. The failure,
`tests/test_merge_tooling_evidence.py::test_the_generated_file_table_names_every_entry`,
was this batch's missing documentation row, not a pre-existing main failure.
`204cb0314` adds the row; that test passed locally. Because `run()` stops on a
failing command, the first run did not execute the heavy stage.

The second Mac selected run after the fix **passed (exit 0)**. The same 375/375
units were selected; checkout setup took 1 s. The light tier reported **14,923
passed, 9 skipped, 83 xfailed in 718.70 s**. All **171 selected heavy tests
passed in 1,834.68 s**. Together the pytest stages took 2,553.38 s; the Mac
wrapper took 2,709 s including checks and queue. The two stages covered
15,186 current default tests exactly: 15,015 light
outcomes plus 171 heavy outcomes. The seven tests added since run A are light.
Against run A's 1,648.1 s, the light stage alone is 56.4% shorter, while this batch's all-heavy pytest
work is 55.0% longer. This branch changes global test setup, so ordinary
selection deliberately picks every heavy node. Mac load and run A's measurement
plugin also differ, so these are observed wall times rather than a controlled
estimate of future fix-round speed. The answer store in batch 3 is not yet
present.

The implementation commit list, paths and baseline counts are saved in
[scope.json](evidence/scope.json); the chain gate checks the final `main..HEAD`
range under R11/D4, without a permanent live-git report test.
Mac timing and test counts are saved in [mac-runs.json](evidence/mac-runs.json).
The text duration parser round-tripped all 15,179 saved IDs, including 1,779
with spaces, through a synthetic `--durations=0` report.

## Tests and seeded bugs

Focused restored run: `XDG_CACHE_HOME=/tmp/ve-tarch-xdg ./.venv/bin/python -m pytest
--noconftest -q tests/test_heavy_tests.py
tests/test_select_tests.py::test_light_tier_keeps_the_heavy_test_of_a_changed_function`:
**7 passed**. `--noconftest` skips the
repository's native build hook for these pure unit tests; the Mac selected run uses
the normal hook and all default plugins. Generated-file checks and `git diff --check`
passed. The full release gate is left to the chain on the final committed HEAD, as
the task explicitly overrides build checklist item 22.

The final focused run used the normal collection hook:
`XDG_CACHE_HOME=/tmp/ve-tarch-xdg VE_NATIVE_PREBUILT=1 ./.venv/bin/python -m pytest -q tests/test_heavy_tests.py tests/test_select_tests.py::test_light_tier_keeps_the_heavy_test_of_a_changed_function tests/test_merge_tooling_evidence.py::test_the_generated_file_table_names_every_entry`:
**8 passed**. These focused tests do not call a checker.

Temporary bugs, each restored before the focused run and never committed. The same list,
with file and test keys, is in `evidence/mutants.json`; one bug in each of the three files
was planted again together at `601100d35`: four tests failed, and after the restore 7 passed.

| Changed product file | Seeded bug | Test that failed |
|---|---|---|
| `tools/heavy_tests.py` | Raise the heavy threshold from 10 to 1,000 s | `test_heavy_inventory_is_generated_from_complete_measurement` (exit 1) |
| `tools/heavy_tests.py` | Ignore setup and teardown duration rows | `test_pytest_duration_report_includes_setup_call_and_teardown` (exit 1) |
| `tools/heavy_tests.py` | Truncate node IDs at a space in pytest's duration text | `test_pytest_duration_report_includes_setup_call_and_teardown` (exit 1) |
| `tests/conftest.py` | Skip every heavy mark | `test_every_measured_node_is_exactly_light_or_heavy` (exit 1) |
| `tests/conftest.py` | Allow a manual heavy mark absent from the inventory | `test_an_unlisted_manual_heavy_mark_is_refused` (exit 1) |
| `tools/select_tests.py` | Select no heavy IDs | `test_light_tier_runs_every_light_node_and_selected_heavy_function` and `test_light_tier_keeps_the_heavy_test_of_a_changed_function` (exit 1 each) |

## Review fix round (tarch-b1 review)

| Finding | Fix | Regression test |
|---|---|---|
| F1 (B) timing-threshold test | `BUDGET`, `check_budget` and the seeded 30 s test removed; `--check` fails only on an inventory stale against the committed report; `--check --report <nightly>` prints `enters heavy` / `leaves heavy` / `absent from` rows and exits 0. The `heavy_tests.py` docstring and `docs/TESTING.md` say the same. | `tests/test_heavy_tests.py::test_no_test_fails_because_a_test_became_slow` (holds the review's probe), `test_check_refuses_an_inventory_stale_against_the_committed_report` |
| F2 (B) saved node IDs on the pytest command line | The heavy stage passes the selected files that hold inventory rows with `-m "... and heavy"`; the collection hook marks what is still collected, so a renamed or split heavy test runs in the light stage. `run` accepts exit 5 only from the commands a plan lists in `may_select_none`. | `test_no_light_tier_command_names_a_saved_node_id`, `test_a_renamed_heavy_test_does_not_break_the_heavy_stage` (the review's probe, collecting for real), `test_a_heavy_stage_that_selects_nothing_is_skipped` |
| F3 (C) hard-coded run A counts | The inventory tests derive counts from the committed report; `docs/TESTING.md` asks for `--durations-min=0` so a nightly text report lists every test. | `test_heavy_inventory_is_generated_from_complete_measurement`, `test_every_measured_node_is_exactly_light_or_heavy` |
| F4 (C) `docs/TESTING.md` | The fast-path command and heading are main's again; the light tier has its own section with a repository-relative command and says it runs every light test; `--base` is documented as committed changes only. | documentation |
| F5 (C) all-heavy wall time | Not changed: a measurement, recorded above; the follow-up is the DRI's. | none |

Seeded bugs for the fix round, each planted, observed failing and restored (also in
`evidence/mutants.json`):

| Changed product file | Seeded bug | Test that failed |
|---|---|---|
| `tools/select_tests.py` | Heavy stage names saved node IDs again | `test_no_light_tier_command_names_a_saved_node_id`, `test_a_renamed_heavy_test_does_not_break_the_heavy_stage`, `test_light_tier_runs_every_light_node_and_selected_heavy_function` |
| `tools/select_tests.py` | Exit 5 of an empty heavy stage not accepted | `test_a_heavy_stage_that_selects_nothing_is_skipped` |
| `tools/heavy_tests.py` | Drift against a nightly report fails the check | `test_no_test_fails_because_a_test_became_slow` |
| `tools/heavy_tests.py` | Drift omits tests entering the heavy list | `test_no_test_fails_because_a_test_became_slow` |
| `tools/heavy_tests.py` | `--check` passes a stale inventory | `test_check_refuses_an_inventory_stale_against_the_committed_report` |

## Build checklist disposition

Items 1–19 concern checker semantics, relays, parsers, deadlines, English, proofs,
and use cases; this batch changes none of those surfaces. Item 13 is satisfied by
the three seeded failures above. Item 14: focused tests write under `tmp_path` and
no test sleeps or asserts on elapsed time. Item 16: the generated inventory is
registered with `regen_generated.py`. Item 20: counts come from the saved run A
duration report; no permanent live-git report test was added (R11/D4). Item 21:
acceptance ownership is in the table above. Item 22: the selected Mac run is
recorded below; the chain owns the final full gate under the task override. Item
23: the delta is recorded above; no standing ruling applies to a VE output because
there is no such change.

## Self-review against BUILDER-CHECKLIST

1. N.A. — no Lean or Rust answer or request decoder changed.
2. PASS — plan §5 acceptance table above and `tests/test_heavy_tests.py`.
3. PASS — seven seeded failures listed above, each a test assertion failure.
4. N.A. — no Python, Lean, or Rust semantic output changed.
5. N.A. — no relayed answer field changed.
6. N.A. — final full gate belongs to the chain by explicit task instruction.
7. PASS — `DELTA.md` records no VE output change; `git diff main...HEAD` review.
8. PASS — `DELTA.md` and `git diff main...HEAD` show only test tooling and docs.
9. PASS — `test_light_tier_keeps_the_heavy_test_of_a_changed_function`; the Mac selector reported 375/375 units because this batch changes global collection and `.gitattributes`, which correctly select all units until the rank 4 selection changes land.
10. N.A. — no Lean theorem or shape changed.
11. N.A. — no public operation budget or deadline changed.
12. N.A. — no product CPU or memory path changed; test wall timing is recorded above.
