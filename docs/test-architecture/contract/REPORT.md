# tarch-contract: the x86 platform contract suite (test-architecture plan rank 2, repository half)

Branch `infra/tarch-contract`, based on main `dae12d5ff` (merge base). Plan: reviews/test-architecture-2026-10-14.md
draft 2, section 3.3. Astra's re-check (ADOPT WITH CHANGES) point 4 overrides the draft where they differ.

**DRI signature needed: none.** No VE output changes (DELTA.md). **DRI decision requested:** the measured cost of
the contract suite is 19.0 min end to end on the loaded VM, against a 5–10 min target. The breakdown and the
options are in "Cost" below. Nothing in this batch narrows the full x86 gate.

## What the batch delivers

| Plan row / directive | Delivered by | Test or evidence |
|---|---|---|
| Contract list by cause, generated: pins and reproducible builds; process supervision, injected deadlines, signals, file locks, resource limits; cross-implementation agreement on recorded fixtures | `tools/platform_contract.py contract --write` → `tests/platform-contract.json` | `test_the_contract_list_is_generated_from_the_tree`, `test_each_cause_lists_its_tests`, `test_generation_lists_each_cause_and_leaves_nightly_reruns_to_the_full_gates` |
| A `--check` that regenerates it | `contract --check`, also run by `tools/regen_generated.py --check` (entry `platform-contract`) | `test_contract_check_fails_on_a_stale_list` |
| The divergence list: every test whose outcome differed between the Mac and the x86 VM on the same tree in the last 30 days, each with its cause from plan 2.8, from the run records | `divergences --records … --mac-known … --write` → `tests/platform-divergences.json` (25 rows); causes in `DIVERGENCE_CAUSES` | `test_a_planted_divergence_in_a_fake_run_record_appears_in_the_regenerated_list` (the seeded case), `test_a_divergence_needs_both_runners_suites_on_the_same_tree_in_the_window`, `test_summaries_pair_by_commit_and_never_repeat_a_gate_record`, `test_mac_known_failures_and_the_plans_divergences_are_in_the_list` |
| A command that runs exactly the contract suite with gate.py's options on a given checkout | `platform_contract.py run --checkout DIR` → that checkout's `tools/gate.py --contract` | `test_the_contract_run_runs_exactly_the_listed_tests_with_the_gates_stages`, `test_a_contract_run_is_never_a_full_gates_evidence`, `test_a_listed_test_that_collects_nothing_fails_the_contract_run`, `test_run_starts_the_checkouts_own_gate_in_contract_mode` |
| Run it once on the VM against main and record its real cost | Two runs plus one seeded run (below) | `evidence/contract-runs.json` |
| A tool that, given an x86 gate FAIL record, says which failed tests are NOT in the list | `platform_contract.py misses RECORD [--mac RECORD]` (exit 1 on a miss) | `test_misses_names_the_x86_failures_outside_the_list`, `test_misses_refuses_a_mac_record_and_judges_other_failures_by_the_contract_runs_stages`, `test_misses_exit_status_and_output`; run on every failed x86 record of the window: `evidence/misses-real-x86-failures.txt` |
| Seeded: an assertion on the pinned x86 digest is in the list and fails the contract run | `test_rust_reproducible.py` is in `pins`; a wrong x86 pin fails the contract run | `test_the_pinned_x86_digest_assertion_is_in_the_contract_for_its_pin`; live seeded run (below) |
| Seeded: a planted Mac/x86 divergence in a fake run record appears in the regenerated divergence list | fake `*.mac.json`/`*.x86.json` records | `test_a_planted_divergence_in_a_fake_run_record_appears_in_the_regenerated_list` |
| docs/TESTING.md's section on it | "The x86 platform contract suite" | prose; `test_merge_tooling_evidence` checks the generated-file table |
| The DRI policy: the full x86 gate still runs for native and runtime diffs; this batch does not narrow it | Nothing in the merge-train path rule or `tools/gate.py`'s full mode changes | `test_a_contract_run_is_never_a_full_gates_evidence` (a full gate on the same scratch tree still runs `tests` and the audit); `tests/test_gate_rerun.py`, `tests/test_gate_integrity.py` unchanged and passing |
| Orchestrator half (merge-train VM leg on every merge; `misses` on every full x86 failure) | not in this repository | the orchestrator wires it in (task directive) |

## The contract list

`tests/platform-contract.json`: 54 entries, which reduce to 51 pytest selectors because a function inside a
listed file runs once. Entries by cause: agreement 18, process 15, divergence 22, pins 2. Some entries have two
causes. Measured on the Mac (`tests/heavy-durations.json`, `platform_contract.py estimate`), the list covers
1,093 tests and 1,317 s of test time, 15.7% of the default suite.

- **pins**: `test_rust_reproducible.py` (which holds `test_release_binary_is_pinned`, the assertion on the pinned
  x86 digest) and `test_gate_integrity.py` (the gate refuses an unpinned build and poisoned toolchains).
- **process**: the plan's list (service client, handles, hang guards, Stage-2 faults, route transport, native
  build lock, assist deadline), `test_cpu_bounds.py`, and the deadline tests of the store inventory (row 8:
  soft request economy, question reading, the two W6a limit-generator tests). It also takes every test file
  that imports `signal`, `resource` or `fcntl`. The import is read with Python's parser, not a regex.
- **agreement**: `tools/gate.py`'s `REQUIRED_FAMILIES`, read from the gate (one owner), every
  `test_*three_way*.py`, and the difffuzz CI sample `test_ci_run`.
- **divergence**: each divergent test, named by its function, so every parameter of it runs. Different
  parameters of `test_english_mixed_merge_smoke` failed on different runs (news-article-0, -1, reviewed-3,
  constitution-reviewed-0), so one parameter would not be enough.
- **left out**: `test_rights_three_way.py::test_rights_differential_on_one_thousand_generated_documents`
  (`nightly`, 254 s in G-suite). R2, the full x86 gate and R3 run it; its 100-document sibling is in the list.

## The divergence list

`tests/platform-divergences.json` covers 2026-09-16 to 2026-10-16.

- **Records read**: 103 runs whose suite ran, inside the window; 37 of them paired with the other runner on the
  same tree. The sources were `integ-runs/`, `nightly-runs/`, `nightly-vm-runs/`, `cand-runs/` (gate JSONs and
  `.md` summaries) and `mac-known-failures.txt`. No `*-x86-verify.final.md` exists in manage-agents today; the
  reader accepts them, and one that names no commit cannot be paired.
- **25 rows by cause**: environment 17, elapsed time 3, unknown 3, repository state 1, pinned artefact 1.
- **Rows from gate records** (14 observations):
  - 8 CPU-deadline `CheckerUnavailable` failures on x86 (environment, fixed by fix-x86-cpu-deadline, 2a4fbf70);
  - `test_difffuzz.py::test_ci_run`, a time-out (elapsed time, quarantined).
- **Rows from plan 2.8**: the sub-tick deadline tests, rd8, `test_agent_policy_rerun` and the ts-B1 relay-gate
  tests. They come from pipeline logs that no gate record keeps, so they are in `PLAN_OBSERVATIONS` with their
  days and age out after 30 days.
- **Rows from `mac-known-failures.txt`**: `test_release_binary_is_pinned` (pinned artefact).
- **The plan's clang SIGBUS** was a build failure, not a test outcome, so it has no row.
- **Classification**: every observed row has a cause from the plan; none is `unclassified`.
- **Regeneration**: `divergences --check` regenerates the list from the same records with its saved window, and
  it matches. The orchestrator owns the records, so the check runs where they are (merge train or nightly), not
  in the suite. The suite checks the saved list's shape and that every row is in the contract.

## The contract run on the VM against main (real cost)

The runs are on tree `5037d327`: main `dae12d5ff` plus this branch. The branch changes no product code. The
runner is the VM: x86_64, 32 CPUs, `--workers 8`, as the x86 legs use. Two full x86 candidate gates ran
beside it. The full records are trimmed into `evidence/contract-runs.json`.

| Run | Setup (toolchains, uv sync, Lean build, wire check, trust counts, Rust build, cargo test, collection) | Suite stage | End to end | Load (1 min) | Result |
|---|---|---|---|---|---|
| 1: fresh scratch checkout, `.lake` copied from ve-integration | 39.7 min: the copied `.lake` was stale and lake rebuilt 458 modules, then 1 min of Rust | 22.0 min (pytest 1,338 s) | 61.8 min | 94 → 72 | failed: 8 (see the first finding below) |
| **2: same checkout, `.venv` made by `uv sync` before the run, Lean current** | **about 1.3 min** | **17.7 min (pytest 1,064.7 s)** | **19.0 min** | 66 → 63 | **contract-passed**: 1,097 passed, 5 skipped, 36 native Rust tests |
| Seeded: wrong x86 Rust pin in `lean/checkers.lock` | 0.8 min | not reached | 0.8 min | ~63 | **failed**: "Rust build … is not pinned in lean/checkers.lock" |

**Seeded pin bug.**
- On a throwaway commit, the x86 digest `3ec83dee…` was replaced in `lean/checkers.lock`. The contract run
  failed at the gate's pin check, before the suite.
- The listed assertion run alone on the same seed, `tests/test_rust_reproducible.py::test_release_binary_is_pinned`,
  also failed: `AssertionError: … (3ec83dee…) is not in lean/checkers.lock`.
- After the reset it passed.

## Cost

Run 2's 19.0 min is the real cost on today's VM at load 63–78. That is a fifth to a quarter of a full x86 gate
(69–106 min for the five complete R2 x86 legs of Oct 15–16 in `integ-runs/*.x86.md`), but above the plan's estimate of 5–10 min.

- **Where it goes.** Two divergence functions are 790 s of the list's 1,317 Mac seconds (60%):
  - `test_readings_rd6b_differential.py::test_generated_documents_agree_on_both_routes`, 10 chunks, 481 s;
  - `test_english_evidence.py::test_english_mixed_merge_smoke`, 310 s.
  - Their cause, kernel memory compaction charged as CPU, was fixed by fix-x86-cpu-deadline.
  - The next largest are `test_difffuzz.py::test_ci_run` (89 s on the Mac, up to 253 s on the VM) and
    `test_lean_conformance.py` (70 s, which includes the in-suite axiom audit).
- **Options for the DRI** (none implemented, because each trades coverage for time):
  1. Keep the function-level list. The two functions leave the 30-day window on 2026-11-14/15 unless they
     diverge again. Est. 7–9 min after that, at the same load.
  2. List those two at their observed parameter IDs only. Est. 654 Mac s, about 9 min on the VM. A failure in
     another parameter would then be a `misses` hit, which is the signal Astra asks for, but no longer a block.
  3. Run the contract leg at `--workers 16`. The VM has 32 CPUs, but its load is the limit today.

## Before and after on the Mac

The contract suite runs on the VM and changes nothing that the Mac runs, except that the suite gains
`tests/test_platform_contract.py`: 40 tests. On ve-mac-1 (`mac-pytest.sh`, 6 workers), they ran with
`test_gate_rerun.py`, `test_merge_tooling_evidence.py` and `test_nested_pytest.py`: 88 passed in 12.6 s. The
slowest new test is `test_contract_check_fails_on_a_stale_list` (5.6 s, three regenerations). The Mac R2 gate's
stages and collection are otherwise unchanged. `contract --check` takes about 2 s.

## Findings outside this batch's files (follow-ups, not fixed here)

1. **The gate's Python is not pinned.**
   - In a checkout without a `.venv`, `tools/gate.py`'s `uv sync` makes one on the system Python 3.12.3, not on
     `.python-version`'s 3.14. The gate gives uv a scratch `XDG_DATA_HOME`, where uv's managed 3.14 is not
     visible.
   - The gate records `toolchains.python` but does not compare it with `.python-version`. The runners' x86
     gates recorded 3.14.7 only because their `.venv` already existed.
   - On 3.12, the 8 `test_relay_mutation_gate.py` tests fail with `RecursionError` while decoding the deep case
     of `tests/data/relay-gate-cases.jsonl`.
   - Owner: the gate (`check_python_project`).
2. **Selection is FULL for this branch.** It edits `.gitattributes` (regenerated for the two new entries) and
   `.gitignore`, which `tools/select_tests.py` counts as whole-suite roots (plan 2.3 cause C, owned by
   tarch-select). `--impacted` selection is precise: `tools/platform_contract.py` reaches 25 test files and
   `tools/gate.py` 51, both including `tests/test_platform_contract.py`.

## R2, R3 and no weakened check

- **Additive only.** No merge and no nightly depends on the contract list, a selection, a store, a cache or
  reuse. R2 (the full live `tools/gate.py` on the candidate) and R3 (`--no-quarantine`) are unchanged.
- **Status.** A contract record's status is `contract-passed` or `failed`, never `passed`
  (`test_a_contract_run_is_never_a_full_gates_evidence`, seeded G2). It writes no collection record for the
  commit (`test_the_contract_run_runs_exactly_the_listed_tests_with_the_gates_stages`).
- **Default record.** Its default record is not `gate-result.json`
  (`test_the_contract_runs_default_record_is_not_the_full_gates`, seeded G4).
- **No timing threshold.** Durations appear only in `estimate` and this report. No test asserts a duration.

## Seeded bugs (Python, the only language changed)

Ran with `tools/mutants.py docs/test-architecture/contract/mutants.json`: 12/12 killed. The results are in
`mutants-evidence.json`, and each file was restored byte for byte.

| ID | File | Behaviour | Failing test |
|---|---|---|---|
| C1 | tools/platform_contract.py | the pins cause lists the pinned x86 digest assertion | test_the_contract_list_is_generated_from_the_tree (and test_the_pinned_x86_digest_assertion_is_in_the_contract_for_its_pin) |
| C2 | tools/platform_contract.py | a test that failed on one runner and passed on the other is a divergence | test_a_planted_divergence_in_a_fake_run_record_appears_in_the_regenerated_list |
| C3 | tools/platform_contract.py | only runs of the same tree are compared | test_a_divergence_needs_both_runners_suites_on_the_same_tree_in_the_window |
| C4 | tools/platform_contract.py | the 30-day window | test_a_divergence_needs_both_runners_suites_on_the_same_tree_in_the_window |
| C5 | tools/platform_contract.py | a selector covers only its own file, class or function | test_the_run_selectors_run_each_listed_test_once |
| C6 | tools/platform_contract.py | `misses` reports an uncovered x86 failure (exit 1) | test_misses_names_the_x86_failures_outside_the_list, test_misses_exit_status_and_output |
| C7 | tools/platform_contract.py | a nightly rerun in a listed file is left out and named | test_generation_lists_each_cause_and_leaves_nightly_reruns_to_the_full_gates |
| C8 | tools/platform_contract.py | an OS-primitive import puts a file in `process` | test_only_imports_of_the_operating_systems_primitives_put_a_file_in_process |
| G1 | tools/gate.py | the contract run runs exactly the listed tests | test_the_contract_run_runs_exactly_the_listed_tests_with_the_gates_stages |
| G2 | tools/gate.py | a contract run is never `passed` | test_a_contract_run_is_never_a_full_gates_evidence |
| G3 | tools/gate.py | a listed test that collects nothing fails the run | test_a_listed_test_that_collects_nothing_fails_the_contract_run |
| G4 | tools/gate.py | the contract record is not gate-result.json | test_the_contract_runs_default_record_is_not_the_full_gates |
| live | lean/checkers.lock (throwaway commit) | a wrong x86 pin fails the contract run | the contract run on the VM (status failed at the pin check); test_release_binary_is_pinned alone |

## Known red and what was not run

- **Known red.** The tests in main-known-red.txt were not touched. Two of them are in the divergence list as
  observations (the sub-tick deadline tests and rd8), from plan 2.8; their test files are unchanged.
- **Full gate.** Not run here, as the task directs: the chain runs `tools/gate.py` on the final HEAD.
- **Selected tests.** The Mac run of the first commit had two failures: the merge-tooling table and a pytest
  word in a fixture. Both were fixed in e9f8010ca, and their tests pass on the Mac.
- **Orchestrator wiring.** The merge-train VM leg and `misses` on every x86 failure are not in this repository.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: N.A. No relay or Lean answer is read; the batch reads gate records,
   and `misses` refuses a malformed or Mac record (`test_misses_refuses_a_mac_record_and_judges_other_failures_by_the_contract_runs_stages`).
2. Every deliverable built, no rule broken: PASS. See the table above. The two lists are generated, not written
   by hand (`test_the_contract_list_is_generated_from_the_tree`), and there is no new permanent report test
   (D4): the run evidence is saved, not re-checked.
3. Tests and gates can fail: PASS. 12 seeded mutants killed (`mutants-evidence.json`) and the live pin seed.
   The divergence comparator returns nothing on empty input and on matching outcomes
   (`test_a_divergence_needs_both_runners_suites_on_the_same_tree_in_the_window`).
4. Python, Lean and Rust agree: N.A. No checker semantics changed.
5. R8 binding: N.A. No relay. Record inputs are checked:
   - a contract selector that collects nothing fails the run
     (`test_a_listed_test_that_collects_nothing_fails_the_contract_run`);
   - a malformed list fails the run (`test_a_malformed_contract_list_fails_the_contract_run`,
     `test_a_malformed_contract_list_is_refused`).
6. Gate evidence matches the final HEAD: PASS. Synced with main `dae12d5ff` before the work. The chain runs the
   full gate on the final HEAD. The VM measurements name their tree (`evidence/contract-runs.json`).
7. No unsigned item: PASS. DELTA.md has zero pending rows (tooling only, no VE output).
8. Every user-visible change in DELTA: PASS. DELTA.md lists `--contract`, its status and record, and the new
   tool and lists. The full gate's behaviour is unchanged (`test_a_contract_run_is_never_a_full_gates_evidence`,
   tests/test_gate_rerun.py).
9. Test selection finds the tests: PASS with a note. `--impacted` on `tools/platform_contract.py` and
   `tools/gate.py` selects `tests/test_platform_contract.py`, whose tests kill every seeded mutant. The default
   selection is FULL because `.gitattributes` and `.gitignore` changed (cause C, tarch-select's item).
10. Lean statements: N.A. No Lean changed.
11. Budgets and deadlines fail closed: N.A. No budget code changed. The new tests use no sleep and no timeout
    (`tests/test_hang_guards.py` passes on the Mac selected run).
12. No CPU or memory regression: N.A. No product path changed. The new suite tests take 12.6 s together on the
    Mac.
13. Test-removed trailers: N.A. No test removed or renamed (only added).
