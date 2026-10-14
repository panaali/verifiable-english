import VE.Core.Wire
import VE.Route.Wire

/-! Route cases on the core family (`closure@0` + `nary@0`) whose vocabulary
declares `definitions@0` defined predicates or `data@0` functional/total flags
(the migration plan's stage 2c). The core decoder has neither extension.

Data flags are decoded by the FOL route over the unary and binary projection.
Definitions of every arity use the core formula decoder, since even a unary or
binary head can depend on an n-ary atom. Every definition is placed in one
dependency order over all of them
(`Layered.order`, Python `compile_definitions`'s). Then

* `background`: the FOL route's regenerated Background (flags, definitions,
  literals), in Python's generator order, with every definition's biconditional
  in that one order (`definitionPremises`);
* `evaluate` and `countermodel`: the FOL projection of the model is decoded
  with its flags checked and its defined tables computed (`decodeDataModel`,
  `InvalidModel(flags|definitions|literals)`), the n-ary defined tables are
  computed under the same budget and tuple count (`completeModel`), and the
  core route answers the case over the environment without the layer fields
  and the model with the computed defined tables added.

* `certificate`: the core route's certificate branch over that Background,
  bound to the submitted environment (`coreCertificate`).

 -/
namespace VE.Core.Layers
open Lean
open VE.Bridge (fields strings)

def layerFields : List String := ["defined", "functional", "total"]

def predicatesOf (environment : Json) : List (String × Json) :=
  match (environment.getObjValD "vocabulary").getObjValD "predicates" with
  | .obj kvs => kvs.toList
  | _ => []

/-- The executable dispatch test: some predicate carries a layer field. -/
def usesLayers (environment : Json) : Bool :=
  (predicatesOf environment).any fun (_, entry) => layerFields.any fun f => (entry.getObjVal? f).isOk

def arity (entry : Json) : Nat :=
  match entry.getObjValD "arguments" with
  | .arr a => a.size
  | _ => 0

/-- Whether a predicate declaration is in the FOL projection: at most two arguments. The one
filter of every regenerated Background (`folPredicates`, the norms route's view). -/
def folEntry (entry : Json) : Bool := arity entry ≤ 2

def withPredicates (environment : Json) (predicates : List (String × Json)) : Except String Json := do
  let vocabulary ← environment.getObjVal? "vocabulary"
  pure (environment.setObjVal! "vocabulary" (vocabulary.setObjVal! "predicates" (Json.mkObj predicates)))

/-- The core environment: every predicate, without the layer fields. -/
def coreEnvironment (environment : Json) : Except String Json := do
  let predicates ← fields (← (← environment.getObjVal? "vocabulary").getObjVal? "predicates")
  withPredicates environment (← predicates.mapM fun (p, entry) => do
    pure (p, Json.mkObj ((← fields entry).filter (fun kv => !layerFields.contains kv.1))))

/-- The FOL projection owns base unary/binary predicates and their data flags;
core elaboration owns definitions of every arity. -/
def folPredicates (environment : Json) : Except String (List (String × Json)) := do
  let predicates ← fields (← (← environment.getObjVal? "vocabulary").getObjVal? "predicates")
  (predicates.filter fun (_, entry) => folEntry entry).filterMapM fun (p, entry) => do
    if (entry.getObjVal? "defined").isOk then
      if (entry.getObjVal? "functional").isOk || (entry.getObjVal? "total").isOk then
        throw "UnsupportedProfile: Defined predicates cannot carry functional or total flags"
      pure none
    else pure (some (p, entry))

def definitionsProfile : String := "defined declarations require the definitions@0 profile"

def decodeLayers (profiles : List String) (environment : Json) :
    Except String VE.Route.Wire.RouteVocabulary := do
  let vocabulary ← environment.getObjVal? "vocabulary"
  let rv ← VE.Route.Wire.decodeVocabulary profiles
    (vocabulary.setObjVal! "predicates" (Json.mkObj (← folPredicates environment)))
  pure rv

/-! ## n-ary definitions -/

/-- A definition `name(args) := body` of one to six arguments; the body is a core formula. -/
structure NaryDef where
  name : String
  args : List String
  body : Formula
  deriving DecidableEq, Repr

/-- The defined atom applied to the bound arguments: `var (n-1)`, …, `var 0`. -/
def NaryDef.head (d : NaryDef) : Formula :=
  match d.args.length with
  | 1 => .unary d.name (.var 0)
  | 2 => .binary d.name (.var 1) (.var 0)
  | _ => .atom d.name ((List.range d.args.length).reverse.map VE.Term.var)

/-- The closed biconditional, with binders in declared argument order (Python
`definitions.premise`). -/
def NaryDef.premise (d : NaryDef) : Formula :=
  d.args.foldr (fun s a => .all s a) (.and (.implies d.head d.body) (.implies d.body d.head))

/-- The predicate symbols a body mentions (edges of the dependency DAG). -/
def mentions : Formula → List String
  | .unary p _ | .binary p _ _ | .atom p _ | .reachNamed _ p _ _ => [p]
  | .not a | .all _ a | .ex _ a | .reachBody _ _ a _ _ => mentions a
  | .and a b | .or a b | .implies a b => mentions a ++ mentions b
  | .top | .bottom | .eq _ _ => []

def hasReach (a : Formula) : Bool :=
  VE.Reports.Preflight.hasReach 65 (VE.Core.Wire.encodeFormula a)

/-- One elaboration step over the core environment `E`, with later definitions hidden. -/
def stepOkFrom (minArity : Nat) (E : VE.Environment) (later : List String) (d : NaryDef) : Bool :=
  !later.contains d.name && E.predicates d.name == some d.args &&
    decide (minArity ≤ d.args.length) && decide (d.args.length ≤ 6) && d.args.all E.sorts.contains &&
    d.body.check (VE.Definitions.hide E (d.name :: later)) d.args.reverse

def stepOk (E : VE.Environment) (later : List String) (d : NaryDef) : Bool := stepOkFrom 3 E later d

/-- A checked definition has a declared arity and a body typed over earlier symbols. -/
theorem stepOkFrom_sound (minArity : Nat) (E : VE.Environment) (later : List String) (d : NaryDef)
    (h : stepOkFrom minArity E later d = true) :
    d.name ∉ later ∧ E.predicates d.name = some d.args ∧ minArity ≤ d.args.length ∧ d.args.length ≤ 6 ∧
      (∀ s ∈ d.args, s ∈ E.sorts) ∧
      d.body.WellFormed (VE.Definitions.hide E (d.name :: later)) d.args.reverse := by
  simp only [stepOkFrom, Bool.and_eq_true, Bool.not_eq_true', beq_iff_eq, decide_eq_true_eq,
    List.all_eq_true, List.contains_iff_mem] at h
  obtain ⟨⟨⟨⟨⟨hlater, hdecl⟩, hlo⟩, hhi⟩, hargs⟩, hbody⟩ := h
  exact ⟨by simpa [List.contains_iff_mem] using hlater, hdecl, hlo, hhi, hargs,
    (VE.Core.check_iff_wellFormed _ _ _).mp hbody⟩

/-- The original n-ary specialization and its unchanged statement. -/
theorem stepOk_sound (E : VE.Environment) (later : List String) (d : NaryDef)
    (h : stepOk E later d = true) :
    d.name ∉ later ∧ E.predicates d.name = some d.args ∧ 3 ≤ d.args.length ∧ d.args.length ≤ 6 ∧
      (∀ s ∈ d.args, s ∈ E.sorts) ∧
      d.body.WellFormed (VE.Definitions.hide E (d.name :: later)) d.args.reverse :=
  stepOkFrom_sound 3 E later d h

def chainOk (E : VE.Environment) : List NaryDef → Bool
  | [] => true
  | d :: ds => stepOkFrom 1 E (ds.map NaryDef.name) d && chainOk E ds

/-- The generated biconditional is within the AST limits of one formula. -/
def premiseWithin (d : NaryDef) : Bool :=
  (VE.Route.AstLimit.check [VE.Core.Wire.encodeFormula d.premise]).isOk

/-- The diagnostic of the first definition (in dependency order) whose step fails, or whose
generated biconditional exceeds the AST limits (the FOL layer's texts). -/
def firstBad (E : VE.Environment) : List NaryDef → Option String
  | [] => none
  | d :: ds =>
    if stepOkFrom 1 E (ds.map NaryDef.name) d then
      if premiseWithin d then firstBad E ds else some (VE.Definitions.premiseTooLarge d.name)
    else some (VE.Definitions.bodyNotTyped d.name)

theorem firstBad_none (E : VE.Environment) : (ds : List NaryDef) → firstBad E ds = none →
    chainOk E ds = true
  | [], _ => rfl
  | d :: ds, h => by
    unfold firstBad at h
    split at h
    · rename_i hs
      split at h
      · simp [chainOk, hs, firstBad_none E ds h]
      · cases h
    · cases h

/-- The dependency graph of every definition: the FOL definitions `fol`, then the n-ary `entries`. -/
def definitionNodes (fol : List VE.Definitions.Def) (entries : List NaryDef) : List VE.Route.DepNode :=
  fol.map (fun d => ⟨d.name, VE.Definitions.mentions d.body⟩) ++
    entries.map fun d => ⟨d.name, mentions d.body⟩

/-- The one dependency order over every definition (`dependencyOrder`, its cycle diagnostic,
over the FOL definitions `fol` and the n-ary `entries`, as Python orders all of them at once),
and the n-ary definitions in that order, each checked over the core environment `E`. The
vocabulary's 256-predicate limit bounds the graph. -/
def elaborateNary (E : VE.Environment) (fol : List VE.Definitions.Def) (entries : List NaryDef) :
    Except String (List String × List NaryDef) := do
  let order ← VE.Route.dependencyOrder (definitionNodes fol entries)
  let ds := order.filterMap fun p => entries.find? (·.name == p)
  match firstBad E ds with
  | some e => throw e
  | none => pure (order, ds)

/-- Every elaborated list is a chain of checked steps, and its order is the one dependency
order of every definition. -/
theorem elaborateNary_chain (E : VE.Environment) (fol : List VE.Definitions.Def)
    (entries : List NaryDef) (order : List String) (ds : List NaryDef)
    (h : elaborateNary E fol entries = .ok (order, ds)) :
    chainOk E ds = true ∧ VE.Route.dependencyOrder (definitionNodes fol entries) = .ok order := by
  unfold elaborateNary at h
  obtain ⟨o, ho, h⟩ := VE.Order.ProfileGate.bind_ok h
  dsimp only at h
  split at h
  · cases h
  · rename_i hn
    cases h
    exact ⟨firstBad_none E _ hn, ho⟩

/-- All `defined` declarations, in declaration order: arguments equal to the
declaration's, and a core body within its own AST limits without reachability; a rejected
body is named as Python names it (`Wire.bodyFault`, the FOL bodies' owner too). -/
def naryEntries (environment : Json) : Except String (List NaryDef) := do
  let predicates ← fields (← (← environment.getObjVal? "vocabulary").getObjVal? "predicates")
  predicates.filterMapM fun (p, entry) => do
    match entry.getObjVal? "defined" with
    | .error _ => pure none
    | .ok payload =>
      let ss ← strings (← entry.getObjVal? "arguments")
      let j ← VE.Route.Wire.definedPayload p ss payload
      VE.Route.AstLimit.check [j]
      let body ← (VE.Core.Bridge.decodeFormula 64 j).mapError (VE.Route.Wire.bodyFault p j)
      if hasReach body then throw VE.Route.Wire.reachBodyUnsupported
      pure (some ⟨p, ss, body⟩)

/-- A layered core environment: the FOL projection's layers, the checked core
environment without the layer fields and its vocabulary, the one dependency order of
every definition and the elaborated n-ary definitions. -/
structure Layered where
  rv : VE.Route.Wire.RouteVocabulary
  core : Json
  v : VE.Bridge.Vocabulary
  order : List String
  nary : List NaryDef
  chain : chainOk v.environment nary = true

def decodeLayered (profiles : List String) (environment : Json) : Except String Layered := do
  let rv ← decodeLayers profiles environment
  let core ← coreEnvironment environment
  let v ← VE.Core.Bridge.decodeEnvironment core
  let entries ← naryEntries environment
  unless entries.isEmpty || profiles.contains "definitions@0" do
    throw definitionsProfile
  match h : elaborateNary v.environment rv.definitions entries with
  | .ok (order, nary) => pure ⟨rv, core, v, order, nary, (elaborateNary_chain _ _ _ _ _ h).1⟩
  | .error e => throw e

/-! ## Background -/

/-- Every definition's biconditional, FOL or n-ary, in the one dependency order
(`Layered.order`). The FOL definitions are closed under dependencies (an FOL body cannot
mention an n-ary predicate), so without n-ary definitions their own order is that order. -/
def definitionPremises (L : Layered) : List Formula :=
  match L.nary with
  | [] => (VE.Definitions.expand L.rv.definitions).map embed
  | _ =>
    let premises := L.rv.definitions.map (fun d => (d.name, embed d.premise)) ++
      L.nary.map fun d => (d.name, d.premise)
    L.order.filterMap fun p => List.lookup p premises

/-- The regenerated Background with generators: the FOL route's flags, every definition in
the one dependency order, then the literals. -/
def background (L : Layered) : List (Formula × String) :=
  (VE.Data.Background.generate L.rv.flags).map (fun a => (embed a, "flags")) ++
    (definitionPremises L).map (fun a => (a, "definitions")) ++
    (VE.Route.Background.background L.rv.literals).map (fun p => (embed p.1, p.2))

/-- Without n-ary definitions the Background is the FOL route's, embedded. -/
theorem background_fol (L : Layered) (h : L.nary = []) :
    background L = (VE.Route.Wire.fullBackground L.rv).map (fun p => (embed p.1, p.2)) := by
  simp [background, definitionPremises, h, VE.Route.Wire.fullBackground, List.map_map,
    Function.comp_def]

/-- Every premise's generator is a Background generator. -/
theorem background_generators (L : Layered) :
    ∀ p ∈ background L, p.2 ∈ VE.Route.Background.generators := by
  intro p hp
  simp only [background, VE.Route.Background.background, List.mem_append, List.mem_map] at hp
  rcases hp with (⟨_, _, rfl⟩ | ⟨_, _, rfl⟩) | ⟨_, ⟨_, _, rfl⟩, rfl⟩ <;>
    simp [VE.Route.Background.generators]

/-- The `background` case: the regenerated Background, in order, with each premise's generator. -/
def runBackground (id : String) (bg : List (Formula × String)) : Json :=
  VE.Route.Wire.ok id [("background", Json.arr (bg.map (fun p => VE.Core.Wire.encodeFormula p.1)).toArray),
    ("premises", Json.arr (bg.map (fun p => VE.Core.Wire.encodeFormula p.1)).toArray),
    ("generators", Json.arr (bg.map (fun p => Json.str p.2)).toArray)]

/-! ## Models -/

/-- The model's relations restricted to the FOL projection's base predicates. -/
def folModel (names : List String) (model : Json) : Except String Json := do
  let relations ← fields (← model.getObjVal? "relations")
  pure (model.setObjVal! "relations" (Json.mkObj (relations.filter fun (p, _) => names.contains p)))

def tableJson (rows : List (List VE.Bridge.Entity)) : Json :=
  Json.arr (rows.map fun row => Json.arr (row.map fun e => Json.str e.2).toArray).toArray

/-- The budgeted value of a core body at a valuation, from a work count (a fresh closure
cache: bodies have no reachability). -/
def bodyValue (M : VE.FiniteModel VE.Bridge.Entity) (mem : String → List VE.Bridge.Entity → Bool)
    (body : Formula) (acc : List VE.Bridge.Entity) (w : Nat) : Option (Bool × Nat) :=
  (VE.Route.Budget.evalN mem M VE.Time.maxEvaluations acc body ⟨w, {}⟩).map fun r => (r.1, r.2.work)

/-- Each n-ary definition's biconditional under its own evaluation budget, as the FOL
layer checks its definitions (`Wire.definitionsCheck`): UNKNOWN is `ResourceLimit`. -/
def naryCheck (mem : String → List VE.Bridge.Entity → Bool)
    (M : VE.FiniteModel VE.Bridge.Entity) : List Formula → Except String Unit
  | [] => .ok ()
  | a :: as => match VE.Route.Budget.evalN mem M VE.Time.maxEvaluations [] a ⟨0, {}⟩ with
    | none => .error VE.Route.Wire.definitionBackgroundBudget
    | some (false, _) => .error (VE.Route.Wire.invalidModel "definitions")
    | some (true, _) => naryCheck mem M as

theorem naryCheck_ok (mem : String → List VE.Bridge.Entity → Bool)
    (M : VE.FiniteModel VE.Bridge.Entity) (hmem : ∀ p row, mem p row = true ↔ row ∈ M.relations p) :
    ∀ (as : List Formula), naryCheck mem M as = .ok () → as.all (fun a => a.eval M []) = true
  | [], _ => rfl
  | a :: as, h => by
    simp only [naryCheck] at h
    split at h
    · cases h
    · cases h
    · rename_i s ha
      have hv := (VE.Route.Budget.evalN_sound mem M _ hmem a [] _ _
        (VE.Route.Closure.cacheOK_empty _ 0) ha).1
      simp only [List.all_cons, Bool.and_eq_true]
      exact ⟨hv.symm, naryCheck_ok mem M hmem as h⟩

/-- The one owner of a layered environment's core model, called by the core
route, the service's model and core-family modes and the metered route: the
FOL projection of `model` is decoded with its flags checked and its defined
tables computed (`decodeDataModel`), and those tables are added to `model`'s
relations. The n-ary defined tables follow, each body evaluated on the model
with every lower table, under the FOL tables' remaining budget and tuple count
(Python shares one budget across all definitions, so exhaustion depends only on
the total work), and each n-ary biconditional is then checked on the result. -/
def completeModel (L : Layered) (environment model : Json) : Except String Json := do
  let names := (← folPredicates environment).map Prod.fst
  let folJson ← folModel names model
  let M ← VE.Route.Wire.decodeDataModel L.rv folJson
  let tables := (VE.Definitions.names L.rv.definitions).map fun p => (p, tableJson (M.relations p))
  let relations ← fields (← model.getObjVal? "relations")
  let complete := model.setObjVal! "relations" (Json.mkObj (relations ++ tables))
  if L.nary.isEmpty then return complete
  let naryNames := L.nary.map NaryDef.name
  VE.Route.Wire.noSuppliedTables naryNames model
  let folData := VE.Route.Wire.sortModelData
    (← VE.Route.Decode.decodeModelData L.rv.baseModelVocabulary folJson)
  let (_, w, folTuples) ← VE.Route.Budget.computeDefinedS folData L.rv.definitions
  let base := { L.v with predicates := L.v.predicates.filter fun p => !naryNames.contains p.1 }
  let data := VE.Route.Wire.sortModelData
    (← VE.Route.Decode.decodeModelData (VE.Core.Wire.modelVocabulary base) complete)
  -- A tuple-limit crossing within the FOL tables, counted with every base tuple.
  let tuples := VE.Route.Budget.tupleCount data
  if folTuples > VE.Route.Budget.tupleCount folData && tuples > 100000 then
    throw VE.Route.Budget.tupleLimit
  let (data, _, _) ← VE.Route.Budget.computeDefinedWith data
    (L.nary.map fun d => (d.name, d.args, d.body)) bodyValue (w, tuples)
  let full := data.toModel
  naryCheck (VE.Route.Budget.tableMem full (VE.Route.Budget.tableIndex (data.relations.map Prod.fst) full))
    full (L.nary.map NaryDef.premise)
  let naryTables := naryNames.map fun p => (p, tableJson (full.relations p))
  pure (model.setObjVal! "relations" (Json.mkObj (relations ++ tables ++ naryTables)))

/-! ## Certificates and the route -/

/-- The core route's certificate branch over a regenerated `background`
(core formulas), bound to the submitted `environment`: every checked premise
(Background first, then the case's premises) and the conclusion by meaning id.
Acceptance is `VE.Core.Tableau.checkCertificate` over `background ++
premises`, sound by `VE.Core.Tableau.checkCertificate_sound`. -/
def coreCertificate (profiles : List String) (environment core : Json) (background : List Formula)
    (id : String) (j : Json) : Except String Json := do
  let v ← VE.Core.Bridge.decodeEnvironment core
  let E := v.environment
  let premisesJson ← j.getObjVal? "premises"
  let _ ← VE.Route.Wire.formulasJson premisesJson (some (← j.getObjVal? "conclusion"))
  let ps ← VE.Core.Bridge.decodeFormulas E premisesJson
  let c ← VE.Core.Bridge.decodeFormula 64 (← j.getObjVal? "conclusion")
  VE.Core.Bridge.checkFormula E c "conclusion"
  VE.Route.Wire.nodeLimit ((c :: ps).map VE.Core.Bridge.formulaNodes)
  let certificate ← VE.Core.Wire.decodeCertificate (← j.getObjVal? "certificate")
  VE.Route.Wire.bindingOk profiles environment
    (background.map VE.Core.Wire.encodeFormula ++ (← premisesJson.getArr?).toList)
    (← j.getObjVal? "conclusion") certificate.environment_id certificate.premise_meaning_ids
    certificate.conclusion_meaning_id
  if VE.Route.Steps.core certificate.trace > (← VE.Route.Steps.limit j) then
    throw VE.Route.Steps.stepLimit
  return VE.Route.Wire.ok id [("valid", .bool (VE.Core.Tableau.checkCertificate E
      (background ++ ps) c certificate)), ("background", toJson background.length),
      ("steps", toJson (VE.Route.Steps.core certificate.trace))]

def run (profiles : List String) (environment : Json) (id kind : String) (j : Json) :
    Except String Json := do
  let L ← decodeLayered profiles environment
  if kind == "background" then
    return runBackground id (background L)
  if kind == "certificate" then
    return ← coreCertificate profiles environment L.core ((background L).map Prod.fst) id j
  unless kind == "evaluate" || kind == "countermodel" do
    throw (VE.Route.Gate.unsupported
      s!"{kind} cases on the core family with definitions or data flags are deferred")
  let complete ← completeModel L environment (← j.getObjVal? "model")
  VE.Core.Wire.run profiles L.core id kind ((j.setObjVal! "environment" L.core).setObjVal! "model" complete)

end VE.Core.Layers
