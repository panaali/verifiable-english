import VE.NormDefaults.Layered
import VE.Readings.SupWitness

/-! The premise-pack theorems over `Layered.lean`'s legacy packs (docs/spec/premise-packs.md 2.5 (3), 2.6, 2.8 and
2.9, 2.10): `X` typed over `envX`, today's soft and rights sources assemble unchanged in today's order, `packPremises`
reads today's arrays, `packFault` gives today's `filledX` text on today's lists, every filled situation the route
accepts satisfies the whole `X`, and the kind table answers today's kinds as `layeredCase` does. -/
namespace VE.NormDefaults.Packs
open Lean
open VE.Norms (envAt size)
open VE.NormDefaults.Wire (LayeredU softLabelledU softPack rightsPack extraValid legacyKinds legacyRows)

/-! ## 2.5 (3) Typing -/

theorem lookup_mem {α γ : Type} [BEq α] [LawfulBEq α] {n : α} {v : γ} :
    ∀ {l : List (α × γ)}, l.lookup n = some v → (n, v) ∈ l
  | [], h => by cases h
  | (k, w) :: l, h => by
    simp only [List.lookup] at h
    split at h
    · rename_i he
      cases h
      rw [eq_of_beq he]
      exact List.mem_cons_self
    · exact List.mem_cons_of_mem _ (lookup_mem h)

theorem lookup_flatMap_mem {α β γ : Type} [BEq α] [LawfulBEq α] {f : β → List (α × γ)} {qs : List β} {p : β}
    (hp : p ∈ qs) {n : α} {v : γ} (hl : (f p).lookup n = some v)
    (hn : ∀ q ∈ qs, ∀ w, (n, w) ∈ f q → q = p) : (qs.flatMap f).lookup n = some v := by
  induction qs with
  | nil => cases hp
  | cons q qs ih =>
    rw [List.flatMap_cons, List.lookup_append]
    by_cases hq : q = p
    · subst hq
      rw [hl]
      rfl
    · have : (f q).lookup n = none := by
        cases h : (f q).lookup n with
        | none => rfl
        | some w => exact absurd (hn q List.mem_cons_self w (lookup_mem h)) hq
      rw [this, Option.none_or]
      exact ih (by rcases List.mem_cons.mp hp with h | h; exact absurd h.symm hq; exact h)
        (fun q' hq' w hw => hn q' (List.mem_cons_of_mem _ hq') w hw)

theorem lookup_flatMap_none {α β γ : Type} [BEq α] [LawfulBEq α] {f : β → List (α × γ)} {qs : List β} {n : α}
    {v : γ} (h : (qs.flatMap f).lookup n = some v) : ∃ q ∈ qs, (n, v) ∈ f q := by
  have := lookup_mem h
  obtain ⟨q, hq, hm⟩ := List.mem_flatMap.mp this
  exact ⟨q, hq, hm⟩

/-- A generated name of distinct names belongs to one pack only. -/
theorem names_unique : ∀ {qs : List Pack}, (names qs).Nodup →
    ∀ p ∈ qs, ∀ q ∈ qs, ∀ n ∈ p.names, n ∈ q.names → q = p
  | [], _ => fun _ hp => absurd hp List.not_mem_nil
  | r :: rs, h => by
    simp only [names, List.flatMap_cons] at h
    obtain ⟨-, hrs, hdis⟩ := List.nodup_append.mp h
    intro p hp q hq n hnp hnq
    have hout : ∀ x ∈ rs, n ∈ x.names → n ∉ r.names := fun x hx hn hr =>
      hdis n hr n (List.mem_flatMap.mpr ⟨x, hx, hn⟩) rfl
    rcases List.mem_cons.mp hp with hp1 | hp1 <;> rcases List.mem_cons.mp hq with hq1 | hq1
    · rw [hp1, hq1]
    · exact absurd (hp1 ▸ hnp) (hout q hq1 hnq)
    · exact absurd (hq1 ▸ hnq) (hout p hp1 hnp)
    · exact names_unique hrs p hp1 q hq1 n hnp hnq

/-- 2.5 (3): each pack typed over the base environment and its own names gives `X` typed over `envX`. -/
theorem assemble_wellFormed {U : UDoc} {used : Nat} {ps qs : List Pack} (h : assemble U used ps = .ok qs)
    (hp : ∀ p ∈ ps, ∀ a ∈ p.labelled, a.2.WellFormed (extendEnv (envAt (fill U) 0) p.decls p.consts) []) :
    ∀ a ∈ X qs, a.WellFormed (envX U qs) [] := by
  obtain ⟨-, hperm, -⟩ := assemble_order h
  obtain ⟨-, hnames, hfresh, -⟩ := assemble_fresh h
  -- a generated name belongs to one pack only
  have hone : ∀ p ∈ qs, ∀ q ∈ qs, ∀ n ∈ p.names, n ∈ q.names → q = p := names_unique hnames
  intro a ha
  simp only [X, labelledX, List.mem_map, List.mem_flatMap] at ha
  obtain ⟨b, ⟨p, hpq, hb⟩, rfl⟩ := ha
  refine VE.Readings.wf_sub (E := extendEnv (envAt (fill U) 0) p.decls p.consts) (E' := envX U qs) (fun s hs => hs) (fun x s hx => ?_) (fun r ss hr => ?_) _ _
    (hp p (hperm.mem_iff.mp hpq) b hb)
  · simp only [extendEnv, envX] at hx ⊢
    split at hx
    · rename_i hl
      cases hx
      rw [lookup_flatMap_mem hpq hl (fun q hq w hw => hone p hpq q hq x
        (List.mem_append_right _ (List.mem_map.mpr ⟨(x, _), lookup_mem hl, rfl⟩))
        (List.mem_append_right _ (List.mem_map.mpr ⟨(x, w), hw, rfl⟩)))]
    · rename_i hl
      cases h' : (qs.flatMap (·.consts)).lookup x with
      | none => exact hx
      | some w =>
        obtain ⟨q, hq, hm⟩ := lookup_flatMap_none h'
        have := (hfresh q hq x (List.mem_append_right _ (List.mem_map.mpr ⟨(x, w), hm, rfl⟩))).2.1
        simp [fullEnv, VE.Norms.envAt_constants] at this
        simp [VE.Norms.envAt_constants, this] at hx
  · simp only [extendEnv, envX] at hr ⊢
    split at hr
    · rename_i hl
      cases hr
      rw [lookup_flatMap_mem hpq hl (fun q hq w hw => hone p hpq q hq r
        (List.mem_append_left _ (List.mem_map.mpr ⟨(r, _), lookup_mem hl, rfl⟩))
        (List.mem_append_left _ (List.mem_map.mpr ⟨(r, w), hw, rfl⟩)))]
    · rename_i hl
      cases h' : (qs.flatMap (·.decls)).lookup r with
      | none => exact hr
      | some w =>
        obtain ⟨q, hq, hm⟩ := lookup_flatMap_none h'
        have := (hfresh q hq r (List.mem_append_left _ (List.mem_map.mpr ⟨(r, w), hm, rfl⟩))).1
        have hE := VE.Norms.envAt_sub _ _ _ _ hr
        simp only [fullEnv, VE.Norms.envAt_size_predicates] at this
        rw [this] at hE
        cases hE

/-! ## 2.6 The legacy packs -/

theorem firstRepeat_none_of : ∀ (seen : List String) (l : List (String × String)), (l.map (·.2)).Nodup →
    (∀ x ∈ l, x.2 ∉ seen) → firstRepeat seen l = none
  | _, [], _, _ => rfl
  | seen, (i, n) :: rest, hn, hs => by
    have hn' := List.nodup_cons.mp hn
    simp only [firstRepeat]
    rw [if_neg (by simpa using hs (i, n) List.mem_cons_self)]
    refine firstRepeat_none_of (n :: seen) rest hn'.2 (fun x hx hm => ?_)
    rcases List.mem_cons.mp hm with h | h
    · exact hn'.1 (h ▸ List.mem_map.mpr ⟨x, hx, rfl⟩)
    · exact hs x (List.mem_cons_of_mem _ hx) h

/-- The checks `assembleIn` runs pass on constraint packs in `packOrder`, with distinct labels. -/
theorem assembleIn_constraint (pre : List (String × String)) (E : VE.Environment) (used : Nat) (hu : used ≤ 256)
    (ps : List Pack) (hps : ordered ps = ps) (hm : ∀ p ∈ ps, p.id ∈ packOrder)
    (hc : ∀ i ∈ packOrder, ps.countP (·.id == i) ≤ 1) (hd : ∀ p ∈ ps, p.decls = [] ∧ p.consts = [])
    (hn : ((labelledX ps).map (·.1)).Nodup) (qs : List Pack) (hq : ordered qs = ps)
    (hqm : ∀ p ∈ qs, p.id ∈ packOrder) (hqc : ∀ i ∈ packOrder, qs.countP (·.id == i) ≤ 1) :
    assembleIn pre E used qs = .ok ps := by
  have _ := hps; have _ := hm; have _ := hc
  have hnames : ∀ p ∈ ps, p.names = [] := fun p hp => by simp [Pack.names, (hd p hp).1, (hd p hp).2]
  have hnamed : ps.flatMap (fun p => p.names.map (fun n => (p.id, n))) = [] :=
    List.flatMap_eq_nil_iff.mpr (fun p hp => by simp [hnames p hp])
  have hl : firstRepeat [] (ps.flatMap (fun p => p.labelled.map (fun a => (p.id, a.1)))) = none :=
    firstRepeat_none_of [] _ (by simpa [labelledX, List.map_flatMap, Function.comp_def] using hn)
      (fun _ _ h => List.not_mem_nil h)
  have hN : names ps = [] := List.flatMap_eq_nil_iff.mpr hnames
  simp only [assembleIn]
  rw [List.find?_eq_none.mpr (fun p hp => by simpa using hqm p hp),
    List.find?_eq_none.mpr (fun i hi => by simpa using hqc i hi)]
  simp only [hq, hl, hnamed, List.find?_nil, firstRepeat, hN, List.length_nil, Nat.add_zero,
    Nat.not_lt.mpr hu, if_false]
  rw [List.find?_eq_none.mpr (fun p hp => by simp [hnames p hp])]
  rfl

/-- 2.6 (5): assembly accepts today's soft source unchanged. -/
theorem assemble_legacy_soft (U : UDoc) (D : VE.SoftNorms.SoftDoc) (used : Nat) (hu : used ≤ 256)
    (hn : ((softLabelledU U D).map (·.1)).Nodup) :
    assemble U used [softPack U D] = .ok [softPack U D] := by
  have ho : ordered [softPack U D] = [softPack U D] := by simp [ordered, packOrder, softPack]
  refine assembleIn_constraint _ _ used hu _ ho (by simp [softPack, packOrder]) (by simp [packOrder, softPack])
    (by simp [softPack]) (by simpa [labelledX, softPack] using hn) _ ho (by simp [softPack, packOrder])
    (by simp [packOrder, softPack])

/-- 2.6 (5): and today's rights source, in today's order, whichever order the decoder lists them in. -/
theorem assemble_legacy_rights (U : UDoc) (R : VE.Rights.RightsDoc) (used : Nat) (hu : used ≤ 256)
    (hn : ((softLabelledU U (VE.Rights.correlate R) ++ VE.Rights.limPremisesLabelled R).map (·.1)).Nodup) :
    assemble U used [softPack U (VE.Rights.correlate R), rightsPack R] =
      .ok [softPack U (VE.Rights.correlate R), rightsPack R] ∧
    assemble U used [rightsPack R, softPack U (VE.Rights.correlate R)] =
      .ok [softPack U (VE.Rights.correlate R), rightsPack R] := by
  have ho : ordered [softPack U (VE.Rights.correlate R), rightsPack R] =
      [softPack U (VE.Rights.correlate R), rightsPack R] := by simp [ordered, packOrder, softPack, rightsPack]
  have ho' : ordered [rightsPack R, softPack U (VE.Rights.correlate R)] =
      [softPack U (VE.Rights.correlate R), rightsPack R] := by simp [ordered, packOrder, softPack, rightsPack]
  have hm : ∀ p ∈ [softPack U (VE.Rights.correlate R), rightsPack R], p.id ∈ packOrder := by
    simp [softPack, rightsPack, packOrder]
  have hc : ∀ i ∈ packOrder, [softPack U (VE.Rights.correlate R), rightsPack R].countP (·.id == i) ≤ 1 := by
    simp [packOrder, softPack, rightsPack]
  have hd : ∀ p ∈ [softPack U (VE.Rights.correlate R), rightsPack R], p.decls = [] ∧ p.consts = [] := by
    simp [softPack, rightsPack]
  have hl : ((labelledX [softPack U (VE.Rights.correlate R), rightsPack R]).map (·.1)).Nodup := by
    simpa [labelledX, softPack, rightsPack] using hn
  exact ⟨assembleIn_constraint _ _ used hu _ ho hm hc hd hl _ ho hm hc,
    assembleIn_constraint _ _ used hu _ ho hm hc hd hl _ ho' (by simp [softPack, rightsPack, packOrder])
      (by simp [packOrder, softPack, rightsPack])⟩

theorem packPremises_legacy (U : UDoc) (R : VE.Rights.RightsDoc) :
    packPremises [softPack U (VE.Rights.correlate R), rightsPack R] "soft" = softLabelledU U (VE.Rights.correlate R) ∧
    packPremises [softPack U (VE.Rights.correlate R), rightsPack R] "rights" = VE.Rights.limPremisesLabelled R := by
  simp [packPremises, softPack, rightsPack]

/-! ## 2.8 Diagnostics on today's lists -/

theorem firstFailing_one (p : Pack) (holds : VE.Formula → Bool) :
    (firstFailing [p] holds = none ↔ (p.labelled.map (·.2)).all holds = true) ∧
    ∀ i l, firstFailing [p] holds = some (i, l) → i = p.id := by
  refine ⟨⟨fun h => ?_, fun h => ?_⟩, fun i l h => ?_⟩
  · simp only [firstFailing, List.flatMap_cons, List.flatMap_nil, List.append_nil] at h
    have := List.findSome?_eq_none_iff.mp h
    simp only [List.all_eq_true, List.mem_map]
    rintro _ ⟨a, ha, rfl⟩
    have := this (p.id, a) (List.mem_map.mpr ⟨a, ha, rfl⟩)
    simp only at this
    split at this
    · assumption
    · cases this
  · simp only [firstFailing, List.flatMap_cons, List.flatMap_nil, List.append_nil]
    refine List.findSome?_eq_none_iff.mpr (fun x hx => ?_)
    obtain ⟨a, ha, rfl⟩ := List.mem_map.mp hx
    simp only [List.all_eq_true, List.mem_map] at h
    simp [h a.2 ⟨a, ha, rfl⟩]
  · simp only [firstFailing, List.flatMap_cons, List.flatMap_nil, List.append_nil] at h
    obtain ⟨x, hx, he⟩ := List.exists_of_findSome?_eq_some h
    obtain ⟨a, _, rfl⟩ := List.mem_map.mp hx
    simp only at he
    split at he
    · cases he
    · cases he; rfl

theorem firstFailing_two (s r : Pack) (holds : VE.Formula → Bool) :
    firstFailing [s, r] holds = (firstFailing [s] holds).or (firstFailing [r] holds) := by
  simp [firstFailing, List.findSome?_append]

/-- 2.8 (8): on a legacy rights list the text is today's `filledX` text. -/
theorem packFault_legacy_rights (U : UDoc) (R : VE.Rights.RightsDoc) (M : VE.FiniteModel VE.Bridge.Entity)
    (F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity)
    (hx : extraValid U (X [softPack U (VE.Rights.correlate R), rightsPack R]) M F = false) :
    packFault [softPack U (VE.Rights.correlate R), rightsPack R] (fun a => a.eval (M.withFill F) []) =
      VE.Route.Wire.invalidModel
        (if extraValid U ((softLabelledU U (VE.Rights.correlate R)).map (·.2)) M F then "rights" else "soft") := by
  have hsome := firstFailing_some _ _ hx
  have hleg : legacyIds.contains ([softPack U (VE.Rights.correlate R), rightsPack R].map (·.id)) = true := by
    simp [legacyIds, softPack, rightsPack]
  unfold packFault
  rw [firstFailing_two] at hsome ⊢
  by_cases hs : extraValid U ((softLabelledU U (VE.Rights.correlate R)).map (·.2)) M F = true
  · have hn : firstFailing [softPack U (VE.Rights.correlate R)] (fun a => a.eval (M.withFill F) []) = none :=
      (firstFailing_one _ _).1.mpr hs
    rw [hn, Option.none_or] at hsome ⊢
    obtain ⟨⟨i, l⟩, he⟩ := Option.isSome_iff_exists.mp hsome
    rw [he, if_pos hs]
    simp only
    rw [if_pos hleg, (firstFailing_one _ _).2 i l he]
    rfl
  · rw [if_neg hs]
    cases he : firstFailing [softPack U (VE.Rights.correlate R)] (fun a => a.eval (M.withFill F) []) with
    | none => exact absurd ((firstFailing_one _ _).1.mp he) hs
    | some x =>
      obtain ⟨i, l⟩ := x
      simp only [Option.some_or]
      rw [if_pos hleg, (firstFailing_one _ _).2 i l he]
      rfl

/-- 2.8 (8): on a legacy soft list it is `InvalidModel(soft)`. -/
theorem packFault_legacy_soft (U : UDoc) (D : VE.SoftNorms.SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity)
    (F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity) (hx : extraValid U (X [softPack U D]) M F = false) :
    packFault [softPack U D] (fun a => a.eval (M.withFill F) []) = VE.Route.Wire.invalidModel "soft" := by
  have hsome := firstFailing_some _ _ hx
  obtain ⟨⟨i, l⟩, he⟩ := Option.isSome_iff_exists.mp hsome
  unfold packFault
  rw [he]
  simp [legacyIds, softPack, (firstFailing_one _ _).2 i l he]

/-! ## 2.9 What PK-1 guarantees about witnesses -/

/-- 2.9 (9): every filled situation the layered route accepts satisfies the whole `X`. -/
theorem filledX_whole (L : LayeredU) (w : Json) (fw : VE.NormDefaults.Wire.FilledX L)
    (_h : VE.NormDefaults.Wire.filledX L w = .ok fw) : extraValid L.U L.X fw.S.M fw.F = true := fw.extra_ok

/-! ## 2.10 The kind table -/

/-- `layeredCase` answers each of today's four kinds, or refuses it; it never returns `none` for one. -/
theorem layeredCase_some (L : LayeredU) (id kind : String) (j : Json) (hk : kind ∈ legacyKinds) :
    VE.NormDefaults.Wire.layeredCase L id kind j ≠ .ok none := by
  intro h
  simp only [legacyKinds, List.mem_cons, List.not_mem_nil, or_false] at hk
  rcases hk with rfl | rfl | rfl | rfl <;>
    simp [VE.NormDefaults.Wire.layeredCase, Functor.map, Except.map, bind, Except.bind, Seq.seq, pure,
      Except.pure] at h <;>
    repeat' (first | (split at h) | simp_all)

theorem dispatch_legacy (ids : List String) (L : LayeredU) (id kind : String) (j : Json) (hk : kind ∈ legacyKinds) :
    dispatch legacyRows ids L id kind j = VE.NormDefaults.Wire.layeredCase L id kind j := by
  have hs := layeredCase_some L id kind j hk
  have hf : legacyRows.find? (·.kind == kind) = some ⟨kind, none, fun L id j => do
      match ← VE.NormDefaults.Wire.layeredCase L id kind j with
      | some a => pure a
      | none => throw "unreachable"⟩ := by
    simp only [legacyKinds, List.mem_cons, List.not_mem_nil, or_false] at hk
    rcases hk with rfl | rfl | rfl | rfl <;> rfl
  rw [dispatch, hf]
  dsimp only
  generalize VE.NormDefaults.Wire.layeredCase L id kind j = x at hs ⊢
  rcases x with _ | _ | _
  · rfl
  · exact absurd rfl hs
  · rfl

/-- The route's dispatch answers every kind as `layeredCase` does: today's four by `dispatch_legacy`, any other
`none`. -/
theorem kindCase_eq (L : LayeredU) (id kind : String) (j : Json) :
    VE.NormDefaults.Wire.kindCase L id kind j = VE.NormDefaults.Wire.layeredCase L id kind j := by
  by_cases hk : kind ∈ legacyKinds
  · exact dispatch_legacy _ L id kind j hk
  · simp only [legacyKinds, List.mem_cons, List.not_mem_nil, or_false, not_or] at hk
    obtain ⟨h1, h2, h3, h4⟩ := hk
    have hf : legacyRows.find? (·.kind == kind) = none := by
      simp [legacyRows, legacyKinds, Ne.symm h1, Ne.symm h2, Ne.symm h3, Ne.symm h4]
    simp [VE.NormDefaults.Wire.kindCase, dispatch, hf, VE.NormDefaults.Wire.layeredCase, h1, h2, h3, h4]

end VE.NormDefaults.Packs
