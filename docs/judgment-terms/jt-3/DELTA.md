# jt-3 DELTA

Measured on the final HEAD: `uv run python tools/trust_map.py --check`, `uv run python tools/lean_statements.py --check`.

| User-visible change | Evidence | Ruling |
|---|---|---|
| `english.read` in mode `authoring` with the new optional field `judgments`: `one` becomes `rejected`/`UndeclaredEvaluative` for a sentence whose reading has an evaluative predicate not in the field. Without the field no answer changes | `tests/test_jt3_english.py::test_the_refusal_names_lean_s_text_and_a_bound_predicate_is_read`, `::test_without_the_field_no_request_is_refused_for_the_word`, `::test_binding_is_per_predicate_never_per_word`, `::test_another_sense_and_a_plain_word_are_not_refused` | SIGNED by the DRI 2026-11-02 (reviews/dri-decisions-20261102-jt-3.md item 1) |
| 9.5's refusal text and the new code in `statusCodes`'s `rejected` list; the relay's table is exported by Lean (`ve/english_grammar/codes.json`) | `tests/test_jt3_english.py::test_the_refusal_names_lean_s_text_and_a_bound_predicate_is_read` (the text equals Lean's); `lean/VE/EnglishGrammar/JudgmentLinesExamples.lean` (one #guard per form) | R3 (DRI-RULINGS.md; reviews/dri-decisions-20261102-jt-3.md item 1) |
| English `actions_version` 37 -> 42, forced by base spec 2.12 for `lean/VE/EnglishGrammar/Run.lean` and the new trusted `JudgmentLines.lean`: each commit that changed a hashed file raised it, and the merge train may raise it again | `uv run python tools/english_grammar_gen.py --check`; the 12 pins of `lean/VE/Senses/RunExamples.lean` move only by the version (see REPORT) | SIGNED by the DRI 2026-11-02 (reviews/dri-decisions-20261102-jt-3p.md item 3) |
| The relay refuses a refusal row whose `sentence` the source cannot hold (a tighter binding; no genuine answer changes: every sentence ends with a period) | `tests/test_jt3_english.py::test_every_retyped_or_rebound_refusal_field_is_refused` | R3 (DRI-RULINGS.md; a binding of a relayed field, R8) |
| New CLI `ve judgments read`, showing Lean's answer verbatim | `tests/test_jt3_english.py::test_the_command_line_shows_lean_s_text` | R3 (DRI-RULINGS.md) |
| Trust: K +0, S +39, untied V +40 (+79 of 150): `VE/EnglishGrammar/JudgmentLines.lean` +75, `VE/EnglishGrammar/Run.lean` +4 | `docs/judgment-terms/jt-3/trust-mutants.json`, `mutants.json`; FOLLOW-UPS.md "## jt-3" | R16 (DRI-RULINGS.md) |

A translation-mode request answers byte-identically with or without the field: `tests/test_jt3_english.py::test_translation_answers_byte_identically_with_the_field`, and the same in Lean over `Run.readCase` (`lean/VE/EnglishGrammar/JudgmentRunExamples.lean`).

Fault order (R2), one sentence: the reader's own refusals come first (lexical, overlay, grammar, a sentence without a reading, budget), and a request whose whole source reads then gets 9.5's refusal for its first sentence with a listed predicate, naming that sentence's first listed predicate.

Statements: 0 changed, 0 removed; 2 added (`parseLine_renders`, `renderingTo_renders`), both about new definitions.
