# cg-vm-gate-width-1121: REPORT

Status: STAGED, not installed. INSTALL WAITS FOR DECIDER READ (placement/width change). HEAD: the commit that adds this file
on infra/cg-vm-gate-width-1121.
Change: chain-gate.sh.new-cgwidth: the VM chain gate and its R13 rerun default to 14 gate.py workers (was 8). The MAC_LAST_RESORT
route test keeps counting 8 workers through its own VM_ROUTE_WORKERS. Paired file: test_chain_gate_vm_cancel.py.new-cgwidth.
Open: the install read; the sibling cg-actions-shard-1121 conflicts on one line (resolution below). No DRI signature is needed.

Item: cg-vm-gate-width-1121 (reviews/chain-gate-20-20261121.md section 7, Fix 2; task prompts/task-cg-vm-gate-width-1121.txt).
This is an infra item. The product change is in manage-agents (`chain-gate.sh`), not in this repository. This directory keeps
the saved evidence, as earlier infra items did (docs/infra/fix-early-running-vm-gate). A copy of this report is at
manage-agents reviews/cg-vm-gate-width-1121/REPORT.md.

SIZE: 9 product (chain-gate.sh: 5 changed lines, 4 added comment lines), 164 tests (new test_chain_gate_vm_width.py 161; 3 in
test_chain_gate_vm_cancel.py.new-cgwidth), ~170 other hand-written lines (this report, seeded-bugs.json).

## Diff summary (staged-changes.diff; sha256 in sha256.txt)

Staged from the live chain-gate.sh, sha256 983236e8... (the live file is unchanged at the time of writing).
- l.7 header: `--workers ${VM_GATE_WORKERS:-14}`, plus a 4-line dated note: the reason, VM_GATE_MAX and CPUWeight 1000
  unchanged, the route's own VM_ROUTE_WORKERS, and the test.
- l.264 MAC_LAST_RESORT comment: "1-min load + VM_ROUTE_WORKERS (8) < MAC_LAST_VM_LOAD (32)".
- l.300 route: `mvw=${VM_GATE_WORKERS:-8}` became `mvw=${VM_ROUTE_WORKERS:-8}`. The route decision no longer reads
  VM_GATE_WORKERS, so a VM_GATE_WORKERS set for an item cannot move Mac use.
- l.471 VM gate: `vmg --workers ${VM_GATE_WORKERS:-14}`; l.491 R13 rerun: `vmg --rerun-failed --workers ${VM_GATE_WORKERS:-14}`.
- Left as they were: VM_GATE_MAX (default 1), the iso.sh vmgate-* scope (CPUWeight 1000, set in iso.sh, not touched),
  VM_GATE_MEM 48G, MAC_LAST_VM_LOAD 32, and the ve-cloud-2 widths (CLOUD2_CHAIN_WORKERS 14).
  Evidence: staged-changes.diff shows exactly the 5 hunks above.
- tools-local/test_chain_gate_vm_cancel.py.new-cgwidth: case (3) pins the default argv `["--workers", "14"]` (was "8"), and
  its docstring says so. It is installed together with chain-gate.sh. The live copy of that test expects 8 and would fail on
  the new script.
- `zsh -n chain-gate.sh.new-cgwidth`: SYNTAX-OK.

## Tests

New test: tools-local/test_chain_gate_vm_width.py (in manage-agents; sha256 in sha256.txt). It works on a scratch M, HOME
and worktree, with a stub `uv` and a stub tools/gate.py that logs its argv. A stub `cut` answers only `cut ... /proc/loadavg`
with $STUB_LOAD. $M/mac-gate.sh is a stub, and there is no iso.sh and no CLOUD2_RUNNER.
- (i) default: the gate gets `--workers 14`, and the R13 rerun gets `--rerun-failed --workers 14`.
- (ii) VM_GATE_WORKERS=5 and VM_GATE_WORKERS=20 set both the gate and the rerun.
- (iii) MAC_LAST_RESORT+MAC_GATE, MAC_LAST_CHAINGATE_SAT=0, limit 32. A load of 23.00 routes to the VM ("VM load 23.00 + 8
  workers < 32: the VM gate"; gate.py ran, mac-gate.sh did not). A load of 24.00 routes to the Mac ("load 24.00 + 8 >= 32";
  mac-gate.sh ran, gate.py did not). This holds with VM_GATE_WORKERS unset, 1, 14 and 30.
- (iv) VM_ROUTE_WORKERS=9 moves the route alone: a load of 23.00 goes to the Mac.

| run | command | result | log |
|---|---|---|---|
| failing first, live | `python3 -I tools-local/test_chain_gate_vm_width.py` | rc 1, FAIL (10) | live-failfirst.log |
| staged | `CG=.../chain-gate.sh.new-cgwidth python3 -I tools-local/test_chain_gate_vm_width.py` | rc 0, PASS | staged.log |
| vm_cancel, staged pair | `CG=...new-cgwidth python3 -I tools-local/test_chain_gate_vm_cancel.py.new-cgwidth` | rc 0, 21 ok, "PASS: 0 failure(s)" | vm-cancel-staged.log |
| empty-ve-diff, staged | `CG=...new-cgwidth python3 -I tools-local/test_chain_gate_empty_ve_diff.py` | rc 0, "all passed (0 failures)" | empty-ve-diff-staged.log |
| vm1-gate-weight, staged | `CG=...new-cgwidth python3 -I tools-local/test_vm1_gate_weight.py` | rc 0, 60 ok, "PASSED: 0 failure(s)" | vm1-gate-weight-staged.log |
| combined with .new-cgshard | width test on the 3-way merge (see Sibling) | rc 0, PASS | combined-with-cgshard.log |
| VE selected tests | `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` at 3b06074d14 | exit 0, 251 units, 0 failed (ve-cloud-2, 1266 s) | selected.log |

On the live file the failing-first run fails on (i) both, (iii) with VM_GATE_WORKERS unset at load 23 (the gate ran
`--workers 8`), (iii) with VM_GATE_WORKERS 1/14/30 (the route moved with the gate width), and (iv). (ii) and "unset, load
24 -> Mac" pass on live, because live behaves the same there.

Pre-existing, not touched: tools-local/test-pinned-require-hosts.py greps chain-gate.sh for the line `uv run python tools/gate.py
--workers ${VM_GATE_WORKERS:-8} >`. That line has not existed since the vm1-gate-weight `vmg()` refactor. The test FAILs (2) on the
live chain-gate.sh as it is now, and the same on .new-cgwidth (command `python3 -I tools-local/test-pinned-require-hosts.py
[.new-cgwidth]`). The pinned-sources requirement itself is covered by test_chain_gate_vm_cancel (3): `pinned == "1"`.

## Seeded bugs (seeded-bugs.json; planted in chain-gate.sh.new-cgwidth one at a time, restored and checked by sha256)

| id | change | failing test | result |
|---|---|---|---|
| S1-gate-default | gate `${VM_GATE_WORKERS:-14}` -> `:-8` | (i) gate --workers 14 | FAIL 3 (seed-S1-gate-default.log) |
| S2-rerun-default | rerun `${VM_GATE_WORKERS:-14}` -> `:-8` | (i) R13 rerun --workers 14 | FAIL 1 (seed-S2-rerun-default.log) |
| S3-route-reads-gate | route `mvw=${VM_ROUTE_WORKERS:-8}` -> `${VM_GATE_WORKERS:-8}` | (iii) VM_GATE_WORKERS 1/14/30 | FAIL 7 (seed-S3-route-reads-gate.log) |
| S4-route-default | route `${VM_ROUTE_WORKERS:-8}` -> `:-14` | (iii) unset, load 23 -> VM | FAIL 8 (seed-S4-route-default.log) |

Language: shell (zsh), the only language changed. No VE product code changed (Lean, Python and Rust are untouched), so there is no
trust_mutants sweep. There is no DELTA row: this is not a trust-base change and nothing is reserved for the DRI.

## Sibling cg-actions-shard-1121 (.new-cgshard)

The sibling has not installed. The live chain-gate.sh is still 983236e8..., the file I staged from. chain-gate.sh.new-cgshard
(sha256 0fad2446...) has changed since then: it adds the Actions step (`ghstep`) just above the route's `mvw` line. `git
merge-file` of the two staged copies gives ONE conflict, on adjacent lines. The resolution keeps both: the sibling's `ghstep`
line first, then `mvw=${VM_ROUTE_WORKERS:-8}`. On that combined file `zsh -n` is OK and test_chain_gate_vm_width.py PASSes
(combined-with-cgshard.log). I did not run the sibling's test_chain_gate_actions_shard.py on the combined file. Whichever item
installs second re-ports onto the new live file with this resolution.

## Install (waits for the decider's read)

Precondition: `sha256sum chain-gate.sh` = 983236e86a75d42e9bb20d3aac72cada1cb0d30e6e6230a525f7c1d88dd62acf. If it differs,
the sibling has installed: re-port and re-run the tests above first.

    cd /home/seyran/code/manage-agents
    cp -p chain-gate.sh chain-gate.sh.bak-20261121cgwidth
    cp -p tools-local/test_chain_gate_vm_cancel.py tools-local/test_chain_gate_vm_cancel.py.bak-20261121cgwidth
    mv chain-gate.sh.new-cgwidth chain-gate.sh
    mv tools-local/test_chain_gate_vm_cancel.py.new-cgwidth tools-local/test_chain_gate_vm_cancel.py

`mv` replaces the file. A chain-gate.sh that is already running keeps the old text, and the next chain gate reads the new one.
Revert: `mv chain-gate.sh.bak-20261121cgwidth chain-gate.sh` (and the same for the test). For a quick knob instead, set
VM_GATE_WORKERS=8 for an item (chain-watch.py ALLOW passes it through).

## How it will be measured (after install; AGENT, the next dri-chain-gate review)

- VM gate-start -> gate-end: from stage-events.jsonl, for each item, take the `gate-start "vm <sha>"` and the next
  `gate-end "vm rc=..."`. Report the median over the next 5 VM chain gates after the install time. Target: <= 95 min. Basis
  today: 111-148 min at 8 workers (MEASURED, reviews/chain-gate-20-20261121.md). The width alone does not change slot
  waits.
- Slot wait: for each item, minutes from `gate-wait "waiting: another VM gate holds vm1 ..."` to its next `gate-start "vm ..."`.
  Compare the sum and median with the 1981 item-min of the last 20 gates.
- Check: the route events ("VM load X + 8 workers < 32") still say 8 after the install.

## Notes for the DRI

- Memory (UNVERIFIED): VM_GATE_MEM stays 48G. The 14-worker basis (gate50) ran on ve-cloud-2, and nothing here measures a
  14-worker gate.py's peak RSS on VM1 (32 cores, 125 GB). If the first 14-worker VM gate hits the 48G scope limit, the
  quick fix is VM_GATE_MEM (no code change).
- Conservative choice: VM_ROUTE_WORKERS does not fall back to VM_GATE_WORKERS (the task says "regardless of VM_GATE_WORKERS").
  An item that sets VM_GATE_WORKERS no longer moves its route. Today no caller sets it (grep of manage-agents *.sh/*.py: only
  chain-watch.py ALLOW and the tests).
- test-pinned-require-hosts.py is stale for chain-gate.sh (pre-existing, above). It is not in this item's scope.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no Lean or relay change.
2. Every deliverable built: PASS. Item 1 is staged-changes.diff. Item 2 is test_chain_gate_vm_width.py, failing first
   (live-failfirst.log) and passing (staged.log), with vm_cancel and empty_ve_diff passing on .new. Item 3 is `zsh -n`
   (SYNTAX-OK). No install (install read).
3. Tests can fail: PASS, seeded-bugs.json S1-S4, each FAIL in test_chain_gate_vm_width.py, and the live file fails (10).
4. Python/Lean/Rust agree: N.A., none changed.
5. R8 binding: N.A., no binding change.
6. Gate evidence matches the final HEAD: PASS. selected.log is the selected run on 3b06074d14 (evidence only, docs/). This
   commit adds only this report. The chain gate runs on the final HEAD.
7. No unsigned item: PASS. There is no DELTA row and no reserved signature (task: "No DELTA row").
8. User-visible change in DELTA: N.A. The change is an infra script default, not a VE user-visible delta (task).
9. Test selection: N.A., no VE code changed. The selected run found 251 units (selected.log).
10. Lean statements: N.A.
11. Budgets fail closed: N.A., no budget or limit logic changed (MAC_LAST_VM_LOAD is unchanged; route boundary tested at
    23/24 in test_chain_gate_vm_width.py (iii)).
12. CPU/memory regression: N.A. for VE code. For the VM: the gate's CPU stays capped by its slot (VM_GATE_MAX 1). Memory is
    UNVERIFIED (Notes).
13. Test-removed trailer: N.A., no test removed or renamed (the vm_cancel test changes one expected value).
14. Both directions, cited evidence, spec re-read: PASS. Both directions: load 23 -> VM and 24 -> Mac. Default and override
    in (i)/(ii). Every claim above names its log. Spec re-read: "VM_GATE_WORKERS default 14 for both the gate and the R13
    rerun; route test keeps 8 via its own variable; VM_GATE_MAX 1; CPUWeight 1000" against
    prompts/task-cg-vm-gate-width-1121.txt:7.
15. Overclaim, silent cut, new checks fail, limits: PASS. "unchanged" claims cite staged-changes.diff (5 hunks only). No
    deliverable cut. Every new check has a seeded bug (S1-S4). Limits: N.A.
