# eff-20261103-1: gate shards weigh tests by measured durations when the merge base has no gate note

**Status:** fix round for review F1 done (one fail-closed JSON decoder for every gate-record reader; see "Fix round"); ready for the chain's gate. Branch infra/eff-20261103-1, merge base 87475ae6a (main = ve-integration).
**What changed:** `tools/gate.py --durations-record RECORD` weighs the suite and the `--shard k/N` plan by a gate record
file's durations when the base has no note. `tools/bench/suite_tail.py durations --gate-record FILE` is added, and
`tools/test-durations.json` is refreshed from four measured full runs.
**No DRI signature needed.** No DELTA rows (no user-visible VE change: tools layer scheduling only). Trust +0. No Lean or Rust change.
**Open:** the dispatcher wiring (one line, below) is the eff pass's FOLLOW-UPS row. It is outside this repo.

## Cause

On the GitHub Actions aarch64 leg, `gha-arm-shard.sh` runs `tools/gate.py --shard k/N` on N runners. Their clones have
no `refs/notes/ve-gate-result`. So `base_durations` finds nothing, `durations_source` is
`{'base': None, 'committed': 2567, ...}`, and `gate_shards.plan` weighs files from the committed
`tools/test-durations.json` alone. That file came from VM/Mac profiles of 2026-10-13..17. Since then, node IDs changed
(for example the speed-vocabpar split of `tests/test_acts_vocab_mutants.py`, now all "unrecorded" at 0.107 s) and costs
moved. The me-8 leg planned 5 × 10492.3 s but measured 3658 / 2434 / 2621 / 5636 / 9690 pytest-seconds per shard
(`evidence/legs.json`, below).

## Diff summary (`git diff --stat main...HEAD`: 16 files; the code is in the first five below)

- `tools/gate.py`:
  - `record_file_durations(path)` (l.651) reads a gate record file. It reads at most `MAX_DURATIONS_RECORD_BYTES`
    (16 MiB, l.80), then takes `durations` through `test_schedule.read_record_field` (where `MAX_RECORD_BYTES`
    applies). It takes the measured IDs from `collection.collected_zlib`, but only when `durations.tests ==
    counts.selected`, the same rule `base_durations` applies to a note. A missing, unreadable, oversize or malformed
    file logs one line (`[gate] durations record … not used`) and gives None.
  - `suite_durations(..., record=None)` (l.675) uses the file only when `base_durations` finds no note. It records
    `durations_source["record_file"] = {"used", "sha256", "recorded"}` when the option is given.
  - `--durations-record RECORD` (l.751) is resolved against the cwd. It is refused with `--merge-shards`.
  - Untouched: `selected`, the collection, `interpret_pytest`/the collection check, the plan digest and `merge_records`.
- `tools/bench/suite_tail.py`: `durations --gate-record FILE` (repeatable). Each record counts as one more run (each test's
  longest time). The unrecorded estimate is the longest of the inputs' means of short tests. The source line names
  each record path and its sha256. A file that is not a gate record with durations is refused.
- The suite_tail option is `--gate-record`, not the task's `--record`. `--record` is one of the repo's writing-mode
  flags (`tools/regen_generated.py` `WRITE_FLAGS`), so that name would class suite_tail.py as a writer of a generated
  file. Listing it in `NOT_REGENERATED` put the literal `tools/bench/suite_tail.py` in `tools/regen_generated.py`.
  The test selector then reached every importer of regen_generated (108 test files) from any `tools/bench/` change.
  The chain's gate at 839a1284 failed on this, in `tests/test_select_tests.py::test_narrow_changes_select_few_tests`
  (`tools/bench/baseline.py`: 108 not < 40). See "Gate fix" below.
- `tools/test-durations.json`: refreshed (see below).
- Tests: `tests/test_gate_durations.py` (+13), `tests/test_gate_shards.py` (+2; the stub of `suite_durations` in
  `patch_gate_stages` now accepts the new argument), `tests/test_suite_tail.py` (+1). No test was removed, renamed or skipped.
- Evidence: `docs/infra/eff-20261103-1/evidence/` holds the input records, `legs.json` and `replay.json`, plus `seeded-bugs.json`.

## The refreshed durations file

Command (run once, in this worktree, collection = the current gate collection):

```
uv run python tools/bench/suite_tail.py durations --output tools/test-durations.json --source "eff-20261103-1 …" \
  --gate-record docs/infra/eff-20261103-1/evidence/arm-en-s6b-87475ae6-t724087.gate-record.json \
  --gate-record docs/infra/eff-20261103-1/evidence/arm-sc-5rdb-3564ccc8-t715994.gate-record.json \
  --gate-record docs/infra/eff-20261103-1/evidence/arm-qt-a4-fd9f25f9-t712041.gate-record.json \
  --gate-record docs/infra/eff-20261103-1/evidence/mac-sa-no-exception-8ef1adbc.gate-result.json
→ wrote 2395 of 2395 tests to tools/test-durations.json
```

Inputs:
- The three merged aarch64 Actions records named in the task, at 4 workers.
- The newest Mac full gate record with durations I found: `/home/seyran/code/ve-sa-no-exception/gate-result.json`.
  It is from ve-mac-1 (aarch64, 9 workers), commit 8ef1adbc, written 2026-11-03 19:18, status passed, 31868 tests timed.
- The newest VM note with durations (4b2c04b68, 01:07) is older, so I did not use it.
- I did not use `--previous`. The old file's overweights (`test_english_evidence.py` 3794 s, `test_assist_invariants.py`
  3072 s) were part of the imbalance.

The source line names each input and its sha256. Per-file weights, before → after, from `test_schedule.unit_seconds`:

| file | before | after |
|---|---|---|
| tests/test_acts_vocab_mutants.py | 0 | 2712.9 |
| tests/test_trust_mutants.py | 0 | 2439.7 |
| tests/test_english_evidence.py | 3794.2 | 1016.8 |
| tests/test_assist_invariants.py | 3071.6 | 435.0 |

The unrecorded estimate goes from 0.107 to 0.06. There are 2567 recorded tests before and 2395 after. The "before"
column counts only recorded IDs; the leg records showed vocab_mutants at 68.8 because each of its tests got 0.107.

## Replay on the measured legs

The shard plans for the me-8 (t706979, N=5) and en-s6b (t724087, N=4) legs come from their own selected IDs (the shard
plans' `selected`, saved in `evidence/legs.json`). "Measured" sums each leg's own per-test `pytest_seconds`
(setup + call + teardown, all shards) by file under each plan. The script (`/tmp/eff-20261103-1/replay.py`, outside the
repo; a `.py` under docs would enter the generated codemap) calls `gate.suite_durations` and `gate_shards.plan`, and
saves its output in `evidence/replay.json`.

**Sanity check:** the "before" plan reproduces each leg's recorded planned seconds and measured per-shard loads exactly.
Compare the recorded `shards[].pytest_seconds` in `legs.json` with the "before" row.

| leg | durations | planned per shard (s) | measured per shard (pytest-s) | max | mean | max/mean |
|---|---|---|---|---|---|---|
| me-8 | before (committed 2026-10-13..17) | 10492 ×5 | 3658 / 2434 / 2622 / 5636 / 9690 | 9690 | 4808 | 2.02 |
| me-8 | after (refreshed, no record) | 5637 ×5 | 4846 / 4538 / 4990 / 4392 / 5272 | 5272 | 4808 | 1.10 |
| me-8 | after + `--durations-record` en-s6b | 4888 ×5 | 4584 / 4824 / 4594 / 4628 / 5408 | 5408 | 4808 | 1.12 |
| en-s6b | before | 13120 ×4 | 7422 / 6154 / 4179 / 6898 | 7422 | 6163 | 1.20 |
| en-s6b | after (refreshed, no record) | 7098 ×4 | 6443 / 5868 / 6119 / 6222 | 6443 | 6163 | 1.05 |
| en-s6b | after + `--durations-record` en-s6b | 6162 ×4 | 6136 / 6243 / 6125 / 6149 | 6243 | 6163 | 1.01 |

Caveats:
- en-s6b is in-sample: its record is one of the refresh's inputs. me-8 is out-of-sample: its run predates all four
  inputs.
- **Wall time (ESTIMATE, not measured):** the shard walls were me-8 1395 / 725 / 804 / 1741 / 3701 s and en-s6b
  3076 / 1686 / 1287 / 1909 s. Scaling the heaviest shard by that leg's own ratio of wall to pytest-seconds gives:
  - me-8: about 3701 → 2000 s (−28 min);
  - en-s6b: about 3076 → 2670 s (−7 min).
- Shard 1 also does the base collection (about 570 s on en-s6b). The plan does not weigh that cost; I left it as is
  (out of scope: scheduling weights only).

## Wiring for the dispatcher (FOLLOW-UPS row; not changed here)

Add `--durations-record <path>` to each shard's `tools/gate.py --shard k/N …` command line in `gha-arm-shard.sh`
(or `gha/gate-job.sh`). Pass every shard of a leg the same file: the newest merged arm `gate-record.json`. The rules:

- **Path:** a relative path is resolved against the gate's working directory.
- **Content:** any full gate record or merged shard record, i.e. any JSON object with a `durations` field in
  `ve-test-durations@1` record format. At most 16 MiB.
- **When it is used:** only when the merge base has no `refs/notes/ve-gate-result` record. A base note always wins.
- **Failure:** a missing, unreadable, oversize or malformed file never fails the gate, at any nesting depth of the
  file or of its compressed `seconds_zlib` field (`test_schedule.json_value`, fix round F1). It logs one line and leaves
  the committed durations. Malformed or too-deep `collected_zlib` IDs keep the file's durations with no measured tests.
- **Effect:** the file changes only weights (the xdist start order and the shard plan's assignments), never `selected`,
  the collection or its check.
- **Where to see it:** `durations_source.record_file` in each shard record says whether the file was used, with its
  sha256 and the number of tests it records.

All shards given the same bytes compute the same plan. The plan digest and `merge_records` still tie them.

## Proof (tests; hermetic, tmp_path only)

- `tests/test_gate_durations.py::test_a_durations_record_file_weighs_the_file_the_committed_durations_underweight`:
  the committed file weighs the heavy file at 4 s and the record at 240 s. With the record, the heavy file's shard holds
  only it, and the measured max/mean is lower than under the committed plan. It also checks `durations_source` and that
  the same file gives the same plan.
- `…::test_a_missing_malformed_or_oversize_record_file_leaves_the_committed_plan[*]` (9 cases: missing, not JSON, not an
  object, no durations, malformed durations, seconds over `MAX_RECORD_BYTES`, a directory, a list nested 100k deep,
  not UTF-8). In each, the plan equals the committed plan and exactly one log line is written.
- `…::test_a_record_file_larger_than_the_limit_is_not_read` checks both sides of `MAX_DURATIONS_RECORD_BYTES`.
- `…::test_a_record_file_that_did_not_time_its_whole_selection_names_no_measured_tests` covers both directions.
- `…::test_a_base_note_wins_over_the_record_file` uses a real git note in a tmp repository.
- `tests/test_gate_shards.py::test_a_durations_record_changes_only_the_plan[good|malformed]`: runs `gate.main()` with
  `--shard k/2` with and without the file. These stay equal: `selected` per plan, the shards' `collected`, each
  record's `collection` (except the share-local `head_ids`), status and failures, and the merged record's counts,
  failures, skips, collection and stages. The union of the shares is every selected test, each exactly once. With a
  good file the plan changes (another digest; `tests/d.py` is no longer with `tests/a.py`). With a malformed file the
  plan is identical.
- `tests/test_suite_tail.py::test_durations_command_reads_gate_records_as_more_runs`.

## Seeded bugs (`docs/infra/eff-20261103-1/seeded-bugs.json`; each planted, run with the one test, restored by `git checkout`)

| id | file | bug | failing test |
|---|---|---|---|
| S1 | tools/gate.py | suite_durations ignores the file (`from_file = None`) | tests/test_gate_durations.py::test_a_durations_record_file_weighs_the_file_the_committed_durations_underweight |
| S2 | tools/gate.py | the base note is skipped, so the file wins | tests/test_gate_durations.py::test_a_base_note_wins_over_the_record_file |
| S3 | tools/gate.py | no file size cap | tests/test_gate_durations.py::test_a_record_file_larger_than_the_limit_is_not_read |
| S4 | tools/gate.py | with the file, the plan takes the collected IDs as the selection | tests/test_gate_shards.py::test_a_durations_record_changes_only_the_plan[good] (and [malformed]) |
| S5 | tools/bench/suite_tail.py | shortest instead of longest unrecorded mean | tests/test_suite_tail.py::test_durations_command_reads_gate_records_as_more_runs |
| S6 | tools/gate.py | `RecursionError` not caught when reading the file | tests/test_gate_durations.py::test_a_missing_malformed_or_oversize_record_file_leaves_the_committed_plan[nested 100k deep] |
| S7 | tools/bench/suite_tail.py | `--gate-record` inputs dropped | tests/test_suite_tail.py::test_durations_command_reads_gate_records_as_more_runs |
| S8 | tools/test_schedule.py | `json_value` catches `ValueError` only (the F1 bug, in the shared decoder) | tests/test_gate_durations.py::test_every_record_reader_leaves_a_value_nested_too_deep_unused (9 tests failed) |
| S9 | tools/gate_collection.py | `parse_record` back on its own `json.loads` / `except ValueError` | tests/test_gate_durations.py::test_the_record_modules_parse_untrusted_json_only_through_json_value (3 tests failed) |

Each showed `1 failed` (S4: `2 failed`) in `uv run pytest -q <test>`. The tree was clean after each. Only Python
product code changed, so there are no Lean or Rust seeds.

## Tests run

- Changed files: `uv run pytest -q tests/test_gate_durations.py tests/test_gate_shards.py` → 118 passed, then
  `tests/test_gate_durations.py` → 38 passed after the S6 fix (two more cases). `tests/test_suite_tail.py` → 10 passed. `tests/test_test_schedule.py tests/test_run_order.py` (readers of the
  committed file) → 58 passed. `--collect-only` on the three changed files collected 128 tests before the S6 fix and 130 after; 16 of them are new.
- Selected: `zsh mac-pytest.sh --select -- --base 87475ae6 --run` on ve-mac-1 at HEAD 301c7c18.
  - 395/538 units were selected, and 54 heavy files were deferred to the chain gate.
  - 391 units passed, and 1 failed: `tests/test_regen_generated.py::test_every_script_with_a_writing_mode_is_registered_or_excluded_with_a_reason`
    (fixed then by a `NOT_REGENERATED` entry, which the gate fix below replaces with the `--gate-record` rename).
  - Known Mac-only failures: none.
  - After the run, one more change: `RecursionError` is caught in `record_file_durations` and two bad-file cases were
    added. Both are covered by `tests/test_gate_durations.py` (38 passed).
  - `git merge-base HEAD ve-integration` = `git merge-base HEAD main` = 87475ae6, so the ve-integration selection is
    this same selection.
- `uv run python tools/regen_generated.py --check` → checked 35 entries, nothing stale.
- No lake build or audit (no Lean change). No trust_mutants (no trusted Lean).
- The full gate is not run by me: the chain runs it on the final HEAD.

## Gate fix (after the chain's gate at 839a1284)

The chain's full gate at 839a1284 ran 32089 selected tests: 31994 passed, 94 skipped, 1 failed. The failure was
`tests/test_select_tests.py::test_narrow_changes_select_few_tests` (`tools/bench/baseline.py` selected 108 test files, not < 40).
It is not in main-known-red. The cause was this branch's `NOT_REGENERATED` entry (see the diff summary).
- What changed: suite_tail's flag `--record` is now `--gate-record` (tools/bench/suite_tail.py, tests/test_suite_tail.py),
  and the `NOT_REGENERATED` entry is gone. The branch's diff of tools/regen_generated.py is now empty.
- `tools/test-durations.json` was rewritten by the same command with `--gate-record`. Only its `source` line changed
  (`--record` → `--gate-record`); every duration and the unrecorded estimate are identical.
- Tests: `tests/test_select_tests.py -k narrow_changes_select_few` → 1 passed.
  `tests/test_suite_tail.py tests/test_regen_generated.py` → 72 passed. `tools/regen_generated.py --check` → 35 entries, nothing stale.
- Selected for the fix: `zsh mac-pytest.sh --select -- --base 839a12844 --run` on ve-mac-1 at HEAD bc5d4b57.
  49/538 units were selected, and all passed (exit 0, 0 failed ids; test_trust_mutants.py 564 passed in 4 chunks).
  tests/test_gate_collection.py was deferred to the chain gate.
- Seed S7 (tools/bench/suite_tail.py): `--gate-record` inputs are dropped (`runs.append` removed).
  `tests/test_suite_tail.py::test_durations_command_reads_gate_records_as_more_runs` failed; restored.

## Fix round (review of 77df5f00: eff-20261103-1-review.final.md)

F1 (B) was the only A/B finding. F4 (C) is closed here as well. F2 (C, the replay script outside the repo) stays a follow-up.

- **F1 class:** a reader that leaves a malformed gate record, note, durations or retry file unused let `json.loads`'s
  `RecursionError` out (it is not a `ValueError`). There were seven readers: `test_schedule.read_record_field` (the
  compressed durations), `gate_collection.decode_ids` (the compressed IDs), `gate_collection.parse_record` (the note text),
  `gate.record_file_durations`, `gate.read_previous`, `gate.retry_quarantined` and `test_schedule.read_source`.
- **Fix (cd9a64a65):** one decoder is shared. `test_schedule.json_value` returns None on any parser error, `RecursionError`
  included, and `test_schedule.zlib_json_value` is the one base64 + bounded zlib + JSON decoder of the compressed fields.
  It replaces the two copies in `read_record_field` and `decode_ids`. All seven readers go through it. So the note path in
  `base_durations` and `suite_tail durations --gate-record` (now `SystemExit: … not a gate record with durations`) are
  covered as well. A change to tools/test_schedule.py keeps the selection at the same units (checked: 42/538 before and
  after).
- **Class guard:** `tests/test_gate_durations.py::test_the_record_modules_parse_untrusted_json_only_through_json_value`
  walks the AST of tools/gate.py, tools/gate_collection.py and tools/test_schedule.py. Every `json.load(s)` call left
  there must appear in `PARSER_CALLS`, with the reason it may raise. These are the gate's own outputs (a malformed one
  fails the gate) or text that `parse_record` has just parsed. A `from json import` also fails it.
- **PROBE F1:** before the fix it raised `RecursionError: Stack overflow … while decoding a JSON array`; after cd9a64a65 it
  prints `OK`. Its regression test is
  `tests/test_gate_durations.py::test_a_missing_malformed_or_oversize_record_file_leaves_the_committed_plan[seconds nested 100k deep]`.
- **Regression tests added (all tmp_path only):**
  - `test_gate_durations.py::test_a_record_field_retyped_or_malformed_is_ignored[seconds nested 100k deep]`
  - `…::test_a_missing_malformed_or_oversize_record_file_leaves_the_committed_plan[seconds nested 100k deep]`
  - `…::test_a_record_file_that_did_not_time_its_whole_selection_names_no_measured_tests`: nested `collected_zlib`, also
    through `suite_durations`
  - `…::test_the_base_durations_come_from_the_base_gate_record`: a note with nested durations, and a note whose text is
    nested
  - `…::test_every_record_reader_leaves_a_value_nested_too_deep_unused`: every reader. It first asserts that
    `json.loads` still raises `RecursionError` on the input.
  - `…::test_the_compressed_field_decoder_takes_exactly_its_limit`: limit and limit-1, plus retyped inputs
  - the class guard above
  - `test_gate_collection.py::test_a_record_retyped_or_rebound_is_ignored[collected nested 100k deep]`
  - `…::test_a_record_that_is_not_an_object_is_ignored[nested 100k deep]`
  - `test_suite_tail.py::test_durations_command_reads_gate_records_as_more_runs`: a nested file and nested `seconds_zlib`
- **Where this departs from the review's wording:** the review asked for a nested-`collected_zlib` case in `BAD_FILES`.
  That table asserts the file is not used. Bad IDs never made a file unused, though: the `"***"` case keeps the durations
  with no measured tests. So the nested case asserts the same behaviour, in the measured-None test, and does not change it.
- **Seeds:** S8 and S9 above (Python only; no Lean or Rust product code changed). Each was planted, failed, and was
  restored from a saved copy (`git diff` clean afterwards).
- **F4:** S7 is now in seeded-bugs.json, with S8 and S9.
- **Tests run:**
  - `tests/test_gate_collection.py tests/test_suite_tail.py tests/test_gate_durations.py tests/test_test_schedule.py`:
    180 passed.
  - Selected: `zsh mac-pytest.sh --select -- --base 87475ae6 --run`, at HEAD cd9a64a6 plus this REPORT and
    seeded-bugs.json, uncommitted (snapshot c11a0be4). 44/538 units on the cloud runner (4 shards, run
    eff-20261103-1-573635c5-t755812): 47 of 47 shard units passed, exit 0, 0 failed. test_trust_mutants.py ran
    564 passed in 4 chunks.
  - `lake build`: exit 0, 1270 jobs; there is no Lean change on the branch. `python3 lean/audit.py`: PASS, 756 files and
    8361 theorems.
  - `tools/regen_generated.py --check`: 35 entries, nothing stale.
- **Not run:** the full gate. The chain runs it on the final HEAD.
- **DELTA:** none. The change is tools-layer scheduling robustness with no user-visible VE delta, so there are no Ruling
  cells and no signature is needed.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer is read or changed.
2. PASS: task items 1 (`--durations-record`, gate.py l.651/675/751), 2 (refresh plus `suite_tail --gate-record`, evidence
   copied) and 3 (no orchestration change; wiring above), and every Proof bullet are delivered by the tests named under
   Proof and Replay. No new permanent report test (D4): the replay is saved evidence.
3. PASS: S1–S9 above, each with its failing test.
4. N.A.: no Python/Lean/Rust semantics changed.
5. N.A.: no Lean answer fields.
6. PASS: the chain's gate runs on the final committed HEAD. The branch sits on current main 87475ae6 (merge base).
7. PASS: no DELTA rows and no trust growth, so nothing to sign.
8. PASS: no user-visible change. The new `durations_source.record_file` gate-record field appears only when the
   option is given. `tests/test_gate_durations.py::test_the_gate_names_the_overlay_to_its_suite_and_records_the_suites_seconds`
   still asserts the exact old dict for a gate without it.
9. PASS: `tools/select_tests.py --base 87475ae6` selects 450/538 locally (395 on the Mac map). It is not every unit:
   the durations file is read by every test's conftest. The selection holds tests/test_gate_durations.py,
   test_gate_shards.py and test_suite_tail.py, which catch S1–S6.
10. N.A.: no Lean.
11. PASS: the size caps fail closed to the committed durations
    (`test_a_record_file_larger_than_the_limit_is_not_read`, `…[seconds over MAX_RECORD_BYTES]`, `…[nested 100k deep]`). There are no
    sleeps or timeouts in the new tests.
12. N.A.: no checker path changed. The gate reads one file of at most 16 MiB once.
13. N.A.: no test removed or renamed.
14. PASS:
    - Opposite directions: file used vs not used; note vs file; under vs over the limit; complete vs incomplete
      timing; good vs malformed in the gate.main test.
    - Each claim above cites its command.
    - Spec re-read: "uses it ONLY when base_durations finds none" against tools/gate.py:675-684. "read with
      read_record_field (MAX_RECORD_BYTES applies)" against tools/gate.py:663. "missing, unreadable or malformed
      leaves the committed durations; log one line, never fail" against tools/gate.py:658-666 and
      `test_a_missing_…[*]`. "measured must not change which tests run" against
      `test_a_durations_record_changes_only_the_plan`. "each test's longest time across the inputs; source line says
      which records" against tools/bench/suite_tail.py:181-210.
