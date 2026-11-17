# notask-wait-alert: ready rows with no task file get their own alert and their own bottleneck cause

- Status: built and staged in `/home/seyran/code/manage-agents/tools-local` as `decider-ready-alert.py.new-nta` and
  `bottleneck-scan.py.new-nta`. INSTALL WAITS FOR THE DRI'S INSTALL READ (sent by the build round:
  `inbox/dri/20261117T123455Z-notask-wait-alert-1080382.md`; the review F1 fix below changes only the staged scan, and the
  install steps are unchanged, section 5).
- No DRI signature is reserved and there are no DELTA rows: this is control-plane tooling, with no VE trusted line and no
  verdict rule changed. Trust +0.
- This VE branch holds only this report and its evidence (`staged-changes.diff`, `review-f1.diff`, `seeded-bugs.json`,
  `run-*.log`, `probe-f1.log`). No VE product code (Lean, Python or Rust) changed. Before the fix round the branch had no
  commit at all (review-ready `[commits]` FAIL, F-ready1); this record is the branch's content, as for tm-drain-vm1-idle.

## 1. The build round (summary of `manage-agents/notask-wait-alert-build.final.md`)

- Root cause: `bottleneck-scan.py` never read `infra-feed.log`, so the infra feed's "no task file and no launch link" WAITs
  counted under no cause, and `resource:accounts` became the binding on the hours it already had (picker waits plus the
  feature feed's account waits). In the bucket table "task file" came last, after the bare `account` pattern, so
  "task file missing (prompts/task-account-fix.txt)" went to accounts.
- Scan fix: `infra-feed.log` WAIT/LAUNCH/RECONCILE lines are read for the no-task spans only; "no task file" is the first
  bucket; accounts match the whole word `account`; a new `process:no-task-file` cause competes in `classify` and is never
  added to accounts.
- Alert fix: ready rows with priority above 1 and no task file are named once per (id, ready time) after 20 min in the
  same "NOW(critical): " message; p1 rows stay with the p1 rule (4 h dedup unchanged).
- Tests: `tools-local/test_decider_ready_alert.py` (NoTaskFile 1-4, test_p1_rows_left_to_p1_rule),
  `tools-local/test_bottleneck_scan.py` (test_6, test_7, test_buckets, test_no_infra_log_no_cause),
  `tools-local/test_p1_ready_alert.py` (test_non_matching_rows_silent adapted).

## 2. Review F1 (B): the capacity hint still named the old bucket key

Finding: the bucket was renamed `"task file"` -> `NO_TASK` (`"no task file"`), but `stage_details` still excluded
`("prerequisites", "task file")`, so no-task row-hours showed as `feed capacity waits (row-h): no task file 169.0` in the
`stage:launch-wait` note (BOTTLENECK.md, the jsonl, and `--alert` when launch-wait is binding or runner-up).

The class: a reader that names a feed bucket by a string literal drifts from the bucket table on any rename. Fix
(structural, `review-f1.diff`):
- Every bucket a reader names is a constant defined next to the table: `NO_TASK, PREREQ, ACCOUNTS, MAC_LOAD, VM_LOAD`; the
  table itself uses them.
- `NOT_CAPACITY = frozenset({NO_TASK, PREREQ})` is the one list of buckets that are a missing input, not a capacity limit;
  `stage_details` reads it. A name in it that is no bucket stops the scan at import.
- The sweep found a second literal reader of the same class, `fw.get("VM load", 0)` in `resources` (correct today, but it
  would break on a rename); it now reads `VM_LOAD`. `fw.get("Mac load")` and `fw.get("accounts")` likewise read
  `MAC_LOAD` and `ACCOUNTS`. The alert script has no bucket names; nothing else in tools-local reads `feed_waits_h`.
- Outside the scan, `reviews/ops-width/q3.py` (a one-off analysis script of the 11-14 ops-width review, committed in
  manage-agents) also names `"task file"`; it only groups its own printout and is a historical record, so it is left as is.

Regression tests (`tools-local/test_bottleneck_scan.py`):
- `BucketKeys.test_f1_no_task_hours_not_a_capacity_hint`: the PROBE F1 case (169 no-task row-hours give no hint; with
  `prerequisites` the hint is empty; a capacity bucket next to them is still listed).
- `BucketKeys.test_every_bucket_capacity_or_not`: for every bucket of `FEED_BUCKETS` and an `other: ...` bucket, the hint
  lists it exactly when it is not in `NOT_CAPACITY`; `NOT_CAPACITY` is exactly {no task file, prerequisites}.
- `BucketKeys.test_no_bucket_literal_outside_the_table`: an AST lint of the scan: no `in`/`not in` over a literal collection,
  no `fw.get(...)` and no `fw[...]` names a bucket (or the old name "task file") by a string.
- `NoTaskFile.test_named_buckets_feed_their_resource`: VM load, Mac load and accounts hours reach VM1, Mac and accounts;
  no-task and prerequisite hours reach no resource.

PROBE F1 (`probe-f1.log`): fails before the fix (`AssertionError: feed capacity waits (row-h): no task file 169.0`), passes
after it. The new tests fail on the staged scan before the fix (3 of 4; the fourth checks behaviour that was already right)
and on the live scan (`run-before.log`); all 25 pass on the staged scan (`run-staged.log`).

## 3. Seeded bugs

Build round (Python, temp copies of the staged files; each failed a test): 1. 20 min changed to 30 in the alert; 2. alert
dedup removed; 3. owner exclusion removed; 4. p1 rows let through; 5. accounts bucket placed first; 6. no-task hours added
to accq; 7. process cause dropped from classify; 8. infra-feed.log not read. The reviewer planted 8 more, all caught.

Review F1 round (`seeded-bugs.json`, file `manage-agents/tools-local/bottleneck-scan.py.new-nta`, each run with
`BN_SCRIPT=<copy> python3 -I tools-local/test_bottleneck_scan.py`): 5 of 5 caught.
- R1 NO_TASK left out of NOT_CAPACITY: test_every_bucket_capacity_or_not, test_f1_no_task_hours_not_a_capacity_hint.
- R2 `fw.get("VM load", 0)` back as a literal: test_no_bucket_literal_outside_the_table.
- R3 no-task hours added to the accounts queue: test_6, test_7, test_named_buckets_feed_their_resource.
- R4 the review's exact stale tuple `(PREREQ, "task file")`: test_every_bucket_capacity_or_not,
  test_f1_no_task_hours_not_a_capacity_hint, test_no_bucket_literal_outside_the_table.
- R5 NOT_CAPACITY names the old key "task file": the scan stops at import (`NOT_CAPACITY names no bucket: ['task file']`).

## 4. Other test files that load the scripts (staged copies, `run-staged.log`)

`test_bottleneck_account_wait.py` 9 OK, `test_bottleneck_actions_abf.py` 3 OK, `test_launch_wait_w3.py` 18/18,
`test_decider_ready_alert.py` 23 OK, `test_p1_ready_alert.py` 33 OK.

## 5. Install (unchanged; no restart: both service loops start a fresh `python3 -I` every pass)

```
cd /home/seyran/code/manage-agents/tools-local
cp -p decider-ready-alert.py decider-ready-alert.py.bak-20261117-nta
cp -p bottleneck-scan.py bottleneck-scan.py.bak-20261117-nta
mv decider-ready-alert.py.new-nta decider-ready-alert.py
mv bottleneck-scan.py.new-nta bottleneck-scan.py
```

Live md5 at this round: `decider-ready-alert.py` e11cd69b651559b3cc1a6aca37fbab7f, `bottleneck-scan.py`
a568738647c6d0f6bcde543a04f89441. Staged: `decider-ready-alert.py.new-nta` 6aea3575c22e01e7e21d7aa0ac585f1b,
`bottleneck-scan.py.new-nta` c82159ef12d611745d140318511b6fcc. The staged scan before F1 is kept as
`bottleneck-scan.py.new-nta.bak-20261117-f1`.

## 6. Review notes not filed (C1-C5)

Left as the review recorded them; none is an A or B finding.

## 7. VE checks of this branch

Recorded in section 8 after the run.
