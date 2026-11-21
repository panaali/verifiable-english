# ESTIMATE: wall time of one complete fresh trust-mutant sweep at main, remote pools only (tm-t1-fresh-sweep-1120, 2026-11-20)

Row tm-t1-fresh-sweep-1120 (orchestrator ruling 080332Z on ADV-3; reviews/dri-decisions-20261120-adv0757.md item 3). Read only.

Saved copy (repo evidence): written in manage-agents/reviews/tm-t1-fresh-sweep-1120/ at 08:21Z and copied here unchanged apart from
this paragraph. The relative paths below (test-skip/, reviews/, cloud-jobs/) are in manage-agents. The plan file is not copied
(366 KB); its sha256 is 1b7d900ecf6da8868eb4e02fac67e2f9441448344705a7dca23158577ccf5703. Outcome: no sweep was launched;
the acting DRI dropped the row at 08:25Z (reviews/dri-decisions-20261120-preflight-plants.md item 5): selection stays
unconfirmed and the gates keep the full suite.
Method: the train-legs-time-1120 method (reviews/train-legs-time-1120/REPORT.md). Every MEASURED cell comes from a record or log line named
here, and `estimate_calc.py` in this folder recomputes it (`python3 -I estimate_calc.py <manage-agents dir>`; output saved as `estimate_calc.out`; named calc.py and calc.out in manage-agents). Cells marked ESTIMATE are not measured.

**Result: 5.8-14.2 days of back-to-back sweeping. With today's pools (ve-cloud-3 unreachable): 8.6-14.2 days. The upper estimate is OVER 5 days, so the sweep is NOT started (STEP 2).**

## Sources
- test-skip/nightly/parts-<stamp>/part-<k>.json: one per finished part. It gives `where`, `seconds` (part wall), `jobs` and the status and detail of each row.
  Window: the sweeps from 20261113T0600Z to 20261120T0745Z (the last 7 days). Parts with no `where` field are GitHub Actions parts
  (tm-shard; e.g. nightly-run-20261114T0600Z.log:84-86, record part_rows `where: cloud`).
- test-skip/nightly.jsonl: per-record `part_rows`, `steps_wall` and `counts`.
- test-skip/nightly.log: each sweep's start line (`pools remote`) and end line (`all N part(s) returned`). These give the sweep wall.
- plan-main-09bea0972d.json (this folder): trust_mutants `plan()` at main 09bea0972d, base 039d3dd51 (the fresh base), trusted classes.
  Made with reviews/tm-build-timeout-1120/evidence/planlist.py.
- Heavy files: reviews/tm-build-timeout-1120/evidence/heavy20.json (15 files with a build timeout on >= 20% of tries).
- Pool state now (08:20Z): `ssh ve-cloud-3`: connection timed out (unreachable, as at 08:09Z, adv0757 item 3). ve-cloud-2: up, 32 cpus, load 1.9.
  cloud-jobs/ACTIONS_MISMATCH: absent (resolved 11-20T03:09Z). It was open from 11-17T17:30Z, and while it was open Actions took no tm parts.

## 1. Ids at current main (MEASURED)

| head | base | mutants | heavy | light |
|---|---|---|---|---|
| main 09bea0972d (contains 17581425: `git merge-base --is-ancestor` = 0) | 039d3dd51 | **8,719** | 777 | 7,942 |

These are the same counts as tm-build-timeout-1120's plan at 727d1d210. The merges since then changed no planned mutant.

## 2. Throughput per pool (MEASURED, 7 days)

Judged = KILLED + SURVIVOR + INVALID (a verdict that needs no new try). bto = UNKNOWN "lake build did not finish" (build timeout).

| pool | parts | part-hours | judged | bto | other UNKNOWN | judged per part-hour | bto rate of tries | jobs |
|---|---|---|---|---|---|---|---|---|
| ve-cloud-2 | 77 | 109.9 | 1,667 | 715 | 174 | 15.2 (light-mostly days 11-13..15: 24.9-38.5; heavy-mostly 11-16..19: 2.4-8.4) | 0.28 (11-13..15: 0.07-0.15; 11-16..19: 0.46-0.73) | 8 |
| ve-cloud-3 | 13 | 16.1 | 418 | 87 | 68 | 26.0 | 0.15 | 8 (last part 11-13; 0 parts since; unreachable now) |
| GitHub Actions | 5 | 5.9 | 99 | 35 | 10 | 16.8 (11-14, 32 jobs: 30.2; 11-16/17, 4 jobs: 5.6-7.6) | 0.24 | 32 / 4 |
| vm1-idle (excluded by this task) | 3 | 4.6 | 2 | 0 | 0 | 0.4 | - | 2/6 |

Per sweep, all remote pools together (judged per hour of sweep wall; each `--once` sweep runs about 9.8 h of its 36,000-s budget):

| sweep | wall h | judged | judged/h | pools that took parts |
|---|---|---|---|---|
| 20261113T0600Z | 9.83 | 899 | **91.4** | ve-cloud-2 + ve-cloud-3 |
| 20261114T0600Z | 9.77 | 501 | **51.3** | ve-cloud-2 + Actions (2 parts) |
| 20261115T0600Z | 9.83 | 466 | **47.4** | ve-cloud-2 |
| 20261116T0600Z | 9.83 | 38 | 3.9 | ve-cloud-2 (heavy ids) |
| 20261117T0600Z | 9.93 | 137 | 13.8 | ve-cloud-2 + Actions (heavy ids) |
| 20261119T0727Z | 9.83 | 58 | 5.9 | ve-cloud-2 (heavy ids) |

**Build-timeout rate (tm-build-timeout-1120, installed 07:46Z):** 7-23% of tries on the light-mostly days 11-13..15 (all pools), and 46-73% on ve-cloud-2 on the heavy-mostly days 11-16..19 (MEASURED, above).
The heavy-file tries at 8 jobs time out 460 of 477 times (96%, tm-build-timeout-1120 REPORT sec. 1, MEASURED).
The installed fix (heavy ids last, at `--jobs 2`) acts only on a **resumed** record. "A sweep with no resumed record is unchanged"
(tm-nightly.sh, test_fresh_sweep_unchanged). So the first fresh sweep tries all 777 heavy ids at 8 jobs, mixed with the light ones, and
they then become build-timeout UNKNOWN. Only the resumed sweeps after it get the heavy-last parts.

## 3. Expected wall time of one complete fresh sweep (remote pools only, 3 parts at once, sweeps back to back, 24 h a day)

| part | basis | hours |
|---|---|---|
| light, 7,942 ids | MEASURED sweep rates of light-mostly sweeps: 91.4/h (cloud-2 + cloud-3), 51.3/h (cloud-2 + Actions), 47.4/h (cloud-2 only) | 86.9 / 154.8 / 167.6 |
| heavy, 777 ids at `--jobs 2`, 3 slots | ESTIMATE 1.5-5 judged per part-hour (tm-build-timeout-1120 sec. 4: VM1 trial 5.1/h at 7 cores, MEASURED there; the remote pools were never measured at 2 jobs) | 51.8-172.7 |
| first try of the heavy ids at 8 jobs | inside the light rates: the light-mostly sweeps already spent their bto tries | 0 extra (optimistic) |

| pools | total | days |
|---|---|---|
| ve-cloud-2 + ve-cloud-3 (cloud-3 unreachable today: the lower bound needs it back) | 138.7-259.6 h | **5.8-10.8** |
| ve-cloud-2 + Actions (today) | 206.6-327.5 h | **8.6-13.6** |
| ve-cloud-2 only (today, Actions idle) | 219.4-340.3 h | **9.1-14.2** |

**Range: 5.8-14.2 days. With today's reachable pools: 8.6-14.2 days.** Basis: the light part is MEASURED; the heavy part is an ESTIMATE
(an allocated rate, not measured on a remote pool). Not counted, so the range is low, not high:
- One `--once` launch stops after its 36,000-s budget. It judges 474-914 of the 8,719 ids (5-10%, MEASURED rates x 10 h).
  A complete fresh sweep is therefore about 14-35 back-to-back launches (138.7-340.3 h / 9.8 h) (fresh, then resumes). The loop is not running
  ("final coverage not complete 7 days after the end: exit", nightly.log:970), so each launch has its own relaunch gap.
- `resume` refuses a record 4 days old or more (tm-nightly.py), so a gap of 4 days restarts from fresh.
- Non-timeout UNKNOWN: 174 on ve-cloud-2 and 68 on ve-cloud-3 in 7 days. Each one needs a disposition before the record is complete
  (tm-nightly-unknown-disposition-3 is open for 5 such ids at 9ccbf3fdf).
- The 96% heavy timeout rate at 8 jobs: a heavy id whose last try times out leaves the record incomplete.

Cross-check: tm-build-timeout-1120 sec. 4 gives P1 (resume at 9ccbf3fdf, then main) 4-10 days back to back with remote+idle pools.
It says "P2 (a fresh sweep of main, 8,719 mutants) is about 2x P1", which is 8-20 days. That agrees with 8.6-14.2 days without the idle pool.

## 4. Decision (STEP 2)

Upper estimate 14.2 days > 5 days: **not started.** No launch, no process touched.
Row tm-t1-fresh-sweep-1120 is set blocked, `--blocked-by tm-build-timeout-1120` (orchestrator ruling 080332Z).
What would bring it under 5 days (for the decider, not decided here):
(a) the build-timeout fix also orders a fresh sweep's heavy ids last at `--jobs 2`;
(b) ve-cloud-3 back (light about 87 h instead of 155-168 h);
(c) Actions taking a full share of the parts (only 5 parts in 7 days).
Even with (a)+(b), the lower bound is 5.8 days.
