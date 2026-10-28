# tm-shard: trust_mutants --shard K/N, --merge and --plan

Status: built and verified; ready for the chain's gate. No DRI signature is needed (tooling, no DELTA row).
Changed: tools/trust_mutants.py and tests/test_trust_mutants.py only (Python). No Lean, Rust, trust, wire or ve/ change.
Proof on real Lean (q1-4, 30 mutants run): three parts merged equal the unsharded record (empty diff), and the
unsharded record equals main's tool byte for byte apart from `seconds` and `inputs.tool`.
Open: none. Not run here: the full gate (the chain runs it), trust_mutants on the Mac (no trusted Lean changed).

## What it does

- `--shard K/N`: part K owns the mutants of `run_now` whose id M<i> has (i - 1) % N == K - 1 (`owns`). It builds and
  judges only those (--rescore and the control build too). Its record gets `shard: {k, n, owned}`, and lists every
  mutant another part owns as `OTHER SHARD` (status and raw_status, counted under its own key). It prints only its
  own SURVIVOR/UNKNOWN lines. A bad K/N exits 2 with one line.
- `--merge OUT.json PART.json...`: reads only the parts and writes `record(...)`, the same function a run writes
  with, so key order and rows match by construction. The run facts differ: `seconds` is the max of the parts',
  `jobs` the sum, plus `shards: [{k, n, jobs, seconds}]`. It prints an unsharded run's lines and exits with its
  rule. It refuses (exit 2, one line) every disagreement and ownership fault listed in the task.
- `--plan`: one JSON line `{base, definitions, mutants, to_run, not_run}` (plus `owned` with --shard), with no
  scratch, build or Lean run. Measured: 6.9 s wall on q1-4 (44 mutants), 12.3 s on qt-a3b (127 mutants), uv start
  included.

## Proof on real Lean (step 5)

Item q1-4: head 50dae2a8b, merge base ab010c3f02bc (`--plan` gives 4 definitions, 44 mutants). I ran it at
`--max-mutants 30`, so 30 run and 14 are NOT RUN, which also checks that every part lists the NOT RUN mutants
identically. The other recent items had 0 trusted mutants (me-12nb, df-2b, me-2n, sc-5r, me-12n, sc-1bb, me-12ab,
df-1b), or 51 and more (qt-a3b 127, ap-1be 51, df-2 69, me-5d 126, ap-3b 214, jt-2 408, ap-2b 1187).
Checkout: a detached worktree of 50dae2a8b. Every run used `nice -n 10 ... --jobs 4`, one after another.

    uv run python tools/trust_mutants.py --root <q1-4 checkout> --base ab010c3f02bca97c3d17775ba85382bf85e208eb \
        --max-mutants 30 --jobs 4 [--shard K/3] --json docs/tm-shard/<name>.json
    uv run python tools/trust_mutants.py --merge docs/tm-shard/merged.json docs/tm-shard/part-{1,2,3}-of-3.json

| run | file | mutants built | seconds | verdicts | VM load (1 min, end) |
|---|---|---|---|---|---|
| main's tool, unsharded | before.json | 30 | 5,763 | 30 KILLED, 14 NOT RUN | up to 90 |
| this tool, unsharded | unsharded.json | 30 | 3,733 | 30 KILLED, 14 NOT RUN | 29 |
| part 1/3 | part-1-of-3.json | 10 | 2,945 | 10 KILLED, 14 NOT RUN, 20 OTHER SHARD | 76 |
| part 2/3 | part-2-of-3.json | 10 | 1,805 | 10 KILLED, 14 NOT RUN, 20 OTHER SHARD | 20 |
| part 3/3 | part-3-of-3.json | 10 | 2,237 | 10 KILLED, 14 NOT RUN, 20 OTHER SHARD | 18 |
| merge | merged.json | 0 | 0.47 s wall | 30 KILLED, 14 NOT RUN (exit 3, as unsharded) | |

The diff, with seconds, jobs and shards dropped:

    jq -S 'del(.seconds,.jobs,.shards)' docs/tm-shard/unsharded.json > /tmp/u.json
    jq -S 'del(.seconds,.jobs,.shards)' docs/tm-shard/merged.json > /tmp/m.json
    diff /tmp/u.json /tmp/m.json && echo jq-diff-empty
    -> jq-diff-empty
    tm.evidence(text without seconds, jobs, shards) of both: equal (90,904 bytes); key order equal: True
    printed lines of --merge and of the unsharded run, without the header and the seconds: equal

No verdict differed, so the noise rerun was not needed. Unchanged unsharded record: before.json (main's tool) and
unsharded.json (this tool) are byte-identical once `seconds` and `inputs.tool` are replaced (90,932 bytes each).
`inputs.tool` is the digest of the tool's own source, so it must change with any edit of the tool. Because of it, a
record from before this change used as --rescore PREV gives a full run ("its inputs differ (tool)"), the same as
after any edit of the tool.

Merged record as --rescore PREV on real Lean: unsharded.json and merged.json, each copied to the same PREV path, give
"30 reused from 50dae2a8be77 (identical inputs)", 0 to run, and records equal without their run facts.

Per-part overhead (the control: scratch copy, control `lake build`, probe install, the checks' probes). I measured it
separately with docs/tm-shard/control-seconds.py.txt, which repeats main's control section for each part's mutants:

| part | targets | check files | control s (copy / build / probe) | load | share of its run |
|---|---|---|---|---|---|
| 1/3 | 5 | 4 | 724 (11 / 0 / 713) | 34 | 25% of 2,945 |
| 2/3 | 5 | 4 | 501 (6 / 0 / 494) | 24 | 28% of 1,805 |
| 3/3 | 3 | 3 | 577 (2 / 0 / 574) | 19 | 26% of 2,237 |
| whole run | 5 | 4 | 413 (3 / 0 / 410) | 14 | 11% of 3,733 |

On this item every part pays nearly the whole control: about 400-700 s here, almost all of it each check file's
probe elaboration. The control `lake build` is 0 s on a built tree; on a cloud part it also pays the branch's
incremental build. The runs were made at different VM loads (14-90), so the seconds are only rough.

## Tests (tests/test_trust_mutants.py, no Lean: `plan`, `run`, `Scratch`, `Reads`, `install`, `targets` and `inputs` stubbed)

- test_a_shard_owns_a_disjoint_stable_part_of_the_mutants_that_run: N = 1..5, every K: the owned list follows the
  rule, it is disjoint, covers run_now and is the same on a second call, the sizes differ by at most 1, only owned
  mutants are run and control-built, the rest are OTHER SHARD or NOT RUN
- test_a_shard_that_is_not_k_of_n_stops_the_run (11 cases, Unicode digits included): exit 2, one line, nothing built
- test_the_parts_merged_are_the_one_runs_record[(N, max)]: (1,6) (2,6) (3,6) (9,6: empty parts) (2,1) (3,0): the
  bytes equal without the run facts, the same printed lines and exit code, shards/jobs/seconds as specified
- test_merge_refuses_parts_that_are_not_one_runs (32 cases): every refusal, with one stderr line and no OUT written
- test_merge_refuses_an_unreadable_part_or_no_part
- test_rescored_parts_merge_to_the_rescored_run: reused/rerun summed; mode, head, file, changed and full_run refused
- test_a_merged_record_is_a_rescore_prev_as_the_one_runs_is
- test_plan_prints_the_counts_and_builds_nothing

Selected tests: `zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` at 30e933de: 130 units,
exit 0, 0 failed (ve-mac-1, 892 s). `uv run python tools/regen_generated.py --check`: 33 entries, clean.

## Seeded bugs (Python; docs/tm-shard/seeded-bugs.json)

| id | file | bug | failing test |
|---|---|---|---|
| S1 | tools/trust_mutants.py | `owns`: (i) % N instead of (i - 1) % N | test_a_shard_owns_a_disjoint_stable_part_of_the_mutants_that_run |
| S2 | tools/trust_mutants.py | merge takes every row from part 1 | test_the_parts_merged_are_the_one_runs_record[2-6] |
| S3 | tools/trust_mutants.py | owned-twice refusal dropped | test_merge_refuses_parts_that_are_not_one_runs[owned-twice] |
| S4 | tools/trust_mutants.py | --plan to_run counts the part's mutants | test_plan_prints_the_counts_and_builds_nothing |
| S5 | tools/trust_mutants.py | --rescore in a part reuses other parts' mutants | test_rescored_parts_merge_to_the_rescored_run |
| S6 | tools/trust_mutants.py | merged seconds summed, not the max | test_the_parts_merged_are_the_one_runs_record[2-6] |

S6 first went uncaught: every stubbed part ran in 0 s, so the sum equalled the max. The test now gives each part
distinct seconds, and S6 fails it.

### Fix round 1 (review F1, F2)

F1: `--merge` read a part's rows without checking them, so a null status vanished from the counts and a non-text
detail crashed the printing. Now each part must be a record this tool writes (`unread`): the fields `record`
copies of their types (`PART`, `SHARD`, `RESCORE`), each row of `ROW`'s fields and types (from `Mutant`), with a
status it writes and the raw_status that status allows (`unwritten`), and its counts, counts by class and
definitions what `record` makes of its rows. Comparisons between parts are of JSON texts (`canon`), so `true` is
not `1`. `--rescore` PREV reads its rows with the same `unwritten`.

F2: a part's rows past --max-mutants were copied into the merge unchecked, so NOT RUN rows turned KILLED gave
exit 0. Now every row a part does not run, OTHER SHARD or NOT RUN, must be exactly the plan's row with that status
(`idle`). Tests: `test_merge_refuses_a_part_this_tool_does_not_write`,
`test_merge_refuses_a_verdict_on_a_row_a_part_does_not_run`, `test_rescore_of_evidence_whose_mutants_differ_is_a_full_run`.

| id | file | bug | failing test |
|---|---|---|---|
| S7 | tools/trust_mutants.py | `typed`: a bool taken for an int | test_merge_refuses_a_part_this_tool_does_not_write[row-line-True] |
| S8 | tools/trust_mutants.py | status not checked against STATUSES | test_merge_refuses_a_part_this_tool_does_not_write[row-status-raw-PASSED] |
| S9 | tools/trust_mutants.py | counts not compared with the rows' | test_merge_refuses_a_part_this_tool_does_not_write[derived-counts] |
| S10 | tools/trust_mutants.py | a row not run checked by status only | test_merge_refuses_a_verdict_on_a_row_a_part_does_not_run[M007-detail] |
| S11 | tools/trust_mutants.py | options compared with `==` | test_merge_refuses_parts_that_are_not_one_runs[inputs-bool-for-int] |
| S12 | tools/trust_mutants.py | raw_status ALLOWED accepted | test_merge_refuses_a_part_this_tool_does_not_write[row-allowed-raw-allowed] |
| S13 | tools/trust_mutants.py | --rescore rows not checked by `unwritten` | test_rescore_of_evidence_whose_mutants_differ_is_a_full_run |

S8 and S11 first went uncaught (a null status already failed its type; the third part lacked the changed input);
the cases now set a typed unknown status and the input in every part.

## DELTA

None. This is builder tooling: no VE language, verdict, wire or product change, so no row and no signature.
