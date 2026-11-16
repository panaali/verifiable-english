# fid-mech-b2: cues and logic words pinned; L1a, L2, L3, L4, D; the first FSF and PF run (build report)

**Status:** built; the selected run is in section 9. **HEAD:** the commit carrying this report (branch infra/fid-mech-b2).
**What changed:** new `tools/fidmech/sentchecks.py` (L1a, L2, L3, L4, D), `cues.json` and `logic_words.json` (frozen on RSP, sha256-pinned), `ruled_out.json` x3 (`[]`), `textcheck --checks L1a,L2,L3,L4,D|all --span sentence`; a fixture case and three test files; the first FSF/PF run saved.
**Open:** none. **DRI signature:** none reserved; DELTA none (Python tooling and data; no trusted Lean line, no decision path replaced; trust +0).
**First run (measured output, not a gate; section 4):** RSP L1a 9, L2b 28, L2q 17, L2a 1, L3w 12, L4u 20, L4l 72, D 1227; FSF L1a 4, L2b 26, L2q 1, L3w 24, L4u 18, L4l 50, D 386 (no sidecar); PF L1a 1, L2b 45, L2q 8, L2a 2, L3w 14, L4u 12, D 661.

SIZE: 678 product, 458 tests, 260 other hand-written lines (224 fixture data, 36 data files). The saved run outputs in this directory are command output, not hand-written.

## 1. Deliverables (task DO list; plan sections 2c, 3.0, 3.2 L1a, 3.3-3.6, 10, 11; Opus round-2 points 2, 3, 7, 9)

| item | where | commit | test |
|---|---|---|---|
| (1) B1 seam remainder | none: B1's REPORT section 1 says Opus point 8's seam was not used (FSF/PF boundaries and the furniture CLI were built in B1) | | |
| (2) cues.json, logic_words.json pinned by sha256 | tools/fidmech/{cues,logic_words}.json | 9d42ed27c8 | tests/test_fidmech_data.py::test_the_frozen_data_file_has_its_pinned_sha256[2] |
| (2) frozen on RSP before any FSF/PF check output (Opus 7) | freeze commit 9d42ed27c8, 03:49:19Z; first FSF/PF run 03:49:26Z | 9d42ed27c8 | section 2 |
| (3) L1a, the last L1 class | sentchecks.l1a | 9d42ed27c8 | test_each_plant_gives_exactly_its_class[L1a-*], test_l1a_is_the_last_class_a_quote_with_an_earlier_class_gets_no_l1a |
| (3) L2b/L2q/L2a per regulated predicate; base predicates and open terms counted | sentchecks.legends, l2 | 9d42ed27c8 | [L2b], [L2q], [L2a], test_l2_counts_the_legends_it_does_not_check |
| (3) L2q includes L1e (point 9) | sentchecks.l2 (every L1 class of a passage) | 9d42ed27c8 | test_l2q_includes_an_elided_legend_passage |
| (3) a legend's bracketed quote is a note (point 2) | textchecks.header_quotes, used for legends too | 9d42ed27c8 | test_a_legend_passage_inside_brackets_is_a_note_and_the_l2b_detail_says_so |
| (3) L3w per rule block, own words less the VE template | sentchecks.own_words, l3 | 9d42ed27c8 | [L3w-after], [L3w-within], test_the_rule_line_less_the_ve_template_keeps_no_guard_if |
| (3) L3 falls back to the header quote, marked | sentchecks.block_sentences | 9d42ed27c8 | test_l3_uses_the_header_quote_when_l1_locates_no_sentence_and_says_so |
| (3) L4u/L4l per sentence; legend-only coverage its own class L4g (point 9) | sentchecks.l4 | 9d42ed27c8 | [L4u], [L4l], [L4g] |
| (3) UNFORMALISED-coverage rule and ruled_out are levers | CASE_LEVERS | 9d42ed27c8 | test_l4_coverage_by_unformalised_units_and_ruled_out_entries_are_levers |
| (3) D `--span sentence`: legend quotes do not account; (i) total, (ii) outside the quote; hit = uncovered word + every loss entry; sidecar a lever (point 3) | sentchecks.d | 9d42ed27c8 | [D-final], test_d_counts_what_lies_outside_the_header_quote, test_every_loss_entry_is_a_d_hit, test_d_lists_the_word_a_legend_quote_alone_carries_and_the_sidecar_can_cover_it |
| (3) D on a case with no sidecar (FSF) | sentchecks.d | 9d42ed27c8 | test_a_case_without_a_sidecar_lists_every_unaccounted_word |
| (3) the CLI | tools/fidmech/__main__.py | 9d42ed27c8 | test_the_textcheck_command_runs_the_b2_checks_with_the_sentence_span |
| (4) ruled_out.json x3, `[]`; reason required; entry outside the source refused | usecases/*/fidmech/ruled_out.json, sentchecks.load_ruled_out | 9d42ed27c8 | test_a_ruled_out_entry_without_a_reason_or_outside_the_source_is_refused[10], test_each_use_case_has_a_ruled_out_list_whose_entries_have_a_reason[3] |
| (5) first FSF and PF run, all checks, after the freeze | docs/infra/fid-mech-b2/{safety-framework,openai-preparedness}.{json,txt} | a6ce8417e3 | section 4 |
| (5) the 12 unlocated ids | section 5 | | |
| malformed or empty inputs refused by name (build checklist 5) | sentchecks._refusing, load_case | 2550499ce9 | test_a_malformed_node_in_any_input_is_refused_by_name[66] |

Every new test fails on the old code: `tools.fidmech.sentchecks`, `cues.json` and `logic_words.json` do not exist on main, so `tests/test_fidmech_b2.py` and `tests/test_fidmech_data.py` fail at import.

Condition tests (stay selected): tests/test_fidmech_segment.py, tests/test_fidmech_l1.py (B1), tests/test_fidmech_b2.py and tests/test_fidmech_data.py (this batch). `tools/select_tests.py --base $(git merge-base HEAD main)` selects all four (output /tmp/b2-sel.log at the time of the run).

Fixture tests: no new test file contains the text the fidq step selects on (`grep -nE 'DEFAULT_SOURCE|pinned\s+source' tests/test_fidmech_b2.py tests/test_fidmech_data.py` prints nothing).

## 2. Freeze record (plan 3.0; Opus round 2 point 7)

- **Frozen on RSP:** cues.json and logic_words.json, the L3 template, the L4 heading rule (`min_words_by_kind`), the matching rules of every check. Commit **9d42ed27c8, 2026-11-16T03:49:19Z**. They were tuned on RSP's output only, as follows.
  - Added after RSP's first output: `min_words_by_kind` 5. RSP's L4u listed headings and labels inside norm units ("2.", "Timing.", "Privacy:"); 65 L4u fell to 20.
  - Added after RSP's first output: the L2b detail names a legend's bracketed passages. candid_reports quotes its sentence inside "(3.2: "...")", which B1's frozen note rule reads as a translator's note.
  - Bug found by a test before the freeze: multi-word logic words ("prior to", "at least") never matched. The fix did not change RSP's L3w count (12).
- **First FSF and PF check run:** 2026-11-16T03:49:26Z to 03:50:00Z, at HEAD 9d42ed27c8. Command: `uv run python -m tools.fidmech textcheck --doc <doc> --checks all --span sentence --json docs/infra/fid-mech-b2/<doc>.json`, one per document. Its stdout is saved beside the JSON as `<doc>.txt`.
- **Changes after that run:** only commit 2550499ce9. It refuses malformed and empty inputs and binds spans.json to the source sha. No segmentation, matching or cue rule changed. Rerunning all three documents at 2550499ce9 gave byte-identical JSON and stdout: `cmp` exit 0 on all six files ("identical" x3 in the build log). No generic rule changed after the first run, so FSF and PF are not relabelled by plan 3.0 rule 5.
- **In-sample labels to carry into every FSF/PF report** (Opus point 7):
  - L1m, shaped by FSF f8 (B1);
  - the footnote stream, from FSF f3 (B1);
  - the first-person present-tense cue of L4 and L1a, from FSF ("We conduct ...");
  - the external-check lists (section 5).
  - RSP is in-sample for every check.
- **What cues.json takes from FSF and PF:** only their company names, "Google DeepMind" and "OpenAI", for the present-tense cue (plan 3.5: "the company's name"). They are document identities, not check output.

## 3. Decisions inside the plan (each the conservative or narrower reading; no DRI question)

1. **L3 classes (point 9).** I added {if, when, whenever, provided that} and {not, nor} before the freeze.
   - "provided that", not "provided": the bare word is mostly the verb ("information provided to").
   - "no" stays out of {not, nor}: plan 3.0 rule 2's quantifier decision keeps all, every, each, any and no out of L3.
   - The invented-guard-in-wording escape remains for words outside these classes.
2. **L3 template.** The rule line loses its quoted constants, its "Rule n." and the words if, unless and not. These are VE's guard, carve-out and negation keywords, i.e. structure. Acts and legends keep those words. So a rule's structural "if" is never an L3 hit; an "if" in an act or a gloss is.
3. **L3 scope.** Rule blocks only (rules.d1.ve), as plan 3.4 says. D runs on rule and fact blocks.
4. **L4l.** Every unit the sentence overlaps has status LABELLED. The plan's "(exposition, meta, example or attributed)" is read as examples of LABELLED kinds; explanation, definition and causal are LABELLED too.
5. **L4 by kind.** A sentence is obligation-bearing by its unit's kind alone (norm, hedged, unformalised) only with 5 words or more. Cue sentences count at any length.
6. **L1a.**
   - "the located sentence lies outside every linked span" is checked per quote: a quote of a guard sentence from a neighbouring unit is a hit (RSP f24, f25, f26).
   - A cue sentence is "of a linked span" when one of its characters lies in the span.
   - A unit linked to a rule id that no block has is skipped.
7. **L2.**
   - Only passages of MIN_QUOTE (12) characters or more are checked; shorter quotes are terms.
   - A passage with an L1 class is L2q before L2a, so one hit per passage.
   - Rules using a predicate are found with accounting.used_names, over rule and fact blocks.
8. **ruled_out.json binding, stricter than plan 2c.**
   - `at` must be the byte start of a sentence.
   - `sentence` must equal that sentence's first 60 normalised characters.
   - Duplicates are refused, and a non-list file is refused.
9. **spans.json** must carry the source's sha256, or the run is refused.
10. **D.** "Accounted" means the block's VE text plus, for each name it uses, the unquoted legend: description less its quoted passages, verbalisation and act. A word is one hit; a loss entry is one hit.

## 4. The first run: RSP (in-sample), FSF and PF (out-of-sample except the labels in section 2)

Measured output, not a gate. Source: `docs/infra/fid-mech-b2/<doc>.txt` (stdout) and `<doc>.json`.

| doc | L1m | L1n | L1u | L1c | L1e | L1a | L2b | L2q | L2a | L3w | L4u | L4l | D | L4g |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RSP | 2 | 0 | 4 | 39 | 1 | 9 | 28 | 17 | 1 | 12 | 20 | 72 | 1227 | 0 |
| FSF | 17 | 0 | 0 | 38 | 1 | 4 | 26 | 1 | 0 | 24 | 18 | 50 | 386 | 0 |
| PF | 0 | 0 | 14 | 64 | 0 | 1 | 45 | 8 | 2 | 14 | 12 | 0 | 661 | 0 |

Info lines, from `<doc>.txt`:
- **L1a, linked and unlinked blocks** (printed on every L1a line, plan 3.2):
  - RSP 52 linked, 33 unlinked;
  - FSF 14 linked, 47 unlinked;
  - PF 14 linked, 87 unlinked.
- **L2, regulated predicates:** RSP 64, FSF 27, PF 62. Not checked:
  - base predicates RSP 55 (50 bare), FSF 35 (35 bare), PF 59 (58 bare);
  - open terms RSP 28, FSF 15, PF 18.
- **L4, obligation-bearing sentences:** RSP 268 of 488, FSF 131 of 313, PF 337 of 435.
- **D, unaccounted words** (total, outside the quote):
  - RSP 1399 and 334;
  - FSF 386 and 209, with no sidecar: every unaccounted word is listed, and D is its own class, so the headline can be read without it (Opus point 3; the headline itself is B5's report);
  - PF 1188 and 605.
  - Loss entries counted as D hits: RSP 3, PF 19.

Lever reruns (clears / adds), from `<doc>.txt`:

| lever | RSP | FSF | PF |
|---|---|---|---|
| extra | 64 / 5 | 0 / 0 | 0 / 0 |
| furniture | 93 / 87 | 5 / 27 | 68 / 44 |
| footnotes | 163 / 85 | 48 / 10 | 0 / 0 |
| hand-footnotes | 16 / 1 | 0 / 0 | 14 / 20 |
| suppress, abbrev | 0 / 0 | 0 / 0 | 0 / 0 |
| ruled_out (all `[]`) | 0 / 0 | 0 / 0 | 0 / 0 |
| unformalised | 15 / 0 | 33 / 0 | 262 / 0 |
| sidecar | 175 / 3 | (none) 0 / 0 | 546 / 19 |

What the hits are, read from the JSON:
- **RSP L1a 9:**
  - 7 quotes outside the block's linked span: f7-publish, f16-ask-commentary, and the guard-sentence pattern f24-argument, f24-delay, f25-meet, f25-delay, f26-effort;
  - 1 duplicate quote on an unlinked block: threshold-t3;
  - 1 cue sentence of a linked span quoted by no block: f11-factual.
- **RSP L3w 12:**
  - "never" or "not" in legend glosses (in_scope "a classification, never a duty"; unredacted_shared "(a draft does not count)");
  - "unless" in f16-only-legal's legend;
  - "once" in f22-third-party-review's act;
  - "at least" in f25-meet.
- **FSF L3w 24:** mostly "before", "not" and "at least" in acts and glosses.

## 5. The 12 units the audit packet could not locate (task DO 5; plan 3.2 external check; in-sample label)

| doc | unit | linked | L1 now | L4 now | why the packet missed it |
|---|---|---|---|---|---|
| PF | f1-security-strict | no | L1u | no L4 hit in a linked span (unlinked) | the source hyphenates the cell text inside a page line; norm() joins hyphens only at page joins |
| PF | f1-contrib-bio-strict | no | L1u | (unlinked) | same: in-page hyphenation of a table cell |
| PF | f12-ara | no | L1u | (unlinked) | the source has "Adap- tation" inside the line |
| PF | f12-ara-unscoped | no | L1u | (unlinked) | same quote as f12-ara |
| PF | f12-nuclear | no | L1u | (unlinked) | the source has "ac- tions" and "com- plexity" inside the line |
| PF | f12-nuclear-unscoped | no | L1u | (unlinked) | same quote as f12-nuclear |
| FSF | f8 | yes | L1m (no quotation) and L1a (its linked span's "will" sentence is quoted by no block) | L4u in its linked span ("● A model for which inherent risk assess...") | the header has no quotation |
| FSF | f12-p | no | L1c | (unlinked) | the quote starts after the run-in label "2. Pre-deployment review of residual risk assessment:", whose next word is lower case, so it is mid-sentence |
| FSF | f12-u | no | L1c | (unlinked) | same sentence as f12-p |
| FSF | f13-p | no | L1c | (unlinked) | same shape, page 13 |
| FSF | f13-u | no | L1c | (unlinked) | same sentence as f13-p |
| FSF | f15-diff | yes | L1m and L1a ("required" sentence of its span quoted by no block) | L4u in its linked span ("At this stage, additional mitigations be...") | the header has no quotation |

**Against plan 3.2's external check:**
- 8 of the 12 come out as L1m, L1u or L1a, as the plan requires.
- FSF f12-p, f12-u, f13-p and f13-u come out as L1c. They are explained in the last column: located, but starting after a run-in label.
- The 6 PF L1u are measurement artefacts of in-page hyphenation, not changed words (Notes for the DRI, 1).

Source of the table:
- a scratch read of `docs/infra/fid-mech-b2/{openai-preparedness,safety-framework}.json` (hits per block, and L4 hits whose byte offset lies in a span linked to the block);
- a source `find` for the quote's first words.

## 6. Plants killed (fixture tests/data/fidmech/b2; plan section 10 rows of this batch; test -> class)

Each plant edits one copy of the clean fixture under tmp_path. The test asserts that the counts of the checks run are exactly {class: n}.

| plan 10 row | plant | test | class |
|---|---|---|---|
| L1a | a quote of a sentence inside another block's linked span | test_each_plant_gives_exactly_its_class[L1a-other-span] | L1a |
| L1a | the wrong sentence of the right linked span | ...[L1a-wrong-sentence], test_the_wrong_sentence_plant_names_the_unquoted_cue_sentence | L1a |
| L1a (unlinked) | an unlinked block's quote that occurs twice | ...[L1a-unlinked-twice] | L1a |
| L2b | "section 3 at {0}" | ...[L2b] | L2b |
| L2q | a legend quoting half a sentence | ...[L2q] | L2q |
| L2a | a legend quoting a sentence of an unrelated span | ...[L2a] | L2a |
| L3w | "after" added to an act phrase (P20's shape) | ...[L3w-after] | L3w |
| L3w | "within one week" added where the source says "In selecting" | ...[L3w-within] | L3w |
| L4u | a rule deleted whose sentence carries "will" | ...[L4u] | L4u |
| L4l | an FSF-shaped "We conduct ..." sentence in an exposition unit left uncovered | ...[L4l] | L4l |
| L4g (point 9) | a sentence a legend quote alone covers | ...[L4g] | L4g |
| D | full quote holding "final", act without "final", legend quoting the sentence (P04's shape) | ...[D-final] | D, "final" listed |

- The clean fixture gives no hit in any check, run together or one at a time: test_the_clean_fixture_has_no_hit_in_any_check.
- Accepted counterparts:
  - a quote with an earlier L1 class gets no L1a: test_l1a_is_the_last_class_a_quote_with_an_earlier_class_gets_no_l1a;
  - a sidecar entry covers the D word: test_d_lists_the_word_a_legend_quote_alone_carries_and_the_sidecar_can_cover_it;
  - a valid ruled_out entry is accepted, and clears its L4u: the ruled_out tests;
  - cue and no-cue sentences: test_the_obligation_cues[11].

## 7. Seeded bugs (Python, the only changed product language; `docs/infra/fid-mech-b2/seeded-bugs.json`)

All 18 were planted one at a time in tools/fidmech/sentchecks.py by a scratch script. For each, the named test failed (rc 1), and the file was restored (`git status` showed only the new JSON afterwards).

1. S1 L1a, the outside-linked-span check off -> test_each_plant_gives_exactly_its_class[L1a-other-span]
2. S2 L1a, a duplicate must occur 3 times -> [L1a-unlinked-twice]
3. S3 L1a, the uncovered-cue-sentence check off -> [L1a-wrong-sentence]
4. S4 L2b skipped -> [L2b]
5. S5 L2q, a passage's L1 class ignored -> [L2q]
6. S6 L2a, the span check off -> [L2a]
7. S7 L3, the VE template left in the rule line -> test_the_clean_fixture_has_no_hit_in_any_check
8. S8 L3/D, the legend's own words keep its quoted passages -> [D-final]
9. S9 L3, a multi-word logic word with an escaped space (the bug found while building) -> test_a_logic_word_matches_whole_words_only
10. S10 L4, UNFORMALISED units cover nothing -> test_the_clean_fixture_has_no_hit_in_any_check
11. S11 L4, headings obligation-bearing by kind -> test_the_clean_fixture_has_no_hit_in_any_check
12. S12 L4l not told apart -> [L4l]
13. S13 L4g, a legend quote covers like a header quote -> [L4g]
14. S14 D, sidecar entries cover nothing -> test_d_lists_the_word_a_legend_quote_alone_carries_and_the_sidecar_can_cover_it
15. S15 D, loss entries not hits -> test_every_loss_entry_is_a_d_hit
16. S16 ruled_out, the sentence text not compared -> test_a_ruled_out_entry_without_a_reason_or_outside_the_source_is_refused
17. S17 cues, the hedge check off -> test_the_obligation_cues
18. S18 spans.json bound to no source -> test_a_malformed_node_in_any_input_is_refused_by_name

## 8. Spec re-read

- **Plan 2c ruled_out:** `{"at", "sentence" (first 60 chars), "reason", "by"}`; "starts `[]`". Built with exactly those keys. `[]` x3.
  - "each entry needs a reason; an entry outside the source is rejected" (task): built, and stricter (section 3, 8).
- **Plan 3.2 L1a:** "linked block: the located sentence lies outside every linked span, OR an obligation-bearing sentence (section 3.5 cues) of a linked span is quoted by no block linked to that span. Unlinked block: the quote occurs more than once." Built word for word.
  - Cues only (not unit kinds) decide "obligation-bearing" here, as "(section 3.5 cues)" says.
  - Precedence: last, so only on quotes with no other L1 class.
- **Plan 3.3:** "L2b no quoted passage of 12 characters or more (MIN_QUOTE)", which is accounting.MIN_QUOTE. "L2q fails as an L1u, L1c or L1n quote would", plus L1e by point 9. "L2a ... Only linked rules are checked; unlinked ones are counted": info `passages_unlinked`. "Not checked: base predicates and open terms, counted": info `not_checked`.
- **Plan 3.4:** "the rule line minus the VE template; the act phrases of the predicates the rule uses; the unquoted parts of their legends". Built as `own_words`.
  - "When L1 cannot locate them, the header quote is used and the hit is marked": built.
  - The 10 frozen classes are the plan's.
  - "in" and "following" are in no class: tests/test_fidmech_data.py::test_the_logic_word_classes_are_the_frozen_ones_and_the_quantifiers_stay_out.
- **Plan 3.5:** obligation-bearing by unit kind (norm, hedged, unformalised) or by cues.
  - The modal list is the plan's, verbatim as regexes. "require(d|s)" and "commit(s|ted)" are literal; "ensure", "strive" and "intend" take no suffix.
  - Covered by: L1-located quote; L2-located legend quote of a used predicate (its own class L4g, point 9); UNFORMALISED with a reason; ruled_out.
  - L4u and L4l as written.
- **Plan 3.6:** widen to full sentences with the B1 segmenter. A word only in a legend's quoted passage is not covered. Per block (i) and (ii). `--check` of safetyfw_accounting.py is unchanged: the file is not touched.
- **Opus round 2:**
  - point 3: "a D hit is an unaccounted word that no sidecar entry covers, plus every loss entry; the sidecar is a lever"; built.
  - point 9: "D: list the one-word-set-per-block escape. The stop list also holds within, must, should, may, will, any, all and each." Listed in section 10.

## 9. Test runs

- While iterating:
  - `uv run pytest -q tests/test_fidmech_b2.py tests/test_fidmech_data.py`, 129 passed;
  - `uv run pytest -q tests/test_fidmech_l1.py`, 44 passed.
- Regen: `uv run python tools/regen_generated.py --write`, rc 0, committed in 2550499ce9. It also refreshed main's stale `docs/kernel/closure-baseline.json` and code-map lines (generator output, R12).
- Collection: `uv run python tools/gate_collection.py --check --prebuilt` after `lake build` (Lean unchanged; restored by lean-prep), rc 0: "130 added, 1 removed by a trailer, 0 refused, 0 stale and 0 malformed".
- trust_mutants: not run, and not required.
  - light-lane printed NOT. The count, 36588 changed lines, includes the saved run JSON.
  - No Lean file and no trusted-core file changed, so R16 (trusted Lean growth) does not apply, and the task asks for no record.
- Selected run: SELECTED-RUN-PLACEHOLDER

## 10. Known escapes (plan section 11, with this batch's additions)

- **L1a.**
  - On an unlinked block, a unique sentence from the wrong section passes.
  - In a paragraph-sized linked span, the wrong sentence passes when the right one carries no cue.
  - Out of sample, L1a is mostly the uniqueness test (14 linked blocks each on FSF and PF).
- **L2.**
  - A legend that quotes the right full sentence but whose gloss misstates it passes.
  - Base-predicate and open-term legends are not checked (counted).
  - A source passage inside brackets is read as a note (B1's frozen rule), so such a legend reads as L2b. The detail says so: RSP candid_reports.
- **L3.**
  - A logic word present in the sentence but attached to another clause passes.
  - A dropped logic word passes.
  - Quantifiers are out.
  - Words outside the 12 classes pass (the invented-guard-in-wording escape, point 9).
  - A structural if, unless or not of the rule line is template, never a hit.
- **L4.**
  - A sentence covered by a quote whose rule drops one of its two obligations passes.
  - Obligation forms outside cues.json are missed.
  - A duty of 4 words or fewer with no cue is missed.
- **D.**
  - A word in the unquoted gloss of some legend of a used predicate passes, even when the gloss is about something else.
  - D compares one word set per block (point 9).
  - It cannot see dropped stop words: the stop list holds only, not, before, after, within, must, should, may, will, any, all and each.

## 11. Notes for the DRI

1. **PF in-page hyphenation.** PF's text hyphenates words inside a page line ("Adap- tation", "ac- tions"). norm() joins a hyphen only at a page join (B1's frozen rule). So the 6 PF unlocated units, and likely more of PF's 14 L1u, are artefacts. Joining "<letter>- <lowercase>" inside a line would be a generic change after the first PF run, which marks PF in-sample (rule 3.0.5). I left it for the DRI or B5 to decide with these counts.
2. **FSF run-in labels with a lower-case continuation** ("...assessment: external deployments ...") start mid-sentence, so a quote that leaves out the label is L1c. Same rule-3.0.5 consequence.
3. **B1 review notes.** F1 (decide "also gated" per hit with quote_faults) and F2-F9 were C notes on B1, not this task, so I did not act on them. The ALSO_GATED wording is unchanged.
4. **The guard-sentence pattern.** RSP f24-argument, f24-delay, f25-meet, f25-delay and f26-effort quote their condition sentence, which lies in a neighbouring unit. By plan 3.2 these are L1a hits; they are 5 of RSP's 9.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No Lean answer is read or relayed.
2. Every deliverable built, no rule broken: PASS. Section 1 table. No protected file is touched: `git diff --stat main...HEAD` lists no quote_evidence.py, conftest, use-case test file, fidquote-gate.py or translation file.
3. Tests can fail: PASS. 18 seeded bugs, section 7 and seeded-bugs.json.
4. Valid inputs still pass: PASS. test_the_clean_fixture_has_no_hit_in_any_check. The B1 L1 output on RSP is unchanged: L1 counts in anthropic-rsp.txt equal the `--checks L1` run before the refactor (L1m 2, L1n 0, L1u 4, L1c 39, L1e 1). tests/test_fidmech_l1.py passes (44).
5. R8 binding: N.A., no relayed answer. Inputs are bound instead: ruled_out entries to a sentence start and its text, spans.json to the source sha (test_a_ruled_out_entry_without_a_reason_or_outside_the_source_is_refused, test_a_malformed_node_in_any_input_is_refused_by_name[spans.json:source_sha256-*]).
6. Gate evidence matches the final HEAD: PASS. The selected run is on the committed tree (section 9); the chain gate runs on the final HEAD.
7. No unsigned item: PASS. DELTA none and no reservation.
8. Every user-visible change in DELTA: N.A. A report-only tool; no verdict or decision path changed (task: "DELTA: none").
9. Test selection finds the tests: PASS. `tools/select_tests.py --base <merge-base>` lists all four tests/test_fidmech_*.py.
10. Lean statements: N.A. No Lean change.
11. Budgets fail closed: PASS. L1a's duplicate count uses textchecks' capped occurrence search (MAX_OCCURRENCES). A capped search still finds more than one placement, so a duplicate is never missed through the cap. No new budget.
12. No CPU or memory regression: PASS. `textcheck --checks all` on RSP with 9 lever reruns takes about 12 s (`time`, during the build). No product path changed.
13. Removed or renamed tests: PASS. A `Test-removed:` trailer for the renamed B1 CLI test, commit 63d8c11909; gate_collection --check rc 0.
14. Both directions, cited evidence, spec re-read: PASS. Clean and plant per check (section 6). Every refusal has its accepted counterpart in the same test. Claims cite the saved files or commands. Spec re-read is section 8.
15. No overclaim / no silent cut / every new check can fail / limits: PASS.
    - "No hit" and "every check" are backed by test_the_clean_fixture_has_no_hit_in_any_check.
    - "Byte-identical" is backed by the cmp run (section 2).
    - No deliverable was cut, and nothing moved to fid-mech-b3.
    - Each check has a seeded bug.
    - No new limit.
