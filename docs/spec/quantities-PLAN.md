# Quantities: plan (counts and proportions; comparisons and graded words)

> **Status.** Draft 4, 2026-10-13, branch `research/quantities-p1`. Draft 3 (branch `design/quantities` from `main` at
> `49de179e`: draft 1 of 2026-10-12, the converged plan debate of Fable and Astra, the cross-plan synthesis edits 1–10
> of `SYNTHESIS.md`, and the QT-0 statement review's FIX) plus the results of phase 1:
> [docs/research/quantities-phase1.md](../research/quantities-phase1.md) (cited as P1 and a section number), as
> revised after its review. Draft 4 changes only what phase 1 measured or found; the synthesis edits (owners, shared
> items, build order) are unchanged, and where a phase-1 result bears on them it is written in section 11, "Cross-plan
> issues for the DRI". Docs only: no product code, no tests, no generated file touched, no model calls. Research and
> measurements:
> [docs/research/quantities.md](../research/quantities.md) (cited as R and a section number). This plan builds R6's
> recommendation: a pilot repair with the existing language, then two tracks, **A** (`cardinality@0`: counts,
> proportions, rounding) and **B** (`scales@0`: comparatives, equatives, graded words). Every number is measured (method
> in R2.1) or marked **estimate**. QT-0's statement spec is [quantities.md](quantities.md): it elaborates the Lean
> blocks of section 4 against `main` and lists every change its stub forced; where they differ, the spec's statement is
> the one under review. Its draft 2 passed the verification of the review's FIX (`manage-agents/quantities-p3ver1`);
> its draft 3 carries phase 1's results and changes no Lean statement.

**Changes in this draft (draft 4)**

1. **Phase-1 results recorded** (new section 0.1): QT-0p's bytes and probes PASS, measured on copies; its pilot re-run
   and its audit DEFERRED. QX-1, QX-2 and QX-3 DEFERRED: not executed (model calls; line "Experiment execution stays
   under its own authorisation"), and each pre-registration found incomplete. Every deferred item has a trigger
   (section 0.2). No bar was changed.
2. **QT-0p kept, rewritten to what was built** (section 4): the closure over Claude's types (P1 1.1, departure 2, kept
   on purpose), u097 on the translation's own `education_kind` predicates (departure 3), and the heading's claim
   without names (departure 1). Bytes: C +128 B and U +76 B, measured on copies, at the top of both estimated ranges.
   **Split**: the UDHR part applies at the next pilot run; the constitution part waits for a premise budget that can
   find its three-object model, or the DRI's acceptance of UNKNOWN (section 11, item 2), because "exactly three"
   turns the whole constitution's premise check from `model` to UNKNOWN.
3. **QX-1 changed before execution**: 42 items (six per word or form, as listed), so 1,680 calls, not 36 items and
   1,440; the sixth "most" point named (2 of 4); the unwritten contexts are a pre-execution step with its own review.
4. **QX-2 changed before execution**: the bar is unchanged and needs forms for at least five units, so decomposed
   forms are written for all six; four (u0165.s02, s03, s04, s06) are a pre-execution step. For its result to gate
   QT-B4, the comparator should be the form QT-B4 starts from, not today's; when QX-2 runs is a cross-plan question
   (section 11, item 1).
5. **QX-3 changed before execution**: item 1 leaves the scored twenty (its label holds only with the unproved
   bridge); item 2 states that no one voted both; the seventeen unwritten items (sixteen unstated, plus item 1's
   replacement) are a pre-execution step.
6. **QT-B4**: "826 B faithful" now says that the last two audits (runs 1800Z and 0600Z) rejected the current form of
   these units for its applicability guard, so it needs queue 4.4's repair as well as QX-2.
7. **Bytes** (sections 0, 7): QT-0p's figures are measured; the others stay estimates. Section 8 gains phase 1's
   risks.
8. **New section 11, "Cross-plan issues for the DRI"**: QX-2's timing against synthesis phase 1; the premise budget;
   the 0600Z audit's guard finding on the shared units u0165.s01–s07.

## 0. Summary

| # | Batch | Hours | Owner | Moves a pilot number? |
|---|---|---:|---|---|
| QT-0p | Pilot repair with the existing language (UDHR part now; constitution part after the premise budget) | 2 | pilot runner | yes: C +128 B, U +76 B claimed, **measured** on copies (P1 1.3); until audited |
| QT-0 | Statement spec, Lean stub, statement review | 3–4 | planner | no |
| QT-A1 | Lean core of `cardinality@0`: counts, regions, erasure, soundness (one soundness milestone with QT-A2) | 5–6 | Lean | no |
| QT-A2 | Lean: "rounds to" with a named tie rule (`VE.Numbers`) and "percent of"; after ME-1 | 3–4 | Lean | no |
| QT-A3 | Lean wire and service mode `cardinality` (registered through AR-10), shapes, documents, certificates | 5–6 | Lean | no |
| QT-A4 | Python relay, document hook, fuzz tests; move six test files to Lean; delete `ve/surface/count.py` | 6–7 (**estimate**) | Python | no |
| QT-A5 | News and paper measurement | 2–3 | pilot tooling | news 0–194 B |
| QT-E | Quantity English into Lean's engine (english-lean E3's quantities step) | 2 × 5–6 | english-lean owner | no |
| QT-A6 | Count, proportion and rounding wordings in Lean; refusals with rewrites | 4–5 | Lean | no (readability) |
| QT-A7 | Exact duration conversions through ME-6's `ve-units@2` (on trigger) | 4–5 | Lean, Python | no |
| QT-B1 | Lean core of `scales@0`: dimensions, graded words, premises, degrees | 5–6 | Lean | no |
| QT-B2 | Scale premises as PK-1's `scales` pack; layered-route kind `scales-coherence` | 5–6 | Lean, Python | no |
| QT-B3 | Scale and graded-word wordings in Lean; refusals | 4–5 | Lean | no |
| QT-B4 | Pilots: dial, trust levels, hard constraints, UDHR equalities | 3 | pilot tooling | C 0–781 B new, 826 B faithful (needs queue 4.4's repair and QX-2); U 0–191 B |
| QX-1 | Experiment: "most", "many", "multiple", bare "16 of the 18", bare "105 percent of" (42 items) | 2–3, plus writing the items | experiment runner | shapes rewrites and reading sets |
| QX-2 | Experiment: hard-constraint decomposition audit (four decomposed forms to write first) | 2, plus writing the forms | experiment runner | gates QT-B4's 826 B |
| QX-3 | Experiment: inferences with proportional grades (17 items to write first) | 2–3, plus writing the items | experiment runner | shapes rewrites |
| QX-4 | Research experiment: the 1,000-users passage | 4 | planner, Lean stub | research |
| QS-1 | Order closure over `VE.Closure` (standalone; before AT-1, QT-B1 and WG-2) | 3–4 | Lean (quantities) | no |

Order:
- QT-0p and QX-1 to QX-3 run now. Experiment execution stays under its own authorisation.
- QT-0 reviews QS-1's statements too. QS-1 then lands before AT-1, QT-B1 and WG-2.
- QT-A1 runs in parallel with the other plans' Lean cores. QT-A2 follows ME-1, still as one soundness milestone with
  QT-A1; then QT-A3, QT-A4 (six test files) and QT-A5.
- QT-B1 after QT-0's statement approval. QT-B2 after PK-1, AR-10's table, `lf-16e`, `lf-14d`, `rd-9-int` and the
  corrected coherence contract.
- QT-E before QT-A6 and QT-B3. QT-B4 waits for QX-2's audit and its slot in the hard-constraint queue.
- Landing preference: track A and QT-B1 land after attitudes and scope's SC-1/SC-2. QT-B2 lands after ET-4 in the
  integration order. QT-A7 follows ME-6.

Phase 1 (the first line above) has run as far as it can without model calls or edits to the pilots' own
translations; sections 0.1 and 0.2 give its results and what is left. The order above is unchanged.

### 0.1 Phase-1 results (2026-10-13, P1)

Every bar is quoted from draft 3 and was fixed before its result; none was changed after. "Measured on copies" means
rebuilt copies of the pilots' inputs from runs 20261012T1800Z and 20261013T0600Z, with `main` at `406736a4`.

| Item | Bar (draft 3) | Result | Verdict | What it gates |
|---|---|---|---|---|
| QT-0p bytes | "C 0–128 B, U 0–76 B, until audited" | C +128 B claimed (+113 CHECKED, +15 LABELLED; 2,951 B, 1.60%, to 3,079 B, 1.67%), the same on both runs; U +76 B OPEN, measured on part03 (whole declaration computed: 4,792 B, 43.90%, to 4,868 B, 44.60%) | **PASS**, on copies | the pilot numbers only; no batch waits for QT-0p |
| QT-0p probes | "fourth type of principal" SETTLED no; "higher education free" UNDECIDED | ALL on the negation, by certificate, on both runs; UNDECIDED (no rule) in the companion and in the rebuilt part | **PASS**, on copies | — |
| QT-0p re-run | "Done when both pilots re-run with the repair" | not done: the pilots' own translations are the pilot runner's | **DEFERRED** (0.2) | QT-0p's "done" |
| QT-0p audit | "… and the next audit samples the changed units" | not done: an independent audit is a model call | **DEFERRED** (0.2) | claimed bytes becoming audit-verified |
| QT-0p cost (not registered) | — | the whole constitution's premise check falls from `model` to UNKNOWN: "exactly three" needs three objects, and the check searches up to domain size 2. The repaired content has a Lean-checked model at size 3 | recorded; no pass or fail | the constitution part's application (0.2; section 11, item 2) |
| QX-1 | no numeric bar: the experiment "only shapes the rewrites and the members of each reading set" | not run. Audit: 42 items listed, 36 budgeted; "most" names five points for six contexts; 33 contexts unwritten; answer format and analysis unstated | **DEFERRED** (0.2) | the reading-set members of "most" and "multiple" (spec decision j, "pending"), and QT-A6's rewrites; never an authoring refusal |
| QX-2 | "faithful on at least 5 of 6 units, introduces no threshold on any, and is judged no worse than the current form on every unit" | not run. Audit: decomposed forms exist for 2 of 6 units (FB1, FB6); the current form was rejected by the audits of runs 1800Z and 0600Z, each time for its applicability guard, not its graded words | **DEFERRED** (0.2) | QT-B4's 826 B |
| QX-3 | no bar: "The answers shape rewrites only" | not run. Audit: 4 of 20 items stated; item 1's label "valid" needs the bridge the plan does not offer; item 2's "contradiction" needs "no one voted both"; items 3 and 4 confirmed | **DEFERRED** (0.2) | QT-A6's rewrites only |

Phase 1 cancels no batch and changes no Lean statement. It changes QT-0p (split, section 4), the three experiments'
material before execution (section 5) and one QT-B4 claim (section 4).

### 0.2 Deferred items and their triggers

| Item | Trigger | Then |
|---|---|---|
| QT-0p, UDHR part (u097) | the next UDHR pilot run (part03 is byte-identical in runs 1800Z and 0600Z) | the pilot runner applies `docs/research/evidence/quantities/qt0p/udhr-u097.ve.md`'s content, rebuilds part03 and the whole declaration, and records the measured bytes |
| QT-0p, constitution part (u0042.presupposition, u0043.s02) | a premise budget that finds a three-object model of one sort is on `main` (section 11, item 2), **or** the DRI accepts the constitution's premise check as UNKNOWN | the pilot runner first checks that the three units' spans and kinds are unchanged (as P1 1.2, step 3, did for run 0600Z), then applies the repair with `nd.py all` and records the bytes and the premise status |
| QT-0p audit | the first pilot audit after either part is in a pilot translation | it samples the changed units (u0042.presupposition, u0043.s02's CHECKED and LABELLED parts, u097); only then are the bytes audit-verified |
| QX-1 execution | the 42 items written and reviewed (section 5; still pre-registration, since no data exists), and execution authorised | run as pre-registered |
| QX-2 execution | the four missing decomposed forms written and reviewed (section 5); the comparator form fixed (section 11, item 1); execution authorised | run as pre-registered, bar unchanged |
| QX-3 execution | the twenty scored items written, each label re-derived under counting semantics, and reviewed; execution authorised | run as pre-registered |
| A premise budget for "exactly n" with n > 2 | the DRI assigns an owner (section 11, item 2) | it unblocks QT-0p's constitution part |
| News rows 7b and 22b (94 B) | the DRI's decision (section 8) | unchanged from draft 3 |

## 1. Scope, owners and rules

### 1.1 In scope, and what siblings own

In scope: counts over sorts declared finite; proportions with literal thresholds over a nonempty population ("more than
half", "at least 1 in 1,000"); "n of the m" beyond W6a's caps; exact rounding with a named tie rule and percent-of over
W6a quantities and counts; thousands separators; exact duration conversions through ME-6's `ve-units@2` (QT-A7);
comparatives, equatives and graded words on declared dimensions; the coherence of a decider's grade decisions;
refusals and rewrites for vague quantity words.

Not in scope, by owner: likelihood words and their order (**attitudes**, `VE.Attitudes.Scale`); ranks, the strength of
a priority step, delegated switches, "outweighs" (**weighing**); days, weeks as calendar units, months, time-indexed
values such as "the rate before the decision" (**events-time-causation**); act phrases such as "pay for work"
(**act-phrases**); which sentence a quantifier scopes over (**scope**); statistics, confidence intervals, real-valued
physics, exact rationals and the tie rules (`VE.Numbers`), the unit registry `ve-units@2` (**math-evidence**); the duty
in "has the right to equal pay" (**rights**, merged).

### 1.2 One owner per piece of logic

| Piece | Owner | This plan |
|---|---|---|
| Linear integer arithmetic and its certificates | `order@0` (`VE.Order.Tableau`: Farkas combinations, cuts) | reused through erasure; no second arithmetic checker |
| Unit tags, decimals, W6a typing, W6a certificates | `VE.Time.*` | reused unchanged; `cardinality@0` wraps W6a statements |
| W6a counting sugar ("at least 8") | `VE.Time.Count` (`atLeast`, `atMost`, `exactly`, `nOfM`; `expand_atLeast_iff`, `expand_exactly_iff`, `expand_atMost_iff`) | not duplicated: `count_atLeast_agree`, `count_atMost_agree` and `count_exactly_agree` prove the new count atoms agree with all three forms, and `count_nOfM_agree` follows from `exactly`; the Python copy `ve/surface/count.py` is deleted (QT-A4, after its six importing test files move to Lean's wire forms) |
| Counts and region arithmetic | **new** `VE.Cardinality` | one owner |
| Rounding and exact ratios | math-evidence's `VE.Numbers` (ME-1, core `Rat`) | QT-A2 proves `roundsTo_ratio_agree`; no second rounding definition |
| Unit declarations and conversions | ME-6's `ve-units@2` | QT-A7 declares `week` and `elapsed_day` in it; no `converts` of its own |
| Comparison, equatives, graded words, their premises | **new** `VE.Scales` | one owner; the grade order is a QS-1 `Order` |
| Order closure | QS-1 (quantities) over `VE.Closure` | `lean/VE/Closure/Order.lean`; no second `Reach` |
| Acyclicity of a declared order | `VE.Route.kahn`, `DagAcyclic` | reused for the grade order |
| Open-term records (`decided_by`, factors, precedents) | W2 schema ([document.md](document.md)) | graded words reference W2 records; no second record type |
| Extra base premises on norm routes | PK-1 packs (RD-9 composition owner) | quantities is the `scales` provider |
| Quantity English (reading, rendering, refusals) | Lean's English engine after english-lean E3; refusals and reading sets are rows of english-lean's catalogue | no new Python English; `ve/surface/time.py`'s parser and renderer leave with QT-E |
| Certificate search | untrusted: Python's existing `prove_quantity` on Lean's regenerated problem | no Python semantics; Lean checks every certificate and countermodel |
| Profile registration | AR-10's profile-gate table (generated Python data) | `cardinality@0` and `scales@0` are one row each, with their composition proofs |

### 1.3 Rules for every batch

- Lean-first gate: selected tests while iterating (`tools/select_tests.py --base $(git merge-base HEAD main) --run`);
  the full gate once, on the final committed HEAD; corpus A/B where an answer changes; a `DELTA.md` by class.
- `python3 lean/audit.py`: standard axioms only; no forbidden word even in comments; no primes in theorem names; names
  under about 57 characters. The Lean statements of section 4 are reviewed in QT-0; a statement that changes during a
  build reopens only that statement.
- Generated files are regenerated with `uv run python tools/regen_generated.py --write`, never edited or merged by
  hand; merges finish with `--resolve`. New trusted Lean lines need a signed allowance (`tools/trust_map.py --write
  --reason`, a person; the AR-4 ratchet) and a trust-cost line in ROADMAP (VISION's converged rule, item 4).
- Seeded bugs: before review, one planted bug per claimed behaviour in each changed language, a failing test shown,
  the bug restored, each recorded with file and test (named per batch below).
- Hermetic tests, no sleeps, `HANG_TIMEOUT` waits; every relayed answer typed and bound, with fuzz tests that retype
  and rebind each field; verdicts three-valued (exhaustion is UNKNOWN).

## 2. Track A design: `cardinality@0`

### 2.1 What a document can say

| English (one reading each) | Meaning |
|---|---|
| "There are finitely many FOMC policymakers." | a declaration, not a statement: the sort joins `finite_sorts`; the paraphrase shows it as an assumption ("The document assumes there are finitely many FOMC policymakers.") |
| "Exactly 16 of the 18 FOMC policymakers expect a further increase." | #policymakers = 18 and #(policymakers expecting a further increase) = 16 |
| "At least 16 of the 18 FOMC policymakers …" / "At most 2 of the 18 …" | ≥ / ≤ instead of = for the second count |
| "More than half of the users are curious." | #users > 0 and 2 × #(curious users) > #users; the paraphrase says there is at least one user |
| "At least 1 in 1,000 of the users intend harm." | #users > 0 and 1,000 × #(users intending harm) ≥ #users; the paraphrase says there is at least one user |
| "The number of scored decisions that are false approvals, divided by the number of scored decisions, rounds to 0.296, rounded to the nearest thousandth with exact ties going up." | d > 0 and `VE.Numbers.RoundsTo .tiesUp ⟨296, 3⟩ (f / d)`, with f the number of scored decisions that are false approvals and d the number of scored decisions, that is (2 × 296 − 1) × d ≤ 2,000 × f < (2 × 296 + 1) × d; the operands are counts or quantities (`CTerm`), each rendered with its whole body; "… with exact ties going to the even digit" is `.halfEven`; the paraphrase says "a value exactly halfway rounds up, to the larger number" |
| "The September estimate is exactly 105 percent of the June estimate." / "… is exactly 5 percent more than …" (the second only for operands whose unit is not declared with `display: percent`) | 100 × sept = 105 × june, june > 0 (same unit tag) |
| "The September estimate is 105 percent of the June estimate, to the nearest percent with exact ties going up." | june > 0 and `VE.Numbers.RoundsTo .tiesUp ⟨105, 0⟩ (100 × sept / june)`; the paraphrase says "rounds up, to the larger number" |
| "GBP 35,000.00", "1,000 users" | thousands separators accepted on input, in groups of exactly three digits ("1,00" is refused) |

Refused, with rewrites (authoring): "most" (rewrite "more than half") and "multiple" (rewrite "at least two"), always,
whatever QX-1 finds; "many", "few", "several", "a lot of"; bare "16 of the 18" (rewrite with "exactly" or "at least");
bare "105 percent of" (rewrites "exactly 105 percent of" and "105 percent of, to the nearest percent" with a tie rule);
"rounds to" with no tie rule (one rewrite per rule); "about"; "out of" between counts (rewrites with "divided by" for
each reading); "N percent more/less than" when the operands' unit is declared with `display: percent` (rewrites
"exactly 105 percent of" and W6a's "… minus … equals 5 percentage points"). In translation, a bare "16 of the 18"
becomes a reading set {exactly, at least} with a distinguishing model; a bare "105 percent of" a reading set {exact,
rounded}; a "rounds to" whose source states no rule a reading set over the rules; "N percent more than" on
percent-displayed operands a reading set {relative, percentage points}; "most" and "multiple" reading sets whose
members QX-1 shapes.

Which route a count takes is decided in English only (spec 7.1): over a sort declared finite, counts are cardinality
count atoms; over a sort not declared finite, "at least / at most / exactly N" and "n of the m" use W6a's counting
sugar within its caps, and beyond the caps, and for proportions and count operands, the sentence is refused with a
rewrite that adds the declaration sentence. No declaration is added silently; on the wire a count over a sort not
declared finite is still `CardinalityNotFinite`.

### 2.2 Environment and wire

- **Environment extension** (identity-bound, Lean-decoded only): `"cardinality_schema": "ve-cardinality@1"` and
  `"cardinality": {"finite_sorts": ["fomc_policymaker", …]}` beside W6a's `unit_schema`/`units` (both required; empty
  `units` allowed). Profiles: `cardinality@0` with `order@0`, `relational-fol@0`, `time@0`, and `documents@1` for
  documents. A declared finite sort restricts admissible structures to finitely many objects of that sort; this is a
  declared assumption, written "There are finitely many FOMC policymakers." and shown in the paraphrase ("The document
  assumes there are finitely many FOMC policymakers."). The W6a part is decoded by W6a's own decoder on a projection
  that removes both cardinality fields and removes `cardinality@0` from `profiles` (W6a's decoder accepts only its own
  two profile lists).
- **Statement**: `{"cardinality": {"format": "ve-cardinality@1", "formula": F}}`, with
  `["quantity", S]` (a W6a `ve-quantity@1` tree, unchanged), `["count", sort, [[k, body], …], rel, bound]` (`rel` is
  `lt`, `le` or `eq`; `k`, `bound` canonical integer strings), `["rounds_to", rule, num, den, "0.296"]` (the decimal's
  written places are kept: "0.30" and "0.3" are different claims; `rule` names a `VE.Numbers` tie rule),
  `["percent_of", part, whole, "105"]` (exact) and its rounded form with a rule, and `not`, `and`, `or`, `implies`.
  Ratio operands are typed terms `CTerm := quantity QTerm | count sort body`, so a ratio can take counts. Bodies:
  `["is", p]`, `["any"]`, `["not", b]`, `["and", b, b]`, `["or", b, b]`.
- **Identity**: the original environment's identity and the projection's W6a identities are computed separately and
  never substituted for each other. The `meaning_id` is over the whole canonical `ve-cardinality@1` object in the
  cardinality environment's domain; the regenerated W6a problem keeps its own W6a identities; reports carry and bind
  both, as W6a binds annotated and erased identities. Region constants never appear on the wire as input.

### 2.3 Meaning and erasure

A count atom means `Σ kᵢ × (number of objects of the sort with bodyᵢ) rel bound`, where a number of objects is the
length of a duplicate-free list of exactly those objects (as W6a's `expand_atLeast_iff` counts; counts stay integers;
exact ratios use core `Rat` through `VE.Numbers`). Every proportion requires a nonempty population, as "rounds to"
requires d > 0. Region constants are fresh: `CEnv.WellFormed` (finite sorts declared, no declared symbol with the
region prefix) is established by the decoder and is a hypothesis of `withRegions_admissible`, `erase_iff`,
`cardinality_elab_sound` and `refutesC_sound`.
Lean **erases** a problem (premises and conclusion together) into W6a: for each counted sort it lists the unary
predicates the problem's counts and universal statements mention on that sort (at most 6), makes one dimensionless
integer constant per region (each combination of true and false for those predicates: at most 64), replaces each
count by the sum of its regions' constants, replaces a universal statement over a counted sort whose body is a Boolean
combination of those predicates ("every policymaker expects a further increase or expects rates to stay") by "the
regions outside it sum to 0", writes `0 ≤ n` for every region constant, and replaces the ratio operations by their
linear integer forms; a count operand of a ratio becomes its dimensionless region sum. The erased problem goes to
W6a's existing certificate route. Soundness (`cardinality_elab_sound`)
is proved by reading each region constant as the size of its region. Countermodels are finite models of the original
vocabulary; Lean computes the region sizes by enumeration and runs W6a's existing countermodel check.

### 2.4 Limits (static, checked first; Lean alone decides the limits and the diagnostic order; Python checks schema and request binding only)

At most 8 counted sorts, 6 predicates per counted sort (64 regions), 64 terms per count atom, 512 region constants per
problem; literals within W6a's 40-digit numeral limit; the erased problem within W6a's 10,000-node aggregate
(`quantityLimits`). Excess is `ResourceLimit` naming the bound, never a partial answer. Within one statement the
envelope and the source-size preflight come first; then one depth-first, left-to-right pass runs the remaining checks
in order at each node, with W6a's own order inside a W6a part (spec 4.2).

## 3. Track B design: `scales@0`

### 3.1 Declarations

A **dimension** names the compared sort, its comparative predicate ("gives more uplift than"), optionally an equative
predicate ("gives as much uplift as"), and whether "any two can be compared" (allowed only with an equative). It may
list **graded words**: unary predicates on the sort, each an existing W2 open term (its decider and factors stay in
the W2 record), each with a direction (upper: "serious", "the vast majority"; lower: "minor", "slight"), and pairs
"whatever is g is h" ("very serious" above "serious"). "A majority" is not a vague word, so it is not a graded word:
it is a proportion (track A); a bridge from "the vast majority" to "more than half" waits for a proved bridge from
scales to cardinality (QX-4's plan item). All predicates are
ordinary declared vocabulary with their verbalisations; the scale block only adds structure. The block is
identity-bound and Lean-decoded; whether it is an environment extension or a document block (as rights and soft norms
carry theirs) is fixed in QT-0.

### 3.2 Generated premises (labelled, universal, quantifier-free bodies)

1. Comparative irreflexive: no x gives more uplift than itself.
2. Comparative transitive.
3. With an equative: reflexive, symmetric, transitive; never both "as much as" and "more than"; the comparative is
   preserved by replacing either side with an equal.
4. With "any two can be compared": for any x, y, more(x, y) or more(y, x) or same(x, y).
5. Upper graded word closed upward: if y is g and x is more than y (or the same as y), x is g. Lower: downward.
6. "g above h": whatever is g is h.

Nothing else: no density, no end points unless declared as constants with facts, no threshold, no number.

### 3.3 Meaning

The premises hold exactly when each dimension has its **intended** meaning, stated directly (`Intended`); on a
comparable dimension, exactly when there is a degree map into a linearly ordered set that gives the comparative and
equative and makes each graded word a set closed in its direction (`intended_iff_degrees`, Kennedy's degrees and
Klein's relations agree). The premises never fix a graded word on any object (`grade_open`): the decider decides.

### 3.4 Use

- On norm routes, the premises enter as PK-1's `scales` pack (`decls := []`, `labelled := scalePremises D`), placed
  in X by PK-1's fixed order (after attitudes, before events), so a rule guard may use a graded word ("no response
  gives serious uplift to …") and the conflict, status and unspecified checks see the coherence. What is proved about
  adding the block is `scales_conflictFree_iff` and no more: when the block is well formed at `envAt (fill U) 0`, no
  guard, carve-out or definition of the filled document mentions a scale symbol, and no other extra premise in X does,
  the whole document is conflict-free with the scale premises exactly when it is without them. Nothing is claimed
  about any one rule's status, or about a document whose guards use a graded word.
- A **coherence check** of recorded decisions (the layered-route kind `scales-coherence`, run on the decoded
  `LayeredU` with the assembled X): given ground facts (grade decisions, recorded comparisons), Lean answers COHERENT
  with a finite model of the facts and X, checked by Lean; INCOHERENT with a refutation of the facts plus the
  generated premises, checked by Lean, listing the premise instances it uses; otherwise UNKNOWN. (A single failing
  instance is not enough: r1 > r2, r2 > r3, r3 > r1 is refuted only by two transitivity steps and irreflexivity
  together.)

## 4. Batches

Each batch lists: what it builds; new files; hand-written shared files; generated files (regenerated, never edited);
Lean statements (Lean batches); fixtures; deletions; seeded bugs; bytes (**estimates**); done when.

### QT-0p. Pilot repair with the existing language (pilot runner, 2 h)

No product code. Smallest step that moves a pilot number. Phase 1 wrote both parts, measured them on rebuilt copies of
the pilots' inputs (P1 1), and left their application to the pilot runner. The content is in
`docs/research/evidence/quantities/qt0p/` (`constitution-u0042-u0043.ve.md`, `udhr-u097.ve.md`), as phase 1 built it.

- **Constitution, u0042.presupposition (38 B) and u0043.s02 (90 B)**: "At the moment, Claude’s three types of
  principals are Anthropic, operators, and users." Content in `relational-fol@0`: a sort `principal_type`, constants
  `anthropic`, `operators`, `users`, a unary predicate `claude_principal_type` ("is one of Claude's types of
  principals"), the three facts, their pairwise distinctness, and the closure over Claude's types,
  `∀t:principal_type. claude_principal_type(t) → t = anthropic ∨ t = operators ∨ t = users`. "At the moment" (15 B)
  becomes a LABELLED part (MIXED unit) naming the document's present without a date; the other 75 B are CHECKED. Once
  `events@0` lands, "the date of this document" is events' anchor, the one indexical day; QT-0p adds no date and no
  second indexical. u0043.s01 is unchanged (UNFORMALISED, `counting`).
  - **The heading** (u0042.presupposition, "Claude’s three types of principals") presupposes only that Claude has
    exactly three types of principals: three pairwise different objects, each one of Claude's types, and every one
    of Claude's types among them. It names none of them; u0043.s02 does (P1 1.1, departure 1). CHECKED.
  - **The closure is over Claude's types, by decision** (P1 1.1, departure 2). Draft 3's closure,
    `∀t:principal_type. t = anthropic ∨ t = operators ∨ t = users`, would also say that no other kind of principal
    exists at all, which the source does not say. The registered probe is answered the same way under both, because
    it is about Claude's types; a probe about every principal type ("there is no principal type other than the
    three") is UNKNOWN under this closure (measured) and is not a claim of this repair.
- **UDHR, u097 (76 B)**: "Education shall be free, at least in the elementary and fundamental stages." A duty with no
  bearer, written as u098 is. Its guard is "elementary or fundamental", over the translation's own `education_kind`
  with its existing `is_elementary` and a new `is_fundamental` (P1 1.1, departure 3: one vocabulary with u098, and no
  assumption that the two stages differ, which the source does not state). Other stages fall to norm-defaults'
  `unspecified` completion: "the text does not say" for higher stages is exactly what "at least" leaves open. "Free"
  is the open term `free_education`, as "compulsory" is in u098, so the unit is OPEN, not CHECKED.
- **Probes added**: "Is there a fourth type of principal?" (SETTLED no, tested as ALL on the negation: on the readings
  route NONE means only "does not follow"); "Must higher education be free under this sentence?" (UNDECIDED).
  Companion documents cannot carry `readings@1` probes without a reading set, so the constitution's probes run on the
  full translation.
- **Measured** (P1 1.3, on copies; runs 1800Z and 0600Z alike): C +128 B claimed (+113 CHECKED, +15 LABELLED, −128 B
  UNFORMALISED); U +76 B OPEN on part03; both probes as registered. Phase-1 verdict: bytes and probes PASS; the
  re-run and the audit DEFERRED (section 0.2).
- **Cost** (measured, not foreseen in draft 3): with "exactly three" in the translation, the whole constitution's
  premise check is UNKNOWN instead of `model`. The check's search stops at domain size 2 (`ve/vacuity.py`,
  `premise_status`), and a model needs three principal types; at size 3 the search finds one, checked by Lean
  ({anthropic, operators, users}, each one of Claude's types). UDHR part03 keeps `model`. Three options were weighed:
  - Keep the repair and accept UNKNOWN: +128 B (0.07% of the constitution) for the loss of the one whole-document
    consistency result the pilot reports. Not chosen by this plan; the DRI may choose it (section 11, item 2).
  - Drop pairwise distinctness: the text would say "at most three", which the source does not say. Rejected.
  - A premise budget that finds the model: product code outside this plan (section 11, item 2). **Chosen as the
    trigger** for the constitution part.
- **Split.** The UDHR part applies at the next UDHR pilot run; it has no cost. The constitution part waits for its
  trigger (section 0.2). Each part is done when its pilot re-runs with it and the next audit samples its changed
  units.
- **Not done here**: news rows 7b and 22b (94 B) could be written in W6a today with named earlier values, but that
  reverses a converged W6 review ruling (units-schema 7.1, N07b, N22b); recorded as a DRI decision item, not done.
- QT-A1 is not needed for these units, and nothing here changes QT-A1.
- Bytes: C +128 B, U +76 B, claimed and measured on copies, until audited. Done when both pilots re-run with the
  repair and the next audit samples the changed units.

### QT-0. Statement spec, stub and review (planner, 3–4 h)

- `docs/spec/quantities.md`: sections 2 and 3 as a statement spec (definitions, wire, diagnostics in order, limits,
  wordings with one reading each, refusals with rewrites, fixtures), the Lean blocks of QT-A1, QT-A2, QT-B1 and QS-1
  verbatim, QX-1's result where it has landed (otherwise "pending" for the reading-set members of "most" and
  "multiple").
- `lean/SpecStubs_quantities.lean`, untracked: every definition with the bodies given here and every theorem as a
  `def … : Prop`, elaborated with `lake env lean` against a build of main; every failure fixed in the spec. The stub
  also computes the adversarial examples: a colliding region constant, the three-step cycle, an empty population, the
  1 out of 8 tie under each rule, and a duration-to-date cast.
- Decides: (a) a new mode `cardinality` (this plan's choice: `VE.Time.Wire.decodeEnvironment` rejects unknown
  fields, so the quantity runner's `Extension` hook cannot receive a cardinality environment) or another carrier;
  (b) the carrier of the scales block (section 3.1); (c) the profile name `cardinality@0` (not PLAN-EXPAND2's deferred
  evaluation-only `count@0`, which this replaces with a proof-carrying layer); (d) the tie rules QT-A2 admits, at
  least `tiesUp` and `halfEven`; (e) the `kind` of PK-1's `scales` pack, with its matching obligation; (f) whether the
  closed interval is kept as a separate approximation relation (QT-A2).
- Done when the stub elaborates, the spec is committed, and the review converges on PASS (checklist in section 9).
  Elaboration alone is not enough: the review is an adversarial statement review.

### QT-A1. Lean core of `cardinality@0` (Lean, 5–6 h)

New files: `lean/VE/Cardinality/{Syntax,Semantics,Regions,Erase,Theorems,Examples}.lean`, `lean/CARDINALITY.md`.
Hand-written shared: none. Generated: `lean/VE.lean`, `lean/VE/Audit.lean`, `lean/VE/Route/frozen-sources.sha256`,
`lean/axioms.txt`, `lean/statements.txt`, `lean/predicates.txt`, `lean/declarations.txt`, trust tables (signed).

```lean
import VE.Time.Semantics
import VE.Time.Count
import VE.Numbers        -- ME-1 (math-evidence); QT-A1 and QT-A2 complete as one milestone after it

namespace VE.Cardinality
open VE.Time (QEnv QTerm QFormula TStructure TEntails)
universe u v

/-! ## Syntax -/

/-- A property of one counted object: unary predicates of its sort with `not`, `and`, `or`; `any` is every object. -/
inductive Body where
  | atom (predicate : String)
  | any
  | not (body : Body)
  | and (left right : Body)
  | or (left right : Body)
  deriving DecidableEq, Repr

inductive Rel where
  | lt | le | eq
  deriving DecidableEq, Repr

/-- `Σ kᵢ · #{x of sort | bodyᵢ x}  rel  bound`. -/
structure CountAtom where
  sort : String
  terms : List (Int × Body)
  rel : Rel
  bound : Int
  deriving DecidableEq, Repr

/-- A ratio operand: a W6a quantity term, or the number of objects of a counted sort with a body (dimensionless). -/
inductive CTerm where
  | quantity (t : QTerm)
  | count (sort : String) (body : Body)
  deriving DecidableEq, Repr

/-- W6a statements, count atoms, the ratio operations with their tie rules (QT-A2 gives their erasure) and the
connectives. -/
inductive CFormula where
  | quantity (a : QFormula)
  | count (c : CountAtom)
  | roundsTo (r : VE.Numbers.Rounding) (num den : CTerm) (digits : Int) (places : Nat)
  | percentOf (part whole : CTerm) (digits : Int) (places : Nat)                              -- exactly
  | percentRoundsTo (r : VE.Numbers.Rounding) (part whole : CTerm) (digits : Int) (places : Nat)  -- to the nearest
  | not (a : CFormula)
  | and (a b : CFormula)
  | or (a b : CFormula)
  | implies (a b : CFormula)
  deriving DecidableEq, Repr

/-- W6a's environment and the sorts the document declares finite. -/
structure CEnv where
  q : QEnv
  finite : List String

/-- What the environment decoder establishes: finite sorts are declared, and no declared symbol begins with the
region prefix, so region constants are fresh. -/
structure CEnv.WellFormed (E : CEnv) : Prop where
  finiteDeclared : ∀ s ∈ E.finite, s ∈ E.q.sorts
  fresh : ∀ c τ, E.q.constants c = some τ → c.startsWith "cardinality__" = false

/-! ## Meaning, stated without erasure -/

def Body.holds {α : Type u} (T : TStructure α) (x : α) : Body → Prop
  | .atom p => T.relation p [.obj x]
  | .any => True
  | .not b => ¬ b.holds T x
  | .and a b => a.holds T x ∧ b.holds T x
  | .or a b => a.holds T x ∨ b.holds T x

/-- Exactly `n` objects of sort `s` have property `b`: a duplicate-free list of exactly those objects has length `n`
(counts are stated with lists, as `VE.Time.expand_atLeast_iff` states them; the Lean tree uses no library). -/
def HasCount {α : Type u} (T : TStructure α) (s : String) (b : Body) (n : Nat) : Prop :=
  ∃ xs : List α, xs.Nodup ∧ xs.length = n ∧ ∀ x, x ∈ xs ↔ T.objects s x ∧ b.holds T x

def Rel.holds : Rel → Int → Int → Prop
  | .lt, a, b => a < b
  | .le, a, b => a ≤ b
  | .eq, a, b => a = b

/-- `ns` lists, in order, the count of each term's body. -/
def Counts {α : Type u} (T : TStructure α) (s : String) : List (Int × Body) → List Nat → Prop
  | [], [] => True
  | kb :: rest, n :: ns => HasCount T s kb.2 n ∧ Counts T s rest ns
  | _, _ => False

/-- The counts of the atom's bodies exist and their weighted sum stands in `rel` to `bound`. -/
def CountAtom.holds {α : Type u} (T : TStructure α) (c : CountAtom) : Prop :=
  ∃ ns : List Nat, Counts T c.sort c.terms ns ∧
    c.rel.holds ((c.terms.zip ns).map (fun p => p.1.1 * (p.2 : Int))).sum c.bound

/-- The integer an operand denotes: a closed tagged term's coordinate, or a count of its sort with its body. -/
def intOf {α : Type u} (T : TStructure α) (t : CTerm) : Option Int

/-- Rounding is `VE.Numbers.RoundsTo` with the sentence's own tie rule; this plan has no rounding definition. -/
def CFormula.holds {α : Type u} (T : TStructure α) : CFormula → Prop
  | .quantity a => a.tdenote T []
  | .count c => c.holds T
  | .roundsTo r n d D k => ∃ a b, intOf T n = some a ∧ intOf T d = some b ∧ 0 < b ∧
      VE.Numbers.RoundsTo r ⟨D, k⟩ ((a : Rat) / b)
  | .percentOf p w D k => ∃ a b, intOf T p = some a ∧ intOf T w = some b ∧ 0 < b ∧ 100 * 10 ^ k * a = D * b
  | .percentRoundsTo r p w D k => ∃ a b, intOf T p = some a ∧ intOf T w = some b ∧ 0 < b ∧
      VE.Numbers.RoundsTo r ⟨D, k⟩ ((100 * a : Rat) / b)
  | .not a => ¬ a.holds T
  | .and a b => a.holds T ∧ b.holds T
  | .or a b => a.holds T ∨ b.holds T
  | .implies a b => a.holds T → b.holds T

/-- W6a-admissible, and every declared finite sort is listed by some finite list. -/
def Admissible {α : Type u} (E : CEnv) (T : TStructure α) : Prop :=
  T.Admissible E.q ∧ ∀ s ∈ E.finite, ∃ xs : List α, ∀ x, T.objects s x ↔ x ∈ xs

def CEntails (E : CEnv) (ps : List CFormula) (c : CFormula) : Prop :=
  ∀ (α : Type v) (T : TStructure α), Admissible E T → (∀ a ∈ ps, a.holds T) → c.holds T

/-! ## Admission -/

/-- Every atom of a body is a declared unary predicate of `s`. -/
def BodyTyped (E : CEnv) (s : String) : Body → Prop
  | .atom p => E.q.predicates p = some [.obj s]
  | .any => True
  | .not b => BodyTyped E s b
  | .and a b | .or a b => BodyTyped E s a ∧ BodyTyped E s b

/-- The tie rules QT-A2 admits; QT-0 lists them (at least `tiesUp` and `halfEven`). -/
def admittedRules : List VE.Numbers.Rounding

/-- A ratio operand's tag: a quantity's W6a tag, or `dimensionless` for a count over a declared finite sort with a
typed body. -/
inductive CTermTyped (E : CEnv) : CTerm → String → Prop
  | quantity {t g} : VE.Time.HasType E.q [] t (.qty g) → CTermTyped E (.quantity t) g
  | count {s b} : s ∈ E.finite → BodyTyped E s b → CTermTyped E (.count s b) VE.Time.dimensionless

/-- Independent admission: counts name a declared finite sort with typed bodies; ratio operands share one tag that
is not `day`, and a rounding names a rule QT-0 admits; W6a parts are W6a-admitted. (Freshness of region constants
is `CEnv.WellFormed`, which the environment decoder establishes.) -/
inductive Admitted (E : CEnv) : CFormula → Prop
  | quantity {a} : VE.Time.Admitted E.q [] a → Admitted E (.quantity a)
  | count {c} : c.sort ∈ E.finite → (∀ kb ∈ c.terms, BodyTyped E c.sort kb.2) → Admitted E (.count c)
  | roundsTo {r n d D k t} : r ∈ admittedRules → t ≠ VE.Time.dayTag → CTermTyped E n t →
      CTermTyped E d t → Admitted E (.roundsTo r n d D k)
  | percentOf {p w D k t} : t ≠ VE.Time.dayTag → CTermTyped E p t → CTermTyped E w t →
      Admitted E (.percentOf p w D k)
  | percentRoundsTo {r p w D k t} : r ∈ admittedRules → t ≠ VE.Time.dayTag → CTermTyped E p t →
      CTermTyped E w t → Admitted E (.percentRoundsTo r p w D k)
  | not {a} : Admitted E a → Admitted E (.not a)
  | and {a b} : Admitted E a → Admitted E b → Admitted E (.and a b)
  | or {a b} : Admitted E a → Admitted E b → Admitted E (.or a b)
  | implies {a b} : Admitted E a → Admitted E b → Admitted E (.implies a b)

def CFormula.admits (E : CEnv) : CFormula → Bool

theorem admits_sound (E : CEnv) (a : CFormula) (h : a.admits E = true) : Admitted E a
theorem admits_complete (E : CEnv) (a : CFormula) (h : Admitted E a) : a.admits E = true

/-! ## Regions and erasure -/

/-- The unary predicates the problem `fs` mentions on sort `s` (counts and recognised universal statements),
in first-use order. -/
def predsOn (fs : List CFormula) (s : String) : List String

/-- `∀x:s. b(x)` with `b` a Boolean combination of unary atoms on `x`, recognised on a W6a formula. -/
def everyBody? : QFormula → Option (String × Body)

/-- A region: one truth value per predicate of `predsOn fs s`; `regions n` lists all `2 ^ n` in binary order. -/
abbrev Region := List Bool
def regions : Nat → List Region
def Body.inRegion (ps : List String) (r : Region) : Body → Bool

/-- The dimensionless integer constant counting region `r` of sort `s`, `cardinality__<s>__<bits>`. -/
def regionConst (s : String) (r : Region) : String

/-- `E.q` plus one dimensionless integer constant per region of every counted sort. -/
def CEnv.elab (E : CEnv) (fs : List CFormula) : QEnv

/-- Counts become sums of region constants; recognised universal statements over a counted sort become
"the regions outside the body sum to 0"; ratios become their linear forms (QT-A2); the rest is unchanged. -/
def CFormula.erase (E : CEnv) (fs : List CFormula) : CFormula → QFormula

/-- One premise `0 ≤ n` per region constant. -/
def nonnegPremises (E : CEnv) (fs : List CFormula) : List QFormula

/-- The structure that reads every region constant as the number of objects in its region. -/
noncomputable def withRegions {α : Type u} (E : CEnv) (fs : List CFormula) (T : TStructure α) : TStructure α

/-! ## Theorems -/

/-- On an admissible structure every count over a declared finite sort exists and is unique, so a count atom and its
negation mean what they say. -/
theorem hasCount_exists_unique {α : Type u} (E : CEnv) (T : TStructure α) (hT : Admissible E T)
    (s : String) (hs : s ∈ E.finite) (b : Body) :
    ∃ n, HasCount T s b n ∧ ∀ m, HasCount T s b m → m = n

theorem withRegions_admissible {α : Type u} (E : CEnv) (hE : E.WellFormed) (fs : List CFormula)
    (T : TStructure α) (hT : Admissible E T) : (withRegions E fs T).Admissible (E.elab fs)

theorem nonneg_hold {α : Type u} (E : CEnv) (fs : List CFormula) (T : TStructure α) :
    ∀ a ∈ nonnegPremises E fs, a.tdenote (withRegions E fs T) []

/-- **Erasure is faithful**: on an admissible structure, a formula of the problem holds exactly when its erasure holds
where region constants are region sizes. -/
theorem erase_iff {α : Type u} (E : CEnv) (hE : E.WellFormed) (fs : List CFormula) (T : TStructure α)
    (hT : Admissible E T) (a : CFormula) (ha : Admitted E a) (hin : a ∈ fs) :
    a.holds T ↔ (a.erase E fs).tdenote (withRegions E fs T) []

/-- **Soundness**: W6a entailment of the erased problem, with the region premises, gives counting entailment. -/
theorem cardinality_elab_sound (E : CEnv) (hE : E.WellFormed) (ps : List CFormula) (c : CFormula)
    (hps : ∀ a ∈ ps, Admitted E a) (hc : Admitted E c)
    (h : TEntails.{v} (E.elab (c :: ps))
      (nonnegPremises E (c :: ps) ++ ps.map (CFormula.erase E (c :: ps)))
      (c.erase E (c :: ps))) :
    CEntails.{v} E ps c

/-! ## Agreement with W6a's counting sugar (all four forms; on the wire `n_of_m` means "exactly") -/

/-- "At least n" as a count atom: `-1 · #b ≤ -n`; "at most n": `#b ≤ n`; "exactly n": `#b = n`. -/
def atLeastAtom (s : String) (b : Body) (n : Nat) : CountAtom := ⟨s, [(-1, b)], .le, -(n : Int)⟩
def atMostAtom (s : String) (b : Body) (n : Nat) : CountAtom := ⟨s, [(1, b)], .le, n⟩
def exactlyAtom (s : String) (b : Body) (n : Nat) : CountAtom := ⟨s, [(1, b)], .eq, n⟩
/-- "Exactly n of the m": W6a's `nOfM`, exactly m selected and exactly n of them with the property. -/
def nOfMFormula (s : String) (n m : Nat) (sel prop : Body) : CFormula :=
  .and (.count (exactlyAtom s sel m)) (.count (exactlyAtom s (.and sel prop) n))

/-- The body as an order@0 formula on the counted variable (de Bruijn index 0). -/
def Body.toFormula : Body → VE.Order.Formula

/-- On a declared finite sort, a count atom and W6a's sugar say the same thing, so "at least 3", "at most 3" and
"exactly 3" each have one meaning on both routes. -/
theorem count_atLeast_agree {α : Type u} (E : CEnv) (T : TStructure α) (hT : Admissible E T)
    (s : String) (hs : s ∈ E.finite) (b : Body) (hb : BodyTyped E s b) (n : Nat) :
    (CFormula.count (atLeastAtom s b n)).holds T ↔ (VE.Time.atLeast s n b.toFormula).denote T.lower []
theorem count_atMost_agree {α : Type u} (E : CEnv) (T : TStructure α) (hT : Admissible E T)
    (s : String) (hs : s ∈ E.finite) (b : Body) (hb : BodyTyped E s b) (n : Nat) :
    (CFormula.count (atMostAtom s b n)).holds T ↔ (VE.Time.atMost s n b.toFormula).denote T.lower []
theorem count_exactly_agree {α : Type u} (E : CEnv) (T : TStructure α) (hT : Admissible E T)
    (s : String) (hs : s ∈ E.finite) (b : Body) (hb : BodyTyped E s b) (n : Nat) :
    (CFormula.count (exactlyAtom s b n)).holds T ↔ (VE.Time.exactly s n b.toFormula).denote T.lower []
/-- Follows from `count_exactly_agree`. -/
theorem count_nOfM_agree {α : Type u} (E : CEnv) (T : TStructure α) (hT : Admissible E T)
    (s : String) (hs : s ∈ E.finite) (sel prop : Body) (h₁ : BodyTyped E s sel) (h₂ : BodyTyped E s prop)
    (n m : Nat) :
    (nOfMFormula s n m sel prop).holds T ↔ (VE.Time.nOfM s n m sel.toFormula prop.toFormula).denote T.lower []

/-! ## Finite countermodels -/

/-- A finite model extended with each region constant's size, computed by enumerating its sorted domains. -/
def withRegionsFinite {α : Type} [DecidableEq α] (E : CEnv) (fs : List CFormula)
    (M : VE.Order.FiniteModel α) : VE.Order.FiniteModel α

/-- W6a's existing countermodel check on the erased problem over `withRegionsFinite`. -/
def refutesC {α : Type} [DecidableEq α] (E : CEnv) (ps : List CFormula) (c : CFormula)
    (M : VE.Order.FiniteModel α) : Bool

theorem refutesC_sound {α : Type} [DecidableEq α] (E : CEnv) (hE : E.WellFormed) (ps : List CFormula)
    (c : CFormula) (M : VE.Order.FiniteModel α) (hps : ∀ a ∈ ps, Admitted E a) (hc : Admitted E c)
    (h : refutesC E ps c M = true) : ¬ CEntails.{0} E ps c

end VE.Cardinality
```

Fixtures (`Examples.lean`, `#guard`):

- **FA1 (news S3, `s3_count`)**. Finite sort `fomc_policymaker`; predicates `expects_further_increase`,
  `expects_rates_to_stay`; premises: #any = 18, #increase = 16, #stay = 2, and "no policymaker expects both" (the
  translator's stated premise that the two expectations exclude each other). Conclusion "every one of the 18 expects
  a further increase or expects rates to stay": the erased problem has 4 regions and a Farkas certificate. Under the
  reading "at least 16" the conclusion still holds. **FA1b**: without the exclusion premise, the countermodel (one
  policymaker expects both, one neither) refutes it.
- **FA2 (agreement)**: `atLeastAtom`, `atMostAtom`, `exactlyAtom` and `nOfMFormula` against `VE.Time.atLeast`,
  `atMost`, `exactly` and `nOfM` on the units-schema 8 gate-4 models (six, seven and eight entities); the evaluation
  counts of the pinned W6a fixtures are unchanged.
- **FA3 (caps)**: "exactly 16 of the 18" is admitted here and still refused by W6a's sugar (`CountingBound`).
- **FA8 (hostile)**: a count over a sort not declared finite (`CardinalityNotFinite`); a body with a binary
  predicate; seven predicates on one sort (`ResourceLimit`); a vocabulary symbol beginning `cardinality__`; a body
  predicate of another sort.
- **Admission is preserved**: the spec's statement (3.6) adds `erasedProblem_admitted` (every formula of the erased
  problem is W6a-admitted in `E.elab`), proved here, with FA1's and FA4c's erased problems as its examples.

Seeded bug: `Body.inRegion` reads `not b` as `b`; FA1's certificate replay and FA1b's countermodel `#guard`s fail.
Bytes: 0. Done when `lake build`, `lean/audit.py` and the `#guard`s pass and `lean/statements.txt` shows additions only.

### QT-A2. Rounding and percent-of (Lean, 3–4 h)

New file: `lean/VE/Cardinality/Ratio.lean` (erasure cases of `roundsTo`, `percentOf` and `percentRoundsTo`,
completing `CFormula.erase`). Shared and generated files as QT-A1. Waits for ME-1 (`VE.Numbers`); with QT-A1 it is one
soundness milestone (`erase_iff` and `cardinality_elab_sound` cover the ratio constructors).

```lean
namespace VE.Cardinality

/-- The linear integer form handed to W6a: "a / b rounds to D / 10^k under rule r", for b > 0. -/
def erasedRounding (r : VE.Numbers.Rounding) (a b D : Int) (k : Nat) : Prop

/-- The erased inequalities mean exactly `VE.Numbers.RoundsTo` under the sentence's rule. -/
theorem roundsTo_ratio_agree (r : VE.Numbers.Rounding) (a b D : Int) (k : Nat) (hb : 0 < b) :
    erasedRounding r a b D k ↔ VE.Numbers.RoundsTo r ⟨D, (k : Int)⟩ ((a : Rat) / b)

end VE.Cardinality
```

`roundHalfUp` is no longer the meaning; it may stay as an executable helper, with a lemma equating it to the `tiesUp`
case. Closeness is ME's `roundsTo_close`. QT-0 lists the rules QT-A2 admits: at least `tiesUp` and `halfEven`. If
QT-0 keeps the closed interval `(2D−1)·b ≤ 2·10^k·a ≤ (2D+1)·b`, it is a separate approximation relation with its own
name and wording (for example "is 0.296 to three places") and its own fixtures; it is never the meaning of "rounds
to".

"a is exactly D / 10^k percent of b" means `100 · 10^k · a = D · b` and b > 0 by definition (reviewed in QT-0); its
erasure is the W6a equation `scale (100 · 10^k) a = scale D b` in the operands' tag, covered by `erase_iff`. "a is
D / 10^k percent of b, to the nearest …" uses `RoundsTo` with its stated rule in the same way. Every rounding sentence
names its tie rule, for example "… rounds to 0.296, rounded to the nearest thousandth with exact ties going up".
Fixtures (from VE's paper, `paper/sections/04-e1.md`): FA4 "176 out of 594 rounds to 0.296" true (591 × 594 = 351,054
≤ 352,000 < 352,242 = 593 × 594) and "rounds to 0.297" false; "52 out of 243 rounds to 0.214", "31 out of 243 rounds
to 0.128", and their difference "21 out of 243 rounds to 0.086" (41,553 ≤ 42,000 < 42,039); "0.30" against "0.3" (two
places against one: different claims); news FA5 "the September estimate divided by the June estimate rounds to
1.028" true (2,055 × 360 = 739,800 ≤ 740,000 < 740,520 = 2,057 × 360) and "about 103 percent" refused (no "about").
The tie fixture is one fixture per rule: "1 out of 8 rounds to 0.13" holds and "0.12" fails under `tiesUp`; the
reverse holds under `halfEven`. FA4d: with 3 unscored false approvals, "the number of scored decisions that are false approvals,
divided by the number of scored decisions" rounds to 0.296 while "the number of false approvals, divided by …" rounds
to 0.301 (the two readings "out of" allowed). FA4e: −1/2 rounds to 0, not −1, under `tiesUp`, for a ratio and a
percent ("to the larger number"). FA5b: on FA5's percent-displayed operands, "exactly 105 percent of" and "… minus …
equals 5 percentage points" separate at September 378 and 860 (June 360). Seeded bug: the upper bound erased with
`≤`; the `tiesUp` tie fixture "1 out of 8 rounds to 0.12" becomes true and its `#guard` fails. Bytes: 0 on the pilots;
VE's paper unmeasured.

### QT-A3. Wire and service mode `cardinality` (Lean, 5–6 h)

New files: `lean/VE/Cardinality/{Wire,Document,Run,Render}.lean`, `lean/ResponseShape/Schemas/Cardinality.lean`,
`lean/ResponseShape/Encoders/Cardinality.lean`.
Hand-written shared: `lean/VE/Service/Protocol.lean` (mode constructor, name, list entry, dispatch line, theorem
`runMode_cardinality`) and `ve/backends/service_schema.py` (`MODES`), both in the protocol queue in landing order; the
`cardinality@0` row of AR-10's profile-gate table, with its composition proof (Python data generated; no
`Dispatch.lean` profile row or gate-lemma edit, no `ve/profiles.py` row); the `cardinality` mode registers through
AR-10's mode registry and keeps the relayed-route recipe; `ve/assurance-manifest.json` (decoder pins, reviewed by
hand), `ROADMAP.md` (trust-cost line).
Generated: `ve/backends/lean_service_schema/cardinality.json`, `lean/ResponseShape.lean`,
`lean/ResponseShape/Audit.lean`, `lean/checkers.lock`, `docs/spec/assurance-manifest.md`,
`lean/VE/Route/examples/route-cases.json`, and QT-A1's list.

Case kinds: `admission` (typing, canonical `F`, the regenerated erased problem and its W6a identities, the region
table), `countermodel`, `certificate`, `document` (claim graph), `paraphrase` (Lean's English line for a canonical
statement, display-only until QT-A6 adds the parse-back check).

```lean
namespace VE.Cardinality

/-- An accepted certificate is a W6a certificate of the regenerated problem, bound to the cardinality identities. -/
theorem checkCertificate_sound {w : CardEnv} (ps : List (CAdmission w)) (c : CAdmission w)
    (cert : CardCertificate) (h : checkCertificate ps c cert = .ok true) :
    cert.environmentId = w.environmentId ∧ cert.premiseIds = ps.map (·.meaningId) ∧
      cert.conclusionId = c.meaningId ∧ CEntails.{v} w.env (ps.map (·.formula)) c.formula

/-- A Lean-admitted cardinality document's root holds wherever its leaves hold. -/
theorem admit_cardinality_report_sound (w : CardEnv) (d : Json) (res : CardReport)
    (h : admitDocument w d = .ok res) : res.Sound

end VE.Cardinality

namespace VE.Service
theorem runMode_cardinality (j : Json) :
    runMode .cardinality j = VE.Cardinality.Run.runCaseReported j := rfl
end VE.Service

namespace ResponseShape.Encoders.Cardinality
theorem runCaseReported_fits (j : Json) :
    ResponseShape.Fits ResponseShape.Schemas.Cardinality.row (VE.Cardinality.Run.runCaseReported j)
end ResponseShape.Encoders.Cardinality
```

(`CardEnv`, `CAdmission`, `CardCertificate`, `CardReport.Sound` and `admitDocument` are this batch's, following
`VE.Time.Wire.W6Env`, `Admission`, `W6Certificate` and `VE.Time.Document`; the decoder proves the decoded `CEnv` is
`WellFormed`; `ResponseShape.Fits` stands for the predicate the existing encoder theorems use, named in QT-0.)
The W6a part of the environment is decoded by `VE.Time.Wire.decodeEnvironment` on the spec's projection `projectW6`
(both cardinality fields and `cardinality@0` removed); `CardEnv.environmentId` is the original environment's identity
and `CardEnv.w6` carries the projection's W6a identities, bound separately.
Fixtures: FA1 and FA1b as route cases; the hostile set
of QT-A1 at the wire (each diagnostic in the order of section 2.4); a forged region table and a forged claimed erased
problem, both refused; FA11, a cardinality environment that decodes through the projection, and a certificate bound
to the wrong one of the two identities, refused; FA13, the competing-fault cases (one node with two faults, two
faulty nodes, an operand's fault before its node's tag mismatch). Seeded bug: the decoder accepts a count whose sort
is not in `finite_sorts`; the hostile route case fails. Bytes: 0.

### QT-A4. Python relay, document hook, fuzz tests (Python, 6–7 h, **estimate**)

New files: `ve/cardinality.py` (sends cases with `rows` from `ve/backends/relay.py`, binds every id, span, unit and
region name to the request; runs the existing `prove_quantity` search on Lean's regenerated problem and sends the
certificate back to Lean), `tests/test_cardinality_lean.py`, `tests/test_cardinality_answer.py` (fuzz: each member
dropped, emptied, retyped, duplicated, reordered, an index out of range, one and two faults at a time).
Hand-written shared: the document hook for `cardinality` content joins the document-mode queue after `lf-16g` (Lean's
`document` mode; `ve/document.py` while it exists), in landing order AT-3b, SC-1b, QT-A4, ET-5, WG-4, ME-10;
`tools/layer_policy.py` (one row); `tests/data/route-cases.jsonl` (recorded by `tests/route_case_recorder.py`,
append-only); the six test files that import `ve/surface/count.py`.
Generated: `.importlinter`, `tools/gate-collection.json`.
**Deleted**: `ve/surface/count.py` (92 lines, a Python copy of `VE.Time.Count`), after its six importing test files
move onto Lean's wire forms (Lean's existing `count` route case for the expansion): `tests/test_count_w6a.py`,
`tests/test_constitution_w6a_controls.py`, `tests/test_w6a_looprecheck1.py`, `tests/test_units_w6a.py`,
`tests/test_units_relay_w6a.py` and `tests/test_units_lean_w6a.py`.
Seeded bug: the binding check skips the region table; a fuzz mutant that renames a region is accepted and the test
fails. Bytes: 0.

### QT-A5. News and paper measurement (pilot tooling, 2–3 h)

- News: rebuild `usecases/news-article/news-w6a.ve.md`'s `s3_count` (194 B) as cardinality content with FA1's
  premises (the expectations stay attributed: each predicate's description says whose projection it reports, and
  the content enters the claim graph through `bridge:accepts(fomc, …)` as rows 13 and 15 do). In translation, "16 of
  the 18" is a reading set {exactly, at least}; FA1's conclusion is checked under both (`readings:…:all`).
  Refresh `coverage-w6a.md` and `coverage.json` from the run (row 8: NO → DIRECT for the count, the counted
  property REIFIED).
- VE's paper: a seeded sample of 20 of the 48 lines with ratios (seed `quantities-QT-A5`), each written as cardinality
  content by hand, checked, and reported as "n of 20 expressible"; no byte claim (the paper is not partitioned).
- Rounding in sources: QT-A5 keeps a source's stated tie convention, or reports the rounding as unresolved (a reading
  set over the rules); it never imposes one.
- Bytes: news 0–194 B (**estimate** until the run). Done when the measured partition is committed with its run.

### QT-E. Quantity English into Lean's engine (english-lean owner, two batches of 5–6 h)

This is english-lean-PLAN 2.5's quantities step of E3, owned by that plan; listed here because QT-A6 and QT-B3 need
it. QT-E gates QT-A6, ME-11 and QT-B3; it does not gate AT-5. Lexer terminal classes for ISO dates, `D Month YYYY`, decimals, labelled amounts, percentages and (new) thousands
separators; W6a's frames (comparisons, `within`, `shift`, `elapsed`, the percentage-point alias) as rules of the
engine with whole-sentence derivation uniqueness. **Deleted** by that step: `ve/surface/time.py`'s parser and
renderer (298 lines) and their two call sites in `ve/document.py` (`:145`, `:1549`), after a delta report on the W6
test corpora (`tests/test_time_surface_w6a.py` and the W6a regression files). Shared files: `lean/VE/EnglishGrammar/*`
(with act-phrases and attitudes), generated `lean/VE/EnglishGrammar/Fixed/*.lean`, `ve/english_grammar/LOCK.json`
(needs a person's `--actions-version`), `ve/english_grammar/codes.json`.

### QT-A6. Count, proportion and rounding wordings in Lean (Lean, 4–5 h)

In the serialised English queue on `lean/VE/EnglishGrammar/*`: AT-5 → QT-A6 → ME-11 → QT-B3 → SC-7; QT-E gates QT-A6,
ME-11 and QT-B3, not AT-5. Rules in the engine (new rule module files if E3's layer mechanism allows, else additive
lines): the wordings of section 2.1, including the sentence that declares a sort finite, rendering that parses back to
the same canonical `F` (the per-output check of english-lean 3.5), and the dispatch of counts by declared finiteness
(spec 7.1). QT-A6's refusals and translation reading sets are rows in english-lean's catalogue, with no
separate table: "most", "many", "few", "several", "a lot of" (and "multiple"); bare "16 of the 18"; bare "105 percent
of"; "rounds to" with no tie rule; "about"; "out of" between counts; "N percent more/less than" on percent-displayed
operands; a proportion, or a count beyond W6a's caps, over a sort not declared finite (the rewrite adds the
declaration). "About", "approximately", "roughly" and "nearly" form **one** catalogue
row shared with math-evidence: QT-A6 adds it, being earlier in the queue, and ME-11 reuses it. Fixtures: every wording
of 2.1 round-trips; FA6 "GBP 35,000.00" lowers to 3,500,000 `gbp_penny` (eligibility's probe P4 now accepted; W6a's
canonical rendering is unchanged, separators are an input alias in groups of exactly three digits, "1,00" refused);
FA7 bare "16 of the 18" refused with both rewrites; FA4d's and FA5b's wordings; FA4e, a tie-up paraphrase at a
negative half; FA12, the declaration's paraphrase and each dispatch case. Seeded bug: "at most n of the m" built as
"at least"; the round-trip fixture fails. Bytes: 0 (readability of QT-A5's content).

### QT-A7. Exact duration conversions through `ve-units@2` (Lean, Python, 4–5 h; on trigger)

Trigger: a pinned document needs a conversion (eligibility's "52 weeks" is the candidate). Waits for ME-6, which owns
`ve-units@2` (base dimensions, units with `base_exponents`, an exact positive `factor` to the coherent unit) and
`units_v1_conservative`; QT-A7 has no `"converts"` design and no `convert_iff`. On its trigger QT-A7 declares `week`
and `elapsed_day` as units of the time physical dimension with exact factors in ME-6's registry, and converts with
`VE.Calc.convert_by_factors`. It never converts into or out of `day`, W6a's calendar-date tag: durations use
`elapsed_day`, and a duration-to-date cast is refused. `ve-units@1` tags stay nominal. Currencies never convert.
Calendar months and years remain events-time-causation's. ("Dimension" in this plan is a comparison scale; ME's units
have a "physical dimension".) Bytes: 0 on the pilots.

### QT-B1. Lean core of `scales@0` (Lean, 5–6 h)

New files: `lean/VE/Scales/{Syntax,Premises,Intended,Degrees,Theorems,Examples}.lean`, `lean/SCALES.md`.
Hand-written shared: none. Generated: as QT-A1.

```lean
import VE.Semantics
import VE.Route.Route
import VE.Closure.Order   -- QS-1

namespace VE.Scales
universe u

inductive Direction where
  | upper
  | lower
  deriving DecidableEq, Repr

/-- A graded word: a unary predicate that is a W2 open term (decider and factors stay in the W2 record). -/
structure Grade where
  name : String
  direction : Direction
  deriving DecidableEq, Repr

/-- One dimension along which objects of one sort are compared. -/
structure Dimension where
  name : String
  sort : String
  more : String
  same : Option String
  comparable : Bool
  grades : List Grade
  above : List (String × String)
  deriving DecidableEq, Repr

structure ScaleDoc where
  dims : List Dimension
  deriving DecidableEq, Repr

/-- The grade order of a dimension is a QS-1 `Order` (no closure of this plan's own). -/
def gradeOrder (d : Dimension) : VE.Closure.Order String := ⟨d.grades.map (·.name), d.above⟩

/-- Predicates declared with the right signatures; grades are W2 open terms; one dimension per predicate; no two
premises share a label (so no two dimensions share a name and no `above` pair is repeated); `above` pairs within one
dimension and one direction, acyclic by `VE.Route.kahn`; `comparable` only with `same`. -/
def WellFormed (E : VE.Environment) (openTerms : List String) (D : ScaleDoc) : Bool

/-- Labelled premises of one dimension (section 3.2); every body is quantifier-free under universal binders. -/
def premises (d : Dimension) : List (String × VE.Formula)

def scalePremises (D : ScaleDoc) : List (String × VE.Formula) := D.dims.flatMap premises

/-- The meaning of a dimension in a structure, stated directly. -/
structure Intended (S : VE.Structure.{u}) (d : Dimension) : Prop where
  irrefl : ∀ x, S.domain d.sort x → ¬ S.relation d.more [x, x]
  trans : ∀ x y z, S.domain d.sort x → S.domain d.sort y → S.domain d.sort z →
    S.relation d.more [x, y] → S.relation d.more [y, z] → S.relation d.more [x, z]
  sameRefl : ∀ e, d.same = some e → ∀ x, S.domain d.sort x → S.relation e [x, x]
  sameSymm : ∀ e, d.same = some e → ∀ x y, S.relation e [x, y] → S.relation e [y, x]
  sameTrans : ∀ e, d.same = some e → ∀ x y z,
    S.relation e [x, y] → S.relation e [y, z] → S.relation e [x, z]
  sameNotMore : ∀ e, d.same = some e → ∀ x y, S.relation e [x, y] → ¬ S.relation d.more [x, y]
  sameLeft : ∀ e, d.same = some e → ∀ x y z,
    S.relation e [x, y] → S.relation d.more [y, z] → S.relation d.more [x, z]
  sameRight : ∀ e, d.same = some e → ∀ x y z,
    S.relation d.more [x, y] → S.relation e [y, z] → S.relation d.more [x, z]
  total : d.comparable = true → ∀ e, d.same = some e → ∀ x y, S.domain d.sort x → S.domain d.sort y →
    S.relation d.more [x, y] ∨ S.relation d.more [y, x] ∨ S.relation e [x, y]
  closed : ∀ g ∈ d.grades, ∀ x y, S.relation g.name [y] →
    (g.direction = .upper → S.relation d.more [x, y] → S.relation g.name [x]) ∧
    (g.direction = .lower → S.relation d.more [y, x] → S.relation g.name [x]) ∧
    (∀ e, d.same = some e → S.relation e [x, y] → S.relation g.name [x])
  aboveImp : ∀ p ∈ d.above, ∀ x, S.relation p.1 [x] → S.relation p.2 [x]

/-- No generated symbol of `D` occurs in `a`. -/
def Fresh (D : ScaleDoc) (a : VE.Formula) : Prop

/-- The environment `E` as `D` declares it (no new symbol: the predicates are `E`'s). -/
def envScales (E : VE.Environment) (D : ScaleDoc) : VE.Environment

/-- **Faithful**: the premises hold exactly when every dimension has its intended meaning. -/
theorem premises_iff_intended (E : VE.Environment) (ots : List String) (D : ScaleDoc)
    (hD : WellFormed E ots D = true) (S : VE.Structure.{u}) (hS : S.Admissible E) :
    (∀ a ∈ (scalePremises D).map (·.2), a.denote S []) ↔ ∀ d ∈ D.dims, Intended S d

/-- A strict linear order, stated directly (the Lean tree uses no library). -/
structure StrictLinear {L : Type u} (lt : L → L → Prop) : Prop where
  irrefl : ∀ a, ¬ lt a a
  trans : ∀ a b c, lt a b → lt b c → lt a c
  connex : ∀ a b, lt a b ∨ a = b ∨ lt b a

/-- **Degrees**: on a comparable dimension the intended meaning is a degree map into a strict linear order, with each
graded word closed in its direction (Kennedy's degrees and Klein's relations agree). The degrees are the classes of
"as much as", built with `Quotient`. -/
theorem intended_iff_degrees (S : VE.Structure.{u}) (d : Dimension) (e : String)
    (hc : d.comparable = true) (he : d.same = some e)
    (htyped : ∀ x y, S.relation d.more [x, y] ∨ S.relation e [x, y] → S.domain d.sort x ∧ S.domain d.sort y) :
    Intended S d ↔ ∃ (L : Type u) (lt : L → L → Prop) (_ : StrictLinear lt) (deg : S.Carrier → L),
      (∀ x y, S.domain d.sort x → S.domain d.sort y →
        (S.relation d.more [x, y] ↔ lt (deg y) (deg x)) ∧ (S.relation e [x, y] ↔ deg x = deg y)) ∧
      (∀ g ∈ d.grades, ∀ x y, S.domain d.sort x → S.domain d.sort y → S.relation g.name [y] →
        (g.direction = .upper → ¬ lt (deg x) (deg y) → S.relation g.name [x]) ∧
        (g.direction = .lower → ¬ lt (deg y) (deg x) → S.relation g.name [x])) ∧
      (∀ p ∈ d.above, ∀ x, S.relation p.1 [x] → S.relation p.2 [x])

/-- **Conservative**: formulas without scale structure have the same consequences with the scale premises. -/
theorem scales_conservative (E : VE.Environment) (ots : List String) (D : ScaleDoc)
    (hD : WellFormed E ots D = true) (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, Fresh D a) (hφ : Fresh D φ) :
    VE.Entails.{u} (envScales E D) (Γ ++ (scalePremises D).map (·.2)) φ ↔ VE.Entails.{u} E Γ φ

/-- **No threshold is chosen**: for each graded word, the premises alone have a model where an object has it and one
where it does not. -/
theorem grade_open (E : VE.Environment) (ots : List String) (D : ScaleDoc) (hD : WellFormed E ots D = true)
    (d : Dimension) (hd : d ∈ D.dims) (g : Grade) (hg : g ∈ d.grades) :
    (∃ S : VE.Structure.{0}, S.Admissible (envScales E D) ∧
      (∀ a ∈ (scalePremises D).map (·.2), a.denote S []) ∧ ∃ x, S.domain d.sort x ∧ S.relation g.name [x]) ∧
    (∃ S : VE.Structure.{0}, S.Admissible (envScales E D) ∧
      (∀ a ∈ (scalePremises D).map (·.2), a.denote S []) ∧ ∃ x, S.domain d.sort x ∧ ¬ S.relation g.name [x])

/-- The premises are well typed in the declared environment; at `E := envAt (fill U) 0` this is the typing
obligation of PK-1's `scales` pack (QT-B2). -/
theorem premises_wellTyped (E : VE.Environment) (ots : List String) (D : ScaleDoc) (hD : WellFormed E ots D = true) :
    ∀ a ∈ (scalePremises D).map (·.2), a.WellFormed E []

/-- **One premise per label**: a reported label or instance, and its `origins` entry, names one premise. -/
theorem scalePremises_labels_nodup (E : VE.Environment) (ots : List String) (D : ScaleDoc)
    (hD : WellFormed E ots D = true) : ((scalePremises D).map (·.1)).Nodup

end VE.Scales
```

(`Fresh`'s symbols are the dimension's comparative, equative and graded predicates; `scales_conservative` reads them
as symbols whose meaning the old document did not constrain.) Fixtures (`Examples.lean`):

- **FB1 (u0165.s01)**: dimension `uplift` on sort `response`, grade `gives_serious_uplift` (upper, W2 open term
  `serious_uplift` with factor "what counts as serious uplift"). Decisions "r1 gives serious uplift", "r2 gives more
  uplift than r1", "r2 does not give serious uplift": refuted, the failing premise being upward closure.
- **FB2 (u0226.s01, s02)**: dimension `autonomy` on sort `disposition` with constants `fully_corrigible` and
  `fully_autonomous`, the facts that every other disposition lies strictly between them, and the endpoint premise
  "Fully autonomous is more autonomous than fully corrigible."; "a disposition more autonomous than fully autonomous"
  is refuted. Without the endpoint premise it is not: with no other disposition, fully corrigible may be above fully
  autonomous (that countermodel stays a fixture). QT-B4 must justify the premise from u0226's text.
- **FB3 (u0043.s01)**: dimension `trust` on `principal_type`; "different levels of trust" as a reading set {not all
  the same; pairwise different}, with a distinguishing model.
- **FB4 (UDHR u094)**: dimension `social_protection` on `child` with `same`; "all children enjoy the same social
  protection" as `∀c₁ c₂. same(c₁, c₂)` (the duty form is rights').
- **FB6 (u0165.s05)**: dimension `share_of_humanity_targeted` on `attempt`, grade `vast_majority` (upper, an open
  term); u0165.s05 says only "vast majority". "A majority" is not a vague word, so it is not a graded word. "The vast
  majority implies more than half" waits for a proved bridge from scales to cardinality (QX-4's plan item); no
  fidelity credit is claimed for it.
- **FB8 (hostile)**: a comparative on an undeclared dimension; an `above` cycle (`ScaleCycle`, from `VE.Route.kahn`'s
  diagnostic); `above` across directions; `comparable` without `same`; a graded word that is not a W2 open term; two
  dimensions with one name; a repeated `above` pair (both rejected for duplicate labels, not deduplicated).

Seeded bug: the lower-direction closure generated with the comparative reversed; FB1's lower twin (a "minor harm"
fixture) is accepted wrongly and its `#guard` fails. Bytes: 0.

### QT-B2. Scale premises as PK-1's `scales` pack; layered-route kind `scales-coherence` (Lean, Python, 5–6 h)

Needs PK-1 and AR-10's profile-gate table, in addition to `lf-16e`, `lf-14d` and `rd-9-int` merged. It lands last in
the integration order on `Layered.lean` (AT-2/AT-3a → WG-3 → ET-4 → QT-B2); its position inside X is PK-1's fixed
order: after attitudes, before events. New files: `lean/VE/Scales/{Wire,Coherence}.lean`, `ve/scales.py`,
`tests/test_scales_lean.py`, `tests/test_scales_answer.py`. QT-B2 registers PK-1's `scales` pack:
- `decls := []`, since the block adds no symbol;
- `labelled := scalePremises D`;
- `origins`: each label ↦ its request path;
- its `kind` is declared in QT-0 with the matching obligation. No conservativity claim for a combination goes beyond
  what `scales_conservative` states.

The pack's typing obligation is `premises_wellTyped` at `envAt (fill U) 0`:
`∀ a ∈ (scalePremises D).map (·.2), a.WellFormed (envAt (fill U) 0) []`. On the readings route, QT-B2 proves its own
`Transfers`, and PK-1's `transfers_append` combines the packs. The `coherence` case is the layered-route kind
`scales-coherence`, run on the decoded `LayeredU` with the assembled X; its shape goes into the layered route's
response-shape files. `scales@0` is one row of AR-10's profile-gate table, with its composition proof. Hand-written
shared: `Layered.lean` (one provider line, in integration order), the layered route's response-shape files,
`ve/assurance-manifest.json`, `ROADMAP.md`; the document hook as in QT-A4. There is no `scales` mode: no
`Protocol.lean` constructor, no `runMode_scales`, no `service_schema.py` entry and no generated `scales.json`.
Generated: as QT-A1, plus the layered route's regenerated schema.

```lean
namespace VE.Scales

/-- With no guard and no other extra premise mentioning scale structure, conflict-freedom is unchanged. -/
theorem scales_conflictFree_iff (U : VE.NormDefaults.UDoc) (X : List VE.Formula) (ots : List String)
    (D : ScaleDoc) (hD : WellFormed (VE.Norms.envAt (VE.NormDefaults.fill U) 0) ots D = true)
    (hguards : GuardsFresh U D) (hX : ∀ a ∈ X, Fresh D a) :
    VE.NormDefaults.Wire.ConflictFreeX.{u} U X ↔
      VE.NormDefaults.Wire.ConflictFreeX.{u} U (X ++ (scalePremises D).map (·.2))

/-- A coherence answer is sound: INCOHERENT carries a refutation of the facts plus the generated premises, checked by
Lean, and lists the premise instances it uses; COHERENT carries a finite model of the facts and X, checked by Lean;
a search that finds neither returns UNKNOWN. -/
theorem coherence_sound (E : VE.Environment) (X : List (String × VE.Formula)) (facts : List VE.Formula)
    (r : CoherenceResult) (h : checkCoherence E X facts = .ok r) : r.Sound E X facts

end VE.Scales
```

(`GuardsFresh`, `CoherenceResult.Sound` and `checkCoherence` are this batch's; the spec, 6.3, gives their statements.
`scales_conflictFree_iff` is stated at `envAt (fill U) 0`, the environment of the pack's typing obligation.) By
`scalePremises_labels_nodup`, each label in `origins` and in a reported instance names one premise. Fixtures: FB1 as
a coherence case; the three-step cycle r1 > r2, r2 > r3, r3 > r1 (no single premise instance is false in every model
of the facts; the refutation uses two transitivity instances and irreflexivity); `scales_conflictFree_iff` with a
nonempty block and every hypothesis holding, conflict-free with and without it (FB9) and conflicting with and without
it (FB10); and, as a separate regression, the constitution's main document with an empty scales block, whose carried
probes stay byte-identical (FB7). Seeded bugs: Lean, the block's premises dropped on one reading choice (an
enumerated fixture fails); Python, the binding check skips an instance's label (a fuzz mutant passes and the test
fails). Bytes: 0.

### QT-B3. Scale and graded-word wordings in Lean (Lean, 4–5 h)

After QT-B2, in the serialised English queue AT-5 → QT-A6 → ME-11 → QT-B3 → SC-7; QT-E gates it (QT-B3 may instead
follow english-lean E3's norm step). Its refusals are rows in english-lean's catalogue. Declarations: "Responses are compared by uplift: one response
gives more uplift than another." "Two responses can give equal uplift." "Any two responses can be compared by
uplift." "Serious uplift is a degree of uplift decided by …" "Very serious uplift is serious uplift." Uses: "Response
A gives more uplift than response B." "Response A gives serious uplift." "Act A is more harmful than act B." "A is
paid as much as B." Refusals with rewrites: a comparative or "very X" on an undeclared dimension ("Declare it first:
'Acts are compared by harm: …'"), "more X than" across two dimensions, "substantially more" (a grade of a difference:
research, R5.2). Fixtures: each wording round-trips; each refusal names its rewrite. Seeded bug: "less X than" read as
"more X than"; the round-trip fixture fails. Bytes: 0.

### QT-B4. Pilots (pilot tooling, 3 h)

- FB2's endpoint premise ("Fully autonomous is more autonomous than fully corrigible.") is used only with u0226.s01's
  own words for it ("a disposition dial that goes from fully corrigible … to fully autonomous"), accepted by the
  audit; otherwise FB2's refutation is not claimed.
- Constitution companion, then main document: FB2 (dial, u0226.s01 and s02, 680 B), FB3 (u0043.s01, 101 B), FB1 and
  FB6 for the hard constraints u0165.s01 to s06 (826 B, already OPEN) only if QX-2 passes. QT-B4's edits to
  u0165.s01–s06 sit in the hard-constraint queue: they come after AT-0p → SC-1b → SC-2 → AT-6a/AT-6b → WG-5, then run
  one at a time with WG-8, whichever is ready first. QT-B4 still also waits for QT-B2 and QX-2, and starts from the
  translation as the previous step left it.
- UDHR companion probe: FB4 (u094, 90 B), u093 ("special care", 73 B) and u031 ("equal before the law", 28 B) with the
  rights route.
- Measure: claimed and audit-verified bytes, the residual (each graded word is an open term in it), and the carried
  probes. Bytes: C 0–781 B newly claimed; 826 B faithful (audit-verifiable after the next audit); U 0–191 B
  (**estimates**).
- The current form of u0165.s01–s06 was rejected by the last two pilot audits (P1 3), each time for its applicability
  guard, not its graded words: run 1800Z's guard lost the mistaken-but-confident cases; run 0600Z's repaired guard
  binds only `situation`, not the regulated Claude instance. So "826 B faithful" needs both queue 4.4's repair of the
  guards and QX-2's pass on the graded words; neither alone is enough. FB1 and FB6 (QT-B1) are unaffected.

### QS-1. Order closure over `VE.Closure` (Lean, quantities, 3–4 h)

Quantities' standalone batch. Its statements are reviewed in QT-0. It lands **before AT-1, QT-B1 and WG-2**. There is
no new algorithm and no second `Reach` definition: the implementation is `VE.Closure` on `main`
(`lean/VE/Closure/Paths.lean`: `Path`, `Reachable .plus/.star`, the deduplicated Warshall closure, `reachEval`,
`reachEval_iff`). In a new file `lean/VE/Closure/Order.lean`, with `Paths.lean` unchanged, QS-1 delivers:

```lean
structure Order (α : Type) where
  elems : List α
  edges : List (α × α)
structure Caps where
  elems : Nat
  edges : Nat
def Order.admit   [DecidableEq α] (c : Caps) (o : Order α) : Except String Unit   -- ResourceLimit
def Order.above   [DecidableEq α] (o : Order α) (a b : α) : Bool := reachEval .plus o.edges a b
def Order.atLeast [DecidableEq α] (o : Order α) (a b : α) : Bool := reachEval .star o.edges a b
theorem path_iff_transGen : Path R a b ↔ Relation.TransGen R a b
theorem reachable_star_iff : Reachable .star R a b ↔ a = b ∨ Relation.TransGen R a b
theorem atLeast_refl ; theorem atLeast_trans ; theorem above_iff ; theorem atLeast_iff
theorem outranksPlus_eq_above   -- VE.SoftNorms.outranksPlus agrees with `above` (soft file unedited)
theorem risk_closure_eq         -- VE.Risk.closure agrees likewise (risk file unedited)
```

- `Relation.ReflTransGen` does not exist in the pinned Lean v4.24.0 core, and VE has no Mathlib. Reflexive agreement
  is therefore stated as `a = b ∨ Relation.TransGen`.
- Acyclicity stays `VE.Route.kahn`.
- Each consumer keeps its own meaning: attitudes, the likelihood table and its gating; weighing, a strict pair needs
  a chain containing an `always` edge; QT-B1, the grade order is a QS-1 `Order`.
- Cardinality, ordinal grades and physical dimensions stay distinct: QS-1 is an order closure only, with no numbers
  and no units.

## 5. Experiments (pre-registered)

Readers for QX-1 and QX-3: Sonnet 5.5 as human proxy (`claude-sonnet-5-5`), 40 independent sessions with no shared
context, items in a seeded random order. This measures agreement among proxy readers, not truth and not human
readers. No experiment has been executed for this plan: phase 1 audited the three pre-registrations without model
calls (P1 2–4; `docs/research/evidence/quantities/qx/prereg-audit.json`) and found each incomplete. The material each
still needs is listed below as a pre-execution step; writing it is still pre-registration, because no data exists,
and each step is reviewed before execution. No bar changes. Experiments cannot select a meaning by vote: they improve
explicit rewrites and identify translation alternatives. Experiment execution stays under its own authorisation.

### QX-1. "most", "many", "multiple", bare "16 of the 18", bare "105 percent of" (2–3 h)

Seed `quantities-QX1`. Items: for "most", six neutral contexts ("Of the 100 members, 51 voted yes. Is it true that
most members voted yes?") at 50, 51, 60 and 95 of 100, at 3 of 5 and at 2 of 4; for "many", "few" and "several", six contexts
each that separate the cardinal from the proportional reading (Partee); for "multiple", six contexts at 1 and 2; for
bare "16 of the 18 … expect X", six contexts asking whether 17 expecting X is compatible; for bare "105 percent of",
six contexts asking whether a value of 105.4 percent is compatible (exact against rounded).

- Authoring always refuses "most" and "multiple", whatever the result, and offers the rewrites "more than half" and
  "at least two". Translation keeps reading sets ("most": {more than half; an open proportion grade}).
- "many", "few", "several" stay refused with rewrites; the answers shape the rewrites.
- Bare "n of the m" stays refused in authoring whatever the result; in translation it is a reading set
  {exactly, at least}.
- Bare "105 percent of" stays refused in authoring with the rewrites "exactly 105 percent of" and "105 percent of, to
  the nearest percent" with a tie rule; in translation it is a reading set {exact, rounded}.
- The experiment only shapes the rewrites and the members of each reading set; agreement among proxy readers never
  admits an ambiguous wording.
- Cost **estimate**: 40 sessions × 42 items (six for each of seven words or forms, as listed) = 1,680 short calls,
  within the usage-cap rules. Draft 3's "36 items, 1,440 calls" did not match its own list (P1 2).
- **Before execution** (phase 1 found these missing): write the 33 unwritten contexts (all eighteen for "many",
  "few" and "several"; the sixth "most" context, at 2 of 4; four of the six "multiple" contexts; five each for bare
  "n of the m" and bare "105 percent of"), the answer format and the analysis; then fix the seeded order over all 42
  (phase 1's order of the nine written items is not the order to run).
- **What the written items can show** (P1 2, computed from the reading sets above): "most" at 50 of 100, and now at 2
  of 4, are the only "most" items where "more than half" says no; at every other point it says yes, so those items
  separate "more than half" only from the open grade, which gives no answer. Bare "16 of the 18" (is 17
  compatible?) and bare "105 percent of" (is 105.4 compatible?) separate their readings; 105.4 is not a tie, so
  `tiesUp` and `halfEven` agree on it.

### QX-2. Hard-constraint decomposition (2 h)

Material: u0165.s01 to s06 (826 B) in the current form (whole-clause open terms) and the decomposed form (act and
graded word on a dimension, FB1 and FB6). One blind independent audit (the reviewer pair of the model split) per unit,
forms unlabelled and in random order: "Does the VE text say what the source says, no more and no less? Is any
threshold, number or comparison present that the source does not give?" Bar: the decomposed form is faithful on at
least 5 of 6 units, introduces no threshold on any, and is judged no worse than the current form on every unit. Then
QT-B4 ships it; otherwise the whole-clause terms stay, with the auditor's reason recorded.

Phase 1 (P1 3) found that QX-2 cannot run as written:

- **Decomposed forms exist for 2 of the 6 units** (FB1 for u0165.s01, FB6 for u0165.s05), and the bar needs one for
  at least five. The bar stays as registered, so **before execution** a decomposed form (dimension, sort, comparative,
  graded word, direction, and the W2 open term of each graded word) is written and reviewed for each of the other
  four. From the source's graded words (bytes from the ledger of run 1800Z):

  | Unit | Bytes | Graded words | Form to write |
  |---|---:|---|---|
  | u0165.s02 | 139 | "serious" (uplift) | candidate: FB1's dimension `uplift` and grade `gives_serious_uplift`, if the compared sort is the same |
  | u0165.s03 | 89 | "significant" (damage) | a damage dimension and an upper grade; the form must also settle the scope the 0600Z audit flags ("that could cause significant damage if deployed" may modify both alternatives or only "malicious code") |
  | u0165.s04 | 175 | "clearly", "substantially" (undermine) | an undermining dimension with "substantially" as an upper grade; whether "clearly" is a second grade or an epistemic word outside the dimension is part of the form, and QT-B3's refusal of "substantially more" (a grade of a difference) does not apply to a grade of the act |
  | u0165.s06 | 160 | "unprecedented", "absolute" (degrees of control) | a control dimension with one or two upper grades |

  The forms are design inputs to the audit, not QT-B1 fixtures; a form that QT-B4 ships becomes a fixture then.
- **The comparator is the form QT-B4 starts from.** The current form has changed once since draft 3 (run 0600Z
  repaired its guard) and is rejected by both audits for its guard, which QX-2 does not test. Queue 4.4 rewrites
  these units (AT-0p → SC-1b → SC-2 → AT-6a/AT-6b → WG-5) before QT-B4, so an audit against today's form would judge a
  comparator QT-B4 never starts from. "The current form" is the form in the translation when QX-2 runs; for the
  result to gate QT-B4, that should be the form after WG-5. When QX-2 runs is set by synthesis phase 1, so this plan
  does not move it: section 11, item 1, asks the DRI. Whatever the timing, the auditors judge the graded words apart
  from the guard, and the record names the form audited (run and SHA-256).

### QX-3. Inferences with proportional grades (2–3 h)

Seed `quantities-QX3`. Twenty items, ten valid under counting semantics and ten invalid, where "most S are P" means
more than half of a nonempty S: "A majority voted yes and a majority voted no. No one voted both yes and no."
(contradiction); "Most S are P; every P is Q. Are most S Q?" (valid); "Most S are P. Are most P S?" (invalid; the
smallest countermodel is one object that is S and P and one that is P only). The answers shape rewrites only. The
majority schema ("the vast majority implies more than half") is not offered on any vote: it waits for a proved bridge
from scales to cardinality (QX-4's plan item), and no fidelity credit is claimed for it. Soundness for counts is not
measured here: on the cardinality route it follows from region arithmetic (FA1-style certificates).

Phase 1 (P1 4) re-derived draft 3's four stated labels under counting semantics and changed two:

- Draft 3's item "The vast majority voted. Did a majority vote?" (labelled valid) is valid only when the grade's
  threshold is above one half, which is the bridge this section does not offer. It leaves the scored twenty. It may
  be asked as an unscored extra, labelled "valid only with the unproved bridge"; its answers inform QX-4, not the
  valid ten.
- "A majority voted yes and a majority voted no." is satisfiable unless no one voted both; the item now states that
  premise, as FA1 states its exclusion premise.
- **Before execution**: write the other seventeen scored items (draft 3 stated four, and item 1 has left), so that
  ten are valid and ten invalid; re-derive each label under counting semantics as phase 1 did
  (`experiments/quantities-phase1/qx_prereg.py` enumerates populations of up to 12 objects; enumeration is a check,
  so each item also gets a short exact argument or a countermodel); then review them.

### QX-4. The 1,000-users passage (research, 4 h)

u0146.s01 to u0147.s05 (bytes 88,637–90,744, 2,107 B) as a companion document: the imagined population as a declared
finite sort, its proportions as cardinality content, "should decline" as a soft norm, "probably" as attitudes'
likelihood word, "1 in 1,000 (or 1 in 1 million)" as a reading set. Needs QT-A4 and the weighing and attitudes
outcomes. Bar: an independent audit finds at least 4 of the 5 key units faithful (u0146.s03, u0146.s04, u0147.s02,
u0147.s04, u0147.s05) and no threshold invented; then a plan item composes `cardinality@0` with the norm routes and
proves the bridge from proportional grades ("the vast majority") to cardinality.
Otherwise the passage stays UNFORMALISED with the failing feature named in the ledger.

## 6. Dependencies and merge conflicts

| Batch | Waits for (in-flight item; branch where known) | Hand-written shared files | Generated (regenerate) |
|---|---|---|---|
| QT-0p | UDHR part: the next UDHR pilot run. Constitution part: a premise budget that finds a three-object model, or the DRI's acceptance of UNKNOWN (section 11, item 2) | pilot directories only | — |
| QT-0 | the cross-plan synthesis (done); QX-1 for the reading-set members of "most" and "multiple" (else "pending") | `docs/spec/quantities.md` (new) | — |
| QT-A1, QT-B1 | QT-0 PASS; QT-B1 also QS-1 | none | `lean/VE.lean`, `lean/VE/Audit.lean`, frozen inventory, axioms, statements, predicates, declarations; trust tables (signed) |
| QT-A2 | QT-A1 (one soundness milestone); ME-1 (`VE.Numbers`) | none | as QT-A1 |
| QT-A3 | QT-A2; AR-10's profile-gate table and mode registry; `fix-main-relay`; the protocol queue on `Protocol.lean` and `service_schema.py` (after `lf-16e`, `qa-q2`, `lean-first/b14d`, AR-10's registry, ME-2; in landing order) | `lean/VE/Service/Protocol.lean`, `ve/backends/service_schema.py`, the `cardinality@0` table row, `ve/assurance-manifest.json`, `ROADMAP.md` | response schemas, `lean/ResponseShape.lean`, `lean/ResponseShape/Audit.lean`, checker pins, assurance doc, route cases, gate collection, AR-10's generated profile data |
| QT-A4 | QT-A3; the document-mode queue after `lf-16g` (AT-3b, SC-1b, QT-A4, ET-5, WG-4, ME-10, in landing order) | Lean `document` mode (`ve/document.py` while it exists), `tools/layer_policy.py`, `tests/data/route-cases.jsonl`, the six test files importing `ve/surface/count.py` | `.importlinter`, gate collection |
| QT-A5 | QT-A4 | `usecases/news-article/*` | — |
| QT-E | english-lean E3 scheduling; english-lean E2 flip (Lean decides English) | `lean/VE/EnglishGrammar/*`, `ve/document.py` (two call sites) | English grammar `Fixed/*` and `LOCK.json` (a person's `--actions-version`), English codes |
| QT-A6 | QT-E, QT-A3, QX-1; the English queue AT-5 → QT-A6 → ME-11 → QT-B3 → SC-7 | `lean/VE/EnglishGrammar/*` (one batch at a time; catalogue rows only, no separate table) | as QT-E |
| QT-A7 | trigger; ME-6 (`ve-units@2`) | ME-6's unit registry (declarations of `week` and `elapsed_day`) | as QT-A3 |
| QT-B2 | QT-B1; PK-1; AR-10's profile-gate table; `lf-16e`, `lf-14d`, `rd-9-int` (`rd-9/integrate`); last in the integration order on `Layered.lean`, after ET-4 | `lean/VE/NormDefaults/Layered.lean` (one provider line), the layered route's response-shape files, the `scales@0` table row, `ve/assurance-manifest.json`, `ROADMAP.md` | as QT-A1, the layered route's schema, gate collection |
| QT-B3 | QT-B2; QT-E or english-lean E3's norm step; the English queue (after ME-11) | `lean/VE/EnglishGrammar/*` | as QT-E |
| QT-B4 | QT-B2 (QT-B3 for display); QX-2 for the hard constraints; the hard-constraint queue (after WG-5; with WG-8, whichever is ready first) | pilot directories | — |
| QX-1 to QX-3 | — (execution under its own authorisation); each its pre-execution material (section 5): QX-1's 33 contexts, QX-2's four decomposed forms, QX-3's seventeen items. QX-2's timing: section 11, item 1 | `experiments/quantities-QX*/` (new); phase 1's audit scripts are in `experiments/quantities-phase1/` | — |
| QX-4 | QT-A4; weighing and attitudes outcomes | `experiments/quantities-QX4/` | — |
| QS-1 | QT-0 PASS (its statements); lands before AT-1, QT-B1 and WG-2 | `lean/VE/Closure/Order.lean` (new; `Paths.lean` unchanged) | as QT-A1 |

How conflicts are avoided: all Lean code is in new directories or files (`lean/VE/Cardinality/`, `lean/VE/Scales/`,
`lean/VE/Closure/Order.lean`), all Python in new modules (`ve/cardinality.py`, `ve/scales.py`) and new test files; the
hand-written shared Lean files are `Protocol.lean` (QT-A3, additive lines in the protocol queue) and `Layered.lean`
(QT-B2's one provider line, after ET-4).
`lf-14b` (norm guards on the order family) touches `norms._lean_route`, which no batch here edits. Generated
inventories are never hand-edited or hand-merged (`regen_generated.py --resolve`). Before each batch, overlap is
checked with `git diff --name-only main...<branch>` against the branches above.

## 7. Expected effect per batch

All **estimates** until a pilot run measures them, except QT-0p's row, which phase 1 measured on rebuilt copies of
the pilots' inputs (P1 1.3); its bytes are claimed, not yet audit-verified.

| Batch | Constitution | UDHR | News | Other |
|---|---|---|---|---|
| QT-0p | **+128 B** claimed, measured (u0042.presupposition 38 B CHECKED; u0043.s02 75 B CHECKED and 15 B LABELLED): 2,951 B (1.60%) to 3,079 B (1.67%); probe "no fourth principal type" SETTLED no (ALL on the negation). Premise check `model` to UNKNOWN, so this part waits (section 0.2) | **+76 B** OPEN, measured on part03 (u097); whole declaration computed, 4,792 B (43.90%) to 4,868 B (44.60%); probe "higher education" UNDECIDED | — | — |
| QT-A1 to QT-A4 | 0 | 0 | 0 | W6a's Python count copy deleted (92 lines) |
| QT-A5 | 0 | 0 | 0–194 B (`s3_count`); one certified consequence under both readings | paper: n of 20 sampled ratio lines expressible |
| QT-E | 0 | 0 | 0 | `ve/surface/time.py` parser and renderer deleted (298 lines) |
| QT-A6 | 0 | 0 | readable wording for the count | eligibility P4 accepted |
| QT-A7 | 0 | 0 | 0 | eligibility's weeks exact |
| QT-B1 to QT-B3 | 0 | 0 | 0 | — |
| QT-B4 | 0–781 B newly claimed (u0043.s01, u0226.s01, s02); 826 B of OPEN hard constraints faithful if queue 4.4 repairs their guards and QX-2 passes | 0–191 B (u031, u093, u094) with rights | — | — |
| QX-4 | research: up to 2,107 B after weighing and attitudes | — | — | — |

NORTH-STAR rows 3 and 9 (combined C score 0.62 from primary tags) recomputed from units with a quantity construct:
at most about 0.29 (R2.6); the buildable part of this plan alone: about 0.19 summed over C, U and N
(5 × 909 / 184,893 + 4 × 267 / 10,916 + 2 × 194 / 5,448). Phase 1 leaves this unchanged: QT-0p measured at the top of
its ranges (128 of C's 909 B, 76 of U's 267 B), and the rest are still the estimates' upper ends. What phase 1 makes
available now is U's 76 B (4 × 76 / 10,916, about 0.03); C's 128 B (about 0.003) waits for its trigger, and 826 B of
hard constraints count only as faithful, not as new bytes, so they are not in the sum.

## 8. Not claimed, open questions, risks

- **Not claimed**: any byte before a pilot run measures it; that any count reported in a source is true; any
  threshold for a graded word; that proxy readers stand for human readers.
- **Open for QT-0**: the carrier of the scales block; the exact name of the response-shape fit predicate; the tie rules
  QT-A2 admits; the `scales` pack's `kind`; whether the closed interval is kept as a separate relation; whether
  english-lean E3's layer mechanism allows separate rule files.
- **Open for the DRI**: news rows 7b and 22b (94 B: a W6 ruling to revisit with a reading set). Phase 1's cross-plan
  questions are in section 11.
- **Limit**: "the vast majority" does not imply "more than half" until a proved bridge from scales to cardinality
  exists (QX-4's plan item); no fidelity credit is claimed for numerical-majority readings.
- **Risks**: the region count grows as 2^n (capped at 6 predicates per sort, refused above); certificate search on the
  erased problem may be slow for many regions (UNKNOWN, never a wrong answer; measured in `tools/bench`, not the
  suite); QX-2 may reject the decomposition, leaving the hard constraints as they are; the norm routes are being
  rebuilt (`rd-9`, `lf-14d`, `lf-16e`), so QT-B2 may need a second statement pass; english-lean E3 may not be
  scheduled soon, which delays all new wordings (contents stay writable as JSON and display through Lean's
  paraphrase).
- **Risks found in phase 1**:
  - An exact count above two in `relational-fol@0` content ("exactly three", pairwise distinctness of three
    constants of one sort) puts every model of the premises above the current search budget (domain size 2), so the
    premise check cannot return `model`. It returns UNKNOWN unless it finds a checked refutation (`INCONSISTENT`,
    `ve/vacuity.py`, `premise_status`); for consistent premises, as in QT-0p, the answer is UNKNOWN. This hits every
    pilot repair of that shape, not only QT-0p.
  - The pilots move under the plan: run 0600Z changed the hard constraints' form within hours of the plan's ledger
    pin. Every experiment record names the run and the SHA-256 of the material it used.
  - Pre-registrations can be incomplete without anyone noticing until execution: all three QX items were. Each
    pre-execution step (section 5) is reviewed before any model call.
  - The readings route shows a unary predicate by its wording only when that wording is one word after "is"
    (`other:english_wording`); QT-0p's `claude_principal_type` displays as `classified as "claude_principal_type"`.
    Display only; recorded, not fixed here.

## 9. Review checklist (QT-0)

- `CFormula.holds` and `Intended` state meanings without reference to erasure or generated formulas.
- `cardinality_elab_sound` has no hypothesis about the structure beyond `Admissible`; `Admissible` adds only
  finiteness of declared sorts.
- Region constants cannot collide with declared symbols (`CEnv.WellFormed`, a hypothesis of `withRegions_admissible`,
  `erase_iff`, `cardinality_elab_sound` and `refutesC_sound`, established by the decoder), and never appear as input.
- `count_atLeast_agree`, `count_atMost_agree`, `count_exactly_agree` and `count_nOfM_agree` hold on declared finite
  sorts for every typed body, so no English count wording has two meanings across routes.
- Every proportion requires a nonempty population, and the paraphrase says so.
- `roundsTo` keeps the written number of places; the tie rule is stated in the sentence.
- `grade_open`: no premise fixes a graded word; `scales_conservative` has no hypothesis that the scale block is empty.
- INCOHERENT carries a Lean-checked refutation and lists the instances it uses; COHERENT a Lean-checked model;
  otherwise UNKNOWN.
- The stub computes the adversarial examples (colliding region constant, three-step cycle, empty population, the
  1 out of 8 tie under each rule, duration-to-date cast).
- Every refusal names a rewrite in plain English; no symbol appears in any wording or diagnostic.
- Every new trusted line has a signed allowance and a ROADMAP trust-cost line.
- The statement review's corrections (spec 2.2): the W6a projection decodes and its identities are bound apart from
  the original's; FB2 states its endpoint premise; each premise label names one premise; only the actual guarantee
  of `scales_conflictFree_iff` is claimed; ratio operands use "divided by"; percentage changes on percent-displayed
  operands are refused; finite sorts are declared in English and counts dispatch by them; tie-up paraphrases say "to
  the larger number"; `erasedProblem_admitted`; the diagnostic order is pinned.

## 10. Shared pieces

The full list, with users, is R7. For this plan: (1) order closure: QS-1 (quantities) over `VE.Closure`, used by
attitudes AT-1, weighing WG-2 and QT-B1; (2) comparison on a dimension with generated coherence premises, which
weighing's precedent rule ("a case at least as strong") and risk's "less severe" could use; (3) graded open terms (a
W2 record plus a dimension and a direction), shared with attitudes' "quite likely"; (4) extra base premises on the
norm routes: PK-1 packs (RD-9 composition owner), with quantities as the `scales` provider; profile registration:
AR-10's profile-gate table (generated Python data); (5) counts over finite sets and closed listings, shared with
events-time-causation and scope; (6) exact rationals and rounding: math-evidence's `VE.Numbers` (QT-A2 proves
`roundsTo_ratio_agree`); (7) unit declarations and conversions: ME-6's `ve-units@2`; (8) quantity English in Lean's
engine, in the serialised English queue AT-5 → QT-A6 → ME-11 → QT-B3 → SC-7, with refusals and reading sets as rows of
english-lean's catalogue ("about" one row shared with math-evidence); (9) one owner per wording for population and
frequency statements ("1 in 1,000", "almost always") among this plan, attitudes and math-evidence.

## 11. Cross-plan issues for the DRI

Phase-1 results that bear on what `SYNTHESIS.md` and `edits-quantities.md` fixed. This plan does not change the shared
part; each item says what the data shows, what stays as written, and what this plan recommends.

1. **When QX-2 runs** (synthesis 4.1, phase 1: "QX-1–QX-3, each under its own gates"; this plan's Order line, edit 10:
   "QT-0p and QX-1 to QX-3 run now").
   - Data (P1 3): QX-2's comparator, the current form of u0165.s01–s06, changed between runs 1800Z and 0600Z, and
     queue 4.4 (AT-0p → SC-1b → SC-2 → AT-6a/AT-6b → WG-5) rewrites it again before QT-B4. An audit run now judges
     a comparator QT-B4 never starts from, and both audits so far rejected that comparator for its guard, which QX-2
     does not test.
   - Unchanged here: the Order line and synthesis 4.1. QT-B4 still waits for QX-2 (synthesis 4.3).
   - Recommendation: write QX-2's four missing decomposed forms now (phase 1 work, no model call), and execute the
     audit after WG-5, as the step before QT-B4 in queue 4.4. This costs QT-B4 nothing, since it already waits for
     WG-5, and the audit then compares with the form QT-B4 edits. The alternative, running now on the graded words
     alone, needs a second audit after WG-5 to gate QT-B4.
2. **A premise budget for exact counts above two** (no shared item covers it; no plan owns it).
   - Data (P1 1.3): QT-0p's "exactly three" turns the whole constitution's premise check from `model` to UNKNOWN.
     The check's model search stops at domain size 2 (`ve/vacuity.py`, `premise_status`; the readings route's
     `ve/readings_verdicts.py`, `BUDGET`), and the repaired content's smallest model has three principal types,
     found at size 3 and checked by Lean.
   - The budget is product code: today a default of `premise_status`, and by the repository's rule a limit is
     Lean's. It is outside this plan and outside QT-A1.
   - Options: (a) the DRI accepts UNKNOWN for the constitution's premise check, and QT-0p's constitution part (+128
     B) applies at the next pilot run; (b) a small item, with an owner the DRI names, that lets the premise check
     find a model needing three or more objects of one sort (a larger or per-sort domain budget), measured for its
     cost on the pilots; (c) drop distinctness, which this plan rejects (the text would say "at most three").
   - Recommendation: (b). Until it lands, QT-0p applies only its UDHR part. Other plans' pilot repairs that state an
     exact count above two meet the same limit: no `model` at size 2, so UNKNOWN unless a checked refutation is found.
3. **The 0600Z audit's finding on the shared hard constraints** (synthesis O17 and queue 4.4: u0165.s01–s07, one
   queue).
   - Data (P1 3): run 0600Z's audit rejects u0165.s01–s07 because both guards take only `situation` and neither binds
     the regulated Claude instance, so one instance's knowledge or belief forbids every instance; it also flags
     u0165.s03's scope ("that could cause significant damage if deployed" may modify both alternatives or only
     "malicious code").
   - This is the queue's to repair, starting with AT-0p; QT-B4 edits only the graded words. Unchanged here: the queue
     and QT-B4's place in it.
   - Recommendation: give the finding to AT-0p's owner as an input. QT-B4's "826 B faithful" needs this repair as well
     as QX-2 (section 4, QT-B4).

Checked, with no conflict: the owners table (section 1.2) and the shared pieces (section 10) are unchanged; QT-0p's
"at the moment" was built as edit 9 says (no date, no second indexical); QS-1, PK-1, AR-10, `VE.Numbers`, `ve-units@2`,
the English queue and the integration order are untouched by phase 1.
