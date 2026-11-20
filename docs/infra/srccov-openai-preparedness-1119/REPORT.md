# srccov-openai-preparedness-1119: source-coverage carries and records for openai-preparedness (PF v2)

No DRI signature is needed and none is reserved. One DELTA row (legend wording), covered by standing ruling R1.

Branch `infra/srccov-openai-preparedness-1119`, rebased onto VE main `b937b17c6c` (merge base); the
work began at main `09bea0972d`, and nothing under `usecases/openai-preparedness/` changed between them.
The lines each claim cites from a /tmp log are copied into [evidence.md](evidence.md).
Map: `reviews/source-coverage-1119/` in manage-agents. I read METHOD.md with amendments 1-17,
openai-preparedness.md, rows-openai-preparedness.tsv, CHALLENGE.md, challenge2/RESULT.md and
units-openai-preparedness.tsv. The pinned text is `pf-v2.txt`, sha256 `d2e3dd5b…`, as
`build_document.py:24-26` pins it. No PF file changed between the map's pin `e53db4e8fc` and main
(`git diff --stat e53db4e8fc HEAD -- usecases/openai-preparedness/` was empty).

## 0. Verify table (17 candidate rows)

Carrier rule (METHOD amendment 4): a legend carries only if a rule or fact line uses its symbol.
- Every predicate below is used by `rules.d1.ve` (grep counts, section 6).
- The nine Table 1 constants are used by the fact lines `facts.d1.ve:1-12` (bio-high … ais-critical).
- The `category` sort is used by `rules.d1.ve` (8 uses).
- `research_category_review` is used by `rules.d1.ve:182` (block f13-review).

| row | verdict | units kept | reason (file:line) |
|---|---|---|---|
| srccov-openai-preparedness-1-1119 | KEPT | S0005, S0006, S0007, S0064 (part), S0071 (part), S0083 (part) | Category sentences and Table 1 category cells go to the constant legends (`pf_vocabulary.py:73` CATEGORY_TEXT). Other cells of the merged units are already carried elsewhere: S0071's BIO-C bullet by f1-contrib-bio, S0083's halt bullet by f1-halt. The column titles stay outside the legends (`tests/test_pf_fidelity_fix.py:1132`). |
| srccov-openai-preparedness-2-1119 | KEPT | S0065, S0066, S0068 (part), S0069, S0072, S0073, S0074, S0080, S0081, S0082, S0084, S0085, S0087 (part), S0088 | Threshold and risk cells go to the six level legends (`pf_vocabulary.py:22` LEVEL_TEXT). The first bullets of S0068 and S0087 are f1 rules. I checked the S0085 column with the PDF layout: it is the AIS-H risk cell. |
| srccov-openai-preparedness-3-1119 | KEPT | S0047 (part), S0048, S0049, S0050 | Criteria 1-5 go to plausible … irremediable (`pf_vocabulary.py:269-281`). S0047's lead-in is reading rs12-category, not carried here. |
| srccov-openai-preparedness-4-1119 | KEPT | S0097 (part), S0099, S0100 (part), S0101 (part), S0102 (part) | Table 2 description cells go to `*_found` (`pf_vocabulary.py:184-203`). The response cells are f12 rules. S0097's "(see Section 4.2" is already an exposition omit (`accounting.d1.txt:77`). |
| srccov-openai-preparedness-5-1119 | KEPT | S0012, S0015, S0046, S0052, S0055, S0057, S0090, S0235, S0245 | S0015 goes to `sufficient_safeguards` (:130), S0046 to sort `category` (:583), S0055/S0057/S0235/S0236 to `high`/`critical` (:146, :150). The Research Category definitions go to `research_category_review` (:246), not `research_review`, because `tests/test_pf_fidelity_fix.py:574` pins research_review's quotations to 2.3's one sentence. |
| srccov-openai-preparedness-6-1119 | KEPT | S0127, S0128, S0129, S0135 (part), S0136, S0137, S0138, S0139, S0140 | S0135 and its examples go to `covered` (:108); the heading "3.2 Testing scope" is not carried. S0127-S0129 go to `evaluations_before_deployment` (:452). |
| srccov-openai-preparedness-14-1119 | DROPPED | none | Already recorded at main as `exposition` omits: `accounting.d1.txt:93` (fn5-indicator), `:77-78` (f12-lra), `:36` (f9-report). The row asks to relabel them `loss`, but `loss` is the translator's fidelity finding with a class number (`usecases/safetyfw_accounting.py:10-11, 293`). That relabel would claim a fidelity loss the text does not have and change the accounting score, so it is not a language carry. |
| srccov-openai-preparedness-15-1119 | KEPT | S0055, S0235 | `high` (:146), 2.2 and change-log item 2 |
| srccov-openai-preparedness-16-1119 | KEPT | S0236 | `critical` (:150), with S0057 |
| srccov-openai-preparedness-17-1119 | KEPT | S0145 | `reached` (:159). It is read by f4-security, whose legends must not say "covered" (`tests/test_pf_fidelity_fix.py:519`); this text does not. |
| srccov-openai-preparedness-18-1119 | KEPT | S0175, S0287, S0288, S0289, S0290, S0291, S0304 | `misuse_safeguards` (:324). The C.1 copies are read after the C.1 heading, because 4.2 has different wordings of the same claims. S0304 is marked "Table 4 (illustrative)". |
| srccov-openai-preparedness-19-1119 | KEPT | S0314 (part), S0316, S0321, S0322, S0330, S0337, S0338, S0344 | `alignment_safeguards` (:349). Only S0314's C.2 sentence is carried: its Table 4 cell, caption and heading are not. `misalignment_risk_minimized` is not a carrier because its quotations are pinned (`tests/test_pf_fidelity_fix.py:678`). |
| srccov-openai-preparedness-20-1119 | KEPT | S0352 (part), S0353-S0365, S0366 (part), S0367-S0371, S0372 (part), S0373, S0374 | `security_practices` (:391). S0352 contributes its C.3 sentence only. S0366 contributes its Identity and Device Management sub-item only; its first sentence is `access_limited` (:571). S0372's third sub-item is **not carried**: see FOLLOW-UP. |
| srccov-openai-preparedness-21-1119 | KEPT | S0242, S0243, S0245 | `research_category_review` (:246), re-pointed from `research_review` for the reason given at row 5 |
| srccov-openai-preparedness-22-1119 | KEPT | S0247 | `evaluations_before_deployment` (:452) |
| srccov-openai-preparedness-29-1119 | KEPT in part | S0230, S0234, S0240, S0248, S0252, S0255 (records) | Recorded as LABELLED exposition (change-log history). Dropped: S0228, S0229, S0231, S0232, S0237, S0238, S0249, S0251, S0253 and S0254. Each holds a claim marker (we/our), and the case refuses LABELLED for any unit with a `build_document.CLAIM_MARKER` hit (`tests/test_safetyfw_usecases.py:785-793`). Also dropped: the "cl-levels omits → loss" part, for row 14's reason. |
| srccov-openai-preparedness-30-1119 | KEPT in part | S0286 (record) | S0286 is the C.1 background sentence, with no marker. Dropped: S0085 (modal "may": amendment 12; it is carried instead, in row 2), S0105 (we, could), S0197 (could, can), S0282 (our, require) and S0283 (should, will: amendment 12). |

### Recording (the 11 OUT-OF-SCOPE-UNRECORDED units)

| unit | verdict | record file:line or reason |
|---|---|---|
| S0134 | DROPPED (not recordable) | spans unit p10-u146 also holds S0135, the 3.2 scope rule (OPEN, ot7). Labelling it would record a rule as out of scope, and a split renumbers every later unit id (`build_document.py:segments`). The words are in no block header, so `accounting.d1.txt` cannot hold them either. FOLLOW-UP. |
| S0208 | DROPPED (not recordable) | p13-u218 also holds S0207, a hedged claim (row 26, needs_rule_line=yes). Same reason as S0134. FOLLOW-UP. |
| S0209 | RECORDED | spans.json `p13-u219` LABELLED exposition. Placed by `build_document.py:107` ("label"), branch `build_document.py:407`. |
| S0211 | RECORDED | spans.json `p13-u221` LABELLED exposition (`build_document.py:108`) |
| S0216 | DROPPED (not recordable) | p13-u227 is the OPEN rule unit of f14-corrective (S0215). FOLLOW-UP. |
| S0281 | DROPPED (not recordable) | Holds claim markers (we, could). The case refuses LABELLED for such units (`tests/test_safetyfw_usecases.py:792-793`). FOLLOW-UP. |
| S0292 | DROPPED (not recordable) | Claim markers (we, our, could). Same rule. FOLLOW-UP. |
| S0293 | DROPPED (not recordable) | Claim marker (could) in a table header. Same rule. FOLLOW-UP. |
| S0323 | DROPPED (not recordable) | Claim markers (we, our, could). Its unit p19-u340 is pinned as not LABELLED (`tests/test_safetyfw_usecases.py:787`). FOLLOW-UP. |
| S0324 | RECORDED | spans.json `p20-u341` LABELLED exposition (`build_document.py:109`) |
| S0339 | RECORDED | spans.json `p20-u356` LABELLED exposition (`build_document.py:110`) |

No recorded unit holds a modal, definition, number, date or condition (amendment 12). The one number
is S0255's list number "12.". The test `test_the_records_are_the_label_placements_of_the_build` also
checks that no recorded unit has a claim-marker hit.

## 1. What changed

- **Carries.** 92 quotations covering 90 source units go into 30 legends of `pf_vocabulary.py`
  (environment.d1.json):
  - 21 predicates, the `category` sort and 9 constants (6 Table 1 levels, 3 Tracked Categories);
  - each is appended as `; <section>: “…”`, word for word from the pinned text;
  - PDF line-break hyphens are rejoined, as amendment 6 and the existing PF legends do;
  - the page number "20" inside S0371 is dropped by splitting that unit into two quotations.

  Counts are from `test_the_carries_reach_every_kept_unit_once_per_passage`. A legend's base text is
  always its prefix (`test_each_changed_legend_keeps_its_base_text_as_its_prefix`).
- **Records.** A new `("label", kind, ())` placement in `build_document.py` PLACEMENTS (branch at :407)
  turns 12 spans.json units into LABELLED `exposition`, the only record form PF's spans.json already
  uses. They cover 11 source units: 4 of the OUT-OF-SCOPE-UNRECORDED units, 6 change-log items (S0255
  has two spans units) and S0286. `git diff` of spans.json changes exactly those 12 units.
- **Regenerated with the case's own scripts:**
  - `build_document.py` → spans.json, coverage.json;
  - `measure.py` → gaps.json, units.json;
  - `stage0.py` → stage0.json;
  - `safetyfw_accounting.py --source --report` → accounting.json (unaccounted words 509 → 468);
  - `run.py` → results.json, only `metrics.M3` (4 values);
  - `conformance.english_lean_lexicon` → lexicon-report.json (PF row only);
  - `conformance.english_lean_seal` → corpus-seal.json, which also re-sealed main's own stale FSF
    environment line after the rebase.

  The README coverage table and the safetyfw REPORT row carry the new counts, as precedent commit
  `d4d72cfe2a` did:
  - LABELLED 48 → 60 units, 5,327 → 6,467 bytes;
  - UNFORMALISED 292 → 280 units, 52,586 → 51,446 bytes.

  `tools/regen_generated.py --check` returned rc 0.
- **Not regenerated:**
  - `tests/data/fidmech/wording-inputs/**` and `wording-golden.json` are frozen copies of the bundle's
    inputs (`tests/test_fidmech_wording.py:1-4`); no tool regenerates them, and the FSF siblings left
    theirs unchanged.
  - `docs/infra/fid-mech-b2/openai-preparedness.json` is the dated fid-mech-b2 run at `9d42ed27c8`, and
    it already differs from main (L2b 45 vs 44). It is saved evidence, so I did not rewrite it.

## 2. Answers touched (so later reads re-pin)

- **Keyed answers: none moved.** I diffed results.json before and after `run.py` (/tmp/pf-run.log:
  "236 / 239"). `comparison` and `mutants` are identical; the only changed paths are
  `metrics/M3/bytes_by_kind/{exposition,unformalised}` and `metrics/M3/bytes_by_status/{LABELLED,UNFORMALISED}`.
- **Reader inputs changed.** A later PF read must re-pin to these files:
  - environment.d1.json, sha256 `528d1489effc1b58d748a2c3b6044fa398d6aa2c9ff141ea322655404833c5ae`; it
    has 30 legends with new text, and its lexicon_id changed (lexicon-report.json);
  - spans.json, sha256 `f853d2cd1b5ccd3d624e60c15c85dd271d6075e7dbb72ca73ab261d32662a1a7`, with 12
    units now LABELLED;
  - pf_vocabulary.py, sha256 `8916942c1b0c776f33e1cf366f582408e4088639385d5c5dc22f51354fb1a712`;
  - coverage.json, whose document_sha256 is now `46374ce4…`.

## 3. Condition test

`tests/test_srccov_openai_preparedness_1119.py` (new file; the selection picks it, as
`/tmp/pf-sel.log` shows).
- **Carries.** For each of the 92 quotations, the test reads the passage from the pinned source
  (`tests/pinned_source.py`) inside its unit's byte span. It asserts that the passage equals one
  whole `“…”` quotation of the legend in environment.d1.json under the case's normalisation,
  `source/quote_evidence.py` `plain`. A source-free twin checks that each quotation's first and last
  words are in the legend.
- **Records.** For each of the 11 source units, the spans.json units must be LABELLED exposition with no
  waits and must cover the unit's text. One exception: a change-log item's "N. " sits in the previous
  unit, which also holds other text. With the source, the test also checks that the build's `label`
  placements are exactly these units.
- On main's PF files (`git checkout main -- usecases/openai-preparedness`, run, restore): 196 failed,
  1 passed (the table self-check) (/tmp/pf-cond-main.log). At HEAD: 200 passed, together with the two
  reran tests (/tmp/pf-rerun.log).

## 4. Seeded bugs (each planted, condition test run, restored with `git checkout`)

| # | language, file | bug | failing test (log) |
|---|---|---|---|
| S1 | Python, `usecases/openai-preparedness/pf_vocabulary.py` | cut "holistic judgment … – for" from the `reached` legend (one carried sentence), regenerate | `test_the_legend_quotes_the_source_passage_whole[S0145-reached-…]` (/tmp/seed-S1-legend.log: 1 failed) |
| S2 | Python, `usecases/openai-preparedness/pf_vocabulary.py` | drop `LEVEL_TEXT[k]` from the constant legends in `environment()` | 28 failed, e.g. `…passage_whole[S0065-biological_and_chemical_high-…]` (/tmp/seed-S2-constants.log) |
| S3 | Python, `usecases/openai-preparedness/build_document.py` | the `label` branch builds `unformalised("unmapped_claim")`, rebuild spans | 11 failed, `test_the_unit_is_recorded_as_labelled_exposition[S0209]` … (/tmp/seed-S3-record.log) |
| S4 | Python, `usecases/openai-preparedness/build_document.py` | delete the "Internal Transparency." placement, rebuild | `…recorded_as_labelled_exposition[S0211]`, `test_the_records_are_the_label_placements_of_the_build` (/tmp/seed-S4-placement.log) |

No Lean or Rust product code changed. Trust mutants: the light lane said NOT (993 lines). The sweep ran
through `mac-pytest.sh --trustmut`: "0 definitions, 0 mutants … 0 KILLED, 0 SURVIVOR" (/tmp/pf-tm.log).

## 5. DELTA

| # | user-visible delta | Ruling | test |
|---|---|---|---|
| 1 | 30 PF legends (environment.d1.json descriptions) gain appended source quotations. Each base text is kept unchanged as the prefix; no name, field or other legend changes. | R1 (standing ruling, DRI-RULINGS.md) | `tests/test_srccov_openai_preparedness_1119.py::test_each_changed_legend_keeps_its_base_text_as_its_prefix` |

Not DELTA rows:
- The 12 coverage reclassifications. The task's recording ruling says recording adds no DELTA row;
  no verdict or keyed answer moved (section 2).
- The README and REPORT counts, which restate them.

## 6. Tests run

- Selected run: `mac-pytest.sh --select -- --base 12cb72fa55 --run` on ve-cloud-2 (/tmp/pf-select.log).
  It ran 378 files; 2 failed, both caused by this change:
  - `test_english_lean_lexicon.py::test_every_corpus_environment_has_a_valid_selected_lexicon` (stale
    lexicon report): fixed by regenerating it;
  - `test_fidmech_records.py::test_every_third_value_spelling_in_an_adapted_documents_sources_is_recognised_by_the_kill_rule`
    (the word "unknown" in the S0372 carry): fixed by not carrying that sub-item.

  Both ids and the condition file were then rerun: 200 passed (/tmp/pf-rerun.log). So were the six PF
  tests in `test_safetyfw_usecases.py` that read the regenerated files: 6 passed (/tmp/pf-rerun2.log).
  The selected run had already passed `test_pf_fidelity_fix.py`, `test_safetyfw_usecases.py`,
  `test_safetyfw_accounting.py` and `test_pinned_sources.py`.
- Grep counts behind the carrier rule (at HEAD):
  - in `rules.d1.ve`: plausible 5, measurable 3, severe 42, net_new 3, irremediable 3, each `*_found` 1,
    reached 42, "is covered" 12, "review the latest research" 2, "undergo the suite of Scalable" 2,
    "have security practices" 1, "misuse safeguards meeting the High standard" 4, "misalignment
    safeguards meeting" 2;
  - in `facts.d1.ve`: every level and category constant at least once.
- No test in main-known-red.txt was touched.

SIZE: 320 product (pf_vocabulary.py 302 changed lines, nearly all quoted source text; build_document.py 18), 287 tests, 315 other hand-written lines (README 15, safetyfw REPORT 2, this REPORT 238, evidence.md 60).

## FOLLOW-UPs (unfinished deliverables)

FOLLOW-UP: srccov-openai-preparedness-records-1119 record S0134, S0208 and S0216, whose spans.json units also hold a rule sentence (S0135, S0207, S0215), and S0281, S0292, S0293 and S0323, whose text has a claim marker the case's LABELLED rule refuses
FOLLOW-UP: srccov-openai-preparedness-s0372-1119 carry S0372's "Adversarial Testing and Red-Teaming" sub-item (its word "unknown" needs a NOT_ANSWERS entry in tests/test_fidmech_records.py:193, outside this item's paths)

## Notes for the DRI

- I re-pointed the carrier for the Research Category definitions (rows 5 and 21) from `research_review`
  to `research_category_review`. Both are read by block f13-review. research_review's quotations are
  pinned by `test_pf_fidelity_fix.py:574`.
- fid-mech-b2's text check, rerun on main's files and then on HEAD (output in /tmp, not committed),
  moves these counts: L2q 9 → 25, L2a 2 → 18, L2b 44 → 41, D 665 → 625.
  - L2q and L2a are report-only classes (`tools/fidmech/report.py:39`, NO_ALLEGATION). L2q comes from
    fidmech `norm()` not rejoining PDF hyphens, while the case's `plain()` does; L2a marks passages in
    spans no rule links.
  - D (dropped words) falls by 40, because the legends now account for those words.
- Coverage records needed a small Python change, `build_document.py`'s `label` placement kind
  (helper `label` is already imported at :28). This is the only way the case's spans.json can hold a
  LABELLED record. For units with a claim marker I took the narrower option and did not record them.
- Files outside the task's path list, all following the PF precedent `d4d72cfe2a`:
  - `docs/usecases/safetyfw/REPORT.md` (one row) and `docs/usecases/safetyfw/openai-preparedness/*.json`
    (generated);
  - `conformance/english-lean/lexicon-report.json` (generated).

## Spec re-read

- Row carries against `rows-openai-preparedness.tsv:3-8,16-25` (carrier keys and units).
- Records against METHOD.md:26 (R, unit records), :34-35 (class 3-4) and :43-44 (amendments 12 and 13).
- The condition test against the task's deliverable 3 (byte-for-byte after quote normalisation;
  record with unit id).
- The R1 row against DRI-RULINGS.md R1 (a)-(c).

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer or relay is read or changed.
2. PASS: every deliverable is mapped in sections 0-5. "Generated" files were made by their scripts
   (section 1). `tools/regen_generated.py --check` rc 0.
3. PASS: seeded bugs S1-S4 (section 4) each fail a named test. On main's files, 196 condition-test
   cases fail (/tmp/pf-cond-main.log).
4. N.A.: no Python, Lean or Rust decision path changed. results.json `comparison` and `mutants` are
   identical before and after (section 2).
5. N.A.: no relayed field is read.
6. PASS: rebased on main b937b17c6c before the final checks (lexicon report unchanged by the rebase; corpus seal regenerated). The chain runs the gate on the final HEAD.
7. PASS: the single DELTA row cites R1 with its test
   (`test_each_changed_legend_keeps_its_base_text_as_its_prefix`).
8. PASS: environment, spans and coverage diffs are listed (sections 1, 2 and 5). The keyed-answer diff
   is empty (results.json comparison identical).
9. PASS: `tools/select_tests.py --base $(git merge-base HEAD main)` selects
   `tests/test_srccov_openai_preparedness_1119.py` and every PF, fidmech and lexicon test
   (/tmp/pf-sel.log). The selected run caught both real breakages (section 6).
10. N.A.: no Lean statement or proof changed.
11. N.A.: no budget, limit or deadline is touched. The new test uses no sleep or timing.
12. N.A.: legend text only. The PF build stays at about 19 s (`build_document.py --check`).
13. N.A.: no test removed or renamed.
14. PASS: both directions are covered. Main's files fail the test and HEAD passes. A cut sentence (S1) or
    a dropped placement (S4) fails it. Each count in this REPORT names its command or log.
15. PASS:
   - No overclaim: the universal words here ("every", "none moved", "exactly") rest on
     `test_the_carries_reach_every_kept_unit_once_per_passage`, the results.json path diff and
     `test_the_records_are_the_label_placements_of_the_build`.
   - No silent cut: the two FOLLOW-UPs name the uncarried units and their seams.
   - Every check can fail: S1-S4.
   - Limits: N.A.
