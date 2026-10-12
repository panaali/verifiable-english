# Quantities: plan (counts and proportions; comparisons and graded words)

> **Status.** Draft 1, 2026-10-12, branch `design/quantities` from `main` at `49de179e`. DRI research wave: docs only,
> no product code, no tests, no generated file touched, no model calls. Research and measurements:
> [docs/research/quantities.md](../research/quantities.md) (cited as R and a section number). This plan builds R6's
> recommendation: a pilot repair with the existing language, then two tracks, **A** (`cardinality@0`: counts,
> proportions, rounding) and **B** (`scales@0`: comparatives, equatives, graded words). Every number is measured (method
> in R2.1) or marked **estimate**. The cross-plan review of the seven research-wave plans runs before any spec or
> build and may move the shared pieces of section 10.

## 0. Summary

| # | Batch | Hours | Owner | Moves a pilot number? |
|---|---|---:|---|---|
| QT-0p | Pilot repair with the existing language | 2 | pilot runner | yes: C 0–128 B, U 0–76 B (**estimate**) |
| QT-0 | Statement spec, Lean stub, statement review | 3–4 | planner | no |
| QT-A1 | Lean core of `cardinality@0`: counts, regions, erasure, soundness | 5–6 | Lean | no |
| QT-A2 | Lean: "rounds to" and "percent of" | 3–4 | Lean | no |
| QT-A3 | Lean wire and service mode `cardinality`, shapes, documents, certificates | 5–6 | Lean | no |
| QT-A4 | Python relay, document hook, fuzz tests; delete `ve/surface/count.py` | 4–5 | Python | no |
| QT-A5 | News and paper measurement | 2–3 | pilot tooling | news 0–194 B |
| QT-E | Quantity English into Lean's engine (english-lean E3's quantities step) | 2 × 5–6 | english-lean owner | no |
| QT-A6 | Count, proportion and rounding wordings in Lean; refusals with rewrites | 4–5 | Lean | no (readability) |
| QT-A7 | Declared exact unit conversions (on trigger) | 4–5 | Lean, Python | no |
| QT-B1 | Lean core of `scales@0`: dimensions, graded words, premises, degrees | 5–6 | Lean | no |
| QT-B2 | Scale premises on the norm routes; wire, mode `scales`, coherence of decisions | 5–6 | Lean, Python | no |
| QT-B3 | Scale and graded-word wordings in Lean; refusals | 4–5 | Lean | no |
| QT-B4 | Pilots: dial, trust levels, hard constraints, UDHR equalities | 3 | pilot tooling | C 0–781 B new, 826 B faithful; U 0–191 B |
| QX-1 | Experiment: "most", "many", "multiple", bare "16 of the 18" | 2–3 | experiment runner | decides wordings |
| QX-2 | Experiment: hard-constraint decomposition audit | 2 | experiment runner | gates QT-B4's 826 B |
| QX-3 | Experiment: inferences with proportional grades | 2–3 | experiment runner | decides premises |
| QX-4 | Research experiment: the 1,000-users passage | 4 | planner, Lean stub | research |
| QS-1 | Shared ordered-scale module (proposal for the synthesis review) | 3–4 | set by synthesis | no |

Order: QT-0p and QX-1 to QX-3 can start now; QT-0 next; then track A (QT-A1 to QT-A5) and QT-B1 in parallel; QT-B2
waits for `lf-16e`, `lf-14d` and `rd-9-int`; English waits for QT-E.

## 1. Scope, owners and rules

### 1.1 In scope, and what siblings own

In scope: counts over sorts declared finite; proportions with literal thresholds ("more than half", "at least 1 in
1,000"); "n of the m" beyond W6a's caps; exact rounding and percent-of over W6a quantities; thousands separators;
declared exact conversions between unit tags; comparatives, equatives and graded words on declared dimensions; the
coherence of a decider's grade decisions; refusals and rewrites for vague quantity words.

Not in scope, by owner: likelihood words and their order (**attitudes**, `VE.Attitudes.Scale`); ranks, the strength of
a priority step, delegated switches, "outweighs" (**weighing**); days, weeks as calendar units, months, time-indexed
values such as "the rate before the decision" (**events-time-causation**); act phrases such as "pay for work"
(**act-phrases**); which sentence a quantifier scopes over (**scope**); statistics, confidence intervals, real-valued
physics (**math-evidence**); the duty in "has the right to equal pay" (**rights**, merged).

### 1.2 One owner per piece of logic

| Piece | Owner | This plan |
|---|---|---|
| Linear integer arithmetic and its certificates | `order@0` (`VE.Order.Tableau`: Farkas combinations, cuts) | reused through erasure; no second arithmetic checker |
| Unit tags, decimals, W6a typing, W6a certificates | `VE.Time.*` | reused unchanged; `cardinality@0` wraps W6a statements |
| W6a counting sugar ("at least 8") | `VE.Time.Count` (`atLeast`, `expand_atLeast_iff`) | not duplicated: `count_atLeast_agree` proves the new count atoms agree with it; the Python copy `ve/surface/count.py` is deleted (QT-A4) |
| Counts and region arithmetic | **new** `VE.Cardinality` | one owner |
| Comparison, equatives, graded words, their premises | **new** `VE.Scales` | one owner; QS-1 proposes one module for every declared order |
| Acyclicity of a declared order | `VE.Route.kahn`, `DagAcyclic` | reused for the grade order |
| Open-term records (`decided_by`, factors, precedents) | W2 schema ([document.md](document.md)) | graded words reference W2 records; no second record type |
| Extra base premises on norm routes | `LayeredU.X`, `BaseAdmissibleX` (norm-defaults) | reused; one hook shared with attitudes (section 6) |
| Quantity English (reading, rendering, refusals) | Lean's English engine after english-lean E3 | no new Python English; `ve/surface/time.py`'s parser and renderer leave with QT-E |
| Certificate search | untrusted: Python's existing `prove_quantity` on Lean's regenerated problem | no Python semantics; Lean checks every certificate and countermodel |
| Profile registration | Lean `VE.Compose.Dispatch` | Python's `ve/profiles.py` row is the existing duplicate; one row each, not widened |

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
| "Exactly 16 of the 18 FOMC policymakers expect a further increase." | #policymakers = 18 and #(policymakers expecting a further increase) = 16 |
| "At least 16 of the 18 FOMC policymakers …" / "At most 2 of the 18 …" | ≥ / ≤ instead of = for the second count |
| "More than half of the users are curious." | 2 × #(curious users) > #users |
| "At least 1 in 1,000 of the users intend harm." | 1,000 × #(users intending harm) ≥ #users |
| "The number of false approvals out of the number of scored decisions rounds to 0.296." | (2 × 296 − 1) × d ≤ 2,000 × f < (2 × 296 + 1) × d, with d > 0 |
| "The September estimate is 105 percent of the June estimate." / "… is 5 percent more than …" | 100 × sept = 105 × june (same unit tag) |
| "GBP 35,000.00", "1,000 users" | thousands separators accepted on input |

Refused, with rewrites (authoring): bare "most" (unless QX-1 admits "more than half" as its meaning), "many", "few",
"several", "a lot of"; bare "16 of the 18" (rewrite with "exactly" or "at least"). In translation, a bare "16 of the
18" becomes a reading set {exactly, at least} with a distinguishing model.

### 2.2 Environment and wire

- **Environment extension** (identity-bound, Lean-decoded only): `"cardinality_schema": "ve-cardinality@1"` and
  `"cardinality": {"finite_sorts": ["fomc_policymaker", …]}` beside W6a's `unit_schema`/`units` (both required; empty
  `units` allowed). Profiles: `cardinality@0` with `order@0`, `relational-fol@0`, `time@0`, and `documents@1` for
  documents. A declared finite sort restricts admissible structures to finitely many objects of that sort; this is a
  declared assumption shown in the paraphrase ("there are finitely many FOMC policymakers").
- **Statement**: `{"cardinality": {"format": "ve-cardinality@1", "formula": F}}`, with
  `["quantity", S]` (a W6a `ve-quantity@1` tree, unchanged), `["count", sort, [[k, body], …], rel, bound]` (`rel` is
  `lt`, `le` or `eq`; `k`, `bound` canonical integer strings), `["rounds_to", num, den, "0.296"]` (the decimal's
  written places are kept: "0.30" and "0.3" are different claims), `["percent_of", part, whole, "105"]`, and `not`,
  `and`, `or`, `implies`. Bodies: `["is", p]`, `["any"]`, `["not", b]`, `["and", b, b]`, `["or", b, b]`.
- **Identity**: the `meaning_id` is over the whole canonical `ve-cardinality@1` object in the environment-bound
  domain; the regenerated W6a problem keeps its own W6a identities; reports bind both, as W6a binds annotated and
  erased identities. Region constants never appear on the wire as input.

### 2.3 Meaning and erasure

A count atom means `Σ kᵢ × (number of objects of the sort with bodyᵢ) rel bound`, where a number of objects is the
length of a duplicate-free list of exactly those objects (as W6a's `expand_atLeast_iff` counts; the Lean tree depends
on no library, so there is no `Set.ncard` or rational type, and ratios are integer pairs as in `VE.Time.Decimal`).
Lean **erases** a problem (premises and conclusion together) into W6a: for each counted sort it lists the unary
predicates the problem's counts and universal statements mention on that sort (at most 6), makes one dimensionless
integer constant per region (each combination of true and false for those predicates: at most 64), replaces each
count by the sum of its regions' constants, replaces a universal statement over a counted sort whose body is a Boolean
combination of those predicates ("every policymaker expects a further increase or expects rates to stay") by "the
regions outside it sum to 0", writes `0 ≤ n` for every region constant, and replaces the ratio operations by their
linear integer forms. The erased problem goes to W6a's existing certificate route. Soundness (`cardinality_elab_sound`)
is proved by reading each region constant as the size of its region. Countermodels are finite models of the original
vocabulary; Lean computes the region sizes by enumeration and runs W6a's existing countermodel check.

### 2.4 Limits (static, checked first, same order in Lean and the relay)

At most 8 counted sorts, 6 predicates per counted sort (64 regions), 64 terms per count atom, 512 region constants per
problem; literals within W6a's 40-digit numeral limit; the erased problem within W6a's 10,000-node aggregate
(`quantityLimits`). Excess is `ResourceLimit` naming the bound, never a partial answer.

## 3. Track B design: `scales@0`

### 3.1 Declarations

A **dimension** names the compared sort, its comparative predicate ("gives more uplift than"), optionally an equative
predicate ("gives as much uplift as"), and whether "any two can be compared" (allowed only with an equative). It may
list **graded words**: unary predicates on the sort, each an existing W2 open term (its decider and factors stay in
the W2 record), each with a direction (upper: "serious", "the vast majority"; lower: "minor", "slight"), and pairs
"whatever is g is h" ("very serious" above "serious"; "the vast majority" above "a majority"). All predicates are
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

- On norm routes, the premises enter as labelled extra base premises (`LayeredU.X` and `BaseAdmissibleX`), so a rule
  guard may use a graded word ("no response gives serious uplift to …") and the conflict, status and unspecified
  checks see the coherence. A rule whose guard mentions no scale symbol keeps every status (`scales_conflictFree_iff`).
- A **coherence check** of recorded decisions (service mode `scales`, case `coherence`): given ground facts (grade
  decisions, recorded comparisons), Lean answers COHERENT with a checked finite model, INCOHERENT naming the premise
  instance that fails, or UNKNOWN.

## 4. Batches

Each batch lists: what it builds; new files; hand-written shared files; generated files (regenerated, never edited);
Lean statements (Lean batches); fixtures; deletions; seeded bugs; bytes (**estimates**); done when.

### QT-0p. Pilot repair with the existing language (pilot runner, 2 h)

No product code. Smallest step that moves a pilot number.

- **Constitution, u0042.presupposition (38 B) and u0043.s02 (90 B)**: "At the moment, Claude’s three types of
  principals are Anthropic, operators, and users." Content in `relational-fol@0`: a sort `principal_type`, constants
  `anthropic`, `operators`, `users`, the three facts, their pairwise distinctness, and closure
  `∀t:principal_type. t = anthropic ∨ t = operators ∨ t = users`. "At the moment" becomes a LABELLED part (MIXED
  unit) naming the document's present; the heading's presupposed claim is the same content.
- **UDHR, u097 (76 B)**: "Education shall be free, at least in the elementary and fundamental stages." A duty
  guarded by the stage (`elementary`, `fundamental`, constants of a sort `education_stage`) with norm-defaults'
  `unspecified` completion for other stages: "the text does not say" for higher stages is exactly what "at least"
  leaves open. The bearer follows the UDHR translation's existing reading sets.
- **Probes added**: "Is there a fourth type of principal?" (SETTLED no); "Must higher education be free under this
  sentence?" (UNDECIDED).
- **Not done here**: news rows 7b and 22b (94 B) could be written in W6a today with named earlier values, but that
  reverses a converged W6 review ruling (units-schema 7.1, N07b, N22b); recorded as a DRI decision item, not done.
- Bytes: C 0–128 B, U 0–76 B, until audited. Done when both pilots re-run with the repair and the next audit samples
  the changed units.

### QT-0. Statement spec, stub and review (planner, 3–4 h)

- `docs/spec/quantities.md`: sections 2 and 3 as a statement spec (definitions, wire, diagnostics in order, limits,
  wordings with one reading each, refusals with rewrites, fixtures), the Lean blocks of QT-A1, QT-A2 and QT-B1
  verbatim, QX-1's result where it has landed (otherwise "pending" for "most" and "multiple").
- `lean/SpecStubs_quantities.lean`, untracked: every definition with the bodies given here and every theorem as a
  `def … : Prop`, elaborated with `lake env lean` against a build of main; every failure fixed in the spec.
- Decides: (a) a new mode `cardinality` (this plan's choice: `VE.Time.Wire.decodeEnvironment` rejects unknown
  fields, so the quantity runner's `Extension` hook cannot receive a cardinality environment) or another carrier;
  (b) the carrier of the scales block (section 3.1); (c) the profile name `cardinality@0` (not PLAN-EXPAND2's deferred
  evaluation-only `count@0`, which this replaces with a proof-carrying layer).
- Done when the stub elaborates, the spec is committed, and the review converges on PASS (checklist in section 9).

### QT-A1. Lean core of `cardinality@0` (Lean, 5–6 h)

New files: `lean/VE/Cardinality/{Syntax,Semantics,Regions,Erase,Theorems,Examples}.lean`, `lean/CARDINALITY.md`.
Hand-written shared: none. Generated: `lean/VE.lean`, `lean/VE/Audit.lean`, `lean/VE/Route/frozen-sources.sha256`,
`lean/axioms.txt`, `lean/statements.txt`, `lean/predicates.txt`, `lean/declarations.txt`, trust tables (signed).

```lean
import VE.Time.Semantics
import VE.Time.Count

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

/-- W6a statements, count atoms, the two ratio operations (QT-A2 gives their erasure) and the connectives. -/
inductive CFormula where
  | quantity (a : QFormula)
  | count (c : CountAtom)
  | roundsTo (num den : QTerm) (digits : Int) (places : Nat)
  | percentOf (part whole : QTerm) (digits : Int) (places : Nat)
  | not (a : CFormula)
  | and (a b : CFormula)
  | or (a b : CFormula)
  | implies (a b : CFormula)
  deriving DecidableEq, Repr

/-- W6a's environment and the sorts the document declares finite. -/
structure CEnv where
  q : QEnv
  finite : List String

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

/-- `a / b` rounded to `k` decimal places, nearest with ties upward, as an integer number of `10^-k` steps:
`⌊(2·10^k·a + b) / (2b)⌋` (floor division; rationals are written as integer pairs, as `VE.Time.Decimal` does). -/
def roundHalfUp (a b : Int) (k : Nat) : Int := Int.fdiv (2 * 10 ^ k * a + b) (2 * b)

/-- The integer coordinate a closed tagged term denotes, if any. -/
def intOf {α : Type u} (T : TStructure α) (t : QTerm) : Option Int :=
  match t.tdenote T [] with
  | some (.qty _ z) => some z
  | _ => none

def CFormula.holds {α : Type u} (T : TStructure α) : CFormula → Prop
  | .quantity a => a.tdenote T []
  | .count c => c.holds T
  | .roundsTo n d D k => ∃ a b, intOf T n = some a ∧ intOf T d = some b ∧ 0 < b ∧ roundHalfUp a b k = D
  | .percentOf p w D k => ∃ a b, intOf T p = some a ∧ intOf T w = some b ∧ 100 * 10 ^ k * a = D * b
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

/-- Independent admission: counts name a declared finite sort with typed bodies; ratio operands share one tag that
is not `day`; W6a parts are W6a-admitted. (The environment decoder separately refuses declared symbols beginning
with `cardinality__`, so region constants are always fresh.) -/
inductive Admitted (E : CEnv) : CFormula → Prop
  | quantity {a} : VE.Time.Admitted E.q [] a → Admitted E (.quantity a)
  | count {c} : c.sort ∈ E.finite → (∀ kb ∈ c.terms, BodyTyped E c.sort kb.2) → Admitted E (.count c)
  | roundsTo {n d D k t} : t ≠ VE.Time.dayTag → VE.Time.HasType E.q [] n (.qty t) →
      VE.Time.HasType E.q [] d (.qty t) → Admitted E (.roundsTo n d D k)
  | percentOf {p w D k t} : t ≠ VE.Time.dayTag → VE.Time.HasType E.q [] p (.qty t) →
      VE.Time.HasType E.q [] w (.qty t) → Admitted E (.percentOf p w D k)
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

theorem withRegions_admissible {α : Type u} (E : CEnv) (fs : List CFormula) (T : TStructure α)
    (hT : Admissible E T) : (withRegions E fs T).Admissible (E.elab fs)

theorem nonneg_hold {α : Type u} (E : CEnv) (fs : List CFormula) (T : TStructure α) :
    ∀ a ∈ nonnegPremises E fs, a.tdenote (withRegions E fs T) []

/-- **Erasure is faithful**: on an admissible structure, a formula of the problem holds exactly when its erasure holds
where region constants are region sizes. -/
theorem erase_iff {α : Type u} (E : CEnv) (fs : List CFormula) (T : TStructure α) (hT : Admissible E T)
    (a : CFormula) (ha : Admitted E a) (hin : a ∈ fs) :
    a.holds T ↔ (a.erase E fs).tdenote (withRegions E fs T) []

/-- **Soundness**: W6a entailment of the erased problem, with the region premises, gives counting entailment. -/
theorem cardinality_elab_sound (E : CEnv) (ps : List CFormula) (c : CFormula)
    (hps : ∀ a ∈ ps, Admitted E a) (hc : Admitted E c)
    (h : TEntails.{v} (E.elab (c :: ps))
      (nonnegPremises E (c :: ps) ++ ps.map (CFormula.erase E (c :: ps)))
      (c.erase E (c :: ps))) :
    CEntails.{v} E ps c

/-! ## Agreement with W6a's counting sugar -/

/-- "At least n" as a count atom: `-1 · #b ≤ -n`. -/
def atLeastAtom (s : String) (b : Body) (n : Nat) : CountAtom := ⟨s, [(-1, b)], .le, -(n : Int)⟩

/-- The body as an order@0 formula on the counted variable (de Bruijn index 0). -/
def Body.toFormula : Body → VE.Order.Formula

/-- On a declared finite sort, a count atom and W6a's sugar say the same thing, so "at least 3" has one meaning on
both routes. -/
theorem count_atLeast_agree {α : Type u} (E : CEnv) (T : TStructure α) (hT : Admissible E T)
    (s : String) (hs : s ∈ E.finite) (b : Body) (hb : BodyTyped E s b) (n : Nat) :
    (CFormula.count (atLeastAtom s b n)).holds T ↔ (VE.Time.atLeast s n b.toFormula).denote T.lower []

/-! ## Finite countermodels -/

/-- A finite model extended with each region constant's size, computed by enumerating its sorted domains. -/
def withRegionsFinite {α : Type} [DecidableEq α] (E : CEnv) (fs : List CFormula)
    (M : VE.Order.FiniteModel α) : VE.Order.FiniteModel α

/-- W6a's existing countermodel check on the erased problem over `withRegionsFinite`. -/
def refutesC {α : Type} [DecidableEq α] (E : CEnv) (ps : List CFormula) (c : CFormula)
    (M : VE.Order.FiniteModel α) : Bool

theorem refutesC_sound {α : Type} [DecidableEq α] (E : CEnv) (ps : List CFormula) (c : CFormula)
    (M : VE.Order.FiniteModel α) (hps : ∀ a ∈ ps, Admitted E a) (hc : Admitted E c)
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
- **FA2 (agreement)**: `atLeastAtom` against `VE.Time.atLeast` on the units-schema 8 gate-4 models (six, seven and
  eight entities); the evaluation counts of the pinned W6a fixtures are unchanged.
- **FA3 (caps)**: "exactly 16 of the 18" is admitted here and still refused by W6a's sugar (`CountingBound`).
- **FA8 (hostile)**: a count over a sort not declared finite (`CardinalityNotFinite`); a body with a binary
  predicate; seven predicates on one sort (`ResourceLimit`); a vocabulary symbol beginning `cardinality__`; a body
  predicate of another sort.

Seeded bug: `Body.inRegion` reads `not b` as `b`; FA1's certificate replay and FA1b's countermodel `#guard`s fail.
Bytes: 0. Done when `lake build`, `lean/audit.py` and the `#guard`s pass and `lean/statements.txt` shows additions only.

### QT-A2. Rounding and percent-of (Lean, 3–4 h)

New file: `lean/VE/Cardinality/Ratio.lean` (erasure cases of `roundsTo` and `percentOf`, completing
`CFormula.erase`). Shared and generated files as QT-A1.

```lean
namespace VE.Cardinality

/-- The erased pair of integer inequalities is exactly "D is a / b rounded to k places, ties upward"
(the floor-division meaning of `roundHalfUp`). -/
theorem roundsTo_linear_iff (a b D : Int) (k : Nat) (hb : 0 < b) :
    ((2 * D - 1) * b ≤ 2 * 10 ^ k * a ∧ 2 * 10 ^ k * a < (2 * D + 1) * b) ↔ roundHalfUp a b k = D

/-- Rounding to `k` places never moves the value by more than half a step: `|2·10^k·a − 2·D·b| ≤ b`. -/
theorem roundHalfUp_close (a b : Int) (k : Nat) (hb : 0 < b) :
    -b ≤ 2 * 10 ^ k * a - 2 * roundHalfUp a b k * b ∧ 2 * 10 ^ k * a - 2 * roundHalfUp a b k * b < b

end VE.Cardinality
```

"a is D / 10^k percent of b" means `100 · 10^k · a = D · b` by definition (reviewed in QT-0); its erasure is the
W6a equation `scale (100 · 10^k) a = scale D b` in the operands' tag, covered by `erase_iff`. Fixtures (from VE's
paper, `paper/sections/04-e1.md`): FA4 "176 out of 594 rounds to 0.296" true (591 × 594 = 351,054 ≤ 352,000 <
352,242 = 593 × 594) and "rounds to 0.297" false; "52 out of 243 rounds to 0.214", "31 out of 243 rounds to 0.128",
and their difference "21 out of 243 rounds to 0.086" (41,553 ≤ 42,000 < 42,039); "0.30" against "0.3" (two places
against one: different claims); news FA5 "the September estimate out of the June estimate rounds to 1.028" true
(2,055 × 360 = 739,800 ≤ 740,000 < 740,520 = 2,057 × 360) and "about 103 percent" refused (no "about"). Seeded bug:
the upper bound erased with `≤`; the tie fixture "1 out of 8 rounds to 0.12" (false: 0.125 ties upward to 0.13)
becomes true and its `#guard` fails. Bytes: 0 on the pilots; VE's paper unmeasured.

### QT-A3. Wire and service mode `cardinality` (Lean, 5–6 h)

New files: `lean/VE/Cardinality/{Wire,Document,Run,Render}.lean`, `lean/ResponseShape/Schemas/Cardinality.lean`,
`lean/ResponseShape/Encoders/Cardinality.lean`.
Hand-written shared: `lean/VE/Service/Protocol.lean` (mode constructor, name, list entry, dispatch line, theorem
`runMode_cardinality`), `ve/backends/service_schema.py` (`MODES`), `lean/VE/Compose/Dispatch.lean` (the profile row;
`#guard` examples added in `lean/VE/Compose/Examples.lean`, none changed), `ve/profiles.py` (one row),
`ve/assurance-manifest.json` (decoder pins, reviewed by hand), `ROADMAP.md` (trust-cost line).
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
`VE.Time.Wire.W6Env`, `Admission`, `W6Certificate` and `VE.Time.Document`; `ResponseShape.Fits` stands for the
predicate the existing encoder theorems use, named in QT-0.) Fixtures: FA1 and FA1b as route cases; the hostile set
of QT-A1 at the wire (each diagnostic in the order of section 2.4); a forged region table and a forged claimed erased
problem, both refused. Seeded bug: the decoder accepts a count whose sort is not in `finite_sorts`; the hostile route
case fails. Bytes: 0.

### QT-A4. Python relay, document hook, fuzz tests (Python, 4–5 h)

New files: `ve/cardinality.py` (sends cases with `rows` from `ve/backends/relay.py`, binds every id, span, unit and
region name to the request; runs the existing `prove_quantity` search on Lean's regenerated problem and sends the
certificate back to Lean), `tests/test_cardinality_lean.py`, `tests/test_cardinality_answer.py` (fuzz: each member
dropped, emptied, retyped, duplicated, reordered, an index out of range, one and two faults at a time).
Hand-written shared: the document hook for `cardinality` content: through Lean's `document` mode if `lf-16g` has
landed, else one dispatch line in `ve/document.py` (rebased after `lf-16e`/`lf-16f`); `tools/layer_policy.py` (one
row); `tests/data/route-cases.jsonl` (recorded by `tests/route_case_recorder.py`, append-only).
Generated: `.importlinter`, `tools/gate-collection.json`.
**Deleted**: `ve/surface/count.py` (92 lines, a Python copy of `VE.Time.Count` used only by
`tests/test_count_w6a.py`); that test now asks Lean's existing `count` route case for the expansion.
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
- Bytes: news 0–194 B (**estimate** until the run). Done when the measured partition is committed with its run.

### QT-E. Quantity English into Lean's engine (english-lean owner, two batches of 5–6 h)

This is english-lean-PLAN 2.5's quantities step of E3, owned by that plan; listed here because QT-A6 and QT-B3 need
it. Lexer terminal classes for ISO dates, `D Month YYYY`, decimals, labelled amounts, percentages and (new) thousands
separators; W6a's frames (comparisons, `within`, `shift`, `elapsed`, the percentage-point alias) as rules of the
engine with whole-sentence derivation uniqueness. **Deleted** by that step: `ve/surface/time.py`'s parser and
renderer (298 lines) and their two call sites in `ve/document.py` (`:145`, `:1549`), after a delta report on the W6
test corpora (`tests/test_time_surface_w6a.py` and the W6a regression files). Shared files: `lean/VE/EnglishGrammar/*`
(with act-phrases and attitudes), generated `lean/VE/EnglishGrammar/Fixed/*.lean`, `ve/english_grammar/LOCK.json`
(needs a person's `--actions-version`), `ve/english_grammar/codes.json`.

### QT-A6. Count, proportion and rounding wordings in Lean (Lean, 4–5 h)

Rules in the engine (new rule module files if E3's layer mechanism allows, else additive lines): the wordings of
section 2.1, rendering that parses back to the same canonical `F` (the per-output check of english-lean 3.5), and
refusals with rewrites in Lean's diagnostic table: "most" (unless QX-1 admitted it), "many", "few", "several", "a lot
of", "about", bare "16 of the 18". Fixtures: every wording of 2.1 round-trips; FA6 "GBP 35,000.00" lowers to
3,500,000 `gbp_penny` (eligibility's probe P4 now accepted; W6a's canonical rendering is unchanged, separators are an
input alias); FA7 bare "16 of the 18" refused with both rewrites. Seeded bug: "at most n of the m" built as "at
least"; the round-trip fixture fails. Bytes: 0 (readability of QT-A5's content).

### QT-A7. Declared exact unit conversions (Lean, Python, 4–5 h; on trigger)

Trigger: a pinned document needs a conversion (eligibility's "52 weeks" entered as 364 days is the candidate).
`ve-units@2` adds `"converts": {"week": {"to": "day", "factor": "7"}}` between scale-1 tags of one dimension; the
statement layer gains `convert(tag, t)`, typed from the source tag to the target, erased to a literal `scale`. Theorem
`convert_iff` (the erased term denotes `factor × value` in the target tag) and `units_v1_conservative` (a `ve-units@1`
environment means what it meant). Currencies never convert. Calendar months and years are events-time-causation's
and are not fixed factors. Bytes: 0 on the pilots.

### QT-B1. Lean core of `scales@0` (Lean, 5–6 h)

New files: `lean/VE/Scales/{Syntax,Premises,Intended,Degrees,Theorems,Examples}.lean`, `lean/SCALES.md`.
Hand-written shared: none. Generated: as QT-A1.

```lean
import VE.Semantics
import VE.Route.Route

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

/-- Predicates declared with the right signatures; grades are W2 open terms; one dimension per predicate; `above`
pairs within one dimension and one direction, acyclic by `VE.Route.kahn`; `comparable` only with `same`. -/
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

/-- The premises are well typed in the declared environment, so every route that takes typed extra premises takes them. -/
theorem premises_wellTyped (E : VE.Environment) (ots : List String) (D : ScaleDoc) (hD : WellFormed E ots D = true) :
    ∀ a ∈ (scalePremises D).map (·.2), a.check E [] = true

end VE.Scales
```

(`Fresh`'s symbols are the dimension's comparative, equative and graded predicates; `scales_conservative` reads them
as symbols whose meaning the old document did not constrain. `a.check` stands for the core typing check the routes
use, named in QT-0.) Fixtures (`Examples.lean`):

- **FB1 (u0165.s01)**: dimension `uplift` on sort `response`, grade `gives_serious_uplift` (upper, W2 open term
  `serious_uplift` with factor "what counts as serious uplift"). Decisions "r1 gives serious uplift", "r2 gives more
  uplift than r1", "r2 does not give serious uplift": refuted, the failing premise being upward closure.
- **FB2 (u0226.s01, s02)**: dimension `autonomy` on sort `disposition` with constants `fully_corrigible` and
  `fully_autonomous` and the facts that every other disposition lies strictly between them; "a disposition more
  autonomous than fully autonomous" is refuted.
- **FB3 (u0043.s01)**: dimension `trust` on `principal_type`; "different levels of trust" as a reading set {not all
  the same; pairwise different}, with a distinguishing model.
- **FB4 (UDHR u094)**: dimension `social_protection` on `child` with `same`; "all children enjoy the same social
  protection" as `∀c₁ c₂. same(c₁, c₂)` (the duty form is rights').
- **FB6 (u0165.s05)**: dimension `share_of_humanity_targeted` on `attempt`, grades `vast_majority` above `majority`
  (upper); "an attempt on the vast majority is an attempt on a majority" is entailed.
- **FB8 (hostile)**: a comparative on an undeclared dimension; an `above` cycle (`ScaleCycle`, from `VE.Route.kahn`'s
  diagnostic); `above` across directions; `comparable` without `same`; a graded word that is not a W2 open term.

Seeded bug: the lower-direction closure generated with the comparative reversed; FB1's lower twin (a "minor harm"
fixture) is accepted wrongly and its `#guard` fails. Bytes: 0.

### QT-B2. Scale premises on the norm routes; mode `scales` (Lean, Python, 5–6 h)

Needs `lf-16e`, `lf-14d` and `rd-9-int` merged. New files: `lean/VE/Scales/{Wire,Coherence,Run}.lean`,
`lean/ResponseShape/{Schemas,Encoders}/Scales.lean`, `ve/scales.py`, `tests/test_scales_lean.py`,
`tests/test_scales_answer.py`. Hand-written shared: the norm-defaults and readings wire decoders gain one call that
adds the block's labelled premises to `X` (or, preferably, one generic "extra premise providers" hook added by the
first of attitudes AT-4 and this batch, which the other then uses); `Protocol.lean`, `service_schema.py`,
`Compose/Dispatch.lean`, `ve/profiles.py`, `ve/assurance-manifest.json`, `ROADMAP.md` as in QT-A3; the document hook
as in QT-A4. Generated: as QT-A3, with `scales.json`.

```lean
namespace VE.Scales

/-- With no guard and no other extra premise mentioning scale structure, conflict-freedom is unchanged. -/
theorem scales_conflictFree_iff (U : VE.NormDefaults.UDoc) (X : List VE.Formula) (ots : List String)
    (D : ScaleDoc) (hD : WellFormed (VE.NormDefaults.envAt U.D 0) ots D = true)
    (hguards : GuardsFresh U D) (hX : ∀ a ∈ X, Fresh D a) :
    VE.NormDefaults.ConflictFreeX.{u} U X ↔
      VE.NormDefaults.ConflictFreeX.{u} U (X ++ (scalePremises D).map (·.2))

/-- A coherence answer is sound: INCOHERENT names a premise instance false in every model of the facts; COHERENT
carries a finite model of the facts and the premises, checked by Lean. -/
theorem coherence_sound (E : VE.Environment) (ots : List String) (D : ScaleDoc) (facts : List VE.Formula)
    (r : CoherenceResult) (h : checkCoherence E ots D facts = .ok r) : r.Sound E D facts

end VE.Scales

namespace VE.Service
theorem runMode_scales (j : Json) : runMode .scales j = VE.Scales.Run.runCaseReported j := rfl
end VE.Service
```

(`GuardsFresh`, `CoherenceResult.Sound` and `checkCoherence` are this batch's.) Fixtures: FB1 as a coherence case;
the constitution's main document with an empty scales block, whose carried probes stay byte-identical (FB7). Seeded
bugs: Lean, the block's premises dropped on one reading choice (an enumerated fixture fails); Python, the binding
check skips the failing premise's label (a fuzz mutant passes and the test fails). Bytes: 0.

### QT-B3. Scale and graded-word wordings in Lean (Lean, 4–5 h)

After QT-E (or english-lean E3's norm step) and QT-B2. Declarations: "Responses are compared by uplift: one response
gives more uplift than another." "Two responses can give equal uplift." "Any two responses can be compared by
uplift." "Serious uplift is a degree of uplift decided by …" "Very serious uplift is serious uplift." Uses: "Response
A gives more uplift than response B." "Response A gives serious uplift." "Act A is more harmful than act B." "A is
paid as much as B." Refusals with rewrites: a comparative or "very X" on an undeclared dimension ("Declare it first:
'Acts are compared by harm: …'"), "more X than" across two dimensions, "substantially more" (a grade of a difference:
research, R5.2). Fixtures: each wording round-trips; each refusal names its rewrite. Seeded bug: "less X than" read as
"more X than"; the round-trip fixture fails. Bytes: 0.

### QT-B4. Pilots (pilot tooling, 3 h)

- Constitution companion, then main document: FB2 (dial, u0226.s01 and s02, 680 B), FB3 (u0043.s01, 101 B), FB1 and
  FB6 for the hard constraints u0165.s01 to s06 (826 B, already OPEN) only if QX-2 passes.
- UDHR companion probe: FB4 (u094, 90 B), u093 ("special care", 73 B) and u031 ("equal before the law", 28 B) with the
  rights route.
- Measure: claimed and audit-verified bytes, the residual (each graded word is an open term in it), and the carried
  probes. Bytes: C 0–781 B newly claimed; 826 B faithful (audit-verifiable after the next audit); U 0–191 B
  (**estimates**).

### QS-1. One ordered-scale module (proposal for the synthesis review, 3–4 h)

A generic finite grade order (`grades`, `above`), its reflexive-transitive closure, `atLeast_refl`,
`atLeast_trans`, acyclicity through `VE.Route.kahn`, and lemmas proving the existing frozen closures equal to it
(`VE.SoftNorms.outranksPlus`, `VE.Risk.closure`) without editing them; attitudes' planned `VE.Attitudes.Scale.atLeast`
and this plan's grade order would use it. The owner is decided by the synthesis review; if no owner is chosen,
QT-B1 uses `VE.Route.kahn` only and adds no closure of its own.

## 5. Experiments (pre-registered)

Readers for QX-1 and QX-3: Sonnet 5.5 as human proxy (`claude-sonnet-5-5`), 40 independent sessions with no shared
context, items in a seeded random order. This measures agreement among proxy readers, not truth and not human
readers. No experiment ran for this plan.

### QX-1. "most", "many", "multiple", bare "16 of the 18" (2–3 h)

Seed `quantities-QX1`. Items: for "most", six neutral contexts ("Of the 100 members, 51 voted yes. Is it true that
most members voted yes?") at 50, 51, 60 and 95 of 100 and at 3 of 5; for "many", "few" and "several", six contexts
each that separate the cardinal from the proportional reading (Partee); for "multiple", six contexts at 1 and 2; for
bare "16 of the 18 … expect X", six contexts asking whether 17 expecting X is compatible.

- "most" gets "more than half" as its meaning iff at least 36 of 40 answer true at 51 of 100 and at least 36 of 40
  answer false at 50 of 100, on at least 5 of the 6 contexts. Otherwise "most" is refused in authoring and a reading
  set {more than half; an open proportion grade} in translation.
- "many", "few", "several" get a fixed meaning only with 36 of 40 agreement on one reading on 5 of 6 items (expected
  to fail); otherwise refused with rewrites.
- "multiple" means "at least two" iff 36 of 40 on 5 of 6.
- Bare "n of the m" stays refused in authoring whatever the result; in translation it is a reading set unless 36 of
  40 choose "exactly" on 5 of 6, which is recorded but narrows nothing by itself.
- Cost **estimate**: 40 sessions × 30 items = 1,200 short calls, within the usage-cap rules.

### QX-2. Hard-constraint decomposition (2 h)

Material: u0165.s01 to s06 (826 B) in the current form (whole-clause open terms) and the decomposed form (act and
graded word on a dimension, FB1 and FB6). One blind independent audit (the reviewer pair of the model split) per unit,
forms unlabelled and in random order: "Does the VE text say what the source says, no more and no less? Is any
threshold, number or comparison present that the source does not give?" Bar: the decomposed form is faithful on at
least 5 of 6 units, introduces no threshold on any, and is judged no worse than the current form on every unit. Then
QT-B4 ships it; otherwise the whole-clause terms stay, with the auditor's reason recorded.

### QX-3. Inferences with proportional grades (2–3 h)

Seed `quantities-QX3`. Twenty items, ten valid under counting semantics and ten invalid: "The vast majority voted.
Did a majority vote?" (valid); "A majority voted yes and a majority voted no." (contradiction); "Most S are P; every P
is Q. Are most S Q?" (valid); "Most S are P. Are most P S?" (invalid). A premise schema (for example "vast majority
is above majority") is declared in fixtures and offered by the assistant iff at least 36 of 40 accept each of its valid
items and at most 4 of 40 accept its invalid twins. Soundness for counts is not measured here: on the cardinality route
it follows from region arithmetic (FA1-style certificates).

### QX-4. The 1,000-users passage (research, 4 h)

u0146.s01 to u0147.s05 (bytes 88,637–90,744, 2,107 B) as a companion document: the imagined population as a declared
finite sort, its proportions as cardinality content, "should decline" as a soft norm, "probably" as attitudes'
likelihood word, "1 in 1,000 (or 1 in 1 million)" as a reading set. Needs QT-A4 and the weighing and attitudes
outcomes. Bar: an independent audit finds at least 4 of the 5 key units faithful (u0146.s03, u0146.s04, u0147.s02,
u0147.s04, u0147.s05) and no threshold invented; then a plan item composes `cardinality@0` with the norm routes.
Otherwise the passage stays UNFORMALISED with the failing feature named in the ledger.

## 6. Dependencies and merge conflicts

| Batch | Waits for (in-flight item; branch where known) | Hand-written shared files | Generated (regenerate) |
|---|---|---|---|
| QT-0p | — | pilot directories only | — |
| QT-0 | QX-1 for the "most" row (else "pending") | `docs/spec/quantities.md` (new) | — |
| QT-A1, QT-A2, QT-B1 | QT-0 PASS | none | `lean/VE.lean`, `lean/VE/Audit.lean`, frozen inventory, axioms, statements, predicates, declarations; trust tables (signed) |
| QT-A3 | QT-A2; `fix-main-relay`; `lf-16e` and `qa-q2` (`question-answering/q2`) merged or rebased onto, since both edit `Protocol.lean` and `service_schema.py` | `lean/VE/Service/Protocol.lean`, `ve/backends/service_schema.py`, `lean/VE/Compose/Dispatch.lean`, `lean/VE/Compose/Examples.lean`, `ve/profiles.py`, `ve/assurance-manifest.json`, `ROADMAP.md` | response schemas, `lean/ResponseShape.lean`, `lean/ResponseShape/Audit.lean`, checker pins, assurance doc, route cases, gate collection |
| QT-A4 | QT-A3; `lf-16g` for the document hook (else one line in `ve/document.py` after `lf-16e`/`lf-16f`) | `ve/document.py` (or none), `tools/layer_policy.py`, `tests/data/route-cases.jsonl` | `.importlinter`, gate collection |
| QT-A5 | QT-A4 | `usecases/news-article/*` | — |
| QT-E | english-lean E3 scheduling; english-lean E2 flip (Lean decides English) | `lean/VE/EnglishGrammar/*`, `ve/document.py` (two call sites) | English grammar `Fixed/*` and `LOCK.json` (a person's `--actions-version`), English codes |
| QT-A6 | QT-E, QT-A3, QX-1 | `lean/VE/EnglishGrammar/*` (act-phrases and attitudes AT-5 edit the same files: additive rules only, rebased in turn) | as QT-E |
| QT-A7 | trigger; events-time-causation's decision on calendar units | the W6a unit decoder (one version switch) | as QT-A3 |
| QT-B2 | QT-B1; `lf-16e`, `lf-14d`, `rd-9-int` (`rd-9/integrate`); attitudes AT-4's hook if it lands first | norm-defaults and readings wire decoders (one call or the shared hook), then as QT-A3 | as QT-A3 |
| QT-B3 | QT-B2; QT-E or english-lean E3's norm step | `lean/VE/EnglishGrammar/*` | as QT-E |
| QT-B4 | QT-B2 (QT-B3 for display); QX-2 for the hard constraints | pilot directories | — |
| QX-1 to QX-3 | — | `experiments/quantities-QX*/` (new) | — |
| QX-4 | QT-A4; weighing and attitudes outcomes | `experiments/quantities-QX4/` | — |
| QS-1 | the synthesis review | as decided | as QT-A1 |

How conflicts are avoided: all Lean code is in new directories (`lean/VE/Cardinality/`, `lean/VE/Scales/`), all
Python in new modules (`ve/cardinality.py`, `ve/scales.py`) and new test files; the only hand-written shared Lean
file is `Protocol.lean` (additive lines, after its in-flight editors merge) plus one decoder call or hook in QT-B2.
`lf-14b` (norm guards on the order family) touches `norms._lean_route`, which no batch here edits. Generated
inventories are never hand-edited or hand-merged (`regen_generated.py --resolve`). Before each batch, overlap is
checked with `git diff --name-only main...<branch>` against the branches above.

## 7. Expected effect per batch

All **estimates** until a pilot run measures them.

| Batch | Constitution | UDHR | News | Other |
|---|---|---|---|---|
| QT-0p | 0–128 B claimed (u0042.presupposition, u0043.s02); probe "no fourth principal type" SETTLED no | 0–76 B (u097); probe "higher education" UNDECIDED | — | — |
| QT-A1 to QT-A4 | 0 | 0 | 0 | W6a's Python count copy deleted (92 lines) |
| QT-A5 | 0 | 0 | 0–194 B (`s3_count`); one certified consequence under both readings | paper: n of 20 sampled ratio lines expressible |
| QT-E | 0 | 0 | 0 | `ve/surface/time.py` parser and renderer deleted (298 lines) |
| QT-A6 | 0 | 0 | readable wording for the count | eligibility P4 accepted |
| QT-A7 | 0 | 0 | 0 | eligibility's weeks exact |
| QT-B1 to QT-B3 | 0 | 0 | 0 | — |
| QT-B4 | 0–781 B newly claimed (u0043.s01, u0226.s01, s02); 826 B of OPEN hard constraints faithful if QX-2 passes | 0–191 B (u031, u093, u094) with rights | — | — |
| QX-4 | research: up to 2,107 B after weighing and attitudes | — | — | — |

NORTH-STAR rows 3 and 9 (combined C score 0.62 from primary tags) recomputed from units with a quantity construct:
at most about 0.29 (R2.6); the buildable part of this plan alone: about 0.19 summed over C, U and N
(5 × 909 / 184,893 + 4 × 267 / 10,916 + 2 × 194 / 5,448).

## 8. Not claimed, open questions, risks

- **Not claimed**: any byte before a pilot run measures it; that any count reported in a source is true; any
  threshold for a graded word; that proxy readers stand for human readers.
- **Open for QT-0**: the carrier of the scales block; the exact names of the response-shape fit predicate and the core
  typing check used in the statements above; whether english-lean E3's layer mechanism allows separate rule files.
- **Open for the DRI**: news rows 7b and 22b (94 B: a W6 ruling to revisit with a reading set); who owns the generic
  extra-premise hook (attitudes or this plan, whichever lands first); QS-1's owner.
- **Risks**: the region count grows as 2^n (capped at 6 predicates per sort, refused above); certificate search on the
  erased problem may be slow for many regions (UNKNOWN, never a wrong answer; measured in `tools/bench`, not the
  suite); QX-2 may reject the decomposition, leaving the hard constraints as they are; the norm routes are being
  rebuilt (`rd-9`, `lf-14d`, `lf-16e`), so QT-B2 may need a second statement pass; english-lean E3 may not be
  scheduled soon, which delays all new wordings (contents stay writable as JSON and display through Lean's
  paraphrase).

## 9. Review checklist (QT-0)

- `CFormula.holds` and `Intended` state meanings without reference to erasure or generated formulas.
- `cardinality_elab_sound` has no hypothesis about the structure beyond `Admissible`; `Admissible` adds only
  finiteness of declared sorts.
- Region constants cannot collide with declared symbols, and never appear as input.
- `count_atLeast_agree` holds on declared finite sorts for every typed body, so no English count wording has two
  meanings across routes.
- `roundsTo` keeps the written number of places; the tie rule is stated in the paraphrase.
- `grade_open`: no premise fixes a graded word; `scales_conservative` has no hypothesis that the scale block is empty.
- Every refusal names a rewrite in plain English; no symbol appears in any wording or diagnostic.
- Every new trusted line has a signed allowance and a ROADMAP trust-cost line.

## 10. Shared pieces

The full list, with users, is R7. For this plan: (1) one ordered-scale module (QS-1); (2) comparison on a dimension
with generated coherence premises, which weighing's precedent rule ("a case at least as strong") and risk's "less
severe" could use; (3) graded open terms (a W2 record plus a dimension and a direction), shared with attitudes'
"quite likely"; (4) one hook for extra base premises on the norm routes, shared with attitudes; (5) counts over finite
sets and closed listings, shared with events-time-causation and scope; (6) exact rationals and rounding, shared with
math-evidence; (7) unit declarations and conversions, shared with events-time-causation and math-evidence; (8) quantity
English in Lean's engine, sharing grammar files with act-phrases, attitudes and scope; (9) one owner per wording for
population and frequency statements ("1 in 1,000", "almost always") among this plan, attitudes and math-evidence.
