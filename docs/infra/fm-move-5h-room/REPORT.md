# fm-move-5h-room: freeze-mover moves a 5-h-frozen worker by --resume; the picker's long-room rate is measured

INSTALL WAITS FOR DECIDER READ. All four changed installed scripts are STAGED as `<file>.new-fmw` (zsh -n / py_compile clean), not
installed. The install commands are in "Install" below. There is no DELTA row: no Lean, no trust base, and no repo product code
changed.

Row: fm-move-5h-room. Spec: orchestrator ruling 222127Z (inbox/dri/done/20261113T222127Z-orchestrator-3091424.md) and
reviews/dri-decisions-20261113-thresholds.md item 4 (orchestrator 230624Z ruling items 3 and 4).

## What changed (all in /home/seyran/code/manage-agents)

| file | state | change |
|---|---|---|
| freeze-mover.sh | staged `.new-fmw` | rule (c) no longer waits out every 5-h freeze. A 5-h-frozen worker is moved when its window resets more than 60 min away (FM_MOVE_AFTER_MIN) AND the picker admits another account (`PICK_NOWAIT=1 PICK_LIGHT=1 PICK_AVOID=<its config dir>`, the same call claude-resume-on-limit.sh makes; PICK_LONG_ROOM projects the room). The move is transcript copy + `--resume`: freeze-mover writes the destination into the wrapper's LR_MOVE_FILE and kills the stopped claude and its tool commands. The wrapper resumes the SAME session there. The chain is not killed, and chain workers and delegates are treated alike. Otherwise the worker waits as before, and the log line says why: reset within 60 min, no account admits it (with the PICK_WHY text), PICK_LONG_ROOM off, or a wrapper without LR_MOVE_FILE. Weekly-cap and FM_MAX_WAIT moves stay chain relaunches. |
| claude-resume-on-limit.sh | staged `.new-fmw` | each attempt runs with `LR_MOVE_FILE=<spool>/<sid>.<wrapper pid>.move`. When an attempt ends non-zero and that file exists, the wrapper copies the transcript to the named config dir (limit-resume.py `where` + `move`) and resumes with `--resume <sid>` and a "you were moved" prompt. If the copy fails, it resumes on the same account. A zero exit removes the file and ignores it. |
| tools-local/limit-resume.py | staged `.new-fmw` | new read-only subcommand `where <config dir> <sid>` that prints the session's transcript path (the existing `transcript()`). |
| pick-claude-account.sh | staged `.new-fmw` (+ `pick-claude-account.sh.fmw.patch`) | (i) the PICK_LONG_ROOM 5-h projection uses the account's MEASURED points per session-hour (tools-local/session_rate.py). If the account has no measurement it uses the pooled rate of its plan size, then the modelled default (5x 6 -> 8; main 1.5 unchanged). The live last hour per running session stays the floor, and a refusal names the rate's source. (ii) Inside main's weekly endgame window (endgame.HOURS before its reset), main goes first and the helpers are ordered by projected 5-h room, not PICK_PREFER. Overflow therefore spreads by 5-h room, or waits through the PICK_LONG_ROOM refusal; it no longer fills one helper. The best account is chosen after the loop; the loop still streams accounts.sh lines. |
| tools-local/session_rate.py | NEW (nothing installed reads it until the picker is installed) | the measured rate: rises of the 5-h meter between consecutive usage-watch.log readings in the last 6 h (PICK_RATE_H), divided by session-hours from pick.log busy counts. It leaves out frozen (>= 88), reset, gap, unknown and unsampled intervals, and returns None below 2 session-hours (PICK_RATE_MIN_SH). It has a read-only CLI. |
| tools-local/test-freeze-mover.zsh | edited in place (backup `.bak-20261120-fmw`) | new case F (F1-F4); cases A-E unchanged |
| tools-local/test_limit_resume.py | edited in place (backup) | 3 move-request tests. The helper import now loads any file name, so `LR_HELPER=<.new copy>` works. |
| tools-local/test_pick_longroom.py, test_pick_why.py | edited in place (backups) | `PICK_BURN5=6` pinned where their arithmetic is at the old default (passes on installed and staged) |
| tools-local/test_pick_srate.py | NEW | 5 module cases + 6 picker cases |

## Measured recalibration (spec item 2)

`python3 -I tools-local/session_rate.py <hours>` on the live logs, 2026-11-20 ~16:55Z:

- 6 h: danielsaeedi37 rise 136 over 17.40 session-hours = **7.82** per session-hour; main and saeedi.danial no measurement.
- 24 h: danielsaeedi37 6.90; 5x pool 7.26.
- 72 h: danielsaeedi37 6.25; saeedi.danial 11.79 (8.73 session-hours); 5x pool 6.83.
- main: no measurement (its 5-h meter reads -2, no window, in the log tail), so main keeps the 1.5 default unless the live hour is higher.

The orchestrator's 11-13 reading was ~8 under Fable seats, and today's 6-h figure is 7.8. So the 5x fallback default for the long-room line
is 8, used only when neither the account nor its plan pool has 2 session-hours of measurement. PICK_BURN5 in the environment still
overrides it. The endgame-room line and the 30-70% cap line keep their default of 6 (out of scope).

## Tests: fail on the installed code, pass on the staged code (tests.log)

- `zsh iso.sh <name> 2G -- zsh tools-local/test-freeze-mover.zsh <freeze-mover file>` with `FMT_WRAPPER`/`FMT_LR_HELPER` = the staged
  wrapper/helper. INSTALLED freeze-mover.sh: SOME FAILED, 11 FAIL lines, all in case F (A-E 19 PASS). STAGED: ALL PASS (A-F).
  F1: a reset 45 min away keeps the worker, with no pick. F2: the picker admits nothing, or PICK_LONG_ROOM is off, so the worker is
  kept and the reason logged; the picker is asked with PICK_AVOID/NOWAIT/LIGHT. F3: the same session resumes on acctB with
  --resume, the transcript is copied, the chain lives on and gets rc 0, and nothing is relaunched. F4: no LR_MOVE_FILE, so the
  worker is kept and logged.
- `python3 -I tools-local/test_limit_resume.py` (LR_SCRIPT/LR_HELPER = staged): INSTALLED 3 new tests fail; STAGED 15/15 OK.
- `python3 -I tools-local/test_pick_srate.py` (PICK_SCRIPT = staged): INSTALLED 6 picker cases FAIL (module cases pass); STAGED 11/11 OK.
- Regression: every tools-local test that names PICK_SCRIPT (22 files) was run with the staged picker. 12 are OK. 10 have failures,
  and each failing set equals the installed picker's (pre-existing, not this item): test_ccloud_main88 1, test_endgame 1,
  test_pick_main5h_nowindow 4, test_pick_main5h_unknown 2, test_pick_main_rank 11, test_pick_mgmt 1, test_pick_rcx_main_pace 2,
  test_pick_released_main 3, test_role_budget 1, test_usage_reset_fresh 16. One finding was fixed on the way. My first version read
  all of stdin before the loop, and test_pick_main5h_unknown's rank-1 interleave test (accounts.sh blocked after main's line) failed
  on it. The loop streams again, and the failing set is back to the installed 2.
- The patch applies on the other item's staged `pick-claude-account.sh.new-usagew` (4 hunks, offset 14), and test_pick_srate passes
  on that combination (11/11 OK).

## Seeded bugs (seeded-bugs.json; each on a /tmp copy of the final staged file, then deleted; md5.txt)

| id | language | file | test that failed |
|---|---|---|---|
| S1 move inside 60 min | zsh | freeze-mover.sh.new-fmw | test-freeze-mover.zsh F1, F2 |
| S2 picker not told to avoid the frozen account | zsh | freeze-mover.sh.new-fmw | test-freeze-mover.zsh F2 picker args |
| S8 moves with PICK_LONG_ROOM off | zsh | freeze-mover.sh.new-fmw | test-freeze-mover.zsh F2 flag |
| S3 wrapper resumes on the same account | zsh | claude-resume-on-limit.sh.new-fmw | test_freeze_mover_move_resumes_on_destination |
| S4 frozen readings counted | Python | tools-local/session_rate.py | test_frozen_reset_gap_and_unsampled_intervals_are_left_out |
| S5 picker ignores the measured rate | Python | pick-claude-account.sh.new-fmw | 3 Picker cases (measured high/low, pool) |
| S6 no endgame room order | Python | pick-claude-account.sh.new-fmw | test_main_endgame_overflow_spreads_by_5h_room, test_main_goes_first_in_its_window |
| S7 `where` finds no transcript | Python | tools-local/limit-resume.py.new-fmw | test_freeze_mover_move_resumes_on_destination |

8 of 8 caught.

## Install (decider read)

```
cd /home/seyran/code/manage-agents; S=$(date -u +%Y%m%dT%H%MZ)-fmw
cp -p tools-local/limit-resume.py tools-local/limit-resume.py.bak-$S
cp -p claude-resume-on-limit.sh claude-resume-on-limit.sh.bak-$S
cp -p pick-claude-account.sh pick-claude-account.sh.bak-$S
cp -p freeze-mover.sh freeze-mover.sh.bak-$S
mv tools-local/limit-resume.py.new-fmw tools-local/limit-resume.py
mv claude-resume-on-limit.sh.new-fmw claude-resume-on-limit.sh
mv pick-claude-account.sh.new-fmw pick-claude-account.sh
#   (if pick-claude-account.sh.new-usagew was installed first: instead of the mv,
#    patch pick-claude-account.sh < pick-claude-account.sh.fmw.patch && zsh -n pick-claude-account.sh)
mv freeze-mover.sh.new-fmw freeze-mover.sh
# restart the freeze-mover service (its running loop keeps the old code):
systemctl --user stop $(systemctl --user list-units --no-legend 've-svc-freeze-mover-*' | awk '{print $1}')
setsid nohup zsh $PWD/iso.sh svc-freeze-mover 2G -- zsh $PWD/freeze-mover.sh >> $PWD/svc-freeze-mover.log 2>&1 < /dev/null &
zsh freeze-mover.sh --dry-run    # one read-only pass
```

Install the order as written: helper, wrapper, picker, then freeze-mover. Only wrappers started after the wrapper's install export
LR_MOVE_FILE. Sessions already running keep the old wrapper and are waited out as before (case F4's path). The wrapper alone is
inert, because nothing writes the file until freeze-mover is installed. The picker can go in on its own. Rollback: mv each
`.bak-$S` back and restart the service.

Overlap with other staged picker copies: `.new-usagew` (usage-watch-reset-fresh, staged 11-20) touches lines 181-198; mine start
at 419, and the patch applies on it (above). `.new-pickw`, `.new-rcxpace`, `.new-rel`, `.new-oseqmain` and `.new-cloud3logins`
delete lines that the installed file now has, so they are built on older installed files. They do not overlap this change's
content, but none of them can be mv'd over the current file. No `.new-*` of freeze-mover.sh, claude-resume-on-limit.sh or
limit-resume.py exists besides mine. I could not find the `pick-main-slot-mark` copy named in the task; that item is merged
(`merge-train-pick-main-slot-mark.final.md`).

## Choices made (conservative option, not asked)

- The move is refused when the PICK_LONG_ROOM flag is off. Without the flag the picker projects no room, and the spec asks for
  "projected room admits it" (S8).
- The picker is called with PICK_LIGHT=1, as claude-resume-on-limit.sh already calls it for a limit move: a moved session is
  admitted work, so the worker cap, the VM load gate and the role hold do not apply. The PICK_LONG_ROOM projection counts it as
  the (n+1)-th session. After each move, freeze-mover waits up to 30 s for the wrapper to resume. The next pick in the same pass
  then counts it, so 8 frozen sessions do not all land on one account.
- The weekly-cap and FM_MAX_WAIT (6 h) paths are unchanged chain relaunches. "Remove rule (c)'s fixed wait" is read as removing the
  unconditional wait for a 5-h freeze.
- The measured rate replaces the modelled default even when it is lower (main 0.45 vs 0.77 is the ruling's own example). It needs
  2 session-hours of data, and the live last-hour rate stays the floor. Meter rises with no counted session (interactive use, the
  orchestrator on main, seats that are not `claude -p`) are kept, so the rate errs high.
- The week projection (bw_) is unchanged: the ruling names the 5-h rate.
- Main goes first in its own weekly endgame window. Its expiring points are the reason for the window, and "overflow" is what main
  cannot take.

## Notes for the DRI

- The plan pool uses the account lines read so far, because the loop streams. accounts.sh prints main, danielsaeedi37,
  saeedi.danial, so saeedi.danial (the usual idle destination) pools with danielsaeedi37. danielsaeedi37 without its own data
  falls to the default 8.
- pick.log busy counts include frozen sessions. Intervals at the freeze level (>= 88) are left out for that reason.
- Each picker call reads about 200 KB of each log tail, about 30 ms (not benchmarked).
- `python3 -I tools-local/delegate-cw.py` prints "own session not found" in this builder seat (no dri-delegate.sh VE_STEP). With my
  transcript path it MEASURED 0.46M CW (47 calls), then 0.86M CW (74 calls); final figure in the build reply.

SIZE: 247 product (freeze-mover 53, wrapper 19, picker 30, limit-resume 6, session_rate.py 139; 14 lines removed), 295 tests
(test-freeze-mover 64 + 3, test_limit_resume 37, test_pick_srate 191, pins 3), about 190 other hand-written lines (this report).

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No Lean or relay changed.
2. Every deliverable built: PASS. Move rule (test-freeze-mover F1-F3), resume move (test_limit_resume move tests), measured
   per-account rate (test_pick_srate Picker), 5x recalibration (test_no_measurement_uses_the_recalibrated_5x_default_8), endgame
   spread (test_main_endgame_overflow_spreads_by_5h_room).
3. Tests can fail: PASS. Installed-code runs fail (tests.log), and 8/8 seeded bugs are caught (seeded-bugs.json).
4. Python, Lean and Rust agree, valid inputs pass: PASS for the scope. Picker regression sweep over 22 files: failing sets equal
   the installed baseline (tests.log).
5. R8 binding: N.A. No binding changed.
6. Gate evidence matches HEAD: PASS. Docs only in the repo; the chain runs the gate on the final HEAD.
7. No unsigned item: PASS. No DELTA row needed (no Lean or trust base).
8. Every user-visible change in DELTA: N.A. Operations scripts only, no checker output.
9. Test selection finds the tests: N.A. No repo code changed. The manage-agents tests are named above.
10. Lean statements: N.A.
11. Limits fail closed: PASS. Unknown reset, no admitting account, flag off, or no move file all mean the worker stays (F1, F2,
    F4). A failed transcript copy resumes on the same account (test_failed_move_resumes_on_the_same_account). Too little data falls
    back to the default (test_too_little_is_none_and_pool_fallback). The zsh test polls with 0.5-s waits (existing pattern) and
    asserts no elapsed time.
12. No CPU or memory regression: PASS by reading. Two log tails (200 KB) per picker call; no per-candidate subprocess.
13. Test-removed trailers: N.A. No test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS.
    - Both directions: move vs keep (F1/F2/F4 vs F3); measured high refuses vs measured low admits; inside vs outside main's
      window; zero exit ignores the move file vs non-zero resumes.
    - Spec re-read: "move when the reset is > 60 min away AND ... projected room on another account admits it" against the row
      note (rmove: `$mins -gt 60` plus the picker call). "transcript move + --resume, not a cold restart" against ruling 222127Z
      (wrapper MOVE + --resume; F3 "chain lives on, no relaunch"). "measured per-session rate per account and plan size" against
      thresholds item 4 (pick_rate: account, then plan pool). "nothing overflows onto one helper: overflow waits or spreads by 5-h
      room" against 230624Z item 3 (the endgame order plus the PICK_LONG_ROOM refusal).
15. Overclaim, silent cut, every new check can fail, limits charged first: PASS.
    - No deliverable was cut.
    - Every new guard has a seed: S1, S2, S8 (freeze-mover); S3, S7 (wrapper/helper); S4 to S6 (rate/picker).
    - "unchanged" claims cite the regression sweep.
