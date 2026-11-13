# kb-10b, round 1: the shadow (step (1) only; STOPPED before step (2) by the DRI gate)

Status: step (1) done and committed; **STOP before step (2)** as the DRI gate (2026-11-11, inbox 20261111T143445Z) asks. Steps (2)-(4) wait for the architect seat's and the DRI's ruling on this shadow.
Shadow: **180,587 calls compared, 0 mismatches, 0 refusals, 0 calls with `background: false`**, over the three safety-framework harnesses run in full with `--check` (each exited 0; no `results.json` changed).
No product file changed (no ve/, tools/, conformance/, lean/ or rust/ diff); no DELTA row needs a DRI signature (one R12 row: generated files).
Open: the switch (steps (2)-(4)); a speed note for step (2) below ("Notes for the DRI").

SIZE: 0 product, 133 tests, 354 other hand-written lines (`usecases/safetyfw_shadow.py`), plus this report, DELTA.md and seeded-bugs.json; generated: the code map, `tests/history-dependent.json`, and the three saved kb10-shadow.json files (`git diff --numstat $(git merge-base HEAD main) HEAD`).

## Deliverables of this round

| Task line | Where | Evidence |
|---|---|---|
| (1) a test-only helper that runs each safety-framework harness with a wrapper over every `selected_rules` call and every `completed` evaluation | `usecases/safetyfw_shadow.py` (`installed`: wraps `SoftenedNormDocument.selected_rules`, the harness's `completed`, its document builder for the choice label, and its item function for the case label; `SoftNormDocument._init_soft` records each elaborated document's soft source) | `tests/test_kb10_shadow.py::test_the_wrappers_are_removed_and_a_document_without_its_soft_source_is_counted` (wrappers return Python's answer and are removed) |
| (1) one Lean call per document and model, with that model's queries | `Shadow.groups`, `Shadow.ask` (`ve.soft_route.selected_at`, kb-10a's relay) | `::test_one_lean_call_per_document_and_model` (six items, four distinct tuples: one call with four queries) |
| (1) every difference recorded with document choice, case id, predicate, tuple, Python's answer, Lean's answer and `background` | `Shadow.compare` (`mismatches` rows; refusals and `background: false` cells listed too) | `::test_a_planted_difference_is_listed_with_python_and_lean_answers`, `::test_a_model_outside_the_soft_premises_is_counted_with_background_false`, `::test_a_refused_query_is_listed_not_dropped` |
| (1) the three reports | `docs/usecases/safetyfw/anthropic-rsp/kb10-shadow.json`, `docs/usecases/safetyfw/openai-preparedness/kb10-shadow.json`, `docs/usecases/safetyfw/safety-framework/kb10-shadow.json` (saved evidence; no test recomputes them, D4) | the command in each file's `command` field, run on 6edb29d11c (the files' `commit`) |
| (2)-(4) | not started: the DRI gate stops this round after (1) | the stop summary (below and `manage-agents/kb-10b-stop.final.md`) |

## The shadow

Command (one per harness, on 6edb29d11c, the shadow script as committed there; the harness runs `--check`, so the
run fails as the harness does if a keyed answer changed):

```
uv run python usecases/safetyfw_shadow.py anthropic-rsp       docs/usecases/safetyfw/anthropic-rsp/kb10-shadow.json
uv run python usecases/safetyfw_shadow.py safety-framework    docs/usecases/safetyfw/safety-framework/kb10-shadow.json
uv run python usecases/safetyfw_shadow.py openai-preparedness docs/usecases/safetyfw/openai-preparedness/kb10-shadow.json
```

Printed lines (log /tmp/kb10b/all.log):
```
anthropic-rsp: exit 0; calls {'completed': 3700, 'selected': 3963}, 458 Lean calls, 0 mismatched calls (0 cells), 0 refused, 0 with background false; unsourced 0
safety-framework: exit 0; calls {'completed': 1194, 'selected': 4366}, 641 Lean calls, 0 mismatched calls (0 cells), 0 refused, 0 with background false; unsourced 0
openai-preparedness: exit 0; calls {'completed': 29484, 'selected': 137880}, 6366 Lean calls, 0 mismatched calls (0 cells), 0 refused, 0 with background false; unsourced 0
```

| Harness | `selected_rules` calls (non-empty) | `completed` calls (true / false) | Documents, models | Lean calls (distinct queries) | Mismatches | Refused | `background: false` | Harness s, Lean s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Anthropic RSP | 3,963 (1,300) | 3,700 (2,347 / 1,353) | 81, 83 | 458 (1,270) | 0 | 0 | 0 | 239.0, 276.5 |
| OpenAI Preparedness | 137,880 (20,778) | 29,484 (18,294 / 11,190) | 1,125, 312 | 6,366 (35,700) | 0 | 0 | 0 | 1,401.2, 4,517.0 |
| DeepMind FSF | 4,366 (731) | 1,194 (712 / 482) | 28, 130 | 641 (2,763) | 0 | 0 | 0 | 115.5, 31.6 |
| **Total** | **146,209 (22,809)** | **34,378 (21,353 / 13,025)** | | **7,465 (39,733)** | **0** | **0** | **0** | |

Calls by key family (`calls_by_family`, the innermost item label's leading letters):
RSP A 5,600, B 360, C 2, G 280, K 1,220, N 201; Preparedness A 77,760, B 6,480, C 8, G 79,920, K 2,700, N 18, and
478 outside an item; FSF (by case id) A 2,814, B 728, G 269, K 139, R 54, conflict 2, and 1,554 in the stages after the
items (family N, default sensitivity, variants). Every call ran with its soft source known (`calls_without_soft_source`
is empty in all three), and Python never answered UNKNOWN (`completed unknown` is absent from `python_answers`).

Scope: everything a `--check` run computes, mutants and removed narrowings included (labelled `[MUTANT=…]` /
`[WITHOUT_NARROWING=…]` in the case label), not only the scored items. Selection is compared as ordered lists (both
are in rule order); an outcome as Python's value `is True` against Lean's boolean, with a Python UNKNOWN always a
mismatch.

### kb-10a's differential (item d), cell by cell

kb-10a's REPORT ("The differential", `docs/kernel/kb-10a/differential.txt`): 5,880 queries, **0 mismatches, mismatch
list empty**. There is no listed mismatch to classify as a changed or unchanged cell. This shadow covers its scope (the
RSP A, B, K, G families, deny and allow) as calls the harness actually makes, and adds the N and C calls, the mutant
and narrowing runs, and the Preparedness and FSF harnesses: still 0.

### Mismatch classification (SPEC 4.1 / 4.2 / other)

None to classify: 0 mismatches, so no SPEC 4.1 conflicting-situation cell, no SPEC 4.2 cell (0 calls with
`background: false`), and no "other" cell. By the task's condition for step (2) ("every mismatch is explained"), step (2)
is unblocked as far as this evidence goes. It still waits for the DRI gate.

## Seeded bugs

`docs/kernel/kb-10b/seeded-bugs.json`: five, all in `usecases/safetyfw_shadow.py`, each caught by
`uv run pytest -q tests/test_kb10_shadow.py`. The task's (c), comparing Python with Python, fails
`::test_a_planted_difference_is_listed_with_python_and_lean_answers`. The others are (d) a Lean row attributed to the
next query (3 tests fail), (e) a dropped refusal, (f) a wrapper that changes Python's answer, and (g) `background:
false` not counted. The task's (a) and (b) are planted in step (2)'s code, so they belong to the continue round.

## Tests

- `uv run pytest -q tests/test_kb10_shadow.py`: 6 passed.
- Selected tests on the committed HEAD 75bbc77674, with a clean tree:
  `MAC_PYTEST_NO_DEFER=1 zsh manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`.
  It selected 56 of 615 units and ran them on the VM (the Mac is the last resort). Result: "recorded 56 units for
  tree 4407fd773a; … 0 failed", `exit=0; 4470s`. Only this .md file changed after that run.
- Pre-existing failures on main (`manage-agents/main-known-red.txt`): none in the selection.
- `uv run python tools/regen_generated.py --check`: "checked 41 entries" (after one `--write`).

## Notes for the DRI

- **Speed for step (2) (SPEC 4.4).** One `soft-selected` call per (document, model) averaged 0.60 s on RSP, 0.71 s on
  Preparedness and 0.05 s on FSF (Lean seconds / Lean calls above, on the shared VM). If step (2) keeps the same
  grouping, the Preparedness `--check` run gains about 75 min of Lean time, against 19 to 23 min for the whole Python harness today (1,139 s and 1,401 s in the two shadow runs). Two
  things are not measured: Python's own evaluation time, which step (2) removes, and whether the per-call cost is
  the source's elaboration repeated per call (A). Step (2) also has to choose the queries of a pair at its first call.
  The shadow sent only the queries the run made (2.8 per pair on RSP, 5.6 on Preparedness); every regulated
  predicate times every tuple would be more (kb-10a: 70 per pair).
- The shadow records `git rev-parse HEAD` in its report, so the generated `tests/history-dependent.json` lists
  `tests/test_kb10_shadow.py` (the test itself starts no git; the listing is static).

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No new relay. The shadow reads Lean only through kb-10a's bound `selected_at`; a refusal is listed (`::test_a_refused_query_is_listed_not_dropped`).
2. Deliverables: PASS. Step (1) is the table above. Steps (2)-(4) are stopped by the DRI gate in the task, not cut. No new permanent report test (the kb10-shadow.json files are evidence only). No authority switch.
3. Tests can fail: PASS, seeded bugs c, d, e, f and g (`docs/kernel/kb-10b/seeded-bugs.json`).
4. Python, Lean and Rust agree: PASS. The shadow is this comparison: 180,587 calls, 0 mismatches.
5. R8 binding: N.A. No new binding; `bind_selected` (kb-10a) is unchanged.
6. Gate evidence on final HEAD: PASS. The selected run is on the committed HEAD; the chain runs the full gate.
7. Unsigned items: PASS. DELTA has one row (R12); no signature is needed.
8. Every user-visible change in DELTA: PASS. No answer changed: each harness's `--check` exited 0 under the shadow, and `git diff --stat` on `usecases/*/results.json` is empty.
9. Test selection: PASS. `tools/select_tests.py --base $(git merge-base HEAD main)` selects 56 of 615 units, including `tests/test_kb10_shadow.py`.
10. Lean statements: N.A. No Lean change.
11. Budgets fail closed: N.A. No budgeted operation added; the shadow counts a Python UNKNOWN as a mismatch, never as false.
12. CPU regression: N.A. for product code (none changed). The step-(2) speed figure is under Notes.
13. Removed tests: N.A. None removed or renamed.
14. Both directions: PASS. Agreeing answers give no mismatch and a planted difference gives one (`::test_agreeing_answers_list_no_mismatch` and `::test_a_planted_difference_…`). A source-less document is counted, not compared (`::test_the_wrappers_are_removed_…`). Every number above is quoted from the printed lines or the saved JSON files.
15. Overclaim, silent cut, checks can fail, limits: PASS. "0 mismatches" is the saved files' `mismatch_calls`; "no product file changed" is the empty `git diff --stat … -- ve tools conformance lean rust`. Nothing was cut. Every new check has a seeded bug. No limit was added.
