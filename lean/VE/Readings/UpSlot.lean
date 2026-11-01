import VE.Readings.UpPremises

/-! The lifted base satisfies the slot of `sup D` (docs/spec/composition-s2.md 1.6, 8.4 `base_up`): the one,
coupling and narrowing premises because the bits spell the compatible choice `c`, and every quiet premise because a
non-empty decision table of the lifted base is the image of a decision predicate of `c`'s document, whose key is
owned by chosen candidates only (`origin_fmap`, `pairOwner_chosen`). -/
namespace VE.Readings
open VE.Norms (envAt size Regulated tupleVal Sat ConstantsTyped bindAll atom)
open VE.SoftNorms (SoftNode SoftDoc soften canon envPrime decisions decisionNames exceptedName offName outweighsName)
open VE.Rights (RightsDoc correlate)
open VE.Compose (BaseAdmissibleP Labelled Content)
universe u

/-! ## The keys of `sup D` -/

theorem genDecls_nil {X : RightsDoc} (h : noRights X = true) : VE.Rights.genDecls X = [] := by
  obtain ⟨_, hl, hb, _⟩ := noRights_parts h
  simp [VE.Rights.genDecls, VE.Rights.limDecls, VE.Rights.condDecls, VE.Rights.aimedDecls,
    VE.Rights.limKeys_nil X hl, VE.Rights.condKeys_nil X hl, hb]

theorem genKeys_name_inj {D : Doc} (hh : Hyps D) {g g' : GenKey × String × List String}
    (hg : g ∈ genKeys (sup D).1) (hg' : g' ∈ genKeys (sup D).1) (h : g.2.1 = g'.2.1) : g = g' := by
  have hn : ((genKeys (sup D).1).map (·.2.1)).Nodup := by
    have e1 := congrArg (List.map Prod.fst) (genKeys_names (sup D).1)
    rw [genDecls_nil hh.noRights, List.append_nil, List.map_map, sup_correlate hh] at e1
    have : (genKeys (sup D).1).map (·.2.1) = decisionNames (sup D).1.soft := by
      rw [VE.SoftNorms.decisionNames, ← e1]; rfl
    rw [this]; exact (sup_softValid hh).decNodup
  exact inj_of_nodup_map hn hg hg' h

theorem outweighs_key_mem {X : RightsDoc} {x : String × String × String}
    (hx : x ∈ VE.SoftNorms.outweighsTriples (correlate X)) :
    (GenKey.outweighs x.1 x.2.1 x.2.2, outweighsName x.1 x.2.1 x.2.2, VE.SoftNorms.actSortsOf (correlate X) x.1) ∈
      genKeys X := by
  simp only [genKeys, List.mem_append]
  exact Or.inl (Or.inl (Or.inl (Or.inr (List.mem_map.mpr ⟨x, hx, rfl⟩))))

/-- A triple of the choice's document is the triple of a colliding pair of images in `sup D`. -/
theorem triple_pair {D : Doc} (hh : Hyps D) (c : Choice) {x : String × String × String}
    (hx : x ∈ VE.SoftNorms.outweighsTriples (choiceDoc D c).1.soft) :
    ∃ P Q, (P, Q) ∈ VE.SoftNorms.collidingPairs (sup D).1.soft ∧ VE.SoftNorms.Comparable (sup D).1.soft P Q = true ∧
      VE.SoftNorms.pairTriple (sup D).1.soft P Q = x ∧ (∃ M ∈ (choiceDoc D c).1.soft.T.nodes, fmap D c M = P) ∧
      (∃ N ∈ (choiceDoc D c).1.soft.T.nodes, fmap D c N = Q) := by
  obtain ⟨_, M, N, hp, hcmp, ht⟩ := mem_outweighsTriples.mp hx
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
  have hrv : VE.SoftNorms.RanksValid (choiceDoc D c).1.soft.soft := by rw [← hsoft]; exact hsv.ranks
  rcases VE.SoftNorms.str_lt_or_gt _ _ hne with hl | hl
  · refine ⟨fmap D c M, fmap D c N, VE.SoftNorms.mem_collidingPairs.mpr ⟨fmap_mem hh c hM, fmap_mem hh c hN,
      by rw [hMm]; exact hMd, by rw [hNm]; exact hNd, hl, hinc'⟩, ?_, ?_, ⟨M, hM, rfl⟩, ⟨N, hN, rfl⟩⟩
    · simp only [VE.SoftNorms.Comparable, hhi M N hM hN, hhi N M hN hM]; exact hcmp
    · simp only [VE.SoftNorms.pairTriple, hhi M N hM hN, hact M hM, hact N hN, hrk M hM, hrk N hN] at ht ⊢
      exact ht
  · refine ⟨fmap D c N, fmap D c M, VE.SoftNorms.mem_collidingPairs.mpr ⟨fmap_mem hh c hN, fmap_mem hh c hM,
      by rw [hNm]; exact hNd, by rw [hMm]; exact hMd, hl, by rw [VE.SoftNorms.incompatible_symm]; exact hinc'⟩, ?_, ?_,
      ⟨N, hN, rfl⟩, ⟨M, hM, rfl⟩⟩
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

/-! ## Owners of the image keys are chosen -/

def ChosenAt (D : Doc) (c : Choice) (x : Nat × Nat) : Prop :=
  ∃ hm : x.1 < D.sets.length, c.index D.sets[x.1].id = some x.2

theorem origin_fmap {D : Doc} (hh : Hyps D) (c : Choice) {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) :
    ∀ x ∈ (origin D (fmap D c N).name).toList, ChosenAt D c x := by
  rcases (mem_choiceNodes D c N).mp hN with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hcc⟩
  · rw [fmap_frame hh c hf, origin_unreserved (frame_not_reserved hh hf)]; simp
  · rw [fmap_fixed hh c hu]
    show ∀ x ∈ (origin D N.name).toList, _
    rw [origin_unreserved (fixed_not_reserved hh hu)]; simp
  · rw [fmap_chosen hh c hm hi ha hcc]
    show ∀ x ∈ (origin D (qualify (position D m i) N.name)).toList, _
    have hlt := (List.getElem?_eq_some_iff.mp ha).1
    have ho := origin_qualify hm hlt ha hcc (d := ("rule", N.name)) (by simp [Content.declared])
    rw [ho]
    intro x hx
    simp only [Option.toList_some, List.mem_singleton] at hx
    subst hx
    exact ⟨hm, hi⟩

theorem pairOwner_chosen {D : Doc} {c : Choice} {P Q : SoftNode}
    (hP : ∀ x ∈ (origin D P.name).toList, ChosenAt D c x) (hQ : ∀ x ∈ (origin D Q.name).toList, ChosenAt D c x) :
    ∃ o, pairOwner D P Q = some o ∧ ∀ x ∈ o, ChosenAt D c x := by
  unfold pairOwner
  cases ho : origin D P.name with
  | none =>
    cases ho' : origin D Q.name with
    | none => exact ⟨[], rfl, by simp⟩
    | some o' =>
      refine ⟨[o'], by simp, ?_⟩
      intro x hx
      simp only [List.mem_singleton] at hx; subst hx
      exact hQ _ (by rw [ho']; simp)
  | some o =>
    have h1 := hP o (by rw [ho]; simp)
    cases ho' : origin D Q.name with
    | none =>
      refine ⟨[o], by simp, ?_⟩
      intro x hx
      simp only [List.mem_singleton] at hx; subst hx; exact h1
    | some o' =>
      have h2 := hQ o' (by rw [ho']; simp)
      have hcond : (o.1 == o'.1 && o.2 != o'.2) = false := by
        cases hm : (o.1 == o'.1) with
        | false => rfl
        | true =>
          have he : o.1 = o'.1 := beq_iff_eq.mp hm
          obtain ⟨hm1, hi1⟩ := h1
          obtain ⟨hm2, hi2⟩ := h2
          have : D.sets[o.1].id = D.sets[o'.1].id := by simp only [he]
          rw [this, hi2] at hi1
          have h22 := Option.some.inj hi1
          simp [h22]
      simp only [hcond, Bool.false_eq_true, if_false]
      refine ⟨_, rfl, fun x hx => ?_⟩
      rw [VE.SoftNorms.mem_dedup] at hx
      simp only [List.mem_cons, List.not_mem_nil, or_false] at hx
      rcases hx with rfl | rfl
      · exact h1
      · exact h2

/-! ## The atoms and patterns of the lifted base -/

theorem atom_iff_of_encodes {D : Doc} (hr : supReady D = true) {c : Choice} (hc : Compatible D c)
    {S : VE.Structure.{u}} (he : Encodes D c S) (s : String) (i : Nat) :
    (choiceAtom D s i).denote S [] ↔ (s, i) ∈ c := by
  have hcm : complete D c = true := by
    simp only [Compatible, compatible, Bool.and_eq_true] at hc; exact hc.1.1
  by_cases hx : ∃ m, D.sets.findIdx? (·.id == s) = some m ∧ i < setSize D m
  · obtain ⟨m, hf, hi⟩ := hx
    obtain ⟨hm, rfl⟩ := findIdx_set hf
    exact he _ (List.getElem_mem hm) i (by rw [← setSize_eq hm]; exact hi)
  · rw [choiceAtom_bottom hx]
    refine ⟨fun h => h.elim, fun h => absurd ?_ hx⟩
    obtain ⟨m, hf, hi⟩ := candidate_isSome (complete_mem hcm h)
    exact ⟨m, hf, hi⟩

theorem upB_pattern {D : Doc} (hr : supReady D = true) {c : Choice} (hc : Compatible D c)
    (B₀ : VE.Structure.{u}) (e : B₀.Carrier) (m : Nat) (hm : m < D.sets.length) (i : Nat)
    (hi : i < 2 ^ bitsOf (setSize D m)) :
    (pattern (m + 1) (setSize D m) i).denote (upB D c B₀ e) [] ↔ i = chosenIdx D c m := by
  have hk := le_two_pow_bitsOf (setSize D m)
  have hcl := (chosen_spec hr hc m hm).2
  rw [pattern_denote]
  constructor
  · intro h
    apply eq_of_low_bits hi (by omega)
    intro j hj
    have := (bitOn_upB hm hj).symm.trans (h j hj)
    cases h1 : i.testBit j <;> cases h2 : (chosenIdx D c m).testBit j <;> simp_all
  · rintro rfl j hj
    exact bitOn_upB hm hj

/-- The one, coupling and narrowing premises hold where the atoms spell a compatible choice. -/
theorem core_sat {D : Doc} (hr : supReady D = true) {c : Choice} (hc : Compatible D c) {S : VE.Structure.{u}}
    (hatom : ∀ s i, (choiceAtom D s i).denote S [] ↔ (s, i) ∈ c)
    (hpat : ∀ m (hm : m < D.sets.length) i, i < 2 ^ bitsOf (setSize D m) →
      ((pattern (m + 1) (setSize D m) i).denote S [] ↔ i = chosenIdx D c m)) :
    ∀ a ∈ choiceCore D, a.denote S [] := by
  have hn := supReady_nodup hr
  have hcm : complete D c = true := by
    simp only [Compatible, compatible, Bool.and_eq_true] at hc; exact hc.1.1
  have hcoup : ∀ K ∈ D.couplings, couplingHolds D c K = true := by
    simp only [Compatible, compatible, Bool.and_eq_true, List.all_eq_true] at hc; exact hc.1.2
  have hnar : ∀ N ∈ D.narrowings, narrowingHolds D c N = true := by
    simp only [Compatible, compatible, Bool.and_eq_true, List.all_eq_true] at hc; exact hc.2
  have hcn : (c.map (·.1)).Nodup := (complete_map hcm) ▸ hn
  have hchosen := chosen_spec hr hc
  intro a ha
  simp only [choiceCore, Labelled.formulas, List.map_append, List.mem_append, List.mem_map] at ha
  rcases ha with (⟨⟨l, a'⟩, hl, rfl⟩ | ⟨⟨l, a'⟩, hl, rfl⟩) | ⟨⟨l, a'⟩, hl, rfl⟩
  · -- one
    simp only [onePremises, List.mem_filterMap, List.mem_range] at hl
    obtain ⟨m, hm, hb⟩ := hl
    rw [List.getElem?_eq_getElem hm] at hb
    simp only [Option.bind_some] at hb
    split at hb
    · cases hb
    · cases hb
      apply (conj_denote S [] _).mpr
      intro f hf
      obtain ⟨i', hi', rfl⟩ := List.mem_map.mp hf
      simp only [List.mem_filter, List.mem_range, decide_eq_true_eq] at hi'
      intro hp
      rw [← setSize_eq hm] at hi' hp
      have := (hpat m hm i' hi'.1).mp hp
      have := (hchosen m hm).2
      omega
  · -- couplings
    simp only [couplingPremises, List.mem_filterMap] at hl
    obtain ⟨K, hK, hb⟩ := hl
    split at hb
    · cases hb
    · cases hb
      apply (conj_denote S [] _).mpr
      intro f hf
      simp only [List.mem_flatMap] at hf
      obtain ⟨⟨x, y⟩, hxy, hf⟩ := hf
      split at hf
      · rename_i R R' hR hR'
        simp only [List.mem_flatMap, List.mem_range, List.mem_filterMap] at hf
        obtain ⟨i, hi, j, hj, hf⟩ := hf
        split at hf
        · rename_i hne
          cases hf
          rintro ⟨h1, h2⟩
          have hm1 := (hatom _ _).mp h1
          have hm2 := (hatom _ _).mp h2
          have hx1 : R.id = x.1 := by simpa using List.find?_some hR
          have hy1 : R'.id = y.1 := by simpa using List.find?_some hR'
          have hi1 := index_of_mem hcn hm1
          have hj1 := index_of_mem hcn hm2
          simp only at hi1 hj1
          rw [hx1] at hi1
          rw [hy1] at hj1
          have := List.all_eq_true.mp (hcoup K hK) (x, y) hxy
          simp only [hi1, hj1, candidate, hR, hR', Option.bind_some] at this
          revert this hne
          cases R.candidates[i]?.bind (labelOf · K.axis) <;> cases R'.candidates[j]?.bind (labelOf · K.axis) <;>
            simp
        · cases hf
      · cases hf
  · -- narrowings
    simp only [narrowingPremises, List.mem_filterMap] at hl
    obtain ⟨N, hN, hb⟩ := hl
    cases hR : inForce D N with
    | none => rw [hR] at hb; cases hb
    | some R =>
      rw [hR] at hb
      simp only [Option.bind_some] at hb
      split at hb
      · cases hb
      · cases hb
        apply (conj_denote S [] _).mpr
        intro f hf
        obtain ⟨i, hi, rfl⟩ := List.mem_map.mp hf
        intro hχ
        have hm1 := index_of_mem hcn ((hatom _ _).mp hχ)
        simp only at hm1
        have := hnar N hN
        simp only [narrowingHolds, hR, hm1] at this
        simp only [List.mem_filter, List.mem_range] at hi
        revert this hi
        cases R.candidates[i]?.map (fun a => N.keeps.contains a.id) <;> simp
        exact fun h _ => h

/-! ## The quiet premises -/

theorem upB_quiet {D : Doc} (hh : Hyps D) {c : Choice} (hc : Compatible D c) (B₀ : VE.Structure.{u})
    (e : B₀.Carrier) {g : GenKey × String × List String} (hg : g ∈ genKeys (sup D).1) :
    (quietFormula D g).denote (upB D c B₀ e) [] := by
  have henc := upB_encodes hh.ready hc B₀ e
  have hdX : g.2.1 ∈ decisionNames (sup D).1.soft := by
    have := genKeys_decision hh.noRights hg
    rw [sup_correlate hh] at this
    exact List.mem_map.mpr ⟨_, this, rfl⟩
  unfold quietFormula
  rw [VE.Norms.bindAll_denote_nil]
  intro vs _
  simp only [VE.Formula.denote]
  intro hat
  obtain ⟨ws, hws⟩ := atom_rel hat
  suffices hown : ∃ o ∈ owners D g.1, ∀ x ∈ o, ChosenAt D c x by
    obtain ⟨o, ho, hoc⟩ := hown
    rw [disj_denote]
    refine ⟨_, List.mem_map.mpr ⟨o, ho, rfl⟩, ?_⟩
    rw [conj_denote]
    intro f hf
    obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hf
    obtain ⟨hm, hi⟩ := hoc x hx
    unfold atomAt
    rw [choiceAtom_rho, List.getElem?_eq_getElem hm]
    simp only [Option.map_some, Option.getD_some]
    exact (atom_iff_of_encodes hh.ready hc henc _ _).mpr (mem_of_index hi)
  rcases hws with h | h | h
  · exact absurd (onBit_isBit h.1) (decision_not_bit hdX)
  · obtain ⟨_, _, q, hq, hqe, _⟩ := h
    obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hq
    rcases mem_decisions.mp hx with ⟨N, hN, hd, rfl⟩ | ⟨N, hN, π, hπ, rfl⟩ | ⟨a, L, H, ht, rfl⟩
    · have hqe' : exceptedName (fmap D c N) = g.2.1 := by rw [← nameMap_excepted hh c hN hd]; exact hqe
      obtain ⟨g', hg', hk', hn'⟩ := excepted_key_mem hh.noRights (fmap_mem hh c hN)
        (by rw [(fmap_fields hh c hN).2.2.1]; exact hd)
      have : g = g' := genKeys_name_inj hh hg hg' (by rw [← hqe', hn'])
      subst this
      rw [hk']
      exact ⟨_, List.mem_singleton.mpr rfl, origin_fmap hh c hN⟩
    · have hqe' : offName (fmap D c N) π = g.2.1 := by rw [← nameMap_off hh c hN hπ]; exact hqe
      obtain ⟨g', hg', hk', hn'⟩ := off_key_mem hh.noRights (fmap_mem hh c hN)
        (by rw [(fmap_fields hh c hN).2.2.2.2.1]; exact hπ)
      have : g = g' := genKeys_name_inj hh hg hg' (by rw [← hqe', hn'])
      subst this
      rw [hk']
      exact ⟨_, List.mem_singleton.mpr rfl, origin_fmap hh c hN⟩
    · have hqe' : outweighsName a L H = g.2.1 := by rw [← nameMap_outweighs hh c]; exact hqe
      have htX : (a, L, H) ∈ VE.SoftNorms.outweighsTriples (correlate (sup D).1) := by
        rw [sup_correlate hh]; exact triple_sup hh c ht
      have hk := outweighs_key_mem htX
      have : g = _ := genKeys_name_inj hh hg hk hqe'.symm
      subst this
      obtain ⟨P, Q, hPQ, hcmp, hpt, ⟨M, hM, rfl⟩, ⟨N, hN, rfl⟩⟩ := triple_pair hh c ht
      obtain ⟨o, hpo, hoc⟩ := pairOwner_chosen (origin_fmap hh c hM) (origin_fmap hh c hN)
      refine ⟨o, ?_, hoc⟩
      simp only [owners]
      rw [VE.SoftNorms.mem_dedup]
      apply List.mem_filterMap.mpr
      refine ⟨(fmap D c M, fmap D c N), by rw [sup_correlate hh]; exact hPQ, ?_⟩
      simp only [sup_correlate hh, hcmp, hpt, beq_self_eq_true, Bool.and_self, if_true]
      exact hpo
  · exact absurd hdX h.2.1

theorem limLabelled_nil {X : RightsDoc} (h : noRights X = true) : VE.Rights.limPremisesLabelled X = [] := by
  obtain ⟨_, hl, _, _⟩ := noRights_parts h
  simp [VE.Rights.limPremisesLabelled, VE.Rights.condKeys_nil X hl]

theorem upB_slot {D : Doc} (hh : Hyps D) {c : Choice} (hc : Compatible D c) (B₀ : VE.Structure.{u})
    (e : B₀.Carrier) : Sat (upB D c B₀ e) (slotP D) := by
  have henc := upB_encodes hh.ready hc B₀ e
  have hcore := core_sat hh.ready hc (atom_iff_of_encodes hh.ready hc henc) (upB_pattern hh.ready hc B₀ e)
  intro a ha
  simp only [slotP, slotLabelled, Labelled.formulas, List.map_append, List.mem_append, choiceLabelled, gatedRel,
    limLabelled_nil hh.noRights, List.map_nil, List.not_mem_nil, false_or, or_false] at ha
  rcases ha with (((ha | ha) | ha) | ha) | ha
  · exact hcore a (by simp only [choiceCore, Labelled.formulas, List.map_append, List.mem_append]; exact Or.inl (Or.inl ha))
  · obtain ⟨⟨l, f⟩, hl, rfl⟩ := List.mem_map.mp ha
    simp only [quietOwn, List.mem_flatMap, List.mem_range, List.mem_filterMap] at hl
    obtain ⟨m, _, R, _, i, _, hb⟩ := hl
    split at hb
    · cases hb
    · cases hb
      apply (conj_denote _ [] _).mpr
      intro f hf
      obtain ⟨g, hg, rfl⟩ := List.mem_map.mp hf
      exact upB_quiet hh hc B₀ e (List.mem_filter.mp hg).1
  · obtain ⟨⟨l, f⟩, hl, rfl⟩ := List.mem_map.mp ha
    simp only [quietShared, List.mem_map, List.mem_filter] at hl
    obtain ⟨g, ⟨hg, _⟩, he⟩ := hl
    cases he
    exact upB_quiet hh hc B₀ e hg
  · exact hcore a (by simp only [choiceCore, Labelled.formulas, List.map_append, List.mem_append]; exact Or.inl (Or.inr ha))
  · exact hcore a (by simp only [choiceCore, Labelled.formulas, List.map_append, List.mem_append]; exact Or.inr ha)

/-- Bases correspond, upward; the extension pulls back to the structure it came from. The extension is stated as
    `B₀` with the relation, domain and constant replaced, so that its carrier is `B₀`'s and the pull-back conjunct
    is well typed (finding 6). -/
theorem base_up (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights) (hs : superposable D = true)
    (c : Choice) (hc : Compatible D c) (B₀ : VE.Structure.{u}) (hne : Nonempty B₀.Carrier)
    (hB : VE.Rights.BaseAdmissibleR (choiceDoc D c).1 B₀) :
    ∃ (R : String → List B₀.Carrier → Prop) (dom : String → B₀.Carrier → Prop) (k : String → Option B₀.Carrier),
      ChoiceExtension D { B₀ with relation := R } { B₀ with relation := R, domain := dom, constant := k } ∧
      BaseAdmissibleP (correlate (sup D).1) (slotP D) { B₀ with relation := R, domain := dom, constant := k } ∧
      Encodes D c { B₀ with relation := R, domain := dom, constant := k } ∧
      ∀ p (vs : List B₀.Carrier),
        (pull D c { B₀ with relation := R, domain := dom, constant := k }).relation p vs ↔ B₀.relation p vs := by
  have hh : Hyps D := ⟨h, hch, hs⟩
  have hYn := choiceDoc_noRights D c hh.noRights
  have hB₀ : VE.SoftNorms.BaseAdmissible' (choiceDoc D c).1.soft B₀ := by
    have := hB.1; rwa [(correlate_noRights _ hYn).1] at this
  obtain ⟨e⟩ := hne
  refine ⟨upRel D c B₀ e, upDom B₀, upConst B₀ e, ⟨upRel D c B₀ e, upDom B₀, upConst B₀ e, rfl,
    fun _ _ _ => Iff.rfl, fun σ hσ => ?_, fun x hx => ?_⟩, ?_, upB_encodes hh.ready hc B₀ e,
    pull_upB hh c B₀ e hB₀.1.1⟩
  · show (if σ = "ve__reading" then _ else _) = _; exact if_neg hσ
  · show (if x = "ve__here" then _ else _) = _; exact if_neg hx
  · show BaseAdmissibleP (correlate (sup D).1) (slotP D) (upB D c B₀ e)
    rw [sup_correlate hh]
    refine ⟨⟨⟨upB_admissible hh hc B₀ e hB₀.1.1, upB_literals hh B₀ e hB₀.1.2⟩, ?_⟩, upB_slot hh hc B₀ e⟩
    intro a ha
    rcases List.mem_append.mp ha with ha | ha
    · exact upB_exc hh hc B₀ e hB₀ a ha
    · exact upB_coh hh hc B₀ e hB₀ a ha

end VE.Readings
