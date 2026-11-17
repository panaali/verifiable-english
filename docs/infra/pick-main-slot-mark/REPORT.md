# pick-main-slot-mark: REPORT

- Status: fix round done (review F1, class B); INSTALL WAITS FOR DECIDER READ. No DRI signature needed, no DELTA row reserved.
- HEAD: the evidence commit is 63dfdea2cc (fix round on 4b44f472fc); the staged files are pinned by `md5.txt`.
- Changed: the rank-1 critical slot is now the 3rd main slot at most (`0 < mcap == running < 3`): a cap of 3 (5-h < 40) no longer gives a 4th session.
- Tests: 18/18 on the staged picker, 18/18 on both merged copies, 10/10 distinct seeds caught; the VE selected run on 652322f096: 10 units, 0 failed (`run-selected.log`).
- Open: none. Not run: the full gate and the full suite (the merge train runs them); no Lean, Python-package or Rust code changed in the VE tree.

INSTALL WAITS FOR DECIDER READ (no DELTA row reserved; no Lean, Python, Rust or trust-base change in the VE tree).

## Fix round (review pick-main-slot-mark-review.final.md)

- **F1 (B): the extra slot could become a 4th main session.** Fix: the gate is `0 < mcap == int(running.get(d, 0)) < 3`
  (`pick-claude-account.sh.new-pickw`, the r1x line in the main worker cap check). Decision item 3 grants "a 3rd main slot".
  The class: any cap at which `mcap + 1` passes 3 (a cap of 3 at 5-h < 40, or `PICK_MAIN_WORKERS` >= 4) and any grant more than
  one over the cap. Regression tests: `CritFallbackSlot.test_rank1_slot_never_a_fourth_main_session` (PROBE F1: 5-h 30, 3 running
  -> refused with the plain cap reason `main worker cap 3/3`, and the waiting-main marker is written) and
  `CritFallbackSlot.test_rank1_slot_sweep_never_past_the_third_main_session`. The sweep covers `PICK_MAIN_WORKERS` 1, 2, 3, 4 and 6
  at 5-h 30 and 45, with main at its cap and one over it. The slot is granted exactly when main runs at its cap and the cap
  is under 3; otherwise the pick is refused and the row is marked. `test_rank1_slot_only_one_over_the_cap` also covers cap 1
  with 2 running. PROBE F1: exit 1 before the fix, exit 0 after it. Both new tests fail on the pre-fix staged picker
  (`run-prefix-f1.log`: failures=2).
- **F2 (C, noted):** the duplicate seed is replaced by a distinct one-row-marker mutant (`ok, why_ = r1hold()` -> `True, ""`).
  All 10 seeds are distinct.
- **F3 (C, noted):** self-review item 11 now lists only the fail-closed cases the cited tests exercise.
- **F4 (C, noted):** this REPORT now opens with the 5-line summary.

Row: pick-main-slot-mark (infra; PLACEMENT class: the account picker). Decision: reviews/dri-decisions-20261117-pf16-main-slot.md
item 3. INSTALL READ sent 2026-11-17T18:00Z: inbox/dri/20261117T180006Z-pick-main-slot-mark-158532.md.

## What changed (staged, not installed)

Staged on the INSTALLED picker (md5 in `md5.txt`; installed == `.new-oseqmain`, oseq-opus-off-main installed 13:05 local file time):

- `/home/seyran/code/manage-agents/pick-claude-account.sh.new-pickw`
- `/home/seyran/code/manage-agents/tools-local/test_pick_main_rank.py.new-pickw`

Full diff: `staged-changes.diff`. Syntax: `syntax.txt` (`zsh -n` clean; the embedded `pick()` Python and the test compile).

1. **cffall marks on a cap refusal.** When the critical fallback's `PICK_CRIT_MAIN=1` pick fails and its reasons contain
   `main: main worker cap`, cffall runs `mmark mark` (pick-waiting-main/<row>; pick_critical.mainmark keeps ranks 1-3 only).
   Before, only the first pick's reason was checked, so a caller whose first pick held main out (`held out (PICK_AVOID)`,
   run-codex.sh's own main) never marked: the pf-f16-without-fix case of 03:28Z.
2. **Rank-1 extra main slot.** In the main worker cap check of `pick()`: when the caller is rank 1 (`PICK_R1_`, Nov 23 path,
   never a coordinator) AND the pick is the critical fallback (`PICK_CRIT_MAIN`) AND main runs exactly `mcap` sessions
   (`0 < mcap`), main is admitted only by the existing rank-1 rule `r1ok(w)`: main week <= PICK_MAIN_PACE line - 4, the 300-min
   week rise < 5, and the one-row holder marker `PICK_R1_MARKER` ($PCF/pick-main-rank1). A grant this call already took
   (5-h-unknown refusals above) is reused, not taken twice; and only while main runs fewer than 3 sessions (fix round F1: the
   slot is "a 3rd main slot", never a 4th); a granted slot sets `r1d`, so the give-back at the end of `pick()`
   keeps the marker when main is picked and returns it when it is not. Refused: the old reason
   `main worker cap n/mcap (...)` plus `, rank-1 critical slot <mcap+1>: <rule reason>` (a comma, not `;`, so cffall's
   reason parsing is unchanged), so (1) marks the row.

Conservative choices taken (override rule 2, not asked):
- The extra slot uses the whole rank-1 rule `r1ok` (pace line - 4 AND the 300-min rise < 5 AND the one-row marker), not the
  pace bound alone: one owner of the rank-1 bound, and the narrower reading.
- Exactly one over the cap (`running == mcap`), and the slot is the 3rd main slot at most (`running < 3`, decision item 3
  "may also take a 3rd main slot"; fix round F1). Never at taper 0 (`0 < mcap`): the 5-h >= 55 stop stays absolute.
- Only the critical fallback pick of a rank-1 row; a rank-1 row's ordinary pick keeps the cap.

## Tests (failing first)

Command: `python3 -I tools-local/test_pick_main_rank.py.new-pickw` (PICK_SCRIPT unset = installed picker) and
`PICK_SCRIPT=$PWD/pick-claude-account.sh.new-pickw python3 -I tools-local/test_pick_main_rank.py.new-pickw`, in
/home/seyran/code/manage-agents.

- Installed picker: `run-installed.log`: Ran 18, FAILED (failures=5, errors=1): the 6 positive cases
  test_crit_fallback_cap_refusal_marks, test_crit_fallback_cap_refusal_marks_rank3, test_rank1_crit_fallback_third_slot,
  test_rank1_slot_one_row_at_a_time, test_rank1_slot_refused_over_pace_minus_4 and the sweep
  test_rank1_slot_sweep_never_past_the_third_main_session (its granted cases). The installed picker has no extra slot, so the
  F1 refusal test test_rank1_slot_never_a_fourth_main_session passes there. It fails on the pre-fix staged picker instead
  (`run-prefix-f1.log`, together with the sweep: failures=2).
- Staged picker: `run-staged.log`: Ran 18, OK.
- The 8 old MainRank tests are unchanged (the helpers moved to a base class `RankBase`, and `pick()` takes `**extra` env);
  no test removed or renamed.

New class CritFallbackSlot (both directions):
- accept/mark: test_crit_fallback_cap_refusal_marks (the MEASURED case; then a rank-4 kb-4b is held off the freed slot),
  test_crit_fallback_cap_refusal_marks_rank3, test_rank1_crit_fallback_third_slot (incl. the boundary week = line - 4 = 56).
- refuse/no mark: test_crit_fallback_other_refusal_or_rank4_no_mark (5-h bound refusal: no marker; rank 4: no marker),
  test_rank1_slot_only_one_over_the_cap (mcap + 1 sessions running refused, at cap 2 and at cap 1),
  test_rank1_slot_never_a_fourth_main_session (cap 3 at 5-h 30, 3 running: refused, marked; F1),
  test_rank1_slot_sweep_never_past_the_third_main_session (both directions over PICK_MAIN_WORKERS 1-6 x 5-h 30/45; F1),
  test_rank1_slot_refused_over_pace_minus_4 (week 57; no pace line),
  test_rank1_slot_one_row_at_a_time (another live rank-1 row holds PICK_R1_MARKER), test_slot_only_for_rank1_critical_fallback
  (rank 3 fallback; rank-1 ordinary pick).

Regression, every `tools-local/test_pick_*.py` on staged and installed (`run-regression.log`): all OK on both, except
test_pick_main5h_nowindow: FAILED (failures=11) on BOTH: those are the failing-first tests of the staged, not yet installed
`.new-m5h2` item (main5h-build-1117), not this change.

Regression rerun on the fixed staged picker (fix round): same results as before, so the installed column is from the first round
(the installed md5 is unchanged, `md5.txt`).

VE selected run on commit 652322f096 (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`): exit 0, 10 units,
0 failed (`run-selected.log`; ran on the VM). The same log records `lake build` (it completed) and `python3 lean/audit.py` (PASS). The VE tree changes are docs under this directory only.

## Seeded bugs (`seeded-bugs.json`, produced by `seed_run.py`)

Command: `python3 -I docs/infra/pick-main-slot-mark/seed_run.py /home/seyran/code/manage-agents docs/infra/pick-main-slot-mark/seeded-bugs.json`.
Each seed mutates a /tmp copy of `pick-claude-account.sh.new-pickw`; the named test passes on the clean copy (clean_rc 0) and
fails on the mutant. 10/10 caught, 10 distinct mutants. Languages: shell (the cffall line) and the picker's embedded Python. No VE product code changed,
so no Lean, Python-package or Rust seed applies.

| seed | file | failing test |
|---|---|---|
| cffall cap refusal does not mark | pick-claude-account.sh.new-pickw (shell) | CritFallbackSlot.test_crit_fallback_cap_refusal_marks |
| cffall marks on any refusal | pick-claude-account.sh.new-pickw (shell) | CritFallbackSlot.test_crit_fallback_other_refusal_or_rank4_no_mark |
| no rank-1 extra slot | pick-claude-account.sh.new-pickw (embedded python) | CritFallbackSlot.test_rank1_crit_fallback_third_slot |
| extra slot not limited to mcap + 1 (`mcap <= running < 3`) | same | CritFallbackSlot.test_rank1_slot_only_one_over_the_cap |
| extra slot past the 3rd main session (bound dropped; F1) | same | CritFallbackSlot.test_rank1_slot_never_a_fourth_main_session |
| extra slot past the 3rd main session (`< 4`, off by one; F1) | same | CritFallbackSlot.test_rank1_slot_sweep_never_past_the_third_main_session |
| extra slot skips the rank-1 rule (pace - 4) | same | CritFallbackSlot.test_rank1_slot_refused_over_pace_minus_4 |
| extra slot skips the one-row marker only (`r1hold` -> True; F2) | same | CritFallbackSlot.test_rank1_slot_one_row_at_a_time |
| extra slot not only for the critical fallback | same | CritFallbackSlot.test_slot_only_for_rank1_critical_fallback |
| granted slot not recorded (r1d): marker given back | same | CritFallbackSlot.test_rank1_crit_fallback_third_slot |

## Overlap with other staged picker copies (`overlap.txt`)

`.new-m5h2` (main5h-build-1117) and `.new-placec` both edit the mcap line (installed line 472) and the cffall `mw/mf` regex
(line 629). This change touches neither line (it adds lines after 473 and before cffall's last line). `git merge-file` of this
change into each copy: 0 conflicts, `zsh -n` clean, and test_pick_main_rank.py.new-pickw passes 18/18 on both merged copies (fix round rerun; each merged copy has the `< 3` gate line once).
Whoever installs second must re-stage on the then-installed file (merge-file as in overlap.txt) and rerun the tests.
Interplay to know: under `.new-m5h2`'s tripwire (`mtrip`), mcap is 2; a rank-1 critical fallback may still take a 3rd slot,
but only through r1ok (pace line - 4, rise < 5, one row), and never a 4th (the `< 3` bound holds under any cap).

## Install commands (for the decider, after the READ)

```
cd /home/seyran/code/manage-agents
cp -p pick-claude-account.sh pick-claude-account.sh.bak-20261117-pickw
cp -p tools-local/test_pick_main_rank.py tools-local/test_pick_main_rank.py.bak-20261117-pickw
mv pick-claude-account.sh.new-pickw pick-claude-account.sh
mv tools-local/test_pick_main_rank.py.new-pickw tools-local/test_pick_main_rank.py
python3 -I tools-local/test_pick_main_rank.py
```

No restart: the picker runs per call (no svc-* loop holds it); pickers already waiting keep the code they loaded (mv swaps the
inode) and take the new code on their next call. Check first that `md5sum pick-claude-account.sh` still matches the installed
line in `md5.txt`; if another item was installed in between, re-stage by `git merge-file` (see above) instead of mv.

## SIZE

SIZE: 15 product (picker), 133 tests (added lines in `staged-changes.diff`), 58 other hand-written lines (seed_run.py) plus
this REPORT. The fix round changed 1 product line (the gate) and its comment.

MEASURED (delegate-cw): `python3 -I tools-local/delegate-cw.py` printed "delegate-cw: own session not found (needs VE_STEP and
CLAUDE_CONFIG_DIR from dri-delegate.sh, or a transcript path)" both times it ran (this session was not started by dri-delegate.sh).

## Notes for the DRI

- Since pick-rcx-main-pace (installed 11:42Z), a run-codex.sh caller's first pick already lifts its own PICK_AVOID main while
  week <= pace line - 4, so there the first pick sees the cap and marks. The cffall mark matters whenever main week is between
  the line - 4 and the critical bound 60, or there is no pace line (as for pf-f16 at 03:28Z); the tests use the latter.
- `test_pick_main5h_nowindow` fails on the installed picker by design until `.new-m5h2` is installed (not this item).
- No FOLLOW-UP lines: both deliverables are built.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer or relay changed (only the account picker in manage-agents).
2. PASS: both spec lines delivered: cffall mark (test_crit_fallback_cap_refusal_marks), rank-1 mcap+1 at pace - 4 via
   PICK_R1_MARKER (test_rank1_crit_fallback_third_slot, test_rank1_slot_refused_over_pace_minus_4, test_rank1_slot_one_row_at_a_time);
   files other staged items edit: named under Overlap (overlap.txt).
3. PASS: 10/10 distinct seeded bugs caught (seeded-bugs.json); 6 new tests fail on the installed picker (run-installed.log);
   the F1 tests fail on the pre-fix staged picker (run-prefix-f1.log).
4. N.A.: no Python/Lean/Rust checker logic changed.
5. N.A.: no R8 binding.
6. PASS: no VE product code; the chain's gate runs on the final HEAD; evidence files are saved under this directory (md5.txt pins the staged files).
7. PASS: no DELTA row needed or reserved (no user-visible checker change).
8. N.A.: no user-visible VE change, so no DELTA row.
9. N.A.: no file under the VE test-selection map changed (docs only in the VE tree).
10. N.A.: no Lean statement.
11. PASS: fail closed, each case with the test that exercises it: no pace line and week over the line - 4
    (test_rank1_slot_refused_over_pace_minus_4), a live other rank-1 holder (test_rank1_slot_one_row_at_a_time), running > mcap
    (test_rank1_slot_only_one_over_the_cap), a 4th main session (test_rank1_slot_never_a_fourth_main_session and the sweep).
    Not exercised here: an unknown week trend (r1ok's own tests cover it), and mcap 0, which the critical fallback's
    5-h < 50 bound rules out (taper 0 needs 5-h >= 55); tests
    use no sleep (subprocess runs only).
12. N.A.: no VE CPU path; the picker adds no new subprocess (r1ok runs only on a rank-1 critical fallback at the cap).
13. N.A.: no test removed or renamed (MainRank keeps its 8 tests; run-staged.log Ran 18 = 8 + 10).
14. PASS: both directions per check (list under Tests); each claim cites a log in this directory; spec re-read: "cffall: when
    the PICK_CRIT_MAIN pick is refused with 'main: main worker cap', run mmark mark" matches the staged cffall line; "a rank-1
    (Nov 23 path) critical fallback gets mcap+1 ... while main week <= PICK_MAIN_PACE line - 4, one row at a time via
    PICK_R1_MARKER" matches the r1x gate (narrower: also the rise < 5 of r1ok, recorded above).
15. PASS: no overclaim (the universal words above each name a test or log); no deliverable cut; every new check has a seed
    (seeded-bugs.json); limits N.A. (no decoded input).
