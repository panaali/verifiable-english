# norm-defaults-cfr-1: user-visible delta

One delta: the client now refuses, as `CheckerUnavailable`, a norm-defaults row it used to show. Lean's own rows are
not refused on the sources run: 21,344 genuine status and certificate rows from ten norm-defaults suites (plain,
soft-norms, soft-norms with events, and rights-document sources), 0 refused by this tree's row schema and binding
(`evidence/genuine-pairs.json`; command in REPORT.md "Genuine answers"), plus the genuine rows of
`test_genuine_answers_pass` (a split act included) and each probe of the new manifest bindings.

| # | Delta | Evidence and tests | Ruling |
|---|---|---|---|
| 1 | A `norm-defaults` mode `ok` row is refused (`CheckerUnavailable`, "malformed response (...)", after the client's one retry) where it used to be shown as Lean's answer, when: its `norm-defaults-status` `tuple` is not the request's `tuple` or its `rules` repeat a name (response schema); its `rules` name a rule that is not a `norm` unit of the request's `norms`, for a request without `acts@0` and `rights@0` (`bind_answers`; with them `rules` stays type-checked only until norm-defaults-cfr-1b, DRI decision reviews/dri-decisions-20261110-norm-defaults-cfr-1.md); or its `norm-defaults-certificate` `premises` is not the request certificate's `premise_meaning_ids` less the request's `premises` (`bind_answers`). | Refusing fixtures: `tests/test_norm_defaults_response_binding.py::test_norm_defaults_response_binding` (16 forged rows), `::test_each_bound_field_deleted_or_retyped_is_no_answer`; still accepted: `::test_genuine_answers_pass` (author norms, a rights document, a split act, certificates with and without the case's own premises) | R16 (conservative: refuses more) |
