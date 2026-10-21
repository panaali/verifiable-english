import VE.Scope.Govern
import VE.NormDefaults.Check
import VE.Readings.Strings

/-! Theorems of scope@0's effects and of `govern` (docs/spec/scope.md 5.1). -/

namespace VE.Scope
open Lean
open Std.DTreeMap.Internal (Impl)

theorem members_obj (kvs : Std.TreeMap.Raw String Json) : members (.obj kvs) = kvs.toList := rfl

theorem hasOwn_mono : ∀ (n m : Nat) (j : Json), n ≤ m → hasOwn n j = true → hasOwn m j = true
  | 0, _, _, _, h => by simp [hasOwn] at h
  | n + 1, m + 1, j, hnm, h => by
    have ih := fun j => hasOwn_mono n m j (Nat.le_of_succ_le_succ hnm)
    cases j with
    | str s => simpa [hasOwn] using h
    | arr xs =>
      simp only [hasOwn, List.any_eq_true] at h ⊢
      obtain ⟨x, hx, hxo⟩ := h
      exact ⟨x, hx, ih x hxo⟩
    | obj kvs =>
      simp only [hasOwn, members_obj, List.any_eq_true] at h ⊢
      obtain ⟨x, hx, hxo⟩ := h
      exact ⟨x, hx, ih x.2 hxo⟩
    | _ => simp [hasOwn] at h
  | n + 1, 0, _, hnm, _ => absurd hnm (by omega)

theorem substOwn_no_own_le (g : Json) (hg : hasOwn depthLimit g = false) :
    ∀ (n : Nat) (c : Json), n ≤ depthLimit → hasOwn n (substOwn g n c) = false
  | 0, _, _ => by simp [hasOwn]
  | n + 1, c, hn => by
    have ih := fun c => substOwn_no_own_le g hg n c (by omega)
    cases c with
    | str s =>
      by_cases hs : s = "own"
      · subst hs
        simp only [substOwn, beq_self_eq_true, if_true]
        cases hgo : hasOwn (n + 1) g with
        | false => rfl
        | true => rw [hasOwn_mono (n + 1) depthLimit g hn hgo] at hg; cases hg
      · simp [substOwn, hasOwn, hs]
    | arr xs =>
      simp only [substOwn, hasOwn, Array.toList_map, List.any_map, List.any_eq_false]
      exact fun x _ => by simpa using ih x
    | obj kvs =>
      simp only [substOwn, hasOwn, members_obj, Std.TreeMap.Raw.toList_map, List.any_map, List.any_eq_false]
      exact fun x _ => by simpa using ih x.2
    | _ => simp [substOwn, hasOwn]

set_option linter.unusedVariables false in
/-- The statement keeps the spec's hypothesis `hc`; the proof does not need it, since `hasOwn` reads no deeper
    than `substOwn` writes. -/
theorem substOwn_no_own (g c : Json) (hg : hasOwn depthLimit g = false) (hc : depthOk depthLimit c = true) :
    hasOwn depthLimit (substOwn g depthLimit c) = false :=
  substOwn_no_own_le g hg depthLimit c (Nat.le_refl _)

theorem impl_map_eq (f : String → Json → Json) : ∀ (t : Impl String (fun _ => Json)),
    (∀ p ∈ Impl.Const.toList t, f p.1 p.2 = p.2) → t.map f = t
  | .leaf, _ => rfl
  | .inner sz k v l r, h => by
    rw [Impl.Const.toList_eq_toListModel_map] at h
    simp only [Impl.toListModel_inner, List.map_append, List.map_cons, List.mem_append, List.mem_cons] at h
    have hl := impl_map_eq f l (fun p hp => h p (Or.inl (by
      rw [Impl.Const.toList_eq_toListModel_map] at hp; exact hp)))
    have hr := impl_map_eq f r (fun p hp => h p (Or.inr (Or.inr (by
      rw [Impl.Const.toList_eq_toListModel_map] at hp; exact hp))))
    have hk := h (k, v) (Or.inr (Or.inl rfl))
    simp only [Impl.map, hl, hr, hk]

theorem substOwn_id_le (g : Json) : ∀ (n : Nat) (c : Json), hasOwn n c = false → substOwn g n c = c
  | 0, _, _ => rfl
  | n + 1, c, hc => by
    have ih := substOwn_id_le g n
    cases c with
    | str s =>
      have hs : (s == "own") = false := by simpa [hasOwn] using hc
      simp [substOwn, hs]
    | arr xs =>
      simp only [hasOwn, List.any_eq_false, Bool.not_eq_true] at hc
      simp only [substOwn]
      congr 1
      rcases xs with ⟨l⟩
      simp only [List.map_toArray, Array.mk.injEq]
      exact (List.map_congr_left (fun x hx => ih x (hc x hx))).trans (List.map_id l)
    | obj kvs =>
      simp only [hasOwn, members_obj, List.any_eq_false, Bool.not_eq_true] at hc
      simp only [substOwn]
      congr 1
      rcases kvs with ⟨⟨t⟩⟩
      simp only [Std.TreeMap.Raw.map, Std.DTreeMap.Raw.map, Std.TreeMap.Raw.mk.injEq,
        Std.DTreeMap.Raw.mk.injEq]
      exact impl_map_eq _ t (fun p hp => ih p.2 (hc p hp))
    | _ => rfl

theorem substOwn_id (g c : Json) (hc : hasOwn depthLimit c = false) : substOwn g depthLimit c = c :=
  substOwn_id_le g depthLimit c hc

theorem commutes_symm (e₁ e₂ : Effect) : Commutes e₁ e₂ = Commutes e₂ e₁ := by
  cases e₁ <;> cases e₂ <;> simp [Commutes, Bool.and_comm]

/-! Joining parts -/

theorem firstKeys_mem (l : List (String × Json)) (hf : ∀ p ∈ l, ∀ q ∈ l, p.1 = q.1 → p = q) :
    ∀ p ∈ l, p ∈ VE.Readings.Wire.firstKeys l := by
  induction l with
  | nil => simp
  | cons e rest ih =>
    intro p hp
    simp only [VE.Readings.Wire.firstKeys, List.mem_cons, List.mem_filter]
    rcases List.mem_cons.mp hp with rfl | hp
    · exact Or.inl rfl
    · by_cases he : p.1 = e.1
      · exact Or.inl (hf p (List.mem_cons_of_mem _ hp) e List.mem_cons_self he)
      · exact Or.inr ⟨ih (fun a ha b hb => hf a (List.mem_cons_of_mem _ ha) b (List.mem_cons_of_mem _ hb)) p hp,
          by simpa using he⟩

/-- What `lookups` lists is exactly what lookup finds, each key once. -/
theorem lookups_spec (j : Json) (ls : List (String × Json)) (h : lookups j = .ok ls) :
    (ls.map (·.1)).Nodup ∧ ∀ k v, (k, v) ∈ ls ↔ j.getObjVal? k = .ok v := by
  cases j with
  | obj kvs =>
    simp only [lookups, VE.Bridge.fields, Json.getObj?, bind, Except.bind, pure, Except.pure,
      Except.ok.injEq] at h
    subst h
    refine ⟨VE.Readings.Wire.firstKeys_nodup _, fun k v => ⟨fun hm => ?_, fun hg => ?_⟩⟩
    · have := VE.Readings.Wire.firstKeys_sub _ _ hm
      obtain ⟨kv, _, hkv⟩ := List.mem_filterMap.mp this
      cases hg : (Json.obj kvs).getObjVal? kv.1 with
      | error _ => simp [hg, Except.toOption] at hkv
      | ok w =>
        simp only [hg, Except.toOption, Option.map_some, Option.some.injEq, Prod.mk.injEq] at hkv
        obtain ⟨rfl, rfl⟩ := hkv
        exact hg
    · apply firstKeys_mem
      · intro p hp q hq hpq
        obtain ⟨a, _, ha⟩ := List.mem_filterMap.mp hp
        obtain ⟨b, _, hb⟩ := List.mem_filterMap.mp hq
        cases hga : (Json.obj kvs).getObjVal? a.1 with
        | error _ => simp [hga, Except.toOption] at ha
        | ok wa =>
          cases hgb : (Json.obj kvs).getObjVal? b.1 with
          | error _ => simp [hgb, Except.toOption] at hb
          | ok wb =>
            simp only [hga, Except.toOption, Option.map_some, Option.some.injEq] at ha
            simp only [hgb, Except.toOption, Option.map_some, Option.some.injEq] at hb
            subst ha hb
            simp only at hpq
            rw [hpq, hgb] at hga
            cases hga
            rw [hpq]
      · exact List.mem_filterMap.mpr ⟨(k, v), VE.Readings.Wire.entries_mem hg, by simp [hg, Except.toOption]⟩
  | _ => simp [lookups, VE.Bridge.fields, Json.getObj?, bind, Except.bind] at h <;> cases h

theorem lookups_absent (j : Json) (ls : List (String × Json)) (h : lookups j = .ok ls) (k : String) :
    (j.getObjVal? k).toOption = none ↔ k ∉ ls.map (·.1) := by
  have hs := (lookups_spec j ls h).2
  constructor
  · intro hn hk
    obtain ⟨p, hp, rfl⟩ := List.mem_map.mp hk
    rw [(hs p.1 p.2).mp hp] at hn
    simp [Except.toOption] at hn
  · intro hk
    cases hg : j.getObjVal? k with
    | error _ => rfl
    | ok v => exact absurd (List.mem_map.mpr ⟨(k, v), (hs k v).mpr hg, rfl⟩) hk

theorem mkObj_getObjVal (l : List (String × Json)) (hd : (l.map (·.1)).Nodup) (k : String) (v : Json) :
    (Json.mkObj l).getObjVal? k = .ok v ↔ (k, v) ∈ l := by
  constructor
  · intro h
    by_cases hk : (l.map (·.1)).contains k = true
    · obtain ⟨p, hp, hpk⟩ := List.mem_map.mp (List.contains_iff_mem.mp hk)
      have := VE.Readings.Wire.mkObj_get hd (k := p.1) (v := p.2) hp
      rw [hpk, h] at this
      cases this
      rw [← hpk]
      exact hp
    · have hk' : (l.map (·.1)).contains k = false := Bool.eq_false_iff.mpr hk
      have := Std.TreeMap.Raw.getElem?_ofList_of_contains_eq_false (cmp := compare) hk'
      simp only [Json.mkObj, Json.getObjVal?, Std.TreeMap.Raw.get?_eq_getElem?] at h
      rw [this] at h
      cases h
  · exact VE.Readings.Wire.mkObj_get hd

/-- One owner per field: every key of the joined object comes from exactly one side. -/
theorem mergeParts_keys (u : String) (lead item out : Json) (h : mergeParts u lead item = .ok out) (k : String)
    (v : Json) : out.getObjVal? k = .ok v ↔
      (lead.getObjVal? k = .ok v ∧ (item.getObjVal? k).toOption = none) ∨
      (item.getObjVal? k = .ok v ∧ (lead.getObjVal? k).toOption = none) := by
  cases hl : lookups lead with
  | error _ => simp [mergeParts, hl, Except.mapError, bind, Except.bind] at h
  | ok ls =>
    cases hi : lookups item with
    | error _ => simp [mergeParts, hl, hi, Except.mapError, bind, Except.bind] at h
    | ok is =>
      cases hf : ls.find? (fun kv => is.any (·.1 == kv.1)) with
      | some p => simp [mergeParts, hl, hi, hf, Except.mapError, bind, Except.bind, throw, throwThe,
          MonadExceptOf.throw] at h
      | none =>
        simp only [mergeParts, hl, hi, hf, Except.mapError, bind, Except.bind, pure, Except.pure,
          Except.ok.injEq] at h
        subst h
        obtain ⟨hdl, hsl⟩ := lookups_spec lead ls hl
        obtain ⟨hdi, hsi⟩ := lookups_spec item is hi
        have disj : ∀ k, k ∈ ls.map (·.1) → k ∉ is.map (·.1) := by
          intro k hk hk'
          obtain ⟨p, hp, rfl⟩ := List.mem_map.mp hk
          obtain ⟨q, hq, hqk⟩ := List.mem_map.mp hk'
          have := List.find?_eq_none.mp hf p hp
          simp only [List.any_eq_true, beq_iff_eq, not_exists, not_and] at this
          exact this q hq hqk
        have hd : ((ls ++ is).map (·.1)).Nodup := by
          rw [List.map_append, List.nodup_append]
          exact ⟨hdl, hdi, fun a ha b hb hab => disj a ha (hab ▸ hb)⟩
        rw [mkObj_getObjVal _ hd, List.mem_append, hsl, hsi, lookups_absent item is hi,
          lookups_absent lead ls hl]
        constructor
        · rintro (h | h)
          · exact Or.inl ⟨h, disj k (List.mem_map.mpr ⟨(k, v), (hsl k v).mpr h, rfl⟩)⟩
          · exact Or.inr ⟨h, fun hk => disj k hk (List.mem_map.mpr ⟨(k, v), (hsi k v).mpr h, rfl⟩)⟩
        · rintro (⟨h, _⟩ | ⟨h, _⟩)
          · exact Or.inl h
          · exact Or.inr h

theorem mergeParts_conflict (u : String) (lead item : Json) (k : String)
    (hl : (lead.getObjVal? k).toOption.isSome) (hi : (item.getObjVal? k).toOption.isSome) :
    (mergeParts u lead item).isOk = false := by
  cases hls : lookups lead with
  | error _ => simp [mergeParts, hls, Except.mapError, bind, Except.bind, Except.isOk, Except.toBool]
  | ok ls =>
    cases his : lookups item with
    | error _ => simp [mergeParts, hls, his, Except.mapError, bind, Except.bind, Except.isOk, Except.toBool]
    | ok is =>
      have hkl : k ∈ ls.map (·.1) := by
        apply Classical.byContradiction; intro hn
        rw [← lookups_absent lead ls hls] at hn
        simp [hn] at hl
      have hki : k ∈ is.map (·.1) := by
        apply Classical.byContradiction; intro hn
        rw [← lookups_absent item is his] at hn
        simp [hn] at hi
      cases hf : ls.find? (fun kv => is.any (·.1 == kv.1)) with
      | some p => simp [mergeParts, hls, his, hf, Except.mapError, bind, Except.bind, throw, throwThe,
          MonadExceptOf.throw, Except.isOk, Except.toBool]
      | none =>
        obtain ⟨p, hp, rfl⟩ := List.mem_map.mp hkl
        obtain ⟨q, hq, hqk⟩ := List.mem_map.mp hki
        have := List.find?_eq_none.mp hf p hp
        simp only [List.any_eq_true, beq_iff_eq, not_exists, not_and] at this
        exact absurd hqk (this q hq)

theorem firstKeys_self : ∀ (l : List (String × Json)), (l.map (·.1)).Nodup → VE.Readings.Wire.firstKeys l = l
  | [], _ => rfl
  | e :: rest, h => by
    simp only [List.map_cons, List.nodup_cons] at h
    simp only [VE.Readings.Wire.firstKeys, firstKeys_self rest h.2, List.cons.injEq, true_and]
    refine List.filter_eq_self.mpr fun x hx => ?_
    have hne : x.1 ≠ e.1 := fun hxe => h.1 (by rw [← hxe]; exact List.mem_map_of_mem hx)
    simpa using hne

/-- On a well-formed object (and on any other value), `lookups` is `VE.Bridge.fields`: the join reads members
    through lookup only so that `mergeParts_keys` holds of every JSON value, and accepts the same on well-formed
    objects. -/
theorem lookups_fields (j : Json) (hw : ∀ kvs, j = .obj kvs → kvs.WF) : lookups j = VE.Bridge.fields j := by
  cases j with
  | obj kvs =>
    have h := hw kvs rfl
    have hfm : kvs.toList.filterMap (fun kv => ((Json.obj kvs).getObjVal? kv.1).toOption.map (kv.1, ·)) =
        kvs.toList := by
      have hs : ∀ kv ∈ kvs.toList, ((Json.obj kvs).getObjVal? kv.1).toOption.map (kv.1, ·) = some kv := by
        intro kv hkv
        have := (Std.TreeMap.Raw.mem_toList_iff_getElem?_eq_some h).mp hkv
        simp only [Json.getObjVal?, Std.TreeMap.Raw.get?_eq_getElem?, this, Except.toOption]
        rfl
      generalize kvs.toList = l at hs ⊢
      induction l with
      | nil => rfl
      | cons kv l ih =>
        rw [List.filterMap_cons, hs kv List.mem_cons_self, ih fun x hx => hs x (List.mem_cons_of_mem _ hx)]
    have hd : (kvs.toList.map (·.1)).Nodup := by
      refine List.pairwise_map.mpr ((Std.TreeMap.Raw.distinct_keys_toList h).imp fun hab heq => hab ?_)
      simp [heq]
    simp only [lookups, VE.Bridge.fields, Json.getObj?, bind, Except.bind, pure, Except.pure, hfm, firstKeys_self _ hd]
  | _ => simp [lookups, VE.Bridge.fields, Json.getObj?, bind, Except.bind]

/-! ## `govern` (sc-1ac, sc-1ad): the block's admission, the reaches, the refusals and the run path -/

section Govern
open VE.SoftNorms (SoftNode)
open VE.NormDefaults (ebind_ok forIn_unit_ok)

/-- The item's rule is the chain's own decoding of the joined object: scope decodes no rule field itself. -/
theorem itemRule_decoder (D : SDoc) (u : String) (lead item : Json) (N : SoftNode)
    (h : itemRule D u lead item = .ok N) :
    ∃ m, mergeParts u lead item = .ok m ∧ VE.Readings.Wire.decodeNorm D.re m = .ok N :=
  (ebind_ok _ _ _).mp h

/-- The block is admitted before anything else, with or without governors. -/
theorem govern_admits (D : SDoc) (out : Json) (ho : govern D = .ok out) : admitBlock D = .ok () := by
  unfold govern at ho
  cases h : admitBlock D with
  | error e => rw [h] at ho; cases ho
  | ok u => rfl

/-- Identity: without governors, an admitted block leaves the document exactly as written. -/
theorem govern_identity (D : SDoc) (h₀ : admitBlock D = .ok ()) (h : D.governors = []) (hp : partUnits D = []) :
    govern D = .ok D.doc := by
  simp [govern, h₀, h, hp, bind, Except.bind, pure, Except.pure]

/-- Without governors, once the block is admitted, a `part` content is refused. -/
theorem govern_orphan (D : SDoc) (h₀ : admitBlock D = .ok ()) (h : D.governors = []) (u : String)
    (hu : u ∈ partUnits D) : ∃ e, govern D = .error e ∧ e.startsWith "ScopeOrphanPart" = true := by
  cases hp : partUnits D with
  | nil => rw [hp] at hu; cases hu
  | cons v _ =>
    refine ⟨"ScopeOrphanPart: " ++ v, ?_, ?_⟩
    · simp [govern, h₀, h, hp, bind, Except.bind, throw, throwThe, MonadExceptOf.throw]; rfl
    · have := VE.Readings.startsWith_append_ascii "ScopeOrphanPart" (": " ++ v) (by decide)
      rwa [← String.append_assoc] at this

theorem coversU_iff (D : SDoc) (g : Governor) (u : String) :
    coversU D g u = true ↔ ∃ us, covered D g.reach = .ok us ∧ u ∈ us := by
  unfold coversU
  cases covered D g.reach <;> simp [Except.toOption]

theorem governorsOf_iff (D : SDoc) (u : String) (g : Governor) :
    g ∈ governorsOf D u ↔ g ∈ D.governors ∧ unary g.effect = true ∧ ∃ us, covered D g.reach = .ok us ∧ u ∈ us := by
  simp [governorsOf, ordered, List.mem_mergeSort, coversU_iff]

/-- Order 1.4: the governors are sorted by reach class, then by the position of their unit. -/
theorem ordered_sorted (D : SDoc) : (ordered D).Pairwise (fun g h => classOf g.reach < classOf h.reach ∨
    (classOf g.reach = classOf h.reach ∧ position D g.unit ≤ position D h.unit)) := by
  have := List.sorted_mergeSort (le := fun g h : Governor => classOf g.reach < classOf h.reach ||
      (classOf g.reach == classOf h.reach && position D g.unit ≤ position D h.unit))
    (fun a b c hab hbc => by simp only [Bool.or_eq_true, Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq] at *; omega)
    (fun a b => by simp only [Bool.or_eq_true, Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq]; omega) D.governors
  simpa [ordered] using this

theorem mem_ordered (D : SDoc) (g : Governor) : g ∈ ordered D ↔ g ∈ D.governors := List.mem_mergeSort

/-- A rule unit's base name is the name the chain's decoder reads from its base object. -/
theorem baseName_some (D : SDoc) (u n : String) : baseName D u = some n ↔
    ∃ o N, baseObj D u = .ok o ∧ VE.Readings.Wire.decodeNorm D.re o = .ok N ∧ N.name = n := by
  unfold baseName
  cases baseObj D u with
  | error => simp [Except.toOption]
  | ok o => cases h : VE.Readings.Wire.decodeNorm D.re o <;> simp [Except.toOption, h]

/-! The graph step -/

theorem mapM_ok_mem {α β ε : Type} (f : α → Except ε β) :
    ∀ (l : List α) (t : List β), l.mapM f = .ok t → ∀ y ∈ t, ∃ x ∈ l, f x = .ok y
  | [], t, h => by cases h; simp
  | x :: l, t, h => by
    rw [List.mapM_cons] at h
    obtain ⟨b, hb, h⟩ := (ebind_ok _ _ _).mp h
    obtain ⟨bs, hbs, h⟩ := (ebind_ok _ _ _).mp h
    cases h
    intro y hy
    rcases List.mem_cons.mp hy with rfl | hy
    · exact ⟨x, List.mem_cons_self, hb⟩
    · obtain ⟨z, hz, hfz⟩ := mapM_ok_mem f l bs hbs y hy
      exact ⟨z, List.mem_cons_of_mem _ hz, hfz⟩

/-- Each rule the graph step reads is the chain's own decoding of the unit's composed object. -/
theorem ruleTable_decoder (D : SDoc) (t : List (String × SoftNode)) (h : ruleTable D = .ok t) (u : String)
    (N : SoftNode) (hu : (u, N) ∈ t) : ∃ o, composed D u = .ok o ∧ VE.Readings.Wire.decodeNorm D.re o = .ok N := by
  obtain ⟨v, -, hv⟩ := mapM_ok_mem _ _ t h (u, N) hu
  obtain ⟨o, ho, hv⟩ := (ebind_ok _ _ _).mp hv
  obtain ⟨M, hM, hv⟩ := (ebind_ok _ _ _).mp hv
  cases hv
  exact ⟨o, ho, hM⟩

theorem edgesFor_ok (D : SDoc) (u : String) (es : List String) :
    edgesFor D u = .ok es ↔ ∃ t, ruleTable D = .ok t ∧ edgesInto D (fun v => t.lookup v) u = es := by
  unfold edgesFor
  rw [ebind_ok]
  simp [pure, Except.pure]

/-- Only a graph governor adds an edge. -/
theorem edgesOf_graph (D : SDoc) (rule : String → Option SoftNode) (g : Governor) (h : edgesOf D rule g ≠ []) :
    graph g.effect = true := by
  unfold edgesOf at h
  split at h
  · exact absurd rfl h
  · revert h; cases g.effect <;> simp [graph]

/-- An edge into a unit comes from a graph governor of the document. -/
theorem edgesInto_mem (D : SDoc) (rule : String → Option SoftNode) (u n : String) (h : n ∈ edgesInto D rule u) :
    ∃ g ∈ D.governors, graph g.effect = true ∧ (u, n) ∈ edgesOf D rule g := by
  simp only [edgesInto, List.mem_filterMap, List.mem_flatMap, List.mem_filter, mem_ordered] at h
  obtain ⟨⟨w, m⟩, ⟨g, ⟨hg, hgr⟩, hm⟩, he⟩ := h
  by_cases hw : (w == u) = true
  · simp only [hw, if_true, Option.some.injEq] at he
    subst he
    exact ⟨g, hg, hgr, by rw [← eq_of_beq hw]; exact hm⟩
  · simp [hw] at he

/-- Nothing to add leaves the rule as composed. -/
theorem addOver_nil (o : Json) : addOver [] o = o := by
  unfold addOver
  split <;> simp

-- the step-8 match on the reach (sc-3ab) doubles the cases the loop body's side goal splits
set_option maxHeartbeats 400000 in
/-- What an admitted block says of each governor (step 8): no graph effect over a frontier reach, and its reach
    exists, holds no unit of a reading set (nor does its own unit), and, for a content-changing effect, holds only
    units that are unwritten, parts or norms. -/
theorem admit_governor (D : SDoc) (h : admitBlock D = .ok ()) (g : Governor) (hg : g ∈ D.governors) :
    ¬ (g.reach = .frontier ∧ graph g.effect = true) ∧
    ∃ us, covered D g.reach = .ok us ∧ (∀ u ∈ g.unit :: us, (setUnits D.doc).contains u = false) ∧
      ((isFrame g.effect || unary g.effect) = true → ∀ u ∈ us,
        ((contentOf D.doc u).isNull || isPart (contentOf D.doc u) || isNorm (contentOf D.doc u)) = true) := by
  unfold admitBlock at h
  -- the two loops over the governors (steps 5 and 8) are set aside, so that each split reads a small term
  generalize hA : (forIn D.governors PUnit.unit _ : Except String PUnit) = A at h
  generalize hB : (forIn D.governors PUnit.unit _ : Except String PUnit) = B at h
  simp only [bind, Except.bind, pure, Except.pure] at h
  repeat (split at h; · cases h)
  have hb := (forIn_unit_ok _ ?_ D.governors).mp hB g hg
  · clear hA hB h
    simp only [bind, Except.bind, pure, Except.pure] at hb
    split at hb
    · cases hb
    revert hb
    cases g.effect <;> cases g.reach <;> intro hb <;> simp only at hb
    all_goals (try (cases hb; done))
    all_goals (try (split at hb; case isFalse => cases hb))
    all_goals refine ⟨by simp [graph], ?_⟩
    all_goals (split at hb; · cases hb)
    all_goals rename_i us hcov
    all_goals (split at hb; case isFalse => cases hb)
    all_goals (split at hb; · cases hb)
    all_goals rename_i hrs
    all_goals refine ⟨us, hcov, fun u hu => ?_, fun hfu u hu => ?_⟩
    all_goals first
      | (have hx := (forIn_unit_ok _ ?_ _).mp hrs u hu
         · simp only at hx
           split at hx
           · cases hx
           · rename_i hnc; simpa using hnc
         · intro x r hx; split at hx
           · cases hx
           · injection hx with hx; exact hx.symm)
      | (split at hb
         · split at hb
           · cases hb
           rename_i hnr
           have hx := (forIn_unit_ok _ ?_ _).mp hnr u hu
           · simp only at hx
             split at hx
             · assumption
             · cases hx
           · intro x r hx; split at hx
             · injection hx with hx; exact hx.symm
             · cases hx
         · exact absurd hfu ‹_›)
  · intro x r hx
    simp only [bind, Except.bind, pure, Except.pure] at hx
    repeat' split at hx
    all_goals (try (cases hx; done))
    all_goals (try (injection hx with hx; exact hx.symm))
    all_goals (try rfl)

theorem govern_refused (D : SDoc) (hn : admitBlock D ≠ .ok ()) : (govern D).isOk = false := by
  cases ho : govern D with
  | error => rfl
  | ok out => exact absurd (govern_admits D out ho) hn

/-- A frontier reach carries a unary effect only (until SC-5's addendum): a graph governor on it is refused. -/
theorem frontier_graph_refused (D : SDoc) (g : Governor) (hg : g ∈ D.governors) (hf : g.reach = .frontier)
    (he : graph g.effect = true) : (govern D).isOk = false :=
  govern_refused D fun h => (admit_governor D h g hg).1 ⟨hf, he⟩

/-- A governor or a governed unit that a reading set owns is refused. -/
theorem readings_refused (D : SDoc) (g : Governor) (hg : g ∈ D.governors) (us : List String)
    (hc : covered D g.reach = .ok us) (u : String) (hu : u = g.unit ∨ u ∈ us) (hs : u ∈ setUnits D.doc) :
    (govern D).isOk = false := by
  refine govern_refused D fun h => ?_
  obtain ⟨vs, hv, hr, _⟩ := (admit_governor D h g hg).2
  rw [hc] at hv; cases hv
  have := hr u (by rcases hu with rfl | hu <;> simp_all)
  simp_all

/-- A content-changing governor never covers a unit whose content it cannot change: such a unit is refused, never
    skipped (an unwritten unit, `null`, stays pending and makes the governor UNFORMALISED). -/
theorem nonrule_refused (D : SDoc) (g : Governor) (hg : g ∈ D.governors) (he : isFrame g.effect || unary g.effect)
    (us : List String) (hc : covered D g.reach = .ok us) (u : String) (hu : u ∈ us)
    (hn : contentOf D.doc u ≠ .null) (hr : isPart (contentOf D.doc u) = false) (hm : isNorm (contentOf D.doc u) = false) :
    (govern D).isOk = false := by
  refine govern_refused D fun h => ?_
  obtain ⟨vs, hv, _, hnr⟩ := (admit_governor D h g hg).2
  rw [hc] at hv; cases hv
  have := hnr he u hu
  generalize contentOf D.doc u = c at this hn hr hm
  cases c <;> simp_all [Json.isNull]

/-! The run path (1.5.8) -/

/-- The run path's tables are keyed by reach: two reaches are the same key exactly when they are equal. -/
theorem reach_beq (r s : Reach) : (r == s) = true ↔ r = s := beq_iff_eq

/-- A table of `f`'s own values reads as `f`. -/
theorem memo_map {α β γ : Type} [BEq α] [LawfulBEq α] (ys : List γ) (k : γ → α) (f : α → β) :
    memo (ys.map fun y => (k y, f (k y))) f = f := by
  funext x
  unfold memo
  split
  · rename_i v hv
    induction ys with
    | nil => cases hv
    | cons y ys ih =>
      simp only [List.map_cons, List.lookup] at hv
      split at hv
      · rename_i hx; cases hv; rw [eq_of_beq hx]
      · exact ih hv
  · rfl

/-- Each step of the run path, read with `govern`'s own reaches, is `govern`'s step. -/
theorem frameOnF_slow (D : SDoc) : frameOnF D (fun r => (coveredLayout D r).toOption.getD []) = frameOn D := rfl
theorem baseObjF_slow (D : SDoc) : baseObjF D (fun r => (coveredLayout D r).toOption.getD []) = baseObj D := rfl
theorem coveredBy_slow (D : SDoc) : coveredBy D (baseName D) = covered D := by funext r; cases r <;> rfl
theorem governorsOfF_slow (D : SDoc) :
    governorsOfF (ordered D) (fun r => (covered D r).toOption.getD []) = governorsOf D := rfl
theorem composedF_slow (D : SDoc) : composedF D (fun r => (coveredLayout D r).toOption.getD []) (ordered D)
    (fun r => (covered D r).toOption.getD []) = composed D := rfl
theorem edgesOfF_slow (D : SDoc) (rule : String → Option SoftNode) :
    edgesOfF (fun r => (covered D r).toOption.getD []) rule = edgesOf D rule := rfl
theorem governBody_slow (D : SDoc) : govern D = (admitBlock D >>= fun _ => governBody D (ordered D)
    (fun r => (coveredLayout D r).toOption.getD []) (fun r => (covered D r).toOption.getD [])) := rfl

theorem fastReads_eq (D : SDoc) : fastReads D =
    (fun r => (coveredLayout D r).toOption.getD [], fun r => (covered D r).toOption.getD []) := by
  have hb := coveredBy_slow D
  have hn : memo ((ruleUnits D).map fun u => (u, ((baseObjF D (fun r => (coveredLayout D r).toOption.getD []) u).toOption.bind
      fun o => (VE.Readings.Wire.decodeNorm D.re o).toOption).map (·.name))) (baseName D) = baseName D :=
    memo_map (ruleUnits D) id (baseName D)
  unfold fastReads
  simp only [memo_map D.governors (·.reach) (fun r => (coveredLayout D r).toOption.getD []), hn, hb,
    memo_map D.governors (·.reach) (fun r => (covered D r).toOption.getD [])]

/-- The run path (1.5.8) answers exactly as `govern`, so every theorem about `govern` holds of it. -/
theorem governFast_eq (D : SDoc) : governFast D = govern D := by
  unfold governFast
  rw [fastReads_eq, governBody_slow]

/-! Headings and labels (spec 5.5, SC-3a): the anchor and label reaches are the layout's -/

/-- A heading's reach is the anchor's units after its heading. -/
theorem anchor_reach_iff (D : SDoc) (hd : (D.layout.map (·.id)).Nodup) (a : String) (us : List String)
    (hc : covered D (.anchor a) = .ok us) (u : String) :
    u ∈ us ↔ u ∈ D.layout.map (·.id) ∧ VE.Layout.within (VE.Layout.spansOf D.layout) D.anchors u a = true ∧
      some u ≠ VE.Layout.headingOf D.layout D.anchors a :=
  VE.Layout.anchorReach_iff D.layout hd D.anchors a us hc u

/-- A bold label's reach is its item: the item, its continuing sentences and its sub-bullets. -/
theorem label_reach_iff (D : SDoc) (hd : (D.layout.map (·.id)).Nodup) (i : String) (us : List String)
    (hc : covered D (.label i) = .ok us) (u : String) : u ∈ us ↔ VE.Layout.ItemUnit D.layout i u :=
  VE.Layout.itemRun_iff D.layout hd i us hc u

end Govern

end VE.Scope
