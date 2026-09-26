import VE.Core.Syntax

namespace VE.Core
universe u

def namedEdges {α : Type u} (rows : List (List α)) : List (α × α) :=
  rows.filterMap fun row => match row with
    | [a, b] => some (a, b)
    | _ => none

theorem mem_namedEdges {α : Type u} (rows : List (List α)) (a b : α) :
    (a, b) ∈ namedEdges rows ↔ [a, b] ∈ rows := by
  simp only [namedEdges, List.mem_filterMap]
  constructor
  · rintro ⟨row, hr, he⟩
    split at he
    next x y => cases he; exact hr
    next => simp at he
  · intro h; exact ⟨[a, b], h, rfl⟩

def bodyEdges {α : Type u} (domain : List α) (f : α → α → Bool) : List (α × α) :=
  domain.flatMap (fun x => (domain.filter (f x)).map (x, ·))

theorem mem_bodyEdges {α : Type u} (domain : List α) (f : α → α → Bool) (a b : α) :
    (a, b) ∈ bodyEdges domain f ↔ a ∈ domain ∧ b ∈ domain ∧ f a b = true := by
  simp [bodyEdges, List.mem_flatMap, List.mem_map, List.mem_filter]

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
  | .atom p ts => match ts.mapM (·.denote M.asStructure ρ) with
      | some vs => decide (vs ∈ M.relations p)
      | none => false
  | .eq t u => match t.denote M.asStructure ρ, u.denote M.asStructure ρ with
      | some v, some w => decide (v = w)
      | _, _ => false
  | .not a => !(a.eval M ρ)
  | .and a b => a.eval M ρ && b.eval M ρ
  | .or a b => a.eval M ρ || b.eval M ρ
  | .implies a b => !(a.eval M ρ) || b.eval M ρ
  | .all s a => (M.domains s).all (fun v => a.eval M (v :: ρ))
  | .ex s a => (M.domains s).any (fun v => a.eval M (v :: ρ))

  | .reachNamed k p t u => match t.denote M.asStructure ρ, u.denote M.asStructure ρ with
      | some v, some w => reachEval k (namedEdges (M.relations p)) v w
      | _, _ => false
  | .reachBody k s a t u => match t.denote M.asStructure ρ, u.denote M.asStructure ρ with
      | some v, some w => reachEval k
          (bodyEdges (M.domains s) (fun x y => a.eval M (y :: x :: ρ))) v w
      | _, _ => false

/-- Equality of base relations transports finite paths and both closures. -/
theorem reachable_congr {α : Type u} (k : Kind) (R Q : α → α → Prop)
    (h : ∀ x y, R x y ↔ Q x y) (a b : α) :
    Reachable k R a b ↔ Reachable k Q a b := by
  have he : R = Q := funext (fun x => funext (fun y => propext (h x y)))
  rw [he]

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
  | atom p ts =>
    simp only [Formula.eval, Formula.denote]
    cases ht : ts.mapM (·.denote M.asStructure ρ) <;> simp [FiniteModel.asStructure]
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

  | reachNamed k p t u =>
    simp only [Formula.eval, Formula.denote]
    cases ht : t.denote M.asStructure ρ <;>
      cases hu : u.denote M.asStructure ρ <;> simp
    case some.some v w =>
      rw [reachEval_iff]
      exact reachable_congr k _ _ (fun x y => mem_namedEdges _ x y) v w
  | reachBody k s a t u ih =>
    simp only [Formula.eval, Formula.denote]
    cases ht : t.denote M.asStructure ρ <;>
      cases hu : u.denote M.asStructure ρ <;> simp
    case some.some v w =>
      rw [reachEval_iff]
      exact reachable_congr k _ _ (fun x y => by
        simp [mem_bodyEdges, ih, FiniteModel.asStructure]) v w

theorem eval_false_iff_not_denote {α : Type u} [DecidableEq α] (M : FiniteModel α)
    (ρ : List α) (a : Formula) :
    a.eval M ρ = false ↔ ¬ a.denote M.asStructure ρ := by
  rw [Bool.eq_false_iff]
  exact not_congr (eval_iff_denote M ρ a)

end VE.Core
