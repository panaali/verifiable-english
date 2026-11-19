# vs-sample-bounded: the VM verdict-sample reference keeps the full part, resumes a deadline cut, and sizes its deadline from the cloud part's run time

INSTALL WAITS FOR DECIDER READ. No DELTA rows: no Lean, Python, Rust or trust-base file of the VE repo changed. Nothing is
reserved for a DRI signature.

Decision: `reviews/dri-decisions-20261114-lp1701.md` item 1 (LP-20261114T1701-1; the 12-mutant cut is WITHDRAWN).
Branch `infra/vs-sample-bounded`. The work is in manage-agents. Every changed installed file is STAGED as `<file>.new-vsw`;
none was moved over the live file. This directory holds the evidence: the three diffs, the test logs and the seeded-bug logs.
`SHA256SUMS` pins the installed and staged files that were tested.

SIZE: 70 product, 113 tests, 150 other hand-written lines. Product is verdict-sample.sh, +70/-14 diff lines (`grep -c` on
`verdict-sample.sh.diff`). Tests are test-comparators.zsh (+103/-2) and test_vs_ref_notrun.py (+10/-8). Other is this
report.

## What changed (staged `verdict-sample.sh.new-vsw`)

- **(a) Resume, not restart.** A reference run is a deadline cut when trust_mutants exits 4 and writes a `partial` record
  (exit 4 is the partial exit, `tools/trust_mutants.py:148,2460`). A cut is renamed aside as before
  (`vm-ref.partial-[c2-]deadline-<UTC>[-n].json`). findref only reads `*/vm-ref.json`, so it never sees an aside. The run
  is then repeated in the same worktree with `trust_mutants --resume <that partial>` and every other argument unchanged. This
  happens in a new `refpasses` loop, which `vmrun` (the VS_TM hook and the real worktree path) and `c2ref` (ve-cloud-2;
  cloud2-run.sh already ships a `--resume` file) both use. The loop stops when a run is not a cut. It also stops when a
  resumed run judges no more ids than the cut before it, or after `VS_REF_PASSES` (6) runs. A cut that is never resumed to
  completion ends exactly as before: row "not run", vdone notrun, the sample stays pending, and the pool and streak are
  untouched. A later sample of the same part resumes the newest cut from its own host (`vm-ref.partial-deadline-*` on the VM,
  `vm-ref.partial-c2-deadline-*` on ve-cloud-2), so a retry does not restart either. The comparison is still over the full
  part, every id: the reference is the whole part's record, and `cloud-verdict-compare.py` is unchanged.
- **(b) The deadline is sized from the cloud record.** The job's `--budget`/`--deadline` are still dropped. The fixed
  `VS_REF_BUDGET` 21600 is replaced by `--budget = ceil(VS_REF_K (2) x wall x cloud jobs / reference jobs)`. wall is the job
  record's `tm_s`, or the cloud JSON's `seconds` when `tm_s` is missing. cloud jobs is the cloud JSON's `jobs`. The reference
  jobs are `VS_REF_JOBS` (6, now also the VM run's `--jobs`) or 8 on ve-cloud-2. The budget is at least `VS_REF_MIN_S` (900)
  s and at most `VS_REF_BUDGET` (21600; 0 means no cap). `VS_REF_BUDGET` is also the budget when the cloud record gives no
  run time. For p9 (tm_s 3205.3, jobs 4) the VM budget is 4274 s, where it used to be 21600.
- (c) The rule that a pending sample never blocks a decide launch is not built here (row decide-launch-bounded, as the spec
  says).

## Tests (failing first)

- `test-harness/comparators/test-comparators.zsh.new-vsw` adds the section "verdict-sample.sh: the full-part reference
  resumes a deadline cut ..." with 14 checks. The fixture is a read-only copy of `tools-local/fixtures/vsnr-p9-9ccbf3fd`.
  A VS_TM stub and a cloud2-run.sh stub stand in for the run, and HOME, uv and lake are stubbed into the scratch directory.
  - On the installed script: `VS=$M/verdict-sample.sh zsh test-comparators.zsh.new-vsw` gives **39 passed, 14 failed**
    (`harness-installed.log`). That is 13 new checks plus 1 pre-existing failure. The 14th new check ("no cloud run time at
    all: the fixed VS_REF_BUDGET (21600)") passes on both scripts, by design.
  - On the staged script: `VS=$M/verdict-sample.sh.new-vsw ...` gives **52 passed, 1 failed** (`harness-staged.log`). The 1
    failure is the pre-existing one below.
  - The spec's named checks: "resume: a budget-cut reference ... is resumed", "no restart", "it ends with all ids judged"
    (failing first, then passing), and "deadline: from the cloud record, not the job's --budget 4532" (= 4274).
  - The 5 "another nightly part" checks and the NOT COMPARED checks still run in this file and pass on both scripts (both
    logs show no FAIL in that section).
- `tools-local/test_vs_ref_notrun.py.new-vsw` has two assertions updated for the new behaviour. The default budget is now
  4274 from the cloud record, with VS_REF_BUDGET=3000 acting as the cap. A cut reference now leaves 2 asides: the cut and
  its resumed run, which judged no more.
  - Staged: `VSNR_SFX=.new-vsw python3 -I tools-local/test_vs_ref_notrun.py.new-vsw` gives OK, 25 tests (`vsnr-staged.log`).
  - Installed: the same file gives 2 FAIL, exactly the two updated tests (`vsnr-installed.log`).
- `test-harness/cloudplumb/test-advfix6.zsh` hardcodes the live script. A copy pointed at the staged script by `VS_SCRIPT`
  gives 68 passed, 0 failed (`advfix6-staged.log`).
- `test-harness/cloudplumb/test-advfix4.zsh` with `VS_SCRIPT` gives 46 passed, 6 failed on **both** the installed and the
  staged script, with the same 6 names (`advfix4-installed.log`, `advfix4-staged.log`). These failures are pre-existing (see
  Notes).
- VE repo selected tests: only `docs/infra/vs-sample-bounded/` changed in this worktree. The run's output is in
  `selected-run.log`, from `zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`.

## Seeded bugs (each planted in a copy of `verdict-sample.sh.new-vsw`, run, and then discarded; the staged file was not edited)

The language is zsh with embedded Python, all in `/home/seyran/code/manage-agents/verdict-sample.sh` (staged as
`.new-vsw`). The logs are in `seeded/`, and each one starts with the planted replacement. Every count below includes the 1
pre-existing failure.

| Seed | Behaviour | Failing check(s) |
|---|---|---|
| S1 drop `--resume $rp` from the run | (a) resume | "resume: a budget-cut reference ... is resumed", "a later sample resumes the part's earlier VM cut", "c2ref: ve-cloud-2 resumes its own cut" (4 failed) |
| S2 drop the jobs scaling | (b) sizing | "deadline: from the cloud record ... = 4274", "another cloud wall", "the factor k", "no tm_s ... seconds" (6 failed) |
| S3 drop the no-progress stop | (a) bounded resume | "resume: a resumed run that judges nothing more stops (2 runs, not 3)" (2 failed) |
| S4 the VM takes any host's cut | (a) own host's cut only | "resume: the VM never resumes a ve-cloud-2 cut" (2 failed) |
| S5 keep the job's `--budget` | (b) job budget dropped | "deadline: from the cloud record, not the job's --budget 4532" and the 2000/6411/1200/900/c2 sizing checks (8 failed) |
| S6 ve-cloud-2 stops at a cut (restart path) | (a) in c2ref | "c2ref: ve-cloud-2 resumes its own cut" and the VM resume checks (8 failed) |

## Spec re-read

- "the VM reference keeps the full part": no `--only` is added and no mutant is dropped. `refargs` keeps the job's
  `--only`/`--test`/`--base`. Checked against the row note (a) in the task, and `alljudged` checks that the cloud's 31 ids
  are all judged.
- "on a deadline exit RESUMES the judged partial with trust_mutants --resume <partial> ... instead of restarting": `refpasses`.
  Checked against `tools/trust_mutants.py:2236-2238,2327-2335` (resume of a partial record at identical inputs).
- "the partial is renamed so findref cannot take it": `aside`, and findref globs only `*/vm-ref.json`
  (`actions-health.py` findref, line 548). Test: "resume: the set-aside cut is no reference for findref".
- "the job's own --budget/--deadline is dropped from the reference args and the reference deadline is SIZED from the cloud
  part's own run time (from the cloud job record; ... k x cloud wall at the VM's jobs)": `refbudget`, which uses job.json
  `tm_s` (the cloud job record) and the cloud JSON's `jobs`.
- "compare stays full-part (every id)": `cloud-verdict-compare.py` is unchanged.
- "(c) ... not here": not built.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relayed Lean answer).
2. Deliverables built, no rule broken: PASS. (a) and (b) are built and staged. (c) is out of scope per the spec. Nothing was
   moved over a live file.
3. Tests and gates can fail: PASS. 13 checks fail on the installed script, and the seeded bugs S1-S6 fail them.
4. Python/Lean/Rust agree: N.A.
5. R8 binding: N.A.
6. Gate evidence matches final HEAD: PASS. The chain gates the final HEAD, which changes only `docs/`.
7. No unsigned item: PASS. There are no DELTA rows.
8. DELTA: N.A. No user-visible VE change.
9. Test selection: N.A. for VE, since only docs changed. The harness section sits in the file the spec names.
10. Lean statements: N.A.
11. Budgets fail closed: PASS. A cut that is not resumed to completion is "not run" and pending, never EQUAL and never
    MISMATCH ("resume: a resumed run that judges nothing more stops ...", "VS_REF_PASSES bounds the runs"). With no cloud
    time, the old fixed budget applies ("no cloud run time at all").
12. No CPU/memory regression: PASS. Each pass is bounded by the sized budget, and passes need progress, capped at 6. The p9
    first pass is 4274 s, down from 21600.
13. Test-removed trailer: N.A. Nothing was removed.
14. Both directions / cited evidence / spec re-read: PASS. A cut is resumed, and a full record is not (the budget cases run
    once). The own host's cut is resumed and the other host's is not. Exit 4 with a partial resumes, and exit 2 does not
    (test_failed_reference_without_partial_is_set_aside). Every claim above cites a log in this directory.
15. Overclaim / silent cut / new check can fail / limits before work: PASS. (c) is stated as not built. Seeds S1-S6 cover
    every new check. Budgets are computed before the run.

## Install (waits for the decider's read)

```
cd /home/seyran/code/manage-agents
cp -p verdict-sample.sh verdict-sample.sh.bak-20261119-vsw
cp -p test-harness/comparators/test-comparators.zsh test-harness/comparators/test-comparators.zsh.bak-20261119-vsw
cp -p tools-local/test_vs_ref_notrun.py tools-local/test_vs_ref_notrun.py.bak-20261119-vsw
mv verdict-sample.sh.new-vsw verdict-sample.sh
mv test-harness/comparators/test-comparators.zsh.new-vsw test-harness/comparators/test-comparators.zsh
mv tools-local/test_vs_ref_notrun.py.new-vsw tools-local/test_vs_ref_notrun.py
zsh test-harness/comparators/test-comparators.zsh      # expect 52 passed, 1 failed (the pre-existing "detail: another line")
python3 -I tools-local/test_vs_ref_notrun.py           # expect OK
```

No restart is needed. cloud-pull.sh starts each sample as a fresh `zsh verdict-sample.sh` through iso.sh, and a sample
already running keeps the old inode because `mv` does not rewrite it.

## Notes for the DRI

- Pre-existing failure, not touched: comparators "detail: another line in the same outside test still trips (VERDICTS
  DIFFER, exit 1)". `cloud-verdict-compare.py` now says "KILLED BY ANOTHER CHECK (both KILLED; not a mismatch)" for that
  case, so the check is out of date. It fails on the installed files with or without this item.
- Pre-existing failure, not touched: 6 test-advfix4.zsh checks compare the VM run's argument list exactly. They have failed
  since vs-ref-notrun-not-compared appended `--budget` (21600 then, the sized value now). The 6 names are the same on both
  scripts.
- Choices made inside scope, taking the conservative option in each case:
  - k = 2.
  - The floor is 900 s, so a tiny cloud part does not spend every pass on planning.
  - The cap is the old 21600, so no single pass holds the VM longer than before.
  - At most 6 passes, and each pass must judge more ids than the last.
  - A pass is resumed only after exit 4 with a partial record. Any other exit is set aside as before and not resumed.
  - A later sample resumes only its own host's newest cut. trust_mutants itself reruns in full when the inputs differ.
- delegate-cw (MEASURED): `python3 -I tools-local/delegate-cw.py` printed "delegate-cw: own session not found (needs VE_STEP
  and CLAUDE_CONFIG_DIR from dri-delegate.sh, or a transcript path)", both times it ran. There is no measurement to quote.
