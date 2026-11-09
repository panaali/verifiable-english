import VE.RightClauses.PlainWellFormed.Lines

/-! The soft builders under a change of guards (8.3, `plain_wellFormed`): `mapG γ C` changes each node's guard by
`γ` (its name and old guard), and every formula soft-norms builds from the nodes (strict selection, eligibility,
dominance, the derived carve-out) changes by `FExt` at the predicate's context. Proof vocabulary only. -/
namespace VE.RightClauses.PWF
open VE.SoftNorms (SoftNode SoftDoc)
open VE.Norms (anyF)

variable (γ : String → VE.Formula → VE.Formula)

/-- A node with its guard changed by `γ`. -/
def setG (N : SoftNode) : SoftNode := { N with guard := γ N.name N.guard }

@[simp] theorem setG_name (N : SoftNode) : (setG γ N).name = N.name := rfl
@[simp] theorem setG_pred (N : SoftNode) : (setG γ N).pred = N.pred := rfl
@[simp] theorem setG_sign (N : SoftNode) : (setG γ N).sign = N.sign := rfl
@[simp] theorem setG_guard (N : SoftNode) : (setG γ N).guard = γ N.name N.guard := rfl
@[simp] theorem setG_carveOuts (N : SoftNode) : (setG γ N).carveOuts = N.carveOuts := rfl
@[simp] theorem setG_over (N : SoftNode) : (setG γ N).over = N.over := rfl
@[simp] theorem setG_mode (N : SoftNode) : (setG γ N).mode = N.mode := rfl
@[simp] theorem setG_rank (N : SoftNode) : (setG γ N).rank = N.rank := rfl
@[simp] theorem setG_alterable (N : SoftNode) : (setG γ N).alterable = N.alterable := rfl
@[simp] theorem setG_exception (N : SoftNode) : (setG γ N).exception = N.exception := rfl
@[simp] theorem setG_hard (N : SoftNode) : (setG γ N).hard = N.hard := rfl
@[simp] theorem setG_splitFrom (N : SoftNode) : (setG γ N).splitFrom = N.splitFrom := rfl

/-- A soft document with every guard changed by `γ`. -/
def mapG (C : SoftDoc) : SoftDoc := withNodes C (C.T.nodes.map (setG γ))

@[simp] theorem mapG_nodes (C : SoftDoc) : (mapG γ C).T.nodes = C.T.nodes.map (setG γ) := rfl
@[simp] theorem mapG_regulated (C : SoftDoc) : (mapG γ C).T.regulated = C.T.regulated := rfl
@[simp] theorem mapG_definitions (C : SoftDoc) : (mapG γ C).T.definitions = C.T.definitions := rfl
@[simp] theorem mapG_soft (C : SoftDoc) : (mapG γ C).soft = C.soft := rfl
@[simp] theorem mapG_E (C : SoftDoc) : (mapG γ C).E = C.E := rfl
@[simp] theorem mapG_lits (C : SoftDoc) : (mapG γ C).lits = C.lits := rfl
@[simp] theorem sortsOf_mapG (C : SoftDoc) (p : String) : VE.SoftNorms.sortsOf (mapG γ C) p = VE.SoftNorms.sortsOf C p :=
  rfl
@[simp] theorem dualPerm_mapG (C : SoftDoc) (p : String) : VE.SoftNorms.dualPerm (mapG γ C) p = VE.SoftNorms.dualPerm C p :=
  rfl
@[simp] theorem dualOblig_mapG (C : SoftDoc) (p : String) :
    VE.SoftNorms.dualOblig (mapG γ C) p = VE.SoftNorms.dualOblig C p := rfl

/-! ### Sorting and children commute with `setG` -/

theorem insertBy_map {α β : Type} (lt : β → β → Bool) (f : α → β) (x : α) :
    ∀ l : List α, VE.Norms.insertBy lt (f x) (l.map f) = (VE.Norms.insertBy (fun a b => lt (f a) (f b)) x l).map f
  | [] => rfl
  | y :: ys => by
    simp only [List.map_cons, VE.Norms.insertBy]
    split <;> simp [insertBy_map lt f x ys]

theorem sortBy_map {α β : Type} (lt : β → β → Bool) (f : α → β) :
    ∀ l : List α, VE.Norms.sortBy lt (l.map f) = (VE.Norms.sortBy (fun a b => lt (f a) (f b)) l).map f
  | [] => rfl
  | x :: xs => by simp only [List.map_cons, VE.Norms.sortBy, sortBy_map lt f xs, insertBy_map]

theorem childrenIn_setG (ns : List SoftNode) (N : SoftNode) :
    VE.SoftNorms.childrenIn (ns.map (setG γ)) (setG γ N) = (VE.SoftNorms.childrenIn ns N).map (setG γ) := by
  unfold VE.SoftNorms.childrenIn
  have h : ∀ C : SoftNode, (if (setG γ C).pred == (setG γ N).pred then
      ((setG γ C).over.filter (· == (setG γ N).name)).map (fun _ => setG γ C) else []) =
      (if C.pred == N.pred then (C.over.filter (· == N.name)).map (fun _ => C) else []).map (setG γ) := by
    intro C; simp only [setG_pred, setG_over, setG_name]; split <;> simp
  simp only [List.flatMap_map, h]
  rw [← List.map_flatMap, sortBy_map]
  rfl

theorem coreNode_setG (N : SoftNode) : VE.SoftNorms.coreNode (setG γ N) = setG γ (VE.SoftNorms.coreNode N) := rfl

/-! ### The builders -/

variable {γ}
variable (Q : String → VE.Formula → VE.Formula → Prop)

theorem liveStrictIn_ext (regs : List VE.Norms.Regulated) (N : SoftNode)
    (h : FExt (Q N.pred) N.guard (γ N.name N.guard)) :
    FExt (Q N.pred) (VE.SoftNorms.liveStrictIn regs N) (VE.SoftNorms.liveStrictIn regs (setG γ N)) :=
  .and (.and h (.refl _)) (.refl _)

theorem strictYieldsIn_ext (regs : List VE.Norms.Regulated) (ns : List SoftNode)
    (hns : ∀ N ∈ ns, FExt (Q N.pred) N.guard (γ N.name N.guard)) :
    ∀ (f : Nat) (N : SoftNode), N ∈ ns → FExt (Q N.pred) (VE.SoftNorms.strictYieldsIn regs ns f N)
      (VE.SoftNorms.strictYieldsIn regs (ns.map (setG γ)) f (setG γ N))
  | 0, N, hN => by
    simp only [VE.SoftNorms.strictYieldsIn, setG_mode]
    exact .or (FExt.ite _ (fun _ => liveStrictIn_ext Q regs N (hns N hN)) (fun _ => .refl _)) (.refl _)
  | f + 1, N, hN => by
    simp only [VE.SoftNorms.strictYieldsIn, setG_mode, childrenIn_setG, List.map_map]
    refine .or (FExt.ite _ (fun _ => liveStrictIn_ext Q regs N (hns N hN)) (fun _ => .refl _)) ?_
    refine FExt.anyF _ _ _ (fun C hC => ?_)
    obtain ⟨hC, hp, -⟩ := VE.SoftNorms.mem_childrenIn_iff.1 hC
    rw [← hp]; exact strictYieldsIn_ext regs ns hns f C hC

theorem strictSelectsIn_ext (regs : List VE.Norms.Regulated) (ns : List SoftNode)
    (hns : ∀ N ∈ ns, FExt (Q N.pred) N.guard (γ N.name N.guard)) (f : Nat) (N : SoftNode) (hN : N ∈ ns) :
    FExt (Q N.pred) (VE.SoftNorms.strictSelectsIn regs ns f N)
      (VE.SoftNorms.strictSelectsIn regs (ns.map (setG γ)) f (setG γ N)) := by
  simp only [VE.SoftNorms.strictSelectsIn, setG_mode, childrenIn_setG, List.map_map]
  refine FExt.ite _ (fun _ => .and (liveStrictIn_ext Q regs N (hns N hN)) (.not (FExt.anyF _ _ _ ?_)))
    (fun _ => .refl _)
  intro C hC
  obtain ⟨hC, hp, -⟩ := VE.SoftNorms.mem_childrenIn_iff.1 hC
  rw [← hp]; exact strictYieldsIn_ext Q regs ns hns f C hC

theorem strictDecidesIn_ext (regs : List VE.Norms.Regulated) (ns : List SoftNode)
    (hns : ∀ N ∈ ns, FExt (Q N.pred) N.guard (γ N.name N.guard)) (p : String) (sign : Bool) :
    FExt (Q p) (VE.SoftNorms.strictDecidesIn regs ns p sign)
      (VE.SoftNorms.strictDecidesIn regs (ns.map (setG γ)) p sign) := by
  simp only [VE.SoftNorms.strictDecidesIn, List.filter_map, List.map_map, List.length_map]
  refine FExt.anyF _ _ _ (fun N hN => ?_)
  simp only [List.mem_filter, Function.comp_def, setG_pred, setG_sign, beq_iff_eq] at hN
  rw [← hN.1.2]
  exact strictSelectsIn_ext Q regs ns hns _ N hN.1.1

theorem strictDecidesF_ext (C : SoftDoc) (hC : ∀ N ∈ C.T.nodes, FExt (Q N.pred) N.guard (γ N.name N.guard))
    (p : String) (sign : Bool) :
    FExt (Q p) (VE.SoftNorms.strictDecidesF C p sign) (VE.SoftNorms.strictDecidesF (mapG γ C) p sign) := by
  have h : (mapG γ C).T.nodes.map VE.SoftNorms.coreNode = (C.T.nodes.map VE.SoftNorms.coreNode).map (setG γ) := by
    simp only [mapG_nodes, List.map_map, Function.comp_def, coreNode_setG]
  simp only [VE.SoftNorms.strictDecidesF, h, mapG_regulated]
  refine strictDecidesIn_ext Q _ _ (fun N hN => ?_) p sign
  obtain ⟨M, hM, rfl⟩ := List.mem_map.1 hN
  exact hC M hM

/-- Duals have the same context. -/
structure DualCtx (C : SoftDoc) : Prop where
  perm : ∀ p m, VE.SoftNorms.dualPerm C p = some m → Q m = Q p
  oblig : ∀ m r, VE.SoftNorms.dualOblig C m = some r → Q r = Q m

variable {Q}

theorem blockedF_ext (C : SoftDoc) (hC : ∀ N ∈ C.T.nodes, FExt (Q N.pred) N.guard (γ N.name N.guard))
    (hd : DualCtx Q C) (N : SoftNode) :
    FExt (Q N.pred) (VE.SoftNorms.blockedF C N) (VE.SoftNorms.blockedF (mapG γ C) (setG γ N)) := by
  simp only [VE.SoftNorms.blockedF, VE.SoftNorms.strictPos, VE.SoftNorms.strictNeg, setG_pred, setG_sign,
    dualPerm_mapG, dualOblig_mapG]
  refine .or (.or (.or (strictDecidesF_ext Q C hC _ _) (strictDecidesF_ext Q C hC _ _)) ?_) ?_
  · refine FExt.ite _ (fun _ => ?_) (fun _ => .refl _)
    cases hm : VE.SoftNorms.dualPerm C N.pred with
    | none => exact .refl _
    | some m => rw [← hd.perm _ _ hm]; exact strictDecidesF_ext Q C hC _ _
  · refine FExt.ite _ (fun _ => .refl _) (fun _ => ?_)
    cases hr : VE.SoftNorms.dualOblig C N.pred with
    | none => exact .refl _
    | some r => rw [← hd.oblig _ _ hr]; exact strictDecidesF_ext Q C hC _ _

theorem liveF_ext (C : SoftDoc) (N : SoftNode) (h : FExt (Q N.pred) N.guard (γ N.name N.guard)) :
    FExt (Q N.pred) (VE.SoftNorms.liveF C N) (VE.SoftNorms.liveF (mapG γ C) (setG γ N)) :=
  .and (liveStrictIn_ext Q _ N h) (by simp only [setG_mode]; exact .refl _)

theorem eligibleF_ext (C : SoftDoc) (hC : ∀ N ∈ C.T.nodes, FExt (Q N.pred) N.guard (γ N.name N.guard))
    (hd : DualCtx Q C) (N : SoftNode) (h : FExt (Q N.pred) N.guard (γ N.name N.guard)) :
    FExt (Q N.pred) (VE.SoftNorms.eligibleF C N) (VE.SoftNorms.eligibleF (mapG γ C) (setG γ N)) := by
  simp only [VE.SoftNorms.eligibleF, setG_mode]
  exact FExt.ite _ (fun _ => .and (liveF_ext C N h) (.not (blockedF_ext C hC hd N))) (fun _ => .refl _)

theorem opponents_mapG (C : SoftDoc) (N : SoftNode) :
    VE.SoftNorms.opponents (mapG γ C) (setG γ N) = (VE.SoftNorms.opponents C N).map (setG γ) := by
  simp only [VE.SoftNorms.opponents, mapG_nodes, List.filter_map]
  rfl

/-- An opponent has the context of the rule it dominates. -/
theorem opp_ctx (C : SoftDoc) (hd : DualCtx Q C) {M N : SoftNode} (hM : M ∈ VE.SoftNorms.opponents C N) :
    Q M.pred = Q N.pred := by
  simp only [VE.SoftNorms.opponents, List.mem_filter, Bool.and_eq_true] at hM
  simp only [VE.SoftNorms.Incompatible, Bool.or_eq_true, Bool.and_eq_true, beq_iff_eq] at hM
  rcases hM.2.1.1 with (h | h) | h
  · rw [h.1]
  · exact (hd.perm _ _ h.2).symm
  · exact hd.perm _ _ h.2

theorem domWith_ext (C : SoftDoc) (hC : ∀ N ∈ C.T.nodes, FExt (Q N.pred) N.guard (γ N.name N.guard))
    (hd : DualCtx Q C) (eff eff' : SoftNode → VE.Formula) (N : SoftNode)
    (he : ∀ M ∈ VE.SoftNorms.opponents C N, FExt (Q M.pred) (eff M) (eff' (setG γ M))) :
    FExt (Q N.pred) (VE.SoftNorms.domWith C eff N) (VE.SoftNorms.domWith (mapG γ C) eff' (setG γ N)) := by
  unfold VE.SoftNorms.domWith
  rw [opponents_mapG, List.map_map]
  refine FExt.anyF _ _ _ (fun M hM => ?_)
  have hq := opp_ctx C hd hM
  have hMC : M ∈ C.T.nodes := (List.mem_filter.1 hM).1
  simp only [Function.comp_def]
  refine .or (FExt.ite _ (fun _ => .and (hq ▸ he M hM) (.refl _)) (fun _ => .refl _))
    (FExt.ite _ (fun _ => .and (hq ▸ eligibleF_ext C hC hd M (hC M hMC)) (.refl _)) (fun _ => .refl _))

theorem effF_ext (C : SoftDoc) (hC : ∀ N ∈ C.T.nodes, FExt (Q N.pred) N.guard (γ N.name N.guard))
    (hd : DualCtx Q C) : ∀ (g : Nat) (N : SoftNode), N ∈ C.T.nodes →
    FExt (Q N.pred) (VE.SoftNorms.effF C g N) (VE.SoftNorms.effF (mapG γ C) g (setG γ N))
  | 0, N, hN => eligibleF_ext C hC hd N (hC N hN)
  | g + 1, N, hN => .and (eligibleF_ext C hC hd N (hC N hN)) (.not (domWith_ext C hC hd _ _ N
      (fun M hM => effF_ext C hC hd g M (List.mem_filter.1 hM).1)))

theorem derived_ext (C : SoftDoc) (hC : ∀ N ∈ C.T.nodes, FExt (Q N.pred) N.guard (γ N.name N.guard))
    (hd : DualCtx Q C) (N : SoftNode) :
    FExt (Q N.pred) (VE.SoftNorms.derived C N) (VE.SoftNorms.derived (mapG γ C) (setG γ N)) := by
  unfold VE.SoftNorms.derived
  simp only [setG_mode]
  split
  · exact .refl _
  · refine .or (.or (.refl _) (blockedF_ext C hC hd N)) ?_
    exact domWith_ext C hC hd _ _ N (fun M hM => effF_ext C hC hd _ M (List.mem_filter.1 hM).1)

end VE.RightClauses.PWF
