import VE.Finite

namespace VE
universe u

/-- A finite acyclic derivation with exact, explicit outstanding leaves. Each
step supplies entailment of its exact ordered premises and conclusion. Sharing
in a DAG can be unfolded into this proof tree; no graph decoder is verified here.
An unproved intermediate claim can occur only as a retained assumption. -/
inductive Derivation (E : Environment) : List Formula → Formula → Prop where
  | assumption (a : Formula) (typed : a.WellFormed E []) : Derivation E [a] a
  | step (premises : List Formula) (conclusion : Formula)
      (leaves : Formula → List Formula)
      (typed : conclusion.WellFormed E [])
      (edge : Entails.{u} E premises conclusion)
      (children : ∀ a ∈ premises, Derivation E (leaves a) a) :
      Derivation E (premises.flatMap leaves) conclusion

/-- P10: every certified finite derivation entails its conclusion from precisely
its accumulated undischarged leaf list (including duplicates). -/
theorem composition_sound {E : Environment} {leaves : List Formula} {root : Formula}
    (d : Derivation.{u} E leaves root) : Entails.{u} E leaves root := by
  induction d with
  | assumption a _ =>
    intro S _ h
    exact h a (by simp)
  | step premises conclusion leaves _ edge _ ih =>
    intro S hS h
    apply edge S hS
    intro a ha
    apply ih a ha S hS
    intro b hb
    apply h b
    exact List.mem_flatMap.mpr ⟨a, ha, hb⟩

/-- The semantic cut principle also supports topologically ordered DAG folds. -/
theorem entails_cut {E : Environment} {leaves premises : List Formula} {c : Formula}
    (edge : Entails.{u} E premises c)
    (dependencies : ∀ a ∈ premises, Entails.{u} E leaves a) :
    Entails.{u} E leaves c := by
  intro S hS h
  exact edge S hS (fun a ha => dependencies a ha S hS h)

/-- Only positive premise evaluations and a negative conclusion count as a
countermodel. No result of a bounded search is used to assert entailment. -/
def countermodelCheck {α : Type u} [DecidableEq α] (M : FiniteModel α)
    (premises : List Formula) (conclusion : Formula) : Bool :=
  premises.all (fun a => a.eval M []) && !(conclusion.eval M [])

/-- Characterization of the Boolean countermodel check, independently of whether
the supplied finite data are admissible for a particular environment. -/
theorem countermodelCheck_iff {α : Type u} [DecidableEq α] (M : FiniteModel α)
    (premises : List Formula) (conclusion : Formula) :
    countermodelCheck M premises conclusion = true ↔
      (∀ a ∈ premises, a.denote M.asStructure []) ∧
        ¬ conclusion.denote M.asStructure [] := by
  simp [countermodelCheck, eval_iff_denote, eval_false_iff_not_denote]

/-- P11: an admissible finite countermodel refutes consequence over arbitrary
admissible structures in the same universe. This general lemma also holds for
raw formulas under their total semantics; it does not establish typing. The
bridge's CountermodelQuery.refutes_sound includes closed typing explicitly. -/
theorem countermodel_sound {α : Type u} [DecidableEq α] {E : Environment}
    (M : FiniteModel α) (valid : M.Valid E) (premises : List Formula)
    (conclusion : Formula) (checked : countermodelCheck M premises conclusion = true) :
    ¬ Entails.{u} E premises conclusion := by
  obtain ⟨hp, hc⟩ := (countermodelCheck_iff M premises conclusion).mp checked
  intro edge
  exact hc (edge M.asStructure valid hp)

/-- A sound edge and an admissible checked countermodel cannot coexist for the
same environment, ordered premise ASTs and conclusion AST. -/
theorem no_certificate_countermodel_conflict {α : Type u} [DecidableEq α]
    {E : Environment} (M : FiniteModel α) (valid : M.Valid E)
    (premises : List Formula) (conclusion : Formula)
    (edge : Entails.{u} E premises conclusion) :
    countermodelCheck M premises conclusion = false := by
  cases h : countermodelCheck M premises conclusion with
  | false => rfl
  | true => exact False.elim (countermodel_sound M valid premises conclusion h edge)

end VE
