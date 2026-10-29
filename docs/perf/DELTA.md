# User-visible deltas: scale-admission-profile

Base: `471ccc7e4` (main). The route's stdout and answer are unchanged; the only
new output is opt-in diagnostic stderr. `admission-profile-20261029.md` records
the measurements and saved evidence.

| Delta | Before | After | Test or evidence | Ruling |
|---|---|---|---|---|
| `VE_READINGS_STAGE_TIMES=1` exposes measurement lines on stderr; unset or `=0` stays silent | no stage lines | one JSON line per sampled stage call, including both admissions of split non-W2 mains | `test_readings_stage_times_are_silent_by_default`, `test_readings_stage_times_are_json_lines_for_each_stage`, `test_readings_stage_times_do_not_change_the_answer`, `test_normal_client_profiles_registered_and_reused_handle`, `test_split_non_w2_main_records_fallback_admission`, `test_saved_non_w2_prefixes_record_fallback_admission`, `test_saved_stage_table_uses_all_calls_in_each_run` | SIGNED by DRI (reviews/dri-decisions-20261028-scale.md, item 1: approved measurement with no meaning change) |
| Trusted Lean V grows by one line in `lean/Serve.lean`; K and S +0; `lean/VE/Service/ReadingsAdmissionProfile.lean` adds measurement checks classified T, trusted +0 | V 43,551 at main tree | V 43,552; `tools/trust_map.py --check` passes with allowance | `test_readings_stage_times_are_silent_by_default` fails under a flipped env gate; `docs/perf/trust-mutants.json` (zero applicable definitions); `tools/trust_map.py --check` | R16 (DRI-RULINGS.md), at most 150 lines, per-file count and ties follow-up |
