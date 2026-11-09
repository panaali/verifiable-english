import VE.RightClauses.PlainWellFormed.Guards

/-! `plain` on the rights layer (8.3): the line instances of `plain D` are those of `D.doc` with only the norm guard
changed (`linesOf_plain`), so `checkRights` reads the same document (`checkRights_plain`) and `correlate (plain D)`
is `correlate D.doc` with the guards of its line nodes changed (`correlate_plain`). Proof vocabulary only. -/
namespace VE.RightClauses.PWF
open VE.Rights (RightsDoc SourceLine Line linesOf sourceLines holderSlot sortsOf lineAct rightOf)
open VE.SoftNorms (SoftNode)

/-- A line instance of `plain D`, read from the instance of `D.doc` it comes from. -/
def hL (D : ClauseDoc) (RN : String × Line) : String × Line :=
  (RN.1, { RN.2 with source := plainSource D.doc.soft D.lines RN.1 RN.2.source,
                     node := if RN.2.kind = .power then RN.2.node else
                       { RN.2.node with guard :=
                           ((plainSource D.doc.soft D.lines RN.1 RN.2.source).norm.map (·.guard)).getD RN.2.node.guard } })

theorem instancesOf_plain (D : ClauseDoc) (R : String) (S : SourceLine) (k : Nat) :
    VE.Rights.instancesOf R (plainSource D.doc.soft D.lines R S) k =
      (VE.Rights.instancesOf R S k).map (fun N => (hL D (R, N)).2) := by
  obtain ⟨g, hg⟩ := plainSource_eq D.doc.soft D.lines R S
  simp only [hL, hg]
  obtain ⟨kd, n, l, r, f, hs, cs⟩ := S
  cases kd <;> cases n <;> simp [VE.Rights.instancesOf] <;> split <;>
    simp [List.mapIdx_eq_zipIdx_map, Function.comp_def, hg]

theorem linesAux_plain (D : ClauseDoc) :
    ∀ (l : List (String × SourceLine)) (k : Nat),
    VE.Rights.linesAux (l.map (fun RS => (RS.1, plainSource D.doc.soft D.lines RS.1 RS.2))) k =
      (VE.Rights.linesAux l k).map (hL D)
  | [], _ => rfl
  | (R, S) :: rest, k => by
    obtain ⟨g, hg⟩ := plainSource_eq D.doc.soft D.lines R S
    have hf : VE.Rights.fanCount (plainSource D.doc.soft D.lines R S) = VE.Rights.fanCount S := by
      rw [hg, fanCount_plain]
    simp only [List.map_cons, VE.Rights.linesAux, List.map_append, List.map_map, hf, linesAux_plain D rest,
      instancesOf_plain]
    simp [Function.comp_def, hL]

theorem linesOf_plain (D : ClauseDoc) : linesOf (plain D) = (linesOf D.doc).map (hL D) := by
  unfold linesOf; rw [sourceLines_plain]; exact linesAux_plain D _ 0

/-! ### What `checkRights` reads -/

/-- A right of `plain D`. -/
def hR (D : ClauseDoc) (R : VE.Rights.Right) : VE.Rights.Right :=
  { R with lines := R.lines.map (plainSource D.doc.soft D.lines R.name) }

@[simp] theorem plain_soft (D : ClauseDoc) : (plain D).soft = D.doc.soft := rfl
@[simp] theorem plain_rights (D : ClauseDoc) : (plain D).rights = D.doc.rights := rfl
@[simp] theorem plain_limits (D : ClauseDoc) : (plain D).limits = D.doc.limits := rfl
@[simp] theorem plain_bars (D : ClauseDoc) : (plain D).bars = D.doc.bars := rfl
@[simp] theorem plain_outsideCites (D : ClauseDoc) : (plain D).outsideCites = D.doc.outsideCites := rfl
@[simp] theorem plain_sourceUnits (D : ClauseDoc) : (plain D).sourceUnits = D.doc.sourceUnits := rfl
theorem plain_rs (D : ClauseDoc) : (plain D).rs = D.doc.rs.map (hR D) := rfl
@[simp] theorem hR_name (D : ClauseDoc) (R : VE.Rights.Right) : (hR D R).name = R.name := rfl
@[simp] theorem hR_holder (D : ClauseDoc) (R : VE.Rights.Right) : (hR D R).holder = R.holder := rfl
@[simp] theorem hR_guard (D : ClauseDoc) (R : VE.Rights.Right) : (hR D R).guard = R.guard := rfl
@[simp] theorem hL_fst (D : ClauseDoc) (RN : String × Line) : (hL D RN).1 = RN.1 := rfl
@[simp] theorem hL_right (D : ClauseDoc) (RN : String × Line) : (hL D RN).2.right = RN.2.right := rfl
@[simp] theorem hL_kind (D : ClauseDoc) (RN : String × Line) : (hL D RN).2.kind = RN.2.kind := rfl
@[simp] theorem hL_ikind (D : ClauseDoc) (RN : String × Line) : (hL D RN).2.ikind = RN.2.ikind := rfl
@[simp] theorem hL_bearer (D : ClauseDoc) (RN : String × Line) : (hL D RN).2.bearer = RN.2.bearer := rfl
@[simp] theorem hL_name (D : ClauseDoc) (RN : String × Line) : (hL D RN).2.node.name = RN.2.node.name := by
  simp only [hL]; split <;> rfl
@[simp] theorem hL_pred (D : ClauseDoc) (RN : String × Line) : (hL D RN).2.node.pred = RN.2.node.pred := by
  simp only [hL]; split <;> rfl
@[simp] theorem hL_sign (D : ClauseDoc) (RN : String × Line) : (hL D RN).2.node.sign = RN.2.node.sign := by
  simp only [hL]; split <;> rfl
@[simp] theorem hL_carveOuts (D : ClauseDoc) (RN : String × Line) :
    (hL D RN).2.node.carveOuts = RN.2.node.carveOuts := by simp only [hL]; split <;> rfl
@[simp] theorem hL_over (D : ClauseDoc) (RN : String × Line) : (hL D RN).2.node.over = RN.2.node.over := by
  simp only [hL]; split <;> rfl
@[simp] theorem hL_mode (D : ClauseDoc) (RN : String × Line) : (hL D RN).2.node.mode = RN.2.node.mode := by
  simp only [hL]; split <;> rfl

theorem plainSource_fields (E : VE.SoftNorms.SoftDoc) (cl : List (String × String × CLine)) (R : String)
    (S : SourceLine) : (plainSource E cl R S).kind = S.kind ∧ (plainSource E cl R S).liberty = S.liberty ∧
      (plainSource E cl R S).recognition = S.recognition ∧ (plainSource E cl R S).fanOut = S.fanOut ∧
      (plainSource E cl R S).holderSlot = S.holderSlot ∧ (plainSource E cl R S).cites = S.cites ∧
      ((plainSource E cl R S).norm.map (·.name)) = S.norm.map (·.name) := by
  obtain ⟨g, hg⟩ := plainSource_eq E cl R S
  rw [hg]; cases S.norm <;> simp

@[simp] theorem hL_holderSlot (D : ClauseDoc) (RN : String × Line) :
    (hL D RN).2.source.holderSlot = RN.2.source.holderSlot := (plainSource_fields _ _ _ _).2.2.2.2.1
@[simp] theorem hL_liberty (D : ClauseDoc) (RN : String × Line) :
    (hL D RN).2.source.liberty = RN.2.source.liberty := (plainSource_fields _ _ _ _).2.1

theorem rightOf_plain' (D : ClauseDoc) (r : String) : rightOf (plain D) r = (rightOf D.doc r).map (hR D) := by
  simp [rightOf, plain_rs, List.find?_map, Function.comp_def]

@[simp] theorem sortsOf_hL (D : ClauseDoc) (RN : String × Line) : sortsOf (plain D) (hL D RN).2 = sortsOf D.doc RN.2 := by
  simp [sortsOf]

@[simp] theorem holderSlot_hL (D : ClauseDoc) (RN : String × Line) :
    holderSlot (plain D) (hL D RN).2 = holderSlot D.doc RN.2 := by
  unfold holderSlot
  simp only [hL_ikind, hL_holderSlot, sortsOf_hL, rightOf_plain', hL_right]
  cases rightOf D.doc RN.2.right <;> rfl

theorem checkSourceLine_plain (D : ClauseDoc) (R : VE.Rights.Right) (S : SourceLine) :
    VE.Rights.checkSourceLine (plain D) (hR D R) (plainSource D.doc.soft D.lines R.name S) =
      VE.Rights.checkSourceLine D.doc R S := by
  obtain ⟨g, hg⟩ := plainSource_eq D.doc.soft D.lines R.name S
  rw [hg]
  obtain ⟨kd, n, l, r, f, hs, cs⟩ := S
  cases n <;> rfl

theorem checkShape_plain (D : ClauseDoc) (R : VE.Rights.Right) (RN : String × Line) :
    VE.Rights.checkShape (plain D) (hR D R) (hL D RN).2 = VE.Rights.checkShape D.doc R RN.2 := by
  unfold VE.Rights.checkShape
  simp only [hL_name, hL_pred, hL_sign, hL_ikind, hL_holderSlot, hL_liberty, holderSlot_hL, hR_name, hR_holder]
  rfl

theorem authorNodes_plain (E : VE.SoftNorms.SoftDoc) (cl : List (String × String × CLine)) (R : String)
    (S : SourceLine) : (VE.Rights.authorNodes (plainSource E cl R S)).map (fun N => (N.name, N.over)) =
      (VE.Rights.authorNodes S).map (fun N => (N.name, N.over)) := by
  obtain ⟨g, hg⟩ := plainSource_eq E cl R S
  rw [hg]; obtain ⟨kd, n, l, r, f, hs, cs⟩ := S; cases n <;> simp [VE.Rights.authorNodes]

theorem limKeys_plain (D : ClauseDoc) : VE.Rights.limKeys (plain D) = VE.Rights.limKeys D.doc := by
  simp only [VE.Rights.limKeys, limActs_plain]; rfl
theorem condKeys_plain (D : ClauseDoc) : VE.Rights.condKeys (plain D) = VE.Rights.condKeys D.doc := by
  simp only [VE.Rights.condKeys, limActs_plain]; rfl

theorem permPreds_plain (D : ClauseDoc) : VE.Rights.permPreds (plain D) = VE.Rights.permPreds D.doc := by
  simp only [VE.Rights.permPreds, linesOf_plain, List.filterMap_map]
  congr 1; funext RN; simp [VE.Rights.libertyKind]

theorem genDecls_plain (D : ClauseDoc) : VE.Rights.genDecls (plain D) = VE.Rights.genDecls D.doc := by
  simp only [VE.Rights.genDecls, VE.Rights.limDecls, VE.Rights.condDecls, VE.Rights.aimedDecls, limKeys_plain,
    condKeys_plain, VE.Rights.barPreds, VE.Rights.barIndex, permPreds_plain, plain_soft, plain_bars]

theorem forIn_congr_key {α β ε : Type} (k : α → β) (f : α → PUnit → Except ε (ForInStep PUnit))
    (hf : ∀ a b, k a = k b → f a = f b) :
    ∀ (l1 l2 : List α), l1.map k = l2.map k → forIn l1 PUnit.unit f = forIn l2 PUnit.unit f
  | [], [], _ => rfl
  | a :: l1, b :: l2, h => by
    simp only [List.map_cons, List.cons.injEq] at h
    simp only [List.forIn_cons, hf a b h.1, forIn_congr_key k f hf l1 l2 h.2]
  | [], _ :: _, h | _ :: _, [], h => by simp at h

theorem forIn_congr_fun {α ε : Type} (l : List α) (f g : α → PUnit → Except ε (ForInStep PUnit))
    (h : ∀ a ∈ l, f a = g a) : forIn l PUnit.unit f = forIn l PUnit.unit g := by
  induction l with
  | nil => rfl
  | cons a l ih =>
    simp only [List.forIn_cons, h a (by simp), ih (fun b hb => h b (by simp [hb]))]

theorem authorNodes_over (D : ClauseDoc) (rs : List VE.Rights.Right) :
    (List.flatMap (fun a => List.flatMap VE.Rights.authorNodes (hR D a).lines) rs).map (fun N => (N.name, N.over)) =
      (List.flatMap (fun a => List.flatMap VE.Rights.authorNodes a.lines) rs).map (fun N => (N.name, N.over)) := by
  simp only [List.map_flatMap, hR, List.flatMap_map]
  congr 1; funext a; congr 1; funext S; exact authorNodes_plain _ _ _ _

theorem authorNodes_name (D : ClauseDoc) (rs : List VE.Rights.Right) :
    (List.flatMap (fun a => List.flatMap VE.Rights.authorNodes (hR D a).lines) rs).map (·.name) =
      (List.flatMap (fun a => List.flatMap VE.Rights.authorNodes a.lines) rs).map (·.name) := by
  have := congrArg (List.map Prod.fst) (authorNodes_over D rs)
  simpa [List.map_map, Function.comp_def] using this

@[simp] theorem hR_lines (D : ClauseDoc) (R : VE.Rights.Right) :
    (hR D R).lines = R.lines.map (plainSource D.doc.soft D.lines R.name) := rfl

@[simp] theorem plainSource_cites (E : VE.SoftNorms.SoftDoc) (cl : List (String × String × CLine)) (R : String)
    (S : SourceLine) : (plainSource E cl R S).cites = S.cites := (plainSource_fields _ _ _ _).2.2.2.2.2.1

theorem checkRights_plain (D : ClauseDoc) : VE.Rights.checkRights (plain D) = VE.Rights.checkRights D.doc := by
  unfold VE.Rights.checkRights
  simp only [plain_rs, linesOf_plain, List.map_map, List.flatMap_map, List.length_map,
    genDecls_plain, plain_soft, plain_rights, plain_limits, plain_bars, plain_outsideCites, plain_sourceUnits,
    hR_name, hR_holder, hR_guard, List.any_map, Function.comp_def, hL_fst, List.forIn_map, authorNodes_name]
  rw [forIn_congr_key (fun N : VE.SoftNorms.SoftNode => (N.name, N.over)) _ ?_ _
    (List.flatMap (fun a => List.flatMap VE.Rights.authorNodes a.lines) D.doc.rs ++ D.doc.soft.T.nodes)
    (by simp only [List.map_append, authorNodes_over])]
  rotate_left
  · intro a b h; have h2 : a.over = b.over := congrArg Prod.snd h; simp only [h2]
  simp only [hR_lines, List.forIn_map, checkSourceLine_plain, List.map_map, Function.comp_def, plainSource_cites]
  rw [forIn_congr_fun (linesOf D.doc) _ ?g ?h]
  · rfl
  case h =>
    intro RN _; funext y
    simp only [rightOf_plain']
    cases rightOf D.doc RN.1 with
    | none => rfl
    | some R => simp only [Option.map_some, checkShape_plain, hL_carveOuts, hL_name]

/-! ### `correlate (plain D)` -/

theorem holderConj_hL (D : ClauseDoc) (RN : String × Line) (G : VE.Formula) :
    VE.Rights.holderConj (plain D) (hL D RN).2 G = VE.Rights.holderConj D.doc RN.2 G := by
  unfold VE.Rights.holderConj
  simp only [rightOf_plain', hL_right, sortsOf_hL, holderSlot_hL]
  cases rightOf D.doc RN.2.right <;> rfl

@[simp] theorem lineAct_hL (D : ClauseDoc) (RN : String × Line) :
    lineAct (plain D) (hL D RN).2 = lineAct D.doc RN.2 := by simp [lineAct]

theorem limPackList_hL (D : ClauseDoc) (RN : String × Line) :
    VE.Rights.limPackList (plain D) (hL D RN).2 = VE.Rights.limPackList D.doc RN.2 := by
  have hs : VE.Rights.scopeLimits (plain D) (hL D RN).2 = VE.Rights.scopeLimits D.doc RN.2 := by
    simp [VE.Rights.scopeLimits, VE.Rights.inScope]
  simp only [VE.Rights.limPackList, VE.Rights.limPack, VE.Rights.limF, VE.Rights.limIndex, hs, limKeys_plain,
    lineAct_hL, sortsOf_hL]

/-- The new guard of a line node. -/
def newGuard (D : ClauseDoc) (RN : String × Line) : VE.Formula :=
  VE.Rights.holderConj D.doc RN.2 (hL D RN).2.node.guard

theorem nodeOf_hL (D : ClauseDoc) (RN : String × Line) :
    VE.Rights.nodeOf (plain D) (hL D RN).2 = { VE.Rights.nodeOf D.doc RN.2 with guard := newGuard D RN } := by
  unfold VE.Rights.nodeOf VE.Rights.ownGuard newGuard
  rw [holderConj_hL, limPackList_hL]
  simp only [hL]
  split <;> rfl

theorem barPreds_plain (D : ClauseDoc) : VE.Rights.barPreds (plain D) = VE.Rights.barPreds D.doc := by
  simp [VE.Rights.barPreds, permPreds_plain]

theorem lineNodes_plain (D : ClauseDoc) :
    VE.Rights.lineNodes (plain D) = (linesOf D.doc).map (fun RN => { VE.Rights.nodeOf D.doc RN.2 with guard := newGuard D RN }) := by
  simp only [VE.Rights.lineNodes, linesOf_plain, List.map_map, Function.comp_def, nodeOf_hL]

theorem barNodes_plain (D : ClauseDoc) : VE.Rights.barNodes (plain D) = VE.Rights.barNodes D.doc := by
  have hp : ∀ m, VE.Rights.posLineNames (plain D) m = VE.Rights.posLineNames D.doc m := by
    intro m
    unfold VE.Rights.posLineNames
    rw [lineNodes_plain]
    simp only [VE.Rights.lineNodes, List.filter_map, List.map_map, Function.comp_def]
  have hb : ∀ m, VE.Rights.barNode (plain D) m = VE.Rights.barNode D.doc m := by
    intro m
    simp only [VE.Rights.barNode, hp, VE.Rights.aimedF, VE.Rights.barIndex, barPreds_plain, plain_soft]
  have hb' : VE.Rights.barNode (plain D) = VE.Rights.barNode D.doc := funext hb
  simp only [VE.Rights.barNodes, VE.Rights.ruleReading, barPreds_plain, plain_bars, hb']

theorem envR_plain (D : ClauseDoc) : VE.Rights.envR (plain D) = VE.Rights.envR D.doc := by
  simp only [VE.Rights.envR, genDecls_plain, plain_soft]

/-- The nodes of `correlate (plain D)`. -/
def plainNodes (D : ClauseDoc) : List SoftNode :=
  (linesOf D.doc).map (fun RN => { VE.Rights.nodeOf D.doc RN.2 with guard := newGuard D RN }) ++
    D.doc.soft.T.nodes ++ VE.Rights.barNodes D.doc

/-- A soft document with other nodes. -/
def withNodes (C : VE.SoftNorms.SoftDoc) (ns : List SoftNode) : VE.SoftNorms.SoftDoc :=
  { C with T := { C.T with nodes := ns } }

theorem correlate_plain (D : ClauseDoc) :
    VE.Rights.correlate (plain D) = withNodes (VE.Rights.correlate D.doc) (plainNodes D) := by
  simp only [VE.Rights.correlate, withNodes, plainNodes, envR_plain, barNodes_plain, plain_soft, linesOf_plain,
    List.map_map, Function.comp_def, nodeOf_hL]

end VE.RightClauses.PWF
