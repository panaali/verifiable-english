import VE.RightClauses.PlainWellFormed.Hyp

/-! `rightsSemanticCheck (plain D)` (8.3, `plain_wellFormed`): the narrowing inventory of each line is unchanged, and
each formula the check types extends the old one by `FExt` at the line's context. Proof vocabulary only. -/
namespace VE.RightClauses.PWF
open VE.Rights (RightsDoc SourceLine Line linesOf sourceLines)
open VE.SoftNorms (SoftNode SoftDoc)

section RS
variable {D : ClauseDoc} (F : Facts D)
include F

theorem correlate_mapG : VE.Rights.correlate (plain D) = mapG (γP D) (VE.Rights.correlate D.doc) := by
  rw [correlate_plain, plainNodes_mapG D (nodes_nodup F)]; rfl

theorem lines_nodup : ((linesOf D.doc).map (fun RN => RN.2.node.name)).Nodup := by
  have := nodes_nodup F
  simp only [VE.Rights.correlate, List.map_append, List.nodup_append, List.map_map, Function.comp_def] at this
  simpa [VE.Rights.nodeOf] using this.1.1

theorem setG_line {RN : String × Line} (hRN : RN ∈ linesOf D.doc) :
    setG (γP D) (VE.Rights.nodeOf D.doc RN.2) = VE.Rights.nodeOf (plain D) (hL D RN).2 := by
  rw [nodeOf_hL]
  simp only [setG, γP, VE.Rights.nodeOf]
  rw [find?_key (fun RN : String × Line => RN.2.node.name) (lines_nodup F) hRN]

theorem direct_nodup : ((VE.Rights.directNodes D.doc).map (·.name)).Nodup := by
  have := nodes_nodup F
  simp only [VE.Rights.correlate, List.map_append, List.nodup_append] at this
  simp only [VE.Rights.directNodes, VE.Rights.lineNodes, List.map_append, List.nodup_append]
  exact this.1

theorem setG_out {N : SoftNode} (hN : N ∈ D.doc.soft.T.nodes) : setG (γP D) N = N := by
  have := nodes_nodup F
  simp only [VE.Rights.correlate, List.map_append, List.nodup_append, List.map_map, Function.comp_def] at this
  apply setG_self
  simp only [γP]
  rw [List.find?_eq_none.2 (fun RN hRN he => this.1.2.2 _ (List.mem_map_of_mem hRN) N.name (List.mem_map_of_mem hN)
    (by simpa [VE.Rights.nodeOf] using he))]

theorem directNodes_plain : VE.Rights.directNodes (plain D) = (VE.Rights.directNodes D.doc).map (setG (γP D)) := by
  unfold VE.Rights.directNodes
  rw [lineNodes_plain]
  simp only [VE.Rights.lineNodes, List.map_append, List.map_map, plain_soft]
  congr 1
  · apply List.map_congr_left
    intro RN hRN
    rw [Function.comp_apply, setG_line F hRN, nodeOf_hL]
  · have : D.doc.soft.T.nodes.map (setG (γP D)) = D.doc.soft.T.nodes.map id :=
      List.map_congr_left (fun N hN => setG_out F hN)
    rw [this, List.map_id]

theorem nodeNamed_plain (M : String) :
    VE.Rights.nodeNamed (plain D) M = (VE.Rights.nodeNamed D.doc M).map (setG (γP D)) := by
  simp only [VE.Rights.nodeNamed, directNodes_plain F, List.find?_map, Function.comp_def, setG_name]

theorem nodeNamed_self {M : SoftNode} (hM : M ∈ VE.Rights.directNodes D.doc) :
    VE.Rights.nodeNamed D.doc M.name = some M :=
  find?_key (fun N : SoftNode => N.name) (direct_nodup F) hM

theorem direct_sub {M : SoftNode} (hM : M ∈ VE.Rights.directNodes D.doc) : M ∈ (VE.Rights.correlate D.doc).T.nodes := by
  simp only [VE.Rights.directNodes, VE.Rights.lineNodes, List.mem_append] at hM
  simp only [VE.Rights.correlate, List.mem_append]
  rcases hM with h | h
  · exact Or.inl (Or.inl h)
  · exact Or.inl (Or.inr h)

end RS

@[simp] theorem hL_alterable (D : ClauseDoc) (RN : String × Line) :
    (hL D RN).2.node.alterable = RN.2.node.alterable := by simp only [hL]; split <;> rfl

section RS2
variable {D : ClauseDoc} (F : Facts D)
include F

theorem barReach_plain (RN : String × Line) :
    VE.Rights.barReach (plain D) (hL D RN).2 = VE.Rights.barReach D.doc RN.2 := by
  simp only [VE.Rights.barReach, VE.Rights.rightPermission, permPreds_plain, hL_pred, hL_mode, hL_sign,
    correlate_mapG F, dualPerm_mapG]

theorem narrowings_plain {RN : String × Line} (hRN : RN ∈ linesOf D.doc) :
    VE.Rights.narrowings (plain D) (hL D RN).2 = VE.Rights.narrowings D.doc RN.2 := by
  unfold VE.Rights.narrowings
  dsimp only
  rw [← setG_line F hRN, correlate_mapG F, directNodes_plain F, childrenIn_setG, limPackList_hL, barReach_plain F]
  simp only [hL_carveOuts, hL_mode, hL_alterable, List.map_map, List.filter_map, Function.comp_def, setG_name,
    setG_mode, VE.Rights.ruleReading, plain_bars]
  rfl

end RS2

theorem limPack_hL (D : ClauseDoc) (RN : String × Line) :
    VE.Rights.limPack (plain D) (hL D RN).2 = VE.Rights.limPack D.doc RN.2 := by
  have hs : VE.Rights.scopeLimits (plain D) (hL D RN).2 = VE.Rights.scopeLimits D.doc RN.2 := by
    simp [VE.Rights.scopeLimits, VE.Rights.inScope]
  simp only [VE.Rights.limPack, VE.Rights.limF, VE.Rights.limIndex, hs, limKeys_plain, lineAct_hL, sortsOf_hL]

theorem aimedF_plain (D : ClauseDoc) (m : String) : VE.Rights.aimedF (plain D) m = VE.Rights.aimedF D.doc m := by
  simp only [VE.Rights.aimedF, VE.Rights.barIndex, barPreds_plain, plain_soft]

theorem incompat_ctx {Q : String → VE.Formula → VE.Formula → Prop} {C : SoftDoc} (hd : DualCtx Q C) {M N : SoftNode}
    (h : VE.SoftNorms.Incompatible C M N = true) : Q M.pred = Q N.pred := by
  simp only [VE.SoftNorms.Incompatible, Bool.or_eq_true, Bool.and_eq_true, beq_iff_eq] at h
  rcases h with (h | h) | h
  · rw [h.1]
  · exact (hd.perm _ _ h.2).symm
  · exact hd.perm _ _ h.2

theorem blocks_ctx {Q : String → VE.Formula → VE.Formula → Prop} {C : SoftDoc} (hd : DualCtx Q C) {X M : SoftNode}
    (h : VE.Rights.blocksOn C X M = true) : Q M.pred = Q X.pred := by
  simp only [VE.Rights.blocksOn, Bool.or_eq_true, Bool.and_eq_true, beq_iff_eq, bne_iff_ne] at h
  rcases h with (h | h) | h
  · rw [h]
  · exact hd.perm _ _ h.1.2
  · exact hd.oblig _ _ h.1.2

theorem mem_narrowings_exception {X : RightsDoc} {N : Line} {M : String}
    (h : VE.Rights.Narrowing.exception M ∈ VE.Rights.narrowings X N) :
    ∃ c ∈ VE.SoftNorms.childrenIn (VE.Rights.directNodes X) (VE.Rights.nodeOf X N), c.name = M := by
  simpa [VE.Rights.narrowings] using h

theorem mem_narrowings_blocked {X : RightsDoc} {N : Line} {M : String}
    (h : VE.Rights.Narrowing.blockedBy M ∈ VE.Rights.narrowings X N) :
    ∃ c ∈ VE.Rights.directNodes X, VE.Rights.blocksOn (VE.Rights.correlate X) (VE.Rights.nodeOf X N) c = true ∧
      c.name = M := by
  simp [VE.Rights.narrowings] at h
  obtain ⟨_, c, ⟨hc, _, hb⟩, he⟩ := h
  exact ⟨c, hc, hb, he⟩

theorem mem_narrowings_dominated {X : RightsDoc} {N : Line} {M : String}
    (h : VE.Rights.Narrowing.dominatedBy M ∈ VE.Rights.narrowings X N) :
    ∃ c ∈ VE.Rights.directNodes X, VE.SoftNorms.Incompatible (VE.Rights.correlate X) c (VE.Rights.nodeOf X N) = true ∧
      c.name = M := by
  simp [VE.Rights.narrowings] at h
  obtain ⟨_, c, ⟨hc, ⟨_, hi⟩, _⟩, he⟩ := h
  exact ⟨c, hc, hi, he⟩

section RS3
variable {D : ClauseDoc} (F : Facts D) (h : WellFormedClauses D = true)
include F h

theorem ownGuard_ext {RN : String × Line} (hRN : RN ∈ linesOf D.doc) :
    FExt (QC (VE.Rights.correlate D.doc) (baseEnv D) RN.2.node.pred) (VE.Rights.ownGuard D.doc RN.2)
      (VE.Rights.ownGuard (plain D) (hL D RN).2) := by
  unfold VE.Rights.ownGuard
  rw [holderConj_hL]
  exact holderConj_ext F D.doc RN.2 (line_guard_ext F h hRN)

theorem condF_ext {RN : String × Line} (hRN : RN ∈ linesOf D.doc) (n : VE.Rights.Narrowing)
    (hn : n ∈ VE.Rights.narrowings D.doc RN.2) :
    FExt (QC (VE.Rights.correlate D.doc) (baseEnv D) RN.2.node.pred) (VE.Rights.condF D.doc RN.2 n)
      (VE.Rights.condF (plain D) (hL D RN).2 n) := by
  have hY : VE.Rights.nodeOf (plain D) (hL D RN).2 = setG (γP D) (VE.Rights.nodeOf D.doc RN.2) :=
    (setG_line F hRN).symm
  have hg := ghyp F h
  cases n with
  | carveOut i =>
    simp only [VE.Rights.condF, hL_carveOuts]; exact .and (ownGuard_ext F h hRN) (.refl _)
  | exception M =>
    obtain ⟨c, hc, rfl⟩ := mem_narrowings_exception hn
    obtain ⟨hcd, hcp, -⟩ := VE.SoftNorms.mem_childrenIn_iff.1 hc
    simp only [VE.Rights.condF, nodeNamed_plain F, nodeNamed_self F hcd, Option.map_some, correlate_mapG F]
    have hy := yields_ext (softenTRel hg) (VE.Rights.correlate D.doc).T.regulated
      (VE.Rights.correlate D.doc).T.definitions (VE.Rights.correlate D.doc).T.nodes.length c (direct_sub F hcd)
    have hl : (VE.SoftNorms.soften (VE.Rights.correlate D.doc)).T.nodes.length =
        (VE.Rights.correlate D.doc).T.nodes.length := by simp [VE.SoftNorms.soften]
    rw [soften_mapG]
    simp only [VE.Norms.fuel, List.length_map, hl]
    have hp : c.pred = RN.2.node.pred := hcp
    rw [← hp]; exact hy
  | limPack => simp only [VE.Rights.condF, limPack_hL]; exact .refl _
  | excepted => simp only [VE.Rights.condF, hY, correlate_mapG F]; exact .refl _
  | switch π => simp only [VE.Rights.condF, hY, correlate_mapG F, hL_pred]; exact .refl _
  | blockedBy M =>
    obtain ⟨c, hcd, hb, rfl⟩ := mem_narrowings_blocked hn
    simp only [VE.Rights.condF, nodeNamed_plain F, nodeNamed_self F hcd, Option.map_some, correlate_mapG F]
    have := selects'_ext hg c (direct_sub F hcd)
    rw [blocks_ctx hg.dual hb] at this
    exact this
  | dominatedBy M =>
    obtain ⟨c, hcd, hi, rfl⟩ := mem_narrowings_dominated hn
    simp only [VE.Rights.condF, nodeNamed_plain F, nodeNamed_self F hcd, Option.map_some, correlate_mapG F, hY]
    have hq := incompat_ctx hg.dual hi
    have hcC := direct_sub F hcd
    unfold VE.Rights.domOneF
    refine .or (FExt.ite _ (fun _ => .and ?_ (.refl _)) (fun _ => .refl _))
      (FExt.ite _ (fun _ => .and ?_ (.refl _)) (fun _ => .refl _))
    · have := effF_ext (VE.Rights.correlate D.doc) hg.guards hg.dual
        (VE.Rights.correlate D.doc).soft.ranks.length c hcC
      rw [hq] at this; exact this
    · have := eligibleF_ext (VE.Rights.correlate D.doc) hg.guards hg.dual c (hg.guards c hcC)
      rw [hq] at this; exact this
  | bar =>
    simp only [VE.Rights.condF, barReach_plain F]
    split
    · rw [aimedF_plain]; exact .refl _
    · exact .refl _

theorem rightsSemanticCheck_plain : VE.Rights.rightsSemanticCheck (plain D) = true := by
  have hs := F.sem
  have hg := ghyp F h
  unfold VE.Rights.rightsSemanticCheck at hs ⊢
  dsimp only at hs ⊢
  rw [correlate_mapG F, envAt_mapG hg, envAt_mapG hg, size_mapG hg]
  simp only [Bool.and_eq_true, List.all_eq_true] at hs ⊢
  obtain ⟨⟨⟨h1, h2⟩, h3⟩, h4⟩ := hs
  have hP : ∀ (RN : String × Line) a b, QC (VE.Rights.correlate D.doc) (baseEnv D) RN.2.node.pred a b →
      a.check (VE.Norms.envAt (VE.SoftNorms.soften (VE.Rights.correlate D.doc))
        (VE.Norms.size (VE.SoftNorms.soften (VE.Rights.correlate D.doc)))) (VE.Rights.sortsOf D.doc RN.2).reverse = true →
      b.check (VE.Norms.envAt (VE.SoftNorms.soften (VE.Rights.correlate D.doc))
        (VE.Norms.size (VE.SoftNorms.soften (VE.Rights.correlate D.doc)))) (VE.Rights.sortsOf D.doc RN.2).reverse = true :=
    fun RN a b hab ha => Plus.check' (envOK_envAt hg _) hab ha
  refine ⟨⟨⟨?_, ?_⟩, ?_⟩, ?_⟩
  · intro X hX B hB
    simp only [mapG_nodes, List.mem_map] at hX
    obtain ⟨X0, hX0, rfl⟩ := hX
    rw [barNodes_plain] at hB
    exact h1 X0 hX0 B hB
  · intro m hm
    rw [permPreds_plain] at hm
    simpa using h2 m hm
  · intro RN' hRN'
    rw [linesOf_plain] at hRN'
    obtain ⟨RN, hRN, rfl⟩ := List.mem_map.1 hRN'
    have hold := h3 RN hRN
    simp only [Bool.and_eq_true, List.all_eq_true, sortsOf_hL] at hold ⊢
    obtain ⟨⟨⟨⟨ho, hsel⟩, hn⟩, hl⟩, hb⟩ := hold
    have hY : VE.Rights.nodeOf (plain D) (hL D RN).2 = setG (γP D) (VE.Rights.nodeOf D.doc RN.2) :=
      (setG_line F hRN).symm
    have hXC : VE.Rights.nodeOf D.doc RN.2 ∈ (VE.Rights.correlate D.doc).T.nodes := by
      simp only [VE.Rights.correlate, List.mem_append, List.mem_map]; exact Or.inl (Or.inl ⟨RN, hRN, rfl⟩)
    refine ⟨⟨⟨⟨FExt.check (hP RN) (ownGuard_ext F h hRN) ho, ?_⟩, ?_⟩, ?_⟩, ?_⟩
    · have := selects'_check hg _ hXC hsel
      rw [← envAt_mapG hg, ← size_mapG hg]
      simpa only [VE.Rights.selectsR, hY, correlate_mapG F] using this
    · intro n hn'
      rw [narrowings_plain F hRN] at hn'
      exact FExt.check (hP RN) (condF_ext F h hRN n hn') (hn n hn')
    · rw [limPack_hL]; exact hl
    · rw [barReach_plain F]
      revert hb
      split
      · simp only [VE.Rights.ruleReading, plain_bars, aimedF_plain]; exact id
      · exact id
  · intro φ hφ
    have : VE.Rights.limPremises (plain D) = VE.Rights.limPremises D.doc := by
      simp only [VE.Rights.limPremises, plain_limPremises]
    rw [this] at hφ
    exact h4 φ hφ

end RS3

end VE.RightClauses.PWF
