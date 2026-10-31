# actions-suspend-per-item (2026-10-31): Actions suspends only on misses from 2 distinct items; the probe reruns a known-good job

Status: built and installed in manage-agents, which is not a git repository. This branch carries only this report. The first
round's report is reviews/actions-suspend-per-item-20261031.md (manage-agents). This file records the fix round for
review actions-suspend-per-item-review.final.md (F1 B, F-ready1 B, and the C findings F2 to F5).
Signature: none needed. There is no VE product code, no DELTA row and no Ruling cell.

## Fix round (all in /home/seyran/code/manage-agents)

Each edited file went through `.new`, `py_compile` or `zsh -n`, a line-count and diff check, a backup
`.bak-20261031-actions-suspend-per-item-fix`, then `mv`. One live `cloud-overflow.sh run` (ap-3d) was reading the old
file, and it keeps the old inode. The change to cloud-overflow.sh is comments only.

- **F1 (B), the class "names of one item's jobs":** `actions-health.py` has one table, `ALIAS`
  (`(?:\.(?:r\d+|s\d+of\d+))+$`). It strips every alias suffix an item's jobs take, in either order and repeated: a rerun of
  a tree that returned a result (`<item>.r<k>`, cloud-overflow.sh L145) and a shard part (`<item>.s<k>of<n>`, tm-shard.sh).
  For example, `X.r2.s1of3` is `X`. `itemkey` is the only place that names an item. All four uses read it: the upgrade of an
  old state file, the miss streak, `probejob`'s set of excluded items, and the probe candidates. A grep of
  manage-agents' `*.py`/`*.sh` (backups excluded) finds no other parser of these suffixes.
- **F4 (C, same class):** a probe job (job.json `probe_src`) is keyed as the item of the job it reran. When that job.json is
  gone, the key comes from the source job's name. Recursion stops at depth 8. An old probe of the failing item's tree is
  therefore excluded from `probejob`. A probe of a known-good tree can still be picked.
- **F3 (C):** the streak keeps `max(5, ACTIONS_MISS_LIMIT)` items and jobs, so a limit above 5 can still suspend.
- **F2 (C):** a new test checks that an old state file's streak item (ap-4a) and a first new miss from another item (pc-3)
  suspend at once.
- **F5 (C):** the comments at `cloud-overflow.sh:33` and `actions-probe.sh:4` now describe the distinct-items rule.
- **F-ready1 (B):** this commit. The branch had 0 commits ahead of main, because the change lives outside the VE repo.

## Evidence

`python3 -I tools-local/test_actions_suspend.py`: `Ran 22 tests ... OK` on the installed files (11 before, 11 added). Run
against the installed scripts from before this round, 9 of the new tests fail. The F2 test passes there by design, because
it targets a mutant.

PROBE F1 (the review's command): before the fix it printed
`['ok', 'suspend 2 Actions jobs in a row without a result, from 2 items (df-1bbb.r2, df-1bbb.r3)']` and failed its
assertion. After the fix it prints `['ok', 'ok']` and exits 0. Its regression test is
`Reruns.test_two_reruns_at_one_snapshot_do_not_suspend`.

| Finding | Claim | Test (tools-local/test_actions_suspend.py) |
|---|---|---|
| F1 | X.r2 and X.r3 at one snapshot are one item | Reruns.test_two_reruns_at_one_snapshot_do_not_suspend |
| F1 | X.r2, then X at a new commit, are one item | Reruns.test_rerun_then_item_at_a_new_commit_does_not_suspend |
| F1 | shard parts of a rerun (X.r2.s1of3, parent gone; part of parent X.r3) and X.s2of3 are one item | Reruns.test_shard_parts_of_a_rerun_are_the_item |
| F1 | a job without an `item` field is keyed by its job name, suffix stripped | Reruns.test_rerun_without_item_field_keys_by_job_name |
| F1 | opposite direction: a rerun and another item still suspend | Reruns.test_rerun_and_another_item_still_suspend |
| F1 | the upgrade of an old state file keys a rerun as its item | Streak.test_old_state_file_rerun_is_its_item |
| F1 | probejob skips a rerun's result of the failing item | Probe.test_probejob_skips_a_rerun_of_the_failing_item |
| F4 | probejob skips an old probe of the failing item's tree (source present, and source gone) | Probe.test_probejob_skips_an_old_probe_of_the_failing_items_tree |
| F4 | opposite direction: a probe of a known-good tree is still a candidate | Probe.test_probejob_takes_a_probe_of_a_known_good_tree |
| F3 | ACTIONS_MISS_LIMIT=7 suspends on the 7th distinct item, not before | Streak.test_limit_above_five_suspends |
| F2 | an old state file's item and a first miss from another item suspend at once | Streak.test_old_state_file_item_counts_against_another_item_at_once |

## Seeded bugs (Python, actions-health.py; each was run on a temp copy and the installed file was left unchanged)

| Mutant | Failing tests |
|---|---|
| upgrade loop replaced by `for j in []` (F2) | Streak.test_old_state_file_item_counts_against_another_item_at_once |
| `ALIAS` without `r\d+` (F1) | all 5 Reruns tests, Streak.test_old_state_file_rerun_is_its_item, Probe.test_probejob_skips_a_rerun_of_the_failing_item, Probe.test_probejob_skips_an_old_probe_of_the_failing_items_tree |
| `ALIAS` strips one suffix only (`?` for `+`) | Reruns.test_shard_parts_of_a_rerun_are_the_item |
| the `probe_src` branch dropped (F4) | Probe.test_probejob_skips_an_old_probe_of_the_failing_items_tree |
| `keep = 5` (F3) | Streak.test_limit_above_five_suspends |

The live check was read-only: `actions-health.py probejob` on the newest live job still picks qt-a3cb-7b7470ef. The live
`actions-health.json` (1 miss, old format without `items`) is upgraded on its next miss, as before.
