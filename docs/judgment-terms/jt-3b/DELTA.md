# jt-3b DELTA

Measured on the final HEAD: `uv run python tools/trust_map.py --check`. Base answers: `tests/data/judgments-document-before-jt-3b.json`, recorded on b13cf9e3e (`plain`, `judged-bound`, `judged-unbound` with a lexicon naming the environment Lean reads, and `judged-bound-through-the-relay`, the case the base relay built).

| User-visible change | Evidence | Ruling |
|---|---|---|
| `ve document check`, judgments@0 document with an English fence: CheckerUnavailable -> Lean's answer (refusal when unbound, the report when bound, any other refusal as without the profile). The relay's lexicon proposal now names the environment Lean reads a fence in, without the document layers | `tests/test_judgments_document.py`: `test_an_unbound_word_in_an_authored_fence_is_refused_with_lean_s_text`, `test_a_bound_word_answers_the_report_as_today`, `test_without_the_profile_the_same_document_answers_byte_identically`, `test_the_proposal_is_the_one_the_plain_document_carries`, `test_a_fence_another_mode_refuses_keeps_its_diagnostic_under_the_profile`; seeded bug PS1 | SIGNED by the DRI 2026-11-05 (reviews/dri-decisions-20261105-jt-3b.md item 1) |
| The `document` mode, an authored fence in a judgments@0 document with an evaluative predicate not bound, sent with such a lexicon: `ok` -> `UndeclaredEvaluative`, gated by the profile. Without the profile the row is byte-identical (J-λ) | the base row `judged-unbound`; `lean/VE/Service/UndeclaredExamples.lean` (`refused` guards); `test_two_predicates_of_one_row_bind_one_by_one` | SIGNED by the DRI 2026-11-02 (reviews/dri-decisions-20261102-jt-3.md item 1) |
| The refusal's text in the document's error field: `UndeclaredEvaluative: ` and 9.5's text, Lean's verbatim | `REASONABLE` in `tests/test_judgments_document.py`, and the `refusal` guard, each compared with the whole string | SIGNED by standing ruling R3 (DRI-RULINGS.md) |
| New report member `judgment_lines` under judgments@0 (`{legend: [{term, lines}], status: [{unit, line}]}`) in the `document` row and in `ve document check`'s report, Lean's English verbatim; `document.json` gains its shape, with `lines_fits` | `test_the_report_places_lean_s_lines`, `test_every_mutant_of_the_lines_is_refused`, `test_the_lines_are_there_exactly_under_the_profile`, `tests/test_route_row_schemas.py` | SIGNED by standing ruling R3 (DRI-RULINGS.md) |
| Fault order under judgments@0 | One sentence per rule below; `test_the_refusal_names_the_first_fence_in_unit_order_before_any_unit_s_status` | SIGNED by standing ruling R2 (DRI-RULINGS.md) |
| Trust: K +0, S +0, untied V +42 (of 150): `VE/Service/Document.lean` +30, `ResponseShape/Schemas/Document.lean` +12 | `tools/trust_map.py --check`; `docs/judgment-terms/jt-3b/trust-mutants.json`, `mutants.json`; FOLLOW-UPS.md "## jt-3b" | SIGNED by standing ruling R16 (DRI-RULINGS.md) |

Fault order (R2):

- Records and their admission come first, as before; the fences are then read while the units compile, in unit order, so a fence's refusal comes before spec 8.1's unit checks (`JudgmentNotChecked` and the rest).
- Within a fence the reader's own refusals come first, then 9.5's refusal, then the document's rule that a fence holds one sentence.

Statements: 1 added (`lines_fits`, about the new `linesJson`), none changed or removed; `lean_statements.py --check` runs in the chain's gate.
