import VE.Readings.SoftVerdicts
import VE.Readings.SupExtra
import VE.Readings.BarQuiet
import VE.Defaults.Meaning

/-! SC-10's first part (docs/spec/rd-9-soft-chain.md 13.1, 13.3): superposition under the soft completion.

The superposed soft document is read as norm-defaults reads a soft document (`supU N`), and `fill` runs after
`soften`, on the superposed document (D1). `fill (supU N)` is not `soften` of any superposed document, so S2a's
simulation is applied to the author rules and `fill` is added on each side: a filled tree decides as its author rules
do, or by `F_p` where the gap says yes and the author rules are silent (`decidesD_fill`). The filled pull `pullF` is
S2a's `pull` onto the filled choice's vocabulary, which keeps the `unsaid__` tables (13.4 item 3). `Fill_T` and `supX`
transfer through it at an encoded filled base (`fillPremisesSD_pull`, `supX_pull`, sc-10). -/
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

/-- The outcome formulas transfer at an encoded filled base (`fill_sim`). -/
theorem outcome_pullF (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c)
    (B : VE.Structure.{u}) (hB : VE.Norms.BaseAdmissible (fill (supU N)) B) (hsl : Sat B (slotP N.D))
    (he : Encodes N.D c B) {q : Regulated} (hq : q ∈ (supU N).D.T.regulated) (vs : List B.Carrier)
    (hvs : VE.TupleTyped B q.sorts vs) :
    (VE.Norms.outcomeBase (fill (supU N)) q.name).denote B (VE.Norms.tupleVal vs) ↔
      (VE.Norms.outcomeBase (fill (choiceU N c)) q.name).denote (pullF N c B) (VE.Norms.tupleVal vs) := by
  have hh := hyps_sd hN hs
  have hcY : VE.Norms.ConstantsTyped (fill (choiceU N c)) (pullF N c B) := fun x s hx =>
    hB.1.1 x s (constants_choiceSD hh x s hx)
  have hregX : (supU N).D.T.regulated = N.D.frame.soft.T.regulated := by rw [supU_D hh]; exact sup_reg
  have hregY : (choiceU N c).D.T.regulated = N.D.frame.soft.T.regulated := by rw [choiceU_D hh]; exact choice_reg c
  have hqf : q ∈ N.D.frame.soft.T.regulated := hregX ▸ hq
  rw [VE.NormDefaults.outcomeBase_fill hsu hB.1.1 hq vs hvs, outcomeBase_fill_v (valid_fill_choiceSD hh hc hN hsu)
    hcY (hregY ▸ hqf) vs ((VE.Norms.tupleTyped_relation B _ _ vs).mpr hvs)]
  split
  · exact not_congr (fill_sim N hN hs hsu c hc B hB hsl he q hqf _ false)
  · exact fill_sim N hN hs hsu c hc B hB hsl he q hqf _ true

/-- `Fill_T` transfers at an encoded filled base. -/
theorem fillPremisesSD_pull (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c)
    (B : VE.Structure.{u}) (hB : VE.Norms.BaseAdmissible (fill (supU N)) B) (hsl : Sat B (slotP N.D))
    (he : Encodes N.D c B) :
    Sat B (VE.NormDefaults.fillPremises (supU N)) ↔ Sat (pullF N c B) (VE.NormDefaults.fillPremises (choiceU N c)) := by
  have hh := hyps_sd hN hs
  have hu := VE.NormDefaults.uvalid hsu
  have hvY := valid_fill_choiceSD hh hc hN hsu
  have hcX : VE.Norms.ConstantsTyped (fill (supU N)) B := hB.1.1
  have hcY : VE.Norms.ConstantsTyped (fill (choiceU N c)) (pullF N c B) := fun x s hx =>
    hcX x s (constants_choiceSD hh x s hx)
  have hregX : (supU N).D.T.regulated = N.D.frame.soft.T.regulated := by rw [supU_D hh]; exact sup_reg
  have hregY : (choiceU N c).D.T.regulated = N.D.frame.soft.T.regulated := by rw [choiceU_D hh]; exact choice_reg c
  have tp : ∀ ss (vs : List B.Carrier), VE.TupleTyped B ss vs ↔ VE.TupleTyped (pullF N c B) ss vs :=
    fun ss vs => (VE.Norms.tupleTyped_relation B _ _ vs).symm
  have hO := fun (q : Regulated) (hq : q ∈ (supU N).D.T.regulated) =>
    outcome_pullF N hN hs hsu c hc B hB hsl he hq
  have hG : ∀ q ∈ (supU N).D.T.regulated, ∀ vs : List B.Carrier, VE.TupleTyped B q.sorts vs →
      ((VE.NormDefaults.gapF (supU N) q.name).denote B (VE.Norms.tupleVal vs) ↔
        (VE.NormDefaults.gapF (choiceU N c) q.name).denote (pullF N c B) (VE.Norms.tupleVal vs)) := by
    intro q hq vs hvs
    have hqf : q ∈ N.D.frame.soft.T.regulated := hregX ▸ hq
    by_cases hp : q.name ∈ N.unspec
    · rw [VE.NormDefaults.gapF_fill hu hsu hcX hq hp vs hvs,
        gapF_fill_v hvY hcY (hregY ▸ hqf) hp vs ((tp _ vs).mp hvs),
        fill_sim_author N hN hs hsu c hc B hB hsl he q hqf _ true,
        fill_sim_author N hN hs hsu c hc B hB hsl he q hqf _ false]
    · simp only [VE.NormDefaults.gapF, show (supU N).unspec = N.unspec from rfl,
        show (choiceU N c).unspec = N.unspec from rfl, if_neg hp]; exact Iff.rfl
  have hpairs : VE.Norms.pairs (choiceU N c).D.T = VE.Norms.pairs (supU N).D.T := by
    unfold VE.Norms.pairs; rw [hregX, hregY]
  unfold VE.NormDefaults.fillPremises
  rw [show (choiceU N c).unspec = N.unspec from rfl, show (supU N).unspec = N.unspec from rfl, hpairs]
  simp only [Sat, List.forall_mem_map]
  refine forall₂_congr fun pr hpr => ?_
  have hpr' := (List.mem_filter.mp hpr).1
  obtain ⟨r, hr, hrn, _, _, hrs⟩ := VE.NormDefaults.pair_req hpr'
  obtain ⟨m, hm, hmn, _, hms⟩ := VE.NormDefaults.pair_perm hu hpr'
  rw [VE.Norms.bindAll_denote_nil, VE.Norms.bindAll_denote_nil]
  refine forall_congr' fun vs => ?_
  rw [← tp]
  refine imp_congr_right fun hvs => ?_
  simp only [VE.Formula.denote, VE.Norms.pairConflict]
  rw [← hrn, ← hmn, hO r hr vs (hrs ▸ hvs), hO m hm vs (hms ▸ hvs), hG r hr vs (hrs ▸ hvs), hG m hm vs (hms ▸ hvs)]

/-! ## `supX` at an encoded base

An image's premises read the base as the choice's read its filled pull. A premise of a candidate not chosen holds:
a sufficient condition and a coherence premise by the candidate's bit, a necessary condition because the slot's quiet
premise empties the candidate's `excepted` table (S-4, S-4′). -/

section X
variable {N : NDoc} (hh : Hyps N.D) {c : Choice} (hc : Compatible N.D c)
include hh

theorem pullF_pull (S : VE.Structure.{u}) {p : String} (hp : (choiceEnvFull N.D c).predicates p ≠ none)
    (vs : List S.Carrier) : (pullF N c S).relation p vs ↔ (pull N.D c S).relation p vs := by
  have h2 : (envAt (fill (choiceU N c)) (size (fill (choiceU N c)))).predicates p ≠ none := by
    unfold choiceEnvFull at hp
    rw [envAt_size_pred, choice_correlate hh] at hp
    rw [envAt_size_pred, VE.NormDefaults.fill_E]
    exact fillEnv_ne_none _ (by rw [choiceU_D hh]; exact hp)
  exact ⟨fun h => ⟨hp, h.2⟩, fun h => ⟨h2, h.2⟩⟩

theorem pullF_denote_frame (S : VE.Structure.{u}) (φ : VE.Formula) (Γ : List String)
    (hφ : φ.WellFormed N.D.frame.soft.E Γ) (ρ : VE.Valuation S) : φ.denote S ρ ↔ φ.denote (pullF N c S) ρ :=
  denote_relation_congr N.D.frame.soft.E S _ (fun p ss hp vs _ =>
    ((pullF_pull hh S (choiceEnvFull_frame hh c (by simp [hp])) vs).trans (pull_frame hh c S (by simp [hp]) vs)).symm)
    φ Γ ρ ((VE.check_iff_wellFormed _ _ _).mpr hφ)

theorem exceptedF_pullF (S : VE.Structure.{u}) {M : SoftNode} (hM : M ∈ (choiceDoc N.D c).1.soft.T.nodes)
    (hd : M.mode = .default) (ρ : VE.Valuation S) :
    (VE.SoftNorms.exceptedF (sup N.D).1.soft (fmap N.D c M)).denote S ρ ↔
      (VE.SoftNorms.exceptedF (choiceDoc N.D c).1.soft M).denote (pullF N c S) ρ := by
  refine (excepted_pull hh c S hM hd ρ).trans
    (atom_congr (pull N.D c S) (pullF N c S).relation _ _ _ (fun vs => (pullF_pull hh S ?_ vs).symm) ρ)
  apply choiceEnvFull_decision hh c
  simp only [VE.SoftNorms.decisionNames, VE.SoftNorms.decisions, VE.SoftNorms.exceptedDecisions, List.map_append,
    List.mem_append, List.mem_map, List.mem_filter]
  exact Or.inl (Or.inl ⟨_, ⟨M, ⟨hM, by simp [hd]⟩, rfl⟩, rfl⟩)

include hc in
/-- An unchosen candidate's gate is false where the bits encode `c`. -/
theorem pattern_off {S : VE.Structure.{u}} (he : Encodes N.D c S) {m i : Nat} (hm : m < N.D.sets.length)
    (hi : i < N.D.sets[m].candidates.length) (hno : c.index N.D.sets[m].id ≠ some i) (ρ : VE.Valuation S) :
    ¬ (pattern (m + 1) (setSize N.D m) i).denote S ρ := by
  intro hχ
  have hilt : i < setSize N.D m := by rw [setSize_eq hm]; exact hi
  rw [pattern_rho, ← choiceAtom_eq (findIdx_of_nodup hh.nodup hm) hilt] at hχ
  have hmem := (he _ (List.getElem_mem hm) i (by rw [← setSize_eq hm]; exact hilt)).mp hχ
  have hcm : complete N.D c = true := by
    simp only [Compatible, compatible, Bool.and_eq_true] at hc; exact hc.1.1
  have := index_of_mem ((complete_map hcm) ▸ hh.nodup) hmem
  exact hno this

/-- An image's exception is the rule's own, each sufficient condition gated by a formula true at an encoded base. -/
theorem fmap_exception_eq {S : VE.Structure.{u}} (he : Encodes N.D c S) {M : SoftNode}
    (hM : M ∈ (choiceDoc N.D c).1.soft.T.nodes) :
    ∃ g : VE.Formula → VE.Formula, (∀ C ρ, (g C).denote S ρ ↔ C.denote S ρ) ∧
      (fmap N.D c M).exception = M.exception.map (fun e => { e with sufficient := e.sufficient.map g }) := by
  rcases (mem_choiceNodes N.D c M).mp hM with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hcc⟩
  · exact ⟨id, fun _ _ => Iff.rfl, by rw [fmap_frame hh c hf]; cases M.exception <;> simp⟩
  · exact ⟨id, fun _ _ => Iff.rfl, by rw [fmap_fixed hh c hu]; cases h : M.exception <;> simp [copyOver, h]⟩
  · rw [fmap_chosen hh c hm hi ha hcc]
    have hilt : i < N.D.sets[m].candidates.length := (List.getElem?_eq_some_iff.mp ha).1
    have hχ : ∀ ρ, (pattern (m + 1) (setSize N.D m) i).denote S ρ := fun ρ => by
      rw [pattern_rho, ← choiceAtom_eq (findIdx_of_nodup hh.nodup hm) (by rw [setSize_eq hm]; exact hilt)]
      exact (he _ (List.getElem_mem hm) i hilt).mpr (mem_of_index hi)
    exact ⟨fun C => .and C (pattern (m + 1) (setSize N.D m) i),
      fun C ρ => ⟨fun h => h.1, fun h => ⟨h, hχ ρ⟩⟩, rfl⟩

include hc in
theorem exc_pullF {B : VE.Structure.{u}} (he : Encodes N.D c B) (hsl : Sat B (slotP N.D)) :
    Sat B (VE.SoftNorms.excPremises (sup N.D).1.soft) ↔
      Sat (pullF N c B) (VE.SoftNorms.excPremises (choiceDoc N.D c).1.soft) := by
  have img : ∀ M ∈ (choiceDoc N.D c).1.soft.T.nodes,
      (∀ a ∈ VE.SoftNorms.excPremisesOf (sup N.D).1.soft (fmap N.D c M), a.denote B []) ↔
        ∀ a ∈ VE.SoftNorms.excPremisesOf (choiceDoc N.D c).1.soft M, a.denote (pullF N c B) [] := by
    intro M hM
    obtain ⟨g, hg, hex⟩ := fmap_exception_eq hh he hM
    obtain ⟨hpred, _, hmode, _, _, _⟩ := fmap_fields hh c hM
    have hss : VE.SoftNorms.sortsOf (sup N.D).1.soft (fmap N.D c M).pred =
        VE.SoftNorms.sortsOf (choiceDoc N.D c).1.soft M.pred := by rw [hpred, sortsOf_eq c]
    unfold VE.SoftNorms.excPremisesOf
    rw [hmode, hex]
    cases hm : M.mode with
    | strict => simp
    | default =>
      cases hE : M.exception with
      | none => simp
      | some e =>
        have hC : ∀ C ∈ e.sufficient ++ e.necessary, ∀ ρ, C.denote B ρ ↔ C.denote (pullF N c B) ρ :=
          fun C hC ρ => by obtain ⟨Γ, hw⟩ := choice_exc_typed hh c hM hE C hC; exact pullF_denote_frame hh B C Γ hw ρ
        simp only [Option.map_some, List.forall_mem_append, List.forall_mem_map, List.map_map, Function.comp,
          VE.Norms.bindAll_denote_nil, hss]
        refine and_congr (forall₂_congr fun C hCm => forall_congr' fun vs => ?_)
          (forall₂_congr fun C hCm => forall_congr' fun vs => ?_) <;>
        rw [← VE.Norms.tupleTyped_relation B (pullF N c B).relation] <;>
        refine imp_congr_right fun _ => ?_ <;>
        simp only [VE.Formula.denote] <;>
        rw [exceptedF_pullF hh B hM hm]
        · rw [hg, hC C (List.mem_append_left _ hCm)]
        · rw [hC C (List.mem_append_right _ hCm)]
  have hq : Sat B (choicePremises N.D) := fun a ha => hsl a (by
    simp only [slotP, slotLabelled, choicePremises, VE.Compose.Labelled.formulas, List.map_append,
      List.mem_append] at ha ⊢
    exact Or.inl (Or.inr ha))
  simp only [Sat, VE.SoftNorms.excPremises, List.forall_mem_flatMap]
  constructor
  · intro hX M hM
    exact (img M hM).mp (hX _ (fmap_mem hh c hM))
  · intro hY M' hM'
    by_cases hi : ∃ M ∈ (choiceDoc N.D c).1.soft.T.nodes, fmap N.D c M = M'
    · obtain ⟨M, hM, rfl⟩ := hi
      exact (img M hM).mpr (hY M hM)
    simp only [not_exists, not_and] at hi
    rcases (mem_supNodes N.D M').mp hM' with hf | ⟨u, F, cs, hu, rfl⟩ | ⟨m, hm, i', a, K, ha, hac, rfl⟩
    · exact absurd (fmap_frame hh c hf) (hi M' ((mem_choiceNodes N.D c M').mpr (Or.inl hf)))
    · exact absurd (fmap_fixed hh c hu) (hi F ((mem_choiceNodes N.D c F).mpr (Or.inr (Or.inl ⟨u, cs, hu⟩))))
    obtain ⟨i, hci, _⟩ := choice_index hh hc hm
    have hii : c.index N.D.sets[m].id ≠ some i' := fun h => by
      rw [hci] at h; cases h
      exact hi K ((mem_choiceNodes N.D c K).mpr (Or.inr (Or.inr ⟨m, hm, i', a, hci, ha, hac⟩)))
        (fmap_chosen hh c hm hci ha hac)
    have hilt : i' < N.D.sets[m].candidates.length := (List.getElem?_eq_some_iff.mp ha).1
    have hoff := pattern_off hh hc he hm hilt hii
    unfold VE.SoftNorms.excPremisesOf
    cases hmK : (gateNorm N.D m i' K).mode with
    | strict => simp
    | default =>
      cases hE : K.exception with
      | none => simp [gateNorm, hE]
      | some e =>
        simp only [gateNorm, hE, Option.map_some, List.forall_mem_append, List.forall_mem_map,
          VE.Norms.bindAll_denote_nil]
        refine ⟨fun C _ vs _ h => absurd h.2 (hoff _), fun C _ vs hvs hx => absurd hx ?_⟩
        -- the slot's quiet premise empties the unchosen candidate's `excepted` table
        let M' := gateNorm N.D m i' K
        have hd : M'.mode = .default := hmK
        have hg : (GenKey.excepted M'.name none, VE.SoftNorms.exceptedName M',
            VE.SoftNorms.sortsOf (correlate (sup N.D).1) M'.pred) ∈ genKeys (sup N.D).1 := by
          obtain ⟨_, _, hb, hs⟩ := noRights_parts hh.noRights
          have hlines : VE.Rights.linesOf (sup N.D).1 = [] := by simp [VE.Rights.linesOf, hs, VE.Rights.linesAux]
          have hk : keyedNodes (sup N.D).1 = (sup N.D).1.soft.T.nodes.map (fun N => (N, N.name, none)) := by
            simp [keyedNodes, hlines, VE.Rights.barNodes_nil _ hb]
          simp only [genKeys, hk, List.mem_append]
          refine Or.inl (Or.inl (Or.inl (Or.inl (Or.inl ?_))))
          exact List.mem_map.mpr ⟨(M', M'.name, none), List.mem_filter.mpr ⟨List.mem_map.mpr ⟨M', hM', rfl⟩,
            by simp [hd]⟩, rfl⟩
        have ho : origin N.D M'.name = some (m, i') :=
          origin_qualify hm hilt ha hac (d := ("rule", K.name)) (by simp [VE.Compose.Content.declared])
        have hown : owners N.D (GenKey.excepted M'.name none) = [[(m, i')]] := by simp [owners, ho]
        have hQ := quiet_holds hq hg (by simp [fixedGenerated, hown]) (by
          simp only [hown, List.mem_singleton]; rintro o rfl x hx
          simp only [List.mem_singleton] at hx; subst hx; exact ⟨hm, by rw [setSize_eq hm]; exact hilt⟩)
        simp only [quietFormula, hown, VE.Norms.bindAll_denote_nil, sup_correlate hh] at hQ
        intro hx'
        have h1 := hQ vs hvs hx'
        simp only [List.map_cons, List.map_nil, disj_denote, conj_denote, List.mem_singleton, forall_eq,
          exists_eq_left] at h1
        unfold atomAt at h1
        rw [List.getElem?_eq_getElem hm, choiceAtom_rho] at h1
        simp only [Option.map_some, Option.getD_some] at h1
        rw [choiceAtom_eq (findIdx_of_nodup hh.nodup hm) (by rw [setSize_eq hm]; exact hilt)] at h1
        exact hoff _ h1

end X

theorem selects_fillRoot (U : UDoc) (T : Tree) (f : Nat) (M : Node) :
    VE.Norms.selects T f (fillRoot U M) = VE.Norms.selects T f M := by
  unfold fillRoot; split <;> rfl

/-- A rule's selection on the filled tree is typed over the full filled vocabulary at its act's sorts. -/
theorem selects_fill_wf {U : UDoc} {Z : SoftDoc} (hU : U.D = soften Z) (hv : Valid (fill U)) {K : SoftNode}
    (hK : K ∈ Z.T.nodes) (hreg : K.pred ∈ Z.T.regulated.map (·.name)) :
    (VE.Norms.selects (fill U).T (fuel (fill U).T) (VE.SoftNorms.primeNode Z K)).WellFormed
      (envAt (fill U) (size (fill U))) (VE.SoftNorms.sortsOf Z K.pred).reverse := by
  obtain ⟨r, hr, hrn⟩ := List.mem_map.mp hreg
  have e : (fill U).T.regulated = Z.T.regulated := by show U.D.T.regulated = _; rw [hU]; rfl
  have hk := VE.Norms.index_before hv (show r ∈ (fill U).T.regulated by rw [e]; exact hr)
  have hs : VE.SoftNorms.sortsOf Z K.pred = r.sorts := by
    unfold VE.SoftNorms.sortsOf VE.SoftNorms.sortsIn; rw [← hrn, ← e, VE.Norms.find_regulated hv hk]; rfl
  have hK0 : VE.SoftNorms.primeNode Z K ∈ U.D.T.nodes := by rw [hU]; exact List.mem_map_of_mem hK
  have hsel := VE.Norms.selects_wellFormed (VE.Norms.rulesTyped_of_valid hv hk) (fuel (fill U).T) _
    (VE.NormDefaults.mem_fill_nodes.mpr (Or.inl ⟨_, hK0, rfl⟩)) (by rw [VE.NormDefaults.fillRoot_pred]; exact hrn.symm)
  rw [selects_fillRoot] at hsel
  rw [hs]
  exact VE.Norms.envAt_mono (Nat.le_of_lt (List.getElem?_eq_some_iff.mp hk).1) _ _ hsel

/-- A rule's selection on the filled tree, as `cohPremiseU` reads it, is its soft selection on the canonical
    interpretation of `fill U`. -/
theorem selU_canon {U : UDoc} {Z : SoftDoc} (hU : U.D = soften Z) (hu : FillLite U) (hv : Valid (fill U))
    {B : VE.Structure.{u}} (hc : VE.Norms.ConstantsTyped (fill U) B) {K : SoftNode} (hK : K ∈ Z.T.nodes)
    (hreg : K.pred ∈ Z.T.regulated.map (·.name)) (vs : List B.Carrier)
    (hvs : VE.TupleTyped B (VE.SoftNorms.sortsOf Z K.pred) vs) :
    (VE.Defaults.selU U Z K).denote B (VE.Norms.tupleVal vs) ↔
      VE.SoftNorms.SelectsSoftD Z (canon (fill U) B) (VE.Norms.tupleVal vs) (VE.SoftNorms.fuel Z) K := by
  have hK0 : VE.SoftNorms.primeNode Z K ∈ U.D.T.nodes := by rw [hU]; exact List.mem_map_of_mem hK
  unfold VE.Defaults.selU
  rw [VE.SoftNorms.canon_subst hv B hc _ _ _ (selects_fill_wf hU hv hK hreg) _ (VE.Norms.tupleVal_typed B _ vs hvs),
    VE.Norms.selects_denote, selects_fill_fuel_lite hu.author _ _ hK0, ← VE.Norms.selects_denote]
  revert hK0; rw [hU]; intro _
  exact VE.SoftNorms.selectsPrime_denote Z _ _ K

section Coh
variable {N : NDoc} (hh : Hyps N.D) {c : Choice} (hc : Compatible N.D c) (hN : WellFormedSD N = true)
  (hsu : VE.NormDefaults.WellFormedU (supU N) = true) {B : VE.Structure.{u}}
  (hB : VE.Norms.BaseAdmissible (fill (supU N)) B) (he : Encodes N.D c B)
include hh hc hN hsu hB he

/-- The coherence premises on the filled trees transfer: an image pair as S2a's `coh_down`, through `fill_sim`'s
    pieces; a pair with an unchosen member never selects both. -/
theorem coh_pullF :
    Sat B ((VE.SoftNorms.collidingPairs (sup N.D).1.soft).map
        (fun x => VE.NormDefaults.Wire.cohPremiseU (supU N) (sup N.D).1.soft x.1 x.2)) ↔
      Sat (pullF N c B) ((VE.SoftNorms.collidingPairs (choiceDoc N.D c).1.soft).map
        (fun x => VE.NormDefaults.Wire.cohPremiseU (choiceU N c) (choiceDoc N.D c).1.soft x.1 x.2)) := by
  have hX := fillLite_of_uvalid (VE.NormDefaults.uvalid hsu)
  have hY := fillLite_choiceSD hh hc hN hsu
  have hvX := valid_fill_supU hsu
  have hvY := valid_fill_choiceSD hh hc hN hsu
  have hsv := sup_softValid hh
  have hcX : VE.Norms.ConstantsTyped (fill (supU N)) B := hB.1.1
  have hcB : ∀ x s, (fill (supU N)).E.constants x = some s → ∃ v, B.constant x = some v :=
    fun x s hx => (hcX x s hx).imp fun _ h => h.1
  have hcY : VE.Norms.ConstantsTyped (fill (choiceU N c)) (pullF N c B) := fun x s hx =>
    hcX x s (constants_choiceSD hh x s hx)
  have tp : ∀ ss (vs : List B.Carrier), VE.TupleTyped (pullF N c B) ss vs ↔ VE.TupleTyped B ss vs :=
    fun ss vs => VE.Norms.tupleTyped_relation B _ _ vs
  have hS := encodes_canon_fill hh hsu B he
  let selX := fun (K : SoftNode) (vs : List B.Carrier) => VE.SoftNorms.SelectsSoftD (sup N.D).1.soft
    (canon (fill (supU N)) B) (VE.Norms.tupleVal vs) (VE.SoftNorms.fuel (sup N.D).1.soft) K
  let selY := fun (K : SoftNode) (vs : List B.Carrier) => VE.SoftNorms.SelectsSoftD (choiceDoc N.D c).1.soft
    (canon (fill (choiceU N c)) (pullF N c B)) (VE.Norms.tupleVal vs) (VE.SoftNorms.fuel (choiceDoc N.D c).1.soft) K
  have F1 : ∀ K ∈ (sup N.D).1.soft.T.nodes, ∀ vs, VE.TupleTyped B (VE.SoftNorms.sortsOf (sup N.D).1.soft K.pred) vs →
      ((VE.Defaults.selU (supU N) (sup N.D).1.soft K).denote B (VE.Norms.tupleVal vs) ↔ selX K vs) :=
    fun K hK vs hvs => selU_canon (supU_D hh) hX hvX hcX hK (hsv.predReg K hK) vs hvs
  have F2 : ∀ M ∈ (choiceDoc N.D c).1.soft.T.nodes, ∀ vs,
      VE.TupleTyped B (VE.SoftNorms.sortsOf (choiceDoc N.D c).1.soft M.pred) vs →
      ((VE.Defaults.selU (choiceU N c) (choiceDoc N.D c).1.soft M).denote (pullF N c B) (VE.Norms.tupleVal vs) ↔
        selY M vs) := by
    intro M hM vs hvs
    have hreg := hsv.predReg _ (fmap_mem hh c hM)
    rw [(fmap_fields hh c hM).1, sup_reg, ← choice_reg c] at hreg
    exact selU_canon (choiceU_D hh c) hY hvY hcY hM hreg vs ((tp _ vs).mpr hvs)
  have F3 : ∀ M ∈ (choiceDoc N.D c).1.soft.T.nodes, ∀ vs, selX (fmap N.D c M) vs ↔ selY M vs := by
    intro M hM vs
    refine (sim_selects_fuel (faithful_sim hh hc _ hS (VE.Norms.tupleVal vs)) M hM).trans ?_
    show _ ↔ VE.SoftNorms.SelectsSoftD (choiceDoc N.D c).1.soft (canon (fill (choiceU N c)) (pullF N c B))
      (VE.Norms.tupleVal vs) (VE.SoftNorms.fuel (choiceDoc N.D c).1.soft) M
    rw [← VE.SoftNorms.selectsPrime_denote, ← VE.SoftNorms.selectsPrime_denote]
    refine denote_relation_congr _ (pull N.D c (canon (fill (supU N)) B)) (canon (fill (choiceU N c)) (pullF N c B)).relation
      (fun p ss hp ws hws => ?_) _ _ _ ((VE.check_iff_wellFormed _ _ _).mpr (choice_selTyped hh hc hM))
    have hp' := envAt_sub hp
    refine (pull_pullF hh (c := c) (canon (fill (supU N)) B) hp' ws).trans (pullF_canon hh hc hN hsu B hcB he ?_ ws hws)
    rw [← choiceU_D hh] at hp'
    rw [VE.NormDefaults.fill_E, VE.NormDefaults.fillEnv_off _ (not_unsaid_lite hY hp')]; exact hp'
  have F4 : ∀ K ∈ (sup N.D).1.soft.T.nodes, (∀ M ∈ (choiceDoc N.D c).1.soft.T.nodes, fmap N.D c M ≠ K) →
      ∀ vs, ¬ selX K vs := by
    intro K hK hext vs hsel
    have hdead := dead_extra hh hc _ hS (VE.Norms.tupleVal vs) hK hext
    have ha := hsel.1
    unfold VE.SoftNorms.AppliesSoftD at ha
    split at ha
    · exact hdead ha
    · exact hdead (effD_eligible ha).2.1
  have hinc : ∀ M ∈ (choiceDoc N.D c).1.soft.T.nodes, ∀ M' ∈ (choiceDoc N.D c).1.soft.T.nodes,
      VE.SoftNorms.Incompatible (sup N.D).1.soft (fmap N.D c M) (fmap N.D c M') =
        VE.SoftNorms.Incompatible (choiceDoc N.D c).1.soft M M' :=
    fun M hM M' hM' => sim_incompatible (faithful_sim hh hc _ hS []) M M' hM hM'
  have hss : ∀ M ∈ (choiceDoc N.D c).1.soft.T.nodes, VE.SoftNorms.sortsOf (sup N.D).1.soft (fmap N.D c M).pred =
      VE.SoftNorms.sortsOf (choiceDoc N.D c).1.soft M.pred := fun M hM => by rw [(fmap_fields hh c hM).1, sortsOf_eq c]
  simp only [Sat, List.forall_mem_map, VE.Defaults.cohPremiseU_selU, VE.Norms.bindAll_denote_nil, VE.SoftNorms.actSorts]
  constructor
  · rintro hXc ⟨M, M'⟩ hMM' vs hvs ⟨h1, h2⟩
    obtain ⟨hM, hM', hMd, hM'd, hlt, hi⟩ := VE.SoftNorms.mem_collidingPairs.mp hMM'
    have hvs' := (tp _ vs).mp hvs
    have hne : (fmap N.D c M).name ≠ (fmap N.D c M').name := fun h => by
      have := fmap_inj hh c hM hM' (sup_name_inj hh (fmap_mem hh c hM) (fmap_mem hh c hM') h)
      subst this; exact absurd hlt (String.lt_irrefl _)
    have hdM : (fmap N.D c M).mode = .default := by rw [(fmap_fields hh c hM).2.2.1]; exact hMd
    have hdM' : (fmap N.D c M').mode = .default := by rw [(fmap_fields hh c hM').2.2.1]; exact hM'd
    have s1 := (F3 M hM vs).mpr ((F2 M hM vs hvs').mp h1)
    rcases VE.SoftNorms.str_lt_or_gt _ _ hne with hl | hl
    · have hp := VE.SoftNorms.mem_collidingPairs.mpr ⟨fmap_mem hh c hM, fmap_mem hh c hM', hdM, hdM', hl,
        by rw [hinc M hM M' hM']; exact hi⟩
      have hsrt := hsv.cpSorts _ hp
      have hv1 : VE.TupleTyped B (VE.SoftNorms.sortsOf (sup N.D).1.soft (fmap N.D c M).pred) vs := by
        rw [hss M hM]; exact hvs'
      have hv2 : VE.TupleTyped B (VE.SoftNorms.sortsOf (choiceDoc N.D c).1.soft M'.pred) vs := by
        rw [← hss M' hM', ← hsrt]; exact hv1
      exact hXc _ hp vs hv1 ⟨(F1 _ (fmap_mem hh c hM) vs hv1).mpr s1,
        (F1 _ (fmap_mem hh c hM') vs (hsrt ▸ hv1)).mpr ((F3 M' hM' vs).mpr ((F2 M' hM' vs hv2).mp h2))⟩
    · have hp := VE.SoftNorms.mem_collidingPairs.mpr ⟨fmap_mem hh c hM', fmap_mem hh c hM, hdM', hdM, hl,
        by rw [hinc M' hM' M hM, VE.SoftNorms.incompatible_symm]; exact hi⟩
      have hsrt := hsv.cpSorts _ hp
      have hv1 : VE.TupleTyped B (VE.SoftNorms.sortsOf (sup N.D).1.soft (fmap N.D c M).pred) vs := by
        rw [hss M hM]; exact hvs'
      have hv2 : VE.TupleTyped B (VE.SoftNorms.sortsOf (sup N.D).1.soft (fmap N.D c M').pred) vs := by
        rw [hsrt]; exact hv1
      exact hXc _ hp vs hv2 ⟨(F1 _ (fmap_mem hh c hM') vs hv2).mpr ((F3 M' hM' vs).mpr ((F2 M' hM' vs
        (by rw [← hss M' hM']; exact hv2)).mp h2)), (F1 _ (fmap_mem hh c hM) vs hv1).mpr s1⟩
  · rintro hYc ⟨P, Q⟩ hPQ vs hvs ⟨h1, h2⟩
    obtain ⟨hP, hQ, hPd, hQd, hlt, hi⟩ := VE.SoftNorms.mem_collidingPairs.mp hPQ
    have hsrt := hsv.cpSorts _ hPQ
    have s1 := (F1 P hP vs hvs).mp h1
    have s2 := (F1 Q hQ vs (by rw [← hsrt]; exact hvs)).mp h2
    have im : ∀ K ∈ (sup N.D).1.soft.T.nodes, selX K vs → ∃ M ∈ (choiceDoc N.D c).1.soft.T.nodes, fmap N.D c M = K :=
      fun K hK hs => Classical.byContradiction fun hn =>
        F4 K hK (fun M hM h => hn ⟨M, hM, h⟩) vs hs
    obtain ⟨M, hM, rfl⟩ := im P hP s1
    obtain ⟨M', hM', rfl⟩ := im Q hQ s2
    have hvY : VE.TupleTyped B (VE.SoftNorms.sortsOf (choiceDoc N.D c).1.soft M.pred) vs := by
      rw [← hss M hM]; exact hvs
    have hvY' : VE.TupleTyped B (VE.SoftNorms.sortsOf (choiceDoc N.D c).1.soft M'.pred) vs := by
      rw [← hss M' hM', ← hsrt]; exact hvs
    have t1 := (F2 M hM vs hvY).mpr ((F3 M hM vs).mp s1)
    have t2 := (F2 M' hM' vs hvY').mpr ((F3 M' hM' vs).mp s2)
    have hMd : M.mode = .default := by rw [← (fmap_fields hh c hM).2.2.1]; exact hPd
    have hM'd : M'.mode = .default := by rw [← (fmap_fields hh c hM').2.2.1]; exact hQd
    have hne : M.name ≠ M'.name := fun h => by
      have : M = M' := choice_name_inj hh c hM hM' h
      subst this; exact absurd hlt (String.lt_irrefl _)
    rcases VE.SoftNorms.str_lt_or_gt _ _ hne with hl | hl
    · exact hYc _ (VE.SoftNorms.mem_collidingPairs.mpr ⟨hM, hM', hMd, hM'd, hl, by rw [← hinc M hM M' hM']; exact hi⟩)
        vs ((tp _ vs).mpr hvY) ⟨t1, t2⟩
    · exact hYc _ (VE.SoftNorms.mem_collidingPairs.mpr ⟨hM', hM, hM'd, hMd, hl,
        by rw [← hinc M' hM' M hM, VE.SoftNorms.incompatible_symm]; exact hi⟩) vs ((tp _ vs).mpr hvY') ⟨t2, t1⟩

end Coh

/-- `supX` transfers at an encoded filled base: a non-chosen candidate's premise holds by its bit or, for a necessary
    condition, by the slot's quiet premise. -/
theorem supX_pull (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c)
    (B : VE.Structure.{u}) (hB : VE.Norms.BaseAdmissible (fill (supU N)) B) (hsl : Sat B (slotP N.D))
    (he : Encodes N.D c B) :
    Sat B (supX N) ↔ Sat (pullF N c B) (choiceX N c) := by
  have hh := hyps_sd hN hs
  have e1 : supX N = VE.Defaults.softX (supU N) (correlate (sup N.D).1) [] := by
    simp [supX, softX, softXL, VE.Defaults.softX, supU]
  have e2 : choiceX N c = VE.Defaults.softX (choiceU N c) (correlate (choiceDoc N.D c).1) [] := by
    simp [choiceX, softX, softXL, VE.Defaults.softX, choiceU]
  rw [e1, e2, VE.Defaults.softX_eq, VE.Defaults.softX_eq, sup_correlate hh, choice_correlate hh,
    List.append_nil, List.append_nil]
  simp only [Sat, List.forall_mem_append]
  exact and_congr (exc_pullF hh hc he hsl) (coh_pullF hh hc hN hsu hB he)

/-! ## Superposition (13.3)

Down: a base of the filled superposed document under `A` encodes one compatible choice taking `A`
(`encodes_unique_slot`, `encodes_atoms`); its filled pull is a base of that choice's filled document (`pullF_admissible`,
`fillPremisesSD_pull`, `supX_pull`), and the two conflict-freedoms agree there (`conflictFree_pullF`, through
`fill_sim`). Up: a base of a choice's filled document with an element is lifted by S2a's `upB`, applied to the base
with its `unsaid__` tables emptied (`dropUnsaid`) so that S2a's lemmas apply; the third disjunct of `upRel` keeps the
tables, so the lift is a base of the filled superposed document (`upB_admissibleF`) and its filled pull is the base it
was lifted from (`pullF_upB`). -/

open VE.SoftNorms (envPrime decisionNames)
open VE.NormDefaults (unsaidNames)

section Down
variable {N : NDoc} (hh : Hyps N.D) {c : Choice}
include hh

theorem sortsOf_choiceU (p : String) :
    VE.NormDefaults.sortsOf (choiceU N c).D p = VE.NormDefaults.sortsOf (supU N).D p := by
  unfold VE.NormDefaults.sortsOf; rw [choiceU_D hh, supU_D hh]; simp only [soften]; rw [regs_eq c]

/-- `nameMap` carries the filled choice's vocabulary into the filled superposed document's. -/
theorem fullF_nameMap {p : String} {ss : List String} (hp : (fill (choiceU N c)).E.predicates p = some ss) :
    (fill (supU N)).E.predicates (nameMap N.D c p) = some ss := by
  rw [VE.NormDefaults.fill_E] at hp ⊢
  by_cases hu : p ∈ unsaidNames (choiceU N c)
  · obtain ⟨q, hq, rfl⟩ := List.mem_map.mp hu
    rw [VE.NormDefaults.fillEnv_unsaid _ hq] at hp
    rw [nameMap_unsaid hh, VE.NormDefaults.fillEnv_unsaid (supU N) hq, ← sortsOf_choiceU hh]; exact hp
  · rw [VE.NormDefaults.fillEnv_off _ hu, choiceU_D hh, soften_E] at hp
    have hn : nameMap N.D c p ∉ unsaidNames (supU N) := by
      intro h
      obtain ⟨q, hq, he⟩ := List.mem_map.mp h
      by_cases hd : p ∈ decisionNames (choiceDoc N.D c).1.soft
      · exact unsaid_not_decision _ q (he ▸ nameMap_decision hh c hd)
      · rw [nameMap_nondecision hh c hd] at he; exact hu (List.mem_map.mpr ⟨q, hq, he⟩)
    rw [VE.NormDefaults.fillEnv_off _ hn, supU_D hh, soften_E]
    exact envPrime_nameMap hh c hp

theorem pullF_admissible (hc : Compatible N.D c) (hN : WellFormedSD N = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (B : VE.Structure.{u})
    (hadm : B.Admissible (envAt (fill (supU N)) 0)) :
    (pullF N c B).Admissible (envAt (fill (choiceU N c)) 0) := by
  refine ⟨fun x s hx => hadm.1 x s (constants_choiceSD hh x s hx), ?_⟩
  rintro p vs ⟨hne, hrel⟩
  obtain ⟨ss', hss', htt⟩ := hadm.2 _ _ hrel
  by_cases hpl : p ∈ layerNames (fill (choiceU N c)).T
  · exfalso
    rw [layerNames_fill_lite (fillLite_choiceSD hh hc hN hsu), choiceU_D hh] at hpl
    obtain ⟨q, hq, rfl⟩ := List.mem_map.mp hpl
    rw [nameMap_frame hh c (by rw [choice_sym_frame hh c hq]; simp)] at hss'
    have hl : q.name ∈ layerNames (fill (supU N)).T := by
      rw [layerNames_fill_lite (fillLite_of_uvalid (VE.NormDefaults.uvalid hsu)), supU_D hh]
      exact (layer_iff hh hc _).mp hpl
    have : (envAt (fill (supU N)) 0).predicates q.name = none := by simp [envAt, VE.Norms.hide, hl]
    rw [this] at hss'; cases hss'
  · rw [envAt_size_pred] at hne
    obtain ⟨ss, hss⟩ := Option.ne_none_iff_exists'.mp hne
    have h3 := (envAt_sub hss').symm.trans (fullF_nameMap hh hss)
    cases h3
    exact ⟨ss', by rw [VE.Norms.envAt_base hpl]; exact hss, (VE.Norms.tupleTyped_relation B _ _ vs).mpr htt⟩

theorem pullF_literals (B : VE.Structure.{u}) (hl : Sat B (VE.Norms.backgroundBase (fill (supU N)))) :
    Sat (pullF N c B) (VE.Norms.backgroundBase (fill (choiceU N c))) := by
  have e : (fill (choiceU N c)).lits = (fill (supU N)).lits := by
    rw [VE.NormDefaults.fill_lits, VE.NormDefaults.fill_lits, choiceU_D hh, supU_D hh]
    show (build N.D (fun _ => true) (pickC c)).1.soft.lits = (sup N.D).1.soft.lits
    rw [(build_shape N.D (fun _ => true) (pickC c)).lits, (sup_shape N.D).lits]; rfl
  intro a ha
  unfold VE.Norms.backgroundBase at ha
  rw [e] at ha
  have := hl a ha
  obtain ⟨x, _, rfl⟩ := List.mem_map.mp ha
  exact this
end Down

theorem conflict_fill_v {U : VE.NormDefaults.UDoc} (hv : Valid (fill U)) {B : VE.Structure.{u}}
    (hc : VE.Norms.ConstantsTyped (fill U) B) {r : Regulated} (hr : r ∈ U.D.T.regulated) (vs : List B.Carrier)
    (hvs : VE.TupleTyped B r.sorts vs) :
    (VE.Norms.conflict (fill U) r).denote B (VE.Norms.tupleVal vs) ↔
      DecidesD (fill U).T (canon (fill U) B) (VE.Norms.tupleVal vs) r.name true ∧
        DecidesD (fill U).T (canon (fill U) B) (VE.Norms.tupleVal vs) r.name false := by
  have hk := VE.Norms.index_before hv (show r ∈ (fill U).T.regulated from hr)
  have hT := VE.Norms.rulesTyped_of_valid hv hk
  have hρ := VE.Norms.tupleVal_typed B _ vs hvs
  simp only [VE.Norms.conflict, VE.Norms.pos, VE.Norms.neg, VE.Formula.denote]
  rw [VE.SoftNorms.canon_subst hv B hc _ _ _ (VE.Norms.decides_wellFormed hT true) _ hρ,
    VE.SoftNorms.canon_subst hv B hc _ _ _ (VE.Norms.decides_wellFormed hT false) _ hρ,
    VE.Norms.decides_denote, VE.Norms.decides_denote]


theorem unsaid_not_bit (D : Doc) (q : String) : ¬ IsBit D (unsaidName q) := by
  rintro ⟨m, j, _, _, h⟩
  have h1 : (unsaidName q).data.head? = some 'u' := by simp [unsaidName, String.data_append]
  rw [h] at h1; simp [bitName, String.data_append] at h1

/-- A base with its `unsaid__` tables emptied: what S2a's lift reads of a filled choice base. -/
def dropUnsaid (N : NDoc) (B : VE.Structure.{u}) : VE.Structure.{u} :=
  { B with relation := fun p vs => p ∉ N.unspec.map unsaidName ∧ B.relation p vs }

theorem envAt_fill_off_lite {U : VE.NormDefaults.UDoc} (hu : FillLite U) (k : Nat) {p : String}
    (hp : p ∉ unsaidNames U) : (envAt (fill U) k).predicates p = (envAt U.D k).predicates p := by
  simp only [envAt, VE.Norms.hide, layerNames_fill_lite hu]
  split
  · rfl
  · rw [VE.NormDefaults.fill_E, VE.NormDefaults.fillEnv_off U hp]

section Up
variable {N : NDoc} (hh : Hyps N.D) {c : Choice} (hc : Compatible N.D c) (hN : WellFormedSD N = true)
  (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (B₀ : VE.Structure.{u}) (e : B₀.Carrier)
  (hadm : B₀.Admissible (envAt (fill (choiceU N c)) 0))
include hh hc hN hsu hadm

theorem dropUnsaid_admissible :
    (dropUnsaid N B₀).Admissible (envAt (soften (choiceDoc N.D c).1.soft) 0) := by
  refine ⟨fun x s hx => hadm.1 x s (by
    show (fillEnv (choiceU N c)).constants x = some s
    rw [VE.NormDefaults.fillEnv_constants, choiceU_D hh]; exact hx), ?_⟩
  rintro p vs ⟨hp, hb⟩
  obtain ⟨ss, hss, htt⟩ := hadm.2 p vs hb
  rw [envAt_fill_off_lite (fillLite_choiceSD hh hc hN hsu) 0 hp, choiceU_D hh] at hss
  exact ⟨ss, hss, (VE.Norms.tupleTyped_relation B₀ _ _ vs).mpr htt⟩

/-- S2a's lift is admissible for the filled superposed document's base vocabulary. -/
theorem upB_admissibleF : (upB N.D c B₀ e).Admissible (envAt (fill (supU N)) 0) := by
  have hX := fillLite_of_uvalid (VE.NormDefaults.uvalid hsu)
  have hr := upB_admissible hh hc (dropUnsaid N B₀) e (dropUnsaid_admissible hh hc hN hsu B₀ hadm)
  have hmono := fun p ss (h : (envAt (soften (sup N.D).1.soft) 0).predicates p = some ss) =>
    envAt_fill_mono_lite hX 0 p ss (by rw [supU_D hh]; exact h)
  refine ⟨fun x s hx => hr.1 x s (by
    show (soften (sup N.D).1.soft).E.constants x = some s
    rw [← supU_D hh]; exact hx), ?_⟩
  intro p vs hrel
  by_cases hp : p ∈ N.unspec.map unsaidName
  · obtain ⟨q, hq, rfl⟩ := List.mem_map.mp hp
    rcases hrel with ⟨h, _⟩ | ⟨_, hd, _⟩ | ⟨_, _, _, hb⟩
    · exact absurd (onBit_isBit h) (unsaid_not_bit _ q)
    · exact absurd hd (unsaid_not_decision _ q)
    · obtain ⟨ss, hss, htt⟩ := hadm.2 _ vs hb
      have h1 := envAt_sub hss
      rw [VE.NormDefaults.fill_E, VE.NormDefaults.fillEnv_unsaid _ hq, sortsOf_choiceU hh] at h1
      cases h1
      refine ⟨_, ?_, tt_up htt⟩
      rw [VE.Norms.envAt_base (fun hl => ?_), VE.NormDefaults.fill_E, VE.NormDefaults.fillEnv_unsaid _ hq]
      rw [layerNames_fill_lite hX] at hl
      obtain ⟨r, hr', he⟩ := List.mem_map.mp hl
      have := (hX.valid.decl r hr').1
      rw [he, hX.unsaid q hq] at this; cases this
  · have hrel' : (upB N.D c (dropUnsaid N B₀) e).relation p vs := by
      rcases hrel with h | ⟨h1, h2, q, hq, hqe, hb⟩ | ⟨h1, h2, h3, hb⟩
      · exact Or.inl h
      · refine Or.inr (Or.inl ⟨h1, h2, q, hq, hqe, ⟨fun hu => ?_, hb⟩⟩)
        obtain ⟨q', _, rfl⟩ := List.mem_map.mp hu
        exact unsaid_not_decision _ q' hq
      · exact Or.inr (Or.inr ⟨h1, h2, h3, hp, hb⟩)
    obtain ⟨ss, hss, htt⟩ := hr.2 p vs hrel'
    exact ⟨ss, hmono p ss hss, (VE.Norms.tupleTyped_relation (upB N.D c (dropUnsaid N B₀) e) (upRel N.D c B₀ e) ss vs).mpr htt⟩

/-- Pulled back with `pullF`, the lift is the base it was lifted from, `unsaid__` tables included. -/
theorem pullF_upB (p : String) (vs : List B₀.Carrier) :
    (pullF N c (upB N.D c B₀ e)).relation p vs ↔ B₀.relation p vs := by
  have hY := fillLite_choiceSD hh hc hN hsu
  by_cases hp : p ∈ N.unspec.map unsaidName
  · obtain ⟨q, hq, rfl⟩ := List.mem_map.mp hp
    refine (pullF_unsaid hh (c := c) (upB N.D c B₀ e) hq vs).trans ⟨?_, fun hb => ?_⟩
    · rintro (⟨h, _⟩ | ⟨_, hd, _⟩ | ⟨_, _, _, hb⟩)
      · exact absurd (onBit_isBit h) (unsaid_not_bit _ q)
      · exact absurd hd (unsaid_not_decision _ q)
      · exact hb
    · exact Or.inr (Or.inr ⟨unsaid_not_bit _ q, unsaid_not_decision _ q, unsaid_not_decision _ q, hb⟩)
  · have hpu := pull_upB hh c (dropUnsaid N B₀) e (dropUnsaid_admissible hh hc hN hsu B₀ hadm) p vs
    have hfull : (envAt (fill (choiceU N c)) (size (fill (choiceU N c)))).predicates p =
        (choiceEnvFull N.D c).predicates p := by
      rw [envAt_size_pred, VE.NormDefaults.fill_E, VE.NormDefaults.fillEnv_off _ hp, choiceU_D hh,
        choiceEnvFull_eq hh c]; rfl
    have hnm : nameMap N.D c p ∉ N.unspec.map unsaidName := by
      intro h
      obtain ⟨q, hq, he⟩ := List.mem_map.mp h
      by_cases hd : p ∈ decisionNames (choiceDoc N.D c).1.soft
      · exact unsaid_not_decision _ q (he ▸ nameMap_decision hh c hd)
      · rw [nameMap_nondecision hh c hd] at he; exact hp (List.mem_map.mpr ⟨q, hq, he⟩)
    have hrel : ∀ q, q ∉ N.unspec.map unsaidName → (upRel N.D c B₀ e q vs ↔ upRel N.D c (dropUnsaid N B₀) e q vs) := by
      intro q hq
      refine or_congr Iff.rfl (or_congr ?_ ?_)
      · refine and_congr_right fun _ => and_congr_right fun _ => exists_congr fun q' => and_congr_right fun hq' =>
          and_congr_right fun _ => ⟨fun hb => ⟨fun hu => ?_, hb⟩, fun h => h.2⟩
        obtain ⟨q'', _, rfl⟩ := List.mem_map.mp hu
        exact unsaid_not_decision _ q'' hq'
      · exact and_congr_right fun _ => and_congr_right fun _ => and_congr_right fun _ =>
          ⟨fun hb => ⟨hq, hb⟩, fun h => h.2⟩
    show (_ ≠ none ∧ upRel N.D c B₀ e (nameMap N.D c p) vs) ↔ _
    rw [hfull, hrel _ hnm]
    exact hpu.trans ⟨fun h => h.2, fun h => ⟨hp, h⟩⟩

/-- A formula over the filled choice's vocabulary reads the pulled lift as it reads `B₀`. -/
theorem pullF_up (φ : VE.Formula) (Γ : List String)
    (hφ : φ.WellFormed (envAt (fill (choiceU N c)) (size (fill (choiceU N c)))) Γ) (ρ : VE.Valuation B₀) :
    φ.denote (pullF N c (upB N.D c B₀ e)) ρ ↔ φ.denote B₀ ρ :=
  ext_denote (E := envAt (fill (choiceU N c)) (size (fill (choiceU N c)))) (S := B₀)
    (by show "ve__reading" ∉ (fillEnv (choiceU N c)).sorts
        rw [VE.NormDefaults.fillEnv_sorts, choiceU_D hh, soften_E, envPrime_sorts, choice_E c]
        exact frame_sorts_free hh.wf)
    (by show (fillEnv (choiceU N c)).constants "ve__here" = none
        rw [VE.NormDefaults.fillEnv_constants, choiceU_D hh, soften_E, envPrime_constants, choice_E c]
        exact frame_here hh)
    (pullF N c (upB N.D c B₀ e)).relation (upDom B₀) (upConst B₀ e)
    (fun p _ _ vs => pullF_upB hh hc hN hsu B₀ e hadm p vs)
    (fun σ hσ => by show (if σ = "ve__reading" then _ else _) = _; exact if_neg hσ)
    (fun x hx => by show (if x = "ve__here" then _ else _) = _; exact if_neg hx) φ Γ ρ hφ


/-- `choiceX` reads the pulled lift as it reads `B₀`: an exception premise through the frame, a coherence premise
    through its selections' types. -/
theorem choiceX_up : Sat (pullF N c (upB N.D c B₀ e)) (choiceX N c) ↔ Sat B₀ (choiceX N c) := by
  have hvY := valid_fill_choiceSD hh hc hN hsu
  have hsv := sup_softValid hh
  have e2 : choiceX N c = VE.Defaults.softX (choiceU N c) (correlate (choiceDoc N.D c).1) [] := by
    simp [choiceX, softX, softXL, VE.Defaults.softX, choiceU]
  have tt : ∀ p (vs : List B₀.Carrier), VE.TupleTyped (pullF N c (upB N.D c B₀ e))
      (VE.SoftNorms.sortsOf (choiceDoc N.D c).1.soft p) vs ↔
      VE.TupleTyped B₀ (VE.SoftNorms.sortsOf (choiceDoc N.D c).1.soft p) vs :=
    fun p vs => (VE.Norms.tupleTyped_relation (upB N.D c B₀ e) _ _ vs).trans ⟨tt_down (sortsY_free hh hc p), tt_up⟩
  have hat : ∀ (n : String) ss (ρ : VE.Valuation B₀),
      (VE.Norms.atom n ss).denote (pullF N c (upB N.D c B₀ e)) ρ ↔ (VE.Norms.atom n ss).denote B₀ ρ := by
    intro n ss ρ; unfold VE.Norms.atom; split
    · exact exists_congr fun v => and_congr_right fun _ => pullF_upB hh hc hN hsu B₀ e hadm _ _
    · exact exists_congr fun v => exists_congr fun w => and_congr_right fun _ => and_congr_right fun _ =>
        pullF_upB hh hc hN hsu B₀ e hadm _ _
    · exact Iff.rfl
  rw [e2, VE.Defaults.softX_eq, choice_correlate hh, List.append_nil]
  simp only [Sat, List.forall_mem_append]
  refine and_congr (forall₂_congr fun a ha => ?_) (forall₂_congr fun a ha => ?_)
  · obtain ⟨M, hM, ha⟩ := List.mem_flatMap.mp ha
    cases hm : M.mode <;> cases hx : M.exception <;> simp only [VE.SoftNorms.excPremisesOf, hm, hx] at ha <;>
      try exact absurd ha List.not_mem_nil
    rename_i ex
    have hC : ∀ C ∈ ex.sufficient ++ ex.necessary, ∀ ρ, C.denote (pullF N c (upB N.D c B₀ e)) ρ ↔ C.denote B₀ ρ := by
      intro C hC ρ
      obtain ⟨Γ, hw⟩ := choice_exc_typed hh c hM hx C hC
      exact (pullF_denote_frame hh (c := c) (upB N.D c B₀ e) C Γ hw ρ).symm.trans (up_frame hh (c := c) B₀ e C Γ hw ρ)
    rcases List.mem_append.mp ha with h | h <;> obtain ⟨C, hCm, rfl⟩ := List.mem_map.mp h <;>
      rw [VE.Norms.bindAll_denote_nil, VE.Norms.bindAll_denote_nil] <;>
      refine forall_congr' fun vs => imp_congr (tt _ vs) ?_ <;> simp only [VE.Formula.denote, VE.SoftNorms.exceptedF]
    · rw [hC C (List.mem_append_left _ hCm), hat]
    · rw [hC C (List.mem_append_right _ hCm), hat]
  · obtain ⟨⟨M, K⟩, hMK, rfl⟩ := List.mem_map.mp ha
    obtain ⟨hM, hK, -⟩ := VE.SoftNorms.mem_collidingPairs.mp hMK
    have hsel : ∀ K ∈ (choiceDoc N.D c).1.soft.T.nodes, ∀ ρ,
        (VE.Defaults.selU (choiceU N c) (choiceDoc N.D c).1.soft K).denote (pullF N c (upB N.D c B₀ e)) ρ ↔
          (VE.Defaults.selU (choiceU N c) (choiceDoc N.D c).1.soft K).denote B₀ ρ := by
      intro K hK ρ
      have hreg := hsv.predReg _ (fmap_mem hh c hK)
      rw [(fmap_fields hh c hK).1, sup_reg, ← choice_reg c] at hreg
      exact pullF_up hh hc hN hsu B₀ e hadm _ _ (VE.Norms.envAt_mono (Nat.zero_le _) _ _
        (VE.Norms.subst_wellFormed hvY _ _ _ (selects_fill_wf (choiceU_D hh c) hvY hK hreg))) ρ
    rw [VE.Defaults.cohPremiseU_selU, VE.Norms.bindAll_denote_nil, VE.Norms.bindAll_denote_nil]
    refine forall_congr' fun vs => imp_congr (tt _ vs) ?_
    simp only [VE.Formula.denote]
    rw [hsel M hM, hsel K hK]

end Up
/-- Conflict-freedom transfers at an encoded filled base (`superpose_conflict_iff` through `fill`). -/
theorem conflictFree_pullF (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c)
    (B : VE.Structure.{u}) (hB : VE.Norms.BaseAdmissible (fill (supU N)) B) (hsl : Sat B (slotP N.D))
    (he : Encodes N.D c B) :
    VE.Norms.ConflictFree (fill (supU N)) B ↔ VE.Norms.ConflictFree (fill (choiceU N c)) (pullF N c B) := by
  have hh := hyps_sd hN hs
  have hcY : VE.Norms.ConstantsTyped (fill (choiceU N c)) (pullF N c B) := fun x s hx =>
    hB.1.1 x s (constants_choiceSD hh x s hx)
  have hregX : (supU N).D.T.regulated = N.D.frame.soft.T.regulated := by rw [supU_D hh]; exact sup_reg
  have hregY : (choiceU N c).D.T.regulated = N.D.frame.soft.T.regulated := by rw [choiceU_D hh]; exact choice_reg c
  have tp : ∀ ss (vs : List B.Carrier), VE.TupleTyped B ss vs ↔ VE.TupleTyped (pullF N c B) ss vs :=
    fun ss vs => (VE.Norms.tupleTyped_relation B _ _ vs).symm
  have hconf : ∀ r ∈ (supU N).D.T.regulated, ∀ vs : List B.Carrier, VE.TupleTyped B r.sorts vs →
      ((VE.Norms.conflict (fill (supU N)) r).denote B (VE.Norms.tupleVal vs) ↔
        (VE.Norms.conflict (fill (choiceU N c)) r).denote (pullF N c B) (VE.Norms.tupleVal vs)) := by
    intro r hr vs hvs
    have hrf : r ∈ N.D.frame.soft.T.regulated := hregX ▸ hr
    rw [conflict_fill_v (valid_fill_supU hsu) hB.1.1 hr vs hvs,
      conflict_fill_v (valid_fill_choiceSD hh hc hN hsu) hcY (hregY ▸ hrf) vs ((tp _ vs).mp hvs),
      fill_sim N hN hs hsu c hc B hB hsl he r hrf _ true, fill_sim N hN hs hsu c hc B hB hsl he r hrf _ false]
  have hpair : ∀ pr ∈ VE.Norms.pairs (supU N).D.T, ∀ vs : List B.Carrier, VE.TupleTyped B pr.sorts vs →
      ((VE.Norms.pairConflict (fill (supU N)) pr).denote B (VE.Norms.tupleVal vs) ↔
        (VE.Norms.pairConflict (fill (choiceU N c)) pr).denote (pullF N c B) (VE.Norms.tupleVal vs)) := by
    intro pr hpr vs hvs
    obtain ⟨r, hr, hrn, _, _, hrs⟩ := VE.NormDefaults.pair_req hpr
    obtain ⟨m, hm, hmn, _, hms⟩ := VE.NormDefaults.pair_perm (VE.NormDefaults.uvalid hsu) hpr
    simp only [VE.Norms.pairConflict, VE.Formula.denote]
    rw [← hrn, ← hmn, outcome_pullF N hN hs hsu c hc B hB hsl he hr vs (hrs ▸ hvs),
      outcome_pullF N hN hs hsu c hc B hB hsl he hm vs (hms ▸ hvs)]
  have hreg : (fill (choiceU N c)).T.regulated = (fill (supU N)).T.regulated := hregY.trans hregX.symm
  have hpairs : VE.Norms.pairs (fill (choiceU N c)).T = VE.Norms.pairs (supU N).D.T := by
    unfold VE.Norms.pairs; rw [hreg]; rfl
  unfold VE.Norms.ConflictFree
  rw [hpairs, hreg]
  constructor
  · rintro ⟨h1, h2⟩
    exact ⟨fun r hr vs hvs hx => h1 r hr vs ((tp _ vs).mpr hvs) ((hconf r hr vs ((tp _ vs).mpr hvs)).mpr hx),
      fun pr hpr vs hvs hx => h2 pr hpr vs ((tp _ vs).mpr hvs) ((hpair pr hpr vs ((tp _ vs).mpr hvs)).mpr hx)⟩
  · rintro ⟨h1, h2⟩
    exact ⟨fun r hr vs hvs hx => h1 r hr vs ((tp _ vs).mp hvs) ((hconf r hr vs hvs).mp hx),
      fun pr hpr vs hvs hx => h2 pr hpr vs ((tp _ vs).mp hvs) ((hpair pr hpr vs hvs).mp hx)⟩


/-- Superposition under the soft completion: CONFLICT-FREE under `A` exactly when every compatible choice taking
    `A` is, each read with its own `X` and `Fill_T`. -/
theorem sd_superpose_conflict_free (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (A : Choice)
    (hA : ∀ x ∈ A, (candidate N.D x.1 x.2).isSome) :
    VE.NormDefaults.Wire.ConflictFreeX.{u} (supU N) (slotUnder N.D A ++ supX N) ↔
      ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) → VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU N c) (choiceX N c) := by
  have hh := hyps_sd hN hs
  constructor
  · intro hcf c hc hAc B₀ hB₀
    have hvY := valid_fill_choiceSD hh hc hN hsu
    by_cases hne : Nonempty B₀.Carrier
    · obtain ⟨e⟩ := hne
      obtain ⟨⟨⟨hadm, hlit⟩, hfill⟩, hX⟩ := hB₀
      have hcm : complete N.D c = true := by
        simp only [Compatible, compatible, Bool.and_eq_true] at hc; exact hc.1.1
      have henc := upB_encodes hh.ready hc B₀ e
      have hsl := upB_slot hh hc B₀ e
      have hUb : VE.Norms.BaseAdmissible (fill (supU N)) (upB N.D c B₀ e) := by
        refine ⟨upB_admissibleF hh hc hN hsu B₀ e hadm, fun a ha => ?_⟩
        refine upB_literals hh B₀ e (fun a ha => hlit a ?_) a ?_
        · unfold VE.Norms.backgroundBase at ha ⊢; rw [VE.NormDefaults.fill_lits, choiceU_D hh]; exact ha
        · unfold VE.Norms.backgroundBase at ha ⊢; rw [VE.NormDefaults.fill_lits, supU_D hh] at ha; exact ha
      have hup := fun a (hw : a.WellFormed (envAt (fill (choiceU N c)) 0) []) =>
        pullF_up hh hc hN hsu B₀ e hadm a [] (VE.Norms.envAt_mono (Nat.zero_le _) _ _ hw) []
      have hUf : Sat (upB N.D c B₀ e) (VE.NormDefaults.fillPremises (supU N)) :=
        (fillPremisesSD_pull N hN hs hsu c hc _ hUb hsl henc).mpr fun a ha =>
          (hup a (fillPremises_wf_v hvY a ha)).mpr (hfill a ha)
      have hUX : Sat (upB N.D c B₀ e) (supX N) :=
        (supX_pull N hN hs hsu c hc _ hUb hsl henc).mpr ((choiceX_up hh hc hN hsu B₀ e hadm).mpr hX)
      have hY := (conflictFree_pullF N hN hs hsu c hc _ hUb hsl henc).mp (hcf _ ⟨⟨hUb, hUf⟩, fun a ha => by
        rcases List.mem_append.mp ha with ha | ha
        · rcases List.mem_append.mp ha with ha | ha
          · exact hsl a ha
          · exact (encodes_atoms N.D c hcm _ henc A).mpr hAc a ha
        · exact hUX a ha⟩)
      have ttp : ∀ ss (vs : List B₀.Carrier), VE.TupleTyped B₀ ss vs → VE.TupleTyped (pullF N c (upB N.D c B₀ e)) ss vs :=
        fun ss vs h => (VE.Norms.tupleTyped_relation (upB N.D c B₀ e) _ ss vs).mpr (tt_up h)
      refine ⟨fun r hr vs hvs hx => ?_, fun pr hpr vs hvs hx => ?_⟩
      · obtain ⟨k, hk⟩ := VE.Norms.mem_syms_index (hvY.regulated r hr)
        exact hY.1 r hr vs (ttp _ vs hvs) ((pullF_up hh hc hN hsu B₀ e hadm _ _
          (VE.Norms.envAt_mono (Nat.zero_le _) _ _ (VE.Norms.conflict_wellFormed hvY hk)) _).mpr hx)
      · exact hY.2 pr hpr vs (ttp _ vs hvs) ((pullF_up hh hc hN hsu B₀ e hadm _ _
          (VE.Norms.envAt_mono (Nat.zero_le _) _ _ (VE.Norms.pairConflict_wellFormed hvY hpr)) _).mpr hx)
    · exact conflictFree_empty hvY B₀ hne
  · rintro hall B ⟨⟨hBb, hBf⟩, hBX⟩
    have hsl : Sat B (slotP N.D) := fun a ha => hBX a (List.mem_append_left _ (List.mem_append_left _ ha))
    obtain ⟨c, hc, he, _⟩ := encodes_unique_slot N.D hh.wf hh.chain hs B hsl
    have hcm : complete N.D c = true := by
      simp only [Compatible, compatible, Bool.and_eq_true] at hc; exact hc.1.1
    have hAc := (encodes_atoms N.D c hcm B he A).mp
      (fun a ha => hBX a (List.mem_append_left _ (List.mem_append_right _ ha)))
    exact (conflictFree_pullF N hN hs hsu c hc B hBb hsl he).mpr (hall c hc hAc _
      ⟨⟨⟨pullF_admissible hh hc hN hsu B hBb.1, pullF_literals hh B hBb.2⟩,
        (fillPremisesSD_pull N hN hs hsu c hc B hBb hsl he).mp hBf⟩,
       (supX_pull N hN hs hsu c hc B hBb hsl he).mp (fun a ha => hBX a (List.mem_append_right _ ha))⟩)

end VE.Readings
