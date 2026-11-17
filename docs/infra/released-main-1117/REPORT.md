# released-main-1117: a released row may take main, one at a time (INSTALL READ)

Status: STAGED, INSTALL WAITS FOR DECIDER READ (nothing installed). Live picker md5 at staging: aa89fe5b4eda1ea93c9afed5894e71c5.
Changed (outside this repo, staged only): pick-claude-account.sh.new-rel, tools-local/pick_critical.py.new-released-main, new tools-local/test_pick_released_main.py.
Open items: none for this item. No DELTA rows: no Lean or trust-base change, and no VE product code in this repo changed.
DRI signature needed: none. The install read goes to the decider (`msg.sh dri`).

SIZE: 155 product (picker +91/-4, pick_critical.py +64), 287 tests, 290 other hand-written lines (this REPORT, seeded-run.py).

## What it does

Decision: reviews/dri-decisions-20261117-released-main.md item 2. Task: prompts/task-released-main-1117.txt.

- Shell (`relmain`): when PICK_ITEM's row has links.released and its links.avoid names main, and the caller is not PICK_COORD,
  the row's own `main` is left out of PICK_AVOID. pick() gets `PICK_REL_=1`, which is never inherited and is not set in the
  cfhold probe. The row's other avoid entries are still added to PICK_AVOID.
- pick() (`relok`): main is admitted for such a caller only while all of these hold:
  - main week <= PICK_MAIN_PACE line - 4;
  - week_rise("main", 300) < 5;
  - the caller holds or can take the ONE released-row marker `$PCF/pick-main-released`, a separate file from the rank-1 marker.
    The marker reads `<row> <pid>[:<grants>] ...` and lists every live holder of the row. A second session of the row joins it.
    It is stale only when no listed pid lives. A give-back takes back only the grants of its own call. One lock covers the take
    and the give-back.
  - to take a FREE marker, no better-ranked released row is waiting.
  Otherwise main is refused: `held out (PICK_AVOID: row links.avoid main; released-row main rule: <why>)`.
- Path rows first: a live Nov 23 path waiting marker makes `ryield` refuse the released row on every account before pick() runs.
- Rank order (pick_critical.py (vi)): a released row that main refused only because main is taken writes
  `pick-waiting-relmain/<row>` (TTL PCF_TTL_S) and removes it on any pick. "Taken" means one of: the marker, a better-ranked
  waiter, the main worker cap, or a rank hold. A free marker goes to the best live waiter first, ordered by `(rank(),
  FEATURE-QUEUE.tsv rank (unqueued last), id)`.
- Unchanged: the stand-in guard, the main worker cap and its taper, the week caps, the pace line, the role hold, mhold,
  ryield, and cffall. ravoid itself is unchanged, so cffall's "row has links.avoid main" refusal still works. Any `main` that
  something else put in PICK_AVOID also stays: run-codex.sh's own, dri-* delegates, claude-resume-on-limit.sh.

## Tests (command, then output file in this directory)

- New suite, staged:
  `PICK_SCRIPT=pick-claude-account.sh.new-rel PCF_SCRIPT=tools-local/pick_critical.py.new-released-main python3 -I tools-local/test_pick_released_main.py`
  gives `Ran 16 tests ... OK` (run-staged-3.tail).
- Failing-first: the same suite on the LIVE picker and pick_critical.py fails all 16 (run-live-1.tail, with the FAIL list).
- The task's tests map to these test ids:
  - (1) `test_1_granted`, `test_1_boundary_pace_minus_4_and_rise_4_granted`, `test_1_continue_round_is_its_row`
  - (2) `test_2_pace_minus_3_avoided`
  - (3) `test_3_rise_5_avoided`
  - (4) `test_4_path_waiter_refuses`
  - (5) `test_5_second_released_row_avoided`
  - (6) `test_6_same_row_second_session_joins`, `test_6_same_holder_counts_grants`
  - (7) `test_7_dead_pid_marker_cleared`
  - (8) `test_8_cap_full_refused`
  - (9) `test_9_non_released_unchanged`
  - rank order: `test_rank_order`, `test_rank_order_stale_or_unreleased_waiter_ignored`, `test_rank_order_pick_critical_rank_first`
  - other avoid entries stay: `test_other_avoid_entries_stay`
- Kept suites on the staged picker and pick_critical (run-staged-suites.txt): test_pick_released_yield, test_pick_why,
  test_pick_critical, test_pick_crit_fallback, test_pick_main_rank, test_pick_tell, test_pick_longroom and test_pick_prefer
  all pass. Two suites fail on the staged picker exactly as they do on the LIVE picker (run-live-suites.txt):
  - test_pick_main5h_unknown: 4 `test_same_row_*` failures (F2 of pick-main-rank1; they pass once `.new-r1` is in, see below);
  - test_pick_mgmt: 7 failures.
  Both failure sets were already there and belong to their own rounds.
- Rebase readiness: `git merge-file` of `.new-rel` onto the other round's staged `pick-claude-account.sh.new-r1` (base: live)
  merges with no conflict and passes `zsh -n`. On that merge, test_pick_released_main, test_pick_main5h_unknown (all 30,
  including F2) and test_pick_released_yield all pass (run-merged-onto-new-r1.txt).
- Install order probe: the staged picker with the LIVE pick_critical.py (no (vi)) refuses main with
  `holder marker unreadable (AttributeError)`, which is fail-closed. Command:
  `PICK_SCRIPT=...new-rel python3 -I tools-local/test_pick_released_main.py ReleasedMain.test_1_granted`.

## Seeded bugs (seeded-bugs.json, seeded-run.log; each in a /tmp copy, staged files untouched, md5.txt)

Command: `python3 -I docs/infra/released-main-1117/seeded-run.py`. All 7 were CAUGHT.

| Seed | File | What it breaks | Test that fails |
|---|---|---|---|
| S1 | pick-claude-account.sh.new-rel | pace bound -4 becomes -3 | test_2_pace_minus_3_avoided |
| S2 | pick-claude-account.sh.new-rel | rise bound 5 becomes 6 | test_3_rise_5_avoided |
| S3 | pick-claude-account.sh.new-rel | give-back drops every holder | test_6_same_row_second_session_joins |
| S4 | pick-claude-account.sh.new-rel | dead pids kept | test_7_dead_pid_marker_cleared |
| S5 | pick-claude-account.sh.new-rel | another row joins the holder | test_5_second_released_row_avoided |
| S6 | pick-claude-account.sh.new-rel | shell keeps the row's main in PICK_AVOID | test_1_granted |
| S7 | tools-local/pick_critical.py.new-released-main | rank order reversed | test_rank_order |

The picker is zsh with embedded Python, and pick_critical.py is Python: every changed language has a seed. No Lean or Rust
was changed.

## Spec re-read

Each statement was checked against prompts/task-released-main-1117.txt (TASK bullets 1-3, TESTS line) and
reviews/dri-decisions-20261117-released-main.md item 2:

- "week % <= PICK_MAIN_PACE line - 4": `w > pl - 4` refuses.
- "week_rise (300 min) < 5": `wr[0] >= 5` refuses; an unknown rise refuses.
- "no live Nov 23 path waiting marker": ryield, before pick().
- "ONE released-row main marker (its own file, not the rank-1 marker; every live pid listed ...; give-back removes only its
  own pid)": pick-main-released. Grants are counted per pid, as in pick-main-rank1 F2.
- "better pick_critical.py / FEATURE-QUEUE.tsv rank takes the marker first": relmain_key.
- "Other avoid entries stay": `test_other_avoid_entries_stay`.

## Notes for the DRI

- Narrow reading taken (conservative; not asked). Only the row's OWN links.avoid main is lifted. A `main` that the caller
  already had in PICK_AVOID stays, and that includes run-codex.sh's own default (PICK_AVOID_RCX=main). As a result, the rule
  reaches the picker calls that feature-pipeline.sh makes directly (lines 22, 112, 144-145) but not run-codex.sh's Claude
  path. arch-decoder-measure's waiting run-codex picker (pid 3569643 in the digest) would still avoid main. Covering
  run-codex too would mean also dropping PICK_AVOID_RCX's main for an admitted released row; that is a separate decision.
- PICK_COORD callers of a released row: the rule is not applied, and main stays held out as today (narrower).
- The 5-h-unknown stand-in guard (PICK_MAIN_WEEKRISE 3/300) still runs before the rule. While main's 5-h is unknown, a
  released row therefore gets main only when the 5-h rise is < 3, not < 5. The rank-1 rule passes that guard; this one does not.
- Install order: pick_critical.py first, then the picker. In the other order the picker fails closed (the probe above).
- `pick_critical.queue_rank` reads FEATURE-QUEUE.tsv's rank column the way `burndown.queue_ranks` does. It is a small
  duplicate, kept so that pick_critical.py imports nothing more.
- Test hygiene in the rank-1 suite: when the F2 `test_same_row_*` tests fail (as they do on the live picker), their held
  callers stay blocked on a fifo. I killed 10 orphaned `zsh /tmp/pm5h-*/s*.sh` left by my baseline runs. The new suite kills
  its held callers in addCleanup.
- If the rank-1 round's `.new-r1` is installed first, `.new-rel` must be rebased onto it before the mv. The merge is clean
  (see above).

## Install (decider read; no service restart, the picker is read per call)

```
cd /home/seyran/code/manage-agents
md5sum pick-claude-account.sh tools-local/pick_critical.py   # must be aa89fe5b4eda1ea93c9afed5894e71c5 / 1c3349ac70d8940ae587fabaff3cbb14, else rebase first
cp -p tools-local/pick_critical.py tools-local/pick_critical.py.bak-20261117-relmain
cp -p pick-claude-account.sh pick-claude-account.sh.bak-20261117-relmain
mv tools-local/pick_critical.py.new-released-main tools-local/pick_critical.py
mv pick-claude-account.sh.new-rel pick-claude-account.sh
python3 -I tools-local/test_pick_released_main.py && python3 -I tools-local/test_pick_released_yield.py && python3 -I tools-local/test_pick_why.py
```

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed: N.A. (no Lean, no relay).
2. Deliverables built: PASS. Every task bullet and test (1)-(9) plus rank order is built (the test map above); nothing was cut.
3. Tests can fail: PASS. 7 seeded bugs caught (seeded-bugs.json), and all 16 tests fail on the live picker (run-live-1.tail).
4. Py/Lean/Rust agree: N.A.
5. R8 binding: N.A.
6. Gate evidence matches final HEAD: PASS. Run outputs are saved files; the chain runs the gate on the final HEAD.
7. No unsigned item: PASS. No DELTA rows (task: none).
8. DELTA: N.A. (no VE user-visible change).
9. Test selection: PASS. The picker header names `tools-local/test_pick_released_main.py`, the decision's "stays selected"
   condition.
10. Lean statements: N.A.
11. Fail closed: PASS. A missing pace line, a missing or stale log, a missing pick_critical (vi), no caller pid, or an
    unreadable marker all refuse main (test_2, test_3, the install-order probe).
12. No CPU/memory regression: PASS. Only released rows with avoid main call the extra code; it is one file lock and one
    directory scan per pick.
13. Removed tests: N.A. (none removed).
14. Both directions: PASS. Each refusal test also asserts the grant (test_1 vs test_2, test_3; test_4 grants after the
    marker is removed; test_9 grants rel-a in the same fixture).
15. Overclaim, silent cut, new checks can fail, limits: PASS. "Unchanged" claims cite run-staged-suites.txt; there is no cut;
    S1-S7; limits N.A.
