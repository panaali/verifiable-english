# pf-f16-without-fix: f16-without per the N2 ruling (reading (c))

Status: built, all condition tests pass; no DRI signature reserved; DELTA none; no stop rule hit.
HEAD: the commit that adds this report (branch feature/pf-f16-without-fix, merge base 9f7d4bd179, main merged at 02688e1fd3).
Changed: f16-without-noinput reads "... if leadership_decision, unless sag_recommendations_given"; f16-without-nodelib
"... if leadership_decision"; new predicate `sag_recommendations_given`; run.py witness_for tries the exception attempt.
MEASURED: N3 NONE, C2 NONE, C-doc NONE, moved [], 236/239; m6 and without-N2 change exactly C-doc and C2; N1 as main.
Open: none. One wording note for the DRI (the new legend quotes one more source phrase than the ruling; Notes below).

Ruling: fable-team/architect/rulings/pf-f16-without-n2-20261116.md (manage-agents), sections 2-6, signed by the DRI
2026-11-16 (reviews/dri-decisions-20261116-pf-f16-without-n2.md item 2).

## What changed (task items 1-7)

| Task item | Change | Commit | Test |
|---|---|---|---|
| 1 rules.d1.ve | noinput: `Rule 1. Every situation need not have Leadership informed by SAG, if that situation is classified as "leadership_decision", unless that situation is classified as "sag_recommendations_given".`; nodelib: `Rule 1. Every situation need not have the SAG take part in the decision, if that situation is classified as "leadership_decision".`; headers, f16-informed, PRECEDENCE, N2_PRECEDENCE as on main | 23fb5b60a9 | `test_f_guards_drop_decided_without_sag_and_noinput_names_its_limit`; `test_f16_without_reads_n2_as_ruled` (PRECEDENCE and N2_PRECEDENCE pinned whole) |
| 2 pf_vocabulary.py | base situation predicate `sag_recommendations_given` (legend: Notes 1); comment with the "given before the decision / still deliberating = none given" rule and the modelling rule; `decided_without_sag` kept (legend unchanged) with a comment that no rule reads it; run.py `WITNESS` gets the same comment (WITNESS["C2"] is in fidmech/bindings.json, a JSON file, so the comment sits at `WITNESS = _B["WITNESS"]`) | 23fb5b60a9 | `test_f16_without_reads_n2_as_ruled`; `test_g_decided_without_sag_is_inert_in_the_c2_witness` |
| 3 run.py witness_for | new `witness_attempts`: (1) guard's positive atoms; (2) those plus the positive atoms of each `unless` entry (`for exception in rule["unless"]`, `guard_atoms(exception)[False]`) of every rule `precedence()` puts over the block, minus the atoms the rule tests negatively, only when it adds an atom; (3) every atom. Docstrings of both updated | 23fb5b60a9 | `test_a_witness_for_returns_a_model_for_each_f16_rule`; `test_g_*` |
| 4 PLAN.md | N2 row (3.1): the precedence decides the case where both rules apply; the clause's own scope (its "i.e." limit) is a decision with no SAG recommendation given; cites the ruling. New section 12 item 31. Section 6 and m6 (section 11) untouched | 7908093d9f | `test_plan_and_readme_record_the_reading_and_the_modelling_rule` |
| 4 README | "Case modelling: SAG recommendations" with the modelling rule | 7908093d9f | same test |
| 5 accounting | omission exposure before/after (below); accounting.d1.txt unchanged: both filibuster entries keep `restates`, now carried | 7908093d9f (evidence) | `tests/test_safetyfw_accounting.py` 72 passed (/tmp/f16-tacc.txt) |
| 6 regenerate | environment.d1.json (pf_vocabulary.py), spans.json/coverage.json (build_document.py), results.json (run.py, "236 / 239 (2016.1 s)", /tmp/f16-run.log), conformance/english-lean/lexicon-report.json (139 -> 140 symbols; 43 valid, 0 invalid), docs/usecases/safetyfw/openai-preparedness/accounting.json (`--report`), docs/kernel/ownership.json and kb-10d/functions-under-passing.json (five keys traced again) | 23fb5b60a9, 73e87b7c4e, 69dbb6d33b | `--check` of build_document.py, stage0.py, measure.py exit 0 (output empty); `tests/test_ownership_floor.py` 25 passed (/tmp/f16-own-t.txt) |
| 7 f7 test | `test_f16_without_keeps_its_guard_until_n2_is_ruled` replaced by `test_f16_without_reads_n2_as_ruled` (Test-removed trailer in 69dbb6d33b); module docstring and `test_touched_rules_keep_a_witness_model`'s updated | 77f30cf75e, 69dbb6d33b | `tools/gate_collection.py --check --prebuilt`: rc 0, "1 removed by a trailer, 0 refused, 0 stale and 0 malformed" (/tmp/f16-gc2.txt) |

## Condition tests (tests/test_pf_f16_without_fix.py)

All pass in the selected run (`mac-pytest.sh --select`, /tmp/f16-select.log: "tests/test_pf_f16_without_fix.py: exit 0
in 264.3 s"; "tests/test_pf_f7_timed_act.py: exit 0 in 127.0 s"). The inertness test was trimmed after that run and rerun
alone: 1 passed (/tmp/f16-t3.txt); the records test was added later: passed (/tmp/f16-t4.txt).

| Condition | Test |
|---|---|
| a | `test_a_n3_is_none_in_results`, `test_a_witness_for_returns_a_model_for_each_f16_rule` |
| b | `test_b_noinput_selects_need_not_on_a_case_silent_on_sag_input` |
| c | `test_c_nodelib_selects_on_every_leadership_decision` |
| d | `test_d_c2_and_c_doc_mutants_and_narrowings_in_results`, `test_d_m6_moves_c2_and_c_doc_live` |
| e | `test_e_no_answer_moved_against_the_key_and_the_merge_base` (this round's snapshot answers-at-merge-base.json and the f7 round's) |
| f | `test_f_guards_drop_decided_without_sag_and_noinput_names_its_limit` |
| g (i) | `test_g_an_exception_whose_limit_contradicts_the_guard_gives_no_witness` (f16-informed's guard patched to `not sag_recommendations_given`) |
| g (ii) | `test_g_only_f16_informed_has_the_exception_attempt`, `test_g_f16_informed_is_witnessed_by_the_exception_attempt` |
| g (iii) | `test_g_decided_without_sag_is_inert_in_the_c2_witness` (C2 and C-doc with N2, C2 under m6) |

## MEASURED (results.json at 73e87b7c4e against main's at 9f7d4bd179, saved as answers-at-merge-base.json)

- N3: NONE (key NONE). C2: NONE (key NONE). C-doc: NONE (key SOME(final & bperm); a disagreement on main too).
- moved: [] against main's results.json and against the frozen key column; agree 236/239 as on main.
- mutants: changed and exact equal to main's for m1-m6, all exact; m6 changed [C-doc, C2], C2 to SOME(RS6=req&RS7=noinput).
- without_narrowings: N2 changed exactly {C-doc, C2}, equal to main's; N1 changed the same 35 items as main's, N3 among them.
- results.json diff: only the N3 witness models (decided_without_sag gone from both f16-without models;
  sag_recommendations_given in f16-informed's). Metrics and cost unchanged.
- Live probe (/tmp/f16-probe.py before the cache fix, then the tests): witness_for gives f16-informed
  {leadership_decision, sag_recommendations_given}, f16-without-noinput and f16-without-nodelib {leadership_decision}
  (with every level reached), as the ruling's section 3 measured.

## Accounting and omission exposure (task item 5)

Command: `tests/omission_rule.exposures("openai-preparedness", [f16-without-noinput, f16-without-nodelib, f16-informed])`;
outputs saved whole: exposure-before.txt (main) and exposure-after.txt (7908093d9f).

| Unit | Before | After |
|---|---|---|
| f16-without-noinput | mistag "For the avoidance of doubt" (reading N2); mistag "i.e., the SAG does not have the ability to filibuster" (restates) | mistag "For the avoidance of doubt" (reading N2); plan12 (item 31) |
| f16-without-nodelib | the same two mistags | mistag "For the avoidance of doubt" (reading N2); plan12 (item 31) |
| f16-informed | 2 mistags, 1 loss | the same, plus plan12 (item 31) |

The filibuster entries now resolve as `restates`: noinput's carrier is the legend of `sag_recommendations_given` (read by its
`unless`), nodelib's the legend of its act `sag_participation`, which now quotes the sentence (Notes 1). Both entries keep
"filibuster" (`test_nested_quote_keeps_its_inner_words_on_the_real_header` passes). The "For the avoidance of doubt" mistag
is the same before and after; this task does not change it (Notes 3).
`uv run python usecases/safetyfw_accounting.py openai-preparedness --source <pinned pf-v2.txt> --check`: with the first legend draft
(the ruling's "the decision is made" and curly apostrophes) rc 1: "f16-without-noinput: unaccounted word 'make' ...", "... "sag'"
...", "f16-without-nodelib: unaccounted word "sag'" ..." (/tmp/f16-acc1.txt); with the committed legends rc 0, "101 blocks, 509
unaccounted words in 70 blocks, 15 blocks with a loss" (/tmp/f16-acc2.txt; main: 513 unaccounted words).

## Seeded bugs (seeded-bugs.json; each planted, run, then restored with `git checkout <file>`; tree clean after each)

1. s1 rules.d1.ve: noinput's guard gets `and that situation is classified as "decided_without_sag"` back. Fails
   `test_b_noinput_selects_need_not_on_a_case_silent_on_sag_input` ("assert ('f16-without-noinput' in {'f16-informed'})")
   and `test_f_guards_drop_decided_without_sag_and_noinput_names_its_limit` ("assert 'decided_without_sag' not in
   {'decided_without_sag', 'leadership_decision'}"). 2 failed (/tmp/f16-seed1.txt).
2. s2 rules.d1.ve: noinput's `unless ...` removed (variant b). Fails `test_a_witness_for_returns_a_model_for_each_f16_rule`
   ("{'f16-informed': None, ...}"). 1 failed (/tmp/f16-seed2.txt).
3. s3 run.py: the exception attempt removed (variant c0). Fails `test_a_witness_for_returns_a_model_for_each_f16_rule`
   ("{'f16-informed': None, ...}"), `test_g_only_f16_informed_has_the_exception_attempt` ("assert [] == ['f16-informed']"),
   `test_g_f16_informed_is_witnessed_by_the_exception_attempt`. 3 failed (/tmp/f16-seed3.txt).
4. s4 run.py: the attempt ignores the negated atoms (`- blocked` dropped). Fails
   `test_g_an_exception_whose_limit_contradicts_the_guard_gives_no_witness` ("assert 3 == 2"). 1 failed (/tmp/f16-seed4.txt).
5. s5 pf_vocabulary.py: the legend loses its "i.e., ... ‘filibuster’" quote. Fails `test_f16_without_reads_n2_as_ruled`.
   1 failed (/tmp/f16-seed5.txt).

Languages: only Python and VE case files changed (no Lean, no Rust); Python seeded bugs s3, s4 (run.py) and s5 (pf_vocabulary.py).

## Checks run

- Selected run (`zsh mac-pytest.sh --select -- --base 9f7d4bd179 --run`, ve-cloud-2, 2798 s, /tmp/f16-select.log): 1 failure,
  `tests/test_ownership_floor.py::test_ownership_json_is_of_the_traced_inputs` (ownership.json names run.py's old blob).
  Fixed by tracing the five keys again (`tools/ownership_trace.py run <key> --out /tmp/f16-own --jobs 4` x5, 734 units, no
  unit with rc != 0; `verdict`; `passing-functions`; /tmp/f16-retrace.log): totals unchanged, RSP 100/126, PF 228/239,
  FSF 244/262, agent-policy 0/42, eligibility 269/269. functions-under-passing.json moved one counter
  (`executable_sha256.<locals>.<lambda>`, safety-framework 1), as the previous retrace (89f865f36e) moved it. Then
  `tests/test_ownership_floor.py`: 25 passed.
- `cd lean && lake build`: "Build completed successfully (1475 jobs)" (/tmp/f16-lake.txt); no Lean file changed.
- `tools/trust_map.py --check`: "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0", PASS.
- Light lane: `NOT 1589 changed lines outside generated files > 150 (15 files)`. `tools/trust_mutants.py --plan`: "definitions 0,
  mutants 0, to_run 0": no trusted Lean definition changed, so no sweep has anything to run; none was started.
- Full gate: not run here (the chain runs it on the final HEAD).

## DELTA

None. No VE checker, relay, schema or CLI output changed; the use case's keyed answers did not move (moved []). trust_map +0,
so no R6/R16 row.

## Cost

run.py full regeneration 2016 s; selected run 2798 s (remote); five-key ownership retrace about 2 h 07 min (22:30-00:37Z,
load 40-50); the new test file 264 s in the selected run (the live C-doc queries dominate; the inertness test was then cut
from four C-doc queries to one).

SIZE: 46 product (rules.d1.ve 4, pf_vocabulary.py 16, run.py 26), 293 tests, 31 other hand-written lines (PLAN 19, README 12) plus this report.

## Notes for the DRI

1. Legend wording. The ruling's legend for `sag_recommendations_given` ends "without them the decision is made “without the
   SAG’s participation”, and the SAG “does not have the ability to ‘filibuster’”". Committed: "... (Appendix B: “informed by
   SAG's recommendations”; without them OpenAI Leadership “can also make decisions without the SAG's participation, i.e., the
   SAG does not have the ability to ‘filibuster’”)": the same three quotes, as one contiguous quote of the source sentence.
   Reason: with the ruling's words the accounting check fails ('make', "sag'", above) and the omission rule's carrier lacks
   "i.e.", so the filibuster entry stays a mistag. Likewise `sag_participation`'s act legend ("Appendix B: decisions without
   the SAG") now quotes the sentence, as nodelib's carrier (task item 5). The predicate, its arguments and its meaning are as ruled.
2. `unless` read entry by entry: the new attempt does so. The existing line `unless = guard_atoms(rule["unless"])` in
   witness_for passes the list itself, so `guard_atoms` skips its first entry (it reads `node[1:]`). Only the `blocked` set is
   affected (an `unless` atom may be set in attempt 3, where VE then does not select the rule: a missed witness, never a wrong
   verdict). Left as on main: changing it would change the N3 harness beyond this task.
3. The "For the avoidance of doubt" `reading N2` entries of both f16-without units were mistags before and still are
   (no carrier holds "avoidance" and "doubt"); not in this task.
4. f16-informed's own entries ("Making all final decisions", "SAG's" restates) are mistags on main and here; unchanged.

## Spec re-read

- Rules against ruling section 4 (lines 78-83): word for word.
- `witness_attempts` against ruling section 3 ("the guard's positive atoms plus the `unless` atoms of the rules PRECEDENCE puts
  over this one") and task item 3 ("read entry by entry", "skip it when it adds nothing").
- PLAN N2 row and item 31 against task item 4; PLAN section 6 and m6 not edited (`git diff 9f7d4bd179 -- usecases/openai-preparedness/PLAN.md`: hunks at the N2 row and after item 30 only).

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no route, schema or relay changed.
2. Every deliverable built: PASS, the table above maps task items 1-7 to commits and tests; nothing cut.
3. Tests can fail: PASS, seeded bugs s1-s5 (seeded-bugs.json) each fail a named test.
4. Python, Lean and Rust agree: N.A., no checker code changed; PF answers equal main's (`test_e_no_answer_moved_against_the_key_and_the_merge_base`).
5. R8 binding: N.A., no field read from a Lean answer added.
6. Gate evidence matches HEAD: PASS, main merged (02688e1fd3); the chain runs the gate on the final HEAD.
7. No unsigned item: PASS, no DELTA row; trust_map +0 (`tools/trust_map.py --check`).
8. Every user-visible change in DELTA: PASS (none): moved [] (`test_e_no_answer_moved_against_the_key_and_the_merge_base`); no ve/ code changed.
9. Test selection finds the tests: PASS, the selected run picked up tests/test_pf_f16_without_fix.py, tests/test_pf_f7_timed_act.py and tests/test_ownership_floor.py (whose failure it caught).
10. Lean statements: N.A., no Lean changed.
11. Budgets fail closed: N.A., no budget or deadline code; the tests use no sleeps or timeouts.
12. No CPU regression: PASS, run.py 2016 s against 1962.9 s in the f7 round (same machine class, under load); the new attempt runs only for f16-informed (`test_g_only_f16_informed_has_the_exception_attempt`).
13. Test-removed trailer: PASS, `tools/gate_collection.py --check --prebuilt` rc 0, 1 removed by a trailer.
14. Both directions: PASS, b checks both models (with and without recommendations); g (i) is the refusal side of g (ii); f checks noinput has its `unless` and nodelib has none.
15. Overclaim, silent cut, checks can fail, limits: PASS, each number above names its command or log; no deliverable cut; s1-s5; limits N.A.
