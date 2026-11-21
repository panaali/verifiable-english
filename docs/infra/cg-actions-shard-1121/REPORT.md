# cg-actions-shard-1121: chain gates run gate.py sharded on Actions before the VM

INSTALL WAITS FOR DECIDER READ. Status: BUILT and tested in staged copies; nothing is installed. No DELTA row and no DRI signature is needed.
HEAD: this branch carries evidence only. The product change is in `manage-agents` as `chain-gate.sh.new-cgshard` and `gha/cancel-leg-runs.py.new-cgshard` (new file).
What changed: the MAC_LAST_RESORT route now tries a sharded Actions gate (`gha-arm-shard.sh`, unchanged) after the ve-cloud-2 step and before the VM step. It writes one merged `gate-result.json` with `where=actions-arm` (or `actions-x86`). A missing, failed or unparseable shard is a FAIL. Anything else that gives no verdict falls back to the VM step, then the Mac, as today.
Open: the decider's install read. The sibling `cg-vm-gate-width-1121` was installed during this build. `chain-gate.sh.new-cgshard` is now re-ported onto that new live file (md5 `e2964a76…`), and against it the change only adds lines (see "Sibling" below).

SIZE: 204 product (115 lines added to `chain-gate.sh`, 0 removed; 89 in the new `gha/cancel-leg-runs.py`), 482 tests (`tools-local/test_chain_gate_actions_shard.py`), 65 other hand-written lines (`measure.py`, `leg-times.py`).

## Route before and after (MAC_LAST_RESORT + MAC_GATE, not the risky-only selected route)

| step | before (live `chain-gate.sh`, md5 `e2964a76…`, cgwidth installed) | after (`chain-gate.sh.new-cgshard`, md5 `82909ce1…`) |
|---|---|---|
| cloud saturated (mac-last-chaingate probe) | take the Mac's one slot, Mac gate | **Actions shard step**; on no verdict, the Mac's one slot as before (`CHAIN_GATE_ACTIONS_SAT=0` restores the old behaviour) |
| 1 | ve-cloud-2 (`cloud2-run.sh gate`) | unchanged |
| 2 | VM load check, then the VM gate | **Actions shard step**; on no verdict, the VM load check, then the VM gate, unchanged |
| 3 | Mac gate when the VM is full | unchanged (the Mac stays last) |

Without MAC_LAST_RESORT (or MAC_GATE, or under the risky-only `nogate` route), nothing changes. Test (vi) covers the no-MAC_LAST_RESORT case.

The Actions step (`ghstep`, header comment in the staged file) works like this:
- **Leg.** `env ARM_SHARD_MODE=blocking ARM_SHARD_JOBFILE=… ARM_SHARD_DEADLINE_MIN=<deadline> zsh gha-arm-shard.sh chain-<label> <HEAD>` runs in `iso.sh` scope `chaingha-<label>-<pid>` (2G). These are the train's blocking-leg arguments. The label `chain-*` means the leg is never seeded (seeding is for `cand-*` only) and is never compared.
  - `CHAIN_GATE_ACTIONS_LEG=x86` gives `--x86 ARM_SHARD_MODE=leg-blocking` instead, which needs `X86_SHARD_BLOCKING`.
  - `gha-arm-shard.sh` needs no change, so deliverable 4 does not apply. Its md5 is unchanged in `md5.txt`.
- **Record.** The leg's merged record goes through the live `gha/arm-leg-record.py`. That script checks the tree, sets `commit_sha` to HEAD, keeps `export_commit`, and sets `where=actions-<arm|x86>`. The result is written to `<worktree>/gate-result.json`.
  - The gate passes only if the leg exits 0 AND the record has status passed, mode full, `dirty` false, non-empty stages, and HEAD's commit and tree.
  - Anything else with a leg verdict rewrites the record as FAILED and exits 1. That covers exit 1, an exit-4 shard that failed or came back in another shape, no record, an unreadable record, and another tree.
  - There is no R13 rerun: `tools/gate.py:473` `rerun_refusal` refuses to rerun another runner's record and would run the full gate on the VM instead.
- **No verdict → next step.** These all go to the next step:
  - not tried (see "Fallback conditions");
  - not sent (exit 3);
  - every missing shard is "no result by the deadline" (exit 4);
  - the chain's hard limit passes;
  - any other exit.

  On a deadline, the hard limit or another exit, the leg's runs are cancelled.
- **Events.**
  - `gate-route "ACTIONS: …"` for each decision;
  - `gate-start "actions-<arm|x86> <sha8>"` and `gate-end "actions-<arm|x86> rc=<n|timeout>"`;
  - `gate-cancelled "actions gate stopped: …"` and `"no actions gate: …"`.

  The host is the first word of the note, as `tools-local/mac-last-resort.py` and `measure.py` read it.

## Fallback conditions (deliverable 2) and the numbers chosen

- **Not tried; the next step runs exactly as today:**
  - the veto file `CHAIN_GATE_ACTIONS_OFF`;
  - the leg's flag (`ARM_SHARD_BLOCKING`, or `X86_SHARD_BLOCKING` for x86) is off;
  - `ACTIONS_SUSPENDED`;
  - `cloud-jobs/ACTIONS_MISMATCH` blocks. This is checked by sourcing `mismatch-scope.sh` live on each use. If the file cannot be sourced, the old rule applies: the file's existence blocks;
  - `CLOUD_PUSH_HOLD`;
  - no `gha-arm-shard.sh`;
  - shard room unreadable;
  - **over the shard cap.**
- **Shard cap.** `shard-room.py actions` room must be at least `CHAIN_GATE_ACTIONS_MIN_ROOM`, **default 10**: one train leg's 8 shards (`ARM_SHARD_NMAX`) plus this leg's minimum of 2. So a chain gate never takes the room the train's next leg needs. Live room during this build was 33 (`shard-room.py actions 40 cloud-jobs gha-tests "" 3600` printed `33 5 2 2`).
- **Deadline.** `CHAIN_GATE_ACTIONS_DEADLINE_MIN`, **default 75 min**, is passed as the leg's `ARM_SHARD_DEADLINE_MIN`. It is sized from `leg-times.txt`, built from 117 blocking arm legs between Nov 14 and Nov 21 11:00Z, all with a merged verdict:
  - median 35.0, p75 38.4, p90 57.2, p95 68.0, max 106.2 min;
  - 4 legs (3.4%) went over 75 min; the last 8 legs had a median of 36.1 min.

  75 min is above p95 and about 2x the median, and still well under the VM path: VM gate-start to gate-end has a median of 130.4 min (`measure-baseline.txt`), before the vm1 slot wait.
- **Hard limit.** `CHAIN_GATE_ACTIONS_HARD_S`, default (deadline + 15) × 60 = 5400 s, measured from the leg's start. It covers time before the push and the merge.
- **Poll.** `CHAIN_GATE_ACTIONS_POLL`, default 5 s. This is the cancel and hard-limit poll, the same as `selrun`.

## FIX_EARLY cancel (deliverable 3)

- **File present before the step:** event `gate-cancelled "no actions gate: …"`, exit 4, and the leg never starts.
- **File appears while the leg runs:**
  1. TERM goes to the leg's session (it is started with `setsid`, like `selrun`), then KILL after 60 s.
  2. `systemctl --user stop ve-chaingha-<label>-<pid>-*.scope` runs.
  3. `gha/cancel-leg-runs.py <job dir> <start>` runs.
  4. `gate-result.json` is removed, event `gate-cancelled "actions gate stopped: …"`, exit 4.

**`gha/cancel-leg-runs.py` (new).**
- It reads the newest push run of each `ci-job/<job>-s<k>`, `-s<k>r1` and `-lean` branch through `gha/shard-run-status.py`, which stays the one owner of that lookup.
- It sends `POST /repos/<slug>/actions/runs/<id>/cancel` for each run that has not completed.
- The token goes only into the header.
- Exit 1 means a refused cancel or a failed lookup.

## Tests (deliverable 5) — `tools-local/test_chain_gate_actions_shard.py`

The tests are hermetic:
- a scratch M with stubs for `gha-arm-shard.sh`, `shard-room.py`, the cancel helper and `mac-gate.sh`;
- live copies of `gha/arm-leg-record.py` and `mismatch-scope.sh`;
- a scratch git worktree whose `tools/gate.py` is the VM stub;
- for the helper, a local HTTP server on 127.0.0.1.

They do not touch the live `cloud-jobs/`, flags, GitHub or any remote.

| run | command | result |
|---|---|---|
| failing first, live script (both before and after the cgwidth install) | `python3 -I tools-local/test_chain_gate_actions_shard.py` | `FAILED (82 failures)`, rc 1, on both lives: `test-on-live.log` (live `e2964a76`) and `test-on-live-pre-cgwidth.log` (live `a2145658`). The 106 ok checks are the fallback cases, which live already routes to the VM. |
| staged script (re-ported) | `CG=chain-gate.sh.new-cgshard python3 -I tools-local/test_chain_gate_actions_shard.py` | `all passed (0 failures)`, 188 ok, rc 0 (`test-on-new.log`) |
| existing chain-gate suites on the re-ported script | `CG=… test_chain_gate_vm_cancel / test_chain_gate_empty_ve_diff / test_gate_reuse / test_mac_last_resort / test_vm1_gate_weight / test_chain_gate_vm_width`, `CHAIN_GATE_SCRIPT=… test_defer_heavy`, `test-harness/l128/test-collcheck.zsh <staged>` | all pass (`existing-tests-on-new.txt`) |
| before the re-port: staged on `a2145658`, and the 3-way merge with the then-staged `.new-cgwidth` | the same tests | all pass (`test-on-combined-cgwidth.log`, `cgwidth-test-on-combined.log`). The merge is byte-identical to the re-port (`cmp`). |
| syntax | `zsh -n chain-gate.sh.new-cgshard`; `ast.parse` of the helper and the test | ok (`syntax.txt`) |

Cases, matching the task's (i)–(v):
- **(i)** Actions available. The shard step comes after the ve-cloud-2 event and before any VM step. It runs with mode blocking, label `chain-t`, HEAD and deadline 75. The result is one `gate-result.json` with `where=actions-arm`, HEAD, the tree and `export_commit`.
  - No VM or Mac gate runs.
  - Running the same HEAD again gives chain-gate's own `gate-skip`.
  - `review-ready.py`'s own `gate_candidates` and the `main()` filter accept the record.
  - (ix) The x86 leg uses `--x86` and `leg-blocking` and writes `where=actions-x86`. Without its flag, the VM step runs.
- **(ii)** Every one of these gives exit 1, a FAILED record of HEAD with `where=actions-arm`, and no VM or Mac gate:
  - a merged FAIL, with its nodeid kept;
  - a shard of another shape (exit 4);
  - one failed shard plus one deadline shard;
  - exit 0 with no record;
  - an unparseable record;
  - a record of another tree;
  - exit 0 with a failed record;
  - exit 1 with a passed record;
  - a passed record with no stages;
  - a passed record that is not clean.
- **(iii)** Each of these goes to the VM step, and the shard stub never starts:
  - ACTIONS_SUSPENDED, CLOUD_PUSH_HOLD, CHAIN_GATE_ACTIONS_OFF;
  - room 9 < 10, room unreadable, room 3 < 4;
  - ARM_SHARD_BLOCKING off;
  - ACTIONS_MISMATCH that is empty or holds a `select-*` line.

  The opposite direction is also tested: room 4 = 4, and a `tm-*` verdict-sample-only ACTIONS_MISMATCH, both take the Actions step. Exit 3 (not sent) goes to the VM step and cancels nothing.
- **(iv)** Deadline cases:
  - The leg's deadline passes (every MISSING shard is "no result by the deadline"): the cancel helper is called with the job dir, then the VM step runs.
  - The hard limit (3 s against a 40 s leg) stops the leg: its process group is gone, its runs are cancelled, `gate-end rc=timeout`, then the VM step runs.
  - `CHAIN_GATE_ACTIONS_DEADLINE_MIN` is passed through to the leg.
- **(v)** Cancel cases:
  - A cancel file made while the leg runs gives exit 4 within 70 s. The process group is gone, the cancel helper gets the job dir, there is no `gate-result.json`, and no VM or Mac gate runs.
  - A cancel file made before the step gives exit 4 and the leg never starts.
- **(vi)** Without MAC_LAST_RESORT there is no Actions step and no ACTIONS event.
- **(vii)** When the cloud is saturated:
  - The Actions step runs and the Mac does not.
  - With `CHAIN_GATE_ACTIONS_SAT=0`, the Mac runs as before.
  - With Actions unavailable, the Mac runs as before.
  - When the leg is not sent, the Mac runs as before and the leg is tried only once.
- **(h)** The helper:
  - only running runs are cancelled;
  - s1..sN, the r1 branches and lean are read;
  - the token appears only in the Authorization header;
  - a 403 gives exit 1 and is named;
  - a failed lookup gives exit 1 and nothing is cancelled;
  - nothing running gives exit 0;
  - with no shards in run.json, 41 branches are read;
  - usage gives exit 2.

## Seeded bugs (each in a /tmp copy of the staged file; `seeded-bugs.txt`, generator `seeded-bugs-mk.py`)

| # | file | bug | test that fails |
|---|---|---|---|
| s1 | `chain-gate.sh` (zsh) | exit 1 is accepted as a pass | (ii) "exit 1 with a passed record" (3 failures) |
| s2 | `chain-gate.sh` | every exit 4 is treated as the deadline | (ii) "a shard of another shape" and others (7 failures) |
| s3 | `chain-gate.sh` | a cancel does not cancel the runs | (v) "runs cancelled with the job dir" |
| s4 | `chain-gate.sh` | ACTIONS_SUSPENDED is ignored | (iii) ACTIONS_SUSPENDED (6 failures) |
| s5 | `chain-gate.sh` | no hard limit | (iv) chain hard limit (6 failures) |
| h1 | `gha/cancel-leg-runs.py` (Python) | completed runs are cancelled too | (h) 3 failures |
| h2 | `gha/cancel-leg-runs.py` | a 403 counts as success | (h) "one cancel refused (403)" |

All 7 failed the test, and the staged files are unchanged (`md5.txt`). The seeds were planted in the staged file before the re-port (md5 in `md5.txt`). The re-port changed no line of the Actions step: `chain-gate.sh.cgshard-pre-report.diff` and `chain-gate.sh.cgshard.diff` add the same 115 lines. No VE product code changed (Lean, Python or Rust), so no VE seeded bug applies. Light lane printed `NOT 1665 changed lines … (17 files)`, all of it evidence (logs and diffs). There is no Lean change, so the R16 trust_mutants sweep (checklist 13a) does not apply.

Selected tests, run once on the committed HEAD b56c9d8764 (`selected-run.txt`): `recorded 276 units … 0 failed`, exit 0. They ran on ve-cloud-2.

## How the saving will be measured

- **Metric.** Run `python3 -I docs/infra/cg-actions-shard-1121/measure.py ~/code/manage-agents/stage-events.jsonl <install time>` over the next chain gates. It gives each host's gate-start→gate-end median.
- **Target.** The `actions-arm` median should be ≤ 45 min. The arm legs had a median of 35.0 (MEASURED, `leg-times.txt`).
- **Second measure.** Also track the count of `vm` gates and `gate-wait` (vm1 slot) events per day.
- **Baseline.** `measure-baseline.txt`, Nov 14-21:
  - `vm` n=32, median 130.4 min;
  - `ve-cloud-2` n=88, median 41.5 min;
  - `mac` n=48, median 10.5 min.
- **Expected saving.** The task's ESTIMATE is ~40-50 item-h/day, from reviews/chain-gate-20-20261121.md. I did not re-derive it.

## Sibling cg-vm-gate-width-1121

- **State.** It was INSTALLED during this build. Live `chain-gate.sh` went from md5 `a2145658…` to `e2964a76…`, with backup `chain-gate.sh.bak-20261121cgwidth` (= `a2145658…`, my base).
- **Re-port.** I re-ported this item onto the new live file with a 3-way merge: `git merge-file -p chain-gate.sh chain-gate.sh.bak-20261121cgwidth chain-gate.sh.new-cgshard`.
  - It had one adjacent-line conflict: my inserted `ghstep` call line next to the sibling's `mvw=${VM_ROUTE_WORKERS:-8}` line.
  - I kept both, my call line first.
  - Against the new live file the result only adds lines: 115 added, 0 removed (`chain-gate.sh.cgshard.diff`).
  - It is byte-identical to the merge I had tested earlier with the then-staged `.new-cgwidth`.
- **Tests on the re-port.** Every suite passes, including the sibling's `test_chain_gate_vm_width.py` (`existing-tests-on-new.txt`).

## Spec re-read

- **Task item 1** ("in the MAC_LAST_RESORT route, after the ve-cloud-2 step and BEFORE the VM step … ARM_SHARD_BLOCKING leg mode; or --x86 with X86_SHARD_BLOCKING … ONE gate record … where=actions-<arm|x86> … missing, failed or unparseable shard = FAIL"): checked against the staged lines `ghstep` and the call after the ve-cloud-2 step.
- **Task item 2** (fallback list, deadline variable): checked against `ghavail` and `ghstep`.
- **Task item 3** (cancel; Mac last): checked against `ghstep` stop=cancel and the saturated branch.
- **Train's leg arguments:** checked against `merge-train.sh:742` (shleg) and `:772` (x86shleg).
- **Record format:** checked against `review-ready.py:472-476` and chain-gate's own prior check (`chain-gate.sh:96-106`).

## Self-review against BUILDER-CHECKLIST

1. N.A. No Lean answer is relayed.
2. PASS. Deliverables 1-6 are built. Deliverable 4 needed no change (`gha-arm-shard.sh` md5 unchanged, `md5.txt`). Tests: `test-on-new.log`.
3. PASS. Failing first on live (`test-on-live.log`, 82 failures); 7 seeded bugs caught (`seeded-bugs.txt`).
4. N.A. No Python/Lean/Rust checker logic changed.
5. N.A. No R8 binding.
6. PASS. The chain runs the gate on the final HEAD. The evidence tests ran on the staged files whose md5s are in `md5.txt`.
7. PASS. No unsigned item; no DELTA row (the task: not a trust-base change).
8. N.A. No user-visible VE change.
9. N.A. No VE code changed, so test selection is unaffected.
10. N.A. No Lean statement.
11. PASS. The deadline and hard limit fail closed to the VM step, never to a pass: (iv) "leg deadline" and "chain hard limit". A missing shard is a FAIL: (ii).
12. PASS. No VM CPU is added; the leg waits and polls. It runs in a 2G scope (the train's figure).
13. N.A. No test removed or renamed.
14. PASS. Both directions are tested: refuse and accept for room (9<10 / 4=4) and mismatch (select / tm-only), and pass vs every fail shape in (ii). Claims cite logs in this directory. Spec re-read is above.
15. PASS on each class:
    - No overclaim: the universal words above cite (i)-(vii) and (h).
    - No silent cut: none.
    - Every new check can fail: seeded s1-s5, h1-h2.
    - Limits charged before work: the room cap is checked before the leg starts ((iii) room cases).

## Notes for the DRI

- **Token scope.** `~/.ve-gh-release-token` is documented as a Contents read/write PAT (reviews/cloud-runner-pilot-20261027.md:64). Cancelling a run needs Actions: write. Until the token has it, a cancel answers 403 and the runs go on to their own end, at most the job's 120 min. The chain still stops at once, exits 4 and writes no record. I made no live API call to check this, because it is outward-facing. The token renewal on Nov 26 is a chance to add the scope.
- **No R13 rerun after an Actions FAIL.** gate.py refuses another runner's record, so a flaky Actions FAIL sends the builder back. In the window, 7 of 117 blocking legs merged FAIL.
- **Why arm is the default leg.** The arm workflow fetches and requires the pinned sources (VE_REQUIRE_PINNED_SOURCES=1, which the chain gate sets on the VM). The staged x86 `gha/ve-job.yml` does not. An arm chain gate does not run x86. The train still runs its x86 leg on every candidate.
- **New rows in shared logs.** Chain legs add rows with label `chain-*` and mode `blocking` to `gha-arm/gha-arm-shard.jsonl` and `shard-overhead.tsv`. Anything that measures the train's legs should filter on `cand-*`.
- **Pushes to the public repo.** The leg pushes the item's committed HEAD as `ci-job/*` branches to the public export repo, as builder selected-test runs on Actions (gha-tests) already do.
- **Context budget.** `python3 -I tools-local/delegate-cw.py` printed "own session not found (needs VE_STEP and CLAUDE_CONFIG_DIR …)", so there is no figure to quote.

## Install (after the decider's read; nothing installed by the builder)

```
cd /home/seyran/code/manage-agents
md5sum chain-gate.sh   # must print e2964a7681dbb5dcaa145b965483a142 (the base of the re-port); anything else: re-port first
mv gha/cancel-leg-runs.py.new-cgshard gha/cancel-leg-runs.py
cp -p chain-gate.sh chain-gate.sh.bak-$(date -u +%Y%m%d)cgshard && mv chain-gate.sh.new-cgshard chain-gate.sh
```

Revert: `touch CHAIN_GATE_ACTIONS_OFF` (the step is not tried), or restore the backup.
