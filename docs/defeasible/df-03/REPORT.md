# df-03: DF-0.3, the defeasible plan's baseline record

No DRI signature is reserved: there are no DELTA rows (no product code changed) and trust grows by +0.

**Result.** I recorded the baseline on `main` `702ff742`, before DF-1b and DF-3. P-1 is **0 of 3** probes answered: each
standalone default answers NONE. The plan expected "0". P-2 is **SOME** for each of the three sets, as the plan
expected. The answers are saved verbatim in `docs/research/evidence/defeasible/baseline/baseline.json`, and the report
is section 6 of `docs/research/defeasible-phase1.md`.

## Statement gate

DF-0.3 is a record and has no statement. The plan's DF-S passed (`manage-agents/defeasible-p3ver1.final.md`, plan
"DF-S ... done"). The probe translation is on `main`: `CE4` is in `tests/ce4.py`, built from the pilot's pinned
translation `76922d6c`, and `tests/test_readings_sd_ce4.py` uses it. P-1's three sets are in `CE4.SETS`. Each predicate
and sort in P-1's and P-2's questions (plan 4.2) is in `CE4`'s frame with the arity the plan uses. RD-9's C7 is the first
question, and `tests/test_readings_sd_ce4.py` already holds it. Nothing was missing.

## Plan rows

| Plan row or directive | Delivered by |
|---|---|
| DF-0 item 3: "on RD-9 SC-9's probe translation, P-1's and P-2's questions with today's kinds, answers recorded verbatim" | `research/defeasible/baseline.py` (run) and `research/defeasible/baseline_cases.py` (cases), commits `96ec79657`, `b4158e08d`, `cd8eba4a4`; evidence `9a23a3d8b` |
| 0.2 DF-0.3 row: "recorded verbatim on that `main`, with today's kinds, before DF-1b merges" | `baseline.json`: `main_commit` 702ff742, `inputs_changed_from_main: []`, exit code, stdout and stderr for each question |
| Deferred table: "the measured 0 of P-1 and the SOME of P-2" | `measured`: `p1_answered: 0`, `p2_verdicts` SOME ×3; `tests/test_defeasible_baseline_evidence.py::test_p1_measured_zero_of_three`, `::test_p2_measured_some_from_the_sets_own_default` |
| P-1 row: the default candidates "as standalone soft documents in `CE4`'s frame" | `p1-<set>.ve.md`; `::test_p1_document_is_the_default_candidate_alone` |
| P-2 row: "the same three sets inside `CE4`" | `p2-ce4.ve.md`, written by `test_readings_sd_ce4.ce4_document`, which owns it; `::test_p2_document_is_ce4` |
| Batch order step 2: DF-0.3 on `main` once `rd-9/integrate` merges | done; DF-1b and DF-3 may now cite it |
| DF-0 outputs: "a dated section to the same report", evidence in the same directory | `defeasible-phase1.md` section 6 (2026-10-19); `docs/research/evidence/defeasible/baseline/` |
| Task: main commit, command and host load saved | `baseline.json` `main_commit`, `command`, `host` (CPUs, load before and after), and the binaries' hashes, each pinned in `lean/checkers.lock` |
| Task: a test of the SAVED evidence only | `tests/test_defeasible_baseline_evidence.py`, 10 tests. They run neither `ve` nor git (`tools/history_tests.py --check` passes) |
| Task: the plan files copied verbatim if `main` lacks them | `ba4263ea5`: `docs/spec/defeasible-PLAN.md`, `docs/spec/defeasible.md` and `docs/research/defeasible-phase1.md`, byte-identical to `00a45ce36` |
| DRI DF1–DF7, X1–X3 | none of them changes DF-0.3. DF4 puts DF-1b and DF-3 in the document-mode queue; this item edits no queued file |
| L70: part documents only | the largest document is `CE4`, at 19.7 kB |

**Method notes.** "Today's kinds" means today's public route, `ve document readings <doc> --conclusion <question>`.
DF-1b asks its strict question through the same command. On the P-1 documents, Lean answers on the
`assertion-shared-model` route. On `CE4`, it answers on the `enumerated` route. No kind available today gives a default
answer, so a P-1 probe counts as answered only when the verdict is ALL (`baseline_cases.follows`).

**Deviations.**
- I copied the three plan documents only, as the task asked. Phase 1's scripts and evidence files are on
  `research/defeasible-p1` and not on `main`. Sections 1–5 of the copied report still name them.
- The plan's 0.1/0.2 tables and section 4 of the report still read "DF-0.3 DEFERRED". I left the copies verbatim, and
  section 6 records the result. Updating the plan's status line is the planner's job.
- I recorded the evidence twice: at `96ec79657`, and again at `cd8eba4a4` by the final script. The answers were the
  same, and so were the document bytes. Only the date, the head and the host load changed.

## Seeded bugs

All of them are in `docs/defeasible/df-03/mutants.json`. Each one was planted, run against
`tests/test_defeasible_baseline_evidence.py` and restored, and each made exactly the named test fail:

1. `research/defeasible/baseline_cases.py`: P-1 takes the `strict` candidate instead of `default`. Failed
   `::test_p1_document_is_the_default_candidate_alone`.
2. `research/defeasible/baseline_cases.py`: C7's atom has its arguments swapped. Failed `::test_questions_are_p1s_three`,
   which derives each question from the set's own rule.
3. `research/defeasible/baseline_cases.py`: `follows` counts NONE as answered. Failed `::test_p1_measured_zero_of_three`.
4. `docs/research/evidence/defeasible/baseline/baseline.json`: a recorded P-2 verdict changed to ALL. Failed
   `::test_p2_measured_some_from_the_sets_own_default`.
5. `docs/research/defeasible-phase1.md`: a P-2 cell changed to ALL. Failed
   `::test_report_section_states_the_recorded_values`.

No product code changed, so there is no Lean, `ve/` or Rust seeded bug to plant.

## Trust, size, pilot bytes, next

- Trust: `tools/trust_map.py --check` reports K +0, S +0, D +0, G +0 and trusted +0 against 702ff742 (PASS). There is
  no allowance and no FOLLOW-UPS row.
- Size: 510 hand-written lines, counted with `git diff --numstat` from the merge base and leaving out the three copied
  files. That is the 37-line report section, 180 lines of scripts, 145 of test, 112 of this report and 36 of
  `mutants.json`. The script also wrote 177 lines of evidence, which count as generated (687 lines if counted).
- Pilot bytes: 0 B moved. This is the "before" of the constitution's defaults path (8,764 B primary, research share). It
  claims nothing.
- Pre-existing red: none of `main-known-red.txt` is in the selected set.
- Next: df-1a (Lean), which may land before or after this record, and then df-1b, which can now cite P-1's measured
  "0" and claim "0 → 3". DF-3 can cite P-2's measured SOME.

## Tests run

- `tests/test_defeasible_baseline_evidence.py` and `tests/test_history_tests.py`: 35 passed.
- Selected tests (`mac-pytest.sh --select`, 24/446 units, on the Mac runner). The first run failed only the
  history-test lint, which I fixed in `b4158e08d`. The final selected run, at `76195178`, passed all 24 units with 0
  failed. Only this report line has changed since.
- `tools/gate_collection.py --check --prebuilt`: 10 added, 0 removed, 0 refused, 0 stale, 0 malformed.
  `tools/regen_generated.py --check`: 31 entries checked, all current.
- The chain runs the full gate on the final HEAD.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. This item adds no relay and no Python reader of Lean answers. It saves the CLI
   output verbatim.
2. Deliverables built, no rule broken: PASS. Every row is in the Plan rows table above. There is no Python copy of a
   Lean decision: `follows` only counts verdicts for the record, and DF-1b's relay owns the default answer. No file
   overlaps an in-flight branch (`git diff --name-only main...<b>` over the feature, lean-first, infra and foundation
   branches). Evidence: `tests/test_defeasible_baseline_evidence.py`.
3. Tests can fail: PASS. Five seeded bugs, each caught by a named test (`docs/defeasible/df-03/mutants.json`). None of
   them fails at a hash step.
4. Python, Lean and Rust agree: N.A. No product code changed. The answers come from today's route unchanged
   (`inputs_changed_from_main: []`).
5. R8 binding: N.A. No new relay. The test checks that each saved answer is bound to its saved document and question
   (`::test_p1_measured_zero_of_three`, `_answers`).
6. Gate evidence matches the final HEAD: PASS. The chain runs the gate on the final HEAD. The baseline was recorded on
   702ff742 inputs with fresh `lake build` and `tools/rust_build.py` binaries, whose hashes are pinned
   (`::test_record_names_main_the_command_the_host_and_pinned_binaries`).
7. Nothing unsigned: PASS. There are no DELTA rows and trust is +0 (`tools/trust_map.py --check`).
8. User-visible changes in DELTA: N.A. No product, CLI or verdict change. DELTA: none.
9. Test selection: PASS. `select_tests --base` picks 24/446 units. A seeded change to `baseline_cases.py`, or to the
   evidence and the report, selects `tests/test_defeasible_baseline_evidence.py` (`select_tests --paths`).
10. Lean statements: N.A. No Lean.
11. Budgets and deadlines: N.A. No budgeted operation was added. The script's subprocesses use `HANG_TIMEOUT`, and the
    test runs no subprocess (`tests/test_hang_guards.py` is in the selection).
12. CPU or memory regression: N.A. No product code. The probe documents are small (L70).
13. Test-removed trailers: N.A. No test removed. `tools/gate_collection.py --check --prebuilt` reports 0 refused, 0
    stale and 0 malformed.
