import VE.Cardinality.Wire
import VE.Compose.Dispatch

/-! The `cardinality@0` row of AR-10's profile table (SYNTHESIS 2.2; quantities 4.2, E2). The batch that adds a row
proves the composition theorem for every list the row newly admits: the table admits a list with `cardinality@0`
exactly when the cardinality decoder's E2 does (one of W6a's two lists beside it), and its route is the frozen one,
whose checker no list with `cardinality@0` reaches (the `cardinality` mode decodes these environments itself). -/
namespace VE.Cardinality
open VE.Compose

/-- A strictly increasing list whose members a strictly increasing list holds is a sublist of it. -/
theorem sublist_of_sorted : ∀ {l m : List String}, l.Pairwise (· < ·) → m.Pairwise (· < ·) →
    (∀ x ∈ l, x ∈ m) → l.Sublist m
  | [], _, _, _, _ => List.nil_sublist _
  | a :: _, [], _, _, h => absurd (h a (List.mem_cons_self ..)) List.not_mem_nil
  | a :: l, b :: m, hl, hm, h => by
    have hl' := List.pairwise_cons.mp hl
    have hm' := List.pairwise_cons.mp hm
    by_cases hab : a = b
    · subst hab
      refine (sublist_of_sorted hl'.2 hm'.2 fun x hx => ?_).cons₂ a
      rcases List.mem_cons.mp (h x (List.mem_cons_of_mem _ hx)) with e | hx'
      · exact absurd (e ▸ hl'.1 x hx) (String.lt_irrefl _)
      · exact hx'
    · have hba : b < a := hm'.1 a ((List.mem_cons.mp (h a (List.mem_cons_self ..))).resolve_left hab)
      refine (sublist_of_sorted hl hm'.2 fun x hx => ?_).cons b
      rcases List.mem_cons.mp (h x hx) with e | hx'
      · subst e
        rcases List.mem_cons.mp hx with e | hx''
        · exact absurd e.symm hab
        · exact absurd (String.lt_trans hba (hl'.1 _ hx'')) (String.lt_irrefl _)
      · exact hx'

/-- The gate admits a list with `cardinality@0` exactly when E2 does (`Wire.profileLists`), on the frozen route. A
list that also has the document layer `judgments@0` is admitted exactly as the same list without it
(`gate_judgments`), which this theorem then decides. -/
theorem gate_cardinality (ps : List String) (h : "cardinality@0" ∈ ps) (hj : "judgments@0" ∉ ps) (r : Route) :
    gateOf profileTable ps = .ok r ↔ ps ∈ Wire.profileLists ∧ r = .frozen := by
  have hlists : ∀ qs ∈ Wire.profileLists, gateOf profileTable qs = .ok .frozen := by
    intro qs hq
    simp only [Wire.profileLists, VE.Time.Wire.w6Profiles, List.map_cons, List.map_nil, List.mem_cons,
      List.not_mem_nil, or_false] at hq
    rcases hq with rfl | rfl <;> rfl
  constructor
  · intro hg
    obtain ⟨⟨hs, hk, hrows⟩, rfl⟩ := (gateOf_iff _ _ _).mp hg
    obtain ⟨hreq, href⟩ := hrows ⟨"cardinality@0", ["order@0", "relational-fol@0", "time@0"],
      refusing "cardinality@0" cardinalityOthers, "layer"⟩ (by simp [profileTable, baseRows]) (.inl h)
    have hsub : ∀ x ∈ ps, x = "documents@1" ∨ x ∈ ["cardinality@0", "order@0", "relational-fol@0", "time@0"] := by
      intro x hx
      obtain ⟨row, hr, rfl⟩ := hk x hx
      have key : ∀ p ∈ profileTable.map (·.profile), p = "documents@1" ∨
          p ∈ ["cardinality@0", "order@0", "relational-fol@0", "time@0"] ∨ p = "judgments@0" ∨
            p ∈ cardinalityOthers := by
        decide
      rcases key _ (List.mem_map_of_mem hr) with h1 | h1 | h2 | h3
      · exact .inl h1
      · exact .inr h1
      · exact absurd hx (h2 ▸ hj)
      · exact absurd hx (href _ (List.mem_map_of_mem (f := fun q => (q, s!"cardinality@0 with {q}")) h3))
    -- ps has E2's members, and only those: it is the one sorted list of them
    have hW : ∀ x ∈ ["cardinality@0", "order@0", "relational-fol@0", "time@0"], x ∈ ps := by
      intro x hx
      simp only [List.mem_cons, List.not_mem_nil, or_false] at hx
      rcases hx with rfl | rfl | rfl | rfl
      all_goals first | exact h | exact hreq _ (by simp)
    have same : ∀ t : List String, t.Pairwise (· < ·) → (∀ x ∈ ps, x ∈ t) → (∀ x ∈ t, x ∈ ps) → ps = t :=
      fun t ht h1 h2 => (sublist_of_sorted hs ht h1).eq_of_length
        (Nat.le_antisymm (sublist_of_sorted hs ht h1).length_le (sublist_of_sorted ht hs h2).length_le)
    have hp : ps ∈ Wire.profileLists := by
      by_cases hd : "documents@1" ∈ ps
      · have h5 : ∀ x ∈ ["cardinality@0", "documents@1", "order@0", "relational-fol@0", "time@0"], x ∈ ps := by
          intro x hx
          simp only [List.mem_cons, List.not_mem_nil, or_false] at hx
          rcases hx with rfl | rfl | rfl | rfl | rfl
          all_goals first | exact h | exact hd | exact hW _ (by simp)
        have h5' : ∀ x ∈ ps, x ∈ ["cardinality@0", "documents@1", "order@0", "relational-fol@0", "time@0"] := by
          intro x hx
          rcases hsub x hx with rfl | hx'
          · simp
          · simp only [List.mem_cons, List.not_mem_nil, or_false] at hx' ⊢
            rcases hx' with rfl | rfl | rfl | rfl <;> simp
        rw [same _ (by decide) h5' h5]
        decide
      · rw [same ["cardinality@0", "order@0", "relational-fol@0", "time@0"] (by decide)
          (fun x hx => (hsub x hx).resolve_left fun e => hd (e ▸ hx)) hW]
        decide
    exact ⟨hp, ((gateOf_iff _ _ _).mp (hlists ps hp)).2.symm⟩
  · rintro ⟨hp, rfl⟩
    exact hlists ps hp

end VE.Cardinality
