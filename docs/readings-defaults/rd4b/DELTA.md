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
