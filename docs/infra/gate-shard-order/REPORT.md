# gate-shard-order: a real sharded gate run can pass

- Status: built. The selected tests pass (113 units, 0 failed). The full gate is the chain's to run (not run here).
- What changed: `tools/gate.py` `merge_pytest_events` takes `any_order=True` for a shard. Each xdist worker must then
  have collected the shard's ids as a set: none missing, none extra, none duplicated. The unsharded gate keeps its exact list comparison.
- Cause: the shard plan stores its ids sorted (`gate_collection.encode_ids`), so a share is in sorted order. The
  workers report pytest's order. The sets were equal and the lists were not.
- Open items: none. No DELTA rows (gate tooling only, per the task). No trust change. No DRI signature needed.

Backlog row gate-shard-order (infra), decision `reviews/dri-decisions-20261028-parallel-actions.md` item 3
(Ruling 2026-10-29 01:54Z, Amendment 02:05Z).

## The failure

All 8 real arm64 shard jobs (manage-agents `gha-arm/armsh-*/s*/`) failed in `merge_pytest_events` after their share of the suite had
run. The count was the same on both sides each time
(`grep -h 'FAILURE: gate' gha-arm/armsh-*/s*/gate.log.tail`):

| record | failure |
|---|---|
| armsh-cand-en-sw-87853bd5 s1..s4 | `worker gw0 collected 4796 / 14085 / 7163 / 4240 tests, not the collection run's 4796 / 14085 / 7163 / 4240` |
| armsh-cand-sc-3ac-8868ce21 s1, s2 | `... 12032 ..., not ... 12032`; `... 18248 ..., not ... 18248` |
| armsh-seed-test-eaf29209 s1, s2 | `... 11899 ..., not ... 11899`; `... 18382 ..., not ... 18382` |

The share in every record is sorted: `shard.ran == sorted(shard.ran)` is True for all 8 records. I checked this with a
`python3 -I` read of each `gate-record.json`.

## The cause (order, not representation)

`gate_shards.share` decodes the plan's `selected` with `gate_collection.decode_ids`. `encode_ids` stores the ids
**sorted** (`json.dumps(sorted(ids))`, `tools/gate_collection.py:137`), so the share is in lexicographic order. The
shard's suite run gives the workers the share's files and keeps the share's ids (`VE_GATE_PYTEST_IDS_FILE`, exact
mode). Each worker then reports its collection in pytest's order: file order, then definition and parameter order.
Within a file that order is not sorted: for example `[plain-act-and-form]` comes before `[permission-form]`. The
shard path then compared the two lists, so every real shard failed with equal counts. The fake-command shard test
never caught this because its fake workers echoed the ids file back in the same order.

The probe (`docs/infra/gate-shard-order/cause-probe.txt`) runs the gate's own `collection_command` on this tree:
once in full, and once on share 2 of a 2-way `gate_shards.plan` with the ids file, as a worker sees it. It shows:

- share 2 has 18186 ids and the explicit collection selects 18186. The sets are equal (`same set True`) and the
  lists are not (`same list False`).
- The first difference is at index 2, inside one parametrized test of `tests/test_acts_lexical.py`, and the
  order of files is equal.
- Share 2 taken in the full run's order equals the explicit collection's order (`... == ... True`), and the full
  run's selection is not sorted (`full run selected == sorted: False`). So the ids have the same representation
  and only the plan's sorting differs.

## The fix

`tools/gate.py`:

- `merge_pytest_events(collection, suite, *, any_order=False)`. Without `any_order` (the unsharded gate, contract
  and rerun runs), every worker's list must equal the collection run's `selected`, as before; the message is
  unchanged. With `any_order`, every worker's ids must be a list with no duplicate and the same set as the share.
  The refusal names how many ids are missing, extra and duplicated, and the first one.
- The shard path calls it with `any_order=True`. The plan and its digest are unchanged, and so are the record format,
  `shard.ran` and `gate_shards.merge_records`. No other caller changes.

I did not reorder the share to pytest's order. The plan's sorted ids are what `merge_records` checks `shard.ran`
against, and a set comparison does not depend on pytest's reordering, which can cross files (fixture-scope
reordering). Duplicates are still refused.

## The condition test (real pytest)

`tests/test_gate_shards.py::test_real_pytest_shards_merge_into_the_unsharded_record[passing]` and
`[failing-in-shard-2]`. The project has 3 test files:

- `tests/test_alpha.py`: one parametrized test whose parameters and functions are out of name order, plus a `live` test
  that the gate deselects.
- `tests/nested/test_beta.py`: in a nested directory, with an optional skip and a test that fails in the failing case.
- `tests/test_gamma.py`: functions out of name order.

`gate.main()` runs unsharded, then `--shard 1/2`, then `2/2`, all with `--workers 2`. The gate's own `collect` /
`collection_command` / `suite_command` / `gate.command` run real pytest with xdist (`-n 2`) in the project. Only the
interpreter is swapped (this venv's for `uv run`). The non-pytest stages are the same stand-ins as the existing
fake-command shard test, shared through `gate_project` / `patch_gate_stages` / `other_stage`.

The test asserts:

- The plan puts `test_alpha.py` in shard 1 and the other two files in shard 2.
- `gate_shards.merge_records(rows)` equals the unsharded record in status, `counts`, `failures`, `skips` and
  `collection.collected_zlib`, with 11 collected and 1 deselected.
- In the failing case, shard 1 passes and shard 2 fails. The merged record is `failed` with exactly one `pytest` failure,
  for `tests/nested/test_beta.py::test_y`, so the merge reports the failure instead of refusing.

Unit tests (`tests/test_gate.py`), both directions:

- `test_a_shard_worker_may_collect_its_share_in_any_order[plan order|pytest order]`: accepted.
- `test_a_shard_worker_must_collect_exactly_its_share[missing|extra|duplicate|duplicate for missing|not a list]`: refused.
- `test_the_unsharded_gate_still_needs_the_collection_runs_order`: the unsharded gate still refuses a reordered list.
- `test_the_gate_records_a_parallel_suite_run` (existing): the unsharded gate still accepts its exact list.

## Seeded bugs (Python only; no Lean or Rust product code changed)

Each bug was planted in `tools/gate.py`, shown failing with the test named in its row, and then restored with `git checkout tools/gate.py`.

| # | seeded bug | failing test | output |
|---|---|---|---|
| 1 | the list comparison comes back in the shard path (`merge_pytest_events(subset, ...)` without `any_order=True`) | `tests/test_gate_shards.py::test_real_pytest_shards_merge_into_the_unsharded_record` | `2 failed`; inner gate: `FAILURE: gate:  worker gw0 collected 5 tests, not the collection run's 5`, the GHA failure itself |
| 2 | the shard check drops its duplicate test (`len(ids) != len(set(ids))`) | `tests/test_gate.py::test_a_shard_worker_must_collect_exactly_its_share[duplicate]` | `1 failed, 6 passed` |
| 3 | the unsharded gate becomes order-independent (`any_order` defaults to True) | `tests/test_gate.py::test_the_unsharded_gate_still_needs_the_collection_runs_order` | `1 failed` |

## Tests run

- While iterating, `uv run pytest -q tests/test_gate_shards.py -k real_pytest` gave `2 passed`.
- `-k "full_collection_and_only_its_share or selected_id_reported"` (the refactored fake-command tests) gave `8 passed`.
- `uv run pytest -q tests/test_gate.py -k "shard_worker or still_needs or did_not_collect or parallel_suite"` gave `13 passed`.
- `uv run python tools/select_tests.py --base $(git merge-base HEAD main)` selects 113/499 units, including `tests/test_gate.py` and
  `tests/test_gate_shards.py`.
- Selected tests on the finished code (`zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`, ve-mac-1 aarch64,
  1713 s): `recorded 113 units ...; 0 failed`, `exit=0; failed/error ids=0`. The run started with the changed
  `tests/test_gate.py` and `tests/test_gate_shards.py`.
- Not run here: the full gate (the chain runs it) and the sharded shadow reruns on arm64. After the merge, manage-agents
  reruns the 2 shadow validations and the seeded run through `gha-arm-shard.sh`.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer or relay changed.
2. PASS: change 1 is `merge_pytest_events(any_order=True)`, tested by `test_a_shard_worker_*` and
   `test_the_unsharded_gate_still_needs_the_collection_runs_order`. Change 2 is
   `test_real_pytest_shards_merge_into_the_unsharded_record` (3 files, parametrized, nested, `-n 2`, 1/2, 2/2,
   unsharded, failure in shard 2). The report is this file. No new Python copy of a Lean decision and no permanent report test.
3. PASS: the 3 seeded bugs above, each with its failing test.
4. N.A.: no Python/Lean/Rust semantics changed.
5. N.A.: no relayed answer or binding changed.
6. N.A. here: the chain runs the full gate on the final HEAD; the branch has no batch evidence commit list.
7. PASS: no DELTA row and no trust growth (task: "No DELTA rows ... No trust signature"). Both exits are tested:
   shard 2 fails with a reason (`assert gate.main() == 1`, failing case), and the merged status is `failed`.
8. PASS (none): gate tooling only. No VE output changed (`git diff main...HEAD --stat` touches only `tools/gate.py`, two
   test files and this directory).
9. PASS: `select_tests.py` selects `tests/test_gate.py` and `tests/test_gate_shards.py`, which catch seeded bugs 1–3.
10. N.A.: no Lean.
11. PASS: no new wait, sleep or deadline. The real pytest runs go through `gate.command` like the gate's own (existing
    real-pytest tests in `tests/test_gate.py` do the same).
12. PASS: no hot path changed. The set comparison is O(n) per worker; the duplicate count runs only on refusal (`collections.Counter`).
13. N.A.: no test removed or renamed (the existing shard test keeps its name and parameters).
14. PASS: both directions are tested (accept reordered / refuse missing-extra-duplicate; unsharded refuse reordered /
    accept exact). Each claim above cites its command or file.
    - spec re-read: "every xdist worker collected exactly this shard's ids: the same SET, no missing, no extra, no duplicate"
      against the task's change 1; `merge_pytest_events` refuses each of those (`test_a_shard_worker_must_collect_exactly_its_share`).
    - spec re-read: "the unsharded gate must stay exactly as strict" against the task's change line; the default is
      `any_order=False` (`test_the_unsharded_gate_still_needs_the_collection_runs_order`).
    - spec re-read: "merged record equals the unsharded record (collection, counts, failures, skips) ... failing test in
      shard 2 is reported as that test's failure" against the task's change 2; asserted field by field in the condition test.
