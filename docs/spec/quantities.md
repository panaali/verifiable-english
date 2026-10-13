# Quantities: statement spec (QT-0)

> **Status.** Draft 1, 2026-10-13, branch `design/quantities`, for the QT-0 statement review. It is the statement spec
> that [quantities-PLAN.md](quantities-PLAN.md) draft 2 asks of QT-0: definitions, wire, diagnostics in order, limits,
> wordings with one reading each and their paraphrases, refusals with rewrites, the Lean statements of QT-A1, QT-A2,
> QT-B1 and QS-1 (and those of QT-A3 and QT-B2 that `main` can type), and acceptance fixtures. Docs only: no product
> code, no tests, no generated file, no model calls.
>
> **Checked.** Every statement below was type-checked as a `def … : Prop` in a scratch file
> `lean/SpecStubs_quantities.lean` (untracked, deleted before commit) with `lake env lean` against a build of this
> branch (`main` at `49de179e` plus docs). 33 statements elaborate. Every definition with a body here has that body in
> the stub. Every fixture number in section 9 was computed in the stub with `#eval`, not by hand. ME-1's `VE.Numbers`
> is not on `main`, so the stub carries a copy of its definitions from SYNTHESIS 2.4 and math-evidence-PLAN 3.1. Two
> recipe equations (`runMode_cardinality`, `runCaseReported_fits`) are not elaborated: they need the mode constructor
> and the generated skeleton (section 8). No theorem is proved here; proofs are the build batches'.

## 0. How to read this

- Section 1 records the decisions QT-0 makes. Section 2 lists every place where this spec's statements differ from the
  plan's Lean blocks, with the reason (an elaboration failure, a false statement found by a computed example, or a
  converged edit made precise). Where they differ, this spec's statement is the one under review.
- Sections 3 to 6 are the statements: track A (`cardinality@0`), QS-1, track B (`scales@0`), and the QT-A3 and QT-B2
  contracts that `main` can type.
- Section 7 is the English: wordings with one reading each, Lean's paraphrase of each, refusals with rewrites, and the
  reading sets translation produces.
- Section 9 is the acceptance fixtures with the computed numbers. Every "exactly when" claim has a fixture for each
  direction (section 9.5 maps them).

## 1. Decisions QT-0 makes

| # | Question (plan) | Decision | Why |
|---|---|---|---|
| a | Carrier of `cardinality@0` | A new mode `cardinality`, registered through AR-10's mode registry, keeping the relayed-route recipe | `VE.Time.Wire.decodeEnvironment` calls `exactFields` on six fields (`lean/VE/Time/Wire.lean:248`), so the quantity runner cannot receive a cardinality environment |
| b | Carrier of the scales block | A member `scales` of the environment's `vocabulary` object, beside `soft` and `rights` (as `lean/VE/SoftNorms/Phases.lean:154` and `lean/VE/Rights/Wire.lean:69` read theirs); identity-bound by `environment_id`; decoded by Lean; it declares no symbol | PK-1's pack has `decls := []`; a block that declares nothing needs no environment extension, so `envScales` is dropped (change C12) |
| c | Profile name | `cardinality@0` and `scales@0`, one row each in AR-10's profile-gate table | Replaces PLAN-EXPAND2's evaluation-only `count@0` with a proof-carrying layer |
| d | Tie rules QT-A2 admits | `tiesUp` and `halfEven`. `down` and `up` decode and are refused (`UnsupportedRounding`) | Sources say "rounds to" for nearest rounding; a bound is written "at least" or "at most". `roundsTo_ratio_agree` is stated for all four rules, so admitting one later is one list entry and its wording row |
| e | `kind` of PK-1's `scales` pack | `.constraint` | The pack adds no fresh symbol; it constrains declared predicates, so there is no expansion step to prove. Its local obligations: typing (`scales_pack_wellTyped`), `Transfers` on the readings route, `origins`. Its only conservativity statement is `scales_conservative`; PK-1 claims nothing for combinations |
| f | Keep the closed interval as a separate relation | No | No pilot sentence needs it and "about" is refused (section 7.3). It can be added later with its own name, wording and fixtures |
| g | Name of the response-shape fit predicate | `ResponseShape.Fits req skel row` (`lean/ResponseShape/Skeleton.lean:288`), as `ResponseShape.Encoders.Discourse.runCaseReported_fits` uses it | Read from `main` |
| h | Core typing check in the statements | `VE.Formula.WellFormed E []` (a `Prop`), as PK-1's obligation is stated | Edit 4 of the synthesis |
| i | Diagnostic for a cyclic `above` | `VE.Route.kahn`'s own text, `DependencyCycle: <sorted names>`, unchanged | One owner for the cycle diagnostic; the plan's `ScaleCycle` would be a second wording |
| j | QX-1's results | Pending. They only shape rewrites and the members of reading sets; "most" and "multiple" are refused in authoring whatever they find | Debate (Astra A3) |
| k | Whether english-lean E3 allows separate rule files | Open (english-lean's) | Not decidable from this branch |

## 2. Changes from the plan's Lean blocks

| # | Plan block | This spec | Reason |
|---|---|---|---|
| C1 | `intOf T (t : CTerm) : Option Int` in `CFormula.holds` | `CTerm.Denotes T : CTerm → Int → Prop` | A count is `HasCount`, a proposition; making it a function value needs choice and a finiteness proof. Meaning otherwise as edit 2 states it |
| C2 | `RoundsTo r ⟨D, k⟩` | `RoundsTo r ⟨D, (k : Int)⟩` | `Printed.places` is `Int` (elaboration) |
| C3 | Proportions written as count atoms (plan 2.1) | A constructor `proportion` whose meaning includes `0 < n`, and `proportion_holds_iff` | The debate's rule "every proportion requires a nonempty population" (A4a) must be part of the meaning, as `0 < b` is for rounding. Computed (9.1, FA10): on an empty population "at least 1 in 1,000" as a bare count atom is true and as a proportion is false |
| C4 | Universal statements over a counted sort are replaced by "the regions outside it sum to 0" | The statement stays; erasure adds a **bridge premise** `(∀x:s. b x) ↔ Σ regions outside b = 0` (`bridgePremises`, `bridge_hold`) | Replacing loses the statement's object-level use in W6a ("every policymaker expects …, so p1 does"); the bridge gives W6a both directions. FA1 needs the bridge for its conclusion and its exclusion premise |
| C5 | `predsOn fs s` over counts and universal statements | Counted sorts come from counts only (count atoms, proportions, count operands); a universal statement adds predicates only on a sort already counted | Otherwise a W6a universal statement over a finite sort that nothing counts creates regions and can fail the 6-predicate limit. Computed (FA8): 7 predicates, no count, 0 regions, no limit; with a count, the limit fires |
| C6 | `everyBody? : QFormula → Option (String × Body)` | `bodyOfQ?` and `universalsOf`, which find recognised universal statements anywhere in a formula | More bridges, so fewer UNKNOWNs; soundness is unchanged (`bridge_hold`) |
| C7 | `refutesC_sound` without a model hypothesis | adds `(hM : M.Valid E.q.erase)` | `countermodelCheck` checks formulas only (`lean/VE/Order/Consequence.lean:10`); a model that breaks the declared typing could "refute". As stated in the plan the theorem is false |
| C8 | QT-A2: `erasedRounding` without a body | a body for all four rules; `halfEven`'s endpoints depend on the parity of the literal `D`, so the erased form stays linear | Needed to state and check `roundsTo_ratio_agree` |
| C9 | `roundHalfUp` kept as an optional helper | Dropped | Nothing needs it: a failing claim's report gives the exact fraction (ME's report does the same) |
| C10 | `CardEnv` fields unspecified; `res.Sound` | `CardEnv.wf : env.WellFormed`; `CardReport.Sound E r := CEntails E r.leaves r.root` | "The decoder establishes `WellFormed`" becomes a field the decoder must fill. `Sound` needs the environment and a universe |
| C11 | Exact `percentOf` without `0 < b` (draft 1) | `0 < b` in its meaning | A percent of a count is a proportion (A4a); and it gives "0 is 105 percent of 0" one reading (false) |
| C12 | QT-B1 `envScales`, `S.Admissible (envScales E D)` | `E` itself | Decision (b): the block declares no symbol |
| C13 | QT-B2 `VE.NormDefaults.envAt`, `VE.NormDefaults.ConflictFreeX` | `VE.Norms.envAt`, `VE.NormDefaults.Wire.ConflictFreeX` | The names on `main` (elaboration) |
| C14 | `GuardsFresh` unspecified | guards, carve-outs and definition bodies of `fill U` | Definitions can mention a graded word too |
| C15 | `coherence_sound (E ots D facts)` | `coherence_sound (E X facts)` over the assembled labelled X | The kind runs on the assembled X (synthesis edit 4); the result lists ground instances, each entailed by X, with facts plus instances entailing ⊥ |
| C16 | QS-1 `outranksPlus_eq_above`, `risk_closure_eq` without hypotheses | `RanksValid env`; every severity edge between declared classes | Without them the frozen closures and `above` differ (the soft table is only the closure when `RanksValid.closure` holds) |

## 3. Track A: `cardinality@0` (QT-A1 with QT-A2)

QT-A1 and QT-A2 are **one soundness milestone**: `erase_iff` and `cardinality_elab_sound` cover the ratio
constructors, whose erasure QT-A2 writes. QT-A1 runs in parallel with the other Lean cores; the milestone completes
after ME-1 lands `VE.Numbers`.

### 3.1 What it says, in one paragraph

A document declares some sorts finite. A count says how many objects of a finite sort have a property (a Boolean
combination of unary predicates). A proportion compares the share of a nonempty population that has a property with
a literal fraction. A rounding says that a ratio of two operands (quantities or counts) rounds to a printed decimal
under a named tie rule. A percent says that one operand is an exact, or rounded, percentage of another. Lean erases a
problem into W6a's integer arithmetic: one dimensionless integer constant per region of each counted sort, each count
a sum of region constants. Soundness reads each region constant as its region's size.

### 3.2 Syntax

```lean
import VE.Time.Semantics
import VE.Time.Count
import VE.Numbers        -- ME-1

namespace VE.Cardinality
open VE.Time (QEnv QTerm QFormula QType TStructure TValue TEntails)
universe u v

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

/-- How a proportion compares with a literal fraction: the share is more than, at least, … the fraction. -/
inductive Cmp where
  | gt | ge | lt | le | eq
  deriving DecidableEq, Repr

/-- "`cmp` `num` in `den` of the objects of `sort` with `whole` have `part`". -/
structure Proportion where
  sort : String
  whole : Body
  part : Body
  cmp : Cmp
  num : Nat
  den : Nat
  deriving DecidableEq, Repr

inductive CFormula where
  | quantity (a : QFormula)
  | count (c : CountAtom)
  | proportion (p : Proportion)
  | roundsTo (r : VE.Numbers.Rounding) (num den : CTerm) (digits : Int) (places : Nat)
  | percentOf (part whole : CTerm) (digits : Int) (places : Nat)                                -- exactly
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

def regionPrefix : String := "cardinality__"

/-- What the environment decoder establishes (section 4.2, E5–E8): finite sorts are declared, and no declared constant
begins with the region prefix, so region constants are fresh. -/
structure CEnv.WellFormed (E : CEnv) : Prop where
  finiteDeclared : ∀ s ∈ E.finite, s ∈ E.q.sorts
  fresh : ∀ c τ, E.q.constants c = some τ → c.startsWith regionPrefix = false
```

`digits` and `places` keep the printed number as written: "0.296" is `(296, 3)`, "0.30" is `(30, 2)`, "0.3" is
`(3, 1)`, "102.5" percent is `(1025, 1)`. "0.30" and "0.3" are different claims (FA4).

### 3.3 Meaning, stated without erasure

```lean
def Body.holds {α : Type u} (T : TStructure α) (x : α) : Body → Prop
  | .atom p => T.relation p [.obj x]
  | .any => True
  | .not b => ¬ b.holds T x
  | .and a b => a.holds T x ∧ b.holds T x
  | .or a b => a.holds T x ∨ b.holds T x

/-- Exactly `n` objects of sort `s` have property `b`: a duplicate-free list of exactly those objects has length `n`
(as `VE.Time.expand_atLeast_iff` states counts). -/
def HasCount {α : Type u} (T : TStructure α) (s : String) (b : Body) (n : Nat) : Prop :=
  ∃ xs : List α, xs.Nodup ∧ xs.length = n ∧ ∀ x, x ∈ xs ↔ T.objects s x ∧ b.holds T x

def Rel.holds : Rel → Int → Int → Prop
  | .lt, a, b => a < b
  | .le, a, b => a ≤ b
  | .eq, a, b => a = b

/-- `cmp.holds (den · m) (num · n)` says the share `m / n` stands in `cmp` to `num / den`. -/
def Cmp.holds : Cmp → Int → Int → Prop
  | .gt, a, b => b < a
  | .ge, a, b => b ≤ a
  | .lt, a, b => a < b
  | .le, a, b => a ≤ b
  | .eq, a, b => a = b

/-- `ns` lists, in order, the count of each term's body. -/
def Counts {α : Type u} (T : TStructure α) (s : String) : List (Int × Body) → List Nat → Prop
  | [], [] => True
  | kb :: rest, n :: ns => HasCount T s kb.2 n ∧ Counts T s rest ns
  | _, _ => False

def CountAtom.holds {α : Type u} (T : TStructure α) (c : CountAtom) : Prop :=
  ∃ ns : List Nat, Counts T c.sort c.terms ns ∧
    c.rel.holds ((c.terms.zip ns).map (fun p => p.1.1 * (p.2 : Int))).sum c.bound

/-- A proportion holds only of a nonempty population. -/
def Proportion.holds {α : Type u} (T : TStructure α) (p : Proportion) : Prop :=
  ∃ n m : Nat, HasCount T p.sort p.whole n ∧ HasCount T p.sort (.and p.whole p.part) m ∧ 0 < n ∧
    p.cmp.holds (p.den * (m : Int)) (p.num * (n : Int))

/-- The integer an operand denotes: a closed tagged term's coordinate, or a count. -/
def CTerm.Denotes {α : Type u} (T : TStructure α) : CTerm → Int → Prop
  | .quantity t, z => ∃ g, t.tdenote T [] = some (.qty g z)
  | .count s b, z => ∃ n : Nat, HasCount T s b n ∧ z = n

/-- Rounding is `VE.Numbers.RoundsTo` under the sentence's own tie rule; this track has no rounding definition. -/
def CFormula.holds {α : Type u} (T : TStructure α) : CFormula → Prop
  | .quantity a => a.tdenote T []
  | .count c => c.holds T
  | .proportion p => p.holds T
  | .roundsTo r n d D k => ∃ a b, n.Denotes T a ∧ d.Denotes T b ∧ 0 < b ∧
      VE.Numbers.RoundsTo r ⟨D, (k : Int)⟩ ((a : Rat) / b)
  | .percentOf p w D k => ∃ a b, p.Denotes T a ∧ w.Denotes T b ∧ 0 < b ∧ 100 * 10 ^ k * a = D * b
  | .percentRoundsTo r p w D k => ∃ a b, p.Denotes T a ∧ w.Denotes T b ∧ 0 < b ∧
      VE.Numbers.RoundsTo r ⟨D, (k : Int)⟩ ((100 * a : Rat) / b)
  | .not a => ¬ a.holds T
  | .and a b => a.holds T ∧ b.holds T
  | .or a b => a.holds T ∨ b.holds T
  | .implies a b => a.holds T → b.holds T

/-- W6a-admissible, and every declared finite sort is listed by some finite list. -/
def Admissible {α : Type u} (E : CEnv) (T : TStructure α) : Prop :=
  T.Admissible E.q ∧ ∀ s ∈ E.finite, ∃ xs : List α, ∀ x, T.objects s x ↔ x ∈ xs

def CEntails (E : CEnv) (ps : List CFormula) (c : CFormula) : Prop :=
  ∀ (α : Type v) (T : TStructure α), Admissible E T → (∀ a ∈ ps, a.holds T) → c.holds T
```

`VE.Numbers.RoundsTo` (ME-1, reproduced in the stub from SYNTHESIS 2.4) means, with `y = x · 10^k`:
`tiesUp`: `2D − 1 ≤ 2y < 2D + 1`; `halfEven`: the same strictly, and an endpoint counts only when `D` is even; `down`:
`D ≤ y < D + 1`; `up`: `D − 1 < y ≤ D`. "Ties going up" is towards the larger value, also for negative values
(computed: −1/2 rounds to 0, not −1, under `tiesUp`).

### 3.4 Admission

```lean
/-- Every atom of a body is a declared unary predicate of `s`. -/
def BodyTyped (E : CEnv) (s : String) : Body → Prop
  | .atom p => E.q.predicates p = some [.obj s]
  | .any => True
  | .not b => BodyTyped E s b
  | .and a b => BodyTyped E s a ∧ BodyTyped E s b
  | .or a b => BodyTyped E s a ∧ BodyTyped E s b

/-- The tie rules QT-A2 admits (decision d). -/
def admittedRules : List VE.Numbers.Rounding := [.tiesUp, .halfEven]

/-- A ratio operand's tag: a quantity's W6a tag, or `dimensionless` for a count over a declared finite sort with a
typed body. -/
inductive CTermTyped (E : CEnv) : CTerm → String → Prop
  | quantity {t g} : VE.Time.HasType E.q [] t (.qty g) → CTermTyped E (.quantity t) g
  | count {s b} : s ∈ E.finite → BodyTyped E s b → CTermTyped E (.count s b) VE.Time.dimensionless

/-- Independent admission: counts and proportions name a declared finite sort with typed bodies; a proportion's
fraction is between 0 and 1 with a positive denominator; ratio operands share one tag that is not `day`, and a rounding
names an admitted rule; W6a parts are W6a-admitted. (Freshness of region constants is `CEnv.WellFormed`.) -/
inductive Admitted (E : CEnv) : CFormula → Prop
  | quantity {a} : VE.Time.Admitted E.q [] a → Admitted E (.quantity a)
  | count {c} : c.sort ∈ E.finite → (∀ kb ∈ c.terms, BodyTyped E c.sort kb.2) → Admitted E (.count c)
  | proportion {p} : p.sort ∈ E.finite → BodyTyped E p.sort p.whole → BodyTyped E p.sort p.part →
      0 < p.den → p.num ≤ p.den → Admitted E (.proportion p)
  | roundsTo {r n d D k g} : r ∈ admittedRules → g ≠ VE.Time.dayTag → CTermTyped E n g →
      CTermTyped E d g → Admitted E (.roundsTo r n d D k)
  | percentOf {p w D k g} : g ≠ VE.Time.dayTag → CTermTyped E p g → CTermTyped E w g →
      Admitted E (.percentOf p w D k)
  | percentRoundsTo {r p w D k g} : r ∈ admittedRules → g ≠ VE.Time.dayTag → CTermTyped E p g →
      CTermTyped E w g → Admitted E (.percentRoundsTo r p w D k)
  | not {a} : Admitted E a → Admitted E (.not a)
  | and {a b} : Admitted E a → Admitted E b → Admitted E (.and a b)
  | or {a b} : Admitted E a → Admitted E b → Admitted E (.or a b)
  | implies {a b} : Admitted E a → Admitted E b → Admitted E (.implies a b)

def bodyCheck (E : CEnv) (s : String) : Body → Bool
  | .atom p => E.q.predicates p == some [.obj s]
  | .any => true
  | .not b => bodyCheck E s b
  | .and a b => bodyCheck E s a && bodyCheck E s b
  | .or a b => bodyCheck E s a && bodyCheck E s b

def dl : String := VE.Time.dimensionless

def CTerm.tagOf (E : CEnv) : CTerm → Option String
  | .quantity t => match t.typeOf E.q [] with
    | some (.qty g) => some g
    | _ => none
  | .count s b => if E.finite.contains s && bodyCheck E s b then some dl else none

def ratioTyped (E : CEnv) (x y : CTerm) : Bool :=
  match x.tagOf E, y.tagOf E with
  | some g, some h => g == h && g != VE.Time.dayTag
  | _, _ => false

def CFormula.admits (E : CEnv) : CFormula → Bool
  | .quantity a => a.admits E.q []
  | .count c => E.finite.contains c.sort && c.terms.all (fun kb => bodyCheck E c.sort kb.2)
  | .proportion p => E.finite.contains p.sort && bodyCheck E p.sort p.whole &&
      bodyCheck E p.sort p.part && decide (0 < p.den) && decide (p.num ≤ p.den)
  | .roundsTo r n d _ _ => admittedRules.contains r && ratioTyped E n d
  | .percentOf p w _ _ => ratioTyped E p w
  | .percentRoundsTo r p w _ _ => admittedRules.contains r && ratioTyped E p w
  | .not a => a.admits E
  | .and a b => a.admits E && b.admits E
  | .or a b => a.admits E && b.admits E
  | .implies a b => a.admits E && b.admits E

theorem admits_sound (E : CEnv) (a : CFormula) (h : a.admits E = true) : Admitted E a
theorem admits_complete (E : CEnv) (a : CFormula) (h : Admitted E a) : a.admits E = true
```

A count is dimensionless, so it can share a ratio with a dimensionless quantity but not with a tagged one (W6a's
`UnitMismatch`). A ratio of two `day` quantities (calendar dates) is refused; durations use `elapsed_day` (FA9).

### 3.5 Regions and erasure

```lean
def firstUse {β : Type} [BEq β] (xs : List β) : List β :=
  xs.foldl (fun acc x => if acc.contains x then acc else acc ++ [x]) []

def Body.atoms : Body → List String
  | .atom p => [p]
  | .any => []
  | .not b => b.atoms
  | .and a b => a.atoms ++ b.atoms
  | .or a b => a.atoms ++ b.atoms

/-- A W6a formula on the counted variable (de Bruijn 0) built from unary atoms, read as a body. -/
def bodyOfQ? : QFormula → Option Body
  | .unary p (.var 0) => some (.atom p)
  | .top => some .any
  | .bottom => some (.not .any)
  | .not a => (bodyOfQ? a).map Body.not
  | .and a b => match bodyOfQ? a, bodyOfQ? b with
    | some x, some y => some (.and x y)
    | _, _ => none
  | .or a b => match bodyOfQ? a, bodyOfQ? b with
    | some x, some y => some (.or x y)
    | _, _ => none
  | .implies a b => match bodyOfQ? a, bodyOfQ? b with
    | some x, some y => some (.or (.not x) y)
    | _, _ => none
  | _ => none

/-- The recognised universal statements `∀x:s. b(x)` anywhere in a W6a formula, each with its own text. -/
def universalsOf : QFormula → List (String × Body × QFormula)
  | .all s a => (match bodyOfQ? a with
      | some b => [(s, b, QFormula.all s a)]
      | none => []) ++ universalsOf a
  | .ex _ a => universalsOf a
  | .not a => universalsOf a
  | .and a b => universalsOf a ++ universalsOf b
  | .or a b => universalsOf a ++ universalsOf b
  | .implies a b => universalsOf a ++ universalsOf b
  | _ => []

def CFormula.universalsC (E : CEnv) : CFormula → List (String × Body × QFormula)
  | .quantity a => (universalsOf a).filter (fun x => E.finite.contains x.1)
  | .not a => a.universalsC E
  | .and a b => a.universalsC E ++ b.universalsC E
  | .or a b => a.universalsC E ++ b.universalsC E
  | .implies a b => a.universalsC E ++ b.universalsC E
  | _ => []

def CTerm.countBodies : CTerm → List (String × Body)
  | .quantity _ => []
  | .count s b => [(s, b)]

/-- The counted sorts and bodies: count atoms, proportions and count operands (not universal statements). -/
def CFormula.countBodies : CFormula → List (String × Body)
  | .quantity _ => []
  | .count c => c.terms.map (fun kb => (c.sort, kb.2))
  | .proportion p => [(p.sort, p.whole), (p.sort, p.part)]
  | .roundsTo _ n d _ _ => n.countBodies ++ d.countBodies
  | .percentOf p w _ _ => p.countBodies ++ w.countBodies
  | .percentRoundsTo _ p w _ _ => p.countBodies ++ w.countBodies
  | .not a => a.countBodies
  | .and a b => a.countBodies ++ b.countBodies
  | .or a b => a.countBodies ++ b.countBodies
  | .implies a b => a.countBodies ++ b.countBodies

def countedSorts (fs : List CFormula) : List String :=
  firstUse ((fs.flatMap (·.countBodies)).map (·.1))

/-- Recognised universal statements over a counted sort, each once. -/
def countedUniversals (E : CEnv) (fs : List CFormula) : List (String × Body × QFormula) :=
  firstUse ((fs.flatMap (·.universalsC E)).filter (fun x => (countedSorts fs).contains x.1))

/-- The predicates on sort `s`, in first-use order: count bodies first, then counted universal statements. -/
def predsOn (E : CEnv) (fs : List CFormula) (s : String) : List String :=
  firstUse ((((fs.flatMap (·.countBodies)).filter (·.1 == s)).flatMap (·.2.atoms)) ++
    (((countedUniversals E fs).filter (·.1 == s)).flatMap (·.2.1.atoms)))

/-- A region: one truth value per predicate of `predsOn`; `regions n` lists all `2 ^ n`, first predicate most
significant. -/
abbrev Region := List Bool

def regions : Nat → List Region
  | 0 => [[]]
  | n + 1 => (regions n).map (false :: ·) ++ (regions n).map (true :: ·)

def Body.inRegion (ps : List String) (r : Region) : Body → Bool
  | .atom p => match ps.findIdx? (· == p) with
    | some i => r.getD i false
    | none => false
  | .any => true
  | .not b => !(b.inRegion ps r)
  | .and a b => a.inRegion ps r && b.inRegion ps r
  | .or a b => a.inRegion ps r || b.inRegion ps r

def bitString (r : Region) : String := String.mk (r.map (fun b => if b then '1' else '0'))

/-- `cardinality__<sort>__<bits>`. Bits are only `0` and `1`, so two different (sort, region) pairs never share a
name. -/
def regionConst (s : String) (r : Region) : String := regionPrefix ++ s ++ "__" ++ bitString r

def regionTable (E : CEnv) (fs : List CFormula) : List (String × String × Region) :=
  (countedSorts fs).flatMap fun s =>
    (regions (predsOn E fs s).length).map fun r => (regionConst s r, s, r)

/-- `E.q` plus one dimensionless integer constant per region of every counted sort. -/
def CEnv.elab (E : CEnv) (fs : List CFormula) : QEnv :=
  { E.q with constants := fun c =>
      if (regionTable E fs).any (·.1 == c) then some (.qty dl) else E.q.constants c }

def sumTerms : List QTerm → QTerm
  | [] => .num dl 0
  | [t] => t
  | t :: ts => .add dl t (sumTerms ts)

def regionSum (E : CEnv) (fs : List CFormula) (s : String) (b : Body) : QTerm :=
  let ps := predsOn E fs s
  sumTerms (((regions ps.length).filter (fun r => b.inRegion ps r)).map
    (fun r => QTerm.const dl (regionConst s r)))

def CountAtom.erase (E : CEnv) (fs : List CFormula) (c : CountAtom) : QFormula :=
  let lhs := sumTerms (c.terms.map (fun kb => QTerm.scale dl kb.1 (regionSum E fs c.sort kb.2)))
  let rhs : QTerm := .num dl c.bound
  match c.rel with
  | .lt => .lt lhs rhs
  | .le => .le lhs rhs
  | .eq => .eq lhs rhs

def Cmp.erase (a b : QTerm) : Cmp → QFormula
  | .gt => .lt b a
  | .ge => .le b a
  | .lt => .lt a b
  | .le => .le a b
  | .eq => .eq a b

def Proportion.erase (E : CEnv) (fs : List CFormula) (p : Proportion) : QFormula :=
  let n := regionSum E fs p.sort p.whole
  let m := regionSum E fs p.sort (.and p.whole p.part)
  .and (.lt (.num dl 0) n) (p.cmp.erase (.scale dl p.den m) (.scale dl p.num n))

def CTerm.erase (E : CEnv) (fs : List CFormula) : CTerm → QTerm
  | .quantity t => t
  | .count s b => regionSum E fs s b

def CFormula.erase (E : CEnv) (fs : List CFormula) : CFormula → QFormula
  | .quantity a => a
  | .count c => c.erase E fs
  | .proportion p => p.erase E fs
  | .roundsTo r n d D k =>
      let g := (n.tagOf E).getD dl
      .and (.lt (.num g 0) (d.erase E fs)) (roundingQ g r (n.erase E fs) (d.erase E fs) D k)
  | .percentOf p w D k =>
      let g := (p.tagOf E).getD dl
      .and (.lt (.num g 0) (w.erase E fs))
        (.eq (.scale g (100 * 10 ^ k) (p.erase E fs)) (.scale g D (w.erase E fs)))
  | .percentRoundsTo r p w D k =>
      let g := (p.tagOf E).getD dl
      .and (.lt (.num g 0) (w.erase E fs)) (roundingQ g r (.scale g 100 (p.erase E fs)) (w.erase E fs) D k)
  | .not a => .not (a.erase E fs)
  | .and a b => .and (a.erase E fs) (b.erase E fs)
  | .or a b => .or (a.erase E fs) (b.erase E fs)
  | .implies a b => .implies (a.erase E fs) (b.erase E fs)

/-- One premise `0 ≤ n` per region constant. -/
def nonnegPremises (E : CEnv) (fs : List CFormula) : List QFormula :=
  (regionTable E fs).map fun e => .le (.num dl 0) (.const dl e.1)

/-- One premise per counted universal statement: it holds exactly when the regions outside its body sum to 0. -/
def bridgePremises (E : CEnv) (fs : List CFormula) : List QFormula :=
  (countedUniversals E fs).map fun x =>
    let z : QFormula := .eq (regionSum E fs x.1 (.not x.2.1)) (.num dl 0)
    .and (.implies x.2.2 z) (.implies z x.2.2)

/-- The problem handed to W6a: region premises, bridges and the erased premises; the erased conclusion. -/
def erasedProblem (E : CEnv) (ps : List CFormula) (c : CFormula) : List QFormula × QFormula :=
  let fs := c :: ps
  (nonnegPremises E fs ++ bridgePremises E fs ++ ps.map (CFormula.erase E fs), c.erase E fs)

def regionBody (ps : List String) (r : Region) : Body :=
  (ps.zip r).foldr (fun pv acc => .and (if pv.2 then .atom pv.1 else .not (.atom pv.1)) acc) .any

open Classical in
noncomputable def regionSize {α : Type u} (T : TStructure α) (s : String) (b : Body) : Nat :=
  if h : ∃ n, HasCount T s b n then Classical.choose h else 0

/-- The structure that reads every region constant as the number of objects in its region. -/
noncomputable def withRegions {α : Type u} (E : CEnv) (fs : List CFormula) (T : TStructure α) :
    TStructure α :=
  { T with constant := fun c => match (regionTable E fs).find? (·.1 == c) with
      | some (_, s, r) => some (.qty dl (regionSize T s (regionBody (predsOn E fs s) r)))
      | none => T.constant c }
```

(`roundingQ` is QT-A2's, section 3.8.) The erased formulas are W6a statements over `E.elab fs`: every region sum is
tagged `dimensionless`, and a ratio's inequalities are in its operands' tag. They go to W6a's existing certificate
route; Python's `prove_quantity` searches for a certificate on Lean's regenerated problem, and Lean replays it.

### 3.6 Theorems

```lean
/-- On an admissible structure every count over a declared finite sort exists and is unique, so a count atom and its
negation mean what they say. -/
theorem hasCount_exists_unique {α : Type u} (E : CEnv) (T : TStructure α) (hT : Admissible E T)
    (s : String) (hs : s ∈ E.finite) (b : Body) :
    ∃ n, HasCount T s b n ∧ ∀ m, HasCount T s b m → m = n

theorem withRegions_admissible {α : Type u} (E : CEnv) (hE : E.WellFormed) (fs : List CFormula)
    (T : TStructure α) (hT : Admissible E T) : (withRegions E fs T).Admissible (E.elab fs)

theorem nonneg_hold {α : Type u} (E : CEnv) (fs : List CFormula) (T : TStructure α) :
    ∀ a ∈ nonnegPremises E fs, a.tdenote (withRegions E fs T) []

theorem bridge_hold {α : Type u} (E : CEnv) (hE : E.WellFormed) (fs : List CFormula) (T : TStructure α)
    (hT : Admissible E T) (hfs : ∀ a ∈ fs, Admitted E a) :
    ∀ a ∈ bridgePremises E fs, a.tdenote (withRegions E fs T) []

/-- **Erasure is faithful**: on an admissible structure, a formula of the problem holds exactly when its erasure holds
where region constants are region sizes. -/
theorem erase_iff {α : Type u} (E : CEnv) (hE : E.WellFormed) (fs : List CFormula) (T : TStructure α)
    (hT : Admissible E T) (a : CFormula) (ha : Admitted E a) (hin : a ∈ fs) :
    a.holds T ↔ (a.erase E fs).tdenote (withRegions E fs T) []

/-- **Soundness**: W6a entailment of the erased problem gives counting entailment. -/
theorem cardinality_elab_sound (E : CEnv) (hE : E.WellFormed) (ps : List CFormula) (c : CFormula)
    (hps : ∀ a ∈ ps, Admitted E a) (hc : Admitted E c)
    (h : TEntails.{v} (E.elab (c :: ps)) (erasedProblem E ps c).1 (erasedProblem E ps c).2) :
    CEntails.{v} E ps c

/-- A proportion holds exactly when the population is nonempty and the share compares as written. -/
theorem proportion_holds_iff {α : Type u} (E : CEnv) (T : TStructure α) (hT : Admissible E T) (p : Proportion)
    (hp : Admitted E (.proportion p)) :
    (CFormula.proportion p).holds T ↔
      ∃ n m : Nat, HasCount T p.sort p.whole n ∧ HasCount T p.sort (.and p.whole p.part) m ∧ 0 < n ∧
        p.cmp.holds ((m : Int) * p.den) ((n : Int) * p.num)
```

`erase_iff` is false without `hE` (computed, FA9a: a declared constant spelled `cardinality__fomc_policymaker__0`
holds at 5 and is overwritten with its region's size 0). `cardinality_elab_sound` has no hypothesis about the
structure beyond `Admissible`, and `Admissible` adds only finiteness of the declared sorts.

### 3.7 Agreement with W6a's four counting forms

```lean
/-- "At least n": `-1 · #b ≤ -n`; "at most n": `#b ≤ n`; "exactly n": `#b = n`. -/
def atLeastAtom (s : String) (b : Body) (n : Nat) : CountAtom := ⟨s, [(-1, b)], .le, -(n : Int)⟩
def atMostAtom (s : String) (b : Body) (n : Nat) : CountAtom := ⟨s, [(1, b)], .le, n⟩
def exactlyAtom (s : String) (b : Body) (n : Nat) : CountAtom := ⟨s, [(1, b)], .eq, n⟩
/-- "Exactly n of the m": exactly m selected and exactly n of them with the property (W6a's `nOfM`). -/
def nOfMFormula (s : String) (n m : Nat) (sel prop : Body) : CFormula :=
  .and (.count (exactlyAtom s sel m)) (.count (exactlyAtom s (.and sel prop) n))

/-- The body as an order@0 formula on the counted variable (de Bruijn index 0). -/
def Body.toFormula : Body → VE.Order.Formula
  | .atom p => .unary p (.var 0)
  | .any => .top
  | .not b => .not b.toFormula
  | .and a b => .and a.toFormula b.toFormula
  | .or a b => .or a.toFormula b.toFormula

theorem count_atLeast_agree {α : Type u} (E : CEnv) (T : TStructure α) (hT : Admissible E T)
    (s : String) (hs : s ∈ E.finite) (b : Body) (hb : BodyTyped E s b) (n : Nat) :
    (CFormula.count (atLeastAtom s b n)).holds T ↔ (VE.Time.atLeast s n b.toFormula).denote T.lower []
theorem count_atMost_agree {α : Type u} (E : CEnv) (T : TStructure α) (hT : Admissible E T)
    (s : String) (hs : s ∈ E.finite) (b : Body) (hb : BodyTyped E s b) (n : Nat) :
    (CFormula.count (atMostAtom s b n)).holds T ↔ (VE.Time.atMost s n b.toFormula).denote T.lower []
theorem count_exactly_agree {α : Type u} (E : CEnv) (T : TStructure α) (hT : Admissible E T)
    (s : String) (hs : s ∈ E.finite) (b : Body) (hb : BodyTyped E s b) (n : Nat) :
    (CFormula.count (exactlyAtom s b n)).holds T ↔ (VE.Time.exactly s n b.toFormula).denote T.lower []
/-- Follows from `count_exactly_agree`; on the wire W6a's `n_of_m` means "exactly". -/
theorem count_nOfM_agree {α : Type u} (E : CEnv) (T : TStructure α) (hT : Admissible E T)
    (s : String) (hs : s ∈ E.finite) (sel prop : Body) (h₁ : BodyTyped E s sel) (h₂ : BodyTyped E s prop)
    (n m : Nat) :
    (nOfMFormula s n m sel prop).holds T ↔
      (VE.Time.nOfM s n m sel.toFormula prop.toFormula).denote T.lower []
```

So "at least 3", "at most 3", "exactly 3" and "exactly 3 of the 7" each have one meaning on both routes. W6a's sugar
keeps its caps (`CountingBound`, `lean/VE/Time/Wire.lean:739–749`); this route has none below the limits of 4.3.

### 3.8 Rounding (QT-A2; waits for ME-1)

```lean
/-- The linear integer form of "a / b rounds to D / 10^k under rule r" (b > 0) that erasure hands to W6a. -/
def erasedRounding : VE.Numbers.Rounding → Int → Int → Int → Nat → Prop
  | .tiesUp, a, b, D, k => (2 * D - 1) * b ≤ 2 * 10 ^ k * a ∧ 2 * 10 ^ k * a < (2 * D + 1) * b
  | .halfEven, a, b, D, k =>
      if D % 2 = 0 then (2 * D - 1) * b ≤ 2 * 10 ^ k * a ∧ 2 * 10 ^ k * a ≤ (2 * D + 1) * b
      else (2 * D - 1) * b < 2 * 10 ^ k * a ∧ 2 * 10 ^ k * a < (2 * D + 1) * b
  | .down, a, b, D, k => D * b ≤ 10 ^ k * a ∧ 10 ^ k * a < (D + 1) * b
  | .up, a, b, D, k => (D - 1) * b < 10 ^ k * a ∧ 10 ^ k * a ≤ D * b

/-- The same inequalities as W6a statements in the operands' tag `g`. -/
def roundingQ (g : String) (r : VE.Numbers.Rounding) (a b : QTerm) (D : Int) (k : Nat) : QFormula :=
  let s := fun (c : Int) (t : QTerm) => QTerm.scale g c t
  match r with
  | .tiesUp => .and (.le (s (2 * D - 1) b) (s (2 * 10 ^ k) a)) (.lt (s (2 * 10 ^ k) a) (s (2 * D + 1) b))
  | .halfEven =>
      if D % 2 = 0 then .and (.le (s (2 * D - 1) b) (s (2 * 10 ^ k) a)) (.le (s (2 * 10 ^ k) a) (s (2 * D + 1) b))
      else .and (.lt (s (2 * D - 1) b) (s (2 * 10 ^ k) a)) (.lt (s (2 * 10 ^ k) a) (s (2 * D + 1) b))
  | .down => .and (.le (s D b) (s (10 ^ k) a)) (.lt (s (10 ^ k) a) (s (D + 1) b))
  | .up => .and (.lt (s (D - 1) b) (s (10 ^ k) a)) (.le (s (10 ^ k) a) (s D b))

/-- The erased inequalities mean exactly `VE.Numbers.RoundsTo` under the sentence's rule. -/
theorem roundsTo_ratio_agree (r : VE.Numbers.Rounding) (a b D : Int) (k : Nat) (hb : 0 < b) :
    erasedRounding r a b D k ↔ VE.Numbers.RoundsTo r ⟨D, (k : Int)⟩ ((a : Rat) / b)
```

A rounded percentage is `erasedRounding r (100 · a) b D k`, so `roundsTo_ratio_agree` covers it too. Closeness is
ME's `roundsTo_close`; uniqueness is ME's `roundsTo_unique`. No closed-interval relation (decision f).

### 3.9 Finite countermodels

```lean
def Body.evalFin {α : Type} [DecidableEq α] (M : VE.Order.FiniteModel α) (x : α) : Body → Bool
  | .atom p => (M.relations p).any (fun t => decide (t = [Sum.inl x]))
  | .any => true
  | .not b => !(b.evalFin M x)
  | .and a b => a.evalFin M x && b.evalFin M x
  | .or a b => a.evalFin M x || b.evalFin M x

/-- The number of distinct listed objects of `s` with `b`. -/
def countFin {α : Type} [DecidableEq α] (M : VE.Order.FiniteModel α) (s : String) (b : Body) : Nat :=
  ((firstUse (M.domains s)).filter (fun x => b.evalFin M x)).length

/-- A finite model extended with each region constant's size. -/
def withRegionsFinite {α : Type} [DecidableEq α] (E : CEnv) (fs : List CFormula)
    (M : VE.Order.FiniteModel α) : VE.Order.FiniteModel α :=
  { M with constants := fun c => match (regionTable E fs).find? (·.1 == c) with
      | some (_, s, r) => some (.inr (countFin M s (regionBody (predsOn E fs s) r)))
      | none => M.constants c }

/-- W6a's existing countermodel check on the erased problem over `withRegionsFinite`. -/
def refutesC {α : Type} [DecidableEq α] (E : CEnv) (ps : List CFormula) (c : CFormula)
    (M : VE.Order.FiniteModel α) : Bool :=
  VE.Order.countermodelCheck (withRegionsFinite E (c :: ps) M)
    ((erasedProblem E ps c).1.map QFormula.erase) (erasedProblem E ps c).2.erase

theorem refutesC_sound {α : Type} [DecidableEq α] (E : CEnv) (hE : E.WellFormed) (ps : List CFormula)
    (c : CFormula) (M : VE.Order.FiniteModel α) (hM : M.Valid E.q.erase) (hps : ∀ a ∈ ps, Admitted E a)
    (hc : Admitted E c) (h : refutesC E ps c M = true) : ¬ CEntails.{0} E ps c
```

A countermodel is a finite model of the original vocabulary; Lean computes the region sizes itself, so a claimed
region table is never read (QT-A3 refuses a forged one).

### 3.10 Limits of what counts can prove

- Counts do not see named objects: from "p1 expects an increase" the route does not derive "at least one policymaker
  expects an increase". Such a problem is UNKNOWN unless a finite countermodel exists. Never a wrong answer.
- A universal statement is bridged only when its body is a Boolean combination of unary atoms on the bound variable
  and its sort is counted (C4, C5).
- A ratio's operands are closed: a count or a closed W6a term. "The rate before the decision" (time-indexed) is
  events-time-causation's.

## 4. Wire, limits and diagnostics (QT-A3)

### 4.1 Wire

- **Environment** (identity-bound, decoded by Lean only): W6a's fields plus `"cardinality_schema": "ve-cardinality@1"`
  and `"cardinality": {"finite_sorts": [sort, …]}`. Profiles: `cardinality@0` with `order@0`, `relational-fol@0`,
  `time@0`, and optionally `documents@1`.
- **Statement**: `{"format": "ve-cardinality@1", "formula": F}`. `F` is one of:
  - `["quantity", Q]`, `Q` a W6a `ve-quantity@1` formula tree, unchanged;
  - `["count", sort, [[k, body], …], rel, bound]`, `rel` one of `lt`, `le`, `eq`; `k` and `bound` canonical integer
    strings;
  - `["proportion", sort, whole, part, cmp, num, den]`, `cmp` one of `gt`, `ge`, `lt`, `le`, `eq`; `num` and `den`
    canonical natural-number strings;
  - `["rounds_to", rule, num, den, printed]` and `["percent_rounds_to", rule, part, whole, printed]`, `rule` one of
    `ties_up`, `half_even` (admitted), `down`, `up` (decoded, refused);
  - `["percent_of", part, whole, printed]` (exactly);
  - `["not", F]`, `["and", F, F]`, `["or", F, F]`, `["implies", F, F]`.
- **Operands**: `["quantity", T]` (a W6a term tree) or `["count", sort, body]`. **Bodies**: `["is", p]`, `["any"]`,
  `["not", b]`, `["and", b, b]`, `["or", b, b]`. **Printed numbers**: a decimal string; `places` is the number of
  written digits after the point.
- **Identity**: the `meaning_id` is over the whole canonical `ve-cardinality@1` object in the environment-bound domain;
  the regenerated W6a problem keeps its own W6a identities; reports bind both. Region constants never appear on the
  wire as input; a claimed region table or erased problem must equal the regenerated one.
- **Case kinds**: `admission` (typing, canonical `F`, the regenerated erased problem with its W6a identities, the
  region table, the bridges), `countermodel`, `certificate`, `document` (claim graph), `paraphrase` (Lean's English
  line, display-only until QT-A6 adds the parse-back check).

### 4.2 Diagnostics, in order (Lean decides them; Python checks schema and request binding only)

Environment:

| # | Check | Text |
|---|---|---|
| E1 | Fields | the frozen `exactFields` texts, over W6a's six fields plus `cardinality_schema` and `cardinality` |
| E2 | Profiles (AR-10 row) | `UnsupportedProfile: cardinality@0 requires order@0, relational-fol@0 and time@0, optionally with documents@1` |
| E3 | Schema | `UnsupportedProfile: Unsupported cardinality schema` |
| E4 | The W6a part | `VE.Time.Wire.decodeEnvironment`'s own texts, in its order, on the environment without the two cardinality fields |
| E5 | `finite_sorts` shape | `InvalidInput: cardinality.finite_sorts must be an array of sort names` |
| E6 | Count | `ResourceLimit: At most 64 finite sorts` |
| E7 | Each name | `DuplicateDeclaration: finite sort <s>`; then `UnknownSort(<s>)` for a name that is not a declared user sort |
| E8 | Reserved prefix | `ReservedName: cardinality__ is reserved for region constants (<name>)`, for any declared sort, predicate or constant |

E5 to E8 establish `CEnv.WellFormed` (QT-A3's `CardEnv.wf`). Statements, each in order, depth first and left to right:

| # | Check | Text |
|---|---|---|
| S1 | Shape and format | `Unsupported cardinality format` |
| S2 | Size | W6a's `ResourceLimit: Quantity AST exceeds node or depth limit` (10,000 nodes, depth 64) |
| S3 | Operators, numbers | `Unknown cardinality operator <op>`; the frozen integer decoder's text; W6a's decimal texts (`Invalid decimal literal …`, `ResourceLimit: Decimal literal exceeds 40 digits`); `Unknown rounding rule <r>` |
| S4 | W6a parts | W6a's elaboration texts |
| S5 | Counted sort | `CardinalityNotFinite(<s>)` |
| S6 | Body atom | `TypeMismatch: <p> is not a unary predicate of sort <s>` |
| S7 | Terms | `ResourceLimit: At most 64 terms in a count` |
| S8 | Fraction | `ProportionRange(<num> in <den>)` when `den = 0` or `num > den` |
| S9 | Ratio tags | W6a's `TypeMismatch: UnitMismatch(<x>,<y>)`; for `day`: `TypeMismatch: a ratio of calendar dates has no meaning; durations use elapsed_day` |
| S10 | Rule | `UnsupportedRounding(<rule>)` |

Problem (premises and conclusion together, after every statement, before any model or certificate is read):

| # | Check | Text |
|---|---|---|
| P1 | Counted sorts | `ResourceLimit: At most 8 counted sorts` |
| P2 | Predicates per counted sort | `ResourceLimit: At most 6 predicates on counted sort <s> (64 regions)` |
| P3 | Erased problem | W6a's `ResourceLimit: premises and conclusion exceed aggregate 10000-node limit` |

So a problem has at most 512 region constants (8 × 64). Then the binding texts: W6a's certificate texts, and
`cardinality certificate is stale or bound to different statements`, `region table differs from the regenerated
one`, `erased problem differs from the regenerated one`. A limit is `ResourceLimit` naming the bound, never a partial
answer; exhaustion of a search is UNKNOWN.

### 4.3 QT-A3 statements

```lean
/-- A decoded cardinality environment; the decoder fills `wf` (E5–E8). -/
structure CardEnv where
  w6 : VE.Time.Wire.W6Env
  env : CEnv
  wf : env.WellFormed
  environmentId : String

structure CAdmission (w : CardEnv) where
  formula : CFormula
  admitted : formula.admits w.env = true
  meaningId : String

structure CardCertificate where
  environmentId : String
  premiseIds : List String
  conclusionId : String
  w6 : VE.Time.Wire.W6Certificate

structure CardReport where
  root : CFormula
  leaves : List CFormula

def CardReport.Sound (E : CEnv) (r : CardReport) : Prop := CEntails.{v} E r.leaves r.root

def checkCertificate {w : CardEnv} (ps : List (CAdmission w)) (c : CAdmission w) (cert : CardCertificate) :
    Except String Bool
def admitDocument (w : CardEnv) (d : Lean.Json) : Except String CardReport

/-- An accepted certificate is a W6a certificate of the regenerated problem, bound to the cardinality identities. -/
theorem checkCertificate_sound {w : CardEnv} (ps : List (CAdmission w)) (c : CAdmission w)
    (cert : CardCertificate) (h : checkCertificate ps c cert = .ok true) :
    cert.environmentId = w.environmentId ∧ cert.premiseIds = ps.map (·.meaningId) ∧
      cert.conclusionId = c.meaningId ∧ CEntails.{v} w.env (ps.map (·.formula)) c.formula

/-- A Lean-admitted cardinality document's root holds wherever its leaves hold. -/
theorem admit_cardinality_report_sound (w : CardEnv) (d : Lean.Json) (res : CardReport)
    (h : admitDocument w d = .ok res) : CardReport.Sound.{v} w.env res
```

The recipe's two equations, not elaborated (section 8): `VE.Service.runMode_cardinality (j : Json) : runMode
.cardinality j = VE.Cardinality.Run.runCaseReported j := rfl`, in the form of `runMode_discourse`
(`lean/VE/Service/Protocol.lean:721`); and `ResponseShape.Encoders.Cardinality.runCaseReported_fits (j : Json) :
Fits j Skeletons.cardinality (VE.Cardinality.Run.runCaseReported j)`, in the form of
`ResponseShape.Encoders.Discourse.runCaseReported_fits` (`lean/ResponseShape/Encoders/Discourse.lean:246`).

## 5. QS-1: order closure (`lean/VE/Closure/Order.lean`, `Paths.lean` unchanged)

```lean
namespace VE.Closure

/-- A finite order: `(a, b) ∈ edges` says `a` is directly above `b`. -/
structure Order (α : Type) where
  elems : List α
  edges : List (α × α)

structure Caps where
  elems : Nat
  edges : Nat

def Order.admit {α : Type} [DecidableEq α] (c : Caps) (o : Order α) : Except String Unit :=
  if o.elems.length > c.elems then .error s!"ResourceLimit: At most {c.elems} grades"
  else if o.edges.length > c.edges then .error s!"ResourceLimit: At most {c.edges} order pairs"
  else if o.edges.all (fun e => o.elems.contains e.1 && o.elems.contains e.2) then .ok ()
  else .error "UnknownSymbol: an order pair names an undeclared element"

def Order.above {α : Type} [DecidableEq α] (o : Order α) (a b : α) : Bool := reachEval .plus o.edges a b
def Order.atLeast {α : Type} [DecidableEq α] (o : Order α) (a b : α) : Bool := reachEval .star o.edges a b

theorem path_iff_transGen {α : Type u} {R : α → α → Prop} {a b : α} : Path R a b ↔ Relation.TransGen R a b
theorem reachable_star_iff {α : Type u} {R : α → α → Prop} {a b : α} :
    Reachable .star R a b ↔ a = b ∨ Relation.TransGen R a b
theorem atLeast_refl {α : Type} [DecidableEq α] (o : Order α) (a : α) : o.atLeast a a = true
theorem atLeast_trans {α : Type} [DecidableEq α] (o : Order α) {a b c : α}
    (h₁ : o.atLeast a b = true) (h₂ : o.atLeast b c = true) : o.atLeast a c = true
theorem above_iff {α : Type} [DecidableEq α] (o : Order α) (a b : α) :
    o.above a b = true ↔ Relation.TransGen (fun x y => (x, y) ∈ o.edges) a b
theorem atLeast_iff {α : Type} [DecidableEq α] (o : Order α) (a b : α) :
    o.atLeast a b = true ↔ a = b ∨ Relation.TransGen (fun x y => (x, y) ∈ o.edges) a b
/-- `VE.SoftNorms.outranksPlus` agrees with `above` (soft file unedited). -/
theorem outranksPlus_eq_above (env : VE.SoftNorms.SoftEnv) (hv : VE.SoftNorms.RanksValid env) (a b : String) :
    VE.SoftNorms.outranksPlus env a b = (Order.mk env.ranks env.outranks).above a b
/-- `VE.Risk.closure` agrees with `above` (risk file unedited). -/
theorem risk_closure_eq (R : VE.Risk.RiskDoc)
    (hd : ∀ e ∈ R.risk.severity.edges, e.1 ∈ R.classes ∧ e.2 ∈ R.classes) (a b : String) :
    (VE.Risk.closure R).contains (a, b) = (Order.mk R.classes R.risk.severity.edges).above a b

end VE.Closure
```

`Relation.TransGen` is in the pinned core (`Init/Core.lean:1348`); `Relation.ReflTransGen` is not, so reflexive
agreement is `a = b ∨ TransGen`. Acyclicity stays `VE.Route.kahn`. QS-1 is an order closure only, with no numbers and
no units; each consumer keeps its own meaning (attitudes' likelihood table and gating; weighing's rule that a strict
pair needs a chain containing an `always` edge; QT-B1's grade order).

## 6. Track B: `scales@0`

### 6.1 Declarations and premises (QT-B1)

The block is `vocabulary.scales` (decision b): a list of dimensions. A dimension names a compared sort, a comparative
predicate, optionally an equative predicate and "any two can be compared" (only with an equative), graded words (W2
open terms, each with a direction) and `above` pairs ("whatever is g is h") within one direction. Every predicate is
ordinary declared vocabulary. "A majority" is not a graded word; it is a proportion (track A). "The vast majority
implies more than half" waits for a proved bridge from scales to cardinality (QX-4's plan item); no fidelity credit
is claimed for it.

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

def Dimension.symbols (d : Dimension) : List String := d.more :: (d.same.toList ++ d.grades.map (·.name))
def ScaleDoc.symbols (D : ScaleDoc) : List String := D.dims.flatMap Dimension.symbols

/-- The grade order of a dimension is a QS-1 `Order`. -/
def gradeOrder (d : Dimension) : VE.Closure.Order String := ⟨d.grades.map (·.name), d.above⟩
def gradeCaps : VE.Closure.Caps := ⟨16, 64⟩

def aboveNodes (d : Dimension) : List VE.Route.DepNode :=
  d.grades.map fun g => ⟨g.name, (d.above.filter (·.1 == g.name)).map (·.2)⟩

def okB {ε β : Type} : Except ε β → Bool
  | .ok _ => true
  | .error _ => false

/-- One dimension per predicate; predicates declared with the right signatures; `comparable` only with `same`; grades
are W2 open terms; `above` pairs within one dimension and one direction, within QS-1's caps, acyclic by `kahn`. -/
def WellFormed (E : VE.Environment) (openTerms : List String) (D : ScaleDoc) : Bool :=
  (D.symbols.length == (VE.Cardinality.firstUse D.symbols).length) && D.dims.all fun d =>
    E.sorts.contains d.sort &&
    E.predicates d.more == some [d.sort, d.sort] &&
    (match d.same with
     | some e => E.predicates e == some [d.sort, d.sort]
     | none => !d.comparable) &&
    d.grades.all (fun g => E.predicates g.name == some [d.sort] && openTerms.contains g.name) &&
    d.above.all (fun p => match d.grades.find? (·.name == p.1), d.grades.find? (·.name == p.2) with
      | some g, some h => g.direction == h.direction && p.1 != p.2
      | _, _ => false) &&
    okB ((gradeOrder d).admit gradeCaps) &&
    okB (VE.Route.dependencyOrder (aboveNodes d))

def rel2 (p : String) (i j : Nat) : VE.Formula := .binary p (.var i) (.var j)
def rel1 (p : String) (i : Nat) : VE.Formula := .unary p (.var i)

/-- The labelled premises of one dimension. Under `.all s (.all s φ)`, `x` is `var 1` and `y` is `var 0`. -/
def premises (d : Dimension) : List (String × VE.Formula) :=
  let s := d.sort
  let m := d.more
  let lbl := fun (x : String) => d.name ++ "/" ++ x
  let all2 := fun (φ : VE.Formula) => VE.Formula.all s (.all s φ)
  let all3 := fun (φ : VE.Formula) => VE.Formula.all s (.all s (.all s φ))
  [(lbl "irreflexive", .all s (.not (rel2 m 0 0))),
   (lbl "transitive", all3 (.implies (.and (rel2 m 2 1) (rel2 m 1 0)) (rel2 m 2 0)))] ++
  (match d.same with
   | none => []
   | some e =>
     [(lbl "same-reflexive", .all s (rel2 e 0 0)),
      (lbl "same-symmetric", all2 (.implies (rel2 e 1 0) (rel2 e 0 1))),
      (lbl "same-transitive", all3 (.implies (.and (rel2 e 2 1) (rel2 e 1 0)) (rel2 e 2 0))),
      (lbl "same-not-more", all2 (.implies (rel2 e 1 0) (.not (rel2 m 1 0)))),
      (lbl "same-left", all3 (.implies (.and (rel2 e 2 1) (rel2 m 1 0)) (rel2 m 2 0))),
      (lbl "same-right", all3 (.implies (.and (rel2 m 2 1) (rel2 e 1 0)) (rel2 m 2 0)))] ++
     (if d.comparable then
       [(lbl "comparable", all2 (.or (rel2 m 1 0) (.or (rel2 m 0 1) (rel2 e 1 0))))] else [])) ++
  d.grades.flatMap (fun g =>
    [(lbl (g.name ++ "/closed"), all2 (.implies
        (.and (rel1 g.name 0) (match g.direction with
          | .upper => rel2 m 1 0
          | .lower => rel2 m 0 1)) (rel1 g.name 1)))] ++
    (match d.same with
     | some e => [(lbl (g.name ++ "/same"), all2 (.implies (.and (rel1 g.name 0) (rel2 e 1 0)) (rel1 g.name 1)))]
     | none => [])) ++
  d.above.map (fun p => (lbl (p.1 ++ "/above/" ++ p.2), .all s (.implies (rel1 p.1 0) (rel1 p.2 0))))

def scalePremises (D : ScaleDoc) : List (String × VE.Formula) := D.dims.flatMap premises
```

Nothing else is generated: no density, no end points unless declared as constants with facts, no threshold, no
number.

### 6.2 Meaning and theorems (QT-B1)

```lean
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

/-- No symbol of `D` occurs in `a`. -/
def Fresh (D : ScaleDoc) (a : VE.Formula) : Prop := ∀ p ∈ VE.Norms.preds a, p ∉ D.symbols

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
graded word closed in its direction (Kennedy's degrees and Klein's relations agree). -/
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

/-- **Conservative**: formulas without scale symbols have the same consequences with the scale premises. -/
theorem scales_conservative (E : VE.Environment) (ots : List String) (D : ScaleDoc)
    (hD : WellFormed E ots D = true) (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, Fresh D a) (hφ : Fresh D φ) :
    VE.Entails.{u} E (Γ ++ (scalePremises D).map (·.2)) φ ↔ VE.Entails.{u} E Γ φ

/-- **No threshold is chosen**: for each graded word, the premises alone have a model where an object has it and one
where it does not. -/
theorem grade_open (E : VE.Environment) (ots : List String) (D : ScaleDoc) (hD : WellFormed E ots D = true)
    (d : Dimension) (hd : d ∈ D.dims) (g : Grade) (hg : g ∈ d.grades) :
    (∃ S : VE.Structure.{0}, S.Admissible E ∧
      (∀ a ∈ (scalePremises D).map (·.2), a.denote S []) ∧ ∃ x, S.domain d.sort x ∧ S.relation g.name [x]) ∧
    (∃ S : VE.Structure.{0}, S.Admissible E ∧
      (∀ a ∈ (scalePremises D).map (·.2), a.denote S []) ∧ ∃ x, S.domain d.sort x ∧ ¬ S.relation g.name [x])

/-- The premises are well typed; at `E := envAt (fill U) 0` this is the `scales` pack's typing obligation. -/
theorem premises_wellTyped (E : VE.Environment) (ots : List String) (D : ScaleDoc) (hD : WellFormed E ots D = true) :
    ∀ a ∈ (scalePremises D).map (·.2), a.WellFormed E []

end VE.Scales
```

`intended_iff_degrees` reads the degrees as the classes of "as much as" over the sort's objects, with the objects
outside the sort in one lowest class (classical case split; `Quot.sound` is a standard axiom).

### 6.3 QT-B2: the `scales` pack and the `scales-coherence` kind

PK-1's `scales` pack: `kind := .constraint` (decision e), `decls := []`, `labelled := scalePremises D`, `origins`: each
label ↦ its request path (`["environment", "vocabulary", "scales", <i>]`). Typing is `scales_pack_wellTyped`. On the
readings route QT-B2 proves `VE.Readings.Transfers D Q (fun _ => Q)` for `Q := (scalePremises S).map (·.2)`; its
hypotheses (the scale symbols are base predicates, untouched by `pull`) are fixed in QT-B2's statement pass with
PK-1's review, because PK-1 is not on `main` (section 8).

```lean
namespace VE.Scales

theorem scales_pack_wellTyped (U : VE.NormDefaults.UDoc) (ots : List String) (D : ScaleDoc)
    (hD : WellFormed (VE.Norms.envAt (VE.NormDefaults.fill U) 0) ots D = true) :
    ∀ a ∈ (scalePremises D).map (·.2), a.WellFormed (VE.Norms.envAt (VE.NormDefaults.fill U) 0) []

/-- No guard, carve-out or definition of the filled tree mentions a scale symbol. -/
def GuardsFresh (U : VE.NormDefaults.UDoc) (D : ScaleDoc) : Prop :=
  (∀ N ∈ (VE.NormDefaults.fill U).T.nodes, Fresh D N.guard ∧ ∀ c ∈ N.carveOuts, Fresh D c) ∧
  ∀ q ∈ (VE.NormDefaults.fill U).T.definitions, Fresh D q.body

/-- With no guard and no other extra premise mentioning scale structure, conflict-freedom is unchanged. -/
theorem scales_conflictFree_iff (U : VE.NormDefaults.UDoc) (X : List VE.Formula) (ots : List String)
    (D : ScaleDoc) (hD : WellFormed (VE.Norms.envAt U.D 0) ots D = true) (hguards : GuardsFresh U D)
    (hX : ∀ a ∈ X, Fresh D a) :
    VE.NormDefaults.Wire.ConflictFreeX.{u} U X ↔
      VE.NormDefaults.Wire.ConflictFreeX.{u} U (X ++ (scalePremises D).map (·.2))

/-- A ground instance of a labelled premise: its label and the constants for its universal binders, outermost
first. -/
structure Instance where
  label : String
  args : List String
  deriving DecidableEq, Repr

def stripAll : VE.Formula → List String × VE.Formula
  | .all s a => let r := stripAll a; (s :: r.1, r.2)
  | a => ([], a)

def instantiate (X : List (String × VE.Formula)) (i : Instance) : Option VE.Formula := do
  let p ← X.find? (·.1 == i.label)
  let r := stripAll p.2
  if r.1.length = i.args.length then some (VE.Norms.inst (i.args.reverse.map VE.Term.const) r.2) else none

inductive CoherenceResult where
  | coherent (M : VE.FiniteModel VE.Bridge.Entity)
  | incoherent (instances : List Instance) (cert : VE.Tableau.Certificate)
  | unknown (reason : String)

/-- COHERENT: a valid finite model of the facts and the whole assembled X. INCOHERENT: every listed instance follows
from X, and the facts with the listed instances entail ⊥ (so the facts with X do). UNKNOWN: nothing is claimed. -/
def CoherenceResult.Sound (E : VE.Environment) (X : List (String × VE.Formula)) (facts : List VE.Formula) :
    CoherenceResult → Prop
  | .coherent M => M.Valid E ∧ ∀ a ∈ facts ++ X.map (·.2), a.eval M [] = true
  | .incoherent is _ =>
      (∀ i ∈ is, ∃ φ, instantiate X i = some φ ∧ VE.Entails.{u} E (X.map (·.2)) φ) ∧
      VE.Entails.{u} E (facts ++ is.filterMap (instantiate X)) .bottom
  | .unknown _ => True

def checkCoherence (E : VE.Environment) (X : List (String × VE.Formula)) (facts : List VE.Formula) :
    Except String CoherenceResult

theorem coherence_sound (E : VE.Environment) (X : List (String × VE.Formula)) (facts : List VE.Formula)
    (r : CoherenceResult) (h : checkCoherence E X facts = .ok r) : CoherenceResult.Sound.{u} E X facts r

end VE.Scales
```

`checkCoherence` checks a COHERENT model with `VE.FiniteModel.Valid` and `eval`, and an INCOHERENT refutation by
instantiating each listed instance itself and replaying `cert` with `VE.Tableau.checkCertificate` on the facts plus
the ground instances. Python's search proposes either; it is never trusted. One failing instance is not enough in
general: the three-step cycle needs three (FB5).

## 7. English (QT-A6 and QT-B3; rows of english-lean's catalogue)

Every wording below has one reading. The first wording of a row is Lean's canonical rendering; the paraphrase is
Lean's English line for the canonical `F` (the `paraphrase` case kind). Rendering parses back to the same canonical
`F` (english-lean 3.5's per-output check). Number words follow W6a's lexer; thousands separators are an input alias
(groups of exactly three digits).

### 7.1 Counts and proportions

| Wording | Canonical `F` | Paraphrase |
|---|---|---|
| "Exactly 16 FOMC policymakers expect a further increase." | `count ⟨fomc_policymaker, [(1, is expects_further_increase)], eq, 16⟩` | "The number of FOMC policymakers who expect a further increase is 16." |
| "At least 16 FOMC policymakers expect a further increase." | `count (atLeastAtom …16)` | "The number of FOMC policymakers who expect a further increase is 16 or more." |
| "At most 2 FOMC policymakers expect rates to stay where they are." | `count (atMostAtom …2)` | "The number of FOMC policymakers who expect rates to stay where they are is 2 or fewer." |
| "Exactly 16 of the 18 FOMC policymakers expect a further increase." | `nOfMFormula fomc_policymaker 16 18 any (is expects_further_increase)` | "There are exactly 18 FOMC policymakers, and exactly 16 of them expect a further increase." |
| "At least 16 of the 18 FOMC policymakers expect a further increase." | `and (count (exactlyAtom … any 18)) (count (atLeastAtom … 16))` | "There are exactly 18 FOMC policymakers, and 16 or more of them expect a further increase." |
| "At most 2 of the 18 FOMC policymakers expect rates to stay where they are." | `and (count (exactlyAtom … any 18)) (count (atMostAtom … 2))` | "There are exactly 18 FOMC policymakers, and 2 or fewer of them expect rates to stay where they are." |
| "More than half of the users are curious." | `proportion ⟨user, any, is curious, gt, 1, 2⟩` | "There is at least one user, and the curious users are more than half of the users." |
| "At least half / less than half / at most half / exactly half of the users …" | `cmp` `ge` / `lt` / `le` / `eq`, `1` in `2` | as above, with "at least half", "less than half", "at most half", "exactly half" |
| "At least 1 in 1,000 of the users intend harm." | `proportion ⟨user, any, is intends_harm, ge, 1, 1000⟩` | "There is at least one user, and the users who intend harm are at least 1 in 1,000 of the users." |
| "More than 2 in 3 of the users who logged in are curious." | `proportion ⟨user, is logged_in, is curious, gt, 2, 3⟩` | "There is at least one user who logged in, and the curious ones are more than 2 in 3 of the users who logged in." |

### 7.2 Rounding and percent

The place word must match the written places: 0 places "to the nearest whole number" (for percent "to the nearest
percent"), 1 "tenth", 2 "hundredth", 3 "thousandth", 4 "ten-thousandth", more "to k decimal places" (for percent "to
the nearest tenth of a percent", …). A mismatch ("rounds to 0.30, rounded to the nearest tenth") is refused (7.3).

| Wording | Canonical `F` | Paraphrase |
|---|---|---|
| "The number of false approvals out of the number of scored decisions rounds to 0.296, rounded to the nearest thousandth with exact ties going up." | `roundsTo tiesUp (count decision (scored ∧ false_approval)) (count decision scored) 296 3` | "There is at least one scored decision, and the number of false approvals among them divided by the number of scored decisions, rounded to the nearest thousandth, is 0.296; a value exactly halfway rounds up, to the larger number." |
| "… rounds to 0.296, rounded to the nearest thousandth with exact ties going to the even digit." | `roundsTo halfEven …` | "…; a value exactly halfway rounds to the one whose last digit is even." |
| "The September PCE estimate is exactly 105 percent of the June PCE estimate." | `percentOf sep jun 105 0` | "The June PCE estimate is more than zero, and the September PCE estimate times 100 equals the June PCE estimate times 105." |
| "The September PCE estimate is exactly 5 percent more than the June PCE estimate." | the same `F` (renders as the row above) | as above |
| "The September PCE estimate is 103 percent of the June PCE estimate, to the nearest percent with exact ties going up." | `percentRoundsTo tiesUp sep jun 103 0` | "The June PCE estimate is more than zero, and the September PCE estimate as a percentage of the June PCE estimate, rounded to the nearest percent, is 103; a value exactly halfway rounds up." |
| "GBP 35,000.00", "1,000 users" | W6a literals `35000.00`, `1000` | W6a's canonical rendering, unchanged (no separators) |

### 7.3 Refusals with rewrites (authoring)

| Input | Catalogue row | Rewrites offered |
|---|---|---|
| "Most users are curious." | "most" | "More than half of the users are curious." |
| "Multiple users complained." | "multiple" (with "most") | "At least two users complained." |
| "Many / few / several / a lot of users …" | "many", "few", "several", "a lot of" | "At least N users …", "More than N in M of the users …" (the author supplies N, M) |
| "16 of the 18 FOMC policymakers expect …" | bare count | "Exactly 16 of the 18 …", "At least 16 of the 18 …" |
| "1 in 1,000 users intend harm." | bare count (same row) | "Exactly 1 in 1,000 of the users …", "At least 1 in 1,000 of the users …" |
| "… is 105 percent of …" | bare "105 percent of" | "… is exactly 105 percent of …"; "… is 105 percent of …, to the nearest percent with exact ties going up"; "…, with exact ties going to the even digit" |
| "… rounds to 0.296." | "rounds to" with no tie rule | "…, rounded to the nearest thousandth with exact ties going up"; "…, rounded to the nearest thousandth with exact ties going to the even digit" |
| "… about 103 percent of …"; "approximately", "roughly", "nearly" | "about" (one row, shared with math-evidence; QT-A6 adds it, ME-11 reuses it) | "… is 103 percent of …, to the nearest percent with exact ties going up" |
| "… rounds to 0.30, rounded to the nearest tenth …" | rounding places | "rounds to 0.3, rounded to the nearest tenth"; "rounds to 0.30, rounded to the nearest hundredth" |
| "…, rounded down / rounded up" | rounding rule | the two admitted rules (decision d) |
| "1,00", "1,0000", ",100" | number | "100" or "1,000" (groups of exactly three digits) |

No symbol appears in any wording, paraphrase or diagnostic.

### 7.4 Translation reading sets

| Source | Reading set | Distinguishing model |
|---|---|---|
| bare "16 of the 18 … expect X" | {exactly 16 of the 18; at least 16 of the 18} | 17 of the 18 expect X |
| "only 2 of the 18 …" | one reading, "exactly 2 of the 18": "only" excludes more, and the sentence says the 2 do | — (FA1c shows what "at most 2" would change) |
| bare "105 percent of" | {exactly 105 percent of; 105 percent of to the nearest percent, each admitted rule} | 105.4 percent |
| "rounds to 0.296" with no stated rule (VE's paper: "176/594 = .296") | one member per admitted rule | a value exactly halfway (none when the value is not a tie: then every member agrees, FA4) |
| "most" | {more than half; an open proportion grade (a W2 open term)}; further members pending QX-1 | 51 of 100 |
| "multiple" | {at least two}; further members pending QX-1 | — |

QT-A5 keeps a source's stated tie convention, or reports the rounding as unresolved; it never imposes one.

### 7.5 Track B (QT-B3)

| Wording | Meaning | Paraphrase |
|---|---|---|
| "Responses are compared by uplift: one response gives more uplift than another." | a dimension `uplift` on `response`, comparative `gives_more_uplift` | "Uplift is a way to compare responses: one can give more uplift than another; no response gives more uplift than itself, and more-than is transitive." |
| "Two responses can give equal uplift." | `same := some gives_as_much_uplift` | "… Two responses can give the same uplift …" |
| "Any two responses can be compared by uplift." | `comparable := true` | "For any two responses, one gives more uplift than the other, or they give the same uplift." |
| "Serious uplift is a degree of uplift decided by <decider>." | grade `gives_serious_uplift`, upper, a W2 open term | "Whether uplift is serious is decided by <decider>; a response that gives more uplift than one that gives serious uplift also gives serious uplift." |
| "Very serious uplift is serious uplift." | `above (gives_very_serious_uplift, gives_serious_uplift)` | "Every response that gives very serious uplift gives serious uplift." |
| "Response A gives more uplift than response B." / "Response A gives serious uplift." / "A is paid as much as B." | ground facts | as written |

Refusals with rewrites: a comparative or "very X" on an undeclared dimension ("Declare it first: 'Acts are compared
by harm: …'"); "more X than" across two dimensions; "substantially more" (a grade of a difference, R5.2); "a
majority" as a graded word (rewrite: "more than half of …", track A).

## 8. What the stub checked, and what it did not

- **Elaborated** (33 statements, each a `def … : Prop`): `admits_sound`, `admits_complete`,
  `hasCount_exists_unique`, `withRegions_admissible`, `nonneg_hold`, `bridge_hold`, `erase_iff`,
  `cardinality_elab_sound`, `count_atLeast_agree`, `count_atMost_agree`, `count_exactly_agree`, `count_nOfM_agree`,
  `proportion_holds_iff`, `roundsTo_ratio_agree`, `refutesC_sound`, `checkCertificate_sound`,
  `admit_cardinality_report_sound`, `path_iff_transGen`, `reachable_star_iff`, `atLeast_refl`, `atLeast_trans`,
  `above_iff`, `atLeast_iff`, `outranksPlus_eq_above`, `risk_closure_eq`, `premises_iff_intended`,
  `intended_iff_degrees`, `scales_conservative`, `grade_open`, `premises_wellTyped`, `scales_pack_wellTyped`,
  `scales_conflictFree_iff`, `coherence_sound`.
- **Stand-ins**: `VE.Numbers` (ME-1's, copied from SYNTHESIS 2.4 with ME-PLAN 3.1's bodies); `checkCertificate`,
  `admitDocument` and `checkCoherence` as `opaque` (their bodies are QT-A3's and QT-B2's).
- **Not elaborated**: `runMode_cardinality` and `runCaseReported_fits` (need the mode constructor and the generated
  skeleton); QT-B2's `Transfers` statement (needs PK-1). Their forms are given in 4.3 and 6.3.
- **Not proved**: any theorem. Computed fixtures check a statement on examples; they are evidence that it is not false
  there, not a proof.

## 9. Acceptance fixtures (computed)

All numbers below were computed in the stub with `#eval`. "Meaning" is a direct evaluation of `CFormula.holds`'s
clauses on a finite model; "erasure" evaluates the erased formula on `withRegionsFinite` of the same model.

### 9.1 Track A

**FA1 (news S3, `s3_count`).** Source: "16 of the 18 FOMC policymakers expect at least one more quarter-point rate
increase …, with only 2 of the 18 expecting rates to stay where they are." Finite sort `fomc_policymaker`; predicates
`expects_further_increase`, `expects_rates_to_stay`. Premises: exactly 18; exactly 16 increase; exactly 2 stay; "no
policymaker expects both" (the translator's stated premise). Conclusion: "every policymaker expects a further increase
or expects rates to stay".
- All five statements are admitted. Regions: `cardinality__fomc_policymaker__00`, `__01`, `__10`, `__11` (first bit:
  increase). Two bridge premises (the exclusion and the conclusion). The erased problem has 91 formula and term nodes.
- Every model of the sort with 18 objects, up to the two predicates, is one of 1,330 region-size vectors. Countermodels
  among them: **0** with "exactly 16", and **0** with "at least 16" (both readings of the bare count give the
  conclusion).
- **FA1b** (no exclusion premise): **2** countermodels, region sizes (neither, stay only, increase only, both) =
  (1, 1, 15, 1) and (2, 0, 14, 2). On (1, 1, 15, 1): the premises' meanings are (true, true, true), the conclusion's is
  false; `refutesC` is true; meaning and erasure agree on all four statements (conclusion false/false, premises
  true/true); both bridges hold.
- **FA1c** ("at least 16" with "at most 2", exclusion kept): **3** countermodels, (1, 0, 17, 0), (1, 1, 16, 0),
  (2, 0, 16, 0). So the reading of "only 2 of the 18" matters (7.4).

**FA2 (agreement with W6a's four forms).** Models of 6, 7 and 8 objects with 0 to all flagged; `n`, `m` from 0 to 8;
each of `atLeast`, `atMost`, `exactly`, `nOfM` against `VE.Time.atLeast`, `atMost`, `exactly`, `nOfM` evaluated by
`VE.Order.Formula.eval`: 7,776 comparisons, **0** disagreements, 2,400 both true, 5,376 both false.

**FA3 (caps).** "Exactly 16 of the 18" is admitted here (computed) and refused by W6a's sugar (`CountingBound(exactly
7)`, `lean/VE/Time/Wire.lean:741–742`, read, not run).

**FA4 (rounding; VE's paper `paper/sections/04-e1.md`).** Each pair is (erased form, `RoundsTo`):

| Claim | Numbers | `tiesUp` | `halfEven` |
|---|---|---|---|
| 176 out of 594 rounds to 0.296 | 591 × 594 = 351,054 ≤ 2,000 × 176 = 352,000 < 593 × 594 = 352,242 | (true, true) | (true, true) |
| 176 out of 594 rounds to 0.297 | | (false, false) | |
| 52 out of 243 rounds to 0.214; 31 out of 243 to 0.128 | | (true, true) each | |
| 21 out of 243 rounds to 0.086 | 41,553 ≤ 42,000 < 42,039 | (true, true) | |
| 26 out of 100 rounds to 0.3 / to 0.30 | one place against two | (true, true) / (false, false) | |
| **1 out of 8 rounds to 0.13 / to 0.12** | 0.125 is a tie | **(true, true) / (false, false)** | **(false, false) / (true, true)** |
| 1/2 to 0 places: 0 / 1; 3/2: 2 / 1 | ties | 0 false, 1 true | 0 true; 2 true, 1 false |
| −1/2 to 0 places: 0 / −1 | ties go to the larger value | 0 true, −1 false | |

`roundsTo_ratio_agree` on a grid (a from −12 to 12, b from 1 to 8, D from −20 to 20, k from 0 to 2, all four rules):
98,400 points, **0** disagreements, 1,424 both true, 96,976 both false.

**FA4c (counts as operands).** 594 scored decisions, 176 of them false approvals (region sizes 5, 418, 0, 176 over
false approval and scored): the claim is admitted; "rounds to 0.296" true by meaning and by erasure; "0.297" false by
both.

**FA5 (news, PCE in basis points: September 370, June 360).**

| Claim | Admitted | Meaning | Erasure |
|---|---|---|---|
| September out of June rounds to 1.028, ties up (2,055 × 360 = 739,800 ≤ 740,000 < 740,520 = 2,057 × 360) | true | true | true |
| … to 1.028, ties to even | true | true | true |
| … is 103 percent of June, to the nearest percent, ties up | true | true | true |
| … is exactly 103 percent of June (37,000 ≠ 37,080) | true | false | false |
| … is exactly 102.7778 percent of June (370,000,000 ≠ 370,000,080) | true | false | false |

"About 103 percent" is refused (7.3).

**FA6 (separators).** Accepted: "1,000" → 1000, "35,000.00" → 35000.00, "1,000,000", "1000", "12,345.6". Refused:
"1,00", "1,0000", ",100", "1,,000", "1234,567". "35000.00" lowers at 2 places to **3,500,000** (`gbp_penny`).

**FA7 (refusal).** Bare "16 of the 18" is refused with both rewrites (QT-A6's catalogue row; English, not computable
before QT-E).

**FA8 (hostile).** Admission is false for: a count over a sort not declared finite; a body with a binary predicate; a
body predicate of another sort; a proportion 3 in 2; a proportion with denominator 0; and true for "exactly 16" on the
finite sort. A count with seven predicates on one sort is admitted and refused by the limits:
`ResourceLimit: At most 6 predicates on counted sort fomc_policymaker (64 regions)`; with six it passes. A W6a
universal statement over the finite sort with seven predicates and no count: **0** regions, limits pass; adding a
count over that sort makes the limit fire (C5). An `above` cycle: `DependencyCycle: gives_serious_uplift,
grave_uplift`.

**FA9 (the debate's adversarial examples).**
- **a. Colliding region constant.** A declared dimensionless constant `cardinality__fomc_policymaker__0` set to 5, a
  count over the sort with one predicate (regions `…__0` and `…__1`, region 0 empty). Both statements are admitted;
  the name starts with the region prefix, so `CEnv.WellFormed.fresh` fails and the decoder refuses it (E8). Without
  that check, "the constant is 5" is true by meaning and false by erasure: `erase_iff` without `hE` is false.
- **b. Three-step cycle**: FB5 below.
- **c. Empty population.** No users: "at least 1 in 1,000 of the users intend harm" is **false** as a proportion; the
  bare count atom `−1,000 × #harm + #users ≤ 0` is **true**. 999 + 1 users with 1 intending harm: true; 1,000 users,
  none: false; 1,000 + 1 users, 1: false (1 in 1,001 is less than 1 in 1,000); 1,001 + 1, 1: false. "More than half":
  no users false; 2 of 4 false; 3 of 5 true. Meaning and erasure agree on both proportions, on an empty and a
  five-user model.
- **d. The 1 out of 8 tie under each rule**: FA4.
- **e. Duration-to-date cast.** A rounding of two `day` quantities: refused; of two `elapsed_day` quantities:
  admitted; of `bp` against `day`: refused (`UnitMismatch`); with rule `down`: refused (`UnsupportedRounding`).
  QT-A7's conversion `week → elapsed_day` and the refusal of `week → day` are ME-6's registry's fixtures (not
  computable before ME-6).

**FA10 (`proportion_holds_iff`, both directions).** The rows of FA9c: the meaning is true exactly on the nonempty
models with the share above the fraction.

### 9.2 QS-1

- Order `a > b > c`, `d` alone: `above a c` true, `above c a` false, `above a a` false, `atLeast a a` true,
  `atLeast d a` false, `atLeast a c` true.
- `Order.admit ⟨16, 64⟩`: 17 elements → `ResourceLimit: At most 16 grades`; the order above → ok; an edge to an
  undeclared element → `UnknownSymbol: an order pair names an undeclared element`.
- `outranksPlus_eq_above` on a soft environment with ranks a, b, c, d and edges a > b > c: 16 pairs, **0**
  disagreements, 3 true.
- `risk_closure_eq` on classes a, b, c, d with edges a > b > c > d (`closeIter` as `VE.Risk.closure` computes it):
  16 pairs, **0** disagreements, 6 true.

### 9.3 Track B

- **FB1 (u0165.s01).** Dimension `uplift` on `response`, grade `gives_serious_uplift` (upper). Facts: r1 gives serious
  uplift; r2 gives more uplift than r1; r2 does not give serious uplift. Over two responses: 64 models, **0** satisfy
  the facts and the premises (INCOHERENT); the one instance `uplift/gives_serious_uplift/closed` at (r2, r1)
  instantiates, and the facts with it alone have **0** models.
- **FB1 lower twin and its seeded bug.** Dimension `harm`, grade `minor_harm` (lower). Facts: r1's harm is minor; r1
  is more harmful than r2; r2's harm is not minor. Correct premises: **0** models (INCOHERENT). With the lower closure
  generated with the comparative reversed: **1** model (wrongly COHERENT), so the fixture fails on the bug.
- **FB2 (dial, u0226.s01, s02).** Constants `fully_corrigible`, `fully_autonomous`, facts that every other
  disposition lies strictly between; "a disposition more autonomous than fully autonomous" is refuted (a certificate
  fixture of QT-B1; not computed here).
- **FB3 (u0043.s01).** "Different levels of trust" is a reading set {not all the same; pairwise different}. With
  Anthropic and operators equally trusted and users less: (true, false), the distinguishing model; with three levels:
  (true, true).
- **FB4 (UDHR u094).** "All children enjoy the same social protection" is `∀c₁ c₂. same(c₁, c₂)` (statement form).
- **FB5 (three-step cycle).** Facts r1 > r2, r2 > r3, r3 > r1, premises irreflexive and transitive. Of the 512
  relations on three responses, **0** satisfy facts and premises. The refutation {transitive (r1, r2, r3), transitive
  (r1, r3, r1), irreflexive (r1)}: all 3 instantiate, and the facts with them have **0** models. Each of the **30**
  ground instances alone (3 irreflexive, 27 transitive) holds in some model of the facts, so no single instance is
  false in every model of the facts.
- **FB6 (u0165.s05).** Grade `vast_majority` (upper) on `share_of_humanity_targeted`: the premises hold in a model
  where the one attempt has the grade and in one where it does not (`grade_open`'s two witnesses).
- **FB8 (hostile `WellFormed`).** False for: a comparative that is not declared; an `above` cycle; `above` across
  directions; `comparable` without `same`; a graded word that is not a W2 open term. True for: the FB1 dimension;
  the same dimension with another declared open-term grade; the chain "grave uplift above serious uplift".

### 9.4 Seeded bugs (from the plan, with the fixture each breaks)

| Batch | Bug | Fixture that fails |
|---|---|---|
| QT-A1 | `Body.inRegion` reads `not b` as `b` | FA1's certificate replay and FA1b's countermodel |
| QT-A2 | the upper bound erased with `≤` | FA4's `tiesUp` tie: "1 out of 8 rounds to 0.12" becomes true |
| QT-A3 | the decoder accepts a count whose sort is not in `finite_sorts` | FA8's hostile route case |
| QT-A4 | the binding check skips the region table | a fuzz mutant that renames a region is accepted |
| QT-B1 | the lower closure generated with the comparative reversed | FB1's lower twin (computed above) |
| QT-B2 | Lean: the block's premises dropped on one reading choice; Python: the binding check skips an instance's label | an enumerated fixture; a fuzz mutant |

### 9.5 Each "exactly when" claim, both directions

| Claim | True on both sides | False on both sides |
|---|---|---|
| `admits_sound` / `admits_complete` | FA1, FA4c, FA5 (admitted) | FA8, FA9e (refused) |
| `erase_iff` | FA1b premises; FA4c "0.296"; FA5 rows 1–3; FA9c "at least 1 in 1,000" on five users | FA1b conclusion; FA4c "0.297"; FA5 rows 4–5; FA9c both proportions with no users, "more than half" on five users |
| `count_*_agree` (four forms) | FA2: 2,400 | FA2: 5,376 |
| `proportion_holds_iff` | FA9c: 999 + 1, 3 of 5 | FA9c: no users, 1,000 + 1, 2 of 4 |
| `roundsTo_ratio_agree` | FA4 grid: 1,424 | FA4 grid: 96,976 |
| `above_iff`, `atLeast_iff`, `outranksPlus_eq_above`, `risk_closure_eq` | 9.2: `above a c`; 3 and 6 true pairs | 9.2: `above c a`; 13 and 10 false pairs |
| `premises_iff_intended` | two trust models: premises true, `Intended` true | irreflexivity broken; "as much as" not transitive: both false |
| `intended_iff_degrees` | two levels: degrees (1, 1, 0), and 3 degree maps into a three-element order; three levels: 1 | "as much as" not transitive: `Intended` false and **0** of the 27 maps |
| `scales_conservative` | Γ = {r1 is flagged}, φ = "r1 is flagged" | φ = "r1 is reviewed": a model of Γ and the premises where it is false |
| `scales_conflictFree_iff` | FB7: the constitution's main document with an empty scales block keeps its probes byte-identical (QT-B2) | a guard that mentions a graded word is outside the theorem (`GuardsFresh` fails) |

## 10. Review checklist (plan section 9, with where each point is met)

- `CFormula.holds` and `Intended` state meanings without erasure or generated formulas: 3.3, 6.2.
- `cardinality_elab_sound` assumes only `Admissible` of the structure: 3.6.
- Region constants cannot collide (`CEnv.WellFormed`, a hypothesis of the four theorems; decoder E5–E8) and never
  appear as input: 3.2, 3.6, 4.2, FA9a.
- The four agreement theorems: 3.7, FA2.
- Every proportion requires a nonempty population, and the paraphrase says so: 3.3, 7.1, FA9c.
- `roundsTo` keeps the written places; the tie rule is stated in the sentence: 3.2, 7.2, FA4.
- `grade_open`; `scales_conservative` without an emptiness hypothesis: 6.2, FB6.
- INCOHERENT carries a checked refutation listing its instances; COHERENT a checked model; otherwise UNKNOWN: 6.3, FB5.
- Every refusal names a rewrite in plain English; no symbol in any wording or diagnostic: 7.3.
- The adversarial examples are computed: FA9.
- Every new trusted line has a signed allowance and a ROADMAP trust-cost line: each build batch's rule (plan 1.3).
