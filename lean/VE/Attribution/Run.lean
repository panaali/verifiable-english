import VE.Attribution.Admission
import VE.Route.Run

/-! The `ve_reports_route` executable (spec 9.4), invoked as
`lean/.lake/build/bin/ve_reports_route <cases.json|->`. Each case is
`{"id", "kind", "environment", "document", ...}`. Every formula, key, name,
premise, open term, bridge formula and identity is regenerated from the decoded
document (`Wire.decodeDocument`); nothing on the wire supplies them.

* `reports-elaborate` → `environment_reports_id`, `keys` (each generated name
  with its source key and argument sort), `premises` (labelled
  `report:<unit>` / `assessment:<unit>`, signed), `open_terms` (names with
  their records), `bridge_formulas` (per declared record), `content_ids` (per
  unit), `envelope`, `warnings`.
* `reports-certificate` with `premises` (Γ, over E_reports), `conclusion`,
  `certificate` and `envelope` → `valid` (false on any binding or envelope
  mismatch), `environment_reports_id`, `envelope`, `bindings`. The certificate
  binds `environment_id(E_reports)`, the checked list
  `literals ++ Γ_reports ++ Γ` and the conclusion (`reports_route_acceptance`).
* `reports-countermodel` with `premises`, `conclusion` and a finite `model`
  over E_reports → `refutes` and the decoded source-model rendering (the holders
  or evidence contexts of each key).
* `reports-scoped` with optional `certificates`, `inconsistency` and
  `witnesses` (maps from check id) → per scoped check FOLLOWS / DOES NOT FOLLOW
  / PAYLOADS INCONSISTENT / UNKNOWN, with the check's environment id and
  Background size. Witness models are replayed for checks over the author's E
  only; a witness for a quoted package's scope is reported UNKNOWN.
* `admission` of a document under `reports@0` → `admitted`, `report`,
  `report_id`, `envelope`, `kinds` (`Run.reports_wire_acceptance`).
* Cases without a reports construct delegate unchanged to
  `VE.Route.Run.runCase`; a reports input never falls back after a failed
  decode. -/
namespace VE.Reports.Run
open Lean
open VE.Bridge (stringField)
open VE.Order.ProfileGate (bind_ok)

def enc (a : VE.Formula) : Json := VE.Route.Wire.encodeFormula a

/-- The executable dispatch test: the `reports@0` profile or a `reports-*` kind. -/
def usesReportsPath (j : Json) : Bool :=
  let profiles := match (j.getObjValD "environment").getObjValD "profiles" with
    | .arr ps => ps.toList.any (· == .str reportsProfile)
    | _ => false
  let kind := match j.getObjValD "kind" with
    | .str k => k.startsWith "reports-"
    | _ => false
  profiles || kind

def envelopeJson (D : ReportDoc) (envId : String) : Json :=
  Json.mkObj [("environment_id", .str envId), ("document_id", .str (documentId D))]

/-! ## reports-elaborate -/

def premiseLabel (u : Unit) : String :=
  if isAssessStatement u.content then "assessment:" ++ u.id else "report:" ++ u.id

def recordJson (r : Assessment) : Json :=
  Json.mkObj [("id", .str r.id), ("context", .str r.context), ("decided_by", .str r.decidedBy),
    ("necessary", Json.arr (r.necessary.map enc).toArray), ("sufficient", Json.arr (r.sufficient.map enc).toArray),
    ("factors", toJson r.factors), ("precedents", toJson r.precedents), ("jurisdiction", .str r.jurisdiction),
    ("version", toJson r.version)]

def warnings (dec : Wire.Decoded) : List String :=
  dec.units.filterMap fun
    | .w2 x => match x.kind with
      | .attributed _ act _ =>
        if ["says", "believes", "wants", "intends"].contains act then none
        else some s!"unreviewed act {act} in {x.id}"
      | _ => none
    | .reports .. => none

def elaborated (dec : Wire.Decoded) (environment : Json) : List (String × Json) :=
  let D := dec.D
  [("environment_reports_id",
      .str ((VE.Route.Wire.environmentId D.profiles (Wire.environmentReportsJson environment D)).toOption.getD "")),
   ("keys", Json.arr ((Wire.generated D).map fun (n, ss, key) =>
      Json.mkObj [("name", .str n), ("arguments", toJson ss), ("key", key)]).toArray),
   ("premises", Json.arr (D.units.filterMap fun u => (unitPremise D u).map fun φ =>
      Json.mkObj [("label", .str (premiseLabel u)), ("ast", enc φ)]).toArray),
   ("open_terms", Json.arr ((akeys D).map fun k =>
      Json.mkObj ([("name", .str (assessName D k)), ("arguments", toJson [D.evidence])] ++
        match recordOf D k.a with
        | some r => [("record", recordJson r)]
        | none => [])).toArray),
   ("bridge_formulas", Json.arr (D.bridges.map fun b =>
      Json.mkObj ([("id", .str b.id), ("unit", .str b.target.unit), ("depth", toJson b.target.depth)] ++
        match bridgeFormula D b.target with
        | some φ => [("ast", enc φ)]
        | none => [])).toArray),
   ("content_ids", Json.arr (D.units.map fun u =>
      Json.mkObj [("unit", .str u.id), ("content_id", .str (contentId D u.content))]).toArray),
   ("envelope", envelopeJson D D.environmentId),
   ("warnings", toJson (warnings dec))]

/-! ## reports-certificate -/

/-- The inner binding (P0 3.9) at E_reports, as a Boolean. -/
def innerBound (profiles : List String) (envReportsJson : Json) (checked : List VE.Formula)
    (conclusion : VE.Formula) (c : VE.Tableau.Certificate) : Bool :=
  (VE.Route.Wire.bindingOk profiles envReportsJson (checked.map enc) (enc conclusion) c.environment_id
    c.premise_meaning_ids c.conclusion_meaning_id).toBool

def outerBound (D : ReportDoc) (j : Json) : Bool :=
  match j.getObjVal? "envelope" with
  | .ok e => e.getObjValD "environment_id" == .str D.environmentId &&
      e.getObjValD "document_id" == .str (documentId D) &&
      (VE.Bridge.exactFields e ["environment_id", "document_id"]).toBool
  | .error _ => false

def runCertificate (c : Wire.Checked) (environment : Json) (id : String) (j : Json) : Except String Json := do
  let D := c.dec.D
  let Γ ← VE.Route.Wire.decodeFormulas (envReports D) (← j.getObjVal? "premises")
  let φ ← VE.Route.Wire.decodeClosed (envReports D) (← j.getObjVal? "conclusion")
  let cert ← VE.CertificateWire.decodeCertificate (← j.getObjVal? "certificate")
  let erj := Wire.environmentReportsJson environment D
  let inner := innerBound D.profiles erj (checkedList D Γ) φ cert
  let outer := outerBound D j
  let accepted := VE.Tableau.checkCertificate (envReports D) (checkedList D Γ) φ cert
  pure (VE.Route.Wire.ok id [("valid", .bool (inner && outer && accepted)),
    ("environment_reports_id", .str ((VE.Route.Wire.environmentId D.profiles erj).toOption.getD "")),
    ("envelope", envelopeJson D D.environmentId),
    ("bindings", Json.mkObj [("inner", .bool inner), ("envelope", .bool outer)])])

/-! ## reports-countermodel -/

def decodeReportsModel (c : Wire.Checked) (j : Json) : Except String (VE.FiniteModel VE.Bridge.Entity) := do
  let v := Wire.reportsModelVocabulary c.dec.re c.dec.D
  let data ← VE.Bridge.decodeModelData v j
  VE.Route.Admission.require (data.valid v) "model is not semantically admissible"
  let M := data.toModel
  VE.Route.Admission.require (VE.Route.Background.literalsValid M c.dec.D.lits) (VE.Route.Wire.invalidModel "literals")
  pure M

def runCountermodel (c : Wire.Checked) (id : String) (j : Json) : Except String Json := do
  let D := c.dec.D
  let Γ ← VE.Route.Wire.decodeFormulas (envReports D) (← j.getObjVal? "premises")
  let φ ← VE.Route.Wire.decodeClosed (envReports D) (← j.getObjVal? "conclusion")
  let M ← decodeReportsModel c (← j.getObjVal? "model")
  let rendering := (Wire.generated D).map fun (n, _, key) =>
    Json.mkObj [("name", .str n), ("key", key),
      ("holds_of", toJson ((M.relations n).filterMap fun
        | [v] => some v.2
        | _ => none))]
  pure (VE.Route.Wire.ok id [("refutes", .bool (VE.countermodelCheck M (premises D ++ Γ) φ)),
    ("source_model", Json.arr rendering.toArray)])

/-! ## reports-scoped -/

def scopedBound (Eq : Pinned) (checked : List VE.Formula) (conclusion : VE.Formula)
    (c : VE.Tableau.Certificate) : Bool :=
  match (checked.map enc).mapM (VE.Route.Wire.meaningId Eq.profiles Eq.id),
      VE.Route.Wire.meaningId Eq.profiles Eq.id (enc conclusion) with
  | .ok ps, .ok cid => c.environment_id == Eq.id && c.premise_meaning_ids == ps && c.conclusion_meaning_id == cid
  | _, _ => false

def certificateFor (j : Json) (key id : String) : Option Json :=
  ((j.getObjValD key).getObjVal? id).toOption

def scopedVerdict (c : Wire.Checked) (j : Json) (s : ScopedCheck) : Except String Json := do
  let D := c.dec.D
  match payloadFormulas D s with
  | none => pure (Json.mkObj [("id", .str s.id), ("status", .str "UNKNOWN"), ("detail", .str "payloads")])
  | some (Eq, ps) =>
    let checked := background Eq ++ ps
    let base := [("id", .str s.id), ("environment_id", .str Eq.id), ("background", toJson (background Eq).length)]
    let certJson := (certificateFor j "certificates" s.id).orElse fun _ =>
      (c.dec.scopedCertificates.find? (·.1 == s.id)).map Prod.snd
    let follows ← match certJson with
      | some cj => do
        let cert ← VE.CertificateWire.decodeCertificate cj
        pure (scopedBound Eq checked s.conclusion cert &&
          VE.Tableau.checkCertificate Eq checked s.conclusion cert)
      | none => pure false
    if follows then return Json.mkObj (base ++ [("status", .str "FOLLOWS")])
    let inconsistent ← match certificateFor j "inconsistency" s.id with
      | some cj => do
        let cert ← VE.CertificateWire.decodeCertificate cj
        pure (scopedBound Eq checked .bottom cert && VE.Tableau.checkCertificate Eq checked .bottom cert)
      | none => pure false
    if inconsistent then return Json.mkObj (base ++ [("status", .str "PAYLOADS INCONSISTENT")])
    match certificateFor j "witnesses" s.id with
    | some mj =>
      if Eq.id == D.environmentId then
        let M ← VE.Route.Wire.decodeModel c.dec.re.rv mj
        if VE.countermodelCheck M checked s.conclusion then
          return Json.mkObj (base ++ [("status", .str "DOES NOT FOLLOW")])
        else return Json.mkObj (base ++ [("status", .str "UNKNOWN"), ("detail", .str "witness does not refute")])
      else return Json.mkObj (base ++ [("status", .str "UNKNOWN"),
        ("detail", .str "witness replay over a quoted package's scope is not implemented")])
    | none => pure (Json.mkObj (base ++ [("status", .str "UNKNOWN"), ("detail", .str "no evidence")]))

/-! ## admission -/

def reportJson (r : VE.Graph.Report) : Json :=
  Json.mkObj [("root", VE.Route.Run.claimJson r.root),
    ("assumptions", Json.arr (r.assumptions.map VE.Route.Run.claimJson).toArray)]

def reportDomain (profiles : List String) : String :=
  s!"ve-report-{VE.Route.Wire.identityVersion profiles}\n"

def reportPayload (envId : String) (document : Json) (r : VE.Graph.Report) : Json :=
  Json.mkObj [("environment_id", .str envId), ("document", document), ("report", reportJson r)]

def encodeAdmitted (id reportId : String) (res : ReportsAdmitted) : Json :=
  VE.Route.Wire.ok id [("admitted", .bool true), ("report", reportJson res.report),
    ("report_id", .str reportId),
    ("envelope", Json.mkObj [("environment_id", .str res.envelope.1), ("document_id", .str res.envelope.2)]),
    ("kinds", Json.arr (res.D.units.map fun u => VE.Route.Admission.renderKind (kindOf u.content)).toArray)]

def runAdmission (id : String) (environment document : Json) : Except String Json := do
  let profiles ← VE.Route.Gate.profilesOf environment
  let res ← admissionReports profiles environment document
  let reportId ← VE.CertificateWire.digest (reportDomain profiles)
    (reportPayload res.envelope.1 document res.report)
  return encodeAdmitted id reportId res

/-- The reports admission answer: the encoding of an admission of exactly the
case's environment and document, whose report id is the digest of the
recomputed environment id, the complete source document and the checked
report; `reports_admission_sound` gives everything the admission establishes. -/
def ReportsAdmissionAnswer (id : String) (environment document answer : Json) : Prop :=
  ∃ profiles res reportId, VE.Route.Gate.profilesOf environment = .ok profiles ∧
    admissionReports profiles environment document = .ok res ∧
    WellFormedReports res.D = true ∧
    VE.Route.Wire.environmentId profiles environment = .ok res.envelope.1 ∧
    res.envelope.2 = documentId res.D ∧
    VE.CertificateWire.digest (reportDomain profiles) (reportPayload res.envelope.1 document res.report) =
      .ok reportId ∧
    answer = encodeAdmitted id reportId res

theorem runAdmission_sound (id : String) (environment document answer : Json)
    (h : runAdmission id environment document = .ok answer) :
    ReportsAdmissionAnswer id environment document answer := by
  unfold runAdmission at h
  obtain ⟨profiles, hp, h⟩ := bind_ok h
  obtain ⟨res, hr, h⟩ := bind_ok h
  obtain ⟨reportId, hd, h⟩ := bind_ok h
  cases h
  obtain ⟨hwf, _, henv, hdoc, _⟩ := reports_admission_sound.{0} profiles environment document res hr
  exact ⟨profiles, res, reportId, hp, hr, hwf, henv, hdoc, hd, rfl⟩

/-! ## Dispatch -/

def runCase (j : Json) : Except String Json := do
  let id ← stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  if kind == "admission" && usesReportsPath j then
    let environment ← j.getObjVal? "environment"
    let document ← j.getObjVal? "document"
    return ← runAdmission id environment document
  if kind.startsWith "reports-" then
    let environment ← j.getObjVal? "environment"
    let c ← Wire.decodeDocument environment (← j.getObjVal? "document")
    if kind == "reports-elaborate" then
      return VE.Route.Wire.ok id (elaborated c.dec environment)
    if kind == "reports-certificate" then
      return ← runCertificate c environment id j
    if kind == "reports-countermodel" then
      return ← runCountermodel c id j
    if kind == "reports-scoped" then
      let verdicts ← c.dec.D.«scoped».mapM (scopedVerdict c j)
      return VE.Route.Wire.ok id [("scoped", Json.arr verdicts.toArray)]
  if usesReportsPath j then
    throw s!"UnsupportedProfile: case kind {kind} is not available on the reports route"
  VE.Route.Run.runCase j

/-- A successful reports `admission` answer is exactly the encoding of an
admission of the case's own environment and document (`ReportsAdmissionAnswer`,
with `reports_admission_sound`). -/
theorem reports_wire_acceptance (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission") (hn : usesReportsPath j = true) :
    ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
      ReportsAdmissionAnswer id (j.getObjValD "environment") (j.getObjValD "document") answer := by
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := bind_ok h
  obtain ⟨kind, hkind, h⟩ := bind_ok h
  have heq : kind = "admission" := by rw [hkind] at hk; cases hk; rfl
  subst kind
  simp only [beq_self_eq_true, Bool.true_and, hn, ↓reduceIte] at h
  obtain ⟨environment, he, h⟩ := bind_ok h
  obtain ⟨document, hd, h⟩ := bind_ok h
  have he' : j.getObjValD "environment" = environment := by
    simp only [Json.getObjValD, he]; rfl
  have hd' : j.getObjValD "document" = document := by
    simp only [Json.getObjValD, hd]; rfl
  rw [he', hd']
  exact ⟨id, hid, runAdmission_sound id environment document answer (by simpa using h)⟩

def runCaseReported (j : Json) : Json :=
  if usesReportsPath j then
    match runCase j with
    | .ok result => result
    | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"),
        ("error", .str message)]
  else VE.Route.Run.runCaseReported j

def main (paths : List String) : IO UInt32 := do
  let input ← match paths with
    | [] | ["-"] => (← IO.getStdin).readToEnd
    | [path] => IO.FS.readFile path
    | _ =>
      (← IO.getStderr).putStrLn "usage: ve_reports_route [cases.json|-]"
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
    return if results.any (fun r => r.getObjValD "status" == .str "error") then 1 else 0

end VE.Reports.Run
