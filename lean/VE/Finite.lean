import VE.Typing

namespace VE
universe u

/-- Finite domains and relation extensions. A finite structure uses only listed
entities, even when the ambient identifier type itself is infinite. Duplicate
list entries do not affect denotation; the wire validator rejects them. -/
structure FiniteModel (α : Type u) where
  domains : String → List α
  constants : String → Option α
  relations : String → List (List α)

def FiniteModel.asStructure {α : Type u} (M : FiniteModel α) : Structure.{u} where
  Carrier := α
  domain s v := v ∈ M.domains s
  constant := M.constants
  relation p vs := vs ∈ M.relations p

/-- This is the semantic validity obligation for supplied finite data. -/
def FiniteModel.Valid {α : Type u} (M : FiniteModel α) (E : Environment) : Prop :=
  M.asStructure.Admissible E

/-- A total structurally recursive evaluator, with no search or work-budget
failure conflated with false. Budgeted production behavior is outside this theorem. -/
def Formula.eval {α : Type u} [DecidableEq α] (M : FiniteModel α)
    (ρ : List α) : Formula → Bool
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
  | .not a => !(a.eval M ρ)
  | .and a b => a.eval M ρ && b.eval M ρ
  | .or a b => a.eval M ρ || b.eval M ρ
  | .implies a b => !(a.eval M ρ) || b.eval M ρ
  | .all s a => (M.domains s).all (fun v => a.eval M (v :: ρ))
  | .ex s a => (M.domains s).any (fun v => a.eval M (v :: ρ))

/-- P6, for every raw formula and valuation; in particular for all typed closed
claims in valid finite structures. Denotation was defined independently of eval. -/
theorem eval_iff_denote {α : Type u} [DecidableEq α] (M : FiniteModel α)
    (ρ : List α) (a : Formula) :
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
    (ρ : List α) (a : Formula) :
    a.eval M ρ = false ↔ ¬ a.denote M.asStructure ρ := by
  rw [Bool.eq_false_iff]
  exact not_congr (eval_iff_denote M ρ a)

def Document.eval {E : Environment} {α : Type u} [DecidableEq α]
    (d : Document E) (M : FiniteModel α) : Bool :=
  d.formulas.all (fun a => a.eval M [])

theorem document_eval_iff_denote {E : Environment} {α : Type u} [DecidableEq α]
    (d : Document E) (M : FiniteModel α) :
    d.eval M = true ↔ d.denote M.asStructure := by
  simp [Document.eval, Document.denote, eval_iff_denote]

end VE
