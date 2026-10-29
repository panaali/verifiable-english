# JT-E1 correction report

Status: **INVALID** for the JT-3 gate; the earlier go-ahead is withdrawn.
HEAD: the committed correction on `feature/jt-e1`; no push.
Changed: archive the invalid comparison, gate future runs on live display, and specify fresh `jt-e1b` measurement.
Open items: JT-3 wording is gated on `jt-e1b`; no DRI signature is reserved.
Model calls: none in this correction; the 80 original raw records are unchanged.

## Review findings

| Finding | Correction | Regression |
|---|---|---|
| F1 | The frozen runner can no longer launch a call from invented answer lines. It requires captured live renderer display before any call, then stops because these 40 items have already been seen. The declaration preview names every named decider, including all seven conditional controls. `jt-e1b` requires actual output for every constructor in both arms. | `test_conditional_control_decider_is_visible_for_every_named_row`, `test_missing_or_inconsistent_live_display_cannot_launch_study` |
| F2 | Every rejected-template preview uses the identifier fallback in both arms. The capture validator rejects unequal arms for such a row. `jt-e1b` will enforce this on its fresh frame. | `test_frozen_frame_and_two_arm_preview`, `test_missing_or_inconsistent_live_display_cannot_launch_study` |

The original 16/40 and 37/40 counts, zero recorded critical misreadings, 80 calls, and 205,437 CW remain in `RESULTS.md` as descriptive evidence of the invalid study. They are not gate results. `PRE-REGISTRATION.md` and `items.tsv` remain frozen; the invalidity arose from the runner's displayed lines and cannot be repaired by rescoring the same answers. The original build report is available in commit `31761f9dd`.

## Delta and scope

No VE product text, diagnostic, verdict, wire response, Lean statement, or Rust behavior changed. The research report's interpretation changed from go-ahead to invalid; that is correction of an unsupported claim, not a product delta. There is no DELTA table row. The pending `jt-e1b` study is a separate item and makes no calls in this branch.

## Verification

Both executable review probes failed before the fix and passed afterward. The regression tests exercise all 40 rows and all three answer kinds, including the seven named conditional controls and all 20 rejected-template rows. `tests/test_jt_e1.py` passed (5), `lake build` passed (1,157 jobs), and `python3 lean/audit.py` passed (666 source files, 7,338 declarations). The selected run executed 153 units: 152 exited 0; `tests/test_trust_mutants.py::test_a_guard_over_the_empty_list_leaves_survivors` failed because two printed `SURVIVOR` records joined on one line (20 lines for 21 evidence records). The isolated failed test passed (1) on a VM rerun through `mac-pytest.sh` with a writable UV cache and one worker. No other selected tests were rerun. The full release gate was not run, as directed for this branch.

The three failures listed in `/home/seyran/code/manage-agents/main-known-red.txt` are pre-existing separate items: the two sub-tick Lean service deadline cases and `test_review_fix_commit_chain_and_final_gate_target`. None was edited here.

Seeded Python bugs in `runner.py` were planted one at a time and restored: omitting the named decider failed `test_conditional_control_decider_is_visible_for_every_named_row`; bypassing rejected-template fallback failed `test_frozen_frame_and_two_arm_preview`. Each failed at the relevant assertion, then the unmutated module passed. No Lean or Rust product code changed.
