# tarch-cutoff: answer-level early cutoff, an R1 experiment (plan rank 8)

<!-- status -->

The [delta](DELTA.md) records no VE user-visible change: this batch changes developer test
selection and recording only. Nothing here is used by `tools/gate.py` (R2), the merge train or the
nightlies (R3); `tests/test_answer_cutoff.py::test_the_gate_and_the_maps_never_reach_the_cutoff`
checks that the gate and the map tools import neither module.

Plan: reviews/test-architecture-2026-10-14.md draft 2, section 3.5 "Answer-level early cutoff is an
R1 experiment", rank 8; Astra's re-check point 6 (ADOPT WITH CHANGES), whose order this batch
follows: first the activation evidence for ts-B2's per-mode narrowing, then request-level recording.

## What the plan asked, and where it is

| Plan or directive line | Owner | Delivered | Evidence |
|---|---|---|---|
| (1) 26 behavioural Lean seeds, each caught by a test the narrowed selection keeps | AGENT | `seeds.json` (46 candidates), `seeds.py`; each seed planted in a Lean runner, `ve_service` rebuilt alone, catching tests run, a catch re-checked with the source restored and the unseeded binary as control (`seeds.py verify`) | `evidence/seeds.json`; table below |
| (1) 10 contemporaneous shadow comparisons of the narrowed selection against the full run on real Lean changes | AGENT | `changes.json` (3 newest Lean merges, 7 Lean branches in flight on 2026-10-16), `measure.py --full-suite` (the gate's collection on ve-mac-1), `shadow.py` | `evidence/shadow.json`; table below |
| (1) Turn ts-B2's narrowing on only for R1, and only if every seed is caught and no comparison has a failure outside the selection | AGENT | <!-- activation --> | <!-- activation-test --> |
| (2) Record per test unit the `ve_service` request keys it sent | AGENT | `tools/test_map_recorder.py` (opt-in, `VE_TESTMAP_REQUESTS`; the coverage map is unchanged), `tools/answer_cutoff.py record` | `tests/test_answer_cutoff.py::test_recorder_records_each_case_the_client_sent`, `::test_request_records_leave_the_map_as_it_was`, `::test_a_child_and_a_nested_recording_send_for_the_outer_unit`; `evidence/recording.json` |
| (2) Select the union of today's selection for every input but `ve_service`'s answers and the files that sent a request whose answer changed | AGENT | `tools/answer_cutoff.py` (`answers` rule), `tools/answer_replay.py` (replay and diff) | `::test_answers_rule_selects_changed_and_unknown_users_only` |
| (2) One-shot executables keep the module rule; lake/lean, Lean source readers and pins select by file | AGENT | only `select_tests.service_impact` is replaced; one-shot runners, `lake`/`lean`, file readers and pin data readers are today's rules | `::test_answers_rule_selects_changed_and_unknown_users_only` (the `ve_metered` runner stays selected), `::test_a_pin_change_selects_only_data_readers_when_the_new_build_is_pinned` |
| (2) A unit with no request recording, or with randomised inputs, is UNKNOWN and selected | AGENT | `answer_cutoff.unknown_units`, `randomised` | `::test_randomised_inputs_make_a_unit_unknown`, `::test_seeded_randomness_is_not_unknown`, `::test_service_uses_the_record_cannot_replay_make_the_unit_unknown`, `::test_a_unit_that_read_an_answer_the_base_build_changed_is_unknown` |
| (2) Measure against R2 for the Lean changes available (target 10); default off until the DRI reads it | AGENT, then HUMAN (DRI) | the same ten comparisons; `answers` is never a default | `evidence/shadow.json`; the DRI reads this report |
| Touch select_tests.py through one small, marked, opt-in hook | AGENT | `--cutoff RULE` and one call into `answer_cutoff.select` (`tools/select_tests.py`, "tarch-cutoff hook") | `::test_the_hook_passes_its_rule_and_is_off_by_default` |
| Never used by tools/gate.py, the merge train or the nightlies | AGENT | neither module is imported there | `::test_the_gate_and_the_maps_never_reach_the_cutoff` |
| Measure the effect before/after on the Mac | AGENT | selection sizes and their recorded Mac seconds per seed and per change; the recording's and the replays' cost | tables below |
| Full release gate on the committed final HEAD | EXTERNAL (chain) | run by the chain on the test runner, per the task | `gate-result.json` |

<!-- body -->
