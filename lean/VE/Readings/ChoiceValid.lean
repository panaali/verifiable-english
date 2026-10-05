import VE.Readings.SupEnv
import VE.NormDefaults.Dag

/-! A compatible choice's document is valid as W1 reads it (docs/spec/composition-s2.md 8.4, the structural part of
`choice_wellFormed`).

`superposable D` checks the chain on `sup D` alone, and every candidate's own document is checked by S1; the
document of a compatible choice is neither. Its elaboration `soften Y` is shown `VE.Norms.Valid` here from those
checks: every rule of `Y` lies in a document S1 checked whose rules are all `Y`'s (`choice_home_in`); its
precedence graph maps into `sup D`'s through `fmap` and so has no cycle; its stratum graph has the stratum graph of
`sup D` over the same nodes as a supergraph, because every layer symbol a formula of `soften Y` reads is read by the
corresponding formula of `soften (sup D)`; and every formula of a layer is typed over the environment below it. The
size limits of `WellFormedSoft` are not claimed here. -/
namespace VE.Readings
open VE.Norms (envAt size)
open VE.SoftNorms (SoftNode SoftDoc soften WellFormedSoft decisions decisionNames envPrime)
open VE.Rights (RightsDoc correlate)
open VE.Route (DepNode DepEdge DepPath DagAcyclic nodeNames deps)

/-! ## Homes inside the choice -/

section Home
variable {D : Doc} (hh : Hyps D) {c : Choice} (hc : Compatible D c)
include hh hc

omit hc in
theorem chosen_in_choice {m : Nat} (hm : m < D.sets.length) {i : Nat} (hi : c.index D.sets[m].id = some i)
    {M : SoftNode} (h : M ∈ (one D D.sets[m].id i).1.soft.T.nodes) : M ∈ (choiceDoc D c).1.soft.T.nodes := by
  rcases mem_one_nodes hh hm h with hf | hx | ⟨a, ha, hac⟩
  · exact (mem_choiceNodes D c M).mpr (Or.inl hf)
  · exact (mem_choiceNodes D c M).mpr (Or.inr (Or.inl hx))
  · exact (mem_choiceNodes D c M).mpr (Or.inr (Or.inr ⟨m, hm, i, a, hi, ha, hac⟩))

omit hh hc in
theorem free_in_choice {M : SoftNode} (h : M ∈ (free D).1.soft.T.nodes) : M ∈ (choiceDoc D c).1.soft.T.nodes := by
  rcases mem_build_nodes h with hf | ⟨u, cs, hu⟩ | ⟨R, a, _, hpa, _⟩
  · exact (mem_choiceNodes D c M).mpr (Or.inl hf)
  · exact (mem_choiceNodes D c M).mpr (Or.inr (Or.inl ⟨u, cs, hu⟩))
  · cases hpa

/-- Every rule of a compatible choice's document lies in a document S1 checked, all of whose rules are the choice's. -/
theorem choice_home_in {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) :
    ∃ H : RightsDoc × List VE.Formula, sideWF D H = true ∧ N ∈ H.1.soft.T.nodes ∧
      H.1.soft.E = D.frame.soft.E ∧ H.1.soft.T.regulated = D.frame.soft.T.regulated ∧
      (∀ M ∈ H.1.soft.T.nodes, M ∈ (choiceDoc D c).1.soft.T.nodes) := by
  obtain ⟨_, _, _, hsa, hfree, hone⟩ := wellFormedDoc_parts hh.wf
  have hfreeE := build_shape D (fun u => (attached D u).isEmpty) (fun _ => none)
  rcases (mem_choiceNodes D c N).mp hN with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hac⟩
  · refine ⟨free D, hfree, ?_, hfreeE.E, hfreeE.regulated, fun M hM => free_in_choice hM⟩
    rw [free, hfreeE.nodes]; exact List.mem_append_left _ hf
  · cases hat : attached D u with
    | nil =>
      refine ⟨free D, hfree, ?_, hfreeE.E, hfreeE.regulated, fun M hM => free_in_choice hM⟩
      rw [free, hfreeE.nodes]
      exact List.mem_append_right _ (List.mem_flatMap.mpr ⟨_, hu, by simp [buildNodes, hat, normsOf]⟩)
    | cons t rest =>
      have hA : Attached D u t := (attached_iff D u t).mp (by rw [hat]; simp)
      obtain ⟨R, hR, rfl⟩ := attached_set hA
      obtain ⟨m, hm, rfl⟩ := mem_sets_getElem hR
      obtain ⟨i, hi, hilt⟩ := choice_index hh hc hm
      obtain ⟨ct, hct⟩ : ∃ ct, D.sets[m].candidates[i].content = some ct := by
        have hr := hh.ready
        simp only [supReady, Bool.and_eq_true, List.all_eq_true] at hr
        exact Option.isSome_iff_exists.mp ((hr.1.1.1.1.1.1.2 _ (List.getElem_mem hm)).2 _ (List.getElem_mem hilt))
      have hw := one_wf hh hm (List.getElem?_eq_getElem hilt) hct
      have hs := build_shape D (fun u => (attached D u).all (· == D.sets[m].id))
        (fun R => if R.id == D.sets[m].id then R.candidates[i]? else none)
      refine ⟨one D D.sets[m].id i, hw, ?_, hs.E, hs.regulated, fun M hM => chosen_in_choice hh hm hi hM⟩
      have hall : (attached D u).all (· == D.sets[m].id) = true := by
        have := (singlyAttached_spec D).mp hsa
        rw [List.all_eq_true]
        intro t' ht'
        have := this u D.sets[m].id t' hA ((attached_iff D u t').mp ht')
        simp [this]
      show N ∈ (build D _ _).1.soft.T.nodes
      rw [hs.nodes]
      exact List.mem_append_right _ (List.mem_flatMap.mpr ⟨_, hu, by simp [buildNodes, hall, normsOf]⟩)
  · have hs := build_shape D (fun u => (attached D u).all (· == D.sets[m].id))
      (fun R => if R.id == D.sets[m].id then R.candidates[i]? else none)
    refine ⟨one D D.sets[m].id i, one_wf hh hm ha hac, ?_, hs.E, hs.regulated,
      fun M hM => chosen_in_choice hh hm hi hM⟩
    show N ∈ (build D _ _).1.soft.T.nodes
    rw [hs.nodes]; exact List.mem_append_right _ (one_has hm ha hac)

/-- An `over` entry of a rule of the choice's document names a rule of it on the same predicate. -/
theorem choice_over_closed {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) {x : String} (hx : x ∈ N.over) :
    ∃ M ∈ (choiceDoc D c).1.soft.T.nodes, M.name = x ∧ M.pred = N.pred := by
  obtain ⟨H, hw, hNH, hE, hR, hsub⟩ := choice_home_in hh hc hN
  obtain ⟨_, _, _, _, _, hov⟩ := nodeFacts_of_home D hh.chain H hw hE hR N hNH
  obtain ⟨M, hM, hn, hp⟩ := hov x hx
  exact ⟨M, hsub M hM, hn, hp⟩

end Home

/-! ## The precedence graph -/

theorem depPath_map {ns ns' : List DepNode} (f : String → String)
    (h : ∀ a b, DepEdge ns a b → DepPath ns' (f a) (f b)) : ∀ {a b}, DepPath ns a b → DepPath ns' (f a) (f b)
  | _, _, .edge he => h _ _ he
  | _, _, .trans h₁ h₂ => .trans (depPath_map f h h₁) (depPath_map f h h₂)

theorem dagAcyclic_of_map {ns ns' : List DepNode} (f : String → String)
    (h : ∀ a b, DepEdge ns a b → DepPath ns' (f a) (f b)) (hac : DagAcyclic ns') : DagAcyclic ns :=
  fun a hp => hac (f a) (depPath_map f h hp)

theorem mem_precedenceNodes {T : VE.Norms.Tree} {n : DepNode} :
    n ∈ VE.Norms.precedenceNodes T ↔ ∃ N ∈ T.nodes, n = ⟨N.name, N.over⟩ := by
  simp only [VE.Norms.precedenceNodes, List.mem_map]
  exact ⟨fun ⟨N, hN, he⟩ => ⟨N, hN, he.symm⟩, fun ⟨N, hN, he⟩ => ⟨N, hN, he.symm⟩⟩

theorem soften_nodes (X : SoftDoc) : (soften X).T.nodes = X.T.nodes.map (VE.SoftNorms.primeNode X) := rfl

theorem precedence_names (X : SoftDoc) :
    nodeNames (VE.Norms.precedenceNodes (soften X).T) = X.T.nodes.map (·.name) := by
  simp [nodeNames, VE.Norms.precedenceNodes, soften_nodes, VE.SoftNorms.primeNode]

section Prec
variable {D : Doc} (hh : Hyps D) {c : Choice} (hc : Compatible D c)
include hh hc

/-- The name in `sup D` of the rule of the choice's document with a given name. -/
def fname (D : Doc) (c : Choice) (n : String) : String :=
  (((choiceDoc D c).1.soft.T.nodes.find? (·.name == n)).map (fun N => (fmap D c N).name)).getD n

omit hc in
theorem fname_eq {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) : fname D c N.name = (fmap D c N).name := by
  unfold fname
  rw [VE.SoftNorms.find_key (fun M : SoftNode => M.name) _ (choice_names_nodup hh c) N hN]
  rfl

theorem choice_precedence_acyclic : DagAcyclic (VE.Norms.precedenceNodes (soften (choiceDoc D c).1.soft).T) := by
  have hX := VE.SoftNorms.softValid_of_wellFormed _ (sup_wfSoft hh)
  have hacX := (VE.Norms.precedence_acyclic _ hX.wf).1
  apply dagAcyclic_of_map (fname D c) _ hacX
  intro a b ⟨n, hn, hna, hb⟩
  obtain ⟨N', hN', rfl⟩ := mem_precedenceNodes.mp hn
  rw [soften_nodes, List.mem_map] at hN'
  obtain ⟨N, hN, rfl⟩ := hN'
  simp only [VE.SoftNorms.primeNode] at hna hb
  subst hna
  simp only [deps, List.mem_filter, List.contains_iff_mem] at hb
  obtain ⟨hbo, _⟩ := hb
  obtain ⟨M, hM, rfl, hp⟩ := choice_over_closed hh hc hN hbo
  have hch : N ∈ VE.SoftNorms.childrenIn (choiceDoc D c).1.soft.T.nodes M :=
    VE.SoftNorms.mem_childrenIn_iff.mpr ⟨hN, hp.symm, hbo⟩
  have hfw := VE.SoftNorms.mem_childrenIn_iff.mp (child_fwd hh c hM hch)
  rw [fname_eq hh hN, fname_eq hh hM]
  apply DepPath.edge
  refine ⟨⟨(fmap D c N).name, (fmap D c N).over⟩, mem_precedenceNodes.mpr ⟨VE.SoftNorms.primeNode _ (fmap D c N),
    by rw [soften_nodes]; exact List.mem_map.mpr ⟨_, fmap_mem hh c hN, rfl⟩, rfl⟩, rfl, ?_⟩
  simp only [deps, List.mem_filter, List.contains_iff_mem]
  refine ⟨hfw.2.2, ?_⟩
  rw [precedence_names]
  exact List.mem_map.mpr ⟨_, fmap_mem hh c hM, rfl⟩

theorem choice_precedence_order : ∃ o, VE.Route.dependencyOrder (VE.Norms.precedenceNodes (soften (choiceDoc D c).1.soft).T) = .ok o :=
  VE.NormDefaults.dependencyOrder_ok _ (by rw [precedence_names]; exact choice_names_nodup hh c)
    (choice_precedence_acyclic hh hc)

end Prec

end VE.Readings

/-! ## The stratum graph: every layer symbol a formula of `soften Y` reads, `soften (sup D)` reads too -/

namespace VE.Readings
open VE.Norms (envAt size preds anyF)
open VE.SoftNorms (SoftNode SoftDoc soften coreNode liveStrictIn strictYieldsIn strictSelectsIn strictDecidesIn
  strictDecidesF blockedF eligibleF liveF exceptedF switchF switchIn outweighsF domWith effF opponents derived
  derivedList childrenIn mem_preds_anyF WellFormedSoft)
open VE.Rights (RightsDoc correlate)
open VE.Route (DepNode DepEdge DepPath DagAcyclic nodeNames deps)

section Strat
variable {D : Doc} (hh : Hyps D) {c : Choice} (hc : Compatible D c)
  {L : String → Prop}
  (hLe : ∀ N ∈ (choiceDoc D c).1.soft.T.nodes, N.mode = .default → ¬ L (VE.SoftNorms.exceptedName N))
  (hLo : ∀ N ∈ (choiceDoc D c).1.soft.T.nodes, ∀ π ∈ N.alterable, ¬ L (VE.SoftNorms.offName N π))

include hh in
theorem fmap_guard_preds {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) :
    ∀ q ∈ preds N.guard, q ∈ preds (fmap D c N).guard := by
  intro q hq
  rcases (mem_choiceNodes D c N).mp hN with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hc'⟩
  · rw [fmap_frame hh c hf]; exact hq
  · rw [fmap_fixed hh c hu]; exact hq
  · rw [fmap_chosen hh c hm hi ha hc']
    simp [gateNorm, preds, hq]

theorem mem_preds_liveStrict {regs : List VE.Norms.Regulated} {N : SoftNode} {q : String} :
    q ∈ preds (liveStrictIn regs N) ↔ q ∈ preds N.guard ∨ (∃ U ∈ N.carveOuts, q ∈ preds U) ∨
      q ∈ preds (switchIn regs N) := by
  simp only [liveStrictIn, preds, List.mem_append, mem_preds_anyF]
  constructor
  · rintro ((h | h) | h)
    · exact Or.inl h
    · exact Or.inr (Or.inl h)
    · exact Or.inr (Or.inr h)
  · rintro (h | h | h)
    · exact Or.inl (Or.inl h)
    · exact Or.inl (Or.inr h)
    · exact Or.inr h

include hh hLo in
/-- The live condition of a rule, read through `fmap`, with core or own switches. -/
theorem preds_live_fmap (core : Bool) {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) {q : String}
    (hq : q ∈ preds (liveStrictIn (choiceDoc D c).1.soft.T.regulated (if core then coreNode N else N))) (hL : L q) :
    q ∈ preds (liveStrictIn (sup D).1.soft.T.regulated (if core then coreNode (fmap D c N) else fmap D c N)) := by
  obtain ⟨_, _, hmode, _, halt, hcarve⟩ := fmap_fields hh c hN
  have hg : ∀ x, (if core then coreNode x else x).guard = x.guard := by intro x; cases core <;> rfl
  have hco : ∀ x, (if core then coreNode x else x).carveOuts = x.carveOuts := by intro x; cases core <;> rfl
  have hal : ∀ x, ∀ π ∈ (if core then coreNode x else x).alterable, π ∈ x.alterable := by
    intro x π hπ
    cases core
    · exact hπ
    · simp only [coreNode, if_true] at hπ; split at hπ
      · exact hπ
      · cases hπ
  have hnm : ∀ x, (if core then coreNode x else x).name = x.name := by intro x; cases core <;> rfl
  rcases mem_preds_liveStrict.mp hq with h | ⟨U, hU, h⟩ | h
  · rw [hg] at h
    exact mem_preds_liveStrict.mpr (Or.inl (by rw [hg]; exact fmap_guard_preds hh hN q h))
  · rw [hco] at hU
    exact mem_preds_liveStrict.mpr (Or.inr (Or.inl ⟨U, by rw [hco, hcarve]; exact hU, h⟩))
  · exfalso
    simp only [switchIn, mem_preds_anyF, List.mem_map] at h
    obtain ⟨_, ⟨π, hπ, rfl⟩, h⟩ := h
    have := VE.SoftNorms.mem_preds_atom h
    subst this
    simp only [VE.SoftNorms.offName, hnm] at hL
    exact hLo N hN π (hal N π hπ) (by simpa [VE.SoftNorms.offName] using hL)

theorem coreNode_fields (N : SoftNode) : (coreNode N).name = N.name ∧ (coreNode N).pred = N.pred ∧
    (coreNode N).sign = N.sign ∧ (coreNode N).mode = N.mode ∧ (coreNode N).over = N.over := ⟨rfl, rfl, rfl, rfl, rfl⟩

include hh in
/-- A child of a core rule of the choice's document is the core of a child, and its image is a child of the image. -/
theorem core_child_fwd {N C : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes)
    (hC : C ∈ childrenIn ((choiceDoc D c).1.soft.T.nodes.map coreNode) (coreNode N)) :
    ∃ C₀ ∈ (choiceDoc D c).1.soft.T.nodes, C = coreNode C₀ ∧
      coreNode (fmap D c C₀) ∈ childrenIn ((sup D).1.soft.T.nodes.map coreNode) (coreNode (fmap D c N)) := by
  obtain ⟨hCm, hp, hx⟩ := VE.SoftNorms.mem_childrenIn_iff.mp hC
  obtain ⟨C₀, hC₀, rfl⟩ := List.mem_map.mp hCm
  have hch : C₀ ∈ childrenIn (choiceDoc D c).1.soft.T.nodes N :=
    VE.SoftNorms.mem_childrenIn_iff.mpr ⟨hC₀, hp, hx⟩
  obtain ⟨hf, hfp, hfx⟩ := VE.SoftNorms.mem_childrenIn_iff.mp (child_fwd hh c hN hch)
  exact ⟨C₀, hC₀, rfl, VE.SoftNorms.mem_childrenIn_iff.mpr ⟨List.mem_map.mpr ⟨_, hf, rfl⟩, hfp, hfx⟩⟩

theorem mem_preds_strictYields {regs : List VE.Norms.Regulated} {ns : List SoftNode} {f : Nat} {N : SoftNode}
    {q : String} (h : q ∈ preds (strictYieldsIn regs ns (f + 1) N)) :
    (N.mode = .strict ∧ q ∈ preds (liveStrictIn regs N)) ∨
      ∃ C ∈ childrenIn ns N, q ∈ preds (strictYieldsIn regs ns f C) := by
  simp only [strictYieldsIn, preds, List.mem_append, mem_preds_anyF, List.mem_map] at h
  rcases h with h | ⟨_, ⟨C, hC, rfl⟩, h⟩
  · split at h
    · exact Or.inl ⟨‹_›, h⟩
    · simp [preds] at h
  · exact Or.inr ⟨C, hC, h⟩

theorem preds_strictYields_live {regs : List VE.Norms.Regulated} {ns : List SoftNode} (f : Nat) {N : SoftNode}
    (hs : N.mode = .strict) {q : String} (h : q ∈ preds (liveStrictIn regs N)) :
    q ∈ preds (strictYieldsIn regs ns f N) := by
  cases f <;> simp [strictYieldsIn, preds, hs, h]

theorem preds_strictYields_child {regs : List VE.Norms.Regulated} {ns : List SoftNode} (f : Nat) {N C : SoftNode}
    (hC : C ∈ childrenIn ns N) {q : String} (h : q ∈ preds (strictYieldsIn regs ns f C)) :
    q ∈ preds (strictYieldsIn regs ns (f + 1) N) := by
  simp only [strictYieldsIn, preds, List.mem_append, mem_preds_anyF, List.mem_map]
  exact Or.inr ⟨_, ⟨C, hC, rfl⟩, h⟩

include hh hLo in
theorem preds_strictYields_fmap : ∀ (f f' : Nat), f ≤ f' → ∀ N ∈ (choiceDoc D c).1.soft.T.nodes, ∀ q,
    q ∈ preds (strictYieldsIn (choiceDoc D c).1.soft.T.regulated ((choiceDoc D c).1.soft.T.nodes.map coreNode) f
      (coreNode N)) → L q →
    q ∈ preds (strictYieldsIn (sup D).1.soft.T.regulated ((sup D).1.soft.T.nodes.map coreNode) f'
      (coreNode (fmap D c N)))
  | 0, f', _, N, hN, q, h, hL => by
    simp only [strictYieldsIn, preds, List.mem_append, mem_preds_anyF, List.not_mem_nil, false_and,
      exists_false, or_false] at h
    split at h
    · rename_i hs
      have hl := preds_live_fmap hh hLo true hN (by simpa using h) hL
      refine preds_strictYields_live f' ?_ (by simpa using hl)
      rw [(coreNode_fields _).2.2.2.1, (fmap_fields hh c hN).2.2.1]; exact hs
    · simp [preds] at h
  | f + 1, f', hle, N, hN, q, h, hL => by
    obtain ⟨g, rfl⟩ : ∃ g, f' = g + 1 := ⟨f' - 1, by omega⟩
    rcases mem_preds_strictYields h with ⟨hs, h⟩ | ⟨C, hC, h⟩
    · have hl := preds_live_fmap hh hLo true hN (by simpa using h) hL
      refine preds_strictYields_live _ ?_ (by simpa using hl)
      rw [(coreNode_fields _).2.2.2.1, (fmap_fields hh c hN).2.2.1]; exact hs
    · obtain ⟨C₀, hC₀, rfl, hfc⟩ := core_child_fwd hh hN hC
      exact preds_strictYields_child g hfc
        (preds_strictYields_fmap f g (by omega) C₀ hC₀ q h hL)

include hh in
theorem nodes_length_le : ((choiceDoc D c).1.soft.T.nodes.map coreNode).length ≤
    ((sup D).1.soft.T.nodes.map coreNode).length := by
  simpa [VE.SoftNorms.fuel] using choice_fuel_le hh c

include hh hLo in
theorem preds_strictDecides_fmap (p : String) (sign : Bool) {q : String}
    (h : q ∈ preds (strictDecidesF (choiceDoc D c).1.soft p sign)) (hL : L q) :
    q ∈ preds (strictDecidesF (sup D).1.soft p sign) := by
  simp only [strictDecidesF, strictDecidesIn, mem_preds_anyF, List.mem_map, List.mem_filter, beq_iff_eq] at h ⊢
  obtain ⟨_, ⟨M, ⟨⟨hM, hp⟩, hsg⟩, rfl⟩, h⟩ := h
  obtain ⟨M₀, hM₀, rfl⟩ := hM
  obtain ⟨hfp, hfs, hfm, _⟩ := fmap_fields hh c hM₀
  refine ⟨_, ⟨coreNode (fmap D c M₀), ⟨⟨⟨_, fmap_mem hh c hM₀, rfl⟩, by
    simpa [coreNode, hfp] using hp⟩, by simpa [coreNode, hfs] using hsg⟩, rfl⟩, ?_⟩
  unfold strictSelectsIn at h ⊢
  split at h
  · rename_i hs
    rw [if_pos (by simpa [coreNode, hfm] using hs)]
    simp only [preds, List.mem_append, mem_preds_anyF, List.mem_map] at h ⊢
    rcases h with h | ⟨_, ⟨C, hC, rfl⟩, h⟩
    · exact Or.inl (by simpa using preds_live_fmap hh hLo true hM₀ (by simpa using h) hL)
    · obtain ⟨C₀, hC₀, rfl, hfc⟩ := core_child_fwd hh hM₀ hC
      exact Or.inr ⟨_, ⟨_, hfc, rfl⟩, preds_strictYields_fmap hh hLo _ _ (nodes_length_le hh) C₀ hC₀ q h hL⟩
  · simp [preds] at h

include hh hLo in
theorem preds_blocked_fmap {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) {q : String}
    (h : q ∈ preds (blockedF (choiceDoc D c).1.soft N)) (hL : L q) :
    q ∈ preds (blockedF (sup D).1.soft (fmap D c N)) := by
  obtain ⟨hfp, hfs, _⟩ := fmap_fields hh c hN
  have hdp := dualPerm_eq (D := D) c
  have hdo : VE.SoftNorms.dualOblig (sup D).1.soft = VE.SoftNorms.dualOblig (choiceDoc D c).1.soft := by
    funext r
    simp only [VE.SoftNorms.dualOblig, VE.SoftNorms.SoftDoc.base, VE.Norms.pairs, regs_eq c]
  have key : ∀ p sign, q ∈ preds (strictDecidesF (choiceDoc D c).1.soft p sign) →
      q ∈ preds (strictDecidesF (sup D).1.soft p sign) := fun p sign hq => preds_strictDecides_fmap hh hLo p sign hq hL
  simp only [blockedF, hfp, hfs, hdp, hdo] at h ⊢
  cases hsg : N.sign <;> simp only [hsg, if_true, Bool.false_eq_true, if_false] at h ⊢
  · cases hd : VE.SoftNorms.dualOblig (choiceDoc D c).1.soft N.pred <;>
      simp only [hd, preds, List.mem_append, List.not_mem_nil, or_false, VE.SoftNorms.strictPos,
        VE.SoftNorms.strictNeg] at h ⊢
    · rcases h with h | h
      · exact Or.inl (key _ _ h)
      · exact Or.inr (key _ _ h)
    · rcases h with (h | h) | h
      · exact Or.inl (Or.inl (key _ _ h))
      · exact Or.inl (Or.inr (key _ _ h))
      · exact Or.inr (key _ _ h)
  · cases hd : VE.SoftNorms.dualPerm (choiceDoc D c).1.soft N.pred <;>
      simp only [hd, preds, List.mem_append, List.not_mem_nil, or_false, VE.SoftNorms.strictPos,
        VE.SoftNorms.strictNeg] at h ⊢
    · rcases h with h | h
      · exact Or.inl (key _ _ h)
      · exact Or.inr (key _ _ h)
    · rcases h with (h | h) | h
      · exact Or.inl (Or.inl (key _ _ h))
      · exact Or.inl (Or.inr (key _ _ h))
      · exact Or.inr (key _ _ h)

include hh hLe hLo in
theorem preds_eligible_fmap {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) {q : String}
    (h : q ∈ preds (eligibleF (choiceDoc D c).1.soft N)) (hL : L q) :
    q ∈ preds (eligibleF (sup D).1.soft (fmap D c N)) := by
  obtain ⟨_, _, hfm, _⟩ := fmap_fields hh c hN
  unfold eligibleF at h ⊢
  split at h
  · rename_i hd
    rw [if_pos (by rw [hfm]; exact hd)]
    simp only [liveF, preds, List.mem_append, if_pos hd, if_pos (show (fmap D c N).mode = .default by
      rw [hfm]; exact hd)] at h ⊢
    rcases h with (h | h) | h
    · exact Or.inl (Or.inl (by simpa using preds_live_fmap hh hLo false hN (by simpa using h) hL))
    · exfalso
      have := VE.SoftNorms.mem_preds_atom h
      subst this
      exact hLe N hN hd hL
    · exact Or.inr (preds_blocked_fmap hh hLo hN h hL)
  · simp [preds] at h

include hh in
/-- Dominance, read through `fmap`, given the opponents' effectiveness read through `fmap`. -/
theorem preds_domWith_fmap (eff eff' : SoftNode → VE.Formula)
    (heff : ∀ M ∈ (choiceDoc D c).1.soft.T.nodes, ∀ q, q ∈ preds (eff M) → L q → q ∈ preds (eff' (fmap D c M)))
    {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) {q : String}
    (h : q ∈ preds (domWith (choiceDoc D c).1.soft eff N)) (hL : L q)
    (helig : ∀ M ∈ (choiceDoc D c).1.soft.T.nodes, q ∈ preds (eligibleF (choiceDoc D c).1.soft M) →
      q ∈ preds (eligibleF (sup D).1.soft (fmap D c M))) :
    q ∈ preds (domWith (sup D).1.soft eff' (fmap D c N)) := by
  simp only [domWith, mem_preds_anyF, List.mem_map] at h ⊢
  obtain ⟨_, ⟨M, hM, rfl⟩, h⟩ := h
  simp only [opponents, List.mem_filter, Bool.and_eq_true, beq_iff_eq] at hM
  obtain ⟨hMm, ⟨hinc, hmd⟩, hcmp⟩ := hM
  obtain ⟨hMp, hMs, hMm', hMr, _⟩ := fmap_fields hh c hMm
  obtain ⟨hNp, hNs, _, hNr, _⟩ := fmap_fields hh c hN
  have hsoft := soft_eq (D := D) c
  have hdp := dualPerm_eq (D := D) c
  have hinc' : VE.SoftNorms.Incompatible (sup D).1.soft (fmap D c M) (fmap D c N) =
      VE.SoftNorms.Incompatible (choiceDoc D c).1.soft M N := by
    simp only [VE.SoftNorms.Incompatible, hMp, hNp, hMs, hNs, hdp]
  have hhi : ∀ A B : SoftNode, A ∈ (choiceDoc D c).1.soft.T.nodes → B ∈ (choiceDoc D c).1.soft.T.nodes →
      VE.SoftNorms.higher (sup D).1.soft (fmap D c A) (fmap D c B) =
        VE.SoftNorms.higher (choiceDoc D c).1.soft A B := by
    intro A B hA hB
    simp only [VE.SoftNorms.higher, (fmap_fields hh c hA).2.2.2.1, (fmap_fields hh c hB).2.2.2.1, hsoft]
  have hact : VE.SoftNorms.act (sup D).1.soft (fmap D c N) = VE.SoftNorms.act (choiceDoc D c).1.soft N := by
    simp only [VE.SoftNorms.act, VE.SoftNorms.actKey, hNp, hdp]
  have hrk : ∀ A, A ∈ (choiceDoc D c).1.soft.T.nodes → VE.SoftNorms.rk (fmap D c A) = VE.SoftNorms.rk A := by
    intro A hA; simp only [VE.SoftNorms.rk, (fmap_fields hh c hA).2.2.2.1]
  have how : ∀ a L H, outweighsF (sup D).1.soft a L H = outweighsF (choiceDoc D c).1.soft a L H := by
    intro a L H
    simp only [outweighsF, VE.SoftNorms.actSortsOf, VE.SoftNorms.sortsOf, regs_eq c]
  refine ⟨_, ⟨fmap D c M, ?_, rfl⟩, ?_⟩
  · simp only [opponents, List.mem_filter, Bool.and_eq_true, beq_iff_eq]
    refine ⟨fmap_mem hh c hMm, ⟨by rw [hinc']; exact hinc, by rw [hMm']; exact hmd⟩, ?_⟩
    simp only [VE.SoftNorms.Comparable, hhi M N hMm hN, hhi N M hN hMm]; exact hcmp
  · simp only [preds, List.mem_append, hhi M N hMm hN, hhi N M hN hMm, hact, hrk M hMm, hrk N hN, how,
      hsoft] at h ⊢
    rcases h with h | h
    · left
      split at h
      · rename_i hhm
        rw [if_pos hhm]
        simp only [preds, List.mem_append] at h ⊢
        rcases h with h | h
        · exact Or.inl (heff M hMm q h hL)
        · exact Or.inr h
      · rename_i hhm
        rw [if_neg hhm]; exact h
    · right
      split at h
      · rename_i hhm
        rw [if_pos hhm]
        simp only [preds, List.mem_append] at h ⊢
        rcases h with h | h
        · exact Or.inl (helig M hMm h)
        · exact Or.inr h
      · rename_i hhm
        rw [if_neg hhm]; exact h

include hh hLe hLo in
theorem preds_effF_fmap : ∀ (g : Nat) (N : SoftNode), N ∈ (choiceDoc D c).1.soft.T.nodes → ∀ q,
    q ∈ preds (effF (choiceDoc D c).1.soft g N) → L q → q ∈ preds (effF (sup D).1.soft g (fmap D c N))
  | 0, N, hN, q, h, hL => preds_eligible_fmap hh hLe hLo hN h hL
  | g + 1, N, hN, q, h, hL => by
    simp only [effF, preds, List.mem_append] at h ⊢
    rcases h with h | h
    · exact Or.inl (preds_eligible_fmap hh hLe hLo hN h hL)
    · exact Or.inr (preds_domWith_fmap hh _ _ (fun M hM q' hq' hL' => preds_effF_fmap g M hM q' hq' hL') hN h hL
        (fun M hM hq' => preds_eligible_fmap hh hLe hLo hM hq' hL))

include hh hLe hLo in
/-- Every layer symbol the derived carve-out of a rule of the choice's document reads, its image's reads. -/
theorem preds_derived_fmap {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) {q : String}
    (h : q ∈ preds (derived (choiceDoc D c).1.soft N)) (hL : L q) :
    q ∈ preds (derived (sup D).1.soft (fmap D c N)) := by
  obtain ⟨_, _, hfm, _, halt, _⟩ := fmap_fields hh c hN
  have hsw : ∀ q ∈ preds (switchF (choiceDoc D c).1.soft N), ¬ L q := by
    intro q hq hLq
    simp only [switchF, switchIn, mem_preds_anyF, List.mem_map] at hq
    obtain ⟨_, ⟨π, hπ, rfl⟩, hq⟩ := hq
    rw [VE.SoftNorms.mem_preds_atom hq] at hLq
    exact hLo N hN π hπ hLq
  unfold derived at h ⊢
  rw [hfm]
  cases hm : N.mode with
  | strict => rw [hm] at h; exact absurd hL (hsw q h)
  | default =>
    rw [hm] at h
    simp only [preds, List.mem_append] at h ⊢
    rcases h with ((h | h) | h) | h
    · exfalso
      have := VE.SoftNorms.mem_preds_atom h
      subst this
      exact hLe N hN hm hL
    · exact absurd hL (hsw q h)
    · exact Or.inl (Or.inr (preds_blocked_fmap hh hLo hN h hL))
    · right
      simp only [VE.SoftNorms.dominatedF, soft_eq (D := D) c] at h ⊢
      exact preds_domWith_fmap hh _ _ (fun M hM q' hq' hL' => preds_effF_fmap hh hLe hLo _ M hM q' hq' hL') hN h hL
        (fun M hM hq' => preds_eligible_fmap hh hLe hLo hM hq' hL)

end Strat

theorem stratum_names (T : VE.Norms.Tree) :
    nodeNames (VE.Norms.stratumNodes T) = T.regulated.map (·.name) ++ T.definitions.map (·.name) := by
  simp [nodeNames, VE.Norms.stratumNodes, List.map_append, List.map_map, Function.comp_def]

theorem defs_eq {D : Doc} (c : Choice) :
    (sup D).1.soft.T.definitions = (choiceDoc D c).1.soft.T.definitions :=
  (sup_shape D).definitions.trans (build_shape D (fun _ => true) (pickC c)).definitions.symm

section StratOrder
variable {D : Doc} (hh : Hyps D) {c : Choice} (hc : Compatible D c)
include hh hc

omit hc in
theorem free_wfSoft : WellFormedSoft (free D).1.soft = true :=
  build_soft_wf D hh.chain _ _ (wellFormedDoc_parts hh.wf).2.2.2.2.1

omit hc in
/-- A name the frame does not declare, beginning `soft__`, is no layer symbol. -/
theorem not_layer_name {x : String} (hfr : D.frame.soft.E.predicates x = none) (hs : x.startsWith "soft__" = true) :
    x ∉ nodeNames (VE.Norms.stratumNodes (soften (sup D).1.soft).T) := by
  rw [stratum_names]
  intro hx
  rcases List.mem_append.mp hx with hx | hx
  · obtain ⟨r, hr, rfl⟩ := List.mem_map.mp hx
    have hv := VE.SoftNorms.softValid_of_wellFormed _ (free_wfSoft hh)
    have hfs := build_shape D (fun u => (attached D u).isEmpty) (fun _ => none)
    have hr' : r ∈ (free D).1.soft.T.regulated := by
      rw [show (free D).1.soft.T.regulated = D.frame.soft.T.regulated from hfs.regulated, ← sup_reg]; exact hr
    have := hv.regDecl r hr'
    rw [show (free D).1.soft.E = D.frame.soft.E from hfs.E, hfr] at this
    cases this
  · obtain ⟨d, hd, rfl⟩ := List.mem_map.mp hx
    have := checkSoft_defs _ (wellFormedSoft_check _ (sup_wfSoft hh)) d hd
    unfold VE.SoftNorms.reservedPredicate at this
    rw [hs] at this; cases this

theorem stratum_edge {a b : String}
    (h : DepEdge (VE.Norms.stratumNodes (soften (choiceDoc D c).1.soft).T) a b) :
    DepEdge (VE.Norms.stratumNodes (soften (sup D).1.soft).T) a b := by
  obtain ⟨n, hn, hna, hb⟩ := h
  simp only [deps, List.mem_filter, List.contains_iff_mem] at hb
  obtain ⟨hbm, hbn⟩ := hb
  have hnames : nodeNames (VE.Norms.stratumNodes (soften (choiceDoc D c).1.soft).T) =
      nodeNames (VE.Norms.stratumNodes (soften (sup D).1.soft).T) := by
    rw [stratum_names, stratum_names]
    simp only [soften, regs_eq c, defs_eq c]
  rw [hnames] at hbn
  have hLe : ∀ N ∈ (choiceDoc D c).1.soft.T.nodes, N.mode = .default →
      ¬ (VE.SoftNorms.exceptedName N ∈ nodeNames (VE.Norms.stratumNodes (soften (sup D).1.soft).T)) :=
    fun N hN hd => not_layer_name hh ((choice_nodeFacts hh c hN).2.2.1 hd) (exceptedName_soft N)
  have hLo : ∀ N ∈ (choiceDoc D c).1.soft.T.nodes, ∀ π ∈ N.alterable,
      ¬ (VE.SoftNorms.offName N π ∈ nodeNames (VE.Norms.stratumNodes (soften (sup D).1.soft).T)) :=
    fun N hN π hπ => not_layer_name hh ((choice_nodeFacts hh c hN).2.2.2.1 π hπ) (offName_soft N π)
  simp only [VE.Norms.stratumNodes, List.mem_append, List.mem_map] at hn
  rcases hn with ⟨r, hr, rfl⟩ | ⟨d, hd, rfl⟩
  · simp only at hna hbm
    subst hna
    refine ⟨⟨r.name, ((VE.Norms.Sym.reg r).formulas (soften (sup D).1.soft).T).flatMap preds⟩, ?_, rfl, ?_⟩
    · simp only [VE.Norms.stratumNodes, List.mem_append, List.mem_map]
      exact Or.inl ⟨r, by simp only [soften, regs_eq c]; exact hr, rfl⟩
    simp only [deps, List.mem_filter, List.contains_iff_mem]
    refine ⟨?_, hbn⟩
    simp only [VE.Norms.Sym.formulas, List.mem_flatMap, VE.Norms.rulesOn, List.mem_filter, beq_iff_eq] at hbm ⊢
    obtain ⟨φ, ⟨N', ⟨hN', hp⟩, hφ⟩, hbφ⟩ := hbm
    rw [soften_nodes, List.mem_map] at hN'
    obtain ⟨N, hN, rfl⟩ := hN'
    have hfN := fmap_mem hh c hN
    obtain ⟨hfp, _, hfm, _, halt, hcarve⟩ := fmap_fields hh c hN
    have hfrule : VE.SoftNorms.primeNode (sup D).1.soft (fmap D c N) ∈ (soften (sup D).1.soft).T.nodes ∧
        (VE.SoftNorms.primeNode (sup D).1.soft (fmap D c N)).pred = r.name :=
      ⟨by rw [soften_nodes]; exact List.mem_map.mpr ⟨_, hfN, rfl⟩, by simpa [VE.SoftNorms.primeNode, hfp] using hp⟩
    simp only [VE.SoftNorms.primeNode, List.mem_cons, List.mem_append] at hφ
    rcases hφ with rfl | hφ | hφ
    · exact ⟨_, ⟨_, hfrule, List.mem_cons_self⟩, fmap_guard_preds hh hN b hbφ⟩
    · exact ⟨φ, ⟨_, hfrule, List.mem_cons_of_mem _ (List.mem_append_left _ (by
        simp only [VE.SoftNorms.primeNode, hcarve]; exact hφ))⟩, hbφ⟩
    · simp only [derivedList] at hφ
      split at hφ
      · cases hφ
      · rename_i hcond
        simp only [List.mem_singleton] at hφ; subst hφ
        refine ⟨_, ⟨_, hfrule, List.mem_cons_of_mem _ (List.mem_append_right _ ?_)⟩,
          preds_derived_fmap hh hLe hLo hN hbφ hbn⟩
        simp only [VE.SoftNorms.primeNode, derivedList, hfm, halt]
        rw [if_neg hcond]; simp
  · simp only at hna hbm
    subst hna
    refine ⟨⟨d.name, preds d.body⟩, ?_, rfl, ?_⟩
    · simp only [VE.Norms.stratumNodes, List.mem_append, List.mem_map]
      exact Or.inr ⟨d, by simp only [soften, defs_eq c]; exact hd, rfl⟩
    simp only [deps, List.mem_filter, List.contains_iff_mem]
    exact ⟨hbm, hbn⟩

theorem choice_stratum_acyclic : DagAcyclic (VE.Norms.stratumNodes (soften (choiceDoc D c).1.soft).T) := by
  have hX := VE.SoftNorms.softValid_of_wellFormed _ (sup_wfSoft hh)
  exact dagAcyclic_of_map id (fun a b he => DepPath.edge (stratum_edge hh hc he))
    (VE.Norms.precedence_acyclic _ hX.wf).2

theorem choice_stratum_order : ∃ o, VE.Route.dependencyOrder (VE.Norms.stratumNodes (soften (choiceDoc D c).1.soft).T) = .ok o := by
  have hX := VE.SoftNorms.softValid_of_wellFormed _ (sup_wfSoft hh)
  obtain ⟨o, ho⟩ := (VE.Norms.valid_of_wellFormed _ hX.wf).stratum
  have hn := names_nodup_of_order ho
  have hnames : nodeNames (VE.Norms.stratumNodes (soften (choiceDoc D c).1.soft).T) =
      nodeNames (VE.Norms.stratumNodes (soften (sup D).1.soft).T) := by
    rw [stratum_names, stratum_names]
    simp only [soften, regs_eq c, defs_eq c]
  exact VE.NormDefaults.dependencyOrder_ok _ (by rw [hnames]; exact hn) (choice_stratum_acyclic hh hc)

end StratOrder

end VE.Readings
