# Q1.3 report: Q1 evidence, the reverse question corpus

- **Status:** delivered for the corpus below; no DRI signature needed. Branch `feature/q1-3`; the evidence was run at
  `7652add57`.
- **Result:** over the whole corpus (98,452 sentences), F1 reads with its sentence's formula for 97,532 of 98,187
  questions; the 655 misses are the question limits (`QuestionTooLong`), not Lean's reader. F2 reads for 1,029 of
  1,029, with no `many`. Lean accepts no moved-word sentence (0 of 3,191).
- **Open:** both latency gates of 3.6 are missed (p95 146.8 ms, 64-candidate maximum 3.4 s); their revision goes to
  review (plan R12) as q1-3c. F2 for subjects with a clause, the seal's `english-mixed` and `natural-view` streams and
  norm documents go to q1-3b.

The numbers are in [question-answering-q1-report.md](../../spec/question-answering-q1-report.md), each citing its
command. **Statement gate:** no theorem statement is added or changed, and Q1.2's reader is on main
(`english_lean.read_question`, mode `english.question`). **Synthesis round 2 edits:** this item implements none of
them. Edit 5 puts q1-3 first in the `lean/VE/Ask/*` queue, but this item touches no Ask file.

## Plan rows (question-answering-PLAN.md Q1.3)

| Row | Status | Where |
|---|---|---|
| F1 question for every one-reading corpus sentence (sealed streams, use-case documents) | delivered for the 17 round-trip streams (each the seal's digest), the 26 use-case streams and the 9 documents: 98,187 sentences, nothing left out (evidence `coverage`). The seal's `english-mixed` and `natural-view` streams are a cut, named in q1-3b | `f1`, `run_config`, `coverage`; `test_f1_frames_the_sentence`, `test_coverage_is_whole_only_when_nothing_is_left_out` |
| F2 question where a quantified or named subject is followed by is, must or may | delivered for subjects without a clause; a clause subject goes to q1-3b | `f2`; `test_f2_fronts_the_word_after_the_subject`, `test_f2_is_not_built_for_other_subjects` |
| Spacing and capitalisation mutants | delivered (6 kinds) | `mutants`; `test_every_mutant_differs_and_has_its_kind` |
| Outcome through Lean's reader, one question per call (no Python reading decision, no whole-document run) | delivered | `ask` (`relay.rows` and `question_problem`); `test_the_group_documents_questions_read_through_lean` |
| F1 share, with each miss listed | delivered: 0.993329, 655 misses explained by the limits | evidence `f1` |
| F2 share counting `many`, with each `many`'s cause | delivered: 1.0; `many` 0 | evidence `f2` |
| Odd-English measure, with each acceptance listed | delivered: 0 of 3,191, for subjects without a clause | evidence `odd`; `test_candidates_are_the_word_gaps_left_to_right` |
| Latency p95 and maximum against 3.6 | delivered: both missed, so q1-3c | evidence `latency`, `limits`; `test_the_latency_budget_is_met_at_its_bound_only`, `test_the_candidate_limit_is_leans_on_both_sides` |
| Every F1 miss fixed or explained | explained: 3.6's token limit; no fix item for Lean's reader | evidence `f1.misses` |

## Evidence

- **Seeded bugs** (Python, `conformance/question_reverse.py` and `conformance/english_lean_e2_evidence.py`;
  [mutants.json](mutants.json), each planted alone by [seed.py](seed.py)): 30, every one killed. Among them: F2 fronting
  the wrong word (`test_f2_fronts_the_word_after_the_subject`); a mutant generator that returns the question unchanged
  (`test_every_mutant_differs_and_has_its_kind`); the F1 share over every question
  (`test_each_share_has_its_forms_denominator`); the formula left uncompared
  (`test_a_reading_counts_only_with_the_sentences_formula`); a long question one word short
  (`test_the_candidate_limit_is_leans_on_both_sides`); the default run a sample again
  (`test_the_default_run_is_the_corpus_size`); coverage that ignores the size, a short stream, an unavailable read or
  a stream that is not the seal's (`test_coverage_is_whole_only_when_nothing_is_left_out`). No Lean or Rust code changed.
- **Trust:** `tools/trust_map.py --check` gives K +0, S +0 and trusted +0 (PASS). No allowance and no FOLLOW-UPS row.
- **Tests:** the selected tests ran once on this fix (239 of 502 units). One failed:
  `test_nested_pytest.py::test_every_pytest_command_is_built_by_the_builder`, because `seed.py` built its own pytest
  command. `seed.py` now uses `tools/nested_pytest`. That test, `test_hang_guards.py` and `test_question_reverse.py`
  then give 150 passed. `gate_collection.py --check --prebuilt` reports 45 added, 0 refused, 0 stale and 0 malformed.
  `lake build` and `lean/audit.py` pass. The full gate is left to the chain.
- **Size and pilot bytes:** about 950 hand-written lines (`git diff --numstat` over the merge base, without the evidence
  JSON and `mutants.json`). That is 350 over the ~600 guide; the workers, the coverage record and their tests are what
  grew. Pilot bytes expected to move: 0, since this is a measurement.
- **Not run:** the corpus run is not repeated at HEAD. HEAD differs from `7652add57` only by `seed.py`, the evidence
  and the reports; `conformance/` is the same. The run took 2,129 s with 12 workers (evidence `seconds`, `workers`).

## Spec re-read

- F2's candidates are the gaps before each token after the first, excluding punctuation: re-read against
  question-answering-PLAN.md:171 (`candidates`).
- F1's frame is exactly the bytes `Is it the case that `: re-read against PLAN.md:166 (`FRAME`).
- Budgets of 100 ms and 1 s, on whole questions: re-read against PLAN.md:377 and R12 at :101.
- `maxCandidates` is 64 (`lean/VE/Question/Basic.lean:16`): 64 candidates are read and 65 are refused.
- "Every one-reading corpus sentence" against PLAN.md:944: 98,187 sentences, by `coverage`. The first run was a sample
  marked delivered, so its result is kept as `question-reverse-sample.json` for its one-at-a-time latency only.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed route is added. `ask` checks every answer with the relay's `question_problem` (`test_a_reading_counts_only_with_the_sentences_formula`).
2. PASS: the plan rows above; q1-3b and q1-3c are named; no in-flight branch shares a file; no Python copy of a Lean decision (F2 skips clause subjects for that reason); the corpus cut is named in q1-3b.
3. PASS: [mutants.json](mutants.json), 30 of 30 killed; empty input fails both gates (`test_no_question_meets_no_budget`).
4. N.A.: no reader changes; the corpus run is the measurement itself.
5. N.A.: no new relayed field.
6. PASS: the evidence commit and HEAD difference are stated above; the chain runs the gate on the final HEAD.
7. PASS: [DELTA.md](DELTA.md) has no rows and no signature is needed.
8. PASS: no file under `ve/`, `lean/` or `rust/` changes (DELTA.md).
9. PASS: `select_tests.py` selects `tests/test_question_reverse.py` (239 of 502 units).
10. N.A.: no Lean statement.
11. PASS: Lean's candidate limit on both sides (`test_the_candidate_limit_is_leans_on_both_sides`); no timing assert (`test_hang_guards`).
12. N.A.: no product code; the latency is measured and reported.
13. PASS: no test removed; `gate_collection.py --check --prebuilt` reports 0 refused, 0 stale and 0 malformed.
14. PASS: both sides for each check (the F2 accept and refuse lists, mutants with and without capital-body, the 100 and 100.001 ms bounds, 64 and 65 candidates); spec re-read above.

## Next

- Q2.1, after RD-3's merge and the Q2 statements' review.
- No fix item for Lean's reader: there is no F1 miss in it.
- q1-3b: F2 for subjects with a clause (front every *is*, *must* or *may* and let Lean decide, with the 4.9 measure on
  them), the sentences of the seal's `english-mixed` and `natural-view` streams and of its random Earley and document
  streams, questions over norm documents, and the closest-candidate count of spec open point 2.
- q1-3c: review the revision of the two latency gates (plan R12); this is a HUMAN item.
