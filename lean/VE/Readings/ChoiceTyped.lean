import VE.Readings.ChoiceValid

/-! The vocabulary of a compatible choice's document and the typing of its elaboration (docs/spec/composition-s2.md
8.4, the structural part of `choice_wellFormed`, continued).

The decision predicates of a choice's document are fresh in the frame and determined by their names; its
`outweighs` triples are `sup D`'s. Every formula a rule of its elaboration carries, the generated carve-out
included, is typed over `E′` in the rule's context, and every layer symbol it reads comes earlier in the stratum
order, so `soften Y` is `VE.Norms.Valid` (`choice_valid`). -/
namespace VE.Readings
open VE.Norms (envAt size preds anyF atom Arity Regulated)
open VE.SoftNorms (SoftNode SoftDoc soften coreNode liveStrictIn strictYieldsIn strictSelectsIn strictDecidesIn
  strictDecidesF blockedF eligibleF liveF exceptedF switchF switchIn outweighsF domWith effF opponents derived
  derivedList childrenIn mem_preds_anyF WellFormedSoft decisions decisionNames envPrime)
open VE.Rights (RightsDoc correlate)
open VE.Route (DepNode DepEdge DepPath DagAcyclic nodeNames deps)

/-- A formula keeps its type over an environment with the same sorts and constants that declares its predicates
    alike. -/
theorem wf_congr {E E' : VE.Environment} (hs : E'.sorts = E.sorts) (hc : E'.constants = E.constants) :
    ∀ (φ : VE.Formula) (Γ : List String), φ.WellFormed E Γ → (∀ p ∈ preds φ, E'.predicates p = E.predicates p) →
      φ.WellFormed E' Γ
  | .top, _, _, _ | .bottom, _, _, _ => trivial
  | .unary p t, Γ, ⟨s, hp, ht⟩, h => ⟨s, by rw [h p (by simp [preds])]; exact hp,
      by rw [VE.Norms.sortOf_congr hc]; exact ht⟩
  | .binary p t w, Γ, ⟨s, r, hp, ht, hw⟩, h => ⟨s, r, by rw [h p (by simp [preds])]; exact hp,
      by rw [VE.Norms.sortOf_congr hc]; exact ht, by rw [VE.Norms.sortOf_congr hc]; exact hw⟩
  | .eq t w, Γ, ⟨s, ht, hw⟩, _ => ⟨s, by rw [VE.Norms.sortOf_congr hc]; exact ht,
      by rw [VE.Norms.sortOf_congr hc]; exact hw⟩
  | .not a, Γ, hw, h => wf_congr hs hc a Γ hw h
  | .and a b, Γ, hw, h | .or a b, Γ, hw, h | .implies a b, Γ, hw, h =>
    ⟨wf_congr hs hc a Γ hw.1 (fun p hp => h p (by simp [preds, hp])),
     wf_congr hs hc b Γ hw.2 (fun p hp => h p (by simp [preds, hp]))⟩
  | .all s a, Γ, hw, h | .ex s a, Γ, hw, h => ⟨hs ▸ hw.1, wf_congr hs hc a (s :: Γ) hw.2 h⟩

theorem anyF_wf {E : VE.Environment} {Γ : List String} (l : List VE.Formula) (h : ∀ a ∈ l, a.WellFormed E Γ) :
    (anyF l).WellFormed E Γ := by
  suffices ∀ acc : VE.Formula, acc.WellFormed E Γ → (l.foldl .or acc).WellFormed E Γ from this _ trivial
  induction l with
  | nil => intro acc h; exact h
  | cons a l ih =>
    intro acc hacc
    exact ih (fun x hx => h x (List.mem_cons_of_mem _ hx)) _ ⟨hacc, h a List.mem_cons_self⟩

/-! ## The `outweighs` triples of a choice's document are `sup D`'s -/

section Triples
variable {D : Doc} (hh : Hyps D) (c : Choice)
include hh

theorem triple_sup {x : String × String × String} (hx : x ∈ VE.SoftNorms.outweighsTriples (choiceDoc D c).1.soft) :
    x ∈ VE.SoftNorms.outweighsTriples (sup D).1.soft := by
  obtain ⟨hol, M, N, hp, hcmp, ht⟩ := mem_outweighsTriples.mp hx
  obtain ⟨hM, hN, hMd, hNd, hlt, hinc⟩ := VE.SoftNorms.mem_collidingPairs.mp hp
  have hsv := sup_softValid hh
  have hsoft := soft_eq (D := D) c
  have hdp := dualPerm_eq (D := D) c
  obtain ⟨hMp, hMs, hMm, hMr, _⟩ := fmap_fields hh c hM
  obtain ⟨hNp, hNs, hNm, hNr, _⟩ := fmap_fields hh c hN
  have hhi : ∀ A B : SoftNode, A ∈ (choiceDoc D c).1.soft.T.nodes → B ∈ (choiceDoc D c).1.soft.T.nodes →
      VE.SoftNorms.higher (sup D).1.soft (fmap D c A) (fmap D c B) = VE.SoftNorms.higher (choiceDoc D c).1.soft A B := by
    intro A B hA hB
    simp only [VE.SoftNorms.higher, (fmap_fields hh c hA).2.2.2.1, (fmap_fields hh c hB).2.2.2.1, hsoft]
  have hact : ∀ A, A ∈ (choiceDoc D c).1.soft.T.nodes →
      VE.SoftNorms.act (sup D).1.soft (fmap D c A) = VE.SoftNorms.act (choiceDoc D c).1.soft A := by
    intro A hA; simp only [VE.SoftNorms.act, VE.SoftNorms.actKey, (fmap_fields hh c hA).1, hdp]
  have hrk : ∀ A, A ∈ (choiceDoc D c).1.soft.T.nodes → VE.SoftNorms.rk (fmap D c A) = VE.SoftNorms.rk A := by
    intro A hA; simp only [VE.SoftNorms.rk, (fmap_fields hh c hA).2.2.2.1]
  have hinc' : VE.SoftNorms.Incompatible (sup D).1.soft (fmap D c M) (fmap D c N) = true := by
    rw [← hinc]; simp only [VE.SoftNorms.Incompatible, hMp, hNp, hMs, hNs, hdp]
  have hne : (fmap D c M).name ≠ (fmap D c N).name := by
    intro he
    have := fmap_inj hh c hM hN (sup_name_inj hh (fmap_mem hh c hM) (fmap_mem hh c hN) he)
    subst this
    exact absurd hlt (String.lt_irrefl _)
  apply mem_outweighsTriples.mpr
  refine ⟨by rw [hsoft]; exact hol, ?_⟩
  have hrv : VE.SoftNorms.RanksValid (choiceDoc D c).1.soft.soft := by rw [← hsoft]; exact hsv.ranks
  rcases VE.SoftNorms.str_lt_or_gt _ _ hne with hl | hl
  · refine ⟨fmap D c M, fmap D c N, VE.SoftNorms.mem_collidingPairs.mpr ⟨fmap_mem hh c hM, fmap_mem hh c hN,
      by rw [hMm]; exact hMd, by rw [hNm]; exact hNd, hl, hinc'⟩, ?_, ?_⟩
    · simp only [VE.SoftNorms.Comparable, hhi M N hM hN, hhi N M hN hM]; exact hcmp
    · simp only [VE.SoftNorms.pairTriple, hhi M N hM hN, hact M hM, hact N hN, hrk M hM, hrk N hN] at ht ⊢
      exact ht
  · refine ⟨fmap D c N, fmap D c M, VE.SoftNorms.mem_collidingPairs.mpr ⟨fmap_mem hh c hN, fmap_mem hh c hM,
      by rw [hNm]; exact hNd, by rw [hMm]; exact hMd, hl, by rw [VE.SoftNorms.incompatible_symm]; exact hinc'⟩, ?_, ?_⟩
    · simp only [VE.SoftNorms.Comparable, hhi M N hM hN, hhi N M hN hM, Bool.or_comm]; exact hcmp
    · have hacts : VE.SoftNorms.act (choiceDoc D c).1.soft M = VE.SoftNorms.act (choiceDoc D c).1.soft N :=
        act_choice_eq hh c hM hN hinc
      simp only [VE.SoftNorms.pairTriple, hhi M N hM hN, hhi N M hN hM, hact M hM, hact N hN, hrk M hM,
        hrk N hN] at ht ⊢
      simp only [VE.SoftNorms.Comparable, Bool.or_eq_true] at hcmp
      rcases hcmp with h1 | h1
      · have h2 := VE.SoftNorms.higher_asymm hrv h1
        rw [h1] at ht; rw [h2]; simp only [if_true, Bool.false_eq_true, if_false] at ht ⊢; exact ht
      · have h2 := VE.SoftNorms.higher_asymm hrv h1
        rw [h2] at ht; rw [h1]; simp only [if_true, Bool.false_eq_true, if_false] at ht ⊢
        rw [← ht, hacts]

end Triples

/-! ## The decision vocabulary of a choice's document -/

section Vocab
variable {D : Doc} (hh : Hyps D) (c : Choice)
include hh

omit hh in
theorem choice_E : (choiceDoc D c).1.soft.E = D.frame.soft.E := (build_shape D (fun _ => true) (pickC c)).E

omit hh in
theorem choice_reg : (choiceDoc D c).1.soft.T.regulated = D.frame.soft.T.regulated :=
  (build_shape D (fun _ => true) (pickC c)).regulated

omit hh in
theorem choice_defs : (choiceDoc D c).1.soft.T.definitions = D.frame.soft.T.definitions :=
  (build_shape D (fun _ => true) (pickC c)).definitions

/-- An `outweighs` name of `sup D` is not declared in the frame. -/
theorem outweighs_frame_fresh {a L H : String} (ht : (a, L, H) ∈ VE.SoftNorms.outweighsTriples (sup D).1.soft) :
    D.frame.soft.E.predicates (VE.SoftNorms.outweighsName a L H) = none := by
  have hv := sup_softValid hh
  have hd : (VE.SoftNorms.outweighsName a L H, VE.SoftNorms.actSortsOf (sup D).1.soft a) ∈ decisions (sup D).1.soft :=
    mem_decisions.mpr (Or.inr (Or.inr ⟨a, L, H, ht, rfl⟩))
  have := hv.decFresh _ (List.mem_map.mpr ⟨_, hd, rfl⟩)
  rw [sup_E] at this
  unfold choiceEnv at this
  split at this
  · exact this
  · simp only at this
    rw [List.find?_eq_none.mpr (fun x hx he => by
      have hxb : ∃ m j, x.1 = bitName m j := by
        simp only [bitDecls, List.mem_flatMap, List.mem_map] at hx
        obtain ⟨m, _, j, _, rfl⟩ := hx
        exact ⟨m + 1, j, rfl⟩
      obtain ⟨m, j, hmj⟩ := hxb
      have h1 := decision_head (X := (sup D).1.soft) (List.mem_map.mpr ⟨_, hd, rfl⟩)
      have h2 : x.1 = VE.SoftNorms.outweighsName a L H := by simpa using he
      rw [← h2, hmj, bitName_head] at h1
      cases h1)] at this
    exact this

/-- The decision predicates of a choice's document are not declared in the frame. -/
theorem choice_decision_fresh {d : String × List String} (hd : d ∈ decisions (choiceDoc D c).1.soft) :
    D.frame.soft.E.predicates d.1 = none := by
  rcases mem_decisions.mp hd with ⟨N, hN, hdm, rfl⟩ | ⟨N, hN, π, hπ, rfl⟩ | ⟨a, L, H, ht, rfl⟩
  · exact (choice_nodeFacts hh c hN).2.2.1 hdm
  · exact (choice_nodeFacts hh c hN).2.2.2.1 π hπ
  · exact outweighs_frame_fresh hh (triple_sup hh c ht)

omit hh in
theorem sortsOf_choice (p : String) :
    VE.SoftNorms.sortsOf (choiceDoc D c).1.soft p = VE.SoftNorms.sortsOf (sup D).1.soft p := by
  simp only [VE.SoftNorms.sortsOf, regs_eq c]

omit hh in
theorem actSortsOf_choice (a : String) :
    VE.SoftNorms.actSortsOf (choiceDoc D c).1.soft a = VE.SoftNorms.actSortsOf (sup D).1.soft a := by
  simp only [VE.SoftNorms.actSortsOf, sortsOf_choice c]

/-- A decision predicate of a choice's document is determined by its name. -/
theorem choice_decision_inj {d d' : String × List String} (hd : d ∈ decisions (choiceDoc D c).1.soft)
    (hd' : d' ∈ decisions (choiceDoc D c).1.soft) (he : d.1 = d'.1) : d = d' := by
  have hv := sup_softValid hh
  rcases mem_decisions.mp hd with ⟨N, hN, _, rfl⟩ | ⟨N, hN, π, hπ, rfl⟩ | ⟨a, L, H, ht, rfl⟩ <;>
    rcases mem_decisions.mp hd' with ⟨N', hN', _, rfl⟩ | ⟨N', hN', π', hπ', rfl⟩ | ⟨a', L', H', ht', rfl⟩ <;>
    simp only at he
  · have := choice_name_inj hh c hN hN' (exceptedName_inj (choice_nodeFacts hh c hN).1
      (choice_nodeFacts hh c hN').1 he)
    subst this; rfl
  · exact absurd he (exceptedName_ne_offName N N' π')
  · exact absurd he (exceptedName_ne_outweighsName N a' L' H')
  · exact absurd he.symm (exceptedName_ne_offName N' N π)
  · obtain ⟨h1, rfl⟩ := offName_inj (choice_nodeFacts hh c hN).1 (choice_nodeFacts hh c hN').1
      ((choice_nodeFacts hh c hN).2.2.2.2 π hπ) ((choice_nodeFacts hh c hN').2.2.2.2 π' hπ') he
    have := choice_name_inj hh c hN hN' h1
    subst this; rfl
  · exact absurd he (offName_ne_outweighsName N π a' L' H')
  · exact absurd he.symm (exceptedName_ne_outweighsName N' a L H)
  · exact absurd he.symm (offName_ne_outweighsName N' π' a L H)
  · have hx := mem_decisions.mpr (Or.inr (Or.inr ⟨a, L, H, triple_sup hh c ht, rfl⟩))
    have hx' := mem_decisions.mpr (Or.inr (Or.inr ⟨a', L', H', triple_sup hh c ht', rfl⟩))
    have := inj_of_nodup_map hv.decNodup hx hx' he
    simp only [Prod.mk.injEq] at this
    rw [actSortsOf_choice c, actSortsOf_choice c, this.2]
    simp only [he]

theorem choice_envPrime_decision {d : String × List String} (hd : d ∈ decisions (choiceDoc D c).1.soft) :
    (envPrime (choiceDoc D c).1.soft).predicates d.1 = some d.2 := by
  unfold envPrime
  simp only
  cases hf : (decisions (choiceDoc D c).1.soft).find? (·.1 == d.1) with
  | none => exact absurd (List.find?_eq_none.mp hf d hd) (by simp)
  | some d' =>
    have := choice_decision_inj hh c (List.mem_of_find?_eq_some hf) hd (by simpa using List.find?_some hf)
    subst this; rfl

theorem choice_envPrime_frame {p : String} (hp : D.frame.soft.E.predicates p ≠ none) :
    (envPrime (choiceDoc D c).1.soft).predicates p = D.frame.soft.E.predicates p := by
  unfold envPrime
  simp only
  rw [List.find?_eq_none.mpr (fun x hx he => by
    have := choice_decision_fresh hh c hx
    rw [show x.1 = p by simpa using he] at this
    exact hp this), choice_E]

/-- An author formula over the frame is typed over the choice's `E′`. -/
theorem lift_frame {φ : VE.Formula} {Γ : List String} (hφ : φ.WellFormed D.frame.soft.E Γ) :
    φ.WellFormed (envPrime (choiceDoc D c).1.soft) Γ := by
  apply wf_congr (by show (choiceDoc D c).1.soft.E.sorts = _; rw [choice_E])
    (by show (choiceDoc D c).1.soft.E.constants = _; rw [choice_E]) φ Γ hφ
  intro p hp
  have := VE.SoftNorms.preds_declared φ hφ hp
  exact choice_envPrime_frame hh c (by simpa [Option.isSome_iff_ne_none] using this)

end Vocab

/-! ## The generated carve-outs are typed (Lemma T) -/

section Typed
variable {D : Doc} (hh : Hyps D) (c : Choice)
include hh

/-- The context of a rule's formulas in the choice's document. -/
abbrev ctxY (D : Doc) (c : Choice) (p : String) : List String :=
  (VE.SoftNorms.sortsOf (choiceDoc D c).1.soft p).reverse

theorem node_arity {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) :
    Arity (VE.SoftNorms.sortsOf (choiceDoc D c).1.soft N.pred) := by
  have hv := sup_softValid hh
  have hvX := VE.Norms.valid_of_wellFormed _ hv.wf
  obtain ⟨r, hr, hrn, hrs⟩ := VE.SoftNorms.reg_of_node hv (fmap_mem hh c hN)
  rw [sortsOf_choice, ← (fmap_fields hh c hN).1, ← hrs]
  exact (hvX.decl _ (hvX.regulated r hr)).2.1

theorem dual_sorts {p m : String} (h : VE.SoftNorms.dualPerm (choiceDoc D c).1.soft p = some m) :
    VE.SoftNorms.sortsOf (choiceDoc D c).1.soft m = VE.SoftNorms.sortsOf (choiceDoc D c).1.soft p := by
  have hv := sup_softValid hh
  rw [← dualPerm_eq c] at h
  simp only [VE.SoftNorms.dualPerm, Option.map_eq_some_iff] at h
  obtain ⟨pr, hpr, rfl⟩ := h
  have hp : pr.req = p := by simpa using List.find?_some hpr
  obtain ⟨⟨r, hr, hrn, hrs⟩, ⟨m', hm', hmn, hms⟩⟩ := VE.SoftNorms.pair_regs hv (List.mem_of_find?_eq_some hpr)
  rw [sortsOf_choice, sortsOf_choice, ← hp, ← hrn, ← hmn, VE.SoftNorms.sortsOf_reg hv hr,
    VE.SoftNorms.sortsOf_reg hv hm', hrs, hms]

theorem dualOblig_sorts {p r : String} (h : VE.SoftNorms.dualOblig (choiceDoc D c).1.soft p = some r) :
    VE.SoftNorms.sortsOf (choiceDoc D c).1.soft r = VE.SoftNorms.sortsOf (choiceDoc D c).1.soft p := by
  have hv := sup_softValid hh
  have hdo : VE.SoftNorms.dualOblig (sup D).1.soft = VE.SoftNorms.dualOblig (choiceDoc D c).1.soft := by
    funext r
    simp only [VE.SoftNorms.dualOblig, VE.SoftNorms.SoftDoc.base, VE.Norms.pairs, regs_eq c]
  rw [← hdo] at h
  simp only [VE.SoftNorms.dualOblig, Option.map_eq_some_iff] at h
  obtain ⟨pr, hpr, rfl⟩ := h
  have hp : pr.perm = p := by simpa using List.find?_some hpr
  obtain ⟨⟨r', hr', hrn, hrs⟩, ⟨m', hm', hmn, hms⟩⟩ := VE.SoftNorms.pair_regs hv (List.mem_of_find?_eq_some hpr)
  rw [sortsOf_choice, sortsOf_choice, ← hp, ← hrn, ← hmn, VE.SoftNorms.sortsOf_reg hv hr',
    VE.SoftNorms.sortsOf_reg hv hm', hrs, hms]

theorem act_sorts (N : SoftNode) :
    VE.SoftNorms.sortsOf (choiceDoc D c).1.soft (VE.SoftNorms.act (choiceDoc D c).1.soft N) =
      VE.SoftNorms.sortsOf (choiceDoc D c).1.soft N.pred := by
  unfold VE.SoftNorms.act VE.SoftNorms.actKey
  cases h : VE.SoftNorms.dualPerm (choiceDoc D c).1.soft N.pred with
  | none => rfl
  | some m => exact dual_sorts hh c h

theorem incompatible_sorts {M N : SoftNode} (h : VE.SoftNorms.Incompatible (choiceDoc D c).1.soft M N = true) :
    VE.SoftNorms.sortsOf (choiceDoc D c).1.soft M.pred = VE.SoftNorms.sortsOf (choiceDoc D c).1.soft N.pred := by
  by_cases hp : M.pred = N.pred
  · rw [hp]
  · unfold VE.SoftNorms.Incompatible at h
    generalize hA : VE.SoftNorms.dualPerm (choiceDoc D c).1.soft M.pred = A at h
    generalize hB : VE.SoftNorms.dualPerm (choiceDoc D c).1.soft N.pred = B at h
    have hpb : (M.pred == N.pred) = false := by simpa using hp
    rw [hpb] at h
    cases A with
    | some a =>
      cases B with
      | some b =>
        by_cases ha : a = N.pred
        · subst ha; exact (dual_sorts hh c hA).symm
        · by_cases hb : b = M.pred
          · subst hb; exact dual_sorts hh c hB
          · simp [ha, hb] at h
      | none =>
        by_cases ha : a = N.pred
        · subst ha; exact (dual_sorts hh c hA).symm
        · simp [ha] at h
    | none =>
      cases B with
      | some b =>
        by_cases hb : b = M.pred
        · subst hb; exact dual_sorts hh c hB
        · simp [hb] at h
      | none => simp at h

theorem typed_switch (core : Bool) {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) :
    (switchIn (choiceDoc D c).1.soft.T.regulated (if core then coreNode N else N)).WellFormed
      (envPrime (choiceDoc D c).1.soft) (ctxY D c N.pred) := by
  apply anyF_wf
  intro a ha
  obtain ⟨π, hπ, rfl⟩ := List.mem_map.mp ha
  have hπN : π ∈ N.alterable := by
    cases core
    · exact hπ
    · simp only [coreNode, if_true] at hπ; split at hπ
      · exact hπ
      · cases hπ
  have hd : (VE.SoftNorms.offName N π, VE.SoftNorms.sortsOf (choiceDoc D c).1.soft N.pred) ∈
      decisions (choiceDoc D c).1.soft := mem_decisions.mpr (Or.inr (Or.inl ⟨N, hN, π, hπN, rfl⟩))
  have hdecl := choice_envPrime_decision hh c hd
  have hname : VE.SoftNorms.offName (if core then coreNode N else N) π = VE.SoftNorms.offName N π := by
    cases core <;> rfl
  have hpred : (if core then coreNode N else N).pred = N.pred := by cases core <;> rfl
  rw [hname, hpred]
  exact VE.Norms.atom_wellFormed (node_arity hh c hN) hdecl

theorem typed_author {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) :
    ∀ φ ∈ N.guard :: N.carveOuts, φ.WellFormed (envPrime (choiceDoc D c).1.soft) (ctxY D c N.pred) := by
  intro φ hφ
  have := (choice_nodeFacts hh c hN).2.1 φ hφ
  apply lift_frame hh c
  simpa [ctxY, VE.SoftNorms.sortsOf, choice_reg] using this

theorem typed_live (core : Bool) {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) :
    (liveStrictIn (choiceDoc D c).1.soft.T.regulated (if core then coreNode N else N)).WellFormed
      (envPrime (choiceDoc D c).1.soft) (ctxY D c N.pred) := by
  have hg : (if core then coreNode N else N).guard = N.guard := by cases core <;> rfl
  have hco : (if core then coreNode N else N).carveOuts = N.carveOuts := by cases core <;> rfl
  refine ⟨⟨?_, anyF_wf _ (fun U hU => ?_)⟩, typed_switch hh c core hN⟩
  · rw [hg]; exact typed_author hh c hN _ List.mem_cons_self
  · rw [hco] at hU; exact typed_author hh c hN U (List.mem_cons_of_mem _ hU)

theorem typed_yields : ∀ (f : Nat) (N : SoftNode), N ∈ (choiceDoc D c).1.soft.T.nodes →
    (strictYieldsIn (choiceDoc D c).1.soft.T.regulated ((choiceDoc D c).1.soft.T.nodes.map coreNode) f
      (coreNode N)).WellFormed (envPrime (choiceDoc D c).1.soft) (ctxY D c N.pred)
  | 0, N, hN => by
    refine ⟨?_, trivial⟩
    split
    · simpa using typed_live hh c true hN
    · trivial
  | f + 1, N, hN => by
    refine ⟨?_, anyF_wf _ (fun a ha => ?_)⟩
    · split
      · simpa using typed_live hh c true hN
      · trivial
    · obtain ⟨C, hC, rfl⟩ := List.mem_map.mp ha
      obtain ⟨hCm, hp, _⟩ := VE.SoftNorms.mem_childrenIn_iff.mp hC
      obtain ⟨C₀, hC₀, rfl⟩ := List.mem_map.mp hCm
      have := typed_yields f C₀ hC₀
      rw [show (coreNode C₀).pred = C₀.pred from rfl] at hp
      rw [show (coreNode N).pred = N.pred from rfl] at hp
      rw [hp] at this
      exact this

theorem typed_decides (p : String) (sign : Bool) :
    (strictDecidesF (choiceDoc D c).1.soft p sign).WellFormed (envPrime (choiceDoc D c).1.soft) (ctxY D c p) := by
  apply anyF_wf
  intro a ha
  simp only [List.mem_map, List.mem_filter, beq_iff_eq] at ha
  obtain ⟨M, ⟨⟨hM, hp⟩, _⟩, rfl⟩ := ha
  obtain ⟨M₀, hM₀, rfl⟩ := hM
  rw [show (coreNode M₀).pred = M₀.pred from rfl] at hp
  unfold strictSelectsIn
  split
  · refine ⟨?_, anyF_wf _ (fun b hb => ?_)⟩
    · rw [← hp]; simpa using typed_live hh c true hM₀
    · obtain ⟨C, hC, rfl⟩ := List.mem_map.mp hb
      obtain ⟨hCm, hCp, _⟩ := VE.SoftNorms.mem_childrenIn_iff.mp hC
      obtain ⟨C₀, hC₀, rfl⟩ := List.mem_map.mp hCm
      have := typed_yields hh c (List.map coreNode (choiceDoc D c).1.soft.T.nodes).length C₀ hC₀
      rw [show (coreNode C₀).pred = C₀.pred from rfl, show (coreNode M₀).pred = M₀.pred from rfl] at hCp
      rw [hCp, hp] at this
      exact this
  · trivial

theorem typed_blocked {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) :
    (blockedF (choiceDoc D c).1.soft N).WellFormed (envPrime (choiceDoc D c).1.soft) (ctxY D c N.pred) := by
  refine ⟨⟨⟨typed_decides hh c _ _, typed_decides hh c _ _⟩, ?_⟩, ?_⟩
  · split
    · split
      · rename_i m hm
        have := typed_decides hh c m false
        simp only [ctxY] at this ⊢
        rw [dual_sorts hh c hm] at this
        exact this
      · trivial
    · trivial
  · split
    · trivial
    · split
      · rename_i r hr
        have := typed_decides hh c r true
        simp only [ctxY] at this ⊢
        rw [dualOblig_sorts hh c hr] at this
        exact this
      · trivial

theorem typed_excepted {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) (hd : N.mode = .default) :
    (exceptedF (choiceDoc D c).1.soft N).WellFormed (envPrime (choiceDoc D c).1.soft) (ctxY D c N.pred) := by
  have hm : (VE.SoftNorms.exceptedName N, VE.SoftNorms.sortsOf (choiceDoc D c).1.soft N.pred) ∈
      decisions (choiceDoc D c).1.soft := mem_decisions.mpr (Or.inl ⟨N, hN, hd, rfl⟩)
  exact VE.Norms.atom_wellFormed (node_arity hh c hN) (choice_envPrime_decision hh c hm)

theorem typed_eligible {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) :
    (eligibleF (choiceDoc D c).1.soft N).WellFormed (envPrime (choiceDoc D c).1.soft) (ctxY D c N.pred) := by
  unfold eligibleF
  split
  · rename_i hd
    refine ⟨⟨by simpa using typed_live hh c false hN, ?_⟩, typed_blocked hh c hN⟩
    rw [if_pos hd]
    exact typed_excepted hh c hN hd
  · trivial

theorem typed_domWith (eff : SoftNode → VE.Formula)
    (heff : ∀ M ∈ (choiceDoc D c).1.soft.T.nodes, M.mode = .default →
      (eff M).WellFormed (envPrime (choiceDoc D c).1.soft) (ctxY D c M.pred))
    {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) (hNd : N.mode = .default) :
    (domWith (choiceDoc D c).1.soft eff N).WellFormed (envPrime (choiceDoc D c).1.soft) (ctxY D c N.pred) := by
  apply anyF_wf
  intro a ha
  obtain ⟨M, hM, rfl⟩ := List.mem_map.mp ha
  simp only [opponents, List.mem_filter, Bool.and_eq_true, beq_iff_eq] at hM
  obtain ⟨hMm, ⟨hinc, hmd⟩, _⟩ := hM
  have hctx : ctxY D c M.pred = ctxY D c N.pred := by simp only [ctxY, incompatible_sorts hh c hinc]
  have hout : ∀ {L H : String}, (VE.SoftNorms.act (choiceDoc D c).1.soft N, L, H) ∈
      VE.SoftNorms.outweighsTriples (choiceDoc D c).1.soft →
      (outweighsF (choiceDoc D c).1.soft (VE.SoftNorms.act (choiceDoc D c).1.soft N) L H).WellFormed
        (envPrime (choiceDoc D c).1.soft) (ctxY D c N.pred) := by
    intro L H ht
    have hm : (VE.SoftNorms.outweighsName (VE.SoftNorms.act (choiceDoc D c).1.soft N) L H,
        VE.SoftNorms.actSortsOf (choiceDoc D c).1.soft (VE.SoftNorms.act (choiceDoc D c).1.soft N)) ∈
        decisions (choiceDoc D c).1.soft := mem_decisions.mpr (Or.inr (Or.inr ⟨_, L, H, ht, rfl⟩))
    have hdecl := choice_envPrime_decision hh c hm
    simp only [VE.SoftNorms.actSortsOf, act_sorts hh c] at hdecl
    unfold outweighsF
    simp only [VE.SoftNorms.actSortsOf, act_sorts hh c]
    exact VE.Norms.atom_wellFormed (node_arity hh c hN) hdecl
  have ht := fun hol => outweighs_triple hh c hMm hN hinc hmd hNd hol
  refine ⟨?_, ?_⟩
  · split
    · rename_i hhi
      refine ⟨by rw [← hctx]; exact heff M hMm hmd, ?_⟩
      split
      · rename_i hol
        exact hout ((ht hol).1 hhi)
      · trivial
    · trivial
  · split
    · rename_i hh2
      refine ⟨by rw [← hctx]; exact typed_eligible hh c hMm, hout ((ht hh2.1).2 hh2.2)⟩
    · trivial

theorem typed_effF : ∀ (g : Nat) (N : SoftNode), N ∈ (choiceDoc D c).1.soft.T.nodes → N.mode = .default →
    (effF (choiceDoc D c).1.soft g N).WellFormed (envPrime (choiceDoc D c).1.soft) (ctxY D c N.pred)
  | 0, N, hN, _ => typed_eligible hh c hN
  | g + 1, N, hN, hd => ⟨typed_eligible hh c hN, typed_domWith hh c _ (fun M hM hMd => typed_effF g M hM hMd) hN hd⟩

theorem typed_derived {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) :
    (derived (choiceDoc D c).1.soft N).WellFormed (envPrime (choiceDoc D c).1.soft) (ctxY D c N.pred) := by
  unfold derived
  cases hm : N.mode with
  | strict => simpa [switchF] using typed_switch hh c false hN
  | default =>
    exact ⟨⟨⟨typed_excepted hh c hN hm, by simpa [switchF] using typed_switch hh c false hN⟩, typed_blocked hh c hN⟩,
      typed_domWith hh c _ (fun M hM hMd => typed_effF hh c _ M hM hMd) hN hm⟩

end Typed

/-! ## Orders and layer names -/

theorem idxOf_getElem_nodup : ∀ (l : List String), l.Nodup → ∀ (k : Nat) (h : k < l.length), l.idxOf l[k] = k
  | [], _, _, h => by simp at h
  | a :: l, hn, k, h => by
    rw [List.nodup_cons] at hn
    cases k with
    | zero => simp [List.idxOf_cons_self]
    | succ k =>
      have hk : k < l.length := by simp at h; omega
      have hne : a ≠ l[k] := fun e => hn.1 (e ▸ List.getElem_mem hk)
      simp only [List.getElem_cons_succ]
      have hb : (a == l[k]) = false := by simpa using hne
      rw [List.idxOf_cons, hb, idxOf_getElem_nodup l hn.2 k hk]
      rfl

theorem not_mem_drop_of_idxOf {l : List String} (hn : l.Nodup) {k : Nat} {x : String} (hx : l.idxOf x < k) :
    x ∉ l.drop k := by
  intro hm
  obtain ⟨j, hj, he⟩ := List.mem_drop_iff_getElem.mp hm
  have := idxOf_getElem_nodup l hn (k + j) (by omega)
  rw [he] at this
  omega

theorem lookupSym_of_node {T : VE.Norms.Tree} {x : String} (hx : x ∈ nodeNames (VE.Norms.stratumNodes T)) :
    ∃ q, VE.Norms.lookupSym T x = some q ∧ q.name = x := by
  rw [stratum_names] at hx
  obtain ⟨q, hq⟩ := lookupSym_some hx
  exact ⟨q, hq, lookupSym_name hq⟩

theorem layerNames_order {T : VE.Norms.Tree} {o : List String}
    (ho : VE.Route.dependencyOrder (VE.Norms.stratumNodes T) = .ok o) : VE.Norms.layerNames T = o := by
  have hmem := (VE.Route.dag_acyclic _ _ ho).2.1
  have horder : VE.Norms.order T = o := by unfold VE.Norms.order; rw [ho]
  unfold VE.Norms.layerNames VE.Norms.syms
  rw [horder]
  suffices ∀ l : List String, (∀ x ∈ l, x ∈ nodeNames (VE.Norms.stratumNodes T)) →
      (l.filterMap (VE.Norms.lookupSym T)).map VE.Norms.Sym.name = l from this o (fun x hx => (hmem x).mp hx)
  intro l hl
  induction l with
  | nil => rfl
  | cons x l ih =>
    obtain ⟨q, hq, hqn⟩ := lookupSym_of_node (hl x List.mem_cons_self)
    rw [List.filterMap_cons, hq]
    simp only [List.map_cons, hqn, ih (fun y hy => hl y (List.mem_cons_of_mem _ hy))]

theorem node_of_lookupSym {T : VE.Norms.Tree} {x : String} {q : VE.Norms.Sym} (h : VE.Norms.lookupSym T x = some q) :
    x ∈ nodeNames (VE.Norms.stratumNodes T) := by
  rw [stratum_names]
  have hn := lookupSym_name h
  cases q with
  | reg r => exact List.mem_append_left _ (List.mem_map.mpr ⟨r, VE.Norms.lookupSym_reg h, hn⟩)
  | defn d => exact List.mem_append_right _ (List.mem_map.mpr ⟨d, VE.Norms.lookupSym_defn h, hn⟩)

theorem syms_mem_of_node {T : VE.Norms.Tree} {o : List String}
    (ho : VE.Route.dependencyOrder (VE.Norms.stratumNodes T) = .ok o) {x : String}
    (hx : x ∈ nodeNames (VE.Norms.stratumNodes T)) {q : VE.Norms.Sym} (hq : VE.Norms.lookupSym T x = some q) :
    q ∈ VE.Norms.syms T := by
  have horder : VE.Norms.order T = o := by unfold VE.Norms.order; rw [ho]
  unfold VE.Norms.syms
  rw [horder]
  exact List.mem_filterMap.mpr ⟨x, ((VE.Route.dag_acyclic _ _ ho).2.1 x).mpr hx, hq⟩

/-! ## `choice_valid` -/

section Valid
variable {D : Doc} (hh : Hyps D) {c : Choice} (hc : Compatible D c)
include hh

omit hh in
theorem pairs_choice : VE.Norms.pairs (soften (choiceDoc D c).1.soft).T = VE.Norms.pairs (soften (sup D).1.soft).T := by
  simp only [VE.Norms.pairs, soften, regs_eq c]

theorem free_soft_valid : VE.SoftNorms.SoftValid (free D).1.soft :=
  VE.SoftNorms.softValid_of_wellFormed _ (free_wfSoft hh)

omit hh in
theorem free_E : (free D).1.soft.E = D.frame.soft.E := (build_shape D _ _).E

omit hh in
theorem free_regs : (free D).1.soft.T.regulated = D.frame.soft.T.regulated := (build_shape D _ _).regulated

omit hh in
theorem free_defs : (free D).1.soft.T.definitions = D.frame.soft.T.definitions := (build_shape D _ _).definitions

/-- A layer symbol of the choice's document is one of `free D`'s, declared alike, and never a decision predicate of
    either. -/
theorem choice_sym_free {q : VE.Norms.Sym} (hq : q ∈ VE.Norms.syms (soften (choiceDoc D c).1.soft).T) :
    q ∈ VE.Norms.syms (soften (free D).1.soft).T := by
  have hv := free_soft_valid hh
  obtain ⟨o, ho⟩ := (VE.Norms.valid_of_wellFormed _ hv.wf).stratum
  obtain ⟨x, _, hx⟩ := List.mem_filterMap.mp hq
  have hlook : VE.Norms.lookupSym (soften (free D).1.soft).T x = VE.Norms.lookupSym (soften (choiceDoc D c).1.soft).T x := by
    simp only [VE.Norms.lookupSym, soften, free_regs, free_defs, choice_reg, choice_defs]
  rw [← hlook] at hx
  exact syms_mem_of_node ho (node_of_lookupSym hx) hx

omit hh in
theorem envPrime_not_decision {X : SoftDoc} {p : String} (hp : p ∉ decisionNames X) :
    (envPrime X).predicates p = X.E.predicates p := by
  unfold envPrime
  simp only
  rw [List.find?_eq_none.mpr (fun x hx he => hp (List.mem_map.mpr ⟨x, hx, by simpa using he⟩))]

theorem choice_decl {q : VE.Norms.Sym} (hq : q ∈ VE.Norms.syms (soften (choiceDoc D c).1.soft).T) :
    (envPrime (choiceDoc D c).1.soft).predicates q.name = some q.sorts ∧ Arity q.sorts ∧
      ∀ s ∈ q.sorts, s ∈ (envPrime (choiceDoc D c).1.soft).sorts := by
  have hv := free_soft_valid hh
  have hvF := VE.Norms.valid_of_wellFormed _ hv.wf
  have hqF := choice_sym_free hh hq
  obtain ⟨hd, har, hs⟩ := hvF.decl q hqF
  have hnd : q.name ∉ decisionNames (free D).1.soft :=
    layer_not_decision (free_wfSoft hh) (List.mem_map.mpr ⟨q, hqF, rfl⟩)
  have hd' : D.frame.soft.E.predicates q.name = some q.sorts := by
    show _ = _
    have : (envPrime (free D).1.soft).predicates q.name = some q.sorts := hd
    rw [envPrime_not_decision hnd, free_E] at this
    exact this
  refine ⟨by rw [choice_envPrime_frame hh c (by rw [hd']; simp)]; exact hd', har, fun s hsq => ?_⟩
  have := hs s hsq
  show s ∈ (choiceDoc D c).1.soft.E.sorts
  rw [choice_E]
  have h2 : s ∈ (free D).1.soft.E.sorts := this
  rwa [free_E] at h2

omit hh in
theorem free_nodes_in {N : SoftNode} (hN : N ∈ (free D).1.soft.T.nodes) : N ∈ (choiceDoc D c).1.soft.T.nodes := by
  rcases mem_build_nodes hN with hf | ⟨u, cs, hu⟩ | ⟨R, a, _, hpa, _⟩
  · exact (mem_choiceNodes D c N).mpr (Or.inl hf)
  · exact (mem_choiceNodes D c N).mpr (Or.inr (Or.inl ⟨u, cs, hu⟩))
  · cases hpa

omit hh in
theorem free_decisions_in {d : String × List String} (hd : d ∈ decisions (free D).1.soft) :
    d ∈ decisions (choiceDoc D c).1.soft := by
  have hsorts : ∀ p, VE.SoftNorms.sortsOf (free D).1.soft p = VE.SoftNorms.sortsOf (choiceDoc D c).1.soft p := by
    intro p; simp only [VE.SoftNorms.sortsOf, free_regs, choice_reg]
  have hsoftF : (free D).1.soft.soft = (choiceDoc D c).1.soft.soft :=
    (build_shape D _ _).soft.trans (build_shape D (fun _ => true) (pickC c)).soft.symm
  have hdp : VE.SoftNorms.dualPerm (free D).1.soft = VE.SoftNorms.dualPerm (choiceDoc D c).1.soft := by
    funext r; simp only [VE.SoftNorms.dualPerm, VE.SoftNorms.SoftDoc.base, VE.Norms.pairs, free_regs, choice_reg]
  rcases mem_decisions.mp hd with ⟨N, hN, hdm, rfl⟩ | ⟨N, hN, π, hπ, rfl⟩ | ⟨a, L, H, ht, rfl⟩
  · exact mem_decisions.mpr (Or.inl ⟨N, free_nodes_in hN, hdm, by rw [hsorts]⟩)
  · exact mem_decisions.mpr (Or.inr (Or.inl ⟨N, free_nodes_in hN, π, hπ, by rw [hsorts]⟩))
  · refine mem_decisions.mpr (Or.inr (Or.inr ⟨a, L, H, ?_, by
      simp only [VE.SoftNorms.actSortsOf, hsorts]⟩))
    obtain ⟨hol, M, N, hp, hcmp, hpt⟩ := mem_outweighsTriples.mp ht
    obtain ⟨hM, hN, hMd, hNd, hlt, hinc⟩ := VE.SoftNorms.mem_collidingPairs.mp hp
    have hinc' : VE.SoftNorms.Incompatible (choiceDoc D c).1.soft M N = true := by
      rw [← hinc]; simp only [VE.SoftNorms.Incompatible, hdp]
    refine mem_outweighsTriples.mpr ⟨by rw [← hsoftF]; exact hol, M, N,
      VE.SoftNorms.mem_collidingPairs.mpr ⟨free_nodes_in hM, free_nodes_in hN, hMd, hNd, hlt, hinc'⟩, ?_, ?_⟩
    · simp only [VE.SoftNorms.Comparable, VE.SoftNorms.higher, ← hsoftF] at hcmp ⊢; exact hcmp
    · simp only [VE.SoftNorms.pairTriple, VE.SoftNorms.higher, VE.SoftNorms.act, VE.SoftNorms.actKey, ← hsoftF,
        ← hdp] at hpt ⊢
      exact hpt

/-- A definition body is typed over the choice's `E′`. -/
theorem choice_def_typed {d : VE.Norms.Definition} (hd : d ∈ (choiceDoc D c).1.soft.T.definitions) :
    d.body.WellFormed (envPrime (choiceDoc D c).1.soft) d.args.reverse := by
  have hv := free_soft_valid hh
  have hck := (VE.NormDefaults.wellFormed_iff _).mp hv.wf
  have hdF : d ∈ (soften (free D).1.soft).T.definitions := by
    show d ∈ (free D).1.soft.T.definitions; rw [free_defs, ← choice_defs c]; exact hd
  have hdef := hck.1.2.2.2.2.1 d hdF
  have hw := (VE.check_iff_wellFormed _ _ _).mp hdef.2.2.2.2
  apply wf_congr (by show (choiceDoc D c).1.soft.E.sorts = (free D).1.soft.E.sorts; rw [choice_E, free_E])
    (by show (choiceDoc D c).1.soft.E.constants = (free D).1.soft.E.constants; rw [choice_E, free_E]) _ _ hw
  intro p hp
  have hdecl := VE.SoftNorms.preds_declared d.body hw hp
  by_cases hpd : p ∈ decisionNames (free D).1.soft
  · obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hpd
    show (envPrime (choiceDoc D c).1.soft).predicates x.1 = (envPrime (free D).1.soft).predicates x.1
    rw [choice_envPrime_decision hh c (free_decisions_in hx), envPrime_decision (free_wfSoft hh) hx]
  · have hF : (envPrime (free D).1.soft).predicates p = D.frame.soft.E.predicates p := by
      rw [envPrime_not_decision hpd, free_E]
    show (envPrime (choiceDoc D c).1.soft).predicates p = (envPrime (free D).1.soft).predicates p
    rw [hF, choice_envPrime_frame hh c (by
      have : ((envPrime (free D).1.soft).predicates p).isSome = true := hdecl
      rw [hF] at this; simpa [Option.isSome_iff_ne_none] using this)]

include hc in
theorem choice_typed : ∀ (k : Nat) (q : VE.Norms.Sym), (VE.Norms.syms (soften (choiceDoc D c).1.soft).T)[k]? = some q →
    ∀ φ ∈ q.formulas (soften (choiceDoc D c).1.soft).T,
      φ.WellFormed (envAt (soften (choiceDoc D c).1.soft) k) q.sorts.reverse := by
  have hvX := VE.Norms.valid_of_wellFormed _ (sup_softValid hh).wf
  obtain ⟨o, ho⟩ := choice_stratum_order hh hc
  have hlay := layerNames_order ho
  obtain ⟨hon, hmem, hedge, _⟩ := VE.Route.dag_acyclic _ _ ho
  intro k q hk φ hφ
  have hq : q ∈ VE.Norms.syms (soften (choiceDoc D c).1.soft).T := List.mem_of_getElem? hk
  have hko : o[k]? = some q.name := by rw [← hlay]; exact VE.Norms.names_getElemOpt hk
  have hklt : k < o.length := (List.getElem?_eq_some_iff.mp hko).1
  have hidx : o.idxOf q.name = k := by
    have he : o[k] = q.name := (List.getElem?_eq_some_iff.mp hko).2
    rw [← he]; exact idxOf_getElem_nodup o hon k hklt
  -- the formula over the complete vocabulary, and the node of q in the stratum graph
  have hfull : φ.WellFormed (envPrime (choiceDoc D c).1.soft) q.sorts.reverse ∧
      ∃ n ∈ VE.Norms.stratumNodes (soften (choiceDoc D c).1.soft).T, n.name = q.name ∧ ∀ p ∈ preds φ, p ∈ n.mentions := by
    cases q with
    | reg r =>
      have hr : r ∈ (soften (choiceDoc D c).1.soft).T.regulated := VE.Norms.mem_syms_reg hq
      have hrs : VE.SoftNorms.sortsOf (choiceDoc D c).1.soft r.name = r.sorts := by
        rw [sortsOf_choice]
        exact VE.SoftNorms.sortsOf_reg (sup_softValid hh) (by rw [regs_eq c]; exact hr)
      refine ⟨?_, ⟨r.name, ((VE.Norms.Sym.reg r).formulas (soften (choiceDoc D c).1.soft).T).flatMap preds⟩,
        List.mem_append_left _ (List.mem_map.mpr ⟨r, hr, rfl⟩), rfl,
        fun p hp => List.mem_flatMap.mpr ⟨φ, hφ, hp⟩⟩
      simp only [VE.Norms.Sym.formulas, List.mem_flatMap, VE.Norms.rulesOn, List.mem_filter, beq_iff_eq] at hφ
      obtain ⟨N', ⟨hN', hp⟩, hφ⟩ := hφ
      rw [soften_nodes, List.mem_map] at hN'
      obtain ⟨N, hN, rfl⟩ := hN'
      have hpr : N.pred = r.name := hp
      show φ.WellFormed _ r.sorts.reverse
      rw [← hrs, ← hpr]
      simp only [VE.SoftNorms.primeNode, List.mem_cons, List.mem_append] at hφ
      rcases hφ with rfl | hφ | hφ
      · exact typed_author hh c hN _ List.mem_cons_self
      · exact typed_author hh c hN _ (List.mem_cons_of_mem _ hφ)
      · simp only [derivedList] at hφ
        split at hφ
        · cases hφ
        · simp only [List.mem_singleton] at hφ; subst hφ; exact typed_derived hh c hN
    | defn d =>
      have hd : d ∈ (soften (choiceDoc D c).1.soft).T.definitions := VE.Norms.mem_syms_defn hq
      simp only [VE.Norms.Sym.formulas, List.mem_singleton] at hφ
      subst hφ
      exact ⟨choice_def_typed hh hd, ⟨d.name, preds d.body⟩,
        List.mem_append_right _ (List.mem_map.mpr ⟨d, hd, rfl⟩), rfl, fun p hp => hp⟩
  obtain ⟨hw, n, hn, hnn, hment⟩ := hfull
  refine wf_congr (E := envPrime (choiceDoc D c).1.soft) (E' := envAt (soften (choiceDoc D c).1.soft) k) rfl rfl
    φ _ hw (fun p hp => ?_)
  have hnot : p ∉ (VE.Norms.layerNames (soften (choiceDoc D c).1.soft).T).drop k := by
    rw [hlay]
    by_cases hpo : p ∈ o
    · have hdep : p ∈ deps (VE.Norms.stratumNodes (soften (choiceDoc D c).1.soft).T) n := by
        simp only [deps, List.mem_filter, List.contains_iff_mem]
        exact ⟨hment p hp, (hmem p).mp hpo⟩
      have := hedge n hn p hdep
      rw [hnn, hidx] at this
      exact not_mem_drop_of_idxOf hon this
    · exact fun h => hpo (List.mem_of_mem_drop h)
  simp only [envAt, VE.Norms.hide, if_neg hnot]
  rfl

include hc in
theorem choice_regulated : ∀ r ∈ (soften (choiceDoc D c).1.soft).T.regulated,
    VE.Norms.Sym.reg r ∈ VE.Norms.syms (soften (choiceDoc D c).1.soft).T := by
  have hv := sup_softValid hh
  intro r hr
  obtain ⟨o, ho⟩ := choice_stratum_order hh hc
  have hn : r.name ∈ nodeNames (VE.Norms.stratumNodes (soften (choiceDoc D c).1.soft).T) := by
    rw [stratum_names]; exact List.mem_append_left _ (List.mem_map.mpr ⟨r, hr, rfl⟩)
  apply syms_mem_of_node ho hn
  have hrn : ((soften (choiceDoc D c).1.soft).T.regulated.map (·.name)).Nodup := by
    show ((choiceDoc D c).1.soft.T.regulated.map (·.name)).Nodup
    rw [← regs_eq c]; exact hv.regNames
  simp only [VE.Norms.lookupSym]
  rw [VE.SoftNorms.find_key (fun x : VE.Norms.Regulated => x.name) _ hrn r hr]

include hc in
/-- The structural part of `choice_wellFormed`: the elaboration of a compatible choice's document is valid as W1
    reads it (the size limits of `WellFormedSoft` are not claimed). -/
theorem choice_valid : VE.Norms.Valid (soften (choiceDoc D c).1.soft) where
  precedence := choice_precedence_order hh hc
  stratum := choice_stratum_order hh hc
  nodup := by
    obtain ⟨o, ho⟩ := choice_stratum_order hh hc
    rw [layerNames_order ho]; exact (VE.Route.dag_acyclic _ _ ho).1
  decl := fun q hq => choice_decl hh hq
  typed := choice_typed hh hc
  regulated := choice_regulated hh hc
  pairs := by
    intro pr hpr
    have hvX := VE.Norms.valid_of_wellFormed _ (sup_softValid hh).wf
    rw [pairs_choice] at hpr
    obtain ⟨hne, ⟨r, hr, hrn, hrs⟩, ⟨m, hm, hmn, hms⟩⟩ := hvX.pairs pr hpr
    have hreg : ∀ x, VE.Norms.Sym.reg x ∈ VE.Norms.syms (soften (sup D).1.soft).T →
        VE.Norms.Sym.reg x ∈ VE.Norms.syms (soften (choiceDoc D c).1.soft).T := by
      intro x hx
      apply choice_regulated hh hc
      have := VE.Norms.mem_syms_reg hx
      show x ∈ (choiceDoc D c).1.soft.T.regulated
      rw [← regs_eq c]; exact this
    exact ⟨hne, ⟨r, hreg r hr, hrn, hrs⟩, ⟨m, hreg m hm, hmn, hms⟩⟩

end Valid

end VE.Readings
