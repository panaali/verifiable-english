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


theorem key_get {t : Std.TreeMap.Raw String Json compare} (ht : t.WF) {k : String} (h : k ∈ t.toList.map Prod.fst) :
    ∃ v, (Json.obj t).getObjVal? k = .ok v := by
  obtain ⟨⟨k', v⟩, hm, hk⟩ := List.mem_map.mp h
  simp only at hk; subst hk
  exact ⟨v, by rw [getObjVal_obj, (Std.TreeMap.Raw.mem_toList_iff_getElem?_eq_some ht).mp hm]⟩

theorem unitBody_none {u : Json} (h : unitBody u = none) (k : String) (hk : k = "right" ∨ k = "right_lines") :
    ∀ v, u.getObjVal? k ≠ .ok v := by
  intro v hv
  unfold unitBody at h
  rcases hk with rfl | rfl
  · simp [hv] at h
  · cases hr : u.getObjVal? "right" <;> simp [hr, hv] at h

set_option maxHeartbeats 400000 in
/-- A unit with no right body: `addUnit` adds nothing to the rights or the order, so it commutes with `plainUnits`. -/
theorem addUnit_plain_none (se : SoftEnvironment) (E : VE.SoftNorms.SoftDoc) (cl : List (String × String × CLine))
    (u0 : Json) (hwf : ∀ t, u0 = .obj t → t.WF) (hb : unitBody u0 = none) {acc acc' : Units}
    (h : addUnit se acc u0 = .ok acc') : addUnit se (plainUnits E cl acc) u0 = .ok (plainUnits E cl acc') := by
  cases u0 with
  | obj t =>
    have ht := hwf t rfl
    unfold addUnit at h ⊢
    simp only [VE.Bridge.fields, Json.getObj?, bind, Except.bind, pure, Except.pure] at h ⊢
    generalize hK : t.toList.map Prod.fst = K at h ⊢
    by_cases c1 : (K == ["source_units"]) = true
    · rw [if_pos c1] at h ⊢
      have hs : (plainUnits E cl acc).sourceUnits = acc.sourceUnits := rfl
      rw [hs]
      split at h <;> (try cases h)
      rename_i hsu
      rw [if_neg hsu]
      split at h <;> (try cases h)
      rfl
    rw [if_neg c1] at h ⊢
    by_cases c2 : (K == ["right"]) = true
    · exfalso; simp only [beq_iff_eq] at c2; subst c2
      obtain ⟨v, hv⟩ := key_get ht (k := "right") (by rw [hK]; simp)
      exact unitBody_none hb "right" (.inl rfl) v hv
    rw [if_neg c2] at h ⊢
    by_cases c3 : (K == ["right_lines"]) = true
    · exfalso; simp only [beq_iff_eq] at c3; subst c3
      obtain ⟨v, hv⟩ := key_get ht (k := "right_lines") (by rw [hK]; simp)
      exact unitBody_none hb "right_lines" (.inr rfl) v hv
    rw [if_neg c3] at h ⊢
    by_cases c4 : (K == ["limitation"]) = true
    · rw [if_pos c4] at h ⊢
      cases hL : VE.Rights.Wire.decodeLimitation ((Json.obj t).getObjValD "limitation") <;> simp only [hL] at h ⊢
      · cases h
      · cases h; rfl
    rw [if_neg c4] at h ⊢
    by_cases c5 : (K == ["bar"]) = true
    · rw [if_pos c5] at h ⊢
      cases hB : VE.Rights.Wire.decodeBar ((Json.obj t).getObjValD "bar") <;> simp only [hB] at h ⊢
      · cases h
      · cases h; rfl
    rw [if_neg c5] at h ⊢
    by_cases c6 : K.contains "norm" = true
    · rw [if_pos c6] at h ⊢
      revert h
      generalize VE.Bridge.displayFields (Json.obj t) ["norm"] ["cites"] = d
      generalize decodeLineNorm se ((Json.obj t).getObjValD "norm") none = dn
      generalize VE.Rights.Wire.optCites (Json.obj t) = dc
      cases d <;> cases dn <;> cases dc <;> intro h <;> first | (cases h; done) | (cases h; rfl)
    rw [if_neg c6] at h; cases h
  | _ => simp [addUnit, VE.Bridge.fields, Json.getObj?, bind, Except.bind, throw, throwThe, MonadExceptOf.throw] at h


/-- `addUnit` only appends to the source order. -/
theorem addUnit_order (se : SoftEnvironment) {acc acc' : Units} (u : Json) (h : addUnit se acc u = .ok acc') :
    ∃ t, acc'.order = acc.order ++ t := by
  unfold addUnit at h
  revert h
  cases VE.Bridge.fields u <;> simp only [bind, Except.bind, pure, Except.pure] <;> intro h
  · cases h
  rename_i fs
  generalize fs.map (fun x => x.fst) = K at h
  have nil : acc.order = acc.order ++ [] := (List.append_nil _).symm
  by_cases c1 : (K == ["source_units"]) = true
  · rw [if_pos c1] at h
    revert h; split <;> intro h
    · cases h
    · revert h; generalize VE.Bridge.strings _ = r; cases r <;> intro h <;> cases h; exact ⟨[], nil⟩
  rw [if_neg c1] at h
  by_cases c2 : (K == ["right"]) = true
  · rw [if_pos c2] at h
    revert h; generalize VE.Rights.Wire.decodeRight se _ = r; cases r <;> intro h <;> cases h; exact ⟨_, rfl⟩
  rw [if_neg c2] at h
  by_cases c3 : (K == ["right_lines"]) = true
  · rw [if_pos c3] at h
    revert h
    generalize VE.Bridge.displayFields _ _ _ = r1
    generalize VE.Bridge.stringField _ "right" = r2
    cases r1 <;> cases r2 <;> intro h
    · cases h
    · cases h
    · cases h
    rename_i rn
    simp only at h
    by_cases ha : (acc.rs.any fun x => x.name == rn) = true
    · rw [if_pos ha] at h
      revert h; generalize VE.Rights.Wire.decodeLines se _ = r3; cases r3 <;> intro h <;> cases h; exact ⟨_, rfl⟩
    · rw [if_neg ha] at h; cases h
  rw [if_neg c3] at h
  by_cases c4 : (K == ["limitation"]) = true
  · rw [if_pos c4] at h
    revert h; generalize VE.Rights.Wire.decodeLimitation _ = r; cases r <;> intro h <;> cases h; exact ⟨[], nil⟩
  rw [if_neg c4] at h
  by_cases c5 : (K == ["bar"]) = true
  · rw [if_pos c5] at h
    revert h; generalize VE.Rights.Wire.decodeBar _ = r; cases r <;> intro h <;> cases h; exact ⟨[], nil⟩
  rw [if_neg c5] at h
  by_cases c6 : K.contains "norm" = true
  · rw [if_pos c6] at h
    revert h
    generalize VE.Bridge.displayFields _ _ _ = r1
    generalize decodeLineNorm se _ none = r2
    generalize VE.Rights.Wire.optCites u = r3
    cases r1 <;> cases r2 <;> cases r3 <;> intro h <;> cases h; exact ⟨[], nil⟩
  rw [if_neg c6] at h; cases h

theorem foldl_order (se : SoftEnvironment) : ∀ (xs : List Json) (a : List (String × String × CLine) × Units) r,
    xs.foldlM (headStep se) a = .ok r → ∃ t, r.2.order = a.2.order ++ t
  | [], a, r, h => by cases h; exact ⟨[], (List.append_nil _).symm⟩
  | u :: xs, a, r, h => by
    simp only [List.foldlM_cons] at h
    obtain ⟨a1, h1, h⟩ := VE.Kit.Except.bind_ok h
    obtain ⟨t, ht⟩ := foldl_order se xs a1 r h
    unfold headStep at h1
    obtain ⟨_, -, h1⟩ := VE.Kit.Except.bind_ok h1
    obtain ⟨us, hus, h1⟩ := VE.Kit.Except.bind_ok h1
    cases h1
    obtain ⟨t', ht'⟩ := addUnit_order se _ hus
    exact ⟨t' ++ t, by rw [ht, ht', List.append_assoc]⟩


theorem unitBody_some {u : Json} {k : String} {b : Json} (h : unitBody u = some (k, b)) :
    (k = "right" ∨ k = "right_lines") ∧ u.getObjVal? k = .ok b := by
  unfold unitBody at h
  cases hr : u.getObjVal? "right" <;> cases hl : u.getObjVal? "right_lines" <;> simp [hr, hl] at h <;>
    obtain ⟨rfl, rfl⟩ := h <;> simp [hr, hl]

theorem dropKeys_wf (ks : List String) (u : Json) : ∀ t, dropKeys ks u = .obj t → t.WF := by
  intro t h
  cases u <;> simp only [dropKeys, Json.mkObj] at h <;> try cases h
  exact Std.TreeMap.Raw.WF.ofList

/-- The head's fold, read back by rights' fold over the plained units: the plained units. -/
theorem fold_plain (se : SoftEnvironment) (D : ClauseDoc) (hw : WellFormedClauses D = true) (hd : PlainOnWire D) :
    ∀ (xs : List Json) (a : List (String × String × CLine) × Units) r, xs.foldlM (headStep se) a = .ok r →
      (∀ RS ∈ r.2.order, RS ∈ VE.Rights.sourceLines D.doc) →
      (xs.map (mapUnit (plainLineJson D))).foldlM (addUnit se) (plainUnits D.doc.soft D.lines a.2) =
        .ok (plainUnits D.doc.soft D.lines r.2)
  | [], a, r, h, _ => by cases h; rfl
  | u :: xs, a, r, h, hr => by
    simp only [List.foldlM_cons, List.map_cons] at h ⊢
    obtain ⟨a1, h1, h⟩ := VE.Kit.Except.bind_ok h
    have ih := fold_plain se D hw hd xs a1 r h hr
    obtain ⟨t, ht⟩ := foldl_order se xs a1 r h
    unfold headStep at h1
    obtain ⟨_, -, h1⟩ := VE.Kit.Except.bind_ok h1
    obtain ⟨us, hus, h1⟩ := VE.Kit.Except.bind_ok h1
    cases h1
    have hmem : ∀ RS ∈ us.order, RS ∈ VE.Rights.sourceLines D.doc := fun RS hRS => hr RS (by rw [ht]; simp [hRS])
    have step : addUnit se (plainUnits D.doc.soft D.lines a.2) (mapUnit (plainLineJson D) u) =
        .ok (plainUnits D.doc.soft D.lines us) := by
      unfold mapUnit at hus ⊢
      dsimp only at hus ⊢
      cases hb : unitBody (dropKeys ["span"] u) with
      | none =>
        simp only [hb] at hus ⊢
        exact addUnit_plain_none se _ _ _ (dropKeys_wf _ u) hb hus
      | some kb =>
        obtain ⟨k, b⟩ := kb
        simp only [hb] at hus ⊢
        obtain ⟨hk, hkb⟩ := unitBody_some hb
        exact addUnit_plain se _ _ _ b k hk hkb _ _ hus fun l hl S hS hm =>
          plainLine_decode se D hw hd _ l hS (hmem _ hm)
    rw [ok_bind step]
    exact ih


/-- 8.5: the elaborated output carries none of the three keys and decodes under rights@0 to plain D. The hypothesis
    `hd` is the DRI's (reviews/dri-decisions-20261104-cmp-s3.md Q1 A1): a plain guard nests one level deeper than its
    line's guard, so W1's depth and node limits must admit it (`notChain` in Examples.lean). -/
theorem elaborate_plain (environment document : Lean.Json) (D : ClauseDoc)
    (h : decodeClauseDoc environment document = .ok D) (hw : WellFormedClauses D = true)
    (hset : NoReadingSets document)
    (hp : VE.Rights.WellFormedRights (plain D) = true) (hd : PlainOnWire D) :
  ∃ src, VE.Rights.Wire.decodeRightsSource (stripProfile environment) (elaborateJson D document) = .ok src ∧
    src.D = plain D := by
  unfold decodeClauseDoc at h
  obtain ⟨re, hre, h⟩ := VE.Kit.Except.bind_ok h
  unfold VE.Rights.Wire.decodeRightsSource
  rw [ok_bind hre]
  simp only [letFun] at h ⊢
  by_cases c1 : re.se.ne.rv.definitions = []
  case neg => simp [c1, throw, throwThe, MonadExceptOf.throw, bind, Except.bind, pure, Except.pure] at h
  by_cases c2 : re.se.ne.rv.flags = []
  case neg => simp [c1, c2, throw, throwThe, MonadExceptOf.throw, bind, Except.bind, pure, Except.pure] at h
  have e1 : re.se.ne.rv.definitions.isEmpty = true := by simp [c1]
  have e2 : re.se.ne.rv.flags.isEmpty = true := by simp [c2]
  rw [if_pos e1, if_pos e2] at h ⊢
  rw [pure_bind, pure_bind] at h ⊢
  cases document with
  | arr xs =>
    simp only [elaborateJson, mapDoc, pure_bind, Array.toList_map, List.length_map] at h ⊢
    by_cases c3 : xs.toList.length > 1024
    case pos => rw [if_pos c3] at h; cases h
    rw [if_neg c3] at h ⊢
    (try rw [pure_bind] at h); (try rw [pure_bind])
    obtain ⟨⟨lines, us⟩, hf, h⟩ := VE.Kit.Except.bind_ok h
    cases h
    have hfold := fold_plain re.se _ hw hd xs.toList ([], {}) (lines, us) hf (fun RS h => h)
    have hfold' : List.foldlM (addUnit re.se) ({} : Units) (xs.toList.map (mapUnit (plainLineJson _))) =
        .ok _ := hfold
    rw [ok_bind hfold']
    have hv : VE.Rights.validateRightsOnce (plain ⟨⟨⟨re.se.ne.rv.environment, re.se.ne.rv.literals, re.se.soft,
        ⟨re.se.ne.regulated, [], us.outside⟩⟩, re.block, us.rs, us.limits, us.bars, us.cites, some us.order,
        us.sourceUnits.getD []⟩, lines, []⟩) = .ok () := by
      rw [VE.Rights.validateRightsOnce_eq]
      unfold VE.Rights.WellFormedRights at hp
      split at hp
      · assumption
      · cases hp
    split
    · rename_i e heq; cases (heq.symm.trans hv)
    · exact ⟨_, rfl, rfl⟩
  | _ => simp [throw, throwThe, MonadExceptOf.throw, bind, Except.bind] at h


/-! ## `decode_unstructured` -/

theorem impl_map_congr {f g : String → Json → Json} :
    ∀ t : Std.DTreeMap.Internal.Impl String (fun _ => Json),
      (∀ p ∈ Std.DTreeMap.Internal.Impl.Const.toList t, f p.1 p.2 = g p.1 p.2) → t.map f = t.map g
  | .leaf, _ => rfl
  | .inner sz k v l r, h => by
    rw [Std.DTreeMap.Internal.Impl.Const.toList_eq_toListModel_map] at h
    simp only [Std.DTreeMap.Internal.Impl.toListModel, List.map_append, List.map_cons, List.mem_append,
      List.mem_cons] at h
    simp only [Std.DTreeMap.Internal.Impl.map]
    have hl := impl_map_congr l (fun p hp => h p (.inl (by
      rw [Std.DTreeMap.Internal.Impl.Const.toList_eq_toListModel_map] at hp; exact hp)))
    have hr := impl_map_congr r (fun p hp => h p (.inr (.inr (by
      rw [Std.DTreeMap.Internal.Impl.Const.toList_eq_toListModel_map] at hp; exact hp))))
    rw [hl, hr, h (k, v) (.inr (.inl rfl))]

theorem mapMember_congr (k : String) {F G : Json → Json} (j : Json)
    (h : ∀ p ∈ members j, p.1 = k → F p.2 = G p.2) : mapMember k F j = mapMember k G j := by
  cases j with
  | obj kvs =>
    simp only [mapMember]
    congr 1
    show (⟨⟨kvs.inner.inner.map _⟩⟩ : Std.TreeMap.Raw String Json compare) = ⟨⟨kvs.inner.inner.map _⟩⟩
    congr 2
    apply impl_map_congr
    intro p hp
    by_cases hk : p.1 = k
    · simp only [hk, beq_self_eq_true, ↓reduceIte]; exact h p hp hk
    · simp [hk]
  | _ => rfl

theorem mapArr_congr {f g : Json → Json} (v : Json) (h : ∀ l ∈ (match v with | .arr ls => ls.toList | _ => []),
    f l = g l) : mapArr f v = mapArr g v := by
  cases v with
  | arr ls => simp only [mapArr]; congr 1; exact Array.map_congr_left (fun l hl => h l (Array.mem_toList_iff.mpr hl))
  | _ => rfl

theorem lineWith_congr (l : Json) (h : ∀ kv ∈ members l, kv.1 ≠ "clauses" ∧ kv.1 ≠ "relation") :
    lineWith ["elided"] l = lineWith headKeys l := by
  unfold lineWith
  congr 2
  cases l with
  | obj kvs =>
    simp only [dropKeys]
    congr 1
    apply List.filter_congr
    intro kv hkv
    obtain ⟨h1, h2⟩ := h kv hkv
    simp [headKeys, h1, h2]
  | _ => rfl

theorem mapUnit_congr (u : Json) (h : ∀ kb ∈ members (dropKeys ["span"] u), (kb.1 = "right" ∨ kb.1 = "right_lines") →
    ∀ kl ∈ members kb.2, kl.1 = "lines" → ∀ l ∈ (match kl.2 with | .arr ls => ls.toList | _ => []),
      ∀ kv ∈ members l, kv.1 ≠ "clauses" ∧ kv.1 ≠ "relation") :
    mapUnit (fun _ => lineWith ["elided"]) u = mapUnit (fun _ => lineWith headKeys) u := by
  unfold mapUnit
  dsimp only
  cases hb : unitBody (dropKeys ["span"] u) with
  | none => rfl
  | some kb =>
    obtain ⟨k, b⟩ := kb
    obtain ⟨hk, -⟩ := unitBody_some hb
    apply mapMember_congr
    intro p hp hpk
    apply mapMember_congr
    intro q hq hqk
    apply mapArr_congr
    intro l hl
    exact lineWith_congr l (h p hp (hpk ▸ hk) q hq hqk l hl)


theorem getObjVal_member {j v : Json} {k : String} (h : j.getObjVal? k = .ok v) : (k, v) ∈ members j := by
  cases j with
  | obj kvs =>
    simp only [Json.getObjVal?] at h
    split at h
    · rename_i w hw; cases h; exact VE.Order.ProfileGate.impl_get_mem hw
    · cases h
  | _ => simp [Json.getObjVal?] at h <;> cases h

theorem filterMapM_loop_mem {α β : Type} (f : α → Except String (Option β)) :
    ∀ (as : List α) (bs : List β) (r : List β), List.filterMapM.loop f as bs = .ok r →
      ∀ x ∈ r, x ∈ bs ∨ ∃ a ∈ as, f a = .ok (some x)
  | [], bs, r, h, x, hx => by
    simp only [List.filterMapM.loop, pure, Except.pure, Except.ok.injEq] at h; subst h; exact .inl (by simpa using hx)
  | a :: as, bs, r, h, x, hx => by
    simp only [List.filterMapM.loop] at h
    obtain ⟨o, ho, h⟩ := VE.Kit.Except.bind_ok h
    cases o with
    | none =>
      rcases filterMapM_loop_mem f as bs r h x hx with hb | ⟨a', ha', hfa⟩
      · exact .inl hb
      · exact .inr ⟨a', by simp [ha'], hfa⟩
    | some b =>
      rcases filterMapM_loop_mem f as (b :: bs) r h x hx with hb | ⟨a', ha', hfa⟩
      · rcases List.mem_cons.mp hb with rfl | hb
        · exact .inr ⟨a, by simp, ho⟩
        · exact .inl hb
      · exact .inr ⟨a', by simp [ha'], hfa⟩

/-- An entry of the head comes from a line object of a unit's body, through `headLine`. -/
theorem headUnit_mem (se : SoftEnvironment) (u : Json) {ls : List (String × String × CLine)}
    (h : headUnit se u = .ok ls) : ∀ x ∈ ls, ∃ k b, unitBody (dropKeys ["span"] u) = some (k, b) ∧
      ∃ l ∈ bodyLines b, ∃ R span, headLine se R span l = .ok (some x) := by
  intro x hx
  unfold headUnit at h
  obtain ⟨span, -, h⟩ := VE.Kit.Except.bind_ok h
  cases hb : unitBody (dropKeys ["span"] u) with
  | none => simp only [hb, pure, Except.pure, Except.ok.injEq] at h; subst h; cases hx
  | some kb =>
    obtain ⟨k, b⟩ := kb
    simp only [hb] at h
    rcases filterMapM_loop_mem _ _ [] ls h x hx with hn | ⟨l, hl, hfl⟩
    · cases hn
    · exact ⟨k, b, rfl, l, hl, _, _, hfl⟩

theorem headLine_plainless (se : SoftEnvironment) (R : String) (span : Nat × Nat) (l : Json)
    {x : String × String × CLine} (h : headLine se R span l = .ok (some x))
    (hk : ∀ kv ∈ members l, kv.1 ≠ "clauses" ∧ kv.1 ≠ "relation") :
    x.2.2.clauses = [] ∧ x.2.2.relation = none := by
  have hc : ∀ v, l.getObjVal? "clauses" ≠ .ok v := fun v hv => (hk _ (getObjVal_member hv)).1 rfl
  have hr : ∀ v, l.getObjVal? "relation" ≠ .ok v := fun v hv => (hk _ (getObjVal_member hv)).2 rfl
  unfold headLine at h
  obtain ⟨S, -, h⟩ := VE.Kit.Except.bind_ok h
  cases hn : lineName S with
  | none => simp only [hn, pure, Except.pure] at h; cases h
  | some n =>
    simp only [hn] at h
    obtain ⟨el, -, h⟩ := VE.Kit.Except.bind_ok h
    obtain ⟨cs, hcs, h⟩ := VE.Kit.Except.bind_ok h
    obtain ⟨rel, hrel, h⟩ := VE.Kit.Except.bind_ok h
    simp only [pure, Except.pure, Except.ok.injEq, Option.some.injEq] at h
    subst h
    unfold decodeClauses at hcs
    unfold decodeRelationOpt at hrel
    cases hx : l.getObjVal? "clauses" with
    | ok v => exact absurd hx (hc v)
    | error e =>
      cases hy : l.getObjVal? "relation" with
      | ok v => exact absurd hy (hr v)
      | error e' =>
        rw [hx] at hcs; rw [hy] at hrel
        simp only [pure, Except.pure, Except.ok.injEq] at hcs hrel
        exact ⟨hcs.symm, hrel.symm⟩

theorem fold_snd (se : SoftEnvironment) : ∀ (xs : List Json) (a : List (String × String × CLine) × Units) r,
    xs.foldlM (headStep se) a = .ok r →
      (xs.map (mapUnit (fun _ => lineWith headKeys))).foldlM (addUnit se) a.2 = .ok r.2
  | [], a, r, h => by cases h; rfl
  | u :: xs, a, r, h => by
    simp only [List.foldlM_cons, List.map_cons] at h ⊢
    obtain ⟨a1, h1, h⟩ := VE.Kit.Except.bind_ok h
    unfold headStep at h1
    obtain ⟨_, -, h1⟩ := VE.Kit.Except.bind_ok h1
    obtain ⟨us, hus, h1⟩ := VE.Kit.Except.bind_ok h1
    cases h1
    rw [ok_bind hus]
    exact fold_snd se xs _ r h

theorem fold_lines (se : SoftEnvironment) (P : String × String × CLine → Prop) :
    ∀ (xs : List Json) (a : List (String × String × CLine) × Units) r,
      (∀ x ∈ a.1, P x) → (∀ u ∈ xs, ∀ ls, headUnit se u = .ok ls → ∀ x ∈ ls, P x) →
      xs.foldlM (headStep se) a = .ok r → ∀ x ∈ r.1, P x
  | [], a, r, ha, _, h => by cases h; exact ha
  | u :: xs, a, r, ha, hu, h => by
    simp only [List.foldlM_cons] at h
    obtain ⟨a1, h1, h⟩ := VE.Kit.Except.bind_ok h
    unfold headStep at h1
    obtain ⟨ls, hls, h1⟩ := VE.Kit.Except.bind_ok h1
    obtain ⟨us, -, h1⟩ := VE.Kit.Except.bind_ok h1
    cases h1
    refine fold_lines se P xs _ r (fun x hx => ?_) (fun u' hu' => hu u' (by simp [hu'])) h
    rcases List.mem_append.mp hx with hx | hx
    · exact ha x hx
    · exact hu u (by simp) ls hls x hx


theorem bodyLines_mem {b l : Json} (h : l ∈ bodyLines b) :
    ∃ kl ∈ members b, kl.1 = "lines" ∧ l ∈ (match kl.2 with | .arr ls => ls.toList | _ => []) := by
  unfold bodyLines at h
  split at h
  · rename_i ls hls; exact ⟨("lines", .arr ls), getObjVal_member hls, rfl, h⟩
  · cases h

/-- 8.5: with the three keys absent from every line, the head decodes what the rights route decodes under the list
    without right-clauses@0 (`stripProfile`), and every entry is unstructured. -/
theorem decode_unstructured (environment document : Lean.Json) (D : ClauseDoc)
    (h : decodeClauseDoc environment document = .ok D) (hk : NoClauseKeys document)
    (src : VE.Rights.Wire.RightsSource)
    (hs : VE.Rights.Wire.decodeRightsSource (stripProfile environment) (stripElided document) = .ok src) :
  src.D = D.doc ∧ ∀ x ∈ D.lines, x.2.2.clauses = [] ∧ x.2.2.relation = none := by
  unfold decodeClauseDoc at h
  obtain ⟨re, hre, h⟩ := VE.Kit.Except.bind_ok h
  unfold VE.Rights.Wire.decodeRightsSource at hs
  rw [ok_bind hre] at hs
  simp only [letFun] at h hs
  by_cases c1 : re.se.ne.rv.definitions = []
  case neg => simp [c1, throw, throwThe, MonadExceptOf.throw, bind, Except.bind, pure, Except.pure] at h
  by_cases c2 : re.se.ne.rv.flags = []
  case neg => simp [c1, c2, throw, throwThe, MonadExceptOf.throw, bind, Except.bind, pure, Except.pure] at h
  have e1 : re.se.ne.rv.definitions.isEmpty = true := by simp [c1]
  have e2 : re.se.ne.rv.flags.isEmpty = true := by simp [c2]
  rw [if_pos e1, if_pos e2] at h hs
  rw [pure_bind, pure_bind] at h hs
  cases document with
  | arr xs =>
    have hcong : xs.map (mapUnit (fun _ => lineWith ["elided"])) = xs.map (mapUnit (fun _ => lineWith headKeys)) :=
      Array.map_congr_left fun u hu => mapUnit_congr u (hk u (Array.mem_toList_iff.mpr hu))
    simp only [stripElided, mapDoc, hcong, pure_bind, Array.toList_map, List.length_map] at h hs
    by_cases c3 : xs.toList.length > 1024
    case pos => rw [if_pos c3] at h; cases h
    rw [if_neg c3] at h hs
    (try rw [pure_bind] at h); (try rw [pure_bind] at hs)
    obtain ⟨⟨lines, us⟩, hf, h⟩ := VE.Kit.Except.bind_ok h
    cases h
    rw [ok_bind (fold_snd re.se xs.toList ([], {}) (lines, us) hf)] at hs
    refine ⟨?_, fold_lines re.se _ xs.toList ([], {}) (lines, us) (by simp) (fun u hu ls hls x hx => ?_) hf⟩
    · split at hs
      · cases hs
      · cases hs; rfl
    · obtain ⟨k, b, hb, l, hl, R, span, hx⟩ := headUnit_mem re.se u hls x hx
      obtain ⟨hkk, hkb⟩ := unitBody_some hb
      obtain ⟨kl, hkl, hkl1, hlk⟩ := bodyLines_mem hl
      exact headLine_plainless re.se R span l hx
        (hk u hu (k, b) (getObjVal_member hkb) hkk kl hkl hkl1 l hlk)
  | _ => simp [throw, throwThe, MonadExceptOf.throw, bind, Except.bind] at h

/-- `PlainOnWire` as a check, for fixtures: W1's budgeted decoder reads every structured line's plain guard back. -/
def plainOnWireB (D : ClauseDoc) : Bool :=
  D.lines.all fun x => x.2.2.line.norm.toList.all fun N =>
    match VE.Norms.Wire.budgetFormula VE.Limits.maxDepth 0
        (enc (plainGuard (lineSorts D.doc.soft x.2.2.line).length N.guard x.2.2)) with
    | .ok (G, _) => decide (G = plainGuard (lineSorts D.doc.soft x.2.2.line).length N.guard x.2.2)
    | .error _ => false

/-- The check is sound: a document it passes meets `elaborate_plain`'s hypothesis `PlainOnWire`. -/
theorem plainOnWire_of_check {D : ClauseDoc} (h : plainOnWireB D = true) : PlainOnWire D := by
  intro x hx N hN
  simp only [plainOnWireB, List.all_eq_true] at h
  have h' := h x hx N hN
  split at h'
  · rename_i G c hres
    exact ⟨c, by rw [hres, of_decide_eq_true h']⟩
  · simp at h'

end VE.RightClauses
