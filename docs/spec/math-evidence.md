# Science papers in VE: `calc@0`, physical dimensions, `arith@0` and proof imports (statement specification)

> **Status.** Item-1 specification (batch ME-S), draft 1 (2026-10-13), branch `design/math-evidence` from `main` at
> `49de179e`. Written from [math-evidence-PLAN.md](math-evidence-PLAN.md) draft 2 (cited `plan n`), which applies the
> converged Astra + Fable review of draft 1 (`manage-agents/debates/design-math-evidence/`, REVISE narrowly, CONVERGED
> after round 3; edits A1-A6 and F1-F5) and the cross-plan synthesis edits of 2026-10-13. Section 15 maps each debate
> edit to the statement and fixture that carry it.
>
> **How it was checked.** Every Lean statement in sections 1 to 12 was type-checked with Lean v4.24.0 against
> `main`'s `lean/` tree (built modules `VE.Time.Decimal`, `VE.Time.Budget`, `VE.CertificateWire`, `VE.Route.Wire`,
> `ResponseShape.Skeleton`) in an untracked stub, `lean/SpecStubs_math-evidence.lean`, run with
> `lake env lean SpecStubs_math-evidence.lean`: 0 errors. Proofs were `sorry` in the stub, and the stub was deleted
> before commit. Every fixture number in section 13 was computed in that stub with `#eval` or `decide` over core
> `Rat`, using the executable definitions given here; none was computed by hand. Names marked *opaque* below had only
> a signature in the stub: the batch defines them, and their statements were checked against the signature.
>
> **What this is not.** Theorem statements and fixtures are implementation obligations, not claims of completed
> proofs or tests. No model was called. The statement review by the reviewer pair (plan 9) has not run yet.
> Section 16 lists every point where this draft chose between readings of the plan.

## 0. Scope

`calc@0` checks the arithmetic of a document: stated numbers, named values defined from them, comparisons, rounding
claims, tables pinned by digest (ME-4), derivations over unknowns (ME-5), physical dimensions (ME-6), exact
statistics (ME-7), the consistency of printed numbers (ME-8) and algebraic identities (ME-9). `arith@0` states facts
about whole numbers and integers, decides those whose quantifiers are all bounded (ME-12), and admits proofs of the
rest from an external Lean project only as residual support (ME-13). Lean owns every meaning, verdict, diagnostic,
limit and English line; Python carries files and relays answers (plan D21); there is no Rust.

The sections follow the batches: the shared numbers `VE.Numbers` (1), the `calc@0` core (2), the wire and runner (3),
tables and source spans (4), derivations (5), physical dimensions (6), statistics (7), consistency and identities (8),
rendering and reading back (9), documents (10), English (11), `arith@0` and imports (12), diagnostics (13.1),
fixtures (13.2-13.5), limits and trust (14), the debate map (15) and the choices this draft made (16).

Out of scope: approximations with error bounds (EX-2), tensor shapes (EX-3), folds and induction inside `arith@0`
(EX-4), chunked data (EX-5), the calc–attitudes bridge for hedged calculations (no plan owns it), dates before 1970
(W6's trigger ET-T3), section-scoped rounding declarations (scope's anchor reach), real numbers in `arith@0`.

## 1. Shared numbers: `VE.Numbers` (ME-1)

Math-evidence owns `VE.Numbers` (`lean/VE/Numbers/`), on core `Rat` (`import Std`). Quantities' QT-A2 proves its
integer-ratio rounding against `VE.Numbers.RoundsTo` and lands after ME-1. `VE.Calc` and `VE.Arith` import it.

### 1.1 Decimal values (`lean/VE/Numbers/Decimal.lean`)

A decimal literal is read by W6a's `VE.Time.parseDecimal` into `VE.Time.Dec` (one decimal grammar). Its exact value:

```lean
namespace VE.Numbers

/-- The exact value of a written decimal. -/
def decValue (d : VE.Time.Dec) : Rat := (d.significand : Rat) / ((10 : Rat) ^ d.places)

/-- One meaning for decimals: where W6 lowers a literal onto the grid of scale `10^k`, the coordinate over `10^k`
is the literal's exact value. -/
theorem decValue_lower (d : VE.Time.Dec) (k : Nat) (q : Int) (h : VE.Time.lower d k = some q) :
    decValue d = (q : Rat) / ((10 : Rat) ^ k)

/-- Ten to an integer power, exactly. -/
def tenPow : Int → Rat
  | .ofNat n => (10 : Rat) ^ n
  | .negSucc n => 1 / (10 : Rat) ^ (n + 1)

theorem tenPow_pos (k : Int) : 0 < tenPow k
theorem tenPow_add (a b : Int) : tenPow (a + b) = tenPow a * tenPow b
```

### 1.2 Printed numbers

A printed number keeps its written places (plan D5): "0.30" is (30, 2), "0.3" is (3, 1), "2 times ten to the power 7"
is (2, −7), "1.5 times ten to the power 7" is (15, −6).

```lean
structure Printed where
  digits : Int
  places : Int
  deriving Repr, DecidableEq

def Printed.value (p : Printed) : Rat := (p.digits : Rat) / tenPow p.places
def Printed.ofDec (d : VE.Time.Dec) : Printed := ⟨d.significand, (d.places : Int)⟩
/-- "D times ten to the power e": the places of D's last written digit, minus e. -/
def Printed.sci (d : VE.Time.Dec) (e : Int) : Printed := ⟨d.significand, (d.places : Int) - e⟩

theorem Printed.value_ofDec (d : VE.Time.Dec) : (Printed.ofDec d).value = decValue d
theorem Printed.value_sci (d : VE.Time.Dec) (e : Int) : (Printed.sci d e).value = decValue d * tenPow e
```

### 1.3 Rounding (`lean/VE/Numbers/Round.lean`)

One definition with four rules (plan D6). Writing y = x · 10^k and D the printed digits:

| Rule | Wire | English (named in every sentence) | `x` rounds to `(D, k)` exactly when |
|---|---|---|---|
| `tiesUp` (default) | `ties-up` | "…, with exact ties going up" | 2D − 1 ≤ 2y < 2D + 1 |
| `halfEven` | `half-even` | "…, with exact ties going to the even digit" (half to even on the exact value) | 2D − 1 < 2y < 2D + 1, or 2y = 2D ± 1 and D is even |
| `down` | `rounds-down` | "… when rounded down to …" | D ≤ y < D + 1 |
| `up` | `rounds-up` | "… when rounded up to …" | D − 1 < y ≤ D |

"Going up" means toward the larger number, also for negative values. Half to even is decided on the exact rational
value, never on a binary double: `round(2.675, 2)` in Python gives 2.67 because the double nearest 2.675 is below it,
while the exact value 107/40 is a tie that both rules round to 2.68 (fixture V-9).

```lean
inductive Rounding where
  | tiesUp | halfEven | down | up
  deriving Repr, DecidableEq

def RoundsTo (r : Rounding) (p : Printed) (x : Rat) : Prop :=
  match r with
  | .tiesUp => 2 * (p.digits : Rat) - 1 ≤ 2 * (x * tenPow p.places) ∧
      2 * (x * tenPow p.places) < 2 * (p.digits : Rat) + 1
  | .halfEven =>
      (2 * (p.digits : Rat) - 1 < 2 * (x * tenPow p.places) ∧
        2 * (x * tenPow p.places) < 2 * (p.digits : Rat) + 1) ∨
      ((2 * (x * tenPow p.places) = 2 * (p.digits : Rat) - 1 ∨
        2 * (x * tenPow p.places) = 2 * (p.digits : Rat) + 1) ∧ p.digits % 2 = 0)
  | .down => (p.digits : Rat) ≤ x * tenPow p.places ∧ x * tenPow p.places < (p.digits : Rat) + 1
  | .up => (p.digits : Rat) - 1 < x * tenPow p.places ∧ x * tenPow p.places ≤ (p.digits : Rat)

instance (r : Rounding) (p : Printed) (x : Rat) : Decidable (RoundsTo r p x)

/-- The digits that `x` rounds to at `k` places under rule `r` (used for findings and display). -/
def Rounding.round (r : Rounding) (k : Int) (x : Rat) : Int :=
  match r with
  | .tiesUp => Rat.floor (x * tenPow k + 1 / 2)
  | .halfEven =>
      let f := Rat.floor (x * tenPow k + 1 / 2)
      if (f : Rat) = x * tenPow k + 1 / 2 ∧ f % 2 ≠ 0 then f - 1 else f
  | .down => Rat.floor (x * tenPow k)
  | .up => Rat.ceil (x * tenPow k)

theorem roundsTo_iff_round (r : Rounding) (p : Printed) (x : Rat) :
    RoundsTo r p x ↔ r.round p.places x = p.digits
theorem roundsTo_round (r : Rounding) (k : Int) (x : Rat) : RoundsTo r ⟨r.round k x, k⟩ x
/-- One printed number per value, rule and number of places, for all four rules. -/
theorem roundsTo_unique (r : Rounding) (x : Rat) (p q : Printed) (hk : p.places = q.places)
    (hp : RoundsTo r p x) (hq : RoundsTo r q x) : p = q
theorem roundsTo_close (p : Printed) (x : Rat) (h : RoundsTo .tiesUp p x) :
    -(1 / 2) ≤ x * tenPow p.places - p.digits ∧ x * tenPow p.places - p.digits < 1 / 2

/-- `x` is an exact tie at `k` places: `x · 10^k` is an odd number of halves. -/
def tieAt (k : Int) (x : Rat) : Bool :=
  let z := 2 * (x * tenPow k)
  z.den == 1 && z.num % 2 != 0

/-- The two declarable rules agree away from exact ties … -/
theorem rules_agree_off_tie (p : Printed) (x : Rat) (h : tieAt p.places x = false) :
    RoundsTo .tiesUp p x ↔ RoundsTo .halfEven p x
/-- … and differ exactly at a tie whose upper neighbour is odd. -/
theorem rules_differ_iff (k : Int) (x : Rat) :
    Rounding.round .tiesUp k x ≠ Rounding.round .halfEven k x ↔
      tieAt k x = true ∧ Rounding.round .tiesUp k x % 2 ≠ 0
```

`roundsTo_unique` is stated for every rule; draft 1 stated it for ties upward only (section 16, C1). A closed interval
that accepts both neighbours at a tie is not a meaning of "rounded" (plan D6).

### 1.4 Comparison phrases: one Lean owner (debate F3)

W6's four order phrases live today in `ve/english.py:51` (`_COMPARISONS`). ME-1 moves them, rows and order unchanged,
into `lean/VE/Numbers/Phrases.lean`, and Python reads them from the generated `ve/numbers_phrases.json` (a new entry
in `tools/regen_generated.py`). If quantities' QT-E has moved them first, ME-1 reads QT-E's table instead and adds only
`equalsPhrase` and `withinPhrase`. ME-11's English engine replaces `Render.lean`'s phrase table rather than sitting
beside it.

```lean
inductive Rel where
  | eq | lt | le
  deriving Repr, DecidableEq

def Rel.Holds : Rel → Rat → Rat → Prop
  | .eq, x, y => x = y
  | .lt, x, y => x < y
  | .le, x, y => x ≤ y

/-- A relation and whether its operands are swapped ("A is more than B" is `B < A`). -/
structure Comparison where
  rel : Rel
  swap : Bool
  deriving Repr, DecidableEq

def Comparison.Holds (c : Comparison) (x y : Rat) : Prop :=
  if c.swap then c.rel.Holds y x else c.rel.Holds x y

/-- W6's order phrases, moved from `ve/english.py` `_COMPARISONS` (same rows, same order). -/
def orderPhrases : List (String × Comparison) :=
  [("{0} is less than {1}", ⟨.lt, false⟩), ("{0} is at most {1}", ⟨.le, false⟩),
   ("{0} is more than {1}", ⟨.lt, true⟩), ("{0} is at least {1}", ⟨.le, true⟩)]

def equalsPhrase : String × Comparison := ("{0} equals {1}", ⟨.eq, false⟩)

def withinPhrase : String := "{0} is from {1} through {2}"
```

### 1.5 Verdicts and outcomes (debate A1)

The mathematical verdict has three values. The operational outcome is a verdict or **unknown** with a named reason.
Both profiles share these types.

```lean
inductive Verdict where
  | holds | fails | undefined
  deriving Repr, DecidableEq

inductive Limit where
  | digits | evaluations | derivationSteps | witnessPoints | polyTerms
  deriving Repr, DecidableEq

inductive UnknownReason where
  | limit (l : Limit)
  | floatingPointNotModelled
  | derivationInconclusive
  | consistencyInconclusive
  | identityNotShown
  | unboundedStatement
  deriving Repr, DecidableEq

inductive Outcome where
  | decided (v : Verdict)
  | unknown (r : UnknownReason)
  deriving Repr, DecidableEq

end VE.Numbers
```

| Reason | Rendered text |
|---|---|
| `limit .digits` | "unknown: an exact value would have more than 4,096 digits" |
| `limit .evaluations` | "unknown: the budget of N evaluation steps ran out" (N is the case's budget) |
| `limit .derivationSteps` | "unknown: the derivation search ran out of its 10,000 combination steps" |
| `limit .witnessPoints` | "unknown: the consistency search tried its 4,096 candidate points" |
| `limit .polyTerms` | "unknown: a normal form would have more than 10,000 terms" |
| `floatingPointNotModelled` | "unknown: floating-point computation not modelled" |
| `derivationInconclusive` | "unknown: no certificate and no counterexample was found" |
| `consistencyInconclusive` | "unknown: neither a witness nor an enclosure decides it" |
| `identityNotShown` | "unknown: the normal forms differ and no point where the sides differ was found" |
| `unboundedStatement` | "stated, not decided: a quantifier has no bound" |

## 2. The `calc@0` core (ME-1)

### 2.1 Expressions and their meaning

```lean
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

/-- The independent meaning: the value an expression denotes, when every name has a value and no divisor is 0. -/
inductive Denotes (σ : Values) : Expr → Rat → Prop
  | lit {q} : Denotes σ (.lit q) q
  | val {n q} : σ n = some q → Denotes σ (.val n) q
  | add {a b x y} : Denotes σ a x → Denotes σ b y → Denotes σ (.add a b) (x + y)
  | sub {a b x y} : Denotes σ a x → Denotes σ b y → Denotes σ (.sub a b) (x - y)
  | mul {a b x y} : Denotes σ a x → Denotes σ b y → Denotes σ (.mul a b) (x * y)
  | div {a b x y} : Denotes σ a x → Denotes σ b y → y ≠ 0 → Denotes σ (.div a b) (x / y)
  | pow {a x k} : Denotes σ a x → Denotes σ (.pow a k) (x ^ k)

def Expr.eval (σ : Values) : Expr → Option Rat
  | .lit q => some q
  | .val n => σ n
  | .add a b => do let x ← a.eval σ; let y ← b.eval σ; pure (x + y)
  | .sub a b => do let x ← a.eval σ; let y ← b.eval σ; pure (x - y)
  | .mul a b => do let x ← a.eval σ; let y ← b.eval σ; pure (x * y)
  | .div a b => do
      let x ← a.eval σ
      let y ← b.eval σ
      if y = 0 then none else pure (x / y)
  | .pow a k => (a.eval σ).map (· ^ k)

theorem Expr.eval_iff (σ : Values) (e : Expr) (q : Rat) : e.eval σ = some q ↔ Denotes σ e q
theorem Denotes.unique {σ : Values} {e : Expr} {x y : Rat} (hx : Denotes σ e x) (hy : Denotes σ e y) : x = y

/-- The names an expression reads, left to right, with repetition. -/
def Expr.names : Expr → List String
  | .lit _ => []
  | .val n => [n]
  | .add a b | .sub a b | .mul a b | .div a b => a.names ++ b.names
  | .pow a _ => a.names

/-- Every subexpression, the expression itself first. -/
def Expr.subexprs : Expr → List Expr
  | .lit q => [.lit q]
  | .val n => [.val n]
  | .add a b => .add a b :: (a.subexprs ++ b.subexprs)
  | .sub a b => .sub a b :: (a.subexprs ++ b.subexprs)
  | .mul a b => .mul a b :: (a.subexprs ++ b.subexprs)
  | .div a b => .div a b :: (a.subexprs ++ b.subexprs)
  | .pow a k => .pow a k :: a.subexprs
```

### 2.2 Claims and verdicts

```lean
inductive Claim where
  | compare (c : Comparison) (a b : Expr)
  | within (e lo hi : Expr)
  | rounds (r : Rounding) (e : Expr) (p : Printed)
  deriving Repr, DecidableEq

def Claim.exprs : Claim → List Expr
  | .compare _ a b => [a, b]
  | .within e lo hi => [e, lo, hi]
  | .rounds _ e _ => [e]

def Claim.Holds (σ : Values) : Claim → Prop
  | .compare c a b => ∃ x y, Denotes σ a x ∧ Denotes σ b y ∧ c.Holds x y
  | .within e lo hi => ∃ x l h, Denotes σ e x ∧ Denotes σ lo l ∧ Denotes σ hi h ∧ l ≤ x ∧ x ≤ h
  | .rounds r e p => ∃ x, Denotes σ e x ∧ RoundsTo r p x

def Claim.Defined (σ : Values) (c : Claim) : Prop := ∀ e ∈ c.exprs, ∃ q, Denotes σ e q

def Claim.decide (σ : Values) : Claim → Verdict
  | .compare c a b => match a.eval σ, b.eval σ with
    | some x, some y => if c.Holds x y then .holds else .fails
    | _, _ => .undefined
  | .within e lo hi => match e.eval σ, lo.eval σ, hi.eval σ with
    | some x, some l, some h => if l ≤ x ∧ x ≤ h then .holds else .fails
    | _, _, _ => .undefined
  | .rounds r e p => match e.eval σ with
    | some x => if RoundsTo r p x then .holds else .fails
    | none => .undefined

theorem Claim.decide_holds (σ : Values) (c : Claim) : c.decide σ = .holds ↔ c.Holds σ
theorem Claim.decide_fails (σ : Values) (c : Claim) : c.decide σ = .fails ↔ c.Defined σ ∧ ¬ c.Holds σ
theorem Claim.decide_undefined (σ : Values) (c : Claim) : c.decide σ = .undefined ↔ ¬ c.Defined σ

/-- The two declarable tie rules disagree on this rounding claim only when its value is an exact tie. -/
def Claim.tieSensitive (σ : Values) : Claim → Bool
  | .rounds .tiesUp e p | .rounds .halfEven e p => match e.eval σ with
    | some x => tieAt p.places x
    | none => false
  | _ => false
```

The report flags every `rounds` claim whose value is an exact tie (`"tie": true`). In translation, a source that
declares no tie rule and prints a tie-sensitive number gives a reading set with two readings, one per rule, whose
distinguishing value is that claim (plan D6, fixture V-8).

### 2.3 Declarations and their values

A named value has one source (plan D4). ME-1 decodes `stated`, `defined` and `free`; ME-4 fills `counted` with the
aggregate Lean computed from the pinned bytes (section 4).

```lean
inductive Source where
  | stated (q : Rat)
  | defined (e : Expr)
  | free
  | counted (q : Option Rat)

structure Decl where
  name : String
  source : Source

def Decl.valueUnder (d : Decl) (σ : Values) : Option Rat :=
  match d.source with
  | .stated q => some q
  | .defined e => e.eval σ
  | .free => none
  | .counted q => q

/-- The values the declarations give, in order. -/
def values (ds : List Decl) : Values :=
  ds.foldl (fun σ d n => if n = d.name then d.valueUnder σ else σ n) (fun _ => none)

/-- Unique names; each defined value reads only earlier names. -/
def WellFormed (ds : List Decl) : Prop :=
  (ds.map Decl.name).Nodup ∧
    ∀ (i : Nat) (hi : i < ds.length) (e : Expr), (ds[i]'hi).source = .defined e →
      ∀ n ∈ e.names, n ∈ (ds.take i).map Decl.name

theorem values_stated (ds : List Decl) (h : WellFormed ds) (d : Decl) (hd : d ∈ ds) (q : Rat)
    (hs : d.source = .stated q) : values ds d.name = some q
theorem values_defined (ds : List Decl) (h : WellFormed ds) (d : Decl) (hd : d ∈ ds) (e : Expr)
    (hs : d.source = .defined e) (q : Rat) : values ds d.name = some q ↔ Denotes (values ds) e q
theorem values_free (ds : List Decl) (h : WellFormed ds) (d : Decl) (hd : d ∈ ds)
    (hs : d.source = .free) : values ds d.name = none
theorem values_counted (ds : List Decl) (h : WellFormed ds) (d : Decl) (hd : d ∈ ds) (q : Option Rat)
    (hs : d.source = .counted q) : values ds d.name = q
theorem values_missing (ds : List Decl) (n : String) (h : n ∉ ds.map Decl.name) : values ds n = none
```

### 2.4 The digit limit and the operational outcome (debate A1)

An exact value whose numerator or denominator would have more than 4,096 decimal digits is not computed. The
operational evaluator returns `ok`, `undefined` or `tooLarge`; evaluation is left to right, and the first fault met
decides.

```lean
def maxDigits : Nat := 4096
def digitCount (n : Nat) : Nat := (Nat.toDigits 10 n).length

def Small (q : Rat) : Prop := digitCount q.num.natAbs ≤ maxDigits ∧ digitCount q.den ≤ maxDigits

inductive Val where
  | ok (q : Rat) | undefined | tooLarge
  deriving Repr, DecidableEq

def Val.guard (q : Rat) : Val := if Small q then .ok q else .tooLarge

def Val.bin (f : Rat → Rat → Val) : Val → Val → Val
  | .ok x, .ok y => f x y
  | .ok _, v => v
  | v, _ => v

def Expr.evalL (τ : String → Val) : Expr → Val
  | .lit q => Val.guard q
  | .val n => τ n
  | .add a b => Val.bin (fun x y => Val.guard (x + y)) (a.evalL τ) (b.evalL τ)
  | .sub a b => Val.bin (fun x y => Val.guard (x - y)) (a.evalL τ) (b.evalL τ)
  | .mul a b => Val.bin (fun x y => Val.guard (x * y)) (a.evalL τ) (b.evalL τ)
  | .div a b => Val.bin (fun x y => if y = 0 then .undefined else Val.guard (x / y)) (a.evalL τ) (b.evalL τ)
  | .pow a k => match a.evalL τ with
    | .ok x => Val.guard (x ^ k)
    | v => v

def Decl.valL (d : Decl) (τ : String → Val) : Val :=
  match d.source with
  | .stated q => Val.guard q
  | .defined e => e.evalL τ
  | .free => .undefined
  | .counted (some q) => Val.guard q
  | .counted none => .undefined

def valuesL (ds : List Decl) : String → Val :=
  ds.foldl (fun τ d n => if n = d.name then d.valL τ else τ n) (fun _ => .undefined)

def firstFault : List Val → Option Val
  | [] => none
  | .ok _ :: vs => firstFault vs
  | v :: _ => some v

def Claim.run (ds : List Decl) (c : Claim) : Outcome :=
  match firstFault (c.exprs.map (Expr.evalL (valuesL ds))) with
  | some .tooLarge => .unknown (.limit .digits)
  | some _ => .decided .undefined
  | none => .decided (c.decide (values ds))

/-- A defined name whose computation, or a computation it reads, reaches a value beyond the digit limit. -/
inductive NameOverflows (ds : List Decl) : String → Prop
  | here {n : String} {e : Expr} :
      (∃ d ∈ ds, d.name = n ∧ d.source = .defined e) →
      (∃ e' ∈ e.subexprs, ∃ q, Denotes (values ds) e' q ∧ ¬ Small q) → NameOverflows ds n
  | dep {n m : String} {e : Expr} :
      (∃ d ∈ ds, d.name = n ∧ d.source = .defined e) → m ∈ e.names → NameOverflows ds m →
      NameOverflows ds n

def Expr.Overflows (ds : List Decl) (e : Expr) : Prop :=
  (∃ e' ∈ e.subexprs, ∃ q, Denotes (values ds) e' q ∧ ¬ Small q) ∨ ∃ m ∈ e.names, NameOverflows ds m

def Claim.Overflows (ds : List Decl) (c : Claim) : Prop := ∃ e ∈ c.exprs, e.Overflows ds

/-- A decided outcome is the mathematical verdict. -/
theorem Claim.run_decided (ds : List Decl) (h : WellFormed ds) (c : Claim) (v : Verdict)
    (hr : c.run ds = .decided v) : v = c.decide (values ds)
/-- Unknown arises only from the named limit, and only when a value on the way really exceeds it. -/
theorem Claim.run_unknown (ds : List Decl) (h : WellFormed ds) (c : Claim) (u : UnknownReason)
    (hr : c.run ds = .unknown u) : u = .limit .digits ∧ c.Overflows ds
theorem Claim.run_complete (ds : List Decl) (h : WellFormed ds) (c : Claim) (hc : ¬ c.Overflows ds) :
    c.run ds = .decided (c.decide (values ds))
```

`Overflows` is stated over `Denotes`, so it is independent of the evaluator. A claim may be unknown although its
meaning is undefined (a value on the way is too large before a later zero divisor is reached); it is never decided
wrongly. Fixture V-11 shows a limit hit and a zero divisor side by side.

### 2.5 Findings (debates F1 and F2)

In a translated document a claim that fails is a **finding**; nothing is repaired. Its kind:

```lean
inductive FindingKind where
  | source | transcriptionUnchecked | softwareUnreproduced
  deriving Repr, DecidableEq

def findingKind (software : Option String) (checks : List Bool) : FindingKind :=
  if software.isSome then .softwareUnreproduced
  else if checks ≠ [] ∧ checks.all id then .source
  else .transcriptionUnchecked

theorem findingKind_source_iff (software : Option String) (checks : List Bool) :
    findingKind software checks = .source ↔ software = none ∧ checks ≠ [] ∧ ∀ b ∈ checks, b = true
```

`checks` has one flag, in order of first occurrence, for each of: every stated value the claim reads, directly or
through defined values; every literal in the claim's expressions or in the definitions it reads; and the claim's
printed number, for a rounding claim. A stated value's or printed number's flag is true when ME-4 matched its `span`
against the pinned source bytes (section 4.4). A literal's flag is always false: the source does not print the case's
constants, so a claim that reads a literal is never a source finding (section 16, C4). Before ME-4 every flag is
false.

| Kind | Rendered text (fixture V-2 with 0.213 printed) |
|---|---|
| `source` | "The source's numbers disagree: 52 divided by 243 is 0.21399…, which rounds to 0.214, not 0.213, with exact ties going up." |
| `transcriptionUnchecked` | "The case's numbers disagree; transcription unchecked: 52 divided by 243 is 0.21399…, which rounds to 0.214, not 0.213, with exact ties going up." |
| `softwareUnreproduced` | "The exact value disagrees with the printed number: 2.675 rounded to two decimal places, with exact ties going up, is 2.68, not 2.67. Whether Python 3.12 prints 2.67 is unknown: floating-point computation not modelled." (V-9) |

The display "0.21399…" is the exact value truncated toward zero at two places beyond the printed ones, followed by
"…" when the truncation dropped a nonzero remainder.

In authoring, a claim that fails is the error `CalcClaimFails` (section 13.1), with the same text as a
transcription-unchecked finding.

### 2.6 Software conventions (debate F2, merged in round 3)

A case may declare `"software": "<name>"` (at most 64 bytes, for example "Python 3.12 float formatting"). The
declaration picks no rounding rule. Each claim is then reported twice: the **exact claim** with its outcome from
`Claim.run`, and **software reproduction**, always `unknown floatingPointNotModelled`. VE has no floating-point
semantics, and this specification names no way to establish that a program's computation equals the exact one. A
failed exact claim under a software convention is a `softwareUnreproduced` finding, never a source finding (V-9,
V-10). V-7 and V-8 declare no software convention; their exact claims hold.

## 3. The wire, identity and runner (ME-2)

### 3.1 The case `ve-calc@0`

| Field | Mandatory | Content |
|---|---|---|
| `format` | yes | `"ve-calc@0"` |
| `values` | yes | a list of value records (below), in order |
| `claims` | yes | a nonempty list of `{"id": <claim id>, "claim": <claim>, "span": [start, stop]?}` |
| `rounding` | no | `"ties-up"` (default) or `"half-even"`: the rule of every `rounds` claim without its own |
| `software` | no | a software convention (2.6) |
| `source` | no (ME-4) | the SHA-256 handle of the pinned source bytes against which spans are checked |
| `data` | no (ME-4) | data declarations (4.1) |
| `environment` | no (ME-6) | a `ve-units@2` (or `ve-units@1`) environment (6.2) |
| `budget` | no (ME-4) | a positive integer at most 1,000,000: the table evaluation budget |

A value record is `{"name": n, "words": w, <source>, "support"?: s, "span"?: [start, stop], "unit"?: u}` with exactly
one source: `"stated": <literal>`, `"defined": <expression>`, `"free": true` or `"counted": <counted>` (ME-4). Names
match `[a-z][a-z0-9_]*`, at most 64 bytes, unique. `words` follow W6's verbalisation rules, checked by the check W6a
already runs (`VerbalisationCollision`), plus the calc rules of 11.2 (`ValueWordsForm`, `ReservedWord`). `support` is
`observation`, `testimony` or `assumption` (W2's `support` provenance field). Claim ids match `[a-z0-9_-]{1,64}` and
are unique.

Literals: `"<decimal>"` (W6's `parseDecimal` grammar) or `["sci", "<decimal>", e]` with an integer `|e| ≤ 64`
("D times ten to the power e"). Expressions: `["lit", literal]`, `["val", name]`, `["add", a, b]`, `["sub", a, b]`,
`["mul", a, b]`, `["div", a, b]`, `["pow", a, k]` with a natural `k ≤ 64`. Claims:
`["eq" | "lt" | "le" | "gt" | "ge", a, b]` (`gt` and `ge` are `lt` and `le` with operands swapped, the phrases
"is more than" and "is at least"), `["within", e, lo, hi]`, `["rounds", e, printed]` or
`["rounds", e, printed, "ties-up" | "half-even"]`, `["rounds-down", e, printed]`, `["rounds-up", e, printed]`, where
`printed` is a literal read with its written places (`Printed.ofDec` or `Printed.sci`).

### 3.2 Limits, checked first and in this order

1. 10,000 JSON nodes; 2. JSON depth 64; 3. 512 values; 4. 512 claims; 5. `pow` exponents and `sci` exponents at most
64 in absolute value; 6. literals at most 40 digits (W6's `maxNumeralChars`); 7. names and claim ids at most 64 bytes.
The first exceeded limit refuses the case with `ResourceLimit: <limit> exceeds <n>` (an UNKNOWN to the relay). A
computed value beyond 4,096 digits is not a refusal: the claims that need it are `unknown` (2.4).

### 3.3 Identity

The case's `meaning_id` is `VE.Route.Wire.meaningId ["calc@0"] envId canonical`, where `envId` is
`VE.Route.Wire.environmentId ["calc@0"] environment` (the case's `environment`, or `{}`), and `canonical` is the case
with `words` removed, every value literal written as its shortest plain decimal ("0.30" and "0.3" as values are one
value; `["sci", "2", 7]` is `"20000000"`), every printed number written as `[digits, places]` with digits as a decimal
string ("0.30" is `["30", 2]`, "0.3" is `["3", 1]`), every `rounds` claim carrying its rule, `gt`/`ge` kept as written,
and object keys in the order of 3.1. `support`, `span`, `software`, `source` and `data` are part of the identity. A
claim's id is `VE.CertificateWire.digest "ve-calc-claim-v0.2:calc@0\n" {"meaning_id": id, "claim": canonicalClaim}`.
A renamed verbalisation keeps the identity; changing a value, a source, a support, a span, a tie rule or a printed
spelling changes it and voids every approval or citation of it.

### 3.4 The runner and its rows

```lean
structure Case where
  decls : List Decl
  claims : List (String × Claim)
  software : Option String

structure Row where
  id : String
  outcome : Outcome
  reproduction : Option Outcome
  deriving Repr

def Run.row (c : Case) (cl : String × Claim) : Row :=
  { id := cl.1, outcome := cl.2.run c.decls,
    reproduction := c.software.map fun _ => .unknown .floatingPointNotModelled }

def Run.rows (c : Case) : List Row := c.claims.map (Run.row c)

theorem Run.rows_outcome (c : Case) (i : Nat) (hi : i < c.claims.length) :
    ((Run.rows c)[i]'(by simpa [Run.rows] using hi)).outcome = (c.claims[i]'hi).2.run c.decls

/-- *Opaque*: decodes `ve-calc@0` (limits of 3.2 first, then fields, names, definition order, literals). -/
def Wire.decodeCase : Lean.Json → Except String Case
theorem Wire.decodeCase_wellFormed (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) :
    WellFormed c.decls

/-- *Opaque*: the service answer, and the reader of row `i`'s outcome in it. -/
def Run.runCaseReported : Lean.Json → Lean.Json
def Run.outcomeAt : Lean.Json → Nat → Option Outcome

theorem Run.outcome_sound (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) (i : Nat)
    (hi : i < c.claims.length) :
    Run.outcomeAt (Run.runCaseReported j) i = some ((c.claims[i]'hi).2.run c.decls)
/-- Debate A1: agreement with the total decision is conditional on completion. -/
theorem Run.verdict_sound (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) (i : Nat)
    (hi : i < c.claims.length) (v : Verdict)
    (hv : Run.outcomeAt (Run.runCaseReported j) i = some (.decided v)) :
    v = (c.claims[i]'hi).2.decide (values c.decls)
theorem Run.unknown_named (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) (i : Nat)
    (hi : i < c.claims.length) (u : UnknownReason)
    (hu : Run.outcomeAt (Run.runCaseReported j) i = some (.unknown u)) :
    u = .limit .digits ∧ (c.claims[i]'hi).2.Overflows c.decls

end VE.Calc

namespace VE.Service
theorem runMode_calc (j : Lean.Json) : runMode .calc j = VE.Calc.Run.runCaseReported j := rfl
end VE.Service

namespace ResponseShape.Encoders.Calc
theorem runCaseReported_fits (j : Lean.Json) :
    ResponseShape.Fits j ResponseShape.Skeletons.calc (VE.Calc.Run.runCaseReported j)
end ResponseShape.Encoders.Calc
```

`ResponseShape.Fits (c : Json) : Skel → Json → Prop` is the predicate the existing encoder theorems use
(`lean/ResponseShape/Skeleton.lean:288`); `ResponseShape.Skeletons.calc` is ME-2's new skeleton. `runMode_calc` was
checked against a stand-in `runMode`, since the `calc` constructor is ME-2's; the mode registers through AR-10's mode
registry and the equation is listed in `lean/VE/Audit.lean`.

Each response row carries: `claim` (the request's claim id), `claim_id` (3.3), `outcome` (`holds`, `fails`,
`undefined`, `unknown`), `reason` (the text of 1.5, for unknown), `sides` (each expression's exact value as a reduced
fraction `"n/d"`, or `null`), `display` (2.5's truncated decimal at the printed places), `line` (Lean's English line,
11.1), `tie` (2.2), `finding` (`{"kind", "text"}` for a failed claim in translation, else `null`), `reproduction`
(`"unknown"` under a software convention, else `null`) and `rests_on` (each stated, counted or free value read, with
its source kind, support and whether its span was checked). The relay (ME-3) binds rows to the request: exactly one
row per request claim, in order, every name in `rests_on` declared in the request; anything else is
`CheckerUnavailable`.

## 4. Tables, data handles and source spans (ME-4)

### 4.1 Tables and their meaning

A case may declare `"data": [{"handle": <sha256>, "format": "csv" | "jsonl", "columns": {name: "text" | "number" |
"bool"}}]`. The request registers the bytes under their SHA-256 in the existing `VE.Service.Handles` table, as a data
kind beside environments (no second table, no shared record-shape project); Lean recomputes the digest
(`VE.CertificateWire.sha256`) and refuses a mismatch. The relay reads the file and sends its bytes; it never parses
them. CSV subset: comma separator, double-quote quoting, a header row, LF or CRLF line ends. JSON lines: one object per
line, columns read by top-level key. A number cell is read by its written digits as an exact decimal (plan D10); a
`bool` cell is `true` or `false`; an empty field or missing key is `absent`; any other text in a `number` or `bool`
column is kept as `text`.

```lean
inductive Cell where
  | num (q : Rat) | text (s : String) | bool (b : Bool) | absent
  deriving Repr, DecidableEq

structure Table where
  columns : List String
  rows : List (List Cell)

def Table.cell (T : Table) (row : List Cell) (col : String) : Cell :=
  match T.columns.idxOf? col with
  | some i => row.getD i .absent
  | none => .absent

inductive Filter where
  | all
  | isText (col v : String)
  | equals (col : String) (q : Rat)
  | isTrue (col : String)
  | not (f : Filter)
  | and (f g : Filter)
  | or (f g : Filter)

/-- The meaning of a filter. -/
def Filter.Selects (T : Table) : Filter → List Cell → Prop
  | .all, _ => True
  | .isText c v, r => T.cell r c = .text v
  | .equals c q, r => T.cell r c = .num q
  | .isTrue c, r => T.cell r c = .bool true
  | .not f, r => ¬ f.Selects T r
  | .and f g, r => f.Selects T r ∧ g.Selects T r
  | .or f g, r => f.Selects T r ∨ g.Selects T r

/-- The executable filter. -/
def Filter.sel (T : Table) : Filter → List Cell → Bool
  | .all, _ => true
  | .isText c v, r => T.cell r c == .text v
  | .equals c q, r => T.cell r c == .num q
  | .isTrue c, r => T.cell r c == .bool true
  | .not f, r => !f.sel T r
  | .and f g, r => f.sel T r && g.sel T r
  | .or f g, r => f.sel T r || g.sel T r

def Table.select (T : Table) (f : Filter) : List (List Cell) := T.rows.filter (f.sel T)

theorem Table.select_iff (T : Table) (f : Filter) (row : List Cell) :
    row ∈ T.select f ↔ row ∈ T.rows ∧ f.Selects T row
theorem Table.select_sublist (T : Table) (f : Filter) : (T.select f).Sublist T.rows
```

### 4.2 Aggregates (debate A4)

```lean
/-- The numbers of a column over the selected rows, in table order; none if a selected cell there is not a number. -/
def Table.numbers (T : Table) (f : Filter) (col : String) : Option (List Rat) :=
  (T.select f).mapM fun r => match T.cell r col with
    | .num q => some q
    | _ => none

def mean? (xs : List Rat) : Option Rat := if xs = [] then none else some (xs.sum / xs.length)

inductive Agg where
  | count | sum (col : String) | mean (col : String) | min (col : String) | max (col : String)

def Agg.run (T : Table) (f : Filter) : Agg → Option Rat
  | .count => some ((T.select f).length : Rat)
  | .sum c => (T.numbers f c).map List.sum
  | .mean c => (T.numbers f c).bind mean?
  | .min c => (T.numbers f c).bind List.min?
  | .max c => (T.numbers f c).bind List.max?

theorem Agg.run_count (T : Table) (f : Filter) : Agg.run T f .count = some ((T.select f).length : Rat)
theorem Agg.run_sum (T : Table) (f : Filter) (col : String) :
    Agg.run T f (.sum col) = (T.numbers f col).map List.sum
theorem Agg.run_mean (T : Table) (f : Filter) (col : String) (q : Rat) :
    Agg.run T f (.mean col) = some q ↔ ∃ xs, T.numbers f col = some xs ∧ xs ≠ [] ∧ q = xs.sum / xs.length
/-- Over an empty selection, count and sum are 0; mean, minimum and maximum are undefined. -/
theorem Agg.run_empty (T : Table) (f : Filter) (h : T.select f = []) (col : String) :
    Agg.run T f .count = some 0 ∧ Agg.run T f (.sum col) = some 0 ∧ Agg.run T f (.mean col) = none ∧
      Agg.run T f (.min col) = none ∧ Agg.run T f (.max col) = none
/-- A selected cell that is not a number makes sum, mean, minimum and maximum undefined. -/
theorem Agg.run_nonnumber (T : Table) (f : Filter) (col : String) (row : List Cell) (hr : row ∈ T.select f)
    (hc : ∀ q, T.cell row col ≠ .num q) :
    Agg.run T f (.sum col) = none ∧ Agg.run T f (.mean col) = none ∧ Agg.run T f (.min col) = none ∧
      Agg.run T f (.max col) = none

/-- *Opaque*: aggregation under a budget of one unit per (row, filter node) visit; `none` is UNKNOWN. -/
def Agg.runB (limit : Nat) (T : Table) (f : Filter) (a : Agg) : Option (Option Rat)
theorem Agg.runB_sound (limit : Nat) (T : Table) (f : Filter) (a : Agg) (v : Option Rat)
    (h : Agg.runB limit T f a = some v) : v = Agg.run T f a
```

A `counted` value is `{"data": <handle>, "filter": F, "aggregate": A}` with filters `["is", column, text]`,
`["equals", column, number]`, `["true", column]`, `["not", F]`, `["and", F, F]`, `["or", F, F]`, `["all"]` and
aggregates `"count"`, `["sum", column]`, `["mean", column]`, `["min", column]`, `["max", column]`. Its `Decl` source is
`counted (Agg.run T f a)`; a budget exhaustion makes every claim reading it `unknown (limit .evaluations)`.

### 4.3 Binding to bytes

```lean
inductive Format where
  | csv | jsonl
  deriving Repr, DecidableEq

inductive ColType where
  | text | number | bool
  deriving Repr, DecidableEq

/-- *Opaque*: the CSV and JSON-lines subsets of 4.1. -/
def decodeTable (format : Format) (columns : List (String × ColType)) (bytes : ByteArray) : Except String Table

structure DataDecl where
  handle : String
  format : Format
  columns : List (String × ColType)

/-- *Opaque*: the counted value of a declaration over the registered handles. -/
def runCounted (handles : List (String × ByteArray)) (dd : DataDecl) (f : Filter) (a : Agg) : Option Rat

/-- A counted value is computed only from bytes whose SHA-256 is the declared handle. -/
theorem counted_bound (handles : List (String × ByteArray)) (dd : DataDecl) (f : Filter) (a : Agg) (q : Rat)
    (h : runCounted handles dd f a = some q) :
    ∃ bytes T, handles.lookup dd.handle = some bytes ∧ VE.CertificateWire.sha256 bytes = dd.handle ∧
      decodeTable dd.format dd.columns bytes = .ok T ∧ Agg.run T f a = some q
```

SHA-256 is trusted code without a refinement theorem, as for the risk log (plan 3.3).

### 4.4 Source spans (debate F1)

The pinned source of a translated document is registered as a data handle (`"source"`). A `span` is a half-open byte
range `[start, stop)` of those bytes. Lean reads the bytes as UTF-8 and reads the text as a number the way a source
prints numbers: an optional minus, a whole part (digits without a leading zero, or comma groups of three after a first
group of one to three digits not starting with 0), an optional point followed by digits; the whole part may be empty
before a point (".296"); at least one digit. The written places are kept. A span whose text reads as the stated
literal's or printed number's `Printed` is checked; any other span is refused with `SpanMismatch`, and so is a span
outside the bytes. A value or printed number without a span is unchecked.

```lean
structure Span where
  start : Nat
  stop : Nat
  deriving Repr, DecidableEq

def spanText (src : ByteArray) (s : Span) : Option String :=
  if s.start ≤ s.stop ∧ s.stop ≤ src.size then String.fromUTF8? (src.extract s.start s.stop) else none

/-- *Executable in the stub*: the grammar above. -/
def readSourceNumber (t : String) : Option Printed

def spanMatches (src : ByteArray) (s : Span) (p : Printed) : Bool :=
  (spanText src s).bind readSourceNumber == some p

theorem spanMatches_iff (src : ByteArray) (s : Span) (p : Printed) :
    spanMatches src s p = true ↔ ∃ t, spanText src s = some t ∧ readSourceNumber t = some p
```

A stated literal's `Printed` is `Printed.ofDec` of its spelling, so "0.30" matches the source text "0.30" or ".30"
and not "0.3". Scientific spellings ("2 × 10⁷" in a source) are outside the grammar: such a value stays unchecked.

## 5. Derivations over rational unknowns (ME-5)

A derivation is `{"id", "follows": claim, "from": [claim ids], "square_links": [[square, root], …]}` over `free`
values. Lean substitutes known values, linearises each premise (a premise that is not linear in the unknowns is
refused with `NonlinearPremise`, naming the term), turns an equality into two facts, searches Farkas multipliers by
Fourier-Motzkin elimination within 64 facts, 16 unknowns and 10,000 combination steps, and replays what it finds.
Outcomes: **follows** (a replayed certificate), **does not follow** (a counterexample checked by evaluation, square
links included), or **unknown** (`limit .derivationSteps`, or `derivationInconclusive` when a needed step is outside
the square rule). The search tries the claimed bound itself as a counterexample candidate first. Physical laws enter as
premises with `support: assumption`.

```lean
/-- A linear form over unknowns with rational coefficients; separate from the frozen integer `VE.Order.Lin`: its
unknowns range over ℚ and it has no cuts. -/
structure QLin where
  const : Rat
  coeffs : List (String × Rat)
  deriving Repr

def QLin.eval (κ : String → Rat) (L : QLin) : Rat := L.const + (L.coeffs.map fun p => p.2 * κ p.1).sum
def QLin.scale (w : Rat) (L : QLin) : QLin := ⟨w * L.const, L.coeffs.map fun p => (p.1, w * p.2)⟩
def QLin.add (L M : QLin) : QLin := ⟨L.const + M.const, L.coeffs ++ M.coeffs⟩
def QLin.coeffOf (L : QLin) (n : String) : Rat := ((L.coeffs.filter (·.1 == n)).map (·.2)).sum

/-- A fact `0 ≤ L`, or `0 < L` when strict. -/
structure QFact where
  form : QLin
  strict : Bool
  deriving Repr

def QFact.Holds (κ : String → Rat) (f : QFact) : Prop :=
  if f.strict then 0 < f.form.eval κ else 0 ≤ f.form.eval κ

/-- ¬(0 ≤ L) is 0 < −L; ¬(0 < L) is 0 ≤ −L. -/
def QFact.negate (f : QFact) : QFact := ⟨f.form.scale (-1), !f.strict⟩
theorem QFact.negate_holds (κ : String → Rat) (f : QFact) : f.negate.Holds κ ↔ ¬ f.Holds κ

structure Farkas where
  weights : List Rat
  deriving Repr

def Farkas.combination (fs : List QFact) (c : Farkas) : QLin :=
  (List.zipWith (fun w f => f.form.scale w) c.weights fs).foldl QLin.add ⟨0, []⟩

/-- One nonnegative weight per fact; the combination cancels every unknown and leaves a negative constant, or zero
with a positive weight on a strict fact. -/
def Farkas.check (fs : List QFact) (c : Farkas) : Bool :=
  let comb := c.combination fs
  c.weights.length == fs.length && c.weights.all (fun w => decide (0 ≤ w)) &&
  (comb.coeffs.map (·.1)).all (fun n => comb.coeffOf n == 0) &&
  (decide (comb.const < 0) ||
    (comb.const == 0 && (List.zipWith (fun w f => decide (0 < w) && f.strict) c.weights fs).any id))

theorem Farkas.check_sound (fs : List QFact) (c : Farkas) (h : c.check fs = true) :
    ∀ κ : String → Rat, ¬ ∀ f ∈ fs, f.Holds κ

/-- The proved square rule (plan D11). -/
theorem lt_of_sq_lt (x a b : Rat) (hx : 0 ≤ x) (hb : 0 < b) (h : x * x < a) (hab : a ≤ b * b) : x < b

/-- A step derives `goal` by a Farkas refutation of the facts so far and `goal.negate`, or derives `0 < b − r` from an
established `0 < a − s`, a link `(s, r)`, `a ≤ b * b` and `0 < b`. -/
inductive Step where
  | farkas (goal : QFact) (cert : Farkas)
  | square (s r : String) (a b : Rat)

structure Derivation where
  steps : List Step

/-- *Opaque*: replays the steps in order; the conclusion must be the last derived fact. -/
def Derivation.check (P : List QFact) (links : List (String × String)) (C : QFact) (d : Derivation) : Bool

theorem Derivation.check_sound (P : List QFact) (links : List (String × String)) (C : QFact) (d : Derivation)
    (h : d.check P links C = true) :
    ∀ κ : String → Rat, (∀ f ∈ P, f.Holds κ) →
      (∀ l ∈ links, κ l.1 = κ l.2 * κ l.2 ∧ 0 ≤ κ l.2) → C.Holds κ

def counterexampleCheck (P : List QFact) (links : List (String × String)) (C : QFact)
    (κ : String → Rat) : Bool :=
  P.all (fun f => decide (f.Holds κ)) &&
    links.all (fun l => κ l.1 == κ l.2 * κ l.2 && decide (0 ≤ κ l.2)) && !decide (C.Holds κ)

/-- Debate A2: a counterexample satisfies every square link and its nonnegativity condition. -/
theorem Counterexample.check_sound (P : List QFact) (links : List (String × String)) (C : QFact)
    (κ : String → Rat) (h : counterexampleCheck P links C κ = true) :
    (∀ f ∈ P, f.Holds κ) ∧ (∀ l ∈ links, κ l.1 = κ l.2 * κ l.2 ∧ 0 ≤ κ l.2) ∧ ¬ C.Holds κ
```

Linear infeasibility over ℚ with rational coefficients is infeasibility over the reals, so the soundness also holds
for real-valued quantities; `lean/CALC.md` states this, not a theorem (plan 9).

## 6. Physical dimensions (ME-6)

### 6.1 Dimensions and unit-change invariance

```lean
/-- A physical dimension: an exponent per base dimension; normal form sorted by name, no zero exponent. -/
structure PhysDim where
  exps : List (String × Int)
  deriving Repr, DecidableEq, Inhabited

def PhysDim.Normal (d : PhysDim) : Prop :=
  (d.exps.map (·.1)).Pairwise (· < ·) ∧ ∀ e ∈ d.exps, e.2 ≠ 0
def PhysDim.one : PhysDim := ⟨[]⟩

/-- Add exponent `e.2` of base `e.1` into a sorted list, dropping a zero exponent. -/
def insertExp (e : String × Int) : List (String × Int) → List (String × Int)
  | [] => if e.2 = 0 then [] else [e]
  | (n, k) :: rest =>
    if e.1 = n then (if k + e.2 = 0 then rest else (n, k + e.2) :: rest)
    else if e.1 < n then (if e.2 = 0 then (n, k) :: rest else e :: (n, k) :: rest)
    else (n, k) :: insertExp e rest

def PhysDim.mul (a b : PhysDim) : PhysDim := ⟨b.exps.foldl (fun acc e => insertExp e acc) a.exps⟩
def PhysDim.inv (a : PhysDim) : PhysDim := ⟨a.exps.map fun e => (e.1, -e.2)⟩
def PhysDim.npow (a : PhysDim) (k : Nat) : PhysDim :=
  if k = 0 then PhysDim.one else ⟨a.exps.map fun e => (e.1, e.2 * k)⟩

/-- Literals are dimensionless; sums and differences need equal dimensions (`none` is `DimensionMismatch`). -/
def Expr.dimOf (Γ : String → Option PhysDim) : Expr → Option PhysDim
  | .lit _ => some PhysDim.one
  | .val n => Γ n
  | .add a b | .sub a b => do
      let x ← a.dimOf Γ
      let y ← b.dimOf Γ
      if x = y then some x else none
  | .mul a b => do let x ← a.dimOf Γ; let y ← b.dimOf Γ; pure (x.mul y)
  | .div a b => do let x ← a.dimOf Γ; let y ← b.dimOf Γ; pure (x.mul y.inv)
  | .pow a k => (a.dimOf Γ).map (·.npow k)

/-- A change of base units: a positive factor per base dimension. -/
structure Rescale where
  factor : String → Rat
  pos : ∀ b, 0 < factor b

def zpowR (q : Rat) : Int → Rat
  | .ofNat n => q ^ n
  | .negSucc n => 1 / q ^ (n + 1)

def Rescale.of (ρ : Rescale) (d : PhysDim) : Rat :=
  (d.exps.map fun e => zpowR (ρ.factor e.1) e.2).foldl (· * ·) 1

theorem Rescale.of_pos (ρ : Rescale) (d : PhysDim) : 0 < ρ.of d
theorem Rescale.of_mul (ρ : Rescale) (a b : PhysDim) (ha : a.Normal) (hb : b.Normal) :
    ρ.of (a.mul b) = ρ.of a * ρ.of b
theorem Rescale.of_one (ρ : Rescale) : ρ.of PhysDim.one = 1

/-- Every named value rescaled by its own physical dimension's factor. -/
def Rescale.apply (ρ : Rescale) (Γ : String → Option PhysDim) (σ : Values) : Values :=
  fun n => match σ n, Γ n with
    | some q, some d => some (q * ρ.of d)
    | v, _ => v

theorem denotes_rescale (Γ : String → Option PhysDim) (ρ : Rescale) (σ : Values) (e : Expr) (d : PhysDim)
    (x : Rat) (hΓ : ∀ n d', Γ n = some d' → d'.Normal) (hd : e.dimOf Γ = some d) (hx : Denotes σ e x) :
    Denotes (ρ.apply Γ σ) e (x * ρ.of d)

/-- **Unit-change invariance**: a comparison of two expressions of one physical dimension has the same truth in
every system of base units. -/
theorem compare_invariant (Γ : String → Option PhysDim) (ρ : Rescale) (σ : Values) (c : Comparison)
    (a b : Expr) (d : PhysDim) (hΓ : ∀ n d', Γ n = some d' → d'.Normal)
    (ha : a.dimOf Γ = some d) (hb : b.dimOf Γ = some d) :
    (Claim.compare c a b).Holds σ ↔ (Claim.compare c a b).Holds (ρ.apply Γ σ)

/-- A rounding claim is admitted only on a dimensionless expression, whose truth no change of units moves. -/
theorem rounds_invariant (Γ : String → Option PhysDim) (ρ : Rescale) (σ : Values) (r : Rounding)
    (e : Expr) (p : Printed) (hΓ : ∀ n d', Γ n = some d' → d'.Normal) (he : e.dimOf Γ = some PhysDim.one) :
    (Claim.rounds r e p).Holds σ ↔ (Claim.rounds r e p).Holds (ρ.apply Γ σ)

/-- Units are values (their factor to the coherent unit): `q` in unit `u` is `q · fu / fv` in unit `v`. Quantities'
QT-A7 uses this theorem. -/
theorem convert_by_factors (σ : Values) (u v : String) (fu fv q x : Rat) (hu : σ u = some fu)
    (hv : σ v = some fv) (hfv : fv ≠ 0) :
    Denotes σ (.mul (.lit q) (.val u)) x ↔ Denotes σ (.mul (.lit (q * fu / fv)) (.val v)) x

/-- `ve-units@1` tags stay nominal (debate A5): each is read as its own base dimension. -/
def legacyDim (tag : String) : PhysDim := ⟨[(tag, 1)]⟩
theorem legacy_nominal (t t' : String) (h : t ≠ t') : legacyDim t ≠ legacyDim t'
```

`compare_invariant` has no hypothesis beyond equal dimensions, normal forms and positive factors (plan 9).

### 6.2 `ve-units@2`

ME-6 owns `ve-units@2` and is its only decoder; quantities' QT-A7 consumes it. An environment declares
`"unit_schema": "ve-units@2"`, `"base_dimensions": [identifiers]` (for example `length`, `time`, `mass`, and
document-declared ones such as `fringe`) and `"units": {name: {"base_exponents": {base: integer}, "factor":
<literal>}}` with an exact positive factor to the coherent unit of that dimension. A unit is also a value: "11 meters"
is `["mul", ["lit", "11"], ["val", "meter"]]`, and `σ meter` is the meter's factor. Each value may declare `"unit"`;
its dimension is that unit's, and an undeclared value is dimensionless. The decoder refuses:

- a unit whose name is an affine unit (`celsius`, `degree_celsius`, `fahrenheit`, `degree_fahrenheit`) or a
  logarithmic one (`decibel`, `bel`, `neper`): `AffineUnit: <name>`, `LogarithmicUnit: <name>`;
- a zero, negative or non-literal factor: `InvalidInput: units.<name>.factor`;
- a declaration that gives `day` `base_exponents`: `CalendarTagNotUnit: day (durations use elapsed_day)`; `day` is
  W6a's calendar-date tag and never converts;
- a sum, difference or comparison of different dimensions: `DimensionMismatch: <dimension> and <dimension>`, each
  written as its base exponents ("length", "length per time");
- a rounding claim on an expression that is not dimensionless: `RoundingNeedsNumber: divide by one <unit> to round
  <words>` (the printed number must say its unit: "the displacement divided by one fringe width is 0.4 when rounded to
  one decimal place, with exact ties going up").

A `ve-units@1` environment is decoded by W6a's frozen decoder, unchanged; its identity is unchanged. Each of its tags
is read as its own base dimension (`legacyDim`), so two identically declared tags remain incompatible
(`units-schema.md` 2.1), and a sum of `usd_cent` and `eur_cent` is `DimensionMismatch`.

## 7. Statistics (ME-7)

```lean
def sampleVariance? (xs : List Rat) : Option Rat :=
  if xs.length < 2 then none
  else
    let m := xs.sum / xs.length
    some ((xs.map fun x => (x - m) * (x - m)).sum / (xs.length - 1 : Nat))

def populationVariance? (xs : List Rat) : Option Rat :=
  if xs = [] then none
  else
    let m := xs.sum / xs.length
    some ((xs.map fun x => (x - m) * (x - m)).sum / xs.length)

def rootGe (v c : Rat) : Prop := c ≤ 0 ∨ c * c ≤ v     -- √v ≥ c
def rootGt (v c : Rat) : Prop := c < 0 ∨ c * c < v     -- √v > c
def rootLe (v c : Rat) : Prop := 0 ≤ c ∧ v ≤ c * c     -- √v ≤ c
def rootLt (v c : Rat) : Prop := 0 < c ∧ v < c * c     -- √v < c
def rootEq (v c : Rat) : Prop := 0 ≤ c ∧ c * c = v     -- √v = c

/-- "The square root of v, rounded, is p", by squared bounds; this is the definition. -/
def SqrtRoundsTo (r : Rounding) (p : Printed) (v : Rat) : Prop :=
  let u := tenPow p.places
  let D : Rat := p.digits
  0 ≤ v ∧ match r with
  | .tiesUp => rootGe v ((2 * D - 1) / (2 * u)) ∧ rootLt v ((2 * D + 1) / (2 * u))
  | .halfEven => (rootGt v ((2 * D - 1) / (2 * u)) ∧ rootLt v ((2 * D + 1) / (2 * u))) ∨
      ((rootEq v ((2 * D - 1) / (2 * u)) ∨ rootEq v ((2 * D + 1) / (2 * u))) ∧ p.digits % 2 = 0)
  | .down => rootGe v (D / u) ∧ rootLt v ((D + 1) / u)
  | .up => rootGt v ((D - 1) / u) ∧ rootLe v (D / u)

instance (r : Rounding) (p : Printed) (v : Rat) : Decidable (SqrtRoundsTo r p v)

/-- Agreement with rounding the root whenever the root is rational. -/
theorem sqrtRoundsTo_of_square (r : Rounding) (p : Printed) (s v : Rat) (hs : 0 ≤ s) (hv : s * s = v) :
    SqrtRoundsTo r p v ↔ RoundsTo r p s

def signs : Nat → List (List Int)
  | 0 => [[]]
  | n + 1 => (signs n).flatMap fun s => [1 :: s, -1 :: s]

theorem signs_length (n : Nat) : (signs n).length = 2 ^ n
theorem mem_signs (n : Nat) (s : List Int) : s ∈ signs n ↔ s.length = n ∧ ∀ k ∈ s, k = 1 ∨ k = -1

def absR (x : Rat) : Rat := if x < 0 then -x else x

/-- The exact two-sided sign-flip p value: the share of sign vectors whose signed mean is at least the observed mean
in absolute value, the observed vector counted (`paper/analysis/README.md`). -/
def signFlipP (d : List Rat) : Rat :=
  let obs := absR (d.sum / d.length)
  let hits := (signs d.length).filter fun s =>
    decide (obs ≤ absR ((List.zipWith (fun (k : Int) (x : Rat) => (k : Rat) * x) s d).sum / d.length))
  (hits.length : Rat) / ((2 ^ d.length : Nat) : Rat)

theorem signFlipP_grain (d : List Rat) :
    ∃ m : Nat, m ≤ 2 ^ d.length ∧ signFlipP d = (m : Rat) / ((2 ^ d.length : Nat) : Rat)

/-- Core Lean v4.24.0 has no `Nat.choose` (checked in the stub), so ME-7 defines it. -/
def choose : Nat → Nat → Nat
  | _, 0 => 1
  | 0, _ + 1 => 0
  | n + 1, k + 1 => choose n k + choose n (k + 1)

theorem choose_succ_succ (n k : Nat) : choose (n + 1) (k + 1) = choose n k + choose n (k + 1)

/-- P(X ≥ k) for X binomial with n trials and success probability p. -/
def binomialTail (n k : Nat) (p : Rat) : Rat :=
  ((List.range (n + 1)).filter (k ≤ ·)).foldl
    (fun acc i => acc + (choose n i : Rat) * p ^ i * (1 - p) ^ (n - i)) 0

theorem binomialTail_zero (n : Nat) (p : Rat) : binomialTail n 0 p = (p + (1 - p)) ^ n

/-- Cohen's kappa of a square agreement table; none when the table is empty or chance agreement is 1. -/
def kappa? (t : List (List Nat)) : Option Rat :=
  let k := t.length
  let n : Rat := ((t.map List.sum).sum : Nat)
  if n = 0 then none else
  let po := ((List.range k).map fun i => (((t.getD i []).getD i 0 : Nat) : Rat)).sum / n
  let rowsum := t.map fun r => ((r.sum : Nat) : Rat)
  let colsum := (List.range k).map fun j => (((t.map fun r => r.getD j 0).sum : Nat) : Rat)
  let pe := (List.zipWith (· * ·) rowsum colsum).sum / (n * n)
  if pe = 1 then none else some ((po - pe) / (1 - pe))
```

Wire forms (new expressions over a list of values or a table column): `["mean", xs]`, `["variance", xs]` (divisor
n − 1), `["population-variance", xs]` (divisor n), `["sign-flip-p", xs]` (n ≤ 16, else `SignFlipTooLong`),
`["binomial-tail", n, k, p]`, `["kappa", table]` (square, else `KappaTableNotSquare`), and the claim
`["sqrt-rounds", e, printed]` (with an optional tie rule as for `rounds`). Each procedure adds its assumption as a
residual line: sign flips, "the differences are independent and their signs exchangeable under the null"; binomial,
"the trials are independent with one success probability"; a stated quantile such as t = 2.593, "the stated quantile
is the 97.5% point of Student's t with 11 degrees of freedom" (`support: testimony`, with its source).

## 8. Consistency of printed numbers (ME-8) and algebraic identities (ME-9)

### 8.1 Consistency

`["consistent", inputs, outputs]`: inputs are names with printed values (each standing for its rounding interval),
outputs are claims. A **witness** (exact inputs inside the intervals under which every output holds) proves
*consistent*; an **enclosure** (exact interval evaluation over the input boxes) that misses an output's printed
interval proves *inconsistent*; a granularity refutation proves *inconsistent*; otherwise unknown
(`consistencyInconclusive`, or `limit .witnessPoints` after 4,096 candidate points). Lean tries as witnesses the
printed values themselves and then the interval endpoints.

```lean
def InBox (r : Rounding) (inputs : List (String × Printed)) (σ : Values) : Prop :=
  ∀ i ∈ inputs, ∃ x, σ i.1 = some x ∧ RoundsTo r i.2 x

/-- *Opaque* checkers. -/
def witnessCheck (r : Rounding) (inputs : List (String × Printed)) (outs : List Claim) (σ : Values) : Bool
def enclose (r : Rounding) (inputs : List (String × Printed)) (e : Expr) : Option (Rat × Rat)
def refuteByEnclosure (r : Rounding) (inputs : List (String × Printed)) (c : Claim) : Bool

theorem witness_sound (r : Rounding) (inputs : List (String × Printed)) (outs : List Claim) (σ : Values)
    (h : witnessCheck r inputs outs σ = true) : InBox r inputs σ ∧ ∀ c ∈ outs, c.Holds σ
theorem enclose_sound (r : Rounding) (inputs : List (String × Printed)) (e : Expr) (lo hi : Rat)
    (h : enclose r inputs e = some (lo, hi)) :
    ∀ σ x, InBox r inputs σ → (∀ n, σ n ≠ none → n ∈ inputs.map Prod.fst) → Denotes σ e x →
      lo ≤ x ∧ x ≤ hi
theorem inconsistent_of_enclosure (r : Rounding) (inputs : List (String × Printed)) (c : Claim)
    (h : refuteByEnclosure r inputs c = true) :
    ¬ ∃ σ, InBox r inputs σ ∧ (∀ n, σ n ≠ none → n ∈ inputs.map Prod.fst) ∧ c.Holds σ

/-- No multiple of `1/g` rounds to `p` under `r` (the candidates are the multiples near p's interval). -/
def grainRefutes (g : Nat) (r : Rounding) (p : Printed) : Bool :=
  let u := tenPow p.places
  let a := Rat.floor ((p.digits - 1 : Rat) / u * g) - 1
  let b := Rat.ceil ((p.digits + 1 : Rat) / u * g) + 1
  (List.range (b - a + 1).toNat).all fun i => !decide (RoundsTo r p (((a + i : Int) : Rat) / g))

theorem grain_sound (g : Nat) (hg : 0 < g) (r : Rounding) (p : Printed) (h : grainRefutes g r p = true) :
    ∀ m : Int, ¬ RoundsTo r p ((m : Rat) / g)
/-- Granularity of sign-flip p values (uses ME-7's `signFlipP_grain`, hence ME-7 → ME-8). -/
theorem signFlip_grain_refutes (d : List Rat) (r : Rounding) (p : Printed)
    (h : grainRefutes (2 ^ d.length) r p = true) : ¬ RoundsTo r p (signFlipP d)
/-- GRIM: the mean of n integers is a multiple of 1/n. -/
theorem mean_grain_refutes (xs : List Int) (hx : xs ≠ []) (r : Rounding) (p : Printed)
    (h : grainRefutes xs.length r p = true) :
    ¬ RoundsTo r p ((xs.map fun (x : Int) => (x : Rat)).sum / xs.length)
```

### 8.2 Identities

`["identity", a, b]` over free values: Lean normalises both sides to polynomials over ℚ (sorted monomials, merged
coefficients, zeros dropped) or, with division, to numerator and denominator, compares cross-multiplied normal forms
and reports **identity**, or **not an identity** with a rational point where both sides denote and differ (found by
trying small values), or unknown (`identityNotShown`; `limit .polyTerms` above 10,000 monomials).

```lean
structure Mono where
  coeff : Rat
  vars : List (String × Nat)

abbrev Poly := List Mono

def Poly.eval (κ : String → Rat) (p : Poly) : Rat :=
  (p.map fun m => m.coeff * (m.vars.map fun v => κ v.1 ^ v.2).foldl (· * ·) 1).sum

/-- *Opaque*: the normaliser (division-free expressions only) and the fraction form. -/
def Poly.ofExpr? : Expr → Option Poly
def Frac.ofExpr? : Expr → Option (Poly × Poly)
def identityCheck (a b : Expr) : Bool

theorem Poly.ofExpr_sound (κ : String → Rat) (e : Expr) (p : Poly) (h : Poly.ofExpr? e = some p) :
    Denotes (fun n => some (κ n)) e (p.eval κ)
theorem Frac.ofExpr_sound (κ : String → Rat) (e : Expr) (n d : Poly) (x : Rat)
    (h : Frac.ofExpr? e = some (n, d)) (hx : Denotes (fun v => some (κ v)) e x) :
    d.eval κ ≠ 0 ∧ x = n.eval κ / d.eval κ
/-- Equal cross-multiplied normal forms mean equal values wherever both sides denote. -/
theorem identity_sound (a b : Expr) (h : identityCheck a b = true) (κ : String → Rat) (x y : Rat)
    (hx : Denotes (fun v => some (κ v)) a x) (hy : Denotes (fun v => some (κ v)) b y) : x = y

def differsAt (a b : Expr) (κ : List (String × Rat)) : Bool :=
  let σ : Values := fun n => κ.lookup n
  match a.eval σ, b.eval σ with
  | some x, some y => x != y
  | _, _ => false

theorem differsAt_sound (a b : Expr) (κ : List (String × Rat)) (h : differsAt a b κ = true) :
    ∃ x y, Denotes (fun n => κ.lookup n) a x ∧ Denotes (fun n => κ.lookup n) b y ∧ x ≠ y

end VE.Calc
```

## 9. Rendering and reading back (ME-1, ME-11)

```lean
namespace VE.Calc.English
/-- *Opaque*: Lean's English line for a claim (ME-1, display only; `none` when an expression exceeds 11.2's nesting
rule, and the display then names the intermediate values). -/
def renderClaim (words : String → Option String) (c : Claim) : Option String
/-- *Opaque*: the claim an English line reads as, by Lean's English engine (ME-11). -/
def readClaim (words : String → Option String) (s : String) : Except String Claim
/-- Parse-back: every rendered line reads as the same claim. -/
theorem read_render (words : String → Option String) (c : Claim) (s : String)
    (h : renderClaim words c = some s) : readClaim words s = .ok c
end VE.Calc.English
```

Whole-sentence uniqueness is the engine's existing `english_reading_unique` (`lean/VE/EnglishGrammar/Read.lean:174`),
extended by ME-11's rules; ME-11 states its instances when QT-E fixes the engine's interface.

## 10. Documents (ME-10)

`calculation` content in `ve-document@1` goes through Lean's `document` mode (one branch in
`lean/VE/Service/Document.lean`, in the document-mode queue after AT-3b, SC-1b, QT-A4, ET-5 and WG-4). A claim-graph
leaf labelled `calc:<case>/<claim>` is discharged by running the case and requiring **holds**. `support: calculation`
counts as checked only with a Lean verdict.

```lean
namespace VE.Calc

inductive UnitStatus where
  | checked | open_ | unformalised
  deriving Repr, DecidableEq

/-- A unit with calculation content: UNFORMALISED (`missing-input`) if it has no claim or a claim is undefined;
otherwise OPEN if a claim is unknown; otherwise CHECKED (holds, or fails with a finding). -/
def unitStatus (os : List Outcome) : UnitStatus :=
  if os = [] ∨ os.contains (.decided .undefined) then .unformalised
  else if os.any (fun o => match o with | .unknown _ => true | _ => false) then .open_
  else .checked

theorem unitStatus_checked_iff (os : List Outcome) :
    unitStatus os = .checked ↔ os ≠ [] ∧ ∀ o ∈ os, o = .decided .holds ∨ o = .decided .fails

def calcLeafDischarged (c : Case) (claimId : String) : Bool :=
  match c.claims.lookup claimId with
  | some cl => cl.run c.decls == .decided .holds
  | none => false

theorem calcLeaf_discharged_iff (c : Case) (claimId : String) :
    calcLeafDischarged c claimId = true ↔
      ∃ cl, c.claims.lookup claimId = some cl ∧ cl.run c.decls = .decided .holds
theorem calcLeaf_holds (c : Case) (h : WellFormed c.decls) (claimId : String)
    (hd : calcLeafDischarged c claimId = true) :
    ∃ cl, c.claims.lookup claimId = some cl ∧ cl.Holds (values c.decls)

end VE.Calc
```

A unit whose numbers are checked but whose hedge or causal framing is not is MIXED (plan 7): hedged calculation units
("probably less than one sixth") stay `hedged` labels until a separately reviewed calc–attitudes bridge exists. A W6a
or relational claim may not cite a `calc:` leaf (no bridge between the profiles is designed). Residual lines use W2's
`support` provenance field: stated values' supports, data digests, procedures' assumptions, free values' premises,
and import labels.

## 11. English

All wordings are Lean's: ME-1 renders them (display only); ME-11 makes them readable as input in Lean's English engine.
The comparison phrases have one owner (1.4). The English authoring milestone also needs the pre-registered writing
and comprehension eval (plan D17); this section fixes what that eval tests.

### 11.1 Sentences

Each wording has one reading; the right column is Lean's rendered line for the canonical claim, which is the same
sentence (parse-back, `read_render`). `<P>` is a printed number; `<places>` is "to one decimal place", "to <two …
twenty> decimal places", "to <n> decimal places" above twenty, "to a whole number" (k = 0), or "to a multiple of ten
to the power <n>" (k = −n < 0).

| Form | Wording | Meaning |
|---|---|---|
| stated | "The number of weakening attacks is 243." | `stated 243` |
| stated with unit (ME-6) | "The path length is 11 meters." | `stated` 11 × meter |
| defined | "Let the false-approval rate in strict VE be the number of weakening attacks approved in strict VE divided by the number of weakening attacks." | `defined` (`div`) |
| free (ME-5) | "Let the velocity ratio be an unknown number." | `free` |
| counted (ME-4) | "Let the approved 32B trials be the number of rows of the trial table whose judge is 32B and that are approved." | `counted` with `and (isText judge "32B") (isTrue approved)`, `count`; "whose <column> is <text>", "whose <column> equals <number>", "that are <column>", their negations "is not", "that are not", a list joined by "and", and "either … or …" at the top only |
| equals | "A equals B." | `compare ⟨eq, false⟩` |
| order | "A is less than B." / "A is at most B." / "A is more than B." / "A is at least B." | `compare` with the four rows of `orderPhrases` |
| range | "A is from L through H." | `within` (both ends included) |
| rounding, default rule | "The false-approval rate is 0.296 when rounded to three decimal places, with exact ties going up." | `rounds tiesUp` |
| rounding, half to even | "The p value is 0.007812 when rounded to six decimal places, with exact ties going to the even digit." | `rounds halfEven` |
| printed bounds | "The lower bound is 0.019 when rounded down to three decimal places." / "… when rounded up to …" | `rounds down` / `rounds up` |
| square root (ME-7) | "The standard deviation of the twelve differences, with divisor eleven, is 0.108 when rounded to three decimal places, with exact ties going up." | `sqrt-rounds` of the sample variance |
| derivation (ME-5) | "Assume the following. 1. The displacement is the product of 0.4 and the square of the velocity ratio. 2. The displacement is less than 0.02. From these, it follows that the velocity ratio is less than 1 divided by 4." | premises 1 and 2 (`support: assumption`), link (square, ratio), conclusion |
| identity (ME-9) | "For all values of the unknowns for which both sides are defined, the round-trip time equals the closed-form time." | `identity` of the two named values' definitions over the free values |

The rendered line of every rounding claim names its rule. "Numbers in this document are rounded half to even." is not
a wording: it needs scope's anchor reach for section-scoped declarations, which is not yet a build item, and even then
each sentence's paraphrase names the rule.

### 11.2 Expressions: phrases and the nesting rule

```
expression ::= term
             | atom "minus" term
             | atom "divided by" term
             | atom "to the power" natural
term       ::= atom
             | "twice" term | "half of" term | "the square of" term | "the cube of" term
             | "the sum of" term "and" term | "the product of" term "and" term
atom       ::= value words | numeral | numeral "times ten to the power" integer
```

- "A minus B" is A − B (debate A6). "The difference between A and B" is refused with the rewrite "A minus B": many
  readers take it to mean the size of the gap.
- An infix phrase ("minus", "divided by", "to the power") stands only at the top of an expression; its left operand is
  an atom. So "the square of A minus B", "twice A divided by B" and "D divided by C minus V" have no parse and are
  refused with a rewrite that names the inner value ("Let the closing speed be the speed of light minus the speed.").
- At most one phrase inside another (plan 2.11): a phrase's operands are atoms or phrases whose operands are atoms.
  Deeper nesting is refused (`NestedPhrase`) with the rewrite "Let … be …".
- Value words begin with "the", contain none of "and", "minus", "divided by", "to the power", "times ten to the
  power", "is", "equals", "when rounded", "through", and do not begin with a phrase word ("the sum of", "the product
  of", "the square of", "the cube of", "twice", "half of"): `ValueWordsForm`, `ReservedWord`.
- Numerals are decimal digits ("0.25", "243"); symbols (`+`, `−`, `×`, `/`, `^`, `=`, `≈`, `<`, `≤`) are refused in VE
  text (`SymbolInText`). The formula view (`2D v²/V²`) is a display generated from the meaning and never parsed.

With these rules a term is prefix notation with "and" separators, and an expression has at most one infix operator at
its top, so every accepted expression has one parse; ME-11 proves it as an instance of the engine's uniqueness.

| Refused sentence | Why | Rewrite |
|---|---|---|
| "The expected displacement is twice the path length divided by the wavelength, times the square of the speed ratio." | two parses; "times" is not a phrase | "Let the path in wavelengths be the path length divided by the wavelength. Let the squared ratio be the square of the speed ratio. The expected displacement is twice the product of the path in wavelengths and the squared ratio." |
| "The round-trip time is the sum of the path length divided by the speed of light minus the speed and the path length divided by the sum of the speed of light and the speed." | "minus" inside "divided by", and "and" at two levels | "Let the closing speed be the speed of light minus the speed. Let the outward time be the path length divided by the closing speed. Let the return time be the path length divided by the sum of the speed of light and the speed. The round-trip time is the sum of the outward time and the return time." |
| "The rate is about 0.3." | approximation word | "The rate is 0.3 when rounded to one decimal place, with exact ties going up." or "The rate is from 0.25 through 0.35." |
| "The standard deviation of the differences is 0.108." | two readings (divisor n − 1 or n) | name the divisor: "…, with divisor eleven, …" |
| "Our method is on par with the baseline." | open comparison | an open term with a decider (W2) |

"About", "approximately", "roughly" and "nearly" are one row of english-lean's catalogue shared with quantities,
which QT-A6 adds; ME-11 reuses it and adds "on the order of", "on par" and "comparable". In translation each is a
reading set {rounded to the written digits, an open tolerance with a decider}; in authoring each is refused with the
rewrite above.

### 11.3 Arithmetic statements (`arith@0`, ME-12; display only)

`arith@0` input is JSON in this plan; Lean renders each statement (ME-12's `Render.lean`) and EX-1's bar item 6
audits M-3's rendering.

| Construct | Wording |
|---|---|
| bounded universal | "for every whole number n from 1 through 161, …" ("integer" when the lower bound is not a numeral at least 0) |
| bounded existential | "there is an integer p from the sum of n and 1 through twice n such that …" |
| unbounded | "for every whole number n, …"; "there is a whole number p such that …"; "for every integer i, …" |
| count | "the number of whole numbers p from 1 through x such that p is prime" |
| atoms | "n equals m", "n is less than m", "n is at most m", "d divides p" |
| connectives | "both A and B", "either A or B", "if A, then B", "it is not the case that A"; a chain of one connective as "A, B and C" |
| predicate definition | "A whole number p is prime exactly when p is at least 2 and no whole number d from 2 through p minus 1 divides p." |
| function definition | "The prime count of a whole number x is the number of whole numbers p from 1 through x such that p is prime." |
| M-3 | "For every whole number n, if n is at least 1, then there is a whole number p such that p is prime, n is less than p, and p is at most twice n." |

## 12. `arith@0` (ME-12) and proof imports (ME-13)

### 12.1 Syntax and meaning (debate F4)

```lean
namespace VE.Arith
open VE.Numbers

mutual
inductive Term where
  | var (i : Nat)
  | num (n : Int)
  | add (a b : Term)
  | sub (a b : Term)
  | mul (a b : Term)
  | call (f : String) (args : List Term)
  | countFromTo (lo hi : Term) (φ : Formula)
inductive Formula where
  | eq (a b : Term)
  | lt (a b : Term)
  | le (a b : Term)
  | dvd (a b : Term)
  | call (p : String) (args : List Term)
  | not (φ : Formula)
  | and (φ ψ : Formula)
  | or (φ ψ : Formula)
  | imp (φ ψ : Formula)
  | allNat (φ : Formula)
  | exNat (φ : Formula)
  | allInt (φ : Formula)
  | exInt (φ : Formula)
  | allFromTo (lo hi : Term) (φ : Formula)
  | exFromTo (lo hi : Term) (φ : Formula)
end

/-- The meaning of each defined name. -/
structure Env where
  funs : String → Option (Nat × (List Int → Option Int))
  preds : String → Option (Nat × (List Int → Prop))

open Classical in
mutual
/-- Variables are de Bruijn indices into `ρ`; a count is the number of `i` from `lo` through `hi` for which `Holds`
of its condition is decided true, by classical decision. Neither function mentions an evaluator. -/
noncomputable def Term.value (E : Env) (ρ : List Int) : Term → Option Int
  | .var i => ρ[i]?
  | .num n => some n
  | .add a b => match Term.value E ρ a, Term.value E ρ b with
    | some x, some y => some (x + y)
    | _, _ => none
  | .sub a b => match Term.value E ρ a, Term.value E ρ b with
    | some x, some y => some (x - y)
    | _, _ => none
  | .mul a b => match Term.value E ρ a, Term.value E ρ b with
    | some x, some y => some (x * y)
    | _, _ => none
  | .call f args => match E.funs f, Term.values E ρ args with
    | some (n, g), some xs => if xs.length = n then g xs else none
    | _, _ => none
  | .countFromTo lo hi φ => match Term.value E ρ lo, Term.value E ρ hi with
    | some l, some h =>
      some ((((List.range (h - l + 1).toNat).filter fun (i : Nat) =>
        decide (Holds E ((l + (i : Int)) :: ρ) φ)).length : Nat) : Int)
    | _, _ => none
noncomputable def Term.values (E : Env) (ρ : List Int) : List Term → Option (List Int)
  | [] => some []
  | t :: ts => match Term.value E ρ t, Term.values E ρ ts with
    | some x, some xs => some (x :: xs)
    | _, _ => none
noncomputable def Holds (E : Env) (ρ : List Int) : Formula → Prop
  | .eq a b => ∃ x y, Term.value E ρ a = some x ∧ Term.value E ρ b = some y ∧ x = y
  | .lt a b => ∃ x y, Term.value E ρ a = some x ∧ Term.value E ρ b = some y ∧ x < y
  | .le a b => ∃ x y, Term.value E ρ a = some x ∧ Term.value E ρ b = some y ∧ x ≤ y
  | .dvd a b => ∃ x y, Term.value E ρ a = some x ∧ Term.value E ρ b = some y ∧ x ∣ y
  | .call p args => ∃ n P xs, E.preds p = some (n, P) ∧ Term.values E ρ args = some xs ∧
      xs.length = n ∧ P xs
  | .not φ => ¬ Holds E ρ φ
  | .and φ ψ => Holds E ρ φ ∧ Holds E ρ ψ
  | .or φ ψ => Holds E ρ φ ∨ Holds E ρ ψ
  | .imp φ ψ => Holds E ρ φ → Holds E ρ ψ
  | .allNat φ => ∀ n : Nat, Holds E ((n : Int) :: ρ) φ
  | .exNat φ => ∃ n : Nat, Holds E ((n : Int) :: ρ) φ
  | .allInt φ => ∀ n : Int, Holds E (n :: ρ) φ
  | .exInt φ => ∃ n : Int, Holds E (n :: ρ) φ
  | .allFromTo lo hi φ => ∃ l h, Term.value E ρ lo = some l ∧ Term.value E ρ hi = some h ∧
      ∀ i : Int, l ≤ i → i ≤ h → Holds E (i :: ρ) φ
  | .exFromTo lo hi φ => ∃ l h, Term.value E ρ lo = some l ∧ Term.value E ρ hi = some h ∧
      ∃ i : Int, l ≤ i ∧ i ≤ h ∧ Holds E (i :: ρ) φ
end

/-- Definitions in order; a body reads its parameters as `var 0 … var (arity − 1)` and only earlier names. -/
inductive Def where
  | fn (name : String) (arity : Nat) (body : Term)
  | pred (name : String) (arity : Nat) (body : Formula)

abbrev Defs := List Def

noncomputable def Defs.env (D : Defs) : Env :=
  D.foldl (fun E d => match d with
    | .fn f n body => { E with funs := fun g => if g = f then some (n, fun xs => Term.value E xs body) else E.funs g }
    | .pred p n body => { E with preds := fun q => if q = p then some (n, fun xs => Holds E xs body) else E.preds q })
    ⟨fun _ => none, fun _ => none⟩

def Defs.Means (D : Defs) (φ : Formula) : Prop := Holds D.env [] φ
```

Admission (decoder checks; *opaque* Boolean functions with these meanings): `Defs.WellFormed D` holds when names are
distinct, each body reads only its parameters and bound variables (indices below the binder depth plus the arity),
each call names an earlier definition with its arity (a definition that calls itself or a later name is
`RecursiveDefinition`), and every count's condition is bounded (`UnboundedCount`). `Formula.Scoped D depth φ` holds
when every variable index is below `depth` plus the binders above it and every call names a definition of `D` with
its arity. A definition is interpreted in the environment of the definitions before it, so the meaning needs no
termination argument beyond the list.

```lean
def Defs.WellFormed (D : Defs) : Bool
def Formula.Scoped (D : Defs) (depth : Nat) (φ : Formula) : Bool
```

### 12.2 Boundedness and the budget (debate F5)

A formula is bounded when it has no `allNat`, `exNat`, `allInt` or `exInt`, here or in a definition it calls:

```lean
mutual
def Term.bnd (B : String → Bool) : Term → Bool
  | .var _ => true
  | .num _ => true
  | .add a b => Term.bnd B a && Term.bnd B b
  | .sub a b => Term.bnd B a && Term.bnd B b
  | .mul a b => Term.bnd B a && Term.bnd B b
  | .call f args => B f && Term.bndList B args
  | .countFromTo lo hi φ => Term.bnd B lo && Term.bnd B hi && Formula.bnd B φ
def Term.bndList (B : String → Bool) : List Term → Bool
  | [] => true
  | t :: ts => Term.bnd B t && Term.bndList B ts
def Formula.bnd (B : String → Bool) : Formula → Bool
  | .eq a b => Term.bnd B a && Term.bnd B b
  | .lt a b => Term.bnd B a && Term.bnd B b
  | .le a b => Term.bnd B a && Term.bnd B b
  | .dvd a b => Term.bnd B a && Term.bnd B b
  | .call p args => B p && Term.bndList B args
  | .not φ => Formula.bnd B φ
  | .and φ ψ => Formula.bnd B φ && Formula.bnd B ψ
  | .or φ ψ => Formula.bnd B φ && Formula.bnd B ψ
  | .imp φ ψ => Formula.bnd B φ && Formula.bnd B ψ
  | .allNat _ => false
  | .exNat _ => false
  | .allInt _ => false
  | .exInt _ => false
  | .allFromTo lo hi φ => Term.bnd B lo && Term.bnd B hi && Formula.bnd B φ
  | .exFromTo lo hi φ => Term.bnd B lo && Term.bnd B hi && Formula.bnd B φ
end

def Defs.boundedNames (D : Defs) : String → Bool :=
  D.foldl (fun B d => match d with
    | .fn f _ body => fun g => if g = f then Term.bnd B body else B g
    | .pred p _ body => fun q => if q = p then Formula.bnd B body else B q) (fun _ => false)

def Formula.Bounded (D : Defs) (φ : Formula) : Bool := Formula.bnd D.boundedNames φ
```

**Fuel accounting.** One unit is charged per **formula-node visit**, exactly as W6's `VE.Time.evalB`: a visit is
refused (UNKNOWN) when the units already spent reach the budget. Term nodes are free; a count is charged through its
condition's visits, once per value in its range; a predicate call is one visit plus its body's visits. Connectives
short-circuit left to right (`imp` evaluates its antecedent first); a bounded quantifier tries lo, lo + 1, … in order
and stops at the first decisive value; a count visits every value in its range. The budget is
`maxSteps = VE.Time.maxEvaluations = 1,000,000` by default and at most; a case may set a smaller `"budget"`. The
following evaluator is the accounting:

```lean
def charge {α : Type} (limit w : Nat) (k : Nat → Option (α × Nat)) : Option (α × Nat) :=
  if limit ≤ w then none else k (w + 1)

def quantLoop (universal : Bool) (step : Int → Nat → Option (Bool × Nat)) :
    Nat → Int → Nat → Option (Bool × Nat)
  | 0, _, w => some (universal, w)
  | n + 1, i, w => match step i w with
    | none => none
    | some (b, w') => if b = universal then quantLoop universal step n (i + 1) w' else some (!universal, w')

def countLoop (step : Int → Nat → Option (Bool × Nat)) : Nat → Int → Nat → Nat → Option (Int × Nat)
  | 0, _, acc, w => some ((acc : Int), w)
  | n + 1, i, acc, w => match step i w with
    | none => none
    | some (b, w') => countLoop step n (i + 1) (if b then acc + 1 else acc) w'

structure OpEnv where
  funs : String → Option (Nat × (List Int → Nat → Option (Int × Nat)))
  preds : String → Option (Nat × (List Int → Nat → Option (Bool × Nat)))

mutual
def Term.evalB (E : OpEnv) (limit : Nat) (ρ : List Int) : Term → Nat → Option (Int × Nat)
  | .var i, w => (ρ[i]?).map fun x => (x, w)
  | .num n, w => some (n, w)
  | .add a b, w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).map fun r => (x + r.1, r.2)
  | .sub a b, w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).map fun r => (x - r.1, r.2)
  | .mul a b, w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).map fun r => (x * r.1, r.2)
  | .call f args, w => match E.funs f with
    | none => none
    | some (n, g) => match Term.evalBs E limit ρ args w with
      | none => none
      | some (xs, w) => if xs.length = n then g xs w else none
  | .countFromTo lo hi φ, w => match Term.evalB E limit ρ lo w with
    | none => none
    | some (l, w) => match Term.evalB E limit ρ hi w with
      | none => none
      | some (h, w) => countLoop (fun i w => Formula.evalB E limit (i :: ρ) φ w) (h - l + 1).toNat l 0 w
def Term.evalBs (E : OpEnv) (limit : Nat) (ρ : List Int) : List Term → Nat → Option (List Int × Nat)
  | [], w => some ([], w)
  | t :: ts, w => match Term.evalB E limit ρ t w with
    | none => none
    | some (x, w) => (Term.evalBs E limit ρ ts w).map fun r => (x :: r.1, r.2)
def Formula.evalB (E : OpEnv) (limit : Nat) (ρ : List Int) : Formula → Nat → Option (Bool × Nat)
  | .eq a b, w => charge limit w fun w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).map fun r => (decide (x = r.1), r.2)
  | .lt a b, w => charge limit w fun w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).map fun r => (decide (x < r.1), r.2)
  | .le a b, w => charge limit w fun w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).map fun r => (decide (x ≤ r.1), r.2)
  | .dvd a b, w => charge limit w fun w => match Term.evalB E limit ρ a w with
    | none => none
    | some (x, w) => (Term.evalB E limit ρ b w).map fun r => (decide (x ∣ r.1), r.2)
  | .call p args, w => charge limit w fun w => match E.preds p with
    | none => none
    | some (n, P) => match Term.evalBs E limit ρ args w with
      | none => none
      | some (xs, w) => if xs.length = n then P xs w else none
  | .not φ, w => charge limit w fun w => (Formula.evalB E limit ρ φ w).map fun r => (!r.1, r.2)
  | .and φ ψ, w => charge limit w fun w => match Formula.evalB E limit ρ φ w with
    | none => none
    | some (true, w) => Formula.evalB E limit ρ ψ w
    | some (false, w) => some (false, w)
  | .or φ ψ, w => charge limit w fun w => match Formula.evalB E limit ρ φ w with
    | none => none
    | some (true, w) => some (true, w)
    | some (false, w) => Formula.evalB E limit ρ ψ w
  | .imp φ ψ, w => charge limit w fun w => match Formula.evalB E limit ρ φ w with
    | none => none
    | some (true, w) => Formula.evalB E limit ρ ψ w
    | some (false, w) => some (true, w)
  | .allNat _, _ => none
  | .exNat _, _ => none
  | .allInt _, _ => none
  | .exInt _, _ => none
  | .allFromTo lo hi φ, w => charge limit w fun w => match Term.evalB E limit ρ lo w with
    | none => none
    | some (l, w) => match Term.evalB E limit ρ hi w with
      | none => none
      | some (h, w) => quantLoop true (fun i w => Formula.evalB E limit (i :: ρ) φ w) (h - l + 1).toNat l w
  | .exFromTo lo hi φ, w => charge limit w fun w => match Term.evalB E limit ρ lo w with
    | none => none
    | some (l, w) => match Term.evalB E limit ρ hi w with
      | none => none
      | some (h, w) => quantLoop false (fun i w => Formula.evalB E limit (i :: ρ) φ w) (h - l + 1).toNat l w
end

def Defs.opEnv (limit : Nat) (D : Defs) : OpEnv :=
  D.foldl (fun E d => match d with
    | .fn f n body => { E with funs := fun g => if g = f then some (n, fun xs w => Term.evalB E limit xs body w) else E.funs g }
    | .pred p n body => { E with preds := fun q => if q = p then some (n, fun xs w => Formula.evalB E limit xs body w) else E.preds q })
    ⟨fun _ => none, fun _ => none⟩

def maxSteps : Nat := VE.Time.maxEvaluations

/-- The value and the units spent, or none (UNKNOWN). -/
def decideBounded (D : Defs) (limit : Nat) (φ : Formula) : Option (Bool × Nat) :=
  Formula.evalB (D.opEnv limit) limit [] φ 0

theorem decideBounded_sound (D : Defs) (hD : D.WellFormed = true) (φ : Formula)
    (hφ : φ.Scoped D 0 = true) (limit : Nat) (b : Bool) (w : Nat)
    (h : decideBounded D limit φ = some (b, w)) : D.Means φ ↔ b = true
theorem decideBounded_mono (D : Defs) (φ : Formula) (limit limit' : Nat) (r : Bool × Nat)
    (h : decideBounded D limit φ = some r) (hl : limit ≤ limit') : decideBounded D limit' φ = some r
theorem decideBounded_work (D : Defs) (φ : Formula) (limit : Nat) (b : Bool) (w : Nat)
    (h : decideBounded D limit φ = some (b, w)) : w ≤ limit
theorem decideBounded_complete (D : Defs) (hD : D.WellFormed = true) (φ : Formula)
    (hφ : φ.Scoped D 0 = true) (hb : φ.Bounded D = true) : ∃ limit r, decideBounded D limit φ = some r

/-- A statement's row. An unbounded statement is classified before any evaluation. -/
def arithOutcome (D : Defs) (limit : Nat) (φ : Formula) : Outcome :=
  if φ.Bounded D then
    match decideBounded D limit φ with
    | some (true, _) => .decided .holds
    | some (false, _) => .decided .fails
    | none => .unknown (.limit .evaluations)
  else .unknown .unboundedStatement

theorem arithOutcome_unbounded_iff (D : Defs) (limit : Nat) (φ : Formula) :
    arithOutcome D limit φ = .unknown .unboundedStatement ↔ φ.Bounded D = false
theorem arithOutcome_exhausted_iff (D : Defs) (limit : Nat) (φ : Formula) :
    arithOutcome D limit φ = .unknown (.limit .evaluations) ↔
      φ.Bounded D = true ∧ decideBounded D limit φ = none
theorem arithOutcome_decided (D : Defs) (hD : D.WellFormed = true) (φ : Formula)
    (hφ : φ.Scoped D 0 = true) (limit : Nat) (v : Verdict) (h : arithOutcome D limit φ = .decided v) :
    v ≠ .undefined ∧ (v = .holds ↔ D.Means φ)

end VE.Arith
```

`decideBounded_sound` is the agreement of the evaluator with `Holds` that debate F4 asks for, conditional on
completion; `decideBounded_mono` says a larger budget never changes an answer. A well-scoped statement always denotes,
so `arith@0` has no undefined verdict; an exhausted budget is unknown and is tested apart (fixtures M-4x, M-1b).

### 12.3 The example vocabulary (`lean/VE/Arith/Examples.lean`)

```lean
namespace VE.Arith.Examples
open VE.Arith

/-- p is prime: p is at least 2 and no whole number from 2 through p − 1 divides p. -/
def primeBody : Formula :=
  .and (.le (.num 2) (.var 0)) (.not (.exFromTo (.num 2) (.sub (.var 0) (.num 1)) (.dvd (.var 0) (.var 1))))

def primeDefs : Defs := [.pred "prime" 1 primeBody]

def IsPrime (p : Nat) : Prop := 2 ≤ p ∧ ∀ d : Nat, 2 ≤ d → d < p → ¬ d ∣ p

/-- M-3, whole-number reading. -/
def bertrand : Formula :=
  .allNat (.imp (.le (.num 1) (.var 0))
    (.exNat (.and (.call "prime" [.var 0]) (.and (.lt (.var 1) (.var 0)) (.le (.var 0) (.mul (.num 2) (.var 1)))))))

/-- The core-Lean unfolding lemma the import project rewrites with. -/
theorem bertrand_means_iff :
    primeDefs.Means bertrand ↔ ∀ n : Nat, 1 ≤ n → ∃ p : Nat, IsPrime p ∧ n < p ∧ p ≤ 2 * n

end VE.Arith.Examples
```

### 12.4 Imports (debate A3; ME-13 only if EX-1 passes)

```lean
namespace VE.Arith

structure Import where
  statementId : String
  meansDigest : String
  project : String
  projectRev : String
  toolchain : String
  mathlibRev : String
  declaration : String
  checkDigest : String
  axioms : List String

def allowedAxioms : List String := ["propext", "Classical.choice", "Quot.sound"]

/-- *Opaque*: the statement's `meaning_id`: `VE.Route.Wire.meaningId ["arith@0"] envId` over the canonical JSON of
the definitions and the formula. -/
def statementIdOf (D : Defs) (φ : Formula) : String
/-- *Opaque*: SHA-256 of the sources that define `Term`, `Formula`, `Holds`, `Defs.env` and `Defs.Means`
(`lean/VE/Arith/{Syntax,Holds,Defs}.lean`), written by a generator into `lean/VE/Arith/MeansDigest.lean`. -/
def currentMeansDigest : String
/-- *Opaque*: the generated Lean file the import project compiles:
`theorem VEImports.Check.c_<id> : VE.Arith.Defs.Means <D as a Lean term> <φ as a Lean term> := <declaration>`. -/
def checkSource (D : Defs) (φ : Formula) (declaration : String) : String
/-- *Opaque*: admission (identity, meaning-source digest, check-file digest, axiom allowlist, names). -/
def Import.admit (D : Defs) (φ : Formula) (i : Import) : Except String Unit

theorem Import.admit_sound (D : Defs) (φ : Formula) (i : Import) (h : i.admit D φ = .ok ()) :
    i.statementId = statementIdOf D φ ∧ i.meansDigest = currentMeansDigest ∧
      i.checkDigest = VE.CertificateWire.sha256 (checkSource D φ i.declaration).toUTF8 ∧
      ∀ a ∈ i.axioms, a ∈ allowedAxioms

def importLabel (i : Import) : String := s!"import:{i.project}@{i.projectRev}/{i.declaration}"

structure Conclusion where
  defs : Defs
  formula : Formula

inductive Support where
  | bounded (limit : Nat)
  | imported (i : Import)

structure ReportRow where
  conclusion : Conclusion
  support : Support

structure Report where
  rows : List ReportRow
  assumptions : List String

def Report.Accepted (r : Report) : Prop :=
  ∀ row ∈ r.rows, match row.support with
    | .bounded limit => ∃ w, decideBounded row.conclusion.defs limit row.conclusion.formula = some (true, w)
    | .imported i => i.admit row.conclusion.defs row.conclusion.formula = .ok () ∧ importLabel i ∈ r.assumptions

/-- *Opaque*: the `arith` report of a request. -/
def Run.report : Lean.Json → Option Report

theorem Run.report_accepted (j : Lean.Json) (r : Report) (h : Run.report j = some r) : r.Accepted
theorem report_import_labelled (r : Report) (h : r.Accepted) :
    ∀ row ∈ r.rows,
      (∃ limit w, row.support = .bounded limit ∧
        decideBounded row.conclusion.defs limit row.conclusion.formula = some (true, w)) ∨
      (∃ i, row.support = .imported i ∧
        i.statementId = statementIdOf row.conclusion.defs row.conclusion.formula ∧
        importLabel i ∈ r.assumptions)
theorem bounded_row_means (r : Report) (h : r.Accepted) (row : ReportRow) (hrow : row ∈ r.rows)
    (limit : Nat) (hs : row.support = .bounded limit) (hD : row.conclusion.defs.WellFormed = true)
    (hφ : row.conclusion.formula.Scoped row.conclusion.defs 0 = true) :
    row.conclusion.defs.Means row.conclusion.formula

end VE.Arith
```

Each imported conclusion needs an import admitted for its own statement. The external kernel checks the generated
`check` theorem, so the declaration's type is exactly `Defs.Means D φ` at the VE revision whose meaning sources have
`meansDigest`; VE checks the record, not the proof, and admission stays conditional on that external build. The
residual line reads "Proved in Lean with Mathlib at revision <rev>, declaration <name>; VE did not replay this proof."
The Mathlib side of EX-1 (from the plan; `Nat.bertrand` is from memory, since no Mathlib was available to ME-S):

```lean
import Mathlib.NumberTheory.Bertrand
import VE.Arith.Examples

theorem VEImports.bertrand_holds : VE.Arith.Examples.primeDefs.Means VE.Arith.Examples.bertrand := by
  rw [VE.Arith.Examples.bertrand_means_iff]
  intro n hn
  obtain ⟨p, hp, h1, h2⟩ := Nat.bertrand n (by omega)
  exact ⟨p, (VEImports.isPrime_iff_nat_prime p).mpr hp, h1, h2⟩

theorem VEImports.isPrime_iff_nat_prime (p : Nat) : VE.Arith.Examples.IsPrime p ↔ Nat.Prime p
```

## 13. Diagnostics and fixtures

### 13.1 Diagnostics

Every diagnostic is in Lean's table; Python shows its text. Decode refusals end the case; claim-level results are
outcomes (1.5).

| Code | Batch | When | Text |
|---|---|---|---|
| `InvalidInput` | ME-2 | a field is missing, of the wrong JSON type, or unknown | `InvalidInput: <path> <what is wrong>` |
| `ResourceLimit` | ME-2 | a limit of 3.2 | `ResourceLimit: <limit> exceeds <n>` |
| `UnknownName` | ME-2 | an expression reads a name not declared before it | `UnknownName: <name> (declare it before the value that uses it)` |
| `DuplicateName` | ME-2 | two values share a name | `DuplicateName: <name>` |
| `DuplicateClaimId` | ME-2 | two claims share an id | `DuplicateClaimId: <id>` |
| `NoClaims` | ME-2 | `claims` is empty | `NoClaims: a calculation needs at least one claim` |
| `VerbalisationCollision` | ME-2 | W6a's check | as W6a |
| `ValueWordsForm` | ME-2 | words do not begin with "the" or begin with a phrase word | `ValueWordsForm: the words of <name> must begin with "the" and not with "<phrase>"` |
| `ReservedWord` | ME-2 | words contain a reserved word (11.2) | `ReservedWord: "<word>" in the words of <name>` |
| `CalcClaimFails` | ME-10 | authoring: a claim fails | the transcription-unchecked text of 2.5 |
| `UnknownHandle` | ME-4 | a `data` or `source` handle not registered | `UnknownHandle: <sha256>` |
| `DigestMismatch` | ME-4 | registered bytes do not hash to the handle | `DigestMismatch: <sha256>` |
| `TableFormat` | ME-4 | bytes outside the CSV or JSON-lines subset | `TableFormat: <handle> line <n>: <what>` |
| `UnknownColumn` | ME-4 | a filter or aggregate names an undeclared column | `UnknownColumn: <column>` |
| `SpanMismatch` | ME-4 | a span does not read as its number | `SpanMismatch: <name> is <spelling> but the source bytes from <start> up to <stop> read "<text>"` |
| `NonlinearPremise` | ME-5 | a premise not linear in the unknowns | `NonlinearPremise: <term> (declare a square link or name the product)` |
| `UnknownLink` | ME-5 | a square link names a value that is not free | `UnknownLink: <name>` |
| `DimensionMismatch` | ME-6 | 6.2 | `DimensionMismatch: <dimension> and <dimension>` |
| `RoundingNeedsNumber` | ME-6 | 6.2 | `RoundingNeedsNumber: divide by one <unit> to round <words>` |
| `AffineUnit`, `LogarithmicUnit` | ME-6 | 6.2 | `AffineUnit: <name>`, `LogarithmicUnit: <name>` |
| `CalendarTagNotUnit` | ME-6 | 6.2 | `CalendarTagNotUnit: day (durations use elapsed_day)` |
| `SignFlipTooLong` | ME-7 | more than 16 values | `SignFlipTooLong: <n> values (at most 16)` |
| `KappaTableNotSquare` | ME-7 | a non-square table | `KappaTableNotSquare: <rows> rows, <columns> columns` |
| `NestedPhrase` | ME-11 | 11.2 | `NestedPhrase: name the inner value: "Let … be …"` |
| `DifferenceBetween` | ME-11 | "the difference between A and B" | `DifferenceBetween: write "A minus B"` |
| `ApproximationWord` | ME-11 | "about", "approximately", "roughly", "nearly", "on the order of" | the shared catalogue row's text, with the rounding or range rewrite |
| `OpenComparisonWord` | ME-11 | "on par", "comparable" | `OpenComparisonWord: "<word>" needs an open term with a decider` |
| `SymbolInText` | ME-11 | a symbol in VE text | `SymbolInText: <the symbol's name, such as "the plus sign"> at <position>: write the phrase (11.2)` |
| `AmbiguousStandardDeviation` | ME-11 | "standard deviation" without a divisor | `AmbiguousStandardDeviation: name the divisor, the number of values or one less than it` |
| `RecursiveDefinition` | ME-12 | a definition calls itself or a later name | `RecursiveDefinition: <name>` |
| `ArityMismatch` | ME-12 | a call with the wrong number of arguments | `ArityMismatch: <name> takes <n>` |
| `UnboundedCount` | ME-12 | a count's condition has an unbounded quantifier | `UnboundedCount: the condition of a count must be bounded` |
| `ImportStatement` | ME-13 | the record's statement id is not this conclusion's | `ImportStatement: the import proves <id>, not <id>` |
| `ImportMeansDigest` | ME-13 | built against other meaning sources | `ImportMeansDigest: <digest>` |
| `ImportCheckDigest` | ME-13 | the check file is not the one VE generates | `ImportCheckDigest: <digest>` |
| `ImportAxiom` | ME-13 | an axiom outside the allowlist | `ImportAxiom: <axiom>` |

No diagnostic text contains a symbol (plan 9); each refusal names its rewrite.

### 13.2 Fixture definitions

Definitions are given here; the expected results, computed in the stub, are in 13.3. Sources marked *paraphrase* are
re-anchored to byte spans in ME-0.

| Id | Source | Case |
|---|---|---|
| V-1 | `paper/sections/04-e1.md`: "Its scored baseline, 176/594 = .296" | stated 176, 594; baseline = 176 / 594; claims `rounds tiesUp baseline (296, 3)`, `baseline < 0.30` |
| V-1n | the same | `rounds tiesUp baseline (297, 3)` |
| V-2 | `04-e1.md`: "false approval is 52/243 (.214) versus 31/243 (.128), an 8.6-point pooled increase" | plan 2.1's case: rates 52/243 and 31/243, increase = 100 × (rate_strict − rate_symbols); claims (214, 3), (128, 3), (86, 1), ties up |
| V-3 | `05-e4.md`: "prose rejects 56/60 … from 4/60" | `60 − 56 = 4`, with the assumption leaf "every reply is an approval or a rejection" |
| V-4 | `04-e1.md`: "34/110 false approvals" in the 30-60% gate | rate = 34 / 110; `within rate 0.30 0.60` |
| V-5 | `paper/generated/posthoc-weakening-rates.md`, 20 rows | each `approved / 243` against its "Pooled FA", ties up, three places |
| V-6 | `paper/sections/10-appendices.md:97`, row "14B AWQ, P1 attacker" | the twelve printed differences; claims `sqrt-rounds` of the sample variance to 0.108, of variance/12 to 0.031, of 2.593² × variance/12 to 0.081 |
| V-6r | the same | `sqrt-rounds` of the population variance to 0.108 |
| V-7 | `paper/generated/posthoc-weakening-contrasts.md`, "Two-sided p", 8 rows of 9 templates | `grainRefutes 512` of each printed p, both rules |
| V-8 | the same, row "14B F − S attacker", "0.007812" | 4/512 at six places, both rules |
| V-9 | software convention "Python 3.12": 2.675 printed as 2.67 | stated 2.675; `rounds tiesUp (267, 2)`; `"software"` declared |
| V-10 | software convention: 0.1 + 0.2 − 0.3 printed as 0.0000000000000001 | `rounds tiesUp` of the sum to (1, 16); `"software"` declared |
| V-11 | debate A1 | x = 10³⁹ (stated), y = x⁶⁴, z = y × y; claims `z < 1`, `1 / (x − x) = 1`, `y < 1` |
| V-12 | debate F1 | source bytes "Its scored baseline, 176/594 = .296, is outside; claimed covered bytes 4,792 (43.90%)"; spans [31, 35) (".296"), [21, 24) ("176"), [71, 76) ("4,792"), [78, 83) ("43.90"), [30, 35), [31, 200) |
| V-13 | finding kinds | `findingKind` of (no software, [checked, checked]), (no software, [checked, unchecked]), (no software, []), (software, [checked]) |
| D-1 | ROADMAP: "17/19 … (15 tableau certificates plus T9 and T9e)" | `15 + 2 = 17` |
| D-2 | UDHR pilot SUMMARY: "claimed covered bytes 4,792 (43.90%)" of 10,916 | `rounds tiesUp (100 × 4792 / 10916) (4390, 2)` |
| D-3 | constitution pilot SUMMARY: 2,951 bytes (1.60%); 73 + 349 + 2,529 | `73 + 349 + 2529 = 2951`; `rounds tiesUp (100 × 2951 / 184893) (160, 2)` |
| H-1 | *paraphrase*: D/(V − v) + D/(V + v) = 2DV/(V² − v²) | identity over free D, V, v |
| H-2 | *paraphrase*: 2DV²/(V² − v²) − 2D(1 + v²/V²) = 2Dv⁴/(V²(V² − v²)) | identity |
| H-3 | *paraphrase*: 2D(1 + v²/V²) − 2D(1 + v²/(2V²)) = Dv²/V² | identity |
| H-4 | *paraphrase*: 2D × (10⁻⁴)² = 2D × 10⁻⁸; with D = 2 × 10⁷ stated | identity in D; with D stated, `2 × D × ratio² = 0.4` |
| H-5 | *paraphrase*: "the displacement to be expected was 0.4 fringe" | path = 2 × 10⁷, ratio = 10⁻⁴: `2 × path × ratio² = 0.4` |
| H-6 | *paraphrase*: "certainly less than the twentieth part … less than one-fourth" | premises d = 0.4 s, d < 0.02; link (s, r); conclusion r < 1/4; certificate weights [1, 0, 1, 0.4] on [d − 0.4s ≥ 0, 0.4s − d ≥ 0, 0.02 − d > 0, negated goal] |
| H-6p | the "probably" pair: fortieth part, one sixth | d < 0.01; conclusion r < 1/6; same weights |
| H-6n | negative control: "less than one fifth" | conclusion r < 1/5; candidate κ: r = 1/5, s = 1/25, d = 0.016 |
| H-6a | debate A2 | H-6's premises; candidate κ: r = 1, s = 0, d = 0, against r < 1/4, with and without the link |
| H-7 | physical dimensions | Γ: D, λ lengths; V, v length per time; T time; D/(V − v), D/λ, D + T |
| H-7u | unit change | path 2 × 10⁷ (length), ratio 10⁻⁴ (dimensionless); rescale length by 1,000; `2 × path × ratio² < path` and `rounds tiesUp (2 × ratio²) (2, 8)`; negative pair: `2 × path × ratio² = 0.4 × path` and `rounds tiesUp (2 × ratio²) (3, 8)` |
| H-7c | conversion | 2.5 × kilometer against 2,500 × meter (factors 1,000 and 1) |
| H-7l | legacy tags | `usd_cent` and `eur_cent` as `ve-units@1` tags; `a + b` |
| H-7d | `day` | a `ve-units@2` declaration giving `day` `{"time": 1}` |
| H-8 | *paraphrase*: "about eleven meters, or 2 × 10⁷ wave-lengths" | length 11, wavelength 5.89 × 10⁻⁷ (testimony): `rounds tiesUp (length / wavelength) (2, −7)` |
| H-9 | the two observation tables | counted means against the printed means; no outcome is presumed |
| H-10 | the dates July 8-12, 1887 | refused (W6a dates start at 1970-01-01); W6's trigger ET-T3 |
| S-1 | kappa and binomial | `kappa?` of [[20, 5], [10, 15]] and [[5, 0], [0, 0]]; `binomialTail 10 8 (1/2)`, `binomialTail 10 0 (1/3)` |
| S-2 | sign flips | `signFlipP [1, 1, 1, 1]`; `signFlipP [1, 2, −1, 3, 2, 1, −2, 4, 1, 2, 3, −1]`; `(signs 12).length` |
| S-3 | GRIM | a mean of five integers printed as 3.47, 3.40, 3.4 |
| S-4 | square roots | `SqrtRoundsTo tiesUp` of 9/100 to 0.3 and 0.4, beside `RoundsTo` of 3/10 |
| T-1 | tables (A4) | table judge/approved/score: ("32B", true, 3), ("32B", false, 5), ("14B", true, absent); filters `judge is "7B"` (empty), `judge is "32B"`, `approved`, `not approved` |
| T-2 | digest | a data handle whose bytes hash differently |
| M-1 | Ramanujan, *paraphrase*: true for n from 1 to 161 | `allFromTo 1 161 (exFromTo (n + 1) (2n) (prime p))` |
| M-1b | budget boundary | M-1 with budgets 17,010 and 17,011 |
| M-2 | the chain 2, 3, 5, 7, 13, 23, 43, 83, 163 | each prime, each less than twice the one before |
| M-3 | Bertrand's postulate, whole-number reading | `bertrand` (12.3) |
| M-3r | the real reading of x | a reading set {whole number, real}; `arith@0` has no reals |
| M-4 | π(x) − π(x/2) ≥ 2 for x ≥ 11 | `primeCount x = #{p ∈ [1, x] : prime p}`, `halfPrimeCount x = #{p ∈ [1, x] : 2p ≤ x ∧ prime p}`; `allFromTo 11 N (2 ≤ primeCount x − halfPrimeCount x)` at N = 200, 248, 249, 1,000 |
| M-4x | exhaustion | M-1 with budget 1,000 |
| M-5 | negative control | strict n < p < 2n for n from 1 through 161 |
| M-6 | the prime predicate | VE's `prime` against `IsPrime` on 0 through 400 |
| E-1 | documents | case: a = 52, n = 243, r = a / n; claims c1 `rounds r (214, 3)`, c2 `rounds r (213, 3)`; leaves c1, c2, c3; statuses of [holds, fails], [holds, unknown], [holds, undefined], [] |

### 13.3 Expected results (computed in the stub)

| Id | Expected | Computed values |
|---|---|---|
| V-1 | holds, holds | 176/594 = 8/27; 2,000 × 8/27 = 16,000/27 = 592.59…, in [591, 593); `round tiesUp 3` gives 296 |
| V-1n | **fails** | 592.59… < 593 |
| V-2 | holds × 3 | 2,000 × 52/243 = 104,000/243 = 427.98… in [427, 429); 62,000/243 = 255.14… in [255, 257); 20 × 100 × 21/243 = 14,000/81 = 172.83… in [171, 173); 100 × 21/243 = 700/81 = 8.642… |
| V-3 | holds | 60 − 56 = 4 |
| V-4 | holds | 34/110 = 17/55 = 0.309… |
| V-5 | holds × 20 | all 20 rows true; none is an exact tie at three places |
| V-6 | holds × 3 | Σx = −109/200, Σx² = 152,053/1,000,000, sample variance 1,527,611/132,000,000; in units of 1/132,000,000: 1,525,425 ≤ 1,527,611 < 1,553,937 (0.1075² and 0.1085²); 2.593² × v/12 = 10,271,120,172,539/1,584,000,000,000,000 = 0.0064843…, above 0.0805² = 25,921/4,000,000 = 0.00648025 |
| V-6r | **fails** | population variance 1,527,611/144,000,000; its root rounds to 0.103 only (the only D in 0…199 with `SqrtRoundsTo tiesUp (D, 3)`) |
| V-7 | 7 of 8 not refuted under ties up; the eighth (0.007812) refuted under ties up, not under half to even | the multiples m/512 that round to each printed p under ties up: 416, 44, 352, none, 348, 184, 64, 448; under half to even the fourth is 4. 44/512 = 11/128 and 348/512 = 87/128 are exact ties at six places whose upper neighbour is even, so both rules agree |
| V-8 | holds only under half to even | `tieAt 6 (4/512)` = true; ties up false, half to even true; `round tiesUp` 7,813, `round halfEven` 7,812 |
| V-9 | exact claim **fails**; reproduction unknown; finding `softwareUnreproduced` | ties up false, half to even false; `tieAt 2 2.675` = true; both rules round to 268 |
| V-10 | exact claim **fails**; reproduction unknown; finding `softwareUnreproduced` | exact value 0; both rules false; `round tiesUp 16 0` = 0 |
| V-11 | **unknown** (`limit .digits`), **undefined**, **fails** | digit counts of 10³⁹, 10^(39·64), 10^(39·128): 40, 2,497, 4,993 |
| V-12 | checked, refused, checked, checked, checked, refused, refused, refused | `spanText`: ".296", "176", "4,792", "43.90"; `spanMatches`: [31,35) vs (296,3) true, vs (297,3) false; [21,24) vs (176,0) true; [71,76) vs (4792,0) true; [78,83) vs (4390,2) true, vs (439,1) false; [30,35) (" .296") false; [31,200) (outside) false |
| V-13 | `source`, `transcriptionUnchecked`, `transcriptionUnchecked`, `softwareUnreproduced` | as computed |
| D-1 | holds | 15 + 2 = 17 |
| D-2 | holds | 200 × 100 × 4,792/10,916 = 23,960,000/2,729 = 8,779.77… in [8,779, 8,781) |
| D-3 | holds × 2 | 73 + 349 + 2,529 = 2,951; 200 × 100 × 2,951/184,893 = 59,020,000/184,893 = 319.21… in [319, 321) |
| H-1, H-2, H-3 | identity (ME-9) | the stub evaluated both sides at (D, V, v) = (11, 3, 1), (2, 5, −3), (7/3, 1/2, 1/7): no point differs; at V = v the left side of H-1 does not denote; the normaliser's result is ME-9's |
| H-4, H-5 | holds | 2 × (2 × 10⁷) × (10⁻⁴)² = 0.4 exactly |
| H-6 | **follows** | 0.02/0.4 = 1/20 and 0.4/20 = 1/50; `Farkas.check` with weights [1, 0, 1, 0.4] true; with −0.4 false (forged); 1/20 ≤ (1/4)² true |
| H-6p | **follows**; "probably" stays a `hedged` label | `Farkas.check` true; 1/40 ≤ (1/6)² true |
| H-6n | **does not follow** | 1/20 ≤ (1/5)² false; `counterexampleCheck` true with r = 1/5, s = 1/25, d = 2/125 |
| H-6a | rejected with the link, accepted without it | with the link (s, r): false; without links: true (draft 1's contract would have accepted it) |
| H-7 | time; dimensionless; `DimensionMismatch` | `dimOf`: {time: 1}, {}, none |
| H-7u | holds, holds, holds, holds; fails, fails, fails, fails | dimensions of both sides {length: 1}; `Rescale.of` length 1,000, velocity 1,000, one 1; the rescaled path is 2 × 10¹⁰ |
| H-7c | holds; the negative direction fails | both 2,500; 2.5 × kilometer is not 2.5 |
| H-7l | `DimensionMismatch` | `legacyDim usd_cent ≠ legacyDim eur_cent`; `dimOf (a + b)` = none |
| H-7d | refused (`CalendarTagNotUnit`) | decoder check (ME-6) |
| H-8 | holds; "about" is a reading set; the wavelength is a residual leaf | 11/(5.89 × 10⁻⁷) = 11,000,000,000/589 = 18,675,721.5…; 2y = 2,200/589 = 3.735… in [3, 5); printed (2, −7) |
| H-9 | whatever exact arithmetic gives; a mismatch is a finding | not presumed |
| H-10 | refused | W6a dates start at 1970-01-01 |
| S-1 | 2/5; none; 7/128; 1 | as computed |
| S-2 | 1/8; 57/1,024; 4,096 | as computed |
| S-3 | 3.47 refuted (GRIM); 3.40 and 3.4 not refuted | 17/5 = 3.4, 18/5 = 3.6 |
| S-4 | true, true; false, false | `sqrtRoundsTo_of_square` both directions |
| T-1 | empty: count 0, sum 0, mean, min, max undefined; 32B: 2, 8, 4, 3, 5; approved: count 2, sum, mean, min, max undefined (an absent score); not approved: count 1 | as computed |
| T-2 | refused (`DigestMismatch`) | decoder check (ME-4) |
| M-1 | holds | `decideBounded primeDefs 1,000,000` = (true, 17,011 units) |
| M-1b | unknown at 17,010; holds at 17,011 | exactly the units M-1 spends |
| M-2 | holds | (true, 395 units) |
| M-3 | stated, not decided (`unboundedStatement`); proved only by import (EX-1) | `Bounded` false |
| M-3r | reading set; the real reading stays residual | — |
| M-4 | holds through 248 within 1,000,000 units; unknown from 249 | π(10) − π(5) = 1 (111 units) and π(11) − π(5) = 2 (127 units); at N = 200: (true, 576,518); at 248: (true, 998,395); at 249: none, and (true, 1,008,568) with a budget of 2,000,000; at 1,000: none |
| M-4x | unknown (`limit .evaluations`) | none at budget 1,000 |
| M-5 | **fails** at n = 1 | (false, 2 units): the range 2…1 is empty |
| M-6 | agree on 0…400 | 78 primes |
| E-1 | c1 discharged, c2 not (fails), c3 not (missing); statuses CHECKED, OPEN, UNFORMALISED, UNFORMALISED | as computed |

M-4's candidate bounds were 200 and 1,000 (debate F5). Under the accounting of 12.2, which is part of the semantics,
the largest completing bound is 248; ME-12 re-measures it with its implementation (which must charge identically, so
the count is the same) and pins it. No runtime estimate is part of the semantics.

### 13.4 Each "exactly when" in both directions

| Statement | Positive direction (both sides true) | Negative direction (both sides false) |
|---|---|---|
| `roundsTo_iff_round` | V-1 | V-1n |
| `rules_agree_off_tie` | V-1 (no tie; both rules hold) | V-1n (no tie; both fail) |
| `rules_differ_iff` | V-8 (tie, upper 7,813 odd: 7,813 against 7,812) | 27/200 at two places (tie, upper 14 even: 14 and 14); V-1 (no tie: 296 and 296) |
| `Expr.eval_iff` | V-2's rate_strict: some 52/243 | 1/(2 − 2): none |
| `Claim.decide_holds` | V-1 | V-1n |
| `Claim.decide_fails` | V-1n | V-1 (holds); a free value (undefined) |
| `Claim.decide_undefined` | a free value; 1/0 | V-1 |
| `values_defined` | rate_strict with q = 52/243 | rate_strict with q = 0.214 |
| `findingKind_source_iff` | V-13 (no software, all checked) | V-13's other three |
| `Table.select_iff` | T-1: the two 32B rows | T-1: the 14B row with filter `judge is "32B"` |
| `Agg.run_mean` | T-1 32B: mean 4 | T-1 empty selection: none |
| `spanMatches_iff` | V-12 [31, 35) against (296, 3) | V-12 [31, 35) against (297, 3); [31, 200) |
| `QFact.negate_holds` | s = 1/10: the goal fails, its negation holds | s = 1/40: the goal holds, its negation fails |
| `compare_invariant` | H-7u `<` claim: holds before and after | H-7u `=` claim: fails before and after |
| `rounds_invariant` | H-7u (2, 8): holds before and after | H-7u (3, 8): fails before and after |
| `convert_by_factors` | H-7c: 2,500 both | H-7c: 2.5 neither |
| `sqrtRoundsTo_of_square` | S-4 at 0.3 | S-4 at 0.4 |
| `mem_signs` | [1, −1] ∈ signs 2 | [1, 0] ∉ signs 2 |
| `unitStatus_checked_iff` | [holds, fails] | [holds, unknown]; []; [holds, undefined] |
| `calcLeaf_discharged_iff` | E-1 c1 | E-1 c2 (fails), c3 (missing) |
| `decideBounded_sound` | M-1 (true; it holds) | M-5 (false; it fails) |
| `arithOutcome_unbounded_iff` | M-3 | M-1 |
| `arithOutcome_exhausted_iff` | M-4x; M-1b at 17,010 | M-1b at 17,011; M-3 (unbounded, not exhausted) |
| `arithOutcome_decided` | M-1 (holds) | M-5 (fails) |
| `bertrand_means_iff` | — | — |

`bertrand_means_iff` relates two unbounded statements, so no evaluation can show either direction. M-6 checks its
ingredient (VE's `prime` agrees with `IsPrime` on 0 through 400), and M-1 is its bounded instance; the proof is an
unfolding of definitions (ME-12).

### 13.5 Negative controls and regressions

- Constitution u0203.s02, u0112.s03 and u0147.s04 stay as they are: their "evidence" and "probability" are epistemic
  standards in norms. A calc case cannot carry a norm, an open term or a reading of them (`InvalidInput`).
- W6a's news fixtures (`tests/test_news_w6a_fixtures.py`) and the math mini-paper's results are unchanged by every
  batch; `ve-units@1` environments keep their identities (H-7l).

## 14. Limits and trust

| Limit | Value | When exceeded |
|---|---|---|
| JSON nodes, depth, values, claims | 10,000; 64; 512; 512 | refused (`ResourceLimit`) |
| exponents (`pow`, `sci`) | 64 | refused |
| literal digits | 40 (W6's `maxNumeralChars`) | refused |
| exact value digits | 4,096 in numerator or denominator | claim unknown (`limit .digits`) |
| table bytes, rows, columns | 16 MB per handle (the service's line cap); 1,000,000; 64 | refused |
| table evaluation | 1,000,000 (row, filter node) visits, or the case's smaller `budget` | claim unknown (`limit .evaluations`) |
| derivation search | 64 facts, 16 unknowns, 10,000 combination steps | unknown (`limit .derivationSteps`) |
| consistency search | 4,096 candidate points | unknown (`limit .witnessPoints`) |
| identity normal form | 10,000 monomials | unknown (`limit .polyTerms`) |
| sign flips | 16 values | refused (`SignFlipTooLong`) |
| `arith` evaluation | 1,000,000 formula-node visits, or the case's smaller `budget` | unknown (`limit .evaluations`) |

Trusted and not certified: SHA-256 (as for the risk log); the decoders (pinned in `ve/assurance-manifest.json` by hand);
the truth of stated values and data files (a digest binds a claim to bytes, not bytes to the world); the
applicability of a physical law or a statistical model; a stated quantile; software reproduction (always unknown);
an imported proof beyond the pinned external build's acceptance. Every new trusted Lean line needs a signed allowance
and a ROADMAP trust-cost line (plan 5).

## 15. The debate edits, statement by statement

| Edit | Statements | Fixtures |
|---|---|---|
| A1 operational outcome | `Outcome`, `UnknownReason` (1.5); `Claim.run`, `run_decided`, `run_unknown`, `run_complete` (2.4); `Run.verdict_sound`, `Run.unknown_named` (3.4); `arithOutcome` and its theorems (12.2) | V-11, M-1b, M-4x |
| A2 links in counterexamples | `Counterexample.check_sound` (5) | H-6a, H-6n |
| A3 import binding | `Import`, `Import.admit_sound`, `report_import_labelled`, `checkSource`, `currentMeansDigest` (12.4) | ME-13's seeded bug (plan) |
| A4 empty aggregates | `Agg.run_empty`, `Agg.run_nonnumber` (4.2) | T-1 |
| A5 nominal legacy tags | `legacyDim`, `legacy_nominal` (6.1), 6.2 | H-7l |
| A6 "A minus B"; English eval | 11.2's grammar and `DifferenceBetween`; 11 intro | ME-11's round-trip and seeded bug (plan) |
| F1 source findings need checked spans | `findingKind`, `findingKind_source_iff` (2.5); `spanMatches_iff` (4.4) | V-12, V-13 |
| F2 merged: two rules, software reproduction unknown | `Rounding` (1.3), `rules_agree_off_tie`, `rules_differ_iff`; `Run.row`'s `reproduction` (3.4); 2.6 | V-8, V-9, V-10 |
| F3 one owner for comparison phrases | `orderPhrases`, `equalsPhrase`, `withinPhrase` (1.4) | ME-1's generated-file check (plan) |
| F4 counts through `Holds` | `Term.value`, `Holds` (12.1); `decideBounded_sound` (12.2) | M-1, M-5 |
| F5 merged: stated budget, measured bound | 12.2's fuel accounting, `maxSteps`, `decideBounded_mono`, `decideBounded_work` | M-4, M-4x, M-1b |

## 16. Choices this draft made

- **C1.** `roundsTo_unique` is stated for every rule, not only ties upward (plan 3.1 stated one rule). All four rules
  give one printed number per value and places, which the reading "one reading per rounded number" needs.
- **C2.** `Verdict`, `Limit`, `UnknownReason` and `Outcome` live in `VE.Numbers`, shared by `calc@0` and `arith@0`
  (plan 3.1 put `Verdict` in `VE.Calc`), so neither profile imports the other.
- **C3.** Comparisons carry a swap flag (`Comparison`), so the wire has `gt` and `ge` and the English keeps W6's "is
  more than" and "is at least" rows unchanged (plan 2.1 listed `eq`, `lt`, `le` only).
- **C4.** A finding's checks include the claim's literals, always unchecked, so a claim that reads a literal is never a
  source finding. The debate's F1 names stated values and printed numbers; a typed literal is the same transcription
  risk, so this draft closes it. A translator who wants a source finding states each source number as a stated value
  with a span. The statement review may relax this for constants that come from a fixed phrase ("twice").
- **C5.** `arith@0`'s meaning interprets definitions in order (`Defs.env`) instead of inlining them (plan 3.9's
  `Defs.expand`): the same meaning without substitution under binders and without an expansion that can grow
  exponentially. `Defs.Means D φ` keeps its name and role.
- **C6.** `arith`'s accounting charges formula-node visits only, as W6 does; term nodes are free, and a count is
  charged through its condition. Every loop therefore costs at least one unit per iteration.
- **C7.** The expression grammar of 11.2 puts infix phrases only at the top with an atom on the left. The plan's
  nesting rule (one phrase inside another) is kept; its own rewrite of the first refused sentence nests three phrases,
  so this draft's rewrite names the squared ratio as well.
- **C8.** Fractions in VE text are written as decimals or with "divided by" ("less than 1 divided by 4"); fraction
  words ("one fourth") are not in this plan's lexicon.
- **C9.** The source-number grammar of 4.4 refuses leading zeros ("007", "0,123") so that a span reads one way.
- **C10.** A unit with calculation content and no claim is UNFORMALISED, not CHECKED.
- **C11.** Every rounding sentence has the form "A is P when rounded …", including the printed bounds ("when rounded
  down to …"; plan 2.11 wrote "rounded down to …" without "when"), so all four rules share one frame.
