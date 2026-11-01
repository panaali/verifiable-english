import VE.Readings.BaseUp
import VE.Compose.Adjoin

/-! S2b's first steps toward the rights case of `superpose_faithful` (docs/spec/composition-PLAN.md 2.3, 2.6, F21;
composition-S2-PLAN.md edit 1). `quiet_holds`: a structure satisfying `Choice_D` satisfies the quiescence premise of
every generated key of `sup D` that the fixed units alone do not generate. `bar_dead`: the fixed bar's node on `m` is
correlate's, guarded by `aimed_m` alone; at every well-sorted tuple it is not live when no owner of `aimed_m` is
chosen (F21's fixed-bar case). The typing is needed: at an ill-sorted tuple quiescence says nothing, so the rights
case of `superpose_faithful` carries `TupleTyped S r.sorts vs` (reviews/dri-decisions-20261031-cmp-s2b.md; the
counterexample is `RightsExamples.f21_needs_typed`). `adjoin_baseAdmissibleR` is the lifting lemma behind
`superpose_all` on a rights document. -/
namespace VE.Readings
open VE.Norms (Sat tupleVal)
open VE.Rights (RightsDoc correlate)
universe u

theorem origin_lt {D : Doc} {n : String} {x : Nat × Nat} (h : origin D n = some x) :
    x.1 < D.sets.length ∧ x.2 < setSize D x.1 := by
  unfold origin at h
  obtain ⟨m, hm, hs⟩ := List.exists_of_findSome?_eq_some h
  obtain ⟨i, hi, rfl⟩ := Option.map_eq_some_iff.mp hs
  exact ⟨List.mem_range.mp hm, List.mem_range.mp (List.mem_of_find?_eq_some hi)⟩

theorem aimedOwners_lt {D : Doc} {m : String} {o : List (Nat × Nat)} (ho : o ∈ aimedOwners D m) :
    ∀ x ∈ o, x.1 < D.sets.length ∧ x.2 < setSize D x.1 := by
  simp only [aimedOwners, VE.SoftNorms.mem_dedup, List.mem_filterMap] at ho
  obtain ⟨RN, _, hs⟩ := ho
  split at hs
  · cases hs
    intro x hx
    cases h : origin D (ruleOf RN.2) with
    | none => simp [h] at hx
    | some y => simp [h] at hx; subst hx; exact origin_lt h
  · cases hs

/-- Every quiescence premise holds where `Choice_D` holds: a key with one single-candidate owner is under that
    candidate's label in `quietOwn`, every other key that is not fixed-generated is in `quietShared`. -/
theorem quiet_holds {D : Doc} {S : VE.Structure.{u}} (hq : Sat S (choicePremises D))
    {g : GenKey × String × List String} (hg : g ∈ genKeys (sup D).1) (hf : fixedGenerated D g.1 = false)
    (hv : ∀ o ∈ owners D g.1, ∀ x ∈ o, x.1 < D.sets.length ∧ x.2 < setSize D x.1) :
    (quietFormula D g).denote S [] := by
  have hmem : ∀ e ∈ choiceLabelled D, e.2.denote S [] := fun e he =>
    hq _ (List.mem_map.mpr ⟨e, he, rfl⟩)
  cases hb : ((owners D g.1).length != 1 || (owners D g.1).any (·.length != 1)) with
  | true =>
    apply hmem ("readings:quiet:" ++ keyLabel g.1, quietFormula D g)
    have hs : ("readings:quiet:" ++ keyLabel g.1, quietFormula D g) ∈ quietShared D :=
      List.mem_map.mpr ⟨g, List.mem_filter.mpr ⟨hg, by simp only [hf, hb]; rfl⟩, rfl⟩
    exact List.mem_append_left _ (List.mem_append_left _ (List.mem_append_right _ hs))
  | false =>
    simp only [Bool.or_eq_false_iff, bne_eq_false_iff_eq, List.any_eq_false, bne_eq_false_iff_eq] at hb
    obtain ⟨h1, h2⟩ := hb
    obtain ⟨o, ho⟩ := List.length_eq_one_iff.mp h1
    have hoo : o ∈ owners D g.1 := by rw [ho]; exact List.mem_singleton_self o
    have hol : o.length = 1 := by
      have := h2 o hoo
      cases h : o.length == 1 <;> simp_all
    obtain ⟨x, rfl⟩ := List.length_eq_one_iff.mp hol
    obtain ⟨hm, hi⟩ := hv _ hoo x (List.mem_singleton_self x)
    have hm' := hm
    rw [setSize_eq hm] at hi
    let mine := (genKeys (sup D).1).filter (fun g' => owners D g'.1 == [[(x.1, x.2)]])
    have hgm : g ∈ mine := List.mem_filter.mpr ⟨hg, by simp [ho]⟩
    have hne : mine.isEmpty = false := List.isEmpty_eq_false_iff.mpr (List.ne_nil_of_mem hgm)
    have hin : ("readings:" ++ label D.sets[x.1] ++ ":" ++ toString x.2 ++ ":quiet", conj (mine.map (quietFormula D)))
        ∈ choiceLabelled D := by
      refine List.mem_append_left _ (List.mem_append_left _ (List.mem_append_left _ (List.mem_append_right _ ?_)))
      simp only [quietOwn, List.mem_flatMap, List.mem_range, List.mem_filterMap]
      refine ⟨x.1, hm', D.sets[x.1], by simp [List.getElem?_eq_getElem hm'], x.2, hi, ?_⟩
      simp only [mine] at hne
      simp [hne, mine]
    exact (conj_denote S [] _).mp (hmem _ hin) _ (List.mem_map.mpr ⟨g, hgm, rfl⟩)

/-- F21's fixed-bar case: the bar's node on m in sup D is not live at a well-sorted tuple when no owner of aimed_m
    is chosen, because quiescence empties aimed_m there. -/
theorem bar_dead {D : Doc} {S : VE.Structure.{u}} (hq : Sat S (choicePremises D)) {m : String}
    (hb : (sup D).1.bars ≠ []) (hm : m ∈ VE.Rights.barPreds (sup D).1) (hf : fixedGenerated D (.aimed m) = false)
    (hno : ∀ o ∈ aimedOwners D m, ¬ (conj (o.map (atomAt D))).denote S [])
    {vs : List S.Carrier} (ht : VE.TupleTyped S (VE.SoftNorms.sortsOf (sup D).1.soft m) vs) :
    ¬ VE.SoftNorms.LiveD (correlate (sup D).1) S (tupleVal vs) (VE.Rights.barNode (sup D).1 m) := by
  let g : GenKey × String × List String :=
    (.aimed m, VE.Rights.aimedName (VE.Rights.barIndex (sup D).1 m), VE.SoftNorms.sortsOf (sup D).1.soft m)
  have hg : g ∈ genKeys (sup D).1 := by
    simp only [genKeys, List.mem_append, if_neg hb]
    exact Or.inr (List.mem_map.mpr ⟨m, hm, rfl⟩)
  have hquiet := quiet_holds hq hg hf (fun o ho => aimedOwners_lt ho)
  rintro ⟨hguard, _⟩
  unfold quietFormula at hquiet
  rw [VE.Norms.bindAll_denote_nil] at hquiet
  have hd := hquiet vs ht hguard
  obtain ⟨φ, hφ, hd⟩ := (disj_denote S _ _).mp hd
  obtain ⟨o, ho, rfl⟩ := List.mem_map.mp hφ
  apply hno o ho
  rw [conj_denote] at hd ⊢
  intro a ha
  obtain ⟨x, _, rfl⟩ := List.mem_map.mp ha
  exact (choiceAtom_rho S _ _ _).mp (hd _ ha)

/-- The lifting lemma on a rights document: adjoining one element in no sort keeps base admissibility. -/
theorem adjoin_baseAdmissibleR (X : RightsDoc) (B : VE.Structure.{u}) :
    VE.Rights.BaseAdmissibleR X (VE.Compose.adjoinOne B) ↔ VE.Rights.BaseAdmissibleR X B :=
  VE.Compose.adjoin_baseAdmissibleP (correlate X) (VE.Rights.limPremises X) B

end VE.Readings
