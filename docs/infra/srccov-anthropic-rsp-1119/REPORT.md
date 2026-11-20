# srccov-anthropic-rsp-1119: REPORT

**Summary.** Status: built, review fix F1 and F2 done (section 9), ready for the chain gate. Base: main e01c3d6680.
Changed: 21 of 23 rows KEPT (row 33 partly), 2 DROPPED; 8 of 8 units RECORDED; one use case's text only, trust +0.
Rows 4-7 (constants) and 33 (D3 dates) count under METHOD amendment 4; the counter shows neither kind (Note 1).
Fixed: results.json (M3, M10), README figures, 5 carries quoted inside citations; tests bind each (section 9).
Open: nothing. No DRI signature is needed and no DELTA row is reserved.

## 0. Verify first (pin of the map: e53db4e8fc; checked against main 09bea0972d, then again after the rebase onto 12cb72fa55)

Units are checked against the pinned source `rsp-3.4.txt` (SHA-256 c7de7fe2..., read through tests/pinned_source.py)
and against what main showed. Since the pin, main changed only one anthropic-rsp product file:
`git log e53db4e8fc..HEAD --no-merges -- usecases/anthropic-rsp` lists c790d35168 (rsp-repair-r1-catastrophic-1119:
stage0.py, accounting.d1.txt). The carrier keys come from `rsp_vocabulary.py` (it writes `environment.d1.json`), so
the change went into the builder's input. Every carrier predicate is used by a rule line: the counter's own
`used_predicates` was run over rules.d1.ve and facts.d1.ve, and all 17 hit at least one block (listed in section 4).

| row id | KEPT / DROPPED | units kept | reason (file:line) |
|---|---|---|---|
| srccov-anthropic-rsp-3-1119 | DROPPED | none | S0048, S0049 are already carried at main: D2's footnote-1 constant `existential_threats` quotes footnote 1 whole (usecases/anthropic-rsp/stage0.py:63), and fn1-catastrophic is CHECKED, routed to D2 (spans.json). Merged after the pin by c790d35168; tests/test_rsp_repair_r1_catastrophic_1119.py |
| srccov-anthropic-rsp-4-1119 | KEPT | S0059 | T1 description appended to `THRESHOLDS["non_novel_chem_bio_weapons"]` (rsp_vocabulary.py:31), the legend of constants.non_novel_chem_bio_weapons |
| srccov-anthropic-rsp-5-1119 | KEPT | S0073, S0074, S0088 (footnote 4 part) | T2 description and footnote 4 appended to `THRESHOLDS["novel_chem_bio_weapons"]` (rsp_vocabulary.py:31); S0074's footnote markers 4 to 7 left out (amendment 6) |
| srccov-anthropic-rsp-6-1119 | KEPT | S0081 (T3 part), S0088 (T3 continuation) | T3 description, which the PDF breaks across a page, rejoined in `THRESHOLDS["misaligned_high_stakes"]`. S0081's other sentence ("We will detail the state ...") is the t3-plan cell, not this row |
| srccov-anthropic-rsp-7-1119 | KEPT | S0096 | T4 description appended to `THRESHOLDS["automated_rd"]` (rsp_vocabulary.py:31) |
| srccov-anthropic-rsp-8-1119 | KEPT | S0120, S0121 | footnotes 8 and 9 quoted in `double_rate` (rsp_vocabulary.py:245) |
| srccov-anthropic-rsp-10-1119 | KEPT | S0151 (S0150 is its lead-in, unchanged) | the whole off-cycle bullet 1 quoted in `more_capable_than_analyzed` (rsp_vocabulary.py:173), a superset of the map's fragment |
| srccov-anthropic-rsp-11-1119 | KEPT | S0153 (S0150 is its lead-in, unchanged) | the whole off-cycle bullet 2 quoted in `exceeds_all_analyzed` (rsp_vocabulary.py:183) |
| srccov-anthropic-rsp-13-1119 | KEPT | S0161 to S0167 | quoted in `factual_documented` (rsp_vocabulary.py:465). S0165's record s33-evidence stays UNFORMALISED (`as_appropriate`, known gap): its words are shown, but "as appropriate" is still not decided |
| srccov-anthropic-rsp-14-1119 | KEPT | S0170 to S0175 | quoted in `risk_analysed` (rsp_vocabulary.py:479) |
| srccov-anthropic-rsp-15-1119 | KEPT | S0177 to S0180 | quoted in `past_reviewed` (rsp_vocabulary.py:489); item 3 is already `roadmap_review_addressed` |
| srccov-anthropic-rsp-16-1119 | KEPT | S0183 to S0187 | S0183 (footnote marker 11 left out) and items 1 to 4 quoted in `marginal_analysed` (rsp_vocabulary.py:502). S0183's condition is quoted in `marginal_justification` (rsp_vocabulary.py:232), which carries the map's "by AI systems such as ours" in the source's own sentence |
| srccov-anthropic-rsp-17-1119 | KEPT | S0195 | quoted in `executive_submitted` (rsp_vocabulary.py:524), next to step 3, the sentence it follows |
| srccov-anthropic-rsp-18-1119 | KEPT | S0202 to S0206 | quoted in `redaction_reason_listed` (rsp_vocabulary.py:149) |
| srccov-anthropic-rsp-19-1119 | KEPT | S0215, S0216 (S0213 is the lead-in, unchanged) | quoted in `significantly_redacted` (rsp_vocabulary.py:190), the OT4 legend. Under amendment 4, the open-term list carries nothing; this is the predicate's legend |
| srccov-anthropic-rsp-20-1119 | KEPT | S0234 (without its heading "Contents of external review"), S0235 to S0241, S0245 to S0247 | quoted in `commentary_asked` (rsp_vocabulary.py:574); footnote 12 (S0242 to S0244, recorded at main as examples) is left out |
| srccov-anthropic-rsp-21-1119 | KEPT | S0253 to S0258 | quoted in `rso_maintained` (rsp_vocabulary.py:606) after its existing pointer "(the listed duties are s4-rso-duties" |
| srccov-anthropic-rsp-22-1119 | KEPT | S0197 | footnote 11 (`MARGINAL_FN11`, rsp_vocabulary.py:59) quoted in `marginal_justification` and `marginal_major_role` |
| srccov-anthropic-rsp-23-1119 | KEPT | S0207 (its last clause) | the clause quoted in `redactions_justified` (rsp_vocabulary.py:544) extends the quote the legend already had |
| srccov-anthropic-rsp-24-1119 | KEPT | S0209 | quoted in `public_review_sought` (rsp_vocabulary.py:553) |
| srccov-anthropic-rsp-25-1119 | KEPT | S0272 | quoted in `compliance_review` (rsp_vocabulary.py:653) |
| srccov-anthropic-rsp-33-1119 | KEPT (S0360 DROPPED) | S0299, S0300, S0336, S0343, S0347, S0349, S0356, S0357 (the date of each) | Each changelog date in its D3 date constant's legend: stage0.py:144 `DATE_WORDS`. S0360's date is already carried at main: `v3_4_date` quotes "July 8, 2026 (RSP v3.4)" (stage0.py:144-145). The rest of each unit is recorded at main as history (the cl-v* explanation units) |
| srccov-anthropic-rsp-34-1119 | KEPT | S0065, S0211, S0280 | recorded as hopes (see RECORDING) |

No row needed a rule line, a feature, a theorem change, trust or a DELTA row. I add no rows of my own.

### RECORDING (the 8 OUT-OF-SCOPE-UNRECORDED units of reviews/source-coverage-1119/anthropic-rsp.md)

Each record is in spans.json, the document's record file, in the forms it already uses: kind `meta`, or kind
`unformalised` with reason `hope`, as s1-hope and s2-hope have. None of the 8 holds a modal from amendment 12's list,
a definition, a number, a date or a condition. So none is "absent, not recordable".

| unit | RECORDED / DROPPED | record (spans.json id, kind; builder line) |
|---|---|---|
| S0065 | RECORDED | t1-expect, unformalised / hope (spans.json:622; build_document.py:255); was attributed (expects) |
| S0141 | RECORDED | s31-heading, meta (spans.json:1470; build_document.py:356): the heading unit now covers "3.1. Scope and Timing Scope." At main, the sub-heading "Scope." sat in the D3-routed s31-coverage-date. Its only record was accounting.d1.txt's D2D3 entry `"Scope." exposition`, which METHOD R does not count. That entry is removed (accounting.d1.txt:87 keeps its one loss) |
| S0182 | RECORDED | s33-marginal-heading, meta (spans.json:1808; build_document.py:393), split off the rule unit s33-marginal |
| S0211 | RECORDED | s36-intent, unformalised / hope (spans.json:2042; build_document.py:419); was attributed (intends) |
| S0280 | RECORDED | appa-priority, unformalised / hope (spans.json:2655; build_document.py:488); was attributed (intends) |
| S0281 | RECORDED | appa-lead-heading, meta (spans.json:2665; build_document.py:490): table head and scenario name, split off appa-lead-scenario |
| S0286 | RECORDED | appa-strong-heading, meta (spans.json:2717; build_document.py:497), split off appa-strong-scenario |
| S0290 | RECORDED | appa-uplevel-heading, meta (spans.json:2768; build_document.py:503), split off appa-uplevel-scenario |

## 1. What changed (commits main..HEAD --no-merges)

- 936157e5e3: the legend carries, the D3 date words, 7 records, the condition test, and the regenerated
  environment.d1.json, spans.json, coverage.json, corpus-seal.json and lexicon-report.json.
- 6a7bc03976: fidmech/actors.json kept at main (see Notes).
- 5c1df0ec7f: units.json, gaps.json, stage0.json and tests/data/route-cases.jsonl regenerated by their writers; the
  README span table and docs/usecases/safetyfw/REPORT.md's RSP row updated to match.
- 63a6a8bedf: rso_maintained keeps its base pointer; derived files regenerated.
- 94e2fda9ab: corpus seal regenerated after the rebase.
- Review fix (section 9): results.json regenerated by run.py; the README's stale figures corrected; the tests that
  bind both; this REPORT, DELTA.md and mutants.json.
- Selected-run fix (section 9): five carried quotes moved out of their citation parentheses; the files that
  hash the legends regenerated; the test that carried runs survive the counter's citation cut.
- 73b665d54c: S0141's record; accounting.d1.txt's D2D3 line; accounting.json (it also follows the new legends, with
  fewer unaccounted words) and the measurement files regenerated; the expectation in
  tests/test_rsp_repair_r1_catastrophic_1119.py follows the D2D3 line.

Every carried text is the source's words. The only changes are the project's quote normalisation
(`safetyfw_accounting.norm`: plain quotes, ligatures; dashes kept as in the source), footnote markers and bullet
signs left out, and one space joining two runs. The PDF's stray spaces are kept: "above )", "Section 1 )",
`By " marginal risk analysis ,"`, "practices —noteworthy".

Derived files, regenerated only by their tools:
- `uv run python usecases/anthropic-rsp/rsp_vocabulary.py` writes environment.d1.json.
- `uv run python usecases/anthropic-rsp/build_document.py` writes spans.json, coverage.json, and rsp.d1.ve.md beside
  the pinned source (not committed).
- `measure.py` writes units.json and gaps.json; `stage0.py` writes stage0.json.
- `uv run python usecases/safetyfw_accounting.py anthropic-rsp --source <pinned rsp-3.4.txt> --check --report
  docs/usecases/safetyfw/anthropic-rsp/accounting.json`.
- `uv run python docs/en-e3-norm/en-2b/route_fixtures.py --write`.
- `uv run python -m conformance.english_lean_seal` and `uv run python -m conformance.english_lean_lexicon`.
- `uv run python usecases/anthropic-rsp/run.py` writes results.json (its M3 and M10 copy coverage.json and
  spans.json). The README's figures are hand-written; test_readme_figures_are_the_committed_measurements binds each.

Final checks on HEAD:
- `build_document.py --check`, `measure.py --check`, `stage0.py --check` and `english_lean_seal --check` all exit 0
  (0 differences).
- `tools/regen_generated.py --check` exits 0 (41 entries).
- The accounting report rewritten to /tmp is byte-identical to the committed one (`cmp`).
- `fidmech boundaries --check` exits 0.
- `run.py --check` exits 0 (after the review fix; it printed "results.json is out of date" before it).

## 2. Condition test (tests/test_srccov_anthropic_rsp_1119.py, selected by tools/select_tests.py for this diff)

- `test_every_kept_row_carries_its_source_text_in_its_legend`: 22 legend carries (rows 4 to 25) and 23 runs. Each run
  is byte ranges of the pinned source, normalised and joined. It must occur in the committed environment.d1.json
  legend. Without the stored source, the test checks that the legend holds a run with the recorded SHA-256 and length.
  Both paths were run: with the source, and with `_source` forced to None (`fallback misses: []`, `no-source path ok`).
- `test_every_changelog_date_is_in_its_d3_legend`: the 8 dates, read from the source, are in the D3 date constants'
  legends (`stage0.date_environment()`).
- `test_every_recorded_unit_lies_in_a_record_that_says_it_is_not_a_rule`: each of the 8 units lies inside its
  spans.json record. The record must have the expected kind, reason and status, and no rule, open term or waits.
- On main's carriers (`git checkout main -- usecases/anthropic-rsp`), all 3 fail: row4, S0299 and S0065 are the first
  failures (evidence/seeded-bugs.log, last block). On HEAD, all 3 pass.

## 3. Seeded bugs (docs/infra/srccov-anthropic-rsp-1119/mutants.json; log evidence/seeded-bugs.log)

Product code changed only in Python (usecases/anthropic-rsp/*.py); no Lean or Rust. There is one seeded bug per
carry kind and record kind. Each was planted, run with `uv run pytest -q tests/test_srccov_anthropic_rsp_1119.py`
(1 failed, 2 passed), and restored. The tree was clean afterwards.

| kind | file | seeded bug | failing test |
|---|---|---|---|
| predicate legend carry | usecases/anthropic-rsp/rsp_vocabulary.py | the carried S0272 sentence removed from compliance_review | test_every_kept_row_carries_its_source_text_in_its_legend |
| constant legend carry | usecases/anthropic-rsp/rsp_vocabulary.py | T4 description cut short | test_every_kept_row_carries_its_source_text_in_its_legend |
| D3 date carry | usecases/anthropic-rsp/stage0.py | the v2_0 DATE_WORDS entry removed | test_every_changelog_date_is_in_its_d3_legend |
| hope record | usecases/anthropic-rsp/build_document.py | s36-intent back to believes("intends") | test_every_recorded_unit_lies_in_a_record_that_says_it_is_not_a_rule |
| heading record | usecases/anthropic-rsp/build_document.py | appa-uplevel-heading unit removed | test_every_recorded_unit_lies_in_a_record_that_says_it_is_not_a_rule |
| sub-heading record | usecases/anthropic-rsp/build_document.py | s31-coverage-date's anchor back to "Scope. A Risk Report ..." | test_every_recorded_unit_lies_in_a_record_that_says_it_is_not_a_rule |

## 4. VE commit and the answers the change touches (so later reads re-pin)

The branch is rebased onto main **e01c3d6680** (first onto 12cb72fa55, then again after main moved during the final selected run). No keyed answer changes value: results.json is unchanged on the
branch, and tests/test_safetyfw_usecases.py, which recomputes every key item, had no other failure in the selected
run. What a later read shows does change, so these re-pin:
- **Rule blocks whose shown legends change (17):** f9-public, f9-internal, f11-factual, f11-analyses, f11-review,
  f11-marginal, f12-approval, f12-board-approval, f13-redact-p, f13-justify-default, f14-full-review,
  f14-public-review-default, f16-ask-commentary, f18-rso, f22-third-party-review, and facts s2-suff-third and
  s2-only-if-third. These were found with tools/defs_carried_counter.py `used_predicates` over the committed blocks.
- **Keyed cases whose findings set the changed open terms:**
  - OT2: G4, K2;
  - OT3b: K4;
  - OT4: G6, K8, K9, K10;
  - OT18: K5;
  - OT19: K6;
  - OT16: T3, T4, T7.
- **Cases that name thresholds (constant legends):** A-T1, A-T2, A-T3, A-T4, G1.
- **D3:** the changelog date-chain answer D1 (the v1.0 to v3.3 date legends).
- **Hashes and units:**
  - environment.d1.json, with its corpus-seal SHA-256 and lexicon_id;
  - the D1 document_sha256 in coverage.json;
  - spans.json: 303 to 307 units, with new ids s33-marginal-heading, appa-lead-heading, appa-strong-heading and
    appa-uplevel-heading;
  - spans moved for s31-heading, s31-coverage-date, s33-marginal and appa-{lead,strong,uplevel}-scenario;
  - kinds changed for t1-expect, s36-intent and appa-priority.

## 5. Tests run

- **New test:** 3 passed on HEAD (`uv run pytest -q tests/test_srccov_anthropic_rsp_1119.py`) and 3 failed on main's
  carriers (section 2).
- **First selected run**, `mac-pytest.sh --select` at 638928a26c: the fast stage failed on
  test_fidmech_wording::test_wording_mutants_are_scored_never_equivalent_and_stillborn_ones_are_listed, because of
  actors.json. Fixed by keeping actors.json at main; that test file then passed (13 passed).
- **Second selected run** at d3056bc1f7 (84 units, ve-cloud-2): 3 failed, 102 passed. The failures were
  test_safetyfw_usecases::test_rsp_reported_coverage_matches_saved_measurement,
  ::test_rsp_every_byte_not_checked_waits_for_a_named_family and ::test_rsp_stage0_rerun_equals_saved, all stale
  saved measurement; plus test_english_statement_blocks::test_the_route_fixtures_are_recorded. All were fixed by
  regenerating with the writers, and the failed ids passed again.
- **After later edits**, the failed ids plus the RSP test files were run: 143 passed and 1 failed, then 20 passed
  after the S0141 change. The run covered test_rsp_b_repair_1115, test_rsp_fidelity_fix,
  test_rsp_repair_r1_catastrophic_1119, test_safetyfw_accounting and test_english_lean_{lexicon,seal}.
- **Final selected run on the final code HEAD:** see section 8.
- **`Test-removed` trailer check:** `(cd lean && lake build) && uv run python tools/gate_collection.py --check --prebuilt`
  printed "3 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers". No test was removed.
- **Not run:**
  - the full gate (the chain runs it on the final HEAD);
  - a trust_mutants sweep. The light lane says NOT (661 changed lines), but no Lean file changed and trust is +0, so
    there is no trusted-core mutant to sweep.

SIZE: 205 product, 194 tests, 20 other hand-written lines (README 16, safetyfw REPORT.md 2, accounting.d1.txt 2),
plus this item's docs.

## 6. Notes for the DRI

1. Rows 4 to 7 carry onto threshold constants and row 33 onto D3's changelog date constants, as METHOD amendment 4
   allows. The constant legends appear in the D1 document's environment, the date legends in D3's. The defs-carried counter, however, shows no constant legends (tools/defs_carried_counter.py
   `seq_unit_legends`: "Constants and unused predicates are not shown"). A counted read will not credit these five
   carries.
2. fidmech/actors.json stays at main. Its generated list (`python -m tools.fidmech actors --doc anthropic-rsp --check`)
   now reports 9 more phrases from the new legend text:
   - 5 parties: third-party organizations, relevant competitors, safety researcher, third parties, developers;
   - 4 non-parties: protect public, raise public, The CEO and RSO, The RSO.

   Rewriting it changes the actor:1 swap that test_fidmech_wording pins: rows-cond would take "third-party
   organizations". This is left to the fidmech owner; nothing gates that check.
3. T2's footnotes 5, 6 and 7 (markers inside S0074) are in no candidate row; the carry leaves the markers out.
4. Row 18's map note still holds for the rule, which this item does not touch: f13-redact-p's condition closes a
   class the source leaves open ("include but are not limited to"). The legend now quotes that lead-in, and the
   `redaction` legend already says the reasons do not close the class.
5. The builder rewrote `rsp.d1.ve.md` beside the pinned source in manage-agents/pilots/anthropic-rsp/source/, which
   is its default output. It is not committed.
6. The task names D3 as "the D3 text built by build_document.py (rsp.d1.ve.md)". That file is D1. D3's legends live
   in stage0.date_environment(), which has no derived file, and stage0.json stores booleans only.
7. Two tests outside this item's new file were touched, both as the data they read requires:
   - tests/test_rsp_repair_r1_catastrophic_1119.py: its expected D2D3 entry list loses the moved "Scope." entry;
   - tests/data/route-cases.jsonl: regenerated.

## 7. Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer, relay or schema touched.
2. PASS: every deliverable (0 verify table, 1 carries, 2 regeneration, 3 condition test, RECORDING, REPORT) maps to a
   commit in section 1 and a test in section 2. There is no Python copy of a Lean decision and no new report test.
3. PASS: six seeded bugs fail the condition test (mutants.json, evidence/seeded-bugs.log), and the test fails on
   main's carriers.
4. N.A.: no Python, Lean or Rust decision path changed. results.json changes only in M3 and M10 (DELTA.md); the key
   recompute is in the selected run.
5. N.A.: no relayed field.
6. PASS: rebased onto main e01c3d6680. The derived files were regenerated after each rebase (the two "corpus seal regenerated" commits), and
   the commit list comes from `git log main..HEAD --no-merges`. The chain runs the gate on the final HEAD.
7. PASS: DELTA.md has no rows (no VE delta, per the fsf-repair-f1 precedent) and no trust growth.
8. PASS: DELTA.md lists every changed record with counts. evidence/legend_keep.py prints "21 changed legends; 0 lose
   base words or change another field".
9. PASS: tools/select_tests.py selects tests/test_srccov_anthropic_rsp_1119.py for this diff, and the seeded bugs make
   it fail.
10. N.A.: no Lean statement or proof.
11. N.A.: no budget, limit or deadline.
12. N.A.: no CPU path; only legend text and span records.
13. PASS: gate_collection --check --prebuilt reports 0 refused, 0 stale and 0 malformed trailers. No test was removed.
14. PASS:
    - opposite direction: the test refuses main's carriers and accepts HEAD's; the hash fallback path was run with the
      source absent;
    - claims cite their commands (sections 1, 2 and 5);
    - spec re-read: each carry against METHOD.md amendment 4 (a legend of a used symbol, not an open-term list), each
      record against METHOD R, amendment 12 and amendment 13, and the RECORDING paragraph of the task.
15. PASS:
    - overclaim: the universal words in this report ("every", "no", "all") cite legend_keep.py, the condition test,
      regen --check or the selected run;
    - no cut: all deliverables are built;
    - every new check can fail: section 3;
    - limits: N.A.

## 8. Final selected run

`zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on 57efa7a03c
(the code is final; only this section was committed after it) exited 0. The cheap units passed first on
multi-agent-lab, then all 95 selected units passed in 5 GitHub Actions shards (run
srccov-anthropic-rsp-1119-57efa7a0-t170844: 24, 23, 21, 14 and 13 units). tests/test_safety_framework.py was
deferred to the chain gate (selected only for weak reasons, over 120 s). The summary lines are in
evidence/final-selected-run.txt.

After this run, main moved to e01c3d6680. The new commits overlap this branch only in the shared generated files
lexicon-report.json and tests/data/route-cases.jsonl. The branch was rebased; each route-cases conflict was
resolved by taking main's file and running route_fixtures.py --write. The files regen_generated lists were regenerated:
`regen_generated --check` exits 0, and only corpus-seal.json changed. (results.json was not: section 9.) The tests of those files then passed:
76 passed (`uv run pytest -q tests/test_srccov_anthropic_rsp_1119.py
tests/test_english_statement_blocks.py::test_the_route_fixtures_are_recorded tests/test_english_lean_lexicon.py
tests/test_english_lean_seal.py tests/test_rsp_repair_r1_catastrophic_1119.py tests/test_rsp_b_repair_1115.py`).
The commit hashes in sections 1 and 5 are from before this rebase: the commits keep their subjects, and
`git log main..HEAD --no-merges` lists them on the final HEAD.

## 9. Review fix (srccov-anthropic-rsp-1119-review.final.md: F1, F2)

Both findings were stale derived records. The class is "a record copies a measured number and is not regenerated
or checked when the measurement moves". Each copy is now checked against the files it comes from, so the class
cannot recur silently.

| Finding | Fix | Regression test | Probe before / after |
|---|---|---|---|
| F1 results.json not regenerated | `run.py` rerun: only M3 (`bytes_by_status`, `bytes_by_kind`) and M10 (units 303 -> 307) change | `tests/test_srccov_anthropic_rsp_1119.py::test_saved_metrics_equal_their_recomputation_from_the_committed_files[anthropic-rsp]`; the `[openai-preparedness]` case covers the sibling with the same copy | `run.py --check`: "results.json is out of date" (exit 1) / exit 0 |
| F2 README figures stale | D3 449 -> 442 B (2 places); no-claim 130 / 31,104 -> 134 / 31,253; JT 11,372 -> 11,230 and alone 33, 6,892 -> 34, 6,896; readings 17 / 3,989 -> 16 / 3,884 (the last two were not in the review: the sweep found them) | `tests/test_srccov_anthropic_rsp_1119.py::test_readme_figures_are_the_committed_measurements` | the review's probe: AssertionError / exit 0 |

What the README test binds. Every row of the three measured tables (status, gaps, answers) is read from the README
and must equal its family's cells in spans.json/gaps.json or results.json M1; every family must have its row; a row
for a family the files lack (AP) must show zeros. 17 measured sentences are each rebuilt from the files: the
total, units, D1/D2/D3 bytes (and D1 + D2 + D3 = the master CHECKED), the CHECKED breakdown, the 3.6.1 clause
bytes, P5/P6, the undecided and key-finding counts and the section 9 comparisons. Any "N bytes", "N-byte", "N B to"
or "N units" in the README outside a checked sentence fails the test.

Before the fix both new tests fail on the files of 6c3711d635 (M3 and M10 out of date; the D3 sentence). The seeded
bugs (mutants.json, the last eight entries) each fail one of them: a stale table cell, a nonzero AP row, a missing
WG row, a wrong Total, an unchecked prose figure, and a PF M10 change. The fix changed no product code (Python,
Lean or Rust), so these are planted in the records the tests bind.

The selected run on 8e916763e2 failed one test, which main's rebase brought in after this item's own run:
`tests/test_fsf_repair_f6_sl2plus_1119.py::test_no_legend_gains_a_quote_inside_a_citation_parenthesis`. Five carries
(marginal_analysed, marginal_justification, marginal_major_role, redaction_reason_listed, significantly_redacted) had
written their quote inside the base's citation, "(3.3: \"...\")", which the counter cuts whole as a citation, so the
carried words were never counted. Each quote now follows the citation ("(3.6): \"...\"", or ", which reads:" and
"lists:" where the base had none); the quoted words and the base words are unchanged (legend_keep.py: "21 changed
legends; 0 lose base words or change another field"). `_open` no longer doubles the full stop after a quoted sentence.
environment.d1.json, coverage.json (the D1 document hash), the corpus seal, the lexicon report and route-cases.jsonl
were regenerated by their writers; build_document, measure, stage0, english_lean_seal and regen_generated `--check`
exit 0, run.py `--check` exits 0, and the accounting report is byte-identical (`cmp`). The class test
`tests/test_srccov_anthropic_rsp_1119.py::test_no_carried_run_sits_inside_a_citation_parenthesis` cuts each carried
predicate run and its legend the counter's way and requires the run to survive; it fails on the pre-fix files and on
the three seeded bugs at the end of mutants.json (rsp_vocabulary.py: Python, the only product language changed).

Notes (not filed): the counter reads the vocabulary file's string literals, so footnote 11, which two legends join by
the name MARGINAL_FN11, is not in its view; and carries appended to a provenance string ("4.7 at {0}: \"...\"", e.g.
compliance_review) count as documentation under the counter's ruling, the shape their base already had on main.

Not done: C1 (fidmech actor list) stays a note for the fidmech owner (section 6, note 2). C3 and C5 were not
changed. C6: the two edits outside the path list stay, since the tests need them. Fixed among the notes: C2 (Note 1
and the summary name row 33), C4 (DELTA base e01c3d6680) and C7 (summary of five lines).

Tests of the review fix. The selected run on 0aa6a2c583 (the final code; only this paragraph and the evidence lines
came after it) exited 0: 96 units in 4 GitHub Actions shards (run srccov-anthropic-rsp-1119-0aa6a2c5-t182933: 26,
25, 23 and 22 units); tests/test_safety_framework.py was deferred to the chain gate (weak reasons, over 120 s).
Summary lines: evidence/final-selected-run.txt. The run on 8e916763e2 before the legend fix had the one failure
described above. `lake build` (1478 jobs) and `python3 lean/audit.py` (898 files) pass; no Lean file changed. The
probes: `run.py --check` exits 0 and the F2 probe passes on this code.
