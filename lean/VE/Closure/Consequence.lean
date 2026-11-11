import VE.Closure.Finite
import VE.Core.Consequence

namespace VE.Closure
universe u

/-- Closure consequence is Core's consequence on the embedding. -/
def Entails (E : Environment) (premises : List Formula) (conclusion : Formula) : Prop :=
  VE.Core.Entails.{u} E (premises.map Formula.toCore) conclusion.toCore

/-- Closure consequence read in closure's own syntax. -/
theorem entails_iff (E : Environment) (premises : List Formula) (conclusion : Formula) :
    Entails.{u} E premises conclusion ↔ ∀ S : Structure.{u}, S.Admissible E →
      (∀ a ∈ premises, a.denote S []) → conclusion.denote S [] := by
  simp [Entails, VE.Core.Entails, Formula.denote]

def countermodelCheck {α : Type u} [DecidableEq α] (M : FiniteModel α)
    (premises : List Formula) (conclusion : Formula) : Bool :=
  premises.all (fun a => a.eval M []) && !conclusion.eval M []

theorem countermodelCheck_iff {α : Type u} [DecidableEq α] (M : FiniteModel α)
    (premises : List Formula) (conclusion : Formula) :
    countermodelCheck M premises conclusion = true ↔
      (∀ a ∈ premises, a.denote M.asStructure []) ∧ ¬ conclusion.denote M.asStructure [] := by
  simp [countermodelCheck, eval_iff_denote, eval_false_iff_not_denote]

theorem countermodel_sound {α : Type u} [DecidableEq α] (M : FiniteModel α)
    (E : Environment) (premises : List Formula) (conclusion : Formula)
    (hm : M.Valid E) (h : countermodelCheck M premises conclusion = true) :
    ¬ Entails.{u} E premises conclusion := by
  obtain ⟨hp, hc⟩ := (countermodelCheck_iff M premises conclusion).mp h
  intro he
  exact hc ((entails_iff E premises conclusion).mp he M.asStructure hm hp)

end VE.Closure
