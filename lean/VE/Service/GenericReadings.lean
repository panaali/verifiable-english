import VE.Service.GenericGraph

/-! The readings checker's three soundness theorems (`VE/Service/Readings.lean`)
over any formula type with a disjunction and a false formula, and any model
semantics (`GenericGraph.Ent`): the `readings` mode on the closure, core and
order families.

A *choice* picks one reading from each set, in set order. `ALL` evidence is one
certificate over Background, the fixed premises and each set's right-nested
disjunction; `NONE` evidence is one admissible model where Background, the
fixed premises and every reading hold and the conclusion fails; `SOME`
evidence is a certificate for one choice and a refuting model for another. -/
namespace VE.Service.GenericReadings
open VE.Service.GenericGraph (Ent)
universe v

section
variable {F : Type} (disj : F → F → F) (bot : F)

/-- Python's per-set disjunction (`ve/readings.py`): `r₀ ∨ (r₁ ∨ … r_{n-1})`. -/
def disjunction : List F → F
  | [] => bot
  | [a] => a
  | a :: b :: rest => disj a (disjunction (b :: rest))

theorem disjunction_holds {Model : Type v} (Holds : Model → F → Prop) (S : Model)
    (hor : ∀ a b, Holds S (disj a b) ↔ Holds S a ∨ Holds S b) (hbot : ¬ Holds S bot) :
    ∀ rs : List F, Holds S (disjunction disj bot rs) ↔ ∃ r ∈ rs, Holds S r
  | [] => by simp [disjunction, hbot]
  | [a] => by simp [disjunction]
  | a :: b :: rest => by
    have ih := disjunction_holds Holds S hor hbot (b :: rest)
    simp only [disjunction, hor, ih, List.mem_cons, exists_eq_or_imp]

/-- `choice` picks one reading of each set, in order. -/
inductive Choice : List (List F) → List F → Prop where
  | nil : Choice [] []
  | cons {r : F} {rs : List F} {sets : List (List F)} {choice : List F}
      (member : r ∈ rs) (tail : Choice sets choice) : Choice (rs :: sets) (r :: choice)

theorem choice_covers {sets : List (List F)} {choice : List F}
    (h : Choice sets choice) : ∀ rs ∈ sets, ∃ r ∈ choice, r ∈ rs := by
  induction h with
  | nil => intro _ hm; cases hm
  | cons hr _ ih =>
    intro rs hm
    rcases List.mem_cons.mp hm with rfl | hm
    · exact ⟨_, List.mem_cons_self .., hr⟩
    · obtain ⟨r', hr', hm'⟩ := ih rs hm
      exact ⟨r', List.mem_cons_of_mem _ hr', hm'⟩

theorem choice_within {sets : List (List F)} {choice : List F}
    (h : Choice sets choice) : ∀ r ∈ choice, ∃ rs ∈ sets, r ∈ rs := by
  induction h with
  | nil => intro _ hm; cases hm
  | cons hr _ ih =>
    intro r hm
    rcases List.mem_cons.mp hm with rfl | hm
    · exact ⟨_, List.mem_cons_self .., hr⟩
    · obtain ⟨rs, hrs, hm'⟩ := ih r hm
      exact ⟨rs, List.mem_cons_of_mem _ hrs, hm'⟩

/-- The readings a list of indices picks, one per set. -/
def resolve : List (List F) → List Nat → Option (List F)
  | [], [] => some []
  | rs :: sets, i :: is => do
    let r ← rs[i]?
    let rest ← resolve sets is
    pure (r :: rest)
  | _, _ => none

theorem resolve_choice : ∀ (sets : List (List F)) (is : List Nat) (choice : List F),
    resolve sets is = some choice → Choice sets choice
  | [], [], _, h => by cases h; exact .nil
  | rs :: sets, i :: is, choice, h => by
    simp only [resolve, Option.bind_eq_bind, Option.bind_eq_some_iff, Option.pure_def,
      Option.some.injEq] at h
    obtain ⟨r, hr, rest, hrest, rfl⟩ := h
    exact .cons (List.mem_of_getElem? hr) (resolve_choice sets is rest hrest)
  | [], _ :: _, _, h => by cases h
  | _ :: _, [], _, h => by cases h

/-- A model refuting the conclusion while every formula of `Γ` holds. -/
def Refutes {Model : Type v} (Adm : Model → Prop) (Holds : Model → F → Prop)
    (Γ : List F) (φ : F) : Prop :=
  ∃ S, Adm S ∧ (∀ a ∈ Γ, Holds S a) ∧ ¬ Holds S φ

theorem refutes_not_ent {Model : Type v} (Adm : Model → Prop) (Holds : Model → F → Prop)
    (Γ Δ : List F) (φ : F) (h : Refutes Adm Holds Γ φ) (sub : ∀ a ∈ Δ, a ∈ Γ) :
    ¬ Ent Adm Holds Δ φ := by
  obtain ⟨S, hS, hΓ, hφ⟩ := h
  exact fun he => hφ (he S hS (fun a ha => hΓ a (sub a ha)))

/-- `ALL`: a certificate over `B ++ fixed ++ disjunctions` that the certificate
contract makes sound shows every choice entails the conclusion. -/
theorem readings_all_sound {Model : Type v} (Adm : Model → Prop) (Holds : Model → F → Prop)
    (hor : ∀ S a b, Holds S (disj a b) ↔ Holds S a ∨ Holds S b) (hbot : ∀ S, ¬ Holds S bot)
    (B fixed : List F) (sets : List (List F)) (φ : F)
    (h : Ent Adm Holds (B ++ fixed ++ sets.map (disjunction disj bot)) φ) :
    ∀ choice, Choice sets choice → Ent Adm Holds (B ++ fixed ++ choice) φ := by
  intro choice hc S hS hsat
  apply h S hS
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · exact hsat a (List.mem_append_left _ ha)
  · obtain ⟨rs, hrs, rfl⟩ := List.mem_map.mp ha
    obtain ⟨r, hr, hm⟩ := choice_covers hc rs hrs
    exact (disjunction_holds disj bot Holds S (hor S) (hbot S) rs).mpr
      ⟨r, hm, hsat r (List.mem_append_right _ hr)⟩

/-- `NONE`: one admissible model where Background, the fixed premises and every
reading hold and the conclusion fails is a countermodel for every choice. -/
theorem readings_none_sound {Model : Type v} (Adm : Model → Prop) (Holds : Model → F → Prop)
    (B fixed : List F) (sets : List (List F)) (φ : F)
    (h : Refutes Adm Holds (B ++ fixed ++ sets.flatten) φ) :
    ∀ choice, Choice sets choice → ¬ Ent Adm Holds (B ++ fixed ++ choice) φ := by
  intro choice hc
  apply refutes_not_ent Adm Holds _ _ φ h
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · exact List.mem_append_left _ ha
  · obtain ⟨rs, hrs, hm⟩ := choice_within hc a ha
    exact List.mem_append_right _ (List.mem_flatten.mpr ⟨rs, hrs, hm⟩)

/-- `SOME`: an entailing choice and a refuted choice. -/
theorem readings_some_sound {Model : Type v} (Adm : Model → Prop) (Holds : Model → F → Prop)
    (B fixed : List F) (sets : List (List F)) (φ : F) (proved refuted : List F)
    (hp : Choice sets proved) (hr : Choice sets refuted)
    (hc : Ent Adm Holds (B ++ fixed ++ proved) φ)
    (hm : Refutes Adm Holds (B ++ fixed ++ refuted) φ) :
    (∃ choice, Choice sets choice ∧ Ent Adm Holds (B ++ fixed ++ choice) φ) ∧
      (∃ choice, Choice sets choice ∧ ¬ Ent Adm Holds (B ++ fixed ++ choice) φ) :=
  ⟨⟨proved, hp, hc⟩, ⟨refuted, hr, refutes_not_ent Adm Holds _ _ φ hm (fun _ ha => ha)⟩⟩

end

end VE.Service.GenericReadings
