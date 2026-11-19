# tmpar-lock-align: REPORT

- **Status:** built and staged. INSTALL WAITS FOR DECIDER READ. No live file was changed. No DELTA row (no Lean, VE-package,
  Rust or trust-base change). No DRI signature needed.
- **Row:** tmpar-lock-align (infra; tm-remote-parallel.sh). Decision: reviews/tm-shard-fallback-overwrite-20261113.md, section 2.
  Spec: the row note written by dri-decider on 2026-11-17 (R21 no-task-file catch-up).
- **SIZE:** 19 product (16 added lines, 3 changed, in the staged script), 209 tests (one new test file), about 130 other
  hand-written lines (this REPORT and seeded-bugs.json).

## MEASURED first: 'disagree on inputs' in the refused-merge copies (`measure.txt`)

- **TMPAR_REFUSED_KEEP copies (`cloud-jobs/tmpar-refused/`):** 0. The directory does not exist. No tmpar merge has been refused
  since keeprefused was added on 2026-11-10 (`ls -d cloud-jobs/tmpar-refused`: no such file).
- **Other records also give 0 'disagree on inputs':**
  - cloud-overflow.log: 79 `slot=tmpar` lines. 2 of them are REFUSED, and both give "its where are not what its rows give"
    (ci-3 and norm-defaults-cfr-1b on 11-10, fixed by tmpar-merge-where).
  - tmpar.jsonl: 6 split runs, 3 merged and 2 merge refused (the same two).
- **No tmpar part has ever finished on the Mac** (`measure.txt`, the part hosts of each run). Every part was on ve-cloud-2 or
  ve-cloud-3. qt-a4b's 3 "fallback" rounds gave no part record.
- **TM_REMOTE_PARALLEL has been off since 2026-11-11T06:05Z.** It is `TM_REMOTE_PARALLEL.off-20261111T0605Z`: the guard tripped
  on part-hours over 1.5x (tmpar-guard.log).
- **So this fix is preventive.** The refusal has not happened in this path yet. It is the same refusal tm-shard.sh merge met 4
  times (pc-1g, at-1c, qt-a4b, et-4b). Here it would hit the first time a Mac part (the Mac slot, or the part fallback order to
  the Mac) is merged with remote parts.

## The change (`tm-remote-parallel.sh.diff`; staged as `$M/tm-remote-parallel.sh.new-tmparw`)

After tm-unstamp.py, the parts go through `tools-local/tm-lock-align.py $T/norm $w $head <parts>`. This is the same call as
tm-shard.sh merge (`tm-shard.sh:267`), with REPO = the worktree and HEAD = its HEAD read at the start. The parts are run at that
HEAD in that worktree, so its objects hold every blob the helper reads.

- **Output check:** a printed path is used only when each of the N lines is the part itself or `$T/norm/part-K.norm.json`.
- **Otherwise:** a helper failure, a wrong count or any other path means the parts go to the merge as they are, and the merge
  refuses as before. A line "tm-lock-align gave ... the parts as they are" goes to lockalign.err. This is the same rule as
  tm-unstamp's.
- **stderr:** lockalign.err is printed, with the helper's one reason line per copy.
- **A refused merge** also keeps lockalign.err in `cloud-jobs/tmpar-refused/<parent>/`.
- **The merged line** in cloud-overflow.log ends with "lean/checkers.lock digest aligned (tm-lock-align): part-K.norm.json, ...".
- **Header:** a 2026-11-19 paragraph, and the new test hook TMPAR_LOCK_ALIGN.
- **The helper itself is unchanged.** It is the installed tools-local/tm-lock-align.py (md5 in `md5.txt`), with all its refusal
  rules: any other input difference, an untracked file, a Lake-read file naming checkers.lock, no part with the committed lock,
  and a head that is not HEAD.

Spec re-read: "add the helper after tm-unstamp the way tm-shard.sh does" against the row note and `tm-shard.sh:259-270`.
- Order: unstamp, then align. Matches.
- Output dir: a subdirectory `norm/`, as tm-shard uses. Matches.
- Path check `(part | OUTDIR/part-<position>.norm.json)`: in tmpar the position K is shard K/N, which is the K the helper names.
  Matches.
- One intended difference: REPO/HEAD are the worktree and its HEAD, not `$SRC`/`vm_head`. tmpar has no vm_head; its parts are
  run from `$w` at `$head`.

## Tests (`tools-local/test_tmpar_lock_align.py`, staged as `.new-tmparw`; `test_tmpar_lock_align.py.new-file.diff`)

The test replays et-4b-a97072e6 through tm-remote-parallel.sh itself:
- The real records: `cloud-jobs/et-4b-a97072e6/part-1..5.json`, plus `scratch/et4b-p6/part-6r.json`.
- The real tm-unstamp.py and tm-lock-align.py.
- The real trust_mutants.py `--merge` at a97072e60 (git archive).
- The worktree is a `--shared` clone of the VE repo with HEAD at a97072e60.
- Hosts: one fake host with 6 free tm slots. A fake cloud2-run.sh returns parts 1, 3, 4 and 5 with its "where" stamp. Parts 2
  and 6, which have the Mac's lock digest, get no result there and take the real part fallback order: a fake mac-pytest.sh runs
  them "on ve-mac-1".

| case | staged (`test-on-staged.log`) | installed (`test-on-installed.log`) |
|---|---|---|
| (a) BEFORE = installed: refused "the parts disagree on inputs", exit 86, 1 guard count, nothing at --json | PASS | PASS |
| (b) merged, exit = the merge's, no guard count | PASS | FAIL |
| (b) where = tmpar:fallback:ve-mac-1,ve-cloud-2 | PASS | FAIL |
| (b) --json = the DRI's hand merge scratch/et4b-p6/merged.json (counts, every status, inputs; 326 KILLED, 5 SURVIVOR, 0 NOT RUN) | PASS | FAIL |
| (b) the merged line names part-2.norm.json, part-6.norm.json; the reason on stderr | PASS | FAIL |
| (c) Mac part 2 also differs in a .lean digest: still refused, counted, nothing at --json | PASS | PASS |
| (c) the kept inputs are the parts as they are (part 2's tampered digest) + lockalign.err | PASS | FAIL |
| (d) helper fails: the parts as they are, refused | PASS | FAIL |
| (d) helper prints other paths: the parts as they are, refused | PASS | FAIL |
| totals (plus 2 setup checks) | **11/11, rc 0** | **4/11, rc 1** |

- **Command:** `TMPAR_SH=$M/tm-remote-parallel.sh.new-tmparw python3 -I <copy of the test>`, then the same without TMPAR_SH.
- **The opposite direction is tested:** accept in (b); refuse in (c) and in both (d) cases. (c) passes on installed because it
  only checks the refusal, which happens either way.
- **Regression: `tools-local/test_tm_remote_parallel.py` passes the same 58 checks on both scripts** ("all passed (0 failures)").
  Commands: `TMPAR_SH=<staged> python3 -I tools-local/test_tm_remote_parallel.py` and the same without TMPAR_SH. Logs:
  `suite-tm-remote-parallel-staged.log` and `-installed.log`, with identical output.
- **VE selected run:** `run-selected.log` (mac-pytest.sh --select on this branch; only docs/ changed).

## Seeded bugs (`seeded-bugs.json`; logs `seed-*.log`)

All in the staged script `/home/seyran/code/manage-agents/tm-remote-parallel.sh.new-tmparw` (shell; no Lean, Python-package or
Rust product code changed). Each was a one-line sed into /tmp, and the copies were deleted afterwards. 4/4 caught:

| seed | behaviour | result | failing checks |
|---|---|---|---|
| m1 `mp=($mp)` for `mp=($la)` | the merge reads the aligned copies | 7/11 | the 4 (b) checks |
| m2 `lok=1` | a bad helper answer is not used | 9/11 | both (d) checks |
| m3 lockalign.err dropped from the kept files | a refused merge keeps lockalign.err | 10/11 | (c) kept inputs |
| m4 the aligned-copies note dropped | the merged line names the copies | 10/11 | (b) merged line |

## INSTALL (waits for the decider's read)

```
cd /home/seyran/code/manage-agents
cp -p tm-remote-parallel.sh tm-remote-parallel.sh.bak-20261119tmparw
mv tm-remote-parallel.sh.new-tmparw tm-remote-parallel.sh
mv tools-local/test_tmpar_lock_align.py.new-tmparw tools-local/test_tmpar_lock_align.py
python3 -I tools-local/test_tmpar_lock_align.py   # 11/11 expected; BEFORE = the .bak above
```

- **No restart:** no svc-* loop runs tm-remote-parallel.sh. mac-pytest.sh starts it per sweep, so the next sweep reads the new
  file.
- **The flag is off** (`TM_REMOTE_PARALLEL.off-20261111T0605Z`), so the change has no effect until someone turns it back on.

## Notes for the DRI
- The test reads the live et-4b records in cloud-jobs/ and scratch/, as test_tm_shard_fallback_overwrite.py (e) does. If those
  are pruned, the first check fails by name ("the replay inputs exist"). They could be copied into tools-local/fixtures/ later.
- `tools-local/delegate-cw.py` finds only dri-delegate sessions. Run on this builder's transcript, it read 0.26M CW (MEASURED,
  at about 27 calls).

## Self-review against BUILDER-CHECKLIST
1. N.A.: no Lean answer or relay changed.
2. PASS: the row's deliverables (MEASURE count, helper after tm-unstamp, stub test before/after, staged install, decider read)
   are in `measure.txt`, `tm-remote-parallel.sh.diff`, `test-on-staged.log` / `test-on-installed.log`, and INSTALL above.
3. PASS: 4/4 seeded bugs caught (`seeded-bugs.json`), and the test fails 7/11 on the installed script.
4. PASS: valid inputs still pass. test_tm_remote_parallel.py gives 58/58 on both scripts (`suite-tm-remote-parallel-*.log`).
5. N.A.: no R8 binding.
6. PASS: the evidence is pinned by `md5.txt` (staged script and test, installed helper files). The gate runs on the committed
   HEAD (the chain).
7. PASS: no SIGNED or reserved cell; no DELTA row.
8. N.A.: no user-visible VE change, so no DELTA row.
9. N.A.: no VE test or product file changed (docs/infra only). `run-selected.log`.
10. N.A.: no Lean.
11. PASS: fails closed. A helper failure or any unexpected path leaves the parts as they are and the merge refuses (test (d));
    any other input difference is still refused (test (c)).
12. N.A.: one extra helper call per split merge (git ls-tree and cat-file on HEAD); the replay merged 6 parts end to end in the
    test run.
13. N.A.: no test removed or renamed.
14. PASS: both directions are tested ((b) accept; (c) and (d) refuse). Each claim above cites its log. Spec re-read: see the
    change section.
15. PASS:
    - No overclaim: the count is "0, preventive", from `measure.txt`.
    - No cut: none.
    - Every new check can fail: m1-m4.
    - Limits: N.A., no new limit.
