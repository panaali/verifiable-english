import VE.SoftNorms.Wire
import VE.Norms.Admission

/-! W2 admission on the soft-norms route (docs/spec/soft-norms.md 9.3, 9.4), W1's
`Norms.Admission` with the soft decoder.

Active `norm` units are decoded as soft rules; `E′`, `T′` and the premises are
regenerated from them. Graph nodes are decoded over `E′` (so decision findings
may be named), certificates bind the regenerated `E′` JSON, and graph leaves may
name, beside W2's ordinary provenance, exactly a regenerated layer premise on
`T′` (`layer:norms:<p>`), a regenerated pair premise (`background:profile`), or
a regenerated soft premise (`soft:coherence:<a>,<b>`, `soft:exception:…`). -/
namespace VE.SoftNorms.Admission
open Lean
open VE.Norms
open VE.SoftNorms.Wire
open VE.Route.Admission
open VE.Bridge (exactFields stringField)
open VE.Norms.Admission (splitDocument premiseAsts nodeBinding checkBindings CertificateBound
  checkBindings_bound mapM_ok_mem forM_ok decodeNode_ast getArr_ok backgroundLeaf)
universe u

/-- A quoted norm never contributes a layer but passes every single-rule check. -/
def checkQuoted (src : SoftSource) (j : Json) : Except String Unit := do
  let N ← decodeSoftNorm src.D.soft j
  validateSoft ⟨src.D.E, src.D.lits, src.D.soft, ⟨src.D.T.regulated, [], [{ N with over := [] }]⟩⟩

def LayerLeaf (src : SoftSource) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone &&
    ((syms (soften src.D).T).filterMap (fun | .reg r => some r | .defn _ => none)).any
      (fun r => decide (w.claim.label = "layer:norms:" ++ r.name ∧
        w.claim.formula = elabPremise (soften src.D).T r))) = true

instance (src : SoftSource) (w : WireNode) : Decidable (LayerLeaf src w) := by
  unfold LayerLeaf; infer_instance

def ProfileLeaf (src : SoftSource) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone && w.claim.label == "background:profile" &&
    (pairPremises (soften src.D).T).any (fun a => decide (w.claim.formula = a))) = true

instance (src : SoftSource) (w : WireNode) : Decidable (ProfileLeaf src w) := by
  unfold ProfileLeaf; infer_instance

/-- A regenerated soft premise, under its exact label, with no unit pointer. -/
def SoftLeaf (src : SoftSource) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone &&
    (softLabelled src.D).any (fun (l, a) => decide (w.claim.label = l ∧ w.claim.formula = a))) = true

instance (src : SoftSource) (w : WireNode) : Decidable (SoftLeaf src w) := by
  unfold SoftLeaf; infer_instance

def NodeAdmitted (src : SoftSource) (D : VE.Route.Admission.Doc) (w : WireNode) : Prop :=
  VE.Route.Admission.NodeAdmitted D w ∨ LayerLeaf src w ∨ ProfileLeaf src w ∨ SoftLeaf src w

instance (src : SoftSource) (D : VE.Route.Admission.Doc) (w : WireNode) :
    Decidable (NodeAdmitted src D w) := by
  unfold NodeAdmitted; infer_instance

def admitNodes (src : SoftSource) (D : VE.Route.Admission.Doc) (ws : List WireNode) : Except String Unit :=
  match ws.find? (fun w => !decide (NodeAdmitted src D w)) with
  | some w => .error (VE.Route.Admission.nodeDiagnostic D w)
  | none => .ok ()

theorem admitNodes_ok (src : SoftSource) (D : VE.Route.Admission.Doc) (ws : List WireNode)
    (h : admitNodes src D ws = .ok ()) : ∀ w ∈ ws, NodeAdmitted src D w := by
  unfold admitNodes at h
  split at h
  · cases h
  · rename_i hf
    intro w hw
    have := List.find?_eq_none.mp hf w hw
    simpa using this

open VE.Order.ProfileGate (bind_ok)

structure Admitted where
  src : SoftSource
  doc : VE.Route.Admission.Doc
  /-- The regenerated `E′` JSON (the canonical source environment plus the decisions). -/
  prime : Json
  graphJson : Json
  nodes : Array Json
  decoded : List (WireNode × Json)
  wires : List WireNode
  graph : VE.Graph.ClaimGraph VE.Tableau.Certificate
  report : VE.Graph.Report
  kinds : List Json

/-- W2's ordinary document decoder with the regenerated decision predicates in
scope. This lets asserted units and reading sets state decision findings. -/
def decodeSoftDoc (src : SoftSource) (j : Json) : Except String VE.Route.Admission.Doc := do
  let E := envPrime src.D
  let data := src.se.profiles.contains "data@0"
  let units ← (← (← j.getObjVal? "units").getArr?).toList.mapM
    (VE.Route.Admission.decodeUnit E data)
  VE.Route.Admission.require (units.length ≤ 10000) "ResourceLimit: unit count"
  VE.Route.Admission.require ((units.map DocUnit.id).eraseDups.length == units.length)
    "duplicate unit id"
  VE.Route.Admission.require (VE.Route.Admission.sortedSpans units)
    "unit spans must be sorted and non-overlapping"
  let optional := fun (key : String) => match j.getObjVal? key with
    | .ok v => v.getArr?.map Array.toList
    | .error _ => pure []
  let lemmas ← (← optional "lemmas").mapM (VE.Route.Admission.decodeLemma E data)
  VE.Route.Admission.require ((lemmas.map Lemma.name).eraseDups.length == lemmas.length)
    "duplicate lemma"
  let openTerms ← VE.Route.Admission.tokens (Json.arr (← optional "open_terms").toArray)
  let readingSets ← (← optional "reading_sets").mapM
    (VE.Route.Admission.decodeReadingSet E data)
  VE.Route.Admission.require
    ((readingSets.map (fun r => (r.id, r.version))).eraseDups.length == readingSets.length)
    "duplicate reading set version"
  let narrowings ← VE.Route.Admission.tokens (Json.arr (← optional "narrowings").toArray)
  pure ⟨src.se.ne.rv.literals, src.se.ne.rv.flags, units, lemmas, openTerms, readingSets,
    narrowings⟩

def admitDocument (environment document : Json) : Except String Admitted := do
  VE.Bridge.displayFields document ["units", "graph"]
    ["lemmas", "open_terms", "reading_sets", "narrowings"]
  let (clean, norms, quoted) ← splitDocument document
  let src ← decodeSoftSource environment norms
  quoted.forM (checkQuoted src)
  let D₀ ← decodeSoftDoc src clean
  let D := { D₀ with literals := src.se.ne.rv.literals }
  let graphJson ← document.getObjVal? "graph"
  exactFields graphJson ["root", "nodes"]
  let root ← stringField graphJson "root"
  let nodeArray ← (← graphJson.getObjVal? "nodes").getArr?
  VE.Route.Admission.require (nodeArray.size ≤ 1000) "ResourceLimit: graph node count"
  let decoded ← nodeArray.toList.mapM (VE.Route.Admission.decodeNode (envPrime src.D) (src.se.profiles.contains "data@0"))
  let prime ← primeJson src.D environment
  VE.Norms.Admission.checkBindings src.se.profiles prime decoded
  let wires := decoded.map Prod.fst
  admitNodes src D wires
  let g : VE.Graph.ClaimGraph VE.Tableau.Certificate := ⟨wires.map WireNode.toNode, root⟩
  let r ← VE.Route.Admission.checkGraph (envPrime src.D) g
  VE.Route.Admission.require (decide (CitationsClosed D r))
    "AdmissionError: a cited lemma's leaves are missing from the report"
  VE.Route.Admission.require (decide (ChoicesCompatible r))
    "AdmissionError: incompatible reading choices"
  pure ⟨src, D, prime, graphJson, nodeArray, decoded, wires, g, r, D.units.map (fun x => renderKind x.kind)⟩

def SourceDecoded (environment document : Json) (res : Admitted) : Prop :=
  (∃ clean norms quoted, splitDocument document = .ok (clean, norms, quoted) ∧
    decodeSoftSource environment norms = .ok res.src ∧
    (∀ q ∈ quoted, checkQuoted res.src q = .ok ()) ∧
    ∃ D₀, decodeSoftDoc res.src clean = .ok D₀ ∧
      res.doc = { D₀ with literals := res.src.se.ne.rv.literals }) ∧
  WellFormedSoft res.src.D = true ∧ res.src.D.E = res.src.se.ne.rv.environment ∧
  res.src.D.lits = res.src.se.ne.rv.literals ∧
  document.getObjVal? "graph" = .ok res.graphJson ∧
  res.graphJson.getObjVal? "nodes" = .ok (Json.arr res.nodes) ∧
  stringField res.graphJson "root" = .ok res.graph.root ∧
  res.wires = res.decoded.map Prod.fst ∧ res.graph.nodes = res.wires.map WireNode.toNode ∧
  (∀ x ∈ res.decoded, ∃ j ∈ res.nodes.toList,
    VE.Route.Admission.decodeNode (envPrime res.src.D) (res.src.se.profiles.contains "data@0") j = .ok x ∧
    j.getObjVal? "ast" = .ok x.2 ∧
    VE.Route.Wire.decodeClosed (envPrime res.src.D) x.2
      ((res.src.se.profiles.contains "data@0") && !x.1.claim.label.startsWith "background:") =
        .ok x.1.claim.formula)

/-- Every certificate is bound to the regenerated `E′` and the source ASTs of its premises
and conclusion. -/
def CertificatesBound (environment : Json) (res : Admitted) : Prop :=
  primeJson res.src.D environment = .ok res.prime ∧
  ∀ x ∈ res.decoded, CertificateBound res.src.se.profiles res.prime res.decoded x

def ReportAdmitted (res : Admitted) : Prop :=
  VE.Graph.SoundReport.{0} (envPrime res.src.D) res.graph res.report ∧
  (∀ w ∈ res.wires, NodeAdmitted res.src res.doc w) ∧
  (∀ leaf ∈ res.report.assumptions, ∃ w ∈ res.wires,
    w.claim = leaf ∧ w.deduction = none ∧ NodeAdmitted res.src res.doc w) ∧
  CitationsClosed res.doc res.report ∧ ChoicesCompatible res.report

theorem admitDocument_spec (environment document : Json) (res : Admitted)
    (h : admitDocument environment document = .ok res) :
    SourceDecoded environment document res ∧ CertificatesBound environment res ∧
    VE.Graph.SoundReport.{u} (envPrime res.src.D) res.graph res.report ∧
    (∀ w ∈ res.wires, NodeAdmitted res.src res.doc w) ∧
    (∀ leaf ∈ res.report.assumptions, ∃ w ∈ res.wires,
      w.claim = leaf ∧ w.deduction = none ∧ NodeAdmitted res.src res.doc w) ∧
    CitationsClosed res.doc res.report ∧ ChoicesCompatible res.report := by
  unfold admitDocument at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨⟨clean, norms, quoted⟩, hsplit, h⟩ := bind_ok h
  obtain ⟨src, hsrc, h⟩ := bind_ok h
  obtain ⟨_, hq, h⟩ := bind_ok h
  obtain ⟨D₀, hD, h⟩ := bind_ok h
  obtain ⟨graphJson, hg, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨root, hroot, h⟩ := bind_ok h
  obtain ⟨nj, hnj, h⟩ := bind_ok h
  obtain ⟨nodeArray, harr, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨decoded, hdec, h⟩ := bind_ok h
  obtain ⟨prime, hprime, h⟩ := bind_ok h
  obtain ⟨_, hbind, h⟩ := bind_ok h
  obtain ⟨_, hadm, h⟩ := bind_ok h
  obtain ⟨r, hr, h⟩ := bind_ok h
  obtain ⟨_, hc, h⟩ := bind_ok h
  obtain ⟨_, hch, h⟩ := bind_ok h
  cases h
  have hnodes := admitNodes_ok src _ (decoded.map Prod.fst) hadm
  obtain ⟨_, _, _, hsound⟩ := VE.Graph.check_sound.{u} (envPrime src.D) _ r
    (VE.Route.Admission.checkGraph_ok _ _ r hr)
  have hnj' : nj = Json.arr nodeArray := getArr_ok harr
  subst hnj'
  refine ⟨⟨⟨clean, norms, quoted, hsplit, hsrc, forM_ok _ quoted hq, D₀, hD, rfl⟩,
      src.wf, src.env, src.lits, hg, hnj, hroot, rfl, rfl, ?_⟩,
    ⟨hprime, checkBindings_bound _ _ decoded hbind⟩, hsound, hnodes, ?_,
    of_decide_eq_true (VE.Route.Gate.require_ok hc),
    of_decide_eq_true (VE.Route.Gate.require_ok hch)⟩
  · intro x hx
    obtain ⟨j, hj, hd⟩ := mapM_ok_mem _ _ decoded hdec x hx
    exact ⟨j, hj, hd, decodeNode_ast _ _ j x hd⟩
  · intro leaf hl
    obtain ⟨node, hn, hcl, hde⟩ := (hsound.2.2.1 leaf hl).2
    obtain ⟨w, hw, rfl⟩ := List.mem_map.mp hn
    exact ⟨w, hw, hcl, hde, hnodes w hw⟩

theorem layerLeaf_formula (src : SoftSource) (w : WireNode) (h : LayerLeaf src w) :
    w.claim.formula ∈ elaborate (soften src.D).T := by
  simp only [LayerLeaf, Bool.and_eq_true] at h
  obtain ⟨r, hr, he⟩ := List.any_eq_true.mp h.2
  have heq : w.claim.label = "layer:norms:" ++ r.name ∧
      w.claim.formula = elabPremise (soften src.D).T r := of_decide_eq_true he
  rw [heq.2]
  change elabPremise (soften src.D).T r ∈
    (syms (soften src.D).T).filterMap (fun | .reg r => some (elabPremise (soften src.D).T r) | .defn _ => none)
  obtain ⟨q, hq, hqr⟩ := List.mem_filterMap.mp
    (show r ∈ (syms (soften src.D).T).filterMap (fun | .reg r => some r | .defn _ => none) from hr)
  cases q with
  | reg r' =>
    simp only [Option.some.injEq] at hqr
    subst hqr
    exact List.mem_filterMap.mpr ⟨.reg r', hq, rfl⟩
  | defn d => cases hqr

theorem softLeaf_formula (src : SoftSource) (w : WireNode) (h : SoftLeaf src w) :
    w.claim.formula ∈ softPremises src.D := by
  simp only [SoftLeaf, Bool.and_eq_true] at h
  obtain ⟨⟨l, a⟩, hm, he⟩ := List.any_eq_true.mp h.2
  have heq : w.claim.label = l ∧ w.claim.formula = a := of_decide_eq_true he
  rw [heq.2]
  simp only [softLabelled, List.mem_append, List.mem_map] at hm
  rcases hm with hm | ⟨⟨M, N⟩, hc, he'⟩
  · exact List.mem_append_left _ (List.of_mem_zip hm).2
  · simp only [Prod.mk.injEq] at he'
    rw [← he'.2]
    exact List.mem_append_right _ (List.mem_map.mpr ⟨(M, N), hc, rfl⟩)

/-- The report assumptions that stay explicit hypotheses: every leaf that is neither a
regenerated layer leaf, a regenerated soft leaf nor a Background leaf. -/
def otherAssumptions (res : Admitted) : List VE.Graph.Claim :=
  res.report.assumptions.filter (fun c =>
    !backgroundLeaf c && !decide (∃ w ∈ res.wires, w.claim = c ∧ (LayerLeaf res.src w ∨ SoftLeaf res.src w)))

/-- The coherence leaves the report actually uses that are not discharged by rank
(`conditional_on`, 6.4). -/
def conditionalOn (res : Admitted) : List String :=
  (openCoherence res.src.D).filter (fun l => res.report.assumptions.any (fun c => c.label == l))

/-- Semantic report consequence: in every structure admissible for `E′` satisfying the
regenerated `background′` and layer premises, the remaining assumptions entail the root. -/
theorem soft_wire_report_consequence (environment document : Json) (res : Admitted)
    (h : admitDocument environment document = .ok res) (S : VE.Structure.{u})
    (hS : S.Admissible (envPrime res.src.D))
    (hflags : Sat S (VE.Data.Background.generate res.doc.flags))
    (hregen : Sat S (background' res.src.D ++ elaborate (soften res.src.D).T))
    (hother : Sat S ((otherAssumptions res).map (·.formula))) :
    res.report.root.formula.denote S [] := by
  obtain ⟨⟨⟨_, _, _, _, _, _, _, _, hdoc⟩, _, _, hlits, _⟩, _, hsound, _, hleaves, _⟩ :=
    admitDocument_spec.{u} environment document res h
  apply hsound.2.2.2.1 S hS
  intro a ha
  obtain ⟨leaf, hl, rfl⟩ := List.mem_map.mp ha
  by_cases hlayer : ∃ w ∈ res.wires, w.claim = leaf ∧ (LayerLeaf res.src w ∨ SoftLeaf res.src w)
  · obtain ⟨w, _, hwl, hw⟩ := hlayer
    rw [← hwl]
    rcases hw with hw | hw
    · exact hregen _ (List.mem_append_right _ (layerLeaf_formula res.src w hw))
    · exact hregen _ (List.mem_append_left _ (List.mem_append_right _ (softLeaf_formula res.src w hw)))
  by_cases hb : backgroundLeaf leaf = true
  · obtain ⟨w, hw, hwl, hde, hadm⟩ := hleaves leaf hl
    rcases hadm with hadm | hadm | hadm | hadm
    · unfold VE.Route.Admission.NodeAdmitted at hadm
      rw [hde] at hadm
      unfold backgroundLeaf at hb
      unfold LeafAdmitted at hadm
      rw [hwl] at hadm
      split at hb
      · rename_i g hg
        rw [hg] at hadm
        obtain ⟨_, p, hp, hpe⟩ := hadm
        subst hpe
        rcases List.mem_append.mp hp with hp | hp
        · obtain ⟨b, hbm, hbe⟩ := List.mem_map.mp hp
          simp only [Prod.mk.injEq] at hbe
          rw [← hbe.1]
          exact hflags b hbm
        · obtain ⟨b, hbm, hbe⟩ := List.mem_map.mp hp
          simp only [Prod.mk.injEq] at hbe
          rw [← hbe.1]
          apply hregen
          apply List.mem_append_left
          unfold background' background backgroundBase
          apply List.mem_append_left
          apply List.mem_append_left
          apply List.mem_append_right
          show b ∈ VE.Route.Background.literals res.src.D.lits
          rw [hlits, ← (show res.doc.literals = res.src.se.ne.rv.literals by rw [hdoc])]
          exact hbm
      · cases hb
    · exact absurd ⟨w, hw, hwl, Or.inl hadm⟩ hlayer
    · simp only [ProfileLeaf, Bool.and_eq_true] at hadm
      obtain ⟨a, ha, hfa⟩ := List.any_eq_true.mp hadm.2
      rw [← hwl, of_decide_eq_true hfa]
      apply hregen
      apply List.mem_append_left
      unfold background' background
      exact List.mem_append_left _ (List.mem_append_right _ ha)
    · exact absurd ⟨w, hw, hwl, Or.inr hadm⟩ hlayer
  · apply hother
    apply List.mem_map_of_mem
    simp only [otherAssumptions, List.mem_filter]
    refine ⟨hl, ?_⟩
    simp only [Bool.not_eq_true] at hb
    simp [hb, hlayer]

end VE.SoftNorms.Admission
