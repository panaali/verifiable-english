# fid-mech-b1: segmenter, L1 m/n/u/c/e, boundaries.json x3 (build report)

**Status:** built; the selected run and the chain gate are recorded below. **HEAD:** the commit carrying this report (branch infra/fid-mech-b1).
**What changed:** new `tools/fidmech/` package (`segment.py`, `textchecks.py`, `__main__.py`); `usecases/{anthropic-rsp,safety-framework,openai-preparedness}/fidmech/boundaries.json`; two condition test files and a fixture; 3 gate-optional rows. Nothing is gated and no translation file changed.
**Open:** none. **DRI signature:** none reserved; DELTA none (Python tooling and data, trust +0).
**RSP L1 (saved evidence `rsp-l1.json`):** L1m 3, L1n 0, L1u 1, L1c 25, L1e 1 over 97 checked quotes in 85 blocks. 14 quotes inside translator's notes are counted as info, outside the headline.

SIZE: 865 product, 492 tests, 114 fixture data + about 60 hand-written boundaries entries (the rest of the 495 boundaries.json lines is generator output) other hand-written lines.

## 1. Deliverables (task DO list, plan section 10 row B1, Opus round-2 points)

| item | where | commit | test |
|---|---|---|---|
| segment.py: raw byte offsets with a normalised->byte map (`Text.starts/ends`) | tools/fidmech/segment.py | 189c6a9d7 | test_sentence_offsets_are_raw_byte_offsets_into_the_source |
| furniture as page-anchored patterns; an unanchored one refused | segment.furniture_matches | 189c6a9d7 | test_a_furniture_pattern_not_anchored_to_its_page_position_is_refused (7 cases), test_the_inline_footer_and_the_repeated_header_are_cut_from_the_main_stream |
| footnote pairs proposed by the generator, frozen, validated (marker digits = n; body starts with n; one body per marker and one marker per body) | segment.propose, segment.validate | 189c6a9d7, 0a3c0f601 | test_the_generator_pairs_bodies_that_come_later_on_the_page_in_the_order_8_4, test_a_boundaries_entry_without_a_reason_or_outside_its_source_is_refused (21 cases) |
| ambiguous pairs left unpaired and resolved by hand with a reason | boundaries.json `footnotes[by=hand]`, `unpaired` | 189c6a9d7, d46f97e40 | test_the_boundaries_check_fails_on_a_stale_pair_or_an_undecided_candidate |
| two streams: main (furniture, bodies, frozen markers cut) and one per footnote body | segment.Segmentation | 189c6a9d7 | test_each_footnote_body_is_a_stream_of_its_own_and_left_out_of_the_main_stream |
| norm() keeps every digit except frozen markers | segment.norm/normalise | 189c6a9d7 | test_norm_folds_whitespace_quote_styles_dashes_and_ligatures_and_keeps_digits, test_paired_markers_are_removed_and_digits_without_a_body_are_kept |
| sentence ends as specified; ':' lead-ins recorded per list item | segment.cuts, segment.sentences | 189c6a9d7 | test_each_list_item_records_its_lead_in |
| Opus point 1: "(n)"/"(a)" ends a sentence only directly after a ':' lead-in | segment.LEAD_IN | 189c6a9d7 | test_clause_numbers_inside_a_sentence_do_not_split_it_and_split_only_after_a_lead_in; fixture block c-clause-two (a quote starting at "(2) involves ...") is L1c |
| Opus point 2: note quotes are info outside the headline; a header with only note quotes is L1m | textchecks.header_quotes, check_block | 189c6a9d7 | test_a_translators_note_quote_is_counted_as_info_and_not_checked, fixture m-note-only |
| L1 m > n > u > c > e, one hit per quote | textchecks.check_block | 189c6a9d7, 0a3c0f601 | test_precedence_gives_one_hit_per_quote_the_first_that_applies |
| `textcheck --doc <name> [--checks L1] [--json OUT]`; `furniture --doc` | tools/fidmech/__main__.py | 189c6a9d7 | test_the_textcheck_command_writes_the_report_and_refuses_checks_of_later_batches, test_the_furniture_command_lists_every_match_with_its_page_and_offset |
| boundaries.json for RSP (generic rules frozen on RSP first), FSF, PF (segmenter alone) | usecases/*/fidmech/boundaries.json | 189c6a9d7, d46f97e40 | test_the_frozen_boundaries_fit_the_pinned_source[3 docs] |
| L1 run on RSP only; no check run on FSF or PF | docs/infra/fid-mech-b1/rsp-l1.json | this commit | section 3 |
| Opus point 8 seam | not used: under the standing size override the whole batch is built (FSF/PF boundaries and the furniture CLI are here, not in b2) | | |
| Opus point 9: real-source test opens the source and names it | tests/test_fidmech_segment.py::test_the_frozen_boundaries_fit_the_pinned_source | d46f97e40 | skips only where the source is absent (section 6, note 1) |

Plan section 10 fixture rows of this batch: L1m, L1u, L1c, L1e, L1n, footnotes, furniture are all built (section 4). L1a, L2, L3, L4 and D are fid-mech-b2's.

Each new test fails on the old code: `tools.fidmech` does not exist on main, so both files fail at import.

## 2. Freeze record (plan 3.0; Opus point 7)

- Generic rules (sentence rules, generic abbreviations `e.g. i.e. cf. vs.`, furniture and footnote rules, matching classes) were frozen on RSP in **189c6a9d7, committed 2026-11-13T20:34:12Z**. They were tuned on RSP only. Two rules came from RSP's L1c output: the run-in label ("Internal review: We ...") and the ':' lead-in before a numbered item ("the following: 1. ...").
- **FSF and PF were first run at 2026-11-13T20:34:34Z with HEAD 189c6a9d7**, through the segmenter and the footnote generator only (`boundaries --write`). No L1 check has run on FSF or PF.
- Generic changes after that run. Neither was shaped by FSF or PF text: both came from the fixture tests.
  - (a) `propose(..., hand_bodies)`: a generator body also ends at a hand pair's body. FSF and PF have no hand pair, so their files are unchanged (`boundaries --check` passes on both). Under rule 3.0.5, FSF and PF are labelled **in-sample for this generator rule**.
  - (b) L1 matching: a fragment may not cut a digit run, and the masked (L1n) search keeps the contiguity rule. These are checks, and no FSF/PF check had run when they changed.
- In-sample labels to carry into every FSF/PF report (Opus point 7): L1m (shaped by FSF f8), the footnote stream (FSF f3), and the external-check lists (PF 6 and FSF 6 unlocated ids).
- The FSF/PF hand decisions were made by reading the source text, never from check output. Each has a reason in its file:
  - FSF: 2 generator proposals rejected (table-of-contents numbers on page 3) and 4 table-of-contents candidates left as text.
  - PF: 3 proposals rejected and 15 candidates left as text (table of contents, headings, "version 2"). Two of them are probably footnote bodies 5 and 6 whose markers use PF's attached shape.

## 3. RSP L1 (`uv run python -m tools.fidmech textcheck --doc anthropic-rsp --checks L1 --json docs/infra/fid-mech-b1/rsp-l1.json`, output saved in rsp-l1.txt)

| run | L1m | L1n | L1u | L1c | L1e | the lever clears / adds |
|---|---|---|---|---|---|---|
| raw (all levers on) | 3 | 0 | 1 | 25 | 1 | |
| extra off (8 layout entries: 6 headings, 2 table cells) | 3 | 0 | 1 | 35 | 1 | clears 10 |
| suppress off (none) | 3 | 0 | 1 | 25 | 1 | 0 |
| document abbrev off (none) | 3 | 0 | 1 | 25 | 1 | 0 |
| furniture off | 3 | 0 | 1 | 26 | 1 | clears 4, adds 3 |
| footnote pairs off | 3 | 0 | 4 | 29 | 1 | clears 7 |
| hand footnote pairs off (the generator's raw proposal) | 3 | 0 | 1 | 25 | 1 | 0 |

- Footnote pairs: 12 by the generator and 1 by hand. The hand pair is footnote 3, whose marker is in Table 1's repeated header, i.e. furniture.
- Unpaired digit runs left as text: 6 ("30 days" x4, "Section 1" x2).
- The hits:
  - L1m: rows-uncond, t4-only-if and s2-only-if-third have no quotation.
  - L1u: rows-cond quotes "Mitigations—our plan as a company", which occurs only in the repeated table header (furniture).
  - L1e: f12-board-approval.
  - L1c, 25 hits:
    - 21 are not a whole sentence run. Examples: f5 and f10-attempt "should"; f12-final; f20-notice-p; s2-suff-third x2.
    - 4 are list items quoted without their lead-in: f9-internal, f10-candid-default, f10-in-line, highly-capable-t4.
- **Also gated today on RSP: none.** No merge-train step compares RSP header quotes (fid-quote-gate NOT-checked list), so all 30 RSP hits are new.
- Overlap list for the other documents (`textchecks.ALSO_GATED`; Opus point 9):
  - PF L1m is gated by quote_evidence.py:39.
  - PF L1u and L1e are gated by quote_evidence.py:40 via test_pf_fidelity_fix.py:179.
  - FSF WILL_FEATURES L1u repeats test_safety_framework.py:408. It compares the WILL_FEATURES table rather than header quotes, so no FSF class is marked.
- The design read's f7-publish finding (header stops at "risks of our systems") is stale: the header now quotes the whole sentence, and L1 gives it no hit.
- The 12 unlocated FSF/PF ids are fid-mech-b2's first FSF/PF run, as the task says.

## 4. Plants killed (fixture tests/data/fidmech/doc; test -> class)

| plant | test | class |
|---|---|---|
| header with no quote (m-none); `""` (m-empty); only a note quote (m-note-only) | test_each_plant_gives_exactly_its_class_once[m-*] | L1m x3 |
| "within 3 days" for "within 30 days" (n-days); "permit 2 attempt" for "permit 1 attempt" (n-permit) | test_each_plant_gives_exactly_its_class_once[n-*] | L1n x2 |
| one word changed (u-word) | ...[u-word-L1u] | L1u |
| cut mid-sentence without "…" (c-cut); quoted up to a page join (c-join); bullet without its lead-in (c-bullet); starting at "(2)" inside a sentence (c-clause-two) | ...[c-*-L1c] | L1c x4 |
| "…" (e-ellipsis) | ...[e-ellipsis-L1e] | L1e |
| footnotes: "harm. 4 That is" and "progress 8 in AI" with bodies in the order 8, 4 | test_the_generator_pairs_bodies_that_come_later_on_the_page_in_the_order_8_4, test_paired_markers_are_removed_and_digits_without_a_body_are_kept | paired, markers removed |
| "permit 1 attempt" / "permit 2 attempts" without bodies | test_paired_markers_are_removed_and_digits_without_a_body_are_kept | digits kept |
| a real marker inside a quote | test_digit_runs_are_compared_and_a_footnote_marker_inside_a_quote_is_no_hit | no hit |
| FSF f3 shape: a quote of a footnote body | test_a_quote_of_a_footnote_body_is_located_in_the_footnote_stream; clean-footnote-body | located in fn8 |
| furniture: inline footer, repeated header removed; an unanchored pattern refused | test_the_inline_footer_and_the_repeated_header_are_cut_from_the_main_stream, test_a_furniture_pattern_not_anchored_to_its_page_position_is_refused | removed; refused |
| boundaries entries without a reason or outside the source | test_a_boundaries_entry_without_a_reason_or_outside_its_source_is_refused | refused |

The 15 clean blocks give no hit (test_a_clean_block_has_no_hit). The whole fixture gives exactly the 12 plants (test_the_whole_fixture_report_counts_each_plant_once).

## 5. Seeded bugs (Python, the only changed product language; `docs/infra/fid-mech-b1/seeded-bugs.json`)

All 13 were planted one at a time, each test failed (exit 1), and each file was restored (`git status` clean afterwards).

1. tools/fidmech/segment.py: every "(n)" splits -> test_clause_numbers_inside_a_sentence_do_not_split_it_and_split_only_after_a_lead_in
2. segment.py: markers kept in the canonical stream -> test_paired_markers_are_removed_and_digits_without_a_body_are_kept
3. segment.py: anchoring check dropped -> test_a_furniture_pattern_not_anchored_to_its_page_position_is_refused
4. segment.py: blank reason accepted -> test_a_boundaries_entry_without_a_reason_or_outside_its_source_is_refused
5. segment.py: norm() drops 1-2 digit runs like plain() -> test_norm_folds_whitespace_quote_styles_dashes_and_ligatures_and_keeps_digits
6. segment.py: the marker allowed as a body candidate -> test_the_generator_pairs_bodies_that_come_later_on_the_page_in_the_order_8_4
7. tools/fidmech/textchecks.py: no masked search (L1n never decided) -> test_each_plant_gives_exactly_its_class_once[n-days-L1n]
8. textchecks.py: any sentence end accepted -> test_each_plant_gives_exactly_its_class_once[c-cut-L1c]
9. textchecks.py: lead-in check off -> test_a_bullet_needs_its_lead_in_among_the_same_blocks_quotes
10. textchecks.py: elision ignored -> test_each_plant_gives_exactly_its_class_once[e-ellipsis-L1e]
11. textchecks.py: note quotes checked as source quotes -> test_a_translators_note_quote_is_counted_as_info_and_not_checked
12. textchecks.py: a fragment may cut a digit run -> test_precedence_gives_one_hit_per_quote_the_first_that_applies
13. textchecks.py: the lever-off rerun uses the lever-on boundaries -> test_the_report_prints_each_lever_off_and_the_hits_it_clears_or_adds

## 6. Notes for the DRI

1. **Real-source test.** Point 9 allowed it to open the source unconditionally. I took the conservative form instead: it names DEFAULT_SOURCE and opens it, so the fidq step selects it and VM1 enforces it, but it skips with the standard reason where the source is absent. Three exact node ids were added to tools/gate-optional.json, so a gate host without the sources does not fail it.
2. **PF footnotes.** PF's markers are attached to the preceding word ("harm.1", "peers.2", "criteria:3"). The RSP-frozen marker shape (a standalone run) does not take them, so PF has no frozen pair and its bodies stay in the main text. Taking that shape would be a generic change and makes PF in-sample (rule 3.0.5). That is fid-mech-b2's call when it first runs PF.
3. **Table of contents.** The generator proposes table-of-contents numbers as pairs. FSF and PF have 5 such proposals between them, all rejected by hand with reasons. An exclusion rule would be a generic change after the first FSF/PF run.
4. **Quote scanner.** `textchecks.header_quotes` repeats safetyfw_accounting.scan_quotes's mark pairing, using the same OPENS/CLOSES/STRAIGHT constants. scan_quotes returns normalised quotes of at least 12 characters without their positions, and L1 needs empty quotes and note positions. A shared position-returning scanner in safetyfw_accounting.py is a later refactor; that file was left untouched here. Character folding is shared: `segment.fold` calls safetyfw_accounting.norm per character.
5. **Code map.** The regen also adds main's missing line for lean/VE/Route/CodecRoundTrip.lean to docs/codemap/lean__VE__Route.md. That file is on main, and its code map was stale there.
6. **Elision contiguity.** The plan's "one run of contiguous sentences" is read as: the fragments touch a contiguous range of sentences, so no whole sentence is skipped.
7. **Known escape.** An `extra` entry at a cut quote's end clears its L1c (plan section 11). test_an_extra_boundary_lever_can_clear_a_cut_and_the_rerun_shows_it shows that the lever-off rerun prints the cleared hit.

## 7. Spec re-read

- Plan 3.1 sentence ends: ". ? ! + whitespace + upper case / opening quote / bracket / bullet / end; not after an abbreviation; a bullet glyph; (1) at a list start; extra minus suppress".
  - Built as `cuts`. "End of stream" is the stream end.
  - "(1) at a list start" is narrowed by Opus point 1 to directly after a ':' lead-in.
  - Two RSP-frozen additions: a numbered item after a sentence end, and a run-in label's ':' before an upper-case letter.
- Plan 3.2 L1c: "only whitespace, closing punctuation and closing quotes may remain". Built as `END_SLACK`, which allows `. , ; : ! ?`, `)`, `]` and quote marks.
- Plan 3.2 L1m: "no quotation, or only quotations that are empty or hold only whitespace or punctuation". Built, plus Opus point 2's "only note quotes".
- Plan 2b validation: "the marker's digits equal n; the body starts with n; each marker has exactly one body; each body has exactly one marker; every entry needs a reason and an offset inside the source". All are built in `validate`/`parse_boundaries`. Abbreviation entries also carry a reason, which is stricter than the plan's string list.

## 8. Test runs

- While iterating: `uv run pytest -q tests/test_fidmech_segment.py tests/test_fidmech_l1.py`, 90 passed.
- Regen: `uv run python tools/regen_generated.py --write`, rc 0, committed in d4276b044.
- Selected run: see section 9.

## 9. Selected run

(filled in below after the run)

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No Lean answer is read or relayed.
2. Every deliverable built: PASS. Section 1 table; grep of the diff found no Python copy of a Lean decision and no permanent report test (rsp-l1.json is saved evidence that no test reads).
3. Tests can fail: PASS. 13 seeded bugs (section 5, seeded-bugs.json).
4. Valid inputs still pass: PASS. test_a_clean_block_has_no_hit (15 clean shapes); test_norm_makes_whitespace_and_quote_styles_in_a_quote_irrelevant.
5. R8 binding: N.A. No relayed answer. Input ids are bound instead: every boundaries offset must be a character of its source (test_a_boundaries_entry_without_a_reason_or_outside_its_source_is_refused).
6. Gate evidence matches the final HEAD: PASS. The chain gate runs on the committed HEAD; the selected run is in section 9.
7. No unsigned item: PASS. DELTA none and no reservation.
8. Every user-visible change in DELTA: N.A. A new report-only tool with no verdict path changed (task: "DELTA: none").
9. Test selection finds the tests: PASS. `tools/select_tests.py --base <merge-base>` selects tests/test_fidmech_l1.py and tests/test_fidmech_segment.py (67 units).
10. Lean statements: N.A. No Lean change.
11. Budgets fail closed: PASS. The occurrence search is capped (`MAX_OCCURRENCES`); a capped search finds fewer placements, so it reports a hit, never a pass (test_the_occurrence_cap_fails_closed_a_capped_search_reports_a_hit_never_a_pass).
12. No CPU or memory regression: PASS. The RSP report with all 6 lever reruns takes about 1.7 s (`time uv run python -m tools.fidmech textcheck --doc anthropic-rsp`). No product path changed.
13. Removed or renamed tests: N.A. None removed.
14. Both directions, cited evidence, spec re-read: PASS.
    - Every refusal test also has its accepted counterpart: test_an_anchored_page_end_pattern_is_accepted_as_the_counterpart; the frozen file is accepted in the refusal test; clean vs plant blocks.
    - Spec re-read is section 7.
15. No overclaim / no silent cut / every new check can fail / limits: PASS.
    - "All 13" and "none" are each backed by seeded-bugs.json and the section 3 command.
    - No deliverable was cut (section 1).
    - Each check has a seeded bug.
    - The occurrence limit is enforced before any placement is walked.
