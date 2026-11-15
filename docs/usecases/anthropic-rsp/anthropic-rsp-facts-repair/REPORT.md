# anthropic-rsp-facts-repair: the three FACTS accounting entries the counter scored (ruling A3)

**Status:** done, no DRI signature needed. HEAD: the last commit on feature/anthropic-rsp-facts-repair (code at ac101e7d9: legends 079f2e099, regenerated records ac101e7d9).
**What changed:** three predicate legends in rsp_vocabulary.py now quote the source wording their formulas already carry. One accounting tag changed, and the generated files followed.
**Target (exposure.py):** 7 -> 4 exposures on FACTS/CASES. The three targeted rows are gone, and none was re-filed with a `loss` tag. The 4 true records remain, and no row is new on any of the manifest's 79 units.
**Answers:** none moved (`run.py --check` exit 0, "110 / 126", twice). **Open:** none on VE. The answers come back only through row facts-cases-omission-reads.

Ruling: inbox/dri/20261114T224834Z-orchestrator-3280609.md item A3; decision reviews/dri-decisions-20261114-replan-ruling.md;
diagnosis reviews/facts-cases-diag-20261114.md section 1 (RSP FACTS). Statement gate: none (a use-case record repair).

## Deliverables

| # | task line | delivered by | test |
|---|---|---|---|
| 1 | the 3.6 phrase "described in Section 1" | legend `highly_capable` (d0bac2b4d, 079f2e099) | test_facts_repair_each_retagged_entry_is_whole_in_its_blocks_carrier; test_facts_repair_legend_quote_is_verbatim_in_the_pinned_source[highly_capable] |
| 2 | the row T4 phrase "We would consider scenario (2) to have occurred where" | legend `scenario_2` (d0bac2b4d, 079f2e099) | the same carrier test; …[scenario_2] |
| 3 | the row T4 phrase "in the absence of" | legend `double_rate` (d0bac2b4d) | the same carrier test; …[double_rate] |
| 4 | regenerate with the case's own scripts; add no PLAN 12 sentence | environment.d1.json, coverage.json, docs/usecases/safetyfw/anthropic-rsp/accounting.json | commands under "Regenerated" |

Choices made, one per task item:
1. Block `highly-capable-t4` uses two predicates, `crossed` and `highly_capable`. `automated_rd` is a constant, and the counter's carrier holds predicate legends only (`used_predicates`). So the 3.6 wording goes into the `highly_capable` legend, which already paraphrased 3.6. That legend now reads: the model of {0} is highly capable: it crosses "the threshold for automated AI R&D described in Section 1" (3.6). The formula's threshold is that Section 1 row 4 threshold. The tag `rule threshold-t4` would not hold: that block's carrier is "is listed" plus the `listed` legend, and neither has "described".
2. `scenario_2` is OT1's open term decided by the company ("if we determine"). It is the company's own finding that scenario (2) occurred, and row T4 says when the company makes that finding: "We would consider scenario (2) to have occurred where" its conditions hold. The legend now quotes that phrase as part of its meaning, outside the citation parenthesis.
3. Row T4 uses "in the absence of" inside condition (a): "the fastest rate of extended progress we've observed in the absence of significant AI contributions to AI R&D". The formula carries condition (a) through `double_rate`, whose legend paraphrased it as "without significant AI contributions". The legend now quotes the source: "in the absence of significant AI contributions to AI R&D". The formula has no negated condition here: the phrase belongs to the open term's meaning. So the honest tag is the carrying one, not `loss`.
4. No PLAN, README or other REPORT sentence was added or edited. No formula, block header, predicate name or argument changed, and no predicate was added (the regulated count is still 64: test_regulated_predicates_stay_64_after_fix_3).

The carrying quotes sit outside the legends' citation parentheses (commit 079f2e099). The installed counter's legend view for carrier reads (`_omit_legend_segments`) treats a parenthesis holding a digit or "section" as a citation. A quote placed there would count as provenance, not meaning.

## Accounting entries, main -> HEAD (usecases/anthropic-rsp/accounting.d1.txt)

| line | block | words | tag on main | tag on HEAD |
|---|---|---|---|---|
| 81 | highly-capable-t4 | "described in Section 1" | exposition | restates |
| 84 | s2-suff-third | "We would consider scenario (2) to have occurred where" | restates | restates (text unchanged) |
| 84 | s2-suff-third | "in the absence of" | restates | restates (text unchanged) |

Line 84 is byte-identical. Its tags were unresolved on main, and the legends now resolve them (`git diff main -- usecases/anthropic-rsp/accounting.d1.txt`: one line).

## Exposure (exposure.py, before and after)

Command: `python3 -I ~/code/manage-agents/reviews/facts-cases-diag/exposure.py anthropic-rsp <sha>`. The argument is a sha because the literal `HEAD` resolves in the main checkout. Counter sha256 f4345f44 both times; the task file names 1c7cc4f7, and the installed counter has moved since. The verbatim outputs are saved beside this file: `exposure-before.txt` (f5c1d64b65, this branch's merge base, main) and `exposure-after.txt` (079f2e0995).

| unit | record unit | kind | main f5c1d64b65 | HEAD 079f2e0995 |
|---|---|---|---|---|
| FACTS | highly-capable-t4 | loss | yes | **no** |
| FACTS | s2-suff-third | mistag, first entry | yes | **no** |
| FACTS | s2-suff-third | mistag, second entry | yes | **no** |
| FACTS | s2-suff-third | plan12 | yes | yes |
| FACTS | t4-suff | plan12 | yes | yes |
| FACTS | t4-only-if | plan12 | yes | yes |
| FACTS | s2-only-if-third | report | yes | yes |
| D2D3 | D2D3 | no-record | yes | yes |
| | | **total on FACTS/CASES** | **7** | **4** |

The four remaining FACTS rows are the true records the task names (PLAN.md:628, PLAN.md:655 twice, fix-2 REPORT.md:27). They are untouched and stay for the omission read. Nothing was re-filed with a `loss` tag, so this item adds no honest-loss entry for that read.

Every unit: a read-only script (`/tmp/facts-repair/expall/expall.py`, not committed) loads the installed counter and runs `omit_exposure` on the RSP manifest (reviews/audit-c2-rspbase/rspbase/union/manifest.json) at main and at HEAD. Output at 079f2e099: "units 79; states run/run; exposures 124 -> 121". The three rows that left are the three targeted rows above, and no row is new. The same script was run again on the commit holding this REPORT (section "Re-run on the REPORT commit").

## Re-run on the REPORT commit

At 7069c87b3, the commit that adds this REPORT, the every-unit script printed "units 79; states run/run; exposures 124 -> 121". The same three targeted rows left and no row was new, so this REPORT is no new record. exposure.py at 7069c87b3 ends "4 exposures on FACTS/CASES".

## Answers

None moved. `uv run python usecases/anthropic-rsp/run.py --check` exit 0, "110 / 126", at d0bac2b4d's tree and again at 079f2e099's tree. `git diff --stat main -- usecases/anthropic-rsp/results.json` is empty. The legends change only descriptions (`environment.d1.json`: three description strings) and the built document's hash in coverage.json.

## Regenerated (each by its own script, never by hand)

- `uv run python usecases/anthropic-rsp/rsp_vocabulary.py`: environment.d1.json (three descriptions).
- `uv run python usecases/safetyfw_accounting.py anthropic-rsp --source <pinned rsp-3.4.txt> --report docs/usecases/safetyfw/anthropic-rsp/accounting.json`. Output: "85 blocks, 160 unaccounted words in 34 blocks, 3 blocks with a loss {'1': 2, 'limit 9': 1}, 0 of 141 quotes unanchored" (main: 164 words in 36 blocks). The words "describ", "absence" and "occurr" are now accounted by the legends. One rules block that uses `highly_capable` also loses its "describ" (accounting.json, the first hunk). The entries by reason go from exposition 11 / restates 45 to 10 / 46. `--check` exit 0.
- `uv run python usecases/anthropic-rsp/build_document.py`: coverage.json, whose only change is `document_sha256` (the built document holds the legends). spans.json is unchanged.
- Unchanged, checked: `stage0.py --source <pinned> --check` exit 0; `python -m tools.fidmech boundaries --doc anthropic-rsp --source <pinned> --check` exit 0; `measure.py --check` exit 0.
- `uv run python docs/en-e3-norm/en-2b/route_fixtures.py --write`: tests/data/route-cases.jsonl, whose 7 RSP english.statement cases carry the three new legends and the new environment id (commit ac101e7d9; `git diff --word-diff`).
- `uv run python -m conformance.english_lean_lexicon`: conformance/english-lean/lexicon-report.json, where the RSP `lexicon_id` changed. Output: `{"valid": 43, "invalid": 0, "failures_by_condition": {}}`. Its `--lean-fixtures` writer leaves lean/VE/EnglishGrammar/LexiconFixtures.lean unchanged (`git status` clean after it).
- These two were found by the selected run at 079f2e099, which failed only on their two tests (section "Selected run"). `tools/regen_generated.py` lists route_fixtures.py as a writer it does not run (NOT_REGENERATED). Neither file is one of its generated files, so `regen_generated.py --write` was not run.
- Not changed: tests/data/relay-gate-cases.jsonl (a sampled recording of genuine requests that tools/relay_mutation_gate.py replays against the current build) and docs/kernel/kb-10e/cases/rsp-case-1.json (another batch's saved evidence). Each holds an older copy of the RSP legends. `grep -rl` for the old RSP environment and lexicon ids finds no other file.

## Seeded bugs (each planted, the named test failed, then `git checkout -- usecases/anthropic-rsp` restored it)

| # | file (language) | bug | failing test |
|---|---|---|---|
| a | usecases/anthropic-rsp/rsp_vocabulary.py (Python) | the `scenario_2` legend's new phrase deleted (planted at d0bac2b4d and again at 079f2e099) | test_facts_repair_each_retagged_entry_is_whole_in_its_blocks_carrier (`('s2-suff-third', 'We would consider scenario (2) to have occurred where')`) and test_facts_repair_legend_quote_is_verbatim_in_the_pinned_source[scenario_2] |
| b | usecases/anthropic-rsp/accounting.d1.txt (data) | the tag `exposition` put back on line 81 | test_facts_repair_each_retagged_entry_is_whole_in_its_blocks_carrier (1 failed) |
| c | usecases/anthropic-rsp/rsp_vocabulary.py (Python) | "significant" changed to "substantial" in the `double_rate` quote | test_facts_repair_legend_quote_is_verbatim_in_the_pinned_source[double_rate] (1 failed, 2 passed) |

The carrier test also checks the opposite direction itself: with each predicate's legend from before this item, its entry is not carried. Only Python product code (the vocabulary's legends) and use-case data changed. No Lean or Rust changed, so there is no Lean or Rust seeded bug.

## Tests

New in tests/test_rsp_fidelity_fix.py (section "anthropic-rsp-facts-repair"):
- (a) `test_facts_repair_each_retagged_entry_is_whole_in_its_blocks_carrier`: the counter's tag rule, written locally from its definition. The rule is every whole token of the omitted words but the articles, in one segment of the block's carrier. The carrier is the body statements (comments and quoted literals stripped) and the vocabulary entry of each predicate the block uses (comments stripped); the header is not in it. The test runs on every FACTS accounting entry, with the pre-item legends as the opposite direction, and pins each block's predicate set.
- (b) `test_facts_repair_legend_quote_is_verbatim_in_the_pinned_source` (3 cases): each legend quote has its start pin, its end pin and the SHA-256 of the whole quote, measured on the pinned rsp-3.4.txt (NFKC, apostrophe written ').

Runs:
- `uv run pytest -q tests/test_rsp_fidelity_fix.py -k "facts_repair or t4_both_branches"`: 5 passed.
- Final selected run, on committed 079f2e099 with a clean tree: `MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base f5c1d64b6 --run`. The 42 selected units include test_rsp_fidelity_fix.py, test_safetyfw_usecases.py (test_section_6_is_the_frozen_key, test_transcription_is_pinned, test_regulated_predicates_stay_within_lean_limit) and test_safetyfw_accounting.py. These passed. Two generated-record tests failed and were fixed: see "Selected run" below.
- `uv run python tools/gate_collection.py --check --prebuilt`: "4 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers".
- Tests on main-known-red.txt (two test_lean_service.py sub-tick tests, one test_readings_defaults_rd8_report.py test): none is in this item's selection.

## Size, trust, DELTA

SIZE: 21 product, 128 tests, 0 other hand-written lines (`git diff --numstat f5c1d64b6`: rsp_vocabulary.py +10/-9, accounting.d1.txt +1/-1, tests +128). This REPORT and the two saved outputs are not counted. Generated: environment.d1.json +3/-3, coverage.json +1/-1, accounting.json +7/-13, tests/data/route-cases.jsonl +7/-7, lexicon-report.json +1/-1. The planner's estimate was ~20-40 lines plus tests.
Trust: `uv run python tools/trust_map.py --check` reports "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0" (PASS). No R6 or R16 record is needed.
DELTA: none (use-case files only; no ve/, lean/, rust/, run.py, build_document.py, stage0.py, key or PLAN change), so there is no DELTA.md.
Light lane: `light-lane.py check` printed "NOT 169 changed lines outside generated files > 150". There is no trust_mutants sweep, because no Lean changed (build checklist 13a covers trusted Lean only) and the task file asks for none.
Overlap: no in-flight branch (`lean-first/*`, `feature/*`, `infra/*`, `foundation/*`) edits a file of this item. run.py was not touched.
Pilot bytes: none expected to move (no span, rule or case changed).

## Notes for the DRI

- Neither expected stop question arose. Each phrase is carried by a legend of a predicate the block already uses, with no formula change and no new predicate, and no answer moved. No msg.sh question was sent.
- The installed counter is f4345f44, not the 1c7cc4f7 the task names. Both exposure.py runs used f4345f44.

## Selected run

- Run on committed 079f2e099 with a clean tree: `MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base f5c1d64b6 --run`, on GitHub Actions (run anthropic-rsp-facts-repair-079f2e09-t709209), exit 1. Shard 1: 21 units, 20 passed. Shard 2: 21 units, 20 passed. The two failures were records generated from the RSP environment, which the legends changed:
  - tests/test_english_statement_blocks.py::test_the_route_fixtures_are_recorded (tests/data/route-cases.jsonl);
  - tests/test_english_lean_lexicon.py::test_every_corpus_environment_has_a_valid_selected_lexicon (lexicon-report.json).
- Fix: both records regenerated by their writers (commit ac101e7d9, section "Regenerated").
- Rerun of only those ids, plus test_each_route_fixture_through_the_service (which reads the regenerated fixtures): `zsh mac-pytest.sh -- <3 ids>` exit 0, "3 passed" (it ran on the VM).
- After ac101e7d9, only this REPORT and the two saved outputs were added. The gate the chain runs is therefore the first full run of the final tree.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no route, schema or relay changed.
2. Deliverables built, no rule broken: PASS. The table under "Deliverables" lists them. In the diff: no Python copy of a Lean decision, no report test (the new tests check the vocabulary and the accounting line, not saved batch numbers), and no file another in-flight branch edits.
3. Tests can fail: PASS, seeded bugs a-c, each with its failing test; the carrier test also runs the pre-item legends.
4. Py/Lean/Rust agree: N.A., no product code in ve/, lean/ or rust/ changed. `run.py --check` (Lean service) gives the same results.json.
5. R8 binding: N.A., no relayed field is read.
6. Gate evidence matches final HEAD: PASS. The selected run was on committed 079f2e099. Its two failures were fixed in ac101e7d9 and rerun by id (exit 0). After that only docs under docs/usecases/anthropic-rsp/anthropic-rsp-facts-repair/ were added, and the chain runs the gate on the final HEAD.
7. No unsigned item: PASS, no DELTA row and trust +0 (trust_map.py --check).
8. Every user-visible change in DELTA: N.A. No verdict, diagnostic or answer changed (`run.py --check` exit 0). Legend text is documentation of the use case.
9. Test selection: PASS. `tools/select_tests.py --base f5c1d64b6` selects 42 units, not every unit, including test_rsp_fidelity_fix.py, which catches seeded bugs a-c.
10. Lean statements: N.A., no Lean changed.
11. Budgets fail closed: N.A., no evaluator or limit.
12. CPU/memory: N.A., legend text only (run.py timing is not pinned).
13. Test-removed trailers: PASS, gate_collection.py --check --prebuilt: 0 refused, 0 stale, 0 malformed (no test removed).
14. Both directions, cited evidence, spec re-read: PASS. The carrier test runs both directions. Each claim here names its command. Spec re-read: the three legend quotes against the pinned rsp-3.4.txt (3.6 bullet "highly capable"; row T4 scenario (2) sentence and condition (a)), and the tag rule against uc-audit.py `omit_exposure`/`carrier()` (lines 2181-2228).
15. Four classes: no overclaim, PASS ("none moved": run.py --check; "no row is new": the every-unit script). No silent cut, PASS (items 1-4 all delivered). Every new check can fail, PASS (seeded bugs a-c). Limits charged before work: N.A., no evaluator.
