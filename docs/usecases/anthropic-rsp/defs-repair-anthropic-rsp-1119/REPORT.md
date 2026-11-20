# defs-repair-anthropic-rsp-1119 REPORT

No DRI signature is needed and no DELTA row is reserved (DELTA.md has no rows: legend text only, trust +0).
Status: 53 of the 55 P1 rows KEPT and carried word for word; 2 DROPPED (x62, x63: already shown verbatim). Base main
12cb72fa55 (the VE commit this merges at unless main moves again). Changed: RSP predicate legends (rsp_vocabulary.py),
D2 harm and D3 coverage-date legends (stage0.py), two stale accounting losses, every derived file by its tool.
Open: x4's definition does not reach 5 of its blocks through `listed` (FOLLOW-UP below). The full gate is the chain's.

## 0. Verification of every candidate (deliverable 0)

Checked first: the pinned text `~/code/manage-agents/pilots/anthropic-rsp/source/rsp-3.4.txt` has SHA-256
c7de7fe2f1f44cdd650efb327ecd798f1140034cf6328eb2e494de587c2c3063 = `usecases/pinned_sources.json` text_sha256
(`sha256sum`). Each row's quote was matched against NFKC(source) word run by word run (/tmp/drsp/extract.py): every
KEPT quote is a substring of the source or, where the PDF extract puts a footnote, the page foot or the next column in
between, two substrings (x17/x18, x24, x41/x42, x57: noted in the test's locations). Carried at main was checked with
the audit's own helper on the counter's carrier texts (`carriers-readdocs.py anthropic-rsp 09bea0972d`, 87 units):
no KEPT quote was carried in any unit it names. Which predicates each block uses was read from the same output. The
six rows blocked by rsp-repair-r1-catastrophic-1119 (x14, x16, x18, x20, x22, x31) were checked against R1's merged
commit c790d35168: it changed only the `existential_threats` legend (footnote 1), so none of the six is carried by
R1, and all six are KEPT. Rows outside the task list (x7, x11, x12 R4/R5; x23, x32, x59-x61 P2) were not taken.

| row | verdict | reason (source and carrier at file:line) | answers_touched (audit) |
|---|---|---|---|
| defs-anthropic-rsp-x1-1119 | KEPT | source rsp-3.4.txt:4 (footnote 1 "refers generally to"); not carried at main; now on `argument_required` legend, rsp_vocabulary.py:740 | 3 of 126 keyed |
| defs-anthropic-rsp-x2-1119 | KEPT | source rsp-3.4.txt:4 (footnote 1 "refers generally to"); not carried at main; now on `lead_delay_needed` legend, rsp_vocabulary.py:234 | 5 of 126 keyed |
| defs-anthropic-rsp-x3-1119 | KEPT | source rsp-3.4.txt:4 (footnote 1 "refers generally to"); not carried at main; now on `competitors_evidence` legend, rsp_vocabulary.py:216 | 6 of 126 keyed |
| defs-anthropic-rsp-x4-1119 | KEPT | source rsp-3.4.txt:4 (§1 table, left column); not carried at main; now on `listed` legend, rsp_vocabulary.py:65; reaches FACTS, f5-default/strict, rows-cond/uncond, threshold-t1..t4; f5-evidence-*, highly-capable-t4, t4-only-if, t4-suff use `crossed`, not `listed` (FOLLOW-UP) | 49 of 126 keyed |
| defs-anthropic-rsp-x5-1119 | KEPT | source rsp-3.4.txt:4 (§1 table, middle column); not carried at main; now on `plans_in_place` legend, rsp_vocabulary.py:442 | 20 of 126 keyed |
| defs-anthropic-rsp-x6-1119 | KEPT | source rsp-3.4.txt:6 (footnote 3 (middle-column header)); not carried at main; now on `plans_in_place` legend, rsp_vocabulary.py:442 | 20 of 126 keyed |
| defs-anthropic-rsp-x8-1119 | KEPT | source rsp-3.4.txt:4 (§1 table, right column (R4 passage, S:7)); not carried at main; now on `advance_recommendations` legend, rsp_vocabulary.py:454 | 0 of 126 keyed |
| defs-anthropic-rsp-x9-1119 | KEPT | source rsp-3.4.txt:4 (§1 table, right column (R4 passage, S:7)); not carried at main; now on `argument_required` legend, rsp_vocabulary.py:740 | 3 of 126 keyed |
| defs-anthropic-rsp-x10-1119 | KEPT | source rsp-3.4.txt:4 (§1 table, right column (R4 passage, S:7)); not carried at main; now on `competitors_evidence` legend, rsp_vocabulary.py:216 | 6 of 126 keyed |
| defs-anthropic-rsp-x13-1119 | KEPT | source rsp-3.4.txt:6 (table row T1, left column); not carried at main; now on `listed` legend, rsp_vocabulary.py:65 | 40 of 126 keyed |
| defs-anthropic-rsp-x14-1119 | KEPT | source rsp-3.4.txt:6 (table row T1, left column); not carried at main; now on D2 harm `harm_of_non_novel_chem_bio_weapons` legend, stage0.py:55; R1 (c790d35168) changed only `existential_threats`, so it does not carry this | 17 of 126 keyed |
| defs-anthropic-rsp-x15-1119 | KEPT | source rsp-3.4.txt:7 (table row T2, left column (footnote marks 4-7)); not carried at main; now on `listed` legend, rsp_vocabulary.py:65 | 40 of 126 keyed |
| defs-anthropic-rsp-x16-1119 | KEPT | source rsp-3.4.txt:7 (table row T2, left column (footnote marks 4-7)); not carried at main; now on D2 harm `harm_of_novel_chem_bio_weapons` legend, stage0.py:60; R1 (c790d35168) changed only `existential_threats`, so it does not carry this | 17 of 126 keyed |
| defs-anthropic-rsp-x17-1119 | KEPT | source rsp-3.4.txt:7,8 (table row T3, left column (extract interleaves the columns; ); not carried at main; now on `listed` legend, rsp_vocabulary.py:65 | 40 of 126 keyed |
| defs-anthropic-rsp-x18-1119 | KEPT | source rsp-3.4.txt:7,8 (table row T3, left column (extract interleaves the columns; ); not carried at main; now on D2 harm `harm_of_misaligned_high_stakes` legend, stage0.py:72; R1 (c790d35168) changed only `existential_threats`, so it does not carry this | 17 of 126 keyed |
| defs-anthropic-rsp-x19-1119 | KEPT | source rsp-3.4.txt:8 (table row T4, left column); not carried at main; now on `listed` legend, rsp_vocabulary.py:65 | 40 of 126 keyed |
| defs-anthropic-rsp-x20-1119 | KEPT | source rsp-3.4.txt:8 (table row T4, left column); not carried at main; now on D2 harm `harm_of_automated_rd` legend, stage0.py:84; R1 (c790d35168) changed only `existential_threats`, so it does not carry this | 17 of 126 keyed |
| defs-anthropic-rsp-x21-1119 | KEPT | source rsp-3.4.txt:7 (footnotes 7, 6, 5, 4 ("That is", "In particular")); not carried at main; now on `listed` legend, rsp_vocabulary.py:65 | 40 of 126 keyed |
| defs-anthropic-rsp-x22-1119 | KEPT | source rsp-3.4.txt:7 (footnotes 7, 6, 5, 4 ("That is", "In particular")); not carried at main; now on D2 harm `harm_of_novel_chem_bio_weapons` legend, stage0.py:60; R1 (c790d35168) changed only `existential_threats`, so it does not carry this | 17 of 126 keyed |
| defs-anthropic-rsp-x24-1119 | KEPT | source rsp-3.4.txt:9,10 (row T4 scenario (2) (two runs joined)); not carried at main; now on `automation_attributable` legend, rsp_vocabulary.py:281 | 9 of 126 keyed |
| defs-anthropic-rsp-x25-1119 | KEPT | source rsp-3.4.txt:9 (footnote 8 "means"); not carried at main; now on `double_rate` legend, rsp_vocabulary.py:271 | 9 of 126 keyed |
| defs-anthropic-rsp-x26-1119 | KEPT | source rsp-3.4.txt:9 (footnote 9); not carried at main; now on `double_rate` legend, rsp_vocabulary.py:271 | 9 of 126 keyed |
| defs-anthropic-rsp-x27-1119 | KEPT | source rsp-3.4.txt:14 (§3.6 "defined as follows" bullet 1 (+ L10 "intended to refle); not carried at main; now on `highly_capable` legend, rsp_vocabulary.py:190 | 9 of 126 keyed |
| defs-anthropic-rsp-x28-1119 | KEPT | source rsp-3.4.txt:14 (§3.6 "defined as follows" bullet 1 (+ L10 "intended to refle); not carried at main; now on `in_the_lead` legend, rsp_vocabulary.py:166; reaches f24-argument, f24-delay; f25-delay/f25-meet do not use `in_the_lead` (x27 carries it there on `highly_capable`) | 8 of 126 keyed |
| defs-anthropic-rsp-x29-1119 | KEPT | source rsp-3.4.txt:14 (§3.6 bullet 2 "means" + "deemed"); not carried at main; now on `significantly_redacted` legend, rsp_vocabulary.py:203 | 3 of 126 keyed |
| defs-anthropic-rsp-x30-1119 | KEPT | source rsp-3.4.txt:11 (§3.1 Scope); not carried at main; now on `in_scope` legend, rsp_vocabulary.py:514 | 12 of 126 keyed |
| defs-anthropic-rsp-x31-1119 | KEPT | source rsp-3.4.txt:11 (§3.1 Scope); not carried at main; now on D3 `start_day` legend `COVERAGE_WORDS`, stage0.py:176; R1 (c790d35168) changed only `existential_threats`, so it does not carry this | 17 of 126 keyed |
| defs-anthropic-rsp-x33-1119 | KEPT | source rsp-3.4.txt:12 (§3.3 Factual information list); not carried at main; now on `factual_documented` legend, rsp_vocabulary.py:539 | 0 of 126 keyed |
| defs-anthropic-rsp-x34-1119 | KEPT | source rsp-3.4.txt:12 (§3.3 Risk analyses list ("i.e." remaining absolute risk)); not carried at main; now on `risk_analysed` legend, rsp_vocabulary.py:550 | 0 of 126 keyed |
| defs-anthropic-rsp-x35-1119 | KEPT | source rsp-3.4.txt:13 (§3.3 Review list); not carried at main; now on `past_reviewed` legend, rsp_vocabulary.py:558 | 0 of 126 keyed |
| defs-anthropic-rsp-x36-1119 | KEPT | source rsp-3.4.txt:13 (§3.3 marginal list); not carried at main; now on `marginal_analysed` legend, rsp_vocabulary.py:576 | 1 of 126 keyed |
| defs-anthropic-rsp-x37-1119 | KEPT | source rsp-3.4.txt:13 (footnote 11 "By ... we mean"); not carried at main; now on `marginal_justification` legend, rsp_vocabulary.py:256 | 1 of 126 keyed |
| defs-anthropic-rsp-x38-1119 | KEPT | source rsp-3.4.txt:13 (footnote 11 "By ... we mean"); not carried at main; now on `marginal_major_role` legend, rsp_vocabulary.py:262 | 2 of 126 keyed |
| defs-anthropic-rsp-x39-1119 | KEPT | source rsp-3.4.txt:14 (§3.5 list); not carried at main; now on `redaction_reason_listed` legend, rsp_vocabulary.py:170 | 2 of 126 keyed |
| defs-anthropic-rsp-x40-1119 | KEPT | source rsp-3.4.txt:14 (§3.6 "This means"); not carried at main; now on `public_review_sought` legend, rsp_vocabulary.py:625 | 0 of 126 keyed |
| defs-anthropic-rsp-x41-1119 | KEPT | source rsp-3.4.txt:15,16 (§3.6.3 lists (footnote 12 text between them dropped)); not carried at main; now on `external_review_process` legend, rsp_vocabulary.py:131 | 1 of 126 keyed |
| defs-anthropic-rsp-x42-1119 | KEPT | source rsp-3.4.txt:15,16 (§3.6.3 lists (footnote 12 text between them dropped)); not carried at main; now on `full_review` legend, rsp_vocabulary.py:631 | 3 of 126 keyed |
| defs-anthropic-rsp-x43-1119 | KEPT | source rsp-3.4.txt:15 (footnote 12 "It does not mean"); not carried at main; now on `legal_rights_redaction` legend, rsp_vocabulary.py:114 | 1 of 126 keyed |
| defs-anthropic-rsp-x44-1119 | KEPT | source rsp-3.4.txt:16 (§4.1 appositive); not carried at main; now on `rso_maintained` legend, rsp_vocabulary.py:678 | 0 of 126 keyed |
| defs-anthropic-rsp-x45-1119 | KEPT | source rsp-3.4.txt:16 (§4.1 appositive); not carried at main; now on `executive_submitted` legend, rsp_vocabulary.py:595 | 1 of 126 keyed |
| defs-anthropic-rsp-x46-1119 | KEPT | source rsp-3.4.txt:16 (§4.1 appositive); not carried at main; now on `governance_notified` legend, rsp_vocabulary.py:604 | 2 of 126 keyed |
| defs-anthropic-rsp-x47-1119 | KEPT | source rsp-3.4.txt:16 (§4.1 appositive); not carried at main; now on `recipient_options` legend, rsp_vocabulary.py:701 | 0 of 126 keyed |
| defs-anthropic-rsp-x48-1119 | KEPT | source rsp-3.4.txt:16 (§4.1 appositive); not carried at main; now on `concerns_rso` legend, rsp_vocabulary.py:148 | 1 of 126 keyed |
| defs-anthropic-rsp-x49-1119 | KEPT | source rsp-3.4.txt:16 (§4.1 appositive); not carried at main; now on `change_approved` legend, rsp_vocabulary.py:731 | 0 of 126 keyed |
| defs-anthropic-rsp-x50-1119 | KEPT | source rsp-3.4.txt:16 (§4.1 duties list); not carried at main; now on `rso_maintained` legend, rsp_vocabulary.py:678 | 0 of 126 keyed |
| defs-anthropic-rsp-x51-1119 | KEPT | source rsp-3.4.txt:3 (Introduction ("not hard commitments but rather")); not carried at main; now on `roadmap_maintained` legend, rsp_vocabulary.py:468 | 0 of 126 keyed |
| defs-anthropic-rsp-x52-1119 | KEPT | source rsp-3.4.txt:3 (Introduction ("not hard commitments but rather")); not carried at main; now on `roadmap_shared` legend, rsp_vocabulary.py:477 | 0 of 126 keyed |
| defs-anthropic-rsp-x53-1119 | KEPT | source rsp-3.4.txt:3 (Introduction ("not hard commitments but rather")); not carried at main; now on `roadmap_updates` legend, rsp_vocabulary.py:485 | 0 of 126 keyed |
| defs-anthropic-rsp-x54-1119 | KEPT | source rsp-3.4.txt:3 (Introduction ("not hard commitments but rather")); not carried at main; now on `past_roadmaps_kept` legend, rsp_vocabulary.py:492 | 0 of 126 keyed |
| defs-anthropic-rsp-x55-1119 | KEPT | source rsp-3.4.txt:3 (Introduction ("not hard commitments but rather")); not carried at main; now on `goals_kept` legend, rsp_vocabulary.py:501 | 0 of 126 keyed |
| defs-anthropic-rsp-x56-1119 | KEPT | source rsp-3.4.txt:3 (Introduction ("not hard commitments but rather")); not carried at main; now on `roadmap_review_addressed` legend, rsp_vocabulary.py:567 | 1 of 126 keyed |
| defs-anthropic-rsp-x57-1119 | KEPT | source rsp-3.4.txt:17,18 (Appendix B "refer to"); not carried at main; now on `plans_in_place` legend, rsp_vocabulary.py:442 | 20 of 126 keyed |
| defs-anthropic-rsp-x58-1119 | KEPT | source rsp-3.4.txt:18 (Changelog v2.0 "refers to"); not carried at main; now on `plans_in_place` legend, rsp_vocabulary.py:442 | 20 of 126 keyed |
| defs-anthropic-rsp-x62-1119 | DROPPED | already carried word for word in what the reader is shown: every ROW_PLANS cell is in `plans_in_place`'s description (environment.d1.json, built by `_row_plans_legend()`, rsp_vocabulary.py:442); the row's quote is a pointer, not a source sentence; making it counted needs a copy of ROW_PLANS (one-owner rule) or a counter change (out of scope) | 20 of 126 keyed |
| defs-anthropic-rsp-x63-1119 | DROPPED | already carried word for word in what the reader is shown: every ROW_ARGUMENTS cell is in `strong_argument`'s description (environment.d1.json, built by `_row_arguments_legend()`, rsp_vocabulary.py:452); the row's quote is a pointer, not a source sentence; making it counted needs a copy of ROW_ARGUMENTS (one-owner rule) or a counter change (out of scope) | 20 of 126 keyed |


## 1. What was carried, and where (deliverable 1)

- **Vocabulary legends (47 rows, 35 keys).** Each source sentence is appended to the legend (description) of the
  predicate its rule blocks use, in `usecases/anthropic-rsp/rsp_vocabulary.py`, as `<legend> + ("; in the source's
  words (<location>): “<sentence>” ...")`. The `+` keeps it a separate string, so it is never part of a citation-led
  provenance string (the counter's `_omit_legend_segments` rule, METHOD-READDOCS amendment 2); it starts with "; in
  the source's words", not a citation. Text: the NFKC form of the pinned source (ligatures folded; curly quotes,
  dashes, footnote marks and the extract's spacing such as "“ highly capable”" and "Section 1 ." kept).
  `environment.d1.json` (what the reader is shown) was rewritten by `uv run python usecases/anthropic-rsp/rsp_vocabulary.py`.
  Rows sharing one sentence (FN1 on 3 keys, RSO on 6, the Introduction's Roadmap paragraph on 6, the right-column
  sentence on 3, footnote 11 on 2, 3.6.3 on 2, "highly capable" on 2) carry it once per key: each block counts only
  its own predicates' legends.
- **D2 (x14, x16, x18, x20, x22).** `stage0.HARMS`: each threshold's harm constant legend gets its row's left column
  whole (T2 also footnotes 7, 6, 5, 4), after its existing harm words.
- **D3 (x31).** `stage0.COVERAGE_WORDS` describes the `start_day` constant of the "publication within" question (D3b;
  its start day is the coverage date) with 3.1's Scope sentence; `date_environment(extra, words=None)` takes it, and
  `d3()` passes it for that question only (D4/D5's start days are other dates). The legend selection is text: the
  formulas, goals and certificates are unchanged.
- **Accounting.** Two losses became false once carried: `f11-review` "and decisions" (now in x35's sentence on
  `past_reviewed`) and D2D3's "A Risk Report will cover the risks of Anthropic's models and actions" (x31; with it the
  "Scope." exposition), so `accounting.d1.txt` drops them (D2D3 now `omits: nothing`).
  `uv run python usecases/safetyfw_accounting.py anthropic-rsp --source <pinned> --check` exit 0 (85 blocks, 0 of 141
  quotes unanchored).
- **Counter view, after.** `carriers-readdocs.py anthropic-rsp 32d508476b` (the carrier commit before the rebase; same
  product files): every KEPT quote (citation parentheses cut from the quote, amendment 2) is CARRIED in every block
  the row names that uses its key; D2D3's code carries the six D2/D3 quotes once its split string literals are joined.

## 2. Derived files (deliverable 2), each by its own tool

| file | tool |
|---|---|
| usecases/anthropic-rsp/environment.d1.json | `uv run python usecases/anthropic-rsp/rsp_vocabulary.py` |
| docs/usecases/safetyfw/anthropic-rsp/accounting.json | `usecases/safetyfw_accounting.py anthropic-rsp --source <pinned> --report <it>` |
| docs/usecases/safetyfw/anthropic-rsp/stage0.json (D2 environment_id only) | `usecases/anthropic-rsp/stage0.py --source <pinned>` |
| conformance/english-lean/lexicon-report.json (RSP lexicon_id) | `uv run python -m conformance.english_lean_lexicon` |
| conformance/english-lean/corpus-seal.json | `uv run python -m conformance.english_lean_seal` (it also renews the safety-framework entry main left stale: `--check` listed it before) |
| tests/data/route-cases.jsonl (english.statement cases embedding the RSP environment) | `uv run python docs/en-e3-norm/en-2b/route_fixtures.py --write` |
| usecases/anthropic-rsp/coverage.json (its `document_sha256` line only; spans.json unchanged) | `uv run python usecases/anthropic-rsp/build_document.py --source <a copy of the pinned text in /tmp>` (output discarded; the file was not opened: SEAL) |

`uv run python tools/regen_generated.py --check`: exit 0, 41 entries. Left as they are, being frozen snapshots
(their safety-framework twins already differ from the live files): tests/data/fidmech/wording-inputs/anthropic-rsp/*,
tests/data/kb2a/rsp-mixed.*, tests/data/relay-gate-cases.jsonl, docs/kernel/kb-10e/cases/rsp-case-1.json. No
approved theorem statement and no rule formula changed (no .ve or lean/ file is in the diff).

## 3. Condition test (deliverable 3)

`tests/test_defs_repair_anthropic_rsp_1119.py` (103 tests) stores the 30 source sentences with their rsp-3.4.txt
locations and the 53 rows (sentence, carrier, the blocks it reaches) and asserts: each sentence, normalised by
`tools/fidmech/segment.py norm`, is in the committed and the built description of its key, inside a legend string
that is not citation-led; each carrier key is used by each named block (`test_rsp_fidelity_fix._used_predicates`);
the D2 harm legends and D3b's start-day legend (read from the environments `d3()` builds; D4/D5 must not get it)
carry theirs; no recorded accounting loss is a carried sentence; and, when the pinned text is stored at its pin
(`tests.pinned_source`, never downloaded), each run occurs once in it. On main's product files it fails: 54 failed,
49 passed (`git checkout main -- <4 product files>`, log /tmp/drsp/t-main.log); on HEAD: 103 passed.
Existing tests edited because they pinned the old state: `tests/test_rsp_b_repair_1115.py` (D2D3_LOSSES now empty),
`tests/test_rsp_repair_r1_catastrophic_1119.py` (the D2D3 line is now empty), `tests/test_rsp_fidelity_fix.py`
(the FACTS counterfactual also sets back `automation_attributable`, which now carries the scenario (2) sentence).

## Seeded bugs (Python, the only language changed; mutants.json)

| id | file | behaviour | failing test |
|---|---|---|---|
| M1 | usecases/anthropic-rsp/rsp_vocabulary.py | x29 on significantly_redacted | test_vocabulary_legend_carries_the_sentence[x29-…] |
| M2 | usecases/anthropic-rsp/rsp_vocabulary.py | x44 in a counted (not citation-led) string | test_vocabulary_legend_carries_the_sentence[x44-…] |
| M3 | usecases/anthropic-rsp/rsp_vocabulary.py | x6 whole on plans_in_place | test_vocabulary_legend_carries_the_sentence[x6-…] |
| M4 | usecases/anthropic-rsp/stage0.py | x18 on D2's harm_of_misaligned_high_stakes | test_d2_harm_legend_carries_its_rows_definition[x18] |
| M5 | usecases/anthropic-rsp/stage0.py | x22 on D2's harm_of_novel_chem_bio_weapons | test_d2_harm_legend_carries_its_rows_definition[x22] |
| M6 | usecases/anthropic-rsp/stage0.py | x31 on D3b's start day | test_d3_coverage_date_legend_carries_the_scope_sentence |
| M7 | usecases/anthropic-rsp/accounting.d1.txt | no stale loss | test_no_recorded_loss_is_a_carried_sentence |

All 7 FAILED when planted and were restored (`git status` clean after the script).

## Trust, size, answers, pilot bytes

- Trust: `uv run python tools/trust_map.py --check` "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0"
  (PASS). light-lane: NOT (870 lines > 150), so the trust_mutants sweep ran (`mac-pytest.sh --trustmut`): 0
  definitions, 0 mutants, exit 0 (trust-mutants.json, base 12cb72fa55). No R16 growth, no FOLLOW-UPS.md row.
- SIZE: 283 product (rsp_vocabulary.py 240, stage0.py 41, accounting.d1.txt 2), 407 tests (new file 395, three
  edited files 12), 294 other hand-written lines (REPORT 219, DELTA.md 13, mutants.json 62); generated: 60 added
  lines in 7 files plus trust-mutants.json (`git diff --numstat $(git merge-base HEAD main)`).
- Answers the change touches (the audit's answers_touched, per row, in the table above; K = 126 keyed): the widest
  rows are x4 (49 of 126, now reaching fewer blocks), x13-x21 (40 of 126 each) and the D2/D3 rows (17 of 126). Later
  reads re-pin at the merge commit.
- Pilot bytes: environment.d1.json grows from 54,788 to 74,627 bytes (+19,839, `wc -c` on main and HEAD); the D2/D3
  legends add about 2.8 KB more to the D2D3 unit. Estimate only: about 53 pair groups (some 110 unit pairs) move from
  NOT CARRIED / PARTIAL to CARRIED at the next counted read; nothing is claimed before a pilot audit. The largest
  touched legends (`listed` about 2.7 KB, `external_review_process` 1.3 KB) feed the planner's C5 131,000-byte check,
  which was not run here.

## Tests run

- Selected run 1 (`mac-pytest.sh --select`, tree 132d07774b): 2 failures, both from this change:
  test_english_statement_blocks.py::test_the_route_fixtures_are_recorded (route-cases.jsonl embeds the RSP
  environment: regenerated) and test_rsp_fidelity_fix.py::test_facts_repair_each_retagged_entry_is_whole_in_its_blocks_carrier
  (counterfactual widened). Both then passed locally (2 passed).
- Selected run 2 (after those fixes, tree 3c5eba104c, 385 units): 1 failed, from this change:
  test_safetyfw_usecases.py::test_rsp_every_byte_is_in_exactly_one_unit (`build_document.py --check`: coverage.json
  records the built D1 document's SHA-256, which the legends feed). coverage.json was regenerated by the tool (row
  above); then that test and the other coverage readers passed (`pytest tests/test_safetyfw_usecases.py -k "rsp and
  (coverage or measure or byte or gaps or units)"`: 4 passed). Every other selected test passed in run 1 or run 2.
- `uv run python tools/gate_collection.py --check --prebuilt`: 103 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- Not run: the full gate (the chain runs it on the final HEAD); the deferred slow files the selection names.

## Notes for the DRI

- The same source sentence is written once per legend key (up to 6 keys): the counter counts only a block's own
  predicates' legends, so one shared string cannot reach those blocks. A later shared-legend mechanism could fold
  them; it is a counter/design question, not this item's.
- x62/x63 are a counter rule (computed legends are shown, not counted), not a reader gap: dropping them avoids copying
  ROW_PLANS / ROW_ARGUMENTS into a second literal (one-owner rule).
- x28 names f25-delay/f25-meet, which do not use `in_the_lead`; x27 carries the same sentence there on `highly_capable`.
- Conservative choices: no candidate of my own carried (x4's five `crossed` blocks left to the follow-up); the seal
  regeneration also renews the safety-framework entry because `--check` listed it stale on main.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer or schema is added or changed.
2. PASS: deliverables 0-3 delivered (table above; commits 998b7aef7e, 9318bcf909, 229b965ab7, c29e93d867 and the docs commit;
   tests/test_defs_repair_anthropic_rsp_1119.py); no Python copy of a Lean decision, no permanent report test.
3. PASS: 7 seeded bugs, each failing a named test (mutants.json); trust_mutants 0 definitions (trust-mutants.json).
4. N.A.: no Python/Lean/Rust decision path changed; RSP answers unchanged (selected runs: test_rsp_fidelity_fix,
   test_safetyfw_usecases pass).
5. N.A.: no field is read from a Lean answer.
6. PASS: rebased onto main 12cb72fa55 and regenerated; the gate is the chain's, on the final HEAD.
7. PASS: no DELTA row, trust +0 (`tools/trust_map.py --check`).
8. PASS: DELTA.md states no user-visible VE change; legend text and identity digests listed there.
9. PASS: the selected runs selected and ran the changed tests (test_rsp_fidelity_fix,
   test_english_statement_blocks, the new file); run 1 caught both real breaks.
10. N.A.: no Lean statement or proof.
11. N.A.: no budget, limit or deadline.
12. N.A.: no evaluator; legend text only (no timed path changed).
13. PASS: no test removed (`gate_collection.py --check --prebuilt`: 0 removed, 0 stale, 0 malformed).
14. PASS: both directions: D3's legend is asserted present for "publication within" and absent for D4/D5
   (test_d3_coverage_date_legend_carries_the_scope_sentence); each claim above names its command. Spec re-read:
   each quote against rsp-3.4.txt (test_each_sentence_is_in_the_pinned_source, 1 occurrence each); carrier rule
   against METHOD-READDOCS.md amendments 1-2 (shown and counted, not citation-led).
15. PASS: overclaim grep done ("every"/"no" claims cite tests above); no deliverable cut; every new check has a
   mutant (M1-M7); no limits involved.

FOLLOW-UP: defs-repair-anthropic-rsp-x4b-1119 carry the left-column sentence (x4) for the five blocks that use `crossed`, not `listed` (f5-evidence-default, f5-evidence-strict, highly-capable-t4, t4-only-if, t4-suff)
