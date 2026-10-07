import VE.Route.Run
import VE.Route.Metered
import VE.Route.MeteredTrace
import VE.Route.NonVacuity
import VE.Core.Layers

/-! The batch-15a Lean entry point. Existing route cases keep their proved
response shapes; batch 15b can relay this case after its trace and witness
contracts have been checked against the frozen oracle. -/
namespace VE.Route.MeteredRun
open Lean
open VE.Route

def tick (limit work : Nat) : Option Nat :=
  if work ≥ limit then none else some (work + 1)

def tickCache {F : Type} [DecidableEq F] [Hashable F] (limit : Nat)
    (state : VE.Route.Closure.Meter F) : Option (VE.Route.Closure.Meter F) :=
  if state.work ≥ limit then none else some { state with work := state.work + 1 }

def nonVacuityResult (id : String) (limit : Nat) (answer : Option (Bool × Nat)) : Json :=
  let (suitable, work, exhausted) := match answer with
    | some (b, w) => (b, w, false)
    | none => (false, limit, true)
  Wire.ok id [("suitable", .bool suitable), ("evaluations", toJson work),
    ("exhausted", .bool exhausted)]

/-- The core family's layer projection is the existing core route's projection. -/
def coreLayers (profiles : List String) (environment model : Json) : Except String (Json × Json) := do
  let rv ← VE.Core.Layers.decodeLayers profiles environment
  let core ← VE.Core.Layers.coreEnvironment environment
  let _ ← VE.Core.Bridge.decodeEnvironment core
  let names := (← VE.Core.Layers.folPredicates environment).map Prod.fst
  let M ← Wire.decodeDataModel rv (← VE.Core.Layers.folModel names model)
  let tables := (VE.Definitions.names rv.definitions).map fun p =>
    (p, VE.Core.Layers.tableJson (M.relations p))
  let relations ← VE.Bridge.fields (← model.getObjVal? "relations")
  pure (core, model.setObjVal! "relations" (Json.mkObj (relations ++ tables)))

def runNonVacuity (j : Json) (id : String) (environment : Json)
    (envelope : Gate.Envelope) : Except String Json := do
  let limit ← Metered.budget j "max_evaluations" VE.Time.maxEvaluations
  let semantic ← match j.getObjVal? "semantic_nonvacuity" with
    | .ok value => value.getBool?
    | .error _ => pure false
  let formula ← j.getObjVal? "formula"
  let model ← j.getObjVal? "model"
  let answer ← match envelope.family with
    | .fol => do
      let rv ← Wire.decodeVocabulary envelope.profiles envelope.vocabulary
      let f ← Wire.decodeClosed rv.environment formula (envelope.profiles.contains "data@0")
      let M ← Wire.decodeDataModel rv model
      let idx := Wire.modelIndex rv M
      let ops : NonVacuity.Ops VE.Formula (List VE.Bridge.Entity) Nat VE.Bridge.Entity :=
        { view := NonVacuity.viewF, tick := tick limit,
          eval := fun a ρ w => Budget.evalF (Budget.tableMem M idx) M limit ρ a w,
          domain := M.domains, bind := fun _ e ρ => e :: ρ }
      pure (NonVacuity.check ops f [] 0 semantic)
    | .closure => do
      let rv ← Wire.decodeVocabulary envelope.profiles envelope.vocabulary
      let f ← VE.Closure.Bridge.decodeFormula 64 formula
      unless f.check rv.environment [] do throw "ill-typed or unbound formula"
      let M ← Wire.decodeDataModel rv model
      let idx := Wire.modelIndex rv M
      let ops : NonVacuity.Ops VE.Closure.Formula (List VE.Bridge.Entity)
          (VE.Route.Closure.Meter VE.Closure.Formula) VE.Bridge.Entity :=
        { view := NonVacuity.viewC, tick := tickCache limit,
          eval := fun a ρ s => Budget.evalC (Budget.tableMem M idx) M limit ρ a s,
          domain := M.domains, bind := fun _ e ρ => e :: ρ }
      pure ((NonVacuity.check ops f [] ⟨0, {}⟩ semantic).map fun r => (r.1, r.2.work))
    | .order => do
      let rv ← Wire.decodeOrderVocabulary envelope.vocabulary
      let f ← VE.Order.Wire.decodeFormula 64 formula
      unless f.check rv.vocabulary.environment [] do throw "ill-typed or unbound formula"
      let d ← Wire.decodeOrderModel rv model
      let M := (Budget.sortOrderData d).toModel
      let idx := Wire.orderIndex rv M
      let ops : NonVacuity.Ops VE.Order.Formula (List (VE.Order.Value VE.Order.Wire.Entity))
          Nat VE.Order.Wire.Entity :=
        { view := NonVacuity.viewB, tick := tick limit,
          eval := fun a ρ w => VE.Time.evalB (Budget.orderMem M idx) M limit ρ a w,
          domain := M.domains, bind := fun _ e ρ => .inl e :: ρ }
      pure (NonVacuity.check ops f [] 0 semantic)
    | .closureNary => do
      let v ← VE.Core.Bridge.decodeEnvironment environment
      let f ← VE.Core.Bridge.decodeFormula 64 formula
      VE.Core.Bridge.checkFormula v.environment f "formula"
      let M ← VE.Core.Wire.decodeModel v model
      let idx := VE.Core.Wire.index v M
      let ops : NonVacuity.Ops VE.Core.Formula (List VE.Bridge.Entity)
          (VE.Route.Closure.Meter VE.Core.Formula) VE.Bridge.Entity :=
        { view := NonVacuity.viewN, tick := tickCache limit,
          eval := fun a ρ s => Budget.evalN (Budget.tableMem M idx) M limit ρ a s,
          domain := M.domains, bind := fun _ e ρ => e :: ρ }
      pure ((NonVacuity.check ops f [] ⟨0, {}⟩ semantic).map fun r => (r.1, r.2.work))
  pure (nonVacuityResult id limit answer)

def runCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let kind ← VE.Bridge.stringField j "kind"
  unless kind == "evaluate-budgeted" || kind == "non-vacuity" do throw "unknown case kind"
  let environment ← j.getObjVal? "environment"
  let envelope ← Gate.decodeEnvelope environment
  let (environment, model) ← if envelope.family == .closureNary &&
      VE.Core.Layers.usesLayers environment then
    coreLayers envelope.profiles environment (← j.getObjVal? "model")
    else pure (environment, ← j.getObjVal? "model")
  let j := (j.setObjVal! "environment" environment).setObjVal! "model" model
  if kind == "non-vacuity" then return ← runNonVacuity j id environment envelope
  let limit ← Metered.limit j
  let trace ← Metered.traceRequested j
  let maxEvaluations ← Metered.budget j "max_evaluations" VE.Time.maxEvaluations
  let maxTraceNodes ← Metered.budget j "max_trace_nodes" 10000
  let ast ← j.getObjVal? "ast"
  let model ← j.getObjVal? "model"
  let (result, explanation) ← match envelope.family with
    | .fol => do
      let rv ← Wire.decodeVocabulary envelope.profiles envelope.vocabulary
      let fs ← Wire.decodeFormulas rv.environment ast (envelope.profiles.contains "data@0")
      if fs.isEmpty then throw "empty document"
      let M ← Wire.decodeDataModel rv model
      let idx := Wire.modelIndex rv M
      let step := fun f w => Budget.evalF (Budget.tableMem M idx) M limit [] f w
      let result := Metered.evaluate step limit fs
      pure (result, if trace then MeteredTrace.document (MeteredTrace.fol M)
        step 0 [] fs result maxEvaluations maxTraceNodes else Json.null)
    | .closure => do
      let rv ← Wire.decodeVocabulary envelope.profiles envelope.vocabulary
      let fs ← VE.Closure.Bridge.decodeFormulas rv.environment ast
      if fs.isEmpty then throw "empty document"
      let M ← Wire.decodeDataModel rv model
      let idx := Wire.modelIndex rv M
      let step := fun f s => Budget.evalC (Budget.tableMem M idx) M limit [] f s
      let initial : VE.Route.Closure.Meter VE.Closure.Formula := ⟨0, {}⟩
      let result := Metered.scanState step (fun s => s.work) limit fs initial
      pure (result, if trace then MeteredTrace.document (MeteredTrace.closure M)
        step initial [] fs result maxEvaluations maxTraceNodes else Json.null)
    | .order => do
      let rv ← Wire.decodeOrderVocabulary envelope.vocabulary
      let fs ← VE.Order.Wire.decodeFormulas rv.vocabulary.environment ast
      if fs.isEmpty then throw "empty document"
      let d ← Wire.decodeOrderModel rv model
      let M := (Budget.sortOrderData d).toModel
      let idx := Wire.orderIndex rv M
      let step := fun f w => VE.Time.evalB (Budget.orderMem M idx) M limit [] f w
      let result := Metered.evaluate step limit fs
      pure (result, if trace then MeteredTrace.document (MeteredTrace.order M)
        step 0 [] fs result maxEvaluations maxTraceNodes else Json.null)
    | .closureNary => do
      let v ← VE.Core.Bridge.decodeEnvironment environment
      let fs ← VE.Core.Bridge.decodeFormulas v.environment ast
      if fs.isEmpty then throw "empty document"
      let M ← VE.Core.Wire.decodeModel v model
      let idx := VE.Core.Wire.index v M
      let step := fun f s => Budget.evalN (Budget.tableMem M idx) M limit [] f s
      let initial : VE.Route.Closure.Meter VE.Core.Formula := ⟨0, {}⟩
      let result := Metered.scanState step (fun s => s.work) limit fs initial
      pure (result, if trace then MeteredTrace.document (MeteredTrace.core M)
        step initial [] fs result maxEvaluations maxTraceNodes else Json.null)
  pure (Wire.ok id [("evaluation", Json.mkObj
    (Metered.resultFields result ++ [("explanation", explanation)]))])

def runCaseReported (j : Json) : Json :=
  match runCase j with
  | .ok result => result
  | .error message => Json.mkObj [("id", j.getObjValD "id"),
      ("status", .str "error"), ("error", .str message)]

def main (paths : List String) : IO UInt32 := do
  let input ← match paths with
    | [] | ["-"] => (← IO.getStdin).readToEnd
    | [path] => IO.FS.readFile path
    | _ =>
      (← IO.getStderr).putStrLn "usage: ve_metered [cases.json|-]"
      return 2
  match VE.JsonInput.parseCases input with
  | .error message =>
    (← IO.getStderr).putStrLn message
    return 2
  | .ok cases =>
    let results := cases.mapIdx fun index c => match c with
      | .ok j => runCaseReported j
      | .error message => Json.mkObj [("status", .str "error"),
          ("case_index", toJson index), ("error", .str message)]
    (← IO.getStdout).putStrLn (Json.arr results).compress
    return 0

end VE.Route.MeteredRun
