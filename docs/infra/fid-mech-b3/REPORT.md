# fid-mech-b3: binding tables in bindings.json, execution adapters, the isolated worker, the result record (build report)

**Status:** built, and review F1 (B) is fixed (section 13). All four deliverables are done and none was cut. The selected run on the committed F1 fix (92f27d2740) passed: 201 units in 3 shards, exit 0. Before the fix, the run on 89f865f36e passed 227 units (section 8b). **HEAD:** the commit carrying this report (branch infra/fid-mech-b3); after 89f865f36e it adds this file, then the F1 fix (tools/fidmech/records.py, tests/test_fidmech_records.py, seeded-bugs.json S16-S18).
**What changed:** the case-to-atom tables of the RSP, PF and FSF run.py files are now in `usecases/<doc>/fidmech/bindings.json`, sha256-pinned, and every results.json is byte for byte unchanged. New `tools/fidmech/{bindings,adapters,worker,records}.py`. FSF main()'s comparison is factored into `with_comparison()`. Four new test files.
**Open:** none. **DRI signature:** none reserved. DELTA is none: Python tooling and data, no trusted Lean line, no decision path replaced, trust +0.
**Seam:** none used. Operations override 1 withdraws the line cap, and no part waits on another item, so (3) and (4) stay in this item (plan 10's seam rule names no other reason).

SIZE: 873 product, 690 tests, 261 other hand-written lines (40 fixture lines; 221 bindings.json lines, the run.py literals moved to data, with 143 run.py lines removed). The evidence files in this directory are command output, not hand-written.

## 1. Deliverables (task DO list; plan 2a, 2e, 6, 10; Opus round 2 points 6 and 12 "VE facts")

| item | where | commit | test |
|---|---|---|---|
| (1) bindings.json x3, loader rebuilding tuple/list/set/nested tuples | `usecases/*/fidmech/bindings.json`, `tools/fidmech/bindings.py` (`load_bindings`, type grammar `str bool int list[T] set[T] tuple[T,...] tuple[T1,T2] dict[str,T]`) | 8b0c2d3975, 3a29c612e9 | test_fidmech_bindings.py::test_the_loader_rebuilds_the_exact_python_types_of_the_literals, test_each_type_round_trips[9], test_a_value_of_the_wrong_shape_is_refused_with_its_path[7], test_a_malformed_bindings_file_is_refused_by_name[8] |
| (1) sha256 of each file pinned in the test, not in the file | tests/test_fidmech_bindings.py `PINNED` | 3a29c612e9 | test_each_bindings_file_has_its_pinned_sha256[3] |
| (1) each file is the canonical dump of its tables | `dump_bindings` | 3a29c612e9 | test_each_file_is_the_canonical_dump_of_its_tables_and_names_plan_2as_tables[3] |
| (1) RSP loader keeps SCENARIO_TERMS, K_LIMITS, PREDICATES as module attributes (test_rsp_fidelity_fix.py:266, :280-282 unchanged) | usecases/anthropic-rsp/run.py | 8b0c2d3975 | test_run_py_keeps_each_table_as_a_module_attribute_read_from_the_bindings[3]; tests/test_rsp_fidelity_fix.py unchanged and passing (section 8) |
| (1) behaviour-preserving: `run.py --check` green, results.json byte for byte | the three run.py files | 8b0c2d3975 | run-check.txt (section 2); test_safety_framework.py::test_rerun_equals_committed_results; the three live adapter tests |
| (1) the report prints the bindings diff against frozen_from | `frozen_diff`, bindings-frozen-diff.txt | 3a29c612e9 | test_the_frozen_diff_compares_what_run_py_reads_with_the_literals_at_frozen_from, test_the_frozen_diff_shows_a_changed_entry_and_a_changed_type |
| (2) one adapter per document: {item id: answer tuple}, no timings, costs or counters | `tools/fidmech/adapters.py` (`adapt`, `project`, `ANSWER_FIELDS`) | 9d7aa88886 | test_the_answer_fields_follow_the_plans_table |
| (2) adapter baseline projection == the matching fields of the committed results.json, per document | `adapt` through a fresh worker | 9d7aa88886 | test_fidmech_adapters.py::test_the_adapters_baseline_projection_equals_the_committed_results[3] (Lean) |
| (2) PF rows carry no release field; FSF rows carry ve_rel (key_rel is the key, left out) | `ANSWER_FIELDS` | 9d7aa88886 | test_the_answer_fields_follow_the_plans_table |
| (2) FSF main()'s comparison factored into one function both call | `with_comparison()` in usecases/safety-framework/run.py; `adapters.run_document` | 8b0c2d3975 | the FSF live adapter test; seeded bug S15 |
| (2) Opus point 6: per item the selected rule ids and the case-model atoms | `rules_of` (RSP choices[*].rules, FSF details[*]["rules"], PF selected_rules), `atoms_of` | 9d7aa88886 | test_the_selected_rule_ids_are_read_from_each_documents_own_place, test_the_case_model_atoms_are_those_true_in_every_model_the_item_read, test_the_committed_results_give_the_rule_ids_the_rsp_tests_name; the live adapter test (atoms of RSP K20, PF K3, FSF A-L1-DEV) |
| (3) scratch copy of the whole usecases/ tree, ve and tools from the worktree | `worker.scratch_tree`, `evaluate_tree` | 9d7aa88886 | test_a_mutant_runs_in_a_scratch_copy_and_the_module_is_purged_after |
| (3) per mutant: purge use-case modules, fresh module names, adapter; never main(), never module globals | `purge`, `import_run`, `evaluate_tree` | 9d7aa88886 | same test; the toy's main() raises; test_a_clean_batch_kills_the_mutant_and_every_sentinel_holds |
| (3) sentinels: baseline first, every 20, last; INVALID and re-queue once; batch INVALID when first and last differ | `run_batch` | 9d7aa88886 | test_a_leaked_module_global_makes_the_batch_invalid (plan 10 plant), test_a_sentinel_failure_requeues_each_result_since_the_last_good_one_once, test_a_result_invalid_twice_stays_invalid_and_a_differing_last_baseline_fails_the_batch, test_the_defaults_are_the_plans |
| (3) timeout 10x baseline seconds -> error; an exception -> error | `Worker.run`, `alarm`, `close_lean_pool` | 9d7aa88886 | test_a_run_past_ten_times_the_baseline_is_an_error, test_a_raised_timeout_is_an_error_and_resets_the_lean_pool, test_an_exception_or_a_system_exit_of_the_mutant_is_an_error, test_the_real_alarm_raises_the_timeout_in_the_main_thread |
| (3) warm against fresh measured; fresh under 2x -> fresh is the default | `measure`, `DEFAULT_FRESH = True` | 9d7aa88886 | section 4; test_a_fresh_process_gives_the_warm_projection, test_the_defaults_are_the_plans |
| (4) the result record: fields and verdict vocabulary of plan 2e | `tools/fidmech/records.py` (`result_record`, `VOCABULARY`, `kernel_verdict`) | 9d7aa88886 | test_a_result_record_has_the_plans_fields_in_their_vocabulary, test_a_verdict_outside_its_vocabulary_or_a_missing_one_is_refused[5], test_k_kills_on_a_decided_answer_that_differs_and_a_move_to_or_from_undecided_is_inconclusive[6] |
| (4) inputs_sha256: canonical JSON of the listed inputs; B4/B5 files enter as absent | `collect_inputs`, `inputs_sha256` | 9d7aa88886 | test_inputs_sha256_changes_when_any_listed_input_changes[12], test_the_generator_version_and_each_mutant_id_and_edit_enter_the_hash, test_every_key_of_the_inputs_enters_the_hash_and_a_missing_or_extra_key_is_refused, test_the_inputs_are_deterministic_and_a_file_later_batches_create_enters_as_absent |

Every new test fails on the old code. `tools/fidmech/{bindings,adapters,worker,records}.py` and the bindings files do not exist on main, so the four new test files fail at import.

**Condition tests (stay selected):** tests/test_fidmech_segment.py, tests/test_fidmech_l1.py (B1); tests/test_fidmech_b2.py, tests/test_fidmech_data.py (B2); tests/test_rsp_fidelity_fix.py; and this batch's tests/test_fidmech_bindings.py, tests/test_fidmech_adapters.py, tests/test_fidmech_worker.py, tests/test_fidmech_records.py. `uv run python tools/select_tests.py --base $(git merge-base HEAD main)` selects all nine (215/638 units; /tmp/b3/select-plan.log at the time of the run).

**Fixture tests:** no new test file contains the text the fidq step selects on: `grep -nE 'DEFAULT_SOURCE|pinned\s+source' tests/test_fidmech_{bindings,adapters,worker,records}.py` prints nothing. The source hashes enter inputs_sha256 from `usecases/pinned_sources.json` (`text_sha256`, `pdf_sha256`); no source is opened.

**Tests that need Lean:** only `test_the_adapters_baseline_projection_equals_the_committed_results[3]`. It is marked the way tests/test_rsp_fidelity_fix.py marks its own: `skipif(not lean/.lake/build/bin/ve_service exists)`. It runs each document's baseline in a fresh worker process (RSP about 80 s, FSF about 170 s, PF about 235 s; section 4). Every other new test runs without Lean, the worker tests on a toy use case (`tests/data/fidmech/worker/usecases/anthropic-rsp/run.py.txt`, built into tmp_path).

**Untouched:** quote_evidence.py, every conftest, fidquote-gate.py, every translation file (rules, facts, vocabulary, spans), every existing use-case test file.

### 1a. Plan 2a's table lists, confirmed against the files

`uv run python -c "from tools.fidmech.bindings import frozen_diff; ..."` → docs/infra/fid-mech-b3/bindings-frozen-diff.txt. It evaluates each run.py name that reads the bindings and compares it with the literal of the same name in run.py's blob at frozen_from (f97dd2d0c0). 28 names read "same". The 2 new names are FSF's INLINE_ITEMS and CATCH_ALL_OWN, which were inline code.

- **RSP, moved (8, as listed):** OT, SCENARIO_TERMS, SCENARIOS, COMPETITORS (a list), SITUATIONS, CASE_ATOMS, PREDICATES, K_LIMITS. K_LIMITS was a dict comprehension; the file holds its two entries.
- **PF, moved (16, as listed):** LEVEL_IDS, ACTIVITY, OT, SITUATIONS, STATED_FALSE, SOME_HIGH_LEVEL (a set), ATOMS, K_ITEMS, ALL_OF (a set), SUBJECT, WITNESS, WITNESS_LEVELS, WITNESS_RELATIONS, THRESHOLD_PREDICATES, CRITICAL_PREDICATES. SAFEGUARD_PREDICATES keeps its structure in code: `THRESHOLD_PREDICATES + _B["SAFEGUARD_PREDICATES_ADDED"]`, with only the literal part in the file.
- **FSF, moved:** SELECTION_ITEMS and SILENT_ITEMS.
  - DM and SEC (point 12) move with SELECTION_ITEMS. The file holds them once, as SELECTION_ITEMS["DM"] and ["SEC"], and run.py reads `DM = SELECTION_ITEMS["DM"][0]` and `SEC = SELECTION_ITEMS["SEC"][0]`, so the data has one owner.
  - SILENT_ITEMS keeps `"SEC": SEC` by reference in code and holds its other four entries in the file.
- **FSF item_predicates() (point 12: "binds four item kinds inline"):** the four are GOV, SILENT:CCA+GOV, FORBIDS+L0 and CHECKPOINT_MCCA. They move to a table INLINE_ITEMS, since by 2a's rule they map a question to predicates. CATCH_ALL's own predicate ("acceptable") moves to CATCH_ALL_OWN, and its structure `CATCH_ALL_OWN + DM + SEC` stays in code.
  - answer() bound the same literals a second time inline: GOV's `("proceed",)`, CATCH_ALL's `("acceptable",)`, CHECKPOINT_MCCA's `("change_assessed",)` and CCA's release `("assessed",)`. It now reads INLINE_ITEMS, CATCH_ALL_OWN and SELECTION_ITEMS["CCA"], so each binding has one owner.
  - Each value is equal, as the frozen diff and the byte-identical results.json show.
- **Stay in code, as 2a says:** FSF DOMAINS (derived from the vocabulary); CLUSTERS, EXPECTED_MUTANTS, ALIASES, CAUSES; PF M2_PERMISSION and M3_ALIGNMENT (the M2/M3 texts).
- **Stay in code, my reading of 2a's rule** (none maps a question or a case to atoms, predicates or entities):
  - PF COMMITMENTS, N1_RULES and NARROWED (bookkeeping of rules and reading sets);
  - PF SEVERITY_BRIDGES (number readings);
  - RSP C_DOC_SETS and G1_ACT;
  - FSF CONFLICT_CLUSTERS and DEVIATIONS (rule clusters and key bookkeeping);
  - FSF GOVERNANCE_FINDING. This is the one borderline case: a single atom the GOV item removes from its case. It is a constant, not a table, so it stays (Notes for the DRI).

## 2. Behaviour preserved (results.json byte for byte)

`uv run python usecases/<doc>/run.py --check` (main(): it rebuilds results.json and compares the text) at the base f97dd2d0c0 and at 8b0c2d3975, the commit that moved the tables. All six exit 0; docs/infra/fid-mech-b3/run-check.txt has the times and last lines (RSP 110/126; PF 236/239; FSF ends at its known DISAGREE G3 line).

Later commits change no run.py and no table value:
- `git diff 8b0c2d3975 HEAD -- usecases/` shows only the one added `run_py_blob` line per bindings.json (3a29c612e9), metadata the loader does not hand to run.py.
- The pinned files' tables are equal (test_each_file_is_the_canonical_dump_of_its_tables_and_names_plan_2as_tables; bindings-frozen-diff.txt).

The live adapter tests at HEAD also rerun run.py on each document and compare its answers with the committed results.json (section 8).

## 3. Adapters (plan 6; Opus round 2 points 6 and 12)

- **Answers** (`ANSWER_FIELDS`):
  - RSP: `ve`.
  - PF: `ve` plus `soft.ve` on the 14 rows that carry `soft`. PF rows have no release field (point 12), and the key's `soft.key` is left out.
  - FSF: `ve`, `ve_rel` (the DM/CCA release sets) and `premises`. These come from the comparison main() writes (`with_comparison`), D2/D3 rows included. `key_rel`, `deviation`, `route`, `status` and `cause` are left out: they are key or bookkeeping, not VE answers.
  - Each value is frozen through a JSON round trip, so a live run and a committed results.json compare equal.
- **Rule ids per item (point 6):**
  - RSP: every `rules` list of a `choices` row at any depth. C-doc's rows hold groups of rule ids, which are flattened.
  - FSF: every `details[*]["rules"]`, through parts and alternatives.
  - PF: `selected_rules`, never `audit_input.rules` (built rules that no block holds).
- **Case-model atoms per item (point 6)** are read through the module's own functions. No logic is copied.
  - RSP: `atoms(case)`, the case plus the threshold facts.
  - FSF: `fact_atoms() | case_atoms(s)` for each situation of `item_case(...)`.
  - PF: `atoms(case, {**BASE, **choice})`.
  - **Decision (conservative):** an atom is listed only when it holds in every model the item read. PF's atoms depend on the choice (RS2 nest adds a High level), so they are intersected over the item's choices; FSF's are intersected over a case's alternatives. B4's add-guard-true then adds only a guard that is true in every model the rule is selected in. An item with no case has none. K9 (SOME_HIGH_LEVEL) is read without its level, so its atoms leave out the level that varies.
- **FSF run() also runs variants() and the default-sensitivity pass (point 12).** The adapter calls run() whole, then with_comparison(). Splitting run() would change the decision path the task keeps byte-identical. The output of those two passes is left out of the projection, and their cost is inside every FSF run's seconds (FSF about 130 s warm, 170 s fresh).
- **Agreement:** the projection also carries each row's own `agree`, which the record's toward/away count reads. The key is never recomputed.

## 4. Worker: warm against fresh (plan 6, "Check of the warm-service choice")

Measured on VM1 (load average about 11), `python -m tools.fidmech.worker measure --document <doc> --scratch /tmp/b3/scratch --runs 2`. Output: docs/infra/fid-mech-b3/warm-fresh-baseline.jsonl (seconds per run).

| document | warm run 1 | warm run 2 | fresh run 1 | fresh run 2 | fresh / warm run 2 |
|---|---|---|---|---|---|
| RSP | 66.0 | 32.7 | 76.2 | 87.4 | 2.5 |
| FSF | 163.4 | 129.9 | 162.8 | 175.2 | 1.3 |
| PF | 191.5 | 118.5 | 202.8 | 266.7 | 2.0 |

- In all three documents the projections of all four runs are equal (`projections_equal: true`), which is a real-document sentinel.
- A repeated baseline can hit the Lean-side caches, which are keyed by the source text, so warm run 2 understates what a mutant costs. A real wording mutant settles it: RSP f20-notify-board must→should (`/tmp/b3/measure_mutant.py`; docs/infra/fid-mech-b3/warm-fresh-mutant.json). The warm worker took 83.0 s after its baseline, a fresh process 118.1 s, so **fresh costs 1.42x warm**. The two projections are equal; K reads `survived` (flip-force).
- Summed over the three documents, the repeated-baseline figures give 485.8 s fresh against 281.1 s warm, which is 1.73x.
- By the plan's rule (fresh under 2x warm), **fresh is the default**: `DEFAULT_FRESH = True`. B5 can pass `fresh=False`.
- **Timeout in each mode.** A fresh run's timeout is the child process's (`subprocess.run(timeout=limit)`). A warm run's is SIGALRM in the main thread, after which the relay's service pool is closed (`close_lean_pool`).
- **cpu_seconds** is this process's CPU plus its reaped children's. That covers a fresh run and the Lean service it stopped. A warm worker's live Lean service is not counted (worker.cpu_seconds docstring).

## 5. The result record and inputs_sha256 (plan 2e)

- **Record keys, in order:** id, verdict {K, L1, L2, L3, L4, D, CR}, kernel {changed, inconclusive, toward_key, away_from_key}, seconds, cpu_seconds, worker, sentinel_ok, inputs_sha256.
- **Vocabulary:** K is killed, survived, inconclusive, error or not-run; L1-L4 and D are killed or survived; CR is found, missed or not-read. Anything else is refused.
- **`kernel_verdict`:**
  - A decided answer that differs from the batch baseline kills.
  - A move to or from the third value is inconclusive, never a kill. `records.UNDECIDED` is the one table of its spellings: UNDECIDED (RSP, PF; `UNDECIDED-faithful`), UNKNOWN (FSF: N1, premises, S1, S4, D1, D3), NOT RUN (FSF) and a resource limit (`resource limit: ...`, `resource-limit`), each alone or followed by `-`, `:`, a space or `(`. A decided string that only contains one of the words (UNKNOWN_ACTOR, NOT RUNNING) still kills. Review F1 (section 13).
  - An item set that differs from the baseline's is `error`.
- **`collect_inputs` gathers each plan input:**
  - the commit, and every uncommitted change: the sha256 of `git diff --binary HEAD` and each untracked file's sha256;
  - `text_sha256` and `pdf_sha256` from pinned_sources.json;
  - the sha256 of boundaries.json, ruled_out.json, equivalents.json and bindings.json, plus any other file of `usecases/<doc>/fidmech/` (actors.json, B4). An absent file is `None`;
  - every file under tools/fidmech/ (cues.json and logic_words.json included);
  - the generator version (`None` until B4);
  - the sorted [mutant id, sha256 of the canonical JSON of its edits] pairs (`[]` until B4).
- **`inputs_sha256`** is the sha256 of the canonical JSON (sorted keys, no spaces, UTF-8) of exactly those seven keys. A missing or an extra key is refused. Refusing a resume or a merge on a difference is B5's runner, as the task says.

## 6. Plant table (plan 10 rows for B3, and the task's tests): test -> class

| plant | test that fails | class |
|---|---|---|
| a SITUATIONS entry changed in bindings.json (plan 10 "bindings") | test_each_bindings_file_has_its_pinned_sha256[anthropic-rsp] | pinned hash |
| the loader rebuilds tuple[T,...] as a list | test_the_loader_rebuilds_the_exact_python_types_of_the_literals | type round trip |
| a worker with a leaked module global (plan 10 "sentinel") | test_a_leaked_module_global_makes_the_batch_invalid (no plant needed: the leak is the fixture; the batch is INVALID) and, with the sentinel compared by status only, that test fails | sentinel |
| a run 31 s against a 30 s limit (injected clock) | test_a_run_past_ten_times_the_baseline_is_an_error (fails when the check is removed or the factor is 20) | timeout -> error |
| the adapter misses a field / a rule source / intersects wrongly | test_the_answer_fields_follow_the_plans_table, test_the_selected_rule_ids_are_read_from_each_documents_own_place, test_the_case_model_atoms_are_those_true_in_every_model_the_item_read | projection, point 6 |
| FSF with_comparison drops the D2/D3 rows | test_the_adapters_baseline_projection_equals_the_committed_results[safety-framework] | adapter baseline == results.json |
| an input left out of the hash (untracked files; a B4 case file) | test_inputs_sha256_changes_when_any_listed_input_changes[actors.json created], [equivalents.json created] | inputs_sha256 |

## 7. Seeded bugs (Python is the only language changed; no Lean, no Rust)

Each bug was planted in a copy of the named file, its test was run, and the file was restored with `git checkout` (script /tmp/b3/plants.py). The 18 records, with each test's FAILED line, are in docs/infra/fid-mech-b3/seeded-bugs.json (`killed: true` on all 18; S16-S18 are the review F1 fix's, section 13). The run was refreshed on the final code (f34eeea976; S15 at c01705f4e5, whose run.py and adapters equal the final ones).

| # | file | bug | failing test |
|---|---|---|---|
| S1 | usecases/anthropic-rsp/fidmech/bindings.json | K2's SITUATIONS atom changed | test_each_bindings_file_has_its_pinned_sha256[anthropic-rsp] |
| S2 | tools/fidmech/bindings.py | tuple[T,...] built as a list | test_the_loader_rebuilds_the_exact_python_types_of_the_literals |
| S3 | tools/fidmech/bindings.py | a set's duplicate member accepted | test_a_value_of_the_wrong_shape_is_refused_with_its_path[set[str]-...] |
| S4 | tools/fidmech/adapters.py | a dotted field (PF soft.ve) never read | test_the_answer_fields_follow_the_plans_table |
| S5 | tools/fidmech/adapters.py | PF rule ids read from audit_input.rules | test_the_selected_rule_ids_are_read_from_each_documents_own_place |
| S6 | tools/fidmech/adapters.py | atoms united, not intersected | test_the_case_model_atoms_are_those_true_in_every_model_the_item_read |
| S7 | tools/fidmech/worker.py | no purge of use-case modules | test_a_mutant_runs_in_a_scratch_copy_and_the_module_is_purged_after |
| S8 | tools/fidmech/worker.py | a sentinel compared by status only | test_a_leaked_module_global_makes_the_batch_invalid |
| S9 | tools/fidmech/worker.py | no re-queue after a failed sentinel | test_a_sentinel_failure_requeues_each_result_since_the_last_good_one_once |
| S10 | tools/fidmech/worker.py | a run past the limit is not an error | test_a_run_past_ten_times_the_baseline_is_an_error |
| S11 | tools/fidmech/worker.py | TIMEOUT_FACTOR 20 | test_a_run_past_ten_times_the_baseline_is_an_error |
| S12 | tools/fidmech/records.py | untracked files left out of the inputs | test_inputs_sha256_changes_when_any_listed_input_changes[actors.json created] |
| S13 | tools/fidmech/records.py | a B4 case file (equivalents.json, actors.json) left out | test_inputs_sha256_changes_when_any_listed_input_changes[actors.json created] |
| S14 | tools/fidmech/records.py | a move to UNDECIDED counted as a kill | test_k_kills_on_a_decided_answer_that_differs_and_a_move_to_or_from_undecided_is_inconclusive[...] |
| S15 | usecases/safety-framework/run.py | with_comparison drops the D2/D3 rows | test_the_adapters_baseline_projection_equals_the_committed_results[safety-framework] (Lean; 363 s) |
| S16 | tools/fidmech/records.py | UNKNOWN left out of UNDECIDED (review F1) | test_the_review_probe_f1_an_fsf_answer_moving_to_unknown_is_inconclusive, test_fsfs_own_undecided_answers_on_its_committed_results_are_inconclusive, the source guard (9 failed) |
| S17 | tools/fidmech/records.py | suffixed spellings not recognised (exact match only) | test_every_third_value_spelling_in_an_adapted_documents_sources_is_recognised_by_the_kill_rule, test_a_move_to_or_from_every_third_value_spelling_is_inconclusive_never_a_kill[*-UNDECIDED-faithful] (10 failed) |
| S18 | tools/fidmech/records.py | substring match: a decided string with a third-value word read as undecided | test_a_decided_string_that_only_contains_a_third_value_word_still_kills (4 failed) |

**trust_mutants:**
- light-lane check: `NOT 1949 changed lines outside generated files > 150 (17 files)`, so the sweep runs as usual.
- `uv run python tools/trust_mutants.py --plan` (a plan, allowed directly) prints `{"definitions": 0, "mutants": 0, "to_run": 0}` (docs/infra/fid-mech-b3/trust-mutants-plan.json). The branch changes no Lean, so there is nothing to sweep and none was run.

## 8. Test runs

- **While iterating:** the four new files.
  - `uv run pytest -q tests/test_fidmech_worker.py`: 12 passed.
  - `tests/test_fidmech_records.py`: 30 passed.
  - `tests/test_fidmech_bindings.py` with `tests/test_lineage_lint.py`: 57 passed.
  - `tests/test_fidmech_adapters.py -n 3`: 9 passed in 463.68 s, Lean tests included.
  - `tests/test_hang_guards.py tests/test_fidmech_worker.py`: 81 passed.
  - `tests/test_difffuzz.py tests/test_history_tests.py`: 130 passed.
- **Selected run at f34eeea976** (`MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base f97dd2d0c0 --run`; GitHub Actions run fid-mech-b3-f34eeea9-t825678; /tmp/b3/final-select2.log): 6 shards, 3 of them green. 3 tests failed, each a lint or inventory over the files this branch adds or changes, each fixed:
  1. `tests/test_history_tests.py::test_the_tree_passes` and `::test_the_command_line_lint_passes_on_the_tree`: the inventory still named `git show`. Regenerated with `tools/history_tests.py --write` (861f4b178e).
  2. `tests/test_difffuzz.py::test_every_fixture_is_read_or_excluded_with_a_reason`: the three bindings.json files are excluded as no-input, beside B1/B2's boundaries.json and ruled_out.json (861f4b178e).
  3. `tests/test_ownership_floor.py::test_ownership_json_is_of_the_traced_inputs`: docs/kernel/ownership.json records the git blob of each harness run.py. All five keys were traced again, the procedure of docs/kernel/kb-10d/REPORT.md section 14 (section 8a).
- **Earlier selected run at 22da737936:** its fast first stage failed `tests/test_lineage_lint.py::test_history_revisions_are_content_addressed`. frozen_diff handed the saved commit id to git, and the GitHub export rewrites commits. Fixed in 3a29c612e9: bindings.json pins run.py's blob (`run_py_blob`), the diff reads that blob, and `frozen_from` is a record only.
- **Final selected run on the committed final code:** section 8b.

### 8a. Ownership re-trace (89f865f36e)

The procedure of docs/kernel/kb-10d/REPORT.md section 14, as script /tmp/b3/retrace.sh (log /tmp/b3/retrace.log, exit 0, 11:16:57Z to 13:02:07Z):
- `zsh iso.sh own-b3-<key> 8G -- uv run python tools/ownership_trace.py run <key> --out /tmp/b3/own --jobs 4` per key: preparedness 239, RSP 126, agent-policy 42, eligibility 80 and safety framework 247 units. All 734 end `rc=0`, none with another code.
- Then `verdict --traces /tmp/b3/own --out docs/kernel` and `passing-functions --traces /tmp/b3/own --out docs/kernel/kb-10d/functions-under-passing.json`.
- **Totals unchanged:** RSP 100/126, preparedness 228/239, safety framework 244/262, agent-policy 0/42, eligibility 269/269, the figures of kb-10d section 14.
- docs/kernel/ownership.json changes only the three run.py blob ids; ownership.md is unchanged.
- functions-under-passing.json moves the item counts of one function, the lambda inside `ve/backends/lean_service.py:executable_sha256`, between keys. Which fresh-process unit first hashes the Lean binary varies between runs; this is no decision function.

### 8b. Final selected run (committed code, 89f865f36e)

`MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base f97dd2d0c0 --run`; GitHub Actions run fid-mech-b3-89f865f3-t834151; log /tmp/b3/final-select3.log; exit 0 (/tmp/b3/final-select3.log.rc).
- The fast first stage passed in 243 s.
- 227 units in 6 shards: SHARD 1/6 45 passed, 2/6 35, 3/6 38, 4/6 37, 5/6 36, 6/6 36. Every shard exits 0.
- This run includes the nine condition and new test files, the three live adapter tests (Lean), tests/test_rsp_fidelity_fix.py, tests/test_pf_fidelity_fix.py, tests/test_safety_framework.py (FSF `run.main(["--check"])`), tests/test_ownership_floor.py, tests/test_difffuzz.py, tests/test_history_tests.py, tests/test_lineage_lint.py and tests/test_hang_guards.py.
- Only this REPORT.md is committed after it.

**Pre-existing failures (main-known-red.txt):** none met; no selected test failed in the final run.

## 9. Decisions inside the plan (each the conservative or narrower reading; no DRI question)

1. **Item_predicates' inline kinds and answer()'s matching inline literals moved to bindings** (INLINE_ITEMS, CATCH_ALL_OWN). They map item kinds to predicates (2a's rule), and leaving answer()'s copies inline would leave two owners. Values unchanged.
2. **DM and SEC are read from SELECTION_ITEMS**, not stored twice.
3. **Atoms are intersected** over the models an item read (section 3).
4. **Fresh is the default worker** (section 4).
5. **Every other file in `usecases/<doc>/fidmech/` enters inputs_sha256** (actors.json, B4), not only the four 2e names: a resume then refuses on more changes, never on fewer.
6. **Uncommitted changes** enter inputs_sha256 as the sha256 of `git diff --binary HEAD` plus each untracked file's sha256. A plain `git diff` misses untracked files.
7. **The toy use case is fixture text** (`run.py.txt`), built into tmp_path by the tests. The only `.py` file under tests/data would otherwise have opened a new code-map area and reached every whole-tree Python lint.
8. **A sentinel failure resets the Lean pool**, as a timeout does, so the next run starts a fresh service.
9. **A batch whose first baseline errors is INVALID** with no mutant run: no limit can be set without a baseline.

## 10. DELTA

None. Python tooling and data only: no Lean line, no Rust line, no verdict, diagnostic or answer changed (results.json byte for byte, section 2), no decision path replaced. Trust +0. No signature reserved. No DELTA.md is written; there is no row.

## 11. Spec re-read

- plan 2a lists ↔ `TABLES` in tests/test_fidmech_bindings.py and section 1a, name by name. 2a's "COMPETITORS (a list)", "SOME_HIGH_LEVEL (a set)" and "ALL_OF (a set)" ↔ test_the_loader_rebuilds_the_exact_python_types_of_the_literals.
- plan 2a "sha256 ... pinned in tests/test_fidmech_bindings.py, not inside the file" ↔ `PINNED` (the file holds no hash of itself).
- plan 6 table: RSP `run()["comparison"][*].ve`; PF `ve` plus soft (and, corrected by point 12, no release field); FSF the comparison main() builds with the D2/D3 answers ↔ `ANSWER_FIELDS` and `with_comparison`.
- plan 6 isolation bullets (purge, fresh names, never main(), never module globals; sentinels first/every 20/last; INVALID and re-queue once; batch INVALID when first and last differ; 10x timeout; timeout or exception is error) ↔ `worker.run_batch`, `Worker.run` and the worker tests.
- plan 2e record fields and vocabulary ↔ `RECORD_KEYS` and `VOCABULARY`. The kill rule's "move to or from UNDECIDED ... inconclusive, never killed" ↔ `kernel_verdict`. The inputs list ↔ `INPUT_KEYS` and `collect_inputs`.
- Opus round 2 point 6 sources (RSP choices[*].rules, FSF details["rules"], PF selected_rules) ↔ `rules_of`. Point 12's VE facts ↔ section 1a and section 3.

## 12. Notes for the DRI

- **GOVERNANCE_FINDING (FSF)** stays in code: a single atom the GOV item removes from its case. If blind re-binding (item 33) should vary it, it would move to bindings.json in that row.
- **FSF's run() also runs variants() and the default-sensitivity pass** for every mutant (section 3). Splitting run() would cut each FSF mutant's cost, but it changes the run.py decision path, so it is not done here.
- **K on RSP f20-notify-board must→should reads `survived`** in the timing probe (section 4). This is a measured flip-force survivor of one mutant, not a plant figure.
- **The code map (docs/codemap/tools__fidmech.md) is not regenerated in this branch.** It is advisory on branches and regenerated on merge (`regen_generated --check`: "WARN: codemap is stale (regenerated on merge)"), and a branch rewrite would also pick up areas already stale on main.

## 13. Review fix (fid-mech-b3-review.final.md, reviewed b61bbd5db6)

**F1 (B), `kernel_verdict` scored a move to FSF's UNKNOWN as a kill.** FSF writes its undecided answers as `UNKNOWN` (N1 `run.py:733`; premises `run.py:262` via the projection; S1-<level> `severity_and_dates.py:150`; S4 `:180`; D1 and D3 `:234`), which the old table (`UNDECIDED`, `NOT RUN`) did not know.

- **Class:** a spelling of the third value that a document writes into an answer field and the kill rule does not recognise. That covers a new document, a new suffix (`UNDECIDED-faithful`, `resource limit: ...`) and a different word.
- **Fix (one table):** `records.UNDECIDED` now lists every spelling: UNDECIDED, UNKNOWN, NOT RUN, `resource limit` and `resource-limit`. Each counts alone or followed by `-`, `:`, a space or `(`. No other file in tools/fidmech decides whether an answer is undecided.
- **Guard for the class:** `test_every_third_value_spelling_in_an_adapted_documents_sources_is_recognised_by_the_kill_rule` checks the sources of every document in `adapters.DOCUMENTS`. It reads every string constant (Python's `ast`, docstrings left out) that names a third value: unknown, undecided, not run, resource limit, timeout, exhausted, budget, inconclusive, undetermined or unresolved. Each one must either be recognised by the kill rule or be listed in `NOT_ANSWERS` with its reason (result-dict and summary keys, reason texts beside an UNDECIDED answer, error-message fragments). A new adapter is read automatically.
- **Regression tests (tests/test_fidmech_records.py):**
  - `test_the_review_probe_f1_an_fsf_answer_moving_to_unknown_is_inconclusive` (PROBE F1: it fails before the fix, `killed`, and passes after it);
  - `test_a_move_to_or_from_every_third_value_spelling_is_inconclusive_never_a_kill` (7 spellings x flat, premises and parts shapes, both directions);
  - `test_fsfs_own_undecided_answers_on_its_committed_results_are_inconclusive` (end to end through `adapters.project` on the committed FSF results.json: N1, S1-L1, S4, D1, D3, G6 premises, NOT RUN; a decided change still kills);
  - `test_a_decided_string_that_only_contains_a_third_value_word_still_kills` (no over-matching);
  - the source guard above.
- **Seeded bugs:** S16-S18 (section 7).
- **Languages:** Python only, so no Lean or Rust mirror applies. results.json is unchanged.
- **DELTA:** still none. The K verdict is mutation-testing tooling that this batch adds; no VE verdict, diagnostic or answer changes.

**Test runs on the fix (92f27d2740):**
- `zsh mac-pytest.sh --select -- --base f97dd2d0c0 --run` on GitHub Actions, run fid-mech-b3-92f27d27-t839059, log /tmp/fm_b3_select.log, exit 0:
  - the cheap units ran first and passed in 174 s;
  - 201 units ran in 3 shards (83, 62 and 56), all passed;
  - 14 test files of more than 120 s, selected only for weak reasons, are deferred to the chain gate.
- `lake build` passed (1475 jobs), and `python3 lean/audit.py` passed (896 files, 10116 theorems).
- tests/test_fidmech_records.py: 59 passed.
- Pre-existing failures (main-known-red.txt): none was selected, and none failed.
- Not run here: the full gate and the trust_mutants sweep (no Lean change).

**Notes (C, not filed):** they stay as the review records them; this fix changes none of them.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer, schema or route is added or changed; the worker calls the use cases' run() and reads only their Python output.
2. PASS: section 1 maps every DO item and plan row to its commit and test. Grep of the diff: no Python copy of a Lean decision, no new report test (the evidence files are read by no test), no authority switch.
3. PASS: 18 seeded bugs, each failing a named test (section 7, seeded-bugs.json). The hash, sentinel and timeout comparators each fail on a changed value: S1, S8, S10.
4. PASS: no Lean or Rust changed. Python valid inputs still pass: the three live adapter tests equal results.json, and run.py --check is green on all three documents (section 2).
5. PASS: inputs are refused by name. Malformed bindings: test_a_malformed_bindings_file_is_refused_by_name[8], test_a_value_of_the_wrong_shape_is_refused_with_its_path[7]. Wrong record fields: test_a_verdict_outside_its_vocabulary_or_a_missing_one_is_refused[5]. An edit outside the tree, a duplicate mutant id or an unknown document: test_an_edit_outside_the_tree_and_duplicate_mutant_ids_are_refused.
6. PASS: the evidence is saved in this directory. The commit list is `git log --oneline --no-merges main..HEAD`; the scope base is `git merge-base HEAD main` (f97dd2d0c0). The full gate is the chain's, on the final HEAD.
7. PASS: no DELTA row and no trust growth (section 10); trust_mutants plan 0 definitions. The worker's status fields are tested on each error exit: timeout, exception, SystemExit, a sentinel failure, a first baseline error (`Batch("INVALID", ...)`).
8. PASS: no user-visible output changed: results.json byte for byte (run-check.txt); no CLI of `ve` changed.
9. PASS: select_tests selects all nine condition and new files (section 1). A seeded change selects its test: S15 in usecases/safety-framework/run.py, and test_fidmech_adapters.py is in the plan.
10. N.A.: no Lean statement or proof.
11. PASS: the deadline wraps the whole mutant run (the alarm around evaluate_tree, or the child's timeout). Tests use an injected clock and HANG_TIMEOUT, no sleep: test_a_run_past_ten_times_the_baseline_is_an_error, test_the_real_alarm_raises_the_timeout_in_the_main_thread. tests/test_hang_guards.py passes.
12. PASS: no ve/ or Lean code changed. run.py --check takes the same time within load noise (RSP 261 s → 320 s, PF 1782 s → 1502 s, FSF 152 s → 166 s on a shared VM; run-check.txt). The loader runs once per import.
13. PASS: no test removed or renamed against main. `(cd lean && lake build) && uv run python tools/gate_collection.py --check --prebuilt` exits 0: "35662 collected, 35567 at f97dd2d0c0; 95 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers" (/tmp/b3/gatecoll.log).
14. PASS: opposite directions are tested: accepted and refused types; sentinel ok and INVALID; under and over the limit; killed, survived and inconclusive; hash same and changed. Every count in this report names its command or file. Spec re-read: section 11.
15. PASS:
    - no overclaim: "every"/"all"/"unchanged" in this report each cite a test or file;
    - no silent cut: all four deliverables are built;
    - every new check can fail: section 7;
    - limits are charged before work: N.A. for budgets. The only limit is the per-mutant timeout, armed before the run (test_a_raised_timeout_is_an_error_and_resets_the_lean_pool).
