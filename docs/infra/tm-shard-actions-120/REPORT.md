INSTALL WAITS FOR DECIDER READ

# tm-shard-actions-120: Actions parts sized from run records, so each one fits under the 120-min limit (staged as tm-shard.sh.new-tsa)

Row tm-shard-actions-120 (guard trust-mutant-nightly; DRI decider 11-17 10:31Z; task: prompts/task-tm-shard-actions-120.txt).
The fix is staged as `/home/seyran/code/manage-agents/tm-shard.sh.new-tsa` (`zsh -n` clean) and has not been moved into place.
The tests are in `/home/seyran/code/manage-agents/tools-local/test_tm_shard_actions_120.py`.
No DELTA rows (no Lean or trust-base change). No VE product code changed: this branch carries only this evidence directory.

## What failed at 0600Z (measured; dri-actions-susp-1117.final.md and the export records)
- tm-shard sized p3 (60 mutants, 2 parts) and p4 (30, unsharded) at SETUP 500 s and the first-sweep floor of 80 slot-s per mutant,
  giving ~1,700 s a part (cloud-jobs.log 06:12:19Z and 08:20:21Z lines).
- The records show the real costs. `branch_lake_build` took 1,703.4 s on p4 and 1,745.6 s on p5
  (`git show refs/cloud/<job>:cloud-results/<job>/timings.tsv` in ~/code/ve-github-export). In p4's log tail, 8 of the 12
  printed verdicts were builds stopped at the 1,800 s `--build-timeout`.
- p4 went **unsharded**, and on that path tm-shard added no `--budget`.
- The caller (tm-nightly.sh) passed `--budget 6300` together with `--deadline 1794931135` (15:58Z). The job script the 0600Z
  jobs shipped was the pre-tm-actions-deadline `cloud-tm-job.sh`: `grep -c tm-actions-deadline
  cloud-jobs/tm-nightly-20261117T0600Z-p4-9ccbf3fd/job-script.sh` = 0. In that version the far deadline won, so no partial
  record was written before the cancel.

## The fix (tm-shard.sh header entry "2026-11-17 tm-shard-actions-120"; diff: staged-changes.diff, +119/-4)
This applies only when the caller's pool is actions and TM-SPM-OFF is absent. Other pools behave exactly as before (test 4).
1. **Records.** tm-shard reads the export repo's `refs/cloud/*`, newest first, keeping runs that have `gha.txt` with `run_id=`
   and a `timings.tsv` with a `branch_lake_build` row. It takes the last 20 such runs within 168 h, using one
   `git cat-file --batch`. That read took 0.86 s and 166 MB peak on the real export (`/usr/bin/time` above).
   - SETUP is the larger of 500 and the **worst** setup of those 20 runs (cache_restore + python_env + branch_lake_build). The
     size target moves up by the same amount, so the mutant phase keeps the room the constants gave it.
   - SPM is the larger of the existing reading and the **p90** of the per-mutant readings.
   - A run with a record gives steps.wall.mutants × jobs / (judged + abandoned).
   - A cancelled run gives tm-spm.py's L151 bound: (7,200 − 300 − setup) × jobs / the number of mutants it had to run.
   - The log tail cannot count judged mutants, because trust_mutants prints KILLED lines only at its end
     (tools/trust_mutants.py:2359-2360, 2435-2436).
2. **Part line.** The line is LIMIT 7,200 (gha/ve-job.yml:32 `timeout-minutes: 120`) − PRE 300 (checkout and tools before
   job.sh; measured 66 s for p4: run job start 08:20:37Z, machine.txt 08:21:43Z) − POST 600 (partial record, `out` upload,
   slack) − HEADROOM 1,200 = **5,100 s** from job.sh's start.
   - The line becomes the default of TM_SHARD_ACTIONS_HARD (the reserve/NMAX waiver line) and TM_SHARD_ACTIONS_CANCEL (the
     not-sent line). An explicit env value still wins.
   - A sweep that cannot be cut under the line is not sent on actions. It goes through TM_FIT_ROOM's offers or the VM path.
3. **Budget.** While TM_PART_DEADLINE exists, every Actions part gets `--budget 6300` (LIMIT − PRE − POST). This now includes:
   - the unsharded part (`plain`);
   - parts where the caller also passed its own `--budget`/`--deadline`.
   A TM_PART_BUDGET over LIMIT − PRE is cut to LIMIT − PRE. A malformed one is replaced by 6,300, so a part never runs with no
   budget.

**What the sizing assumes:** tm-actions-deadline is installed. `cloud-tm-job.sh` was modified 2026-11-17 12:35; its header and
lines 45-55 pass trust_mutants the EARLIEST of every `--deadline` and `--budget`. cloud-dispatch.sh:187 embeds
`$M/cloud-tm-job.sh` into each new job. trust_mutants kills its Lake runs at that deadline (tools/trust_mutants.py:142-148,
1283-1296), so a part stops at job.sh start + 6,300 s, which leaves about 900 s of the job for the record and the upload.
Without tm-actions-deadline, a caller's far `--deadline` would beat the budget again.

## Replay of the real 0600Z dispatches against the real records (replay-0600Z.log)
| | live tm-shard.sh | staged |
|---|---|---|
| p3, 60 mutants, records as of 06:12Z | 2 parts, ~1,700 s each, budget 6300 (both were cancelled) | not sent on actions: 12 parts would still be ~5,201 s > 5,100 (records: setup worst 1,770 s, p90 2,265 slot-s) |
| p4, 30 mutants, records as of 08:20Z | unsharded, ~1,700 s, **no budget** (cancelled) | 8 parts, ~4,635 s each, `--budget 6300` |

The replay uses room 40 and busy 0. At 06:12Z the real room was 22, which still allows the 12-part hard NMAX, so the outcome is
the same.

## Tests (tools-local/test_tm_shard_actions_120.py; `TSH=<copy>` tests another file)
Live results are in run-live.log (`python3 -I tools-local/test_tm_shard_actions_120.py --skip-5`, exit 1, 12 FAIL). Staged results
are in run-staged.log (`TSH=$M/tm-shard.sh.new-tsa python3 -I tools-local/test_tm_shard_actions_120.py`, exit 0, `PASS: 0 failed`).
| Case | live | staged |
|---|---|---|
| (1) 0600Z fixture (p4 cancelled with build 1,703.4 s; heavy parts at 1,800 slot-s; light ones): p4 30 and p3 60 go as parts whose predicted total (PRE + worst setup + CONTROL + mutants × 1,800/4 + POST) is < 6,000; the log names the records and the line | FAIL (16,720 s) | ok (5,020 / 5,920 s) |
| (1) 84 mutants: 12 parts would be ~5,470 s, so not sent (exit 3) and never a part over the line | FAIL (3 parts, 15,820 s) | ok |
| (2) records p90 300 > floor 80: sized at 300; reading 50 < floor: the floor 80, no records note | FAIL | ok |
| (3) --budget ≤ 6,300 on sharded parts, beside a caller's `--budget 9000` and far `--deadline`, on the unsharded part; 99999 cut to 6,900; malformed gives 6,300; TM_PART_DEADLINE off gives none | FAIL ×4 (the flag-off check passes on both) | ok |
| (4) claude-cloud ×3, codex ×2, claude: exit code, dispatch calls and log lines equal to the live script's, with the same records present | ok (trivially) | ok |
| (5) tools-local/test_tm_shard_fallback_overwrite.py with TMS = the file under test | ok | ok |

The Mac/VM part runs do not go through tm-shard dispatch. mac-pytest.sh tmparts builds their args from the caller's args
(mac-pytest.sh:385-395: pa/pn), so none of these changes reach them.

## Seeded bugs (seed_run.py; seeds.log; seeded-bugs.json)
Each bug was planted in a temporary copy of `/home/seyran/code/manage-agents/tm-shard.sh.new-tsa` (zsh with embedded Python),
then the tests were run with TSH set to that copy. Every bug was caught (test rc 1):
- B1: SETUP uses the best setup instead of the worst. 4 checks fail (p3 predicted 6,820 s, among others).
- B2: the records' p90 is never used. 5 checks fail (p4 16,720 s, among others).
- B3: the unsharded part gets no budget. "unsharded (5 mutants fit one part) …" fails.
- B4: no cut over LIMIT − PRE. "TM_PART_BUDGET 99999 is cut …" fails.
- B5: HARD/CANCEL keep 5,400/6,600. "84 mutants: not sent …" fails.
- B6: a malformed or unset TM_PART_BUDGET drops the budget. 4 checks fail.

## Old harnesses against the staged file (harness-regression.txt)
- `test-harness/tmshard/test-tmshard.zsh` on the live file: 148 passed, 1 failed. That failure ("pc-3's case") is **pre-existing**.
- The same harness on the staged file with records isolated (`TM_SHARD_RECORDS=/nonexistent`): 144 passed, 5 failed. Those 5 are
  pc-3 plus 4 **intended** changes:
  - "own heavy reading over the hard limit … 5 parts ~5,120 s": now 6 parts at ~4,418 s, under the 5,100 line;
  - "the hard NMAX caps a waiver at cap 8 (2000 mutants)": 8 parts at ~5,800 s are now not sent;
  - "P4 the caller's own --budget: no second one" and "P5 … --deadline: no --budget": tm-shard's budget is now added beside
    the caller's.
- Without that env, the harness reads the live export records: 106 passed, 42 failed.
- `test_tm_actions_first.py` on the staged file: PASS, 20 ok.
- `test_tm_shard_fallback_overwrite.py` on the staged file: exit 0.

## Answers to the task's questions
- **Why the seed-pinned cache rebuilds ~1,424 jobs.** The cause is outside tm-shard.sh; see the finding below.
- **ve-job.yml timeout.** Not raised, and I don't recommend raising it now. With the part line, a sized part is predicted to
  finish under 120 min, and the budget turns any overrun into a partial record. I did not measure the Actions-minutes cost of a
  raise. A raise would need that measurement first: each cancelled part already holds a runner for 120 min.

## FINDING (for a separate row; outside tm-shard.sh, not fixed here)
**The seed-pinned cache restore rebuilds 1,424 jobs because the cache asset comes from a Lean tree 99 files away.**
- The nightly tests the fixed commit 9ccbf3fdf (2026-11-12; lean tree 4acf8387e957) against base 039d3dd5 (2026-11-08).
- `~/.cache/ve-cloud-cache/manifest.json` keeps only 5 assets (lean-cache-publish.sh). All of them are from main on Nov 16-17
  (trees ec87fe990deb, 71a76c375f58, f73cacbe6bd8, 547a9924ac50, d820b947a44d).
- None matches the job's tree, its base's tree, or a near ancestor of the base, so cloud-dispatch.sh:158-166 falls through to
  "newest". That restored lean-build-71a76c375f58 (main 47e81ec57a46) for p4 and f73cacbe6bd8 for p3.
- `git diff --stat 47e81ec57a46 9ccbf3fdf -- lean` gives 99 files changed, +1,641 / −14,176. ve-cache.sh:177 labels this
  "seed-pinned", so a 1,000-1,770 s `branch_lake_build` follows on every part.
- The fix belongs in cloud-dispatch.sh's asset pick, lean-cache-publish.sh's keep set, or a pinned asset for the nightly's commit.
- GUESS (unverified): the 1,800 s mutant builds come from the mutated files' reverse closures (Compose/Dispatch.lean,
  EnglishGrammar/Advice.lean), not from the cache.

## Install (the decider runs these; I did not)
```
cd /home/seyran/code/manage-agents
cp -p tm-shard.sh tm-shard.sh.bak-20261117tsa
mv tm-shard.sh.new-tsa tm-shard.sh
python3 -I tools-local/test_tm_shard_actions_120.py      # TSH defaults to the installed file: expect "PASS: 0 failed"
```
No flag to touch: TM_PART_DEADLINE and TM_SHARD already exist. TM-SPM-OFF (absent) vetoes rules (1) and (2), as it vetoes tm-spm.

## ACTIONS_SUSPENDED after the install (the decider decides; I did not touch the flag)
**Safe for the tm-shard-dispatched trust_mutants parts, provided the tm-actions-deadline `cloud-tm-job.sh` is the one shipped
(it is: cloud-dispatch.sh embeds the live file).** Each part is then sized under the 5,100 s line from the worst measured setup
and the p90 per-mutant time, and stops itself at +6,300 s with a partial record. Sweeps that cannot fit (the p3 shape) are not
sent on actions.

Not covered by this item:
- other Actions job kinds;
- the 05:32Z verdict-sample MISMATCH (ACTIONS_POOL/ACTIONS_MISMATCH, a separate flag);
- the cache finding above, which keeps every part's setup at ~1,000-1,770 s until it is fixed.

`ls $M/ACTIONS_SUSPENDED` found no file when I read it at 14:41Z.

SIZE: 119 product, 235 tests, 31 other hand-written lines (seed_run.py; plus this REPORT)

## Notes for the DRI
- test-tmshard.zsh needs updating after the install, and it is outside this row's paths:
  - `export TM_SHARD_RECORDS=/nonexistent` beside its other isolating exports (line 7);
  - the 4 expectations listed above (5-part → 6-part, 8 parts not sent, P4/P5 now expect tm-shard's budget beside the
    caller's).
- When an Actions refusal is offered on to claude-cloud or Codex (TM_FIT_ROOM), the offer's log line now also carries Actions'
  "part line … records: …" clause. claude-cloud parts there are sized at the SPM Actions used, which can now be the records' p90.
  That is the existing fit-room design.
- CONTROL stays 600 s. The records show 13-27 s (steps.wall plan..control_probes), so the 600 s acts as extra headroom.
- The p90 at 06:12Z (2,265) was dominated by L151 bounds of cancelled runs. A bound can overstate when slots sat idle at the
  cancel. It is the conservative side: such sweeps go elsewhere rather than being cancelled. At ~14:35Z the p90 was 1,376.

## Self-review against BUILDER-CHECKLIST
1. N.A.: no Lean answer or relay.
2. PASS: all 3 fix bullets, the cache finding and both tests files are delivered (run-staged.log `PASS: 0 failed`; tests 1-5).
3. PASS: tests fail on the live file (run-live.log, 12 FAIL), and 6 seeded bugs are caught (seeds.log).
4. N.A.: no Python/Lean/Rust product code; for zsh the comparison against the live file is case (4).
5. N.A.: no R8 binding.
6. PASS: the evidence is from the final staged file (sha256.txt matches run-staged.log's TSH). The VE gate runs on this
   docs-only HEAD.
7. PASS: no unsigned item; no DELTA row needed (no Lean or trust-base change).
8. N.A.: no user-visible VE change.
9. N.A.: no VE code changed; tools-local tests are run by name.
10. N.A.: no Lean.
11. PASS: the budget fails closed. A malformed TM_PART_BUDGET gives 6,300 and an oversized one is cut (case 3; seeds B4, B6).
    The flag-off path is unchanged.
12. PASS: the records read is 0.86 s / 166 MB once per Actions dispatch (`/usr/bin/time`). No VE runtime change.
13. N.A.: no test removed or renamed.
14. PASS: each rule is tested in both directions (300 used / 50 not; sent and fits / not sent; budget on / flag off; other pools
    unchanged). Spec re-read: task file bullets 1-4 and tests (1)-(5) against prompts/task-tm-shard-actions-120.txt.
15. PASS:
    - no overclaim: "every Actions part" is cases 3a-3c and 3f; "exactly as before" is case 4;
    - no silent cut: all deliverables are built;
    - every new check can fail: B1-B6;
    - limits are charged before work: N.A.
