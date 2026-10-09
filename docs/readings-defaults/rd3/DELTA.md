# RD-3: verdicts across enumerated readings in Lean

Batch RD-3 of [the readings-defaults plan](../../spec/readings-defaults-PLAN.md) and [statement spec](../../spec/readings-defaults.md) 6.4–6.5, on branch `readings-defaults/rd3` from `main` at `a3476e66`. The DRI's signed English delta is the reading's own sentence in the `<reading>` slot. No model call was made.

## Implementation

- Lean owns the enumerated conflict, premise and entailment folds, their three-valued gate, `restrictionsFor`, checked label use and the English line plan. Its wire replays each choice on the regenerated document and proves the successful answers against the fold statements. The lower route has the same fold proof. The 30-set restriction fixture computes its labels without the product of all choices.
- `Enumerated` sends the evidence it proposes to `readings-verdicts` and returns Lean’s answer. Python validates the response against the generated Lean schema and formats the English plan; it does not fold enumerated verdicts, compute their restrictions, or select their lines. The schema closes the status words in one table, and Lean proves the encoder fits it. Existing Python proof and model generators remain untrusted evidence proposers, and Lean accepts or rejects every piece.
- The generated `readings-route` response schema, assurance pin, frozen source hashes, axiom, declaration, statement and trust inventories, gate collection and `lean/READINGS.md` were refreshed. The recorder now writes its diagnostic English shadow beside its scratch output, including when its base checkout is read only.

## Statement and fixture gate

- `lake build`: Build completed successfully (847 jobs).
- `lean/audit.py`: PASS: 458 source files; 4881 named theorem declarations, with only the standard axiom allowlist and no sorry.
- `tools/lean_statements.py --check`: PASS: 4488 Lean statements, none changed or removed.
- `tools/check_readings_defaults_statements.py`: 30 exact RD-3 declarations; no pending RD-3 ruling.
- RD-3 service, RD-2b document, statement and budget-zero tests: 234 passed.
- Frozen source check, import graph, response schemas, trust map, inventory lint and relay lint pass. The trust baseline has no unclassified growth.
- F-ND1, F-ND2 and F-ND3 exercise CONFLICT-FREE, CONFLICT, ALL, SOME, NONE and UNKNOWN through the service; the `--under` and 30-set cases check restrictions and early refusal. Lean guards cover the gate, both directions of the folds, coupling restrictions and label removal.

## Saved A/B and latency

- Readings and pilots: 1549 records; 1538 identical; 7 scratch-path wording differences; 0 unlisted; 4 unavailable on both sides. The wording differences are the two temporary paths in otherwise identical missing `pack.json` diagnostics. The unavailable cases have the same English lexicon `CheckerUnavailable` on both sides, so they provide no verdict evidence.
- M8, M9 and M12: identical verdicts and English in saved public result captures. The signed reading-sentence wording was already in the base; no new wording change appears in these cases.
- The unchanged `readings-route` requests remain inside the 20% paired warm CPU budget:

| Case | Calls per side | Base CPU ms | Head CPU ms |
|---|---:|---:|---:|
| `differential/c0` | 500 | 2.604 | 2.604 |
| `differential/c568` | 500 | 2.503 | 2.517 |
| `nulls/rights/vocabulary.predicates.arrest_permitted.instruction_of` | 500 | 2.980 | 3.096 |

## Code commits before this evidence report

Saved from `git log --reverse main..HEAD --no-merges` at the code head. The report tests read this list from `evidence/summary.json`, never from a moving `main`.

| Commit | Subject |
|---|---|
| `0b928e78` | readings-defaults RD-3: the fold, conditions, English plan and readings-verdicts in Lean |
| `a8fc0d25` | readings-defaults RD-3: the enumerated route asks Lean for every verdict; Python generates evidence and renders the plan |
| `29c21f38` | readings-defaults RD-3: spec 8.2's service fixtures for readings-verdicts; Lean's answer checked as untrusted output |
| `ee11e1fc` | readings-defaults RD-3: inventories (audit, statements, declarations, axioms, trust classes, assurance pin), the statement check of spec 6.4 and 6.5, READINGS.md |
| `e141ec0a` | readings-defaults RD-3: the plan renderer reads Lean's model index with decimal_value (numeral policy) |
| `55eb5913` | readings-defaults RD-3: readings-verdicts' answer is closed and typed in the client schema, proved to fit; its cases join the route corpus |
| `be5cf0f3` | readings-defaults RD-3: refresh trust baseline after audited fold |
| `ff4c7b75` | readings-defaults RD-3: keep pilot recorder shadow outside read-only base |
| `af7c0b6b` | readings-defaults RD-3: isolate recorder shadow from ambient path |
| `f90ef497` | readings-defaults RD-3: pin saved-evidence report checks in the gate |
| `d0d89234` | readings-defaults RD-3: account for saved pilot availability and scratch paths |
| `a33a8e07` | readings-defaults RD-3: use proved response schema for verdict statuses |

## Seeded failures, restored

Each Python or recorder mutant was planted in the named changed file, its targeted test failed, and the original bytes were restored. The targeted suite then passed.

| ID | File | Failing test | Result |
|---|---|---|---|
| M1 | `ve/readings_verdicts.py` | `tests/test_readings_verdicts_lean.py::test_fnd1_query_some_each_reading_named_by_its_own_sentence` | exit 1 |
| M2 | `ve/readings_verdicts.py` | `tests/test_readings_verdicts_lean.py::test_a_mutated_verdicts_answer_is_unavailable[an acceptance as 1]` | exit 1 |
| M3 | `ve/readings_s2_wording.py` | `tests/test_readings_verdicts_lean.py::test_fnd1_query_some_each_reading_named_by_its_own_sentence` | exit 1 |
| M4 | `tools/lean_first_diff.py` | `tests/test_lean_first_diff.py::test_pilot_recording_keeps_the_english_shadow_in_its_writable_scratch` | exit 1 |
| M5 | `ve/backends/lean_service_schema/readings-route.json` | `tests/test_readings_verdicts_lean.py::test_a_choice_result_outside_the_proved_schema_is_unavailable` | exit 1 |

The Lean mutants changed each approved definition in turn; its dependent proof or guard made the build fail. The source and full build were restored.

| ID | File | Seeded behavior | Build result |
|---|---|---|---|
| L1 | `lean/VE/Readings/Verdicts.lean` | entailment gate | 3 errors |
| L2 | `lean/VE/Readings/Verdicts.lean` | local restriction meaning | 4 errors |
| L3 | `lean/VE/Readings/Verdicts.lean` | needed labels | 3 errors |

The saved-evidence report tests were also seeded with wrong build, theorem, fixture, A/B and commit values and verified to fail; the mutation log is in `evidence/report-mutants.json`.

## Acceptance and limits

- **AGENT:** The RD-3 Lean statements, generated response contract, service fixtures, frozen inventories, A/B on available records, public S2a examples and paired route latency are checked by the evidence above.
- **HUMAN:** The reading’s own sentence is the DRI-signed wording delta. This batch introduces no additional user-visible wording in the saved A/B.
- **EXTERNAL, deferred to the English lexicon owner:** Four constitution pilot documents are `CheckerUnavailable` on both sides; A/B rechecks list them separately and do not count them as equality.
- The seven missing sense-pack diagnostics are a corpus fixture dependency, recorded as exact scratch-path wording pairs. No verdict or acceptance changed in the saved A/B.
- Python’s pre-existing untrusted proof and model search still proposes evidence. RD-3 moves acceptance, the fold, conditions and English selection to Lean. The superposed route retains its prior Python path until RD-7, as the plan schedules.

## Build checklist

| # | Disposition |
|---|---|
| 1 | Generated response shape and Lean diagnostics; Python validates and relays. |
| 2 | No Rust readings fold exists to compare; Rust remains an untrusted accelerator. |
| 3 | No normalization change; the existing English gate covers rendered lines. |
| 4 | Typed Lean output is checked; field deletion, duplication, retyping and bool-for-int mutations fail. |
| 5 | Malformed request and evidence nodes produce errors or UNKNOWN, never a positive verdict. |
| 6 | Budget-zero public operations remain UNKNOWN; the entailment gate is proved and exercised. |
| 7 | Existing per-case deadline and generator budgets apply; no new public deadline. |
| 8 | Lean inductive folds are exhaustive; Python does not classify the enumerated result. |
| 9 | The English plan comes from Lean and passes the established W7 rendering gate. |
| 10 | `ve document` and `readings` use the same admitted route; service fixtures cover both. |
| 11 | No new regex for a language; response parsing is structural. |
| 12 | No new state machine or ledger. |
| 13 | Code and proof mutants are recorded above; saved-evidence report mutants are recorded separately. |
| 14 | Pilot recorder shadow now stays in writable scratch; tests use temporary paths. |
| 15 | Lean replays evidence on each regenerated choice document; the client binds choice rows to the request. |
| 16 | Audit, frozen, schema, declarations, trust and gate lists were regenerated and checked. |
| 17 | Exact RD-3 statement diff passed; no theorem amendment is pending. |
| 18 | Lean guards pin fold boundaries, restrictions in both directions and needed labels. |
| 19 | No new use-case rule formalisation in RD-3. |
| 20 | Report tests recompute all stated measured numbers and commit rows from saved JSON. |
| 21 | AGENT, HUMAN and EXTERNAL dispositions are stated above. |
| 22 | The final full gate runs on a clean committed HEAD; disk space was checked. |
