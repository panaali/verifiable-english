import VE.Route.Background

/-! The `data@0` statement layer. Flag formulas are generated from declared
binary predicates; author text cannot supply or edit them. The theorems connect
their checked first-order meaning to functional and total relation tables. -/
namespace VE.Data.Background
universe u

structure Flag where
  name : String
  source : String
  target : String
  functional : Bool
  total : Bool
  deriving Repr, DecidableEq

def functionalPremise (f : Flag) : VE.Formula :=
  .all f.source (.all f.target (.all f.target
    (.implies (.and (.binary f.name (.var 2) (.var 1))
                    (.binary f.name (.var 2) (.var 0))) (.eq (.var 1) (.var 0)))))

def totalPremise (f : Flag) : VE.Formula :=
  .all f.source (.ex f.target (.binary f.name (.var 1) (.var 0)))

def premises (f : Flag) : List VE.Formula :=
  (if f.functional then [functionalPremise f] else []) ++
  (if f.total then [totalPremise f] else [])

def generate (flags : List Flag) : List VE.Formula := flags.flatMap premises

/-- The reviewed meaning of a functional table: each source has at most one
target among the true rows. -/
def Functional (S : VE.Structure.{u}) (f : Flag) : Prop :=
  ∀ x, S.domain f.source x → ∀ y, S.domain f.target y →
    ∀ z, S.domain f.target z →
      S.relation f.name [x, y] → S.relation f.name [x, z] → y = z

/-- The reviewed meaning of a total table: each source has a target. -/
def Total (S : VE.Structure.{u}) (f : Flag) : Prop :=
  ∀ x, S.domain f.source x → ∃ y, S.domain f.target y ∧ S.relation f.name [x, y]

def Intended (S : VE.Structure.{u}) (f : Flag) : Prop :=
  (f.functional = true → Functional S f) ∧ (f.total = true → Total S f)

theorem functionalPremise_iff (S : VE.Structure.{u}) (f : Flag) :
    (functionalPremise f).denote S [] ↔ Functional S f := by
  simp [functionalPremise, VE.Formula.denote, VE.Term.denote, Functional]
  exact ⟨fun h x hx y hy z hz hxy hxz => (h x hx y hy z hz hxy hxz).symm,
    fun h x hx y hy z hz hxy hxz => (h x hx y hy z hz hxy hxz).symm⟩

theorem totalPremise_iff (S : VE.Structure.{u}) (f : Flag) :
    (totalPremise f).denote S [] ↔ Total S f := by
  simp [totalPremise, VE.Formula.denote, VE.Term.denote, Total]

theorem premises_sat_iff (S : VE.Structure.{u}) (f : Flag) :
    (∀ a ∈ premises f, a.denote S []) ↔ Intended S f := by
  cases hf : f.functional <;> cases ht : f.total <;>
    simp [premises, Intended, hf, ht, functionalPremise_iff, totalPremise_iff]

theorem generate_sat_iff (S : VE.Structure.{u}) (flags : List Flag) :
    (∀ a ∈ generate flags, a.denote S []) ↔ ∀ f ∈ flags, Intended S f := by
  unfold generate
  constructor
  · intro h f hf
    exact (premises_sat_iff S f).mp (fun a ha => h a (List.mem_flatMap.mpr ⟨f, hf, ha⟩))
  · intro h a ha
    obtain ⟨f, hf, hfa⟩ := List.mem_flatMap.mp ha
    exact (premises_sat_iff S f).mpr (h f hf) a hfa

/-- The executable finite-table check evaluates precisely the generated
premises. This is regenerated from flag declarations, never a wire premise. -/
def flagsValid {α : Type u} [DecidableEq α] (M : VE.FiniteModel α)
    (flags : List Flag) : Bool :=
  (generate flags).all (fun a => a.eval M [])

theorem flags_model_valid {α : Type u} [DecidableEq α] (M : VE.FiniteModel α)
    (flags : List Flag) (h : flagsValid M flags = true) :
    ∀ f ∈ flags, Intended M.asStructure f := by
  apply (generate_sat_iff M.asStructure flags).mp
  intro a ha
  exact (VE.eval_iff_denote M [] a).mp (List.all_eq_true.mp h a ha)

/-- Equality-only string semantics: checked consequence with the declared
literal distinctness premises implies consequence over string-admissible
structures. -/
theorem string_encoding_sound (E : VE.Environment) (lits : List String)
    (hn : lits.Nodup) (Γ : List VE.Formula) (φ : VE.Formula)
    (h : VE.Entails.{u} E (VE.Route.Background.literals lits ++ Γ) φ) :
    VE.Route.Background.EntailsString.{u} E lits Γ φ :=
  (VE.Route.Background.fol_route_entails_iff E lits hn Γ φ).mp h

end VE.Data.Background
