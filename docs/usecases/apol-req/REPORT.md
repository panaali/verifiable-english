# apol-req: the policy family's requirement register and its measured level

Status: built, selected tests pass (GitHub Actions selection run, then the 2 tests it flagged were fixed and rerun: 134 passed); full gate left to the chain. No DRI signature is needed.
What changed: `usecases/agent-policy/requirements.json` (46 rows), `usecases/agent-policy/level.py` (relay reader), `tests/test_agent_policy_level.py`, a named test for cedar-attributes, README "Measured level".
Level: **1,944 verified bytes of 3,055 source bytes** (35 VERIFIED rows of 46). Bytes moved by this item: none (it measures).
Open: the OPEN rows below are the family's next items; DELTA none; trust +0.

## Delivered (task rows)

| Task row | Delivered by |
|---|---|
| (1) register, one row per unit, bytes computed, VE text, linked cases/tests, family for OPEN | `requirements.json` (71002fa3e, rebuilt in 03d006297); `test_rows_are_taken_from_the_named_sources`, `test_live_register_passes` |
| rows taken, not invented: 26 rules, 8 PLAN 7 findings, 4 PLAN 2 out-of-scope bullets, 6 PLAN 10 rows, cedar claim, gatekeeper operation | same test counts each source section and compares the 26 rule statements with the README column |
| frozen header (UTC date, SHA-256 of the rows, basis verbatim); appended rows dated, never edited | header `frozen_utc` 2026-10-29, `rows_sha256`, `basis`; `test_an_edited_frozen_row_refuses_the_whole_register`, `test_appended_rows_need_a_date_and_a_new_id` |
| (2) `level.py`, relay only, prints verified/source/per-family OPEN bytes, fails on a disagreeing linked case or unchecked VE text | `level.py`; `test_main_exits_one_on_a_failing_register_and_zero_on_the_live_one` |
| (3) tests on both sides; the four named seeded bugs | `test_each_check_at_and_around_its_boundary[flipped linked verdict / bytes ±1 / verified, no case]`, `test_an_open_row_with_no_feature_family_is_refused`, each with its accepting neighbour |
| (4) README "Measured level": basis, numbers, the remeasure line | README; `test_readme_states_the_measured_level` |

"CHECKED VE text on main", as a relay: an agent-policy file must hash to the digest `results.json` records as the input VE checked (`inputs`), rule names must be in `policy.manifest.json` whose `text_digest` is the current `policy.ve`, and record ids must be actions in `results.json` (re-established by `tests/test_agent_policy_rerun.py`). Cedar and gatekeeper rows count only when their named tests pass; `level.py` runs them through `tools/nested_pytest.py`. The suite's live test checks that they exist, since the suite runs them itself.

Linked cases compare the key with `results.json`: `action:aNN` verdict and positive/negative/open sets (M1/M2), `report:aNN` the rule-25 status, `policy:<field>` the policy summary (`gap_tools` less `(an undeclared tool)`, which the key admits as `unnamed_tool: gap or OPEN`; `required_overlaps` as a subset, as PLAN 7 says), `obligation:covered`, `default:sensitive`.

## Measured level and the line for usecase-levels.tsv

`uv run python usecases/agent-policy/level.py` on 77a78084d: verified 1944, source 3055, exit 0. The line a remeasure appends (I did not edit manage-agents):

```text
2026-10-29T01:14Z	agent-policy	1944	3055	requirement register (apol-req)	ve usecases/agent-policy/requirements.json, level.py (77a78084d)
```

The three largest OPEN byte groups, the family's next items: **speech acts 445 B** (scope-3, speech-1, -4, -5, -6; apol-assent), **the classifiers PLAN section 2 puts outside VE 241 B** (scope-1, finding-8), **numbers 134 B** (scope-2). Then information flow 111 B (speech-2; apol-flow), Cedar permit/forbid via W1 95 B (scope-4), time 85 B (speech-3; apol-time), the full Gatekeeper template 0 B.

## Choices recorded (no plan file was edited)

- Statements of rules 14 and 19 are taken verbatim from the README column, including "(D1)"/"(D2)".
- PLAN 2 and 10 rows got one requirement statement each, as a policy author would state it. A row spanning several families names one: scope-2 (numbers and time) is numbers; speech-2 (who asked: prompt injection) is information flow; speech-3 (standing permissions until revoked) is time; finding-8 (where VE forced a choice: (iii) limit and (iv) containment reduced to tool facts) is classifiers.
- The 7 VERIFIED PLAN 7 findings link the key's policy-level cases; rule 12 (D4) links `policy:never_deciding`, rule 14 (D1) adds `policy:satisfiable_pairs`, and rules 11 and 19 add the NOT-COVERED actions their wording leaves out (a36, a27).
- cedar-attributes had no test of its claim; `tests/test_cedar_attributes.py::test_usecase_claim_holds_on_its_model` runs `ve evaluate` on `claim.ve` and is its named test.
- Selection fixes: `tools/difffuzz_corpus.py` excludes the register (a no-input data file); `tests/history-dependent.json` (regenerated with `regen_generated.py --write`) lists the level test, because `level.py` can run nested pytest.

## Seeded bugs (Python only; no Lean or Rust changed)

Listed with files and failing tests in [mutants.json](mutants.json); each was planted, shown failing, and restored. S1 verdict ignored; S2 bytes as characters; S3 VERIFIED without a case; S4 OPEN with family null (first survived a row-only assertion; the test now checks the refusal reason, fa4818738); S5 VE text not compared with the checked inputs; S6 overlaps always agree; S7 failing named test counted; S8 frozen hash unchecked (all in `usecases/agent-policy/level.py`); S9 the difffuzz exclusion misspelt (`tools/difffuzz_corpus.py`).

## Trust, DELTA, size

- `tools/trust_map.py --check`: K +0, S +0, D +0, G +0, trusted +0; no new trusted definitions, so no R16 mutants or FOLLOW-UPS row.
- DELTA: none (no answer changes, so no DELTA.md).
- Size: 635 hand-written lines plus this report and mutants.json (~690). That is over the ~600 target: the register's 57 data lines and the report count too. The reader and tests were compacted once (ece7cf341). No deliverable was cut.
- Pre-existing red tests: none met in the selection.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed. The reader's own inputs are retyped field by field: `test_each_row_field_retyped_is_refused`, `test_malformed_register_results_key_or_manifest_fail_without_raising`.
2. PASS: the task-row table above, and `git diff main...HEAD` was read. There is no Python copy of a VE decision (the reader compares key and results) and no new report test on live git.
3. PASS: S1–S9 in mutants.json. Comparators fail on a changed value (`flipped linked verdict`), on bool for int (`test_each_row_field_retyped_is_refused[True-bytes]`), on a missing record (`case action:a99`) and on empty input (`verified, no case`, `measure(register=[])`).
4. PASS: valid inputs still pass with reordered lists (`reordered deciding rules`), an extra overlap (`overlap extra`) and multibyte statements (`bytes as UTF-8`). No three-language path.
5. PASS: undeclared names are refused for rule (`rule outside manifest`), record (`record outside log`), case (`case policy:bogus`), file (`unchecked file`), a duplicated id (`test_appended_rows_need_a_date_and_a_new_id`) and an extra field (`extra=1`).
6. PASS: the evidence commit list is above, from `main..HEAD --no-merges`. The chain runs the gate on the final HEAD.
7. PASS: no DELTA row, no trust growth. Every exit code is tested (`test_main_exits_one_...`: failing row, unreadable JSON, absent file).
8. N.A.: no user-visible VE output changed; usecase files and tests only.
9. PASS: `tools/select_tests.py --base $(git merge-base HEAD main)` selects `tests/test_agent_policy_level.py`, `test_difffuzz.py` and `test_history_tests.py`, which caught two real issues.
10. N.A.: no Lean statement or proof changed.
11. N.A.: the reader runs no evaluator and has no budget. A 10,000-deep and a 100,000-deep input fail closed (`test_malformed_...`, `test_main_exits_one_...`). Tests use no sleeps or timeouts; the cedar test uses `HANG_TIMEOUT`.
12. N.A.: no checker or renderer path changed; the reader runs in about 0.1 s without named tests.
13. N.A.: no test was removed or renamed on main. `test_live_register_passes_with_its_named_tests_run` was renamed within this branch before any merge.
