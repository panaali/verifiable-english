# Build checklist disposition, batch 11b

This applies `/home/seyran/code/manage-agents/prompts/build-checklist.txt` to the W2 caller switch. The DRI signoffs named below are gate blockers, not implied approvals.

| # | Disposition and evidence |
|---:|---|
| 1 | The route's Lean `rejectionCode` and text are relayed without Python content diagnostics. W2 JSON is decoded by the existing restricted wire reader. `tools/wire_contract.py --check` is part of the full gate. |
| 2 | The frozen Python/Lean W2 single- and two-fault corpus remains in `test_speech_source_lean.py`; the global Py/Lean/Rust differential fuzzer's CI and 14 date seeds have equal base/head signatures and answers in `evidence/difffuzz-ab.json`. Rust has no speech-act implementation. |
| 3 | English wording continues to use the one `speech_english` owner until E3. The existing speech conformance fixtures exercise NBSP, whitespace, Unicode and control cases at inline, fence and route entry points; 11b adds no text normalizer. |
| 4 | The transport checks the report's structural fields, request row binding, typed IDs, coverage counts and bool-for-int. `test_every_producer_field_is_required_and_typed` drops and retypes each actual producer field; the route test pins the output fields to Lean's emitted report. The W2 response shape is still a structural table in the adapter until the route joins the generated service schema. |
| 5 | Existing W2 single-fault and deep-input tests cover malformed JSON trees and reference checks. The new adapter's operational failures are `CheckerUnavailable`; Lean content rejections remain `VEError`. |
| 6 | An absent premise witness is `UNKNOWN` in `Run.decodePremiseStatus`; no budget exhaustion becomes false or success. The experimental speech CLI has no caller-supplied zero-budget option. |
| 7 | Route calls use the configured transport timeout, and the Python witness proposal has finite proof/model/evaluation budgets. The experimental CLI has no public operation deadline; adding one belongs to F4 rather than this switch. |
| 8 | Lean's W2 source and record kind matches are exercised by `test_every_record_kind_is_replayed`; coverage reconciliation and CHECKED status are checked by `test_template_reports_cover_every_class_and_record`. No kind was added in 11b. |
| 9 | English E3 is external to this batch. The existing parser supplies fence ASTs; Lean checks the resulting structure. The English derivation is explicitly unproved, never claimed CHECKED by 11b. |
| 10 | `ve speech-acts` and `load_speech_document` call `SpeechSource`, which calls one Lean route. `test_public_speech_projection_matches_frozen`, `test_fenced_english_is_checked_after_resolution`, and `test_cli_shows_checked_nomination` cover the public paths. No `migrate` speech entry exists. |
| 11 | JSON uses the standard restricted parser; import and declaration inventories use their library/compiler readers. No language parser was added in this batch. |
| 12 | No state machine or ledger behavior was changed. |
| 13 | Three independent seeded faults in identity, answer display and fence resolution each failed a named test and were restored; see `evidence/mutants.txt`. |
| 14 | Gate runs use the project's hermetic environment and pinned, rebuilt binaries. New file-writing tests use `tmp_path`; subprocess tests use `HANG_TIMEOUT`. The first full gate's load-sensitive service timeout is recorded for rerun. |
| 15 | W2 document/source identity and removable-weight tests remain in `test_speech_source_lean.py`; seven public templates match frozen IDs. `test_source_transport_fails_closed_on_tampered_report` checks ID type and binding. |
| 16 | The gate collection gained only intended test IDs; the Lean frozen-source inventory and trust class table were updated. `tools/relay_lint.py` includes both new relayed modules. |
| 17 | `tools/lean_statements.py --check`: 4,211 statements, no additions/removals/changes. `tools/check_lean_imports.py` passed; generated assurance tables and source hashes are pinned. No theorem statement changed. |
| 18 | No new spec-stage theorem or iff was introduced in 11b; 11a owns the W2 source/admission theorems. |
| 19 | No use-case rule was formalised in 11b; historical use-case/pilot checks are in the A/B corpus and full gate. |
| 20 | `test_batch_report_metrics_match_evidence` runs `report.py`, regenerating the numeric block of `DELTA.md` from the evidence JSON and source diff. Full-gate counts are cited from the gate JSON after the clean-HEAD run. |
| 21 | `DELTA.md` tags agent, human and external items. The three availability rows and Lean-CPU exception explicitly await the speech-acts DRI; English E3 is external. |
| 22 | Source, tests, pins and this nonempty report are committed before the final full gate on clean HEAD. Free disk is checked and reported with the final gate result. |
