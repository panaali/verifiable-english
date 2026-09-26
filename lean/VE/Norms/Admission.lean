import VE.Norms.Replay
import VE.Route.Admission

/-! W2 admission on the norms route. Norm content is decoded as a rule only for
active `norm` units. Its FOL premises are regenerated from that rule set; graph
leaves may name those premises, while every other leaf follows W2 admission. -/
namespace VE.Norms.Admission
open Lean
open VE.Route.Admission
open VE.Bridge (exactFields stringField)
universe u

/-- Remove norm content only from the copy passed to the FOL unit decoder.
The original source document remains intact for report identity. -/
def splitUnit (j : Json) : Except String (Json × Option Json) := do
  match j.getObjVal? "content" with
  | .ok content =>
    if (content.getObjVal? "norm").toBool then
      let kind ← decodeKind 16 (← j.getObjVal? "kind")
      let active := if kind == .norm then some content else none
      let obj ← VE.Bridge.fields j
      return (Json.mkObj (obj.filter (·.1 != "content")), active)
    else return (j, none)
  | .error _ => return (j, none)

def splitDocument (j : Json) : Except String (Json × Json) := do
  let units ← (← (← j.getObjVal? "units").getArr?).toList.mapM splitUnit
  let clean := j.setObjVal! "units" (Json.arr (units.map Prod.fst).toArray)
  let active := Json.arr (units.filterMap Prod.snd).toArray
  pure (clean, active)

/-- Exact regenerated layer leaf, with no unit pointer. -/
def LayerLeaf (src : Wire.Source) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone &&
    ((syms src.D.T).filterMap (fun | .reg r => some r | .defn _ => none)).any
      (fun r => decide (w.claim.label = "layer:norms:" ++ r.name ∧
        w.claim.formula = elabPremise src.D.T r))) = true

instance (src : Wire.Source) (w : WireNode) : Decidable (LayerLeaf src w) := by
  unfold LayerLeaf
  infer_instance

def NodeAdmitted (src : Wire.Source) (D : VE.Route.Admission.Doc) (w : WireNode) : Prop :=
  VE.Route.Admission.NodeAdmitted D w ∨ LayerLeaf src w

instance (src : Wire.Source) (D : VE.Route.Admission.Doc) (w : WireNode) :
    Decidable (NodeAdmitted src D w) := by
  unfold NodeAdmitted; infer_instance

def admitNodes (src : Wire.Source) (D : VE.Route.Admission.Doc) (ws : List WireNode) :
    Except String Unit :=
  match ws.find? (fun w => !decide (NodeAdmitted src D w)) with
  | some w => .error (VE.Route.Admission.nodeDiagnostic D w)
  | none => .ok ()

theorem admitNodes_ok (src : Wire.Source) (D : VE.Route.Admission.Doc)
    (ws : List WireNode) (h : admitNodes src D ws = .ok ()) :
    ∀ w ∈ ws, NodeAdmitted src D w := by
  unfold admitNodes at h
  split at h
  · cases h
  · rename_i hf
    intro w hw
    have := List.find?_eq_none.mp hf w hw
    simpa using this

structure Admitted where
  src : Wire.Source
  doc : VE.Route.Admission.Doc
  wires : List WireNode
  graph : VE.Graph.ClaimGraph VE.Tableau.Certificate
  report : VE.Graph.Report
  kinds : List Json

/-- Required document admission: regenerated norm layers, W2 provenance,
certificate bindings, graph checking, citations and reading choices. -/
def admitDocument (environment document : Json) : Except String Admitted := do
  VE.Bridge.displayFields document ["units", "graph"]
    ["lemmas", "open_terms", "reading_sets", "narrowings"]
  let (clean, norms) ← splitDocument document
  let src ← Wire.decodeSource environment norms
  let D ← VE.Route.Admission.decodeDoc src.ne.rv clean
  let graphJson ← document.getObjVal? "graph"
  exactFields graphJson ["root", "nodes"]
  let root ← stringField graphJson "root"
  let nodeArray ← (← graphJson.getObjVal? "nodes").getArr?
  VE.Route.Admission.require (nodeArray.size ≤ 1000) "ResourceLimit: graph node count"
  let decoded ← nodeArray.toList.mapM (VE.Route.Admission.decodeNode src.ne.rv.environment)
  VE.Route.Admission.checkBindings src.ne.profiles (← Wire.canonicalEnvironmentJson environment) decoded
  let wires := decoded.map Prod.fst
  admitNodes src D wires
  let g : VE.Graph.ClaimGraph VE.Tableau.Certificate := ⟨wires.map WireNode.toNode, root⟩
  let r ← VE.Route.Admission.checkGraph src.ne.rv.environment g
  VE.Route.Admission.require (decide (CitationsClosed D r))
    "AdmissionError: a cited lemma's leaves are missing from the report"
  VE.Route.Admission.require (decide (ChoicesCompatible r))
    "AdmissionError: incompatible reading choices"
  pure ⟨src, D, wires, g, r, D.units.map (fun x => renderKind x.kind)⟩

/-- A successful admission has a sound checked graph and every submitted node
is admitted either by W2's ordinary provenance rules or by a regenerated norm
layer. Each report assumption is exactly one of those decoded leaves. -/
theorem norms_wire_admission_sound (environment document : Json) (res : Admitted)
    (h : admitDocument environment document = .ok res) :
    VE.Graph.SoundReport.{u} res.src.ne.rv.environment res.graph res.report ∧
    (∀ w ∈ res.wires, NodeAdmitted res.src res.doc w) ∧
    (∀ leaf ∈ res.report.assumptions, ∃ w ∈ res.wires,
      w.claim = leaf ∧ w.deduction = none ∧ NodeAdmitted res.src res.doc w) := by
  unfold admitDocument at h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨src, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨D, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨decoded, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, hadm, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨r, hr, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  have hnodes := admitNodes_ok src D (decoded.map Prod.fst) hadm
  obtain ⟨_, _, _, hsound⟩ := VE.Graph.check_sound.{u} src.ne.rv.environment _ r
    (VE.Route.Admission.checkGraph_ok _ _ r hr)
  refine ⟨hsound, hnodes, ?_⟩
  intro leaf hl
  obtain ⟨node, hn, hcl, hde⟩ := (hsound.2.2.1 leaf hl).2
  obtain ⟨w, hw, rfl⟩ := List.mem_map.mp hn
  exact ⟨w, hw, hcl, hde, hnodes w hw⟩

theorem layerLeaf_formula (src : Wire.Source) (w : WireNode) (h : LayerLeaf src w) :
    w.claim.formula ∈ elaborate src.D.T := by
  simp only [LayerLeaf, Bool.and_eq_true] at h
  have ha := h.2
  obtain ⟨r, hr, he⟩ := List.any_eq_true.mp ha
  have heq : w.claim.label = "layer:norms:" ++ r.name ∧
      w.claim.formula = elabPremise src.D.T r := of_decide_eq_true he
  rw [heq.2]
  change elabPremise src.D.T r ∈
    (syms src.D.T).filterMap (fun | .reg r => some (elabPremise src.D.T r) | .defn _ => none)
  obtain ⟨q, hq, hqr⟩ := List.mem_filterMap.mp
    (show r ∈ (syms src.D.T).filterMap (fun | .reg r => some r | .defn _ => none) from hr)
  cases q with
  | reg r' =>
    simp only [Option.some.injEq] at hqr
    subst hqr
    exact List.mem_filterMap.mpr ⟨.reg r', hq, rfl⟩
  | defn d => cases hqr

/-- Semantic report consequence: every admitted norm leaf is discharged by the
regenerated elaborations, and all other reported assumptions retain their
provenance and remain explicit hypotheses. -/
theorem norms_wire_report_consequence (environment document : Json) (res : Admitted)
    (h : admitDocument environment document = .ok res) (S : VE.Structure.{u})
    (hS : S.Admissible res.src.ne.rv.environment)
    (hlayers : Sat S (elaborate res.src.D.T))
    (hother : ∀ leaf ∈ res.report.assumptions,
      (¬ ∃ w ∈ res.wires, w.claim = leaf ∧ LayerLeaf res.src w) →
      leaf.formula.denote S []) : res.report.root.formula.denote S [] := by
  obtain ⟨hsound, _, hleaves⟩ := norms_wire_admission_sound.{u} environment document res h
  apply hsound.2.2.2.1 S hS
  intro a ha
  obtain ⟨leaf, hl, rfl⟩ := List.mem_map.mp ha
  by_cases hlayer : ∃ w ∈ res.wires, w.claim = leaf ∧ LayerLeaf res.src w
  · obtain ⟨w, _, hwl, hw⟩ := hlayer
    rw [← hwl]
    exact hlayers _ (layerLeaf_formula res.src w hw)
  · exact hother leaf hl hlayer

end VE.Norms.Admission
