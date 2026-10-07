import VE.Core.Route
import VE.Core.Bridge
import VE.Route.Wire

namespace VE.Core.Wire
open Lean
open VE.Route
universe u

def literals (v : VE.Bridge.Vocabulary) : List String :=
  (v.constants.filter (fun c => c.2 == "$string")).map Prod.fst

def modelVocabulary (v : VE.Bridge.Vocabulary) : VE.Bridge.Vocabulary :=
  { v with sorts := v.sorts ++ (if (literals v).isEmpty then [] else ["$string"]) }

/-- Decoded tables with each domain in Python/Rust order (`sortModelData`): the
budgeted evaluator stops quantifiers at the first decisive entity. -/
def decodeModel (v : VE.Bridge.Vocabulary) (j : Json) :
    Except String (VE.FiniteModel VE.Bridge.Entity) := do
  let data := VE.Route.Wire.sortModelData (← VE.Route.Decode.decodeModelData (modelVocabulary v) j)
  unless VE.Route.Decode.validFast data (modelVocabulary v) do
    throw "model is not semantically admissible"
  let M := data.toModel
  match VE.Route.Wire.backgroundViolation M (literals v) with
  | some g => throw (VE.Route.Wire.invalidModel g)
  | none => pure M

/-- A hash index of a decoded model's tables, for every declared predicate. -/
def index (v : VE.Bridge.Vocabulary) (M : VE.FiniteModel VE.Bridge.Entity) :
    Std.HashMap String (Std.HashSet (List VE.Bridge.Entity)) :=
  VE.Route.Budget.tableIndex ((modelVocabulary v).predicates.map Prod.fst) M

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
  VE.CertificateWire.certificateFields j
  pure ⟨← VE.Bridge.stringField j "checker_version", ← VE.Bridge.stringField j "environment_id",
    ← VE.Bridge.strings (← j.getObjVal? "premise_meaning_ids"),
    ← VE.Bridge.stringField j "conclusion_meaning_id", ← decodeTrace 125 (← j.getObjVal? "trace")⟩

/-- The Core route decodes n-ary signatures and regenerates literal premises. -/
def run (profiles : List String) (environment : Json) (id kind : String)
    (j : Json) : Except String Json := do
  let v ← Bridge.decodeEnvironment environment
  let E := v.environment
  if kind == "background" then
    return VE.Route.Wire.runBackground id (VE.Route.Background.background (literals v))
  if kind == "evaluate" then
    let _ ← VE.Route.Wire.formulasJson (← j.getObjVal? "ast")
    let fs ← Bridge.decodeFormulas E (← j.getObjVal? "ast")
    if fs.isEmpty then throw "empty document"
    let M ← decodeModel v (← j.getObjVal? "model")
    return VE.Route.Wire.ok id [("values", toJson (← VE.Route.Budget.valuesN (VE.Route.Budget.tableMem M (index v M)) M fs))]
  let premisesJson ← j.getObjVal? "premises"
  let _ ← VE.Route.Wire.formulasJson premisesJson (some (← j.getObjVal? "conclusion"))
  let ps ← Bridge.decodeFormulas E premisesJson
  let c ← Bridge.decodeFormula 64 (← j.getObjVal? "conclusion")
  Bridge.checkFormula E c "conclusion"
  VE.Route.Wire.nodeLimit ((c :: ps).map Bridge.formulaNodes)
  if kind == "countermodel" then
    let M ← decodeModel v (← j.getObjVal? "model")
    let idx := index v M
    let some refutes := VE.Route.Budget.refutesN (VE.Route.Budget.tableMem M idx) M
      VE.Time.maxEvaluations ps c 0
      | throw VE.Route.Budget.budgetExhausted
    return VE.Route.Wire.ok id [("refutes", .bool refutes)]
  unless kind == "certificate" do throw "unknown case kind"
  let certificate ← decodeCertificate (← j.getObjVal? "certificate")
  let background := VE.Route.Background.literals (literals v)
  VE.Route.Wire.bindingOk profiles environment
    (background.map VE.Route.Wire.encodeFormula ++ (← premisesJson.getArr?).toList)
    (← j.getObjVal? "conclusion") certificate.environment_id certificate.premise_meaning_ids
    certificate.conclusion_meaning_id
  if VE.Route.Steps.core certificate.trace > VE.Route.Steps.limit j then
    throw VE.Route.Steps.stepLimit
  return VE.Route.Wire.ok id [("valid", .bool (Tableau.checkCertificate E
      (background.map embed ++ ps) c certificate)), ("background", toJson background.length),
      ("steps", toJson (VE.Route.Steps.core certificate.trace))]

theorem validField (id : String) (b : Bool) (n : Nat) :
    (VE.Route.Wire.ok id [("valid", .bool b), ("background", toJson n)]).getObjVal? "valid" =
      .ok (.bool b) := by
  rfl

/-- Acceptance at the wire endpoint uses the decoded formulas and the
regenerated literal premises. The identity check is part of the successful
run, before the checker result is returned. -/
theorem run_certificate_acceptance (profiles : List String) (environment : Json)
    (id : String) (j result premisesJson conclusionJson certificateJson : Json)
    (premiseArray : Array Json)
    (v : VE.Bridge.Vocabulary) (ps : List Formula) (c : Formula)
    (certificate : Tableau.Certificate)
    (hv : Bridge.decodeEnvironment environment = .ok v)
    (hpj : j.getObjVal? "premises" = .ok premisesJson)
    (hpa : premisesJson.getArr? = .ok premiseArray)
    (hps : Bridge.decodeFormulas v.environment premisesJson = .ok ps)
    (hcj : j.getObjVal? "conclusion" = .ok conclusionJson)
    (hc : Bridge.decodeFormula 64 conclusionJson = .ok c)
    (hcc : Bridge.checkFormula v.environment c "conclusion" = .ok ())
    (hcertj : j.getObjVal? "certificate" = .ok certificateJson)
    (hcert : decodeCertificate certificateJson = .ok certificate)
    (hrun : run profiles environment id "certificate" j = .ok result)
    (hvalid : result.getObjVal? "valid" = .ok (.bool true)) :
    VE.Route.Wire.bindingOk profiles environment
      ((VE.Route.Background.literals (literals v)).map VE.Route.Wire.encodeFormula ++
        premiseArray.toList) conclusionJson certificate.environment_id
      certificate.premise_meaning_ids certificate.conclusion_meaning_id = .ok () ∧
    ∀ S : VE.Structure.{u}, S.Admissible v.environment →
      (∀ b ∈ VE.Route.Background.literals (literals v), b.denote S []) →
      (∀ p ∈ ps, p.denote S []) → c.denote S [] := by
  simp [run, hv, hpj, hps, hcj, hc, hcc, hpa, hcertj, hcert, bind, Except.bind,
    pure, Except.pure] at hrun
  split at hrun
  · cases hrun
  split at hrun
  · cases hrun
  split at hrun
  · cases hrun
  rename_i _ outputUnit hbind
  cases outputUnit
  have hbound := hbind
  split at hrun
  · cases hrun
  cases hrun
  have hcheck : Tableau.checkCertificate v.environment
      ((VE.Route.Background.literals (literals v)).map embed ++ ps) c certificate = true := by
    cases ht : Tableau.checkCertificate v.environment
        ((VE.Route.Background.literals (literals v)).map embed ++ ps) c certificate
    · have hfield : (Json.mkObj [("id", .str id), ("status", .str "ok"),
          ("valid", .bool false),
          ("background", toJson (VE.Route.Background.literals (literals v)).length),
          ("steps", toJson (VE.Route.Steps.core certificate.trace))]).getObjVal? "valid" =
          .ok (.bool false) := rfl
      simp only [ht] at hvalid
      change (Json.mkObj [("id", .str id), ("status", .str "ok"),
        ("valid", .bool false),
        ("background", toJson (VE.Route.Background.literals (literals v)).length),
        ("steps", toJson (VE.Route.Steps.core certificate.trace))]).getObjVal? "valid" =
        .ok (.bool true) at hvalid
      rw [hfield] at hvalid
      cases hvalid
    · rfl
  refine ⟨hbound, ?_⟩
  intro S hS hbgSat hp
  have hall : ∀ p ∈ (VE.Route.Background.literals (literals v)).map embed ++ ps,
      p.denote S [] := by
    intro p hmem
    rcases List.mem_append.mp hmem with hbg | hps'
    · obtain ⟨b, hb, rfl⟩ := List.mem_map.mp hbg
      exact (conservativity S [] b).mpr (hbgSat b hb)
    · exact hp p hps'
  exact VE.Core.Tableau.checkCertificate_sound v.environment _ c certificate hcheck S hS hall

end VE.Core.Wire
