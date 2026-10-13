# Math-evidence, phase 1: ME-0 (pilots and pre-registered measurements)

> **Status.** Phase 1 of [the plan](../spec/math-evidence-PLAN.md) (draft 4), as the cross-plan review orders it
> (`manage-agents/debates/plan-synthesis/SYNTHESIS.md` 4.1, phase 1: "Pilots: … ME-0"; `edits-math-evidence.md`
> edit 10: "ME-0 runs now"). Branch `research/math-evidence-p1`. No product code (`ve/`, `lean/VE/`, `rust/`,
> `tools/`) is changed and no model is called. Measurement scripts are in `research/math-evidence/`; evidence files in
> `docs/research/evidence/math-evidence/`. "Today's VE" is `main` at `406736a4`, run from its built checkout
> `ve-pilot-20261013T0600Z` (read-only; every `ve` run under `prlimit --as=6442450944`).
>
> **Placement.** The plan's ME-0 names new `usecases/` directories. This run puts the same files under
> `docs/research/evidence/math-evidence/<target>/` instead, as the phase-1 brief directs; nothing else about ME-0 changes.

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
