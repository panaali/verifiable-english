# srccov-rl-claude-constitution-pilot-1121: REPORT

- **Status:** done. 0 of 3 in-scope units carried, 3 DROPPED. No DRI signature is reserved and there is no DELTA row.
- **Why:** each unit's sentence is a norm whose force is an **open reading set** with two candidates (`strict`,
  `default`). A rule line would pick one of them, and VE gives a document exactly one reading, never a guessed one. The
  map's shards could not see this because reading sets were neither carriers nor records for them (METHOD amendment 3).
- **What changed:** one new test, `tests/test_srccov_rl_claude_constitution_pilot_1121.py`, which holds the drop's
  reason, and this report. No carrier, record, derived file or product code changed.
- **Branch base:** `cebf4fd24f` (main). Test commit `b0bffe29f3`. The merge commit is the one the merge train writes.

## 0. Verify table

| unit id | row id | KEPT / DROPPED | reason (file:line) |
|---|---|---|---|
| S0443 | srccov-claude-constitution-pilot-22-1119 | DROPPED | Needs a reading choice, not a plain line. The norm unit `u0125.s04.p2` has no body because its reading set `force-u0125-s04-p2` is `open` with `strict` (`sign: false`, guard `top`) and `default` (`mode: default`, exception `decided_by: unstated`) on `denial_of_being_claude_permitted` (probe-translation.probe.md:2, `reading_sets`; body: probe-translation.probe.md:316). The run's readings queries are keyed to this set (run-20261104T0716Z/measure.py:33 `DENIAL = "force-u0125-s04-p2"`, :59 `c6-denial` unconditional and under each candidate). |
| S0553 | srccov-claude-constitution-pilot-23-1119 | DROPPED | Needs a reading choice, not a plain line. The norm unit `u0156.s03` has no body because its reading set `force-u0156-s03` is `open` with `strict` and `default` on `system_prompt_deception_permitted` (probe-translation.probe.md:2; body: probe-translation.probe.md:404). |
| S0941 | srccov-claude-constitution-pilot-42-1119 | DROPPED | Needs a reading choice, not a plain line. The norm unit `u0263.s04.p2` has no body because its reading set `force-u0263-s04-p2` is `open` with `strict` and `default` on `exploit_instruction_compliance_required`, guard `explicit_instruction_against_exploits` (probe-translation.probe.md:2; body: probe-translation.probe.md:681). The row's other 16 units are out of scope (not tagged omission). |

Paths are under `usecases/claude-constitution-pilot/run-20261119-defs-carry/` unless the cell says otherwise.

**How each unit was checked.**
- **Source text.** Each source sentence is at the map's byte offsets in the pinned body
  (`units-claude-constitution-pilot.tsv:444, 554, 942` in manage-agents reviews/source-coverage-1119). The probe body
  equals the pinned translation's body (`tests/ce4`, checked against its blob). Proof:
  `test_the_probe_unit_lies_inside_the_source_sentence`.
- **No change at main.** `git diff --stat e53db4e8fc cebf4fd24f -- usecases/claude-constitution-pilot` lists 4 files.
  The probe's only changes are the 26 rule-8 records of srccov-claude-constitution-pilot-1119. A front-matter comparison
  of the two commits gave `body same True`, `reading_sets same True` and `in-scope units same True`.
- **Not already carried.** No unit's body states any of the three predicates. Proof:
  `test_no_other_unit_states_the_open_predicate`.
- **Why the drop is the narrower option.** The two candidates differ in content (proof:
  `test_the_unit_has_no_body_while_its_reading_set_is_open`). So any body is the `strict` reading, the `default`
  reading, or something neither candidate says.
  - **`strict`** settles a reading the translation keeps open on purpose. Each set's `admission.why`, written by the
    translator, gives the text's grounds for the defeasible reading (u0109.s05/s06 for S0443 and S0553; u0253.s04 and
    u0011.s01 for S0941).
  - **`default`** needs the soft route's completion. The same admission says this "makes 'not required' an extra claim
    the source does not state".
  - **Either way**, it changes the readings answers of a reading set the run measures (c6-denial for S0443).
  - The task's drop rules cover this: it needs more than a plain line (a reading decision under `readings@1`), and it
    is the conservative direction (builder-overrides rule 2). So I did not ask the DRI.

## 1–2. Units carried, derived files

None carried, so there are no new rule or fact lines and no span or record changes. Nothing was regenerated:
`tools/fidmech/manifests.py`, `conformance/english-lean/corpus-seal.json` and `tests/data/fidmech/` are untouched.
`uv run python tools/regen_generated.py --check` at `b0bffe29f3` printed `regen_generated: checked 43 entries` with
exit 0.

## 3. Answers touched

**None.** The probe is byte-unchanged, so no answer or question changes status. The answers that **would** change if
S0443 were given a body are run-20261104T0716Z's readings queries `readings-c6-denial` (unconditional, and under
`force-u0125-s04-p2:0` and `:1`; measure.py:33, :59). Its source sentence: "Still, Claude should never directly deny
that it is Claude, as that would cross the line into deception that could seriously mislead the user." No answers/,
reports/ or sealed file was opened.

## 4. Condition test and seeded bugs

`tests/test_srccov_rl_claude_constitution_pilot_1121.py` (10 tests) holds the drop's reason for each unit:
- its probe unit lies inside the source sentence, checked by first and last words after `omit_norm`;
- it has no body while its reading set is open with at least two different candidates on its predicate;
- no other unit's body states that predicate;
- across the probe, no unit has both a body and an open reading set.

**Deviation from deliverable 4:** the task asks for a test that fails on the pre-change main and passes after, for
each kept unit. No unit is kept, so the product side has no change for such a test to detect. This test passes on
main, with this branch adding only the test. A later item that settles a reading closes the set, gives the unit a
body and updates this file.

Run: `uv run pytest -q tests/test_srccov_rl_claude_constitution_pilot_1121.py` gave `10 passed`.

**Seeded bugs.** Each was planted in the carrier `usecases/claude-constitution-pilot/run-20261119-defs-carry/probe-translation.probe.md`,
the new test was run, and the file was restored with `git checkout`. The script was `/tmp/srccov1121-seed.py`; its logs
are `/tmp/srccov1121-seed-<k>.log`.

| # | behaviour claimed | planted bug | result |
|---|---|---|---|
| 1 | no body beside an open set | `u0156.s03` given the `strict` candidate as its body | 3 failed: `test_the_unit_has_no_body_while_its_reading_set_is_open[...-23-1119:S0553]`, `test_no_other_unit_states_the_open_predicate[...-23-1119:S0553]`, `test_no_unit_has_both_a_body_and_an_open_reading_set` |
| 2 | the set stays open | `force-u0125-s04-p2` status set to `chosen` | 2 failed: `test_the_unit_has_no_body_while_its_reading_set_is_open[...-22-1119:S0443]`, `test_no_unit_has_both_a_body_and_an_open_reading_set` |
| 3 | unit lies inside its sentence | `u0263.s04.p2` span moved 200 bytes back | 1 failed: `test_the_probe_unit_lies_inside_the_source_sentence[...-42-1119:S0941]` |
| 4 | no other line states the predicate | `u0165.s01`'s body predicate set to `denial_of_being_claude_permitted` | 1 failed: `test_no_other_unit_states_the_open_predicate[...-22-1119:S0443]` |

There are no Lean, Python or Rust product changes, so no language needs a seeded bug of its own. review-ready's
`[mutants]` check should report "no product code changed".

## Tests run

- New test file: 10 passed (above).
- Selected run at `b0bffe29f3`: `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` exited 0 on 6
  shards, with 189 units passed and 0 failed. The shard lines are saved in `selected-run.txt` beside this report.
- The new test stays selected: `select_tests.py --paths <probe> --explain` lists
  `tests/test_srccov_rl_claude_constitution_pilot_1121.py: names usecases/claude-constitution-pilot/run-20261119-defs-carry/probe-translation.probe.md (static)`.
- Full gate: not run by me (task rule). The chain runs it on the final HEAD.
- Light lane / trust mutants: no sweep was needed, because there is no product or trusted-core change.

## Freeze

The item merges at the merge train's commit on top of `cebf4fd24f` (or a later main). It touches no answer and does
not change the probe, so later reads of the constitution pilot need no re-pin for this item.

SIZE: 0 product, 95 tests, 162 other hand-written lines (this report and selected-run.txt).

## Notes for the DRI

- **The map's label does not hold for these units.** All three units the map tagged 'none: translation omission' in
  these rows are reading-set units. Reading sets were invisible to the shards (METHOD.md amendment 3, SUMMARY.md:48:
  "s4 asks the planner to rule on whether reading sets should count for this format"). The probe has a fourth unit of
  the same shape, `u0036.s05` (S0117, `force-u0036-s05`). It is in another row and is not touched here.
- **What it would take to carry them.** Carrying any of the three is a reading decision: choose `strict` or `default`
  for the open set, or rephrase. It belongs to whoever owns the constitution pilot's readings, not to an omission row.
  The architect page already asks for a constitution re-run on today's soft norms before any constitution-driven
  feature (srccov-features-20261120.md:38).

## Spec re-read

- "a plain line of the document's own profile carries the sentence", checked against architect
  srccov-features-20261120.md:17. Each unit needs a reading choice, not just a line.
- "ambiguous sentence is refused or rephrased, never guessed", checked against CLAUDE.md ("What VE is").
- "In .ve.md front matter, `reading_sets`/`readings` are neither carriers nor records", checked against METHOD.md:60.
  This is why the map saw no carrier.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relay or Lean answer was touched.
2. Deliverables built, no rule broken: PASS.
   - The verify table is in section 0.
   - Deliverables 1–3 are empty because no unit was kept.
   - The test is built; its deviation is stated in section 4.
   - Evidence: `tests/test_srccov_rl_claude_constitution_pilot_1121.py`.
3. Tests can fail: PASS. Four seeded bugs, each failing named tests (section 4).
4. Py/Lean/Rust agree: N.A. No product code changed.
5. R8 binding: N.A. No binding changed.
6. Gate evidence matches final HEAD: PASS for the selected run at `b0bffe29f3` (`selected-run.txt`). The full gate is
   run by the chain on the final HEAD.
7. No unsigned item: PASS. No DELTA row and no reserved signature.
8. User-visible change in DELTA: N.A. Nothing user-visible changed (probe byte-unchanged; `regen_generated.py --check`
   exit 0).
9. Selection finds the tests: PASS. `select_tests.py --paths <probe> --explain` lists the new test.
10. Lean statements: N.A. No Lean change.
11. Budgets fail closed: N.A. No budget code.
12. CPU/memory: N.A. No product change. The new test runs in about 1.4 s locally.
13. Test-removed trailer: N.A. No test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS.
    - Passing direction: the current probe passes, 10 passed.
    - Failing direction: four mutants of the probe fail.
    - Each claim above names its command.
    - The spec re-read list is above.
15. No overclaim, no silent cut, every check can fail, limits: PASS.
    - Universal words in this report: "None carried", "no answer", "no other unit". Each is backed by
      `test_no_other_unit_states_the_open_predicate`, the front-matter comparison or `regen_generated.py --check`.
    - The deliverable-4 deviation is stated, not hidden.
    - Each new test has a mutant.
    - Limits: N.A.
