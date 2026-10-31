# q2-6 REPORT: Q2.6 evidence and measurement, the part with no model call

- **Status:** built; no DRI signature reserved. The DRI set the three new bars (reviews/dri-decisions-20261031-q2-6.md).
- **HEAD:** feature/q2-6 on main e68b0dd88. No file of `ve/`, `lean/` or `rust/` changes; no model call anywhere.
- **What changed:** the report's expected-against-got table and wording counts; the reading and writing evaluation
  sealed (19 items, 16 tasks, MANIFEST.sha256) with its bars registered; the tests of both.
- **Open:** the run (model calls), its scorer and the readability section of the report are q2-6b.

## Plan rows (docs/spec/question-answering-PLAN.md Q2.6, lines 1032-1044) and task deliverables

| Row | Delivered | Where | Test |
|---|---|---|---|
| Fixtures, expected against got | done: 18 rows; 6 differ, each D6 | `tools/question_answering_report.py` `expected_rows`; `evidence/expected.json` (hand-written, spec line and quote per value) | `tests/test_question_answering_measure_report.py::test_q26_each_fixture_lead_against_the_spec_names_the_delta_row_that_explains_it` |
| Wording counts | done: 3 of 17 answers show `classified as "` (U3, U5, U7; 9 lines); S1 2 lines, 55 clauses, 27 read back with one reading; S2 8, 127, 49; S2p 11, 11, 6; S3 0 | `conformance/question_answering_readability.py capture`; `evidence/wording.json` | `...::test_q26_wording_counts_cover_every_saved_answer_line` |
| Reading evaluation, sealed | done: 17 items plus the "No." variants of G3 and A3 | `readability/items.json`, `contexts/R-*.txt` | `tests/test_question_answering_readability.py` (5 tests) |
| Writing evaluation, sealed | done: 16 tasks (G1 and G2 read the same formula: one task) | `readability/writing.json`, `contexts/W-*.txt`, `contexts/retry.txt` | `...::test_each_writing_gold_is_the_saved_reading` |
| README, protocol and bars | done: frozen bars copied; B1-B3 set by the DRI | `readability/README.md` | sealed in `MANIFEST.sha256` |
| Report Scope line | replaced as the task words it | `docs/spec/question-answering-report.md` | `...::test_q26_wording_counts_cover_every_saved_answer_line` |
| Agreement, latency | not redone: already on main (task) | — | — |
| Running the evaluation | not run: q2-6b (DRI, reviews/escalations-20261029.md line 67) | — | — |

Commands: `uv run python conformance/question_answering_readability.py capture` (27.7 s, `ve document render` of the 5
documents and 193 clause reads), `... build`, `... check` (exit 0), `uv run python tools/question_answering_report.py
--write`. The counts above are the generated report's (`docs/spec/question-answering-report.md`, "Wording counts").

**Deviations, recorded here.** One writing task per distinct reading: G1 and G2 have the same saved formula and the
same intended meaning, so two tasks would be byte-identical (`W-G1` lists both). The frames that cut a situation line
into its slot are Lean's `VE.Question.answerFrames`, printed by Lean at capture and saved in `wording.json`. The
capture script holds two of Lean's joiners as literals, each citing its Lean owner: `"; "` (`VE.Words.situationText`)
and `", reading sentence "` (`VE.Ask.readingSuffix`). Only the capture uses them; the test checks that the clauses
rejoin to the saved line. A clause is read with a full stop added. Element lines (`ann is a member`) and unnamed
elements (`e1`, `e0`) have no reading; the report gives the counts and claims nothing about them.

## Bars (readability/README.md)

Copied from the frozen protocol (ac91e1e4, PASS BARS): critical misreadings at most 2%, two-session agreement at least
90%, writing silent wrong meaning at most 5%, meaning correct within three attempts at least 80%. Asked through
`msg.sh dri` (inbox/dri/20261031T151945Z-q2-6-3818467.md) and set by the acting DRI in
reviews/dri-decisions-20261031-q2-6.md: B1 leads read correctly at least 85% of the 34 source-item responses; B2
first-try writing at least 50% of 32 sessions; B3 "No." against "Not necessarily.", using the DRI's two-step rule.

## Seeded bugs (Python only; no Lean or Rust product code changed)

Each was planted, its test failed, and it was restored (`docs/question-answering/q2-6/mutants.json` has the failing
assertion of each):

| Bug | File | Failing test |
|---|---|---|
| reading key from the first row's lead, not the answer's | `conformance/question_answering_readability.py` | `test_question_answering_readability.py::test_every_reading_key_is_the_saved_lean_lead` (R-U3: OPEN, not BY-READING) |
| a context that leaks its key | `conformance/question_answering_readability.py` | `...::test_a_context_is_what_a_human_gets_and_leaks_nothing` |
| a "No." variant that also changes the lines after the lead | `conformance/question_answering_readability.py` | `...::test_each_no_variant_differs_from_its_source_in_the_lead_line_only` |
| a sealed file edited after the manifest | `readability/contexts/R-G1.txt` | `...::test_the_builder_is_deterministic_and_the_manifest_verifies` |
| the expected table drops D6's row for A3 | `evidence/expected.json` | `test_question_answering_measure_report.py::test_q26_each_fixture_lead_against_the_spec_names_the_delta_row_that_explains_it` |
| a wording count that skips one fixture | `tools/question_answering_report.py` | `...::test_q26_wording_counts_cover_every_saved_answer_line` |

## Trust, size, bytes

- Trust: `uv run python tools/trust_map.py --check`: "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0;
  PASS". No Lean, so no R16 allowance, no trust mutants and no FOLLOW-UPS row.
- Size (`git diff --numstat $(git merge-base HEAD main)`, generated and captured files left out): builder 315,
  expected.json 25, README 107, tests 49 + 104, report tool 47, plus this REPORT and DELTA. That is about 720 lines,
  over the ~600 line. The six deliverables are one coherent part: the tests and README cannot be split from the
  sealed files they check, and q2-6b is already the next item. Generated or captured, not counted: the renders,
  wording.json, items.json, writing.json, contexts, MANIFEST, mutants.json, the report and the code map.
- Pilot bytes: 0 (plan line 1058: "Nothing in this plan states a coverage gain").

## Tests run

- Each new test while building: `uv run pytest -q tests/test_question_answering_readability.py` (5 passed);
  `... tests/test_question_answering_measure_report.py -k q26` (2 passed).
- Selected tests, once, on the finished code: `zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`:
  shard 1 "40 units, 40 passed", shard 2 "35 units, 35 passed", exit 0.
- `uv run python tools/regen_generated.py --write`, once: it wrote the code map, which was already stale on main
  (`lean/VE/Acts/ReadingsExamples.lean` and others).
- Not run: the full gate (the chain runs it), `lake build` and `lean/audit.py` (Lean unchanged; `lake build` was already
  up to date before capture), trust mutants (no trusted Lean).

## Spec re-read

- The expected column against docs/spec/question-answering.md 7.2 (1290-1299), 7.4 (1347-1355), 7.5 (1370-1375): each
  `quote` is in its row (test above).
- The D6 rows against docs/spec/question-answering-q2/DELTA.md D6: U7, A2, A3, A4, A7, A1d, exactly the differing set.
- The reading options, the "No." variants and the critical pair against the task and plan lines 1038-1039 and 1062.
- The bars against the frozen README's PASS BARS and the DRI decision.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No new relay. The capture uses `english_lean.read`, which checks each answer.
2. Deliverables: PASS. The table above, with the test of each row.
3. Tests can fail: PASS. Six seeded bugs, `mutants.json`; plus opposite-direction cases in
   `test_the_builder_is_deterministic_and_the_manifest_verifies` and `test_q26_each_fixture_lead_...`.
4. Py/Lean/Rust agree: N.A. No product code changed.
5. R8 binding: N.A. No relayed field is added.
6. Gate evidence: PASS for the selected run on the finished code. The full gate is the chain's.
7. Unsigned items: PASS. No DELTA row; the bars are signed in reviews/dri-decisions-20261031-q2-6.md.
8. Every user-visible change in DELTA: PASS. None (DELTA.md says why).
9. Test selection: PASS. The selection included both changed test files (`select.log`: "changed
   ['tests/test_question_answering_measure_report.py', 'tests/test_question_answering_readability.py']").
10. Lean statements: N.A. None added.
11. Budgets: N.A. No public operation added. Capture reads each distinct clause of a document once.
12. CPU and memory: N.A. No product path changed.
13. Test-removed trailers: N.A. No test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. See the opposite-direction cases above, the commands
    quoted in this report, and "Spec re-read".

## Next item

FOLLOW-UP: q2-6b the reading and writing proxy run under the sealed protocol and registered bars, its scorer, and the readability section of the report
