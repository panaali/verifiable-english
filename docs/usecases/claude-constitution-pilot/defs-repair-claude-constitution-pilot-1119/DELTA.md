# defs-repair-claude-constitution-pilot-1119 DELTA

This item changes no file under `ve/`, `lean/`, `rust/` or `tools/`. Run-20261104T0716Z is byte-identical to main.
The one user-visible change is a new run directory, whose probe's legends carry 15 source definitions. The new
probe's identities change with its environment, which now includes the longer descriptions.

| # | Delta | Ruling | Evidence |
|---|---|---|---|
| 1 | `usecases/claude-constitution-pilot/run-20261119-defs-carry/probe-translation.probe.md`, a new file (DRI decision 2026-11-19 item 1): 15 vocabulary legends (sorts `claude_instance`, `operator`, `user`; constant `claude`; 11 predicates) end with the source's definition of their term, appended word for word. No text is removed or renamed. Against run-20261104T0716Z's probe, the body, units, formulas, candidates' content, open terms and situation entries are the same. The environment id, 8 candidate `meaning_id`s and 4 situation ids differ, and C9's 160 saved point statuses are the same once those ids are masked. | R3 | `tests/test_defs_repair_claude_constitution_pilot_1119.py`: `test_the_legend_carries_the_source_definition_word_for_word` (each passage read from the pinned body; 15 rows), `test_the_legends_only_grow`, `test_only_the_rows_legends_and_the_identities_change`, `test_the_committed_probe_is_the_drivers_rewrite`, `test_c9_point_status_is_the_old_runs_but_for_identities`, `test_c9_point_status_records_are_bound_to_the_carried_probe` |
