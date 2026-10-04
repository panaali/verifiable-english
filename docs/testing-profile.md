# Test suite profile (2026-10-04, branch infra/testperf)

Where the default pytest suite spends its time, what was changed, and what to do next.
Machine: the shared 32-CPU VM, with other sessions' suites and builds running (the load
average is stated for each run; it ranged from 17 to 105 during the day). Every run used
prebuilt Lean and Rust binaries (`VE_NATIVE_PREBUILT=1`).

## Result

| | before (main f4142cb9) | after (HEAD of infra/testperf) |
|---|---|---|
| whole default suite, one run at `-n 8` | **47.9 min**, load 42-67 | **25.0 min**, load 47-72 |
| tests run by default | 8,641 passed, 6 skipped | 8,668 passed, 6 skipped, 3 nightly deselected |
| sum of test wall times | 14,461 s | 9,453 s |
| suite CPU (workers and every descendant) | 19,091 s | 9,885 s |
| nightly tests (`-m nightly -n 3`) | (part of the default run) | 3 passed in 14.6 min, load 48-60 |

The before run and the after run were made on the same machine, back to back in the same
afternoon: the before run with main's versions of the changed files checked out in this worktree;
the after run on HEAD. Earlier, the same baseline in three chunks took 47.5 min (load 50-80), and
HEAD before the last fix took 22.8 min (load 17-41). Wall time on this machine depends on the
load more than on the worker count (see worker counts below); suite CPU is the steadier measure,
and it halved.

The numbers in the tables come from `docs/testing-profile/before.json` and `after.json`, which
`tools/test_profile_report.py --json` wrote from the raw per-worker records (not committed).
`tests/test_testing_profile_doc.py` checks the tables and the Lean, Rust and service figures below
against the two JSON files; the raw records are not kept, so no test regenerates the JSON.

## Method

- `tools/pytest_profile.py` (load with `-p tools.pytest_profile`, set `VE_TEST_PROFILE_DIR`):
  per test, the wall time of setup, call and teardown, the worker's own CPU and its children's CPU;
  per child process started through `subprocess`, the executable, the test that started it, its
  lifetime and its own CPU (from `wait4`). It observes only.
- `tools/test_profile_report.py DIR`: slowest tests and files, child processes by executable, and
  each test's wall time split among the processes it started (a test whose children ran in
  parallel is scaled to its own wall time; the long-lived Lean service counts by CPU); the
  remainder is Python work in the test process.
- Start-up of each Lean executable measured directly (an empty batch, 10 runs each).
- `cProfile` on representative tests for the Python remainder.

## Where the time goes

Test wall time by category (seconds, one run at `-n 8`):

| category | before | after |
|---|---|---|
| Python in the test process | 8,825 (61%) | 6,361 (67%) |
| Lean routes and runners (one process per call) | 3,707 (26%) | 2,067 (22%) |
| child Python processes (nested pytest, CLIs) | 1,320 (9%) | 537 (6%) |
| other tools (pre-commit, fake checkers) | 221 | 187 |
| Rust checker | 200 | 159 |
| builds inside tests (lake, cargo) | 136 | 99 |
| Lean service (CPU) | 33 | 30 |
| git | 18 | 14 |

- **Lean start-up vs checking.** An empty batch takes 86-139 ms per route executable at load 76
  (55 ms at low load); the median call in the suite takes 80-120 ms, so most calls are start-up.
  After: 10,490 route calls, 2,834 s of process time, 2,435 CPU s; start-up is about 1,000 s
  (~11% of test time), checking the rest. Before, one test (the asimov-extended rerun) used
  8,070 CPU s of `ve_risk_route` alone (the per-test split of the raw records, which the JSON does
  not keep), 42% of the suite's CPU: each `risk-decision` case costs
  about as much as elaborating its policy (1.05 s per case on the base rules, 4.3 s on the
  extended ones, linear in the batch size), and the run decides 1,400+ cases.
- **One long-lived Lean process per worker.** The Lean service already is one: `ve.backends.lean_runner`
  keeps a lazy process-wide pool, so each xdist worker starts it once. The 289 service starts per
  run are tests that start their own service on purpose; they cost 37 CPU s in total. The route
  executables (`ve_risk_route`, `ve_discourse_route`, ...) have no service mode, so they cannot be
  kept alive without a Lean change; they all accept a JSON list of cases, so batching is the lever.
- **Rust.** 1,770 calls, 159 s, median 4 ms: process start-up is negligible.
- **Builds.** The session build is a no-op when outputs are current (lake 0.5 s, the whole session
  overhead ~2 s). Inside tests: one full release build in
  `test_rust_reproducible.py::test_a_copy_of_the_workspace_elsewhere_builds_the_same_binary`
  (51 s, the point of that test), and 17 `lake env lean --run VE/English/Run.lean` calls in
  `test_english_differential_merge_smoke` (37 s, an interpreted runner, not a build).
- **Sleeps.** Fake hanging checkers in the hang-guard tests account for about 20 s; those tests
  belong to the testspeed item and were not touched.
- **Python.** cProfile: English parsing is lark's Earley parser plus the hashing and equality it
  calls, ~75% of the time of a mixed-construct slice and of `test_assist_invariants` (both are
  dominated by `parse_english`'s all-derivations check), and rebuilding `EnglishVocabulary` for
  every parse is another ~15% of the slice (1,906 constructions in 37 s). Files dominated by
  English parsing hold about 2,100 s of the 6,361 s Python remainder.

## Slowest tests

Before (`-n 8`, load 42-67):

| s | test |
|---|---|
| 1,279 | test_english_evidence.py::test_english_mixed_merge_smoke |
| 1,008 | test_asimov_extended.py::test_rerun_equals_the_committed_results |
| 948 | test_wire_gate_corpus.py::test_gate_corpus_holds_every_contract_and_soft_test_input |
| 477 | test_readings_s1_differential.py::test_generated_sets_agree_with_lean |
| 436 | test_english.py::test_identity_fixtures_are_unchanged_after_english_roundtrip |
| 372 | test_lean_conformance.py::test_lean_transitive_axiom_allowlist |
| 361 | test_rights_three_way.py::test_rights_differential_on_one_thousand_generated_documents |
| 337 | test_bluedot_grant.py::test_document_coverage_and_premise_limit |
| 244 | test_p1_amendment13.py::test_refresh_dev_is_read_only_and_missing_cache_fails_closed |
| 243 | test_soft_review_regressions.py::test_generated_soft_conformance_is_part_of_suite |
| 225 | test_assist.py::test_astra_fix3_property_success_is_invariant_under_node_order_and_monotone_in_budget |
| 168 | test_safety_framework.py::test_rerun_equals_committed_results |
| 163 | test_norm_defaults_three_way.py::test_spec8_differentials |
| 160 | test_order.py::test_lean_differential_corpus |
| 152 | test_agent_policy_rerun.py::test_every_action_and_policy_query_equals_the_committed_results |
| 141 | test_soft_review_regressions.py::test_rejection_fixtures_and_generated_soft_inputs_share_codes |
| 140 | test_p1_amendment15.py::test_runner_preserves_finished_trajectories_initials_and_resumes_without_repurchase |
| 131 | test_soft_review_regressions.py::test_accepted_sources_elaborate_and_rejected_sources_share_codes |
| 124 | test_wire_gate_corpus.py::test_gate_corpus_holds_every_source_of_the_soft_conformance_module |
| 107 | test_discourse_lean.py::test_mention_spans_start_and_end_on_tokens |

After (`-n 8`, load 47-72):

| s | test |
|---|---|
| 271 | test_english.py::test_identity_fixtures_are_unchanged_after_english_roundtrip |
| 267 | test_wire_gate_corpus.py::test_gate_corpus_holds_every_contract_and_soft_test_input |
| 265 | test_lean_conformance.py::test_lean_transitive_axiom_allowlist |
| 221 | test_assist.py::test_astra_fix3_property_success_is_invariant_under_node_order_and_monotone_in_budget |
| 200 | test_soft_review_regressions.py::test_generated_soft_conformance_is_part_of_suite |
| 144 | test_p1_amendment15.py::test_runner_preserves_finished_trajectories_initials_and_resumes_without_repurchase |
| 143 | test_agent_policy_rerun.py::test_every_action_and_policy_query_equals_the_committed_results |
| 129 | test_p1_amendment13.py::test_refresh_dev_is_read_only_and_missing_cache_fails_closed |
| 125 | test_norm_defaults_three_way.py::test_spec8_differentials |
| 105 | test_asimov_laws.py::test_followability_agrees_across_python_rust_and_source_reading |
| 103 | test_discourse_lean.py::test_mention_spans_start_and_end_on_tokens |
| 97 | test_order.py::test_lean_differential_corpus |
| 93 | test_english_evidence.py::test_english_mixed_merge_smoke[12-4of8] |
| 93 | test_english_evidence.py::test_english_mixed_merge_smoke[12-0of8] |
| 91 | test_safety_framework.py::test_rerun_equals_committed_results |
| 90 | test_eligibility_wfp.py::test_staged_answers_match_the_key_and_the_recorded_results |
| 88 | test_wire_gate_corpus.py::test_gate_corpus_holds_every_source_of_the_soft_conformance_module |
| 87 | test_english_evidence.py::test_english_mixed_merge_smoke[12-3of8] |
| 87 | test_english_evidence.py::test_english_mixed_merge_smoke[12-2of8] |
| 87 | test_english_evidence.py::test_english_mixed_merge_smoke[8-0of2] |

The longest test now takes 271 s; before, three tests took 15-21 minutes each, and the suite could
not finish sooner than the longest of them.

## Changes (one commit each)

| commit | change | before → after |
|---|---|---|
| 871b5fd1 | profiling plugin and report | — |
| 30cdbfdf | mixed-construct English smoke split into 29 slices (per configuration, the three slowest configurations also by text index; the commit message says 30) plus one coverage test that generates without parsing; same seeds, same texts | one 1,214 s test → slowest slice 90 s |
| e5491dda | the contract/soft input recorder runs its 622 tests on xdist workers; recordings merged in collection order | serial 580 s → 258 s side by side; byte-identical output; committed inputs regenerate unchanged |
| d4b98970 | `compare_rejected` built the 17 fixed sources on each of 4,843 rows; now once | 83.6 s → 60.3 s per call |
| 3b23004e | two soft tests deleted: the module's report test makes the same calls and asserts the same values | −86 s and −107 s |
| d5a656f1 | risk margin candidates decided in batches; same records (checked) | candidate phase 6.3 s → 2.8 s per shard |
| 85f758d8 | `nightly` marker; asimov-extended full rerun moves to it, a records test replaces it by default | 900-1,008 s → 36 s by default |
| e24b661b | rights differential: 100 documents by default, 1,000 nightly | 341-361 s → 28 s |
| 199d0e4a | readings@1 differential: 200 documents by default, 1,000 nightly | 281-477 s → 72 s |
| dbc24d8e | `ve.search`: the defined predicates read once per model enumeration instead of decoding every definition's JSON for each predicate of each candidate (96% of the bluedot test's time) | 257-377 s → 31 s |

Tried and reverted: computing the eligibility baseline profiles lazily per mutant test. Its gain
depends on how xdist distributes the file's tests; on its own the file got slower.

## Nightly tests

Excluded by the default `addopts` (`-m 'not live and not nightly'`); run with `pytest -m nightly`.
`tools/gate.py` overrides `addopts` with `-m "not live"`, so the gate still runs them. All three
passed on HEAD (14.6 min at `-n 3`).

| nightly test | default replacement (same inputs) |
|---|---|
| test_asimov_extended.py::test_rerun_equals_the_committed_results (870-1,008 s) | test_rerun_of_the_records_equals_the_committed_results: the 51 records under both rule sets, the committed per-record results (36 s; a mutant changes 23 records and fails it) |
| test_rights_three_way.py::test_rights_differential_on_one_thousand_generated_documents (293-361 s) | test_rights_differential_on_one_hundred_generated_documents: the first 100 accepted documents of the same seeds, every shape, 23 rejections (28 s) |
| test_readings_s1_differential.py::test_all_generated_sets_agree_with_lean (416 s) | test_generated_sets_agree_with_lean: the first 200 of the same seeds, every fault and generator (72 s) |

What the default run no longer covers: the asimov document checks, mutants, sampled records and
permission default; documents 101-1,000 and 201-1,000 of the two differentials.

## Worker counts

The same 69 files (1,797-1,799 tests, ~2,700 test-seconds, longest test ~210 s), measured twice,
in opposite orders because the load changed during each series:

| workers | series 1 (before the fixes) | series 2 (after) |
|---|---|---|
| 8 | 557 s (load 72) | 362 s (load 35 → 18) |
| 12 | 400 s (load 72 → 59) | 329 s (load 47 → 35) |
| 16 | 370 s (load 59 → 45) | 293 s (load 90 → 47) |
| 24 | 340 s (load 45 → 31) | 388 s (load 96 → 90) |

`-n 16` was best or close to best in both; `-n 24` helped only on a quiet machine and was the
slowest at load 90. A whole-suite run at `-n 16` took 25.3 min at load 88-105, against 22.8 min at
`-n 8` at load 17-41: the load dominated. Recommendation: `-n 16` (docs/TESTING.md); not
`-n auto` (32) on this shared machine.

## Duplicate tests and tests that cannot fail (for review)

No test is shadowed by a second definition with the same name, no parametrization repeats an
entry exactly, and no test asserts nothing or compares a value with itself (all 2,445 test
functions in 209 files scanned; about half of the multi-line parametrize lists checked by hand).

| test(s) | finding | proposal |
|---|---|---|
| test_soft_review_regressions.py: the two `..._share_codes` tests | same calls and asserted values as `test_generated_soft_conformance_is_part_of_suite` | **deleted** (3b23004e) |
| test_discourse_lean.py: `test_python_verdict_is_lean_verdict_on_wording_variants`, `test_lean_and_python_discover_the_same_slots`, `..._agree_on_joined_words_and_spans`, `..._agree_on_discourse_wording`, the `agree`/`lean_verdict` callers; test_discourse_three_way.py `agree` (lines 127-128) | Python's admission of a `ve-document@2` text is the Lean route's answer, relayed (ve/discourse.py `lean_admission`, `validate_discourse`), so "same verdict, report id and references" compares Lean with Lean run twice. They still check the relay, Python's hints and the both-reject texts. | keep; rename as relay tests, or compare Python's own check where a differential is meant; the verdict part could use one Lean call per document instead of two |
| test_soft_norms_conformance.py::test_document_check_to_python_route_to_lean | the "three" answers come from the same soft route; the regeneration check is real | keep as a plumbing test; rename |
| test_discourse_lean.py::test_renewal_items_are_counterexamples_to_the_approved_statements | blocks R1, R2, R4, R7 repeat inputs and assertions of earlier tests (lines 355, 744-746, 675-678, 1015-1018) | merge on review (each block is another Lean call); they document the renewal table, so not deleted |
| test_evaluate_search.py lines 61-63 | `pytest.raises(Exception)` also passes on an unrelated error | narrow the exception |

## Where Rust could replace slow Python (not ported here)

1. **English all-derivations parsing** (lark Earley, `ve.surface.unambiguity`/`ve.english`):
   ~75% of the time of the English and assist tests profiled; ~2,100 s of test time. A Rust Earley
   check behind the same interface is the largest single Python cost the tests exercise. Before
   that, a cache of `EnglishVocabulary` per environment and options would save ~15% of it in Python.
2. **Wire JSON validation** (`ve.wire.validate_json`/`_string`, a per-character `ord` loop): it was
   73% of the bluedot test before the search fix and remains on every `loads_json`.
3. **Service response schema checks** (`ve.backends.service_schema`): in
   `test_fuzz_detects_a_weakened_schema[error-id]`, the schema checker's own code took 15% of the
   time and the test's fuzz driver 14%, the rest being the built-ins they call (the file: 253 s).

The prover and countermodel search were not dominant in any profiled test after the search fix.

## Next fixes, by estimated savings

| # | fix | estimate | owner / approval |
|---|---|---|---|
| 1 | `tools/gate.py` runs the Python suite serially (~2.6 CPU-hours of test time); run it on xdist (`tools/gate_pytest.py` must merge worker events) | gate pytest stage ~2.5 h → ~25 min | HUMAN (lead): the gate's trust setup |
| 2 | Lean risk route: elaborate each distinct policy once per batch (`lean/VE/Risk/Run.lean` `runDecision`) | asimov nightly ~870 s → ~60 s; risk margins and generated policies ~300 s | HUMAN: trusted checker change, statement review |
| 3 | English: cache `EnglishVocabulary`; then a Rust Earley check | ~300 s; then ~1,500 s | AGENT (cache), HUMAN (port) |
| 4 | `lean/audit.py` re-elaborates `VE/Audit.lean` (2,959 `#print axioms`) instead of reading lake's cached build log | test_lean_transitive_axiom_allowlist 211-372 s → ~10 s; the gate's audit stage too | HUMAN: audit trust boundary |
| 5 | `ve_experiments/paid.py` `Ledger.locked()` parses the 17 MB cost ledger on every call (~416 parses in one test) | p1_amendment12/13/15 ~300 s | HUMAN: paid-call ledger |
| 6 | Discourse: Python relays each document to `ve_discourse_route` alone (4,534 launches) | ~400-500 s | AGENT, needs a batched admission entry point |
| 7 | wire gate corpus: share `gate_cases` and the soft generators across its three tests | 50-100 s | AGENT |
| 8 | English identity round trip: reuse render's parse (`sentence_parse_cache`) | 90-140 s | AGENT; calls `render_english` directly, review |
| 9 | Longest-first scheduling (a custom xdist scheduler) once `-n 16` is standard | up to the 271 s longest test off the tail | AGENT |
| 10 | `conformance/english_lean.py`: the compiled `ve_english_run` instead of `lake env lean --run` | ~35 s | AGENT; the report's pinned runner |

## Not run, and checklist notes

- `tools/gate.py` did not finish: its pytest stage is serial and alone exceeds the one-hour
  foreground limit. On 5b005ade every stage before it passed (toolchains, wire contract check,
  Lean build and audit, Rust build, cargo test); the serial suite was stopped at the two-hour
  background limit, at `test_readings_s1_differential.py`. The default suite (8,668 passed, 6 skipped) and the nightly tests (3 passed)
  were run on HEAD in this worktree with prebuilt binaries.
- `tools/gate-collection.json` was updated only for the test IDs changed here; it was already
  212 IDs behind main's collection (another item regenerates it).
- Checklist items on contracts, normalisation, three-valued verdicts and identity (1-12, 15,
  17-19) do not apply: no checker semantics changed. Item 13: the new default tests were shown to
  fail on a mutant (asimov) or keep their predecessors' assertions. Item 20: the tables are taken
  from the committed summary JSONs, and `tests/test_testing_profile_doc.py` checks them against
  those files (it found four double-rounded times, such as 132 for 131.49 s, and a 44% that is 42%).
