# Lean-first batch 11a: fix report and gate record

Base: `2ce1134e` (before this batch). Branch: `lean-first/b11a`. This is the Lean-side half of row 11: 8.5's wrapper **and admission**. `speech-source` reads the W2 source wrapper, projects coverage, replays answer, judgment (`follows`, `gap`) and compliance (certificate, external `done` unit) evidence, and emits nominations; `admission` admits the payload's claim graph over W2's P0 projection with binding units withheld and the two route-local speech leaves (`Source/Admission/Run.lean`). No Python caller changes and no Python semantics are deleted. Batch 11b owns only that switch and deletion.

## Acceptance and ownership

| Item | Owner | Evidence or state |
|---|---|---|
| 8.5 source wrapper, document/source/environment IDs | AGENT | `Source/Run.lean`; `test_templates_agree_with_python`, `test_document_id_excludes_removable_weights_only` |
| W2 statuses, bytes and residual coverage | AGENT | `coverage_partition`; `test_template_reports_cover_every_class_and_record` |
| Answer, query and compliance replay | AGENT | `answers_sound`, `query_records_sound`, `gap_records_sound`, `external_records_sound`; `test_every_record_kind_is_replayed` (one valid record of every 3.3/5.4 kind), `test_gap_judgment_records_replay_their_model`, `test_external_compliance_names_an_asserted_done_unit`, `test_answer_records_replay_their_evidence`, `test_premise_status_evidence_comes_from_the_case` |
| 8.5 admission: `SpeechAdmitted`, claim graph, `bindings_withheld`, `active_commands`, `speech_wire_acceptance` | AGENT | `Source/Admission/Run.lean`; `test_admission_admits_the_claim_graph_over_the_projection`, `test_admission_rejects_leaves_without_provenance`, `test_binding_units_are_withheld_from_p0_and_classed`, `test_admission_layer_leaves_are_the_regenerated_policy`, `test_admission_entry_points`, `test_admission_graph_type_confusion_is_a_bounded_rejection`, `test_every_spec_8_5_name_has_a_lean_owner` |
| Nomination records and narrowing | AGENT | `test_nominations_name_a_candidate_of_the_bound_set` |
| Statement review of the new theorems (8.5's as implemented over the wrapper, and the record theorems) | HUMAN (speech-acts DRI/reviewers) | Deferred: statements and their dependencies are in `lean/statements.txt`, `lean/SPEECH-ACTS.md`; no approved statement was changed. |
| English fences | EXTERNAL (English E3) | Explicitly open; `speech-source` and `admission` answer `NotImplemented: fenced English content`. |

The shared W2 readers of `Discourse/Loader.lean` have two check modes. With `python` (the speech-source wrapper only) they give Python's `validate_*` order and texts and type open-term conditions; without it (the discourse route, which Python relays verbatim) they run the base code path unchanged. `lean/SPEECH-ACTS.md` lists the definitions, theorem meanings and open boundaries.

## Review response (lf-11a review, B1 to B3)

| Finding | Class removed | Fix | Regression tests |
|---|---|---|---|
| B1: row 11a's 8.5 admission was missing and reassigned to 11b | a required spec item silently left out | `Source/Admission/Run.lean`: `SpeechAdmitted`, `admitSpeech` (P0 projection `p0Json` without binding units, the `speech:presupposition:<u>` and `speech:answer:<u>:<a>` leaves, W1 layer and profile leaves, bindings, graph check, citations, choices), the report id over the 3.5 document id; theorems `bindings_withheld`, `active_commands`, `report_consequence`, `records_sound`, `speech_wire_acceptance`; the `admission` kind on a payload | the admission tests above; `test_every_spec_8_5_name_has_a_lean_owner` fails when any 8.5 structure, definition or theorem has no Lean owner or named stand-in |
| B2: Python-visible discourse diagnostics changed without a signed DELTA | a shared Lean decoder changed for one route moves another route's relayed answers | the loader's `python` mode (`Loader.field`): the discourse route runs the base code path; only speech-source reads Python's texts and typing | `test_w2_front_matter_diagnostics_are_pinned`: 882 single-fault mutants of open terms, reading sets, narrowings and meanings answered by the discourse route equal the answers recorded from the base route (`tests/data/w2-front-matter-pins.json`; the pre-fix head differed on 183); `test_ill_typed_open_term_condition_keeps_its_base_answer` |
| B3: a valid model-backed `gap` record and external compliance were rejected | spec'd record branches not implemented | `gapRecord`, `externalRecord`, `doneFact`; records in one ordered list (also follow-up C1) | `test_every_record_kind_is_replayed` (8 kinds), `test_gap_judgment_records_replay_their_model` (the record line equals `speech-consequence`'s for the same model), `test_external_compliance_names_an_asserted_done_unit` |

Proposed, not applied (needs a DRI signature, plan 5.1 item 2): on the discourse route, an ill-typed open-term condition is today `CheckerUnavailable` (Lean admits, Python's `validate_open_terms` rejects). Typing it in the discourse mode would make it Lean's rejection with Python's text (`availability`), and the malformed-field texts of the W2 readers would become Python's (`wording`, 183 pinned mutants). Until signed, the pins hold the base answers.

## Behaviour and gate 5.1

- **Suite:** the batch tests passed (67 tests in `test_speech_source_lean.py` and `test_discourse.py`). The gate collection was refreshed with 37 new test IDs and no removals. The hermetic full gate at `3877e6e2` passed: 11,481 Python tests passed, 7 allowed skips, 49 Rust tests passed, and no failures. Its validated counts and clean-worktree record are in `evidence/full-gate.json`. The final committed HEAD is gated again after this report commit.
- **Corpus A/B:** Python-visible files and the public Python dispatch are unchanged. Against base `2ce1134e`, the probe, conformance and readings corpora have 59,619 identical records (`evidence/core-compare.json`); the pilot comparison has 278 identical results; the discourse comparison has 6,350 identical results. All five corpora total 66,247 identical records, with no unlisted difference. The speech-source template and single-fault differential tests compare the new route to the frozen Python wrapper and pin every known diagnostic wording class. The recorded A/B tool does not include the separate use-case harnesses; their pinned answer-key tests passed in the full suite.
- **Differential fuzzer:** 14 date seeds, 2026-09-21 through 2026-10-04, were run on both base and head with the same one- and two-fault sample. Counts, sampled answers, finding signatures and baseline replay match for each seed (`evidence/difffuzz-14-seeds.json`): zero head-only signatures. The first 13 seeds each have existing signatures absent from the reviewed baseline on both revisions (677 appearances across samples, not 677 distinct findings); the 2026-10-04 CI seed has none and passes. The fuzzer baseline therefore does not grow in this batch.
- **Deletion ledger:** no deletion is planned for 11a; the Python wrapper remains the current caller. The new Lean route is selected only by the new `speech-source` kind. Batch 11b will map Python decision sites before deleting them.
- **Latency:** `evidence/speech-source-cpu.txt` measures 50 calls per template: 5.45–15.67 ms CPU per case including startup share. No existing operation has a new call, so its budget does not change.
- **Lean assurance:** `tools/lean_statements.py --check` reports 3,936 statements with zero changed relative to the pinned inventory; `lean/audit.py` audits 3,936 named theorems with standard axioms only; the frozen source check passes. New statements and declarations are inventoried and pinned in this batch's commits.

There is no `DELTA` of Python-visible verdict, wording, order or availability to sign. Python rejects nomination records because it does not implement them; the new Lean-only case implements the specified narrowing result and is not called by Python yet.

## Seeded bugs: tests can fail

Each mutation was applied to one file alone (M1 to M3 and M7 `Source/Run.lean`, M4 to M5b `Source/Admission/Run.lean`, M6 `Discourse/Loader.lean`), rebuilt with `lake build ve_speech_acts_route ve_discourse_route`, tested, removed, and rebuilt clean. The raw failures are in `evidence/mutants.txt`.

| Seed | Changed behaviour | Failing test |
|---|---|---|
| M1 | Report `source_id` in the `document_id` field | `test_templates_agree_with_python`: document IDs differ |
| M2 | Populate `bytes_by_class` with status counts | `test_template_reports_cover_every_class_and_record`: class keys differ |
| M3 | Count duplicate nominations as separate choices | `test_nominations_name_a_candidate_of_the_bound_set`: duplicate testimony becomes `CLARIFICATION-OPEN (multiple)` |
| M4 | `p0Json` keeps binding units (review B1) | `test_binding_units_are_withheld_from_p0_and_classed`: the admission fails on P0's kind decoder |
| M5 | An answer leaf's formula is not compared (review B1) | does not build: `answerLeaf_entailed` and `report_consequence` no longer prove |
| M5b | A presupposition leaf's formula is not compared (review B1) | `test_admission_rejects_leaves_without_provenance[node3]`: `reviewed(atlas)` is admitted as `speech:presupposition:p` |
| M6 | The loader's discourse mode uses Python's texts (review B2) | `test_w2_front_matter_diagnostics_are_pinned`: 183 discourse answers move |
| M7 | A `gap` record is accepted when the model satisfies the target (review B3) | `test_gap_judgment_records_replay_their_model`: no `AnswerMismatch: f` |

## Build checklist disposition

1–3. The new route calls existing Lean decoders and replay owners. One- and two-fault wire mutations, Unicode wording and ASCII whitespace/control fixtures are in `test_speech_source_lean.py`. The English parse remains E3's owner.
4–5. The route checks the strict record schema, references, IDs, and deep JSON bound. Mutations include null, booleans and wrong container types; `test_deep_input_is_a_bounded_rejection` checks 300 and 10,000 levels. The response is produced by Lean and no Python response consumer was added.
6–8. No public verdict, budget, deadline, or kind fold changed. Evidence absence remains `UNKNOWN`; coverage and status projection are exhaustive for the template classes.
9–10. The English parser and public entry points are unchanged; fenced English explicitly rejects on the new route until E3/11b.
11–12. JSON and Lean are parsed by the existing readers; no new ledger or state machine was added.
13–16. M1–M3 above prove three behavioural tests fail. The gate runs hermetically; document identity and weight exclusion are tested; new test IDs are pinned in gate collection.
17–19. Statement inventory, axiom audit and theorem explanations are checked. This batch has no use-case formalisation rule. Human statement review is deferred above.
20–22. Counts here come from the named tests and evidence artifacts; unrun checks are stated. Everything is committed before the full gate on clean HEAD; disk and final status are recorded below.

## Final verification on committed HEAD

At `3877e6e2`, `python3 tools/gate.py --workers 8` passed in a clean worktree (11,481 passed, 7 allowed skips; Lean build and audit, Rust build and 49 Rust tests passed). The Lean statement check separately found 3,936 entries with no stale statement, predicate or declaration; the frozen source inventory passed. Final report-only commit and gate status are stated in the handoff.
