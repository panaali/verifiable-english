# lw-allowances-shared: docs/kernel/ALLOWANCES.md is rebase-second, with a resolver

- Status: built and staged as `.new-lwas` in `/home/seyran/code/manage-agents`. INSTALL WAITS FOR DECIDER READ (the
  commands are at the end). No DELTA rows. No DRI signature is reserved. Trust +0.
- What changed:
  1. `path_overlap.py` gets rule 3a. When the running branch's diff to `docs/kernel/ALLOWANCES.md` is append-only, the
     file is rebase-second. Append-only means: table rows added at the end of a table, plus the `signed total:` line, with
     the total following the rows. Anything else keeps the file serial.
  2. A new resolver, `tools-local/allowances_merge.py`, is called first in `regen_merge`. Both `merge-train.sh` and
     `presync-watch-job.sh` call it, so it covers every sync site: syncbranch, the post-agent rounds, the queue's re-sync
     at line ~1469, and the presync job. Its result is main's file plus the branch's appended rows, with signed total =
     main's total + (branch total - merge-base total). If the branch's change has any other shape, the resolver refuses
     and logs why, and the merge goes to the agent sync as before.
- Tests: `tools-local/test_allowances_shared.py` has 18 tests. 17 fail on the installed code and all 18 pass on the staged
  code. The one that passes on the installed code is `test_resolver_missing_keeps_the_file_serial`, which is today's
  behaviour by design. The existing path_overlap, feed, presync and merge-train harnesses give the same results on the
  staged code as on the installed code (table below).
- This VE branch holds only this report and its evidence. No VE product code (Lean, Python or Rust) changed.

SIZE: 311 product (allowances_merge.py 267 new; path_overlap.py +24; merge-train.sh +12; presync-watch-job.sh +8), 296
tests (test_allowances_shared.py, new), 1 other hand-written file (this report; replay.py.txt is a probe;
seeded-bugs.json, the logs and live-changes.diff are records).

Row: lw-allowances-shared (infra, critical path, pinned 2026-11-23T16:00Z). Decision
`reviews/dri-decisions-20261115-lw-allowances.md` item 1. Task `prompts/task-lw-allowances-shared.txt`.

## Deliverables

| # | Task line | Where (staged) | Test |
|---|---|---|---|
| 1 | path_overlap: ALLOWANCES.md joins the rebase-second class, so two branches that both edit it no longer hold each other's path lock, provided each branch's diff is append-only table rows plus the `signed total:` line | `tools-local/path_overlap.py.new-lwas` rule 3a: `classify` calls `allowances_merge.branch_shape` | `test_path_overlap_check_no_longer_reports_append_only_branches` (`check` prints `rebase-second`); `test_two_append_only_branches_...` (both branches classify rebase-second) |
| 1 | A branch that edits or deletes an existing table row (or anything else in the file) stays serial | `allowances_merge.analyse` (the base rows must be an unchanged prefix of each table; other text unchanged; no table added or removed) | `test_branch_editing_an_existing_row_is_serial_and_refused`; Shapes: `test_deleted_row_refused`, `test_row_inserted_before_the_end_refused`, `test_pre_signed_row_removed_refused`, `test_text_outside_tables_refused`, `test_new_table_refused`, `test_two_total_lines_refused` |
| 2 | Resolver used by presync and the merge train: main's file + the branch's appended rows | `allowances_merge.py resolve --repo W --commit`, called by `amerge` in `merge-train.sh.new-lwas` and in `presync-watch-job.sh.new-lwas`, both at the start of `regen_merge` and again after its handshake re-merge | `test_two_append_only_branches_rebase_second_with_both_rows_and_summed_total` (merge-train's own `regen_merge`, library mode); `test_presync_job_resolves_the_same_conflict` (the real presync job, `refs/ve-presync/kb-y`) |
| 2 | A row already on main is not duplicated | `resolve`: compares against the rows main added since the merge base. In the kernel table every cell but "Total after" must match; in the other tables the whole row | `test_duplicate_appended_row_is_not_doubled` (kernel row and Ownership-floor row) |
| 2 | signed total = main's total + (branch total - merge-base total) | `resolve` (`want`, checked against the renumbered running total) | `test_two_append_only_...` (9,966 + 10 + 5 = 9,981); `test_fall_is_append_only_and_summed` (9,976 - 135) |
| 2 | Change not of that shape: the resolver refuses, the item falls back to the serial path and says why; never guess | `cmd_resolve` exit 1 with `refused: <why>`. The file stays as git left it. `amerge` logs the line (merge-train.log / presync-watch.log), the generated-file resolve declines and the agent sync runs | `test_branch_editing_...` (resolver exit 1, file still unmerged, train `regen_merge` != 0, `refused` in merge-train.log); `test_total_not_matching_branch_delta_is_refused` |
| T | A total that does not match the branch delta arithmetic is refused | `analyse`: branch total - base total must equal the sum of the appended kernel rows' Lines, and each appended row's Total after must follow | `test_total_not_matching_branch_delta_is_refused`; `test_total_after_not_following_lines_refused`; `test_total_raised_without_a_row_refused` |
| T | Each fails on the installed code | - | `run-live.log`: `FAILED (failures=17)` of 18 |
| T | Existing path_overlap / presync / merge-train harness tests stay green | - | table below |

## Readings I took (the conservative option each time; I did not ask)

- **Which tables.** The file has three tables: the kernel table, "Pre-signed" and "Ownership floor". A row may be appended
  to the end of any of them. A removed row is refused. This includes a used pre-signed row (KB-1) that a branch deletes:
  that branch stays serial. A branch that adds a new table is refused too. In the history replay, kb-10d added the
  Ownership-floor table, and both of its merges are refused.
- **Delta arithmetic.** The kernel table is the one whose header has "Lines" and "Total after". The branch's total change
  must equal the sum of its appended kernel rows' Lines, and each of those rows' Total after must equal the previous total
  plus its Lines. The chain starts at the merge base's signed total. A branch that appends only Ownership-floor rows must
  leave the total unchanged.
- **"Total after" is renumbered in the result.** The branch's appended kernel rows get Total after = main's total plus
  the running Lines. This is the same arithmetic as the signed total, applied row by row. It is what the humans did by hand
  in every historical merge I replayed (for example b7ca4aeca9 has kb-10c's row at 10,083 in both). Without it, the column
  would contradict the signed total after every rebase-second merge. Row text is never changed apart from that cell.
- **Duplicates** are checked only against rows that main added since the merge base (a multiset difference). A dropped
  duplicate kernel row also drops its Lines from the sum: total = main + delta - Lines of the rows main already has. Any
  other result would count that rise twice.
- **Lock time vs. sync time.** At lock time path_overlap can only see the running (holder) branch's diff. The waiting
  item's own diff is checked by the resolver when it syncs. If that diff is refused, the item goes to the agent sync, the
  path it took before this change, and `allowances resolve in <wt>: refused: <why>` is logged. The pair guard
  (REBASE-SECOND-SERIAL, rule 1) is still applied first, so two failed syncs put the file back to serial
  (`test_path_overlap_check_...` checks that the guard wins).
- **Missing resolver = old behaviour.** If `allowances_merge.py` is not next to `path_overlap.py`, the file stays serial
  (`test_resolver_missing_keeps_the_file_serial`). If it is not at `$M/tools-local/`, `amerge` does nothing. The
  existing harnesses run without it and stay green.
- **The gate still decides.** After a resolved merge, `tests/test_kernel_closure.py` still requires
  `signed total == closure-baseline.json kernel_lines` on the merged tree. If two rises overlap so that the measured
  merged figure is not the sum, the candidate gate fails and the item goes to verify-fix, as it would after a hand
  merge. The resolver never re-measures.

## Test runs (2026-11-16, manage-agents, `python3 -I` / zsh, foreground)

| Run | Command | Result |
|---|---|---|
| New tests, staged | `python3 -I tools-local/test_allowances_shared.py` (default `LWAS_SFX=.new-lwas`) | `Ran 18 tests ... OK` (`run-staged.log`) |
| New tests, installed | `LWAS_SFX= python3 -I tools-local/test_allowances_shared.py` | `FAILED (failures=17)`: every test but `test_resolver_missing_keeps_the_file_serial` (`run-live.log`) |
| path_overlap unit tests, staged | `test_path_overlap.py` run in a temp dir with `path_overlap.py.new-lwas` as `path_overlap.py` and the resolver beside it | `Ran 17 tests ... OK` |
| Feed harness, staged path_overlap | `OVERLAP_PY=<tmp>/path_overlap.py zsh test-harness/feed/test-feed.zsh $PWD/feed-features.sh` | `116 passed, 6 failed` |
| Feed harness, installed | `zsh test-harness/feed/test-feed.zsh $PWD/feed-features.sh` | `116 passed, 6 failed`: the same 6 `urgent:` cases. They fail on the installed code too and are not touched by this change (Notes) |
| presync-watch harness, alone | `PW_SFX=.new-lwas zsh test-harness/presync/test-presync-watch.zsh` | `38 passed, 0 failed` |
| presync-lean-regen harness (sources merge-train.sh) | `PW_SFX=.new-lwas zsh test-harness/presync/test-presync-lean-regen.zsh` | `31 passed, 0 failed` |
| pwtake harness | `PS_NEW=1 PS_NEW_SFX=.new-lwas zsh test-harness/presync/test-pwtake.zsh` | `10 ok, 0 FAIL` |
| apply1017 harness (regen_merge paths) | `PS_NEW=1 PS_NEW_SFX=.new-lwas zsh test-harness/ps1014/harness/test-apply1017.zsh` | `22 passed, 0 failed` |
| Merge-train harness | `PS_NEW=1 PS_NEW_SFX=.new-lwas zsh test-harness/ps1014/harness/test-mq.zsh` | `57 passed, 0 failed` (3 min 23 s) |
| History replay (probe, not a test) | `python3 -I docs/infra/lw-allowances-shared/replay.py.txt` in this worktree | `replay-history.txt`: 5 historical ALLOWANCES.md merges resolved, each with the signed total the humans committed (9,966; 10,101; 10,083; 10,023; 10,015). 2 were refused (kb-10d added a table) |
| Selected VE tests | `MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on the committed HEAD | see "Selected run" below |

## Seeded bugs (`seeded-bugs.json`; all 8 CAUGHT)

Each seed was applied to a temp copy of the staged file and run with `LWAS_SFX=.seed` and the named test. The staged
files were never edited.

| Id | File (manage-agents) | Change | Failing test |
|---|---|---|---|
| S1 | tools-local/allowances_merge.py.new-lwas | signed total = branch total, not main + delta | `test_two_append_only_branches_..._summed_total` |
| S2 | tools-local/allowances_merge.py.new-lwas | the prefix check only counts rows (an edited row passes) | `test_branch_editing_an_existing_row_is_serial_and_refused` |
| S3 | tools-local/allowances_merge.py.new-lwas | duplicate rows are appended again | `test_duplicate_appended_row_is_not_doubled` |
| S4 | tools-local/allowances_merge.py.new-lwas | the delta arithmetic check is off | `test_total_not_matching_branch_delta_is_refused` |
| S5 | tools-local/path_overlap.py.new-lwas | rule 3a never matches | `test_path_overlap_check_no_longer_reports_append_only_branches` |
| S6 | merge-train.sh.new-lwas | `regen_merge` does not call `amerge` | `test_two_append_only_branches_..._summed_total` |
| S7 | presync-watch-job.sh.new-lwas | `regen_merge` does not call `amerge` | `test_presync_job_resolves_the_same_conflict` |
| S8 | tools-local/allowances_merge.py.new-lwas | Total after is not renumbered | `test_two_append_only_branches_..._summed_total` |

Python and zsh are the only languages whose product code changed, and each has a seed. The resolver's last check
(`want` == the renumbered total) is a second line of defence. With S4 alone it still refuses the merge. S4 is caught by
the classify half of its test.

## Spec re-read

- "append one table row, raise the signed total line ... any two kernel rows conflict on one line" against decision item 1
  and the task WHY: the fixtures do exactly that (`doc()`, rows RX/RY), and `conflicted()` asserts that git conflicts.
- "union of both sides' appended table rows, signed total = main's total + (branch total - merge-base total)" against
  decision item 1: `resolve` builds main + the branch rows. `want = total + (otot - btot) - dup_lines`, where the last
  term is the not-duplicated rule from task (2).
- "A branch that edits or deletes an existing table row (or anything else in the file) stays serial" against task (1):
  `analyse` refuses each case, and each has its own test.
- "the resolver refuses (the item falls back to the serial path and says why); never guess" against task (2): exit 1, one
  `refused:` line, the file left unmerged, and the line logged by `amerge`.

## Notes for the DRI

- The 6 `urgent:` failures of `test-feed.zsh` (feed-features.sh's urgent-row cases) also fail with the installed
  path_overlap.py. They are not in this change's code.
- `merge-train.sh.new-fdre` is byte-identical to the installed `merge-train.sh`, so it does not compete with
  `merge-train.sh.new-lwas`. `merge-train.sh.new-amf2.orig` (2026-11-02) is an old `.orig` snapshot, not a staged
  install. No other `.new-*` copy of the four files exists (`ls merge-train.sh.new* presync-watch-job.sh.new*
  tools-local/path_overlap.py.new*`).
- The queue's merge-tree conflict test (`qfirst`, mkcand) still treats two kernel candidates as conflicting. The second
  one waits for the first to publish, then syncs through this resolver. That wait is the queue's, not the path lock's,
  and the task did not ask for it. Folding the resolver into merge-tree would need a custom merge in `$R`.
- The resolver commits the merge with git's default message (`--no-edit`), the same way regen_merge does.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer or relay is involved (control-plane tooling).
2. PASS: each task line is mapped to its code and test in the Deliverables table. No new copy of a Lean decision. The
   shape rule lives only in `allowances_merge.py`, and path_overlap imports it. No permanent report test is added.
3. PASS: 8 seeded bugs, all caught (`seeded-bugs.json`). 17 of 18 new tests fail on the installed code (`run-live.log`).
4. N.A.: no Python/Lean/Rust checker path. The history replay (`replay-history.txt`) is the real-data check of valid
   inputs: 5 of 5 append-only merges give the hand-committed totals.
5. N.A.: no Lean answer fields. The resolver's input binding (the table is matched by its exact header, which must occur
   once on main) is tested by `test_main_without_the_table_refused`.
6. PASS: the selected run is made on the committed HEAD (below). The full gate is run by the chain, not by me.
7. PASS: no DELTA row and no trust growth. No signature is reserved. The resolver's exit codes 0/1/2/3 are tested for 0
   (`test_two_append_only_...`) and 1 (`test_branch_editing_...`). Code 3 (not conflicted) is the `amerge` no-op that the
   existing harnesses run through.
8. N.A.: no VE user-visible output changed (DELTA: none, as the task says).
9. PASS: this branch changes only `docs/infra/lw-allowances-shared/`. The selected run is below.
10. N.A.: no Lean.
11. PASS: no budgets. The resolver fails closed: every unknown shape is refused (Shapes tests). The tests use no sleeps
    or wall-clock asserts (subprocess timeouts of 300-600 s only as hang guards).
12. N.A.: one Python call per conflicted merge, and only when ALLOWANCES.md is unmerged (otherwise exit 3 after two git calls).
13. N.A.: no test removed or renamed.
14. PASS: both directions are tested. Accept: `test_ownership_row_with_unchanged_total_is_append_only`,
    `test_fall_is_append_only_and_summed`, `test_two_append_only_...`. Refuse: the 8 refusal tests. Each claim here cites
    a command and log, and the spec re-read is listed above.
15. PASS: no overclaim (each "every"/"all" above names its test or log). No deliverable cut. Every new check has a seed
    (S2, S4, S5). Limits: N.A. (no limits).

## Install (INSTALL WAITS FOR DECIDER READ)

Live sha256 the staged copies were made from (check these first; a mismatch means the live file moved and the copy must
be rebased):

    68244abb0731cccf884245c320ba9bf16a7f3eefd7a85c87bae0ca9ed1cb477c  merge-train.sh
    461260b257ef11f1a9f2b3fe1f45c51b7c5a5ca73fe273b4ce643330c859d344  presync-watch-job.sh
    11298b7a415a3c770ce2d6d0efb185715368d2a60162554ed6f2c44fac2d91f5  tools-local/path_overlap.py

Staged sha256:

    28b4f9a798b4fdd00bd6bd30e9196f1d19513485f9ab4f32e0901a21e1ff27a2  merge-train.sh.new-lwas
    15bb21576dc581a51136a99034422994c4a31386d9ca363aab08d97990aa6792  presync-watch-job.sh.new-lwas
    512c1f28481bf50a46b742fb3fc8dacebaabd89397285b3135456032d51df86b  tools-local/path_overlap.py.new-lwas
    87b1896adb3ffd7902ec86cf8a1f6c0defbdb4fa88dee599ee2afdc7f51eea23  tools-local/allowances_merge.py.new-lwas

Commands (in /home/seyran/code/manage-agents):

    cd /home/seyran/code/manage-agents
    sha256sum merge-train.sh presync-watch-job.sh tools-local/path_overlap.py   # must equal the three live lines above
    for f in merge-train.sh presync-watch-job.sh tools-local/path_overlap.py; do cp -p $f $f.bak-20261116-lwas; done
    mv tools-local/allowances_merge.py.new-lwas tools-local/allowances_merge.py    # first: path_overlap and amerge look for it
    mv tools-local/path_overlap.py.new-lwas tools-local/path_overlap.py
    mv presync-watch-job.sh.new-lwas presync-watch-job.sh
    mv merge-train.sh.new-lwas merge-train.sh
    python3 -I tools-local/test_allowances_shared.py          # 18 OK on the installed files (no .new-lwas left)

Restart: none. `path_overlap.py` is run fresh by `feed-features.sh` on each pass (svc-feature-feed). `presync-watch-job.sh`
is started fresh per job by `presync-watch.py` (svc-presync-watch). `merge-train.sh` is executed fresh per train. A train
already running keeps the file it opened (`mv` gives a new inode). Remote presync lean regen hosts get the new
merge-train.sh by sha automatically (presync-watch-job.sh copies it when the sha differs). Rollback: `mv` each
`.bak-20261116-lwas` back and `rm tools-local/allowances_merge.py`.
