# Q1.3b report: the rest of Q1.3's evidence (a measurement)

- **Status:** delivered, all five rows; no DRI signature needed. Branch `feature/q1-3b`; the corpus run was at
  `5728eb968`.
- **Result:** over 435,136 frontings of every *is*, *must* or *may*, Lean reads none with another formula and none is
  `many`. No unit text of the 15 norm part documents is a question's source. On the 1,446 F2 questions with no
  reading that open point 10.2 can measure, the closest candidate is a tie in 91% and has its moved word second in 97%.
- **Open:** latency is recorded, not judged (q1-3c, HUMAN). The `soft-chain` part's profile `soft-norms@0` is refused
  by `english.read` and `english.question` (follow-up below). Hand-written size is ~800 lines, ~200 over the guide.

The numbers are in [question-answering-q1-report.md](../../spec/question-answering-q1-report.md), section "q1-3b",
and each cites its command (C4, C5). **Statement gate:** no theorem statement is added or changed, and Q1.2's reader is
on main (`english.question`). **Synthesis round 2 edits** (plan at `35f28a8a8`, section 11, and
`edits-question-answering.md`): this item implements none of them, since it touches no `VE.Ask`, `VE.Words` or
mapping-table file. The edited plan's Q1.3 rows are the same as main's.

## Plan rows (question-answering-PLAN.md Q1.3; q1-3's REPORT "Next")

| Row | Status | Where |
|---|---|---|
| (1) F2 for subjects with a clause: front each *is*, *must* or *may* in turn, Lean decides; the 4.9 measure | delivered: 435,136 frontings of 102,207 sentences; `other_formula` 0, `many` 0; share 0.256 (0.336 within the limits), each other sentence `moved` | `frontings`, `run_config_b`, `fronting_measure`; C4 `f2`; `test_frontings_front_every_is_must_or_may_in_turn`, `test_every_fronting_of_the_group_document_is_read_by_lean` |
| (2) the seal's `english-mixed` and `natural-view` streams, its random Earley and document streams (F1 and F2, counts per stream) | delivered: 6,757 mixed texts (18 digests), 1,220 natural statements, 17 × 250 random Earley and 17 × 50 documents, each digest equal to the seal's; `whole_streams` true | `mixed_texts`, `natural_texts`, `earley_stream`, `per_stream`, `coverage_b`; C4 `coverage`, `streams`; `test_the_mixed_stream_is_its_generators_draw`, `test_the_natural_stream_is_each_rendered_statement`, `test_the_random_earley_stream_skips_the_sealed_texts`, `test_every_stream_is_counted_and_a_missing_one_leaves_the_run_partial` |
| (3) questions over norm documents, part documents only (L70), the sentences no question form reaches and why | delivered: 15 part documents, 5,858 units, 0 reached; each unit's kind and `english.read` outcome counted, with examples | `norm_documents`, `norm_units`, `why`, `unit_reach`; C4 `norm`; `test_a_norm_documents_units_say_why_no_question_reaches_them` |
| (4) open point 10.2: leftmost ties, moved word second, ten examples | delivered: 5,252 questions with no reading; 1,446 measured; tied 1,314, moved second 1,406, not the reader's 1,239 of 1,430; 10 examples | `closeness`, `closest_measure`; C4 `closest`; `test_closeness_names_leans_closest_its_ties_and_the_readers_sentence`, `test_the_closest_shares_count_only_named_f2_questions_with_no_reading`, `test_a_question_with_no_reading_has_leans_closest_among_its_candidates` |
| (5) the report extended, every number citing its command; tests on a small fixed slice | delivered | question-answering-q1-report.md "q1-3b"; 12 new test functions in `tests/test_question_reverse.py` |

**On the gap row `dr-qa-q1-3-public`:** the norm part documents give no sentence that `english.read` reads. A norm's
or an assertion's meaning is in its unit's `content`, and its text is the source English. So the reverse method has
no source sentence there, and the row cannot be closed by Q1 evidence. A re-scope fits the evidence: questions over
norm documents are answered over the content (Q2, `ve ask`), with Q1 evidence from the norm's rendered English, not
its text. The decision is the plan's.

## How each row keeps Lean's decisions in Lean

- **Frontings:** Python builds every fronting of every auxiliary and never picks the main sentence's word. Each
  outcome (`one`, `moved`, `budget`) is Lean's.
- **10.2:** Lean names the closest sentence in its answer's text. Python reads each candidate with `english.read` and
  counts the ties of their diagnosis starts. It checks Lean's choice against the leftmost tie: 0 of 5,192 disagree.
  The word-gap candidates are q1-3's `candidates`. When Lean's token gaps differ (Markdown `**`), the question is
  listed, not measured.
- **New streams:** `english-mixed` and `natural-view` are drawn by their own generators (their checks left out),
  not by copies of them. The random Earley stream is drawn as `english_surface.audit` draws it, and its 17 digests and
  17 document digests equal the seal's.

## Evidence

- **Seeded bugs** (Python, all in `conformance/question_reverse.py`; [mutants.json](mutants.json), each planted alone
  by [seed.py](seed.py), which reuses q1-3's loop): 12, every one killed. The three the task names are:
  - F2 fronting only the first auxiliary, caught by `test_frontings_front_every_is_must_or_may_in_turn`;
  - a stream dropped from the counts, caught by `test_every_stream_is_counted_and_a_missing_one_leaves_the_run_partial`;
  - the 10.2 count over the wrong denominator, caught by `test_the_closest_shares_count_only_named_f2_questions_with_no_reading`.

  The others are ties in code points, Lean's choice not checked against the leftmost tie, a natural statement left
  out of coverage, a sealed text kept in the random Earley stream, a two-formula norm sentence counted as reached, the
  limited share with `any`, a statement without its period, a mixed paragraph counted as a sentence, and a put-back
  that keeps an opener's capital. No Lean or Rust code changed.
- **Trust:** `tools/trust_map.py --check` gives K +0, S +0 and trusted +0 (PASS). There is no allowance and no
  FOLLOW-UPS row.
- **Tests:** the first selected run (fast stage, 13 units) failed one test,
  `test_the_q1_3b_evidence_stays_in_the_tree`, which compared the saved streams in order although the evidence is
  written with sorted keys. With that fixed, the id passes, and the selected tests (137 units) gave 0 failed on the
  Mac runner at `abf32707`. `gate_collection.py --check --prebuilt` reports 15 added, 0 refused, 0 stale and 0
  malformed. The full gate is left to the chain.
- **Corpus run:** one run, C4, of 12,248 s with 12 workers. The code under `conformance/` is unchanged since
  `5728eb968`; later commits add only tests, evidence and reports.
- **Size and pilot bytes:** about 800 hand-written lines (`git diff --numstat` over the merge base, without the
  evidence JSON and `mutants.json`). That is ~200 over the ~600 guide: the stream reproductions and the norm-document
  reader are what grew. Pilot bytes expected to move: 0, since this is a measurement.
- **Not run:** a whole UDHR or constitution document (L70). The `soft-chain` part's 1,003 sentences have no answer
  (`UnsupportedProfile`), and they are counted as unavailable, not as `none`.

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
3. PASS: [mutants.json](mutants.json), 12 of 12 killed, the three the task names among them.
4. N.A.: no reader changes; Lean's closest agrees with the leftmost tie of its own reads in 5,192 of 5,192.
5. N.A.: no new relayed field.
6. PASS: the evidence commit and the HEAD difference are stated above; the chain runs the gate on the final HEAD.
7. PASS: [DELTA.md](DELTA.md) has no rows, and no signature is needed or reserved.
8. PASS: no file under `ve/`, `lean/` or `rust/` changes.
9. PASS: `select_tests.py` selects `tests/test_question_reverse.py` for `conformance/question_reverse.py`.
10. N.A.: no Lean statement.
11. PASS: Lean's limits decide every `budget`; the share is given with and without them (`test_every_fronting_of_the_group_document_is_read_by_lean`); there is no timing assert.
12. N.A.: no product code; latency is recorded for q1-3c.
13. PASS: no test is removed or renamed.
14. PASS: both directions are checked. Examples: a tie in bytes against code points, Lean's leftmost choice against a non-leftmost one, coverage whole against a stream left out, a limited sentence against one with a fronting within the limits, reached against two formulas. The spec re-read is above.

## Next

- Q2.1, after RD-3's merge and the Q2 statements' review.
- q1-3c: the review of the latency gates (HUMAN). C4's latency is recorded for it.
- A tie rule for the closest candidate (10.2), if the plan takes it: the count above is its evidence, and it needs its
  own statement.
- `english.read` and `english.question` for profile `soft-norms@0` (the constitution `soft-chain` part).
