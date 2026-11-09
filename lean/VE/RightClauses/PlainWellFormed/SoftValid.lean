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

end VE.RightClauses.PWF
