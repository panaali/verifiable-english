# English in Lean, E2: the deletion ledger

Spec [english-lean-e2.md](../../spec/english-lean-e2.md) 2.9, plan item E2.4. One row per decision site of
formula-level English admission, each with its disposition: **owned by Lean** (the Lean check named; the site
is off the admission path), **comparator** (run only with `VE_ENGLISH_COMPARATOR=1`, after Lean decided, never
deciding; deleted in the next stage), or **kept** (its caller named). Line numbers are those of this branch's
head; the sites are named so that a later edit can find them.

`tools/relay_lint.py` passes on the admission path: `ve/backends/english_lean.py` whole, and the functions
`_lean_reading`, `_nearest_help`, `_parse_english_document_uncached`, `_parse_english_document`,
`parse_english`, `parse_english_with_metadata` and `parse_english_argument` of `ve/english.py`
(`tests/test_relay_lint.py::test_the_english_admission_path_is_relayed_by_function`).

| Site | Disposition | Evidence |
|---|---|---|
| `ve/english.py` `_python_reading` (hand parser, Lark audit, `check_document`) | comparator, and kept for the statement layers through `parse_statement_english` (operation `english.statement`, until E3) | `tests/test_english_lean_adapter.py::test_default_admission_calls_lean_and_not_python` (ev6); `tests/test_english_e2_overlay.py::test_the_suite_runs_the_english_comparator` (ev7) |
| `ve/english.py` `_parse_english_document_uncached`: the former `dispatch.shadowed('english.admission', …)` | owned by Lean: `admitRequest` through the relay; `english.admission` is out of `dispatch.SHADOW_ONLY` | `tests/test_english_lean_route.py::test_admission_refuses_non_lean_authority` |
| the source byte limit (formerly `english.py` before the reading) | owned by Lean: `sourceTooLong`; the comparator's Python reading keeps Python's limit first (`_python_reading`) so it compares Python's public outcome | `conformance/english-lean/e2-evidence.json` (G3) |
| `A conclusion needs an earlier premise.` (`_check_conclusions`) | owned by Lean: `noPremise` (`ConclusionWithoutPremise`); `_check_conclusions` runs only for a comparator reading | E2Examples cn16, cn17; the shadow record compares the two (`english_lean.NO_PREMISE`) |
| the entailment refusal of a marked conclusion | kept (relay; S3 D10): the text is Lean's obligation `unproved`, its `{status}` slot filled with the prover's status verbatim, from `parse_english` and `parse_english_argument` alike | `tests/test_english_e2_python.py::test_argument_failure_text_preserves_prover_status` (rl2) |
| the premises of each marked conclusion | owned by Lean: `obligations`; `parse_english_argument` computes no premise and refuses a reading without Lean's obligations (`CheckerUnavailable`) | `tests/test_english_e2_responses.py::test_an_argument_without_lean_obligations_is_checker_unavailable` |
| re-parse of renderings (`render_english`, `parse_english_with_metadata`) | owned by Lean: `checkRequest` (`english.check`); the statement layer's own rendering check (`_statement_layer`) is kept for E3 | `tests/test_english_lean_route.py`; spec rl4, rl5 |
| `ve/english.py` `EnglishParser` | comparator for admission; kept for `norm_english.py` and `norm_defaults_english.py` and the E3 statement wording until E3 | operation `english.statement` in `ve/assurance-manifest.json` |
| `ve/surface/unambiguity.py` `require_unique_derivation`, `require_correspondence` | comparator for admission; kept for the statement layers (`english.statement`) until E3 | the same |
| `ve/english.py` `EnglishVocabulary` selection, `_RESERVED` | kept: the producer, whose every lexicon V6 checks (spec Q1) | `conformance/english-lean/e2-evidence.json` (`parity`: the port's selection equals Python's symbol by symbol) |
| `EnglishVocabulary` O1: the duplicate wording of an overlay entry (`english.py:378`) | owned by Lean: O1 of `overlayCheck`; off on the admission path, kept for the other callers | `tests/test_english_e2_overlay.py::test_rl9_lean_refuses_the_overlay_on_the_admission_path`, `::test_rl10_every_other_caller_keeps_the_producers_refusal` |
| `EnglishVocabulary` O2: an overlay entry's reused risk wording (`english.py:447`) | owned by Lean: O2; off on the admission path, kept for the other callers | the same |
| `EnglishVocabulary` O3: the final comparison of the overlay's entries (`english.py:522`) | owned by Lean: O3; off on the admission path, kept for the other callers, among them the statement reader and the statement-layer renderer, where no Lean overlay check runs | the same |
| `ve/english_vocabulary.py` `display_environment`: the overlay's format, identity, symbols and fields, the `accept_suggested_vocabulary` consent gate (`:113–114`) and the validation of the display environment by `Environment(data)` (`:131`) | kept: it decides whether a suggested entry may be used and whether the display environment is an environment, before any Lean call (rl8, ov11) | `tests/test_english_e2_overlay.py::test_rl8_display_environment_refuses_before_any_lean_call` |
| `ve/backends/english_lean.py` `CLASSES`, `STATUS_CLASSES`, `STATUS_CODES`, `ERRORS` | owned by Lean: `codeClasses`, `statusCodes` and `unsentencedCodes`, exported by `english.grammar` and generated into `ve/english_grammar/codes.json` (`tools/english_codes.py`); the relay raises the class Lean names, taken from `ve.errors` by name. The comparator keeps only its class tolerance for `IllTyped` and `RelativeForm` (`COMPARATOR_CLASSES`) | `tests/test_english_e2_responses.py::test_the_code_table_is_the_english_grammar_export`, `::test_every_code_is_raised_as_the_class_lean_names` |
| `ve/backends/english_lean.py` `_transport` over `ve_english_route` | owned by Lean: the `ve_service` modes; the S2 validator for the route's answers is gone, and the test override is checked like the service | `tests/test_english_e2_responses.py::test_the_test_transport_is_checked_like_the_service` |
| `ve/backends/senses.py` its copy of the class table | owned by Lean: the senses relay validates S2's outcomes with `english_lean.refusal_problem` | `tests/test_senses_route.py` |
| `ve/english.py` `english_lark_grammar` | comparator; an editor that reads it would regenerate it from the `english.grammar` export (LEAN-FIRST 5.2) | — |
| `ve/surface/definitions.py` definition and citation sentences, and their renderings (`render_citation`, `wordings`) | owned by Lean: `parse_english` reads them and `english.check` reads each rendering back (review A3 of E2 reverted their move to the Python-only reader; recheck 1 removed the renderings' `_statement_layer`) | `tests/test_definitions_english.py::test_definition_sentence_parts_are_read_by_lean`, `::test_citation_and_definition_renderings_are_checked_by_lean`; every caller of Python's reader is a row here (`tests/test_english_e2_ledger_sites.py`) |
| `ve/readings_s2_wording.py` `S2Wording.conclusion` | kept for E3 (`english.statement`): it reads back its own rendering of a checked conclusion over the frame environment, whose generated decision and `rights@0` atoms are outside the E2 reader | `tests/test_readings_s2_document.py` |
| `conformance/english_lean_{engine,lexer,lexicon}.py` | kept: still compared against by the S0 to S3 conformance tests (`tests/test_english_lean_{engine,lexer,lexicon,s0,s2,s3,tokens}.py`); deleted once nothing compares against them (LEAN-FIRST 6.3) | — |

**Signature.** The ledger is the E2.4 deliverable that GE2 item 8 asks the DRI to sign. It is recorded here,
unsigned: owner the English E2 DRI (HUMAN, deferred).
