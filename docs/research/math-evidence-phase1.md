# Math-evidence, phase 1: ME-0 (pilots and pre-registered measurements)

> **Status.** Phase 1 of [the plan](../spec/math-evidence-PLAN.md) (draft 4), as the cross-plan review orders it
> (`manage-agents/debates/plan-synthesis/SYNTHESIS.md` 4.1, phase 1: "Pilots: … ME-0"; `edits-math-evidence.md`
> edit 10: "ME-0 runs now"). Branch `research/math-evidence-p1`. No product code (`ve/`, `lean/VE/`, `rust/`,
> `tools/`) is changed and no model is called. Measurement scripts are in `research/math-evidence/`; evidence files in
> `docs/research/evidence/math-evidence/`. "Today's VE" is `main` at `406736a4`, run from its built checkout
> `ve-pilot-20261013T0600Z` (read-only; every `ve` run under `prlimit --as=6442450944`).
>
> **Placement.** The plan's ME-0 names new `usecases/` directories and a `SOURCE.md` per target. This run puts the
> same files under `docs/research/evidence/math-evidence/<target>/` instead, as the phase-1 brief directs, and records
> the pin in `raw/fetch-log.json` and `SUMMARY.md` (4.2 item 10).
>
> **Revised after review** (section 1 untouched; no bar moved). H-5 is reclassified CHANGED and M-4 RE-WORDED; P4
> is counted over its pre-registered scope; the order basis in 4.1, the "certified" wording, the premise status
> (UNKNOWN for H, V, DL) and the clean-clone reproduce recipe are corrected; the math `run.json` is regenerated.

## 1. Pre-registration (written and committed before any measurement below was run)

Each bar is quoted from the plan verbatim. Estimates the plan labels **estimate** are not bars: they are reported as
inside or outside their range, never PASS/FAIL, and never moved.

One step ran before this section was committed: the licence fetch for D22 (P2) and a read of the Michelson-Morley
Wikisource index page, needed to know which texts exist. The rule D22 applies was fixed in the plan before that fetch,
so no bar moved; the fetch's output is recorded with its retrieval time.

### P1. ME-0's done-condition (the bar)

> "Done when the four (or three) ledgers account for 100% of their source bytes and `SUMMARY.md` states the numbers."
> (plan, ME-0)

- **Measured by:** Lean's own coverage (`ve document coverage`, `accounted_bytes` = `source_bytes`) over one
  `ve-document@1` per pinned source, whose prose is the pinned source byte for byte (checked by SHA-256), and
  `SUMMARY.md` in the evidence directory.
- **PASS** iff every ledger reports `accounted_bytes == source_bytes` with `coverage_percent` 100, its document is
  admitted by `ve document check`, and `SUMMARY.md` states bytes by status and kind for each.

The plan's ME-0 also requires, without a numeric bar (each is reported done or not done):

> "**Pin**: for each target, fetch the text with a plain HTTP client (no model), record URL, retrieval time, licence
> evidence (…) and SHA-256 in `SOURCE.md`."
>
> "**Partition** every byte into units with kinds (exposition, definition, theorem, proof step, equation, quantity,
> table, empirical claim, comparison, hedge, citation, caption, meta) and today's statuses: W6a quantity facts and
> linear comparisons with unit tags (CHECKED), attributions (`reports@0`), labels (LABELLED), and UNFORMALISED with one
> `missing_feature` from: `calc`, `calc-data`, `calc-derive`, `calc-dimension`, `calc-stats`, `calc-algebra`,
> `arith`, `arith-import`, `approximation`, or a sibling's tag (`quantities`, `attitudes`, `events`, `attribution`)."
>
> "**Measure**: `coverage.json` with bytes by status and kind; a sentence-kind count replacing research 2.5's
> estimates; the NORTH-STAR rows M, H, DL, V refreshed from measurements."

Status rules fixed now (plan section 7): CHECKED only when Lean admits the unit's W6a content in the checked document
(a stated quantity with a unit tag, `support: testimony`: Lean admits it, it does not make it true); "LABELLED for
exposition and meta"; "A unit whose numbers are checked but whose hedge or causal framing is not is MIXED, never wholly
CHECKED". A unit with a primary kind among definition, theorem, proof step, equation, quantity, table, empirical
claim, comparison or hedge that is not CHECKED is UNFORMALISED with exactly one `missing_feature` from the list above,
chosen as the first plan batch family that would check it. Citations, captions and narrative are LABELLED.
Segmentation: one unit per sentence (a table: one unit per row), split further only where the status differs.

### P2. The deep-learning target (decision rule D22)

> "deep learning = the first of the ranked candidates whose CC-BY licence ME-0 confirms by reading the licence field of
> its abstract page with a plain HTTP fetch and no model" (plan D22), the ranked candidates being "(1) … LoRA …
> (arXiv 2106.09685) …; (2) … Vision Transformers Need Registers (arXiv 2309.16588) …; (3) … AlphaFold, *Nature* 596
> (2021) 583-589" (research 2.4); "if none qualifies, DL stays unpinned and the plan's DL batches wait".

- **Outcome categories:** the pinned candidate, or "none". Reported as the rule's result (no PASS/FAIL).

### P3. The pinned pilots stay at zero

> "The pinned constitution and UDHR pilots have **no unit** blocked by this topic (research 2.2), so no batch claims a
> byte there." (plan 0); ME-0 row of plan 7: "Constitution 0 | UDHR 0".

- **Measured by** a script over `pilots/claude-constitution/run-20261012T1800Z/units.json` and
  `pilots/udhr/run-20261012T1800Z/units.json` (read-only): units whose `missing_feature` or any `other_blockers`
  entry names this topic. The topic's tags, fixed now: the plan's ME-0 list (`calc`, `calc-data`, `calc-derive`,
  `calc-dimension`, `calc-stats`, `calc-algebra`, `arith`, `arith-import`, `approximation`) and research 2.2's words
  (evidence, statistic, mathematic, calculat, equation, empiric, science, probabilit, number, arithmetic), matched as
  case-insensitive substrings of the tag.
- **PASS** iff 0 units and 0 bytes match in both pilots.

### P4. Fixture anchors

> "Target sentences marked *paraphrase* are from memory and are re-anchored to the pinned text's byte spans in ME-0;
> their arithmetic does not depend on the exact wording." (plan 4)

- **Scope:** the physics fixtures H-1 to H-10 and the mathematics fixtures M-1 to M-5 (paraphrases), and the
  in-repository quotes V-1 to V-8 and D-1 to D-3 (said to be exact quotes).
- **Outcome per fixture**, fixed now: **ANCHORED** (the quoted words occur in the pinned source and the case's numbers
  are the source's), **RE-WORDED** (a span says the same with different words; the case's numbers are the source's),
  **CHANGED** (the source's span exists but a number or relation the case uses differs), **ABSENT** (no span), or
  **NOT A QUOTE** (the plan itself says the fixture is not the author's wording).
- **Bar** (from "their arithmetic does not depend on the exact wording"): **PASS** iff no fixture is CHANGED or
  ABSENT; every CHANGED or ABSENT fixture is listed under "Consequences for draft 2".

### P5. The paper denominator

> "VE's paper sections by SHA-256 at the ME-0 commit (73,801 B at `49de179e`, measured with `wc -c`)." (plan 7)

- **PASS** iff `paper/sections/*.md` total 73,801 bytes at this branch's ME-0 commit and on `main`.

### P6. H-10: 1887 dates are refused today

> "W6a date literals start at 1970-01-01 (W6 6.1), so these are refused" (plan 4.2, H-10).

- **Measured by** `ve document check` on a one-unit document stating an observation date of 1887-07-08 as a W6a
  `day` quantity, beside the same document dated 1970-01-01 as a control.
- **PASS** iff the 1887 document is refused and the 1970 control is admitted.

### P7. Estimates (not bars; reported inside or outside the range)

> ME-0: "Estimated: H 1.5-2.5 KB CHECKED, 13-16 KB LABELLED; V-E1 0.3-0.8 KB CHECKED; M 0 CHECKED; DL 2-4 KB if
> pinned (all **estimates**). Constitution and UDHR: 0." (plan, ME-0)

> Research 2.4 sizes: physics "13 pages; about 30-40 KB of text and tables"; mathematics "2 pages; about 4-6 KB".
> Research 2.5: sentence kinds per target (its table), "for H, M and DL … **estimates from memory of the texts**, to be
> replaced by ME-0's measured partition"; exposition share "about 60%" (physics), "about 15%" (mathematics),
> "about 45%" (deep learning, LoRA as a structural proxy).

### What is not run in phase 1

Every other math-evidence item needs product code (ME-1 to ME-13, ME-P1 to ME-P4) or a statement review (ME-S), or is
an experiment that waits for a batch (EX-1 after ME-12; EX-2 after ME-9; EX-3 after ME-6; EX-5 after ME-4). Section 5
lists them as DEFERRED with the reason.

## 2. Results (measured after the pre-registration commit `0d9db6e1`)

Numbers come from `docs/research/evidence/math-evidence/summary.json` and its files;
[SUMMARY.md](evidence/math-evidence/SUMMARY.md) has the full tables. "Today's VE" is `main` `406736a4`.

| Item | Bar (quoted in section 1) | Measured | Result |
|---|---|---|---|
| P1 ME-0 done-condition | every ledger `accounted_bytes == source_bytes`, document accepted by `ve document check`, `SUMMARY.md` states the numbers | 4 ledgers (5 documents): H 24,368/24,368, M 2,651/2,651, V 8,883/8,883 + 1,054/1,054, DL 66,858/66,858 B accounted (Lean coverage 100%); all five documents accepted, and each document's graph admitted (H, V's E1 file, DL); SUMMARY.md written. Premise status is UNKNOWN for H, V and DL (see below) | **PASS** |
| P2 DL target (D22) | the first ranked candidate whose licence field is CC BY | LoRA: arXiv non-exclusive; Registers: arXiv non-exclusive; AlphaFold: `"license":"http://creativecommons.org/licenses/by/4.0/"` (Nature page) and CC BY 4.0 (Europe PMC JATS) | **AlphaFold pinned** (rule applied; no PASS/FAIL) |
| P3 pilots stay at zero | 0 units and 0 bytes in both pilots | constitution 0 of 1,132 units; UDHR 0 of 130 (1,074 and 46 units do carry a `missing_feature`, so the zero is not an empty field) | **PASS** |
| P4 fixture anchors | no fixture CHANGED or ABSENT | 32 fixtures in the pre-registered scope: 14 ANCHORED, 9 RE-WORDED, **3 CHANGED (H-4, H-5, H-9)**, 0 ABSENT, 6 NOT A QUOTE. Outside the scope, V-9 to V-12: 1 RE-WORDED, 3 NOT A QUOTE | **FAIL** |
| P5 paper denominator | 73,801 B at the ME-0 commit and on `main` | 73,801 on this branch, on `main` and at `49de179e` | **PASS** |
| P6 H-10: 1887 dates | 1887 refused, 1970-01-01 admitted | 1887-07-08: `DateRange(1887-07-08)`; 1970-01-01: accepted | **PASS** |

The ME-0 sub-tasks without a bar: **Pin**, done for all four targets (`raw/fetch-log.json`: URL, time, status,
SHA-256). **Partition**, done (every unit has a plan kind and a status, and every UNFORMALISED unit has one feature).
**Measure**: `coverage.json` is done for every document, and the sentence-kind count is done. The NORTH-STAR rows are
DEFERRED (section 5); their measured text is in 4.4.

**Premise status (three-valued).** `ve document check` reports the premise set of the H, V (both files) and DL
documents as `UNKNOWN` (budget: 10,000 proof steps, models up to domain size 2): Lean found neither a model nor a
contradiction certificate. Only M's premises have a checked model. So for H, V and DL the admission's `vacuous` field
is `null` and the check issues no document status. "Accepted" in P1 means `ve document check` exits 0 with the graph
admitted, which the bar asks; it does not mean the premises were shown consistent. The same holds for every
"certified" relation below: Lean replayed the certificate, but whether the premise set behind it has a model is
undecided, so non-vacuity is UNKNOWN, not established.

**Notes on the pre-registration** (section 1 is unchanged since `0d9db6e1`; these notes are added after review):

- Section 1 says the licence fetch that ran before it "is recorded with its retrieval time". That earlier fetch's
  output was not kept. The committed licence evidence is the fetch at 08:16:04 UTC, after the pre-registration
  commit (08:15:34), so the D22 result rests only on bytes fetched after the rule was registered.
- P4's scope is "H-1 to H-10, M-1 to M-5, V-1 to V-8, D-1 to D-3". The counts above take each range with its
  lettered variants (H-6p, H-6n, M-3r, M-4x, V-1n, V-6r): 32 fixtures. The first version of this report counted 36,
  silently adding V-9 to V-12; they are now reported apart. (Leaving out V-6r gives 31, with the same outcome.)
- The plan's ME-0 records each pin in a `SOURCE.md`. This run records the same facts in `raw/fetch-log.json` (URL,
  time, status, size, SHA-256) and the Sources table of `SUMMARY.md` instead; no `SOURCE.md` is written.

### P4 in detail (the three CHANGED fixtures)

- **H-4.** The plan's case takes "v/V = 10⁻⁴ stated". The source states no v/V. It gives v²/V² = 10⁻⁸ only through
  "this would be 2D × 10⁻⁸" (unit h049, bytes 7,350-7,444, and again in h113). The arithmetic still holds. The fixture's premise
  is not the source's.
- **H-5.** The case computes 2 × (2 × 10⁷) × (10⁻⁴)² = 0.4, so it rests on H-4's unstated premise v/V = 10⁻⁴. The
  result 0.4 is the source's ("0•4 fringe"), reached there through v²/V² = 10⁻⁸ (h113). The first version of this
  report marked H-5 RE-WORDED by reading the source's route instead of the case's; by the pre-registered rule it is
  CHANGED.
- **H-9.** The plan's case reads "readings at 16 azimuths per session and their printed means". The source's table
  (bytes 12,968-15,143, units h086-h106) differs:
  - Each cell is already "the means of the six readings"; the readings themselves are not printed.
  - There are 17 columns, because mark 16 appears at the start and at the end of a turn.
  - There are three sessions per table (noon: July 8, 9, 11; evening: July 8, 9, 12).
  - There are derived rows: Mean, Mean in w. l., a repeated half row, and Final mean.
- The full list, with spans, reasons and exact-fraction pre-checks for ME-S, is in `fixture-anchors.json`. The
  pre-checks are not VE verdicts.

### P7 estimates (inside or outside; never bars)

| Estimate (plan or research) | Measured | Inside? |
|---|---|---|
| H 1.5-2.5 KB CHECKED | 1,858 B (1,582 B in units that take part in Lean-certified relations) | inside |
| H 13-16 KB LABELLED | 11,560 B | outside (below) |
| H text 30-40 KB | 24,368 B | outside (below) |
| V-E1 0.3-0.8 KB CHECKED | 1,199 B (382 B in certified relations; 716 B are the appendix's stated differences) | outside (above) |
| M 0 CHECKED | 0 | inside |
| M text 4-6 KB | 2,651 B | outside (below) |
| DL 2-4 KB CHECKED (estimated for LoRA) | 4,453 B for AlphaFold (2,548 B in certified relations) | outside (above) |
| Exposition share: H 60%, M 15%, DL 45% | H 39.4%, M 1.5%, DL 29.3% (DL citations are another 24.0%) | all outside (below) |
| Constitution and UDHR 0 | 0 and 0 (P3) | inside |

## 3. Findings beyond the bars

1. **W6a already checks part of the physics table.** Michelson and Morley print their table means, which makes the
   Mean and Final mean rows ground linear arithmetic over printed values. For each Mean, a rounded mean is the pair
   of bounds 3m − 0.15 ≤ r₁ + r₂ + r₃ < 3m + 0.15. Ties cannot occur: a sum of tenths divided by 3 is never an odd
   twentieth. Results:
   - 34 Mean values, 18 repeat equalities and 18 Final means are certified by `prove_quantity`, and Lean replays the
     certificates.
   - A Mean changed by 0.3 with the old certificate kept is refused by Lean.
   - Only "Mean in w. l." (Mean × 0.02 wave-length per division) is beyond W6a, because it is cross-tag arithmetic.
2. **The Rust accelerator's default limit stops a two-table paper.** At the default 5 s wall-clock limit, the
   untrusted Rust checker stops the physics document (216 W6a constants), which is then CheckerUnavailable. With
   `VE_RUST_TIMEOUT=1800` the document is admitted in about 47 s (157 MB peak). The VE-paper document hit the same
   limit on one run of three. This is load-dependent, as the UDHR pilot also reported.
3. **AlphaFold's own numbers give two reading-set fixtures that the plan's LoRA-based DL fixtures lacked.** Both
   computations are exact fractions done in this research script, not VE verdicts.
   - **"8× faster".** The timings give exactly 8 at 256 residues (4.8/0.6). At 384 residues it is 92/11 ≈ 8.36, and
     at 2,500 residues it is 60/7 ≈ 8.57, which rounds to 9. Read as "rounded to the written digit", the claim fails
     at 2,500 residues.
   - **"around 350,000" sequences** (d119) against the 355,993 that Methods states (d231). Rounded at the written
     place (10⁴), 355,993 gives 360,000. So the "rounded to the written digits" reading of "around" fails, and only
     an open tolerance holds.
4. **VE's main-text p values are a second granularity fixture.** All six values (v060-v065) are within rounding of
   k/4096: .460938 (1,888, an exact tie that both rules print alike), .875488, .000977, .001953, .218750 and
   .993164. That makes a V-7 companion over 2¹² sign flips.
5. **The pinned mathematics text is OCR.** Both scans garble the formulas: 2,114 B (79.7%) is analytic (logarithms,
   the Chebyshev functions, Stirling). No plan batch states that analytic content in VE; it stays residual or is
   imported. Formula (18)'s thresholds 2, 11, 17, 29, 41 are intact and pre-check exactly; they give M-4 four more
   pairs.
6. **The CHECKED byte count mixes two strengths.** In each target, these bytes are only stated (Lean admitted the
   value but no relation was certified): H 276 of 1,858, V 817 of 1,199, DL 1,905 of 4,453. The rest are units
   that take part in a certified relation, as premise or as consequence; they are not all certified values
   themselves (H's "Mean in w. l." rows are premises there, not certified), and the premise status behind every
   certificate is UNKNOWN (section 2).

## 4. Consequences for draft 2

The ceilings below are upper bounds from the partition. Each assumes that every unit tagged with one of this plan's
features becomes CHECKED, and leaves out approximation units, which D17 makes reading sets and so never CHECKED
(`summary.json`, `ceilings_percent`).

### 4.1 Confirmed

- **ME-0 is done** (P1). The three pinned ledgers and DL exist, with Lean's coverage at 100%.
- **The order "physics, then deep learning, then mathematics" is confirmed, by bytes a batch can check.** In raw
  bytes tagged with this plan's features DL is larger (6,560 B against H's 6,166 B). The order holds on two other
  bases, and draft 2 should name which one it uses:
  - bytes left after the approximation units (which D17 keeps out of CHECKED) and the comparisons that need unpinned
    figure data: H 3,435 B, DL 1,475 B, M 272 B without imports;
  - share of the source: H 25.3%, DL 9.8%.
- **The constitution and UDHR stay at 0 for every batch** (P3). No batch claims a byte there.
- **H-10 stays refused until ET-T3** (P6, `DateRange`).
- **H-6, H-6p and H-8 are anchored in the author's words.** H-1, H-2, H-3 and H-7 are the source's equations in
  TeX form; their arithmetic is unchanged.
- **The fixtures from VE's own paper and the pilots are exact quotes** (V-1 to V-8, D-1 to D-3).
- **The ME-1, ME-7 and ME-12 batch shares are confirmed by measured bytes:**
  - `calc` (ME-1): H 2,216 B, V 469 B.
  - `calc-stats` (ME-7): V 2,858 B (28.8% of the E1 slice, its largest lever), DL 1,329 B.
  - `arith` (ME-12): M 220 B.
- **`calc-dimension` (ME-6) and `calc-derive` (ME-5) are small in these texts:** H 92 B and H 222 B, plus M 52 B. They
  stay because they decide H-6, H-7 and the w. l. rows, not for their bytes.

### 4.2 Changed (draft 2 should edit)

1. **H-4 and H-5 (both P4 CHANGED).** Both cases rest on "v/V = 10⁻⁴ stated", which the source never states.
   - H-4: replace the premise with the source's own v²/V² = 10⁻⁸, read from the span "this would be 2D × 10⁻⁸"
     (h049; repeated in h113).
   - H-5: rewrite the case as 2 × (2 × 10⁷) × 10⁻⁸ = 0.4 over the same span, so its result "0•4 fringe" is reached
     the source's way.
   - Alternatively keep v/V = 10⁻⁴ in both as an external premise with `support: testimony` and a residual leaf.
2. **H-9 (P4 CHANGED), and with it ME-P2's physics share.**
   - Rewrite H-9 as the source's table: 17 marks, three sessions, means of six unprinted readings, and the rows Mean,
     Mean in w. l., the repeated half row, and Final mean.
   - Today's W6a already certifies the Mean, repeated-half and Final mean relations. The units that take part in
     those relations, as premises or as consequences, are 1,582 B: the six session rows and both "Mean in w. l."
     rows are among them as premises, and "Mean in w. l." is not itself certified. H-9 therefore no longer waits for
     ME-4's `counted` means: its inputs are printed means, not a data file.
   - What remains is "Mean in w. l." = 0.02 × Mean, a unit change from divisions to wave-lengths: ME-6, or ME-1 with
     a defined factor.
   - ME-P2's estimate "H +3.0-4.5 KB" must drop the table bytes that are already CHECKED.
3. **H's after-plan estimate.**
   - Research 7's "physics 20-31%" exceeds the measured ceiling of **21.7%** (24,368 B text, not 30-40 KB). Its upper
     part needs approximation units (2,731 B) to become CHECKED, which D17 rules out.
   - Draft 2 should state ≤ 21.7%.
   - The supplement's trigonometric derivation (h134-h142) has no plan batch, so no batch checks those bytes. It is
     tagged `approximation` and should be named as residual.
4. **The DL target is AlphaFold, not LoRA (P2).**
   - D22 and research 2.4 should name AlphaFold, CC BY 4.0, with the licence evidence.
   - Section 4.4's DL-1 ("highest score in column C"), DL-2 ("average across the eight tasks") and DL-4 ("parameter
     count from a stated formula") have no span in the pinned text: the main text has no result tables, and its
     results are in five figures and the supplement.
   - Replace them with anchored fixtures:
     - the medians and intervals of d024 and d027, already CHECKED with certified order today;
     - the "8× faster" ratio against the stated timings, a DL-3-style reading-set case that fails under rounding at
       2,500 residues;
     - "around 350,000" against the stated 355,993, where the rounded reading fails and only the tolerance reading
       holds;
     - the ablation drops of 0.4, 0.7 and 6.1 GDT.
   - DL-5 ("on par") does not occur in the text; drop it, or keep it as a constructed fixture.
5. **DL's after-plan estimate and ME-P3's DL share.**
   - Research 7's "14-25%" is above the measured ceiling of **13.9%**, and the ceiling is **8.9%** unless the figure
     source data are pinned: `calc-data` is 3,355 B of comparisons whose data are figures.
   - ME-P3's "DL +5-8.5 KB" must be re-derived from the ledger. The addressable bytes are 6,560 B, of which 1,730 B
     are approximation and 3,355 B need unpinned data.
   - Add a decision: pin AlphaFold's figure source data, a data handle under ME-4, or leave those comparisons
     UNFORMALISED.
6. **EX-3 (tensor shapes) has almost no anchor in the pinned DL text.** Its shapes are in the supplement, which is not
   pinned; the main text names array shapes only in a caption (d035). Draft 2 should tie EX-3 to the AlphaFold
   supplement (pin it first) or demote EX-3 to a trigger.
7. **M's source and estimate.**
   - The text is 2,651 B (not 4-6 KB), and both available OCR texts garble the formulas.
   - Add a step before ME-P4: a clean transcription of the paper's formulas, checked by a person against the scan, as
     a translation companion. The source file itself stays the OCR bytes.
   - The ceilings: 10.3% without imports, which fits "6-12% if EX-1 fails". With imports of the theorem statements it
     is 23.2%, above "10-20%".
   - The analytic chain (2,114 B, 79.7%) stays residual even if EX-1 passes. M-4 (RE-WORDED: the case's numbers
     are in the OCR bytes, its words are not) gains the four other pairs of formula (18).
8. **V's estimate and the measure.**
   - V-E1's CHECKED today (1,199 B) is above the 0.3-0.8 KB estimate because stated values (the appendix's 48
     differences) count as CHECKED.
   - Plan section 7 should report CHECKED in two parts: **stated only** (Lean admitted the value) and **in a
     certified relation** (the unit is a premise or the consequence of a Lean-replayed relation). Today these are
     H 276 / 1,582 B, V 817 / 382 B and DL 1,905 / 2,548 B.
   - The CHECKED definition should also say what a premise status of UNKNOWN means. Today it is UNKNOWN for H, V and
     DL, so the certificates are replayed but their non-vacuity is undecided. A premise-consistency route that scales
     to a few hundred stated quantities belongs on the risk list next to item 9.
   - Add V-7b (the six main-text p values over 2¹²) to ME-8's fixtures.
9. **The risk list gains the Rust limit.**
   - A table formalised as W6a facts (about 200 constants) stops at the Rust accelerator's default 5 s wall-clock
     limit, so the document is CheckerUnavailable. It passes with a raised limit.
   - ME-4's data handles, or a Lean-only path for large stated tables, are needed even for a two-table 1887 paper.
     This should be raised with the owner of the Rust fast path.
10. **Placement and record format.** Two deviations from ME-0's wording:
    - ME-0's files are in `docs/research/evidence/math-evidence/`, not `usecases/`.
    - There is no per-target `SOURCE.md`. Its facts are in `raw/fetch-log.json` and the Sources table of `SUMMARY.md`.

    Draft 2 should either accept both, or have ME-P1 move the files and write `SOURCE.md` from those records. The
    bytes and digests do not change.

### 4.3 Cancelled

None. No measurement removes a batch:

- ME-4's role for physics shrinks (H-9 no longer needs it) but remains for V's counts and for data handles.
- EX-3 is weakened (4.2 item 6), not cancelled.
- The approximation words (H 2,731 B, DL 1,730 B, V 376 B; 4,837 B together) are the largest ME-tagged block in H
  and the largest of the four ledgers summed. They are not the largest in DL (`calc-data` 3,355 B) or V
  (`calc-stats` 2,858 B). D17 keeps them OPEN at best. That confirms ME-11's reading sets as the right treatment and
  the low ceilings above.

### 4.4 The NORTH-STAR rows, refreshed (text for the orchestrator; the file is not in this worktree)

- **H (physics):** measured 2026-10-13 on Michelson and Morley 1887 (24,368 B).
  - 7.6% CHECKED today by W6a, of which 6.5% is in units that take part in Lean-certified table relations
    (premise status UNKNOWN).
  - 47.4% LABELLED.
  - 44.9% UNFORMALISED: this plan's features 25.3%, siblings' 19.6%.
  - Ceiling for this plan: 21.7%.
- **M (mathematics):** measured on Ramanujan 1919 (2,651 B, OCR).
  - 0% CHECKED.
  - 90.0% UNFORMALISED: analytic or import 79.7%, bounded `arith` 8.3%.
  - Ceiling: 10.3% without imports, 23.2% with imports of the theorem statements.
- **DL (deep learning):** measured on AlphaFold 2021, CC BY 4.0 (66,858 B).
  - 6.7% CHECKED, of which 3.8% is in certified relations.
  - 74.3% LABELLED (references 24.0%).
  - 19.0% UNFORMALISED: this plan's features 9.8%.
  - Ceiling: 13.9%, or 8.9% without figure data.
- **V (VE's paper):** only the E1 slice is measured (9,937 B of 73,801).
  - 12.1% CHECKED (3.8% in certified relations).
  - 41.1% LABELLED.
  - 46.8% UNFORMALISED (`calc-stats` 28.8%).

## 5. DEFERRED

| Item | Why it was not done in phase 1 |
|---|---|
| Editing NORTH-STAR.md rows M, H, DL, V | The file is in another repository (`ve-northstar`), outside this worktree; the measured text is in 4.4 |
| Clean transcription of Ramanujan's formulas | Needs a person reading the scan (no model calls); proposed as a step before ME-P4 (4.2 item 7) |
| Pinning AlphaFold's supplement and figure source data | Not part of ME-0's pinned text; a draft-2 decision (4.2 items 5, 6) |
| Partition of the rest of VE's paper (63,864 B outside the E1 slice) | ME-0 pins only E1 and the appendix rows; the whole-paper row V needs a later pilot |
| ME-S's bounded re-check (spec 17) | A statement review by the reviewer pair (model calls); not a phase-1 pilot |
| ME-1 to ME-13, ME-P1 to ME-P4 | Product code (`lean/VE/`, `ve/`) |
| EX-1 (Mathlib proofs), EX-2, EX-3, EX-5 | Each waits for a batch (ME-12, ME-9, ME-6 and a pinned supplement, ME-4) and needs product code or Mathlib |
| The pre-registered writing and comprehension eval (D17) | Needs model calls (Sonnet as reader and writer) |
| `usecases/` directories named by ME-0 | The phase-1 brief puts evidence under `docs/research/evidence/`; see 4.2 item 10 |
| Per-target `SOURCE.md` named by ME-0 | Replaced by `raw/fetch-log.json` and `SUMMARY.md`'s Sources table; ME-P1 can write it from them (4.2 item 10) |

## 6. Reproduce

```text
python3 -I research/math-evidence/fetch_sources.py        # verifies the pin; re-fetches ignored pages (see below)
python3 -I research/math-evidence/licence_evidence.py --check
python3 -I research/math-evidence/extract_sources.py --check
P=/home/seyran/code/ve-pilot-20261013T0600Z               # a built checkout of main 406736a4
for t in physics math vepaper dl; do prlimit --as=6442450944 $P/.venv/bin/python -I research/math-evidence/ledger.py $t; done
for t in physics vepaper dl; do prlimit --as=6442450944 $P/.venv/bin/python -I research/math-evidence/ledger.py $t --control; done
prlimit --as=6442450944 $P/.venv/bin/python -I research/math-evidence/date_floor.py
python3 -I research/math-evidence/pilots_zero.py
python3 -I research/math-evidence/fixture_anchors.py
python3 -I research/math-evidence/summarise.py
```

The built `*.ve.md` documents (1.2 MB for H, holding the certificates) are regenerated, not committed. Their SHA-256
is in each `run.json`.

**On a clean clone** (checked on a fresh `git clone` of this branch):

- The physics pages, the Europe PMC XML, the archive.org metadata and the Kerala OCR text are committed. The Kerala
  text is the 1927 Cambridge edition, public domain. `fetch_sources.py` checks each against `fetch-log.json`'s
  SHA-256; `extract_sources.py --check` then re-derives all five sources byte for byte.
- The gitignored third-party pages are fetched again and kept only if they match their pinned SHA-256. On
  2026-10-13 the Hardy OCR text and both arXiv pages matched. The Nature page did not: it is a dynamic page, and two
  re-fetches gave two different digests. The script keeps that page under `raw/refetched/` and exits 1.
- `licence_evidence.py --check` then reads the Nature licence field from the re-fetch and reports the digest
  difference. Everything D22 reads is unchanged: the licence fields of all three candidates, the CC BY result and the
  committed Europe PMC JATS licence. The pinned Nature bytes themselves can only be checked against their SHA-256.
- `pilots_zero.py`, `fixture_anchors.py` and `summarise.py` reproduce their committed outputs byte for byte.
