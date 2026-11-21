# defs-carried-gate-stage1-1119: REPORT (stage 1, detection in report mode)

**Status:** built; review F1-F3 (`02cd654`) fixed (section 9), ready for recheck; no DRI signature needed (no DELTA row, trusted Lean growth +0).
**Measured at:** VE main `0ce720e46b` (the merge base; `usecases/` identical to main), the audit pin `3d6b459df4`, and, for the FSF/RSP repairs, each repair's merge base.
**Numbers:** known cases: IN-SAMPLE (the design's own cases, the ones the tool was built against): 60 of 61 findings detected (363 of 389 pairs; 26 pairs not reached, each named below); out-of-sample recall and an independently judged false-alarm rate: docs/infra/defs-carried-oos-measure-1119/REPORT.md. All documents: 472 pairs flagged; a hand check of 24 found 10 false alarms and 2 new true findings (both P2-kind). Run time 8.1 s for all 15 documents (bar 60 s).
**Changed:** new `tools/defs_carried.py` (report-mode checker), `tools/defs_carried_counter.py` (counter code copied byte for byte), `tools/defs_carried_known.py` (fixture builder), `tests/test_definitions_carried.py`, fixtures under `tests/data/defs_carried/`, and `tests/history-dependent.json` (regenerated).
**Open:** none blocking. Stage 2 waits for the orchestrator's ruling on these numbers (row defs-carried-gate-stage2-1119).

Design: manage-agents `reviews/defs-carried-gate-1119/DESIGN.md` r3, sections 1, 2, 5 and 6. Stage 1 only: there is no ledger, baseline, waiver, expiry or done-row check, and no fingerprint, approval or edit-digest code. Nothing can block a merge, and nothing outside this VE branch was changed. The tool exits 0 whatever it finds; only a usage error exits 2.

## 1. The stage-1 numbers (MEASURED)

### a. The 61 known cases (T1 raw detection)
Command: `python3 tools/defs_carried.py --known-trees`. It reads each case at its recorded tree by blob id: the pin `3d6b459df4` for the audit rows and D7, and each repair's merge base for F1-F9 and R1. Evidence: `evidence/t1-known-trees.json`.

| group | findings | detected | pairs | pairs detected | NOT CARRIED | FRAGMENT | ELSEWHERE | UNSHOWN |
|---|---|---|---|---|---|---|---|---|
| P1 rows | 52 | 51 | 224 | 202 | 196 | 28 | 0 | 0 |
| FSF/RSP repairs (F1-F3, F5-F9, R1) | 9 | 9 | 90 | 90 | 53 | 23 | 5 | 9 |
| **the 61 known findings** | **61** | **60** | 314 | 292 | | | | |
| P2 rows (where they apply) | 20 | 20 | 70 | 68 | 43 | 27 | 0 | 0 |
| UDHR D7 (rowless) | 1 | 1 | 5 | 3 | 5 | 0 | 0 | 0 |
| all known cases | 82 | 81 | 389 | 363 | 297 | 78 | 5 | 9 |

- **No known case is called CARRIED or CARRIED-ASSUMED.** "Detected" means the adapter reaches the (rule, term) pair (or the rule is UNPARSED) and the verdict is below CARRIED-ASSUMED. A finding is detected when at least one of its pairs is.
- **Misses: 26 pairs, 1 finding.** Each pair is not reached by the adapters (its verdict is still NOT CARRIED). The test pins each one with its reason:

| known case (pairs) | reason |
|---|---|
| defs-eligibility-2 "qualifying week", 20 of its 49 rules | No VE term. These 20 rules use no predicate whose legend names the qualifying week (B1 is a date fact; the audit row says "needs rule line"). The other 29 pairs are reached through the lexical match of "qualifying week". |
| defs-udhr-pilot-1, u052 (1; **the one missed finding**) | u052 uses `asylum_right_covers_case` only in its reading sets. Reading sets are not a dependency source: a reading holds a meaning_id hash and `content: null`. |
| udhr D7, u112 `exercise_of_declared_right` and u114 `declaration_implies_destructive_right` (2) | The same reason: these predicates are used only in reading sets. The other 3 D7 pairs (`rights_and_freedoms_set_forth`, an open term) are reached. |
| defs-asimov-extended-7, R16 (1) | R16 uses `lawful_action`, which R14 derives from `breaks_first_law`. The adapter follows rule cross-references ("exception to rule 8") but not a derived predicate back to the rule that derives it. |
| defs-asimov-laws-2, R9 (1) | R9 names `harms_humanity`, not `breaks_zeroth_law`. The audit paired them by meaning (the Zeroth Law's content). |
| defs-claude-constitution-pilot-1, u0036.s05 = R1 (1) | The unit's open meaning names `genuine_ambiguity` only. The sort `claude_instance` is not among the terms of that open term or of any predicate the unit names. |

- **Class checks.** At F3's base the Glossary's Safety Cases sentence sits whole on the `safety_case` legend, which f12/f13 do not use: ELSEWHERE, the FSF F3 lesson, computed mechanically. F6's SL2+ text sits only in a `## measures-sl2plus` header: UNSHOWN. At main, F5 is merged and its two pairs compute CARRIED, which is the expected after-state.
- **Agreement with the audit's verdicts (P1 and P2 pairs).** NOT CARRIED 126 of 126 agree. Audit FRAGMENT: 28 FRAGMENT, 59 NOT CARRIED (the carried run is under 4 words). Audit ELSEWHERE: 11 NOT CARRIED (the audit's ELSEWHERE meant "formalised on an unused predicate"; the words are not there whole). Audit FORMALISED/PARAPHRASE: 27 FRAGMENT, 43 NOT CARRIED. That is expected, because the verbatim check cannot see a formalisation. PARTIAL fires only when every clause's content words occur contiguously; no known case meets that.

### b. All documents
Command: `python3 tools/defs_carried.py` (main) and `python3 tools/defs_carried.py --ref 3d6b459df4` (pin). Evidence: `evidence/summary-main.txt`, `evidence/summary-pin.txt`, `evidence/findings-tables.md`.

Scope:
- The 12 non-FSF documents are checked against the marker-grep inventory (detector b), with terms linked by detector (c).
- FSF, RSP and PF are checked on the 9 repair terms only (coverage tier PARTIAL), so the marker grep is not run on them.
- The 5 out-of-scope documents have no frozen source: agent-policy (an authored policy whose sources.md pages are not in the repository), cedar-attributes, gatekeeper-exemption, webapp-commands (fixtures with no source document), and closure-induction (its premises are math-mini-paper T9/T9e plus two policy fixtures).

Document-level findings:
- **VISIBILITY-UNESTABLISHED:** one on each of the 12 non-FSF documents. Their surface is assumed, never counted.
- **UNPARSED:** 32 rules (bluedot-grant 6, claude-constitution-pilot 3, news-article 1, question-answering 2, udhr-pilot 20). Each is printed with "dependencies unknown: any of the document's N declared terms" and the candidate list (terms no parsed rule reaches). The 20 UDHR rules are exactly the design's "20 specified units".

Pair findings at main (the auto inventory; known-case pairs are counted in a, not here). The pin gives identical counts, because no translation, rule or legend file of these documents changed between the pin and main.

| document | rules | UNPARSED | marker hits (link no term) | pairs flagged | NOT CARRIED | FRAGMENT | s |
|---|---|---|---|---|---|---|---|
| asimov-laws | 13 | 0 | 1 (1) | 0 | 0 | 0 | 0.02 |
| asimov-extended | 29 | 0 | 5 (5) | 0 | 0 | 0 | 0.05 |
| birthright-citizenship-debate | 7 | 0 | 7 (7) | 0 | 0 | 0 | 0.01 |
| bluedot-grant | 69 | 6 | 16 (8) | 61 | 61 | 0 | 0.08 |
| claude-constitution-excerpt | 11 | 0 | 10 (9) | 1 | 0 | 1 | 0.03 |
| claude-constitution-pilot | 19 | 3 | 140 (135) | 36 | 34 | 2 | 0.22 |
| eligibility | 49 | 0 | 117 (98) | 364 | 266 | 98 | 4.40 |
| math-mini-paper | 19 | 0 | 122 (119) | 9 | 9 | 0 | 0.07 |
| news-article | 26 | 1 | 5 (5) | 0 | 0 | 0 | 0.02 |
| question-answering | 10 | 2 | 0 | 0 | 0 | 0 | 0.02 |
| udhr-pilot | 50 | 20 | 4 (3) | 1 | 1 | 0 | 0.04 |
| us-constitution-14th-s1 | 4 | 0 | 8 (8) | 0 | 0 | 0 | 0.01 |
| safety-framework | 62 | 0 | not run | - | - | - | 0.71 |
| anthropic-rsp | 86 | 0 | not run | - | - | - | 0.97 |
| openai-preparedness | 102 | 0 | not run | - | - | - | 1.46 |
| **total** | 556 | 32 | 435 | 472 | 371 | 101 | 8.11 |

No auto pair computes PARTIAL, ELSEWHERE, UNSHOWN, OVERSIZE, CARRIED-ASSUMED or CARRIED: a marker passage is a whole source sentence, and no legend holds one whole. OVERSIZE has no case: the largest lower bound on a prompt (the pinned source plus the largest unit render) is 85,611 bytes for PF, 73,304 for RSP and 66,999 for FSF, against ARG_LIMIT 131,000.

**Hand check: 24 findings outside the known cases**, read against the source and the rule's shown surface (`evidence/hand-check-sample.txt` has each passage, legend and surface). The 472 flagged pairs group into 120 distinct (marker entry, term) links, 86 of them outside the known cases. The sample covers all 6 documents that have links.

| # | doc, entry -> term | judgement |
|---|---|---|
| S1 | bluedot M2 (source.md:8, "(VEX)") -> vex | TRUE, **new** (see below) |
| S2 | bluedot M3 (:11, "(VEX)") -> vex | TRUE, the same new finding as S1 |
| S3 | bluedot M9 (:35, "unresolved") -> unresolved | FALSE ALARM: a quoted word in a sentence that does not define it (the audit: no source definition) |
| S4 | bluedot M9 -> proof_label | FALSE ALARM: a name inside a guessed phrase; the sentence is a risk statement, not a definition |
| S5 | pilot M24 (Operators:) -> operator_input | TRUE, already a known finding (pilot-3: the same rules and passage, another term naming "operator") |
| S6 | bluedot M9 -> false_confidence | FALSE ALARM: as S4 |
| S7 | bluedot M10 (:43, G10 matched-cost) -> matched_cost | TRUE, **new** (see below) |
| S8 | bluedot M10 -> proof_production | FALSE ALARM: a term that is a component of another term's definition |
| S9 | pilot M24 -> operator_input_permitted | TRUE, already known (pilot-3) |
| S10 | pilot M25 (Users:) -> instruction_deceptive_tactics_harming_users | TRUE, already known (pilot-3's passage covers the Users entry) |
| S11 | pilot M91 ("(CSAM)") -> child_sexual_abuse_material | FALSE ALARM: the legend carries the content inflected ("generating" for "Generate"); 5 of 6 words |
| S12 | pilot M128 (the name "Claude") -> csam_generation_permitted_for_claude | TRUE, already known (pilot-1 covers that rule, R16) |
| S13 | excerpt M10 (source.md:43) -> violates_hard_constraint | FALSE ALARM: commentary quoting a phrase; it defines nothing |
| S14 | math M55 (:391, "least") -> least | TRUE, already known (math-5); the passage is cut at the line end |
| S15 | udhr M4 (Art. 29(2)) -> determined_by_law | FALSE ALARM: the sentence states the rule itself |
| S16 | eligibility M10 (Sch4:334) -> reached_pa | FALSE ALARM: an amendment to another Act's definition |
| S17 | eligibility M12 (Sch4:344) -> applicant_pa_date | TRUE, already known (eligibility-1, another term on R2) |
| S18 | eligibility M38 ("partner" means) -> partner_from | TRUE, already known (eligibility-3, another term on R7b) |
| S19 | eligibility M39 ("pensionable age") -> applicant_pa_date | TRUE, already known (eligibility-1) |
| S20 | eligibility M41 ("qualifying week" means) -> home_start_dated | TRUE, already known (eligibility-2) |
| S21 | eligibility M42 ("relevant benefit" means—) -> R4 gloss | TRUE, already known (eligibility-13, P2); the list is cut at the line end |
| S22 | eligibility M79 (explanatory note) -> has_rb | FALSE ALARM: a mention of the defined term |
| S23 | eligibility M93 ("See section 7A(6)(d)") -> has_rb | FALSE ALARM: a pointer to a definition outside the source |
| S24 | eligibility M101 (wfp-print:33, "(ESA)") -> R4 gloss | TRUE, already known (eligibility-15, P2; another place the same abbreviation is introduced) |

**Result: 10 false alarms and 14 true findings.** Of the true findings, 12 are already known (the same definition on another term or passage of a known row) and 2 are new.

The false alarms have six causes:
- mention or commentary rather than a definition: S3, S13, S22;
- a name matched inside a guessed phrase: S4, S6, S8;
- the rule's own sentence: S15;
- amendment text: S16;
- a definition by reference outside the source: S23;
- an inflected carrier: S11.

**New true findings.** These are candidate repairs, listed only and not repaired here; both are of the P2 kind (optional).
1. **bluedot-grant, VEX on u007, u056, u074.** The VEX definition (G1) is not carried on these rules: the legend of `vex` is "VEX". The audit table records these pairs as PARTIAL (FORMALISED) but filed no row; row defs-bluedot-grant-1 lists only u009, u039, u059, u076 and u090.
2. **bluedot-grant, matched-cost comparison (G10) on u013, u018, u024, u079**, the rules that use `matched_cost`. The `matched_cost` legend paraphrases the sentence ("count authoring, formalisation, proof production, ..."); the audit row defs-bluedot-grant-9 covers u062 only.

### c. Lexical matcher, UNPARSED, run time
- **Lexical bar (section 5): met.** Aliases are off, and the only equivalence is a plural fold. Of the 98 known (entry, term) pairs that have a defined phrase, 66 have a phrase that occurs as tokens in the term's identifier or legend (or a multi-word identifier that occurs in the phrase). **The matcher links 66 of those 66 (100%), F3 included** ("Safety Cases" -> `governance_found_acceptable_with_safety_case_where_ccl_reached`). Recall on the other 32 is **0 of 32**. These are alias-only pairs, listed in `evidence/lexical-recall.json`, for example:
  - "severity classes and order" -> `less_severe_competitor`;
  - "Rule 1" -> `breaks_first_law`;
  - "couple" -> `partner_of`;
  - "deception" -> `instruction_deceptive_tactics_harming_users`;
  - "rights and freedoms set forth in this Declaration" -> `exercise_of_declared_right`.
- **UNPARSED rules:** 32 (b above).
- **Run time (MEASURED on this VM, 2026-11-19):**
  - all 15 documents at main: 8.11 s (the run's own clock; 8.3 s wall);
  - all 15 at the pin: 8.46 s;
  - the 389 known cases at their trees: 7-11 s;
  - slowest document: eligibility, 4.4 s, which compares its 117 marker passages with the 40 KB executed-code carrier.
  - All within the 60 s bar.

### d. Statement for stage 2 (ESTIMATE unless marked)
- **Trusted base: +0 Lean lines.** Stage 1 is MEASURED with `tools/trust_map.py --check` on this branch: K +0, S +0, trusted +0. Stage 2 is expected to be +0 as well, because it adds Python and data only and trust_map counts Lean.
- **Python and test lines (ESTIMATE):**

| stage-2 part | where | Python lines | test lines |
|---|---|---|---|
| ledger loader, per-record `fp`, guards (a)-(f), UNMATCHED/STALE/CONTRADICTED/NO-VE-TERM, coverage rule | tools/defs_carried.py | 450-600 | 300-400 (T3, T4, T4i) |
| baseline, waivers, RETIRE, `out_of_source`, scoped done-row/expiry checks | tools/defs_carried.py | 200-300 | 200-300 (T6, T7, T10) |
| edit digests, approvals, light path, weakening list | manage-agents review-ready.py `--defs-check` | 250-400 | 200-300 (T6m) |
| merge-train.sh call | manage-agents merge-train.sh | 5-15 | covered by T6m |
| conversion of the audit into 12 ledgers plus 3 partial ones | a script like tools/defs_carried_known.py | 150-250 | 50-100 |

  The ledgers themselves are reviewed data, several thousand JSON lines, not code. The design's own total for this stage-2 work (section 6) is 0.7-1.0M CW, plus 0.6-1.0M for the conversion and 0.3M for its review.
- **What stage 1 already gives stage 2:**
  - the adapters, the surface, the verdicts and `source_norm`;
  - the known-case fixture, which serves as T1 and as the seed of the ledgers' `governed` records;
  - the selection function;
  - the byte pin of the counter code.

## 2. What was built
- **`tools/defs_carried.py`** (report mode).
  - Trees: a checkout, a commit (`--ref`), or blobs.
  - Per-format adapters:
    - `rules.ve` (rules.ve with base.ve; the rules a header names, "exception to rule 8" or "exception to rules 8, 9", and a precedence sentence "Rule 3 takes precedence over rule 1." are followed transitively, read with VE's own header grammar `ve.surface.softnorms.parse_header_options`; a header that grammar does not read leaves the rule UNPARSED, never short of a reference);
    - `claims.ve` (with countermodel premises and conclusions as T1-T5);
    - `.ve.md` units: ast, norm, quantity or a body fence; an `open` meaning; the speaker of an attributed unit; `specified` with no body is UNPARSED;
    - `rules.json` with `translation.py` as executed code: comments, docstrings and the vocabulary's own legend strings stripped, so an unused predicate's legend never carries through the code;
    - `theorems` (premises plus conclusion, with the environment that verdict.json names);
    - `counter` (FSF/RSP/PF: `rule_blocks`, `used_predicates`, `omit_carrier_texts` and `seq_unit_legends`, all byte-pinned).
  - The carrier surface of section 2 (narrow default, or the counter's own), with VISIBILITY-UNESTABLISHED on every non-FSF document.
  - `source_norm`: the pinned `omit_norm` after stripping markdown emphasis, list and quote markers, header marks, link and image syntax, math italics and the counter's citations.
  - The verdict table, worst first, with the longest carried run as a diagnostic (token-level longest common substring).
  - The marker grep (detector b, amendment-2 regex plus bold or numbered lead-ins and table rows) and the lexical matcher (detector c). Both print their hits in the JSON.
  - The selection function (`--select PATH...`).
  - Output: one JSON report (`--json`) and one short text summary per document (`--summary-dir`). Exit 0 always.
- **`tools/defs_carried_counter.py`.** It holds 11 statements copied byte for byte: `omit_norm`, `rule_blocks`, `seq_unit_legends`, `used_predicates`, `legend_raw`, `_omit_strip_comments`, `_omit_legend_segments` and `omit_carrier_texts` from `uc-audit.py.reads-1119` (sha256 `d618d963...`), the `OMIT_CODE` and `OMIT_CODE_SECTION` tables, and `ARG_LIMIT = 131000` from `omission-seq-read.py`. Each is hashed against `tests/data/defs_carried/counter_pin.json`. The module adds four functions of its own: three read shims and a narrowed `omit_code_parts` (see the limits).
- **`tools/defs_carried_known.py` and `tests/data/defs_carried/known_cases.json`** (deliverable 2): see section 3.
- **`tests/test_definitions_carried.py`**: 60 tests (42 at build; the review fixes removed 1 and added 19, section 9).
  - The condition tests:
    - T1 (every known case is not carried at its tree, or a named miss);
    - the 61-finding check;
    - the F3/F6 classes;
    - report mode exits 0 with findings.
  - T5 surface mutants: a constant legend, a sort legend, a verbalisation, an unused predicate's legend, a comment, an open-term factor, a `## ` header, a constant table, ELSEWHERE, OVERSIZE, and CARRIED-ASSUMED rather than CARRIED.
  - T9 equivalences: curly quotes, a line-break hyphen, a citation strip, a bold lead-in.
  - Selection (Codex B11): an edit to asimov-laws/source.md selects asimov-laws and asimov-extended; an edit to tools/defs_carried.py, the counter copy or the fixture selects all 15.
  - The detectors, and the lexical bar.
  - UNPARSED output.
  - Normalisation edge cases.
  - Malformed JSON (7, true, null, [], {}, mistyped nodes): no crash, and never a pass.
  - A use-case directory with no adapter and no out-of-scope reason is listed in the report (`unscoped_use_cases`) and printed, and the tool still exits 0; no test reads the live `usecases/` directory, so a later item that adds a use case is never blocked (review F1).
  - The counter byte pin, and the fixture's counts and verbatim passages.
- **`tests/history-dependent.json`**: regenerated by `tools/history_tests.py --write`, because the test reads blobs with git. `tests/test_lineage_lint.py` and `tests/test_history_tests.py` pass: the blob ids come from saved data under a `blob` key, which is content-addressed.

## 3. The known-case fixture (deliverable 2)
`python3 tools/defs_carried_known.py --audit tests/data/defs_carried/audit --repo <VE repo> --out tests/data/defs_carried/known_cases.json` gives **389 cases**, one per (document, rule, term, passage).

Inputs:
- the 72 audit rows (52 P1, 20 P2) from `rows-*.tsv`, copied verbatim into `tests/data/defs_carried/audit/`;
- the rowless UDHR D7 (5 pairs: u100b, u112 x2, u114 x2), from the udhr-pilot page's table;
- the 9 FSF/RSP repairs, from their branches. Each repair's appended legend or `stage0.py` string is cut into the source passages it adds that are at least 10 words long; passages the legend already held are dropped. The term is the predicate (F1: the level constant the legend names; R1: the `HARMS` key `existential_threats`).

Resolution:
- Wildcards and ranges are resolved at the pin: `R5b.*`, `R14.1-R14.3`, "all 49", `claims.ve:5`, and the pilot page's R1-R19 mapped to unit ids.
- The term is the row's carrier key when the pin declares it. Otherwise it is the identifier the row's term column names, or the term of the rule that the lexical matcher links to the row's phrase.

**Count: 389 cases**: P1 224, P2 70, F1 14, F2 8, F3 5, F5 2, F6 36, F7 18, F8 3, F9 3, R1 1, D7 5. The 61 known findings are the 52 P1 rows and the 9 repairs.

**Quotes that are not in the source as written: 18, each re-cut verbatim from the source.** Each is listed in the fixture's `recut` list with the words it dropped. No model judgement was used: the cut keeps the source's own runs of at least 3 words.
- **Wrapper dropped (6).** asimov-laws-1/2/3 and asimov-extended-7/8/9 drop `Source ("Runaround", 1942), Rule 1` / `Source, Zeroth Law` / `Source, Rule 2`; the passage is the quoted law.
- **Wrapper dropped (1).** udhr-pilot-1 drops `Article 14(1):`; the passage is "Everyone has the right to seek and to enjoy in other countries asylum from persecution."
- **Split into the source's separate passages (11)**, because the row joined non-adjacent passages:
  - claude-constitution-pilot-3 and -4 (Operators/Users + the role sentence), -7 (two passages), -9 and -10 (three), -13 (three), -15 (three);
  - eligibility-1 (the S1 definition + Sch4 para 1 + its rules), -2 (S1:40 + wfp-print:38), -10 (S1:27 + S.I. 2005/3360 reg. 2(4)), -11 (two wfp-print sentences).
- **D7's passage** is Articles 3-27 cut whole from the body, as the udhr-pilot page says ("The target is ... Articles 3-27").

## 4. Seeded bugs (MEASURED; `mutants.json` has file and test keys)
Each bug was planted alone, its tests were run, and the file was restored with `git checkout`. All 28 made a test fail (19 at build, 9 for the review fixes). Python is the only product language changed; there is no Lean or Rust change.

| behaviour | bug planted (file) | failing test |
|---|---|---|
| adapter: rules.ve dependency path | rule-reference path terms dropped (tools/defs_carried.py) | test_t1_every_known_case_is_reported_not_carried_or_a_named_miss |
| adapter: .ve.md speaker | attributed-unit speaker ignored (tools/defs_carried.py) | the same T1 test |
| adapter: UNPARSED | `specified` units without body skipped (tools/defs_carried.py) | test_unparsed_rules_print_the_full_set_and_candidates |
| carrier surface: unused legend | unused predicates' legends shown (tools/defs_carried.py) | test_t5_a_definition_off_the_shown_surface_is_not_carried[unused] |
| carrier surface: header | counter `## ` header shown (tools/defs_carried.py) | test_t5_open_term_factor_and_header_and_constant_table |
| verdict CARRIED-ASSUMED | non-counter carried as CARRIED | test_t5_the_shown_surface_carries_but_only_as_assumed_outside_the_counter |
| verdict ELSEWHERE | other rules' surfaces not searched | test_t5_elsewhere_and_oversize |
| verdict UNSHOWN | unshown fields not searched | test_t5_a_definition_off_the_shown_surface_is_not_carried[constant] |
| verdict OVERSIZE | oversize ignored | test_t5_elsewhere_and_oversize |
| verdict PARTIAL | clause map disabled | test_fragment_partial_and_not_carried |
| verdict FRAGMENT / NOT CARRIED | FRAGMENT_MIN 4 -> 40 | test_fragment_partial_and_not_carried |
| source_norm: markdown | md_strip removed | test_t9_equivalences_carry[Operators:...] |
| source_norm: citations | cite_strip disabled | test_t9_equivalences_carry[A careful robot (1.3.2)...] |
| lexical matcher (c) | identifier split disabled | test_lexical_matcher_finds_phrases_inside_identifiers_f3 |
| marker grep (b) | lead-in match disabled | test_marker_grep_hits_definitions_lead_ins_and_table_rows |
| selection: select-all | SELECT_ALL check removed | test_selection_shared_input_selects_every_reader |
| selection: shared input | reads outside the document's directory ignored | test_selection_shared_input_selects_every_reader |
| review F1: unscoped use case listed | `unscoped_use_cases` returns [] (tools/defs_carried.py) | test_a_new_use_case_is_reported_never_failed |
| review F2: every header reference read | only the header's first rule kept (tools/defs_carried.py) | test_a_multi_rule_header_puts_every_named_rule_on_the_path, test_rule_header_refs_read_every_header_ve_renders |
| review F2: unreadable header UNPARSED | an unreadable header gives no references instead of UNPARSED (tools/defs_carried.py) | test_a_header_the_grammar_does_not_read_is_unparsed_never_short |
| review F2: precedence sentence | precedence sentences dropped (tools/defs_carried.py) | test_a_precedence_sentence_puts_its_target_on_the_path |
| review F3: repair commits pinned | `repair_cases` resolves the branch against main (tools/defs_carried_known.py) | test_a_rebuild_resolves_no_branch_and_no_main |
| review F3: resolver not reached | `repair_commits` returns the branch's commits today (tools/defs_carried_known.py) | test_a_rebuild_resolves_no_branch_and_no_main |
| review F3: trees, not commit labels | `repair_cases` reads the base commit label instead of its pinned tree (tools/defs_carried_known.py) | test_a_rebuild_resolves_no_branch_and_no_main (test_lineage_lint does not see this one: the label flows through a return value) |
| review F3: GitTree reads a tree id | a tree id no longer accepted (tools/defs_carried.py) | test_git_tree_reads_a_commit_or_a_tree_by_id |
| review F3: audit pin a full id | PIN shortened to `3d6b459df4` (tools/defs_carried_known.py) | test_the_builder_pins_every_commit_the_fixture_records |
| report mode | exit 1 when a case is detected | test_report_mode_exits_0_with_findings |
| counter byte pin | one character changed in the copied omit_norm (tools/defs_carried_counter.py) | test_the_counter_code_is_a_byte_copy_of_the_pinned_source |

## 5. Checks run
- `tests/test_definitions_carried.py`: 42 passed, locally.
- `tests/test_lineage_lint.py` and `tests/test_history_tests.py`: 40 passed.
- `tools/regen_generated.py --check`: history-tests was stale and is now regenerated. The codemap warning says it is regenerated on merge.
- `tools/trust_map.py --check`: PASS, trusted +0.
- `tools/trust_mutants.py --plan`: 0 Lean definitions and 0 mutants, so no sweep is needed. The light lane says NOT, because the fixture JSON counts as changed lines.
- Selected run: `mac-pytest.sh --select -- --base 0ce720e46b --run` on commit 26c2114b72 (fallback runner ve-cloud-2) exited 0, 0 failed; tests/test_definitions_carried.py exit 0 in 28.2 s. The full gate is run by the chain on the final HEAD.
- **No DELTA.md.** This change makes no user-visible change to the VE checker: no Lean, no `ve/` code, no verdict, wording, field, fault order or trust budget. The verdict classes here belong to this infra check (DESIGN r3).

## 6. Stated limits (stage 1)
- **Adapters.** The dependency parse is lexical: identifier tokens, the counter's `used_predicates`, AST atoms. It is not the VE parser, except that rules.ve rule references are read with VE's header grammar (`parse_header_options`). A derived predicate is not followed back to the rule that derives it (the asimov-extended-7 R16 miss), and reading sets are never a dependency source (by design).
- **Narrowed code unit.** The counter's D2D3 code unit is copied without its definition closure (`omit_code_closure`). The narrower unit can only miss a carrier, never add one.
- **OVERSIZE lower bound.** OVERSIZE uses a lower bound on the step-1 prompt: the pinned source's `text_bytes` plus the unit's render. The full prompt depends on the answer plan, which stage 1 does not read.
- **CARRIED is strict.** CARRIED needs the passage whole as a character substring after `source_norm`, in one shown run. Off the rule's surface, ELSEWHERE and UNSHOWN accept the passage's words whole and in order with punctuation ignored. Neither of those passes.
- **Marker passages.** A marker passage is one sentence or one line, so a definition that continues on the next line (a list, the math prose) is cut short (S14, S21). One-word phrases that the grep guesses are matched against names only.
- **Not checked.** The read-time seat class DEF/WHAT. CARRIED is necessary, not sufficient (the design's stated limit).

## 7. Notes for the DRI
- R19 (no new verdict words) does not apply as far as I can tell. It covers VE service modes and verdict words of the checker, and this item adds an infra report tool whose classes the approved DESIGN r3 names. Nothing here is a VE route or mode.
- Q6, the surface of the non-counter formats: every one of the 12 documents carries VISIBILITY-UNESTABLISHED, and no known case relied on CARRIED-ASSUMED. The two pilot and two UDHR rows aimed at unshown fields (sort/constant legends, open-term factors) will compute UNSHOWN after their repairs until Q6 is ruled. The T5 tests show this for a sort legend and an open-term factor.
- Conservative choices taken without asking:
  - CARRIED is character-level, not word-level;
  - the vocabulary's own legend strings are stripped from executed code;
  - one-word guessed phrases match names only;
  - FSF/RSP/PF are not marker-grepped (PARTIAL tier).

## 8. Notes
- **Detector noise to reduce in stage 2**, measured in 1b: mentions and pointers ("the definition of X", "See section N for the definition of X") and amendment text. A rule that drops a marker hit whose quoted phrase follows "definition of" would remove S16, S22 and S23.
- **Repair commits.** `tests/data/defs_carried/repair_pins.json` records each repair's tip, base and merge as full commit ids (labels the fixture records, never given to git; a test checks they equal the fixture's) and the content-addressed tip and base trees, which `tools/defs_carried_known.py` reads. A rebuild names no branch, repair commit or `main` to git, so it gives the same fixture after main moves, after a repair merges, after a branch is deleted and after the history is rewritten (review F3; a rebuild on 2026-11-19 gave a byte-equal fixture while five repair tips and F9's merge had moved). It still needs the pinned trees in the repository it reads. `--resolve-branches` prints how the branches resolve today next to the pins, for a deliberate refresh; it changes nothing. The audit pin `PIN` stays a commit (now a full id), as before: the pin's report names its commit.
- **SIZE:** 1,843 product (tools/defs_carried.py 1,251, tools/defs_carried_known.py 524, the counter module's own 68 lines; plus 178 lines copied verbatim), 382 tests, 281 other hand-written lines (this REPORT). Generated or copied data, not counted: known_cases.json, counter_pin.json, the audit copies, the evidence files and history-dependent.json.
- **COST: ESTIMATE**, since this session has no token meter. About 2.5-3.5M CW: checker, adapters and tests 1.8-2.4M; known-case conversion 0.4-0.6M; measurement, hand check and report 0.3-0.5M. The design's estimate was 1.5-3M plus 0.6-1.0M.

## Self-review against BUILDER-CHECKLIST
1. Typed and contained Lean answers: N.A. (no Lean answer relayed).
2. Every deliverable built, no rule broken: PASS. Deliverables 1-4 are present; nothing under manage-agents was changed; no legend or rule was edited. Tests: test_t1_every_known_case_is_reported_not_carried_or_a_named_miss, test_report_mode_exits_0_with_findings.
3. Tests can fail: PASS. 28 seeded bugs (section 4, mutants.json).
4. Python, Lean and Rust agree: N.A. (Python only).
5. R8 binding, undeclared names refused: N.A. (no relay). Known cases bind to declared rules and terms, with misses named: test_t1_every_known_case_is_reported_not_carried_or_a_named_miss.
6. Gate evidence matches the final HEAD: PASS. The full gate runs in the chain on the final HEAD, and the evidence numbers were saved from this branch.
7. No unsigned item: PASS. No DELTA row, no reserved signature.
8. User-visible change in DELTA: N.A. (no VE product change; section 5).
9. Test selection finds the tests: PASS. A new test file is selected as changed; history-dependent.json is regenerated; test_selection_shared_input_selects_every_reader covers the tool's own selection.
10. Lean statements: N.A.
11. Budgets and limits fail closed: PASS. OVERSIZE against the pinned ARG_LIMIT (test_t5_elsewhere_and_oversize); malformed input never passes (test_malformed_inputs_never_crash_and_never_pass).
12. No CPU or memory regression: PASS. A new tool only; 8.1 s for all documents. The test file runs in about 30 s.
13. Removed or renamed tests: one test of this branch (never on main) was removed for review F1: `test_every_use_case_is_checked_or_named_out_of_scope` compared the live `usecases/` with the tool's lists, a merge blocker for any later use case. It is replaced by `test_a_new_use_case_is_reported_never_failed` and `test_the_scope_lists_are_disjoint_and_complete_as_named` (section 9).
14. Pre-review self-check, both directions: PASS. Misses and false alarms are both measured, and new true findings are listed (sections 1a and 1b).
15. The four FIX classes: PASS. Hermetic tests: writes only under tmp_path, waits use HANG_TIMEOUT, git reads are by blob or tree id only, plus one throwaway repository under tmp_path (test_lineage_lint passes).

## 9. Review fixes (review of `02cd654`: F1 B, F2 B, F3 A)
Each finding is fixed as a class. Each PROBE failed before the fix and passes after it. Notes F4-F11 were not filed and are not changed here.

| finding | class removed | fix | regression tests |
|---|---|---|---|
| F1 (B): a test compared the live `usecases/` with `DOCS` + `OUT_OF_SCOPE`, so any later use case failed the VE gate | tests whose outcome depends on the moving live tree (a merge blocker, which stage 1 forbids) | the tool lists unscoped use cases in the report (`unscoped_use_cases`) and prints them, exit 0; trees list their subdirectories (`subdirs`, all three tree kinds); the selection test, which also read the live tree, now reads the pin's blobs | test_a_new_use_case_is_reported_never_failed, test_the_scope_lists_are_disjoint_and_complete_as_named, test_no_test_here_reads_the_live_use_case_tree (AST guard: no `FsTree(ROOT)`, no `ROOT / "usecases"`, no `select_documents` without a tree), test_selection_shared_input_selects_every_reader |
| F2 (B): `rules? (\d+)` read only the first rule of "exception to rules 8, 9", so R10 lost R9's terms | a hand-copied rule-header regex instead of VE's grammar | rules.ve references are read with VE's own `ve.surface.softnorms.parse_header_options` (one owner), plus precedence sentences as `norm_english` reads them; a header the grammar does not read makes the rule UNPARSED, never short | test_a_multi_rule_header_puts_every_named_rule_on_the_path[asimov-laws, asimov-extended], test_rule_header_refs_read_every_header_ve_renders (round trip through VE's `render_header_options`, 1-4 rules), test_a_header_the_grammar_does_not_read_is_unparsed_never_short (6 forms), test_a_precedence_sentence_puts_its_target_on_the_path |
| F3 (A): the REPORT said a rebuild reads the recorded commits, but the builder resolved branch names against the moving `main` | provenance that depends on moving refs | `tests/data/defs_carried/repair_pins.json` records each repair's tip, base and merge (commit labels, equal to the fixture's) and pins the tip and base trees the builder reads (content-addressed, R18); `PIN` is a full id; the builder never names a branch, a repair commit or `main` to git; `GitTree` reads a tree id as it reads a commit; `--resolve-branches` prints today's resolution for a deliberate refresh | test_the_builder_pins_every_commit_the_fixture_records, test_a_rebuild_resolves_no_branch_and_no_main (also an AST check that no commit label is read), test_git_tree_reads_a_commit_or_a_tree_by_id |

- **F2's effect on the numbers: none.** R10's dependency list grows by 5 terms in asimov-laws (7 to 12) and 6 in asimov-extended (7 to 13): `harms_humanity`, `has_lawful_option`, `harm`, `robot`, `available` (and `prevent_required` in asimov-extended). No pair count, verdict, known-case result or lexical-recall row changes: the reports at main and `--known-trees` are equal apart from timings and R10's `terms`/`shown`, and `evidence/lexical-recall.json` and `evidence/t1-known-trees.json` still match a fresh run.
- **F3's rebuild:** `python3 tools/defs_carried_known.py --audit tests/data/defs_carried/audit --repo . --out /tmp/k.json` gives a fixture byte-equal to the committed one (`cmp`), not just equal `trees`. `--resolve-branches` shows today's branches differ from the pins for F1, F2, F3, F6, F8 (tips) and F9 (now merged). The probe itself is not a pytest test, because the builder reads the FSF/RSP/PF sources from `~/<path>` outside the repository (note F10), which a hermetic test may not do. The two tests above pin the same property without git or home-directory reads.
- **Why trees, and why saved data.** A first fix pinned the repair commits as literals; the selected run then failed `tests/test_lineage_lint.py::test_history_revisions_are_content_addressed` (13 commit ids reach git; R18 asks for content-addressed pins). A second fix pinned the trees as literals; the next selected run (on ve-cloud-2) failed the same test, because the tip trees of F2, F3, F6 and F7, which never reached main, are absent from that clone. The trees are now saved data under `tip_tree` and `base_tree` keys (the lint's content keys), and the commits are labels only.
- **F1's probe** (a `usecases/zz-probe` directory, then the test file) passes; the class guard keeps any later test here off the live tree.
- **Verification of the fixes (MEASURED, 2026-11-19).** Selected run (`mac-pytest.sh --select`, on ve-cloud-2) at `a9194d2f4c` (tree `2cf5e2204e`): exit 0, 0 failed, 319 units. Before it, two selected runs failed only `tests/test_lineage_lint.py::test_history_revisions_are_content_addressed`, on the commit-literal and tree-literal pins (see "Why trees"). `lake build` completed (1478 jobs), and `python3 lean/audit.py` PASS. No Lean or Rust change. The full gate was not run here: it runs in the merge train.
