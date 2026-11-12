# gcp-vm1-move-plan: build report (infra, plan only)

- Status: done. This is a plan-only item, so no product code, test or generated file changed in this repository.
- What changed: the deliverable is an operations plan in the private operations directory
  (`manage-agents/reviews/gcp-vm1-move-plan-20261116.md`, with `manage-agents/gcp-vm1-move-plan.final.md`). It is not in
  this public repository, because it names hosts, ssh keys and accounts. This file is the only change on the branch.
- Open items: none for the build. The plan asks the lead questions L1-L7, which the 11-16 warning carries. It also
  proposes one wake (gcp-endgame-1118), which the decider arms as INSTALL READ.
- DRI signature needed: none. There is no user-visible change to the checker, so there is no DELTA row.
- SIZE: 0 product, 0 tests, 375 other hand-written lines (plan 280, final note 26, this report 69). Review fixes (below):
  0 product, 0 repository tests; in the operations directory 1 new test file (330 lines), 1 new script (57 lines),
  2 changed scripts (+33/-2) and the plan (+37/-11).

## What the plan covers (task sections 1-6)

1. An inventory of VM1: the 49 running service scopes, the orchestrator session, chains, trains, wakes due after
   11-17T20:45Z, and the state with sizes. It also covers what VM2 and VM3 hold and do. All of it was read on the hosts
   on 2026-11-12 between 19:55Z and 20:15Z.
2. Where each item goes for phase (a) and phase (b), for both cases: VM1 credit confirmed or not. Phase (a) does not
   justify a move. A restore measured 3.1 s, but the rest of a move is 5-6 h and two moves, to gain at most 11.5 h.
3. Drain commands per host, each with its undo. One finding: on its own, the down marker is erased by the health
   service while the host answers, so the drain moves the host's runner and builder flags aside first.
4. A backup check and a timed test restore on the Mac test runner: 0.8 s on tmpfs and 3.1 s on disk. The ref counts
   match VM1 (4,977). The scratch dirs were deleted afterwards.
5. Lead-only questions, with recommendations and the minutes each costs the lead, plus money options as costed options
   only.
6. A dated runbook for the decider at the gcp-drain-* wakes, plus the proposed endgame wake.

## Evidence (commands run, read-only)

- `systemctl --user list-units --type=scope 've-svc*'`: 49 running scopes and 2 failed duplicates (svc-cloud-inbox).
- `ssh ve-mac-1`: a timed `zstd -dc ... | tar -xf -` of core-20261112T1904Z into `mktemp -d` printed `core_s=0.8`. A
  second restore into a disk dir printed `disk_core_s=3.1 files=34541`. `git -C ~/ve.git for-each-ref refs/vm-backup`
  counted 4,977, and VM1's state-backup.jsonl at 19:04Z had `"refs_vm":4977`. A final `ls` showed both scratch dirs
  were gone.
- `cloud2-health.sh` lines 21 and 25: probes are skipped while the runner flag is absent, and the down marker is deleted
  when a probe answers OK. This is the basis of the drain order in plan section 3.2.
- `cloud-secret-scan.py files` on a copy of the plan: `scanned 1 files, 5 secret values checked, hits 0`.

## Seeded bugs

N.A. for the repository: no product code (Lean, Python or Rust) changed. The review fixes change operations scripts,
and each of their behaviours was seeded and caught (section "Review fixes", seeded bugs).

## Notes for the DRI

- There is no global "no new merge trains" flag. Trains start from each chain's merge stage. For the VM1 quiesce, the
  plan uses the existing publish hold (`MQ_PUBLISH_HOLD.<sha>`), with a note that it is not a nightly red.
- `backlog.py` shows "(0 rows)" on a copy outside `/home/seyran/code/manage-agents` unless `BL_M`/`BL_OUT` are set.
  This matters only for a Mac move (plan section 2.4).

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no Lean or relay change)
2. Every required deliverable built: PASS. Plan sections 1-6, the CURRENT-STATE line and the final note all exist.
3. Tests and gates can fail: N.A. (no test or gate changed)
4. Python, Lean and Rust agree: N.A.
5. R8 binding: N.A.
6. Gate evidence matches the final HEAD: PASS. The final selected run is on the committed HEAD; the chain's gate decides the rest.
7. No unsigned item: PASS. No DELTA row and no signature is needed.
8. Every user-visible change in DELTA: N.A. (no checker behaviour changed)
9. Test selection still finds the tests: N.A. (docs only)
10. Lean statements: N.A.
11. Budgets and deadlines fail closed: N.A.
12. No CPU or memory regression: N.A.
13. Test-removed trailer: N.A. (no test removed)
14. Both directions, cited evidence, spec re-read: PASS. Each number above names its command. Spec re-read: task
    sections 1-6 against prompts/dri-task-gcp-vm1-move-plan.txt, and the lead decision of 11-12 against
    reviews/dri-decisions-20261112-compute-vm1.md.
15. No overclaim, no silent cut: PASS. "Nothing was spent, moved or created" holds because every command run on a host
    was a read, an `ls`, a `count`, or a restore into a scratch dir that was then removed. No flag, marker or wake file
    was written (`ls` of the CLOUD*_DOWN, PAUSE-FEATURES and MQ_PUBLISH_HOLD* names shows none).

## Review fixes (gcp-vm1-move-plan-review.final.md, F1-F3, all B)

Everything changed is in the private operations directory (`manage-agents/`); this report is the only repository file.
The operations directory is committed by its own snapshot service (ops-git-snapshot), so the evidence below pins each
file by its sha256 prefix at the time of the fix (2026-11-12 ~21:00Z).

| finding | class | fix | regression test (`python3 -I tools-local/test_gcp_vm1_move_plan.py`) |
|---|---|---|---|
| F1 | a drain control that the launcher does not read (PAUSE-FEATURES vs feature-plan-daily), and "skip if busy" for a loop that runs its work in its own scope (pilots) | Plan 3.1: a row per launcher of section 1.1 with the control that launcher reads: feature-plan-daily loop stopped (its delegate runs in its own scope); pilots stopped by a new watcher `tools-local/stop-when-idle.sh` as soon as each loop is idle (only its zsh and a `sleep` with >= 60 s left), so a run in progress finishes and no 06:00Z run starts; LANG_ACCEPT.off for lang-accept. Section 6 checks at 07:22Z that no feature-plan/pilot scope is left. | `F1Launchers.test_probe_f1_feature_plan_daily_does_not_launch_after_the_drain` (PROBE F1), `F1Launchers.test_every_launcher_has_a_control_it_reads` (each launcher's control must be a flag its script tests or a stop of its own scope; a loop with in-scope work must use stop-when-idle), `F1Launchers.test_pilot_globs_do_not_hit_other_scopes`, `F1StopWhenIdle.*` (3) |
| F2 | a cleanup that lists credential paths by hand (`codex-*/auth.json` vs the real `codex/auth.json`) | Plan 3.3 step 2: `rm -f ~/.agent-accounts/*/.credentials.json ~/.agent-accounts/*/auth.json` plus the peer keys, then `bash -s wipe <hostname>` of `tools-local/remote-host-setup.sh`, which now owns the one list (LOGIN_DIRS, already used by its REMOTE_CLEAN check, and PEER_KEYS) and has `clean-check` / `wipe` modes (wipe refuses on any other machine). The 1.5 inventory now lists every name seen on both hosts (`ssh <h> ls`, names only). | `F2Wipe.test_probe_f2_rm_line_removes_every_credential_file` (PROBE F2), `F2Wipe.test_wipe_mode_removes_the_whole_list_and_clean_check_sees_leftovers`, `F2Wipe.test_wipe_list_covers_the_credential_inventory`, `F2Wipe.test_runbook_uses_the_one_list` |
| F3 | a synchronizer that writes a deleted secret back (c2b-creds.py, called before/during/after each session by both wrappers) | `tools-local/c2b-creds.py` (the only writer of a login to a remote host) refuses while `C2B_CREDS_RETIRED.<host>` exists, reading it after it takes the account lock. Plan 3.3 step 0 writes the marker and takes each lock once before anything is removed, so no sync is mid-write and every later one refuses; absence is checked twice (after step 4 and >= 10 min after the wipe), with the "VM -> host" log count. The wrong "creds runs only in prep" claim is gone. | `F3CredsRetired.test_retired_host_gets_nothing_and_is_not_contacted`, `.test_a_sync_waiting_on_the_lock_refuses_once_the_marker_is_written`, `.test_marker_is_per_host`, `.test_without_the_marker_the_login_is_written_back` (the test can fail), `.test_runbook_quiesces_before_it_removes_and_checks_after` |

PROBE F1 and PROBE F2 (`/tmp/gcp-vm1-review-probes.py`): both failed on the plan as filed (run on its backup
`reviews/gcp-vm1-move-plan-20261116.md.bak-20261112-gcpvm1fix`: "feature-plan-daily is still enabled after the VM1
drain"; "the documented cleanup leaves credential files behind") and pass on the fixed plan. PROBE F3: none (race); its
regression test drives the race with the lock held and the sync seen queued in /proc/locks.

Seeded bugs (each on a scratch copy, test run against it, copy deleted; baseline 15/15 OK):
- c2b-creds.py, marker check removed: `test_retired_host_gets_nothing_and_is_not_contacted` and
  `test_a_sync_waiting_on_the_lock_refuses_once_the_marker_is_written` fail.
- c2b-creds.py, marker read before the lock: `test_a_sync_waiting_on_the_lock_refuses_once_the_marker_is_written` fails.
- stop-when-idle.sh, no ">= 60 s left" check: `test_idle_loop_is_stopped_and_busy_loops_are_not` fails (a retry sleep
  inside a run, and a sleep about to end at 06:00Z, were taken as idle).
- stop-when-idle.sh, any number of shells: the same test fails.
- remote-host-setup.sh, `.codex` dropped from LOGIN_DIRS: `test_wipe_mode_...` and `test_wipe_list_covers_...` fail.
- remote-host-setup.sh, no hostname guard on wipe: `test_wipe_mode_...` fails.
- Plan as filed: 5 tests fail (both probes, the launcher class test, the one-list test, the 3.3 order test). Plan with
  only the pilot row reverted (with or without its "skip this row"): the launcher class test fails.

Evidence (sha256 prefixes, operations directory): plan 95489a53628b70d5, test_gcp_vm1_move_plan.py 40e546288915a312,
stop-when-idle.sh 3a3524917e2066ad, c2b-creds.py 3c91ee39fba72e48, remote-host-setup.sh 1d1f7547eb3ee8fe. Secret scan of
copies of the five: `cloud-secret-scan.py files <copy dir>`: "scanned 5 files, 5 secret values checked, hits 0". The
watcher was also run once against the live pilot loop's real pids with a stub systemctl (it reported the loop idle and
called only the stub). Read-only ssh on 11-12: `ssh <h> hostname` (multi-agent-lab-2, -3) and `ls` of names under ~ (no
contents read). No unit was stopped, no flag, marker or wake was written, and no login was touched on any host.

DELTA: none. No checker behaviour changed, so there is no DELTA row and no signature is needed.
