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

end VE.RightClauses
