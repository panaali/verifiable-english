# tm-build-timeout-1120: why the T1 final-coverage nightly ends in build timeouts, and the fix

**Summary.**
- Status: review. Install read sent (inbox/dri/20261120T073932Z-tm-build-timeout-1120-4071591.md). The decider INSTALLED it
  at 07:46Z and relaunched one `--once` sweep (CURRENT-STATE.md). The live tm-nightly.sh, tm-nightly.py and
  tools-local/test_tm_build_timeout_heavy.py match `evidence/staged-sha256.txt` (checked 08:22Z).
- HEAD: VE branch infra/tm-build-timeout-1120 adds one docs-only commit on ef7ecd59ac: this report, its evidence and the
  manage-agents diffs under `docs/infra/tm-build-timeout-1120/` (the pre-review gate's [commits] check). No VE product code
  changed. The change is in manage-agents, staged as `.new-tmbto`.
- What changed: a resumed record's build-timeout ids run last, in parts of <= 4 at trust_mutants `--jobs 2`.
- Open items: install and relaunch (HUMAN: the decider); a disposition row for 5 non-timeout UNKNOWN (HUMAN: the DRI). Every
  other item here is AGENT and done.
- No DELTA row and no DRI signature needed.

Row tm-build-timeout-1120 (infra, p90; decision reviews/dri-decisions-20261120-tm-final-coverage.md item 2). Builder: Opus 5.5,
2026-11-20. INSTALL READ applies: nothing is installed and the nightly is not relaunched. The edits are staged as
`.new-tmbto`. No DELTA row (manage-agents tooling, not a trust-base change). No VE product code changed. The VE branch
infra/tm-build-timeout-1120 carries only the docs-only record `docs/infra/tm-build-timeout-1120/` (precedent: infra/chain-gate-empty-ve-diff).

**In one line.** The cause is CPU per build, not the timeout value. Each remote part runs trust_mutants with `--jobs 8` inside
a 9-10-core tm scope on ve-cloud-2. The heavy-cone mutants' builds then get about 1.1 cores each. A heavy cone needs
2,583-3,913 CPU-s (MEASURED), so those builds run past 1800 s and often past 3600 s. On ve-cloud-2, 11-16..19, 460 of 477
heavy-file tries were build timeouts. The fix: a resumed record's build-timeout ids run last, in small parts at `--jobs 2`.
Before the fix, no complete record comes at these rates. After it, one comes in about 9-22 sweeps (ESTIMATE, section 4).

## 1. MEASURED: judged vs timed out, per day, host, file and timeout

Sources: every part record `test-skip/nightly/parts-*/part-*.json`, with the day each part ended (`parts.tsv`); the records
`test-skip/nightly/2026111[6-9]*.json`; `test-skip/nightly.log`; the part logs `test-skip/nightly-run-*.log`;
`cloud2-runs.jsonl`; `remote-hosts-load.jsonl`. Scripts and their outputs are in `evidence/` (`perday.py` -> `perday.out`,
`runs.py` -> `runs.out`, `parts.py` -> `parts.out`, `rate.py` -> `rate.out`, `corr.py` -> `corr.out`, `files.py` -> `files.out`).
A build timeout is an UNKNOWN with "did not finish in N s (--build-timeout)", the rule of tm-nightly.py `build_timeout`.
"Judged" counts every other row that is not NOT RUN.

| day (part end) | judged | build timeouts | where the timeouts ran | timeout in force |
|---|---|---|---|---|
| 11-16 | 90 | 161 | ve-cloud-2 161 | 1800 s |
| 11-17 | 217 | 190 | ve-cloud-2 181, Actions 9, vm1-idle 0 | 1800 s; the 16:20Z run: 3600 s (21 of the ve-cloud-2 timeouts) |
| 11-18 | 0 | 0 | VM1 was shut down from 11-17 22:08Z to 11-19 00:48Z (CURRENT-STATE.md, 11-19 07:27Z line) | - |
| 11-19 | 64 | 170 | ve-cloud-2 170 | 1800 s (see below) |

(`evidence/perday.out`; the 11-17 Actions rows ran on 4-core runners at `--jobs 4`.)

**The orchestrator's figures match the measurements** for 11-16 (90 judged, 161 timeouts) and 11-19 (64 judged, 170
timeouts). 11-17 was higher (217 judged, 190 timeouts) because two sweeps ran that day. The 21 judged rows of the 11-17
16:20Z run were never merged: VM1 shut down at 22:08Z, before the merge. No record `20261117T1620Z.json` exists.

**Which files.** Build-timeout rows of 11-16..19, by mutated file (`evidence/files.out`):

| file | build timeouts |
|---|---|
| VE/Compose/Dispatch.lean | 140 |
| VE/Cardinality/Wire.lean | 92 |
| VE/EnglishGrammar/SourceWords.lean | 54 |
| VE/SpeechActs/Wire.lean | 52 |
| VE/EnglishGrammar/Advice.lean | 41 |
| VE/EnglishGrammar/Run.lean | 28 |
| VE/Service/Standalone.lean | 16 |
| VE/Acts/Lexical.lean | 15 |

**"Heavy" files.** 15 files have a build timeout on at least 20% of their tries since 11-10 (`evidence/heavy20.json`). On
ve-cloud-2 at `--jobs 8`, heavy-file tries ended like this:

| period | judged | build timeouts | timeout share |
|---|---|---|---|
| 11-10..15 | 72 | 248 | 77% |
| 11-16..19 | 17 | 460 | 96% |

Light-file tries on ve-cloud-2, 11-16..19: 328 judged, 52 build timeouts (`evidence/perday.out`, H and L columns).

**Host.** After 11-13 every ve-cloud-2 part ran 8 jobs (`"jobs": 8` in each part record; `evidence/parts.out`). ve-cloud-3
has been paused since 11-13 16:03Z (`remote-hosts.tsv`), so ve-cloud-2 has been the only remote host. The part logs show its
5-min load at 70-135 on 32 cores while the 11-19 parts ran (`nightly-run-20261119T0727Z.log`, lines 104-215: "5-min load
134.62 >= 2x 32 cores"). Each tm job runs in its own scope with CPUQuota 9 cores (`remote-hosts-load.jsonl`, 11-09..12:
`"tm": quota_cores 9.0` per job). The default is `C2_TM_CPU:-1000%`, cloud2-job.sh:249. Busy scopes ran at the cap: with 2 tm
jobs, median use was 9.19 cores and p90 18.04.

**Build time reached.** A timed-out build is killed, so only a lower bound is known: the limit. The timeout share changed
little with the limit or the load. The table groups the 11-16..19 ve-cloud-2 parts, whose ids are mostly heavy, by how much
of each part's time overlapped a gate on the host (`evidence/gate-overlap.py` -> `gate-overlap.out`, from `corr.out`):

| limit | gate overlap | timeout share | tries |
|---|---|---|---|
| 1800 s | 0.00-0.15 | 62% | 428 |
| 1800 s | 0.21-0.48 | 61% | 147 |
| 1800 s | 0.53-0.98 | 56% | 242 |
| 3600 s | 0.86-1.01 | 53% | 40 |

So these builds do not finish just past 1800 s. Half of them also ran past 3600 s. A looser timeout alone is not the fix.

**The 3600 s limit was not in force on 11-19.** The DRI took TM_NIGHTLY_BUILD_TIMEOUT=3600 and pools remote+idle on 11-17
(reviews/dri-decisions-20261117-tm-drain-vm1-idle.md item 1), and nightly.log line 791 shows them in force from 11-17 16:24Z.
VM1 then shut down at 22:08Z. On 11-19 07:30Z restart-services-20261014.sh relaunched the nightly. Its line 61 is
`env TM_NIGHTLY_POOLS=remote zsh $M/tm-nightly.sh`, so the run started without the 3600 s limit and without the VM1 slot:
nightly.log line 854 has no "TM_NIGHTLY_BUILD_TIMEOUT" line, and the 11-19 rows say "did not finish in 1800 s". The 170
timeouts that day were at 1800 s. This loss is real, but it is not the largest cause: at 3600 s the share was still 53%.

## 2. The single largest cause: 8 heavy-cone builds share one 9-10-core scope

**Direct measurement.** I timed one full rebuild of the VE/Compose/Dispatch.lean cone on VM1, after adding a declaration
to the file. Setup: a scratch copy of this worktree's built lean/ with the .olean files hard-linked
(`evidence/mkscratch.py`, `cone.sh`). Targets: the sweep's 51 Lean `--test` modules (`evidence/targets.txt`). Lake ran 676
jobs, pinned with `taskset` (`evidence/cone8.log`, `cone3.log`):

| cores | wall | CPU (user + sys) |
|---|---|---|
| 8 | 936 s | 2,583 s |
| 3 | 1,753 s | 3,913 s |

The cone parallelizes: 8 cores gave 1.9x the speed of 3. It is not bound by a serial chain of about 1,500 s. That reading
(the 11-17 Part 0) took a part's average over its check builds, 40,747 s / 25 = 1,630 s, for the 11-16 16Z part 2. But 22
of that part's mutants ended in a 1,800 s timeout, so the average mostly measured the timeout. In the same part, the builds
that finished took about 210 s on average (`rate.out`, "avg_nonTO_run").

**Arithmetic.** 8 jobs in a 9-core scope give about 1.1 cores per build. At 2,583-3,913 CPU-s a cone, one heavy build then
takes at least 2,300-3,500 s. That is past 1800 s every time and near 3600 s, which matches 96% and 53%. The control build
(`stage_controls`, the same cone without the mutant) costs about as much again. On VM1 it averaged 1,468-2,578 s per run
(11-17 16:20Z parts 10, 1 and 6; `parts.out`).

**The same mutants with more cores per build.** On VM1 at 2-5 cores a build, 0 of 56 check and control builds timed out
(`parts-20261117T1620Z/part-{1,6,10}.json`; VE docs/infra/tm-drain-vm1-idle/trial/trial{1,2}-part-1.json):

| run | cores / jobs | limit | builds |
|---|---|---|---|
| trial 1 | 5 / 1 | 1800 s | 3 |
| trial 2 | 7 / 3 | 3600 s | 23 |
| live p1 | 5 / 2 | 3600 s | 6 |
| live p6 | 12 / 6 | 3600 s | 18 |
| live p10 | 4 / 2 | 3600 s | 6 |

Check builds there averaged 752-1,838 s: lake seconds over runs, from the steps of the same records.

**Candidates that do not bind.** Each is MEASURED within the 11-16..19 heavy set:
- **Host load from gates.** Gates have CPUWeight 1000 since 11-14 (dri-gate50). Parts with gate overlap >= 0.5 had a 56%
  timeout share and parts with < 0.2 had 62%.
- **Two vs three concurrent nightly parts.** The share was 0.58 vs 0.64 (`corr.out`).
- **Cold olean cache.** trust_mutants copies every scratch from the control-built first scratch (tools/trust_mutants.py,
  around line 2410), so a cold setup costs part time, not build time.

The binding variable is cores per concurrent build, and it is set in manage-agents. cloud2-run.sh:102 has
`tcap=${CLOUD2_TM_JOBS:-8}`, and nothing passes a lower `--jobs` to remote parts: tm-nightly.sh adds one only for local
vm1-idle parts. The cause is in manage-agents, not in VE's trust_mutants, so no VE feature branch is needed.

## 3. The fix (staged, not installed)

Staged files, in /home/seyran/code/manage-agents:

| staged file | change |
|---|---|
| `tm-nightly.py.new-tmbto` | +20 lines: subcommand `heavy <record>` prints the record's build-timeout UNKNOWN ids in numeric id order (`idnum`). |
| `tm-nightly.sh.new-tmbto` | +25/-2 lines: when a record is resumed, its build-timeout ids that are still to judge run last, in parts of their own (at most TM_NIGHTLY_HEAVY_PART, 4 ids), each with trust_mutants `--jobs TM_NIGHTLY_HEAVY_JOBS` (2). |
| `tools-local/test_tm_build_timeout_heavy.py.new-tmbto` | the new test file (8 tests). |

Details of the tm-nightly.sh change:
- The other ids run first with the command as before. A sweep with no resumed record is unchanged.
- TM_NIGHTLY_HEAVY_JOBS takes a whole number 1-8; 0 or off restores the old behaviour. TM_NIGHTLY_HEAVY_PART takes 1-50. Any
  other value is refused, said in the log, and the default is kept.
- A local vm1-idle part keeps its own `--jobs`, which comes last on its command.
- The log says "heavy: <n> of the <m> ids to judge are build timeouts in <record>: they run last, in parts of <= 4 at
  --jobs 2", and each heavy part line carries "--jobs 2 (heavy: build timeouts in <record>)".

Checks: `zsh -n tm-nightly.sh.new-tmbto` and `python3 -m py_compile tm-nightly.py.new-tmbto` both pass. I removed the
`.pyc` that py_compile wrote.

**Why `--jobs 2`.** In a 9-10-core scope, 2 jobs give about 4.5-5 cores a build. By the measurement above, a cone build
then takes about 1,100-1,300 s (interpolated between 936 s at 8 cores and 1,753 s at 3). That is under 1800 s with margin,
so a heavy mutant's 2-3 cone builds fit a 6,300 s part. The throughput of the scope does not fall: the CPU is the same, and
none of it is spent on builds that are killed.

**Verdicts.** No verdict turns KILLED or SURVIVOR because of this change. It changes only the order of parts and
`--jobs`:
- A build past `--build-timeout` still returns TIMED_OUT -> UNKNOWN (tools/trust_mutants.py:1297). Test (3): a heavy id that
  times out again stays that UNKNOWN, and the record is not complete.
- A finished build's errors do not depend on `--jobs`.
- merge (`parts.tsv` ids) and classify are unchanged.

**Tests.** `TMN_SH=tm-nightly.sh.new-tmbto TMN_PY=tm-nightly.py.new-tmbto python3 -I
tools-local/test_tm_build_timeout_heavy.py.new-tmbto`:
- On the INSTALLED files: 6 of 8 FAIL (`evidence/test-live.log`): heavy_ids_run_last, heavy_parts_hold_at_most,
  heavy_timeout_again, refused_values, remote_pool_heavy_part_carries_jobs, only_build_timeout_unknowns_in_id_order. The 2
  that pass are the "as before" cases: off, and a fresh sweep.
- On the STAGED files: 8 of 8 pass (`evidence/test-staged-final.log`).
- Scratch only: each test makes its own temporary home, repository and worktrees (the test_tm_nightly_split.py harness).

**Regression run on the staged files.** 10 of the 11 existing tm-nightly test files pass (`evidence/reg-*.log`):
blame_prebase 3, build_timeout 16, complete 9, escape_rows 15, forward_kill 12, lookups 17, split 11, tests_allow 5,
unknown_disposition 3, drain_vm1_idle 5. test_tm_nightly_restart_main.py has 1 failure and 1 error:
test_pools_absent_routes_as_before and test_remote_every_pool_refusing_no_vm_no_mac. Both test mac-pytest.sh, and both fail
the same way on the live files (`evidence/reg-restart-live.log`). They predate this item and I did not edit them.

**Selected VE run, once.** `mac-pytest.sh --select -- --base ef7ecd59ac --run` exited 0 on GitHub Actions (6 shards,
2,502 s; `evidence/select.tail.log`, the last 40 lines). Nothing in VE changed, so this is the branch's once-only check.

**Seeded bugs.** Each was planted in a scratch copy of the staged files and each made the new tests fail
(`evidence/seed-logs/*.log`):

| # | file | bug | failing tests |
|---|---|---|---|
| S1 | tm-nightly.py | `heavy` prints every row (filter dropped) | test_heavy_ids_run_last_in_own_parts_at_two_jobs, test_remote_pool_heavy_part_carries_jobs, test_only_build_timeout_unknowns_in_id_order |
| S2 | tm-nightly.sh | no `--jobs` on heavy parts | 5 tests, incl. test_heavy_ids_run_last_in_own_parts_at_two_jobs and test_remote_pool_heavy_part_carries_jobs |
| S3 | tm-nightly.sh | a light part is not cut at the heavy boundary | test_heavy_ids_run_last_in_own_parts_at_two_jobs, test_remote_pool_heavy_part_carries_jobs |
| S4 | tm-nightly.sh | no TM_NIGHTLY_HEAVY_PART cap | test_heavy_parts_hold_at_most_heavy_part_ids, test_refused_values_keep_the_defaults |
| S5 | tm-nightly.sh | bound 1-8 widened to 1-9 | test_refused_values_keep_the_defaults |

## 4. ESTIMATE: days to one complete record that covers main (t1-final-main 17581425)

**Work left (MEASURED).** Plans come from `evidence/planlist.py`, which calls trust_mutants' own `plan()` in scratch
worktrees, since removed (`evidence/plan-counts.txt`):

| plan | mutants | heavy | light |
|---|---|---|---|
| 9ccbf3fdf since 039d3dd51 (planned 7,038) | 2,324 to judge | 423 | 1,901 |
| main 727d1d210 since 9ccbf3fdf | 1,785 | 173 | 1,612 |
| main fresh since 039d3dd51 | 8,719 | 777 | 7,942 |

The 2,324 at 9ccbf3fdf are 2,161 NOT RUN and 163 unallowed UNKNOWN. Of the 163, 158 are build timeouts and 5 are not.

Coverage path P1, which the loop already follows (tm-nightly-complete (b)): complete 9ccbf3fdf, then sweep main since
9ccbf3fdf. The NOT RUN ids M5332-M7038 were never tried at this head. Every 10-hour sweep spent its budget on the heavy ids,
which come first, and then stopped ("the 36000-s budget is spent", nightly.log, 11-19 17:19Z).

**Before the fix.** On ve-cloud-2, 17 heavy rows were judged in 11-16..19, about 6 per sweep (MEASURED). That gives 596
heavy / 6 = about 100 sweeps. Each of those tries also times out about 96% of the time, and one timeout on the last try
leaves the record incomplete. ESTIMATE: no complete record at these rates (more than 100 days). The DRI's 22-34 days counts
the NOT RUN only, at 64-100 a day; the timeouts block completion in any case.

**After the fix, P1, one 10-hour sweep a day, 3 remote slots on ve-cloud-2.** About 24 useful part-hours a sweep (3 x 10 h,
less about 20% setup):

| step | ids | rate per part-hour | sweeps |
|---|---|---|---|
| light | 3,513 | 35-54 (ve-cloud-2 11-12..13, MEASURED, mostly light) | 2.7-4.2 |
| first try of the heavy ids that are not yet build timeouts, at 8 jobs (they time out once, then join the heavy parts) | ~438 | about 2,000 slot-s each | ~1.25 |
| heavy, at 2 jobs | 596 | 1.5-5 | 5-16.5 |

Sources for the heavy rate: VM1 trial 2, 5.1 per hour at 7 cores (MEASURED); and the CPU model, 9 cores x 3,600 s /
(2-3 cone builds x 2,583-3,913 CPU-s).

Total: **about 9-22 sweeps, so 9-22 days at one sweep a day, or 4-10 days with --once sweeps back to back** (about 2.2 a
day). The VM1 idle slot (remote+idle) adds about 5 heavy an hour while its gate is open (trial 2).

Completion also needs a disposition for the 5 unallowed non-timeout UNKNOWN at 9ccbf3fdf: M-ids in
VE/Commands/StepsExamples.lean (3), VE/Service/Registry.lean (1) and VE/Readings/ActsExamples.lean (1), from the nightly.log
"not complete" line. That is not this item's work, and no open row owns it today: tm-nightly-unknown-disposition is done and
-2 is merged (BACKLOG.jsonl). See Notes for the DRI. Path P2 (a fresh sweep of main, 8,719 mutants) is about 2x P1.

**Time limit for P1.** resume refuses a record 4 days old or more (tm-nightly.py resume). 20261119T0727Z.json reaches that age
at 2026-11-23 07:27Z, and each new partial record restarts the clock. If no sweep runs before then, its 4,714 judged rows
(7,038 planned - 2,324 to judge) are not carried, and P1 becomes P2.

## Install read (not done here)

```
cd /home/seyran/code/manage-agents
systemctl --user list-units 've-svc-tm-nightly*' --no-legend      # must print nothing (never replace a running script)
cp -p tm-nightly.sh tm-nightly.sh.bak-20261120tmbto
cp -p tm-nightly.py tm-nightly.py.bak-20261120tmbto
mv tm-nightly.sh.new-tmbto tm-nightly.sh
mv tm-nightly.py.new-tmbto tm-nightly.py
mv tools-local/test_tm_build_timeout_heavy.py.new-tmbto tools-local/test_tm_build_timeout_heavy.py
python3 -I tools-local/test_tm_build_timeout_heavy.py           # 8 OK on the installed files
# undo: mv tm-nightly.sh.bak-20261120tmbto tm-nightly.sh; mv tm-nightly.py.bak-20261120tmbto tm-nightly.py
```

**Relaunch: one final-coverage sweep.** The loop exits at once now, because it is 7 days past test-skip/t1-end, so a sweep
runs with `--once`. It carries the 3600 s limit and the VM1 slot that the DRI took on 11-17 and the 11-19 restart dropped:

```
setsid nohup zsh iso.sh svc-tm-nightly 1G -- env TM_NIGHTLY_POOLS=remote+idle TM_NIGHTLY_BUILD_TIMEOUT=3600 zsh tm-nightly.sh --once >> svc-tm-nightly.log 2>&1 < /dev/null &
```

- P1, recommended: run it before 2026-11-23 07:27Z. It resumes 20261119T0727Z.json at 9ccbf3fdf; main follows once that
  record completes.
- A sweep of main itself now (P2): add `TM_NIGHTLY_FRESH=1`. That costs about 2x and drops the carried verdicts.

## Notes for the DRI

- Completion at 9ccbf3fdf also needs a disposition for 5 unallowed non-timeout UNKNOWN. They are judged again on each resume
  and come back the same, so they block completion whatever the build speed. No open row owns them. My recommendation is a
  row like tm-nightly-unknown-disposition-2 for these 5. This is in the install-read message.
- restart-services-20261014.sh line 61 still launches the nightly as remote-only with no TM_NIGHTLY_BUILD_TIMEOUT. That is
  how the 11-17 decision was lost on 11-19. The loop exits at once today, so the line does nothing now. If the loop is
  re-enabled, the line should carry the decision's env.
- The `remote-load` service stops sampling at `--until 2026-11-13` (restart-services line 60), so remote-hosts-load.jsonl
  has no host CPU samples after 11-12. A ve-cloud-2 measurement of the fix's heavy rate will need it, or `sar`.
- Setup per ve-cloud-2 part was 1,100-1,400 s at an unchanged head ("setup 1383s", nightly-run-20261119T0727Z.log line 78),
  about 20% of each 6,300 s part. It costs time but does not cause timeouts.
- The 11-17 Part 0 figure, "a heavy check ~1,500-1,650 s at best, bound by its serial chain", came from an average
  dominated by 1,800 s timeouts (section 2). The direct measurement corrects it.
- `python3 -I tools-local/delegate-cw.py` printed "own session not found" (no VE_STEP / CLAUDE_CONFIG_DIR from
  dri-delegate.sh), so I could not read the CW figure. No MEASURED number to quote.

SIZE: 45 product (tm-nightly.sh +25/-2 of which 13 code, tm-nightly.py +20 of which 10 code), 126 tests, ~190 other
hand-written lines (this report and the evidence scripts).

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed: N.A. (no relay, no Lean).
2. Every deliverable built, no rule broken: PASS. Measure (section 1), cause (2), staged fix and failing test (3), estimate
   (4), install read. Nothing installed or relaunched; edits staged as .new-tmbto; scratch dirs only (test harness tmp dirs;
   /tmp/tmbto).
3. Tests can fail: PASS. 6 of 8 fail on the installed files (`evidence/test-live.log`); seeded bugs S1-S5 each fail
   named tests.
4. Python, Lean and Rust agree: N.A. (no product language change in VE).
5. R8 binding: N.A.
6. Gate evidence matches the final HEAD: PASS. No VE commit, and the chain's gate runs on the unchanged HEAD. The staged
   files tested last are recorded in `evidence/staged-sha256.txt` (tm-nightly.sh.new-tmbto b9bf29028814ec55...,
   tm-nightly.py.new-tmbto f494ff523c2365ad..., test a4fcec7caafff90c...).
7. No unsigned item: PASS. No DELTA row (the task says none), and no SIGNED cell.
8. DELTA: N.A. (manage-agents tooling).
9. Test selection: N.A. (no VE file changed).
10. Lean statements: N.A.
11. Budgets fail closed: PASS. A heavy build past --build-timeout stays UNKNOWN and the record stays incomplete
    (test_heavy_timeout_again_stays_unknown_not_complete). Part --budget and --deadline are unchanged. Refused env values
    keep the defaults (test_refused_values_keep_the_defaults). The tests have no sleep and no elapsed-time assert.
12. No CPU or memory regression: PASS. The same scope CPU runs 2 builds instead of 8; light parts are unchanged
    (test_off_is_as_before, test_fresh_sweep_unchanged).
13. Test-removed trailers: N.A. (no test removed).
14. Both directions, cited evidence, spec re-read: PASS. Accept and refuse cases: heavy -> --jobs 2, light -> none, off -> as
    before, 9/abc refused. Every count above names its script or log in evidence/. Spec re-read: "a verdict must never turn
    KILLED/SURVIVOR because of the change" against prompts/task-tm-build-timeout-1120.txt line 11 (test (3)); "a looser
    timeout alone is not the fix unless step 1 shows builds finish just past it" against the same line (section 1 table:
    53% past 3600 s).
15. No overclaim: PASS. "Unchanged" claims cite test_fresh_sweep_unchanged and test_off_is_as_before. The estimates are
    marked ESTIMATE. The "0 of 56" and "460 of 477" counts cite their record files. No cut deliverable. Every new check has a
    seeded bug (S1-S5). No limit change.
