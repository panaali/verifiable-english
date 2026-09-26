import VE.Core.Route
import VE.Core.Bridge
import VE.Route.Wire

namespace VE.Core.Wire
open Lean
open VE.Route

def literals (v : VE.Bridge.Vocabulary) : List String :=
  (v.constants.filter (fun c => c.2 == "$string")).map Prod.fst

def modelVocabulary (v : VE.Bridge.Vocabulary) : VE.Bridge.Vocabulary :=
  { v with sorts := v.sorts ++ (if (literals v).isEmpty then [] else ["$string"]) }

def decodeModel (v : VE.Bridge.Vocabulary) (j : Json) :
    Except String (VE.FiniteModel VE.Bridge.Entity) := do
  let data ← VE.Bridge.decodeModelData (modelVocabulary v) j
  unless data.valid (modelVocabulary v) do throw "model is not semantically admissible"
  let M := data.toModel
  match VE.Route.Wire.backgroundViolation M (literals v) with
  | some g => throw (VE.Route.Wire.invalidModel g)
  | none => pure M

def decodeTrace : Nat → Json → Except String Tableau.Trace
  | 0, _ => throw "ResourceLimit: certificate expansion depth exceeds 124"
  | fuel + 1, j => do
    let rule ← VE.Bridge.stringField j "rule"
    if rule == "close" then
      VE.Bridge.exactFields j ["rule"]
      pure .close
    else if rule == "closure-induct@1" then
      VE.Bridge.exactFields j ["rule", "at", "sort", "invariant", "children"]
      let index ← (← j.getObjVal? "at").getNat?
      let sort ← VE.Bridge.stringField j "sort"
      let invariant ← Bridge.decodeFormula 64 (← j.getObjVal? "invariant")
      if Bridge.formulaNodes invariant > 10000 then throw "ResourceLimit: invariant AST node count"
      let children ← (← (← j.getObjVal? "children").getArr?).toList.mapM (decodeTrace fuel)
      pure (.induct index sort invariant children)
    else if rule == "expand" || rule == "closure-plus@0" || rule == "closure-star@0" ||
        Tableau.extraRule rule then
      let names := (← VE.Bridge.fields j).map Prod.fst
      let optional := names.contains "parameter"
      VE.Bridge.exactFields j (["rule", "at", "children"] ++ if optional then ["parameter"] else [])
      let index ← (← j.getObjVal? "at").getNat?
      let parameter ← if optional then do pure (some (← VE.Bridge.stringField j "parameter")) else pure none
      let children ← (← (← j.getObjVal? "children").getArr?).toList.mapM (decodeTrace fuel)
      pure (.expand rule index parameter children)
    else throw "unknown tableau rule"

def decodeCertificate (j : Json) : Except String Tableau.Certificate := do
  VE.Bridge.exactFields j ["checker_version", "environment_id", "premise_meaning_ids",
    "conclusion_meaning_id", "trace"]
  pure ⟨← VE.Bridge.stringField j "checker_version", ← VE.Bridge.stringField j "environment_id",
    ← VE.Bridge.strings (← j.getObjVal? "premise_meaning_ids"),
    ← VE.Bridge.stringField j "conclusion_meaning_id", ← decodeTrace 125 (← j.getObjVal? "trace")⟩

/-- The Core route decodes n-ary signatures and regenerates literal premises. -/
def run (profiles : List String) (environment : Json) (id kind : String)
    (j : Json) : Except String Json := do
  let v ← Bridge.decodeEnvironment environment
  let E := v.environment
  if kind == "evaluate" then
    let M ← decodeModel v (← j.getObjVal? "model")
    let fs ← Bridge.decodeFormulas E (← j.getObjVal? "ast")
    if fs.isEmpty then throw "empty document"
    return VE.Route.Wire.ok id [("values", toJson (fs.map (fun a => a.eval M [])))]
  let premisesJson ← j.getObjVal? "premises"
  let ps ← Bridge.decodeFormulas E premisesJson
  let c ← Bridge.decodeFormula 64 (← j.getObjVal? "conclusion")
  unless c.check E [] do throw "ill-typed or unbound conclusion"
  if ((c :: ps).map Bridge.formulaNodes).foldl (· + ·) 0 > 10000 then
    throw "ResourceLimit: AST node count"
  if kind == "countermodel" then
    let M ← decodeModel v (← j.getObjVal? "model")
    return VE.Route.Wire.ok id [("refutes", .bool (countermodelCheck M ps c))]
  unless kind == "certificate" do throw "unknown case kind"
  let certificate ← decodeCertificate (← j.getObjVal? "certificate")
  let background := VE.Route.Background.literals (literals v)
  VE.Route.Wire.bindingOk profiles environment
    (background.map VE.Route.Wire.encodeFormula ++ (← premisesJson.getArr?).toList)
    (← j.getObjVal? "conclusion") certificate.environment_id certificate.premise_meaning_ids
    certificate.conclusion_meaning_id
  return VE.Route.Wire.ok id [("valid", .bool (Tableau.checkCertificate E
      (background.map embed ++ ps) c certificate)), ("background", toJson background.length)]

end VE.Core.Wire
