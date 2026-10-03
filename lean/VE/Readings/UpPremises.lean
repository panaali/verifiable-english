import VE.Readings.BaseUp

/-! The lifted base satisfies `sup D`'s exception and coherence premises (docs/spec/composition-s2.md 8.4
`base_up`). An image rule's premises are the choice's premises read through the name map; an unchosen copy's
sufficient conditions carry a false `χ`, its decision predicates are empty, and it never selects. -/
namespace VE.Readings
open VE.Norms (envAt size Regulated tupleVal Sat ConstantsTyped bindAll atom)
open VE.SoftNorms (SoftNode SoftDoc soften canon envPrime decisions decisionNames exceptedName offName outweighsName
  SelectsSoftD)
open VE.Rights (RightsDoc correlate)
open VE.Compose (BaseAdmissibleP Labelled Content)
universe u

theorem atom_rel {S : VE.Structure.{u}} {p : String} {ss : List String} {ρ : VE.Valuation S}
    (h : (atom p ss).denote S ρ) : ∃ ws, S.relation p ws := by
  unfold atom at h
  split at h
  · obtain ⟨v, _, hv⟩ := h; exact ⟨[v], hv⟩
  · obtain ⟨v, w, _, _, hv⟩ := h; exact ⟨[v, w], hv⟩
  · exact h.elim

section Extra
variable {D : Doc} (hh : Hyps D) {c : Choice} (hc : Compatible D c)
include hh

/-- A rule of `sup D` outside the image is an unchosen candidate's copy. -/
theorem extra_node {P : SoftNode} (hP : P ∈ (sup D).1.soft.T.nodes)
    (hext : ∀ N ∈ (choiceDoc D c).1.soft.T.nodes, fmap D c N ≠ P) :
    ∃ m, ∃ hm : m < D.sets.length, ∃ i a N, D.sets[m].candidates[i]? = some a ∧ a.content = some (.norm N) ∧
      P = gateNorm D m i N ∧ c.index D.sets[m].id ≠ some i := by
  rcases (mem_supNodes D P).mp hP with hf | ⟨u, F, cs, hu, rfl⟩ | ⟨m, hm, i, a, N, ha, hcn, rfl⟩
  · exact absurd (fmap_frame hh c hf) (hext P ((mem_choiceNodes D c P).mpr (Or.inl hf)))
  · exact absurd (fmap_fixed hh c hu) (hext F ((mem_choiceNodes D c F).mpr (Or.inr (Or.inl ⟨u, cs, hu⟩))))
  · refine ⟨m, hm, i, a, N, ha, hcn, rfl, fun hi => ?_⟩
    exact hext N ((mem_choiceNodes D c N).mpr (Or.inr (Or.inr ⟨m, hm, i, a, hi, ha, hcn⟩)))
      (fmap_chosen hh c hm hi ha hcn)

include hc in
theorem extra_chi {S : VE.Structure.{u}} (he : Encodes D c S) {m : Nat} (hm : m < D.sets.length) {i : Nat}
    {a : Candidate} (ha : D.sets[m].candidates[i]? = some a) (hi : c.index D.sets[m].id ≠ some i)
    (ρ : VE.Valuation S) : ¬ (pattern (m + 1) (setSize D m) i).denote S ρ := by
  intro hχ
  have hilt : i < setSize D m := by rw [setSize_eq hm]; exact (List.getElem?_eq_some_iff.mp ha).1
  rw [pattern_rho, ← choiceAtom_eq (findIdx_of_nodup hh.nodup hm) hilt] at hχ
  have hmem := (he _ (List.getElem_mem hm) i (by rw [← setSize_eq hm]; exact hilt)).mp hχ
  have hcm : complete D c = true := by
    simp only [Compatible, compatible, Bool.and_eq_true] at hc; exact hc.1.1
  exact hi (index_of_mem ((complete_map hcm) ▸ hh.nodup) hmem)

theorem sup_alterable_valid {P : SoftNode} (hP : P ∈ (sup D).1.soft.T.nodes) :
    ∀ π ∈ P.alterable, VE.SoftNorms.validSoftName π = true := by
  have hcs := checkSoft_parts _ (wellFormedSoft_check _ (sup_wfSoft hh))
  intro π hπ
  have hp := checkSoftRule_parties _ P (hcs.2 P hP) π hπ
  exact checkSoftEnv_names _ hcs.1 π (List.mem_append_right _ hp)

/-- No decision predicate of the choice names, through the name map, an unchosen copy's decision. -/
theorem extra_unnamed {P : SoftNode} (hP : P ∈ (sup D).1.soft.T.nodes)
    (hext : ∀ N ∈ (choiceDoc D c).1.soft.T.nodes, fmap D c N ≠ P) {q : String}
    (hq : q ∈ decisionNames (choiceDoc D c).1.soft) :
    nameMap D c q ≠ exceptedName P ∧ ∀ π ∈ P.alterable, nameMap D c q ≠ offName P π := by
  obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hq
  have img : ∀ {N : SoftNode}, N ∈ (choiceDoc D c).1.soft.T.nodes → (fmap D c N).name ≠ P.name := fun hN h =>
    hext _ hN (sup_name_inj hh (fmap_mem hh c hN) hP h)
  have rP := sup_ruleName hh hP
  rcases mem_decisions.mp hx with ⟨N, hN, hd, rfl⟩ | ⟨N, hN, π, hπ, rfl⟩ | ⟨a, L, H, _, rfl⟩
  · show nameMap D c (exceptedName N) ≠ _ ∧ ∀ π ∈ P.alterable, nameMap D c (exceptedName N) ≠ _
    rw [nameMap_excepted hh c hN hd]
    exact ⟨fun h => img hN (exceptedName_inj (sup_ruleName hh (fmap_mem hh c hN)) rP h),
      fun π _ h => exceptedName_ne_offName _ _ _ h⟩
  · show nameMap D c (offName N π) ≠ _ ∧ ∀ π' ∈ P.alterable, nameMap D c (offName N π) ≠ _
    rw [nameMap_off hh c hN hπ]
    refine ⟨fun h => exceptedName_ne_offName _ _ _ h.symm, fun π' hπ' h => ?_⟩
    have v1 := (choice_nodeFacts hh c hN).2.2.2.2 π hπ
    exact img hN (offName_inj (sup_ruleName hh (fmap_mem hh c hN)) rP v1 (sup_alterable_valid hh hP π' hπ') h).1
  · show nameMap D c (outweighsName a L H) ≠ _ ∧ ∀ π ∈ P.alterable, nameMap D c (outweighsName a L H) ≠ _
    rw [nameMap_outweighs hh c]
    exact ⟨fun h => exceptedName_ne_outweighsName _ _ _ _ h.symm,
      fun π _ h => offName_ne_outweighsName _ _ _ _ _ h.symm⟩

end Extra

/-- The exception of a rule's image, from the image's side. -/
theorem fmap_exception_up {D : Doc} (hh : Hyps D) (c : Choice) (B : VE.Structure.{u}) (he : Encodes D c B)
    {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) {e : VE.SoftNorms.Exception}
    (hex : N.exception = some e) :
    ∃ e', (fmap D c N).exception = some e' ∧ e'.necessary = e.necessary ∧
      ∀ (ρ : VE.Valuation B), ∀ C' ∈ e'.sufficient, ∃ C ∈ e.sufficient, (C'.denote B ρ ↔ C.denote B ρ) := by
  rcases (mem_choiceNodes D c N).mp hN with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hcc⟩
  · rw [fmap_frame hh c hf]; exact ⟨e, hex, rfl, fun ρ C hC => ⟨C, hC, Iff.rfl⟩⟩
  · rw [fmap_fixed hh c hu]; exact ⟨e, hex, rfl, fun ρ C hC => ⟨C, hC, Iff.rfl⟩⟩
  · rw [fmap_chosen hh c hm hi ha hcc]
    refine ⟨{ e with sufficient := e.sufficient.map (fun C => .and C (pattern (m + 1) (setSize D m) i)) },
      by simp [gateNorm, hex], rfl, fun ρ C' hC' => ?_⟩
    obtain ⟨C, hC, rfl⟩ := List.mem_map.mp hC'
    refine ⟨C, hC, ?_⟩
    have hilt : i < setSize D m := by rw [setSize_eq hm]; exact (List.getElem?_eq_some_iff.mp ha).1
    have hχ : (pattern (m + 1) (setSize D m) i).denote B ρ := by
      rw [pattern_rho, ← choiceAtom_eq (findIdx_of_nodup hh.nodup hm) hilt]
      exact (he _ (List.getElem_mem hm) i (by rw [← setSize_eq hm]; exact hilt)).mpr (mem_of_index hi)
    simp only [VE.Formula.denote]
    exact ⟨fun h => h.1, fun h => ⟨h, hχ⟩⟩

theorem fmap_exception_none {D : Doc} (hh : Hyps D) (c : Choice) {N : SoftNode}
    (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) (hex : N.exception = none) : (fmap D c N).exception = none := by
  rcases (mem_choiceNodes D c N).mp hN with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hcc⟩
  · rw [fmap_frame hh c hf]; exact hex
  · rw [fmap_fixed hh c hu]; exact hex
  · rw [fmap_chosen hh c hm hi ha hcc]; simp [gateNorm, hex]

section Prem
variable {D : Doc} (hh : Hyps D) {c : Choice} (hc : Compatible D c) (B₀ : VE.Structure.{u}) (e : B₀.Carrier)
  (hB₀ : VE.SoftNorms.BaseAdmissible' (choiceDoc D c).1.soft B₀)
include hh hc hB₀

theorem upB_exc : Sat (upB D c B₀ e) (VE.SoftNorms.excPremises (sup D).1.soft) := by
  have hadm := hB₀.1.1
  have henc := upB_encodes hh.ready hc B₀ e
  have hY : ∀ a ∈ VE.SoftNorms.excPremises (choiceDoc D c).1.soft, a.denote B₀ [] :=
    fun a ha => hB₀.2 a (List.mem_append_left _ ha)
  intro a ha
  obtain ⟨P, hP, ha⟩ := List.mem_flatMap.mp ha
  by_cases himg : ∃ N ∈ (choiceDoc D c).1.soft.T.nodes, fmap D c N = P
  · obtain ⟨N, hN, rfl⟩ := himg
    obtain ⟨hpred, _, hmode, _, _, _⟩ := fmap_fields hh c hN
    have hss : VE.SoftNorms.sortsOf (sup D).1.soft (fmap D c N).pred =
        VE.SoftNorms.sortsOf (choiceDoc D c).1.soft N.pred := by rw [hpred, sortsOf_eq c]
    have tdown : ∀ vs : List B₀.Carrier,
        VE.TupleTyped (upB D c B₀ e) (VE.SoftNorms.sortsOf (sup D).1.soft (fmap D c N).pred) vs →
        VE.TupleTyped B₀ (VE.SoftNorms.sortsOf (choiceDoc D c).1.soft N.pred) vs := fun vs h => by
      rw [hss] at h; exact tt_down (sortsY_free hh hc _) h
    unfold VE.SoftNorms.excPremisesOf at ha
    cases hm : N.mode with
    | strict => rw [hmode, hm] at ha; cases ha
    | default =>
      cases hex : N.exception with
      | none => rw [hmode, hm, fmap_exception_none hh c hN hex] at ha; cases ha
      | some ex =>
        obtain ⟨e', hex', hnec, hsuf⟩ := fmap_exception_up hh c _ henc hN hex
        rw [hmode, hm, hex'] at ha
        have hYp : ∀ a' ∈ VE.SoftNorms.excPremisesOf (choiceDoc D c).1.soft N, a'.denote B₀ [] :=
          fun a' h' => hY a' (List.mem_flatMap.mpr ⟨_, hN, h'⟩)
        have htyped := choice_exc_typed hh c hN hex
        have hexc : ∀ ρ : VE.Valuation B₀,
            (VE.SoftNorms.exceptedF (sup D).1.soft (fmap D c N)).denote (upB D c B₀ e) ρ ↔
              (VE.SoftNorms.exceptedF (choiceDoc D c).1.soft N).denote B₀ ρ := fun ρ =>
          (excepted_pull hh c (upB D c B₀ e) hN hm ρ).trans (pull_up hh B₀ e hadm _ _ (typed_excepted hh c hN hm) ρ)
        rcases List.mem_append.mp ha with ha | ha
        · obtain ⟨C', hC'm, rfl⟩ := List.mem_map.mp ha
          rw [VE.Norms.bindAll_denote_nil]
          intro vs hvs
          simp only [VE.Formula.denote]
          intro hC'
          obtain ⟨C, hCm, hiff⟩ := hsuf (tupleVal vs) C' hC'm
          obtain ⟨Γ, hw⟩ := htyped C (List.mem_append_left _ hCm)
          have hC0 := (up_frame hh B₀ e C Γ hw _).mp (hiff.mp hC')
          have hprem := hYp (bindAll (VE.SoftNorms.sortsOf (choiceDoc D c).1.soft N.pred)
            (.implies C (VE.SoftNorms.exceptedF (choiceDoc D c).1.soft N))) (by
              unfold VE.SoftNorms.excPremisesOf; rw [hm, hex]
              exact List.mem_append_left _ (List.mem_map_of_mem hCm))
          rw [VE.Norms.bindAll_denote_nil] at hprem
          exact (hexc _).mpr (hprem vs (tdown vs hvs) hC0)
        · obtain ⟨C, hCm, rfl⟩ := List.mem_map.mp ha
          rw [VE.Norms.bindAll_denote_nil]
          intro vs hvs
          simp only [VE.Formula.denote]
          intro hE
          rw [hnec] at hCm
          obtain ⟨Γ, hw⟩ := htyped C (List.mem_append_right _ hCm)
          have hprem := hYp (bindAll (VE.SoftNorms.sortsOf (choiceDoc D c).1.soft N.pred)
            (.implies (VE.SoftNorms.exceptedF (choiceDoc D c).1.soft N) C)) (by
              unfold VE.SoftNorms.excPremisesOf; rw [hm, hex]
              exact List.mem_append_right _ (List.mem_map_of_mem hCm))
          rw [VE.Norms.bindAll_denote_nil] at hprem
          exact (up_frame hh B₀ e C Γ hw _).mpr (hprem vs (tdown vs hvs) ((hexc _).mp hE))
  · have hext : ∀ N ∈ (choiceDoc D c).1.soft.T.nodes, fmap D c N ≠ P := fun N hN h => himg ⟨N, hN, h⟩
    obtain ⟨m, hm, i, a', N', ha', _, rfl, hi⟩ := extra_node hh hP hext
    unfold VE.SoftNorms.excPremisesOf at ha
    split at ha
    · rename_i ex hd hex
      rcases List.mem_append.mp ha with ha | ha
      · obtain ⟨C', hC'm, rfl⟩ := List.mem_map.mp ha
        rw [VE.Norms.bindAll_denote_nil]
        intro vs _ hC'
        exfalso
        have hex2 := hex
        simp only [gateNorm] at hex2
        obtain ⟨ex0, _, rfl⟩ := Option.map_eq_some_iff.mp hex2
        obtain ⟨C, _, rfl⟩ := List.mem_map.mp hC'm
        exact extra_chi hh hc henc hm ha' hi _ hC'.2
      · obtain ⟨C, _, rfl⟩ := List.mem_map.mp ha
        rw [VE.Norms.bindAll_denote_nil]
        intro vs _ hE
        exfalso
        obtain ⟨ws, hws⟩ := atom_rel hE
        have hdX : exceptedName (gateNorm D m i N') ∈ decisionNames (sup D).1.soft :=
          List.mem_map.mpr ⟨_, mem_decisions.mpr (Or.inl ⟨_, hP, hd, rfl⟩), rfl⟩
        rcases hws with h | h | h
        · exact decision_not_bit hdX (onBit_isBit h.1)
        · obtain ⟨_, _, q, hq, hqe, _⟩ := h
          exact (extra_unnamed hh hP hext hq).1 hqe
        · exact h.2.1 hdX
    · cases ha

theorem upB_coh : Sat (upB D c B₀ e) (VE.SoftNorms.cohPremises (sup D).1.soft) := by
  have hadm := hB₀.1.1
  have henc := upB_encodes hh.ready hc B₀ e
  have hBX : VE.Norms.BaseAdmissible (soften (sup D).1.soft) (upB D c B₀ e) :=
    ⟨upB_admissible hh hc B₀ e hadm, upB_literals hh B₀ e hB₀.1.2⟩
  have hcB : ConstantsTyped (soften (sup D).1.soft) (upB D c B₀ e) := hBX.1.1
  have hcB' : ∀ x s, (soften (sup D).1.soft).E.constants x = some s → ∃ v, (upB D c B₀ e).constant x = some v :=
    fun x s h => (hcB x s h).imp fun _ h => h.1
  have hvX := sup_softValid hh
  have hvY := choice_valid hh hc
  have hcP := constantsTyped_pull hh (c := c) (upB D c B₀ e) hcB
  -- selections on the two bases of the choice's expansion agree
  have hsel : ∀ M ∈ (choiceDoc D c).1.soft.T.nodes, ∀ vs : List B₀.Carrier,
      VE.TupleTyped B₀ (VE.SoftNorms.sortsOf (choiceDoc D c).1.soft M.pred) vs →
      (SelectsSoftD (choiceDoc D c).1.soft (canon (soften (choiceDoc D c).1.soft) (pull D c (upB D c B₀ e)))
          (tupleVal vs) (VE.SoftNorms.fuel (choiceDoc D c).1.soft) M ↔
        SelectsSoftD (choiceDoc D c).1.soft (canon (soften (choiceDoc D c).1.soft) B₀) (tupleVal vs)
          (VE.SoftNorms.fuel (choiceDoc D c).1.soft) M) := by
    intro M hM vs hvs
    have hw := choice_selTyped hh hc hM
    have hρ0 := VE.Norms.tupleVal_typed B₀ _ vs hvs
    have hρ1 := VE.Norms.tupleVal_typed (pull D c (upB D c B₀ e)) _ vs
      ((VE.Route.Examples.tupleTyped_relation (upB D c B₀ e) _ _ vs).mpr (tt_up (D := D) (c := c) (e := e) hvs))
    rw [← VE.SoftNorms.selectsPrime_denote, ← VE.SoftNorms.selectsPrime_denote,
      ← VE.SoftNorms.canon_subst hvY _ hcP _ _ _ hw _ hρ1, ← VE.SoftNorms.canon_subst hvY _ hadm.1 _ _ _ hw _ hρ0]
    have hw0 := VE.Norms.subst_wellFormed hvY _ _ _ hw
    exact pull_up hh B₀ e hadm _ _ (VE.Norms.wf_mono (E := envAt (soften (choiceDoc D c).1.soft) 0)
      (E' := envPrime (choiceDoc D c).1.soft) rfl rfl (fun r ss h => envAt_sub h) _ _ hw0) _
  intro a ha
  obtain ⟨⟨P, Q⟩, hPQ, rfl⟩ := List.mem_map.mp ha
  rw [VE.SoftNorms.coh_canon hvX _ hBX hPQ]
  intro vs hvs ⟨hsP, hsQ⟩
  obtain ⟨hP, hQ, hPd, hQd, hlt, hinc⟩ := VE.SoftNorms.mem_collidingPairs.mp hPQ
  have hs := faithful_sim hh hc (canon (soften (sup D).1.soft) (upB D c B₀ e)) (encodes_canon hh _ henc) (tupleVal vs)
  have hPi : ∃ M ∈ (choiceDoc D c).1.soft.T.nodes, fmap D c M = P := Classical.byContradiction fun h =>
    sim_applies_extra hs P hP (fun N hN he => h ⟨N, hN, he⟩) hsP.1
  have hQi : ∃ N ∈ (choiceDoc D c).1.soft.T.nodes, fmap D c N = Q := Classical.byContradiction fun h =>
    sim_applies_extra hs Q hQ (fun N hN he => h ⟨N, hN, he⟩) hsQ.1
  obtain ⟨M, hM, rfl⟩ := hPi
  obtain ⟨N, hN, rfl⟩ := hQi
  obtain ⟨hpM, _, hmM, _, _, _⟩ := fmap_fields hh c hM
  obtain ⟨hpN, _, hmN, _, _, _⟩ := fmap_fields hh c hN
  have hincY : VE.SoftNorms.Incompatible (choiceDoc D c).1.soft M N = true := by
    rw [← sim_incompatible hs M N hM hN]; exact hinc
  have hneq : M.name ≠ N.name := fun h => by
    have := choice_name_inj hh c hM hN h
    subst this
    exact absurd hlt (String.lt_irrefl _)
  have hsX : VE.SoftNorms.sortsOf (sup D).1.soft (fmap D c M).pred =
      VE.SoftNorms.sortsOf (sup D).1.soft (fmap D c N).pred := hvX.cpSorts _ hPQ
  have hsY : VE.SoftNorms.sortsOf (choiceDoc D c).1.soft M.pred = VE.SoftNorms.sortsOf (choiceDoc D c).1.soft N.pred := by
    rw [← sortsOf_eq c, ← sortsOf_eq c, ← hpM, ← hpN]; exact hsX
  have hvsM : VE.TupleTyped B₀ (VE.SoftNorms.sortsOf (choiceDoc D c).1.soft M.pred) vs := by
    have : VE.TupleTyped (upB D c B₀ e) (VE.SoftNorms.sortsOf (sup D).1.soft (fmap D c M).pred) vs := hvs
    rw [hpM, sortsOf_eq c] at this
    exact tt_down (sortsY_free hh hc _) this
  have hvsN : VE.TupleTyped B₀ (VE.SoftNorms.sortsOf (choiceDoc D c).1.soft N.pred) vs := by rw [← hsY]; exact hvsM
  have hcB0 : ∀ x s, (soften (sup D).1.soft).E.constants x = some s → ∃ v, (upB D c B₀ e).constant x = some v := hcB'
  have sM := (hsel M hM vs hvsM).mp ((selects_iff hh hc _ hcB0 henc hM vs).mp hsP)
  have sN := (hsel N hN vs hvsN).mp ((selects_iff hh hc _ hcB0 henc hN vs).mp hsQ)
  have hYc : ∀ A ∈ VE.SoftNorms.cohPremises (choiceDoc D c).1.soft, A.denote B₀ [] :=
    fun A hA => hB₀.2 A (List.mem_append_right _ hA)
  rcases VE.SoftNorms.str_lt_or_gt _ _ hneq with h1 | h1
  · have hp : (M, N) ∈ VE.SoftNorms.collidingPairs (choiceDoc D c).1.soft :=
      VE.SoftNorms.mem_collidingPairs.mpr ⟨hM, hN, by rw [← hmM]; exact hPd, by rw [← hmN]; exact hQd, h1, hincY⟩
    have := (coh_canonY hh hc B₀ hadm.1 hp hsY).mp (hYc _ (List.mem_map.mpr ⟨_, hp, rfl⟩))
    exact this vs hvsM ⟨sM, sN⟩
  · have hp : (N, M) ∈ VE.SoftNorms.collidingPairs (choiceDoc D c).1.soft :=
      VE.SoftNorms.mem_collidingPairs.mpr ⟨hN, hM, by rw [← hmN]; exact hQd, by rw [← hmM]; exact hPd, h1,
        by rw [VE.SoftNorms.incompatible_symm]; exact hincY⟩
    have := (coh_canonY hh hc B₀ hadm.1 hp hsY.symm).mp (hYc _ (List.mem_map.mpr ⟨_, hp, rfl⟩))
    exact this vs hvsN ⟨sN, sM⟩

end Prem

end VE.Readings
