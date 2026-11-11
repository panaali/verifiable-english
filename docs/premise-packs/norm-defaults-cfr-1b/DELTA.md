# norm-defaults-cfr-1b: user-visible delta

One delta: the client now refuses, as `CheckerUnavailable`, some `norm-defaults-status` rows under `acts@0` or
`rights@0` that it used to show. The rows also carry a new field, `sources` (each rule with the request rule Lean echoes
as its source). The field adds information, and no verdict changes. Lean's own rows still pass:
`test_genuine_answers_pass` covers author norms, a split act, a rights document, a fan-out, a bar rule and two UNKNOWN
points, and the selected tests on the final HEAD relay every other norm-defaults suite through the same binding
(REPORT.md, "Tests").

| # | Delta | Evidence and tests | Ruling |
|---|---|---|---|
| 1 | A `norm-defaults` mode `ok` status row is refused ("malformed response (...)", after the client's one retry) where it used to be shown, under `acts@0` or `rights@0` too: when its `sources` are not one `{rule, source}` echo per rule naming that rule in order (schema `x-same-length`, `bind_answers`); when an echoed source is not a rule of the request (its `norms`, or under `rights@0` its `document`); or when a rule differs from its source but either no generating profile is listed or the rule is itself a request rule. On main, under these two profiles, `rules` was type-checked only. | Refusing fixtures, accepted on main (`evidence/new-tests-on-main.txt`): `tests/test_norm_defaults_response_binding.py::test_norm_defaults_response_binding[acts-status-rules-forged_generated]`, `[rights-fan-status-rules-forged_generated]`, `[acts-status-rules-ghost]`, `[rights-fan-status-rules-ghost]`, `[acts-status-rules-appended]`, `[rights-fan-status-rules-appended]`. Also `[rights-bar-status-rules-forged_generated]`, the `*-sources-*` forgeries, `::test_each_echo_field_deleted_retyped_or_extended_is_no_answer`, `::test_a_generated_rule_needs_its_echo`. Still accepted: `::test_genuine_answers_pass`. | R16 (conservative: refuses more) |
| 2 | Trusted base: V +31, K +0, S +0. Per file: `VE/NormDefaults/Layered.lean` +12, `VE/NormDefaults/Explain.lean` +11, `VE/NormDefaults/Wire.lean` +3, `ResponseShape/Schemas/NormDefaults.lean` +3, `VE/Acts/Decode.lean` +1, `VE/NormDefaults/Run.lean` +1. Re-measured with `tools/trust_map.py --check` and recorded in `docs/trust-baseline.json`. | Every new trusted definition has a mutant that a `#guard`, a proof or a named test catches (`mutants.json`, `trust-mutants.json`). FOLLOW-UPS.md has the row `## norm-defaults-cfr-1b` asking for the ties pass. | R16 |
