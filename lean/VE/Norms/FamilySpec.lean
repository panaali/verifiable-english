import VE.Norms.Family
import VE.Order.Conservativity

/-! # What the FOL view's dispatch test guarantees

`VE.Service.FamilyNorms.runCase` sends a family norm document to the FOL view
(`VE.Service.FamilyNorms.folView`) when `firstOrder` holds. These theorems state what the test
guarantees about the document: every definition's head is one the view keeps
(`VE.Core.Layers.folEntry`), and every body, guard and carve-out the family decodes is the
embedding of an FOL formula, whose meaning the embedding keeps
(`VE.Core.conservativity_without_reach`, `VE.Order.conservativity`). -/

namespace VE.Norms.Family
open Lean

/-- A term `orderTermFol` passes is an FOL term: a variable or a constant, no number or
arithmetic. -/
theorem orderTermFol_embed (t : VE.Order.Term) (h : orderTermFol t = true) :
    ∃ s : VE.Term, VE.Order.embedTerm s = t := by
  cases t with
  | var i => exact ⟨.var i, rfl⟩
  | const c => exact ⟨.const c, rfl⟩
  | _ => simp [orderTermFol] at h

/-- An order formula `orderFol` passes is the embedding of an FOL formula: no comparison and no
arithmetic term. -/
theorem orderFol_embed : ∀ (a : VE.Order.Formula), orderFol a = true →
    ∃ φ : VE.Formula, VE.Order.embed φ = a := by
  have term := orderTermFol_embed
  intro a h
  induction a with
  | top => exact ⟨.top, rfl⟩
  | bottom => exact ⟨.bottom, rfl⟩
  | unary p t =>
    obtain ⟨s, rfl⟩ := term t h
    exact ⟨.unary p s, rfl⟩
  | binary p t u =>
    simp only [orderFol, Bool.and_eq_true] at h
    obtain ⟨s, rfl⟩ := term t h.1
    obtain ⟨r, rfl⟩ := term u h.2
    exact ⟨.binary p s r, rfl⟩
  | eq t u =>
    simp only [orderFol, Bool.and_eq_true] at h
    obtain ⟨s, rfl⟩ := term t h.1
    obtain ⟨r, rfl⟩ := term u h.2
    exact ⟨.eq s r, rfl⟩
  | lt _ _ | le _ _ => simp [orderFol] at h
  | not a ih =>
    obtain ⟨φ, rfl⟩ := ih h
    exact ⟨.not φ, rfl⟩
  | all s a ih =>
    obtain ⟨φ, rfl⟩ := ih h
    exact ⟨.all s φ, rfl⟩
  | ex s a ih =>
    obtain ⟨φ, rfl⟩ := ih h
    exact ⟨.ex s φ, rfl⟩
  | and a b iha ihb =>
    simp only [orderFol, Bool.and_eq_true] at h
    obtain ⟨φ, rfl⟩ := iha h.1
    obtain ⟨ψ, rfl⟩ := ihb h.2
    exact ⟨.and φ ψ, rfl⟩
  | or a b iha ihb =>
    simp only [orderFol, Bool.and_eq_true] at h
    obtain ⟨φ, rfl⟩ := iha h.1
    obtain ⟨ψ, rfl⟩ := ihb h.2
    exact ⟨.or φ ψ, rfl⟩
  | implies a b iha ihb =>
    simp only [orderFol, Bool.and_eq_true] at h
    obtain ⟨φ, rfl⟩ := iha h.1
    obtain ⟨ψ, rfl⟩ := ihb h.2
    exact ⟨.implies φ ψ, rfl⟩

/-- A formula `firstOrderFormula` passes is first-order wherever its family decodes it: the
embedding of an FOL formula (`VE.Core.embed`, whose meaning `conservativity_without_reach` keeps;
`VE.Order.embed` for the order family). -/
theorem firstOrderFormula_fol {order : Bool} {j : Json}
    (h : firstOrderFormula order j = true) :
    (order = false → ∀ a, VE.Core.Bridge.decodeFormula 64 j = .ok a → ∃ φ : VE.Formula, VE.Core.embed φ = a) ∧
    (order = true → ∀ a, VE.Order.Wire.decodeFormula 64 j = .ok a → ∃ φ : VE.Formula, VE.Order.embed φ = a) := by
  refine ⟨fun ho a ha => ?_, fun ho a ha => ?_⟩
  · subst ho
    simp only [firstOrderFormula, Bool.false_eq_true, ↓reduceIte, ha] at h
    obtain ⟨φ, hφ⟩ := Option.isSome_iff_exists.mp h
    exact ⟨φ, VE.Core.embed_of_erase a φ hφ⟩
  · subst ho
    simp only [firstOrderFormula, ↓reduceIte, ha] at h
    exact orderFol_embed a h

/-- A definition `firstOrderDefinition` passes is one the FOL view carries: its head passes the
view's filter (`folEntry`: at most two arguments, the entries `folView` keeps), and its body is
first-order wherever its family decodes it (`firstOrderFormula_fol`). -/
theorem firstOrderDefinition_fol {order : Bool} {entry payload : Json}
    (h : firstOrderDefinition order entry = true)
    (hd : entry.getObjVal? "defined" = .ok payload) :
    VE.Core.Layers.folEntry entry = true ∧
    (order = false → ∀ a, VE.Core.Bridge.decodeFormula 64 (payload.getObjValD "body") = .ok a →
      ∃ φ : VE.Formula, VE.Core.embed φ = a) ∧
    (order = true → ∀ a, VE.Order.Wire.decodeFormula 64 (payload.getObjValD "body") = .ok a →
      ∃ φ : VE.Formula, VE.Order.embed φ = a) := by
  simp only [firstOrderDefinition, hd, Bool.and_eq_true] at h
  exact ⟨h.1, firstOrderFormula_fol h.2⟩

/-- A document `firstOrder` sends to the FOL view is one the view regenerates: no declaration uses
`$int`, every definition is one the view carries (`firstOrderDefinition_fol`), and every guard and
carve-out is first-order wherever its family decodes it (`firstOrderFormula_fol`); `order` is
whether the environment has the `order@0` profile. -/
theorem firstOrder_fol {environment norms : Json} {order : Bool}
    (ho : (match VE.Route.Gate.profilesOf environment with
      | .ok ps => ps.contains "order@0"
      | .error _ => false) = order)
    (h : firstOrder environment norms = true) :
    usesInt environment = false ∧
    (∀ p entry payload, (p, entry) ∈ VE.Core.Layers.predicatesOf environment →
      entry.getObjVal? "defined" = .ok payload →
      VE.Core.Layers.folEntry entry = true ∧
      (order = false → ∀ a, VE.Core.Bridge.decodeFormula 64 (payload.getObjValD "body") = .ok a →
        ∃ φ : VE.Formula, VE.Core.embed φ = a) ∧
      (order = true → ∀ a, VE.Order.Wire.decodeFormula 64 (payload.getObjValD "body") = .ok a →
        ∃ φ : VE.Formula, VE.Order.embed φ = a)) ∧
    (∀ xs, norms = .arr xs → ∀ u ∈ xs.toList, ∀ g ∈ (match (u.getObjValD "norm").getObjValD "unless" with
        | .arr ys => ys.toList
        | _ => []) ++ [(u.getObjValD "norm").getObjValD "guard"],
      (order = false → ∀ a, VE.Core.Bridge.decodeFormula 64 g = .ok a → ∃ φ : VE.Formula, VE.Core.embed φ = a) ∧
      (order = true → ∀ a, VE.Order.Wire.decodeFormula 64 g = .ok a → ∃ φ : VE.Formula, VE.Order.embed φ = a)) := by
  unfold firstOrder at h
  cases hp : VE.Route.Gate.profilesOf environment <;> simp only [hp] at h ho <;> subst ho
  all_goals
    simp only [Bool.and_eq_true, Bool.not_eq_true', List.all_eq_true] at h
    obtain ⟨⟨hint, hdefs⟩, hnorms⟩ := h
    refine ⟨hint, fun p entry payload hm hd => firstOrderDefinition_fol (hdefs (p, entry) hm) hd, ?_⟩
    intro xs hx u hu g hg
    subst hx
    simp only [Array.all_eq_true'] at hnorms
    have hu' := hnorms u (Array.mem_toList_iff.mp hu)
    simp only [Bool.and_eq_true] at hu'
    apply firstOrderFormula_fol
    simp only [List.mem_append, List.mem_singleton] at hg
    rcases hg with hg | rfl
    · split at hg
      · rename_i ys hys
        rw [hys] at hu'
        simp only [Array.all_eq_true'] at hu'
        exact hu'.2 g (Array.mem_toList_iff.mp hg)
      · simp at hg
    · exact hu'.1

end VE.Norms.Family
