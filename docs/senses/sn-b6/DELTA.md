# sn-b6 DELTA (senses B6: service and relay)

Base: the merge base with main, `0c4ea31d2`. The new `senses.project` service mode is a new route and has no
row. The document mode's own call of the senses reader (`VE.Service.Document`, unchanged) gets the answer it got
before: `readCase` adds identities only for the `senses.read` runner (`identified`), and the answer's new
`senses_version` member is beside the `reading` that mode reads (pinned: the guard "the document mode's call: no
identities" in `lean/VE/Senses/RunExamples.lean`).

| # | Delta | Evidence | Ruling |
|---|---|---|---|
| 1 | `senses.read` (`ve senses check`, the one-shot `ve_senses_route`) answers gain members, none removed or renamed: `senses_version` beside `dictionary_id`; on an admitted reading `identities` (the projection's `environment_id`, `lexicon_id`, `grammar_id`, S2's `actions_version`, and `source_sha256` for a source request) and `used` (the dictionary words the body uses); on each candidate `identities` (its own projection's, plan 2.6) | Values equal the true ones: `tests/test_senses_project.py::test_i1_reading_identities_are_its_projections` (environment_id equals Python's over the returned environment JSON; source, grammar and actions identities), `::test_i7_candidate_projection_identities` (each candidate's equal `senses.project`'s for its lines); bound to the request: `::test_reading_identity_rebinding_is_refused`, `tests/test_senses_route.py::test_genuine_response_field_mutations_are_rejected` (every new member dropped or retyped); goldens: `tests/test_senses_route.py::test_spec_fixtures_through_the_route_against_lean` compares candidates without the new member, which the tests above check | SIGNED by standing ruling R3 (DRI-RULINGS.md) |
| 2 | Trusted Lean growth V +73 (K +0, S +0) over `0c4ea31d2`: `lean/VE/Senses/Run.lean` +69, `VE/Service/Registry.lean` +1, `VE/Service/Protocol.lean` +1, `ResponseShape/Skeletons.lean` +1, `ResponseShape/Schemas.lean` +1 | `uv run python tools/trust_map.py --check` (exit 0 after the allowance in `docs/trust-baseline.json`); every new trusted definition killed by a check: `docs/senses/sn-b6/trust-mutants.json` (213 killed, 0 survivors, 0 unknown; the 27 allowed are listed with reasons in `trust-mutants-allow.json`); ties pass requested in FOLLOW-UPS.md "## sn-b6" | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
