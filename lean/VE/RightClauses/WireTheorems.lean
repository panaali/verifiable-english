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


theorem mapM_forward {α β : Type} {g1 g2 : α → Except String β} {φ : β → β} :
    ∀ (xs : List α) (ys : List β), xs.mapM g1 = .ok ys →
      (∀ x ∈ xs, ∀ y ∈ ys, g1 x = .ok y → g2 x = .ok (φ y)) → xs.mapM g2 = .ok (ys.map φ)
  | [], ys, h, _ => by simp only [List.mapM_nil] at h ⊢; cases h; rfl
  | x :: xs, ys, h, hg => by
    simp only [List.mapM_cons] at h ⊢
    obtain ⟨y, hy, h⟩ := VE.Kit.Except.bind_ok h
    obtain ⟨ys', hys, h⟩ := VE.Kit.Except.bind_ok h
    cases h
    rw [ok_bind (hg x (by simp) y (by simp) hy),
      ok_bind (mapM_forward xs ys' hys fun x' hx y' hy' => hg x' (by simp [hx]) y' (by simp [hy']))]
    rfl

theorem decodeLines_plain (se : SoftEnvironment) (b : Json) (f1 f2 : Json → Json) (φ : VE.Rights.SourceLine →
    VE.Rights.SourceLine) {ls : List VE.Rights.SourceLine}
    (h : VE.Rights.Wire.decodeLines se (mapMember "lines" (mapArr f1) b) = .ok ls)
    (hl : ∀ l ∈ bodyLines b, ∀ S ∈ ls, decodeLine se (f1 l) = .ok S → decodeLine se (f2 l) = .ok (φ S)) :
    VE.Rights.Wire.decodeLines se (mapMember "lines" (mapArr f2) b) = .ok (ls.map φ) := by
  unfold VE.Rights.Wire.decodeLines at h ⊢
  rw [getObjVal_mapMember, if_pos rfl] at h ⊢
  unfold bodyLines at hl
  cases hb : b.getObjVal? "lines" with
  | error e => rw [hb] at h; cases h
  | ok v =>
    rw [hb] at h hl
    cases v with
    | arr xs =>
      simp only [Functor.map, Except.map, mapArr, bind, Except.bind, Json.getArr?, pure, Except.pure,
        Array.toList_map, List.mapM_map] at h ⊢
      exact mapM_forward _ _ h fun x hx y hy hxy => hl x hx y hy hxy
    | _ => simp [Functor.map, Except.map, mapArr, bind, Except.bind, Json.getArr?, throw, throwThe,
        MonadExceptOf.throw] at h

theorem decodeRight_plain (se : SoftEnvironment) (b : Json) (f1 f2 : Json → Json)
    (φ : String → VE.Rights.SourceLine → VE.Rights.SourceLine) {R : VE.Rights.Right}
    (h : VE.Rights.Wire.decodeRight se (mapMember "lines" (mapArr f1) b) = .ok R)
    (hl : ∀ l ∈ bodyLines b, ∀ S ∈ R.lines, decodeLine se (f1 l) = .ok S → decodeLine se (f2 l) = .ok (φ R.name S)) :
    VE.Rights.Wire.decodeRight se (mapMember "lines" (mapArr f2) b) =
      .ok { R with lines := R.lines.map (φ R.name) } := by
  unfold VE.Rights.Wire.decodeRight at h ⊢
  rw [displayFields_mapMember] at h ⊢
  simp only [VE.Bridge.stringField, getObjVal_mapMember_ne _ _ (show "name" ≠ "lines" by decide),
    getObjVal_mapMember_ne _ _ (show "holder" ≠ "lines" by decide),
    getObjVal_mapMember_ne _ _ (show "guard" ≠ "lines" by decide)] at h ⊢
  obtain ⟨_, hd, h⟩ := VE.Kit.Except.bind_ok h
  rw [ok_bind hd]
  obtain ⟨nm, hn, h⟩ := VE.Kit.Except.bind_ok h
  rw [ok_bind hn]
  obtain ⟨ho, hh, h⟩ := VE.Kit.Except.bind_ok h
  rw [ok_bind hh]
  rcases hgd : b.getObjVal? "guard" with e | gj <;> simp only [hgd] at h ⊢
  all_goals
    obtain ⟨g, hg, h⟩ := VE.Kit.Except.bind_ok h
    rw [ok_bind hg]
    obtain ⟨ls, hls, h⟩ := VE.Kit.Except.bind_ok h
    cases h
    rw [ok_bind (decodeLines_plain se b f1 f2 (φ nm) hls hl)]
    rfl


/-- The units decoded so far with every line through `plainSource` (what `plain` does to the document they build). -/
def plainUnits (E : VE.SoftNorms.SoftDoc) (cl : List (String × String × CLine)) (us : Units) : Units :=
  { us with rs := us.rs.map (fun R => { R with lines := R.lines.map (plainSource E cl R.name) }),
            order := us.order.map (fun RS => (RS.1, plainSource E cl RS.1 RS.2)) }

theorem decodeRight_name (se : SoftEnvironment) (j : Json) {R : VE.Rights.Right}
    (h : VE.Rights.Wire.decodeRight se j = .ok R) : VE.Bridge.stringField j "name" = .ok R.name := by
  unfold VE.Rights.Wire.decodeRight at h
  obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h
  obtain ⟨nm, hn, h⟩ := VE.Kit.Except.bind_ok h
  obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h
  rw [hn]
  rcases hgd : j.getObjVal? "guard" with e | gj <;> simp only [hgd] at h <;>
    (obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h; obtain ⟨_, -, h⟩ := VE.Kit.Except.bind_ok h; cases h; rfl)

theorem bodyRight_of (k : String) (b : Json) {r : String} (h : VE.Bridge.stringField b (if k == "right" then "name" else "right") = .ok r) :
    bodyRight k b = r := by
  unfold VE.Bridge.stringField at h
  obtain ⟨v, hv, hs⟩ := VE.Kit.Except.bind_ok h
  unfold bodyRight
  rw [getObjValD_of_ok hv, hs]; rfl


theorem any_plain (E : VE.SoftNorms.SoftDoc) (cl : List (String × String × CLine)) (us : Units) (r : String) :
    (plainUnits E cl us).rs.any (·.name == r) = us.rs.any (·.name == r) := by
  simp [plainUnits, List.any_map, Function.comp_def]

/-- One unit whose body's lines are rewritten: rights' `addUnit` on the plained lines adds the plained right or lines. -/
theorem addUnit_plain (se : SoftEnvironment) (E : VE.SoftNorms.SoftDoc) (cl : List (String × String × CLine))
    (u0 b : Json) (k : String) (hk : k = "right" ∨ k = "right_lines") (hb : u0.getObjVal? k = .ok b)
    (f1 f2 : Json → Json) {acc acc' : Units}
    (h : addUnit se acc (mapMember k (mapMember "lines" (mapArr f1)) u0) = .ok acc')
    (hl : ∀ l ∈ bodyLines b, ∀ S, decodeLine se (f1 l) = .ok S → (bodyRight k b, S) ∈ acc'.order →
      decodeLine se (f2 l) = .ok (plainSource E cl (bodyRight k b) S)) :
    addUnit se (plainUnits E cl acc) (mapMember k (mapMember "lines" (mapArr f2)) u0) =
      .ok (plainUnits E cl acc') := by
  obtain ⟨fs, hfs, hkm⟩ := VE.Order.ProfileGate.getObjVal_mem hb
  have hu : ∀ f, (mapMember k (mapMember "lines" (mapArr f)) u0).getObjValD k = mapMember "lines" (mapArr f) b :=
    fun f => by simp only [Json.getObjValD, getObjVal_mapMember, if_pos rfl, hb]; rfl
  have hne : ∀ f a, a ≠ k → (mapMember k (mapMember "lines" (mapArr f)) u0).getObjValD a = u0.getObjValD a :=
    fun f a ha => getObjValD_mapMember_ne _ _ ha
  unfold addUnit at h ⊢
  rw [fields_mapMember, hfs] at h ⊢
  simp only [Functor.map, Except.map, bind, Except.bind, map_fst_mapPair, List.map_map, fst_comp_mapPair] at h ⊢
  generalize hK : fs.map Prod.fst = K at h ⊢ hkm
  by_cases c1 : (K == ["source_units"]) = true
  · exfalso; simp only [beq_iff_eq] at c1; subst c1; rcases hk with rfl | rfl <;> simp at hkm
  rw [if_neg c1] at h ⊢
  by_cases c2 : (K == ["right"]) = true
  · rw [if_pos c2] at h ⊢
    simp only [beq_iff_eq] at c2; subst c2
    have hk' : k = "right" := by simpa using hkm
    subst hk'
    rw [hu f1] at h; rw [hu f2]
    cases hR : VE.Rights.Wire.decodeRight se (mapMember "lines" (mapArr f1) b) with
    | error e => rw [hR] at h; cases h
    | ok R =>
      rw [hR] at h; simp only [pure, Except.pure, Except.ok.injEq] at h; subst h
      have hn : bodyRight "right" b = R.name := bodyRight_of _ _ (by
        have := decodeRight_name se _ hR
        simp only [VE.Bridge.stringField, getObjVal_mapMember_ne _ _ (show "name" ≠ "lines" by decide)] at this
        simpa using this)
      rw [decodeRight_plain se b f1 f2 (plainSource E cl) hR (fun l hlb S hS hd => by
        rw [← hn]; exact hl l hlb S hd (by simp [hn, hS]))]
      simp only [plainUnits, List.map_append, List.map_cons, List.map_nil, List.map_map]
      rfl
  rw [if_neg c2] at h ⊢
  by_cases c3 : (K == ["right_lines"]) = true
  · rw [if_pos c3] at h ⊢
    simp only [beq_iff_eq] at c3; subst c3
    have hk' : k = "right_lines" := by simpa using hkm
    subst hk'
    rw [hu f1] at h; rw [hu f2, displayFields_mapMember]
    rw [displayFields_mapMember] at h
    simp only [VE.Bridge.stringField, getObjVal_mapMember_ne _ _ (show "right" ≠ "lines" by decide)] at h ⊢
    cases hD : VE.Bridge.displayFields b ["right", "lines"] [] with
    | error e => rw [hD] at h; cases h
    | ok _ =>
      simp only [hD] at h ⊢
      cases hr : (b.getObjVal? "right" >>= fun x => x.getStr?) with
      | error e => rw [hr] at h; cases h
      | ok r =>
        simp only [hr] at h ⊢
        rw [any_plain]
        by_cases ha : (acc.rs.any fun x => x.name == r) = true
        case neg => rw [if_neg ha] at h; cases h
        rw [if_pos ha] at h ⊢
        simp only [pure, Except.pure] at h ⊢
        cases hls : VE.Rights.Wire.decodeLines se (mapMember "lines" (mapArr f1) b) with
        | error e => rw [hls] at h; cases h
        | ok ls =>
          rw [hls] at h; simp only [Except.ok.injEq] at h; subst h
          have hn : bodyRight "right_lines" b = r := bodyRight_of _ _ (by simpa [VE.Bridge.stringField] using hr)
          rw [decodeLines_plain se b f1 f2 (plainSource E cl r) hls (fun l hlb S hS hd => by
            rw [← hn]; exact hl l hlb S hd (by simp [hn, hS]))]
          simp only [plainUnits, List.map_map, List.map_append, Except.ok.injEq, Units.mk.injEq]
          refine ⟨List.map_congr_left fun R _ => ?_, trivial, trivial, trivial, trivial, ?_, trivial⟩
          · by_cases hRn : (R.name == r) = true
            · simp only [Function.comp, hRn, ↓reduceIte, List.map_append]
              simp only [beq_iff_eq] at hRn; rw [hRn]
            · simp only [Function.comp, hRn, ↓reduceIte, Bool.false_eq_true]
          · rfl
  rw [if_neg c3] at h ⊢
  have n1 : "limitation" ≠ k := by rcases hk with rfl | rfl <;> decide
  have n2 : "bar" ≠ k := by rcases hk with rfl | rfl <;> decide
  have n3 : "norm" ≠ k := by rcases hk with rfl | rfl <;> decide
  have n4 : "cites" ≠ k := by rcases hk with rfl | rfl <;> decide
  simp only [hne f1 _ n1, hne f1 _ n2, hne f1 _ n3, displayFields_mapMember, VE.Rights.Wire.optCites,
    getObjVal_mapMember_ne _ _ n4] at h
  simp only [hne f2 _ n1, hne f2 _ n2, hne f2 _ n3, displayFields_mapMember, VE.Rights.Wire.optCites,
    getObjVal_mapMember_ne _ _ n4]
  by_cases c4 : (K == ["limitation"]) = true
  · rw [if_pos c4] at h ⊢
    cases hL : VE.Rights.Wire.decodeLimitation (u0.getObjValD "limitation") <;> simp only [hL] at h ⊢
    · cases h
    · simp only [pure, Except.pure, Except.ok.injEq] at h ⊢; subst h; rfl
  rw [if_neg c4] at h ⊢
  by_cases c5 : (K == ["bar"]) = true
  · rw [if_pos c5] at h ⊢
    cases hB : VE.Rights.Wire.decodeBar (u0.getObjValD "bar") <;> simp only [hB] at h ⊢
    · cases h
    · simp only [pure, Except.pure, Except.ok.injEq] at h ⊢; subst h; rfl
  rw [if_neg c5] at h ⊢
  by_cases c6 : K.contains "norm" = true
  · rw [if_pos c6] at h ⊢
    cases hD : VE.Bridge.displayFields u0 ["norm"] ["cites"] <;> simp only [hD] at h ⊢
    · cases h
    cases hN : decodeLineNorm se (u0.getObjValD "norm") none <;> simp only [hN] at h ⊢
    · cases h
    cases hC : u0.getObjVal? "cites" <;> simp only [hC] at h ⊢
    all_goals first
      | (simp only [pure, Except.pure, Except.ok.injEq] at h ⊢; subst h; rfl)
      | (cases hc : VE.Rights.Wire.decodeCites _ <;> simp only [hc] at h ⊢ <;>
          first | (cases h; done) | (cases h; rfl))
  rw [if_neg c6] at h; cases h

end VE.RightClauses
