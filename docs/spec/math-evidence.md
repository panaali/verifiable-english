# Science papers in VE: `calc@0`, physical dimensions, `arith@0` and proof imports (statement specification)

## Changes in this draft

Draft 4 (2026-10-13) applies phase 1 (ME-0, [math-evidence-phase1.md](../research/math-evidence-phase1.md)) with the
plan's draft 5. It changes fixtures and prose only: **no Lean statement changes**, so the untracked stub
`lean/SpecStubs_math-evidence.lean` needs no edit for this draft (it is not tracked in this branch, and its
re-run stays the re-check's item 1).

- 13.2 and 13.3: every physics, mathematics and VE-paper fixture names its ME-0 anchor (span and outcome) instead of
  *paraphrase*.
- H-4 and H-5 (CHANGED by ME-0) read the source's v²/V² = 10⁻⁸ (spans in h049 and h113), never the unstated
  v/V = 10⁻⁴; same results (identity in D; 2/5).
- H-9 (CHANGED by ME-0) is the source's printed table: Mean rounding, Mean in w. l. = 0.02 × Mean, the repeated half
  row, Final mean; 104 claims, all hold, and a negative control. It needs `calc@0`'s core only (ME-1), not counted
  values.
- New fixtures: H-5b (the 1881 figure 0.04), V-7b (six main-text p values over 2¹²), M-4b (formula (18)'s other four
  pairs), DL-1 to DL-4 (AlphaFold, the pinned deep-learning target). H-7u is marked constructed.
- Section 10 says how pilots report CHECKED (two parts) and the premise status (UNKNOWN for H, V, DL today).
- Section 17's re-check gains item 8: the phase-1 fixtures, recomputed in the stub.
- Section 0: EX-3 is now a trigger.

> **Status.** Item-1 specification (batch ME-S), draft 4 (2026-10-13), branch `research/math-evidence-p1`; drafts 1
> to 3 on `design/math-evidence` from `main` at `49de179e`. Draft 4 applies phase 1 (list above); the rest of this
> note is draft 3's. Written from [math-evidence-PLAN.md](math-evidence-PLAN.md) draft 4 (cited `plan n`); draft 4
> follows the plan's draft 5. Draft 1 applied
> the converged Astra + Fable review of the plan (`manage-agents/debates/design-math-evidence/`, edits A1-A6 and
> F1-F5; section 15). Draft 2 applies the converged statement review of draft 1
> (`manage-agents/debates/math-evidence-spec/`, verdict FIX, CONVERGED after round 2): Fable's joint edits J1-J11 with
> Astra's refinements. Section 17 maps each of them to the statements and fixtures that carry it. No design change
> beyond those edits was made; section 16 lists the points where draft 2 had to choose a reading of an edit. Draft 3
> applies the verification of draft 2 (`manage-agents/math-evidence-p3ver1.final.md`, FAIL narrowly): J2's
> `Run.unknown_named` is the agreed disjunction again, and every kind's unknown at the digit limit has a cause (3.4);
> fixture R-10 adds the unknown and undefined rows of derivations, consistency checks and identities (J3, 13.6); and
> re-check item 7 names the draft-2 choices beyond J1-J11 that both reviewers must accept explicitly (17).
>
> **How it was checked.** Draft 1's Lean statements were type-checked with Lean v4.24.0 against `main`'s `lean/`
> tree (built modules `VE.Time.Decimal`, `VE.Time.Budget`, `VE.CertificateWire`, `VE.Route.Wire`,
> `ResponseShape.Skeleton`) in an untracked stub, `lean/SpecStubs_math-evidence.lean`, with
> `lake env lean SpecStubs_math-evidence.lean`: 0 errors, proofs `sorry`. Draft 1's fixture numbers were computed
> there with `#eval` or `decide` over core `Rat`. **Drafts 2's and 3's new and changed statements were not
> type-checked**: Lean could not be run in the sessions that wrote them, and the stub still holds draft 1's
> statements. Every fixture number that draft 2 adds or changes is marked *by hand* in 13.3, and draft 3's R-10 (13.6)
> was derived by hand from 2.7, 4.2 and T-3. Both are the first items of the bounded re-check (17). Names marked *opaque* have only a signature: the batch defines them.
>
> **What this is not.** Theorem statements and fixtures are implementation obligations, not claims of completed
> proofs or tests. No model was called. Build authorisation follows the reviewers' bounded re-check of the changed
> sections and the new fixtures against the checklist in 17; it is not a fresh full review.

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
fixtures (13.2-13.6), limits and trust (14), the plan-review map (15), the choices this specification made (16) and
the statement-review map with its re-check list (17).

One case kind per profile carries every check. A `calc@0` case asks four kinds of question, each with its own
meaning and its own row theorem (3.4): a **claim** about declared values (2.2), a **derivation** (5), a
**consistency check** of printed numbers (8.1) and an **identity** (8.2). An `arith@0` case asks for statements
(12.5).

Out of scope: approximations with error bounds (EX-2), tensor shapes (EX-3, a trigger from plan draft 5), folds and induction inside `arith@0`
(EX-4), chunked data (EX-5), the calc–attitudes bridge for hedged calculations (no plan owns it), dates before 1970
(W6's trigger ET-T3), section-scoped rounding declarations (scope's anchor reach), real numbers in `arith@0`.

## 1. Shared numbers: `VE.Numbers` (ME-1)

Math-evidence owns `VE.Numbers` (`lean/VE/Numbers/`), on core `Rat` (`import Std`). Quantities' QT-A2 proves its
integer-ratio rounding against `VE.Numbers.RoundsTo` and lands after ME-1. `VE.Calc` and `VE.Arith` import it, so
ME-12 (`VE.Arith`, which needs 1.5's `Verdict`, `UnknownReason` and `Outcome`) follows ME-1 (J6).

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

These are the full types (J3). ME-1 builds the constructors without a batch mark; ME-7 adds `stat`, `binom` and
`kappa` with their clauses below, extends every function over `Expr` in this specification (`eval`, `names`,
`subexprs`, `evalL`, `dimOf`) and re-proves ME-1's theorems for them. Until a constructor's batch lands, the decoder
refuses its wire form (`InvalidInput`). `Stat.run`, `binomialTail` and `kappa?` are section 7's definitions.

```lean
namespace VE.Calc
open VE.Numbers

/-- The statistics of a list of named values (ME-7, section 7). -/
inductive Stat where
  | mean | variance | populationVariance | signFlip
  deriving Repr, DecidableEq

inductive Expr where
  | lit (q : Rat)
  | val (name : String)
  | add (a b : Expr)
  | sub (a b : Expr)
  | mul (a b : Expr)
  | div (a b : Expr)
  | pow (a : Expr) (k : Nat)
  | stat (s : Stat) (xs : List String)   -- ME-7: a statistic of stated or counted values, in the written order
  | binom (n k : Nat) (p : Expr)         -- ME-7: P(X ≥ k) for X binomial with n trials and success probability p
  | kappa (t : List (List Nat))          -- ME-7: Cohen's kappa of a square agreement table
  deriving Repr, DecidableEq

abbrev Values := String → Option Rat

/-- The independent meaning: the value an expression denotes, when every name has a value, no divisor is 0 and every
statistic's input is in its domain (7). -/
inductive Denotes (σ : Values) : Expr → Rat → Prop
  | lit {q} : Denotes σ (.lit q) q
  | val {n q} : σ n = some q → Denotes σ (.val n) q
  | add {a b x y} : Denotes σ a x → Denotes σ b y → Denotes σ (.add a b) (x + y)
  | sub {a b x y} : Denotes σ a x → Denotes σ b y → Denotes σ (.sub a b) (x - y)
  | mul {a b x y} : Denotes σ a x → Denotes σ b y → Denotes σ (.mul a b) (x * y)
  | div {a b x y} : Denotes σ a x → Denotes σ b y → y ≠ 0 → Denotes σ (.div a b) (x / y)
  | pow {a x k} : Denotes σ a x → Denotes σ (.pow a k) (x ^ k)
  | stat {s xs vs q} : xs.mapM σ = some vs → s.run vs = some q → Denotes σ (.stat s xs) q
  | binom {n k p x} : Denotes σ p x → 0 ≤ x → x ≤ 1 → Denotes σ (.binom n k p) (binomialTail n k x)
  | kappa {t q} : kappa? t = some q → Denotes σ (.kappa t) q

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
  | .stat s xs => (xs.mapM σ).bind s.run
  | .binom n k p => (p.eval σ).bind fun x => if 0 ≤ x ∧ x ≤ 1 then some (binomialTail n k x) else none
  | .kappa t => kappa? t

theorem Expr.eval_iff (σ : Values) (e : Expr) (q : Rat) : e.eval σ = some q ↔ Denotes σ e q
theorem Denotes.unique {σ : Values} {e : Expr} {x y : Rat} (hx : Denotes σ e x) (hy : Denotes σ e y) : x = y

/-- The names an expression reads, left to right, with repetition. -/
def Expr.names : Expr → List String
  | .lit _ => []
  | .val n => [n]
  | .add a b | .sub a b | .mul a b | .div a b => a.names ++ b.names
  | .pow a _ => a.names
  | .stat _ xs => xs
  | .binom _ _ p => p.names
  | .kappa _ => []

/-- Every subexpression, the expression itself first; a statistic's inputs count as `val` subexpressions. -/
def Expr.subexprs : Expr → List Expr
  | .lit q => [.lit q]
  | .val n => [.val n]
  | .add a b => .add a b :: (a.subexprs ++ b.subexprs)
  | .sub a b => .sub a b :: (a.subexprs ++ b.subexprs)
  | .mul a b => .mul a b :: (a.subexprs ++ b.subexprs)
  | .div a b => .div a b :: (a.subexprs ++ b.subexprs)
  | .pow a k => .pow a k :: a.subexprs
  | .stat s xs => .stat s xs :: xs.map Expr.val
  | .binom n k p => .binom n k p :: p.subexprs
  | .kappa t => [.kappa t]
```

### 2.2 Claims and verdicts

A claim is decided under the declared values. Derivations, consistency checks and identities quantify over free
values or printed inputs instead; they are the other kinds of `Check` (3.4, 5, 8).

```lean
inductive Claim where
  | compare (c : Comparison) (a b : Expr)
  | within (e lo hi : Expr)
  | rounds (r : Rounding) (e : Expr) (p : Printed)
  | sqrtRounds (r : Rounding) (e : Expr) (p : Printed)   -- ME-7: the square root of e, rounded, is p
  deriving Repr, DecidableEq

def Claim.exprs : Claim → List Expr
  | .compare _ a b => [a, b]
  | .within e lo hi => [e, lo, hi]
  | .rounds _ e _ => [e]
  | .sqrtRounds _ e _ => [e]

def Claim.Holds (σ : Values) : Claim → Prop
  | .compare c a b => ∃ x y, Denotes σ a x ∧ Denotes σ b y ∧ c.Holds x y
  | .within e lo hi => ∃ x l h, Denotes σ e x ∧ Denotes σ lo l ∧ Denotes σ hi h ∧ l ≤ x ∧ x ≤ h
  | .rounds r e p => ∃ x, Denotes σ e x ∧ RoundsTo r p x
  | .sqrtRounds r e p => ∃ v, Denotes σ e v ∧ SqrtRoundsTo r p v

/-- Every expression denotes; the square root of a negative value is undefined, like a division by 0 (J5). -/
def Claim.Defined (σ : Values) : Claim → Prop
  | .sqrtRounds _ e _ => ∃ v, Denotes σ e v ∧ 0 ≤ v
  | c => ∀ e ∈ c.exprs, ∃ q, Denotes σ e q

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
  | .sqrtRounds r e p => match e.eval σ with
    | some v => if v < 0 then .undefined else if SqrtRoundsTo r p v then .holds else .fails
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

A named value has one source (plan D4). ME-1 decodes `stated`, `defined` and `free`; ME-4 fills `counted` (section
4). A counted value carries two things (J2): its mathematical value `Agg.run T f a`, held unevaluated (`Thunk`), and
the operational result of computing it within the case's budget, which is either that value or **exhausted**. The
runner reads the mathematical value only when the operational result completed, so no aggregate is computed outside
the budget; the proofs read it always.

```lean
/-- The operational result of a counted value (ME-4): its value within the budget, or the budget ran out. -/
inductive Counted where
  | ok (v : Option Rat)
  | exhausted
  deriving Repr, DecidableEq

inductive Source where
  | stated (q : Rat)
  | defined (e : Expr)
  | free
  | counted (value : Thunk (Option Rat)) (run : Counted)

structure Decl where
  name : String
  source : Source

def Decl.valueUnder (d : Decl) (σ : Values) : Option Rat :=
  match d.source with
  | .stated q => some q
  | .defined e => e.eval σ
  | .free => none
  | .counted q _ => q.get

/-- The values the declarations give, in order. -/
def values (ds : List Decl) : Values :=
  ds.foldl (fun σ d n => if n = d.name then d.valueUnder σ else σ n) (fun _ => none)

/-- Unique names; each defined value reads only earlier names; a counted value's completed result is its value. -/
def WellFormed (ds : List Decl) : Prop :=
  (ds.map Decl.name).Nodup ∧
    (∀ (i : Nat) (hi : i < ds.length) (e : Expr), (ds[i]'hi).source = .defined e →
      ∀ n ∈ e.names, n ∈ (ds.take i).map Decl.name) ∧
    ∀ d ∈ ds, ∀ q v, d.source = .counted q (.ok v) → q.get = v

theorem values_stated (ds : List Decl) (h : WellFormed ds) (d : Decl) (hd : d ∈ ds) (q : Rat)
    (hs : d.source = .stated q) : values ds d.name = some q
theorem values_defined (ds : List Decl) (h : WellFormed ds) (d : Decl) (hd : d ∈ ds) (e : Expr)
    (hs : d.source = .defined e) (q : Rat) : values ds d.name = some q ↔ Denotes (values ds) e q
theorem values_free (ds : List Decl) (h : WellFormed ds) (d : Decl) (hd : d ∈ ds)
    (hs : d.source = .free) : values ds d.name = none
theorem values_counted (ds : List Decl) (h : WellFormed ds) (d : Decl) (hd : d ∈ ds) (q : Thunk (Option Rat))
    (r : Counted) (hs : d.source = .counted q r) : values ds d.name = q.get
theorem values_missing (ds : List Decl) (n : String) (h : n ∉ ds.map Decl.name) : values ds n = none
```

### 2.4 The digit limit and the operational outcome (debate A1)

An exact value whose numerator or denominator would have more than 4,096 decimal digits is not computed. The
operational evaluator returns `ok`, `undefined`, `tooLarge` or `exhausted` (a counted value whose budget ran out,
J2); evaluation is left to right, and the first fault met decides. An exhausted counted value propagates through every
defined value that reads it, so a claim that reads it, directly or through definitions, is
`unknown (limit .evaluations)` unless an earlier fault decided it.

```lean
def maxDigits : Nat := 4096
def digitCount (n : Nat) : Nat := (Nat.toDigits 10 n).length

def Small (q : Rat) : Prop := digitCount q.num.natAbs ≤ maxDigits ∧ digitCount q.den ≤ maxDigits

inductive Val where
  | ok (q : Rat) | undefined | tooLarge | exhausted
  deriving Repr, DecidableEq

def Val.guard (q : Rat) : Val := if Small q then .ok q else .tooLarge

def Val.bin (f : Rat → Rat → Val) : Val → Val → Val
  | .ok x, .ok y => f x y
  | .ok _, v => v
  | v, _ => v

/-- The values of a list, or its first fault. -/
def Val.all : List Val → Except Val (List Rat)
  | [] => .ok []
  | .ok q :: vs => (Val.all vs).map (q :: ·)
  | v :: _ => .error v

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
  | .stat s xs => match Val.all (xs.map τ) with
    | .error v => v
    | .ok vs => match s.run vs with
      | some q => Val.guard q
      | none => .undefined
  | .binom n k p => match p.evalL τ with
    | .ok x => if 0 ≤ x ∧ x ≤ 1 then Val.guard (binomialTail n k x) else .undefined
    | v => v
  | .kappa t => match kappa? t with
    | some q => Val.guard q
    | none => .undefined

def Decl.valL (d : Decl) (τ : String → Val) : Val :=
  match d.source with
  | .stated q => Val.guard q
  | .defined e => e.evalL τ
  | .free => .undefined
  | .counted _ (.ok (some q)) => Val.guard q
  | .counted _ (.ok none) => .undefined
  | .counted _ .exhausted => .exhausted

def valuesL (ds : List Decl) : String → Val :=
  ds.foldl (fun τ d n => if n = d.name then d.valL τ else τ n) (fun _ => .undefined)

def firstFault : List Val → Option Val
  | [] => none
  | .ok _ :: vs => firstFault vs
  | v :: _ => some v

def Claim.run (ds : List Decl) (c : Claim) : Outcome :=
  match firstFault (c.exprs.map (Expr.evalL (valuesL ds))) with
  | some .tooLarge => .unknown (.limit .digits)
  | some .exhausted => .unknown (.limit .evaluations)
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

/-- A name that is a counted value whose budget ran out, or a defined value that reads one (J2). -/
inductive NameExhausted (ds : List Decl) : String → Prop
  | here {n : String} {q : Thunk (Option Rat)} :
      (∃ d ∈ ds, d.name = n ∧ d.source = .counted q .exhausted) → NameExhausted ds n
  | dep {n m : String} {e : Expr} :
      (∃ d ∈ ds, d.name = n ∧ d.source = .defined e) → m ∈ e.names → NameExhausted ds m →
      NameExhausted ds n

def Expr.ReadsExhausted (ds : List Decl) (e : Expr) : Prop := ∃ m ∈ e.names, NameExhausted ds m

def Claim.ReadsExhausted (ds : List Decl) (c : Claim) : Prop := ∃ e ∈ c.exprs, e.ReadsExhausted ds

/-- A decided outcome is the mathematical verdict. -/
theorem Claim.run_decided (ds : List Decl) (h : WellFormed ds) (c : Claim) (v : Verdict)
    (hr : c.run ds = .decided v) : v = c.decide (values ds)
/-- Unknown arises only from a named limit, and only when that limit is really met: a value on the way exceeds the
digit limit, or the claim reads a counted value whose budget ran out. -/
theorem Claim.run_unknown (ds : List Decl) (h : WellFormed ds) (c : Claim) (u : UnknownReason)
    (hr : c.run ds = .unknown u) :
    (u = .limit .digits ∧ c.Overflows ds) ∨ (u = .limit .evaluations ∧ c.ReadsExhausted ds)
theorem Claim.run_complete (ds : List Decl) (h : WellFormed ds) (c : Claim) (hc : ¬ c.Overflows ds)
    (he : ¬ c.ReadsExhausted ds) : c.run ds = .decided (c.decide (values ds))
```

`Overflows` and `ReadsExhausted` are stated over `Denotes` and the declarations, so they are independent of the
evaluator. A claim may be unknown although its meaning is undefined (a value on the way is too large, or exhausted,
before a later zero divisor or empty mean is reached); it is never decided wrongly. Fixture V-11 shows a limit hit and
a zero divisor side by side; T-3 shows an exhausted count read directly and through a definition, beside an empty
mean, in both orders.

### 2.5 Findings (debates F1 and F2)

In a translated document a claim that fails is a **finding**; nothing is repaired. So is a fails row of the other
kinds of check (3.4): a derivation that does not follow, printed numbers shown inconsistent, or an identity shown false.
Its kind:

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

### 2.7 Unknowns, printed inputs and inlining (ME-5, ME-8, ME-9; J3, J4)

Derivations and identities quantify over the **free values**; a consistency check quantifies over its **inputs**,
stated values that stand for their rounding intervals. Their meanings (5, 8.1, 8.2) give those names a value `κ n` and
keep every other declaration as it is: stated and counted values keep their values, and a defined value is evaluated
from the assigned names. The checkers work on **inlined** expressions: every name outside the quantified ones is
replaced by its stated or counted value as a literal, or by its definition, recursively. The quantified names stay as
`val` nodes: an input is never replaced by its printed value (Astra's refinement of J4). The lowering is one function,
built by whichever of ME-5, ME-8 and ME-9 lands first.

```lean
/-- The free values, in declaration order: the unknowns of derivations and identities. -/
def freeNames (ds : List Decl) : List String :=
  (ds.filter fun d => match d.source with | .free => true | _ => false).map Decl.name

/-- The declarations with each name in `ns` given the value `κ n`. -/
def assign (ds : List Decl) (ns : List String) (κ : String → Rat) : List Decl :=
  ds.map fun d => if d.name ∈ ns then { d with source := .stated (κ d.name) } else d

theorem assign_wellFormed (ds : List Decl) (h : WellFormed ds) (ns : List String) (κ : String → Rat) :
    WellFormed (assign ds ns κ)

/-- *Opaque*: inlining. `.error .undefined` when a name read outside `keep` has no value (a free value, a missing
name, a counted value that is undefined) or a statistic of known values is outside its domain; `.error .exhausted`
when it reads, directly or through definitions, a counted value whose budget ran out; `.error .tooLarge` when a
statistic it evaluates, or an input of one, is beyond the digit limit (2.4). -/
def Expr.inline (ds : List Decl) (keep : List String) (e : Expr) : Except Val Expr
/-- *Opaque*: `Expr.inline` on each expression of a claim. -/
def Claim.inline (ds : List Decl) (keep : List String) (c : Claim) : Except Val Claim

theorem Expr.inline_names (ds : List Decl) (keep : List String) (e e' : Expr) (he : e.inline ds keep = .ok e') :
    ∀ n ∈ e'.names, n ∈ keep
theorem Expr.inline_sound (ds : List Decl) (h : WellFormed ds) (keep : List String)
    (hk : ∀ n ∈ keep, n ∈ ds.map Decl.name) (e e' : Expr) (he : e.inline ds keep = .ok e') (κ : String → Rat)
    (x : Rat) : Denotes (values (assign ds keep κ)) e x ↔ Denotes (fun n => some (κ n)) e' x
theorem Expr.inline_undefined (ds : List Decl) (h : WellFormed ds) (keep : List String) (e : Expr)
    (he : e.inline ds keep = .error .undefined) : ∀ κ x, ¬ Denotes (values (assign ds keep κ)) e x
theorem Expr.inline_exhausted (ds : List Decl) (keep : List String) (e : Expr)
    (he : e.inline ds keep = .error .exhausted) : e.ReadsExhausted ds
/-- The lowering meets the digit limit only where the expression, directly or through definitions, has a part that
denotes a value beyond it (draft 3: the cause of 3.4's digit-limit unknown for derivations, consistency checks and
identities). -/
theorem Expr.inline_tooLarge (ds : List Decl) (h : WellFormed ds) (keep : List String) (e : Expr)
    (he : e.inline ds keep = .error .tooLarge) : e.Overflows ds
theorem Claim.inline_sound (ds : List Decl) (h : WellFormed ds) (keep : List String)
    (hk : ∀ n ∈ keep, n ∈ ds.map Decl.name) (c c' : Claim) (hc : c.inline ds keep = .ok c') (κ : String → Rat) :
    c.Holds (values (assign ds keep κ)) ↔ c'.Holds (fun n => some (κ n))
```

`Expr.inline` substitutes and evaluates nothing but statistics: a known zero divisor stays in the inlined expression,
where it denotes nothing on both sides of `inline_sound`. A statistic reads names, not expressions, and its names are
stated or counted values (3.1); one whose names are all in `keep` stays, and one with none in `keep` becomes the
literal of its exact value (or the fault above). The decoder refuses a statistic that mixes the two, so the case does
not arise. Another fault (`.tooLarge`) can arise only there, and the row is then `unknown (limit .digits)`, with the
cause `inline_tooLarge` names: the statistic reads no kept name, so it, or the input that is too large, denotes its
value under the declarations themselves. The checkers of 5, 8.1 and 8.2 give no digit-limit unknown of their own
(3.4's `Check.UnknownCause`).

## 3. The wire, identity and runner (ME-2)

### 3.1 The case `ve-calc@0`

| Field | Mandatory | Content |
|---|---|---|
| `format` | yes | `"ve-calc@0"` |
| `values` | yes | a list of value records (below), in order |
| `claims` | yes | a nonempty list of `{"id": <claim id>, "claim": <check>, "span": [start, stop]?}`; every entry gets one response row |
| `premises` | no (ME-5) | a list of `{"id": <claim id>, "claim": <claim>, "support": s, "span"?: [start, stop]}`: the premises derivations name; a premise gets no row of its own |
| `rounding` | no | `"ties-up"` (default) or `"half-even"`: the rule of every `rounds` and `sqrt-rounds` claim without its own, and of every consistency check's inputs |
| `software` | no | a software convention (2.6) |
| `source` | no (ME-4) | the SHA-256 handle of the pinned source bytes against which spans are checked |
| `data` | no (ME-4) | data declarations (4.1) |
| `environment` | no (ME-6) | a `ve-units@2` (or `ve-units@1`) environment (6.2) |
| `budget` | no (ME-4) | a positive integer at most 1,000,000: the evaluation budget of each counted value (4.2) |

A value record is `{"name": n, "words": w, <source>, "support"?: s, "span"?: [start, stop], "unit"?: u}` with exactly
one source: `"stated": <literal>`, `"defined": <expression>`, `"free": true` or `"counted": <counted>` (ME-4). Names
match `[a-z][a-z0-9_]*`, at most 64 bytes, unique. `words` follow W6's verbalisation rules, checked by the check W6a
already runs (`VerbalisationCollision`), plus the calc rules of 11.2 (`ValueWordsForm`, `ReservedWord`). `support` is
`observation`, `testimony` or `assumption` (W2's `support` provenance field). Claim ids match `[a-z0-9_-]{1,64}` and
are unique.

Literals: `"<decimal>"` (W6's `parseDecimal` grammar) or `["sci", "<decimal>", e]` with an integer `|e| ≤ 64`
("D times ten to the power e"). Expressions: `["lit", literal]`, `["val", name]`, `["add", a, b]`, `["sub", a, b]`,
`["mul", a, b]`, `["div", a, b]`, `["pow", a, k]` with a natural `k ≤ 64`; from ME-7, `["mean", names]`,
`["variance", names]` (divisor n − 1), `["population-variance", names]` (divisor n), `["sign-flip-p", names]` (at
most 16 names, else `SignFlipTooLong`), where `names` lists stated or counted values in order (else `InvalidInput`;
in a consistency check, either all of them are inputs or none is), `["binomial-tail", n, k, p]`
with naturals `n ≤ 1,000` and `k` and an expression `p`, and `["kappa", table]` with a square list of lists of
naturals (else `KappaTableNotSquare`). Claims: `["eq" | "lt" | "le" | "gt" | "ge", a, b]` (`gt` and `ge` are `lt` and
`le` with operands swapped, the phrases "is more than" and "is at least"), `["within", e, lo, hi]`,
`["rounds", e, printed]` or `["rounds", e, printed, "ties-up" | "half-even"]`, `["rounds-down", e, printed]`,
`["rounds-up", e, printed]`, and from ME-7 `["sqrt-rounds", e, printed]` with the same optional rule, where `printed`
is a literal read with its written places (`Printed.ofDec` or `Printed.sci`).

A **check** (the `claim` of a `claims` entry) is a claim or one of the following (J3):

- `["follows", conclusion, [premise ids], [[square, root], …]]` (ME-5): `conclusion` is an `lt`, `le`, `gt` or `ge`
  claim (else `InvalidInput`); each id names an entry of `premises` (else `UnknownPremise`); each link names two free
  values (else `UnknownLink`). Premises are `eq`, `lt`, `le`, `gt`, `ge` or `within` claims (else `InvalidInput`).
  After inlining, every premise and the conclusion must be linear in the free values (else `NonlinearPremise`, naming
  the term). Linearity is a property of the form, in which every name other than a free value is a constant, so it
  needs no value: a premise that reads an exhausted or undefined counted value is not refused, and its row is unknown
  or undefined (3.4, R-10). A premise's `support` is `observation`, `testimony` or `assumption`.
- `["consistent", [input names], [outputs]]` (ME-8): each input names a stated value (else `ConsistencyInput`), at
  most once; each output is a claim other than a check of these three kinds. The name rule of 8.1: every name an
  output reads, directly or through definitions, is an input or a value that is not free (else `ConsistencyName`).
- `["identity", a, b]` (ME-9): two expressions; the free values they read, directly or through definitions, are the
  unknowns.

Premise ids and claim ids share one namespace (`DuplicateClaimId`).

### 3.2 Limits, checked first and in this order

1. 10,000 JSON nodes; 2. JSON depth 64; 3. 512 values; 4. 512 claims; 5. `pow` exponents and `sci` exponents at most
64 in absolute value; 6. literals at most 40 digits (W6's `maxNumeralChars`); 7. names and claim ids at most 64 bytes;
8. 512 premises (ME-5); 9. `binomial-tail` trials at most 1,000 (ME-7).
The first exceeded limit refuses the case with `ResourceLimit: <limit> exceeds <n>` (an UNKNOWN to the relay). A
computed value beyond 4,096 digits is not a refusal: the claims that need it are `unknown` (2.4).

### 3.3 Identity

The case's `meaning_id` is `VE.Route.Wire.meaningId ["calc@0"] envId canonical`, where `envId` is
`VE.Route.Wire.environmentId ["calc@0"] environment'` (the case's environment normalised as below, or `{}`), and
`canonical` is the case normalised as below. Both are hashed by the frozen encoder `VE.CertificateWire.canonical`,
unchanged (J1). It reads every JSON number with `getNat?` (`lean/VE/CertificateWire.lean:125`), so a negative number
is refused with "Natural number expected", and it sorts object keys by their UTF-16 code units (line 131), so the
order of keys in a request does not matter. A **canonical decimal string** of an integer is an optional "-" and its
digits with no leading zero ("0" for zero, never "-0").

- `words` are removed.
- Every value literal, a unit factor included, is its shortest plain decimal string: "0.30" and "0.3" as values are
  one value, `["sci", "2", 7]` is `"20000000"` and `["sci", "5.89", -7]` is `"0.000000589"`. No `sci` exponent
  remains.
- Every printed number is `[digits, places]`, both as canonical decimal strings: "0.30" is `["30", "2"]`, "0.3" is
  `["3", "1"]`, and H-8's "2 times ten to the power 7" is `["2", "-7"]`.
- Every `rounds` and `sqrt-rounds` claim carries its rule; `gt`/`ge` are kept as written. Every consistency check
  lists its inputs as `[name, [digits, places]]`, each with the printed number of its stated value, and carries the
  case's rule as a fourth element, since the inputs' intervals depend on both.
- In a `ve-units@2` environment, every exponent of `base_exponents` is a canonical decimal string
  (`{"length": "1", "time": "-1"}`). A `ve-units@1` environment is hashed as written, with no normalisation, and
  W6a's identities of it are unchanged.
- Natural numbers (`pow` exponents, spans, `binomial-tail`'s n and k, kappa counts, `budget`) stay JSON numbers.

`support`, `span`, `software`, `source`, `data` and `premises` are part of the identity. A claim's id is
`VE.CertificateWire.digest "ve-calc-claim-v0.2:calc@0\n" {"meaning_id": id, "claim": canonicalClaim}`. A renamed
verbalisation keeps the identity; changing a value, a source, a support, a span, a tie rule or a printed spelling
changes it and voids every approval or citation of it. Fixtures I-1 and I-2 (13.2) are a negative printed place and a
negative unit exponent.

### 3.4 Checks, the runner and its rows

Every entry of `claims` is a `Check` (J3). Each kind has its meaning (`Claim.decide`; `Follows` in 5; `Consistent` in
8.1; `IsIdentity` in 8.2), and `Check.OutcomeMeans` says what each outcome of each kind states; for unknown, that is
`Check.UnknownCause`, the named cause of J2 (draft 3). `Check.run_sound` is the row theorem: every outcome the runner
gives means what its clause says. Each batch adds its constructor, its clauses and its case of `Check.run_sound`.

```lean
/-- Every question a `calc@0` case asks: a claim (2.2), a derivation (5), a consistency check (8.1) or an identity
(8.2). The decoder resolves premise ids to their claims and each input to its stated value's printed number. -/
inductive Check where
  | claim (c : Claim)
  | follows (P : List Claim) (links : List (String × String)) (C : Claim)              -- ME-5
  | consistent (r : Rounding) (inputs : List (String × Printed)) (outs : List Claim)    -- ME-8
  | identity (a b : Expr)                                                              -- ME-9

def Check.exprs : Check → List Expr
  | .claim c => c.exprs
  | .follows P _ C => (C :: P).flatMap Claim.exprs
  | .consistent _ _ outs => outs.flatMap Claim.exprs
  | .identity a b => [a, b]

/-- The names a check's meaning quantifies over: its inputs, or the free values. -/
def Check.keep (ds : List Decl) : Check → List String
  | .consistent _ inputs _ => inputs.map Prod.fst
  | _ => freeNames ds

/-- The reasons for unknown that each kind may give (1.5). -/
def Check.reasons : Check → List UnknownReason
  | .claim _ => [.limit .digits, .limit .evaluations]
  | .follows .. => [.limit .derivationSteps, .derivationInconclusive, .limit .digits, .limit .evaluations]
  | .consistent .. => [.limit .witnessPoints, .consistencyInconclusive, .limit .digits, .limit .evaluations]
  | .identity .. => [.limit .polyTerms, .identityNotShown, .limit .digits, .limit .evaluations]

/-- The named cause of an unknown row (J2). A claim is unknown only at the digit limit with a value on the way beyond
it, or at the budget with a read of an exhausted counted value: `Claim.run_unknown`'s disjunction. The other kinds
may also give their own reasons (1.5); at those two limits their causes are the same, in one of their expressions,
since they meet the digit limit only in the lowering (2.7, `Expr.inline_tooLarge`). -/
def Check.UnknownCause (ds : List Decl) : Check → UnknownReason → Prop
  | .claim c, u => (u = .limit .digits ∧ c.Overflows ds) ∨ (u = .limit .evaluations ∧ c.ReadsExhausted ds)
  | k, u => u ∈ k.reasons ∧ (u = .limit .digits → ∃ e ∈ k.exprs, e.Overflows ds) ∧
      (u = .limit .evaluations → ∃ e ∈ k.exprs, e.ReadsExhausted ds)

/-- What each outcome states, one clause per kind and outcome; the clauses are tried in order. -/
def Check.OutcomeMeans (ds : List Decl) : Check → Outcome → Prop
  | .claim c, .decided v => v = c.decide (values ds)
  | .follows P links C, .decided .holds => Follows ds P links C
  | .follows P links C, .decided .fails => HasCounterexample ds P links C
  | .consistent r inputs outs, .decided .holds => Consistent ds r inputs outs
  | .consistent r inputs outs, .decided .fails => ¬ Consistent ds r inputs outs
  | .identity a b, .decided .holds => IsIdentity ds a b
  | .identity a b, .decided .fails => NotIdentity ds a b
  | k, .decided .undefined => ∃ e ∈ k.exprs, ∀ κ x, ¬ Denotes (values (assign ds (k.keep ds) κ)) e x
  | k, .unknown u => k.UnknownCause ds u

/-- *Opaque* beyond claims: the runner of 5, 8.1 and 8.2. -/
def Check.run (ds : List Decl) : Check → Outcome

theorem Check.run_claim (ds : List Decl) (c : Claim) : (Check.claim c).run ds = c.run ds
/-- The row theorem (J3): every outcome means what its kind's clause says. -/
theorem Check.run_sound (ds : List Decl) (h : WellFormed ds) (k : Check) : k.OutcomeMeans ds (k.run ds)

structure Case where
  decls : List Decl
  claims : List (String × Check)
  software : Option String

structure Row where
  id : String
  outcome : Outcome
  reproduction : Option Outcome
  deriving Repr

def Run.row (c : Case) (cl : String × Check) : Row :=
  { id := cl.1, outcome := cl.2.run c.decls,
    reproduction := c.software.map fun _ => .unknown .floatingPointNotModelled }

def Run.rows (c : Case) : List Row := c.claims.map (Run.row c)

theorem Run.rows_outcome (c : Case) (i : Nat) (hi : i < c.claims.length) :
    ((Run.rows c)[i]'(by simpa [Run.rows] using hi)).outcome = (c.claims[i]'hi).2.run c.decls

/-- *Opaque*: decodes `ve-calc@0` (limits of 3.2 first, then fields, names, definition order, literals, the
admission rules of 3.1). -/
def Wire.decodeCase : Lean.Json → Except String Case
theorem Wire.decodeCase_wellFormed (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) :
    WellFormed c.decls
theorem Wire.decodeCase_keep (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) :
    ∀ k ∈ c.claims.map Prod.snd, ∀ n ∈ k.keep c.decls, n ∈ c.decls.map Decl.name

/-- *Opaque*: the service answer, and the reader of row `i`'s outcome in it. -/
def Run.runCaseReported : Lean.Json → Lean.Json
def Run.outcomeAt : Lean.Json → Nat → Option Outcome

theorem Run.outcome_sound (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) (i : Nat)
    (hi : i < c.claims.length) :
    Run.outcomeAt (Run.runCaseReported j) i = some ((c.claims[i]'hi).2.run c.decls)
/-- The row theorem on the wire, for every kind. -/
theorem Run.row_sound (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) (i : Nat)
    (hi : i < c.claims.length) (o : Outcome) (ho : Run.outcomeAt (Run.runCaseReported j) i = some o) :
    (c.claims[i]'hi).2.OutcomeMeans c.decls o
/-- Debate A1, for claims: agreement with the total decision is conditional on completion. -/
theorem Run.verdict_sound (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) (i : Nat)
    (hi : i < c.claims.length) (cl : Claim) (hk : (c.claims[i]'hi).2 = .claim cl) (v : Verdict)
    (hv : Run.outcomeAt (Run.runCaseReported j) i = some (.decided v)) :
    v = cl.decide (values c.decls)
/-- Unknown arises only from its named cause (J2). For a claim row this is the agreed disjunction: the digit limit
with a value beyond it, or the budget with a read of an exhausted counted value; for the other kinds, a reason of the
kind, with the same causes at those two limits (draft 3 restores the disjunction that draft 2 had weakened). -/
theorem Run.unknown_named (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) (i : Nat)
    (hi : i < c.claims.length) (u : UnknownReason)
    (hu : Run.outcomeAt (Run.runCaseReported j) i = some (.unknown u)) :
    (c.claims[i]'hi).2.UnknownCause c.decls u

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

A refused case answers the service's common case error (`{"status": "error", "case_index", "error"}`, with the
diagnostic of 13.1). Otherwise there is one row per `claims` entry, in order (J3). Every row carries `status`
(`"ok"`), `claim` (the request's claim id), `claim_id` (3.3), `kind` (`"claim"`, `"follows"`, `"consistent"` or
`"identity"`, the form of the request's check), `outcome` (`holds`, `fails`, `undefined`, `unknown`), `reason` (the
text of 1.5 for unknown, else `null`), `line` (Lean's English, 11.1), `finding` (`{"kind", "text"}` for a fails row
in translation, else `null`),
`reproduction` (`"unknown"` under a software convention, else `null`) and `rests_on`: each stated, counted or free
value read, as `{"name", "source", "support", "span"}` with its source kind, its support or `null`, and `"checked"` or
`"unchecked"`; for a derivation also each premise, `{"premise": id, "support": s}`, and each square link,
`{"link": [square, root], "support": "assumption"}` (J10). The fields of each kind, `null` where the outcome has none:

| Kind | Fields | Content |
|---|---|---|
| claim | `sides`, `display`, `tie` | each expression's exact value as a reduced fraction `"n/d"` (an integer as `"n"`), or `null`; 2.5's truncated decimal at the printed places; 2.2's tie flag |
| follows | `certificate` (holds), `counterexample` (fails) | the replayed steps in order, each `{"farkas": {"goal": fact, "weights": ["n/d", …]}}` or `{"square": {"square": s, "root": r, "a": "n/d", "b": "n/d"}}`, with a fact written `{"const": "n/d", "coeffs": [[name, "n/d"], …], "strict": bool}` and one weight per fact in this order: the premises' facts in premise order (an `eq` or `within` premise gives two, `a − b ≥ 0` then `b − a ≥ 0`, or `e − lo ≥ 0` then `hi − e ≥ 0`), the facts earlier steps derived, then the step's negated goal; one `[name, "n/d"]` per free value read, in declaration order |
| consistent | `witness` (holds), `refutation` (fails) | one `[input, "n/d"]` per input; `{"output": i, "enclosure": ["lo", "hi"]}` or `{"output": i, "grain": "<2^n>"}` |
| identity | `point`, `sides` (fails) | one `[name, "n/d"]` per free value read; the two sides' values there |

The relay (ME-3, and each later batch for its kind) checks schema and binding only (R8): exactly one row per request
claim, in order, `claim` equal to the request's id and `kind` to its form; every name in `rests_on` is declared in the
request, every premise id and link is the request's for that derivation; every name in a `counterexample` or `point`
is a free value of the request, every name in a `witness` an input of that check, and `refutation.output` an index of
its outputs. Anything else is `CheckerUnavailable`. The relay never re-evaluates a certificate, witness or point:
Lean's row theorem (`Run.row_sound`) carries their meaning. 13.6 gives a complete request and answer per kind.

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

There is no general negation (J9). A negated atom selects only a row whose cell has the atom's type: "that are not
approved" selects a row whose `approved` cell is the Boolean false, and a row whose cell is absent, or is text in a
`bool` column, is selected by neither "that are approved" nor "that are not approved" (Astra's refinement). Likewise
"is not" selects only text cells and "does not equal" only number cells.

```lean
inductive Filter where
  | all
  | isText (col v : String)
  | isNotText (col v : String)
  | equals (col : String) (q : Rat)
  | notEquals (col : String) (q : Rat)
  | isTrue (col : String)
  | isFalse (col : String)
  | and (f g : Filter)
  | or (f g : Filter)

/-- The meaning of a filter. -/
def Filter.Selects (T : Table) : Filter → List Cell → Prop
  | .all, _ => True
  | .isText c v, r => T.cell r c = .text v
  | .isNotText c v, r => ∃ s, T.cell r c = .text s ∧ s ≠ v
  | .equals c q, r => T.cell r c = .num q
  | .notEquals c q, r => ∃ x, T.cell r c = .num x ∧ x ≠ q
  | .isTrue c, r => T.cell r c = .bool true
  | .isFalse c, r => T.cell r c = .bool false
  | .and f g, r => f.Selects T r ∧ g.Selects T r
  | .or f g, r => f.Selects T r ∨ g.Selects T r

/-- The executable filter. -/
def Filter.sel (T : Table) : Filter → List Cell → Bool
  | .all, _ => true
  | .isText c v, r => T.cell r c == .text v
  | .isNotText c v, r => match T.cell r c with
    | .text s => s != v
    | _ => false
  | .equals c q, r => T.cell r c == .num q
  | .notEquals c q, r => match T.cell r c with
    | .num x => x != q
    | _ => false
  | .isTrue c, r => T.cell r c == .bool true
  | .isFalse c, r => T.cell r c == .bool false
  | .and f g, r => f.sel T r && g.sel T r
  | .or f g, r => f.sel T r || g.sel T r

def Table.select (T : Table) (f : Filter) : List (List Cell) := T.rows.filter (f.sel T)

theorem Table.select_iff (T : Table) (f : Filter) (row : List Cell) :
    row ∈ T.select f ↔ row ∈ T.rows ∧ f.Selects T row
theorem Table.select_sublist (T : Table) (f : Filter) : (T.select f).Sublist T.rows

/-- A Boolean atom and its negation never select one row, and neither selects a row whose cell is not a Boolean. -/
theorem Filter.bool_atoms (T : Table) (c : String) (row : List Cell) :
    ¬ ((Filter.isTrue c).Selects T row ∧ (Filter.isFalse c).Selects T row) ∧
      ((∀ b, T.cell row c ≠ .bool b) →
        ¬ (Filter.isTrue c).Selects T row ∧ ¬ (Filter.isFalse c).Selects T row)
/-- A negated text or number atom selects only a cell of its type. -/
theorem Filter.negated_typed (T : Table) (c v : String) (q : Rat) (row : List Cell) :
    ((Filter.isNotText c v).Selects T row → ∃ s, T.cell row c = .text s) ∧
      ((Filter.notEquals c q).Selects T row → ∃ x, T.cell row c = .num x)
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
  | variance (col : String) | populationVariance (col : String)   -- ME-7

def Agg.run (T : Table) (f : Filter) : Agg → Option Rat
  | .count => some ((T.select f).length : Rat)
  | .sum c => (T.numbers f c).map List.sum
  | .mean c => (T.numbers f c).bind mean?
  | .min c => (T.numbers f c).bind List.min?
  | .max c => (T.numbers f c).bind List.max?
  | .variance c => (T.numbers f c).bind sampleVariance?
  | .populationVariance c => (T.numbers f c).bind populationVariance?

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
`["is-not", column, text]`, `["equals", column, number]`, `["not-equals", column, number]`, `["true", column]`,
`["false", column]`, `["and", F, F]`, `["or", F, F]`, `["all"]` and aggregates `"count"`, `["sum", column]`,
`["mean", column]`, `["min", column]`, `["max", column]` and, from ME-7, `["variance", column]` and
`["population-variance", column]`. Each counted value is computed under the case's `budget` (default and at most
1,000,000) on its own. Its `Decl` source is `counted value run` with `value` the unevaluated `Agg.run T f a` and
`run` the operational result (J2): `.ok v` when `Agg.runB` completes with `v`, `.exhausted` when it does not. An
exhausted value makes every claim that reads it, directly or through definitions, `unknown (limit .evaluations)`
(2.4); an undefined one (an empty mean) makes it `undefined`.

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

/-- *Opaque*: the operational counted result of a declaration over the registered handles, within the budget `limit`
(J2); an error is a refusal (`UnknownHandle`, `DigestMismatch`, `TableFormat`, `UnknownColumn`). -/
def runCounted (limit : Nat) (handles : List (String × ByteArray)) (dd : DataDecl) (f : Filter) (a : Agg) :
    Except String Counted

/-- A counted value is computed only from bytes whose SHA-256 is the declared handle, and a completed result is the
aggregate's value, undefined included. -/
theorem counted_bound (limit : Nat) (handles : List (String × ByteArray)) (dd : DataDecl) (f : Filter) (a : Agg)
    (v : Option Rat) (h : runCounted limit handles dd f a = .ok (.ok v)) :
    ∃ bytes T, handles.lookup dd.handle = some bytes ∧ VE.CertificateWire.sha256 bytes = dd.handle ∧
      decodeTable dd.format dd.columns bytes = .ok T ∧ Agg.run T f a = v
/-- Exhaustion is reported only when the budgeted aggregate really did not complete. -/
theorem counted_exhausted (limit : Nat) (handles : List (String × ByteArray)) (dd : DataDecl) (f : Filter) (a : Agg)
    (h : runCounted limit handles dd f a = .ok .exhausted) :
    ∃ bytes T, handles.lookup dd.handle = some bytes ∧ VE.CertificateWire.sha256 bytes = dd.handle ∧
      decodeTable dd.format dd.columns bytes = .ok T ∧ Agg.runB limit T f a = none
```

SHA-256 is trusted code without a refinement theorem, as for the risk log (plan 3.3).

### 4.4 Source spans (debate F1)

The pinned source of a translated document is registered as a data handle (`"source"`). A `span` is a half-open byte
range `[start, stop)` of those bytes. Lean reads the bytes as UTF-8 and reads the text as a number the way a source
prints numbers: an optional minus, a whole part (the single digit "0", or digits not starting with 0, or comma groups
of three after a first group of one to three digits not starting with 0), an optional point followed by digits; the
whole part may be empty before a point (".296"); at least one digit. So "0" and "0.30" read, and "007" and "0,123"
do not (J11). The written places are kept. A span whose text reads as the stated
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

A derivation is the check `["follows", conclusion, [premise ids], [[square, root], …]]` (3.1) over `free` values; its
premises are entries of the case's `premises`, each with its support. Lean inlines the stated, defined and counted
values (2.7), linearises each premise and the conclusion (a claim that is not linear in the unknowns is refused with
`NonlinearPremise`, naming the term), turns an equality or a range into two facts, searches Farkas multipliers by
Fourier-Motzkin elimination within 64 facts, 16 unknowns and 10,000 combination steps, and replays what it finds.
Outcomes: **follows** (a replayed certificate; outcome `holds`), **does not follow** (a counterexample checked by
evaluation, square links included; outcome `fails`), **undefined** (a premise or the conclusion reads a value that has
none, 3.4), or **unknown** (`limit .derivationSteps`, or `derivationInconclusive` when a needed step is outside the
square rule). The search tries the claimed bound itself as a counterexample candidate first. Physical laws enter as
premises with `support: assumption`.

A square link `(s, r)` is two assumptions, the square equation s = r · r and the root's nonnegativity 0 ≤ r, and the
reader sees both (J10, with Astra's refinement): the rendering lists them as numbered premises after the `premises`,
"S equals the square of R." and "R is at least 0.", each with `support: assumption`, and `rests_on` lists the link as
an assumption line. The wire keeps the two apart: a link is never an entry of `premises`, and a `premises` claim that
reads "S equals the square of R" is nonlinear and refused (`NonlinearPremise`). Reading English back (ME-11), the pair
of consecutive premises "S equals the square of R." and "R is at least 0.", for free values S and R, is the link
`(S, R)`; any other nonlinear premise is refused.

```lean
/-- The meaning of a derivation: wherever the free values satisfy every square link and every premise, the conclusion
holds. Stated, defined and counted values keep their meaning; a defined value is evaluated from the free values. -/
def Follows (ds : List Decl) (P : List Claim) (links : List (String × String)) (C : Claim) : Prop :=
  ∀ κ : String → Rat, (∀ l ∈ links, κ l.1 = κ l.2 * κ l.2 ∧ 0 ≤ κ l.2) →
    (∀ p ∈ P, p.Holds (values (assign ds (freeNames ds) κ))) → C.Holds (values (assign ds (freeNames ds) κ))

/-- What a "does not follow" row states: values of the free values meeting every link and premise, where the
conclusion does not hold. -/
def HasCounterexample (ds : List Decl) (P : List Claim) (links : List (String × String)) (C : Claim) : Prop :=
  ∃ κ : String → Rat, (∀ l ∈ links, κ l.1 = κ l.2 * κ l.2 ∧ 0 ≤ κ l.2) ∧
    (∀ p ∈ P, p.Holds (values (assign ds (freeNames ds) κ))) ∧ ¬ C.Holds (values (assign ds (freeNames ds) κ))

theorem not_follows_of_counterexample (ds : List Decl) (P : List Claim) (links : List (String × String)) (C : Claim)
    (h : HasCounterexample ds P links C) : ¬ Follows ds P links C
```

The checkers work on facts over the free values; the lowering and its two bridge theorems follow them.

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

/-- *Opaque*: the lowering of a premise or conclusion to facts over the free values (J3): inline (2.7), linearise;
`eq` and `within` give two facts, `lt`, `le`, `gt` and `ge` one; none when the claim is not linear in the free values
or reads a value that has none. -/
def Claim.facts (ds : List Decl) (c : Claim) : Option (List QFact)

theorem Claim.facts_sound (ds : List Decl) (h : WellFormed ds) (c : Claim) (fs : List QFact)
    (hf : c.facts ds = some fs) (κ : String → Rat) :
    (∀ f ∈ fs, f.Holds κ) ↔ c.Holds (values (assign ds (freeNames ds) κ))

/-- A replayed certificate over the lowered facts proves the derivation's meaning. -/
theorem follows_of_check (ds : List Decl) (h : WellFormed ds) (P : List Claim) (links : List (String × String))
    (C : Claim) (fss : List (List QFact)) (g : QFact) (d : Derivation) (hP : P.mapM (Claim.facts ds) = some fss)
    (hC : C.facts ds = some [g]) (hd : d.check fss.flatten links g = true) : Follows ds P links C
/-- A counterexample checked over the lowered facts is a counterexample of the derivation. -/
theorem counterexample_of_check (ds : List Decl) (h : WellFormed ds) (P : List Claim)
    (links : List (String × String)) (C : Claim) (fss : List (List QFact)) (g : QFact) (κ : String → Rat)
    (hP : P.mapM (Claim.facts ds) = some fss) (hC : C.facts ds = some [g])
    (hκ : counterexampleCheck fss.flatten links g κ = true) : HasCounterexample ds P links C
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

/-- The one physical dimension of a list of named values, if they share one (ME-7). -/
def commonDim (Γ : String → Option PhysDim) : List String → Option PhysDim
  | [] => some PhysDim.one
  | x :: xs => do
      let d ← Γ x
      let ds ← xs.mapM Γ
      if ds.all (· = d) then some d else none

/-- Literals are dimensionless; sums and differences need equal dimensions (`none` is `DimensionMismatch`). A mean
has its values' dimension, a variance its square; sign-flip p values, binomial tails (of a dimensionless p) and kappa
are dimensionless (ME-7). -/
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
  | .stat .mean xs => commonDim Γ xs
  | .stat .variance xs | .stat .populationVariance xs => (commonDim Γ xs).map (·.npow 2)
  | .stat .signFlip xs => (commonDim Γ xs).map fun _ => PhysDim.one
  | .binom _ _ p => match p.dimOf Γ with
    | some d => if d = PhysDim.one then some PhysDim.one else none
    | none => none
  | .kappa _ => some PhysDim.one

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

/-- The shortest list each statistic of 2.1 is defined on (J5). -/
def Stat.minLength : Stat → Nat
  | .variance => 2
  | _ => 1

def Stat.run : Stat → List Rat → Option Rat
  | .mean, xs => mean? xs
  | .variance, xs => sampleVariance? xs
  | .populationVariance, xs => populationVariance? xs
  | .signFlip, xs => if xs = [] then none else some (signFlipP xs)

theorem Stat.run_isSome (s : Stat) (xs : List Rat) : (s.run xs).isSome = true ↔ s.minLength ≤ xs.length

/-- On its domain a binomial tail is a probability. -/
theorem binomialTail_unit (n k : Nat) (p : Rat) (h0 : 0 ≤ p) (h1 : p ≤ 1) :
    0 ≤ binomialTail n k p ∧ binomialTail n k p ≤ 1
```

**Domains (J5).** A statistic outside its domain is **undefined**, like a division by 0, and is never refused, so a
table column and a list of names behave alike. The mean and the population variance need at least one value, the
sample variance two, and the sign-flip p one. A binomial tail denotes only when 0 ≤ p ≤ 1 (`Denotes.binom`), kappa
only when the table's total is positive and chance agreement is not 1, and a square root only of a value at least 0
(`Claim.Defined`, 2.2). The domain lives in `Denotes`, not in the functions: unguarded, `binomialTail 1 1 2` is 2 and
`signFlipP []` is 1. Two forms are refused at decode, since the limit is known there: a sign flip over more than 16
names (`SignFlipTooLong`) and a binomial tail over more than 1,000 trials (`ResourceLimit`, 3.2).

Wire forms (2.1, 3.1): over a list of value names, `["mean", names]`, `["variance", names]` (divisor n − 1),
`["population-variance", names]` (divisor n) and `["sign-flip-p", names]`; over a table column, the counted
aggregates `["mean", column]`, `["variance", column]` and `["population-variance", column]` (4.2); and
`["binomial-tail", n, k, p]`, `["kappa", table]` (square, else `KappaTableNotSquare`) and the claim
`["sqrt-rounds", e, printed]` (with an optional tie rule as for `rounds`). Each procedure adds its assumption as a
residual line: sign flips, "the differences are independent and their signs exchangeable under the null"; binomial,
"the trials are independent with one success probability"; a stated quantile such as t = 2.593, "the stated quantile
is the 97.5% point of Student's t with 11 degrees of freedom" (`support: testimony`, with its source).

## 8. Consistency of printed numbers (ME-8) and algebraic identities (ME-9)

### 8.1 Consistency

`["consistent", inputs, outputs]` (3.1): each input is a stated value and stands for every exact value that rounds to
its printed spelling under the case's rule; the outputs are claims. **One proposition**, `Consistent`, is the meaning
(J4): some exact inputs inside their intervals make every output hold, every other declaration keeping its meaning
(2.7). **One name rule** decides what an output may read: an input, or a value that is not free; the decoder refuses a
free value (`ConsistencyName`). So an output that reads a stated value omitted from the inputs reads that value's exact
stated value, in the witness and in the enclosure alike (fixture C-1). Both checkers work on the outputs inlined with
the inputs kept (2.7), so no input is replaced by its printed value.

A **witness** (a value for each input, inside its interval, under which every output holds) proves *consistent*
(outcome `holds`); an **enclosure** (exact interval evaluation over the input intervals) that misses an output, or a
granularity refutation, proves *inconsistent* (outcome `fails`); an output that reads a value that has none is
`undefined`; otherwise unknown (`consistencyInconclusive`, or `limit .witnessPoints` after 4,096 candidate points).
Lean tries as witnesses the printed values themselves and then the interval endpoints.

```lean
/-- Every input's value rounds to its printed number. -/
def InBox (r : Rounding) (inputs : List (String × Printed)) (κ : String → Rat) : Prop :=
  ∀ i ∈ inputs, RoundsTo r i.2 (κ i.1)

/-- The meaning of a consistency check (J4). -/
def Consistent (ds : List Decl) (r : Rounding) (inputs : List (String × Printed)) (outs : List Claim) : Prop :=
  ∃ κ : String → Rat, InBox r inputs κ ∧ ∀ c ∈ outs, c.Holds (values (assign ds (inputs.map Prod.fst) κ))

/-- A witness for inlined outputs: a value for every input, inside its interval, under which every output holds. -/
def witnessCheck (r : Rounding) (inputs : List (String × Printed)) (outs : List Claim)
    (w : List (String × Rat)) : Bool :=
  inputs.all (fun i => match w.lookup i.1 with
    | some x => decide (RoundsTo r i.2 x)
    | none => false) &&
  outs.all fun c => c.decide (fun n => w.lookup n) == .holds

/-- *Opaque*: exact interval evaluation of an inlined expression over the input intervals; none when it reads a name
that is not an input or divides by an interval that contains 0. -/
def enclose (r : Rounding) (inputs : List (String × Printed)) (e : Expr) : Option (Rat × Rat)
/-- *Opaque*: an inlined output whose enclosures show it false at every point of the input intervals. -/
def refuteByEnclosure (r : Rounding) (inputs : List (String × Printed)) (c : Claim) : Bool
/-- *Opaque*: an inlined output `rounds r' (.stat .signFlip xs) p` with `grainRefutes (2 ^ xs.length) r' p` (below). -/
def refuteByGrain (c : Claim) : Bool

theorem enclose_sound (r : Rounding) (inputs : List (String × Printed)) (e : Expr) (lo hi : Rat)
    (h : enclose r inputs e = some (lo, hi)) (κ : String → Rat) (hκ : InBox r inputs κ) (x : Rat)
    (hx : Denotes (fun n => some (κ n)) e x) : lo ≤ x ∧ x ≤ hi
theorem refuteByEnclosure_sound (r : Rounding) (inputs : List (String × Printed)) (c : Claim)
    (h : refuteByEnclosure r inputs c = true) (κ : String → Rat) (hκ : InBox r inputs κ) :
    ¬ c.Holds (fun n => some (κ n))
theorem refuteByGrain_sound (c : Claim) (h : refuteByGrain c = true) (σ : Values) : ¬ c.Holds σ

/-- The witness establishes, and the enclosure and the granularity refute, the one proposition, over one lowering. -/
theorem consistent_of_witness (ds : List Decl) (h : WellFormed ds) (r : Rounding)
    (inputs : List (String × Printed)) (hk : ∀ i ∈ inputs, i.1 ∈ ds.map Decl.name) (outs outs' : List Claim)
    (hl : outs.mapM (Claim.inline ds (inputs.map Prod.fst)) = .ok outs') (w : List (String × Rat))
    (hw : witnessCheck r inputs outs' w = true) : Consistent ds r inputs outs
theorem inconsistent_of_refutation (ds : List Decl) (h : WellFormed ds) (r : Rounding)
    (inputs : List (String × Printed)) (hk : ∀ i ∈ inputs, i.1 ∈ ds.map Decl.name) (outs outs' : List Claim)
    (hl : outs.mapM (Claim.inline ds (inputs.map Prod.fst)) = .ok outs') (c : Claim) (hc : c ∈ outs')
    (hr : refuteByEnclosure r inputs c = true ∨ refuteByGrain c = true) : ¬ Consistent ds r inputs outs

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

On the route the granularity refutation is the sign-flip one (`refuteByGrain`; plan 2.9). `mean_grain_refutes`
(GRIM) is a library theorem with fixture S-3: a consistency check has no inputs that range over whole numbers, so it
has no route form in this plan (16, C17).

### 8.2 Identities

`["identity", a, b]` over free values: Lean inlines both sides with the free values kept (2.7, J3), so a named value
such as "the round-trip time" is replaced by its definition; then it normalises both sides to polynomials over ℚ
(sorted monomials, merged coefficients, zeros dropped) or, with division, to numerator and denominator, compares
cross-multiplied normal forms and reports **identity** (outcome `holds`), or **not an identity** with a rational point
where both sides denote and differ (found by trying small values; outcome `fails`), or `undefined` (a side reads a
value that has none), or unknown (`identityNotShown`; `limit .polyTerms` above 10,000 monomials). The checkers below
are stated over inlined expressions, whose names are all free.

```lean
/-- The meaning of an identity: the two sides are equal wherever both denote, for every value of the free values. -/
def IsIdentity (ds : List Decl) (a b : Expr) : Prop :=
  ∀ κ x y, Denotes (values (assign ds (freeNames ds) κ)) a x → Denotes (values (assign ds (freeNames ds) κ)) b y →
    x = y

/-- What a "not an identity" row states. -/
def NotIdentity (ds : List Decl) (a b : Expr) : Prop :=
  ∃ κ x y, Denotes (values (assign ds (freeNames ds) κ)) a x ∧ Denotes (values (assign ds (freeNames ds) κ)) b y ∧
    x ≠ y

theorem not_isIdentity (ds : List Decl) (a b : Expr) (h : NotIdentity ds a b) : ¬ IsIdentity ds a b
```

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

/-- Over the inlined sides, the normaliser proves the identity and a differing point refutes it (J3). -/
theorem isIdentity_of_check (ds : List Decl) (h : WellFormed ds) (a b a' b' : Expr)
    (ha : a.inline ds (freeNames ds) = .ok a') (hb : b.inline ds (freeNames ds) = .ok b')
    (hc : identityCheck a' b' = true) : IsIdentity ds a b
theorem notIdentity_of_differsAt (ds : List Decl) (h : WellFormed ds) (a b a' b' : Expr)
    (ha : a.inline ds (freeNames ds) = .ok a') (hb : b.inline ds (freeNames ds) = .ok b')
    (κ : List (String × Rat)) (hd : differsAt a' b' κ = true) : NotIdentity ds a b

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
/-- *Opaque*: the English of a check (11.1): a claim's line; a derivation's numbered premises, its square links as two
premises each (J10), and its conclusion; a consistency check's inputs and outputs; an identity's sentence. -/
def renderCheck (words : String → Option String) (k : Check) : Option String
/-- *Opaque*: the check an English passage reads as (ME-11). -/
def readCheck (words : String → Option String) (s : String) : Except String Check
theorem read_renderCheck (words : String → Option String) (k : Check) (s : String)
    (h : renderCheck words k = some s) : readCheck words s = .ok k
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
  | some k => k.run c.decls == .decided .holds
  | none => false

theorem calcLeaf_discharged_iff (c : Case) (claimId : String) :
    calcLeafDischarged c claimId = true ↔
      ∃ k, c.claims.lookup claimId = some k ∧ k.run c.decls = .decided .holds
/-- A discharged leaf states its check's meaning: a claim holds, a derivation follows, printed numbers are
consistent, an identity holds (3.4). -/
theorem calcLeaf_holds (c : Case) (h : WellFormed c.decls) (claimId : String)
    (hd : calcLeafDischarged c claimId = true) :
    ∃ k, c.claims.lookup claimId = some k ∧ k.OutcomeMeans c.decls (.decided .holds)
theorem calcLeaf_claim_holds (c : Case) (h : WellFormed c.decls) (claimId : String) (cl : Claim)
    (hk : c.claims.lookup claimId = some (.claim cl)) (hd : calcLeafDischarged c claimId = true) :
    cl.Holds (values c.decls)

end VE.Calc
```

Pilot reports (plan 7, draft 4 of this spec) split CHECKED bytes into **stated only** (Lean admitted the value; no
relation over it was decided) and **in a certified relation** (the unit is a premise or the consequence of a relation
Lean replayed, or of a claim Lean decided), and give the document's premise status beside them, three-valued: a
checked model, a contradiction, or UNKNOWN within budget. CHECKED never asserts that the premises are consistent; ME-0
found them UNKNOWN for the H, V and DL documents. Both are reporting rules over Lean's answers, not new statements:
`unitStatus` is unchanged.

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

The places phrase must name the places of the printed spelling (J8): "0.3 when rounded to two decimal places" could
mean (3, 1) or (30, 2), so it is refused (`PlacesMismatch`, naming both) with the rewrites "0.30 when rounded to two
decimal places" and "0.3 when rounded to one decimal place". A printed number with negative places is written "D times
ten to the power e"; "20000000 when rounded to a multiple of ten to the power 7" is refused the same way, since
"20000000" is written to a whole number, and "2 times ten to the power 7 when rounded to a multiple of ten to the power
7" is (2, −7).

"Is" followed by a numeral (with its unit, if any) declares a stated value, and "is" followed by a comparison phrase
or by a numeral and "when rounded" makes a claim. "A is E" with any other E is refused (`IsExpression`, J7) with both
rewrites: "Let A be E." declares a defined value, and "A equals E." claims an equality. Premises use "equals".

| Form | Wording | Meaning |
|---|---|---|
| stated | "The number of weakening attacks is 243." | `stated 243` |
| stated with unit (ME-6) | "The path length is 11 meters." | `stated` 11 × meter |
| defined | "Let the false-approval rate in strict VE be the number of weakening attacks approved in strict VE divided by the number of weakening attacks." | `defined` (`div`) |
| free (ME-5) | "Let the velocity ratio be an unknown number." | `free` |
| counted (ME-4) | "Let the approved 32B trials be the number of rows of the trial table whose judge is 32B and that are approved." | `counted` with `and (isText judge "32B") (isTrue approved)`, `count`; "whose <column> is <text>", "whose <column> equals <number>", "that are <column>", their negations "whose <column> is not <text>" (`isNotText`), "whose <column> does not equal <number>" (`notEquals`) and "that are not <column>" (`isFalse`), each selecting only a cell of its type, so a row whose cell is absent or mistyped is selected by neither an atom nor its negation (J9); a list joined by "and", and "either … or …" at the top only |
| equals | "A equals B." | `compare ⟨eq, false⟩` |
| order | "A is less than B." / "A is at most B." / "A is more than B." / "A is at least B." | `compare` with the four rows of `orderPhrases` |
| range | "A is from L through H." | `within` (both ends included) |
| rounding, default rule | "The false-approval rate is 0.296 when rounded to three decimal places, with exact ties going up." | `rounds tiesUp` |
| rounding, half to even | "The p value is 0.007812 when rounded to six decimal places, with exact ties going to the even digit." | `rounds halfEven` |
| printed bounds | "The lower bound is 0.019 when rounded down to three decimal places." / "… when rounded up to …" | `rounds down` / `rounds up` |
| square root (ME-7) | "The standard deviation of the twelve differences, with divisor eleven, is 0.108 when rounded to three decimal places, with exact ties going up." | `sqrt-rounds` of the sample variance |
| derivation (ME-5) | "Assume the following. 1. The displacement equals the product of 0.4 and the squared velocity ratio. 2. The displacement is less than 0.02. 3. The squared velocity ratio equals the square of the velocity ratio. 4. The velocity ratio is at least 0. From these, it follows that the velocity ratio is less than 1 divided by 4." | premises 1 and 2 (`support: assumption`); premises 3 and 4 are the link (squared ratio, ratio), each `support: assumption` (J10); conclusion |
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
- Every rewrite that names a value uses "Let … be …", and the rewritten claim uses "equals" (J7): "A is E" with an
  expression E is not a sentence (11.1, `IsExpression`).
- Value words begin with "the", contain none of "and", "minus", "divided by", "to the power", "times ten to the
  power", "is", "be", "equals", "when rounded", "through", and do not begin with a phrase word ("the sum of", "the
  product of", "the square of", "the cube of", "twice", "half of"): `ValueWordsForm`, `ReservedWord`.
- Numerals are decimal digits ("0.25", "243"); symbols (`+`, `−`, `×`, `/`, `^`, `=`, `≈`, `<`, `≤`) are refused in VE
  text (`SymbolInText`). The formula view (`2D v²/V²`) is a display generated from the meaning and never parsed.

With these rules a term is prefix notation with "and" separators, and an expression has at most one infix operator at
its top, so every accepted expression has one parse; ME-11 proves it as an instance of the engine's uniqueness.

| Refused sentence | Why | Rewrite |
|---|---|---|
| "The expected displacement is twice the path length divided by the wavelength, times the square of the speed ratio." | two parses; "times" is not a phrase | "Let the path in wavelengths be the path length divided by the wavelength. Let the squared ratio be the square of the speed ratio. Let the expected displacement be twice the product of the path in wavelengths and the squared ratio." |
| "The round-trip time is the sum of the path length divided by the speed of light minus the speed and the path length divided by the sum of the speed of light and the speed." | "minus" inside "divided by", and "and" at two levels | "Let the closing speed be the speed of light minus the speed. Let the outward time be the path length divided by the closing speed. Let the return time be the path length divided by the sum of the speed of light and the speed. Let the round-trip time be the sum of the outward time and the return time." |
| "The round-trip time is the sum of the outward time and the return time." | "A is E" with an expression E: a definition or a claim (J7) | "Let the round-trip time be the sum of the outward time and the return time." or "The round-trip time equals the sum of the outward time and the return time." |
| "The rate is 0.3 when rounded to two decimal places, with exact ties going up." | the places phrase names two places, the spelling one (J8) | "The rate is 0.30 when rounded to two decimal places, with exact ties going up." or "The rate is 0.3 when rounded to one decimal place, with exact ties going up." |
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
the definitions and the formula (12.5). -/
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

end VE.Arith
```

Draft 1's `Report` and `Report.Accepted` described only rows that hold, so they were not a response contract (J3,
Astra). 12.5 replaces them with the case's rows, which hold, fail or are unknown; its `Case.import_row` keeps
debate A3's binding: a holds row on an unbounded statement rests on an import admitted for that statement, whose
label is among the row's residual lines. Each imported conclusion needs an import admitted for its own statement. The external kernel checks the generated
`check` theorem, so the declaration's type is exactly `Defs.Means D φ` at the VE revision whose meaning sources have
`meansDigest`; VE checks the record, not the proof, and admission stays conditional on that external build. The
residual line reads "Proved in Lean with Mathlib at revision <rev>, declaration <name>; VE did not replay this proof."
The Mathlib side of EX-1 (from the plan; `Nat.bertrand` is from memory, since no Mathlib was available to ME-S):

```lean
import Mathlib.NumberTheory.Bertrand
import VE.Arith.Examples

/-- The one bridge lemma for this vocabulary, declared before its use (J11): VE's prime is Mathlib's. -/
theorem VEImports.isPrime_iff_nat_prime (p : Nat) : VE.Arith.Examples.IsPrime p ↔ Nat.Prime p

theorem VEImports.bertrand_holds : VE.Arith.Examples.primeDefs.Means VE.Arith.Examples.bertrand := by
  rw [VE.Arith.Examples.bertrand_means_iff]
  intro n hn
  obtain ⟨p, hp, h1, h2⟩ := Nat.bertrand n (by omega)
  exact ⟨p, (VEImports.isPrime_iff_nat_prime p).mpr hp, h1, h2⟩
```

### 12.5 The `arith@0` wire, identity, runner and rows (ME-12, ME-13; J3)

This section does for `arith@0` what 3.1 to 3.4 do for `calc@0` (Fable's E6).

**The case `ve-arith@0`.**

| Field | Mandatory | Content |
|---|---|---|
| `format` | yes | `"ve-arith@0"` |
| `definitions` | yes (may be empty) | a list of definitions, in order |
| `statements` | yes | a nonempty list of `{"id": <statement id>, "formula": <formula>}`; every statement gets one row |
| `budget` | no | a positive integer at most 1,000,000 (`maxSteps`, the default): the formula-node visits of each statement (12.2) |
| `imports` | no (ME-13) | a list of `{"statement": <statement id>, "record": <import record>}`, the record with the fields of `Import` (12.4) in snake case (`statement_id`, `means_digest`, `project`, `project_rev`, `toolchain`, `mathlib_rev`, `declaration`, `check_digest`, `axioms`) |

A definition is `{"name": f, "kind": "function" | "predicate", "params": [x, …], "words": w, "body": b}`: `b` is a
term for a function and a formula for a predicate, and `words` is its English ("is prime", "the prime count of").
Definition and variable names match `[a-z][a-z0-9_]*`, statement ids `[a-z0-9_-]{1,64}`, all at most 64 bytes.
Terms: `["var", x]`, `["num", "<integer>"]` (a canonical decimal string, 3.3), `["add", a, b]`, `["sub", a, b]`,
`["mul", a, b]`, `["call", f, [args]]`, `["count", x, lo, hi, φ]` (the number of x from lo through hi such that φ).
Formulas: `["eq" | "lt" | "le" | "dvd", a, b]`, `["call", p, [args]]`, `["not", φ]`, `["and" | "or" | "imp", φ, ψ]`,
`["all-nat" | "ex-nat" | "all-int" | "ex-int", x, φ]`, `["all-from-to" | "ex-from-to", x, lo, hi, φ]`.

A variable names the innermost enclosing binder of that name, else the definition's parameter of that name; the
decoder turns it into 12.1's de Bruijn index (a body's parameters are `var 0 … var (arity − 1)` in order, and each
binder pushes one value). A binder's `lo` and `hi` are outside its own scope.

Limits, checked first and in this order (`ResourceLimit`): 10,000 JSON nodes; JSON depth 64; 512 definitions; 512
statements; numerals at most 40 digits; names and ids at most 64 bytes. Then the refusals, in this order:
`InvalidInput` (a field or form, including an empty `statements`); `DuplicateName` (two definitions, or two parameters
of one definition); `DuplicateClaimId` (two statements); `UnscopedVariable` (a variable that no binder or parameter
names); `ShadowedVariable` (a binder or parameter that reuses a name in scope, so that the rendered English of 11.3
has one reading); `UnknownDefinition` (a call that names no function, or no predicate, of that name);
`RecursiveDefinition` (a call of itself or of a later definition); `ArityMismatch`; `UnboundedCount`; and from ME-13
`ImportStatement`, `ImportMeansDigest`, `ImportCheckDigest`, `ImportAxiom`. A decoded case satisfies
`Defs.WellFormed` and `Formula.Scoped D 0` for every statement, and every import is admitted.

**Identity.** `canonical` is the case with `words`, parameter names and variable names removed: each variable is
`["var", i]` with its de Bruijn index (a JSON natural), each binder loses its name (`["all-from-to", lo, hi, φ]`,
`["count", lo, hi, φ]`), each definition keeps `name` and `kind` and gives `"arity": k`, and numerals stay canonical
decimal strings, so a negative numeral is hashable by the frozen encoder (J1). Renaming a variable keeps every
identity. The case's `meaning_id` is `VE.Route.Wire.meaningId ["arith@0"] envId canonical` with
`envId = VE.Route.Wire.environmentId ["arith@0"] {}`, and `statementIdOf D φ` is `meaningId ["arith@0"] envId` of
`{"definitions": <canonical definitions>, "formula": <canonical φ>}`: it depends on the definitions and the formula,
not on the budget, the other statements or the imports.

```lean
namespace VE.Arith

structure Case where
  defs : Defs
  statements : List (String × Formula)
  budget : Nat
  imports : List (String × Import)   -- ME-13: statement id ↦ its import record

/-- A statement's outcome: a bounded statement by evaluation within the budget (12.2); an unbounded one holds only on
an import admitted for it (ME-13), and is otherwise stated, not decided. -/
def Case.outcome (c : Case) (s : String × Formula) : Outcome :=
  if s.2.Bounded c.defs then arithOutcome c.defs c.budget s.2
  else match c.imports.lookup s.1 with
    | some i => match i.admit c.defs s.2 with
      | .ok () => .decided .holds
      | .error _ => .unknown .unboundedStatement
    | none => .unknown .unboundedStatement

/-- *Opaque*: the first decisive value of a statement's outermost bounded quantifier, in 12.2's evaluation order: for
`allFromTo`, the first value where its body fails; for `exFromTo`, the first where it holds; none otherwise. -/
def decidingValue (D : Defs) (limit : Nat) (φ : Formula) : Option Int

/-- *Opaque*: decodes `ve-arith@0` (limits first, then fields, names, scoping and the refusals above). -/
def Wire.decodeCase : Lean.Json → Except String Case
theorem Wire.decodeCase_admitted (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) :
    c.defs.WellFormed = true ∧ (∀ s ∈ c.statements, s.2.Scoped c.defs 0 = true) ∧ c.budget ≤ maxSteps ∧
      ∀ s ∈ c.statements, ∀ i, c.imports.lookup s.1 = some i → i.admit c.defs s.2 = .ok ()

/-- Each outcome of a statement means what it says. -/
theorem Case.outcome_bounded (c : Case) (hD : c.defs.WellFormed = true) (s : String × Formula)
    (hs : s.2.Scoped c.defs 0 = true) (hb : s.2.Bounded c.defs = true) (v : Verdict)
    (h : c.outcome s = .decided v) : v ≠ .undefined ∧ (v = .holds ↔ c.defs.Means s.2)
theorem Case.outcome_never_undefined (c : Case) (s : String × Formula) : c.outcome s ≠ .decided .undefined
theorem Case.outcome_unknown (c : Case) (s : String × Formula) (u : UnknownReason) (h : c.outcome s = .unknown u) :
    (u = .unboundedStatement ∧ s.2.Bounded c.defs = false) ∨
      (u = .limit .evaluations ∧ s.2.Bounded c.defs = true ∧ decideBounded c.defs c.budget s.2 = none)
/-- Debate A3, on the rows: a holds row on an unbounded statement rests on an import admitted for that very
statement. -/
theorem Case.import_row (c : Case) (s : String × Formula) (hb : s.2.Bounded c.defs = false)
    (h : c.outcome s = .decided .holds) :
    ∃ i, c.imports.lookup s.1 = some i ∧ i.statementId = statementIdOf c.defs s.2 ∧
      i.meansDigest = currentMeansDigest ∧ (∀ a ∈ i.axioms, a ∈ allowedAxioms)

/-- The deciding value of a failed universal is its first counterexample… -/
theorem decidingValue_all (D : Defs) (hD : D.WellFormed = true) (lo hi : Term) (ψ : Formula)
    (hφ : (Formula.allFromTo lo hi ψ).Scoped D 0 = true) (limit : Nat) (i : Int)
    (h : decidingValue D limit (.allFromTo lo hi ψ) = some i) :
    ∃ l u, Term.value D.env [] lo = some l ∧ Term.value D.env [] hi = some u ∧ l ≤ i ∧ i ≤ u ∧
      ¬ Holds D.env [i] ψ ∧ ∀ m, l ≤ m → m < i → Holds D.env [m] ψ
/-- … and of a true existential its first witness. -/
theorem decidingValue_ex (D : Defs) (hD : D.WellFormed = true) (lo hi : Term) (ψ : Formula)
    (hφ : (Formula.exFromTo lo hi ψ).Scoped D 0 = true) (limit : Nat) (i : Int)
    (h : decidingValue D limit (.exFromTo lo hi ψ) = some i) :
    ∃ l u, Term.value D.env [] lo = some l ∧ Term.value D.env [] hi = some u ∧ l ≤ i ∧ i ≤ u ∧
      Holds D.env [i] ψ ∧ ∀ m, l ≤ m → m < i → ¬ Holds D.env [m] ψ
/-- A failed universal always reports its deciding value. -/
theorem decidingValue_of_fails (D : Defs) (limit : Nat) (lo hi : Term) (ψ : Formula)
    (h : arithOutcome D limit (.allFromTo lo hi ψ) = .decided .fails) :
    (decidingValue D limit (.allFromTo lo hi ψ)).isSome = true

/-- *Opaque*: the service answer, and the readers of row `i`'s outcome, units, deciding value and import label. -/
def Run.runCaseReported : Lean.Json → Lean.Json
def Run.outcomeAt : Lean.Json → Nat → Option Outcome
def Run.unitsAt : Lean.Json → Nat → Option Nat
def Run.decidingAt : Lean.Json → Nat → Option Int
def Run.importAt : Lean.Json → Nat → Option String

theorem Run.outcome_sound (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) (i : Nat)
    (hi : i < c.statements.length) :
    Run.outcomeAt (Run.runCaseReported j) i = some (c.outcome (c.statements[i]'hi))
theorem Run.units_sound (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) (i : Nat)
    (hi : i < c.statements.length) (w : Nat) (hw : Run.unitsAt (Run.runCaseReported j) i = some w) :
    ∃ b, decideBounded c.defs c.budget (c.statements[i]'hi).2 = some (b, w)
theorem Run.deciding_sound (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) (i : Nat)
    (hi : i < c.statements.length) (v : Int) (hv : Run.decidingAt (Run.runCaseReported j) i = some v) :
    decidingValue c.defs c.budget (c.statements[i]'hi).2 = some v
theorem Run.import_sound (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) (i : Nat)
    (hi : i < c.statements.length) (l : String) (hl : Run.importAt (Run.runCaseReported j) i = some l) :
    ∃ imp, c.imports.lookup (c.statements[i]'hi).1 = some imp ∧ l = importLabel imp ∧
      c.outcome (c.statements[i]'hi) = .decided .holds

end VE.Arith

namespace VE.Service
theorem runMode_arith (j : Lean.Json) : runMode .arith j = VE.Arith.Run.runCaseReported j := rfl
end VE.Service

namespace ResponseShape.Encoders.Arith
theorem runCaseReported_fits (j : Lean.Json) :
    ResponseShape.Fits j ResponseShape.Skeletons.arith (VE.Arith.Run.runCaseReported j)
end ResponseShape.Encoders.Arith
```

**Rows.** A refused case answers the common case error. Otherwise each statement has one row, in order, with
`statement` (the request's id), `statement_id`, `outcome` (`holds`, `fails` or `unknown`; never `undefined`),
`reason` (1.5's text for unknown, else `null`), `bounded` (`Formula.Bounded`), `units` (the formula-node visits spent
when evaluation decided it, else `null`), `deciding` (`{"variable": x, "value": "<integer>"}` with the request's name
of the outermost binder, else `null`), `line` (11.3's rendering), `import` (`importLabel`, else `null`) and `rests_on`
(for an imported row its residual line "Proved in Lean with Mathlib at revision <rev>, declaration <name>; VE did not
replay this proof.", else empty). With the deciding value, M-5's row says "fails at n = 1" (13.3). The relay
(`ve/arith.py`) checks schema and binding only: one row per statement in order, `statement` equal to the request's id,
`deciding.variable` the request's outermost binder of that statement and present only when that binder is
`all-from-to` or `ex-from-to`, `import` present only when the request has an import for that statement, `units` at
most the request's budget. Anything else is `CheckerUnavailable`. 13.6 gives complete requests and answers.

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
| `NonlinearPremise` | ME-5 | a premise or conclusion not linear in the unknowns | `NonlinearPremise: <term> (declare a square link or name the product)` |
| `UnknownLink` | ME-5 | a square link names a value that is not free | `UnknownLink: <name>` |
| `UnknownPremise` | ME-5 | a derivation names a premise id that `premises` lacks | `UnknownPremise: <id>` |
| `ConsistencyInput` | ME-8 | a consistency input is not a stated value | `ConsistencyInput: <name> is not a stated value` |
| `ConsistencyName` | ME-8 | an output reads a free value (8.1's name rule) | `ConsistencyName: <name> is an unknown; an output may read only the inputs and values that have a value` |
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
| `PlacesMismatch` | ME-11 | the places phrase does not name the printed spelling's places (11.1, J8) | `PlacesMismatch: <printed> is written <its places phrase>, not <the sentence's places phrase>` |
| `IsExpression` | ME-11 | "A is E" with an expression E (11.1, J7) | `IsExpression: write "Let <A> be <E>." to define it or "<A> equals <E>." to claim it` |
| `UnscopedVariable` | ME-12 | a variable that no binder or parameter names | `UnscopedVariable: <name> (bind it with a quantifier or name it as a parameter)` |
| `ShadowedVariable` | ME-12 | a binder or parameter reuses a name in scope | `ShadowedVariable: <name> (choose another name)` |
| `UnknownDefinition` | ME-12 | a call names no function, or no predicate, of that name | `UnknownDefinition: <name> is not a defined <function or predicate>` |
| `RecursiveDefinition` | ME-12 | a definition calls itself or a later name | `RecursiveDefinition: <name>` |
| `ArityMismatch` | ME-12 | a call with the wrong number of arguments | `ArityMismatch: <name> takes <n>` |
| `UnboundedCount` | ME-12 | a count's condition has an unbounded quantifier | `UnboundedCount: the condition of a count must be bounded` |
| `ImportStatement` | ME-13 | the record's statement id is not this conclusion's | `ImportStatement: the import proves <id>, not <id>` |
| `ImportMeansDigest` | ME-13 | built against other meaning sources | `ImportMeansDigest: <digest>` |
| `ImportCheckDigest` | ME-13 | the check file is not the one VE generates | `ImportCheckDigest: <digest>` |
| `ImportAxiom` | ME-13 | an axiom outside the allowlist | `ImportAxiom: <axiom>` |

No diagnostic text contains a symbol (plan 9); each refusal names its rewrite.

### 13.2 Fixture definitions

Definitions are given here; the expected results are in 13.3, computed in the stub for draft 1's fixtures and by hand
for draft 2's (marked there). Draft 4's fixtures (marked *phase 1*) were computed with exact fractions by phase 1's
scripts (`fixture-anchors.json`'s pre-checks, not VE verdicts) and by hand, and are recomputed in the stub at the
re-check (17, item 8). Draft 3's *paraphrase* sources were re-anchored by ME-0 to byte spans of the pinned texts
(`docs/research/evidence/math-evidence/fixture-anchors.json`); each row now gives its anchor. Physics spans are in
`physics-michelson-morley/source.txt` (24,368 B), mathematics spans in the OCR text
`math-ramanujan-bertrand/source.txt` (2,651 B), deep-learning units in `dl-alphafold/source.txt` (66,858 B). A
source span written in TeX ("10^{-8}") or with a superscript ("2×10^7") is not read by 4.4's source-number grammar,
so a finding over it stays "transcription unchecked" (2.5).

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
| V-7b | *phase 1*: `paper/sections/04-e1.md`, the six main-text p values (ME-0 units v060-v065): .460938, .875488, .000977, .001953, .218750, .993164 | `grainRefutes 4096` of each printed p at six places, both rules |
| V-9 | software convention "Python 3.12": 2.675 printed as 2.67 | stated 2.675; `rounds tiesUp (267, 2)`; `"software"` declared |
| V-10 | software convention: 0.1 + 0.2 − 0.3 printed as 0.0000000000000001 | `rounds tiesUp` of the sum to (1, 16); `"software"` declared |
| V-11 | debate A1 | x = 10³⁹ (stated), y = x⁶⁴, z = y × y; claims `z < 1`, `1 / (x − x) = 1`, `y < 1` |
| V-12 | debate F1 | source bytes "Its scored baseline, 176/594 = .296, is outside; claimed covered bytes 4,792 (43.90%)"; spans [31, 35) (".296"), [21, 24) ("176"), [71, 76) ("4,792"), [78, 83) ("43.90"), [30, 35), [31, 200) |
| V-13 | finding kinds | `findingKind` of (no software, [checked, checked]), (no software, [checked, unchecked]), (no software, []), (software, [checked]) |
| I-1 | identity, negative printed place (J1) | H-8's case: values length `"11"` and wavelength `["sci", "5.89", -7]`; claim `["rounds", ["div", ["val", "length"], ["val", "wavelength"]], ["sci", "2", 7]]`; beside it the same case with the wavelength written `"0.000000589"`, and the same case with the printed number written `"20000000"` |
| I-2 | identity, negative unit exponent (J1) | the `ve-units@2` environment `{"unit_schema": "ve-units@2", "base_dimensions": ["length", "time"], "units": {"meter_per_second": {"base_exponents": {"length": 1, "time": -1}, "factor": "1"}}}`; the same with its keys in another order; a `ve-units@1` environment of W6a's news fixtures |
| D-1 | ROADMAP: "17/19 … (15 tableau certificates plus T9 and T9e)" | `15 + 2 = 17` |
| D-2 | UDHR pilot SUMMARY: "claimed covered bytes 4,792 (43.90%)" of 10,916 | `rounds tiesUp (100 × 4792 / 10916) (4390, 2)` |
| D-3 | constitution pilot SUMMARY: 2,951 bytes (1.60%); 73 + 349 + 2,529 | `73 + 349 + 2529 = 2951`; `rounds tiesUp (100 × 2951 / 184893) (160, 2)` |
| H-1 | RE-WORDED (the source's TeX, spans from 6,698): D/(V − v) + D/(V + v) = 2DV/(V² − v²) | identity over free D, V, v |
| H-2 | RE-WORDED: 2DV²/(V² − v²) − 2D(1 + v²/V²) = 2Dv⁴/(V²(V² − v²)) | identity |
| H-3 | RE-WORDED: 2D(1 + v²/V²) − 2D(1 + v²/(2V²)) = Dv²/V² | identity |
| H-4 | *phase 1* (CHANGED in draft 3, which stated v/V = 10⁻⁴; the source never does): "hence the displacement of the interference fringes should be ${2D \frac{v^2}{V^2}}$. Considering only the velocity of the earth in its orbit, this would be ${2D \times 10^{-8}}$." (spans [7,265, 7,348) and [7,350, 7,443), unit h049) | sq stated `["sci", "1", -8]` (the squared speed ratio, `support: testimony`, span in h049), D free: `["identity", 2 × D × sq, 2 × D × ["sci", "1", -8]]`; with D = 2 × 10⁷ stated, `2 × D × sq = 0.4` |
| H-5 | *phase 1* (CHANGED in draft 3, which used H-4's unstated v/V): "The distance D was about eleven meters, or 2×10^7 wave-lengths of yellow light; hence the displacement to be expected was 0•4 fringe." (span [15,790, 15,882), unit h114; the source's decimal point is a bullet) | path = 2 × 10⁷ (stated, span), sq = 10⁻⁸ (stated, span in h113): `2 × path × sq = 0.4` |
| H-5b | *phase 1*: "If, as was the case in the first experiment, ${D =2\times 10^{6}}$ waves of yellow light, the displacement to be expected would be 0.04 of the distance between the interference fringes." (unit h050) | path = 2 × 10⁶, sq = 10⁻⁸: `2 × path × sq = 0.04` |
| H-6 | ANCHORED (h115-h116): "The actual displacement was certainly less than the twentieth part of this … the relative velocity of the earth and the ether is … certainly less than one-fourth" | premises d = 0.4 s, d < 0.02; link (s, r); conclusion r < 1/4; certificate weights [1, 0, 1, 0.4] on [d − 0.4s ≥ 0, 0.4s − d ≥ 0, 0.02 − d > 0, negated goal] |
| H-6p | ANCHORED: "and probably less than the fortieth part" … "probably less than one sixth the earth's orbital velocity" | d < 0.01; conclusion r < 1/6; same weights |
| H-6n | negative control: "less than one fifth" | conclusion r < 1/5; candidate κ: r = 1/5, s = 1/25, d = 0.016 |
| H-6a | debate A2 | H-6's premises; candidate κ: r = 1, s = 0, d = 0, against r < 1/4, with and without the link |
| H-7 | physical dimensions | Γ: D, λ lengths; V, v length per time; T time; D/(V − v), D/λ, D + T |
| H-7u | unit change (constructed: its ratio 10⁻⁴ is not the source's, which states only v²/V² = 10⁻⁸; the results do not depend on it) | path 2 × 10⁷ (length), ratio 10⁻⁴ (dimensionless); rescale length by 1,000; `2 × path × ratio² < path` and `rounds tiesUp (2 × ratio²) (2, 8)`; negative pair: `2 × path × ratio² = 0.4 × path` and `rounds tiesUp (2 × ratio²) (3, 8)` |
| H-7c | conversion | 2.5 × kilometer against 2,500 × meter (factors 1,000 and 1) |
| H-7l | legacy tags | `usd_cent` and `eur_cent` as `ve-units@1` tags; `a + b` |
| H-7d | `day` | a `ve-units@2` declaration giving `day` `{"time": 1}` |
| H-8 | ANCHORED (h114): "The distance D was about eleven meters, or 2×10^7 wave-lengths of yellow light" | length 11, wavelength 5.89 × 10⁻⁷ (testimony): `rounds tiesUp (length / wavelength) (2, −7)` |
| H-9 | *phase 1* (CHANGED in draft 3, which assumed printed readings at 16 azimuths): the noon and evening tables, spans [12,968, 15,143), units h086-h106. "The following tables give the means of the six readings"; 17 marks per row (mark 16 at the start and end of a turn); sessions noon July 8, 9, 11 and evening July 8, 9, 12; rows Mean, Mean in w. l., a repeated half row (marks 8-16), Final mean; "one division means 0.02 wave-length" | stated: the 102 session cells and the 104 printed derived cells; factor = 0.02 (stated, span); columns j = 0 … 16 in printed order (column 0 is mark 16 at the start of the turn); for each table t and column j: m(t, j) defined as the sum of the three session cells divided by 3, claim `rounds tiesUp m(t, j) Mean(t, j)` at one place (34); `factor × Mean(t, j) = WL(t, j)` (34); `Half(t, i) = WL(t, 8 + i)` for i = 0 … 8 (18); `(WL(t, i) + WL(t, i + 8)) / 2 = Final(t, i)` for i = 0 … 8 (18). Negative control H-9n: the noon Mean at mark 1 stated 41.9 instead of 41.6 |
| H-10 | RE-WORDED: the dates July 8, 9, 11 and 12 (row labels without a year; "November 1887" is the publication line, span [176, 189)) | refused (W6a dates start at 1970-01-01; ME-0 P6: `DateRange(1887-07-08)`, the 1970-01-01 control admitted); W6's trigger ET-T3; the year is a stated premise with its span |
| S-1 | kappa and binomial | `kappa?` of [[20, 5], [10, 15]] and [[5, 0], [0, 0]]; `binomialTail 10 8 (1/2)`, `binomialTail 10 0 (1/3)` |
| S-2 | sign flips | `signFlipP [1, 1, 1, 1]`; `signFlipP [1, 2, −1, 3, 2, 1, −2, 4, 1, 2, 3, −1]`; `(signs 12).length` |
| S-3 | GRIM | a mean of five integers printed as 3.47, 3.40, 3.4 |
| S-4 | square roots | `SqrtRoundsTo tiesUp` of 9/100 to 0.3 and 0.4, beside `RoundsTo` of 3/10 |
| S-5 | statistical domains (J5) | `["binomial-tail", 10, 8, p]` at p = 0, 1 and 2, beside the unguarded `binomialTail 10 8 2` and `binomialTail 1 1 2`; `["mean", []]`, `["population-variance", []]`, `["sign-flip-p", []]` beside the unguarded `signFlipP []`; with x stated `"3"`, `["variance", ["x"]]`, `["population-variance", ["x"]]`, `["sign-flip-p", ["x"]]`; `["sqrt-rounds", ["lit", "-0.01"], "0.1"]`; `kappa? [[0, 0], [0, 0]]` |
| C-1 | consistency name rule (J4) | a stated `"0.4"` (the input), b stated `"0.3"` (not an input), f free; k1 `["consistent", ["a"], [["rounds", ["add", ["val", "a"], ["val", "b"]], "0.9"]]]`; k2 `["consistent", ["a"], [["lt", ["add", ["val", "a"], ["val", "b"]], ["lit", "0.66"]]]]`; k3 `["consistent", ["a"], [["lt", ["add", ["val", "a"], ["val", "f"]], ["lit", "1"]]]]` |
| T-1 | tables (A4, J9) | table judge (text) / approved (bool) / score (number), as the CSV bytes `judge,approved,score\n32B,true,3\n32B,false,5\n14B,true,\n14B,,4\n14B,yes,6\n`: rows ("32B", true, 3), ("32B", false, 5), ("14B", true, absent), ("14B", absent, 4), ("14B", text "yes", 6); filters `judge is "7B"` (empty), `judge is "32B"`, `approved`, `not approved` (`["false", "approved"]`), `judge is not "32B"`, `score does not equal 3` |
| T-2 | digest | a data handle whose bytes hash differently |
| T-3 | exhaustion through definitions (J2) | T-1's bytes, `"budget": 6`; values: `approved_32b` counted (`count`, `["and", ["is", "judge", "32B"], ["true", "approved"]]`), `share` defined `approved_32b / 2`, `mean_7b` counted (`["mean", "score"]`, `["is", "judge", "7B"]`); claims c1 `approved_32b = 1`, c2 `share < 1`, c3 `mean_7b < 1`, c4 `mean_7b + share < 1`, c5 `share + mean_7b < 1`; the same case without `budget` |
| M-1 | Ramanujan, RE-WORDED: "Thus Bertrand's Postulate is proved for all values of x, not less than 162: and, by actual verification, we find that it is true for smaller values" (whole n from 1 to 161) | `allFromTo 1 161 (exFromTo (n + 1) (2n) (prime p))` |
| M-1b | budget boundary | M-1 with budgets 17,010 and 17,011 |
| M-2 | the chain 2, 3, 5, 7, 13, 23, 43, 83, 163 | each prime, each less than twice the one before |
| M-3 | Bertrand's postulate, whole-number reading | `bertrand` (12.3) |
| M-3r | the real reading of x | a reading set {whole number, real}; `arith@0` has no reals |
| M-4 | π(x) − π(x/2) ≥ 2 for x ≥ 11; RE-WORDED: formula (18), OCR span [2,575, 2,620) "> 1, 2, 3, 4,5,..., if * » 2, 11, 17, 29, 41" (numbers intact, symbols garbled) | `primeCount x = #{p ∈ [1, x] : prime p}`, `halfPrimeCount x = #{p ∈ [1, x] : 2p ≤ x ∧ prime p}`; `allFromTo 11 N (2 ≤ primeCount x − halfPrimeCount x)` at N = 200, 248, 249, 1,000 |
| M-4b | *phase 1*: formula (18)'s other pairs, the same span | for (k, T) = (1, 2), (3, 17), (4, 29), (5, 41): `allFromTo T N (k ≤ primeCount x − halfPrimeCount x)` at the bound N ME-12 measures for each, and the single instance at x = T − 1 |
| M-4x | exhaustion | M-1 with budget 1,000 |
| M-5 | negative control | strict n < p < 2n for n from 1 through 161; its deciding value (12.5) |
| M-6 | the prime predicate | VE's `prime` against `IsPrime` on 0 through 400 |
| DL-1 | *phase 1*, AlphaFold d024 and d027: medians 0.96 Å (95% interval 0.85–1.16) against 2.8 Å (2.7–4.0); all-atom 1.5 Å (1.2–1.6) against 3.5 Å (3.1–4.2) | stated medians and bounds; claims `within` for each median (4) and `alphafold < alternative` for each measure (2) |
| DL-2 | *phase 1*, d239 and d242: "4.8 min with 256 residues, 9.2 min with 384 residues and 18 h at 2,500 residues"; "Without ensembling, the network is 8× faster and the representative timings for a single model are 0.6 min …, 1.1 min … and 2.1 h …" | for each length, `rounds tiesUp (with / without) (8, 0)`; the two timings of a length share their unit |
| DL-3 | *phase 1*, d119 "around 350,000 diverse sequences" and d231 "a Uniclust dataset of 355,993 sequences" (one set: a translation premise, `support: assumption`) | `rounds tiesUp 355993 (350000, 0)`, `rounds tiesUp 355993 (35, −4)` |
| DL-4 | *phase 1*, d214: "Removing BFD reduced the mean accuracy by 0.4 GDT, removing Mgnify reduced the mean accuracy by 0.7 GDT, and removing both reduced the mean accuracy by 6.1 GDT." | stated 0.4, 0.7, 6.1; constructed claim `0.4 + 0.7 < 6.1` |
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
| V-7 | 7 of 8 not refuted under ties up; the fourth (0.007812) refuted under ties up, not under half to even (J11: draft 1 said "the eighth") | the multiples m/512 that round to each printed p under ties up: 416, 44, 352, none, 348, 184, 64, 448; under half to even the fourth is 4. 44/512 = 11/128 and 348/512 = 87/128 are exact ties at six places whose upper neighbour is even, so both rules agree |
| V-8 | holds only under half to even | `tieAt 6 (4/512)` = true; ties up false, half to even true; `round tiesUp` 7,813, `round halfEven` 7,812 |
| V-7b | *phase 1*: none of the six refuted, under either rule | the multiples k/4,096 that round to each printed p: 1,888, 3,586, 4, 8, 896, 4,068 (0.4609375, 0.87548828125, 0.0009765625, 0.001953125, 0.21875, 0.9931640625); 1,888/4,096 is an exact tie at six places whose upper neighbour 460,938 is even, so both rules give .460938; no other is a tie |
| V-9 | exact claim **fails**; reproduction unknown; finding `softwareUnreproduced` | ties up false, half to even false; `tieAt 2 2.675` = true; both rules round to 268 |
| V-10 | exact claim **fails**; reproduction unknown; finding `softwareUnreproduced` | exact value 0; both rules false; `round tiesUp 16 0` = 0 |
| V-11 | **unknown** (`limit .digits`), **undefined**, **fails** | digit counts of 10³⁹, 10^(39·64), 10^(39·128): 40, 2,497, 4,993 |
| V-12 | checked, refused, checked, checked, checked, refused, refused, refused | `spanText`: ".296", "176", "4,792", "43.90"; `spanMatches`: [31,35) vs (296,3) true, vs (297,3) false; [21,24) vs (176,0) true; [71,76) vs (4792,0) true; [78,83) vs (4390,2) true, vs (439,1) false; [30,35) (" .296") false; [31,200) (outside) false |
| V-13 | `source`, `transcriptionUnchecked`, `transcriptionUnchecked`, `softwareUnreproduced` | as computed |
| I-1 | *by hand*: `canonical` succeeds; the two wavelength spellings give one `meaning_id`; the `"20000000"` spelling gives another | canonical value literals `"11"` and `"0.000000589"`; canonical claim `["rounds",["div",["val","length"],["val","wavelength"]],["2","-7"],"ties-up"]`; `"20000000"` is `["20000000","0"]`; draft 1's encoding `["2",-7]` gives `Except.error "Natural number expected"` (Astra evaluated the frozen functions read-only); the digests are pinned by ME-2 |
| I-2 | *by hand*: `environmentId` succeeds; the reordered environment has the same id; the `ve-units@1` id is W6a's today | canonical text `{"base_dimensions":["length","time"],"unit_schema":"ve-units@2","units":{"meter_per_second":{"base_exponents":{"length":"1","time":"-1"},"factor":"1"}}}`; without J1's strings the exponent −1 gives "Natural number expected"; the digests are pinned by ME-6 |
| D-1 | holds | 15 + 2 = 17 |
| D-2 | holds | 200 × 100 × 4,792/10,916 = 23,960,000/2,729 = 8,779.77… in [8,779, 8,781) |
| D-3 | holds × 2 | 73 + 349 + 2,529 = 2,951; 200 × 100 × 2,951/184,893 = 59,020,000/184,893 = 319.21… in [319, 321) |
| H-1, H-2, H-3 | identity (ME-9) | the stub evaluated both sides at (D, V, v) = (11, 3, 1), (2, 5, −3), (7/3, 1/2, 1/7): no point differs; at V = v the left side of H-1 does not denote; the normaliser's result is ME-9's |
| H-4, H-5 | *phase 1*: identity in D; holds | 2 × (2 × 10⁷) × 10⁻⁸ = 2/5 exactly (draft 3 reached the same 0.4 through the unstated (10⁻⁴)²) |
| H-5b | *phase 1*: holds | 2 × (2 × 10⁶) × 10⁻⁸ = 1/25 = 0.04 |
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
| H-9 | *phase 1*: all 104 claims hold; H-9n **fails** | no rounding tie can occur (a sum of tenths divided by 3 is never an odd twentieth); noon column 0: (44.7 + 57.4 + 27.3)/3 = 647/15 = 43.13…, ten times it in [430.5, 431.5), printed 43.1; 0.02 × 43.1 = 0.862; Half(0, 0) = WL(0, 8) = 0.706; (0.862 + 0.706)/2 = 0.784; evening column 0: 154/3 = 51.33…, printed 51.3, WL 1.026; H-9n: noon column 1 is (44.0 + 57.3 + 23.5)/3 = 41.6 exactly, not within rounding of 41.9. Today's W6a certifies the Mean, Half and Final relations (ME-0); only `factor × Mean = WL` is beyond it |
| H-10 | refused | W6a dates start at 1970-01-01; ME-0 measured `DateRange(1887-07-08)` |
| S-1 | 2/5; none; 7/128; 1 | as computed |
| S-2 | 1/8; 57/1,024; 4,096 | as computed |
| S-3 | 3.47 refuted (GRIM); 3.40 and 3.4 not refuted | 17/5 = 3.4, 18/5 = 3.6 |
| S-4 | true, true; false, false | `sqrtRoundsTo_of_square` both directions |
| S-5 | *by hand*: binomial tail 0, 1, **undefined**; mean, population variance and sign-flip p of no values **undefined**; of the one value 3: variance **undefined**, population variance 0, sign-flip p 1; the square root of −0.01 **undefined** (not fails); kappa of the empty table **undefined** | unguarded, `binomialTail 10 8 2` = 45 · 256 − 10 · 512 + 1024 = 7,424 and `binomialTail 1 1 2` = 2, `signFlipP []` = 1: these are why the domain is in `Denotes`; at p = 1 only the i = 10 term is nonzero |
| C-1 | *by hand*: k1 **inconsistent** (fails), refuted by enclosure; k2 **consistent** (holds), witness a = 7/20; k3 refused (`ConsistencyName: f`) | a's interval is 7/20 ≤ a < 9/20 and b stays 3/10, so a + b lies in the enclosure [13/20, 3/4], which misses 0.9's interval [17/20, 19/20); the printed value a = 2/5 gives 7/10 and fails k2's output, the lower endpoint 7/20 gives 13/20 < 0.66. Under draft 1's `witness_sound`, which let b vary, a = 2/5 and b = 1/2 would have "witnessed" k1 while the enclosure refuted it |
| T-1 | empty: count 0, sum 0, mean, min, max undefined; 32B: 2, 8, 4, 3, 5; approved: count 2, sum, mean, min, max undefined (an absent score); *by hand*: not approved: count 1 (the 32B row with false), sum, mean, min and max 5; judge is not 32B: count 3, sum undefined (an absent score); score does not equal 3: count 3, sum 15, mean 5, min 4, max 6 | the three-row results are the stub's (the two added rows change none of them); draft 1's `not approved` would select the absent and the text cell too: count 3 |
| T-2 | refused (`DigestMismatch`) | decoder check (ME-4) |
| T-3 | *by hand*: at budget 6, c1 and c2 **unknown** (`limit .evaluations`; c2 through `share`'s definition), c3 and c4 **undefined** (the empty mean is the first fault), c5 **unknown**; without `budget`, c1 and c2 hold and c3 to c5 are undefined | `mean_7b`'s filter is one node over five rows, five visits within 6; `approved_32b`'s is three nodes, at least two visits per row, at least ten; at the default budget `approved_32b` = 1 (the first row only) and `share` = 1/2 |
| M-1 | holds | `decideBounded primeDefs 1,000,000` = (true, 17,011 units) |
| M-1b | unknown at 17,010; holds at 17,011 | exactly the units M-1 spends |
| M-2 | holds | (true, 395 units) |
| M-3 | stated, not decided (`unboundedStatement`); proved only by import (EX-1) | `Bounded` false |
| M-3r | reading set; the real reading stays residual | — |
| M-4 | holds through 248 within 1,000,000 units; unknown from 249 | π(10) − π(5) = 1 (111 units) and π(11) − π(5) = 2 (127 units); at N = 200: (true, 576,518); at 248: (true, 998,395); at 249: none, and (true, 1,008,568) with a budget of 2,000,000; at 1,000: none |
| M-4b | *phase 1*: each pair holds from its threshold to its measured bound; each instance at x = T − 1 fails | primeCount − halfPrimeCount at x = 1, 16, 28, 40 is 0, 2, 3, 4 (one less than k), at x = 2, 17, 29, 41 it is 1, 3, 4, 5; its minimum over T … 1,000 is k for each pair (exact counts in phase 1); the bounds N are ME-12's, as for M-4 |
| M-4x | unknown (`limit .evaluations`) | none at budget 1,000 |
| M-5 | **fails** at n = 1: deciding value 1 | (false, 2 units): the range 2…1 is empty; *by hand*: `decidingValue` is 1, the first n, since the evaluator stops there |
| M-6 | agree on 0…400 | 78 primes |
| E-1 | c1 discharged, c2 not (fails), c3 not (missing); statuses CHECKED, OPEN, UNFORMALISED, UNFORMALISED | as computed |
| DL-1 | *phase 1*: holds × 6 | 0.85 ≤ 0.96 ≤ 1.16, 2.7 ≤ 2.8 ≤ 4.0, 1.2 ≤ 1.5 ≤ 1.6, 3.1 ≤ 3.5 ≤ 4.2; 0.96 < 2.8, 1.5 < 3.5 |
| DL-2 | *phase 1*: holds, holds, **fails** | 4.8/0.6 = 8; 9.2/1.1 = 92/11 = 8.36…; 18/2.1 = 60/7 = 8.57…, outside [7.5, 8.5); in translation "8×" is a reading set, and this row distinguishes its readings |
| DL-3 | *phase 1*: **fails**, **fails** | 355,993 is not 350,000 (places 0), and 355,993 × 10⁻⁴ = 35.5993 is outside [34.5, 35.5) (it rounds to 36, that is 360,000); only an open tolerance reading holds |
| DL-4 | *phase 1*: holds | 0.4 + 0.7 = 1.1 < 6.1 |

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
| `Case.outcome_bounded` (draft 2) | R-7's m1 (holds; it means) | R-7's m5 (fails; it does not) |
| `Stat.run_isSome` (draft 2) | S-5's population variance of one value (some 0; 1 ≤ 1) | S-5's variance of one value (none; 2 > 1) |
| `Claim.facts_sound` (draft 2) | H-6's p1 at d = 2/125, s = 1/25 (facts and premise hold) | p1 at d = 1, s = 0 (both fail) |
| `Expr.inline_sound` (draft 2) | C-1's a + b at a = 7/20 and x = 13/20 (both sides denote it) | the same at x = 7/10 (neither does: the input was not replaced by its printed value) |
| `Claim.inline_sound` (draft 2) | C-1's k2 output at a = 7/20 (holds on both sides) | at a = 2/5 (fails on both sides) |
| `bertrand_means_iff` | — | — |

`bertrand_means_iff` relates two unbounded statements, so no evaluation can show either direction. M-6 checks its
ingredient (VE's `prime` agrees with `IsPrime` on 0 through 400), and M-1 is its bounded instance; the proof is an
unfolding of definitions (ME-12).

### 13.5 Negative controls and regressions

- Constitution u0203.s02, u0112.s03 and u0147.s04 stay as they are: their "evidence" and "probability" are epistemic
  standards in norms. A calc case cannot carry a norm, an open term or a reading of them (`InvalidInput`).
- W6a's news fixtures (`tests/test_news_w6a_fixtures.py`) and the math mini-paper's results are unchanged by every
  batch; `ve-units@1` environments keep their identities (H-7l, I-2).

### 13.6 Complete requests and answers, one per kind (J3)

Each request is a whole case; each answer gives every row in full. Digests are written `<hex64>`: they are SHA-256
values that ME-2 (calc), ME-6 (units) and ME-12 (arith) compute and pin in their route cases; none was computed for
this draft. A `line` is Lean's display (9, 11); where 11.1 or 11.3 fixes the sentence it is written out, and where
they do not, it is `"<display>"`, pinned by the batch. These are standalone cases, not a translated document's
`calculation` content (ME-10), so `finding` is `null`. The values and units of fixtures that draft 1 computed in the
stub are the stub's; every other number below was computed by hand (draft 2; R-10 in draft 3) and is part of the
re-check (17).

**R-1, claims: holds and fails** (V-1, V-1n).

```json
{"format": "ve-calc@0",
 "values": [
   {"name": "scored", "words": "the false approvals of the scored baseline", "stated": "176"},
   {"name": "trials", "words": "the trials of the scored baseline", "stated": "594"},
   {"name": "baseline", "words": "the scored baseline rate", "defined": ["div", ["val", "scored"], ["val", "trials"]]}],
 "claims": [
   {"id": "c1", "claim": ["rounds", ["val", "baseline"], "0.296"]},
   {"id": "c2", "claim": ["rounds", ["val", "baseline"], "0.297"]}]}
```

```json
[{"status": "ok", "claim": "c1", "claim_id": "<hex64>", "kind": "claim", "outcome": "holds", "reason": null,
  "sides": ["8/27"], "display": "0.29629…", "tie": false,
  "line": "The scored baseline rate is 0.296 when rounded to three decimal places, with exact ties going up.",
  "finding": null, "reproduction": null,
  "rests_on": [{"name": "scored", "source": "stated", "support": null, "span": "unchecked"},
               {"name": "trials", "source": "stated", "support": null, "span": "unchecked"}]},
 {"status": "ok", "claim": "c2", "claim_id": "<hex64>", "kind": "claim", "outcome": "fails", "reason": null,
  "sides": ["8/27"], "display": "0.29629…", "tie": false,
  "line": "The scored baseline rate is 0.297 when rounded to three decimal places, with exact ties going up.",
  "finding": null, "reproduction": null,
  "rests_on": [{"name": "scored", "source": "stated", "support": null, "span": "unchecked"},
               {"name": "trials", "source": "stated", "support": null, "span": "unchecked"}]}]
```

**R-2, claims: unknown and undefined** (V-11).

```json
{"format": "ve-calc@0",
 "values": [
   {"name": "x", "words": "the large number", "stated": ["sci", "1", 39]},
   {"name": "y", "words": "the larger number", "defined": ["pow", ["val", "x"], 64]},
   {"name": "z", "words": "the largest number", "defined": ["mul", ["val", "y"], ["val", "y"]]}],
 "claims": [
   {"id": "v1", "claim": ["lt", ["val", "z"], ["lit", "1"]]},
   {"id": "v2", "claim": ["eq", ["div", ["lit", "1"], ["sub", ["val", "x"], ["val", "x"]]], ["lit", "1"]]}]}
```

```json
[{"status": "ok", "claim": "v1", "claim_id": "<hex64>", "kind": "claim", "outcome": "unknown",
  "reason": "unknown: an exact value would have more than 4,096 digits",
  "sides": [null, "1"], "display": null, "tie": false, "line": "The largest number is less than 1.",
  "finding": null, "reproduction": null,
  "rests_on": [{"name": "x", "source": "stated", "support": null, "span": "unchecked"}]},
 {"status": "ok", "claim": "v2", "claim_id": "<hex64>", "kind": "claim", "outcome": "undefined", "reason": null,
  "sides": [null, "1"], "display": null, "tie": false, "line": "<display>",
  "finding": null, "reproduction": null,
  "rests_on": [{"name": "x", "source": "stated", "support": null, "span": "unchecked"}]}]
```

**R-3, a derivation that follows** (H-6), and **R-4, one that does not** (H-6n: the same case with the conclusion
`["lt", ["val", "r"], ["div", ["lit", "1"], ["lit", "5"]]]`).

```json
{"format": "ve-calc@0",
 "values": [
   {"name": "r", "words": "the velocity ratio", "free": true},
   {"name": "s", "words": "the squared velocity ratio", "free": true},
   {"name": "d", "words": "the displacement", "free": true}],
 "premises": [
   {"id": "p1", "claim": ["eq", ["val", "d"], ["mul", ["lit", "0.4"], ["val", "s"]]], "support": "assumption"},
   {"id": "p2", "claim": ["lt", ["val", "d"], ["lit", "0.02"]], "support": "assumption"}],
 "claims": [
   {"id": "h6", "claim": ["follows", ["lt", ["val", "r"], ["div", ["lit", "1"], ["lit", "4"]]], ["p1", "p2"],
                          [["s", "r"]]]}]}
```

```json
[{"status": "ok", "claim": "h6", "claim_id": "<hex64>", "kind": "follows", "outcome": "holds", "reason": null,
  "certificate": [
    {"farkas": {"goal": {"const": "1/20", "coeffs": [["s", "-1"]], "strict": true},
                "weights": ["1", "0", "1", "2/5"]}},
    {"square": {"square": "s", "root": "r", "a": "1/20", "b": "1/4"}}],
  "counterexample": null,
  "line": "Assume the following. 1. The displacement equals the product of 0.4 and the squared velocity ratio. 2. The displacement is less than 0.02. 3. The squared velocity ratio equals the square of the velocity ratio. 4. The velocity ratio is at least 0. From these, it follows that the velocity ratio is less than 1 divided by 4.",
  "finding": null, "reproduction": null,
  "rests_on": [{"premise": "p1", "support": "assumption"}, {"premise": "p2", "support": "assumption"},
               {"link": ["s", "r"], "support": "assumption"},
               {"name": "r", "source": "free", "support": null, "span": "unchecked"},
               {"name": "s", "source": "free", "support": null, "span": "unchecked"},
               {"name": "d", "source": "free", "support": null, "span": "unchecked"}]}]
```

R-4's row differs in `claim_id`, `outcome` (`"fails"`), `certificate` (`null`), `counterexample`
(`[["r", "1/5"], ["s", "1/25"], ["d", "2/125"]]`: the claimed bound tried first, s = r · r, d = 0.4 s) and `line`
("… it follows that the velocity ratio is less than 1 divided by 5."). The weights are on the facts d − 0.4 s ≥ 0,
0.4 s − d ≥ 0, 0.02 − d > 0 and the negated goal s − 1/20 ≥ 0 (3.4's order); they sum to the constant 0 with a positive
weight on the strict fact, as the stub's `Farkas.check` found for H-6.

**R-5, consistency: inconsistent and consistent** (C-1's k1 and k2).

```json
{"format": "ve-calc@0",
 "values": [
   {"name": "a", "words": "the first printed share", "stated": "0.4"},
   {"name": "b", "words": "the second printed share", "stated": "0.3"}],
 "claims": [
   {"id": "k1", "claim": ["consistent", ["a"], [["rounds", ["add", ["val", "a"], ["val", "b"]], "0.9"]]]},
   {"id": "k2", "claim": ["consistent", ["a"], [["lt", ["add", ["val", "a"], ["val", "b"]], ["lit", "0.66"]]]]}]}
```

```json
[{"status": "ok", "claim": "k1", "claim_id": "<hex64>", "kind": "consistent", "outcome": "fails", "reason": null,
  "witness": null, "refutation": {"output": 0, "enclosure": ["13/20", "3/4"]},
  "line": "<display>", "finding": null, "reproduction": null,
  "rests_on": [{"name": "a", "source": "stated", "support": null, "span": "unchecked"},
               {"name": "b", "source": "stated", "support": null, "span": "unchecked"}]},
 {"status": "ok", "claim": "k2", "claim_id": "<hex64>", "kind": "consistent", "outcome": "holds", "reason": null,
  "witness": [["a", "7/20"]], "refutation": null,
  "line": "<display>", "finding": null, "reproduction": null,
  "rests_on": [{"name": "a", "source": "stated", "support": null, "span": "unchecked"},
               {"name": "b", "source": "stated", "support": null, "span": "unchecked"}]}]
```

**R-6, identities: holds and fails** (H-1, and (x + y)² = x² + y²).

```json
{"format": "ve-calc@0",
 "values": [
   {"name": "path", "words": "the path length", "free": true},
   {"name": "light", "words": "the speed of light", "free": true},
   {"name": "speed", "words": "the speed", "free": true},
   {"name": "round_trip", "words": "the round-trip time",
    "defined": ["add", ["div", ["val", "path"], ["sub", ["val", "light"], ["val", "speed"]]],
                       ["div", ["val", "path"], ["add", ["val", "light"], ["val", "speed"]]]]},
   {"name": "closed_form", "words": "the closed-form time",
    "defined": ["div", ["mul", ["mul", ["lit", "2"], ["val", "path"]], ["val", "light"]],
                       ["sub", ["pow", ["val", "light"], 2], ["pow", ["val", "speed"], 2]]]},
   {"name": "x", "words": "the first unknown", "free": true},
   {"name": "y", "words": "the second unknown", "free": true}],
 "claims": [
   {"id": "h1", "claim": ["identity", ["val", "round_trip"], ["val", "closed_form"]]},
   {"id": "sq", "claim": ["identity", ["pow", ["add", ["val", "x"], ["val", "y"]], 2],
                                      ["add", ["pow", ["val", "x"], 2], ["pow", ["val", "y"], 2]]]}]}
```

```json
[{"status": "ok", "claim": "h1", "claim_id": "<hex64>", "kind": "identity", "outcome": "holds", "reason": null,
  "point": null, "sides": null,
  "line": "For all values of the unknowns for which both sides are defined, the round-trip time equals the closed-form time.",
  "finding": null, "reproduction": null,
  "rests_on": [{"name": "path", "source": "free", "support": null, "span": "unchecked"},
               {"name": "light", "source": "free", "support": null, "span": "unchecked"},
               {"name": "speed", "source": "free", "support": null, "span": "unchecked"}]},
 {"status": "ok", "claim": "sq", "claim_id": "<hex64>", "kind": "identity", "outcome": "fails", "reason": null,
  "point": [["x", "1"], ["y", "1"]], "sides": ["4", "2"],
  "line": "For all values of the unknowns for which both sides are defined, the square of the sum of the first unknown and the second unknown equals the sum of the square of the first unknown and the square of the second unknown.",
  "finding": null, "reproduction": null,
  "rests_on": [{"name": "x", "source": "free", "support": null, "span": "unchecked"},
               {"name": "y", "source": "free", "support": null, "span": "unchecked"}]}]
```

`sq`'s point is the plan's (ME-9's fixture a = b = 1); ME-9 pins the search order that finds it.

**R-7, statements: holds, fails with its deciding value, and stated, not decided** (M-1, M-5, M-3).

```json
{"format": "ve-arith@0",
 "definitions": [
   {"name": "prime", "kind": "predicate", "params": ["p"], "words": "is prime",
    "body": ["and", ["le", ["num", "2"], ["var", "p"]],
             ["not", ["ex-from-to", "d", ["num", "2"], ["sub", ["var", "p"], ["num", "1"]],
                      ["dvd", ["var", "d"], ["var", "p"]]]]]}],
 "statements": [
   {"id": "m1", "formula": ["all-from-to", "n", ["num", "1"], ["num", "161"],
      ["ex-from-to", "p", ["add", ["var", "n"], ["num", "1"]], ["mul", ["num", "2"], ["var", "n"]],
         ["call", "prime", [["var", "p"]]]]]},
   {"id": "m5", "formula": ["all-from-to", "n", ["num", "1"], ["num", "161"],
      ["ex-from-to", "p", ["add", ["var", "n"], ["num", "1"]],
         ["sub", ["mul", ["num", "2"], ["var", "n"]], ["num", "1"]], ["call", "prime", [["var", "p"]]]]]},
   {"id": "m3", "formula": ["all-nat", "n", ["imp", ["le", ["num", "1"], ["var", "n"]],
      ["ex-nat", "p", ["and", ["call", "prime", [["var", "p"]]],
         ["and", ["lt", ["var", "n"], ["var", "p"]], ["le", ["var", "p"], ["mul", ["num", "2"], ["var", "n"]]]]]]]]}]}
```

```json
[{"status": "ok", "statement": "m1", "statement_id": "<hex64>", "outcome": "holds", "reason": null, "bounded": true,
  "units": 17011, "deciding": null,
  "line": "For every whole number n from 1 through 161, there is an integer p from the sum of n and 1 through twice n such that p is prime.",
  "import": null, "rests_on": []},
 {"status": "ok", "statement": "m5", "statement_id": "<hex64>", "outcome": "fails", "reason": null, "bounded": true,
  "units": 2, "deciding": {"variable": "n", "value": "1"}, "line": "<display>", "import": null, "rests_on": []},
 {"status": "ok", "statement": "m3", "statement_id": "<hex64>", "outcome": "unknown",
  "reason": "stated, not decided: a quantifier has no bound", "bounded": false, "units": null, "deciding": null,
  "line": "For every whole number n, if n is at least 1, then there is a whole number p such that p is prime, n is less than p, and p is at most twice n.",
  "import": null, "rests_on": []}]
```

The decoder gives exactly the stub's formulas (`FxArith.m1 161`, `FxArith.m5`, `bertrand` and `primeBody` in de Bruijn
form), so the units are the stub's 17,011 and 2.

**R-8, an exhausted budget** (M-4x): R-7's definitions, the statement m1 alone and `"budget": 1000`. Its row is
`{"status": "ok", "statement": "m1", "statement_id": "<hex64>", "outcome": "unknown", "reason": "unknown: the budget
of 1,000 evaluation steps ran out", "bounded": true, "units": null, "deciding": null, "line": <as in R-7>,
"import": null, "rests_on": []}`; its `statement_id` equals R-7's m1's, since the budget is not part of it.

**R-9, an imported statement** (ME-13; M-3 with the EX-1 record): R-7's case with m3 alone and
`"imports": [{"statement": "m3", "record": {"statement_id": "<hex64 of m3>", "means_digest": "<currentMeansDigest>",
"project": "imports/mathlib", "project_rev": "<rev>", "toolchain": "leanprover/lean4:v4.24.0", "mathlib_rev": "<rev>",
"declaration": "VEImports.bertrand_holds", "check_digest": "<sha256 of the check file>", "axioms": ["propext",
"Classical.choice", "Quot.sound"]}}]`. Its row has `"outcome": "holds"`, `"bounded": false`, `"units": null`,
`"import": "import:imports/mathlib@<rev>/VEImports.bertrand_holds"` and `"rests_on": ["Proved in Lean with Mathlib at
revision <rev>, declaration VEImports.bertrand_holds; VE did not replay this proof."]`; the placeholders are EX-1's.

**T-3** (13.2) is the counted-value request: T-1's bytes registered under their SHA-256, `"data": [{"handle":
"<sha256 of T-1's bytes>", "format": "csv", "columns": {"judge": "text", "approved": "bool", "score": "number"}}]`,
its three values and five claims; its rows are claim rows as in R-1 and R-2, with the outcomes of 13.3.

**R-10, derivations, consistency checks and identities: unknown and undefined** (J3, draft 3). Three requests, one
per kind, so that each runs in its own batch (plan 4.4a). Each is the common part below with its own values and
checks added: R-10a adds the free value t and the derivations, R-10b the stated value a and the consistency checks,
R-10c the free value t and the identities. The common part is T-3's data declaration, budget and two counted values:

```json
{"format": "ve-calc@0",
 "data": [{"handle": "<sha256 of T-1's bytes>", "format": "csv",
           "columns": {"judge": "text", "approved": "bool", "score": "number"}}],
 "budget": 6,
 "values": [
   {"name": "approved_32b", "words": "the approved 32B count",
    "counted": {"data": "<sha256 of T-1's bytes>", "filter": ["and", ["is", "judge", "32B"], ["true", "approved"]],
                "aggregate": "count"}},
   {"name": "mean_7b", "words": "the mean 7B score",
    "counted": {"data": "<sha256 of T-1's bytes>", "filter": ["is", "judge", "7B"], "aggregate": ["mean", "score"]}}]}
```

R-10a (ME-5) appends `{"name": "t", "words": "the threshold", "free": true}` to `values` and adds:

```json
{"premises": [
   {"id": "p1", "claim": ["lt", ["val", "t"], ["val", "approved_32b"]], "support": "assumption"},
   {"id": "p2", "claim": ["lt", ["val", "t"], ["val", "mean_7b"]], "support": "assumption"}],
 "claims": [
   {"id": "f_unknown", "claim": ["follows", ["lt", ["val", "t"], ["lit", "2"]], ["p1"], []]},
   {"id": "f_undefined", "claim": ["follows", ["lt", ["val", "t"], ["lit", "2"]], ["p2"], []]}]}
```

```json
[{"status": "ok", "claim": "f_unknown", "claim_id": "<hex64>", "kind": "follows", "outcome": "unknown",
  "reason": "unknown: the budget of 6 evaluation steps ran out", "certificate": null, "counterexample": null,
  "line": "Assume the following. 1. The threshold is less than the approved 32B count. From these, it follows that the threshold is less than 2.",
  "finding": null, "reproduction": null,
  "rests_on": [{"premise": "p1", "support": "assumption"},
               {"name": "approved_32b", "source": "counted", "support": null, "span": "unchecked"},
               {"name": "t", "source": "free", "support": null, "span": "unchecked"}]},
 {"status": "ok", "claim": "f_undefined", "claim_id": "<hex64>", "kind": "follows", "outcome": "undefined",
  "reason": null, "certificate": null, "counterexample": null,
  "line": "Assume the following. 1. The threshold is less than the mean 7B score. From these, it follows that the threshold is less than 2.",
  "finding": null, "reproduction": null,
  "rests_on": [{"premise": "p2", "support": "assumption"},
               {"name": "mean_7b", "source": "counted", "support": null, "span": "unchecked"},
               {"name": "t", "source": "free", "support": null, "span": "unchecked"}]}]
```

R-10b (ME-8) appends `{"name": "a", "words": "the printed share", "stated": "0.4"}` to `values` and adds:

```json
{"claims": [
   {"id": "k_unknown", "claim": ["consistent", ["a"], [["lt", ["val", "a"], ["val", "approved_32b"]]]]},
   {"id": "k_undefined", "claim": ["consistent", ["a"], [["lt", ["val", "a"], ["val", "mean_7b"]]]]}]}
```

```json
[{"status": "ok", "claim": "k_unknown", "claim_id": "<hex64>", "kind": "consistent", "outcome": "unknown",
  "reason": "unknown: the budget of 6 evaluation steps ran out", "witness": null, "refutation": null,
  "line": "<display>", "finding": null, "reproduction": null,
  "rests_on": [{"name": "approved_32b", "source": "counted", "support": null, "span": "unchecked"},
               {"name": "a", "source": "stated", "support": null, "span": "unchecked"}]},
 {"status": "ok", "claim": "k_undefined", "claim_id": "<hex64>", "kind": "consistent", "outcome": "undefined",
  "reason": null, "witness": null, "refutation": null,
  "line": "<display>", "finding": null, "reproduction": null,
  "rests_on": [{"name": "mean_7b", "source": "counted", "support": null, "span": "unchecked"},
               {"name": "a", "source": "stated", "support": null, "span": "unchecked"}]}]
```

R-10c (ME-9) appends t as in R-10a and adds:

```json
{"claims": [
   {"id": "i_unknown", "claim": ["identity", ["add", ["val", "t"], ["val", "approved_32b"]],
                                             ["add", ["val", "approved_32b"], ["val", "t"]]]},
   {"id": "i_undefined", "claim": ["identity", ["add", ["val", "t"], ["val", "mean_7b"]], ["val", "t"]]}]}
```

```json
[{"status": "ok", "claim": "i_unknown", "claim_id": "<hex64>", "kind": "identity", "outcome": "unknown",
  "reason": "unknown: the budget of 6 evaluation steps ran out", "point": null, "sides": null,
  "line": "For all values of the unknowns for which both sides are defined, the sum of the threshold and the approved 32B count equals the sum of the approved 32B count and the threshold.",
  "finding": null, "reproduction": null,
  "rests_on": [{"name": "approved_32b", "source": "counted", "support": null, "span": "unchecked"},
               {"name": "t", "source": "free", "support": null, "span": "unchecked"}]},
 {"status": "ok", "claim": "i_undefined", "claim_id": "<hex64>", "kind": "identity", "outcome": "undefined",
  "reason": null, "point": null, "sides": null,
  "line": "For all values of the unknowns for which both sides are defined, the sum of the threshold and the mean 7B score equals the threshold.",
  "finding": null, "reproduction": null,
  "rests_on": [{"name": "mean_7b", "source": "counted", "support": null, "span": "unchecked"},
               {"name": "t", "source": "free", "support": null, "span": "unchecked"}]}]
```

No outcome depends on a search order: 2.7 and 4.2 decide them. At budget 6 `approved_32b` is exhausted and `mean_7b`
completes with no value (T-3's visit counts: `approved_32b` needs at least ten visits, `mean_7b` five, and T-1 has no
7B row). Each check's one faulting read is in its lowering, so the `*_unknown` checks inline to `.error .exhausted`
and are `unknown (limit .evaluations)` with `Check.UnknownCause`'s cause, `val approved_32b` reading an exhausted
counted value (`Expr.inline_exhausted`); the `*_undefined` checks inline to `.error .undefined` and are `undefined`,
since `val mean_7b` denotes nothing whatever values the kept names take (`Expr.inline_undefined`). Without `budget`,
`approved_32b` is 1 (T-3), so f_unknown, k_unknown and i_unknown hold (t < 1 gives t < 2; a = 2/5, the printed value,
is a witness; t + 1 = 1 + t), and the `*_undefined` rows are unchanged.

## 14. Limits and trust

| Limit | Value | When exceeded |
|---|---|---|
| JSON nodes, depth, values, claims, premises | 10,000; 64; 512; 512; 512 | refused (`ResourceLimit`) |
| exponents (`pow`, `sci`) | 64 | refused |
| literal digits | 40 (W6's `maxNumeralChars`) | refused |
| `binomial-tail` trials | 1,000 | refused (`ResourceLimit`) |
| exact value digits | 4,096 in numerator or denominator | every check that needs the value unknown (`limit .digits`; for derivations, consistency checks and identities only in the lowering, 2.7) |
| table bytes, rows, columns | 16 MB per handle (the service's line cap); 1,000,000; 64 | refused |
| table evaluation | 1,000,000 (row, filter node) visits per counted value, or the case's smaller `budget` | every check reading it unknown (`limit .evaluations`), through definitions too |
| derivation search | 64 facts, 16 unknowns, 10,000 combination steps | unknown (`limit .derivationSteps`) |
| consistency search | 4,096 candidate points | unknown (`limit .witnessPoints`) |
| identity normal form | 10,000 monomials | unknown (`limit .polyTerms`) |
| sign flips | 16 values | refused (`SignFlipTooLong`) |
| `arith` evaluation | 1,000,000 formula-node visits per statement, or the case's smaller `budget` | unknown (`limit .evaluations`) |
| `arith` JSON nodes, depth, definitions, statements, numerals, names | 10,000; 64; 512; 512; 40 digits; 64 bytes | refused (`ResourceLimit`) |

Trusted and not certified: SHA-256 (as for the risk log); the decoders (pinned in `ve/assurance-manifest.json` by hand);
the truth of stated values and data files (a digest binds a claim to bytes, not bytes to the world); the
applicability of a physical law or a statistical model; a stated quantile; software reproduction (always unknown);
an imported proof beyond the pinned external build's acceptance. Every new trusted Lean line needs a signed allowance
and a ROADMAP trust-cost line (plan 5).

## 15. The plan-review edits, statement by statement

The edits of the plan review (`manage-agents/debates/design-math-evidence/`), as draft 3 carries them.

| Edit | Statements | Fixtures |
|---|---|---|
| A1 operational outcome | `Outcome`, `UnknownReason` (1.5); `Claim.run`, `run_decided`, `run_unknown`, `run_complete` (2.4); `Check.UnknownCause`, `Check.OutcomeMeans`, `Run.row_sound`, `Run.verdict_sound`, `Run.unknown_named` (3.4); `arithOutcome` and its theorems (12.2); `Case.outcome_unknown` (12.5) | V-11, M-1b, M-4x, T-3, R-2, R-8, R-10 |
| A2 links in counterexamples | `Counterexample.check_sound`, `counterexample_of_check`, `HasCounterexample` (5) | H-6a, H-6n, R-4 |
| A3 import binding | `Import`, `Import.admit_sound`, `checkSource`, `currentMeansDigest` (12.4); `Case.import_row`, `Run.import_sound` (12.5), replacing draft 1's `report_import_labelled` | ME-13's seeded bug (plan), R-9 |
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

Draft 2's choices, each made to carry a statement-review edit (17):

- **C12 (J2).** A counted value's mathematical value is held as a `Thunk`. Stored as a plain value, the decoder would
  compute every aggregate outside the budget, and the budget would never bound the work.
- **C13 (J2).** The budget applies to each counted value on its own, as draft 1's `Agg.runB limit` already did; the
  case-level `budget` field had not said so.
- **C14 (J3).** A derivation is the claim form `["follows", …]`, and its premises are a separate `premises` list
  with their supports. Draft 1 named premises by claim ids; read as rows, they read free values, would be
  `undefined`, and would make their document unit UNFORMALISED (10). The conclusion is one order comparison, since
  `Derivation.check` concludes one fact; premises are comparisons and ranges.
- **C15 (J3).** Statistics read names of stated or counted values, not expressions, so `Expr` stays a plain
  inductive type. Inlining therefore evaluates a statistic that reads no kept name, and the decoder refuses one that
  mixes inputs with other names. The sign-flip p has no table-column form, since its 16-value limit is checked at
  decode.
- **C16 (J5).** The square root of a negative value is undefined, not false: J5's rule for a value outside a
  statistic's domain.
- **C17.** GRIM (`mean_grain_refutes`) has no route form (8.1): a consistency check has no inputs that range over
  whole numbers, and adding them is a design change beyond the review's edits. The plan's ME-8 fixture for GRIM is a
  `#guard` (S-3).
- **C18 (J1).** A consistency check's canonical form carries its inputs' printed numbers and its rule. The stated
  values' canonical literals drop the written places ("0.30" and "0.3" are one value), but an input's interval
  depends on them, so without this two different checks would share an identity.
- **C19 (J3).** Two decode limits are new: 512 premises, and 1,000 `binomial-tail` trials, whose binomial
  coefficients are computed before the digit guard.
- **C20 (J3).** `arith@0`'s wire names its variables; the identity uses de Bruijn indices, so renaming a variable
  keeps it, and shadowing is refused so that the rendered English has one reading.
- **C21 (J3).** The deciding value is reported for the outermost bounded quantifier only: enough for M-5's "at
  n = 1" and plan 2.13's "false with the deciding values" at the top level.
- **C22 (J3).** An unbounded statement with an admitted import is a `holds` row whose residual line names the import,
  as draft 1's `Report.Accepted` had it; VE never decides it.
- **C23.** New diagnostics: `UnknownPremise`, `ConsistencyInput`, `ConsistencyName`, `PlacesMismatch`,
  `IsExpression`, `UnscopedVariable`, `ShadowedVariable` and `UnknownDefinition`; other refusals reuse draft 1's
  codes. Rows carry `status` and `kind`, like the service's other modes. `finding` is filled for a translated
  document's calculation content (ME-10) and is `null` in a standalone case: this is how draft 2 reads draft 1's "in
  translation".

Draft 3's choices, each made to carry a finding of the verification of draft 2 (17):

- **C24 (J2).** A derivation, consistency check or identity is unknown at the digit limit only in its lowering (2.7
  already said so), and the cause is the claims' one, `Expr.Overflows` of one of its expressions
  (`Expr.inline_tooLarge`, `Check.UnknownCause`). The checkers' own arithmetic gives no digit-limit unknown.
- **C25 (J3).** R-10 shows each kind's unknown row through budget exhaustion, the one cause this specification
  decides without a search order; the kinds' own reasons (`derivationInconclusive`, `consistencyInconclusive`,
  `identityNotShown` and the search limits) depend on search orders the batches pin. R-10 is three requests, so that
  each batch runs its own kind before the others land, and its counted values tie it to ME-4 (plan 4.4a).
- **C26 (J3).** The linearity rule of 3.1 judges a premise's form, every name other than a free value being a
  constant, so a premise whose counted value is exhausted or undefined gets its row (R-10a) rather than a refusal;
  draft 2 did not say what the decoder does when the lowering meets a fault.

## 17. The statement-review edits and the bounded re-check

The converged position (`manage-agents/debates/math-evidence-spec/`, round 2) is Fable's J1-J11 with Astra's
refinements; both reviewers agreed to a bounded re-check of the changed sections and the new fixtures, not a fresh
full review.

The verification of draft 2 (`manage-agents/math-evidence-p3ver1.final.md`, FAIL narrowly) found all eleven edits
present, with Astra's refinements, and the hand-computed numbers it checked correct (S-5's 7,424, C-1, T-1, T-3, R-3's
weights, R-4 and R-6). It asked for three edits, which draft 3 makes: (1) J2: `Run.unknown_named` had dropped
`Overflows` from the claims' digit-limit unknown, and 3.4 let derivations, consistency checks and identities be
unknown at the digit limit with no cause; both now conclude `Check.UnknownCause`. (2) J3: no fixture showed an
unknown or undefined derivation, consistency check or identity; R-10 does. (3) Draft-2 choices that go beyond
J1-J11 must be accepted explicitly by both reviewers; item 7 below names them.

| Edit | What draft 2 changed (draft 3's additions marked) | Statements | Fixtures |
|---|---|---|---|
| J1 (A1) signed integers in identities | canonical decimal strings for printed places and unit exponents; the frozen encoder unchanged; its key sorting stated | 3.3; 12.5's identity | I-1, I-2 |
| J2 (A2) exhaustion | `Counted`, `Source.counted value run`, `Val.exhausted`, `NameExhausted`, `ReadsExhausted`; `run_unknown` disjunctive; `runCounted` takes the budget; `counted_exhausted`; draft 3: `Check.UnknownCause` (the claims' disjunction, and a cause at the digit limit and at the budget for every other kind), concluded by `Run.unknown_named` and used by `Check.OutcomeMeans`; `Expr.inline_tooLarge` | 2.3, 2.4, 2.7, 3.4, 4.2, 4.3 | T-3 (exhausted count, directly and through a definition, beside an empty mean); draft 3: R-10 (an exhausted count read by each other kind) |
| J3 (A3, E1, E6) every kind's contract | full `Expr` and `Claim` (ME-7's constructors); `Check`, `Check.OutcomeMeans`, `Check.run_sound`, `Run.row_sound`; the lowering `Expr.inline` (2.7) and `Claim.facts` (5); `Follows`, `IsIdentity` and their bridge theorems; 12.5's `arith@0` wire, identity, rows, `runMode_arith`, encoder theorem, refusals and deciding values; draft 3: 3.1's linearity rule needs no value (C26) | 2.1, 2.2, 2.7, 3.1, 3.4, 5, 8.2, 12.5 | R-1 to R-10 (13.6): every kind with every outcome; draft 3: R-10, the unknown and undefined rows of derivations, consistency checks and identities |
| J4 (A4) one consistency proposition | `Consistent`, one name rule (`ConsistencyName`), witness and refutations proved against it over one lowering (draft 1's `witness_sound` and `inconsistent_of_enclosure` become `consistent_of_witness` and `inconsistent_of_refutation`); inputs kept, never replaced by their printed values (Astra) | 8.1 | C-1, R-5 |
| J5 (A5) statistical domains | `Stat.run`, `Stat.minLength`, `Stat.run_isSome`, `Denotes.binom`'s 0 ≤ p ≤ 1, `binomialTail_unit`, undefined outside the domain | 2.1, 2.2, 7 | S-5 |
| J6 (A6) dependencies | ME-12 follows ME-1 | 1; plan 0, 6 | — |
| J7 (E2) "Let … be"; "A is E" | rewrites use "Let … be"; premises use "equals"; `IsExpression`; "be" reserved | 11.1, 11.2 | 11.2's refused sentences |
| J8 (E3) places | `PlacesMismatch`; negative places only as "times ten to the power" | 11.1 | 11.2's refused sentences |
| J9 (E4) negated filters | `isNotText`, `notEquals`, `isFalse` replace `not`, each needing a cell of its type (Astra); `Filter.bool_atoms`, `Filter.negated_typed` | 4.1, 11.1 | T-1's absent and mistyped cells |
| J10 (E5) square links shown | each link is two numbered premises, the square equation and the root's nonnegativity, and a residual line; the wire keeps links apart from premises (Astra) | 5, 3.4's `rests_on`, 11.1 | R-3 |
| J11 (E7) small fixes | V-7 names the fourth row; 4.4's grammar admits "0"; EX-1's bridge lemma declared before use | 4.4, 12.4, 13.3 | V-7 |

**The re-check list.** PASS when each holds:

1. Drafts 2's and 3's statements type-check in the stub with Lean v4.24.0 against `main`'s `lean/` tree (`sorry`
   proofs), and each *by hand* number in 13.3 and 13.6 is recomputed there with `#eval`: S-5, C-1, T-1's added rows,
   T-3, I-1 and I-2's canonical texts and the "Natural number expected" contrast, M-5's deciding value, and R-1 to
   R-10.
2. J1: every canonical case and environment hashes with the unchanged frozen encoder; `ve-units@1` identities do not
   move.
3. J2: no runner theorem allows an unknown without its named cause: `Run.unknown_named` and `Check.OutcomeMeans`
   conclude `Check.UnknownCause`, which for a claim row is `Claim.run_unknown`'s disjunction and gives every other
   kind a cause at the digit limit (`Expr.inline_tooLarge`) and at the budget; exhaustion propagates through
   definitions; the first fault still decides.
4. J3: every check kind and every outcome has its `OutcomeMeans` clause; the lowering theorems connect each checker to
   its kind's meaning; R-1 to R-10 show every kind with every outcome; 12.5's rows cover holds, fails and unknown, and
   its refusals cover unscoped variables and unknown calls.
5. J4: the witness and the refutations are proved against the one `Consistent`, and C-1's three checks come out as
   13.3 says.
6. J5 to J11 as the table above, each with its fixture.
7. Section 16's choices C12 to C26 are acceptable, or the reviewers name the edit. Both reviewers accept explicitly,
   by name, the draft-2 changes that the verification of draft 2 found beyond J1-J11: C14 and C15 (the derivation and
   statistics wire forms redesigned: `["follows", …]` with a `premises` list, statistics over names), C17 (GRIM loses
   ME-8's route fixture and stays a `#guard`), C19 (the new refusal of more than 1,000 `binomial-tail` trials, beside
   the 512-premise limit), C20 (the new `ShadowedVariable` refusal) and C21 (only the outermost bounded quantifier's
   deciding value is reported). A reviewer who does not accept one names the edit, and the next draft makes it.
8. (Draft 4, phase 1.) The fixtures phase 1 changed or added are as 13.2 and 13.3 give them, recomputed in the stub
   with `#eval`: H-4 and H-5 over sq = 10⁻⁸ (and no fixture of the source reads v/V = 10⁻⁴; H-7u is marked
   constructed); H-5b; H-9's 104 claims and H-9n; V-7b's six multiples of 1/4,096; M-4b at x = T − 1 and T (its
   bounds are ME-12's); DL-1 to DL-4. Each source row's span is the one `fixture-anchors.json` records against the
   pinned source's SHA-256. No Lean statement changed in draft 4, so items 1 to 7 are unchanged.

**Phase 1 (draft 4).** ME-0's pre-registered fixture check (P4) failed: of 32 fixtures in scope, 14 were ANCHORED, 9
RE-WORDED, 6 NOT A QUOTE and 3 CHANGED (H-4, H-5, H-9), none ABSENT. Draft 4 rewrites the three to the source, adds
the fixtures phase 1 found (H-5b, V-7b, M-4b, DL-1 to DL-4), and records every anchor in 13.2. The results of H-4 and
H-5 do not change; H-9's does, from "not presumed" to 104 claims that hold.
