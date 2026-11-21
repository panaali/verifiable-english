# srccov-rl-news-article-1121: REPORT

- **Status:** verify done. All 5 in-scope units are DROPPED, so 0 are carried. No carrier, legend or derived file changed. No DRI signature is needed and no DELTA row exists.
- **HEAD / merge commit:** branch `infra/srccov-rl-news-article-1121` on main `cebf4fd24f`. This merges at the train's merge commit of its last commit (the chain's final HEAD). No answer, question, carrier or seal changes, so a later FSF read on this document has nothing to re-pin.
- **What changed:** a new test, `tests/test_srccov_rl_news_article_1121.py` (18 cases). It pins the verify facts and each drop reason, read from the repo. This REPORT and `mutants.json` are new too.
- **Open:** nothing for this row. Three units (S0001 c2, S0010 c2, S0011 c1) can be carried once the English idiom list grows (see Notes for the DRI). Per override 3, that is not filed as work.

## 0. Verify table

The row is `srccov-news-article-s7-1-1119` (map pin `e53db4e8fc`, Opus reading, `reviews/source-coverage-1119/news-article.md` in manage-agents). Its units tagged `none: translation omission` are S0001, S0008, S0010, S0011 and S0014. I checked each one against `usecases/news-article/source.md` and against what main `cebf4fd24f` shows the reader: `claims.ve`, the `environment.json` legends and `environment.english.json`. The units tagged `attribution-evaluation` (S0002, S0004, S0009, S0012, S0013) are out of scope and unchanged.

| unit id | row id | KEPT / DROPPED | reason (file:line) |
|---|---|---|---|
| S0001 (c2 "signaled that further rate increases could come in the following months") | srccov-news-article-s7-1-1119 | DROPPED | The text is in the source (source.md:13) and no carrier holds it at main. A carry needs a new predicate (`signaled`), and that predicate needs reviewed English wording (tests/test_english.py:401,412). The overlay linter accepts a binary template only from the fixed idiom list (ve/english_vocabulary.py:12-60, Lean copy lean/VE/EnglishGrammar/Lexicon.lean:133-163), and it refuses `{0} signaled {1}` and `{0} signaled that {1}` (ve/english.py:549). Adding an idiom is a Lean and Python change, which is out of scope. Reusing `stated` ("issued this statement", environment.json:60-63) would say that a signal is a statement, so I did not take it (conservative). The content is also a "could" possibility plus a time window (also:modality,temporal). |
| S0008 (c3 "at the time expecting he would cut rates") | srccov-news-article-s7-1-1119 | DROPPED | The text is in the source (source.md:17). This is attitude content (an expectation). Also, the sentence does not say who held it: the participle attaches to "he" (Warsh) by grammar, while the context suggests Trump. It waits for srccov-design-attributed-1119. The dated audit has the same row as NO, "attitude report" (coverage.md row 12). |
| S0010 (c2 "issued after a two-day meeting") | srccov-news-article-s7-1-1119 | DROPPED | The text is in the source (source.md:19) and no carrier holds it at main. A carry needs a new predicate (`issued_after`). The linter refuses `{0} was issued after {1}` and `{0} issued after {1}` (ve/english.py:549; the list is at ve/english_vocabulary.py:12-60). This is the same Lean and Python idiom change as S0001. |
| S0011 (c1 "The statement gave no forward guidance about future decisions"; c2 "which is Warsh's preference") | srccov-news-article-s7-1-1119 | DROPPED | The text is in the source (source.md:20). c1 needs a new predicate, and the linter refuses `{0} gave forward guidance about future decisions` and `{0} gave forward guidance about {1}`. The only nearby unary shape it accepts, `{0} is guided`, would misstate the source, so I did not take it. c2 is attitude content (a preference) and waits for srccov-design-attributed-1119. |
| S0014 (c2 "to explain the decision further") | srccov-news-article-s7-1-1119 | DROPPED | The text is in the source (source.md:22). This is purpose content (the map has also:causation-purpose). `purposes@0` is a designed slot the gate refuses (architect page srccov-features-20261120.md, row 6). The declared profile is `relational-fol@0` only (environment.json:2-3). |

Shared blocker for any carry: every change to `environment.json` changes `environment_id`. That rebinds the overlay digest (ve/english_vocabulary.py:79-92), so the 2026-09-21 record in ve/reviewed-overlays.json:23-28 stops matching. The overlay then drops to "unreviewed", and `test_reviewed_overlays_preserve_all_historical_views_and_identities` fails. A new record needs a reviewer who is not the builder (precedent: reviews/defs-repair-claude-constitution-excerpt-1119-dri-note-20261119.md). So even a carry that used only existing predicates would need a DRI decision. No unit reached that point.

None of the five is already carried at main. No earlier srccov-news-article-1119, defs-repair, fsf-repair or rsp-repair row touched `usecases/news-article/` (`git log` on that directory: last change 9328122e7e, W6a). The news-w6a records for these clauses (`s1_rest` news-w6a.ve.md:187, `s4_s5` :286, `s7_rest` :460, `s8_s10` :472) are unformalised `relational_route_claims_ve`, and claims.ve has no matching line.

## 1. Units carried

None. `claims.ve`, `environment.json`, `environment.english.json`, `claims.map.md` and the w6a record are unchanged. `claims.map.md` already lists S0001 c2, S0008 c3 and sentence 8 under "Clauses with no claims.ve statement".

## 2. Derived files

None regenerated: no input changed. `rendered.md`, `rendered-english.md`, `conformance/english-lean/corpus-seal.json`, `tests/data/fidmech/wording-golden.json` and the conformance reports are byte-equal to main. `tools/fidmech/manifests.py` pins nothing from this document.

## 3. Answers touched

None. No line was added, so no answer or question changes status or verdict. I opened no sealed-read, answers/, reports/, counted-read or diagnostic file.

## 4. Condition test and seeded bugs

`tests/test_srccov_rl_news_article_1121.py` reads the source and carriers from the repo and checks four things:
- `test_the_clause_is_in_its_source_sentence[*]`: each in-scope clause is in its numbered source sentence, after `omit_norm`.
- `test_the_clause_is_not_carried_by_claims_or_legends[*]`: neither the clause nor the words it adds appear in claims.ve, any environment.json legend or the overlay.
- `test_every_predicate_needs_reviewed_overlay_wording` and `test_the_overlay_linter_refuses_the_wording_a_carry_needs[*]`: these are the drop reasons for S0001, S0010 and S0011 c1.
- `test_the_document_declares_only_relational_fol`: this is the drop reason for the attitude and purpose clauses.

The task asks for a test that fails on main and passes after. That cannot hold here, because no unit is kept and nothing changes. The test passes on main by design, and a case fails when its drop reason stops holding.

Seeded bugs (planted by `/tmp/na-proto/mutants.sh`, each run on the new test file and restored with `git checkout`; `git status` was clean after; log `/tmp/na-mutants.log`; also in `mutants.json`):

| id | file | change | failing test |
|---|---|---|---|
| M1 | ve/english_vocabulary.py | add the idiom `{0} signaled {1}` | `test_the_overlay_linter_refuses_the_wording_a_carry_needs[S0001-{0} signaled {1}]` |
| M2 | usecases/news-article/environment.json | carry "a two-day meeting" in the `sept_meeting` legend | `test_the_clause_is_not_carried_by_claims_or_legends[S0010]`, `test_every_predicate_needs_reviewed_overlay_wording` |
| M3 | usecases/news-article/source.md | "gave no forward guidance" becomes "offered no forward guidance" | `test_the_clause_is_in_its_source_sentence[S0011]` |
| M4 | usecases/news-article/environment.json | add a second profile key | `test_the_document_declares_only_relational_fol` (plus 7 more) |

No product code changed (ve/, lean/, rust/ are untouched), so no language needs a seeded bug of its own. M1 is in Python product code anyway.

## Tests run

- New file, local: `18 passed` (`/tmp/na-t1.log`).
- Selected: `mac-pytest.sh --select -- --base cebf4fd24f --run` ran on GitHub Actions (6 shards, run `srccov-rl-news-article-1121-6b7301ef-t226612`) and exited 0. The shards passed 34, 33, 33, 35, 28 and 26 units (189/678 units planned; 35 heavy files were deferred to the chain gate) (`/tmp/na-select.log`).
- Selection probe (checklist 9): with M1 planted, and again with a byte appended to source.md, `tools/select_tests.py --base cebf4fd24f` plans `tests/test_srccov_rl_news_article_1121.py` (`/tmp/na-sel-m1.log`, `/tmp/na-sel-m3.log`).
- Light lane: `LIGHT 127 changed lines ... no trusted-core file`, so no trust_mutants sweep.
- I did not run the full gate (task rule): the chain runs it on the final HEAD.

SIZE: 0 product, 127 tests, 0 other hand-written lines (plus this REPORT and mutants.json).

## Notes for the DRI

- **One seam blocks three units.** S0001 c2, S0010 c2 and S0011 c1 are plain relational facts. Only the English surface stops them: the fixed idiom list (Lean `idioms2` and Python `IDIOMS`) plus the reviewed-overlay record. A later item could add three idioms, for example `{0} signaled {1}`, `{0} was issued after {1}` and `{0} gave forward guidance about {1}`. It would also need a non-builder overlay read and a `ve/reviewed-overlays.json` record, as in the claude-constitution-excerpt precedent. With those, the three units can be carried in claims.ve. The sibling rows on other claims.ve documents with English overlays will likely hit the same seam.
- **The w6a records describe these clauses inaccurately.** The units `s1_rest`, `s7_rest` and `s8_s10` give the reason `relational_route_claims_ve`. The w6a build script's docstring says those clauses' relational claims "live in claims.ve" (build_w6a_document.py:8-9), but for these clauses claims.ve has no line. Changing the reason would regenerate news-w6a.ve.md and coverage.json and move the dashboard's measured counts. That record is shared with units this row may not touch, so I left it. METHOD amendment 13 already counts these as known gaps.
- **Conservative choices.** I did not reuse `stated` for "signaled", did not use `{0} is guided`, and did not pick a holder for S0008's "expecting". Each would have added content the source does not state.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer is typed and contained: N.A. (no route or relay touched).
2. Every deliverable is built: PASS. The verify table, the carry (none kept), regeneration (none needed), answers (none) and the condition test are all done (`test_the_clause_is_in_its_source_sentence[*]`, `test_the_overlay_linter_refuses_the_wording_a_carry_needs[*]`). Diff grep: no new Python copy of a Lean decision and no report test reading live git.
3. Tests can fail: PASS (M1-M4 above).
4. Python, Lean and Rust agree: N.A. (no product code changed).
5. R8 binding: N.A. (no Lean answer read).
6. Gate evidence matches the final HEAD: PASS. The branch is on current main `cebf4fd24f`, and the chain runs the gate on the final HEAD.
7. No unsigned item: PASS (no DELTA row, no trust growth).
8. Every user-visible change is in DELTA: PASS. There is no user-visible change: no carrier, rendering or output differs from main.
9. Selection finds the tests: PASS (selection probe above).
10. Lean statements and proofs: N.A.
11. Budgets and deadlines fail closed: N.A.
12. No CPU or memory regression: N.A. (only a test file was added).
