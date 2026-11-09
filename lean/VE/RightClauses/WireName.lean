import VE.RightClauses.WireDecode

/-! The rule name a decoded line has is the one its (rebuilt) norm object is written with, which `plainLineJson` reads
(`jsonLineName`): the soft decoder keeps the W1 node it decoded (`ruleFields_toNode`). -/
namespace VE.RightClauses
open Lean

theorem map_bind₂ {ε α β γ : Type} (Φ Ψ : β → γ) (x : Except ε α) {f : α → Except ε β}
    (h : ∀ a, Φ <$> f a = Ψ <$> f a) : Φ <$> (x >>= f) = Ψ <$> (x >>= f) := by
  cases x <;> simp [bind, Except.bind, h] <;> rfl

set_option maxRecDepth 20000 in
set_option maxHeartbeats 4000000 in
/-- The soft decoder returns the W1 node it decoded from the rule's W1 members, with its soft fields. -/
theorem ruleFields_toNode (x : Option String) (t : Std.TreeMap.Raw String Json compare) {R : VE.SoftNorms.SoftNode}
    (h : VE.SoftNorms.Phases.ruleFields x (Json.mkObj [("norm", Json.obj t)]) = .ok R) :
    VE.Norms.Wire.decodeNorm (Json.mkObj [("norm", Json.mkObj (t.toList.filter
      (fun kv => VE.SoftNorms.Phases.w1Keys.contains kv.fst)))]) false = .ok R.toNode := by
  have hf : VE.Bridge.fields (Json.obj t) = .ok t.toList := rfl
  have hn : ∀ r : Json, (Json.mkObj [("norm", r)]).getObjValD "norm" = r := fun r => by
    simp only [Json.getObjValD, getObjVal_single]; rfl
  unfold VE.SoftNorms.Phases.ruleFields at h
  rw [hn] at h
  simp only [letFun] at h
  rw [keysOf_norm, hf] at h
  by_cases hc : (Option.any (fun x => VE.SoftNorms.Phases.sameKeys x ["norm"]) (some ["norm"]) &&
      (VE.SoftNorms.Phases.keysOf (Json.obj t)).isSome) = true
  case neg => rw [if_neg hc] at h; cases h
  rw [if_pos hc, pure_bind] at h
  rw [ok_bind (rfl : VE.SoftNorms.Phases.inherited (Except.ok t.toList) = .ok _)] at h
  generalize t.toList = T at h ⊢
  by_cases hc2 : (VE.SoftNorms.Phases.w1Keys.all (List.map (fun x => x.fst) T).contains &&
      (List.map (fun x => x.fst) T).all fun k => VE.SoftNorms.Phases.w1Keys.contains k ||
        VE.SoftNorms.Phases.softKeys.contains k) = true
  case neg => rw [if_neg hc2] at h; cases h
  rw [if_pos hc2, pure_bind] at h
  obtain ⟨N1, hN1, h⟩ := VE.Kit.Except.bind_ok h
  have hN : VE.Norms.Wire.decodeNorm (Json.mkObj [("norm", Json.mkObj
      (T.filter (fun kv => VE.SoftNorms.Phases.w1Keys.contains kv.fst)))]) false = .ok N1 := by
    unfold VE.SoftNorms.Phases.inherited at hN1; split at hN1 <;> cases hN1; assumption
  rw [hN]
  have key : (fun R : VE.SoftNorms.SoftNode => R.toNode) <$> (Except.ok R : VE.SoftNorms.Phases.Check _) =
      (fun _ : VE.SoftNorms.SoftNode => N1) <$> (Except.ok R : VE.SoftNorms.Phases.Check _) := by
    rw [← h]
    clear h hN hN1 hc2 hc hn hf
    by_cases r1 : VE.Norms.ruleName N1.name = true
    case neg => rw [if_neg r1]; rfl
    rw [if_pos r1, pure_bind]
    by_cases r2 : N1.carveOuts.length > 8
    case pos => rw [if_pos r2]; rfl
    rw [if_neg r2, pure_bind]
    refine map_bind₂ _ _ _ fun _ => ?_
    repeat (first | rfl | (simp only [pure_bind]) | (refine map_bind₂ _ _ _ fun _ => ?_) | split)
  cases key; rfl


theorem normFields_name {j : Json} {r : String × String × Bool × Json × List Json × List String}
    (h : VE.Norms.Wire.normFields j = .ok r) : (j.getObjValD "norm").getObjValD "name" = .str r.1 := by
  unfold VE.Norms.Wire.normFields at h
  obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h
  obtain ⟨raw, hr, h⟩ := VE.Kit.Except.bind_ok h
  obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h
  have e : j.getObjValD "norm" = raw := by simp [Json.getObjValD, hr, Except.toOption]
  rw [e]
  cases hname : raw.getObjValD "name" with
  | str s =>
    rw [hname] at h
    have key : (fun r : String × String × Bool × Json × List Json × List String => r.1) <$>
        (Except.ok r : Except String _) = (fun _ => s) <$> (Except.ok r : Except String _) := by
      rw [← h]
      repeat (first | rfl | (simp only [pure_bind]) | (refine map_bind₂ _ _ _ fun _ => ?_) | split)
    cases key; rfl
  | _ => rw [hname] at h; cases h

theorem decodeNorm_name {j : Json} {sh : Bool} {N : VE.Norms.Node} (h : VE.Norms.Wire.decodeNorm j sh = .ok N) :
    (j.getObjValD "norm").getObjValD "name" = .str N.name := by
  unfold VE.Norms.Wire.decodeNorm at h
  obtain ⟨r, hr, h⟩ := VE.Kit.Except.bind_ok h
  rw [normFields_name hr]
  obtain ⟨n, p, sg, gJ, u, o⟩ := r
  have key : (fun N : VE.Norms.Node => N.name) <$> (Except.ok N : Except String _) =
      (fun _ => n) <$> (Except.ok N : Except String _) := by
    rw [← h]
    repeat (first | rfl | (simp only [pure_bind]) | (refine map_bind₂ _ _ _ fun _ => ?_) | split)
  cases key; rfl


set_option maxHeartbeats 2000000 in
/-- The soft decoder reads a rule only from an object. -/
theorem ruleFields_obj (x : Option String) (j : Json) {R : VE.SoftNorms.SoftNode}
    (h : VE.SoftNorms.Phases.ruleFields x (Json.mkObj [("norm", j)]) = .ok R) : ∃ t, j = .obj t := by
  have hn : ∀ r : Json, (Json.mkObj [("norm", r)]).getObjValD "norm" = r := fun r => by
    simp only [Json.getObjValD, getObjVal_single]; rfl
  unfold VE.SoftNorms.Phases.ruleFields at h
  rw [hn] at h
  simp only [letFun] at h
  rw [keysOf_norm] at h
  by_cases hc : (Option.any (fun x => VE.SoftNorms.Phases.sameKeys x ["norm"]) (some ["norm"]) &&
      (VE.SoftNorms.Phases.keysOf j).isSome) = true
  case neg => rw [if_neg hc] at h; cases h
  cases j <;> first | exact ⟨_, rfl⟩ | (simp [VE.SoftNorms.Phases.keysOf, VE.Bridge.fields, Json.getObj?, Functor.map,
    Except.map, throw, throwThe, MonadExceptOf.throw, Except.toOption, bind, Except.bind] at hc)

theorem getObjVal_obj (t : Std.TreeMap.Raw String Json compare) (k : String) :
    (Json.obj t).getObjVal? k = match t[k]? with | some v => .ok v | none => throw s!"property not found: {k}" := by
  simp only [Json.getObjVal?, Std.TreeMap.Raw.get?_eq_getElem?]; rfl

/-- W1's member list of a well-formed norm keeps its `name`. -/
theorem name_filter (t : Std.TreeMap.Raw String Json compare) (ht : t.WF) :
    (Json.mkObj (t.toList.filter (fun kv => VE.SoftNorms.Phases.w1Keys.contains kv.fst))).getObjValD "name" =
      (Json.obj t).getObjValD "name" := by
  have hd : Distinct (t.toList.filter (fun kv => VE.SoftNorms.Phases.w1Keys.contains kv.fst)) :=
    (Std.TreeMap.Raw.distinct_keys_toList ht).filter _
  unfold Json.getObjValD
  rw [getObjVal_obj]
  cases hv : t["name"]? with
  | some v =>
    have hm : ("name", v) ∈ t.toList := (Std.TreeMap.Raw.mem_toList_iff_getElem?_eq_some ht).mpr hv
    rw [getObjVal_mkObj_mem hd (List.mem_filter.mpr ⟨hm, by simp [VE.SoftNorms.Phases.w1Keys]⟩)]
  | none =>
    have hc : ((t.toList.filter (fun kv => VE.SoftNorms.Phases.w1Keys.contains kv.fst)).map Prod.fst).contains "name"
        = false := by
      apply Bool.eq_false_iff.mpr
      intro hc
      obtain ⟨⟨k, v⟩, hm, hk⟩ := List.mem_map.mp (List.contains_iff_mem.mp hc)
      simp only at hk; subst hk
      have := (Std.TreeMap.Raw.mem_toList_iff_getElem?_eq_some ht).mp (List.mem_filter.mp hm).1
      rw [hv] at this; cases this
    rw [getObjVal_mkObj_not hc]

theorem fault_ok {X : VE.SoftNorms.Phases.Check VE.SoftNorms.SoftNode} {N : VE.SoftNorms.SoftNode}
    (h : (match X with | .ok N => .ok N | .error f => .error f.message : Except String VE.SoftNorms.SoftNode) = .ok N) :
    X = .ok N := by
  cases X <;> simp_all

/-- The rule name a decoded (rebuilt) norm object carries is the decoded rule's. -/
theorem decodeLineNorm_name (se : VE.SoftNorms.Wire.SoftEnvironment) (t : Std.TreeMap.Raw String Json compare)
    (ht : t.WF) (fp : Option String) {N : VE.SoftNorms.SoftNode}
    (h : VE.Rights.Wire.decodeLineNorm se (.obj t) fp = .ok N) : (Json.obj t).getObjValD "name" = .str N.name := by
  unfold VE.Rights.Wire.decodeLineNorm at h
  obtain ⟨t', ht', hname, hr⟩ : ∃ t' : Std.TreeMap.Raw String Json compare, t'.WF ∧
      (Json.obj t').getObjValD "name" = (Json.obj t).getObjValD "name" ∧
      VE.SoftNorms.Phases.ruleFields se.soft.exceptionDecider (Json.mkObj [("norm", .obj t')]) = .ok N := by
    cases fp with
    | none => exact ⟨t, ht, rfl, fault_ok h⟩
    | some p =>
      cases hp : (Json.obj t).getObjVal? "predicate" with
      | ok _ => rw [hp] at h; exact ⟨t, ht, rfl, fault_ok h⟩
      | error _ =>
        rw [hp] at h
        refine ⟨t.insert "predicate" (.str p), ht.insert, ?_, fault_ok h⟩
        simp only [Json.getObjValD, getObjVal_obj, Std.TreeMap.Raw.getElem?_insert ht]
        rfl
  rw [← hname]
  have := decodeNorm_name (ruleFields_toNode _ t' hr)
  rw [show (Json.mkObj [("norm", Json.mkObj (t'.toList.filter
      (fun kv => VE.SoftNorms.Phases.w1Keys.contains kv.fst)))]).getObjValD "norm" = _ by
    simp only [Json.getObjValD, getObjVal_single]; rfl] at this
  rw [← name_filter t' ht']; exact this

end VE.RightClauses
