# Lean-first batch 11a: fix report and gate record

Base: `2ce1134e` (before this batch). Branch: `lean-first/b11a`. This is the Lean-side half of row 11: `speech-source` reads the W2 source wrapper, projects coverage, checks answer and compliance evidence, and emits nominations. No Python caller changes and no Python semantics are deleted. Batch 11b owns that switch and deletion.

## Acceptance and ownership

| Item | Owner | Evidence or state |
|---|---|---|
| 8.5 source wrapper, document/source/environment IDs | AGENT | `Source/Run.lean`; `test_templates_agree_with_python`, `test_document_id_excludes_removable_weights_only` |
| W2 statuses, bytes and residual coverage | AGENT | `coverage_partition`; `test_template_reports_cover_every_class_and_record` |
| Answer, query and compliance replay | AGENT | `answers_sound`, `query_records_sound`; `test_answer_records_replay_their_evidence`, `test_premise_status_evidence_comes_from_the_case` |
| Nomination records and narrowing | AGENT | `test_nominations_name_a_candidate_of_the_bound_set` |
| Statement review of four new theorems | HUMAN (speech-acts DRI/reviewers) | Deferred: statements and their dependencies are in `lean/statements.txt`, `lean/SPEECH-ACTS.md`; no approved statement was changed. |
| English fences and claim-graph admission | EXTERNAL (English E3 and batch 11b owners) | Explicitly open; the route rejects fenced English and does not assert `SpeechAdmitted`. |

The shared W2 `Discourse/Loader.lean` now types open-term conditions and narrowing references once for both routes. `test_ill_typed_open_term_condition_is_leans_rejection` and the source tests cover the affected order. `lean/SPEECH-ACTS.md` lists the definitions, theorem meanings and open boundaries.

## Behaviour and gate 5.1

- **Suite:** the batch tests passed (67 tests in `test_speech_source_lean.py` and `test_discourse.py`). The gate collection was refreshed with 37 new test IDs and no removals. Full gate result is recorded below.
- **Corpus A/B:** Python-visible files and the public Python dispatch are unchanged. The recorded pilot comparison has 278 identical results; the discourse comparison has 6,350 identical results, with no unlisted difference (evidence JSON). The speech-source template and single-fault differential tests compare the new route to the frozen Python wrapper, and pin every known diagnostic wording class. Other A/B corpora and the 14 difffuzz date seeds are recorded below if run; no claim of coverage is made for an unrun corpus.
- **Deletion ledger:** no deletion is planned for 11a; the Python wrapper remains the current caller. The new Lean route is selected only by the new `speech-source` kind. Batch 11b will map Python decision sites before deleting them.
- **Latency:** `evidence/speech-source-cpu.txt` measures 50 calls per template: 5.45–15.67 ms CPU per case including startup share. No existing operation has a new call, so its budget does not change.
- **Lean assurance:** `tools/lean_statements.py --check` reports 3,936 statements with zero changed relative to the pinned inventory; `lean/audit.py` audits 3,936 named theorems with standard axioms only; the frozen source check passes. New statements and declarations are inventoried and pinned in this batch's commits.

There is no `DELTA` of Python-visible verdict, wording, order or availability to sign. Python rejects nomination records because it does not implement them; the new Lean-only case implements the specified narrowing result and is not called by Python yet.

## Seeded bugs: tests can fail

Each mutation was applied to `Source/Run.lean` alone, rebuilt with `lake build ve_speech_acts_route`, tested, removed, and rebuilt clean. The raw failures are in `evidence/mutants.txt`.

| Seed | Changed behaviour | Failing test |
|---|---|---|
| M1 | Report `source_id` in the `document_id` field | `test_templates_agree_with_python`: document IDs differ |
| M2 | Populate `bytes_by_class` with status counts | `test_template_reports_cover_every_class_and_record`: class keys differ |
| M3 | Count duplicate nominations as separate choices | `test_nominations_name_a_candidate_of_the_bound_set`: duplicate testimony becomes `CLARIFICATION-OPEN (multiple)` |

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

Pending the full gate run.
