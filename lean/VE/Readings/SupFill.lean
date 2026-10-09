import VE.Readings.Unspecified
import VE.Readings.ChoiceValid
import VE.NormDefaults.Wire

/-! The lemmas behind `fill_transfers` (docs/spec/readings-defaults.md 6.7, plan RD-6b).

`Fill_T` of a document reads two kinds of decision on its canonical interpretation: the filled tree's (`pairConflict`
on `fill U`) and the author rules' alone (`gapF`, which reads `U.D.T`). For the superposed document `supU N` the
facts `WellFormedU` gives are a hypothesis; for a choice's document `choiceU N c` they are not, and only what the
author-rule lemmas of `fill` read is derived here (`AuthorLite`: no author rule is named `F_p`, and the precedence
graph has no cycle), from the filled choice document S2a shows valid (`choice_valid`, `choice_precedence_acyclic`).

The author rules' decisions of `sup (fillDoc N)` and of a choice's filled document agree at an encoded base through
S2a's simulation restricted to rules not named `F_p` (`sim_authorDecides`): the simulation sends an `F_p` unit to
itself and an author rule to an author rule. The filled decisions agree through the unrestricted simulation, as in
`superpose_situation`. -/
namespace VE.Readings
open VE.Norms (Regulated Sat envAt size Node Tree rulesOn SelectsD DecidesD YieldsD children fuel precedenceNodes
  ConstantsTyped)
open VE.SoftNorms (SoftNode SoftDoc soften canon)
open VE.Rights (RightsDoc correlate)
open VE.NormDefaults (UDoc fill fillName fillRoot fillNode fillNodes)
open VE.Route (DagAcyclic DepEdge DepPath)
universe u

/-! ## The author-rule lemmas of `fill` with only what they read -/

/-- What the author-rule lemmas of `fill` read of `WellFormedU`: no author rule is named `F_p`, and the precedence
    graph of the author tree has no cycle. -/
structure AuthorLite (U : UDoc) : Prop where
  freshRule : ∀ N ∈ U.D.T.nodes, N.name ∉ U.unspec.map fillName
  acyclic : DagAcyclic (precedenceNodes U.D.T)

theorem authorLite_of_uvalid {U : UDoc} (hu : VE.NormDefaults.UValid U) : AuthorLite U :=
  ⟨hu.freshRule, hu.acyclic⟩

section Lite
variable {U : UDoc} (hu : AuthorLite U)
include hu

theorem children_fill_lite {N : Node} (hN : N ∈ U.D.T.nodes) :
    children (fill U).T N = children U.D.T N := by
  have hfresh := hu.freshRule N hN
  unfold children
  congr 1
  rw [VE.NormDefaults.fill_nodes, List.flatMap_append, List.flatMap_map]
  have h₂ : (fillNodes U).flatMap (fun C => if C.pred == N.pred then (C.over.filter (· == N.name)).map
      (fun _ => C) else []) = [] := by
    rw [List.flatMap_eq_nil_iff]
    intro C hC
    obtain ⟨r, _, _, rfl⟩ := VE.NormDefaults.mem_fillNodes.mp hC
    simp [fillNode]
  rw [h₂, List.append_nil]
  apply VE.NormDefaults.flatMap_congr_mem
  intro C _
  rcases VE.NormDefaults.fillRoot_over U C with ⟨hp, ho, ho'⟩ | ⟨_, he⟩
  · simp only [VE.NormDefaults.fillRoot_pred, ho', ho]
    have : (fillName C.pred == N.name) = false := by
      simp only [beq_eq_false_iff_ne]
      intro e
      exact hfresh (List.mem_map.mpr ⟨C.pred, hp, e⟩)
    simp [this]
  · rw [he]

theorem yields_fill_lite (S : VE.Structure.{u}) (ρ : VE.Valuation S) : ∀ (f : Nat) (N : Node), N ∈ U.D.T.nodes →
    (YieldsD (fill U).T S ρ f N ↔ YieldsD U.D.T S ρ f N)
  | 0, _, _ => Iff.rfl
  | f + 1, N, hN => by
    simp only [YieldsD]
    rw [children_fill_lite hu hN]
    apply or_congr_right
    constructor
    · rintro ⟨C, hC, hy⟩
      exact ⟨C, hC, (yields_fill_lite S ρ f C (VE.Norms.mem_children_iff.mp hC).1).mp hy⟩
    · rintro ⟨C, hC, hy⟩
      exact ⟨C, hC, (yields_fill_lite S ρ f C (VE.Norms.mem_children_iff.mp hC).1).mpr hy⟩

theorem yields_fill_fuel_lite (S : VE.Structure.{u}) (ρ : VE.Valuation S) {N : Node} (hN : N ∈ U.D.T.nodes) :
    YieldsD (fill U).T S ρ (fuel (fill U).T) N ↔ YieldsD U.D.T S ρ (fuel U.D.T) N := by
  rw [yields_fill_lite hu S ρ _ N hN]
  have := VE.NormDefaults.belowCount_lt hu.acyclic hN
  exact VE.NormDefaults.yields_stable hu.acyclic S ρ _ _ N hN
    (by rw [VE.NormDefaults.fuel_fill]; unfold fuel; omega) (by unfold fuel; omega)

theorem selects_fill_fuel_lite (S : VE.Structure.{u}) (ρ : VE.Valuation S) {N : Node} (hN : N ∈ U.D.T.nodes) :
    SelectsD (fill U).T S ρ (fuel (fill U).T) N ↔ SelectsD U.D.T S ρ (fuel U.D.T) N := by
  simp only [SelectsD]
  rw [children_fill_lite hu hN]
  apply and_congr_right
  intro _
  apply not_congr
  constructor
  · rintro ⟨C, hC, hy⟩
    exact ⟨C, hC, (yields_fill_fuel_lite hu S ρ (VE.Norms.mem_children_iff.mp hC).1).mp hy⟩
  · rintro ⟨C, hC, hy⟩
    exact ⟨C, hC, (yields_fill_fuel_lite hu S ρ (VE.Norms.mem_children_iff.mp hC).1).mpr hy⟩

/-- The author rules decide on `p` as the rules of the filled tree not named `F_p` do. -/
theorem decides_author_fill (S : VE.Structure.{u}) (ρ : VE.Valuation S) (p : String) (sign : Bool) :
    DecidesD U.D.T S ρ p sign ↔ ∃ M ∈ rulesOn (fill U).T p, M.name ∉ U.unspec.map fillName ∧ M.sign = sign ∧
      SelectsD (fill U).T S ρ (fuel (fill U).T) M := by
  constructor
  · rintro ⟨N₀, hN₀, hs, hsel⟩
    have hN₀m := (List.mem_filter.mp hN₀).1
    refine ⟨fillRoot U N₀, VE.NormDefaults.mem_rulesOn_fill.mpr (Or.inl ⟨N₀, hN₀, rfl⟩),
      by rw [VE.NormDefaults.fillRoot_name]; exact hu.freshRule N₀ hN₀m, by rw [VE.NormDefaults.fillRoot_sign]; exact hs, ?_⟩
    rw [VE.NormDefaults.selectsD_fillRoot, selects_fill_fuel_lite hu S ρ hN₀m]
    exact hsel
  · rintro ⟨M, hM, hP, hs, hsel⟩
    rcases VE.NormDefaults.mem_rulesOn_fill.mp hM with ⟨N₀, hN₀, rfl⟩ | ⟨r, _, hrp, hp, rfl⟩
    · have hN₀m := (List.mem_filter.mp hN₀).1
      rw [VE.NormDefaults.selectsD_fillRoot, selects_fill_fuel_lite hu S ρ hN₀m] at hsel
      exact ⟨N₀, hN₀, by rw [← VE.NormDefaults.fillRoot_sign U]; exact hs, hsel⟩
    · exact absurd (List.mem_map.mpr ⟨r.name, hrp ▸ hp, rfl⟩) hP

end Lite

/-! ## `Fill_T` read with only `Valid (fill U)` -/

/-- The author rules on a predicate are typed where the filled tree's rules on it are. -/
theorem rulesTyped_author {U : UDoc} {E : VE.Environment} {Γ : List String} {p : String}
    (hT : VE.Norms.RulesTyped (fill U).T E Γ p) : VE.Norms.RulesTyped U.D.T E Γ p := by
  intro N hN hp
  have := hT (fillRoot U N) (VE.NormDefaults.mem_fill_nodes.mpr (Or.inl ⟨N, hN, rfl⟩))
    (by rw [VE.NormDefaults.fillRoot_pred]; exact hp)
  simpa [VE.NormDefaults.fillRoot_guard, VE.NormDefaults.fillRoot_carveOuts] using this

section Valid
variable {U : UDoc} (hv : VE.Norms.Valid (fill U))
include hv

/-- `outcomeBase_fill` with `Valid (fill U)` for `WellFormedU U`. -/
theorem outcomeBase_fill_v {B : VE.Structure.{u}} (hc : ConstantsTyped (fill U) B)
    {q : Regulated} (hq : q ∈ U.D.T.regulated) (vs : List B.Carrier) (hvs : VE.TupleTyped B q.sorts vs) :
    (VE.Norms.outcomeBase (fill U) q.name).denote B (VE.Norms.tupleVal vs) ↔
      (if q.allowByDefault then ¬ DecidesD (fill U).T (canon (fill U) B) (VE.Norms.tupleVal vs) q.name false
       else DecidesD (fill U).T (canon (fill U) B) (VE.Norms.tupleVal vs) q.name true) := by
  have hk := VE.Norms.index_before hv (show q ∈ (fill U).T.regulated from hq)
  have hT := VE.Norms.rulesTyped_of_valid hv hk
  simp only [VE.Norms.outcomeBase, VE.Norms.find_regulated hv hk]
  rw [VE.SoftNorms.canon_subst hv B hc _ _ _ (VE.Norms.outcome_wellFormed hT) _
      (VE.Norms.tupleVal_typed B _ vs hvs), VE.Norms.outcome_denote, VE.Norms.pos, VE.Norms.neg,
    VE.Norms.decides_denote, VE.Norms.decides_denote]

/-- `gapF_fill` with `Valid (fill U)` for `WellFormedU U`. -/
theorem gapF_fill_v {B : VE.Structure.{u}} (hc : ConstantsTyped (fill U) B)
    {r : Regulated} (hr : r ∈ U.D.T.regulated) (hp : r.name ∈ U.unspec) (vs : List B.Carrier)
    (hvs : VE.TupleTyped B r.sorts vs) :
    (VE.NormDefaults.gapF U r.name).denote B (VE.Norms.tupleVal vs) ↔
      ¬ DecidesD U.D.T (canon (fill U) B) (VE.Norms.tupleVal vs) r.name true ∧
        ¬ DecidesD U.D.T (canon (fill U) B) (VE.Norms.tupleVal vs) r.name false := by
  have hk := VE.Norms.index_before hv (show r ∈ (fill U).T.regulated from hr)
  have hT := rulesTyped_author (VE.Norms.rulesTyped_of_valid hv hk)
  have hρ := VE.Norms.tupleVal_typed B _ vs hvs
  simp only [VE.NormDefaults.gapF, hp, if_true, VE.Formula.denote, VE.Norms.pos, VE.Norms.neg]
  rw [VE.SoftNorms.canon_subst hv B hc _ _ _ (VE.Norms.decides_wellFormed hT true) _ hρ,
    VE.SoftNorms.canon_subst hv B hc _ _ _ (VE.Norms.decides_wellFormed hT false) _ hρ,
    VE.Norms.decides_denote, VE.Norms.decides_denote]

/-- `fillPremises_wellFormed` with `Valid (fill U)` for `WellFormedU U`: every `Fill_T` formula is a closed base
    formula of `E‴`. -/
theorem fillPremises_wf_v : ∀ a ∈ VE.NormDefaults.fillPremises U, a.WellFormed (envAt (fill U) 0) [] := by
  intro a ha
  obtain ⟨pr, hpr, rfl⟩ := List.mem_map.mp ha
  have hpr : pr ∈ VE.Norms.pairs (fill U).T := (List.mem_filter.mp hpr).1
  obtain ⟨_, ⟨i, r, hi, hrn, hrs, _⟩, ⟨j, m, hj, hmn, hms, _⟩⟩ := VE.Norms.pair_members hv hpr
  have hgap : ∀ (k : Nat) (q : Regulated), (VE.Norms.syms (fill U).T)[k]? = some (VE.Norms.Sym.reg q) → q.sorts = pr.sorts →
      (VE.NormDefaults.gapF U q.name).WellFormed (envAt (fill U) 0) pr.sorts.reverse := by
    intro k q hk hqs
    unfold VE.NormDefaults.gapF
    split
    · have hT := rulesTyped_author (VE.Norms.rulesTyped_of_valid hv hk)
      rw [show VE.Norms.before (fill U) q.name = k from VE.Norms.before_eq hv hk, ← hqs]
      exact ⟨VE.Norms.subst_wellFormed hv _ _ _ (VE.Norms.decides_wellFormed hT true),
        VE.Norms.subst_wellFormed hv _ _ _ (VE.Norms.decides_wellFormed hT false)⟩
    · trivial
  apply VE.Norms.bindAll_wellFormed (fun s hs => ?_) [] _
  · simp only [List.append_nil]
    refine ⟨VE.Norms.pairConflict_wellFormed hv hpr, ?_, ?_⟩
    · rw [← hrn]; exact hgap i r hi hrs
    · rw [← hmn]; exact hgap j m hj hms
  · have := (hv.decl _ (List.mem_of_getElem? hi)).2.2 s (by rw [← hrs] at hs; exact hs)
    exact this

end Valid

/-! ## Decisions by the rules a name test admits -/

/-- `DecidesD` by the rules whose name passes `P`. -/
def DecidesByD (T : Tree) (P : String → Prop) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (p : String)
    (sign : Bool) : Prop :=
  ∃ M ∈ rulesOn T p, P M.name ∧ M.sign = sign ∧ SelectsD T S ρ (fuel T) M

/-- `DecidesSoftD` by the rules whose name passes `P`. -/
def DecidesBySoftD (X : SoftDoc) (P : String → Prop) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (p : String)
    (sign : Bool) : Prop :=
  ∃ N ∈ VE.SoftNorms.rulesOn X p, P N.name ∧ N.sign = sign ∧ VE.SoftNorms.SelectsSoftD X S ρ (VE.SoftNorms.fuel X) N

theorem decidesBy_soften (X : SoftDoc) (P : String → Prop) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (p : String)
    (sign : Bool) : DecidesByD (soften X).T P S ρ p sign ↔ DecidesBySoftD X P S ρ p sign := by
  simp only [DecidesByD, DecidesBySoftD, VE.SoftNorms.fuel_soften]
  constructor
  · rintro ⟨N', hN', hP, hs, h⟩
    obtain ⟨N, hN, rfl⟩ := (VE.SoftNorms.mem_rulesOn_soften X p N').mp hN'
    exact ⟨N, hN, hP, hs, (VE.SoftNorms.selectsD_prime X S ρ _ N).mp h⟩
  · rintro ⟨N, hN, hP, hs, h⟩
    exact ⟨VE.SoftNorms.primeNode X N, (VE.SoftNorms.mem_rulesOn_soften X p _).mpr ⟨N, hN, rfl⟩, hP, hs,
      (VE.SoftNorms.selectsD_prime X S ρ _ N).mpr h⟩

/-- `sim_decides` restricted to the rules whose name passes `P`, when the simulation keeps `P`. -/
theorem sim_decidesBy {X Y : SoftDoc} {f : SoftNode → SoftNode} {S : VE.Structure.{u}}
    {R' : String → List S.Carrier → Prop} {ρ : VE.Valuation S} (hs : Sim X Y f S R' ρ) (P : String → Prop)
    (hP : ∀ N ∈ Y.T.nodes, (P (f N).name ↔ P N.name)) (p : String) (sign : Bool) :
    DecidesBySoftD X P S ρ p sign ↔ DecidesBySoftD Y P { S with relation := R' } ρ p sign := by
  constructor
  · rintro ⟨M, hM, hPM, hsg, hsel⟩
    have hMX := (VE.SoftNorms.mem_rulesOn.mp hM).1
    by_cases him : ∃ N ∈ Y.T.nodes, f N = M
    · obtain ⟨N, hN, rfl⟩ := him
      refine ⟨N, VE.SoftNorms.mem_rulesOn.mpr ⟨hN, ?_⟩, (hP N hN).mp hPM, by rw [← hs.sign N hN]; exact hsg,
        (sim_selects_fuel hs N hN).mp hsel⟩
      rw [← hs.pred N hN]; exact (VE.SoftNorms.mem_rulesOn.mp hM).2
    · exact absurd hsel.1 (sim_applies_extra hs M hMX (fun N hN he => him ⟨N, hN, he⟩))
  · rintro ⟨N, hN, hPN, hsg, hsel⟩
    have hNY := (VE.SoftNorms.mem_rulesOn.mp hN).1
    refine ⟨f N, VE.SoftNorms.mem_rulesOn.mpr ⟨hs.mem N hNY, ?_⟩, (hP N hNY).mpr hPN,
      by rw [hs.sign N hNY]; exact hsg, (sim_selects_fuel hs N hNY).mpr hsel⟩
    rw [hs.pred N hNY]; exact (VE.SoftNorms.mem_rulesOn.mp hN).2

/-! ## The names `fill` adds are not the author's -/

theorem notFill_of_startsWith {unspec : List String} {n : String} (h : n.startsWith "unsaid--" = false) :
    n ∉ unspec.map fillName := by
  intro hm
  obtain ⟨p, _, rfl⟩ := List.mem_map.mp hm
  rw [fillName_unsaid] at h; cases h

theorem qualify_notFill (unspec : List String) (k : Nat) (n : String) : qualify k n ∉ unspec.map fillName := by
  intro hm
  obtain ⟨p, _, he⟩ := List.mem_map.mp hm
  have h1 : (fillName p).data.head? = some 'u' := by simp [fillName, String.data_append]
  have h2 : (qualify k n).data.head? = some 'r' := by simp [qualify, String.data_append]
  rw [he] at h1; rw [h1] at h2; cases h2

/-- The precedence graph of the author tree is a subgraph of the filled tree's. -/
theorem acyclic_author {U : UDoc} (h : DagAcyclic (precedenceNodes (fill U).T)) : DagAcyclic (precedenceNodes U.D.T) := by
  apply dagAcyclic_of_map id _ h
  intro a b ⟨n, hn, hna, hb⟩
  obtain ⟨N₀, hN₀, rfl⟩ := mem_precedenceNodes.mp hn
  simp only [VE.Route.deps, List.mem_filter, List.contains_iff_mem] at hb
  obtain ⟨hbo, hbn⟩ := hb
  rw [VE.NormDefaults.nodeNames_precedence] at hbn
  obtain ⟨M₀, hM₀, rfl⟩ := List.mem_map.mp hbn
  have hfr : fillRoot U N₀ = N₀ := by
    rcases VE.NormDefaults.fillRoot_over U N₀ with ⟨_, ho, _⟩ | ⟨_, he⟩
    · rw [ho] at hbo; cases hbo
    · exact he
  apply DepPath.edge
  refine ⟨⟨N₀.name, N₀.over⟩, mem_precedenceNodes.mpr ⟨N₀, ?_, rfl⟩, hna, ?_⟩
  · rw [← hfr]; exact VE.NormDefaults.mem_fill_nodes.mpr (Or.inl ⟨N₀, hN₀, rfl⟩)
  · simp only [VE.Route.deps, List.mem_filter, List.contains_iff_mem]
    refine ⟨hbo, ?_⟩
    rw [VE.NormDefaults.nodeNames_precedence]
    exact List.mem_map.mpr ⟨fillRoot U M₀, VE.NormDefaults.mem_fill_nodes.mpr (Or.inl ⟨M₀, hM₀, rfl⟩),
      VE.NormDefaults.fillRoot_name U M₀⟩

theorem strict_choiceDoc (D : Doc) (hn : normsShaped D = true) (c : Choice) : StrictDoc (choiceDoc D c).1 :=
  build_strict D (shaped hn) _ _ (fun R a h => by
    cases hi : c.index R.id with
    | none => simp only [hi, Option.bind_none] at h; cases h
    | some i => simp only [hi, Option.bind_some] at h; exact List.mem_of_getElem? h)

theorem choiceU_nodes (N : NDoc) (hn : normsShaped N.D = true) (c : Choice) :
    (choiceU N c).D.T.nodes = (choiceDoc N.D c).1.soft.T.nodes.map SoftNode.toNode := by
  have hX := strict_choiceDoc N.D hn c
  simp only [choiceU, asU]
  rw [(correlate_noRights _ hX.1).1, soften_strict _ hX.2]

/-- The parts of `WellFormedND`. -/
theorem wellFormedND_parts {N : NDoc} (h : WellFormedND N = true) :
    WellFormedDoc N.D = true ∧ normsShaped N.D = true ∧ fillNamesFree N = true ∧
      VE.NormDefaults.WellFormedU (freeU N) = true := by
  simp only [WellFormedND, Bool.and_eq_true] at h
  exact ⟨h.1.1.1.1, h.1.1.1.2, h.1.1.2, h.1.2⟩

theorem fillDoc_chain (N : NDoc) : (fillDoc N).chain = N.D.chain := rfl

theorem chain_of_shaped {D : Doc} (hn : normsShaped D = true) : D.chain ≠ .rights := by
  have : D.chain = .norms := by
    simp only [normsShaped, Bool.and_eq_true, beq_iff_eq] at hn; exact hn.1.1.1
  rw [this]; exact nofun

/-- The S2a hypotheses of the filled document. -/
theorem hyps_fill {N : NDoc} (hN : WellFormedND N = true) (hF : WellFormedDoc (fillDoc N) = true)
    (hs : superposable (fillDoc N) = true) : Hyps (fillDoc N) :=
  ⟨hF, by rw [fillDoc_chain]; exact chain_of_shaped (wellFormedND_parts hN).2.1, hs⟩

section Choice
variable {N : NDoc} (hN : WellFormedND N = true) (hF : WellFormedDoc (fillDoc N) = true)
  (hs : superposable (fillDoc N) = true) {c : Choice} (hc : Compatible (fillDoc N) c)
include hN hF hs

theorem fill_choiceU : fill (choiceU N c) = soften (choiceDoc (fillDoc N) c).1.soft := by
  have hp := wellFormedND_parts hN
  rw [← (fillDoc_choice N hp.2.1 hp.2.2.1 c).1, choice_correlate (hyps_fill hN hF hs) c]

theorem fill_supU : fill (supU N) = soften (sup (fillDoc N)).1.soft := by
  have hp := wellFormedND_parts hN
  rw [← (fillDoc_sup N hp.2.1 hp.2.2.1).1, sup_correlate (hyps_fill hN hF hs)]

include hc in
theorem valid_fill_choiceU : VE.Norms.Valid (fill (choiceU N c)) := by
  rw [fill_choiceU hN hF hs]; exact choice_valid (hyps_fill hN hF hs) hc

include hc in
/-- What the author-rule lemmas of `fill` read holds of every compatible choice's document. -/
theorem authorLite_choiceU : AuthorLite (choiceU N c) := by
  have hp := wellFormedND_parts hN
  have hfree := namesFree hp.2.2.1
  refine ⟨fun M₀ hM₀ => ?_, ?_⟩
  · rw [choiceU_nodes N hp.2.1 c] at hM₀
    obtain ⟨M, hM, rfl⟩ := List.mem_map.mp hM₀
    show M.name ∉ _
    rcases (mem_choiceNodes N.D c M).mp hM with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, _, ha, hac⟩
    · rw [(shaped hp.2.1).nodes] at hf; cases hf
    · exact notFill_of_startsWith (hfree.declared hu (m := ("rule", M.name)) (by simp [VE.Compose.Content.declared]))
    · exact notFill_of_startsWith (hfree.sets _ (List.getElem_mem hm) ("rule", M.name)
        (candidate_declares hm ha hac (by simp [VE.Compose.Content.declared])))
  · have hac := choice_precedence_acyclic (hyps_fill hN hF hs) hc
    rw [← fill_choiceU hN hF hs] at hac
    exact acyclic_author hac

omit hN hF hs in
/-- S2a's simulation sends a rule named `F_p` to itself and an author rule to an author rule. -/
theorem fmap_keeps_author (hh : Hyps (fillDoc N)) (hfree : fillNamesFree N = true) {M : SoftNode}
    (hM : M ∈ (choiceDoc (fillDoc N) c).1.soft.T.nodes) :
    ((fmap (fillDoc N) c M).name ∉ N.unspec.map fillName ↔ M.name ∉ N.unspec.map fillName) := by
  rw [fmap_name hh c hM, qName_chosenAt]
  rcases (mem_choiceNodes _ c M).mp hM with hf | ⟨u, cs, hu⟩ | ⟨m, hm, i, a, hi, ha, hac⟩
  · rw [chosenAt_frame hh c hf]
  · rw [chosenAt_fixed _ hh.da c hu]
  · rw [chosenAt_chosen _ hh.nodup hh.da c hm hi ha hac]
    have hd := candidate_declares hm ha hac (x := ("rule", M.name)) (by simp [VE.Compose.Content.declared])
    obtain ⟨R0, hR0, hR⟩ := mem_sets_fillDoc.mp (List.getElem_mem hm)
    have hd' : ("rule", M.name) ∈ declaredBy R0 := by
      rw [← declaredBy_fillSet N R0, ← hR]; exact hd
    have h1 := (namesFree hfree).sets R0 hR0 ("rule", M.name) hd'
    have hn : M.name ∉ N.unspec.map fillName := notFill_of_startsWith (unspec := N.unspec) h1
    have hq : qualify (position (fillDoc N) m i) M.name ∉ N.unspec.map fillName := qualify_notFill _ _ _
    simp only
    exact ⟨fun _ => hn, fun _ => hq⟩

end Choice

/-! ## The author rules through the simulation and the canonical interpretations -/

/-- `decides_pull_canon` for the rules a name test admits, on W1's reading of the choice's document. -/
theorem decidesBy_pull_canon {D : Doc} (hh : Hyps D) {c : Choice} (hc : Compatible D c) (B : VE.Structure.{u})
    (hcB : ∀ x s, (soften (sup D).1.soft).E.constants x = some s → ∃ v, B.constant x = some v)
    (he : Encodes D c B) (P : String → Prop) {r : Regulated} (hr : r ∈ (choiceDoc D c).1.soft.T.regulated)
    (ρ : VE.Valuation B) (sign : Bool) :
    DecidesByD (soften (choiceDoc D c).1.soft).T P (pull D c (canon (soften (sup D).1.soft) B)) ρ r.name sign ↔
      DecidesByD (soften (choiceDoc D c).1.soft).T P (canon (soften (choiceDoc D c).1.soft) (pull D c B)) ρ r.name
        sign := by
  have hvY := choice_valid hh hc
  have hT := VE.Norms.rulesTyped_of_valid hvY
    (VE.Norms.index_before hvY (show r ∈ (soften (choiceDoc D c).1.soft).T.regulated from hr))
  unfold DecidesByD
  apply exists_congr; intro M
  apply and_congr_right; intro hM
  apply and_congr_right; intro _
  apply and_congr_right; intro _
  have hMm : M ∈ (soften (choiceDoc D c).1.soft).T.nodes ∧ M.pred = r.name := by
    simpa [VE.Norms.rulesOn] using hM
  rw [← VE.Norms.selects_denote, ← VE.Norms.selects_denote]
  exact denote_relation_congr _ (pull D c (canon (soften (sup D).1.soft) B))
    (canon (soften (choiceDoc D c).1.soft) (pull D c B)).relation
    (fun p ss hp vs hvs => pull_canon hh hc B hcB he (envAt_sub hp) vs hvs) _ _ ρ
    ((VE.check_iff_wellFormed _ _ _).mpr (VE.Norms.selects_wellFormed hT _ M hMm.1 hMm.2))

section Pull
variable {N : NDoc} (hN : WellFormedND N = true) (hF : WellFormedDoc (fillDoc N) = true)
  (hs : superposable (fillDoc N) = true) {c : Choice} (hc : Compatible (fillDoc N) c) {B : VE.Structure.{u}}
  (hB : VE.Compose.BaseAdmissibleP (correlate (sup (fillDoc N)).1) (slotP (fillDoc N)) B)
  (he : Encodes (fillDoc N) c B)
include hN hF hs hc hB he

/-- The filled trees decide alike: the superposed one on its canonical interpretation of `B`, the choice's on its
    canonical interpretation of the pulled base. -/
theorem decides_fill_pull {q : Regulated} (hq : q ∈ (fillDoc N).frame.soft.T.regulated) (ρ : VE.Valuation B)
    (sign : Bool) :
    DecidesD (fill (supU N)).T (canon (fill (supU N)) B) ρ q.name sign ↔
      DecidesD (fill (choiceU N c)).T (canon (fill (choiceU N c)) (pull (fillDoc N) c B)) ρ q.name sign := by
  have hh := hyps_fill hN hF hs
  have hcB := hyps_constants hh hB
  rw [fill_supU hN hF hs, fill_choiceU hN hF hs, VE.SoftNorms.decidesD_soften, VE.SoftNorms.decidesD_soften]
  exact (sim_decides (faithful_sim hh hc _ (encodes_canon hh B he) ρ) q.name sign).trans
    (decides_pull_canon hh hc B hcB he (by rw [choice_reg]; exact hq) ρ sign)

/-- The author rules decide alike (`sim_decides` on the rules not named `F_p`). -/
theorem decides_author_pull (hsu : VE.NormDefaults.WellFormedU (supU N) = true) {q : Regulated}
    (hq : q ∈ (fillDoc N).frame.soft.T.regulated) (ρ : VE.Valuation B) (sign : Bool) :
    DecidesD (supU N).D.T (canon (fill (supU N)) B) ρ q.name sign ↔
      DecidesD (choiceU N c).D.T (canon (fill (choiceU N c)) (pull (fillDoc N) c B)) ρ q.name sign := by
  have hh := hyps_fill hN hF hs
  have hcB := hyps_constants hh hB
  have hfree := (wellFormedND_parts hN).2.2.1
  rw [decides_author_fill (authorLite_of_uvalid (VE.NormDefaults.uvalid hsu)),
    decides_author_fill (authorLite_choiceU hN hF hs hc)]
  change DecidesByD (fill (supU N)).T (· ∉ N.unspec.map fillName) (canon (fill (supU N)) B) ρ q.name sign ↔
    DecidesByD (fill (choiceU N c)).T (· ∉ N.unspec.map fillName)
      (canon (fill (choiceU N c)) (pull (fillDoc N) c B)) ρ q.name sign
  rw [fill_supU hN hF hs, fill_choiceU hN hF hs, decidesBy_soften,
    ← decidesBy_pull_canon hh hc B hcB he _ (by rw [choice_reg]; exact hq), decidesBy_soften]
  exact sim_decidesBy (faithful_sim hh hc _ (encodes_canon hh B he) ρ) _
    (fun M hM => fmap_keeps_author hh hfree hM) q.name sign

/-- `Fill_T` of `sup (fillDoc N)` holds of an encoded slot-admissible base exactly when `Fill_T` of the choice's
    document holds of the pulled base. -/
theorem fillPremises_pull (hsu : VE.NormDefaults.WellFormedU (supU N) = true) :
    Sat B (VE.NormDefaults.fillPremises (supU N)) ↔
      Sat (pull (fillDoc N) c B) (VE.NormDefaults.fillPremises (choiceU N c)) := by
  have hh := hyps_fill hN hF hs
  have hu := VE.NormDefaults.uvalid hsu
  have hvY := valid_fill_choiceU hN hF hs hc
  have hcX : ConstantsTyped (fill (supU N)) B := by
    have := hB.1.1.1.1; rw [sup_correlate hh, ← fill_supU hN hF hs] at this; exact this
  have hcY : ConstantsTyped (fill (choiceU N c)) (pull (fillDoc N) c B) := by
    have := (base_down _ hF hh.chain hs c hc B hB he).1.1.1.1
    rw [choice_correlate hh, ← fill_choiceU hN hF hs] at this; exact this
  have hregX : (supU N).D.T.regulated = (fillDoc N).frame.soft.T.regulated := by
    show (fill (supU N)).T.regulated = _
    rw [fill_supU hN hF hs]; exact sup_reg
  have hregY : (choiceU N c).D.T.regulated = (fillDoc N).frame.soft.T.regulated := by
    show (fill (choiceU N c)).T.regulated = _
    rw [fill_choiceU hN hF hs]; exact choice_reg c
  have hpairs : VE.Norms.pairs (choiceU N c).D.T = VE.Norms.pairs (supU N).D.T := by
    unfold VE.Norms.pairs; rw [hregX, hregY]
  have hO : ∀ q ∈ (supU N).D.T.regulated, ∀ vs : List B.Carrier, VE.TupleTyped B q.sorts vs →
      ((VE.Norms.outcomeBase (fill (supU N)) q.name).denote B (VE.Norms.tupleVal vs) ↔
        (VE.Norms.outcomeBase (fill (choiceU N c)) q.name).denote (pull (fillDoc N) c B) (VE.Norms.tupleVal vs)) := by
    intro q hq vs hvs
    have hq' : q ∈ (choiceU N c).D.T.regulated := by rw [hregY, ← hregX]; exact hq
    have hqf : q ∈ (fillDoc N).frame.soft.T.regulated := by rw [← hregX]; exact hq
    rw [VE.NormDefaults.outcomeBase_fill hsu hcX hq vs hvs,
      outcomeBase_fill_v hvY hcY hq' vs ((VE.Norms.tupleTyped_relation B _ _ vs).mpr hvs)]
    split
    · exact not_congr (decides_fill_pull hN hF hs hc hB he hqf _ false)
    · exact decides_fill_pull hN hF hs hc hB he hqf _ true
  have hG : ∀ q ∈ (supU N).D.T.regulated, ∀ vs : List B.Carrier, VE.TupleTyped B q.sorts vs →
      ((VE.NormDefaults.gapF (supU N) q.name).denote B (VE.Norms.tupleVal vs) ↔
        (VE.NormDefaults.gapF (choiceU N c) q.name).denote (pull (fillDoc N) c B) (VE.Norms.tupleVal vs)) := by
    intro q hq vs hvs
    have hq' : q ∈ (choiceU N c).D.T.regulated := by rw [hregY, ← hregX]; exact hq
    have hqf : q ∈ (fillDoc N).frame.soft.T.regulated := by rw [← hregX]; exact hq
    by_cases hp : q.name ∈ N.unspec
    · rw [VE.NormDefaults.gapF_fill hu hsu hcX hq hp vs hvs,
        gapF_fill_v hvY hcY hq' hp vs ((VE.Norms.tupleTyped_relation B _ _ vs).mpr hvs),
        decides_author_pull hN hF hs hc hB he hsu hqf _ true, decides_author_pull hN hF hs hc hB he hsu hqf _ false]
    · have h1 : VE.NormDefaults.gapF (supU N) q.name = .bottom := by
        simp only [VE.NormDefaults.gapF]; exact if_neg hp
      have h2 : VE.NormDefaults.gapF (choiceU N c) q.name = .bottom := by
        simp only [VE.NormDefaults.gapF]; exact if_neg hp
      rw [h1, h2]; exact Iff.rfl
  unfold VE.NormDefaults.fillPremises
  rw [show (choiceU N c).unspec = N.unspec from rfl, show (supU N).unspec = N.unspec from rfl, hpairs]
  constructor
  · intro hX a ha
    obtain ⟨pr, hpr, rfl⟩ := List.mem_map.mp ha
    have hXa := hX _ (List.mem_map.mpr ⟨pr, hpr, rfl⟩)
    have hpr' := (List.mem_filter.mp hpr).1
    obtain ⟨r, hr, hrn, _, _, hrs⟩ := VE.NormDefaults.pair_req hpr'
    obtain ⟨m, hm, hmn, _, hms⟩ := VE.NormDefaults.pair_perm hu hpr'
    rw [VE.Norms.bindAll_denote_nil] at hXa ⊢
    intro vs hvs
    have hvsB : VE.TupleTyped B pr.sorts vs := (VE.Norms.tupleTyped_relation B _ _ vs).mp hvs
    have h1 := hXa vs hvsB
    simp only [VE.Formula.denote, VE.Norms.pairConflict] at h1 ⊢
    rw [← hrn, ← hmn] at h1 ⊢
    rw [← hO r hr vs (hrs ▸ hvsB), ← hO m hm vs (hms ▸ hvsB), ← hG r hr vs (hrs ▸ hvsB),
      ← hG m hm vs (hms ▸ hvsB)]
    exact h1
  · intro hY a ha
    obtain ⟨pr, hpr, rfl⟩ := List.mem_map.mp ha
    have hYa := hY _ (List.mem_map.mpr ⟨pr, hpr, rfl⟩)
    have hpr' := (List.mem_filter.mp hpr).1
    obtain ⟨r, hr, hrn, _, _, hrs⟩ := VE.NormDefaults.pair_req hpr'
    obtain ⟨m, hm, hmn, _, hms⟩ := VE.NormDefaults.pair_perm hu hpr'
    rw [VE.Norms.bindAll_denote_nil] at hYa ⊢
    intro vs hvsB
    have h1 := hYa vs ((VE.Norms.tupleTyped_relation B _ _ vs).mpr hvsB)
    simp only [VE.Formula.denote, VE.Norms.pairConflict] at h1 ⊢
    rw [← hrn, ← hmn] at h1 ⊢
    rw [hO r hr vs (hrs ▸ hvsB), hO m hm vs (hms ▸ hvsB), hG r hr vs (hrs ▸ hvsB), hG m hm vs (hms ▸ hvsB)]
    exact h1

end Pull

/-! ## A choice's filled document on the norms chain -/

theorem strict_choice_fillDoc (N : NDoc) (hn : normsShaped N.D = true) (c : Choice) :
    StrictDoc (choiceDoc (fillDoc N) c).1 := by
  have h := build_fillDoc N (shaped hn).nodes (fun _ => true) (fun _ => true) (pickC c) (pickC c)
    (fun _ _ _ _ => rfl) (fun _ _ _ => rfl)
    (fun R _ => by
      show ((c.index R.id).bind ((fillSet N R).candidates[·]?)) = (pickC c R).map (fillCand N)
      cases h : c.index R.id <;> simp [candidates_fillSet, pickC, h])
    (fun _ _ _ => rfl)
  have hX := strict_choiceDoc N.D hn c
  rw [choiceDoc_eq, h]
  exact ⟨by rw [noRights_fill]; exact hX.1, strictNodes_fill N _ _ hX.2⟩

/-- A base admissible for a compatible choice's filled document with `Fill_T` is one norm-defaults admits. -/
theorem baseAdmissibleP_choiceU {N : NDoc} (hN : WellFormedND N = true) (c : Choice) (B : VE.Structure.{u}) :
    VE.Compose.BaseAdmissibleP (correlate (choiceDoc (fillDoc N) c).1)
        (VE.Rights.limPremises (choiceDoc (fillDoc N) c).1 ++ VE.NormDefaults.fillPremises (choiceU N c)) B ↔
      VE.NormDefaults.BaseAdmissibleU (choiceU N c) B := by
  have hX := strict_choice_fillDoc N (wellFormedND_parts hN).2.1 c
  have hc := correlate_noRights _ hX.1
  unfold VE.Compose.BaseAdmissibleP VE.NormDefaults.BaseAdmissibleU VE.SoftNorms.BaseAdmissible'
  rw [hc.2, List.nil_append, ← (fillDoc_choice N (wellFormedND_parts hN).2.1 (wellFormedND_parts hN).2.2.1 c).1,
    hc.1, softPremises_strict _ hX.2]
  exact ⟨fun h => ⟨h.1.1, h.2⟩, fun h => ⟨⟨h.1, VE.Compose.sat_nil B⟩, h.2⟩⟩

/-- On a document expansion, a sentence over the complete vocabulary reads as on the canonical interpretation of the
    base. -/
theorem documentExpansion_canon {D : VE.Norms.Doc} (hv : VE.Norms.Valid D) {B S : VE.Structure.{u}}
    (hE : VE.Norms.DocumentExpansion D B S) (ψ : VE.Formula) (hψ : ψ.WellFormed (envAt D (size D)) []) :
    ψ.denote S [] ↔ ψ.denote (canon D B) [] := by
  obtain ⟨hr, hA, hsat⟩ := hE
  have hc : ConstantsTyped D S := VE.Norms.constantsTyped_of_admissible hA
  have ha := VE.Norms.agreesBelow_of_meanings ((VE.Norms.sat_document hv S).mp hsat).2.1
  rw [← hr, ← VE.Norms.subst_restrict_denote hv _ S hc ha ψ [] hψ [] (typed_nil _)]
  exact VE.SoftNorms.canon_subst hv (VE.Norms.restrictAll D.T S) hc _ ψ [] hψ [] (typed_nil _)

end VE.Readings
