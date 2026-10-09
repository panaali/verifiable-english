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

## Review fixes (rd-3-review.final)

- **B1, the result was untyped.** `readings-route.json`'s `verdicts_result` had a field list but no types, so `verdict: true` and a conflict result holding only its route were accepted, and the second crashed the report. The class: a relayed result whose form the client never closes. Fix: the schema is now generated from one Lean table per question, `verdicts_conflict`, `verdicts_premises` and `verdicts_query`. Each is a closed object for every form its encoder builds (`conflictResult`, `premisesResult`, `entailmentResult` and W2's budget shape, with and without `assumed`). Every field is typed and every status word comes from a closed list. The answer's `question` selects its result's form. `result_conflict_fits`, `result_premises_fits` and `result_query_fits` prove the encoder fits; the fold range lemmas close the status enumerations. Regression tests: `test_review_b1_findings_cases` covers the review's two cases. `test_the_result_of_every_form_is_typed_and_closed` drops each member of each genuine result form at every depth and replaces each value with one of another type or another value of its type.
- **B2, Lean's rows were not bound to the request.** The class: an answer whose rows, ids and per-row pieces the client checked only partly against what it asked. Fix: `_check_answer` now takes the request itself. With 64 or fewer compatible choices, every question's rows must be exactly the choices taking `assumed`, in order, and at least one; `exact=False` and the budget bypass are gone. Past 64, the answer must be W2's budget shape, with rows only for evidence the request sent. Every choice the result names must be a row's: a proof's row must be proved, a countermodel's refuted. The checker recomputes the result from the rows (the three folds and their gate), and each per-choice list, candidate status, label list and shown model must match its rows and the request's pieces. Every sent piece must have Lean's answer, Lean must not answer a piece it was not sent, and the dead notes must be the request's. Regression tests: the B2 rows of `test_a_mutated_verdicts_answer_is_unavailable`, `test_every_question_binds_its_rows_exactly`, `test_beyond_64_choices_rows_are_only_the_requests_evidence` and `test_review_b2_rd3_dead_evidence_lean_does_not_confirm_is_unavailable`. The review's three surviving mutants now fail the suite: exact binding weakened to a subset, the `errors` loop dropped, and the dead `accepted` check dropped. So does a mutant of each new check: budget `assumed`, fold, shown-model binding and sent-piece presence.

## Recheck fixes (rd-3-looprecheck1.final)

- **B, a row's word was not tied to the evidence the request sent.** `_check_answer` checked which word field a row had, not that the word was the one Lean's acceptance of the sent pieces gives. A row could say `proved` with only an accepted countermodel (SOME became ALL), `INCONSISTENT` with an accepted model, or `CONFLICT-FREE` with the packages' note false or missing. The class: any member of the answer the client checks only for consistency with other relayed members, not regenerated from the request. Fix: each row's words come from one table of Lean's notes (`ROW_WORDS`, Lean's `lowerInfo` and `ndConflictRow`/`ndQueryRow`/`ndPremiseRow`). Every other member of the answer is regenerated from the request's document, Lean's compatible choices and the rows, as `verdictsAnswer` computes it, and must equal Lean's answer as JSON (`_expected_answer`). That covers the result, restrictions (`restrictionsFor`), labels, untaken candidates, dead readings, candidate statuses and the English plan (`planItems`). Only what Lean computes from evidence the answer does not show is relayed, typed: the labels a certificate or package uses, a witness's lower status text, filled gaps and a dead certificate's acceptance. No choice may be both CONFLICT-FREE and in conflict; under the completion a sent witness is always noted; a choice's conflict notes are the same in every answer of the route. Regression tests: `test_every_row_word_lean_did_not_give_is_unavailable` uses a forger that sets every row's conflict and question word to every other word of every genuine answer form and makes all other members consistent (`test_the_forger_regenerates_every_genuine_answer` checks the forger). The review's probes are covered by `test_review_b_looprecheck1_rows_tied_to_the_evidence_sent` and `test_a_reading_s_conflict_notes_are_the_same_in_every_answer`.
- **B, dead readings were only required to be untaken.** With proof budget 0 no certificate was sent, yet a claimed dead reading `rs9:1` with an E17 line was accepted, and `DeadReading: rs8:0` on rs9:1's entry passed. Fix: the dead readings are regenerated. They are every untaken candidate when Lean accepted a sent certificate for each, else null, and each finding comes from `dead_finding`, which the superposed route uses too. The untaken list, the dead notes and every E17 line are regenerated as well. The follow-ups in the same class are closed too: a candidate narrowed by a made-up narrowing, a premises result naming another row's choice, and a dropped untaken entry or dead reading. Regression tests: `test_review_b_rd3_looprecheck1_dead_readings_are_regenerated` (full and zero budget) and `test_follow_up_rd3_looprecheck1_the_premises_choice_is_the_first_model`.
- **Mutants.** Nine seeded mutants of the new checks were each killed by the suite, then restored: row words unchecked, plan relayed, both conflict notes accepted, the completion's witness unnoted, the cross-request notes unchecked, and each of the dead readings, a narrowing's id, the premises choice and the untaken list relayed from the answer. The untaken mutant first survived; the zero-budget forgery `untaken: [], dead_readings: []` was added to the test, which now kills it.

## Round 3 fixes (rd-3-looprecheck2.final; DRI directive rd-3-fix3, 2026-10-09)

The DRI ruled that `check_answer` checks only the schema and the binding to the request, and that the semantic consistency of an answer (which conditions apply, which lines are said) is Lean's, by theorem. This round therefore replaces the regeneration added in review B2 and looprecheck1 B (`_expected_answer`, `_plan`, `ROW_WORDS`, the Python folds and restrictions): the earlier sections describe those rounds as built.

- **B, conditional overclaim.** On F-ND1 the reviewer removed the required pair condition from a genuine CONFLICT-FREE answer and an ALL query and regenerated the dependent fields; `check_answer` accepted both, and the English omitted the condition, because `conditional_on` was relayed. The class: a condition a verdict rests on that the answer or its English can leave out. Fix, in Lean: one value, `conditionsOf` (every label a row's accepted evidence uses, then the restrictions), is the result's `conditional_on`, the answer's `labels` under the completion and the source of the plan's condition lines. `verdicts_conditions_conflict_free`, `verdicts_conditions_all`, `verdicts_conditions_some` and `verdicts_conditions_none` state it for each verdict and per choice (`proofJson`'s labels are the row's own, each among the answer's); `mem_conditionsOf` says nothing is dropped or added; `verdictsPlan_cites` says the plan cites every label and `plan_conditions_only` that no line cites another. A label with no wording gets an `unworded` line, which Python refuses (`CheckerUnavailable`), so a condition is never left out silently. All are in `lean/VE/Audit.lean`, `axioms.txt` and `statements.txt`. The approved `englishPlan D route q a` statement is unchanged; `jstrings_toJson` proves that the answer's plan is planned from the `labelsOf` value. `planItems` now compares texts (`strOf`), because `Json`'s `==` cannot be unfolded in a proof.
- **Same class, also fixed in Lean.** On F-ND1 the SOME proof under the first reading rests on the pair condition (its conflict packages use it), yet its plan stated no condition. Its `labels` are now the proof's labels under the completion, and the plan cites them after the R2 line. A NONE's `labels` are its restrictions, from which its condition lines were already planned.
- **The client, schema and binding only.** `_check_answer` checks the generated schema; the id and question; rows that are exactly the request's compatible choices (no empty, missing or extra row); every piece a row notes or shows was sent for its choice; a row's word names a piece it notes as accepted (`ROW_PIECES`); lists that restate the rows (`choices`, `proofs`, `countermodels`, `witnesses`) restate them; and every choice, reading, candidate, narrowing, unit, label, model, status line, E17 line and dead reading in the result, the conditions and the plan belongs to the request. Labels are resolved against the document's couplings and narrowings and the environment's predicates. Under the completion every `conditional_on` label is resolved; on the lower route a choice's own labels are only typed. Python relays Lean's plan line for line and never builds or omits a condition.
- **Regression tests.** `test_review_b_looprecheck2_conditions_are_lean_s` reruns the reviewer's probe. Asked the same request, Lean gives the condition in `conditional_on`, `labels` and a P1 line, so the forgery is not Lean's answer. The theorems are checked in the audit and statement inventory, and the probe names nothing the request lacks. `test_python_relays_every_planned_line` checks one sentence per planned line, with E3 and P1 included. `test_the_result_of_every_form_is_typed_and_bound` pins the result mutants the client relays (`LEAN_OWNED_RESULTS`), each with its owning theorem or encoder. New `test_a_mutated_verdicts_answer_is_unavailable` rows cover labels, readings, models, status and E17 lines. `test_every_row_word_names_a_piece_lean_accepted` replaces the forger. The dead-readings test separates bound mutants from Lean-owned ones.
- **DRI wording sign-off (DRI = orchestrator, 2026-10-09).** `evidence/wording-round3.json` records the English of F-ND1's four queries and the F-ND1 and F-ND2 reports, base (main at `a3476e66`) against head. `test_dri_wording_rows_keep_the_base` checks lf-12 rule 2(a)–(c) on each row and recomputes the head lines. (a) Every name the base shows is shown. (b) Every base condition line is kept, and the head adds only condition lines. (c) Every result is as specific as the base's, and its gap sentences are among the base's; spec 2.2 keeps exactly the gaps the result depends on. All six rows pass, so they are SIGNED: the head adds the pair condition to the CONFLICT-FREE report, SOME and both ALLs, and it drops gap sentences outside the result's cone. No row loses a name, condition or specificity, so none needed a fix in Lean.
- **Seeded mutants, restored** (`evidence/round3-mutants.json`). Each Lean mutant broke the named proof (`lake env lean` on the file); each Python mutant failed the targeted suite.

| ID | File | Seeded behavior | Proof that broke | Result |
|---|---|---|---|---|
| L4 | `lean/VE/Readings/VerdictsWire.lean` | the encoder drops a CONFLICT-FREE condition | `verdicts_conditions_conflict_free` | 1 errors |
| L5 | `lean/VE/Readings/VerdictsWire.lean` | the encoder drops an ALL condition | `verdicts_conditions_all` | 1 errors |
| L6 | `lean/VE/Readings/VerdictsWire.lean` | conditionsOf drops a row's label | `mem_conditionsOf` | 1 errors |
| L7 | `lean/VE/Readings/VerdictsWire.lean` | labels drop the conditions under the completion | `verdicts_conditions_conflict_free` | 1 errors |
| L8 | `lean/VE/Readings/VerdictsWire.lean` | the plan drops a pair label's line | `conditionItems_label` | 2 errors |
| L9 | `lean/VE/Readings/VerdictsWire.lean` | a SOME's plan omits its conditions | `plan_cites_conditions` | 1 errors |

| ID | File | Seeded behavior | Result |
|---|---|---|---|
| P1 | `ve/readings_s2_wording.py` | Python drops the condition clause (the E3 and P1 lines) | 20 failed |
| P2 | `ve/readings_verdicts.py` | the client stops resolving labels against the request | 5 failed |
| P3 | `ve/readings_verdicts.py` | a row's word stops naming the piece it rests on | 3 failed |

## Acceptance and limits

- **AGENT:** The RD-3 Lean statements, generated response contract, service fixtures, frozen inventories, A/B on available records, public S2a examples and paired route latency are checked by the evidence above.
- **HUMAN:** The reading’s own sentence is the DRI-signed wording delta. This batch introduces no additional user-visible wording in the saved A/B. Round 3’s wording rows (the conditions added, gaps outside the cone dropped) are SIGNED by the DRI rule above (DRI = orchestrator, 2026-10-09).
- **EXTERNAL, deferred to the English lexicon owner:** Four constitution pilot documents are `CheckerUnavailable` on both sides; A/B rechecks list them separately and do not count them as equality.
- The seven missing sense-pack diagnostics are a corpus fixture dependency, recorded as exact scratch-path wording pairs. No verdict or acceptance changed in the saved A/B.
- Python’s pre-existing untrusted proof and model search still proposes evidence. RD-3 moves acceptance, the fold, conditions and English selection to Lean. The superposed route retains its prior Python path until RD-7, as the plan schedules.

## Build checklist

| # | Disposition |
|---|---|
| 1 | Generated response shape and Lean diagnostics; Python validates and relays. |
| 2 | No Rust readings fold exists to compare; Rust remains an untrusted accelerator. |
| 3 | No normalization change; the existing English gate covers rendered lines. |
| 4 | Typed Lean output is checked for its schema and its binding to the request only (DRI ruling, round 3): field deletion, duplication, retyping and bool-for-int mutations fail at every depth of the result, and so does every name the request lacks; the mutants the client relays are pinned with their owning Lean theorem. |
| 5 | Malformed request and evidence nodes produce errors or UNKNOWN, never a positive verdict. |
| 6 | Budget-zero public operations remain UNKNOWN; the entailment gate is proved and exercised. |
| 7 | Existing per-case deadline and generator budgets apply; no new public deadline. |
| 8 | Lean inductive folds are exhaustive; Python does not classify the enumerated result. |
| 9 | The English plan comes from Lean and passes the established W7 rendering gate. Its condition lines are planned from the answer's one conditions value and cite every label (`verdictsPlan_cites`); Python words each line and omits none. |
| 10 | `ve document` and `readings` use the same admitted route; service fixtures cover both. |
| 11 | No new regex for a language; response parsing is structural. |
| 12 | No new state machine or ledger. |
| 13 | Code and proof mutants are recorded above; saved-evidence report mutants are recorded separately. |
| 14 | Pilot recorder shadow now stays in writable scratch; tests use temporary paths. |
| 15 | Lean replays evidence on each regenerated choice document. The client binds every row, choice, reading, label, model, piece, dead note and plan line to the request (review B2; round 3); what the answer concludes from its rows is Lean's, by theorem (round 3 supersedes the regeneration of looprecheck1 B). |
| 16 | Audit, frozen, schema, declarations, trust and gate lists were regenerated and checked. |
| 17 | Exact RD-3 statement diff passed; no theorem amendment is pending. |
| 18 | Lean guards pin fold boundaries, restrictions in both directions and needed labels. |
| 19 | No new use-case rule formalisation in RD-3. |
| 20 | Report tests recompute all stated measured numbers and commit rows from saved JSON. |
| 21 | AGENT, HUMAN and EXTERNAL dispositions are stated above. |
| 22 | The final full gate runs on a clean committed HEAD; disk space was checked. |
