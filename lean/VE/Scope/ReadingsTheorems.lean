import VE.Scope.Readings
import VE.Scope.Theorems

/-! Scope spec 11.3's statements on `governSets` (sc-5rb), as sc-5r's statement stub writes them. The four that take
    `Pinned.JsonWF` (`governSets_preserves`, `governSets_every_choice`, `governSets_strings`,
    `governSets_readings_refused`) wait for sc-1ae's parser lemma: sc-5rc (spec 11.7). -/

namespace VE.Scope
open Lean

/-- `governAt_no_frontier`, restated: with no governed set, the answer is `govern`'s, byte for byte as a value. -/
theorem governSets_no_sets (D : SDoc) (h : governedSetUnits D = []) : governSets D = govern D := by
  simp only [governSets, governSetsWith, h, List.isEmpty_nil, if_true]

/-- The run path answers as the statement (`governFast_eq` per choice). -/
theorem governSetsFast_eq (D : SDoc) : governSetsWith governFast D = governSets D := by
  rw [show governFast = govern from funext governFast_eq]; rfl

/-- `scope_choices`, restated: the choices checked are lf-14d's joint choices over the governed sets. -/
theorem scope_set_choices (D : SDoc) (cs : List VE.Discourse.Choice) (hcs : setChoices D = .ok cs)
    (K : VE.Discourse.Manifest) (n : Nat) (cs' : List VE.Discourse.Choice)
    (hk : VE.Discourse.compatibleChoices K (setShapes D) n = .ok cs') :
    (∀ c ∈ cs', c ∈ cs) ∧ (K.constraints = [] → cs' = cs) := by
  have hcs' : cs = VE.Discourse.allChoices (setShapes D) := by
    unfold setChoices at hcs; split at hcs
    · cases hcs
    · cases hcs; rfl
  subst hcs'
  refine ⟨fun c hc => ?_, fun hK => VE.Discourse.compatibleChoices_unconstrained K hK _ n cs' hk⟩
  obtain ⟨hl, hi, _⟩ := ((VE.Discourse.compatible_sound K _ n cs' hk).1 c).mp hc
  exact (VE.Discourse.mem_allChoices _ c).mpr ⟨hl, hi⟩

theorem faultOf_some (D : SDoc) (rs : List (VE.Discourse.Choice × Except String Json)) (ch : VE.Discourse.Choice)
    (e : String) (hm : (ch, .error e) ∈ rs) : ∃ x, faultOf D rs = some x := by
  unfold faultOf
  split
  · rename_i hf
    have := List.findSome?_eq_none_iff.mp hf _ hm
    simp at this
  · exact ⟨_, rfl⟩

/-- A fault under one choice refuses the document: it is admitted only when every choice is. -/
theorem governSets_choice_refused (D : SDoc) (hs : governedSetUnits D ≠ []) (cs : List VE.Discourse.Choice)
    (hcs : setChoices D = .ok cs) (ch : VE.Discourse.Choice) (hc : ch ∈ cs) (e : String)
    (he : governChoice D ch = .error e) : (governSets D).isOk = false := by
  have hm : (ch, Except.error e) ∈ cs.map fun ch => (ch, govern (atChoice D ch)) :=
    List.mem_map.mpr ⟨ch, hc, by rw [← he]; rfl⟩
  obtain ⟨x, hx⟩ := faultOf_some D _ ch e hm
  have hne : (governedSetUnits D).isEmpty = false := by simpa using hs
  simp only [governSets, governSetsWith, hne, hcs, Bool.false_eq_true, if_false]
  simp only [bind, Except.bind, hx]
  rfl

/-- A fault every choice has is the document's own text, named with no choice (as `govern` would give it). -/
theorem faultOf_every (D : SDoc) (rs : List (VE.Discourse.Choice × Except String Json)) (hn : rs ≠ []) (e : String)
    (h : ∀ p ∈ rs, p.2 = .error e) : faultOf D rs = some e := by
  obtain ⟨⟨ch, r⟩, rest, rfl⟩ := List.exists_cons_of_ne_nil hn
  have hr : r = .error e := h _ (List.mem_cons_self ..)
  subst hr
  unfold faultOf
  simp only [List.findSome?_cons, Option.some.injEq]
  rw [if_pos]
  simp only [List.all_cons, beq_self_eq_true, Bool.true_and, List.all_eq_true]
  intro p hp
  rw [h p (List.mem_cons_of_mem _ hp)]
  simp

/-- A resource limit under a choice is passed on unchanged: UNKNOWN, never a refusal of that choice (9.4 item 4). -/
theorem choiceFault_limit (D : SDoc) (ch : VE.Discourse.Choice) (e : String) (h : e.startsWith "ResourceLimit" = true) :
    choiceFault D ch e = e := by
  simp [choiceFault, h]

/-- More joint choices than the limit: `ResourceLimit` (UNKNOWN), never a truncated product. -/
theorem governSets_limit (D : SDoc) (h : VE.Discourse.productSize (setShapes D) > choiceLimit) :
    governSets D = .error "ResourceLimit: scope choices" := by
  cases he : (governedSetUnits D).isEmpty
  · simp only [governSets, governSetsWith, he, Bool.false_eq_true, if_false, setChoices, h, if_true]
    rfl
  · have : governedSets D = [] := by
      simp [governedSets, List.isEmpty_iff.mp he]
    simp [setShapes, this, VE.Discourse.productSize, choiceLimit] at h

end VE.Scope
