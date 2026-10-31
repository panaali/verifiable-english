# eff-tm-control: where a trust_mutants sweep spends its time

Status: done, measure only; code b13852342. `--json` gains `steps`, and `--merge` keeps and sums the parts' steps.
Open: none; no DRI signature (`steps` is added information, R3). Result: jt-2c's shared step is the check-file
probes without a mutant, 98% of its pre-mutant time. They can't be reused across parts or across a fix: no cut.

| VM, --jobs 4 (`evidence.json`)     | run s | pre-mutant s | control probes                    | mutants s |
|------------------------------------|-------|--------------|-----------------------------------|-----------|
| jt-2c 73e809748, unsharded         | 4,327 | 1,292        | 1,264 wall; 1,801 Lake-s, 7 files | 3,033     |
| jt-2c --shard 2/4, lazy (reverted) | 2,485 | 32           | 1,586 Lake-s, 3 files             | 2,451     |
| qt-a3d 493da762, unsharded         | 5,446 | 132          | 109 wall, 1 file                  | 5,312     |

Actions implies (7,250 − 2,513) / 3 ≈ 1,579 s shared per jt-2c part. Other candidates: control build 0.5 s,
scratch copies 12 s, stage controls 192 Lake-s; the survivors' check builds are per mutant.

## Decision: stop

- Across parts: the parts run at the same time on different runners.
- Across sweeps: the kills read 3 files (Compose/Examples 23, Service/ScopeExamples 5, Service/ActsExamples 1).
  Each imports the item's changed modules (Compose/Dispatch, Norms/Plain, Service/Document), so a fix probes them
  again; only an identical-inputs rerun could reuse them.
- Lazy probing (8831a1b28, reverted): the 3 files read hold 1,586 of the 1,801 Lake-s. Skipping the 4 others
  saves about 215 s and can leave a job idle waiting on a probe. The 19 owned verdicts matched the unsharded run's.

Follow-up (needs a DRI ruling): each probe elaborates its whole check file; per-kill probes take 58% of jt-2c's Lake
time and 52% of qt-a3d's.

Seeded bugs: `seeded-bugs.json`.
