# English Lean E2 integration report

Branch `english-lean-e2/integrate`. The Python and Lean branches were merged locally. This report records the integrated implementation and the remaining acceptance work; it does not grant approval to any open item.

## Implementation

- `english.admission` calls the persistent Lean service for its reading. The three public admission functions share `_parse_english_document`; marked conclusions use Lean's obligation list and Python's existing entailment checker.
- For public formula admission, the Python hand parser and Lark audit run only when `VE_ENGLISH_COMPARATOR=1`. Comparator results are logged and cannot decide the public verdict. E3 statement wording still uses its checked Python all-derivations reader.
- `english.check` checks rendered candidates and canonical display. The Python boundary validates E2 response fields, formulas, spans, obligations, classes and all six request identities before use.
- The Lean request policy now guards `senses.read`; its approved theorem is proved. The lexicon action lock includes that trusted module.
- Lean reduces reports, readings and speech-act declarations to their formula typing view; the E3 statement layer checks its generated decision wording before display. The pilot readings document uses a V3-valid act wording with re-bound model IDs.
- The S2/S3 specification fixtures are compared by Python, the Lean reader and the W7 route in `tests/test_english_lean_route.py::test_three_way_conformance_on_the_spec_fixtures`.

## Evidence and open points

The exact E2 statement diff finds 11 of 12 declarations. `decode_encode` remains unproved. The Lean tree contains no `sorry` or extra axiom for it. E2 acceptance remains open until the proof and the applicable checklist work below are complete.

The clean gate on `38eb65ff` passed: **11,275 Python tests passed, 7 allowed skips, 0 failures; 50 Rust tests passed**. Its complete result is [e2-gate-result.json](../../conformance/english-lean/e2-gate-result.json), and `tests/test_english_e2_report.py::test_report_counts_follow_gate_json` checks the numbers above against that file. The S3 comparison records **200 cases, 198 agreements, 2 disposed differences, 0 unexplained differences**; the same test derives these figures from the case records.

Three temporary mutations were introduced into `ve/backends/english_lean.py`, each made `tests/test_english_e2_relay.py` fail, and each was removed:

1. `bool-for-int`: `isinstance(value, int)` accepted a Boolean as a natural index (`/tmp/e2-mutant-bool-for-int.log`).
2. `identity-unbound`: skipping the identity comparison admitted a substituted `environment_id` (`/tmp/e2-mutant-identity-unbound.log`).
3. `empty-premise`: allowing an empty obligation premise list admitted a marked conclusion without premises (`/tmp/e2-mutant-empty-premise.log`).

## Build checklist

The statuses here refer to the integrated E2 work. An open status means the line is **not done**, even if part of it has evidence.

| Line | Status | Evidence or remaining work |
|---|---|---|
| 1. Single generated contract | Open | Lean owns public English diagnostics, but the E2 result schema and Python's validation tables are still hand maintained. |
| 2. Differential fuzz | Open | The S2/S3 three-way fixtures run; the requested 1- and 2-fault Py/Lean/Rust matrix is absent. Rust has no English reader. |
| 3. Shared normalization | Open | Existing normalization fixtures run; the full character matrix across every English entry point is absent. |
| 4. Untrusted output schema | Open | Python validates E2 fields, counts, formulas and identities and rejects bool-for-int; the Lean-derived inner result schema and every-field mutation matrix are absent. |
| 5. Malformed JSON nodes | Open | S3 malformed requests run; every-node seven-shape/deep replacement coverage is absent. |
| 6. Three-valued verdicts | Open | The relay preserves Lean budget and proof status; budget-zero coverage for every public operation is absent. |
| 7. Whole-operation deadlines | Open | Service deadlines exist; delay injection across the complete Python admission path is absent. |
| 8. Kind and owner folds | Not applicable | The integration changes no kind/owner fold. |
| 9. English roundtrip | Open | Rendered candidates pass `english.check`; all-constructor unique-derivation roundtrip coverage is absent. |
| 10. Single admit entry | Open | The three public formula admission functions share `_parse_english_document`; the full CLI/view/formatter/migration inventory and metamorphic test are absent. |
| 11. Language parsing | Done | New Lean policy uses explicit scanners, and E2 transport uses JSON libraries rather than regex parsing of a programming language. |
| 12. State machine and ledger | Not applicable | No state-machine or event-ledger code changed. |
| 13. Seeded mutants | Done | The three seeded boundary bugs above each failed a committed test and were removed. |
| 14. Hermetic tests | Done | The clean-HEAD full gate on `38eb65ff` passed with a clean source identity; the Rust cache was seeded into the gate's isolated Cargo home. |
| 15. Identity binding | Open | All six E2 request identities have mutation tests; the requested per-field schema identity matrix is incomplete. |
| 16. Registered lists | Done | Grammar lock, frozen inventory, theorem inventories, service modes and test collection are generated or checked. |
| 17. Statement diff | Open | The exact checker finds 11/12; `decode_encode` is unproved. |
| 18. Spec-stage fixtures | Open | S2/S3 three-way fixtures and E2 Lean guards exist; the complete E2 iff-boundary matrix is absent. |
| 19. Use-case formalisation | Not applicable | This merge changes no use-case rule or answer key. |
| 20. Regenerated report numbers | Done | The gate JSON and S3 case records are committed; `tests/test_english_e2_report.py::test_report_counts_follow_gate_json` checks the printed counts. |
| 21. Acceptance ownership | Open | The E2 acceptance cases and DRI rulings still need complete AGENT/HUMAN/EXTERNAL ownership tags with test IDs. |
| 22. Handoff | Open | This report commit still needs its own clean-HEAD gate and final disk check. |

## Acceptance ownership

The E2 decisions D1–D18 and fixture obligations in section 8 are AGENT-owned implementation checks. The following bounded review is HUMAN-owned and deferred to the English E2 DRI: approval of the `decode_encode` proof and of any changed theorem statement. The requested run forbids model calls, so no external reviewer was invoked. No EXTERNAL acceptance item has been identified for this code-only integration.

| DRI decision | Owner | Evidence or deferred test |
|---|---|---|
| D1–D4: policy and V6 | AGENT | `VE.EnglishGrammar.policy_selection`, `VE.EnglishGrammar.ProfileExamples` guards; complete parity matrix open |
| D5–D7: new fields, display identity, boundary | AGENT | `tests/test_english_lean_route.py::test_every_identity_is_the_adapters`; use-case boundary matrix open |
| D8: request order | AGENT | `VE.EnglishGrammar.admitRequest_policy`, `VE.EnglishGrammar.grammarFault_none`; mode mutation matrix open |
| D9–D12: response class, obligations, advice | AGENT | `tests/test_english_lean_adapter.py::test_class_and_span_are_part_of_diagnostic_schema`; full advice matrix open |
| D13: formula decoder | AGENT, HUMAN proof approval | `decode_encode` is open; owner: English E2 DRI |
| D14: prepared grammar cache | AGENT | open; cache hit/miss fixture IDs ev3 and ev3b |
| D15: comparator | AGENT | `tests/test_english_lean_adapter.py::test_comparator_failure_cannot_change_lean_verdict` |
| D16–D17: producer and overlay refusal | AGENT | `tests/test_english_e2_python.py::test_overlay_refusals_can_be_deferred_for_lean_admission`; full overlay matrix open |
| D18: modal form order | AGENT | Lean `Env.decode` modal order; md4 direct boundary fixture open |
