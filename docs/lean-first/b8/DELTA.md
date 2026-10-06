# Lean-first batch 8: reports

## Scope and public delta

Lean now returns the reports environment, meaning IDs, unit and document statuses, residual lines, and display lines from the same decoded report document. The Python `ReportsDocument` keeps only accepted input and the containers needed by existing callers. The route reports `BridgeHolder` and `MissingBridgeRecord` before the generic graph failure. The reports Python elaborator, identity calculation, status folds, and residual classifier were deleted in this batch.

Production `ve/*.py` changes delete **695 lines** and add 70 relay/container lines (net −625). The Lean sources add **257 lines** and delete 37 (net +220), including the generated response shape and proof. This is a behavior migration batch, not a speed optimization; the section 4 reports route keeps its 60-second operation budget.

The section 5.1 A/B recorder compared 66,247 public results against `9aaf918d`: 18,870 Stage-0 probes, 39,612 conformance operations, 1,137 readings cases, 6,350 discourse results, and 278 historical pilot documents. Every result was identical; `wording`, `order`, `verdict`, and `availability` deltas are empty, as is `unavailable_both`. No DRI delta signature is needed for those corpora. The final status-text extension affects only the internal reports route; the historical pilot corpus has no reports document. The batch-profile A/B (`profile_ab.py`) compares the old Python implementation with the new relay on elaboration, document and meaning IDs, unit statuses, and residual lines for 1,000 generated reports trees: **1,000 identical, zero changed**.

The raw A/B records were kept outside the commit at `/tmp/ve-lf8-base-all.jsonl`, `/tmp/ve-lf8-head-core.jsonl`, `/tmp/ve-lf8-head-readings.jsonl`, and `/tmp/ve-lf8-head-rest.jsonl`. The compact gate evidence below is committed. The frozen Python oracle remains at the plan's batch-0 tag.

## Deletion ledger

| Deleted Python decision | Lean owner now called |
|---|---|
| `ReportsDocument` profile, record, span, context, assessment, unit, content, bridge, scoped, and metadata rejections | `Attribution.Wire.decodeEnvironment`, `decodeDocument`, `decodeContent`, `firstFailure`, and `Attribution.Admission` |
| `_canonical`, `_id`, document/meaning/content IDs and generated environment identity | `Attribution.Content.documentId` / `contentId`, `Route.Wire.meaningId`, and `Attribution.Run.elaborated` |
| Generated predicates, premise formulas, open terms, bridge formulas, and warnings | `Attribution.Wire.generated` and `Attribution.Run.elaborated` |
| `fold_status`, `verdict_status`, `unit_status`, `statuses`, and scoped verdict cross-check | `Attribution.Status` and `Attribution.Run.runStatus` / `scopedVerdict` |
| `unreviewed_acts`, `unformalised_kinds`, `residual_lines`, and the reports branch of `document.coverage` | `Attribution.Run.unreviewedActs`, `unformalisedKinds`, `residualLines`, and `runStatus` |
| `reports_route.checked_elaboration` and the eight-field Python/Lean comparison | `reports_route.run_case` relays the checked Lean row directly |

The `reports-content` route checks a parsed manifest node and supplies its meaning ID, so the English renderer does not hash it in Python. The reports extended `Environment` is constructed only after Lean accepts its returned JSON; failure to construct or bind it is operational `CheckerUnavailable`.

## Verification

The acceptance items are **AGENT**: Lean build and audit, schema generation, affected tests, full suite, A/B corpora, fuzzer, seeded failures, and clean-HEAD gate. **HUMAN**: DRI review of wording and the remaining P0 premise display line is deferred to the DRI; no DRI approval is inferred from this report. **EXTERNAL**: none.

The trust declaration table was reseeded to classify the 150 declarations missing from the inherited table, and its measured step figures in `docs/CONSOLIDATION-PLAN.md` were refreshed. The optional `tools/trust_map.py --check` budget comparison still fails in both this branch and the base checkout on the inherited S/V signed-allowance overrun. This batch adds no changed VE theorem statements; `tools/lean_statements.py` reports zero added, removed, or changed statements. The new response-shape helper theorems are in `ResponseShape/Audit.lean` and the axiom audit.

The build checklist's applicable checks are exercised as follows: one Lean diagnostic and status owner (1, 8); malformed and two-fault report fixtures plus the differential fuzzer (2, 5); shared text fixtures and the reports English round trip (3, 9); generated response schema with field mutation tests and bound IDs (4, 15); scoped UNKNOWN on missing, stale, or unreplayed evidence (6); service deadlines (7, 14); `check_document`, direct route, English render/parse, and graph admission call the same Lean reports path (10); Lean compiler and decoder supply syntax and JSON decisions (11); seeded mutants demonstrate the gate can fail (13); report and route registries are exercised by the full gate (16); frozen-source hashes and statement diff are checked (17); generated report numbers are traced to the A/B evidence (20). Checklist items 12, 18, and 19 concern state ledgers, new spec theorems, and use-case answer keys; this batch changes none of those. Item 21 is tagged above. Item 22 is recorded after the final clean gate.

Five seeded defects failed targeted tests and were removed: document identity forced to zeros; every unit forced `CHECKED`; residual lines emptied; Lean status lines emptied; and Lean bridge-specific diagnosis suppressed. The reproducible scripts are `seeds.py` and `lean_seeds.py`; `evidence/mutants.txt` names each failing test.

## Gate result

The A/B corpus is unchanged as recorded above. The generated statement diff has zero additions, removals, and changes. The Lean build passed 743 jobs; the axiom audit passed 4,314 named theorems in 408 source files. The focused report/document suite passed 219 tests. The paired differential fuzzer's CI run and 14 dated seeds are **15/15 equal** on findings, new signatures, and baseline replay; CI has zero new signatures and 351 baseline entries seen on each side. The deep seeds have 682 new signatures on each side, all already present in the base checkout's matching runs. `evidence/difffuzz.json` records each pair. The first clean-HEAD full gate found stale decoder pins, trust and collection tables, a missing `reports-content` case, and an open reports environment response shape; these were corrected. The second clean-HEAD gate passed 11,074 Python tests but found a stale generated assurance-manifest table; that table was regenerated and its focused test passed. The final clean-HEAD full gate is run after this report is committed; its result is reported in the handoff.
