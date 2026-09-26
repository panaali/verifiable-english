import Std

/-! The assertion-only, same-background reading-set rule. Each predicate below
is the truth of one closed formula in one fixed environment and one structure.
The theorem does not apply when a reading changes the environment or its
background premises. -/
namespace VE.Route

/-- One globally consistent reading per source unit, in source order. -/
inductive ReadingChoices {Model : Type} (S : Model) :
    List (List (Model → Prop)) → List (Model → Prop) → Prop where
  | nil : ReadingChoices S [] []
  | cons {rs rest r choices} (member : r ∈ rs) (holds : r S)
      (tail : ReadingChoices S rest choices) :
      ReadingChoices S (rs :: rest) (r :: choices)

/-- A structure satisfies the disjunction of every assertion reading set iff
one reading can be selected from each set and all selected readings hold in
that same structure. -/
theorem readings_all_iff {Model : Type} (S : Model)
    (sets : List (List (Model → Prop))) :
    (∀ rs ∈ sets, ∃ r ∈ rs, r S) ↔
      ∃ choices : List (Model → Prop),
        ReadingChoices S sets choices := by
  induction sets with
  | nil =>
    constructor
    · intro _
      exact ⟨[], .nil⟩
    · intro _ rs h
      cases h
  | cons rs rest ih =>
    constructor
    · intro h
      obtain ⟨r, hr, hs⟩ := h rs (by simp)
      obtain ⟨choices, hc⟩ := ih.mp (by
        intro ys hy
        exact h ys (by simp [hy]))
      exact ⟨r :: choices, .cons hr hs hc⟩
    · rintro ⟨choices, hc⟩ ys hy
      cases hc with
      | cons hmember hholds htail =>
        have hrest : ∀ zs ∈ rest, ∃ z ∈ zs, z S := ih.mpr ⟨_, htail⟩
        rcases List.mem_cons.mp hy with heq | hmem
        · subst ys
          exact ⟨_, hmember, hholds⟩
        · exact hrest ys hmem

end VE.Route
