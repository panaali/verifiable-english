# ps1014-armshard-b1m1: test-armshard B1 and M1 against the installed train

Row ps1014-armshard-b1m1 (infra; decision reviews/dri-decisions-20261109-trainfix-seed.md, R21 catch-up 2026-11-17).
The deliverable is a harness fix in /home/seyran/code/manage-agents/test-harness/ps1014/harness/test-armshard.zsh
(backup: test-armshard.zsh.bak-20261119-b1m1). The installed merge-train.sh and the stubs are unchanged. This directory
holds the evidence. No VE product code changed. No DELTA rows.

## Triage: the harness was out of date. merge-train.sh's flag-off behaviour is unchanged.

Both failures come from later DRI-ruled train changes that the 2026-11-02 harness did not know about. They are not
ARM_MAC_FIRST flag-off regressions. Evidence: `zsh test-armshard.zsh` before the fix (before.log: `40 ok, 2 FAIL`), and
`diff /tmp/ps1014mf/m1a.{log,calls} /tmp/ps1014mf/m1b.{log,calls}` on that run. The diff had exactly these rows:

| diff row (installed vs the .bak-20261102-arm-leg-mac-first baseline) | source |
|---|---|
| log `sharded aarch64 leg of item: shard deadline 105 min (ve-mac-1 online: DRI rule lp1201 Q1)` | 2026-11-08 DRI rule lp1201 Q1 (reviews/dri-decisions-20261108-lp1201.md item 1; 45 -> 105 by adv1313 item 1), merge-train.sh `shleg` |
| calls: one more `ssh ... ve-mac-1 true` (the `macup` probe) | the same rule: shleg asks macup to choose the deadline |
| calls: `ARMSH ... deadline=180` -> `deadline=105` | the same rule: ve-mac-1 is online in the stub (senv default) |
| log `fidquote step of item: not run (...)` | 2026-11-13 fidquote step (backup merge-train.sh.bak-20261113fidquote) |
| log `trust baseline after item not recorded: no tools/trust_map.py on main` | 2026-11-12 tbr trust-baseline-record (`trustrec`; first in the 20261113fidquote backup) |

- B1 failed only on `deadline=180`. The stub has ve-mac-1 online, and the lp1201 rule gives that case 105, so 180 was the
  pre-rule expectation.
- M1 compares the installed script with a fixed 2026-11-02 baseline. Each of the three changes above adds lines whatever
  ARM_MAC_FIRST says.
- No row of that diff involves ARM_MAC_FIRST.

## Fix (harness-changes.diff, 19 changed lines)

- **B1** now expects `deadline=105` and the log line `shard deadline 105 min (ve-mac-1 online: DRI rule lp1201 Q1)`.
- **B5b** (ve-mac-1 unreachable) now also asserts `deadline=180` and `shard deadline 180 min (ve-mac-1 unreachable: ...)`.
  This tests the rule's other side.
- **M1** maps the baseline through the later changes listed above and through nothing else:
  - `m1later` drops the three new log-line kinds from both sides.
  - `m1lp` turns the baseline's `deadline=180` into 105.
  - `m1probe` drops only the first `macup` probe from the installed side.

  The equality check also asserts `PROBE = 0` (no macslot probe with the flag off). When M1 fails it writes
  /tmp/ps1014mf/m1.diff and prints the head of it, which makes the next triage quick. The comment in the test says to add a
  new flag-independent line there together with its ruling, or to file the train bug.

## Results

- After the fix: `zsh test-harness/ps1014/harness/test-armshard.zsh` -> `== armshard: 42 ok, 0 FAIL` (after.log, last line).
  The installed merge-train.sh at that run is sha256 68f36b19... (sha256.txt).
- Seeded bugs (seeded-bugs.json, seed-s*.log, seed-s*.patch). Each was planted in a /tmp copy of merge-train.sh and run
  through a copy of the harness:
  - control s0 (the installed script): `42 ok, 0 FAIL`.
  - S1 (online deadline back to 180): `40 ok, 2 FAIL`. B1 and M1 fail.
  - S2 (unreachable deadline 105): `41 ok, 1 FAIL`. B5b fails.
  - S3 (an extra macup probe with ARM_MAC_FIRST off): `41 ok, 1 FAIL`. M1 fails. This shows that `m1probe` hides no more
    than the one ruled probe.

- Selected tests, run once on 9b8257dcd6 plus this evidence: `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`.
  It ran 10 units with exit=0 and `0 failed` (it ran on the VM because of MAC_LAST).
- Light lane: `light-lane.py check` printed `NOT 603 changed lines ... (13 files)`. All of those lines are evidence logs.
  `trust_mutants.py --plan` gives `"mutants": 0` (trust-mutants-plan.log): there is no product definition to sweep, so no
  sweep ran.

No train bug was filed: the triage found none.

SIZE: 0 product, 19 tests (harness lines changed, harness-changes.diff), ~96 other hand-written lines (this report and seeded-bugs.json).

## Notes for the DRI

- `delegate-cw.py` printed `own session not found (needs VE_STEP and CLAUDE_CONFIG_DIR from dri-delegate.sh, or a transcript path)`,
  so the context window is not MEASURED for this item.
- The manage-agents harness edit is not committed in manage-agents. It is picked up by that repo's periodic snapshot, as for
  the earlier harness .bak edits.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relay or Lean change.
2. Deliverables built, no rule broken: PASS, test-armshard 42/42 (after.log) and the triage table above.
3. Tests and gates can fail: PASS, seeds S1-S3 (seeded-bugs.json, seed-s1..s3.log).
4. Python, Lean and Rust agree: N.A., no product code changed.
5. R8 binding: N.A., no binding change.
6. Gate evidence matches the final HEAD: PASS, the chain runs gate.py on the final HEAD. The harness evidence names the
   merge-train.sh sha256 it ran against (sha256.txt).
7. No unsigned item: PASS, there are no DELTA rows and no signature is reserved.
8. User-visible change in DELTA: N.A., this is an ops harness only, with no VE user-visible change.
9. Test selection: PASS, the selected run had exit 0 (/tmp/b1m1-select.log summary quoted above).
10. Lean statements: N.A., no Lean.
11. Budgets and deadlines fail closed: PASS, B1 (105 online) and B5b (180 unreachable) pin both sides of the lp1201
    deadline. Seeds S1 and S2 fail them.
12. CPU or memory: N.A., harness assertions only.
13. Test removed or renamed: N.A. No ok() was removed. The M1 equality ok's name gained "(no macslot probe)", and the count
    stays 42.
14. Both directions and cited evidence: PASS. The deadline is tested online and unreachable (B1, B5b). M1 accepts the
    installed script (after.log) and refuses a flag-off change (S3). Every claim above cites a log in this directory.
15. Overclaim, silent cut, a new check that can fail, limits: PASS. There is no cut. Each new assertion has a seed (S1, S2,
    S3). There are no limits.
