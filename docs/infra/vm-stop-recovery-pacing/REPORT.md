# vm-stop-recovery-pacing: REPORT

- Status: fix round done (review F1, the only A/B finding, fixed as a class); the tool is new and nothing calls it yet. No DRI signature needed, no DELTA row (no Lean, Python-package, Rust or trust-base change in the VE tree).
- HEAD: this REPORT's commit, on top of fix-evidence commit 5f89d11664 (first round: cc377c4331, 1f3be45008). The three manage-agents files are pinned by `md5.txt` (script now md5 210ad96a…), and their full text is in `new-files.diff`; `pin_files.py --check` compares both with the files.
- Changed: new `tools-local/vm-stop-recover.sh` (pauses CHAIN_WATCH, FEATURE_FEED and INFRA_FEED; relaunches merge trains first; holds each relaunch until the 1-min load is under 48 and fewer than 6 relaunches are in their first 15 min; writes CURRENT-STATE.md lines; restores the flags once the last relaunch has run 10 min), the 1108 job list, and 18 tests. Fix round: the dry-run load release no longer drops the time holds (see "Fix round").
- Tests: 18/18 (`tests.log`); 17/17 seeded bugs caught (`seeded-bugs.json`); PROBE F1 rc 1 before, rc 0 after (`probe-f1.log`); old vs new dry runs (`f1-old-vs-new.txt`); dry runs on the 1108 list moved no flag and wrote no file (`dry-run-flags-before.txt` == `-after.txt`); real-clock VM run (`real-clock-run.log`); VE selected run (`run-selected.log`).
- Open: none. Not run: the full gate (the chain runs it) and a live recovery (by design).

SIZE: 271 product (250 script + 21 job list), 590 tests (395 test file + 81 seed runner + 76 F1 differential + 38 pin script), about 170 other hand-written lines (this REPORT).

## Fix round (review F1, B; reviews vm-stop-recovery-pacing-review.final.md and -ov.final.md, same finding)

**F1.** In a dry run, a load hold on a load that no longer changes (a live load of 48 or more, read once; a `--dry-loads` list
ending at 48 or more; an unreadable load file) ended the hold loop with `break`. That also dropped the 6-in-15-min hold and the
60 s gap present at the same moment. On the 1108 list at a load of 60, all 15 relaunches showed at +0m00s ("15/6").

- **Class:** a release of one hold that releases the others. **Structural fix:** the hold loop keeps two lists, the load holds
  (`lwhy`) and the time holds (`twhy`: young relaunches, the gap). The dry-run release empties `lwhy` only and breaks only when
  `twhy` is empty too, so the time-jump code then waits out the time holds as in a real run. The same split replaced the two
  text matches (`*(in their first|1-min load)*`, `*load*`) that decided whether a hold is logged and whether to jump the virtual
  clock. No regex lists the hold texts any more, so a new hold kind cannot be dropped by a text mismatch. The real-run path is unchanged
  (the release needs `--dry-run`).
- **Class test:** `Base.assert_paced()` runs after EVERY script run of every test (dry and real). It checks that no relaunch is a 7th while 6
  are in their first 15 min, that relaunches are at least 60 s apart, and that no "7/6 … in their first 15 min" text appears. On the reviewed script
  it also fails the old test `test_dry_run_on_a_load_that_stays_high_shows_the_hold_and_ends` (2 relaunches in the same second).
- **Regression test:** `DryRun.test_1108_a_load_that_stays_high_releases_only_the_load_hold` (PROBE F1 as a test). It covers all three
  triggers the review swept, plus a load of exactly 48. Each must give the low-load schedule (+0…+5, +15…+20, +30…+32 min), the HOLD lines of the 7th and
  13th relaunch, and the restore at +42m.
- **Probe:** PROBE F1 verbatim: rc 1 on the reviewed script, rc 0 on the fixed one (`probe-f1.log`).
- **Old vs new** (`f1_differential.py`, output `f1-old-vs-new.txt`): on the 1108 list, the output is byte-identical where no release
  happens (low live load; the rising `--dry-loads` profile). On every release trigger, the old script reaches 15/6 and the new one stays at 6/6 with the
  low-load schedule. `dry-run-1108-high-load.log` is the fixed dry run at a load of 60.
- **Seeds:** two new F1 seeds, the reviewed `break` and a release that drops only the 60 s gap; both are caught (17/17). Running the new test file
  against the reviewed script (md5 12b06170…) fails the new test on all 4 triggers, plus the old high-load test through `assert_paced`.
- **Not filed (C notes F2–F7):** left as they are. Only F2's unreadable-load claim gained a test, and only for the dry run: in the regression test above, an unreadable load file
  shows a HOLD. The real-run unreadable-load hold and the recheck after a hold are still untested.

Row: vm-stop-recovery-pacing (infra, L178). Decision: reviews/recover-20261108.md. Task: prompts/task-vm-stop-recovery-pacing.txt.

## Files (manage-agents; new files only, no live script changed, so no install read)

- `/home/seyran/code/manage-agents/tools-local/vm-stop-recover.sh` is the tool. Its header documents usage, the six steps and the jobs-file format.
- `/home/seyran/code/manage-agents/tools-local/vm-stop-recover-jobs-20261108.txt` holds recover-20261108.sh's 15 `L` lines, in their order, as a job list.
- `/home/seyran/code/manage-agents/tools-local/test_vm_stop_recover.py` is the test file. Run it with `python3 -I tools-local/test_vm_stop_recover.py` in manage-agents.

Usage: a dated `recover-<date>.sh` keeps its per-incident steps (empty finals, interrupted merges, dated wakes), then runs
`zsh iso.sh recover-<date>-jobs 1G -- zsh tools-local/vm-stop-recover.sh --date <YYYYMMDD> <jobs-file>`. Run `--dry-run` first.
To put this date's paused flags back by hand: `--restore --date <YYYYMMDD>`.

## Spec, line by line (TASK and SPEC re-read; each part with its test)

| Spec text | Delivered | Test (tools-local/test_vm_stop_recover.py) |
|---|---|---|
| (1) moves FEATURE_FEED and INFRA_FEED aside the way CHAIN_WATCH was (`FEATURE_FEED.paused-recovery-<date>`) | `pause_flags`: `mv -n <flag> <flag>.paused-recovery-<date>` for CHAIN_WATCH, FEATURE_FEED and INFRA_FEED. Before moving anything, all three are checked. The stub launcher records the flags it sees at each launch: none. | RealRun.test_pause_launch_record_restore (`| none |` on each launch line), test_absent_flag_stays_off, test_earlier_pause_of_this_date_is_kept_and_restored, test_flag_present_and_paused_refuses |
| ... and restores them when the last relaunch has run 10 min | The restore waits until `last + 600 s`, then runs `mv -n` back | DryRun.test_1108_six_in_fifteen_minutes_and_restore_ten_minutes_after_the_last (restore − last launch = 600 s), RealRun.test_pause_launch_record_restore (same check, real mode), `real-clock-run.log` (b1 at 21:14:04Z, restore at 21:24:04Z) |
| (2) next relaunch only when the 1-min load is below 48 | First field of `/proc/loadavg`, compared with `>= 48` (48 itself holds) | DryRun.test_load_hold_at_48_and_release_under_it (48 holds, 60.5 and 50 hold, 47.99 starts) |
| ... and no more than 6 relaunches are in their first 15 min | Holds while 6 of this run's relaunches are younger than 900 s | DryRun.test_1108_six_in_fifteen_minutes_... (no 15-min window has more than 6 launches; the 7th starts exactly 900 s after the 1st); Base.assert_paced on every run of every test; DryRun.test_1108_a_load_that_stays_high_releases_only_the_load_hold (also when the dry run releases a load hold: review F1) |
| ... with the merge trains first | `train` rows first, then `job` rows, each group in file order | DryRun.test_1108_order_trains_first, test_trains_first_whatever_the_file_order, RealRun.test_pause_launch_record_restore |
| (3) records each relaunch in CURRENT-STATE.md | One line each for the start (pause), every relaunch, every skip, and the end (restore). Also an INTERRUPTED line. | RealRun.test_pause_launch_record_restore (exactly 5 lines for 3 jobs), test_running_job_is_skipped, test_interrupted_run_leaves_flags_paused |
| Test: dry run against the recover-20261108 job list prints the order (trains first), the load / 6-in-15-min holds and the feed pause/restore steps, and launches nothing | `--dry-run` uses a virtual clock. It prints the same steps, moves no flag, launches nothing and writes no file. | DryRun.test_1108_moves_no_flag_launches_nothing_writes_nothing (the directory listing and CURRENT-STATE.md are unchanged, and there is no iso-calls file), plus the DryRun tests above; DryRun.test_1108_a_load_that_stays_high_releases_only_the_load_hold (the same holds at any live load: review F1) |
| HOW: must not move a flag file in its dry run | as above; also run against the live manage-agents directory | `dry-run-flags-before.txt` vs `dry-run-flags-after.txt`: identical md5s, 0 paused files, no log or lock file |
| HOW: its timing runs go to the VM; no Mac use | Every run happened on the VM. The VE selected run also fell back to the VM ("ran LOCALLY (VM)") | `real-clock-run.log`, `run-selected.log` |

## Dry runs on the recover-20261108 job list (saved output)

Command (in manage-agents): `zsh tools-local/vm-stop-recover.sh --dry-run --date 20261108 tools-local/vm-stop-recover-jobs-20261108.txt`

- `dry-run-1108-live-load.log` (live 1-min load 14-19). The order is 5 trains (gt-pc-1g, ps-1c-train, gt-et-4b, gt-df-5, gt-ps-e1), then 10 jobs (at-1b first).
  The first 6 relaunches go out 1 min apart (+0 to +5 min). The 7th is held by "6 relaunches in their first 15 min" until +15m00s.
  The 13th is held until +30m. The last relaunch is at +32m and the restore at +42m (1108 as run: 15 jobs in 35 min).
  At the time of this run, INFRA_FEED had been turned off by someone else (`INFRA_FEED.off-gcpdrain-20261117T2109Z`, 21:09Z, not
  this work). The dry run shows the case live: "INFRA_FEED is off (absent): stays off, not restored".
- `dry-run-1108-load-profile.log` (`--dry-loads` replays a rising load: 3 9 17 26 35 44 51 58 63 66 61 55 50 47 ...).
  gt-df-5 is held by "1-min load 51..50 >= 48" from +3m00s and starts at +6m30s at load 47. gt-ps-e1 is held at loads 52 and 49.
  Then the 15-min holds follow (18 HOLD lines in total).

## Choices taken (conservative; override rule 2, not asked)

- **CHAIN_WATCH is paused and restored too.** The spec calls it "the way CHAIN_WATCH was". In 1108 a check-in paused it and the script restored it. Here one owner does both.
- **A 60 s gap between relaunches,** on top of the two spec conditions, so that the 1-min load reflects the previous relaunch before the next check. This is the narrower reading: it only slows the relaunches. Without the gap, 6 relaunches would go out in the same second at low load.
- **A flag that is absent at the start stays off.** It is never turned on by the restore.
- **At the restore, a re-created flag wins** (its paused copy is kept for a human). **A removed paused copy is read as a veto** and stays removed.
- **An interrupted run (INT/TERM/HUP) leaves the flags paused.** It writes a CURRENT-STATE line that names `--restore --date <d>`. Present AND paused flags refuse the run.
- **Skip checks:** the job's key is already running (the same process scan as recover-20261108.sh), or a `ve-<scope>-*` scope is live. Both are checked before the hold and again right before the launch. **If the scope list is unreadable, the job is skipped, not guessed.**
- **The jobs file is data, not shell.** Only `$M` and `$HOME` are replaced. Any other `$`, a backtick or a shell operator refuses the whole file before anything is paused.
- **One run at a time:** a flock(2) lock on `vm-stop-recover.lock`. Launched jobs do not inherit the lock's fd: the stub records `lock:no`, and seed 15 checks it.
- **Trains** are the gate-trains and the merge train (`train` rows). at-1b (infra-item.sh in its chain gate) is a `job` row, the first one.
- **The dry run on a load that no longer changes** (the live load is read once; `--dry-loads` repeats its last value) shows the hold, then releases the load hold only, with a note. The 6-in-15-min and 60 s holds still apply (review F1). A real run waits.

## Tests (each fails first; each check is tested in both directions)

Command: `python3 -I tools-local/test_vm_stop_recover.py` in manage-agents. Result: `tests.log`, "Ran 18 tests ... OK".
Every run uses a temp manage-agents dir (`VMSR_M`) with a stub iso.sh and a stub systemctl; the real-mode tests use the virtual
clock (`VMSR_VIRTUAL_CLOCK=1`). Both directions: a load of 48 holds and 47.99 starts; 6 young relaunches hold and 5 do not;
a running job is skipped and a free one starts (same run); a live scope or an unreadable scope list skips, and a free scope starts;
a valid jobs file runs, and 14 kinds of bad file are refused (each with flags untouched and no launch); an absent flag stays off,
and a present one is paused and restored; a free lock runs, and a held lock refuses.

## Seeded bugs (17; all in `/home/seyran/code/manage-agents/tools-local/vm-stop-recover.sh`)

The runner is `python3 -I docs/infra/vm-stop-recovery-pacing/seed_run.py` (output `seed-run.log`, `seeded-bugs.json`). Each seed edits a copy of the script, never
the live file. The tests run against that copy through `VMSR_SCRIPT`. The baseline copy passes: rc 0, nothing failing. Result: 17/17 caught (16 and 17 added in the F1 fix round; the failing lists now include the tests that fail through `assert_paced`: `seed-run.log`).

| # | Seed | Failing test(s) |
|---|---|---|
| 1 | order: file order instead of trains first | test_trains_first_whatever_the_file_order, test_pause_launch_record_restore |
| 2 | load: 48 itself passes (`>` for `>=`) | test_load_hold_at_48_and_release_under_it |
| 3 | young cap: a 7th relaunch in 15 min passes | test_1108_six_in_fifteen_minutes_and_restore_ten_minutes_after_the_last |
| 4 | young window 10 min instead of 15 | test_1108_six_in_fifteen_minutes_..., test_load_hold_at_48_... |
| 5 | restore: no 10-min wait | test_1108_six_in_fifteen_minutes_..., test_pause_launch_record_restore |
| 6 | the dry run moves the flag | test_1108_moves_no_flag_launches_nothing_writes_nothing, test_dry_run_on_a_load_that_stays_high_... |
| 7 | real run does not move the flags | test_pause_launch_record_restore (+3) |
| 8 | the dry run launches | test_1108_moves_no_flag_launches_nothing_writes_nothing (+2) |
| 9 | restore overwrites a re-created flag | test_recreated_flag_wins_and_vetoed_copy_stays_removed |
| 10 | a running job is relaunched | test_running_job_is_skipped |
| 11 | an unreadable scope list read as "no scope" | test_live_or_unreadable_scope_is_skipped |
| 12 | no CURRENT-STATE.md line | test_pause_launch_record_restore (+5) |
| 13 | `$(...)` accepted in the jobs file | test_bad_jobs_file_refused_before_anything |
| 14 | the launched job inherits the lock fd | test_pause_launch_record_restore, test_absent_flag_stays_off |
| 15 | an interrupt restores the flags | test_interrupted_run_leaves_flags_paused |
| 16 | F1: the dry-run load release also drops the time holds (the reviewed `break`) | test_1108_a_load_that_stays_high_releases_only_the_load_hold, test_dry_run_on_a_load_that_stays_high_... |
| 17 | F1 class: the dry-run load release drops the 60 s gap | test_1108_a_load_that_stays_high_releases_only_the_load_hold, test_dry_run_on_a_load_that_stays_high_... |

Languages: the only product code is zsh (with embedded Python for the process scan) in manage-agents. No Lean, Python-package or
Rust product code changed in the VE tree, so there is no Lean or Rust seed. Trust mutants: `trust_mutants.py --plan` on this branch planned
`"mutants": 0` (`trust-mutants-plan.log`). The light lane printed NOT only on line count (1132 lines, all evidence under docs/), with no
trusted-core file, so there was nothing to sweep.

## VE tree checks

- Selected run: `zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`. First round: 10 units, 0 failed, exit 0. Fix round: rerun on this REPORT's commit; its result is in `run-selected.log` (it replaces the first-round log).
- Fix round: `lake build` rc 0 (1478 jobs) and `python3 lean/audit.py` PASS (`lean-checks.log`). There is no Lean change; the task asks for both checks anyway.
- Not run: the full gate (the chain runs it on the final HEAD).
- main-known-red: none of its tests were selected or hit.

## Notes for the DRI

- The task's HOW asks for `msg.sh dri ... "done: vm-stop-recover.sh + dry run"`. Standing override 2 (2026-11-11) allows `msg.sh dri`
  only for a blocking decision or a DELTA signature, and it replaces conflicting task lines. So no message was sent, and this REPORT is the "done".
  The playbook pointer stays with the decider, as the task says.
- recover-20261108.sh is unchanged, and nothing calls the new tool. The next dated recovery adopts it by calling it with a job list
  (format in the script header; example: the 1108 list).
- zsh 5.9 crashed (`malloc(): smallbin double linked list corrupted`) when a long trap body ran mid-loop. The trap now only sets a flag.
  The loop acts on the flag at its next check: at most 30 s later on a real clock. test_interrupted_run_leaves_flags_paused covers it.
- The thresholds (48, 6, 15 min, 10 min, 60 s gap, 30 s poll) are constants in one place at the top of the script. Nothing overrides them;
  the tests reach them through the virtual clock.
- MEASURED (delegate-cw.py on this session's transcript): 0.52M CW at 33 calls; 0.61M CW at 41 calls (raw context 3.73M), before the final commit.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relayed Lean answer).
2. Every deliverable built, no rule broken: PASS (spec table above; no Python copy of a Lean decision, no permanent report test).
3. Tests and gates can fail: PASS (17/17 seeds, `seeded-bugs.json`; the baseline passes; the new test fails on the reviewed script).
4. Py/Lean/Rust agree: N.A. (no checker code).
5. R8 binding: N.A. (no Lean answer fields). Inputs: unknown classes, keys, scopes and variables in the jobs file are refused (test_bad_jobs_file_refused_before_anything).
6. Gate evidence matches the final HEAD: PASS as far as possible here. The fix round's selected run is on this REPORT's commit; only its log is added after it. The chain runs the full gate on the final HEAD.
7. No unsigned item: PASS (no DELTA row, no trust-budget growth).
8. Every user-visible change in DELTA: N.A. (no VE output changes; an ops tool only).
9. Test selection: PASS (select_tests chose 10 units for a docs-only diff, not every unit).
10. Lean statements: N.A.
11. Budgets and deadlines fail closed: PASS. An unreadable load holds (dry run: test_1108_a_load_that_stays_high_releases_only_the_load_hold; real run: not tested, review note F2), and an unreadable scope list skips (test_live_or_unreadable_scope_is_skipped). An interrupt leaves the feeds paused (test_interrupted_run_leaves_flags_paused). The tests use no sleeps for timing: a virtual clock, with only bounded polls for detached stubs.
12. No CPU or memory regression: N.A. (no product path changed). The tool itself polls every 30 s.
13. Test-removed trailers: N.A. (no test removed or renamed).
14. Both directions, cited evidence, spec re-read: PASS (both-directions list above; each claim names its log; spec table).
15. Four FIX classes: PASS (deliverables complete, evidence saved with the batch, seeds recorded, no live diff in a test).
