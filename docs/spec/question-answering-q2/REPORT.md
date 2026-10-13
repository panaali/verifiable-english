# Question answering Q2: build report

Branch `question-answering/q2`, first based on `main` at `f0547468` (Q1 merged), synced with `main` at `96887019`. The spec is
`docs/spec/question-answering.md` (5.2 for the statements, 7 for the fixtures, 8 for the wire); the plan is
`docs/spec/question-answering-PLAN.md` (Q2.1 to Q2.6). Builder's working notes: `../question-answering-q2-progress.md`.
User-visible deltas, each signed by a standing ruling or needing the DRI's signature: `DELTA.md`; Q2.4's moved
wording: `LEDGER.md`. Every number below the generated block's marker is
regenerated from `evidence/` by `report.py` and checked by `tests/test_question_answering_q2_report.py`.

## What `ve ask` does now

`ve ask DOCUMENT QUESTION` reads the question with Lean (Q1), builds the case of the document's route with the
existing untrusted generators, sends it to Lean's new `ask` mode, and prints Lean's lines:

- **Yes.** then `Sentence N says: "…"` for exactly the sentences the certificate's used premises come from, in the
  certificate's segment order (`checkedCites_spec`, `answerFor_cites`, the approved `render_cites_exact`);
- **No. The document rules this out.** with the certificate of the negation's sentences, likewise;
- **Not necessarily.** then `Here is a situation the document allows where it fails: …`, the countermodel's
  situation in the document's own words (`VE.Words.Situation`);
- **The text does not settle this.** with the situation and `The text does not say whether …` lines of a checked
  split (one base situation, two fillings of what the text leaves unsaid);
- **VE could not decide this.** with Lean's reason (X1 to X6);
- per reading where the readings differ (`If sentence N means "…", yes.`), with `(VE has not checked this wording)`
  where a reading's name could not be read back, and the unused-sentence line once at the end.

Python only runs the CLI, the generators and the display; it checks that Lean's answer is fully typed (the schema
generated from Lean's shapes) and bound to the request (every compatible choice has exactly one row, and every line,
reading, witness, source, definition, quote, gap element, unused unit, unchecked name and identity the answer names
exists in the request), and decides nothing (`tools/relay_lint.py`).

## What was built, by plan item

| Item | Status | Where |
|---|---|---|
| Q2.1 answer core | done | `lean/VE/Ask/{Basic,Sound,Sources,Groups,Plain,Examples}.lean` |
| Q2.2 `ask` wire | done, three routes | `lean/VE/Ask/{Binding,Wire,PlainWire,ZeroWire,Run}.lean`; `VE.Service.Protocol` mode `ask` (`runMode_ask`); `lean/ResponseShape/{Schemas,Encoders}/Ask.lean` |
| Q2.3 words and text | done | `lean/VE/Words/Situation.lean`, `lean/VE/Ask/{Lines,Render,PlainAnswer,ZeroAnswer}.lean`; the frames' `num` piece (DELTA D3) |
| Q2.4 one owner of situation wording | done: Lean words every situation line, point clause, filled-gap and pair sentence; the Python producers are deleted (`LEDGER.md`); the relay lint's wording rule; the A/B byte-identical | `lean/VE/Words/{Situation,Run}.lean` (mode `words`, `runMode_words`; DELTA D13), `ve/words.py`, `tools/relay_lint.py`, `tools/words_ab.py`, `evidence/words-ab.json` |
| Q2.5 `ve ask` | done, with one flip search (the point search its instance, the point-only copy deleted) | `ve/ask.py`, `ve/filling_search.py`, `tools/ask_fixtures.py`, `tests/fixtures/ask/` |
| Q2.6 evidence and measurement | **partly**: fixtures, the CPU and wall budgets (met), the agreement with the existing route on the fixtures and the corpora; the reading and writing evaluation is not run (model calls) | `../question-answering-report.md`; see "Not done" |

The three routes, chosen by Lean from the document's profiles (`routeOfDocument`): *readings* (`readings@1`, RD-3's
replay; the UDHR pilot, part 7), *plain* (`relational-fol@0`; the G document) and *zero-set norm-defaults*
(`norms@0` + `norm-defaults@0` without a reading set; the agent-policy documents; DELTA D5).

## The approved statements

All 27 approved theorems of spec 5.2 are proved, with no `sorry` and only the standard axioms (`lean/audit.py`). The
statement check (`tools/question_statements.py --q2`, extended in this batch, checklist 17) compares spec 5.2 with
`lean/VE/Ask` and `lean/VE/Words`: every approved theorem's text, every approved definition with a body (32), and
every approved structure and inductive (13) equal the implementation except `Asked.hnames` (DELTA D4). Then Lean is
the oracle: a generated file states each of the 41 approved statements and signatures as `example : <approved
statement> := @name` and Lean elaborates it. `tests/test_question_statements.py` runs the check and shows that a
renamed, re-bodied or reworded declaration fails it and that Lean refuses a changed conclusion.

The task's three proof obligations:

- **Answer soundness against the entailment verdict:** `lead_sound` and `reason_sound` (each lead's claim from the
  rows' `Holds`), `ask_wire_sound` (the replayed request's rows are `RowOk`), `plain_lead_sound` with
  `plain_ask_wire_sound`, and `leadU_sound`, `reasonU_sound`, `zero_ask_wire_sound` on the zero-set route.
- **Citation exactness, segment order included:** `sourcesU_zip_premisesU` (the sources zipped with `premisesU`
  segment by segment, not only `sourcesU_length`), `usedPositions_sufficient`, `mem_cited`, `cited_nodup`,
  `checkedCites_spec`, `answerFor_cites`, `plainCites_spec`, `zeroCites_spec`, and the approved
  `render_cites_exact`.
- **The A0 and answer lines under the all-derivations gate:** `answerFor_gated`, `gated_some` (every rendered line,
  A0 included, has exactly one derivation and it is its own frame's); `answerForPlain_gated`, `answerForZero_gated`.

## Tests added

- `tests/test_ask_fixtures.py`: the 18 recorded fixtures replayed through Lean's `ask` and the relay, compared with
  the recorded answer and with the spec's text (7.2, 7.4, 7.5); a replay can fail; a case of another document, an
  edited unit, a foreign environment and an undecodable environment are refused.
- `tests/test_ask_relay.py`: the relay's typing and binding (R8, checklist 4, 5, 7, 15): genuine answers of all three
  routes accepted; every node retyped and every field dropped refused; every id, choice, reading, witness, source,
  quote, gap element, unused unit, unchecked name and identity rebound refused, including an unknown definition and
  an omitted choice row (G1, G3, U3, U5, A1); Lean's own binding (names, evidence entries,
  asserted names); a broken split and a split differing in a base atom are not splits; a fence read as two formulas
  is not the case's unit; each request and case field replaced by 7, true, null, [], {} or a 10,000-deep list is
  refused, never answered; the mode's CPU deadline bounds the whole answer; Lean's refusal raised with its class and
  text, a forged refusal unavailable; the schema types every field.
- `tests/test_relay_mutation_gate.py::test_ask_is_read_as_ve_ask_reads_it`: the relay gate reads `ask`'s mutants
  through `ve.ask.read_answer` (request binding included), not by the transport alone.
- `tests/test_ask_cli.py`: `ve ask` end to end on G1, G3, G4 and U6, the leads, the refusal of G5, the JSON honesty
  fields, and eight odd spellings of a question reaching the answer only through Lean's reader (checklist 3, 10).
- `tests/test_question_statements.py`: the statement check above.
- `tests/test_question_answering_q2_report.py`: this report against its saved evidence (files under `evidence/`
  only, never live git, so it holds after syncs and the merge; architecture decision D4).
- `lean/VE/Ask/Examples.lean`: spec 7.6's figures (4,802 rows and their leads and reasons, the fold agreement, the
  groups) and the frames' `num` piece, as `#guard`s; `lean/VE/Ask/Run.lean`: X5's `#guard`s.

## Seeded bugs

19 seeded bugs, 8 in Lean and 11 in Python (five of them for the review fixes F2 and F3), one per behaviour claimed, each in a file this batch changed, each caught,
then removed (`mutants.py`, `evidence/mutants.json`; the table is in the generated block). No Rust code changed.

## Build checklist

| # | Line | State |
|---|---|---|
| 1 | One contract | The answer's shapes are Lean's (`ResponseShape/Schemas/Ask.lean`), rendered to `ask.json`; `ve/ask.py` reads its field sets, leads and reasons from that file, and a refusal's statuses, codes and classes from Lean's exported question contract (`ve/question/codes.json`). Every text is Lean's. |
| 2 | Differential fuzz | Not applicable: the answer has one owner (Lean); there is no Python or Rust answer to compare. The relay is fuzzed instead (4, 5). |
| 3 | Normalisation | The question reaches `ask` only through Q1's reader; `test_ask_reads_the_question_as_the_reader_does` covers NBSP, double space, tab, `\r`, curly quotes, U+212A, dotted I and a control character. |
| 4 | Untrusted output | Schema from the producer, binding to the request (including definition names and exact choice row coverage), bool-for-int refused, fuzz by dropping, emptying, duplicating, retyping and rebinding each field (`tests/test_ask_relay.py`). `tools/relay_mutation_gate.py` reads `ask`'s mutants as `ve ask` reads them (`ve.ask.read_answer`), with fixtures of the three routes; every accepted mutant is a listed by-design class (generated block). |
| 5 | Malformed input | `test_a_malformed_request_is_refused_never_answered` (three routes); Lean now refuses evidence of another type, foreign case fields and names on a one-choice route (DELTA D11). |
| 6 | Three-valued | No evidence answers unknown (X2 or X4), never yes or no (tested); past 64 choices is `ResourceLimit` (X5's text). `ask` has no budget option, so budget 0 has no entry point; the generators' budgets are internal. |
| 7 | Deadlines | The mode's CPU deadline wraps the whole request (`test_the_deadline_bounds_the_whole_answer`). A delay was not injected into each Lean callee. |
| 8 | Exhaustive folds | Lean's matches on `Lead`, `Reason`, `Source` are exhaustive by the compiler; Python reads the enumerations from the generated schema. |
| 9 | English one reading | Every line, A0 included, passes W7's all-derivations gate before it is shown (`answerFor_gated`, `answerForPlain_gated`, `answerForZero_gated`); a reading's name is read back to its formula where the candidate is asserted, else marked unchecked. |
| 10 | Entry points | `ve ask` (text, `--json`, `--reading`, `--evidence`) all go through one relay call (`ve.ask._ask`); metamorphic test as in 3. |
| 11 | No regex of a real language | The statement check uses Lean as the oracle; the text comparison is the existing whitespace-collapsed one. |
| 12 | State machines | Not applicable. |
| 13 | Tests can fail | 19 seeded bugs; `test_a_replay_can_fail`; the statement check's mutants. |
| 14 | Hermetic | CLI tests use the env allowlist and `HANG_TIMEOUT`; writes go to `tmp_path`. |
| 15 | Identity | Every identity field of the answer rebound and refused. |
| 16 | Lists | Fixture list, gate collection, frozen inventory, decoder pins, binding probe, trust classes, layer policy, import-linter layers: generated or tested. |
| 17 | Spec statements | `tools/question_statements.py --q2` and its test; DELTA rows for each difference. |
| 18 | Spec-stage | Not applicable (build stage). |
| 19 | Use-case formalisation | Not applicable: the fixtures use the existing G, UDHR and agent-policy documents. |
| 20 | Reports | This report's numbers from saved evidence, by test; what was not run is listed below. |
| 21 | Acceptance tags | Below. |
| 22 | Tests | Selected tests while iterating; the full gate once on the final HEAD (generated block). |
| 23 | DRI rulings | `DELTA.md`: D14 is signed by R3 and Q2.4's trust growth by R6 (D12, `docs/trust-baseline.json`'s `signed`), each with its test; D1 to D13 need the DRI's signature. |

## Acceptance items

| Item | Tag | State |
|---|---|---|
| Q2 statements proved; audit clean | AGENT | done |
| Fixtures G, U, A replayed from recorded evidence | AGENT | done; six leads differ from the spec's derived ones (DELTA D6) |
| Typed schema, binding, fuzz tests | AGENT | done |
| Seeded bugs | AGENT | done |
| Full gate on the final HEAD | EXTERNAL | the saved gate (generated block) is `7b75c7af`'s; the review fixes after it were checked by their selected tests, `lake build` and `lean/audit.py` only, because the fixer was told not to run the full gate; owner: the merge train's branch verify on the final HEAD |
| Q2.4 one owner of situation wording (Python producers deleted, corpus A/B byte-identical) | AGENT | done (`LEDGER.md`; `evidence/words-ab.json`: no difference) |
| Q2.3 `VE.Words` against Python's producers on the readings and norm-defaults corpora | AGENT | done: the A/B compares every moved site with the pre-Q2.4 producers (`tools/words_ab.py`), and `tests/test_words.py` keeps a generated differential |
| Q2.6 reading and writing evaluation (Sonnet as reader and writer) | EXTERNAL | **deferred**: needs model calls, which this task forbids; owner: the orchestrator |
| Q2.6 latency and agreement with W2 | AGENT | done: `ask` Lean CPU 0.5 s on U3 and A1 (budget 2 s; the benchmark `tools/bench/test_perf.py::test_ask_lean_cpu` against its stored baseline, since a correctness test never accepts on speed), U3 `ve ask` wall within 60 s; the agreement table in `../question-answering-report.md` |
| Q2.5 one flip generator (the point search as its instance, the copy deleted) | AGENT | done (`ve/filling_search.py`, `tests/test_filling_search.py`) |
| DRI signatures on DELTA D1 to D13 | HUMAN (DRI) | pending |

## Not done, and not run

- **Q2.6's reading and writing evaluation**: not run (model calls are forbidden here). The
  [non-model measurement report](../question-answering-report.md) records the fixtures, the budgets and the agreement
  with the existing route on the fixtures and the corpora, with what each corpus could not compare.
- **The final-HEAD full gate**: not run after the review fixes (the fixer's instruction); see the acceptance items.
- **The relay mutation gate on `words`**: run on its own route (`tools/relay_mutation_gate.py --route
  service:words`: 2 fixtures, 342 mutants, all refused, 0 allowed); `evidence/relay-gate.json` is the earlier run of
  every route and was not rerun.
- **Seen by the corpus agreement, not fixed here** (follow-ups for `ask`'s owner, each a refusal or a wording flaw,
  never a contradicted lead): a reading name that quotes a word (`the recorded relation "asks"`) makes the R1 line
  fail W7's gate, so `ask` refuses that question (`CheckerUnavailable`); U1 reads "VE did not use 1 sentences" for one
  unused sentence (the frame is fixed in the approved `render_unused_once`); a yes citing both a pair and a fill
  source, or a definition and the background, repeats the same C4 or C3 line. The exposition-unit refusal the same run
  found is fixed (`tests/test_ask_null_free.py`).
- **Q2.2's "A/B shows no change outside the new mode"**: no corpus comparison was run; the full gate is the evidence
  that existing behaviour is unchanged, and DELTA D9 names the one generator change that can change a readings
  answer.
- **Lean CPU**: `english.question` after the frames' `num` piece (DELTA D3) was not measured against a base binary;
  `ask` has no base. Recorded replay times are in the fixtures table (UDHR part 7: about 11 s per question; the
  agent documents about 3 s; the G document 0.1 to 0.2 s).
- **Flaky test seen once**: `tests/test_question_reading.py::test_the_whole_question_is_bounded_by_the_modes_deadline`
  (Q1's, unchanged) did not raise once in a combined run and passed on two reruns; it races a near-zero deadline.
- **Sync with `main`**: the branch merged `main` at `96887019` (`fc106062`), with RD-4b, eff-tests, eff-merge's
  `tools/relay_mutation_gate.py` and AR-6's identity lint, which now run on `ask`. `main` has moved 49 commits since; a
  trial merge (`git merge-tree`) conflicts only in generated inventories (assurance manifest, trust baseline, frozen
  hashes, declarations, gate collection), which the merge train regenerates (R12); the one hand-written file both
  sides change, `ve/readings_verdicts.py`, merges cleanly.
- **Selected tests**: `tools/select_tests.py --base 96887019 --run` selected all 360 test files because the lock and
  `Audit.lean` changed. It did not return a passing aggregate: `test_regen_generated.py` found two unregistered Q2
  writers and `tools/test_layer_policy.py` found `ve.ask` absent from the documented layer; both were fixed and their
  combined rerun passed. `test_lean_conformance.py::test_lean_transitive_axiom_allowlist` hit its 30-minute limit
  even serially; the audit is now allowed `2 * HANG_TIMEOUT` and the exact test passed in 38 minutes. The selector
  cut off `test_english_evidence.py` and `test_wire_gate_corpus.py` at one hour per file. The former's saved log then
  finished with 67 passing tests; the latter passed all 8 tests in a serial run after 1 hour 24 minutes. After these
  test and inventory fixes, the full gate on the committed final code is the aggregate result (generated block).
- **Gate attempts**: the first full gate on `4be32836` completed Lean audit, the Rust build and tests, and all
  14,433 selected Python tests, but six Q2 report tests failed because full-suite collection had already imported
  another module named `report` (`evidence/gate-initial-failed.json`). The report test now loads this batch's
  `report.py` by path (`7b75c7af`); its eight tests passed directly, and the fix selector's 78 units passed with
  zero failures. The new full gate on that clean commit passed (saved `evidence/gate-result.json`, generated block).
  That saved gate applies to `7b75c7af`, not to the later review fixes; this worker was explicitly instructed not to
  run the full gate. The merge train will run branch verification. The A7 end-to-end CLI regression passed on this
  fix round in 1,420.965 s with its outer timeout raised from 1,800 s to 3,600 s (DRI note 2026-10-13 13:20Z).
- **Seeded bugs under load**: at load 50 to 80, one run of all 11 mutants passed the one-hour limit (the Lean
  mutants rebuild `ve_service`); `mutants.py` now saves each result as it runs, and the 11 ran in four groups on the
  same code, each caught. The 12th (`python-gap-unbound`) was added with the gap binding; the 13th and 14th
  (`python-definition-unbound`, `python-row-omitted`) were added with the final relay binding fix. Each was caught.

<!-- BEGIN GENERATED: report.py -->

Scope: `main..HEAD --no-merges` at `6ce96e31` (base `96887019`): 53 commits; 145 new theorems in `lean/statements.txt` (143 in `VE.Ask` and `VE.Words`).

| Language | Files | Lines added | Lines deleted |
|---|---:|---:|---:|
| Lean | 34 | 5582 | 785 |
| Python (product) | 26 | 2437 | 374 |
| Python (tests) | 19 | 1437 | 73 |
| Rust | 0 | 0 | 0 |

Recorded answers (`tests/fixtures/ask`, replayed by `tests/test_ask_fixtures.py`):

| Fixture | Route | Lead | Rows | Row leads | Reasons | Replay s |
|---|---|---|---:|---|---|---:|
| A1 | norm-defaults | notSettled | 1 | notSettled | — | 2.9 |
| A1d | — | refused: UnsupportedProfile | 0 | — | — | — |
| A2 | norm-defaults | unknown | 1 | unknown | X4 | 2.4 |
| A3 | norm-defaults | notNecessarily | 1 | notNecessarily | — | 2.4 |
| A4 | norm-defaults | unknown | 1 | unknown | X4 | 2.9 |
| A5 | norm-defaults | unknown | 1 | unknown | X1 | 2.9 |
| A7 | norm-defaults | notSettled | 1 | notSettled | — | 3.7 |
| A8 | norm-defaults | notSettled | 1 | notSettled | — | 3.1 |
| G1 | plain | yes | 1 | yes | — | 0.2 |
| G10 | plain | yes | 1 | yes | — | 0.1 |
| G2 | plain | yes | 1 | yes | — | 0.1 |
| G3 | plain | notNecessarily | 1 | notNecessarily | — | 0.1 |
| G4 | plain | no | 1 | no | — | 0.1 |
| U2 | readings | yes | 6 | yes | — | 10.9 |
| U3 | readings | by_reading | 6 | notSettled, yes | — | 8.6 |
| U5 | readings | by_reading | 6 | notSettled, yes | — | 7.4 |
| U6 | readings | yes | 6 | yes | — | 10.9 |
| U7 | readings | by_reading | 6 | notSettled, unknown | X4 | 4.7 |

Statement check (`tools/question_statements.py --q2`, exit 0):

    Q2 statements: 27 of 27 implemented; 0 missing; 0 differ in text
    Q2 definitions: 46 approved, 32 with bodies, 32 equal to the approved text, 0 changed (0 listed with their reasons); 0 absent
    Q2 structures and inductives: 13 approved, 12 equal to the approved text, 1 changed
      changed Asked: `hnames` uses `NameReadsBackSame` (canonical JSON text, the relation `UnitBound` uses) for the approved `NameReadsBack` (kept as approved): Lean's `Json` has no decidable equality, so `=` on the read-back formula cannot be decided
    Q2 Lean check: 41 approved statements and signatures elaborated against the implementation; PASS

Seeded bugs (`mutants.py`, `evidence/mutants.json`): 19 of 19 caught.

| Seeded bug | File | Behaviour | Caught by |
|---|---|---|---|
| lean-lead-yes-without-model | `lean/VE/Ask/Basic.lean` | answer soundness: yes needs a model of the premises (lead_sound) | `lake build VE.Ask.Sound` |
| lean-cited-reversed | `lean/VE/Ask/Run.lean` | citation exactness, in segment order: a row cites its sources in the certificate's order | `tests/test_ask_fixtures.py::test_a_recorded_answer_replays_and_says_what_the_spec_says[G1]` |
| lean-gaps-dropped | `lean/VE/Ask/Run.lean` | not settled: a refuted row names the gaps its countermodel turns on, for the split | `tests/test_ask_fixtures.py::test_a_recorded_answer_replays_and_says_what_the_spec_says[U3]` |
| lean-evidence-unbound | `lean/VE/Ask/Wire.lean` | request binding: every evidence entry names a compatible choice, once | `tests/test_ask_relay.py::test_lean_refuses_a_request_not_bound_to_its_document` |
| lean-environment-unbound | `lean/VE/Ask/PlainWire.lean` | request binding: the plain case's environment is the document's | `tests/test_ask_fixtures.py::test_a_case_of_another_document_is_not_this_documents` |
| python-choice-unbound | `ve/ask.py` | relay binding: a row's choice names the request's open sets, each once, in order | `tests/test_ask_relay.py::test_every_id_rebound_is_refused` |
| python-text-unbound | `ve/ask.py` | relay binding: the answer's text is its lines' text | `tests/test_ask_relay.py::test_every_id_rebound_is_refused` |
| python-quote-unbound | `ve/ask.py` | relay binding: a line's quote is text of the unit it names | `tests/test_ask_relay.py::test_every_id_rebound_is_refused` |
| python-gap-unbound | `ve/ask.py` | relay binding: a gap names elements of the models the request's evidence holds | `tests/test_ask_relay.py::test_every_id_rebound_is_refused` |
| python-definition-unbound | `ve/ask.py` | relay binding: a cited definition belongs to the request's document | `tests/test_ask_relay.py::test_every_id_rebound_is_refused` |
| python-row-omitted | `ve/ask.py` | relay binding: a readings answer has one row for every compatible choice | `tests/test_ask_relay.py::test_every_id_rebound_is_refused` |
| python-gate-transport-only | `tools/relay_mutation_gate.py` | relay gate: ask's mutants are read as ve ask reads them, not by the transport alone | `tests/test_relay_mutation_gate.py::test_ask_is_read_as_ve_ask_reads_it` |
| lean-row-id-untyped | `lean/ResponseShape/Schemas/Ask.lean` | response schema: an answer row's id is the case's id | `tests/test_ask_relay.py::test_the_rows_id_is_typed_and_bound_to_the_case` |
| python-statement-text-ignored | `tools/question_statements.py` | statement check: a Q2 statement whose text differs from the approved text fails | `tests/test_question_statements.py::test_a_changed_statement_or_definition_fails` |
| lean-words-article-by-letter | `lean/VE/Words/Situation.lean` | one owner of situation wording (F2): an element line's article is chosen by sound, as before Q2.4 | `lake build VE.Words.Situation` |
| lean-words-negation-must-not | `lean/VE/Words/Situation.lean` | one owner of point wording (F2): an obligation's negation is `need not`, a permission's `must not` | `tests/test_words.py::test_lean_words_as_the_pre_q24_producers_did` |
| python-words-count-unbound | `ve/words.py` | words relay binding (F2): one line per requested item | `tests/test_words.py::test_an_answer_not_bound_to_its_request_is_refused` |
| python-lint-element-line | `tools/relay_lint.py` | relay lint (F2): an element line built from parts outside Lean is a finding | `tests/test_words.py::test_the_lint_refuses_a_producer_that_comes_back` |
| python-point-search-own-fillings | `ve/filling_search.py` | one flip search (F3): the point search's fillings are the shared split's | `tests/test_filling_search.py::test_point_search_sends_the_shared_split_to_lean` |

Relay mutation gate (`tools/relay_mutation_gate.py --json`, `evidence/relay-gate.json`): 0 failures and 0 findings over all routes; `ask`: 4735 mutants of 10 fixtures, 4709 refused, 26 accepted, each by a listed by-design class (B0 12, B3 14), 0 untyped.

Trust budget (`docs/trust-baseline.json`): K 997 → 997 (+0), S 9791 → 9974 (+183), V 36765 → 37363 (+598).

Full gate (`tools/gate.py`, `evidence/gate-result.json`): passed on `7b75c7af` (dirty: false); stages toolchains, lean_build, lean_audit, rust_build, cargo_test, pytest; collected 14434, deselected 1, failed 0, passed 14341, rust_ignored 0, rust_passed 36, selected 14433, skipped 92.

<!-- END GENERATED: report.py -->
