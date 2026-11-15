# kb-10b-switch: kb-10b steps (2)-(4), the switch of soft selection and outcomes to Lean

No DRI signature is reserved. DELTA row 2 (speed) is decided by rule (b) of reviews/dri-decisions-20261114-kb-10b-switch.md
item 1, "SIGNED by the DRI" on that condition: every harness is at most 1.15x its before value in both pairs. Rule (a)
(R4) fails on one Preparedness call that took 2.58 s wall. Row 1 cites R12.

Restart round (DRI decider 2026-11-14 19:50Z): the branch is rebased on local main 4a5d3460d3, which has kb-10e
(07a963f74d). It keeps the review-F1 loader fix. All five keys pass `--check` (or their frozen command) with
unchanged results, in two paired rounds against the base. The per-answer count on RSP is **99/126**, the same as
before the rebase, with the same rows and call sites. The DRI note's three items are done: the F1 cache-key test,
the F7 reset, and the F8 line. F8 is explained below.

SIZE: 225 product (about 55 of them moved from `ve/soft_route.py`), 419 tests, 580 other hand-written lines (added
lines, `git diff --numstat main...HEAD`. This REPORT and the generated or saved evidence files are not counted:
the code map, `tests/history-dependent.json`, `docs/usecases/keyed-answers.json`, `seeded-bugs.json`,
`evidence/*.json*`, `evidence/*.txt`, `ownership/per-item.tsv`, `ownership/called-from.json`). "Other" is the
evidence scripts under `evidence/scripts/` and `ownership/`, DELTA.md and `docs/usecases/keyed-answers.md`.

## Commits (`git log --oneline --no-merges main..HEAD`, oldest first)

| Commit | Part |
|---|---|
| 9d8a58a47 | (2) soft documents' selected rules and completed outcomes are Lean's `soft-selected` answers |
| 1b4892ce9 | (2) the relay and its binding live in `ve.softnorms` |
| 1daa873b9 | (3)-(4) first saved evidence (before the rebase), DELTA, seeded bugs, code map |
| 78f5655e6 | (2) the hand-built fallback imports no class-A body; `seed.py` builds pytest through `tools/nested_pytest.py` |
| dcec5d58e | (2) keyed-answers.md, its recorder and its test say and record `soft-selected` |
| 283bf4073 | REPORT of the first round (STOP: needs kb-10e) |
| f54983ab0, bb21306bd | review F1 of round 1: the scoped harness loader (`tests/usecase_scope.py`), code map |
| b10951d09 | restart: F1 cache-key test, F7 reset, seeded bugs l, m |
| e6591899a | restart: `seed.py` owns the loader bugs too, and all ten bugs re-run on the rebased code |
| 4c10d5b71 | restart: regenerated code map after the rebase (R12) |
| fba43bcdf, 1fb2efc7a | restart: evidence scripts (`split.py`/`count*.py` wrap the relay the document calls, review F2; `py_funcs.py`; `pair5.sh`; F8 probe) |
| cb7320345 | restart: the pair's call goes by kb-10e's soft-document handle (test, seeded bug n) |
| be7de5e99 … (last) | restart: wall times, ownership re-run, keyed-answers re-measure, `PYTHONPATH` fix of the pairing, saved evidence, DELTA, this REPORT |

Before the rebase these were b44f9ac7bf, ed16ff899f, e786674ec5, 59b5d24361, 4c2258bb62, 37e96491fb, 3fcb8f312b and bc5aa5a099.
The rebase conflicted only in generated code-map files. I took main's copy and regenerated them (4c10d5b71).
`usecases/openai-preparedness/run.py`: openai-preparedness-fidelity-fix-5 is on main (dc67245e0). This branch
changes only `completed` there, and the rebase kept both changes.

## Deliverables

| Task line | Commit | Evidence |
|---|---|---|
| (2) `selected_rules` and a new `outcome_at(predicate, model, values)` take their answers from `selected_at`, kept per (document, model identity: the model's `to_dict` JSON) | 9d8a58a47, 1b4892ce9 | `tests/test_kb10b_switch.py` (24 tests) |
| (2) grouping (architect ruling, section 2): one call per (document, model) at the pair's first question, every regulated predicate times every tuple, fixed order | 9d8a58a47 | `::test_one_call_per_document_and_model_sends_every_query_of_the_pair`, `::test_another_model_or_another_document_is_another_call`, `::test_same_environment_with_other_rules_is_another_document`, `::test_a_wire_dictionary_model_is_the_same_pair_as_its_finite_model` |
| (2) over Lean's query limit: per predicate, then the single query; never truncated, never answered from Python | 9d8a58a47 | `::test_over_the_query_limit_the_pair_is_asked_per_predicate`, `::test_over_the_limit_for_one_predicate_each_query_is_asked_alone_never_truncated`, `::test_within_the_limit_the_pair_is_one_call`, `::test_a_refusal_other_than_the_limit_is_raised_not_answered` |
| (2) the harnesses' `selected` and `completed` call them; no harness imports `_Evaluator` for these | 9d8a58a47 | `::test_the_harnesses_completed_is_outcome_at`. RSP and Preparedness no longer import `_Evaluator`. FSF keeps it only in `holds_at`, which sets a case model's decision atoms. |
| (2) a hand-built SoftenedNormDocument keeps the Python path and says so; no key builds one | 9d8a58a47, 78f5655e6 | `::test_a_document_without_its_soft_source_keeps_pythons_path`. The re-measured `docs/usecases/keyed-answers.json` has no `python selected_rules` and no `python outcome_at` under any of the three harnesses. |
| "make `selected_at` use kb-10e's soft-document handle if kb-10e did not already" | kb-10e did (its client sends every `soft-norms` `soft-selected` case by handle) | `::test_the_documents_call_names_its_soft_document_by_handle` (cb7320345): the document's one call is sent with `_Sent.soft`. |
| (3) the five keys, results byte-identical except wall time | rounds r1-r4 | below, `evidence/wall-times.txt` |
| (3) wall time of each safety-framework `--check`, before and after, same machine, same hour; 2.0x bound | rounds r1-r4 | below. All five harnesses ≤ 1.15x. |
| (4) before/after: the `ve/norms.py` and `ve/evaluate.py` functions that no longer run | phase B and r3 | below, `evidence/pyfuncs-summary.json` |
| Seeded bugs (a), (b) | `seed.py` re-run on the rebased code | below, `seeded-bugs.json` |
| Per-answer count (Nov 23 checkpoint) | 90ab752b7 | below, `ownership/` |
| Handle-table count | kb-10e's REPORT gives it | below |
| DRI note 2026-11-14: row 2 cell by (a)/(b)/(c); F1 test; F7 reset; F8 line | this round | DELTA row 2; `::test_same_environment_with_other_rules_is_another_document`; `tests/test_keyed_answers_authority.py::test_selection_and_outcome_are_leans_soft_selected`; "F8" below |

kb-10a's differential (item d): 0 mismatches, as kb-10b step (1) recorded (docs/kernel/kb-10b/REPORT.md). The step
(1) shadow found 0 mismatches in 180,587 calls, so no cell is listed as changed or unchanged.

## (3) The keys

Runs: `evidence/scripts/pair5.sh <round> [harness...]`. Each harness runs in the base worktree (main 4a5d3460d3)
and in this worktree at the same time, under `iso.sh`, with one Lean binary (this branch changes no Lean). The
commands are those of docs/kernel/frozen-keys-20261111.md, except that Preparedness runs its full `--check`, which
also compares the mutants and `results.json`, not `--base-only`.

- Every run exits 0: 20 runs in r1-r2 and 8 in r3-r4. After each round, neither worktree has a changed file
  (`git status --short`, last lines of each round in `evidence/wall-times.txt`). RSP prints `110 / 126` and
  Preparedness `236 / 239` on both sides.
- FSF and eligibility print the same lines on both sides. agent-policy differs only in its printed seconds (the
  two `time-r1-*.log` outputs compared with timings masked; the logs are under `/tmp/kb10bs/`, not saved).
- **Pairing fault found and fixed:** in the base worktree, the Preparedness and agent-policy scripts import `ve`
  from the venv's editable install, which points at this worktree. RSP, FSF and eligibility put their own root on
  `sys.path`. The r1 and r2 "before" runs of those two harnesses therefore ran the head's `ve`. Found with
  `python -v <script> --help` in the base worktree. `pair5.sh` now runs each side with `PYTHONPATH=<its worktree>`
  and prints the `ve` each side imports. Rounds r3 and r4 rerun those two pairs, and their lines show
  `ve=…-base/ve/__init__.py` on the base side. The same cause made the first round's Preparedness `py_under`
  "before" run record 0 functions.

No keyed cell changed, so task item (3)'s stop for a changed cell does not apply.

### Wall times (seconds, before → after; `evidence/wall-times.txt`)

| Harness | Pair 1 | Pair 2 | Rounds |
|---|---|---|---|
| RSP | 362.9 → 344.2 (0.95x) | 410.7 → 380.5 (0.93x) | r1, r2 |
| FSF | 142.1 → 128.1 (0.90x) | 199.9 → 181.7 (0.91x) | r1, r2 |
| Preparedness | 1535.1 → 1766.6 (1.15x) | 1517.0 → 1709.4 (1.13x) | r3, r4 |
| agent-policy | 166.0 → 167.7 (1.01x) | 203.9 → 201.8 (0.99x) | r3, r4 |
| eligibility | 251.3 → 249.7 (0.99x) | 241.1 → 241.5 (1.00x) | r1, r2 |

Before the rebase (no kb-10e), RSP was 1.89x and 2.07x (`evidence/wall-times-37e96491fb.txt`). With kb-10e's handle,
RSP and FSF are faster than the base, because the Python evaluation they no longer run cost more than the Lean
calls. Preparedness is 1.13-1.15x.

### The split (head only; `evidence/split-restart.jsonl`, `evidence/scripts/split.py`)

| Harness | wall | first `soft-selected` call per document | later calls | rest (Python, other Lean kinds) | longest call: wall / Lean CPU | calls over 1 s wall / over 2 s wall / over 1 s CPU |
|---|---|---|---|---|---|---|
| RSP | 476.4 s | 81 calls, 13.5 s | 377 calls, 7.1 s | 455.8 s | 0.678 s / 0.21 s | 0 / 0 / 0 |
| FSF | 250.6 s | 28 calls, 1.0 s | 614 calls, 6.8 s | 242.8 s | 0.267 s / 0.04 s | 0 / 0 / 0 |
| Preparedness | 2313.1 s | 1,125 calls, 152.2 s | 5,251 calls, 110.3 s | 2050.6 s | 2.582 s / 0.23 s | 8 / 1 / 0 |

These runs ran beside the other evidence runs (`evidence/scripts/phase_b.sh`, `evidence/phase-b.txt`), so their
wall times are not the paired figures above. RSP's later calls cost about 0.02 s each, against 0.78 s before kb-10e.
Lean CPU per call stays at most 0.23 s. Wall per call reaches 2.58 s once, so R4's absolute budget (at most 2 s
wall per check) does not hold on this evidence. DELTA row 2 therefore follows rule (b).

## (4) Functions that run, before and after (`evidence/pyfuncs-summary.json`, `evidence/scripts/py_funcs.py`, `pyfuncs_diff.py`)

The architect's `fable-team/architect/experiments/py_under.py` cannot be read from this worktree after the restart
(the directory is not visible). `py_funcs.py` asks the same question: which functions of the `ve` package run. It
uses `sys.monitoring` with each location disabled after its first hit. Base and head runs use `--check`, each side
with its own `ve` (`PYTHONPATH`). All six exit 0.

| Harness | `ve/norms.py` functions that no longer run | `ve/evaluate.py` |
|---|---|---|
| RSP | `NormDocument.outcome`, `NormDocument.selected_rules` (and its genexpr), `_instantiate` (and its genexpr), `_replace_term`, `_shift_term` (43 → 36) | 15 → 15: `_Evaluator` still runs for the C family (`_find_conflict`, kb-10c) |
| FSF | `NormDocument.outcome`, `NormDocument.selected_rules` (and its genexpr) (39 → 36) | 15 → 15: the C family, and `holds_at` while the harness builds a case model's decision atoms |
| Preparedness | `NormDocument.selected_rules` (and its genexpr) (39 → 37) | 15 → 15: the C family |

On Preparedness `NormDocument.outcome` still runs after the switch. Its callers in `ve/` are `conflict_targets`
(`ve/norms.py:588`), `_expand` (`:471`), `relayed()` (`:456`), the hand-built fallback of `outcome_at`
(`ve/softnorms.py:326`), and `ve/readings*.py`. `_instantiate` does not run (so `_expand` substitutes nothing), no
`readings*.py` function runs, and the re-measured keyed paths have no `python outcome_at`. The call is therefore
`conflict_targets` under `check_conflict` → `_check_conflict_python` (52 calls, `docs/usecases/keyed-answers.json`),
the C family (kb-10c). This is an inference from those three facts; `py_funcs.py` does not record call sites.

## The per-answer count (reviews/lean-ownership-baseline-20261112.md section 2), RSP key, this branch

Method: as reviews/lean-ownership-20261112/RESULT.md, one fresh process per item (`ownership/run_all.sh` under
`iso.sh kb10bs-ownership 16G`, `xargs -P 6`), on be7de5e99c (the rebased branch). The script
`ownership/trace_item_callers.py` is the DRI's `trace_item.py` plus the call chain into each decision function.
126 of 126 items ran, with 0 errors. `ownership/summarize.py` writes `ownership/per-item.tsv` and
`ownership/called-from.json`. **Both are identical to the files measured before the rebase** (`per-item.tsv`
byte-identical; `called-from.json` differs only by a final newline). So the table is unchanged:

| family | items | 1 clean | agrees (or recorded deviation) | passes | why not |
|---|---:|---:|---:|---:|---|
| T | 9 | 9 | 9 (T7 recorded deviation) | **9** | |
| S | 8 | 8 | 7 (S2 UNDECIDED) | 0 | criterion 2 kept as RESULT.md judged it (`risk`); see Notes |
| D | 9 | 9 | 6 (D6a, D6b, D7 UNDECIDED) | **6** | |
| A | 40 | 40 | 40 | **40** | |
| B | 12 | 12 | 12 | **12** | |
| K | 27 | 27 | 24 (K9, K10 UNDECIDED; K18 differs from the key, as on 9be13b93de) | **24** | |
| G | 8 | 8 | 5 (G4, G5, G6 UNDECIDED) | **5** | |
| N | 5 | 5 | 3 (N4, N5 UNDECIDED) | **3** | |
| C | 8 | 0 | 5 | 0 | `_check_conflict_python` (kb-10c) |
| total | 126 | 118 | 111 | **99** | |

Of the A/B/K/G/N items (92), none still calls a Python selection, outcome or `_Evaluator` function: criterion 1 is
clean on all 92 (`per-item.tsv`, empty `python_decision_calls`). The decision calls left are on the 8 C items, all
from `usecases/anthropic-rsp/run.py:_conflict:396` → `ve.norms.check_conflict` → `_check_conflict_python` →
`_find_conflict` (`_Evaluator`), and → `conflict_targets` → `NormDocument.selection`, `_expand`
(`ownership/called-from.json`). No keyed answer was changed.

Criterion 2 for A/B/K/G/N: the values come from `soft-selected`, whose wire theorem is kb-10a's (`SelectedSound.lean`).
Through the handle they come from kb-10e's prepared path, `soft_wire_selected_prepared`. The case model's
premises come from `metered` (kb-7). One point stays Python on these paths: the harness combines the deny and
allow answers (`holds = left and right`, the rule intersection, `default_sensitive`). Row kb-9 puts that
composition under one kernel row (architect ruling, section 5).

## Handle-table count

kb-10e's REPORT gives it (docs/kernel/kb-10e/REPORT.md, "Registrations under `maxHandles` = 64"): in the pair
order this switch uses, a Preparedness run makes **1,381 registrations for 1,125 documents, 1.23 per document**.
That is under 1.5, so no bound or eviction rule is proposed. This branch's own simulation before the rebase
(`evidence/handle-table.jsonl`) gives the same 1,381. `maxHandles` and the emptying rule are unchanged.

## The DRI note of 2026-11-14

- **F1 (cache key):** `tests/test_kb10b_switch.py::test_same_environment_with_other_rules_is_another_document`. Two soft
  documents share one environment and differ in their rules (`RULES` and `RULES[1:]`, without the strict rule
  `h`). At `b` the first selects `h` and the second `d`, and the test asserts two calls. Seeded bug l (the key
  built from the environment alone, `ve/softnorms.py:362`) fails it.
- **F7 (cache reset):** `tests/test_keyed_answers_authority.py::test_selection_and_outcome_are_leans_soft_selected`
  first replaces the process-wide `_SELECTIONS` with an empty one (monkeypatch). It is parametrized over which
  question comes first (`selected_rules` or `outcome_at`), so both of its cases ask the same module-scoped
  document. Seeded bug m (the reset removed) fails the second case: "1 failed, 1 passed".
- **F8 (FSF 642 calls against 641 shadow pairs):** explained. In one FSF run of the head code,
  `evidence/scripts/f8_pairs.py` installs step (1)'s own shadow recorders (record only) and a recorder on
  `ve.softnorms.selected_at`. The switch makes 642 calls on 642 distinct (document, model) pairs, the shadow
  recorders count 642 pairs, and the two sets are equal: 0 pairs outside the shadow, 0 repeated, 0 shadow pairs not
  asked (`evidence/f8-safety-framework.json`). The 641 was counted by step (1) on 6edb29d11c. Between that commit and
  this branch's first base, FSF fix-2 changed the harness's cases (8 commits under `usecases/safety-framework/`,
  among them 479d5850a "f20 pairs, FACTS, CASES (G8)"). The extra pair comes from the harness, not from the switch.
  I did not isolate which case adds it.
- **Review F2 (stale evidence scripts):** `split.py`, `count.py` and `count2.py` wrapped `ve.soft_route.selected_at`.
  Since 1b4892ce9 the document calls `ve.softnorms.selected_at`, so they would have counted nothing. They now wrap the
  latter, and the restart's split was measured with it.

## Seeded bugs (`seeded-bugs.json`; `evidence/scripts/seed.py [bug...]` plants each, runs one test, restores the file)

Product code changed only in Python. Each bug makes its named test fail (a failing test, not a collection error:
`nested_pytest.failed_test_run`). All were re-run on the rebased code.

| Bug | File | Fails |
|---|---|---|
| (a) the task's: a result row kept under the next query (`zip(queries[1:], results)`) | `ve/softnorms.py` | `tests/test_kb10b_switch.py::test_selected_rules_and_outcomes_are_leans_answers_at_each_tuple` |
| (b) the task's: `outcome_at` returns the truth of the selection | `ve/softnorms.py` | `::test_the_outcome_is_not_the_truth_of_the_selection` (kb-10a's three-rule fixture) |
| (h) the limit fallback compares the `code` | `ve/softnorms.py` | `::test_over_the_query_limit_the_pair_is_asked_per_predicate` |
| (i) every model shares one kept answer | `ve/softnorms.py` | `::test_another_model_or_another_document_is_another_call` |
| (j) the regulated predicates without rules left out of the query list | `ve/softnorms.py` | `::test_one_call_per_document_and_model_sends_every_query_of_the_pair` |
| (k) RSP's `completed` sends the tuple reversed | `usecases/anthropic-rsp/run.py` | `::test_the_harnesses_completed_is_outcome_at` |
| (l) review F1: the document key is the environment alone | `ve/softnorms.py` | `::test_same_environment_with_other_rules_is_another_document` |
| (m) review F7: the authority test does not reset the kept answers | `tests/test_keyed_answers_authority.py` | `tests/test_keyed_answers_authority.py::test_selection_and_outcome_are_leans_soft_selected` |
| (n) the case is not sent by handle (planted in kb-10e's client, a file this branch does not change) | `ve/backends/lean_service.py` | `::test_the_documents_call_names_its_soft_document_by_handle` |
| review-F1-modules, review-F1-path (round 1): the loader keeps a sibling module or a `sys.path` entry | `tests/usecase_scope.py` | `::test_a_harness_loads_its_own_siblings_and_leaves_none_behind` |

Task bug (c), the shadow comparing Python with Python, belongs to step (1) and is recorded in
docs/kernel/kb-10b/seeded-bugs.json.

## Tests

- `uv run pytest -q tests/test_kb10b_switch.py tests/test_keyed_answers_authority.py`: 33 passed after the F1 and F7
  changes. The handle test passed in a `-k` run (2 passed).
- Selected run and the other final checks: "Final runs" below.
- Not run: the full gate (the chain runs it), and trust_mutants (no Lean change, so build-checklist 13a and R16 do not
  apply; the light lane printed NOT only for the line count).
- Pre-existing failures (`manage-agents/main-known-red.txt`): none met (no test failed).

## Final runs (on 1afa9b5284, committed and clean; only this section was committed after them)

- Selected tests: `MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`. It ran on
  GitHub Actions in 6 shards (run kb-10b-switch-1afa9b52-t698009): exit 0, 308 units passed, 0 failed, recorded for
  tree a6a4220d38 (`git write-tree` of 1afa9b5284). The selection includes `tests/test_kb10b_switch.py`,
  `tests/test_keyed_answers_authority.py`, `tests/test_soft_selected.py`, `tests/test_soft_document_handles.py`,
  `tests/test_kb10_shadow.py`, `tests/test_relay_binding_inventory.py` and `tests/test_safetyfw_usecases.py`.
- `uv run python tools/regen_generated.py --check`: exit 0, "checked 41 entries".
- `uv run python tools/gate_collection.py --check --prebuilt`: exit 0, "35223 collected, 35197 at 4a5d3460d3; 27
  added, 1 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers".
- `uv run python tools/relay_mutation_gate.py`: exit 0, "50 routes, 155878 mutants, 0 failures".
- No test failed, so nothing from `main-known-red.txt` applies.

## Notes for the DRI

- Preparedness is 1.13-1.15x slower, and RSP and FSF are 0.90-0.95x. On Preparedness the 6,376 Lean calls take
  about 262 s (split), which is more than the Python evaluation they replace. kb-10e estimated about 189 s through the
  relay. Its trace counted 6,366 pairs; this run makes 6,376 because main's Preparedness changes after that trace add
  pairs.
- The pairing fault above (the Preparedness and agent-policy scripts import the editable install's `ve`) can affect
  any base/head comparison made with one shared venv. Any future paired measurement should set `PYTHONPATH` per
  side.
- Criterion 2 for family S: `lean/VE/Risk/Run.lean` has `risk_wire_scenario_sound` and `risk_wire_audit_sound`. RESULT.md
  judged that `risk` had no runner theorem. This report keeps S at 0 and does not re-judge it.
- Model construction over a soft base environment checks the soft background in Python (`ve.background._valid_soft`
  → `_evaluate_validated`). It is not on the RSP items' paths (the trace is clean). It is row kb-validators' question.
- The preconditions of `selected_rules` (a tuple of the wrong length or sort, an unregulated predicate) stay Python's
  input checks, with the same errors as before and before any Lean call. They are not a verdict.
- Preparedness's old `completed` also type-checked the outcome formula in Python (`A._Checker(env).formula`). The
  switch drops that; Lean decodes and checks the case. The answers are unchanged (`--check`).

## Spec re-read

- One call per (document, model), the query order, the fallback and no truncation: against architect ruling
  20261113-kb-10b-step2.md sections 2-3, as quoted in prompts/task-kb-10b.txt:13. The ruling file itself is not
  visible from this worktree after the restart.
- `outcome_at(predicate, model, values)`, the model's identity as its `to_dict` JSON, and the hand-built document
  keeping the Python path: against prompts/task-kb-10b.txt:6.
- Seeded bugs (a) and (b): against task-kb-10b.txt:9.
- Row 2's cell: against reviews/dri-decisions-20261114-kb-10b-switch.md item 1 (a)-(c) and
  reviews/kb-10b-switch-dri-note-20261114.md item 1. The text is copied exactly.
- The F1 test (same environment, different rules, different kept answers) and the F7 reset: against
  reviews/kb-10b-switch-dri-note-20261114.md item 2.
- The handle count: against docs/kernel/kb-10e/REPORT.md (registrations table) and the task's fallback rule.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: PASS. No new route: `selected_at`'s schema and binding are kb-10a's.
   `tests/test_soft_selected.py::test_every_answer_field_retyped_is_unavailable`, `::test_a_forged_answer_is_unavailable`,
   `tests/test_kb10b_switch.py::test_an_unbound_answer_is_unavailable_through_the_document`, and the relay mutation
   gate (Final runs).
2. Deliverables: PASS. Every task line is in the Deliverables table, with its commit and test. The Preparedness
   `--check` and the merge bound were waiting for kb-10e, and both are done in this round.
3. Tests can fail: PASS. Seeded bugs a, b, h-n and the two loader bugs (`seeded-bugs.json`, all `"caught": true`).
4. Python and Lean agree, valid inputs pass: PASS. All five keys exit 0 base and head with unchanged results
   (`evidence/wall-times.txt`). The hand-built path: `::test_a_document_without_its_soft_source_keeps_pythons_path`.
5. R8 binding: PASS. `::test_an_unbound_answer_is_unavailable_through_the_document` (a row shifted to another query),
   `::test_a_query_outside_the_document_is_refused_as_before_without_a_call`.
6. Gate evidence on final HEAD: PASS. Rebased on main and regenerated (4c10d5b71). The selected run is on the
   committed HEAD (Final runs), and the chain runs the gate.
7. Unsigned items: PASS. Row 1 cites R12. Row 2 is SIGNED by the decision's rule (b), with the ratios in its Evidence.
   Nothing is reserved.
8. Every user-visible change in DELTA: PASS. No answer changed (five keys, two pairs each). Speed is row 2, and the
   generated files are row 1.
9. Test selection: PASS. The selected run takes `tests/test_kb10b_switch.py` and `tests/test_keyed_answers_authority.py`
   (Final runs).
10. Lean statements: N.A. No Lean change.
11. Budgets fail closed: PASS. `::test_over_the_limit_for_one_predicate_each_query_is_asked_alone_never_truncated`,
    `::test_a_refusal_other_than_the_limit_is_raised_not_answered`.
12. CPU regression: PASS under the decision's bound: wall ≤ 1.15x on every harness in both pairs, and Lean CPU per
    call ≤ 0.23 s (`evidence/split-restart.jsonl`). The call count is pinned by
    `::test_one_call_per_document_and_model_sends_every_query_of_the_pair` (no step-count test beyond it).
13. Removed tests: PASS. `test_selection_is_pythons_evaluation` was renamed in round 1, with a `Test-removed` trailer.
    `tools/gate_collection.py --check --prebuilt`: Final runs.
14. Both directions: PASS. One call within the limit and the fallback over it. Lean's path for a sourced document and
    Python's for a hand-built one. Same environment with the same rules shares answers
    (`::test_one_call_per_document_and_model_sends_every_query_of_the_pair`: a rebuilt copy makes no call); with other
    rules it does not (`::test_same_environment_with_other_rules_is_another_document`).
15. Overclaim, silent cut, checks can fail, limits: PASS. Each number names its file. The two void pairs and the
    `py_under` stand-in are stated. The Preparedness `outcome` call site is marked as an inference. Each new test has
    a seeded bug. The query limit is Lean's, charged before decoding (kb-10a).

## Review fix, round 1 (kb-10b-switch-review.final.md; f54983ab0, bb21306bd)

- **F1 (B):** `harness()` in `tests/test_kb10b_switch.py` ran each harness's `run.py` with whatever another test
  had left in `sys.modules`, so eligibility's `translation` (from `tests/test_eligibility_wfp.py`) stood in for
  FSF's. It also left the harness's own siblings and `sys.path` entries behind. Fix: one shared loader,
  `tests/usecase_scope.py` (`usecase_scope`, `load_script`). Its sibling names are every `*.py` stem of the use
  case's directory, read from the tree. It moves other use cases' modules aside while the script loads, and
  restores `sys.modules` and the whole `sys.path` afterwards. Regression test:
  `tests/test_kb10b_switch.py::test_a_harness_loads_its_own_siblings_and_leaves_none_behind`. Seeded bugs
  review-F1-modules and review-F1-path.
