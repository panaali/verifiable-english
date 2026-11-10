# norm-defaults-cfr-1: user-visible delta

One delta: the client now refuses, as `CheckerUnavailable`, a norm-defaults row it used to show. Lean's own rows are
not refused: 0 of 21,344 genuine status and certificate rows from the norm-defaults suites
(`evidence/genuine-pairs.json`, command in REPORT.md "Genuine answers") and each probe of the new manifest bindings.

| # | Delta | Evidence and tests | Ruling |
|---|---|---|---|
| 1 | A `norm-defaults` mode `ok` row whose `norm-defaults-status` `tuple` is not the request's `tuple`, whose `rules` name a rule that is not a `norm` of the request's `norms` or `document` (under `acts@0`, nor Lean's part `<rule>-a<k>` of one), or name one twice, or whose `norm-defaults-certificate` `premises` is not the request certificate's `premise_meaning_ids` less the request's `premises`: before, shown as Lean's answer; now `CheckerUnavailable` ("malformed response (...)") after the client's one retry. A request for a certificate row without `certificate` or `premises` gets no `ok` row either. | Refusing fixtures: `tests/test_norm_defaults_response_binding.py::test_norm_defaults_response_binding` (16 forged rows), `::test_each_bound_field_deleted_or_retyped_is_no_answer`, `::test_a_certificate_case_without_its_certificate_has_no_count`; still accepted: `::test_genuine_answers_pass` (author norms, a rights document, a split act, a certificate) | R16 (conservative: refuses more) |
