# safety-framework-fidelity-fix-3: report

- **Status:** batches 1-4 delivered as the DRI ruled. reviews/dri-decisions-20261114-safety-framework-fidelity-fix-3.md
  holds G7, measures-sl2plus and the K2/G3 key question for the follow-on rows. No DRI signature is reserved, and DELTA has no rows.
- **HEAD:** the branch head that carries this report (feature/safety-framework-fidelity-fix-3, from main a84c072d76).
- **What changed:** G4 and G5 name no activity. N1's bridge is a rules.d1.ve block headed `item N1`, loaded for
  N1 alone. The safety-case, internal and high-risk legends quote their Glossary definitions whole. The f10 sentence
  of the fsf-fidelity-fix REPORT is reworded. PLAN section 12 gains item 26.
- **VE answers:** none move. All 262 are as on main (260/262 agree with the key; C3 and C-doc are the section-12
  disagreements). Every count below is PROJECTED; nothing is claimed before the re-read and fresh omission reads.
- **Open:** G7's second branch, measures-sl2plus and K2-L1/K2-L5/G3, each in a follow-on row the DRI filed.

Ruling: orchestrator re-plan ruling 2026-11-14 22:48Z item A2, with reviews/replan-20261114.md section 2. The
answers to this item's STOP questions are in reviews/dri-decisions-20261114-safety-framework-fidelity-fix-3.md
(items 1-5). Folded rows: safety-framework-cases-repair and safety-framework-facts-repair (their DELIVER steps are
covered below, as amended by that decision). No AMENDMENT line was appended to the task file.

## Units changed, by checklist class

| class (prompts/translation-fidelity-checklist.md) | unit | finding (seat, where) | fix |
|---|---|---|---|
| 8 case facts fixing open terms | CASES (G4, G5) | "PLAN:228 requires 'the named activity' ... Yet `cases.json:905` and `cases.json:913` set `"activity": "EXT"`" (astra.md:322; conceded opus.md:404, :412) | cases.json G4 and G5: `"activity": null`, following PLAN.md:232 "Every other open term is unset unless the case says so" and the 6.5 rows "significant but not severe cyber or manipulation risk" and "a capability in a domain outside the four" |
| 8 case facts (missing branch) | CASES (G7) | "G7 still sets only `cbrn_uplift_tcl`, so the plan's 'or for a mitigated CCL risk' branch (PLAN.md:353) has no case" (earlier/opus.md:62; earlier/astra.md:60) | not changed: DRI item 3 holds it for row safety-framework-case-alternatives (needs run.py) |
| 7 invented guards and exclusions | FACTS (bridge-one-domain) | "`facts.d1.ve:23` admits 'the text never states that the domains exclude each other,' but line 24 still asserts four exclusions" (earlier/astra.md:58; earlier/opus.md:60) | the block is now the last block of rules.d1.ve, headed `item N1`; facts.d1.ve holds only premises of every item (src 1.2 "We identify TCLs for CBRN risk, as well as ML R&D and misalignment risks" stays the only closure) |
| 7 | FACTS (measures-sl2plus) | "`measures-sl2plus` (:13-14) ... is still outside PLAN 4.1's table, closures and activity facts" (earlier/opus.md:60) | not changed: DRI item 5 holds it (needs run.py) |
| 10 key cells | N1 (item) | "PLAN:361 promises 'a certificate from the closure in 4.1'; `results.json:9514-9517` reports `"bridge-one-domain"` among `"own_premises"`" (astra.md:364) | PLAN section 12 item 26 records that the 4.1 closure alone does not certify N1 (DRI item 1); the key is unchanged |
| 1 dropped clause | f7-sc | omitted from the carrier: "are an assessable argument showing how severe risks associated with a model's CCLs have been reduced to an acceptable level" (uc-reads-unadj-fsf.tsv:142, :146) | the `safety_case` legend quotes the Glossary definition whole (DEF only) |
| 1 | f2 (deployment scope) | not carried: "represent model releases restricted to Google employees for internal use" and the high-risk sentence (uc-reads-unadj-fsf.tsv:100, :105) | the `internal` and `high_risk` legends quote their Glossary sentences whole (DEF only); row uc-split-scope-codex decides the class |
| 11 elided quotes | f17-hri | PLAN.md:623 quotes "also account for the safety implications of high-risk internal deployments" | no change: the quote is verbatim (src 3.2.1), and the `periodic_covers_internal` legend carries every word |
| 10 | K2-L1/PROXIMITY, K2-L5/PROXIMITY, G3 | src:4 "Similarly to CCLs, early warning evaluations will be used to assess the proximity of a model to a TCL and analyze the risk posed" is a commitment (opus.md:318; astra.md round 2) | question only: DRI item 2 files row safety-framework-proximity-tcl |

The other G and K cases were checked for the same two defects: a field PLAN 5 does not stipulate, or a PLAN 5
branch with no case.
- Fields: none found. G1, G2 and G9-TCCL each name one level standing for the class the row names ("a CCL
  model", "an ML R&D CCL model", "T/CCL models"). Neither seat raised this.
- Branches without a case: G3, "approaching or reaching a TCL", has a case for approaching only. G9, "for T/CCL
  models", has a case for a CCL only. DRI item 3 puts both with G7 in row safety-framework-case-alternatives.

Shared names: `translation.read_blocks`, `translation.facts` and run.py:282 now read the item-scoped block from
rules.d1.ve. `tests/test_english_statement_blocks.py::source_blocks` reads only rule blocks (see Tests). No other
block's predicate or legend was renamed.

## Batch 1: CASES

- G4, G5: `"activity": "EXT"` -> `null` (cases.json). The case's own run.py ran afterwards: results.json is byte
  for byte the same, G4 ALL -> ALL, G5 ALL -> ALL, 260/262. Both seats expected no answer to move (astra.md:326),
  so STOP question 1 was not needed for G4 and G5.
- G7: held (DRI item 3). Scratch, not committed: SILENT:DISC on a case reaching each of the five CCLs, with a
  `mitigates` finding and no OT11 findings, is ALL. Adding the branch therefore moves no answer away from the key.
- PROJECTED answer changes: none. The G4/G5 item finding is answered. The CASES unit stays failing on G7, so no
  CASES answer comes back from this batch.

## Batch 2: FACTS and N1

- bridge-one-domain: the block left facts.d1.ve and is now the last block of rules.d1.ve, header unchanged
  (`item N1`).
  - translation.py: `rule_blocks()` keeps the numbered rules, and `rule_fact_blocks()` gives the item-scoped
    premise blocks. `facts(item)` adds the blocks headed with that item. A facts.d1.ve block headed `item <id>`
    is refused, and so is a rules.d1.ve fact block with no item.
  - run.py:282: the one line DRI item 4 allows. It lists bridges from both files, so `invention_audit.bridges`
    still names the block.
  - results.json: N1's record names the block in `own_premises`, as before, so the counter ties it to N1 alone.
- measures-sl2plus: held in facts.d1.ve (DRI item 5). Every case model gets it through `T.facts()`, and no item
  record names it without a wider run.py change. Its PLAN section-12 sentence is unchanged.
- N1, from the document's premises and 4.1's closure alone (scratch `run.refute`): UNKNOWN. Neither goal
  certifies, and Astra's countermodel `concerns(cbrn_uplift_tcl, cyber)` stands. The key cell is PLAN.md:361
  "never: ALL (a certificate from the closure in 4.1)". STOP question 1 went to the DRI; item 1 keeps VE ALL with
  the bridge as N1's own assumption and records the finding in PLAN section 12 item 26. Item 26 names the block
  by its `item N1` header, as item 24 does, so it adds no record to the new unit (DRI item 1: no new exposure).
- run.py ran afterwards: the comparison is identical to main. N1 stays ALL, with only its certificate hashes
  changed (batch 3's legends are in the environment the certificate carries).
- PROJECTED answer changes: none. The bridge finding is answered. FACTS keeps measures-sl2plus, so FACTS still
  holds every answer. N1's item finding is disclosed, not settled; the re-read judges it.

## Batch 3: carriers

- f7-sc (B-L0..L7/SC, 8 answers): the `safety_case` legend now ends: safety cases "are an assessable argument
  showing how severe risks associated with a model's CCLs have been reduced to an acceptable level" (Glossary).
  Checked read-only with the counter's helpers (used_predicates, legend_raw, omit_norm): f7-sc's carrier holds
  every word of the read's quote.
- f2 scope (A-L0..L7-HRI/INT /CCA, 16 answers): two legends were missing words, which are now added verbatim (DEF
  only).
  - `internal` lacked "represent model releases". It now quotes "represent model releases restricted to Google
    employees for internal use".
  - `high_risk` lacked "represent model releases restricted to Google employees" and "(e.g. building internal
    security infrastructure or automating ML R&D)". It now quotes the whole Glossary sentence.
  - Measured with the same helpers: f2's own carrier uses `assessed`, `first_deployment` and `frontier`, not
    `internal` or `high_risk`, so the mechanical carrier still lacks these words. The legend-level route is what
    row uc-split-scope-codex reads; this item does not clear it.
- Regenerated with the case's own scripts: environment.d1.json (vocabulary.py), coverage.json (build_document.py;
  the document hash only), readings/results.json (readings_r1.py; unchanged) and results.json (run.py; N1's
  certificate hashes only).
- PROJECTED: up to 8 /SC answers clear on the f7-sc read once a fresh read at the scored commit finds the words.
  The 16 scope answers depend on uc-split-scope-codex. Every one of them is still held by FACTS and CASES.

## Batch 4: wording items

| file:line | old sentence | new sentence | carrier or ruling |
|---|---|---|---|
| docs/usecases/safety-framework/fsf-fidelity-fix/REPORT.md:160-163 | "(a) ... against reviews/dri-decisions-20261029-uc-audit2.md item 1:", then one sentence that set the three surviving `-diff` ids next to the drop word for the `-same` blocks (verbatim at a84c072d76, lines 160-162) | "RS9 and RS6 keep the one reading "different", and the blocks f10-dm-same, f10-rel-same and f15-same no longer exist. The blocks f10-dm-diff, f10-rel-diff and f15-diff stay, selected by "different"." | reviews/dri-decisions-20261029-uc-audit2.md item 1 (SIGNED), VE 64f7f147b |

- (b) f17-hri, PLAN.md:623: kept as written. The quote is verbatim (src 3.2.1). rules.d1.ve:67's act
  `periodic_covers_internal` has the legend "also account for the safety implications of high-risk internal
  deployments (3.2.1)". No carrier change.
- (c) safety-framework-fidelity-fix-2/REPORT.md:213: left as it is (DRI answer NO,
  reviews/dri-decisions-20261114-facts-void.md item 1). Row record-void-counter or the omission read handles it.
- (d) Not reworded, also because of that NO. Each waits for a clearing read: safety-framework-fidelity-fix-2/REPORT.md:59
  (f16-ds, f16-ds-strict, the class 7 row), :36 (the f7-rra bullet) and :107 (the f5 bullet).
- (e) Kept as they are, each waiting for a clearing read: PLAN.md:647 (measures-sl2plus), PLAN.md:581 (f16-ds-strict) and
  PLAN.md:616 (f4-need-d, f4-need-r).

The scan, run read-only at this branch's head (omit_exposure on the 15:04Z manifest with ve_commit set to the
head, bridge-one-domain added to its units). The records it still finds, one row per unit:

| unit | records |
|---|---|
| FACTS | PLAN.md:647; fix-2 REPORT.md:213 |
| CASES | fix-2 REPORT.md:213 |
| D2D3 | fix-2 REPORT.md:213 |
| f3, f6, f12-p, f12-u, f13-p, f13-u, f14 | fix-2 REPORT.md:213 |
| f16-ds | fix-2 REPORT.md:59; :213 |
| f16-ds-strict | PLAN.md:581; fix-2 REPORT.md:59; :213 |
| f7-rra | fix-2 REPORT.md:36; :213 |
| f5 | fix-2 REPORT.md:107 |
| f4-need-d, f4-need-r | PLAN.md:616 |
| f17-hri | PLAN.md:623 |

The scan finds none for f10-dm-diff, f10-rel-diff, f15-diff or bridge-one-domain. Every FSF answer also carries
the `no-record *` exposure (no accounting file), which only a per-answer read clears.

PROJECTED: the 15 answers the replan counts behind the f10 wording no longer have that record. They still need
the idmap earlier pass for f10-dm-diff and f15-diff. The 8 f17-hri answers need a read of PLAN.md:623.

## exposure.py (FACTS/CASES), before and after

Before, on main a84c072d76 (raw output: exposure-before.txt beside this report). Each record's text is shown here by its file:line:

```
counter sha256 28966da1  case safety-framework  commit a84c072d76  state run
FACTS <- measures-sl2plus     plan12       | usecases/safety-framework/PLAN.md:647
FACTS <- FACTS                report       | docs/usecases/safety-framework/safety-framework-fidelity-fix-2/REPORT.md:213
CASES <- CASES                report       | docs/usecases/safety-framework/safety-framework-fidelity-fix-2/REPORT.md:213
D2D3  <- D2D3                 report       | docs/usecases/safety-framework/safety-framework-fidelity-fix-2/REPORT.md:213
3 exposures on FACTS/CASES
```

The same 3 came out at the start of the work with the counter at sha 1c7cc4f7; the installed counter is now 28966da1.

After: the section "exposure.py after" at the end of this file (run on the committed head).

## Open list

| id | question or reason | answer |
|---|---|---|
| N1 | STOP 1: N1 is UNKNOWN from the 4.1 closure alone | DRI item 1: keep ALL with the bridge as N1's own assumption, PLAN section 12 item 26 |
| K2-L1/PROXIMITY, K2-L5/PROXIMITY, G3 | STOP 2: formalise src:4? Scratch: NONE -> ALL, NONE -> ALL, ALL -> NONE | DRI item 2: yes in principle, in row safety-framework-proximity-tcl |
| G7 (and G3's reaching branch, G9's TCL half) | STOP 3: run.py states no case alternative | DRI item 3: row safety-framework-case-alternatives |
| invention audit | run.py:282 reads bridges from facts.d1.ve only | DRI item 4: the one-line edit, done |
| measures-sl2plus | its item records need run.py | DRI item 5: held, row safety-framework-case-alternatives under facts-split-sizing |
| C3, C-doc | VE != key, recorded key errors (PLAN section 12) | not this item's (task table) |
| f10-dm-diff, f15-diff (findings) | carried through audit-findings/safety-framework/idmap.tsv | the next blind re-read's earlier pass |
| f4-check-d/r, f9-acc, f10-acc, f10-rel-diff, f11-rel, f16-ds(-strict), f17-pra, f20 x4, D2D3 (findings) | both seats NOT-PRESENT in the 11-14 earlier pass | the decider's records |
| f19-default | a read defect | the fresh omission read |

## Seeded bugs (each planted alone, shown failing, restored)

| bug | file | failing test |
|---|---|---|
| (a) `"activity": "EXT"` back on G4 | usecases/safety-framework/cases.json | tests/test_safety_framework.py::test_g4_and_g5_name_no_activity[G4] |
| (b1) a bridge exclusion back in facts.d1.ve as an `always` block | usecases/safety-framework/facts.d1.ve | ::test_facts_holds_the_premises_of_every_item_and_no_item_s_own_bridge |
| (b2) the bridge loaded for every item (`facts()` ignores the item) | usecases/safety-framework/translation.py | ::test_n1_alone_loads_its_bridge_and_its_record_names_it |
| (b3) run.py:282 unedited (bridges from facts.d1.ve only) | usecases/safety-framework/run.py | ::test_n1_alone_loads_its_bridge_and_its_record_names_it |
| (c) "an assessable argument" cut from the safety_case legend | usecases/safety-framework/vocabulary.py | ::test_the_legend_quotes_the_glossary_definition_whole[safety_case] |
| (d) "restricted to Google employees" cut from the internal legend | usecases/safety-framework/vocabulary.py | ::test_the_legend_quotes_the_glossary_definition_whole[internal] |
| (e) void: no rewording under item 4(c) | - | - |
| (f) "(not removed)" put into the f10 spec re-read sentence | docs/usecases/safety-framework/fsf-fidelity-fix/REPORT.md | ::test_the_f10_spec_reread_names_the_surviving_blocks_without_a_drop_word |
| (g) "also account for the safety implications of" cut from the periodic_covers_internal legend | usecases/safety-framework/vocabulary.py | ::test_the_section_12_f17_quote_is_carried_by_f17_hri |

Product code is Python only (translation.py, run.py, vocabulary.py), with no Lean or Rust change. (b2), (b3), (c),
(d) and (g) are in changed Python files.

## Tests

- New, in tests/test_safety_framework.py:
  - test_g4_and_g5_name_no_activity
  - test_facts_holds_the_premises_of_every_item_and_no_item_s_own_bridge
  - test_an_item_s_premise_in_facts_or_an_unscoped_fact_in_rules_is_refused
  - test_n1_alone_loads_its_bridge_and_its_record_names_it (the conditions of DRI items 1 and 4)
  - test_the_legend_quotes_the_glossary_definition_whole
  - test_every_glossary_definition_is_the_pinned_source_text
  - test_the_f10_spec_reread_names_the_surviving_blocks_without_a_drop_word
  - test_the_section_12_f17_quote_is_carried_by_f17_hri
- Changed: tests/test_english_statement_blocks.py `source_blocks` reads the rule blocks of rules.d1.ve, since
  N1's bridge is a premise block there. The pinned 44 FSF and 76 RSP statement blocks are unchanged. No test was
  taken out.
- The frozen-key test, the transcription pin, `test_rerun_equals_committed_results` and fix-2's tests are
  unchanged.

## DELTA, trust, budget, size

- DELTA: none. These are use-case files and docs; no checker output changes.
- Trust: `tools/trust_map.py --check` against a84c072d76 reports K +0, S +0, trusted +0. No Lean changed, so there is
  no trust_mutants sweep: light-lane.py printed NOT (203 lines > 150), but there is no trusted Lean to mutate.
- Budget: the launcher gave no readings.
- SIZE: 59 product, 121 tests, 11 other hand-written lines before this report (PLAN.md section 12 item 26 and the
  fsf-fidelity-fix REPORT sentence); this report is the rest.

## PLAN section-12 deviation

Item 26, "N1's bridge and the 4.1 closure (safety-framework-fidelity-fix-3)". It records the bridge's place and
that the 4.1 closure alone does not certify N1. Sections 1-11 are not edited, nor are section 6 or answer-key.json.

## Notes

- The comments at run.py:669 and build_document.py:249 still name facts.d1.ve as the bridge's place. This item
  may edit run.py only at :282 and build_document.py only for the measures-sl2plus lookup. Row
  safety-framework-case-alternatives can fix the comments when it touches those files.
- run.py:281's `untraced` list still checks the rule blocks and facts.d1.ve only. The bridge's header cites its
  source, so it stays traced.
- README.md:199 still describes G7 as "disclosure for a TCL", which G7 is until its branch lands.

## Next item (launched by the DRI decider)

1. The blind re-read on the commit where this item lands on main; its earlier pass covers f10-dm-diff and f15-diff through the
   idmap.
2. Fresh omission reads at that same commit (every FSF read is commit-bound), with row uc-split-scope-codex's read.
3. The records for what (1) answers NOT-PRESENT.
4. Rows safety-framework-case-alternatives and safety-framework-proximity-tcl (filed by the DRI).
