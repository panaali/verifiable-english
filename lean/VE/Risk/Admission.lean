import VE.Risk.Wire
import VE.Alternatives.Admission

/-! W2 graph admission over a regenerated risk source (docs/spec/risk.md 3.4 and
7.2). Graph nodes are typed over `riskExtEnv R` (`E_risk` with alt's four
profile words and the two risk words). Besides W2's own leaves, the checker
admits regenerated leaves only: alt's slot premises (`alternatives:*`), the
risk slot premises (`risk:*`), the closed definitions of alt's profile words
(`alternatives:profile:<word>`) and of the two risk words
(`risk:profile:<word>`), the norm layers and the profile premises. Every
binding is to the complete source environment, blocks included. -/
namespace VE.Risk.Admission
open Lean VE.Norms
open VE.Route.Admission (WireNode)
open Wire (RiskSource decodeRiskSource)

/-- The closed definition of a risk word: its atom is equivalent to the same capture-avoiding inlining used for
active units. -/
def riskDefinition (R : RiskDoc) (p : String) : Option VE.Formula :=
  match riskWordDef R p with
  | some ([first, second], _) =>
    let atom : VE.Formula := .binary p (.var 1) (.var 0)
    let body := VE.Alternatives.inline (toAlt R) (riskInline R atom)
    some (.all first (.all second (.and (.implies atom body) (.implies body atom))))
  | _ => none

def riskDefinitions (R : RiskDoc) : List (String × VE.Formula) :=
  riskWords.filterMap (fun p => (riskDefinition R p).map (fun f => ("risk:profile:" ++ p, f)))

def riskLeaf (src : RiskSource) (w : WireNode) : Bool :=
  let A := toAlt src.R
  w.deduction.isNone && w.unit.isNone &&
    (((VE.Alternatives.altPremiseLabels A).zip (VE.Alternatives.altPremises A)) ++
      ((riskPremiseLabels src.R).zip (riskPremises src.R)) ++
      VE.Alternatives.Admission.profileDefinitions A ++ riskDefinitions src.R).any
      (fun x => decide (w.claim.label = x.1 && w.claim.formula = x.2))

def layerLeaf (src : RiskSource) (w : WireNode) : Bool :=
  let D := VE.Alternatives.inlineTree (toAlt src.R)
  w.deduction.isNone && w.unit.isNone &&
    ((syms D.T).filterMap (fun | .reg r => some r | .defn _ => none)).any
      (fun r => decide (w.claim.label = "layer:norms:" ++ r.name && w.claim.formula = elabPremise D.T r))

def profileLeaf (src : RiskSource) (w : WireNode) : Bool :=
  w.deduction.isNone && w.unit.isNone && w.claim.label == "background:profile" &&
    (pairPremises (VE.Alternatives.inlineTree (toAlt src.R)).T).any (fun a => decide (w.claim.formula = a))

def nodeAdmitted (src : RiskSource) (D : VE.Route.Admission.Doc) (w : WireNode) : Bool :=
  decide (VE.Route.Admission.NodeAdmitted D w) || riskLeaf src w || layerLeaf src w || profileLeaf src w

def checkNodes (src : RiskSource) (D : VE.Route.Admission.Doc) (ws : List WireNode) : Except String Unit :=
  match ws.find? (fun w => !nodeAdmitted src D w) with
  | some w => .error (VE.Route.Admission.nodeDiagnostic D w)
  | none => .ok ()

structure Admitted where
  src : RiskSource
  doc : VE.Route.Admission.Doc
  canonical : Json
  decoded : List (WireNode × Json)
  wires : List WireNode
  graph : VE.Graph.ClaimGraph VE.Tableau.Certificate
  report : VE.Graph.Report
  kinds : List Json
  sound : VE.Graph.SoundReport.{0} (riskExtEnv src.R) graph report

def admitDocument (environment document : Json) : Except String Admitted := do
  VE.Bridge.displayFields document ["units", "graph"] ["lemmas", "open_terms", "reading_sets", "narrowings"]
  let (clean, norms, quoted) ← VE.Norms.Admission.splitDocument document
  let ps ← Wire.profileGate environment
  -- Decode the source once without units to obtain the typing environment; the final source regenerates Γ
  -- from the asserted units.
  let vocabulary ← decodeRiskSource environment (Json.mkObj [("norms", norms)])
  let D ← VE.Route.Admission.decodeDoc vocabulary.ne.rv (ps.contains "data@0") clean (riskExtEnv vocabulary.R)
  let src ← decodeRiskSource environment
    (Json.mkObj [("norms", norms), ("units", VE.Alternatives.Admission.sourcePremises D)])
  for q in quoted do
    let N ← VE.Norms.Wire.decodeNorm q
    validateRisk { src.R with T := { src.R.T with nodes := [{ N with over := [] }] } }
  let graphJson ← document.getObjVal? "graph"
  VE.Bridge.exactFields graphJson ["root", "nodes"]
  let root ← VE.Bridge.stringField graphJson "root"
  let nodes ← (← graphJson.getObjVal? "nodes").getArr?
  VE.Route.Admission.require (nodes.size ≤ 1000) "ResourceLimit: graph node count"
  let decoded ← nodes.toList.mapM (VE.Route.Admission.decodeNode (riskExtEnv src.R) (ps.contains "data@0"))
  let canonical ← VE.Norms.Wire.canonicalEnvironmentJson environment
  VE.Norms.Admission.checkBindings ps canonical decoded
  let wires := decoded.map Prod.fst
  checkNodes src D wires
  let graph : VE.Graph.ClaimGraph VE.Tableau.Certificate := ⟨wires.map WireNode.toNode, root⟩
  match hc : VE.Route.Admission.checkGraph (riskExtEnv src.R) graph with
  | .error e => throw e
  | .ok report =>
    VE.Route.Admission.require (decide (VE.Route.Admission.CitationsClosed D report))
      "AdmissionError: a cited lemma's leaves are missing from the report"
    VE.Route.Admission.require (decide (VE.Route.Admission.ChoicesCompatible report))
      "AdmissionError: incompatible reading choices"
    have sound : VE.Graph.SoundReport.{0} (riskExtEnv src.R) graph report :=
      (VE.Graph.check_sound.{0} (riskExtEnv src.R) graph report
        (VE.Route.Admission.checkGraph_ok _ _ report hc)).2.2.2
    pure ⟨src, D, canonical, decoded, wires, graph, report,
      D.units.map (fun u => VE.Route.Admission.renderKind u.kind), sound⟩

/-- Premises regenerated from the complete risk source, never from a graph leaf: alt's premises plus
`riskPremises` and the two regenerated definitions. Remaining leaves keep their W2 assumption status. -/
def generated (res : Admitted) : List VE.Formula :=
  let A := toAlt res.src.R
  VE.Alternatives.backgroundAlt A ++ riskPremises res.src.R ++ elaborate (VE.Alternatives.inlineTree A).T ++ A.Γ ++
    (VE.Alternatives.Admission.profileDefinitions A).map Prod.snd ++ (riskDefinitions res.src.R).map Prod.snd

noncomputable def otherAssumptions (res : Admitted) : List VE.Graph.Claim := by
  classical
  exact res.report.assumptions.filter (fun leaf => !decide (leaf.formula ∈ generated res))

theorem report_consequence (res : Admitted) (S : VE.Structure.{0}) (hS : S.Admissible (riskExtEnv res.src.R))
    (hgen : Sat S (generated res)) (hother : Sat S ((otherAssumptions res).map (·.formula))) :
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

end VE.Risk.Admission
