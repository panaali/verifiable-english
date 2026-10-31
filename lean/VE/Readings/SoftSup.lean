import VE.Readings.SoftVerdicts
import VE.Readings.SupExtra

/-! SC-10's first part (docs/spec/rd-9-soft-chain.md 13.1, 13.3): superposition under the soft completion.

The superposed soft document is read as norm-defaults reads a soft document (`supU N`), and `fill` runs after
`soften`, on the superposed document (D1). `fill (supU N)` is not `soften` of any superposed document, so S2a's
simulation is applied to the author rules and `fill` is added on each side: a filled tree decides as its author rules
do, or by `F_p` where the gap says yes and the author rules are silent (`decidesD_fill`). The filled pull `pullF` is
S2a's `pull` onto the filled choice's vocabulary, which keeps the `unsaid__` tables (13.4 item 3). -/
namespace VE.Readings
open VE.Norms (Regulated Sat envAt size)
open VE.NormDefaults (fill)
universe u

/-- The superposed document's extra base premises under the soft completion (D2 on `sup`). -/
def supX (N : NDoc) : List VE.Formula := softX N (sup N.D).1

/-- S2a's `pull` onto the filled choice's full vocabulary: keeps the `unsaid__` tables. -/
def pullF (N : NDoc) (c : Choice) (S : VE.Structure.{u}) : VE.Structure.{u} :=
  { S with relation := fun p vs =>
      (envAt (fill (choiceU N c)) (size (fill (choiceU N c)))).predicates p ≠ none ∧ S.relation (nameMap N.D c p) vs }

/-- The free document's filled full vocabulary: the queries' vocabulary on the superposed route (OPEN-SC10-1). -/
def sharedEnvSD (N : NDoc) : VE.Environment := envAt (fill (freeU N)) (size (fill (freeU N)))

/-- A certificate on the filled superposed document under `A`: slot, atoms, `supX`, then `Fill_T` (`premisesX`). -/
def supCertificateCheckSD (N : NDoc) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (cert : VE.Tableau.Certificate) : Bool :=
  VE.Tableau.checkCertificate (envAt (fill (supU N)) (size (fill (supU N))))
    (VE.NormDefaults.Wire.premisesX (supU N) (slotUnder N.D A ++ supX N) ((sup N.D).2 ++ Γ)) φ cert

/-! ## The filled tree of a document with only what S2a gives of a choice's document

A choice's document has no `WellFormedU`, so `fill_wellFormed` does not apply to it. What `Valid (fill U)`, the
decisions of `fill U` and `F_p`'s selection read is listed here as hypotheses (`FillLite`), each of which S2a gives
of a compatible choice's document. -/

open VE.Norms (Node Tree rulesOn SelectsD DecidesD YieldsD children fuel precedenceNodes stratumNodes Valid syms
  layerNames)
open VE.SoftNorms (SoftNode SoftDoc soften canon)
open VE.Rights (correlate)
open VE.NormDefaults (UDoc fillName fillRoot fillNode fillNodes fillEnv unsaidName)
open VE.Route (DagAcyclic DepEdge DepPath nodeNames)
open VE.NormDefaults (keyOf)

theorem envAt_size_pred (D : VE.Norms.Doc) (p : String) : (envAt D (size D)).predicates p = D.E.predicates p := by
  simp [envAt, VE.Norms.hide, size, layerNames, List.drop_of_length_le]

theorem fillEnv_ne_none (U : UDoc) {p : String} (h : U.D.E.predicates p ≠ none) : (fillEnv U).predicates p ≠ none := by
  unfold fillEnv; simp only; split <;> simp_all

/-- What the lemmas of `fill` below read of a document: no more than S2a gives of a choice's document. -/
structure FillLite (U : UDoc) : Prop where
  valid : Valid U.D
  author : AuthorLite U
  over : ∀ N ∈ U.D.T.nodes, ∀ m ∈ N.over, ∃ M ∈ U.D.T.nodes, M.name = m ∧ M.pred = N.pred
  unsaid : ∀ p ∈ U.unspec, U.D.E.predicates (unsaidName p) = none
  stratum : ∀ x ∈ nodeNames (stratumNodes U.D.T), ∀ p ∈ U.unspec, x ≠ unsaidName p
  names : ((fill U).T.nodes.map Node.name).Nodup

theorem fillLite_of_uvalid {U : UDoc} (hu : VE.NormDefaults.UValid U) : FillLite U :=
  ⟨hu.valid, authorLite_of_uvalid hu, fun _ hN _ hm => hu.over_node hN hm, hu.freshPred,
    (fun x hx p hp he => by
      obtain ⟨ss, hss⟩ := VE.NormDefaults.stratum_declared hu hx
      rw [he, hu.freshPred p hp] at hss; cases hss),
    VE.NormDefaults.fill_names_nodup hu⟩

section Lite
variable {U : UDoc} (hu : FillLite U)
include hu

theorem fill_acyclic_lite : DagAcyclic (precedenceNodes (fill U).T) := by
  have hnoout : ∀ a b, DepEdge (precedenceNodes (fill U).T) a b → a ∉ U.unspec.map fillName ∧
      (b ∈ U.unspec.map fillName ∨ DepEdge (precedenceNodes U.D.T) a b) := by
    rintro a b ⟨n, hn, rfl, hb⟩
    obtain ⟨N, hN, rfl⟩ := List.mem_map.mp hn
    rw [VE.NormDefaults.mem_deps] at hb
    obtain ⟨hbo, _⟩ := hb
    rcases VE.NormDefaults.mem_fill_nodes.mp hN with ⟨N₀, hN₀, rfl⟩ | hN
    · refine ⟨by simpa using hu.author.freshRule N₀ hN₀, ?_⟩
      rcases VE.NormDefaults.fillRoot_over U N₀ with ⟨hp, _, ho⟩ | ⟨_, he⟩
      · simp only [ho, List.mem_singleton] at hbo
        exact Or.inl (hbo ▸ List.mem_map_of_mem hp)
      · rw [he] at hbo ⊢
        obtain ⟨M, hM, rfl, _⟩ := hu.over N₀ hN₀ _ hbo
        exact Or.inr (VE.NormDefaults.over_edge hN₀ hM hbo)
    · obtain ⟨r, _, _, rfl⟩ := VE.NormDefaults.mem_fillNodes.mp hN
      simp [fillNode] at hbo
  have hpath : ∀ a c, DepPath (precedenceNodes (fill U).T) a c → a ∉ U.unspec.map fillName ∧
      (c ∈ U.unspec.map fillName ∨ DepPath (precedenceNodes U.D.T) a c) := by
    intro a c hp
    induction hp with
    | edge he =>
      obtain ⟨ha, hb⟩ := hnoout _ _ he
      exact ⟨ha, hb.imp id DepPath.edge⟩
    | trans _ _ ih₁ ih₂ =>
      obtain ⟨ha, hab⟩ := ih₁
      obtain ⟨hb, hbc⟩ := ih₂
      refine ⟨ha, ?_⟩
      rcases hab with hab | hab
      · exact absurd hab hb
      · exact hbc.imp id (DepPath.trans hab)
  intro a hp
  obtain ⟨ha, h⟩ := hpath a a hp
  rcases h with h | h
  · exact ha h
  · exact hu.author.acyclic a h

theorem fill_stratum_key_lite : keyOf (stratumNodes (fill U).T) = keyOf (stratumNodes U.D.T) := by
  have hfm : ∀ r : Regulated, List.filter (nodeNames (stratumNodes U.D.T)).contains
      ((((fillNodes U).filter (·.pred == r.name)).flatMap (fun N => N.guard :: N.carveOuts)).flatMap
        VE.Norms.preds) = [] := by
    intro r
    rw [List.filter_eq_nil_iff]
    intro x hx hc
    simp only [List.mem_flatMap, List.mem_filter] at hx
    obtain ⟨φ, ⟨F, ⟨hF, _⟩, hφ⟩, hxφ⟩ := hx
    obtain ⟨r', _, hp, rfl⟩ := VE.NormDefaults.mem_fillNodes.mp hF
    simp only [fillNode, List.not_mem_nil, or_false, List.mem_cons] at hφ
    subst hφ
    have hxu : x = unsaidName r'.name := by
      unfold VE.Norms.atom at hxφ
      split at hxφ <;> simp_all [VE.Norms.preds]
    exact hu.stratum x (by simpa using hc) r'.name hp hxu
  unfold keyOf VE.Route.deps
  rw [VE.NormDefaults.stratum_names]
  generalize nodeNames (stratumNodes U.D.T) = NN at hfm ⊢
  simp only [stratumNodes, List.map_append, List.map_map]
  congr 1
  apply List.map_congr_left
  intro r _
  simp only [Function.comp, VE.NormDefaults.formulas_fill, List.flatMap_append, List.filter_append, hfm,
    List.append_nil]

theorem syms_fill_lite : syms (fill U).T = syms U.D.T := by
  unfold syms VE.Norms.order
  rw [VE.NormDefaults.dependencyOrder_congr (fill_stratum_key_lite hu)]
  rfl

theorem layerNames_fill_lite : layerNames (fill U).T = layerNames U.D.T := by
  unfold layerNames; rw [syms_fill_lite hu]

theorem not_unsaid_lite {n : String} {ss : List String} (hn : U.D.E.predicates n = some ss) :
    n ∉ VE.NormDefaults.unsaidNames U := by
  intro h
  obtain ⟨p, hp, rfl⟩ := List.mem_map.mp h
  rw [hu.unsaid p hp] at hn; cases hn

theorem envAt_fill_mono_lite (k : Nat) (n : String) (ss : List String) (h : (envAt U.D k).predicates n = some ss) :
    (envAt (fill U) k).predicates n = some ss := by
  simp only [envAt, VE.Norms.hide, layerNames_fill_lite hu] at h ⊢
  split at h
  · cases h
  · rename_i hn
    simp only [hn, if_false, VE.NormDefaults.fill_E]
    rw [VE.NormDefaults.fillEnv_off U (not_unsaid_lite hu h), h]

theorem regulated_eq_lite {r r' : Regulated} (hr : r ∈ U.D.T.regulated) (hr' : r' ∈ U.D.T.regulated)
    (e : r.name = r'.name) : r = r' := by
  obtain ⟨k, hk⟩ := VE.Norms.mem_syms_index (hu.valid.regulated r hr)
  obtain ⟨k', hk'⟩ := VE.Norms.mem_syms_index (hu.valid.regulated r' hr')
  have h₂ := VE.Norms.find_regulated hu.valid hk'
  rw [← e, VE.Norms.find_regulated hu.valid hk] at h₂
  exact Option.some.inj h₂

/-- `fill U` is valid with only the facts of `FillLite`. -/
theorem valid_fill_lite : Valid (fill U) where
  precedence := VE.NormDefaults.dependencyOrder_ok _ (by rw [VE.NormDefaults.nodeNames_precedence]; exact hu.names)
    (fill_acyclic_lite hu)
  stratum := by rw [VE.NormDefaults.dependencyOrder_congr (fill_stratum_key_lite hu)]; exact hu.valid.stratum
  nodup := by rw [layerNames_fill_lite hu]; exact hu.valid.nodup
  decl := by
    intro q hq
    rw [syms_fill_lite hu] at hq
    obtain ⟨hd, ha, hs⟩ := hu.valid.decl q hq
    exact ⟨by rw [VE.NormDefaults.fill_E, VE.NormDefaults.fillEnv_off U (not_unsaid_lite hu hd), hd], ha, hs⟩
  typed := by
    intro k q hq φ hφ
    rw [syms_fill_lite hu] at hq
    have hmono := fun ψ (hψ : ψ.WellFormed (envAt U.D k) q.sorts.reverse) =>
      VE.Definitions.wf_mono (E := envAt U.D k) (E' := envAt (fill U) k) rfl rfl (envAt_fill_mono_lite hu k) ψ _ hψ
    cases q with
    | defn d => exact hmono φ (hu.valid.typed k _ hq φ hφ)
    | reg r =>
      rw [VE.NormDefaults.formulas_fill, List.mem_append] at hφ
      rcases hφ with hφ | hφ
      · exact hmono φ (hu.valid.typed k _ hq φ hφ)
      · simp only [List.mem_flatMap, List.mem_filter, beq_iff_eq] at hφ
        obtain ⟨F, ⟨hF, hFp⟩, hφF⟩ := hφ
        obtain ⟨r', hr', hp, rfl⟩ := VE.NormDefaults.mem_fillNodes.mp hF
        simp only [fillNode] at hFp
        have hrr : r' = r := regulated_eq_lite hu hr' (VE.Norms.mem_syms_reg (List.mem_of_getElem? hq)) hFp
        subst hrr
        simp only [fillNode, List.not_mem_nil, or_false, List.mem_cons] at hφF
        subst hφF
        obtain ⟨hd, ha, _⟩ := hu.valid.decl _ (List.mem_of_getElem? hq)
        have hn : unsaidName r'.name ∉ (layerNames (fill U).T).drop k := fun h => by
          rw [layerNames_fill_lite hu] at h
          obtain ⟨q', hq', he⟩ := List.mem_map.mp (List.mem_of_mem_drop h)
          have := (hu.valid.decl q' hq').1
          rw [he, hu.unsaid _ hp] at this; cases this
        have hpr : (envAt (fill U) k).predicates (unsaidName r'.name) = some r'.sorts := by
          simp only [envAt, VE.Norms.hide, hn, if_false, VE.NormDefaults.fill_E]
          rw [VE.NormDefaults.fillEnv_unsaid U hp]
          unfold VE.NormDefaults.sortsOf
          rw [VE.Norms.find_regulated hu.valid hq]; rfl
        exact (VE.check_iff_wellFormed _ _ _).mp (VE.NormDefaults.atom_typed hpr ha).2
  regulated := by rw [syms_fill_lite hu]; exact hu.valid.regulated
  pairs := by rw [syms_fill_lite hu]; exact hu.valid.pairs

/-- The exceptions of `F_p` are the roots on `p` (`mem_children_fillNode`). -/
theorem mem_children_fillNode_lite {r : Regulated} (hp : r.name ∈ U.unspec) {C : Node} :
    C ∈ children (fill U).T (fillNode r) ↔
      ∃ C₀ ∈ U.D.T.nodes, C = fillRoot U C₀ ∧ C₀.pred = r.name ∧ C₀.over = [] := by
  rw [VE.Norms.mem_children_iff]
  simp only [fillNode]
  constructor
  · rintro ⟨hC, hpred, hover⟩
    rcases VE.NormDefaults.mem_fill_nodes.mp hC with ⟨C₀, hC₀, rfl⟩ | hC
    · rw [VE.NormDefaults.fillRoot_pred] at hpred
      rcases VE.NormDefaults.fillRoot_over U C₀ with ⟨_, ho, _⟩ | ⟨_, he⟩
      · exact ⟨C₀, hC₀, rfl, hpred, ho⟩
      · rw [he] at hover
        obtain ⟨M, hM, hMn, _⟩ := hu.over C₀ hC₀ _ hover
        exact absurd (List.mem_map.mpr ⟨r.name, hp, hMn.symm⟩) (hu.author.freshRule M hM)
    · obtain ⟨r', _, _, rfl⟩ := VE.NormDefaults.mem_fillNodes.mp hC
      simp [fillNode] at hover
  · rintro ⟨C₀, hC₀, rfl, hpred, ho⟩
    refine ⟨VE.NormDefaults.mem_fill_nodes.mpr (Or.inl ⟨C₀, hC₀, rfl⟩), by rw [VE.NormDefaults.fillRoot_pred, hpred], ?_⟩
    rcases VE.NormDefaults.fillRoot_over U C₀ with ⟨_, _, ho'⟩ | ⟨hn, _⟩
    · rw [ho', hpred]; exact List.mem_singleton_self _
    · exact absurd ⟨hpred ▸ hp, ho⟩ hn

variable (S : VE.Structure.{u}) (ρ : VE.Valuation S)

/-- `F_p` selects exactly where the gap is filled "yes" and no author rule on `p` selects (`selects_fillNode`). -/
theorem selects_fillNode_lite {r : Regulated} (hp : r.name ∈ U.unspec) :
    SelectsD (fill U).T S ρ (fuel (fill U).T) (fillNode r) ↔
      (VE.Norms.atom (unsaidName r.name) r.sorts).denote S ρ ∧
        ¬ DecidesD U.D.T S ρ r.name true ∧ ¬ DecidesD U.D.T S ρ r.name false := by
  simp only [SelectsD, VE.Norms.AppliesD, fillNode, List.not_mem_nil, false_and, exists_false, not_false_eq_true,
    and_true]
  apply and_congr_right
  intro _
  rw [← not_or, VE.NormDefaults.decides_either, ← VE.NormDefaults.yields_iff_selects hu.author.acyclic S ρ hu.over]
  apply not_congr
  constructor
  · rintro ⟨C, hC, hy⟩
    obtain ⟨C₀, hC₀, rfl, hpred, ho⟩ := (mem_children_fillNode_lite hu hp).mp hC
    rw [VE.NormDefaults.yieldsD_fillRoot, yields_fill_fuel_lite hu.author S ρ hC₀] at hy
    exact ⟨C₀, hC₀, hpred, ho, hy⟩
  · rintro ⟨C₀, hC₀, hpred, ho, hy⟩
    refine ⟨fillRoot U C₀, (mem_children_fillNode_lite hu hp).mpr ⟨C₀, hC₀, rfl, hpred, ho⟩, ?_⟩
    rw [VE.NormDefaults.yieldsD_fillRoot, yields_fill_fuel_lite hu.author S ρ hC₀]
    exact hy

/-- A filled tree decides as its author rules do, or by `F_p` where the gap says yes and they are silent. -/
theorem decidesD_fill_lite (p : String) (sign : Bool) :
    DecidesD (fill U).T S ρ p sign ↔ DecidesD U.D.T S ρ p sign ∨
      (sign = true ∧ ∃ r ∈ U.D.T.regulated, r.name = p ∧ p ∈ U.unspec ∧
        (VE.Norms.atom (unsaidName r.name) r.sorts).denote S ρ ∧
          ¬ DecidesD U.D.T S ρ r.name true ∧ ¬ DecidesD U.D.T S ρ r.name false) := by
  simp only [DecidesD]
  constructor
  · rintro ⟨N, hN, hs, hsel⟩
    rcases VE.NormDefaults.mem_rulesOn_fill.mp hN with ⟨N₀, hN₀, rfl⟩ | ⟨r, hr, hrp, hp, rfl⟩
    · rw [VE.NormDefaults.selectsD_fillRoot, selects_fill_fuel_lite hu.author S ρ (List.mem_filter.mp hN₀).1] at hsel
      exact Or.inl ⟨N₀, hN₀, by simpa using hs, hsel⟩
    · subst hrp
      exact Or.inr ⟨hs.symm, r, hr, rfl, hp, (selects_fillNode_lite hu S ρ hp).mp hsel⟩
  · rintro (⟨N₀, hN₀, hs, hsel⟩ | ⟨rfl, r, hr, rfl, hp, hsel⟩)
    · refine ⟨fillRoot U N₀, VE.NormDefaults.mem_rulesOn_fill.mpr (Or.inl ⟨N₀, hN₀, rfl⟩), by simpa using hs, ?_⟩
      rw [VE.NormDefaults.selectsD_fillRoot, selects_fill_fuel_lite hu.author S ρ (List.mem_filter.mp hN₀).1]
      exact hsel
    · exact ⟨fillNode r, VE.NormDefaults.mem_rulesOn_fill.mpr (Or.inr ⟨r, hr, rfl, hp, rfl⟩), rfl,
        (selects_fillNode_lite hu S ρ hp).mpr hsel⟩

end Lite

/-! ## The soft-chain documents -/

theorem wellFormedSD_parts {N : NDoc} (h : WellFormedSD N = true) :
    WellFormedDoc N.D = true ∧ softShaped N.D = true ∧ fillNamesFree N = true := by
  simp only [WellFormedSD, Bool.and_eq_true] at h
  exact ⟨h.1.1.1.1, h.1.1.1.2, h.1.1.2⟩

/-- The S2a hypotheses of a superposable soft-chain document. -/
theorem hyps_sd {N : NDoc} (hN : WellFormedSD N = true) (hs : superposable N.D = true) : Hyps N.D := by
  obtain ⟨hw, hsh, _⟩ := wellFormedSD_parts hN
  refine ⟨hw, ?_, hs⟩
  have : N.D.chain = .soft := by
    simp only [softShaped, Bool.and_eq_true, beq_iff_eq] at hsh; exact hsh.1.1.1
  rw [this]; exact nofun

theorem unsaid_not_decision (X : SoftDoc) (p : String) : unsaidName p ∉ VE.SoftNorms.decisionNames X := fun h => by
  obtain ⟨t, ht⟩ := eq_append_of_startsWith soft_prefix_ascii (decision_soft h)
  have h1 : (unsaidName p).data.head? = some 'u' := by simp [unsaidName, String.data_append]
  rw [ht] at h1; simp [String.data_append] at h1

section Doc
variable {N : NDoc} (hh : Hyps N.D)
include hh

theorem supU_D : (supU N).D = soften (sup N.D).1.soft := by
  show soften (correlate (sup N.D).1) = _; rw [sup_correlate hh]

theorem choiceU_D (c : Choice) : (choiceU N c).D = soften (choiceDoc N.D c).1.soft := by
  show soften (correlate (choiceDoc N.D c).1) = _; rw [choice_correlate hh]

/-- `nameMap` keeps a name that is no decision name. -/
theorem nameMap_unsaid (c : Choice) (p : String) : nameMap N.D c (unsaidName p) = unsaidName p := by
  have hY := choiceDoc_noRights N.D c hh.noRights
  cases hf : (genKeys (choiceDoc N.D c).1).find? (·.2.1 == unsaidName p) with
  | none => unfold nameMap; rw [hf]
  | some g =>
    have hd := genKeys_decision hY (List.mem_of_find?_eq_some hf)
    have hgn : g.2.1 = unsaidName p := by simpa using List.find?_some hf
    exact absurd (List.mem_map.mpr ⟨_, hd, hgn⟩) (unsaid_not_decision _ p)

variable (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (hfree : fillNamesFree N = true)
  (hsh : softShaped N.D = true) {c : Choice} (hc : Compatible N.D c)
include hsu

omit hsu in
theorem fillNodes_choiceU : fillNodes (choiceU N c) = fillNodes (supU N) := by
  unfold fillNodes; rw [choiceU_D hh, supU_D hh]; simp only [soften]; rw [regs_eq c]; rfl

include hfree hsh hc in
theorem fillLite_choiceU : FillLite (choiceU N c) := by
  have hu := VE.NormDefaults.uvalid hsu
  have hX := fillLite_of_uvalid hu
  have hnf := namesFree hfree
  have hfr : ∀ M ∈ (choiceU N c).D.T.nodes, M.name ∉ (choiceU N c).unspec.map fillName := by
    intro M₀ hM₀
    rw [choiceU_D hh] at hM₀
    obtain ⟨M, hM, rfl⟩ := List.mem_map.mp hM₀
    show M.name ∉ _
    rcases (mem_choiceNodes N.D c M).mp hM with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, _, ha, hac⟩
    · simp only [softShaped, Bool.and_eq_true, List.isEmpty_iff] at hsh
      rw [hsh.1.1.2] at hf; cases hf
    · exact notFill_of_startsWith (hnf.declared hu (m := ("rule", M.name)) (by simp [VE.Compose.Content.declared]))
    · exact notFill_of_startsWith (hnf.sets _ (List.getElem_mem hm) ("rule", M.name)
        (candidate_declares hm ha hac (by simp [VE.Compose.Content.declared])))
  refine ⟨by rw [choiceU_D hh]; exact choice_valid hh hc,
    ⟨hfr, by rw [choiceU_D hh]; exact choice_precedence_acyclic hh hc⟩, ?_, ?_, ?_, ?_⟩
  · intro M₀ hM₀ m hm
    rw [choiceU_D hh] at hM₀ ⊢
    obtain ⟨M, hM, rfl⟩ := List.mem_map.mp hM₀
    obtain ⟨M', hM', hn, hp⟩ := choice_over_closed hh hc hM hm
    exact ⟨_, List.mem_map.mpr ⟨M', hM', rfl⟩, hn, hp⟩
  · intro p hp
    have h0 := hu.freshPred p hp
    rw [supU_D hh] at h0
    change (VE.SoftNorms.envPrime _).predicates _ = none at h0
    rw [envPrime_not_decision (unsaid_not_decision _ p)] at h0
    rw [choiceU_D hh]
    change (VE.SoftNorms.envPrime _).predicates _ = none
    rw [envPrime_not_decision (unsaid_not_decision _ p), choice_E]
    cases hfp : N.D.frame.soft.E.predicates (unsaidName p) with
    | none => rfl
    | some ss =>
      rw [sup_E_frame hh (by rw [hfp]; simp), hfp] at h0; cases h0
  · intro x hx p hp
    apply hX.stratum x _ p hp
    rw [supU_D hh]; rw [choiceU_D hh] at hx
    simpa [nodeNames, stratumNodes, soften, regs_eq c, defs_eq c] using hx
  · rw [VE.NormDefaults.fill_nodes, List.map_append, List.map_map, fillNodes_choiceU hh]
    have hsupn := hX.names
    rw [VE.NormDefaults.fill_nodes, List.map_append] at hsupn
    have h₁ : ((choiceU N c).D.T.nodes.map (Node.name ∘ fillRoot (choiceU N c))).Nodup := by
      have : Node.name ∘ fillRoot (choiceU N c) = Node.name := funext fun M => VE.NormDefaults.fillRoot_name _ M
      rw [this, choiceU_D hh]
      simpa [soften, List.map_map, Function.comp, VE.SoftNorms.primeNode] using choice_names_nodup hh c
    refine List.nodup_append.mpr ⟨h₁, (List.nodup_append.mp hsupn).2.1, fun a ha b hb e => ?_⟩
    subst e
    obtain ⟨M, hM, rfl⟩ := List.mem_map.mp ha
    obtain ⟨F, hF, he⟩ := List.mem_map.mp hb
    obtain ⟨r, _, hp, rfl⟩ := VE.NormDefaults.mem_fillNodes.mp hF
    exact hfr M hM (List.mem_map.mpr ⟨r.name, hp, by simpa using he⟩)

end Doc

/-! ## The simulation through `fill` -/

section Sim
variable {N : NDoc} (hh : Hyps N.D) {c : Choice} (hc : Compatible N.D c)
include hh

/-- On the choice's unfilled vocabulary `pullF` reads as `pull`. -/
theorem pull_pullF (S : VE.Structure.{u}) {p : String} {ss : List String}
    (hp : (soften (choiceDoc N.D c).1.soft).E.predicates p = some ss) (vs : List S.Carrier) :
    (pull N.D c S).relation p vs ↔ (pullF N c S).relation p vs := by
  have h1 : (choiceEnvFull N.D c).predicates p ≠ none := by
    unfold choiceEnvFull; rw [envAt_size_pred, choice_correlate hh, hp]; simp
  have h2 : (envAt (fill (choiceU N c)) (size (fill (choiceU N c)))).predicates p ≠ none := by
    rw [envAt_size_pred, VE.NormDefaults.fill_E]
    exact fillEnv_ne_none _ (by rw [choiceU_D hh, hp]; simp)
  exact ⟨fun h => ⟨h2, h.2⟩, fun h => ⟨h1, h.2⟩⟩

/-- `pullF` keeps the gap's table. -/
theorem pullF_unsaid (S : VE.Structure.{u}) {p : String} (hp : p ∈ N.unspec) (vs : List S.Carrier) :
    (pullF N c S).relation (unsaidName p) vs ↔ S.relation (unsaidName p) vs := by
  have hd : (envAt (fill (choiceU N c)) (size (fill (choiceU N c)))).predicates (unsaidName p) ≠ none := by
    rw [envAt_size_pred, VE.NormDefaults.fill_E, VE.NormDefaults.fillEnv_unsaid _ hp]; simp
  show (_ ∧ S.relation (nameMap N.D c (unsaidName p)) vs) ↔ _
  rw [nameMap_unsaid hh]
  exact ⟨fun h => h.2, fun h => ⟨hd, h⟩⟩

theorem atom_pullF (S : VE.Structure.{u}) {p : String} (hp : p ∈ N.unspec) (ss : List String)
    (ρ : VE.Valuation S) :
    (VE.Norms.atom (unsaidName p) ss).denote (pullF N c S) ρ ↔ (VE.Norms.atom (unsaidName p) ss).denote S ρ := by
  unfold VE.Norms.atom
  split
  · exact exists_congr fun v => and_congr_right fun _ => pullF_unsaid hh S hp _
  · exact exists_congr fun v => exists_congr fun w => and_congr_right fun _ => and_congr_right fun _ =>
      pullF_unsaid hh S hp _
  · exact Iff.rfl

include hc in
/-- The author rules decide alike at a structure that encodes `c` (S2a's simulation, then `pull` to `pullF`). -/
theorem author_sim (S : VE.Structure.{u}) (he : Encodes N.D c S) (ρ : VE.Valuation S) {q : Regulated}
    (hq : q ∈ N.D.frame.soft.T.regulated) (sign : Bool) :
    DecidesD (supU N).D.T S ρ q.name sign ↔ DecidesD (choiceU N c).D.T (pullF N c S) ρ q.name sign := by
  have hvY := choice_valid hh hc
  have hr : q ∈ (soften (choiceDoc N.D c).1.soft).T.regulated := by
    show q ∈ (choiceDoc N.D c).1.soft.T.regulated; rw [choice_reg]; exact hq
  have hT := VE.Norms.rulesTyped_of_valid hvY (VE.Norms.index_before hvY hr)
  rw [supU_D hh, choiceU_D hh, VE.SoftNorms.decidesD_soften]
  refine (sim_decides (faithful_sim hh hc S he ρ) q.name sign).trans ?_
  rw [← VE.SoftNorms.decidesD_soften, ← VE.Norms.decides_denote, ← VE.Norms.decides_denote]
  exact denote_relation_congr _ (pull N.D c S) (pullF N c S).relation
    (fun p ss hp vs _ => pull_pullF hh S (envAt_sub hp) vs) _ _ ρ
    ((VE.check_iff_wellFormed _ _ _).mpr (VE.Norms.decides_wellFormed hT sign))

variable (hN : WellFormedSD N = true) (hsu : VE.NormDefaults.WellFormedU (supU N) = true)
include hc hN hsu

theorem fillLite_choiceSD : FillLite (choiceU N c) :=
  fillLite_choiceU hh hsu (wellFormedSD_parts hN).2.2 (wellFormedSD_parts hN).2.1 hc

/-- The filled trees decide alike at a structure that encodes `c`: by the author rules, or by `F_p`. -/
theorem fill_sim_at (S : VE.Structure.{u}) (he : Encodes N.D c S) (ρ : VE.Valuation S) {q : Regulated}
    (hq : q ∈ N.D.frame.soft.T.regulated) (sign : Bool) :
    DecidesD (fill (supU N)).T S ρ q.name sign ↔ DecidesD (fill (choiceU N c)).T (pullF N c S) ρ q.name sign := by
  have hA := fun s => author_sim hh hc S he ρ hq s
  rw [decidesD_fill_lite (fillLite_of_uvalid (VE.NormDefaults.uvalid hsu)),
    decidesD_fill_lite (fillLite_choiceSD hh hc hN hsu), hA sign]
  apply or_congr_right
  apply and_congr_right; intro _
  have hregs : (choiceU N c).D.T.regulated = (supU N).D.T.regulated := by
    rw [choiceU_D hh, supU_D hh]; exact (regs_eq c).symm
  rw [hregs]
  apply exists_congr; intro r
  apply and_congr_right; intro _
  apply and_congr_right; intro hrn
  apply and_congr_right; intro hp
  rw [hrn, atom_pullF hh S hp, hA true, hA false]

end Sim

/-! ## The filled pull and the canonical interpretations (Lemma K through `fill`) -/

section K
variable {N : NDoc} (hh : Hyps N.D) {c : Choice} (hc : Compatible N.D c) (hN : WellFormedSD N = true)
  (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (B : VE.Structure.{u})
  (hcB : ∀ x s, (fill (supU N)).E.constants x = some s → ∃ v, B.constant x = some v) (he : Encodes N.D c B)
include hh hc hN hsu

omit hh hc hN in
theorem valid_fill_supU : Valid (fill (supU N)) := valid_fill_lite (fillLite_of_uvalid (VE.NormDefaults.uvalid hsu))

theorem valid_fill_choiceSD : Valid (fill (choiceU N c)) := valid_fill_lite (fillLite_choiceSD hh hc hN hsu)

omit hc hN in
include he in
theorem encodes_canon_fill : Encodes N.D c (canon (fill (supU N)) B) := by
  intro R hR i hi
  have hw := VE.Definitions.wf_mono (E := envAt (supU N).D 0) (E' := envAt (fill (supU N)) 0) rfl rfl
    (envAt_fill_mono_lite (fillLite_of_uvalid (VE.NormDefaults.uvalid hsu)) 0) _ []
    (by rw [supU_D hh]; exact choiceAtom_wf hh R.id i [])
  rw [VE.SoftNorms.canon_base B _ [] hw []]
  exact he R hR i hi

theorem layer_supU {p : String} (hp : p ∉ layerNames (fill (choiceU N c)).T) :
    nameMap N.D c p ∉ layerNames (fill (supU N)).T := by
  rw [layerNames_fill_lite (fillLite_of_uvalid (VE.NormDefaults.uvalid hsu)), supU_D hh]
  exact nameMap_nonlayer hh hc (by
    rwa [layerNames_fill_lite (fillLite_choiceSD hh hc hN hsu), choiceU_D hh] at hp)

theorem pullF_canon_off {p : String} (hp : p ∉ layerNames (fill (choiceU N c)).T) (ws : List B.Carrier) :
    (pullF N c (canon (fill (supU N)) B)).relation p ws ↔ (canon (fill (choiceU N c)) (pullF N c B)).relation p ws := by
  rw [VE.SoftNorms.canon_off (pullF N c B) hp]
  show (_ ∧ (canon (fill (supU N)) B).relation (nameMap N.D c p) ws) ↔ (_ ∧ B.relation (nameMap N.D c p) ws)
  rw [VE.SoftNorms.canon_off B (layer_supU hh hc hN hsu hp)]

omit hc hN hsu in
theorem constants_choiceSD (x s : String) (hx : (fill (choiceU N c)).E.constants x = some s) :
    (fill (supU N)).E.constants x = some s := by
  rw [VE.NormDefaults.fill_E, VE.NormDefaults.fillEnv_constants, choiceU_D hh, soften_E,
    envPrime_constants, choice_E c] at hx
  rw [VE.NormDefaults.fill_E, VE.NormDefaults.fillEnv_constants, supU_D hh]
  exact frame_const_sup hh hx

include hcB he in
theorem pullF_canon_layer : ∀ (j : Nat) (q : VE.Norms.Sym), (syms (fill (choiceU N c)).T)[j]? = some q →
    ∀ ws : List B.Carrier, ws.length = q.sorts.length →
      ((pullF N c (canon (fill (supU N)) B)).relation q.name ws ↔
        (canon (fill (choiceU N c)) (pullF N c B)).relation q.name ws) := by
  intro j
  induction j using Nat.strongRecOn with
  | ind j ih =>
  intro q hq ws hws
  have hX := fillLite_of_uvalid (VE.NormDefaults.uvalid hsu)
  have hY := fillLite_choiceSD hh hc hN hsu
  have hvY := valid_fill_choiceSD hh hc hN hsu
  have hvX := valid_fill_supU hsu
  have hqY : q ∈ syms (soften (choiceDoc N.D c).1.soft).T := by
    have := List.mem_of_getElem? hq; rwa [syms_fill_lite hY, choiceU_D hh] at this
  obtain ⟨j', hj'⟩ := VE.Norms.mem_syms_index (show q ∈ syms (fill (supU N)).T by
    rw [syms_fill_lite hX, supU_D hh]; exact sup_choice_sym hh c hqY)
  have hfr := choice_sym_frame hh c hqY
  have hcdY : ∀ x s, (fill (choiceU N c)).E.constants x = some s → ∃ v, (pullF N c B).constant x = some v :=
    fun x s hx => hcB x s (constants_choiceSD hh x s hx)
  have hfull : (envAt (fill (choiceU N c)) (size (fill (choiceU N c)))).predicates q.name ≠ none := by
    rw [envAt_size_pred, (hvY.decl q (List.mem_of_getElem? hq)).1]; simp
  have hL : (pullF N c (canon (fill (supU N)) B)).relation q.name ws ↔
      (q.meaning (fill (supU N)).T).denote (canon (fill (supU N)) B) (VE.Norms.tupleVal ws) := by
    show (_ ∧ (canon (fill (supU N)) B).relation (nameMap N.D c q.name) ws) ↔ _
    rw [nameMap_frame hh c (by rw [hfr]; simp), canon_meaning hvX B hcB hj' ws hws]
    exact ⟨fun h => h.2, fun h => ⟨hfull, h⟩⟩
  rw [hL, canon_meaning hvY (pullF N c B) hcdY hq ws hws]
  have hM : (q.meaning (fill (supU N)).T).denote (canon (fill (supU N)) B) (VE.Norms.tupleVal ws) ↔
      (q.meaning (fill (choiceU N c)).T).denote (pullF N c (canon (fill (supU N)) B)) (VE.Norms.tupleVal ws) := by
    cases q with
    | reg r =>
      have hr : r ∈ N.D.frame.soft.T.regulated := by
        rw [← choice_reg c]; exact VE.Norms.mem_syms_reg hqY
      have h1 := fun sign => fill_sim_at hh hc hN hsu _ (encodes_canon_fill hh hsu B he)
        (VE.Norms.tupleVal ws) hr sign
      simp only [VE.Norms.Sym.meaning]
      rw [VE.Norms.outcome_denote, VE.Norms.outcome_denote]
      simp only [VE.Norms.pos, VE.Norms.neg, VE.Norms.decides_denote, h1]
    | defn d =>
      have hd : d ∈ (free N.D).1.soft.T.definitions := by
        rw [free_defs, ← choice_defs c]; exact VE.Norms.mem_syms_defn hqY
      simp only [VE.Norms.Sym.meaning]
      apply denote_relation_congr (VE.SoftNorms.envPrime (free N.D).1.soft) _ _ _ d.body d.args.reverse _
        (free_def_typed hh hd)
      intro p ss hp vs _
      have hpY := free_envPrime_sub hh c hp
      show _ ↔ ((envAt (fill (choiceU N c)) (size (fill (choiceU N c)))).predicates p ≠ none ∧ _)
      have hne : (choiceU N c).D.E.predicates p ≠ none := by
        rw [choiceU_D hh]; show (VE.SoftNorms.envPrime _).predicates p ≠ none
        rw [hpY]; simp
      rw [nameMap_shared hh c (by rw [hp]; simp), envAt_size_pred, VE.NormDefaults.fill_E]
      exact ⟨fun h => ⟨fillEnv_ne_none _ hne, h⟩, fun h => h.2⟩
  rw [hM]
  apply denote_relation_congr (envAt (fill (choiceU N c)) j) _ _ _ _ q.sorts.reverse _
    ((VE.check_iff_wellFormed _ _ _).mpr (VE.Norms.meaning_wellFormed hvY hq))
  intro p ss hp vs hvs
  by_cases hpl : p ∈ layerNames (fill (choiceU N c)).T
  · obtain ⟨q', hq', rfl⟩ := List.mem_map.mp hpl
    obtain ⟨k, hk⟩ := VE.Norms.mem_syms_index hq'
    have hkj : k < j := by
      rcases Nat.lt_or_ge k j with h | h
      · exact h
      · rw [VE.Norms.envAt_later hvY hk h] at hp; cases hp
    rw [VE.Norms.envAt_earlier hvY hk hkj] at hp
    cases hp
    exact ih k hkj q' hk vs hvs
  · exact pullF_canon_off hh hc hN hsu B hpl vs

include hcB he in
/-- Lemma K through `fill`, over the complete vocabulary of the choice's filled document. -/
theorem pullF_canon {p : String} {ss : List String} (hp : (fill (choiceU N c)).E.predicates p = some ss)
    (ws : List B.Carrier) (hws : ws.length = ss.length) :
    (pullF N c (canon (fill (supU N)) B)).relation p ws ↔ (canon (fill (choiceU N c)) (pullF N c B)).relation p ws := by
  by_cases hpl : p ∈ layerNames (fill (choiceU N c)).T
  · obtain ⟨q, hq, rfl⟩ := List.mem_map.mp hpl
    obtain ⟨k, hk⟩ := VE.Norms.mem_syms_index hq
    rw [((valid_fill_choiceSD hh hc hN hsu).decl q hq).1] at hp
    cases hp
    exact pullF_canon_layer hh hc hN hsu B hcB he k q hk ws hws
  · exact pullF_canon_off hh hc hN hsu B hpl ws

end K

/-! ## The statements of 13.3 -/

/-- `fill_sim`: the filled trees decide alike at an encoded filled base (S2a's `sim_decides`, `pull_canon` through
    `fill`). -/
theorem fill_sim (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c)
    (B : VE.Structure.{u}) (hB : VE.Norms.BaseAdmissible (fill (supU N)) B) (hsl : Sat B (slotP N.D))
    (he : Encodes N.D c B) (q : Regulated) (hq : q ∈ N.D.frame.soft.T.regulated)
    (ρ : VE.Valuation B) (sign : Bool) :
    VE.Norms.DecidesD (fill (supU N)).T (VE.SoftNorms.canon (fill (supU N)) B) ρ q.name sign ↔
      VE.Norms.DecidesD (fill (choiceU N c)).T (VE.SoftNorms.canon (fill (choiceU N c)) (pullF N c B)) ρ q.name sign := by
  have hh := hyps_sd hN hs
  have hcB : ∀ x s, (fill (supU N)).E.constants x = some s → ∃ v, B.constant x = some v :=
    fun x s hx => (hB.1.1 x s hx).imp fun _ h => h.1
  have hvY := valid_fill_choiceSD hh hc hN hsu
  have hr : q ∈ (fill (choiceU N c)).T.regulated := by
    show q ∈ (choiceU N c).D.T.regulated; rw [choiceU_D hh]; show q ∈ (choiceDoc N.D c).1.soft.T.regulated
    rw [choice_reg]; exact hq
  have hT := VE.Norms.rulesTyped_of_valid hvY (VE.Norms.index_before hvY hr)
  rw [fill_sim_at hh hc hN hsu _ (encodes_canon_fill hh hsu B he) ρ hq sign,
    ← VE.Norms.decides_denote, ← VE.Norms.decides_denote]
  exact denote_relation_congr _ (pullF N c (canon (fill (supU N)) B))
    (canon (fill (choiceU N c)) (pullF N c B)).relation
    (fun p ss hp vs hvs => pullF_canon hh hc hN hsu B hcB he (envAt_sub hp) vs hvs)
    _ _ ρ ((VE.check_iff_wellFormed _ _ _).mpr (VE.Norms.decides_wellFormed hT sign))

/-- The author rules (no `F_p`) decide alike: what `gapF` reads. -/
theorem fill_sim_author (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c)
    (B : VE.Structure.{u}) (hB : VE.Norms.BaseAdmissible (fill (supU N)) B) (hsl : Sat B (slotP N.D))
    (he : Encodes N.D c B) (q : Regulated) (hq : q ∈ N.D.frame.soft.T.regulated)
    (ρ : VE.Valuation B) (sign : Bool) :
    VE.Norms.DecidesD (supU N).D.T (VE.SoftNorms.canon (fill (supU N)) B) ρ q.name sign ↔
      VE.Norms.DecidesD (choiceU N c).D.T (VE.SoftNorms.canon (fill (choiceU N c)) (pullF N c B)) ρ q.name sign := by
  have hh := hyps_sd hN hs
  have hcB : ∀ x s, (fill (supU N)).E.constants x = some s → ∃ v, B.constant x = some v :=
    fun x s hx => (hB.1.1 x s hx).imp fun _ h => h.1
  have hvY := valid_fill_choiceSD hh hc hN hsu
  have hr : q ∈ (fill (choiceU N c)).T.regulated := by
    show q ∈ (choiceU N c).D.T.regulated; rw [choiceU_D hh]; show q ∈ (choiceDoc N.D c).1.soft.T.regulated
    rw [choice_reg]; exact hq
  have hT := rulesTyped_author (VE.Norms.rulesTyped_of_valid hvY (VE.Norms.index_before hvY hr))
  rw [author_sim hh hc _ (encodes_canon_fill hh hsu B he) ρ hq sign,
    ← VE.Norms.decides_denote, ← VE.Norms.decides_denote]
  exact denote_relation_congr _ (pullF N c (canon (fill (supU N)) B))
    (canon (fill (choiceU N c)) (pullF N c B)).relation
    (fun p ss hp vs hvs => pullF_canon hh hc hN hsu B hcB he (envAt_sub hp) vs hvs)
    _ _ ρ ((VE.check_iff_wellFormed _ _ _).mpr (VE.Norms.decides_wellFormed hT sign))

end VE.Readings
