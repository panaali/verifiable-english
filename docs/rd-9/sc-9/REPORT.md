# sc-9 report: the constitution under the soft form (pilot tooling and measurement)

**Status:** built. **C10 NOT RUN** (no model calls; DRI decision `reviews/dri-decisions-20261104-sc-9.md` item 1, follow-up sc-9-comprehension). Branch `feature/sc-9`; the C9 status measurement code is at `427f40684`.
**Changed:** the run directory `usecases/claude-constitution-pilot/run-20261104T0716Z/` (`migrate_soft.py`, `measure.py`, the probe translation, the queries, the verbatim answers, `SUMMARY.md`, `changed_units.json`), `tests/test_sc9_migrate.py`, and this report and `DELTA.md`. No product file changes.
**Open:** C6 and C7 are UNKNOWN on the whole translation, C7 `:0` is CheckerUnavailable, C1 and C3 are unworded, the six universal C9 entailment queries remain UNKNOWN, and C10 was not run. Concrete C9 point statuses and the strict separation are now measured on all 16 choices. The remaining analysis is **sc-9b**.
**Signatures:** none needed. No DELTA row, trusted +0. The DRI accepted D1 (candidate ids) in the same decision file, item 2.

## Plan and task rows

| Row (plan SC-9, task) | Delivered | Evidence |
|---|---|---|
| (1) Pilot run directory, every script at one commit, foreground, host load recorded | yes. The 26 steps ran at `c4d6e79f4`, `decided` at `2d0b9d1a9`, and two C9 status steps at `427f40684`; no product tree changed (SUMMARY "What ran") | `answers/measurements.json` (`commit`, `host_at_start` per step) |
| (2) `migrate_soft.py`: `soft-norms@0`; `default` rewritten as 5.2; the `exception_to_*` terms removed; situations re-proposed by SC-8's search and checked by Lean; units, spans and `source_word` unchanged | yes. 5.2's rewrite is `tests/ce4.soft_default` (one owner, imported, not copied). The search is `ve.readings_s1.search` over `readings-elaborate`'s filled frame. All 8 pairs were found | `answers/search.json`; tests `test_rule1…`, `test_rule2…`, `test_rule4…`, `test_units_spans_and_source_words_are_unchanged`, `test_the_committed_probe_is_the_rewrite_with_searched_situations` |
| (2) every `meaning_id` from Lean's answer | units: yes. Candidates: **no** (deviation D1, accepted by DRI item 2) | `answers/meaning-ids.json`; `test_each_candidate_id_is_the_loaders_binding_of_its_content` |
| (3) `load`, `check`, `render`, C6, C7, claim to be human, each answer verbatim | yes, before and after. `ve document` has no `load` subcommand, so `load` is `ve.document.load_document` in a subprocess (`measure.LOAD`) | `answers/{before,after}/*.out` |
| (4) The before/after table, measured | yes | SUMMARY "Before and after" |
| (5) C9: u0073.s05 as one default rule with three sufficient conditions; its `soft_premises`; statuses; separation from strict | rule, `soft_premises`, statuses and separation found on all 16 compatible choices. Under each condition the default is UNDECIDED and the strict twin SETTLED yes; with none both are SETTLED yes. The older universal entailment queries stay UNKNOWN | `test_rule3…`, `test_the_c9_probe_has_three_sufficient_premises_on_every_choice`, `test_c9_point_status_is_measured_on_every_choice_and_condition`; `answers/{after,strict}/point-status-c9.out` |
| (6) C10: Sonnet 5.5 answers spec 2.6's four questions | **NOT RUN** (DRI item 1). The lines and questions are recorded | `comprehension/questions.json`; `test_the_comprehension_lines_are_the_renderers` |
| (7) `changed_units` for the next audit | yes: u0036.s05, u0073.s05, u0125.s04.p2, u0156.s03, u0263.s04.p2. The plan's row names four units; C9's u0073.s05 is the fifth | `changed_units.json` |
| R14 | the SUMMARY says it. No conflict was reported; the separations are about the translation | SUMMARY first lines |
| L70 memory: one whole-constitution run at a time, 16 GB limit, wall/CPU/RSS | yes, all sequential. Earlier steps used `systemd-run`'s `MemoryMax=16G`; the C9 point-status steps used `RLIMIT_AS=16G` because this worker has no user bus. Peak RSS of the new steps was 185,704 KB; none killed | `answers/measurements.json` |

Deviations:
- **D1.** Candidate `meaning_id`s are `ve.readings.s1_content_meaning_id`, the loader's binding, not Lean's. Lean's `document` mode gives a unit with a candidate's content its soft content id, which differs on 8 of 8. The DRI accepted this (item 2) and filed follow-up sc-9-candidate-ids.
- **D2.** The first measuring pass found no Rust release binary in this worktree (`CheckerUnavailable: missing Rust executable`). That was setup, not a measured result, so the pass was rerun after `python3 tools/rust_build.py`.

## Seeded bugs (Python only; no Lean or Rust changed)

Each bug was planted alone in the committed file, the named test was run, and the file was restored with `git checkout`.

| Bug | File | Change | Caught by |
|---|---|---|---|
| S1 | `run-20261104T0716Z/migrate_soft.py` | rewrite the `strict` candidate instead of the `default` one | `test_rule2_each_default_candidate_is_rewritten_as_in_5_2` (ERROR: the rewrite refuses) |
| S2 | same | `sufficient: conditions[:2]` | `test_rule3_u0073_s05_is_one_default_rule_with_three_sufficient_conditions` FAILED |
| S3 | same | keep the dropped terms in `open_terms` | `test_rule4_the_five_open_terms_are_dropped_everywhere` (ERROR: the guard refuses) |
| S4 | same | `unchanged` ignores `source_word` | `test_units_spans_and_source_words_are_unchanged` FAILED |
| S5 | same | the "still mentioned" guard disabled | `test_rule4_refuses_a_term_some_content_still_names` FAILED |
| S6 | `comprehension/questions.json` | C2's line reworded | `test_the_comprehension_lines_are_the_renderers` FAILED |
| S7 | `probe-translation.probe.md` | one candidate given Lean's unit id | `test_each_candidate_id_is_the_loaders_binding_of_its_content` FAILED |
| S8 | `c9_status.py` | suppress the UNDECIDED witness, making a sufficient-condition request use `table3` | `test_c9_point_status_is_measured_on_every_choice_and_condition` FAILED (`method` mismatch) |

## Trust, size, bytes
- **Trust.** `uv run python tools/trust_map.py --check` reports "PASS: K, S and untied [V] within c3d9ea9380cb". No Lean change, so no R16 allowance, no mutants JSON and no FOLLOW-UPS row.
- **Size** (`git diff --numstat $(git merge-base HEAD main)`, hand-written). `migrate_soft.py` 223, `measure.py` 141, `c9_status.py` 91, `tests/test_sc9_migrate.py` 221, the queries 6, `SUMMARY.md` 64, this report 83 and `DELTA.md` 5: 834 lines. The required C9 point-status matrix added the excess over the ~600 rule; analysis work remains in sc-9b. Excluded as script output: the probe translation, `answers/`, `changed_units.json` and `comprehension/questions.json` (a one-off extraction from `answers/after/render.out`).
- **Pilot bytes expected:** 0 now. If an audit accepts the five units, Lean-decided coverage moves from 0 B to 2,602 B (1.41%); claimed coverage does not move. Nothing is claimed before that audit.
- **Overlaps.** None: `git diff --name-only main...<b>` over `feature/*`, `infra/*`, `foundation/*` and `lean-first/*` touches none of these paths.

## Next item
**sc-9b**:
- why C6 and C7 end UNKNOWN on the whole translation while CE4 decides them;
- C7 `:0`'s `ReadingsConformance` unavailability;
- C1 and C3's unworded lines on the whole translation;
- why the universal C9 entailment questions remain UNKNOWN although all concrete C9 point statuses separate the readings;

Then sc-9-comprehension and sc-9-candidate-ids, filed by the DRI. The next item in the feed is wg-0.

## Tests run
- `uv run pytest -q tests/test_sc9_migrate.py`: 13 passed.
- `tests/test_sc9_migrate.py::test_c9_point_status_is_measured_on_every_choice_and_condition`: 1 passed on the new evidence, and failed under seeded bug S8.
- `uv run pytest -q tests/test_hang_guards.py`: 69 passed. That covers `usecases/` importing `tests.ce4` outside pytest.
- `uv run python tools/regen_generated.py --check`: one stale entry, `history-tests` (`migrate_soft.py` ran `git cat-file`). The git call was removed instead; then `tools/history_tests.py --check` reported "every test that reads history is listed". The migration was rerun and the probe is byte-identical.
- `uv run python tools/gate_collection.py --check --prebuilt`: "13 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers".
- `tools/select_tests.py --base $(git merge-base HEAD main)`: 51/539 units, including `tests/test_sc9_migrate.py`.
- Earlier selected tests at `a60572b3` (clean) ran on ve-mac-1: 42 units, 0 failed. The first C9 fix selected run at `f9a6a83c3` found two history-lint failures: the new test imported `measure.py`, whose recording entry point calls git. Moving the pure status builder to `c9_status.py` fixed the class; both failed tests and the C9 regression passed on targeted rerun (3 passed).
- Final selected tests: `zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` at `427f40684` plus the refreshed evidence and report ran on ve-mac-1: 42 units, 0 failed, exit 0 (210 s). The C9 regression was among the selected tests.
- `PATH=~/.elan/bin:$PATH lake build`: passed (1,270 jobs); `python3 lean/audit.py`: PASS (756 source files, 8,385 named theorem declarations). The exact review probe F1 failed before the fix and passed after it.
- Not run: the full gate, which the chain runs on the final HEAD.

## Self-review against BUILDER-CHECKLIST
1. Typed and contained Lean answers: N.A., no relayed answer, route or schema changes.
2. Deliverables: PASS with D1, C10 NOT RUN and sc-9b recorded (Plan and task rows; DRI items 1, 2). No Python copy of a decision: `tests/ce4.soft_default` is imported and every verdict is a `ve` answer. No report test.
3. Tests can fail: PASS, seeded bugs S1 to S7, each with its test.
4. Py/Lean/Rust agreement: N.A., no product change. The probe's answers are the product's own.
5. R8 binding: N.A., no new relayed field.
6. Gate evidence on final HEAD: PASS for selection and collection (above). The gate is the chain's.
7. Unsigned items: PASS, DELTA has no row. D1 and C10 are covered by DRI decision sc-9 items 1 and 2.
8. User-visible change in DELTA: PASS, none (`git diff --stat … -- ve lean rust tools` is empty).
9. Test selection: PASS, `select_tests.py` selects `tests/test_sc9_migrate.py`.
10. Lean statements: N.A., no Lean.
11. Budgets fail closed: N.A., no evaluator added. The UNKNOWNs measured are the product's three-valued answers, reported as UNKNOWN.
12. CPU/memory: PASS as measured. `check` takes 53.70 s before and 46.34 s after; peak RSS ≤ 141 MB (`answers/measurements.json`). No product change.
13. Test-removed trailers: N.A., no test removed. The collection check reports 0 refused, 0 stale and 0 malformed.
14. Both directions, cited evidence, spec re-read: PASS. `conditioned` and `drop_open_terms` each have an accept fixture and a refuse fixture (`test_rule3_refuses_a_rule_of_another_shape`, `test_rule4_refuses_…`). Every number cites `answers/`. Re-read: plan SC-9 :1461-1500, C1-C10 :1210-1224, 5.2 :1198-1207, spec 2.6 and 8.4, soft-norms 3.2.
