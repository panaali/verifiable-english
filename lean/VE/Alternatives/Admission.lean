import VE.Alternatives.Replay
import VE.Norms.Admission

/-! W2 graph admission over a regenerated alternatives source. The source
environment and certificate bindings retain the alternatives block. -/
namespace VE.Alternatives.Admission
open Lean VE.Norms
open VE.Route.Admission (WireNode)
open VE.Order.ProfileGate (bind_ok)

def sourcePremises (D : VE.Route.Admission.Doc) : Json :=
  Json.arr (D.units.filterMap (fun u =>
    if u.kind == .asserted then u.content.map (fun a => Json.mkObj
      [("label", .str ("unit:" ++ u.id)), ("ast", VE.Route.Wire.encodeFormula a)])
    else none)).toArray

/-- Closed definitions make profile-word graph claims usable with base facts.
The right side is the same capture-avoiding inlining used for active units. -/
def profileDefinition (A : AltDoc) (p : String) : Option VE.Formula :=
  match profileDef A.alt p with
  | some ([first, second], _) =>
    let atom : VE.Formula := .binary p (.var 1) (.var 0)
    let body := inline A atom
    some (.all first (.all second
      (.and (.implies atom body) (.implies body atom))))
  | _ => none

def profileDefinitions (A : AltDoc) : List (String × VE.Formula) :=
  profileWords.filterMap (fun p =>
    (profileDefinition A p).map (fun f => ("alternatives:profile:" ++ p, f)))

def altLeaf (src : Wire.AltSource) (w : WireNode) : Bool :=
  w.deduction.isNone && w.unit.isNone &&
    (((altPremiseLabels src.A).zip (altPremises src.A)) ++
      (src.labels.zip src.A.Γ).filter (fun x => x.1 == "alternatives:table_complete") ++
      profileDefinitions src.A).any
      (fun x => decide (w.claim.label = x.1 && w.claim.formula = x.2))

def layerLeaf (src : Wire.AltSource) (w : WireNode) : Bool :=
  w.deduction.isNone && w.unit.isNone &&
    ((syms (inlineTree src.A).T).filterMap (fun | .reg r => some r | .defn _ => none)).any
      (fun r => decide (w.claim.label = "layer:norms:" ++ r.name &&
        w.claim.formula = elabPremise (inlineTree src.A).T r))

def profileLeaf (src : Wire.AltSource) (w : WireNode) : Bool :=
  w.deduction.isNone && w.unit.isNone && w.claim.label == "background:profile" &&
    (pairPremises (inlineTree src.A).T).any (fun a => decide (w.claim.formula = a))

def nodeAdmitted (src : Wire.AltSource) (D : VE.Route.Admission.Doc) (w : WireNode) : Bool :=
  decide (VE.Route.Admission.NodeAdmitted D w) || altLeaf src w || layerLeaf src w || profileLeaf src w

def checkNodes (src : Wire.AltSource) (D : VE.Route.Admission.Doc) (ws : List WireNode) :
    Except String Unit :=
  match ws.find? (fun w => !nodeAdmitted src D w) with
  | some w => .error (VE.Route.Admission.nodeDiagnostic D w)
  | none => .ok ()

structure Admitted where
  src : Wire.AltSource
  doc : VE.Route.Admission.Doc
  canonical : Json
  decoded : List (WireNode × Json)
  wires : List WireNode
  graph : VE.Graph.ClaimGraph VE.Tableau.Certificate
  report : VE.Graph.Report
  kinds : List Json
  sound : VE.Graph.SoundReport.{0} (extEnv src.A) graph report

def admitDocument (environment document : Json) : Except String Admitted := do
  VE.Bridge.displayFields document ["units", "graph"]
    ["lemmas", "open_terms", "reading_sets", "narrowings"]
  let (clean, norms, quoted) ← VE.Norms.Admission.splitDocument document
  let ps ← Wire.profileGate environment
  -- Decode the source once without units to obtain the profile-extended typing
  -- environment. The final source below regenerates Γ from asserted units.
  let vocabulary ← Wire.decodeAltSource environment norms (Json.arr #[])
  let D ← VE.Route.Admission.decodeDoc vocabulary.ne.rv (ps.contains "data@0") clean
    (extEnv vocabulary.A)
  let src ← Wire.decodeAltSource environment norms (sourcePremises D)
  for q in quoted do
    let N ← VE.Norms.Wire.decodeNorm q
    let A := { src.A with T := { src.A.T with nodes := [{ N with over := [] }] } }
    validateAlt A
  let graphJson ← document.getObjVal? "graph"
  VE.Bridge.exactFields graphJson ["root", "nodes"]
  let root ← VE.Bridge.stringField graphJson "root"
  let nodes ← (← graphJson.getObjVal? "nodes").getArr?
  VE.Route.Admission.require (nodes.size ≤ 1000) "ResourceLimit: graph node count"
  let decoded ← nodes.toList.mapM (VE.Route.Admission.decodeNode (extEnv src.A) (ps.contains "data@0"))
  let canonical ← VE.Norms.Wire.canonicalEnvironmentJson environment
  VE.Norms.Admission.checkBindings ps canonical decoded
  let wires := decoded.map Prod.fst
  checkNodes src D wires
  let graph : VE.Graph.ClaimGraph VE.Tableau.Certificate := ⟨wires.map WireNode.toNode, root⟩
  match hc : VE.Route.Admission.checkGraph (extEnv src.A) graph with
  | .error e => throw e
  | .ok report =>
    VE.Route.Admission.require (decide (VE.Route.Admission.CitationsClosed D report))
      "AdmissionError: a cited lemma's leaves are missing from the report"
    VE.Route.Admission.require (decide (VE.Route.Admission.ChoicesCompatible report))
      "AdmissionError: incompatible reading choices"
    have sound : VE.Graph.SoundReport.{0} (extEnv src.A) graph report :=
      (VE.Graph.check_sound.{0} (extEnv src.A) graph report
        (VE.Route.Admission.checkGraph_ok _ _ report hc)).2.2.2
    pure ⟨src, D, canonical, decoded, wires, graph, report,
      D.units.map (fun u => VE.Route.Admission.renderKind u.kind), sound⟩

/-- Premises regenerated from the complete alternatives source, never from a
graph leaf. Remaining leaves keep their ordinary W2 assumption status. -/
def generated (res : Admitted) : List VE.Formula :=
  backgroundAlt res.src.A ++ elaborate (inlineTree res.src.A).T ++ res.src.A.Γ ++
    (profileDefinitions res.src.A).map Prod.snd

noncomputable def otherAssumptions (res : Admitted) : List VE.Graph.Claim := by
  classical
  exact res.report.assumptions.filter (fun leaf => !decide (leaf.formula ∈ generated res))

theorem report_consequence (res : Admitted) (S : VE.Structure.{0})
    (hS : S.Admissible (extEnv res.src.A))
    (hgen : Sat S (generated res))
    (hother : Sat S ((otherAssumptions res).map (·.formula))) :
    res.report.root.formula.denote S [] := by
  classical
  apply res.sound.2.2.2.1 S hS
  intro a ha
  obtain ⟨leaf, hl, rfl⟩ := List.mem_map.mp ha
  by_cases hg : leaf.formula ∈ generated res
  · exact hgen _ hg
  · apply hother
    apply List.mem_map_of_mem
    simp [otherAssumptions, hg, hl]

end VE.Alternatives.Admission
