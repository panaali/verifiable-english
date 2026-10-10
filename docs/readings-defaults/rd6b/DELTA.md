# RD-6b: superposition under the unspecified completion

Batch RD-6b of [the plan](../../spec/readings-defaults-PLAN.md) and [statement spec](../../spec/readings-defaults.md), on `readings-defaults/rd6b`. The A/B base is the pinned merge-base commit `0d93e591d3963b65d1ad909a508b9d928322a014`; `main` was `c24aeab20ee513e3e1bef310c5e3263fab3998cc` when the code-head commit list was saved. No model calls or push were made.

## Implementation and proof

- `fill_transfers`, `nd_superpose_conflict_free`, and `nd_superpose_all` have exact approved statements and complete Lean proofs. The route selects filled superposition only when the filled document is superposable and `supU` is well formed; otherwise it returns the enumerated route with Lean’s cause. The superposed conflict, certificate, and model services carry `Fill_T` in the slot.
- Lean builds the filled document, `Fill_T`, generated predicates, names, and route response. Python validates the generated response schema and request binding before formatting it. Rust remains an untrusted accelerator.
- The response schema now closes filled and superposed units, contents, names, positions and numeric fields, with Lean `Fits` proofs. The filled environment remains a broad schema field; the client validates it using `Environment` and binds its sorts, constants and predicates to the request. This does **not** meet the requested fully typed response-schema condition.
- Existing Python `Superposed` evidence generation and verdict assembly remain in the pre-RD-7 path. The new binding code checks products and limits against the request. This does **not** meet the requested Python-only-CLI/files/display ownership boundary.

## Checks on the clean code head

- `lake build`: Build completed successfully (859 jobs).
- Lean audit: PASS: 464 source files; 5040 named theorem declarations, no sorry and only the standard axiom allowlist.
- Statement inventory: PASS: 4610 statements; 0 added, removed or changed in the final check. Exact RD-6b statement check: 3 approved declarations; 0 pending.
- Full gate on clean code head `4db9b7a150e17b07b3f4c8ca0782456411e66867`: 13611 passed, 92 skipped, 0 failed, of 13704 collected (1 live test deselected). Rust: 36 passed, 0 ignored. Lean build, audit, Rust build and Python suite all passed.
- Focused RD-6b document tests: 62 passed. The 200-case generated norms-chain differential passed. F-ND1 and F-ND2 take the superposed route with the previous verdicts; F-ND3 decides the 128-choice conflict fixture.
- Frozen-source inventory, assurance pin, generated response schemas, declaration and axiom inventories, gate collection and inventory lint were refreshed and checked.

## Saved A/B and latency

- Readings and pilots: 1591 records; 1555 identical; 29 route/payload differences; 7 scratch-path wording differences; 0 unlisted. All 29 changed pilot records move from `enumerated` to `superposed` and keep their public conflict status; one changes the UNKNOWN limit reason from more than 64 to more than 1024. The seven wording cases are missing sense-pack diagnostics whose only differing text is the scratch path.
- Five pilot checks hit the Rust subprocess’s five-second deadline under concurrent recording. The serial retries all returned successfully; original and retried outcomes are saved. Both sides cover 454 pilot documents and 1,137 readings cases, with no remaining unavailable records.
- The superposed route drops the old “checked one way at a time” English sentence on the changed pilot documents. That sentence would be false for the new route. This user-visible wording is recorded in the exact A/B delta and still needs DRI review; the DRI note signs only the reading’s own sentence change.
- Paired warm route CPU time stayed within the existing 20% budget:

| Case | Calls per side | Base CPU ms | Head CPU ms |
|---|---:|---:|---:|
| `differential/c0` | 500 | 2.254 | 2.323 |
| `differential/c568` | 500 | 2.132 | 2.318 |
| `nulls/rights/vocabulary.predicates.arrest_permitted.instruction_of` | 500 | 2.690 | 2.732 |

## Code commits before this evidence report

Saved from `git log --reverse main..HEAD --no-merges` at the code head. Report tests use the saved list and saved gate JSON; they never query a moving `main` or a live diff.

| Commit | Subject |
|---|---|
| `092fd857` | readings-defaults RD-6b: fill_transfers, nd_superpose_conflict_free and nd_superpose_all proved |
| `8c13fffa` | readings-defaults RD-6b: the superposed route under the completion (route, elaborate, conflict, certificate, model) |
| `8d45588a` | readings-defaults RD-6b: route filled superposition and bind answers |
| `647bc451` | readings-defaults RD-6b: refresh audit and response manifests |
| `e0dc4731` | readings-defaults RD-6b: record seeded failures |
| `5df25d29` | readings-defaults RD-6b: update route tests and reviewed fuzz baseline |
| `0acbab9f` | readings-defaults RD-6b: preserve fuzz baseline order |
| `324d72e2` | readings-defaults RD-6b: type superposed units and prove encoder shape |
| `0ee10a85` | readings-defaults RD-6b: bind superposed counts and names to requests |
| `4db9b7a1` | readings-defaults RD-6b: classify reviewed fuzz diagnostic under DF-9 |

## Seeded bugs, removed

Each bug was planted in changed code, failed the named test, then was removed. The restored targeted tests passed.

| Bug | File | Failing test | Result |
|---|---|---|---|
| M1 checked choice count ignored | `ve/readings_route.py` | `tests/test_readings_nd_document.py::test_superposed_answer_retypes_each_field_and_rebinds_each_reference` | exit 1 |
| M2 Fill_T omitted from superposed evidence | `ve/readings_verdicts.py` | `tests/test_readings_nd_document.py::test_fnd1_check_every_choice_conflict_free_with_a_model` | exit 1 |
| M3 generated constant passed to English gap renderer | `ve/readings_s2_wording.py` | `tests/test_readings_nd_document.py::test_fnd2_check_conflict_under_one_reading_only` | exit 1 |

## Acceptance and remaining work

- **AGENT:** The three Lean statements, no-sorry audit, F-ND1/F-ND2/F-ND3 and 200-case differential, saved A/B accounting, latency and clean code-head gate pass. Saved-evidence report tests check numbers, hashes, commit rows, route/status review and mutation records.
- **HUMAN (DRI):** Review the removed “checked one way at a time” line on the 29 superposed pilot reports. The signed English delta in the DRI note covers the reading’s own sentence, not this new route wording.
- **HUMAN (DRI):** The trust map has no unclassified growth, but S grew by 16 and V by 82 against signed allowances of zero. A baseline change needs a DRI ruling; none is recorded.
- **AGENT, open:** `filled.environment` is not recursively typed by the generated response schema. Python’s validation and request binding does not satisfy the stated schema requirement.
- **AGENT, open:** Pre-existing `Superposed` Python logic still searches and assembles verdicts; the new client binder also checks product sizes and limits. Moving all of that ownership to Lean is still required by the user’s instruction, despite RD-7 scheduling part of it later.
- **EXTERNAL (English lexicon owner):** Missing sense-pack pilot diagnostics are retained as seven exact scratch-path wording pairs.

## Build checklist

| # | Disposition |
|---:|---|
| 1 | Generated Lean response shapes and diagnostics checked; the filled environment schema gap is open. |
| 2 | Rust is an untrusted accelerator; saved A/B and the gate exercise it. |
| 3 | No normalization implementation changed; established normalization tests ran in the full gate. |
| 4 | Superposed fields are fuzzed for type and request binding, including bool-for-int, empty and extra rows; the filled environment schema gap is open. |
| 5 | Malformed request and forged answer tests fail closed through `CheckerUnavailable`. |
| 6 | F-ND3 and budget-zero tests retain UNKNOWN on exhaustion. |
| 7 | Existing whole-operation deadlines and budgets apply; no new deadline was added. |
| 8 | Lean inductive cases and route conditions are proved; the legacy Python superposed assembly is open. |
| 9 | The signed reading-sentence wording is retained; the route wording change is deferred to DRI. |
| 10 | Public document and readings entry points are covered by route fixtures and the full gate. |
| 11 | No language regex was added. |
| 12 | No state machine or ledger was changed. |
| 13 | Three code mutants failed real tests and were removed; report evidence mutations are tested. |
| 14 | Gate environment was isolated; A/B recordings used pinned checkouts and saved inputs. |
| 15 | IDs, choices, names, spans and counts in new superposed answers are bound to the request by relay tests. |
| 16 | Audit, frozen-source, response schema, assurance and gate collection manifests were refreshed. Trust allowance remains unsigned. |
| 17 | Exact RD-6b statement diff passed with no amendment. |
| 18 | F-ND1, F-ND2, F-ND3 and the generated 200-case boundary/differential exercise the theorem conditions. |
| 19 | No use-case rule formalisation was added. |
| 20 | Report tests read only saved gate, A/B, latency and commit evidence; none queries live git. |
| 21 | AGENT, HUMAN and EXTERNAL dispositions and owners are listed above. |
| 22 | Code-head gate passed on a clean commit; the final report-head gate is run after the report commit. Disk space was checked. |
