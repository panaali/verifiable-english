import VE.Service.Document
import VE.Scope.Theorems
import VE.Scope.ReadingsTheorems

/-! SC-1b's theorems (docs/spec/scope.md 5.2): the governor status, the front-matter decoder's layout, and the document
    mode's answer on a `scope@0` document. The spec's placeholders (8.1) are pinned here: `Pinned.checkDoc` is
    `VE.Service.Document.checkDoc`, the document mode's entry; `Pinned.checkCore` is `checkCore`, the entry without
    scope's branch; `Pinned.profilesOf` and `Pinned.withUnits` are the mode's; `Pinned.decodeScope` and
    `Pinned.foldGovernors` are SC-1b's own (`VE.Scope.decodeScope`, `VE.Scope.foldGovernors`). -/

namespace VE.Scope
open Lean
open VE.Reports (Status)
open VE.Service.Document (checkDoc checkCore profilesOf withUnits)

theorem mapM_some_mem {st : String → Option Status} {us : List String} {ts : List Status}
    (h : us.mapM st = some ts) : (∀ u ∈ us, ∃ t ∈ ts, st u = some t) ∧ ∀ t ∈ ts, ∃ u ∈ us, st u = some t := by
  induction us generalizing ts with
  | nil => simp only [List.mapM_nil, Option.pure_def, Option.some.injEq] at h; subst h; simp
  | cons u us ih =>
    simp only [List.mapM_cons, Option.pure_def, Option.bind_eq_bind, Option.bind_eq_some_iff,
      Option.some.injEq] at h
    obtain ⟨t, ht, ts', hts, rfl⟩ := h
    obtain ⟨ih1, ih2⟩ := ih hts
    refine ⟨fun v hv => ?_, fun x hx => ?_⟩
    · rcases List.mem_cons.mp hv with rfl | hv
      · exact ⟨t, List.mem_cons_self .., ht⟩
      · obtain ⟨x, hx, e⟩ := ih1 v hv; exact ⟨x, List.mem_cons_of_mem _ hx, e⟩
    · rcases List.mem_cons.mp hx with rfl | hx
      · exact ⟨u, List.mem_cons_self .., ht⟩
      · obtain ⟨v, hv, e⟩ := ih2 x hx; exact ⟨v, List.mem_cons_of_mem _ hv, e⟩

theorem foldl_meet_mem (acc : Status) (xs : List Status) : xs.foldl Status.meet acc ∈ acc :: xs := by
  induction xs generalizing acc with
  | nil => exact List.mem_cons_self ..
  | cons x xs ih =>
    rcases List.mem_cons.mp (ih (acc.meet x)) with e | e
    · rw [List.foldl_cons, e]; unfold Status.meet; split
      · exact List.mem_cons_self ..
      · exact List.mem_cons_of_mem _ (List.mem_cons_self ..)
    · exact List.mem_cons_of_mem _ (List.mem_cons_of_mem _ e)

theorem foldStatus_mem (ts : List Status) (h : ts ≠ []) : VE.Reports.foldStatus ts ∈ ts := by
  unfold VE.Reports.foldStatus
  rcases List.mem_cons.mp (foldl_meet_mem .checked ts) with e | e
  · obtain ⟨t, ht⟩ := List.exists_mem_of_ne_nil ts h
    have := VE.Reports.foldl_meet_rank_le .checked ts t ht
    rw [e] at this ⊢
    cases t <;> simp [Status.rank] at this <;> exact ht
  · exact e

theorem governor_status_weakest (st : String → Option Status) (us : List String) (s : Status)
    (h : governorStatus st us = some s) :
    us ≠ [] ∧ (∀ u ∈ us, ∃ t, st u = some t ∧ s.rank ≤ t.rank) ∧ ∃ u ∈ us, st u = some s := by
  unfold governorStatus at h
  cases hu : us.isEmpty
  · rw [hu] at h; simp only [Bool.false_eq_true, if_false] at h
    cases hm : us.mapM st with
    | none => rw [hm] at h; cases h
    | some ts =>
      rw [hm] at h; simp only [Option.map_some, Option.some.injEq] at h; subst h
      obtain ⟨h1, h2⟩ := mapM_some_mem hm
      have hne : us ≠ [] := by simpa using hu
      refine ⟨hne, fun u hu' => ?_, ?_⟩
      · obtain ⟨t, ht, e⟩ := h1 u hu'
        exact ⟨t, e, VE.Reports.foldl_meet_rank_le .checked ts t ht⟩
      · have hts : ts ≠ [] := by
          obtain ⟨u, hu'⟩ := List.exists_mem_of_ne_nil us hne
          obtain ⟨t, ht, _⟩ := h1 u hu'
          exact List.ne_nil_of_mem ht
        exact h2 _ (foldStatus_mem ts hts)
  · rw [hu] at h; cases h

theorem governor_status_none (st : String → Option Status) (us : List String)
    (h : us = [] ∨ ∃ u ∈ us, st u = none) : governorStatus st us = none := by
  unfold governorStatus
  rcases h with rfl | ⟨u, hu, hn⟩
  · rfl
  · split
    · rfl
    · cases hm : us.mapM st with
      | none => rfl
      | some ts => obtain ⟨t, _, e⟩ := (mapM_some_mem hm).1 u hu; rw [hn] at e; cases e

theorem bind_ok {α β : Type} {x : Except String α} {f : α → Except String β} {b : β} (h : (x >>= f) = .ok b) :
    ∃ a, x = .ok a ∧ f a = .ok b := by
  cases x with
  | error e => cases h
  | ok a => exact ⟨a, rfl, h⟩

theorem decodeBlock_ok (front : Json) (source : String) (re : VE.Readings.Wire.ReadingsEnvironment) (D : SDoc)
    (h : decodeBlock front source re = .ok D) :
    jsonWF? front = true ∧ D.layout = layoutOf front source ∧ D.doc = front ∧ D.block = front.getObjValD "scope" := by
  unfold decodeBlock at h
  cases hi : illFormed front with
  | some p => rw [hi] at h; cases h
  | none =>
    rw [hi] at h
    have hw : jsonWF? front = true := by
      unfold illFormed at hi; split at hi
      · assumption
      · cases hi
    cases hp : decodeParts (front.getObjValD "scope") with
    | error e => rw [hp] at h; cases h
    | ok p => rw [hp] at h; cases h; exact ⟨hw, rfl, rfl, rfl⟩

theorem decodeBlock_layout (front : Json) (source : String) (re : VE.Readings.Wire.ReadingsEnvironment) (D : SDoc)
    (h : decodeBlock front source re = .ok D) : D.layout = layoutOf front source ∧ D.doc = front :=
  ⟨(decodeBlock_ok front source re D h).2.1, (decodeBlock_ok front source re D h).2.2.1⟩

/-- The boundary (sc-1af): the document of a decoded block passes `jsonWF?`, so it is `JsonWF`, and so is its scope
    block (spec 11.3: the payloads are read from it), with no hypothesis on the parser. -/
theorem decodeBlock_jsonWF (front : Json) (source : String) (re : VE.Readings.Wire.ReadingsEnvironment) (D : SDoc)
    (h : decodeBlock front source re = .ok D) : JsonWF D.doc ∧ JsonWF D.block := by
  obtain ⟨hw, _, hd, hb⟩ := decodeBlock_ok front source re D h
  have hf := jsonWF?_sound hw
  exact ⟨hd ▸ hf, hb ▸ jsonWF_getD front hf "scope"⟩

/-- SC-1b's decoder reads the layout of exactly the document's units, in order. -/
theorem decodeScope_layout (front : Json) (D : SDoc) (h : decodeScope front = .ok D) :
    D.layout.map (·.id) = unitIds D.doc := by
  unfold decodeScope at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨hl, hd⟩ := decodeBlock_layout _ _ _ D h
  rw [hl, hd]
  simp [layoutOf, VE.Layout.ofSource, unitIds, List.map_map, Function.comp_def]

/-- The document mode's answer on a scope@0 document is its answer on govern's output, statuses folded. -/
theorem scope_admission (front ans : Json) (h : checkDoc front = .ok ans)
    (hs : "scope@0" ∈ profilesOf front) :
    ∃ D out a, decodeScope front = .ok D ∧ govern D = .ok out ∧
      checkCore (withUnits front out) = .ok a ∧ ans = foldGovernors D a := by
  unfold checkDoc at h
  rw [if_pos hs] at h
  simp only [bind, Except.bind] at h
  split at h
  · cases h
  split at h
  · cases h
  rename_i D hD
  split at h
  · cases h
  rename_i out ho
  split at h
  · cases h
  rename_i a ha
  cases h
  exact ⟨D, out, a, hD, (governFast_eq D) ▸ ho, ha, rfl⟩

/-- Documents without scope@0 are answered exactly as before. -/
theorem scope_absent_unchanged (front : Json) (h : "scope@0" ∉ profilesOf front) :
    checkDoc front = checkCore front := by
  unfold checkDoc
  rw [if_neg h]

/-! ## Per choice over a reading set (scope spec 11.3 and 11.4, sc-5rb)

The document mode's entry is `checkDocSets`, which calls `governSetsWith governFast`; `scope_admission` and
`scope_absent_unchanged` above stay true of `checkDoc`, which `checkDocSets` answers as wherever no set is governed.
The stub's placeholders are pinned here: `Pinned.checkDocSets` is the entry (an alias), and `Pinned.withGoverned` the case it
hands the chain, read off the case's own scope block. -/

namespace Pinned

export VE.Service.Document (checkDocSets)

/-- The case `checkDocSets` hands the chain: GOVERN's units, and its reading sets when the case's scope block governs
    a reading set per choice (11.4). -/
def withGoverned (j out : Json) : Json := match decodeScope j with
  | .ok D => if (governedSetUnits D).isEmpty then withUnits j out else VE.Service.Document.withSets j out
  | .error _ => withUnits j out

end Pinned

/-- `scope_admission` (5.2), restated: the chain checks GOVERN's units and reading sets. -/
theorem scope_admission_sets (front ans : Json) (h : Pinned.checkDocSets front = .ok ans)
    (hs : "scope@0" ∈ VE.Service.Document.profilesOf front) :
    ∃ D out a, decodeScope front = .ok D ∧ governSets D = .ok out ∧
      VE.Service.Document.checkCore (Pinned.withGoverned front out) = .ok a ∧ ans = foldGovernors D a := by
  unfold VE.Service.Document.checkDocSets at h
  rw [if_pos hs] at h
  simp only [bind, Except.bind] at h
  split at h
  · cases h
  split at h
  · cases h
  rename_i D hD
  split at h
  · cases h
  rename_i out ho
  split at h
  · cases h
  rename_i a ha
  cases h
  refine ⟨D, out, a, hD, (governSetsFast_eq D) ▸ ho, ?_, rfl⟩
  unfold Pinned.withGoverned
  rw [hD]
  exact ha

/-- `scope_admission`'s text, kept where no set is governed: the document mode answers exactly as today's `checkDoc`,
    a block or profile fault included (`governSets_no_sets`, and the chain reads `withGoverned` as `withUnits`). -/
theorem checkDocSets_no_sets (front : Json) (h : ∀ D, decodeScope front = .ok D → governedSetUnits D = []) :
    Pinned.checkDocSets front = VE.Service.Document.checkDoc front := by
  unfold VE.Service.Document.checkDocSets VE.Service.Document.checkDoc
  split
  · simp only [bind, Except.bind]
    split
    · rfl
    · cases hD : decodeScope front with
      | error e => rfl
      | ok D =>
        have h0 := h D hD
        simp only [VE.Scope.governSetsWith, h0, List.isEmpty_nil, if_true]
  · rfl

/-- `scope_absent_unchanged`, restated: a document without `scope@0` is `checkCore`'s, as before. -/
theorem checkDocSets_absent_unchanged (front : Json) (h : "scope@0" ∉ VE.Service.Document.profilesOf front) :
    Pinned.checkDocSets front = VE.Service.Document.checkCore front := by
  unfold VE.Service.Document.checkDocSets
  rw [if_neg h]

end VE.Scope
