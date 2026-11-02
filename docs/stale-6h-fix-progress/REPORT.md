# stale-6h-fix-progress: a commit alone is not progress for a fix round past 4x its median

Status: installed in `tools-local/stale-6h.py`; 34 stub tests pass; 20 of 20 seeded bugs caught.
Changed: the script and `tools-local/test_stale_6h.py` (manage-agents, not in git); this directory is the saved evidence.
Replay: pc-1 flagged 11-02 02:36Z, about 6 h before the advisor raised it; jt-2c is the only other live flag.
Open: the measured median is about 140 min, not the 85 min in the task, so the limit is about 9.3 h, not 5.7 h (below).
No DRI signature is needed: no VE behaviour changed and there is no DELTA.md.

## Decision: DRI item 3 of reviews/dri-decisions-20261102-adv0847.md

The rule, in `fix_rounds`, `fix_median` and `fix_stale`:

- In a fix round: last `fix-start` with no later `gate-start`, `gate-skip`, `ready` or `train-start`; `-cNNNNNN` folds into the item.
- Median: the last `fix-start` of each round to the `ready` or `gate-start` that ended it, rounds ended in the last 7 days,
  measured on every pass.
- Past 4x the median: reported with the round's age and the reason, whatever its commit dates, with no 6-h floor.
- Every other item, and a fix round under the limit: the 6-h rule as before.
- No measured round: the rule is off for that pass, stderr says so, and `stale-6h.json` has `fix_median_min` null.

## The 85-min median does not match the measure in the task

`fix-start` to `recheck-start` is what `tools-local/fix-round-stats.py` reports as a fix round's minutes, and it gives 72 min
here (82 over the rounds that tool lists). The task's measure, `fix-start` to the next `ready` or `gate-start`, is longer.
Each row below is the same 7-day window, read from `stage-events.jsonl` at the time shown.

| Pairing | At 08:47Z: n, median, 4x | At 15:00Z: n, median, 4x |
|---|---|---|
| Last fix-start of a round to its ready or gate-start (installed) | 13, 142.9 min, 9.5 h | 12, 136.8 min, 9.1 h |
| Every fix-start to the next ready or gate-start | 58, 410.2 min, 27.3 h | 50, 343.7 min, 22.9 h |
| fix-start to recheck-start (not the task's measure) | 96, 72.2 min, 4.8 h | 95, 71.8 min, 4.8 h |

The second row fails the acceptance: pc-1's round was 21.4 h, so that limit would never have flagged it. The installed row is
the task's measure read with the task's own definition of a round (the last `fix-start`), and it does flag pc-1. Two things
follow, and neither was changed here:

- pc-1 fired 3.9 h later than a 5.7-h limit would have (round 9.5 h, not 5.7 h).
- The median rests on about 12 rounds: 42 of the 54 rounds closed in the window went straight to `train-start`, which the task
  does not measure. One new round can move the limit by tens of minutes, so an item near the limit can alarm twice.

A round replaced by a new `fix-start` is not sampled, and neither is one ended by `gate-skip` or `train-start`. `recheck-start`
does not close a round, as the task says, so a round waiting on its recheck still counts as open.

## Replay of the last 7 days

`python3 -I tools-local/stale-6h.py --replay 7`, run 2026-11-02 about 15:21Z, output in `replay-20261102.txt` and `.json`. One pass
per 15 min, each seeing only the events up to it, so a flag time is good to 15 min.

| Item | Round started | Flagged at | Limit then | Ended |
|---|---|---|---|---|
| pc-1 | 11-01 17:04Z | 11-02 02:36Z (9.5 h) | 9.5 h (143 min, n 13) | new fix-start 11-02 14:27Z after 21.4 h |
| jt-2c | 10-31 01:01Z | 10-31 10:36Z (9.6 h) | 9.3 h (140 min, n 12) | gate-start 10-31 12:58Z after 11.9 h |

The replay also lists qa-q2b, rd-9b and qa-q2c: rounds from Oct 14 that never ended, marked "not in flight now: no live flag".
They are abandoned rounds the live rule would not report (it reports in-flight items only). Stage events do not record which
chains were alive, so for these three the replay can only say that they are not in flight now.

pc-1 made 12 non-merge commits inside the round, 11-01 18:04Z to 11-02 11:26Z
(`git -C ~/code/ve-pc-1 log --since=2026-11-01T17:04:27Z --until=2026-11-02T14:27:29Z --no-merges`).

## Install

`.new`, py_compile, backup `tools-local/stale-6h.py.bak-20261102-stale-6h-fix-progress`, md5 check, mv.
Base md5 9c09e10cb75e35e7371293bc1c3f4ae2, installed md5 5a0b8924b22635fc614e94f17bf40972. svc-stale-6h runs the script fresh,
so it was not restarted. On the real state at install, the old and new scripts printed the same `--json` (`[]`), because no
in-flight item was past the limit.

`stale-6h.json` gains `fix_median_min` and `fix_rounds`, and a fix-round row gains `rule`. NOW.md and checkin-scan.py read the
same keys as before, and `last` fits NOW.md's 80-character cut (`test_the_row_fits_now_md`). `tools-local/stale-6h-svc.sh`'s
header comment still describes only the 6-h rule; it was left alone rather than editing a running zsh script in place.

## Tests and seeded bugs

`python3 -I tools-local/test_stale_6h.py`: 34 tests, OK. `seeded-bugs.json` lists all 20 seeded bugs with file and failing test.
