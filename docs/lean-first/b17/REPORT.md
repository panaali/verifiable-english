# Lean first batch 17: assist and Cedar ownership

**Scope.** This batch rewires the two assist decision paths and Cedar adapter decisions to Lean. No Lean theorem or service code changed. The lead's 2026-10-08 rule-3 decision is recorded in [DELTA.md](DELTA.md).

## Saved source scope

Range: `main..HEAD --no-merges`, captured at code head `bcc6aa53f20aaa88e7dc6945325750428637486a` while `main` was `c85797de464d7b9a955b7e906a3d88e15c7b732f`; the A/B base is `7550e08a704a1a08690c9b1df9c18ad75590b2bd`. The figures below use the saved commit list and numstat in `evidence/scope.json`, so a later main sync cannot change them.

Source commits (saved): bcc6aa53f20aaa88e7dc6945325750428637486a, 533dd2907403dac325de8d198738309dd73bb03f, 39ba909ab219190ca14968ec39fcaea2ac60c11f, 1555942981587f945a33e334049995dfbf6abc71, 5ca2794ca398fe09a1092711c7e14b05136d717e

- Total lines deleted: 37
- Lean lines added: 0
- Python lines deleted: 37

The plan calls this a zero-deletion rewire. The physical Python deletions replace old decision call sites; there was no separate assist or Cedar semantic engine to delete. The Cedar caller no longer imports or invokes `_Evaluator`. The proof status in assist is an untrusted proposal: `_decide` and `_entails` call Lean certificate replay before `yes`; `_decide` calls Lean countermodel checking before `no`. Cedar closes each request query and takes the allow/deny and policy error decisions from Lean evaluation. Search-internal accelerators remain proposal mechanisms under the lead's rule-3 decision.

The line counts are cumulative per-commit numstat, including the tests and collection list, rather than a net source diff.

## Gate evidence

- Full gate: PENDING
- Rust: PENDING
- A/B: 96623 identical outcomes, 4 unavailable on both sides, across 96627 cases. Pilots: 412 documents. The four unavailable cases returned the same Lean lexicon diagnostic at base and head; there are zero divergent public outcomes. A transient Rust timeout in one head pilot was rerun twice at the same source and matched the base (saved raw records, comparison and rerun in `evidence/`; details in [DELTA.md](DELTA.md)).
- Difffuzz CI: 339 baseline entries, 0 new signatures, all baseline entries reproduced. The default sample covered requests, environments, wire and documents.
- Date seeds: 14 paired, 0 head-only signatures; 492 inherited signatures across the paired runs.
- `lake build --quiet` and the pinned Rust build passed. The Lean audit is included in the full gate. The separate `tools/lean_statements.py --check` passed: 4422 statements, 0 added, removed or changed (`evidence/statement-check.json`).

The gate's optional-test policy now names the existing Rust-scope skips for dependency order and labels; they were already skipped by the test and are outside Rust's declared operation set.

## Failure sensitivity

Seeded mutants: 4 failed as expected; each was removed and its named regression test then passed. The saved run is `evidence/mutants.json`:

- `assist_found_without_replay`: `_decide` returned yes from the prover status alone; `test_assist_decide_replays_found_in_lean` failed.
- `entails_found_without_replay`: `_entails` returned true from the prover status alone; `test_assist_positive_entailment_requires_lean_replay` failed.
- `assist_no_without_lean_witness`: `_decide` returned no without a Lean checked witness; `test_assist_negative_decision_requires_lean_countermodel` failed.
- `cedar_python_verdict`: Cedar pinned the Python evaluator; `test_cedar_evaluates_each_request_under_lean` failed.

**AGENT completed:** caller rewire, focused ownership tests, saved source scope, A/B corpus, CI difffuzz, date-seed pairs, seeded failures. **AGENT in progress:** final clean full gate. **HUMAN:** no public delta requiring DRI signature. **EXTERNAL:** none.
