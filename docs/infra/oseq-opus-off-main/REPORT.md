# oseq-opus-off-main: the picker never returns main to a PICK_OSEQ_OPUS caller (reads-window Amendment K2)

- Row: oseq-opus-off-main (infra item, SERVICE class, install read). Decision: reviews/dri-ruling-reads-window-20261116.md
  Amendment K (K1: no Opus read job on main; K2: this row); orchestrator BATCH 125731Z item 1;
  reviews/dri-decisions-20261117-orch1257.md item 1; evidence reviews/main-share-challenge-20261117.md finding 1.
- Where the work is: `/home/seyran/code/manage-agents`, not this VE tree. Staged `pick-claude-account.sh.new-oseqmain`
  (7 added lines, `staged-changes.diff`; `zsh -n` clean) and the new suite `tools-local/test_pick_oseq_opus_main.py`
  (manage-agents commit `f9d57b58`). This VE branch holds only this report and its evidence; no VE product code (Lean,
  Python or Rust) changed, no DELTA rows, no signature (no Lean or trust-base change). Trust +0.
- Built on the live picker md5 `bbda0c0f74e7c23d272308133d3383b8` (rcxpace and released-main installed); staged md5
  `4cc8cce24dadf854674b8fdb5db8b898`. Review: MERGE (`oseq-opus-off-main-review-ov.final.md`, no A/B findings).
- Install state at this commit (2026-11-17): the live `pick-claude-account.sh` md5 is `4cc8cce2…`, the staged file's; the
  pre-install picker is `pick-claude-account.sh.bak-20261117oseqmain` (md5 `bbda0c0f…`). The install was not made by this
  builder.

SIZE: 7 product (pick-claude-account.sh), 180 tests (test_pick_oseq_opus_main.py, new), ~110 other hand-written lines (this
report, seed_run.py).

## Change

One early check at the top of `pick()`'s account loop, before the run-codex lift, the critical, released-row, rank-1,
`PICK_MGMT` and endgame rules: when `PICK_OSEQ_OPUS` is non-empty and the account is main (by name, or by its config dir
`claude-panaali2`), it is refused (`held out (PICK_OSEQ_OPUS: no Opus read job on main, reads-window Amendment K1)`) and no
released-row main waiter is recorded (`relwant = False`). With no other account the picker gives the usual no-pick
(PICK_NOWAIT: exit 1, empty stdout, one PICK_WHY line). `PICK_OSEQ_OPUS` unset or empty: unchanged.

## Tests (logs in this directory)

- `run-staged.log`: the new suite on the staged picker, 18/18 OK (`LIVE_PICK_SCRIPT` = the pre-install backup, so the
  unset cases compare with the pre-install picker).
- `run-pre-install.log`: the same suite on the pre-install picker: 14 of 18 FAIL (failing first). The 4 that pass check
  unchanged behaviour (I10 week-44 rule, unset = live).
- `run-regression.log`: test_endgame.py, every other tools-local/test_pick_*.py and test_codex_week_ceiling.sh with
  `PICK_SCRIPT`/`PICKER` pointed at the staged file: all pass.

## Seeded bugs (`seeded-bugs.json`, `seed_run.py`; shell with embedded Python, in `pick-claude-account.sh.new-oseqmain`)

Each mutates a /tmp copy; the named test FAILS on each (4 of 4 caught):

1. check removed -> `test_1_no_avoid_main_only`
2. check only when PICK_AVOID is empty -> `test_3_rcx_main_pace_lift`
3. config-dir match (`claude-panaali2`) dropped -> `test_1_config_dir_of_main`
4. `relwant = False` dropped -> `test_3_released_row`

## Runner check (read only)

`tools-local/omission-seq-read.py.new-oseqk` lines 988-990: both passes (`{'PICK_AVOID': 'main'}` then `{}`) drop every
inherited `PICK_*` and set `PICK_OSEQ_OPUS='1'` in the picker's environment. Confirmed; the runner was not edited (round 7
of dri-record-void-fix-f owns it). Its pass-2 note still says "main allowed" (wording only; Notes).

## Notes for the DRI

- Pre-review [commits] FAILed because the VE branch had 0 commits (the item lives in manage-agents); this report commit
  follows the docs/infra/tm-drain-vm1-idle precedent.
- The picker never reads `RCX_ALLOW_MAIN` (only run-codex.sh does), so `test_3_rcx_allow_main` sees the same input as
  `test_1_no_avoid_main_only`.
- The shell's yield branch (`relwait mark`) can still write a main waiter for a flagged caller with a released-row
  `PICK_ITEM`; the runner drops `PICK_ITEM`, so it cannot reach it (review F1, grade C).
