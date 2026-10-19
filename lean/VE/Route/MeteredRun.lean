import VE.Route.Run
import VE.Route.Metered
import VE.Route.MeteredTrace
import VE.Route.NonVacuity
import VE.Route.AstLimit
import VE.Core.Layers
import VE.Service.Standalone
import VE.Limits

/-! The batch-15a Lean entry point. Existing route cases keep their proved
response shapes; batch 15b can relay this case after its trace and witness
contracts have been checked against the frozen oracle.

Every case reads its environment through the service's one validation
(`Standalone.evaluable`: the frozen `ve.core@0` and `ve.core@0.1` envelopes by
their frozen decoders, `ve.core@0.2` by `Standalone.validated`), and each
family is decoded once into a `Session` that both case kinds use.

What a case decodes from its environment alone is a `Prepared` (`prepare`): the
service keeps it with an environment handle and answers every case against that
handle with it (`VE.Service.Entry`), and `runCase` is `runWith` of the case's own
environment's. -/
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

/-- A case's family-independent fields, read before any family decoding. -/
structure Query where
  id : String
  nonVacuity : Bool
  /-- The work budget: `max_evaluations` for non-vacuity, `Metered.limit` for
  evaluation. -/
  limit : Nat
  semantic : Bool
  trace : Bool
  maxEvaluations : Nat
  maxTraceNodes : Nat
  /-- The candidate formula, or the document's formula list. -/
  input : Json

def query (j : Json) (id : String) (nonVacuity : Bool) : Except String Query := do
  if nonVacuity then
    let limit ← Metered.budget j "max_evaluations" VE.Time.maxEvaluations
    let semantic ← match j.getObjVal? "semantic_nonvacuity" with
      | .ok value => value.getBool?
      | .error _ => pure false
    let input ← j.getObjVal? "formula"
    pure ⟨id, true, limit, semantic, false, limit, 0, input⟩
  else
    let limit ← Metered.limit j
    let trace ← Metered.traceRequested j
    let maxEvaluations ← Metered.budget j "max_evaluations" VE.Time.maxEvaluations
    let maxTraceNodes ← Metered.budget j "max_trace_nodes" 10000
    let input ← j.getObjVal? "ast"
    pure ⟨id, false, limit, false, trace, maxEvaluations, maxTraceNodes, input⟩

/-- A decoded request: one candidate, or a nonempty document. -/
inductive Request (α : Type) where
  | nonVacuity (formula : α)
  | evaluate (formulas : List α)

/-- Python's AST limits hold on every family, counted across a document (as
the service's typing mode checks them), before the family decoder runs. -/
def request {α : Type} (q : Query) (formula : Json → Except String α)
    (formulas : Json → Except String (List α)) : Except String (Request α) := do
  AstLimit.check (← if q.nonVacuity then pure [q.input] else (·.toList) <$> q.input.getArr?)
  if q.nonVacuity then return .nonVacuity (← formula q.input)
  let fs ← formulas q.input
  if fs.isEmpty then throw "empty document"
  pure (.evaluate fs)

/-- One family over one decoded model: the non-vacuity traversal (whose `eval`
is the family's proved metered evaluator), the trace display, the closed
valuation and starting meter, and the family's proved document meter
(`MeteredProofs`). -/
structure Session (α ρ σ entity : Type) where
  ops : NonVacuity.Ops α ρ σ entity
  trace : MeteredTrace.Ops α ρ entity
  closed : ρ
  initial : σ
  work : σ → Nat
  document : List α → Metered.Result

/-- Both case kinds, once for every family. -/
def answer {α ρ σ entity : Type} (q : Query) (s : Session α ρ σ entity) :
    Request α → Json
  | .nonVacuity f => nonVacuityResult q.id q.limit
      ((NonVacuity.check s.ops f s.closed s.initial q.semantic).map fun r => (r.1, s.work r.2))
  | .evaluate fs =>
    let result := s.document fs
    let step := fun f state => s.ops.eval f s.closed state
    let explanation := if q.trace then (MeteredTrace.document s.trace step s.initial s.closed fs
        result q.maxEvaluations q.maxTraceNodes).json else Json.null
    Wire.ok q.id [("evaluation", Json.mkObj (Metered.resultFields result ++
      [("explanation", explanation)]))]

def fol (limit : Nat) (M : VE.FiniteModel VE.Bridge.Entity)
    (mem : String → List VE.Bridge.Entity → Bool) :
    Session VE.Formula (List VE.Bridge.Entity) Nat VE.Bridge.Entity :=
  let eval := fun a ρ w => Budget.evalF mem M limit ρ a w
  { ops := { view := NonVacuity.viewF, tick := tick limit, eval := eval,
             domain := M.domains, bind := fun _ e ρ => e :: ρ }
    trace := MeteredTrace.fol M, closed := [], initial := 0, work := id
    document := Metered.evaluate (fun f w => eval f [] w) limit }

def closure (limit : Nat) (M : VE.FiniteModel VE.Bridge.Entity)
    (mem : String → List VE.Bridge.Entity → Bool) :
    Session VE.Closure.Formula (List VE.Bridge.Entity)
      (VE.Route.Closure.Meter VE.Closure.Formula) VE.Bridge.Entity :=
  let eval := fun a ρ s => Budget.evalC mem M limit ρ a s
  { ops := { view := NonVacuity.viewC, tick := tickCache limit, eval := eval,
             domain := M.domains, bind := fun _ e ρ => e :: ρ }
    trace := MeteredTrace.closure M, closed := [], initial := ⟨0, {}⟩, work := (·.work)
    document := fun fs => Metered.scanState (fun f s => eval f [] s) (·.work) limit fs ⟨0, {}⟩ }

def core (limit : Nat) (M : VE.FiniteModel VE.Bridge.Entity)
    (mem : String → List VE.Bridge.Entity → Bool) :
    Session VE.Core.Formula (List VE.Bridge.Entity)
      (VE.Route.Closure.Meter VE.Core.Formula) VE.Bridge.Entity :=
  let eval := fun a ρ s => Budget.evalN mem M limit ρ a s
  { ops := { view := NonVacuity.viewN, tick := tickCache limit, eval := eval,
             domain := M.domains, bind := fun _ e ρ => e :: ρ }
    trace := MeteredTrace.core M, closed := [], initial := ⟨0, {}⟩, work := (·.work)
    document := fun fs => Metered.scanState (fun f s => eval f [] s) (·.work) limit fs ⟨0, {}⟩ }

def order (limit : Nat) (M : VE.Order.FiniteModel VE.Order.Wire.Entity)
    (mem : String → List (VE.Order.Value VE.Order.Wire.Entity) → Bool) :
    Session VE.Order.Formula (List (VE.Order.Value VE.Order.Wire.Entity)) Nat
      VE.Order.Wire.Entity :=
  let eval := fun a ρ w => VE.Time.evalB mem M limit ρ a w
  { ops := { view := NonVacuity.viewB, tick := tick limit, eval := eval,
             domain := M.domains, bind := fun _ e ρ => .inl e :: ρ }
    trace := MeteredTrace.order M, closed := [], initial := 0, work := id
    document := Metered.evaluate (fun f w => eval f [] w) limit }

/-- What a case decodes from its environment alone: the service's validation and,
on first use, the layers and the family's vocabulary decoded from it (each still an
`Except`, so that a case meets its faults in the same order as before). -/
structure Prepared where
  checked : Except String VE.Service.Standalone.Validated
  layered : Thunk (Except String VE.Core.Layers.Layered)
  route : Thunk (Except String Wire.RouteVocabulary)
  order : Thunk (Except String Wire.RouteOrderVocabulary)
  core : Thunk (Except String VE.Bridge.Vocabulary)

def prepare (environment : Json) : Prepared :=
  let checked := VE.Service.Standalone.evaluable environment
  { checked
    layered := Thunk.mk fun _ => do
      let c ← checked
      VE.Core.Layers.decodeLayered c.envelope.profiles (← c.layers.elim (throw "no layers") pure)
    route := Thunk.mk fun _ => do Run.decodeRouteVocabulary (← checked).envelope
    order := Thunk.mk fun _ => do Wire.decodeOrderVocabulary (← checked).envelope.vocabulary
    core := Thunk.mk fun _ => do VE.Core.Bridge.decodeEnvironment (← checked).decodable }

/-- The family dispatch: each family's vocabulary (`p`, of the validated environment
`checked`), request and model decoders, in that order, then `answer`. -/
def run (q : Query) (checked : VE.Service.Standalone.Validated) (p : Prepared) (model : Json) :
    Except String Json := do
  let e := checked.envelope
  match e.family with
  | .fol => do
    let rv ← p.route.get
    let data := e.profiles.contains "data@0"
    let r ← request q (Wire.decodeClosed rv.environment · data)
      (Wire.decodeFormulas rv.environment · data)
    let M ← Wire.decodeDataModel rv model
    pure (answer q (fol q.limit M (Budget.tableMem M (Wire.modelIndex rv M))) r)
  | .closure => do
    let rv ← p.route.get
    let r ← request q (fun j => do
        let f ← VE.Closure.Bridge.decodeFormula VE.Limits.maxDepth j
        unless f.check rv.environment [] do throw "ill-typed or unbound formula"
        pure f)
      (VE.Closure.Bridge.decodeFormulas rv.environment)
    let M ← Wire.decodeDataModel rv model
    pure (answer q (closure q.limit M (Budget.tableMem M (Wire.modelIndex rv M))) r)
  | .order => do
    let rv ← p.order.get
    let r ← request q (fun j => do
        let f ← VE.Order.Wire.decodeFormula VE.Limits.maxDepth j
        unless f.check rv.vocabulary.environment [] do throw "ill-typed or unbound formula"
        pure f)
      (VE.Order.Wire.decodeFormulas rv.vocabulary.environment)
    let d ← Wire.decodeOrderModel rv model
    let M := (Budget.sortOrderData d).toModel
    pure (answer q (order q.limit M (Budget.orderMem M (Wire.orderIndex rv M))) r)
  | .closureNary => do
    let v ← p.core.get
    let r ← request q (fun j => do
        let f ← VE.Core.Bridge.decodeFormula VE.Limits.maxDepth j
        VE.Core.Bridge.checkFormula v.environment f "formula"
        pure f)
      (VE.Core.Bridge.decodeFormulas v.environment)
    let M ← VE.Core.Wire.decodeModel v model
    pure (answer q (core q.limit M (Budget.tableMem M (VE.Core.Wire.index v M))) r)

/-- A case answered with `prepared`, what its environment decodes to (`prepare`). -/
def runWith (prepared : Except String Prepared) (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let kind ← VE.Bridge.stringField j "kind"
  unless kind == "evaluate-budgeted" || kind == "non-vacuity" do throw "unknown case kind"
  let p ← prepared
  let checked ← p.checked
  let model ← j.getObjVal? "model"
  -- A layered core environment's model gains its defined tables, computed by
  -- the one owner (`Core.Layers.completeModel`).
  let model ← match checked.layers with
    | some layered => do VE.Core.Layers.completeModel (← p.layered.get) layered model
    | none => pure model
  run (← query j id (kind == "non-vacuity")) checked p model

def runCase (j : Json) : Except String Json := runWith (prepare <$> j.getObjVal? "environment") j

def reportedWith (prepared : Except String Prepared) (j : Json) : Json :=
  match runWith prepared j with
  | .ok result => result
  | .error message => Json.mkObj [("id", j.getObjValD "id"),
      ("status", .str "error"), ("error", .str message)]

def runCaseReported (j : Json) : Json := reportedWith (prepare <$> j.getObjVal? "environment") j

/-- A case answered with what its own environment decodes to is answered as it was sent. -/
theorem reportedWith_prepare (j environment : Json) (h : j.getObjVal? "environment" = .ok environment) :
    reportedWith (.ok (prepare environment)) j = runCaseReported j := by
  simp [runCaseReported, h, Functor.map, Except.map]

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
    -- Exit 1 when some case is rejected, as every one-shot runner does (`ve.backends.lean.read_rows`).
    return if results.any (·.getObjValD "status" == .str "error") then 1 else 0

end VE.Route.MeteredRun
