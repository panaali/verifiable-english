# en-e3b build report: english.statement registered in ve_service (en-e3ab's scope), and the shadow comparator

**Re-scope (no signature reserved, nothing open):** this launch ran before its prerequisite en-e3ab was built. The DRI
re-scoped it (`reviews/dri-decisions-20261110-en-e3b.md` item 1, SIGNED). It builds en-e3ab's deliverables
(task-en-e3a.txt (3) and (4)) and the part of task-en-e3b.txt that needs no relay: the shadow comparator (spec 2.4,
E14) and P5. The rest of task-en-e3b.txt moves unchanged to **en-e3bb**: the `parse_english` shadow relay, the
binding and `SERVICE_READERS`, the fuzz tests, the EN-2 relay fixtures P1-P3, the delta report and the DRI message.
No route's answer changes (DELTA.md: no rows).

## Rows delivered, and not

| Row | Where / test |
|---|---|
| Registry, protocol, `runMode_englishStatement` (rfl), RegistryExamples count 44 | `lean/VE/Service/{Registry,Protocol,RegistryExamples}.lean` |
| The shape, typed to the leaves: members per status from `statementFields`, `code` per `statementStatusCodes`, rule rows' `span`, identities hex64 | `lean/ResponseShape/Schemas/EnglishStatement.lean`; generated `english.statement.json` |
| `statementCaseReported_fits` (every status, the overlay failure, the error row), every-mode case | `lean/ResponseShape/Encoders/EnglishStatement.lean`, `Encoders.lean` |
| Audit lines | regenerated `lean/VE/Audit.lean`, `lean/ResponseShapeAudit.lean` |
| `english_codes.py` copies the three statement tables; reader `statement_codes()` | `test_the_code_table_is_the_english_grammar_export`, `test_the_statement_tables_are_the_lean_export` |
| `DEADLINES` (english.read's `_CORE`); `_SCHEMA_SEEDS` and the wrong-row-type list | `test_random_malformed_responses_never_escape_schema`, `test_the_english_statement_seed_is_a_valid_row` |
| layer_policy rows | none needed: `tools/check_lean_imports.py` keeps the graph as it is |
| R-f1..R-f24 and R-stale: 32 cases in `tests/data/route-cases.jsonl` (`route_fixtures()`, written by `route_fixtures.py`) | `test_each_route_fixture_through_the_service`, `test_the_route_fixtures_are_recorded`, `test_route_row_schemas.py` (mode added) |
| Relay mutation gate minimum (a registered mode needs an ok fixture) | 7 rows appended to `tests/data/relay-gate-cases.jsonl` (see below); the service corpus gains the mode |
| Shadow comparator: `statement_class`, `statement_record`, `statement_shadow_log` (spec 2.4, E14, P5) | `tests/test_english_statement_shadow.py` (16 tests) |

Route answers through ve_service: `one` 18 (nodes equal to Python's `parse_english`), `none` 6, `rejected` 6, `many` 1
(f18, two different trees), R-stale `InvalidInput: the lexicon names another environment`. No fixture reaches
`unformalised` (authoring mode never does, spec 3.1), `budget`, or `invalidGrammar`. The encoder theorem covers them.

**Relay-gate fixtures.** `--record` rewrote other routes' rows in this worktree (229 gate failures), so the file keeps
main's rows and appends the 7 english.statement rows `--record` kept, as ap-4 and sn-b6d did. The full gate gives
49 routes, 154559 mutants, 0 failures. `_shape` groups rows by the outer status, so no kept row is a `one` answer. The
gate refuses all 1192 mutants of the route by schema alone. **en-e3bb must add a `one` fixture with its reader.**
`tools/binding_census.py --answers` re-asked the recorded answers: english.statement's 7, plus 13 English answers
whose `actions_version` main had left at 45 (now 47).

## Seeded bugs (each planted alone, shown failing, restored)

Python (`/tmp/e3b_seed.py` runs each with its test):
1. `ve/norm_english.py` `statement_class`: a Lean refusal of a Python-admitted text classed `both-refuse` (spec 9):
   `test_a_lean_refusal_is_classed_by_python_outcome` fails (8 cases).
2. `ve/norm_english.py`: the `lean-unavailable` test placed after the other rows, where no answer reaches it (spec 9):
   `test_an_unavailable_answer_is_a_delta_row_whatever_python_did` fails (3).
3. `ve/norm_english.py` `statement_shadow_log`: defaults to `ve-shadow.jsonl` without `VE_SHADOW_LOG` (P5):
   `test_the_shadow_needs_both_flags` fails.
4. `ve/norm_english.py`: nodes compared with `==` (true equals 1): `test_a_lean_reading_is_compared_by_position`.
5. `ve/english_grammar/__init__.py` `statement_codes`: required and optional members swapped:
   `test_the_statement_tables_are_the_lean_export`.
6. `tools/english_codes.py` `from_lean`: `statement_fields` dropped:
   `test_the_code_table_is_the_english_grammar_export`.

Lean:
7. `lean/VE/Service/Registry.lean`: `.englishStatement` named `"english.statements"`: `RegistryExamples.lean:6` #guard.
8. `lean/ResponseShape/Schemas/EnglishStatement.lean`: `place` without `bearer`: `statementCaseReported_fits`'s
   `spanRow_fits` (`Encoders/EnglishStatement.lean:43`) fails the build.

The spec's other two Python bugs (an extra rule row, the span overlap check) test the binding: en-e3bb.

## Trust (R16)

`tools/trust_map.py --check`: PASS. Against `f3f40d51d`: K +0, S +0, trusted **+4**, one case each in the existing
`VE.Service.Mode`, `runMode`, `Skeletons.row` and `Schemas.files`. The new declarations are G[R] (the schema,
`Skeletons.englishStatement`) or P (the encoder's helpers), classified in `tools/trust-classes.json`. Recorded with
`--allow` as "SIGNED by standing ruling R16"; FOLLOW-UPS "## en-e3b" asks for the ties pass. Trust-mutants sweep
(`trust-mutants.json`): 23 mutants, 19 killed, 0 survivors, 1 invalid. 3 are allowed (`trust-mutants-allow.json`):
mutants that do not compile (a dropped constructor line, a schema list without `common.json`).

## Spec re-read

`statementCaseReported_fits` against docs/spec/en-e3-norm.md:1126-1127 and `runMode_englishStatement` against
:1130-1131 (same text, qualified as written); the shape against :496-501 (seven statuses without `rendered`, `code`
in its status's list, `node` the W1 norm object, `span` a pair of naturals); DEADLINES against :508; the comparator
against :569-594 (both flags; the record's fields; `lean-unavailable` first; the class table) and E14 at :1340.

## Size, checks, next

Counted lines: 724 changed outside generated files, minus 185 exempt encoder-proof lines = 539. With the 32
route-fixture lines and this report, about 615, against the DRI's ~600. Regen `--write` (38 entries), the full
`lake build` and `python3 lean/audit.py` ("PASS: 832 source files; 9352 named theorem declarations") ran once.
Self-review: 2 A, 2 B, 8 C; fixed 9 (A, B, and five C). The other C's are recorded above (fixture statuses,
no `one` gate fixture) or left: R-stale is compared with `english.read`'s text by literal. Pilot bytes: 0 (nothing
reads the mode).

Next: **en-e3bb** (the rest of task-en-e3b.txt), then en-e3a-cutback, then en-e3 (EN-3) after the DRI's W1 delta
decision.
