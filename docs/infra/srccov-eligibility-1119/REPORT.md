# srccov-eligibility-1119: REPORT

No DRI signature needed: DELTA.md rows 1-2 cite R3; trust +0; no reserved row.

**Summary.** Ready for the gate. HEAD rebased on main 12cb72fa55 (the VE commit this merges at, unless main moves).
Of the 7 candidate rows, 6 are kept (rows 1 and 11 in part) and row 10 is dropped. 3 units are carried word for word on two legends (reached_pa, entitled), and all 52 OUT-OF-SCOPE-UNRECORDED units are recorded in the translation.py comment block (the document's record file).
The change is text only. Derived files were regenerated with their tools. Verdicts are unchanged (269/269 answers, 32/32 mutants). There are no FOLLOW-UPs.

## Verify table (deliverable 0)

The source is usecases/eligibility/source/*.txt at main (S1 = uksi-2025-969-made.txt, S2 = wfp-print.txt, Sch4 = ukpga-1995-26-sch4.txt). It is unchanged between the map's pin e53db4e8fc and main: `git diff --stat e53db4e8fc HEAD -- usecases/eligibility` printed only corpus-seal.json.
The script /tmp/sce1119/atmain.py (not committed; log /tmp/sce1119/atmain.log) checked the 55 kept units. Each one's text is at its span in the source (the byte offsets in units-eligibility.tsv, line breaks read as spaces). None of them is in environment.json, rules.json or translation.py at main, and no unit id is there either.

| row | verdict | units kept | reason |
|---|---|---|---|
| srccov-eligibility-1-1119 | KEPT (2 of 12) | S0005, S0015 | S0015 is the S1 definition (S1:34), carried word for word on the reached_pa legend. reached_pa is used by rule R2 (`test_each_carrying_legend_belongs_to_a_predicate_a_rule_uses`). S0005 (S1:16) is the lead-in of S1 reg. 1(3). Its items S0006-S0025 are all carried once S0015 is (METHOD amendment 8b), and its text goes in front of the definition, as the "(4) In these Regulations, a person—" lead-in already does for residential care. DROPPED: S0115 (Sch4:10, the lead-in of the rules) and the table rows S0125, S0135, S0145, S0155, S0165, S0185, S0205 (Sch4:42, :62, :82, :102, :125, :168, :211). Each maps a birth-date range to a date of pensionable age: a rule or fact, not a legend. Map row 9 holds the same units with needs_rule_line=yes, and translation.py:35-44 (bridge B2) is a constant table, which cannot carry them. Also DROPPED: S0175 (Sch4:145, "attains pensionable age when the person attains the age of 66": a condition and a number, row 9) and S0285 (Sch4:343, a Sch. 4 amendment of SSCBA s.122(1), not the words of the S1 definition; row 17 needs_rule_line=yes). |
| srccov-eligibility-2-1119 | KEPT | S0033 | S1:60 is carried word for word on the entitled legend. entitled is used by R13 and the Q1 goal. Its items S0034-S0035 were already carried in other words (map class); this carries the missing clause "the Secretary of State must pay … out of the social fund" as legend text (via:legend, METHOD amendment 5). |
| srccov-eligibility-10-1119 | DROPPED | none | The units S0209-S0345 (Sch4:238-:429) are Category B retirement pension rules and the Sch. 4 amending text. They hold modals ("shall be entitled", Sch4:242), conditions and numbers, and the map class is ABSENT. Under METHOD amendment 12 and this task's recording rule, such a unit is never recorded as out of scope. A comment is not a carrier, and rows 15-18 (needs_rule_line=yes) hold the shared units. |
| srccov-eligibility-11-1119 | KEPT (6 of 9) | S0067, S0068, S0069, S0070, S0090, S0091 | Recorded as change log (S1:100-104, :131-132), translation.py:185-188. DROPPED: S0305, S0315, S0355 (Sch4:383, :393, :439). The merge kept them ABSENT (eligibility.md overlap table) and placed them in row 18 (needs_rule_line=yes). They are not among the 52 OUT-OF-SCOPE-UNRECORDED units. |
| srccov-eligibility-12-1119 | KEPT | S0094, S0095, S0097, S0099-S0113 (18) | Recorded as history (the footnotes on the amendment history of the cited Acts), translation.py:189-193. |
| srccov-eligibility-13-1119 | KEPT | S0071 | Recorded as editorial annotation (S1:112, under "(This note is not part of the Regulations)", S1:111), translation.py:194-195. |
| srccov-eligibility-28-1119 | KEPT | S0449 | Recorded as rationale (S2:114), translation.py:196. |

### RECORDING (orchestrator ruling item 2a: the 52 OUT-OF-SCOPE-UNRECORDED units)

All 52 units are RECORDED in usecases/eligibility/translation.py:167-196, the comment block "Out of scope (srccov-eligibility-1119)". Each record gives the kind, a name for the content and `<unit> <file>:<line>`.
None was carried or recorded at main (atmain.log). None holds must/shall/should/will/may/never or "means": atmain.py printed MODAL only for S0033, a carry and not a record.
The numbers these units contain are citations (section, S.I. and footnote numbers), headings or instrument years used as names, which matches the map's notes (amendment 12). So none of them is "absent, not recordable".

| unit | verdict | record file:line (kind) |
|---|---|---|
| S0001 | RECORDED | translation.py:173 (metadata) |
| S0092 | RECORDED | translation.py:173 (metadata) |
| S0374 | RECORDED | translation.py:173 (metadata) |
| S0114 | RECORDED | translation.py:175 (title) |
| S0223 | RECORDED | translation.py:175 (title) |
| S0243 | RECORDED | translation.py:175 (title) |
| S0268 | RECORDED | translation.py:176 (title) |
| S0293 | RECORDED | translation.py:176 (title) |
| S0401 | RECORDED | translation.py:176 (title) |
| S0432 | RECORDED | translation.py:176 (title) |
| S0441 | RECORDED | translation.py:176 (title) |
| S0446 | RECORDED | translation.py:176 (title) |
| S0480 | RECORDED | translation.py:177 (title) |
| S0073 | RECORDED | translation.py:180 (navigation or page furniture) |
| S0164 | RECORDED | translation.py:180 (navigation or page furniture) |
| S0177 | RECORDED | translation.py:180 (navigation or page furniture) |
| S0195 | RECORDED | translation.py:180 (navigation or page furniture) |
| S0386 | RECORDED | translation.py:180 (navigation or page furniture) |
| S0451 | RECORDED | translation.py:181 (navigation or page furniture) |
| S0487 | RECORDED | translation.py:181 (navigation or page furniture) |
| S0093 | RECORDED | translation.py:183 (bare citation or pointer) |
| S0096 | RECORDED | translation.py:183 (bare citation or pointer) |
| S0098 | RECORDED | translation.py:183 (bare citation or pointer) |
| S0455 | RECORDED | translation.py:184 (bare citation or pointer) |
| S0459 | RECORDED | translation.py:184 (bare citation or pointer) |
| S0479 | RECORDED | translation.py:184 (bare citation or pointer) |
| S0067 | RECORDED | translation.py:187 (change log) |
| S0068 | RECORDED | translation.py:187 (change log) |
| S0069 | RECORDED | translation.py:188 (change log) |
| S0070 | RECORDED | translation.py:188 (change log) |
| S0090 | RECORDED | translation.py:188 (change log) |
| S0091 | RECORDED | translation.py:188 (change log) |
| S0094 | RECORDED | translation.py:190 (history) |
| S0095 | RECORDED | translation.py:190 (history) |
| S0097 | RECORDED | translation.py:190 (history) |
| S0099 | RECORDED | translation.py:190 (history) |
| S0100 | RECORDED | translation.py:191 (history) |
| S0101 | RECORDED | translation.py:191 (history) |
| S0102 | RECORDED | translation.py:191 (history) |
| S0103 | RECORDED | translation.py:191 (history) |
| S0104 | RECORDED | translation.py:191 (history) |
| S0105 | RECORDED | translation.py:191 (history) |
| S0106 | RECORDED | translation.py:192 (history) |
| S0107 | RECORDED | translation.py:192 (history) |
| S0108 | RECORDED | translation.py:192 (history) |
| S0109 | RECORDED | translation.py:192 (history) |
| S0110 | RECORDED | translation.py:192 (history) |
| S0111 | RECORDED | translation.py:192 (history) |
| S0112 | RECORDED | translation.py:193 (history) |
| S0113 | RECORDED | translation.py:193 (history) |
| S0071 | RECORDED | translation.py:195 (editorial annotation) |
| S0449 | RECORDED | translation.py:196 (rationale) |

## Rows carried (deliverables 1-2)

- Carries, in usecases/eligibility/translation.py. `DEFINITIONS["pensionable age"]` (:112, S1:16 + S1:34) and `DEFINITIONS["regulation 2"]` (:115, S1:60) are taken word for word from the source lines, and `LEGEND_DEFINITIONS` adds `reached_pa` and `entitled` (:163-164). `legend()` appends them to the existing descriptions, which are kept whole. The comment above DEFINITIONS now says "definitions and wording", because reg. 2's lead-in is wording, not a definition.
- Records: the comment block at :167-196 (deliverable 1, "an out-of-scope record in the form … the document's record file already uses"). METHOD section 0 makes translation.py comments the eligibility record file. The form follows translation.py:542-544 ("… are out of scope (PLAN O7)").
- Derived files, all regenerated by their tools and never by hand:
  - `uv run python usecases/eligibility/run.py` rewrote environment.json and results.json. rules.json and RESULTS.md came out byte-equal. Log /tmp/sce1119/run.log: 6 min 2 s, `"mutants_killed": "32/32"`, 269/269 documents admitted.
  - `uv run python -m conformance.english_lean_seal` rewrote corpus-seal.json, again after the rebase.
  - `uv run python -m conformance.english_lean_lexicon` rewrote lexicon-report.json (`{"valid": 43, "invalid": 0}`).
  - `uv run python tools/regen_generated.py --check` exits 0 after the rebase ("checked 41 entries", /tmp/sce1119/regencheck2.log).
- translation.py is not hashed in corpus-seal.json (only environment.json is), so the seal changes only through environment.json.

## Answers the change touches (for later reads to re-pin)

reached_pa is in rule R2 and entitled is in Q1, and every case uses both, so all 80 eligibility profiles (all 269 keyed answers) now run under environment_id 00315b75bba7… (was b3325267dc0f…). No answer value changed: evidence/results-delta.json has `answers_equal`, `summary_equal` and `mutants_equal` true, and its only changed paths are `/environment_id` and `/seconds`.
A read pinned to the old legends of reached_pa or entitled, or to the old environment_id or lexicon_id, re-pins. The recorded units add no shown text, so they touch no answer.

## Condition test (deliverable 3)

New file: tests/test_srccov_eligibility_1119.py, 65 tests.
- **Carries.** Each source line, read from the repo, is in the shown environment.json legend after `omit_norm`, and the carrying predicate is used by a rule.
- **Records.** The record block parsed from translation.py's comment tokens equals the expected `unit -> (kind, file, line)` map exactly: no unit missing, none extra, none duplicated. Each cited line holds the unit's opening words.
- **Opposite direction.** A legend with the sentence cut out fails the carry check. A block that drops a unit, duplicates one, shifts a line or changes a kind fails the record check.
- **Fails on main.** With main's translation.py, environment.json and rules.json checked out: "9 failed, 56 passed" (/tmp/sce1119/t-main.log). The failures are the three carries, the carry refusal and the block-equality tests. On HEAD: "65 passed" (/tmp/sce1119/t-head.log).
- **Stays selected.** A comment-only edit of translation.py's record block selects it ("tests/test_srccov_eligibility_1119.py: names usecases/eligibility/translation.py (static)", /tmp/sce1119/sel-comment.log).

## Seeded bugs (all Python, usecases/eligibility/translation.py; mutants.json)

Script: /tmp/sce1119/mutants.sh, log /tmp/sce1119/mutants.log. For each mutant the script applied the edit, rewrote environment.json the way run.py does, ran the new test file, then restored with `git checkout`. The tree was clean afterwards.

| id | carry kind | change | failing test |
|---|---|---|---|
| M1 | legend carry: carried sentence removed | `LEGEND_DEFINITIONS["entitled"] = ()` | `test_each_carried_unit_is_on_the_shown_legend_word_for_word[S0033]` (and the refusal test) |
| M2 | legend carry: one word changed | "paragraph 1" -> "paragraph 2" in the S0015 text | `…word_for_word[S0015]` |
| M3 | lead-in carry: lead-in removed | drop "(3) In these Regulations—" | `…word_for_word[S0005]` (S0015 also failed: the join then spells out characters) |
| M4 | record removed | drop "S0449 S2:114" | `test_the_record_block_lists_exactly_the_recorded_units_with_their_kind_and_line` |
| M5 | record at the wrong line | "S0001 S1:11" -> "S1:12" | same |
| M6 | record under the wrong kind | the "editorial annotation" header renamed "rationale" | same |

## Tests, trust, light lane

- Selected run on the pre-rebase HEAD 0efaaed3: `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` ran on GitHub Actions in 4 shards. 77 units, 77 passed, exit 0, 825 s (/tmp/sce1119/select.log:108, :204, :300, :396-397). The 9 slow files it selected only for weak reasons are deferred to the chain gate (log line 5).
- After the rebase (only the seal moved: main changed no eligibility file, `git diff --stat 09bea0972d 12cb72fa55 -- usecases/eligibility` is empty): tests/test_srccov_eligibility_1119.py, test_defs_repair_eligibility_1119.py and test_english_lean_seal.py gave "89 passed" (/tmp/sce1119/t2.log).
- Light lane: `light-lane.py check` printed "NOT 248 changed lines outside generated files > 150". The sweep `mac-pytest.sh --trustmut -- --json docs/infra/srccov-eligibility-1119/evidence/trust-mutants.json` found "0 definitions, 0 mutants", exit 0, because no Lean changed (/tmp/sce1119/tm.log).
- Trust: `uv run python tools/trust_map.py --check` reports "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0; PASS" (/tmp/sce1119/trustmap.log).
- Known-red tests on main (main-known-red.txt): none in the selection, none touched.
- The full gate is not run here; the chain runs it on the final HEAD.

SIZE: 41 product (translation.py: 39 added, 2 changed), 191 tests, 213 other hand-written lines (REPORT, DELTA, mutants.json); generated: environment.json 4, results.json 4, corpus-seal.json 6, lexicon-report.json 2, evidence 21.

## Spec re-read

- Carry "word for word from the source" against usecases/eligibility/source/uksi-2025-969-made.txt:16, :34, :60. The DEFINITIONS strings equal those lines byte for byte, and the test reads the lines from the repo.
- Record "in the form that file already uses" against METHOD section 0 (eligibility: comments in translation.py) and amendment R ("a comment counts only if it names the content as left out"). Each group says "out of scope" and names its content.
- METHOD amendment 12 against each recorded unit's text (atmain.log MODAL column) and against row 10, which is dropped.
- METHOD amendment 4 (a legend counts only on a used symbol): `test_each_carrying_legend_belongs_to_a_predicate_a_rule_uses`.
- Task rule "comment only is not a carrier": rows 11, 12, 13 and 28 are records the method accepts. Row 10 was not one, so it is dropped.

## Notes for the DRI

- Row 10 (42 Sch. 4 units on Category B pensions and amendments to other Acts) and the dropped Sch. 4 units of rows 1 and 11 stay ABSENT. They are a rule-line decision for rows 9 and 15-18, or an out-of-scope ruling the task's recording rule does not allow here.
- The earlier FOLLOW-UP defs-eligibility-1b-1119 (carry the whole of Sch. 4 para. 1 on reached_pa) is still open. This item carries only S1's definition by reference (S1:34). If that item lands, it appends after this text, and the two do not conflict.
- main's corpus-seal.json was stale for usecases/safety-framework/environment.d1.json (after the fsf-repair merges). The regenerated seal now holds the true hash of main's file (DELTA row 2). Sibling items that regenerate the seal will get the same value.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relay, schema or route changed (diff: translation.py text, generated files, tests, docs).
2. Deliverables built, no rule broken: PASS. Deliverable 0 is the verify table, 1 the carries and records (commit 0487c03d54), 2 the regeneration (b6c5b27918, 2f7999ac34), 3 tests/test_srccov_eligibility_1119.py. There is no Python copy of a Lean decision and no permanent report test (D4): the evidence is read from saved files only.
3. Tests can fail: PASS, mutants M1-M6 (mutants.json, /tmp/sce1119/mutants.log). The trust sweep had 0 mutants (no Lean).
4. Python, Lean and Rust agree: PASS. run.py: 269/269 documents admitted by Lean, 2352/2352 certificates (/tmp/sce1119/run.log). No Rust or Lean code changed.
5. R8 binding: N.A., no field is read from a Lean answer.
6. Gate evidence matches the final HEAD: PASS. Rebased on main 12cb72fa55 and regenerated. The chain gates the final HEAD.
7. No unsigned item: PASS. The DELTA.md Ruling cells cite R3, with tests named.
8. Every user-visible change in DELTA: PASS. results.json was diffed path by path (evidence/results-delta.json), and the legends, ids and seal are rows 1-2.
9. Test selection finds the tests: PASS. A comment-only edit selects the new test (/tmp/sce1119/sel-comment.log line 74).
10. Lean statements: N.A., no Lean change.
11. Budgets and deadlines: N.A., no limit or deadline code. The new tests have no sleeps or timeouts.
12. CPU and memory: N.A. Legend text only, and run.py took 6 min 2 s against 14 min 30 s in the precedent (wall time only, not a measure).
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. `test_the_carry_check_refuses_a_legend_without_the_sentence` and `test_the_record_check_refuses_an_edited_block[*]` cover the refusal side. The claims above cite /tmp/sce1119 logs, and the spec re-read is above.
15. No overclaim, no silent cut, new checks can fail, limits: PASS. "All 52" is backed by `test_the_record_block_lists_exactly_the_recorded_units_with_their_kind_and_line`; "unchanged" by results-delta.json. Row 10 and the dropped units are named as dropped, not carried. No limit was added.
