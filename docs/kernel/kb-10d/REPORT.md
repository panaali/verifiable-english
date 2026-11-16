# kb-10d: the per-answer Lean ownership test in the repo, its floor, the measure and the words

Status: built, review F1 and F2 fixed (section 13); no DRI signature needed (no DELTA row). Head: see `git log -1` of feature/kb-10d (this file is committed with it).
What changed: `tools/ownership_trace.py` traces every item of the five frozen keys in its own process and writes
docs/kernel/ownership.json (RSP 100/126, Preparedness 228/239, safety framework 244/262, agent-policy 0/42,
eligibility 269/269 answers pass); `tests/test_ownership_floor.py` makes those counts a floor; the public wording
now says what the trace shows. Open: every conflict answer, agent-policy, and the risk route's answers (below). No Lean change.

SIZE: 922 product (tools/ownership_trace.py 910, tools/ownership-decision-functions.json 12), 405 + 37 tests (tests/test_ownership_floor.py; the F2 test in tests/test_keyed_answers_authority.py), about 160 other hand-written lines (this report, ALLOWANCES.md's table, the six wording edits).

## 1. What was built (task file, step by step)

| Task line | Delivered by | Evidence |
|---|---|---|
| Step 1: `tools/ownership_trace.py`, one FRESH process per item, `sys.setprofile`, every ve/ function, every Lean kind and mode, value, equals the frozen key | `trace <key> <unit> <out>` (the harness is imported under the profile too); `run <key> --out DIR --jobs N` (at most 4; refuses more) | the five runs below, each `zsh manage-agents/iso.sh own-<key> 8G -- uv run python tools/ownership_trace.py run <key> --out /tmp/own/full2 --jobs 4`: 126, 42, 80, 247 and 239 units, `fails=0` each (/tmp/own/full2.log) |
| the single relay | `LeanServicePool.run_bound` and `LeanService.run_bound` (`ve/backends/relay.py`'s `rows`, `decide`, `answer`, `decide_once` all reach Lean through them); each case's mode, kind, environment profiles and sending harness function are counted. A call of `ve/backends/lean.py`'s one-shot `run`, `run_route_cases` or `run_english_cases` fails criterion 2 (none ran) | `Recorder.wrap`, `UNRELAYED` |
| Harnesses without a per-item answer function | eligibility: no per-item function; its unit is one profile (`main --profiles P --no-single-shot --no-mutants --no-write`), 80 units for 269 scored questions. safety framework: `run` answers in a loop; the unit of an item is that loop's body for it; N1-N3 (`family_n` reads every item's evaluation) are one unit, the whole loop; S is `family_s(d2())`, D is `d3()`. Preparedness: N3 (`dead_rules`) reads every other answer, so its unit runs them all. agent-policy: `check.run(actions={a}, level=False)` per action (the harness's own selection); its 42 scored actions (M1/M2) are its items, its policy section is not scored per item by the harness and is not counted. No harness was changed | adapters in tools/ownership_trace.py |
| Step 2: three criteria, the decision functions in ONE place with a reason each | tools/ownership-decision-functions.json (`NormDocument.selection`, `outcome`, `_expand`, `selected_rules`, `conflict_targets`, `_check_conflict_python`, every method of `_Evaluator`; ve/softnorms.py has no status function of its own on the Lean path since kb-10b: its two Python fallbacks run listed functions); criterion 2 reads tools/kernel-paths.json (kinds, `uncovered`, `nonverdict`, `untied_kinds`, tier, theorem listed); criterion 3 reads the harness's own comparison and PLAN.md section 12's entries (`plan12_entries`, one reader of both forms a plan writes) | `tests/test_ownership_floor.py::test_each_listed_decision_function_exists_and_has_a_reason`, `::test_criterion_two_reads_kinds_families_and_the_relay`, `::test_criterion_three_accepts_an_agreeing_value_or_a_difference_plan_12_records` |
| docs/kernel/ownership.json, ownership.md | `verdict --traces /tmp/own/full4 --out docs/kernel` (all five keys traced again after the merge of main, section 14; before it /tmp/own/full3, /tmp/own/full2 with the five units section 13 traced again) | `::test_every_item_of_the_five_keys_is_accounted_for`, `::test_the_totals_are_the_items_that_pass` |
| Step 3: the floor test, the stale check by tree hash, the fast re-trace | docs/kernel/ownership-floor.json; `::test_no_key_falls_below_its_floor`, `::test_the_floor_falls_only_with_a_signed_allowance`, `::test_ownership_json_is_of_the_traced_inputs` (git blob ids of ve/norms.py, ve/evaluate.py, ve/softnorms.py, ve/soft_route.py and the five harness run files, agent-policy's being check.py), `::test_three_passing_items_per_key_still_pass` (12 units, about 2 minutes) | `uv run pytest -q tests/test_ownership_floor.py` on the final tool: 19 passed in 104.09 s (/tmp/own/floor-test2.log) |
| The floor falls only with a signed ALLOWANCES.md line | docs/kernel/ALLOWANCES.md, new "Ownership floor" table; the test reads each key's last row | `::test_a_fall_without_the_architect_seat_is_refused_and_a_rise_needs_no_signature` |
| Seeded bugs (a) and (b), docs/kernel/kb-10d/seeded-bugs.json | (a) RSP's `selected` through `NormDocument.selected_rules`: `::test_ownership_json_is_of_the_traced_inputs` and `::test_three_passing_items_per_key_still_pass` fail (A-T0/ARG1 fails criterion 1); (b) soft-selected `uncovered` in a scratch registry: criterion 2 fails exactly the 537 passing items whose value is a soft-selected answer | seeded-bugs.json; section 6 |
| Step 4: the measure before and after kb-10 | section 4 | docs/kernel/kb-10d/trust-measure.json |
| Step 4: the wording | README.md, docs/ARCHITECTURE.md (two places), AGENTS.md, the three safety-framework READMEs | section 5 |

## 2. Totals per key (docs/kernel/ownership.json)

| key | items | pass | fail (1) | fail (2) | fail (3) |
|---|---:|---:|---:|---:|---:|
| anthropic-rsp | 126 | 100 | 8 | 15 | 3 |
| openai-preparedness | 239 | 228 | 8 | 3 | 0 |
| safety-framework | 262 | 244 | 6 | 12 | 0 |
| agent-policy | 42 | 0 | 42 | 0 | 0 |
| eligibility | 269 | 269 | 0 | 0 | 0 |

An item is counted once, at its first failing criterion. The first measured run (RESULT.md, VE main 9be13b93de)
counted 8 of RSP's 126; kb-8 (quantity), kb-10b (soft-selected) and kb-10c moved the rest.

Every traced value equals the value of the harness's committed results.json (`reproduces` in each trace record);
an item whose trace differed would fail criterion 3.

## 3. Every item that fails, with its reason (from ownership.json)

The conflict answers fail criterion 1 through Python's conflict search, not through a verdict Python reports:
`ve.soft_route.decide_soft_conflict` calls `norms._find_conflict` (which evaluates the conflict targets with
`_Evaluator`) and `norms._prove_targets` → `_generator_targets` → `NormDocument.conflict_targets` (which builds
`selection`, `_expand` and, in Preparedness, `outcome`). In RSP and Preparedness Lean's `soft-conflict` gives the
verdict. In the safety framework `soft-conflict` only confirms CONFLICT and fills the side field
`w1_without_premises`: CONFLICT-FREE comes from `refute`'s replayed entailment certificates over goals Python builds
from `conflict_targets`, and a cluster with no rules left is CONFLICT-FREE with no Lean call (`cluster_conflict`).
The test counts any run of a decision function, so these stay Python's until the search stops building them (first callers are in
each item's `criteria.1.first_callers`).
<!-- the tables below are ownership.json's failing items, grouped by reason -->

**anthropic-rsp** (26 fail):

| items | criterion | function, kind or value that fails it |
|---|---:|---|
| C-doc, C1, C2, C3, C4, C5, C6, C7 | 1 | decision functions ran: NormDocument._expand, NormDocument.conflict_targets, NormDocument.selection, _Evaluator.* |
| D6a, D7 | 3 | value "UNDECIDED" differs from the key "NONE"; no PLAN.md section 12 entry gives it as the item's answer (item 17 names them faithful UNDECIDED, not an answer) |
| D6b | 3 | value "UNDECIDED" differs from the key "SOME(bound)"; no PLAN.md section 12 entry gives it as the item's answer |
| G4, G5, G6, K10, K9, N4, N5 | 2 | no Lean answer gives the value (the harness answers UNDECIDED itself) |
| S1-T1, S1-T2, S1-T3, S1-T4, S2, S3, S4, S5 | 2 | no kernel path lists a theorem for risk kind risk-decision (paths: risk (candidate)), sent by d2 |

**openai-preparedness** (11 fail):

| items | criterion | function, kind or value that fails it |
|---|---:|---|
| C-doc, C1, C2, C3, C4, C5, C6, N3 | 1 | decision functions ran: NormDocument._expand, NormDocument.conflict_targets, NormDocument.outcome, NormDocument.selection, _Evaluator.* (N3's unit answers every item, the conflicts included) |
| S6, S7, S8 | 2 | no kernel path lists a theorem for risk kind risk-decision (paths: risk (candidate)), sent by risk_probe |

**safety-framework** (18 fail):

| items | criterion | function, kind or value that fails it |
|---|---:|---|
| C-doc, C2, C3 | 1 | decision functions ran: NormDocument._expand, NormDocument.conflict_targets, NormDocument.selection, _Evaluator.* |
| C1, C4, C5 | 1 | decision functions ran: NormDocument._expand, NormDocument.conflict_targets, NormDocument.selection |
| S1-L1 … S1-L7, S2, S3, S4, S5, S6 | 2 | no kernel path lists a theorem for risk kind risk-decision (paths: risk (candidate)), sent by risk_run |

**agent-policy** (42 fail): every action, criterion 1. The harness calls `NormDocument.selection` and
`selected_rules` itself (`check.py` `analyse_action`) and `NormDocument.outcome` (`_complete`, 41 actions), which run
`_expand` and `_Evaluator`. Not a soft-rule document: a hard norm document whose selection the harness reads from
Python directly.

## 4. The trust measure before and after kb-10 (baseline section 3)

Before: b3431f71df, the parent of the kb-10a merge (bb2c8d4604); its Lean service built in a scratch worktree
(`lake build ve_service`, 6.5 min warm). Now: this branch (no Lean change from main da0822ae80).

Keyed Lean lines and kernel lines (docs/kernel/closure-baseline.json): keyed_lines 16,150 → 16,545; kernel_lines
9,504 → 10,083; keyed_kernel_lines 9,504 → 10,083. `tools/kernel_closure.py --check docs/kernel/closure-baseline.json`
on this branch: `PASS: kernel 10083 <= 10083`, `PASS: verdict writers outside the kernel 56 <= 56` (/tmp/own/kclosure.log).

ve/ functions and function-body lines that run under each key's whole harness (py_under.py's method:
`tools/ownership_trace.py under <key>`, the harness's own check against its committed results.json, in one
process; checked against `py_under.py` itself on RSP: 708 functions, 7,265 lines both), and the listed decision
functions among them (distinct code objects):

| key | ve/ functions / lines before | now | decision functions before (listed entries) | now | answers with one now |
|---|---:|---:|---|---|---:|
| anthropic-rsp | 693 / 7,066 | 708 / 7,265 | 15: NormDocument._expand, NormDocument.conflict_targets, NormDocument.outcome, NormDocument.selected_rules, NormDocument.selection, _Evaluator (methods), _check_conflict_python | 11: NormDocument._expand, NormDocument.conflict_targets, NormDocument.selection, _Evaluator (methods) | 8 |
| openai-preparedness | 688 / 7,024 | 708 / 7,284 | 15: NormDocument._expand, NormDocument.conflict_targets, NormDocument.outcome, NormDocument.selected_rules, NormDocument.selection, _Evaluator (methods), _check_conflict_python | 12: NormDocument._expand, NormDocument.conflict_targets, NormDocument.outcome, NormDocument.selection, _Evaluator (methods) | 8 |
| safety-framework | 693 / 7,037 | 710 / 7,255 | 15: NormDocument._expand, NormDocument.conflict_targets, NormDocument.outcome, NormDocument.selected_rules, NormDocument.selection, _Evaluator (methods), _check_conflict_python | 11: NormDocument._expand, NormDocument.conflict_targets, NormDocument.selection, _Evaluator (methods) | 6 |
| agent-policy | 583 / 5,799 | 583 / 5,828 | 14: NormDocument._expand, NormDocument.conflict_targets, NormDocument.outcome, NormDocument.selected_rules, NormDocument.selection, _Evaluator (methods) | 14: NormDocument._expand, NormDocument.conflict_targets, NormDocument.outcome, NormDocument.selected_rules, NormDocument.selection, _Evaluator (methods) | 42 |
| eligibility | 446 / 4,218 | 446 / 4,249 | 0: none | 0: none | 0 |

The whole-harness figures include each harness's mutants and narrowing reruns (not eligibility's). Before, every soft-rule harness ran `outcome`, `selected_rules` and `_check_conflict_python`; now none does: what is left (`selection`, `_expand`, `conflict_targets`, `_Evaluator`, and `outcome` in Preparedness, through `conflict_targets`) runs only in the conflict search. agent-policy is unchanged (kb-10 did not touch hard norm documents). The function counts rise by 15 to 20 per soft-rule harness: 25 functions are new under each (the relay and binding of soft-selected and soft-conflict: `SoftenedNormDocument._selected_row`, `_ask_rows`, `selected_at`, `bind_selected`, `soft_route.decide_soft_conflict`, `check_soft_conflict`, `bind_conflict`, …) and 6 to 11 are gone (`NormDocument.outcome`, `selected_rules`, `_check_conflict_python`, `check_conflict`, …). Agreement of the checks: RSP, Preparedness and the safety framework's `--check` pass both times; agent-policy's compared fields are equal both times; eligibility differs from its committed results.json in english, probes and (mutants left out) summary both times (section 9).

## 5. The words

Replaced: README.md ("Python decides which rules a case selects, a completed outcome and every conflict"),
docs/ARCHITECTURE.md section 1 and section 4 (*Norm documents with soft rules*), the "How these answers are computed
today" paragraph of the three safety-framework READMEs. Each now says Lean decides selection and completed
outcomes, says which Lean answer gives each harness's conflict verdicts (`soft-conflict` in RSP and Preparedness;
in the safety framework `soft-conflict` for CONFLICT and `refute` for CONFLICT-FREE, with no Lean call for a
cluster with no rules left; section 13, F2), and that the conflict search still runs Python's conflict targets,
selection formulas and evaluator (the C family fails criterion 1 in every key, so that part of the sentence stays,
restated); each quotes only ownership.json's per-answer counts. AGENTS.md's "Not yet true for soft-rule norm
documents" stays as a caveat, narrowed to "soft-rule conflicts and agent-policy" and pointing at ownership.md (it
must stay under 6,000 bytes: `tests/test_repo_map.py`). `tests/test_keyed_answers_authority.py::test_the_wording_has_one_owner`
still passes (each page links keyed-answers.md).

## 6. Seeded bugs (docs/kernel/kb-10d/seeded-bugs.json; each planted, its test run, then removed)

| id | file | bug | test that fails |
|---|---|---|---|
| a | usecases/anthropic-rsp/run.py | `selected` calls `NormDocument.selected_rules` (Python's path) | `test_ownership_json_is_of_the_traced_inputs`, `test_three_passing_items_per_key_still_pass` (2 failed) |
| b | scratch copy of tools/kernel-paths.json | soft-selected listed `uncovered` (and `nonverdict`; the path a candidate) | `test_a_kind_the_registry_no_longer_covers_fails_criterion_two` asserts criterion 2 fails those 537 items and keeps 301 |
| S1 | tools/ownership_trace.py | `decision_hits` ignores code nested in a listed function | `test_decision_functions_match_functions_and_their_nested_code_not_the_class_body` |
| S2 | tools/ownership_trace.py | `kind_problem` ignores `uncovered` | `test_a_kind_the_registry_no_longer_covers_fails_criterion_two` |
| S3 | tools/ownership_trace.py | a family-qualified untied kind never fails | `test_criterion_two_reads_kinds_families_and_the_relay` |
| S4 | tools/ownership_trace.py | `blob_id` ignores the content | `test_a_changed_traced_input_makes_ownership_json_stale` |
| S5 | tools/ownership_trace.py | criterion 3 accepts any deviation text | `test_criterion_three_accepts_an_agreeing_value_or_a_difference_plan_12_records` |
| S6 | tools/ownership_trace.py | `plan12_entries` reads no "Key: … Entry: **…**" bullet (review F1's class) | `test_plan12_entries_reads_the_table_and_the_bullet_forms`, `test_the_real_plans_entries_are_read`, `test_every_plan12_entry_the_value_equals_is_recorded`, `test_the_safety_framework_adapter_records_plan_12_item_27` (4 failed) |
| S7 | tools/ownership_trace.py | `same_key` byte for byte (`∧` against `&`) | `test_plan12_entries_reads_the_table_and_the_bullet_forms`, `test_every_plan12_entry_the_value_equals_is_recorded` (2 failed) |
| S8 | tools/ownership_trace.py | an entry recorded although the case's premises fail on the model | `test_the_safety_framework_adapter_records_plan_12_item_27` |
| S9 | docs/kernel/ownership.json | the ownership.json of 30973716f3 | `test_every_plan12_entry_the_value_equals_is_recorded`, `test_the_safety_framework_adapter_records_plan_12_item_27` (2 failed) |
| S10 | docs/kernel/kb-10d/functions-under-passing.json | the file of 30973716f3 (a function counted once per code object) | `test_functions_under_passing_count_each_passing_item_at_most_once` |
| S11 | usecases/safety-framework/README.md | the README of 30973716f3 | `tests/test_keyed_answers_authority.py::test_no_document_says_soft_conflict_gives_a_conflict_free_it_does_not_give` |
| S12 | tests/test_ownership_floor.py | `lowest_floors` accepts a second "-" row for a key | `test_a_fall_without_the_architect_seat_is_refused_and_a_rise_needs_no_signature` |

Test selection: a seeded change to ve/norms.py and one to usecases/anthropic-rsp/run.py each select
tests/test_ownership_floor.py (`tools/select_tests.py --paths … --explain`: "imports … (static); names … (static)").

## 7. The ve/ functions under passing answers that are not plain encoding or decoding (input of the next step)

docs/kernel/kb-10d/functions-under-passing.json lists all 763 functions that ran under a passing item, with the
keys and item counts. The ones that compute something:

| function(s) | file | what it computes |
|---|---|---|
| `prove_entailment`, `_Searcher.*` | ve/entailment.py | Python's tableau prover: the entailment certificates `route certificate` replays (T, N1, C, S4) |
| `_check_certificate_python`, `_Replayer.replay` | ve/entailment.py | Python's own replay of a certificate it found, before Lean's (the generator's self-check; not reported) |
| `_Search.*`, `search`, `farkas_closes`, `_fourier_motzkin`, `replay_trace` | ve/order.py | Python's order prover (Fourier-Motzkin, Farkas) and its self-replay, for order certificates Lean replays |
| `prove_quantity`, `quantity_countermodel`, `check_quantity_limits`, `elaborate_quantity` | ve/units.py | Python's quantity prover and limits, proposing what the `quantity` kinds check (T, D, S, eligibility) |
| `background`, `_validate_background_python`, `_fill_premises`, `_soft_premises`, `dependency_order` | ve/background.py | the background premises sent with a case, and Python's validation of them |
| `NormDocument.__init__`, `_regulated_closure`, `base_data`, `plain_wordings` | ve/norms.py | a norm document's derived structure (heights, regulated closure, base vocabulary) under every soft answer |
| `bind_soft_elaboration` (`_incompatible`, `_rank_above`), `check_soft_source` | ve/softnorms.py | the binding of Lean's elaboration: recomputes the incompatible pairs and the rank closure to compare with Lean's rows |
| `FiniteModel.from_dict`, `_decode`; `_validate_model`; `Environment.__init__`, `closure` | ve/model.py, ve/evaluate.py, ve/environment.py | model and vocabulary validation (closure of the declarations) before a case is sent |
| `EnglishParser.*`, `parse_english`, `_parse_w1`, `parse_quantity_sentence`, `_Derivations.*` | ve/english.py, ve/norm_english.py, ve/surface/time.py | the English readers that turn the use cases' sentences into formulas (translation) |
| eligibility's `Staged` prover (harness code, not ve/) over `prove_quantity` | usecases/eligibility/run.py | which step to prove next and the YES/NO/amount it proposes; Lean admits the document that carries it |

## 8. Acceptance

| Acceptance line | Tag | Result |
|---|---|---|
| five harnesses pass, results.json byte-identical | AGENT | RSP, Preparedness, safety framework: their own `run.py --check` passes (in `under`, before and now). agent-policy: `inputs`, `actions`, `policy`, `policy_summary`, `comparison`, `M8` equal results.json (as tests/test_agent_policy_rerun.py compares; M10 holds timings). eligibility: see section 9 (pre-existing) |
| ownership.json for five keys, every item accounted for | AGENT | `test_every_item_of_the_five_keys_is_accounted_for` |
| the two tests pass; each seeded bug fails the test named | AGENT | section 6 |
| selected tests and the kernel check pass unchanged | AGENT | kernel check: section 4; selected tests: `MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select -- --base da0822ae80 --run` on the committed HEAD 1d619233cd: exit 0, 2 shards on GitHub Actions (run kb-10d-1d619233-t780201, 1190 s; /tmp/own/select.start) |

## 9. Notes for the DRI

- eligibility's committed results.json is stale on main in two fields that are not scored answers: `english`
  (the refusal text now starts with `UnsupportedProfile: `) and `probes` (P3's conditional refusal text). The same
  two fields differ at b3431f71df; profiles, answers and summary are equal. Not fixed here (no harness change).
- The value sources of criterion 2 (`VALUE` in each adapter: which harness function's Lean answers the harness
  turns into the value) are a statement about each harness, each with its reason; the registry alone decides whether
  each kind passes. A family-qualified untied kind (route's closureNary) fails a case unless the case's profiles rule
  the family out (`nary@0` absent: `VE.Route.Run.route_gate` and `Gate.AllowedFamily`).
- Criterion 1 counts any run of a listed function, the conflict search's proposals included; that is the baseline's
  rule ("no call on its path"), so the conflict answers fail even where Lean checks the verdict (`soft-conflict`;
  `refute` for the safety framework's CONFLICT-FREE).
- The trace records were made by `run` in /tmp/own/full2 (not committed: about 30 MB), five safety-framework units
  traced again into a copy, /tmp/own/full3, for section 13; ownership.json keeps each
  item's value calls and decision hits, which is what the Lean-free tests re-judge.
- The traces' import of each harness runs under the profile, as py_under.py counts it.

## 10. Spec re-read

- Step 1 against SPEC (task file) "one FRESH Python process", "wrap the single relay", "record kind and mode per
  call", "processes in parallel only up to 4", "every run through iso.sh own-<key> 8G": `run` starts one
  `python tools/ownership_trace.py trace` per unit, `MAX_JOBS = 4`, each key's driver ran under `iso.sh own-<key> 8G`.
- Step 2 (1) against the task's list: the JSON has exactly its norms.py entries, `_Evaluator` (methods) and no
  softnorms.py entry, with the reason in its comment; (2) "a kind listed under a path's `uncovered` or `nonverdict`
  fails": `kind_problem` returns a failure for both before it looks for a theorem; "do not hard-code the list of
  kinds": no kind name is in the verdict code (the adapters' `VALUE` say where each harness reads its value; the
  registry decides). (3) "or the difference is recorded in that key's PLAN.md section 12 (cite the entry)": the
  citation is kept in `criteria.3.recorded` and checked against section 12's text (`plan12_cites`); every adapter
  that reads section 12 reads it through `plan12_entries` (the RSP table rows and the safety framework's
  "Key: … Entry: **…**" bullets), and Preparedness through its harness's `classify` citations.
- Step 3 against "compare a recorded tree hash of those files, not dates": git blob ids of the nine files; "first,
  middle, last of the passing ones": `_chosen`; "falls only with a line in docs/kernel/ALLOWANCES.md signed by the
  architect seat": `lowest_floors`.
- Step 4 against "quoting only the per-answer count of ownership.json (never a family tally)": each rewritten
  sentence quotes a key's passing count only; "If any family of any key still fails criterion 1, its sentence
  stays": the conflict caveat and AGENTS.md's caveat stay.
- Baseline section 2 criterion 1 "no call on its path": the import of the harness is traced too.

## 11. DELTA

None. No ve/, lean/ or rust/ code changed and no harness changed; the only output that changed is documentation.
No DELTA.md; no DRI signature is needed.

## 12. Not run

- tools/gate.py (the chain runs it on the final HEAD); trust_mutants (no Lean change).
- The eligibility harness's 32 mutants under the profile (they take hours in one process; the per-unit traces do not
  run them either).

## 13. Review fix (manage-agents kb-10d-review.final.md, commit 30973716f3)

| Finding | Fix | Regression tests |
|---|---|---|
| F1 (B): criterion 3 missed differences PLAN.md section 12 records (safety framework item 27: K2-L1/PROXIMITY, K2-L5/PROXIMITY ALL, G3 NONE), so the count was 241, not 244 | The class: an adapter read only a harness-specific subset of section 12 (the safety framework only run.py's `DEVIATIONS`, item 23). `plan12_entries` is now the one reader of section 12's entries in both forms a plan writes (a "Key deviation" table row, a "- **id.** Key: k. Entry: **a**." bullet), and the RSP and safety-framework adapters judge against it (`same_key` binds an entry to the frozen key; the safety framework's also needs the case's premises to hold on the model and a release condition to agree, as its `compare` does). Preparedness keeps its harness's `classify` citations; agent-policy and eligibility have no entry. The five safety-framework units with an entry (G3, K2-L1/PROXIMITY, K2-L5/PROXIMITY, C3, C-doc) were traced again (their functions and Lean calls are unchanged; only the recorded entry is); ownership.json, ownership.md, functions-under-passing.json regenerated; the floor rises to 244 (ALLOWANCES.md row, a rise, no signature). The failing reason now reads "no PLAN.md section 12 entry gives it as the item's answer" (true for RSP D6a, D6b, D7: item 17 names them faithful UNDECIDED, not an answer). Every place that quoted 241 now quotes 244 | `tests/test_ownership_floor.py::test_plan12_entries_reads_the_table_and_the_bullet_forms`, `::test_the_real_plans_entries_are_read`, `::test_every_plan12_entry_the_value_equals_is_recorded` (all five keys), `::test_the_safety_framework_adapter_records_plan_12_item_27` (PROBE F1) |
| F2 (A, text only): the wording said `soft-conflict` gives every CONFLICT-FREE answer, false for the safety framework (`refute`, or no Lean call for an empty cluster) | README.md, docs/ARCHITECTURE.md (sections 1 and 4), usecases/safety-framework/README.md and this report (sections 3, 5, 9) say which Lean answer gives each harness's conflict verdicts. The RSP and Preparedness READMEs were right and are unchanged | `tests/test_keyed_answers_authority.py::test_no_document_says_soft_conflict_gives_a_conflict_free_it_does_not_give` (PROBE F2 over every describing document, AGENTS.md and docs/kernel; the exempt READMEs are derived from each harness's `decide_soft_conflict(prove=True)` calls without `refute`) |

Also fixed from the review's notes: the module docstring cited a missing `ownership_verdict.py`; `lowest_floors`
refused no second "-" row for a key (an unsigned fall); `passing_functions` counted a function once per code object
of one qualified name (1,904 safety-framework items under one function, more than the key has). Not changed from the
notes: `check_premises` in the RSP value sources (no passing item depends on it alone, per the review),
`differs_from_results_json: null` in trust-measure.json, the staleness check's nine files, criterion 2 per unit.
Seeded bugs S6 to S12 (section 6). No DELTA row: no ve/, lean/, rust/ or harness code changed; the outputs that
changed are this tool's measurement (R10: a wrong number on the real tree, fixed) and documentation.

## 14. Re-trace after the merge of main (candidate gate dd2ddd8249)

The candidate gate failed `tests/test_ownership_floor.py::test_ownership_json_is_of_the_traced_inputs`: main's
58f1b0d260 (PF f7-evaluations' timed act) changed `usecases/openai-preparedness/run.py`, a traced input, and the
merge 7cba6155a1 took it without a new trace. All five keys were traced again on the merged tree (`run` per key,
`--jobs 4`, under `iso.sh own-<key> 8G`, into /tmp/own/full4: preparedness 239, RSP 126, agent-policy 42, eligibility 80 and safety framework
247 units, `fails=0` each; /tmp/own/full4.log), then `verdict --traces /tmp/own/full4 --out docs/kernel` and `passing-functions`
regenerated ownership.json, ownership.md and functions-under-passing.json. The totals are unchanged (RSP 100/126,
preparedness 228/239, safety framework 244/262, agent-policy 0/42, eligibility 269/269); what changed is the input
blob id, the registry id (main changed tools/kernel-paths.json), a few Lean call counts of the preparedness units,
and `commits`, now empty: the tracer records no commit since a8b38fec33 (no git call in the tracer).

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer, schema or route changed (the tool only reads them).
2. PASS: section 1 maps each task line to its commit artefact and test; grep of the diff: no ve/ change, no Python copy of a Lean decision, no new report test (ownership.json is a measurement read by the floor test the task asks for).
3. PASS: seeded bugs a, b, S1 to S5 (section 6, docs/kernel/kb-10d/seeded-bugs.json); the comparators refuse an empty and a changed input (`test_a_changed_traced_input_makes_ownership_json_stale`, `test_criterion_two_reads_kinds_families_and_the_relay` with no call).
4. PASS: the five harnesses' checks before and now (section 4, docs/kernel/kb-10d/trust-measure.json); every traced value equals results.json (`reproduces`).
5. N.A.: no relayed field is read; the trace records request fields only.
6. N.A. (gate evidence is the chain's); evidence numbers are saved in docs/kernel/kb-10d/ and ownership.json, not read from a live diff.
7. PASS: no DELTA row (section 11); no trust growth (`tools/kernel_closure.py --check`: PASS, section 4).
8. PASS: no product output changed (no ve/, lean/, harness change); the harness checks are unchanged before and now.
9. PASS: seeded changes to ve/norms.py and usecases/anthropic-rsp/run.py each select tests/test_ownership_floor.py (section 6).
10. N.A.: no Lean statement or proof.
11. N.A.: no budget or deadline; the tests wait with `HANG_TIMEOUT` (`test_three_passing_items_per_key_still_pass`).
12. N.A.: no product path changed; the fast test runs 12 units in about 2 minutes (19 tests in 104.09 s).
13. N.A.: no test removed or renamed.
14. PASS: opposite directions: `test_a_fall_without_the_architect_seat_is_refused_and_a_rise_needs_no_signature`, `test_a_kind_the_registry_no_longer_covers_fails_criterion_two` (fails the soft-selected items, keeps the 301 others), `test_criterion_three_accepts_an_agreeing_value_or_a_difference_plan_12_records` (accepts two, refuses four), `test_decision_functions_match_functions_and_their_nested_code_not_the_class_body`; every report figure names its command or file; spec re-read in section 10.
15. PASS: overclaim: "every", "no", "none" in sections 2 to 5 are counts of ownership.json or test names; nothing deferred is written as done (eligibility's stale fields are a note, not claimed equal); no deliverable cut; every new check has a seeded bug (section 6); no limit added.
