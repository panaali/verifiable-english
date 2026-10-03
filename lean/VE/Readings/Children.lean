import VE.Readings.ChoiceFacts

/-! The children of a rule in a choice's document and in the superposed document correspond (the `childFwd`,
`childBack` and `sibling` conditions of `Sim`; docs/spec/composition-s2.md 1.4, 1.8).

Every `over` entry of a rule names a rule of the document S1 checked it in, on the same predicate, so it is an
author name and never the rule's own. A fixed rule's entry on an interface name is mapped to every qualified copy;
an unchosen copy is a child of the parents of the chosen copy (uniform precedence), and its own children, fixed
rules over the interface name, are children of the chosen copy. -/
namespace VE.Readings
open VE.SoftNorms (SoftNode SoftDoc soften children)
open VE.Rights (RightsDoc correlate)
open VE.Compose (Content)

/-- The rules of a document `build` assembles from a document's own candidates. -/
theorem build_names_reserved {D : Doc} (hh : Hyps D) (keep : String → Bool) (pick : ReadingSet → Option Candidate)
    (hpick : ∀ R a, pick R = some a → a ∈ R.candidates) {M : SoftNode}
    (hM : M ∈ (build D keep pick).1.soft.T.nodes) : reservedName M.name = false := by
  have hrf := (wellFormedDoc_parts hh.wf).1
  rw [(build_shape D keep pick).nodes, List.mem_append] at hM
  rcases hM with hM | hM
  · exact frame_not_reserved hh hM
  · obtain ⟨it, hit, hM⟩ := List.mem_flatMap.mp hM
    cases it with
    | fixed u c cs =>
      simp only [buildNodes] at hM
      split at hM
      · rw [mem_normsOf] at hM; subst hM; exact fixed_not_reserved hh hit
      · simp at hM
    | bar u b => simp [buildNodes] at hM
    | set R =>
      simp only [buildNodes] at hM
      split at hM
      · rename_i c cs hp
        rw [mem_normsOf] at hM; subst hM
        simp only [Option.bind_eq_some_iff, Option.map_eq_some_iff] at hp
        obtain ⟨a, hpa, c', hc', he⟩ := hp
        cases he
        simp only [reservedFree, Bool.and_eq_true, List.all_eq_true] at hrf
        have := hrf.2 _ hit
        simp only [List.all_eq_true, Bool.not_eq_true'] at this
        have := this a (hpick R a hpa)
        simpa [hc', contentReserved, Content.declared] using this
      · simp at hM

/-- An `over` entry of a rule of a checked document: an author name, not the rule's own, naming a rule of that
    document on the same predicate. -/
theorem build_over {D : Doc} (hh : Hyps D) (keep : String → Bool) (pick : ReadingSet → Option Candidate)
    (hpick : ∀ R a, pick R = some a → a ∈ R.candidates) (hw : sideWF D (build D keep pick) = true) {M : SoftNode}
    (hM : M ∈ (build D keep pick).1.soft.T.nodes) {x : String} (hx : x ∈ M.over) :
    reservedName x = false ∧ x ≠ M.name ∧
      ∃ M' ∈ (build D keep pick).1.soft.T.nodes, M'.name = x ∧ M'.pred = M.pred := by
  have hs := build_shape D keep pick
  obtain ⟨_, _, _, _, _, hov⟩ := nodeFacts_of_home D hh.chain _ hw hs.E hs.regulated M hM
  obtain ⟨M', hM', hn, hp⟩ := hov x hx
  refine ⟨hn ▸ build_names_reserved hh keep pick hpick hM', fun he => ?_, M', hM', hn, hp⟩
  -- a rule over itself is a cycle of the precedence graph
  have hv := VE.SoftNorms.softValid_of_wellFormed _ (build_soft_wf D hh.chain keep pick hw)
  have hac := (VE.Norms.precedence_acyclic _ hv.wf).1
  apply hac M.name
  apply VE.Route.DepPath.edge
  refine ⟨⟨M.name, M.over⟩, List.mem_map.mpr ⟨VE.SoftNorms.primeNode _ M, List.mem_map.mpr ⟨M, hM, rfl⟩, rfl⟩,
    rfl, ?_⟩
  simp only [VE.Route.deps, List.mem_filter, List.contains_iff_mem]
  refine ⟨he ▸ hx, ?_⟩
  simp only [VE.Route.nodeNames, VE.Norms.precedenceNodes, List.map_map, List.mem_map]
  exact ⟨VE.SoftNorms.primeNode _ M, List.mem_map.mpr ⟨M, hM, rfl⟩, rfl⟩

/-- A rule of a choice's document lies in a checked document built from the sets' own candidates. -/
theorem choice_home {D : Doc} (hh : Hyps D) (c : Choice) {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) :
    ∃ keep pick, (∀ R a, pick R = some a → a ∈ R.candidates) ∧ sideWF D (build D keep pick) = true ∧
      N ∈ (build D keep pick).1.soft.T.nodes := by
  rcases (mem_choiceNodes D c N).mp hN with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hc⟩
  · refine ⟨fun u => (attached D u).isEmpty, fun _ => none, (fun R a h => by cases h),
      (wellFormedDoc_parts hh.wf).2.2.2.2.1, ?_⟩
    show N ∈ (free D).1.soft.T.nodes
    rw [free, (build_shape D _ _).nodes]; exact List.mem_append_left _ hf
  · obtain ⟨keep, pick, hp, hw, hmem⟩ := fixed_home hh hu
    exact ⟨keep, pick, hp, hw, by rw [(build_shape D keep pick).nodes]; exact List.mem_append_right _ hmem⟩
  · refine ⟨_, _, fun R a' h => ?_, one_wf hh hm ha hc, ?_⟩
    · simp only at h
      split at h
      · exact List.mem_of_getElem? h
      · cases h
    · show N ∈ (one D D.sets[m].id i).1.soft.T.nodes
      rw [one, (build_shape D _ _).nodes]; exact List.mem_append_right _ (one_has hm ha hc)

theorem choice_over {D : Doc} (hh : Hyps D) (c : Choice) {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes)
    {x : String} (hx : x ∈ N.over) : reservedName x = false ∧ x ≠ N.name := by
  obtain ⟨keep, pick, hp, hw, hmem⟩ := choice_home hh c hN
  obtain ⟨h1, h2, _⟩ := build_over hh keep pick hp hw hmem hx
  exact ⟨h1, h2⟩

/-! ## Copies of interface names -/

theorem mem_copies {D : Doc} {x y : String} (h : y ∈ copies D x) : y = x ∨ ∃ k, y = qualify k x := by
  unfold copies at h
  split at h
  · simp only [List.mem_map, List.mem_range] at h
    obtain ⟨j, _, rfl⟩ := h
    exact Or.inr ⟨_, rfl⟩
  · simp at h; exact Or.inl h

theorem copies_plain {D : Doc} {x : String} (h : ∀ R ∈ D.sets, ("rule", x) ∉ interfaceOf R) : copies D x = [x] := by
  unfold copies
  rw [List.findIdx?_eq_none_iff.mpr]
  intro R hR
  cases he : (interfaceOf R).contains ("rule", x) with
  | false => rfl
  | true => exact absurd (List.contains_iff_mem.mp he) (h R hR)

theorem interface_declared {R : ReadingSet} {n : String × String} (h : n ∈ interfaceOf R) : n ∈ declaredBy R :=
  (List.mem_filter.mp h).1

theorem copies_iface {D : Doc} (hh : Hyps D) {m : Nat} (hm : m < D.sets.length) {n : String}
    (hn : ("rule", n) ∈ interfaceOf D.sets[m]) :
    copies D n = (List.range (setSize D m)).map (fun j => qualify (position D m j) n) := by
  unfold copies
  rw [List.findIdx?_eq_some_iff_getElem.mpr ⟨hm, by simpa using hn, fun j hj => ?_⟩]
  simp only [List.contains_iff_mem]
  intro hj'
  exact sets_declare_disjoint hh.nodup hh.da (Nat.lt_trans hj hm) hm (by omega) (interface_declared hj')
    (interface_declared hn) rfl

/-- The `over` entries of the image of a rule. -/
theorem mem_fmap_over {D : Doc} (hh : Hyps D) (c : Choice) {C : SoftNode} (hC : C ∈ (choiceDoc D c).1.soft.T.nodes)
    {y : String} : y ∈ (fmap D c C).over ↔
      (FixedNorm D C ∧ ∃ x ∈ C.over, y ∈ copies D x) ∨ (¬ FixedNorm D C ∧ y ∈ C.over) := by
  rcases (mem_choiceNodes D c C).mp hC with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hc⟩
  · have hnf : ¬ FixedNorm D C := fun ⟨u, cs, hu⟩ => fixed_not_frame hh hu hf
    rw [fmap_frame hh c hf]
    simp [hnf]
  · rw [fmap_fixed hh c hu]
    simp only [copyOver, List.mem_flatMap]
    exact ⟨fun h => Or.inl ⟨⟨u, cs, hu⟩, h⟩, fun h => h.elim (fun h => h.2) (fun h => absurd ⟨u, cs, hu⟩ h.1)⟩
  · have hnf : ¬ FixedNorm D C := by
      rintro ⟨u, cs, hu⟩
      have := chosenAt_fixed D hh.da c hu
      rw [chosenAt_chosen D hh.nodup hh.da c hm hi ha hc] at this
      cases this
    rw [fmap_chosen hh c hm hi ha hc]
    simp [gateNorm, hnf]

/-- The name of the image of a rule: its own author name, or a qualified copy of it. -/
theorem fmap_name_cases {D : Doc} (hh : Hyps D) (c : Choice) {N : SoftNode}
    (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) :
    (reservedName N.name = false ∧ (fmap D c N).name = N.name) ∨ ∃ k, (fmap D c N).name = qualify k N.name := by
  rw [fmap_name hh c hN, qName_chosenAt]
  rcases (mem_choiceNodes D c N).mp hN with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hc⟩
  · rw [chosenAt_frame hh c hf]; exact Or.inl ⟨frame_not_reserved hh hf, rfl⟩
  · rw [chosenAt_fixed D hh.da c hu]; exact Or.inl ⟨fixed_not_reserved hh hu, rfl⟩
  · rw [chosenAt_chosen D hh.nodup hh.da c hm hi ha hc]; exact Or.inr ⟨_, rfl⟩

theorem child_back {D : Doc} (hh : Hyps D) (c : Choice) {N C : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes)
    (hC : C ∈ (choiceDoc D c).1.soft.T.nodes)
    (h : fmap D c C ∈ VE.SoftNorms.childrenIn (sup D).1.soft.T.nodes (fmap D c N)) :
    C ∈ VE.SoftNorms.childrenIn (choiceDoc D c).1.soft.T.nodes N := by
  rw [VE.SoftNorms.mem_childrenIn_iff] at h ⊢
  obtain ⟨_, hp, hx⟩ := h
  refine ⟨hC, by rw [← (fmap_fields hh c hC).1, ← (fmap_fields hh c hN).1]; exact hp, ?_⟩
  rw [mem_fmap_over hh c hC] at hx
  rcases hx with ⟨_, x, hxC, hy⟩ | ⟨_, hy⟩
  · have hxr := (choice_over hh c hC hxC).1
    rcases mem_copies hy with he | ⟨k, he⟩ <;> rcases fmap_name_cases hh c hN with ⟨hr, hn⟩ | ⟨k', hn⟩
    · rw [hn] at he; rw [he]; exact hxC
    · rw [hn] at he; rw [← he] at hxr; rw [reservedName_qualify] at hxr; cases hxr
    · rw [hn] at he; rw [he, reservedName_qualify] at hr; cases hr
    · rw [hn] at he; rw [(qualify_inj he).2]; exact hxC
  · rcases fmap_name_cases hh c hN with ⟨_, hn⟩ | ⟨k', hn⟩
    · rw [hn] at hy; exact hy
    · rw [hn] at hy
      have := (choice_over hh c hC hy).1
      rw [reservedName_qualify] at this; cases this

/-! ## Children, forward -/

theorem mem_build_nodes {D : Doc} {keep : String → Bool} {pick : ReadingSet → Option Candidate} {M : SoftNode}
    (h : M ∈ (build D keep pick).1.soft.T.nodes) :
    M ∈ D.frame.soft.T.nodes ∨ (∃ u cs, Item.fixed u (.norm M) cs ∈ D.items) ∨
      (∃ R a, Item.set R ∈ D.items ∧ pick R = some a ∧ a.content = some (.norm M)) := by
  rw [(build_shape D keep pick).nodes, List.mem_append] at h
  rcases h with h | h
  · exact Or.inl h
  · obtain ⟨it, hit, hM⟩ := List.mem_flatMap.mp h
    cases it with
    | fixed u c cs =>
      simp only [buildNodes] at hM
      split at hM
      · rw [mem_normsOf] at hM; subst hM; exact Or.inr (Or.inl ⟨u, cs, hit⟩)
      · simp at hM
    | bar u b => simp [buildNodes] at hM
    | set R =>
      simp only [buildNodes] at hM
      split at hM
      · rename_i c cs hp
        rw [mem_normsOf] at hM; subst hM
        simp only [Option.bind_eq_some_iff, Option.map_eq_some_iff] at hp
        obtain ⟨a, hpa, c', hc', he⟩ := hp
        cases he
        exact Or.inr (Or.inr ⟨R, a, hit, hpa, hc'⟩)
      · simp at hM

/-- No set declares the name of a frame or fixed rule. -/
theorem no_set_declares {D : Doc} (hh : Hyps D) {N : SoftNode}
    (hN : N ∈ D.frame.soft.T.nodes ∨ FixedNorm D N) : ∀ R ∈ D.sets, ("rule", N.name) ∉ declaredBy R := by
  intro R hR hd
  rcases hN with hf | ⟨u, cs, hu⟩
  · have hd' := hd
    simp only [declaredBy, List.mem_flatMap, List.mem_filterMap] at hd'
    obtain ⟨c', ⟨a, ha, hc⟩, hx⟩ := hd'
    obtain ⟨m, hm, rfl⟩ := mem_sets_getElem hR
    obtain ⟨i, hi, rfl⟩ := List.getElem_of_mem ha
    have ha' : D.sets[m].candidates[i]? = some D.sets[m].candidates[i] := List.getElem?_eq_getElem hi
    obtain ⟨N', rfl, hn⟩ := declared_rule_norm
      ((contrib_zero D hh.noRights).2 _ (List.getElem_mem hm) _ (List.getElem_mem hi) _ hc) hx
    exact (build_names D hh.chain _ _ (one_wf hh hm ha' hc)).2 N hf N' (one_has hm ha' hc) hn.symm
  · exact ((distinctAcrossSets_spec D).mp hh.da).1 R hR _ hd u _ cs hu ("rule", N.name)
      (by simp [Content.declared]) rfl

/-- The rules of the document of candidate `i` of the `m`-th set: the frame's, fixed ones and that candidate's. -/
theorem mem_one_nodes {D : Doc} (hh : Hyps D) {m : Nat} (hm : m < D.sets.length) {i : Nat} {M : SoftNode}
    (h : M ∈ (one D D.sets[m].id i).1.soft.T.nodes) :
    M ∈ D.frame.soft.T.nodes ∨ FixedNorm D M ∨
      (∃ a, D.sets[m].candidates[i]? = some a ∧ a.content = some (.norm M)) := by
  rcases mem_build_nodes h with h | ⟨u, cs, hu⟩ | ⟨R, a, hR, hpa, hc⟩
  · exact Or.inl h
  · exact Or.inr (Or.inl ⟨u, cs, hu⟩)
  · split at hpa
    · rename_i he
      obtain ⟨m', hm', rfl⟩ := mem_sets_getElem (mem_sets.mpr hR)
      have : m' = m := ids_inj hh.nodup hm' hm (by simpa using he)
      subst this
      exact Or.inr (Or.inr ⟨a, hpa, hc⟩)
    · cases hpa

theorem child_fwd {D : Doc} (hh : Hyps D) (c : Choice) {N C : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes)
    (hC : C ∈ VE.SoftNorms.childrenIn (choiceDoc D c).1.soft.T.nodes N) :
    fmap D c C ∈ VE.SoftNorms.childrenIn (sup D).1.soft.T.nodes (fmap D c N) := by
  rw [VE.SoftNorms.mem_childrenIn_iff] at hC ⊢
  obtain ⟨hCm, hp, hx⟩ := hC
  refine ⟨fmap_mem hh c hCm, by rw [(fmap_fields hh c hCm).1, (fmap_fields hh c hN).1]; exact hp, ?_⟩
  rw [mem_fmap_over hh c hCm]
  have hic := (interfaceClosed_spec D).mp (wellFormedDoc_parts hh.wf).2.2.1
  rcases (mem_choiceNodes D c N).mp hN with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hc⟩
  · -- a frame rule's name is no interface name
    rw [fmap_frame hh c hf]
    by_cases hcf : FixedNorm D C
    · refine Or.inl ⟨hcf, N.name, hx, ?_⟩
      rw [copies_plain (fun R hR hi' => no_set_declares hh (Or.inl hf) R hR (interface_declared hi'))]
      simp
    · exact Or.inr ⟨hcf, hx⟩
  · rw [fmap_fixed hh c hu]
    by_cases hcf : FixedNorm D C
    · refine Or.inl ⟨hcf, N.name, hx, ?_⟩
      rw [copies_plain (fun R hR hi' => no_set_declares hh (Or.inr ⟨u, cs, hu⟩) R hR (interface_declared hi'))]
      simp [copyOver]
    · exact Or.inr ⟨hcf, hx⟩
  · rw [fmap_chosen hh c hm hi ha hc]
    have hdecl : ("rule", N.name) ∈ declaredBy D.sets[m] := candidate_declares hm ha hc (by simp [Content.declared])
    have hilt : i < setSize D m := by rw [setSize_eq hm]; exact (List.getElem?_eq_some_iff.mp ha).1
    rcases (mem_choiceNodes D c C).mp hCm with hcf | ⟨u, cs, hu⟩ | ⟨m', hm', i', a', hi', ha', hc'⟩
    · -- a frame rule over a candidate's rule: its `over` entry names no rule of the free document
      exfalso
      obtain ⟨_, _, M', hM', hn, _⟩ := build_over hh (fun u => (attached D u).isEmpty) (fun _ => none)
        (fun R a h => by cases h) (wellFormedDoc_parts hh.wf).2.2.2.2.1
        (by rw [(build_shape D _ _).nodes]; exact List.mem_append_left _ hcf) hx
      rcases mem_build_nodes hM' with h1 | h1 | ⟨R, a'', _, hpa, _⟩
      · exact no_set_declares hh (Or.inl h1) _ (List.getElem_mem hm) (hn ▸ hdecl)
      · exact no_set_declares hh (Or.inr h1) _ (List.getElem_mem hm) (hn ▸ hdecl)
      · cases hpa
    · refine Or.inl ⟨⟨u, cs, hu⟩, N.name, hx, ?_⟩
      have hif : ("rule", N.name) ∈ interfaceOf D.sets[m] :=
        hic u _ cs hu ("rule", N.name) (by simp [uses, nodeUses, hx]) _ (List.getElem_mem hm) hdecl
      rw [copies_iface hh hm hif]
      exact List.mem_map.mpr ⟨i, List.mem_range.mpr hilt, rfl⟩
    · exfalso
      have hCnf : ¬ FixedNorm D C := by
        rintro ⟨u, cs, hu⟩
        have := chosenAt_fixed D hh.da c hu
        rw [chosenAt_chosen D hh.nodup hh.da c hm' hi' ha' hc'] at this
        cases this
      obtain ⟨_, hne, M', hM', hn, _⟩ := build_over hh (fun u => (attached D u).all (· == D.sets[m'].id))
        (fun R => if R.id == D.sets[m'].id then R.candidates[i']? else none)
        (fun R a h => by simp only at h; split at h; exact List.mem_of_getElem? h; cases h) (one_wf hh hm' ha' hc')
        (by rw [(build_shape D _ _).nodes]; exact List.mem_append_right _ (one_has hm' ha' hc')) hx
      rcases mem_one_nodes hh hm' hM' with h1 | h1 | ⟨a'', ha'', hc''⟩
      · exact no_set_declares hh (Or.inl h1) _ (List.getElem_mem hm) (hn ▸ hdecl)
      · exact no_set_declares hh (Or.inr h1) _ (List.getElem_mem hm) (hn ▸ hdecl)
      · have hMC : M' = C := by
          rw [ha'] at ha''; cases ha''; rw [hc'] at hc''; cases hc''; rfl
        rw [hMC] at hn
        by_cases hmm : m' = m
        · subst hmm
          rw [hi] at hi'; cases hi'
          rw [ha] at ha'; cases ha'
          rw [hc] at hc'; cases hc'
          exact hne hn.symm
        · exact sets_declare_disjoint hh.nodup hh.da hm' hm hmm
            (candidate_declares hm' ha' hc' (x := ("rule", C.name)) (by simp [Content.declared])) hdecl hn

/-! ## The sibling condition -/

/-- A compatible choice takes one candidate in every open set. -/
theorem choice_index {D : Doc} (hh : Hyps D) {c : Choice} (hc : Compatible D c) {m : Nat} (hm : m < D.sets.length) :
    ∃ i, c.index D.sets[m].id = some i ∧ i < D.sets[m].candidates.length := by
  have hcm : complete D c = true := by
    simp only [Compatible, compatible, Bool.and_eq_true] at hc; exact hc.1.1
  have hmap := complete_map hcm
  have hcn : (c.map (·.1)).Nodup := hmap ▸ hh.nodup
  have hlen : c.length = D.sets.length := by simpa using congrArg List.length hmap
  have hcm' : m < c.length := hlen ▸ hm
  have hfst : c[m].1 = D.sets[m].id := by
    have := congrArg (·[m]?) hmap
    simpa [List.getElem?_eq_getElem hcm', List.getElem?_eq_getElem hm] using this
  have hidx := index_of_mem hcn (List.getElem_mem hcm')
  rw [hfst] at hidx
  refine ⟨c[m].2, hidx, ?_⟩
  obtain ⟨m', hf, hi⟩ := candidate_isSome (complete_mem hcm (List.getElem_mem hcm'))
  rw [hfst, findIdx_of_nodup hh.nodup hm] at hf
  cases hf
  rw [← setSize_eq hm]; exact hi

theorem sibling {D : Doc} (hh : Hyps D) {c : Choice} (hc : Compatible D c) {N : SoftNode}
    (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) {C : SoftNode}
    (hC : C ∈ VE.SoftNorms.childrenIn (sup D).1.soft.T.nodes (fmap D c N))
    (hext : ∀ N' ∈ (choiceDoc D c).1.soft.T.nodes, fmap D c N' ≠ C) {G : SoftNode}
    (hG : G ∈ VE.SoftNorms.childrenIn (sup D).1.soft.T.nodes C) :
    ∃ N'' ∈ VE.SoftNorms.childrenIn (choiceDoc D c).1.soft.T.nodes N,
      G ∈ VE.SoftNorms.childrenIn (sup D).1.soft.T.nodes (fmap D c N'') := by
  rw [VE.SoftNorms.mem_childrenIn_iff] at hC hG
  obtain ⟨hCX, hCp, hCo⟩ := hC
  obtain ⟨hGX, hGp, hGo⟩ := hG
  have hic := (interfaceClosed_spec D).mp (wellFormedDoc_parts hh.wf).2.2.1
  -- C is an unchosen copy
  rcases (mem_supNodes D C).mp hCX with hf | ⟨u, F, cs, hu, rfl⟩ | ⟨m', hm', i', a', N', ha', hc', rfl⟩
  · exact absurd (fmap_frame hh c hf) (hext C ((mem_choiceNodes D c C).mpr (Or.inl hf)))
  · exact absurd (fmap_fixed hh c hu) (hext F ((mem_choiceNodes D c F).mpr (Or.inr (Or.inl ⟨u, cs, hu⟩))))
  obtain ⟨i, hi, hilt⟩ := choice_index hh hc hm'
  have hii : i' ≠ i := by
    rintro rfl
    exact hext N' ((mem_choiceNodes D c N').mpr (Or.inr (Or.inr ⟨m', hm', i', a', hi, ha', hc'⟩)))
      (fmap_chosen hh c hm' hi ha' hc')
  have hdecl : ("rule", N'.name) ∈ declaredBy D.sets[m'] := candidate_declares hm' ha' hc' (by simp [Content.declared])
  -- G is a fixed rule over the interface name
  rcases (mem_supNodes D G).mp hGX with hf | ⟨u, F, cs, hu, rfl⟩ | ⟨m'', hm'', i'', a'', N'', ha'', hc'', rfl⟩
  · exfalso
    have := (choice_over hh c ((mem_choiceNodes D c G).mpr (Or.inl hf)) hGo).1
    rw [show (gateNorm D m' i' N').name = qualify _ _ from rfl, reservedName_qualify] at this; cases this
  · have hFY : F ∈ (choiceDoc D c).1.soft.T.nodes := (mem_choiceNodes D c F).mpr (Or.inr (Or.inl ⟨u, cs, hu⟩))
    have hFo : N'.name ∈ F.over := by
      simp only [copyOver, List.mem_flatMap] at hGo
      obtain ⟨x, hx, hy⟩ := hGo
      rcases mem_copies hy with he | ⟨k, he⟩
      · have := (choice_over hh c hFY hx).1
        rw [← he, show (gateNorm D m' i' N').name = qualify _ _ from rfl, reservedName_qualify] at this; cases this
      · rw [(qualify_inj he).2]; exact hx
    have hif : ("rule", N'.name) ∈ interfaceOf D.sets[m'] :=
      hic u _ cs hu ("rule", N'.name) (by simp [uses, nodeUses, hFo]) _ (List.getElem_mem hm') hdecl
    -- the chosen candidate's rule of that name
    have hai : D.sets[m'].candidates[i]? = some D.sets[m'].candidates[i] := List.getElem?_eq_getElem hilt
    have hr := hh.ready
    obtain ⟨ci, hci⟩ : ∃ ci, D.sets[m'].candidates[i].content = some ci := by
      simp only [supReady, Bool.and_eq_true, List.all_eq_true] at hr
      have := (hr.1.1.1.1.2 _ (List.getElem_mem hm'))
      exact Option.isSome_iff_exists.mp (this.2 _ (List.getElem_mem hilt))
    have hdi : ("rule", N'.name) ∈ ci.declared := by
      have := (List.mem_filter.mp hif).2
      simp only [List.all_eq_true] at this
      have := this _ (List.getElem_mem hilt)
      simpa [hci] using this
    obtain ⟨Nc, rfl, hNc⟩ := declared_rule_norm
      ((contrib_zero D hh.noRights).2 _ (List.getElem_mem hm') _ (List.getElem_mem hilt) _ hci) hdi
    have hNcY : Nc ∈ (choiceDoc D c).1.soft.T.nodes :=
      (mem_choiceNodes D c Nc).mpr (Or.inr (Or.inr ⟨m', hm', i, _, hi, hai, hci⟩))
    -- uniform precedence: the copies carry one `over` list
    have hsp := hh.sp
    simp only [superposable, Bool.and_eq_true] at hsp
    have hup := (uniformPrecedence_spec D).mp hsp.1.2 u (.norm F) cs hu F rfl N'.name hFo D.sets[m']
      (List.getElem_mem hm') hif a' (List.mem_of_getElem? ha') D.sets[m'].candidates[i] (List.getElem_mem hilt)
      N' Nc (by simp [hc', ruleNamed]) (by simp [hci, ruleNamed, hNc])
    have h1 : (fmap D c N).name ∈ Nc.over := (hup _).mp hCo
    have h2 : N.name ∈ Nc.over := by
      rcases fmap_name_cases hh c hN with ⟨_, hn⟩ | ⟨k, hn⟩
      · rw [hn] at h1; exact h1
      · rw [hn] at h1
        have := (choice_over hh c hNcY h1).1
        rw [reservedName_qualify] at this; cases this
    -- the fixed rule's entry resolves to the chosen rule in its document: one predicate
    have hA : Attached D u D.sets[m'].id :=
      .direct hu ("rule", N'.name) (by simp [uses, nodeUses, hFo]) _ (List.getElem_mem hm') rfl hdecl
    have hall : (attached D u).all (· == D.sets[m'].id) = true := by
      have := (singlyAttached_spec D).mp (wellFormedDoc_parts hh.wf).2.2.2.1
      rw [List.all_eq_true]
      intro t' ht'
      have := this u _ t' hA ((attached_iff D u t').mp ht')
      simp [this]
    have hFhome : F ∈ (one D D.sets[m'].id i).1.soft.T.nodes := by
      rw [one, (build_shape D _ _).nodes]
      apply List.mem_append_right
      exact List.mem_flatMap.mpr ⟨_, hu, by simp [buildNodes, hall, normsOf]⟩
    obtain ⟨_, _, M', hM', hn', hp'⟩ := build_over hh (fun u => (attached D u).all (· == D.sets[m'].id))
      (fun R => if R.id == D.sets[m'].id then R.candidates[i]? else none)
      (fun R a h => by simp only at h; split at h; exact List.mem_of_getElem? h; cases h) (one_wf hh hm' hai hci)
      hFhome hFo
    have hMc : M' = Nc := by
      rcases mem_one_nodes hh hm' hM' with h | h | ⟨a3, ha3, hc3⟩
      · exact absurd (hn' ▸ hdecl) (no_set_declares hh (Or.inl h) _ (List.getElem_mem hm'))
      · exact absurd (hn' ▸ hdecl) (no_set_declares hh (Or.inr h) _ (List.getElem_mem hm'))
      · rw [hai] at ha3; cases ha3; rw [hci] at hc3; cases hc3; rfl
    rw [hMc] at hp'
    have hNp : (fmap D c N).pred = N.pred := (fmap_fields hh c hN).1
    have hpred : Nc.pred = N.pred := by
      rw [hp', ← hNp, ← hCp]
      exact hGp
    refine ⟨Nc, (VE.SoftNorms.mem_childrenIn_iff).mpr ⟨hNcY, hpred, h2⟩, ?_⟩
    rw [VE.SoftNorms.mem_childrenIn_iff, fmap_chosen hh c hm' hi hai hci]
    refine ⟨hGX, hp'.symm, ?_⟩
    simp only [copyOver, List.mem_flatMap]
    refine ⟨N'.name, hFo, ?_⟩
    rw [copies_iface hh hm' hif]
    refine List.mem_map.mpr ⟨i, List.mem_range.mpr (by rw [setSize_eq hm']; exact hilt), ?_⟩
    simp [gateNorm, hNc]
  · exfalso
    have hGo' : (gateNorm D m' i' N').name ∈ N''.over := hGo
    obtain ⟨hr, _, _⟩ := build_over hh (fun u => (attached D u).all (· == D.sets[m''].id))
      (fun R => if R.id == D.sets[m''].id then R.candidates[i'']? else none)
      (fun R a h => by simp only at h; split at h; exact List.mem_of_getElem? h; cases h) (one_wf hh hm'' ha'' hc'')
      (by rw [(build_shape D _ _).nodes]; exact List.mem_append_right _ (one_has hm'' ha'' hc'')) hGo'
    rw [show (gateNorm D m' i' N').name = qualify _ _ from rfl, reservedName_qualify] at hr; cases hr

end VE.Readings
