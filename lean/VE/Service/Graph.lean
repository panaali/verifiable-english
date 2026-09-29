import VE.ClaimGraph
import VE.Service.Standalone

/-! The service `graph` mode (SEMANTICS-MIGRATION-PLAN.md section 2.1, 1.2 row 1):
the composition of a `ve-argument-tableau@1` package's root over a ve.core@0.2
FOL environment or the frozen v0 envelope (`ve.core@0`, no Background), checked
by the unchanged `VE.Graph.checkTableau`.

Case: `{"id", "environment", "nodes": [{"name", "source", "ast", "claim_id",
"label"?}], "edges": [{"name", "premises": [names], "conclusion": name,
"edge_id", "certificate"}], "root"}`: every claim in declaration order, and the
deductions whose `follows` certificate the package established.

* Identities are recomputed from the request data: each claim's `source_id`,
  `meaning_id` and `claim_id`, and each deduction's `edge_id`; a submitted
  identity that differs rejects the case. Each certificate must bind the
  submitted environment, the regenerated Background followed by its premises'
  ASTs, and its conclusion's AST. Source text is bound through `source_id`;
  its parse is the parse mode's (the claim's AST is the checked formula).
* Background: each regenerated premise (`Standalone.folBackground`: flags,
  definitions, literals, then norms profile premises) is an
  explicit assumption leaf `background:<i>` labelled `background:<generator>`,
  and it heads every deduction's premise list, as the route certificate
  predicate orders it (Background ++ premises). The proved graph checker then
  covers composition with Background: its report's assumptions are the named
  leaves and the Background leaves the root unfolds to.
* Only the root's dependency cone is submitted to the checker, in a
  deterministic topological order; declaration order is kept for the
  projection.

Answer: the raw `report` (root and assumptions by name, in unfold order), the
compatibility projection (`assumptions`: the named leaves in declaration order;
`supporting_edges`: the cone's deductions in declaration order) and the
regenerated `background` (label, AST). `graph_sound`, `graph_entails` and
`graph_unfolds` state what an answer means. -/
namespace VE.Service.Graph
open Lean
open VE.Graph (Claim Node Edge ClaimGraph Report)

def argumentVersion : String := "ve-argument-tableau@1"

/-- One decoded claim node and its recomputed identity. -/
structure Decoded where
  name : String
  ast : Json
  claim : Claim
  claimId : String

/-- One decoded deduction with its certificate. -/
structure Deduction where
  name : String
  premises : List String
  conclusion : String
  edgeId : String
  certificate : VE.Tableau.Certificate

def labelOf (j : Json) : Except String String :=
  match j.getObjVal? "label" with
  | .ok (.str label) => pure label
  | .ok _ => throw "claim label must be a string"
  | .error _ => pure "asserted"

def claimIdOf (envId sourceId meaningId label : String) : Except String String :=
  VE.CertificateWire.digest "ve-claim-v1\n" (Json.mkObj ([("environment_id", .str envId),
    ("source_id", .str sourceId), ("meaning_id", .str meaningId)] ++
    if label == "asserted" then [] else [("label", .str label)]))

/-- What the node and edge decoders need from the envelope: the environment,
its identity domains and formula decoder, and the regenerated Background. -/
structure Ctx where
  E : VE.Environment
  environment : Json
  envId : String
  version : String
  formula : Json → Except String VE.Formula
  meaningId : Json → Except String String
  /-- The certificate binding over the Background premises, the premises' and the conclusion's ASTs. -/
  bound : List Json → Json → VE.Tableau.Certificate → Except String Unit
  background : List (VE.Formula × String)

def decodeNode (ctx : Ctx) (j : Json) : Except String Decoded := do
  VE.Bridge.exactFields j (["name", "source", "ast", "claim_id"] ++
    if (j.getObjVal? "label").isOk then ["label"] else [])
  let name ← VE.Bridge.stringField j "name"
  let source ← VE.Bridge.stringField j "source"
  let ast ← j.getObjVal? "ast"
  let label ← labelOf j
  let formula ← ctx.formula ast
  let sourceId := VE.CertificateWire.sha256 (s!"ve-source-{ctx.version}\n" ++ source).toUTF8
  let meaningId ← ctx.meaningId ast
  let claimId ← claimIdOf ctx.envId sourceId meaningId label
  unless (← VE.Bridge.stringField j "claim_id") == claimId do
    throw s!"claim {name}: submitted claim_id is not the recomputed identity"
  pure ⟨name, ast, ⟨name, formula, label⟩, claimId⟩

def lookupNode (nodes : List Decoded) (name : String) : Except String Decoded :=
  match nodes.find? (·.name == name) with
  | some n => pure n
  | none => throw s!"unresolved claim reference {name}"

def edgeIdOf (envId : String) (nodes : List Decoded) (name : String) (premises : List String)
    (conclusion : String) : Except String String := do
  let ref := fun (n : String) => do
    pure (Json.mkObj [("name", .str n), ("claim_id", .str (← lookupNode nodes n).claimId)])
  VE.CertificateWire.digest "ve-deduction-v1\n" (Json.mkObj [("version", .str argumentVersion),
    ("environment_id", .str envId), ("name", .str name),
    ("premises", Json.arr (← premises.mapM ref).toArray), ("conclusion", ← ref conclusion)])

def decodeEdge (ctx : Ctx) (nodes : List Decoded) (j : Json) : Except String Deduction := do
  VE.Bridge.exactFields j ["name", "premises", "conclusion", "edge_id", "certificate"]
  let name ← VE.Bridge.stringField j "name"
  let premises ← VE.Bridge.strings (← j.getObjVal? "premises")
  let conclusion ← VE.Bridge.stringField j "conclusion"
  let edgeId ← edgeIdOf ctx.envId nodes name premises conclusion
  unless (← VE.Bridge.stringField j "edge_id") == edgeId do
    throw s!"deduction {name}: submitted edge_id is not the recomputed identity"
  let certificate ← VE.CertificateWire.decodeCertificate (← j.getObjVal? "certificate")
  let premiseAsts ← premises.mapM fun p => do pure (← lookupNode nodes p).ast
  ctx.bound premiseAsts (← lookupNode nodes conclusion).ast certificate
  pure ⟨name, premises, conclusion, edgeId, certificate⟩

/-- A ve.core@0.2 FOL-family envelope: the route vocabulary, its identity
domains, and the certificate binding over the regenerated Background. -/
def routeCtx (environment : Json) : Except String Ctx := do
  let checked ← VE.Service.Standalone.validated environment
  let e := checked.envelope
  unless e.family == .fol do
    throw (VE.Route.Gate.unsupported "graph composition on this family is not implemented")
  let rv ← VE.Route.Run.decodeRouteVocabulary e
  let envId ← VE.Service.Standalone.environmentIdOf e.profiles environment
  let background ← VE.Service.Standalone.folBackground environment rv
  pure { E := rv.environment, environment, envId, version := VE.Route.Wire.identityVersion e.profiles,
         formula := fun a => VE.Route.Wire.decodeClosed rv.environment a (e.profiles.contains "data@0"),
         meaningId := VE.Route.Wire.meaningId e.profiles envId,
         bound := fun premises conclusion c => VE.Route.Wire.bindingOk e.profiles environment
           ((background.map (VE.Route.Wire.encodeFormula ·.1)) ++ premises) conclusion
           c.environment_id c.premise_meaning_ids c.conclusion_meaning_id,
         background }

/-- The frozen v0 envelope (`ve.core@0`): no Background; the P0 identity
domains and certificate binding (`CertificateWire.decodeQuery`). -/
def legacyCtx (environment : Json) : Except String Ctx := do
  let v ← VE.Bridge.decodeEnvironment environment
  let envId ← VE.CertificateWire.digest "ve-environment-v0\n" environment
  pure { E := v.environment, environment, envId, version := "v0",
         formula := fun a => do
           let f ← VE.Bridge.decodeFormula 64 a
           unless f.check v.environment [] do throw "ill-typed or unbound formula"
           pure f,
         meaningId := VE.CertificateWire.meaningId envId,
         bound := fun premises conclusion c => do
           let ps ← premises.mapM (VE.CertificateWire.meaningId envId)
           let q ← VE.CertificateWire.meaningId envId conclusion
           unless c.environment_id == envId && c.premise_meaning_ids == ps && c.conclusion_meaning_id == q do
             throw "certificate is stale or bound to different inputs",
         background := [] }

/-- The root's dependency cone: every claim a path of deductions reaches. -/
def cone (edges : List Deduction) : Nat → List String → List String → List String
  | 0, _, seen => seen
  | _ + 1, [], seen => seen
  | fuel + 1, name :: rest, seen =>
    if seen.contains name then cone edges fuel rest seen
    else match edges.find? (·.conclusion == name) with
      | some e => cone edges fuel (e.premises ++ rest) (seen ++ [name])
      | none => cone edges fuel rest (seen ++ [name])

/-- A topological order of `names` (premises first), stable in declaration
order: each pass emits, in order, the names whose premises are all emitted. -/
def topological (edges : List Deduction) : Nat → List String → List String → Except String (List String)
  | _, [], done => pure done
  | 0, _, _ => throw "dependency cycle in the argument"
  | fuel + 1, pending, done =>
    let ready := pending.filter fun n => match edges.find? (·.conclusion == n) with
      | some e => e.premises.all done.contains
      | none => true
    if ready.isEmpty then throw "dependency cycle in the argument"
    else topological edges fuel (pending.filter (!ready.contains ·)) (done ++ ready)

def backgroundName (i : Nat) : String := s!"background:{i}"

/-- A checked composition: the submitted graph, its accepted report and the projection. -/
structure Checked where
  E : VE.Environment
  graph : ClaimGraph VE.Tableau.Certificate
  report : Report
  accepted : VE.Graph.checkTableau E graph = some report
  assumptions : List String
  supporting : List String
  background : List (String × Json)

def compose (j : Json) : Except String Checked := do
  let environment ← j.getObjVal? "environment"
  let ctx ← if environment.getObjValD "language" == .str "ve.core@0" then legacyCtx environment
    else routeCtx environment
  let E := ctx.E
  let nodes ← (← (← j.getObjVal? "nodes").getArr?).toList.mapM (decodeNode ctx)
  let names := nodes.map (·.name)
  unless names.Nodup do throw "duplicate claim alias"
  let bg := ctx.background
  let edges ← (← (← j.getObjVal? "edges").getArr?).toList.mapM (decodeEdge ctx nodes)
  unless (edges.map (·.conclusion)).Nodup && (edges.map (·.name)).Nodup do
    throw "each conclusion must have exactly one deduction"
  let root ← VE.Bridge.stringField j "root"
  let _ ← lookupNode nodes root
  let reached := cone edges (names.length + edges.length * (names.length + 1) + 1) [root] []
  let inCone := names.filter reached.contains
  let ordered ← topological edges (inCone.length + 1) inCone []
  let bgNames := (List.range bg.length).map backgroundName
  let bgNodes : List (Node VE.Tableau.Certificate) := (bg.zip bgNames).map fun ((a, g), n) =>
    ⟨⟨n, a, "background:" ++ g⟩, none⟩
  let claimNodes ← ordered.mapM fun n => do
    let d ← lookupNode nodes n
    pure ({ claim := d.claim, deduction := (edges.find? (·.conclusion == n)).map fun ded =>
      ⟨bgNames ++ ded.premises, ded.certificate⟩ } : Node VE.Tableau.Certificate)
  let g : ClaimGraph VE.Tableau.Certificate := ⟨bgNodes ++ claimNodes, root⟩
  match h : VE.Graph.checkTableau E g with
  | none => throw "graph rejected: a certificate in the root's cone does not check"
  | some r =>
    let leafNames := r.assumptions.map (·.name)
    pure ⟨E, g, r, h, names.filter leafNames.contains,
      (edges.filter (reached.contains ·.conclusion)).map (·.name),
      bg.map fun (a, g) => ("background:" ++ g, VE.Route.Wire.encodeFormula a)⟩

def claimJson (c : Claim) : Json := .str c.name

def graphCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let c ← compose j
  pure (VE.Route.Wire.ok id [
    ("report", Json.mkObj [("root", claimJson c.report.root),
      ("assumptions", Json.arr (c.report.assumptions.map claimJson).toArray)]),
    ("assumptions", toJson c.assumptions), ("supporting_edges", toJson c.supporting),
    ("background", Json.arr (c.background.map fun (label, ast) =>
      Json.mkObj [("label", .str label), ("ast", ast)]).toArray)])

/-- A composed answer's report is a sound report of the submitted cone graph:
acyclic, uniquely named, rooted at the case's root, every assumption a
submitted leaf (a named claim or a Background leaf), with exact provenance. -/
theorem graph_sound (j : Json) (c : Checked) (_h : compose j = .ok c) :
    VE.Graph.Acyclic c.graph ∧ (c.graph.nodes.map (fun n => n.claim.name)).Nodup ∧
      c.report.root.name = c.graph.root ∧ VE.Graph.SoundReport.{u} c.E c.graph c.report :=
  VE.Graph.check_sound c.E c.graph c.report c.accepted

/-- The root follows from the report's assumptions, Background leaves included. -/
theorem graph_entails (j : Json) (c : Checked) (_h : compose j = .ok c) :
    VE.Entails.{u} c.E (c.report.assumptions.map Claim.formula) c.report.root.formula :=
  VE.Graph.check_entails c.E c.graph c.report c.accepted

/-- The report's assumptions are exactly the unfolding of the submitted edges. -/
theorem graph_unfolds (j : Json) (c : Checked) (_h : compose j = .ok c) :
    VE.Graph.Unfolds c.graph c.report.root c.report.assumptions :=
  VE.Graph.check_unfolds c.E c.graph c.report c.accepted

end VE.Service.Graph
