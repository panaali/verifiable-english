import VE.NormDefaults.LayeredEntail
import VE.NormDefaults.Admission
import VE.SoftNorms.Admission
import VE.Norms.Run

/-! The soft branch's `admission` and `norm-defaults-certificate` under `norm-defaults@0`
(docs/spec/rd-9-soft-chain.md 1.13, 4.5 and 6.10; plan SC-6).

`layeredCase` answers the `norm-defaults-*` kinds of a layered source that read its regenerated outputs; it has no
admission and no certificate kind. `softCase` answers both for a soft source (`layeredRoute = some "soft-norms@0"`),
and `Run.runCase` calls it before every other branch. Nothing here changes `layeredCase`.

* `norm-defaults-certificate` (`replayLayeredEntailment`): the source decoded by `decodeSoftU`, the premises and the
  conclusion decoded over `envAt (fill L.U) (size (fill L.U))`, the certificate bound by the one binder `bindCertX`
  to the source environment, the regenerated `premisesX L.U L.X []` and the case's premises and conclusion as
  written; `valid` is the check over `premisesX L.U L.X premises` (`layered_wire_acceptance`).
* `admission` (`admitDocumentX`): W1's `Norms.Admission` on the filled tree, in today's order: W2's split, the soft
  source over the placeholder completions (`decodeSoftU`, and the soft source `src` it reads), the quoted norms
  checked as the soft route checks them, the units decoded by W2's `decodeDoc` over `E‴`, the graph's nodes decoded
  over `E‴`, certificates bound to the regenerated soft `E‴` JSON (`filledJsonX`), every node admitted
  (`NodeAdmittedX`: W2 provenance, a regenerated layer or pair premise of the filled tree, a regenerated soft premise
  `soft:exception:…`/`soft:coherence:…`, or a `Fill_T` premise), and the graph checked. `admitDocumentX_spec` keeps
  the source correspondence (`SourceDecodedX`), and `wire_report_consequenceX` the report's consequence. -/
namespace VE.NormDefaults.Wire
open Lean
open VE.Norms
universe u

open VE.Order.ProfileGate (bind_ok)

/-- What `decodeSoftU` builds `L` from: the soft source over the placeholder completions, its softened and filled
    tree, and soft's premises regenerated on it. -/
theorem decodeSoftU_source (environment norms : Json) (L : LayeredU) (h : decodeSoftU environment norms = .ok L) :
    ∃ env' src, placeholderJson environment = .ok env' ∧ VE.SoftNorms.Wire.decodeSoftSource env' norms = .ok src ∧
      L.D = src.D ∧ L.U = ⟨VE.SoftNorms.soften src.D, unspecOf environment (VE.SoftNorms.soften src.D)⟩ ∧
      L.labelled = softLabelledU L.U src.D ∧ L.rightsCount = 0 ∧ L.route = "soft-norms@0" := by
  unfold decodeSoftU at h
  obtain ⟨env', he, h⟩ := bind_ok h
  obtain ⟨src, hs, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  split at h
  · obtain ⟨_, _, h⟩ := bind_ok h
    obtain ⟨_, _, h⟩ := bind_ok h
    obtain ⟨_, _, h⟩ := bind_ok h
    obtain ⟨_, _, h⟩ := bind_ok h
    obtain ⟨_, _, h⟩ := bind_ok h
    cases h
    exact ⟨env', src, he, hs, rfl, rfl, rfl, rfl, rfl⟩
  · cases h

theorem decodeSoftU_X_wellFormed (environment norms : Json) (L : LayeredU) (h : decodeSoftU environment norms = .ok L) :
    ∀ a ∈ L.X, a.WellFormed (envAt (fill L.U) 0) [] := by
  obtain ⟨_, src, _, _, _, hU, hl, _⟩ := decodeSoftU_source environment norms L h
  have hw := L.wfU
  unfold LayeredU.X
  rw [hl]
  rw [hU] at hw ⊢
  exact softLabelledU_wellFormed src.D _ src.wf hw

structure LayeredEntailment where
  L : LayeredU
  hX : ∀ a ∈ L.X, a.WellFormed (envAt (fill L.U) 0) []
  premises : List VE.Formula
  conclusion : VE.Formula
  cert : VE.Tableau.Certificate
  valid : Bool
  hvalid : valid = VE.Tableau.checkCertificate (envAt (fill L.U) (size (fill L.U)))
    (premisesX L.U L.X premises) conclusion cert
/-- 4.5: `decodeSoftU`, the formulas over `envAt (fill L.U) (size (fill L.U))`, `bindCertX environment L.U L.X []`. -/
def replayLayeredEntailment (j : Json) : Except String LayeredEntailment := do
  let environment ← j.getObjVal? "environment"
  let norms := j.getObjValD "norms"
  match hL : decodeSoftU environment norms with
  | .error e => throw e
  | .ok L =>
    let E := envAt (fill L.U) (size (fill L.U))
    let premisesJson ← j.getObjVal? "premises"
    let ps ← VE.Route.Wire.decodeFormulas E premisesJson
    let conclusionJson ← j.getObjVal? "conclusion"
    let c ← VE.Route.Wire.decodeClosed E conclusionJson
    let cert ← bindCertX environment L.U L.X [] (← premisesJson.getArr?).toList conclusionJson
      (← j.getObjVal? "certificate")
    pure ⟨L, decodeSoftU_X_wellFormed environment norms L hL, ps, c, cert,
      VE.Tableau.checkCertificate E (premisesX L.U L.X ps) c cert, rfl⟩

theorem layered_wire_acceptance (j : Json) (r : LayeredEntailment) (h : replayLayeredEntailment j = .ok r)
    (hv : r.valid = true) : VE.NormDefaults.EntailsX.{u} r.L.U r.L.X r.premises r.conclusion :=
  have _ := h
  VE.NormDefaults.acceptanceX r.L.U r.L.wfU r.L.X r.hX r.premises r.conclusion r.cert (r.hvalid ▸ hv)

end VE.NormDefaults.Wire

namespace VE.NormDefaults.Admission
open Lean
open VE.Norms
open VE.Route.Admission
open VE.Bridge (exactFields stringField)
open VE.Norms.Admission (splitDocument checkBindings CertificateBound checkBindings_bound
  mapM_ok_mem forM_ok decodeNode_ast getArr_ok backgroundLeaf)
universe u

/-- A regenerated soft premise of the filled tree (`soft:exception:…`, `soft:coherence:…`), under its label, with no
    unit pointer. -/
def SoftLeafX (L : Wire.LayeredU) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone &&
    (L.labelled.take (L.labelled.length - L.rightsCount)).any
      (fun (l, a) => decide (w.claim.label = l ∧ w.claim.formula = a))) = true

instance (L : Wire.LayeredU) (w : WireNode) : Decidable (SoftLeafX L w) := by
  unfold SoftLeafX; infer_instance

def NodeAdmittedX (L : Wire.LayeredU) (D : VE.Route.Admission.Doc) (w : WireNode) : Prop :=
  VE.Route.Admission.NodeAdmitted D w ∨ LayerLeafU L.U w ∨ ProfileLeafU L.U w ∨ SoftLeafX L w ∨ FillLeafU L.U w

instance (L : Wire.LayeredU) (D : VE.Route.Admission.Doc) (w : WireNode) : Decidable (NodeAdmittedX L D w) := by
  unfold NodeAdmittedX; infer_instance

/-- Every node admitted, else the first one's diagnostic (W1's admission text). -/
def admitNodesX (L : Wire.LayeredU) (D : VE.Route.Admission.Doc) (ws : List WireNode) : Except String Unit :=
  match ws.find? (fun w => !decide (NodeAdmittedX L D w)) with
  | some w => .error (VE.Route.Admission.nodeDiagnostic D w)
  | none => .ok ()

theorem admitNodesX_ok (L : Wire.LayeredU) (D : VE.Route.Admission.Doc) (ws : List WireNode)
    (h : admitNodesX L D ws = .ok ()) : ∀ w ∈ ws, NodeAdmittedX L D w := by
  unfold admitNodesX at h
  split at h
  · cases h
  · rename_i hf
    intro w hw
    have := List.find?_eq_none.mp hf w hw
    simpa using this

structure AdmittedX where
  L : Wire.LayeredU
  doc : VE.Route.Admission.Doc
  filled : Json
  graphJson : Json
  nodes : Array Json
  decoded : List (WireNode × Json)
  wires : List WireNode
  graph : VE.Graph.ClaimGraph VE.Tableau.Certificate
  report : VE.Graph.Report
  kinds : List Json

def filledJsonX (environment : Json) (L : Wire.LayeredU) : Except String Json := do
  Wire.withUnsaid L.U (← VE.SoftNorms.Wire.primeJson L.D (← Wire.placeholderJson environment))
def filledProfilesX (environment : Json) : List String := (Wire.profilesOf environment).filter (· != Wire.profile)

open VE.Order.ProfileGate (bind_ok)

/-- 4.5. -/
def admitDocumentX (environment document : Json) : Except String AdmittedX := do
  VE.Bridge.displayFields document ["units", "graph"]
    ["lemmas", "open_terms", "reading_sets", "narrowings"]
  let (clean, norms, quoted) ← splitDocument document
  let L ← Wire.decodeSoftU environment norms
  VE.Route.Admission.require (Wire.layeredRoute environment == some "soft-norms@0")
    "UnsupportedProfile: the layered norm-defaults branch needs soft-norms@0"
  let src ← VE.SoftNorms.Wire.decodeSoftSource (← Wire.placeholderJson environment) norms
  quoted.forM (VE.SoftNorms.Admission.checkQuoted src)
  let data := src.se.profiles.contains "data@0"
  let D₀ ← VE.Route.Admission.decodeDoc src.se.ne.rv data clean (fill L.U).E
  let D := { D₀ with literals := src.se.ne.rv.literals }
  let graphJson ← document.getObjVal? "graph"
  exactFields graphJson ["root", "nodes"]
  let root ← stringField graphJson "root"
  let nodeArray ← (← graphJson.getObjVal? "nodes").getArr?
  VE.Route.Admission.require (nodeArray.size ≤ 1000) "ResourceLimit: graph node count"
  let decoded ← nodeArray.toList.mapM (VE.Route.Admission.decodeNode (fill L.U).E data)
  let filled ← filledJsonX environment L
  VE.Norms.Admission.checkBindings (filledProfilesX environment) filled decoded
  let wires := decoded.map Prod.fst
  admitNodesX L D wires
  let g : VE.Graph.ClaimGraph VE.Tableau.Certificate := ⟨wires.map WireNode.toNode, root⟩
  let r ← VE.Route.Admission.checkGraph (fill L.U).E g
  VE.Route.Admission.require (decide (CitationsClosed D r))
    "AdmissionError: a cited lemma's leaves are missing from the report"
  VE.Route.Admission.require (decide (ChoicesCompatible r))
    "AdmissionError: incompatible reading choices"
  pure ⟨L, D, filled, graphJson, nodeArray, decoded, wires, g, r, D.units.map (fun x => renderKind x.kind)⟩

def otherAssumptionsX (res : AdmittedX) : List VE.Graph.Claim :=
  res.report.assumptions.filter (fun c =>
    !VE.Norms.Admission.backgroundLeaf c && !decide (∃ w ∈ res.wires, w.claim = c ∧
      (decide (LayerLeafU res.L.U w) || decide (FillLeafU res.L.U w) || decide (SoftLeafX res.L w)) = true))
def ReportAdmittedX (res : AdmittedX) : Prop :=
  VE.Graph.SoundReport.{0} (fill res.L.U).E res.graph res.report ∧
  (∀ w ∈ res.wires, NodeAdmittedX res.L res.doc w) ∧
  (∀ leaf ∈ res.report.assumptions, ∃ w ∈ res.wires,
    w.claim = leaf ∧ w.deduction = none ∧ NodeAdmittedX res.L res.doc w) ∧
  CitationsClosed res.doc res.report ∧ ChoicesCompatible res.report
/-- Today's `SourceDecoded` (`Admission.lean:168–185`) over `res.L`, conjunct by conjunct. The soft source `src` is
    the one `decodeSoftU` builds `L` from, over the placeholder completions. -/
def SourceDecodedX (environment document : Json) (res : AdmittedX) : Prop :=
  (∃ clean norms quoted env' src, VE.Norms.Admission.splitDocument document = .ok (clean, norms, quoted) ∧
    Wire.decodeSoftU environment norms = .ok res.L ∧
    Wire.placeholderJson environment = .ok env' ∧ VE.SoftNorms.Wire.decodeSoftSource env' norms = .ok src ∧
    res.L.D = src.D ∧
    (∀ q ∈ quoted, VE.SoftNorms.Admission.checkQuoted src q = .ok ()) ∧
    (∃ D₀, VE.Route.Admission.decodeDoc src.se.ne.rv (src.se.profiles.contains "data@0") clean (fill res.L.U).E =
        .ok D₀ ∧ res.doc = { D₀ with literals := src.se.ne.rv.literals }) ∧
    (fill res.L.U).lits = src.se.ne.rv.literals ∧
    (∀ x ∈ res.decoded, ∃ j ∈ res.nodes.toList,
      VE.Route.Admission.decodeNode (fill res.L.U).E (src.se.profiles.contains "data@0") j = .ok x ∧
      j.getObjVal? "ast" = .ok x.2 ∧
      VE.Route.Wire.decodeClosed (fill res.L.U).E x.2
        ((src.se.profiles.contains "data@0") && !x.1.claim.label.startsWith "background:") =
          .ok x.1.claim.formula)) ∧
  Wire.layeredRoute environment = some "soft-norms@0" ∧ WellFormed (fill res.L.U) = true ∧
  document.getObjVal? "graph" = .ok res.graphJson ∧
  res.graphJson.getObjVal? "nodes" = .ok (Json.arr res.nodes) ∧
  VE.Bridge.stringField res.graphJson "root" = .ok res.graph.root ∧
  res.wires = res.decoded.map Prod.fst ∧ res.graph.nodes = res.wires.map WireNode.toNode
def CertificatesBoundX (environment : Json) (res : AdmittedX) : Prop :=
  filledJsonX environment res.L = .ok res.filled ∧
  ∀ x ∈ res.decoded, VE.Norms.Admission.CertificateBound (filledProfilesX environment) res.filled res.decoded x

theorem admitDocumentX_spec (environment document : Json) (res : AdmittedX)
    (h : admitDocumentX environment document = .ok res) :
    SourceDecodedX environment document res ∧ CertificatesBoundX environment res ∧
    VE.Graph.SoundReport.{u} (fill res.L.U).E res.graph res.report ∧
    (∀ w ∈ res.wires, NodeAdmittedX res.L res.doc w) ∧
    (∀ leaf ∈ res.report.assumptions, ∃ w ∈ res.wires,
      w.claim = leaf ∧ w.deduction = none ∧ NodeAdmittedX res.L res.doc w) ∧
    CitationsClosed res.doc res.report ∧ ChoicesCompatible res.report := by
  unfold admitDocumentX at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨⟨clean, norms, quoted⟩, hsplit, h⟩ := bind_ok h
  obtain ⟨L, hL, h⟩ := bind_ok h
  obtain ⟨_, hroute, h⟩ := bind_ok h
  obtain ⟨env', he, h⟩ := bind_ok h
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
  obtain ⟨filled, hfilled, h⟩ := bind_ok h
  obtain ⟨_, hbind, h⟩ := bind_ok h
  obtain ⟨_, hadm, h⟩ := bind_ok h
  obtain ⟨r, hrep, h⟩ := bind_ok h
  obtain ⟨_, hc, h⟩ := bind_ok h
  obtain ⟨_, hch, h⟩ := bind_ok h
  cases h
  obtain ⟨env'', src', he', hsrc', hLD, hU, _⟩ := Wire.decodeSoftU_source environment norms L hL
  rw [he] at he'
  cases he'
  rw [hsrc] at hsrc'
  cases hsrc'
  have hnodes := admitNodesX_ok L _ (decoded.map Prod.fst) hadm
  obtain ⟨_, _, _, hsound⟩ := VE.Graph.check_sound.{u} (fill L.U).E _ r
    (VE.Route.Admission.checkGraph_ok _ _ r hrep)
  have hnj' : nj = Json.arr nodeArray := getArr_ok harr
  subst hnj'
  have hlits : (fill L.U).lits = src.se.ne.rv.literals := by
    rw [fill_lits, hU]; exact src.lits
  refine ⟨⟨⟨clean, norms, quoted, env', src, hsplit, hL, he, hsrc, hLD, forM_ok _ quoted hq, ⟨D₀, hD, rfl⟩,
      hlits, ?_⟩, by simpa using VE.Route.Gate.require_ok hroute, fill_wellFormed L.U L.wfU, hg, hnj, hroot, rfl, rfl⟩,
    ⟨hfilled, checkBindings_bound _ _ decoded hbind⟩, hsound, hnodes, ?_,
    of_decide_eq_true (VE.Route.Gate.require_ok hc),
    of_decide_eq_true (VE.Route.Gate.require_ok hch)⟩
  · intro x hx
    obtain ⟨j, hj, hd⟩ := mapM_ok_mem _ _ decoded hdec x hx
    exact ⟨j, hj, hd, decodeNode_ast _ _ j x hd⟩
  · intro leaf hl
    obtain ⟨node, hn, hcl, hde⟩ := (hsound.2.2.1 leaf hl).2
    obtain ⟨w, hw, rfl⟩ := List.mem_map.mp hn
    exact ⟨w, hw, hcl, hde, hnodes w hw⟩

theorem layerLeafU_formula (U : UDoc) (w : WireNode) (h : LayerLeafU U w) :
    w.claim.formula ∈ elaborate (fill U).T := by
  simp only [LayerLeafU, Bool.and_eq_true] at h
  obtain ⟨r, hr, he⟩ := List.any_eq_true.mp h.2
  have heq : w.claim.label = "layer:norms:" ++ r.name ∧
      w.claim.formula = elabPremise (fill U).T r := of_decide_eq_true he
  rw [heq.2]
  change elabPremise (fill U).T r ∈
    (syms (fill U).T).filterMap (fun | .reg r => some (elabPremise (fill U).T r) | .defn _ => none)
  obtain ⟨q, hq, hqr⟩ := List.mem_filterMap.mp
    (show r ∈ (syms (fill U).T).filterMap (fun | .reg r => some r | .defn _ => none) from hr)
  cases q with
  | reg r' =>
    simp only [Option.some.injEq] at hqr
    subst hqr
    exact List.mem_filterMap.mpr ⟨.reg r', hq, rfl⟩
  | defn d => cases hqr

theorem fillLeafU_formula (U : UDoc) (w : WireNode) (h : FillLeafU U w) : w.claim.formula ∈ fillPremises U := by
  simp only [FillLeafU, Bool.and_eq_true] at h
  obtain ⟨⟨l, a⟩, hm, he⟩ := List.any_eq_true.mp h.2
  have heq : w.claim.label = l ∧ w.claim.formula = a := of_decide_eq_true he
  rw [heq.2]
  exact (List.of_mem_zip hm).2

theorem softLeafX_formula (L : Wire.LayeredU) (w : WireNode) (h : SoftLeafX L w) : w.claim.formula ∈ L.X := by
  simp only [SoftLeafX, Bool.and_eq_true] at h
  obtain ⟨⟨l, a⟩, hm, he⟩ := List.any_eq_true.mp h.2
  have heq : w.claim.label = l ∧ w.claim.formula = a := of_decide_eq_true he
  rw [heq.2]
  exact List.mem_map.mpr ⟨(l, a), List.mem_of_mem_take hm, rfl⟩

theorem wire_report_consequenceX (environment document : Json) (res : AdmittedX)
    (h : admitDocumentX environment document = .ok res) (S : VE.Structure.{u}) (hS : S.Admissible (fill res.L.U).E)
    (hflags : Sat S (VE.Data.Background.generate res.doc.flags))
    (hregen : Sat S (background (fill res.L.U) ++ res.L.X ++ fillPremises res.L.U ++ elaborate (fill res.L.U).T))
    (hother : Sat S ((otherAssumptionsX res).map (·.formula))) :
    res.report.root.formula.denote S [] := by
  obtain ⟨⟨⟨_, _, _, _, src, _, _, _, _, _, _, ⟨_, _, hdoc⟩, hlits, _⟩, _⟩, _, hsound, _, hleaves, _⟩ :=
    admitDocumentX_spec.{u} environment document res h
  apply hsound.2.2.2.1 S hS
  intro a ha
  obtain ⟨leaf, hl, rfl⟩ := List.mem_map.mp ha
  by_cases hlayer : ∃ w ∈ res.wires, w.claim = leaf ∧
      (decide (LayerLeafU res.L.U w) || decide (FillLeafU res.L.U w) || decide (SoftLeafX res.L w)) = true
  · obtain ⟨w, _, hwl, hw⟩ := hlayer
    rw [← hwl]
    simp only [Bool.or_eq_true, decide_eq_true_eq] at hw
    rcases hw with (hw | hw) | hw
    · exact hregen _ (List.mem_append_right _ (layerLeafU_formula res.L.U w hw))
    · exact hregen _ (List.mem_append_left _ (List.mem_append_right _ (fillLeafU_formula res.L.U w hw)))
    · exact hregen _ (List.mem_append_left _ (List.mem_append_left _
        (List.mem_append_right _ (softLeafX_formula res.L w hw))))
  by_cases hb : backgroundLeaf leaf = true
  · obtain ⟨w, hw, hwl, hde, hadm⟩ := hleaves leaf hl
    rcases hadm with hadm | hadm | hadm | hadm | hadm
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
          apply List.mem_append_left
          apply List.mem_append_left
          unfold background backgroundBase
          apply List.mem_append_left
          apply List.mem_append_right
          rw [hlits, ← (show res.doc.literals = src.se.ne.rv.literals by rw [hdoc])]
          exact hbm
      · cases hb
    · exact absurd ⟨w, hw, hwl, by simp [hadm]⟩ hlayer
    · simp only [ProfileLeafU, Bool.and_eq_true] at hadm
      obtain ⟨a, ha, hfa⟩ := List.any_eq_true.mp hadm.2
      rw [← hwl, of_decide_eq_true hfa]
      apply hregen
      apply List.mem_append_left
      apply List.mem_append_left
      apply List.mem_append_left
      unfold background
      exact List.mem_append_right _ ha
    · exact absurd ⟨w, hw, hwl, by simp [hadm]⟩ hlayer
    · exact absurd ⟨w, hw, hwl, by simp [hadm]⟩ hlayer
  · apply hother
    apply List.mem_map_of_mem
    simp only [otherAssumptionsX, List.mem_filter]
    refine ⟨hl, ?_⟩
    simp only [Bool.not_eq_true] at hb
    simp only [hb, Bool.not_false, Bool.true_and, Bool.not_eq_eq_eq_not, Bool.not_true, decide_eq_false_iff_not]
    exact hlayer

/-- The open coherence labels the report uses, as the soft route's admission answer lists them. -/
def conditionalOnX (res : AdmittedX) : List String :=
  (VE.SoftNorms.Wire.openCoherence res.L.D).filter (fun l => res.report.assumptions.any (fun c => c.label == l))
def encodeAdmittedX (id reportId : String) (res : AdmittedX) : Json :=
  VE.Route.Wire.ok id [("admitted", .bool true), ("report", VE.Norms.Run.reportJson res.report),
    ("report_id", .str reportId), ("kinds", Json.arr res.kinds.toArray),
    ("conditional_on", toJson (conditionalOnX res))]
def AdmissionAnswerX (id : String) (environment document answer : Json) : Prop :=
  ∃ res : AdmittedX, ∃ reportId : String,
    admitDocumentX environment document = .ok res ∧
    answer = encodeAdmittedX id reportId res ∧
    SourceDecodedX environment document res ∧
    CertificatesBoundX environment res ∧
    ReportAdmittedX res ∧
    (∃ canonical envId, Wire.canonicalEnvironmentJsonU environment = .ok canonical ∧
      VE.Route.Wire.environmentId (Wire.profilesOf environment) canonical = .ok envId ∧
      VE.CertificateWire.digest (VE.Norms.Run.reportDomain (Wire.profilesOf environment))
        (VE.Norms.Run.reportPayload envId document res.report) = .ok reportId) ∧
    (∀ S : VE.Structure.{0}, S.Admissible (fill res.L.U).E →
      Sat S (VE.Data.Background.generate res.doc.flags) →
      Sat S (background (fill res.L.U) ++ res.L.X ++ fillPremises res.L.U ++ elaborate (fill res.L.U).T) →
      Sat S ((otherAssumptionsX res).map (·.formula)) →
      res.report.root.formula.denote S [])

/-- The admission answer: the report id bound to the source environment under its own profiles, as `runAdmission`
    binds it. -/
def runAdmissionX (id : String) (environment document : Json) : Except String Json := do
  let res ← admitDocumentX environment document
  let canonical ← Wire.canonicalEnvironmentJsonU environment
  let envId ← VE.Route.Wire.environmentId (Wire.profilesOf environment) canonical
  let reportId ← VE.CertificateWire.digest (VE.Norms.Run.reportDomain (Wire.profilesOf environment))
    (VE.Norms.Run.reportPayload envId document res.report)
  return encodeAdmittedX id reportId res

theorem runAdmissionX_sound (id : String) (environment document answer : Json)
    (h : runAdmissionX id environment document = .ok answer) :
    AdmissionAnswerX id environment document answer := by
  unfold runAdmissionX at h
  obtain ⟨res, hres, h⟩ := bind_ok h
  obtain ⟨canonical, hc, h⟩ := bind_ok h
  obtain ⟨envId, he, h⟩ := bind_ok h
  obtain ⟨reportId, hd, h⟩ := bind_ok h
  cases h
  obtain ⟨hsrc, hbound, hsound, hnodes, hleaves, hcit, hch⟩ :=
    admitDocumentX_spec.{0} environment document res hres
  exact ⟨res, reportId, hres, rfl, hsrc, hbound, ⟨hsound, hnodes, hleaves, hcit, hch⟩,
    ⟨canonical, envId, hc, he, hd⟩,
    fun S hS hf hg ho => wire_report_consequenceX environment document res hres S hS hf hg ho⟩

/-- The soft branch's two kinds `layeredCase` lacks: `admission` and `norm-defaults-certificate`; `none` otherwise. -/
def softCase (id kind : String) (j : Json) : Except String (Option Json) := do
  if kind == "admission" then
    let environment ← j.getObjVal? "environment"
    let document ← j.getObjVal? "document"
    return some (← runAdmissionX id environment document)
  if kind == "norm-defaults-certificate" then
    let r ← Wire.replayLayeredEntailment j
    return some (VE.Route.Wire.ok id [("valid", .bool r.valid),
      ("premises", toJson (Wire.premisesX r.L.U r.L.X []).length)])
  return none

end VE.NormDefaults.Admission
