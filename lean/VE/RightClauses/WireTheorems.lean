import VE.RightClauses.WireName

/-! 8.5's statements (docs/spec/right-clauses.md): `decode_unstructured` and `elaborate_plain`, the latter with the DRI's
signed hypothesis `PlainOnWire` (reviews/dri-decisions-20261104-cmp-s3.md Q1 A1). -/
namespace VE.RightClauses
open Lean
open VE.Rights.Wire (decodeRightsEnvironment decodeLine decodeLineNorm addUnit Units)
open VE.SoftNorms.Wire (SoftEnvironment enc)

theorem decodeLineNorm_guard (se : SoftEnvironment) (L : List (String × Json)) {g : Json} {G : VE.Formula} {c : Nat}
    (hg : VE.Norms.Wire.budgetFormula VE.Limits.maxDepth 0 g = .ok (G, c)) {N : VE.SoftNorms.SoftNode}
    (h : decodeLineNorm se (Json.mkObj L) none = .ok N) :
    decodeLineNorm se (mapMember "guard" (fun _ => g) (Json.mkObj L)) none = .ok { N with guard := G } := by
  unfold decodeLineNorm at h ⊢
  dsimp only at h ⊢
  cases hN : VE.SoftNorms.Phases.ruleFields se.soft.exceptionDecider (Json.mkObj [("norm", Json.mkObj L)]) with
  | error e => rw [hN] at h; cases h
  | ok N' => rw [hN] at h; cases h; rw [ruleFields_guard _ L hg hN]

theorem decodeLine_guard (se : SoftEnvironment) (l : Json) {L : List (String × Json)}
    (hn : l.getObjVal? "norm" = .ok (Json.mkObj L)) {g : Json} {G : VE.Formula} {c : Nat}
    (hg : VE.Norms.Wire.budgetFormula VE.Limits.maxDepth 0 g = .ok (G, c)) {S : VE.Rights.SourceLine}
    (h : decodeLine se l = .ok S) (hf : S.fanOut = []) :
    decodeLine se (mapMember "norm" (mapMember "guard" (fun _ => g)) l) =
      .ok { S with norm := S.norm.map (fun N => { N with guard := G }) } := by
  have ne : ∀ a, a ≠ "norm" → (mapMember "norm" (mapMember "guard" (fun _ => g)) l).getObjVal? a = l.getObjVal? a :=
    fun a ha => getObjVal_mapMember_ne _ _ ha
  have hn2 : (mapMember "norm" (mapMember "guard" (fun _ => g)) l).getObjVal? "norm" =
      .ok (mapMember "guard" (fun _ => g) (Json.mkObj L)) := by
    rw [getObjVal_mapMember, if_pos rfl, hn]; rfl
  unfold decodeLine at h ⊢
  rw [displayFields_mapMember]
  rw [getObjValD_mapMember_ne _ _ (show "kind" ≠ "norm" by decide)]
  simp only [ne "fan_out" (by decide), ne "holder_slot" (by decide),
    ne "liberty" (by decide), ne "recognition" (by decide), hn2, VE.Rights.Wire.optCites, ne "cites" (by decide)]
  simp only [hn, VE.Rights.Wire.optCites] at h
  obtain ⟨_, hd, h⟩ := VE.Kit.Except.bind_ok h
  rw [ok_bind hd]
  obtain ⟨kind, hk, h⟩ := VE.Kit.Except.bind_ok h
  rw [ok_bind hk]
  cases hfo : l.getObjVal? "fan_out" <;> cases hhs : l.getObjVal? "holder_slot" <;> simp only [hfo, hhs] at h ⊢
  all_goals
    repeat (obtain ⟨_, _, h⟩ := VE.Kit.Except.bind_ok h)
    cases h
    simp only at hf
    try subst hf
    simp only [List.head?_nil, Option.map_none] at *
    have hnm := ‹some <$> decodeLineNorm se (Json.mkObj L) none = _›
    cases hd : decodeLineNorm se (Json.mkObj L) none with
    | error e => rw [hd] at hnm; cases hnm
    | ok N =>
      rw [hd] at hnm; cases hnm
      have h2 := decodeLineNorm_guard se L hg hd
      simp only [bind, Except.bind, Functor.map, Except.map, pure, Except.pure, List.head?_nil, Option.map_none] at *
      try simp only [Except.ok.injEq] at *
      try subst_vars
      try simp only [List.head?_nil, Option.map_none] at *
      try simp only [List.head?_nil, Option.map_none, h2]
      try simp only [List.head?, Option.map, h2]
      try simp only [*]
      try rfl


theorem getObjValD_of_ok {j v : Json} {k : String} (h : j.getObjVal? k = .ok v) : j.getObjValD k = v := by
  simp [Json.getObjValD, h, Except.toOption]

theorem getObjValD_of_error {j : Json} {k e : String} (h : j.getObjVal? k = .error e) : j.getObjValD k = .null := by
  simp [Json.getObjValD, h, Except.toOption]

theorem null_name : ((Json.null.getObjValD "name").getStr?).toOption = none := rfl

theorem str_name (v : Json) (s : String) (h : v.getObjValD "name" = .str s) :
    ((v.getObjValD "name").getStr?).toOption = some s := by rw [h]; rfl

theorem some_map_ok {ε α : Type} {x : Except ε α} {w : Option α} (h : some <$> x = .ok w) :
    ∃ a, x = .ok a ∧ w = some a := by
  cases x <;> simp_all [Functor.map, Except.map]

/-- A norm or liberty member decoded from a well-formed object, or from no object at all, names the rule it is
    written with. -/
theorem member_name (se : SoftEnvironment) (v : Json) (hv : ∀ t, v = .obj t → t.WF) (fp : Option String)
    {N : VE.SoftNorms.SoftNode} (h : decodeLineNorm se v fp = .ok N) : v.getObjValD "name" = .str N.name := by
  cases v with
  | obj t => exact decodeLineNorm_name se t (hv t rfl) fp h
  | _ =>
    exfalso
    unfold decodeLineNorm at h
    cases fp <;> simp only [Json.getObjVal?] at h <;> split at h <;> (try cases h) <;>
      (rename_i heq; obtain ⟨t, ht⟩ := ruleFields_obj _ _ heq; cases ht)

/-- The rebuilt members of a line decoded by rights' `decodeLine`: `jsonLineName` is the decoded `lineName`. -/
theorem decodeLine_name (se : SoftEnvironment) (l : Json)
    (hn : ∀ v, l.getObjVal? "norm" = .ok v → ∀ t, v = .obj t → t.WF)
    (hl : ∀ v, l.getObjVal? "liberty" = .ok v → ∀ t, v = .obj t → t.WF)
    {S : VE.Rights.SourceLine} (h : decodeLine se l = .ok S) : jsonLineName l = lineName S := by
  unfold decodeLine at h
  obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h
  obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h
  unfold jsonLineName lineName
  rcases hfo : l.getObjVal? "fan_out" with e1 | v1 <;> cases hhs : l.getObjVal? "holder_slot" <;>
    simp only [hfo, hhs] at h
  case' ok.error => obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h
  case' ok.ok => obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h
  all_goals
    obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h
    obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h
    obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h
    obtain ⟨wn, hnn, h⟩ := VE.Kit.Except.bind_ok h
    obtain ⟨wl, hll, h⟩ := VE.Kit.Except.bind_ok h
    obtain ⟨wr, -, h⟩ := VE.Kit.Except.bind_ok h
    cases h
    rcases hN : l.getObjVal? "norm" with eN | vN <;> rcases hL : l.getObjVal? "liberty" with eL | vL <;>
      simp only [hN, hL] at hnn hll
    · simp only [pure, Except.pure, Except.ok.injEq] at hnn hll; subst hnn hll
      rw [getObjValD_of_error hN, getObjValD_of_error hL, null_name]; rfl
    · simp only [pure, Except.pure, Except.ok.injEq] at hnn; subst hnn
      obtain ⟨N', hd', rfl⟩ := some_map_ok hll
      rw [getObjValD_of_error hN, getObjValD_of_ok hL, null_name, str_name _ _ (member_name se _ (hl _ hL) _ hd')]; rfl
    · simp only [pure, Except.pure, Except.ok.injEq] at hll; subst hll
      obtain ⟨N, hd, rfl⟩ := some_map_ok hnn
      rw [getObjValD_of_ok hN, str_name _ _ (member_name se _ (hn _ hN) _ hd)]; rfl
    · obtain ⟨N, hd, rfl⟩ := some_map_ok hnn
      obtain ⟨N', hd', rfl⟩ := some_map_ok hll
      rw [getObjValD_of_ok hN, str_name _ _ (member_name se _ (hn _ hN) _ hd)]; rfl

end VE.RightClauses
