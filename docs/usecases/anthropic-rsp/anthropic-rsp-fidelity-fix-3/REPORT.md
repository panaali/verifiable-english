# anthropic-rsp-fidelity-fix-3: the union-rule audit's 10 units

Open questions for the DRI: none. No STOP rule fired, no DRI question was sent, and this item reserves no signature.

The item is cycle 3 of the RSP fix cycle. It covers the ten units that fail the union rule on VE main 175814252d
(DRI audit-stability addendum 6, items 39-41; reviews/audit-c2-rspbase-20261112.md section 29). The branch was
synced to main 9be13b93de, a fast-forward; main did not change any file under usecases/anthropic-rsp.
Each fix is a translation fix only. There is no ve/, lean/ or rust/ change and no key edit.
PLAN section 12, item 22 records the fixes (`usecases/anthropic-rsp/PLAN.md`).

## Units changed, by checklist class

The checklist is prompts/translation-fidelity-checklist.md. Each class below is the one the seat named.

| Unit | Class(es) | Finding (seat, where) | Fix |
|---|---|---|---|
| f7-publish [K1] | 1, 11 | 1515ZB sess-2: "The decision-explanation conjunct is absent"; the header "stops at 'discussing the risks of our systems'" | The header quotes S:11 in full. The act names both parts, "{0} have Risk Reports on risks as well as continuation determinations published" (79 characters). The legend quotes the full sentence. The 3.5 restatement is kept. |
| f16-share-one-week [K14, D5] | 2 | 1515ZB sess-5: "replacing the explicit existential minimum ... its legend supplies only '3.6.2 at {0}'"; relay split (Opus NOT, Astra REAL) | The act keeps the source's group name "the external reviewers" and picks no quantifier. The legend of `shared_with_reviewers` quotes the full 3.6.2 sentence, "with one or more external reviewers within one week of submitting the same report to our Board and LTBT", and notes that the next sentence names the group. |
| f23-publish [K17] | 1 | 1515ZB sess-8: "without specifying the comparison baseline" | The act is "{0} have the update published with its prior-draft differences in the Change Log" (80 characters). The legend quotes the full 4.8 sentence and keeps "prior to or on its effective date". |
| f11-goal-missed [K22a] | 1, 7 | 1515ZB sess-3: "the Roadmap-changes conjunct is not independently represented"; the guard is an "added restriction" | One duty with no guard: `roadmap_review_addressed`, "{0} have Roadmap changes as well as missed goals addressed in a Risk Report". The legend quotes review item 3. The predicate is renamed from `goal_miss_addressed` and merged, so the predicate count does not grow. |
| FACTS / t4-suff [T5] | 1 | 1515ZB sess-8; REAL by both adjudicators (item 28 Q05): `scenario_2` was occurrence alone, "dropping the s[ubject's determination]" | `scenario_2` is now an open term decided by `we` ("if we determine"). It is OT1's T4 determination, as OT15 is branch (1)'s. Its legend quotes the T4 sentence. The t4-suff header quotes the full sentence. The formulas of t4-suff and t4-only-if (RS3o = iff) are unchanged, so they stay consistent. RS3c = result stays excluded. |
| f13-redact-p [C4, C-doc] | 3, 11 (Astra also 7) | 1557ZA opus round 1, astra round 2: "The rule drops the regular-clearance version" | The header quotes the S:14 span with no "...". The permission act is "{0} have material redacted from the public as well as regular-clearance versions" (80 characters). The reasons list stays open (`redaction_reason_listed`; the legend keeps "include but are not limited to"). |
| f12-approval [N4, N5] | 5 | 1515ZB sess-4: "Submission for approval does not guarantee approval" | The act is the submission, `executive_submitted`, "{0} have its Risk Report sent to the CEO with the RSO" (renamed from `executive_approved`). The legend keeps "for final review and approval" and quotes step 3. |
| f6-maintain [N4, N5] | 1, 11 | 1515ZB sess-1; REAL by both (arms-cf section 0) | The header and the legend of `roadmap_maintained` quote the full S:11 sentence: the goals, and charting progress and raising the bar over time. |
| f10-candid-default [N4, N5] | 1, 11 | 1515ZB sess-2; REAL by both (item 28 Q01): the legend "omits both specified subjects" | The header and the legend of `candid_reports` carry "about how we see the risks of our systems and our state of preparedness for them". |
| f18-rso [N4, N5] | 1 | 1515ZB sess-6; REAL by both (item 28 Q04) | The legend of `rso_maintained` quotes 4.1, "a designated member of staff who is responsible for the implementation of this policy". The six listed duties stay LABELLED (`s4-rso-duties` in spans.json; test `test_f6_f10_f18_legends_carry_the_dropped_qualifiers`). |

Units per class: class 1: 7 (f7, f23, f11, FACTS, f6, f10, f18); class 2: 1 (f16); class 3: 1 (f13); class 5: 1
(f12); class 7: 1 (f11; f13 in Astra's reading); class 11: 4 (f7, f13, f6, f10). Classes 4, 6, 8, 9 and 10: none.

No other block changed. The two renamed predicates were each used by one rule only: each changed act appears in
exactly one line of rules.d1.ve (a `grep -c` on each act gives 1).

The accounting sidecar `accounting.d1.txt` was updated for f7, f11, f12, f16, f18, f23 and t4-suff. The saved
`docs/usecases/safetyfw/anthropic-rsp/accounting.json` was regenerated by
`usecases/safetyfw_accounting.py anthropic-rsp --check --source <the pinned rsp-3.4.txt, sha256 c7de7fe2...>
--report ...`. Its output: "85 blocks, 198 unaccounted words in 39 blocks, 4 blocks with a loss {'1': 5, 'limit 9':
1}, 0 of 96 quotes unanchored". The f11 and f18 class-1 losses are gone; before the fix there were 6 blocks with a
loss, {'1': 7}.

## Answers, old -> new

Evidence: `answers.json` in this directory. It compares results.json at merge base 9be13b93de with the branch's
results.json, regenerated by `run.py`, all 126 items: 110 -> 110 agree with the key, `moved: []`.

| Item | Key | Old | New | Unit fix |
|---|---|---|---|---|
| K1 | ALL | ALL | ALL | f7-publish |
| K14 | ALL | ALL | ALL | f16-share-one-week |
| D5 | ALL | ALL | ALL | f16-share-one-week |
| K17 | ALL | ALL | ALL | f23-publish |
| K22a | ALL | ALL | ALL | f11-goal-missed |
| K22b | NONE | NONE | NONE | f11-goal-missed |
| K7 | ALL | ALL | ALL | f12-approval (f12-share reads `risk_report_approved`, unchanged) |
| T1 | ALL | ALL | ALL | FACTS |
| T2b | SOME(iffo) | SOME(RS3o=iff&RS3i=suff \| RS3o=iff&RS3i=iff) | the same | FACTS |
| T3 | ALL | ALL | ALL | FACTS |
| T4b | SOME(iffo & iffi) | SOME(RS3o=iff&RS3i=iff) | the same | FACTS |
| T5 | ALL | ALL | ALL | FACTS |
| T6 | NONE | NONE | NONE | FACTS |
| T7 | SOME(result) | NONE | NONE | FACTS (PLAN section 12 item 21 entry; the fix-2 ruling, item 2) |
| C4 | NONE | NONE | NONE | f13-redact-p (`basis.different_acts` names the new act) |
| C-doc | SOME(rel) | NONE | NONE | f13-redact-p (section 12 item 21 entry) |
| N4 | NONE | UNDECIDED | UNDECIDED | f6, f10, f12, f18 (UNDECIDED-faithful, unchanged) |
| N5 | ALL | UNDECIDED | UNDECIDED | f6, f10, f12, f18 (UNDECIDED-faithful, unchanged) |

The case has no keyed item named T4 (its key item is T4b). Why no answer moves:

- The FACTS fix changes `scenario_2`'s legend and makes it an open term. The premises' formulas are the same, so
  T1 to T7 are the same; `test_t_answers_hold_with_the_branch_2_determination` recomputes T3, T5, T6 and T7.
- The other fixes change acts or legends, and drop the f11 guard, which K22 satisfies anyway.

Union-rule ceiling (an ESTIMATE; nothing is claimed before the re-audit): 103 -> 109/126 if every fix holds and a
blind read clears each unit. Coverage bytes by status are unchanged; only `coverage.json`'s document hash moved
(build_document.py).

## Regulated predicates

64 of 64 (`test_regulated_predicates_stay_64_after_fix_3`). Two predicates are renamed and none is added:
`goal_miss_addressed` -> `roadmap_review_addressed` and `executive_approved` -> `executive_submitted`.

## Seeded bugs

Each bug was planted in the product file, the one test was run, and the file was restored with `git checkout`.
All are in usecases/anthropic-rsp, the only product code changed (Python: rsp_vocabulary.py; VE: rules.d1.ve).
No Lean or Rust changed.

| # | Seeded bug | File | Failing test (tests/test_rsp_fidelity_fix.py) |
|---|---|---|---|
| a | `scenario_2` back to a plain stipulated situation (`_base`, no OT, no decider): branch (2) sufficient with no determination | rsp_vocabulary.py | test_t4_both_branches_are_the_companys_determination: 1 failed |
| b | "roadmap_goal_missed" back as the guard of f11-goal-missed | rules.d1.ve | test_f11_states_both_parts_of_review_item_3_with_no_guard: 1 failed |
| c | "approved by the CEO with the RSO" restored in f12-approval (act and rule) | rsp_vocabulary.py, rules.d1.ve | test_f12_approval_states_the_submission_not_an_approval: 1 failed |
| d | the regular-clearance version dropped from f13-redact-p (act and rule) | rsp_vocabulary.py, rules.d1.ve | test_f13_redact_p_covers_both_versions_and_keeps_its_reasons_open: 1 failed |
| e | "prior-draft" dropped from f23-publish (act and rule) | rsp_vocabulary.py, rules.d1.ve | test_f23_names_the_prior_draft_baseline: 1 failed |
| f | f7-publish's header cut back before "and how we have made determinations" | rules.d1.ve | test_fix_3_headers_quote_the_full_source_sentence: 1 failed |
| g | the pointer legend "3.6.2 at {0}" put back on `shared_with_reviewers` | rsp_vocabulary.py | test_f16_legend_keeps_one_or_more_and_the_act_picks_no_quantifier: 1 failed |
| h | 4.1's designation and responsibility dropped from `rso_maintained`'s legend | rsp_vocabulary.py | test_f6_f10_f18_legends_carry_the_dropped_qualifiers: 1 failed |
| i | "we determine that" dropped from `scenario_2`'s legend | rsp_vocabulary.py | test_t4_both_branches_are_the_companys_determination: 1 failed |

Each test is also exercised in the opposite direction:

- Every test passes on the fixed text: `uv run pytest -q tests/test_rsp_fidelity_fix.py tests/test_safetyfw_accounting.py`
  gave 90 passed.
- test_t4_both_branches also checks in-test that a plain `_base` description is refused.

## Open list

- DRI questions sent: none. Question 1 (FACTS): no T answer moved. Question 2 (f12-approval): no answer moved, and
  no block or case reads the old approved-by predicate (run.py's PREDICATES never named `executive_approved`;
  f12-share, f12-final and f12-board-approval read `risk_report_approved` and `board_approved`). Question 3
  (f16): K14 and D5 equal the key (ALL), and the act picks no quantifier.
- Out of scope, with their rulings:
  - K18, T7, C1, C7 and C-doc: K findings with section-12 deviation entries (PLAN section 12 item 21). The rulings
    are dri-decisions-20261112-anthropic-rsp-fidelity-fix-2.md, item 1 (C1, C7, C-doc) and item 2 (T7), and
    -fix-2-k18.md (K18). Keys and scorer are untouched.
  - f16-ask-commentary: NOT by both adjudicators (item 28 Q03), so it is refuted and unchanged.

## Budget readings

There is no `anthropic-rsp-fidelity-fix-3-loop.log` in manage-agents. The only reading is the task file's: VM1 at
16:31Z 2026-11-12, 4.23M of 14M left, round budget 1.00M: START. Per the task, I did not run ucfix-budget.py.

## Trust, DELTA, size

- Trust: `tools/trust_map.py --check` gives "K +0, S +0, D +0, G +0, tied +0 ... PASS".
- trust_mutants: `tools/trust_mutants.py --plan` gives `{"definitions": 0, "mutants": 0, "to_run": 0}`. The
  light-lane check printed NOT ("457 changed lines outside generated files", which counts the saved accounting
  report). There is no trusted definition, so no sweep was run.
- DELTA: none. There is no product-code change in ve/, lean/ or rust/ and no user-visible checker delta.
- Test-removed: `tests/test_safetyfw_usecases.py::test_rsp_n1_prediction_removes_inherited_commitments[K22-goal_miss_addressed]`.
  Its parameter is renamed, and the same case runs as `[K22-roadmap_review_addressed]`. The trailer is on the
  REPORT commit, and `tools/gate_collection.py --check --prebuilt` names exactly this ID.
- SIZE: 59 product (rsp_vocabulary.py, rules.d1.ve, facts.d1.ve, run.py), 151 tests, 26 other hand-written lines
  (PLAN 19, accounting.d1.txt 7), plus this REPORT and answers.json. Generated files are excluded (`git diff --numstat
  $(git merge-base HEAD main)`).

## Selected tests

See "Selected-test run" below: the final run on committed code.

## Next item

After merge, the DRI decider launches two audits; the builder runs neither:

1. The production checklist pass re-reads only the changed units (addendum 6 item 41): f7-publish,
   f16-share-one-week, f23-publish, f11-goal-missed, FACTS, f13-redact-p, f12-approval, f6-maintain,
   f10-candid-default and f18-rso.
2. The full union audit runs at the Nov 23 checkpoint.

## Notes for the DRI

- f11's guard is dropped. `roadmap_goal_missed` is now read by no rule; only K22 stipulates it. Under the source,
  "any cases where we failed to meet our goals" needs no condition. K22a stays ALL because the duty holds in every
  situation.
- `scenario_2` uses OT1 rather than a new OT number. PLAN 3.2 lists OT1 to OT28 and sections 1-11 are not edited.
  OT1 is the company's T4 crossing determination ("if we determine"), which is what branch (2) needed.
- The recorded fixtures `tests/data/norm-blocks/rsp.jsonl`, `route-cases.jsonl` and `relay-gate-cases.jsonl`
  still hold the old predicate names. They are snapshots pinned to the commit they were read at, so they were left
  unchanged.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A. No relay or schema changed; use-case files only.
2. Every deliverable built: PASS. All 7 deliverables (10 units) are in the table above. Tests:
   test_fix_3_headers_quote_the_full_source_sentence and the eight fix-3 tests.
3. Tests can fail: PASS. Seeded bugs a-i above each fail a named test.
4. Python, Lean and Rust agree: N.A. No product code in any of them changed. `run.py` (110/126) and
   `stage0.py --source` were regenerated; stage0.json is unchanged.
5. R8 binding: N.A. No relay changed.
6. Gate evidence matches the final HEAD: PASS. The final selected run is on committed code; the chain runs the gate.
7. No unsigned item: PASS. No DELTA row and no reserved signature.
8. DELTA: N.A. No user-visible checker change.
9. Test selection: PASS. The changed files are use-case files and tests; `mac-pytest.sh --select` ran them (see
   below).
10. Lean statements: N.A. No Lean changed (`trust_mutants --plan`: 0 definitions).
11. Budgets fail closed: N.A. No limit or deadline changed.
12. CPU/memory: N.A. `run.py` took 292 s, the same run as before (a printed time, not pinned).
13. Test-removed trailer: PASS. `gate_collection.py --check --prebuilt` gives 0 refused after the trailer (see the
    selected-run section).
14. Both directions, cited evidence, spec re-read: PASS. Each test checks the restored text, and seeds a-i show the
    old text fails. Spec re-read: each header quote against rsp-3.4.txt: S:9 (t4), S:11 (f6, f7), S:12 (f10), S:13
    (f11, f12), S:14 (f13), S:15 (f16), S:16 (f18), S:17 (f23). All are anchored: "0 of 96 quotes unanchored".
15. No overclaim / no silent cut / every check can fail / limits: PASS. No deliverable was cut. "No answer moves"
    is answers.json `moved: []`. The new checks fail under seeds a-i. Limits: N.A.
