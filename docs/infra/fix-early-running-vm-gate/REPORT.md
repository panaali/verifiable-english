# fix-early-running-vm-gate: REPORT

Item: fix-early-running-vm-gate (reviews/dri-decisions-20261117-cg1218.md item 1; guard stage:chain-gate).
Infra item: the product change is in manage-agents (`chain-gate.sh`), not in this repository. This directory
keeps the saved evidence, as the earlier infra items do (docs/infra/tm-actions-deadline, docs/infra/digest-main-line).

Status: STAGED, reviewed (review-ov MERGE) and INSTALLED by the decider at 2026-11-17 13:45Z
(CURRENT-STATE.md line "install reads INSTALLED ... (3) fix-early-running-vm-gate chain-gate.sh (bak
.bak-20261117vmcancel; test_chain_gate_vm_cancel 21/21 ...)"). The live chain-gate.sh has had later installs on top
(chain-gate.sh.new-vm1w and others). The fix is still in the live file, and the test below passes on it.

## Defect

With FIX_EARLY, infra-item.sh writes `<item>-gate.cancel` when the overlapped review says FIX. chain-gate.sh read the
file only once before the VM gate started. The VM gate (`uv run python tools/gate.py --workers ${VM_GATE_WORKERS:-8}`)
and its R13 rerun (`gate.py --rerun-failed`) ran without a cancel poll: p1-ready-unstartable-alert waited 1.72 h on a
cancelled VM gate (2026-11-16).

## Change (chain-gate.sh; diff in installed-changes.diff, pre-install backup chain-gate.sh.bak-20261117vmcancel)

- `vmg()`: with `CHAIN_GATE_CANCEL` set, the VM gate and its R13 rerun run through the existing `selrun()`. That gives
  them their own setsid session, a poll every 5 s, TERM to the group on the cancel file, KILL after 60 s, and `cx=1`.
  With it unset, the old foreground subshell `(cd $w && VE_REQUIRE_PINNED_SOURCES=1 uv run python tools/gate.py ...)`
  runs unchanged, with the same rc.
- `vmcx()`: after a cancel, removes `$w/gate-result.json` (gate.py's failed placeholder or the partial record), writes
  `ev gate-cancelled "vm gate stopped: $CHAIN_GATE_CANCEL (FIX_EARLY[; R13 rerun])"` and exits 4, the same as the
  ve-cloud-2 branch. When the rerun is cancelled, the full record is kept as `$M/vm-gate-<label>.full.json`, never as
  gate-result.json.
- The pre-start check (old :349, "no VM gate") is unchanged.

## Tests (tools-local/test_chain_gate_vm_cancel.py, new; stub `uv` plus a stub tools/gate.py in a scratch worktree, M flags off so the VM branch runs)

| Case | Pre-install file (bak-20261117vmcancel) | Staged chain-gate.sh.new-vmcancel | Live chain-gate.sh (2026-11-17 re-run) |
|---|---|---|---|
| (1) cancel 5 s after the start: group gone within 70 s, exit 4, event, no record | FAIL | ok | ok |
| (1k) stub ignores TERM: KILL after 60 s | FAIL | ok | ok |
| (2) cancel during the R13 rerun | FAIL | ok | ok |
| (3) unset: runs to completion, rc 0/1 passed through, R13 as before | ok | ok | ok |
| (3s) set, no file: rc 0/1 and R13 passed through, record kept | ok | ok | ok |
| (4) file present before start: exit 4, "no VM gate", gate.py never started | ok | ok | ok |
| Total | FAIL: 11 failure(s) (preinstall.log) | PASS: 0 failure(s) (staged.log) | PASS: 0 failure(s) (live.log) |

(5) The other chain-gate suites pass on the live file (other-suites.log): test_defer_heavy, test_gate_reuse,
test_mac_last_resort, test_vm1_gate_weight and test_builder_test_runs all return rc 0. Of the files matching
`tools-local/test_chain_gate*.py`, the only one is the new test. `zsh -n chain-gate.sh.new-vmcancel` is clean.

## Seeded bugs (seeded-bugs.json; planted in /tmp copies of the staged file, never in the live file)

- S1 `vmg()` runs gate.py without the cancel poll: test (1) and (1k) fail, FAIL: 11 failure(s) (seed-s1.log).
- S2 `vmcx()` leaves gate-result.json: (1), (1k) and (2) "no gate-result.json" fail, FAIL: 3 (seed-s2.log).
- S3 no `vmcx` after the R13 rerun: (2) exit 4, event and record fail, FAIL: 3 (seed-s3.log).
- S4 `selrun()` sends no KILL after the 60 s grace: (1k) fails, FAIL: 1 (seed-s4.log).

File for all four: /home/seyran/code/manage-agents/chain-gate.sh. Language: shell (zsh). No Lean, Python or Rust
product code of this repository changed.

## Install (done by the decider, 2026-11-17 13:45Z; the commands asked for)

    cp -p /home/seyran/code/manage-agents/chain-gate.sh /home/seyran/code/manage-agents/chain-gate.sh.bak-20261117vmcancel
    cp -p /home/seyran/code/manage-agents/chain-gate.sh.new-vmcancel /home/seyran/code/manage-agents/chain-gate.sh.new && mv /home/seyran/code/manage-agents/chain-gate.sh.new /home/seyran/code/manage-agents/chain-gate.sh

Current state: the backup chain-gate.sh.bak-20261117vmcancel exists. chain-gate.sh.new-vmcancel still exists and is
byte-identical to chain-gate.sh.bak-20261117-vm1w, which is the live file as it was before the later vm1w install.
The live file has since been changed by later installs, and the VM cancel test still passes on it (live.log).
No service restart is needed: each new chain-gate.sh run reads the file, and running chains keep their inode.
The install read message was sent in the first round and was handled at 13:45Z, so no new message was sent.

## Pre-review round (this commit)

The pre-review gate failed `[commits]` (0 commits ahead): the first round left no commit in this repository. This
commit adds this evidence directory. No product file of the repository changed. No DELTA rows: there is no Lean or
trust-base change.

SIZE: 19 product (chain-gate.sh diff lines, comments included), 216 tests, about 110 other hand-written lines (this report and seeded-bugs.json).

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relay or Lean answer touched).
2. Deliverables built, no rule broken: PASS. Fix, test cases (1)-(5), staged file with zsh -n clean, install read, all installed.
3. Tests and gates can fail: PASS. Pre-install 11 failures; seeds S1-S4 each fail test_chain_gate_vm_cancel.py.
4. Python/Lean/Rust agree: N.A.
5. R8 binding: N.A.
6. Gate evidence matches the final HEAD: PASS. The chain gates this HEAD; this commit is docs only.
7. No unsigned item: PASS. No DELTA rows.
8. DELTA: N.A. No user-visible VE change.
9. Test selection: N.A. No repository code changed.
10. Lean statements: N.A.
11. Budgets and deadlines fail closed: PASS. A TERM-ignoring gate is KILLed after 60 s (test (1k)), and a cancel
    always exits 4 with no record (tests (1), (2)).
12. CPU and memory: PASS. One 5 s poll loop, only while CHAIN_GATE_CANCEL is set; unset is unchanged (test (3)).
13. Removed or renamed tests: N.A. None removed.
14. Both directions: PASS. Fails on the pre-install file and passes on the staged and live files (tables above).
15. Four FIX classes: PASS. Unset behaviour unchanged (3), cancel before the start unchanged (4).

## Notes for the DRI

- Pre-existing main-known-red tests: none touched.
