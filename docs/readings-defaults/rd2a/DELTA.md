# RD-2a: admission, separation and choices under the completion (Lean wire)

Batch RD-2a of [readings-defaults-PLAN.md](../../spec/readings-defaults-PLAN.md) (its RD-2a section), statements of
[readings-defaults.md](../../spec/readings-defaults.md) 6.3, on branch `readings-defaults/rd2a` from `167eb8ff`.
Built by one Lean worker session on 2026-10-07 and 2026-10-08; the review's fixes (below) by one session on 2026-10-08,
with the branch synced to `main` at `228f01da`; no model was called. Every number below is in
[evidence/gate.json](evidence/gate.json) or [evidence/latency-b2.json](evidence/latency-b2.json) and is checked against
it by `tests/test_readings_defaults_rd2a_report.py`.

## Review fixes (rd-2a-review: B1, B2, B3; C2 and C3 with them)

| Finding | Fix (the class, not the example) | Regression test | Commit |
|---|---|---|---|
| B1: the merge with main broke the build (`witnessConflictX` returns a triple), `ndInner` copied `runLayered`'s dispatch and lacked main's `conflictFields`/`statusFields`, the tests called the deleted `nd.check_conflict` | synced with `main` twice (`81d53b6b`, then `228f01da` with RD-6a); `layeredCase` is the one dispatch of the layered kinds, called by `runLayered` and by `ndInner`; the tests propose evidence with the pinned oracle `conformance.frozen_norm_defaults`, as main's do; main's Lean-backed `UnspecifiedDocument` is built with `readings@1` stripped beside content-bearing sets too (Lean's `runLower`) | `test_inner_answers_are_the_norm_defaults_routes`: each inner answer equals the norm-defaults route's on the choice's document, field for field (13 cases, R1) | `16462b5d`, `1eb94f6f` |
| B2: under the completion validate and separate admitted the author's document twice; C2: so did the S2a kinds of a norm-defaults document with no content-bearing set | `runCase` admits once and passes the admission on (`admitS2Of` continues S1's admission; every S2a runner and `replayCertificateOf`/`replayModelOf` take the admitted document) | `test_the_route_admits_the_case_document_once` (compiled-IR walk: only `runCase` calls `admitS2`, only it and `admitS2` call `admitReadings`, no JSON admission is reachable; R4) | `eb503391` |
| B3: the relay expected the abstention, so `ve document` raised `ReadingsConformance: ... S2 route` on every completion document; this file described it wrongly | Python's route row follows Lean's `routeOf` (the completion on the norms chain, the abstention elsewhere); for the completion the relay binds Lean's route and cause, then refuses by name (`UNDER_COMPLETION`) until RD-2b; the availability paragraph below is corrected | `test_rd2a_review_b3_completion_document_is_refused_by_name`, `test_rd2a_review_b3_route_table_is_lean_s` (R2, R3) | `e77b0b86` |
| C3: the rights-chain abstention was untested | (no code change) | `test_fnd6_rights_chain_keeps_the_abstention` | `16462b5d` |

Open: C1 (no service fixture reaches step 5's `choiceStepText`/`ndChoiceText`; `ND4` unused) and C4 (spec 8.3 rows
F-ND4 and F-ND10, the planner's: EXTERNAL) are follow-ups, not done here.

## What changed

- `lean/VE/Readings/UnspecifiedWire.lean` (new): `underCompletion`, `unspecOf`, the reserved names (`reservedUnsaid`),
  `ndText` (4.1 steps 2 and 3), `ndChoiceText` and `choiceStepText` (step 5, SR1), `AdmittedND`, `admitND`
  (`admitNDFull` with the run's tables), the filled document as S1's admitted document (`filledEnvironment`,
  `FilledAdmitted`), `replaySeparateU`, `replayChoiceU`, the three 6.3 theorems, and the runners of
  `readings-elaborate` and `readings-choice` under the completion. Each choice is read as norm-defaults' layered
  source with no extra premise (`choiceLayered`), so the conflict (packages or a filled witness), status, report and
  elaborate inner kinds are the layered branch's own dispatch (`layeredCase`, review B1); `norm-defaults-certificate` checks `premisesU` on the choice
  (`acceptanceU`), `choice-model` a base model with a separate filling (`modelCheckU`).
- `NormDefaults/Wire.lean`: `EntailsU`, `acceptanceU`; `normDefaults_wire_acceptance` keeps its statement and calls
  the shared proof `acceptance_of_fillTyped`. `NormDefaults/Report.lean`: `modelCheckU`, `modelCheckU_sound`.
- Definitions only: `Wire.abstention` fires off the norms chain only; `routeOf`'s norm-defaults row is the enumerated
  route on the norms chain; `elaborateFields` gives that route the finding `ReadingsNotSuperposable: <every open
  set>`, cause `the unspecified completion` (`completionFinding`); `admitReadings` is decoding then `admitDecoded`;
  `setPairs` and `validateResult` are `setPairsWith id` and `validateResultWith id`; `runDead` is admission then
  `deadAnswer`; `Run.runCase` dispatches every readings kind of a completion document to the new runners
  (`readings-conflict`, `-certificate` and `-model` are refused until RD-6 with
  `ReadingsNotSuperposable: <sets> (the unspecified completion); use readings-choice`).
- Wire answers: `readings-validate` under the completion adds `fill_premises` (per reading with content, its
  `Fill_T` labelled `unsaid:pair:<r>,<m>`) and `filled` (the lower environment with `unspecified` read as `deny`,
  `norm-defaults@0` removed and `unsaid__p` added; the filled units, `F_p` units last). Schema `readings-route.json`
  (`fill_premises`, `filled`, regenerated from `ResponseShape/Schemas/ReadingsRoute.lean`); every new runner has its
  `*_fits` theorem.
- Python, relay only: `ve/readings_route.py`'s row check accepts the two new fields, typed, and reads neither (their
  relay is RD-2b). No Python search, count or classification was added.
- Manifests: `VE/Audit.lean` and `ResponseShape/Audit.lean`, `axioms.txt`, `statements.txt` (additions only),
  `predicates.txt`, `declarations.txt`, `VE/Route/frozen-sources.sha256`, `tools/trust-classes.json`,
  `ve/assurance-manifest.json` with `docs/spec/assurance-manifest.md`, `lean/checkers.lock` (the new `ve_service`),
  `tools/gate-collection.json`, `tools/consolidation-ledger.json` (step 5 names `setPairsWith`) with the plan's
  measured rows; `tools/check_readings_defaults_statements.py` compares spec 6.3 too; `lean/READINGS.md`.

## Deviations from the spec, each for the statement re-review or the planner (EXTERNAL)

1. **F-ND4 and F-ND10 as specified are not reachable on the wire.** The spec's values (252 and 251 fixed rules on one
   predicate) were *derived*. Measured: one predicate's generated layer exceeds the depth limit (64) at about 52
   rules, before any rule limit, with or without the completion; and S1's own admission grows steeply in the
   number of fixed units (see Latency), so 250 units exceed the service's CPU deadline. Built instead: the rule
   limit of a choice pinned by `#guard` on `choiceU` in `UnspecifiedExamples.lean` (253 rules, `checkAuthorN`'s
   `ResourceLimit: rules`); step 3's per-reading refusal through the service with `checkAuthorN`'s precedence limit
   (F-ND4 as `test_fnd4_a_readings_document_beyond_an_author_limit`: chains of 14, 15 and 17 rules give `ok`,
   `ResourceLimit: precedence depth under rs_1@1:0` and the free document's `ResourceLimit: precedence depth`). No
   service fixture reaches `ndChoiceText` itself: every additive limit of a choice is reached first by a layer
   limit of S2a's check. Owner: planner (spec 8.3 rows F-ND4, F-ND10).
2. **Step 4 is S1's staged admission of the filled document** (`admitDecoded` on the filled environment), which runs
   `admissionText`'s checks with the same texts and builds the filled document's own table; the spec writes
   `admissionText re (fillDoc N)`. Equal texts: the filled environment differs only by the `unsaid__p` base
   predicates, which `reservedText` does not refuse.
3. **`AdmittedND` is as specified**; the runners use `AdmittedNDFull` (it adds the filled document's admission and the
   table of the author's documents). `ndText` is `ndTextWith re N (one N.D)`; admission evaluates `ndTextWith` on the
   request's table (`ndTextWith_eq`) and derives `WellFormedND`'s norm-defaults conjuncts from it
   (`ndRest_of_ndText`), so each check runs once.
4. **`fill_premises`** is one top-level list per reading, not a field of each candidate row (S1's rows stay
   byte-identical).
5. **One more build of the free document per request under the completion** (`freeU`, step 3), recorded in
   `tests/test_readings_lean_sharing.py` beside `sharedEnv`'s; every reading's document is built once, in a table.
6. **The 10a cores.** `acceptanceU` and `modelCheckU_sound` are new UDoc lemmas; the witness, status and report checks
   are the layered branch's dispatch (`layeredCase`) with its functions and theorems (`witnessConflictX`,
   `replayStatusX`, `layered_report_sound`) on the choice's document instead of new lemmas.

## Availability change (HUMAN: DRI to sign)

A `readings@1` document with content under `norm-defaults@0` on the norms chain no longer gets the abstention: Lean
admits it (`readings-validate`; `readings-elaborate` on the enumerated route with the cause "the unspecified
completion"; `readings-choice`). `ve document` has no fold for such a document's choices until RD-2b relays their inner
kinds, so after binding Lean's route and cause the relay refuses the document by name (`ve/readings_route.py`,
`UNDER_COMPLETION`): `UnsupportedProfile: readings with content under norm-defaults@0 on the norms chain (the
unspecified completion) are admitted by Lean's readings route; ve document relays their checks from readings-defaults
RD-2b`. That is a refusal, never a verdict and never a conformance alarm (review B3: the relay used to expect the
abstention and raised `ReadingsConformance: Python and Lean differ on the S2 route`; the earlier text here, that
Python's fold reaches inner kinds Lean refuses, was wrong). Tests:
`test_rd2a_review_b3_completion_document_is_refused_by_name` and `test_rd2a_review_b3_route_table_is_lean_s`. A set
with a pending candidate takes the pending route and loads unresolved: changed test
`test_ruling4_rule_candidate_beside_norm_defaults_is_under_the_completion` (the pilot's probe (b)). The soft chain (K18)
and the rights chain (`test_fnd6_rights_chain_keeps_the_abstention`) keep the abstention, and every other document keeps
its answer: the corpus A/B below has no difference.

## Gate (HEAD before this report, `b7d3822a`, this worktree with a clean status)

| Check | Result |
|---|---|
| `lake build` | 809 jobs, success |
| `python3 lean/audit.py` | PASS: 437 source files, 4745 theorems (base 4707), standard axioms only |
| `python3 VE/Route/frozen.py` | PASS |
| `tools/lean_statements.py --check` | PASS: 4371 statements (base 4345), 0 changed, 0 removed |
| `tools/check_readings_defaults_statements.py` | RD-1: 31 exact, 0 pending; RD-2a: 16 exact, 0 pending (RD-6a, main's: 7 exact, 1 amended) |
| service fixtures `tests/test_readings_nd_lean.py` | 19 passed, 1.26 s serially |
| full suite in 5 chunks (`-n 16`, `VE_LEAN_PREBUILT=1`, the 4 slow tests and this report's test deselected) | 2171, 3862, 1823, 2499 and 1688 passed; 1, 2, 3, 0 and 0 skipped; 0 failed |
| the 4 slow tests alone (`-n 4`) | 28 passed |
| this report's test, after the report commit | 7 passed |
| corpus A/B (`tools/lean_first_diff.py`, base `167eb8ff`, at `17470adc` before the review fixes) | 94498 records, 94498 the same, 0 unlisted (`evidence/ab-*.json`) |
| `tools/trust_map.py` | 0 unclassified; `--check` still fails on growth that predates RD-2a (RD-1's DELTA) and on main's (RD-8, lf-10b); RD-2a's own trusted growth is `UnspecifiedWire.lean` and `Run.lean`'s runners |

The base is `main` at `228f01da` (the second sync). Not run: `tools/gate.py` in a fresh worktree (it does not fit one
60-minute foreground call; the chunks above are its suite); the corpus A/B again after the review fixes (the saved
evidence is from `17470adc`); the plan's latency budgets on a quiet host.

## Latency

Admission of F-ND1's set beside `n` fixed rules over 20 extra regulated pairs, in CPU seconds per request of the
`ve_service` process (every thread, six calls after a warm-up), the build before review B2 (`02803f6b`) and after it
(`3fa65c68`) timed in turn on the same host (load 17 to 27 on 32 cores); `docs/readings-defaults/rd2a/latency.py`:

| `n` fixed units | `deny` validate, before | after | `unspecified` validate, before | after | elaborate, before | after |
|---|---|---|---|---|---|---|
| 10 | 0.41 | 0.31 | 9.72 | 7.71 | 2.97 | 3.24 |
| 20 | 0.66 | 0.43 | 10.48 | 11.7 | 4.37 | 4.29 |
| 30 | 1.01 | 0.77 | 12.04 | 12.01 | 7.17 | 7.89 |
| 44 | 5.0 | 3.7 | 30.52 | 25.89 | 18.58 | 16.18 |

With every completion `deny` the completion's own checks are trivial and the author's admission is most of the cost:
the second admission B2 removed was a quarter to a third of it at every size. With unspecified completions the
norm-defaults checks and the filled document's admission dominate (about ten times the `deny` cost), and the saved
admission is within this loaded host's noise; `readings-elaborate` never admitted twice. Both builds' answers were
the same on every request.

## Seeded bugs (each planted, the test run, then removed; the binary rebuilt and its pinned hash restored)

| # | Bug | What failed |
|---|---|---|
| M1 | step 3's per-reading suffix replaced | `test_fnd4_a_readings_document_beyond_an_author_limit` |
| M2 | the witness's `Fill_T` check dropped from `ndPairFacts` | `test_fnd1_prime_the_witness_filling_must_satisfy_its_fill_premises` |
| M3 | `readings-validate` not dispatched under the completion | 8 tests of `test_readings_nd_lean.py` |
| M4 | a choice's packages bound to the first compatible choice's document hash | `test_fnd1_each_choice_conflict_free_and_certificate` (after the test gained an independent hash check: the first run passed, the bindings having been read from Lean's own answer) |
| M5 | the abstention kept on the norms chain | 15 tests of `test_readings_nd_lean.py` |
| M6 | the relay's row check without `fill_premises` and `filled` | `test_ruling4_rule_candidate_beside_norm_defaults_is_under_the_completion` |
| R1 | `ndInner` answers a witness's CONFLICT itself, without main's `conflictFields` (review B1) | `test_inner_answers_are_the_norm_defaults_routes` (`test_fnd2_latent_conflict_under_one_reading`, which reads the verdict only, passed) |
| R2 | the relay's route row back to the abstention for every `norm-defaults@0` document (review B3) | `test_rd2a_review_b3_completion_document_is_refused_by_name` and `test_rd2a_review_b3_route_table_is_lean_s` (the conformance alarm) |
| R3 | the norm-defaults document built with `readings@1` beside content-bearing sets (review B3, after the sync) | `test_rd2a_review_b3_completion_document_is_refused_by_name` (`Unsupported profile readings@1`) |
| R4 | `readings-validate` admitted again through `admitNDFullJ` (review B2) | `test_the_route_admits_the_case_document_once` |

The statement checker's tests also fail on every changed 6.3 declaration, a dropped hypothesis and a missing
declaration; the report test fails on a wrong A/B total in this file and on a seeded bug naming a test that does not
exist (each tried once, then restored).

## Build checklist

| # | Status |
|---|---|
| 1 one contract | partly: every new text is Lean's and Python relays it; readings@1 has no generated diagnostic table (none existed before) |
| 2 differential fuzz | not done: no Python or Rust implementation of the completion exists (Lean only); RD-2b's relay is the first other path |
| 3 normalization | not applicable: no text input |
| 4 untrusted output | partly: the relay checks the new fields' shape (M6); no fuzz of genuine responses for them yet (RD-2b reads them) |
| 5 malformed input | partly: F-ND8's tampering (stolen packages, an ill-typed filling tuple, an `unsaid__` table as a table, outside the profile too); no 7/true/null sweep over the new inner kinds |
| 6 three-valued verdicts | done for what exists: missing or unbound packages give UNKNOWN with `detail`, a refused inner case is an error row; `ve document` refuses a completion document by name before any fold |
| 7 deadlines | not applicable: the service's per-case CPU deadline wraps every new kind; no new loop has its own budget |
| 8 exhaustive folds | done: the inner kinds fall through to the norm-defaults route's refusal |
| 9 English | not applicable: no sentence (RD-3) |
| 10 one admit() | done: every readings kind of a completion document goes through `admitNDFull` (validate, separate, elaborate, choice, dead; the superposed kinds after it), and each case admits its document once (review B2, `test_the_route_admits_the_case_document_once`); `ve document` refuses a completion document by name (review B3) |
| 11 no regex of a real language | partly: the statement checker reads Lean text by regex, as RD-1's |
| 12 state machines | not applicable |
| 13 tests can fail | done: M1 to M6, R1 to R4 |
| 14 hermetic | done: the new tests write nothing, read no environment variable, no sleep |
| 15 identity | done: each choice's packages are bound to its own document hash and environment id, checked against an independent hash (M4) |
| 16 lists | done: audit manifests, frozen inventory, statement, predicate and declaration dumps, trust classes, assurance manifest, gate collection, ledger |
| 17 statement diff | done: 16 of 16 exact; no DRI ruling in RD-2a; the deviations above need the planner's update of 8.3 |
| 18 both directions | done: F-ND9 (depth 50 both admit, 52 only S1, 56 neither), F-ND4 (14, 15, 17), F-ND1 both separation directions and not separated, F-ND5 a rule name and a unit id, conservativity with `deny` and without content |
| 19 use-case formalisation | not applicable |
| 20 reports | done: `tests/test_readings_defaults_rd2a_report.py` checks this file's numbers against `evidence/gate.json` and the A/B files |
| 21 AGENT/HUMAN/EXTERNAL | done: the availability change is HUMAN (DRI); the 8.3 deviations EXTERNAL (planner, statement re-review); the rest AGENT |
| 22 hand-off | partly: all committed, chunked suite on HEAD with a clean status, 67 GB free; `tools/gate.py` in a fresh worktree not run |
