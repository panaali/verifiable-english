# tm-drain-vm1-idle: VM1's idle cores for the trust-mutant drain, and why parts end in build timeouts

- Status: built and staged in `/home/seyran/code/manage-agents` as `tm-nightly.sh.new-tmidle` (live base md5
  `d4b1487b84b1e6eda462dba731a82e15`). INSTALL WAITS FOR THE DRI'S INSTALL READ (section 7; sent with `msg.sh dri`). I did not
  restart svc-tm-nightly. The new tests are in `tools-local/test_tm_drain_vm1_idle.py` (new file; `TMN_SH=<staged>` picks the
  staged copy, default the live script).
- No DRI signature is reserved and there are no DELTA rows: this is control-plane tooling, with no VE trusted line and no
  verdict rule changed. Trust +0.
- This VE branch holds only this report and its evidence (`part0_measure.py`, `part0-tables.md`, `sar/`, `trial/`, logs,
  `seeded-bugs.json`, `seed_run.py`, `staged-changes.diff`). No VE product code (Lean, Python or Rust) changed.
- Tests: 4 of the 5 new tests fail on the live script and all 5 pass on the staged one (`run-live.log`, `run-staged.log`).
  The fifth (`test_remote_only_mode_never_local`) checks unchanged behaviour, so it passes on both by design. The six
  existing tm-nightly test files pass on the staged script as they do on the live one (`run-regression.log`).
- Seeded bugs: 8 of 8 caught (`seeded-bugs.json`; shell, in the staged file).

SIZE: 54 product (tm-nightly.sh +54/-4, comments included), 177 tests (test_tm_drain_vm1_idle.py, new), ~560 other
hand-written lines (this report, part0_measure.py, seed_run.py; the tables, logs, diff and sar files are records).

Row: tm-drain-vm1-idle (infra p1, PLACEMENT class). Decision: reviews/dri-decisions-20261116-coord-budget.md item 4
(orchestrator BATCH 200749Z), Part 0 BATCH 210454Z, Part 0b BATCH 223244Z.

## 1. Part 0: build timeouts vs verdicts (MEASURED)

Sources: every part record since 11-12 06Z (`test-skip/nightly/parts-*/parts.tsv`, `part-*.json`), the run logs
(`nightly-run-*.log`: setup seconds and clones), the Actions job records (`cloud-jobs/*/job.json`), and the hosts' own
`sar -q` 5-min loads (VM1 and ve-cloud-2, read-only, saved in `sar/`; ve-cloud-3 is paused and unreachable).
Command: `python3 -I part0_measure.py <test-skip> <cloud-jobs> sar --end 2026-11-17T00:00Z > part0-tables.md`. A verdict
is KILLED, SURVIVOR, INVALID or ALLOWED. A build timeout is an UNKNOWN with "did not finish in N s (--build-timeout)",
the rule tm-nightly.py `build_timeout` uses.

**The orchestrator's 24 h numbers reconcile** (`part0-tables.md` F): 10 parts ended on 11-16, all on ve-cloud-2. They
gave 54 verdicts and 36 other UNKNOWN, which is the "90 judged". They also gave 161 build timeouts (75%) and 105 NOT RUN.
The timeout value in force was 1800 s for every timeout since 11-12 (column "timeout value s" in table A). No run set
TM_NIGHTLY_BUILD_TIMEOUT.

Per day and host (table B, excerpt):

| day | host | verdicts | build timeouts | share | verdicts per part-hour |
|---|---|---|---|---|---|
| 11-12 | Actions / ve-cloud-2 / ve-cloud-3 | 204 / 568 / 1127 | 0 / 44 / 111 | 0% / 7% / 9% | 90 / 37 / 34 |
| 11-13 | ve-cloud-2 / ve-cloud-3 | 607 / 572 | 52 / 100 | 8% / 15% | 36 / 28 |
| 11-14 | Actions / ve-cloud-2 | 75 / 426 | 26 / 79 | 26% / 16% | 8 / 22 |
| 11-15 | ve-cloud-2 | 466 | 84 | 15% | 24 |
| 11-16 | ve-cloud-2 | 54 | 161 | 75% | 2 |

What each candidate cause shows:

1. **Host load: it makes the timeouts worse, but it is not what binds.** Table C sorts ve-cloud-2's parts by the host's
   mean 5-min load while the part ran (32 cores; the part's own 8 jobs included). The timeout share is 3% (< 16), 7%
   (16-32), 13% (32-64) and 38% (>= 64). The load at a part's start says little: the 11-16 16Z parts started at load 7,
   and ran at 46-137 (`sar/ve-cloud-2.txt` 16:20-18:40Z), 97% timeouts. Table G controls for the mutant. Take the 208
   mutants tried more than once with at least one build timeout. On ve-cloud-2 they timed out on 43 of 43 tries at load
   < 32, 97 of 102 at 32-64 and 192 of 201 at >= 64. On ve-cloud-3 it was 192 of 202. On Actions (idle 4-core runners) it
   was 22 of 47. 163 of the 208 timed out on every try. The same mutants time out at low load too.
2. **The cache and setup: no.** Table D: parts after a cold setup (re-clone and Lean rebuild, 1558-2466 s, after the
   disk-low eviction; ve-cloud-2 has 67 GB free, under the 80 GB line) show 41% timeouts, and warm parts 13%. Cold
   setups cluster on 11-16, when the remaining plan is the heavy set. A setup builds the whole tree once, before any
   mutant. Each mutant's check then rebuilds its own cone in the scratch copy either way, so a cold setup costs part
   time, not per-mutant time.
3. **The mutant's own rebuild cone, measured against the 1800 s timeout: this is the binding cause.** The timeouts sit in
   a few heavy files (table E): VE/Compose/Dispatch.lean 167, VE/Cardinality/Wire.lean 119, VE/SpeechActs/Wire.lean 60,
   VE/EnglishGrammar/Advice.lean 47, VE/EnglishGrammar/SourceWords.lean 45 (657 in all). A check of one of them is
   bound by its chain of dependent modules, not by cores. On ve-cloud-2 (8 jobs on a 9-core cap) the 11-16 16Z part 2 ran
   25 checks in 40747 s, about 1630 s each (`part-2.json` steps). On VM1 with 5 cores for ONE job (trial 1, section 4) a
   check took 1476 s (2 checks, 2952 s). That is 4.5x the cores per job for 10% less time. On an idle Actions runner the
   same ids timed out at 1 core per job (Part 0b). The resume plan puts these ids first (the unallowed build-timeout
   UNKNOWNs and the NOT RUN ids of the same files), so the share rose from 7-15% (all mutants, 11-12..15) to 75%
   (11-16). That is the plan's tail, not a new fault.

**Fix.** TM_NIGHTLY_BUILD_TIMEOUT=3600, the bounded option (adv0725 item 2; tm-nightly.sh accepts 1800-3600 only), is
needed. With 1800 s, a check of the heavy set that takes ~1500-1650 s at best (measured above) crosses the timeout as
soon as its host is loaded at all. No setting of cores or hosts moved it under 1800 s on more than half of the tries. A
build past 3600 s stays UNKNOWN (resumable). No timeout becomes KILLED: trust_mutants returns TIMED_OUT -> UNKNOWN
(`tools/trust_mutants.py:1297`), tm-nightly.py `build_timeout` keeps it out of the verdicts, and this item changes
neither. The VM1 idle-core pool adds lanes (section 4). By itself it does not cure the timeouts.

## 2. Part 0b: "cloud result refused (verify exit 2)" is a second fault, exposed by the first (MEASURED)

Jobs tm-nightly-20261116T1607Z-p6 and -p7 (Actions run ids 43949400053 and 43950434727). Each result commit
(`~/code/ve-github-export` refs/cloud/<job>) has `gha.txt` "run_result=cancelled", `timings.tsv` with cache_restore,
python_env and branch_lake_build rc 0, and no tm.rc, DONE or trust-mutants.json. cloud-tm-verify.py exits 2 on that ("no
trust-mutants.json (DONE ?, failed steps none)", `svc-cloud-pull.log` 22:32:24-27Z). The runners were idle (nproc 4, load
1.6 at the start, `machine.txt`) and ran `--jobs 4`. Their trust_mutants log tails list 11 and 9 rows, 11 and 8 of them
"lake build did not finish in 1800 s". That is the same heavy set as Part 0.

So: the build timeouts are the same fault (the heavy cones). The lost results are a SECOND fault. job.json's cloud_args
carry the caller's `--budget 6300 --deadline 1794880865` (tm-nightly.sh part args; 1794880865 = 11-17 02:01Z).
cloud-tm-job.sh turns `--budget 6300` into `--deadline <job start + 6300>` (lines 103-106) and keeps the caller's
`--deadline` after it. argparse keeps the LAST `--deadline`, so trust_mutants ran to 02:01Z
(`tools/trust_mutants.py:2282` takes the min of `--deadline` and start + `--budget`, but only one `--deadline` survives).
GitHub's `timeout-minutes: 120` (ve-job.yml line 42) cancelled the job at ~22:25Z, before trust_mutants wrote its
partial record. With the job's own deadline (start + 6300 s = ~22:10Z) it would have written a partial record (exit 4) and
the judged rows would have come back. I did not touch the recovery probe or ACTIONS_SUSPENDED (no ACTIONS_SUSPENDED file
existed when I looked; cloud-pull.sh cleared it).

## 3. The build (staged `tm-nightly.sh.new-tmidle`)

`TM_NIGHTLY_POOLS=remote+idle` = the remote mode, plus up to `TM_IDLE_MAX` (1) local slots on VM1 (worktree `$W-l<i>`).

| Task line | Where (staged file) | Test (`tools-local/test_tm_drain_vm1_idle.py`) |
|---|---|---|
| a pool mode where parts also run locally on VM1 | `case $TM_NIGHTLY_POOLS in ... (remote+idle) rmt=1; idle=1`; local slots after the remote ones; `rslot` offers a free local slot first | `test_idle_part_runs_locally_same_args_in_a_capped_scope` |
| only while the 5-min load < nproc - reserve (env, default 8) | `igate`: `TM_IDLE_RESERVE` (8); at least `TM_IDLE_MIN` (4) whole cores; MemAvailable >= `TM_IDLE_MEM` + `TM_IDLE_MEM_SPARE` (24 + 8 GiB); flag `TM_IDLE.off` | `test_gate_boundaries` (19.90 local, 20.10 remote; the reserve and cores-per-job by env; memory; flag) |
| nice/ionice, own iso scope, memory cap | `lpart`: `systemd-run --user --scope --slice=ve-workers.slice -p CPUWeight=10 -p CPUQuota=<cores>00% -p MemoryMax=24G -p MemorySwapMax=0 --unit=ve-tmidle-<stamp>-p<k> nice -n 19 ionice -c 2 -n 7`, for the setup `lake build` and for trust_mutants | same test (scope args, niceness 19 seen by the stubs); `scope-smoke.log` (the real systemd-run: cpu.max 400000, weight 10, memory.max 24G, swap 0, nice 19, best-effort 7) |
| later parts wait or go remote when the load rises | the gate is re-read before every part; a closed gate sends the part to a free remote slot or waits (poll) | `test_load_rises_later_parts_go_remote_or_wait` |
| verdicts the same as a remote run: same command, same record format | the args after mac-pytest's `--` plus the part's `--only/--budget/--deadline` and `--json` (what cloud2-run.sh passes), `--jobs` from the cores; `"where": "vm1-idle"` written as cloud2-run.sh writes the host | same test: the remote and local args are equal once the per-part values are blanked; the record has `where` |
| a failed local setup loses nothing | setup rc != 0: no trust_mutants and no record; the part's ids stay NOT RUN and resume | `test_setup_failure_no_record_ids_resume` |
| remote-only mode unchanged | `remote` sets no idle slot | `test_remote_only_mode_never_local` (passes on live too) |

Choices I made, each the conservative option (not asked):
- A local part that is already running is not stopped when the load rises. Its scope has CPU weight 10, against 100 to
  1000 for every other job in ve-workers.slice (iso.sh), so gates and chains get the CPU first. Its quota stays at the
  cores lent at its start. Its `--budget`/`--deadline` and the outer `timeout` bound it. Killing it would throw away
  judged rows.
- No lean-prep.sh share restore in the local worktree. lean-prep refuses the nightlies (R3), so the local slot builds with
  plain `lake build`, as the remote hosts' setup does. The worktree persists, so only a new head pays the setup.
- At most one local part by default (`TM_IDLE_MAX` 1). `TM_IDLE.off` stops new local parts without a restart.
- `--jobs` = cores / `TM_IDLE_CORES_PER_JOB` (2), 1 to 8. I first set 4 cores a job. Trial 1 measured that more cores per
  job barely help (section 1, cause 3), so the staged default is 2.

## 4. Mutants/day and timeout share, before and after (MEASURED)

Before, from the records (`part0-tables.md` B and F): 11-16, 54 verdicts and 161 build timeouts (75%) on ve-cloud-2;
11-15, 466 and 84 (15%); 11-14, 501 and 105. Actions is suspended and ve-cloud-3 paused, so ve-cloud-2 is the only pool.

VM1's idle cores (`sar/vm1.txt`, 10-min samples 11-12..16, gate = >= 4 whole cores under 32 - 8 - load): the gate is
open 79%, 86%, 51%, 59% and 56% of each day, with 14.2, 12.9, 11.3, 10.6 and 10.8 cores on average when open.

After: two trial runs on VM1 of the STAGED script with `TM_NIGHTLY_POOLS=remote+idle` (`trial/run.sh`, `trial/run2.sh`).
Each ran in its own home (`TM_NIGHTLY_HOME`/`TEST_SKIP_DIR` under /tmp; resuming a copy of 20261116T0600Z.json, as the
live 1607Z run did), its own worktrees (`~/code/ve-tmidle-trial`, `-l1`) and a remote stub that takes no part (exit 4), so
nothing left VM1. The live records, the live service and the remote pools were not touched. Each local part ran the
heavy-first ids the live 1607Z part 1 ran on ve-cloud-2 (from M011).

| run | cores / --jobs | build timeout | setup | trust_mutants wall | verdicts | build timeouts | other UNKNOWN | judged (all rows but NOT RUN) per hour of trust_mutants |
|---|---|---|---|---|---|---|---|---|
| ve-cloud-2, 11-16 16Z part 1 (same ids, before) | 9 / 8 | 1800 | 2466 s | 6306 s | 0 | 19 | 4 | 2.3 (0 verdicts; plus 10.9 timeouts) |
| VM1 trial 1 (cores per job 4) | 5 / 1 | 1800 | 3292 s (first build at this head) | 4415 s | 1 | 0 | 1 | 1.6 (0.8 verdicts) |
| VM1 trial 2 (staged defaults) | 7 / 3 | 3600 (TM_NIGHTLY_BUILD_TIMEOUT) | 1 s (built at this head) | 6303 s | 7 | 0 | 2 | 5.1 (4.0 verdicts) |

Sources: `trial/trial1-part-1.json`, `trial/trial2-part-1.json` (trust_mutants' own records, `"where": "vm1-idle"`),
`trial/nightly-run-*.excerpt.log` (each row and the steps line), `trial/nightly.log` (the gate's line for each part:
"5-min load 18.69 < nproc 32 - reserve 8: 5 cores, --jobs 1" and "16.58 ... 7 cores, --jobs 3"), and for ve-cloud-2
`parts-20261116T1607Z/part-1.json`. Both trials stopped at their 6300 s budget (exit 4, partial), as a remote part does;
the load rose to 52 during trial 2, and the weight-10 scope yielded.

**Verdicts are the same as a remote run's** (each judged id against every earlier record of head 9ccbf3fd):
- M021, M031, M052 and M054 were SURVIVOR on ve-cloud-3 and are SURVIVOR on VM1, with the same "proofs it breaks" detail.
- M011, M015 and M068 were UNKNOWN on ve-cloud-2 (a Lean error in the mutant, not a timeout) and are the same UNKNOWN,
  word for word, on VM1.
- M012, M016, M017 and M069 timed out twice on ve-cloud-2 at 1800 s. They are now judged: M012 KILLED (trial 1, 1800 s,
  one job on 5 cores), and M016, M017, M069 SURVIVOR (trial 2, 3600 s). These are the build timeouts the fix turns into
  verdicts. No timeout became KILLED: M012 is KILLED because its build finished, with a located Lean error at
  lean/VE/Commands/Examples.lean:404.

**Before and after.** Before (records): 11-16, 54 verdicts and 90 judged a day, 75% build timeouts, all on ve-cloud-2.
On the same heavy-first ids, ve-cloud-2 judged 4 (all UNKNOWN) and timed out 19 in its 6306 s part. After (VM1 idle
cores, staged defaults, TM_NIGHTLY_BUILD_TIMEOUT 3600, MEASURED): 5.1 judged an hour with 0% build timeouts in one local
slot. Mutants/day from VM1 (DERIVED from two measurements, not a measured day): 5.1 an hour x the gate's open hours
(56% of 11-16 = 13.4 h) = ~70 judged a day on this heavy tail. That is about as many as ve-cloud-2 judged on 11-16 (90),
added on top of it. The light part of the plan judges faster (ve-cloud-2 did 37 an hour on 11-12 with 7% timeouts), so
~70 is the floor for this tail, not the rate for a fresh plan. I did not measure a full day on VM1. The first sweep after
the install is that measurement (`part0_measure.py` counts `"where": "vm1-idle"` as its own host).

## 5. Seeded bugs (shell; in a /tmp copy of the staged file, never the staged file; `seed_run.py`, `seeded-bugs.json`)

| id | bug | caught by |
|---|---|---|
| S1 | the reserve ignored | test_gate_boundaries, test_idle_part_runs_locally_same_args_in_a_capped_scope, test_load_rises_later_parts_go_remote_or_wait |
| S2 | the memory gate dropped | test_gate_boundaries |
| S3 | the local run drops the first trust_mutants arg (not a remote host's command) | test_idle_part_runs_locally_same_args_in_a_capped_scope, test_load_rises_later_parts_go_remote_or_wait |
| S4 | no nice/ionice | test_idle_part_runs_locally_same_args_in_a_capped_scope |
| S5 | no CPU weight or quota | test_gate_boundaries, test_idle_part_runs_locally_same_args_in_a_capped_scope |
| S6 | the gate read once (later parts local whatever the load) | test_load_rises_later_parts_go_remote_or_wait |
| S7 | a failed setup still runs trust_mutants | test_setup_failure_no_record_ids_resume |
| S8 | the record does not say where it ran | test_idle_part_runs_locally_same_args_in_a_capped_scope |

Run: `python3 -I seed_run.py <staged> tools-local/test_tm_drain_vm1_idle.py seeded-bugs.json`, 8 of 8 rc 1 (`seeds.log`).
All three languages of the VE repo: none changed, so no Lean, Python or Rust seed applies.

## 6. Pre-existing failures (not this item's)

`tools-local/test_tm_nightly_restart_main.py` `MacPytestRemoteOnly.test_remote_every_pool_refusing_no_vm_no_mac` and
`test_pools_absent_routes_as_before` fail the same way on the live files (`run-regression.log`, last block). Their fixture's
`--deadline` now trips mac-pytest.sh's later tm-shard-fallback-overwrite guard ("NOT starting the whole run: the caller's
--deadline ... leaves under 300 s"). They test mac-pytest.sh, which this item does not change.

## 7. Install read (for the DRI; I did not install or restart)

Safe window: when `test-skip/nightly.log` ends with "final coverage: not yet complete; next try ..." (today's sweep
started at 06:08Z with a 10 h budget, so after ~16:10Z) and no mac-pytest.sh runs in the svc-tm-nightly scope. A restart
during a sweep kills its in-flight parts (their ids stay unjudged and resume, but their work is lost).

    cd /home/seyran/code/manage-agents; S=$(date -u +%Y%m%dT%H%MZ)
    md5sum tm-nightly.sh tm-nightly.sh.new-tmidle   # base d4b1487b84b1e6eda462dba731a82e15, staged dbfbeac3721831abe9dc78fbd2473d7d (else re-stage)
    TMN_SH=$PWD/tm-nightly.sh.new-tmidle python3 -I tools-local/test_tm_drain_vm1_idle.py   # Ran 5, OK
    cp -p tm-nightly.sh tm-nightly.sh.bak-$S-tmidle && mv tm-nightly.sh.new-tmidle tm-nightly.sh
    python3 -I tools-local/test_tm_drain_vm1_idle.py   # Ran 5, OK on the installed file
    systemctl --user list-units 've-svc-tm-nightly-*' --no-legend   # today: ve-svc-tm-nightly-1794845271.scope (env TM_NIGHTLY_POOLS=remote)
    systemctl --user stop ve-svc-tm-nightly-1794845271.scope
    setsid nohup zsh iso.sh svc-tm-nightly 1G -- env TM_NIGHTLY_POOLS=remote+idle TM_NIGHTLY_BUILD_TIMEOUT=3600 zsh tm-nightly.sh >> svc-tm-nightly.log 2>&1 < /dev/null &

TM_NIGHTLY_BUILD_TIMEOUT=3600 is the recommended part of the restart (section 1: needed for the heavy set). It is the
bounded option of adv0725 item 2; tm-nightly.sh refuses any value outside 1800-3600. It applies to every sweep of that
service process. To take only the idle cores, drop `TM_NIGHTLY_BUILD_TIMEOUT=3600` from the last line.

The restart starts a final-coverage sweep at once, as the tm-nightly-complete restart did (that is intended: tonight's
idle cores). The first local part builds Lean once in `~/code/ve-tm-nightly-l1` (~55 min at 5 cores, measured), and later
parts at that head start at once. Stop new local parts without a restart: `touch TM_IDLE.off` (rm to resume). Undo:
`systemctl --user stop 've-tmidle-*'` (a running local part), then mv tm-nightly.sh.bak-$S-tmidle back and restart the
scope with `TM_NIGHTLY_POOLS=remote`, as above. A stop of the service scope does not stop a running local part, which
has its own scope: stop it with the same `systemctl --user stop 've-tmidle-*'`.

## Notes for the DRI

- Part 0b's second fault (cloud-tm-job.sh keeps the caller's `--deadline` after the one it makes from `--budget`, so an
  Actions part runs into GitHub's 120-min cancel and returns nothing) is not fixed here. It makes no verdict wrong:
  the ids come back NOT RUN and resume. But it loses each Actions part that carries the nightly's far deadline, and it
  is what suspended Actions on 11-16. A fix is to give trust_mutants the earlier of the two deadlines (cloud-tm-job.sh,
  lines 103-106). It is outside this item's files.
- Trial 2 judged three SURVIVORs that no live record has: M016 and M069 (VE/Closure/Syntax.lean:43
  `VE.Closure.Formula.WellFormed`, body-false) and M017 (VE/Closure/Syntax.lean:63 `VE.Closure.Formula.denote`,
  body-false). The class is K, trusted, at head 9ccbf3fd (`trial/trial2-part-1.json`). They are trial evidence, outside
  the live records. The live nightly will judge these ids itself and classify them once its build timeout lets them
  finish.
- The service's `vm_cpu_s` (cgcpu, the svc scope's CPU) does not count a local part's CPU, which runs in its own scope.
  The scope's own CPU is in `systemctl --user show ve-tmidle-<stamp>-p<k>.scope -p CPUUsageNSec` while it runs.
- The trials cost VM1 03:21-07:18Z of one weight-10 scope (5, then 7 cores at most), and two worktrees, since removed.
- `tm-nightly.py size` sizes a local part like a remote one (from the newest part records). The trial homes had no records,
  so their parts got 383 ids each; the live home gives ~31-36.

## Self-review against BUILDER-CHECKLIST

Spec re-read (task file `prompts/task-tm-drain-vm1-idle.txt`):
- "a pool mode (e.g. TM_NIGHTLY_POOLS=remote+idle) where one or more parts also run locally on VM1" (line 8): mode
  `remote+idle`, `TM_IDLE_MAX` local slots (1 by default).
- "while its 5-min load stays below nproc minus a reserve kept for gates and chains (env, default 8 cores)": `igate`
  reads field 2 of /proc/loadavg; `TM_IDLE_RESERVE` 8.
- "under nice/ionice in its own iso scope with a memory cap": the scope sits in ve-workers.slice, as iso.sh's scopes
  do, with MemoryMax and no swap, under nice 19 and ionice -c 2 -n 7. I call systemd-run directly, not iso.sh, because
  iso.sh has no way to set the low CPU weight or the quota.
- "later parts wait or go remote when the load rises": `rslot` re-reads the gate for every part.
- "Verdicts must stay the same as a remote run (same trust_mutants command, same record format)": the same args and the
  record trust_mutants writes, plus `where` (section 3); the same verdicts on 7 ids already judged remotely (section 4).
- "Tests fail on the live files and pass on the staged ones": `run-live.log`, `run-staged.log` (the regression test
  passes on both, said above).
- "Stage as .new-tmidle and send an install read to dri ... Do not restart svc-tm-nightly yourself": staged; the
  install read was sent; no restart.
- "Report mutants/day before and after (MEASURED from the records)": section 4. The after rate is measured, and the per
  day figure is derived and labelled so.
- Part 0's list (per host and per hour; timeouts vs verdicts; load at the start; setup; cache; timeout value): tables
  A-G. "No timeout ever becomes KILLED": section 1 Fix and section 4.
- Part 0b ("same fault or a second one, with the evidence"; do not touch the probe or ACTIONS_SUSPENDED): section 2.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relayed Lean answer and no VE code changed.
2. Every deliverable built, no rule broken: PASS. Section 3's table (each line with its test), section 1 (Part 0),
   section 2 (Part 0b), section 4 (before/after) and section 7 (install read, sent with msg.sh dri); no restart done.
3. Tests and gates can fail: PASS. `run-live.log` (4 of the 5 new tests fail on the live script, 10 failures with
   subtests); `seeded-bugs.json` (8 of 8 caught).
4. Python, Lean and Rust agree: N.A. No VE product code changed.
5. R8 binding: N.A. No binding.
6. Gate evidence matches the final HEAD: N.A. I claim no gate result. The chain gates the final HEAD, and this branch
   adds docs only.
7. No unsigned item: PASS. No DELTA rows and no reserved signature. Control-plane tooling, with no trusted line or
   verdict rule changed.
8. Every user-visible change in DELTA: N.A. No VE user-visible change.
9. Test selection still finds the tests: PASS. The one selected run on the final HEAD (`selected-run.log`).
10. Lean statements: N.A. No Lean.
11. Budgets and deadlines fail closed: PASS. A local part keeps the part's `--budget`/`--deadline`
    (`test_idle_part_runs_locally_same_args_in_a_capped_scope`, equal args). A failed setup leaves no record
    (`test_setup_failure_no_record_ids_resume`). No time left after the setup gives rc 4 with no record. A build timeout
    stays UNKNOWN (`tools/trust_mutants.py:1297`, unchanged).
12. No CPU or memory regression: PASS. The local scope has CPUWeight 10, CPUQuota at the lent cores and MemoryMax 24G,
    with no swap. The memory gate (`test_gate_boundaries`, 31 GiB refused) and `scope-smoke.log` (the real
    cgroup values) back this. Trial 2's scope yielded at load 52.
13. Test-removed trailer: N.A. No test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. `test_gate_boundaries` opens the gate at 19.90 and closes it
    at 20.10, refuses 31 GiB and accepts 64, and honours the flag. `test_remote_only_mode_never_local` checks the
    unchanged side. Each claim names its file or command. The spec re-read is above.
15. No overclaim; no silent cut; every new check can fail; limits charged before work: PASS. The universal words I
    checked: "no timeout became KILLED" (trust_mutants:1297 and the trial rows); "the same verdicts" (7 ids compared,
    section 4); "nothing left VM1" (the trial's remote stub `trial/noremote.py` exits 4). The per-day after figure is
    labelled DERIVED. No deliverable was cut. Each gate check has a seed (S1, S2, S5, S6). The gate is read before a
    part starts.
