# kb-10b-switch: kb-10b steps (2)-(4), the switch of soft selection and outcomes to Lean

**STOPPED: needs kb-10e on main.** The DELTA reserves row 2 (speed) as a stop reason (L52). It is re-measured after kb-10e, and the 2.0x merge bound decides it then.
HEAD: see `git log -1` (the last commit adds only this report). Steps (2)-(4) are built and committed. RSP and FSF pass `--check` with unchanged results. The per-answer count on RSP is **99/126** (it was 8/126 on 9be13b93de).
What changed: `SoftenedNormDocument.selected_rules` and the new `outcome_at` take Lean's `soft-selected` answers. The three safety-framework harnesses' `completed` call `outcome_at`.
Open: the Preparedness `--check` run, the rebase and the merge wait for kb-10e (orchestrator order 2026-11-13). RSP `--check` wall time is 1.89x and 2.07x its base in two paired runs, against the 2.0x bound.

SIZE: 225 product (about 55 of them moved from `ve/soft_route.py`), 317 tests, 318 other hand-written lines (added lines; this REPORT not counted). The other lines are the evidence scripts under `evidence/scripts/` and `ownership/`, and the page `docs/usecases/keyed-answers.md`. Generated: the code map, `tests/history-dependent.json`, `docs/usecases/keyed-answers.json`, and the saved evidence files. Source: `git diff --numstat $(git merge-base HEAD main) HEAD`.

## Deliverables

| Task line | Commit | Evidence |
|---|---|---|
| (2) `SoftenedNormDocument.selected_rules` and a new `outcome_at(predicate, model, values)` take their answers from `selected_at`, kept per (document, model identity; the model's `to_dict` JSON) | b44f9ac7bf, ed16ff899f | `tests/test_kb10b_switch.py` (21 tests) |
| (2) grouping (architect ruling, section 2): one call per (document, model) at the pair's first question, sending every regulated predicate (rule order, then `order`) times every tuple over the model's domains (product order) | b44f9ac7bf | `::test_one_call_per_document_and_model_sends_every_query_of_the_pair`, `::test_another_model_or_another_document_is_another_call`, `::test_a_wire_dictionary_model_is_the_same_pair_as_its_finite_model` |
| (2) over Lean's query limit: per predicate, then the single query; never truncated, never answered from Python | b44f9ac7bf | `::test_over_the_query_limit_the_pair_is_asked_per_predicate`, `::test_over_the_limit_for_one_predicate_each_query_is_asked_alone_never_truncated`, `::test_within_the_limit_the_pair_is_one_call`, `::test_a_refusal_other_than_the_limit_is_raised_not_answered` |
| (2) the harnesses' `selected` and `completed` call them; no harness imports `_Evaluator` for these | b44f9ac7bf | `::test_the_harnesses_completed_is_outcome_at`. `selected` already called `selected_rules`. RSP and Preparedness no longer import `_Evaluator`. FSF keeps it only in `holds_at`, which sets a case model's decision atoms. |
| (2) a hand-built SoftenedNormDocument (no soft source) keeps the Python path and says so in its docstring; no key builds one | b44f9ac7bf, 59b5d24361 | `::test_a_document_without_its_soft_source_keeps_pythons_path`. Class docstring of `SoftenedNormDocument`. The ownership trace shows no `NormDocument.selected_rules` call on any RSP item (`ownership/per-item.tsv`). The keyed-paths measurement shows no `python selected_rules` in any of the three harnesses (`docs/usecases/keyed-answers.json`). |
| (3) the five keys `--check`, results byte-identical except wall time | RSP, FSF: e786674ec5 and 4c2258bb62 (the final code) | `evidence/final-check.txt` (e786674ec5), "Final runs" below (4c2258bb62), `evidence/wall-times.txt`. agent-policy and eligibility make 0 `soft-selected` calls (`evidence/lean-calls.txt`). **Preparedness: not run, it waits for kb-10e (the order).** |
| (3) wall time of each safety-framework `--check`, before and after, same machine, same hour; 2.0x bound | e786674ec5 | below. Preparedness waits for kb-10e. |
| (4) `py_under.py` before and after; the `ve/norms.py` and `ve/evaluate.py` functions that no longer run | e786674ec5 | below. Preparedness "after" waits for kb-10e. |
| Seeded bugs (a), (b) | 59b5d24361 | below, `seeded-bugs.json` |
| Per-answer count (Nov 23 checkpoint) | e786674ec5 (b44f9ac7bf code) | below, `ownership/` |
| Handle-table count (fallback: kb-10e's REPORT is not on main) | e786674ec5 | below, `evidence/handle-table.jsonl` |

kb-10a's differential (item d): 0 mismatches, as kb-10b step (1) recorded (docs/kernel/kb-10b/REPORT.md). The
step (1) shadow found 0 mismatches in 180,587 calls. No cell is listed as changed or unchanged because none differs.

## (3) The keys

Runs:
```
.venv/bin/python usecases/<harness>/run.py --check   # in iso.sh, VE_LEAN_SERVICE = this worktree's ve_service
```
- RSP: exit 0, `110 / 126`, on b44f9ac7bf, e786674ec5 (`evidence/final-check.txt`) and 4c2258bb62 ("Final runs").
- FSF: exit 0 on the same commits. Base and head print the same lines apart from timestamps, including the two
  `DISAGREE C-doc ...` lines already on main (`diff` of the two `time-1-safety-framework-*.log` outputs).
- agent-policy `check.py base` and eligibility `run.py --no-write --no-mutants`: exit 0, 0 `soft-selected` calls,
  no file changed (`evidence/lean-calls.txt`). They do not reach a soft document.
- Preparedness: **not run on this branch**. The order puts its `--check` run after kb-10e merges.

No keyed cell changed, so task item (3)'s stop for a changed cell does not apply.

### Wall times (same machine, same hour; base 0f6d59d441 and head run concurrently: `evidence/scripts/pair.sh`)

| Harness | Pair 1 before → after | Pair 2 before → after |
|---|---|---|
| FSF | 158.7 → 179.9 s (1.13x) | 138.0 → 159.1 s (1.15x) |
| RSP | 279.6 → 527.3 s (1.89x) | 314.2 → 650.1 s (**2.07x**) |
| Preparedness | waits for kb-10e | |

The architect's ruling (section 4) sets the merge bound: no `--check` above 2.0x its before value. RSP is at that
bound now, so I give the split the ruling asks for (`evidence/split.jsonl`, `evidence/scripts/split.py`; head only):

| Harness | wall | first `soft-selected` call per document | later calls | rest (Python and other Lean kinds) | longest call, wall / Lean CPU |
|---|---|---|---|---|---|
| RSP | 680.2 s | 81 calls, 67.4 s | 377 calls, 295.6 s (0.78 s each) | 317.2 s | 1.76 s / 1.73 s |
| FSF | 188.6 s | 28 calls, 1.7 s | 614 calls, 40.1 s | 146.7 s | 0.26 s |

On RSP a later call costs about what a first call costs: the per-document work is redone on every call. That is the
cost kb-10e removes. If later calls drop to about 0.05 s each, as the ruling estimates, RSP comes to about
680 - 296 + 19 = 403 s, about 1.3-1.4x. That figure is an estimate, not a measurement. RSP makes 458 calls, one per
(document, model) pair, the same pairs the shadow counted. A first version kept the answers per document object
and made 1,326 calls, because `--check` rebuilds each document after clearing the caches. The answers are now kept
per document request: `/tmp/kb10bs/rsp-count.log` against `rsp-count2.log`, in `evidence/lean-calls.txt`.

## (4) `py_under.py`, before and after (`evidence/pyunder-*.json`, `evidence/scripts/pyunder_diff.py`)

| Harness | `ve/norms.py` functions that no longer run | `ve/evaluate.py` |
|---|---|---|
| RSP | `NormDocument.outcome`, `NormDocument.selected_rules` (with its genexpr), `_instantiate` (with its genexpr), `_replace_term`, `_shift_term` | 10 functions before and after: `_Evaluator` still runs for the C family (`_find_conflict`, kb-10c) |
| FSF | `NormDocument.outcome`, `NormDocument.selected_rules` (with its genexpr) | 10 functions before and after: the C family, and `holds_at` while the harness builds a case model's decision atoms |
| Preparedness | not measured. The "before" run on the base exited 0 after 11,758 s but recorded 0 functions (its JSON has `total_lines` 0, cause not found), so it is void. Both runs belong to the continue round, after kb-10e and the rebase. | |

`NormDocument.selection` and `_expand` still run under RSP and FSF. The ownership trace below shows where from:
`ve.norms.check_conflict` → `_check_conflict_python` → `conflict_targets` (the C family, kb-10c).

## The per-answer count (reviews/lean-ownership-baseline-20261112.md section 2), RSP key, this branch

Method: as reviews/lean-ownership-20261112/RESULT.md, one fresh process per item (`ownership/run_all.sh` through
`iso.sh kb10bs-ownership 8G`, `xargs -P 6`), on b44f9ac7bf (the switch; the later commits move the relay without
changing it). The script is `ownership/trace_item_callers.py`: the DRI's `trace_item.py` plus one field, the call
chain into each decision function. 126 of 126 items ran, with 0 errors. Raw summary: `ownership/per-item.tsv`.
Call sites: `ownership/called-from.json`.

| family | items | 1 clean | agrees (or recorded deviation) | passes | why not |
|---|---:|---:|---:|---:|---|
| T | 9 | 9 | 9 (T7 recorded deviation) | **9** | (T5 now passes: kb-8's `quantity` wire theorem is on main) |
| S | 8 | 8 | 7 (S2 UNDECIDED) | 0 | criterion 2 kept as RESULT.md judged it (`risk`). Not re-judged here: see Notes. |
| D | 9 | 9 | 6 (D6a, D6b, D7 UNDECIDED) | **6** | kb-8 merged |
| A | 40 | 40 | 40 | **40** | |
| B | 12 | 12 | 12 | **12** | |
| K | 27 | 27 | 24 (K9, K10 UNDECIDED; K18 differs from the key, as on 9be13b93de) | **24** | |
| G | 8 | 8 | 5 (G4, G5, G6 UNDECIDED) | **5** | |
| N | 5 | 5 | 3 (N4, N5 UNDECIDED) | **3** | |
| C | 8 | 0 | 5 | 0 | `_check_conflict_python` (kb-10c) |
| total | 126 | 118 | 111 | **99** | |

No A/B/K/G/N item still calls a Python selection, outcome or `_Evaluator` function (criterion 1 clean on all 92).
The only decision calls left are on the 8 C items, all from `usecases/anthropic-rsp/run.py:_conflict:396` →
`ve.norms.check_conflict` → `_check_conflict_python` → `_find_conflict` (`_Evaluator`), and → `conflict_targets` →
`NormDocument.selection`, `_expand`. No keyed answer was changed; every disagreement above is the same as on
9be13b93de (RESULT.md: K agrees 24, G 5, N 3).

Criterion 2 for A/B/K/G/N: the values come from `soft-selected`, whose wire theorem is kb-10a's (SelectedSound.lean,
on main). The case model's premises come from `metered` (kb-7). Criterion 3 is read as RESULT.md reads it. One
point stays Python on these paths: the harness combines the deny and allow answers (`holds = left and right`, the
rule intersection, `default_sensitive`). Row kb-9 puts that composition under one kernel row (architect ruling,
section 5).

## Handle-table count (reviews/kb-10e-dri-note-20261113-next.md; kb-10e's REPORT is not on main)

The call order is the order the switch sends its `soft-selected` calls: each (document, model) pair at its first
question. It was recorded on the base with step (1)'s shadow wrappers (`evidence/scripts/order.py`; 167,364
calls, 6,366 pairs, 1,125 documents, harness exit 0) and saved as `evidence/preparedness-call-order.json`. The
simulation (`evidence/scripts/handles.py`, `evidence/handle-table.jsonl`) applies `Handles.insert`
(Protocol.lean:631, :658): at most 64 entries, emptied first when one more would exceed it. It assumes one table,
as one service process holds it, and does not model the byte bound.

**A Preparedness run makes 1,381 registrations for 1,125 documents: 1.23 per document.** That is under 1.5, so no
bound or eviction rule is proposed. For comparison: LRU with 64 entries gives 1,275 (1.13 per document); emptying
at 128 gives 1,263 (1.12), at 256 gives 1,200 (1.07). `maxHandles` and the emptying rule are unchanged.

## Seeded bugs (`seeded-bugs.json`; `evidence/scripts/seed.py` plants each one, runs one test, restores the file)

All are in Python, the only language whose product code changed. Each makes its named test fail (a failing test,
not a collection error: `nested_pytest.failed_test_run`).

| Bug | File | Fails |
|---|---|---|
| (a) the task's: a result row kept under the next query (`zip(queries[1:], results)`) | `ve/softnorms.py` | `tests/test_kb10b_switch.py::test_selected_rules_and_outcomes_are_leans_answers_at_each_tuple` |
| (b) the task's: `outcome_at` returns the truth of the selection | `ve/softnorms.py` | `::test_the_outcome_is_not_the_truth_of_the_selection` (kb-10a's three-rule fixture) |
| (h) the limit fallback compares the `code` (the relay sets Lean's wire code) | `ve/softnorms.py` | `::test_over_the_query_limit_the_pair_is_asked_per_predicate` |
| (i) every model shares one kept answer | `ve/softnorms.py` | `::test_another_model_or_another_document_is_another_call` |
| (j) the regulated predicates without rules are left out of the pair's query list | `ve/softnorms.py` | `::test_one_call_per_document_and_model_sends_every_query_of_the_pair` |
| (k) RSP's `completed` sends the tuple reversed | `usecases/anthropic-rsp/run.py` | `::test_the_harnesses_completed_is_outcome_at` |

Task bug (c), the shadow comparing Python with Python, belongs to step (1). It was recorded in docs/kernel/kb-10b/seeded-bugs.json.

## Tests

- `uv run pytest -q tests/test_kb10b_switch.py tests/test_soft_selected.py tests/test_kb10_shadow.py`: 200 passed.
  `tests/test_relay_binding_inventory.py -k soft`: 21 passed.
- `uv run python tools/relay_mutation_gate.py` on e786674ec5: exit 0, "50 routes, 155878 mutants, 0 failures".
- Selected runs (`MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select`). On e786674ec5 the fast stage failed 2 tests; they
  were fixed in 59b5d24361:
  - `tests/test_inventory_lint.py::test_no_retained_code_imports_a_class_a_body`: the fallback imported `ve.ast._Checker`.
  - `tests/test_nested_pytest.py::test_every_pytest_command_is_built_by_the_builder`: `seed.py` started pytest itself.
  On 59b5d24361 the Actions shards failed 2 files; they were fixed in 4c2258bb62:
  - `tests/test_identity_lint.py` (5 tests): the cache key used a `ve-` domain literal.
  - `tests/test_keyed_answers_authority.py::test_selection_is_pythons_evaluation`: it pinned the old authority. The
    test, `docs/usecases/keyed-answers.md` and `usecases/keyed_paths.py` now say and record `soft-selected`, and
    `docs/usecases/keyed-answers.json` is re-measured. Against the same measurement on the base, the only changed
    paths are `python selected_rules`, `python completed` and FSF's `python holds_at` (its old `completed`), which
    became `lean soft-selected`. Base 0f6d59d441 → head, from `usecases/measure_keyed_paths.py` run in each worktree:
    RSP `python completed` 370 → none, `python selected_rules` 396 → none, `lean soft-selected` none → 122;
    Preparedness `python completed` 3,276 → none, `lean soft-selected` none → 1,180; FSF `python holds_at` 1,258 → none,
    `python selected_rules` 4,464 → none, `lean soft-selected` none → 642. Every other count is equal.
  The rerun is under "Final runs" below.
- `uv run python tools/regen_generated.py --check`: "checked 41 entries".
- Pre-existing failures (`manage-agents/main-known-red.txt`): none of the failures above is listed there.
- Not run: the full gate (the chain runs it), trust_mutants (no Lean change: R16 does not apply), and the
  Preparedness `--check`.

## Final runs

- Selected tests: the same `mac-pytest.sh --select` run, after the Actions shards gave no usable result (one shard
  missed the deadline), ran the whole selection on ve-cloud-2: "recorded 315 units for tree e1d4800ae0; 0 failed",
  `exit=0` (`/tmp/kb10bs/selected2.log`). That run takes the worktree as it is, so it tested the fixes before they
  were committed. e1d4800ae0 is exactly the tree of the committed code 4c2258bb62
  (`git write-tree` of the worktree without this report). It covers the failed ids above and the 41 units shard 1
  did not reach. Only this report was committed after it.
- `uv run python tools/gate_collection.py --check --prebuilt` on 4c2258bb62: exit 0, "23 added, 1 removed by a
  trailer, 0 refused, 0 stale and 0 malformed trailers".
- `--check` on 4c2258bb62: `safety-framework rc=0 133s`, `anthropic-rsp rc=0 490s` (`110 / 126`), 06:49Z-06:57Z.
- `uv run python tools/regen_generated.py --check` on 4c2258bb62: "checked 41 entries".

## Notes for the DRI

- Speed is the only open question, and it waits for kb-10e (split above). RSP's per-call Lean CPU reaches 1.73 s,
  so R4 (at most 1 s per check) does not cover the row today. After kb-10e it is re-measured, and R4 or the 2.0x
  bound is cited then.
- FSF made 642 calls where the shadow counted 641 pairs. The extra pair is not explained. The answers are unchanged
  (`--check` exit 0).
- Criterion 2 for family S: `lean/VE/Risk/Run.lean` has `risk_wire_scenario_sound` and `risk_wire_audit_sound` on
  this tree. RESULT.md judged that `risk` had no runner theorem. This report keeps S at 0 and does not re-judge it.
- Model construction over a soft base environment checks the soft background in Python
  (`ve.background._valid_soft` → `_evaluate_validated`). It is not on the RSP items' paths (the trace is clean). It
  is row kb-validators' question.
- The preconditions of `selected_rules` (a tuple of the wrong length or sort, an unregulated predicate) stay Python's
  input checks, with the same errors as before and before any Lean call. They are not a verdict.

## Spec re-read

- One call per (document, model), the query order, the fallback and no truncation: against architect ruling
  20261113-kb-10b-step2.md:13-24.
- `outcome_at(predicate, model, values)`, the model's identity as its `to_dict` JSON, and the hand-built document
  keeping the Python path: against prompts/task-kb-10b.txt:6.
- Seeded bugs (a) and (b): against task-kb-10b.txt:9.
- The handle table's rule: against Protocol.lean:631, :658 and reviews/kb-10e-dri-note-20261113-next.md:9-13.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: PASS. No new route: `selected_at`'s schema and binding are kb-10a's, moved to
   `ve.softnorms` unchanged. `tests/test_soft_selected.py::test_every_answer_field_retyped_is_unavailable`,
   `::test_a_forged_answer_is_unavailable`, the relay mutation gate (0 failures), and
   `tests/test_kb10b_switch.py::test_an_unbound_answer_is_unavailable_through_the_document`.
2. Deliverables: PASS for (2), (4) on RSP and FSF, the count and the handle count. (3) on Preparedness, (4) "after"
   on Preparedness and the merge are STOPPED by the order (needs kb-10e), not cut. No new permanent report test.
3. Tests can fail: PASS, seeded bugs a, b, h, i, j, k (`seeded-bugs.json`).
4. Python and Lean agree, valid inputs pass: PASS. RSP and FSF `--check` exit 0, and the five keys are covered as
   stated in (3). The hand-built Python path agrees on the fixture:
   `::test_a_document_without_its_soft_source_keeps_pythons_path`.
5. R8 binding: PASS. A row shifted to another query is refused:
   `::test_an_unbound_answer_is_unavailable_through_the_document`. A query outside the document is refused:
   `::test_a_query_outside_the_document_is_refused_as_before_without_a_call`.
6. Gate evidence on final HEAD: PASS. Selected run and harness `--check` on committed code; the chain runs the gate.
7. Unsigned items: PASS. One row is reserved as the stop reason (DELTA row 2), listed in this report's first line.
8. Every user-visible change in DELTA: PASS. No answer changed (`--check`). Speed is row 2, generated files row 1.
9. Test selection: PASS. The selected run took `tests/test_keyed_answers_authority.py`, `tests/test_identity_lint.py`
   and `tests/test_inventory_lint.py`, and they failed on the change as they should.
10. Lean statements: N.A. No Lean change.
11. Budgets fail closed: PASS. Over Lean's query limit the pair falls back and never truncates
    (`::test_over_the_limit_for_one_predicate_each_query_is_asked_alone_never_truncated`). Any other refusal is
    raised (`::test_a_refusal_other_than_the_limit_is_raised_not_answered`).
12. CPU regression: measured above (speed row, DELTA row 2). No step-count test was added, because the call count
    is pinned by `::test_one_call_per_document_and_model_sends_every_query_of_the_pair`.
13. Removed tests: PASS. `test_selection_is_pythons_evaluation` is renamed, with a `Test-removed` trailer in its commit.
14. Both directions: PASS. One call within the limit, and fallback over it. Lean's path for a sourced document, and
    Python's for a hand-built one (`tests/test_keyed_answers_authority.py::test_a_hand_built_document_keeps_pythons_selection`).
15. Overclaim, silent cut, checks can fail, limits: PASS. Each number above names its file. The Preparedness parts
    are written as not run. Each new check has a seeded bug. The query limit is Lean's, charged before decoding (kb-10a).
