import VE.RightClauses.Wire

namespace VE.RightClauses
open Lean

theorem impl_get_map (f : String → Json → Json) (a : String) :
    ∀ t : Std.DTreeMap.Internal.Impl String (fun _ => Json),
      Std.DTreeMap.Internal.Impl.Const.get? (t.map f) a = (Std.DTreeMap.Internal.Impl.Const.get? t a).map (f a)
  | .leaf => rfl
  | .inner _ k v l r => by
    simp only [Std.DTreeMap.Internal.Impl.map, Std.DTreeMap.Internal.Impl.Const.get?]
    cases h : compare a k with
    | lt => exact impl_get_map f a l
    | gt => exact impl_get_map f a r
    | eq => simp [Std.LawfulEqOrd.eq_of_compare h]

theorem getObjVal_mapMember (k : String) (f : Json → Json) (j : Json) (a : String) :
    (mapMember k f j).getObjVal? a = if a = k then (fun v => f v) <$> j.getObjVal? a else j.getObjVal? a := by
  cases j with
  | obj kvs =>
    simp only [mapMember, Json.getObjVal?, Std.TreeMap.Raw.get?, Std.TreeMap.Raw.map, Std.DTreeMap.Raw.Const.get?,
      Std.DTreeMap.Raw.map, impl_get_map]
    cases Std.DTreeMap.Internal.Impl.Const.get? kvs.inner.inner a <;> by_cases h : a = k <;> simp [h] <;> rfl
  | _ => split <;> rfl


/-- The member list of `mapMember`: each value of key `k` through `f`, in place. -/
def mapPair (k : String) (f : Json → Json) (p : String × Json) : String × Json := (p.1, if p.1 == k then f p.2 else p.2)

@[simp] theorem fst_comp_mapPair (k : String) (f : Json → Json) : Prod.fst ∘ mapPair k f = Prod.fst := by
  funext p; rfl

@[simp] theorem map_fst_mapPair (k : String) (f : Json → Json) (l : List (String × Json)) :
    (l.map (mapPair k f)).map Prod.fst = l.map Prod.fst := by
  simp [List.map_map, Function.comp_def, mapPair]

theorem fields_mapMember (k : String) (f : Json → Json) (j : Json) :
    VE.Bridge.fields (mapMember k f j) = (fun l => l.map (mapPair k f)) <$> VE.Bridge.fields j := by
  cases j <;> simp only [mapMember, VE.Bridge.fields, Json.getObj?] <;> try rfl
  simp only [bind, Except.bind, pure, Except.pure, Functor.map, Except.map, Std.TreeMap.Raw.toList_map]
  rfl

theorem names_mapMember (k : String) (f : Json → Json) (j : Json) :
    (fun l => l.map (·.1)) <$> VE.Bridge.fields (mapMember k f j) = (fun l => l.map (·.1)) <$> VE.Bridge.fields j := by
  rw [fields_mapMember]
  cases VE.Bridge.fields j <;> simp [Functor.map, Except.map, mapPair]

theorem exactFields_mapMember (k : String) (f : Json → Json) (j : Json) (e : List String) :
    VE.Bridge.exactFields (mapMember k f j) e = VE.Bridge.exactFields j e := by
  unfold VE.Bridge.exactFields
  rw [fields_mapMember]
  cases VE.Bridge.fields j <;> simp only [Functor.map, Except.map, bind, Except.bind, map_fst_mapPair, List.map_map,
    fst_comp_mapPair]

theorem displayFields_mapMember (k : String) (f : Json → Json) (j : Json) (r o : List String) :
    VE.Bridge.displayFields (mapMember k f j) r o = VE.Bridge.displayFields j r o := by
  unfold VE.Bridge.displayFields
  simp only [exactFields_mapMember]
  rw [fields_mapMember]
  cases VE.Bridge.fields j <;> simp [Functor.map, Except.map, bind, Except.bind]

theorem getObjVal_mapMember_ne {k a : String} (f : Json → Json) (j : Json) (h : a ≠ k) :
    (mapMember k f j).getObjVal? a = j.getObjVal? a := by
  rw [getObjVal_mapMember]; simp [h]

theorem getObjValD_mapMember_ne {k a : String} (f : Json → Json) (j : Json) (h : a ≠ k) :
    (mapMember k f j).getObjValD a = j.getObjValD a := by
  simp only [Json.getObjValD, getObjVal_mapMember_ne f j h]

/-- Distinct keys, as `Std.TreeMap.Raw.ofList`'s lemmas state it. -/
abbrev Distinct (L : List (String × Json)) : Prop := L.Pairwise (fun a b => ¬ compare a.1 b.1 = .eq)

theorem getObjVal_mkObj_mem {L : List (String × Json)} (hd : Distinct L) {k : String} {v : Json} (hm : (k, v) ∈ L) :
    (Json.mkObj L).getObjVal? k = .ok v := by
  have := Std.TreeMap.Raw.getElem?_ofList_of_mem (cmp := compare) (k := k) (k' := k) (Std.ReflCmp.compare_self) hd hm
  simp only [Json.mkObj, Json.getObjVal?, Std.TreeMap.Raw.get?_eq_getElem?, this]; rfl

theorem getObjVal_mkObj_not {L : List (String × Json)} {k : String} (h : (L.map Prod.fst).contains k = false) :
    (Json.mkObj L).getObjVal? k = throw s!"property not found: {k}" := by
  have := Std.TreeMap.Raw.getElem?_ofList_of_contains_eq_false (cmp := compare) h
  simp only [Json.mkObj, Json.getObjVal?, Std.TreeMap.Raw.get?_eq_getElem?, this]

theorem fields_mkObj_single (k : String) (v : Json) : VE.Bridge.fields (Json.mkObj [(k, v)]) = .ok [(k, v)] := rfl


theorem ok_bind {ε α β : Type} {x : Except ε α} {a : α} (h : x = .ok a) (f : α → Except ε β) : (x >>= f) = f a := by
  rw [h]; rfl

theorem distinct_map {L : List (String × Json)} (hd : Distinct L) (k : String) (f : Json → Json) :
    Distinct (L.map (mapPair k f)) := by
  unfold Distinct at *; rw [List.pairwise_map]; exact hd.imp id

theorem names_mkObj_length {L : List (String × Json)} (hd : Distinct L) :
    ((Std.TreeMap.Raw.ofList L compare).toList.map Prod.fst).length = L.length := by
  rw [Std.TreeMap.Raw.map_fst_toList_eq_keys, Std.TreeMap.Raw.length_keys Std.TreeMap.Raw.WF.ofList,
    Std.TreeMap.Raw.size_ofList hd]

theorem names_mkObj_contains (L : List (String × Json)) (a : String) :
    ((Std.TreeMap.Raw.ofList L compare).toList.map Prod.fst).contains a = (L.map Prod.fst).contains a := by
  rw [Std.TreeMap.Raw.map_fst_toList_eq_keys, Std.TreeMap.Raw.contains_keys Std.TreeMap.Raw.WF.ofList,
    Std.TreeMap.Raw.contains_ofList]

/-- A key-preserving rewrite of a distinct member list keeps `exactFields`'s success. -/
theorem exactFields_mkObj_map {L : List (String × Json)} (hd : Distinct L) (k : String) (f : Json → Json)
    {e : List String} (h : VE.Bridge.exactFields (Json.mkObj L) e = .ok ()) :
    VE.Bridge.exactFields (Json.mkObj (L.map (mapPair k f))) e = .ok () := by
  unfold VE.Bridge.exactFields at h ⊢
  simp only [VE.Bridge.fields, Json.mkObj, Json.getObj?, bind, Except.bind, pure, Except.pure] at h ⊢
  have hl := names_mkObj_length hd
  have hl' := names_mkObj_length (distinct_map hd k f)
  have hc := names_mkObj_contains L
  have hc' := names_mkObj_contains (L.map (mapPair k f))
  simp only [map_fst_mapPair] at hc'
  split at h
  · rename_i hcond
    rw [if_pos]
    simp only [Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hcond ⊢
    refine ⟨?_, fun x hx => ?_⟩
    · have := hcond.1; simp only [List.length_map] at hl hl' this ⊢; omega
    · rw [hc', ← hc]; exact hcond.2 x hx
  · cases h

theorem contains_of_mem {L : List (String × Json)} {k : String} {v : Json} (h : (k, v) ∈ L) :
    (L.map Prod.fst).contains k = true :=
  List.contains_iff_mem.mpr (List.mem_map.mpr ⟨(k, v), h, rfl⟩)

theorem getObjVal_mkObj_map_ne {L : List (String × Json)} (hd : Distinct L) {k a : String} (f : Json → Json)
    (hne : a ≠ k) : (Json.mkObj (L.map (mapPair k f))).getObjVal? a = (Json.mkObj L).getObjVal? a := by
  cases hc : (L.map Prod.fst).contains a with
  | false =>
    rw [getObjVal_mkObj_not hc, getObjVal_mkObj_not (by simpa using hc)]
  | true =>
    obtain ⟨⟨a', v⟩, hm, ha⟩ := List.mem_map.mp (List.contains_iff_mem.mp hc)
    simp only at ha; subst ha
    rw [getObjVal_mkObj_mem hd hm, getObjVal_mkObj_mem (v := v) (distinct_map hd k f)
      (List.mem_map.mpr ⟨(a', v), hm, by simp [mapPair, hne]⟩)]

theorem getObjVal_mkObj_map_eq {L : List (String × Json)} (hd : Distinct L) {k : String} (w : Json)
    (hk : (L.map Prod.fst).contains k = true) : (Json.mkObj (L.map (mapPair k (fun _ => w)))).getObjVal? k = .ok w := by
  obtain ⟨⟨k', v⟩, hm, hk'⟩ := List.mem_map.mp (List.contains_iff_mem.mp hk)
  simp only at hk'; subst hk'
  exact getObjVal_mkObj_mem (distinct_map hd k' _) (List.mem_map.mpr ⟨(k', v), hm, by simp [mapPair]⟩)


theorem exactFields_norm (r : Json) : VE.Bridge.exactFields (Json.mkObj [("norm", r)]) ["norm"] = .ok () := rfl

theorem getObjVal_single (k : String) (r : Json) : (Json.mkObj [(k, r)]).getObjVal? k = .ok r :=
  getObjVal_mkObj_mem (List.pairwise_singleton _ _) (List.mem_singleton_self _)

/-- W1's field reader on a norm whose member list has its `guard` replaced: the same fields, the new guard. -/
theorem normFields_guard {F : List (String × Json)} (hd : Distinct F) (g : Json)
    {r : String × String × Bool × Json × List Json × List String}
    (h : VE.Norms.Wire.normFields (Json.mkObj [("norm", Json.mkObj F)]) = .ok r) :
    VE.Norms.Wire.normFields (Json.mkObj [("norm", Json.mkObj (F.map (mapPair "guard" (fun _ => g))))]) =
      .ok (r.1, r.2.1, r.2.2.1, g, r.2.2.2.2) := by
  have ne : ∀ a, a ≠ "guard" → (Json.mkObj (F.map (mapPair "guard" (fun _ => g)))).getObjValD a =
      (Json.mkObj F).getObjValD a := fun a ha => by
    simp only [Json.getObjValD, getObjVal_mkObj_map_ne hd _ ha]
  unfold VE.Norms.Wire.normFields at h ⊢
  rw [ok_bind (exactFields_norm _)] at h ⊢
  rw [ok_bind (getObjVal_single _ _)] at h ⊢
  obtain ⟨_, hx, h⟩ := VE.Kit.Except.bind_ok h
  have hg : ((F.map Prod.fst).contains "guard") = true := by
    unfold VE.Bridge.exactFields at hx
    simp only [VE.Bridge.fields, Json.mkObj, Json.getObj?, bind, Except.bind, pure, Except.pure] at hx
    split at hx
    · rename_i hc
      rw [← names_mkObj_contains]
      simp only [Bool.and_eq_true, List.all_eq_true] at hc
      exact hc.2 "guard" (by simp)
    · cases hx
  rw [ok_bind (exactFields_mkObj_map hd "guard" (fun _ => g) hx)]
  have sp : VE.Bridge.stringField (Json.mkObj (F.map (mapPair "guard" (fun _ => g)))) "predicate" =
      VE.Bridge.stringField (Json.mkObj F) "predicate" := by
    simp only [VE.Bridge.stringField, getObjVal_mkObj_map_ne hd _ (show "predicate" ≠ "guard" by decide)]
  have sg : (Json.mkObj (F.map (mapPair "guard" (fun _ => g)))).getObjValD "guard" = g := by
    simp only [Json.getObjValD, getObjVal_mkObj_map_eq hd g hg]; rfl
  rw [ne "name" (by decide), ne "sign" (by decide), ne "unless" (by decide), ne "over" (by decide), sp, sg]
  generalize (Json.mkObj F).getObjValD "name" = nm at h ⊢
  generalize VE.Bridge.stringField (Json.mkObj F) "predicate" = pr at h ⊢
  generalize (Json.mkObj F).getObjValD "sign" = sn at h ⊢
  generalize (Json.mkObj F).getObjValD "unless" = un at h ⊢
  generalize (Json.mkObj F).getObjValD "over" = ov at h ⊢
  generalize (Json.mkObj F).getObjValD "guard" = g1 at h
  cases nm <;> cases pr <;> cases sn <;> cases un <;> cases ov <;>
    simp only [bind, Except.bind, pure, Except.pure] at h ⊢ <;>
    first | cases h | skip
  revert h
  cases VE.Bridge.strings _ <;> intro h <;> cases h
  rfl


/-- W1's carve-out loop with unshared budgets: its carve-outs do not depend on the count it starts from. -/
theorem forIn_carve_count (f : Json → Except String (VE.Formula × Nat)) (u : List Json) (a : List VE.Formula)
    (c c' : Nat) {r : MProd (List VE.Formula) Nat}
    (h : forIn u (⟨a, c⟩ : MProd (List VE.Formula) Nat) (fun x (r : MProd (List VE.Formula) Nat) => do
      let d ← f x
      pure PUnit.unit
      pure (ForInStep.yield (⟨r.fst ++ [d.fst], d.snd⟩ : MProd (List VE.Formula) Nat))) = .ok r) :
    ∃ r', forIn u (⟨a, c'⟩ : MProd (List VE.Formula) Nat) (fun x (r : MProd (List VE.Formula) Nat) => do
      let d ← f x
      pure PUnit.unit
      pure (ForInStep.yield (⟨r.fst ++ [d.fst], d.snd⟩ : MProd (List VE.Formula) Nat))) = .ok r' ∧ r'.fst = r.fst := by
  cases u with
  | nil => cases h; exact ⟨_, rfl, rfl⟩
  | cons x xs =>
    simp only [List.forIn_cons] at h ⊢
    cases hf : f x with
    | error e => simp [hf, bind, Except.bind] at h
    | ok d =>
      simp only [hf, bind, Except.bind, pure, Except.pure] at h ⊢
      exact ⟨r, h, rfl⟩

theorem decodeNorm_guard {F : List (String × Json)} (hd : Distinct F) {g : Json} {G : VE.Formula} {c : Nat}
    (hg : VE.Norms.Wire.budgetFormula VE.Limits.maxDepth 0 g = .ok (G, c)) {N : VE.Norms.Node}
    (h : VE.Norms.Wire.decodeNorm (Json.mkObj [("norm", Json.mkObj F)]) false = .ok N) :
    VE.Norms.Wire.decodeNorm (Json.mkObj [("norm", Json.mkObj (F.map (mapPair "guard" (fun _ => g))))]) false =
      .ok { N with guard := G } := by
  unfold VE.Norms.Wire.decodeNorm at h ⊢
  obtain ⟨r, hr, h⟩ := VE.Kit.Except.bind_ok h
  rw [ok_bind (normFields_guard hd g hr)]
  obtain ⟨n, p, sg, gJ, u, o⟩ := r
  simp only at h ⊢
  obtain ⟨⟨G1, c1⟩, hb, h⟩ := VE.Kit.Except.bind_ok h
  rw [ok_bind hg]
  simp only [Bool.false_eq_true, ↓reduceIte] at h ⊢
  obtain ⟨r, hl, h⟩ := VE.Kit.Except.bind_ok h
  obtain ⟨r', hl', he⟩ := forIn_carve_count _ u [] c1 c hl
  rw [ok_bind hl']
  cases h
  simp only [he]; rfl

end VE.RightClauses
