# JT-E1r F1 fix report

Status: F1 fixed in `2901a39fe`; no model calls or push.
Changed: durable dispatch journal, reported-usage accounting, and restart validation in the experiment runner.
Open items: JT-3 wording revision and human reader audit remain separate; no DRI signature is reserved.
Evidence: original F1 probe failed before the fix and passed after it; 28 focused tests, Lean build, and Lean audit passed.

## Finding

F1 -> save each dispatch before execution, charge failed calls at least their reported CW, save every returned outcome before testing the cap, and stop on unknown usage -> `tests/test_jt_e1r.py::test_failed_call_charges_reported_usage_above_reserve`, `::test_every_dispatched_outcome_is_saved_and_restart_is_blocked`, `::test_interrupted_call_keeps_durable_dispatch_record` -> `2901a39fe`.

The tests mock the CLI. They cover both arms and all three answer classes for reported failure usage, plus timeout with and without partial usage, oversized output and record, invalid model/result/usage/wrapper, successful and failed reported-cap overflow, and interruption before completion. Restart tests assert that no second call is dispatched. Saved-result mutations check answer, model, counter type, charge, and dispatch state. The original 80 successful records still score 20/40 per arm at 1,191,512 CW; no saved result was edited.

Two seeded Python faults failed their named tests and were restored: replacing `max(RESERVE_CW, reported)` with `RESERVE_CW` in `runner.py` failed `test_failed_call_charges_reported_usage_above_reserve` for both arms; removing the pre-call `save_record` failed `test_interrupted_call_keeps_durable_dispatch_record`.

There is no user-visible VE product delta: only this research runner and its tests changed. No DELTA row or standing-ruling signature applies. The three known-red tests on main listed in `/home/seyran/code/manage-agents/main-known-red.txt` are outside this fix and were not edited.
