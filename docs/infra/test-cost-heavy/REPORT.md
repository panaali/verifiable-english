# test-cost-heavy: cut the cost of the heavy units selected in most runs

**Summary.**
- **Status:** built. Base 327bf922a; the commits are listed in section 7.
- **(2) Built and on.** `tools/select_tests.py --defer-heavy` leaves out a test file over 120 s that only weak reasons select (static graph, a listed directory, smoke). The chain gate runs those files. The `mac-pytest.sh` wiring and the DEFER_WEAK_HEAVY flag pass it to builder runs only.
- **Measured saving:** ~137 s of builder test-wait per non-full selected run (12% of the mean wall), ~14 wall-h and ~80 unit-h of CPU per 14 days.
- **(1) Measured, not built.** test_english_evidence is not setup-dominated: its time is Lean service round trips per document. The in-flight row eff-20261030-1 splits files like it by node ID. No setup cache was built.
- **Signatures and follow-ups:** none for the DRI. Follow-ups are in section 8.

## 1. The row and what delivers it

Row (backlog `test-cost-heavy`): "Cut the cost of the heavy units selected in most runs (reviews/nightly-tier-20261029.md table): (1) test_english_evidence 636 s median, 74% of runs, setup-dominated (~4 s of call time in full gates): cache/share its setup (with gha-heavy-split); (2) selection precision: when a heavy unit (> 120 s) is selected ONLY for weak reasons (static graph, listed directory, smoke), defer it to the chain gate instead of every builder run; measure saved builder test-wait".

| part | delivered by | test |
|---|---|---|
| (1) cache/share the setup | not built: measured, there is no setup to share (section 2). The lever is per-node splitting, eff-20261030-1 (in flight) and gha-heavy-split | evidence `english-evidence-durations.txt`, `english-evidence-gate-durations.json` |
| (2) defer heavy weak-only units | `tools/select_tests.py` `weak_reason`, `defer_heavy`, `map_seconds`, `--defer-heavy`, `run_recorded`'s `deferred` exit | `tests/test_select_defer.py` (17 tests) |
| (2) "to the chain gate instead of every builder run" | manage-agents: `defer-heavy.zsh`, `mac-pytest.sh` (appends the option), `chain-gate.sh` and `infra-item.sh` (their own runs set `MAC_PYTEST_NO_DEFER=1`), flag `DEFER_WEAK_HEAVY` + FLAGS.tsv row | `tools-local/test_defer_heavy.py` (12 tests) |
| (2) measure saved builder test-wait | manage-agents `tools-local/defer-heavy-measure.py`; saved output `measure-jobs6.json`, `measure-jobs8.json` | `tools-local/test_defer_heavy.py` `Measure` |

## 2. Part (1): test_english_evidence is Lean work, not setup

- **Serial run, as a selected unit runs it** (one process per file, `tools/test_map.py` `run_unit`). Command: `uv run pytest -q -p no:cacheprovider --durations=40 --durations-min=1 tests/test_english_evidence.py` on the VM at load ~20. Result: 77 passed in 1400 s (`english-evidence-durations.txt`). The 30 `test_english_mixed_merge_smoke` parts take ~1250 s of that, `test_english_differential_merge_smoke` 38.6 s, and collection 1.5-2.7 s (`--collect-only`).
- **The gate's own record says the same.** `mac-gate-cand-usecase-pf-run.json` (commit 327bf922a, `ve-test-durations@1`) records 43 nodes of this file: 927.4 s of call time in total, max 65.9 s per node (`english-evidence-gate-durations.json`). The "~4 s" in the nightly-tier table is classified.json's `full_med` (4.2), a per-node median, not the file's call time.
- **Where a part's time goes.** cProfile of `english_mixed.mixed(1, only={us-constitution-14th-s1})`: 15.0 s in total. Of that, 11.1 s is 1156 Lean service requests (`relay.decide`), 8.6 s of it waiting on the service's reply. Parts split the documents (`documents[part::parts]`) and share no rendering or parsing.
- **So there is no setup to cache.** Caching Lean answers across runs would break the hermetic-test rule (CLAUDE.md: "do not rely on caches"). In the full gate the 43 nodes already spread over xdist workers. The serial floor in selected runs is what eff-20261030-1 (chunk heavy files by node ID, in flight) and gha-heavy-split address. Part (2) cuts the rest: this file was selected for weak reasons only in 12 of the 63 valid replays (section 4, matching the nightly-tier `rep_weak` 12 of 48).

## 3. Part (2): the rule

`defer_heavy(plan, seconds, keep=..., threshold=120)`, in `tools/select_tests.py` (the one owner; the measurement imports it):

- **What it defers.** A `tests/` file is deferred when the map records it at over 120 s (`seconds > threshold`, the map's whole-process seconds, `map_seconds`) and every one of its reasons is weak (`weak_reason`). The weak reasons are those ending ` (static)`, those starting `lists the directory of ` and `smoke`. This is the nightly-tier definition, reviews/nightly-tier-20261029.md:90.
- **What always stays.** Nothing is deferred from a full plan. A changed test always stays, as do SMOKE, HISTORY_TEST and a unit that failed last time (`run_order.last_failed`, which includes the worktree's gate record, so a chain-gate failure comes back to the builder). So does a unit with no recorded seconds, and every non-`tests/` unit.
- **Commands.** Deferred files leave `selected` and the pytest command. A pytest command left with no file is dropped, because a bare `pytest -q` would run the whole suite.
- **The tree map.** `run_recorded` gives each deferred unit exit `"deferred"`. It is never counted as passed (`Coverage.recorded` needs exit 0 or 5), and the static graph answers for it until it runs again.
- **The CLI.** `--defer-heavy` refuses `--full`, `--impacted` and `--tier`. The run prints `deferred to the chain gate: N test files ... (S s): ...`.
- **Where it applies.** It is opt-in. `tools/gate.py`, `verify.sh` and the merge train never pass it.

Where it applies (manage-agents):

- **When `mac-pytest.sh` adds it.** It appends `--defer-heavy` to a `--select ... --run` when `defer_heavy_ok` (defer-heavy.zsh) says so. That needs the flag DEFER_WEAK_HEAVY, no CHAIN_GATE_RISKY_ONLY (its skip could let a deferring builder run stand in for the chain gate), no `MAC_PYTEST_NO_DEFER`, and no `--full/--impacted/--tier`. The worktree's own `tools/select_tests.py` must also have the option, so a branch from before this merges never gets an argument it would refuse with exit 2.
- **The chain's own runs.** `chain-gate.sh`'s selected run (the Mac-unavailable fallback) and `infra-item.sh`'s FAST-lane `fast_tests` set `MAC_PYTEST_NO_DEFER=1`.
- **The deferred files still run** in the chain's full gate (MAC_GATE: `tools/gate.py` runs every unit), the candidate gate (R2) and the nightlies.
- **Actions.** The Actions shards (`gha/shard-select.py`) record a map of their own units only, so a deferred file is absent there, never passed.

Live probe on this branch: `uv run python tools/select_tests.py --base $(git merge-base HEAD main) --defer-heavy` printed `115/505 test units` (127 without the option) and `deferred to the chain gate: 12 test files over 120 s selected only for weak reasons (7072.3 s)`, including test_english_evidence, test_trust_mutants and test_relay_mutation_gate.

## 4. Measured saving

Command: `python3 -I tools-local/defer-heavy-measure.py --repo <this worktree> --jobs 6 --json measure-jobs6.json`, and the same with `--jobs 8`.

- **Method.** The script replays this branch's `defer_heavy` over the 179 saved select_tests plans of the nightly-tier measurement (main commits since Oct 15). Each unit's seconds are its median selected-run seconds (classified.json `sel_med`). It simulates each recorded run's wall: `run_order.order`, then each unit on the first free worker.
- **Plans.** 63 are non-full. 78 are full only because the replay had no coverage map, a replay artefact. 38 are full for real and defer nothing.

| jobs | non-full plans with a deferral | mean wall before | mean wall saved | median | max | est. saved wall / 14 d (373 runs) | est. saved unit-h / 14 d |
|---|---|---|---|---|---|---|---|
| 6 (mac-pytest cap) | 31 of 63 | 1126 s | 136.6 s | 0 | 642 s | 14.2 h | 80.3 |
| 8 (select_tests default) | 31 of 63 | 946 s | 118.8 s | 0 | 715 s | 12.3 h | 80.3 |

- **Files deferred most** (count of plans): test_relay_mutation_gate 19, test_consolidation_tools 18, test_trust_mutants 18, test_difffuzz 17, test_english_evidence 12, test_lean_document_wrapper 9 (`deferred_by_unit`).
- **Bounds.** The figures are an upper bound for the "failed last time" rule, which a replay cannot know. They are a lower bound for branch diffs, which are wider than one main commit.
- **The 373 runs** are the non-full selected runs per 14 days in reviews/nightly-tier-20261029.md section 3.
- **The cost.** A builder learns of a failure in a deferred file at the chain gate, one round later. The FLAGS.tsv guard counts these escapes.

## 5. Tests and seeded bugs

- `uv run pytest -q -p no:cacheprovider tests/test_select_defer.py`: 17 passed. Each rule is tested in both directions: weak against strong reasons, over against at the threshold, deferred against kept for each kept kind, a full plan against a plain one, and the option on against off.
- `python3 -I tools-local/test_defer_heavy.py`: 12 tests OK. Against the scripts before the change it failed 3 and errored 1, and against the first `defer-heavy.zsh` it failed 2: the wiring tests can fail.
- `seeded-bugs.json`: 9 seeded bugs. S1-S7 are in `tools/select_tests.py` (Python) and S8-S9 in `defer-heavy.zsh`. Each was caught by the named test (rc 1, FAILED) and then removed.

## 6. DELTA, trust and rulings

- **No DELTA.** No VE output changes (code, text, verdict or schema): the change is in the test selector and the pipeline scripts.
- **No trust growth.** No Lean was touched.
- **No test or check is deleted or skipped.** A deferred file runs in the chain's full gate, the candidate gate (R2) and the nightlies. No ruling is needed and none is reserved.

Spec re-read:

- "heavy unit (> 120 s)", against the row title: `DEFER_SECONDS = 120.0`, strict `>`. Test: `test_only_a_file_over_the_threshold_is_heavy`.
- "selected ONLY for weak reasons (static graph, listed directory, smoke)", against reviews/nightly-tier-20261029.md:90: `weak_reason`. Tests: `test_the_weak_reasons_are_...`, `test_a_heavy_file_selected_only_for_weak_reasons_is_deferred`.
- "defer it to the chain gate instead of every builder run", against the row and chain-gate.sh:7-34: builder runs only. The chain's runs opt out; `gate.py` is unchanged. Tests: `Wiring.*`, `Decision.*`.
- "measure saved builder test-wait": section 4.

## 7. Commits (main..HEAD --no-merges, saved at writing)

- a65b8abb2 test-cost-heavy: select_tests --defer-heavy leaves heavy files selected only for weak reasons to the chain gate
- the report, evidence and docs commit that follows it (this file)

## 8. Follow-ups

- **Merging with eff-20261030-1.** That branch adds the same `map_seconds(plan)` (same body). Whichever merges second keeps one copy. Its `run_recorded` rewrite must keep the `deferred` exit loop.
- **The trial guard.** DEFER_WEAK_HEAVY is not in the combined trial-stack guard (`tools-local/trial-guards.py`, PL L126). Its own guard and end are in FLAGS.tsv (review 2026-11-12, with the nightly-tier re-check).
- **Re-measuring.** The saving can be re-measured from the tree maps: each deferred unit has exit `"deferred"` and its seconds in `~/.cache/ve-testmap/tree-*.json.gz`.
