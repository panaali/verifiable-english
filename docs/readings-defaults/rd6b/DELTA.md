# RD-6b: superposition under the unspecified completion

Batch RD-6b of [the plan](../../spec/readings-defaults-PLAN.md) and [statement spec](../../spec/readings-defaults.md), on `readings-defaults/rd6b`. The A/B base is the pinned merge-base commit `0d93e591d3963b65d1ad909a508b9d928322a014`; `main` was `c24aeab20ee513e3e1bef310c5e3263fab3998cc` when the code-head commit list was saved. No model calls or push were made.

## Implementation and proof

- `fill_transfers`, `nd_superpose_conflict_free`, and `nd_superpose_all` have exact approved statements and complete Lean proofs. The route selects filled superposition only when the filled document is superposable and `supU` is well formed; otherwise it returns the enumerated route with Lean’s cause. The superposed conflict, certificate, and model services carry `Fill_T` in the slot.
- Lean builds the filled document, `Fill_T`, generated predicates, names, and route response. Python validates the generated response schema and request binding before formatting it. Rust remains an untrusted accelerator.
- The response schema now closes filled and superposed units, contents, names, positions and numeric fields, with Lean `Fits` proofs. At the code head the filled environment was still a broad schema field (review B4). Review round 1 types it fully; see below.
- Existing Python `Superposed` evidence generation and verdict assembly remain in the pre-RD-7 path. The new binding code checks products and limits against the request. This does **not** meet the requested Python-only-CLI/files/display ownership boundary.

## Checks on the clean code head

- `lake build`: Build completed successfully (859 jobs).
- Lean audit: PASS: 464 source files; 5040 named theorem declarations, no sorry and only the standard axiom allowlist.
- Statement inventory: PASS: 4610 statements; 0 added, removed or changed in the final check. Exact RD-6b statement check: 3 approved declarations; 0 pending.
- Full gate on clean code head `4db9b7a150e17b07b3f4c8ca0782456411e66867`: 13611 passed, 92 skipped, 0 failed, of 13704 collected (1 live test deselected). Rust: 36 passed, 0 ignored. Lean build, audit, Rust build and Python suite all passed.
- Focused RD-6b document tests: 62 passed. The 200-case generated norms-chain differential passed; F-ND3 decides the 128-choice conflict fixture. At this head, F-ND1 and F-ND2 did **not** keep all of RD-3's answers, and the differential repeated two shapes: F-ND1 `--under rs_1:1` answered NOT ALL, not NONE; gap sentences were added; per-choice statuses were lost; and the tests were loosened to match (review B3, B5). Review round 1 fixes these; see below.
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
- **HUMAN (DRI):** The trust growth of RD-6b, after review round 1: K +0, S +0, V +142. Of this, +16 under R6 and +126 awaiting the DRI's signature (round 1, B1).
- **HUMAN (DRI):** The route wording of the superposed route under the completion, listed line by line in round 1, B3.
- **AGENT, open:** Pre-existing `Superposed` Python logic still searches and assembles verdicts; the new client binder also checks product sizes and limits. Moving all of that ownership to Lean is still required by the user’s instruction, despite RD-7 scheduling part of it later.
- **EXTERNAL (English lexicon owner):** Missing sense-pack pilot diagnostics are retained as seven exact scratch-path wording pairs.

## Build checklist

| # | Disposition |
|---:|---|
| 1 | Generated Lean response shapes and diagnostics checked; the filled environment is typed in round 1 (B4). |
| 2 | Rust is an untrusted accelerator; saved A/B and the gate exercise it. |
| 3 | No normalization implementation changed; established normalization tests ran in the full gate. |
| 4 | Superposed fields are fuzzed for type and request binding, including bool-for-int, empty and extra rows; every field of the filled environment is retyped against the schema in round 1 (B4). |
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

## Review round 1 (`rd-6b-review.final.md`)

The fixes are on top of the code head above. The saved gate, A/B and latency evidence above are of that head. This round's own evidence is listed below.

| Finding | Fix | Commits |
|---|---|---|
| B1: the batch-12 trust test measured an old commit, so nothing compared the tree with `docs/trust-baseline.json` | The test is main's again: the baseline must equal the measured tree. `AuthorLite`, `DecidesByD` and `DecidesBySoftD` are proof-helper predicates that only lemmas mention, so they are P. The baseline is rewritten with an RD-6b entry. `tests/test_readings_defaults_rd6b_report.py` pins that entry to the growth measured from the pinned merge base. | `bd6046f9`, `dfa7b6cd` |
| B2: a fuzz-baseline entry came from a stale `ve_conformance` (a trace copied from another checkout) | `tools/lake_outputs.py` compares each executable's trace `outputs` with the pinned toolchain's own hash of the file (`tools/lake_output_hash.lean`) and drops stale traces. The gate (in its own allowlisted environment) and the map recorder drop them before `lake build`, the gate fails if one is left, and the CI fuzz test refuses a stale binary. Rebuilt, `requests-01651c1807526be3` reports fixed and the baseline is main's again. | `ac87e6fd`, `1fc602bd` |
| B3: F-ND1/F-ND2 answers changed without disclosure; tests loosened | Under the completion: `--under` folds over the compatible choices taking the named readings (F-ND1 `rs_1:1` is NONE again). Each choice's conflict status is listed (CONFLICT-FREE under no assumed reading is every choice's, `readings_wire_nd_conflict_sound`). A gated query names its choice. The gaps shown are Lean's: `readings-model` and a witness of `readings-conflict` carry `ndModelGaps`/`gapsOf`, the function the enumerated route uses, bound to the request, in place of Python's list of every filled point. The tests are strict again. The wording guard compares every line with `evidence/wording.json`, chained to RD-3's signed rows, with no line filtered. | `767457cd`, `63765768`, `6c608a47`, `37013777` |
| B4: `filled.environment` untyped | Its schema is `decodeEnvelope`'s four fields, with language and revision equal to the request's, and every sort, constant and predicate entry typed as the route's vocabulary decoder admits it (`filled_predicate`). A companion component's frame merges its readings' sorts, so the schema does not compare the entries with the outer request. The client binds the profiles and the sort, constant and predicate names of the answer it relays to its case. A test retypes every field and adds a field to every object of a genuine filled environment; the generated schema alone refuses each. The binding mutants are refused by the client. The gaps of every readings-route answer are typed too. | `767457cd`, `63765768`, `37013777` |
| B5: the differential used two shapes | 200 seeded documents vary: one or two predicate pairs, one or two open sentences of two or three readings from four templates, and four kinds of fixed unit. Each is compared on both routes: the conflict status of every choice, the premise status of every candidate, and a query with or without `--under`. The test runs in ten chunks. A fast test checks the shapes vary (at least 100 distinct). | `4b11c7b3`, `6c608a47` |

### B3: what the superposed route says that RD-3 did not

On the six rows the DRI signed for RD-3, the result lines, their gap sentences and their conditions are RD-3's (`evidence/wording.json`). The route's own wording differs, and needs the DRI's signature:

- Removed, because it would be false on the superposed route: "The readings of sentence 1 were checked one way at a time, not together." and "The readings of sentence 2 were checked one way at a time, not together."
- Added on the superposed route: "This does not depend on how sentence 1 is read." (F-ND1's implication, from one certificate whose labels mention no reading bit) and "CONFLICT: pair conflict on x_required->x_permitted at act e0" (F-ND2's classification line).
- Status texts: F-ND1 "CONFLICT-FREE among rules on the same act, conditional on 0 coherence premises and 1 reading premises" (was "... under every reading (2 readings checked one at a time)"); F-ND2 "CONFLICT: pair conflict on x_required->x_permitted at e0 under rs_2@1:0" (was "CONFLICT under rs_2@1:0").
- JSON: the superposed answer's own shape (a single certificate in place of per-choice proofs; `mentions`; the countermodel without `outcome`; per-reading premise statuses). The superposed route gives no premise status per choice: each would need one Lean check, and on a 32-choice pilot that took 562 s. RD-7's superposed fold also states per-reading statuses. Lean's `gaps` is added beside a shown model.
- The SOME answer's condition lines (`ve/readings_s2_wording.py`) are shown on the superposed route outside the completion too, as RD-3's plan shows them.

### B3: the changed pilot records, recorded again

29 changed pilot records recorded again, one process at a time: 721 s on this round's head, 1076 s on the base (`evidence/round1-pilots-head.jsonl.gz`, `evidence/round1-pilots-base.jsonl.gz`; `pilot_check` of `tools/lean_first_diff.py`). Every record keeps the base's conflict and premise statuses and the previous head's status text and English, line for line. Against the previous head, this round only adds `readings.conflict.choices` and `premises.gaps`. 6 of them more than 20% slower than the base: `nd-s01p1.ve.md`, `nd-force.ve.md` and `nd-op.ve.md` (two runs) of the constitution pilot, and `translation-part07.ve.md` and `translation-part01.ve.md` of the UDHR pilot. The worst is `nd-op.ve.md`, 9.1 s on the base and 34.8 s on this head. R4 does not cover a markedly slower pilot, so this is for the DRI. The previous head was not timed in this round.

### B1: trust growth

`tools/trust_map.py --check` passes against the rewritten baseline. Its RD-6b entry records the growth from the pinned merge base: K +0, S +0, V +142. +16 under R6: `ndModelGaps`, the `gaps` shape and its three uses replace Python's choice of the gaps a superposed model shows (`S2Wording.gaps` listed every point of every filled table), deleted in this round. +126 awaiting the DRI's signature:
- the route's wire, +34: `elaborateFieldsND` +25, `supUnitsFrom` +5 net, `ndFillJson` +6, `decodeAssumedND` +5, `ndSlotLabels` +2 and `runElaborateNDWith` +1, less `runElaborateND` −3 and `Run.lean` −7;
- the typed superposed answer (contents, units, names, labelled premises): +48;
- the typed filled environment (B4): +44.

### Seeded mutants of this round

Each failed the named tests and was removed:
- the `--under` fold disabled failed all ten differential chunks;
- every choice reported CONFLICT-FREE failed all ten differential chunks;
- the old untyped schema failed `test_filled_environment_is_typed_by_the_schema_and_bound_to_the_request`.

### Rulings applied

- R8 (B4): the schema is typed, and the client checks only the binding: profiles, sort, constant and predicate names, predicate sorts, and the gaps' predicates and elements.
- R6: the +16 lines above.
- R3: the added `gaps` and `choices` members. They add information and remove none, and tests check them against Lean's answer and the theorem.
- Nothing else is claimed under a standing ruling.

### Not run in this round

The full suite and the release gate (left to the merge train and the nightly run). The full A/B of all 1,591 records; only the 29 changed pilot records were recorded again.
