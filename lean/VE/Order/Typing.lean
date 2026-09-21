import VE.Order.Syntax

namespace VE.Order

/-- The executable checker recognizes exactly the independent typing predicate. -/
theorem check_iff_wellFormed (E : Environment) (Γ : List SortName) (a : Formula) :
    a.check E Γ = true ↔ a.WellFormed E Γ := by
  induction a generalizing Γ with
  | top | bottom => simp [Formula.check, Formula.WellFormed]
  | unary p t =>
    simp only [Formula.check, Formula.WellFormed]
    cases hp : E.predicates p with
    | none => simp
    | some ss =>
      cases ss with
      | nil => simp
      | cons s ss =>
        cases ss with
        | nil => cases ht : t.sortOf E Γ <;> simp_all <;> exact eq_comm
        | cons r ss => simp
  | binary p t u =>
    simp only [Formula.check, Formula.WellFormed]
    cases hp : E.predicates p with
    | none => simp
    | some ss =>
      cases ss with
      | nil => simp
      | cons s ss =>
        cases ss with
        | nil => simp
        | cons r ss =>
          cases ss with
          | nil => cases ht : t.sortOf E Γ <;> cases hu : u.sortOf E Γ <;>
              simp_all
          | cons q ss => simp
  | eq t u =>
    simp only [Formula.check, Formula.WellFormed]
    cases ht : t.sortOf E Γ <;> cases hu : u.sortOf E Γ <;> simp <;> exact eq_comm
  | lt t u | le t u => simp [Formula.check, Formula.WellFormed]
  | not a ih => exact ih Γ
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    simp [Formula.check, Formula.WellFormed, ia, ib]
  | all s a ih | ex s a ih =>
    simp [Formula.check, Formula.WellFormed, ih, and_assoc]

end VE.Order
