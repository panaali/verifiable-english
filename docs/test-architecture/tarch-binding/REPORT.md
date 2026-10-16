# Test architecture rank 10, first step: binding from the Lean shapes (tarch-binding)

**DRI signature needed: none for a user-visible delta (there is none, below). One file-ownership note:** the batch
was to add new files only. It edits one existing hand-written file, `tools/regen_generated.py` (one `GENERATED`
entry, 3 lines), and the generated `.gitattributes` follows it. The repository requires this:
`tests/test_regen_generated.py::test_every_script_with_a_writing_mode_is_registered_or_excluded_with_a_reason`
fails for an unregistered writer, and CLAUDE.md names that file as the one inventory of generated files.
Nothing else outside new files changed: no route module, `ve/backends/service_schema.py`, `lean/ResponseShape/` or
`tools/relay_mutation_gate.py`.

Plan: `manage-agents/reviews/test-architecture-2026-10-14.md` draft 2, rank 10, section 3.9, with Astra's
re-check (point 11 resolved; nothing there overrides 3.9) and ADR 0001. Base `dae12d5ff`, synced with main
`c53117326` (merge `c19cda70f`). Saved evidence: `evidence.json` (commit list, numbers), `seeded-faults.json`,
`mutants.json`.

## What was delivered

| Plan or directive line | Delivery | Commit | Check |
|---|---|---|---|
| 3.9 "Finish ADR 0001's census"; directive (1): every string and integer leaf of every response shape, how it is bound today (hand check, file:line) or "unbound"; generated, with a `--check` | `tools/binding_census.py` renders `docs/test-architecture/binding-census.json` and `.md` from the Lean-rendered shapes, the recorded answers and a probe of the hand path. Registered in `tools/regen_generated.py` (`binding-census`). | `2c3c219eb`, `fc4a36bb5`, `f32633959` | `test_the_census_is_current`, `test_a_stale_census_fails_the_check`, `test_the_census_covers_every_mode_and_every_leaf` |
| Directive (1): rd-9's 47-field audit as a cross-check | `docs/test-architecture/rd9-binding-rows.json` transcribes the 47 fields with their census paths. The census places each one (`rd9` section). | `2c3c219eb` | `test_rd9s_47_fields_are_each_placed` |
| 3.9 "one generic checker per mode"; directive (2) | `ve/backends/shape_binding.py`: `check(mode, case, row)` is the shape check (`service_schema.check_row`, the one validator) plus the classification of every leaf of the answer. `leaves(mode)` is the static census. Nothing is re-validated or re-derived. | `829a0c293` | the mutation test below |
| 3.9 "one generic mutation test per mode on recorded genuine answers"; directive (2): each leaf mutated, coordinated multi-field mutants included | `tests/data/binding-answers.jsonl.gz` (537 genuine answers, all 36 modes). `tests/binding_mutants.py` mutates each leaf, array and map, and coordinated pairs. `tests/test_shape_binding_mutants.py` runs one test per mode. | `829a0c293`, `fc4a36bb5`, `2ee24ed6d`, `f32633959` | `test_the_generic_checker_gives_every_mutant_the_verdict_its_shape_decides[<mode>]` (36), `test_coordinated_mutants_are_generated_and_decided`, `test_a_name_renamed_everywhere_is_refused_where_one_occurrence_is_bound`, `test_every_leaf_of_an_answer_is_a_leaf_of_the_census[<mode>]`, `test_the_walker_classifies_every_dialect_keyword` |
| 3.9 "a hand fuzz path is retired only after a seeded fault at that boundary is caught by the generic test"; directive (3): per hand binder, whether a seeded fault is caught (render, readings, document check, coordinated mutants); list both | The probe (`tests/binding_probe.py`) delivers every shape-generated mutant to the real consumer code in a fork of each consumer test. It records the hand check that refused it and the generic verdict: 51 hand binders, 12 covered, 39 not. `seeded_faults.py` disables five binders and judges them end to end on the wire. | `2c3c219eb`, `f54ba98d9` | `test_the_probe_finds_the_hand_check_of_a_consumer_test` (live), `test_a_refusal_is_attributed_to_the_check_that_made_it`, `test_a_hand_check_is_retirable_only_if_the_generic_checker_refuses_all_it_refuses`; `seeded-faults.json` |
| "Retire NOTHING" | Nothing is retired. Every hand binder, every consumer test (`tests/test_discourse_answer.py:139` included) and the relay mutation gate are unchanged. No test was removed. | – | `git diff main...HEAD` touches no test or product file except new ones and the inventory entry |
| "Measure the effect (before/after on the Mac)" | Below. | – | `evidence.json` `measurements` |

## 1. The census

Totals, from `binding-census.json` at the final commit:

- 36 modes and 1,626 leaves outside tagged grammars (string, integer, map key, and `any` for a binding keyword
  on an untyped node). Grammar-internal leaves are listed once per grammar in `grammars`.
- By ADR 0001 class: 239 bound, 231 closed domain, 1,156 none. `pattern`, `minLength` and `maxLength` put no
  leaf in a class (ADR 0001).
- How each leaf is bound today:
  - **shape**: 470, the bound and closed leaves;
  - **hand**: 202. A hand check refused a mutant of the leaf that the generic checker accepts. The census names
    the check (file, function, the raising line's text and its line at the probe's commit);
  - **unbound**: 137. Every probed mutant passed both the shape and the hand path;
  - **later Lean request**: 59. The only refusal came from a later request that sent the mutant back to Lean
    (rd-9's "caught by accident");
  - **not probed**: 758. No consumer test reached that branch. These are mostly `readings-route`'s 382 branch
    leaves and each mode's rejection rows, whose `error` and `path` `relay._raised` relays verbatim.

Line numbers are not stored as identities. A hand check is identified by its file, function and line text, so an
edit elsewhere in a route module leaves the census valid; `--show` prints the current lines.
`--check` regenerates the census and compares it. If a binder's line text changes, the census marks it
`present: false` (re-probe) instead of failing.

**rd-9's 47 fields.**
- 43 are placed in the census and unbound by the shapes today. That agrees with rd-9's "No" or "Partly".
- Field 20 (`lines[].instance`) is now a closed domain. rd-9 found it unbound; the shape has since gained an
  `enum`.
- Fields 21 and 22 (`node.sign`, `node.hard`) are booleans, outside the census.
- Field 5 (`decisions[].key`) no longer exists in the shape.
- How the 43 are handled today:
  - one is carried by a hand check (field 27, `generated[].name`, by `ve/rights.py:__init__`);
  - 17 are refused only through a later Lean request;
  - 8 are unbound after probing;
  - 17 were not reached by a probed test (the `soft-pairs` and `soft-conflict` kinds have no product caller,
    as rd-9 says).

## 2. The generic checker and its mutation test

On the 537 recorded answers, the shapes generate 14,184 mutants:
- 4,401 are predicted refused and 9,054 accepted, and the checker gives every one of these 13,455 the
  predicted verdict;
- the other 729 are "either": the shapes alone do not decide them. Examples are another member of a closed
  domain, or a reordered list whose positions `x-zip` binds element by element.

| mode | answers | mutants | predicted refuse | predicted accept | either |
|---|---:|---:|---:|---:|---:|
| route | 37 | 331 | 268 | 31 | 32 |
| norms | 49 | 385 | 217 | 128 | 40 |
| discourse | 19 | 333 | 121 | 208 | 4 |
| rights | 26 | 894 | 295 | 551 | 48 |
| readings-route | 52 | 3,093 | 507 | 2,520 | 66 |
| alternatives | 24 | 2,635 | 811 | 1,666 | 158 |
| other 30 modes | 330 | 6,513 | 2,182 | 3,950 | 381 |

The full table is in `evidence.json`.

Coordinated mutants are decided both ways:
- `rename` (one request name changed everywhere): 309 refused, 455 accepted;
- an array moved together with its counter: 13 refused, 121 accepted;
- `replace` (the SOME-to-ALL form): 10 refused, 354 accepted.

The accepted coordinated mutants are exactly where internal agreement is the only binding: a hand binder, or
nothing, stands between them and the consumer.

**Main moved during the batch.** It brought three dialect keywords that bind fields of the answer to each other
(`x-equal-fields`, `x-same-length`, `x-unique-strings`), and the mutation test caught the walker's ignorance of
them at once. They are classified as internal agreements: a leaf under them stays of class none, since it binds
nothing to the request. `test_the_walker_classifies_every_dialect_keyword` now fails on any keyword that
`service_schema` reads and the walker does not classify.

## 3. Hand binders: is a seeded fault at each boundary caught by the generic test?

The probe ran over the 46 consumer test files in `PROBE_TESTS`:
- 10,204 mutants, each delivered after the shape check;
- 3,158 hand refusals, attributed to 51 hand checks.

A seeded fault that disables check H lets through exactly the mutants H refused. Where the generic checker
refuses all of them, the fault is caught before any consumer (render, readings, document check, coordinated
mutants alike). Where it accepts some, the fault reaches the consumer.

- **Covered at every probed field (could be retired later): 12.**
  - `ve/admission.py:lean`, `ve/ast.py:decode`, `ve/backends/english_lean.py:_transport`, `:check` and
    `:read_question`, `ve/backends/speech_source.py:decide_source`, `ve/bundle.py:_leaf_choices`,
    `ve/readings.py:_check_readings_lean`, `ve/readings_route.py:_completion_elaborate`,
    `ve/readings_verdicts.py:conflict`, `ve/reports.py:_load_statuses`, `ve/wire.py:validate_json`.
  - Why "later" and not now:
    - the evidence covers only the probed mutants and fields;
    - most of these checks also guard the case where the service is not the producer (a one-shot or replayed
      row);
    - a retirement still needs its own seeded fault at the same boundary, per route.
- **Not covered (not retirable on this evidence): 39.** These carry bindings the shapes do not state, among them:
  - `ve/discourse.py:_bind_joint`: joint choices (SOME-to-ALL) and the joint formula;
  - `ve/discourse.py:lean_admission`, `:_bind_references`, `:_keys`;
  - `ve/document.py:require`, `:_lean_document`;
  - `ve/norms.py:_lean_regenerated`, `:_bound_targets`, `:_norm_certificate_lean`;
  - `ve/readings_route.py:_need` (178 mutants only it refuses) and `:elaborate`;
  - `ve/ask.py:read_answer`, `ve/words.py:read_answer`, `ve/reports.py:__init__`, `ve/rights.py:__init__`;
  - `ve/norm_defaults.py:__init__`, `ve/parser.py:_parse_lean`, `ve/argument.py:_check_argument_lean`;
  - `ve/admission.py:bound_admission`, which recomputes the report identity (an ADR 0001 debt, AR-11).
  - The table is `binding-census.md`, "Hand binders".

**Seeded faults, run end to end** (`seeded_faults.py`, `seeded-faults.json`). Each binder's check was disabled by a
temporary edit, and its mutants were delivered again before the shape check (`--wire`):

| hand check | census | consumer tests failing with the fault | its mutants on the wire, fault in place |
|---|---|---|---|
| `ve/discourse.py:_bind_joint` | not covered | 4, including `test_discourse_answer.py::test_duplicate_and_out_of_range_choices_are_no_answer` (the SOME-to-ALL regression) | 5 reach the consumer: 4 shown wrong, 1 `IndexError`; 2 refused by the shape |
| `ve/rights.py:__init__` (line binding) | not covered | **none** | 6 accepted silently; 4 refused by the shape; the rest refused by the other checks of `__init__` or by a later Lean request |
| `ve/admission.py:bound_admission` | not covered | **none** | 3 reach the consumer; 32 refused by the shape; 50 not reached by these three test files |
| `ve/reports.py:_load_statuses` | covered | none | all 3 refused by the shape |
| `ve/backends/english_lean.py:check` | covered | none | its 1 refused by the shape |

So the plan's rule decides as follows:
- `tests/test_discourse_answer.py` and the discourse binders stay. The generic test cannot catch a fault in
  `_bind_joint`, because the shapes do not bind joint choices to the request.
- The two binders the census marks covered are retirable later, by the rule's own test.

**Per hand fuzz path:**

| hand fuzz path | retirable later? | why |
|---|---|---|
| `tests/test_discourse_answer.py`, the discourse binders | no | joint choices, references and statuses are bound only by hand |
| `tests/test_words.py` (answer mutants), `ve/words.py:read_answer` | no | 4 probed mutants only it refuses |
| `tests/test_ask_relay.py`, `ve/ask.py:read_answer` | no | 92 only it refuses |
| `ve/rights.py:__init__`, `ve/admission.py:bound_admission` | no | they carry bindings, and no test fails when the line-binding check is removed (finding F1) |
| `ve/reports.py:_load_statuses`, `ve/backends/english_lean.py:check` and the other 10 covered checks | yes, later | every probed mutant is refused by the shape; no hand test of theirs exists to retire |
| `tools/relay_mutation_gate.py`, `tests/test_route_row_schemas.py` | n/a | generic transport and schema gates, not hand paths; untouched |

## 4. Findings for follow-up (all pre-existing; none introduced here)

- **F1. Untested hand checks.** No test fails when these two checks are disabled, yet each carries bindings the
  shapes lack:
  - `ve/rights.py:199` ("rights line binding");
  - `ve/admission.py:275`.
  - The probe shows mutants they alone refuse (`seeded-faults.json`).
- **F2. A shape-valid answer crashes Python.** A `norm-defaults` answer that the generic checker accepts raises
  `KeyError` at `ve/norm_defaults.py:262` (`audit_completions`) and at `ve/filling_search.py:56`
  (`binding-probes.jsonl.gz`, test `tests/test_norm_defaults.py`). BUILDER-CHECKLIST 1 says only `VEError` may
  escape.
- **F3. Corrupted Lean formulas misread as input errors.** Shape-valid mutants of Lean-generated formulas (a
  `route` or `norms` Background premise with a renamed predicate or a shifted variable) surface as the user's
  `UnknownSymbol`, `UnboundVariable` or `TypeMismatch` from `ve/ast.py:term`/`formula` (about 80 probes). They
  should be `CheckerUnavailable`. The relay mutation gate calls this class "misread".
- **F4. The selector picks everything for this batch.** Registering the census changes `.gitattributes`, which
  `tools/select_tests.py` treats as a whole-suite root. That is the plan's cause C, owned by tarch-select (rank 4);
  this batch does not edit the selector.
- **F5. The rd-9 inventory doc is stale.** rd-9 notes that `docs/spec/rd-9-relay-binding.md` is out of date, and
  the census now gives the current picture.

## 5. Measurements

On the Mac:
- **Before:** the two new test files do not exist on main (0 tests, 0 s).
- **After:** on `ve-mac-1` (aarch64), `mac-pytest -n 6`, commit `f32633959`:
  - `tests/test_shape_binding_mutants.py`: 37 tests, 23.3 s of test time;
  - `tests/test_binding_census.py`: 9 tests, 2.7 s, the live probe test included (1.1 s).
- **For comparison**, the same run's `tests/test_discourse_answer.py` took 99.6 s for 16 tests. That is the
  kind of hand fuzz path a later batch might retire, though not this one, by section 3.
- Three files at 6 workers: 52.8 s wall. All passed, including the fork-based probe test on macOS.

Measured on the VM, outside any gate:
- `--write` or `--check` takes 2–3 s.
- The probe recording (`--record`, a manual step like `relay_mutation_gate.py --record`) took 23.4, 44.3 and
  11.6 min for its three groups at 12 workers, at a load of 58–89 on 32 cores.
- The five seeded faults took 42 min.

What this adds to a gate is about 26 s of test time. The probe is never part of a gate.

## 6. The plan's rules

- **R2 and R3 stay complete, live and without reuse.**
  - The new tests are ordinary tests in the gate's collection.
  - The recorded answers are an *added* input to an added test. They replace no live check: the relay mutation
    gate still asks the current build for its answers, and every consumer test still runs live.
  - The census is a generated file checked by its own `--check`.
  - Nothing lets a merge or a nightly depend on selection, a store, a cache or reuse.
- **Nothing weakens what is checked.** No test, check, allow-list or hand path was removed or changed.
- **No timing-threshold test.**
  - The probe's per-child limit (600 s, a measurement tool's limit) is never asserted on.
  - The live probe test waits for its nested run without a timeout; its child processes are bounded by the
    probe's limit.
- **D1 and R8.**
  - The generic checker re-derives nothing. Classification reads the Lean-rendered shapes, and branch choice uses
    `service_schema`'s compiled validators.
  - Internal agreements are kept apart from relations to the request: a leaf under them stays class none.
- **D4.** Batch numbers are saved in `evidence.json`. No new test pins them. A census-content test written during
  the batch was removed before handoff for this reason.

## 7. DELTA

No user-visible delta:
- no `ve` command's output, code, text, path, verdict or availability changes;
- `ve/backends/shape_binding.py` is new, and no product path calls it.

No standing ruling applies.

## 8. Limitations

- **The probe samples.** It covers the first two calls and each new answer shape per (mode, calling function),
  one mutant per (path, kind), on the 46 `PROBE_TESTS` files. "Not probed" and "unbound" are statements about
  that sample.
- **Children share the parent's files.** A fork shares the parent's `tmp_path`. So
  `test_rights.py::test_document_loader_relays_lean_rights_rejections_verbatim` failed in the probe run (a child
  had made the directory the parent then made). It passes alone, and the census counts such outcomes as
  inconclusive (`FileExistsError`, 334 probes).
- **Attribution names the innermost deciding `ve` line.** That is the exception a binder converted, or the first
  frame that is not an error-building helper. A refusal by a later Lean request is never attributed to a binder.
- **A cost for other branches.** A branch that changes a response shape must regenerate the census as well as
  the schemas. `tools/regen_generated.py --write` does both: `binding-census` follows `response-schemas` in the
  inventory, and the write takes 2–3 s. The merge train regenerates only on a conflict. So a branch that merges a
  shape change without syncing fails `test_the_census_is_current` in its candidate verify, before main moves, and
  needs one `--write`. An edit to a hand binder's cited line needs the same `--write` (the line is marked
  `present: false`), never a re-probe.
- **Probes before the merge.** The probes were recorded before the sync with main. Paths of the recursive
  `kind` and `q_term` shapes, and main's new `search-budget` mode, have no probe yet (`--record` refreshes them).
  The answers were refreshed on the merged build (`--answers`).

## 9. Seeded bugs (Python is the only product language changed)

All eight are recorded in `mutants.json`; each was planted, its test run, and the file restored.

| id | file | behaviour | failing test |
|---|---|---|---|
| B1 | `ve/backends/shape_binding.py` | `x-claim-nodes` binds the claims it names | `test_the_generic_checker_gives_every_mutant_the_verdict_its_shape_decides[route]` |
| B2 | `ve/backends/shape_binding.py` | a relation keyword on a list binds every leaf below it | `…[environment]` |
| B3 | `ve/backends/shape_binding.py` | a recursive shape takes its first entry's pattern | `test_every_leaf_of_an_answer_is_a_leaf_of_the_census[norms]` |
| B4 | `tests/binding_mutants.py` | a rename is refused where one occurrence is bound | `test_a_name_renamed_everywhere_is_refused_where_one_occurrence_is_bound` |
| B5 | `tools/binding_census.py` | a converted later-request rejection is the transport's | `test_a_refusal_is_attributed_to_the_check_that_made_it` |
| B6 | `tools/binding_census.py` | retirable only if the generic checker refuses everything the check refuses | `test_a_hand_check_is_retirable_only_if_…` |
| B7 | `tools/binding_census.py` | the census lists integer leaves | `test_the_census_is_current` |
| B8 | `tests/binding_probe.py` | the probe records the refusing hand check | `test_the_probe_finds_the_hand_check_of_a_consumer_test` |

Two seeds needed a second run:
- B4 first survived. The prediction was only weakened to "either", which nothing asserted, so the rename test was
  added.
- B7 was first run against the coverage test, which reads the committed file; `--check` catches it.

## 10. Tests run

- **Selected tests.** Because of `.gitattributes` the selection is all 403 units (F4). On the Mac, 56 units
  finished, all exit 0, before my one-hour command limit.
- **The affected set** passed on the VM: 1,000 tests in 36:47, after the sync. It covered the new tests,
  `test_regen_generated`, `test_architecture_docs`, `test_response_schemas`, `test_service_schema_compiler`,
  `test_route_row_schemas`, `test_lean_service_schema`, `test_repo_map`, `test_select_tests`,
  `test_gate_collection`, `test_nested_pytest`, `test_relay_mutation_gate`, `test_inventory_lint`,
  `test_single_owner`, `test_relay_lint`, `test_words`, `test_discourse_answer` and `test_hang_guards`.
- **Layer checks:** `tools/check_python_layers.py` (contracts kept) and `tools/test_layer_policy.py` (kept).
- **Known red on main** (`main-known-red.txt`): the two sub-tick deadline tests and rd8. None was touched.
- **Relay mutation gate** (`tools/relay_mutation_gate.py`, which the pre-review gate runs because `ve/` changed): 43
  routes, 117,799 mutants, 15 failures, all from main's state at `c53117326`, not this branch.
  - 14 are allow-list entries that now match nothing. Main's route Background is bound by `x-equal-fields`, and
    its `parse` AST paths changed (`B0`, `F3`, `F4`, `F7`, `F11`).
  - One is an accepted `norm-defaults` mutant (`unsaid/*/description` emptied).
  - The gate imports none of this batch's files. Its fixtures, allow-list and code are unchanged here
    (`git diff main...HEAD` is empty for all three), and no Lean file changed, so its result is main's.
  - Those files belong to their own items (the batch must not edit `tools/relay_mutation_gate.py`), so they are
    reported here, not edited.
- **The full gate** is not run here: the chain runs it on the final HEAD.

## Sibling lessons (tarch-b8 review)

- **Conflicts with main.** Synced at `c53117326`, with no conflict.
- **Fixture cost.** No fixture copies the repository. The recorded data is 118 KB of answers and 96 KB of probes,
  gzipped without a timestamp (`test_the_recorded_evidence_is_gzip_without_a_timestamp`). The census is 850 KB of
  JSON plus a 249 KB view, regenerated in 2–3 s.
- **No relay repair outside scope.** No relay or route file was edited.

## Self-review against BUILDER-CHECKLIST

1. **N.A.** No new relayed answer and no route reader changed. This batch's own fuzzing of genuine answers is
   `test_the_generic_checker_gives_every_mutant_the_verdict_its_shape_decides`.
2. **PASS.** The plan rows and directive lines are in "What was delivered", with their commits and tests. The rule
   breaks were grepped: no Python copy of a Lean decision (classification reads the shapes; branch choice is
   `service_schema`'s); no new permanent report test (one removed, section 6); one in-flight-shared file, the
   inventory entry, flagged in the first line.
3. **PASS.** `mutants.json`: B1–B8 each make a named test fail. The census comparator fails on a changed copy
   (`test_a_stale_census_fails_the_check`), and the mutation test fails on a wrong prediction in either direction.
4. **PASS.** Base and HEAD do not differ on any corpus, since no product path changed. Valid inputs still pass:
   every genuine answer passes (`test_the_generic_checker_gives_every_mutant_the_verdict_its_shape_decides`, line
   "a genuine answer is accepted").
5. **N.A.** No field is newly read from a Lean answer.
6. **PASS.** Synced with main first (`c53117326`). The evidence commit list is from `main..HEAD --no-merges`
   (`evidence.json`). The chain gates the final HEAD.
7. **PASS.** There is no DELTA row (section 7) and no trust-budget change. The one ownership note is in the first
   line.
8. **PASS.** No user-visible change: no `ve` output path was touched (`git diff main...HEAD -- ve/` shows only the
   new `ve/backends/shape_binding.py`, which no product code imports).
9. **PASS (with F4).** `tools/select_tests.py --base $(git merge-base HEAD main)` selects everything because
   `.gitattributes` is a whole-suite root. The cause is the selector's rule, owned by tarch-select. Seeding a change
   in `ve/backends/shape_binding.py` selects `tests/test_shape_binding_mutants.py`: it is in the plan.
10. **N.A.** No Lean statement or proof changed.
11. **PASS.** No deadline in a test. The probe's child limit belongs to a tool and is never asserted on
    (`tests/test_hang_guards.py` passed in the affected set).
12. **N.A.** No product path changed. The new tests add 26 s of test time on the Mac (section 5).
13. **PASS.** No test was removed or renamed relative to main. The one test removed was added on this branch and
    never reached main. `tools/gate_collection.py --check --prebuilt`: 16,044 collected, 84 added, 0 removed by a
    trailer, 0 refused, 0 stale, 0 malformed.
