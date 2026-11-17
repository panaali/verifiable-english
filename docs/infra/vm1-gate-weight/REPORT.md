# vm1-gate-weight: VM1 chain gates get ve-cloud-2's rule (weight 1000, one gate per host)

Status: BUILT and STAGED; INSTALL WAITS FOR DECIDER READ. No DRI signature needed (no DELTA row, no Lean or trust-base change).
HEAD: this commit on infra/vm1-gate-weight (VE side: evidence only). Staged: `chain-gate.sh.new-vm1w` (2fd93d12…, after the review F1 fix; was cc914a94…), `iso.sh.new-vm1w` (cff1c75d…, unchanged), new test `tools-local/test_vm1_gate_weight.py` (ba8c75b3…; was f7ddf636…).
Change: the VM gate and its R13 rerun run as `zsh $M/iso.sh vmgate-<label>-<pid> ${VM_GATE_MEM:-48G} -- <same gate.py command>`. iso.sh gives `vmgate-*` CPUWeight 1000. Each gate holds one of `VM_GATE_MAX` (default 1) slots, `$M/locks/vm1-gate.lock`, for the gate and its rerun. A gate that has to wait honours CHAIN_GATE_CANCEL.
Open: the decider installs it (HUMAN). MEASURE: the last 72 h had 2 overlaps (118 min). From Nov 18, about 14 gates a day at about 2.3 h each would exceed 24 gate-hours a day on one slot. That argues for VM_GATE_MAX 2 or more workers per gate (Notes). The default stays 1.

SIZE: 87 product (chain-gate.sh +79/-4, of which the F1 fix is +40/-6; iso.sh +4/-1), 541 tests (test_vm1_gate_weight.py, new; the F1 fix +129/-4), 73 other hand-written lines (measure.py).

## Review fix F1 (vm1-gate-weight-review.final.md, B): stopping a chain stops its VM gate

- **Finding:** iso.sh moved gate.py into its own `ve-vmgate-*.scope`, so stopping the chain's scope (stop-at-boundary.sh,
  freeze-mover.sh, a manual stop) killed the chain and freed the vm1 slot, but left gate.py running for hours. The next
  gate then started beside it. This happened at both `vmg` call sites, with and without the cancel file, and in the rerun after a failed ve-cloud-2 gate.
- **Fix (class: anything that ends the chain, not one stop path):** the scope's main process is now a watcher (`$vwatch` in
  chain-gate.sh.new-vm1w, inline: one file to install). It runs gate.py as its child, in its own process group, so
  selrun's group kill still reaches it. It polls the chain every `VM_GATE_WATCH` s (1) by pid plus start time. A zombie
  counts as gone: a killed chain stays a zombie until its parent reaps it, and the first test run caught this. When the
  chain is gone, the watcher runs `systemctl --user stop "$vunit"`, which ends the gate's scope and everything in it.
  If anything is left (no systemd, or the stop failed), it TERMs the gate's process tree and KILLs it after
  `VM_GATE_STOP_GRACE` s (30). A watcher that gets TERM, INT or HUP does the same. `$vunit` is now one variable, shared by
  the watcher and `vmcx`.
- **The slot is kept until the gate's scope is gone:** the watcher records its scope's cgroup, or its own pid and start
  time when it is not in a `ve-vmgate-*` scope, in `<lock>.gate`. A chain that gets the flock while that record is live
  releases the flock and keeps waiting. Its wait event names `<label>: gate of a stopped chain`. A gate that ends by
  itself removes its record, so a stray process left in a finished scope never holds the slot.
- **PROBE F1** (`probe-f1.log`): before, `orphan gate.py alive: True`, exit 1. After, `False`, exit 0.
- **Regression tests** (test_vm1_gate_weight.py, new cases (8a), (8b), (8c), (9r) and (9s)):
  - (8a) the VM gate, no cancel file; (8b) the R13 rerun, CHAIN_GATE_CANCEL set; (8c) the rerun after a failed ve-cloud-2
    gate. In each, SIGKILL goes to the chain shell only. The gate.py is gone, `systemctl --user stop` gets a pattern that
    matches its unit, and the gate was TERMed. In (8a) and (8b), a second chain that waits gets its gate.py started only
    after the first exited: the first ignores TERM for 2 s.
  - (9r) the probe on the real systemd user manager, with a waiting second chain; the stopped chain's ve-vmgate scope is gone.
  - (9s) a stray in a finished scope keeps no slot.
  - (9r) and (9s) are skipped, with a note, where `systemd-run --user --scope` does not work.
  - Check (5) "systemd-run pid = gate pid" became "systemd-run pid = gate pgid": the gate is now the watcher's child. The
    property tested is the one that matters, that selrun's group kill reaches the gate.
- **Runs:** `run-staged-f1.log` 60 ok, 0 FAIL. `run-pre-f1.log` is the pre-fix staged file (cc914a94): 13 FAIL, all in
  (8a)–(8c) and (9r). `run-suites-f1.log`: test_chain_gate_vm_cancel, test_gate_reuse, test_mac_last_resort and
  test_defer_heavy all rc 0 on the fixed file. Diffs: `chain-gate.sh.new-vm1w.f1.diff` and `test_vm1_gate_weight.f1.diff`.
- **Not done (review notes F2–F5, C, not filed):** F2's leftover gate-result.json on a first-slot cancel, F3's scratch-tree
  coverage and F4's `<label>-<pid>` pattern overlap are unchanged. F5 (stale-6h.py and backlog.py do not know `gate-wait`) is already with the DRI.

## Base

- Built on `chain-gate.sh.new-vmcancel` (row fix-early-running-vm-gate). It was installed during this build, so live
  `chain-gate.sh` = `chain-gate.sh.new-vmcancel` = md5 `dd1904863dcf6df2c14bea053c382f69` (`md5.txt`). The staged file
  therefore needs no rebase: `chain-gate.sh.new-vm1w.diff` is its diff against both.
- `iso.sh.new-vm1w` is live `iso.sh` (md5 `493df1e17a9eb072cf436503171e1788`) plus `|vmgate-*` in the weight-1000 case.
  Another row (gate-cpu-over-tmfill) has staged `iso.sh.new-gcpu`, which is not installed. I did not bundle it. If it is
  installed first, add the one word to the new live file instead (the install commands below check the md5).

## Deliverables (task rows) and evidence

| Task row | Delivered by | Test (tools-local/test_vm1_gate_weight.py check names; `run-staged.log`) |
|---|---|---|
| (1) WEIGHT: VM gate + R13 rerun through iso.sh `vmgate-<label>`, cw 1000; builders stay 100; VM_GATE_MEM 48G | `vmg()` in chain-gate.sh.new-vm1w; iso.sh.new-vm1w case | (i) vmgate-x→1000, chain-foo / vm1-gate-weight→100, merge-x / integ-y→1000, exp-z→25; (1) two scopes, unit `ve-vmgate-a-<pid>-<t>`, CPUWeight 1000, MemoryMax 48G; VM_GATE_MEM sets MemoryMax |
| Cancel still stops the gate inside its scope | selrun's group kill (systemd-run --scope keeps pid/group/session: probed live, below) + `systemctl --user stop ve-vmgate-<label>-<pid>-*.scope` in `vmcx` | (5) group gone, exit 4, the stop pattern matches the unit name systemd-run was given |
| (2) ONE GATE PER HOST, incl. the R13 rerun, one hold | `vlock()` (zsystem flock, fcntl), called before the VM gate and before the rerun (no-op when held) | (2) second gate.py starts after the first ended, rc 0 / 1 passed through; (4) rerun sees the same holder record/mtime, a second chain starts only after the rerun |
| Wait: no slot timeout; CHAIN_GATE_CANCEL → exit 4 + gate-cancelled; one "waiting: another VM gate holds vm1 (<holder>)" event | `vlock()` loop, VM_GATE_POLL (10 s) | (2) one gate-wait event naming the holder; (2u) stale holder → "(unknown)"; (3) cancel while waiting → exit 4 while the holder still runs, event "no VM gate: … while waiting for vm1", gate.py never started, lock free after |
| selrun, collection check, Mac / ve-cloud-2 paths take no lock, keep weight | `vlock` only in the VM-gate and rerun branches | (6) lock held elsewhere: a ve-cloud-2 pass and the selected-test fallback finish without waiting, no scope; a rerun after a failed ve-cloud-2 gate waits for the slot, then runs scoped |
| (3) VM_GATE_MAX (default 1) | slot files vm1-gate.lock, vm1-gate-2.lock, … | (7) VM_GATE_MAX=2: both gates start before either ends |
| Failing-first | — | `run-live.log` (live of 13:10Z, md5 358b0b30…): 19 FAIL; `run-live-vmcancel.log` (live = vmcancel): 18 FAIL; `run-staged.log`: 38 ok, 0 FAIL |
| (5) Existing suites on the staged files | — | `run-suites.log`: test_chain_gate_vm_cancel, test_gate_reuse, test_mac_last_resort, test_defer_heavy (CG / CHAIN_GATE_SCRIPT = staged) rc 0; test_gate_one_per_host, test_tm_drain_vm1_idle, test_builder_test_runs rc 0; test_iso_weight_tmfill with iso.sh.new-vm1w: 1 failure, the same as on live iso.sh (it tests the uninstalled iso.sh.new-gcpu) |
| MEASURE | `measure.py` → `measure-72h.txt` | below |
| STAGE, zsh -n clean, no mv | `zsh -n` on both: clean (`zsh -n … && echo zsh-n-clean`) | — |

Live probe (real systemd, not a stub): `setsid zsh iso.sh.new-vm1w vmgate-probe-<pid> 1G -- sleep 120` → unit
`ve-vmgate-probe-…-1794922554.scope`, `Slice=ve-workers.slice`, `CPUWeight=1000`, `MemoryMax=1073741824`.
`systemctl --user stop "ve-vmgate-probe-<pid>-*.scope"` returned 0 and left no unit. A separate `setsid -w` probe showed
that the command in a `systemd-run --user --scope` keeps the caller's pid, process group and session, so selrun's
`kill -- -$p` reaches it.

## MEASURE (read only; `measure-72h.txt`, taken 2026-11-17T13:36Z over the previous 72 h of stage-events.jsonl)

Pairing: VM gate gate-start/gate-end events, one item's gate and its rerun within 5 min = one hold.

- MEASURED: 15 VM gate runs (12 holds, 12 items). 2 overlapping pairs, 118.1 min in all: fidq-dri-read-exact |
  pf-f7-timed-act for 4.7 min (11-15 14:13Z), and rsp-b-repair-1115 | counter-fix-unfinished-final for 113.4 min
  (11-16 19:54–21:47Z). At most 2 at once. Time at concurrency 2: 118.1 min of 72 h. A VM gate (tm-sc7-rejudge) was
  running at the time of the measurement.
- ESTIMATE (one per host, first come first served by start time, durations unchanged): 3 of 12 holds would have waited,
  147.6 min in all, max 113.4 min (counter-fix-unfinished-final), 49.2 min mean over those that wait.
- ESTIMATE, from Nov 18: the same window had 31 ve-cloud-2 chain gates (median 69.8 min) and 12 VM gates (median
  136.7 min). The 17 "mac" gates had a median of 0.7 min (the runner was down; they fell back). When ve-cloud-2 ends,
  about 43 full gates per 72 h (about 14.3 a day) land on VM1. At the measured VM median of 2.28 h with 8 workers, that
  is about 32.7 gate-hours a day, more than the 24 h one slot has. At the fastest VM gates (97–103 min) it is about 24 h a
  day, already at capacity. With VM_GATE_MAX 1 and VM_GATE_WORKERS 8 the queue would therefore grow during busy days.
  This argues for VM_GATE_MAX 2, or for ve-cloud-2's other half of the rule: one gate with the host's cores (workers
  raised; on ve-cloud-2, 30 workers gave a median of 69.8 min). Not measured: how much weight 1000 shortens a VM gate at
  load ~40, and whether two weight-1000 8-worker gates each keep single-gate speed. The default is unchanged (1).

## Seeded bugs (`mutants.json`; each planted in a /tmp copy run through the CG / ISO hooks; the staged files were never edited, md5s in `md5.txt`)

| id | file | mutation | test that fails (checks) |
|---|---|---|---|
| S1 | iso.sh.new-vm1w | `vmgate-*` dropped from the 1000 case | test_vm1_gate_weight.py: (i) vmgate-x→1000, (1) unit…CPUWeight 1000, (2) both scoped at 1000, (6) rerun scoped (5 FAIL) |
| S2 | chain-gate.sh.new-vm1w | VM gate's `vlock` disabled | (1) lock held, (4) same hold, (2) one at a time, (2) gate-wait, (3) cancel while waiting … (9 FAIL) |
| S3 | chain-gate.sh.new-vm1w | rerun releases and re-acquires | (4) rerun inside the same hold (1 FAIL) |
| S4 | chain-gate.sh.new-vm1w | cancel check in the slot wait disabled | (3) exits 4 while the holder runs, (3) event, (3) gate.py never started (3 FAIL) |
| S5 | chain-gate.sh.new-vm1w | stop pattern `ve-vm-gate-…` | (5) systemctl stop pattern matches the unit (1 FAIL) |
| S6 | chain-gate.sh.new-vm1w | holder liveness check removed | (2u) stale holder → unknown (1 FAIL) |
| S7 | chain-gate.sh.new-vm1w (F1) | the watcher never sees its chain gone | (8a)–(8c) gate gone / scope stopped / TERMed, (9r) gate gone (10 FAIL) |
| S8 | chain-gate.sh.new-vm1w (F1) | `vglive` always false: the slot ignores a stopped chain's running gate | (8a), (8b), (9r) second gate starts only after the first exited (3 FAIL) |
| S9 | chain-gate.sh.new-vm1w (F1) | no watcher in the scope (the pre-F1 command) | (8a)–(8c), (9r) (13 FAIL) |
| S10 | chain-gate.sh.new-vm1w (F1) | a zombie chain counts as alive | (8a)–(8c), (9r) gate gone (10 FAIL) |
| S11 | chain-gate.sh.new-vm1w (F1) | a gate that ended by itself keeps its `.gate` record | (9s) a stray keeps no slot (1 FAIL) |
| S12 | chain-gate.sh.new-vm1w (F1) | the watcher does not `systemctl stop` its scope | (8a)–(8c) scope stopped (3 FAIL) |

S7–S12: `mutants-f1.json` (each mutation, its failing checks and rc), planted in /tmp copies run with `CG=`.

Changed languages: zsh only (manage-agents placement scripts). No Lean, Python product or Rust product code in VE changed.
I wrote the test file in Python.

## Install (HUMAN: decider read; not done by me)

INSTALL WAITS FOR DECIDER READ. Both files are read on each run (no service restart). Check, back up, then mv the `.new` copies:

```
cd /home/seyran/code/manage-agents
[ "$(md5sum < chain-gate.sh | cut -c1-32)" = dd1904863dcf6df2c14bea053c382f69 ] && [ "$(md5sum < iso.sh | cut -c1-32)" = 493df1e17a9eb072cf436503171e1788 ] && echo BASE-OK
zsh -n chain-gate.sh.new-vm1w && zsh -n iso.sh.new-vm1w && python3 -I tools-local/test_vm1_gate_weight.py
cp -p chain-gate.sh chain-gate.sh.bak-20261117-vm1w && cp -p iso.sh iso.sh.bak-20261117-vm1w
mv chain-gate.sh.new-vm1w chain-gate.sh && mv iso.sh.new-vm1w iso.sh
```

If BASE-OK is not printed for iso.sh (for example, iso.sh.new-gcpu was installed first), do not mv `iso.sh.new-vm1w`.
Add the one word to the live file instead, then check it:
`cp -p iso.sh iso.sh.bak-20261117-vm1w && sed 's/|integ-\*) cw=1000/|integ-*|vmgate-*) cw=1000/' iso.sh > iso.sh.new && zsh -n iso.sh.new && mv iso.sh.new iso.sh`.
If chain-gate.sh moved, rebase the hunks in `chain-gate.sh.new-vm1w.diff` (+79/-4).
Revert: mv the two `.bak-20261117-vm1w` files back. A gate already running keeps the script it started with.

## Notes for the DRI

- Conservative choices I made without asking:
  - No slot timeout, as the task says.
  - A missing `$VM_GATE_ISO` (default `$M/iso.sh`) runs the old unscoped command with a stderr note, so the scratch-M
    suites (test_chain_gate_vm_cancel) keep passing. Production always has iso.sh.
  - The waiter names the holder only from a live pid in `<lock>.holder`. A holder writes that file just after its flock,
    so the waiter retries for up to 3 polls before it says "unknown". This was a real race, found in a seeded-bug run.
  - A cancel during the rerun's wait removes gate-result.json, as vmcx does for a cancelled rerun. The full record is
    kept as vm-gate-<label>.full.json.
- The scope name is `vmgate-<label>-<chain pid>`, not just `vmgate-<label>`. The pid makes the `systemctl --user stop`
  glob match only this chain's unit. It is still matched by the `vmgate-*` case.
- VM_GATE_MAX is read from the environment of chain-gate.sh. To set 2 for every chain, export it in the launchers or
  change the default `${VM_GATE_MAX:-1}`. Neither was done here (see MEASURE).
- No trust_mutants sweep. light-lane printed NOT (386 lines, all docs/evidence), but the item changes no Lean (R16 is
  about Lean growth only).
- Selected tests of this branch: `mac-pytest.sh --select` → GitHub Actions run vm1-gate-weight-baeb2b98-t923172, 5 units,
  5 passed, exit 0.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no Lean answer or relay touched.
2. Deliverables built, no rule broken: PASS, the deliverables table above; each row names its test in test_vm1_gate_weight.py.
3. Tests and gates can fail: PASS, `mutants.json` S1–S6 and `mutants-f1.json` S7–S12 (each fails test_vm1_gate_weight.py); `run-pre-f1.log` fails on the pre-F1 staged file; `run-live.log` and `run-live-vmcancel.log` fail on the live files.
4. Py/Lean/Rust agree: N.A., no checker code changed.
5. R8 binding: N.A., no Lean answer fields read.
6. Gate evidence matches final HEAD: PASS, the full gate runs on the final HEAD by the chain. Evidence files are saved, not live diffs (md5.txt, measure-72h.txt with its timestamp).
7. No unsigned item: PASS, no DELTA row or trust growth (the task says none).
8. Every user-visible change in DELTA: N.A., no VE user-visible change (placement scripts only).
9. Test selection finds tests: PASS, the selected run picked 5 units for a docs-only diff (the GitHub Actions run above). The staged scripts are covered by test_vm1_gate_weight.py, not by VE selection.
10. Lean statements: N.A., no Lean.
11. Budgets fail closed: PASS, the wait has no timeout by design (task). Cancel ends it with exit 4, never a pass: test_vm1_gate_weight.py (3). The test waits on events; its sleeps are stub work and fixed outer limits only (tools-local script, not the VE suite).
12. No CPU/memory regression: PASS, the change lowers contention (one gate at a time, weight 1000). Memory is capped by VM_GATE_MEM 48G: (1) MemoryMax checks.
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions, cited evidence: PASS. Refuse side: (2), (3), (4). Accept side: chain name keeps 100 (i); ve-cloud-2 and selected runs not blocked (6); VM_GATE_MAX 2 runs two (7). Each claim here names a log file.
15. Four classes: overclaim PASS (claims scoped to the stubbed tests and one live probe; unmeasured effects named in MEASURE). No silent cut PASS (all task rows in the table). New checks can fail PASS (S1–S6). Limits charged before work N.A. (no input limits).
