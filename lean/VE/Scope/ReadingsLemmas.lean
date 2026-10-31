import VE.Scope.Readings
import VE.Scope.Theorems

/-! Lemmas for spec 11.3's statements that take `JsonWF` (sc-5rd, `ReadingsTheorems.lean`): what `atChoiceOn` writes
    and what a lookup reads back from it on a well-formed tree (spec 11.3: on a tree that is not well formed a lookup
    can miss the member `setObjVal!` wrote), what a choice leaves of the rule units and the reaches, and what a
    successful `governSets` and `assemble` are made of. -/

namespace VE.Scope
open Lean
open VE.NormDefaults (ebind_ok)

/-- A member of an array member of a JSON value is part of it. -/
theorem arrAt_mem (doc x : Json) (k : String) (hx : x ∈ (match doc.getObjValD k with | .arr xs => xs.toList | _ => [])) :
    (∀ s, HasStr s x → HasStr s doc) ∧ (JsonWF doc → JsonWF x) := by
  split at hx
  · next xs he =>
    have hm := Array.mem_toList_iff.mp hx
    refine ⟨fun s h => hasStr_getD s doc k (he ▸ .arr hm h), fun hw => ?_⟩
    have := jsonWF_getD doc hw k
    rw [he] at this
    cases this with | arr _ hall => exact hall x hm
  · cases hx

theorem jsonWF_set (o v : Json) (ho : JsonWF o) (hv : JsonWF v) (k : String) : JsonWF (o.setObjVal! k v) := by
  cases ho with
  | obj t hw hall =>
    refine .obj _ hw.insert fun kv hkv => ?_
    rw [Std.TreeMap.Raw.mem_toList_iff_getElem?_eq_some hw.insert, Std.TreeMap.Raw.getElem?_insert hw] at hkv
    split at hkv
    · cases hkv; exact hv
    · exact hall kv ((Std.TreeMap.Raw.mem_toList_iff_getElem?_eq_some hw).mpr hkv)
  | _ => exact .null

theorem getD_set2 (t : Std.TreeMap.Raw String Json) (ht : t.WF) (k₁ k₂ : String) (hk : k₁ ≠ k₂) (v₁ v₂ : Json) :
    (((Json.obj t).setObjVal! k₁ v₁).setObjVal! k₂ v₂).getObjValD k₂ = v₂ ∧
      (((Json.obj t).setObjVal! k₁ v₁).setObjVal! k₂ v₂).getObjValD k₁ = v₁ := by
  have e : (Json.obj t).setObjVal! k₁ v₁ = .obj (t.insert k₁ v₁) := rfl
  rw [e]
  constructor
  · rw [Json.getObjValD, setObjVal_self _ ht.insert]; rfl
  · rw [Json.getObjValD, setObjVal_ne _ (fun _ h => by cases h; exact ht.insert) _ _ _ (Ne.symm hk), ← e,
      setObjVal_self t ht]; rfl

theorem find?_congr' {α : Type} (p q : α → Bool) : ∀ (l : List α), (∀ x ∈ l, p x = q x) → l.find? p = l.find? q
  | [], _ => rfl
  | x :: l, h => by
    simp only [List.find?_cons, h x List.mem_cons_self, find?_congr' p q l fun y hy => h y (List.mem_cons_of_mem _ hy)]

theorem readingAt_src (s : Json) (i : Nat) :
    (∀ t, HasStr t (readingAt s i) → HasStr t s) ∧ (JsonWF s → JsonWF (readingAt s i)) := by
  unfold readingAt
  cases hi : (readingsJson s)[i]? with
  | none => exact ⟨fun t h => absurd h (hasStr_null t), fun _ => .null⟩
  | some r =>
    have hrr := arrAt_mem s r "readings" (List.mem_of_getElem? hi)
    exact ⟨fun t h => hrr.1 t (hasStr_getD _ _ _ h), fun hw => jsonWF_getD _ (hrr.2 hw) _⟩

/-- Each unit under one choice: its id and every member but `content` kept, unchanged outside `su`, well formed, and
    every string of the document's. -/
theorem unitsOf_atChoiceOn (su : List String) (doc : Json) (ch : VE.Discourse.Choice) (hw : JsonWF doc) :
    unitsOf (atChoiceOn su doc ch) = (unitsOf doc).map fun u =>
      match (setsJson doc).find? (fun s => su.contains (setUnit s) && setUnit s == idOf u) with
      | some s => u.setObjVal! "content" (((pickOf ch s).map (readingAt s)).getD .null)
      | none => u := by
  unfold atChoiceOn
  cases hw with
  | obj t ht _ => simp only [unitsOf, (getD_set2 t ht "units" "reading_sets" (by decide) _ _).2]; rfl
  | _ => rfl

theorem atChoiceOn_sets (su : List String) (doc : Json) (ch : VE.Discourse.Choice) (hw : JsonWF doc) :
    setsJson (atChoiceOn su doc ch) = (setsJson doc).filter fun s => !su.contains (setUnit s) := by
  unfold atChoiceOn
  cases hw with
  | obj t ht _ => simp only [setsJson, (getD_set2 t ht "units" "reading_sets" (by decide) _ _).1]
  | _ => rfl

theorem atChoiceOn_units (su : List String) (doc : Json) (ch : VE.Discourse.Choice) (hw : JsonWF doc) :
    ∃ F : Json → Json, atChoiceOn su doc ch = (doc.setObjVal! "units" (.arr ((unitsOf doc).map F).toArray)).setObjVal!
        "reading_sets" (.arr ((setsJson doc).filter fun s => !su.contains (setUnit s)).toArray) ∧
      unitsOf (atChoiceOn su doc ch) = (unitsOf doc).map F ∧ ∀ y ∈ unitsOf doc,
      idOf (F y) = idOf y ∧ (∀ k, k ≠ "content" → (F y).getObjVal? k = y.getObjVal? k) ∧ (idOf y ∉ su → F y = y) ∧
      JsonWF (F y) ∧ ∀ s, HasStr s (F y) → HasStr s doc := by
  refine ⟨_, rfl, unitsOf_atChoiceOn su doc ch hw, fun y hy => ?_⟩
  have hy' := unitsOf_mem doc y hy
  have hyw := jsonWF_top _ (hy'.2 hw)
  split
  · next s hs =>
    have hsm := List.mem_of_find?_eq_some hs
    have hsu := List.find?_some hs
    simp only [Bool.and_eq_true, beq_iff_eq, List.contains_iff_mem] at hsu
    have hss := arrAt_mem doc s "reading_sets" hsm
    have hr : ∀ i, (∀ t, HasStr t (readingAt s i) → HasStr t doc) ∧ JsonWF (readingAt s i) := fun i =>
      ⟨fun t h => hss.1 t ((readingAt_src s i).1 t h), (readingAt_src s i).2 (hss.2 hw)⟩
    have hv : (∀ t, HasStr t (((pickOf ch s).map (readingAt s)).getD .null) → HasStr t doc) ∧
        JsonWF (((pickOf ch s).map (readingAt s)).getD .null) := by
      cases pickOf ch s with
      | none => exact ⟨fun t h => absurd h (hasStr_null t), .null⟩
      | some i => exact hr i
    refine ⟨idOf_set y hyw _, fun k hk => setObjVal_ne _ hyw _ _ _ (Ne.symm hk), fun hn => absurd hsu.2.symm ?_,
      jsonWF_set _ _ (hy'.2 hw) hv.2 _, fun t h => ?_⟩
    · intro he; exact hn (he ▸ hsu.1)
    · rcases hasStr_set t y hyw _ _ h with h | h
      · exact hy'.1 t h
      · exact hv.1 t h
  · exact ⟨rfl, fun _ _ => rfl, fun _ => rfl, hy'.2 hw, hy'.1⟩

theorem unitIds_atChoiceOn (su : List String) (doc : Json) (ch : VE.Discourse.Choice) (hw : JsonWF doc) :
    unitIds (atChoiceOn su doc ch) = unitIds doc := by
  obtain ⟨F, -, hF, hp⟩ := atChoiceOn_units su doc ch hw
  rw [unitIds, hF, List.map_map]
  exact List.map_congr_left fun y hy => (hp y hy).1

theorem contentOf_atChoiceOn (su : List String) (doc : Json) (ch : VE.Discourse.Choice) (hw : JsonWF doc) (v : String)
    (hv : v ∉ su) : contentOf (atChoiceOn su doc ch) v = contentOf doc v := by
  obtain ⟨F, -, hF, hp⟩ := atChoiceOn_units su doc ch hw
  unfold contentOf
  rw [hF, List.find?_map, find?_congr' _ (idOf · == v) _ fun y hy => by simp only [Function.comp, (hp y hy).1]]
  cases hf : (unitsOf doc).find? (idOf · == v) with
  | none => rfl
  | some y =>
    have := List.find?_some hf
    simp only [beq_iff_eq] at this
    simp only [Option.map_some, (hp y (List.mem_of_find?_eq_some hf)).2.2.1 (this ▸ hv)]

theorem setUnits_eq (doc : Json) : setUnits doc = (setsJson doc).map setUnit := by
  unfold setUnits setsJson; split <;> simp_all [setUnit]

/-- A rule unit is no governed set unit (its content is not `null`): under a choice it is the same rule. -/
theorem rule_atChoice (D : SDoc) (ch : VE.Discourse.Choice) (hw : JsonWF D.doc) (v : String) (hv : v ∈ ruleUnits D) :
    v ∈ ruleUnits (atChoice D ch) ∧ baseName (atChoice D ch) v = baseName D v := by
  have hn : v ∉ governedSetUnits D := fun h => by
    have := (List.mem_filter.mp hv).2
    have h' := (List.mem_filter.mp h).2
    simp only [Bool.and_eq_true] at h'
    have hnull : contentOf D.doc v = .null := by
      generalize contentOf D.doc v = c at h'; cases c <;> simp_all [Json.isNull]
    rw [hnull] at this
    exact absurd this (by decide)
  have hc := contentOf_atChoiceOn (governedSetUnits D) D.doc ch hw v hn
  refine ⟨?_, ?_⟩
  · have := List.mem_filter.mp hv
    exact List.mem_filter.mpr ⟨(unitIds_atChoiceOn _ _ ch hw).symm ▸ this.1, by simpa [atChoice, hc] using this.2⟩
  · simp only [baseName, baseObj, atChoice, hc]; rfl

/-- Under a choice a reach covers every unit it covers on the document (a `rules` reach reads the rule units, which
    no choice changes). -/
theorem covered_atChoice (D : SDoc) (ch : VE.Discourse.Choice) (hw : JsonWF D.doc) (r : Reach) (us : List String)
    (hc : covered D r = .ok us) : ∃ us', covered (atChoice D ch) r = .ok us' ∧ ∀ v ∈ us, v ∈ us' := by
  cases r with
  | rules ns =>
    unfold covered at hc ⊢
    obtain ⟨_, hl, hc⟩ := (ebind_ok _ _ _).mp hc
    cases hc
    refine ⟨_, (ebind_ok _ _ _).mpr ⟨PUnit.unit, ?_, rfl⟩, fun v hv => ?_⟩
    · rename_i w; cases w
      have hf : ∀ (D' : SDoc) (x : String) (r : ForInStep PUnit),
          (if ((ruleUnits D').any fun u => baseName D' u == some x) = true then
            (do pure PUnit.unit; pure (ForInStep.yield PUnit.unit) : Except String _)
          else do throw (toString "ScopeUnknownRule: " ++ toString x); pure (ForInStep.yield PUnit.unit)) = .ok r →
          r = .yield PUnit.unit := fun D' x r h => by
        split at h
        · cases h; rfl
        · cases h
      rw [VE.NormDefaults.forIn_unit_ok _ (hf D) ns] at hl
      rw [VE.NormDefaults.forIn_unit_ok _ (hf (atChoice D ch)) ns]
      intro n hn
      have := hl n hn
      split at this
      · next h =>
        obtain ⟨v, hv, hb⟩ := List.any_eq_true.mp h
        obtain ⟨hv', hb'⟩ := rule_atChoice D ch hw v hv
        rw [if_pos (List.any_eq_true.mpr ⟨v, hv', hb' ▸ hb⟩)]; rfl
      · cases this
    · obtain ⟨hv, hb⟩ := List.mem_filter.mp hv
      obtain ⟨hv', hb'⟩ := rule_atChoice D ch hw v hv
      exact List.mem_filter.mpr ⟨hv', hb' ▸ hb⟩
  | _ => exact ⟨us, hc, fun _ h => h⟩

/-- A successful `governSets` over governed sets: every per-choice answer it assembles is `govern`'s under that choice. -/
theorem governSets_ok (D : SDoc) (hs : governedSetUnits D ≠ []) (out : Json) (ho : governSets D = .ok out) :
    ∃ ch₀ o₀ outs, (∀ p ∈ outs, governChoice D p.1 = .ok p.2) ∧ (ch₀, o₀) ∈ outs ∧
      assemble D ch₀ o₀ outs = .ok out := by
  have hne : (governedSetUnits D).isEmpty = false := by simpa using hs
  simp only [governSets, governSetsWith, hne, Bool.false_eq_true, if_false] at ho
  obtain ⟨cs, -, ho⟩ := (ebind_ok _ _ _).mp ho
  split at ho
  · cases ho
  · split at ho
    · cases ho
    · next outs ch₀ o₀ rest hm =>
      refine ⟨ch₀, o₀, (ch₀, o₀) :: rest, fun p hp => ?_, List.mem_cons_self, ho⟩
      rw [← hm] at hp
      obtain ⟨⟨ch, r⟩, hr, he⟩ := List.mem_filterMap.mp hp
      obtain ⟨c, -, hc⟩ := List.mem_map.mp hr
      cases hc
      cases hg : govern (atChoice D ch) with
      | error e => rw [hg] at he; cases he
      | ok o => rw [hg] at he; cases he; exact hg

theorem mapM_ok_idx {α β ε : Type} (f : α → Except ε β) : ∀ (xs : List α) (ys : List β), xs.mapM f = .ok ys →
    ys.length = xs.length ∧ ∀ (i : Nat) (x : α) (y : β), xs[i]? = some x → ys[i]? = some y → f x = .ok y
  | [], ys, h => by cases h; exact ⟨rfl, fun _ _ _ h => by simp at h⟩
  | x :: xs, ys, h => by
    rw [List.mapM_cons] at h
    obtain ⟨b, hb, h⟩ := (ebind_ok _ _ _).mp h
    obtain ⟨bs, hbs, h⟩ := (ebind_ok _ _ _).mp h
    cases h
    obtain ⟨hl, hi⟩ := mapM_ok_idx f xs bs hbs
    refine ⟨by simp [hl], fun i x' y hx hy => ?_⟩
    cases i with
    | zero => simp only [List.getElem?_cons_zero, Option.some.injEq] at hx hy; subst hx hy; exact hb
    | succ i => exact hi i x' y (by simpa using hx) (by simpa using hy)

/-- What `assemble` writes: the units of `o₀` outside the governed set units, and each governed set with each
    reading's `content` either as written or as a per-choice answer gives its unit. -/
theorem assemble_ok (D : SDoc) (ch₀ : VE.Discourse.Choice) (o₀ : Json) (outs : List (VE.Discourse.Choice × Json))
    (out : Json) (h : assemble D ch₀ o₀ outs = .ok out) :
    ∃ sets : List Json, out = (D.doc.setObjVal! "units" (.arr ((((unitsOf o₀).zip (unitsOf D.doc)).map fun (x, y) =>
        if (governedSetUnits D).contains (idOf y) then y else x).toArray))).setObjVal! "reading_sets" (.arr sets.toArray) ∧
      sets.length = (setsJson D.doc).length ∧
      ∀ (i : Nat) (s s' : Json), (setsJson D.doc)[i]? = some s → sets[i]? = some s' →
        ((governedSetUnits D).contains (setUnit s) = false → s' = s) ∧
        ((governedSetUnits D).contains (setUnit s) = true → ∃ rs : List Json,
          s' = s.setObjVal! "readings" (.arr rs.toArray) ∧ rs.length = (readingsJson s).length ∧
          ∀ (n : Nat) (r r' : Json), (readingsJson s)[n]? = some r → rs[n]? = some r' →
            ∃ c, r' = r.setObjVal! "content" c ∧ (c = readingAt s n ∨ ∃ p ∈ outs, c = contentOf p.2 (setUnit s))) := by
  unfold assemble at h
  obtain ⟨_, -, h⟩ := (ebind_ok _ _ _).mp h
  obtain ⟨sets, hm, h⟩ := (ebind_ok _ _ _).mp h
  cases h
  obtain ⟨hl, hi⟩ := mapM_ok_idx _ _ sets hm
  refine ⟨sets, rfl, hl, fun i s s' hs hs' => ?_⟩
  have hf := hi i s s' hs hs'
  refine ⟨fun hn => by rw [if_neg (Bool.eq_false_iff.mp hn)] at hf; cases hf; rfl, fun hy => ?_⟩
  rw [if_pos hy] at hf
  obtain ⟨rs, hrs, hf⟩ := (ebind_ok _ _ _).mp hf
  cases hf
  obtain ⟨hl', hi'⟩ := mapM_ok_idx _ _ rs hrs
  refine ⟨rs, rfl, by simpa using hl', fun n r r' hr hr' => ?_⟩
  have hg := hi' n (r, n) r' (by simp [List.getElem?_zipIdx, hr]) hr'
  obtain ⟨c, hc, hg⟩ := (ebind_ok _ _ _).mp hg
  cases hg
  refine ⟨c, rfl, ?_⟩
  dsimp only at hc
  split at hc
  · cases hc; exact .inl rfl
  · next c₁ o₁ rest he =>
    obtain ⟨_, -, hc⟩ := (ebind_ok _ _ _).mp hc
    cases hc
    exact .inr ⟨(c₁, o₁), (List.mem_filter.mp (he ▸ List.mem_cons_self : (c₁, o₁) ∈ _)).1, rfl⟩

theorem jsonWF_atChoiceOn (su : List String) (doc : Json) (ch : VE.Discourse.Choice) (hw : JsonWF doc) :
    JsonWF (atChoiceOn su doc ch) := by
  obtain ⟨F, he, -, hp⟩ := atChoiceOn_units su doc ch hw
  rw [he]
  refine jsonWF_set _ _ (jsonWF_set _ _ hw (.arr _ fun x hx => ?_) _) (.arr _ fun x hx => ?_) _
  · obtain ⟨y, hy, rfl⟩ := List.mem_map.mp (List.mem_toArray.mp hx)
    exact (hp y hy).2.2.2.1
  · exact (arrAt_mem doc x "reading_sets" (List.mem_filter.mp (List.mem_toArray.mp hx)).1).2 hw

theorem setsJson_of_get (a b : Json) (h : a.getObjVal? "reading_sets" = b.getObjVal? "reading_sets") :
    setsJson a = setsJson b := by
  simp only [setsJson, Json.getObjValD, h]

theorem readingsJson_set (y : Json) (hy : ∀ kvs, y = .obj kvs → kvs.WF) (rs : List Json)
    (hl : rs.length = (readingsJson y).length) : readingsJson (y.setObjVal! "readings" (.arr rs.toArray)) = rs := by
  cases y with
  | obj t => simp only [readingsJson, Json.getObjValD, setObjVal_self t (hy t rfl)]; rfl
  | _ => exact (List.eq_nil_of_length_eq_zero hl).symm ▸ rfl

theorem su_obj (D : SDoc) (hs : governedSetUnits D ≠ []) : ∃ t, D.doc = .obj t := by
  cases hd : D.doc with
  | obj t => exact ⟨t, rfl⟩
  | _ =>
    exfalso; apply hs
    simp only [governedSetUnits, hd, setUnits, Json.getObjValD, Json.getObjVal?]
    rfl

theorem hasStr_atChoiceOn (su : List String) (doc : Json) (ch : VE.Discourse.Choice) (hw : JsonWF doc) (s : String)
    (h : HasStr s (atChoiceOn su doc ch)) : HasStr s doc := by
  obtain ⟨F, he, -, hp⟩ := atChoiceOn_units su doc ch hw
  rw [he] at h
  rcases hasStr_set s _ (top_set _ (jsonWF_top _ hw) _ _) _ _ h with h | h
  · rcases hasStr_set s _ (jsonWF_top _ hw) _ _ h with h | h
    · exact h
    · cases h with
      | arr hm h =>
        obtain ⟨y, hy, rfl⟩ := List.mem_map.mp (List.mem_toArray.mp hm)
        exact (hp y hy).2.2.2.2 s h
      | obj hk _ => cases hk
  · cases h with
    | arr hm h => exact (arrAt_mem doc _ "reading_sets" (List.mem_filter.mp (List.mem_toArray.mp hm)).1).1 s h
    | obj hk _ => cases hk

end VE.Scope
