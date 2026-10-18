import VE.Scope.Effects

/-! Theorems of scope@0's effects (docs/spec/scope.md 5.1). -/

namespace VE.Scope
open Lean

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

end VE.Scope
