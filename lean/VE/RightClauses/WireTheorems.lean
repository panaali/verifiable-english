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


theorem rebuild_wf (v : Json) : ∀ t, rebuild v = .obj t → t.WF := by
  intro t h
  cases v <;> simp only [rebuild, Json.mkObj] at h <;> try cases h
  exact Std.TreeMap.Raw.WF.ofList

theorem lineWith_norm (ks : List String) (l : Json) :
    (lineWith ks l).getObjVal? "norm" = rebuild <$> (dropKeys ks l).getObjVal? "norm" := by
  unfold lineWith
  rw [getObjVal_mapMember_ne _ _ (by decide), getObjVal_mapMember, if_pos rfl]

theorem lineWith_liberty (ks : List String) (l : Json) :
    (lineWith ks l).getObjVal? "liberty" = rebuild <$> (dropKeys ks l).getObjVal? "liberty" := by
  unfold lineWith
  rw [getObjVal_mapMember, if_pos rfl, getObjVal_mapMember_ne _ _ (by decide)]

theorem lineWith_wf (ks : List String) (l : Json) (k : String) (hk : k = "norm" ∨ k = "liberty") :
    ∀ v, (lineWith ks l).getObjVal? k = .ok v → ∀ t, v = .obj t → t.WF := by
  intro v hv t ht
  rcases hk with rfl | rfl
  · rw [lineWith_norm] at hv
    cases hx : (dropKeys ks l).getObjVal? "norm" <;> rw [hx] at hv <;> cases hv; exact rebuild_wf _ t ht
  · rw [lineWith_liberty] at hv
    cases hx : (dropKeys ks l).getObjVal? "liberty" <;> rw [hx] at hv <;> cases hv; exact rebuild_wf _ t ht

theorem decodeLineNorm_obj (se : SoftEnvironment) (v : Json) (fp : Option String) {N : VE.SoftNorms.SoftNode}
    (h : decodeLineNorm se v fp = .ok N) : ∃ t, v = .obj t := by
  cases v with
  | obj t => exact ⟨t, rfl⟩
  | _ =>
    exfalso
    unfold decodeLineNorm at h
    cases fp <;> simp only [Json.getObjVal?] at h <;> split at h <;> (try cases h) <;>
      (rename_i heq; obtain ⟨t, ht⟩ := ruleFields_obj _ _ heq; cases ht)

/-- The norm a decoded line carries was decoded from its `norm` member. -/
theorem decodeLine_norm (se : SoftEnvironment) (l : Json) {S : VE.Rights.SourceLine} (h : decodeLine se l = .ok S)
    {N : VE.SoftNorms.SoftNode} (hN : S.norm = some N) :
    ∃ v fp, l.getObjVal? "norm" = .ok v ∧ decodeLineNorm se v fp = .ok N := by
  unfold decodeLine at h
  obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h
  obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h
  rcases hfo : l.getObjVal? "fan_out" with e1 | v1 <;> cases hhs : l.getObjVal? "holder_slot" <;>
    simp only [hfo, hhs] at h
  case' ok.error => obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h
  case' ok.ok => obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h
  all_goals
    obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h
    obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h
    obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h
    obtain ⟨wn, hnn, h⟩ := VE.Kit.Except.bind_ok h
    obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h
    obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h
    cases h
    simp only at hN
    subst hN
    rcases hv : l.getObjVal? "norm" with e | v <;> simp only [hv] at hnn
    · cases hnn
    · obtain ⟨N', hd, he⟩ := some_map_ok hnn
      cases he
      exact ⟨v, _, rfl, hd⟩

theorem with_norm_eq (S : VE.Rights.SourceLine) {n : Option VE.SoftNorms.SoftNode} (h : S.norm = n) :
    { S with norm := n } = S := by
  cases S; simp only at h; simp [h]

/-- One line of right `R` through `plainLineJson` decodes as `plainSource` of its decoded line. -/
theorem plainLine_decode (se : SoftEnvironment) (D : ClauseDoc) (hw : WellFormedClauses D = true)
    (hd : PlainOnWire D) (R : String) (l : Json) {S : VE.Rights.SourceLine}
    (hS : decodeLine se (lineWith headKeys l) = .ok S) (hm : (R, S) ∈ VE.Rights.sourceLines D.doc) :
    decodeLine se (plainLineJson D R l) = .ok (plainSource D.doc.soft D.lines R S) := by
  have hname := decodeLine_name se _ (lineWith_wf _ l "norm" (.inl rfl)) (lineWith_wf _ l "liberty" (.inr rfl)) hS
  have hfind : (lineName S).bind (fun n => D.lines.find? (fun x => x.1 == R && x.2.1 == n)) =
      D.lines.find? (fun x => x.1 == R && some x.2.1 == lineName S) := by
    cases lineName S with
    | none => simp only [Option.bind]; exact (List.find?_eq_none.2 (fun _ _ => by simp)).symm
    | some n => simp [Option.bind]
  unfold plainLineJson plainSource
  dsimp only
  rw [hname, hfind]
  cases hx : D.lines.find? (fun x => x.1 == R && some x.2.1 == lineName S) with
  | none => exact hS
  | some x =>
    obtain ⟨R', n, L⟩ := x
    have hxm := List.mem_of_find?_eq_some hx
    have hp := List.find?_some hx
    simp only [Bool.and_eq_true, beq_iff_eq] at hp
    obtain ⟨rfl, hn⟩ := hp
    obtain ⟨hsh, -, -, hsrc, -⟩ := entry_facts D hw R' n L hxm
    have hSL : S = L.line := by
      have : (R', S) ∈ (VE.Rights.sourceLines D.doc).filter (fun RS => lineName RS.2 == some n) :=
        List.mem_filter.2 ⟨hm, by simp [← hn]⟩
      rw [hsrc] at this; simpa using this
    subst hSL
    dsimp only
    cases hN : L.line.norm with
    | none =>
      dsimp only
      rw [hS]; congr 1
      simp only [hN, Option.map_none]
      exact (with_norm_eq L.line hN).symm
    | some N =>
      dsimp only
      by_cases he : (L.clauses.isEmpty && L.relation.isNone) = true
      · rw [if_pos he, hS]
        simp only [Bool.and_eq_true, List.isEmpty_iff, Option.isNone_iff_eq_none] at he
        congr 1
        simp only [plainGuard, he.1, he.2, List.map_nil, Option.toList_none, List.append_nil, List.foldl_nil]
        exact (with_norm_eq L.line hN).symm
      · rw [if_neg he]
        obtain ⟨v, fp, hv, hdv⟩ := decodeLine_norm se _ hS hN
        obtain ⟨t, rfl⟩ := decodeLineNorm_obj se v fp hdv
        rw [lineWith_norm] at hv
        cases hr : (dropKeys headKeys l).getObjVal? "norm" with
        | error e => rw [hr] at hv; cases hv
        | ok raw0 =>
          rw [hr] at hv
          cases raw0 with
          | obj kvs =>
            have hv' : (lineWith headKeys l).getObjVal? "norm" = .ok (Json.mkObj kvs.toList) := by
              rw [lineWith_norm, hr]; rfl
            have hf : L.line.fanOut = [] := by
              simp only [shapeOk, he, Bool.false_or, Bool.and_eq_true, List.isEmpty_iff] at hsh
              exact hsh.1.2
            obtain ⟨c, hg⟩ := hd _ hxm N (by simp [hN])
            rw [decodeLine_guard se _ hv' hg hS hf, hN]
            rfl
          | _ => cases hv

end VE.RightClauses
