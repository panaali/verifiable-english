import VE.Service.Family

/-! Complete-choice readings checks. Python proposes certificates and finite
models, but this mode checks every proposal, the complete choice set, and the
ALL/SOME/NONE/UNKNOWN fold. An omitted compatible choice cannot prove ALL or
NONE. -/
namespace VE.Service.ReadingsChoices
open Lean
open VE.Service

private def arr (j : Json) (field : String) : Except String (List Json) := do
  pure (← (← j.getObjVal? field).getArr?).toList

private def index (j : Json) : Except String Nat :=
  j.getNat?.mapError fun _ => "a choice is a list of reading indices"

private def indices (j : Json) : Except String (List Nat) := do
  (← j.getArr?).toList.mapM index

private def label (reading : Json) (axis : String) : Json :=
  (reading.getObjValD "labels").getObjValD axis

private def compatible (couplings : List Json) (selected : List (String × Json)) : Bool :=
  couplings.all fun coupling => Id.run do
    let axis := (coupling.getObjValD "axis").getStr?.toOption.getD ""
    let refs := ((coupling.getObjValD "sets").getArr?.toOption.getD #[]).toList.map
      fun ref => s!"{(ref.getObjValD "set").getStr?.toOption.getD ""}@{(ref.getObjValD "version").getNat?.toOption.getD 0}"
    let values := (selected.filter fun (name, _) => refs.contains name).map fun (_, reading) =>
      label reading axis
    return values.all (· == values.headD Json.null)

private def enumerate (limit : Nat) (couplings : List Json) :
    List (String × List Json) → List (String × Json) → List Nat → List (List Nat)
  | [], _, chosen => [chosen.reverse]
  | (name, readings) :: rest, selected, chosen => Id.run do
    let mut out := []
    for i in List.range readings.length do
      if out.length > limit then break
      let reading := readings[i]!
      let next := selected ++ [(name, reading)]
      if compatible couplings next then
        out := out ++ enumerate limit couplings rest next (i :: chosen)
    return out.take (limit + 1)

private def metadata (j : Json) : Except String (List (String × List Json)) := do
  let sets ← arr j "set_meta"
  sets.mapM fun s => do
    let name ← VE.Bridge.stringField s "id"
    let version ← (← s.getObjVal? "version").getNat?
    unless version > 0 do throw "invalid reading set version"
    let readings ← arr s "readings"
    unless !readings.isEmpty do throw "every reading set holds a reading"
    pure (s!"{name}@{version}", readings)

private def validateCouplings (couplings : List Json) (setInfo : List (String × List Json))
    (documentValidation : Bool := false) :
    Except String Unit := do
  unless !couplings.isEmpty do throw "coupled choices require couplings"
  let names := setInfo.map Prod.fst
  for coupling in couplings do
    let couplingId ← VE.Bridge.stringField coupling "id"
    let axis ← VE.Bridge.stringField coupling "axis"
    let refs ← arr coupling "sets"
    unless refs.length ≥ 2 do throw "invalid coupling set"
    let mut seen : List String := []
    let mut common : Option (List Json) := none
    let mut firstName := ""
    for ref in refs do
      let name ← VE.Bridge.stringField ref "set"
      let version ← (← ref.getObjVal? "version").getNat?
      let key := s!"{name}@{version}"
      unless names.contains key && !seen.contains name do throw "invalid coupling set"
      seen := name :: seen
      let readings := (setInfo.find? (fun (s, _) => s == key)).map Prod.snd |>.getD []
      unless readings.all (fun reading => (label reading axis).getStr?.isOk) do
        throw s!"CouplingLabelMissing: {couplingId}, {name}"
      if firstName.isEmpty then firstName := name
      let values := readings.map (label · axis)
      common := some (match common with
        | none => values
        | some prior => prior.filter values.contains)
    unless !(common.getD []).isEmpty do
      if documentValidation then
        throw s!"CouplingLabelMissing: {couplingId}, {firstName}"
      let names ← couplings.mapM (VE.Bridge.stringField · "id")
      throw ("CouplingUnsatisfiable: " ++ String.intercalate ", " names.mergeSort)

private def expected (j : Json) (setInfo : List (String × List Json)) : Except String (List (List Nat)) := do
  let route ← VE.Bridge.stringField j "route"
  if route == "joint-choices" then
    let choices ← arr j "joint_choices"
    unless !choices.isEmpty do throw "InvalidCompatibility: no compatible joint choices"
    choices.mapM indices
  else if route == "coupled-choices" then
    let couplings ← arr j "couplings"
    validateCouplings couplings setInfo
    let answer := enumerate 64 couplings setInfo [] []
    unless !answer.isEmpty do throw "CouplingUnsatisfiable: no compatible choices"
    unless answer.length ≤ 64 do throw "ResourceLimit: compatible choices"
    pure answer
  else throw "invalid readings choice route"

private def selectedAxes (couplings : List Json) (name : String) : List String :=
  ((couplings.filter fun coupling =>
    ((coupling.getObjValD "sets").getArr?.toOption.getD #[]).toList.any fun ref =>
      s!"{(ref.getObjValD "set").getStr?.toOption.getD ""}@{(ref.getObjValD "version").getNat?.toOption.getD 0}" == name)
      |>.map fun coupling => (coupling.getObjValD "axis").getStr?.toOption.getD "").eraseDups

private def openUnit (axes : List String) (readings : List Json) : Bool :=
  readings.any fun reading =>
    (readings.filter fun other => axes.all (fun axis => label reading axis == label other axis)).length > 1

/-- The public coupled planner uses the same compatible-choice enumeration as
the evidence checker. It reports at most one choice beyond the limit. -/
def plan (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let setInfo ← metadata j
  let couplings ← arr j "couplings"
  validateCouplings couplings setInfo (j.getObjValD "document_validation" == .bool true)
  let limit ← (← j.getObjVal? "limit").getNat?
  let choices := enumerate limit couplings setInfo [] []
  unless !choices.isEmpty do
    let names ← couplings.mapM (VE.Bridge.stringField · "id")
    throw ("CouplingUnsatisfiable: " ++ String.intercalate ", " names.mergeSort)
  if choices.length > limit then
    let rawSets ← arr j "set_meta"
    let mut units : List Json := []
    for (s, (name, readings)) in List.zip rawSets setInfo do
      if openUnit (selectedAxes couplings name) readings then
        let unit := (s.getObjValD "unit").getStr?.toOption.getD
          ((s.getObjValD "id").getStr?.toOption.getD "")
        units := units ++ [.str unit]
    pure (VE.Route.Wire.ok id [
      ("route", .str "UNKNOWN"), ("budget", Json.mkObj [("max_choices", toJson limit)]),
      ("choice_count", toJson choices.length), ("units", toJson units)])
  else
    let names ← couplings.mapM (VE.Bridge.stringField · "id")
    pure (VE.Route.Wire.ok id [
      ("route", .str "enumerate"), ("choices", toJson choices),
      ("conditional_on", toJson (names.map ("coupling:" ++ ·)))])

/-- Every proposed row is checked against the chosen premises. The verdict is
computed only after the submitted choices equal the complete allowed set. -/
def check {F C M : Type} (ctx : Family.Ctx F C M)
    (valid : C → List F → F → Bool) (refutes : M → List F → F → Bool)
    (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let fixedJson ← arr j "fixed"
  let fixed ← fixedJson.mapM ctx.formula
  let setsJson ← (arr j "sets").bind fun sets => sets.mapM Json.getArr?
  let sets ← setsJson.mapM fun s => s.toList.mapM ctx.formula
  let setInfo ← metadata j
  unless setInfo.length == sets.length &&
      (List.zip setInfo sets).all (fun ((_, ms), fs) => ms.length == fs.length) do
    throw "reading metadata does not match the sets"
  let wanted ← expected j setInfo
  let rows ← arr j "choice_evidence"
  let parsed ← rows.mapM fun row => do
    let is ← indices (← row.getObjVal? "choice")
    let chosen ← match VE.Service.GenericReadings.resolve sets is with
      | some fs => pure fs
      | none => throw "a choice must pick one reading of each set"
    let chosenJson ← match VE.Service.GenericReadings.resolve (setsJson.map Array.toList) is with
      | some fs => pure fs
      | none => throw "a choice must pick one reading of each set"
    let premises := ctx.background.map (·.1) ++ fixed ++ chosen
    if let .ok certificate := row.getObjVal? "certificate" then
      VE.Bridge.exactFields row ["choice", "certificate"]
      let c ← ctx.certificate certificate
      ctx.bound (fixedJson ++ chosenJson) (← j.getObjVal? "conclusion") c
      unless valid c premises (← ctx.formula (← j.getObjVal? "conclusion")) do
        throw "the choice certificate does not check"
      pure (is, "positive")
    else if let .ok model := row.getObjVal? "model" then
      VE.Bridge.exactFields row ["choice", "model"]
      let m ← ctx.model model
      unless refutes m premises (← ctx.formula (← j.getObjVal? "conclusion")) do
        throw "the choice countermodel does not check"
      pure (is, "negative")
    else
      VE.Bridge.exactFields row ["choice", "status"]
      unless row.getObjValD "status" == .str "UNKNOWN" do
        throw "invalid choice evidence"
      pure (is, "unknown")
  let submitted := parsed.map Prod.fst
  unless submitted.length == wanted.length &&
      submitted.eraseDups.length == submitted.length &&
      submitted.all wanted.contains do
    throw "choice evidence does not cover the compatible choices"
  let positives := (parsed.filter (fun (_, status) => status == "positive")).length
  let negatives := (parsed.filter (fun (_, status) => status == "negative")).length
  let joint := j.getObjValD "route" == .str "joint-choices"
  let verdict := if joint && positives + negatives != parsed.length then "UNKNOWN"
    else if positives > 0 && negatives > 0 then "SOME"
    else if positives == parsed.length then "ALL"
    else if negatives == parsed.length then "NONE"
    else "UNKNOWN"
  pure (VE.Route.Wire.ok id [("verdict", .str verdict)])

def run (j : Json) : Except String Json := do
  if j.getObjValD "kind" == .str "plan" then return ← plan j
  let environment ← j.getObjVal? "environment"
  if Family.isFamily environment || Standalone.isLegacy environment then
    if Standalone.isLegacy environment then
      match ← Standalone.decodeLegacy environment with
      | .v0 v =>
        return ← check (← Family.legacyFolCtx environment v) (Family.folValid v.environment)
          (Family.folRefutes (v.predicates.map Prod.fst) v.environment) j
      | .closure v =>
        return ← check (← Family.legacyClosureCtx environment v) (Family.closureValid v.environment)
          (Family.closureRefutes (v.predicates.map Prod.fst) v.environment) j
      | .order v =>
        return ← check (← Family.legacyOrderCtx environment v) (Family.orderValid v.environment)
          (Family.orderRefutes (v.predicates.map Prod.fst) v.environment) j
    let checked ← Standalone.validated environment
    match checked.envelope.family with
    | .closure =>
      let f ← Family.closureEnv environment checked
      return ← check f.ctx (Family.closureValid f.rv.environment)
        (Family.closureRefutes (f.rv.modelVocabulary.predicates.map Prod.fst) f.rv.environment) j
    | .closureNary =>
      let f ← Family.coreEnv environment checked
      return ← check f.ctx (Family.coreValid f.v.environment)
        (Family.coreRefutes ((VE.Core.Wire.modelVocabulary f.v).predicates.map Prod.fst) f.v.environment) j
    | .order =>
      let f ← Family.orderEnv environment checked
      return ← check f.ctx (Family.orderValid f.rv.vocabulary.environment)
        (Family.orderRefutes (f.rv.modelVocabulary.predicates.map Prod.fst) f.rv.vocabulary.environment) j
    | .fol => throw "invalid family"
  -- The FOL route uses the same validated vocabulary, Background and binding
  -- as Service.Readings.readingsCase.
  let checked ← Standalone.validated environment
  let e := checked.envelope
  unless e.family == .fol do throw "reading checks on this family are not implemented"
  let rv ← VE.Route.Run.decodeRouteVocabulary e
  let E := rv.environment
  let B ← Standalone.folBackground environment rv
  let envId ← Standalone.environmentIdOf e.profiles environment
  let ctx : Family.Ctx VE.Formula VE.Tableau.Certificate
      { M : VE.FiniteModel VE.Bridge.Entity // M.asStructure.Admissible E } := {
    environment := environment
    envId := envId
    version := VE.Route.Wire.identityVersion e.profiles
    formula := fun f => VE.Route.Wire.decodeClosed E f (e.profiles.contains "data@0")
    meaningId := VE.Route.Wire.meaningId e.profiles envId
    certificate := VE.CertificateWire.decodeCertificate
    bound := fun premises conclusion c => VE.Route.Wire.bindingOk e.profiles environment
      (B.map (VE.Route.Wire.encodeFormula ·.1) ++ premises) conclusion
      c.environment_id c.premise_meaning_ids c.conclusion_meaning_id
    background := Family.withAst B id
    model := VE.Service.Readings.decodeModel rv }
  check ctx (Family.folValid E) (fun m Γ φ => VE.Service.Readings.refutes m.1 Γ φ) j

end VE.Service.ReadingsChoices
