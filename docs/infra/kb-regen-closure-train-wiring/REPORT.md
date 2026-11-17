# kb-regen-closure-train-wiring: the merge train runs the kernel-closure check after a merge and rewrites a stale baseline

Status: BUILT and STAGED. INSTALL WAITS FOR DECIDER READ. No DRI signature needed: no DELTA row, no Lean change, no trust-base change.
Decision: reviews/dri-decisions-20261116-kb-regen-closure-check.md item 1, follow-up F1. Row note (spec) quoted in the task.
VE side: evidence only, under this directory. No VE source file changed (`git diff --stat main...HEAD` lists only `docs/infra/kb-regen-closure-train-wiring/`).
Staged (manage-agents, live files untouched; md5 in `md5.txt`):
- `merge-train.sh.new-kbw` (07b354eb…; live merge-train.sh 4968a062…). Diff: `merge-train.sh.new-kbw.diff`.
- `test-harness/ps1014/harness/test-mq.zsh.new-kbw` (6fea801b…; live a009cf23…). Diff: `test-mq.zsh.new-kbw.diff`.

SIZE: 52 product (merge-train.sh +52/-1), 119 tests (test-mq.zsh +119), 0 other hand-written lines (plus this REPORT).

## The change

`branchregen` (the train's per-round regeneration on the item's worktree, after `syncbranch` merged main) is now two steps:
1. `branchinv`: the existing L87 Lean inventory regeneration, renamed and otherwise unchanged (lake build when the probe reads stale modules).
2. `brclosure` (new), which runs after step 1 and its Lean build:
   - Runs only when all of these hold: train mode (the `brclose` variable is set after the library-mode `return`); step 1
     did not report a compile failure (`brbuild` empty); `$M/KERNEL_CLOSURE_REGEN.off` is absent; the tree's
     `tools/regen_generated.py` names `"kernel-closure"`. It runs once per branch head (the `brcseen` map).
   - Runs `regen_generated.py --check --only kernel-closure`. That is the entry's whole check: `kernel_closure.py --check`
     and `--fresh`, one measurement. If it passes: a "kernel closure fresh" line in `merge-train.log.candregen`, nothing else.
   - It rewrites only when the output has a `STALE: ` line and no `FAIL: ` line. A limit failure (kernel grew) is never
     rewritten here: a write under a higher signed total would raise the baseline. Rewriting means
     `--write --only kernel-closure`, the check again (it must pass), and every changed path's `--owner` must be
     `kernel-closure`. The result is one commit on the branch, "Regenerate the kernel closure baseline after the merge of
     main (merge train, R12)", whose body quotes the STALE line. Plus one `kernel closure regen of <label>: h -> n refreshed …` line in merge-train.log.
   - Anything else (uncommitted changes, a failure with no STALE line, STALE plus FAIL, a writer failure or timeout, still
     failing after the write, another entry's file changed, a commit failure): the branch is reset to its head. Untracked
     files the attempt created are removed; files that were there before are kept. A `kernel closure regen of <label>
     skipped (<why>): the branch is gated as is` line is written. The gate's Kernel check then refuses the stale baseline, as today.
   - Timeout: `KERNEL_CLOSURE_TIMEOUT`, else `CAND_REGEN_LEAN_TIMEOUT`, default 2700 s, per regen_generated call.
- Library mode (presync-lean-regen.zsh sources the train and calls `branchregen`) never runs `brclosure`.
  presync-watch-job.sh:150-151 refuses a presync result that changes a file outside the four inventory owners. A
  closure commit there would throw the whole presync regen away. The train runs the step after the presync fast-forward instead.
- The speculative regen (`specregen`, MQ_SPEC_REGEN / MQ_STACK_SPEC) calls `branchregen` on its detached merge. So S is
  closure-checked too, and a closure commit made there is part of S.

## Tests (stub harness, test-mq.zsh section K; `zsh test-mq.zsh kc` runs only these)

The stub tree has a regen entry `kernel-closure`: `docs/kernel/closure-baseline.json` measured from `lean/*.lean`, one row
per file with its line count, `kernel_lines` the sum. The output wording is the real tool's (`STALE: <file> is not what
--out writes now (path rows …)`, `FAIL: the kernel grew …`). The baseline has a "keeps ours" merge driver. The branch adds
lean/B.lean and its baseline. Main then moves a line from P to Q. The train's sync merge keeps the branch's baseline:
total 6, equal to the fresh total 6, with rows P.lean and Q.lean stale. This is the row note's case.

| case | asserts | staged | installed |
|---|---|---|---|
| K1 | premise (equal totals, stale rows); one regen commit on the sync merge changing only the baseline; main = the one gated candidate, baseline fresh; log line names the rows; calls exactly check, write, check (not again on the new head) | 4 ok | premise ok, 3 FAIL |
| K2 | fresh tree: one check, fresh line, branch head published unchanged | ok | FAIL |
| K3 | STALE + FAIL: no write, head unchanged | ok | FAIL |
| K4 | failure without STALE (broken build): no write, failure quoted | ok | FAIL |
| K5 | write changes docs/notes.txt (owner extra): refused, reset, tracked tree clean | ok | FAIL |
| K6 | still STALE after the write: refused, reset | ok | FAIL |
| K7 | writer fails leaving out.tmp: out.tmp removed, the builder's mine.txt kept | ok | FAIL |
| K8 | KERNEL_CLOSURE_REGEN.off: no check, stale published (old behaviour) | ok | ok |
| K9 | library mode (presync-lean-regen.zsh run): no check on a stale tree, PSLR fresh | ok | ok |
| K10 | check killed at KERNEL_CLOSURE_TIMEOUT=1: no write, timeout named | ok | FAIL |

- `run-staged.log`: `PS_NEW=1 PS_NEW_SFX=.new-kbw zsh test-mq.zsh.new-kbw kc` gives 13 passed, 0 failed.
- `run-live.log`: the same cases on the installed merge-train.sh give 3 passed, 10 failed. The row note's test fails on
  the old train: K1 "published: … its baseline fresh" FAILs.
- Regressions, all on the staged train:
  - `run-staged-full.log`: the whole test-mq.zsh.new-kbw (Q, C, H and K cases), 70 passed, 0 failed.
  - `run-mqstack-staged.log`: test-mqstack.zsh (branchregen, specregen, stacked S), 68 passed, 0 failed.
  - `run-presync-staged.log`: test-presync-lean-regen.zsh with `PW_SFX=.new-kbw` (library mode, psrnote, presync-watch-job), 31 passed, 0 failed.
- Selected VE tests (`mac-pytest.sh --select`): GitHub Actions run kb-regen-closure-train-wiring-9e527aff-t934676,
  2 shards (6 + 4 units), all passed, exit 0. Docs-only diff.
- No lake build or audit run: no Lean or VE source changed.
- Light lane: `light-lane.py check` printed `NOT 679 changed lines outside generated files > 150 (17 files)`. All of them
  are evidence under this directory, and no trusted-core or VE source file changed. No trust_mutants sweep: there is no VE product mutant to sweep.

## Seeded bugs (`mutants.json`; each run `PS_NEW_SFX=.mut-kbw zsh test-mq.zsh.new-kbw kc`, then the mutant file removed)

All are in `/home/seyran/code/manage-agents/merge-train.sh.new-kbw` (zsh, the only product language changed). Each diff is in `mut-S<n>.diff` and each log in `mut-S<n>.log`.
- S1: FAIL-line guard disabled → K3 "skipped (a limit), no write…" FAILs.
- S2: owner check disabled → K5 "skipped (owner extra)…" FAILs.
- S3: `brclose` guard removed (library mode runs the step) → K9 "the tree is stale, yet no check ran…" FAILs.
- S4: cleanup of untracked files after a refused write removed → K7 "skipped (writer failed), out.tmp removed…" FAILs.
- The installed train (no step at all) is the fifth: `run-live.log`, K1 FAILs.

## Spec re-read

- "merge-train.sh per-merge regen … runs only --check --at-merge entries; kernel-closure needs a Lean run so it is
  skipped, and branchregen skips it too": confirmed against live merge-train.sh:284-289 (cregen_entries `--at-merge`) and
  :354-388 (branchregen `le=(lean-statements lean-audit-manifests assurance-doc)`), and against
  tools/regen_generated.py:188-198 (kernel-closure has no `at_merge`).
- "After a merge of main, run regen_generated.py --check --only kernel-closure (after the Lean build)": `brclosure` runs
  in `branchregen` after `branchinv`. `branchregen` follows `syncbranch` (merge of main) in qloop (merge-train.sh.new-kbw,
  `branchregen  # L87: before the queue lock`) and in the non-queue loop. Merges of main into the branch, by the builder or by the train, give a new head, which is checked once.
- "on STALE rewrite with --write --only kernel-closure and commit": the STALE line comes from kernel_closure.py
  check_fresh (tools/kernel_closure.py:307). The step writes, rechecks and commits (K1).
- "Test must fail on the old train: a merged tree with a per-path stale baseline, same totals": K1 premise check (totals
  6 = 6, rows P and Q) passes on both trains. K1's outcome checks FAIL on the installed train (`run-live.log`).
- "stage as .new-<tag>, harness test-mq.zsh (PS_NEW=1)": tag `kbw`, both files staged, live files untouched (md5.txt).

## Install (waits for the decider's read)

```
cd /home/seyran/code/manage-agents
cp -p merge-train.sh merge-train.sh.bak-20261117-kbw && mv merge-train.sh.new-kbw merge-train.sh
cp -p test-harness/ps1014/harness/test-mq.zsh test-harness/ps1014/harness/test-mq.zsh.bak-20261117-kbw \
  && mv test-harness/ps1014/harness/test-mq.zsh.new-kbw test-harness/ps1014/harness/test-mq.zsh
```
No restart: each train launch reads merge-train.sh, and running trains keep the old file's inode. The step is on by
default. Rollback without a reinstall: `touch $M/KERNEL_CLOSURE_REGEN.off`. Message sent:
inbox/dri/20261117T165748Z-kb-regen-closure-train-wiring-3348694.md.
Before installing, check the md5 of the live merge-train.sh (4968a062…). If another staged copy was installed first,
this diff must be re-applied on top of it. `merge-train.sh.new-fdre` is older than the live file (172128 bytes, the same
size as bak-20261116-lwas) and looks stale; it is not part of this item.

## Notes for the DRI

- Cost: every new branch head in the train now pays one kernel_closure measurement: a `lake build` of its imports
  (warm in the item's worktree) plus one `lake env lean` run, "minutes on a loaded host" per tools/kernel_closure.py:64.
  This was not measured here (stubs only). It runs before the queue lock, beside other items' gates. A head that changed
  no Lean and no kernel registry is checked too: a path filter would be a second, hand-kept list of the measure's inputs.
- Not covered (conservative: the gate refuses): a plain stacked candidate (MERGE_QUEUE without MQ_STACK_SPEC) is a
  merge-tree of an unpublished candidate and the branch under the queue lock, where no Lean step runs (L87 rule: no write
  under the queue lock). If that merge leaves the baseline stale, its gate's Kernel check fails and the item is rebuilt
  or verify-fixed as today. With MQ_STACK_SPEC (on in production), S goes through `branchregen` and is covered.
- A check that is killed or fails without STALE is not retried on the same head (once per head). The gate still decides.
- After install, the sentence in tools/kernel_closure.py:56-57 ("The merge train's per-merge regeneration (R12) does not
  run this entry (…; follow-up kb-regen-closure-train-wiring)") is out of date. That is a wording change for a VE item, not made here before install.
- delegate-cw (MEASURED): `python3 -I tools-local/delegate-cw.py` printed "delegate-cw: own session not found (needs
  VE_STEP and CLAUDE_CONFIG_DIR from dri-delegate.sh, or a transcript path)" both times it ran, so there is no figure.
- Pre-existing failures: none met. No test of main-known-red.txt was selected or touched.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no Lean answer or relay touched.
2. Deliverables built, no rule broken: PASS. The train step (K1) and the test that fails on the old train (`run-live.log` K1) are built. The step is staged as .new-kbw with live files untouched (md5.txt), and the install read was messaged.
3. Tests and gates can fail: PASS, `mutants.json` S1–S4 (each FAILs one K check) and `run-live.log` (10 FAIL on the installed train).
4. Py/Lean/Rust agree: N.A., no checker code changed.
5. R8 binding: N.A., no Lean answer fields read.
6. Gate evidence matches final HEAD: PASS. The full gate is run by the chain on the final HEAD. Evidence is saved files (md5.txt with its timestamp, run logs), not live diffs.
7. No unsigned item: PASS, no DELTA row or trust growth (the task says none).
8. Every user-visible change in DELTA: N.A., no VE user-visible change (train script only).
9. Test selection finds tests: PASS. The selected run (GitHub Actions t934676) ran 10 units for the docs-only diff. The staged script is covered by test-mq.zsh section K, not by VE selection.
10. Lean statements: N.A., no Lean.
11. Budgets fail closed: PASS. A timeout or killed check is never a pass and never a write: K10. The stub's sleep sits under a 1 s train timeout in a manage-agents harness, not the VE suite.
12. No CPU/memory regression: PASS with a named cost. One measurement per new head, not per round (K1 calls exactly "check;write;check;"). The cost is in Notes, unmeasured.
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions, cited evidence: PASS. Rewrite side: K1. Keep side: K2 (fresh), K3 (limit), K4 (no STALE), K5 (owner), K6 (still stale), K7 (writer failed), K8 (off), K9 (library mode), K10 (timeout). Each claim names a log in this directory.
15. Four classes: overclaim PASS (claims scoped to stub runs; the Lean cost marked unmeasured). No silent cut PASS (the one uncovered path, plain stacked candidates, is outside "after a merge of main" and named in Notes). New checks can fail PASS (S1–S4). Limits charged before work N.A. (no input limits).
