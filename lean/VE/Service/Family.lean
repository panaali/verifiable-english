import VE.Service.Graph
import VE.Service.Readings
import VE.Service.GenericReadings

/-! The service `graph` and `readings` modes on the closure, core and order
families of `ve.core@0.2` (SEMANTICS-MIGRATION-PLAN.md sections 1.2 and 2.1,
stage 2c): the cases `VE/Service/Graph.lean` and `VE/Service/Readings.lean`
answer for the FOL family, over each family's own formulas, certificate
checker and model decoder.

A family context (`Ctx`) holds what both cases read from an envelope: the
closed-formula decoder (AST limits, decoding, typing), the identity domains,
the certificate decoder and binding, the regenerated Background with its ASTs
and generators, and the model decoder. Each family also supplies a typing test,
a certificate predicate and a budgeted refutation check; the theorems below
take their soundness from the family's existing theorems:

* closure: `VE.Closure.Tableau.checkCertificate_sound`, the budgeted
  `Budget.refutesC_sound` and `VE.Closure.countermodelCheck_iff`, models from
  the route's `decodeDataModel` (`decodeDataModel_valid`);
* core: `VE.Core.Tableau.checkCertificate_sound`, `Budget.refutesN_sound`,
  `VE.Core.countermodelCheck_iff`, models checked by `ModelData.valid`
  (`VE.Bridge.modelData_valid`);
* order: `VE.Order.Tableau.checkCertificate_sound`,
  `Budget.refutesB_sortOrderData_sound`, `VE.Order.countermodelCheck_iff`,
  models checked by `validModel?` (`VE.Order.validModel_iff`).

Background is the family route's (`Standalone.folBackground` on the closure
family; literals, or the core layers' flags, definitions and literals, then
the norms profile premises on the core family; order literals on the order
family, whose profile pairs are deferred as in `Norms.Plain`). -/
namespace VE.Service.Family
open Lean
open VE.Service.GenericGraph (Claim Node Edge ClaimGraph Report Ent)
open VE.Service.GenericReadings (disjunction Refutes Choice)
universe u

abbrev Entity := VE.Bridge.Entity

/-- What the graph and readings cases read from an envelope of one family. -/
structure Ctx (F C M : Type) where
  environment : Json
  envId : String
  version : String
  /-- One closed formula: its AST limits, decoding and typing. -/
  formula : Json → Except String F
  meaningId : Json → Except String String
  certificate : Json → Except String C
  /-- The certificate binds the environment, Background's ASTs followed by
  `premises`, and `conclusion`. -/
  bound : List Json → Json → C → Except String Unit
  /-- Background: each regenerated premise, its AST and its generator. -/
  background : List (F × Json × String)
  model : Json → Except String M

/-- The norms profile premises of the submitted environment's regulated predicates. -/
def profilePremises (environment : Json) : Except String (List VE.Formula) := do
  let predicates ← VE.Bridge.fields (← (← environment.getObjVal? "vocabulary").getObjVal? "predicates")
  pure (VE.Norms.pairPremises ⟨← VE.Norms.Plain.decodeRegulatedAll predicates, [], []⟩)

def withAst (bg : List (VE.Formula × String)) (embed : VE.Formula → F) : List (F × Json × String) :=
  bg.map fun (a, g) => (embed a, VE.Route.Wire.encodeFormula a, g)

/-! ## Closure family -/

def closureWf (E : VE.Environment) (a : VE.Closure.Formula) : Bool := a.check E []

def closureValid (E : VE.Environment) (c : VE.Closure.Tableau.Certificate)
    (ps : List VE.Closure.Formula) (r : VE.Closure.Formula) : Bool :=
  VE.Closure.Tableau.checkCertificate E ps r c

abbrev ClosureModel (E : VE.Environment) := { M : VE.FiniteModel Entity // M.Valid E }

/-- The budgeted refutation check of the route's closure countermodel case. -/
def closureRefutes (names : List String) (E : VE.Environment) (M : ClosureModel E)
    (Γ : List VE.Closure.Formula) (φ : VE.Closure.Formula) : Bool :=
  VE.Route.Budget.refutesC (VE.Route.Budget.tableMem M.1 (VE.Route.Budget.tableIndex names M.1)) M.1
    VE.Time.maxEvaluations Γ φ 0 == some true

theorem closureRefutes_sound (names : List String) (E : VE.Environment) (M : ClosureModel E)
    (Γ : List VE.Closure.Formula) (φ : VE.Closure.Formula) (h : closureRefutes names E M Γ φ = true) :
    Refutes (fun S : VE.Structure.{0} => S.Admissible E) (fun S a => a.denote S []) Γ φ := by
  have hr : VE.Route.Budget.refutesC (VE.Route.Budget.tableMem M.1 (VE.Route.Budget.tableIndex names M.1))
      M.1 VE.Time.maxEvaluations Γ φ 0 = some true := by simpa [closureRefutes] using h
  have hc := VE.Route.Budget.refutesC_sound _ M.1 _ (VE.Route.Budget.tableMem_iff names M.1) Γ φ 0 true hr
  obtain ⟨hp, hn⟩ := (VE.Closure.countermodelCheck_iff M.1 Γ φ).mp hc.symm
  exact ⟨M.1.asStructure, M.2, hp, hn⟩

structure ClosureEnv where
  rv : VE.Route.Wire.RouteVocabulary
  ctx : Ctx VE.Closure.Formula VE.Closure.Tableau.Certificate (ClosureModel rv.environment)

def closureModel (rv : VE.Route.Wire.RouteVocabulary) (j : Json) :
    Except String (ClosureModel rv.environment) :=
  match h : VE.Route.Wire.decodeDataModel rv j with
  | .ok M => .ok ⟨M, (VE.Route.Wire.decodeDataModel_valid rv j M h).1.1⟩
  | .error e => .error e

def closureEnv (environment : Json) (checked : Standalone.Validated) : Except String ClosureEnv := do
  let e := checked.envelope
  let rv ← VE.Route.Run.decodeRouteVocabulary e
  let E := rv.environment
  let data := e.profiles.contains "data@0"
  let envId ← Standalone.environmentIdOf e.profiles environment
  let bg ← Standalone.folBackground environment rv
  let decodeF := fun (j : Json) => do
    VE.Route.AstLimit.check [j]
    let a ← VE.Closure.Bridge.decodeFormula 64 j
    if data && VE.Route.Wire.closureUsesStringBinder a then
      throw "UnsupportedProfile: $string quantification requires data stage 2"
    unless a.check E [] do throw "ill-typed or unbound formula"
    pure a
  pure ⟨rv, {
    environment := environment
    envId := envId
    version := VE.Route.Wire.identityVersion e.profiles
    formula := decodeF
    meaningId := VE.Route.Wire.meaningId e.profiles envId
    certificate := VE.CertificateWire.decodeClosureCertificate
    bound := fun premises conclusion c => VE.Route.Wire.bindingOk e.profiles environment
      (bg.map (VE.Route.Wire.encodeFormula ·.1) ++ premises) conclusion
      c.environment_id c.premise_meaning_ids c.conclusion_meaning_id
    background := withAst bg VE.Closure.embed
    model := closureModel rv }⟩

/-! ## Core family (closure + n-ary) -/

def coreWf (E : VE.Environment) (a : VE.Core.Formula) : Bool := a.check E []

def coreValid (E : VE.Environment) (c : VE.Core.Tableau.Certificate)
    (ps : List VE.Core.Formula) (r : VE.Core.Formula) : Bool :=
  VE.Core.Tableau.checkCertificate E ps r c

abbrev CoreModel (E : VE.Environment) := { M : VE.FiniteModel Entity // M.Valid E }

def coreRefutes (names : List String) (E : VE.Environment) (M : CoreModel E)
    (Γ : List VE.Core.Formula) (φ : VE.Core.Formula) : Bool :=
  VE.Route.Budget.refutesN (VE.Route.Budget.tableMem M.1 (VE.Route.Budget.tableIndex names M.1)) M.1
    VE.Time.maxEvaluations Γ φ 0 == some true

theorem coreRefutes_sound (names : List String) (E : VE.Environment) (M : CoreModel E)
    (Γ : List VE.Core.Formula) (φ : VE.Core.Formula) (h : coreRefutes names E M Γ φ = true) :
    Refutes (fun S : VE.Structure.{0} => S.Admissible E) (fun S a => a.denote S []) Γ φ := by
  have hr : VE.Route.Budget.refutesN (VE.Route.Budget.tableMem M.1 (VE.Route.Budget.tableIndex names M.1))
      M.1 VE.Time.maxEvaluations Γ φ 0 = some true := by simpa [coreRefutes] using h
  have hc := VE.Route.Budget.refutesN_sound _ M.1 _ (VE.Route.Budget.tableMem_iff names M.1) Γ φ 0 true hr
  obtain ⟨hp, hn⟩ := (VE.Core.countermodelCheck_iff M.1 Γ φ).mp hc.symm
  exact ⟨M.1.asStructure, M.2, hp, hn⟩

/-- A core model: `Core.Wire.decodeModel` (the core route's decoder: tables
with domains in Python order, admissibility, then literals), with its
admissibility re-checked by `ModelData.valid` for the proof. -/
def coreModel (v : VE.Bridge.Vocabulary) (j : Json) : Except String (CoreModel v.environment) := do
  let _ ← VE.Core.Wire.decodeModel v j
  let data := VE.Route.Wire.sortModelData
    (← VE.Route.Decode.decodeModelData (VE.Core.Wire.modelVocabulary v) j)
  if h : data.valid v = true then pure ⟨data.toModel, VE.Bridge.modelData_valid data v h⟩
  else throw "model is not semantically admissible"

structure CoreEnv where
  v : VE.Bridge.Vocabulary
  ctx : Ctx VE.Core.Formula VE.Core.Tableau.Certificate (CoreModel v.environment)

def coreEnv (environment : Json) (checked : Standalone.Validated) : Except String CoreEnv := do
  let e := checked.envelope
  let v ← VE.Core.Bridge.decodeEnvironment checked.decodable
  let E := v.environment
  let envId ← Standalone.environmentIdOf e.profiles environment
  let profile := (← profilePremises environment).map (·, "profile")
  -- Base Background and the model decoder: literals over the core decoder, or,
  -- with definitions@0 or data@0 layer fields, the FOL projection's flags,
  -- definitions and literals, and each model's defined tables computed there
  -- (as `Core.Layers.run` and the model mode do).
  let (base, model) ← match checked.layers with
    | none => pure (VE.Route.Background.background (VE.Core.Wire.literals v), coreModel v)
    | some layered => do
      let rv ← VE.Core.Layers.decodeLayers e.profiles layered
      let names := (← VE.Core.Layers.folPredicates layered).map Prod.fst
      pure (VE.Route.Wire.fullBackground rv, fun (j : Json) => do
        let M ← VE.Route.Wire.decodeDataModel rv (← VE.Core.Layers.folModel names j)
        let tables := (VE.Definitions.names rv.definitions).map fun p =>
          (p, VE.Core.Layers.tableJson (M.relations p))
        let relations ← VE.Bridge.fields (← j.getObjVal? "relations")
        coreModel v (j.setObjVal! "relations" (Json.mkObj (relations ++ tables))))
  let bg := base ++ profile
  let decodeF := fun (j : Json) => do
    VE.Route.AstLimit.check [j]
    let a ← VE.Core.Bridge.decodeFormula 64 j
    VE.Core.Bridge.checkFormula E a "formula"
    unless a.check E [] do throw "ill-typed or unbound formula"
    pure a
  pure ⟨v, {
    environment := environment
    envId := envId
    version := VE.Route.Wire.identityVersion e.profiles
    formula := decodeF
    meaningId := VE.Route.Wire.meaningId e.profiles envId
    certificate := VE.Core.Wire.decodeCertificate
    bound := fun premises conclusion c => VE.Route.Wire.bindingOk e.profiles environment
      (bg.map (VE.Route.Wire.encodeFormula ·.1) ++ premises) conclusion
      c.environment_id c.premise_meaning_ids c.conclusion_meaning_id
    background := withAst bg VE.Core.embed
    model := model }⟩

/-! ## Order family -/

def orderWf (E : VE.Order.Environment) (a : VE.Order.Formula) : Bool := a.check E []

def orderValid (E : VE.Order.Environment) (c : VE.Order.Tableau.Certificate)
    (ps : List VE.Order.Formula) (r : VE.Order.Formula) : Bool :=
  VE.Order.Tableau.checkCertificate E ps r c

abbrev OrderModel (E : VE.Order.Environment) :=
  { d : VE.Order.ModelData VE.Order.Wire.Entity // d.toModel.Valid E }

/-- The budgeted refutation check of the route's order countermodel case, on
the model with its domains in Python order. -/
def orderRefutes (names : List String) (E : VE.Order.Environment) (d : OrderModel E)
    (Γ : List VE.Order.Formula) (φ : VE.Order.Formula) : Bool :=
  let M := (VE.Route.Budget.sortOrderData d.1).toModel
  VE.Time.refutesB (VE.Route.Budget.orderMem M (VE.Route.Budget.orderIndex names M)) M
    VE.Time.maxEvaluations Γ φ 0 == some true

theorem orderRefutes_sound (names : List String) (E : VE.Order.Environment) (d : OrderModel E)
    (Γ : List VE.Order.Formula) (φ : VE.Order.Formula) (h : orderRefutes names E d Γ φ = true) :
    Refutes (fun S : VE.Order.Structure.{0} => S.Admissible E) (fun S a => a.denote S []) Γ φ := by
  have hr : VE.Time.refutesB (VE.Route.Budget.orderMem (VE.Route.Budget.sortOrderData d.1).toModel
      (VE.Route.Budget.orderIndex names (VE.Route.Budget.sortOrderData d.1).toModel))
      (VE.Route.Budget.sortOrderData d.1).toModel VE.Time.maxEvaluations Γ φ 0 = some true := by
    simpa [orderRefutes] using h
  have hc := VE.Route.Budget.refutesB_sortOrderData_sound d.1 _ names Γ φ 0 true hr
  obtain ⟨hp, hn⟩ := (VE.Order.countermodelCheck_iff d.1.toModel Γ φ).mp hc.symm
  exact ⟨d.1.toModel.asStructure, d.2, hp, hn⟩

structure OrderEnv where
  rv : VE.Route.Wire.RouteOrderVocabulary
  ctx : Ctx VE.Order.Formula VE.Order.Tableau.Certificate (OrderModel rv.vocabulary.environment)

def orderModel (rv : VE.Route.Wire.RouteOrderVocabulary) (j : Json) :
    Except String (OrderModel rv.vocabulary.environment) := do
  let d ← VE.Route.Wire.decodeOrderModel rv j
  if h : VE.Order.validModel? rv.vocabulary d = true then
    pure ⟨d, (VE.Order.validModel_iff rv.vocabulary d).mp h⟩
  else throw "model is not semantically admissible"

def orderEnv (environment : Json) (checked : Standalone.Validated) : Except String OrderEnv := do
  let e := checked.envelope
  let rv ← VE.Route.Wire.decodeOrderVocabulary e.vocabulary
  let E := rv.vocabulary.environment
  unless (← profilePremises environment).isEmpty do
    throw (VE.Route.Gate.unsupported "profile pairs on the order family are deferred")
  let envId ← Standalone.environmentIdOf e.profiles environment
  let lits := VE.Route.Background.literals rv.literals
  let decodeF := fun (j : Json) => do
    VE.Route.AstLimit.check [j]
    let a ← VE.Order.Wire.decodeFormula 64 j
    unless a.check E [] do throw "ill-typed or unbound formula"
    pure a
  pure ⟨rv, {
    environment := environment
    envId := envId
    version := VE.Route.Wire.identityVersion e.profiles
    formula := decodeF
    meaningId := VE.Route.Wire.meaningId e.profiles envId
    certificate := VE.Order.Wire.decodeCertificate
    bound := fun premises conclusion c => VE.Route.Wire.bindingOk e.profiles environment
      (lits.map VE.Route.Wire.encodeFormula ++ premises) conclusion
      c.environment_id c.premise_meaning_ids c.conclusion_meaning_id
    background := ((VE.Route.Background.orderLiterals rv.literals).zip lits).map fun (a, f) =>
      (a, VE.Route.Wire.encodeFormula f, "literals")
    model := orderModel rv }⟩

/-! ## FOL formulas (the frozen v0 envelope's readings and bundles) -/

def folWf (E : VE.Environment) (a : VE.Formula) : Bool := a.check E []

def folValid (E : VE.Environment) (c : VE.Tableau.Certificate) (ps : List VE.Formula)
    (r : VE.Formula) : Bool :=
  VE.Tableau.checkCertificate E ps r c

abbrev FolModel (E : VE.Environment) := { M : VE.FiniteModel Entity // M.Valid E }

def folRefutes (names : List String) (E : VE.Environment) (M : FolModel E)
    (Γ : List VE.Formula) (φ : VE.Formula) : Bool :=
  VE.Route.Budget.refutesF (VE.Route.Budget.tableMem M.1 (VE.Route.Budget.tableIndex names M.1)) M.1
    VE.Time.maxEvaluations Γ φ 0 == some true

theorem folRefutes_sound (names : List String) (E : VE.Environment) (M : FolModel E)
    (Γ : List VE.Formula) (φ : VE.Formula) (h : folRefutes names E M Γ φ = true) :
    Refutes (fun S : VE.Structure.{0} => S.Admissible E) (fun S a => a.denote S []) Γ φ := by
  have hr : VE.Route.Budget.refutesF (VE.Route.Budget.tableMem M.1 (VE.Route.Budget.tableIndex names M.1))
      M.1 VE.Time.maxEvaluations Γ φ 0 = some true := by simpa [folRefutes] using h
  have hc := VE.Route.Budget.refutesF_sound _ M.1 _ (VE.Route.Budget.tableMem_iff names M.1) Γ φ 0 true hr
  obtain ⟨hp, hn⟩ := (VE.countermodelCheck_iff M.1 Γ φ).mp hc.symm
  exact ⟨M.1.asStructure, M.2, hp, hn⟩

/-! ## The frozen pre-route envelopes

`ve.core@0` (FOL) and `ve.core@0.1` (closure; order) have no Background and
bind certificates by their frozen identity domains (`Standalone.Legacy`). -/

/-- A legacy envelope's identity and certificate binding. -/
def legacyIds (l : Standalone.Legacy) (environment : Json) :
    Except String (String × (Json → Except String String) ×
      (List Json → Json → String → List String → String → Except String Unit)) := do
  let envId ← Standalone.legacyEnvironmentId l environment
  let meaningId := Standalone.legacyMeaningId l envId
  pure (envId, meaningId, fun premises conclusion e ps q => do
    let expected ← premises.mapM meaningId
    let c ← meaningId conclusion
    unless e == envId && ps == expected && q == c do
      throw "certificate is stale or bound to different inputs")

def legacyCtx {F C M : Type} (l : Standalone.Legacy) (environment : Json) (decodeF : Json → Except String F)
    (certificate : Json → Except String C) (fields : C → String × List String × String)
    (model : Json → Except String M) : Except String (Ctx F C M) := do
  let (envId, meaningId, bind) ← legacyIds l environment
  pure {
    environment := environment
    envId := envId
    version := l.version
    formula := fun j => do
      VE.Route.AstLimit.check [j]
      decodeF j
    meaningId := meaningId
    certificate := certificate
    bound := fun premises conclusion c =>
      let (e, ps, q) := fields c
      bind premises conclusion e ps q
    background := []
    model := model }

def bridgeModel (v : VE.Bridge.Vocabulary) (j : Json) :
    Except String { M : VE.FiniteModel Entity // M.Valid v.environment } :=
  match h : VE.Bridge.decodeModel v j with
  | .ok M => .ok ⟨M, VE.Bridge.decodeModel_valid v j M h⟩
  | .error e => .error e

def legacyFolCtx (environment : Json) (v : VE.Bridge.Vocabulary) :
    Except String (Ctx VE.Formula VE.Tableau.Certificate (FolModel v.environment)) :=
  legacyCtx (.v0 v) environment
    (fun j => do
      let a ← VE.Bridge.decodeFormula 64 j
      unless a.check v.environment [] do throw "ill-typed or unbound formula"
      pure a)
    VE.CertificateWire.decodeCertificate
    (fun c => (c.environment_id, c.premise_meaning_ids, c.conclusion_meaning_id)) (bridgeModel v)

def legacyClosureCtx (environment : Json) (v : VE.Bridge.Vocabulary) :
    Except String (Ctx VE.Closure.Formula VE.Closure.Tableau.Certificate (ClosureModel v.environment)) :=
  legacyCtx (.closure v) environment
    (fun j => do
      let a ← VE.Closure.Bridge.decodeFormula 64 j
      unless a.check v.environment [] do throw "ill-typed or unbound formula"
      pure a)
    VE.CertificateWire.decodeClosureCertificate
    (fun c => (c.environment_id, c.premise_meaning_ids, c.conclusion_meaning_id)) (bridgeModel v)

def legacyOrderModel (v : VE.Order.Vocabulary) (j : Json) : Except String (OrderModel v.environment) := do
  let d ← VE.Order.Wire.decodeValidModel v j
  if h : VE.Order.validModel? v d = true then pure ⟨d, (VE.Order.validModel_iff v d).mp h⟩
  else throw "model is not semantically admissible"

def legacyOrderCtx (environment : Json) (v : VE.Order.Vocabulary) :
    Except String (Ctx VE.Order.Formula VE.Order.Tableau.Certificate (OrderModel v.environment)) :=
  legacyCtx (.order v) environment
    (fun j => do
      let a ← VE.Order.Wire.decodeFormula 64 j
      unless a.check v.environment [] do throw "ill-typed or unbound formula"
      pure a)
    VE.Order.Wire.decodeCertificate
    (fun c => (c.environment_id, c.premise_meaning_ids, c.conclusion_meaning_id)) (legacyOrderModel v)

/-! ## Graph composition -/

section Graph
variable {F C M : Type}

structure Decoded (F : Type) where
  name : String
  ast : Json
  claim : Claim F
  claimId : String

structure Deduction (C : Type) where
  name : String
  premises : List String
  conclusion : String
  edgeId : String
  certificate : C

def decodeNode (ctx : Ctx F C M) (j : Json) : Except String (Decoded F) := do
  VE.Bridge.exactFields j (["name", "source", "ast", "claim_id"] ++
    if (j.getObjVal? "label").isOk then ["label"] else [])
  let name ← VE.Bridge.stringField j "name"
  let source ← VE.Bridge.stringField j "source"
  let ast ← j.getObjVal? "ast"
  let label ← Graph.labelOf j
  let formula ← ctx.formula ast
  let sourceId := VE.CertificateWire.sha256 (s!"ve-source-{ctx.version}\n" ++ source).toUTF8
  let meaningId ← ctx.meaningId ast
  let claimId ← Graph.claimIdOf ctx.envId sourceId meaningId label
  unless (← VE.Bridge.stringField j "claim_id") == claimId do
    throw s!"claim {name}: submitted claim_id is not the recomputed identity"
  pure ⟨name, ast, ⟨name, formula, label⟩, claimId⟩

def lookupNode (nodes : List (Decoded F)) (name : String) : Except String (Decoded F) :=
  match nodes.find? (·.name == name) with
  | some n => pure n
  | none => throw s!"unresolved claim reference {name}"

def edgeIdOf (envId : String) (nodes : List (Decoded F)) (name : String) (premises : List String)
    (conclusion : String) : Except String String := do
  let ref := fun (n : String) => do
    pure (Json.mkObj [("name", .str n), ("claim_id", .str (← lookupNode nodes n).claimId)])
  VE.CertificateWire.digest "ve-deduction-v1\n" (Json.mkObj [("version", .str Graph.argumentVersion),
    ("environment_id", .str envId), ("name", .str name),
    ("premises", Json.arr (← premises.mapM ref).toArray), ("conclusion", ← ref conclusion)])

def decodeEdge (ctx : Ctx F C M) (nodes : List (Decoded F)) (j : Json) : Except String (Deduction C) := do
  VE.Bridge.exactFields j ["name", "premises", "conclusion", "edge_id", "certificate"]
  let name ← VE.Bridge.stringField j "name"
  let premises ← VE.Bridge.strings (← j.getObjVal? "premises")
  let conclusion ← VE.Bridge.stringField j "conclusion"
  let edgeId ← edgeIdOf ctx.envId nodes name premises conclusion
  unless (← VE.Bridge.stringField j "edge_id") == edgeId do
    throw s!"deduction {name}: submitted edge_id is not the recomputed identity"
  let certificate ← ctx.certificate (← j.getObjVal? "certificate")
  let premiseAsts ← premises.mapM fun p => do pure (← lookupNode nodes p).ast
  ctx.bound premiseAsts (← lookupNode nodes conclusion).ast certificate
  pure ⟨name, premises, conclusion, edgeId, certificate⟩

/-- The root's dependency cone (`Graph.cone`). -/
def cone (edges : List (Deduction C)) : Nat → List String → List String → List String
  | 0, _, seen => seen
  | _ + 1, [], seen => seen
  | fuel + 1, name :: rest, seen =>
    if seen.contains name then cone edges fuel rest seen
    else match edges.find? (·.conclusion == name) with
      | some e => cone edges fuel (e.premises ++ rest) (seen ++ [name])
      | none => cone edges fuel rest (seen ++ [name])

/-- A stable topological order, premises first (`Graph.topological`). -/
def topological (edges : List (Deduction C)) : Nat → List String → List String →
    Except String (List String)
  | _, [], done => pure done
  | 0, _, _ => throw "dependency cycle in the argument"
  | fuel + 1, pending, done =>
    let ready := pending.filter fun n => match edges.find? (·.conclusion == n) with
      | some e => e.premises.all done.contains
      | none => true
    if ready.isEmpty then throw "dependency cycle in the argument"
    else topological edges fuel (pending.filter (!ready.contains ·)) (done ++ ready)

/-- Certificate validity on claims: the certificate predicate on their formulas. -/
def claimValid (valid : C → List F → F → Bool) (c : C) (ps : List (Claim F)) (r : Claim F) : Bool :=
  valid c (ps.map Claim.formula) r.formula

/-- A checked composition: the submitted graph and its accepted report. -/
structure Checked (F C : Type) (wf : F → Bool) (valid : C → List F → F → Bool) where
  graph : ClaimGraph F C
  report : Report F
  accepted : GenericGraph.check wf (claimValid valid) graph = some report
  assumptions : List String
  supporting : List String
  background : List (String × Json)

/-- `Graph.compose` over a family context. -/
def compose (ctx : Ctx F C M) (wf : F → Bool) (valid : C → List F → F → Bool) (j : Json) :
    Except String (Checked F C wf valid) := do
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
  let bgNames := (List.range bg.length).map Graph.backgroundName
  let bgNodes : List (Node F C) := (bg.zip bgNames).map fun ((a, _, g), n) =>
    ⟨⟨n, a, "background:" ++ g⟩, none⟩
  let claimNodes ← ordered.mapM fun n => do
    let d ← lookupNode nodes n
    pure ({ claim := d.claim, deduction := (edges.find? (·.conclusion == n)).map fun ded =>
      ⟨bgNames ++ ded.premises, ded.certificate⟩ } : Node F C)
  let g : ClaimGraph F C := ⟨bgNodes ++ claimNodes, root⟩
  match h : GenericGraph.check wf (claimValid valid) g with
  | none => throw "graph rejected: a certificate in the root's cone does not check"
  | some r =>
    let leafNames := r.assumptions.map (·.name)
    pure ⟨g, r, h, names.filter leafNames.contains,
      (edges.filter (reached.contains ·.conclusion)).map (·.name),
      bg.map fun (_, ast, g) => ("background:" ++ g, ast)⟩

def answer (id : String) (c : Checked F C wf valid) : Json :=
  VE.Route.Wire.ok id [
    ("report", Json.mkObj [("root", .str c.report.root.name),
      ("assumptions", Json.arr (c.report.assumptions.map (Json.str ·.name)).toArray)]),
    ("assumptions", toJson c.assumptions), ("supporting_edges", toJson c.supporting),
    ("background", Json.arr (c.background.map fun (label, ast) =>
      Json.mkObj [("label", .str label), ("ast", ast)]).toArray)]

end Graph

/-- The `graph` case on the closure, core and order families. -/
def graphCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let environment ← j.getObjVal? "environment"
  if Standalone.isLegacy environment then
    match ← Standalone.decodeLegacy environment with
    | .closure v =>
      return answer id (← compose (← legacyClosureCtx environment v) (closureWf v.environment)
        (closureValid v.environment) j)
    | .order v =>
      return answer id (← compose (← legacyOrderCtx environment v) (orderWf v.environment)
        (orderValid v.environment) j)
    | .v0 _ => throw "the v0 envelope composes through Graph.graphCase"
  let checked ← Standalone.validated environment
  match checked.envelope.family with
  | .closure =>
    let f ← closureEnv environment checked
    pure (answer id (← compose f.ctx (closureWf f.rv.environment) (closureValid f.rv.environment) j))
  | .closureNary =>
    let f ← coreEnv environment checked
    pure (answer id (← compose f.ctx (coreWf f.v.environment) (coreValid f.v.environment) j))
  | .order =>
    let f ← orderEnv environment checked
    let E := f.rv.vocabulary.environment
    pure (answer id (← compose f.ctx (orderWf E) (orderValid E) j))
  | .fol => throw "the FOL family composes through Graph.graphCase"

/-! ### What a composition means -/

/-- A closure-family composition: acyclic, uniquely named, rooted at the case's
root, with a sound report whose root follows from its assumptions (Background
leaves included) over every admissible structure. -/
theorem closure_graph_sound (E : VE.Environment)
    (c : Checked VE.Closure.Formula VE.Closure.Tableau.Certificate (closureWf E) (closureValid E)) :
    GenericGraph.Acyclic c.graph ∧ (c.graph.nodes.map (fun n => n.claim.name)).Nodup ∧
      c.report.root.name = c.graph.root ∧
      GenericGraph.SoundReport (fun S : VE.Structure.{u} => S.Admissible E) (fun S a => a.denote S [])
        (closureWf E) c.graph c.report :=
  GenericGraph.check_sound _ _ _ _
    (fun cert _ _ h => VE.Closure.Tableau.checkCertificate_sound E _ _ cert h) c.graph c.report c.accepted

theorem closure_graph_entails (E : VE.Environment)
    (c : Checked VE.Closure.Formula VE.Closure.Tableau.Certificate (closureWf E) (closureValid E)) :
    VE.Closure.Entails.{u} E (c.report.assumptions.map Claim.formula) c.report.root.formula :=
  (closure_graph_sound.{u} E c).2.2.2.2.2.2.1

theorem closure_graph_unfolds (E : VE.Environment)
    (c : Checked VE.Closure.Formula VE.Closure.Tableau.Certificate (closureWf E) (closureValid E)) :
    GenericGraph.Unfolds c.graph c.report.root c.report.assumptions :=
  (closure_graph_sound.{0} E c).2.2.2.2.2.2.2

theorem core_graph_sound (E : VE.Environment)
    (c : Checked VE.Core.Formula VE.Core.Tableau.Certificate (coreWf E) (coreValid E)) :
    GenericGraph.Acyclic c.graph ∧ (c.graph.nodes.map (fun n => n.claim.name)).Nodup ∧
      c.report.root.name = c.graph.root ∧
      GenericGraph.SoundReport (fun S : VE.Structure.{u} => S.Admissible E) (fun S a => a.denote S [])
        (coreWf E) c.graph c.report :=
  GenericGraph.check_sound _ _ _ _
    (fun cert _ _ h => VE.Core.Tableau.checkCertificate_sound E _ _ cert h) c.graph c.report c.accepted

theorem core_graph_entails (E : VE.Environment)
    (c : Checked VE.Core.Formula VE.Core.Tableau.Certificate (coreWf E) (coreValid E)) :
    VE.Core.Entails.{u} E (c.report.assumptions.map Claim.formula) c.report.root.formula :=
  (core_graph_sound.{u} E c).2.2.2.2.2.2.1

theorem core_graph_unfolds (E : VE.Environment)
    (c : Checked VE.Core.Formula VE.Core.Tableau.Certificate (coreWf E) (coreValid E)) :
    GenericGraph.Unfolds c.graph c.report.root c.report.assumptions :=
  (core_graph_sound.{0} E c).2.2.2.2.2.2.2

theorem order_graph_sound (E : VE.Order.Environment)
    (c : Checked VE.Order.Formula VE.Order.Tableau.Certificate (orderWf E) (orderValid E)) :
    GenericGraph.Acyclic c.graph ∧ (c.graph.nodes.map (fun n => n.claim.name)).Nodup ∧
      c.report.root.name = c.graph.root ∧
      GenericGraph.SoundReport (fun S : VE.Order.Structure.{u} => S.Admissible E) (fun S a => a.denote S [])
        (orderWf E) c.graph c.report :=
  GenericGraph.check_sound _ _ _ _
    (fun cert _ _ h => VE.Order.Tableau.checkCertificate_sound E _ _ cert h) c.graph c.report c.accepted

theorem order_graph_entails (E : VE.Order.Environment)
    (c : Checked VE.Order.Formula VE.Order.Tableau.Certificate (orderWf E) (orderValid E)) :
    VE.Order.Entails.{u} E (c.report.assumptions.map Claim.formula) c.report.root.formula :=
  (order_graph_sound.{u} E c).2.2.2.2.2.2.1

theorem order_graph_unfolds (E : VE.Order.Environment)
    (c : Checked VE.Order.Formula VE.Order.Tableau.Certificate (orderWf E) (orderValid E)) :
    GenericGraph.Unfolds c.graph c.report.root c.report.assumptions :=
  (order_graph_sound.{0} E c).2.2.2.2.2.2.2

/-! ## Readings -/

/-- Python's right-nested per-set disjunction on the wire. -/
def disjunctionJson : List Json → Json
  | [] => Json.arr #[.str "bottom"]
  | [a] => a
  | a :: b :: rest => Json.arr #[.str "or", a, disjunctionJson (b :: rest)]

/-- `Readings.readingsCase` over a family context: Lean rebuilds the premise
lists and checks the verdict's evidence with the family's certificate
predicate and budgeted refutation check. -/
def readings (ctx : Ctx F C M) (valid : C → List F → F → Bool) (refutes : M → List F → F → Bool)
    (disj : F → F → F) (bot : F) (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let B := ctx.background.map (·.1)
  let fixedJson := (← (← j.getObjVal? "fixed").getArr?).toList
  let fixed ← fixedJson.mapM ctx.formula
  let setsJson ← (← (← j.getObjVal? "sets").getArr?).toList.mapM fun s => do pure (← s.getArr?).toList
  unless setsJson.all (!·.isEmpty) do throw "every reading set holds a reading"
  let sets ← setsJson.mapM (·.mapM ctx.formula)
  let conclusionJson ← j.getObjVal? "conclusion"
  let φ ← ctx.formula conclusionJson
  let evidence ← j.getObjVal? "evidence"
  let bound := fun (premises : List Json) (c : C) => ctx.bound (fixedJson ++ premises) conclusionJson c
  let chosen := fun (field : String) (ev : Json) => do
    let is ← (← (← ev.getObjVal? field).getArr?).toList.mapM fun x => do
      match x.getNat? with
      | .ok n => pure n
      | .error _ => throw "a choice is a list of reading indices"
    match GenericReadings.resolve sets is, GenericReadings.resolve setsJson is with
    | some choice, some choiceJson => pure (choice, choiceJson)
    | _, _ => throw "a choice must pick one reading of each set"
  let verdict ← VE.Bridge.stringField j "verdict"
  let accepted ← match verdict with
    | "ALL" => do
      let c ← ctx.certificate (← evidence.getObjVal? "certificate")
      bound (setsJson.map disjunctionJson) c
      pure (valid c (B ++ fixed ++ sets.map (disjunction disj bot)) φ)
    | "NONE" => do
      let m ← ctx.model (← evidence.getObjVal? "model")
      pure (refutes m (B ++ fixed ++ sets.flatten) φ)
    | "SOME" => do
      let proof ← evidence.getObjVal? "proof"
      let (proved, provedJson) ← chosen "choice" proof
      let c ← ctx.certificate (← proof.getObjVal? "certificate")
      bound provedJson c
      let counter ← evidence.getObjVal? "countermodel"
      let (refuted, _) ← chosen "choice" counter
      let m ← ctx.model (← counter.getObjVal? "model")
      pure (valid c (B ++ fixed ++ proved) φ && refutes m (B ++ fixed ++ refuted) φ)
    | _ => throw s!"unknown readings verdict {verdict}"
  unless accepted do throw s!"the {verdict} evidence does not check"
  pure (VE.Route.Wire.ok id [("verdict", .str verdict)])

/-- The `readings` case on the closure, core and order families. -/
def readingsCase (j : Json) : Except String Json := do
  let environment ← j.getObjVal? "environment"
  if Standalone.isLegacy environment then
    match ← Standalone.decodeLegacy environment with
    | .v0 v =>
      return ← readings (← legacyFolCtx environment v) (folValid v.environment)
        (folRefutes (v.predicates.map Prod.fst) v.environment) .or .bottom j
    | .closure v =>
      return ← readings (← legacyClosureCtx environment v) (closureValid v.environment)
        (closureRefutes (v.predicates.map Prod.fst) v.environment) .or .bottom j
    | .order v =>
      return ← readings (← legacyOrderCtx environment v) (orderValid v.environment)
        (orderRefutes (v.predicates.map Prod.fst) v.environment) .or .bottom j
  let checked ← Standalone.validated environment
  match checked.envelope.family with
  | .closure =>
    let f ← closureEnv environment checked
    let names := f.rv.modelVocabulary.predicates.map Prod.fst
    readings f.ctx (closureValid f.rv.environment) (closureRefutes names f.rv.environment)
      .or .bottom j
  | .closureNary =>
    let f ← coreEnv environment checked
    let names := (VE.Core.Wire.modelVocabulary f.v).predicates.map Prod.fst
    readings f.ctx (coreValid f.v.environment) (coreRefutes names f.v.environment) .or .bottom j
  | .order =>
    let f ← orderEnv environment checked
    let names := f.rv.modelVocabulary.predicates.map Prod.fst
    readings f.ctx (orderValid f.rv.vocabulary.environment)
      (orderRefutes names f.rv.vocabulary.environment) .or .bottom j
  | .fol => throw "the FOL family checks readings through Readings.readingsCase"

/-! ### What an accepted verdict means

For each family: an accepted `ALL` certificate makes every choice entail the
conclusion; an accepted `NONE` model is a countermodel for every choice; an
accepted `SOME` pair gives an entailing and a refuted choice
(`GenericReadings.readings_*_sound` at the family's semantics). -/

theorem fol_readings_all_sound (E : VE.Environment) (B fixed : List VE.Formula)
    (sets : List (List VE.Formula)) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (h : folValid E c (B ++ fixed ++ sets.map (disjunction .or .bottom)) φ = true) :
    ∀ choice, Choice sets choice → VE.Entails.{u} E (B ++ fixed ++ choice) φ :=
  GenericReadings.readings_all_sound (VE.Formula.or) VE.Formula.bottom
    (fun S : VE.Structure.{u} => S.Admissible E)
    (fun (S : VE.Structure.{u}) (a : VE.Formula) => a.denote S []) (fun _ _ _ => Iff.rfl) (fun _ h => h)
    B fixed sets φ (VE.Tableau.checkCertificate_sound E _ φ c h)

theorem fol_readings_none_sound (names : List String) (E : VE.Environment) (M : FolModel E)
    (B fixed : List VE.Formula) (sets : List (List VE.Formula)) (φ : VE.Formula)
    (h : folRefutes names E M (B ++ fixed ++ sets.flatten) φ = true) :
    ∀ choice, Choice sets choice → ¬ VE.Entails.{0} E (B ++ fixed ++ choice) φ :=
  GenericReadings.readings_none_sound _ _ B fixed sets φ (folRefutes_sound names E M _ φ h)

theorem fol_readings_some_sound (names : List String) (E : VE.Environment)
    (B fixed : List VE.Formula) (sets : List (List VE.Formula)) (φ : VE.Formula)
    (proved refuted : List VE.Formula) (hp : Choice sets proved) (hr : Choice sets refuted)
    (c : VE.Tableau.Certificate) (hc : folValid E c (B ++ fixed ++ proved) φ = true)
    (M : FolModel E) (hm : folRefutes names E M (B ++ fixed ++ refuted) φ = true) :
    (∃ choice, Choice sets choice ∧ VE.Entails.{0} E (B ++ fixed ++ choice) φ) ∧
      (∃ choice, Choice sets choice ∧ ¬ VE.Entails.{0} E (B ++ fixed ++ choice) φ) :=
  GenericReadings.readings_some_sound _ _ B fixed sets φ proved refuted hp hr
    (VE.Tableau.checkCertificate_sound E _ φ c hc) (folRefutes_sound names E M _ φ hm)

theorem closure_readings_all_sound (E : VE.Environment) (B fixed : List VE.Closure.Formula)
    (sets : List (List VE.Closure.Formula)) (φ : VE.Closure.Formula) (c : VE.Closure.Tableau.Certificate)
    (h : closureValid E c (B ++ fixed ++ sets.map (disjunction .or .bottom)) φ = true) :
    ∀ choice, Choice sets choice → VE.Closure.Entails.{u} E (B ++ fixed ++ choice) φ :=
  GenericReadings.readings_all_sound (VE.Closure.Formula.or) VE.Closure.Formula.bottom (fun S : VE.Structure.{u} => S.Admissible E)
    (fun (S : VE.Structure.{u}) (a : VE.Closure.Formula) => a.denote S []) (fun _ _ _ => Iff.rfl) (fun _ h => h) B fixed sets φ
    (VE.Closure.Tableau.checkCertificate_sound E _ φ c h)

theorem closure_readings_none_sound (names : List String) (E : VE.Environment) (M : ClosureModel E)
    (B fixed : List VE.Closure.Formula) (sets : List (List VE.Closure.Formula)) (φ : VE.Closure.Formula)
    (h : closureRefutes names E M (B ++ fixed ++ sets.flatten) φ = true) :
    ∀ choice, Choice sets choice → ¬ VE.Closure.Entails.{0} E (B ++ fixed ++ choice) φ :=
  GenericReadings.readings_none_sound _ _ B fixed sets φ (closureRefutes_sound names E M _ φ h)

theorem closure_readings_some_sound (names : List String) (E : VE.Environment)
    (B fixed : List VE.Closure.Formula) (sets : List (List VE.Closure.Formula)) (φ : VE.Closure.Formula)
    (proved refuted : List VE.Closure.Formula) (hp : Choice sets proved) (hr : Choice sets refuted)
    (c : VE.Closure.Tableau.Certificate) (hc : closureValid E c (B ++ fixed ++ proved) φ = true)
    (M : ClosureModel E) (hm : closureRefutes names E M (B ++ fixed ++ refuted) φ = true) :
    (∃ choice, Choice sets choice ∧ VE.Closure.Entails.{0} E (B ++ fixed ++ choice) φ) ∧
      (∃ choice, Choice sets choice ∧ ¬ VE.Closure.Entails.{0} E (B ++ fixed ++ choice) φ) :=
  GenericReadings.readings_some_sound _ _ B fixed sets φ proved refuted hp hr
    (VE.Closure.Tableau.checkCertificate_sound E _ φ c hc) (closureRefutes_sound names E M _ φ hm)

theorem core_readings_all_sound (E : VE.Environment) (B fixed : List VE.Core.Formula)
    (sets : List (List VE.Core.Formula)) (φ : VE.Core.Formula) (c : VE.Core.Tableau.Certificate)
    (h : coreValid E c (B ++ fixed ++ sets.map (disjunction .or .bottom)) φ = true) :
    ∀ choice, Choice sets choice → VE.Core.Entails.{u} E (B ++ fixed ++ choice) φ :=
  GenericReadings.readings_all_sound (VE.Core.Formula.or) VE.Core.Formula.bottom (fun S : VE.Structure.{u} => S.Admissible E)
    (fun (S : VE.Structure.{u}) (a : VE.Core.Formula) => a.denote S []) (fun _ _ _ => Iff.rfl) (fun _ h => h) B fixed sets φ
    (VE.Core.Tableau.checkCertificate_sound E _ φ c h)

theorem core_readings_none_sound (names : List String) (E : VE.Environment) (M : CoreModel E)
    (B fixed : List VE.Core.Formula) (sets : List (List VE.Core.Formula)) (φ : VE.Core.Formula)
    (h : coreRefutes names E M (B ++ fixed ++ sets.flatten) φ = true) :
    ∀ choice, Choice sets choice → ¬ VE.Core.Entails.{0} E (B ++ fixed ++ choice) φ :=
  GenericReadings.readings_none_sound _ _ B fixed sets φ (coreRefutes_sound names E M _ φ h)

theorem core_readings_some_sound (names : List String) (E : VE.Environment)
    (B fixed : List VE.Core.Formula) (sets : List (List VE.Core.Formula)) (φ : VE.Core.Formula)
    (proved refuted : List VE.Core.Formula) (hp : Choice sets proved) (hr : Choice sets refuted)
    (c : VE.Core.Tableau.Certificate) (hc : coreValid E c (B ++ fixed ++ proved) φ = true)
    (M : CoreModel E) (hm : coreRefutes names E M (B ++ fixed ++ refuted) φ = true) :
    (∃ choice, Choice sets choice ∧ VE.Core.Entails.{0} E (B ++ fixed ++ choice) φ) ∧
      (∃ choice, Choice sets choice ∧ ¬ VE.Core.Entails.{0} E (B ++ fixed ++ choice) φ) :=
  GenericReadings.readings_some_sound _ _ B fixed sets φ proved refuted hp hr
    (VE.Core.Tableau.checkCertificate_sound E _ φ c hc) (coreRefutes_sound names E M _ φ hm)

theorem order_readings_all_sound (E : VE.Order.Environment) (B fixed : List VE.Order.Formula)
    (sets : List (List VE.Order.Formula)) (φ : VE.Order.Formula) (c : VE.Order.Tableau.Certificate)
    (h : orderValid E c (B ++ fixed ++ sets.map (disjunction .or .bottom)) φ = true) :
    ∀ choice, Choice sets choice → VE.Order.Entails.{u} E (B ++ fixed ++ choice) φ :=
  GenericReadings.readings_all_sound (VE.Order.Formula.or) VE.Order.Formula.bottom (fun S : VE.Order.Structure.{u} => S.Admissible E)
    (fun (S : VE.Order.Structure.{u}) (a : VE.Order.Formula) => a.denote S []) (fun _ _ _ => Iff.rfl) (fun _ h => h) B fixed sets φ
    (VE.Order.Tableau.checkCertificate_sound E _ φ c h)

theorem order_readings_none_sound (names : List String) (E : VE.Order.Environment) (d : OrderModel E)
    (B fixed : List VE.Order.Formula) (sets : List (List VE.Order.Formula)) (φ : VE.Order.Formula)
    (h : orderRefutes names E d (B ++ fixed ++ sets.flatten) φ = true) :
    ∀ choice, Choice sets choice → ¬ VE.Order.Entails.{0} E (B ++ fixed ++ choice) φ :=
  GenericReadings.readings_none_sound _ _ B fixed sets φ (orderRefutes_sound names E d _ φ h)

theorem order_readings_some_sound (names : List String) (E : VE.Order.Environment)
    (B fixed : List VE.Order.Formula) (sets : List (List VE.Order.Formula)) (φ : VE.Order.Formula)
    (proved refuted : List VE.Order.Formula) (hp : Choice sets proved) (hr : Choice sets refuted)
    (c : VE.Order.Tableau.Certificate) (hc : orderValid E c (B ++ fixed ++ proved) φ = true)
    (d : OrderModel E) (hm : orderRefutes names E d (B ++ fixed ++ refuted) φ = true) :
    (∃ choice, Choice sets choice ∧ VE.Order.Entails.{0} E (B ++ fixed ++ choice) φ) ∧
      (∃ choice, Choice sets choice ∧ ¬ VE.Order.Entails.{0} E (B ++ fixed ++ choice) φ) :=
  GenericReadings.readings_some_sound _ _ B fixed sets φ proved refuted hp hr
    (VE.Order.Tableau.checkCertificate_sound E _ φ c hc) (orderRefutes_sound names E d _ φ hm)

end VE.Service.Family

namespace VE.Service.Family
open Lean

/-- Whether a `ve.core@0.2` envelope names the closure, core or order family
(its profiles include `closure@0` or `order@0`). -/
def isFamily (environment : Json) : Bool :=
  environment.getObjValD "language" == .str "ve.core@0.2" &&
    match VE.Route.Gate.profilesOf environment with
    | .ok ps => ps.contains "closure@0" || ps.contains "order@0"
    | .error _ => false

/-- The service `graph` mode: the FOL family and the v0 envelope through
`Graph.graphCase`, the closure, core and order families and the ve.core@0.1
envelopes through `graphCase`. -/
def graphMode (j : Json) : Except String Json := do
  let environment ← j.getObjVal? "environment"
  if isFamily environment || environment.getObjValD "language" == .str "ve.core@0.1" then graphCase j
  else Graph.graphCase j

/-- The service `readings` mode: the FOL family through
`Readings.readingsCase`, the closure, core and order families and the frozen
pre-route envelopes through `readingsCase`. -/
def readingsMode (j : Json) : Except String Json := do
  let environment ← j.getObjVal? "environment"
  if isFamily environment || Standalone.isLegacy environment then readingsCase j
  else Readings.readingsCase j

end VE.Service.Family
