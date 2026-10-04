import VE.Readings.Separate

/-! `decision_only_sound` (docs/spec/composition-s1.md 1.7, 8.3).

`decisionOnly` answers the default twin's exception key only when `twinDocs` holds: the default reading's
elaborated document is the strict reading's through `relaxTo` (`relaxDoc`), and so are its generated keys, its
selectable rules and everything else the semantics reads. The proof has three parts.

* **Force.** Where the twin's exception predicate is false, a document and its relaxed twin decide every
  predicate alike and their rules select alike (`decides_relax`, `selects_relax`). This is
  `force_agrees_off_exception` for a whole document: the twin is the only rule on its act, so no other rule's
  blocking, dominance or exceptions read it, and the twin itself is neither blocked nor dominated.
* **Expansion.** Over one base on which the exception predicate is false, the two canonical expansions give
  every formula of the strict document the same truth (`canon_relax`): the relaxed expansion agrees below every
  layer with the strict document's meanings (by the force part), so `subst_denote` applies to it.
* **Assembly.** The completions of the two readings over one base and tables are one structure when the
  exception table is empty (`withTables_twin`); admissibility and every probe value then agree. -/
namespace VE.Readings
open VE.Norms (Regulated Sat tupleVal envAt size)
open VE.SoftNorms (SoftNode SoftDoc SoftValid soften WellFormedSoft ValueSoft canon exceptedF act actKey
  dualPerm dualOblig Incompatible LiveD StrictYieldsD StrictSelectsD StrictDecidesD BlockedD EligibleD DomWithD
  EffD AppliesSoftD YieldsSoftD SelectsSoftD DecidesSoftD rulesOn mem_rulesOn mem_childrenIn_iff)
open VE.Rights (RightsDoc correlate BaseAdmissibleR)
open VE.Compose (Content)
universe u

/-! ## The relaxed document -/

/-- `C` with the twin's name relaxed to the default twin. -/
def relaxDoc (C : SoftDoc) (Nd : SoftNode) : SoftDoc :=
  { C with T := { C.T with nodes := C.T.nodes.map (relaxTo Nd) } }

theorem relaxTo_name (Nd M : SoftNode) : (relaxTo Nd M).name = M.name := by unfold relaxTo; split <;> rfl
theorem relaxTo_pred (Nd M : SoftNode) : (relaxTo Nd M).pred = M.pred := by unfold relaxTo; split <;> rfl
theorem relaxTo_sign (Nd M : SoftNode) : (relaxTo Nd M).sign = M.sign := by unfold relaxTo; split <;> rfl
theorem relaxTo_over (Nd M : SoftNode) : (relaxTo Nd M).over = M.over := by unfold relaxTo; split <;> rfl
theorem relaxTo_alterable (Nd M : SoftNode) : (relaxTo Nd M).alterable = M.alterable := by
  unfold relaxTo; split <;> rfl

theorem relaxTo_of_ne {Nd M : SoftNode} (h : M.name ≠ Nd.name) : relaxTo Nd M = M := by
  simp [relaxTo, h]

theorem relaxTo_of_eq {Nd M : SoftNode} (h : M.name = Nd.name) :
    relaxTo Nd M = { M with mode := .default, exception := Nd.exception, hard := Nd.hard } := by
  simp [relaxTo, h]

theorem mem_relaxDoc {C : SoftDoc} {Nd X : SoftNode} :
    X ∈ (relaxDoc C Nd).T.nodes ↔ ∃ M ∈ C.T.nodes, X = relaxTo Nd M := by
  simp only [relaxDoc, List.mem_map]
  exact ⟨fun ⟨M, hM, h⟩ => ⟨M, hM, h.symm⟩, fun ⟨M, hM, h⟩ => ⟨M, hM, h.symm⟩⟩

theorem relax_mem {C : SoftDoc} {Nd M : SoftNode} (h : M ∈ C.T.nodes) : relaxTo Nd M ∈ (relaxDoc C Nd).T.nodes :=
  mem_relaxDoc.mpr ⟨M, h, rfl⟩

theorem fuel_relax (C : SoftDoc) (Nd : SoftNode) : VE.SoftNorms.fuel (relaxDoc C Nd) = VE.SoftNorms.fuel C := by
  simp [VE.SoftNorms.fuel, relaxDoc]

/-- Two members of a list with distinct keys and the same key are equal. -/
theorem eq_of_key {α : Type} (key : α → String) {l : List α} (hn : (l.map key).Nodup) {x y : α} (hx : x ∈ l)
    (hy : y ∈ l) (h : key x = key y) : x = y := by
  have h1 := VE.SoftNorms.find_key key l hn x hx
  have h2 := VE.SoftNorms.find_key key l hn y hy
  rw [h] at h1
  exact Option.some.inj (h1.symm.trans h2)

/-! ## Acts under the pair facts -/

section Acts
variable {D : SoftDoc} (hv : SoftValid D)
include hv

theorem dualPerm_act {q m : String} (h : dualPerm D q = some m) : actKey D q = m ∧ actKey D m = m := by
  refine ⟨by simp [actKey, h], ?_⟩
  unfold dualPerm at h
  obtain ⟨pr, hpr, rfl⟩ := Option.map_eq_some_iff.mp h
  have hm := List.mem_of_find?_eq_some hpr
  have hn : dualPerm D pr.perm = none := by
    unfold dualPerm
    rw [Option.map_eq_none_iff, List.find?_eq_none]
    intro pr' hpr' he
    exact hv.permNotReq pr hm (List.mem_map.mpr ⟨pr', hpr', by simpa using he⟩)
  simp [actKey, hn]

theorem dualOblig_act {q r : String} (h : dualOblig D q = some r) : actKey D q = q ∧ actKey D r = q := by
  unfold dualOblig at h
  obtain ⟨pr, hpr, rfl⟩ := Option.map_eq_some_iff.mp h
  have hm := List.mem_of_find?_eq_some hpr
  have hq : pr.perm = q := by simpa using List.find?_some hpr
  have hn : dualPerm D q = none := by
    unfold dualPerm
    rw [Option.map_eq_none_iff, List.find?_eq_none]
    intro pr' hpr' he
    exact hv.permNotReq pr hm (List.mem_map.mpr ⟨pr', hpr', by rw [hq]; simpa using he⟩)
  have hr : dualPerm D pr.req = some q := by
    unfold dualPerm
    rw [VE.SoftNorms.find_key VE.Norms.Pair.req _ hv.pairReq pr hm]
    simp [hq]
  exact ⟨by simp [actKey, hn], by simp [actKey, hr]⟩

theorem act_of_incompatible {M N : SoftNode} (h : Incompatible D M N = true) : act D M = act D N := by
  unfold Incompatible at h
  simp only [Bool.or_eq_true, Bool.and_eq_true, beq_iff_eq, bne_iff_ne, ne_eq, Bool.not_eq_true'] at h
  unfold act
  rcases h with (⟨hp, _⟩ | ⟨_, hd⟩) | ⟨_, hd⟩
  · rw [hp]
  · obtain ⟨h1, h2⟩ := dualPerm_act hv hd
    rw [h1, h2]
  · obtain ⟨h1, h2⟩ := dualPerm_act hv hd
    rw [h1, h2]

end Acts

theorem incompatible_self (D : SoftDoc) (N : SoftNode) : Incompatible D N N = false := by
  unfold Incompatible
  cases N.sign <;> simp

/-! ## Force: a document and its relaxed twin -/

/-- What the force lemma reads: rules named like the twin are strict and on the twin's predicate, the relaxed
    document is well-formed, and there the twin is the only rule on its act. -/
structure Twin (C : SoftDoc) (Nd : SoftNode) : Prop where
  strict : ∀ M ∈ C.T.nodes, M.name = Nd.name → M.mode = .strict
  pred : ∀ M ∈ C.T.nodes, M.name = Nd.name → M.pred = Nd.pred
  valid : SoftValid (relaxDoc C Nd)
  alone : ∀ M ∈ (relaxDoc C Nd).T.nodes, act (relaxDoc C Nd) M = act (relaxDoc C Nd) Nd → M.name = Nd.name

section Force
variable {C : SoftDoc} {Nd : SoftNode} (hw : Twin C Nd) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
include hw

theorem Twin.alone_src : ∀ M ∈ C.T.nodes, act C M = act C Nd → M.name = Nd.name := by
  intro M hM ha
  have := hw.alone (relaxTo Nd M) (relax_mem hM) (by
    show actKey C (relaxTo Nd M).pred = actKey C Nd.pred
    rw [relaxTo_pred]; exact ha)
  rwa [relaxTo_name] at this

theorem Twin.off_name {M : SoftNode} (hM : M ∈ C.T.nodes) (hp : M.pred ≠ Nd.pred) : M.name ≠ Nd.name :=
  fun hn => hp (hw.pred M hM hn)

theorem Twin.act_ne {M : SoftNode} (hM : M ∈ C.T.nodes) (hn : M.name ≠ Nd.name) : act C M ≠ act C Nd :=
  fun ha => hn (hw.alone_src M hM ha)

/-- On the twin's act the relaxed document has default rules only. -/
theorem Twin.default_on {N : SoftNode} (hN : N ∈ (relaxDoc C Nd).T.nodes)
    (ha : act (relaxDoc C Nd) N = act (relaxDoc C Nd) Nd) : N.mode = .default := by
  have hn := hw.alone N hN ha
  obtain ⟨M, _, rfl⟩ := mem_relaxDoc.mp hN
  rw [relaxTo_name] at hn
  rw [relaxTo_of_eq hn]

theorem Twin.mem_off {X : SoftNode} (hp : X.pred ≠ Nd.pred) : X ∈ (relaxDoc C Nd).T.nodes ↔ X ∈ C.T.nodes := by
  rw [mem_relaxDoc]
  constructor
  · rintro ⟨M, hM, rfl⟩
    rw [relaxTo_pred] at hp
    rw [relaxTo_of_ne (hw.off_name hM hp)]; exact hM
  · intro hX
    exact ⟨X, hX, (relaxTo_of_ne (hw.off_name hX hp)).symm⟩

theorem Twin.exceptedF_eq {M : SoftNode} (hM : M ∈ C.T.nodes) (hn : M.name = Nd.name) :
    exceptedF (relaxDoc C Nd) (relaxTo Nd M) = exceptedF C Nd := by
  unfold exceptedF VE.SoftNorms.exceptedName
  rw [relaxTo_name, relaxTo_pred, hn, hw.pred M hM hn]
  rfl

theorem Twin.live_twin {M : SoftNode} (hM : M ∈ C.T.nodes) (hn : M.name = Nd.name)
    (he : ¬ (exceptedF C Nd).denote S ρ) : LiveD (relaxDoc C Nd) S ρ (relaxTo Nd M) ↔ LiveD C S ρ M := by
  have hs := hw.strict M hM hn
  have hx := hw.exceptedF_eq hM hn
  unfold LiveD
  rw [hx]
  rw [relaxTo_of_eq hn]
  constructor
  · rintro ⟨hg, hc, hsw, _⟩
    exact ⟨hg, hc, hsw, fun h => by rw [hs] at h; cases h⟩
  · rintro ⟨hg, hc, hsw, _⟩
    exact ⟨hg, hc, hsw, fun _ => he⟩

theorem Twin.strictYields_off : ∀ (f : Nat) (N : SoftNode), N.pred ≠ Nd.pred →
    (StrictYieldsD (relaxDoc C Nd) S ρ f N ↔ StrictYieldsD C S ρ f N)
  | 0, _, _ => Iff.rfl
  | f + 1, N, hp => by
    simp only [StrictYieldsD]
    apply or_congr Iff.rfl
    constructor
    · rintro ⟨X, hX, hy⟩
      obtain ⟨hX, hXp, hXo⟩ := mem_childrenIn_iff.mp hX
      have hp' : X.pred ≠ Nd.pred := hXp ▸ hp
      exact ⟨X, mem_childrenIn_iff.mpr ⟨(hw.mem_off hp').mp hX, hXp, hXo⟩,
        (Twin.strictYields_off f X hp').mp hy⟩
    · rintro ⟨X, hX, hy⟩
      obtain ⟨hX, hXp, hXo⟩ := mem_childrenIn_iff.mp hX
      have hp' : X.pred ≠ Nd.pred := hXp ▸ hp
      exact ⟨X, mem_childrenIn_iff.mpr ⟨(hw.mem_off hp').mpr hX, hXp, hXo⟩,
        (Twin.strictYields_off f X hp').mpr hy⟩

theorem Twin.strictSelects_off (f : Nat) {N : SoftNode} (hp : N.pred ≠ Nd.pred) :
    StrictSelectsD (relaxDoc C Nd) S ρ f N ↔ StrictSelectsD C S ρ f N := by
  unfold StrictSelectsD
  apply and_congr Iff.rfl
  apply and_congr Iff.rfl
  apply not_congr
  constructor
  · rintro ⟨X, hX, hy⟩
    obtain ⟨hX, hXp, hXo⟩ := mem_childrenIn_iff.mp hX
    have hp' : X.pred ≠ Nd.pred := hXp ▸ hp
    exact ⟨X, mem_childrenIn_iff.mpr ⟨(hw.mem_off hp').mp hX, hXp, hXo⟩, (hw.strictYields_off S ρ f X hp').mp hy⟩
  · rintro ⟨X, hX, hy⟩
    obtain ⟨hX, hXp, hXo⟩ := mem_childrenIn_iff.mp hX
    have hp' : X.pred ≠ Nd.pred := hXp ▸ hp
    exact ⟨X, mem_childrenIn_iff.mpr ⟨(hw.mem_off hp').mpr hX, hXp, hXo⟩, (hw.strictYields_off S ρ f X hp').mpr hy⟩

theorem Twin.strictDecides_off {q : String} (hq : q ≠ Nd.pred) (sign : Bool) :
    StrictDecidesD (relaxDoc C Nd) S ρ q sign ↔ StrictDecidesD C S ρ q sign := by
  unfold StrictDecidesD
  rw [fuel_relax]
  constructor
  · rintro ⟨N, hN, hs, h⟩
    obtain ⟨hN', hq'⟩ := mem_rulesOn.mp hN
    have hp : N.pred ≠ Nd.pred := hq' ▸ hq
    exact ⟨N, mem_rulesOn.mpr ⟨(hw.mem_off hp).mp hN', hq'⟩, hs, (hw.strictSelects_off S ρ _ hp).mp h⟩
  · rintro ⟨N, hN, hs, h⟩
    obtain ⟨hN', hq'⟩ := mem_rulesOn.mp hN
    have hp : N.pred ≠ Nd.pred := hq' ▸ hq
    exact ⟨N, mem_rulesOn.mpr ⟨(hw.mem_off hp).mpr hN', hq'⟩, hs, (hw.strictSelects_off S ρ _ hp).mpr h⟩

/-- No strict rule decides a predicate on the twin's act. -/
theorem Twin.strictDecides_none {q : String} (hq : actKey C q = act C Nd) (sign : Bool) :
    ¬ StrictDecidesD (relaxDoc C Nd) S ρ q sign := by
  rintro ⟨N, hN, _, hsel⟩
  obtain ⟨hN', hq'⟩ := mem_rulesOn.mp hN
  have := hw.default_on hN' (by show actKey C N.pred = actKey C Nd.pred; rw [hq']; exact hq)
  rw [hsel.1] at this
  cases this

theorem Twin.blocked_off {M : SoftNode} (hM : M ∈ C.T.nodes) (hn : M.name ≠ Nd.name) :
    BlockedD (relaxDoc C Nd) S ρ M ↔ BlockedD C S ρ M := by
  have hv := hw.valid
  have hne := hw.act_ne hM hn
  have hp : M.pred ≠ Nd.pred := fun h => hne (by unfold act; rw [h])
  have hm : ∀ m, dualPerm C M.pred = some m → m ≠ Nd.pred := by
    intro m hd he
    obtain ⟨h1, h2⟩ := dualPerm_act hv hd
    exact hne (by unfold act; rw [← he]; exact h1.trans h2.symm)
  have hr : ∀ r, dualOblig C M.pred = some r → r ≠ Nd.pred := by
    intro r hd he
    obtain ⟨h1, h2⟩ := dualOblig_act hv hd
    exact hne (by unfold act; rw [← he]; exact h1.trans h2.symm)
  unfold BlockedD
  constructor
  · rintro (h | h | ⟨hs, m, hd, h⟩ | ⟨hs, r, hd, h⟩)
    · exact Or.inl ((hw.strictDecides_off S ρ hp true).mp h)
    · exact Or.inr (Or.inl ((hw.strictDecides_off S ρ hp false).mp h))
    · exact Or.inr (Or.inr (Or.inl ⟨hs, m, hd, (hw.strictDecides_off S ρ (hm m hd) false).mp h⟩))
    · exact Or.inr (Or.inr (Or.inr ⟨hs, r, hd, (hw.strictDecides_off S ρ (hr r hd) true).mp h⟩))
  · rintro (h | h | ⟨hs, m, hd, h⟩ | ⟨hs, r, hd, h⟩)
    · exact Or.inl ((hw.strictDecides_off S ρ hp true).mpr h)
    · exact Or.inr (Or.inl ((hw.strictDecides_off S ρ hp false).mpr h))
    · exact Or.inr (Or.inr (Or.inl ⟨hs, m, hd, (hw.strictDecides_off S ρ (hm m hd) false).mpr h⟩))
    · exact Or.inr (Or.inr (Or.inr ⟨hs, r, hd, (hw.strictDecides_off S ρ (hr r hd) true).mpr h⟩))

theorem Twin.blocked_twin {M : SoftNode} (hM : M ∈ C.T.nodes) (hn : M.name = Nd.name) :
    ¬ BlockedD (relaxDoc C Nd) S ρ (relaxTo Nd M) := by
  have hv := hw.valid
  have hp : (relaxTo Nd M).pred = Nd.pred := by rw [relaxTo_pred]; exact hw.pred M hM hn
  unfold BlockedD
  rw [hp]
  rintro (h | h | ⟨_, m, hd, h⟩ | ⟨_, r, hd, h⟩)
  · exact hw.strictDecides_none S ρ rfl true h
  · exact hw.strictDecides_none S ρ rfl false h
  · obtain ⟨h1, h2⟩ := dualPerm_act hv hd
    exact hw.strictDecides_none S ρ (h2.trans h1.symm) false h
  · obtain ⟨h1, h2⟩ := dualOblig_act hv hd
    exact hw.strictDecides_none S ρ (h2.trans h1.symm) true h

theorem Twin.dom_twin {M : SoftNode} (hM : M ∈ C.T.nodes) (hn : M.name = Nd.name) (eff : SoftNode → Prop) :
    ¬ DomWithD (relaxDoc C Nd) S ρ eff (relaxTo Nd M) := by
  have hv := hw.valid
  rintro ⟨M', hM', hi, _⟩
  have ha := act_of_incompatible hv hi
  have hT := relax_mem (Nd := Nd) hM
  have hn' : M'.name = Nd.name := hw.alone M' hM' (by
    rw [ha]; show actKey C (relaxTo Nd M).pred = actKey C Nd.pred
    rw [relaxTo_pred, hw.pred M hM hn])
  have he : M' = relaxTo Nd M := eq_of_key (·.name) hv.names hM' hT (by show M'.name = (relaxTo Nd M).name; rw [hn', relaxTo_name, hn])
  rw [he, incompatible_self] at hi
  cases hi

theorem Twin.eff_twin {M : SoftNode} (hM : M ∈ C.T.nodes) (hn : M.name = Nd.name) :
    ∀ g, EffD (relaxDoc C Nd) S ρ g (relaxTo Nd M) ↔ LiveD (relaxDoc C Nd) S ρ (relaxTo Nd M) := by
  have hd : (relaxTo Nd M).mode = .default := by rw [relaxTo_of_eq hn]
  have hel : EligibleD (relaxDoc C Nd) S ρ (relaxTo Nd M) ↔ LiveD (relaxDoc C Nd) S ρ (relaxTo Nd M) :=
    ⟨fun h => h.2.1, fun h => ⟨hd, h, hw.blocked_twin S ρ hM hn⟩⟩
  intro g
  cases g with
  | zero => exact hel
  | succ g =>
    simp only [EffD]
    rw [hel]
    exact ⟨fun h => h.1, fun h => ⟨h, hw.dom_twin S ρ hM hn _⟩⟩

theorem Twin.eligible_off {M : SoftNode} (hM : M ∈ C.T.nodes) (hn : M.name ≠ Nd.name) :
    EligibleD (relaxDoc C Nd) S ρ M ↔ EligibleD C S ρ M := by
  unfold EligibleD
  rw [hw.blocked_off S ρ hM hn]
  rfl

/-- An opponent of a rule off the twin's act is off it too: the two documents have the same opponents. -/
theorem Twin.opponent {M M' : SoftNode} (hM : M ∈ C.T.nodes) (hn : M.name ≠ Nd.name)
    (hi : Incompatible C M' M = true) :
    (M' ∈ (relaxDoc C Nd).T.nodes ↔ M' ∈ C.T.nodes) ∧ M'.pred ≠ Nd.pred := by
  have ha : act C M' = act C M := act_of_incompatible hw.valid hi
  have hp : M'.pred ≠ Nd.pred := fun h => hw.act_ne hM hn (by rw [← ha]; unfold act; rw [h])
  exact ⟨hw.mem_off hp, hp⟩

theorem Twin.eff_off : ∀ (g : Nat) (M : SoftNode), M ∈ C.T.nodes → M.name ≠ Nd.name →
    (EffD (relaxDoc C Nd) S ρ g M ↔ EffD C S ρ g M)
  | 0, _, hM, hn => hw.eligible_off S ρ hM hn
  | g + 1, M, hM, hn => by
    simp only [EffD]
    rw [hw.eligible_off S ρ hM hn]
    apply and_congr Iff.rfl
    apply not_congr
    constructor
    · rintro ⟨M', hM', hi, hd, hc, h⟩
      obtain ⟨hmem, hp'⟩ := hw.opponent hM hn hi
      have hM'' := hmem.mp hM'
      have hn' := hw.off_name hM'' hp'
      refine ⟨M', hM'', hi, hd, hc, ?_⟩
      rcases h with ⟨hh, he, ho⟩ | ⟨hol, hh, hel, ho⟩
      · exact Or.inl ⟨hh, (Twin.eff_off g M' hM'' hn').mp he, ho⟩
      · exact Or.inr ⟨hol, hh, (hw.eligible_off S ρ hM'' hn').mp hel, ho⟩
    · rintro ⟨M', hM', hi, hd, hc, h⟩
      obtain ⟨hmem, hp'⟩ := hw.opponent hM hn hi
      have hn' := hw.off_name hM' hp'
      refine ⟨M', hmem.mpr hM', hi, hd, hc, ?_⟩
      rcases h with ⟨hh, he, ho⟩ | ⟨hol, hh, hel, ho⟩
      · exact Or.inl ⟨hh, (Twin.eff_off g M' hM' hn').mpr he, ho⟩
      · exact Or.inr ⟨hol, hh, (hw.eligible_off S ρ hM' hn').mpr hel, ho⟩

theorem Twin.applies {M : SoftNode} (hM : M ∈ C.T.nodes) (he : ¬ (exceptedF C Nd).denote S ρ) :
    AppliesSoftD (relaxDoc C Nd) S ρ (relaxTo Nd M) ↔ AppliesSoftD C S ρ M := by
  by_cases hn : M.name = Nd.name
  · have hs := hw.strict M hM hn
    have hd : (relaxTo Nd M).mode = .default := by rw [relaxTo_of_eq hn]
    unfold AppliesSoftD
    rw [hd, hs]
    exact (hw.eff_twin S ρ hM hn _).trans (hw.live_twin S ρ hM hn he)
  · rw [relaxTo_of_ne hn]
    unfold AppliesSoftD
    cases hm : M.mode
    · exact Iff.rfl
    · exact hw.eff_off S ρ _ M hM hn

omit hw in
theorem relax_children {M : SoftNode} (X : SoftNode) :
    X ∈ VE.SoftNorms.children (relaxDoc C Nd) (relaxTo Nd M) ↔
      ∃ Y ∈ VE.SoftNorms.children C M, X = relaxTo Nd Y :=
  VE.SoftNorms.mem_childrenIn_map (ns := C.T.nodes) (relaxTo Nd) (relaxTo_name Nd) (relaxTo_pred Nd)
    (relaxTo_over Nd) M X

theorem Twin.yields (he : ¬ (exceptedF C Nd).denote S ρ) : ∀ (f : Nat) (M : SoftNode), M ∈ C.T.nodes →
    (YieldsSoftD (relaxDoc C Nd) S ρ f (relaxTo Nd M) ↔ YieldsSoftD C S ρ f M)
  | 0, _, hM => hw.applies S ρ hM he
  | f + 1, M, hM => by
    simp only [YieldsSoftD]
    rw [hw.applies S ρ hM he]
    apply or_congr Iff.rfl
    constructor
    · rintro ⟨X, hX, hy⟩
      obtain ⟨Y, hY, rfl⟩ := (relax_children X).mp hX
      exact ⟨Y, hY, (Twin.yields he f Y (mem_childrenIn_iff.mp hY).1).mp hy⟩
    · rintro ⟨Y, hY, hy⟩
      exact ⟨relaxTo Nd Y, (relax_children _).mpr ⟨Y, hY, rfl⟩,
        (Twin.yields he f Y (mem_childrenIn_iff.mp hY).1).mpr hy⟩

theorem Twin.selects (he : ¬ (exceptedF C Nd).denote S ρ) (f : Nat) {M : SoftNode} (hM : M ∈ C.T.nodes) :
    SelectsSoftD (relaxDoc C Nd) S ρ f (relaxTo Nd M) ↔ SelectsSoftD C S ρ f M := by
  unfold SelectsSoftD
  rw [hw.applies S ρ hM he]
  apply and_congr Iff.rfl
  apply not_congr
  constructor
  · rintro ⟨X, hX, hy⟩
    obtain ⟨Y, hY, rfl⟩ := (relax_children X).mp hX
    exact ⟨Y, hY, (hw.yields S ρ he f Y (mem_childrenIn_iff.mp hY).1).mp hy⟩
  · rintro ⟨Y, hY, hy⟩
    exact ⟨relaxTo Nd Y, (relax_children _).mpr ⟨Y, hY, rfl⟩,
      (hw.yields S ρ he f Y (mem_childrenIn_iff.mp hY).1).mpr hy⟩

/-- The force lemma for a whole document: where the twin's exception predicate is false, a document and its
    relaxed twin decide every predicate alike. -/
theorem Twin.decides (he : ¬ (exceptedF C Nd).denote S ρ) (p : String) (sign : Bool) :
    DecidesSoftD (relaxDoc C Nd) S ρ p sign ↔ DecidesSoftD C S ρ p sign := by
  unfold DecidesSoftD
  rw [fuel_relax]
  constructor
  · rintro ⟨X, hX, hs, h⟩
    obtain ⟨hX', hp⟩ := mem_rulesOn.mp hX
    obtain ⟨M, hM, rfl⟩ := mem_relaxDoc.mp hX'
    exact ⟨M, mem_rulesOn.mpr ⟨hM, (relaxTo_pred Nd M).symm.trans hp⟩, (relaxTo_sign Nd M) ▸ hs,
      (hw.selects S ρ he _ hM).mp h⟩
  · rintro ⟨M, hM, hs, h⟩
    obtain ⟨hM', hp⟩ := mem_rulesOn.mp hM
    exact ⟨relaxTo Nd M, mem_rulesOn.mpr ⟨relax_mem hM', (relaxTo_pred Nd M).trans hp⟩, (relaxTo_sign Nd M).trans hs,
      (hw.selects S ρ he _ hM').mpr h⟩

end Force

end VE.Readings
