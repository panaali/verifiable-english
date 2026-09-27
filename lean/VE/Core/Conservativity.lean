import VE.Core.TableauExtendedChecker
import VE.Closure.Consequence

namespace VE.Core
universe u

def embedKind : VE.Closure.Kind → Kind
  | .plus => .plus
  | .star => .star

theorem path_iff {α : Type u} (R : α → α → Prop) (a b : α) :
    Path R a b ↔ VE.Closure.Path R a b := by
  constructor
  · intro h
    induction h with
    | edge h => exact .edge h
    | cons h _ ih => exact .cons h ih
  · intro h
    induction h with
    | edge h => exact .edge h
    | cons h _ ih => exact .cons h ih

theorem reachable_iff {α : Type u} (k : VE.Closure.Kind)
    (R : α → α → Prop) (a b : α) :
    Reachable (embedKind k) R a b ↔ VE.Closure.Reachable k R a b := by
  cases k <;> simp [embedKind, Reachable, VE.Closure.Reachable, path_iff]

/-- The closure language embeds constructor for constructor. -/
def embedClosure : VE.Closure.Formula → Formula
  | .top => .top
  | .bottom => .bottom
  | .unary p t => .unary p t
  | .binary p t r => .binary p t r
  | .eq t r => .eq t r
  | .not a => .not (embedClosure a)
  | .and a b => .and (embedClosure a) (embedClosure b)
  | .or a b => .or (embedClosure a) (embedClosure b)
  | .implies a b => .implies (embedClosure a) (embedClosure b)
  | .all s a => .all s (embedClosure a)
  | .ex s a => .ex s (embedClosure a)
  | .reachNamed k p t r => .reachNamed (embedKind k) p t r
  | .reachBody k s a t r => .reachBody (embedKind k) s (embedClosure a) t r

theorem embedClosure_denote (S : Structure) (ρ : Valuation S)
    (a : VE.Closure.Formula) :
    (embedClosure a).denote S ρ ↔ a.denote S ρ := by
  induction a generalizing ρ <;>
    simp_all [embedClosure, Formula.denote, VE.Closure.Formula.denote, reachable_iff]

theorem embedClosure_check (E : Environment) (Γ : List String)
    (a : VE.Closure.Formula) :
    (embedClosure a).check E Γ = a.check E Γ := by
  induction a generalizing Γ <;>
    simp_all [embedClosure, Formula.check, VE.Closure.Formula.check] <;> rfl

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
    VE.Closure.Entails.{u} E ps c := by
  intro S hS hp
  apply (embedClosure_denote S [] c).mp
  apply h S hS
  intro a ha
  obtain ⟨p, hp', rfl⟩ := List.mem_map.mp ha
  exact (embedClosure_denote S [] p).mpr (hp p hp')

end VE.Core
