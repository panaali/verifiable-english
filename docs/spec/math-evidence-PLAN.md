# Science papers in VE (`calc@0`, physical dimensions, `arith@0` with proof imports): buildable plan

## Changes in this draft

Draft 5 (2026-10-13) applies phase 1 (ME-0; [docs/research/math-evidence-phase1.md](../research/math-evidence-phase1.md),
reviewed FIX and fixed: `manage-agents/math-evidence-ph1-review.final.md`, `math-evidence-ph1-fix.final.md`). It is
the "draft 2" that the cross-plan edits and the phase-1 report name. No owner, shared item or build order of the
cross-plan review (`SYNTHESIS.md`, `edits-math-evidence.md`) changes; the last section, "Cross-plan issues for the DRI", lists what phase 1 raises for them.

- ME-0 is **done** (P1 PASS); section 0.1 records every phase-1 result, PASS or FAIL, and what it gates.
- The deep-learning target is **AlphaFold** (Jumper et al. 2021, CC BY 4.0) by D22's rule; LoRA and Registers are
  arXiv non-exclusive (D22, 4.4).
- P4 FAILED: H-4, H-5 and H-9 were CHANGED against the pinned text. H-4 and H-5 now read the source's
  v²/V² = 10⁻⁸; H-9 is the source's table (17 marks, three sessions, Mean, Mean in w. l., Final mean), and it needs
  ME-1 only, so it moves from ME-4 and ME-P2 to ME-1 and ME-P1. Every fixture of 4.1 to 4.3 names its phase-1 anchor.
- New fixtures: H-5b (the 1881 figure 0.04), V-7b (six main-text p values over 2¹²), M-4b (formula (18)'s other
  four pairs), DL-1 to DL-4 from AlphaFold's own numbers; the LoRA-shaped DL-1 to DL-5 are dropped.
- Bytes: every per-batch estimate is replaced by the **measured ceiling** from the ME-0 partition (7). After the plan:
  H ≤ 21.7% (was 20-31%), DL ≤ 13.9% and ≤ 8.9% without figure data (was 14-25%), M ≤ 10.3% without imports and
  ≤ 23.2% with them (was 6-12% and 10-20%), V's E1 slice ≤ 50.7% (whole paper still unmeasured).
- The measure reports CHECKED in two parts, *stated only* and *in a certified relation*, beside the document's
  premise status, which is UNKNOWN for H, V and DL today (7).
- The pilot order "physics, then deep learning, then mathematics" names its basis: bytes a batch can check (0).
- EX-3 (tensor shapes) is demoted to a trigger: the pinned DL text has no equations (5).
- ME-P1 moves the ME-0 ledgers to `usecases/`, writes each `SOURCE.md` from the fetch logs and partitions the rest of
  VE's paper; ME-P4 starts from a person's transcription of Ramanujan's formulas (OCR garbles them).
- Risks gain the Rust accelerator's 5 s default limit and the UNKNOWN premise status (8); both go to the DRI ("Cross-plan issues for the DRI"), with the word "around" and the NORTH-STAR rows.
- No Lean statement of section 3 changes.

> **Status.** Plan draft 5 (2026-10-13), branch `research/math-evidence-p1`; drafts 1 to 4 on `design/math-evidence`
> from `main` at `49de179e`. Draft 5 applies phase 1 (list above); the rest of this note is draft 4's. DRI research wave,
> docs only: no code, proof, test or generated file changed, and no model was called. It is the plan for the design
> recommended in [docs/research/math-evidence.md](../research/math-evidence.md) (cited `research n`), which holds the
> evidence, the measured need, the prior art and the comparison of candidates. Draft 2 applied the converged Astra +
> Fable review of draft 1 (`manage-agents/debates/design-math-evidence/`, REVISE narrowly, CONVERGED after round 3:
> edits A1-A6 and F1-F5 as merged in round 3) and the cross-plan synthesis edits of 2026-10-13 (`SYNTHESIS.md`, ten
> edits). Draft 3 applies the converged statement review of the spec's draft 1
> (`manage-agents/debates/math-evidence-spec/`, FIX, CONVERGED after round 2: Fable's J1-J11 with Astra's
> refinements), with no other design change; the change log lists them. Draft 4 applies the verification of the
> spec's draft 2 (`manage-agents/math-evidence-p3ver1.final.md`, FAIL narrowly) with the spec's draft 3: J2's
> `Run.unknown_named` restored, fixture R-10 for J3, and the draft-2 choices both reviewers must accept by name. The
> Lean blocks of section 3 are the statements the batches prove, written against `main` at `49de179e` as statement
> schemata. ME-S's statement spec, [math-evidence.md](math-evidence.md) (draft 3), elaborates them. Draft 1 of the
> spec was type-checked against `main`'s `lean/` tree in an untracked stub and its fixture numbers computed there with
> `#eval`; drafts 2's and 3's changes are not yet type-checked, and their new fixture numbers were computed by hand,
> both for the reviewers' bounded re-check (spec 17). Where the spec and section 3 differ, the spec governs. Every number is measured (method named) or
> labelled **estimate**.
>
> **Siblings read.** `design/quantities` (research and plan, read 2026-10-13), `design/attitudes`,
> `design/events-time-causation`, `design/act-phrases`, `design/weighing` (plan), `design/scope` (shared pieces). Where
> this plan needs what they own it names a dependency; section 10 lists the shared pieces as the cross-plan review
> settled them.

## 0. Summary

The pinned constitution and UDHR pilots have **no unit** blocked by this topic (research 2.2; measured by ME-0's P3:
0 of 1,132 and 0 of 130 units), so no batch claims a byte there. The need is in three new use cases (NORTH-STAR rows
M, H, DL, weight 3 each, measured by ME-0) and VE's own paper (row V, weight 3; its E1 slice measured): their
checkable spine is calculations, tables, derivations, physical dimensions, statistics and, for mathematics, theorems
about whole numbers.

In the last column, a byte count after a pilot is its **measured ceiling**: the bytes of the ME-0 ledger's units
tagged with that pilot's features, as if every one became CHECKED (7). Approximation units are left out: D17 makes
them reading sets, never CHECKED.

| # | Batch | Hours | Owner | Moves a pilot number? |
|---|---|---:|---|---|
| ME-0 | Pin the targets; baseline partition with today's language | 3-4 | pilot runner | **done** (P1 PASS): H 1,858 B CHECKED, V's E1 slice 1,199 B, DL 4,453 B, M 0 (measured) |
| ME-S | Statement spec, Lean stub, statement review | 4-5 | planner | no |
| ME-1 | Lean core of `calc@0` and the shared `VE.Numbers`: exact values, rounding, claims, verdicts, rendering | 5-6 | Lean | no |
| ME-2 | Wire and service mode `calc`, shapes, identities | 5-6 | Lean | no |
| ME-3 | Python relay `ve/calc.py`, `ve calc check`, fuzz tests | 4-5 | Python | no |
| ME-P1 | Pilot (backend evidence): physics and VE paper, ground calculations and the physics table as companion cases; ledgers to `usecases/`; the rest of VE's paper partitioned | 4-5 | pilot runner | ceiling H +2,216 B, V's slice +469 B |
| ME-4 | Tables pinned by SHA-256; data handles; counts, sums, means | 5-6 | Lean, Python | no |
| ME-5 | Derivations over rational unknowns: Farkas certificates, the square rule | 5-6 | Lean | no |
| ME-6 | Physical dimensions and unit-change invariance; owns `ve-units@2` | 4-5 | Lean | no |
| ME-P2 | Pilot (backend evidence): physics bounds and dimensions; VE paper counts from data | 3 | pilot runner | ceiling H +467 B, V's slice +512 B |
| ME-7 | Exact statistics: mean, variance, SD by squared bounds, sign-flip p, binomial, kappa | 5-6 | Lean | no |
| ME-8 | Consistency of printed numbers: witnesses, enclosures, granularity | 4-5 | Lean | no |
| ME-9 | Algebraic identities: a proved normaliser over ℚ | 5-6 | Lean | no |
| ME-10 | Calculation content in `ve-document@1`; the `calc:` leaf label | 5-6 | Lean, Python | no (turns companions into document units) |
| ME-11 | English: arithmetic phrases, rounding, tables, derivations in Lean's engine | 5-6 | Lean | no (readability) |
| ME-P3 | Pilot (backend evidence): physics complete, VE paper statistics, AlphaFold | 3-4 | pilot runner | ceiling H +752 B, V's slice +2,858 B, DL +1,475 B (+3,355 B more only with figure data) |
| ME-12 | Lean core of `arith@0`: statements, meaning, bounded evaluation | 5-6 | Lean | no |
| EX-1 | **Experiment**: Mathlib proofs of VE's own statements (Bertrand's postulate) | 4-6 | planner, Lean | decides ME-13 |
| ME-13 | Import records (only if EX-1 passes) | 4-5 | Lean, Python | no |
| ME-P4 | Pilot: mathematics, from a person's transcription of the formulas | 2-3 | pilot runner, a person | ceiling M +272 B (+344 B more with imports) |
| EX-2 | **Experiment**: approximations with error bounds; square-root and sum-of-squares certificates | 5-6 | Lean | research |
| EX-3 | **Trigger** (draft 5; was an experiment): tensor shapes for deep-learning equations | — | — | trigger only |
| EX-4 | **Trigger**: folds over lists and induction inside `arith@0` | — | — | trigger only |
| EX-5 | **Experiment**: a 21 MB data file through the service in chunks | 3-4 | Lean, Python | V's raw recounts |

Order:

1. ME-0 now (no code, no dependency). **Done** in phase 1 (0.1).
2. Draft 2 (this draft 5) → ME-S. ME-S's statement review confirms each debate edit with a fixture, and its bounded
   re-check covers the fixtures phase 1 changed or added.
3. ME-1 right after ME-S: it builds the shared foundation `VE.Numbers` and lands before quantities' QT-A2, which
   waits for it. Then ME-1 → ME-2 → ME-3 → ME-P1.
4. ME-4 and ME-5 may overlap. ME-6 follows ME-1 with no other wait and lands before quantities' QT-A7. All three come
   before ME-P2.
5. ME-7 and ME-9 may overlap; ME-8 follows ME-7 (it uses ME-7's `signFlipP_grain`). ME-P3 follows ME-7 to ME-9.
6. ME-10 follows `lean-first/b16g` (or its successor that gives the `document` mode a content hook) and takes its
   place in the document-mode queue; ME-11 follows quantities' QT-E and is third in the English queue. ME-10, ME-11
   and the pre-registered writing and comprehension eval gate the document and English authoring milestone.
7. Independently of ME-2 to ME-11: ME-S → ME-1 → ME-12 → EX-1 (after ME-12's statement API) → ME-13 only if EX-1
   passes → the import part of ME-P4. ME-12 waits for ME-1 because `VE.Arith` imports `VE.Numbers`'s `Verdict`,
   `UnknownReason` and `Outcome` (statement review J6). Imports are always residual support.

ME-5 and ME-12's core are Lean-core work that may run in parallel with the other plans' cores. The rest of ME lands
last among the seven plans (AP → AT → SC-1/SC-2 → QT → WG → ET → SC-3…SC-7 → ME), a preference subject to the
explicit dependencies above. ME-P1 to ME-P3 are backend evidence: companion cases in JSON, not the English
milestone. **Pilot order: physics, then deep learning, then mathematics** (research 7), confirmed by ME-0 on one
basis, named here: **bytes a batch can check**, that is, bytes tagged with this plan's features less the
approximation units (D17) and the comparisons that need unpinned figure data: H 3,435 B, DL 1,475 B, M 272 B without
imports. The share of the source gives the same order (H 25.3%, DL 9.8%). Raw tagged bytes do not: DL has 6,560 B
against H's 6,166 B.

**The first batch that moved a pilot number** is ME-0: it pinned the texts, partitioned every byte, and recorded what
today's VE checks (W6a quantities and linear comparisons, attributions, labels; the 1887 dates are outside W6's
calendar). It needed no product code.

### 0.1 Phase 1: results and what they gate

Phase 1 ran ME-0 against bars pre-registered at `0d9db6e1` before any measurement
([math-evidence-phase1.md](../research/math-evidence-phase1.md) 1; evidence in
`docs/research/evidence/math-evidence/`, today's VE = `main` at `406736a4`). No bar moved after review.

| Item | Bar (phase-1 report 1) | Measured | Result | What it gates |
|---|---|---|---|---|
| P1 ME-0's done-condition | every ledger 100% accounted, documents accepted, `SUMMARY.md` written | H 24,368 B, M 2,651 B, V 8,883 + 1,054 B, DL 66,858 B, all at 100% (Lean coverage); all accepted; premise status UNKNOWN for H, V, DL | **PASS** | ME-0 is done; ME-S may start on this draft; the measure's denominators (7) |
| P2 DL target (D22) | the first ranked candidate whose licence field is CC BY | LoRA and Registers: arXiv non-exclusive; AlphaFold: CC BY 4.0 (Nature page field, Europe PMC JATS) | **AlphaFold pinned** (a rule, not a bar) | DL fixtures (4.4), ME-P3's DL part, EX-3's trigger |
| P3 pilots stay at zero | 0 units and 0 bytes in both pilots | 0 of 1,132 (constitution), 0 of 130 (UDHR) | **PASS** | every batch's constitution and UDHR column stays 0 (7) |
| P4 fixture anchors | no fixture CHANGED or ABSENT | 32 in scope: 14 ANCHORED, 9 RE-WORDED, **3 CHANGED (H-4, H-5, H-9)**, 0 ABSENT, 6 NOT A QUOTE | **FAIL** | H-4, H-5 and H-9 are rewritten (4.2) and re-checked in ME-S (spec 17, item 8); ME-1's and ME-P1's fixtures use the rewritten cases |
| P5 paper denominator | 73,801 B at the ME-0 commit and on `main` | 73,801 B on the branch, on `main` and at `49de179e` | **PASS** | V's denominator (7) |
| P6 H-10, 1887 dates | 1887 refused, 1970-01-01 admitted | `DateRange(1887-07-08)`; 1970-01-01 accepted | **PASS** | H-10 stays refused until ET-T3 (4.2) |
| P7 estimates | not bars | inside: H 1.5-2.5 KB CHECKED (1,858 B), M 0, constitution and UDHR 0; outside: H LABELLED 11,560 B (est. 13-16 KB), H text 24,368 B (30-40 KB), V-E1 1,199 B (0.3-0.8 KB), M text 2,651 B (4-6 KB), DL 4,453 B (2-4 KB for LoRA), every exposition share (below) | reported, not judged | every estimate of 7 is replaced by a measured ceiling |

The plan's experiments did not run in phase 1; each waits for its batch (5): EX-1 for ME-12, EX-2 for ME-9, EX-5 for
ME-4; EX-3 is now a trigger and EX-4 stays one.

**DEFERRED, each with its trigger.**

| Item | Why not done | Trigger |
|---|---|---|
| NORTH-STAR rows M, H, DL, V | the file is in `ve-northstar`, outside this worktree; the measured text is in the phase-1 report 4.4 | the DRI's next NORTH-STAR update ("Cross-plan issues for the DRI", item 4) |
| A person's transcription of Ramanujan's formulas | needs a person reading the scan; OCR garbles 79.7% of M | ME-12 lands; the transcription is ME-P4's first step |
| Pinning AlphaFold's figure source data and supplement | not part of ME-0's pinned text | ME-4 lands **and** D22's licence rule confirms CC BY for those files; until then DL's ceiling is 8.9% |
| Partition of the rest of VE's paper (63,864 B outside the E1 slice) | ME-0 pinned only E1 and the appendix rows | ME-P1, which partitions it first |
| `usecases/` directories and per-target `SOURCE.md` | phase 1 kept the evidence under `docs/research/evidence/` and the pins in `raw/fetch-log.json` and `SUMMARY.md` | ME-P1 moves the ledgers and writes `SOURCE.md` from those records; bytes and digests unchanged |
| ME-S's bounded re-check (spec 17) | needs the reviewer pair (model calls) | this draft |
| The pre-registered writing and comprehension eval (D17) | needs Sonnet as reader and writer | ME-10 and ME-11 land |
| EX-1, EX-2, EX-5 | each needs its batch and product code or Mathlib | ME-12, ME-9, ME-4 respectively |
| EX-3 | the pinned DL text has no equations (ME-0's sentence kinds: 0) | a pinned DL text with method equations over matrix operands (5) |

## 1. Decisions

| # | Decision | Why | Rejected |
|---|---|---|---|
| D1 | A new profile **`calc@0`** with its own mode `calc` and namespace `VE.Calc`. The profile is one row of AR-10's profile-gate table with its own composition proof; the mode registers in AR-10's mode registry and stays separate from `arith` | `order@0` is frozen (`lean/VE/Route/frozen-sources.sha256` lines 191-206), integer-valued, and uses integer cuts that are unsound for real-valued quantities; W6a's `ve-units@1` and its linear integer typing are frozen by the meaning-freeze rule | widening `order@0` or W6a in place |
| D2 | Values are **exact rationals**: core `Rat` (`import Std`, as `lean/Iceberg.lean` uses it with `grind`); no floating point anywhere. The exact-number pieces live in the shared module **`VE.Numbers`** (`lean/VE/Numbers/`), which math-evidence owns and ME-1 builds | exactness is the point; the pinned toolchain has `Rat` and ring automation without Mathlib | binary floats; a VE-defined fraction type (duplicate of `Rat`) |
| D3 | Decimal literals are read by W6a's `VE.Time.parseDecimal` into `VE.Time.Dec`; one new lemma gives its exact value (`decValue`, in `lean/VE/Numbers/Decimal.lean`) | one decimal grammar (W6) | a second decimal parser |
| D4 | A **named value** has one source: *stated* (the text gives it), *defined* (an expression over earlier names), *counted* (an aggregate of a pinned table), or *free* (an unknown, for derivations only) | a reader sees where every number comes from; definitions are non-recursive by construction | implicit values; recursive definitions |
| D5 | A printed number keeps its **written places** ("0.30" is two places, "0.3" one); the scientific form "2 times ten to the power 7" has the places of its last written digit (here minus 7) | the precision a reader sees is part of the claim | a default precision; significant-figure guessing |
| D6 | **One rounding definition with two declarable tie rules.** The default rule is ties upward; a case may declare *half to even on the exact value*. Each rounding sentence names its rule ("… 0.296 when rounded to three decimal places, with exact ties going up"), and Lean's rendered line for every rounding claim names it. In translation an exact tie under an undeclared rule is a reading set (fixture V-8). The definition lives in `VE.Numbers`, which ME-1 builds; quantities' QT-A2 proves `roundsTo_ratio_agree` against it. Declaring a **software convention** picks no rule: it splits each claim into the **exact claim**, which VE decides, and **software reproduction**, which is UNKNOWN with the reason "floating-point computation not modelled" (VE has no floating-point semantics and this plan names no way to establish equivalence to exact computation). A failed exact claim under a software convention is never a source finding (fixtures V-9, V-10). A closed interval that accepts both neighbours at a tie is a separate approximation relation with its own name and wording if a batch needs it; it is never the meaning of "rounded" | one reading per rounded number; VE cannot decide what a program printed: floating-point error moves values that are not ties across a rounding boundary (V-10) | a tie-tolerant "either neighbour" meaning (two readings in one); a second rounding definition; a rule that imitates a program's printing |
| D7 | Verdicts: **holds**, **fails**, **undefined** (a missing value, a zero divisor). The operational outcome adds **unknown** with a named reason (a limit, floating-point computation not modelled, an inconclusive search, an unbounded statement); a decided outcome equals the mathematical verdict and unknown arises only for its named reason. In translation a claim that fails is a finding, reported with exact values: a **source finding** ("The source's numbers disagree: …") only when Lean has checked every stated value and printed number the claim reads against its `span` in the pinned source bytes (the source registered as a data handle, ME-4) and the case declares no software convention; otherwise "The case's numbers disagree; transcription unchecked: …", the only form before ME-4. In authoring a failure is an error to fix | statcheck and GRIM report inconsistencies, they never repair them (research 3.5); "undefined" is not "false"; a typed-in table or paraphrase may carry a typo, which must not become a false finding against the source | turning a failed source calculation into a rejected translation; blaming the source for an unchecked transcription |
| D8 | Ratios of **counts of vocabulary objects** ("16 of the 18 policymakers") belong to quantities' `cardinality@0` and its wording "X out of Y"; `calc@0` ratios are of stated or table-derived **numbers**, worded "X divided by Y" | one owner per wording; both share D6's rounding | two wordings for one meaning |
| D9 | **Tables pinned by SHA-256**: Lean computes the digest (`VE.CertificateWire.sha256`) of bytes the relay transports; the service keeps data handles like its environment handles; CSV and JSON-lines subsets; filters and count, sum, mean, minimum, maximum | a number bound to bytes anyone can hash; Python transports, never computes | Python-side aggregation; trusting a supplied digest |
| D10 | JSON numbers in data are read by their **written digits** as exact decimals; derived float files (`paper/generated/posthoc-e1.json`'s `-0.14999999999999997`) are not used for exact recomputation; exact work starts from integer counts | binary floats carry noise that flips exact ties | re-deriving exact values from floats |
| D11 | **Derivations over rational unknowns** by Farkas certificates that a Fourier-Motzkin search in Lean produces and a proved checker replays; no integer cuts; plus one proved nonlinear rule ("from 0 ≤ x, x² < a, a ≤ b², 0 < b infer x < b") | linear reasoning over ℚ is complete with Farkas certificates; `order@0`'s frozen integer module cannot be reused for rational unknowns, so a rational module is a different owner's logic, not a copy | Python certificate search (the directive keeps Python to CLI, files, display); cuts |
| D12 | **Physical dimensions**: a unit declares integer exponents over declared base dimensions and an exact positive factor to the coherent unit; sums and comparisons need equal dimensions; the theorem is **unit-change invariance**. Affine units (degrees Celsius) and logarithmic units (decibels) are refused by name. Declared in `ve-units@2`, which ME-6 owns and decodes (the only decoder); quantities' QT-A7 consumes it and uses `convert_by_factors`. `ve-units@1` tags stay nominal: identically declared tags remain incompatible (`units-schema.md` 2.1). `day`, W6a's calendar-date tag, is never a unit of a physical dimension and never converts; durations use `elapsed_day` | Buckingham and Bridgman (research 3.4); one unit registry | a second unit schema; conversions without dimensions; equating legacy tags by their declarations |
| D13 | Called **physical dimension** in prose and `base_exponents` on the wire | quantities' `scales@0` already uses "dimension" for a comparison scale | reusing the word for two things |
| D14 | **Statistics**: only procedures with an exact rational meaning (counts, rates, means, sample variance, exact sign-flip and binomial tail probabilities, Cohen's kappa) or a rational characterisation (a square root by squared bounds). Quantiles of continuous distributions (Student's t) are *stated* constants with their source. Each procedure carries its **assumptions as named residual leaves** | exact recomputation; no floating special functions in the trusted core; the paper itself names its assumptions (`paper/analysis/README.md`) | a statistics library in Lean; hiding assumptions |
| D15 | **Consistency of printed numbers**: given that inputs were printed rounded, a *witness* (exact inputs inside their rounding intervals reproducing every printed output) proves consistency; an *enclosure* (exact interval arithmetic over the boxes) proves inconsistency; otherwise unknown | GRIM and statcheck in Lean, with certificates both ways | float re-computation |
| D16 | **Algebraic identities** by a proved normaliser for polynomials and rational functions over ℚ; the side conditions are exactly the nonzero divisors `Denotes` already requires | derivation steps in physics are mostly identities ("D/(V − v) + D/(V + v) = 2DV/(V² − v²)") | trusting a computer-algebra system |
| D17 | **English**: words only; fixed phrases ("the product of A and B", "A divided by B", "the square of A", "rounded to three decimal places"); a **name for every intermediate value** instead of nested formulas; a formula view is an optional display, never input. "About", "approximately", "roughly", "nearly" are refused in authoring with rewrites and become reading sets in translation; they are one row of english-lean's catalogue shared with quantities. Lean renders claim lines from ME-1 (display only); input wordings join Lean's English engine after english-lean E3 (ME-11). The comparison phrases ("is less than", "is at most") have one Lean owner. The user-facing English authoring milestone needs a pre-registered writing and comprehension eval (Sonnet as reader and writer, as in the readability eval); ME-P1 to ME-P3 are backend evidence | zero-training English; one reading per sentence; internal parse-back does not show that people read and write it | symbols in VE text; a Python English parser; two owners for one wording |
| D18 | **Documents**: `calculation` content in `ve-document@1` goes through Lean's `document` mode; a claim-graph leaf labelled `calc:<case>/<claim>` is discharged by the calc route; `support: calculation` counts as checked only when Lean recomputed it | the support field exists (`document.md`) and is only a label today | a Python document branch |
| D19 | **Mathematics** is a separate profile **`arith@0`**: whole numbers and integers, addition, subtraction, multiplication, divisibility, order, functions and predicates defined by non-recursive terms and formulas, bounded and unbounded quantifiers; meaning `VE.Arith.Holds` in core Lean, where a count is the number of values for which `Holds` of its condition is true (classical decision), never defined through the evaluator; **bounded evaluation** decides statements whose quantifiers are all bounded, within a stated budget (one unit per formula-node visit, as W6's `VE.Time.evalB`; default and maximum 1,000,000); exhaustion is UNKNOWN, tested apart from undefined values; `arith@0` is one row of AR-10's profile-gate table and its mode stays separate from `calc` | finite checks ("by actual verification ... for smaller values") are decidable; the rest needs proofs VE does not search for | function symbols, recursion or induction inside the tableau (research D4, rejected) |
| D20 | **Proof imports**: a Lake project outside `lean/` (`imports/mathlib/`) requires Mathlib and VE and proves `VE.Arith.Holds ... s` for VE's own statement `s`. Lean renders the definitions `D` and the statement `φ` as Lean terms, and the import project compiles a generated `theorem check : Defs.Means ⟨D⟩ ⟨φ⟩ := <declaration>`, so the external kernel checks the declaration's type, not just its axioms. VE's record binds the statement's id, the digest of VE's meaning sources (the VE `lean/` revision), the project revision, toolchain, Mathlib revision, declaration, the generated check file's digest and the axioms; each imported conclusion needs an import with its own statement id. Admission stays conditional on that external build. The import enters reports only as a leaf labelled `import:<project>@<revision>/<declaration>`, counted in the residual (VISION rule 6). Never linked into `ve_service`. Built only if EX-1 passes | the statement a reader approves is the statement Lean proves; VE's trusted runtime does not grow | Mathlib inside `lean/`; hand-written Lean statements reviewed against English (the iceberg's gap) |
| D21 | **Rust: none.** Python: the `ve calc` and `ve arith` commands, file reading, relays, display; no arithmetic, no search | `CLAUDE.md` ownership; exact arithmetic is cheap in Lean | a Rust accelerator before a measured need |
| D22 | **Targets** (research 2.4): physics = Michelson and Morley 1887 (public domain); mathematics = Ramanujan 1919 (public domain); deep learning = the first of the ranked candidates whose CC-BY licence ME-0 confirms by reading the licence field of its abstract page with a plain HTTP fetch and no model; VE's own paper is the in-repository fixture source. **Result (ME-0, P2):** LoRA (arXiv 2106.09685) and Registers (arXiv 2309.16588) carry arXiv's non-exclusive licence, so deep learning = **AlphaFold** (Jumper et al. 2021, *Nature* 596: 583-589), CC BY 4.0 by the Nature page's `license` field and the Europe PMC JATS licence; pinned as the JATS text of PMC8371605 (66,858 B). The Nature page is dynamic, so its pinned bytes are checked only against their SHA-256; the committed JATS licence and the three licence fields re-derive. Research 2.4's ranking stays the record of the rule's inputs | measured claims only; no copied text without a licence | storing a text whose licence is unconfirmed |

## 2. Design

### 2.1 A calculation case

A case is a JSON object of format `ve-calc@0`. Example (fixture V-2, VE paper `04-e1.md`):

```json
{"format": "ve-calc@0",
 "rounding": "ties-up",
 "values": [
   {"name": "approved_strict", "words": "the number of weakening attacks approved in strict VE", "stated": "52"},
   {"name": "approved_symbols", "words": "the number of weakening attacks approved in symbols", "stated": "31"},
   {"name": "attacks", "words": "the number of weakening attacks", "stated": "243"},
   {"name": "rate_strict", "words": "the false-approval rate in strict VE",
    "defined": ["div", ["val", "approved_strict"], ["val", "attacks"]]},
   {"name": "rate_symbols", "words": "the false-approval rate in symbols",
    "defined": ["div", ["val", "approved_symbols"], ["val", "attacks"]]},
   {"name": "increase", "words": "the increase in percentage points",
    "defined": ["mul", ["lit", "100"], ["sub", ["val", "rate_strict"], ["val", "rate_symbols"]]]}],
 "claims": [
   {"id": "c1", "claim": ["rounds", ["val", "rate_strict"], "0.214"]},
   {"id": "c2", "claim": ["rounds", ["val", "rate_symbols"], "0.128"]},
   {"id": "c3", "claim": ["rounds", ["val", "increase"], "8.6"]}]}
```

- `values` are in order; a `defined` value uses only earlier names; names are unique identifiers; `words` follow W6's
  verbalisation rules (whitespace-normalised, distinct up to sentence-initial capitalisation, diagnostic
  `VerbalisationCollision`), checked by the Lean check W6a already runs, reused rather than copied.
- Expressions: `["lit", decimal]`, `["sci", decimal, exponent]` ("2 times ten to the power 7"), `["val", name]`,
  `["add", a, b]`, `["sub", a, b]`, `["mul", a, b]`, `["div", a, b]`, `["pow", a, natural]`.
- Claims: `["eq" | "lt" | "le", a, b]`, `["within", e, low, high]` (inclusive), `["rounds", e, printed]` (places from
  the printed spelling; the case's `rounding` gives the tie rule: `ties-up`, the default, or `half-even`, half to even
  on the exact value; `["rounds-down", e, printed]` and `["rounds-up", e, printed]` for printed bounds).
- A case may declare a software convention, `"software": "<name>"` (D6): each claim is then decided as an exact claim
  and also reported with a software-reproduction row that is UNKNOWN, reason "floating-point computation not
  modelled".
- Each `stated` value may carry `"support"` (`observation`, `testimony`, `assumption`) and `"span"` (bytes in the
  pinned source); the report lists them as the residual a claim rests on. Before ME-4 a span is recorded but not
  checked; from ME-4 Lean checks it against the source's bytes (2.5).
- Limits, checked first and in this order: 10,000 JSON nodes, expression depth 64, 512 values, 512 claims, exponents
  at most 64, literals at most 40 digits (W6's numeral limit); a `pow` or `div` chain whose exact result would exceed
  4,096 digits in numerator or denominator gives **unknown** with the limit named.
- From ME-5, ME-8 and ME-9 a `claims` entry may also be a derivation, a consistency check or an identity (2.6, 2.9,
  2.10). Each kind has its own meaning, a row theorem per outcome, and its own response fields (a certificate, a
  counterexample, a witness, a refutation or a point); spec 3.1 and 3.4 give the full wire and the rows, and spec 13.6
  a complete request and answer per kind (statement review J3).

### 2.2 Identity

The case's `meaning_id` is the environment-bound identity (the `ve-meaning-…` domain W6a uses, `Admission.meaningId`)
over the canonical case with `words` excluded: value literals in canonical form ("0.30" and "0.3" as values are one
value), printed numbers with their written places ("0.30" and "0.3" as rounding targets are two claims). A renamed
verbalisation does not change the meaning; the approved wording is bound separately, as for W6a constants. Each claim has its own id: the case id plus the claim's
canonical JSON. Changing a value, a source, a tie rule or a printed spelling changes the id and voids every approval
or citation of it. The frozen canonical encoder (`VE.CertificateWire.canonical`) accepts only natural JSON numbers and
sorts object keys, so the canonical case and environment write every signed integer (printed places such as H-8's
−7, unit exponents such as a velocity's −1) as a canonical decimal string, and the encoder stays unchanged
(statement review J1; spec 3.3, fixtures I-1 and I-2).

### 2.3 Values and printed numbers

A printed number is a pair `(D, k)` read from its spelling: "0.296" is (296, 3), "8.6" is (86, 1), "0.40" is (40, 2),
"2 times ten to the power 7" is (2, −7). Its value is D / 10^k. Rounding a value x to the printed (D, k):

- ties upward: (2D − 1)/2 ≤ x·10^k < (2D + 1)/2;
- half to even on the exact value: the same, except that x·10^k = (2D − 1)/2 or (2D + 1)/2 counts only when D is
  even;
- rounded down (a printed lower bound): D ≤ x·10^k < D + 1; rounded up: D − 1 < x·10^k ≤ D.

### 2.4 Claims, verdicts and findings

A claim **holds** or **fails** when every value it mentions denotes; it is **undefined** when a value is free or
missing or a divisor is zero. These three are the mathematical verdict. The operational outcome is either that verdict
or **unknown** with a named reason, here a limit reached (2.1); a limit hit is never reported as undefined, and a
zero divisor never as unknown. Lean reports, for each claim, the outcome, the exact value of every side as a reduced
fraction, its decimal display at the printed places, the names it depends on with their sources and supports, and one
English line (2.11). In a translated document a failed claim stays CHECKED with a **finding**, and nothing is
repaired. The finding is a source finding, "The source's numbers disagree: 52 divided by 243 is 0.21399…, which rounds
to 0.214, not 0.213", only when Lean has checked every stated value and printed number in the claim against its `span`
in the pinned source bytes (2.5) and the case declares no software convention. Otherwise it reads "The case's numbers
disagree; transcription unchecked: …", the only form before ME-4; under a software convention the exact-value form
names the convention and never blames the source.

### 2.5 Tables and data handles

- A case may declare `"data": [{"handle": sha256, "format": "csv" | "jsonl", "columns": {name: "text" | "number" |
  "bool"}}]`. A request registers the bytes under their SHA-256 (as environment handles are registered,
  `VE.Service.Handles`); Lean recomputes the digest and refuses a mismatch. The relay reads the file and sends its bytes;
  it never parses them.
- CSV subset: comma separator, double-quote quoting, a header row, LF or CRLF line ends; JSON lines: one object per
  line, columns read by top-level key. Numbers are read by their written digits (D10); "true"/"false" for booleans;
  a missing key or empty field is *absent*.
- A `counted` value is `{"data": sha256, "filter": F, "aggregate": A}` with filters `["is", column, text]`,
  `["is-not", column, text]`, `["equals", column, number]`, `["not-equals", column, number]`, `["true", column]`,
  `["false", column]`, `["and", F, F]`, `["or", F, F]`, `["all"]` and aggregates `"count"`, `["sum", column]`,
  `["mean", column]`, `["min", column]`, `["max", column]` (ME-7 adds `["variance", column]` and
  `["population-variance", column]`). There is no general negation: each negated atom selects only a cell of its
  type, so "that are not approved" selects the Boolean false, and a row whose cell is absent or mistyped is selected
  by neither "that are approved" nor "that are not approved" (statement review J9). Over an empty selection, count and
  sum are 0, and mean, minimum and maximum are **undefined**. Over a selection with an absent or non-number cell in its
  column, sum, mean, minimum and maximum are **undefined**.
- Each counted value is computed within the case's budget on its own. A counted value keeps its mathematical value
  (the aggregate of the pinned table) apart from its operational result, which is that value or **exhausted**; an
  exhausted value makes every claim that reads it, directly or through definitions, **unknown** with the evaluation
  limit named (statement review J2).
- The pinned source of a translated document is registered the same way, as a data handle. Lean then checks each
  stated value's and printed number's `span` against those bytes; a span whose text does not read as the stated
  number, written places included, is refused (`SpanMismatch`).
- Limits: 16 MB per handle in this batch (the service's line cap; EX-5 adds chunks), 1,000,000 rows, 64 columns, and
  the same evaluation budget as W6a (1,000,000 evaluations, `VE.Time.Budget`); exhaustion is **unknown**.

### 2.6 Derivations over unknowns

A case may declare `free` values (unknowns) and **premise** claims about them, and ask whether a claim **follows**:
the check `["follows", claim, [premise ids], [[square, root], …]]`, whose premises are entries of the case's
`premises` list, each with its `support` (statement review J3; a premise is not itself a reported claim). Lean inlines
the stated, defined and counted values, linearises (a premise that is not linear in the unknowns is refused, naming
the term), searches Farkas multipliers by Fourier-Motzkin elimination within a budget, and checks them; a square link
`s = r²` with `0 ≤ r` allows one proved step of the square rule (D11). The reader sees both halves of each link: it is
rendered as two numbered premises, "S equals the square of R." and "R is at least 0.", each `support: assumption`,
and listed as a residual line; the wire keeps links apart from ordinary premises (statement review J10). Outcomes: **follows** (with the replayed certificate), **does not follow** (with exact
values of the unknowns satisfying every premise, every square link and its nonnegativity condition, and refuting the
claim, checked by evaluation; for purely linear
premises Fourier-Motzkin yields such values whenever no certificate exists, and across a square link the search tries
the claimed bound itself), or **unknown** (budget, or a nonlinear step the rule does not cover). Physical laws ("the displacement is proportional to the square of the
velocity") enter as named premises with `support: assumption`, never as truths.

### 2.7 Physical dimensions

The environment carries `ve-units@2` (owned and decoded by ME-6; quantities' QT-A7 consumes it, section 10 piece 3):
base dimensions (identifiers,
for example `length`, `time`, `mass`, and document-declared ones such as `fringe`), and units with `base_exponents`
(for example `{"length": 1, "time": -1}`) and an exact positive `factor` to the coherent unit of that physical dimension.
A unit is also a value: "11 meters" is `["mul", ["lit", "11"], ["val", "meter"]]`. Each value declares its physical
dimension; literals are dimensionless. Lean infers the physical dimension of every expression and refuses a sum,
difference or comparison of different physical dimensions (`DimensionMismatch`, naming both) and a rounding claim on a
non-dimensionless expression (the printed number must say its unit: "the displacement divided by one fringe width
rounds to 0.4"). Conversions are no extra declaration: two units of one physical dimension convert by the ratio of
their factors. `ve-units@1` tags stay nominal: two identically declared tags remain incompatible, as
`units-schema.md` 2.1 says, and `ve-units@1` environment identities are unchanged. `day`, W6a's calendar-date tag, is
never a unit of a physical dimension and never converts; a declaration that gives `day` `base_exponents` is refused.
Durations use `elapsed_day`.

### 2.8 Statistics

New expression forms over a table column or a list of values: `["mean", xs]`, `["variance", xs]` (sample, divisor
n − 1), `["population-variance", xs]` (divisor n), `["sign-flip-p", xs]` (two-sided, exact over all 2^n sign vectors,
n ≤ 16), `["binomial-tail", n, k, p]` (P(X ≥ k)), `["kappa", table]` (Cohen's kappa of a square agreement table). A
list is a list of names of stated or counted values; a table column is a counted aggregate (the mean and the two
variances; the sign-flip p takes a list only). A square root appears only in claims: `["sqrt-rounds", e, printed]`
means "the square root of e, rounded, is printed", defined by squared bounds (exact). Outside its domain a statistic
is **undefined**, like a division by 0: the mean, the population variance and the sign-flip p need one value, the
sample variance two, the binomial tail 0 ≤ p ≤ 1, and the square root a value at least 0 (statement review J5;
unguarded, the formula gives a "probability" of 2 at n = k = 1, p = 2). Each form carries its assumption leaves, rendered in the residual: sign-flip,
"the differences are independent and their signs exchangeable under the null"; binomial, "the trials are independent
with one success probability"; t-based half-width, "the stated quantile is the 97.5% point of Student's t with 11
degrees of freedom" (a stated constant with `support: testimony` and its source).

### 2.9 Consistency of printed numbers

`["consistent", inputs, outputs]`: the inputs are printed values (each with its rounding interval), the outputs are
claims. Two certificates, both checked exactly: a **witness** (exact inputs inside their intervals under which every
output claim holds) proves *consistent*; an **enclosure** (interval evaluation over the input boxes for `add`, `sub`,
`mul`, `div` with a divisor interval not containing zero, `pow`, and squared bounds for square roots) that misses an
output's printed interval proves *inconsistent*. A granularity rule covers enumeration counts: an exact sign-flip p over
n values is a multiple of 1/2^n, so a printed p with no such multiple in its rounding interval is inconsistent.
Otherwise *unknown*. Lean searches witnesses by trying the printed values themselves and the interval endpoints; a
witness from elsewhere is replayed the same way. Both certificates are proved against **one** proposition,
`Consistent`, under **one** name rule: an output may read the inputs and any value that is not free, and a stated value
left out of the inputs keeps its exact value, in the witness as in the enclosure. The checkers work on the outputs with
every other value inlined and the inputs kept, never replaced by their printed values (statement review J4; spec 8.1,
fixture C-1).

### 2.10 Algebraic identities

`["identity", a, b]` over free values: Lean first inlines the named values the sides read (statement review J3), then
normalises both sides to polynomials over ℚ (sorted monomials, merged
coefficients, zeros dropped) or, with division, to numerator and denominator, compares cross-multiplied normal forms,
and reports **identity** or **not shown** (with a rational point where the sides differ when one is found by trying
small values; otherwise unknown). Soundness needs only that equal normal forms mean equal values wherever both sides
denote; the nonzero-divisor side conditions are those of `Denotes`.

### 2.11 English

Reader-facing wordings (one reading each; rendered by Lean from ME-1, readable as input after ME-11):

| Wording | Meaning |
|---|---|
| "The path length is 11 meters." | stated value with unit |
| "The expected displacement is twice the path length divided by the wavelength, times the square of the speed ratio." | **refused**: two parses; rewrite: "Let the path in wavelengths be the path length divided by the wavelength. Let the squared ratio be the square of the speed ratio. Let the expected displacement be twice the product of the path in wavelengths and the squared ratio." |
| "Let the speed ratio be the orbital speed divided by the speed of light." | defined value |
| "A equals B", "A is less than B", "A is at most B", "A is from L through H" | comparisons (W6's wordings, one Lean table: D17) |
| "The false-approval rate is 0.296 when rounded to three decimal places, with exact ties going up." | `rounds`, ties upward |
| "The p value is 0.007812 when rounded to six decimal places, with exact ties going to the even digit." | `rounds`, half to even on the exact value |
| "The lower bound is 0.019 when rounded down to three decimal places." | `rounds-down` |
| "Let the count of approved 32B trials be the number of rows of the trial table whose judge is 32B, whose view is symbols, whose explanation is none, whose label is bad and that are approved. The count of approved 32B trials equals 176." | counted value, then a claim; the table's digest is shown on request |
| "The standard deviation of the twelve differences, with divisor eleven, is 0.108 when rounded to three decimal places." | `sqrt-rounds` of the sample variance; "standard deviation" alone is a reading set {divisor n − 1, divisor n} in translation and refused in authoring |
| "From these, it follows that the velocity ratio is less than 1 divided by 4." | a derivation; the premises are listed above it as numbered sentences using "equals" ("The displacement equals the product of 0.4 and the squared velocity ratio."), and each square link as two of them (statement review J10) |
| "The round-trip time is the sum of the path length divided by the speed of light minus the speed and the path length divided by the sum of the speed of light and the speed." | **refused**: "and" at two levels and "minus" inside "divided by" give several parses; rewrite: "Let the closing speed be the speed of light minus the speed. Let the outward time be the path length divided by the closing speed. Let the return time be the path length divided by the sum of the speed of light and the speed. Let the round-trip time be the sum of the outward time and the return time." |
| "The round-trip time is the sum of the outward time and the return time." | **refused**: "A is E" with an expression E is a definition or a claim; rewrites "Let the round-trip time be …" or "The round-trip time equals …" (statement review J7) |
| "The rate is 0.3 when rounded to two decimal places, with exact ties going up." | **refused** (`PlacesMismatch`): the spelling has one place, the phrase two; rewrites "0.30 when rounded to two decimal places" or "0.3 when rounded to one decimal place" (statement review J8) |

Arithmetic phrases: "the sum of A and B", "A minus B", "the product of A and B", "A divided by B", "twice A", "half
of A", "the square of A", "the cube of A", "A to the power N", "D times ten to the power N". Operands are names,
numbers or one of these phrases with name or number operands; deeper nesting is refused with the rewrite "Let ... be
..." naming the inner value. Every rewrite that names a value uses "Let ... be ...", and claims and premises use
"equals"; "is" followed by anything but a numeral, a comparison phrase or a rounding phrase is refused, and "be" is a
reserved word in value words (statement review J7). Refused words with rewrites: "the difference between A and B" (many readers take it to
mean the size of the gap; rewrite: "A minus B"); "about", "approximately", "roughly", "nearly" (one row of
english-lean's catalogue shared with quantities, which QT-A6 adds), "on the order of" (rewrite: the rounding sentence or
an inclusive range); "on par", "comparable" (an open term with a decider); every symbol (`+`, `×`, `/`, `^`, `=`, `≈`)
in VE text. The formula view (`2D v²/V²`) is a display generated from the meaning and never parsed. The document-wide
sentence "Numbers in this document are rounded half to even." is not a wording yet: it needs scope's anchor reach for
section-scoped declarations (section 10, piece 11), which is not yet a build item, and even then each sentence's
paraphrase still names its rule.

### 2.12 Documents, statuses and the residual

A unit with `calculation` content is CHECKED when Lean decided every claim (holds or fails; a failure is a finding in
the ledger's `findings` list), OPEN when a claim is unknown (the limit named), and UNFORMALISED with reason
`missing-input` when a value is undefined. Its residual lines, in W2's `support` provenance field (`document.md`; no
new line format), are its stated values' supports, its data digests, its procedures' assumptions, its free values'
premises and, for imports, the import label. A claim-graph leaf
`calc:<case>/<claim>` may stand in a document's claim graph; Lean's `document` mode discharges it by running the case
and requiring **holds**; a W6a or relational claim may not cite it until a bridge between the profiles is designed
(out of scope).

### 2.13 Mathematics: `arith@0` and proof imports

Statements about whole numbers (0, 1, 2, …) and integers: terms are numerals, variables, sum, difference, product,
calls of defined functions and bounded counts ("the number of primes from 1 through x"); formulas are equality, order,
divisibility, calls of defined predicates, connectives, quantifiers over whole numbers and integers, and bounded
quantifiers ("for every whole number n from 1 to 161"). A count's condition must itself be bounded. Definitions are
non-recursive: a function by a term, a predicate by a formula, each over earlier names only ("a whole number p is
prime exactly when p is at least 2 and no whole number from 2 to p minus 1 divides p"). Meaning:
`VE.Arith.Holds`, in core Lean; a count is the number of values for which `Holds` of its condition is true, so the
meaning never depends on the evaluator. Lean decides a statement whose every quantifier is bounded, by evaluation within
a budget (true, false with the deciding value of its outermost bounded quantifier, or unknown). Spec 12.5 gives the
`ve-arith@0` request, its limits and identity, its rows (holds, fails, unknown), their theorems and the refusals of
unscoped variables and unknown calls (statement review J3). The budget is stated: one unit per formula-node visit as in
W6's `VE.Time.evalB`, default and maximum 1,000,000, and a case may set a smaller one; exhaustion is unknown and is
tested apart from undefined values. An unbounded statement is stated, rendered and identified; it is proved only by an
import (ME-13, if EX-1 passes). An import record names the statement's `meaning_id`, the digest of VE's meaning
sources, the import project and its revision, the Lean toolchain, the Mathlib revision, the declaration, the digest of
the generated check file and the axioms. Lean renders `D` and `φ` as Lean terms; the import project compiles the
generated `theorem check : Defs.Means ⟨D⟩ ⟨φ⟩ := <declaration>`, so the external kernel checks the declaration's type.
`tools/lean_import_check.py` (a tool, not the service) builds the import project and prints axioms; Lean's `arith`
mode admits the record (statement identity for each conclusion, meaning-source digest, check-file digest, axiom
allowlist, names) and the report carries the leaf `import:imports/mathlib@<revision>/<declaration>`. Admission stays
conditional on that external build. The residual line reads "Proved in Lean with Mathlib at revision …, declaration
…; VE did not replay this proof."

### 2.14 One owner; deleted or not duplicated

| Piece | Owner | This plan |
|---|---|---|
| Decimal literals and their exact value | `VE.Time.Decimal` (`parseDecimal`, `Dec`, `lower`, `decimal_exact`) | reused; `decValue` and the lemma `decValue_lower` (the exact value agrees with W6's coordinate) added in `lean/VE/Numbers/Decimal.lean`, nothing copied |
| Rounding with a tie rule | `VE.Numbers` (`lean/VE/Numbers/Round.lean`, section 10, piece 2): quantities' integer-ratio rounding is its special case | ME-1 builds it; QT-A2 proves agreement (`roundsTo_ratio_agree`) |
| Comparison phrases ("is less than", "is at most", "is more than", "is at least") | today `ve/english.py:51` (`_COMPARISONS`) | whichever of ME-1 and quantities' QT-E lands first moves them into one Lean table; Python reads them from a generated file; ME-11's English engine replaces `Render.lean`'s phrase table rather than sitting beside it |
| Verbalisation rules for named values | W6a (`VerbalisationCollision`, `VE.Time.Wire`) | reused |
| SHA-256 and canonical JSON | `VE.CertificateWire.sha256`, `VE.CertificateWire.canonical` | reused |
| Handle tables | `VE.Service.Handles` (environment handles) | extended with a data kind in the same table, not a second table; no shared record-shape project |
| Linear arithmetic over integers with cuts | `order@0` (frozen) | not touched; rational linear forms are new (D11) and say why in their file header |
| Counts of vocabulary objects, "X out of Y" | quantities' `cardinality@0` | not duplicated (D8) |
| Unit tags, unit declarations, conversions | W6a `ve-units@1` (nominal tags, unchanged); `ve-units@2`, owned and decoded by ME-6 | `ve-units@2` with physical dimensions and factors (D12); quantities' QT-A7 drops its `converts` design and `convert_iff` and uses `convert_by_factors` |
| Open terms, reading sets, kinds, `support` | W2 (`document.md`) | reused; `support: calculation` gains a check (D18); residual lines use W2's `support` provenance field |
| Attribution of cited results | `reports@0` | reused for citations |
| Likelihood words ("probably") | attitudes | hedged calc units stay `hedged` labels until a separately reviewed calc–attitudes bridge exists: attitudes' conditions are quantifier-free chain formulas, not calc claims, so attitudes landing does not lift the label; no plan owns that bridge yet |
| Dates of observation sessions | W6a dates (`VE.Time.Calendar`, the one calendar); events-time-causation for events | reused; no new date code; dates before 1970 are a recorded W6 trigger (ET-T3) |
| English engine and lexicon | english-lean (E3); quantities' QT-E moves W6's wordings | ME-11 adds rules there, third in the serialised English queue; the approximation words are one shared catalogue row; no Python English |
| Profile registration | AR-10's profile-gate table (its scope includes `lean/VE/Compose/Dispatch.lean:417–474`) and mode registry | one AR-10 table row per profile, with its composition proof (`calc@0`, `arith@0`) |
| Proof checking of imports | the Lean kernel in the import project's build | VE checks the record, not the proof (D20) |

**Deleted:** nothing on `main` duplicates this topic's logic. The plan adds no Python arithmetic, so nothing in Python
needs deleting. Paper reanalysis scripts (`paper/analysis/*.py`) are experiment tooling, not product logic; VE's
recomputation is an independent check of the paper's text against its data, so it is not a second owner of the
paper's analysis.

### 2.15 What stays open (never certified)

The truth of stated values and of data files (a digest binds a claim to bytes, not bytes to the world); the
applicability of a physical law or a statistical model; the choice of a test; a stated quantile's correctness; whether
an imported Mathlib proof is correct beyond the pinned build's acceptance; every interpretive sentence ("it seems fair
to conclude"); likelihood hedges (hedged calc units stay `hedged` labels until a separately reviewed calc–attitudes
bridge exists); software reproduction, that is, whether a program printed a number (always UNKNOWN, "floating-point
computation not modelled", D6); exposition, which stays LABELLED.

## 3. Lean statements

Schemata (status note), corrected by drafts 2 and 3; [math-evidence.md](math-evidence.md) gives the elaborated
statements. Draft 3 changes the schemata only where the statement review changed a statement (3.1's `run_unknown`,
3.3's filters and counted values, 3.7's consistency, 3.9's rows and the EX-1 snippet); the spec's `Check` type and
its row theorems (spec 3.4), the lowering (spec 2.7), the derivation, consistency and identity meanings (spec 5, 8)
and the `arith@0` runner (spec 12.5) are given there only. Draft 4 changes no schema here: its edits are the spec's
3.4 (`Check.UnknownCause`), 2.7 (`Expr.inline_tooLarge`), 3.1 (linearity needs no value) and 13.6 (R-10). Names
follow `main`'s conventions; `Rat` is core's (via `import Std`).

### 3.1 ME-1: values, rounding, claims, verdicts

The exact-number pieces are in the shared `VE.Numbers` (`lean/VE/Numbers/Decimal.lean` and
`lean/VE/Numbers/Round.lean`), with unchanged statements; `VE.Calc` imports it.

```lean
import Std
import VE.Time.Decimal

namespace VE.Numbers

/-- The exact value of a written decimal: its significand over ten to its number of places. -/
def decValue (d : VE.Time.Dec) : Rat := (d.significand : Rat) / ((10 : Rat) ^ d.places)

/-- One meaning for decimals: where W6 lowers a literal onto the grid of scale `10^k`, the coordinate over `10^k` is
the literal's exact value. -/
theorem decValue_lower (d : VE.Time.Dec) (k : Nat) (q : Int) (h : VE.Time.lower d k = some q) :
    decValue d = (q : Rat) / ((10 : Rat) ^ k)

/-- Ten to an integer power, exactly. -/
def tenPow : Int → Rat
  | .ofNat n => (10 : Rat) ^ n
  | .negSucc n => 1 / (10 : Rat) ^ (n + 1)

/-- A printed number `D / 10^k`, with the places `k` read from its spelling ("0.30" is (30, 2); "2 times ten to the
power 7" is (2, -7)). -/
structure Printed where
  digits : Int
  places : Int
  deriving Repr, DecidableEq

def Printed.value (p : Printed) : Rat := (p.digits : Rat) / tenPow p.places

/-- Ties upward (the default), half to even on the exact value, rounded down, rounded up. -/
inductive Rounding where
  | tiesUp | halfEven | down | up
  deriving Repr, DecidableEq

/-- `x` rounds to `p` under rule `r`. Ties upward is the default; quantities' QT-A2 proves its integer-ratio
rounding agrees (`roundsTo_ratio_agree`). -/
def RoundsTo (r : Rounding) (p : Printed) (x : Rat) : Prop :=
  let y := x * tenPow p.places
  let D : Rat := p.digits
  match r with
  | .tiesUp => 2 * D - 1 ≤ 2 * y ∧ 2 * y < 2 * D + 1
  | .halfEven => (2 * D - 1 < 2 * y ∧ 2 * y < 2 * D + 1) ∨
      ((2 * y = 2 * D - 1 ∨ 2 * y = 2 * D + 1) ∧ p.digits % 2 = 0)
  | .down => D ≤ y ∧ y < D + 1
  | .up => D - 1 < y ∧ y ≤ D

instance (r : Rounding) (p : Printed) (x : Rat) : Decidable (RoundsTo r p x)

/-- Rounding to `k` places moves a value by at most half a unit of the last place. -/
theorem roundsTo_close (p : Printed) (x : Rat) (h : RoundsTo .tiesUp p x) :
    -(1 / 2) ≤ x * tenPow p.places - p.digits ∧ x * tenPow p.places - p.digits < 1 / 2

/-- One printed number per value and rule: two different printed numbers with the same places cannot both be the
nearest rounding of one value (ties upward). -/
theorem roundsTo_unique (x : Rat) (p q : Printed) (hk : p.places = q.places)
    (hp : RoundsTo .tiesUp p x) (hq : RoundsTo .tiesUp q x) : p = q

end VE.Numbers

namespace VE.Calc
open VE.Numbers

inductive Expr where
  | lit (q : Rat)
  | val (name : String)
  | add (a b : Expr)
  | sub (a b : Expr)
  | mul (a b : Expr)
  | div (a b : Expr)
  | pow (a : Expr) (k : Nat)
  deriving Repr, DecidableEq

abbrev Values := String → Option Rat

/-- The independent meaning of an expression: the value it denotes, when every name has a value and no divisor is 0. -/
inductive Denotes (σ : Values) : Expr → Rat → Prop
  | lit {q} : Denotes σ (.lit q) q
  | val {n q} : σ n = some q → Denotes σ (.val n) q
  | add {a b x y} : Denotes σ a x → Denotes σ b y → Denotes σ (.add a b) (x + y)
  | sub {a b x y} : Denotes σ a x → Denotes σ b y → Denotes σ (.sub a b) (x - y)
  | mul {a b x y} : Denotes σ a x → Denotes σ b y → Denotes σ (.mul a b) (x * y)
  | div {a b x y} : Denotes σ a x → Denotes σ b y → y ≠ 0 → Denotes σ (.div a b) (x / y)
  | pow {a x k} : Denotes σ a x → Denotes σ (.pow a k) (x ^ k)

def Expr.eval (σ : Values) : Expr → Option Rat

theorem Expr.eval_iff (σ : Values) (e : Expr) (q : Rat) : e.eval σ = some q ↔ Denotes σ e q
theorem Denotes.unique {σ : Values} {e : Expr} {x y : Rat} (hx : Denotes σ e x) (hy : Denotes σ e y) : x = y

inductive Rel where
  | eq | lt | le
  deriving Repr, DecidableEq

def Rel.Holds : Rel → Rat → Rat → Prop
  | .eq, x, y => x = y
  | .lt, x, y => x < y
  | .le, x, y => x ≤ y

inductive Claim where
  | compare (r : Rel) (a b : Expr)
  | within (e lo hi : Expr)
  | rounds (r : Rounding) (e : Expr) (p : Printed)
  deriving Repr, DecidableEq

def Claim.Holds (σ : Values) : Claim → Prop
  | .compare r a b => ∃ x y, Denotes σ a x ∧ Denotes σ b y ∧ r.Holds x y
  | .within e lo hi => ∃ x l h, Denotes σ e x ∧ Denotes σ lo l ∧ Denotes σ hi h ∧ l ≤ x ∧ x ≤ h
  | .rounds r e p => ∃ x, Denotes σ e x ∧ RoundsTo r p x

/-- Every expression of the claim denotes. -/
def Claim.Defined (σ : Values) : Claim → Prop

inductive Verdict where
  | holds | fails | undefined
  deriving Repr, DecidableEq

def Claim.decide (σ : Values) (c : Claim) : Verdict

theorem Claim.decide_holds (σ : Values) (c : Claim) : c.decide σ = .holds ↔ c.Holds σ
theorem Claim.decide_fails (σ : Values) (c : Claim) : c.decide σ = .fails ↔ c.Defined σ ∧ ¬ c.Holds σ
theorem Claim.decide_undefined (σ : Values) (c : Claim) : c.decide σ = .undefined ↔ ¬ c.Defined σ

/-- The operational outcome (debate A1): the mathematical verdict, or unknown with a named reason. -/
inductive UnknownReason where
  | limit (l : Limit)
  | floatingPointNotModelled
  | derivationInconclusive | consistencyInconclusive | identityNotShown
  | unboundedStatement

inductive Outcome where
  | decided (v : Verdict)
  | unknown (r : UnknownReason)

/-- Where a named value comes from (counted values arrive in ME-4). -/
inductive Source where
  | stated (q : Rat)
  | defined (e : Expr)
  | free

structure Decl where
  name : String
  source : Source

/-- Unique names; each defined value mentions only earlier names. -/
def WellFormed (ds : List Decl) : Prop

/-- The values the declarations give, in order: stated values as written, defined values by evaluation, free values
none. -/
def values (ds : List Decl) : Values

theorem values_stated (ds : List Decl) (h : WellFormed ds) (d : Decl) (hd : d ∈ ds) (q : Rat)
    (hs : d.source = .stated q) : values ds d.name = some q
theorem values_defined (ds : List Decl) (h : WellFormed ds) (d : Decl) (hd : d ∈ ds) (e : Expr)
    (hs : d.source = .defined e) (q : Rat) : values ds d.name = some q ↔ Denotes (values ds) e q
theorem values_free (ds : List Decl) (h : WellFormed ds) (d : Decl) (hd : d ∈ ds)
    (hs : d.source = .free) : values ds d.name = none

/-- The claim's outcome within the limits of 2.1; `Overflows` says a value on the way exceeds 4,096 digits. -/
def Claim.run (ds : List Decl) (c : Claim) : Outcome

/-- A decided outcome is the mathematical verdict; unknown arises only when a named limit is met: the digit limit,
or (from ME-4) a counted value, read directly or through definitions, whose budget ran out (statement review J2). -/
theorem Claim.run_decided (ds : List Decl) (h : WellFormed ds) (c : Claim) (v : Verdict)
    (hr : c.run ds = .decided v) : v = c.decide (values ds)
theorem Claim.run_unknown (ds : List Decl) (h : WellFormed ds) (c : Claim) (u : UnknownReason)
    (hr : c.run ds = .unknown u) :
    (u = .limit .digits ∧ c.Overflows ds) ∨ (u = .limit .evaluations ∧ c.ReadsExhausted ds)

end VE.Calc
```

### 3.2 ME-2: wire, runner, shapes

```lean
namespace VE.Calc

/-- A decoded case: declarations, claims (each `rounds` claim carries its tie rule), and the declared software
convention, if any. -/
structure Case where
  decls : List Decl
  claims : List (String × Claim)
  software : Option String

/-- Decodes `ve-calc@0`: limits first (2.1), then fields, names, order of definitions, literals by
`VE.Time.parseDecimal`. -/
def Wire.decodeCase : Lean.Json → Except String Case

theorem Wire.decodeCase_wellFormed (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) : WellFormed c.decls

/-- The runner's row for claim `i` reports `Claim.run`; agreement with `Claim.decide` is conditional on completion. -/
theorem Run.verdict_sound (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) (i : Nat)
    (hi : i < c.claims.length) (v : Verdict) (hv : Run.outcomeAt (Run.runCaseReported j) i = some (.decided v)) :
    v = (c.claims[i]'hi).2.decide (values c.decls)

end VE.Calc

namespace VE.Service
theorem runMode_calc (j : Lean.Json) : runMode .calc j = VE.Calc.Run.runCaseReported j := rfl
end VE.Service

namespace ResponseShape.Encoders.Calc
theorem runCaseReported_fits (j : Lean.Json) :
    ResponseShape.Fits j ResponseShape.Skeletons.calc (VE.Calc.Run.runCaseReported j)
end ResponseShape.Encoders.Calc
```

(`Run.outcomeAt` reads the outcome of row `i`; `ResponseShape.Fits` is the predicate the existing encoder theorems
use, as in `ResponseShape.Encoders.Discourse.runCaseReported_fits`. The spec gives the elaborated forms: from draft 3
`Case.claims` holds checks, `Run.verdict_sound` is stated for claim rows, and `Run.row_sound` and `Run.unknown_named`
cover every kind (spec 3.4). From draft 4 `Run.unknown_named` concludes `Check.UnknownCause`: for a claim row,
`run_unknown`'s disjunction above; for the other kinds, a cause at the digit limit and at the budget.)

### 3.3 ME-4: tables and data

```lean
namespace VE.Calc

inductive Cell where
  | num (q : Rat) | text (s : String) | bool (b : Bool) | absent
  deriving Repr, DecidableEq

structure Table where
  columns : List String
  rows : List (List Cell)

/-- No general negation (statement review J9): each negated atom needs a cell of its type. -/
inductive Filter where
  | all | isText (col v : String) | isNotText (col v : String) | equals (col : String) (q : Rat)
  | notEquals (col : String) (q : Rat) | isTrue (col : String) | isFalse (col : String)
  | and (f g : Filter) | or (f g : Filter)

inductive Agg where
  | count | sum (col : String) | mean (col : String) | min (col : String) | max (col : String)

def Filter.Selects (T : Table) : Filter → List Cell → Prop
def Table.select (T : Table) (f : Filter) : List (List Cell)

theorem Table.select_iff (T : Table) (f : Filter) (row : List Cell) :
    row ∈ T.select f ↔ row ∈ T.rows ∧ f.Selects T row

/-- The numbers in a column of the selected rows, or none if a selected cell there is not a number. -/
def Table.numbers (T : Table) (f : Filter) (col : String) : Option (List Rat)

def Agg.run (T : Table) (f : Filter) : Agg → Option Rat

theorem Agg.run_count (T : Table) (f : Filter) : Agg.run T f .count = some ((T.select f).length : Rat)
theorem Agg.run_sum (T : Table) (f : Filter) (col : String) (q : Rat) :
    Agg.run T f (.sum col) = some q ↔ ∃ xs, T.numbers f col = some xs ∧ q = xs.sum
theorem Agg.run_mean (T : Table) (f : Filter) (col : String) (q : Rat) :
    Agg.run T f (.mean col) = some q ↔ ∃ xs, T.numbers f col = some xs ∧ xs ≠ [] ∧ q = xs.sum / xs.length

/-- Debate A4: over an empty selection, count and sum are 0; mean, minimum and maximum are undefined. -/
theorem Agg.run_empty (T : Table) (f : Filter) (h : T.select f = []) (col : String) :
    Agg.run T f .count = some 0 ∧ Agg.run T f (.sum col) = some 0 ∧ Agg.run T f (.mean col) = none ∧
      Agg.run T f (.min col) = none ∧ Agg.run T f (.max col) = none

/-- Decoders: the CSV and JSON-lines subsets of 2.5. -/
def decodeTable (format : String) (columns : List (String × String)) (bytes : ByteArray) : Except String Table

/-- A counted value is computed only from bytes whose SHA-256 is the declared handle, within the budget `limit`; its
result is the aggregate's value or exhausted (statement review J2). -/
theorem counted_bound (limit : Nat) (handles : List (String × ByteArray)) (d : String) (f : Filter) (a : Agg)
    (v : Option Rat) (h : runCounted limit handles d f a = .ok (.ok v)) :
    ∃ bytes T, handles.lookup d = some bytes ∧ VE.CertificateWire.sha256 bytes = d ∧
      decodeTable (formatOf d) (columnsOf d) bytes = .ok T ∧ Agg.run T f a = v

/-- Debate F1: a span is checked against the pinned source's bytes; the text must read as the printed number. -/
theorem spanMatches_iff (src : ByteArray) (s : Span) (p : Printed) :
    spanMatches src s p = true ↔ ∃ t, spanText src s = some t ∧ readSourceNumber t = some p

end VE.Calc
```

(`runCounted`, `formatOf` and `columnsOf` are ME-4's; SHA-256 is trusted code without a refinement theorem, as for
the risk log, and the plan does not claim more. The spec adds `counted_exhausted`, `Filter.bool_atoms` and
`Filter.negated_typed`, and fixture T-3 for an exhausted count read through a definition beside an empty mean.)

### 3.4 ME-5: derivations over rational unknowns

```lean
namespace VE.Calc

/-- A linear form over unknowns with rational coefficients. A separate module from the frozen integer `VE.Order.Lin`:
its unknowns range over ℚ and it has no cuts. -/
structure QLin where
  const : Rat
  coeffs : List (String × Rat)

def QLin.eval (κ : String → Rat) (L : QLin) : Rat

/-- A fact `0 ≤ L`, or `0 < L` when strict. -/
structure QFact where
  form : QLin
  strict : Bool

def QFact.Holds (κ : String → Rat) (f : QFact) : Prop :=
  if f.strict then 0 < f.form.eval κ else 0 ≤ f.form.eval κ

/-- Nonnegative weights whose combination cancels every unknown and leaves a negative constant (or zero, with a
positive weight on a strict fact). -/
structure Farkas where
  weights : List Rat

def Farkas.check (fs : List QFact) (c : Farkas) : Bool

theorem Farkas.check_sound (fs : List QFact) (c : Farkas) (h : c.check fs = true) :
    ∀ κ : String → Rat, ¬ ∀ f ∈ fs, f.Holds κ

/-- The proved square rule. -/
theorem lt_of_sq_lt (x a b : Rat) (hx : 0 ≤ x) (hb : 0 < b) (h : x * x < a) (hab : a ≤ b * b) : x < b

/-- A derivation step list is accepted only if each step is a checked Farkas refutation of (premises and the negated
step) or one square-rule step; then the conclusion holds wherever the premises and square links hold. -/
theorem Derivation.check_sound (P : List QFact) (links : List (String × String)) (C : QFact) (d : Derivation)
    (h : d.check P links C = true) :
    ∀ κ : String → Rat, (∀ f ∈ P, f.Holds κ) →
      (∀ l ∈ links, κ l.1 = κ l.2 * κ l.2 ∧ 0 ≤ κ l.2) → C.Holds κ

/-- A reported counterexample is checked by evaluation, square links and their nonnegativity included (debate A2:
without them, s = 0, r = 1 would refute "r < 1/4" from "s < 1/20" although s = r² fails). -/
theorem Counterexample.check_sound (P : List QFact) (links : List (String × String)) (C : QFact)
    (κ : String → Rat) (h : counterexampleCheck P links C κ = true) :
    (∀ f ∈ P, f.Holds κ) ∧ (∀ l ∈ links, κ l.1 = κ l.2 * κ l.2 ∧ 0 ≤ κ l.2) ∧ ¬ C.Holds κ

end VE.Calc
```

### 3.5 ME-6: physical dimensions

```lean
namespace VE.Calc

/-- A physical dimension: an exponent per base dimension; normal form sorted by name, no zero exponent. -/
structure PhysDim where
  exps : List (String × Int)
  deriving Repr, DecidableEq

def PhysDim.Normal (d : PhysDim) : Prop
def PhysDim.one : PhysDim := ⟨[]⟩
def PhysDim.mul (a b : PhysDim) : PhysDim
def PhysDim.inv (a : PhysDim) : PhysDim
def PhysDim.npow (a : PhysDim) (k : Nat) : PhysDim

/-- The physical dimension of an expression, given each name's; literals are dimensionless; sums need equal ones. -/
def Expr.dimOf (Γ : String → Option PhysDim) : Expr → Option PhysDim

/-- A change of base units: a positive factor per base dimension. -/
structure Rescale where
  factor : String → Rat
  pos : ∀ b, 0 < factor b

def zpowR (q : Rat) : Int → Rat
  | .ofNat n => q ^ n
  | .negSucc n => 1 / q ^ (n + 1)

def Rescale.of (ρ : Rescale) (d : PhysDim) : Rat := (d.exps.map fun e => zpowR (ρ.factor e.1) e.2).foldl (· * ·) 1

theorem Rescale.of_pos (ρ : Rescale) (d : PhysDim) : 0 < ρ.of d
theorem Rescale.of_mul (ρ : Rescale) (a b : PhysDim) (ha : a.Normal) (hb : b.Normal) :
    ρ.of (a.mul b) = ρ.of a * ρ.of b

/-- Every named value rescaled by its own physical dimension's factor. -/
def Rescale.apply (ρ : Rescale) (Γ : String → Option PhysDim) (σ : Values) : Values :=
  fun n => match σ n, Γ n with
    | some q, some d => some (q * ρ.of d)
    | v, _ => v

theorem denotes_rescale (Γ : String → Option PhysDim) (ρ : Rescale) (σ : Values) (e : Expr) (d : PhysDim) (x : Rat)
    (hΓ : ∀ n, (Γ n).isSome → (Γ n).get!.Normal) (hd : e.dimOf Γ = some d) (hx : Denotes σ e x) :
    Denotes (ρ.apply Γ σ) e (x * ρ.of d)

/-- **Unit-change invariance**: a comparison between two expressions of one physical dimension has the same truth in
every system of base units. -/
theorem compare_invariant (Γ : String → Option PhysDim) (ρ : Rescale) (σ : Values) (r : Rel) (a b : Expr)
    (d : PhysDim) (hΓ : ∀ n, (Γ n).isSome → (Γ n).get!.Normal)
    (ha : a.dimOf Γ = some d) (hb : b.dimOf Γ = some d) :
    (Claim.compare r a b).Holds σ ↔ (Claim.compare r a b).Holds (ρ.apply Γ σ)

/-- Units are values (their factor in the coherent unit): an amount `q` in unit `u` is the amount `q · fu / fv` in unit
`v` of the same physical dimension. Quantities' QT-A7 uses this theorem. -/
theorem convert_by_factors (σ : Values) (u v : String) (fu fv q x : Rat) (hu : σ u = some fu) (hv : σ v = some fv)
    (hfv : fv ≠ 0) :
    Denotes σ (.mul (.lit q) (.val u)) x ↔ Denotes σ (.mul (.lit (q * fu / fv)) (.val v)) x

end VE.Calc
```

(ME-6 is the only decoder of `ve-units@2`'s unit record; quantities' QT-A7 consumes it. `ve-units@1` tags stay
nominal: each is read as its own base dimension, so identically declared tags remain incompatible.)

### 3.6 ME-7: statistics

```lean
namespace VE.Calc

def mean? (xs : List Rat) : Option Rat := if xs = [] then none else some (xs.sum / xs.length)

/-- Sample variance (divisor n − 1); none below two values. -/
def sampleVariance? (xs : List Rat) : Option Rat

/-- Population variance (divisor n). -/
def populationVariance? (xs : List Rat) : Option Rat

/-- "The square root of v, rounded, is p" for 0 ≤ v, by squared bounds; this is the definition. -/
def SqrtRoundsTo (r : Rounding) (p : Printed) (v : Rat) : Prop

/-- Agreement with rounding the root whenever the root is rational. -/
theorem sqrtRoundsTo_of_square (r : Rounding) (p : Printed) (s v : Rat) (hs : 0 ≤ s) (hv : s * s = v)
    (hp : 0 ≤ p.digits) : SqrtRoundsTo r p v ↔ RoundsTo r p s

/-- All sign vectors of length n. -/
def signs : Nat → List (List Int)
  | 0 => [[]]
  | n + 1 => (signs n).flatMap fun s => [1 :: s, -1 :: s]

theorem signs_length (n : Nat) : (signs n).length = 2 ^ n
theorem mem_signs (n : Nat) (s : List Int) : s ∈ signs n ↔ s.length = n ∧ ∀ k ∈ s, k = 1 ∨ k = -1

def absR (x : Rat) : Rat := if x < 0 then -x else x

/-- The exact two-sided sign-flip p value: the share of sign vectors whose signed mean is at least the observed mean
in absolute value (the observed vector counted), as `paper/analysis/README.md` defines it. -/
def signFlipP (d : List Rat) : Rat :=
  let obs := absR (d.sum / d.length)
  let hits := (signs d.length).filter fun s =>
    decide (obs ≤ absR ((List.zipWith (fun k x => (k : Rat) * x) s d).sum / d.length))
  (hits.length : Rat) / (2 ^ d.length : Nat)

/-- An enumeration p value is a multiple of 1/2^n. -/
theorem signFlipP_grain (d : List Rat) : ∃ m : Nat, signFlipP d = (m : Rat) / (2 ^ d.length : Nat)

def binomialTail (n k : Nat) (p : Rat) : Rat :=
  ((List.range (n + 1)).filter (k ≤ ·)).foldl (fun acc i => acc + (Nat.choose n i : Rat) * p ^ i * (1 - p) ^ (n - i)) 0

/-- Cohen's kappa of a square agreement table; none when chance agreement is 1. -/
def kappa? (t : List (List Nat)) : Option Rat

end VE.Calc
```

(`Nat.choose` is core's if present in the pinned toolchain; otherwise ME-7 defines it with `choose_succ_succ`; ME-S
found it absent. Draft 3: the domains are in the meaning, not in these functions, which are total: a binomial tail
denotes only for 0 ≤ p ≤ 1, and a statistic over too few values is undefined (`Stat.run`, `Stat.run_isSome`,
`binomialTail_unit`; statement review J5, spec 7, fixture S-5).)

### 3.7 ME-8: consistency of printed numbers

```lean
namespace VE.Calc

/-- A printed input stands for every value in its rounding interval. -/
def InBox (r : Rounding) (inputs : List (String × Printed)) (κ : String → Rat) : Prop :=
  ∀ i ∈ inputs, RoundsTo r i.2 (κ i.1)

/-- One proposition (statement review J4): exact inputs inside their intervals make every output hold, every other
declaration keeping its meaning. -/
def Consistent (ds : List Decl) (r : Rounding) (inputs : List (String × Printed)) (outs : List Claim) : Prop :=
  ∃ κ : String → Rat, InBox r inputs κ ∧ ∀ c ∈ outs, c.Holds (values (assign ds (inputs.map Prod.fst) κ))

/-- Witness: over the outputs inlined with the inputs kept, a checked witness proves `Consistent`. -/
theorem consistent_of_witness (ds : List Decl) (h : WellFormed ds) (r : Rounding)
    (inputs : List (String × Printed)) (hk : ∀ i ∈ inputs, i.1 ∈ ds.map Decl.name) (outs outs' : List Claim)
    (hl : outs.mapM (Claim.inline ds (inputs.map Prod.fst)) = .ok outs') (w : List (String × Rat))
    (hw : witnessCheck r inputs outs' w = true) : Consistent ds r inputs outs

/-- An enclosure that misses an inlined output, or a sign-flip granularity refutation, refutes the same proposition. -/
theorem inconsistent_of_refutation (ds : List Decl) (h : WellFormed ds) (r : Rounding)
    (inputs : List (String × Printed)) (hk : ∀ i ∈ inputs, i.1 ∈ ds.map Decl.name) (outs outs' : List Claim)
    (hl : outs.mapM (Claim.inline ds (inputs.map Prod.fst)) = .ok outs') (c : Claim) (hc : c ∈ outs')
    (hr : refuteByEnclosure r inputs c = true ∨ refuteByGrain c = true) : ¬ Consistent ds r inputs outs

end VE.Calc
```

### 3.8 ME-9: algebraic identities

```lean
namespace VE.Calc

/-- A monomial: a coefficient and variables with positive exponents, sorted by name. -/
structure Mono where
  coeff : Rat
  vars : List (String × Nat)

/-- A normal polynomial: monomials sorted by their variable lists, no repeated list, no zero coefficient. -/
abbrev Poly := List Mono

def Poly.eval (κ : String → Rat) (p : Poly) : Rat
def Poly.ofExpr? : Expr → Option Poly   -- division-free expressions only

theorem Poly.ofExpr_sound (κ : String → Rat) (e : Expr) (p : Poly) (h : Poly.ofExpr? e = some p) :
    Denotes (fun n => some (κ n)) e (p.eval κ)

/-- Numerator and denominator of an expression with division. -/
def Frac.ofExpr? : Expr → Option (Poly × Poly)

theorem Frac.ofExpr_sound (κ : String → Rat) (e : Expr) (n d : Poly) (x : Rat)
    (h : Frac.ofExpr? e = some (n, d)) (hx : Denotes (fun v => some (κ v)) e x) :
    d.eval κ ≠ 0 ∧ x = n.eval κ / d.eval κ

/-- **Identity**: equal cross-multiplied normal forms mean equal values wherever both sides denote. -/
theorem identity_sound (a b : Expr) (h : identityCheck a b = true) (κ : String → Rat) (x y : Rat)
    (hx : Denotes (fun v => some (κ v)) a x) (hy : Denotes (fun v => some (κ v)) b y) : x = y

end VE.Calc
```

### 3.9 ME-12 and ME-13: `arith@0` and imports

```lean
namespace VE.Arith

mutual
/-- Terms: numerals, variables (de Bruijn), sum, difference, product, calls of defined functions, and bounded counts
("the number of whole numbers p from lo through hi such that φ"). -/
inductive Term where
  | var (i : Nat) | num (n : Int) | add (a b : Term) | sub (a b : Term) | mul (a b : Term)
  | call (f : String) (args : List Term)
  | countFromTo (lo hi : Term) (φ : Formula)

inductive Formula where
  | eq (a b : Term) | lt (a b : Term) | le (a b : Term) | dvd (a b : Term)
  | call (p : String) (args : List Term)
  | not (φ : Formula) | and (φ ψ : Formula) | or (φ ψ : Formula) | imp (φ ψ : Formula)
  | allNat (φ : Formula) | exNat (φ : Formula) | allInt (φ : Formula) | exInt (φ : Formula)
  | allFromTo (lo hi : Term) (φ : Formula) | exFromTo (lo hi : Term) (φ : Formula)
end

/-- Non-recursive definitions, each over earlier names only. -/
structure Defs where
  funs : List (String × Nat × Term)
  preds : List (String × Nat × Formula)

/-- Inline every call (definitions are acyclic, so this terminates); none on an unknown name or a wrong arity. -/
def Defs.expand (D : Defs) : Formula → Option Formula

/-- Every quantifier of the formula is bounded (checked at admission for every count's condition). -/
def Formula.Bounded : Formula → Prop

/-- The meaning, over call-free terms and formulas: `Term.value` and `Holds` are defined together, and neither
refers to an evaluator (debate F4). Whole-number binders range over 0, 1, 2, …; `allFromTo lo hi` over the integers
from lo through hi; `countFromTo lo hi φ` is the number of integers i from lo through hi for which `Holds (i :: ρ) φ`
is decided true by classical decision (0 when hi < lo). -/
noncomputable def Term.value (ρ : List Int) : Term → Option Int
def Holds (ρ : List Int) : Formula → Prop

def Defs.Means (D : Defs) (φ : Formula) : Prop := ∃ ψ, D.expand φ = some ψ ∧ Holds [] ψ

/-- The budgeted Boolean evaluator: one unit per formula-node visit, as W6's `VE.Time.evalB`; connectives
short-circuit left to right and a bounded quantifier stops at the first decisive value; none on an unbounded binder
or an exhausted budget. -/
def Formula.evalB (budget : Nat) (ρ : List Int) : Formula → Nat → Option (Bool × Nat)
def decideBounded (budget : Nat) (ρ : List Int) (φ : Formula) : Option (Bool × Nat) := φ.evalB budget ρ 0

/-- The evaluator agrees with the meaning whenever it completes; the budget only turns an answer into unknown. -/
theorem decideBounded_sound (budget : Nat) (ρ : List Int) (φ : Formula) (v : Bool) (w : Nat)
    (h : decideBounded budget ρ φ = some (v, w)) : Holds ρ φ ↔ v = true

/-- `arith`'s budget: default and maximum 1,000,000 visits (`VE.Time.maxEvaluations`); a case may set less. -/
def maxSteps : Nat := VE.Time.maxEvaluations

/-- An import record, admitted by identity, axioms and names; its truth rests on the external build. -/
structure Import where
  statementId : String
  meansDigest : String     -- digest of VE's meaning sources (the VE `lean/` revision the project built against)
  project : String
  projectRev : String
  toolchain : String
  mathlibRev : String
  declaration : String
  checkDigest : String     -- digest of the generated `theorem check : Defs.Means ⟨D⟩ ⟨φ⟩ := <declaration>`
  axioms : List String

def allowedAxioms : List String := ["propext", "Classical.choice", "Quot.sound"]

def Import.admit (D : Defs) (φ : Formula) (i : Import) : Except String Unit

/-- Debate A3: admission binds the statement, the meaning sources and the generated check file, not axioms alone. -/
theorem Import.admit_sound (D : Defs) (φ : Formula) (i : Import) (h : i.admit D φ = .ok ()) :
    i.statementId = statementIdOf D φ ∧ i.meansDigest = currentMeansDigest ∧
      i.checkDigest = VE.CertificateWire.sha256 (checkSource D φ i.declaration).toUTF8 ∧
      ∀ a ∈ i.axioms, a ∈ allowedAxioms

/-- A holds row on an unbounded statement rests on an import admitted for that statement's own id, whose leaf
`import:<project>@<rev>/<declaration>` is the row's residual line (spec 12.5's `Run.import_sound`). Draft 3: the
rows hold, fail or are unknown; draft 2's `Report.Accepted` described only rows that hold (statement review J3). -/
theorem Case.import_row (c : Case) (s : String × Formula) (hb : s.2.Bounded c.defs = false)
    (h : c.outcome s = .decided .holds) :
    ∃ i, c.imports.lookup s.1 = some i ∧ i.statementId = statementIdOf c.defs s.2 ∧
      i.meansDigest = currentMeansDigest ∧ (∀ a ∈ i.axioms, a ∈ allowedAxioms)

end VE.Arith
```

The import project's proof for EX-1 has this shape (Mathlib side; `Nat.bertrand` is from memory: no Mathlib was
available to ME-S, so EX-1 checks the name), and the project also compiles the generated `check` theorem that applies
the declaration at exactly the type `Defs.Means D φ`:

```lean
import Mathlib.NumberTheory.Bertrand
import VE.Arith.Examples

/-- The one bridge lemma for this vocabulary, declared before its use (statement review J11): VE's definition of
prime is Mathlib's. -/
theorem VEImports.isPrime_iff_nat_prime (p : Nat) :
    VE.Arith.Examples.IsPrime p ↔ Nat.Prime p

theorem VEImports.bertrand_holds : VE.Arith.Examples.primeDefs.Means VE.Arith.Examples.bertrand := by
  rw [VE.Arith.Examples.bertrand_means_iff]          -- core-Lean unfolding lemma, proved in VE
  intro n hn
  obtain ⟨p, hp, h1, h2⟩ := Nat.bertrand n (by omega)
  exact ⟨p, (VEImports.isPrime_iff_nat_prime p).mpr hp, h1, h2⟩
```

## 4. Fixtures

Expected results were computed by hand in exact arithmetic for this plan; ME-S recomputes every one with `#eval` in the
stub and the batches pin them as `#guard`s and route cases. Target sentences marked *paraphrase* were from memory;
ME-0 re-anchored each to the pinned text's byte spans (P4, `docs/research/evidence/math-evidence/fixture-anchors.json`,
which holds every span and the source's SHA-256). Each row below names its outcome: ANCHORED (the source's words and
numbers), RE-WORDED (the source's numbers, other words), NOT A QUOTE (constructed), or, in draft 4, CHANGED, which
draft 5 rewrites to the source. Draft 5's new fixtures' numbers were computed with exact fractions in phase 1's
scripts and by hand; they are not VE verdicts, and ME-S recomputes them in the stub.

### 4.1 VE's own paper and documentation (in the repository; exact quotes)

ME-0 found V-1 to V-8 and D-1 to D-3 ANCHORED in these words, except the constructed V-1n and V-6r (NOT A QUOTE).
V-9 to V-11 are constructed; V-12 is constructed over V-1's real span ".296".

| Id | Source | Case | Expected |
|---|---|---|---|
| V-1 | `paper/sections/04-e1.md`: "Its scored baseline, 176/594 = .296, is outside the gate band" (the band is 30-60%) | 176/594 = 8/27; rounds to 0.296 (ties up: 591 ≤ 2,000 × 8/27 = 592.59 < 593); and 8/27 < 0.30 (80 < 81) | holds, holds |
| V-1n | the same with "0.297" | 593 ≤ 592.59 is false | **fails** (seeded-bug target) |
| V-2 | `04-e1.md`: "false approval is 52/243 (.214) versus 31/243 (.128), an 8.6-point pooled increase" | 52/243 → 0.214 (427 ≤ 427.98 < 429); 31/243 → 0.128 (255 ≤ 255.14 < 257); 100 × 21/243 = 8.642 → 8.6 (171 ≤ 172.84 < 173) | holds ×3 |
| V-3 | `05-e4.md`: "For 7B, prose rejects 56/60 valid inferences; checked feedback increases HA from 4/60 to 52/60" | premise (assumption leaf): every reply is an approval or a rejection; 60 − 56 = 4 | holds, with the leaf in the residual |
| V-4 | `04-e1.md`: "The 32B symbolic/no-explanation baseline was 34/110 false approvals, only one candidate inside the primary 30--60% gate" | 34/110 within [0.30, 0.60] | holds |
| V-5 | `paper/generated/posthoc-weakening-rates.md`, 20 rows "Approved / weakening" against "Pooled FA" | e.g. 151/243 → 0.621, 155/243 → 0.638, 136/243 → 0.560, 90/243 → 0.370, 43/243 → 0.177, 37/243 → 0.152 | all 20 hold (hand-checked) |
| V-6 | `paper/sections/10-appendices.md`, row "14B AWQ, P1 attacker": twelve printed per-template differences, "SD between templates 0.108", "SE with 12 templates 0.031", "97.5% half-width with 12 (t = 2.593) 0.081" | values in thousandths: Σx = −545 (thousandths), Σx² = 152,053 (millionths), n = 12; sample variance v = 1,527,611 / 132,000,000; `sqrt-rounds` v to 0.108 (1,525,425 ≤ 1,527,611 < 1,553,937 in units of 1/132,000,000, the squares of 0.1075 and 0.1085); v/12 to 0.031; 2.593² × v/12 to 0.081 (0.00648430 against the lower bound 0.0805² = 0.00648025) | holds ×3; t = 2.593 is a stated constant with its source |
| V-6r | the same printed SD under the population reading (divisor 12) | 0.127301/12 = 0.010608; its root 0.1030 prints as 0.103 | **fails**: the calculation distinguishes the two readings of "SD" |
| V-7 | `paper/generated/posthoc-weakening-contrasts.md`, column "Two-sided p", 9 templates | granularity: a printed p must be within rounding of a multiple of 1/512 (0.812500 = 416/512, 0.687500 = 352/512, 0.359375 = 184/512, 0.125000 = 64/512, 0.875000 = 448/512; 0.085938 from 44/512 and 0.679688 from 348/512, both exact ties at the lower end of their intervals) | consistent for 7 of 8 under ties upward; the fourth row (0.007812) is V-8 (ME-8) |
| V-8 | the same table, row "14B F − S attacker", printed "0.007812" | 4/512 = 0.0078125 is an exact tie at six places: half to even on the exact value gives 0.007812 (holds), ties up gives 0.007813 (fails) | holds only under "rounded half to even"; in translation without a declared rule, a **reading set** whose distinguishing value is this row |
| V-7b | (draft 5, from ME-0) `paper/sections/04-e1.md`, the six main-text p values of the contrast table (units v060-v065): .460938, .875488, .000977, .001953, .218750, .993164 | granularity over 2¹² sign flips: each printed p is within rounding at six places of k/4096 for k = 1,888, 3,586, 4, 8, 896, 4,068 (1,888/4,096 = 0.4609375 is an exact tie whose upper neighbour 460,938 is even, so both rules print .460938) | consistent for all six under either rule (ME-8) |
| V-9 | software convention: 2.675 printed as 2.67 at two places (Python's `round(2.675, 2)`, which rounds the nearest binary double) | the exact value 107/40 is a tie at two places; both rules give 2.68 | the exact claim **fails**; software reproduction **unknown** ("floating-point computation not modelled"); no source finding |
| V-10 | software convention: 0.1 + 0.2 − 0.3 printed as 0.0000000000000001 at sixteen places (what Python prints; no tie is involved) | the exact value is 0, which rounds to 0 at sixteen places | the exact claim **fails**; software reproduction **unknown**; no source finding |
| V-11 | a limit hit against a zero divisor (debate A1): x = 10³⁹, y = x⁶⁴, z = y × y; claims z < 1 and 1/(x − x) = 1 | z has 4,993 digits, above 4,096; x − x = 0 | **unknown** (limit named) and **undefined**: two distinct outcomes |
| V-12 | a span over a mistyped value (debate F1): the source bytes read ".296", the case states "0.297" with that span | the span reads (296, 3), not (297, 3) | **refused** (`SpanMismatch`) |
| D-1 | ROADMAP: "Math mini paper: **17/19** current verified outcomes (15 tableau certificates plus T9 and T9e by closure induction)" | 15 + 2 = 17 | holds |
| D-2 | UDHR pilot SUMMARY (copied into the test data with its path and digest): "claimed covered bytes 4,792 (43.90%)" of 10,916 | 100 × 4,792/10,916 = 43.899 → 43.90 (8,779 ≤ 8,779.8 < 8,781) | holds |
| D-3 | constitution pilot SUMMARY: "Claimed coverage is unchanged at 2,951 bytes (1.60%)", with `coverage.json` bytes CHECKED 73, LABELLED 349, OPEN 2,529 | 73 + 349 + 2,529 = 2,951; 100 × 2,951/184,893 = 1.596 → 1.60 | holds ×2 |

### 4.2 Physics (Michelson and Morley 1887; anchored by ME-0)

Spans are byte offsets in the pinned `physics-michelson-morley/source.txt` (24,368 B, SHA-256 `7bc59a08…a1946b`),
whose equations are Wikisource's TeX; unit ids (`h049`) are the ME-0 ledger's.

| Id | Sentence (ME-0 outcome) | Case | Expected |
|---|---|---|---|
| H-1 | "T = D/(V − v), T₁ = D/(V + v); the whole time of going and coming is T + T₁ = 2DV/(V² − v²)" (RE-WORDED: the source's TeX, with T-sub-slash for T₁) | `identity` over free D, V, v | identity (ME-9), side conditions V ≠ v, V ≠ −v |
| H-2 | "the distance traveled in this time is 2DV²/(V² − v²) = 2D(1 + v²/V²), neglecting terms of the fourth order" (RE-WORDED) | the exact remainder: 2DV²/(V² − v²) − 2D(1 + v²/V²) = 2Dv⁴/(V²(V² − v²)) | identity (ME-9); "neglecting" becomes the exact remainder, bounded numerically at v²/V² = 10⁻⁸ by ME-1 (EX-2 for the general bound) |
| H-3 | "the difference is therefore Dv²/V²" (RE-WORDED) | 2D(1 + v²/V²) − 2D(1 + v²/(2V²)) = Dv²/V² | identity (ME-9) |
| H-4 | (draft 5; CHANGED in draft 4, which took "v/V = 10⁻⁴ stated", a premise the source never states) "hence the displacement of the interference fringes should be 2D v²/V². Considering only the velocity of the earth in its orbit, this would be 2D × 10⁻⁸." (spans 7,265-7,348 and 7,350-7,443, unit h049; again in h113) | the squared speed ratio `sq` stated as 10⁻⁸ (`["sci", "1", -8]`, `support: testimony`, span in h049), D free: 2D × sq = 2D × 10⁻⁸ | identity in D (ME-9); with D stated (2 × 10⁷), 2D × sq = 0.4 holds (ME-1) |
| H-5 | (draft 5; CHANGED in draft 4, which used H-4's unstated v/V) "The distance D was about eleven meters, or 2×10⁷ wave-lengths of yellow light; hence the displacement to be expected was 0•4 fringe." (span 15,790-15,882, unit h114; the decimal point is a bullet in the source) | D = 2 × 10⁷ (stated, span), sq = 10⁻⁸ (stated, span in h113): 2 × D × sq = 0.4 | holds (ME-1): 2 × (2 × 10⁷) × 10⁻⁸ = 2/5, the source's route |
| H-5b | (draft 5, from ME-0) "If, as was the case in the first experiment, D = 2 × 10⁶ waves of yellow light, the displacement to be expected would be 0.04 of the distance between the interference fringes." (unit h050, ANCHORED) | D = 2 × 10⁶, sq = 10⁻⁸: 2 × D × sq = 0.04 | holds (ME-1): 1/25 |
| H-6 | "The actual displacement was certainly less than the twentieth part of this ... the relative velocity of the earth and the ether is ... certainly less than one-fourth" (ANCHORED, h115-h116) | premises: displacement = 0.4 fringe × r² (assumption: proportional to the square, as the source says), r ≥ 0, displacement < 0.4/20 fringe; claim r < 1/4 | **follows** (ME-5: Farkas gives r² < 1/20; square rule with 1/20 ≤ 1/16) |
| H-6p | "and probably less than the fortieth part" ... "is probably less than one sixth the earth's orbital velocity" (ANCHORED) | r² < 1/40 and 1/40 ≤ 1/36 | follows; the hedge "probably" stays a `hedged` label until a separately reviewed calc–attitudes bridge exists |
| H-6n | negative control: "less than one fifth" from "less than the twentieth part" (NOT A QUOTE) | 1/20 ≤ 1/25 is false | **does not follow**; counterexample r = 1/5 (r² = 1/25 < 1/20; the search tries the claimed bound itself first) |
| H-7 | physical dimensions: "D/(V − v)" is a time; "D/λ" is dimensionless; negative "D + T" (RE-WORDED: D and T are the source's definitions, the expressions the case's) | ME-6 | time; dimensionless; `DimensionMismatch(length, time)` |
| H-8 | "The distance D was about eleven meters, or 2×10⁷ wave-lengths of yellow light" (ANCHORED) | with the external premise "the wavelength of yellow light is 5.89 × 10⁻⁷ meters" (stated, `support: testimony`, cited): 11 m / λ = 1.868 × 10⁷, rounds to 2 × 10⁷ at places −7 (3 ≤ 3.735 < 5) | holds; "about" is a reading set in translation; the wavelength is a residual leaf |
| H-9 | (draft 5; CHANGED in draft 4, which assumed printed readings at 16 azimuths) the two tables, noon and evening (spans 12,968-15,143, units h086-h106): "The following tables give the means of the six readings"; each table has 17 marks (mark 16 at the start and end of a turn), three sessions (noon: July 8, 9, 11; evening: July 8, 9, 12) and the rows Mean, Mean in w. l., a repeated half row (marks 8-16) and Final mean; "one division means 0.02 wave-length" | stated: the 102 session cells and the printed rows; for each mark, Mean = the sum of the three sessions divided by 3, rounded at one place (34 claims); Mean in w. l. = 0.02 × the printed Mean (34 equalities; the factor stated with its span, or ME-6's unit `division` with factor 0.02 wave-length); the half row repeats marks 8-16 (18); Final mean at mark k = the average of Mean in w. l. at k and k + 8 (18). Negative control: noon Mean at mark 1 printed 41.9 instead of 41.6 | all 104 hold (exact fractions in phase 1; no rounding tie can occur, since a sum of tenths divided by 3 is never an odd twentieth: noon mark 16 is 647/15 = 43.13…, printed 43.1; 0.02 × 43.1 = 0.862; (0.862 + 0.706)/2 = 0.784); the control **fails**. ME-1 suffices: the inputs are printed means, not a data file. Today's W6a already certifies the Mean, half-row and Final-mean relations; only Mean in w. l. is beyond it (cross-tag arithmetic) |
| H-10 | the observation dates (July 8, 9, 11 and 12; RE-WORDED: the tables print no year, which comes from the publication line "November 1887") | W6a date literals start at 1970-01-01 (W6 6.1), so these are refused (ME-0 P6: `DateRange(1887-07-08)`, the 1970-01-01 control admitted) | refused; a recorded trigger, ET-T3 in events' plan, to extend W6's `VE.Time.Calendar` below 1970 under W6's own review. Never a second calendar; until then H-10 stays refused (section 10, piece 8). The year enters as a stated premise with its span |

The supplement's trigonometric derivation (units h134-h142, tagged `approximation`) has no batch in this plan; its
bytes are named residual, beyond EX-2's bar.

### 4.3 Mathematics (Ramanujan 1919; anchored by ME-0 in OCR bytes)

The pinned text (`math-ramanujan-bertrand/source.txt`, 2,651 B) is the OCR of the 1927 *Collected Papers*, and both
available scans garble the formulas: 2,114 B (79.7%) is analytic (logarithms, Chebyshev's functions, Stirling), which
no batch states in VE. The numbers the fixtures use are intact. ME-0's outcomes: M-1, M-3, M-3r and M-4 RE-WORDED;
M-2, M-4x and M-5 NOT A QUOTE.

| Id | Sentence or case | Expected |
|---|---|---|
| M-1 | "Thus Bertrand's Postulate is proved for all values of x, not less than 162: and, by actual verification, we find that it is true for smaller values": "for every whole number n from 1 to 161, there is a prime p with n < p and p at most twice n" | bounded evaluation: holds (ME-12) |
| M-2 | the standard check of the small cases (not Ramanujan's wording): the chain 2, 3, 5, 7, 13, 23, 43, 83, 163, each prime and each less than twice the one before | holds (3 < 4, 5 < 6, 7 < 10, 13 < 14, 23 < 26, 43 < 46, 83 < 86, 163 < 166) |
| M-3 | Bertrand's postulate, whole-number reading: "for every whole number n that is at least 1 there is a prime p with n < p and p at most twice n" (the source: "conjectured by Bertrand: namely that there is at least one prime p such that x < p ≤ 2x if x ≥ 1", read from the scan since the OCR garbles the formula, with x real) | unbounded: no bounded decision; proved only by import (EX-1) |
| M-3r | the same with a real x (Ramanujan's x is real: "[x] denotes as usual the greatest integer in x") | a reading set {whole number, real}; `arith@0` has no reals, so the real reading stays residual |
| M-4 | formula (18)'s second pair, "π(x) − π(x/2) ≥ 2 if x ≥ 11", bounded part for whole x from 11 to the measured bound (RE-WORDED: the OCR span 2,575-2,620 reads "> 1, 2, 3, 4,5,..., if * » 2, 11, 17, 29, 41"; the numbers are intact, the words are not) | holds by evaluation (at x = 10 the difference is 1, at x = 11 it is 2); the unbounded remainder is residual or import. ME-S defines the fuel accounting; ME-12 measures M-4 at the candidate bounds 200 and 1,000 and takes the completing bound from that measurement (the spec's reference count: 248 completes within 1,000,000 visits, 249 does not); no runtime estimate is part of the semantics |
| M-4b | (draft 5, from ME-0) formula (18)'s other four pairs: π(x) − π(x/2) ≥ 1, 3, 4, 5 if x ≥ 2, 17, 29, 41 | for each pair, bounded evaluation from its threshold to the bound ME-12 measures: holds; one below each threshold the difference is one less (0 at x = 1, 2 at 16, 3 at 28, 4 at 40), so each threshold is the least whole number that works (exact counts in phase 1, to 1,000) |
| M-4x | exhaustion: M-1 with a deliberately insufficient budget (1,000 visits) | the evaluator stops: **unknown** (limit named), never fails; tested apart from undefined values |
| M-5 | negative control: strict "n < p < 2n" from 1 to 161 | **fails** at n = 1, reported as the row's deciding value (spec 12.5) |

### 4.4 Deep learning (AlphaFold, pinned by ME-0)

Draft 4's DL-1 to DL-5 were shapes for a LoRA-like text. ME-0 pinned AlphaFold instead (D22), whose main text has no
result tables (its results are in five figures and the supplement) and no equations, so DL-1 ("the highest score in
column C"), DL-2 ("on average across the eight tasks") and DL-4 ("a parameter count from a stated formula") have no
span, and "on par" (DL-5) does not occur; all five are dropped ("on par" stays a refused wording in ME-11 with a
constructed fixture). Draft 5's fixtures are AlphaFold's own numbers. Spans are units of the ME-0 ledger
(`dl-alphafold/source.txt`, 66,858 B).

| Id | Source | Case | Expected |
|---|---|---|---|
| DL-1 | d024: "AlphaFold structures had a median backbone accuracy of 0.96 Å r.m.s.d.95 … (95% confidence interval = 0.85–1.16 Å) whereas the next best performing method had a median backbone accuracy of 2.8 Å r.m.s.d.95 (95% confidence interval = 2.7–4.0 Å)"; d027: all-atom 1.5 Å (1.2–1.6 Å) against 3.5 Å (3.1–4.2 Å) | each median within its interval; AlphaFold's median less than the alternative's, for both measures | holds × 6 (ME-1); already CHECKED today with certified order (W6a), so the case is a parity check, not new bytes |
| DL-2 | d239: "4.8 min with 256 residues, 9.2 min with 384 residues and 18 h at 2,500 residues"; d242: "Without ensembling, the network is 8× faster and the representative timings for a single model are 0.6 min …, 1.1 min … and 2.1 h …" | for each length, the timing with ensembling divided by the timing without, against "8×": 4.8/0.6 = 8, 9.2/1.1 = 92/11 = 8.36…, 18/2.1 = 60/7 = 8.57… | "8×" is a **reading set** in translation {rounded to the written digit, an open tolerance}: under the rounded reading the first two hold and the third **fails** (60/7 rounds to 9), a finding ("transcription unchecked" until ME-4 checks spans); the tolerance reading needs its decider |
| DL-3 | d119: "we use a trained network to predict the structure of around 350,000 diverse sequences"; d231: "a Uniclust dataset of 355,993 sequences" (that the two name one set is a translation premise, `support: assumption`) | "around 350,000" against 355,993 | a **reading set** {rounded to the written digits, an open tolerance}: 355,993 rounds to neither 350,000 at its last written digit nor at its last nonzero digit (360,000 at ten thousands), so the rounded reading fails and only the tolerance holds. "Around" is not in the shared approximation row as section 10 piece 6 lists it; where it belongs is a question for the DRI ("Cross-plan issues for the DRI", item 3), and until then it is treated as that row's words are |
| DL-4 | d214: "Removing BFD reduced the mean accuracy by 0.4 GDT, removing Mgnify reduced the mean accuracy by 0.7 GDT, and removing both reduced the mean accuracy by 6.1 GDT." | stated drops; constructed claim (NOT A QUOTE) "the drop from removing both is more than the sum of the two single drops": 0.4 + 0.7 < 6.1 | holds (ME-1); the stated values are CHECKED today |

### 4.4a Fixtures added by the statement review

The spec (13.2, 13.3, 13.6) defines them; their numbers were computed by hand and are recomputed in the stub at the
bounded re-check. I-1 and I-2: identities with a negative printed place (H-8) and a negative unit exponent (a
velocity), against the frozen encoder (J1). T-3: an exhausted count read directly and through a definition, beside an
empty mean, in both orders (J2). T-1 gains a row whose `approved` cell is absent and one whose cell is the text "yes"
(J9). S-5: binomial tails at p = 0, 1 and 2, statistics of no values and of one value, the square root of a negative
value (J5). C-1: a consistency output that reads a stated value left out of the inputs, one whose witness is an
interval endpoint, and one that reads a free value (J4). R-1 to R-10: a complete request and answer for every kind and
outcome, `calc@0` and `arith@0` (J3). R-10 (draft 4, from the verification of the spec's draft 2) gives the unknown
(an exhausted count) and undefined (an empty mean) rows of a derivation, a consistency check and an identity, in
three requests over T-1's bytes, one per kind: R-10a, R-10b and R-10c each run in the later of ME-4 (their counted
values) and their kind's batch, ME-5, ME-8 and ME-9.

### 4.5 Negative controls from the pinned pilots, and regressions

- Constitution u0203.s02, u0112.s03 and u0147.s04 stay as they are: their "evidence" and "probability" are epistemic
  standards in norms (research 2.2). A calc case cannot carry a norm, an open term or a reading of them (`Unsupported`).
- W6a's news fixtures (`tests/test_news_w6a_fixtures.py`) and the math mini-paper's 18/19 are unchanged by every batch.

## 5. Batches

Every batch follows the rules quantities' plan 1.3 also lists: the selected tests while iterating, the full gate once on
the final HEAD, `python3 lean/audit.py` (standard axioms only, no forbidden words even in comments, theorem names under
about 57 characters), generated files regenerated with `uv run python tools/regen_generated.py --write` and merges
finished with `--resolve`, new trusted Lean lines with a signed allowance (`tools/trust_map.py --write --reason`, a
person) and a ROADMAP trust-cost line, hermetic tests, three-valued verdicts, and a seeded bug in each changed language.

### ME-0. Pin the targets; baseline partition (pilot runner, 3-4 h, no product code)

- **Pin**: for each target, fetch the text with a plain HTTP client (no model), record URL, retrieval time, licence
  evidence (publication date and authors' deaths for the public-domain texts; the licence link of the abstract page
  for a CC-BY one) and SHA-256 in `SOURCE.md`. New directories: `usecases/physics-michelson-morley/`,
  `usecases/math-ramanujan-bertrand/`, `usecases/ve-paper-e1/` (pins `paper/sections/04-e1.md` and the appendix table
  rows by SHA-256 at the batch's commit), and `usecases/dl-<slug>/` only for a confirmed CC-BY licence. Transcribe
  formulas into words in the translation, never into the source file.
- **Partition** every byte into units with kinds (exposition, definition, theorem, proof step, equation, quantity,
  table, empirical claim, comparison, hedge, citation, caption, meta) and today's statuses: W6a quantity facts and
  linear comparisons with unit tags (CHECKED), attributions (`reports@0`), labels (LABELLED), and UNFORMALISED with one
  `missing_feature` from: `calc`, `calc-data`, `calc-derive`, `calc-dimension`, `calc-stats`, `calc-algebra`,
  `arith`, `arith-import`, `approximation`, or a sibling's tag (`quantities`, `attitudes`, `events`, `attribution`).
- **Measure**: `coverage.json` with bytes by status and kind; a sentence-kind count replacing research 2.5's estimates;
  the NORTH-STAR rows M, H, DL, V refreshed from measurements.
- Shared files: none (new directories). Estimated: H 1.5-2.5 KB CHECKED, 13-16 KB LABELLED; V-E1 0.3-0.8 KB CHECKED;
  M 0 CHECKED; DL 2-4 KB if pinned (all **estimates**). Constitution and UDHR: 0.
- Done when the four (or three) ledgers account for 100% of their source bytes and `SUMMARY.md` states the numbers.
- **Done (phase 1, P1 PASS; 0.1).** Measured: H 1,858 B CHECKED (276 stated only, 1,582 in certified relations),
  11,560 B LABELLED, 10,950 B UNFORMALISED; V's E1 slice 1,199 B CHECKED (817 / 382), 4,088 B LABELLED; DL 4,453 B
  CHECKED (1,905 / 2,548), 49,707 B LABELLED; M 0 CHECKED, 265 B LABELLED, 2,386 B UNFORMALISED. Two deviations,
  accepted: the files are under `docs/research/evidence/math-evidence/`, not `usecases/`, and the pins are in
  `raw/fetch-log.json` and `SUMMARY.md`'s Sources table, not `SOURCE.md`; ME-P1 moves them (bytes and digests
  unchanged).

### ME-S. Statement spec, Lean stub, statement review (planner, 4-5 h)

Write `docs/spec/math-evidence.md` (statements of section 3 made exact, wire forms of section 2, diagnostics, the
fixtures of section 4 with definitions separated from expected results); elaborate section 3 in an untracked
`lean/SpecStubs_math_evidence.lean` against `main` (or a build at the same `lean/` tree); recompute every fixture with
`#eval` over `Rat`; settle the names `ResponseShape.Fits`, `Run.verdictAt`, `Nat.choose`, `Nat.bertrand`; define
`arith`'s fuel accounting (what counts as one step). Statement review by the reviewer pair (section 9); it confirms
each debate edit (A1-A6, F1-F5) with a fixture. The review of the spec's draft 1 converged on FIX (J1-J11); the spec's
draft 2 applies it, draft 3 applies the verification of draft 2 (FAIL narrowly: J2's `Run.unknown_named`, J3's
fixtures, the draft-2 choices to accept by name), and a bounded re-check of the changed sections and new fixtures by
both reviewers (spec 17), with the stub re-run, gates ME-1. The spec's draft 4 applies phase 1 to the fixtures (no
Lean statement changes); the re-check adds its item 8: H-4, H-5 and H-9 as rewritten, and the new H-5b, V-7b, M-4b
and DL-1 to DL-4, recomputed in the stub.

### ME-1. Lean core of `calc@0` (Lean, 5-6 h)

- New files: `lean/VE/Numbers/{Decimal,Round}.lean` (the shared `VE.Numbers`: `decValue`, `decValue_lower`,
  `tenPow`, `Printed`, `Rounding`, `RoundsTo` with its `Decidable` instance, `roundsTo_close`, `roundsTo_unique`),
  `lean/VE/Calc/{Syntax,Eval,Decls,Render,Examples}.lean`, `lean/CALC.md` (statement review notes, as
  `lean/RISK.md`). `VE.Calc` imports `VE.Numbers`. ME-1 lands before quantities' QT-A2, which proves
  `roundsTo_ratio_agree` against `VE.Numbers.RoundsTo`.
- Proves 3.1. It builds the operational types in their final shape (spec 2.3, 2.4): `Val.exhausted`, the `Counted`
  result of a counted source and `NameExhausted`, so that ME-4 only fills counted values (statement review J2).
  `Render.lean` gives the English line of each claim from `words` and the fixed phrases of 2.11 (display
  only; parse-back arrives with ME-11, whose engine then replaces `Render.lean`'s phrase table rather than sitting
  beside it). Every rendered rounding line names its tie rule. If quantities' QT-E has not landed, ME-1 moves W6's
  comparison phrases (`ve/english.py:51`, `_COMPARISONS`) into one Lean table, and Python reads them from a generated
  file; if QT-E landed first, ME-1 reads QT-E's table.
- `#guard` fixtures: V-1, V-1n, V-2, V-4, V-9, V-10, V-11, D-1, H-5, H-5b and H-4 with D stated (all three over the
  source's sq = 10⁻⁸), H-9's noon column at mark 16 (Mean, Mean in w. l., Final mean) and its negative control,
  DL-1, DL-2 under the rounded reading, DL-4.
- Hand-written shared: none. Generated: `lean/VE.lean`, `lean/VE/Audit.lean`, frozen inventory, axioms, statements,
  predicates, declarations, trust tables (signed).
- Seeded bug (Lean): `eval` computes `sub a b` as `b - a`; V-2's third claim fails its `#guard`.
- Bytes: 0 (no pilot run).

### ME-2. Wire and service mode `calc` (Lean, 5-6 h)

- New files: `lean/VE/Calc/{Wire,Run}.lean`, `lean/ResponseShape/Schemas/Calc.lean`,
  `lean/ResponseShape/Encoders/Calc.lean`.
- Proves 3.2 and the decoder limits of 2.1 in order; identities of 2.2, with every signed integer written as a
  canonical decimal string for the unchanged frozen encoder (statement review J1). It introduces spec 3.4's `Check`
  with its `claim` constructor, `Check.OutcomeMeans` and `Run.row_sound`; later batches add their kinds.
- Hand-written shared: `lean/VE/Service/Protocol.lean` (constructor, name, list entry, dispatch line,
  `runMode_calc`) and `ve/backends/service_schema.py` (`MODES`), which join the protocol queue in landing order; the
  `calc@0` row of AR-10's profile-gate table with its composition proof for the combinations it newly admits, and the
  `calc` mode's entry in AR-10's mode registry (ME-2 waits for AR-10's table; no hand-written `Dispatch.lean` rows,
  gate lemmas, `lean/VE/Compose/Examples.lean` additions or `ve/profiles.py` rows: Python's profile data is
  generated); `ve/assurance-manifest.json` (decoder pins, by hand), `ROADMAP.md` (trust-cost line). Generated:
  `ve/backends/lean_service_schema/calc.json`, `lean/ResponseShape.lean`, `lean/ResponseShape/Audit.lean`,
  `lean/checkers.lock`, `docs/spec/assurance-manifest.md`, `lean/VE/Route/examples/route-cases.json`, AR-10's
  generated profile data, and ME-1's list.
- Route cases: V-1, V-2, V-5 (20 claims in one case), V-11 (a limit hit beside a zero divisor), a software-convention
  case (V-9), I-1 (H-8's negative printed place), spec 13.6's R-1 and R-2 (every claim outcome), a hostile set
  (unknown name, a name defined after its use, `pow` above the limit, a literal of 41 digits, a printed spelling with a
  sign error, a forged `meaning_id`).
- Seeded bug (Lean): the runner reports claim i + 1's verdict for claim i; the route-case test fails.
- Bytes: 0.

### ME-3. Python relay, command, fuzz tests (Python, 4-5 h)

- New files: `ve/calc.py` (sends cases with `rows` from `ve/backends/relay.py`; binds every claim id, value name and
  data handle in the answer to the request, and each row's `kind` and kind fields as spec 3.4 lists them, each later
  batch extending the binding for its kind; displays Lean's English lines and exact values), `tests/test_calc_lean.py`,
  `tests/test_calc_answer.py` (fuzz: each member dropped, emptied, retyped, duplicated, reordered, an index out of
  range, one and two faults at a time; every mutant is `CheckerUnavailable` or changes nothing shown).
- Hand-written shared: `ve/__main__.py` (subcommand `ve calc check FILE`), `tools/layer_policy.py` (one row),
  `tests/data/route-cases.jsonl` (recorded by `tests/route_case_recorder.py`, append-only). Generated: `.importlinter`,
  `tools/gate-collection.json`.
- Seeded bug (Python): the binding check skips claim ids; a fuzz mutant that swaps two claim ids is accepted and the
  fuzz test fails.
- Bytes: 0.

### ME-P1. Pilot (backend evidence): ground calculations (pilot runner, 4-5 h; draft 4 said 2-3 h, before the move and the paper partition)

Companion calc cases beside the ME-0 ledgers (as the UDHR pilot's companion documents): physics H-5, H-5b, H-4 with D
stated, H-8 and the theory section's other numeric substitutions, and H-9's two tables in full (104 claims in one
case, within 2.1's limits); VE paper V-1 to V-4 and the other ratio sentences of `04-e1.md` and `05-e4.md`.
A unit is CHECKED when every claim of its companion case is decided by Lean.

- First (draft 5): move the ME-0 ledgers to `usecases/physics-michelson-morley/`, `usecases/math-ramanujan-bertrand/`,
  `usecases/ve-paper-e1/` and `usecases/dl-alphafold/`, and write each `SOURCE.md` from `raw/fetch-log.json` and
  `SUMMARY.md`'s Sources table (bytes and digests unchanged); then partition the rest of VE's paper (63,864 B outside
  the E1 slice) with today's VE, as ME-0 did the slice, so row V gets a whole-paper denominator.
- Measured ceiling: H +2,216 B (`calc`), V's slice +469 B; V outside the slice is measured by the step above. H-9's
  table rows are already CHECKED (most in certified relations), so H-9 adds almost no bytes: what it adds is the
  Mean in w. l. relation, which W6a cannot state, and a calc-route check of what W6a certifies today. Its sentence
  "the means of the six readings" (h086, 153 B, `calc-data`) describes readings that are not printed and stays
  UNFORMALISED.
- Shared files: pilot directories only.

### ME-4. Tables and pinned data (Lean and Python, 5-6 h)

- New files: `lean/VE/Calc/{Table,Csv,Jsonl,Data}.lean`, `tests/test_calc_tables.py`, `tests/data/calc/*.csv` and
  `*.jsonl` (small, committed).
- Proves 3.3. The service's existing handle table gains a data kind (`lean/VE/Service/Protocol.lean`, the `Handles`
  structure: hand-written shared, additive, part of the protocol queue); the relay registers file bytes by SHA-256 and
  sends them; Lean recomputes the digest. A translated document's pinned source is registered the same way, and Lean
  checks every `span` against it (debate F1); from here a failed claim can be a source finding. Residual lines use
  W2's `support` provenance field.
- Filters have negated atoms, each needing a cell of its type, and no general negation (statement review J9). Each
  counted value runs under the case's budget; `runCounted` takes the budget, and an exhausted run is `Counted.exhausted`
  (statement review J2).
- Fixtures: a 30-row synthetic trial table with counts by filter; V-5 recomputed from a committed table of the
  20 rows' counts (draft 5 drops H-9 here: its inputs are printed means, so ME-1 checks it); empty selections (count 0, sum 0, mean,
  minimum and maximum undefined); an absent cell making a mean undefined; T-1 with its absent and mistyped `approved`
  cells, selected by neither "that are approved" nor "that are not approved"; T-3 (an exhausted count read directly
  and through a definition beside an empty mean); spec 13.6's R-10a and R-10c if ME-5 or ME-9 landed first (4.4a); a
  wrong digest refused; V-12 (a span over a mistyped value refused); a source finding with every span checked beside
  "transcription unchecked" with one span missing.
- Seeded bugs: Lean, `isFalse` selects every row whose cell is not the Boolean true (T-1's "not approved" count
  becomes 3 and its `#guard` fails); Python, the relay sends the bytes of the wrong handle (the digest refusal test
  fails).
- Bytes: 0 (lands in ME-P2).

### ME-5. Derivations over rational unknowns (Lean, 5-6 h)

- New files: `lean/VE/Calc/{Linear,FourierMotzkin,Derive}.lean`, `tests/test_calc_derive.py`.
- Proves 3.4. Fourier-Motzkin elimination with multiplier tracking, within a budget (64 facts, 16 unknowns, 10,000
  combination steps); its output is replayed by `Farkas.check`; counterexamples are checked by evaluation.
- Adds the `follows` check and the case's `premises` list, the lowering (spec 2.7's `Expr.inline`, unless ME-8 or ME-9
  built it first, and spec 5's `Claim.facts`), the meaning `Follows` with its bridge theorems, and the `follows`
  clauses of `Check.OutcomeMeans` (statement review J3). Each square link is rendered as two premises and listed as a
  residual line (J10).
- Fixtures: H-6, H-6p, H-6n; spec 13.6's R-3 and R-4, and R-10a (unknown and undefined derivations) once ME-4 has
  landed; a linear system with no solution and its certificate; a forged
  certificate with a negative weight refused; the assignment s = 0, r = 1 against H-6's premises, rejected as a
  counterexample because it breaks the link s = r² (debate A2).
- Seeded bug (Lean): `Farkas.check` accepts a negative weight; a forged certificate for a false conclusion is accepted
  and its regression fails.
- Bytes: 0.

### ME-6. Physical dimensions (Lean, 4-5 h; after ME-1, before quantities' QT-A7)

- New files: `lean/VE/Calc/{Dimension,Units}.lean`, `tests/test_calc_dimensions.py`.
- Proves 3.5. ME-6 is the only decoder and the only owner of `ve-units@2`: base dimensions, `base_exponents`, an
  exact positive `factor`. Quantities' QT-A7 consumes it and uses `convert_by_factors`. Refuses affine and
  logarithmic units by name. `ve-units@1` tags stay nominal: identically declared tags remain incompatible
  (`units-schema.md` 2.1), each tag is read as its own base dimension, and `ve-units@1` identities are unchanged.
  `day` is never a unit of a physical dimension and never converts; durations use `elapsed_day`.
- Fixtures: H-7; meters against kilometers converted by factors; a sum of a length and a time refused with both names;
  two identically declared `ve-units@1` tags still incompatible; a declaration that gives `day` `base_exponents`
  refused; I-2 (a velocity's exponent −1 written as a canonical decimal string in the environment's identity, so the
  frozen encoder accepts it; statement review J1).
- Seeded bug (Lean): `dimOf` of `div` adds exponents instead of subtracting; H-7's "D/λ is dimensionless" fails.
- Bytes: 0.

### ME-P2. Pilot (backend evidence): bounds, dimensions and counts (pilot runner, 3 h)

Physics: the velocity bounds (H-6, H-6p), dimensions of the theory section (H-7), and Mean in w. l. as ME-6's unit
change if ME-P1 stated the factor as a value. VE paper: counts recomputed from committed count tables (V-5).
Measured ceiling (draft 4 estimated H +3.0-4.5 KB, V +1-2 KB, before ME-0 found the tables already CHECKED): H +467 B
(`calc-derive` 222 B, `calc-data` 153 B, `calc-dimension` 92 B; the 153 B are h086, which stays UNFORMALISED, so
314 B are reachable); V's slice +512 B (`calc-data`). ME-4's physics role is gone; it stays for V's counts, DL's
figure data and EX-5.

### ME-7. Exact statistics (Lean, 5-6 h)

- New files: `lean/VE/Calc/Stats.lean`, `tests/test_calc_stats.py`.
- Proves 3.6. Assumption leaves per procedure (2.8). Adds the constructors `stat`, `binom`, `kappa` and `sqrtRounds`
  to ME-1's `Expr` and `Claim` (its own `lean/VE/Calc/` files), with their meaning clauses, and re-proves ME-1's
  theorems for them; the column aggregates `variance` and `populationVariance` join ME-4's `Agg`, so that part waits
  for ME-4. Domains are in the meaning: undefined outside them (statement review J5).
- Fixtures: V-6, V-6r; S-5 (domain boundaries); a sign-flip p over 12 synthetic differences checked against
  exhaustive hand enumeration; a binomial tail; Cohen's kappa of a 2 × 2 table.
- Seeded bug (Lean): the sample variance divides by n; V-6's SD claim fails (it would print 0.103).
- Bytes: 0.

### ME-8. Consistency of printed numbers (Lean, 4-5 h)

- New files: `lean/VE/Calc/{Interval,Consistency}.lean`, `tests/test_calc_consistency.py`.
- Proves 3.7 and `signFlipP_grain`'s use as a granularity check: the witness and both refutations against the one
  `Consistent`, over the lowering with the inputs kept (statement review J4).
- Fixtures: V-7 (granularity), V-7b (the six main-text p values over 2¹², draft 5), V-8 (tie rule), V-6 from the
  printed per-template values (a witness: the printed values
  themselves), C-1 and spec 13.6's R-5 (an output that reads a stated value left out of the inputs; a witness at an
  interval endpoint; a free value refused), R-10b (unknown and undefined consistency checks; ME-4 is in place, since
  ME-8 follows ME-7), and GRIM as a `#guard` of `mean_grain_refutes` (S-3: a mean of five
  integer scores printed as 3.47, impossible since 5 × 3.47 = 17.35 has no integer within rounding; GRIM has no route
  form, spec 16 C17).
- Seeded bug (Lean): the enclosure of `sub` uses [lo − lo, hi − hi]; the consistent fixture V-6 is refuted and fails.
- Bytes: 0.

### ME-9. Algebraic identities (Lean, 5-6 h)

- New files: `lean/VE/Calc/Poly.lean`, `tests/test_calc_algebra.py`.
- Proves 3.8, over sides inlined with the free values kept, against the meaning `IsIdentity` (statement review J3).
- Fixtures: H-1, H-2, H-3, H-4 with D free; spec 13.6's R-6, and R-10c (unknown and undefined identities) once ME-4
  has landed; the false "(a + b)² = a² + b²" not shown, with the point a = b = 1; a division by an expression that can
  be zero denotes nothing at that point.
- Seeded bug (Lean): monomials with different variable lists are merged; "(a + b)² = a² + b²" is reported an identity
  and its regression fails.
- Bytes: 0.

### ME-10. Calculation content in documents (Lean and Python, 5-6 h)

- New files: `lean/VE/Calc/Document.lean`, `tests/test_calc_document.py`.
- `calculation` content in `ve-document@1` goes through Lean's `document` mode; the `calc:` leaf label (2.12); statuses
  and findings; coverage counts `support: calculation` units as checked only with a Lean verdict. A discharged leaf
  states its check's meaning for every kind (spec 10's `calcLeaf_holds`).
- Hand-written shared: the `document` mode's content dispatch (`lean/VE/Service/Document.lean`, one branch; after
  `lean-first/b16g` or its successor adds a content hook, rebased onto it; it joins the document-mode queue in
  landing order AT-3b, SC-1b, QT-A4, ET-5, WG-4, ME-10), `lean/VE/ClaimGraph.lean` is **not**
  edited: the label is a string the existing `Claim.label` carries; `ve/document.py` only if the hook is not yet in
  Lean (one dispatch line).
- Seeded bugs: Lean, a `calc:` leaf accepted when its claim fails (the document test fails); Python, the relay drops a
  finding from the display (the binding test fails).
- Bytes: 0 new (companions become document units).

### ME-11. English in Lean's engine (Lean, 5-6 h; after english-lean E3's quantities step, quantities' QT-E)

- Rules for the wordings of 2.11 in Lean's English engine, whole-sentence derivation uniqueness, parse-back of every
  rendered line to the same canonical case, refusals with rewrites in Lean's diagnostic table (the nested-phrase
  refusal, "the difference between", "on the order of", "on par", "comparable", every symbol, "A is E" with an
  expression E (`IsExpression`, statement review J7), and a places phrase that does not name the printed spelling's
  places (`PlacesMismatch`, J8)). A square link reads back from its two consecutive premises (J10). The approximation
  words "about", "approximately", "roughly" and "nearly" are one row of english-lean's catalogue shared with
  quantities: QT-A6, earlier in the queue, adds it; ME-11 reuses it and adds only what is missing ("on the order of",
  "on par", "comparable"). The engine's rules replace `Render.lean`'s phrase table rather than sitting beside it, and
  the comparison phrases keep their single Lean owner.
- Hand-written shared: `lean/VE/EnglishGrammar/*`, one batch at a time in the serialised English queue
  `AT-5 → QT-A6 → ME-11 → QT-B3 → SC-7` (ME-11 is third; QT-E gates QT-A6, ME-11 and QT-B3); additive rules, rebased in
  turn. Generated: `lean/VE/EnglishGrammar/Fixed/*.lean`, `ve/english_grammar/LOCK.json` (a person's
  `--actions-version`), `ve/english_grammar/codes.json`.
- Fixtures: every wording of 2.11 round-trips, including one rounding sentence per tie rule and a derivation with a
  square link; the refused sentences give their rewrites; "standard deviation" alone is refused in authoring.
- Seeded bug (Lean): "A minus B" built as B minus A; the round-trip fixture fails.
- The English authoring milestone needs, beyond ME-10 and ME-11, a pre-registered writing and comprehension eval with
  Sonnet as reader and writer, as in the readability eval; ME-11's parse-back is internal evidence only.
- Bytes: 0 (readability).

### ME-P3. Pilot (backend evidence): physics complete, VE paper statistics, deep learning (pilot runner, 3-4 h)

Physics H-1 to H-3 and the theory section; VE paper V-6 to V-8, V-7b and the appendix tables' rows (consistency and
recomputation); AlphaFold's DL-1 to DL-4 and its other stated statistics and comparisons. Measured ceiling (draft 4
estimated H +1.5-2.5 KB, V +10-16 KB, DL +5-8.5 KB): H +752 B (`calc-algebra`); V's slice +2,858 B (`calc-stats`,
28.8% of the slice, its largest lever), and outside the slice whatever ME-P1's partition measures; DL +1,475 B
(`calc-stats` 1,329 B, `calc` 146 B). DL's `calc-data` (3,355 B) compares values that the text gives only in figures;
it counts only if the figure source data are pinned (DEFERRED in 0.1: after ME-4, under D22's licence rule), else it
stays UNFORMALISED.

### ME-12. Lean core of `arith@0` (Lean, 5-6 h; after ME-1, whose `VE.Numbers` it imports; independent of ME-2 to ME-11)

- New files: `lean/VE/Arith/{Syntax,Holds,Defs,Bounded,Examples,Wire,Run,Render}.lean`,
  `lean/ResponseShape/Schemas/Arith.lean`, `lean/ResponseShape/Encoders/Arith.lean`, `lean/ARITH.md`, `ve/arith.py`,
  `tests/test_arith_lean.py`, `tests/test_arith_answer.py`.
- Proves 3.9's meaning and bounded-evaluation theorems; mode `arith`. A count's meaning is defined through `Holds`;
  the evaluator is proved to agree. The budget is the spec's fuel accounting (one unit per formula-node visit, default
  and maximum 1,000,000).
- Builds spec 12.5's contract (statement review J3): the `ve-arith@0` request with named variables, its limits, the
  identity over de Bruijn indices with numerals as canonical decimal strings, the refusals (`UnscopedVariable`,
  `ShadowedVariable`, `UnknownDefinition`, `RecursiveDefinition`, `ArityMismatch`, `UnboundedCount`), rows that hold,
  fail or are unknown with their theorems, the deciding value of the outermost bounded quantifier, `runMode_arith` and
  the encoder theorem; the relay binds each row to its statement.
- Hand-written shared: as ME-2 and ME-3 (`Protocol.lean`, `service_schema.py`, the `arith@0` row of AR-10's
  profile-gate table with its composition proof and the mode's entry in AR-10's mode registry, `ve/__main__.py`,
  `tools/layer_policy.py`, the assurance manifest, ROADMAP); waits for AR-10's table; no hand-written `Dispatch.lean`
  rows or `ve/profiles.py` rows. Generated: as ME-2 and ME-3.
- Fixtures: M-1, M-2, M-4, M-4b (draft 5: formula (18)'s other four pairs), M-4x, M-5 (with its deciding value
  n = 1); spec 13.6's R-7 and R-8; a definition that
  calls itself refused; an unscoped variable and a call of an undefined name refused; an unbounded statement reported
  "stated, not decided". ME-12 measures M-4 at the candidate bounds 200 and 1,000 and pins the completing bound from
  that measurement, and does the same for each pair of M-4b.
- Seeded bugs: Lean, a bounded quantifier from lo to hi ranges up to hi + 1 (M-5 fails); Python, the relay accepts a
  row for a statement it did not send (the binding fuzz test fails).
- Bytes: 0.

### EX-1. Experiment: Mathlib proofs of VE's own statements (planner and Lean, 4-6 h)

- **Pre-registered bar** (all must hold): (1) VE generates the statements and identities of Bertrand's postulate
  (whole-number reading, M-3), "there is no largest prime", and "every prime greater than 2 is odd"; (2) a new Lake
  project `imports/mathlib/` at the toolchain `leanprover/lean4:v4.24.0` and the Mathlib revision built for it proves
  `Defs.Means` of each and compiles the generated `theorem check : Defs.Means ⟨D⟩ ⟨φ⟩ := <declaration>` for each; (3) `#print axioms` of each is within `propext`, `Classical.choice`, `Quot.sound`; (4) on the
  VM, a clean build takes at most 3 hours with Mathlib's prebuilt cache or 6 hours without, and uses at most 15 GB of
  disk; (5) the bridge lemmas (VE's definitions against Mathlib's) total at most 150 lines; (6) a blind independent
  audit by the reviewer pair finds that the English rendering of M-3 states Ramanujan's theorem under the whole-number
  reading.
- Pass: build ME-13. Fail: record which item failed; mathematics stays at bounded evaluation; the M row's "after the
  plan" ceiling is 10.3% (measured by ME-0; draft 4 estimated 6-12%) instead of 23.2%.
- Files: `imports/mathlib/{lakefile.toml,lean-toolchain,VEImports/*.lean,README.md}`, `experiments/math-evidence-EX1/`
  (report and measurements). Shared files: none. No test in the suite builds Mathlib (hermetic tests).

### ME-13. Import records (Lean and Python, 4-5 h; only if EX-1 passes)

- New files: `lean/VE/Arith/Import.lean`, `tools/lean_import_check.py` (builds the import project, reads `#print axioms`,
  writes the record; not a test), `tests/test_arith_import.py` (record admission and labels only, hermetic).
- Proves `Import.admit_sound`, `Case.import_row` and `Run.import_sound` (spec 12.5, replacing draft 2's
  `report_import_labelled`, statement review J3): the record binds the statement's id (one import per
  imported conclusion), the digest of VE's meaning sources, the project revision, the declaration and the digest of
  the generated check file whose `theorem check : Defs.Means ⟨D⟩ ⟨φ⟩ := <declaration>` the external build compiled.
  Admission stays conditional on that external build; imports are always residual support. Fixture: spec 13.6's R-9.
- Hand-written shared: none beyond ME-12's mode (a new case kind). Generated: as ME-2, plus the meaning-source digest
  file (registered in `tools/regen_generated.py`).
- Seeded bugs (Lean): `admit` skips the axiom check (a record listing an extra axiom is admitted and its test fails);
  `admit` skips the statement-id check (an import for "every prime greater than 2 is odd" is accepted as support for
  Bertrand's postulate and its test fails).
- Bytes: 0.

### ME-P4. Pilot: mathematics (pilot runner and a person, 2-3 h, plus the person's transcription)

- First (draft 5): a person transcribes the paper's formulas from the scan into a translation companion and checks
  it against the scan; the pinned source stays the OCR bytes, and every span still points into them. No model is
  used.
- Then M-1 to M-4b in the Ramanujan ledger; the main theorem by import if ME-13 landed.
- Measured ceiling (draft 4 estimated M +0.5-1.0 KB): +272 B without imports (`arith` 220 B, `calc-derive` 52 B;
  10.3% of the text), +344 B more with imports of the theorem statements (23.2%). The analytic chain (2,114 B,
  79.7%) stays residual even if EX-1 passes.

### EX-2. Experiment: approximations with error bounds (Lean, 5-6 h)

Square roots by squared bounds in derivations (for example "the square root of 1 + y is at most 1 + y/2 for y ≥ 0",
by squaring and the nonnegativity of (y/2)²), sums-of-squares certificates checked by ME-9's normaliser (Harrison 2007),
and exact remainders. **Bar**: certify, with Lean-checked certificates each replayed in under one second, (a) H-2's
remainder bound for |v/V| ≤ 10⁻³, (b) the transverse path "2D√(1 + v²/V²) differs from 2D(1 + v²/(2V²)) by at most
D(v/V)⁴/4", and (c) the Einstein alternate's "1/√(1 − β²) − 1 − β²/2 is between 0 and β⁴ for 0 ≤ β² ≤ 1/2". Pass:
plan an `approximation` batch. Fail: these sentences stay residual with the reason named.

### EX-3. Trigger: tensor shapes (draft 5; was an experiment)

Shapes as a second dimension-like type (rows by columns) for products, transposes and sums of declared matrices.
Draft 4's bar ("on the pinned DL text, at least 80% of its method equations with matrix operands receive a shape")
cannot be measured: ME-0 counted no equations in AlphaFold's main text, which names array shapes only in one caption
(d035, 162 B, LABELLED); its shapes are in the unpinned supplement. **Trigger**: a pinned DL text (AlphaFold's
supplement under D22's rule, or another target) with method equations over matrix operands. Then EX-3 runs with
draft 4's bar (Lean, 4-5 h; after ME-6): pass plans a shapes batch beside ME-6; fail leaves method equations as
definitions with prose types.

### EX-4. Trigger: folds and induction in `arith@0`

Trigger: a pinned text needs a product over an unknown list (Euclid's N) or an induction VE must check itself (the
Dedekind alternate). Until then, imports cover unbounded proofs.

### EX-5. Experiment: large data through the service (Lean and Python, 3-4 h)

Chunked data handles (each chunk at most 8 MB with its own digest; the whole by its digest). **Bar**: the
20,975,471-byte E1 trial file (`experiments/E1/runs/e1-scored-0921/trials.jsonl`) registered and verified by Lean, the
20 counts of V-5 recounted from it in at most 60 seconds on the VM, and equal to the printed counts (or each difference
listed as a finding). Pass: V's counts bind to raw trials. Fail: they stay bound to the committed count table.

## 6. In-flight work, dependencies and merge conflicts

| Batch | Waits for (branch where known) | Hand-written shared files | Generated (regenerate) |
|---|---|---|---|
| ME-0 | — (**done** in phase 1) | none: the evidence is under `docs/research/evidence/math-evidence/` | — |
| ME-S | draft 2 | `docs/spec/math-evidence.md` (new) | — |
| ME-1 | ME-S PASS (after the bounded re-check of spec 17); lands before quantities' QT-A2 | none (`lean/VE/Numbers/` and `lean/VE/Calc/` are new); `ve/english.py` (`_COMPARISONS` read from the generated phrase file) only if QT-E has not moved the phrases | `lean/VE.lean`, `lean/VE/Audit.lean` (union merges), frozen inventory, axioms, statements, predicates, declarations, trust tables, the comparison-phrase file |
| ME-2 | ME-1; AR-10's profile-gate table; `fix/main-relay` (main is red since ts-B1); `lean-first/b14d`, `question-answering/q2` and quantities' QT-A3, each of which edits `Protocol.lean` and `service_schema.py`: merged or rebased onto, in the protocol queue's landing order | `lean/VE/Service/Protocol.lean`, `ve/backends/service_schema.py`, the `calc@0` row of AR-10's table, `ve/assurance-manifest.json`, `ROADMAP.md` | response schemas, `lean/ResponseShape.lean`, `lean/ResponseShape/Audit.lean`, checker pins, assurance doc, route cases, AR-10's profile data, gate collection |
| ME-3 | ME-2; `mig3/py` if it touches `ve/backends/relay.py` | `ve/__main__.py`, `tools/layer_policy.py`, `tests/data/route-cases.jsonl` | `.importlinter`, gate collection |
| ME-P1 | ME-3 | pilot directories: the new `usecases/` directories, moved from `docs/research/evidence/math-evidence/` | — |
| ME-4 | ME-2 | `lean/VE/Service/Protocol.lean` (`Handles`, additive, in the protocol queue) | as ME-2 |
| ME-5 | ME-1 | none | as ME-1 |
| ME-6 | ME-1; lands before quantities' QT-A7 | the W6a unit decoder's version switch (`lean/VE/Time/Wire.lean`) only if `ve-units@2` is decoded there | as ME-1 |
| ME-P2 | ME-4, ME-5, ME-6 | pilot directories | — |
| ME-7, ME-8, ME-9 | ME-1 (ME-7 also ME-4 for its column aggregates; ME-8 also ME-7 for granularity) | none | as ME-1 |
| ME-10 | ME-2; `lean-first/b16g` (or the batch after `b16e` that gives the `document` mode a content hook); the document-mode queue AT-3b, SC-1b, QT-A4, ET-5, WG-4 before it | `lean/VE/Service/Document.lean` (one branch), else one line in `ve/document.py` | as ME-2 |
| ME-11 | english-lean E3's quantities step (quantities' QT-E; no branch yet); the english-lean E2 flip; AT-5 and QT-A6 before it in the English queue | `lean/VE/EnglishGrammar/*` (serialised queue `AT-5 → QT-A6 → ME-11 → QT-B3 → SC-7`; additive) | English `Fixed/*.lean`, `LOCK.json` (a person's `--actions-version`), English codes |
| ME-P3 | ME-7 to ME-9 (ME-10, ME-11 for display); DL's figure comparisons also ME-4 and pinned figure data | pilot directories | — |
| ME-12 | ME-S PASS; ME-1 (`VE.Numbers`: `Verdict`, `UnknownReason`, `Outcome`; statement review J6); AR-10's profile-gate table | as ME-2 and ME-3 | as ME-2 and ME-3 |
| EX-1 | ME-12 | `imports/` (new), `experiments/math-evidence-EX1/` (new) | — |
| ME-13 | EX-1 PASS | none | as ME-2 |
| ME-P4 | ME-12 (ME-13 if built); a person's transcription of the formulas | pilot directories | — |
| EX-2 | ME-9 | new experiment directories | as ME-1 if Lean is added |
| EX-3 (trigger) | its trigger (a pinned DL text with method equations over matrix operands), then ME-6 | new experiment directories | as ME-1 if Lean is added |
| EX-5 | ME-4 | `lean/VE/Service/Protocol.lean` (`Handles`) | as ME-2 |

How conflicts are avoided: all Lean is in new directories (`lean/VE/Calc/`, `lean/VE/Arith/`) and new response-shape
files; all Python in new modules (`ve/calc.py`, `ve/arith.py`) and new test files; the import project and the pilots in
new top-level and `usecases/` directories. The hand-written shared files are `Protocol.lean` (additive lines, in the
protocol queue's landing order), `service_schema.py`, AR-10's profile-gate table, `ve/__main__.py`,
`tools/layer_policy.py`, the assurance manifest, `ROADMAP.md`, the `document` mode's dispatch (document-mode queue) and
the English grammar files (English queue). Two profile rows (`calc@0`, `arith@0`) in AR-10's table are added in
separate batches, each after rebasing and each with its own composition proof. Generated inventories are never edited or merged by hand (`regen_generated.py --write`, then
`--resolve`). Before each batch, overlap is checked with `git diff --name-only main...<branch>` against the branches
above.

## 7. The measure

- **Denominators**: the pinned texts' bytes as ME-0 recorded them (`raw/fetch-log.json` and `SUMMARY.md`'s Sources
  table until ME-P1 writes `SOURCE.md`): H 24,368 B, M 2,651 B, DL 66,858 B; VE's paper sections by SHA-256 at the
  ME-0 commit (73,801 B at `49de179e`, measured with `wc -c`, confirmed by P5), of which ME-0 partitioned the E1 slice
  (8,883 + 1,054 = 9,937 B) and ME-P1 partitions the rest.
- **Statuses**: CHECKED when every claim of the unit's companion case or document content is decided by Lean (holds,
  or fails with a finding); OPEN when a claim is unknown; UNFORMALISED with a reason otherwise; LABELLED for exposition
  and meta; MIXED units split into parts as W2 specifies. A unit whose numbers are checked but whose hedge or causal
  framing is not is MIXED, never wholly CHECKED.
- **CHECKED in two parts** (draft 5, from ME-0, where one CHECKED count mixed two strengths): **stated only**, Lean
  admitted the value (a W6a quantity with `support: testimony`, or a calc `stated` value) and no relation over it was
  certified; and **in a certified relation**, the unit is a premise or the consequence of a relation whose
  certificate Lean replayed, or of a calc claim Lean decided. Today: H 276 / 1,582 B, V's slice 817 / 382 B, DL
  1,905 / 2,548 B. A premise of a certified relation is not itself certified (H's Mean in w. l. rows).
- **Premise status beside CHECKED** (draft 5): each pilot run reports the document's premise status from
  `ve document check`, three-valued: a checked model, a contradiction, or UNKNOWN within the budget. CHECKED never
  says the premises are consistent; with UNKNOWN (H, V and DL today: no model or contradiction within 10,000 proof
  steps and domain size 2) every certificate is replayed but whether it holds vacuously is undecided, and the report
  says so. Only M's premises have a checked model.
- **Reported each pilot run**: bytes and units by status and kind, CHECKED in its two parts, and the premise status;
  findings (source arithmetic that fails); the residual (stated values by support, data digests, assumptions,
  imports); and the NORTH-STAR rows M, H, DL, V refreshed. The constitution and UDHR runs are not touched by these
  batches (P3: 0 and 0).

### Effect per batch: measured at ME-0, measured ceilings after

Every number from ME-1 on is a **ceiling** read from the ME-0 ledgers (`docs/research/evidence/math-evidence/
summary.json`, `ceilings_percent`): the bytes of the UNFORMALISED units tagged with the features that pilot's batches
check, as if every one became CHECKED. Approximation units (H 2,731 B, DL 1,730 B, V 376 B) are left out, since D17
keeps them reading sets, never CHECKED. A pilot run measures the real number; a ceiling is not a forecast. Draft 4's
estimates are in parentheses.

| Batch | Constitution | UDHR | Physics (24,368 B) | VE paper (E1 slice, 9,937 B) | Deep learning (AlphaFold, 66,858 B) | Mathematics (2,651 B) |
|---|---|---|---|---|---|---|
| ME-0 (measured) | 0 | 0 | 1,858 B CHECKED, 7.6% (est. 1.5-2.5 KB) | 1,199 B, 12.1% (est. 0.3-0.8 KB) | 4,453 B, 6.7% (est. 2-4 KB for LoRA) | 0 |
| ME-P1 | 0 | 0 | ≤ +2,216 B (est. +0.6-1.0 KB) | ≤ +469 B (est. +0.8-1.5 KB, whole paper) | — | — |
| ME-P2 | 0 | 0 | ≤ +467 B, 314 B reachable (est. +3.0-4.5 KB) | ≤ +512 B (est. +1-2 KB) | — | — |
| ME-P3 | 0 | 0 | ≤ +752 B (est. +1.5-2.5 KB) | ≤ +2,858 B (est. +10-16 KB, whole paper) | ≤ +1,475 B; ≤ +4,830 B with figure data (est. +5-8.5 KB) | — |
| ME-P4 | 0 | 0 | — | — | — | ≤ +272 B; ≤ +616 B with imports (est. +0.5-1.0 KB) |
| After the plan | 0 | 0 | ≤ 21.7% (research 7: 20-31%) | ≤ 50.7% of the slice; whole paper unmeasured (research 7: 16-28%) | ≤ 13.9%; ≤ 8.9% without figure data (research 7: 14-25%) | ≤ 10.3% without imports, ≤ 23.2% with imports of the theorem statements (research 7: 6-12% and 10-20%) |

Research 7's physics upper range needed the approximation units to become CHECKED, which D17 rules out, and assumed
30-40 KB of text where ME-0 measured 24,368 B. The VE paper's whole-paper row stays research 7's **estimate** until
ME-P1's partition.

## 8. Not claimed, risks, open questions

- **Not claimed**: any byte before a pilot run measures it; that any stated value, data file or imported proof is true
  beyond what is checked; that a passing calculation makes a source's conclusion true; that readers follow worded
  equations (unmeasured; it needs human or proxy readers, which this plan does not call); any DL licence beyond
  AlphaFold's CC BY 4.0, which ME-0 read from its licence fields; that a CHECKED unit's premises are consistent (7).
- **Risks found by ME-0** (draft 5):
  - *The Rust accelerator's default limit.* At its default 5 s wall-clock limit the untrusted Rust checker stops the
    physics document (216 W6a constants), which is then CheckerUnavailable; with `VE_RUST_TIMEOUT=1800` Lean admits it
    in about 47 s (157 MB peak). VE's paper document hit the limit on one run of three, so it depends on load. A paper
    with two tables already reaches it. The calc route is Lean-only (D21), so ME-1's cases do not meet it; W6a
    documents and the `document` mode's other content do. It belongs to the Rust fast path's owner ("Cross-plan issues for the DRI", item 1).
  - *Premise consistency at scale.* `ve document check` leaves the premise set of the H, V and DL documents UNKNOWN
    (a few hundred stated quantities; domain size 2, 10,000 steps), so certificates are replayed but non-vacuity is
    undecided. A premise-consistency route that scales to a few hundred stated quantities is not in this plan
    ("Cross-plan issues for the DRI", item 2); until it exists the measure reports the status (7).
  - *OCR mathematics.* Both available texts of Ramanujan 1919 garble the formulas (79.7% of M is analytic and
    garbled); ME-P4 starts from a person's transcription.
  - *Figure-only results.* AlphaFold's comparisons rest on figure data (3,355 B); without pinned source data they
    stay UNFORMALISED and DL's ceiling is 8.9%.
- **Risks**: the paper texts' sizes and sentence kinds were estimates from memory until ME-0 measured them; exact arithmetic on large
  powers or long tables may hit limits (UNKNOWN, never a wrong verdict; measured in `tools/bench`); printed tables come
  from software whose floating-point results VE does not model (D6: the exact claim is decided, software reproduction
  is UNKNOWN, an undeclared tie rule is a reading set); Mathlib's build cost may fail EX-1's bar; english-lean E3 may be
  scheduled late, which delays input wordings (cases stay writable as JSON and display through Lean's rendered lines);
  physics dates before 1970 are outside W6's calendar (H-10): a recorded trigger, ET-T3 in events' plan, to extend W6's
  `VE.Time.Calendar` below 1970 under W6's own review, never a second calendar; until then H-10 stays refused.
- **Settled by ME-S** (the spec records each): the response-shape fit predicate is `ResponseShape.Fits`; the runner's
  reader is `Run.outcomeAt`; core has no `Nat.choose`, so ME-7 defines `choose`; `arith`'s fuel accounting. Still
  open: Mathlib's name for Bertrand's postulate (no Mathlib was available; EX-1 checks it); whether `Handles` can take
  a data kind without changing its existing theorems (ME-4).
- **Settled by the statement review** (spec 17; FIX, J1-J11): identities write signed integers as canonical decimal
  strings for the unchanged frozen encoder; a counted value keeps its mathematical value apart from its operational
  result, and exhaustion propagates through definitions; every check kind has its meaning, a clause per outcome and a
  row theorem; `arith@0` has a full request and response contract; one consistency proposition and one name rule;
  statistics are undefined outside their domains; ME-12 follows ME-1; "Let … be" rewrites, `IsExpression`,
  `PlacesMismatch`, typed negated filters and visible square links. The verification of the spec's draft 2 (FAIL
  narrowly) added: every unknown row names its cause (`Check.UnknownCause`), and R-10 shows unknown and undefined
  derivations, consistency checks and identities. Open until the bounded re-check: drafts 2's and 3's statements are
  not yet type-checked, their new fixture numbers were computed by hand, and both reviewers have still to accept by
  name the draft-2 choices beyond J1-J11 (spec 17, item 7: C14, C15, C17, C19, C20, C21).
- **Closed by the cross-plan review**: math-evidence owns the rounding module (`VE.Numbers`, built by ME-1; QT-A2
  proves agreement) and `ve-units@2` (ME-6; QT-A7 consumes it). Quantities' note that "the Lean tree depends on no
  library, so there is no ... rational type" (its plan 2.3) was false, since `lean/Iceberg.lean` uses core `Rat` with
  `import Std` at the pinned toolchain; quantities corrects it.

## 9. Review checklist (ME-S)

- `Denotes`, `Claim.Holds`, `RoundsTo`, `SqrtRoundsTo`, `Agg.run`'s specification and `Arith.Holds` state meanings
  without reference to the executable functions they are proved against; a count in `arith@0` is defined through
  `Holds`, not the evaluator.
- `RoundsTo` keeps the written places; the tie rule is explicit and named in every rounding sentence; QT-A2 proves its
  integer-ratio rounding agrees with `VE.Numbers.RoundsTo`; `roundsTo_unique` holds.
- Decided outcomes equal the mathematical verdict; unknown arises only for its named reason, and a limit hit is
  distinct from an undefined value; software reproduction is always unknown.
- A finding is a source finding only when every transcribed number it reads was checked against its span.
- Counterexamples satisfy every square link and its nonnegativity condition.
- Over an empty selection count and sum are 0, and mean, minimum and maximum are undefined.
- `compare_invariant` has no hypothesis beyond equal physical dimensions, normal forms and positive factors.
- `Farkas.check_sound` and `Derivation.check_sound` quantify over every rational assignment; linear infeasibility over
  ℚ with rational coefficients is infeasibility over the reals, so the soundness also holds for real-valued quantities
  (stated in `lean/CALC.md`, not as a theorem).
- The statistics definitions match `paper/analysis/README.md`'s stated procedures (sample variance, exact sign flips
  with the observed vector counted).
- `decideBounded_sound` is an equivalence whenever the evaluator completes; bounded quantifiers range exactly from lo
  through hi; the fuel accounting is stated and exhaustion is unknown.
- Import admission checks, for each conclusion, the statement id, the meaning-source digest, the generated check
  file's digest and the axioms; every unbounded `arith` conclusion carries a bounded decision or the leaf of an import
  admitted for its own statement.
- No symbol appears in any wording or diagnostic; every refusal names a rewrite.
- Every new trusted line has a signed allowance and a ROADMAP trust-cost line.
- (Statement review, spec 17.) Every canonical case and environment hashes with the unchanged frozen encoder; every
  check kind and every outcome has a meaning clause, a row theorem and a complete fixture (R-1 to R-10), with fails
  and unknown rows in `arith@0` too; every unknown row names its cause, for a claim the digit limit with `Overflows` or
  the budget with an exhausted read;
  witness and refutations prove and refute one `Consistent`; a negated filter never selects an absent or mistyped
  cell; each square link is visible as two premises; statistics are undefined outside their domains.
- (Phase 1, spec 17 item 8.) Every source fixture's case reads only what its anchored span states: H-4 and H-5 take
  the source's v²/V² = 10⁻⁸, never v/V = 10⁻⁴; H-9's case is the printed table (means of unprinted readings), not
  readings; the DL fixtures are AlphaFold's; every number of H-5b, H-9, V-7b, M-4b and DL-1 to DL-4 is recomputed in
  the stub.

## 10. Shared pieces

Abstractions several of the seven research-wave designs share, as the cross-plan review of 2026-10-13 settled them.

| # | Shared piece | Who would use it | Proposal |
|---|---|---|---|
| 1 | **Exact numbers**: one exact value function for written decimals (`VE.Time.Dec` → `Rat`), written places kept, the scientific form | quantities (`cardinality@0`), math-evidence, risk (estimates), events (durations) | `VE.Numbers` (`lean/VE/Numbers/Decimal.lean`), owned by math-evidence and built by ME-1; core `Rat` via `import Std` (contrary to quantities' plan 2.3, which quantities corrects, a rational type exists without Mathlib) |
| 2 | **One rounding definition with an explicit tie rule** (ties up by default; half to even on the exact value declared; bounds rounded down or up) | quantities QT-A2 (integer ratios), math-evidence ME-1 (any exact value) | `VE.Numbers.RoundsTo` (`lean/VE/Numbers/Round.lean`); ME-1 builds it before QT-A2, and QT-A2 proves `VE.Cardinality.roundsTo_ratio_agree` against it; an undeclared tie in a translated source is a reading set |
| 3 | **One unit registry `ve-units@2`**: base dimensions, `base_exponents`, exact positive factors | quantities QT-A7, math-evidence ME-6, events (days, weeks) | ME-6 owns and decodes it; QT-A7 drops its `converts` design and `convert_iff` and uses `convert_by_factors`; `ve-units@1` tags stay nominal; `day` never converts (durations use `elapsed_day`); "physical dimension" in prose so that quantities' comparison "dimension" keeps its name |
| 4 | **Pinned inputs by digest**: the service's handle table for environments and data, W5's adapter records, risk's hash-chained log, import records, VEX's evidence snapshots | math-evidence (data, imports), weighing and risk (records), events (dated evidence), attribution (quoted sources) | ME-4's data kind in `VE.Service.Handles`; no shared record-shape project |
| 5 | **A residual line for external support**: stated values with a support kind, data digests, procedure assumptions, imports, adapter outputs | math-evidence, events (causal links' support), weighing (decisions), attitudes (attributed beliefs) | W2 `support` provenance; no new line format |
| 6 | **Approximation words** ("about", "approximately", "roughly", "nearly", "on the order of") | quantities (refuses "about"), math-evidence, events ("around noon") | one row in english-lean's catalogue, which QT-A6 adds; ME adds rows only ("on the order of", "on par", "comparable"); refused in authoring with the rounding or range rewrite; in translation a reading set {rounded to the written digits, an open tolerance with a decider} |
| 7 | **Hedged quantitative claims** ("probably less than one sixth") | attitudes (likelihood words), math-evidence (the bound and its derivation) | attitudes owns the word, math-evidence the bound; joining them needs a separately reviewed calc–attitudes bridge, which no plan owns yet |
| 8 | **Procedures and dated sessions** ("observations at noon on July 8, 9, 11 and 12, 1887") | events-time-causation, math-evidence | events owns events and its anchor, and `VE.Time.Calendar` is the one calendar; dates before 1970 are W6's recorded trigger ET-T3 |
| 9 | **Arithmetic noun phrases and number words in Lean's English engine** | quantities, math-evidence, act-phrases, attitudes, scope | one lexicon of number words and arithmetic phrases, additive rules, one owner per wording |
| 10 | **Readings distinguished by a number** ("SD" with divisor n or n − 1; "x" a whole number or a real; "a/2b"; an undeclared tie rule) | math-evidence, quantities ("16 of the 18": exactly or at least), scope | reading sets whose distinguishing situation is an exact value computed by `calc@0`, a service to any design with numeric readings |
| 11 | **Section-scoped declarations** (scope's piece: "all lengths in this section are in meters") | scope, quantities, math-evidence | calc cases read a section's declared units through scope's anchor reach once it exists |
| 12 | (deleted in draft 2: profile registration is AR-10's profile-gate table, an existing item whose scope now includes the gate; there is no additional route-registry project) | | |
| 13 | **VE statements as Lean propositions** (`VE.Arith.Holds` as the target of imports) | math-evidence, question answering (citing proved facts), ROADMAP's "Lean statement layer for mathematics" | one meaning function per profile that an external Lean project can import and prove, with one import-record format |

## Change log

- Draft 1 (2026-10-13): first plan, from the research note of 2026-10-12; aligned with quantities' plan draft 1
  (rounding, units, the "X out of Y" wording, the word "dimension").
- Draft 2 (2026-10-13): applies the converged review of draft 1 (Astra + Fable, REVISE narrowly, CONVERGED after
  round 3) and the cross-plan synthesis edits; the architecture is unchanged.
  - A1: verdicts stay holds/fails/undefined; an operational outcome adds unknown with a named reason; decided rows
    equal `Claim.decide` and unknown arises only for its reason; fixture V-11 (D7, 2.4, 3.1, 3.2).
  - A2: counterexamples include every square link and its nonnegativity (2.6, 3.4, ME-5).
  - A3: imports bind the statement id, the meaning sources, the project revision, the declaration and the generated
    `check` theorem's file, compiled by the external build at exactly `Defs.Means D φ` (D20, 2.13, 3.9, EX-1, ME-13).
  - A4: over an empty selection count and sum are 0; mean, minimum and maximum are undefined (2.5, 3.3, ME-4).
  - A5: `ve-units@1` tags stay nominal (D12, 2.7, ME-6).
  - A6: "A minus B" replaces "the difference between A and B", which is refused with that rewrite; the English
    authoring milestone needs a pre-registered writing and comprehension eval; ME-P1 to ME-P3 are backend evidence
    (D17, 2.11, ME-11, order).
  - F1: a source finding needs Lean-checked spans; otherwise "transcription unchecked"; fixture V-12 (D7, 2.4, 2.5,
    ME-4).
  - F2 (merged in round 3): one rounding definition with two declarable rules, ties upward and half to even on the
    exact value; a software convention splits the exact claim (decided) from software reproduction (UNKNOWN,
    "floating-point computation not modelled"), never a source finding; fixtures V-9 and V-10 (D6, 2.1, 2.3, 2.15).
  - F3: one Lean owner for the comparison phrases; ME-11's engine replaces `Render.lean`'s phrase table (D17, 2.14,
    ME-1, ME-11).
  - F4: an `arith` count is defined through `Holds`; the evaluator is proved to agree (D19, 3.9, ME-12).
  - F5 (merged in round 3): `arith`'s budget and fuel accounting are stated by ME-S; ME-12 measures M-4's completing
    bound; exhaustion is tested with an insufficient budget (fixture M-4x).
  - Order: ME-8 follows ME-7; ME-S → ME-12 → EX-1 → conditional ME-13.
  - Cross-plan synthesis edits 1-10: `VE.Numbers` owned by math-evidence and built by ME-1 before QT-A2; each rounding
    sentence names its tie rule; ME-6 owns `ve-units@2` and QT-A7 consumes it, `day` never converts; ME-4 extends
    `Handles` and W2 `support` with no new record or registry project; `calc@0` and `arith@0` register through AR-10;
    hedged calculations need a separate calc–attitudes bridge; dates before 1970 are W6's trigger ET-T3; the English
    and document-mode queues; the order line.
  - ME-S's statement spec, [math-evidence.md](math-evidence.md), is written with this draft; its statements were
    type-checked and its fixture numbers computed in an untracked stub.
- Draft 3 (2026-10-13): applies the converged statement review of the spec's draft 1 (Astra + Fable,
  `manage-agents/debates/math-evidence-spec/`, FIX, CONVERGED after round 2) with the spec's draft 2; no other design
  change. The spec's section 17 maps each edit to its statements and fixtures, and section 16 (C12-C23) records the
  readings draft 2 chose.
  - J1: canonical decimal strings for signed integers in identities; the frozen encoder unchanged (2.2, ME-2, ME-6).
  - J2: counted values keep the mathematical value and the operational result apart; exhaustion is named and
    propagates through definitions; `run_unknown` is disjunctive; `runCounted` takes the budget (2.5, 3.1, 3.3, ME-1,
    ME-4).
  - J3: every check kind (claim, derivation, consistency, identity) has its meaning, outcome clauses and row theorem;
    derivations become the claim form `["follows", …]` with a `premises` list; `arith@0` has its request, limits,
    identity, rows, refusals and deciding values; draft 2's `report_import_labelled` becomes `Case.import_row` (2.1,
    2.6, 2.10, 2.13, 3.9, ME-2, ME-3, ME-5, ME-9, ME-12, ME-13).
  - J4: one `Consistent` proposition and one name rule; inputs are kept by the lowering (2.9, 3.7, ME-8).
  - J5: statistics are undefined outside their domains (2.8, 3.6, ME-7).
  - J6: ME-12 follows ME-1 (order 7, ME-12, section 6).
  - J7-J10: "Let … be" rewrites and `IsExpression`; `PlacesMismatch`; typed negated filters; square links shown as
    two premises (2.5, 2.6, 2.11, ME-4, ME-11).
  - J11: V-7 names the fourth row; the source-number grammar admits "0"; the EX-1 snippet declares its bridge lemma
    first and uses the spec's `primeDefs` (4.1, 3.9).
  - New fixtures (4.4a): I-1, I-2, T-3, T-1's added rows, S-5, C-1, R-1 to R-9; computed by hand, recomputed in the
    stub at the bounded re-check.
- Draft 4 (2026-10-13): applies the verification of the spec's draft 2 (`manage-agents/math-evidence-p3ver1.final.md`,
  FAIL narrowly: J1-J11 present, the numbers it checked correct) with the spec's draft 3; no other design change. Spec
  16's C24-C26 record the readings draft 3 chose.
  - J2: `Run.unknown_named` concludes the spec's `Check.UnknownCause`, which is `run_unknown`'s disjunction for a claim
    row (the spec's draft 2 had kept only the budget's cause) and gives derivations, consistency checks and
    identities a cause at the digit limit, met only in the lowering (`Expr.inline_tooLarge`); `Check.OutcomeMeans`
    uses the same cause (3.2's note).
  - J3: R-10 adds the unknown and undefined rows of each of those kinds, in three requests, each run in the later of
    ME-4 and its kind's batch (4.4a, ME-4, ME-5, ME-8, ME-9); the spec's linearity rule needs no value, so a premise
    whose counted value is exhausted or undefined gets its row.
  - The draft-2 choices beyond J1-J11 (spec 16's C14, C15, C17, C19, C20, C21) are named in the spec's re-check item
    7, for both reviewers to accept explicitly (8).
- Draft 5 (2026-10-13, branch `research/math-evidence-p1`): applies phase 1 (ME-0) with the spec's draft 4; the list
  at the top gives the changes. No Lean statement, owner, shared item or build order changes. Kept: every batch ME-1 to
  ME-13 (phase 1 cancels none), EX-1, EX-2, EX-5. Changed: H-4, H-5, H-9 (P4), the DL target and fixtures (P2), ME-P1
  (H-9, the move to `usecases/`, the paper partition), ME-P2 (no H-9), ME-P3 (AlphaFold), ME-P4 (transcription first),
  the measure (CHECKED in two parts, premise status, ceilings). Demoted: EX-3 to a trigger. Dropped: draft 4's DL-1 to
  DL-5.

## Cross-plan issues for the DRI

Phase-1 results that bear on what the cross-plan review settled (`SYNTHESIS.md`, `edits-math-evidence.md`). None of
the shared parts is changed in this plan; each item names the owner and what the DRI is asked to decide.

1. **The Rust accelerator's default limit stops a two-table paper** (owner: the Rust fast path in `rust/` and its
   relay timeout; not this plan, D21). At the default 5 s wall-clock limit the untrusted checker stops ME-0's physics
   document (216 W6a constants) and, under load, VE's paper document; the answer is CheckerUnavailable, and Lean admits
   both with `VE_RUST_TIMEOUT=1800` (physics in about 47 s). The UDHR pilot reported the same load dependence. The
   calc route is Lean-only and is not affected; every pilot that states a table as W6a facts is. To decide: a limit
   set by measurement, a Lean-only path for large stated documents, or stated tables carried as ME-4 data handles
   (which keeps ME-4's shared item, a data kind in `VE.Service.Handles`, but widens what it carries). Until then this
   plan's pilots run with a raised `VE_RUST_TIMEOUT` and say so.
2. **Premise consistency for documents with a few hundred stated quantities** (owner: the `document` mode's premise
   check, `ve document check`; not this plan). It leaves H, V and DL UNKNOWN (domain size 2, 10,000 steps), so every
   certified relation in them has undecided non-vacuity. This affects every plan whose pilot counts certified bytes.
   To decide: who builds a premise-consistency route that scales (for example, one that exploits that stated W6a
   facts are ground). This plan only reports the status (7).
3. **"Around" and the shared approximation row** (owner: english-lean's catalogue; QT-A6 adds the row, and edit 8 and
   section 10 piece 6 fix its words as "about", "approximately", "roughly", "nearly", with ME adding only "on the
   order of", "on par", "comparable"). AlphaFold uses "around" ("around 350,000 diverse sequences", DL-3; "around
   1,300 residues"), and piece 6 already cites events' "around noon". To decide: whether "around" joins the shared row
   in QT-A6 or is a row ME-11 adds. This plan adds neither.
4. **NORTH-STAR rows M, H, DL and V** (owner: the DRI; the file is in `ve-northstar`). The measured text is the
   phase-1 report's 4.4: H 7.6% CHECKED, ceiling 21.7%; M 0%, ceilings 10.3% and 23.2%; DL 6.7%, ceilings 13.9% and
   8.9%; V's E1 slice 12.1%. To decide: apply it at the next NORTH-STAR update; the weights are unchanged.
5. **No change asked** (recorded so the DRI need not check): ME-4 loses its physics fixture (H-9 needs only ME-1), but
   its shared item and protocol-queue place stay, since V's counts, DL's figure data and EX-5 need it; the pilot order
   and the build order are confirmed; H-10 stays refused until events' ET-T3, as edit 7 says.
