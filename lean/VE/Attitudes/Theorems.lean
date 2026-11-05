import VE.Attitudes.Syntax

/-! The statements of docs/spec/attitudes.md section 6.1 that take `WellFormedAtt`. at-1b proves the five about the
generated names and the elaborated document, from `checkNames` and the `Nodup` check (the spec's proof notes); at-1
adds the rest. -/

namespace VE.Attitudes

theorem ok_of_bind {α β : Type} {x : Except String α} {f : α → Except String β} {b : β}
    (h : (x >>= f) = .ok b) : ∃ a, x = .ok a ∧ f a = .ok b := by
  cases x with
  | error e => cases h
  | ok a => exact ⟨a, rfl, h⟩

/-- `throwIf` passes exactly when its condition is false. -/
theorem not_of_throwIf {b : Bool} {m : String} (h : throwIf b m = .ok ()) : b = false := by
  cases b
  · rfl
  · cases h

/-- The last steps of `checkAtt`: the names, then their distinctness, then W1's check of the elaborated document. -/
theorem checkAtt_tail {A : AttDoc} (h : WellFormedAtt A = true) :
    checkNames A (keys A) = .ok () ∧ ((keys A).map (name A)).Nodup ∧
      ∃ D, toNorms A = some D ∧ VE.Norms.validate D = .ok () := by
  have h0 : checkAtt A = .ok () := by
    unfold WellFormedAtt at h
    cases hc : checkAtt A with
    | error e => simp [hc, Except.toBool] at h
    | ok a => rfl
  unfold checkAtt at h0
  iterate 4 obtain ⟨_, _, h0⟩ := ok_of_bind h0
  dsimp only at h0
  split at h0
  · cases h0
  split at h0
  · iterate 2 obtain ⟨_, _, h0⟩ := ok_of_bind h0
    cases h0
  iterate 7 obtain ⟨_, _, h0⟩ := ok_of_bind h0
  obtain ⟨_, hn, h0⟩ := ok_of_bind h0
  obtain ⟨_, hd, h0⟩ := ok_of_bind h0
  refine ⟨hn, by simpa using not_of_throwIf hd, ?_⟩
  split at h0
  · cases h0
  · exact ⟨_, ‹_›, h0⟩

/-- `checkNames`'s three checks, for each key of the list it passes. -/
theorem checkNames_mem {A : AttDoc} : ∀ {l : List Key}, checkNames A l = .ok () → ∀ k ∈ l,
    A.E.predicates (name A k) = none ∧ (name A k).utf8ByteSize ≤ 64 ∧
      name A k ∉ A.regulated.map (·.name) ++ A.definitions.map (·.name)
  | [], _, _, hk => by cases hk
  | k :: rest, h, x, hx => by
    unfold checkNames at h
    obtain ⟨_, h1, h⟩ := ok_of_bind h
    obtain ⟨_, h2, h⟩ := ok_of_bind h
    obtain ⟨_, _, h⟩ := ok_of_bind h
    cases hx with
    | head =>
      have h1 := not_of_throwIf h1
      have h2 := not_of_throwIf h2
      obtain ⟨hp, hc⟩ := Bool.or_eq_false_iff.1 h1
      refine ⟨Option.not_isSome_iff_eq_none.1 (by simp only [hp]; decide), by simpa using h2, fun hm => ?_⟩
      rw [List.contains_iff_mem.2 hm] at hc
      cases hc
    | tail _ hx => exact checkNames_mem h x hx

theorem inj_of_nodup_map {α β : Type} {f : α → β} : ∀ {l : List α}, (l.map f).Nodup →
    ∀ a ∈ l, ∀ b ∈ l, f a = f b → a = b
  | [], _, _, ha, _, _, _ => by cases ha
  | x :: xs, h, a, ha, b, hb, he => by
    rw [List.map_cons, List.nodup_cons] at h
    cases ha with
    | head =>
      cases hb with
      | head => rfl
      | tail _ hb => exact absurd (he ▸ List.mem_map_of_mem hb) h.1
    | tail _ ha =>
      cases hb with
      | head => exact absurd (he.symm ▸ List.mem_map_of_mem ha) h.1
      | tail _ hb => exact inj_of_nodup_map h.2 a ha b hb he

theorem names_fresh (A : AttDoc) (h : WellFormedAtt A = true) :
    ∀ k ∈ keys A, A.E.predicates (name A k) = none ∧ (name A k).utf8ByteSize ≤ 64 ∧
      name A k ∉ A.regulated.map (·.name) ++ A.definitions.map (·.name) :=
  checkNames_mem (checkAtt_tail h).1

theorem names_injective (A : AttDoc) (h : WellFormedAtt A = true) :
    ∀ k ∈ keys A, ∀ k2 ∈ keys A, name A k = name A k2 → k = k2 :=
  inj_of_nodup_map (checkAtt_tail h).2.1

theorem keyOf_name (A : AttDoc) (h : WellFormedAtt A = true) : ∀ k ∈ keys A, keyOf A (name A k) = some k := by
  intro k hk
  unfold keyOf
  have hs : ((keys A).find? (fun k2 => name A k2 == name A k)).isSome :=
    List.find?_isSome.2 ⟨k, hk, by simp⟩
  obtain ⟨k2, h2⟩ := Option.isSome_iff_exists.1 hs
  have hp := List.find?_some h2
  have hm := List.mem_of_find?_eq_some h2
  rw [h2, names_injective A h k2 hm k hk (by simpa using hp)]

/-- A name `keyOf` answers for is one of the generated names, so `E` does not declare it; so `envAtt` keeps every
    predicate `E` declares. -/
theorem envAtt_keeps (A : AttDoc) (h : WellFormedAtt A = true) {p : String} {sig : List String}
    (hp : A.E.predicates p = some sig) : (envAtt A).predicates p = some sig := by
  show (match keyOf A p with | some k => some k.sorts | none => A.E.predicates p) = some sig
  cases hk : keyOf A p with
  | none => exact hp
  | some k =>
    have hm := List.mem_of_find?_eq_some hk
    have hn : name A k = p := by simpa using List.find?_some hk
    have := (names_fresh A h k hm).1
    rw [hn, hp] at this
    cases this

theorem envAtt_extends (A : AttDoc) (h : WellFormedAtt A = true) (Γ : List String) (φ : VE.Formula)
    (hφ : φ.WellFormed A.E Γ) : φ.WellFormed (envAtt A) Γ := by
  have hsort : ∀ (Γ : List String) (t : VE.Term), t.sortOf (envAtt A) Γ = t.sortOf A.E Γ := fun Γ t => by
    cases t <;> rfl
  induction φ generalizing Γ with
  | top | bottom => trivial
  | unary p t =>
    obtain ⟨s, hp, ht⟩ := hφ
    exact ⟨s, envAtt_keeps A h hp, by rw [hsort]; exact ht⟩
  | binary p t u =>
    obtain ⟨s, r, hp, ht, hu⟩ := hφ
    exact ⟨s, r, envAtt_keeps A h hp, by rw [hsort]; exact ht, by rw [hsort]; exact hu⟩
  | eq t u =>
    obtain ⟨s, ht, hu⟩ := hφ
    exact ⟨s, by rw [hsort]; exact ht, by rw [hsort]; exact hu⟩
  | not a ih => exact ih Γ hφ
  | and a b iha ihb | or a b iha ihb | implies a b iha ihb => exact ⟨iha Γ hφ.1, ihb Γ hφ.2⟩
  | all s a ih | ex s a ih => exact ⟨hφ.1, ih (s :: Γ) hφ.2⟩

theorem toNorms_wellFormed (A : AttDoc) (h : WellFormedAtt A = true) :
    ∃ D, toNorms A = some D ∧ VE.Norms.WellFormed D = true := by
  obtain ⟨D, hD, hv⟩ := (checkAtt_tail h).2.2
  exact ⟨D, hD, by simp [VE.Norms.WellFormed, hv]⟩

end VE.Attitudes
