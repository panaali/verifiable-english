# gha-gate-shard build report

Status: implementation complete; selected tests timed out on the loaded VM without a reported failure; final gate is delegated to the chain.
HEAD: `infra/gha-gate-shard` branch tip after this report is committed.
Changed: `tools/gate.py --shard K/N` and `--merge-shards`, a deterministic file plan, fail-closed assembly, and fixture tests.
Open items: the chain must run the final full gate; the DRI-owned Actions workflow must dispatch shards and supply the pinned Rust binary to shards 2..N. No DRI signature is needed for this infrastructure item.

## Delivery and evidence

| Acceptance item | Owner | Evidence |
|---|---|---|
| All shards build Lean, check toolchains and source identity, collect the full suite; shard 1 runs audit, Rust build/tests, wire contract and trust | AGENT | `test_gate_runs_full_collection_and_only_its_share` (N=1,2,3, including live deselection) |
| Greedy longest-first file plan, identical in each shard, one owner for every selected ID | AGENT | `test_plan_is_repeatable_and_partitions_each_collected_id_once`; [plan evidence](plan-evidence.json) |
| One full record with all counts, failures, skips, quarantine, durations, stages and shard metadata | AGENT | `test_merged_counts_and_collection_match_unsharded_fixture`, `test_failed_test_is_reported_in_merged_full_record`, `test_gate_runs_full_collection_and_only_its_share`, `test_merge_cli_writes_one_full_record` |
| Missing shard; changed commit, tree, N, plan or platform; no suite; incomplete events | AGENT | `test_merge_cli_refuses_any_missing_shard`, `test_merge_refuses_mismatched_or_empty_shard` |
| Real suite N=6 and N=10 plan from main's collection and recorded durations, without running the suite on the VM | AGENT | [plan evidence](plan-evidence.json): main `d25bc343`, 20,287 collected, 20,286 selected, 2,218 recorded durations. Predicted seconds: N=6 min 4,347.5 / max 4,347.6; N=10 min 2,552.3 / max 3,114.5. These are summed test estimates, not measured wall time. |
| x86 Actions leg and nightly workflow, with fallback and comparison to the existing gate | EXTERNAL, DRI workflow owner | DRI decision `dri-decisions-20261028-gha-gate-shard.md` item 2 and backlog `actions-gate-x86`; no `.github/workflows` edit here. |
| aarch64 Actions leg | HUMAN, DRI | Separate decision required; outside this item. |

The DRI decision's condition test is `test_gate_runs_full_collection_and_only_its_share` (N=1,2,3 against an unsharded run of the same fixture commit) together with `test_merge_cli_refuses_any_missing_shard`. The merge also refuses changed commit, plan digest or N. R18 is met by keeping the existing optional-test policy and checking the full deselected collection; `test_gate_runs_full_collection_and_only_its_share[True-3]` compares skips with the unsharded result. No VE language, wire, trust or product behavior changed, so there are no DELTA rows.

The predicted ten-shard maximum is above its minimum because one test file is an indivisible unit. The input is the saved main gate record `mac-gate-cand-me-3.raw.json`, overlaid on `tools/test-durations.json` using `test_schedule.overlay_text`. The JSON evidence records both plan digests and every predicted shard load. No full suite ran on the VM.

## Seeded bugs, removed

Each mutation was made in `tools/gate_shards.py`, run with its named test, and restored before final validation:

| Behavior | Seeded bug | Failing test |
|---|---|---|
| Greedy partition | Forced every file onto shard 1 | `test_plan_is_repeatable_and_partitions_each_collected_id_once` |
| Missing shard must fail | Returned a passing record at the missing-record branch | `test_merge_cli_refuses_any_missing_shard` (all three missing positions) |
| Merged counts equal unsharded | Counted only shard 1 | `test_merged_counts_and_collection_match_unsharded_fixture` (N=2,3) |

The three local mutant commands exited 1 with, respectively, 1, 3 and 2 failing cases in those tests. No mutant remains in the committed source.

## Gate record readers

The merged JSON keeps `mode=full`, `status=passed` or `failed`, the standard full stage list, full collection encoding, and standard counts. `test_gate_runs_full_collection_and_only_its_share` exercises `tools/batch_evidence.py` and the `tools/gate_collection.py` note format. `tools/since_pass.py` and `tools/run_order.py` read the same fields. When the merger runs in the matching checkout, it writes the usual collection/result git note.

Read-only audit of `/home/seyran/code/manage-agents`: `gaterec.py`, `review-ready.py`, `chain-gate.sh`, `merge-train.sh` and `gha/gate-compare.py` consume standard full records and need no schema change. The DRI-owned Actions dispatch must collect all N shard JSON files, call `tools/gate.py --merge-shards ... --output gate-result.json`, then pass that one record to `gaterec.py`/the train. It must provide the pinned `rust/target/release/ve` artifact to shards 2..N, which verify its hash before pytest. No manage-agents file was edited.

## Checks and limits

- Focused tests: 23 passed in `tests/test_gate_shards.py` (merge refusals and full collection for N=1,2,3). The selected run also completed `tests/test_gate_shards.py` and the unsharded regression files `tests/test_gate.py` and `tests/test_gate_integrity.py` with exit 0.
- Generated history manifest: `tools/history_tests.py --write` updated `tests/history-dependent.json` for the new test file. `tools/regen_generated.py --write` and `--check` both exited 0; the later write changed no generated file.
- Selected tests: the wrapper's first attempt never reached pytest because the sandbox's default selector cache was read-only. With caches redirected to `/tmp`, the selection was 131 of 486 units. Its one-hour VM run completed 125 of 130 pytest files with exit 0 and timed out with five files unfinished. A run of only those five files reached 73% with no reported failure and also timed out at one hour. The Mac connection was unavailable; neither run produced a complete selected-test verdict. No whole-suite run was launched.
- Full release gate: not run locally, as explicitly directed; the chain runs it on final HEAD. No model calls, push or workflow edit.

## Build checklist applicability

Lines 1–12, 15, 17–19 concern VE contracts, product inputs, Lean proofs or use-case formalisation and are N.A. here. Line 13 is covered by the three seeded bugs above and the missing/empty-record tests. Line 13a is N.A. because no Lean changed. Line 14 is covered by the temporary fixture and isolated gate smoke tests. Line 16 is covered by the generated history manifest and the full-collection partition test. Line 20 is covered by this report and the saved plan evidence; no permanent report test was added (D4/R11). Line 21 is the AGENT/HUMAN/EXTERNAL table above. Line 22 follows this item's override: selected tests once on finished code, full gate by the chain on final HEAD. Line 23 is N.A. because there is no VE language delta or DELTA row; DRI item 2 covers the x86 infrastructure use, and R18 adds no skips.

## Self-review against BUILDER-CHECKLIST

1. N.A. — no Lean response or decoder changed.
2. PASS — acceptance table and `git diff --check`; `test_gate_runs_full_collection_and_only_its_share`.
3. PASS — three seeded bugs and `test_merge_cli_refuses_any_missing_shard`.
4. N.A. — no Python/Lean/Rust product semantics changed.
5. N.A. — no relayed Lean answer or request binding changed.
6. N.A. — the task explicitly assigns the final full gate on committed HEAD to the chain.
7. PASS — no DELTA row or trust growth; DRI decision item 2 and R18 condition test above.
8. PASS — `test_gate_runs_full_collection_and_only_its_share` compares full record outcomes and skips; no VE output delta.
9. PASS — `tools/select_tests.py --base d25bc343be0f41a29a65c6a8766f18f2b1694e8d` selected `tests/test_gate_shards.py` and 130 test files total; `tests/test_gate_shards.py` passed in the selected run. The whole selection timed out as recorded above.
10. N.A. — no Lean statement or proof changed.
11. N.A. — no budget, limit or deadline changed.
12. N.A. — no VE check or render CPU path changed; [plan evidence](plan-evidence.json) gives gate load estimates.
13. N.A. — no test was removed or renamed.
