import VE.RightClauses.PlainWellFormed.SoftCheck

/-! `validateSoft` under a change of guards (8.3, `plain_wellFormed`): when each node's new guard extends its old
one by base conjuncts typed in the node's context (`QC`), `validateSoft (mapG γ C)` passes or reports a resource
limit (`validateSoft_mapG`). Proof vocabulary only. -/
namespace VE.RightClauses.PWF
open VE.SoftNorms
open VE.Norms (Node envAt size syms layerNames preds)

/-! ### Environments that show the base conjuncts -/

/-- `E` shows every predicate of `E0` that is not regulated or defined, with its sorts. -/
def EnvOK' (E0 : VE.Environment) (keep : String → Bool) (E : VE.Environment) : Prop :=
  E.sorts = E0.sorts ∧ E.constants = E0.constants ∧
    ∀ p s, E0.predicates p = some s → keep p = false → E.predicates p = some s

theorem check_preds_mono {E0 E : VE.Environment} (hs : E.sorts = E0.sorts) (hc : E.constants = E0.constants) :
    ∀ (φ : VE.Formula) (Γ : List String), (∀ p ∈ preds φ, ∀ s, E0.predicates p = some s → E.predicates p = some s) →
      φ.check E0 Γ = true → φ.check E Γ = true
  | .top, _, _, _ | .bottom, _, _, _ => rfl
  | .unary p t, Γ, hp, h => by
    have ht : t.sortOf E Γ = t.sortOf E0 Γ := by cases t <;> simp [VE.Term.sortOf, hc]
    simp only [VE.Formula.check, ht] at h ⊢
    cases h0 : E0.predicates p with
    | none => simp [h0] at h
    | some s => rw [hp p (by simp [VE.Norms.preds]) s h0]; simpa [h0] using h
  | .binary p t u, Γ, hp, h => by
    have ht : ∀ t : VE.Term, t.sortOf E Γ = t.sortOf E0 Γ := by intro t; cases t <;> simp [VE.Term.sortOf, hc]
    simp only [VE.Formula.check, ht] at h ⊢
    cases h0 : E0.predicates p with
    | none => simp [h0] at h
    | some s => rw [hp p (by simp [VE.Norms.preds]) s h0]; simpa [h0] using h
  | .eq t u, Γ, _, h => by
    have ht : ∀ t : VE.Term, t.sortOf E Γ = t.sortOf E0 Γ := by intro t; cases t <;> simp [VE.Term.sortOf, hc]
    simpa only [VE.Formula.check, ht] using h
  | .not a, Γ, hp, h => check_preds_mono hs hc a Γ hp h
  | .and a b, Γ, hp, h | .or a b, Γ, hp, h | .implies a b, Γ, hp, h => by
    simp only [VE.Formula.check, Bool.and_eq_true] at h ⊢
    exact ⟨check_preds_mono hs hc a Γ (fun p hq => hp p (by simp [VE.Norms.preds, hq])) h.1,
      check_preds_mono hs hc b Γ (fun p hq => hp p (by simp [VE.Norms.preds, hq])) h.2⟩
  | .all s a, Γ, hp, h | .ex s a, Γ, hp, h => by
    simp only [VE.Formula.check, Bool.and_eq_true, hs] at h ⊢
    exact ⟨h.1, check_preds_mono hs hc a _ hp h.2⟩

theorem Plus.check' {E0 E : VE.Environment} {keep : String → Bool} {Γ : List String} (hE : EnvOK' E0 keep E)
    {a b : VE.Formula} (h : Plus E0 keep Γ a b) (ha : a.check E Γ = true) : b.check E Γ = true := by
  obtain ⟨cs, rfl, hcs⟩ := h
  rw [foldl_and_check]
  simp only [ha, Bool.true_and, List.all_eq_true]
  exact fun c hc => check_preds_mono hE.1 hE.2.1 c Γ
    (fun p hp s hs => hE.2.2 p s hs ((hcs c hc).2 p hp)) (hcs c hc).1

theorem EnvOK'.hide {E0 E : VE.Environment} {keep : String → Bool} (h : EnvOK' E0 keep E) (ns : List String)
    (hns : ∀ n ∈ ns, keep n = true) : EnvOK' E0 keep (VE.Norms.hide E ns) := by
  refine ⟨h.1, h.2.1, fun p s hp hk => ?_⟩
  have : p ∉ ns := fun hm => by rw [hns p hm] at hk; cases hk
  simp [VE.Norms.hide, this, h.2.2 p s hp hk]

theorem layerNames_keep (T : VE.Norms.Tree) : ∀ n ∈ layerNames T, keepOf T.regulated T.definitions n = true := by
  intro n hn
  simp only [layerNames, syms, List.mem_map, List.mem_filterMap, VE.Norms.lookupSym] at hn
  obtain ⟨q, ⟨m, -, hq⟩, rfl⟩ := hn
  simp only [keepOf, List.contains_iff_mem, List.mem_append, List.mem_map]
  split at hq
  · rename_i r hr; cases hq
    exact Or.inl ⟨r, List.mem_of_find?_eq_some hr, rfl⟩
  · cases hd : T.definitions.find? (·.name == m) with
    | none => simp [hd] at hq
    | some d => simp [hd] at hq; subst hq; exact Or.inr ⟨d, List.mem_of_find?_eq_some hd, rfl⟩

/-! ### What `mapG` keeps -/

variable (γ : String → VE.Formula → VE.Formula)

theorem incompatible_mapG (C : SoftDoc) (M N : SoftNode) :
    Incompatible (mapG γ C) (setG γ M) (setG γ N) = Incompatible C M N := rfl

theorem collidingPairs_mapG (C : SoftDoc) :
    collidingPairs (mapG γ C) = (collidingPairs C).map (fun x => (setG γ x.1, setG γ x.2)) := by
  unfold collidingPairs
  simp only [mapG_nodes, List.flatMap_map, List.filterMap_map, Function.comp_def]
  have hin : (C.T.nodes.flatMap fun a => C.T.nodes.filterMap fun x =>
      if (setG γ a).mode = .default ∧ (setG γ x).mode = .default ∧ (setG γ a).name < (setG γ x).name ∧
        Incompatible (mapG γ C) (setG γ a) (setG γ x) = true then some (setG γ a, setG γ x) else none) =
      (C.T.nodes.flatMap fun M => C.T.nodes.filterMap fun N =>
        if M.mode = .default ∧ N.mode = .default ∧ M.name < N.name ∧ Incompatible C M N = true
        then some (M, N) else none).map (fun x => (setG γ x.1, setG γ x.2)) := by
    rw [List.map_flatMap]
    congr 1; funext M
    rw [List.map_filterMap]
    congr 1; funext N
    simp only [setG_mode, setG_name, incompatible_mapG]
    split <;> rfl
  rw [hin, sortBy_map]
  rfl

theorem decisions_mapG (C : SoftDoc) : decisions (mapG γ C) = decisions C := by
  simp only [decisions, exceptedDecisions, offDecisions, outweighsDecisions, outweighsTriples, collidingPairs_mapG,
    mapG_nodes, mapG_soft, List.filter_map, List.map_map, List.flatMap_map, List.filterMap_map, Function.comp_def,
    setG_mode, setG_name, setG_pred, setG_alterable]
  rfl

theorem envPrime_mapG (C : SoftDoc) : envPrime (mapG γ C) = envPrime C := by
  simp only [envPrime, decisions_mapG, mapG_E]

theorem decisionNames_mapG (C : SoftDoc) : decisionNames (mapG γ C) = decisionNames C := by
  simp only [decisionNames, decisions_mapG]

/-! ### The hypotheses and the two W1 trees -/

/-- The extensions at predicate `p`: base conjuncts typed in `p`'s declared context. -/
def QC (C : SoftDoc) (E0 : VE.Environment) (p : String) : VE.Formula → VE.Formula → Prop :=
  Plus E0 (keepOf C.T.regulated C.T.definitions) (VE.SoftNorms.sortsOf C p).reverse

/-- What `validateSoft_mapG` needs of the new guards. -/
structure GHyp (C : SoftDoc) (E0 : VE.Environment) : Prop where
  guards : ∀ N ∈ C.T.nodes, FExt (QC C E0 N.pred) N.guard (γ N.name N.guard)
  dual : DualCtx (QC C E0) C
  envC : EnvOK' E0 (keepOf C.T.regulated C.T.definitions) C.E
  envP : EnvOK' E0 (keepOf C.T.regulated C.T.definitions) (envPrime C)

variable {γ}

theorem QC_preds {C : SoftDoc} {E0 : VE.Environment} :
    ∀ p a b, QC C E0 p a b → (preds b).filter (keepOf C.T.regulated C.T.definitions) =
      (preds a).filter (keepOf C.T.regulated C.T.definitions) := fun _ _ _ h => Plus.preds h

theorem baseTRel {C : SoftDoc} {E0 : VE.Environment} (h : GHyp γ C E0) :
    TRel (QC C E0) C.T.nodes SoftNode.toNode (fun N => (setG γ N).toNode) where
  name _ := rfl
  pred _ := rfl
  over _ := rfl
  sign _ := rfl
  rel N hN := ⟨h.guards N hN, N.carveOuts.map (fun c => (c, c)), by simp [Function.comp_def],
    by simp [Function.comp_def],
    fun c hc => by obtain ⟨c', -, rfl⟩ := List.mem_map.1 hc; exact .refl _⟩

theorem softenTRel {C : SoftDoc} {E0 : VE.Environment} (h : GHyp γ C E0) :
    TRel (QC C E0) C.T.nodes (primeNode C) (fun N => primeNode (mapG γ C) (setG γ N)) where
  name _ := rfl
  pred _ := rfl
  over _ := rfl
  sign _ := rfl
  rel N hN := by
    refine ⟨h.guards N hN, N.carveOuts.map (fun c => (c, c)) ++
      (if N.mode = .strict ∧ N.alterable = [] then [] else [(derived C N, derived (mapG γ C) (setG γ N))]), ?_, ?_, ?_⟩
    · simp only [primeNode, derivedList, List.map_append, List.map_map, Function.comp_def, List.map_id']
      split <;> rfl
    · simp only [primeNode, derivedList, List.map_append, List.map_map, Function.comp_def, List.map_id', setG_mode,
        setG_alterable, setG_carveOuts]
      split <;> rfl
    · intro c hc
      rcases List.mem_append.1 hc with hc | hc
      · obtain ⟨c', -, rfl⟩ := List.mem_map.1 hc; exact .refl _
      · split at hc
        · cases hc
        · simp only [List.mem_singleton] at hc; subst hc
          exact derived_ext C h.guards h.dual N

theorem mapG_base (C : SoftDoc) : (mapG γ C).base =
    ⟨C.E, C.lits, ⟨C.T.regulated, C.T.definitions, C.T.nodes.map (fun N => (setG γ N).toNode)⟩⟩ := by
  simp only [SoftDoc.base, mapG_E, mapG_lits, mapG_regulated, mapG_definitions, mapG_nodes, List.map_map]; rfl

theorem soften_mapG (C : SoftDoc) : soften (mapG γ C) =
    ⟨envPrime C, C.lits, ⟨C.T.regulated, C.T.definitions, C.T.nodes.map (fun N => primeNode (mapG γ C) (setG γ N))⟩⟩ := by
  simp only [soften, envPrime_mapG, mapG_lits, mapG_regulated, mapG_definitions, mapG_nodes, List.map_map]; rfl

theorem find?_name {l : List VE.Norms.Regulated} (hnd : (l.map (·.name)).Nodup) {r : VE.Norms.Regulated}
    (hr : r ∈ l) : l.find? (fun y => y.name == r.name) = some r := by
  induction l with
  | nil => cases hr
  | cons a l ih =>
    simp only [List.map_cons, List.nodup_cons, List.mem_map] at hnd
    rcases List.mem_cons.1 hr with rfl | hr
    · simp
    · have hne : (a.name == r.name) = false := by
        simp only [beq_eq_false_iff_ne]; intro he; exact hnd.1 ⟨r, hr, he.symm⟩
      simp [List.find?_cons, hne, ih hnd.2 hr]

theorem sortsOf_find {C : SoftDoc} {p : String} {r0 : VE.Norms.Regulated}
    (h : C.T.regulated.find? (fun y => y.name == p) = some r0) : VE.SoftNorms.sortsOf C p = r0.sorts := by
  simp [VE.SoftNorms.sortsOf, sortsIn, h]

theorem typesAt {C : SoftDoc} {E0 E : VE.Environment} {ι : Type} (L : List ι) (f : ι → Node)
    (hE : EnvOK' E0 (keepOf C.T.regulated C.T.definitions) E) : TypesAt (QC C E0) L f E C.T.regulated := by
  intro x _ r0 hr a b hab ha
  have hs := sortsOf_find hr
  unfold QC at hab; rw [hs] at hab
  exact Plus.check' hE hab ha

theorem validateW1_mapG {C : SoftDoc} {E0 : VE.Environment} (h : GHyp γ C E0)
    (hnd : (C.T.regulated.map (·.name)).Nodup) (hv : validateW1 (soften C) = .ok ()) :
    OkOrRL (validateW1 (soften (mapG γ C))) ∧
      (validateW1 (soften (mapG γ C)) = .ok () → VE.NormDefaults.RulesOK (soften (mapG γ C))) := by
  have ht := softenTRel h
  unfold validateW1 at hv ⊢
  rw [soften_mapG]
  split at hv
  · cases hv
  rename_i hc
  split at hv
  · rename_i hs
    have hw := ht.checkW1 (envPrime C) C.lits C.T.regulated C.T.definitions (typesAt _ _ h.envP) QC_preds hc
    rcases hw.1 with hw1 | ⟨e, he, hre⟩
    · rw [hw1]
      have hsem := ht.semanticCheck (envPrime C) C.lits C.T.regulated C.T.definitions QC_preds
        (fun r0 hr0 k a b hab ha => by
          have hs' := sortsOf_find (find?_name hnd hr0)
          unfold QC at hab; rw [hs'] at hab
          exact Plus.check' (h.envP.hide _ (fun n hn => layerNames_keep _ n (List.mem_of_mem_drop hn))) hab ha) hs
      simp only [hsem, if_true]
      exact ⟨Or.inl rfl, fun _ => hw.2 hw1⟩
    · rw [he]; exact ⟨Or.inr ⟨e, rfl, hre⟩, fun h' => by cases h'⟩
  · cases hv

/-! ### `softSemanticCheck` -/

theorem bindAll_check (E : VE.Environment) :
    ∀ (ss : List String) (φ : VE.Formula) (Γ : List String),
      (VE.Norms.bindAll ss φ).check E Γ = true ↔ (∀ s ∈ ss, s ∈ E.sorts) ∧ φ.check E (ss.reverse ++ Γ) = true
  | [], φ, Γ => by simp [VE.Norms.bindAll]
  | s :: ss, φ, Γ => by
    have := bindAll_check E ss φ (s :: Γ)
    simp only [VE.Norms.bindAll, List.foldr_cons] at this ⊢
    simp only [VE.Formula.check, Bool.and_eq_true, List.contains_iff_mem, this, List.mem_cons, forall_eq_or_imp,
      List.reverse_cons, List.append_assoc, List.singleton_append, and_assoc]

theorem wellFormed_check {D : VE.Norms.Doc} (h : VE.Norms.WellFormed D = true) : VE.Norms.check D = .ok () := by
  unfold VE.Norms.WellFormed VE.Norms.validate at h
  split at h <;> rename_i heq
  · split at heq
    · cases heq
    · rename_i hc; cases hc' : VE.Norms.check D <;> simp_all
  · cases h

section SS
variable {C : SoftDoc} {E0 : VE.Environment} (h : GHyp γ C E0) (hnd : (C.T.regulated.map (·.name)).Nodup)
include h

/-- The complete environment of `soften (mapG γ C)` is `soften C`'s, and shows the base conjuncts. -/
theorem envAt_mapG (k : Nat) : envAt (soften (mapG γ C)) k = envAt (soften C) k := by
  have hs := (softenTRel h).syms C.T.regulated C.T.definitions QC_preds
  simp only [envAt, soften_mapG, layerNames, hs]; rfl

theorem size_mapG : size (soften (mapG γ C)) = size (soften C) := by
  have hs := (softenTRel h).syms C.T.regulated C.T.definitions QC_preds
  simp only [size, soften_mapG, hs]; rfl

theorem envOK_envAt (k : Nat) : EnvOK' E0 (keepOf C.T.regulated C.T.definitions) (envAt (soften C) k) :=
  h.envP.hide _ (fun n hn => layerNames_keep _ n (List.mem_of_mem_drop hn))

/-- `selects′` of a changed node extends the old one. -/
theorem selects'_ext (N : SoftNode) (hN : N ∈ C.T.nodes) :
    FExt (QC C E0 N.pred) (selects' C N) (selects' (mapG γ C) (setG γ N)) := by
  have := selects_ext (softenTRel h) C.T.regulated C.T.definitions C.T.nodes.length N hN
  unfold selects'
  rw [soften_mapG]
  have hl : (soften C).T.nodes.length = C.T.nodes.length := by simp [soften]
  simp only [VE.Norms.fuel, List.length_map, hl]
  exact this

theorem selects'_check (N : SoftNode) (hN : N ∈ C.T.nodes)
    (hc : (selects' C N).check (envAt (soften C) (size (soften C))) (sortsOf C N.pred).reverse = true) :
    (selects' (mapG γ C) (setG γ N)).check (envAt (soften (mapG γ C)) (size (soften (mapG γ C))))
      (sortsOf C N.pred).reverse = true := by
  rw [envAt_mapG h, size_mapG h]
  exact FExt.check (fun a b hab => Plus.check' (envOK_envAt h _) hab) (selects'_ext h N hN) hc

theorem decides_check (p : String) (hp : ∀ r0 ∈ C.T.regulated, r0.name = p → True) (sign : Bool) {Γ : List String}
    (hΓ : (sortsOf C p).reverse = Γ)
    (hs : (strictDecidesF C p sign).check (envAt (soften C) (size (soften C))) Γ = true)
    (hd : (defaultDecidesF C p sign).check (envAt (soften C) (size (soften C))) Γ = true) :
    (strictDecidesF (mapG γ C) p sign).check (envAt (soften (mapG γ C)) (size (soften (mapG γ C)))) Γ = true ∧
    (defaultDecidesF (mapG γ C) p sign).check (envAt (soften (mapG γ C)) (size (soften (mapG γ C)))) Γ = true := by
  subst hΓ
  rw [envAt_mapG h, size_mapG h]
  have hP := fun a b (hab : QC C E0 p a b) => Plus.check' (envOK_envAt h (size (soften C))) hab
  refine ⟨FExt.check hP (strictDecidesF_ext (QC C E0) C h.guards p sign) hs, ?_⟩
  refine FExt.check hP ?_ hd
  simp only [defaultDecidesF, rulesOn, mapG_nodes, List.filter_map, List.map_map, Function.comp_def, setG_pred,
    setG_mode, setG_sign]
  refine FExt.anyF _ _ _ (fun N hN => ?_)
  simp only [List.mem_filter, beq_iff_eq] at hN
  have := selects'_ext h N hN.1.1.1
  rw [hN.1.1.2] at this
  exact this

end SS

end VE.RightClauses.PWF
