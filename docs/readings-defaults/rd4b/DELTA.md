# RD-4b: components in readings verdicts and the report

Batch RD-4b of [the plan](../../spec/readings-defaults-PLAN.md), implementing [the statement specification](../../spec/readings-defaults.md) §6.6 and its product gate. The signed English change makes “reading N” the reading’s own sentence. No model calls were made. The code-head evidence is saved under [`evidence/`](evidence/); `tests/test_readings_defaults_rd4b_report.py` checks these saved files without a moving Git diff.

## Change

- Lean proves the component product fold, its conflict, model, ALL, NONE and SOME conditions, `--under` generalisations, decided units, query typing, component replay and English plan; all 16 approved RD-4b declarations are exact and all 6 theorems have proofs without `sorry`. The response encoder proves the product row fits the generated schema.
- `ve document` relays the Lean split and per-component evidence, binds the returned IDs, choices, rows, units and copied source records to the request, and renders Lean’s English plan in each accepted component environment. A missing or extra relayed row is refused. Python does file and display work; Lean decides meaning and acceptance. Rust remains an untrusted accelerator.
- The W7 display receives the canonical conclusion slot for E30; a narrowing citation keeps the content boundary Lean gave it. Without companions the established route is used.
- Audit, statement, frozen-source, response-schema, assurance, trust-class and gate-collection manifests were regenerated.

## Scope and verification

Saved `main..HEAD --no-merges` at code head `5f186a23`: **7 code commits**, **4,459 added lines**, **321 deleted lines**. The commit list is frozen in [`scope.json`](evidence/scope.json). `main` advanced to `c24aeab2` during the work; the A/B base is the branch point `0d93e591`:

- `b3b9a98a`
- `e0184421`
- `f5c1ee5c`
- `95312f23`
- `be0c447b`
- `db6a0ce3`
- `5f186a23`

Full gate on that clean code head: **13,639 Python passed**, **97 permitted skips**, **36 Rust passed**, **13,737 collected**, zero failures. Its six stages were toolchains, Lean build, Lean audit, Rust build, Rust tests and pytest ([`gate.json`](evidence/gate.json)).

Lean audit: **464 source files**, **5,045 audited theorems**, standard axioms only. RD-4b statement check: 16 exact declarations, 6 theorems, 0 pending. The focused RD-4b suite passed 160 tests, with 21 more focused checks after the final gap-binding change; the five gate-fix tests passed after the first gate identified stale expectations.

The full gate on the final report commit is recorded separately after this evidence is committed. The saved code-head gate remains the immutable source of the numbers above.

## Acceptance checks (AGENT)

The following test IDs were collected and passed in the code-head gate (fixture numbers F-C1 and F-C11–F-C17, conservativity, schema and request binding):

- `tests/test_readings_components_document.py::test_fc1_check_three_components_conflict_free_with_a_model`
- `tests/test_readings_components_document.py::test_each_case_is_answered_as_a_document_of_its_own`
- `tests/test_readings_components_document.py::test_fc1_render_reads_each_set_in_its_component`
- `tests/test_readings_components_document.py::test_a_query_typed_in_one_component_is_all_with_e30`
- `tests/test_readings_components_document.py::test_fc14_conclusion_typing`
- `tests/test_readings_components_document.py::test_fc13_under_names_sets_of_the_query_s_component_only`
- `tests/test_readings_components_document.py::test_fc11_a_narrowing_is_listed_under_its_component_only`
- `tests/test_readings_components_document.py::test_fc12_an_unseparated_set_stays_in_main_with_w2_s_unknown`
- `tests/test_readings_components_document.py::test_fc15_none_needs_every_other_component_consistent`
- `tests/test_readings_components_document.py::test_fc17_all_is_gated_on_every_other_component`
- `tests/test_readings_components_document.py::test_fc16_a_choice_without_evidence_leaves_its_component_undecided`
- `tests/test_readings_components_document.py::test_fc17_main_conflict_evidence_missing`
- `tests/test_readings_components_document.py::test_without_companions_nothing_changes`
- `tests/test_readings_components_document.py::test_a_component_outside_the_completion_is_refused`
- `tests/test_readings_components_document.py::test_operational_failures_are_unavailable`
- `tests/test_readings_components_lean.py::test_the_genuine_answers_cover_every_result_form`
- `tests/test_readings_components_lean.py::test_every_retyped_or_dropped_field_is_refused`
- `tests/test_readings_components_lean.py::test_every_emptied_or_duplicated_row_list_is_refused`
- `tests/test_readings_components_lean.py::test_every_rebound_identity_is_refused`
- `tests/test_readings_components_lean.py::test_a_component_s_status_that_is_not_its_own_is_refused`
- `tests/test_readings_components_lean.py::test_the_sentence_is_the_request_s`

The fuzz retypes, drops and rebinds fields of genuine conflict, premises, ALL, NONE and UNKNOWN product answers. It empties or duplicates request rows and checks that they are refused. Lean alone computes the contents of filled-gap cones; the schema types every gap triple and the relay binds shown evidence to the request.

## Seeded failures (AGENT)

Each fault was planted in changed code, its named test failed, and the original bytes were restored. [`mutants.json`](evidence/mutants.json) holds the failing output and restoration digest.

| Fault | Failing test |
|---|---|
| `companion-route` | `tests/test_readings_components_document.py::test_fc1_check_three_components_conflict_free_with_a_model` |
| `product-verdict` | `tests/test_readings_components_document.py::test_fc17_all_is_gated_on_every_other_component` |
| `response-unit-binding` | `tests/test_readings_components_lean.py::test_every_emptied_or_duplicated_row_list_is_refused` |
| `gap-name-binding` | `tests/test_readings_components_lean.py::test_every_rebound_identity_is_refused` |
| `english-conclusion-slot` | `tests/test_readings_components_document.py::test_a_query_typed_in_one_component_is_all_with_e30` |
| `split-citation-content` | `tests/test_readings_components_document.py::test_fc11_a_narrowing_is_listed_under_its_component_only` |

## A/B and limits

The branch-point main and code-head recordings each contain **60,073 records**: 18,870 probe, 39,612 conformance, 454 pilot
documents and 1,137 readings cases. The raw comparison has **60,066 same** and **7 wording** differences, all seven
the absolute scratch path in the stderr of the same missing-sense-pack pilot probes. Both sides exited 1 with the
same failure text apart from `/tmp/rd4b-ab-base-pilots-final.pilots/pack.json` versus
`/tmp/rd4b-ab-head-final.pilots/pack.json`. Replacing only that path in those seven stderr fields and ordering records by their case keys gives byte-identical
normalized recordings (SHA-256 `4809a12c30abe078f983a987f84ca1f2b69b3d2d85595f99497b793e378ecedc`):
**60,073 same, 0 unlisted**. [`ab.json`](evidence/ab.json), [`ab-raw-compare.json`](evidence/ab-raw-compare.json)
and [`ab-normalized-compare.json`](evidence/ab-normalized-compare.json) preserve the raw differences, the two
recording hashes, the exact normalization and the tool's comparison result. The branch-point main Lean service was rebuilt from the
clean `0d93e591` checkout; its Rust binary has a digest pinned by main's `checkers.lock`.

**Not run:** live model calls (the task forbids them), a new latency benchmark, and any independent DRI signoff. The full non-live gate ran.

## Review ownership

- **AGENT:** implementation, proved statements, response binding, seeded failures, frozen manifests, focused and full gate checks.
- **HUMAN:** review the product English in actual companion documents and assess latency on deployment hardware; deferred to the project owner.
- **EXTERNAL:** DRI statement re-review or trust-budget signoff if required by the project process. The 16 RD-4b statements are exact, so no statement amendment is requested; the trust map still reports growth against its older signed baseline.

## Build checklist

| # | RD-4b disposition |
|---|---|
| 1 | The generated Lean response shape is the contract for relayed rows; diagnostics are Lean’s. |
| 2 | Differential corpus A/B is recorded below; Rust has no product-fold authority. |
| 3 | W7 checks rendered English; the existing normalization contract applies. |
| 4 | Generated schema, request binding and per-field fuzz cover relayed answers; bool-for-int is rejected. |
| 5 | Malformed companion and reference cases are in the RD-4a and RD-4b suites. |
| 6 | Lean’s three-valued folds and the gate preserve UNKNOWN for missing evidence. |
| 7 | The existing public operation budget wraps the Lean call and Python evidence preparation. |
| 8 | Product result forms are proved against the generated shape. |
| 9 | E30–E32 rendering passes W7; F-C1 and query tests cover the new sentences. |
| 10 | `ve document` uses the one Lean split and product route; route-entry tests cover check, render and query. |
| 11 | No new parser for a real language was added. |
| 12 | No state machine or ledger was changed. |
| 13 | Six seeded code faults each produced a real failing test. |
| 14 | Tests use temporary documents and no live model calls. |
| 15 | Meaning IDs remain Lean’s; request identities are rebound by fuzz tests. |
| 16 | Audit, frozen hashes, response schema, assurance, trust classes and gate collection were refreshed. |
| 17 | The statement checker reports 16 exact RD-4b declarations, zero pending. |
| 18 | F-C13–F-C17 exercise both acceptance and refusal directions. |
| 19 | No new use-case rule was formalised in this batch. |
| 20 | This report’s numbers are tested against saved gate and scope evidence. |
| 21 | AGENT, HUMAN and EXTERNAL owners and deferrals are recorded above. |
| 22 | All files are committed and the final clean-HEAD gate is run after the report commit. |

## Review fix round (`rd-4b-review.final.md`)

Each B finding was fixed as a class, with a regression test. The evidence above belongs to the code head before review and is kept unchanged.

| Finding | Class removed | Fix | Regression tests |
|---|---|---|---|
| B1: a companion sentence before a main one failed with CheckerUnavailable | Python and Lean disagree on the order of a list of the document's units | Lean lists `decided_units` in the document's own order (`documentOrder`) | `test_every_order_of_sentences_and_sets_gets_the_same_answer` (every order of F-C1's units and sets, through check, readings and render), `test_fc17_with_its_companions_first_gets_the_same_answer`, `#guard`s in `ComponentsExamples.lean` |
| B2: untyped `environment`, `document` and `checked`; load checks outside the guard, so raw TypeError and ValueError escaped | malformed untrusted answer crashes, or is accepted unbound | the schema types the three fields as objects (`asObject`, proved to fit); every check of a Lean answer runs inside one guard (`relayed`); each case is bound to the request by its name (`_bind_part`, `_bind_merged`) | `tests/test_readings_components_load.py`: a fuzz retypes, drops, empties and duplicates every field of F-C1's and F-C17's load-time answers, and only listed Lean-owned values survive; plus the finding's own probes and swapped or invented case rows |
| B3: the document's UNKNOWN had no English | an UNKNOWN worded nowhere (one case or the product) | `gateItems` names the choice by E12: R4 with the checked witness under a CONFLICT, the new R8 for an uncertified status, the new R9 for a missing result. It is used by RD-3's `planItems` and by `productPlan`, which names the other sentence's choice | F-C17 through `ve document readings` (R4) and with main's evidence withheld (R8); RD-3's missing-evidence test (R8, R9); F-ND2's gated query; M8's gated query |
| B4: no SR4 fixture, no checks of 8.4's computed rows | spec rows without a fixture | `ComponentsExamples.lean` `#guard`s every row of 8.4's 1.10 list in each direction | `test_sr4_conflict_under_one_choice_and_unknown_under_the_other_is_not_decided`: F-C17's main case is decided with all its evidence (CONFLICT, CONFLICT-FREE) and not with one choice withheld (CONFLICT, UNKNOWN) |

What did not change: the RD-3 and RD-4b theorem statements (the statement checker passes, and `Line` keeps its approved text). The plan lemmas `witnessItems_label`, `conflictRowItems_label`, `gateItems_label` and `unknownItems_label` keep `plan_conditions_only` proved. `asObject_fits` keeps the response encoders proved.

Seeded failures (AGENT): when the guard in `load` is removed, `test_a_case_s_frame_of_another_type_is_refused` fails with a raw `Invalid`. When `_bind_part` is skipped, `test_each_case_is_bound_by_its_name` fails.

Verification (AGENT): `lake build` passes. `python3 lean/audit.py` passes with 465 source files and 5,050 audited theorems, standard axioms only. `tools/lean_statements.py` adds only the four lemmas. `VE/Route/frozen.py` passes. The full suite at `-n 16` on this code (`ae014c0d`) gave 13,648 passed, 8 skipped, 83 xfailed and 2 failed:
- The first failure is `test_review_b2_conflicting_reading_certifies_no_entailment`, which expected no English for a gate UNKNOWN. It now expects the witness line, and it passes.
- The second is `test_difffuzz.py::test_ci_run`, which took 336 CPU seconds against a 300-second budget under suite load. It passes alone.

**HUMAN / EXTERNAL:** the R8 and R9 sentences are new W7 wordings and need DRI sign-off (spec 2.1). The trust map still reports growth against its older signed baseline, now including this round's lines. Not run: a new A/B recording and the saved gate evidence for this round.

## Recheck fix round (`rd-4b-looprecheck1.final.md`)

| Finding | Class removed | Fix | Regression tests |
|---|---|---|---|
| B2: a companion case could carry a unit its set does not cite (`u0` in `rs_a`, stored as `['u0', 'u_a']`) | the relay binds the split's rows to the request only in part: it checks that they exist and come from the request, not where they belong or in which form | `_projection` gives each case's document as Lean's split makes it (`mainDoc`, `componentDoc`). `_bind_part` requires the answer to match it member for member and row for row. The multiset copy checks are gone, because the projection covers them | `test_a_companion_case_holding_an_uncited_unit_is_refused` (the finding's probe, with `u0` in each form a split gives a unit); `test_every_graft_of_a_request_row_into_a_case_is_refused` over F-C1, F-C11 and F-C17: every unit, set, narrowing and coupling of the request is inserted into every case, each case's units are swapped to other forms, and its lists are reversed; `test_a_cited_unit_is_carried_by_id_alone` |

The graft fuzz found a second hole of the same class on the old code: the main case could carry a unit by id alone, without its `kind`. The old binding let 4 of the 5 new tests pass mutants through. With `_projection`'s check replaced by `_need(True)`, the same 4 tests fail. Lean's split was already right: `CompanionsExamples.lean` guards `rs_a`'s units as `["u0", "u_a"]`, with `u0` by id. No Lean or theorem statement changed.

Also fixed: `ve.readings_components` had no layer in `tools/layer_policy.py`, so `tools/check_python_layers.py` refused the graph. It is now in layer 4 (`.importlinter` regenerated, `docs/ARCHITECTURE-LAYERS.md`).
