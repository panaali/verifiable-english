# usage-watch-reset-fresh: a pre-reset reading cannot pause workers past the reset (build report)

**Review fix, on bdf43319a6 (this commit's parent).** F1 (B) is fixed at its owner: `endgame.hours_to` now picks the nearest year.
The fix is staged as five `.new-usagew2` copies, and two more year-less parsers of the reset field now go through it.
PROBE F1 gives 73.0 (exit 0) on the staged copies and 77.0 on the installed ones. 28/28 pass staged; 6 new tests fail installed.
The 5 new seeds (S10-S14) are all caught. INSTALL WAITS FOR DECIDER READ (section "Review fix F1" below). No DELTA row.

INSTALL WAITS FOR DECIDER READ. No DELTA row: no Lean, Python, Rust or trust-base file of this repo changed.

Row usage-watch-reset-fresh; decision `reviews/dri-decisions-20261113-thresholds.md` (orchestrator thresholds ruling 230624Z
item 4 and its 23:09Z note; challenge NOTE 5). Every product change is a staged `.new-usagew` copy in
`/home/seyran/code/manage-agents`. Nothing installed was changed. The full diffs are in `live-changes.diff` and the md5s in `md5.txt`.

## What changed (staged)

1. `tools-local/reset_fresh.py.new-usagew` (new, 68 lines). This is the one owner of the rule "this reading names a reset that has
   passed". It parses the reset fields with endgame.py's `hours_to` (adding a year wrap) and reads the clock from `ENDGAME_NOW`.
   `line <taken> <r1> <r2>` prints one of three states:
   - `pre`: the line was taken before a reset that has now passed.
   - `post`: the line was taken after the passed reset but still names it.
   - `none`: no reset named in the line has passed.

   `watch <r1> <r2>` prints `<old5> <oldW> <next s>`. A pool counts as old while its reset passed less than 600 s ago.
   On any error it prints the neutral answer and exits 0.
2. `accounts.sh.new-usagew` (+15 -4):
   - A cached line in the `pre` state is never reused, so the account is probed at once. The `.last` fallback skips such a line too.
   - A `post` line (the service still reports the old window) is reused for ACCOUNTS_TTL only, never for the 1800-s
     ACCOUNTS_CAP_TTL. This removes the 1800-s reuse across a reset.
   - The age clock is `ENDGAME_NOW` when set (tests), otherwise `date`.
3. `usage-watch.sh.new-usagew` (+24 -5):
   - **Ignoring the old window.** For each account and pool, if the reading names a reset that passed less than 10 min ago,
     that pool's % counts as -1 (unknown) for PAUSE, RESUME, HOLD and WARN. The watcher prints one `RESET-FRESH` event,
     `usage-watch.log` keeps the raw %, and the next poll comes after 60 s with `ACCOUNTS_CAP_TTL=0`.
   - **Waking at the reset.** The loop also wakes 5 s after the nearest reset still ahead, when that comes before the
     next poll, and that poll runs with `ACCOUNTS_CAP_TTL=0`.
   - **Effect.** An account paused before its reset resumes on the first post-reset poll, even if the service still reports
     the old 97.
4. `pick-claude-account.sh.new-usagew` (+14 -0). `pace_line()` accepts `weekly <A> <S> <F>`, which gives
   min(A - S x days to main's weekly reset, F). The reset is field 7 of `accounts-cache/main.line`. If that reset has
   already passed, the count runs to the next one, 7 days later. If the reset is unreadable, d = 7, which gives the lowest
   line. With `weekly 97 4 90`: 69 at the reset, then +4 a day, flat 90 in the last 1.75 d. The dated form is unchanged.
   The function stays self-contained, because `inbox-wait.sh` execs it alone (it imports `endgame` itself).
5. `tools-local/test_usage_reset_fresh.py` (new, 290 lines, 21 tests):
   - Helper (4 tests): reset_fresh.py itself.
   - Accounts (6 tests): `accounts.sh` with a stub claude.
   - UsageWatch (5 tests): `usage-watch.sh` on a stub accounts.sh, with a stub `sleep` that ends the loop after N polls.
   - WeeklyPace (6 tests): the picker in the `PickCase` sandbox.

   Clocks are fake throughout: `ENDGAME_NOW`, taken from the wall clock at the start of each test so the installed
   accounts.sh sees the same ages. The tests use no sleep, no live file and no probe.

## Tests (both directions)

- On the INSTALLED files, 16 of 21 fail (`tests-installed.log`: `FAILED (failures=16)`). Command:
  `python3 -I tools-local/test_usage_reset_fresh.py`. Among them:
  - the incident: a cached 97 taken 300 s before the reset and read after it is reused with no probe;
  - the 97 is PAUSED on;
  - no wake at the reset;
  - the weekly form reads as no line.
- On the STAGED files, 21 of 21 pass (`tests-staged.log`: `OK`). Command: `ACCOUNTS_SCRIPT=$PWD/accounts.sh.new-usagew
  USAGE_WATCH_SCRIPT=$PWD/usage-watch.sh.new-usagew PICK_SCRIPT=$PWD/pick-claude-account.sh.new-usagew
  RESET_FRESH_SCRIPT=$PWD/tools-local/reset_fresh.py.new-usagew python3 -I tools-local/test_usage_reset_fresh.py`.
- The 5 tests that pass on both are the controls for the opposite direction:
  - a >= 88 line with its reset 3 d ahead is still reused for 1800 s;
  - a < 88 line inside the TTL is still reused;
  - a reading whose reset passed 11 min ago is acted on (PAUSED), as before;
  - with no reset near, the loop sleeps 300 s with the default ACCOUNTS_CAP_TTL;
  - the dated PICK_MAIN_PACE form is unchanged.
- I ran 22 existing suites that read these scripts on both the installed and the staged copies (`existing-suites.txt`). All 22
  have the same failing test ids on both. 10 suites already fail on the installed files: test_ccloud_main88 1, test_endgame 1,
  test_infra_feed 5, test_pick_main5h_nowindow 4, test_pick_main5h_unknown 2, test_pick_main_rank 11, test_pick_mgmt 1,
  test_pick_rcx_main_pace 2, test_pick_released_main 3, test_role_budget 1. Those failures come from the installed code, not
  this item. `test_codex_meter_reset.sh` passes on both.

## Seeded bugs (`seeded-bugs.json`; each on a /tmp copy of the staged file, all caught, copies deleted)

| id | file | change | failing test |
|---|---|---|---|
| S1 | manage-agents/accounts.sh.new-usagew (zsh) | `pre` never returns 1 | Accounts.test_pre_reset_cap_line_not_reused_probe_at_once (+2) |
| S2 | manage-agents/accounts.sh.new-usagew (zsh) | cap reuse for `post` lines | Accounts.test_lagging_post_reset_line_no_cap_reuse |
| S3 | manage-agents/usage-watch.sh.new-usagew (zsh) | old week not set to -1 | UsageWatch.test_old_window_97_after_reset_not_paused (+1) |
| S4 | manage-agents/usage-watch.sh.new-usagew (zsh) | no wake at the reset | UsageWatch.test_wakes_at_the_next_reset_with_cap_ttl_0 |
| S5 | manage-agents/tools-local/reset_fresh.py.new-usagew (Python) | `pre` only a day after | Helper.test_line_states (+1) |
| S6 | manage-agents/tools-local/reset_fresh.py.new-usagew (Python) | GRACE 6000 | Helper.test_watch_grace_and_next (+1) |
| S7 | manage-agents/pick-claude-account.sh.new-usagew (Python) | no wrap past the reset | WeeklyPace.test_fresh_week_after_reset_low_line |
| S8 | manage-agents/pick-claude-account.sh.new-usagew (Python) | flat F dropped | WeeklyPace.test_inbox_wait_reader_gets_the_weekly_line |
| S9 | manage-agents/pick-claude-account.sh.new-usagew (Python) | unknown reset = d 0 | WeeklyPace.test_no_cache_start_of_week_value |

## Choices made (the conservative option, not asked)

- A `post` line (taken after the reset but still naming it) never gets the 1800-s cap reuse, with no time limit. This costs at
  most one probe per 240 s per >= 88 account while the service lags, and the watcher polls every 300 s anyway.
- During the 10 min, the old pool counts as unknown (-1). That is the existing meaning of an unknown probe, so a paused
  account resumes: its own reading says that window has ended.
- If the weekly form cannot read main's reset, it uses d = 7, the lowest line (69 for 97 4 90), not "no line".
- `PICK_MAIN_PACE` is not rewritten by this item. The install steps below write `weekly 97 4 90` only at or after main's
  reset (23:00Z 11-20). Written now, it would raise the line from about 87 (the dated line) to 90 before the reset.

## Install (for the decider; nothing below has been run)

```
cd /home/seyran/code/manage-agents
md5sum accounts.sh usage-watch.sh pick-claude-account.sh   # expect e8620f912790a399738d42030d9dd809, fe58d49c390029436c35cba4ff3ab929, 4b4547aaa96bdb0cd5e33110c9426726 (see md5.txt); any other: rebase the .new-usagew first
ACCOUNTS_SCRIPT=$PWD/accounts.sh.new-usagew USAGE_WATCH_SCRIPT=$PWD/usage-watch.sh.new-usagew PICK_SCRIPT=$PWD/pick-claude-account.sh.new-usagew RESET_FRESH_SCRIPT=$PWD/tools-local/reset_fresh.py.new-usagew python3 -I tools-local/test_usage_reset_fresh.py   # 21 OK
ts=$(date -u +%Y%m%dT%H%MZ); for f in accounts.sh usage-watch.sh pick-claude-account.sh; do cp -p $f $f.bak-$ts-usagew; done
zsh -n accounts.sh.new-usagew && zsh -n usage-watch.sh.new-usagew && zsh -n pick-claude-account.sh.new-usagew && mv tools-local/reset_fresh.py.new-usagew tools-local/reset_fresh.py && mv accounts.sh.new-usagew accounts.sh && mv pick-claude-account.sh.new-usagew pick-claude-account.sh && mv usage-watch.sh.new-usagew usage-watch.sh
python3 -I tools-local/test_usage_reset_fresh.py           # now on the installed files: 21 OK
grep -E 'PAUSED|RESUMED' svc-usage-watch.log | tail -n 3   # restart only when no account is left PAUSED (its pids live in the loop's memory)
systemctl --user stop ve-svc-usage-watch-1795073208.scope
setsid nohup zsh /home/seyran/code/manage-agents/iso.sh svc-usage-watch 2G -- zsh /home/seyran/code/manage-agents/usage-watch.sh 300 >> /home/seyran/code/manage-agents/svc-usage-watch.log 2>&1 < /dev/null &
# at or after 23:00Z 11-20 (main's weekly reset), in place of wake main-endgame-1120 step (c)'s dated rewrite:
cp -p PICK_MAIN_PACE PICK_MAIN_PACE.bak-$(date -u +%Y%m%dT%H%MZ)-usagew && echo "weekly 97 4 90" > PICK_MAIN_PACE
```

accounts.sh and the picker run fresh on each call, so they need no restart. usage-watch.sh is a running loop (pid 45696 in
`ve-svc-usage-watch-1795073208.scope`), so it needs the restart above. Rollback: mv each `.bak-$ts-usagew` back, rm
`tools-local/reset_fresh.py` and restart usage-watch the same way. Without reset_fresh.py, the new scripts behave as the
old ones (accounts.sh `rstate` is empty; usage-watch falls back to `0 0 -1`).

**Overlap with other staged picker copies.** `pick-claude-account.sh.new-{cloud3logins,oseqmain,pickw,rcxpace,rel}` are all
older than the installed picker (15:31Z 11-20). Four of them have the same `def pace_line` as the installed picker; `.new-cloud3logins`
(Nov 8) has an older or absent one. This item was built on the INSTALLED picker. Whichever of those is installed later must
carry this `pace_line` hunk.

## Notes for the DRI

- After install, wake main-endgame-1120 step (c) should write `weekly 97 4 90` (above) instead of the dated line. At the reset
  the two agree: 69 at 23:00Z 11-20 and 90 from 05:00Z 11-26.
- 10 existing picker/feed suites already fail on the installed files (list above). They are not from this item.

SIZE: 121 product, 290 tests, 0 other hand-written lines (plus this report).

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no Lean or relay change).
2. Deliverables built, no rule broken: PASS. Built: the cache drop and immediate probe (Accounts.test_pre_reset_*), the 10-min
   ignore and forced ACCOUNTS_CAP_TTL=0 (UsageWatch.*), the 1800-s reuse across a reset removed
   (Accounts.test_lagging_post_reset_line_no_cap_reuse), and the week-relative PICK_MAIN_PACE (WeeklyPace.*). Everything is
   staged and not installed, as the task says.
3. Tests and gates can fail: PASS. 16/21 fail on the installed files; 9 seeded bugs are all caught (seeded-bugs.json).
4. Implementations agree, valid inputs pass: PASS. Controls (test_control_*, test_dated_form_unchanged); 22 existing suites
   have the same failing ids on both copies (existing-suites.txt).
5. R8 binding: N.A.
6. Gate evidence matches final HEAD: N.A. for the builder (the chain runs the gate on the final HEAD; this commit adds docs only).
7. No unsigned item: PASS (no DELTA row; no signature reserved).
8. User-visible change in DELTA: N.A. (no VE language or checker change).
9. Test selection: PASS (mac-pytest --select on this branch; docs-only change).
10. Lean statements: N.A.
11. Budgets and deadlines fail closed: PASS. The reset helper's errors fall back to the old behaviour, never to a looser one:
    Helper.test_cli_never_fails; an unknown reset gives the lowest pace line (test_no_cache_start_of_week_value). The tests
    use no sleep (the stub sleep records the duration and does not wait).
12. CPU and memory: PASS. One extra `python3 -I` call per account per accounts.sh `fresh()` and per usage-watch poll (about
    30 ms each), next to the existing endgame.py calls. No pilot is affected.
13. Test-removed trailer: N.A. (no test removed or renamed).
14. Both directions, cited evidence, spec re-read: PASS. The controls are listed above. Each claim cites a log in this folder.
    I re-read the spec (row note in prompts/task-usage-watch-reset-fresh.txt, SPEC and TESTS):
    - "drop the cached line and probe at once": accounts.sh `pre`.
    - "ignore a pre-reset reading for 10 min": usage-watch GRACE 600.
    - "Remove: the 1800-s reuse across a reset": `post` gets no cap reuse.
    - "line = 97 - 4 x days ..., flat 90 in the last 1.75 d": min(A - S d, F), checked at 1.75 d by the reader test.
15. Overclaim, silent cut, every check can fail, limits: PASS. No deliverable was cut, and every new check has a seed (S1-S9).

## Review fix F1 (usage-watch-reset-fresh-review.final.md)

Evidence is in `fix-f1/`: staged diffs (`staged-changes.diff`), test diffs (`test-changes.diff`), md5s, logs, seeds and suite parity.
Nothing installed was changed. Every product change is a staged `.new-usagew2` copy in `/home/seyran/code/manage-agents`.

**Finding.** The weekly `PICK_MAIN_PACE` form read main's reset field with `endgame.hours_to`. That parser used the clock's year,
so on Dec 26 the field `Fri_Jan01_15:00` became Jan 1 2026. "+7 d while < 0" then landed a day short, because 365 mod 7 = 1:
the line read 77.0 instead of 73.

**Class.** The accounts.sh reset field (`%a_%b%d_%H:%M`, America/Los_Angeles, no year) had five parsers:
- `endgame.hours_to`: no year wrap. It feeds the endgame window (`inside`), usage-watch freezes, accounts.sh and the pace line.
- `reset_fresh.reset_epoch`: had its own 183-day wrap on top of hours_to.
- `pick-claude-account.sh:638`: the hours to the weekly reset used for the pace order. It had its own strptime with `now.year`.
- `tools-local/burndown.py:1651`: the account table. It hard-coded the year 2026.
- `tools-local/review-ab-rule.py:137`: token binding. It had its own strptime, read the PT field as UTC (7-8 h early), had a
  one-way wrap, and crashed on a Feb29 field.

**Fix (one owner).** `endgame.hours_to` is the one parser. It tries the clock's year and the years on each side, and keeps the
reading nearest the clock. A Feb29 field is read in the leap year among the three. Hours are wall-clock hours in TZ, as before.
The other four now read the field only through it:
- `reset_epoch` drops its own wrap.
- Picker line 638 reuses `hw`, which line 512 already computes with `endgame.hours_to(r2, now)`. Unreadable still means 168 h.
- burndown uses `NOW + hours_to(rs, NOW)`.
- review-ab-rule uses `now + hours_to(f[6], now)`. This also fixes its zone; burndown's adv0031 ruling already read the field as PT.

`pace_line` keeps its code and only gains a comment, so `inbox-wait.sh` still execs it alone.

**Guard.** `OneParser.test_only_endgame_parses_the_reset_field` scans every live `*.sh`/`*.py` of manage-agents and tools-local
(the files under test take their live copies' place). It fails on any `strptime` of the `%b%d` form outside endgame.py. That
scan is how burndown and review-ab-rule were found; the review's sweep named only endgame.py:63 and picker:638.

**Tests** (`fix-f1/*.log`):
- `test_usage_reset_fresh.py`: 28/28 on the staged copies. 6 fail on the installed ones, all new:
  - `WeeklyPace.test_december_clock_line_73`: the probe, as a pick.
  - `WeeklyPace.test_december_week_every_day`: the exec'd def, Dec 25 to 31.
  - `YearWrap.test_hours_to_nearest_year`.
  - `YearWrap.test_endgame_window_across_new_year`: endgame.py:63.
  - `PickOrderYearWrap.test_nearer_reset_first_across_new_year`: picker:638.
  - `OneParser.test_only_endgame_parses_the_reset_field`.
  - `YearWrap.test_reset_fresh_across_new_year` passes on both. It is the control: reset_fresh had its own wrap.
- `test_review_ab_rule.py`: 22/22 staged. On installed, only the new `test_token_binding_reset_field_is_pacific_and_year_safe`
  fails (136.0 h instead of 144.0 h: the zone).
  - The fixture's reset fields are now written in PT for the same instants (10:00Z, 16:00Z), so the existing assertions keep
    their meaning.
  - `REVIEW_AB_RULE_SCRIPT` and `EG_SCRIPT` select the copies under test.
- `test_burndown.py`: the new `test_account_table_reset_year_nearest_now` fails on installed (Jan 1 2026) and passes staged. The
  11 other failing ids are the same on both: pre-existing, not this item.
- Suite parity (`fix-f1/existing-suites.txt`): 44 tools-local suites that read endgame, the picker, reset_fresh, burndown or
  review-ab-rule were run on installed and staged copies.
  - 41 have the same failing ids on both.
  - The 3 that differ are the suites above, and they differ only by the new tests.
  - `test_omission_seq_read` and `test_oseq_pathf_marker` stop on missing `.new-oseq`/`.new-pathf` files on both: pre-existing.
- **PROBE F1:** prints 77.0 and exits 1 before the fix (live files). Run with `PICK_SCRIPT=…new-usagew2` and its
  `sys.path` entry pointed at a copy of `endgame.py.new-usagew2`, it prints 73.0 and exits 0. The probe hard-codes the live
  tools-local for `import endgame`, so it passes unmodified once the staged files are installed.

**Seeded bugs** (`fix-f1/seeded-bugs.json`; each on a /tmp copy, all caught, copies deleted):

| id | file | change | failing tests |
|---|---|---|---|
| S10 | tools-local/endgame.py.new-usagew2 (Python) | only the clock's year | 7 (YearWrap.*, WeeklyPace.test_december_*, PickOrderYearWrap, Helper.test_year_wrap) |
| S11 | pick-claude-account.sh.new-usagew2 (Python) | line 638 back to its own year-less strptime | OneParser, PickOrderYearWrap |
| S12 | tools-local/reset_fresh.py.new-usagew2 (Python) | own year-less strptime | Helper.test_year_wrap, OneParser, YearWrap.test_reset_fresh_across_new_year |
| S13 | tools-local/burndown.py.new-usagew2 (Python) | year 2026 again | test_account_table_reset_year_nearest_now (+ the 11 pre-existing) |
| S14 | tools-local/review-ab-rule.py.new-usagew2 (Python) | field read as UTC | test_token_binding_reset_field_is_pacific_and_year_safe |

**Install (for the decider; nothing below has been run).** No restart is needed: every caller runs endgame.py, reset_fresh.py,
burndown.py and review-ab-rule.py in a fresh `python3`, and the picker runs fresh on each call.

```
cd /home/seyran/code/manage-agents; S=.new-usagew2
md5sum tools-local/endgame.py tools-local/reset_fresh.py pick-claude-account.sh tools-local/burndown.py tools-local/review-ab-rule.py   # expect the first 5 rows of fix-f1/md5.txt; any other: rebase the .new-usagew2 first
E="PICK_SCRIPT=$PWD/pick-claude-account.sh$S RESET_FRESH_SCRIPT=$PWD/tools-local/reset_fresh.py$S EG_SCRIPT=$PWD/tools-local/endgame.py$S BURNDOWN_SCRIPT=$PWD/tools-local/burndown.py$S REVIEW_AB_RULE_SCRIPT=$PWD/tools-local/review-ab-rule.py$S"
env $E python3 -I tools-local/test_usage_reset_fresh.py; env $E python3 -I tools-local/test_review_ab_rule.py   # 28 OK, 22 OK
env $E python3 -I tools-local/test_burndown.py 2>&1 | grep -E '^(FAIL|ERROR):'   # the 11 ids of fix-f1/test_burndown-staged.log
ts=$(date -u +%Y%m%dT%H%MZ); for f in tools-local/endgame.py tools-local/reset_fresh.py pick-claude-account.sh tools-local/burndown.py tools-local/review-ab-rule.py; do cp -p $f $f.bak-$ts-usagew2; done
zsh -n pick-claude-account.sh$S && for f in tools-local/endgame.py tools-local/reset_fresh.py pick-claude-account.sh tools-local/burndown.py tools-local/review-ab-rule.py; do mv $f$S $f; done
python3 -I tools-local/test_usage_reset_fresh.py; python3 -I tools-local/test_review_ab_rule.py   # now on the installed files: 28 OK, 22 OK
```

Rollback: mv each `.bak-$ts-usagew2` back. The three test files were edited in place. Their previous versions are
`tools-local/test_{usage_reset_fresh,review_ab_rule,burndown}.py.bak-20261120T1930Z-usagew2`.

**Notes.**
- **For the DRI:** `pick-claude-account.sh.new-fmw` (staged 17:21Z) predates both the usagew `pace_line` hunk and this
  line-638 hunk. Whichever is installed second must carry the other's hunks.
- F5 (C): the opening summary above answers it.
- F6 (C) is not changed. The wall-clock hours across a DST change are the parser's existing meaning. The test fixtures of
  about 20 picker suites build their fields with wall-clock `timedelta`, so moving to elapsed hours is its own item.
- F2, F3, F4 and F7 (C) are not filed and not changed.

SIZE (fix): 5 product files, +31 -24 lines. Tests: +134 -8 lines in 3 files.
