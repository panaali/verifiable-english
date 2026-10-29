# RSP run loop recheck 1 fix

Status: F4 fixed; no open A/B finding or DRI signature requested.
HEAD: implementation commit `407d322c3` on `infra/usecase-rsp-run`; this report follows it.
Scope: N1 counterfactual classification and saved comparison; the frozen key and scored answers are unchanged.
Checks: original F4 probe, six focused regressions, 47 selected units, `lake build` and `lean/audit.py` passed.
Known red on main: the three IDs in `main-known-red.txt` were not edited or repaired here.

## Finding

- F4 -> each rule header explicitly labels whether N1 supplies its commitment reading; the counterfactual removes all RS0 rules, including clauses that inherit “will” from their context. The regenerated unscored comparison now includes B-INTD/INSCOPE, K2, K4 and K22a as `ALL` with N1 and `NONE` without it -> `test_rsp_n1_classification_is_explicit_for_every_rule`, `test_rsp_n1_prediction_removes_inherited_commitments` (four cases), `test_rsp_each_narrowing_has_an_unscored_counterfactual` -> `407d322c3`.

The original `PROBE F4` failed before the fix and passed after it. The N1 variant changes 46 cells, up from 42; N2 and N3 still change 2 and 1. The scored baseline remains 111/126 with 15 faithful undecided rows. This corrects an unscored section 9 comparison, with no VE product verdict or frozen-key delta, so there is no DELTA ruling row. Conflict claims about the source remain candidates under signed standing ruling R14 (`DRI-RULINGS.md`); the separate source check and `uc-audit` remain deferred.

## Seeded failure

Temporarily retaining `f9-public` in the N1 variant in `usecases/anthropic-rsp/run.py` made `test_rsp_n1_prediction_removes_inherited_commitments[K2-off_cycle_published]` fail (`ALL` instead of `NONE`). The temporary edit was restored, and the six focused regressions passed. No Lean or Rust product code changed, so no language-specific mutation was needed there.

## Verification

`lake build` completed 1,161 jobs. `lean/audit.py` passed for 668 source files and 7,428 theorem declarations. The foreground selected plan ran on the Mac against clean commit `407d322c3`: 47 units passed, 0 failed. No full suite or release gate was run, as requested.
