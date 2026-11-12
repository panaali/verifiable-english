# gcp-vm1-move-plan: build report (infra, plan only)

- Status: done. This is a plan-only item, so no product code, test or generated file changed in this repository.
- What changed: the deliverable is an operations plan in the private operations directory
  (`manage-agents/reviews/gcp-vm1-move-plan-20261116.md`, with `manage-agents/gcp-vm1-move-plan.final.md`). It is not in
  this public repository, because it names hosts, ssh keys and accounts. This file is the only change on the branch.
- Open items: none for the build. The plan asks the lead questions L1-L7, which the 11-16 warning carries. It also
  proposes one wake (gcp-endgame-1118), which the decider arms as INSTALL READ.
- DRI signature needed: none. There is no user-visible change to the checker, so there is no DELTA row.
- SIZE: 0 product, 0 tests, 375 other hand-written lines (plan 280, final note 26, this report 69).

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

N.A. No product code (Lean, Python or Rust) changed. The deliverable is an operations document.

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
