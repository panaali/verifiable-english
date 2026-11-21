# srccov-rl-news-article-1121: REPORT

- **Status:** verify done. All 5 in-scope units are DROPPED, so 0 are carried. No carrier, legend or derived file changed. No DRI signature is needed and no DELTA row exists.
- **HEAD / merge commit:** branch `infra/srccov-rl-news-article-1121` on main `cebf4fd24f`. This merges at the train's merge commit of its last commit (the chain's final HEAD). No answer, question, carrier or seal changes, so a later FSF read on this document has nothing to re-pin.
- **What changed:** a new test, `tests/test_srccov_rl_news_article_1121.py` (22 cases). It pins the verify facts and each drop reason, read from the repo. This REPORT and `mutants.json` are new too.
- **Correction (F1, review of 73da418189):** the first version of this REPORT claimed that a two-place wording had to be one of the `IDIOMS` entries, so a carry of S0001 c2, S0010 c2 or S0011 c1 needed a Lean and Python change. That was wrong. The linter's base shape (ve/printer.py:322-328) accepts a present-tense wording such as `{0} signals {1}`. It is not every present-tense wording: the shape refuses an auxiliary first word (is, are, was, were, be, been, being, gets, got; `BINARY_AUXILIARY`, :323) and a final by/to/of/from/with/for (`BINARY_CONVERSE`, :325), so `{0} signals to {1}`, `{0} gives guidance to {1}` and `{0} gets {1}` are refused, and the first word must end in s (`BINARY_VERB`, :327). These are refusals of the base shape only, not of the public path: a wording in the idiom list (`IDIOMS`, ve/english_vocabulary.py:12) or matching an `_ACTIVE` phrase (ve/english.py:39-45) passes anyway (ve/english.py:286,321). This document's own reviewed overlay keeps `{0} voted for {1}`, `{0} raised its policy rate to {1}` and `{0} was appointed by {1}` (environment.english.json:95,100,120), and `{0} reports to {1}`, `{0} communicates with {1}` and `{0} has responsibility for {1}` pass with no lint issue (correction F3; `test_the_idiom_list_and_active_phrases_pass_outside_the_base_shape`). The three wordings this REPORT proposes pass all three checks; the article's past-tense wordings would need an idiom. `test_the_base_shape_refuses_an_auxiliary_or_a_converse_ending[*]` pins both refusals (correction F2). The reason for the three drops is the overlay review binding (below). `test_a_present_tense_wording_passes_and_only_the_review_blocks[*]` pins it. The build report's paragraph "Why a new predicate needs a Lean and Python change" (manage-agents, not in this repo) is superseded by this REPORT.
- **Open:** nothing for this row. Three units (S0001 c2, S0010 c2, S0011 c1) can be carried once a non-builder reviewer records the changed overlay in `ve/reviewed-overlays.json` (see Notes for the DRI). No Lean or Python change is needed. Per override 3, that is not filed as work.

## 0. Verify table

The row is `srccov-news-article-s7-1-1119` (map pin `e53db4e8fc`, Opus reading, `reviews/source-coverage-1119/news-article.md` in manage-agents). Its units tagged `none: translation omission` are S0001, S0008, S0010, S0011 and S0014. I checked each one against `usecases/news-article/source.md` and against what main `cebf4fd24f` shows the reader: `claims.ve`, the `environment.json` legends and `environment.english.json`. The units tagged `attribution-evaluation` (S0002, S0004, S0009, S0012, S0013) are out of scope and unchanged.

| unit id | row id | KEPT / DROPPED | reason (file:line) |
|---|---|---|---|
| S0001 (c2 "signaled that further rate increases could come in the following months") | srccov-news-article-s7-1-1119 | DROPPED | The text is in the source (source.md:13) and no carrier holds it at main. A carry needs a new predicate, and that predicate needs reviewed English wording (tests/test_english.py:401,412). The wording itself is not the blocker: the linter's base shape (ve/printer.py:322-328) accepts `{0} signals {1}`, and a render and `parse_english` round trip gives the same `meaning_id`. The blocker is the overlay review binding (shared blocker, below): the new overlay is "unreviewed" until a non-builder record is added to `ve/reviewed-overlays.json`, which is outside this row's paths. (The past-tense `{0} signaled {1}` is not the base shape and no idiom holds it, but a present-tense wording avoids that.) Reusing `stated` ("issued this statement", environment.json:60-63) would say that a signal is a statement, so I did not take it (conservative). The content is also a "could" possibility plus a time window (also:modality,temporal). |
| S0008 (c3 "at the time expecting he would cut rates") | srccov-news-article-s7-1-1119 | DROPPED | The text is in the source (source.md:17). This is attitude content (an expectation). Also, the sentence does not say who held it: the participle attaches to "he" (Warsh) by grammar, while the context suggests Trump. It waits for srccov-design-attributed-1119. The dated audit has the same row as NO, "attitude report" (coverage.md row 12). The map row also names the order "after Trump selected him" (c2, loss:temporal). It is temporal, so out of this row's class, and it is dropped too. |
| S0010 (c2 "issued after a two-day meeting") | srccov-news-article-s7-1-1119 | DROPPED | The text is in the source (source.md:19) and no carrier holds it at main. A carry needs a new predicate. The linter accepts a present-tense wording such as `{0} follows {1}` (the past-tense `{0} was issued after {1}` and `{0} issued after {1}` are not the base shape). As for S0001, the blocker is the overlay review binding, not the wording. |
| S0011 (c1 "The statement gave no forward guidance about future decisions"; c2 "which is Warsh's preference") | srccov-news-article-s7-1-1119 | DROPPED | The text is in the source (source.md:20). c1 needs a new predicate. The linter accepts the binary present-tense `{0} gives forward guidance about {1}`, so the blocker is again the overlay review binding. The unary shape must be `{0} is <word>`, and the nearest, `{0} is guided`, would misstate the source, so I did not take it. c1 is also a negative existential over a vague category ("any forward guidance"; usecases/news-article/coverage.md:31). c2 is attitude content (a preference) and waits for srccov-design-attributed-1119. |
| S0014 (c2 "to explain the decision further") | srccov-news-article-s7-1-1119 | DROPPED | The text is in the source (source.md:22). This is purpose content (the map has also:causation-purpose). `purposes@0` is a designed slot the gate refuses (architect page srccov-features-20261120.md, row 6). The declared profile is `relational-fol@0` only (environment.json:2-3). |

Shared blocker for any carry: every change to `environment.json` changes `environment_id`. That rebinds the overlay digest (ve/english_vocabulary.py:79-92), so the 2026-09-21 record in ve/reviewed-overlays.json:23-28 stops matching. The overlay then drops to "unreviewed", and `test_reviewed_overlays_preserve_all_historical_views_and_identities` fails. A new record needs a reviewer who is not the builder (precedent: reviews/defs-repair-claude-constitution-excerpt-1119-dri-note-20261119.md). So even a carry that used only existing predicates would need a DRI decision whenever it changes `environment.json` (for example by adding a constant); a carry that changed only claims.ve would not rebind the overlay. This is the reason S0001 c2, S0010 c2 and S0011 c1 are dropped: each needs a new predicate, so each changes `environment.json`.

None of the five is already carried at main. No earlier srccov-news-article-1119, defs-repair, fsf-repair or rsp-repair row touched `usecases/news-article/` (`git log` on that directory: last change 9328122e7e, W6a). The news-w6a records for these clauses (`s1_rest` news-w6a.ve.md:187, `s4_s5` :286, `s7_rest` :460, `s8_s10` :472) are unformalised `relational_route_claims_ve`, and claims.ve has no matching line.

## 1. Units carried

None. `claims.ve`, `environment.json`, `environment.english.json`, `claims.map.md` and the w6a record are unchanged. `claims.map.md` already lists S0001 c2, S0008 c3 and sentence 8 under "Clauses with no claims.ve statement".

## 2. Derived files

None regenerated: no input changed. `rendered.md`, `rendered-english.md`, `conformance/english-lean/corpus-seal.json`, `tests/data/fidmech/wording-golden.json` and the conformance reports are byte-equal to main. `tools/fidmech/manifests.py` pins nothing from this document.

## 3. Answers touched

None. No line was added, so no answer or question changes status or verdict. I opened no sealed-read, answers/, reports/, counted-read or diagnostic file.

## 4. Condition test and seeded bugs

`tests/test_srccov_rl_news_article_1121.py` reads the source and carriers from the repo and checks these things:
- `test_the_clause_is_in_its_source_sentence[*]`: each in-scope clause is in its numbered source sentence, after `omit_norm`.
- `test_the_clause_is_not_carried_by_claims_or_legends[*]`: neither the clause nor the words it adds appear in claims.ve, any environment.json legend or the overlay.
- `test_every_predicate_needs_reviewed_overlay_wording` and `test_a_present_tense_wording_passes_and_only_the_review_blocks[*]`: these are the drop reason for S0001 c2, S0010 c2 and S0011 c1. The present-tense wording given for each (`{0} signals {1}`, `{0} follows {1}`, `{0} gives forward guidance about {1}`) has no linter issue and round-trips to the same `meaning_id`; only the review status ("unreviewed") fails.
- `test_the_overlay_linter_refuses_only_the_past_tense_wordings[*]`: the article's past-tense wordings are not the base shape. This is a fact about the wording, not a drop reason.
- `test_the_report_gives_the_review_binding_as_the_drop_reason`: probe F1 as a test. This REPORT and the test file name the review binding and do not repeat the false linter reason.
- `test_the_base_shape_refuses_an_auxiliary_or_a_converse_ending[*]` and `test_the_report_names_both_refusals_of_the_base_shape` (F2): the base shape does not take every present-tense wording. Each word of `_AUXILIARIES` and `_CONVERSE_ENDINGS` (read from ve/printer.py) is refused outside the idiom list (`IDIOMS`) and the `_ACTIVE` phrases, and the REPORT names both word sets exactly.
- `test_the_idiom_list_and_active_phrases_pass_outside_the_base_shape` and `test_the_refusal_claims_name_the_idiom_and_active_exceptions` (F3): the two exceptions. Every wording of this document's overlay that the base shape would refuse is an idiom and is kept, and every `_ACTIVE` phrase (expanded from ve/english.py) that the base shape would refuse passes the public path and the deferred lint with no issue. The second test is probe F3: wherever this file or the REPORT says such a wording is refused, it names both exceptions.
- `test_the_document_declares_only_relational_fol`: this is the drop reason for the attitude and purpose clauses.

The task asks for a test that fails on main and passes after. That cannot hold here, because no unit is kept and nothing changes. The test passes on main by design, and a case fails when its drop reason stops holding.

Seeded bugs (planted by `/tmp/na-proto/mutants.sh`, each run on the new test file and restored with `git checkout`; `git status` was clean after; log `/tmp/na-mutants.log`; also in `mutants.json`):

| id | file | change | failing test |
|---|---|---|---|
| M1 | ve/english_vocabulary.py | add the idiom `{0} signaled {1}` | `test_the_overlay_linter_refuses_only_the_past_tense_wordings[S0001-{0} signaled {1}]` (rerun on the F1 fix) |
| M2 | usecases/news-article/environment.json | carry "a two-day meeting" in the `sept_meeting` legend | `test_the_clause_is_not_carried_by_claims_or_legends[S0010]`, `test_every_predicate_needs_reviewed_overlay_wording` |
| M3 | usecases/news-article/source.md | "gave no forward guidance" becomes "offered no forward guidance" | `test_the_clause_is_in_its_source_sentence[S0011]` |
| M4 | usecases/news-article/environment.json | add a second profile key | `test_the_document_declares_only_relational_fol` (plus 7 more) |
| M5 | ve/printer.py:327 | the base binary shape refuses every wording (`if True:` for the `-s` verb check) | `test_a_present_tense_wording_passes_and_only_the_review_blocks[*]` (all 3) and `test_the_overlay_linter_refuses_only_the_past_tense_wordings[*]` (all 6): the planted check refuses the document's existing predicates too, so 9 fail, not 3 (F2 recheck); all 16 F2 cases fail as well |
| M7 | ve/printer.py:100 | drop `gets` from `_AUXILIARIES` | `test_the_base_shape_refuses_an_auxiliary_or_a_converse_ending[{0} gets {1}]`, `test_the_report_names_both_refusals_of_the_base_shape` |
| M8 | ve/printer.py:101 | drop `to` from `_CONVERSE_ENDINGS` | `test_the_base_shape_refuses_an_auxiliary_or_a_converse_ending[{0} signals to {1}]`, `[{0} gives guidance to {1}]`, `test_the_report_names_both_refusals_of_the_base_shape` |
| M9 | REPORT.md | restore the REPORT of 9f7fa89790 (its overclaim of the base shape) | `test_the_report_names_both_refusals_of_the_base_shape` |
| M6 | ve/english_vocabulary.py:87 | the review record no longer matches on the overlay digest | `test_a_present_tense_wording_passes_and_only_the_review_blocks[*]` (all 3), `test_every_predicate_needs_reviewed_overlay_wording` |
| M10 | tests/test_srccov_rl_news_article_1121.py | restore the F2 docstring ("the public path raises", no exception named) | `test_the_refusal_claims_name_the_idiom_and_active_exceptions` |
| M11 | ve/english.py:309 | no `_ACTIVE` phrase matches (`matches = []`) | `test_the_idiom_list_and_active_phrases_pass_outside_the_base_shape` |
| M12 | ve/english.py:350 | the idiom branch accepts nothing (`accepted = False and (...)`) | `test_the_idiom_list_and_active_phrases_pass_outside_the_base_shape`; this document's own overlay is then refused, so 26 fail in all |
| M13 | REPORT.md | restore the REPORT of 092f2ae082 (no exception named) | `test_the_refusal_claims_name_the_idiom_and_active_exceptions` |

M1, M5 and M6 for the F1 fix were planted by hand with `sed`, each run on the test file and restored with `git checkout -- ve/`; `git status` showed only this item's two files after (log `/tmp/na-f1-mutants.log`). With M1 and M5, `test_the_report_gives_the_review_binding_as_the_drop_reason` also failed, because the REPORT was not yet corrected at that point.

M10-M13 for the F3 fix were planted by hand (`sed` and a short Python edit), each run on the test file and restored (`git checkout -- ve/`, or a copy of the file saved before); `git status` showed only this item's two files after (logs `/tmp/na-f3/M10.log` to `M13.log`).

No product code changed (ve/, lean/, rust/ are untouched), so no language needs a seeded bug of its own. M1, M5 and M6 are in Python product code anyway.

## Tests run

- New file, local: `18 passed` (`/tmp/na-t1.log`); after the F1 fix, `22 passed` (`/tmp/na-f1-t2.log`).
- Selected: `mac-pytest.sh --select -- --base cebf4fd24f --run` ran on GitHub Actions (6 shards, run `srccov-rl-news-article-1121-6b7301ef-t226612`) and exited 0. The shards passed 34, 33, 33, 35, 28 and 26 units (189/678 units planned; 35 heavy files were deferred to the chain gate) (`/tmp/na-select.log`).
- Selection probe (checklist 9): with M1 planted, and again with a byte appended to source.md, `tools/select_tests.py --base cebf4fd24f` plans `tests/test_srccov_rl_news_article_1121.py` (`/tmp/na-sel-m1.log`, `/tmp/na-sel-m3.log`).
- Light lane: `LIGHT 127 changed lines ... no trusted-core file`, so no trust_mutants sweep.
- F1 fix (commit 6630d46c4a): `mac-pytest.sh --select -- --base cebf4fd24f --run` ran on GitHub Actions (5 shards, run `srccov-rl-news-article-1121-6630d46c-t228156`) and exited 0: 38, 39, 40, 40 and 41 units passed; 38 heavy files were deferred to the chain gate (`/tmp/na-f1-select.log`). `lake build`: `Build completed successfully (1478 jobs)`. `python3 lean/audit.py`: PASS, 898 source files.
- F2 fix (commit fbc1f25c7a): test file local `39 passed` (`/tmp/f2-t5.log`); probe F2 exits 0 (it exited 1 before the fix). `mac-pytest.sh --select -- --base cebf4fd24f --run` ran on GitHub Actions (6 shards, run `srccov-rl-news-article-1121-fbc1f25c-t230358`) and exited 0: 29, 35, 33, 34, 33 and 34 units passed (198); 38 heavy files were deferred to the chain gate (`/tmp/f2-select.log`). `lake build`: `Build completed successfully (1478 jobs)`. `python3 lean/audit.py`: PASS, 898 source files.
- F3 fix: test file local `41 passed` (`/tmp/f3-t2.log`); probe F3 exits 0 (it exited 1 before the fix). Selected run: see the next commit.
- I did not run the full gate (task rule): the chain runs it on the final HEAD.

SIZE: 0 product, 127 tests at first (289 lines in the test file after the F1-F3 fixes), 0 other hand-written lines (plus this REPORT and mutants.json).

## Notes for the DRI

- **One seam blocks three units.** S0001 c2, S0010 c2 and S0011 c1 are plain relational facts. The reviewed-overlay record is what stops all three; the table above also notes modality and time for S0001 c2 and a vague negative existential for S0011 c1, which a carry must still word conservatively. A later item can add three predicates with the present-tense wordings `{0} signals {1}`, `{0} follows {1}` and `{0} gives forward guidance about {1}`, which the linter accepts (not every present-tense wording passes: see the F2 correction above). No Lean or Python change and no new idiom is needed. It does need a non-builder overlay read and a `ve/reviewed-overlays.json` record, as in the claude-constitution-excerpt precedent. With those, the three units can be carried in claims.ve. The sibling rows on other claims.ve documents with English overlays will likely hit the same seam.
- **The w6a records describe these clauses inaccurately.** The units `s1_rest`, `s7_rest` and `s8_s10` give the reason `relational_route_claims_ve`. The w6a build script's docstring says those clauses' relational claims "live in claims.ve" (build_w6a_document.py:8-9), but for these clauses claims.ve has no line. Changing the reason would regenerate news-w6a.ve.md and coverage.json and move the dashboard's measured counts. That record is shared with units this row may not touch, so I left it. METHOD amendment 13 already counts these as known gaps.
- **Conservative choices.** I did not reuse `stated` for "signaled", did not use `{0} is guided`, and did not pick a holder for S0008's "expecting". Each would have added content the source does not state.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer is typed and contained: N.A. (no route or relay touched).
2. Every deliverable is built: PASS. The verify table, the carry (none kept), regeneration (none needed), answers (none) and the condition test are all done (`test_the_clause_is_in_its_source_sentence[*]`, `test_a_present_tense_wording_passes_and_only_the_review_blocks[*]`). Diff grep: no new Python copy of a Lean decision and no report test reading live git.
3. Tests can fail: PASS (M1-M13 above).
4. Python, Lean and Rust agree: N.A. (no product code changed).
5. R8 binding: N.A. (no Lean answer read).
6. Gate evidence matches the final HEAD: PASS. The branch is on current main `cebf4fd24f`, and the chain runs the gate on the final HEAD.
7. No unsigned item: PASS (no DELTA row, no trust growth).
8. Every user-visible change is in DELTA: PASS. There is no user-visible change: no carrier, rendering or output differs from main.
9. Selection finds the tests: PASS (selection probe above).
10. Lean statements and proofs: N.A.
11. Budgets and deadlines fail closed: N.A.
12. No CPU or memory regression: N.A. (only a test file was added).
