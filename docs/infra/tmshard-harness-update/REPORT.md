# tmshard-harness-update: REPORT

- Status: DONE. Harness installed in manage-agents (backup `test-tmshard.zsh.bak-tmshard-harness-update`); evidence on branch
  infra/tmshard-harness-update. No DRI signature needed (test-only; no DELTA rows; no Lean, Python or Rust product code).
- Changed: `test-harness/tmshard/test-tmshard.zsh`: 1 isolation export + exactly the 4 intended expectations of
  tm-shard-actions-120 (decision reviews/dri-decisions-20261117-tm-shard-actions-120.md item 3).
- Before (live records leak in): 106 passed, 42 failed. After: **149 passed, 0 failed**.
- pc-3: **not failing** in any run here (before, isolated, after); its expectation is untouched. See "pc-3".
- Open: none filed. One possible 5th change (live TM_FIT_ROOM / Codex state leaks into two cases) is listed, not made.

SIZE: 0 product, 5 tests (1 line added, 4 lines changed in test-tmshard.zsh), ~150 other hand-written lines (this report,
seeded-bugs.json).

## Where the change lives

The harness is in the ops directory, `/home/seyran/code/manage-agents/test-harness/tmshard/test-tmshard.zsh` (gitignored
there), so as in the earlier harness-only infra item tmcarry-fixture-main it is edited in place with a backup, and this branch
carries the evidence:

| File | What |
|---|---|
| `harness.diff` | `diff -u` backup -> installed harness |
| `test-tmshard.zsh` | the installed harness, byte-identical (sha256 in `sha256.txt`) |
| `sha256.txt` | live tm-shard.sh (25d77274..., the file the decision installed; unchanged), the backup, the installed harness |
| `runs/before.log` | the harness as it was, live files (`TMS_SUFFIX=`) |
| `runs/isolated.log` | step 1 only (the export), before the expectation changes |
| `runs/after.log` | the installed harness, live files |
| `seeds.diff`, `seeded-bugs.json`, `runs/seed{A,B,C}.log` | the seeded bugs |

Every run: `TMS_SUFFIX= zsh test-tmshard.zsh` (the live tm-shard.sh, cloud-pull.sh, cloud-overflow.sh; no `.new-tmshard`
files exist). Seed runs add `TMS_TS=<seeded copy of tm-shard.sh>`.

## Before / after

| Run | Passed | Failed | Failing cases |
|---|---|---|---|
| before (no isolation) | 106 | 42 | 42 cases that read the live export records (runs/before.log); the 4 intended among them |
| isolated (step 1 only) | 145 | 4 | exactly the 4 intended cases below |
| after (installed) | 149 | 0 | none |

The tm-shard-actions-120 REPORT predicted these numbers: 106/42 without the env, and with it 144/5 = pc-3 plus the same 4.

## The changes, each confirmed against the merged code (tm-shard.sh sha256 25d77274...)

1. Isolation (line 9): `export TM_SHARD_RECORDS=/nonexistent` beside the CCLOUD_POOL_FLAG and TM_CODEX_VMLOAD_FLAG exports.
   tm-shard.sh:423 `arecs()` reads `${TM_SHARD_RECORDS:-${TM_SPM_EXPORT:-~/code/ve-github-export}}`; header (1): "No export
   repo or no run: the constants and readings as before". The env wins over TM_SPM_EXPORT, so no live record is read.
2. "own heavy reading over the hard limit (400 x 216)": 5 parts ~5,120 s -> **6 parts ~4,418 s**. tm-shard.sh:513-514
   default TM_SHARD_ACTIONS_HARD to the part line 7,200 - 300 - 600 - 1,200 = 5,100 s; 5,120 > 5,100, so the waiver loop
   (line 375) goes on to 6 parts. Output: `-> 6 parts (~4418 s each; ... reserve and NMAX waived to 6 parts: ~5100 s per part
   at most`. The case now also counts 6 dispatches.
3. "the hard NMAX caps a waiver at cap 8 (2000 mutants)": 8 parts -> **not sent on actions**. Lines 513-514 also default
   TM_SHARD_ACTIONS_CANCEL to 5,100 (was 6,600); 8 parts at ~5,800 s exceed it. Output: `it: 2000 mutants need ~5800 s per
   part in 8 parts (...) on actions, which cancels a job at 120 min: not sent`. The case checks that line and that no job.json
   in the scratch jobs dir has pool actions (so it holds whatever the TM_FIT_ROOM offer does next; see the 5th change below).
4. "P4 the caller's own --budget": no second one -> **`--budget 99 --budget 6300 --shard k/3` on each of the 3 parts**, exit 0.
5. "P5 the caller's own --deadline": no --budget -> **`--deadline 99 --budget 6300 --shard k/3` on each of the 3 parts**, exit 0.
   P4/P5: tm-shard.sh:539-541 and header (3): every Actions part gets `--budget TM_PART_BUDGET` "also beside a caller's own
   --budget/--deadline: cloud-tm-job.sh ... passes trust_mutants the EARLIEST of them". Both use the harness's existing
   `budgeted` helper (the exact dispatch argument order).

The case names were updated to say what they now expect and cite tm-shard-actions-120.

## pc-3

Named as required: "pc-3's case: 6+1 runners busy, 253 first-sweep mutants ~6,160 s: ... not sent". The task and the
tm-shard-actions-120 REPORT list it as a pre-existing failure. Here it **passed in all three runs** (before, isolated, after)
on the installed tm-shard.sh. I did not edit it. Its check `[ ! -e $S/drec ]` runs through the live TM_FIT_ROOM offer, which
reads live pool state (next section), so I would expect its result to depend on that state; I did not test this.

## Possible 5th change: listed, not made

The first-sweep section (pc-3, the cap-8 case and the other "not sent" cases) reaches tm-shard.sh:524, which reads the
**live** `${TM_FIT_ROOM_FLAG:-$M/TM_FIT_ROOM}` (present now). The offer then calls cloud-overflow.sh, which reads live
Codex/claude-cloud state (runs/isolated.log: `codex off (Codex week 83% >= 47%)`, `(no CLAUDE_CLOUD_POOL)`). If Codex had
room, a case expecting "not sent" could see a dispatch. The fix would be one more isolating export (`TM_FIT_ROOM_FLAG=/nonexistent`;
the fit-room sections at harness lines ~356 and ~435 already set their own). It is outside the 4 changes the task allows, so it is
not made. The cap-8 expectation is written to be independent of it (it checks only that nothing went to actions).

## Seeded bugs (prove the changed cases can fail)

No product code changed in any language. The seeds are in /tmp copies of the code under test, run with `TMS_TS=<copy>`:

| Seed | File (copy of) | Bug | Result |
|---|---|---|---|
| A | manage-agents/tm-shard.sh | TM_SHARD_ACTIONS_HEADROOM default 1200 -> 1100 (line 5,200) | 148/1: only "own heavy reading over the hard limit ... 6 parts" FAILS |
| B | manage-agents/tm-shard.sh | TM_SHARD_ACTIONS_CANCEL default back to 6600 | 148/1: only "the hard NMAX caps a waiver at cap 8 ..." FAILS |
| C | manage-agents/tm-shard.sh | no tm-shard --budget beside a caller's --budget/--deadline (the old rule) | 147/2: only P4 and P5 FAIL |
| D | manage-agents/test-harness/tmshard/test-tmshard.zsh | without the TM_SHARD_RECORDS export (the old harness) | 106/42 (runs/before.log) |

The seeds were never in the live file: its sha256 (sha256.txt) is the same before and after.

## Tests

- The harness itself, as above (runs/*.log).
- Selected VE tests (`mac-pytest.sh --select`, on ecaa912a65, the evidence commit; the branch adds only
  `docs/infra/tmshard-harness-update/`): 10 units, 0 failed, exit 0 (ran on the VM, 223 s).
- No DELTA rows: no Lean, trust-base or user-visible VE change.

## Notes for the DRI

- After the install the harness is green (149/0) on the live files and guards tm-shard changes again.
- tools-local/test_tm_shard_actions_120.py (the decision's condition) was not touched.
