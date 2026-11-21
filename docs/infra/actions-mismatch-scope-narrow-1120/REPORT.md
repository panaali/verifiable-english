# actions-mismatch-scope-narrow-1120: build report

INSTALL WAITS FOR DECIDER READ. Staged only; nothing live was changed. Reviewer read (Opus xhigh): **OK**, on condition that `mismatch-scope.sh` is installed before, or in the same step as, the four call sites.

Task: prompts/task-actions-mismatch-scope-narrow-1120.txt. Background: reviews/advisor/20261120T0757Z.md ADV-1 and reviews/dri-decisions-20261120-adv0757.md item 1.
Saved evidence is committed on VE branch infra/actions-mismatch-scope-narrow-1120 under docs/infra/actions-mismatch-scope-narrow-1120/ (abbreviated `E/` below).

## What changed (staged as `<file>.new-amscope2`)

1. **mismatch-scope.sh.new-amscope2** (the one copy of the rule). A file leaves the gate's Actions legs on (rc 1) only when:
   - it exists, is a readable regular file and is not empty, and
   - EVERY line has the form `<YYYY-MM-DDTHH:MMZ> <job>: verdict sample differs (<path with no ')'>/verdict-compare.txt)`, with `<job>` matching `tm-<alnum>…` or `testmap-<alnum>…` and made only of `[A-Za-z0-9._-]`.

   Everything else blocks (rc 0):
   - every select-* line, whatever its reason;
   - every cloud-pull.sh line (`cloud-tm-verify <job>: MISMATCH: …`, covering provenance, digest, head/base, tree, options and rescore), whatever its job;
   - cloud-late.py's late-compare lines;
   - gate-leg jobs and jobs of unknown kind;
   - blank or unparseable lines, and CR line endings;
   - an empty file, an unreadable file, or a path that is not a regular file.

   An absent file gives rc 1, as before. Diff against the 06:42Z rule: E/mismatch-scope.sh.vs-amscope.diff.
   - **Conservative choice, recorded here:** the task says the reason "starts with" `verdict sample differs`. The staged rule is narrower. It also pins the rest of the verdict-sample.sh:201 text: one parenthesised path ending in `/verdict-compare.txt)`, and nothing after it. So `verdict sample differs (x) MISMATCH …` blocks too. The task's "only when" wording allows this, and "when unsure, block" asks for it.
   - `setopt extendedglob` is set after `emulate -L zsh`, so it is local to the function. The reviewer checked that it does not leak into the caller.
2. **Call sites** merge-train.sh, gha-arm-shard.sh, arm-postcheck.sh and gha-arm-gate.sh `.new-amscope2`:
   - Each live file is byte-identical to its .bak-20261120amscope (`cmp`, E/syntax.txt), so no other install landed since the rollback.
   - Each copy is the 06:42Z `.new-amscope` change applied to that live file. The copies differ from `.new-amscope` only in comments, which now describe the narrowed rule (E/<file>.vs-amscope.diff; arm-postcheck.sh is byte-identical to its `.new-amscope`).
   - Behaviour: every rc but 1 blocks. If the helper cannot be sourced, the old rule applies (the file exists = blocks).
   - The tm, testmap and select pools still read the bare file (test_iv).
3. **tools-local/test_actions_mismatch_scope.py.new-amscope2**: 20 tests.
   - Cases (i)-(iv) are kept. The old (v) absent and (vi) no-helper cases are renamed (ix) and (x); no selection list names the old method names (grep in the reviewer section).
   - New Scope cases, run on every gate leg in a scratch M:
     - (v) a tm-* line carrying cloud-pull.sh's provenance text `cloud-tm-verify <job>: MISMATCH: the result commit's parent is not the exported head`;
     - (vi) a testmap-* `N file digests differ from the VM commit` line;
     - (vii) `select-…: verdict sample differs (…/verdict-compare.txt)`;
     - (viii) TM_LINE + PROV_LINE, and PROV_LINE + TESTMAP_LINE.
   - New Direct cases, run on the helper alone:
     - all 11 cloud-tm-verify.py `fail(1, …)` reasons × 5 job kinds, alone and after an allowed line;
     - every select-* variant;
     - the cloud-late.py reason;
     - 21 near-misses: CR, `from x`, case, a leading space, text after the path, a `)` inside, bad jobs, a missing stamp, a double space, a trailing blank line, an empty file, a lone newline, and job-charset violations;
     - a directory, a broken symlink, a mode-000 file holding an allowed line, and an absent file.
   - `test_writers_text` pins the allowed text to verdict-sample.sh:201. It also pins cloud-pull.sh's ACTIONS_MISMATCH write and cloud-tm-verify's print and all 11 `fail(1, …)` reasons to their sources, so a reworded writer fails this test instead of being silently allowed or blocked.

## Required pass/fail pattern (command: `AMSCOPE_SFX=<sfx> python3 -I tools-local/test_actions_mismatch_scope.py.new-amscope2 -v`)

- `.new-amscope2`: Ran 20, OK (E/test-new-amscope2.log).
- Live (rolled-back) scripts, SFX empty: 6 FAIL, including (i) `test_i_tm_line_does_not_block` and `test_i_tm_and_testmap_lines_no_newline`. The others are `test_helper_one_copy` and the 3 Direct cases; those fail because the live mismatch-scope.sh is still the broad 06:42Z helper (E/test-live.summary.txt).
- `.new-amscope` (06:42Z copies): 7 FAIL, namely (v), (vi), (vii), (viii) and the 3 Direct cases (E/test-new-amscope.summary.txt).
- No test reads or writes the live cloud-jobs/. Each test's tearDown compares live state before and after.
  - One run (seed S1, first attempt) tripped that guard: a real train shard (`armsh-cand-actions-mismatch-scope-1120`) appended to the live gha-arm/gha-arm-shard.log during the run.
  - `grep -c 'cand-x ' gha-arm/gha-arm-shard.log` = 0, so none of those lines came from this test.
  - S1 was rerun clean (E/seeds-runs.txt, second S1 block).

## Harness and syntax

- `zsh -n` passes on all 5 staged shell files (E/syntax.txt).
- test-harness/ps1014/harness/test-mq.zsh, each run alone, one after the other:
  - live baseline: `== merge queue: 70 passed, 0 failed`;
  - `PS_NEW=1 PS_NEW_SFX=.new-amscope2`: `70 passed, 0 failed`.
  - The failing sets are identical (both empty). `diff` of the ok/FAIL lines is empty (E/harness-mq-live.txt, E/harness-mq-new-amscope2.txt).
  - Note: lib.zsh does not copy mismatch-scope.sh into the harness M, so the harness exercises merge-train.sh's fallback path. The rule itself is covered by the test file.

## Seeded bugs (shell product files, zsh; each planted in the staged file, the test run, then the file restored and checked with `cmp`) — E/seeds-runs.txt, planters E/seed-plant*.py.txt

| # | File | Bug | Failing tests |
|---|---|---|---|
| S1 | mismatch-scope.sh.new-amscope2 | the reason check is skipped (`true \|\| [[ $why == … ]]`) | (v), (vi), (viii), Direct v_vi_vii, near-misses |
| S2 | mismatch-scope.sh.new-amscope2 | select-* is allowed (`(tm\|testmap\|select)-`) | (vii) Scope, Direct vii |
| S3 | mismatch-scope.sh.new-amscope2 | prefix-only (`'verdict sample differs '*`: the task's literal wording) | Direct near-misses |
| S4 | mismatch-scope.sh.new-amscope2 | an empty file is on (`(( n >= 0 ))`) | test_iii_empty_blocks, near-misses |
| S5 | gha-arm-gate.sh.new-amscope2 | the call site goes back to `[ -f … ]` | (i) ×2, test_helper_one_copy |
| S6 | mismatch-scope.sh.new-amscope2 | an unreadable or non-regular file is on (`\|\| return 1`) | test_iii_unreadable_or_not_a_regular_file_blocks |
| S7 | mismatch-scope.sh.new-amscope2 | the job charset check is removed | Direct near-misses |

S6 and S7 are the two gaps the reviewer found (its plants passed all 19 tests then). I added tests for both after the read, changing tests only. With those tests in place, both seeds fail (20-test runs).

Python and Lean: no product code changed in either; the test file is test code. Rust: not touched. trust_mutants: not applicable, because no VE product code changed (light lane).

## Reviewer read (step 5): Opus 5.5 xhigh, read-only seat

- How it ran: `iso.sh rv-amscope2-readrv 8G -- run-codex.sh /tmp/amscope2-review/M … xhigh` (prefer-Opus path; RUN line: `model=opus … effort=xhigh`). It worked on a scratch copy of every file.
- Final: manage-agents/actions-mismatch-scope-narrow-1120-readrv.final.md (copy: E/reviewer-read.final.md).
- **Verdict: OK**, "safe to install as staged, provided `mismatch-scope.sh` is installed before the four call sites". All 4 claims hold. The reviewer probed C and UTF-8 locales, BOM, NUL, tab, FIFO, directory, broken symlink, unreadable file and multi-line `$out`. No cloud-pull.sh write can pass, because each write's first line starts `cloud-tm-verify <job>: MISMATCH:`, holds a traceback, or is empty.
- Its non-blocking notes, and what I did with each:
  - (a) Two cases were unpinned: unreadable/non-regular files and the job charset check. **Fixed** with tests plus S6 and S7.
  - (b) The test file lost its shebang. **Fixed.**
  - (c) Test methods were renamed. Grep finds the old names only in the old item's report; there is no selection list to update.
  - (d) A NUL inside the path of an otherwise exact line passes. No writer emits NUL; left as is (Notes).
- The re-read was done before those test-only additions; the helper and call sites are byte-identical to what it read (md5 in E/md5.txt).

## Install commands (for the decider; NOT run). Order matters: the helper goes first.

```
cd /home/seyran/code/manage-agents
for f in merge-train.sh gha-arm-shard.sh arm-postcheck.sh gha-arm-gate.sh; do cmp $f $f.bak-20261120amscope || echo "LIVE CHANGED: $f (re-port first)"; done
cmp mismatch-scope.sh mismatch-scope.sh.new-amscope || echo "LIVE CHANGED: mismatch-scope.sh"
for f in mismatch-scope.sh merge-train.sh gha-arm-shard.sh arm-postcheck.sh gha-arm-gate.sh tools-local/test_actions_mismatch_scope.py; do cp -p $f $f.bak-20261120amscope2; done
mv mismatch-scope.sh.new-amscope2 mismatch-scope.sh            # helper FIRST (else a train started in the gap keeps the broad rule)
for f in merge-train.sh gha-arm-shard.sh arm-postcheck.sh gha-arm-gate.sh; do mv $f.new-amscope2 $f; done
mv tools-local/test_actions_mismatch_scope.py.new-amscope2 tools-local/test_actions_mismatch_scope.py
for f in mismatch-scope.sh merge-train.sh gha-arm-shard.sh arm-postcheck.sh gha-arm-gate.sh; do zsh -n $f && echo "$f ok"; done
python3 -I tools-local/test_actions_mismatch_scope.py      # expect Ran 20, OK
```
File modes of the staged copies match the live ones (664; arm-postcheck.sh and gha-arm-gate.sh 775).
Rollback: `for f in mismatch-scope.sh merge-train.sh gha-arm-shard.sh arm-postcheck.sh gha-arm-gate.sh tools-local/test_actions_mismatch_scope.py; do mv $f.bak-20261120amscope2 $f; done`.
Running trains keep the copy they started with, so no restart is needed.

SIZE: 33 product (new helper; call sites +24/-10 lines, mostly the 06:42Z change re-applied), 142 tests (+142/-11), ~0 other hand-written lines (evidence files are copies and logs).

## Notes for the DRI

- The narrowed rule also blocks cloud-late.py's late-compare lines (`<job>: the VM/Mac run of the same tree (…)`). These are verdict differences on tm jobs, but the task allows only the "verdict sample differs" text, so they block (the conservative reading). A later item could add them if wanted.
- A NUL byte inside an otherwise exact verdict-sample line passes (reviewer note d). No writer emits one; zsh `read` truncation semantics. Left as is.
- test-armshard.zsh was not rerun. gha-arm-shard.sh.new-amscope2 differs from the 06:42Z `.new-amscope` only in comments, and the 06:42Z build recorded identical installed and staged results for it (41 ok / 11 FAIL on both).
- CW: `python3 -I tools-local/delegate-cw.py` printed "own session not found (needs VE_STEP and CLAUDE_CONFIG_DIR from dri-delegate.sh…)", so no measured number is available. This session is well under the cap by its size.
- No DELTA row (task: not a trust-base change).

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed/contained: N.A. (no Lean or relay change).
2. Deliverables built, no rule broken: PASS. Steps 1-5 done; install not done, by instruction.
3. Tests can fail: PASS. Seeds S1-S7 (table above); live fails (i); `.new-amscope` fails (v)-(viii).
4. Python/Lean/Rust agree: N.A.
5. R8 binding: N.A.
6. Gate evidence matches final HEAD: PASS. The chain gates the final HEAD; the evidence commit is docs-only.
7. No unsigned item: PASS. There is no DELTA row and nothing is reserved for the DRI.
8. DELTA: N.A. Not user-visible VE behaviour; the task says no DELTA row.
9. Test selection: PASS. Cases (v)-(viii) are in the test file the decision names (condition: "cases (v)-(viii) stay selected"); the file runs as one unit.
10. Lean statements: N.A.
11. Fails closed: PASS. Every rc but 1 blocks; a missing helper falls back to the old rule (test_x_no_helper_falls_back_to_the_old_rule); unreadable or non-regular files block (test_iii_unreadable_or_not_a_regular_file_blocks).
12. CPU/memory: PASS. One read loop over a few lines per call; test-mq harness 70/70, the same as live.
13. Test-removed trailer: N.A. The VE repo has no tests removed or renamed; the two renamed methods are in manage-agents tools-local, which gate_collection does not collect.
14. Both directions, cited evidence, spec re-read: PASS.
    - Both directions: allow (test_i_*, Direct test_i_allowed) and block ((ii)-(viii), Direct).
    - Every claim cites E/ files.
    - Spec re-read: "tm-* or testmap-* AND reason starts with 'verdict sample differs'" against prompts/task-actions-mismatch-scope-narrow-1120.txt:6 and verdict-sample.sh:201. "every select-* line … provenance/digest/head/base/options" against task:6 and cloud-tm-verify.py:48-118.
15. Overclaim, silent cut, new checks can fail, limits: PASS. Universal words in this report are backed: "every fail(1) reason" by test_writers_text, which counts 11 against the source; "all legs" by Scope.legs; the rest by the files cited. No cut was made. Every new check has a seed. Limits: N.A.
