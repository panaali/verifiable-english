# actions-mismatch-scope-1120: scope cloud-jobs/ACTIONS_MISMATCH by the job that raised it (build report, 2026-11-20)

Spec: reviews/dri-decisions-20261120-actions-mismatch-scope.md item 1 (APPROVED) and reviews/train-legs-time-1120/REPORT.md section 3.
Nothing installed by the builder (INSTALL READ). Every edit is staged as `<file>.new-amscope` in the manage-agents root.
No VE product code changed, so there is no VE product diff, DELTA row or trust-mutant sweep.

Saved record (added on the pre-review gate's [commits] FAIL, 0 commits ahead): this directory, docs/infra/actions-mismatch-scope-1120/,
is the VE branch's one commit, following earlier infra items (docs/infra/chain-gate-empty-ve-diff, docs/infra/remote-dead-job-reaper).
It holds this report, the staged-vs-backup diff of each changed script (`<file>.amscope.diff`, made against `<file>.bak-20261120amscope`),
the new files (`mismatch-scope.sh.new-file`, `test_actions_mismatch_scope.py.new-file`), the test logs on the old and staged scripts,
the harness baseline/new failing sets, the seeded-bug scripts (`seed.py.txt`, `seed9.py.txt`) and results (`seeds.txt`), `md5.txt` and
`syntax.txt` (zsh -n of all 5 staged files). The acting DRI has since installed the staged files (CURRENT-STATE 06:42Z; installed == staged per md5.txt).
No DELTA row and no DRI signature reserved: the decision says this is a shell guard scope, not a trust-base change.

SIZE: 51 product (mismatch-scope.sh 29 + merge-train.sh 9 + gha-arm-shard.sh 5 + arm-postcheck.sh 5 + gha-arm-gate.sh 3), 246 tests, 0 other hand-written lines (this report excepted).

## 1. Diff summary

- NEW `mismatch-scope.sh` (staged `mismatch-scope.sh.new-amscope`), the one copy of the rule. It is sourced, never run.
  `mismatch_blocks_gate <file>` returns rc 0 (blocks) or rc 1 (does not block) and prints nothing.
  - rc 1 (does not block): the file is absent, or every line has the form `<YYYY-MM-DDTHH:MMZ> <job>: <why>` and every job is `tm-*`, `testmap-*` or `select-*`.
  - rc 0 (blocks): the path exists but is not a readable regular file; the file is empty; a line does not parse (blank, no
    timestamp, no `: `, characters outside `[A-Za-z0-9._-]` in the job); or a line names any other job. That covers the gate-leg
    prefixes `armsh-*`, `x86sh-*`, `cand-*`, `post-*` and `arm-*`, and also any job of no known kind.
- `merge-train.sh`: after `M=`, it sources the helper. If the helper cannot be sourced, it defines a fallback that keeps the old rule (`[[ -e $1 ]]`: the file blocks).
  A new `actoff <flag>` uses the helper for `cloud-jobs/ACTIONS_MISMATCH`, where every rc but 1 blocks, and `[ -f ]` for the other flags.
  `armavail()` (:604), `shavail()` (:696) and `x86shavail()` (:732) call `actoff` in place of `[ -f $M/$f ]`. Each keeps the same flag order and the same printed reason (`cloud-jobs/ACTIONS_MISMATCH`),
  so the `case $why in (...|cloud-jobs/ACTIONS_MISMATCH|...)` at :569/:576 still matches.
- `gha-arm-shard.sh` (:91 source + fallback; :161 `{ mismatch_blocks_gate ...; [ $? != 1 ]; } && no cloud-jobs/ACTIONS_MISMATCH`; header line 16).
- `gha-arm-gate.sh` (:29 source + fallback; :50 the same test; header line 7).
- `arm-postcheck.sh`: :25 source + fallback; :26 `actoff`; `armavail` (:31) and `actok` (:39) call it; header line 9.
- Left as they were, as the spec says: `ACTIONS_SUSPENDED`, `CLOUD_PUSH_HOLD`, and the arm-compare DIFFERENT -> `ARM_SHARD_BLOCKING` guard (gha-arm-shard.sh `stops`, line 534 unchanged).
  `diff <file> <file>.new-amscope` shows only the hunks above (run 06:37Z).

The tm/testmap/select pools still stop on their own mismatch lines. None of them calls the helper, and each still reads the bare file:
- `cloud-overflow.sh:121`: the trust_mutants Actions pool rule (`elif [ -f $J/ACTIONS_MISMATCH ]; then ano+=("actions off ...")`).
- `gha-select.sh:103`: `[ -f $CJ/ACTIONS_MISMATCH ] && ano=...`.
- `testmap-gha.sh:76`: `[ -f $M/cloud-jobs/ACTIONS_MISMATCH ] && ano=...`.
- The writers `verdict-sample.sh:201-202` and `cloud-pull.sh:147-148` also remove `ACTIONS_POOL` on a mismatch.

Test (iv) runs `cloud-overflow.sh pool-ok actions` on a scratch jobs dir and asserts these three bare-file tests by regex.

## 2. Tests: tools-local/test_actions_mismatch_scope.py

Style: scratch, as in test_trainfix_stack.py. Every run builds a scratch M.
- merge-train.sh's and arm-postcheck.sh's functions are cut out of the script text and run with M set to the scratch. The test asserts that the cut text names no live path.
- gha-arm-shard.sh runs from a scratch copy with ARM_SHARD_M, HOME, CLOUD_CONF, VE_EXPORT_*, CLOUD_REMOTE and CLOUD_JOBS_DIR all in the scratch.
- gha-arm-gate.sh runs as a copy whose `M=` line points at the scratch; the test asserts that the substitution happened.
- Both gha scripts run `--dry-run cand-x <sha>` in blocking mode against a one-commit repo. If their Actions gates pass, they stop at `not sent: no first parent`.
- Guard against the old script hitting live dirs (memory note "negative test vs old script"): setUp and tearDown compare the size and mtime of the live
  `gha-arm/gha-arm-shard.log`, `gha-arm/gha-arm.log` and `cloud-jobs/ACTIONS_MISMATCH`. Every test checks them. They held on both runs below.

Gate-leg readers checked per case (7): merge-train `shavail`/`armavail`/`x86shavail`, arm-postcheck `armavail`/`actok`, gha-arm-shard blocking and gha-arm-gate blocking.
Cases: (i) the real 11-17 line (`2026-11-17T17:30Z tm-nightly-20261117T0600Z-p10-9ccbf3fd: verdict sample differs (...)`) leaves all 7 on.
A tm line plus a testmap line with no final newline also leaves all 7 on.
(ii) tm + `armsh-cand-x-...` blocks all 7. (iii) an empty file, an unparseable line, a blank line and an item-named job (`ps-1-4f940bd4`) block all 7.
(iv) a tm-only line still stops the tm pool: `cloud-overflow.sh pool-ok actions` prints `actions off (a result mismatched: cloud-jobs/ACTIONS_MISMATCH)`, and `ok` once the file is gone.
(v) no file: all 7 on. (vi) helper missing: the old rule (a tm line blocks; no file is on). Also: one helper copy, no bare-file test left in the 4 callers.

| run | command | result |
|---|---|---|
| installed scripts (before) | `python3 -I tools-local/test_actions_mismatch_scope.py` | FAILED (failures=3): test_i_tm_line_does_not_block, test_i_tm_and_testmap_lines_no_newline (all 7 readers print `cloud-jobs/ACTIONS_MISMATCH`), test_helper_one_copy; (ii)-(vi) pass. evidence/test-installed.log |
| staged copies (after) | `AMSCOPE_SFX=.new-amscope python3 -I tools-local/test_actions_mismatch_scope.py` | Ran 10 tests, OK. evidence/test-new-amscope.log |

The decision's condition, that the test must fail on the current code, holds: (i) fails on the installed scripts.
After install, the default run (no AMSCOPE_SFX) tests the installed files and must pass.

## 3. Harness compare (zsh -n: all 5 staged files OK)

| harness | baseline (installed) | staged (.new-amscope) | failing sets |
|---|---|---|---|
| ps1014/harness/test-mq.zsh (`PS_NEW=1 PS_NEW_SFX=.new-amscope`) | 70 passed, 0 failed | 70 passed, 0 failed | same (sorted ok/FAIL lines identical) |
| armshard/test-armshard.zsh (`ARMSH_NEW=new-amscope`) | 41 ok, 11 FAIL | 41 ok, 11 FAIL | same 11 (shard-count/room cases: `shards 3: latency n 5`, `n 2 raised to 3/4` ...); they fail on the installed file too, so they are not caused by this change |

Evidence: evidence/harness-{mq,armsh}-{base,new}.txt. Both harnesses run on scratch M without the helper, so the staged scripts take
the old-rule fallback there, which matches the baseline by construction. The new rule is covered by section 2.

## 4. Seeded bugs (shell only; no Lean, Python or Rust product code changed)

Each seed was planted in a staged file, the test was run with AMSCOPE_SFX=.new-amscope, and the file was restored (byte-compared). Evidence: evidence/seeds.txt, seed.py, seed9.py.

| # | file | bug | failing tests |
|---|---|---|---|
| S1 | mismatch-scope.sh.new-amscope | tm/testmap/select lines block | test_i_tm_line_does_not_block, test_i_tm_and_testmap_lines_no_newline |
| S2 | mismatch-scope.sh.new-amscope | gate-leg prefixes accepted | test_ii_armsh_line_blocks |
| S3 | mismatch-scope.sh.new-amscope | empty file accepted | test_iii_empty_blocks |
| S4 | mismatch-scope.sh.new-amscope | unparseable line skipped | test_iii_unparseable_blocks, test_iii_blank_line_and_item_job_block |
| S5 | mismatch-scope.sh.new-amscope | unknown job accepted | test_iii_blank_line_and_item_job_block |
| S6 | merge-train.sh.new-amscope | actoff back to `[ -f ]` | test_i_tm_line_does_not_block, test_i_tm_and_testmap_lines_no_newline |
| S7 | gha-arm-shard.sh.new-amscope | line 161 back to `[ -f ]` | test_i_* (2), test_helper_one_copy |
| S8 | gha-arm-gate.sh.new-amscope | fallback `return 1` (helper missing = no block) | test_vi_no_helper_falls_back_to_the_old_rule, test_helper_one_copy |
| S9 | arm-postcheck.sh.new-amscope | actoff back to `[ -f ]` | test_i_* (2) |

S8 first showed only test_helper_one_copy failing. That exposed a test bug: gha() read both scripts' logs, so gha-arm-shard's line made gha-arm-gate look
blocked. The fix: each script is judged on its own log only. After the fix, S8 also fails test_vi.

## 5. Install (INSTALL WAITS FOR DECIDER READ)

The installed files were hashed at staging (md5): merge-train.sh d1f03692..., gha-arm-shard.sh ab23118b..., arm-postcheck.sh 9efdbde7..., gha-arm-gate.sh 1fe58fde....
If one differs at install time, re-stage it. Note: `merge-train.sh.new-fdre` (11-15) is another staged copy of merge-train.sh; installing it after this item would drop these hunks.

```
cd /home/seyran/code/manage-agents
md5sum merge-train.sh gha-arm-shard.sh arm-postcheck.sh gha-arm-gate.sh   # expect d1f03692 ab23118b 9efdbde7 1fe58fde
mv mismatch-scope.sh.new-amscope mismatch-scope.sh                        # new file: no backup; helper first (the old scripts ignore it)
for f in merge-train.sh gha-arm-shard.sh arm-postcheck.sh gha-arm-gate.sh; do cp -p $f $f.bak-20261120amscope && mv $f.new-amscope $f; done
python3 -I tools-local/test_actions_mismatch_scope.py                     # the installed files: must say OK (10 tests)
```
Rollback: `for f in merge-train.sh gha-arm-shard.sh arm-postcheck.sh gha-arm-gate.sh; do mv $f.bak-20261120amscope $f; done` (mismatch-scope.sh may stay; nothing else sources it).

Restart: none. Each changed script runs as a fresh `zsh` process per use: merge-train.sh per train; gha-arm-shard.sh and gha-arm-gate.sh from merge-train.sh
(`zsh $M/iso.sh ... zsh $M/gha-a...`, :560/:676/:710); arm-postcheck.sh via merge-train.sh's bgjob (:650). No svc-* loop sources any of them.
The `mv` gives a new inode, so a train running now keeps its loaded copy and the next train uses the new one.
presync-lean-regen.zsh sources merge-train.sh in library mode. That mode now also runs the source line and the two function definitions; they are harmless
there, and the names do not collide. On a clean cloud host (~/c2/pslr) the helper is absent, so the fallback is defined and never called.

## Notes for the DRI

- Narrower reading taken (task rule: when unsure, block; overrides rule 2). Only `tm-*`, `testmap-*` and `select-*` lines are let through.
  Item-named trust_mutants Actions jobs (`ps-1-4f940bd4`, `et-4.s1of5-...`, `jt-2c-...`) are of no known kind, so they still block the gate. They are most of the Actions jobs:
  `ap-`, `cmp-`, `sc-` ... from cloud-jobs/*/job.json pool=actions; tm-* is 156 of 1,397 (prefix count, 06:2xZ). Of the 6 archived ACTIONS_MISMATCH files, the 11-14, 11-17 (05:34Z) and 11-17 (17:30Z, the measured
  58 h case) ones are tm-nightly and would no longer block; the 10-29, 10-30 and 11-04 ones (et-4, jt-2c, ps-1) still would (evidence/archived-mismatch-files.txt: the helper on each archived file). The report's measured saving
  comes from the tm-nightly case. To also let item-named trust_mutants jobs through, a reliable marker is needed, for example a line written only by
  verdict-sample.sh/cloud-pull.sh for a job whose cloud-jobs/<job>/job.json has pool=actions and a trust_mutants payload. That would be a separate decision.
- Not changed, outside the listed readers, so they keep the old rule (any file stops them):
  - `mac-watch.sh:28`: the MAC_LAST_RESORT sharded arm run of an uncovered head.
  - `lean-cache-arm.sh:43`: the arm Lean cache warm-up.
  - `nightly-vm-verify.sh`: through gha-arm-shard.sh --x86, which does get the new rule.
  - `cloud-late.py` and `actions-health.py`: pool health.
  If mac-watch should follow the gate legs, it is a one-line call of the same helper.
- The caller fallback `mismatch_blocks_gate(){ [[ -e $1 ]]; }` restates the old rule in each caller. It runs only when the helper cannot be sourced, and it
  keeps the harnesses (which copy only the script into scratch M) identical to the baseline.
- `armshard/test-armshard.zsh` fails 11 cases on the installed gha-arm-shard.sh (shard-count/room expectations). They predate this item; not touched here.
- Light lane / trust_mutants: not applicable (no VE diff).
- delegate-cw.py: 0.51M CW at call 61 (MEASURED).

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed: N.A. (no relayed answer; shell guard only).
2. Deliverables: PASS. Helper (section 1); 6 call sites in 4 files; test (i)-(iv) plus (v)/(vi); .new-amscope staged; zsh -n; harness compare (section 3); report, CURRENT-STATE line, backlog status, msg dri.
3. Tests can fail: PASS. S1-S9 (section 4), and the installed-script run fails (i).
4. Python/Lean/Rust agree: N.A.
5. R8 binding: N.A.
6. Gate evidence matches final HEAD: N.A. for the VE gate (no VE commit; the chain gates the unchanged HEAD). Harness evidence was taken on the final staged files (md5 in section 5 for the originals; staged files restored byte-identical after seeding).
7. No unsigned item: PASS. No DELTA row; nothing reserved for the DRI.
8. DELTA: N.A. (decision item 1: not a trust-base change).
9. Test selection: PASS. The decision asks this test to stay selected; it is a tools-local unittest file next to test_trainfix_stack.py.
10. Lean statements: N.A.
11. Budgets fail closed: PASS. Every unsure input blocks (test_iii_*, test_vi): helper rc 127 or any rc but 1 blocks, and an unreadable or non-regular path blocks.
12. CPU/memory: PASS. One read of a small file per availability check; 10 tests in about 1.2 s.
13. Removed tests: N.A. (none removed).
14. Both directions and cited evidence: PASS. Accept cases (i), (v) and refuse cases (ii), (iii), (vi); every claim cites a file under evidence/ or a command above.
15. No overclaim / no silent cut / every check can fail / limits: PASS. No deliverable was cut. The narrower reading is recorded under Notes, with its cost.
