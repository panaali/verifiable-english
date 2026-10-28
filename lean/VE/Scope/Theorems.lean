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

/-! ## Spec 5.1's statements on a well-formed document (sc-1ae, the DRI's fix (a) of 2026-10-27)

    `decodeNorm_name`, `govern_strings`, `govern_no_new_symbols` and `govern_preserves` take `JsonWF` of the document
    (and of the decoded rule): `setObjVal!` and the soft chain's `toList` read a tree no parser builds otherwise
    (F-raw, `Examples.lean`). Each lemma below needs only the top level of the object it writes to be well formed. -/

section Statements
open VE.SoftNorms (SoftNode)
open VE.NormDefaults (ebind_ok)

theorem getObjVal_obj (kvs : Std.TreeMap.Raw String Json) (k : String) (x : Json) :
    (Json.obj kvs).getObjVal? k = .ok x ↔ kvs[k]? = some x := by
  simp only [Json.getObjVal?, Std.TreeMap.Raw.get?_eq_getElem?]
  split <;> simp_all [pure, Except.pure, throw, throwThe, MonadExceptOf.throw]

theorem setObjVal_get (kvs : Std.TreeMap.Raw String Json) (hw : kvs.WF) (k k' : String) (v x : Json) :
    ((Json.obj kvs).setObjVal! k v).getObjVal? k' = .ok x ↔
      (k = k' ∧ x = v) ∨ (k ≠ k' ∧ (Json.obj kvs).getObjVal? k' = .ok x) := by
  simp only [Json.setObjVal!, getObjVal_obj, Std.TreeMap.Raw.getElem?_insert hw, Std.LawfulEqCmp.compare_eq_iff_eq]
  by_cases h : k = k' <;> simp [h, eq_comm]

theorem hasStr_null (s : String) : ¬ HasStr s .null := by
  intro h; cases h with | obj hk _ => simp [Json.getObjVal?, throw, throwThe, MonadExceptOf.throw] at hk

theorem hasStr_setObj (s : String) (kvs : Std.TreeMap.Raw String Json) (hw : kvs.WF) (k : String) (v : Json)
    (h : HasStr s ((Json.obj kvs).setObjVal! k v)) : HasStr s (.obj kvs) ∨ HasStr s v := by
  cases h with
  | obj hk hx =>
    rcases (setObjVal_get kvs hw _ _ _ _).mp hk with ⟨_, rfl⟩ | ⟨_, hk'⟩
    · exact .inr hx
    · exact .inl (.obj hk' hx)

theorem members_get (kvs : Std.TreeMap.Raw String Json) (hw : kvs.WF) (k : String) (x : Json)
    (h : (k, x) ∈ members (.obj kvs)) : (Json.obj kvs).getObjVal? k = .ok x := by
  rw [members_obj, Std.TreeMap.Raw.mem_toList_iff_getElem?_eq_some hw] at h
  exact (getObjVal_obj kvs k x).mpr h

theorem members_nodup (kvs : Std.TreeMap.Raw String Json) (hw : kvs.WF) :
    ((members (.obj kvs)).map (·.1)).Nodup := by
  rw [members_obj, List.nodup_iff_pairwise_ne, List.pairwise_map]  
  exact (Std.TreeMap.Raw.distinct_keys_toList hw).imp fun h e => h (by simp [e])

theorem impl_get_map (f : String → Json → Json) (k : String) : ∀ (t : Impl String (fun _ => Json)),
    Impl.Const.get? (t.map f) k = (Impl.Const.get? t k).map (f k)
  | .leaf => rfl
  | .inner _ k' v l r => by
    have hl := impl_get_map f k l
    have hr := impl_get_map f k r
    simp only [Impl.map, Impl.Const.get?]
    cases h : compare k k' <;> simp only [hl, hr, Option.map_some]
    rw [Std.LawfulEqCmp.eq_of_compare h]

theorem getObjVal_map (f : String → Json → Json) (kvs : Std.TreeMap.Raw String Json) (k : String) (x : Json)
    (h : (Json.obj (kvs.map f)).getObjVal? k = .ok x) : ∃ y, (Json.obj kvs).getObjVal? k = .ok y ∧ x = f k y := by
  rw [getObjVal_obj] at h
  have hm : (kvs.map f)[k]? = kvs[k]?.map (f k) := impl_get_map f k kvs.inner.inner
  rw [hm] at h
  obtain ⟨y, hy, rfl⟩ := Option.map_eq_some_iff.mp h
  exact ⟨y, (getObjVal_obj kvs k y).mpr hy, rfl⟩


theorem normFields_name (j : Json) (r : String × String × Bool × Json × List Json × List String)
    (h : VE.Norms.Wire.normFields j = .ok r) : (j.getObjValD "norm").getObjValD "name" = .str r.1 := by
  unfold VE.Norms.Wire.normFields at h
  obtain ⟨_, -, h⟩ := (ebind_ok _ _ _).mp h
  obtain ⟨raw, hr, h⟩ := (ebind_ok _ _ _).mp h
  obtain ⟨_, -, h⟩ := (ebind_ok _ _ _).mp h
  have hj : j.getObjValD "norm" = raw := by simp [Json.getObjValD, hr, Except.toOption]
  rw [hj]
  cases hn : raw.getObjValD "name" with
  | str s =>
    simp only [hn] at h
    cases hp : VE.Bridge.stringField raw "predicate" <;> simp only [hp, bind, Except.bind, pure, Except.pure] at h
    · cases h
    split at h <;> try simp only [bind, Except.bind, pure, Except.pure, throw, throwThe, MonadExceptOf.throw] at h
    · split at h <;> try simp only [bind, Except.bind, pure, Except.pure, throw, throwThe, MonadExceptOf.throw] at h
      · split at h <;> try simp only [bind, Except.bind, pure, Except.pure, throw, throwThe, MonadExceptOf.throw] at h
        · revert h; cases VE.Bridge.strings (raw.getObjValD "over") <;> intro h
          · cases h
          · cases h; rfl
        · cases h
      · cases h
    · cases h
  | _ => simp [hn, bind, Except.bind] at h

theorem w1_name (j : Json) (sh : Bool) (N : VE.Norms.Node) (h : VE.Norms.Wire.decodeNorm j sh = .ok N) :
    (j.getObjValD "norm").getObjValD "name" = .str N.name := by
  unfold VE.Norms.Wire.decodeNorm at h
  obtain ⟨r, hf, h⟩ := (ebind_ok _ _ _).mp h
  rw [normFields_name j r hf]
  obtain ⟨_, -, h⟩ := (ebind_ok _ _ _).mp h
  obtain ⟨_, -, h⟩ := (ebind_ok _ _ _).mp h
  cases h; rfl

theorem ite_bind_ok {ε α β : Type} {c : Prop} [Decidable c] (a b : Except ε α) (k : α → Except ε β) (r : β)
    (h : (if c then a >>= k else b >>= k) = .ok r) : ∃ u, k u = .ok r := by
  split at h <;> obtain ⟨u, -, h⟩ := (ebind_ok _ _ _).mp h <;> exact ⟨u, h⟩

theorem ruleFields_name (x : Option String) (j : Json) (R : SoftNode) (h : VE.SoftNorms.Phases.ruleFields x j = .ok R) :
    ∃ obj N, VE.Bridge.fields (j.getObjValD "norm") = .ok obj ∧
      VE.Norms.Wire.decodeNorm (Json.mkObj [("norm", Json.mkObj (obj.filter
        (fun kv => VE.SoftNorms.Phases.w1Keys.contains kv.1)))]) false = .ok N ∧ R.name = N.name := by
  unfold VE.SoftNorms.Phases.ruleFields at h
  extract_lets raw seen given k₁ at h
  split at h
  · obtain ⟨_, -, h⟩ := (ebind_ok _ _ _).mp h
    simp -zeta only [k₁] at h
    obtain ⟨obj, ho, h⟩ := (ebind_ok _ _ _).mp h
    extract_lets keys k₂ at h
    split at h
    · obtain ⟨_, -, h⟩ := (ebind_ok _ _ _).mp h
      simp -zeta only [k₂] at h
      obtain ⟨N, hN, h⟩ := (ebind_ok _ _ _).mp h
      simp only [VE.SoftNorms.Phases.inherited] at ho hN
      split at ho <;> cases ho
      split at hN <;> cases hN
      refine ⟨obj, N, by assumption, by assumption, ?_⟩
      extract_lets bad j₁ j₂ j₃ at h
      obtain ⟨_, h⟩ := ite_bind_ok _ _ _ _ h
      simp -zeta only [j₃] at h
      obtain ⟨_, h⟩ := ite_bind_ok _ _ _ _ h
      simp -zeta only [j₂] at h
      obtain ⟨_, -, h⟩ := (ebind_ok _ _ _).mp h
      obtain ⟨_, h⟩ : ∃ y, j₁ y = .ok R := by
        split at h <;> obtain ⟨u, -, h⟩ := (ebind_ok _ _ _).mp h <;> exact ⟨u, h⟩
      simp -zeta only [j₁] at h
      extract_lets jr at h
      obtain ⟨_, h⟩ : ∃ y, jr y = .ok R := by
        split at h <;> obtain ⟨u, -, h⟩ := (ebind_ok _ _ _).mp h <;> exact ⟨u, h⟩
      simp -zeta only [jr] at h
      extract_lets ja at h
      obtain ⟨_, h⟩ : ∃ y, ja y = .ok R := by
        split at h <;> (try split at h) <;> obtain ⟨u, -, h⟩ := (ebind_ok _ _ _).mp h <;> exact ⟨u, h⟩
      simp -zeta only [ja] at h
      extract_lets jh jb at h
      obtain ⟨_, h⟩ := ite_bind_ok _ _ _ _ h
      simp -zeta only [jb] at h
      obtain ⟨_, h⟩ : ∃ y, jh y = .ok R := by
        split at h <;> obtain ⟨u, -, h⟩ := (ebind_ok _ _ _).mp h <;> exact ⟨u, h⟩
      simp -zeta only [jh] at h
      extract_lets je jc at h
      obtain ⟨_, h⟩ := ite_bind_ok _ _ _ _ h
      simp -zeta only [jc] at h
      clear_value given
      obtain ⟨_, h⟩ : ∃ y, je y = .ok R := by
        split at h <;> obtain ⟨u, -, h⟩ := (ebind_ok _ _ _).mp h <;> exact ⟨u, h⟩
      simp -zeta only [je] at h
      cases h; rfl
    · obtain ⟨_, h', -⟩ := (ebind_ok _ _ _).mp h; cases h'
  · obtain ⟨_, h', -⟩ := (ebind_ok _ _ _).mp h; cases h'

theorem getObjValD_str (o : Json) (k n : String) (h : o.getObjValD k = .str n) : o.getObjVal? k = .ok (.str n) := by
  unfold Json.getObjValD at h
  cases hk : o.getObjVal? k <;> simp_all [Except.toOption]

theorem mkObj_one (k : String) (o : Json) : (Json.mkObj [(k, o)]).getObjValD k = o := by
  simp [Json.getObjValD, (mkObj_getObjVal [(k, o)] (by simp) k o).mpr (by simp), Except.toOption]

/-- `decodeNorm_name` on an object whose top level is a well-formed tree. -/
theorem decodeNorm_name_top (re : VE.Readings.Wire.ReadingsEnvironment) (o : Json)
    (hw : ∀ kvs, o = .obj kvs → kvs.WF) (N : SoftNode) (h : VE.Readings.Wire.decodeNorm re o = .ok N) :
    HasStr N.name o := by
  unfold VE.Readings.Wire.decodeNorm at h
  split at h
  · obtain ⟨M, hM, h⟩ := (ebind_ok _ _ _).mp h
    cases h
    have := w1_name _ _ _ hM
    rw [mkObj_one] at this
    exact .obj (getObjValD_str _ _ _ this) .str
  · unfold VE.SoftNorms.Wire.decodeSoftNorm at h
    split at h
    · next _ R hR =>
      cases h
      obtain ⟨R', hR', h⟩ := (ebind_ok _ _ _).mp hR
      have hRR : R' = N := by
        revert h; cases VE.SoftNorms.Phases.ruleReferences _ _ R' <;> simp [Except.map]
      subst hRR
      obtain ⟨obj, M, hf, hM, hn⟩ := ruleFields_name _ _ _ hR'
      rw [mkObj_one] at hf
      cases o with
      | obj kvs =>
        simp only [VE.Bridge.fields, Json.getObj?, bind, Except.bind, pure, Except.pure, Except.ok.injEq] at hf
        subst hf
        have hm := getObjValD_str _ _ _ (w1_name _ _ _ hM)
        rw [mkObj_one, mkObj_getObjVal _ (by
          have := members_nodup kvs (hw kvs rfl)
          rw [members_obj] at this
          exact (List.Nodup.sublist (List.Sublist.map _ List.filter_sublist) this))] at hm
        rw [hn]
        exact .obj (members_get kvs (hw kvs rfl) _ _ (by rw [members_obj]; exact (List.mem_filter.mp hm).1)) .str
      | _ => simp [VE.Bridge.fields, Json.getObj?, bind, Except.bind, throw, throwThe, MonadExceptOf.throw] at hf
    · cases h

theorem jsonWF_top (o : Json) (hw : JsonWF o) : ∀ kvs, o = .obj kvs → kvs.WF := by
  intro kvs he; subst he; cases hw; assumption

/-- The chain's decoder reads a rule's name from the object as written (the names `addOver` writes). -/
theorem decodeNorm_name (re : VE.Readings.Wire.ReadingsEnvironment) (o : Json) (hw : JsonWF o) (N : SoftNode)
    (h : VE.Readings.Wire.decodeNorm re o = .ok N) : HasStr N.name o :=
  decodeNorm_name_top re o (jsonWF_top o hw) N h

/-! JSON lemmas for the statements of 5.1 -/

theorem mkObj_get_mem (l : List (String × Json)) (k : String) (x : Json) (h : (Json.mkObj l).getObjVal? k = .ok x) :
    ∃ p ∈ l, p.2 = x := by
  simp only [Json.mkObj, getObjVal_obj, Std.TreeMap.Raw.ofList_eq_insertMany_empty] at h
  rw [Std.TreeMap.Raw.getElem?_insertMany_list Std.TreeMap.Raw.WF.emptyc, Std.TreeMap.Raw.getElem?_emptyc] at h
  rw [List.findSomeRev?_eq_findSome?_reverse, Option.or_none] at h
  obtain ⟨⟨a, b⟩, hm, hy⟩ := List.exists_of_findSome?_eq_some h
  by_cases hc : compare a k = .eq <;> simp only [hc, if_true, if_false, reduceCtorEq] at hy
  exact ⟨(a, b), List.mem_reverse.mp hm, Option.some.inj hy⟩

theorem hasStr_mkObj (s : String) (l : List (String × Json)) (h : HasStr s (Json.mkObj l)) : ∃ p ∈ l, HasStr s p.2 := by
  cases h with
  | obj hk hx => obtain ⟨p, hp, rfl⟩ := mkObj_get_mem l _ _ hk; exact ⟨p, hp, hx⟩

theorem setObjVal_null (o : Json) (h : ∀ kvs, o ≠ .obj kvs) (k : String) (v : Json) : o.setObjVal! k v = .null := by
  cases o <;> first | rfl | exact absurd rfl (h _)

theorem top_set (o : Json) (hw : ∀ kvs, o = .obj kvs → kvs.WF) (k : String) (v : Json) :
    ∀ kvs, o.setObjVal! k v = .obj kvs → kvs.WF := by
  cases o with
  | obj t => intro kvs he; cases he; exact (hw t rfl).insert
  | _ => intro kvs he; rw [setObjVal_null _ (by simp)] at he; cases he

theorem hasStr_set (s : String) (o : Json) (hw : ∀ kvs, o = .obj kvs → kvs.WF) (k : String) (v : Json)
    (h : HasStr s (o.setObjVal! k v)) : HasStr s o ∨ HasStr s v := by
  cases o with
  | obj t => exact hasStr_setObj s t (hw t rfl) k v h
  | _ => rw [setObjVal_null _ (by simp)] at h; exact absurd h (hasStr_null s)

theorem hasStr_getD (s : String) (j : Json) (k : String) (h : HasStr s (j.getObjValD k)) : HasStr s j := by
  unfold Json.getObjValD at h
  cases hk : j.getObjVal? k with
  | error => rw [hk] at h; exact absurd h (hasStr_null s)
  | ok x => rw [hk] at h; exact .obj hk h

theorem jsonWF_getD (j : Json) (hw : JsonWF j) (k : String) : JsonWF (j.getObjValD k) := by
  unfold Json.getObjValD
  cases hk : j.getObjVal? k with
  | error => exact .null
  | ok x =>
    cases hw with
    | obj kvs hw hall =>
      exact hall (k, x) ((Std.TreeMap.Raw.mem_toList_iff_getElem?_eq_some hw).mpr ((getObjVal_obj kvs k x).mp hk))
    | _ => simp [Json.getObjVal?, throw, throwThe, MonadExceptOf.throw] at hk

theorem unitsOf_mem (doc x : Json) (hx : x ∈ unitsOf doc) :
    (∀ s, HasStr s x → HasStr s doc) ∧ (JsonWF doc → JsonWF x) := by
  unfold unitsOf at hx
  split at hx
  · next xs he =>
    have hm := Array.mem_toList_iff.mp hx
    refine ⟨fun s h => hasStr_getD s doc "units" (he ▸ .arr hm h), fun hw => ?_⟩
    have := jsonWF_getD doc hw "units"
    rw [he] at this
    cases this with | arr _ hall => exact hall x hm
  · cases hx

theorem contentOf_src (doc : Json) (u : String) :
    (∀ s, HasStr s (contentOf doc u) → HasStr s doc) ∧ (JsonWF doc → JsonWF (contentOf doc u)) := by
  unfold contentOf
  cases hf : (unitsOf doc).find? (idOf · == u) with
  | none => exact ⟨fun s h => absurd h (hasStr_null s), fun _ => .null⟩
  | some x =>
    have := unitsOf_mem doc x (List.mem_of_find?_eq_some hf)
    exact ⟨fun s h => this.1 s (hasStr_getD s x "content" h), fun hw => jsonWF_getD x (this.2 hw) "content"⟩

theorem hasStr_substOwn (g : Json) (s : String) : ∀ (n : Nat) (c : Json), HasStr s (substOwn g n c) →
    HasStr s g ∨ HasStr s c
  | 0, c, h => .inr h
  | n + 1, c, h => by
    cases c with
    | str t =>
      simp only [substOwn] at h
      split at h
      · exact .inl h
      · exact .inr h
    | arr xs =>
      simp only [substOwn] at h
      cases h with
      | arr hm hx =>
        obtain ⟨y, hy, rfl⟩ := Array.mem_map.mp hm
        rcases hasStr_substOwn g s n y hx with h | h
        · exact .inl h
        · exact .inr (.arr hy h)
      | obj hk _ => simp [Json.getObjVal?, throw, throwThe, MonadExceptOf.throw] at hk
    | obj kvs =>
      simp only [substOwn] at h
      cases h with
      | obj hk hx =>
        obtain ⟨y, hy, rfl⟩ := getObjVal_map _ kvs _ _ hk
        rcases hasStr_substOwn g s n y hx with h | h
        · exact .inl h
        · exact .inr (.obj hy h)
    | _ => exact .inr h

theorem hasStr_inv (s : String) (kvs : Std.TreeMap.Raw String Json) (h : HasStr s (.obj kvs)) :
    ∃ k x, (Json.obj kvs).getObjVal? k = .ok x ∧ HasStr s x := by
  cases h with | obj hk hx => exact ⟨_, _, hk, hx⟩

theorem mergeParts_mk (u : String) (lead item out : Json) (h : mergeParts u lead item = .ok out) :
    ∃ l, out = Json.mkObj l := by
  unfold mergeParts at h
  cases hl : lookups lead <;> cases hi : lookups item <;>
    simp [hl, hi, Except.mapError, bind, Except.bind] at h
  split at h
  · cases h
  · cases h; exact ⟨_, rfl⟩

theorem mergeParts_src (u : String) (lead item out : Json) (h : mergeParts u lead item = .ok out) :
    (∀ kvs, out = .obj kvs → kvs.WF) ∧ ∀ s, HasStr s out → HasStr s lead ∨ HasStr s item := by
  obtain ⟨l, rfl⟩ := mergeParts_mk u lead item out h
  refine ⟨fun kvs he => by cases he; exact Std.TreeMap.Raw.WF.ofList, fun s hs => ?_⟩
  obtain ⟨k, x, hk, hx⟩ := hasStr_inv s _ hs
  rcases (mergeParts_keys u lead item _ h k x).mp hk with ⟨hk, _⟩ | ⟨hk, _⟩
  · exact .inl (.obj hk hx)
  · exact .inr (.obj hk hx)

theorem baseObj_src (D : SDoc) (hw : JsonWF D.doc) (u : String) (o : Json) (h : baseObj D u = .ok o) :
    (∀ kvs, o = .obj kvs → kvs.WF) ∧
      ∀ s, HasStr s o → HasStr s D.doc ∨ ∃ g ∈ D.governors, HasStr s (payload g.effect) := by
  have hc := contentOf_src D.doc u
  have ho : (∀ kvs, objectOf (contentOf D.doc u) = .obj kvs → kvs.WF) ∧
      ∀ s, HasStr s (objectOf (contentOf D.doc u)) → HasStr s D.doc := by
    unfold objectOf
    split
    all_goals exact ⟨jsonWF_top _ (jsonWF_getD _ (hc.2 hw) _), fun s h => hc.1 s (hasStr_getD _ _ _ h)⟩
  unfold baseObj at h
  dsimp only at h
  by_cases h1 : (!(isPart (contentOf D.doc u) || isNorm (contentOf D.doc u))) = true
  · simp only [h1, if_true] at h; cases h
  simp only [h1, if_false, Bool.false_eq_true] at h
  cases hf : frameOn D u with
  | nil =>
    by_cases hp : isPart (contentOf D.doc u) = true <;> simp only [hf, hp, if_true, if_false,
      Bool.false_eq_true] at h <;> cases h
    exact ⟨ho.1, fun s h => .inl (ho.2 s h)⟩
  | cons g gs =>
    have hgD : g ∈ D.governors := (List.mem_filter.mp (hf ▸ List.mem_cons_self : g ∈ frameOn D u)).1
    cases gs with
    | cons => simp only [hf] at h; cases h
    | nil =>
      simp only [hf] at h
      cases he : g.effect with
      | frame lead =>
        rw [he] at h
        obtain ⟨htop, hs⟩ := mergeParts_src _ _ _ _ h
        refine ⟨htop, fun s h => ?_⟩
        rcases hs s h with h | h
        · exact .inr ⟨g, hgD, by rw [he]; exact h⟩
        · exact .inl (ho.2 s h)
      | _ => rw [he] at h; cases h; exact ⟨ho.1, fun s h => .inl (ho.2 s h)⟩

theorem applyEffect_src (u : String) (e : Effect) (o o' : Json) (h : applyEffect u e o = .ok o')
    (hw : ∀ kvs, o = .obj kvs → kvs.WF) :
    (∀ kvs, o' = .obj kvs → kvs.WF) ∧ ∀ s, HasStr s o' → HasStr s o ∨ HasStr s (payload e) := by
  unfold applyEffect at h
  split at h
  · split at h
    · next g hg =>
      cases h
      refine ⟨top_set o hw _ _, fun s hs => ?_⟩
      rcases hasStr_set s o hw _ _ hs with h | h
      · exact .inl h
      · rcases hasStr_substOwn g s _ _ h with h | h
        · exact .inl (.obj hg h)
        · exact .inr h
    · cases h
  · split at h
    · next xs _ hu =>
      cases h
      refine ⟨top_set o hw _ _, fun s hs => ?_⟩
      rcases hasStr_set s o hw _ _ hs with h | h
      · exact .inl h
      · cases h with
        | arr hm hx =>
          rcases Array.mem_push.mp hm with hm | rfl
          · exact .inl (.obj hu (.arr hm hx))
          · rcases hasStr_substOwn _ s _ _ hx with h | h
            · exact .inl (.obj ‹_› h)
            · exact .inr h
        | obj hk _ => simp [Json.getObjVal?, throw, throwThe, MonadExceptOf.throw] at hk
    · cases h
  · cases h; exact ⟨hw, fun s h => .inl h⟩

theorem fold_src (u : String) : ∀ (gs : List Governor) (o o' : Json),
    gs.foldlM (fun o g => applyEffect u g.effect o) o = .ok o' → (∀ kvs, o = .obj kvs → kvs.WF) →
    (∀ kvs, o' = .obj kvs → kvs.WF) ∧ ∀ s, HasStr s o' → HasStr s o ∨ ∃ g ∈ gs, HasStr s (payload g.effect)
  | [], o, o', h, hw => by cases h; exact ⟨hw, fun s h => .inl h⟩
  | g :: gs, o, o', h, hw => by
    rw [List.foldlM_cons] at h
    obtain ⟨o₁, h₁, h⟩ := (ebind_ok _ _ _).mp h
    obtain ⟨hw₁, hs₁⟩ := applyEffect_src u g.effect o o₁ h₁ hw
    obtain ⟨hw', hs'⟩ := fold_src u gs o₁ o' h hw₁
    refine ⟨hw', fun s hs => ?_⟩
    rcases hs' s hs with h | ⟨g', hg', h⟩
    · rcases hs₁ s h with h | h
      · exact .inl h
      · exact .inr ⟨g, List.mem_cons_self, h⟩
    · exact .inr ⟨g', List.mem_cons_of_mem _ hg', h⟩

theorem composed_src (D : SDoc) (hw : JsonWF D.doc) (u : String) (o : Json) (h : composed D u = .ok o) :
    (∀ kvs, o = .obj kvs → kvs.WF) ∧
      ∀ s, HasStr s o → HasStr s D.doc ∨ ∃ g ∈ D.governors, HasStr s (payload g.effect) := by
  unfold composed at h
  obtain ⟨o₀, h₀, h⟩ := (ebind_ok _ _ _).mp h
  obtain ⟨hw₀, hs₀⟩ := baseObj_src D hw u o₀ h₀
  obtain ⟨hw', hs'⟩ := fold_src u _ o₀ o h hw₀
  refine ⟨hw', fun s hs => ?_⟩
  rcases hs' s hs with h | ⟨g, hg, h⟩
  · exact hs₀ s h
  · exact .inr ⟨g, ((governorsOf_iff D u g).mp hg).1, h⟩

/-! `govern`'s answer -/

theorem govern_ok (D : SDoc) (out : Json) (ho : govern D = .ok out) :
    (D.governors = [] ∧ partUnits D = [] ∧ out = D.doc) ∨
    ∃ comp t, (affected D).mapM (fun u => do pure (u, ← composed D u)) = .ok comp ∧ ruleTable D = .ok t ∧
      out = patch D (comp.map fun (u, o) => (u, addOver (edgesInto D (fun v => t.lookup v) u) o)) := by
  unfold govern at ho
  obtain ⟨_, -, ho⟩ := (ebind_ok _ _ _).mp ho
  split at ho
  · next hg =>
    split at ho
    · next hp => cases ho; exact .inl ⟨List.isEmpty_iff.mp hg, hp, rfl⟩
    · cases ho
  · obtain ⟨_, -, ho⟩ := (ebind_ok _ _ _).mp ho
    obtain ⟨comp, hc, ho⟩ := (ebind_ok _ _ _).mp ho
    obtain ⟨t, ht, ho⟩ := (ebind_ok _ _ _).mp ho
    obtain ⟨_, -, ho⟩ := (ebind_ok _ _ _).mp ho
    cases ho
    exact .inr ⟨comp, t, hc, ht, rfl⟩

theorem fresh_mem (old : List String) (x : String) : ∀ (names acc : List String),
    x ∈ names.foldl (fun acc n => if old.contains n || acc.contains n then acc else acc ++ [n]) acc →
      x ∈ acc ∨ x ∈ names
  | [], acc, h => .inl h
  | n :: ns, acc, h => by
    rw [List.foldl_cons] at h
    rcases fresh_mem old x ns _ h with h | h
    · split at h
      · exact .inl h
      · rcases List.mem_append.mp h with h | h
        · exact .inl h
        · exact .inr (List.mem_singleton.mp h ▸ List.mem_cons_self)
    · exact .inr (List.mem_cons_of_mem _ h)

theorem addOver_src (es : List String) (o : Json) (hw : ∀ kvs, o = .obj kvs → kvs.WF) :
    (∀ kvs, addOver es o = .obj kvs → kvs.WF) ∧ ∀ s, HasStr s (addOver es o) → HasStr s o ∨ s ∈ es := by
  unfold addOver
  split
  · next xs hx =>
    dsimp only
    split
    · exact ⟨hw, fun s h => .inl h⟩
    · refine ⟨top_set o hw _ _, fun s hs => ?_⟩
      rcases hasStr_set s o hw _ _ hs with h | h
      · exact .inl h
      · cases h with
        | arr hm hx' =>
          rcases Array.mem_append.mp hm with hm | hm
          · exact .inl (.obj hx (.arr hm hx'))
          · simp only [List.mem_toArray, List.mem_map] at hm
            obtain ⟨n, hn, rfl⟩ := hm
            cases hx' with
            | str => exact .inr ((fresh_mem _ _ es [] hn).resolve_left (by simp))
            | obj hk _ => simp [Json.getObjVal?, throw, throwThe, MonadExceptOf.throw] at hk
        | obj hk _ => simp [Json.getObjVal?, throw, throwThe, MonadExceptOf.throw] at hk
  · exact ⟨hw, fun s h => .inl h⟩

theorem newContent_src (c o : Json) (hw : JsonWF c) (s : String) (h : HasStr s (newContent c o)) :
    HasStr s c ∨ HasStr s o := by
  unfold newContent at h
  split at h
  · obtain ⟨p, hp, hs⟩ := hasStr_mkObj s _ h
    rcases List.mem_append.mp hp with hp | hp
    · have hp := (List.mem_filter.mp hp).1
      cases c with
      | obj kvs => exact .inl (.obj (members_get kvs (jsonWF_top _ hw kvs rfl) _ _ hp) hs)
      | _ => exact absurd hp (by rw [show members _ = [] from rfl]; exact List.not_mem_nil)
    · rw [List.mem_singleton.mp hp] at hs; exact .inr hs
  · exact hasStr_set s c (jsonWF_top c hw) _ _ h

theorem setObjVal_ne (o : Json) (hw : ∀ kvs, o = .obj kvs → kvs.WF) (k k' : String) (v : Json) (hk : k ≠ k') :
    (o.setObjVal! k v).getObjVal? k' = o.getObjVal? k' := by
  cases o with
  | obj t =>
    simp [Json.setObjVal!, Json.getObjVal?, Std.TreeMap.Raw.get?_eq_getElem?,
      Std.TreeMap.Raw.getElem?_insert (hw t rfl), Std.LawfulEqCmp.compare_eq_iff_eq, hk]
  | _ => rw [setObjVal_null _ (by simp)]; try rfl

theorem setObjVal_self (kvs : Std.TreeMap.Raw String Json) (hw : kvs.WF) (k : String) (v : Json) :
    ((Json.obj kvs).setObjVal! k v).getObjVal? k = .ok v :=
  (setObjVal_get kvs hw k k v v).mpr (.inl ⟨rfl, rfl⟩)

theorem idOf_set (u : Json) (hw : ∀ kvs, u = .obj kvs → kvs.WF) (v : Json) : idOf (u.setObjVal! "content" v) = idOf u := by
  simp only [idOf, Json.getObjValD, setObjVal_ne u hw "content" "id" v (by decide)]

theorem unitsOf_patch (D : SDoc) (hw : JsonWF D.doc) (comp : List (String × Json)) :
    unitsOf (patch D comp) = (unitsOf D.doc).map fun u => match comp.lookup (idOf u) with
      | some o => u.setObjVal! "content" (newContent (u.getObjValD "content") o)
      | none => u := by
  unfold patch
  cases hd : D.doc with
  | obj t =>
    conv => lhs; unfold unitsOf
    simp only [Json.getObjValD, setObjVal_self t (jsonWF_top _ hw t hd), Except.toOption, Option.getD_some]
    rfl
  | _ => rw [setObjVal_null _ (by simp)]; rfl

theorem lookup_mem {β : Type} (k : String) (b : β) : ∀ (l : List (String × β)), l.lookup k = some b → (k, b) ∈ l
  | [], h => by cases h
  | (k', b') :: l, h => by
    simp only [List.lookup] at h
    split at h
    · next he => cases h; rw [eq_of_beq he]; exact List.mem_cons_self
    · exact List.mem_cons_of_mem _ (lookup_mem k b l h)

/-- Every string of the patched document is the document's or a composed rule's. -/
theorem patch_src (D : SDoc) (hw : JsonWF D.doc) (comp : List (String × Json)) (s : String)
    (h : HasStr s (patch D comp)) : HasStr s D.doc ∨ ∃ p ∈ comp, HasStr s p.2 := by
  unfold patch at h
  rcases hasStr_set s _ (jsonWF_top _ hw) _ _ h with h | h
  · exact .inl h
  · cases h with
    | arr hm hx =>
      simp only [List.mem_toArray, List.mem_map] at hm
      obtain ⟨y, hy, rfl⟩ := hm
      have hu := unitsOf_mem D.doc y hy
      split at hx
      · next o ho =>
        rcases hasStr_set s y (jsonWF_top _ (hu.2 hw)) _ _ hx with h | h
        · exact .inl (hu.1 s h)
        · rcases newContent_src _ o (jsonWF_getD _ (hu.2 hw) _) s h with h | h
          · exact .inl (hu.1 s (hasStr_getD _ _ _ h))
          · exact .inr ⟨(idOf y, o), lookup_mem _ _ _ ho, h⟩
      · exact .inl (hu.1 s hx)
    | obj hk _ => simp [Json.getObjVal?, throw, throwThe, MonadExceptOf.throw] at hk

theorem edgesOf_name (D : SDoc) (rule : String → Option SoftNode) (g : Governor) (w n : String)
    (h : (w, n) ∈ edgesOf D rule g) : ∃ v M, rule v = some M ∧ n = M.name := by
  unfold edgesOf at h
  split at h
  · cases h
  · next N hN =>
    split at h <;> simp only [List.mem_filterMap, Option.bind_eq_some_iff] at h
    · obtain ⟨v, -, M, hM, he⟩ := h
      split at he <;> cases he
      exact ⟨v, M, hM, rfl⟩
    · obtain ⟨v, -, M, hM, he⟩ := h
      split at he <;> cases he
      exact ⟨g.unit, N, hN, rfl⟩
    · cases h

/-- A rule `govern` writes is the composed rule of an affected unit, with the edges into it. -/
theorem comp_entry (D : SDoc) (comp : List (String × Json))
    (hc : (affected D).mapM (fun u => do pure (u, ← composed D u)) = .ok comp) (u : String) (o : Json)
    (h : (u, o) ∈ comp) : u ∈ affected D ∧ composed D u = .ok o := by
  obtain ⟨x, hx, he⟩ := mapM_ok_mem _ _ comp hc (u, o) h
  obtain ⟨o', ho', he⟩ := (ebind_ok _ _ _).mp he
  cases he
  exact ⟨hx, ho'⟩

/-- Every string value of the answer is a string value of the document or of a governor's payload. -/
theorem govern_strings (D : SDoc) (hw : JsonWF D.doc) (out : Json) (ho : govern D = .ok out) (s : String)
    (hs : HasStr s out) : HasStr s D.doc ∨ ∃ g ∈ D.governors, HasStr s (payload g.effect) := by
  rcases govern_ok D out ho with ⟨-, -, rfl⟩ | ⟨comp, t, hc, ht, rfl⟩
  · exact .inl hs
  rcases patch_src D hw _ s hs with h | ⟨p, hp, h⟩
  · exact .inl h
  obtain ⟨⟨u, o⟩, hm, rfl⟩ := List.mem_map.mp hp
  obtain ⟨-, hco⟩ := comp_entry D comp hc u o hm
  obtain ⟨hwo, hso⟩ := composed_src D hw u o hco
  rcases (addOver_src _ o hwo).2 s h with h | h
  · exact hso s h
  obtain ⟨g, -, -, he⟩ := edgesInto_mem D _ u s h
  obtain ⟨v, M, hv, rfl⟩ := edgesOf_name D _ g u _ he
  obtain ⟨o', hc', hd⟩ := ruleTable_decoder D t ht v M (lookup_mem _ _ _ hv)
  have := composed_src D hw v o' hc'
  exact this.2 _ (decodeNorm_name_top D.re o' this.1 M hd)

/-- Scope introduces no symbol: for governors bound to the block, every string value of the answer is a string
    value of the document or the block. -/
theorem govern_no_new_symbols (D : SDoc) (hw : JsonWF D.doc) (hb : BlockBound D) (out : Json)
    (ho : govern D = .ok out) (s : String) (hs : HasStr s out) : HasStr s D.doc ∨ HasStr s D.block := by
  rcases govern_strings D hw out ho s hs with h | ⟨g, hg, h⟩
  · exact .inl h
  · exact .inr (hb g hg s h)

/-- Preservation: every member outside `units`, the unit order, every unit member but `content`, and every
    content outside `affected D`, are the document's own. -/
theorem govern_preserves (D : SDoc) (hw : JsonWF D.doc) (out : Json) (ho : govern D = .ok out) :
    (∀ k, k ≠ "units" → out.getObjVal? k = D.doc.getObjVal? k) ∧
    (unitsOf out).map idOf = (unitsOf D.doc).map idOf ∧
    ∀ (i : Nat) (x y : Json), (unitsOf out)[i]? = some x → (unitsOf D.doc)[i]? = some y →
      (∀ k, k ≠ "content" → x.getObjVal? k = y.getObjVal? k) ∧ (idOf y ∉ affected D → x = y) := by
  rcases govern_ok D out ho with ⟨-, -, rfl⟩ | ⟨comp, t, hc, ht, rfl⟩
  · refine ⟨fun _ _ => rfl, rfl, fun i x y hx hy => ?_⟩
    rw [hx] at hy; cases hy
    exact ⟨fun _ _ => rfl, fun _ => rfl⟩
  have hu : ∀ y ∈ unitsOf D.doc, ∀ kvs, y = .obj kvs → kvs.WF := fun y hy => jsonWF_top _ ((unitsOf_mem _ y hy).2 hw)
  refine ⟨fun k hk => setObjVal_ne _ (jsonWF_top _ hw) _ _ _ (Ne.symm hk), ?_, fun i x y hx hy => ?_⟩
  · rw [unitsOf_patch D hw, List.map_map]
    refine List.map_congr_left fun y hy => ?_
    simp only [Function.comp]
    split
    · exact idOf_set y (hu y hy) _
    · rfl
  · rw [unitsOf_patch D hw, List.getElem?_map, hy, Option.map_some, Option.some.injEq] at hx
    subst hx
    have hy' := hu y (List.mem_of_getElem? hy)
    split
    · next o hl =>
      refine ⟨fun k hk => setObjVal_ne _ hy' _ _ _ (Ne.symm hk), fun hn => ?_⟩
      obtain ⟨⟨u, o'⟩, hm, he⟩ := List.mem_map.mp (lookup_mem _ _ _ hl)
      cases he
      exact absurd (comp_entry D comp hc _ o' hm).1 hn
    · exact ⟨fun _ _ => rfl, fun _ => rfl⟩

end Statements

end VE.Scope
