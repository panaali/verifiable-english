# safety-framework-proximity-tcl: src:4's TCL proximity commitment

- Status: built and ready for review. No DRI signature is reserved, and DELTA has no rows.
- What changed: rule `f6-tcl` (rules.d1.ve) now carries 1.2's sentence "Similarly to CCLs, early warning evaluations
  will be used to assess the proximity of a model to a TCL and analyze the risk posed". The span is tagged with that rule.
- Answers: exactly the three named answers move, each in the named direction (K2-L1/PROXIMITY NONE -> ALL,
  K2-L5/PROXIMITY NONE -> ALL, G3 ALL -> NONE). PLAN section 12 item 27 records each one beside its key cell.
- Open items: none. Exposures on the shared units: 2 before and 2 after, with no record added or taken away on any unit.

Ruling: reviews/dri-decisions-20261114-safety-framework-fidelity-fix-3.md item 2 (SIGNED in principle). Critical path:
reviews/dri-decisions-20261115-adv0223.md item 1. The base is main at e51bec7301, which already includes
safety-framework-case-alternatives, so this branch needs no rebase on it.

## Delivered

1. **The rule.** `f6-tcl` is f6's rule with "that level is tracked", the scratch rule from fix-3's Q2:
   "Every proposal must be followed by an assessment of proximity to each level with a risk analysis, if both that
   proposal approaches that level and that level is tracked." Its header quotes the whole src:4 sentence and starts
   `F6, 1.2`, so the rule takes F6's RS0 status (`translation.will_rules()`: a "will", narrowed by N1 as F6 is), and
   translation.py did not change. "Similarly to CCLs" carries 1.3.3's trigger, an alert threshold reached (OT1,
   `approaches`), to TCLs. "As needed" qualifies only the experts' involvement, which is the act's legend, as in F6.
   The header also records what the act does not carry: the means, "early warning evaluations will be used".
   build_document.py tags the src:4 span `rule("f6-tcl", "ot1_level_reached")`, which is how F6's own span is tagged.
   No other span's marker changed: the coverage reasons differ only in `no_trigger_stated` 1 -> 0.
2. **Regenerated** with the case's own scripts: `run.py` (results.json), then `build_document.py` (spans.json,
   coverage.json). `run.py --check` and `build_document.py --check` pass on the committed tree. environment.d1.json
   did not change, because no predicate is new. `regen_generated.py --check` is clean.
3. **PLAN section 12 item 27.** It quotes src:4, gives each moved answer beside its old key cell, and records that
   section 4.2 names only 1.3.3 as F6's source. PLAN section 6, answer-key.json and KEY-FREEZE.md are not edited.
   The frozen-key test `test_answer_key_is_the_transcription` is unchanged and passes.

### Answer moves (results.json comparison, old -> new)

| answer | key | VE on main | VE now | section 12 |
|---|---|---|---|---|
| K2-L1/PROXIMITY | NONE | NONE | ALL | item 27 |
| K2-L5/PROXIMITY | NONE | NONE | ALL | item 27 |
| G3 | ALL | ALL | NONE | item 27 |

No other answer moved. Agreement went from 260/262 to 257/262. The five disagreements are C3 and C-doc (item 23, as
on main) and the three above. Every other comparison row is the same. Other changes in results.json:
`cost.rule_candidates` went 44 -> 45 and N3's rule count 44 -> 45 (f6-tcl has its own N3 witness). The F6 rule group
and the f6 conflict cluster now list f6-tcl. K2's default sensitivity went from 1 to 0 sensitive choices, because the
answer no longer depends on the completion default. G3's two approaching alternatives went ALL -> NONE, and its two
reaching alternatives stay ALL.

Coverage: 181 bytes (the src:4 span) went from UNFORMALISED to OPEN, the same status as F6's span. D1 now has
UNFORMALISED 6,684 (was 6,865) and OPEN 8,135 (was 7,954). CHECKED is unchanged.

## exposure.py before and after

The counter resolves `HEAD` in the main checkout, so it was given this worktree's commit sha.

Before (e51bec7301, counter f4345f44):

```
counter sha256 f4345f44  case safety-framework  commit e51bec7301  state run
FACTS <- FACTS                report       | docs/usecases/safety-framework/safety-framework-fidelity-fix-2/REPORT.md:213
CASES <- CASES                report       | docs/usecases/safety-framework/safety-framework-fidelity-fix-2/REPORT.md:213
D2D3  <- D2D3                 report       | docs/usecases/safety-framework/safety-framework-fidelity-fix-2/REPORT.md:213
2 exposures on FACTS/CASES
```

After (a26d347f57, the commit with the rule, PLAN section 12 and README; counter f4345f44): the same three lines,
"2 exposures on FACTS/CASES". The detail column is shown as the record's location. The counter prints that record's
sentence, and this REPORT does not copy it.

Across every unit of the manifest (`omit_exposure`, both commits): 22 records before and 22 after, none added and
none taken away. The section-12 entry and the README name the new rule `f6-tcl`, which is no manifest unit, and they
name no unit of the manifest.

## Tests

New file `tests/test_fsf_proximity_tcl.py` (condition tests, stays selected):
- (a) `test_the_three_answers_are_pinned_beside_their_section_12_entries`: pins the three answers (old key cell, new
  answer) against results.json, answer-key.json and item 27's bullets, and checks the src:4 quote. It fails if an
  answer that disagrees with the key has no section-12 entry with that answer, or an item-27 entry records no move.
  `test_a_move_without_its_entry_or_an_entry_without_a_move_fails` checks both directions on edited copies.
- (b) `test_src4_is_carried_by_a_rule_and_not_unformalised`: checks build_document.UNITS, spans.json, the rule
  block (F6's text with "tracked"), its one-reading parse, its RS0 status, the K2 details naming f6-tcl, and the
  sentence in the pinned source when it is stored. It fails on main's build_document.py (seeded bug a).

Existing tests changed to follow the three moves (the moves are this item's subject):
- `tests/test_safety_framework.py`: RECORDED_DISAGREEMENTS gains the three (citing item 27), and 260 becomes 257. In
  `test_premises_leave_every_level_open_to_its_decider`, the "agree" check on K2 and G3 is now a check of the item-27
  answers.
- `tests/test_fsf_case_alternatives.py::test_each_alternative_is_answered_and_the_answer_holds_in_every_one`: G3 now
  expects NONE in its two approaching alternatives and in the item. G7 and G9 are unchanged. The test ids stay the
  same, and no test was taken out.

Runs while iterating: the new file, test_fsf_case_alternatives.py, and the three touched test_safety_framework ids
gave 15 passed. Also `run.py --check` and `build_document.py --check`.

### Selected run and its one failure

The first selected run (`mac-pytest.sh --select`, on 77c640ffea, committed, on GitHub Actions in 4 shards, 980 s)
had one failure: `tests/test_english_statement_blocks.py::test_every_pinned_block_has_its_python_node[fsf]`. The
pinned FSF norm blocks (`tests/data/norm-blocks/fsf.jsonl`) hold every rule block of rules.d1.ve, and f6-tcl was not
there yet. The fix follows fsf-fidelity-fix (429e7c0192, 15b7da9ada) and fix-2 (0cadd1f6c7):
- `capture_blocks.capture` for FSF only, keeping the numbered-rule blocks: 45 rows at d255cbd9f4's parent
  (77c640ffea). f6-tcl is new, Python reads it with no refusal, and every other row is unchanged apart from its
  commit. tests/test_english_statement_blocks.py now pins fsf 45, and the Lean-side totals are 122 (with f21)
  and 105 strict. `-k pinned` (4 tests, Lean included) passed: Lean reads f6-tcl as Python does.
- The saved W1 delta evidence pinned the old block list, so `docs/en-e3-norm/en-2/w1_delta.py --workers 8` was
  rerun at d255cbd9f4 on a clean tree (29 min). All 121 pinned blocks agree. Suite counts and every non-agree row
  are unchanged. Soft-rights has 1 more record, which agrees, and 65 suite units are derived from the map at
  e51bec7301. The en-2c REPORT cites the new numbers and says why it was rerun.
  `tests/test_english_statement_shadow.py -k "delta or report"` gave 7 passed.
- Then the failed id, test_english_statement_shadow.py and test_fsf_proximity_tcl.py were rerun with
  `mac-pytest.sh` on 4f34d584c4 (it ran on the VM): 27 passed.

## Seeded bugs (each planted alone, shown failing, restored)

| bug | file | failing test |
|---|---|---|
| (a) src:4's span tagged `unformalised("no_trigger_stated")` again | usecases/safety-framework/build_document.py (Python) | tests/test_fsf_proximity_tcl.py::test_src4_is_carried_by_a_rule_and_not_unformalised |
| (b) G3's section-12 entry deleted | usecases/safety-framework/PLAN.md | tests/test_fsf_proximity_tcl.py::test_the_three_answers_are_pinned_beside_their_section_12_entries (and ::test_a_move_without_its_entry_or_an_entry_without_a_move_fails) |
| (c) f6-tcl's guard "tracked" -> "critical" (the weakening mutant, checklist 19) | usecases/safety-framework/rules.d1.ve | tests/test_fsf_proximity_tcl.py::test_src4_is_carried_by_a_rule_and_not_unformalised; `run.py --check` exits 1 ("results.json is out of date"), which is tests/test_safety_framework.py::test_rerun_equals_committed_results |

Lean and Rust: no product code changed. The changed Python is use-case code (build_document.py), seeded by (a).

## Trust, DELTA, mutants

- `tools/trust_map.py --check`: K +0, S +0, D +0, G +0, tied +0, trusted +0. No allowance is needed.
- DELTA: no rows. The three keyed answers move under the DRI's item-2 decision, and they are recorded in PLAN
  section 12 as the precedent asks. No ve/, lean/ or rust/ behaviour changed.
- trust_mutants: not run. light-lane printed NOT (270 changed lines, which counts the case's generated
  results/spans/coverage). Checklist 13a applies to trusted Lean growth, and this item changes no Lean file and no
  trusted-core file. The task does not ask for a trust_mutants record.

SIZE: 5 product (build_document.py 3, rules.d1.ve 2), 144 tests, 59 other hand-written lines (PLAN 17, README 23,
en-2c REPORT 19), plus this REPORT. Generated or captured: results.json, spans.json, coverage.json,
tests/data/norm-blocks/fsf.jsonl, docs/en-e3-norm/en-2/delta.json and DELTA.md (git diff --numstat against
e51bec7301, added plus deleted).

## Notes for the DRI

- The scorer's `DEVIATIONS` table (run.py) lists item 23 only, so the three item-27 rows carry no `deviation` field in
  results.json. Adding them would be a run.py change, which the task does not expect, so item 27 is bound to the
  answers by tests/test_fsf_proximity_tcl.py instead. The scorer is untouched, as in the fsf-fidelity-fix (c)
  precedent.
- README.md is not in this item's file list. Its overlap with safety-framework-case-alternatives no longer exists,
  because that row is on main. Leaving it alone would leave false statements: 260/262, "G3 ... silent", and that the
  1.2 sentence has no formal rule. Only those lines were corrected. Its Oct 18 history line ("257 of 262") is a dated
  record and is unchanged.
- Under item 27 the rule is F6's TCL half. Section 4.2's F6 row still names only 1.3.3, and section 4 was not edited.
- The counter's `rule <id>` mistag scan reads accounting.d1.txt, which this case does not have. The header of
  `f6-tcl` still states the words its carrier does not hold (the means), so a later accounting file can tag them
  honestly.
- docs/usecases/safetyfw/safety-framework/kb10-shadow.json is kb-10b's saved evidence. No test recomputes it, and the
  FSF rows after kb-10b did not regenerate it, so this row leaves it too.
- Pre-existing failures: none of main-known-red.txt touches this case.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relay or Lean change).
2. Every deliverable built: PASS. DELIVER 1 to 3 are done, and the condition tests (a) and (b) are in test_fsf_proximity_tcl.py.
3. Tests can fail: PASS. Seeded bugs (a), (b) and (c) above.
4. Python, Lean and Rust agree: N.A. (no product path changed; `run.py --check` passes).
5. R8 binding: N.A. (no relayed answer).
6. Gate evidence matches the final HEAD: PASS. The selected run was on committed code; its one failure was fixed and that id rerun (27 passed). The chain runs the gate on the final HEAD.
7. No unsigned item: PASS. No DELTA row and no reserved signature.
8. Every user-visible change is in DELTA: PASS. There is no ve/lean/rust change. The keyed answers move under DRI item 2 and are recorded in PLAN section 12 item 27.
9. Test selection finds the tests: PASS. select_tests picks test_fsf_proximity_tcl.py, test_safety_framework.py and test_fsf_case_alternatives.py.
10. Lean statements: N.A.
11. Budgets fail closed: N.A. (no evaluator added).
12. No CPU or memory regression: PASS. This item adds one rule to 44, and run.py took 186 to 199 s here. Main was not timed; tools/bench is not affected.
13. Test-removed trailer: N.A. No test was taken out, and the G3 parameter id is kept.
14. Both directions, cited evidence: PASS. test_a_move_without_its_entry_or_an_entry_without_a_move_fails covers both, and the PLAN entry cites the source sentence and the findings.
15. The four FIX classes: PASS. The key is frozen, evidence is saved (this REPORT), and no live git diff is in the tests.
