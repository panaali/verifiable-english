import VE.NormDefaults.Wire
import VE.Norms.Admission

/-! W2 admission under `norm-defaults@0` (docs/spec/norm-defaults.md 2.3 and 3.2):
W1's `Norms.Admission` on `fill U`.

Active `norm` units are decoded by the profile decoder (`decodeSourceU`); `E‴`,
`T‴` and `Fill_T` are regenerated from them. Graph nodes are decoded over `E‴`
(so a leaf may name an unsaid table), certificates bind the regenerated `E‴`
JSON, and graph leaves may name, beside W2's ordinary provenance, exactly a
regenerated layer premise of `T‴` (`layer:norms:<p>`), a regenerated pair premise
(`background:profile`), or a regenerated `Fill_T` premise under its label
(`unsaid:pair:<r>,<m>`). -/
namespace VE.NormDefaults.Admission
open Lean
open VE.Norms
open VE.Route.Admission
open VE.Bridge (exactFields stringField)
open VE.Norms.Admission (splitDocument checkBindings CertificateBound checkBindings_bound
  mapM_ok_mem forM_ok decodeNode_ast getArr_ok backgroundLeaf)
universe u

/-- The labels of `Fill_T`, in `fillPremises` order (`unsaid:pair:<r>,<m>`, 2.4). -/
def fillLabels (U : UDoc) : List String :=
  ((pairs U.D.T).filter (fun pr => pr.req ∈ U.unspec ∨ pr.perm ∈ U.unspec)).map fun pr =>
    s!"unsaid:pair:{pr.req},{pr.perm}"

def fillLabelled (U : UDoc) : List (String × VE.Formula) := (fillLabels U).zip (fillPremises U)

/-- The regenerated `E‴` JSON: the canonical placeholder environment (profile set aside,
`unspecified` read as `deny`) plus one base predicate `unsaid__p` per unspecified `p`. -/
def fillJson (environment : Json) (U : UDoc) : Except String Json := do
  let base ← VE.Norms.Wire.canonicalEnvironmentJson (← Wire.placeholderJson environment)
  let vocab ← base.getObjVal? "vocabulary"
  let preds ← VE.Bridge.fields (← vocab.getObjVal? "predicates")
  let extra := U.unspec.map fun p => (unsaidName p, Json.mkObj [("arguments", toJson (sortsOf U.D p)),
    ("description", .str (unsaidDescription p))])
  pure (base.setObjVal! "vocabulary" (vocab.setObjVal! "predicates" (Json.mkObj (preds ++ extra))))

/-- A quoted norm never contributes a layer, but it is still a norm object over
the source environment: W1's single-rule checks apply. -/
def checkQuoted (s : Wire.SourceU) (j : Json) : Except String Unit :=
  VE.Norms.Admission.checkQuoted s.src j

/-- A regenerated layer premise of `T‴` (`layer:norms:<p>`), with no unit pointer: over the `UDoc` it reads, so the
    layered soft branch (`LayeredAdmission.lean`) admits the same leaves of its own filled tree. -/
def LayerLeafU (U : UDoc) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone &&
    ((syms (fill U).T).filterMap (fun | .reg r => some r | .defn _ => none)).any
      (fun r => decide (w.claim.label = "layer:norms:" ++ r.name ∧
        w.claim.formula = elabPremise (fill U).T r))) = true

instance (U : UDoc) (w : WireNode) : Decidable (LayerLeafU U w) := by
  unfold LayerLeafU; infer_instance

def ProfileLeafU (U : UDoc) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone && w.claim.label == "background:profile" &&
    (pairPremises (fill U).T).any (fun a => decide (w.claim.formula = a))) = true

instance (U : UDoc) (w : WireNode) : Decidable (ProfileLeafU U w) := by
  unfold ProfileLeafU; infer_instance

/-- A regenerated `Fill_T` premise, under its exact label, with no unit pointer. -/
def FillLeafU (U : UDoc) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone &&
    (fillLabelled U).any (fun (l, a) => decide (w.claim.label = l ∧ w.claim.formula = a))) = true

instance (U : UDoc) (w : WireNode) : Decidable (FillLeafU U w) := by
  unfold FillLeafU; infer_instance

def LayerLeaf (s : Wire.SourceU) (w : WireNode) : Prop := LayerLeafU s.U w

instance (s : Wire.SourceU) (w : WireNode) : Decidable (LayerLeaf s w) := by
  unfold LayerLeaf; infer_instance

def ProfileLeaf (s : Wire.SourceU) (w : WireNode) : Prop := ProfileLeafU s.U w

instance (s : Wire.SourceU) (w : WireNode) : Decidable (ProfileLeaf s w) := by
  unfold ProfileLeaf; infer_instance

def FillLeaf (s : Wire.SourceU) (w : WireNode) : Prop := FillLeafU s.U w

instance (s : Wire.SourceU) (w : WireNode) : Decidable (FillLeaf s w) := by
  unfold FillLeaf; infer_instance

def NodeAdmitted (s : Wire.SourceU) (D : VE.Route.Admission.Doc) (w : WireNode) : Prop :=
  VE.Route.Admission.NodeAdmitted D w ∨ LayerLeaf s w ∨ ProfileLeaf s w ∨ FillLeaf s w

instance (s : Wire.SourceU) (D : VE.Route.Admission.Doc) (w : WireNode) :
    Decidable (NodeAdmitted s D w) := by
  unfold NodeAdmitted; infer_instance

def admitNodes (s : Wire.SourceU) (D : VE.Route.Admission.Doc) (ws : List WireNode) :
    Except String Unit :=
  match ws.find? (fun w => !decide (NodeAdmitted s D w)) with
  | some w => .error (VE.Route.Admission.nodeDiagnostic D w)
  | none => .ok ()

theorem admitNodes_ok (s : Wire.SourceU) (D : VE.Route.Admission.Doc) (ws : List WireNode)
    (h : admitNodes s D ws = .ok ()) : ∀ w ∈ ws, NodeAdmitted s D w := by
  unfold admitNodes at h
  split at h
  · cases h
  · rename_i hf
    intro w hw
    have := List.find?_eq_none.mp hf w hw
    simpa using this

open VE.Order.ProfileGate (bind_ok)

structure Admitted where
  s : Wire.SourceU
  doc : VE.Route.Admission.Doc
  /-- The regenerated `E‴` JSON that certificates bind. -/
  filled : Json
  graphJson : Json
  nodes : Array Json
  decoded : List (WireNode × Json)
  wires : List WireNode
  graph : VE.Graph.ClaimGraph VE.Tableau.Certificate
  report : VE.Graph.Report
  kinds : List Json

/-- W2's ordinary document decoder over `E‴`, with the source environment's
literals and flags. -/
def decodeFilledDoc (s : Wire.SourceU) (j : Json) : Except String VE.Route.Admission.Doc := do
  let E := (fill s.U).E
  let data := s.src.ne.profiles.contains "data@0"
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
  pure ⟨s.src.ne.rv.literals, s.src.ne.rv.flags, units, lemmas, openTerms, readingSets,
    narrowings⟩

/-- The profiles `E‴` carries: the source's, without `norm-defaults@0`. -/
def filledProfiles (s : Wire.SourceU) : List String :=
  s.src.ne.profiles.filter (· != Wire.profile)

def admitDocument (environment document : Json) : Except String Admitted := do
  VE.Bridge.displayFields document ["units", "graph"]
    ["lemmas", "open_terms", "reading_sets", "narrowings"]
  let (clean, norms, quoted) ← splitDocument document
  let s ← Wire.decodeSourceU environment norms
  VE.Route.Admission.require s.profiled "UnsupportedProfile: norm-defaults@0 is required"
  quoted.forM (checkQuoted s)
  let D₀ ← decodeFilledDoc s clean
  let D := { D₀ with literals := s.src.ne.rv.literals }
  let graphJson ← document.getObjVal? "graph"
  exactFields graphJson ["root", "nodes"]
  let root ← stringField graphJson "root"
  let nodeArray ← (← graphJson.getObjVal? "nodes").getArr?
  VE.Route.Admission.require (nodeArray.size ≤ 1000) "ResourceLimit: graph node count"
  let decoded ← nodeArray.toList.mapM
    (VE.Route.Admission.decodeNode (fill s.U).E (s.src.ne.profiles.contains "data@0"))
  let filled ← fillJson environment s.U
  VE.Norms.Admission.checkBindings (filledProfiles s) filled decoded
  let wires := decoded.map Prod.fst
  admitNodes s D wires
  let g : VE.Graph.ClaimGraph VE.Tableau.Certificate := ⟨wires.map WireNode.toNode, root⟩
  let r ← VE.Route.Admission.checkGraph (fill s.U).E g
  VE.Route.Admission.require (decide (CitationsClosed D r))
    "AdmissionError: a cited lemma's leaves are missing from the report"
  VE.Route.Admission.require (decide (ChoicesCompatible r))
    "AdmissionError: incompatible reading choices"
  pure ⟨s, D, filled, graphJson, nodeArray, decoded, wires, g, r,
    D.units.map (fun x => renderKind x.kind)⟩

def SourceDecoded (environment document : Json) (res : Admitted) : Prop :=
  (∃ clean norms quoted, splitDocument document = .ok (clean, norms, quoted) ∧
    Wire.decodeSourceU environment norms = .ok res.s ∧
    (∀ q ∈ quoted, checkQuoted res.s q = .ok ()) ∧
    ∃ D₀, decodeFilledDoc res.s clean = .ok D₀ ∧
      res.doc = { D₀ with literals := res.s.src.ne.rv.literals }) ∧
  res.s.profiled = true ∧ WellFormed (fill res.s.U) = true ∧
  (fill res.s.U).lits = res.s.src.ne.rv.literals ∧
  document.getObjVal? "graph" = .ok res.graphJson ∧
  res.graphJson.getObjVal? "nodes" = .ok (Json.arr res.nodes) ∧
  stringField res.graphJson "root" = .ok res.graph.root ∧
  res.wires = res.decoded.map Prod.fst ∧ res.graph.nodes = res.wires.map WireNode.toNode ∧
  (∀ x ∈ res.decoded, ∃ j ∈ res.nodes.toList,
    VE.Route.Admission.decodeNode (fill res.s.U).E (res.s.src.ne.profiles.contains "data@0") j = .ok x ∧
    j.getObjVal? "ast" = .ok x.2 ∧
    VE.Route.Wire.decodeClosed (fill res.s.U).E x.2
      ((res.s.src.ne.profiles.contains "data@0") && !x.1.claim.label.startsWith "background:") =
        .ok x.1.claim.formula)

/-- Every certificate is bound to the regenerated `E‴` and the source ASTs of its premises
and conclusion. -/
def CertificatesBound (environment : Json) (res : Admitted) : Prop :=
  fillJson environment res.s.U = .ok res.filled ∧
  ∀ x ∈ res.decoded, CertificateBound (filledProfiles res.s) res.filled res.decoded x

def ReportAdmitted (res : Admitted) : Prop :=
  VE.Graph.SoundReport.{0} (fill res.s.U).E res.graph res.report ∧
  (∀ w ∈ res.wires, NodeAdmitted res.s res.doc w) ∧
  (∀ leaf ∈ res.report.assumptions, ∃ w ∈ res.wires,
    w.claim = leaf ∧ w.deduction = none ∧ NodeAdmitted res.s res.doc w) ∧
  CitationsClosed res.doc res.report ∧ ChoicesCompatible res.report

theorem fill_lits_source (s : Wire.SourceU) : (fill s.U).lits = s.src.ne.rv.literals := by
  rw [fill_lits, s.doc]; exact s.src.lits

theorem admitDocument_spec (environment document : Json) (res : Admitted)
    (h : admitDocument environment document = .ok res) :
    SourceDecoded environment document res ∧ CertificatesBound environment res ∧
    VE.Graph.SoundReport.{u} (fill res.s.U).E res.graph res.report ∧
    (∀ w ∈ res.wires, NodeAdmitted res.s res.doc w) ∧
    (∀ leaf ∈ res.report.assumptions, ∃ w ∈ res.wires,
      w.claim = leaf ∧ w.deduction = none ∧ NodeAdmitted res.s res.doc w) ∧
    CitationsClosed res.doc res.report ∧ ChoicesCompatible res.report := by
  unfold admitDocument at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨⟨clean, norms, quoted⟩, hsplit, h⟩ := bind_ok h
  obtain ⟨s, hsrc, h⟩ := bind_ok h
  obtain ⟨_, hprof, h⟩ := bind_ok h
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
  obtain ⟨r, hr, h⟩ := bind_ok h
  obtain ⟨_, hc, h⟩ := bind_ok h
  obtain ⟨_, hch, h⟩ := bind_ok h
  cases h
  have hnodes := admitNodes_ok s _ (decoded.map Prod.fst) hadm
  obtain ⟨_, _, _, hsound⟩ := VE.Graph.check_sound.{u} (fill s.U).E _ r
    (VE.Route.Admission.checkGraph_ok _ _ r hr)
  have hnj' : nj = Json.arr nodeArray := getArr_ok harr
  subst hnj'
  refine ⟨⟨⟨clean, norms, quoted, hsplit, hsrc, forM_ok _ quoted hq, D₀, hD, rfl⟩,
      VE.Route.Gate.require_ok hprof, s.wfFill, fill_lits_source s, hg, hnj, hroot, rfl, rfl, ?_⟩,
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

theorem layerLeaf_formula (s : Wire.SourceU) (w : WireNode) (h : LayerLeaf s w) :
    w.claim.formula ∈ elaborate (fill s.U).T := by
  simp only [LayerLeaf, LayerLeafU, Bool.and_eq_true] at h
  obtain ⟨r, hr, he⟩ := List.any_eq_true.mp h.2
  have heq : w.claim.label = "layer:norms:" ++ r.name ∧
      w.claim.formula = elabPremise (fill s.U).T r := of_decide_eq_true he
  rw [heq.2]
  change elabPremise (fill s.U).T r ∈
    (syms (fill s.U).T).filterMap (fun | .reg r => some (elabPremise (fill s.U).T r) | .defn _ => none)
  obtain ⟨q, hq, hqr⟩ := List.mem_filterMap.mp
    (show r ∈ (syms (fill s.U).T).filterMap (fun | .reg r => some r | .defn _ => none) from hr)
  cases q with
  | reg r' =>
    simp only [Option.some.injEq] at hqr
    subst hqr
    exact List.mem_filterMap.mpr ⟨.reg r', hq, rfl⟩
  | defn d => cases hqr

theorem fillLeaf_formula (s : Wire.SourceU) (w : WireNode) (h : FillLeaf s w) :
    w.claim.formula ∈ fillPremises s.U := by
  simp only [FillLeaf, FillLeafU, Bool.and_eq_true] at h
  obtain ⟨⟨l, a⟩, hm, he⟩ := List.any_eq_true.mp h.2
  have heq : w.claim.label = l ∧ w.claim.formula = a := of_decide_eq_true he
  rw [heq.2]
  exact (List.of_mem_zip hm).2

/-- The report assumptions that stay explicit hypotheses: every leaf that is neither a
regenerated layer leaf, a regenerated `Fill_T` leaf nor a Background leaf. -/
def otherAssumptions (res : Admitted) : List VE.Graph.Claim :=
  res.report.assumptions.filter (fun c =>
    !backgroundLeaf c && !decide (∃ w ∈ res.wires, w.claim = c ∧ (LayerLeaf res.s w ∨ FillLeaf res.s w)))

/-- Semantic report consequence: in every structure admissible for `E‴` satisfying the
regenerated Background of `fill U`, `Fill_T` and the layer premises of `T‴`, the
remaining assumptions entail the root. -/
theorem wire_report_consequence (environment document : Json) (res : Admitted)
    (h : admitDocument environment document = .ok res) (S : VE.Structure.{u})
    (hS : S.Admissible (fill res.s.U).E)
    (hflags : Sat S (VE.Data.Background.generate res.doc.flags))
    (hregen : Sat S (background (fill res.s.U) ++ fillPremises res.s.U ++ elaborate (fill res.s.U).T))
    (hother : Sat S ((otherAssumptions res).map (·.formula))) :
    res.report.root.formula.denote S [] := by
  obtain ⟨⟨⟨_, _, _, _, _, _, _, _, hdoc⟩, _, _, hlits, _⟩, _, hsound, _, hleaves, _⟩ :=
    admitDocument_spec.{u} environment document res h
  apply hsound.2.2.2.1 S hS
  intro a ha
  obtain ⟨leaf, hl, rfl⟩ := List.mem_map.mp ha
  by_cases hlayer : ∃ w ∈ res.wires, w.claim = leaf ∧ (LayerLeaf res.s w ∨ FillLeaf res.s w)
  · obtain ⟨w, _, hwl, hw⟩ := hlayer
    rw [← hwl]
    rcases hw with hw | hw
    · exact hregen _ (List.mem_append_right _ (layerLeaf_formula res.s w hw))
    · exact hregen _ (List.mem_append_left _ (List.mem_append_right _ (fillLeaf_formula res.s w hw)))
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
          apply List.mem_append_left
          unfold background backgroundBase
          apply List.mem_append_left
          apply List.mem_append_right
          rw [hlits, ← (show res.doc.literals = res.s.src.ne.rv.literals by rw [hdoc])]
          exact hbm
      · cases hb
    · exact absurd ⟨w, hw, hwl, Or.inl hadm⟩ hlayer
    · simp only [ProfileLeaf, ProfileLeafU, Bool.and_eq_true] at hadm
      obtain ⟨a, ha, hfa⟩ := List.any_eq_true.mp hadm.2
      rw [← hwl, of_decide_eq_true hfa]
      apply hregen
      apply List.mem_append_left
      apply List.mem_append_left
      unfold background
      exact List.mem_append_right _ ha
    · exact absurd ⟨w, hw, hwl, Or.inr hadm⟩ hlayer
  · apply hother
    apply List.mem_map_of_mem
    simp only [otherAssumptions, List.mem_filter]
    refine ⟨hl, ?_⟩
    simp only [Bool.not_eq_true] at hb
    simp [hb, hlayer]

end VE.NormDefaults.Admission
