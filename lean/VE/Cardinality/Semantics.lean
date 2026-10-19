import VE.Cardinality.Syntax

/-! The meaning of `cardinality@0` statements, stated without erasure (docs/spec/quantities.md 3.3).

A count is the length of a duplicate-free list of exactly the counted objects, as `VE.Time.expand_atLeast_iff`
states counts; counts stay integers. Every proportion requires a nonempty population, as a rounding or a percentage requires a
positive denominator. Rounding is `VE.Numbers.RoundsTo` under the sentence's own tie rule; this track has no rounding
definition. -/
namespace VE.Cardinality
open VE.Time (TStructure)
universe u v

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

end VE.Cardinality
