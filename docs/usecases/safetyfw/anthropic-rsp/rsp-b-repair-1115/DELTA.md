# rsp-b-repair-1115 delta

Base: `git merge-base HEAD main` (f97dd2d0c0). Public output of the RSP case: `usecases/anthropic-rsp/results.json`
is unchanged (`tests/test_safetyfw_usecases.py::test_rsp_run_recomputes_every_key_item_and_records_causes` recomputes
every keyed answer and compares it with the saved file; `::test_rsp_six_mutants_change_exactly_the_named_results`
likewise for the six mutants). The legend quotes (in_scope, full_review, public_notice, risk_reports_published,
goals_kept) and D3's description of v3.4's date add source text to descriptions and change no answer.

| Change | Before | After | Evidence | Ruling |
|---|---|---|---|---|
| F6's rule (`f6-strive-default`) has its own cause condition: the new predicate `revised_because_unable` ("simply because we are unable to achieve them") joins `goal_revised_less_ambitious` in the guard | F6 applied to every less ambitious revision | F6 applies only to a revision made for that cause; a revision for another cause gets no duty from F6. G8, whose case states the cause, keeps SOME(intent) | `tests/test_rsp_b_repair_1115.py::test_f6_forbids_a_revision_for_inability_and_not_for_another_cause` (both directions), `::test_g8_keeps_its_keyed_answer`, `::test_f6_guard_has_the_revision_and_its_cause`; seeds S1, S2, S6 in `mutants.json` | R16 (DRI-RULINGS.md): new behaviour within 150 lines, 0 trusted Lean lines (`uv run python tools/trust_map.py --check`: K +0, S +0, trusted +0), the new predicate exercised by the tests named here; ordered by reviews/dri-decisions-20261115-rsp-blockers.md item 2, the G8 line by reviews/dri-decisions-20261116-rsp-b-repair-1115.md item 1 |
