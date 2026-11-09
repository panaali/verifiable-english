import VE.RightClauses.PlainWellFormed.Clauses

/-! `correlate (plain D)` is `mapG (γP D) (correlate D.doc)` (`plainNodes_mapG`; `correlate_mapG` in
RightsSem.lean), and the new guards meet
`GHyp` (`ghyp`): each extends the old one by the line's clauses and relation atom, typed over the base vocabulary
in the line's context (8.3, `plain_wellFormed`). Proof vocabulary only. -/
namespace VE.RightClauses.PWF
open VE.Rights (RightsDoc SourceLine Line linesOf sourceLines)
open VE.SoftNorms (SoftNode SoftDoc)

/-- What an instance keeps of its source line. -/
def FromSource (N : Line) : Prop :=
  N.kind = N.source.kind ∧ (N.kind ≠ .power → ∃ n0, N.source.norm = some n0 ∧ N.node.guard = n0.guard ∧
    N.node.pred = (if N.source.fanOut = [] then n0.pred else N.node.pred) ∧ (N.source.fanOut = [] → N.node = n0))

theorem instancesOf_from (R : String) (S : SourceLine) (k : Nat) :
    ∀ N ∈ VE.Rights.instancesOf R S k, N.source = S ∧ FromSource N := by
  intro N hN
  obtain ⟨kd, n, l, r, f, hs, cs⟩ := S
  cases kd
  case power =>
    simp only [VE.Rights.instancesOf] at hN
    split at hN
    · simp only [List.mem_cons, List.not_mem_nil, or_false] at hN
      rcases hN with rfl | rfl <;> exact ⟨rfl, rfl, fun h => absurd rfl h⟩
    · simp at hN
  all_goals
    cases n with
    | none => simp [VE.Rights.instancesOf] at hN
    | some n0 =>
      simp only [VE.Rights.instancesOf] at hN
      by_cases hf : f = []
      · subst hf
        simp only [if_true, List.mem_singleton] at hN; subst hN
        exact ⟨rfl, rfl, fun _ => ⟨n0, rfl, rfl, by simp, fun _ => rfl⟩⟩
      · simp only [hf, if_false, List.mem_mapIdx] at hN
        obtain ⟨i, hi, rfl⟩ := hN
        exact ⟨rfl, rfl, fun _ => ⟨n0, rfl, rfl, by simp [hf], fun h => absurd h hf⟩⟩

theorem linesAux_from : ∀ (l : List (String × SourceLine)) (k : Nat) (RN : String × Line),
    RN ∈ VE.Rights.linesAux l k → (RN.1, RN.2.source) ∈ l ∧ FromSource RN.2
  | [], _, _, h => by cases h
  | (R, S) :: rest, k, RN, h => by
    simp only [VE.Rights.linesAux, List.mem_append, List.mem_map] at h
    rcases h with ⟨N, hN, rfl⟩ | h
    · obtain ⟨hs, hf⟩ := instancesOf_from R S k N hN
      exact ⟨by simp [hs], hf⟩
    · obtain ⟨h1, h2⟩ := linesAux_from rest _ RN h
      exact ⟨List.mem_cons_of_mem _ h1, h2⟩

theorem mem_linesOf {X : RightsDoc} {RN : String × Line} (h : RN ∈ linesOf X) :
    (RN.1, RN.2.source) ∈ sourceLines X ∧ FromSource RN.2 := linesAux_from _ 0 RN h

/-! ### `correlate (plain D)` as `mapG` -/

/-- The new guard of the node named `n` (its old guard `G` when no line instance has that name). -/
def γP (D : ClauseDoc) (n : String) (G : VE.Formula) : VE.Formula :=
  match (linesOf D.doc).find? (fun RN => RN.2.node.name == n) with
  | some RN => newGuard D RN
  | none => G

theorem find?_key {α : Type} (k : α → String) :
    ∀ {l : List α}, (l.map k).Nodup → ∀ {a : α}, a ∈ l → l.find? (fun b => k b == k a) = some a
  | [], _, _, ha => by cases ha
  | b :: l, hnd, a, ha => by
    simp only [List.map_cons, List.nodup_cons, List.mem_map] at hnd
    rcases List.mem_cons.1 ha with rfl | ha
    · simp
    · have hne : (k b == k a) = false := by
        simp only [beq_eq_false_iff_ne]; intro he; exact hnd.1 ⟨a, ha, he.symm⟩
      simp [List.find?_cons, hne, find?_key k hnd.2 ha]

theorem setG_self (γ : String → VE.Formula → VE.Formula) (N : SoftNode) (h : γ N.name N.guard = N.guard) :
    setG γ N = N := by
  obtain ⟨⟨⟩⟩ := N; simp only [setG] at h ⊢; rw [h]

theorem plainNodes_mapG (D : ClauseDoc) (hnd : ((VE.Rights.correlate D.doc).T.nodes.map (·.name)).Nodup) :
    plainNodes D = (VE.Rights.correlate D.doc).T.nodes.map (setG (γP D)) := by
  have hC : (VE.Rights.correlate D.doc).T.nodes =
      (linesOf D.doc).map (fun RN => VE.Rights.nodeOf D.doc RN.2) ++ D.doc.soft.T.nodes ++ VE.Rights.barNodes D.doc :=
    rfl
  rw [hC] at hnd ⊢
  simp only [List.map_append, List.nodup_append, List.map_map, Function.comp_def] at hnd
  have hlines : ((linesOf D.doc).map (fun RN => RN.2.node.name)).Nodup := by
    have := hnd.1.1; simpa [VE.Rights.nodeOf] using this
  have hout : ∀ N : SoftNode, (∀ RN ∈ linesOf D.doc, RN.2.node.name ≠ N.name) → setG (γP D) N = N := by
    intro N hN
    apply setG_self
    simp only [γP]
    rw [List.find?_eq_none.2 (fun RN hRN => by simpa using hN RN hRN)]
  have h1 : (linesOf D.doc).map (fun RN => { VE.Rights.nodeOf D.doc RN.2 with guard := newGuard D RN }) =
      (linesOf D.doc).map (fun RN => setG (γP D) (VE.Rights.nodeOf D.doc RN.2)) := by
    apply List.map_congr_left
    intro RN hRN
    simp only [setG, γP, VE.Rights.nodeOf]
    rw [find?_key (fun RN : String × Line => RN.2.node.name) hlines hRN]
  have h2 : D.doc.soft.T.nodes = D.doc.soft.T.nodes.map (setG (γP D)) := by
    have : D.doc.soft.T.nodes.map (setG (γP D)) = D.doc.soft.T.nodes.map id := by
      apply List.map_congr_left
      intro N hN
      refine hout N (fun RN hRN he => hnd.1.2.2 _ (List.mem_map_of_mem hRN) N.name (List.mem_map_of_mem hN) ?_)
      simpa [VE.Rights.nodeOf] using he
    rw [List.map_id] at this; exact this.symm
  have h3 : VE.Rights.barNodes D.doc = (VE.Rights.barNodes D.doc).map (setG (γP D)) := by
    have : (VE.Rights.barNodes D.doc).map (setG (γP D)) = (VE.Rights.barNodes D.doc).map id := by
      apply List.map_congr_left
      intro N hN
      refine hout N (fun RN hRN he => hnd.2.2 _ (List.mem_append_left _ (List.mem_map_of_mem hRN)) N.name
        (List.mem_map_of_mem hN) ?_)
      simpa [VE.Rights.nodeOf] using he
    rw [List.map_id] at this; exact this.symm
  unfold plainNodes
  rw [h1, List.map_append, List.map_append, List.map_map, ← h2, ← h3]
  rfl

/-! ### The facts of a well-formed rights document -/

theorem validateRights_ok {X : RightsDoc} (h : VE.Rights.validateRights X = .ok ()) :
    VE.Rights.checkRights X = .ok () ∧ VE.SoftNorms.validateSoft (VE.Rights.correlate X) = .ok () ∧
      (VE.SoftNorms.decisionNames (VE.Rights.correlate X)).find?
        (fun n => n.utf8ByteSize > VE.Limits.maxIdentifierBytes) = none ∧
      VE.Rights.rightsSemanticCheck X = true := by
  unfold VE.Rights.validateRights at h
  split at h
  · cases h
  rename_i h1
  split at h
  · cases h
  rename_i h2
  split at h
  · cases h
  rename_i h3
  split at h
  · exact ⟨h1, h2, h3, by assumption⟩
  · cases h

/-- What `GHyp` and the rights checks read of `WellFormedRights D.doc`. -/
structure Facts (D : ClauseDoc) : Prop where
  rights : VE.Rights.checkRights D.doc = .ok ()
  soft : VE.SoftNorms.validateSoft (VE.Rights.correlate D.doc) = .ok ()
  ident : (VE.SoftNorms.decisionNames (VE.Rights.correlate D.doc)).find?
    (fun n => n.utf8ByteSize > VE.Limits.maxIdentifierBytes) = none
  sem : VE.Rights.rightsSemanticCheck D.doc = true
  ss : VE.SoftNorms.softSemanticCheck (VE.Rights.correlate D.doc) = true
  w1sem : VE.Norms.semanticCheck (VE.SoftNorms.soften (VE.Rights.correlate D.doc)) = true

theorem facts (D : ClauseDoc) (h0 : VE.Rights.WellFormedRights D.doc = true) : Facts D := by
  have hv : VE.Rights.validateRights D.doc = .ok () := by
    unfold VE.Rights.WellFormedRights at h0; split at h0 <;> simp_all
  obtain ⟨h1, h2, h3, h4⟩ := validateRights_ok hv
  have hss := ((validateSoft_ok_iff _).1 h2).2
  refine ⟨h1, h2, h3, h4, hss, ?_⟩
  simp only [VE.SoftNorms.softSemanticCheck, Bool.and_eq_true] at hss
  exact VE.Norms.semanticCheck_of_wellFormed _ (by simpa using hss.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1.1)

theorem eq_of_key {α : Type} (k : α → String) {l : List α} (hnd : (l.map k).Nodup) {a b : α} (ha : a ∈ l)
    (hb : b ∈ l) (he : k a = k b) : a = b := by
  have h1 := find?_key k hnd ha
  have h2 := find?_key k hnd hb
  rw [he] at h1; rw [h1] at h2; exact Option.some.inj h2

section Hyps
variable {D : ClauseDoc} (F : Facts D)
include F

/-- A base predicate is neither regulated nor defined, and `E` declares it. -/
theorem baseEnv_keep {p : String} {s : List String} (hp : (baseEnv D).predicates p = some s) :
    keepOf (VE.Rights.correlate D.doc).T.regulated (VE.Rights.correlate D.doc).T.definitions p = false ∧
      D.doc.soft.E.predicates p = some s := by
  simp only [baseEnv, VE.Norms.envAt, VE.Norms.hide, List.drop_zero] at hp
  split at hp
  · cases hp
  rename_i hl
  refine ⟨?_, hp⟩
  cases hk : keepOf (VE.Rights.correlate D.doc).T.regulated (VE.Rights.correlate D.doc).T.definitions p
  · rfl
  · exfalso; apply hl
    refine layer_names (VE.Rights.correlate D.doc) D.doc.soft.base.T rfl rfl ?_ F.w1sem p hk
    intro N hN
    simp only [VE.SoftNorms.SoftDoc.base, List.mem_map] at hN
    obtain ⟨M, hM, rfl⟩ := hN
    exact ⟨M, by simp [VE.Rights.correlate, hM], rfl, rfl, fun _ h => h⟩

theorem envC : EnvOKB (baseEnv D) (keepOf (VE.Rights.correlate D.doc).T.regulated
    (VE.Rights.correlate D.doc).T.definitions) (VE.Rights.correlate D.doc).E := by
  refine ⟨rfl, rfl, fun p s hp _ => ?_⟩
  obtain ⟨-, hE⟩ := baseEnv_keep F hp
  show (VE.Rights.envR D.doc).predicates p = some s
  simp only [VE.Rights.envR]
  cases hg : (VE.Rights.genDecls D.doc).find? (·.1 == p) with
  | none => exact hE
  | some d =>
    have hd := genDecls_fresh D.doc F.rights d (List.mem_of_find?_eq_some hg)
    have := List.find?_some hg
    simp only [beq_iff_eq] at this
    rw [this, hE] at hd; cases hd

theorem envP : EnvOKB (baseEnv D) (keepOf (VE.Rights.correlate D.doc).T.regulated
    (VE.Rights.correlate D.doc).T.definitions) (VE.SoftNorms.envPrime (VE.Rights.correlate D.doc)) := by
  refine ⟨rfl, rfl, fun p s hp hk => ?_⟩
  have hC := (envC F).2.2 p s hp hk
  simp only [VE.SoftNorms.envPrime]
  cases hd : (VE.SoftNorms.decisions (VE.Rights.correlate D.doc)).find? (·.1 == p) with
  | none => exact hC
  | some d =>
    have hss := F.ss
    simp only [VE.SoftNorms.softSemanticCheck, Bool.and_eq_true, and_assoc, List.all_eq_true] at hss
    have hn := hss.2.2.2.2.2.2.2.2.2.2.2.2.1 d.1 (by
      simp only [VE.SoftNorms.decisionNames, List.mem_map]; exact ⟨d, List.mem_of_find?_eq_some hd, rfl⟩)
    have := List.find?_some hd
    simp only [beq_iff_eq] at this
    rw [this, hC] at hn; cases hn

theorem regs_nodup : ((VE.Rights.correlate D.doc).T.regulated.map (·.name)).Nodup := by
  have hss := F.ss
  simp only [VE.SoftNorms.softSemanticCheck, Bool.and_eq_true, and_assoc, decide_eq_true_eq] at hss
  exact hss.2.2.1

theorem pair_sorts {pr : VE.Norms.Pair} (hpr : pr ∈ VE.Norms.pairs (VE.Rights.correlate D.doc).base.T) :
    VE.SoftNorms.sortsOf (VE.Rights.correlate D.doc) pr.req = pr.sorts ∧
      VE.SoftNorms.sortsOf (VE.Rights.correlate D.doc) pr.perm = pr.sorts := by
  have hw := F.w1sem
  simp only [VE.Norms.semanticCheck, Bool.and_eq_true, List.all_eq_true, List.any_eq_true] at hw
  have hp := hw.2 pr hpr
  simp only [Bool.and_eq_true] at hp
  obtain ⟨⟨-, ⟨q, hq, hq'⟩⟩, ⟨q2, hq2, hq2'⟩⟩ := hp
  have hnd := regs_nodup F
  refine ⟨?_, ?_⟩
  · cases q with
    | defn _ => cases hq'
    | reg r =>
      simp only [Bool.and_eq_true, beq_iff_eq] at hq'
      rw [← hq'.1, sortsOf_find (find?_name hnd (mem_syms_reg hq)), hq'.2]
  · cases q2 with
    | defn _ => cases hq2'
    | reg r =>
      simp only [Bool.and_eq_true, beq_iff_eq] at hq2'
      rw [← hq2'.1, sortsOf_find (find?_name hnd (mem_syms_reg hq2)), hq2'.2]

theorem dualCtx : DualCtx (QC (VE.Rights.correlate D.doc) (baseEnv D)) (VE.Rights.correlate D.doc) where
  perm p m h := by
    simp only [VE.SoftNorms.dualPerm, Option.map_eq_some_iff] at h
    obtain ⟨pr, hpr, rfl⟩ := h
    have hreq := List.find?_some hpr
    simp only [beq_iff_eq] at hreq
    obtain ⟨h1, h2⟩ := pair_sorts F (List.mem_of_find?_eq_some hpr)
    simp only [QC, h2, ← hreq, h1]
  oblig m r h := by
    simp only [VE.SoftNorms.dualOblig, Option.map_eq_some_iff] at h
    obtain ⟨pr, hpr, rfl⟩ := h
    have hperm := List.find?_some hpr
    simp only [beq_iff_eq] at hperm
    obtain ⟨h1, h2⟩ := pair_sorts F (List.mem_of_find?_eq_some hpr)
    simp only [QC, h1, ← hperm, h2]

theorem holderConj_ext {P : VE.Formula → VE.Formula → Prop} (X : RightsDoc) (N : Line) {G G' : VE.Formula}
    (h : FExt P G G') : FExt P (VE.Rights.holderConj X N G) (VE.Rights.holderConj X N G') := by
  unfold VE.Rights.holderConj
  split
  · split
    · exact h
    · exact .and h (.refl _)
  · exact h

theorem line_guard_ext (h : WellFormedClauses D = true) {RN : String × Line} (hRN : RN ∈ linesOf D.doc) :
    FExt (QC (VE.Rights.correlate D.doc) (baseEnv D) RN.2.node.pred) RN.2.node.guard (hL D RN).2.node.guard := by
  obtain ⟨hsrc, -, hfrom⟩ := mem_linesOf hRN
  simp only [hL]
  split
  · exact .refl _
  rename_i hpw
  obtain ⟨n0, hn0, hg, -, hfan⟩ := hfrom hpw
  unfold plainSource
  split
  · rename_i x hx
    have hxmem := List.mem_of_find?_eq_some hx
    have hxc := List.find?_some hx
    obtain ⟨R', n', L⟩ := x
    simp only [Bool.and_eq_true, beq_iff_eq] at hxc
    obtain ⟨hshape, -, -, hfilter, -⟩ := entry_facts D h R' n' L hxmem
    have hS : RN.2.source = L.line := by
      have hm : (RN.1, RN.2.source) ∈ (sourceLines D.doc).filter (fun RS => lineName RS.2 == some n') :=
        List.mem_filter.2 ⟨hsrc, by simp [← hxc.2]⟩
      rw [hfilter] at hm; simp at hm; exact hm.2
    simp only [hn0, Option.map_some, Option.getD_some]
    rw [hg]
    simp only [shapeOk, Bool.or_eq_true, Bool.and_eq_true, List.isEmpty_iff, Option.isNone_iff_eq_none] at hshape
    rcases hshape with ⟨hc, hr⟩ | ⟨⟨-, hf⟩, -⟩
    · simp only [plainGuard, hc, hr, List.map_nil, Option.map_none, Option.toList_none, List.append_nil,
        List.foldl_nil]
      exact .refl _
    · have hnode := hfan (by rw [hS]; simpa using hf)
      have hsorts : VE.SoftNorms.sortsOf (VE.Rights.correlate D.doc) RN.2.node.pred =
          lineSorts D.doc.soft L.line := by
        rw [← hS, hnode]; simp [lineSorts, hn0]; rfl
      obtain ⟨htc, htr⟩ := entry_typed D h (R', n', L) hxmem
      refine .base ⟨L.clauses.map (·.formula) ++ (L.relation.map (relAtom (lineSorts D.doc.soft L.line).length)).toList,
        by simp only [plainGuard, hS, hn0], ?_⟩
      intro c hc
      have hct : c.check (baseEnv D) (lineSorts D.doc.soft L.line).reverse = true := by
        rcases List.mem_append.1 hc with hc | hc
        · obtain ⟨cl, hcl, rfl⟩ := List.mem_map.1 hc; exact htc cl hcl
        · cases hrel : L.relation with
          | none => simp [hrel] at hc
          | some rel => simp [hrel] at hc; subst hc; exact htr rel hrel
      refine ⟨by rw [hsorts]; exact hct, fun p hp => ?_⟩
      obtain ⟨s, hs⟩ := Option.isSome_iff_exists.1 (preds_declared c _ hct p hp)
      exact (baseEnv_keep F hs).1
  · simp only [hn0, Option.map_some, Option.getD_some, hg]
    exact .refl _

theorem nodes_nodup : ((VE.Rights.correlate D.doc).T.nodes.map (·.name)).Nodup := by
  have hss := F.ss
  simp only [VE.SoftNorms.softSemanticCheck, Bool.and_eq_true, and_assoc, decide_eq_true_eq] at hss
  exact hss.2.1

theorem ghyp (h : WellFormedClauses D = true) : GHyp (γP D) (VE.Rights.correlate D.doc) (baseEnv D) where
  guards N hN := by
    unfold γP
    split
    · rename_i RN hRN
      have hRNm := List.mem_of_find?_eq_some hRN
      have hname := List.find?_some hRN
      simp only [beq_iff_eq] at hname
      have hX : VE.Rights.nodeOf D.doc RN.2 ∈ (VE.Rights.correlate D.doc).T.nodes := by
        simp only [VE.Rights.correlate, List.mem_append, List.mem_map]; exact Or.inl (Or.inl ⟨RN, hRNm, rfl⟩)
      have hN' := eq_of_key (fun M : SoftNode => M.name) (nodes_nodup F) hN hX (by show N.name = RN.2.node.name; exact hname.symm)
      subst hN'
      exact holderConj_ext F D.doc RN.2 (line_guard_ext F h hRNm)
    · exact .refl _
  dual := dualCtx F
  envC := envC F
  envP := envP F

end Hyps

end VE.RightClauses.PWF
