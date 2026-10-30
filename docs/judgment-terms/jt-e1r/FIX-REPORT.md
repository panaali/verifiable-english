# JT-E1r fix report

Status: F1 fixed in `2901a39fe`; F2 fixed in `528d24080` (DRI decision `dri-decisions-20261030-jt-e1r.md`, item 2); no model calls or push.
Changed: durable dispatch journal and reported-usage accounting (F1); `results()` scores a failed, fully accounted call as incorrect and non-critical and lists it under `errors` (F2).
Open items: JT-3 wording revision and human reader audit remain separate; no DRI signature is reserved.
Evidence: PROBE F2 failed before the fix (`RuntimeError: cannot score a failed reader call`) and passed after it; selected tests (104 units, 0 failed; run on the VM because the Mac runner had no free slot), Lean build and Lean audit passed; full gate not run (left to the merge train).

## Findings

F1 -> save each dispatch before execution, charge failed calls at least their reported CW, save every returned outcome before testing the cap, and stop on unknown usage -> `tests/test_jt_e1r.py::test_failed_call_charges_reported_usage_above_reserve`, `::test_every_dispatched_outcome_is_saved_and_restart_is_blocked`, `::test_interrupted_call_keeps_durable_dispatch_record` -> `2901a39fe`.

F2 -> every record goes through one `record_score()`: a record with `error` set is incorrect and never critical and its answer is never passed to `score()`; fewer than 80 records and any record `record_cw` rejects still raise; failed ids are returned as `errors`; `cw` still sums every record -> `tests/test_jt_e1r.py::test_failed_accounted_call_scores_incorrect_and_not_critical`, `::test_failed_call_answer_is_never_scored_or_critical`, `::test_failed_call_with_unknown_usage_still_blocks_scoring`, `::test_scoring_requires_all_80_records` -> `528d24080`.

The F2 tests read the 80 saved records and never edit them. The first test is the recheck's probe: U02-English failed gives English 19/40, `errors ["U02-english"]` and 1,201,615 CW. It then fails each of the 80 records in turn and checks that only its arm drops, by exactly that record's correctness. The second replaces `score()` with one that marks every answer correct and critical: the two failed records stay incorrect, stay out of `critical` and are never scored (78 calls). The unknown-usage cases are an unknown charge, missing usage, credit fallback, undercharge, a kept answer and a dispatch-only record. The frame, bars, wording and `PRE-REGISTRATION.md` are unchanged. The saved frame still scores 20/40 per arm with `errors []`.

Six seeded Python faults in `runner.py` were planted, each failed its named tests, and each was restored: putting back the raise on `error` (M1) failed the first two F2 tests; scoring the failed answer (M2) and marking a failed call critical (M3) failed `test_failed_call_answer_is_never_scored_or_critical`; marking a failed call correct (M4) failed both; dropping the `record_cw` loop (M5) failed all six `test_failed_call_with_unknown_usage_still_blocks_scoring` cases; relaxing the count check to `> 80` (M6) failed all three `test_scoring_requires_all_80_records` cases.

The F1 tests mock the CLI. They cover both arms and all three answer classes for reported failure usage, plus timeout with and without partial usage, oversized output and record, invalid model/result/usage/wrapper, successful and failed reported-cap overflow, and interruption before completion. Restart tests assert that no second call is dispatched. Saved-result mutations check answer, model, counter type, charge, and dispatch state. The original 80 successful records still score 20/40 per arm at 1,191,512 CW; no saved result was edited.

Two seeded Python faults failed their named tests and were restored: replacing `max(RESERVE_CW, reported)` with `RESERVE_CW` in `runner.py` failed `test_failed_call_charges_reported_usage_above_reserve` for both arms; removing the pre-call `save_record` failed `test_interrupted_call_keeps_durable_dispatch_record`.

There is no user-visible VE product delta: only this research runner and its tests changed, in F1 and F2. No DELTA row or standing-ruling signature applies. The three known-red tests on main listed in `/home/seyran/code/manage-agents/main-known-red.txt` are outside this fix and were not edited.
