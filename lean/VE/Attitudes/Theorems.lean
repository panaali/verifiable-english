import VE.Attitudes.Semantics
import VE.NormDefaults.Evidence
import VE.EnglishGrammar.Encode
import VE.Typing
import VE.Discourse.Manifest

/-! The statements of docs/spec/attitudes.md section 6.1 that take `WellFormedAtt`. at-1b proves the five about the
generated names and the elaborated document, from `checkNames` and the `Nodup` check (the spec's proof notes); at-1
adds the rest. -/

namespace VE.Attitudes
universe u

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


/-! ## The frame (spec 2.7): at-1c's seven statements of 6.1 (`table_reviewed` is at-1a's, in `Scale.lean`) -/

/-- A loop of `throwIf`s passes exactly when no item meets its condition. -/
theorem forIn_throwIf {l : List String} {P : String → Bool} {m : String → String}
    (h : (forIn l PUnit.unit fun s _ => do throwIf (P s) (m s); pure (ForInStep.yield PUnit.unit)) =
      (Except.ok PUnit.unit : Except String PUnit)) : ∀ s ∈ l, P s = false := by
  induction l with
  | nil => intro s hs; cases hs
  | cons x xs ih =>
    rw [List.forIn_cons] at h
    obtain ⟨_, h1, h⟩ := ok_of_bind h
    obtain ⟨⟨⟩, h2, h1⟩ := ok_of_bind h1
    cases h1
    intro s hs
    rcases List.mem_cons.1 hs with rfl | hs
    · exact not_of_throwIf h2
    · exact ih h s hs

/-- `checkAtt`'s holder loop and its checks of the conditions and of the parts. -/
theorem checkAtt_conds {A : AttDoc} (h : WellFormedAtt A = true) :
    (∀ s ∈ A.holders, s ∈ A.E.sorts) ∧ checkConds A (condsOf A) = .ok () ∧ checkParts A A.parts = .ok () := by
  have h0 : checkAtt A = .ok () := by
    unfold WellFormedAtt at h
    cases hc : checkAtt A with
    | error e => simp [hc, Except.toBool] at h
    | ok a => rfl
  unfold checkAtt at h0
  obtain ⟨_, _, h0⟩ := ok_of_bind h0
  obtain ⟨⟨⟩, hh, h0⟩ := ok_of_bind h0
  iterate 2 obtain ⟨_, _, h0⟩ := ok_of_bind h0
  dsimp only at h0
  split at h0
  · cases h0
  split at h0
  · iterate 2 obtain ⟨_, _, h0⟩ := ok_of_bind h0
    cases h0
  iterate 4 obtain ⟨_, _, h0⟩ := ok_of_bind h0
  obtain ⟨⟨⟩, h5, h0⟩ := ok_of_bind h0
  obtain ⟨⟨⟩, h6, h0⟩ := ok_of_bind h0
  refine ⟨fun s hs => ?_, h5, h6⟩
  have := forIn_throwIf hh s hs
  simpa using this

theorem checkConds_mem {A : AttDoc} : ∀ {l : List (List String × Cond)}, checkConds A l = .ok () →
    ∀ p ∈ l, checkCond A p.1 p.2 = .ok ()
  | [], _, _, hp => by cases hp
  | _ :: _, h, p, hp => by
    unfold checkConds at h
    obtain ⟨⟨⟩, h1, h⟩ := ok_of_bind h
    cases hp with
    | head => exact h1
    | tail _ hp => exact checkConds_mem h p hp

theorem checkParts_mem {A : AttDoc} : ∀ {l : List Cond}, checkParts A l = .ok () →
    ∀ c ∈ l, checkCond A [] c true = .ok ()
  | [], _, _, hc => by cases hc
  | _ :: _, h, c, hc => by
    unfold checkParts at h
    obtain ⟨⟨⟩, h1, h⟩ := ok_of_bind h
    cases hc with
    | head => exact h1
    | tail _ hc => exact checkParts_mem h c hc

/-- What `checkCond` checks of a condition's key: its slot sort is declared, its content quantifier-free and typed
    over `baseEnv` in the slot's context, its holder sort a holder sort. -/
theorem checkCond_key {A : AttDoc} {Γ : List String} {c : Cond} {part : Bool} {k : Key}
    (hc : checkCond A Γ c part = .ok ()) (hk : c.key A Γ = some k) :
    (∀ s, k.slotSort = some s → s ∈ A.E.sorts) ∧ VE.Norms.Formula.qfree k.content = true ∧
      k.content.check (baseEnv A) k.slotSort.toList = true ∧ A.holders.contains k.holderSort = true := by
  unfold Cond.key at hk
  split at hk
  · split at hk
    · cases hk
      unfold checkCond at hc
      iterate 3 obtain ⟨_, _, hc⟩ := ok_of_bind hc
      split at hc
      · rename_i hsl
        obtain ⟨_, hp, hc⟩ := ok_of_bind hc
        cases hp
        obtain ⟨_, hq, hc⟩ := ok_of_bind hc
        obtain ⟨_, _, hc⟩ := ok_of_bind hc
        obtain ⟨_, hch, _⟩ := ok_of_bind hc
        refine ⟨by simp [hsl], by simpa using not_of_throwIf hq, by simpa [hsl] using not_of_throwIf hch, ‹_›⟩
      · rename_i s t hsl
        obtain ⟨_, h1, hc⟩ := ok_of_bind hc
        iterate 2 obtain ⟨_, _, hc⟩ := ok_of_bind hc
        obtain ⟨_, hp, hc⟩ := ok_of_bind hc
        cases hp
        obtain ⟨_, hq, hc⟩ := ok_of_bind hc
        obtain ⟨_, _, hc⟩ := ok_of_bind hc
        obtain ⟨_, hch, _⟩ := ok_of_bind hc
        refine ⟨fun s' h' => ?_, by simpa using not_of_throwIf hq, by simpa [hsl] using not_of_throwIf hch, ‹_›⟩
        simp only [hsl, Option.map_some, Option.some.injEq] at h'
        subst h'
        simpa using not_of_throwIf h1
    · cases hk
  · cases hk

/-- Each key's facts, from the check of the condition or part it comes from. -/
theorem key_checked {A : AttDoc} (h : WellFormedAtt A = true) : ∀ k ∈ keys A,
    k.holderSort ∈ A.E.sorts ∧ (∀ s, k.slotSort = some s → s ∈ A.E.sorts) ∧
      VE.Norms.Formula.qfree k.content = true ∧ k.content.check (baseEnv A) k.slotSort.toList = true := by
  intro k hk
  obtain ⟨hh, hc, hp⟩ := checkAtt_conds h
  unfold keys at hk
  rw [VE.Reports.mem_dedup, List.mem_filterMap] at hk
  obtain ⟨⟨Γ, c⟩, hm, hkey⟩ := hk
  have hcc : ∃ part, checkCond A Γ c part = .ok () := by
    rcases List.mem_append.1 hm with hm | hm
    · exact ⟨false, checkConds_mem hc _ hm⟩
    · unfold partsOf at hm
      obtain ⟨c', hc', he⟩ := List.mem_map.1 hm
      simp only [Prod.mk.injEq] at he
      obtain ⟨rfl, rfl⟩ := he
      exact ⟨true, checkParts_mem hp _ hc'⟩
  obtain ⟨part, hcc⟩ := hcc
  obtain ⟨h1, h2, h3, h4⟩ := checkCond_key hcc hkey
  exact ⟨hh _ (List.contains_iff_mem.1 h4), h1, h2, h3⟩

theorem wellFormed_append {E : VE.Environment} : ∀ {Γ Δ : List String} {φ : VE.Formula},
    φ.WellFormed E Γ → φ.WellFormed E (Γ ++ Δ) := by
  have ht : ∀ {Γ Δ : List String} {t : VE.Term} {s : String}, t.sortOf E Γ = some s → t.sortOf E (Γ ++ Δ) = some s :=
    fun {Γ Δ t s} h => by
      cases t with
      | var i =>
        simp only [VE.Term.sortOf] at h ⊢
        rw [List.getElem?_append_left (List.getElem?_eq_some_iff.1 h).1]; exact h
      | const c => exact h
  intro Γ Δ φ hφ
  induction φ generalizing Γ with
  | top | bottom => trivial
  | unary p t => obtain ⟨s, hp, h1⟩ := hφ; exact ⟨s, hp, ht h1⟩
  | binary p t u => obtain ⟨s, r, hp, h1, h2⟩ := hφ; exact ⟨s, r, hp, ht h1, ht h2⟩
  | eq t u => obtain ⟨s, h1, h2⟩ := hφ; exact ⟨s, ht h1, ht h2⟩
  | not a ih => exact ih hφ
  | and a b iha ihb | or a b iha ihb | implies a b iha ihb => exact ⟨iha hφ.1, ihb hφ.2⟩
  | all s a ih | ex s a ih => exact ⟨hφ.1, ih (Γ := s :: Γ) hφ.2⟩

/-- `baseEnvAtt` keeps every predicate `baseEnv` declares (a generated name is not declared by `E`). -/
theorem baseEnvAtt_extends (A : AttDoc) (h : WellFormedAtt A = true) : ∀ {Γ : List String} {φ : VE.Formula},
    φ.WellFormed (baseEnv A) Γ → φ.WellFormed (baseEnvAtt A) Γ := by
  have hkeep : ∀ {p sig}, (baseEnv A).predicates p = some sig → (baseEnvAtt A).predicates p = some sig := by
    intro p sig hp
    show (match keyOf A p with | some k => some k.sorts | none => (baseEnv A).predicates p) = some sig
    cases hk : keyOf A p with
    | none => exact hp
    | some k =>
      have hm := List.mem_of_find?_eq_some hk
      have hn : name A k = p := by simpa using List.find?_some hk
      have := (names_fresh A h k hm).1
      rw [hn] at this
      simp [baseEnv, VE.Norms.hide, this] at hp
  have hsort : ∀ (Γ : List String) (t : VE.Term), t.sortOf (baseEnvAtt A) Γ = t.sortOf (baseEnv A) Γ :=
    fun Γ t => by cases t <;> rfl
  intro Γ φ hφ
  induction φ generalizing Γ with
  | top | bottom => trivial
  | unary p t => obtain ⟨s, hp, h1⟩ := hφ; exact ⟨s, hkeep hp, by rw [hsort]; exact h1⟩
  | binary p t u =>
    obtain ⟨s, r, hp, h1, h2⟩ := hφ; exact ⟨s, r, hkeep hp, by rw [hsort]; exact h1, by rw [hsort]; exact h2⟩
  | eq t u => obtain ⟨s, h1, h2⟩ := hφ; exact ⟨s, by rw [hsort]; exact h1, by rw [hsort]; exact h2⟩
  | not a ih => exact ih hφ
  | and a b iha ihb | or a b iha ihb | implies a b iha ihb => exact ⟨iha hφ.1, ihb hφ.2⟩
  | all s a ih | ex s a ih => exact ⟨hφ.1, ih hφ.2⟩

theorem mem_framePairs {A : AttDoc} {k k2 : Key} : (k, k2) ∈ framePairs A ↔
    k ∈ keys A ∧ k2 ∈ keys A ∧ sameSubject k k2 = true ∧ entailsMode A k.mode k2.mode = true := by
  simp only [framePairs, List.mem_flatMap, List.mem_map, List.mem_filter, Bool.and_eq_true, Prod.mk.injEq]
  constructor
  · rintro ⟨a, ha, b, ⟨hb, hs, hm⟩, rfl, rfl⟩
    exact ⟨ha, hb, hs, hm⟩
  · rintro ⟨ha, hb, hs, hm⟩
    exact ⟨k, ha, k2, ⟨hb, hs, hm⟩, rfl, rfl⟩

theorem sameSubject_eq {k k2 : Key} (h : sameSubject k k2 = true) :
    k.holderSort = k2.holderSort ∧ k.slotSort = k2.slotSort ∧ k.content = k2.content := by
  simpa [sameSubject, and_assoc] using h

/-- The key's atom over its own context `closeOver` opens: typed over `baseEnvAtt`, for any key with its sorts. -/
theorem atomAt_wellFormed (A : AttDoc) (h : WellFormedAtt A = true) {k k2 : Key} (hk2 : k2 ∈ keys A)
    (hs : k.holderSort = k2.holderSort ∧ k.slotSort = k2.slotSort) :
    (atomAt A k2).WellFormed (baseEnvAtt A) (k.slotSort.toList ++ [k.holderSort]) := by
  have hp : (baseEnvAtt A).predicates (name A k2) = some k2.sorts := by
    show (match keyOf A (name A k2) with | some k => some k.sorts | none => _) = _
    rw [keyOf_name A h k2 hk2]
  unfold atomAt
  rw [hs.1, hs.2]
  cases hsl : k2.slotSort with
  | none => exact ⟨_, by rw [hp, Key.sorts, hsl]; rfl, rfl⟩
  | some s => exact ⟨_, _, by rw [hp, Key.sorts, hsl]; rfl, rfl, rfl⟩

theorem closeOver_wellFormed (A : AttDoc) {k : Key} {body : VE.Formula} (hh : k.holderSort ∈ A.E.sorts)
    (hs : ∀ s, k.slotSort = some s → s ∈ A.E.sorts)
    (hb : body.WellFormed (baseEnvAtt A) (k.slotSort.toList ++ [k.holderSort])) :
    (closeOver k body).WellFormed (baseEnvAtt A) [] := by
  unfold closeOver
  cases hsl : k.slotSort with
  | none => rw [hsl] at hb; exact ⟨hh, hb⟩
  | some s => rw [hsl] at hb; exact ⟨hh, hs s hsl, hb⟩

/-- Typed over the base vocabulary extended by the generated names (A2). -/
theorem frame_wellFormed (A : AttDoc) (h : WellFormedAtt A = true) :
    ∀ φ ∈ framePremises A, φ.WellFormed (baseEnvAtt A) [] := by
  intro φ hφ
  rcases List.mem_append.1 hφ with hφ | hφ
  · obtain ⟨k, hk, rfl⟩ := List.mem_map.1 hφ
    have hk := (List.mem_filter.1 hk).1
    obtain ⟨hh, hs, _, hc⟩ := key_checked h k hk
    refine closeOver_wellFormed A hh hs ⟨atomAt_wellFormed A h hk ⟨rfl, rfl⟩, ?_⟩
    exact wellFormed_append (baseEnvAtt_extends A h ((VE.check_iff_wellFormed _ _ _).1 hc))
  · obtain ⟨⟨k, k2⟩, hp, rfl⟩ := List.mem_map.1 hφ
    obtain ⟨hk, hk2, hss, _⟩ := mem_framePairs.1 hp
    obtain ⟨hh, hs, _, _⟩ := key_checked h k hk
    obtain ⟨e1, e2, _⟩ := sameSubject_eq hss
    exact closeOver_wellFormed A hh hs ⟨atomAt_wellFormed A h hk ⟨rfl, rfl⟩, atomAt_wellFormed A h hk2 ⟨e1, e2⟩⟩

theorem closeOver_universalQF {k : Key} {a b : VE.Formula} (hb : VE.Norms.Formula.qfree (.implies a b) = true) :
    VE.NormDefaults.UniversalQF (closeOver k (.implies a b)) := by
  unfold VE.NormDefaults.UniversalQF closeOver
  cases k.slotSort <;> exact hb

theorem atomAt_qfree (A : AttDoc) (k : Key) : VE.Norms.Formula.qfree (atomAt A k) = true := by
  unfold atomAt; cases k.slotSort <;> rfl

theorem frame_universalQF (A : AttDoc) (h : WellFormedAtt A = true) :
    ∀ φ ∈ framePremises A, VE.NormDefaults.UniversalQF φ := by
  intro φ hφ
  rcases List.mem_append.1 hφ with hφ | hφ
  · obtain ⟨k, hk, rfl⟩ := List.mem_map.1 hφ
    obtain ⟨_, _, hq, _⟩ := key_checked h k (List.mem_filter.1 hk).1
    exact closeOver_universalQF (by simp [VE.Norms.Formula.qfree, atomAt_qfree, hq])
  · obtain ⟨p, _, rfl⟩ := List.mem_map.1 hφ
    exact closeOver_universalQF (by simp [VE.Norms.Formula.qfree, atomAt_qfree])

/-- `checkNames`'s third check: no generated name contains `:`. -/
theorem checkNames_colon {A : AttDoc} : ∀ {l : List Key}, checkNames A l = .ok () → ∀ k ∈ l,
    ':' ∉ (name A k).data
  | [], _, _, hk => by cases hk
  | k :: rest, h, x, hx => by
    unfold checkNames at h
    obtain ⟨_, _, h⟩ := ok_of_bind h
    obtain ⟨_, _, h⟩ := ok_of_bind h
    obtain ⟨_, h3, h⟩ := ok_of_bind h
    cases hx with
    | head =>
      have h3 := not_of_throwIf h3
      intro hc
      have : (name A k).any (· == ':') = true := by
        rw [show name A k = ⟨(name A k).data⟩ from rfl, VE.EnglishGrammar.DecodeEncode.string_any]
        exact List.any_eq_true.2 ⟨':', hc, by decide⟩
      rw [this] at h3; cases h3
    | tail _ hx => exact checkNames_colon h x hx

theorem colon_split : ∀ {a b c d : List Char}, ':' ∉ a → ':' ∉ c → a ++ ':' :: b = c ++ ':' :: d → a = c ∧ b = d
  | [], _, [], _, _, _, h => by simpa using h
  | [], _, x :: _, _, _, hc, h => by
    simp only [List.nil_append, List.cons_append, List.cons.injEq] at h
    exact absurd (h.1 ▸ List.mem_cons_self) hc
  | x :: _, _, [], _, ha, _, h => by
    simp only [List.nil_append, List.cons_append, List.cons.injEq] at h
    exact absurd (h.1 ▸ List.mem_cons_self) ha
  | x :: a, _, y :: c, _, ha, hc, h => by
    simp only [List.cons_append, List.cons.injEq] at h
    obtain ⟨e1, e2⟩ := colon_split (fun hm => ha (List.mem_cons_of_mem _ hm))
      (fun hm => hc (List.mem_cons_of_mem _ hm)) h.2
    exact ⟨by rw [h.1, e1], e2⟩

theorem keys_nodup (A : AttDoc) (h : WellFormedAtt A = true) : (keys A).Nodup :=
  List.Pairwise.of_map (name A) (fun _ _ hne e => hne (congrArg _ e)) (checkAtt_tail h).2.1

theorem nodup_map_on {α β : Type} {f : α → β} {l : List α} (hl : l.Nodup)
    (hf : ∀ a ∈ l, ∀ b ∈ l, f a = f b → a = b) : (l.map f).Nodup :=
  List.pairwise_map.2 (hl.imp_of_mem (fun ha hb hne e => hne (hf _ ha _ hb e)))

theorem framePairs_nodup (A : AttDoc) (h : WellFormedAtt A = true) : (framePairs A).Nodup := by
  unfold framePairs
  refine List.pairwise_flatMap.2 ⟨fun k _ => nodup_map_on ((keys_nodup A h).filter _)
    (fun _ _ _ _ e => (Prod.mk.inj e).2), (keys_nodup A h).imp (fun hne => ?_)⟩
  intro p hp q hq e
  obtain ⟨_, _, e1⟩ := List.mem_map.1 hp
  obtain ⟨_, _, e2⟩ := List.mem_map.1 hq
  subst e1 e2
  exact hne (congrArg Prod.fst e)

theorem frameLabels_nodup (A : AttDoc) (h : WellFormedAtt A = true) :
    (frameLabels A).length = (framePremises A).length ∧ (frameLabels A).Nodup := by
  refine ⟨by simp [frameLabels, framePremises], ?_⟩
  have hinj := names_injective A h
  have hcolon := checkNames_colon (checkAtt_tail h).1
  unfold frameLabels
  refine List.nodup_append.2 ⟨?_, ?_, ?_⟩
  · refine nodup_map_on ((keys_nodup A h).filter _) (fun k hk k2 hk2 e => ?_)
    have e := congrArg String.data e
    simp only [String.data_append, List.append_cancel_left_eq] at e
    exact hinj k (List.mem_filter.1 hk).1 k2 (List.mem_filter.1 hk2).1 (String.ext e)
  · refine nodup_map_on (framePairs_nodup A h) (fun p hp q hq e => ?_)
    obtain ⟨hp1, hp2, _⟩ := mem_framePairs.1 hp
    obtain ⟨hq1, hq2, _⟩ := mem_framePairs.1 hq
    have e := congrArg String.data e
    simp only [String.data_append, List.append_assoc, List.append_cancel_left_eq] at e
    obtain ⟨e1, e2⟩ := colon_split (hcolon _ hp1) (hcolon _ hq1) e
    exact Prod.ext (hinj _ hp1 _ hq1 (String.ext e1)) (hinj _ hp2 _ hq2 (String.ext e2))
  · intro a ha b hb he
    obtain ⟨k, _, rfl⟩ := List.mem_map.1 ha
    obtain ⟨p, _, rfl⟩ := List.mem_map.1 hb
    have e := congrArg (fun s => (String.data s).take 10) he
    simp [String.data_append] at e

/-- D-A9: no frame pair starts at says, believes, wants or intends, and none ends at knows. -/
theorem framePairs_modes (A : AttDoc) :
    ∀ p ∈ framePairs A, (p.1.mode = .knows ∨ ∃ w, p.1.mode = .thinks w) ∧ p.2.mode ≠ .knows := by
  rintro ⟨k, k2⟩ hp
  have hm := (mem_framePairs.1 hp).2.2.2
  revert hm
  rcases k.mode with a | _ | w <;> rcases k2.mode with b | _ | w2 <;> (try cases a) <;> (try cases b) <;>
    simp [entailsMode]

theorem framePairs_transitive (A : AttDoc) (k1 k2 k3 : Key) (h12 : (k1, k2) ∈ framePairs A)
    (h23 : (k2, k3) ∈ framePairs A) (hne : k1 ≠ k3) : (k1, k3) ∈ framePairs A := by
  obtain ⟨hk1, _, hs12, hm12⟩ := mem_framePairs.1 h12
  obtain ⟨_, hk3, hs23, hm23⟩ := mem_framePairs.1 h23
  obtain ⟨a1, a2, a3⟩ := sameSubject_eq hs12
  obtain ⟨b1, b2, b3⟩ := sameSubject_eq hs23
  refine mem_framePairs.2 ⟨hk1, hk3, by simp [sameSubject, a1, a2, a3, b1, b2, b3], ?_⟩
  have trans := fun {a b c : Word} => @VE.Closure.atLeast_trans Word _ A.scale.toOrder a b c
  have hmode : k1.mode ≠ k3.mode := fun e => hne (by
    obtain ⟨m1, h1, s1, c1⟩ := k1
    obtain ⟨m3, h3, s3, c3⟩ := k3
    simp only at e a1 a2 a3 b1 b2 b3
    rw [e, a1, a2, a3, b1, b2, b3])
  revert hm12 hm23 hmode
  rcases k1.mode with a | _ | w1 <;> rcases k2.mode with b | _ | w2 <;> rcases k3.mode with c | _ | w3 <;>
    (try cases a) <;> (try cases b) <;> (try cases c) <;> simp only [entailsMode] <;> try simp
  · intro p i hm h1 _ h2
    exact ⟨p, ⟨i, hm⟩, trans h1 h2⟩
  · intro _ h1 _ h2 hw
    exact ⟨hw, trans h1 h2⟩

/-- The expansion step of conservativity: empty attitude relations satisfy every frame premise, over any
    structure. (Drafts 1–4 also called it the pack's PK-1 `vocabulary` expansion step; the pack is a `constraint`
    pack, section 2.9.) -/
theorem empty_relations_frame (A : AttDoc) (S : VE.Structure.{u}) :
    VE.Norms.Sat (interp A ⟨S, fun _ _ => False⟩) (framePremises A) := by
  have hno : ∀ k ∈ keys A, ∀ vs, ¬ (interp A ⟨S, fun _ _ => False⟩).relation (name A k) vs := by
    intro k hk vs
    have hs : ((keys A).find? (fun k2 => name A k2 == name A k)).isSome :=
      List.find?_isSome.2 ⟨k, hk, by simp⟩
    obtain ⟨k2, h2⟩ := Option.isSome_iff_exists.1 hs
    show ¬ (match keyOf A (name A k) with | some k => False | none => _)
    unfold keyOf; rw [h2]; exact id
  have hatom : ∀ k ∈ keys A, ∀ ρ, ¬ (atomAt A k).denote (interp A ⟨S, fun _ _ => False⟩) ρ := by
    intro k hk ρ
    unfold atomAt
    cases k.slotSort with
    | none => rintro ⟨v, _, hr⟩; exact hno k hk _ hr
    | some _ => rintro ⟨v, w, _, _, hr⟩; exact hno k hk _ hr
  have hclose : ∀ k ∈ keys A, ∀ φ, (closeOver k (.implies (atomAt A k) φ)).denote
      (interp A ⟨S, fun _ _ => False⟩) [] := by
    intro k hk φ
    unfold closeOver
    cases k.slotSort with
    | none => intro v _ ha; exact absurd ha (hatom k hk _)
    | some _ => intro v _ x _ ha; exact absurd ha (hatom k hk _)
  intro a ha
  rcases List.mem_append.1 ha with ha | ha
  · obtain ⟨k, hk, rfl⟩ := List.mem_map.1 ha
    exact hclose k (List.mem_filter.1 hk).1 _
  · obtain ⟨⟨k, k2⟩, hp, rfl⟩ := List.mem_map.1 ha
    exact hclose k (mem_framePairs.1 hp).1 _

/-! ## Intended models and the seed closure (spec 2.8): at-1d's seven statements of 6.1 -/

/-- Frame pairs relate keys with the same sorts. -/
theorem sorts_of_pair {A : AttDoc} {k k2 : Key} (hp : (k, k2) ∈ framePairs A) : k.sorts = k2.sorts := by
  obtain ⟨e1, e2, _⟩ := sameSubject_eq (mem_framePairs.1 hp).2.2.1
  simp only [Key.sorts, e1, e2]

/-- A path of frame pairs ends at a key of the document, by a last pair, with its start's sorts. -/
theorem path_pairs {A : AttDoc} {k k2 : Key}
    (hp : VE.Closure.Path (fun a b => (a, b) ∈ framePairs A) k k2) :
    k2 ∈ keys A ∧ k.sorts = k2.sorts ∧ ∃ k1, (k1, k2) ∈ framePairs A := by
  induction hp with
  | edge h => exact ⟨(mem_framePairs.1 h).2.1, sorts_of_pair h, _, h⟩
  | cons h _ ih => exact ⟨ih.1, (sorts_of_pair h).trans ih.2.1, ih.2.2⟩

/-- Frame premise 1 as a fact of every intended model. -/
theorem knows_factive (A : AttDoc) (m : AttModel.{u} A) (hI : Intended A m) (k : Key) (hk : k ∈ keys A)
    (hm : k.mode = .knows) (vs : List m.S.Carrier) (hJ : m.J k vs) : contentAt m.S k vs :=
  hI.2.1 k hk hm vs hJ

/-- The frame closure of a typed seed whose knowing members have true contents is intended. -/
theorem seed_intended (A : AttDoc) (S : VE.Structure.{u}) (seed : List (Key × List S.Carrier))
    (hseed : ∀ p ∈ seed, p.1 ∈ keys A ∧ VE.TupleTyped S p.1.sorts p.2)
    (hfact : ∀ p ∈ seed, p.1.mode = .knows → contentAt S p.1 p.2) : Intended A ⟨S, seedClosure A seed⟩ := by
  refine ⟨?_, ?_, ?_⟩
  · rintro k2 vs ⟨k, hm, rfl | hp⟩
    · exact hseed _ hm
    · obtain ⟨hk2, e, _⟩ := path_pairs hp
      exact ⟨hk2, e ▸ (hseed _ hm).2⟩
  · rintro k2 _ hkn vs ⟨k, hm, rfl | hp⟩
    · exact hfact _ hm hkn
    · obtain ⟨_, _, k1, h1⟩ := path_pairs hp
      exact absurd hkn ((framePairs_modes A _ h1).2)
  · rintro ⟨k1, k2⟩ hp vs ⟨k, hm, hr⟩
    refine ⟨k, hm, .inr ?_⟩
    rcases hr with rfl | hr
    · exact .edge hp
    · exact VE.Closure.Path.trans hr (.edge hp)

/-- Every intended model holding the seed holds its frame closure. -/
theorem seed_least (A : AttDoc) (m : AttModel.{u} A) (hI : Intended A m) (seed : List (Key × List m.S.Carrier))
    (hs : ∀ p ∈ seed, m.J p.1 p.2) : ∀ k vs, seedClosure A seed k vs → m.J k vs := by
  rintro k2 vs ⟨k, hm, rfl | hp⟩
  · exact hs _ hm
  · have hJ := hs _ hm
    clear hm
    induction hp with
    | edge h => exact hI.2.2 _ h vs hJ
    | cons h _ ih => exact ih (hI.2.2 _ h vs hJ)

/-- Nothing beyond the frame (F3, edit 2): a seed forces an attitude exactly when frame pairs reach it from a seed
    member at the same tuple. No closure under consequence or conjunction, nothing across holders, contents or
    tuples. -/
theorem forced_iff_reachable (A : AttDoc) (S : VE.Structure.{u}) (seed : List (Key × List S.Carrier))
    (hseed : ∀ p ∈ seed, p.1 ∈ keys A ∧ VE.TupleTyped S p.1.sorts p.2)
    (hfact : ∀ p ∈ seed, p.1.mode = .knows → contentAt S p.1 p.2) (k : Key) (vs : List S.Carrier) :
    (∀ J : Key → List S.Carrier → Prop, Intended A ⟨S, J⟩ → (∀ p ∈ seed, J p.1 p.2) → J k vs) ↔
      seedClosure A seed k vs :=
  ⟨fun hf => hf _ (seed_intended A S seed hseed hfact) (fun p hp => ⟨p.1, hp, .inl rfl⟩),
    fun hr J hI hs => seed_least A ⟨S, J⟩ hI seed hs k vs hr⟩

/-- The audit's requirement (R 2.2): any attitude other than knowing may be held of a false content; an instance
    of `seed_intended` with the seed `[(k, vs)]`. No hypothesis about the content appears. -/
theorem mistaken_belief_admissible (A : AttDoc) (S : VE.Structure.{u}) (k : Key) (hk : k ∈ keys A)
    (hm : k.mode ≠ .knows) (vs : List S.Carrier) (hvs : VE.TupleTyped S k.sorts vs) :
    ∃ J : Key → List S.Carrier → Prop, Intended A ⟨S, J⟩ ∧ J k vs := by
  refine ⟨seedClosure A [(k, vs)], seed_intended A S [(k, vs)] ?_ ?_, k, List.mem_singleton_self _, .inl rfl⟩
  · intro p hp; rw [List.mem_singleton.1 hp]; exact ⟨hk, hvs⟩
  · intro p hp hkn; rw [List.mem_singleton.1 hp] at hkn; exact absurd hkn hm

/-- A name `baseEnv` declares is no generated name (`names_fresh`). -/
theorem keyOf_base {A : AttDoc} (h : WellFormedAtt A = true) {p : String} {sig : List String}
    (hp : (baseEnv A).predicates p = some sig) : keyOf A p = none := by
  cases hk : keyOf A p with
  | none => rfl
  | some k =>
    have hn : name A k = p := by simpa using List.find?_some hk
    have := (names_fresh A h k (List.mem_of_find?_eq_some hk)).1
    rw [hn] at this
    simp [baseEnv, VE.Norms.hide, this] at hp

/-- A formula over `baseEnv` means on `interp` what it means on the base structure, at valuations that agree on its
    context: it names no generated name. -/
theorem denote_interp_base {A : AttDoc} (h : WellFormedAtt A = true) (m : AttModel.{u} A) :
    ∀ {Γ : List String} {φ : VE.Formula} {ρ ρ' : List m.S.Carrier}, φ.WellFormed (baseEnv A) Γ →
      (∀ i < Γ.length, ρ[i]? = ρ'[i]?) → (φ.denote (interp A m) ρ ↔ φ.denote m.S ρ') := by
  have ht : ∀ {Γ : List String} {t : VE.Term} {s : String} {ρ ρ' : List m.S.Carrier},
      t.sortOf (baseEnv A) Γ = some s → (∀ i < Γ.length, ρ[i]? = ρ'[i]?) →
      t.denote (interp A m) ρ = t.denote m.S ρ' := by
    intro Γ t s ρ ρ' hs hρ
    cases t with
    | var i =>
      simp only [VE.Term.sortOf] at hs
      exact hρ i (List.getElem?_eq_some_iff.1 hs).1
    | const c => rfl
  have hr : ∀ {p : String} {sig : List String} (vs : List m.S.Carrier), (baseEnv A).predicates p = some sig →
      ((interp A m).relation p vs ↔ m.S.relation p vs) := by
    intro p sig vs hp
    show (match keyOf A p with | some k => m.J k vs | none => m.S.relation p vs) ↔ _
    rw [keyOf_base h hp]
  have hcons : ∀ {Γ : List String} {ρ ρ' : List m.S.Carrier} (s : String) (v : m.S.Carrier),
      (∀ i < Γ.length, ρ[i]? = ρ'[i]?) → ∀ i < (s :: Γ).length, (v :: ρ)[i]? = (v :: ρ')[i]? := by
    intro Γ ρ ρ' s v hρ i hi
    cases i with
    | zero => rfl
    | succ i => exact hρ i (Nat.lt_of_succ_lt_succ hi)
  intro Γ φ
  induction φ generalizing Γ with
  | top | bottom => intros; exact Iff.rfl
  | unary p t =>
    intro ρ ρ' hφ hρ
    obtain ⟨s, hp, h1⟩ := hφ
    show (∃ v, _ ∧ _) ↔ (∃ v, _ ∧ _)
    rw [ht h1 hρ]
    exact exists_congr fun v => and_congr_right fun _ => hr _ hp
  | binary p t u =>
    intro ρ ρ' hφ hρ
    obtain ⟨s, r, hp, h1, h2⟩ := hφ
    show (∃ v w, _ ∧ _ ∧ _) ↔ (∃ v w, _ ∧ _ ∧ _)
    rw [ht h1 hρ, ht h2 hρ]
    exact exists_congr fun v => exists_congr fun w => and_congr_right fun _ => and_congr_right fun _ => hr _ hp
  | eq t u =>
    intro ρ ρ' hφ hρ
    obtain ⟨s, h1, h2⟩ := hφ
    show (∃ v, _ ∧ _) ↔ (∃ v, _ ∧ _)
    rw [ht h1 hρ, ht h2 hρ]
    exact Iff.rfl
  | not a ih => intro ρ ρ' hφ hρ; exact not_congr (ih hφ hρ)
  | and a b iha ihb => intro ρ ρ' hφ hρ; exact and_congr (iha hφ.1 hρ) (ihb hφ.2 hρ)
  | or a b iha ihb => intro ρ ρ' hφ hρ; exact or_congr (iha hφ.1 hρ) (ihb hφ.2 hρ)
  | implies a b iha ihb => intro ρ ρ' hφ hρ; exact imp_congr (iha hφ.1 hρ) (ihb hφ.2 hρ)
  | all s a ih =>
    intro ρ ρ' hφ hρ
    exact forall_congr' fun v => imp_congr_right fun _ => ih hφ.2 (hcons s v hρ)
  | ex s a ih =>
    intro ρ ρ' hφ hρ
    exact exists_congr fun v => and_congr_right fun _ => ih hφ.2 (hcons s v hρ)

theorem tupleTyped_interp (A : AttDoc) (m : AttModel.{u} A) : ∀ (ss : List String) (vs : List m.S.Carrier),
    VE.TupleTyped (interp A m) ss vs ↔ VE.TupleTyped m.S ss vs
  | [], [] | [], _ :: _ | _ :: _, [] => Iff.rfl
  | _ :: ss, _ :: vs => and_congr Iff.rfl (tupleTyped_interp A m ss vs)

/-- `closeOver k body` holds exactly when `body` holds at every typed tuple of `k`, read with the slot as variable 0. -/
theorem closeOver_denote (S : VE.Structure.{u}) (k : Key) (body : VE.Formula) :
    (closeOver k body).denote S [] ↔ ∀ vs, VE.TupleTyped S k.sorts vs → body.denote S vs.reverse := by
  unfold closeOver Key.sorts
  cases k.slotSort with
  | none =>
    refine ⟨fun hb vs hT => ?_, fun hb v hv => hb [v] ⟨hv, trivial⟩⟩
    rcases vs with _ | ⟨v, _ | ⟨_, _⟩⟩ <;> simp only [VE.TupleTyped, Option.toList, and_false] at hT
    exact hb v hT.1
  | some s =>
    refine ⟨fun hb vs hT => ?_, fun hb v hv w hw => hb [v, w] ⟨hv, hw, trivial⟩⟩
    rcases vs with _ | ⟨v, _ | ⟨w, _ | ⟨_, _⟩⟩⟩ <;> simp only [VE.TupleTyped, Option.toList, and_false] at hT
    exact hb v hT.1 w hT.2.1

/-- A key's atom, read at a typed tuple reversed, is its relation in `J`. -/
theorem atomAt_interp {A : AttDoc} (h : WellFormedAtt A = true) (m : AttModel.{u} A) {k : Key} (hk : k ∈ keys A)
    {vs : List m.S.Carrier} (hT : VE.TupleTyped m.S k.sorts vs) :
    (atomAt A k).denote (interp A m) vs.reverse ↔ m.J k vs := by
  have hr : ∀ ws, (interp A m).relation (name A k) ws ↔ m.J k ws := fun ws => by
    show (match keyOf A (name A k) with | some k => m.J k ws | none => _) ↔ _
    rw [keyOf_name A h k hk]
  unfold atomAt
  unfold Key.sorts at hT
  cases hs : k.slotSort with
  | none =>
    rw [hs] at hT
    rcases vs with _ | ⟨v, _ | ⟨_, _⟩⟩ <;> simp only [VE.TupleTyped, Option.toList, and_false] at hT
    exact ⟨fun ⟨_, hx, hrel⟩ => by cases hx; exact (hr _).1 hrel, fun hJ => ⟨v, rfl, (hr _).2 hJ⟩⟩
  | some s =>
    rw [hs] at hT
    rcases vs with _ | ⟨v, _ | ⟨w, _ | ⟨_, _⟩⟩⟩ <;> simp only [VE.TupleTyped, Option.toList, and_false] at hT
    exact ⟨fun ⟨_, _, h1, h2, hrel⟩ => by cases h1; cases h2; exact (hr _).1 hrel,
      fun hJ => ⟨v, w, rfl, rfl, (hr _).2 hJ⟩⟩

/-- A key's content at a typed tuple is its content on `interp` at the tuple reversed (the holder's extra binder
    changes nothing: closed contents are typed in `[]`, slot contents in `[s]`). -/
theorem contentAt_interp {A : AttDoc} (h : WellFormedAtt A = true) (m : AttModel.{u} A) {k : Key} (hk : k ∈ keys A)
    {vs : List m.S.Carrier} (hT : VE.TupleTyped m.S k.sorts vs) :
    contentAt m.S k vs ↔ k.content.denote (interp A m) vs.reverse := by
  have hc := (VE.check_iff_wellFormed _ _ _).1 (key_checked h k hk).2.2.2
  unfold Key.sorts at hT
  cases hs : k.slotSort with
  | none =>
    rw [hs] at hT hc
    rcases vs with _ | ⟨v, _ | ⟨_, _⟩⟩ <;> simp only [VE.TupleTyped, Option.toList, and_false] at hT
    simp only [contentAt, hs, true_and, List.reverse_cons, List.reverse_nil, List.nil_append]
    exact (denote_interp_base h m hc (fun i hi => absurd hi (Nat.not_lt_zero i))).symm
  | some s =>
    rw [hs] at hT hc
    rcases vs with _ | ⟨v, _ | ⟨w, _ | ⟨_, _⟩⟩⟩ <;> simp only [VE.TupleTyped, Option.toList, and_false] at hT
    simp only [contentAt, hs, Option.isSome_some, true_and, List.reverse_cons, List.reverse_nil, List.nil_append,
      List.cons_append]
    refine (denote_interp_base h m hc (fun i hi => ?_)).symm
    cases i with
    | zero => rfl
    | succ i => exact absurd hi (by simp)

/-- Faithfulness, the frame: the frame premises hold exactly when the relations mean what `Intended` says. -/
theorem frame_iff_intended (A : AttDoc) (h : WellFormedAtt A = true) (m : AttModel.{u} A)
    (hJ : ∀ k vs, m.J k vs → k ∈ keys A ∧ VE.TupleTyped m.S k.sorts vs) :
    VE.Norms.Sat (interp A m) (framePremises A) ↔ Intended A m := by
  have hfac : ∀ k ∈ knowsKeys A,
      ((factive A k).denote (interp A m) [] ↔ ∀ vs, m.J k vs → contentAt m.S k vs) := by
    intro k hk
    have hk := (List.mem_filter.1 hk).1
    rw [factive, closeOver_denote]
    constructor
    · intro hb vs hJk
      have hT := (hJ k vs hJk).2
      exact (contentAt_interp h m hk hT).2 (hb vs ((tupleTyped_interp A m _ _).2 hT) ((atomAt_interp h m hk hT).2 hJk))
    · intro hc vs hT ha
      have hT := (tupleTyped_interp A m _ _).1 hT
      exact (contentAt_interp h m hk hT).1 (hc vs ((atomAt_interp h m hk hT).1 ha))
  have hent : ∀ p ∈ framePairs A, ((entails A p).denote (interp A m) [] ↔ ∀ vs, m.J p.1 vs → m.J p.2 vs) := by
    rintro ⟨k, k2⟩ hp
    obtain ⟨hk, hk2, _⟩ := mem_framePairs.1 hp
    have e := sorts_of_pair hp
    show (closeOver k (.implies (atomAt A k) (atomAt A k2))).denote _ [] ↔ _
    rw [closeOver_denote]
    constructor
    · intro hb vs hJk
      have hT := (hJ k vs hJk).2
      exact (atomAt_interp h m hk2 (e ▸ hT)).1 (hb vs ((tupleTyped_interp A m _ _).2 hT) ((atomAt_interp h m hk hT).2 hJk))
    · intro hc vs hT ha
      have hT := (tupleTyped_interp A m _ _).1 hT
      exact (atomAt_interp h m hk2 (e ▸ hT)).2 (hc vs ((atomAt_interp h m hk hT).1 ha))
  unfold VE.Norms.Sat framePremises
  constructor
  · intro hS
    refine ⟨hJ, fun k hk hm => ?_, fun p hp => ?_⟩
    · have hkk : k ∈ knowsKeys A := List.mem_filter.2 ⟨hk, by simp [hm]⟩
      exact (hfac k hkk).1 (hS _ (List.mem_append_left _ (List.mem_map_of_mem hkk)))
    · exact (hent p hp).1 (hS _ (List.mem_append_right _ (List.mem_map_of_mem hp)))
  · intro hI a ha
    rcases List.mem_append.1 ha with ha | ha
    · obtain ⟨k, hk, rfl⟩ := List.mem_map.1 ha
      exact (hfac k hk).2 (hI.2.1 k (List.mem_filter.1 hk).1 (by simpa using (List.mem_filter.1 hk).2))
    · obtain ⟨p, hp, rfl⟩ := List.mem_map.1 ha
      exact (hent p hp).2 (hI.2.2 p hp)

/-- R 5's collapse (repaired, A3): when a frame pair links the two keys, `(ck ∧ a) ∨ ct` is `ct`. -/
theorem guard_collapse (A : AttDoc) (m : AttModel.{u} A) (hI : Intended A m) (Γ : List String)
    (ρ : VE.Valuation m.S) (ck ct : Cond) (a : AFormula) (k kt : Key) (hk : ck.key A Γ = some k)
    (hkt : ct.key A Γ = some kt) (hp : (k, kt) ∈ framePairs A) (hh : ck.holder = ct.holder)
    (hsl : ck.slot.map (·.2) = ct.slot.map (·.2)) :
    AFormula.denote A m Γ ρ (.or (.and (.att ck) a) (.att ct)) ↔ AFormula.denote A m Γ ρ (.att ct) := by
  refine ⟨?_, .inr⟩
  rintro (⟨⟨k', hk', vh, hvh, hs⟩, _⟩ | hc)
  · rw [hk] at hk'
    cases hk'
    refine ⟨kt, hkt, vh, hh ▸ hvh, ?_⟩
    have hJ := hI.2.2 _ hp
    revert hsl
    revert hs
    rcases ck.slot with _ | ⟨_, t1⟩ <;> rcases ct.slot with _ | ⟨_, t2⟩ <;> intro hs hsl
    · exact hJ _ hs
    · simp at hsl
    · simp at hsl
    · obtain rfl : t1 = t2 := by simpa using hsl
      obtain ⟨vx, hvx, hJx⟩ := hs
      exact ⟨vx, hvx, hJ _ hJx⟩
  · exact hc

end VE.Attitudes
