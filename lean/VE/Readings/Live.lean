import VE.Readings.Children

/-! Liveness corresponds, through the name map (docs/spec/composition-s2.md 1.7; the `live`, `dead` and
`outweighs` conditions of `Sim`).

On a document without rights material the generated keys are the exception keys of its default rules, the switch
keys of its alterable rules and the outweighs keys of its comparable colliding pairs (`genKeys_soft`). `nameMap`
sends a predicate of the frame to itself, the decision predicates of a rule of a choice's document to those of its
image, and an outweighs predicate to itself; the pulled structure reads them so, and a rule is live in the
superposed document exactly when its preimage is live in the choice's document. -/
namespace VE.Readings
open VE.SoftNorms (SoftNode SoftDoc soften exceptedName offName outweighsName)
open VE.Rights (RightsDoc correlate)
open VE.Compose (Content)
universe u

theorem noRights_parts {X : RightsDoc} (h : noRights X = true) :
    X.rs = [] ∧ X.limits = [] ∧ X.bars = [] ∧ VE.Rights.sourceLines X = [] := by
  simp only [noRights, Bool.and_eq_true, List.isEmpty_iff] at h
  exact ⟨h.1.1.1, h.1.1.2, h.1.2, h.2⟩

theorem genKeys_soft {X : RightsDoc} (h : noRights X = true) (g : GenKey × String × List String)
    (hg : g ∈ genKeys X) :
    (∃ N ∈ X.soft.T.nodes, N.mode = .default ∧ g.1 = .excepted N.name none ∧ g.2.1 = exceptedName N) ∨
    (∃ N ∈ X.soft.T.nodes, ∃ π ∈ N.alterable, g.1 = .off N.name none π ∧ g.2.1 = offName N π) ∨
    (∃ a L H, g.1 = .outweighs a L H ∧ g.2.1 = outweighsName a L H) := by
  obtain ⟨_, hl, hb, hs⟩ := noRights_parts h
  have hlines : VE.Rights.linesOf X = [] := by simp [VE.Rights.linesOf, hs, VE.Rights.linesAux]
  have hk : keyedNodes X = X.soft.T.nodes.map (fun N => (N, N.name, none)) := by
    simp [keyedNodes, hlines, VE.Rights.barNodes_nil X hb]
  simp only [genKeys, hk, VE.Rights.limKeys_nil X hl, VE.Rights.condKeys_nil X hl, hb, List.mem_append,
    List.mem_map, List.mem_filter, List.mem_flatMap, List.map_nil, List.not_mem_nil, if_true, or_false] at hg
  rcases hg with ((⟨⟨N, n, b⟩, ⟨⟨M, hM, he⟩, hmode⟩, rfl⟩ | ⟨⟨N, n, b⟩, ⟨M, hM, he⟩, π, hπ, rfl⟩) |
    ⟨x, _, rfl⟩)
  · simp only [Prod.mk.injEq] at he
    obtain ⟨rfl, rfl, rfl⟩ := he
    exact Or.inl ⟨M, hM, by simpa using hmode, rfl, rfl⟩
  · simp only [Prod.mk.injEq] at he
    obtain ⟨rfl, rfl, rfl⟩ := he
    exact Or.inr (Or.inl ⟨M, hM, π, hπ, rfl, rfl⟩)
  · exact Or.inr (Or.inr ⟨_, _, _, rfl, rfl⟩)

theorem excepted_key_mem {X : RightsDoc} (h : noRights X = true) {N : SoftNode} (hN : N ∈ X.soft.T.nodes)
    (hd : N.mode = .default) :
    ∃ g ∈ genKeys X, g.1 = .excepted N.name none ∧ g.2.1 = exceptedName N := by
  obtain ⟨_, _, hb, hs⟩ := noRights_parts h
  have hlines : VE.Rights.linesOf X = [] := by simp [VE.Rights.linesOf, hs, VE.Rights.linesAux]
  have hk : keyedNodes X = X.soft.T.nodes.map (fun N => (N, N.name, none)) := by
    simp [keyedNodes, hlines, VE.Rights.barNodes_nil X hb]
  refine ⟨(GenKey.excepted N.name none, exceptedName N, VE.SoftNorms.sortsOf (correlate X) N.pred), ?_, rfl, rfl⟩
  simp only [genKeys, hk, List.mem_append]
  refine Or.inl (Or.inl (Or.inl (Or.inl (Or.inl ?_))))
  exact List.mem_map.mpr ⟨(N, N.name, none), List.mem_filter.mpr ⟨List.mem_map.mpr ⟨N, hN, rfl⟩, by simp [hd]⟩, rfl⟩

theorem off_key_mem {X : RightsDoc} (h : noRights X = true) {N : SoftNode} (hN : N ∈ X.soft.T.nodes)
    {π : String} (hπ : π ∈ N.alterable) :
    ∃ g ∈ genKeys X, g.1 = .off N.name none π ∧ g.2.1 = offName N π := by
  obtain ⟨_, _, hb, hs⟩ := noRights_parts h
  have hlines : VE.Rights.linesOf X = [] := by simp [VE.Rights.linesOf, hs, VE.Rights.linesAux]
  have hk : keyedNodes X = X.soft.T.nodes.map (fun N => (N, N.name, none)) := by
    simp [keyedNodes, hlines, VE.Rights.barNodes_nil X hb]
  refine ⟨(GenKey.off N.name none π, offName N π, VE.SoftNorms.sortsOf (correlate X) N.pred), ?_, rfl, rfl⟩
  simp only [genKeys, hk, List.mem_append]
  refine Or.inl (Or.inl (Or.inl (Or.inl (Or.inr ?_))))
  exact List.mem_flatMap.mpr ⟨(N, N.name, none), List.mem_map.mpr ⟨N, hN, rfl⟩, List.mem_map.mpr ⟨π, hπ, rfl⟩⟩

/-! ## The name map -/

theorem choice_nodeFacts {D : Doc} (hh : Hyps D) (c : Choice) {N : SoftNode}
    (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) :
    VE.Norms.ruleName N.name = true ∧
    (∀ φ ∈ N.guard :: N.carveOuts,
      φ.WellFormed D.frame.soft.E (VE.SoftNorms.sortsIn D.frame.soft.T.regulated N.pred).reverse) ∧
    (N.mode = .default → D.frame.soft.E.predicates (exceptedName N) = none) ∧
    (∀ π ∈ N.alterable, D.frame.soft.E.predicates (offName N π) = none) ∧
    (∀ π ∈ N.alterable, VE.SoftNorms.validSoftName π = true) := by
  obtain ⟨keep, pick, _, hw, hm⟩ := choice_home hh c hN
  have hs := build_shape D keep pick
  obtain ⟨h1, h2, h3, h4, h5, _⟩ := nodeFacts_of_home D hh.chain _ hw hs.E hs.regulated N hm
  exact ⟨h1, h2, h3, h4, h5⟩

theorem sup_softValid {D : Doc} (hh : Hyps D) : VE.SoftNorms.SoftValid (sup D).1.soft := by
  have h := (sup_wellFormed D hh.sp).2
  rw [(correlate_noRights _ hh.noRights).1] at h
  exact VE.SoftNorms.softValid_of_wellFormed _ h

/-- The rule of `sup D` with a given name. -/
theorem sup_name_inj {D : Doc} (hh : Hyps D) {M M' : SoftNode} (hM : M ∈ (sup D).1.soft.T.nodes)
    (hM' : M' ∈ (sup D).1.soft.T.nodes) (he : M.name = M'.name) : M = M' :=
  inj_of_nodup_map (sup_softValid hh).names hM hM' he

theorem nameMap_excepted {D : Doc} (hh : Hyps D) (c : Choice) {N : SoftNode}
    (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) (hd : N.mode = .default) :
    nameMap D c (exceptedName N) = exceptedName (fmap D c N) := by
  have hY := choiceDoc_noRights D c hh.noRights
  have hX := hh.noRights
  unfold nameMap
  cases hf : (genKeys (choiceDoc D c).1).find? (·.2.1 == exceptedName N) with
  | none =>
    obtain ⟨g0, hg0, _, hn0⟩ := excepted_key_mem hY hN hd
    exact absurd (by simpa using hn0) (List.find?_eq_none.mp hf g0 hg0)
  | some g =>
    have hgm := List.mem_of_find?_eq_some hf
    have hgn : g.2.1 = exceptedName N := by simpa using List.find?_some hf
    have hk : g.1 = .excepted N.name none := by
      rcases genKeys_soft hY g hgm with ⟨M, hM, _, hk, hn⟩ | ⟨M, hM, π, _, _, hn⟩ | ⟨a, L, H, _, hn⟩
      · rw [hk, exceptedName_inj (choice_nodeFacts hh c hM).1 (choice_nodeFacts hh c hN).1 (hn.symm.trans hgn)]
      · exact absurd (hn.symm.trans hgn).symm (exceptedName_ne_offName N M π)
      · exact absurd (hn.symm.trans hgn).symm (exceptedName_ne_outweighsName N a L H)
    simp only [hk, qualifyKey]
    have hfX := fmap_mem hh c hN
    have hdX : (fmap D c N).mode = .default := by rw [(fmap_fields hh c hN).2.2.1]; exact hd
    cases hf' : (genKeys (sup D).1).find? (·.1 == .excepted (qName D c N.name) none) with
    | none =>
      obtain ⟨g0, hg0, hk0, _⟩ := excepted_key_mem hX hfX hdX
      rw [fmap_name hh c hN] at hk0
      exact absurd (by simpa using hk0) (List.find?_eq_none.mp hf' g0 hg0)
    | some g' =>
      have hgm' := List.mem_of_find?_eq_some hf'
      have hgk : g'.1 = .excepted (qName D c N.name) none := by simpa using List.find?_some hf'
      simp only [Option.map_some, Option.getD_some]
      rcases genKeys_soft hX g' hgm' with ⟨M, hM, _, hk', hn⟩ | ⟨M, hM, π, _, hk', _⟩ | ⟨a, L, H, hk', _⟩
      · rw [hk'] at hgk
        simp only [GenKey.excepted.injEq, and_true] at hgk
        rw [hn, sup_name_inj hh hM hfX (by rw [hgk, fmap_name hh c hN])]
      · rw [hk'] at hgk; cases hgk
      · rw [hk'] at hgk; cases hgk

theorem nameMap_off {D : Doc} (hh : Hyps D) (c : Choice) {N : SoftNode}
    (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) {π : String} (hπ : π ∈ N.alterable) :
    nameMap D c (offName N π) = offName (fmap D c N) π := by
  have hY := choiceDoc_noRights D c hh.noRights
  have hX := hh.noRights
  unfold nameMap
  cases hf : (genKeys (choiceDoc D c).1).find? (·.2.1 == offName N π) with
  | none =>
    obtain ⟨g0, hg0, _, hn0⟩ := off_key_mem hY hN hπ
    exact absurd (by simpa using hn0) (List.find?_eq_none.mp hf g0 hg0)
  | some g =>
    have hgm := List.mem_of_find?_eq_some hf
    have hgn : g.2.1 = offName N π := by simpa using List.find?_some hf
    have hk : g.1 = .off N.name none π := by
      rcases genKeys_soft hY g hgm with ⟨M, hM, _, _, hn⟩ | ⟨M, hM, π', hπ', hk, hn⟩ | ⟨a, L, H, _, hn⟩
      · exact absurd (hn.symm.trans hgn) (exceptedName_ne_offName M N π)
      · obtain ⟨h1, h2⟩ := offName_inj (choice_nodeFacts hh c hM).1 (choice_nodeFacts hh c hN).1
          ((choice_nodeFacts hh c hM).2.2.2.2 π' hπ') ((choice_nodeFacts hh c hN).2.2.2.2 π hπ) (hn.symm.trans hgn)
        rw [hk, h1, h2]
      · exact absurd (hn.symm.trans hgn).symm (offName_ne_outweighsName N π a L H)
    simp only [hk, qualifyKey]
    have hfX := fmap_mem hh c hN
    have hπX : π ∈ (fmap D c N).alterable := by rw [(fmap_fields hh c hN).2.2.2.2.1]; exact hπ
    cases hf' : (genKeys (sup D).1).find? (·.1 == .off (qName D c N.name) none π) with
    | none =>
      obtain ⟨g0, hg0, hk0, _⟩ := off_key_mem hX hfX hπX
      rw [fmap_name hh c hN] at hk0
      exact absurd (by simpa using hk0) (List.find?_eq_none.mp hf' g0 hg0)
    | some g' =>
      have hgm' := List.mem_of_find?_eq_some hf'
      have hgk : g'.1 = .off (qName D c N.name) none π := by simpa using List.find?_some hf'
      simp only [Option.map_some, Option.getD_some]
      rcases genKeys_soft hX g' hgm' with ⟨M, hM, _, hk', _⟩ | ⟨M, hM, π', _, hk', hn⟩ | ⟨a, L, H, hk', _⟩
      · rw [hk'] at hgk; cases hgk
      · rw [hk'] at hgk
        simp only [GenKey.off.injEq, true_and] at hgk
        obtain ⟨hgk1, rfl⟩ := hgk
        rw [hn, sup_name_inj hh hM hfX (by rw [hgk1, fmap_name hh c hN])]
      · rw [hk'] at hgk; cases hgk

/-- When the first key of a name is an outweighs key, the name map keeps the name. -/
theorem nameMap_of_outweighs {D : Doc} (hh : Hyps D) (c : Choice) {p : String} {g : GenKey × String × List String}
    (hf : (genKeys (choiceDoc D c).1).find? (·.2.1 == p) = some g) {a L H : String}
    (hk : g.1 = .outweighs a L H) (hn : g.2.1 = outweighsName a L H) : nameMap D c p = p := by
  have hgn : g.2.1 = p := by simpa using List.find?_some hf
  unfold nameMap
  rw [hf]
  simp only [hk, qualifyKey]
  cases hf' : (genKeys (sup D).1).find? (·.1 == .outweighs a L H) with
  | none => rfl
  | some g' =>
    have hgk : g'.1 = .outweighs a L H := by simpa using List.find?_some hf'
    simp only [Option.map_some, Option.getD_some]
    rcases genKeys_soft hh.noRights g' (List.mem_of_find?_eq_some hf') with ⟨M, _, _, hk', _⟩ |
      ⟨M, _, π, _, hk', _⟩ | ⟨a', L', H', hk', hn'⟩
    · rw [hk'] at hgk; cases hgk
    · rw [hk'] at hgk; cases hgk
    · rw [hk'] at hgk
      simp only [GenKey.outweighs.injEq] at hgk
      obtain ⟨rfl, rfl, rfl⟩ := hgk
      rw [hn', ← hn, hgn]

theorem nameMap_frame {D : Doc} (hh : Hyps D) (c : Choice) {p : String}
    (hp : D.frame.soft.E.predicates p ≠ none) : nameMap D c p = p := by
  have hY := choiceDoc_noRights D c hh.noRights
  cases hf : (genKeys (choiceDoc D c).1).find? (·.2.1 == p) with
  | none => unfold nameMap; rw [hf]
  | some g =>
    have hgm := List.mem_of_find?_eq_some hf
    have hgn : g.2.1 = p := by simpa using List.find?_some hf
    rcases genKeys_soft hY g hgm with ⟨M, hM, hd, _, hn⟩ | ⟨M, hM, π, hπ, _, hn⟩ | ⟨a, L, H, hk, hn⟩
    · exact absurd ((choice_nodeFacts hh c hM).2.2.1 hd) (by rw [← hn, hgn]; exact hp)
    · exact absurd ((choice_nodeFacts hh c hM).2.2.2.1 π hπ) (by rw [← hn, hgn]; exact hp)
    · exact nameMap_of_outweighs hh c hf hk hn

theorem nameMap_outweighs {D : Doc} (hh : Hyps D) (c : Choice) (a L H : String) :
    nameMap D c (outweighsName a L H) = outweighsName a L H := by
  have hY := choiceDoc_noRights D c hh.noRights
  cases hf : (genKeys (choiceDoc D c).1).find? (·.2.1 == outweighsName a L H) with
  | none => unfold nameMap; rw [hf]
  | some g =>
    have hgm := List.mem_of_find?_eq_some hf
    have hgn : g.2.1 = outweighsName a L H := by simpa using List.find?_some hf
    rcases genKeys_soft hY g hgm with ⟨M, _, _, _, hn⟩ | ⟨M, _, π, _, _, hn⟩ | ⟨a', L', H', hk, hn⟩
    · exact absurd (hn.symm.trans hgn) (exceptedName_ne_outweighsName M a L H)
    · exact absurd (hn.symm.trans hgn) (offName_ne_outweighsName M π a L H)
    · exact nameMap_of_outweighs hh c hf hk hn

/-! ## The pulled structure -/

theorem choice_correlate {D : Doc} (hh : Hyps D) (c : Choice) :
    correlate (choiceDoc D c).1 = (choiceDoc D c).1.soft :=
  (correlate_noRights _ (choiceDoc_noRights D c hh.noRights)).1

theorem sup_correlate {D : Doc} (hh : Hyps D) : correlate (sup D).1 = (sup D).1.soft :=
  (correlate_noRights _ hh.noRights).1

/-- The complete vocabulary of a choice's document: its decision predicates over the frame's. -/
theorem choiceEnvFull_pred {D : Doc} (hh : Hyps D) (c : Choice) (p : String) :
    (choiceEnvFull D c).predicates p =
      match (VE.SoftNorms.decisions (choiceDoc D c).1.soft).find? (·.1 == p) with
      | some d => some d.2
      | none => D.frame.soft.E.predicates p := by
  unfold choiceEnvFull
  rw [choice_correlate hh c]
  have hd : (VE.Norms.layerNames (soften (choiceDoc D c).1.soft).T).drop
      (VE.Norms.size (soften (choiceDoc D c).1.soft)) = [] := by
    simp [VE.Norms.layerNames, VE.Norms.size]
  simp only [VE.Norms.envAt, hd, VE.Norms.hide, List.not_mem_nil, if_false]
  show (VE.SoftNorms.envPrime _).predicates p = _
  have hE : (choiceDoc D c).1.soft.E = D.frame.soft.E := (build_shape D (fun _ => true) (pickC c)).E
  unfold VE.SoftNorms.envPrime
  simp only [hE]
  split <;> rename_i heq <;> simp [heq]

theorem choiceEnvFull_decision {D : Doc} (hh : Hyps D) (c : Choice) {p : String}
    (hp : p ∈ VE.SoftNorms.decisionNames (choiceDoc D c).1.soft) : (choiceEnvFull D c).predicates p ≠ none := by
  rw [choiceEnvFull_pred hh c]
  cases hf : (VE.SoftNorms.decisions (choiceDoc D c).1.soft).find? (·.1 == p) with
  | some d => simp
  | none =>
    simp only [VE.SoftNorms.decisionNames, List.mem_map] at hp
    obtain ⟨d, hd, rfl⟩ := hp
    exact absurd (by simp) (List.find?_eq_none.mp hf d hd)

theorem choiceEnvFull_frame {D : Doc} (hh : Hyps D) (c : Choice) {p : String}
    (hp : D.frame.soft.E.predicates p ≠ none) : (choiceEnvFull D c).predicates p ≠ none := by
  rw [choiceEnvFull_pred hh c]
  split <;> simp_all

theorem pull_frame {D : Doc} (hh : Hyps D) (c : Choice) (S : VE.Structure.{u}) {p : String}
    (hp : D.frame.soft.E.predicates p ≠ none) (vs : List S.Carrier) :
    (pull D c S).relation p vs ↔ S.relation p vs := by
  show ((choiceEnvFull D c).predicates p ≠ none ∧ S.relation (nameMap D c p) vs) ↔ _
  rw [nameMap_frame hh c hp]
  exact ⟨fun h => h.2, fun h => ⟨choiceEnvFull_frame hh c hp, h⟩⟩

theorem pull_excepted {D : Doc} (hh : Hyps D) (c : Choice) (S : VE.Structure.{u}) {N : SoftNode}
    (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) (hd : N.mode = .default) (vs : List S.Carrier) :
    (pull D c S).relation (exceptedName N) vs ↔ S.relation (exceptedName (fmap D c N)) vs := by
  show ((choiceEnvFull D c).predicates _ ≠ none ∧ S.relation (nameMap D c _) vs) ↔ _
  rw [nameMap_excepted hh c hN hd]
  refine ⟨fun h => h.2, fun h => ⟨choiceEnvFull_decision hh c ?_, h⟩⟩
  simp only [VE.SoftNorms.decisionNames, VE.SoftNorms.decisions, VE.SoftNorms.exceptedDecisions, List.map_append,
    List.mem_append, List.mem_map, List.mem_filter]
  exact Or.inl (Or.inl ⟨_, ⟨N, ⟨hN, by simp [hd]⟩, rfl⟩, rfl⟩)

theorem pull_off {D : Doc} (hh : Hyps D) (c : Choice) (S : VE.Structure.{u}) {N : SoftNode}
    (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) {π : String} (hπ : π ∈ N.alterable) (vs : List S.Carrier) :
    (pull D c S).relation (offName N π) vs ↔ S.relation (offName (fmap D c N) π) vs := by
  show ((choiceEnvFull D c).predicates _ ≠ none ∧ S.relation (nameMap D c _) vs) ↔ _
  rw [nameMap_off hh c hN hπ]
  refine ⟨fun h => h.2, fun h => ⟨choiceEnvFull_decision hh c ?_, h⟩⟩
  simp only [VE.SoftNorms.decisionNames, VE.SoftNorms.decisions, VE.SoftNorms.offDecisions, List.map_append,
    List.mem_append, List.mem_map, List.mem_flatMap]
  exact Or.inl (Or.inr ⟨_, ⟨N, hN, ⟨π, hπ, rfl⟩⟩, rfl⟩)

theorem pull_outweighs {D : Doc} (hh : Hyps D) (c : Choice) (S : VE.Structure.{u}) {a L H : String}
    (ht : (a, L, H) ∈ VE.SoftNorms.outweighsTriples (choiceDoc D c).1.soft) (vs : List S.Carrier) :
    (pull D c S).relation (outweighsName a L H) vs ↔ S.relation (outweighsName a L H) vs := by
  show ((choiceEnvFull D c).predicates _ ≠ none ∧ S.relation (nameMap D c _) vs) ↔ _
  rw [nameMap_outweighs hh c]
  refine ⟨fun h => h.2, fun h => ⟨choiceEnvFull_decision hh c ?_, h⟩⟩
  simp only [VE.SoftNorms.decisionNames, VE.SoftNorms.decisions, VE.SoftNorms.outweighsDecisions, List.map_append,
    List.mem_append, List.mem_map]
  exact Or.inr ⟨_, ⟨(a, L, H), ht, rfl⟩, rfl⟩

/-! ## Liveness -/

theorem atom_congr (S : VE.Structure.{u}) (R : String → List S.Carrier → Prop) (p q : String) (ss : List String)
    (h : ∀ vs, S.relation p vs ↔ R q vs) (ρ : VE.Valuation S) :
    (VE.Norms.atom p ss).denote S ρ ↔ (VE.Norms.atom q ss).denote { S with relation := R } ρ := by
  unfold VE.Norms.atom
  split
  · simp only [VE.Formula.denote, term_relation_congr]
    exact exists_congr fun v => and_congr_right fun _ => h [v]
  · simp only [VE.Formula.denote, term_relation_congr]
    exact exists_congr fun v => exists_congr fun w => and_congr_right fun _ => and_congr_right fun _ => h [v, w]
  · exact Iff.rfl

theorem pattern_rho (S : VE.Structure.{u}) (n k i : Nat) (ρ : VE.Valuation S) :
    (pattern n k i).denote S ρ ↔ (pattern n k i).denote S [] := by
  rw [pattern, conj_denote, conj_denote]
  simp only [List.mem_map, List.mem_range, forall_exists_index, and_imp, forall_apply_eq_imp_iff₂]
  apply forall_congr'; intro j; apply imp_congr_right; intro _
  unfold lit
  split <;> simp [VE.Formula.denote, here, VE.Term.denote]

/-- A formula over the frame's vocabulary reads the pulled structure as it reads the structure. -/
theorem pull_denote_frame {D : Doc} (hh : Hyps D) (c : Choice) (S : VE.Structure.{u}) (φ : VE.Formula)
    (Γ : List String) (hφ : φ.WellFormed D.frame.soft.E Γ) (ρ : VE.Valuation S) :
    φ.denote S ρ ↔ φ.denote (pull D c S) ρ := by
  apply denote_relation_congr D.frame.soft.E S _ (fun p ss hp vs _ => (pull_frame hh c S (by simp [hp]) vs).symm)
    φ Γ ρ ((VE.check_iff_wellFormed _ _ _).mpr hφ)

theorem live_corr {D : Doc} (hh : Hyps D) (c : Choice) (S : VE.Structure.{u}) (he : Encodes D c S)
    (ρ : VE.Valuation S) {N : SoftNode} (hN : N ∈ (choiceDoc D c).1.soft.T.nodes) :
    VE.SoftNorms.LiveD (sup D).1.soft S ρ (fmap D c N) ↔ VE.SoftNorms.LiveD (choiceDoc D c).1.soft (pull D c S) ρ N := by
  obtain ⟨_, htyped, _, _, _⟩ := choice_nodeFacts hh c hN
  obtain ⟨hpred, _, hmode, _, halt, hcarve⟩ := fmap_fields hh c hN
  have hregX : (sup D).1.soft.T.regulated = D.frame.soft.T.regulated := (sup_shape D).regulated
  have hregY : (choiceDoc D c).1.soft.T.regulated = D.frame.soft.T.regulated :=
    (build_shape D (fun _ => true) (pickC c)).regulated
  -- the guard
  have hguard : (fmap D c N).guard.denote S ρ ↔ N.guard.denote (pull D c S) ρ := by
    have hg := pull_denote_frame hh c S N.guard _ (htyped N.guard (by simp)) ρ
    rcases (mem_choiceNodes D c N).mp hN with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hc⟩
    · rw [fmap_frame hh c hf]; exact hg
    · rw [fmap_fixed hh c hu]; exact hg
    · rw [fmap_chosen hh c hm hi ha hc]
      show (N.guard.denote S ρ ∧ (pattern (m + 1) (setSize D m) i).denote S ρ) ↔ _
      have hilt : i < setSize D m := by rw [setSize_eq hm]; exact (List.getElem?_eq_some_iff.mp ha).1
      have hχ : (pattern (m + 1) (setSize D m) i).denote S ρ := by
        rw [pattern_rho, ← choiceAtom_eq (findIdx_of_nodup hh.nodup hm) hilt]
        exact (he _ (List.getElem_mem hm) i (by rw [← setSize_eq hm]; exact hilt)).mpr (mem_of_index hi)
      rw [← hg]
      exact ⟨fun h => h.1, fun h => ⟨h, hχ⟩⟩
  -- the carve-outs
  have hcar : (∃ U ∈ (fmap D c N).carveOuts, U.denote S ρ) ↔ (∃ U ∈ N.carveOuts, U.denote (pull D c S) ρ) := by
    rw [hcarve]
    exact exists_congr fun U => and_congr_right fun hU =>
      pull_denote_frame hh c S U _ (htyped U (List.mem_cons_of_mem _ hU)) ρ
  -- the switch
  have hsw : (VE.SoftNorms.switchF (sup D).1.soft (fmap D c N)).denote S ρ ↔
      (VE.SoftNorms.switchF (choiceDoc D c).1.soft N).denote (pull D c S) ρ := by
    simp only [VE.SoftNorms.switchF, VE.SoftNorms.switchIn, VE.Norms.anyF_denote, List.mem_map, hregX, hregY,
      halt, hpred]
    constructor
    · rintro ⟨_, ⟨π, hπ, rfl⟩, h⟩
      exact ⟨_, ⟨π, hπ, rfl⟩, (atom_congr S _ _ _ _ (fun vs => (pull_off hh c S hN hπ vs).symm) ρ).mp h⟩
    · rintro ⟨_, ⟨π, hπ, rfl⟩, h⟩
      exact ⟨_, ⟨π, hπ, rfl⟩, (atom_congr S _ _ _ _ (fun vs => (pull_off hh c S hN hπ vs).symm) ρ).mpr h⟩
  -- the exception
  have hex : N.mode = .default → ((VE.SoftNorms.exceptedF (sup D).1.soft (fmap D c N)).denote S ρ ↔
      (VE.SoftNorms.exceptedF (choiceDoc D c).1.soft N).denote (pull D c S) ρ) := by
    intro hd
    simp only [VE.SoftNorms.exceptedF, VE.SoftNorms.sortsOf, hregX, hregY, hpred]
    exact atom_congr S _ _ _ _ (fun vs => (pull_excepted hh c S hN hd vs).symm) ρ
  unfold VE.SoftNorms.LiveD
  rw [hguard, hcar, hsw, hmode]
  apply and_congr_right; intro _; apply and_congr_right; intro _; apply and_congr_right; intro _
  exact imp_congr_right fun hd => not_congr (hex hd)

end VE.Readings
