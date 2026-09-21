import VE.Order.Semantics

namespace VE.Order
universe u

-- The toolchain supplies Sum's Boolean equality but no corresponding law.
local instance {α : Type u} [DecidableEq α] : LawfulBEq (Value α) where
  rfl := by intro a; cases a <;> simp [BEq.beq, Sum.instBEq.beq]
  eq_of_beq := by intro a b h; cases a <;> cases b <;> simp_all [BEq.beq, Sum.instBEq.beq]

/-- A finite presentation, not a finite integer domain. Only user domains are
listed. Constants and finite relation rows can contain arbitrary actual Int
values; unlisted rows are false, including rows containing unlisted integers. -/
structure FiniteModel (α : Type u) where
  domains : String → List α
  constants : String → Option (Value α)
  relations : String → List (List (Value α))

abbrev FiniteModel.asStructure {α : Type u} (M : FiniteModel α) : Structure.{u} where
  Carrier := α
  objects s v := v ∈ M.domains s
  constant := M.constants
  relation p vs := vs ∈ M.relations p

/-- This is the semantic validity obligation for supplied finite data. -/
def FiniteModel.Valid {α : Type u} (M : FiniteModel α) (E : Environment) : Prop :=
  M.asStructure.Admissible E

def compareEval {α : Type u} (r : Int → Int → Bool) (x y : Option (Value α)) : Bool :=
  match x, y with
  | some (.inr a), some (.inr b) => r a b
  | _, _ => false

theorem compareEval_iff {α : Type u} (r : Int → Int → Bool) (R : Int → Int → Prop)
    (h : ∀ a b, r a b = true ↔ R a b) (x y : Option (Value α)) :
    compareEval r x y = true ↔ Compare R x y := by
  cases x with
  | none => simp [compareEval, Compare]
  | some x => cases x <;> cases y with
    | none => simp [compareEval, Compare]
    | some y => cases y <;> simp [compareEval, Compare, h]

/-- A total structurally recursive evaluator, with no search or work-budget
failure conflated with false. Budgeted production behavior is outside this theorem. -/
def Formula.eval {α : Type u} [DecidableEq α] (M : FiniteModel α)
    (ρ : List (Value α)) : Formula → Bool
  | .top => true
  | .bottom => false
  | .unary p t => match t.denote M.asStructure ρ with
      | some v => decide ([v] ∈ M.relations p)
      | none => false
  | .binary p t u => match t.denote M.asStructure ρ, u.denote M.asStructure ρ with
      | some v, some w => decide ([v, w] ∈ M.relations p)
      | _, _ => false
  | .eq t u => match t.denote M.asStructure ρ, u.denote M.asStructure ρ with
      | some v, some w => decide (v = w)
      | _, _ => false
  | .lt t u => compareEval (fun x y => decide (x < y))
      (t.denote M.asStructure ρ) (u.denote M.asStructure ρ)
  | .le t u => compareEval (fun x y => decide (x ≤ y))
      (t.denote M.asStructure ρ) (u.denote M.asStructure ρ)
  | .not a => !(a.eval M ρ)
  | .and a b => a.eval M ρ && b.eval M ρ
  | .or a b => a.eval M ρ || b.eval M ρ
  | .implies a b => !(a.eval M ρ) || b.eval M ρ
  | .all s a => (M.domains s).all (fun v => a.eval M (.inl v :: ρ))
  | .ex s a => (M.domains s).any (fun v => a.eval M (.inl v :: ρ))

/-- P6, for every raw formula and valuation; in particular for all typed closed
claims in valid finite structures. Denotation was defined independently of eval. -/
theorem eval_iff_denote {α : Type u} [DecidableEq α] (M : FiniteModel α)
    (ρ : List (Value α)) (a : Formula) :
    a.eval M ρ = true ↔ a.denote M.asStructure ρ := by
  induction a generalizing ρ with
  | top | bottom => simp [Formula.eval, Formula.denote]
  | unary p t =>
    simp only [Formula.eval, Formula.denote]
    cases ht : t.denote M.asStructure ρ <;> simp [FiniteModel.asStructure]
  | binary p t u =>
    simp only [Formula.eval, Formula.denote]
    cases ht : t.denote M.asStructure ρ <;>
      cases hu : u.denote M.asStructure ρ <;> simp [FiniteModel.asStructure]
  | eq t u =>
    simp only [Formula.eval, Formula.denote]
    cases ht : t.denote M.asStructure ρ <;>
      cases hu : u.denote M.asStructure ρ <;> simp <;> exact eq_comm
  | lt t u => exact compareEval_iff _ _ (fun _ _ => decide_eq_true_iff) _ _
  | le t u => exact compareEval_iff _ _ (fun _ _ => decide_eq_true_iff) _ _
  | not a ih => simp [Formula.eval, Formula.denote, Bool.eq_false_iff, ih]
  | and a b ia ib | or a b ia ib => simp [Formula.eval, Formula.denote, ia, ib]
  | implies a b ia ib =>
    classical
    simp [Formula.eval, Formula.denote, Bool.eq_false_iff, ia, ib]
    constructor
    · intro h ha
      rcases h with hn | hb
      · exact False.elim (hn ha)
      · exact hb
    · intro h
      by_cases ha : a.denote M.asStructure ρ
      · exact Or.inr (h ha)
      · exact Or.inl ha
  | all s a ih => simp [Formula.eval, Formula.denote, FiniteModel.asStructure, ih]
  | ex s a ih => simp [Formula.eval, Formula.denote, FiniteModel.asStructure, ih]

theorem eval_false_iff_not_denote {α : Type u} [DecidableEq α] (M : FiniteModel α)
    (ρ : List (Value α)) (a : Formula) :
    a.eval M ρ = false ↔ ¬ a.denote M.asStructure ρ := by
  rw [Bool.eq_false_iff]
  exact not_congr (eval_iff_denote M ρ a)


end VE.Order
