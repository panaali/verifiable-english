import VE.Readings.Wire

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

/-! ## Expansion: the two canonical expansions agree -/

/-- Two trees with the same declarations whose stratum graphs both pass have the same layer symbols. -/
theorem syms_mem {T₁ T₂ : VE.Norms.Tree} (hr : T₁.regulated = T₂.regulated) (hd : T₁.definitions = T₂.definitions)
    (h₁ : ∃ o, VE.Route.dependencyOrder (VE.Norms.stratumNodes T₁) = .ok o)
    (h₂ : ∃ o, VE.Route.dependencyOrder (VE.Norms.stratumNodes T₂) = .ok o)
    {q : VE.Norms.Sym} (hq : q ∈ VE.Norms.syms T₁) : q ∈ VE.Norms.syms T₂ := by
  obtain ⟨n, hn, hl⟩ := List.mem_filterMap.mp hq
  obtain ⟨o₁, ho₁⟩ := h₁
  obtain ⟨o₂, ho₂⟩ := h₂
  obtain ⟨_, hm₁, _⟩ := VE.Route.dag_acyclic _ _ ho₁
  obtain ⟨_, hm₂, _⟩ := VE.Route.dag_acyclic _ _ ho₂
  have hn₁ : n ∈ o₁ := by unfold VE.Norms.order at hn; rw [ho₁] at hn; exact hn
  have hnames : VE.Route.nodeNames (VE.Norms.stratumNodes T₁) = VE.Route.nodeNames (VE.Norms.stratumNodes T₂) := by
    rw [nodeNames_stratum, nodeNames_stratum, hr, hd]
  refine List.mem_filterMap.mpr ⟨n, ?_, ?_⟩
  · unfold VE.Norms.order; rw [ho₂]; exact (hm₂ n).mpr (hnames ▸ (hm₁ n).mp hn₁)
  · unfold VE.Norms.lookupSym at hl ⊢; rw [← hr, ← hd]; exact hl

theorem layerNames_mem {T₁ T₂ : VE.Norms.Tree} (hr : T₁.regulated = T₂.regulated)
    (hd : T₁.definitions = T₂.definitions)
    (h₁ : ∃ o, VE.Route.dependencyOrder (VE.Norms.stratumNodes T₁) = .ok o)
    (h₂ : ∃ o, VE.Route.dependencyOrder (VE.Norms.stratumNodes T₂) = .ok o)
    {n : String} (h : n ∈ VE.Norms.layerNames T₁) : n ∈ VE.Norms.layerNames T₂ := by
  obtain ⟨q, hq, rfl⟩ := List.mem_map.mp h
  exact List.mem_map.mpr ⟨q, syms_mem hr hd h₁ h₂ hq, rfl⟩

section Expansion
variable {C : SoftDoc} {Nd : SoftNode} (hw : Twin C Nd) (hs : SoftValid C) (S : VE.Structure.{u})
  (hc : VE.Norms.ConstantsTyped (soften C) S)
  (he : ∀ ρ, ¬ (exceptedF C Nd).denote (canon (soften (relaxDoc C Nd)) S) ρ)
include hw hs hc he

/-- Over one base on which the twin's exception predicate is false in the relaxed expansion, a formula of the
    strict document has the same truth in the two canonical expansions. -/
theorem canon_relax (k : Nat) (φ : VE.Formula) (Γ : List String) (hφ : φ.WellFormed (envAt (soften C) k) Γ)
    (ρ : VE.Valuation S) (hρ : VE.Valuation.Typed S Γ ρ) :
    φ.denote (canon (soften C) S) ρ ↔ φ.denote (canon (soften (relaxDoc C Nd)) S) ρ := by
  have hvs := VE.Norms.valid_of_wellFormed _ hs.wf
  have hvd := VE.Norms.valid_of_wellFormed _ hw.valid.wf
  have hcd : VE.Norms.ConstantsTyped (soften (relaxDoc C Nd)) S := hc
  have hcd' : VE.Norms.ConstantsTyped (soften C) (canon (soften (relaxDoc C Nd)) S) := hc
  have hagree : ∀ k, VE.Norms.AgreesBelow (soften C) k (canon (soften (relaxDoc C Nd)) S) := by
    intro k j q _ hq vs hvs'
    have hqd : q ∈ VE.Norms.syms (soften (relaxDoc C Nd)).T :=
      syms_mem (T₁ := (soften C).T) (T₂ := (soften (relaxDoc C Nd)).T) rfl rfl hvs.stratum hvd.stratum (List.mem_of_getElem? hq)
    obtain ⟨j', hj'⟩ := List.mem_iff_getElem?.mp hqd
    have hlt : j' < size (soften (relaxDoc C Nd)) := (List.getElem?_eq_some_iff.mp hj').1
    rw [VE.SoftNorms.canon_agrees hvd S hcd (size (soften (relaxDoc C Nd))) j' q hlt hj' vs hvs']
    cases q with
    | defn d => exact Iff.rfl
    | reg r =>
      show (VE.Norms.outcome (soften (relaxDoc C Nd)).T r).denote _ _ ↔ (VE.Norms.outcome (soften C).T r).denote _ _
      rw [VE.Norms.outcome_denote, VE.Norms.outcome_denote]
      simp only [VE.Norms.pos, VE.Norms.neg, VE.Norms.decides_denote, VE.SoftNorms.decidesD_soften]
      rw [hw.decides _ _ (he _) r.name true, hw.decides _ _ (he _) r.name false]
  rw [← VE.SoftNorms.canon_subst hvs S hc k φ Γ hφ ρ hρ,
    ← VE.Norms.subst_denote hvs k (canon (soften (relaxDoc C Nd)) S) hcd' (hagree k) φ Γ hφ ρ hρ]
  exact (VE.Norms.denote_relation_congr (E := envAt (soften C) 0) (ns := VE.Norms.layerNames (soften C).T)
    (fun _ hr => VE.Norms.envAt_zero_later hr) S _
    (fun r vs hr => VE.SoftNorms.canon_off S
      (fun h => hr (layerNames_mem (T₁ := (soften (relaxDoc C Nd)).T) (T₂ := (soften C).T) rfl rfl hvd.stratum hvs.stratum h)) vs)
    _ Γ ρ (VE.Norms.subst_wellFormed hvs k φ Γ hφ)).symm

theorem decides_canon {r : Regulated} (hr : r ∈ C.T.regulated) (vs : List S.Carrier)
    (hvs : VE.TupleTyped S r.sorts vs) (sign : Bool) :
    DecidesSoftD C (canon (soften C) S) (tupleVal vs) r.name sign ↔
      DecidesSoftD (relaxDoc C Nd) (canon (soften (relaxDoc C Nd)) S) (tupleVal vs) r.name sign := by
  have hvs' := VE.Norms.valid_of_wellFormed _ hs.wf
  have hT := VE.Norms.rulesTyped_of_valid hvs' (VE.Norms.index_before hvs' hr)
  rw [← VE.SoftNorms.decidesD_soften, ← VE.Norms.decides_denote,
    canon_relax hw hs S hc he _ _ _ (VE.Norms.decides_wellFormed hT sign) _ (VE.Norms.tupleVal_typed S _ vs hvs),
    VE.Norms.decides_denote, VE.SoftNorms.decidesD_soften, hw.decides _ _ (he _)]

theorem value_canon {r : Regulated} (hr : r ∈ C.T.regulated) (vs : List S.Carrier)
    (hvs : VE.TupleTyped S r.sorts vs) :
    ValueSoft C r (canon (soften C) S) vs = ValueSoft (relaxDoc C Nd) r (canon (soften (relaxDoc C Nd)) S) vs := by
  unfold ValueSoft
  rw [propext (decides_canon hw hs S hc he hr vs hvs true), propext (decides_canon hw hs S hc he hr vs hvs false)]

theorem selects_canon {N : SoftNode} (hN : N ∈ C.T.nodes) (vs : List S.Carrier)
    (hvs : VE.TupleTyped S (VE.SoftNorms.sortsOf C N.pred) vs) :
    SelectsSoftD C (canon (soften C) S) (tupleVal vs) (VE.SoftNorms.fuel C) N ↔
      SelectsSoftD (relaxDoc C Nd) (canon (soften (relaxDoc C Nd)) S) (tupleVal vs)
        (VE.SoftNorms.fuel (relaxDoc C Nd)) (relaxTo Nd N) := by
  rw [← VE.SoftNorms.selectsPrime_denote,
    canon_relax hw hs S hc he _ _ _ (hs.selTyped N hN) _ (VE.Norms.tupleVal_typed S _ vs hvs),
    VE.SoftNorms.selectsPrime_denote, fuel_relax, hw.selects _ _ (he _) _ hN]

end Expansion

/-! ## The premises of a document and its relaxed twin -/

theorem flatMap_congr_mem {α β : Type} {l : List α} {f g : α → List β} (h : ∀ a ∈ l, f a = g a) :
    l.flatMap f = l.flatMap g := by
  induction l with
  | nil => rfl
  | cons a l ih =>
    simp only [List.flatMap_cons]
    rw [h a List.mem_cons_self, ih (fun b hb => h b (List.mem_cons_of_mem _ hb))]

theorem filterMap_congr_mem {α β : Type} {l : List α} {f g : α → Option β} (h : ∀ a ∈ l, f a = g a) :
    l.filterMap f = l.filterMap g := by
  induction l with
  | nil => rfl
  | cons a l ih =>
    simp only [List.filterMap_cons]
    rw [h a List.mem_cons_self, ih (fun b hb => h b (List.mem_cons_of_mem _ hb))]

/-- A list's first match on `P` is its filter's when every match passes the filter. -/
theorem find?_of_filter {α : Type} (l : List α) (P Q : α → Bool) (h : ∀ a, P a = true → Q a = true) :
    (l.filter Q).find? P = l.find? P := by
  rw [List.find?_filter]
  congr 1
  funext a
  cases hp : P a
  · simp
  · simp [h a hp]

theorem sat_append (S : VE.Structure.{u}) (a b : List VE.Formula) : Sat S (a ++ b) ↔ Sat S a ∧ Sat S b := by
  simp only [Sat, List.mem_append]
  exact ⟨fun h => ⟨fun x hx => h x (Or.inl hx), fun x hx => h x (Or.inr hx)⟩,
    fun ⟨ha, hb⟩ x hx => hx.elim (ha x) (hb x)⟩

theorem atom_false {S : VE.Structure.{u}} {p : String} (h : ∀ vs, ¬ S.relation p vs) (ss : List String)
    (ρ : VE.Valuation S) : ¬ (VE.Norms.atom p ss).denote S ρ := by
  unfold VE.Norms.atom
  split
  · rintro ⟨v, _, hv⟩; exact h _ hv
  · rintro ⟨v, w, _, _, hv⟩; exact h _ hv
  · exact id

section Premises
variable {C : SoftDoc} {Nd : SoftNode} (hw : Twin C Nd)
include hw

theorem Twin.collidingPairs_eq :
    VE.SoftNorms.collidingPairs (relaxDoc C Nd) = VE.SoftNorms.collidingPairs C := by
  have hv := hw.valid
  unfold VE.SoftNorms.collidingPairs
  congr 1
  show (C.T.nodes.map (relaxTo Nd)).flatMap _ = _
  rw [List.flatMap_map]
  apply flatMap_congr_mem
  intro M hM
  show List.filterMap _ (C.T.nodes.map (relaxTo Nd)) = _
  rw [List.filterMap_map]
  apply filterMap_congr_mem
  intro N hN
  simp only [Function.comp_def]
  -- two rules named like the twin never collide, and the twin collides with nothing
  have hcol : ∀ X ∈ C.T.nodes, ∀ Y ∈ C.T.nodes, X.name = Nd.name →
      Incompatible (relaxDoc C Nd) (relaxTo Nd X) (relaxTo Nd Y) = true → Y.name = Nd.name := by
    intro X hX Y hY hn hi
    have ha := act_of_incompatible hv hi
    have := hw.alone (relaxTo Nd Y) (relax_mem hY) (by
      rw [← ha]; show actKey C (relaxTo Nd X).pred = actKey C Nd.pred
      rw [relaxTo_pred, hw.pred X hX hn])
    rwa [relaxTo_name] at this
  by_cases hm : M.name = Nd.name
  · have h1 : ¬ ((relaxTo Nd M).mode = .default ∧ (relaxTo Nd N).mode = .default ∧
        (relaxTo Nd M).name < (relaxTo Nd N).name ∧
        Incompatible (relaxDoc C Nd) (relaxTo Nd M) (relaxTo Nd N) = true) := by
      rintro ⟨_, _, hlt, hi⟩
      have := hcol M hM N hN hm hi
      rw [relaxTo_name, relaxTo_name, hm, this] at hlt
      exact String.lt_irrefl _ hlt
    have h2 : ¬ (M.mode = .default ∧ N.mode = .default ∧ M.name < N.name ∧ Incompatible C M N = true) :=
      fun h => by rw [hw.strict M hM hm] at h; cases h.1
    rw [if_neg h1, if_neg h2]
  · by_cases hn : N.name = Nd.name
    · have h1 : ¬ ((relaxTo Nd M).mode = .default ∧ (relaxTo Nd N).mode = .default ∧
          (relaxTo Nd M).name < (relaxTo Nd N).name ∧
          Incompatible (relaxDoc C Nd) (relaxTo Nd M) (relaxTo Nd N) = true) := by
        rintro ⟨_, _, _, hi⟩
        have hi' : Incompatible (relaxDoc C Nd) (relaxTo Nd N) (relaxTo Nd M) = true := by
          rw [VE.SoftNorms.incompatible_symm]; exact hi
        exact hm (hcol N hN M hM hn hi')
      have h2 : ¬ (M.mode = .default ∧ N.mode = .default ∧ M.name < N.name ∧ Incompatible C M N = true) :=
        fun h => by rw [hw.strict N hN hn] at h; cases h.2.1
      rw [if_neg h1, if_neg h2]
    · rw [relaxTo_of_ne hm, relaxTo_of_ne hn]
      rfl

theorem Twin.outweighsTriples_eq :
    VE.SoftNorms.outweighsTriples (relaxDoc C Nd) = VE.SoftNorms.outweighsTriples C := by
  unfold VE.SoftNorms.outweighsTriples
  rw [hw.collidingPairs_eq]
  rfl

omit hw in
theorem offDecisions_relax : VE.SoftNorms.offDecisions (relaxDoc C Nd) = VE.SoftNorms.offDecisions C := by
  unfold VE.SoftNorms.offDecisions
  show (C.T.nodes.map (relaxTo Nd)).flatMap _ = _
  rw [List.flatMap_map]
  congr 1
  funext N
  simp only [relaxTo_alterable, VE.SoftNorms.offName, relaxTo_name, relaxTo_pred]
  rfl

theorem Twin.exceptedDecisions_filter : ∀ l : List SoftNode, (∀ M ∈ l, M ∈ C.T.nodes) →
    ((((l.map (relaxTo Nd)).filter (·.mode == .default)).map (fun N =>
        (VE.SoftNorms.exceptedName N, VE.SoftNorms.sortsOf (relaxDoc C Nd) N.pred))).filter
        (·.1 != VE.SoftNorms.exceptedName Nd)) =
      ((((l.filter (·.mode == .default)).map (fun N =>
        (VE.SoftNorms.exceptedName N, VE.SoftNorms.sortsOf C N.pred))).filter
        (·.1 != VE.SoftNorms.exceptedName Nd)))
  | [], _ => rfl
  | M :: l, hl => by
    have ih := Twin.exceptedDecisions_filter l (fun X hX => hl X (List.mem_cons_of_mem _ hX))
    have hM := hl M List.mem_cons_self
    by_cases hn : M.name = Nd.name
    · have hs := hw.strict M hM hn
      have hd : (relaxTo Nd M).mode = .default := by rw [relaxTo_of_eq hn]
      have hx : VE.SoftNorms.exceptedName (relaxTo Nd M) = VE.SoftNorms.exceptedName Nd := by
        unfold VE.SoftNorms.exceptedName; rw [relaxTo_name, hn]
      rw [List.map_cons, List.filter_cons_of_pos (by simp [hd]), List.map_cons,
        List.filter_cons_of_neg (by simp [hx]), List.filter_cons_of_neg (by simp [hs])]
      exact ih
    · rw [List.map_cons, relaxTo_of_ne hn]
      by_cases hd : M.mode = .default
      · rw [List.filter_cons_of_pos (by simp [hd]), List.filter_cons_of_pos (by simp [hd]),
          List.map_cons, List.map_cons]
        by_cases hx : VE.SoftNorms.exceptedName M = VE.SoftNorms.exceptedName Nd
        · rw [List.filter_cons_of_neg (by simp [hx]), List.filter_cons_of_neg (by simp [hx])]
          exact ih
        · rw [List.filter_cons_of_pos (by simp [hx]), List.filter_cons_of_pos (by simp [hx]), ih]
          rfl
      · rw [List.filter_cons_of_neg (by simp [hd]), List.filter_cons_of_neg (by simp [hd])]
        exact ih

theorem Twin.decisions_find {p : String} (hp : p ≠ VE.SoftNorms.exceptedName Nd) :
    (VE.SoftNorms.decisions (relaxDoc C Nd)).find? (·.1 == p) =
      (VE.SoftNorms.decisions C).find? (·.1 == p) := by
  have hq : ∀ a : String × List String, (a.1 == p) = true → (a.1 != VE.SoftNorms.exceptedName Nd) = true := by
    intro a ha
    simp only [beq_iff_eq] at ha
    simp [ha, hp]
  rw [← find?_of_filter _ _ _ hq, ← find?_of_filter (VE.SoftNorms.decisions C) _ _ hq]
  congr 1
  unfold VE.SoftNorms.decisions
  rw [List.filter_append, List.filter_append, List.filter_append, List.filter_append, offDecisions_relax]
  unfold VE.SoftNorms.outweighsDecisions
  rw [hw.outweighsTriples_eq]
  congr 2
  exact hw.exceptedDecisions_filter C.T.nodes (fun _ h => h)

/-- Off the exception predicate, the base vocabularies of the two elaborations agree. -/
theorem Twin.envAt_zero (hs : SoftValid C) {p : String} (hp : p ≠ VE.SoftNorms.exceptedName Nd) :
    (envAt (soften (relaxDoc C Nd)) 0).predicates p = (envAt (soften C) 0).predicates p := by
  have hvs := VE.Norms.valid_of_wellFormed _ hs.wf
  have hvd := VE.Norms.valid_of_wellFormed _ hw.valid.wf
  simp only [envAt, VE.Norms.hide, List.drop_zero]
  have hl : p ∈ VE.Norms.layerNames (soften (relaxDoc C Nd)).T ↔ p ∈ VE.Norms.layerNames (soften C).T :=
    ⟨layerNames_mem (T₁ := (soften (relaxDoc C Nd)).T) (T₂ := (soften C).T) rfl rfl hvd.stratum hvs.stratum,
     layerNames_mem (T₁ := (soften C).T) (T₂ := (soften (relaxDoc C Nd)).T) rfl rfl hvs.stratum hvd.stratum⟩
  by_cases hm : p ∈ VE.Norms.layerNames (soften C).T
  · rw [if_pos (hl.mpr hm), if_pos hm]
  · rw [if_neg (fun h => hm (hl.mp h)), if_neg hm]
    show (VE.SoftNorms.envPrime (relaxDoc C Nd)).predicates p = (VE.SoftNorms.envPrime C).predicates p
    unfold VE.SoftNorms.envPrime
    simp only
    rw [hw.decisions_find hp]
    rfl

theorem Twin.baseAdmissible (hs : SoftValid C) (S : VE.Structure.{u})
    (hS : ∀ vs, ¬ S.relation (VE.SoftNorms.exceptedName Nd) vs) :
    VE.Norms.BaseAdmissible (soften C) S ↔ VE.Norms.BaseAdmissible (soften (relaxDoc C Nd)) S := by
  unfold VE.Norms.BaseAdmissible VE.Structure.Admissible
  have key : ∀ p vs, S.relation p vs → (envAt (soften (relaxDoc C Nd)) 0).predicates p =
      (envAt (soften C) 0).predicates p :=
    fun p vs h => hw.envAt_zero hs (fun he => hS vs (he ▸ h))
  constructor
  · rintro ⟨⟨hc, hr⟩, hb⟩
    exact ⟨⟨hc, fun p vs h => by rw [key p vs h]; exact hr p vs h⟩, hb⟩
  · rintro ⟨⟨hc, hr⟩, hb⟩
    exact ⟨⟨hc, fun p vs h => by rw [← key p vs h]; exact hr p vs h⟩, hb⟩

/-- The exception premises: the relaxed document adds only the twin's necessary conditions, which hold where its
    exception predicate is false. -/
theorem Twin.excPremises (S : VE.Structure.{u}) (hsuf : ∀ e, Nd.exception = some e → e.sufficient = [])
    (hS : ∀ vs, ¬ S.relation (VE.SoftNorms.exceptedName Nd) vs) :
    Sat S (VE.SoftNorms.excPremises C) ↔ Sat S (VE.SoftNorms.excPremises (relaxDoc C Nd)) := by
  have hoff : ∀ M ∈ C.T.nodes, M.name ≠ Nd.name →
      VE.SoftNorms.excPremisesOf (relaxDoc C Nd) (relaxTo Nd M) = VE.SoftNorms.excPremisesOf C M := by
    intro M _ hn
    rw [relaxTo_of_ne hn]
    rfl
  have hon : ∀ M ∈ C.T.nodes, M.name = Nd.name → VE.SoftNorms.excPremisesOf C M = [] := by
    intro M hM hn
    unfold VE.SoftNorms.excPremisesOf
    rw [hw.strict M hM hn]
  have hsat : ∀ M ∈ C.T.nodes, M.name = Nd.name →
      Sat S (VE.SoftNorms.excPremisesOf (relaxDoc C Nd) (relaxTo Nd M)) := by
    intro M hM hn φ hφ
    have hmode : (relaxTo Nd M).mode = .default := by rw [relaxTo_of_eq hn]
    have hexc : (relaxTo Nd M).exception = Nd.exception := by rw [relaxTo_of_eq hn]
    have hname : VE.SoftNorms.exceptedName (relaxTo Nd M) = VE.SoftNorms.exceptedName Nd := by
      unfold VE.SoftNorms.exceptedName; rw [relaxTo_name, hn]
    unfold VE.SoftNorms.excPremisesOf at hφ
    rw [hmode, hexc] at hφ
    cases hex : Nd.exception with
    | none => simp [hex] at hφ
    | some e =>
      simp only [hex] at hφ
      rw [hsuf e hex, List.map_nil, List.nil_append] at hφ
      obtain ⟨c, _, rfl⟩ := List.mem_map.mp hφ
      rw [VE.Norms.bindAll_denote_nil]
      intro vs _ hx
      have he2 : ∀ ws, ¬ S.relation (VE.SoftNorms.exceptedName (relaxTo Nd M)) ws := by
        intro ws; rw [hname]; exact hS ws
      exact (atom_false he2 _ _ hx).elim
  unfold VE.SoftNorms.excPremises Sat
  constructor
  · intro h φ hφ
    have hφ' : φ ∈ (C.T.nodes.map (relaxTo Nd)).flatMap (VE.SoftNorms.excPremisesOf (relaxDoc C Nd)) := hφ
    rw [List.flatMap_map, List.mem_flatMap] at hφ'
    obtain ⟨M, hM, hφ'⟩ := hφ'
    by_cases hn : M.name = Nd.name
    · exact hsat M hM hn φ hφ'
    · rw [hoff M hM hn] at hφ'
      exact h φ (List.mem_flatMap.mpr ⟨M, hM, hφ'⟩)
  · intro h φ hφ
    obtain ⟨M, hM, hφ'⟩ := List.mem_flatMap.mp hφ
    by_cases hn : M.name = Nd.name
    · rw [hon M hM hn] at hφ'; cases hφ'
    · apply h φ
      show φ ∈ (C.T.nodes.map (relaxTo Nd)).flatMap (VE.SoftNorms.excPremisesOf (relaxDoc C Nd))
      rw [List.flatMap_map, List.mem_flatMap]
      refine ⟨M, hM, ?_⟩
      rw [hoff M hM hn]; exact hφ'

end Premises

/-! ## The exception predicate in the relaxed expansion -/

/-- The exception predicate is no layer symbol of the relaxed elaboration. -/
theorem Twin.excepted_out {C : SoftDoc} {Nd : SoftNode} (hw : Twin C Nd) (hn : ∃ M ∈ C.T.nodes, M.name = Nd.name)
    (hdef : ∀ d ∈ C.T.definitions, d.name ≠ VE.SoftNorms.exceptedName Nd) :
    VE.SoftNorms.exceptedName Nd ∉ VE.Norms.layerNames (soften (relaxDoc C Nd)).T := by
  intro h
  rcases List.mem_append.mp (Wire.layerNames_sub h) with h | h
  · obtain ⟨r, hr, hrn⟩ := List.mem_map.mp h
    obtain ⟨M, hM, hMn⟩ := hn
    have hdec : VE.SoftNorms.exceptedName Nd ∈ VE.SoftNorms.decisionNames (relaxDoc C Nd) := by
      unfold VE.SoftNorms.decisionNames VE.SoftNorms.decisions VE.SoftNorms.exceptedDecisions
      refine List.mem_map.mpr ⟨(VE.SoftNorms.exceptedName (relaxTo Nd M),
        VE.SoftNorms.sortsOf (relaxDoc C Nd) (relaxTo Nd M).pred), ?_, ?_⟩
      · refine List.mem_append_left _ (List.mem_append_left _ (List.mem_map.mpr ⟨relaxTo Nd M, ?_, rfl⟩))
        refine List.mem_filter.mpr ⟨relax_mem hM, ?_⟩
        rw [relaxTo_of_eq hMn]; rfl
      · show VE.SoftNorms.exceptedName (relaxTo Nd M) = _
        unfold VE.SoftNorms.exceptedName; rw [relaxTo_name, hMn]
    have h1 := hw.valid.decFresh _ hdec
    have h2 := hw.valid.regDecl r hr
    have hrn' : r.name = VE.SoftNorms.exceptedName Nd := hrn
    rw [hrn', h1] at h2
    cases h2
  · obtain ⟨d, hd, hdn⟩ := List.mem_map.mp h
    exact hdef d hd hdn

theorem Twin.excepted_canon {C : SoftDoc} {Nd : SoftNode} (hw : Twin C Nd) (hn : ∃ M ∈ C.T.nodes, M.name = Nd.name)
    (hdef : ∀ d ∈ C.T.definitions, d.name ≠ VE.SoftNorms.exceptedName Nd) (S : VE.Structure.{u})
    (hS : ∀ vs, ¬ S.relation (VE.SoftNorms.exceptedName Nd) vs) (ρ : VE.Valuation S) :
    ¬ (exceptedF C Nd).denote (canon (soften (relaxDoc C Nd)) S) ρ :=
  have hc : ∀ vs, ¬ (canon (soften (relaxDoc C Nd)) S).relation (VE.SoftNorms.exceptedName Nd) vs :=
    fun vs h => hS vs ((VE.SoftNorms.canon_off S (hw.excepted_out hn hdef) vs).mp h)
  atom_false hc _ ρ

end VE.Readings
