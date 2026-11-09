# ap-4 report: the `act-readings` mode, its relay and `ve acts readings`

- **Status:** built, and the review's four B findings fixed (ap-4-review.final.md, F1 to F4: section "Review fix"
  below); no DRI signature reserved. DELTA row 1 cites reviews/dri-decisions-20261108-ap-4.md item 1, row 2
  R16. Sources at readings admission (deliverable 5), its O5 DELTA row and deliverable 8 move to **ap-4c** under that
  decision's items 3 (b) and 6.
- **HEAD:** this branch's final commit; base `da5303b78` (main, `git merge-base HEAD main`).
- **Changed:** `lean/VE/Acts/Run.lean` (the mode), its shape and encoder theorem, registration, `ve/acts.py`,
  `ve acts readings`, two test files, five route cases.
- **Open:** none in this item. The parse's CPU grows with the frame count; the DRI kept spec 12's limits and the 5 s
  deadline (reviews/dri-decisions-20261109-ap-4.md item 1) and filed the parser row `ap-parse-index` (item 2).

## Review fix (ap-4-review.final.md, 2026-11-09)

Each finding was fixed as a class (FINDING-CLASSES.md), with the review's probe run before (it failed, as the review
says) and after (it passes) and turned into regression tests; every test named below passed on the final code.

| Finding | Class and fix | Regression tests | Commit |
|---|---|---|---|
| F1 (B) relay refuses E16's genuine answer | N9 (valid answer refused): `answer_problem` checks exactly spec 7's binding list and R8's "no row empty"; "an act occurs twice in one reading" dropped. Class test over every genuine answer; the fuzz waives a duplicated act (Lean's content), as does the relay gate (`tools/relay-gate-allow.json` AP4-F1) | `test_e16_one_act_written_twice_is_bound`, `test_every_genuine_answer_is_bound` (pilot, `from` fixtures, edges) | `a7ec90c1c`, `ed40ac9a6` |
| F2 (B) `decodeFixed` once per act | Evaluated-once (10-27 rule): no act is lexed again; each act's tokens come from the meaning (`Simple.toks`), and the readings with their derivations from the one parse (`witnessed`, proved equal to `phraseReadings` by `witnessed_readings`) | `test_each_act_is_read_off_the_parse_not_lexed_again` (128 fixed phrases, P64: 64 readings LISTED; was `CheckerUnavailable`); RunExamples' `witnessed` guard; plants `witnessed-no-limit`, `firstsBy-keeps-equal` | `9fa57885b` |
| F3 (B) `--acts` coerced or crashed | 15 (malformed input crashes) and coercion: `request` coerces no member (`_as_sent`), so Lean's decoder refuses a mistyped one; the file is read as `ve calc` reads its case (package cap, `loads_json`), must be an object with only `fixed`, `frames`, `adverbs`; every `VEError`, `OSError`, `UnicodeError` is exit 2 (4 at the cap) | `test_a_malformed_acts_file_is_invalid_input_never_coerced` (7 cases), `test_an_unreadable_invalid_or_oversized_acts_file_is_invalid_input_or_a_limit`, `test_the_request_coerces_no_member` | `a7ec90c1c`, `ed40ac9a6` |
| F4 (B) `from` searched by text | Structural: `from` is read off each reading's own derivation with its content leaves tagged by place (`tagTree`; `piecesOf` unchanged), so a repeated word is its own item's token; a written token (subject, *to*, *be*, marker, join word, comma) is the nearest function token before the next content token new to the act | `test_from_names_the_tokens_each_act_is_made_of` (11 phrases: repeated objects, E16, shared *to* and object, split markers, three items, P11, A5's second meaning), `test_every_from_token_is_a_token_of_its_acts_text`; RunExamples' `from`, `fnsOf` and token-text guards | `9fa57885b` |

The review's C1 is closed with F1's fuzz work: a moved index or span is waived only while it stays in range, and each
`from` index and span is pushed out of range and duplicated (`pushed`). C2 (the 400 bytes charged on the raw phrase)
is unchanged: the safe direction. Probes after the fix: F1 `LISTED`, F2 64 readings (under 1 s wall with Python's
start, against about 50 s CPU before), F3 `[2, 2]`, F4 `[0, 1, 2, 3]`. None of the failures below is on
`main-known-red.txt`, and none of that list's tests was selected as failing here.

## Plan rows and task deliverables

Plan `docs/spec/act-phrases-PLAN.md` AP-4 (lines 959-1016 at `b5c1e805b`, equal to main's file); spec
`docs/spec/act-phrases.md` 7 and 11.4 (main's file differs from `b5c1e805b` only in an AP-3 statement's namespace,
line 1280).

| Task deliverable | Where | Evidence |
|---|---|---|
| (1) `runActReadings`: a phrase's readings and paraphrases; Lean lexes the phrase and returns each act's token indices | `lean/VE/Acts/Run.lean`: `decodeRequest`, `listed`, `listReadings`, `rowsOf`, `readingJson`, `actJson`, `spans`, `fromOf`, `sameTok`, `refusedRow`, `verdictOf`, `actReadingsReported` | `lean/VE/Acts/RunExamples.lean` (A5, A8-A12 counts; AR1 pinned; spans and indices; D-32; limits; refusals) |
| (2) the shape and `runActReadings_fits` | `lean/ResponseShape/Schemas/ActReadings.lean`, `lean/ResponseShape/Encoders/ActReadings.lean` (`runActReadings_fits`, `actReadingsReported_fits`, used by `runMode_fits`) | `lake build` (1331 jobs); plant `listReadings-bogus-verdict` breaks `Encoders/ActReadings.lean:43` |
| (3) the mode through AR-10's registry, `MODES`, `ve acts readings` | `lean/VE/Service/Registry.lean` (`Mode.actReadings`), `Protocol.lean` (`runMode`, `runMode_actReadings`), `envelope.json` (generated; `MODES` reads it), `DEADLINES`, `ve/__main__.py` | `tools/repo_map.py --check`: "PASS: 43 modes, each with its schema file"; `RegistryExamples.lean:6`; `test_the_command_line_prints_leans_answer` |
| (4) `ve/acts.py`, relay only (R8): schema and binding (in range, none repeated in an act, readings distinct); lexes nothing | `ve/acts.py` `read_answer` (`check_row` on `act-readings.json`, then `answer_problem`) | `tools/relay_lint.py`: "PASS: 21 relayed module(s)"; the fuzz below |
| (5) one `sourceCheck` call per source at readings admission | **not delivered: ap-4c** | DRI 2026-11-08 items 3 (b) and 6 (below) |
| (6) `tests/test_acts_readings_lean.py`, `tests/test_acts_readings_answer.py` (AR1-AR5 fuzz) | both files | 18 + 12 tests, all passing (Tests) |
| (7) the plan's Tests: A9, A10, A11 give 2; A5, A8, A12 give 4 | `test_the_pilot_phrases_give_the_readings_the_audit_asks_for`; RunExamples:32 | passes |
| (7) rs_u055 passes; rs_u105b/c refused under F11 (S1, S8); skipped middle, missing reading, permission to prohibition, `unspecified` to `deny` refused | `sourceCheck`'s fixtures, ap-4b/ap-3r's (`ReadingsExamples.lean:183-239`), unchanged; through admission: ap-4c | `lake build VE.Acts.ReadingsExamples`; plant `e1x-all-dropped` refuses S4 (`ReadingsExamples.lean:213`) |
| (7) 64 listed, 65 refused, raw cap refused | RunExamples:95-96, `test_64_readings_are_listed_and_more_are_a_limit`, `test_a_saturated_raw_cap_is_a_limit` | passes; "65" is spec 11.4's P65, 128 readings: the L family's counts are powers of two, so no 65-reading phrase exists among the fixtures |
| (8) "Deleted": the pilot's hand-built separating situations | **not delivered: ap-4c** (the task's first cut) | it needs (5) |
| DRI ap-7-fail item 2: an adverb inside the last joined item reads over that item only | RunExamples:79-80, `test_an_adverb_inside_the_last_joined_item_reads_over_that_item_only` | passes |
| Evaluator rule: each value once, charged against stated limits, a fixture at each | the 400-byte act phrase and the parse limits checked in `listReadings` before the parse; `decodeFixed` and `checkVocab` charge fixed phrases and frames before the parse; the phrase lexed, listed and paraphrased once | 400/401 bytes, 300/301-byte fixed phrase, 128/129 fixed phrases, 129 frames, 64/128 readings, raw cap: tests above; the frame count's CPU: "Cost at the limits" |

### Why (5) and the O5 row moved

The DRI signed sources at admission on the readings route (item 2) but rejected leaving `sources` out of
`environment_id` (item 3) and accepting it unchecked on other `acts@0` routes (item 6). Fail-closed acceptance needs a
flag threaded from `Readings/Run.lean` to the frame decoder through every readings admission entry point, while the
`document`, `environment` and other modes that call `Readings.Wire.decodeEnvironment` keep refusing it: `decodeFrame`,
`decodeEnvironment`, `admitReadingsSpec`/`admitReadings` and `admitReadings_eq` (Readings/Wire.lean), `admitS2`
(SupWire), `admitSD` (SoftWire, SoftVerdicts), `splitCase` (Companions), the three identity sites (Wire.lean:458,
UnspecifiedWire.lean:507, 522), and Run.lean's `validateOne`, `elaborateOne`, `runOne`, `admitComponent`,
`admitChecked`, `admitComponents` and the memo path. Each is trusted readings code, so each new parameter is trusted
growth with its own mutants on top of this item's +57 (R16's line is 150), and the S-fixtures through admission and
the O5 condition come with it. The DRI's item 3 (b) names this cut; the first build (commit `130f17598`) took the
inert-data route item 6 rejects and was reverted in `337b2d782`, so `sources` stays refused as an unknown field on
every route, as on the base.

## Deviations (no approved statement changed)

1. **`form` is optional, not `null`.** Spec 7's request lists `form`; the service's restricted JSON has no `null`
   (`offset 289: expected restricted JSON value`), so an absent `form` is no form.
2. **The act phrase's limit is 400 bytes** (`Lexical.maxActBytes`), not the task's "300": DRI item 1 ("the builder's
   reading is right and the task file is wrong").
3. **`LIMIT` is any `ResourceLimit`** (`verdictOf`: the diagnostic's code), `REFUSED` any other refusal; both lists
   are then empty and `diagnostic` is present (the schema's `if/then/else`).
4. **`act` and `text`.** `act` is the simple act as a predicate declares it (`Simple.text` with *to* exactly when the
   role is plain, as `Sources.expected` renders it); `text` is the act under the modal (`sentence`).
5. **`from`** (spec 7: "the indices into `tokens` of the request tokens its text is made of, in the act's order"):
   read off the reading's own derivation (review F4). `witnessed` keeps each meaning's first derivation from the one
   parse; `tagTree` tags its content leaves by place, so `piecesOf` gives the same meaning with each word, slot and
   fixed phrase naming its token; a token the meaning writes itself (the subject, *to*, *be*, a marker's or join
   word, a comma) is the nearest equal function token before the next content token new to the act; each place once,
   in the act's order; a token the rendering adds that the phrase lacks (*to* after *has the right*) has none
   (`fromOf`). An act's normal form may reorder the phrase (G5's *enjoy* reads the shared object before its
   modifier: `[0, 4, 5, 8, 9, 10, 6, 7]`), and a whole join reads a shared token once.
6. **Binding beyond spec 7's list**, all of R8's "no row is empty": a reading needs acts and a paraphrase, an act needs
   text and tokens, a refusal needs a diagnostic, token spans only with `LISTED`. Which acts a reading lists, one
   twice included, is Lean's content (review F1: E16 reads one act written twice). The
   64-reading bound is the schema's (`maxItems` = `VE.Acts.maxReadings`), so Python holds no copy of it.
7. **Files beyond the task's list**, each a registration a new mode or module needs: `ve/backends/lean_service.py`
   (the deadline, recipe step 4), `tools/relay_lint.py`, `tools/layer_policy.py` and `docs/ARCHITECTURE-LAYERS.md`
   (`ve.acts` in layer 4, RunExamples a layer-4 fixture), `tools/relay_mutation_gate.py` (the reader),
   `tests/lean_service_corpus.py`, `tests/test_lean_service.py` (a schema seed), `tests/test_route_row_schemas.py`,
   `ve/assurance-manifest.json`, `lean/VE/Service/RegistryExamples.lean` and the recorded fixtures
   (`route-cases.jsonl`, `relay-gate-cases.jsonl`, `binding-answers.jsonl.gz`).

## Cost at the limits (DRI 2026-11-09, option A)

The builder's measurements, through `ve_service` on the VM, deadline lifted for the probe: `{0} to seekaa asylum` with 1, 32, 64 and 128 frames
took 0.06, 0.69, 2.80 and 13.4 s wall; L6 (P64, 64 readings) 0.18 s with V5's two frames and 322.8 s with 126 more;
L8 (the raw cap) 8.3 s with 126 more; a 400-byte one-act phrase with 128 frames reaches the step budget (`LIMIT`) in
12.8 s. The time is in `VE.Acts.readings` (ap-2's parse and meaning); the mode's own code reads no frame. The norms
decoder's `checkAct` (`Acts/Wire.lean` `joinedAct`) and `sourceCheck` call the same `readings`, so a norms document with
many frames and a joined act costs the same on main. Over its 5 s CPU deadline (`_CORE`) the relay raises
`CheckerUnavailable`: fail closed, never a verdict. The DRI signed option (A): spec 12's limits and the 5 s deadline
stay; its conditions are tests in `tests/test_acts_readings_lean.py`: (a) 32 frames, 64 readings with V5's two frames
and the 400-byte phrase with one frame, within the deadline; (b) 129 frames refused by D-31 before any parse
(`test_the_document_caps_on_fixed_phrases_and_frames_are_limits`, 1.37 s for its whole file selection); (c) P64 with 126
frames more answered `CheckerUnavailable` naming `act-readings`, then the next request answered
(`test_a_request_over_the_cpu_deadline_is_unavailable_and_the_service_recovers`, 5.95 s); (d) these figures. The parser
row `ap-parse-index` (rules indexed by their first terminal, so `stepBudget` bounds CPU) is the DRI's (item 2).

## Seeded bugs

`python3 docs/act-phrases/ap-4/seed_bugs.py` plants each bug, runs its check, restores the file; results in
[mutants.json](mutants.json): **40 plants, 40 KILLED, `restored_build_returncode` 0** (the review fix's sweep at
`165926532`, with `rowsOf-one-tag`, `tagged-content-as-function` rerun after their guards and `py-block-any-json`,
`py-cli-oserror` after `ed40ac9a6`). The rows below name each plant; [mutants.json](mutants.json) has each one's
failing `#guard`, theorem or test. At least one per new trusted definition and per claimed behaviour, in each language changed.

| Plant | Language, file | Definition | Killed by |
|---|---|---|---|
| e1x-all-dropped (the plan's) | Lean, `lean/VE/Acts/Grammar.lean` | `globalRules` | `ReadingsExamples.lean:213` (S4, rs_u055 refused) and 12 more |
| actJson-no-from, actJson-text-is-act, actJson-act-not-plain | Lean, `lean/VE/Acts/Run.lean` | `actJson` | RunExamples:45 (AR1) and the `from` guards |
| readingJson-first-act, readingJson-untagged (F4) | Lean, Run.lean | `readingJson` | RunExamples:45 and the `from` guards |
| rowsOf-paraphrase-what, rowsOf-one-tag (F4) | Lean, Run.lean | `rowsOf` | D-32's "this act phrase"; A5's second-meaning guard |
| witnessed-no-limit, firstsBy-keeps-equal (F2) | Lean, Run.lean | `witnessed`, `firstsBy` | `witnessed_readings`, `firstsBy_map` (Run.lean) |
| tagTree-tags-function-words, placeOf-no-word, tagged-content-as-function (F4) | Lean, Run.lean | `tagTree`, `placeOf`, `tagged` | the `from` and `fnsOf` guards |
| toks-or-for-and, toks-no-to (F4) | Lean, Run.lean | `Act.toks`, `Simple.toks` | the token-text and `from` guards |
| listReadings-no-byte-limit, -no-tokens, -none-listed | Lean, Run.lean | `listReadings` | RunExamples:87; 45; 40 |
| listReadings-bogus-verdict | Lean, Run.lean | `listReadings` | `ResponseShape/Encoders/ActReadings.lean:43` (`listReadings_fits`) |
| listed-sign-ignored, listed-no-frames | Lean, Run.lean | `listed` | RunExamples:32-38, 101; 32-45, 80, 108 |
| runActReadings-refusal-listed | Lean, Run.lean | `runActReadings` | RunExamples:40, 87-104 |
| verdictOf-no-limit | Lean, Run.lean | `verdictOf` | RunExamples:87, 92, 96 |
| spans-no-fold, spans-one-space | Lean, Run.lean | `spans` | RunExamples:50; 57 |
| fromOf-any-anchor, fromOf-reuse, fromOf-any-token (F4) | Lean, Run.lean | `fromOf` | AR1 (P11's *or*); the `from` guards; the `fromOf` unit guards |
| sameTok-case | Lean, Run.lean | `sameTok` | the `fromOf` unit guard |
| registry-name | Lean, `lean/VE/Service/Registry.lean` | `Mode.name` | `RegistryExamples.lean:6` |
| py-range-check-dropped (the plan's) | Python, `ve/acts.py` | `answer_problem` | `test_ar2_a_token_index_past_the_last_token_is_no_answer` and the fuzz (A11, A12, A9) |
| py-span-bound-dropped, py-equal-readings, py-index-twice | Python, `ve/acts.py` | `answer_problem` | `test_ar3_…`, `test_ar4_…`, `test_an_index_twice_in_one_act_…` |
| py-no-schema | Python, `ve/acts.py` | `read_answer` | the fuzz (A11, A12, A9) |
| py-verdict-binding | Python, `ve/acts.py` | `answer_problem` | `test_a_listing_needs_readings_and_a_refusal_has_no_tokens` |
| py-act-twice-refused (F1) | Python, `ve/acts.py` | `answer_problem` | `test_e16_one_act_written_twice_is_bound` |
| py-coerced, py-block-any-json, py-cli-oserror (F3) | Python, `ve/acts.py` | `_as_sent`, `read_block`, `main` | `test_the_request_coerces_no_member`, `test_a_malformed_acts_file_…`, `test_an_unreadable_invalid_or_oversized_acts_file_…` |

No Rust product code changed.

## Trust

`uv run python tools/trust_map.py --check` on the final code: "against da5303b78769: K +0, S +0, D +160, G +95, tied
+18, unclassified +0, trusted +63": `lean/VE/Acts/Run.lean` +60, `Registry.lean`, `Protocol.lean`,
`ResponseShape/Schemas.lean` +1 each; "PASS: K, S and untied [V] within da5303b78769 and the allowances introduced
since" after `trust_map.py --allow` twice (+57 for the build, +6 for the review fix; SIGNED by standing ruling R16,
ap-4: +63 of its 150). The review fix's declarations: `witnessed` (G[V]) and `firstsBy` (D[V]) tied by
`witnessed_readings` and `firstsBy_map`; `tagTree`, `placeOf`, `Act.toks`, `Simple.toks`, `tagged`, `tagBase` D[I]
(`from` is provenance); RunExamples' `Vsf`, `fromsAt`, `fnsOf` T. The new declarations are classified in
`tools/trust-classes.json` (G[V] `listReadings`, `listed`, `runActReadings`; D[V] `actJson`, `readingJson`, `rowsOf`;
D[I] `spans`, `fromOf`; G[I] `sameTok`; D[R] `verdictOf`, `refusedRow`, `decodeRequest`; G[R] `actReadingsReported`,
the schema's and skeleton's; T the fixtures). FOLLOW-UPS.md "## ap-4" asks for the ties pass.

Trust mutants (checklist 13a, `mac-pytest.sh --trustmut -- --max-mutants 1000 --json …`, ve-cloud-2), the review
fix's run at `165926532` (Lean unchanged since): 8 definitions, 115 mutants, **82 KILLED, 0 SURVIVOR, 0 UNKNOWN, 12
INVALID, 21 ALLOWED, exit 0** ([trust-mutants.json](trust-mutants.json), a `--rescore` of the first run, whose 14
UNKNOWN were ill-typed list cuts of `readingJson` and `rowsOf`, now allowed with that reason). The build's run at
`4966e82e7`: 64 KILLED, 0 SURVIVOR, 0 UNKNOWN, 4 INVALID, 7 ALLOWED, exit 0, 163 s (`--rescore` of the first run, whose only survivor was `listed`'s
`allowByDefault` flag, which `opOf` does not read; its six UNKNOWN were ill-typed cuts). The reasons are in
[trust-mutants-allow.json](trust-mutants-allow.json).

## Tests

- While iterating: `lake build` of the edited modules; the two new files and their `-k` selections;
  `tests/test_route_row_schemas.py` once after adding the route cases ("32 passed in 577.03s").
- `cd lean && lake build`: "Build completed successfully (1331 jobs)"; `python3 lean/audit.py`: "PASS: 795 source
  files; 8779 named theorem declarations audited".
- `uv run python tools/regen_generated.py --write`: "wrote 37 entries" (the first run stopped at `import-contract`:
  `ve.acts` unmapped, fixed in `tools/layer_policy.py`).
- `uv run python tools/lean_statements.py`: "removed: 0, changed: 0" (no approved statement changed).
- Selected tests (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`): the selector picks 555 of
  555 units, because every service test reads `lean/checkers.lock` and `envelope.json`, which a new mode changes
  (`select_tests.py --explain`). First run (ve-cloud-2) stopped at `check_lean_imports.py` ("new outward Lean import:
  VE.Acts.RunExamples -> VE.Acts.Run"): fixed by listing RunExamples with the layer-4 runner fixtures. Second run
  (ve-cloud-3, 6082 s): "recorded 161 units …; 4 failed", then `--maxfail 5` left 394 units unrun. The four:
  `test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified` (RunExamples' `other_json` reason),
  `test_nested_pytest.py::test_every_pytest_command_is_built_by_the_builder` (`seed_bugs.py` now builds its pytest
  command with `nested_pytest`), `test_relay_mutation_gate.py::test_every_route_has_fixtures` and
  `::test_the_gate_passes_on_every_route[service:act-readings]` (the route's fixtures and its reader
  `ve.acts.read_answer`), `test_shape_binding_mutants.py::…[act-readings]` (the five answers recorded with
  `binding_census.py --answers`, keeping every other mode's committed answers; census rewritten). Then the five ids
  and the 393 unrun test files on ve-mac-1: "1 failed, 11044 passed, 7 skipped, 83 xfailed" in 645 s, the failure
  `test_lean_service.py::test_random_malformed_responses_never_escape_schema` (no `_SCHEMA_SEEDS` row for the mode;
  added, all 11 mutations run for it directly), rerun on ve-mac-1: "1 passed", exit 0. The unrun
  `tools/test_layer_policy.py` failed locally on the undocumented layer of `ve.acts` (`docs/ARCHITECTURE-LAYERS.md`
  row 4 now lists it): "Ran 49 tests … OK".
- `uv run python tools/gate_collection.py --check --prebuilt`: "32962 collected, 32928 at da5303b78…; 34 added, 0
  removed by a trailer, 0 refused, 0 stale and 0 malformed trailers". `regen_generated.py --check`: "checked 37
  entries", exit 0.
- Known red on main (`main-known-red.txt`): none of the failures above is listed; each was this branch's and is fixed.
- Review fix: `cd lean && lake build`: "Build completed successfully (1331 jobs)"; `python3 lean/audit.py`: "PASS: 795
  source files; 8781 named theorem declarations audited"; `regen_generated.py --write --only lean-statements --only
  lean-audit-manifests --only trust-tables --only assurance-manifest`, `--only checker-pins`; the two test files:
  "91 passed". Selected tests (`mac-pytest.sh --select`, ve-cloud-2, 7371 s, 555 units): "2 failed", both this fix's:
  `test_relay_mutation_gate.py::test_the_gate_passes_on_every_route[service:act-readings]` (the duplicated-act mutant,
  by design after F1: allow entry AP4-F1) and `test_relay_lint.py::test_every_relayed_module_exists_and_passes`
  (`ve/acts.py` imported `ve.__main__`, which made the CLI and its imports relay helpers; now read as `ve calc`
  reads). Rerun of those two with the two act-readings files: "204 passed"; `relay_lint.py`: "PASS: 21 relayed
  module(s)". `trust_map.py --check`: PASS (above).
- Not run: the full release gate (the chain runs it on the final HEAD); Rust tests (no Rust change).

## Pilot bytes

0 from this item by itself (an estimate; nothing is claimed before a pilot audit). M1's u092 (163 B) and M2 (u055
checked exact) need the admission hook, now ap-4c; u076's 125 B also waits for the readings elaboration (spec F11).

## Size

Hand-written lines against the merge base (`git diff --numstat`, added plus removed, generated files and recorded
evidence JSON excluded): product 409 (Lean 278: `Acts/Run.lean` 135, encoder 83, schema 46, registration 14; Python
112: `ve/acts.py` 106, CLI 4, deadline 2; tools 19: relay lint 5, layer map 6 and its doc 2, relay-gate reader 13,
manifest 1, less shared lines); tests and guards 510 (RunExamples 111, RegistryExamples 7, the two test files 188 and
184, route and relay-gate cases 10, corpus, seed and row-schema lines 10); evidence 199 (`seed_bugs.py` 143, allow
file 7, trust classes 49); DELTA and this report 235. 1,361 in all. The DRI's item 3 counts product code against the
~600 line (tests and guards exempt, the qt-a4 / jt-3b precedent); by the common rule's count (everything) the item is
over it, and the cut taken is the one the DRI named (deliverables 5 and 8 to ap-4c).
The review fix adds, against `0af902d7f` (added plus removed): product 328 (`Acts/Run.lean` 217, encoder 30,
`ve/acts.py` 81), tests and guards 275 (RunExamples 61, the two test files 92 and 122), evidence and allow entries
(seed plants, trust classes, gate and trust-mutant allow files). Product code against the merge base is now about
610 (Lean 427: `Acts/Run.lean` 282, encoder 85, schema 46, registration 14; Python 164; tools 19), at the DRI's
~600 line; the growth is the review's required F2 and F4 fixes (the derivation-read `from` with its proof).

## Next items

- `FOLLOW-UP: ap-4c sources at readings admission with spec 3.3 identity` (DRI 2026-11-08 items 3 (b) and 6:
  `sources` decoded and checked once per source by `sourceCheck`, fail closed on every other path, in the identity; the
  S-fixtures through admission; the O5 row with its u105 condition; deliverable 8).
- me-4b, ap-5, ap-6 (behind ap-4c where they read reading sets).

## Spec re-read

- The request and row against act-phrases.md 7 ("The `act-readings` mode", lines 1412-1430 at `b5c1e805b`): members,
  verdicts, `tokens` as UTF-8 spans, `from` in the act's order; binding's four bullets; "What binding cannot show".
- AR1-AR5 against 11.4 (lines 1801-1810); P5-P12, P64, P65 against 11.4 (1765-1776); D-17, D-22, D-32 against 10.
- Limits against 12 and DRI item 1; DELTA rows against the DRI's quoted Ruling cells (items 1 and 2's R16 text).
- Plan AP-4 Tests and Seeded bugs (lines 994-1006) against the fixtures and plants above.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: PASS, `test_every_mutant_is_no_answer_or_lean_content_binding_cannot_see`
   (840-1573 one-fault mutants per answer, retyped to 7, true, null, [], {}, "x", -1, 999), `test_route_row_schemas.py`
   over the five route cases; malformed requests are Lean's case errors, raised by `relay.decide`.
2. Every deliverable built or moved by a ruling: PASS, the table above; (5), (8) and the O5 row moved by DRI items 3 (b)
   and 6; no Python copy of a Lean decision (the 64 bound is the schema's); overlap check at the start: no in-flight
   branch touches these files (ci-5 touches `Acts/Lexical.lean`, not changed here).
3. Tests can fail: PASS, mutants.json (40 of 40) and trust-mutants.json (0 survivors, exit 0).
4. Python, Lean and Rust agree; valid inputs pass: PASS for valid inputs (every genuine answer bound:
   `test_every_genuine_answer_is_bound` over the pilot, the `from` fixtures and the edges, after review F1;
   `test_ar1_genuine_answer_is_bound_and_shown`, `test_a_refusal_and_a_limit_are_bound…`); N.A. for Rust (unchanged).
5. R8 binding: PASS, AR2-AR4, `test_an_index_twice_in_one_act_and_spans_out_of_order_are_no_answer`,
   `test_an_answer_to_another_case_is_no_answer`, `test_a_listing_needs_readings_and_a_refusal_has_no_tokens`; AR5
   accepted by `test_ar5_a_reading_dropped_with_its_row_is_bound` (no claim beyond it).
6. Gate evidence: PASS for the saved evidence (base from `git merge-base`); the full gate is the chain's.
7. No unsigned item: PASS, DELTA rows cite DRI item 1 and R16; nothing reserved.
8. Every user-visible change in DELTA: PASS, the mode and CLI (row 1), trust (row 2); `sources` unchanged (refused).
9. Test selection: PASS, the selector picks every unit for a stated cause (a new mode changes `checkers.lock` and
   `envelope.json`, read by every service test: `select_tests.py --explain`), and the run included both new files;
   seeded bugs fail named tests in that selection (mutants.json).
10. Lean statements: PASS, `runActReadings_fits` is about `runActReadings`'s own result; plant
    `listReadings-bogus-verdict` breaks it; `lean_statements.py`: 0 changed.
11. Budgets fail closed: PASS, every limit is `LIMIT` with Lean's text before the work (`test_the_act_phrase_limit_is_400_bytes`,
    `test_the_document_caps_…`, `test_a_saturated_raw_cap_is_a_limit`); over the CPU deadline the relay raises
    `CheckerUnavailable` (never a verdict): `test_a_request_over_the_cpu_deadline_is_unavailable_and_the_service_recovers`
    (DRI 2026-11-09 item 1).
12. No CPU regression: PASS for existing paths (no existing route changed); the new mode's cost grows with the frames
    (measured above), bounded by its deadline under DRI 2026-11-09 item 1, with the parser row `ap-parse-index`.
13. Removed tests: N.A., none removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS, 400/401, 300/301, 128/129, 64/128 readings, LISTED and
    refused rows bound and their mutants refused; spec re-read above.
15. No overclaim: PASS (each claim names its test); no silent cut (the cut is the DRI's item 3 (b), asked before it was
    taken, at 20:52Z and 21:12Z); every new check can fail (mutants.json); limits charged before work (above).
