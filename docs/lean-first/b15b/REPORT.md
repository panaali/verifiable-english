# Batch 15b fix report

Base `c07377ed` (main). Implementation commits on `lean-first/b15b`: `bc580837`, `39525394`, `14b61780`, `1a3bd559`, `b0f1c533`, `1d45f912`, `0dddf7d7`, `62b5ef8e`, `ac6f94a2`, `4e79a824`, `176929a1`, `760572b9`, `0509537d`, `427f6413`, `9770be82`, `60ae5b00`, `f19d9466`, `8f525133`, `373a7dd5`, `c43afbcc`. The immutable
[change snapshot](evidence/change-metrics.json) (`main..HEAD --no-merges`, captured before this report's last
commit) gives: Lean lines added: **2**; Total lines deleted: **7691**; Python lines deleted in `ve/`: **571**; Rust lines deleted: **1168**. The total counts every file: 5,393 of its deleted lines are the re-recorded fuzzer baseline (`conformance/difffuzz-baseline.json`, 350 to 339 entries), and its additions are mostly that file and this batch's evidence. The [ledger](LEDGER.md) maps every deleted decision site to
its owner; [`DELTA.md`](DELTA.md) lists every change for signature.

## The rule-3 condition (plan row 15b): measured, does not hold

[`rule3.py`](rule3.py) measures the implementation batch 2 measured, Rust enumerating and Lean evaluating,
now with batch 15a's metered evaluator (`ve_metered`), so charging is checked as well as order, first witness,
counts and exhaustion. Base: Rust's search with its own evaluator (`eval.rs`, the order evaluator), and the
provers' self-replay in Python. Head: the same Rust candidate stream (`rule3_enumerate`, and for order@0 a new
measurement-only stream `rule3_order_enumerate` behind `bench-internals`) charged and decided by Lean, and the
same certificates replayed by Lean's certificate route. Every head count is Lean's own answer to the exact
budget left at that candidate. The certificate rows cover the three cohorts whole: every prover query each
cohort generator (`conformance/certificates.py`, `closure_certificates.py`, `order.py`) asks, 811, 35 and
690 queries, of which 732, 33 and 546 yield a certificate. Their order is measured too: the prover must emit
the same status, certificate and step count when its self-replay is Lean's route instead of Python's
(review B4; the first measurement took the first 40 queries of each cohort and set order to pass). Record:
[`rule3.json`](evidence/rule3.json) (searches at load 20.85, 256 candidates per `ve_metered` call;
certificates re-measured at load 13.88 with `--certificates-into`); the table is regenerated from it by
`tests/test_b15b_evidence.py`.

| Operation | Queries | Order | First witness | Charging | Counts | Exhaustion | Deadline (s) | Base wall, total / slowest query (s) | Head wall, total / slowest query (s) |
|---|---:|---|---|---|---|---|---:|---:|---:|
| countermodel search | 28 | pass | pass | pass | pass | pass | 5: pass | 0.044 / 0.004 | 1.747 / 0.099 |
| guarded countermodel search | 56 | pass | pass | pass | pass | pass | 5: pass | 0.085 / 0.002 | 4.361 / 0.144 |
| distinguishing-model search | 28 | pass | pass | pass | pass | pass | 5: pass | 0.040 / 0.002 | 2.200 / 0.149 |
| bluedot countermodel search | 1 | pass | pass | pass | pass | pass | 5: FAIL (1) | 4.700 / 4.700 | 164.368 / 164.368 |
| order countermodel search | 40 | pass | pass | pass | pass | pass | 5: pass | 0.609 / 0.064 | 38.630 / 3.236 |
| tableau prover replay | 732 | pass | pass | pass | pass | pass | 5.00764: pass | 0.502 / 0.002 | 1.398 / 0.003 |
| closure prover replay | 33 | pass | pass | pass | pass | pass | 5.01107: pass | 0.027 / 0.001 | 0.070 / 0.003 |
| order prover replay | 546 | pass | pass | pass | pass | pass | 5.00967: pass | 0.521 / 0.003 | 1.185 / 0.005 |

**Which rows fail, and by how much.** One row fails, on one property: the bluedot document's search query
(19 premises, `definitions@0`; 10,000 candidates, `ResourceLimit` at the model bound) takes 164.4 s against its 5 s deadline
(base 4.70 s, Rust's own search), 32.9 times over the deadline. Lean is not wrong there: order, first witness,
charging (23,781 units), counts (10,000 models) and exhaustion all agree. The time is transport and decoding:
40 `ve_metered` processes received 516 MB (each candidate carries its model and the environment) and spent
153.8 s of CPU. Batch 2's handle-based service route took 42.3 s on the same query (8.4 times the deadline,
without charging). Every other row meets its deadline per query, but the head is far slower in total: the order
search 38.6 s against 0.61 s (63 times), the 28 search fixtures 1.75 s against 0.04 s.

**Consequence.** As the plan and the DRI's answer 2/10 require, `eval.rs`, the order evaluator and the provers'
Python replay are **kept** and listed unfinished (below); the rest of the row's list is deleted. The numbers go
to the lead for question 10.

## What was deleted and switched

- **Python search** (`ve/search.py`, 907 to 427 lines): the enumerator, the model pool and Python's
  non-vacuity check are deleted. Every authority now runs Rust's search; a witness is reported only after the
  countermodel.check entry accepts it and Lean's `VE.Route.NonVacuity` (through `ve_metered`) finds it
  non-vacuous. `check_document` no longer opens a model-pool scope.
- **Reported evaluation** (`ve/evaluate.py`, `ve/search.py`): under the `lean` (and, for `evaluate`,
  `rust-experimental`) authority the value, count, trace and `ResourceLimit` of `evaluate`, and the premise
  values, conclusion value, count and status of the countermodel check, come from Lean's metered evaluator
  instead of Rust's, so nothing Rust's evaluator computes is reported there (rule 3) except search counters
  (unfinished, below). The A/B shows the one consequence: 9 closure@0 counts now equal the Python authority's
  (DELTA V1).
- **Rust** (merged from a sub-worker): the `ve-surface` crate (`surface.rs`, 528 lines), `route.rs` (167),
  order.rs's own source parser (243), and the `ve` binary's `parse`, `format`, `evaluate`, `countermodel` and
  `check-countermodel` commands, `label`/`dependency-order` kinds and no-kind canonical/identity branch.
  Conformance tooling compares Rust only on the kinds it keeps (Python against Lean for parser, labels and
  dependency order); the difffuzz baseline was re-recorded with the same follow-up ids (350 to 339 entries).
  `units.rs`, `risk.rs`, `discourse.rs` and `readings.rs` were already gone (batches 3, 4, 5, 9).
- **Supporting changes**: `ve_metered` exits 1 when a case is rejected, as every one-shot runner (Lean, 1 line);
  manifest bindings and probes for both `ve_metered` calls; Rust's search and countermodel cases and both
  `ve_metered` calls read one model environment (`profiles.model_environment`: a row per registered profile
  saying what it adds that no model reads, plus English display text), so they answer every environment
  Python's search did (review A1/B1, below);
  `check_countermodel`'s Rust path binds to the plain projection (it rebuilt an `Environment` from an immutable
  cached projection, a latent bug on speech-acts environments). The 15a tests that used Python's
  `_nonvacuous` as their oracle read its frozen answers (`tests/nonvacuity_oracle.py`, 72,031 requests recorded
  at `bc580837` before the deletion; DRI answer 7).

## Gate evidence

| Acceptance item | Status and saved evidence |
|---|---|
| AGENT — rule-3 measurement | [`rule3.json`](evidence/rule3.json): table above; condition does not hold (bluedot deadline). |
| AGENT — corpus A/B | [`ab-compare.json`](evidence/ab-compare.json) over [both recordings](evidence/ab-recordings.json): 96,588 of 96,608 records identical; the rest listed in DELTA (9 `verdict` count rows, 7 recorder-path `wording` rows, 4 `unavailable` on both sides), 0 unlisted; 393 historical pilot rows. Head recorded at `1a3bd559`; recorded again at `176929a1` after the Rust deletion ([`ab2-compare.json`](evidence/ab2-compare.json), 96,587 identical, 0 unlisted), where the bluedot pilot document hit Rust's 5 s search deadline under load (DELTA A2). Recorded a third time at `0be2e4a5` after the review fixes ([`ab3-compare.json`](evidence/ab3-compare.json), 96,588 identical, 0 unlisted; the bluedot pilot document identical to base). |
| AGENT — differential fuzz | [`difffuzz-ab.json`](evidence/difffuzz-ab.json): CI plus 14 date seeds at base and head. The head finds fewer disagreements in every run (for example seed 20260929: 42 against 46 new, 246 against 256 baseline entries seen), because Rust no longer answers the parser, label and dependency-order surfaces; the committed baseline shrinks from 350 to 339 entries. There is 1 head-only signature, and [`difffuzz-head-only.json`](evidence/difffuzz-head-only.json) maps it to base finding `db6d6c1e`: the same seed and mutation with the same Python and Lean answers, renamed because Rust left its engine set. So there is no head-only signature that is a new disagreement. |
| AGENT — latency | [`latency.json`](evidence/latency.json): `evaluate` under Lean authority is 9.7 times slower (one-shot `ve_metered`, DELTA L1, needs the DRI); default search 1.9 times on the fixtures (no speed promised). |
| AGENT — seeded bugs | [`mutants.txt`](evidence/mutants.txt), from `mutants.py` at `0be2e4a5`: 13 seeds, one per claimed behaviour (seven for the review fixes), each planted alone, each failing its named tests, then removed; the restored tree passes all 617 focused tests (below). |
| AGENT — full suite | [`full-suite.json`](evidence/full-suite.json): at `feadf353` in a clean checkout (`VE_*_PREBUILT=1`, `-n 20`, `tests` plus `tools/test_layer_policy.py`): 12330 passed, 8 skipped, 0 failed; Rust 36 passed. An earlier run under heavier load had two `test_w6a_limit_generator` bounded-time failures that passed on rerun and in this run. `tools/gate.py` (serial) was not run. |
| HUMAN — DELTA signatures | V1, W1, A1, A2, L1 (DRI). |
| HUMAN — lead decision | question 10 on the rule-3 duplicates, with the table above. |
| EXTERNAL — operational soak | deferred to the DRI after 13b (DRI answer 1). |

Checklist: 1 and 5 (decoding stays Lean's: `ve_metered` reads through `Standalone.evaluable`); 4 (both
`ve_metered` rows are checked against manifest response types; malformed evaluation objects and traces are
`CheckerUnavailable`); 6 (an exhausted non-vacuity check is never a yes; budget-zero searches covered by the
existing search tests); 13 (seeded bugs below); 14 (`HANG_TIMEOUT`, tmp paths); 16 (manifest probes for every
binding); 20 (this report's numbers are regenerated by `tests/test_b15b_evidence.py` from saved evidence).
Items 2-3, 8-12, 15, 17-19 have no new decision site in this batch. Lean statements: none added or changed.

## Seeded bugs (build checklist 13)

| Seed | Behaviour claimed | Fails |
|---|---|---|
| `python-search-branch` | Python has no search of its own: every authority runs Rust's | `test_search_reports_found_only_through_the_countermodel_check` |
| `lean-nonvacuity-ignores-semantic` | a witness's non-vacuity is Lean's, semantic mode included | `test_semantic_clause_guard_is_joint_per_occurrence_and_checks_hidden_branches` |
| `lean-evaluation-count` | the reported evaluation count is Lean's metered count | 40 tests of `tests/test_stage2_evaluation.py` (traced and layered evaluation against Python) |
| `model-environment-keeps-display` | Rust's search and Lean's metered cases read no display text (A1/B1) | 113 tests of `tests/test_model_environment.py` |
| `model-environment-keeps-unspecified` | the model environment carries every registered profile (A1) | 16 tests of `tests/test_model_environment.py` |
| `metered-reads-the-route-environment` | Lean's non-vacuity and metered evaluation read the model environment (B1) | 118 tests of `tests/test_model_environment.py` |
| `lean-countermodel-check-reports-rust` | the Lean authority's countermodel check reports Lean's values and counts (B3) | 47 tests of `tests/test_lean_authority_values.py` |
| `execute-shadows-one-implementation` | no dispatch compares one implementation with itself (B2) | `test_execute_refuses_a_comparison_of_one_implementation_with_itself` |
| `difffuzz-compares-search-with-itself` | difffuzz does not compare Python's (Rust's) search value with Rust's (B2) | `test_difffuzz_never_compares_a_single_owner_value_with_its_owner` |
| `metered-exit-status` | `ve_metered` exits 1 on a rejected case (Lean, rebuilt) | `test_bad_budget_types_are_bounded_errors` |
| `rule3-summary-ignores-deadline` | the rule-3 table counts the deadline | `test_rule3_rows_are_recomputed_from_the_saved_records` |
| `rule3-certificate-sample` | the certificate rows count the whole cohorts (B4) | `test_rule3_rows_are_recomputed_from_the_saved_records` |
| `rule3-certificate-order-constant` | the certificate rows measure order (B4) | `test_rule3_certificate_order_is_measured_not_assumed` |

## Review fixes (`lf-15b-review.final.md`)

Each finding was treated as a class, with a failing example kept as a regression test; every fix keeps the
search, its witness checks and the frozen contracts as they were.

| Finding | Class removed, and how | Commit | Regression |
|---|---|---|---|
| A1: default-authority search, `premise_status` and `compare` failed with Rust's own error on `norm-defaults@0`, `readings@1`, `alternatives@0` and `risk@0` environments | Engines given an environment Python accepts but they refuse. One table, `profiles.MODEL_REDUCTIONS` (a row per registered profile, checked against the registry), says what each profile adds that no model reads; `model_environment` applies it, plus display text, for every Rust case and every `ve_metered` case. `route_environment` is the statement-layer rows of the same table (byte-identical on every saved environment). | `0577b1bb` | `tests/test_model_environment.py`: search, guarded and semantic search, distinguishing search, `premise_status` and `compare` over 347 fixture environments covering all 17 profiles, each also with display text everywhere, equal Python's own answers at the base (1,962 answers; 545 differed before the fix); the projection keeps every model-relevant declaration and Background premise |
| B1: non-vacuity search with a constant's `verbalisation` was `CheckerUnavailable` | Same class, Lean side: `ve_metered` reads the model environment | `0577b1bb` | the same test's display variants |
| B2: search tests compared Rust with Rust | Differentials of an engine with itself. `dispatch.SINGLE_OWNER` names the single-owner operations: `execute` refuses them and any identical pair (the shadow mode compared Rust with Rust too), `owned()` runs them, `three_way.KIND_OPERATIONS` maps request kinds onto them, and difffuzz no longer compares Python's search value with Rust's | `41221717` | the three tests now compare the Rust binary with Python's own answers at the base (`tests/data/b15b-search-oracle.json`) and check witnesses with Python's check; `tests/test_single_owner.py` requires every request kind reaching a single-owner operation to be classified |
| B3: under the Lean authority the countermodel check reported Rust's values and counts | Reported answers computed by Rust's evaluator. The check's sequencing is one function over an evaluator: Python's, or Lean's metered one under the Lean authority | `40b1553c` | `tests/test_lean_authority_values.py` fails any non-search Rust request under the Lean authority and requires Python's values and counts on every closure fixture (47 of 48 failed before) |
| B4: certificate rows were samples, order hard-coded | Measurements re-deriving a corpus by hand. `rule3.py` captures every prover query the cohort generators make, and measures order as the prover's output with Lean's self-replay | `ad350b88` | `tests/test_b15b_evidence.py` recomputes order from the saved prover answers, checks the cohorts are whole, and runs the measurement with a sabotaged Lean replay |

## Unfinished

- **The three rule-3 duplicates**: Rust's `eval.rs`, the order evaluator in `order.rs`, and the provers'
  Python replay (`_Replayer`, `_check_certificate_python` with `_background=False`, `order.replay_trace`).
  Kept because the condition fails (bluedot deadline); their own certificate rows pass. Rust's search counters
  are still Rust's, measured equal to Lean's on every row.
- **`_Evaluator` and its callers** (`norms`, `cedar`, `readings`, `model`, `background`, `norm_defaults`,
  `readings_verdicts`, the default-authority countermodel check): the default authority is still `python`
  because batches 12b and 13b have not merged; rewiring them first would change every default-authority path.
- **Lean checking every witness under the default authority**: Lean's route refuses environments Python
  accepts (`verbalisation` fields), so the default authority's witness check is still Python's; non-vacuity is
  Lean's under every authority. Closed by batch 12b.
- **`ve_metered` as service modes** (latency L1).

Not run: a pilot-load latency comparison (the readings route is untouched; its pilots are unavailable at both
sides), and the 1,000-document rights and soft-norm differentials beyond the A/B's own corpora.
