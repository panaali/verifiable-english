# Q1.3b report: the rest of Q1.3's evidence (a measurement)

- **Status:** delivered, all five rows; no DRI signature needed. Branch `feature/q1-3b`; the corpus run was at
  `5c56edcec`.
- **Result:** over 435,142 frontings of every *is*, *must* or *may*, Lean answers all but one (212,297 of them by
  refusing at its limits), reads none with another formula, and none is `many` (C4 `f2.frontings`, `f2.outcomes`,
  `f2.other_formula`, `f2.many_causes`). In the 15 norm part documents, 5 of 5,859 units are reached, all `ve` fences; no
  prose Lean answers for reads, and 1,006 units of `soft-chain` have no answer (C4 `norm.questions.configs`,
  `norm.reached`, `norm.by_why`). On the 1,442 F2 questions with no reading that open point 10.2 can measure, the
  closest candidate is a tie in 91% and has its moved word second in 97% (C4 `closest.measured`, `closest.share_tied`,
  `closest.share_moved_second`).
- **Open:** latency is recorded, not judged (q1-3c, HUMAN; C4 `latency.recorded_only`). The `soft-chain` part lists
  both `soft-norms@0` and `norm-defaults@0`, a pair `english.read` and `english.question` refuse though each alone
  reads (C6 `pair`, `soft_only`, `defaults_only`; follow-up below), so `whole_streams` is false (C4
  `coverage.whole_streams`, `coverage.unavailable_reads`).
  Hand-written size is about 1,670 lines, ~1,070 over the guide.

The numbers are in [question-answering-q1-report.md](../../spec/question-answering-q1-report.md), section "q1-3b",
and each cites its command (C4, C5). **Statement gate:** no theorem statement is added or changed, and Q1.2's reader is
on main (`english.question`). **Synthesis round 2 edits** (plan at `35f28a8a8`, section 11, and
`edits-question-answering.md`): this item implements none of them, since it touches no `VE.Ask`, `VE.Words` or
mapping-table file. The edited plan's Q1.3 rows are the same as main's.

## Plan rows (question-answering-PLAN.md Q1.3; q1-3's REPORT "Next")

| Row | Status | Where |
|---|---|---|
| (1) F2 for subjects with a clause: front each *is*, *must* or *may* in turn, Lean decides; the 4.9 measure | delivered: 435,142 frontings of 102,212 sentences; `other_formula` 0, `many` 0, 1 unanswered; share 0.256 (0.336 within the limits); the other frontings are refused, `moved` or at the limits | `frontings`, `run_config_b`, `fronting_measure`; C4 `f2`; `test_frontings_front_every_is_must_or_may_in_turn`, `test_every_fronting_of_the_group_document_is_read_by_lean`, and both zeros can show: `test_a_fronting_read_with_another_formula_is_counted_and_listed`, `test_a_many_fronting_reaches_its_sentence_and_is_listed` |
| (2) the seal's `english-mixed` and `natural-view` streams, its random Earley and document streams (F1 and F2, counts per stream) | delivered: 6,757 mixed texts (18 digests), 1,220 natural statements, 17 × 250 random Earley and 17 × 50 documents, each digest equal to its record (`natural-view` has a count only); `whole_streams` false only by `soft-chain`'s `unavailable_reads` (row 3) | `mixed_texts`, `natural_texts`, `earley_stream`, `per_stream`, `coverage_b`; C4 `coverage`, `streams`; `test_the_mixed_stream_is_its_generators_draw`, `test_the_natural_stream_is_each_rendered_statement`, `test_the_random_earley_stream_skips_the_sealed_texts`, `test_every_stream_is_counted_and_a_missing_one_leaves_the_run_partial`, `test_every_part_a_run_can_leave_out_stops_it_being_whole` |
| (3) questions over norm documents, part documents only (L70), the sentences no question form reaches and why | delivered: 15 part documents, 5,859 units, 5 reached, all fences; each unit's kind and `english.read` outcome counted, with examples | `norm_documents`, `document_units`, `norm_units`, `why`, `unit_reach`, `norm_measure`; C4 `norm`; `test_a_norm_documents_units_say_why_no_question_reaches_them`, `test_a_units_english_fence_is_the_sentence_lean_reads_not_its_prose` |
| (4) open point 10.2: leftmost ties, moved word second, ten examples | delivered: 5,243 questions with no reading (1,336 distinct texts); 1,442 measured (364 distinct); tied 1,310, moved second 1,402, not the reader's 1,239 of 1,426; 10 examples | `closeness`, `closest_measure`; C4 `closest`; `test_closeness_names_leans_closest_its_ties_and_the_readers_sentence`, `test_the_closest_shares_count_only_named_f2_questions_with_no_reading`, `test_a_question_with_no_reading_has_leans_closest_among_its_candidates` |
| (5) the report extended, every number citing its command; tests on a small fixed slice | delivered | question-answering-q1-report.md "q1-3b"; 26 new test functions in `tests/test_question_reverse.py` |

**On the gap row `dr-qa-q1-3-public`:** the reverse method reaches a norm part document only through a unit's own
English `ve` fence (C4 `norm.reached`). All 5 fences Lean answers for read with one formula, each F1 question reads with
it, and so does each F2 question of the one-line sentence (C4 `streams.norm-documents.f1_same`,
`streams.norm-documents.f2_same`). But only 8 of the 5,859 units have a fence, none is of kind `norm`, and the 3 in
`soft-chain` have no answer (C4 `norm.documents.*.reach`, `norm.by_why`). Every other unit's text is source prose, and
none that Lean answers for reads (C4 `norm.by_why`). Without `soft-norms@0`, `soft-chain` reads its 3 fences and none of
its other 1,002 sentences, in a changed environment that is not C4's (C6 `soft_chain_without_soft`). The meaning of the
73 norms and 31 AST assertions with a `content` is in it, for which the document holds no VE sentence, and the other 70
norms have none (C4 `norm.documents.*.reach`). So the fences are Q1 evidence for their own 2 distinct sentences (C4
`norm.documents.*.examples`), and the row cannot be closed for norms by Q1 evidence. A re-scope fits this: questions over
norm documents are answered over the content (Q2, `ve ask`), with Q1 evidence from the fences and from the norm's
rendered English, not its text. This run does not measure rendered English. The decision is the plan's.

## How each row keeps Lean's decisions in Lean

- **Frontings:** Python builds every fronting of every auxiliary and never picks the main sentence's word. Each
  outcome (`one`, `moved`, `budget`) is Lean's.
- **10.2:** Lean names the closest sentence in its answer's text. Python reads each candidate with `english.read` and
  counts the ties of their diagnosis starts. It checks Lean's choice against the leftmost tie: 0 of 5,183 disagree (3,741 have one candidate, 1,442 a choice).
  The word-gap candidates are q1-3's `candidates`. When Lean's token gaps differ (Markdown `**`), the question is
  listed, not measured.
- **Units of norm documents:** `document_units` reads a document with the loader's own `_split`, `_parts` and `_english_fences`, and
  `documents()` uses it too, so one reader gives every document's units (its output over the 9 use-case documents is
  unchanged). Whether a fence's sentence reads is Lean's answer.
- **New streams:** `english-mixed` and `natural-view` are drawn by their own generators (their checks left out),
  not by copies of them. The random Earley stream is drawn as `english_surface.audit` draws it, and its 17 digests and
  17 document digests equal the seal's.

## Evidence

- **Seeded bugs** (Python: 36 in `conformance/question_reverse.py`, 13 in [claims.py](claims.py);
  [mutants.json](mutants.json), each planted alone by [seed.py](seed.py), which reuses q1-3's loop): 49, every one
  killed. The three the task names are:
  - F2 fronting only the first auxiliary, caught by `test_frontings_front_every_is_must_or_may_in_turn`;
  - a stream dropped from the counts, caught by `test_every_stream_is_counted_and_a_missing_one_leaves_the_run_partial`;
  - the 10.2 count over the wrong denominator, caught by `test_the_closest_shares_count_only_named_f2_questions_with_no_reading`.

  The others are ties in code points, Lean's choice not checked against the leftmost tie, a natural statement left
  out of coverage, a sealed text kept in the random Earley stream, a two-formula norm sentence counted as reached, the
  limited share with `any`, a statement without its period, a mixed paragraph counted as a sentence, and a put-back
  that keeps an opener's capital. The 24 added after review give every headline zero a mutant (`other`, `many`,
  `several_same`, `inconsistent`, each `whole_streams` key), and cover the `read` filters and the fence, `MIXED`, span
  and unavailable counts. The last 13 make the claims check able to fail. No Lean or Rust code changed.
- **Claims:** [claims.py](claims.py) checks both reports against C4, C5, C6 and q1-3's C1 (79 units): each summary,
  headline and conclusion sentence cites its key or is listed as no claim with its reason, each bullet and row of the
  q1-3b section cites one, each key exists, each number is its key's value, each headline claim without a number holds
  of the evidence (`TRUTHS`), and no wording of a refuted premise stays.
  Its logic is tested on fixtures (`test_a_claim_must_cite_a_key_that_holds_its_numbers`,
  `test_the_old_premises_sentence_fails_the_claims_check`, `test_a_headline_claim_must_hold_of_the_evidence`); the run over the saved evidence stays a batch probe (D4).
- **Samples:** [samples.py](samples.py) saves C5 and C6 to `evidence/samples.json`. C6 reads under changed profile
  lists, so its outcomes name the cause of `soft-chain`'s refusal and are never C4's answers.
- **Trust:** `tools/trust_map.py --check` gives K +0, S +0 and trusted +0 (PASS). There is no allowance and no
  FOLLOW-UPS row.
- **Tests:** The selected tests (137 units, 3 shards, run `q1-3b-9c600a54-t631791`) gave 0 failed at `9c600a54e`; the
  commit after it changes only this report and DELTA. `lake build` and `lean/audit.py` pass. `gate_collection.py --check
  --prebuilt` reports 49 added, 0 refused, 0 stale and 0 malformed. The full gate is left to the chain. `test_the_q1_3b_evidence_stays_in_the_tree` is removed:
  it was a permanent test over batch evidence, which DRI decision D4 rules out, so the saved numbers are checked by
  this batch's review probes, and the regression tests run on fixtures.
- **Corpus run:** C4, 13,694 s with 12 workers, at `5c56edcec`. It replaces the run at `5728eb968`. The code under
  `conformance/` is unchanged since `5c56edcec`; later commits add only evidence, reports and the batch's own scripts.
  Between the two runs, apart from the norm documents, each configuration's non-timing fields are equal; the new run
  adds an `unavailable` count, 0 in each of these.
- **One unanswered fronting:** C4 has 1 `unavailable` in `usecase-surface`, and `coverage.whole_streams` reads sentence
  reads only, so it would not have noticed this one alone. The count is in `streams.usecase-surface.f2_unavailable`.
- **Size and pilot bytes:** About 1,670 hand-written lines (`git diff --numstat` over the merge base, without the
  evidence JSON and `mutants.json`). That is ~1,070 over the ~600 guide: the stream reproductions, the norm-document
  reader, the tests, and this round's `claims.py` (271) and `samples.py` (85) are what grew. Pilot bytes expected to move: 0, since this is a measurement.
- **Not run:** a whole UDHR or constitution document (L70). The English rendering of the 104 norm and AST contents.
  The `soft-chain` part's 1,005 sentences have no answer (`UnsupportedProfile`, for the profile pair above), and they
  are counted as unavailable, not as `none`.

## Spec re-read

- The 4.9 measure, re-read at PLAN.md:954: "the word is moved to every other gap and the acceptances are counted.
  Each acceptance is listed." Here a fronting that reads another formula is an acceptance (0); `moved` is Lean's
  refusal of 4.1 row 11a.
- 10.2, re-read at spec:1481: "Ties go to the leftmost … the candidate with the moved word second". Lean's `closest`
  (spec 2.5) compares `d.span.1` in the candidate's own bytes with a strict `>`, so the leftmost of the maxima wins.
  `closeness` converts `english.read`'s code-point span to bytes for that reason (a seeded bug checks it).
- Candidates: gaps before each token after the first, excluding punctuation (spec 2.2, `gaps`). The word gaps of
  `candidates` equal them except next to tokens without a space, which is the 60 unmatched questions.
- F2 shape (spec 3.1): `Is`, `Must` or `May` with a capital, then the body. `frontings` capitalises the fronted word
  and lowers an opener's initial, as q1-3's `f2` does. `test_frontings_hold_q1_3s_question_and_its_put_back` checks
  that every q1-3 F2 question is one of its frontings.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed route is added. Every answer is checked by the relay's `question_problem` or `response_problem` (`ask`, `read_sentences`); a failed service is `unavailable` (`test_a_failed_service_is_unavailable_not_a_crash`).
2. PASS: the five rows above. No in-flight branch shares a file. There is no Python copy of a Lean decision (each fronting is Lean's to decide; the closest is Lean's, checked against the leftmost tie).
3. PASS: [mutants.json](mutants.json), 49 of 49 killed, the three the task names among them.
4. N.A.: no reader changes; Lean's closest agrees with the leftmost tie of its own reads in 5,183 of 5,183 (1,442 with a choice).
5. N.A.: no new relayed field.
6. PASS: the evidence commit and the HEAD difference are stated above; the chain runs the gate on the final HEAD.
7. PASS: [DELTA.md](DELTA.md) has no rows, and no signature is needed or reserved.
8. PASS: no file under `ve/`, `lean/` or `rust/` changes.
9. PASS: `select_tests.py` selects `tests/test_question_reverse.py` for `conformance/question_reverse.py`.
10. N.A.: no Lean statement.
11. PASS: Lean's limits decide every `budget`; the share is given with and without them (`test_every_fronting_of_the_group_document_is_read_by_lean`); there is no timing assert.
12. N.A.: no product code; latency is recorded for q1-3c.
13. PASS: no test on main is removed or renamed; the one test removed was added on this branch and D4 rules it out (above).
14. PASS: both directions are checked. Examples: a tie in bytes against code points, Lean's leftmost choice against a non-leftmost one, coverage whole against each part left out, a limited sentence against one with a fronting within the limits, reached against two formulas, a fronting with the sentence's formula against another formula and against `many`. The spec re-read is above.

## Next

- Q2.1, after RD-3's merge and the Q2 statements' review.
- q1-3c: the review of the latency gates (HUMAN); C4's latency is recorded for it.
- A tie rule for the closest candidate (10.2), if the plan takes it: the count above is its evidence, and it needs its
  own statement.
- More seeded bugs (recheck F12, optional): the `limited` status, `slice_b`'s `every`, `run_b`'s `reads`, the read guard
  of `other` and `one` in `conformance/question_reverse.py`. A change there would no longer be C4's code, so they wait.
- `english.read` and `english.question` for an environment listing both `soft-norms@0` and `norm-defaults@0` (the
  constitution `soft-chain` part; C6 `pair`). Either profile alone already reads (C6 `soft_only`, `defaults_only`).
