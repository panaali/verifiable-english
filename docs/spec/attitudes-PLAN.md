# Typed attitudes as conditions of norms (`attitudes@0`): buildable plan

> **Status.** Draft 1, 2026-10-12, branch `design/attitudes` at `49de179e`. Research and measurements:
> [docs/research/attitudes.md](../research/attitudes.md) (cited as **R n**). Docs only: nothing here is built,
> proved or measured unless it says so. The Lean blocks are obligations to be elaborated against `main` in AT-0, not
> proofs; where a block names an existing declaration, the name was read on `main` at `49de179e`. Every byte figure
> is either measured from the pinned pilot ledgers (R 2) or marked **estimate**. No model calls were made.
>
> **Gate before any build.** AT-0's statement review must PASS (two planning reviewers converged; under the
> 2026-10-09 model split, Astra and Opus, with Fable arbitrating an item that does not converge). The build starts
> only by DRI decision, after the dependencies of section 5 land (research wave rule `STOP_BEFORE_BUILD=1`).

## 0. Summary

The constitution's latest audit rejected the seven hard constraints (u0165.s01–s07, 874 B) because a mistaken but
confident belief does not trigger them (R 2.2). This plan adds **attitude conditions** to rule guards: "if that
instance of Claude knows that …", "… thinks it quite likely that …", "… intends that …", bound to the rule's party,
to the rule's action through one de re slot, and to a typed content (the category). Lean elaborates each distinct
attitude to a generated predicate and regenerates a fixed set of **frame premises** (knowing is factive; knowing
implies believing and thinking it likely; a stronger likelihood word implies a weaker one where the scale orders
them). The elaborated document is first-order. The frame rides base-premise families the norm-defaults and readings
routes already carry (`BaseAdmissibleX`, `LayeredU.labelled`, `Transfers`). No modal checker, no numbers, no new
budget. Thresholds such as "quite likely" stay open terms with a decider.

**Pilot path.** AT-0p (pilot, no code, now) → E1 and E2 beside AT-0 → AT-0 PASS → AT-1 → AT-2 → AT-3a → AT-3b →
AT-6a (strict companion measured) → AT-4 → AT-6b (main translation measured) → AT-5 (English). About 43 to 51
hours by the table's estimates, experiments included (estimates, not evidence of speed). Off the path: AT-7
(nesting), AT-8 (`reports@0` units in norm documents, after E3), AT-9 (numeric bands, on risk stage B's trigger),
E4 (research).

**The smallest batch that moves a pilot number** is AT-0p: the pilot rewrites the seven guards with the existing
language, so the seven "mistaken belief" points move from UNDECIDED to SETTLED no and the seven units can pass the
next audit. The smallest *product* batch that moves one is AT-3b (it needs AT-1 to AT-3a), measured by AT-6a.

## 1. Evidence (short; details in R 2)

| What | Measured value | How |
|---|---|---|
| Hard-constraint units the audit rejects | 7 units, 874 B, OPEN | `AUDIT.md` verdicts; spans in `units.json` (147 + 139 + 89 + 175 + 116 + 160 + 48) |
| The qualification they lack | u0173.s01, 263 B, UNFORMALISED | `units.json` |
| Probe at "case false, knowledge atom true" | UNDECIDED for all 7 rules | `metrics.json`, `unspecified_probe.hard_constraint_points` |
| Primary `modality/belief` tag | 25 units, 3,268 B; none is a rule condition | grep count; spans summed; classification in R 2.3 |
| Co-blocker `modality/belief` | 628 units; bytes not summed (**estimate** ≈ 106 kB upper bound) | grep count of list entries |
| Other attitude-conditioned rules | 7 units, 1,070 B, co-blocked | R 2.8 |
| UDHR | 0 B for this design (upper 97 B) | R 2.5 |

## 2. Decisions

- **D-A1. One new profile, no new checker.** `attitudes@0` is an elaboration (VISION rule 1) into the norms chain
  under `norm-defaults@0`, and into the readings chain under `readings@1`. Its premises ride existing extra-premise
  families. Nothing frozen changes (rule 2).
- **D-A2. Modes.** `knows`; `thinks w` ("thinks it *w* that", *w* a word of the scale); and `reports@0`'s four acts
  (`says`, `believes`, `wants`, `intends`) reused as `Mode.act a`, never copied. No other mode.
- **D-A3. Contents.** A quantifier-free formula over the author's environment, about at most one thing named by a
  term of the guard (the slot). Content identity is equality of syntax trees, the identity
  `VE.Reports.content_structural` proves `reports@0`'s digests encode. This profile never hashes a content.
- **D-A4. The frame, and nothing else.** (1) knowing is factive; (2) knowing implies believing; (3) knowing implies
  thinking it *w* for every word *w* the document uses; (4) thinking it *w₁* implies thinking it *w₂* when the
  scale puts *w₁* at or above *w₂*. All four relate keys with the same holder sort, slot sort and content. (2) and
  (3) ship only if E2 meets its bar; the pairs of (4) only where E1 meets its bar. Decided before AT-0 closes,
  because the profile's meaning freezes when it ships.
- **D-A5. Likelihood words are lower bounds and stay open.** "Quite likely" means "quite likely or more"; the
  glossary says so. Its threshold is a named open term. Numbers enter only from a document's declared bands, through
  risk stage B (AT-9), which extends this scale and never copies it.
- **D-A6. Every generated atom is an open term.** Its record is generated: arguments (holder sort, slot sort),
  factors from a Lean table by mode ("what counts as knowing that …", "how likely counts as quite likely"),
  `decided_by` the document's `attitudes.decided_by`, else `unresolved_decider`.
- **D-A7. One reading.** Refused, each with one-reading rewrites (AT-5): a negated "knows" except right after its
  content is asserted in the same condition; "does not think it *w* that" (neg-raising); bare "thinks that" (as
  `reports@0` refuses it); attitude adverbs ("knowingly", "intentionally", "deliberately"); a holder pronoun that
  does not resolve to a variable of the rule.
- **D-A8. Lean owns the words.** The attitude verbs, synonyms and refusals are one Lean table. `reports@0`'s Python
  literals (`_VERBS`, `_SYNONYMS`, `_REJECTED` in `ve/report_english.py`) are deleted in AT-5 and read from the
  generated export.
- **D-A9. Nothing from intending, wanting or saying.** No success, no desire, no obligation, no belief follows from
  them; no closure under consequence or conjunction; nothing across holders; no introspection.
- **D-A10. Residual honesty.** Generated open terms count in the residual like any other. The constitution's count
  rises by an **estimated** 20 (21 generated atoms replace one hand-named term); how the residual is displayed is not
  this plan's decision.

## 3. Design

### 3.1 What a writer writes and a reader sees

The pilot's rule u0165.s01 with u0173.s01's condition, as VE renders it (the act phrase and the category wording are
the pilot's existing ones):

> Every instance of Claude must not do the weapons uplift in each situation, if that instance of Claude knows that
> that situation is classified as "mass_casualty_weapon_uplift" and intends that that situation is classified as
> "mass_casualty_weapon_uplift", or if that instance of Claude thinks it quite likely that that situation is
> classified as "mass_casualty_weapon_uplift".

The legend adds, rendered by Lean from the frame premises:

> If an instance of Claude knows that a situation is classified as "mass_casualty_weapon_uplift", then that
> situation is classified as "mass_casualty_weapon_uplift".
> If an instance of Claude knows that a situation is classified as "mass_casualty_weapon_uplift", then it thinks it
> quite likely that that situation is classified as "mass_casualty_weapon_uplift".
> "Quite likely" means quite likely or more likely. How likely counts as quite likely is not decided by VE (decided
> by: unresolved decider).

No symbol appears in what people read or write. The structured form (JSON content) is what the pilot writes today;
the English form becomes writable in AT-5.

### 3.2 Syntax, keys and names

A guard is W1's guard grammar with one more atom, an attitude condition. A **key** is (mode, holder sort, slot sort,
content). Keys are listed once each (`VE.Reports.dedup`, reused); each key gets the predicate
`attitudes__<mode>__<i>` on (holder sort, slot sort). Names are fresh in `E`, at most 64 bytes and pairwise
distinct (checked by `WellFormedAtt`, proved by `names_fresh`, `names_injective`).

### 3.3 Elaboration

Each condition becomes `attitudes__<mode>__<i>(holder)` (closed content) or `attitudes__<mode>__<i>(holder, t)`
(slot term `t`). The rule becomes an ordinary `VE.Norms.Node` over `envAtt A = E + generated predicates`. The
document's regulated predicates, completions, act phrases and definitions are unchanged.

### 3.4 The frame

For each `knows` key `k`: `∀h ∀x. k(h, x) → content(x)` (label `attitude:factive`). For each ordered pair of keys
with the same subject that D-A4 relates: `∀h ∀x. k(h, x) → k′(h, x)` (label `attitude:entails`). Contents are
quantifier-free, so every frame premise is universal with a quantifier-free body (`frame_universalQF`), the shape
the norm-defaults evidence requires (`VE.NormDefaults.UniversalQF`).

### 3.5 Semantics and obligations

`Intended` (AT-1) says exactly: attitude relations are typed, knowing is factive, and each frame pair holds. The
obligations of VISION rule 4: faithfulness against this independent semantics (`att_elaboration_faithful`,
`frame_iff_intended`, model correspondence both ways); conservativity (`att_old_language_conservative`); the
audit's requirement (`mistaken_belief_admissible`); independence beyond the frame (`attitudes_independent`);
certificate soundness and model validity are the existing routes' theorems instantiated with the frame (AT-2, AT-4);
a trust-cost line in ROADMAP (AT-3a).

### 3.6 Routes

| Route | Existing extra-premise mechanism | How the frame enters |
|---|---|---|
| norm-defaults, strict chain (the pilot's `readings/all-strict.ve.md`) | `VE.NormDefaults.Wire.LayeredU` (`labelled`, `X`, `background := backgroundBase ++ X ++ fillPremises`), `layered_conflict_sound`, `layered_report_sound`, `UndecidedAtX` | an `attitudes@0` branch builds a `LayeredU` with `labelled := frameLabels.zip framePremises` (AT-2, AT-3a) |
| norm-defaults statuses at a point | `replayStatus`, `normDefaults_wire_status_sound` | the point's model must satisfy the frame; then `SettledAs`/`UndecidedAt` agree with their frame versions (`settled_frame_agree`, `undecided_frame_agree`, AT-2) |
| readings, superposed and enumerated (the main translation) | `VE.Readings.Transfers`, `superpose_*_extra`, `fill_transfers` | `Q := fillPremises (supU N) ++ framePremises`, by `transfers_append` and `frame_transfers` (AT-4) |

### 3.7 English and one reading (AT-5)

| Wording | Reading | Status |
|---|---|---|
| "X knows that P" | knows | admitted |
| "X thinks it *w* that P", *w* in the scale | thinks *w* (lower bound) | admitted |
| "X believes that P", "X wants Y to VP", "X intends that P", "X says that P" | `reports@0`'s acts | admitted (VP needs the act-phrases design; until then "intends that P") |
| "P, and X does not know that P" | not knows, content asserted | admitted (presupposition satisfied in the same condition) |
| "unless X knows that P" (carve-out) | not knows, no presupposition | admitted |
| "X does not know that P" elsewhere | two readings (with and without P) | refused `NegatedFactive`, rewrites: the two rows above |
| "X does not think it *w* that P" | neg-raising: two readings | refused `NegRaising`, rewrites: "it is not the case that X thinks it *w* that P"; "X thinks it *w* that it is not the case that P" |
| "X thinks that P" | belief or opinion | refused (as `reports@0`), rewrites: "X believes that P"; "X thinks it likely that P" |
| "X knowingly / intentionally / deliberately VPs" | scope of the adverb | refused `AttitudeAdverb`, rewrite into conditions |
| "it thinks …" with "it" not a rule variable | unresolved holder | refused (discourse rule: no pronoun crosses a quote boundary) |

### 3.8 Limits and UNKNOWN

No new budget. Generated predicates count against `MAX_PREDICATES` (256; the constitution's main translation uses
68 now and would use **about** 88: 68 − 1 hand-named term + 21 generated). Above it, admission refuses (`InvalidInput`), never a verdict. Every UNKNOWN of the routes stays
UNKNOWN.

### 3.9 One owner per piece of logic

| Piece | Owner | This plan |
|---|---|---|
| Acts says, believes, wants, intends; their names | `VE.Reports.Act`, `Act.name` | reused as `Mode.act` |
| Content identity | AST equality (`VE.Reports.content_structural`) | reused; no hashing |
| Key de-duplication | `VE.Reports.dedup` | reused |
| Open-term record schema | W2 (`document.md`), `VE.Reports.Assessment` shape | generated records follow it |
| Extra base premises on routes | `LayeredU`, `BaseAdmissibleX`, `Transfers` | reused; no new route semantics |
| Likelihood words and their order | **new** `VE.Attitudes.Scale` | the one owner; risk stage B extends it (AT-9) |
| Attitude verbs, synonyms, refusals (English) | **moves** from `ve/report_english.py` to `VE.Attitudes.Words` | AT-5 deletes the Python literals |
| The hand-named open term `restricted_action_knowing_or_quite_likely` | pilot translation | deleted by AT-0p, then AT-0p's atoms by AT-6 |

### 3.10 Conservativity

Any structure over `E` extends to `envAtt A` by reading every generated predicate as empty; every frame premise
then holds (its antecedent is false), and old formulas keep their values. So a document without attitude
conditions means what it meant, and old-language consequence is unchanged (`att_old_language_conservative`,
`att_conservative_doc`).

## 4. Batches

Every product batch: 2 to 6 hours for one builder, with the lean-first gate (selected tests while iterating; the
full gate once, on the final HEAD; corpus A/B where the batch changes an answer; `DELTA.md` by class), the Lean audit
(`python3 lean/audit.py`: no forbidden word even in comments, no primes in theorem names, names under about 57
characters), regenerated inventories through `uv run python tools/regen_generated.py --write` (never by hand),
`tools/lean_statements.py` showing additions only, and seeded bugs in each changed language (CLAUDE.md). The seeded
bugs, one per behaviour claimed: AT-1, factivity generated with its implication reversed (F-AT1's M2 `#guard`
fails); AT-2, the frame check skipped at a point (M2 is no longer refused); AT-3a, the decoder accepting `degree` on
a mode other than `thinks`; AT-3b, below; AT-4, the frame dropped from one choice's base premises (an enumerated
fixture fails); AT-5, a refused form read with one of its two readings (`refused_have_rewrites`'s fixture fails).
Statement review before Lean build: AT-0 reviews every statement below; a statement that changes during a build
reopens only that statement.

| # | Batch | Hours | Owner | Needs |
|---|---|---:|---|---|
| AT-0p | Pilot repair with the existing language (no product code) | 2 | pilot runner | — |
| E1 | Likelihood-word order and lower-bound reading (experiment) | 2–3 | experiment runner | — |
| E2 | Factivity, knows → believes, knows → thinks it likely, negated "know" (experiment) | 2 | experiment runner | — |
| AT-0 | Statement spec `docs/spec/attitudes.md`, stub elaborated against main, statement review | 3–4 | planner | E1, E2 results |
| AT-1 | Lean core: syntax, keys, elaboration, frame, semantics, theorems, fixtures | 5–6 | Lean | AT-0 PASS |
| AT-2 | Lean: the norm-defaults route under the frame (statuses, conflicts, report) | 4–5 | Lean | AT-1 |
| AT-3a | Lean wire, service mode `attitudes`, response shape and encoder theorem | 5–6 | Lean | AT-2; `lf-16e`, `qa-q2` merged |
| AT-3b | Python relay, `ve document` hook, fixtures and fuzz tests | 4–5 | Python | AT-3a |
| AT-6a | Pilot: the strict companion with typed attitudes, measured | 3 | pilot tooling | AT-3b |
| AT-4 | Readings chain under the frame (superposed and enumerated) | 5–6 | Lean, Python | AT-3b; `lf-14d`, `rd-9-int` merged |
| AT-6b | Pilot: the main translation with typed attitudes, measured | 3 | pilot tooling | AT-4 |
| AT-5 | English in Lean: wordings, refusals, rewrites; `reports@0`'s Python tables deleted | 5–6 | Lean, Python | AT-3b; `qa-q2` merged |
| AT-7 | Nested conditions (two levels) and "knows whether" | 5–6 | Lean | AT-4 |
| E3 | "We want Claude to X": report, rule, or both (experiment) | 3 | experiment runner | — |
| AT-8 | `reports@0` units in norm documents | 5–6 | Lean, Python | E3; DRI decision with the attribution owners |
| AT-9 | Numeric bands on the scale (shared with risk stage B) | 3–4 | Lean | risk stage B's trigger |
| E4 | Claims as objects for honesty norms (experiment) | 4–5 | planner, Lean stub | AT-1 |

### AT-0p. Pilot repair with the existing language (pilot runner, 2 h)

No product code. In the constitution pilot, for each hard constraint i (seven categories `C_i`, the existing case
atoms), replace the guard `C_i(s) ∧ restricted_action_knowing_or_quite_likely(s)` by

```text
( C_i(s) ∧ knowingly_engages_<i>(c, s) ) ∨ thinks_quite_likely_<i>(c, s)
```

with fourteen binary open terms on (`claude_instance`, `situation`): `knowingly_engages_<i>` ("Claude knowingly and
intentionally engages in the action of the situation as an action of category i"; factor: what counts as knowingly
and intentionally engaging) and `thinks_quite_likely_<i>` ("Claude thinks it quite likely that the action of the
situation falls into category i"; factor: how likely counts as quite likely). `C_i(s)` stays explicit in the first
branch because VE cannot know, with untyped terms, that knowing implies the category. Delete
`restricted_action_knowing_or_quite_likely`.

- **Probe points to add** (four per rule, `probes/unspecified-probe.json`): case false and thinks-quite-likely true
  (expected SETTLED no, the audit's case); case true and knowingly true (SETTLED no); neither (UNDECIDED); case
  false and knowingly true (UNDECIDED: an impossible situation the untyped language cannot refuse).
- **Expected numbers (estimates until measured):** claimed bytes unchanged (2,951); the 7 units (874 B) become
  candidates for audit verification; open terms 33 → 46; the seven audit-case points UNDECIDED → SETTLED no.
- **Not claimed:** typing. AT-6a replaces the fourteen open terms with generated attitudes.

### E1. Likelihood words: order and lower bounds (experiment, 2–3 h)

Pre-registered. Readers: Sonnet 5.5 as human proxy (`claude-sonnet-5-5`), 40 independent sessions with no shared
context, items in a seeded random order (seed `attitudes-E1`). Words: almost certain, very likely, quite likely,
likely, more likely than not, as likely as not, unlikely, very unlikely (8 words, 28 pairs), each pair as two
sentences "Claude thinks it *a* that the file is safe" / "… *b* …", question: "If the first sentence is true, must the
second be true?" (yes / no / cannot tell). Plus 8 items "If Claude is certain that the file is safe, does Claude
think it *w* that the file is safe?".

- **A pair enters the scale table** (`Scale.table.above`) iff at least 36 of 40 answer yes and at most 2 answer no.
- **The lower-bound reading of a word** is confirmed iff at least 34 of 40 answer yes to its certainty item; a word
  that fails stays in the scale with no pair (it implies and is implied by nothing).
- Nothing else is concluded. This measures agreement among proxy readers, not truth and not human readers. Cost
  **estimate**: 40 × 36 = 1,440 short calls, under the usage cap rules.

### E2. Factivity and the knowing entailments (experiment, 2 h)

Same protocol, 12 items: three factivity items ("Claude knows that the file is safe. Must the file be safe?"); three
"knows → believes"; three "knows → thinks it quite likely"; three negated-"know" items ("Claude does not know that
the file is safe. Must the file be safe?", where the expected answer splits).

- Frame premise 1 ships iff all three factivity items reach 36 of 40. (If not, `knows` is not admitted at all.)
- Frame premise 2 ships iff its three items reach 36 of 40; premise 3 likewise.
- The negated-"know" items are expected to split (that is why D-A7 refuses the form); if instead 36 of 40 agree on
  one reading, AT-0 records it and keeps the refusal anyway (one reading must not depend on a majority).

### AT-0. Statement spec and review (planner, 3–4 h)

- `docs/spec/attitudes.md`: sections 2 and 3 as a statement spec (definitions, wordings with one reading each, wire,
  diagnostics in order, the Lean blocks of AT-1 to AT-4 verbatim, fixtures, limits, review checklist), with E1's
  pairs and E2's frame decisions written in.
- `lean/SpecStubs_attitudes.lean`, untracked: every definition with the bodies given here and every statement as a
  `def … : Prop`, elaborated with `lake env lean` against a build of main. Every failure is fixed in the spec.
- Pins the integration points this plan can only name: the `LayeredU` constructor for a strict attitudes document
  (expected: the elaborated W1 document as a soft document with no soft rule, through `VE.Readings.strictNodeOf`
  and `soften_hard_identity`); where the point-status replay checks the frame; whether `ve document` dispatch is
  Python or Lean's `document` mode after `lf-16e`; the export of the English table (AT-5).
- Review checklist: section 8.
- Done when the stub elaborates, the spec is committed, and the review converges on PASS.

### AT-1. Lean core (Lean, 5–6 h)

Files: `lean/VE/Attitudes/Scale.lean`, `Syntax.lean`, `Frame.lean`, `Semantics.lean`, `Theorems.lean`,
`Examples.lean` (`#guard`s), all new; `lean/ATTITUDES.md` (new). Generated (regenerate, never hand-edit):
`lean/VE.lean` (import union), `lean/VE/Audit.lean` (one `#print axioms` line per theorem),
`lean/VE/Route/frozen-sources.sha256`, `lean/axioms.txt`, `lean/statements.txt`, `lean/declarations.txt`,
`lean/predicates.txt`, `tools/gate-collection.json` (unchanged unless a test is added). No hand-written shared file.

```lean
import VE.Attribution.Content
import VE.Norms.Tree
import VE.NormDefaults.Evidence

namespace VE.Attitudes
open VE.Reports (Act)
universe u

/-! ## The likelihood scale (D-A5). Risk stage B adds declared ranges to these words (AT-9); it never copies them. -/

/-- A likelihood word as written after "thinks it", in lower case: "quite likely". -/
abbrev Word := String

/-- `above` lists pairs `(a, b)` read "a is at least as likely as b". -/
structure Scale where
  words : List Word
  above : List (Word × Word)
  deriving DecidableEq, Repr

/-- One round of composing `above` with itself. -/
def Scale.step (σ : Scale) (ps : List (Word × Word)) : List (Word × Word) :=
  ps ++ ps.flatMap (fun p => (σ.above.filter (·.1 == p.2)).map (fun q => (p.1, q.2)))

/-- The reflexive and transitive closure of `above`, by `words.length` rounds. -/
def Scale.atLeast (σ : Scale) (a b : Word) : Bool :=
  a == b || (Nat.iterate σ.step σ.words.length σ.above).contains (a, b)

/-- The Lean table. `above` holds exactly the pairs E1 confirmed; before E1 reports it is empty. -/
def table : Scale :=
  { words := ["almost certain", "very likely", "quite likely", "likely", "more likely than not",
      "as likely as not", "unlikely", "very unlikely"],
    above := [] }

/-! ## Syntax (3.2) -/

/-- `act a` is the act `a` of reports@0 with its name and English verbs; `knows` and `thinks w` are new. -/
inductive Mode where
  | act (a : Act)
  | knows
  | thinks (w : Word)
  deriving DecidableEq, Repr

def Mode.slug : Mode → String
  | .act a => a.name
  | .knows => "knows"
  | .thinks w => "thinks_" ++ w.map (fun c => if c == ' ' then '_' else c)

/-- One attitude condition. `holder` is a term of the guard. `slot = some (s, t)`: the content's variable 0 has sort
    `s` and stands for the guard's term `t`; `slot = none`: the content is closed. -/
structure Cond where
  holder : VE.Term
  mode : Mode
  slot : Option (String × VE.Term)
  content : VE.Formula
  deriving DecidableEq, Repr

/-- W1's guard formulas with attitude conditions as atoms. -/
inductive AFormula where
  | base (φ : VE.Formula)
  | att (c : Cond)
  | not (a : AFormula)
  | and (a b : AFormula)
  | or (a b : AFormula)
  | implies (a b : AFormula)
  | all (s : String) (a : AFormula)
  | ex (s : String) (a : AFormula)
  deriving DecidableEq, Repr

/-- A W1 rule whose guard and carve-outs may carry attitude conditions (the fields of `VE.Norms.Node`). -/
structure ARule where
  name : String
  pred : String
  sign : Bool
  guard : AFormula
  carveOuts : List AFormula
  over : List String
  deriving DecidableEq, Repr

structure AttDoc where
  E : VE.Environment
  lits : List String
  regulated : List VE.Norms.Regulated
  definitions : List VE.Norms.Definition
  rules : List ARule
  /-- the holder sorts -/
  holders : List String
  /-- `table` plus the document's declared pairs between its own words -/
  scale : Scale
  /-- the decider of every generated open term; "unresolved_decider" when the document names none -/
  decidedBy : String

/-- What makes two conditions one attitude (D-A3): no hashing, syntax-tree equality of the content. -/
structure Key where
  mode : Mode
  holderSort : String
  slotSort : Option String
  content : VE.Formula
  deriving DecidableEq, Repr

def Key.sorts (k : Key) : List String := k.holderSort :: k.slotSort.toList

def Cond.key (A : AttDoc) (Γ : List String) (c : Cond) : Option Key :=
  match c.holder.sortOf A.E Γ with
  | some hs => if A.holders.contains hs then some ⟨c.mode, hs, c.slot.map (·.1), c.content⟩ else none
  | none => none

def AFormula.conds : List String → AFormula → List (List String × Cond)
  | _, .base _ => []
  | Γ, .att c => [(Γ, c)]
  | Γ, .not a => a.conds Γ
  | Γ, .and a b => a.conds Γ ++ b.conds Γ
  | Γ, .or a b => a.conds Γ ++ b.conds Γ
  | Γ, .implies a b => a.conds Γ ++ b.conds Γ
  | Γ, .all s a => a.conds (s :: Γ)
  | Γ, .ex s a => a.conds (s :: Γ)

/-- A rule's guard context: its predicate's sorts, the last argument as variable 0 (W1's `(sorts pred).reverse`). -/
def ruleContext (A : AttDoc) (r : ARule) : List String :=
  match A.regulated.find? (·.name == r.pred) with
  | some d => d.sorts.reverse
  | none => []

def condsOf (A : AttDoc) : List (List String × Cond) :=
  A.rules.flatMap (fun r => (r.guard :: r.carveOuts).flatMap (·.conds (ruleContext A r)))

def keys (A : AttDoc) : List Key := VE.Reports.dedup ((condsOf A).filterMap (fun p => p.2.key A p.1))

/-- `attitudes__<mode>__<i>`, `i` the 1-based position among the keys of that mode. -/
def name (A : AttDoc) (k : Key) : String :=
  "attitudes__" ++ k.mode.slug ++ "__" ++ toString (((keys A).filter (·.mode == k.mode)).idxOf k + 1)

def keyOf (A : AttDoc) (r : String) : Option Key := (keys A).find? (fun k => name A k == r)

/-- `E` plus one predicate per key, on the key's sorts. -/
def envAtt (A : AttDoc) : VE.Environment :=
  { A.E with predicates := fun r =>
      match keyOf A r with
      | some k => some k.sorts
      | none => A.E.predicates r }

/-! ## Elaboration (3.3) -/

def atom (A : AttDoc) (k : Key) (h : VE.Term) : Option VE.Term → VE.Formula
  | none => .unary (name A k) h
  | some t => .binary (name A k) h t

def AFormula.elab (A : AttDoc) : List String → AFormula → Option VE.Formula
  | _, .base φ => some φ
  | Γ, .att c => (c.key A Γ).map (fun k => atom A k c.holder (c.slot.map (·.2)))
  | Γ, .not a => (a.elab A Γ).map .not
  | Γ, .and a b => (a.elab A Γ).bind (fun x => (b.elab A Γ).map (.and x))
  | Γ, .or a b => (a.elab A Γ).bind (fun x => (b.elab A Γ).map (.or x))
  | Γ, .implies a b => (a.elab A Γ).bind (fun x => (b.elab A Γ).map (.implies x))
  | Γ, .all s a => (a.elab A (s :: Γ)).map (.all s)
  | Γ, .ex s a => (a.elab A (s :: Γ)).map (.ex s)

def ARule.elab (A : AttDoc) (r : ARule) : Option VE.Norms.Node :=
  (r.guard.elab A (ruleContext A r)).bind (fun g =>
    (r.carveOuts.mapM (·.elab A (ruleContext A r))).map (fun cs => ⟨r.name, r.pred, r.sign, g, cs, r.over⟩))

/-- The elaborated W1 document over `envAtt A`. -/
def toNorms (A : AttDoc) : Option VE.Norms.Doc :=
  (A.rules.mapM (·.elab A)).map (fun ns => ⟨envAtt A, A.lits, ⟨A.regulated, A.definitions, ns⟩⟩)

/-- Quantifier-free formulas. -/
def qf : VE.Formula → Bool
  | .all _ _ => false
  | .ex _ _ => false
  | .not a => qf a
  | .and a b => qf a && qf b
  | .or a b => qf a && qf b
  | .implies a b => qf a && qf b
  | _ => true

/-- The executable check (spec 4.1, bodies in the stub): every condition's key exists (a holder of a holder sort);
    its slot term has the slot's sort in its context; its content is `qf` and well formed over `E` in the slot's
    context (`[s]`, or `[]` when closed); every `thinks w` uses a word of `A.scale.words`; every `A.scale.above`
    pair is between two of its words and contains `table.above`; every base formula is well formed over `E`;
    generated names are undeclared in `E`, at most 64 bytes and pairwise distinct; `E`'s predicates plus the keys stay
    within `VE.Reports.maxPredicates`; every rule's predicate is regulated; `decidedBy` is non-empty. -/
def WellFormedAtt (A : AttDoc) : Bool := wellFormedBody A

/-- The guard-level part of `WellFormedAtt`, as a proposition over one formula in context `Γ`. -/
def AWellFormed (A : AttDoc) (Γ : List String) (a : AFormula) : Prop := aWellFormedBody A Γ a

/-! ## The frame (3.4) -/

/-- An attitude of mode `m` implies one of mode `m′` on the same subject (D-A4). Premises 2 and 3 are the first two
    rows; AT-0 removes either row if E2 does not meet its bar. -/
def entailsMode (σ : Scale) : Mode → Mode → Bool
  | .knows, .act .believes => true
  | .knows, .thinks _ => true
  | .thinks w, .thinks w2 => w != w2 && σ.atLeast w w2
  | _, _ => false

def sameSubject (k k2 : Key) : Bool :=
  k.holderSort == k2.holderSort && k.slotSort == k2.slotSort && k.content == k2.content

def framePairs (A : AttDoc) : List (Key × Key) :=
  (keys A).flatMap (fun k =>
    ((keys A).filter (fun k2 => sameSubject k k2 && entailsMode A.scale k.mode k2.mode)).map (k, ·))

/-- `∀h. body` or `∀h ∀x. body`: the slot is variable 0, the holder variable 1 (or 0 when closed). -/
def closeOver (k : Key) (body : VE.Formula) : VE.Formula :=
  match k.slotSort with
  | none => .all k.holderSort body
  | some s => .all k.holderSort (.all s body)

def atomAt (A : AttDoc) (k : Key) : VE.Formula :=
  match k.slotSort with
  | none => .unary (name A k) (.var 0)
  | some _ => .binary (name A k) (.var 1) (.var 0)

/-- Frame premise 1. -/
def factive (A : AttDoc) (k : Key) : VE.Formula := closeOver k (.implies (atomAt A k) k.content)

/-- Frame premises 2 to 4. -/
def entails (A : AttDoc) (p : Key × Key) : VE.Formula :=
  closeOver p.1 (.implies (atomAt A p.1) (atomAt A p.2))

def framePremises (A : AttDoc) : List VE.Formula :=
  ((keys A).filter (·.mode == .knows)).map (factive A) ++ (framePairs A).map (entails A)

def frameLabels (A : AttDoc) : List String :=
  ((keys A).filter (·.mode == .knows)).map (fun _ => "attitude:factive") ++
    (framePairs A).map (fun _ => "attitude:entails")

/-! ## Semantics (3.5), independent of `elab` -/

structure AttModel (A : AttDoc) where
  S : VE.Structure.{u}
  J : Key → List S.Carrier → Prop

/-- A key's content at a tuple: closed content at `[h]`, slot content at `[h, x]` with `x` as variable 0. -/
def contentAt {A : AttDoc} (m : AttModel.{u} A) (k : Key) : List m.S.Carrier → Prop
  | [_] => k.slotSort = none ∧ k.content.denote m.S []
  | [_, x] => k.slotSort.isSome ∧ k.content.denote m.S [x]
  | _ => False

/-- What the attitude words mean, and nothing more: typed relations, factive knowing, the frame pairs. -/
def Intended (A : AttDoc) (m : AttModel.{u} A) : Prop :=
  (∀ k vs, m.J k vs → k ∈ keys A ∧ VE.TupleTyped m.S k.sorts vs) ∧
  (∀ k ∈ keys A, k.mode = .knows → ∀ vs, m.J k vs → contentAt m k vs) ∧
  (∀ p ∈ framePairs A, ∀ vs, m.J p.1 vs → m.J p.2 vs)

def AFormula.denote (A : AttDoc) (m : AttModel.{u} A) : List String → VE.Valuation m.S → AFormula → Prop
  | _, ρ, .base φ => φ.denote m.S ρ
  | Γ, ρ, .att c => ∃ k, c.key A Γ = some k ∧ ∃ vh, c.holder.denote m.S ρ = some vh ∧
      match c.slot with
      | none => m.J k [vh]
      | some (_, t) => ∃ vx, t.denote m.S ρ = some vx ∧ m.J k [vh, vx]
  | Γ, ρ, .not a => ¬ a.denote A m Γ ρ
  | Γ, ρ, .and a b => a.denote A m Γ ρ ∧ b.denote A m Γ ρ
  | Γ, ρ, .or a b => a.denote A m Γ ρ ∨ b.denote A m Γ ρ
  | Γ, ρ, .implies a b => a.denote A m Γ ρ → b.denote A m Γ ρ
  | Γ, ρ, .all s a => ∀ v, m.S.domain s v → a.denote A m (s :: Γ) (v :: ρ)
  | Γ, ρ, .ex s a => ∃ v, m.S.domain s v ∧ a.denote A m (s :: Γ) (v :: ρ)

/-- The structure over `envAtt A`: each generated name read as its key's relation. -/
def interp (A : AttDoc) (m : AttModel.{u} A) : VE.Structure.{u} :=
  { m.S with relation := fun r vs =>
      match keyOf A r with
      | some k => m.J k vs
      | none => m.S.relation r vs }

/-- An `envAtt A` structure read back as an attitude model. -/
def restrict (A : AttDoc) (T : VE.Structure.{u}) : AttModel.{u} A :=
  ⟨{ T with relation := fun r vs => keyOf A r = none ∧ T.relation r vs },
    fun k vs => k ∈ keys A ∧ T.relation (name A k) vs⟩

/-! ## Theorems (bodies in AT-1; statements reviewed in AT-0) -/

theorem names_fresh (A : AttDoc) (h : WellFormedAtt A = true) :
    ∀ k ∈ keys A, A.E.predicates (name A k) = none ∧ (name A k).utf8ByteSize ≤ 64
theorem names_injective (A : AttDoc) (h : WellFormedAtt A = true) :
    ∀ k ∈ keys A, ∀ k2 ∈ keys A, name A k = name A k2 → k = k2
theorem envAtt_extends (A : AttDoc) (h : WellFormedAtt A = true) (Γ : List String) (φ : VE.Formula)
    (hφ : φ.WellFormed A.E Γ) : φ.WellFormed (envAtt A) Γ
theorem toNorms_isSome (A : AttDoc) (h : WellFormedAtt A = true) : (toNorms A).isSome = true
theorem frame_wellFormed (A : AttDoc) (h : WellFormedAtt A = true) :
    ∀ φ ∈ framePremises A, φ.WellFormed (envAtt A) []
theorem frame_universalQF (A : AttDoc) (h : WellFormedAtt A = true) :
    ∀ φ ∈ framePremises A, VE.NormDefaults.UniversalQF φ

/-- Faithfulness, guards: the elaborated guard means what the attitude guard means. -/
theorem att_elaboration_faithful (A : AttDoc) (h : WellFormedAtt A = true) (m : AttModel.{u} A)
    (hS : m.S.Admissible A.E) (Γ : List String) (ρ : VE.Valuation m.S) (hρ : VE.Valuation.Typed m.S Γ ρ)
    (a : AFormula) (ha : AWellFormed A Γ a) (φ : VE.Formula) (he : a.elab A Γ = some φ) :
    φ.denote (interp A m) ρ ↔ a.denote A m Γ ρ
/-- Faithfulness, the frame: the frame premises hold exactly when the relations mean what `Intended` says. -/
theorem frame_iff_intended (A : AttDoc) (h : WellFormedAtt A = true) (m : AttModel.{u} A)
    (hS : m.S.Admissible A.E) (hJ : ∀ k vs, m.J k vs → k ∈ keys A ∧ VE.TupleTyped m.S k.sorts vs) :
    VE.Norms.Sat (interp A m) (framePremises A) ↔ Intended A m
/-- Model correspondence, both ways. -/
theorem interp_admissible (A : AttDoc) (h : WellFormedAtt A = true) (m : AttModel.{u} A)
    (hS : m.S.Admissible A.E) (hI : Intended A m) : (interp A m).Admissible (envAtt A)
theorem restrict_admissible (A : AttDoc) (h : WellFormedAtt A = true) (T : VE.Structure.{u})
    (hT : T.Admissible (envAtt A)) : (restrict A T).S.Admissible A.E
theorem interp_restrict (A : AttDoc) (h : WellFormedAtt A = true) (T : VE.Structure.{u})
    (hT : T.Admissible (envAtt A)) (r : String) (vs : List T.Carrier) :
    (interp A (restrict A T)).relation r vs ↔ T.relation r vs
theorem old_formula_invariant (A : AttDoc) (h : WellFormedAtt A = true) (m : AttModel.{u} A) (Γ : List String)
    (ρ : VE.Valuation m.S) (φ : VE.Formula) (hφ : φ.WellFormed A.E Γ) :
    φ.denote (interp A m) ρ ↔ φ.denote m.S ρ

/-- Conservativity (VISION rule 4). -/
theorem att_old_language_conservative (A : AttDoc) (h : WellFormedAtt A = true) (Γ : List VE.Formula)
    (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed A.E []) (hφ : φ.WellFormed A.E []) :
    VE.Entails.{u} (envAtt A) (Γ ++ framePremises A) φ ↔ VE.Entails.{u} A.E Γ φ
/-- A document with no attitude condition: no key, no frame, the same environment. -/
theorem att_conservative_doc (A : AttDoc) (h0 : condsOf A = []) :
    keys A = [] ∧ framePremises A = [] ∧ envAtt A = A.E

/-- Frame premise 1 as a fact of every intended model. -/
theorem knows_factive (A : AttDoc) (m : AttModel.{u} A) (hI : Intended A m) (k : Key) (hk : k ∈ keys A)
    (hm : k.mode = .knows) (vs : List m.S.Carrier) (hJ : m.J k vs) : contentAt m k vs
/-- The audit's requirement (R 2.2): any attitude other than knowing may be held of a false content. No hypothesis
    about the content appears. -/
theorem mistaken_belief_admissible (A : AttDoc) (h : WellFormedAtt A = true) (S : VE.Structure.{u})
    (hS : S.Admissible A.E) (k : Key) (hk : k ∈ keys A) (hm : k.mode ≠ .knows) (vs : List S.Carrier)
    (hvs : VE.TupleTyped S k.sorts vs) :
    ∃ J : Key → List S.Carrier → Prop, Intended A ⟨S, J⟩ ∧ J k vs
/-- Nothing beyond the frame (no closure under consequence or conjunction, nothing across holders or contents). -/
theorem attitudes_independent (A : AttDoc) (h : WellFormedAtt A = true) (S : VE.Structure.{u})
    (hS : S.Admissible A.E) (k k2 : Key) (hk : k ∈ keys A) (hne : k ≠ k2) (hnp : (k, k2) ∉ framePairs A)
    (vs : List S.Carrier) (hvs : VE.TupleTyped S k.sorts vs)
    (hfact : k.mode = .knows → contentAt (A := A) ⟨S, fun _ _ => False⟩ k vs) :
    ∃ J : Key → List S.Carrier → Prop, Intended A ⟨S, J⟩ ∧ J k vs ∧ ¬ J k2 vs
/-- R 5's collapse: with premise 3, `(knows ∧ intends) ∨ thinks w` on one subject is `thinks w`. -/
theorem guard_collapse (A : AttDoc) (h : WellFormedAtt A = true) (m : AttModel.{u} A) (hI : Intended A m)
    (Γ : List String) (ρ : VE.Valuation m.S) (ck ci ct : Cond) (k kt : Key) (w : Word)
    (hk : ck.key A Γ = some k) (hkt : ct.key A Γ = some kt) (hm : k.mode = .knows) (hmt : kt.mode = .thinks w)
    (hs : sameSubject k kt = true) (hh : ck.holder = ct.holder) (hsl : ck.slot = ct.slot) :
    AFormula.denote A m Γ ρ (.or (.and (.att ck) (.att ci)) (.att ct)) ↔ AFormula.denote A m Γ ρ (.att ct)
theorem atLeast_refl (σ : Scale) (a : Word) : σ.atLeast a a = true
theorem framePairs_transitive (A : AttDoc) (h : WellFormedAtt A = true) (k1 k2 k3 : Key)
    (h12 : (k1, k2) ∈ framePairs A) (h23 : (k2, k3) ∈ framePairs A) (hne : k1 ≠ k3) : (k1, k3) ∈ framePairs A
end VE.Attitudes
```

(`wellFormedBody` and `aWellFormedBody` stand for the bodies AT-0 writes in the stub from the conjuncts listed in
the docstring. No comment above uses a word `lean/audit.py` forbids.)

Proof notes. Conservativity: extend by the empty attitude relations (every frame premise has a false antecedent);
the other direction restricts (`restrict_admissible`) and uses `old_formula_invariant`, which needs `names_fresh`.
`mistaken_belief_admissible`: take `J` the set of `(k′, vs)` with `(k, k′) ∈ framePairs A` or `k′ = k`; no frame
pair has a `knows` key as its target (`entailsMode`), so factivity is never triggered; `framePairs_transitive`
closes the third conjunct. `attitudes_independent` is the same construction plus `hnp`. `guard_collapse` is premise
3 through `frame_iff_intended`. `framePairs_transitive` needs `atLeast` transitive, which the closure gives within
`words.length` rounds (pairs are between words, `WellFormedAtt`).

Fixtures (`Examples.lean`, `#guard` on executable checks over finite models):

- **F-AT1 (u0165.s01 with u0173.s01).** `E`: sorts `claude_instance`, `situation`; base `mass_casualty_weapon_uplift
  (situation)`; regulated `weapons_uplift_permitted (claude_instance, situation)`, a permission, act "{0} do the
  weapons uplift in {1}". One rule, sign false, guard `or (and (att knows) (att intends)) (att (thinks "quite
  likely"))`, each condition with holder `var 1`, slot `("situation", var 0)`, content
  `unary "mass_casualty_weapon_uplift" (var 0)`. Expected: keys named `attitudes__knows__1`,
  `attitudes__intends__1`, `attitudes__thinks_quite_likely__1`; two frame premises (`attitude:factive`,
  `attitude:entails` knows → thinks quite likely). One instance `c`, one situation `s`:
  - M1, category false, thinks true: frame holds, guard holds (the audit's case).
  - M2, category false, knows and thinks true: frame fails (factive).
  - M3, category true, knows true, thinks false: frame fails (entails).
  - M4, category true, no attitude: frame holds, guard fails (u0173.s04's unknowing contribution).
- **F-AT2 (two categories, u0165.s01 and u0165.s07).** Contents for two case atoms: six keys, `__1` and `__2` per
  mode, and no frame pair across contents (`attitudes_independent`'s instance).
- **F-AT3 (degree order).** A document using "very likely" and "quite likely" on one content with the declared pair
  ("very likely", "quite likely"): one `attitude:entails` premise in that direction, none in the other.
- **F-AT0 (conservative).** F-AT1 with the attitude conditions removed: no key, no frame, `envAtt = E`.

Deleted, not duplicated: nothing deleted. `Act`, `dedup` and content identity are `reports@0`'s.

Shared files: none hand-written. In-flight overlap: none (new directory).

Bytes unlocked: 0 (nothing calls the code).

Done when: the files build with standard axioms only, the fixtures `#guard`, `lean/ATTITUDES.md` lists every theorem
in plain words, the audit passes, and the gate passes (no answer can change).

### AT-2. The norm-defaults route under the frame (Lean, 4–5 h)

Files: `lean/VE/Attitudes/Route.lean` and `RouteExamples.lean` (new). Generated as in AT-1. No hand-written shared
file.

```lean
import VE.Attitudes.Theorems
import VE.NormDefaults.Layered

namespace VE.Attitudes
-- the opens of `VE/NormDefaults/Status.lean`, where `SettledAs` is stated, plus that namespace itself
open VE.Norms VE.Route VE.NormDefaults
open VE.NormDefaults.Wire (BaseAdmissibleX ConflictFreeX UndecidedAtX LayeredU)
universe u

/-- The norm-defaults view of an attitudes document. -/
def toU (A : AttDoc) (unspec : List String) : Option UDoc := (toNorms A).map (fun D => ⟨D, unspec⟩)

/-- SETTLED over the bases that also satisfy `X` (the counterpart of `UndecidedAtX`, which exists). -/
def SettledAsX (U : UDoc) (X : List VE.Formula) (B : VE.Structure.{u}) (r : Regulated) (vs : List B.Carrier)
    (b : Bool) : Prop :=
  ∀ F : FillTables U B, BaseAdmissibleX U X (withFill U B F) →
    ((outcomeBase (fill U) r.name).denote (withFill U B F) (tupleVal vs) ↔ b = true)

/-- At a base whose relations satisfy the frame, SETTLED with and without the frame agree: the frame mentions no
    `unsaid__` table, so no filling changes it. -/
theorem settled_frame_agree (A : AttDoc) (h : WellFormedAtt A = true) (U : UDoc) (hU : toU A U.unspec = some U)
    (B : VE.Structure.{u}) (hX : Sat B (framePremises A)) (r : Regulated) (vs : List B.Carrier) (b : Bool) :
    SettledAs U B r vs b ↔ SettledAsX U (framePremises A) B r vs b
theorem undecided_frame_agree (A : AttDoc) (h : WellFormedAtt A = true) (U : UDoc) (hU : toU A U.unspec = some U)
    (B : VE.Structure.{u}) (hX : Sat B (framePremises A)) (r : Regulated) (vs : List B.Carrier) :
    UndecidedAt U B r vs ↔ UndecidedAtX U (framePremises A) B r vs
/-- The layered source of an attitudes document carries exactly the frame as its extra premises. -/
def FrameSource (A : AttDoc) (L : LayeredU) : Prop :=
  L.route = "attitudes@0" ∧ L.labelled = (frameLabels A).zip (framePremises A) ∧
    (toU A L.U.unspec).map (·.D) = some L.U.D
theorem frameSource_X (A : AttDoc) (L : LayeredU) (hL : FrameSource A L) : L.X = framePremises A
/-- Conflict-freedom under the frame is `layered_conflict_sound`, unchanged. -/
theorem att_conflict_sound (A : AttDoc) (L : LayeredU) (hL : FrameSource A L) (packages : Lean.Json)
    (hc : VE.NormDefaults.Wire.conflictFreeX L packages = true) : ConflictFreeX.{u} L.U (framePremises A)
/-- The audit's case as a route fact: at a base satisfying the frame where the rule's guard holds, the rule on `r`
    with sign `false` settles `r` false; F-AT1's M1 is an instance. -/
theorem mistaken_belief_settled (A : AttDoc) (h : WellFormedAtt A = true) (U : UDoc)
    (hU : toU A U.unspec = some U) (B : VE.Structure.{u}) (hX : Sat B (framePremises A)) (r : Regulated)
    (vs : List B.Carrier) (hdec : VE.NormDefaults.decidesAt U B r vs false) : SettledAsX U (framePremises A) B r vs false
end VE.Attitudes
```

(`VE.NormDefaults.decidesAt` stands for the existing "a rule decides `r` at this tuple" fact the status evidence
uses (`settled_of_table3`, `settled_of_enumeration`); AT-0 replaces it with the exact name or states it.)

Fixtures (`RouteExamples.lean`): F-AT1's points through the strict route's status evaluator with the frame check:
M1 SETTLED no; M4 UNDECIDED; M2 and M3 refused (`InvalidModel: attitude:factive`, `InvalidModel:
attitude:entails`). F-AT1 is conflict-free under the frame.

Deleted, not duplicated: no second status or conflict semantics; `SettledAsX` is the one missing counterpart of
`UndecidedAtX` and is defined from the same parts.

Shared files: none hand-written. In-flight overlap: `rd-9-int` edits norm-defaults files; this batch only imports
them. If `rd-9-int` changes `LayeredU`'s fields, AT-2 rebases (one structure literal).

Bytes: 0.

Done when: builds, audit passes, fixtures `#guard`, `lean/ATTITUDES.md` updated, gate passes.

### AT-3a. Wire, service mode and response shape (Lean, 5–6 h)

Files (new): `lean/VE/Attitudes/Wire.lean` (decoder of the `attitudes` environment block and of attitude guard
nodes; elaboration of the environment and norms JSON; the `LayeredU` constructor `decodeAttitudesU`),
`lean/VE/Attitudes/Run.lean` (`VE.Attitudes.Run.runCaseReported`, case kinds `attitudes-elaborate`,
`attitudes-status`, `attitudes-conflict`, `attitudes-report`), `lean/ResponseShape/Schemas/Attitudes.lean`,
`lean/ResponseShape/Encoders/Attitudes.lean`.

Wire (structured content; JSON never carries `null`):

```text
environment.attitudes = { "holders": [sort, …], "scale": [[word, word], …], "decided_by": token }
guard node             = { "attitude": { "holder": term, "mode": "knows" | "thinks" | "believes" | "wants"
                           | "intends" | "says", "degree": word (only with "thinks"),
                           "slot": { "sort": sort, "term": term } (optional), "content": formula } }
```

`attitudes-elaborate` answers the generated predicates (name, sorts, key, wording template, open-term record), the
frame (label, formula) and the elaborated guards; `attitudes-status` answers a point's status with the frame checked
on the model first; `attitudes-conflict` and `attitudes-report` are the layered route's with `X` the frame.

Statements:

```lean
namespace VE.Attitudes.Run
/-- The answer is exactly the encoding of the elaboration of the case's own decoded document. -/
theorem attitudes_wire_acceptance (j : Lean.Json) (A : AttDoc) (hd : VE.Attitudes.Wire.decodeAttDoc j = .ok A)
    (ans : Lean.Json) (hr : runCaseReported j = ans) (hk : j.getObjValD "kind" = .str "attitudes-elaborate") :
    ans = VE.Attitudes.Wire.encodeElaboration A
/-- A replayed SETTLED or UNDECIDED status holds of the decoded document at the decoded model, and that model
    satisfies the frame; UNKNOWN claims nothing. -/
theorem attitudes_status_sound (j : Lean.Json) (d : StatusDataAtt j) (hr : replayStatusAtt j = .ok d) :
    Sat d.M.asStructure (framePremises d.A) ∧
    (∀ b, d.status = .settled b → SettledAsX.{0} d.U (framePremises d.A) d.M.asStructure d.r d.tuple b) ∧
    (d.status = .undecided → UndecidedAtX.{0} d.U (framePremises d.A) d.M.asStructure d.r d.tuple)
end VE.Attitudes.Run

namespace VE.Service
theorem runMode_attitudes (j : Lean.Json) : runMode .attitudes j = VE.Attitudes.Run.runCaseReported j
end VE.Service

namespace ResponseShape.Encoders.Attitudes
theorem runCaseReported_fits (j : Lean.Json) :
    ResponseShape.Fits ResponseShape.Schemas.Attitudes.shape (VE.Attitudes.Run.runCaseReported j)
end ResponseShape.Encoders.Attitudes
```

(`StatusDataAtt` and `replayStatusAtt` are the batch's new definitions, `VE.NormDefaults.Wire.StatusData` and
`replayStatus` with the decoded attitudes document `A`, its `UDoc` `U` and the frame check on the model added;
`ResponseShape.Fits` stands for the relation the other encoder theorems use, and AT-0 copies its exact name from
`lean/ResponseShape/Encoders/Discourse.lean`.)

Fixtures: F-AT1 as wire cases, each case kind; malformed cases (unknown mode, `degree` on a non-`thinks` mode, a
slot term of the wrong sort, a holder of a non-holder sort, a content with a quantifier, a generated name over 64
bytes) refused with their diagnostic in the spec's order.

Shared hand-written files: `lean/VE/Service/Protocol.lean` (a `Mode` constructor, its name, the `modes` list, one
`runMode` case, the `runMode_attitudes` equation; all additive), `ve/backends/service_schema.py` (`MODES`: one
name), `ve/assurance-manifest.json` (pins of the new JSON decoder, reviewed by hand), `conformance/binding_probes.py`
(`BUILDERS`: a probe for the new binding), `ROADMAP.md` (the trust-cost line, VISION rule 4). Generated:
`ve/backends/lean_service_schema/attitudes.json` (`tools/response_schemas.py --write`), `lean/ResponseShape.lean`,
`lean/ResponseShape/Audit.lean`, `docs/spec/assurance-manifest.md`, `lean/checkers.lock`, `docs/trust-baseline.json`
(growth needs `trust_map.py --write --reason` and a DRI signature, ruling D3).

In-flight overlap: `lf-16e` and `qa-q2` both add modes to `Protocol.lean` and schemas; start after both merge, or
rebase onto them (additive lines). `fix-main-relay` touches `service_schema.py`; after it merges.

Bytes: 0.

### AT-3b. Relay, document hook and tests (Python, 4–5 h)

Files (new): `ve/attitudes.py` (sends the case with `rows` from `ve/backends/relay.py`; binds the answer: every
generated name is in the answer's environment, every rule id and unit id names one in the request, every frame label
is one of the two, no row is empty or extra; anything else is `CheckerUnavailable`), `tests/test_attitudes_lean.py`
(the route's own documents: F-AT1 to F-AT3 and the seven hard constraints), `tests/test_attitudes_answer.py` (fuzz:
each member of a genuine answer dropped, emptied, retyped, duplicated or reordered, an index pushed out of range, one
and two faults at a time; every mutant is `CheckerUnavailable` or changes nothing shown).

Shared hand-written files: the `ve document` dispatch (Python `ve/document*.py` today; Lean's `document` mode if
`lf-16e` has moved it, as AT-0 records), `tools/layer_policy.py` (the layer of `ve/attitudes.py`). Generated:
`tests/data/route-cases.jsonl` (recorded by `tests/route_case_recorder.py`), `.importlinter`
(`tools/check_python_layers.py --write`), `tools/gate-collection.json`.

Seeded bug (Python is the only language this batch changes; recorded with file and failing test): the binding check
that a frame label is one of the two accepts any label; `tests/test_attitudes_answer.py` must fail, then the check is
restored.

In-flight overlap: `lf-16e` (document dispatch). Start after it merges.

Bytes: 0 by itself; AT-6a measures.

### AT-6a. Pilot: the strict companion with typed attitudes (pilot tooling, 3 h)

In `readings/all-strict.ve.md`, replace AT-0p's fourteen open terms with attitude conditions (D2's guard), declare
`attitudes@0` and `environment.attitudes = {"holders": ["claude_instance"], "scale": [], "decided_by":
"unresolved_decider"}`. Re-run the unspecified probe and the conflict check. Report, measured: the points of the
seven rules (expected: the audit's case SETTLED no; unknowing UNDECIDED; impossible points refused), the generated
open terms (expected 21), predicates used, time (one run, not a comparison), `DELTA` against AT-0p's run. No model
calls. The main translation is unchanged until AT-6b.

Bytes (**estimate**): 0 claimed; the typed form of 874 B on the companion.

### AT-4. The readings chain under the frame (Lean and Python, 5–6 h)

Files: `lean/VE/Attitudes/Readings.lean` (new); the readings route decoder's one call to `decodeAttitudes` (shared,
hand-written, in the readings wire file AT-0 names); `ve/readings.py` passes the `attitudes` block through only.

```lean
import VE.Attitudes.Route
import VE.Readings.SupExtra

namespace VE.Readings
-- the opens of `VE/Readings/SupExtra.lean`
open VE.Rights (RightsDoc correlate)
open VE.Compose (BaseAdmissibleP ConflictFreeP)
universe u

theorem transfers_append (D : Doc) (Q₁ Q₂ : List VE.Formula) (Q₁c Q₂c : Choice → List VE.Formula)
    (h₁ : Transfers.{u} D Q₁ Q₁c) (h₂ : Transfers.{u} D Q₂ Q₂c) :
    Transfers.{u} D (Q₁ ++ Q₂) (fun c => Q₁c c ++ Q₂c c)
/-- The frame is over the shared base vocabulary (generated names are fresh, not choice symbols), so every choice
    reads it unchanged. -/
theorem frame_transfers (N : NDoc) (Att : VE.Attitudes.AttDoc) (hA : VE.Attitudes.WellFormedAtt Att = true)
    (hN : WellFormedND N = true) (hF : WellFormedDoc (fillDoc N) = true) (hs : superposable (fillDoc N) = true)
    (hsh : ∀ φ ∈ VE.Attitudes.framePremises Att, φ.WellFormed (sharedEnv (fillDoc N)) []) :
    Transfers.{u} (fillDoc N) (VE.Attitudes.framePremises Att) (fun _ => VE.Attitudes.framePremises Att)
theorem att_nd_superpose_conflict_free (N : NDoc) (Att : VE.Attitudes.AttDoc)
    (hA : VE.Attitudes.WellFormedAtt Att = true) (hN : WellFormedND N = true)
    (hF : WellFormedDoc (fillDoc N) = true) (hs : superposable (fillDoc N) = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true)
    (hsh : ∀ φ ∈ VE.Attitudes.framePremises Att, φ.WellFormed (sharedEnv (fillDoc N)) [])
    (A : Choice) (hAc : ∀ x ∈ A, (candidate N.D x.1 x.2).isSome) :
    ConflictFreeP.{u} (correlate (sup (fillDoc N)).1)
        (slotUnder (fillDoc N) A ++ (VE.NormDefaults.fillPremises (supU N) ++ VE.Attitudes.framePremises Att)) ↔
      ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) →
        ConflictFreeP.{u} (correlate (choiceDoc (fillDoc N) c).1)
          (VE.Rights.limPremises (choiceDoc (fillDoc N) c).1 ++
            (VE.NormDefaults.fillPremises (choiceU N c) ++ VE.Attitudes.framePremises Att))
end VE.Readings
```

`att_nd_superpose_all` and `att_nd_superpose_countermodel` follow `nd_superpose_all` and the countermodel theorem
the same way (AT-0 writes them out from `superpose_all_extra` and `superpose_countermodel_extra`); the enumerated
route checks each choice with the frame in its base premises. Every existing readings fixture answers byte-identically
(the existing theorems are the `Att` without conditions, `att_conservative_doc`).

Shared hand-written files: the readings wire decoder (one call), `ve/readings.py` (pass-through). Generated: as AT-1,
plus recorded route cases.

In-flight overlap: `lf-14d` (reading plans and verdicts move to Lean; `ve/readings.py` becomes a relay), `rd-9-int`
(soft norms with reading sets), `lf-16e` (Lean document mode for `readings@1`). Start after all three merge.

Bytes: 0 by itself; AT-6b measures.

### AT-6b. Pilot: the main translation with typed attitudes (pilot tooling, 3 h)

The same change as AT-6a in `translation.ve.md` (three "should" reading sets, superposed route). Report, measured:
conflict status over the eight choices; the denial and claim-to-be-human conclusions (expected unchanged); the seven
rules' points; open terms; predicates; the companion probe's decided units. Ask the next audit to sample the seven
units. If the scope design has landed, u0173.s01 is attached to the seven rules and claimed (263 B, **estimate**).

### AT-5. English in Lean (Lean and Python, 5–6 h)

Files: `lean/VE/Attitudes/Words.lean` (new: the verb, synonym and refusal table for the six modes, with the
reasons now in `ve/report_english.py`), `lean/VE/Attitudes/English.lean` (new: wording templates for generated
predicates, composed from the content predicate's own template; the frame lines; the glossary line of each degree
word), the Lean English grammar's admission of the 3.7 rows (files in `lean/VE/EnglishGrammar/` that AT-0 names).

```lean
namespace VE.Attitudes
/-- Rendering then reading an attitude condition gives it back, under the document's lexicon. -/
theorem att_english_roundtrip (A : AttDoc) (h : WellFormedAtt A = true) (Γ : List String) (c : Cond)
    (hc : c.key A Γ ≠ none) : readCond A Γ (renderCond A Γ c) = .ok c
/-- Each refused form of 3.7 has no reading and its rewrites have exactly one each. -/
theorem refused_have_rewrites (A : AttDoc) (s : String) (r : Refusal) (hr : refusalOf A s = some r) :
    readCond A [] s = .error r.code ∧ ∀ s2 ∈ r.rewrites, (readAll A [] s2).length = 1
end VE.Attitudes
```

(`readCond`, `renderCond`, `readAll`, `refusalOf` and `Refusal` (a code and its rewrites) are the batch's new
definitions; `readAll` lists every derivation, as the all-derivations gate does.)

Deleted: `_VERBS`, `_SYNONYMS` and `_REJECTED` in `ve/report_english.py`; it reads the exported table instead. No
second verb table remains.

Shared files: the English grammar files; the export's generator (the `english-codes` entry if its format can carry
the table, else a new `attitude-words` entry in `tools/regen_generated.py`, which is hand-written); the generated
`lean/VE/EnglishGrammar/Fixed/*.lean` and `ve/english_grammar/LOCK.json`, whose generator refuses a changed hashed
file without a new `--actions-version` (a person decides).

In-flight overlap: `qa-q2` (Lean-rendered English answers). Start after it merges.

Bytes: 0; makes the 3.1 sentences writable in English.

### AT-7. Nested conditions and "knows whether" (Lean, 5–6 h)

Two levels: a content may mention a generated level-1 atom (an attitude of someone named by a constant or by the
slot), so "the user says that the user intends to harm" (u0149.s03) and "a user who wants to know whether they are
talking to a human" (u0080.s04) elaborate in two rounds. "X knows whether P" is sugar for "X knows that P or X knows
that it is not the case that P", one reading. The frame is generated per level; every premise stays first-order and
universal.

```lean
namespace VE.Attitudes
/-- Two-level documents: level-2 contents are formulas over `envAtt` of level 1. Conservative over level 1. -/
theorem nested_conservative (A : AttDoc2) (h : WellFormedAtt2 A = true) (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (envAtt A.lower) []) (hφ : φ.WellFormed (envAtt A.lower) []) :
    VE.Entails.{u} (envAtt2 A) (Γ ++ framePremises2 A) φ ↔
      VE.Entails.{u} (envAtt A.lower) (Γ ++ framePremises A.lower) φ
/-- A nested attitude is free unless the frame relates it: saying that one intends implies nothing about intending. -/
theorem says_not_intends (A : AttDoc2) (h : WellFormedAtt2 A = true) : NestedIndependent A
end VE.Attitudes
```

(`AttDoc2`, `WellFormedAtt2`, `envAtt2`, `framePremises2` and `NestedIndependent` are the batch's new definitions:
`AttDoc2` is an `AttDoc` for level 1, `lower`, and the level-2 conditions over `envAtt lower`.)

Profile: `attitudes@1` (a new version admits more documents; `attitudes@0` documents keep their meaning,
`nested_conservative` at level 1 alone). Bytes: 0 now; up to 1,070 B over seven units when their co-blockers land
(**estimate**). Shared files: none beyond AT-3a's (the decoder gains a field). Needs AT-4.

### E3. "We want Claude to X" (experiment, 3 h)

Pre-registered. Sample 40 of the 183 author-attitude units (R 2.4) with `random.Random("attitudes-E3")` over the
unit ids sorted. Readers as E1, each shown the sentence with its paragraph, asked: "Does this sentence (a) only say
what Anthropic wants, (b) tell Claude what to do, or (c) both?". One independent audit of the same 40.

- If at least 32 of 40 readers choose (b) or (c) on at least 30 units, AT-8 records such units as a reading set
  {report; report and soft rule}, with the IDE showing both. If at most 8 of 40 do, AT-8 records the report alone.
  Otherwise each unit is a reading set.
- Nothing about the soft rule's force is concluded (weighing owns it).

### AT-8. `reports@0` units in norm documents (Lean and Python, 5–6 h)

Top-level report units beside rules: the attitudes route decodes them with `reports@0`'s own decoder and adds their
signed premises `VE.Reports.premises` to the document's asserted premises. No `reports@0` statement changes: the
gate `reports_gate_sound` stays as it is, and the combination is admitted only on the attitudes route.

```lean
namespace VE.Attitudes
/-- Report premises in a norm document change old-language consequence by exactly their forced disequalities
    (`VE.Reports.reports_no_leak`), and the rules' statuses not at all when no guard mentions a report key. -/
theorem reports_in_norms_conservative (A : AttDoc) (D : VE.Reports.ReportDoc)
    (hD : VE.Reports.WellFormedReports D = true) (hsep : ReportKeysUnused A D) (U : VE.NormDefaults.UDoc)
    (hU : toU A U.unspec = some U) (B : VE.Structure.{u}) (r : VE.Norms.Regulated) (vs : List B.Carrier) (b : Bool) :
    SettledAsX U (framePremises A) B r vs b ↔ SettledAsX U (framePremises A ++ VE.Reports.premises D) (expandR D B) r vs b
end VE.Attitudes
```

(`ReportKeysUnused` and `expandR` are this batch's: no guard mentions a report predicate, and the expansion of a base
with report relations.) Owner: the composition attribution.md 11.3 defers; DRI decision with the attribution owners
before build, so that one owner remains. Bytes (**estimate**): upper bound about 31 kB over the 183 units (183 × 169
B); the expected gain is far lower and depends on E3 and on the contents' own features.

### AT-9. Numeric bands on the scale (Lean, 3–4 h, on risk stage B's trigger)

`Scale` gains optional declared ranges per word; a declared range orders words it covers (a range wholly above
another implies the pair). Risk stage B reads its bands from `VE.Attitudes.Scale` instead of declaring its own.
Theorem: `bands_order_sound` (a declared pair agrees with the ranges). Bytes: 0 on the pinned pilots.

### E4. Claims as objects for honesty norms (experiment, 4–5 h)

Pre-registered. A stub profile with a sort of claims, one constant per content the document names, and a generated
`holds_<claim>` table restricted to first-order contents over `E` (no claim about a claim, so no self-reference).
Formalise 12 honesty units (u0112.s01 to s07, u0113.s02, u0114.s03, u0115.s01, u0118.s01, u0120.s04) in the stub.

- Success bar: the stub's conservativity statement elaborates; an independent audit finds at least 8 of 12 faithful;
  no unit needs a claim about a claim. Then a profile plan follows.
- Failure: the honesty section stays UNFORMALISED for this reason, recorded in the ledger.
- Opportunity: part of the 13,379-byte honesty section (R 2.4), co-blocked by speech acts and causation.

## 5. Dependencies and merge conflicts

| Batch | Waits for | Hand-written shared files | Generated files (regenerate) |
|---|---|---|---|
| AT-0p | — | (pilot directory only) | — |
| AT-1, AT-2 | AT-0 | none | `lean/VE.lean`, `lean/VE/Audit.lean`, frozen inventory, axioms, statements |
| AT-3a | `lf-16e`, `qa-q2`, `fix-main-relay` | `lean/VE/Service/Protocol.lean`, `ve/backends/service_schema.py`, `ve/assurance-manifest.json`, `conformance/binding_probes.py`, `ROADMAP.md` | response schema, `ResponseShape` roots and audit, assurance doc, checker pins, trust baseline (signed) |
| AT-3b | AT-3a; `lf-16e` | document dispatch (Python or Lean), `tools/layer_policy.py` | route cases, `.importlinter`, gate collection |
| AT-4 | `lf-14d`, `rd-9-int`, `lf-16e` | readings wire decoder (one call), `ve/readings.py` | as AT-1, route cases |
| AT-5 | `qa-q2` | English grammar files, `ve/report_english.py`, possibly `tools/regen_generated.py` | English grammar lock (needs a person's `--actions-version`), codes |
| AT-7 | AT-4 | AT-3a's decoder (own file) | as AT-1 |
| AT-8 | E3; DRI decision | AT-3a's decoder (own file), `ve/attitudes.py` | as AT-1 |
| AT-9 | risk stage B trigger | `lean/VE/Attitudes/Scale.lean` (own), risk stage B's files | as AT-1 |

How conflicts are avoided: every Lean batch writes new files under `lean/VE/Attitudes/`; the only hand-written shared
Lean file is `Protocol.lean` (additive lines, after its two in-flight editors merge) and one decoder call in AT-4.
Generated inventories are never hand-edited or hand-merged (ruling R12; `tools/regen_generated.py --resolve`
finishes a merge whose only conflicts are generated). Overlap is checked before each batch with
`git diff --name-only main...<branch>` against the in-flight branches named above.

Sibling designs: **scope** (u0173.s01 attached to the seven rules, needed for its 263 B), **act-phrases** ("intends
to VP", "wants X to VP"), **weighing** (u0173.s02's "more holistic and nuanced prioritization", u0145.s05),
**quantities** (vague degrees other than likelihood, "serious uplift"; this plan's scale covers likelihood words
only), **events-time-causation** (u0173.s04's "contributing", "deceive into thinking").

## 6. Expected effect per batch

All **estimates** until the pilot batches measure them.

| Batch | Claimed bytes | Audit-verifiable bytes | Answers |
|---|---:|---:|---|
| AT-0p | 0 | 874 (7 units) | 7 audit-case points UNDECIDED → SETTLED no; open terms 33 → 46 |
| AT-0 to AT-3b | 0 | 0 | none (no pilot uses them yet) |
| AT-6a | 0 | 874 typed (companion) | impossible points refused; open terms 46 → 53 (21 generated) |
| AT-4 + AT-6b | 0, or 263 with the scope design | 874 typed (main) | the "intentionally" readings do not separate (`guard_collapse`) |
| AT-5 | 0 | 0 | the sentences of 3.1 writable in English |
| AT-7 | 0 now; up to 1,070 | — | — |
| AT-8 | 0 until E3; upper ≈ 31 kB | — | — |
| AT-9 | 0 | — | — |
| E4 | research | — | part of 13,379 B (section) |

NORTH-STAR row 8 (0.1920 from tags) recomputed on this basis: the buildable part's upper bound is about 0.036
(5 × 1,333 / 184,893; R 2.8).

## 7. Not claimed, open questions, risks

- **Not claimed:** that Claude knows or thinks anything in any case; any threshold for "quite likely"; any coverage
  before the pilot batches measure it; that proxy readers stand for human readers.
- **Open (for AT-0):** the exact `LayeredU` constructor for a strict document; where the point replay checks the
  frame; the response-shape relation's name; whether the `english-codes` generator can carry the word table; the
  readings wire decoder's hook point after `lf-14d`.
- **Open (for the DRI):** AT-8's owner (attribution or attitudes); how the residual displays 21 generated open
  terms; whether "is aware that" may be an input synonym of "knows that" (only if E2-style agreement is shown; else
  refused with that rewrite).
- **Risks:** the readings route is being rebuilt (AT-4 may need a second statement pass); E2 may reject premise 3,
  in which case `guard_collapse` is dropped and the "intentionally" readings stay a reading set; one slot may be too
  narrow for the honesty and intentions sections (AT-7 and E4 measure before widening it).

## 8. Review checklist (for AT-0)

- `Intended` says what the attitude words mean and nothing more (D-A4, D-A9): no closure, no introspection,
  nothing from intending, wanting or saying.
- `mistaken_belief_admissible` has no hypothesis about the content's truth, and its conclusion is about the given
  structure `S` (no existential carrier mismatch, the deviation `lean/REPORTS.md` records for `holder_atom_free`).
- `att_old_language_conservative` has no hypothesis that the frame is empty.
- Every frame premise is universal with a quantifier-free body (`frame_universalQF`), as the norm-defaults evidence
  requires.
- Generated names cannot collide with `reports__`, `unsaid__`, `soft__`, `risk__` or `ve__` names (prefix
  `attitudes__`; `names_fresh` covers declared names, and the route checks the generated families of the profiles it
  combines).
- E1's pairs and E2's decisions are written into `table` and `entailsMode` before PASS.
- The 3.7 table gives every refused form two or more rewrites with one reading each.
- No Lean comment uses a word `lean/audit.py` forbids; no theorem name has a prime or exceeds about 57 characters
  with its namespace.
