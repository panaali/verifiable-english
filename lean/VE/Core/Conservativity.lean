import VE.Core.TableauExtendedChecker
import VE.Closure.Consequence

namespace VE.Core
universe u

def embedKind : VE.Closure.Kind → Kind
  | .plus => .plus
  | .star => .star

theorem path_iff {α : Type u} (R : α → α → Prop) (a b : α) :
    Path R a b ↔ VE.Closure.Path R a b := Iff.rfl

theorem reachable_iff {α : Type u} (k : VE.Closure.Kind)
    (R : α → α → Prop) (a b : α) :
    Reachable (embedKind k) R a b ↔ VE.Closure.Reachable k R a b := by
  cases k <;> exact Iff.rfl

/-- The closure language embeds constructor for constructor: closure's own embedding, which
defines closure's typing, checker, meaning and consequence. -/
def embedClosure : VE.Closure.Formula → Formula := VE.Closure.Formula.toCore

theorem embedClosure_denote (S : Structure) (ρ : Valuation S)
    (a : VE.Closure.Formula) :
    (embedClosure a).denote S ρ ↔ a.denote S ρ := Iff.rfl

theorem embedClosure_check (E : Environment) (Γ : List String)
    (a : VE.Closure.Formula) :
    (embedClosure a).check E Γ = a.check E Γ := rfl

/-- A Core proof of embedded v0 statements has exactly the v0 consequence. -/
theorem entails_v0 (E : Environment) (ps : List VE.Formula) (c : VE.Formula)
    (h : Entails.{u} E (ps.map embed) (embed c)) :
    VE.Entails.{u} E ps c := by
  intro S hS hp
  apply (conservativity S [] c).mp
  apply h S hS
  intro a ha
  obtain ⟨p, hp', rfl⟩ := List.mem_map.mp ha
  exact (conservativity S [] p).mpr (hp p hp')

/-- A Core proof of embedded closure statements has exactly closure consequence. -/
theorem entails_closure (E : Environment) (ps : List VE.Closure.Formula)
    (c : VE.Closure.Formula)
    (h : Entails.{u} E (ps.map embedClosure) (embedClosure c)) :
    VE.Closure.Entails.{u} E ps c := h

end VE.Core
