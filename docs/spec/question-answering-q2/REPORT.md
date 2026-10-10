# Question answering Q2: build report

Branch `question-answering/q2`, base `main` at `f0547468` (Q1 merged). The spec is
`docs/spec/question-answering.md` (5.2 for the statements, 7 for the fixtures, 8 for the wire); the plan is
`docs/spec/question-answering-PLAN.md` (Q2.1 to Q2.6). Builder's working notes: `../question-answering-q2-progress.md`.
User-visible deltas, each needing the DRI's signature: `DELTA.md`. Every number below the generated block's marker is
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
generated from Lean's shapes) and bound to the request (every row, line, reading, witness, source, quote, unused unit,
unchecked name and identity the answer names exists in the request), and decides nothing (`tools/relay_lint.py`).

## What was built, by plan item

| Item | Status | Where |
|---|---|---|
| Q2.1 answer core | done | `lean/VE/Ask/{Basic,Sound,Sources,Groups,Plain,Examples}.lean` |
| Q2.2 `ask` wire | done, three routes | `lean/VE/Ask/{Binding,Wire,PlainWire,ZeroWire,Run}.lean`; `VE.Service.Protocol` mode `ask` (`runMode_ask`); `lean/ResponseShape/{Schemas,Encoders}/Ask.lean` |
| Q2.3 words and text | done (see "Not done") | `lean/VE/Words/Situation.lean`, `lean/VE/Ask/{Lines,Render,PlainAnswer,ZeroAnswer}.lean`; the frames' `num` piece (DELTA D3) |
| Q2.4 one owner of situation wording | **not done** | see "Not done" |
| Q2.5 `ve ask` | done | `ve/ask.py`, `tools/ask_fixtures.py`, `tests/fixtures/ask/` |
| Q2.6 evidence and measurement | **partly**: fixtures and this report | see "Not done" |

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
  quote, unused unit, unchecked name and identity rebound refused; Lean's own binding (names, evidence entries,
  asserted names); a broken split and a split differing in a base atom are not splits; a fence read as two formulas
  is not the case's unit; each request and case field replaced by 7, true, null, [], {} or a 10,000-deep list is
  refused, never answered; the mode's CPU deadline bounds the whole answer; Lean's refusal raised with its class and
  text, a forged refusal unavailable; the schema types every field.
- `tests/test_ask_cli.py`: `ve ask` end to end on G1, G3, G4 and U6, the leads, the refusal of G5, the JSON honesty
  fields, and eight odd spellings of a question reaching the answer only through Lean's reader (checklist 3, 10).
- `tests/test_question_statements.py`: the statement check above.
- `tests/test_question_answering_q2_report.py`: this report against its saved evidence.
- `lean/VE/Ask/Examples.lean`: spec 7.6's figures (4,802 rows and their leads and reasons, the fold agreement, the
  groups) and the frames' `num` piece, as `#guard`s; `lean/VE/Ask/Run.lean`: X5's `#guard`s.

## Seeded bugs

8 seeded bugs, 5 in Lean and 3 in Python, one per behaviour claimed, each in a file this batch changed, each caught,
then removed (`mutants.py`, `evidence/mutants.json`; the table is in the generated block). No Rust code changed.

## Build checklist

| # | Line | State |
|---|---|---|
| 1 | One contract | The answer's shapes are Lean's (`ResponseShape/Schemas/Ask.lean`), rendered to `ask.json`; `ve/ask.py` reads its field sets, leads and reasons from that file, and a refusal's statuses, codes and classes from Lean's exported question contract (`ve/question/codes.json`). Every text is Lean's. |
| 2 | Differential fuzz | Not applicable: the answer has one owner (Lean); there is no Python or Rust answer to compare. The relay is fuzzed instead (4, 5). |
| 3 | Normalisation | The question reaches `ask` only through Q1's reader; `test_ask_reads_the_question_as_the_reader_does` covers NBSP, double space, tab, `\r`, curly quotes, U+212A, dotted I and a control character. |
| 4 | Untrusted output | Schema from the producer, binding to the request, bool-for-int refused, fuzz by dropping, emptying, duplicating, retyping and rebinding each field (`tests/test_ask_relay.py`). |
| 5 | Malformed input | `test_a_malformed_request_is_refused_never_answered` (three routes); Lean now refuses evidence of another type, foreign case fields and names on a one-choice route (DELTA D11). |
| 6 | Three-valued | No evidence answers unknown (X2 or X4), never yes or no (tested); past 64 choices is `ResourceLimit` (X5's text). `ask` has no budget option, so budget 0 has no entry point; the generators' budgets are internal. |
| 7 | Deadlines | The mode's CPU deadline wraps the whole request (`test_the_deadline_bounds_the_whole_answer`). A delay was not injected into each Lean callee. |
| 8 | Exhaustive folds | Lean's matches on `Lead`, `Reason`, `Source` are exhaustive by the compiler; Python reads the enumerations from the generated schema. |
| 9 | English one reading | Every line, A0 included, passes W7's all-derivations gate before it is shown (`answerFor_gated`, `answerForPlain_gated`, `answerForZero_gated`); a reading's name is read back to its formula where the candidate is asserted, else marked unchecked. |
| 10 | Entry points | `ve ask` (text, `--json`, `--reading`, `--evidence`) all go through one relay call (`ve.ask._ask`); metamorphic test as in 3. |
| 11 | No regex of a real language | The statement check uses Lean as the oracle; the text comparison is the existing whitespace-collapsed one. |
| 12 | State machines | Not applicable. |
| 13 | Tests can fail | 8 seeded bugs; `test_a_replay_can_fail`; the statement check's mutants. |
| 14 | Hermetic | CLI tests use the env allowlist and `HANG_TIMEOUT`; writes go to `tmp_path`. |
| 15 | Identity | Every identity field of the answer rebound and refused. |
| 16 | Lists | Fixture list, gate collection, frozen inventory, decoder pins, binding probe, trust classes, layer policy, import-linter layers: generated or tested. |
| 17 | Spec statements | `tools/question_statements.py --q2` and its test; DELTA rows for each difference. |
| 18 | Spec-stage | Not applicable (build stage). |
| 19 | Use-case formalisation | Not applicable: the fixtures use the existing G, UDHR and agent-policy documents. |
| 20 | Reports | This report's numbers from saved evidence, by test; what was not run is listed below. |
| 21 | Acceptance tags | Below. |
| 22 | Tests | Selected tests while iterating; the full gate once on the final HEAD (generated block). |
| 23 | DRI rulings | `DELTA.md`: no standing ruling covers a row; each needs the DRI's signature. |

## Acceptance items

| Item | Tag | State |
|---|---|---|
| Q2 statements proved; audit clean | AGENT | done |
| Fixtures G, U, A replayed from recorded evidence | AGENT | done; six leads differ from the spec's derived ones (DELTA D6) |
| Typed schema, binding, fuzz tests | AGENT | done |
| Seeded bugs | AGENT | done |
| Full gate on the final HEAD | AGENT | generated block |
| Q2.4 one owner of situation wording (Python producers deleted, corpus A/B byte-identical) | AGENT | **deferred** to a later batch; owner: the orchestrator (DRI) |
| Q2.3 `VE.Words` `#guard`s recorded against Python's producers on the readings and norm-defaults corpora | AGENT | **deferred** with Q2.4, whose A/B is that comparison |
| Q2.6 reading and writing evaluation (Sonnet as reader and writer) | EXTERNAL | **deferred**: needs model calls, which this task forbids; owner: the orchestrator |
| Q2.6 latency and agreement with W2 | AGENT | **deferred** with Q2.6 |
| DRI signatures on DELTA D1 to D12 | HUMAN (DRI) | pending |

## Not done, and not run

- **Q2.4** (Lean routes carrying `VE.Words`' lines, Python's situation-wording producers deleted, the relay-lint rule,
  the corpus A/B): not started. The task named Q2's answers, proofs, `ve ask`, the schema and binding, fixtures,
  seeded bugs and this report; Q2.4 touches the merged readings and norm-defaults routes and needs its own A/B.
  Release needs it (plan: "Release requires Q2.4 and Q2.6").
- **Q2.6's evaluation, latency and W2 agreement**: not run (model calls forbidden here).
- **Q2.2's "A/B shows no change outside the new mode"**: no corpus comparison was run; the full gate is the evidence
  that existing behaviour is unchanged, and DELTA D9 names the one generator change that can change a readings
  answer.
- **Lean CPU**: `english.question` after the frames' `num` piece (DELTA D3) was not measured against a base binary;
  `ask` has no base. Recorded replay times are in the fixtures table (UDHR part 7: about 11 s per question; the
  agent documents about 3 s; the G document 0.1 to 0.2 s).
- **Flaky test seen once**: `tests/test_question_reading.py::test_the_whole_question_is_bounded_by_the_modes_deadline`
  (Q1's, unchanged) did not raise once in a combined run and passed on two reruns; it races a near-zero deadline.
- **The selected-tests run** with `--jobs 8` stopped at the one-hour limit while re-recording its coverage map, after
  336 of 345 files had run; the 9 files it had not reached were run directly and passed, and the 4 files it reported
  failing were fixed (the trust baseline's totals, the `ask` seed of the response fuzz, the nested-pytest builder in
  `mutants.py`, the nullable enum of the schema) and rerun.

<!-- BEGIN GENERATED: report.py -->
<!-- END GENERATED: report.py -->
