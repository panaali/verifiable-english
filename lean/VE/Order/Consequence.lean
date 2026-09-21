import VE.Order.Finite

namespace VE.Order
universe u

def Entails (E : Environment) (premises : List Formula) (conclusion : Formula) : Prop :=
  ∀ S : Structure.{u}, S.Admissible E →
    (∀ a ∈ premises, a.denote S []) → conclusion.denote S []

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
  exact hc (he M.asStructure hm hp)

end VE.Order
